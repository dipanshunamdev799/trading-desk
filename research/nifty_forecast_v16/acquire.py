"""Acquire read-only provenance and test authenticated offshore quote coverage."""
from concurrent.futures import ThreadPoolExecutor
import sys
from urllib.parse import quote

import requests
from research.nifty_forecast_v15.sources import API, NSE, token
from research.nifty_forecast_v4.ledger import events, verify_files
from research.nifty_forecast_v4.distributions import Distribution

from .common import *

DOCS={
 'nse-auction':'https://www.nseindia.com/static/products-services/equity-market-pre-open',
 'nse-timings':'https://www.nseindia.com/static/market-data/market-timings',
 'nse-stock-feed':'https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Real%20time_Stock_Product_V1.4.pdf',
 'nse-2026-holidays':'https://archives.nseindia.com/content/circulars/CMTR71775.pdf',
 'nifty-index-method':'https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf',
 'nseix-extended':'https://www.nseix.com/web/pressrelease/2026-11/PR_CC_03112026_20261103101702.pdf',
 'nseix-contracts':'https://www1.nseix.com/web/contentpage/2026-11/NSEIX__GIFT_Nifty_and_SSFs_Deck_20261104131032.pdf',
 'nseix-reports':'https://www.nseix.com/markets/reports',
 'upstox-global':'https://upstox.com/developer/api-documentation/announcements/global-instruments/',
 'upstox-history':'https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/',
}

def request(name,url,auth=None,folder='sources/acquisition'):
    row=dict(name=name,url=url,sent=now())
    headers={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/csv,*/*'}
    if auth:
        headers['Authorization']='Bearer '+auth
    try:
        r=requests.get(url,headers=headers,timeout=(7,15))
        row.update(status=r.status_code,server_date=r.headers.get('Date'),received=now())
        if r.ok and r.content:
            binary=r.content
            suffix='pdf' if binary.startswith(b'%PDF') else 'json' if binary[:1] in {b'[',b'{'} else 'txt'
            if url.endswith('.csv'):
                suffix='csv'
            path=OUT/folder/(name+'.'+suffix)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(binary)
            row.update(file=path.relative_to(OUT).as_posix(),sha256=sha(path),bytes=len(binary))
            if auth:
                x=r.json()
                rows=x.get('data',{}).get('candles',[]) if isinstance(x,dict) else []
                row.update(candles=len(rows),stamp_min=min((t[0] for t in rows),default=None),
                           stamp_max=max((t[0] for t in rows),default=None),stamp_times=sorted({z[0][11:16] for z in rows})[:40])
        else:
            try:
                x=r.json()
                row['errors']=[{'code':e.get('errorCode',e.get('error_code')),'message':str(e.get('message',''))[:250]} for e in x.get('errors',[])]
            except (ValueError,AttributeError):
                pass
    except (requests.RequestException,ValueError) as e:
        row.update(error=type(e).__name__,received=now())
    return row

def hurl(key,span,start,end):
    return API+quote(key,safe='')+f'/{span}/{end}/{start}'

def sources():
    register()
    m=V5/'metadata/global.json.gz'
    inventory=json.loads(gzip.decompress(m.read_bytes()))
    copy=[{k:v for k,v in r.items()} for r in inventory]
    save('upstox-global-inventory.json',dict(source=m.relative_to(ROOT).as_posix(),sha256=sha(m),entries=copy))
    keys={str(r.get('trading_symbol','')):r.get('instrument_key') for r in inventory}
    auth=token()
    gif=next((r['instrument_key'] for r in inventory if r.get('name','').upper()=='GIFT NIFTY'),'GLOBAL_INDEX|SGX NIFTY')
    jobs=[(f'doc-{k}',u,None) for k,u in DOCS.items()]
    for sym in ['SGX NIFTY','^NDX','^IXIC','^GSPC','^N225','^HSI','US Tech 100','^GDAXI','USDINR']:
        k=keys.get(sym)
        if not k:
            continue
        label=''.join(c for c in sym if c.isalnum()).lower()
        for span in ('minutes/5','minutes/25','hours/1') if k==gif else ('minutes/5',):
            jobs.append((label+'-'+span.replace('/','-'),hurl(k,span,'2026-11-06','2026-11-17'),auth))
        if k==gif:
            for span in ('minutes/5','hours/1'):
                jobs.append((label+'-older-'+span.replace('/','-'),hurl(k,span,'2025-06-09','2025-06-20'),auth))
    if gif not in [keys.get('SGX NIFTY')]:
        jobs.append(('gift-minutes-5',hurl(gif,'minutes/5','2026-11-06',FREEZE),auth))
    # Retain the vendor daily series independently of any successful contract-level search.
    jobs.append(('gift-daily',hurl(gif,'days/1',FIRST,FREEZE),auth))
    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts=list(pool.map(lambda x:request(*x),jobs))
    save('source-attempts.json',dict(records=receipts,gift_key=gif,daily_vendor_archive=(V5/'sources/g_SGX_NIFTY.json').relative_to(ROOT).as_posix()))
    print('Archived',sum('file' in x for x in receipts),'of',len(receipts),'documentation and data probes',flush=True)
    for r in receipts:
        if 'upstox.com/v3' in r['url']:
            print(r['name'],r.get('status'),r.get('candles'),r.get('stamp_times',[])[:3],flush=True)

def official_row(f,day):
    d=pd.read_csv(f,skipinitialspace=True)
    x=d.loc[d['Index Name'].str.strip().str.casefold().eq('nifty 50')]
    if len(x)!=1 or not pd.to_datetime(x['Index Date'],dayfirst=True).dt.strftime('%Y-%m-%d').eq(day).all():
        raise ValueError('Daily archive does not identify the expected NIFTY 50 observation')
    cols={'open':'Open Index Value','high':'High Index Value','low':'Low Index Value','close':'Closing Index Value'}
    return {a:float(x[b].iloc[0]) for a,b in cols.items()}

def forward():
    at=pd.Timestamp(now()).tz_convert(IST)
    bound=(at-pd.Timedelta(days=int(at.hour<16))).strftime('%Y-%m-%d')
    assert '2026-11-18'<=bound<=END
    target_folder='forward/'+at.strftime('%Y-%m-%dT%H%M%S')
    auth=token()
    rows=[request(k,hurl(v,'days/1','2026-11-18',bound),auth,target_folder) for k,v in
          [('nifty','NSE_INDEX|Nifty 50'),('vix','NSE_INDEX|India VIX'),
           ('bank','NSE_INDEX|Nifty Bank'),('broad','NSE_INDEX|Nifty 500')]]
    daily=(OUT/rows[0]['file']) if 'file' in rows[0] else None
    pairs=[]
    if daily:
        for ts,o,h,l,c,*_ in json.loads(daily.read_text(encoding='utf-8'))['data']['candles']:
            d=pd.Timestamp(ts).tz_convert(IST).strftime('%Y-%m-%d')
            if '2026-11-18'<=d<=bound:
                pairs.append((d,list(map(float,(o,h,l,c)))))
    calendar=dict(day='2026-11-24',status='NSE cash holiday',reason='Guru Nanak Jayanti',
                  notice=DOCS['nse-2026-holidays'])
    official=[]; certified={}
    # Every expected date gets a receipt, even when an input is omitted by the provider.
    supported={day:value for day,value in pairs}
    expected=[d.strftime('%Y-%m-%d') for d in pd.bdate_range('2026-11-18',bound) if d.strftime('%Y-%m-%d')!=calendar['day']]
    for d in sorted(set(expected)|set(supported)):
        q=request('NSE-'+d,NSE+pd.Timestamp(d).strftime('%d%m%Y')+'.csv',None,target_folder)
        state='awaiting authoritative reconciliation'
        q['upstox_ohlc']=supported.get(d)
        if 'file' in q and (OUT/q['file']).suffix=='.csv':
            try:
                mark=official_row(OUT/q['file'],d)
                q['nse_ohlc']=mark
                if d in supported and max(abs(a-b) for a,b in zip(mark.values(),supported[d]))<=.05:
                    state='verified'
                    certified[d]=mark['close']
            except (ValueError,KeyError,pd.errors.ParserError):
                state='archive identity discrepancy'
        official.append({**q,'http_status':q.get('status'),'day':d,'status':state})
    old=read('forward-ledger.json',V15)
    original_v4=events(V4/'prospective-ledger.jsonl')
    for item in original_v4:
        verify_files(item)
    v4={(item['key'],int(h)): r for item in original_v4 if item['kind']=='FORECAST' for h,r in item['payload']['forecasts'].items()}
    v5=read('experimental-forecasts.json',V5)['forecasts']
    assert sha(V5/'experimental-forecasts.json')==old['v5_issue_file_hash']
    assert sha(V4/'prospective-ledger.jsonl')==old['v4_issue_file_hash']
    rec=[]
    for r in old['records']:
        days=r['target_sessions']
        terminal=days[-1]
        status='pending completion and publication'; y=None;scores={}
        if stamp(terminal,'18:00')<=at:
            actual=[d for d in sorted(certified) if r['reference_session']<d<=terminal]
            if actual==days:
                y=certified[terminal]/r['reference_close']-1
                status='resolved on original target'
                distrib=v4[r['key'],r['horizon']]['distributions'] if r['version']=='V4' else {r['key']:v5[r['key']]}
                for name,x in distrib.items():
                    z=Distribution(x['atoms'],x['weights']).score(y)
                    scores[name]={a:z[a] for a in ('brier','log_loss','crps','p','predicted_mean')}
            else:
                status='awaiting full authoritative match to original session sequence'
        ex={k:v for k,v in r.items() if k not in {'scores','maturity','realized_return','official_close','completed_target_dates'}}
        rec.append(dict(**ex,maturity=status,official_close=certified.get(terminal) if y is not None else None,
                        realized_return=y,scores=scores,completed_target_dates=[d for d in days if d in certified]))
    receipt=dict(checked_at=at.isoformat(),bound=bound,closure=calendar,sessions=official,sources=rows,records=rec,
                 v4_sha256=old['v4_issue_file_hash'],v5_sha256=old['v5_issue_file_hash'],new_v16_issues=0)
    save(target_folder+'/receipt.json',receipt)
    save('forward-ledger.json',receipt)
    print('Forward reconciliation:',len(certified),'cash sessions and',sum(r['realized_return'] is not None for r in rec),'mature issues',flush=True)


def minute_series():
    capture=read('source-attempts.json')
    k=capture['gift_key']
    plans=[('gift',k,5),('nikkei','GLOBAL_INDEX|^N225',25),('hsi','GLOBAL_INDEX|^HSI',25),
           ('spx','GLOBAL_INDEX|^GSPC',25),('us_tech','GLOBAL_INDEX|IXIX',25),
           ('fx','GLOBAL_INDICATOR|USDINR',25),('brent','GLOBAL_INDICATOR|BZUSD',25)]
    auth=token()
    tasks=[]
    for name,code,minute in plans:
        step=pd.offsets.MonthEnd() if minute<=15 else pd.offsets.QuarterEnd()
        freq='MS' if minute<=15 else 'QS'
        for s in pd.date_range(FIRST,FREEZE,freq=freq):
            begin=s.strftime('%Y-%m-%d')
            end=min(s+step,pd.Timestamp(FREEZE)).strftime('%Y-%m-%d')
            tasks.append((name,code,minute,begin,end))
    def load(x):
        name,code,minute,a,b=x
        r=request(f'{name}-{a}',hurl(code,f'minutes/{minute}',a,b),auth,'sources/foreign-intraday')
        return dict(series=name,instrument=code,bar_minutes=minute,begin=a,end=b,**r)
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs=list(pool.map(load,tasks))
    save('foreign-intraday-acquisition.json',dict(records=jobs,instrument_contract='Upstox global instrument keys. OHLC vendor candles without per-contract identifiers or exchange receipt timestamps.'))
    print('Intraday',sum(x.get('candles',0) for x in jobs),'bars in',sum(bool(x.get('candles')) for x in jobs),'files /',len(jobs),'requests',flush=True)

if __name__=='__main__':
    {'sources':sources,'forward':forward,'intraday':minute_series}[sys.argv[1]]()

