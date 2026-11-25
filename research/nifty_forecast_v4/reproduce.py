"""Recompute V3 metrics and every named candidate's outer predictions."""
import json,joblib
import numpy as np
from .common import *
from research.nifty_forecast_v3.models import predict,train,SPECS
from research.nifty_forecast_v3.experiment import summarize,nonoverlap

def run():
    x,labels,allp=load();outer=allp[allp.split=='outer_exposed'];rows=[];errors=[]
    for h in [5,21]:
        for name in ['M05_lgbm','A00_sector','Z_reversion','Z_neutral','B00_empirical','S_direction','S_distribution']:
            g=outer[(outer.horizon==h)&(outer.model==name)].sort_values('origin')
            rows.append({'horizon':h,'model':name,**summarize(g),'disjoint':summarize(nonoverlap(g))})
            if name.startswith('S_'):continue
            for fold,f in g.groupby('fold'):
                modelname=name if not name.startswith('Z_') else 'B00_empirical'
                artifact=joblib.load(V3/'models'/f'h{h}-{fold}-{modelname}.joblib')
                pp=predict(artifact['model'],x.loc[f.origin],artifact['residuals'])
                if name=='Z_neutral':p=np.full(len(f),.5)
                elif name=='Z_reversion':p=np.where(x.loc[f.origin,'price_ret5']>0,.45,.55)
                else:p=np.array([p['p'] for p in pp])
                delta=float(np.max(abs(p-f.p.to_numpy())));errors.append({'horizon':h,'fold':fold,'model':name,'max_probability_difference':delta})
                np.testing.assert_allclose(p,f.p,atol=1e-12,rtol=1e-12)
    # Independent refits, rather than just loading saved estimators.
    for name in ['M05_lgbm','A00_sector']:
        fold='2026-07';a=joblib.load(V3/'models'/f'h5-{fold}-{name}.joblib')
        fitted=train(SPECS[name],x.loc[a['train_idx']],labels[5].loc[a['train_idx']])
        query=outer[(outer.horizon==5)&(outer.fold==fold)&(outer.model==name)]
        pp=predict(fitted,x.loc[query.origin],a['residuals'])
        np.testing.assert_allclose([p['p'] for p in pp],query.p,atol=1e-12,rtol=1e-12)
    save('v3-reproduced-metrics.json',rows);save('v3-reproduction-checks.json',{'passed':True,'folds':errors,'independent_refits':['h5-2026-07-M05_lgbm','h5-2026-07-A00_sector'],
        'original_feature_significance_min_q':float(__import__('pandas').read_csv(V3/'development-feature-information.csv').bh_q.min()),
        'v3_intervals':read('simultaneous-uncertainty.json',V3)})
    print('Reproduced metrics and',len(errors),'candidate/fold probability vectors; two independent refits',flush=True)
if __name__=='__main__':run()
