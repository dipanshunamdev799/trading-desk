"""Versioned archive paths, scope and registered comparisons."""
import json
import gzip
import os
from pathlib import Path

from research.nifty_forecast_v15.common import ROOT, V4, V5, V6, V8, V10, V11, V12, V13, V14, sha, now, np, pd

V15 = ROOT / 'artifacts/nifty_forecast_v15/2026-11-25/run-001'
BASE = ROOT / 'artifacts/nifty_forecast_v16'
OUT = Path(os.environ.get('NIFTY_V16_OUT',BASE / '2026-11-25/run-001')).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V16 outputs belong under the V16 artifact tree')
SRC=Path(__file__).parent
FIRST='2025-01-01'
FREEZE='2026-11-17'
END='2026-12-31'
IST='Asia/Kolkata'
CLOCKS=('08:30','08:45','08:55','09:10','09:25','10:20','17:00')
TIMING_POLICIES={'base':60,'tight':30,'conservative':180,'close_plus_six_hours':360,'vendor_date_plus_day':1440}
HORIZONS=(5,21)
EXPECTED={5:265,21:217}
HIST=160
SEED=161125
PATH_N=256
BOOT=1500
BLOCKS=(5,10,21,42)

def read(name,root=OUT):
    return json.loads((root/name).read_text(encoding='utf-8-sig'))

def write(name,df,index=False):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(p,index=index)

def save(name,value):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,default=str,allow_nan=False),encoding='utf-8')

def matrix(name,folder=OUT):
    return pd.read_csv(folder/name,index_col=0,low_memory=False)

def stamp(day,clock):
    return pd.Timestamp(f'{day}T{clock}:00',tz=IST)

def register():
    if (OUT/'registration.json').exists():
        return
    save('registration.json',dict(registered_at=now(),historical_scope=[FIRST,FREEZE],forward_year=2026,
         clocks_IST=CLOCKS,source_delay_minutes=TIMING_POLICIES,seed=SEED,history=HIST,minimum_training=54,
         bootstrap_draws=BOOT,block_lengths=BLOCKS,path_draws=PATH_N,horizons=HORIZONS,original_cohorts=EXPECTED,
         window_maturity='target date strictly earlier than decision day, with a one-complete-session guard on the training outcome',
         gap='official NIFTY open divided by previous official NIFTY close minus one',
         directional_experiments=['archived replay','neutral','historical distribution','previous domestic return/volatility',
            'single US return','equal six-market mean','ridge','joint sign and magnitude','Student t location and scale',
            'shallow nonlinear interactions','cluster-balanced fit','first-session decomposition','matched OHLC session blocks',
            'reduced-rank multitask','fixed coherent mixture'],
         falsification=['strict pre-auction hours','delay 1/2/5','smoothed','foreign week-block shift/permutation','noise',
            'drop one market','publication lag policies','leave month out','large gap episodes',
            'unavailable future state mutation','copy invariance','matched refit and reselection'],
         score_families=['gap timing','freshness by return target','disagreement','domestic sector channels','multiscale',
            'conditional risk and range','fixed barrier and first passage','gap fill survivor status'],
         inference='historical research-exposed. Forward refresh separate. Added falsifications reported as diagnostics.'))

if __name__=='__main__':
    register()
