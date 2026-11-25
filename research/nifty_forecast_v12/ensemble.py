"""Expert novelty, exact duplicate invariance and matured-only law weighting."""
from itertools import combinations
from scipy.optimize import minimize
from .common import *
from .market import MAIN
from research.nifty_forecast_v9.run_models import cohort_queries,score_law
from research.nifty_forecast_v10.targets import buckets
from research.nifty_forecast_v11.ensemble import moment

CORE=['V12_STAT','V12_IV_SCALE','V12_JOINT_IV','PH_NATIVE_PHASE_MIXTURE','V12_HIST']
QCORE=CORE+['P12_Q_TILT']
ROLE={'V12_STAT':'statistical','PH_NATIVE_PHASE_MIXTURE':'phase','V12_IV_SCALE':'priced risk',
      'V12_JOINT_IV':'priced risk','V12_HIST':'historical','P12_Q_TILT':'calibrated priced shape'}
ALIASES={'STAT_COPY':'V12_STAT','STAT_COPY_TWO':'V12_STAT'}


def designs():
    all_={
      'J12_EQUAL':(CORE,'equal','V12_STAT'),
      'J12_GROUP_BALANCED':(CORE,'group','J12_EQUAL'),
      'J12_SIMILARITY_CLUSTERS':(CORE,'clusters','J12_EQUAL'),
      'J12_CANONICAL':(CORE,'canonical','J12_EQUAL'),
      'J12_DUPLICATE_CANONICAL':(CORE+list(ALIASES),'canonical','J12_CANONICAL'),
      'J12_DUPLICATE_NAIVE':(CORE+list(ALIASES),'equal','J12_EQUAL'),
      'J12_PHASE_MARKET':(['PH_NATIVE_PHASE_MIXTURE','V12_IV_SCALE','V12_HIST'],[.50,.30,.20],'PH_NATIVE_PHASE_MIXTURE'),
      'J12_HISTORICAL_MARKET':(['V12_STAT','V12_IV_SCALE','V12_HIST'],[.45,.30,.25],'V12_STAT'),
      'J12_STACK_BRIER':(CORE,'brier','J12_CANONICAL'),
      'J12_STACK_CRPS':(CORE,'crps','J12_CANONICAL'),
      'J12_STACK_DEDUP':(CORE+list(ALIASES),'crps_canonical','J12_STACK_CRPS'),
      'J12_Q_EQUAL':(QCORE,'equal','J12_EQUAL'),
      'J12_Q_GROUP':(QCORE,'group','J12_Q_EQUAL'),
      'J12_Q_STACK':(QCORE,'crps','J12_Q_EQUAL'),
      'J12_Q_CROSS':(['V12_STAT','P12_Q_TILT','V12_JOINT_IV'],[.55,.20,.25],'P12_Q_PHYSICAL_MIX'),
      'J12_Q_HISTORICAL':(['V12_STAT','P12_Q_TILT','V12_HIST'],[.45,.20,.35],'P12_Q_HIST_FALLBACK'),
    }
    for expert in CORE:
        all_[f'J12_OMIT_{expert}']=([n for n in CORE if n!=expert],'equal','J12_EQUAL')
        all_[f'J12_ADD_{expert}']=(list(dict.fromkeys(['V12_STAT','V12_HIST',expert])),'equal','J12_STAT_HIST_CONTROL')
    all_['J12_STAT_HIST_CONTROL']=(['V12_STAT','V12_HIST'],[.5,.5],'V12_STAT')
    return all_


def distribution_keys():
    cache={}
    for batch in ['market','priced','phase']:
        for (h,n,d,e),law in bundle_entries(OUT/f'laws/{batch}.npz'):
            if n in QCORE:cache[int(h),n,d]=law
    for (h,n,d),law in list(cache.items()):
        if n=='V12_STAT':
            for alias in ALIASES:cache[h,alias,d]=exact_law(law.a.copy(),law.w.copy())
    return cache


def digest(d):
    from hashlib import sha256
    return sha256(d.a.tobytes()+d.w.tobytes()).digest()


def deduplicate(cache,h,members,history):
    """Canonicalize exact expert archives while preserving economically distinct experts."""
    chosen=[];present=set()
    for n in members:
        alias=ALIASES.get(n,n)
        if n!=alias:
            assert all(digest(cache[h,n,d])==digest(cache[h,alias,d]) for d in history)
        if alias not in present:chosen.append(alias);present.add(alias)
    return chosen


def group_weights(experts,cluster):
    distinct=set(cluster.values())
    return np.array([1/(len(distinct)*sum(v==cluster[e] for v in cluster.values())) for e in experts],float)


def similarity(am,experts):
    # Use the joint vector of probabilities, quantiles and means from earlier laws.
    if len(am)<20:return {n:n for n in experts}
    X=np.asarray(am)
    corr=np.corrcoef(X,rowvar=False)
    left={n:n for n in experts}
    for i,j in combinations(range(len(experts)),2):
        if np.isfinite(corr[i,j]) and corr[i,j]>=.965:
            a,b=left[experts[i]],left[experts[j]]
            left={n:a if v==b else v for n,v in left.items()}
    return left


def features(cache,h,names,days,y):
    rows={}
    for day in days:
        ds=[cache[h,n,day] for n in names]
        realized=float(y.loc[day,'return'])
        p=np.array([d.w[d.a>0].sum() for d in ds])
        mean=np.array([d.w@d.a for d in ds])
        width=np.array([float(d.quantile(.9)-d.quantile(.1)) for d in ds])
        pair=np.zeros((len(ds),len(ds)))
        for i,a in enumerate(ds):
            for j in range(i+1):pair[i,j]=pair[j,i]=moment(a,ds[j])
        ae=np.array([d.w@abs(d.a-realized) for d in ds])
        rows[day]={'p':p,'mu':mean,'width':width,'pair':pair,'abs':ae,'direction':int(realized>0),'y':realized}
    return rows


def solve_weights(values,n,mode):
    w0=np.full(n,1/n)
    if len(values)<20:return w0,'fewer than 20 mature forecasts'
    if mode=='brier':
        a=np.stack([v['p'] for v in values]);y=np.array([v['direction'] for v in values])
        G=a.T@a/len(a);b=-2*a.T@y/len(a);penalty=.09
    else:
        G=-.5*np.mean([v['pair'] for v in values],axis=0)
        b=np.mean([v['abs'] for v in values],axis=0);penalty=.010
    f=lambda w:float(w@G@w+b@w+penalty*((w-w0)**2).sum())
    grad=lambda w:2*G@w+b+2*penalty*(w-w0)
    ans=minimize(f,w0,jac=grad,bounds=[(.03,.65)]*n,constraints=[{'type':'eq','fun':lambda w:w.sum()-1.,
                 'jac':lambda w:np.ones(n)}],method='SLSQP',options={'ftol':1e-11,'maxiter':120})
    w=ans.x.clip(min=0.)
    return (w/w.sum(),'fit') if ans.success else (w0,'solver fallback')


def evaluate():
    plan=designs()
    save('ensemble-registry.json',{'registered_at':now(),'code':sha(SRC/'ensemble.py'),'forecast_archive':list(QCORE),
          'models':{n:{'members':r[0],'weighting':r[1],'parent':r[2],'diagnostic':n=='J12_DUPLICATE_NAIVE'}
                      for n,r in plan.items()},'aliases':ALIASES,'min_mature':20})
    laws=distribution_keys()
    price=matrix('price.csv')
    save_rows=[];keys=[];output=[];attempt=[];pair_report=[];invariance=[]
    for h in [5,21]:
        y=matrix(f'labels-{h}.csv')
        q=cohort_queries(h)
        index=q.set_index('origin')
        by_groups={}
        for required in [CORE,QCORE]:
            days=[d for d in q.origin if all((h,n,d) in laws for n in required)]
            by_groups[tuple(required)]=features(laws,h,required,days,y)
        r_data=by_groups[tuple(CORE)]
        for c in ['early','later','combined']:
            for flag in ['all','high_prior_volatility','low_prior_volatility']:
                v=matrix(f'features/{h}-TRADE.csv',OUT).rv21
                high=v>v.shift().rolling(63,min_periods=25).median()
                dates=[d for d in r_data if (c=='combined' or index.loc[d,'split']==c) and
                       (flag=='all' or bool(high.at[d])==(flag=='high_prior_volatility'))]
                a=[r_data[d] for d in dates]
                if len(a)<5:continue
                prob=np.stack([v['p'] for v in a]);mu=np.stack([v['mu'] for v in a])
                width=np.stack([v['width'] for v in a]);obs=np.array([v['y'] for v in a])
                expected=np.array([v['direction'] for v in a])
                err=prob-expected[:,None]
                for i,j in combinations(range(len(CORE)),2):
                    x=err[:,i]**2;z=err[:,j]**2
                    pair_report.append({'horizon':h,'cohort':c,'condition':flag,'n':len(a),'first':CORE[i],'second':CORE[j],
                        'probability_corr':np.corrcoef(prob[:,i],prob[:,j])[0,1],
                        'location_corr':np.corrcoef(mu[:,i],mu[:,j])[0,1],
                        'width_corr':np.corrcoef(width[:,i],width[:,j])[0,1],
                        'directional_error_corr':np.corrcoef(err[:,i],err[:,j])[0,1],
                        'return_error_corr':np.corrcoef(mu[:,i]-obs,mu[:,j]-obs)[0,1],
                        'shared_worst_decile':np.mean((x>=np.quantile(x,.9))&(z>=np.quantile(z,.9))),
                        'direction_disagreement':np.mean((prob[:,i]>=.5)!=(prob[:,j]>=.5)),
                        'energy_distance':np.mean([2*t['pair'][i,j]-t['pair'][i,i]-t['pair'][j,j] for t in a])})
        exact={}
        for (c,fold),g in q.groupby(['split','fold'],sort=False):
            first=g.origin.min()
            history=y.loc[y.endpoint.notna()&y.endpoint.lt(first),'return'].iloc[-252:]
            cut=np.quantile(history,[.1,.3,.5,.7,.9])
            for name,(names,mode,parent) in plan.items():
                original=tuple(names)
                q_set=QCORE if 'P12_Q_TILT' in names else CORE
                history=by_groups[tuple(q_set)]
                mature=[d for d in history if index.at[d,'endpoint']<first]
                if mode in ['canonical','crps_canonical']:names=deduplicate(laws,h,names,mature+list(g.origin))
                train=[];roles=None;status='fixed'
                if isinstance(mode,list):w=np.asarray(mode,float)
                elif mode=='group':
                    roles={e:ROLE[e] for e in names};w=group_weights(names,roles)
                elif mode=='clusters':
                    train=mature.copy()
                    arrays=[history[d]['p'] for d in train]
                    roles=similarity(arrays,names);w=group_weights(names,roles)
                    status='clustered mature archives'
                elif mode in ['brier','crps','crps_canonical']:
                    assert names==list(q_set)
                    train=mature.copy()
                    w,status=solve_weights([history[d] for d in train],len(names),'brier' if mode=='brier' else 'crps')
                else:w=np.full(len(names),1/len(names))
                scored=0
                for r in g.itertuples():
                    if not all((h,n,r.origin) in laws for n in names):continue
                    d=mixture([laws[h,n,r.origin] for n in names],w)
                    if name in ['J12_CANONICAL','J12_STACK_CRPS']:
                        exact[name,r.origin]=d
                    if name in ['J12_DUPLICATE_CANONICAL','J12_STACK_DEDUP']:
                        alias='J12_CANONICAL' if name=='J12_DUPLICATE_CANONICAL' else 'J12_STACK_CRPS'
                        want=exact[alias,r.origin]
                        np.testing.assert_array_equal(d.a,want.a)
                        np.testing.assert_array_equal(d.w,want.w)
                        invariance.append({'horizon':h,'origin':r.origin,'model':name,'reference':alias,'exact':True})
                    save_rows.append({**score_law(h,fold,name,r,d,float(price.close.loc[r.origin]),c),**buckets(d,r.realized_return,cut),
                                      'absolute_return_error':abs(float(d.w@abs(d.a))-abs(r.realized_return))})
                    keys.append((h,name,r.origin,r.endpoint));output.append(d);scored+=1
                attempt.append({'model':name,'horizon':h,'cohort':c,'fold':fold,'cutoff':first,'status':'ok' if scored else 'unestimated',
                  'reason':None if scored else 'missing complete component', 'quotes':scored,'input_members':list(original),
                  'active_members':names,'weights':list(w),'fit_origins':train,'weight_status':status,'cluster_or_role':roles})
        print('Ensembles',h,'sessions;',len(save_rows),'complete laws',flush=True)
    write('ensemble-predictions.csv',pd.DataFrame(save_rows));save('ensemble-ledger.json',attempt)
    write('expert-information.csv',pd.DataFrame(pair_report));write('ensemble-exact-invariance.csv',pd.DataFrame(invariance))
    save('ensemble-laws.json',pack_bundle('laws/ensemble.npz',keys,output))


if __name__=='__main__':evaluate()
