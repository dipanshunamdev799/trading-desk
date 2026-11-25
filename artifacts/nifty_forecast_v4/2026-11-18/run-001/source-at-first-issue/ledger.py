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
