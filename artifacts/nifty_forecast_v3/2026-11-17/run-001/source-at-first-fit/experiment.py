"""Purged nested chronological experiment registry and multi-target scores."""
from __future__ import annotations
import os
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,time,warnings
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from .audit import OUT,ROOT,save,sha
from .models import SPECS,SEED,train,predict

BUCKETS=np.array([-.05,-.02,-.005,.005,.02,.05])
TARGET_METRICS={'direction':'brier','return':'mae','distribution':'crps','volatility':'qlike','tail':'tail02_brier'}

def available(labels,day):
    return labels.index[(labels.endpoint.notna())&(labels.endpoint<day)&labels['return'].notna()]

def validate_availability(decision,availability):
    if any(pd.Timestamp(stamp)>pd.Timestamp(decision) for stamp in availability):
        raise ValueError('LOOKAHEAD_SENTINEL: feature not yet available at decision')

def inner_split(labels,train_idx):
    validation=train_idx[-42:];first=validation[0]
    fitting=train_idx[(train_idx<first)&(labels.loc[train_idx,'endpoint'].to_numpy()<first)]
    return fitting,validation

def score_prediction(pred,row):
    samples=np.sort(np.asarray(pred['samples']));n=len(samples);y=float(row['return']);up=int(y>0);p=pred['p']
    q=np.quantile(samples,[.1,.25,.5,.75,.9]);b=np.bincount(np.digitize(samples,BUCKETS),minlength=7)/n
    one=np.zeros(7);one[int(np.digitize(y,BUCKETS))]=1
    crps=float(np.mean(abs(samples-y))-np.dot(2*np.arange(1,n+1)-n-1,samples)/(n*n))
    ratio=max(float(row.volatility)**2,1e-10)/max(pred['vol']**2,1e-10)
    return {'p':p,'outcome':up,'realized_return':y,'predicted_mean':pred['mean'],'predicted_median':float(q[2]),
        'brier':float((p-up)**2),'log_loss':float(-up*np.log(p)-(1-up)*np.log(1-p)),
        'mae':abs(pred['mean']-y),'squared_error':(pred['mean']-y)**2,'median_mae':abs(q[2]-y),
        'magnitude_mae':abs(float(np.mean(abs(samples)))-abs(y)),
        'crps':crps,'bucket_brier':float(np.sum((b-one)**2)),
        'pinball':float(np.mean(np.maximum(np.array([.1,.25,.5,.75,.9])*(y-q),(np.array([.1,.25,.5,.75,.9])-1)*(y-q)))),
        'coverage50':int(q[1]<=y<=q[3]),'coverage80':int(q[0]<=y<=q[4]),
        'width50':float(q[3]-q[1]),'width80':float(q[4]-q[0]),
        'q10':float(q[0]),'q25':float(q[1]),'q50':float(q[2]),'q75':float(q[3]),'q90':float(q[4]),
        'predicted_vol':pred['vol'],'realized_vol':float(row.volatility),'vol_mae':abs(pred['vol']-row.volatility),
        'qlike':float(ratio-np.log(ratio)-1),
        'tail02_p':pred['tail02'],'tail02_y':int(row.path_loss<-.02),
        'tail02_brier':float((pred['tail02']-int(row.path_loss<-.02))**2),
        'tail05_p':pred['tail05'],'tail05_brier':float((pred['tail05']-int(row.path_loss<-.05))**2),
        'dist_up_probability':float(np.mean(samples>0)),'quantile_crossings':pred['crossings'],
        **{f'bucket{k}_p':float(v) for k,v in enumerate(b)}}

def fold_prediction(spec,x,labels,train_idx,query_idx,cache_dir):
    fit_idx,val_idx=inner_split(labels,train_idx)
    if len(fit_idx)<80:raise ValueError('Insufficient purged inner training')
    inner=train(spec,x.loc[fit_idx],labels.loc[fit_idx])
    validation=predict(inner,x.loc[val_idx])
    inner_scores=[score_prediction(p,labels.loc[i]) for p,i in zip(validation,val_idx)]
    residuals=np.array([labels.loc[i,'return']-p['mean'] for p,i in zip(validation,val_idx)])
    model=train(spec,x.loc[train_idx],labels.loc[train_idx])
    forecast=predict(model,x.loc[query_idx],residuals)
    cache_dir.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump({'model':model,'residuals':residuals,'train_idx':list(train_idx),'inner_train_idx':list(fit_idx),
        'inner_validation_idx':list(val_idx),'preprocess_available_at':query_idx[0]},cache_dir,compress=3)
    pinner=np.array([p['p'] for p in validation]);threshold=max(.05,float(np.quantile(abs(pinner-.5),.8)))
    return forecast,inner_scores,{'train_n':len(train_idx),'first_training_origin':train_idx[0],
        'last_training_endpoint':labels.loc[train_idx,'endpoint'].max(),
        'inner_train_n':len(fit_idx),'inner_validation_n':len(val_idx),
        'last_inner_train_endpoint':labels.loc[fit_idx,'endpoint'].max(),'first_inner_validation_origin':val_idx[0],
        'confidence_threshold':threshold,'model_path':str(cache_dir),'model_sha256':sha(cache_dir)}

def summarize(frame):
    if frame.empty:return {'n':0}
    y=frame.outcome.to_numpy();p=frame.p.to_numpy();pred=p>=.5
    recalls=[float(np.mean(pred[y==value]==value)) for value in [0,1] if (y==value).any()]
    result={'n':len(frame),'accuracy':float(np.mean(pred==y)),
        'balanced_accuracy':float(np.mean(recalls)) if len(recalls)==2 else None,
        'rmse':float(np.sqrt(frame.squared_error.mean()))}
    for c in ['brier','log_loss','mae','median_mae','magnitude_mae','crps','pinball','bucket_brier','coverage50','coverage80',
              'width50','width80','qlike','vol_mae','tail02_brier','tail05_brier']:
        result[c]=float(frame[c].mean())
    bins=[]
    for lo,hi in zip([0,.35,.45,.55,.65],[.35,.45,.55,.65,1.00001]):
        mask=(p>=lo)&(p<hi)
        if mask.any():bins.append({'lo':lo,'hi':min(hi,1),'n':int(mask.sum()),'predicted':float(p[mask].mean()),'observed':float(y[mask].mean())})
    result['calibration_bins']=bins
    result['ece']=float(sum(b['n']*abs(b['predicted']-b['observed']) for b in bins)/len(frame))
    result['always_up_accuracy']=float(y.mean());result['always_down_accuracy']=float(1-y.mean())
    return result

def nonoverlap(frame):
    keep=[];last=''
    for i,r in frame.sort_values('origin').iterrows():
        if r.origin>=last:keep.append(i);last=r.endpoint
    return frame.loc[keep]

def effective_n(values,h):
    a=np.asarray(values,float);n=len(a)
    if n<5 or np.std(a)<1e-10:return None
    total=0
    for lag in range(1,min(2*h,n//4)+1):
        corr=np.corrcoef(a[:-lag],a[lag:])[0,1]
        if not np.isfinite(corr) or corr<=0:break
        total+=corr
    return float(np.clip(n/(1+2*total),1,n))

def paired_ci(values,h):
    a=np.asarray(values,float);n=len(a)
    if n<8*h:return None
    rng=np.random.default_rng(SEED);block=2*h
    starts=rng.integers(0,n-block+1,(2000,int(np.ceil(n/block))))
    ix=(starts[:,:,None]+np.arange(block)).reshape(2000,-1)[:,:n]
    return np.quantile(a[ix].mean(axis=1),[.025,.975]).tolist()

def run():
    x=pd.read_csv(OUT/'features.csv',index_col=0);x.index=x.index.astype(str)
    (OUT/'models').mkdir(exist_ok=True)
    registry_path=OUT/'registry-config.json'
    if registry_path.exists():raise FileExistsError('Use a separately versioned workspace; registry exists')
    save('registry-config.json',{'frozen_before_evaluation':True,'seed':SEED,'configuration_count':len(SPECS),
        'specifications':SPECS,'outer_start':'2026-07-01','history_start':'2025-01-01',
        'design_sha256':sha(Path(__file__).with_name('DESIGN.md')),
        'probability_clip':[.02,.98],'tail_clip':[.001,.999],
        'source_code_hashes':{p.name:sha(p) for p in Path(__file__).parent.glob('*.py')},
        'dataset_manifest_sha256':sha(OUT/'dataset-manifest.json')})
    records=[];ledger=[];live={};all_inner=[]
    for h in [5,21]:
        labels=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0,dtype={'origin':str,'endpoint':str})
        next_days=list(x.index[1:])+['2026-11-17'];labels['forecast_day']=next_days
        eligible=[]
        for day in x.index[:-1]:
            matured=available(labels,day)
            if len(matured)>=126 and len(inner_split(labels,matured)[0])>=80:eligible.append(day)
        bymonth={}
        for day in eligible:bymonth.setdefault(labels.loc[day,'forecast_day'][:7],[]).append(day)
        bymonth['LIVE_ASOF']=[x.index[-1]]
        for month,query in bymonth.items():
            began=time.monotonic();first=query[0];train_idx=available(labels,first)
            fold_results={};inner_results={};metadata={}
            for name,spec in SPECS.items():
                try:
                    forecasts,inner_scores,meta=fold_prediction(spec,x,labels,train_idx,query,OUT/'models'/f'h{h}-{month}-{name}.joblib')
                    fold_results[name]=forecasts;inner_results[name]=inner_scores;metadata[name]=meta
                    ledger.append({'experiment_id':f'V3-H{h}-{month}-{name}','horizon':h,'fold':month,
                        'hypothesis':name,'features':spec['features'],'algorithm':spec['kind'],'parameters':spec['parameters'],
                        'research_only':spec['research_only'],'configurations_total':len(SPECS),
                        'origin_first':query[0],'origin_last':query[-1],**meta,'status':'ok'})
                except Exception as exc:
                    ledger.append({'experiment_id':f'V3-H{h}-{month}-{name}','horizon':h,'fold':month,'model':name,'status':'failed','error':str(exc)[:400]})
            # Deterministic requested controls add no fitted configurations.
            if 'B00_empirical' not in fold_results:raise RuntimeError('Empirical control failed; inspect ledger before proceeding')
            val_idx=inner_split(labels,train_idx)[1]
            control_p={
                'Z_neutral':lambda frame:np.full(len(frame),.5),
                'Z_momentum':lambda frame:np.where(frame.price_ret21>0,.55,.45),
                'Z_reversion':lambda frame:np.where(frame.price_ret5>0,.45,.55),
                'Z_always_up':lambda frame:np.full(len(frame),.98),
                'Z_always_down':lambda frame:np.full(len(frame),.02)}
            for control,fn in control_p.items():
                fold_results[control]=[{**p,'p':float(v)} for p,v in zip(fold_results['B00_empirical'],fn(x.loc[query]))]
                controls=[]
                for r,p in zip(inner_results['B00_empirical'],fn(x.loc[val_idx])):
                    up=r['outcome'];controls.append({**r,'p':float(p),'brier':float((p-up)**2),
                        'log_loss':float(-up*np.log(p)-(1-up)*np.log(1-p))})
                inner_results[control]=controls;metadata[control]=metadata['B00_empirical']
            valid=[name for name in fold_results if name not in SPECS or not SPECS[name]['research_only']]
            choices={target:min(valid,key=lambda name:np.mean([r[metric] for r in inner_results[name]])) for target,metric in TARGET_METRICS.items()}
            baseline_choices={target:min([name for name in valid if name.startswith(('B','Z'))],key=lambda name:np.mean([r[metric] for r in inner_results[name]])) for target,metric in TARGET_METRICS.items()}
            for name,scores in inner_results.items():
                all_inner.append({'horizon':h,'fold':month,'model':name,'inner_metrics':{metric:float(np.mean([r[metric] for r in scores])) for metric in TARGET_METRICS.values()}})
            if month=='LIVE_ASOF':
                live[str(h)]={'origin':first,'forecast_day':labels.loc[first,'forecast_day'],'train_n':len(train_idx),
                    'selectors':choices,'baseline_selectors':baseline_choices,
                    'forecasts':{name:[{k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in f.items()} for f in forecasts] for name,forecasts in fold_results.items()},
                    'metadata':metadata,'inner_scores':{name:{metric:float(np.mean([r[metric] for r in scores])) for metric in TARGET_METRICS.values()} for name,scores in inner_results.items()}}
            else:
                # Each target's selector uses only the purged inner history.
                expanded={**fold_results,**{'S_'+target:fold_results[name] for target,name in choices.items()},
                    **{'C_'+target:fold_results[name] for target,name in baseline_choices.items()}}
                for j,day in enumerate(query):
                    if not np.isfinite(labels.loc[day,'return']):continue
                    regime='high_vol' if x.loc[day,'price_rv21']>x.loc[train_idx,'price_rv21'].median() else 'low_vol'
                    trend='trend' if abs(x.loc[day,'price_ret21'])/max(.001,x.loc[day,'price_rv21'])/np.sqrt(21)>1 else 'sideways'
                    for name,forecasts in expanded.items():
                        source=choices[name[2:]] if name.startswith('S_') else baseline_choices[name[2:]] if name.startswith('C_') else name
                        p=forecasts[j];score=score_prediction(p,labels.loc[day])
                        records.append({'horizon':h,'fold':month,'model':name,'selected_model':source,
                            'origin':day,'forecast_day':labels.loc[day,'forecast_day'],'endpoint':labels.loc[day,'endpoint'],
                            'split':'outer_exposed' if labels.loc[day,'forecast_day']>='2026-07-01' else 'development_exposed',
                            'regime':regime,'trend_regime':trend,'breadth_regime':'broad' if x.loc[day,'sector_participation']>=.5 else 'narrow',
                            'expiry_regime':'near' if x.loc[day,'fo_option_dte']<=2 else 'far',
                            'global_riskoff':bool(x.loc[day,'global_sp500_ret1']<x.loc[train_idx,'global_sp500_ret1'].quantile(.1)),
                            'large_prior_move':bool(abs(x.loc[day,'price_ret1'])>x.loc[train_idx,'price_ret1'].abs().quantile(.9)),
                            'selected_confident':bool(abs(p['p']-.5)>=metadata[source]['confidence_threshold']),**score})
            pd.DataFrame(records).to_csv(OUT/'predictions.csv',index=False)
            save('experiment-ledger.json',ledger);save('inner-validation.json',all_inner);save('current-model-record.json',live)
            print(f'h={h} fold={month}: {len(query)} origins; {len(fold_results)}/{len(SPECS)} configurations; {time.monotonic()-began:.1f}s',flush=True)
    frame=pd.DataFrame(records);results=[]
    for (h,model,split),g in frame.groupby(['horizon','model','split']):
        summary=summarize(g);summary.update({'horizon':int(h),'model':model,'split':split,
            'nonoverlapping_n':len(nonoverlap(g)),'outcome_autocorrelation_ess':effective_n(g.outcome,int(h)),
            'origin_first':g.forecast_day.min(),'origin_last':g.forecast_day.max(),
            'research_only':bool(model in SPECS and SPECS[model]['research_only'])})
        results.append(summary)
    save('metrics.json',results)
    print('Finished controlled V3 batch',len(ledger),'fits; predictions',len(frame),flush=True)

if __name__=='__main__':run()
