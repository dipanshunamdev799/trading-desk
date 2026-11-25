"""Learn coherent combination weights and sign adjustments on matured prior forecasts."""
from scipy.optimize import minimize_scalar
from .common import *
from .models import fit, location, laws, Distribution, mix, cross_abs
from .experiments import all_frames, score_row
from research.nifty_forecast_v3.experiment import available, inner_split
from research.nifty_forecast_v6.common import V3


def weight(history):
    terms=[]
    for _,a,b,y in history:
        terms.append((a.w@abs(a.a-y),b.w@abs(b.a-y),cross_abs(a,a),cross_abs(b,b),cross_abs(a,b),a.stats()['p_up'],b.stats()['p_up'],y>0))
    ea,eb,aa,bb,ab,pa,pb,y=np.array(terms).T
    def objective(w):
        crps=w*ea+(1-w)*eb-.5*(w*w*aa+(1-w)**2*bb+2*w*(1-w)*ab)
        brier=(w*pa+(1-w)*pb-y)**2
        return float(np.mean(crps/.02+brier/.25)+.25*(w-.5)**2)
    return float(minimize_scalar(objective,bounds=(.1,.9),method='bounded').x)


def train_tilt(history):
    pa=np.array([a.stats()['p_up'] for _,a,b,y in history]);actual=np.array([y>0 for _,a,b,y in history])
    def objective(shift):
        p=pa*np.exp(shift)/(1-pa+pa*np.exp(shift))
        return float(np.mean((p-actual)**2)+.15*shift**2)
    return float(minimize_scalar(objective,bounds=(-.5,.5),method='bounded').x)


def run():
    specs={'J_EQUAL':{'parent':'C_NO_DEF','hypothesis':'Equal complete-law mixture of V6 winner representations'},
           'J_JOINT':{'parent':'J_EQUAL','hypothesis':'Regularized joint fit of training CRPS and Brier, only matured reconstructed forecasts'},
           'J_TILT':{'parent':'C_NO_DEF','hypothesis':'Train-only shrinkage on sign log odds by reweighting positive return atoms'}}
    save('integration-registry.json',{'registered_at':now(),'configurations':specs,'training_origin_window':42,
          'penalties':'w in [.1,.9], CRPS/.02 + Brier/.25 + .25(w-.5)^2. Tilt in [-.5,.5], Brier+.15*tilt^2.'})
    frames,_=all_frames();price=matrix('price.csv');old=pd.read_csv(V3/'predictions.csv')
    old=old[(old.model=='B00_empirical')&old.split.isin(['development_exposed','outer_exposed'])]
    context=pd.read_csv(V5/'all-predictions.csv');context=context[context.model=='I03_nosize'][['horizon','origin','regime','trend','global_risk']]
    old=old.drop(columns=['regime','trend','global_risk'],errors='ignore').merge(context,on=['horizon','origin'],how='left',validate='one_to_one')
    predictions=[];ledger=[];cache=[]
    for h in [5,21]:
        labels=matrix(f'labels-{h}.csv');historical=[]
        for fold,q in old[old.horizon==h].groupby('fold'):
            cutoff=q.origin.min();ix=available(labels,cutoff);ii,vv=inner_split(labels,ix)
            candidates=[]
            for frame in ['nodef','noauto_volume']:
                x=frames[frame];inner=fit({},x.loc[ii],labels.loc[ii,'return'].to_numpy());model=fit({},x.loc[ix],labels.loc[ix,'return'].to_numpy())
                res=labels.loc[vv,'return'].to_numpy()-location(inner,x.loc[vv]);candidates.append(laws(model,x.loc[q.origin],res,x.loc[vv,'p_rv21'].to_numpy()))
            past=[p for p in historical if p[0].endpoint<cutoff][-42:];w=weight(past) if len(past)>=20 else .5;tilt=train_tilt(past) if len(past)>=20 else 0.
            ledger.append({'horizon':h,'fold':fold,'cutoff':cutoff,'last_training_endpoint':labels.loc[ix,'endpoint'].max(),
                           'inner_first':vv[0],'inner_last_endpoint':labels.loc[ii,'endpoint'].max(),'weight':w,'tilt':tilt,
                           'history':[{'origin':r.origin,'endpoint':r.endpoint} for r,_,_,_ in past]})
            for r,a,b in zip(q.itertuples(),*candidates):
                y=r.realized_return
                historical.append((r,a,b,y))
                cache.append({'horizon':h,'origin':r.origin,'endpoint':r.endpoint,'fold':fold,'split':r.split,'realized_return':y,
                              'no_defensive_atoms':a.a.tolist(),'no_defensive_weights':a.w.tolist(),'auto_volume_atoms':b.a.tolist(),'auto_volume_weights':b.w.tolist()})
                if r.split!='outer_exposed':continue
                for name,law in [('J_EQUAL',mix(a,b,.5)),('J_JOINT',mix(a,b,w)),('J_TILT',Distribution(a.a,a.w*np.exp(tilt*(a.a>0))))]:
                    predictions.append(score_row(h,fold,name,r,law,float(price.loc[r.origin,'close'])))
    pd.DataFrame(predictions).to_csv(OUT/'integration-predictions.csv',index=False)
    save('integration-ledger.json',ledger)
    (OUT/'integration-parent-laws.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in cache),encoding='utf-8')
    print('Complete-law integration',len(predictions),'forecasts',flush=True)


if __name__=='__main__':
    run()
