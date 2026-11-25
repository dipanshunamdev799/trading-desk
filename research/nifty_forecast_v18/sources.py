"""Acquire exchange filings and dated non-price control series through authorized public routes."""
from concurrent.futures import ThreadPoolExecutor
import io
import re
import sys
from urllib.parse import urlencode
import requests
from .common import *

NSE='https://www.nseindia.in'
ARCH='https://nsearchives.nseindia.com'
LISTING=NSE+'/companies-listing/corporate-integrated-filing'
BULK=NSE+'/api/historicalOR/bulk-block-short-deals'
FED='https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm'
RBI25='https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60062'
RBI26='https://rbi.org.in/scripts/PublicationsView.aspx?Id=23809'
RELEASES={'announcement_page':NSE+'/companies-listing/corporate-filings-announcements','integrated_page':LISTING,
          'fed_schedule':FED,'rbi25_schedule':RBI25,'rbi26_schedule':RBI26,
          'delivery_documentation':NSE+'/all-reports','fpi_monitor':'https://www.fpi.nsdl.co.in/web/Reports/Latest.aspx',
          'consensus_public_data':'https://www.nseindia.com/static/market-data/corporate-data-subscription',
          'bls_archive':'https://www.bls.gov/bls/news-release/cpi.htm'}

def unpack(path):
    return gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()

def grab(url,where,kind=None):
    p=OUT/where
    meta=dict(url=url,requested_at=now(),file=where)
    if p.is_file():
        return meta|dict(status=200,sha256=sha(p),bytes=p.stat().st_size,cache=True)
    try:
        r=requests.get(url,timeout=(5,15),headers={'User-Agent':'Mozilla/5.0','Referer':LISTING,'Accept':'application/json,text/html,text/csv,*/*'})
        meta.update(status=r.status_code,received=now(),server_date=r.headers.get('Date'),content_type=r.headers.get('Content-Type'))
        a=r.content
        if not r.ok or not a or (kind=='csv' and a.lstrip()[:1]==b'<'):
            return meta|{'file':None}
        if kind=='json':
            r.json()
        if kind=='document' and not a.lstrip().startswith((b'<',b'\xef\xbb\xbf<')):
            return meta|{'file':None,'rejected':'not XML/HTML'}
        if kind=='zip' and a[:2]!=b'PK':
            return meta|{'file':None,'rejected':'not ZIP'}
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(gzip.compress(a,compresslevel=3,mtime=0) if p.suffix=='.gz' else a)
        return meta|dict(sha256=sha(p),bytes=p.stat().st_size)
    except (requests.RequestException,ValueError) as e:
        return meta|{'file':None,'error':type(e).__name__}

def release_table():
    # Only future meeting dates and their then-published schedules enter the experiment.
    tables=[('FED','2024-08-09 23:00:00',FED,('2025-01-29','2025-03-19','2025-05-07','2025-06-18','2025-07-30','2025-09-17','2025-10-29','2025-12-10',
             '2026-01-28','2026-03-18','2026-04-29','2026-06-17','2026-07-29','2026-09-16','2026-10-28','2026-12-09')),
            ('RBI','2025-03-27 00:00:00',RBI25,('2025-04-09','2025-06-06','2025-08-07','2025-10-01','2025-12-05','2026-02-06')),
            ('RBI','2026-03-24 00:00:00',RBI26,('2026-04-08','2026-06-05','2026-08-05','2026-10-07','2026-12-04'))]
    rows=[]
    for family,known,source,days in tables:
        for day in days:
            estimated=(pd.Timestamp(day+' 14:00',tz='America/New_York').tz_convert(IST).tz_localize(None) if family=='FED' else pd.Timestamp(day+' 10:00'))
            rows.append(dict(family=family,public_by=known,scheduled_local=estimated.isoformat(sep=' '),date=day,
                             precision='announced statement hour' if family=='FED' else 'published meeting-end date, model uses date only',source=source))
    write('policy-schedule.csv',pd.DataFrame(rows))

def jobs(tasks,workers=8):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for j,item in enumerate(ex.map(lambda x:grab(*x),tasks),1):
            if j%120==0:
                print('Archive requests checked',j,'of',len(tasks),flush=True)
            yield item

def additional():
    release_table()
    docs=list(jobs([(v,f'sources/official/{k}.html.gz',None) for k,v in RELEASES.items()],5))
    c=csv('official-stock-breadth.csv',V17)
    all_days=csv('official-index-closes.csv',V11).iloc[:,0].astype(str)
    days=sorted(set(c.day)|set(all_days[all_days.between(FIRST,FREEZE)]))
    seed=set(csv('issuer-seed.csv').stock)
    primary=ARCH+'/products/content/sec_bhavdata_full_{}.csv'
    participant=ARCH+'/content/nsccl/fao_participant_oi_{}.csv'
    extra=ARCH+'/content/cm/BhavCopy_NSE_CM_0_0_0_{}_F_0000.csv.zip'
    task=[]
    for d in days:
        ab=pd.Timestamp(d).strftime('%d%m%Y')
        if d not in set(c.day):
            task.append((extra.format(d.replace('-','')),f'sources/early-cash/{d}.zip','zip'))
        task.append((primary.format(ab),f'sources/delivery/{d}.csv.gz','csv'))
        task.append((participant.format(ab),f'sources/participants/{d}.csv.gz','csv'))
    for m in pd.date_range(FIRST,FREEZE,freq='MS'):
        end=min(m+pd.offsets.MonthEnd(),pd.Timestamp(FREEZE))
        for cat in ('bulk_deals','block_deals'):
            url=BULK+'?'+urlencode({'optionType':cat,'from':m.strftime('%d-%m-%Y'),'to':end.strftime('%d-%m-%Y')})
            task.append((url,f'sources/deals/{cat}-{m:%Y-%m}.json.gz','json'))
    receipts=list(jobs(task))
    save('non-price-sources.json',dict(documentation=docs,records=receipts))
    delivery=[];participants=[];deals=[];equity=[]
    from research.nifty_forecast_v17.acquire import cash_frame
    for x in receipts:
        p=OUT/x['file'] if x.get('file') else None
        if p is None:continue
        try:
            if p.parent.name=='delivery':
                t=pd.read_csv(io.BytesIO(unpack(p)),skipinitialspace=True,low_memory=False)
                d=p.name[:10]
                t=t.loc[t.SERIES.eq('EQ')&t.SYMBOL.isin(seed),['SYMBOL','DATE1','DELIV_QTY','DELIV_PER','TTL_TRD_QNTY']].copy()
                if not pd.to_datetime(t.DATE1,format='%d-%b-%Y',errors='coerce').dt.strftime('%Y-%m-%d').eq(d).all():continue
                for k in ('DELIV_QTY','DELIV_PER','TTL_TRD_QNTY'):
                    t[k]=pd.to_numeric(t[k],errors='coerce')
                delivery.append(t.rename(columns={'SYMBOL':'symbol','DELIV_QTY':'delivery_qty','DELIV_PER':'delivery_pct','TTL_TRD_QNTY':'traded_qty'}).drop(columns='DATE1').assign(day=d))
            if p.parent.name=='participants':
                d=p.name[:10]
                raw=unpack(p)
                if pd.Timestamp(d).strftime('%b %d, %Y') not in raw.decode('utf8',errors='ignore')[:240] and pd.Timestamp(d).strftime('%b %d, %Y').replace(' 0',' ') not in raw.decode('utf8',errors='ignore')[:240]:
                    continue
                t=pd.read_csv(io.BytesIO(raw),skiprows=1,skipinitialspace=True).dropna(how='all')
                if t.columns[0].strip()!='Client Type':continue
                for _,row in t.iterrows():
                    typ=str(row.iloc[0]).strip()
                    if typ not in ('FII','DII','Pro','Client'):continue
                    vals={}
                    for k,v in row.iloc[1:].items():
                        if pd.notna(v):
                            vals[re.sub('[^a-z]+','_',str(k).lower()).strip('_')]=int(str(v).strip().replace(',','').split('.')[0])
                    participants.append(dict(day=d,participant=typ,**vals))
            if p.parent.name=='deals':
                t=json.loads(unpack(p))
                a=t.get('data',[]) if isinstance(t,dict) else t
                for row in a:
                    if not isinstance(row,dict):continue
                    d=next((row[k] for k in row if k.lower() in ('date','tradedate','bd_dt_date','bd_date') or k.lower().endswith('_dt_date')),None)
                    when=pd.to_datetime(d,format='mixed',dayfirst=True,errors='coerce')
                    if pd.isna(when) or not FIRST<=when.strftime('%Y-%m-%d')<=FREEZE:continue
                    deals.append(dict(day=when.strftime('%Y-%m-%d'),file=p.name,**{k:v for k,v in row.items() if k not in ('day','file')}))
            if p.parent.name=='early-cash':
                t=cash_frame(p)
                assert t.day.eq(p.stem).all()
                equity.append(t[t.series.eq('EQ')])
        except (KeyError,ValueError,pd.errors.ParserError,OSError):
            continue
    tables={'delivery-statistics.csv.gz':pd.concat(delivery,ignore_index=True) if delivery else pd.DataFrame(columns=['day','symbol','delivery_pct']),
            'participant-open-interest.csv.gz':pd.DataFrame(participants), 'bulk-block-events.csv.gz':pd.DataFrame(deals),
            'supplementary-equity-cash.csv.gz':pd.concat(equity,ignore_index=True) if equity else pd.DataFrame(columns=['day','stock'])}
    for name,data in tables.items():write(name,data)
    save('non-price-receipt.json',dict(accepted={k:{'rows':len(v),'days':int(v.day.nunique()) if 'day' in v else 0} for k,v in tables.items()},
         rule='Official delivery and derivatives participant files are dated EOD vintages. Past or next morning features use a guarded previous date. Bulk and block trade archives lack publication timestamps and enter a separate earlier-date-sensitive track. No FII cash flow inferred from derivatives positions.'))
    print('Additional market sources',[(k,len(v)) for k,v in tables.items()],flush=True)

def forward():
    from research.nifty_forecast_v16 import acquire
    original=(acquire.OUT,acquire.save)
    try:
        acquire.OUT=OUT
        acquire.save=save
        acquire.forward()
    finally:
        acquire.OUT,acquire.save=original
    f=read('forward-ledger.json')
    f['previous_v17_refresh']=read('forward-ledger.json',V17)['checked_at']
    f['new_v18_issues']=0
    f.pop('new_v16_issues',None)
    save('forward-ledger.json',f)

if __name__=='__main__':
    {'additional':additional,'forward':forward}[sys.argv[1]]()
