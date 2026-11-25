from __future__ import annotations
import os,json,hashlib
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];SRC=Path(__file__).parent
OUT=Path(os.environ.get('NIFTY_V6_OUT',str(ROOT/'artifacts/nifty_forecast_v6/2026-11-19/run-001'))).resolve()
if not OUT.is_relative_to(ROOT/'artifacts/nifty_forecast_v6'):raise ValueError('OUTPUT_MUST_STAY_IN_V6')
V5=ROOT/'artifacts/nifty_forecast_v5/2026-11-18/run-001';V4=ROOT/'artifacts/nifty_forecast_v4/2026-11-18/run-001';V3=ROOT/'artifacts/nifty_forecast_v3/2026-11-17/run-001'
SEED=20261119
def now():return datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=str,allow_nan=False),encoding='utf-8')
def read(name,base=OUT):return json.loads((base/name).read_text(encoding='utf-8'))
def scope(days):
    if any(not '2025-01-01'<=str(d)[:10]<='2026-12-31' for d in days):raise ValueError('OUT_OF_SCOPE')
def load():
    x=pd.read_csv(V5/'features.csv',index_col=0);p=pd.read_csv(V5/'price.csv',index_col=0);labels={h:pd.read_csv(V5/f'labels-{h}.csv',index_col=0) for h in [1,3,5,21]}
    return x,p,labels
def preserve():
    if (OUT/'prior-preservation.json').exists():raise FileExistsError('Version exists')
    hashes={};review=[]
    for dirname in ['nifty_forecast','nifty_forecast_v3','nifty_forecast_v4','nifty_forecast_v5']:
        for folder in [ROOT/'research'/dirname,ROOT/'artifacts'/dirname]:
            for p in folder.rglob('*'):
                if not p.is_file() or '__pycache__' in p.parts:continue
                hashes[str(p.relative_to(ROOT))]=sha(p)
                if p.suffix in ['.md','.py']:review.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'text':p.read_text(encoding='utf-8')})
    for p in ROOT.glob('NIFTY*.md'):hashes[str(p.relative_to(ROOT))]=sha(p)
    save('prior-preservation.json',{'recorded_at':now(),'files':hashes});save('history-review.json',review)
    print('Preserved prior artifacts',len(hashes),'read reports/source',len(review),flush=True)
if __name__=='__main__':preserve()
