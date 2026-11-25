"""Registered attribution for the newly promising monthly weekly-state model."""
import joblib
from .common import *
from .engine import fit,means,predict
from .experiments import SMALL
from research.nifty_forecast_v3.experiment import available,inner_split
def run():
    if (OUT/'monthly-followup-plan.json').exists():raise FileExistsError('Follow-up exists')
    save('monthly-followup-plan.json',{'registered_at':now(),'motivation':'Initial M_WEEKSTATE exposed monthly Brier≈.17835/CRPS≈.02482. Test whether gain is feature information, shorter training window, levels or slopes; no tuning on final scores.',
        'models':{'M2_WINDOW_SMALL':'Only same four native price/risk inputs on exact weekly-state-eligible dates','M2_WINDOW_NATIVE':'Full57-native block on same dates','M2_LEVELS':'Price4+weekly-state levels only','M2_SLOPES':'Price4+weekly-state5-session slopes only','M2_STATE_LAG1':'Price4+weekly states delayed one extra session','M2_HUBER_WINDOW':'Robust native model on same eligible dates'},
        'negative_control':'Common21-session circular block shift of training state columns, separately inside inner/full past partitions; diagnostic only, not eligible to win',
        'sample_limit':'All76origins are exposed and overlap into approximately four disjoint months'})
    x=pd.read_csv(OUT/'native-reference.csv',index_col=0);s=pd.read_csv(OUT/'state-features.csv',index_col=0);labels=pd.read_csv(OUT/'labels-21.csv',index_col=0);p=pd.read_csv(V5/'all-predictions.csv');query=p[(p.horizon==21)&(p.model=='I03_nosize')&(p.split=='outer_exposed')]
    frames={'M2_WINDOW_SMALL':x[SMALL[:4]],'M2_WINDOW_NATIVE':x,
        'M2_LEVELS':pd.concat([x[SMALL[:4]],s[[c for c in s if not c.endswith('_slope5')]]],axis=1),
        'M2_SLOPES':pd.concat([x[SMALL[:4]],s[[c for c in s if c.endswith('_slope5')]]],axis=1),
        'M2_STATE_LAG1':pd.concat([x[SMALL[:4]],s.shift(1)],axis=1),'M2_HUBER_WINDOW':x}
    rows=[];ledger=[];null=[]
    for fold,g in query.groupby('fold'):
        cutoff=g.origin.min();ix=available(labels,cutoff);ii,vv=inner_split(labels,ix);present=s.w_I03_nosize_p.notna();ix=ix[present.loc[ix].to_numpy()];ii=ii[present.loc[ii].to_numpy()]
        for name,xx in frames.items():
            spec={'kind':'huber' if name=='M2_HUBER_WINDOW' else 'ridge'}
            inner=fit(spec,xx.loc[ii],labels,vv[0]);res=labels.loc[vv,'return'].to_numpy()-means(inner,xx.loc[vv]);model=fit(spec,xx.loc[ix],labels,cutoff);ds=predict(model,xx.loc[g.origin],res)
            path=OUT/'models'/f'h21-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'cutoff':cutoff,'inner_fit':list(ii),'inner_validation':list(vv)},path,compress=3);ledger.append({'horizon':21,'fold':fold,'model':name,'status':'ok','training_n':len(ix),'inner_n':len(ii),'last_endpoint':str(labels.loc[ix,'endpoint'].max()),'cutoff':cutoff,'inner_last_endpoint':str(labels.loc[ii,'endpoint'].max()),'inner_first':vv[0],'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
            for r,d in zip(g.itertuples(),ds):rows.append({'horizon':21,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,'regime':r.regime,'trend':r.trend,'global_risk':r.global_risk,**d.score(r.realized_return)})
        xx=pd.concat([x[SMALL[:4]],s],axis=1);statecols=list(s);xi=xx.loc[ii].copy();xf=xx.loc[ix].copy();xi[statecols]=np.roll(xi[statecols].to_numpy(),21,axis=0);xf[statecols]=np.roll(xf[statecols].to_numpy(),21,axis=0)
        inner=fit({'kind':'ridge'},xi,labels,vv[0]);res=labels.loc[vv,'return'].to_numpy()-means(inner,xx.loc[vv]);model=fit({'kind':'ridge'},xf,labels,cutoff);ds=predict(model,xx.loc[g.origin],res)
        for r,d in zip(g.itertuples(),ds):null.append({'horizon':21,'fold':fold,'origin':r.origin,'model':'STATE_BLOCK_RANDOMIZED_DIAGNOSTIC',**d.score(r.realized_return)})
        print('Monthly-state attribution',fold,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'monthly-followup-predictions.csv',index=False);pd.DataFrame(null).to_csv(OUT/'monthly-state-null.csv',index=False);save('monthly-followup-ledger.json',ledger)
if __name__=='__main__':run()
