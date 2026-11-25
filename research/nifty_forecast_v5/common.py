from __future__ import annotations
import os,json,hashlib
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];SRC=Path(__file__).parent
OUT=Path(os.environ.get('NIFTY_V5_OUT',str(ROOT/'artifacts/nifty_forecast_v5/2026-11-18/run-001'))).resolve()
if not OUT.is_relative_to(ROOT):raise ValueError('RESEARCH_OUTPUT_OUTSIDE_WORKSPACE')
V3=ROOT/'artifacts/nifty_forecast_v3/2026-11-17/run-001';V4=ROOT/'artifacts/nifty_forecast_v4/2026-11-18/run-001'
START='2025-01-01';END='2026-11-18';SEED=202611185
def now():return datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=str,allow_nan=False),encoding='utf-8')
def read(name,base=OUT):return json.loads((base/name).read_text(encoding='utf-8'))
def scope(days):
    if any(not START<=str(d)[:10]<='2026-12-31' for d in days):raise ValueError('SCOPE_REJECTED')
def audit():
    if (OUT/'history-audit.json').exists():raise FileExistsError('Version already exists')
    OUT.mkdir(parents=True,exist_ok=True);review=[];preserve={}
    for folder in [ROOT/'research/nifty_forecast',ROOT/'research/nifty_forecast_v3',ROOT/'research/nifty_forecast_v4',V3,V4]:
        for p in sorted(folder.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            preserve[str(p.relative_to(ROOT))]=sha(p)
            if p.suffix in ['.md','.py']:
                review.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p),'contents':p.read_text(encoding='utf-8')})
    for p in ROOT.glob('NIFTY*.md'):
        preserve[str(p.relative_to(ROOT))]=sha(p);review.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p),'contents':p.read_text(encoding='utf-8')})
    save('history-audit.json',{'reviewed_at':now(),'read_sources_reports':review,'preservation_hashes':preserve,'exposure':'All historical2025–2026 findings are research-exposed; no V5 historical date is independent confirmation'})
    print('Read history files',len(review),'preserved artifacts',len(preserve),flush=True)
if __name__=='__main__':audit()
