"""Combine complete laws and fit regularized simplex weights on mature dates."""
from itertools import combinations
from scipy.optimize import minimize
from .common import *
from .engine import Distribution,cohort_queries,score_law,buckets

CORE=['B_ROT','B_SPARSE_EQ','D_EQ_STUDENT','L_EQ_CONC','HISTORY','D_EQ_SIGNMAG']
POLICIES={
 'J11_FIXED_EQ':(['B_ROT','B_SPARSE_EQ','D_EQ_STUDENT'],[.4,.3,.3],'J10_STRUCTURAL_BLEND'),
 'J11_FIXED_NATIVE_EQ':(['B_NATIVE_EQ','B_SPARSE_EQ','D_EQ_STUDENT'],[.4,.3,.3],'J11_FIXED_EQ'),
 'J11_FIXED_HIST':(['B_ROT','B_SPARSE_EQ','D_EQ_STUDENT','HISTORY'],[.20,.15,.15,.50],'J10_HISTORY_SHRINK'),
 'J11_EQUAL':(CORE,None,'J11_FIXED_EQ'),
 'J11_NO_BREADTH':(['B_ROT','B_SPARSE','D_ROT_STUDENT','HISTORY'],[.20,.15,.15,.50],'J11_FIXED_HIST'),
 'J11_HISTORY_MORE':(CORE,[.1,.1,.1,.1,.5,.1],'J11_EQUAL'),
 'J11_STACK_BRIER':(CORE,'brier','J11_EQUAL'),
 'J11_STACK_CRPS':(CORE,'crps','J11_EQUAL'),
 'J11_STACK_REGIME':(CORE,'regime','J11_STACK_CRPS'),
 'J11_MEMORY':(['B_ROT','M_SPREAD_85','P_LONG_SHORT','O_ROT_BLOCKMEAN','HISTORY'],[.2,.2,.2,.2,.2],'J10_HISTORY_SHRINK'),
 'J11_ETF':(CORE+['D_ETF'],None,'J11_EQUAL'),
 'J11_DERIV_RISK':(CORE+['D_DERIV_RISK'],None,'J11_EQUAL'),
 'J11_REDUNDANT':(CORE+['B_ROT','B_ROT'],None,'J11_EQUAL'),
}
for expert in CORE:
    POLICIES[f'J11_EXCLUDE_{expert}']=([n for n in CORE if n!=expert],None,'J11_EQUAL')


def baseline_laws():
    laws={}
    paths=[V10/'base-laws.jsonl',OUT/'breadth-laws.jsonl',OUT/'distribution-laws.jsonl',OUT/'memory-laws.jsonl',OUT/'overlap-laws.jsonl']
    want={n for names,_,__ in POLICIES.values() for n in names}|{'B_ROT_EQ','B_STUD_EQ'}
    for path in paths:
        with path.open(encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                if r['model'] not in want:continue
                d=Distribution.__new__(Distribution);d.a=np.asarray(r['atoms']);d.w=np.asarray(r['weights'])
                laws[r['horizon'],r['origin'],r['model']]=d
    return laws


def moment(a,b):
    """Compute E|X-Y| from the weighted empirical CDF and partial first moments."""
    k=np.searchsorted(a.a,b.a,side='right')
    weight=np.r_[0,np.cumsum(a.w)][k]
    integral=np.r_[0,np.cumsum(a.w*a.a)][k]
    return float(b.w@(b.a*(2*weight-1)+(a.w@a.a)-2*integral))


def train_weights(data,dates,method):
    prior=np.full(len(CORE),1/len(CORE))
    if len(dates)<20:return prior,'less than 20 mature archived origins'
    A=np.stack([data[d]['prob'] for d in dates])
    y=np.array([data[d]['outcome'] for d in dates])
    if method=='brier':
        gram=A.T@A/len(y);lin=-2*A.T@y/len(y);reg=.075
    else:
        gram=-.5*np.mean([data[d]['pair'] for d in dates],axis=0)
        lin=np.mean([data[d]['absolute'] for d in dates],axis=0);reg=.006
    f=lambda w:float(w@gram@w+lin@w+reg*np.sum((w-prior)**2))
    jac=lambda w:2*gram@w+lin+2*reg*(w-prior)
    result=minimize(f,prior,jac=jac,bounds=[(.025,.55)]*len(prior),constraints=[{'type':'eq','fun':lambda w:w.sum()-1,'jac':lambda w:np.ones(len(w))}],
                    method='SLSQP',options={'ftol':1e-11,'maxiter':100})
    if not result.success:return prior,'solver fallback '+result.message
    w=np.maximum(result.x,0);return w/w.sum(),'fitted'


def run(exact=False):
    tag='ensemble-exact' if exact else 'ensemble'
    active={
      'J11_BREADTH_ALL':(['B_ROT_EQ','B_SPARSE_EQ','B_STUD_EQ'],[.4,.3,.3],'J10_STRUCTURAL_BLEND'),
      'J11_BREADTH_ALL_HIST':(['B_ROT_EQ','B_SPARSE_EQ','B_STUD_EQ','HISTORY'],[.2,.15,.15,.5],'J10_HISTORY_SHRINK'),
    } if exact else POLICIES
    save(f'{tag}-registry.json',{'registered':now(),'models':{n:{'parent':p,'experts':e,'policy':w,'diagnostic':n=='J11_REDUNDANT'}
           for n,(e,w,p) in active.items()},'code':sha(SRC/'ensemble.py'),'minimum_matured':20,'embargo':'Latest eligible endpoint strictly before each frozen monthly refit.'})
    laws=baseline_laws();price=matrix('price.csv')
    states=matrix('selection-states.csv',V10);vol=states.s_vol
    threshold=vol.rolling(63,min_periods=20).median().shift()
    risk=(vol>threshold);data=[];logs=[];archive=[];div=[];conditions=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv')
        query=cohort_queries(h);statistics={}
        for r in query.itertuples():
            ds=[laws.get((h,r.origin,n)) for n in CORE]
            if any(d is None for d in ds):continue
            pair=np.zeros((len(ds),len(ds)))
            for i,a in enumerate(ds):
                for j in range(i+1):
                    pair[i,j]=pair[j,i]=moment(a,ds[j])
            measures=[d.score(r.realized_return) for d in ds]
            statistics[r.origin]={'cohort':r.split,'endpoint':r.endpoint,'vol_high':bool(risk.loc[r.origin]),'outcome':int(r.realized_return>0),
                         'prob':np.array([m['p'] for m in measures]),'crps':np.array([m['crps'] for m in measures]),
                         'covered80':np.array([m['coverage80'] for m in measures]),
                         'absolute':np.array([d.w@abs(d.a-r.realized_return) for d in ds]),'pair':pair}
        for (c,fold),g in query.groupby(['split','fold'],sort=False):
            cutoff=g.origin.min();past=[t for t,v in statistics.items() if v['endpoint']<cutoff]
            pools=y.loc[y.endpoint.lt(cutoff),'return'].iloc[-252:].to_numpy()
            cuts=np.quantile(pools,[.1,.3,.5,.7,.9])
            for name,(experts,policy,parent) in active.items():
                w0=np.full(len(experts),1/len(experts)) if policy is None else policy
                fits={}
                if isinstance(policy,str):
                    if policy=='regime':
                        static,tag=train_weights(statistics,past,'crps')
                        for regime in [False,True]:
                            own=[d for d in past if statistics[d]['vol_high']==regime]
                            special,status=train_weights(statistics,own,'crps')
                            w=(.70*static+.30*special) if status=='fitted' else static
                            fits[regime]=(w,own,status)
                    else:
                        w,reason=train_weights(statistics,past,policy);fits={b:(w,past,reason) for b in [False,True]}
                else:fits={b:(w0,[],'fixed') for b in [False,True]}
                n=0
                for r in g.itertuples():
                    ds=[laws.get((h,r.origin,e)) for e in experts]
                    if any(d is None for d in ds):continue
                    w=fits[bool(risk.loc[r.origin])][0]
                    d=Distribution(np.concatenate([a.a for a in ds]),np.concatenate([float(k)*a.w for a,k in zip(ds,w)]))
                    data.append({**score_law(h,fold,name,r,d,float(price.close.loc[r.origin]),c),**buckets(d,r.realized_return,cuts)})
                    archive.append({'model':name,'horizon':h,'cohort':c,'origin':r.origin,'endpoint':r.endpoint,'atoms':d.a.tolist(),'weights':d.w.tolist()})
                    n+=1
                logs.append({'model':name,'horizon':h,'cohort':c,'fold':fold,'cutoff':cutoff,'queries':n,
                             'status':'ok' if n else 'unestimated','reason':None if n else 'missing component law',
                             'mature_dates':past if isinstance(policy,str) else [],
                             'conditional_weights':{str(b):{'weights':list(f[0]),'dates':f[1],'status':f[2]} for b,f in fits.items()}})
        for c in ['early','later','combined']:
            samples=[x for x in statistics.values() if c=='combined' or x['cohort']==c]
            a=np.stack([z['prob'] for z in samples]);y0=np.array([z['outcome'] for z in samples])
            cr=np.stack([z['crps'] for z in samples]);err=a-y0[:,None]
            for i,j in combinations(range(len(CORE)),2):
                b1=err[:,i]**2;b2=err[:,j]**2
                div.append({'horizon':h,'cohort':c,'expert1':CORE[i],'expert2':CORE[j],'n':len(samples),
                     'probability_corr':np.corrcoef(a[:,i],a[:,j])[0,1],'error_corr':np.corrcoef(err[:,i],err[:,j])[0,1],
                     'crps_corr':np.corrcoef(cr[:,i],cr[:,j])[0,1],'classification_disagreement':np.mean((a[:,i]>=.5)!=(a[:,j]>=.5)),
                     'shared_worst_decile':np.mean((b1>=np.quantile(b1,.9))&(b2>=np.quantile(b2,.9))),
                     'mean_cross_law_absolute_difference':np.mean([z['pair'][i,j] for z in samples]),
                     'energy_distance':np.mean([2*z['pair'][i,j]-z['pair'][i,i]-z['pair'][j,j] for z in samples])})
            for risk_state in [False,True]:
                group=[z for z in samples if z['vol_high']==risk_state]
                for j,n in enumerate(CORE):
                    pred=np.array([z['prob'][j] for z in group]);obs=np.array([z['outcome'] for z in group])
                    conditions.append({'horizon':h,'cohort':c,'model':n,'vol_high':risk_state,'n':len(group),
                                       'mean_probability':pred.mean(),'positive_rate':obs.mean(),'brier':np.mean((pred-obs)**2),
                                       'crps':np.mean([z['crps'][j] for z in group]),'coverage80':np.mean([z['covered80'][j] for z in group])})
    write(f'{tag}-predictions.csv',pd.DataFrame(data));cache(f'{tag}-laws.jsonl',archive)
    if not exact:
        write('expert-diversity.csv',pd.DataFrame(div));write('expert-conditional-calibration.csv',pd.DataFrame(conditions))
    save(f'{tag}-ledger.json',logs)
    print('Ensembles',len(data),'forecasts',flush=True)


if __name__=='__main__':
    import sys
    run('--exact' in sys.argv)
