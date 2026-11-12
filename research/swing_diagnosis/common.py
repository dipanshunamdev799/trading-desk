from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'artifacts/swing_discovery'
OUT=ROOT/'artifacts/swing_diagnosis'
PERIODS={'development':('2024-11-10','2025-11-10'),'validation':('2025-11-10','2026-05-10'),'final':('2026-05-10','2026-11-10'),'two_year':('2024-11-10','2026-11-10')}

def load_panel():
    idx=json.loads((OLD/'panel-index.json').read_text())
    with np.load(OLD/'daily-panel.npz') as f:
        p={k:f[k].copy() for k in f.files if not k.startswith(('actual_','neutral_'))}
        for basis in ['actual','neutral']:p[basis]={k:f[basis+'_'+k].copy() for k in ['open','high','low','close','volume']}
    p.update(symbols=idx['symbols'],sector=idx['sector'],dates=pd.DatetimeIndex(pd.to_datetime(idx['dates'],utc=True)).tz_convert('Asia/Kolkata'))
    p['nifty']=p['niftyclose'];p['median_volume20']=p['liquidity_volume'];p['liquidity_value']=p['liquidity_turnover']
    return p

def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(np.bool_,)):return bool(x)
    if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
    if isinstance(x,(pd.Timestamp,Path)):return str(x)
    return x

def save(name,x):
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False),encoding='utf-8')
