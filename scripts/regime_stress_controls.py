from pathlib import Path
import sys,json
from concurrent.futures import ProcessPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from scripts import research_regimes as core
from research.regime_opportunities.framework import OUT,PERIODS,save
from research.regime_opportunities.engine import simulate
from research.ema_validation.engine import orders
from research.swing_diagnosis.common import clean

def job(task):
    regime,style,stage=task;seeds=json.loads((OUT/'freeze.json').read_text())['broad_seeds'];key=f'{regime}-{style}-{stage}-stress-random';folder=OUT/'portfolio_jobs';path=folder/(key+'.json');archive=folder/(key+'.npz')
    if path.exists() and archive.exists():return json.loads(path.read_text())
    rows=[];packed={};gate=core.INPUT['mask_'+regime]
    for seed in seeds:
        r=simulate(core.Q,orders(core.Q,core.random_mask(style,seed)&gate[None,:]),*PERIODS[stage],cost=2,slip_bps=10)
        row=dict(regime=regime,style=style,stage=stage,seed=seed,scenario='double_fees10bps',**r['metrics']);row['rejections']=json.dumps(clean(row['rejections']));rows.append(clean(row))
        for k in ['equity','cash','utilization','positions','trades','cols']:packed[f'{seed}_{k}']=r[k]
    np.savez_compressed(archive,**packed);path.write_text(json.dumps(rows));return rows

def main():
    short=json.loads((OUT/'frozen-combinations.json').read_text())['combinations'];save('stress-null-design.json',dict(scope='Same frozen64commonseedopportunitycontrols underdoublefees10bps; no re-selection. Apples-to-apples stress context for the three training hypotheses.',seeds=64))
    rows=[]
    with ProcessPoolExecutor(max_workers=4,initializer=core.worker_init) as pool:
        for f in as_completed([pool.submit(job,(x['regime'],x['style'],stage)) for x in short for stage in PERIODS]):rows+=f.result()
    pd.DataFrame(rows).to_csv(OUT/'stress-random-results.csv',index=False);print('STRESS_NULL_COMPLETE')

if __name__=='__main__':main()
