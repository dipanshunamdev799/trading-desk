"""Train-only duplicate handling, structured penalties, and endpoint laws."""
from sklearn.linear_model import Ridge, ElasticNet, BayesianRidge, QuantileRegressor
from sklearn.covariance import LedoitWolf
from scipy.stats import t
from .common import *
from research.nifty_forecast_v7.models import clusters, families, Scale, Distribution, mix, cross_abs


def canonical(names, standardized):
    """Identify the same affine standardized history, including missingness.

    The caller appends missingness to each fingerprint before equivalence tests.
    Tie breaking uses stable feature names and never reads query observations.
    """
    kept, duplicates = [], []
    for i in sorted(range(len(names)),key=lambda k:names[k]):
        match = next((j for j in kept if np.allclose(standardized[i],standardized[j],rtol=0,atol=1e-11)),None)
        if match is None:kept.append(i)
        else:duplicates.append((names[i],names[match]))
    return np.array(kept),duplicates


def fit(spec,x,y):
    scale=Scale().fit(x)
    a=scale.transform(x)
    names=scale.cols
    meta={'aliases':[],'clusters':[]}
    base=np.eye(len(names))
    if spec.get('dedup'):
        values=x[names].to_numpy(float)
        # Use unclipped standardized values for identification, plus exact missing masks.
        raw=(np.where(np.isfinite(values),values,scale.med)-scale.mu)/scale.sd
        ids,aliases=canonical(names,np.c_[raw.T,np.isfinite(values).T]);meta['aliases']=aliases
        base=base[:,ids];a=a[:,ids];names=[names[i] for i in ids]
    size=len(names)
    rep=spec.get('rep','raw')
    if rep in ['cluster','hierarchical','cluster_bayes','representative','factor_residual','covariance']:
        is_sector=lambda c:c.startswith('i_') and c.endswith(('_rel5','_rel21'))
        ids=np.array([j for j,c in enumerate(names) if is_sector(c)],dtype=int)
        if len(ids)<2:raise ValueError('Structured representation needs native sector columns')
        groups,cor,_=clusters(a[:,ids]);meta['clusters']=[[names[ids[j]] for j in group] for group in groups]
        transform=np.eye(size)
        if rep in ['cluster','cluster_bayes','hierarchical']:
            labels=np.array(families(names))
            for g in groups:
                members=ids[g]
                transform[members,members]/=np.sqrt(len(g))
                if rep=='hierarchical':
                    for j in members:transform[j,j]/=np.sqrt(max(1,np.sum(labels==labels[j])/4))
        elif rep=='covariance':
            cov=LedoitWolf().fit(a[:,ids]).covariance_
            eig,basis=np.linalg.eigh(np.eye(len(ids))+.65*cov)
            transform[np.ix_(ids,ids)]=(basis*(eig**-.5))@basis.T
        else:
            factors=[]
            for g in groups:
                medoid=g[np.argmax(abs(cor[np.ix_(g,g)]).sum(axis=1))]
                loading=np.zeros(size)
                if rep=='representative':
                    yc=y-y.mean();predictor=a[:,ids[g]];z=predictor-predictor.mean(axis=0)
                    correlation=abs(z.T@yc)/(np.linalg.norm(z,axis=0)*np.linalg.norm(yc)+1e-12)
                    centrality=abs(cor[np.ix_(g,g)]).mean(axis=1)
                    loading[ids[g[np.argmax(.75*centrality+.25*correlation)]]]=1
                else:
                    loading[ids[g]]=np.where(cor[g,medoid]<0,-1,1)/len(g)
                factors.append(loading)
            other=np.setdiff1d(np.arange(size),ids)
            transform=np.c_[np.eye(size)[:,other],np.column_stack(factors)]
            if rep=='factor_residual':
                ff=np.column_stack(factors);f=a@ff
                beta=np.linalg.solve(f.T@f+10*np.eye(f.shape[1]),f.T@a[:,ids])
                # Ridge projection of supervised inputs on train-only cluster averages.
                residual=np.eye(size)[:,ids]-ff@beta
                transform=np.c_[transform,.5*residual]
        base=base@transform
    if rep=='defensive':
        defs=np.flatnonzero(np.array(families(names))=='DEFENSIVE')
        if len(defs):base[:,defs]/=np.sqrt(len(defs))
    z=scale.transform(x)@base
    kind=spec.get('kind','ridge')
    estimator=Ridge(alpha=spec.get('alpha',100))
    if kind=='elastic':estimator=ElasticNet(alpha=.0006,l1_ratio=.3,max_iter=8000)
    if kind=='bayes':estimator=BayesianRidge(alpha_1=1e-3,alpha_2=1e-3,lambda_1=1e-3,lambda_2=1e-3)
    estimator.fit(z,y)
    obj={'spec':spec,'scale':scale,'transform':base,'estimator':estimator,'pool':np.asarray(y[-252:]),'metadata':meta}
    if spec.get('law')=='quantile':
        obj['qr']=[QuantileRegressor(quantile=q,alpha=.005,solver='highs').fit(z,y) for q in [.1,.25,.50,.75,.9]]
    return obj


def location(obj,x):
    return obj['estimator'].predict(obj['scale'].transform(x)@obj['transform'])


def predict(obj,x,residual,valid_risk,valid_rotation):
    means=location(obj,x);history=obj['pool'];mode=obj['spec'].get('law','empirical');result=[]
    risk=x.p_rv21.to_numpy();threshold=np.median(valid_risk)
    rot=x['r_bank_change'].to_numpy() if 'r_bank_change' in x else np.zeros(len(x))
    rot_cut=np.nanmedian(abs(valid_rotation)) if np.isfinite(valid_rotation).any() else 0
    components=(np.arange(301)+.5)/301
    if mode=='quantile':
        design=obj['scale'].transform(x)@obj['transform'];qs=np.array([q.predict(design) for q in obj['qr']]).T
    for j,mean in enumerate(means):
        atoms=mean+residual;res_w=np.full(len(residual),1/len(residual))
        if mode=='student':
            sigma=np.sqrt(.5*np.mean(residual**2)+.5*np.var(history))*np.sqrt(3/5)
            atoms=mean+max(sigma,.001)*t.ppf(components,df=5);res_w=np.full(len(atoms),1/len(atoms))
        elif mode in ['risk','factor']:
            include=(valid_risk>threshold)==(risk[j]>threshold) if mode=='risk' else (abs(valid_rotation)>rot_cut)==(abs(rot[j])>rot_cut)
            if include.sum()>=8:res_w=.55*res_w+.45*include/include.sum()
        elif mode=='quantile':
            atoms=np.interp(components,[.1,.25,.50,.75,.9],np.sort(qs[j]));res_w=np.full(len(atoms),1/len(atoms))
        d=Distribution(np.r_[np.maximum(atoms,-.999999),history],np.r_[.65*res_w,np.full(len(history),.35/len(history))])
        result.append(d)
    return result
