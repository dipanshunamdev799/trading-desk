"""V15 read-only predecessor paths and research registration."""
import json
import os
from pathlib import Path

from research.nifty_forecast_v14.common import ROOT, V5, V6, V8, V10, V11, V12, V13, sha, now, np, pd

SRC = Path(__file__).parent
BASE = ROOT / 'artifacts/nifty_forecast_v15'
V4 = ROOT / 'artifacts/nifty_forecast_v4/2026-11-18/run-001'
V14 = ROOT / 'artifacts/nifty_forecast_v14/2026-11-25/run-001'
OUT = Path(os.environ.get('NIFTY_V15_OUT', BASE / '2026-11-25/run-001')).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V15 outputs must be in the V15 artifact directory')

FIRST='2025-01-01'
FREEZE='2026-11-17'
LAST='2026-12-31'
HORIZONS=(5,21)
EXPECTED={5:265,21:217}
CHECKPOINTS={5:(0,1,2,3,4),21:(0,1,5,10,15,20)}
CLOCKS={'pre_open':'09:10','opening':'10:05','midday':'12:30','near_close':'15:10','completed':'17:00'}
SEED=151125
N=256
HIST=180
BLOCKS=(5,10,21,42)
DRAW=1500
BARRIERS=(.005,.01,.02,.03,.05)
MODELS=('frozen','zero_remaining','price_only','historical','iv_restart','gjr_restart','refit',
        'incremental','domestic','domestic_stale','full','derivatives_first','full_stale_surface','full_stale_global',
        'full_delayed','full_permuted','full_noise','particle','hybrid','vol_state','analogue',
        'vol_only_shock','shock_persistence','sign_magnitude','heavy_tail','episode_tail')
CORE_CHECKS=('frozen','price_only','historical','iv_restart','gjr_restart','refit','incremental','domestic',
             'full','particle','hybrid','vol_state','analogue')
PREDECESSOR_PATH={5:'gjr_iv',21:'gjr_student'}
DEMO='2026-10-15'

def save(name,obj):
    file=OUT/name
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(obj,indent=2,default=str,allow_nan=False),encoding='utf-8')

def read(name,root=OUT):
    return json.loads((root/name).read_text(encoding='utf-8'))

def write(name,df,index=False):
    file=OUT/name
    file.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(file,index=index)

def matrix(name,root=OUT):
    return pd.read_csv(root/name,index_col=0,low_memory=False)

def register():
    if (OUT/'registration.json').exists():
        return
    save('registration.json',dict(timestamp=now(),historical_freeze=FREEZE,scope=[FIRST,LAST],seed=SEED,draws=N,
        horizons=HORIZONS,reference_counts=EXPECTED,all_daily=True,display_checkpoints=CHECKPOINTS,intraday_IST=CLOCKS,
        barriers=BARRIERS,expansion_multipliers=[1.25,1.5],contraction=.8,
        n_boot=DRAW,block_lengths=BLOCKS,models=MODELS,prior_paths=PREDECESSOR_PATH,
        targets=['endpoint return relative to original close','remaining endpoint return','whole and remaining range',
                 'whole and remaining realized volatility','extrema and drawdown','first-touch survival risk sets'],
        asof_rule='Fixed original target identity. Hth observed trading-session labels remain frozen. Term features use only schedule known at the decision.',
        training='strictly matured before each fit cutoff, training-only conditioning and transformations',
        choice='Compare matched price-only, restart IV/GJR, and same-time historical controls. Use separate losses and target-window aggregation. Follow-up allowed for observed anomalies and calibration mechanisms only.'))
