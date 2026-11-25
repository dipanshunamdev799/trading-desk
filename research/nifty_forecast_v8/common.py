"""Isolated V8 paths and frozen input access."""
from research.nifty_forecast_v7.common import ROOT, V5, V6, now, sha, np, pd
from pathlib import Path
import json
import os

SRC = Path(__file__).parent
V7 = ROOT/'artifacts/nifty_forecast_v7/2026-11-24/run-001'
BASE = ROOT/'artifacts/nifty_forecast_v8'
DEFAULT = BASE/'2026-11-24/run-001'
OUT = Path(os.environ.get('NIFTY_V8_OUT', DEFAULT)).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V8 output must stay inside its artifact directory')
SEED = 20261125


def save(name, obj):
    p = OUT/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, default=str, allow_nan=False), encoding='utf-8')


def read(name, root=OUT):
    return json.loads((root/name).read_text(encoding='utf-8'))


def matrix(name, root=V6):
    return pd.read_csv(root/name,index_col=0)


def write(name, frame):
    OUT.mkdir(parents=True,exist_ok=True)
    frame.to_csv(OUT/name,index=False)
