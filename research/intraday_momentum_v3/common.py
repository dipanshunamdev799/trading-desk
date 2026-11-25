from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,os
from dotenv import dotenv_values
from research.intraday_momentum import data as base

ROOT=base.ROOT;OUT=ROOT/'artifacts/intraday_momentum_v3';SOURCE=ROOT/'research/intraday_momentum_v3'
def now():return datetime.now(timezone.utc)
def dump(path,value):base.dump(path,value)
def sha(path):return base.sha(path)
def client():
    from upstox_analytics import UpstoxAnalyticsClient
    explicit=os.getenv('UPSTOX_MARKET_DATA_TOKEN') or dotenv_values(ROOT/'.env').get('UPSTOX_MARKET_DATA_TOKEN')
    return UpstoxAnalyticsClient(analytics_token=explicit or base._settings().upstox_analytics_token,timeout=20,max_retries=0)
def append(path,row):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,default=str,allow_nan=False)+'\n')
def archive_response(method,parameters,payload,received=None):
    received=received or now();params=json.dumps(parameters,sort_keys=True)
    key=hashlib.sha256((method+params).encode()).hexdigest()
    with base.connection(write=True) as c:
        c.execute('INSERT INTO market_responses(recorded_at,request_key,method,parameters,payload) VALUES(%s,%s,%s,%s::jsonb,%s::jsonb) ON CONFLICT DO NOTHING',
            (received,key,method,params,json.dumps(payload,allow_nan=False)))
