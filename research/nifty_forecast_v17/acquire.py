"""Read-only NSE identity and traded-asset history acquisition."""
from concurrent.futures import ThreadPoolExecutor
import io
import time
import threading
import sys
import zipfile
from urllib.parse import quote, urlencode
import requests
from research.nifty_forecast_v15.sources import token, API
from .common import *

NSEARCH='https://nsearchives.nseindia.com'
NSE='https://www.nseindia.com'
REPORT_URL=NSEARCH+'/content/cm/BhavCopy_NSE_CM_0_0_0_{date}_F_0000.csv.zip'
ETFS={'NIFTYBEES':'NSE_EQ|INF204KB14I2','BANKBEES':None}
DOCS={
 'nse-preopen':NSE+'/static/products-services/equity-market-pre-open',
 'nse-eod':NSE+'/static/market-data/eod-historical-data-subscription',
 'nse-index-method':NSEARCH+'/content/indices/Nifty_Broad_Market_Indices_Methodology.pdf',
 'nse-holiday':'https://archives.nseindia.com/content/circulars/CMTR71775.pdf',
 'nse-actions':NSE+'/companies-listing/corporate-filings-actions',
 'nse-announcements':NSE+'/companies-listing/corporate-filings-announcements',
 'nse-bulk-block':NSE+'/report-detail/display-bulk-and-block-deals',
 'nse-institutional':NSE+'/reports/fii-dii',
 'nse-index-dated':'https://www.niftyindices.com/resources/index-reconstitution',
 'upstox-candle':'https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/',
 'upstox-expired':'https://upstox.com/developer/api-documentation/expired-instruments/',
 'upstox-live-depth':'https://upstox.com/developer/api-documentation/v3/get-market-data-feed/',
 'nseix-dated-contracts':'https://www.nseix.com/markets/reports',
}
ACTION_LIST=['2025-01-01','2025-12-31','2026-01-01','2026-11-17']


def fetch(url,file,auth=None,kind='blob',tries=3):
    record=dict(url=url,sent=now())
    if file.exists():
        record.update(status=200,cache=True,file=file.relative_to(OUT).as_posix(),sha256=sha(file),bytes=file.stat().st_size)
        if kind=='candles':
            record.update(inspect_candles(gzip.decompress(file.read_bytes())))
        return record
    headers={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/csv,*/*','Referer':NSE+'/'}
    if auth:
        headers['Authorization']='Bearer '+auth
    for retry in range(tries):
        try:
            r=requests.get(url,headers=headers,timeout=(6,17))
            record.update(status=r.status_code,received=now(),server_date=r.headers.get('Date'))
            if r.ok and r.content:
                payload=r.content
                if kind=='zip' and payload[:2]!=b'PK':
                    record['invalid_payload']='wrong archive format'
                    break
                if kind in ('candles','json'):
                    data=r.json()
                    if kind=='candles':
                        details=inspect_candles(payload)
                        record.update(details)
                        if details['bars']==0:
                            record['reason']='provider returned an empty candle payload'
                            break
                file.parent.mkdir(parents=True,exist_ok=True)
                temporary=file.with_name(f'.{file.name}.{os.getpid()}.{threading.get_ident()}.partial')
                temporary.write_bytes(gzip.compress(payload,compresslevel=3,mtime=0) if file.suffix=='.gz' else payload)
                try:
                    os.link(temporary,file)
                except FileExistsError:
                    record['concurrent_cache']=True
                    if kind=='candles':
                        record.update(inspect_candles(gzip.decompress(file.read_bytes())))
                finally:
                    temporary.unlink()
                record.update(file=file.relative_to(OUT).as_posix(),bytes=file.stat().st_size,sha256=sha(file))
                break
            try:
                err=r.json()
                record['api_errors']=[dict(code=e.get('errorCode',e.get('error_code')),message=str(e.get('message',''))[:180])
                                      for e in err.get('errors',[])] if isinstance(err,dict) else []
            except ValueError:
                pass
            if r.status_code not in (429,500,502,503,504):
                break
            time.sleep(1.0+retry*1.5)
        except (requests.RequestException,ValueError) as e:
            record['exception']=type(e).__name__
    return record


def inspect_candles(payload):
    x=json.loads(payload)
    d=x.get('data') or {}
    c=d.get('candles',[]) if isinstance(d,dict) else []
    return dict(bars=len(c),first_ts=min((a[0] for a in c),default=None),last_ts=max((a[0] for a in c),default=None))


def cash_frame(file):
    with zipfile.ZipFile(file) as z:
        ns=[k for k in z.namelist() if k.endswith('.csv')]
        assert len(ns)==1
        t=pd.read_csv(io.BytesIO(z.read(ns[0])),low_memory=False)
    cols={'TradDt':'day','TckrSymb':'stock','SctySrs':'series','ISIN':'isin','OpnPric':'open','HghPric':'high','LwPric':'low',
          'ClsPric':'close','PrvsClsgPric':'previous_close','TtlTradgVol':'volume','TtlTrfVal':'turnover','TtlNbOfTxsExctd':'trades'}
    assert set(cols).issubset(t.columns),list(t.columns)
    return t[list(cols)].rename(columns=cols)


def daily_download(days):
    def go(d):
        fmt=d.replace('-','')
        api=REPORT_URL.format(date=fmt)
        file=OUT/'sources'/'cash-eod'/(d+'.zip')
        return dict(day=d,**fetch(api,file,kind='zip'))
    with ThreadPoolExecutor(max_workers=7) as pool:
        return list(pool.map(go,days))


def seeds():
    received=daily_download(SEEDS)
    frames=[]
    for r in received:
        if 'file' not in r:continue
        f=cash_frame(OUT/r['file'])
        assert f.day.eq(r['day']).all()
        frames.append(f[f.series.eq('EQ')])
    assert len(frames)>=3,received
    seed=pd.concat(frames,ignore_index=True)
    u=seed.groupby(['stock','isin'],as_index=False).agg(seeds=('day','nunique'),avg_turnover=('turnover','mean'),volume=('volume','sum'))
    rows=[]
    for sector,(n,names) in SLEEVES.items():
        p=u[u.stock.isin(names)&u.seeds.ge(3)&u.avg_turnover.gt(0)].sort_values(['avg_turnover','stock'],ascending=[False,True]).head(n)
        for rank,r in enumerate(p.itertuples(index=False),1):
            rows.append(dict(sector=sector,rank=rank,stock=r.stock,isin=r.isin,seed_days=r.seeds,seed_turnover=r.avg_turnover,
                             instrument='NSE_EQ|'+r.isin,frozen_after=SEEDS[-1],coverage_class='dated January NSE cash eligibility'))
    master=json.loads(gzip.decompress((V5/'metadata/NSE.json.gz').read_bytes()))
    for name,key0 in ETFS.items():
        key=key0 or next((m['instrument_key'] for m in master if m.get('trading_symbol')==name and m.get('segment')=='NSE_EQ'),None)
        if key:
            rows.append(dict(sector='ETF',rank=1,stock=name,isin=key.split('|')[-1],instrument=key,frozen_after=SEEDS[-1],
                             coverage_class='ETF instrument identity'))
    assert len(rows)>=27
    t=pd.DataFrame(rows)
    write('historical-stock-basket.csv',t)
    save('stock-eligibility-receipt.json',dict(seeds=received,basket_equities=int(t.sector.ne('ETF').sum()),etfs=t[t.sector.eq('ETF')].stock.tolist(),
      decision='A fixed January 2025 turnover-ranked research basket within predeclared sector sleeves. Official constituent histories and weights remain separate.',
      original_index_anchor='Confirmed identity via NSE daily cash archive; index membership and official historical free-float weights were not reconstructed.'))
    return t


def stock_minutes():
    register()
    target=OUT/'historical-stock-basket.csv'
    basket=pd.read_csv(target) if target.is_file() else seeds()
    k=token()
    jobs=[]
    for r in basket.itertuples(index=False):
        for d in pd.date_range(FIRST,FREEZE,freq='MS'):
            begin=d.strftime('%Y-%m-%d')
            end=min(d+pd.offsets.MonthEnd(),pd.Timestamp(FREEZE)).strftime('%Y-%m-%d')
            jobs.append((r.stock,r.instrument,begin,end))
    def go(t):
        name,key,a,b=t
        p=OUT/'sources'/'stock-minute'/name/(a+'.json.gz')
        return dict(stock=name,begin=a,end=b,instrument=key,**fetch(API+quote(key,safe='')+f'/minutes/5/{b}/{a}',p,k,'candles'))
    done=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for i,r in enumerate(pool.map(go,jobs),1):
            done.append(r)
            if i%120==0:
                print('Stock candle payloads checked',i,'/',len(jobs),flush=True)
    save('stock-candle-receipt.json',dict(records=done,requested=len(jobs),successful=sum('file' in x for x in done),
        total_bars=sum(x.get('bars',0) for x in done),timestamp_model='5 minute intervals, timestamp at start, 5 minute allowance after bar end'))
    print('Saved',sum(x.get('bars',0) for x in done),'stock and ETF bars',flush=True)


def equity_daily():
    t=matrix('cash-panel/cash.csv',V16)
    job=sorted(set(t.index)|set(SEEDS))
    out=daily_download(job)
    frames=[]
    for r in out:
        if 'file' not in r:continue
        x=cash_frame(OUT/r['file'])
        assert x.day.eq(r['day']).all()
        frames.append(x[x.series.eq('EQ')])
    a=pd.concat(frames,ignore_index=True)
    write('official-equity-daily.csv.gz',a)
    save('official-equity-receipt.json',dict(records=out,accepted=len(frames),rows=len(a)))
    print('Archived',len(a),'dated NSE cash rows over',len(frames),'sessions',flush=True)


def reconcile_cash_receipts():
    books={'official-equity-receipt.json':'records','stock-eligibility-receipt.json':'seeds'}
    rows=[]
    for filename,key in books.items():
        book=read(filename)
        dirty=False
        for record in book[key]:
            if not record.get('file'):
                continue
            path=OUT/record['file']
            current=sha(path)
            if record['sha256']==current:
                continue
            day=record['day']
            actual=cash_frame(path)
            actual=actual.loc[actual.series.eq('EQ')].reset_index(drop=True)
            kept=pd.read_csv(OUT/'official-equity-daily.csv.gz',low_memory=False)
            earlier=kept.loc[kept.day.eq(day),actual.columns].reset_index(drop=True)
            pd.testing.assert_frame_equal(actual,earlier,check_dtype=False,rtol=1e-12,atol=0.)
            record['initial_receipt_sha256']=record['sha256']
            record['sha256']=current
            record['bytes']=path.stat().st_size
            record['cache_reconciled_at']=now()
            rows.append(dict(book=filename,day=day,archived=record['file'],earlier_hash=record['initial_receipt_sha256'],
                             archived_hash=current,unchanged_equity_rows=len(actual)))
            dirty=True
        if dirty:
            save(filename,book)
    if rows or not (OUT/'cash-archive-reconciliation.json').exists():
        save('cash-archive-reconciliation.json',dict(checked_at=now(),reconciled=rows,
           verification='Existing official EQ input and the retained ZIP matched record for record. Raw concurrent archive digests are retained when they differed.'))
    print('Reconciled cash archive receipts',len(rows),flush=True)


def probes():
    auth=token()
    root=OUT/'sources'/'source-probes'
    jobs=[(name,url,root/(name+'.bin'),None,'blob') for name,url in DOCS.items()]
    for first,last in zip(ACTION_LIST[::2],ACTION_LIST[1::2]):
        for u,slug in [('corporates-corporateActions','corporate-action'),('corporate-announcements','announcements')]:
            target=urlencode(dict(index='equities',from_date=pd.Timestamp(first).strftime('%d-%m-%Y'),to_date=pd.Timestamp(last).strftime('%d-%m-%Y')))
            name=f'{slug}-{first[:4]}'
            jobs.append((name,NSE+f'/api/{u}?'+target,root/(name+'.json.gz'),None,'json'))
    nxt={'fii-dii-history':NSE+'/reports/fii-dii','bulk-sample':NSEARCH+'/content/equities/bulk_deals_28102026.csv',
         'block-sample':NSEARCH+'/content/equities/block_deals_28102026.csv'}
    for name,url in nxt.items():
        jobs.append((name,url,root/(name+'.bin'),None,'blob'))
    under='NSE_INDEX|Nifty 50'
    for name,q in [('nifty-expiries','expiries?'+urlencode(dict(instrument_key=under))),
                   ('nifty-future-october','future/contract?'+urlencode(dict(instrument_key=under,expiry_date='2026-10-27')))]:
        jobs.append((name,CONTRACT_HTTP+q,root/(name+'.json.gz'),auth,'json'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        a=list(pool.map(lambda x:dict(name=x[0],**fetch(*x[1:])),jobs))
    future=root/'nifty-future-october.json.gz'
    if future.is_file():
        result=read(future.relative_to(OUT).as_posix()).get('data') or []
        if isinstance(result,list):
            for i,q in enumerate(result[:3]):
                key=q.get('instrument_key',q.get('expired_instrument_key'))
                if key:
                    name=f'nifty-future-bars-probe-{i}'
                    base=CONTRACT_HTTP+'historical-candle/'+quote(key,safe='')
                    url=base+'/1minute/2026-10-27/2026-10-20'
                    a.append(dict(name=name,instrument=key,**fetch(url,root/(name+'.json.gz'),auth,'candles')))
    save('new-source-availability.json',dict(probes=a,scope='Official archives and documented authenticated endpoints. No current-session book or trading APIs queried.'))
    for q in a:
        if 'future' in q['name'] or 'action' in q['name'] or 'announce' in q['name']:
            print(q['name'],q.get('status'),q.get('bars'),flush=True)


def extensions():
    roster=pd.read_csv(OUT/'historical-stock-basket.csv')
    o=pd.read_csv(OUT/'official-equity-daily.csv.gz',usecols=['day','stock','isin'])
    o=o[o.stock.isin(roster.stock)]
    p=o.groupby(['stock','isin'],as_index=False).agg(first=('day','min'),last=('day','max'),rows=('day','size'))
    p=p.merge(roster[['stock','isin']].rename(columns={'isin':'jan_isin'}),on='stock',validate='many_to_one')
    write('stock-identifier-history.csv',p)
    native={
      'bank':'NSE_INDEX|Nifty Bank','finance':'NSE_INDEX|Nifty Fin Service','it':'NSE_INDEX|Nifty IT',
      'energy':'NSE_INDEX|Nifty Energy','auto':'NSE_INDEX|Nifty Auto','defensive':'NSE_INDEX|Nifty FMCG',
      'broad':'NSE_INDEX|Nifty 500',
    }
    master=json.loads(gzip.decompress((V5/'metadata/NSE.json.gz').read_bytes()))
    labels={str(r.get('trading_symbol','')).casefold():r['instrument_key'] for r in master
            if r.get('segment')=='NSE_INDEX' and r.get('instrument_key')}
    native.update({k:labels.get(v.split('|')[-1].casefold(),v) for k,v in native.items()})
    jobs=[]
    for t in p.itertuples(index=False):
        if t.isin==t.jan_isin:continue
        jobs.append((t.stock,'NSE_EQ|'+t.isin,t.first,t.last,'identity'))
    for k,v in native.items():
        jobs.append((k,v,FIRST,FREEZE,'native'))
    windows=[]
    for name,key,begin,end,origin in jobs:
        for start in pd.date_range(pd.Timestamp(begin).replace(day=1),end,freq='MS'):
            a=max(start,pd.Timestamp(begin)).strftime('%Y-%m-%d')
            b=min(start+pd.offsets.MonthEnd(),pd.Timestamp(end)).strftime('%Y-%m-%d')
            windows.append((name,key,a,b,origin))
    auth=token()
    def go(x):
        name,key,a,b,src=x
        ident=key.split('|')[-1] if src=='identity' else 'index'
        f=OUT/'sources'/('minute-'+src)/name/(ident+'-'+a+'.json.gz')
        return dict(stock=name,instrument=key,begin=a,end=b,group=src,
              **fetch(API+quote(key,safe='')+f'/minutes/5/{b}/{a}',f,auth,'candles'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        a=list(pool.map(go,windows))
    save('intraday-extensions-receipt.json',dict(records=a,native=native))
    print('Identity transitions and synchronized native histories:',sum(r.get('bars',0) for r in a),'bars',flush=True)


def forward():
    # V16 forward resolver is reused with its entire output root and writer scoped to V17.
    from research.nifty_forecast_v16 import acquire as v16
    keep=(v16.OUT,v16.save)
    try:
        v16.OUT=OUT
        v16.save=save
        v16.forward()
    finally:
        v16.OUT,v16.save=keep
    f=read('forward-ledger.json')
    f.update(previous_v16_checked_at=read('forward-ledger.json',V16)['checked_at'],new_v17_issues=0)
    f.pop('new_v16_issues',None)
    save('forward-ledger.json',f)

if __name__=='__main__':
    {'sources':probes,'stocks':stock_minutes,'eod':equity_daily,'forward':forward,'extensions':extensions,
     'reconcile_cash':reconcile_cash_receipts}[sys.argv[1]]()
