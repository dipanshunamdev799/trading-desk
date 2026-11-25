"""Training-only feature transforms and regularized endpoint laws."""
from dataclasses import dataclass
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from scipy.stats import t
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import SparsePCA
from sklearn.linear_model import Ridge, ElasticNet, HuberRegressor, BayesianRidge, QuantileRegressor
from sklearn.preprocessing import SplineTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from research.nifty_forecast_v5.models import Scale
from research.nifty_forecast_v6.engine import Distribution, mix, cross_abs
from research.nifty_forecast_v6.forensics import GROUPS
from .common import *


def families(columns):
    return [next((k for k,fn in GROUPS.items() if fn(c)), 'OTHER') for c in columns]


def clusters(a, threshold=.25):
    c = np.nan_to_num(np.corrcoef(a,rowvar=False))
    c = np.clip(c,-1,1)
    dist = 1-abs(c)
    np.fill_diagonal(dist,0)
    tree = linkage(squareform(dist,checks=False),method='average')
    result = fcluster(tree,t=threshold,criterion='distance')
    return [np.flatnonzero(result == j) for j in sorted(set(result))], c, tree


def representation(spec, scale, a):
    mode = spec.get('rep','raw')
    columns = scale.cols
    sector = np.array([i for i,c in enumerate(columns) if c.startswith('i_') and c.endswith(('_rel5','_rel21'))])
    other = np.setdiff1d(np.arange(len(columns)),sector)
    w = np.eye(len(columns))
    groups = families(columns)
    info = {'mode':mode,'columns':columns,'clusters':[]}
    if mode in ['defensive','defense_banks']:
        for key in (['DEFENSIVE','BANKS'] if mode=='defense_banks' else ['DEFENSIVE']):
            ids = [j for j,label in enumerate(groups) if key==label]
            if ids:w[ids,ids] /= np.sqrt(len(ids))
    if mode in ['duplicate','duplicate_balanced']:
        ids = [j for j,label in enumerate(groups) if label=='DEFENSIVE']
        if mode=='duplicate_balanced':w[ids,ids] /= np.sqrt(2)
        w = np.c_[w,w[:,ids]]
    if mode in ['prune','representative','cluster_mean','cluster_balance','factor_groups']:
        cluster_sample = a[:,sector]
        if mode=='factor_groups':
            labels = [groups[i] for i in sector]
            assigned = [np.flatnonzero(np.array(labels)==label) for label in dict.fromkeys(labels)]
            cor = np.nan_to_num(np.corrcoef(cluster_sample,rowvar=False))
        else:
            assigned,cor,_ = clusters(cluster_sample)
        info['clusters'] = [[columns[sector[i]] for i in group] for group in assigned]
        if mode=='cluster_balance':
            for group in assigned:w[sector[group],sector[group]]/=np.sqrt(len(group))
        elif mode=='prune':
            keep=[]
            for i in range(len(sector)):
                if not any(abs(cor[i,k])>=.9 for k in keep):keep.append(i)
            w = w[:,np.r_[other,sector[keep]]]
        else:
            weights = []
            for group in assigned:
                medoid = group[np.argmax(abs(cor[np.ix_(group,group)]).sum(axis=1))]
                coeff = np.zeros(len(columns))
                if mode=='representative':coeff[sector[medoid]]=1
                else:coeff[sector[group]] = np.where(cor[group,medoid]<0,-1,1)/len(group)
                weights.append(coeff)
            w = np.column_stack([w[:,other],*weights])
    if mode in ['pca','pca_roll','pca_lw','pca_white','sparse_pca']:
        subset = a[-126:,sector] if mode=='pca_roll' else a[:,sector]
        cov = np.cov(subset,rowvar=False,bias=True)
        if mode=='pca_lw':
            lw = LedoitWolf().fit(subset)
            cov = lw.covariance_
            info['shrinkage'] = float(lw.shrinkage_)
        values, vectors = np.linalg.eigh(cov)
        ids = np.argsort(values)[-6:][::-1]
        v = vectors[:,ids]
        if mode in ['pca_white','pca_lw']:v = v/np.sqrt(np.maximum(values[ids],.05))
        if mode=='sparse_pca':
            sparse = SparsePCA(n_components=6,alpha=1.,max_iter=100,tol=1e-5,random_state=SEED).fit(subset)
            components = sparse.components_
            v = components.T @ np.linalg.inv(components @ components.T+.01*np.eye(len(components)))
            info['sparse_nonzero'] = int(np.count_nonzero(components))
        w = np.zeros((len(columns),len(other)+v.shape[1]))
        w[other,np.arange(len(other))]=1
        w[sector,len(other):]=v
        info['eigenvalues'] = values[::-1].tolist()
    return w,info


@dataclass
class GroupLasso:
    coef_: np.ndarray
    intercept_: float

    def predict(self, x):
        return x@self.coef_+self.intercept_


def group_lasso(a,y,labels):
    """Proximal gradient for average squared loss + group penalty + L2 shrinkage."""
    center = a.mean(axis=0)
    X = a-center
    Y = y-y.mean()
    groups = [np.flatnonzero(np.array(labels)==g) for g in dict.fromkeys(labels)]
    beta = np.zeros(a.shape[1])
    step = 1/(np.linalg.norm(X,ord=2)**2/len(y)+.1)
    for iteration in range(1200):
        update = beta-step*(X.T@(X@beta-Y)/len(y)+.1*beta)
        for ids in groups:
            scale = max(0.,1-(step*.001*np.sqrt(len(ids)))/max(np.linalg.norm(update[ids]),1e-12))
            update[ids] *= scale
        if np.linalg.norm(update-beta)<1e-9:
            return GroupLasso(update,float(y.mean()-center@update))
        beta=update
    raise RuntimeError('Group Lasso reached the registered iteration cap')


def fit(spec,x,y):
    scale = Scale().fit(x)
    a = scale.transform(x)
    transform, info = representation(spec,scale,a)
    z = a@transform
    kind = spec.get('kind','ridge')
    alpha = spec.get('alpha',100)
    extra = {}
    if kind=='group_lasso':
        estimator = group_lasso(z,y,families(scale.cols))
    else:
        estimator = Ridge(alpha=alpha)
        if kind=='elastic':estimator = ElasticNet(alpha=.0006,l1_ratio=.3,max_iter=8000)
        if kind=='bayes':estimator = BayesianRidge()
        if kind=='huber':estimator = HuberRegressor(alpha=10,epsilon=1.35,max_iter=1500)
        if kind=='forest':estimator = RandomForestRegressor(n_estimators=48,max_depth=3,min_samples_leaf=35,max_features=.8,n_jobs=1,random_state=SEED)
        if kind=='boost':estimator = HistGradientBoostingRegressor(max_iter=55,max_leaf_nodes=4,max_depth=2,min_samples_leaf=32,l2_regularization=5,learning_rate=.05,random_state=SEED)
        if kind=='gam':
            keys=np.arange(min(10,z.shape[1]));extra['spline'] = SplineTransformer(n_knots=3,degree=2,include_bias=False).fit(z[:,keys]);extra['spline_keys']=keys
            z = np.c_[z,extra['spline'].transform(z[:,keys])]
        if kind=='interaction':
            z = np.c_[z,z[:,0]*z[:,-1], z[:,2]*z[:,-2]]
        estimator.fit(z,y)
        if kind=='residual_boost':
            extra['residual_boost'] = HistGradientBoostingRegressor(max_iter=35,max_leaf_nodes=4,max_depth=2,min_samples_leaf=45,l2_regularization=8,learning_rate=.035,random_state=SEED).fit(z,y-estimator.predict(z))
        if kind=='experts':
            risk = x.p_rv21.to_numpy(); threshold=np.median(risk);extra['threshold']=threshold
            extra['high'] = Ridge(alpha=alpha*2).fit(z[risk>threshold],y[risk>threshold])
            extra['low'] = Ridge(alpha=alpha*2).fit(z[risk<=threshold],y[risk<=threshold])
    if spec.get('law')=='quantile':
        extra['quantiles'] = [QuantileRegressor(quantile=p,alpha=.005,solver='highs').fit(z,y) for p in [.1,.25,.5,.75,.9]]
    return {'spec':spec,'scale':scale,'transform':transform,'estimator':estimator,'pool':y[-252:], 'info':info,**extra}


def design(model,x):
    z = model['scale'].transform(x)@model['transform']
    if 'spline' in model:z = np.c_[z,model['spline'].transform(z[:,model['spline_keys']])]
    if model['spec'].get('kind')=='interaction':z = np.c_[z,z[:,0]*z[:,-1],z[:,2]*z[:,-2]]
    return z


def location(model,x):
    z = design(model,x)
    mu = model['estimator'].predict(z)
    if 'residual_boost' in model:mu += .5*model['residual_boost'].predict(z)
    if 'threshold' in model:
        high = x.p_rv21.to_numpy()>model['threshold']
        mu = .6*mu+.4*np.where(high,model['high'].predict(z),model['low'].predict(z))
    return mu


def laws(model,x,residual,validation_risk,tilt=0.):
    mu = location(model,x)
    pool = model['pool']
    mode = model['spec'].get('law','empirical')
    z = design(model,x) if mode=='quantile' else None
    risk = x.p_rv21.to_numpy()
    quant = np.array([m.predict(z) for m in model['quantiles']]).T if z is not None else None
    result=[]
    for i,mean in enumerate(mu):
        if mode=='student':
            sigma=np.sqrt(.5*np.mean(residual**2)+.5*np.var(pool))*np.sqrt(3/5)
            atoms=mean+max(sigma,.001)*t.ppf((np.arange(301)+.5)/301,df=5)
        elif mode=='risk_scaled':
            ratio=np.clip(risk[i]/np.median(validation_risk),.65,1.6)
            atoms=mean+residual*ratio
        elif mode=='quantile':
            atoms=np.interp((np.arange(201)+.5)/201,[.1,.25,.5,.75,.9],np.sort(quant[i]))
        else:
            atoms=mean+residual
        law = Distribution(np.r_[np.maximum(atoms,-.999999),pool],np.r_[np.full(len(atoms),.65/len(atoms)),np.full(len(pool),.35/len(pool))])
        if tilt:
            law=Distribution(law.a,law.w*np.exp(tilt*(law.a>0)))
        result.append(law)
    return result
