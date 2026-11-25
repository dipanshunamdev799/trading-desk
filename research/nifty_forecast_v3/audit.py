from __future__ import annotations
import ast,hashlib,json,sys,os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from sqlalchemy import create_engine,text
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from app.config import get_settings
OUT=Path(os.environ.get('NIFTY_V3_OUT',str(ROOT/'artifacts/nifty_forecast_v3/2026-11-17/run-001'))).resolve()
if not OUT.is_relative_to(ROOT):raise ValueError('V3 output must remain within the trading-desk workspace')
OLD=ROOT/'artifacts/nifty_forecast/2026-11-17'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,default=str,allow_nan=False),encoding='utf-8')
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'legacy-review.json').exists():raise FileExistsError('Audit already frozen')
    review=[]
    paths=list((ROOT/'research/nifty_forecast').glob('*'))+list(ROOT.glob('NIFTY_*2026-11-17.md'))+list(OLD.rglob('*'))
    for p in paths:
        if not p.is_file() or p.suffix not in ['.py','.md','.json','.csv']:continue
        r={'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
        try:
            if p.suffix=='.py':
                source=p.read_text(encoding='utf-8');tree=ast.parse(source)
                r.update(functions=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))],lines=len(source.splitlines()))
            elif p.suffix=='.json':
                obj=json.loads(p.read_text(encoding='utf-8'));r.update(type=type(obj).__name__,keys=list(obj)[:35] if isinstance(obj,dict) else None,items=len(obj) if hasattr(obj,'__len__') else None)
            elif p.suffix=='.csv':
                f=pd.read_csv(p);r.update(rows=len(f),columns=list(f.columns),missing_cells=int(f.isna().sum().sum()))
            else:r['text']=p.read_text(encoding='utf-8')
        except Exception as exc:r['error']=str(exc)[:180]
        review.append(r)
    save('legacy-review.json',review)
    eng=create_engine(get_settings().database_url_sync,connect_args={'connect_timeout':8})
    queries={
        'schema':"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position",
        'datasets':"SELECT * FROM market_datasets LIMIT 1000",
        'coverage':"SELECT * FROM candle_coverage LIMIT 10000",
        'responses':"SELECT method,count(*) AS captures,min(fetched_at),max(fetched_at) FROM market_responses GROUP BY method",
        'factors':"SELECT factor_id,count(*) AS n,min(observed_at),max(observed_at),min(reported_at),max(reported_at) FROM nifty_observations GROUP BY factor_id",
        'chain_schema':"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_name IN ('market_stream_chains','market_stream_ticks','market_responses','candle_coverage') ORDER BY table_name,ordinal_position",
        'events':"SELECT event_at,observed_at,payload FROM nifty_research_events WHERE event_at>='2025-01-01' ORDER BY event_at LIMIT 500",
    }
    database={}
    for name,q in queries.items():
        try:
            with eng.connect() as c:
                c.execute(text('SET statement_timeout=15000'));database[name]=[dict(r) for r in c.execute(text(q)).mappings()]
        except Exception as exc:database[name]={'error':type(exc).__name__,'detail':str(exc).splitlines()[0][:180]}
    eng.dispose();save('database-inventory.json',database)
    save('audit-start.json',{'issued_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'constraint':'2025-2026 only; no pre-2025 market values or fitted state in V3','legacy_artifacts_reviewed':len(review),'prior_forecast_hashes':{str(p.relative_to(ROOT)):sha(p) for p in OLD.glob('*/forecast.json')}})
    print(json.dumps({'reviewed':len(review),'database_inventory':{k:len(v) if isinstance(v,list) else v for k,v in database.items()}}),flush=True)
if __name__=='__main__':main()
