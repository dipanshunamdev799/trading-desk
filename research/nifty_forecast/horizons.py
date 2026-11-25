"""Maturity-aware weekly/monthly direction, weights and return distributions."""
from __future__ import annotations
import argparse
from datetime import datetime,timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from .engine import BASE,ROOT,SEED,Scale,load_panel,sigmoid,digest,write_json
from .two_year import START,TARGET,bounded_features
from .adaptive import (institutional_features,feature_groups,weighted_logistic,
                       learn_blend,fit_calibrator,weight_explanations)

METHODS=['neutral','rolling_frequency','equal_groups','adaptive_groups','calibrated_adaptive']
HORIZONS={'week':5,'month':21}


def future_sessions(reference,calendar,count=21):
    entries={r['date']:r for r in calendar['payload']}
    result=[];day=pd.Timestamp(reference).date()
    while len(result)<count:
        day+=timedelta(days=1);name=day.isoformat();entry=entries.get(name,{})
        closed='NSE' in entry.get('closed_exchanges',[])
        opened=any(r.get('exchange')=='NSE' for r in entry.get('open_exchanges',[]))
        if closed and opened:raise ValueError(f'Ambiguous NSE calendar: {name}')
        if not closed and (day.weekday()<5 or opened):result.append(name)
    return result


def horizon_labels(day_labels,bars,future,h):
    price=bars['nifty_spot'];sessions=list(price.index)+future
    positions={day:i for i,day in enumerate(price.index)}
    rows=[]
    for row in day_labels.itertuples():
        pos=positions[row.decision_day];end=pos+h
        value=float(price.close.iloc[end]/price.close.iloc[pos]-1) if end<len(price) else np.nan
        rows.append({'decision_day':row.decision_day,'forecast_day':row.target_day,
            'target_day':sessions[end],'label_end_day':sessions[end],
            'reference_close':float(price.close.iloc[pos]),'horizon_return':value,'horizon':h})
    return pd.DataFrame(rows)


def matured_indices(labels,decision_index,start=0,limit=None):
    indices=np.arange(len(labels));day=labels.decision_day.iloc[decision_index]
    mask=(indices<decision_index)&(indices>=start)&labels.horizon_return.notna().to_numpy() \
         &(labels.label_end_day.to_numpy()<=day)
    selected=np.flatnonzero(mask)
    return selected[-limit:] if limit else selected


def fit_experts(x,labels,groups,h):
    raw=x.to_numpy(float);y=(labels.horizon_return.to_numpy()>0).astype(float)
    start=252+h-1;eligible=np.arange(len(x))>=start
    pred=np.full((len(x),len(groups)),np.nan);counts=np.zeros_like(pred,dtype=int);fits=[]
    months=labels.forecast_day.str[:7]
    blocks=[np.flatnonzero((months==month).to_numpy()&eligible) for month in months[eligible].unique()]
    blocks=[b[b<len(x)-1] for b in blocks]
    blocks=[b for b in blocks if len(b)]+[np.array([len(x)-1])]
    for block in blocks:
        first=int(block[0]);history=matured_indices(labels,first,limit=1260)
        for j,(name,columns) in enumerate(groups.items()):
            if not columns:continue
            cols=[x.columns.get_loc(k) for k in columns]
            valid=np.isfinite(raw[history][:,cols]).mean(axis=1)>=.5
            train=history[valid];counts[block,j]=len(train)
            if len(train)<(63 if name in ['institutional_cash','fii_positioning'] else 252):continue
            scaler=Scale().fit(raw[train][:,cols]);beta=weighted_logistic(scaler.transform(raw[train][:,cols]),y[train])
            observed=np.isfinite(raw[block][:,cols]).mean(axis=1)>=.5;query=block[observed]
            if len(query):
                z=scaler.transform(raw[query][:,cols])
                pred[query,j]=np.clip(sigmoid(np.column_stack([np.ones(len(query)),z])@beta),.05,.95)
            fits.append({'target':'horizon_return','group':name,'horizon':h,
                'fit_for_target':labels.forecast_day.iloc[first],'fit_after_close':labels.decision_day.iloc[first],
                'first_training_origin':labels.decision_day.iloc[train[0]],
                'last_training_origin':labels.decision_day.iloc[train[-1]],
                'last_training_endpoint':labels.label_end_day.iloc[train[-1]],
                'first_training_target':labels.label_end_day.iloc[train[0]],
                'last_training_target':labels.label_end_day.iloc[train[-1]],'training_n':len(train),
                'columns':columns,'intercept':float(beta[0]),'coefficients':beta[1:].tolist(),
                'mean':scaler.mean.tolist(),'std':scaler.std.tolist(),'median':scaler.median.tolist(),
                'current_fit':first==len(x)-1})
    return pred,counts,fits


def weighted_quantile(values,weights,probabilities):
    order=np.argsort(values,kind='stable');v=np.asarray(values)[order];w=np.asarray(weights)[order]
    c=np.cumsum(w)/np.sum(w)
    # Empirical inverse CDF: interpolation across zero would put probability
    # mass in the gap between negative and positive conditional samples.
    return v[np.minimum(np.searchsorted(c,probabilities,side='left'),len(v)-1)]


def magnitude_distribution(returns,p):
    returns=np.asarray(returns,float)
    if not len(returns):raise ValueError('No matured return magnitude history')
    up=returns>0;down=~up
    if not up.any() or not down.any():
        weights=np.full(len(returns),1/len(returns))
    else:weights=np.where(up,p/max(1,int(up.sum())),(1-p)/max(1,int(down.sum())))
    quantiles=weighted_quantile(returns,weights,[.1,.25,.5,.75,.9])
    return {'mean':float(np.dot(weights,returns)),
            'quantiles':{str(q):float(v) for q,v in zip([.1,.25,.5,.75,.9],quantiles)},
            'unconditional_quantiles':{str(q):float(np.quantile(returns,q)) for q in [.1,.25,.5,.75,.9]},
            'historical_n':len(returns),'positive_n':int(up.sum()),'nonpositive_n':int(down.sum())}


def replay_predictions(pred,counts,labels,h):
    start=252+h-1;y=(labels.horizon_return.to_numpy()>0).astype(float)
    allocation=np.zeros((len(labels),pred.shape[1]+1));allocation[:,0]=1
    raw_history=np.full(len(labels),np.nan);rows=[]
    for i in range(start,len(labels)):
        history=matured_indices(labels,i,start,504);available=np.isfinite(pred[i])
        evidence=np.sum(np.isfinite(pred[history]),axis=0) if len(history) else np.zeros(pred.shape[1])
        active=available&(evidence>=126)&(counts[i]>=252);active_idx=np.flatnonzero(active)
        meta=np.array([],dtype=int)
        if len(history)>=126 and len(active_idx):
            common=np.isfinite(pred[history][:,active_idx]).all(axis=1);meta=history[common]
            if len(meta)>=126:
                matrix=np.column_stack([np.full(len(meta),.5),pred[meta][:,active_idx]])
                learned=learn_blend(matrix,y[meta]);allocation[i,0]=learned[0];allocation[i,active_idx+1]=learned[1:]
            else:meta=np.array([],dtype=int)
        query=np.where(available,pred[i],.5);raw=float(allocation[i]@np.r_[.5,query]);raw_history[i]=raw
        calibration=matured_indices(labels,i,start,252)
        calibration=calibration[np.isfinite(raw_history[calibration])]
        beta=fit_calibrator(raw_history[calibration],y[calibration]) if len(calibration)>=126 else np.array([0.,1.])
        calibrated=float(np.clip(sigmoid(beta[0]+beta[1]*np.log(raw/(1-raw))),.05,.95))
        prior=matured_indices(labels,i,limit=1260);magnitude_history=prior[-252:]
        sizes=magnitude_distribution(labels.horizon_return.to_numpy()[magnitude_history],calibrated)
        realized=float(labels.horizon_return.iloc[i]);resolved=np.isfinite(realized)
        row={'i':i,'decision_day':labels.decision_day.iloc[i],'forecast_day':labels.forecast_day.iloc[i],
            'target_day':labels.label_end_day.iloc[i],'label_end_day':labels.label_end_day.iloc[i],
            'horizon':h,'outcome':int(y[i]) if resolved else np.nan,'return':realized,
            'neutral':.5,'rolling_frequency':float((y[prior].sum()+1)/(len(prior)+2)),
            'equal_groups':float(query[active].mean()) if active.any() else .5,
            'adaptive_groups':raw,'calibrated_adaptive':calibrated,
            'meta_training_n':len(meta),'meta_last_endpoint':labels.label_end_day.iloc[meta[-1]] if len(meta) else None,
            'calibration_training_n':len(calibration),'calibration_last_endpoint':labels.label_end_day.iloc[calibration[-1]] if len(calibration) else None,
            'calibration_intercept':float(beta[0]),'calibration_slope':float(beta[1]),
            'active_experts':int(active.sum()),'magnitude_history_n':len(magnitude_history),
            'magnitude_last_endpoint':labels.label_end_day.iloc[magnitude_history[-1]],
            'median_return':sizes['quantiles']['0.5'],'mean_return':sizes['mean'],
            'unconditional_median_return':sizes['unconditional_quantiles']['0.5']}
        row.update({f'q{int(float(q)*100)}':v for q,v in sizes['quantiles'].items()})
        rows.append(row)
    return pd.DataFrame(rows),allocation


def block_interval(values,h):
    values=np.asarray(values);n=len(values);block=2*h
    if n<8*h:return None
    rng=np.random.default_rng(SEED)
    starts=rng.integers(0,n-block+1,(2000,int(np.ceil(n/block))))
    indices=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:n]
    return np.quantile(values[indices].mean(axis=1),[.025,.975]).tolist()


def nonoverlapping(frame):
    chosen=[];last_end=''
    for index,row in frame.sort_values('decision_day').iterrows():
        if row.decision_day>=last_end:
            chosen.append(index);last_end=row.label_end_day
    return frame.loc[chosen].copy()


def evaluate(frame,h):
    if frame.empty:return {'n':0,'methods':{},'period':None}
    y=frame.outcome.to_numpy(float);stats={}
    for method in METHODS:
        p=frame[method].to_numpy(float);loss=(p-y)**2
        stats[method]={'n':len(y),'brier':float(loss.mean()),
            'accuracy':float(((p>=.5)==y).mean()),
            'log_loss':float((-y*np.log(p)-(1-y)*np.log(1-p)).mean()),
            'brier_improvement_vs_neutral':float(np.mean(.25-loss)),
            'paired_ci95':block_interval(.25-loss,h),
            'first_half_brier':float(loss[:len(loss)//2].mean()) if len(loss)>1 else None,
            'second_half_brier':float(loss[len(loss)//2:].mean())}
    return {'n':len(frame),'origin_period':[frame.forecast_day.iloc[0],frame.forecast_day.iloc[-1]],
        'endpoint_period':[frame.label_end_day.iloc[0],frame.label_end_day.iloc[-1]],
        'nonoverlapping_n':len(nonoverlapping(frame)),'always_up_accuracy':float(y.mean()),
        'always_down_accuracy':float(1-y.mean()),'methods':stats,
        'median_mae_bps':float((frame['return']-frame.median_return).abs().mean()*10000),
        'unconditional_median_mae_bps':float((frame['return']-frame.unconditional_median_return).abs().mean()*10000),
        'central50_coverage':float(((frame['return']>=frame.q25)&(frame['return']<=frame.q75)).mean()),
        'central80_coverage':float(((frame['return']>=frame.q10)&(frame['return']<=frame.q90)).mean()),
        'ci_block_length':2*h,'ci_minimum_origin_rows':8*h,
        'ci_note':'Conditional moving-block diagnostic' if len(frame)>=8*h else 'Not estimated: too few independent horizon outcomes'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=BASE/'horizons-v1')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    calendar_path=BASE/'horizon-calendar-v1.json';calendar=json.loads(calendar_path.read_text())
    previous_path=BASE/'two-year-v1/forecast.json';previous_hash=digest(previous_path)
    previous=json.loads(previous_path.read_text())
    bars,global_data,_,provisional,_,_=load_panel(BASE/'inputs-v2',BASE/'supplement-v1',TARGET)
    x,day_labels,_,bars,global_data=bounded_features(bars,global_data)
    institution,inst_audit=institutional_features(BASE/'institutional-v1',BASE/'inputs-v2',day_labels.decision_day.tolist())
    x=pd.concat([x,institution],axis=1);groups=feature_groups(x.columns)
    future=future_sessions(bars['nifty_spot'].index[-1],calendar,21)
    x.to_csv(args.out/'feature-panel.csv',index=False)
    write_json(args.out/'data-audit.json',{'start':START,'exclusive_end':TARGET,'raw_nifty_sessions':len(bars['nifty_spot']),
        'feature_rows':len(x),'features':list(x.columns),'groups':groups,'institutional':inst_audit,
        'future_sessions':future,'calendar_sha256':digest(calendar_path),'provisional_bars':provisional,
        'initialization':'All source series clipped before deriving features; same frozen context as the two-year daily study'})
    validation={};forecasts={};all_weights=[];all_coefficients=[]
    for name,h in HORIZONS.items():
        labels=horizon_labels(day_labels,bars,future,h);labels.to_csv(args.out/f'labels-{name}.csv',index=False)
        pred,counts,fits=fit_experts(x,labels,groups,h)
        replay,allocation=replay_predictions(pred,counts,labels,h)
        replay.to_csv(args.out/f'prequential-{name}.csv',index=False)
        pd.concat([labels[['decision_day','forecast_day','label_end_day']],pd.DataFrame(pred,columns=list(groups))],axis=1).to_csv(args.out/f'expert-predictions-{name}.csv',index=False)
        pd.concat([labels[['decision_day','forecast_day','label_end_day']],pd.DataFrame(allocation,columns=['neutral']+list(groups))],axis=1).to_csv(args.out/f'daily-weights-{name}.csv',index=False)
        write_json(args.out/f'expert-fits-{name}.json',fits)
        resolved=replay[replay.outcome.notna()].copy()
        ready=resolved[(resolved.meta_training_n>=126)&(resolved.calibration_training_n>=126)].copy()
        ready.to_csv(args.out/f'evaluation-{name}.csv',index=False)
        nonoverlapping(ready).to_csv(args.out/f'nonoverlapping-evaluation-{name}.csv',index=False)
        validation[name]={'horizon_sessions':h,'all_after_expert_training':evaluate(resolved,h),
            'fully_learned':evaluate(ready,h),'fully_learned_nonoverlapping':evaluate(nonoverlapping(ready),h),
            'fully_learned_published_only':evaluate(ready[ready.label_end_day<'2026-11-16'],h)}
        rows,coefs=weight_explanations(x,labels,groups,pred,counts,fits,allocation,'horizon_return')
        # Evidence for current horizon must have matured, not merely originated.
        mature=matured_indices(labels,len(labels)-1,252+h-1,504)
        for j,row in enumerate(rows):
            row['target']=name
            row['out_of_sample_n']=len(mature) if j==0 else int(np.isfinite(pred[mature,j-1]).sum())
            if j==0:row['recent_oos_n']=min(252,len(mature))
        for row in coefs:row['target']=name
        all_weights.extend(rows);all_coefficients.extend(coefs)
        now=replay.iloc[-1];p=float(now.calibrated_adaptive)
        history=matured_indices(labels,len(labels)-1,limit=252)
        sizes=magnitude_distribution(labels.horizon_return.to_numpy()[history],p)
        reference=float(day_labels.reference_close.iloc[-1])
        forecasts[name]={'horizon_sessions':h,'expected_endpoint_date':labels.label_end_day.iloc[-1],
            'reference_close':reference,'up_probability':{method:float(now[method]) for method in METHODS},
            'primary_model':'calibrated_adaptive','calibration_intercept':float(now.calibration_intercept),
            'calibration_slope':float(now.calibration_slope),'meta_training_n':int(now.meta_training_n),
            'calibration_training_n':int(now.calibration_training_n),
            'group_weights':{r['group']:r['weight'] for r in rows},'return_distribution':sizes,
            'projected_median_level':reference*(1+sizes['quantiles']['0.5']),
            'projected_mean_level':reference*(1+sizes['mean']),
            'closing_level_quantiles':{q:reference*(1+v) for q,v in sizes['quantiles'].items()},
            'magnitude_last_observed_endpoint':labels.label_end_day.iloc[history[-1]],
            'outcome':{'official_endpoint_date':None,'official_reference_close':None,'official_endpoint_close':None,'return':None}}
        print(name,json.dumps({'current':forecasts[name],'evaluation':validation[name]['fully_learned']}),flush=True)
    pd.DataFrame(all_weights).to_csv(args.out/'group-weights.csv',index=False)
    pd.DataFrame(all_coefficients).to_csv(args.out/'input-coefficients.csv',index=False)
    write_json(args.out/'validation.json',validation)
    final={'experiment':'NIFTY 5/21-session learned forecasts, strict two-year history',
        'issued_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'forecast_date':TARGET,
        'reference_date':bars['nifty_spot'].index[-1],'reference_close':float(day_labels.reference_close.iloc[-1]),
        'history_window':{'inclusive_start':START,'exclusive_end':TARGET},
        'forecasts':forecasts,'input_manifests':previous['input_manifests'],
        'calendar_path':str(calendar_path),'calendar_sha256':digest(calendar_path),
        'comparison_daily_forecast_path':str(previous_path),'comparison_daily_forecast_sha256':previous_hash,
        'source_code_hashes':{p.name:digest(p) for p in [Path(__file__),Path(__file__).with_name('HORIZON_PROTOCOL.md'),
            Path(__file__).with_name('two_year.py'),Path(__file__).with_name('adaptive.py'),Path(__file__).with_name('engine.py')]},
        'limits':['Horizon labels overlap and are not independent observations',
            'Only matured full-horizon returns can fit models, weights, calibration or magnitude distributions',
            'Two-year history leaves few fully learned monthly evaluation periods',
            'Move-size distributions reweight historical conditional sizes; they are not guaranteed price ranges',
            'Conservative global daily lag, reconstructed institutional publication and provisional Monday quote as previously disclosed']}
    write_json(args.out/'forecast.json',final)
    write_json(args.out/'artifact-manifest.json',{'files':{p.name:digest(p) for p in sorted(args.out.glob('*')) if p.is_file()}})
    if digest(previous_path)!=previous_hash:raise AssertionError('Previous daily forecast changed')


if __name__=='__main__':main()
