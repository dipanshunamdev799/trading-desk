"""Explicit V11 output root and read-only parent vintages."""
import json
import os
from pathlib import Path
from research.nifty_forecast_v10.common import ROOT,V5,V6,V7,V8,V9,sha,now,pd,np,matrix
from research.nifty_forecast_v10.common import OUT as V10

SRC=Path(__file__).parent
V11=ROOT/'artifacts/nifty_forecast_v11'
OUT=Path(os.environ.get('NIFTY_V11_OUT',V11/'2026-11-24/run-001')).resolve()
if not OUT.is_relative_to(V11):raise ValueError('V11 outputs must stay inside the V11 artifact tree')
SEED=20261124


def read(name,folder=OUT):
    return json.loads((folder/name).read_text(encoding='utf-8'))


def save(name,obj):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')


def write(name,df,index=False):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);df.to_csv(p,index=index)


def cache(name,rows):
    with (OUT/name).open('w',encoding='utf-8') as f:
        for row in rows:f.write(json.dumps(row,allow_nan=False)+'\n')
