"""Conditional weight stability and local input sensitivity; no refitting policy."""
from __future__ import annotations
import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from .engine import BASE,SEED,write_json,digest,block_interval
from .adaptive import learn_blend


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',type=Path,default=BASE/'adaptive-v2')
    args=parser.parse_args();run=args.run
    frozen=digest(run/'forecast.json')
    call=json.loads((run/'forecast.json').read_text())
    groups=pd.read_csv(run/'group-weights.csv')
    coefficients=pd.read_csv(run/'input-coefficients.csv')
    sensitivity=[];stability=[];comparisons={}
    for target in ['close_return','intraday_return']:
        expert=pd.read_csv(run/f'expert-predictions-{target}.csv')
        replay=pd.read_csv(run/f'prequential-{target}.csv')
        evidence=groups[(groups.target==target)&(groups.status=='eligible')]
        names=evidence.group.tolist()
        eligible=replay[replay.outcome.notna()].tail(504)
        joined=eligible[['target_day','outcome']].merge(expert[['target_day']+names],on='target_day',validate='one_to_one').dropna()
        matrix=np.column_stack([np.full(len(joined),.5),joined[names].to_numpy()])
        y=joined.outcome.to_numpy()
        rng=np.random.default_rng(SEED)
        boot=[];n=len(y);block=10
        for _ in range(300):
            starts=rng.integers(0,n-block+1,int(np.ceil(n/block)))
            indices=(starts[:,None]+np.arange(block)).ravel()[:n]
            boot.append(learn_blend(matrix[indices],y[indices]))
        boot=np.array(boot)
        for j,name in enumerate(['neutral']+names):
            stability.append({'target':target,'group':name,'bootstrap_runs':300,
                'weight_q025':float(np.quantile(boot[:,j],.025)),
                'weight_median':float(np.median(boot[:,j])),
                'weight_q975':float(np.quantile(boot[:,j],.975)),
                'selected_above_1pct_fraction':float((boot[:,j]>.01).mean())})
        f=call['forecasts'][target]
        raw=f['up_probability']['adaptive_groups'];cal=f['up_probability']['calibrated_adaptive']
        calibration_derivative=f['calibration_slope']*cal*(1-cal)/(raw*(1-raw))
        for _,row in coefficients[coefficients.target==target].iterrows():
            group=groups[(groups.target==target)&(groups.group==row.group)].iloc[0]
            p=group.expert_up_probability
            derivative=row.group_weight*p*(1-p)*row.signed_logistic_coefficient*calibration_derivative
            sensitivity.append({**row.to_dict(),'local_up_probability_change_pp_per_training_sd':float(100*derivative)})
        old=pd.read_csv(BASE/f'run-v3/walk-forward-{target}.csv')
        aligned=eligible.merge(old[['target_day','ensemble']],on='target_day',validate='one_to_one')
        y=aligned.outcome.to_numpy();old_loss=(aligned.ensemble.to_numpy()-y)**2
        comparisons[target]={}
        for method in ['adaptive_groups','calibrated_adaptive']:
            difference=old_loss-(aligned[method].to_numpy()-y)**2
            comparisons[target][method]={'paired_brier_improvement_vs_original':float(difference.mean()),
                'paired_ci95':block_interval(difference),'matched_sessions':len(aligned)}
    pd.DataFrame(stability).to_csv(run/'weight-stability.csv',index=False)
    pd.DataFrame(sensitivity).to_csv(run/'input-sensitivity.csv',index=False)
    write_json(run/'comparison-with-original.json',comparisons)
    if digest(run/'forecast.json')!=frozen:raise AssertionError('Frozen call changed')
    print(json.dumps({'comparisons':comparisons,'selected_weight_stability':
        [r for r in stability if r['group'] in ['neutral','gift_nifty','candles_gaps','volatility']]}))


if __name__=='__main__':main()
