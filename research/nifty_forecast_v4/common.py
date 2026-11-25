from __future__ import annotations
import hashlib,json,os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
V3=ROOT/'artifacts/nifty_forecast_v3/2026-11-17/run-001'
OUT=ROOT/'artifacts/nifty_forecast_v4/2026-11-18/run-001'
SOURCE=Path(__file__).parent
TZ=ZoneInfo('Asia/Kolkata')
SEED=20261118
def now():return datetime.now(TZ).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def read(name,base=OUT):return json.loads((base/name).read_text(encoding='utf-8'))
def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2,default=str,allow_nan=False),encoding='utf-8')
def load():
    x=pd.read_csv(V3/'features.csv',index_col=0);x.index=x.index.astype(str)
    labels={h:pd.read_csv(V3/f'labels-{h}.csv',index_col=0) for h in [5,21]}
    return x,labels,pd.read_csv(V3/'predictions.csv')
def check_scope(days):
    if any(not '2025-01-01'<=str(d)[:10]<='2026-12-31' for d in days):raise ValueError('OUT_OF_SCOPE')

def register():
    if (OUT/'registry.json').exists():raise FileExistsError('V4 registry is immutable; choose a new run')
    from research.nifty_forecast_v3.models import SPECS
    OUT.mkdir(parents=True,exist_ok=True)
    audit=[]
    for p in sorted(V3.rglob('*')):
        if not p.is_file():continue
        row={'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
        if p.suffix=='.md':row['text']=p.read_text(encoding='utf-8')
        elif p.suffix=='.json':
            obj=json.loads(p.read_text());row['shape']=list(obj) if isinstance(obj,dict) else len(obj)
        audit.append(row)
    source=[]
    import ast
    for p in (ROOT/'research/nifty_forecast_v3').glob('*.py'):
        text=p.read_text(encoding='utf-8');tree=ast.parse(text)
        source.append({'path':str(p),'sha256':sha(p),'source':text,'definitions':[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]})
    save('v3-audit-inventory.json',audit);save('v3-source-review.json',source)
    save('registry.json',{'version':'V4-20261118-001','registered_at':now(),'scope':['2025-01-01','2026-12-31'],
        'historical_end':'2026-11-16','all_history_research_exposed':True,
        'frozen_weekly':{k:SPECS[k] for k in ['M05_lgbm','A00_sector','B00_empirical']},
        'fixed_weekly_controls':{'Z_reversion':'.45 if ret5>0 else .55','Z_neutral':.5},
        'frozen_training':'Exact V3 monthly refits, expanding matured labels, endpoint strictly before origin; min126; purged inner42/min80; no retuning',
        'prospective_clock':'09:10:00 IST, prior complete NSE session; execution deadline 09:12:00; process must start before 09:10 and retrieve before decision',
        'source_rule':'Actual local sent/received clocks plus server Date when available; immutable file hashes, revision checks; local clock is not external notarization',
        'primary_weekly_comparisons':['M05_lgbm vs Z_reversion','M05_lgbm vs A00_sector','A00_sector vs Z_reversion'],
        'distribution_candidates':{'D00_empirical':'Latest252 matured return atoms, uniform weights; baseline',
          'D01_regime_shrunk':'Latest252; causal ret21 sign x training-median RV21; conditional counts plus30 unconditional pseudoobservations',
          'D02_student_shrunk':'Fixed df5 Student quantile atoms501; location .5*sectorRidge+.5*historicalmean; RMS inner residual scale, floor .005*sqrt(h/5)',
          'D03_residual_shrunk':'Same shrunk location plus inner heldout sectorRidge residual atoms; no posthoc rescaling'},
        'distribution_status':'New exploratory algorithms; no outer-result selection; D00 and D03 retained for fixed monthly prospective comparison regardless of retrospective rank',
        'calibration_diagnostics':{'models':['M05_lgbm','A00_sector'],'variants':['RAW','SHRINK50 toward matured latest252 base rate','OFFSET bounded[-1,1], inner logloss plus10*b^2/2'], 'activation':'NONE; raw frozen policies remain raw'},
        'lgbm_stress_variants':['rolling126','drop_sector','drop_fo','drop_institution','drop_global','drop_risk','drop_intraday','drop_etf'],
        'stress_status':'Separate retrospective diagnostics, never eligible to replace frozen candidates',
        'uncertainty':'Moving block2H,2000 reps, require8H rows; familywise standardized max-deviation intervals; disjoint phase sensitivity and leave-one-month-out',
        'distribution_selection':'No adaptive selector and no tuning on outer results',
        'primary_prospective':'First30 disjoint weekly /12 monthly for descriptive interim; qualification requires fixed final power-based N and no discretionary significance peeking',
        'no_deployment':True,'v3_design_sha256':sha(ROOT/'research/nifty_forecast_v3/DESIGN.md'),
        'v3_dataset_sha256':sha(V3/'dataset-manifest.json'),'v3_source_hashes':{p.name:sha(p) for p in (ROOT/'research/nifty_forecast_v3').glob('*.py')},
        'v4_initial_code_hashes':{p.name:sha(p) for p in SOURCE.glob('*.py')}})

if __name__=='__main__':register()
