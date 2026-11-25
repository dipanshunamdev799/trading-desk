"""Replay every V6 fitted candidate against frozen inputs in a fresh V6 folder.

Does not reacquire data or overwrite the original run. Prequential parent laws
were independently checked against V5; replay treats these as frozen inputs.
"""
import argparse, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
from .common import ROOT, OUT, save, sha, now

PARTS=['forensic-predictions.csv','model-predictions.csv','monthly-risk-predictions.csv',
       'monthly-followup-predictions.csv','weekly-followup-predictions.csv']

def run(destination):
    dest=Path(destination).resolve()
    if not dest.is_relative_to(ROOT/'artifacts/nifty_forecast_v6') or dest.exists():
        raise ValueError('Replay needs a NEW folder inside artifacts/nifty_forecast_v6')
    dest.mkdir(parents=True)
    inputs=list(OUT.glob('labels-*.csv'))+[OUT/n for n in [
        'native-reference.csv','deep-features.csv','liquidity-reference.csv',
        'global-reference.csv','price.csv','state-features.csv','mediator-features.csv',
        'prequential-laws.jsonl','prequential-classifiers.joblib','dataset-manifest.json',
        'feature-definitions.json']]
    for p in inputs:shutil.copy2(p,dest/p.name)
    (dest/'models').mkdir()
    for p in (OUT/'models').glob('baseline-*.joblib'):shutil.copy2(p,dest/'models'/p.name)
    env={**os.environ,'NIFTY_V6_OUT':str(dest)}
    with (dest/'replay.log').open('w',encoding='utf-8') as log:
        for module in ['forensics','experiments','monthly','monthly_followup','followups']:
            subprocess.run([sys.executable,'-m','research.nifty_forecast_v6.'+module],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    checks=[]
    for filename in PARTS+['block-null-predictions.csv','monthly-expanded-nulls.csv','intermediate-horizon-predictions.csv']:
        a=pd.read_csv(OUT/filename);b=pd.read_csv(dest/filename)
        keys=[c for c in ['horizon','model','fold','origin','shift'] if c in a and c in b]
        a=a.sort_values(keys).reset_index(drop=True);b=b.sort_values(keys).reset_index(drop=True)
        if len(a)!=len(b) or not a[keys].equals(b[keys]):raise AssertionError('Replay cohort differs: '+filename)
        cols=[c for c in ['p','predicted_mean','predicted_median','brier','crps','q10','q90'] if c in a and c in b]
        np.testing.assert_allclose(a[cols],b[cols],atol=1e-10,rtol=1e-10,equal_nan=True)
        checks.append({'file':filename,'rows':len(a),'columns':cols,'max_abs_difference':float(np.nanmax(abs(a[cols].to_numpy()-b[cols].to_numpy())))})
    save('replay-verification.json',{'completed_at':now(),'passed':True,'directory':str(dest.relative_to(ROOT)),
         'frozen_inputs':{p.name:sha(p) for p in inputs},'checks':checks,
         'scope':'Full refit of fitted candidate batches; parent prequential laws/mediator inputs frozen and independently audited; no reacquisition'})
    print('Replay identical:',sum(c['rows'] for c in checks),'forecast/control rows',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
