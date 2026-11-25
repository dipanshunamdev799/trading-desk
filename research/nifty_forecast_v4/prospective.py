"""Fixed-clock market-data capture, immutable prediction issuance, later resolution."""
from __future__ import annotations
import argparse,json,shutil,time,uuid,sys
from datetime import datetime,timedelta,time as walltime
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from pathlib import Path
import numpy as np
import pandas as pd
import requests,joblib
from .common import *
from .ledger import append,events,verify_files,resolution_eligible

LEDGER=OUT/'prospective-ledger.jsonl'

def timing(start,issued,diagnostic=False):
    a=datetime.fromisoformat(start);b=datetime.fromisoformat(issued)
    check_scope([a.date(),b.date()])
    decision=datetime.combine(a.date(),walltime(9,10),TZ);deadline=decision+timedelta(minutes=2)
    eligible=a<decision and decision<=b<=deadline
    if not eligible and not diagnostic:raise ValueError('MISSED_DECISION_WINDOW: start before09:10, finish09:10–09:12 IST')
    return eligible

class Capture:
    def __init__(self,folder):
        sys.path[:0]=[str(ROOT/'backend')]
        from app.config import get_settings
        self.headers={'Authorization':'Bearer '+get_settings().upstox_analytics_token,'Accept':'application/json'}
        self.folder=folder;self.requests=[]
    def get(self,url,name,auth=True):
        sent=now();r=requests.get(url,headers=self.headers if auth else {'User-Agent':'Mozilla/5.0 NiftyResearch/4.0'},timeout=25);received=now()
        if r.status_code!=200:raise ValueError(f'SOURCE_HTTP_{r.status_code}: {name}')
        p=self.folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.content)
        server=r.headers.get('Date');skew=None
        if server:
            skew=abs((parsedate_to_datetime(server)-datetime.fromisoformat(received)).total_seconds())
            if skew>180:raise ValueError('SOURCE_CLOCK_SKEW')
        self.requests.append({'url':url,'sent_at':sent,'received_at':received,'server_date':server,'absolute_clock_skew_seconds':skew,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
        return r

def eligible_reference(today,calendar):
    from research.nifty_forecast.horizons import future_sessions
    sessions=future_sessions('2026-01-01',calendar,260)
    if today not in sessions:raise ValueError('NOT_AN_NSE_SESSION')
    return max(d for d in sessions if d<today)

def acquire(folder,start,reference):
    import research.nifty_forecast_v3.data as d3
    import research.nifty_forecast_v3.features as f3
    capture=Capture(folder)
    series=folder/'sources/upstox';series.mkdir(parents=True)
    revisions=[]
    for old in (V3/'sources/upstox').glob('*.json'):
        doc=json.loads(old.read_text());rows={r['day']:r for r in doc['rows']}
        if not old.stem.startswith('stock_'):
            key=quote(doc['instrument_key'],safe='')
            r=capture.get(f'https://api.upstox.com/v3/historical-candle/{key}/days/1/{reference}/2026-11-16','responses/'+old.name)
            payload=r.json().get('data',{})
            d3.END=reference
            for row in d3.candles(payload):
                if row['day'] in rows and any(float(row[c])!=float(rows[row['day']][c]) for c in ['open','high','low','close','volume']):revisions.append({'series':old.stem,'day':row['day']})
                rows[row['day']]=row
        doc['rows']=[rows[k] for k in sorted(rows) if k<=reference];doc['acquired_at']=now();(series/old.name).write_text(json.dumps(doc),encoding='utf-8')
    # Preserve the original raw histories; append authenticated new dated archives.
    shutil.copytree(V3/'sources/fo',folder/'sources/fo')
    base=json.loads((series/'nifty_spot.json').read_text())
    for day in sorted({r['day'] for r in base['rows']}):
        if day<='2026-11-16':continue
        name=f'responses/fo-{day}.zip';url='https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'+day.replace('-','')+'_F_0000.csv.zip'
        capture.get(url,name,False);rows=d3.read_nifty_fo(folder/name,day)
        (folder/'sources/fo'/f'{day}.json').write_text(json.dumps({'day':day,'ok':True,'rows':rows,'acquired_at':now(),'source_url':url}),encoding='utf-8')
    key=quote('NSE_INDEX|Nifty 50',safe='')
    r=capture.get(f'https://api.upstox.com/v3/historical-candle/{key}/minutes/5/{reference}/2026-11-16','responses/intraday.json')
    bars=pd.read_csv(V3/'sources/nifty-intraday.csv');new=[]
    for row in r.json().get('data',{}).get('candles',[]):
        stamp=pd.Timestamp(row[0]);day=stamp.tz_convert(TZ).strftime('%Y-%m-%d')
        if '2025-01-01'<=day<=reference:new.append({'ts':stamp.tz_convert('UTC').isoformat(),**dict(zip(['open','high','low','close','volume'],row[1:6])),'source':'upstox'})
    merged=pd.concat([bars,pd.DataFrame(new)]);merged['ts']=pd.to_datetime(merged.ts,utc=True,format='mixed')
    merged=merged.drop_duplicates('ts',keep='last').sort_values('ts');merged.to_csv(folder/'sources/nifty-intraday.csv',index=False)
    # Runtime output isolation only: no V3 file or fitted feature definition is edited.
    old_dout,old_fout,old_dend,old_fend=d3.OUT,f3.OUT,'2026-11-16',f3.END
    try:
        d3.OUT=folder;f3.OUT=folder;d3.END=reference;f3.END=reference
        data,quality=d3.load_series();fo=d3.fo_features(data);x,price=f3.build(data,fo)
        if reference!=price.index[-1] or data['nifty_spot'].index[-1]!=reference:raise ValueError('LATEST_REFERENCE_MISSING')
        spot=float(price.close.loc[reference]);official=float(fo.spot_official.loc[reference])
        if abs(spot-official)>1e-6:raise ValueError('REFERENCE_CROSSCHECK_FAILED')
        if any(data[k].index.max()!=reference for k in data if not k.startswith(('stock_','global_'))):raise ValueError('REQUIRED_DOMESTIC_SOURCE_STALE')
        x.to_csv(folder/'features.csv');price.to_csv(folder/'price.csv')
        labels={h:f3.labels_for(price,h) for h in [5,21]}
        for h,l in labels.items():l.to_csv(folder/f'labels-{h}.csv')
        availability={'received_records':capture.requests,'revisions':revisions,'quality':quality,'reference':reference,'reference_close':spot,
            'known_missing_policy':'Frozen train-median imputation; no stale forward fill; institutional series are not freshly extended; missingness recorded',
            'current_feature_missing':[c for c in x if pd.isna(x.loc[reference,c])],
            'institutional_limitation':'Old authenticated snapshots only; recent unavailable institutional values remain missing. No invented report timestamps.',
            'local_clock_authentication':'Local sent/received clocks plus available HTTPS server Date. Hash chain detects edits relative to retained head; no external timestamp notarization.'}
        (folder/'availability.json').write_text(json.dumps(availability,indent=2),encoding='utf-8')
        return x,labels,price,availability
    finally:d3.OUT=old_dout;f3.OUT=old_fout;d3.END=old_dend;f3.END=old_fend

def issue(diagnostic=False):
    start=now();a=datetime.fromisoformat(start);decision=datetime.combine(a.date(),walltime(9,10),TZ)
    if not diagnostic and a>=decision:raise ValueError('MISSED_DECISION_WINDOW: no late primary prediction permitted')
    if not diagnostic and (decision-a).total_seconds()>600:raise ValueError('START_AT_09:00_TO_09:10_IST')
    check_scope([a.date()]);calendar=read('horizon-calendar-v1.json',ROOT/'artifacts/nifty_forecast/2026-11-17')
    if not diagnostic:
        protocols=[e for e in events(LEDGER) if e['kind']=='PROTOCOL_FREEZE']
        if len(protocols)!=1:raise ValueError('REQUIRE_FROZEN_PROTOCOL_BEFORE_PRIMARY')
        verify_files(protocols[0])
    reference=eligible_reference(a.date().isoformat(),calendar)
    cohort='LATE_DIAGNOSTIC' if diagnostic else 'PRIMARY'
    key=reference+'|'+cohort
    if any(e['kind']=='FORECAST' and e['key']==key for e in events(LEDGER)):raise ValueError('FORECAST_ALREADY_ISSUED')
    folder=OUT/'captures'/(reference+'-'+uuid.uuid4().hex[:10]);folder.mkdir(parents=True)
    (folder/'code').mkdir()
    for p in SOURCE.glob('*.py'):shutil.copy2(p,folder/'code'/p.name)
    x,labels,price,availability=acquire(folder,start,reference)
    from research.nifty_forecast_v3.experiment import available,inner_split
    from research.nifty_forecast_v3.models import train,predict,SPECS
    from research.nifty_forecast.horizons import future_sessions
    from .distributions import prepare,forecast
    outputs={};future=future_sessions(reference,calendar,21)
    check_scope(future)
    # Exact V3 monthly refit anchor (prior-session origin of first monthly forecast).
    dates=list(x.index);anchor=next(d for i,d in enumerate(dates[:-1]) if dates[i+1][:7]==a.strftime('%Y-%m'))
    for h in [5,21]:
        ix=available(labels[h],anchor);innerfit,innerval=inner_split(labels[h],ix)
        if len(ix)<126 or len(innerfit)<80:raise ValueError('INSUFFICIENT_MATURED_TRAINING')
        endpoint=future[h-1];binary={}
        for name in ['M05_lgbm','A00_sector','B00_empirical'] if h==5 else ['B00_empirical']:
            model=train(SPECS[name],x.loc[ix],labels[h].loc[ix]);p=predict(model,x.loc[[reference]])[0]['p'];binary[name]=p
            joblib.dump(model,folder/f'h{h}-{name}.joblib',compress=3)
        if h==5:binary.update(Z_neutral=.5,Z_reversion=.45 if x.loc[reference,'price_ret5']>0 else .55)
        context=prepare(x,labels[h],ix,innerfit,innerval);dd=forecast(context,x.loc[reference],h)
        distributions={name:{'statistics':law.stats(float(price.close.iloc[-1])),'atoms':law.a.tolist(),'weights':law.w.tolist()} for name,law in dd.items() if name in ['D00_empirical','D03_residual_shrunk']}
        outputs[str(h)]={'expected_endpoint':endpoint,'target_sessions':future[:h],'reference':reference,'reference_close':float(price.close.iloc[-1]),'binary_probabilities':binary,
            'distributions':distributions,'last_training_endpoint':str(labels[h].loc[ix,'endpoint'].max()),'refit_anchor':anchor,'status':'EXPERIMENTAL / NOT VALIDATED'}
    if not diagnostic and availability['revisions']:raise ValueError('SOURCE_REVISION_REQUIRES_NEW_REGISTERED_VINTAGE')
    issued=now()
    if not diagnostic:
        remaining=(decision-datetime.fromisoformat(issued)).total_seconds()
        while remaining>0:
            time.sleep(min(30,remaining));remaining=(decision-datetime.fromisoformat(now())).total_seconds()
        issued=now()
    eligible=timing(start,issued,diagnostic)
    if any(datetime.fromisoformat(r['received_at'])>decision for r in availability['received_records']):
        if not diagnostic:raise ValueError('SOURCE_RECEIVED_AFTER_DECISION')
        eligible=False
    if any(sha(p)!=sha(folder/'code'/p.name) for p in SOURCE.glob('*.py')):raise ValueError('CODE_CHANGED_DURING_ISSUANCE')
    payload={'started_at':start,'issued_at':issued,'reference_session':reference,'cohort':cohort,'primary_eligible':eligible and not diagnostic,
        'fresh_prediction_before_endpoint':True,'not_a_fresh_premarket_call':diagnostic,'forecasts':outputs,
        'registry_sha256':sha(OUT/'registry.json'),'v3_dataset_sha256':sha(V3/'dataset-manifest.json'),
        'stop_rules_sha256':sha(OUT/'prospective-stop-rules.json'),
        'code_hashes':{p.name:sha(p) for p in SOURCE.glob('*.py')},'source_received_at_max':max(r['received_at'] for r in availability['received_records']),
        'limitations':['NO DEPLOYMENT','Local clocks/hash chain are not external notarization','Prior source revision histories remain incomplete','Institutional short history/missingness'],
        'files':{str(p.relative_to(ROOT)):sha(p) for p in folder.rglob('*') if p.is_file()}}
    row=append(LEDGER,'FORECAST',key,payload)
    print(json.dumps({'issued':row['created_at'],'cohort':cohort,'primary_eligible':payload['primary_eligible'],'ledger_hash':row['hash'],'reference':reference}),flush=True)

def resolve():
    from .distributions import Distribution
    existing=events(LEDGER);stamp=now();check_scope([stamp[:10]]);folder=OUT/'resolutions'/uuid.uuid4().hex;todo=[]
    for e in existing:
        if e['kind']!='FORECAST':continue
        verify_files(e)
        for h,f in e['payload']['forecasts'].items():
            key=e['hash']+'|'+h
            if any(r['kind']=='RESOLUTION' and r['key']==key for r in existing):continue
            if resolution_eligible(f,stamp):todo.append((e,h,f,key))
    if not todo:print('No unresolved fully matured horizons; no network call or ledger mutation',flush=True);return
    folder.mkdir(parents=True);capture=Capture(folder);latest=max(f['expected_endpoint'] for _,_,f,_ in todo)
    r=capture.get('https://api.upstox.com/v3/historical-candle/'+quote('NSE_INDEX|Nifty 50',safe='')+'/days/1/'+latest+'/2025-01-01','outcomes.json')
    bars={pd.Timestamp(row[0]).tz_convert(TZ).strftime('%Y-%m-%d'):row for row in r.json().get('data',{}).get('candles',[])}
    for e,h,f,key in todo:
        sessions=[d for d in sorted(bars) if f['reference']<d<=f['expected_endpoint']]
        if sessions!=f['target_sessions']:raise ValueError('TARGET_CALENDAR_OR_CANDLE_MISMATCH_REVIEW_REQUIRED')
        close=float(bars[f['expected_endpoint']][4]);ref=f['reference_close'];y=close/ref-1
        binary={n:{'brier':(p-int(y>0))**2,'log_loss':float(-int(y>0)*np.log(max(p,1e-6))-(1-int(y>0))*np.log(max(1-p,1e-6))),'correct':bool((p>=.5)==(y>0))} for n,p in f['binary_probabilities'].items()}
        dist={n:Distribution(d['atoms'],d['weights']).score(y) for n,d in f['distributions'].items()}
        append(LEDGER,'RESOLUTION',key,{'forecast_hash':e['hash'],'horizon':int(h),'primary_eligible':e['payload']['primary_eligible'],'reference_close_frozen':ref,'reference_close_latest':float(bars[f['reference']][4]),
            'endpoint_close':close,'realized_return':y,'binary_scores':binary,'distribution_scores':dist,
            'matched_binary_improvements':{n:{'brier_vs_'+b:binary[b]['brier']-s['brier'] for b in ['Z_neutral','Z_reversion','A00_sector'] if b in binary} for n,s in binary.items()},
            'matched_distribution_improvements':{n:{metric:dist['D00_empirical'][metric]-s[metric] for metric in ['crps','pinball','mae','bucket_brier']} for n,s in dist.items()},
            'received':capture.requests,'files':{str(p.relative_to(ROOT)):sha(p) for p in folder.rglob('*') if p.is_file()}})
    print('Appended matched resolutions',len(todo),flush=True)

def status():
    rows=events(LEDGER)
    for e in rows:verify_files(e)
    print(json.dumps({'events':len(rows),'primary_forecasts':sum(e['kind']=='FORECAST' and e['payload']['primary_eligible'] for e in rows),
        'diagnostic_forecasts':sum(e['kind']=='FORECAST' and not e['payload']['primary_eligible'] for e in rows),'resolutions':sum(e['kind']=='RESOLUTION' for e in rows),'head':rows[-1]['hash'] if rows else None,'decision':'NO DEPLOYMENT'}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','diagnostic-late','resolve','status']);args=p.parse_args()
    if args.command in ['run','diagnostic-late']:issue(args.command=='diagnostic-late')
    elif args.command=='resolve':resolve()
    else:status()
