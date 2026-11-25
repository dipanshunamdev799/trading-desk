"""Exact named V5 and V4 forecast reconstructions before V6 modifications."""
import joblib
from .common import *
from research.nifty_forecast_v5.data import load as sources
from research.nifty_forecast_v5.expansion import variant
from research.nifty_forecast_v5.models import fit,mean_prediction,laws
from research.nifty_forecast_v3.experiment import available,inner_split
def frames():
    x,price,labels=load();data,_=sources();liquid=pd.read_csv(V5/'liquidity-features.csv',index_col=0)
    out={n:variant(n,x,data) for n in ['I03_nosize','I01_legacy','I02_newindices']}
    out['I00']=x;out['L01']=pd.concat([x,liquid.add_prefix('p_liq_')],axis=1);out['L02']=out['L01']
    return x,price,labels,data,out
def run():
    x,price,labels,data,xx=frames();allp=pd.read_csv(V5/'all-predictions.csv');outer=allp[allp.split=='outer_exposed'];checks=[]
    for h in [5,21]:
        for name in ['I03_nosize','I00','I01_legacy','I02_newindices','L01','L02']:
            g=outer[(outer.horizon==h)&(outer.model==name)]
            for fold,f in g.groupby('fold'):
                a=joblib.load(V5/'models'/f'h{h}-{fold}-{name}.joblib');pred=laws(a['model'],xx[name].loc[f.origin],{},a['residual'])
                error={}
                for col,fn in [('p',lambda d:d.stats()['p_up']),('predicted_mean',lambda d:d.stats()['mean_return']),('predicted_median',lambda d:d.stats()['median_return'])]:
                    values=np.array([fn(d) for d in pred]);np.testing.assert_allclose(values,f[col],atol=1e-12,rtol=1e-12);error[col]=float(np.max(abs(values-f[col])))
                checks.append({'horizon':h,'fold':fold,'model':name,'errors':error})
    # Rebuild V4's coherent laws rather than only reciting saved metrics.
    from research.nifty_forecast_v4.distributions import prepare,forecast
    from research.nifty_forecast_v3.models import predict as predict_old
    oldx=pd.read_csv(V3/'features.csv',index_col=0);oldlabels={h:pd.read_csv(V3/f'labels-{h}.csv',index_col=0) for h in [5,21]};p4=pd.read_csv(V4/'distribution-predictions.csv')
    p3=pd.read_csv(V3/'predictions.csv')
    for h in [5,21]:
        g=p4[(p4.horizon==h)&(p4.model=='D00_empirical')&(p4.split=='outer_exposed')]
        for fold,f in g.groupby('fold'):
            ix=available(oldlabels[h],f.origin.min());ii,vv=inner_split(oldlabels[h],ix);context=prepare(oldx,oldlabels[h],ix,ii,vv)
            errors={n:[] for n in ['D02_student_shrunk','D03_residual_shrunk']}
            for row in f.itertuples():
                ds=forecast(context,oldx.loc[row.origin],h)
                for name in errors:
                    expected=p4[(p4.horizon==h)&(p4.model==name)&(p4.origin==row.origin)].iloc[0];s=ds[name].stats();errors[name].append(abs(s['p_up']-expected.p));np.testing.assert_allclose([s['p_up'],s['mean_return'],s['median_return']],[expected.p,expected.predicted_mean,expected.predicted_median],atol=1e-12,rtol=1e-12)
            for name,d in errors.items():checks.append({'horizon':h,'fold':fold,'model':'V4_'+name,'max_probability_difference':float(max(d))})
            a=joblib.load(V3/'models'/f'h{h}-{fold}-M05_lgbm.joblib');pp=predict_old(a['model'],oldx.loc[f.origin],a['residuals']);expected=p3[(p3.horizon==h)&(p3.model=='M05_lgbm')&(p3.fold==fold)].set_index('origin').reindex(f.origin)
            np.testing.assert_allclose([d['p'] for d in pp],expected.p,atol=1e-12,rtol=1e-12);checks.append({'horizon':h,'fold':fold,'model':'V4_M05_lgbm','max_probability_difference':float(np.max(abs(np.array([d['p'] for d in pp])-expected.p.to_numpy())))})
    for name in ['I03_nosize','L01']:
        cutoff='2026-06-30';ix=available(labels[5],cutoff);ii,vv=inner_split(labels[5],ix);ctx={'cutoff':cutoff,'labels':labels};base='I00';inner=fit(base,xx[name].loc[ii],labels[5].loc[ii,'return'].to_numpy(),5,ctx)
        res=labels[5].loc[vv,'return'].to_numpy()-mean_prediction(inner,xx[name].loc[vv],ctx);model=fit(base,xx[name].loc[ix],labels[5].loc[ix,'return'].to_numpy(),5,ctx)
        g=outer[(outer.horizon==5)&(outer.fold=='2026-07')&(outer.model==name)];p=laws(model,xx[name].loc[g.origin],ctx,res);np.testing.assert_allclose([d.stats()['p_up'] for d in p],g.p,atol=1e-12,rtol=1e-12)
    save('reproduction.json',{'completed_at':now(),'passed':True,'fold_vectors':checks,'independent_refits':['July weekly I03_nosize','July weekly L01'],'scope':'No pre2025 state; all historical dates exposed'})
    save('reproduced-metrics.json',[r for r in read('metrics.json',V5) if r['model'] in ['I03_nosize','I00','I01_legacy','I02_newindices','L01','L02']])
    print('Exactly reproduced',len(checks),'named model/fold vectors and2 independent refits',flush=True)
if __name__=='__main__':run()
