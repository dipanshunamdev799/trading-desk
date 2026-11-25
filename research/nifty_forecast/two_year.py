"""Strict two-year inputs, feature initialization and learned prediction weights."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from .engine import BASE,ROOT,Scale,load_panel,make_features,digest,write_json,sigmoid
from .adaptive import (institutional_features,feature_groups,weighted_logistic,
    sequential_blend,weight_explanations,metrics,METHODS)

START='2024-11-17'
TARGET='2026-11-17'
FIRST_PREDICTION=252


def bounded_series(series,start=START,target=TARGET):
    return {name:frame.loc[(frame.index>=start)&(frame.index<target)].copy()
            for name,frame in series.items()}


def bounded_features(bars,globals_,start=START,target=TARGET):
    clipped=bounded_series(bars,start,target)
    globals_clipped=bounded_series(globals_,start,target)
    x,labels,core=make_features(clipped,globals_clipped,target)
    if (labels.decision_day<start).any() or (labels.decision_day>=target).any():
        raise AssertionError('Feature decision escaped the two-year window')
    return x,labels,core,clipped,globals_clipped


def fit_experts(x,labels,groups,target):
    """Same experts, with the startup holdoff bounded to one training year."""
    raw=x.to_numpy(float);returns=labels[target].to_numpy(float)
    y=(returns>0).astype(float);known=np.isfinite(returns)
    pred=np.full((len(x),len(groups)),np.nan);counts=np.zeros_like(pred,dtype=int)
    fits=[];eligible=np.arange(len(x))>=FIRST_PREDICTION
    months=labels.target_day.str[:7]
    blocks=[np.flatnonzero((months==month).to_numpy()&eligible) for month in months[eligible].unique()]
    blocks=[b[b<len(x)-1] for b in blocks]
    blocks=[b for b in blocks if len(b)]+[np.array([len(x)-1])]
    for block in blocks:
        first=int(block[0]);history=np.flatnonzero(known&(np.arange(len(x))<first))[-1260:]
        if len(history) and labels.target_day.iloc[history[-1]]>labels.decision_day.iloc[first]:
            raise AssertionError('Unresolved training label')
        for j,(name,columns) in enumerate(groups.items()):
            if not columns:continue
            cols=[x.columns.get_loc(k) for k in columns]
            valid=np.isfinite(raw[history][:,cols]).mean(axis=1)>=.5
            train=history[valid];counts[block,j]=len(train)
            minimum=63 if name in ['institutional_cash','fii_positioning'] else 252
            if len(train)<minimum:continue
            scaler=Scale().fit(raw[train][:,cols])
            beta=weighted_logistic(scaler.transform(raw[train][:,cols]),y[train])
            observed=np.isfinite(raw[block][:,cols]).mean(axis=1)>=.5
            query=block[observed]
            if len(query):
                z=scaler.transform(raw[query][:,cols])
                pred[query,j]=np.clip(sigmoid(np.column_stack([np.ones(len(query)),z])@beta),.05,.95)
            fits.append({'target':target,'group':name,'fit_for_target':labels.target_day.iloc[first],
                'first_training_target':labels.target_day.iloc[train[0]],
                'last_training_target':labels.target_day.iloc[train[-1]],'training_n':len(train),
                'columns':columns,'intercept':float(beta[0]),'coefficients':beta[1:].tolist(),
                'mean':scaler.mean.tolist(),'std':scaler.std.tolist(),'median':scaler.median.tolist(),
                'current_fit':first==len(x)-1})
    return pred,counts,fits


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=BASE/'two-year-v1')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    reference=BASE/'adaptive-v2/forecast.json';reference_hash=digest(reference)
    source=json.loads(reference.read_text())
    bars,globals_,old_audit,provisional,_,_=load_panel(BASE/'inputs-v2',BASE/'supplement-v1',TARGET)
    x,labels,core,bars,globals_=bounded_features(bars,globals_)
    institution,institution_audit=institutional_features(BASE/'institutional-v1',BASE/'inputs-v2',labels.decision_day.tolist())
    x=pd.concat([x,institution],axis=1);groups=feature_groups(x.columns)
    x.to_csv(args.out/'feature-panel.csv',index=False);labels.to_csv(args.out/'labels.csv',index=False)
    series_audit={prefix+name:{'first':frame.index[0],'last':frame.index[-1],'sessions':len(frame)}
                  for prefix,collection in [('',bars),('global_',globals_)] for name,frame in collection.items() if not frame.empty}
    write_json(args.out/'data-audit.json',{'requested_start':START,'exclusive_end':TARGET,
        'feature_rows':len(x),'resolved_target_rows':int(labels.close_return.notna().sum()),
        'first_feature_decision':labels.decision_day.iloc[0],'last_feature_decision':labels.decision_day.iloc[-1],
        'series':series_audit,'institutional':institution_audit,'groups':groups,
        'first_prediction_index':FIRST_PREDICTION,'indicator_initialization':'All series clipped before indicators; no imported fitted state',
        'provisional_bars':[r for r in provisional if START<=r['day']<TARGET]})
    results={};forecasts={};group_rows=[];features=[]
    for target in ['close_return','intraday_return']:
        pred,counts,fits=fit_experts(x,labels,groups,target)
        replay,allocations=sequential_blend(pred,counts,labels,target,start=FIRST_PREDICTION)
        replay.to_csv(args.out/f'prequential-{target}.csv',index=False)
        pd.concat([labels[['decision_day','target_day']],pd.DataFrame(pred,columns=list(groups))],axis=1).to_csv(args.out/f'expert-predictions-{target}.csv',index=False)
        pd.concat([labels[['decision_day','target_day']],pd.DataFrame(allocations,columns=['neutral']+list(groups))],axis=1).to_csv(args.out/f'daily-weights-{target}.csv',index=False)
        write_json(args.out/f'expert-fits-{target}.json',fits)
        all_oos=replay[replay.outcome.notna()].copy()
        ready=all_oos[(all_oos.meta_training_n>=126)&(all_oos.calibration_training_n>=126)].copy()
        if len(ready)<20:raise ValueError('Too few fully learned test decisions in the bounded window')
        ready.to_csv(args.out/f'evaluation-{target}.csv',index=False)
        results[target]={'all_after_initial_expert_training':metrics(all_oos),
            'fully_learned_evaluation':metrics(ready),
            'fully_learned_published_only':metrics(ready[ready.target_day<'2026-11-16'])}
        grow,frow=weight_explanations(x,labels,groups,pred,counts,fits,allocations,target)
        # The shared explanation helper's neutral count uses the old holdoff.
        grow[0]['out_of_sample_n']=len(all_oos)
        grow[0]['recent_oos_n']=min(252,len(all_oos))
        group_rows.extend(grow);features.extend(frow)
        today=replay.iloc[-1]
        history=labels[target].dropna().tail(252).to_numpy()
        forecasts[target]={'primary_model':'calibrated_adaptive',
            'up_probability':{k:float(today[k]) for k in METHODS},
            'group_weights':{r['group']:r['weight'] for r in grow},
            'calibration_intercept':float(today.calibration_intercept),'calibration_slope':float(today.calibration_slope),
            'meta_training_n':int(today.meta_training_n),'calibration_training_n':int(today.calibration_training_n),
            'training_n':int(labels[target].notna().sum()),
            'prior252_quantiles':{str(q):float(np.quantile(history,q)) for q in [.1,.25,.5,.75,.9]}}
        forecasts[target]['up_probability']['ensemble']=float(today.calibrated_adaptive)
        print(target,json.dumps({'current':forecasts[target]['up_probability'],
            'all_oos_n':len(all_oos),'fully_learned_n':len(ready),'fully_learned_period':results[target]['fully_learned_evaluation']['period']}),flush=True)
    spot=float(labels.reference_close.iloc[-1]);d=bars['nifty_spot']
    forecasts['close_return']['closing_level_quantiles']={k:spot*(1+v) for k,v in forecasts['close_return']['prior252_quantiles'].items()}
    pd.DataFrame(group_rows).to_csv(args.out/'group-weights.csv',index=False)
    pd.DataFrame(features).to_csv(args.out/'input-coefficients.csv',index=False)
    write_json(args.out/'validation.json',results)
    call={'experiment':'NIFTY strict two-calendar-year learned weights','target_date':TARGET,
        'issued_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
        'history_window':{'inclusive_start':START,'exclusive_end':TARGET,'no_older_indicator_warmup':True},
        'primary_model':'calibrated_adaptive','input_manifests':source['input_manifests'],
        'comparison_forecast_sha256':reference_hash,'comparison_forecast_path':str(reference),
        'source_code_hashes':{p.name:digest(p) for p in [Path(__file__),Path(__file__).with_name('TWO_YEAR_PROTOCOL.md'),
            Path(__file__).with_name('adaptive.py'),Path(__file__).with_name('engine.py')]},
        'features':list(x.columns),'forecasts':forecasts,
        'levels':{'reference_close':spot,'reference_day':d.index[-1],
            'previous_session_high':float(d.high.iloc[-1]),'previous_session_low':float(d.low.iloc[-1]),
            'prior20_high':float(d.high.tail(20).max()),'prior20_low':float(d.low.tail(20).min())},
        'provisional_reference':True,'outcome':{'official_close':None,'official_open':None},
        'limits':['Only two years total; training and weight-learning consume part of that window',
            'Latest historical evaluation already examined in earlier research; exploratory, not new confirmation',
            'Monday NIFTY reference comes from the earlier post-close quote freeze',
            'Same conservative global daily lag and institutional publication assumptions as the longer-history study']}
    write_json(args.out/'forecast.json',call)
    write_json(args.out/'artifact-manifest.json',{'files':{p.name:digest(p) for p in sorted(args.out.glob('*')) if p.is_file()}})
    if digest(reference)!=reference_hash:raise AssertionError('Longer-history comparison forecast changed')
    print(json.dumps({'out':str(args.out),'series_sessions':len(d),'feature_rows':len(x),
        'validation':{k:v['fully_learned_evaluation']['methods'] for k,v in results.items()}},indent=2),flush=True)


if __name__=='__main__':main()
