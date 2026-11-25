"""Sparse global→sector/magnitude tests and honest intermediate forecasts."""
import joblib
from .common import *
from .engine import fit,means
from research.nifty_forecast_v5.data import load as sources
from research.nifty_forecast_v3.experiment import available
TARGETS={
 'IT':(['p_ret5','p_ret21','i_nifty_it_rel5','i_nifty_it_rel21','p_rv21'],['g_IXIX_ret1','g_IXIX_ret5']),
 'ENERGY':(['p_ret5','p_ret21','i_nifty_energy_rel5','i_nifty_energy_rel21','p_rv21'],['g_BZUSD_ret5','g_USDINR_ret5','x_oil_fx']),
 'BANKREL':(['p_ret5','p_ret21','i_bank_nifty_rel5','i_bank_nifty_rel21','p_rv21'],['x_global_mean','x_global_dispersion']),
 'MAGNITUDE':(['p_rv21','p_vix','p_ret5'],['x_global_vol','x_global_dispersion'])}
def run():
    if (OUT/'mediator-features.csv').exists():raise FileExistsError('Mediation cache exists')
    save('mediation-plan.json',{'registered_at':now(),'targets':TARGETS,'kind':'Ridge alpha100; no search; sparse global increments over own-state controls',
        'clock':'Existing exact causal global-source joins; US Tech100 provider proxy is not relabeled Nasdaq Composite',
        'intermediate_uses':'Honest prior forecasts only; no in-sample fitted outcomes as NIFTY training features','interpretation':'Predictive precedence, not causation'})
    x=pd.read_csv(V5/'features.csv',index_col=0);old=pd.read_csv(V3/'predictions.csv');data,_=sources();records=[];ledger=[];feature=pd.DataFrame(index=x.index)
    for h in [5,21]:
        labels=pd.read_csv(OUT/f'labels-{h}.csv',index_col=0);queries=old[(old.horizon==h)&(old.model=='B00_empirical')]
        for target,(base,glob) in TARGETS.items():
            y=(data['nifty_it' if target=='IT' else 'nifty_energy' if target=='ENERGY' else 'bank_nifty'].close.reindex(x.index).shift(-h)/data['nifty_it' if target=='IT' else 'nifty_energy' if target=='ENERGY' else 'bank_nifty'].close.reindex(x.index)-1) if target!='MAGNITUDE' else labels['return'].abs()
            if target=='BANKREL':y=y-labels['return']
            target_labels=labels.copy();target_labels['return']=y
            for fold,g in queries.groupby('fold'):
                cutoff=g.origin.min();ix=available(target_labels,cutoff);pred={}
                for mode,names in [('base',base),('global',base+glob)]:
                    model=fit({'kind':'ridge','alpha':100},x.loc[ix,names],target_labels,cutoff);values=means(model,x.loc[g.origin,names]);values=np.maximum(values,0) if target=='MAGNITUDE' else values;pred[mode]=values
                    path=OUT/'models'/f'mediator-h{h}-{fold}-{target}-{mode}.joblib';joblib.dump({'model':model,'cutoff':cutoff},path,compress=3)
                    ledger.append({'horizon':h,'fold':fold,'target':target,'mode':mode,'training_n':len(ix),'last_endpoint':str(target_labels.loc[ix,'endpoint'].max()),'cutoff':cutoff,'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
                for j,r in enumerate(g.itertuples()):
                    records.append({'horizon':h,'target':target,'fold':fold,'origin':r.origin,'endpoint':r.endpoint,'split':r.split,'outcome':float(y.loc[r.origin]),'base_prediction':float(pred['base'][j]),'global_prediction':float(pred['global'][j]),'increment':float(pred['global'][j]-pred['base'][j])})
                    # Features keep separate horizons, and never fill dates before first honest forecast.
                    for mode in ['base','global']:feature.loc[r.origin,f'med{h}_{target}_{mode}']=pred[mode][j]
                    feature.loc[r.origin,f'med{h}_{target}_increment']=pred['global'][j]-pred['base'][j]
    for h in [5,21]:
        feature[f'med{h}_weak_breadth_shock']=feature[f'med{h}_BANKREL_increment']*(x.i_participation<=.5)
    feature.to_csv(OUT/'mediator-features.csv');pd.DataFrame(records).to_csv(OUT/'intermediate-predictions.csv',index=False);save('mediation-ledger.json',ledger)
    f=pd.DataFrame(records);rows=[]
    for (h,target),g in f[f.split=='outer_exposed'].groupby(['horizon','target']):
        eb=abs(g.base_prediction-g.outcome);eg=abs(g.global_prediction-g.outcome)
        rows.append({'horizon':int(h),'target':target,'n':len(g),'base_mae':float(eb.mean()),'global_mae':float(eg.mean()),'mae_improvement':float((eb-eg).mean()),'base_rmse':float(np.sqrt(np.mean((g.base_prediction-g.outcome)**2))),'global_rmse':float(np.sqrt(np.mean((g.global_prediction-g.outcome)**2))),'claim':'Exposed intermediate predictive test, not causal transmission'})
    save('intermediate-metrics.json',rows);print('Sparse global/sector intermediate studies complete',len(rows),flush=True)
if __name__=='__main__':run()
