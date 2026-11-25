"""Training composition, overlap-aware estimation and structured penalties."""
from scipy.linalg import cho_factor,cho_solve
from sklearn.linear_model import Ridge,BayesianRidge,LogisticRegression
from research.nifty_forecast_v8.models import Scale,canonical,clusters,families,Distribution,mix
from .common import *


def normalize(w):
    w=np.asarray(w,float)
    return w/w.sum()


def dependence(pos,h):
    return np.maximum(1-abs(pos[:,None]-pos[None,:])/h,0.)


def diagnostics(pos,h,w):
    ord=np.argsort(pos);pos=pos[ord];w=normalize(w[ord]);end=-1;disjoint=0
    for t in pos:
        if t>=end:disjoint+=1;end=t+h
    unique=len(set((pos[:,None]+np.arange(1,h+1)).ravel()))
    return {'nominal_rows':len(pos),'distinct_return_sessions':unique,'disjoint_training_windows':disjoint,
            'kish_ESS':float(1/(w@w)),'overlap_effective_count':float(1/(w@dependence(pos,h)@w)),
            'maximum_training_weight':float(w.max())}


def balanced_ids(dates,values,n):
    x=values.reindex(dates).fillna(values.reindex(dates).median()).fillna(0.).to_numpy()
    # Equal counts across four quantile classes. Within each class sample across time.
    order=np.argsort(x,kind='stable');groups=np.array_split(order,4);take=[]
    for j,group in enumerate(groups):
        k=n//4+int(j<n%4)
        take.extend(group[np.linspace(0,len(group)-1,k,dtype=int)])
    return dates[np.sort(take)]


def choose(dates,n,selection,state,query,seed):
    if not n or n>=len(dates):return dates
    if selection=='earliest':return dates[:n]
    if selection=='spread':return dates[np.linspace(0,len(dates)-1,n,dtype=int)]
    if selection=='blocks':
        k=n//5;starts=np.linspace(0,len(dates)-5,k,dtype=int) if k else np.array([],int)
        ix=list((starts[:,None]+np.arange(5)).ravel());addition=np.setdiff1d(np.arange(len(dates)),ix)[-int(n-len(ix)):] if len(ix)<n else []
        return dates[sorted(ix+list(addition))]
    if selection in ['balance_vol','balance_trend','balance_rotation']:
        c={'balance_vol':'s_vol','balance_trend':'s_trend','balance_rotation':'s_bank'}[selection]
        return balanced_ids(dates,state[c],n)
    if selection=='representative':
        v=similarity(state,dates,query)
        # Leave close and distant conditions represented through systematic coverage in analogue rank.
        ranks=np.argsort(v,kind='stable');return dates[np.sort(ranks[np.linspace(0,len(ranks)-1,n,dtype=int)])]
    if selection=='analogues':
        d=similarity(state,dates,query);return dates[np.sort(np.argsort(d,kind='stable')[:n])]
    if selection=='random_blocks':
        rng=np.random.default_rng(seed);blocks=np.array_split(np.arange(len(dates)),max(1,len(dates)//5));ids=np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])[:n]
        return dates[np.sort(ids)]
    return dates[-n:]


def similarity(state,dates,query):
    current=state.loc[query];sample=state.loc[dates];med=sample.median().fillna(0);std=sample.std().fillna(1).clip(lower=1e-8)
    z=(sample.fillna(med)-med)/std;recent=(current.fillna(med)-med)/std
    return np.sqrt(np.mean(np.clip(z.to_numpy()-recent.to_numpy(),-6,6)**2,axis=1))


def weights(kind,state,dates,query):
    n=len(dates);uniform=np.ones(n)/n
    if kind=='recency':signal=normalize(np.exp(-np.log(2)*np.arange(n-1,-1,-1)/55))
    elif kind=='similarity':signal=normalize(np.exp(-.75*similarity(state,dates,query)**2))
    elif kind=='balance':
        risk=state.loc[dates,'s_vol'];trend=state.loc[dates,'s_trend'];c=(risk>risk.median()).astype(int)+2*(trend>0).astype(int)
        signal=normalize(1/c.map(c.value_counts()).to_numpy())
    elif kind=='analogue_recency':signal=normalize(np.exp(-.5*similarity(state,dates,query)**2-np.log(2)*np.arange(n-1,-1,-1)/100))
    else:return uniform
    # Equal mass floor avoids fitting almost entirely to a few dates.
    return .40*uniform+.60*signal


def feature_map(spec,x,y):
    s=Scale().fit(x);a=s.transform(x);names=s.cols;ids=np.arange(len(names));aliases=[]
    if spec.get('dedup',True):
        raw=x[names].to_numpy(float);z=(np.where(np.isfinite(raw),raw,s.med)-s.mu)/s.sd
        ids,aliases=canonical(names,np.c_[z.T,np.isfinite(raw).T]);a=a[:,ids]
    basis=np.eye(len(names))[:,ids];n=[names[k] for k in ids];rep=spec.get('rep','plain');clusters_saved=[]
    if rep in ['groups','hierarchy','pool','factor_residual','cluster_elastic']:
        ids0=np.array([j for j,c in enumerate(n) if c.startswith('i_') and c.endswith(('_rel5','_rel21'))],int)
        lab=np.array(families(n));w=np.eye(len(n))
        cg=[]
        if len(ids0)>1:
            groups,cor,_=clusters(a[:,ids0]);cg=[[int(ids0[k]) for k in g] for g in groups]
            clusters_saved=[[n[j] for j in g] for g in cg]
        if rep=='groups' or rep=='hierarchy':
            for key in ['BANKS','DEFENSIVE','CYCLICAL','BROAD']:
                g=np.flatnonzero(lab==key)
                if len(g):w[g,g]/=np.sqrt(len(g))
            if rep=='hierarchy':
                for g in cg:w[g,g]/=np.sqrt(len(g))
        elif rep=='cluster_elastic':
            for g in cg:w[g,g]/=np.sqrt(len(g))
        elif rep in ['pool','factor_residual']:
            groups=[];ungrouped=np.ones(len(n),bool)
            for key in ['BANKS','DEFENSIVE','CYCLICAL','BROAD','IT']:
                g=np.flatnonzero(lab==key)
                if len(g)>=2:groups.append(g);ungrouped[g]=False
            if groups:
                F=np.column_stack([np.isin(np.arange(len(n)),g)/len(g) for g in groups]);w=np.c_[w[:,ungrouped],F]
                if rep=='factor_residual':
                    U=a@F;projection=np.linalg.solve(U.T@U+15*np.eye(len(groups)),U.T@a[:,~ungrouped]);w=np.c_[w,.5*(np.eye(len(n))[:,~ungrouped]-F@projection)]
        basis=basis@w
    elif rep=='lowrank':
        _,_,vectors=np.linalg.svd(a-a.mean(axis=0),full_matrices=False);basis=basis@vectors[:min(5,len(vectors))].T
    return s,basis,{'aliases':aliases,'clusters':clusters_saved}


def fit(spec,x,y,pos,h,date_state,anchor):
    """Fit a scalar or vector location after selecting the training dates."""
    s,basis,meta=feature_map(spec,x,y);a=s.transform(x)@basis;y=np.asarray(y,float)
    if y.ndim==1:y=y[:,None]
    n=len(a);pr=weights(spec.get('weight'),date_state,x.index,anchor);alpha=spec.get('alpha',125)
    dep=dependence(pos,h);method=spec.get('overlap','plain');diag=diagnostics(pos,h,pr);estimators=[]
    X=np.c_[np.ones(n),a];P=np.eye(X.shape[1]);P[0,0]=1e-8

    def solve(Q,Z,Y,reg):
        normal=Z.T@Q@Z;rhs=Z.T@Q@Y;system=normal+reg*P
        factor=cho_factor(system,check_finite=False)
        b=cho_solve(factor,rhs,check_finite=False)
        df=float(np.trace(cho_solve(factor,normal,check_finite=False)))
        return b,df,float(np.linalg.cond(system))
    if method=='overlap_weight':
        pr=normalize(1/np.maximum(dep.sum(axis=0),1));diag=diagnostics(pos,h,pr)
    if method in ['gls','gls_strong','gls_empirical']:
        rho=.65 if method!='gls_strong' else .85;cov=(1-rho)*np.eye(n)+rho*dep
        if method=='gls_empirical':
            pilot,_,_=solve(np.eye(n),X,y,alpha)
            err=(y-X@pilot).reshape(n,-1)[:,0]
            distance=abs(pos[:,None]-pos[None,:]);pairs=(distance==1)&np.triu(np.ones((n,n),bool),1)
            left,right=np.where(pairs)
            ac=float(np.corrcoef(err[left],err[right])[0,1]) if len(left)>15 and np.std(err)>1e-10 else 0.
            ac=float(np.clip(np.nan_to_num(ac),0,.96));cov=.25*np.eye(n)+.45*dep+.30*ac**distance
            diag['training_residual_lag1']=ac
        inv=cho_solve(cho_factor(cov,check_finite=False),np.eye(n),check_finite=False)
        # Normalize exposure to a constant intercept, preserving comparable ridge scale.
        inv*=n/max(float(inv.sum()),1e-8);b,df,cond=solve(inv,X,y,alpha);estimators.append(b)
        diag['label_covariance_condition']=float(np.linalg.cond(cov))
    elif method in ['phase0','phase1','staggered']:
        phases=[0] if method=='phase0' else [min(2,h-1)] if method=='phase1' else list(range(h))
        degrees=[];condition=[];counts=[]
        for phase in phases:
            mask=pos%h==phase
            if mask.sum()<3:continue
            b,d,c=solve(np.eye(mask.sum()),X[mask],y[mask],alpha*mask.mean())
            estimators.append(b);degrees.append(d);condition.append(c);counts.append(int(mask.sum()))
        if not estimators:raise ValueError('No eligible disjoint training phase')
        df=float(np.mean(degrees));cond=max(condition);diag['phase_sample_sizes']=counts
        if len(phases)==1:
            mask=pos%h==phases[0];diag.update(diagnostics(pos[mask],h,np.ones(mask.sum())))
    elif method=='blockmean':
        groups=(pos-pos.min())//h;ids=np.unique(groups)
        Z=np.stack([X[groups==k].mean(axis=0) for k in ids]);Y=np.stack([y[groups==k].mean(axis=0) for k in ids])
        b,df,cond=solve(np.eye(len(ids)),Z,Y,alpha*len(ids)/n);estimators.append(b);diag['block_equations']=len(ids)
    elif spec.get('kind')=='elastic':
        from sklearn.linear_model import ElasticNet
        rr=ElasticNet(alpha=.00055,l1_ratio=.25,max_iter=12000).fit(a,y[:,0],sample_weight=pr*n)
        b=np.r_[rr.intercept_,rr.coef_][:,None];estimators.append(b);df=float(1+np.count_nonzero(rr.coef_));cond=float(np.linalg.cond(X.T@X+alpha*P))
    elif spec.get('kind')=='bayes':
        rr=BayesianRidge(lambda_1=.01,lambda_2=.01).fit(a,y[:,0]);estimators.append(np.r_[rr.intercept_,rr.coef_][:,None])
        df=float(np.trace(np.eye(a.shape[1])-rr.lambda_*rr.sigma_)+1);cond=float(np.linalg.cond(X.T@X+alpha*P))
    else:
        if spec.get('shared_rank'):
            center=y.mean(axis=0);std=y.std(axis=0).clip(min=1e-7)
            b,df,cond=solve(np.diag(pr*n),X,(y-center)/std,alpha)
            u,v,w=np.linalg.svd(b[1:].T,full_matrices=False);k=min(spec['shared_rank'],len(v))
            b[1:]=((u[:,:k]*v[:k])@w[:k]).T;b=b*std;b[0]+=center;estimators.append(b)
        else:
            b,df,cond=solve(np.diag(pr*n),X,y,alpha);estimators.append(b)
    beta=np.mean(estimators,axis=0)
    meta.update(diag,df=df,design_condition=cond,peak_coefficient=float(abs(beta[1:]).max()),
                member_variance=float(np.mean(np.var(np.stack(estimators),axis=0))))
    return {'scale':s,'basis':basis,'beta':beta,'member_beta':estimators,'metadata':meta,'weights':pr,'spec':spec}


def location(model,x,member=False):
    z=model['scale'].transform(x)@model['basis'];a=np.c_[np.ones(len(z)),z]
    return np.stack([a@b for b in model['member_beta']],axis=0) if member else a@model['beta']
