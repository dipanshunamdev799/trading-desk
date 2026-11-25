"""Versioned output and immutable parent paths."""
import os
import json
from pathlib import Path
from research.nifty_forecast_v8.common import ROOT, V5, V6, V7, now, sha, np, pd

SRC = Path(__file__).parent
V8 = ROOT/'artifacts/nifty_forecast_v8/2026-11-24/run-001'
BASE = ROOT/'artifacts/nifty_forecast_v9'
DEFAULT = BASE/'2026-11-24/run-001'
OUT = Path(os.environ.get('NIFTY_V9_OUT', DEFAULT)).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('Output must be in the V9 artifact tree')
SEED = 20261129


def read(name, directory=OUT):
    return json.loads((directory/name).read_text(encoding='utf-8'))


def save(name, value):
    path = OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,default=str,allow_nan=False),encoding='utf-8')


def matrix(name, directory=V6):
    return pd.read_csv(directory/name,index_col=0)


def write(name, frame, index=False):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(path,index=index)
