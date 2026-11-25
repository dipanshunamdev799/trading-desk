"""Read-only historical inputs and issue-ledger resolution in a separate vintage."""
from datetime import time
from urllib.parse import quote
import gzip
import io
import sys
import time as clock

import requests

from .common import *
from research.nifty_forecast_v4.ledger import events, verify_files
from research.nifty_forecast_v4.distributions import Distribution

API='https://api.upstox.com/v3/historical-candle/'
NSE='https://nsearchives.nseindia.com/content/indices/ind_close_all_'


def token():
    sys.path.insert(0,str(ROOT/'backend'))
    from app.config import get_settings
    return get_settings().upstox_analytics_token


def get_upstox(http,url,auth,file):
    row=dict(url=url,sent=now())
    for retry in range(2):
        clock.sleep(.37)
        try:
            r=http.get(url,headers={'Authorization':'Bearer '+auth,'Accept':'application/json'},timeout=15)
            row.update(status=int(r.status_code),received=now(),server_date=r.headers.get('Date'))
            if r.ok and 'candles' in r.json().get('data',{}):
                file.parent.mkdir(parents=True,exist_ok=True)
                file.write_bytes(r.content)
                break
            if r.status_code not in (429,500,502,503,504):
                break
            clock.sleep(1)
        except (requests.RequestException,ValueError) as e:
            row['unavailable']=type(e).__name__
    if file.exists():
        candle=read(file.name,file.parent)['data']['candles']
        row.update(rows=len(candle),file=file.relative_to(OUT).as_posix(),sha256=sha(file))
    return row


def intraday():
    register()
    data=json.loads(gzip.decompress((V5/'metadata/NSE.json.gz').read_bytes()))
    lookup={str(a.get('trading_symbol','')).lower().replace(' ',''):a['instrument_key'] for a in data
            if a.get('instrument_key') and a.get('segment') in ('NSE_INDEX','NSE_EQ')}
    wanted={'broad':'nifty500','equal':'nifty500equalweight','etf':'niftybees','defensive':'niftyfmcg'}
    inventory=[];requests_log=[]
    cached=OUT/'sources/market-intraday'
    auth=token()
    with requests.Session() as http:
        for label,symbol in wanted.items():
            key=lookup.get(symbol)
            inventory.append(dict(label=label,symbol=symbol,instrument=key))
            if not key:
                continue
            for start in pd.date_range(FIRST,FREEZE,freq='QS'):
                stop=min(pd.Timestamp(FREEZE),start+pd.offsets.QuarterEnd())
                first,last=str(start.date()),str(stop.date())
                url=API+quote(key,safe='')+f'/minutes/25/{last}/{first}'
                file=cached/f'{label}-{first}.json'
                if file.is_file():
                    res=dict(url=url,rows=len(read(file.name,file.parent)['data']['candles']),
                             file=file.relative_to(OUT).as_posix(),sha256=sha(file),status='replay')
                else:
                    res=get_upstox(http,url,auth,file)
                requests_log.append(dict(label=label,begin=first,end=last,**res))
    save('intraday-acquisition.json',dict(inventory=inventory,requests=requests_log,
         coverage='Archive candle timestamps label bar start. Intraday research admits completed bars with five minute buffers.'))
    print('Archived',sum('file' in r for r in requests_log),'historical intraday payloads of',len(requests_log),flush=True)


def closing_table(raw):
    df=pd.read_csv(io.BytesIO(raw))
    df.columns=df.columns.str.strip()
    match=df[df['Index Name'].astype(str).str.strip().str.upper().eq('NIFTY 50')]
    if len(match)!=1:
        raise ValueError('Official index identity missing or ambiguous')
    return float(match.iloc[0]['Closing Index Value'])


def distribution_scores(items,realized):
    scores={}
    for key,f in items.items():
        val=Distribution(f['atoms'],f['weights']).score(realized)
        scores[key]={i:float(val[i]) for i in ['p','predicted_mean','predicted_median','brier','crps','log_loss','mae']}
    return scores


def forward():
    stamp=pd.Timestamp(now()).tz_convert('Asia/Kolkata')
    assert FIRST<=str(stamp.date())<=LAST
    cutoff=str((stamp-pd.Timedelta(days=int(stamp.time()<time(16)))).date())
    begin='2026-11-18'
    folder=OUT/'forward'/stamp.strftime('%Y-%m-%dT%H%M%S')
    folder.mkdir(parents=True,exist_ok=True)
    auth=token()
    refresh=[]
    with requests.Session() as http:
        for name,key in [('nifty','NSE_INDEX|Nifty 50'),('india-vix','NSE_INDEX|India VIX'),
                         ('bank','NSE_INDEX|Nifty Bank'),('nifty500','NSE_INDEX|Nifty 500')]:
            url=API+quote(key,safe='')+f'/days/1/{cutoff}/{begin}'
            refresh.append(dict(instrument=name,**get_upstox(http,url,auth,folder/f'{name}.json')))
        provider=read('nifty.json',folder)['data']['candles'] if (folder/'nifty.json').exists() else []
        actual={}
        for row in provider:
            day=pd.Timestamp(row[0]).tz_convert('Asia/Kolkata').date().isoformat()
            if begin<=day<=cutoff:
                actual[day]=dict(upstox_open=float(row[1]),upstox_high=float(row[2]),upstox_low=float(row[3]),
                                 upstox_close=float(row[4]))
        for day,entry in actual.items():
            url=NSE+pd.Timestamp(day).strftime('%d%m%Y')+'.csv'
            entry.update(source=url,checked_at=now(),status='awaiting NSE verification')
            try:
                r=http.get(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/csv,*/*'},timeout=9)
                r.raise_for_status()
                close=closing_table(r.content)
                path=folder/f'NSE-{day}.csv'
                path.write_bytes(r.content)
                entry.update(nse_close=close,delta=entry['upstox_close']-close,
                    data_file=path.relative_to(OUT).as_posix(),sha256=sha(path),
                    status='verified' if abs(entry['upstox_close']-close)<=.05 else 'source discrepancy')
            except (requests.RequestException,ValueError,KeyError,IndexError) as e:
                entry['reason']=type(e).__name__
    certified={k:v['nse_close'] for k,v in actual.items() if v['status']=='verified'}
    v4_path=V4/'prospective-ledger.jsonl'
    v4=events(v4_path)
    original=V5/'experimental-forecasts.json'
    v5=read(original.name,V5)
    control=read('frozen-benchmark-supplement.json',V5)
    ident=sha(original)
    assert ident==control['forecast_sha256']
    manifest=read('forecast-source-manifest.json',V5)
    for prior in v4:
        verify_files(prior)
    res=[]
    def status(ref,days):
        endpoint=days[-1]
        if pd.Timestamp(endpoint+' 18:00',tz='Asia/Kolkata')>stamp:
            return 'pending completion and publication',None
        if any(s not in certified for s in days):
            return 'awaiting authoritative session reconciliation',None
        observed=sorted(k for k in certified if ref<k<=endpoint)
        if observed!=days:
            return 'pending calendar review',None
        return 'resolved in V15 with authoritative outcome',certified[endpoint]
    for record in v4:
        if record['kind']!='FORECAST':
            continue
        x=record['payload']
        for h,r in x['forecasts'].items():
            days=r['target_sessions']
            flag,close=status(x['reference_session'],days)
            y=None if close is None else close/r['reference_close']-1
            p={k:float(v) for k,v in r['binary_probabilities'].items()}
            laws={k:v for k,v in r['distributions'].items()}
            arch=distribution_scores(laws,y) if y is not None else {}
            res.append(dict(version='V4',key=record['key'],horizon=int(h),issued=x['issued_at'],issue_hash=record['hash'],
                reference_session=x['reference_session'],reference_close=r['reference_close'],target=days[-1],target_sessions=days,
                issue_class='prospective before endpoint; late first-session diagnostic' if not x['primary_eligible'] else 'pre-open primary',
                completed_target_dates=[d for d in days if d in certified],maturity=flag,official_close=close,realized_return=y,
                original_probabilities=p,law_p_up={k:float(v['statistics']['p_up']) for k,v in laws.items() if 'statistics' in v},
                scores=arch,binary_scores={k:(v-int(y>0))**2 for k,v in p.items()} if y is not None else {}))
    for key,r in v5['forecasts'].items():
        days=r['target_sessions']
        flag,close=status(v5['reference_session'],days)
        y=None if close is None else close/v5['reference_close']-1
        eval_law={key:r}
        if r['horizon']==5:
            eval_law['weekly_empirical']=control['weekly_empirical']
        res.append(dict(version='V5',key=key,horizon=r['horizon'],issued=v5['issued_at'],issue_hash=ident,
            reference_session=v5['reference_session'],reference_close=v5['reference_close'],target=days[-1],target_sessions=days,
            issue_class='forward experimental before first target session',
            completed_target_dates=[d for d in days if d in certified],maturity=flag,official_close=close,realized_return=y,
            p_up=float(r['statistics']['p_up']),mean_return=float(r['statistics']['mean_return']),
            scores=distribution_scores(eval_law,y) if y is not None else {}))
    archive=dict(checked_at=stamp.isoformat(),refresh_bound=cutoff,frozen_vintage=FREEZE,authenticated_refresh=refresh,
        sessions=sorted([dict(day=d,**v) for d,v in actual.items()],key=lambda v:v['day']),
        additional_vs_V13=sorted(set(certified)-{a['day'] for a in read('refresh-reconciliation.json',V13)['rows']}),
        v4_issue_file_hash=sha(v4_path),v4_chain_head=v4[-1]['hash'],v4_chain_events=len(v4),
        v5_issue_file_hash=ident,v5_benchmark_file_hash=sha(V5/'frozen-benchmark-supplement.json'),
        v5_source_manifest_hash=sha(V5/'forecast-source-manifest.json'),v5_source_manifest_fields=list(manifest),
        records=res,scope='Separate refresh and resolutions. Preserved exact original dates, prices, forecast laws and issue records.')
    save(folder.relative_to(OUT).as_posix()+'/receipt.json',archive)
    save('forward-ledger.json',archive)
    print('Verified completed sessions',sorted(certified),'forward records',len(res),
          'resolved',sum(r['official_close'] is not None for r in res),flush=True)


if __name__=='__main__':
    {'intraday':intraday,'forward':forward}[sys.argv[1]]()
