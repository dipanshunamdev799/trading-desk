"""Fixed-calendar disjoint phases, pooled coefficients and matched training memories."""
import joblib
from scipy.linalg import solve
from .common import *
from research.nifty_forecast_v10.estimators import feature_map,diagnostics,fit,location,choose
from research.nifty_forecast_v10.targets import buckets
from research.nifty_forecast_v11.engine import inputs,dates
from research.nifty_forecast_v9.run_models import cohort_queries,score_law


def phase_set():
    cfg={f'PH_NATIVE_{i:02}':{'method':'phase','phase':i,'frame':'native','parent':'PH_NATIVE_PLAIN',
          'horizons':[21] if i>=5 else [5,21]} for i in range(21)}
    for frame,label in [('native','NATIVE'),('rotation','ROT')]:
        for method in ['plain','blockmean','overlap_weight','phase_location','phase_mixture','pooled','shared']:
            cfg[f'PH_{label}_{method.upper()}']={'method':method,'frame':frame,
                 'parent':('BASE_NATIVE' if frame=='native' else 'BASE_ROTATION') if method=='plain' else f'PH_{label}_PLAIN'}
    for n in [85,126]:
        for mode in ['recent','spread','diverse','random_blocks','phase_balance']:
            parent=f'PH_MEM{n}_RECENT_PLAIN'
            for method in ['plain','phase_mixture','blockmean']:
                cfg[f'PH_MEM{n}_{mode.upper()}_{method.upper()}']={'method':method,'frame':'native','budget':n,'selection':mode,
                         'parent':parent if mode!='recent' or method!='plain' else 'PH_NATIVE_PLAIN','diagnostic':mode=='random_blocks'}
    return cfg


def select_balanced(pool,n,pos,h):
    """Use approximately equal phase quotas and evenly spread dates within each."""
    order=[]
    for i in range(h):
        a=pool[pos.loc[pool].to_numpy()%h==i]
        order.append(list(a))
    quota=np.zeros(h,int);remaining=n
    while remaining:
        possible=[i for i in range(h) if len(order[i])>quota[i]]
        if not possible:break
        for i in possible:
            quota[i]+=1;remaining-=1
            if remaining==0:break
    dates=[np.asarray(order[i])[np.linspace(0,len(order[i])-1,quota[i],dtype=int)] for i in range(h) if quota[i]]
    return pd.Index(sorted(np.concatenate(dates)))


def make_plan(y,setting,state,k,pos,h,loss,seed=SEED):
    mode=setting.get('selection','recent')
    mask=pd.Series(True,index=pos.index)
    if mode!='phase_balance':return dates(y,setting,state,k,mask,pos,h,loss,seed)
    tr,ii,vv,pool,ic=dates(y,{},state,k,mask,pos,h,loss,seed)
    n=setting['budget']
    if len(tr)<n:raise ValueError('Insufficient nominal phase-balanced budget')
    return select_balanced(tr,n,pos,h),select_balanced(ii,min(n,len(ii)),pos,h),vv,pool,ic


def basis(x,y,query,p,h):
    scale,transform,_=feature_map({},x,y)
    a=np.c_[np.ones(len(x)),scale.transform(x)@transform]
    b=np.c_[np.ones(len(query)),scale.transform(query)@transform]
    reg=np.eye(a.shape[1])
    reg[0,0]=1e-8
    return a,b,reg,scale,transform


def fit_family(x,y,query,pos,h,anchor,state,perm_seed=None,phase_only=False):
    yy=y.loc[x.index,'return'].to_numpy()
    if perm_seed is not None:
        rng=np.random.default_rng(perm_seed)
        blocks=np.array_split(yy,max(2,len(yy)//h))
        yy=np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
    a,b,reg,scale,transform=basis(x,yy,query,pos,h)
    observed=pos.loc[x.index].to_numpy()
    phases=observed%h
    fit_phases={}
    for i in range(h):
        ix=phases==i;n=int(ix.sum())
        if n<3:continue
        H=a[ix].T@a[ix];g=a[ix].T@yy[ix]
        beta=solve(H+125.*n/len(a)*reg,g,assume_a='pos',check_finite=False)
        fit_phases[i]={'prediction':b@beta,'beta':beta,'rows':n,'information':diagnostics(observed[ix],h,np.ones(n))}
    if not fit_phases:raise ValueError('No mature disjoint phase has three labels')
    if phase_only:return {'phases':fit_phases}
    pred={m:location(fit({'overlap':m},x,yy,observed,h,state,anchor),query)[:,0] for m in ['plain','blockmean','overlap_weight']}
    # The shared model gives equal influence to each phase, with a block-average coefficient prior.
    equal=np.zeros(len(a))
    for i,result in fit_phases.items():equal[phases==i]=len(a)/(result['rows']*len(fit_phases))
    equation=(a.T*equal)@a
    g=(a.T*equal)@yy
    groups=(observed-observed.min())//h
    block_a=np.stack([a[groups==i].mean(axis=0) for i in np.unique(groups)])
    block_y=np.array([yy[groups==i].mean() for i in np.unique(groups)])
    prior=solve(block_a.T@block_a+125.*len(block_a)/len(a)*reg,block_a.T@block_y,assume_a='pos')
    shared=solve(equation+250*reg,g+125*reg@prior,assume_a='pos',check_finite=False)
    betas=np.stack([z['beta'] for z in fit_phases.values()])
    pred['shared']=b@shared
    pred['phase_location']=b@betas.mean(axis=0)
    pred['pooled']=b@(.60*prior+.40*betas.mean(axis=0))
    return {'phases':fit_phases,'pred':pred,'shared_beta':shared,'prior_beta':prior,'features':scale.cols,'basis':transform,'scale':scale,
            'support':diagnostics(observed,h,np.ones(len(observed))),
            'member_location_sd':float(np.std(b@betas.T,axis=1).mean()),'member_coefficient_sd':float(np.std(betas,axis=0).mean())}


def combinations(mode,phase,large,small,y,valid,past):
    err_y=y.loc[valid,'return'].to_numpy()
    if mode=='phase':
        if phase not in large['phases'] or phase not in small['phases']:
            raise ValueError('Fewer than three phase-specific mature inner or outer dates')
        l=large['phases'][phase]['prediction']
        residual=err_y-small['phases'][phase]['prediction']
        atoms=l[:,None]+residual[None,:]
    elif mode=='phase_mixture':
        active=sorted(set(large['phases'])&set(small['phases']))
        atoms=np.concatenate([large['phases'][i]['prediction'][:,None]+(err_y-small['phases'][i]['prediction'])[None,:]
                              for i in active],axis=1)
    else:atoms=large['pred'][mode][:,None]+(err_y-small['pred'][mode])[None,:]
    weights=np.r_[np.full(atoms.shape[1],.65/atoms.shape[1]),np.full(len(past),.35/len(past))]
    return [Distribution(np.maximum(np.r_[a,past],-.999999),weights) for a in atoms]


def run():
    cfg=phase_set()
    frames,_,state,price,broad,pos,loss=inputs()
    save('phase-registry.json',{'registered_at':now(),'models':cfg,'code':sha(SRC/'phase.py'),
         'phase_calendar_anchor':str(pos.index[0]),'definition':'Observed session position from frozen V6 calendar modulo h; same anchor in every fold.',
         'prespecified_default':'Equal complete-law phase mixture, with an ordinary overlapping and block-average control.'})
    attempt=[];rows=[];keys=[];archive=[]
    for h in [5,21]:
        yy=matrix(f'labels-{h}.csv')
        for (cohort,fold),g in cohort_queries(h).groupby(['split','fold'],sort=False):
            k=g.origin.min();plans={}
            for n,s in cfg.items():
                if h not in s.get('horizons',[5,21]):continue
                ident=(s['frame'],s.get('budget'),s.get('selection','recent'))
                item={'model':n,'horizon':h,'cohort':cohort,'fold':fold,'cutoff':k}
                try:
                    if ident not in plans:
                        x=frames[s['frame']]
                        tr,ii,vv,pool,ic=make_plan(yy,s,state,k,pos,h,loss)
                        a=fit_family(x.loc[tr],yy,x.loc[g.origin],pos,h,k,state)
                        b=fit_family(x.loc[ii],yy,x.loc[vv],pos,h,ic,state)
                        rel=f'models/phase/{h}-{cohort}-{fold}-{ident[0]}-{ident[1] or "all"}-{ident[2]}.joblib'
                        path=OUT/rel;path.parent.mkdir(parents=True,exist_ok=True)
                        joblib.dump({'outer':a,'inner':b,'training':list(tr),'inner_dates':list(ii),'validation':list(vv),
                                     'query':list(g.origin),'pool':list(pool[-252:])},path,compress=2)
                        plans[ident]=(a,b,tr,ii,vv,pool,ic,rel,sha(path))
                    a,b,tr,ii,vv,pool,ic,rel,digest=plans[ident]
                    hist=yy.loc[pool[-252:],'return'].to_numpy()
                    laws=combinations(s['method'],s.get('phase'),a,b,yy,vv,hist)
                    bounds=np.quantile(hist,[.1,.3,.5,.7,.9])
                    for r,law in zip(g.itertuples(),laws):
                        rows.append({**score_law(h,fold,n,r,law,float(price.close.loc[r.origin]),cohort),**buckets(law,r.realized_return,bounds)})
                        keys.append((h,n,r.origin,r.endpoint));archive.append(law)
                    support=a['phases'][s['phase']]['information'] if s['method']=='phase' else a['support']
                    item.update(status='ok',training=len(tr),inner=len(ii),queries=len(g),file=rel,sha256=digest,
                        last_endpoint=yy.loc[tr,'endpoint'].max(),inner_last_endpoint=yy.loc[ii,'endpoint'].max(),inner_cutoff=ic,
                        active_phases=sorted(set(a['phases'])&set(b['phases'])),phase_counts={i:v['rows'] for i,v in a['phases'].items()},
                        member_location_sd=a['member_location_sd'],member_coefficient_sd=a['member_coefficient_sd'],support=support)
                except (ValueError,KeyError,np.linalg.LinAlgError) as error:item.update(status='unestimated',reason=str(error))
                attempt.append(item)
        print('Phase designs',h,'sessions;',len(rows),'cumulative forecasts',flush=True)
    write('phase-predictions.csv',pd.DataFrame(rows));save('phase-ledger.json',attempt)
    save('phase-laws.json',pack_bundle('laws/phase.npz',keys,archive))


if __name__=='__main__':run()
