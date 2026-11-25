"""Versioned V10 artifact paths with explicit frozen data access."""
import os
import json
from pathlib import Path
from research.nifty_forecast_v9.common import ROOT,V5,V6,V7,V8,now,sha,np,pd

SRC=Path(__file__).parent
V9=ROOT/'artifacts/nifty_forecast_v9/2026-11-24/run-001'
BASE=ROOT/'artifacts/nifty_forecast_v10'
DEFAULT=BASE/'2026-11-24/run-001'
OUT=Path(os.environ.get('NIFTY_V10_OUT',DEFAULT)).resolve()
if not OUT.is_relative_to(BASE):raise ValueError('Output must remain in the V10 artifact tree')
SEED=20261130


def read(name,where=OUT):return json.loads((where/name).read_text(encoding='utf-8'))


def save(name,obj):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')


def matrix(name,where=V6):return pd.read_csv(where/name,index_col=0)


def write(name,df,index=False):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);df.to_csv(p,index=index)
