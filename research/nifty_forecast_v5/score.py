"""Manual later scoring; append outcomes without changing any issued forecast."""
import sys,uuid
from urllib.parse import quote
from datetime import datetime,time
import requests
from .common import *
from research.nifty_forecast_v4.distributions import Distribution
from research.nifty_forecast_v4.ledger import append,events
def mature(endpoint,stamp):
    return pd.Timestamp(stamp)>=pd.Timestamp(endpoint+' 18:00',tz='Asia/Kolkata')
def run():
    stamp=now();scope([stamp[:10]]);call=read('experimental-forecasts.json');benchmark=read('frozen-benchmark-supplement.json');digest=sha(OUT/'experimental-forecasts.json')
    if benchmark['forecast_sha256']!=digest:raise ValueError('FORECAST_BENCHMARK_IDENTITY_MISMATCH')
    ledger=OUT/'evaluation-ledger.jsonl';old=events(ledger);todo={}
    for name,f in call['forecasts'].items():
        key=digest+'|'+str(f['horizon'])
        if mature(f['endpoint'],stamp) and not any(e['key']==key and e['kind']=='HORIZON' for e in old):todo.setdefault(f['horizon'],[]).append((name,f))
    if not todo:print('PENDING: no new mature horizons; no network call or ledger mutation',flush=True);return
    sys.path[:0]=[str(ROOT/'backend')]
    from app.config import get_settings
    latest=max(f['endpoint'] for group in todo.values() for _,f in group);url='https://api.upstox.com/v3/historical-candle/'+quote('NSE_INDEX|Nifty 50',safe='')+'/days/1/'+latest+'/'+call['reference_session'];sent=now()
    r=requests.get(url,headers={'Authorization':'Bearer '+get_settings().upstox_analytics_token},timeout=25);r.raise_for_status();received=now()
    folder=OUT/'outcome-sources';folder.mkdir(exist_ok=True);raw=folder/(uuid.uuid4().hex+'.json');raw.write_bytes(r.content)
    bars={pd.Timestamp(row[0]).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d'):row for row in r.json().get('data',{}).get('candles',[])}
    for h,group in todo.items():
        f=group[0][1];target=f['endpoint']
        if target not in bars:print('PENDING SOURCE: daily endpoint not published',h,target,flush=True);continue
        observed=[day for day in sorted(bars) if call['reference_session']<day<=target]
        if observed!=f['target_sessions']:raise ValueError('CALENDAR_OR_MISSING_SESSION_REVIEW_REQUIRED')
        ref=call['reference_close'];close=float(bars[target][4]);y=close/ref-1
        scores={name:Distribution(a['atoms'],a['weights']).score(y) for name,a in group}
        control=benchmark['weekly_empirical'] if h==5 else call['forecasts']['h21-E00'];base=Distribution(control['atoms'],control['weights']).score(y)
        binary={name:{'p':p,'brier':(p-int(y>0))**2,'log_loss':float(-int(y>0)*np.log(p)-(1-int(y>0))*np.log(1-p))} for name,p in (benchmark['weekly_binary_controls'].items() if h==5 else [('neutral',.5)])}
        append(ledger,'HORIZON',digest+'|'+str(h),{'forecast_sha256':digest,'horizon':h,'endpoint':target,'frozen_reference':ref,'latest_reference':float(bars[call['reference_session']][4]),'endpoint_close':close,'return':y,
            'experimental_scores':scores,'empirical_baseline':base,'matched_improvements':{name:{metric:base[metric]-s[metric] for metric in ['brier','crps','mae','pinball','bucket_brier']} for name,s in scores.items()},
            'fixed_binary_baseline_scores':binary,'matched_binary_brier_improvements':{name:{b:v['brier']-s['brier'] for b,v in binary.items()} for name,s in scores.items()},
            'received_at':received,'sent_at':sent,'server_date':r.headers.get('Date'),'source_url':url,'files':{str(raw.relative_to(ROOT)):sha(raw)},'status':'New resolved experimental observation; not sufficient independent validation'})
    print('Outcome scoring finished; original forecast unchanged',flush=True)
if __name__=='__main__':run()
