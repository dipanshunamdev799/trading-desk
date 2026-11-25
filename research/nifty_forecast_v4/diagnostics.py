"""Bounded exposed-history calibration and weekly tree stress diagnostics."""
import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import expit,logit
from .common import *
from research.nifty_forecast_v3.models import train,predict,SPECS
from research.nifty_forecast_v3.experiment import summarize,nonoverlap,paired_ci

def direction_metrics(frame):
    p=frame.p.to_numpy();y=frame.outcome.to_numpy();pc=np.clip(p,1e-6,1-1e-6);pred=p>=.5
    bins=[]
    for lo,hi in [(0,.35),(.35,.45),(.45,.55),(.55,.65),(.65,1.00001)]:
        m=(p>=lo)&(p<hi)
        if m.any():bins.append({'lo':lo,'hi':min(hi,1),'n':int(m.sum()),'predicted':float(p[m].mean()),'observed':float(y[m].mean())})
    return {'n':len(y),'brier':float(np.mean((p-y)**2)),'log_loss':float(np.mean(-y*np.log(pc)-(1-y)*np.log(1-pc))),
        'accuracy':float(np.mean(pred==y)),'balanced_accuracy':float(np.mean([np.mean(pred[y==v]==v) for v in [0,1] if (y==v).any()])),
        'bins':bins,'up_frequency':float(y.mean())}

def run():
    if (OUT/'weekly-stress-predictions.csv').exists():raise FileExistsError('Study already exists')
    registry=read('registry.json');x,labels,frame=load();outer=frame[(frame.horizon==5)&(frame.split=='outer_exposed')]
    baseline=outer.pivot(index='origin',columns='model',values='brier').sort_index()
    audit={'frozen_metrics':{},'slices':[],'phase_nonoverlap':[],'leave_one_month_out':[],'exceptional_origin_sensitivity':[],'family_gains':[]}
    for name in ['M05_lgbm','A00_sector','Z_reversion','Z_neutral','B00_empirical']:
        data=outer[outer.model==name].sort_values('origin');audit['frozen_metrics'][name]=direction_metrics(data)
        for var in ['fold','regime','trend_regime','breadth_regime','expiry_regime','global_riskoff','large_prior_move']:
            for val,g in data.groupby(var):audit['slices'].append({'model':name,'variable':var,'value':str(val),**direction_metrics(g)})
        for offset in range(5):audit['phase_nonoverlap'].append({'model':name,'phase':offset,**direction_metrics(nonoverlap(data.iloc[offset:]))})
    delta=baseline.Z_reversion-baseline.M05_lgbm
    for month in sorted(outer.fold.unique()):
        days=outer[(outer.fold!=month)&(outer.model=='M05_lgbm')].origin
        audit['leave_one_month_out'].append({'removed_month':month,'n':len(days),'brier_improvement_vs_reversion':float(delta.reindex(days).mean())})
    for k in [1,3,5,10]:audit['exceptional_origin_sensitivity'].append({'remove_best_origins':k,'remaining_mean_improvement':float(delta.sort_values().iloc[:-k].mean()),'note':'Overlapping origins, not independent periods'})
    calibrations=[];stresses=[];calfit=[]
    for fold,g0 in outer[outer.model=='M05_lgbm'].groupby('fold'):
        daylist=list(g0.origin)
        for name in ['M05_lgbm','A00_sector']:
            artifact=joblib.load(V3/'models'/f'h5-{fold}-{name}.joblib');ix=artifact['train_idx'];fit=artifact['inner_train_idx'];val=artifact['inner_validation_idx']
            inner=train(SPECS[name],x.loc[fit],labels[5].loc[fit]);pv=np.array([p['p'] for p in predict(inner,x.loc[val])]);yv=labels[5].loc[val,'return'].gt(0).to_numpy()
            objective=lambda b:float(np.sum(np.logaddexp(0,logit(pv)+b)-yv*(logit(pv)+b))+10*b*b/2)
            offset=float(minimize_scalar(objective,bounds=(-1,1),method='bounded').x)
            base=float(labels[5].loc[ix[-252:],'return'].gt(0).mean());data=outer[(outer.model==name)&(outer.fold==fold)]
            for r in data.itertuples():
                for method,p in [('RAW',r.p),('SHRINK50',.5*r.p+.5*base),('OFFSET',float(expit(logit(r.p)+offset)))]:calibrations.append({'fold':fold,'origin':r.origin,'endpoint':r.endpoint,'model':name,'method':method,'p':p,'outcome':r.outcome,'raw_p':r.p,'base_rate':base})
            calfit.append({'fold':fold,'model':name,'offset':offset,'inner_n':len(val),'inner_nonoverlap_n':len(nonoverlap(pd.DataFrame({'origin':val,'endpoint':labels[5].loc[val,'endpoint'].to_numpy()}))),'inner_up_frequency':float(yv.mean()),'outer_up_frequency':float(data.outcome.mean()),'base_rate':base})
        original=joblib.load(V3/'models'/f'h5-{fold}-M05_lgbm.joblib');ix=original['train_idx']
        model=original['model'];cols=model['pre'].columns;gains=model['direction_model'].feature_importance('gain')
        for fam in sorted({c.split('_')[0] for c in cols}):audit['family_gains'].append({'fold':fold,'family':fam,'gain':float(sum(v for c,v in zip(cols,gains) if c.startswith(fam+'_'))),'note':'Training gain, not causal or validated incremental importance'})
        for variant in registry['lgbm_stress_variants']:
            xx=x if variant=='rolling126' else x.drop(columns=[c for c in x if c.startswith(variant[5:]+'_')]);training=ix[-126:] if variant=='rolling126' else ix
            fitted=train(SPECS['M05_lgbm'],xx.loc[training],labels[5].loc[training]);pred=predict(fitted,xx.loc[daylist])
            for r,p in zip(g0.itertuples(),pred):stresses.append({'fold':fold,'origin':r.origin,'endpoint':r.endpoint,'model':variant,'p':p['p'],'outcome':r.outcome})
        print('LightGBM/calibration diagnostics',fold,flush=True)
    cal=pd.DataFrame(calibrations);stress=pd.DataFrame(stresses);cal.to_csv(OUT/'calibration-predictions.csv',index=False);stress.to_csv(OUT/'weekly-stress-predictions.csv',index=False)
    audit['stress_metrics']=[{'variant':name,**direction_metrics(g)} for name,g in stress.groupby('model')]
    calmetrics=[]
    for (name,method),g in cal.groupby(['model','method']):
        flip=(g.p>=.5)!=(g.raw_p>=.5)
        calmetrics.append({'model':name,'method':method,**direction_metrics(g),'threshold_flips':int(flip.sum()),'correct_to_wrong':int((flip&((g.raw_p>=.5)==g.outcome)).sum()),'wrong_to_correct':int((flip&((g.p>=.5)==g.outcome)).sum()),'activation':'DISABLED; diagnostic only'})
    save('weekly-lightgbm-audit.json',audit);save('calibration-metrics.json',calmetrics);save('calibration-fit-ledger.json',calfit)
    print('Saved bounded diagnostic results',flush=True)
if __name__=='__main__':run()
