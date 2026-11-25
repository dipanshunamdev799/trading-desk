"""Single-writer, hash-chained append-only research events. No trade APIs."""
import os,json
from pathlib import Path
from .common import canonical,digest,now,OUT,ROOT,sha

def events(path):
    path=Path(path)
    if not path.exists():return []
    result=[];previous='0'*64;keys=set()
    for line in path.read_text(encoding='utf-8').splitlines():
        row=json.loads(line);signed={k:v for k,v in row.items() if k!='hash'}
        if row['previous_hash']!=previous or row['hash']!=digest(signed):raise ValueError('LEDGER_TAMPER_OR_PARTIAL_WRITE')
        key=(row['kind'],row['key'])
        if key in keys:raise ValueError('DUPLICATE_EVENT')
        keys.add(key);previous=row['hash'];result.append(row)
    return result

def append(path,kind,key,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);lock=path.with_suffix('.lock')
    fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        os.close(fd);old=events(path)
        if any(e['kind']==kind and e['key']==key for e in old):raise ValueError('DUPLICATE_EVENT')
        row={'sequence':len(old)+1,'kind':kind,'key':key,'created_at':now(),'previous_hash':old[-1]['hash'] if old else '0'*64,'payload':payload}
        row['hash']=digest(row);blob=canonical(row)+b'\n'
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
        try:
            offset=0
            while offset<len(blob):offset+=os.write(fd,blob[offset:])
            os.fsync(fd)
        finally:os.close(fd)
        return row
    finally:lock.unlink()

def verify_files(event):
    for name,expected in event['payload'].get('files',{}).items():
        p=(ROOT/name).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file() or sha(p)!=expected:raise ValueError('ARTIFACT_CHANGED: '+name)

def resolution_eligible(forecast,now_stamp):
    from datetime import datetime,time
    from .common import TZ
    endpoint=forecast['expected_endpoint']
    return datetime.fromisoformat(now_stamp)>=datetime.combine(datetime.fromisoformat(endpoint).date(),time(18),TZ)

def freeze_protocol():
    from .common import V3,SOURCE,read
    path=OUT/'prospective-ledger.jsonl';old=events(path)
    if any(e['kind']=='PROTOCOL_FREEZE' for e in old):raise ValueError('PROTOCOL_ALREADY_FROZEN')
    if any(e['kind']=='FORECAST' and e['payload']['primary_eligible'] for e in old):raise ValueError('PRIMARY_COLLECTION_ALREADY_STARTED')
    inputs=[OUT/n for n in ['registry.json','prospective-stop-rules.json','power-assessment.json','protocol-amendment.json']]
    inputs+=list(SOURCE.glob('*.py'))+list((ROOT/'research/nifty_forecast_v3').glob('*.py'))
    inputs+=[ROOT/'research/nifty_forecast/adaptive.py',ROOT/'research/nifty_forecast/horizons.py',ROOT/'upstox_analytics.py']
    inputs+=list((V3/'sources/upstox').glob('*.json'))+list((V3/'sources/fo').glob('*.json'))
    inputs+=[V3/'sources/nifty-intraday.csv',V3/'dataset-manifest.json',V3/'feature-definitions.json']
    oldroot=ROOT/'artifacts/nifty_forecast/2026-11-17'
    inputs+=[oldroot/'horizon-calendar-v1.json']+list((oldroot/'institutional-v1').glob('*.json'))+list((oldroot/'inputs-v2').glob('*.json'))
    for n in ['features.csv','price.csv','labels-5.csv','labels-21.csv']:inputs.append(V3/n)
    return append(path,'PROTOCOL_FREEZE','V4-20261118-001',{'note':'Pinned before first primary issuance; no independent success claimed. Retain trusted external head.',
        'files':{str(p.relative_to(ROOT)):sha(p) for p in inputs}})
