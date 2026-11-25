"""Exact artifact arithmetic and 2025-only reproduction of the old architecture."""
import json
import numpy as np
import pandas as pd
from .audit import ROOT,OUT,OLD,save
from .data import load_series

def main():
    diagnostics={}
    for name in ['week','month']:
        p=OLD/f'horizons-v2/evaluation-{name}.csv';g=pd.read_csv(p)
        raw=g.adaptive_groups.to_numpy();cal=g.calibrated_adaptive.to_numpy();y=g.outcome.to_numpy()
        flips=(raw>=.5)!=(cal>=.5)
        diagnostics[name]={'legacy_scope':'Includes November2024 training; not a valid V3 candidate',
            'n':len(g),'raw_brier':float(np.mean((raw-y)**2)),'calibrated_brier':float(np.mean((cal-y)**2)),
            'raw_accuracy':float(np.mean((raw>=.5)==y)),'calibrated_accuracy':float(np.mean((cal>=.5)==y)),
            'classification_flips':int(flips.sum()),'flips_correct_to_wrong':int((flips&((raw>=.5)==y)).sum()),
            'flips_wrong_to_correct':int((flips&((raw>=.5)!=y)).sum()),
            'mean_calibration_intercept':float(g.calibration_intercept.mean()),
            'mean_raw_probability':float(raw.mean()),'mean_calibrated_probability':float(cal.mean()),
            'actual_up_frequency':float(y.mean()),
            'explanation':'Mapping learns recent overlapping-label prevalence; intercept drift can reverse weak forecasts across .5. This is descriptive diagnosis, not proof of a sole cause.'}
    save('legacy-artifact-reproduction.json',diagnostics)
    # Refit old source algorithms without any old market observations/state.
    from research.nifty_forecast.engine import make_features
    from research.nifty_forecast.adaptive import institutional_features
    from research.nifty_forecast.horizons import future_sessions,horizon_labels,fit_experts,replay_predictions,evaluate
    all_data,_=load_series()
    bars={k:v for k,v in all_data.items() if not k.startswith(('stock_','global_')) and k!='niftybees'}
    rename={'global_gift':'gift_nifty','global_sp500':'sp500','global_dow':'dow','global_hang_seng':'hang_seng','global_brent':'brent','global_usdinr':'usdinr'}
    global_data={rename[k]:v for k,v in all_data.items() if k in rename}
    x,day_labels,_=make_features(bars,global_data,'2026-11-17')
    inst,_=institutional_features(OLD/'institutional-v1',OLD/'inputs-v2',day_labels.decision_day.tolist())
    x=pd.concat([x,inst],axis=1)
    from research.nifty_forecast.adaptive import feature_groups
    groups=feature_groups(x.columns);calendar=json.loads((OLD/'horizon-calendar-v1.json').read_text())
    future=future_sessions(bars['nifty_spot'].index[-1],calendar,21);repro={}
    for name,h in [('week',5),('month',21)]:
        labels=horizon_labels(day_labels,bars,future,h);pred,n,fits=fit_experts(x,labels,groups,h)
        replay,allocation=replay_predictions(pred,n,labels,h)
        replay.to_csv(OUT/f'legacy-2025-only-{name}.csv',index=False)
        ready=replay[replay.outcome.notna()&(replay.meta_training_n>=126)&(replay.calibration_training_n>=126)]
        repro[name]={'data_start':'2025-01-01','no_pre2025_values_or_state':True,'features':len(x.columns),
            'fully_learned':evaluate(ready,h),'all_resolved':evaluate(replay[replay.outcome.notna()],h),
            'notes':'Original old architecture on fresh 2025-only vintage; differs from old frozen source vintage and sample. Old 252+126 evidence gates leave very few monthly validation origins.'}
    save('legacy-2025-only-reproduction.json',repro)
    print('Legacy arithmetic and 2025-only reproduction complete',flush=True)
if __name__=='__main__':main()
