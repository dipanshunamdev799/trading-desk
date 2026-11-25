"""V6 estimators and coherent endpoint laws, guarded before every fit."""
from .common import *
from research.nifty_forecast_v5.models import Scale
from research.nifty_forecast_v4.distributions import Distribution
from sklearn.linear_model import Ridge,ElasticNet,HuberRegressor,BayesianRidge,QuantileRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import SplineTransformer,RobustScaler
from scipy.stats import t,norm
import lightgbm as lgb

def validate(x,y,labels,cutoff):
    scope(x.index)
    allowed=set()
    for name in ['native-reference.csv','liquidity-reference.csv','deep-features.csv','global-reference.csv','state-features.csv','mediator-features.csv']:
        p=OUT/name
        if p.exists():allowed.update(pd.read_csv(p,nrows=0).columns[1:])
    if set(x.columns)-allowed:raise ValueError('UNREGISTERED_FEATURE_COLUMN')
    if not len(x) or not np.isfinite(y).all():raise ValueError('INVALID_TRAINING_LABEL')
    l=labels.loc[x.index]
    if not (l.endpoint.notna()&(l.endpoint<cutoff)&l['return'].notna()).all():raise ValueError('UNMATURED_OR_EMBARGO_VIOLATION')
    if np.isinf(x.to_numpy(float)).any():raise ValueError('INFINITE_FEATURE')
    for c,stamps in x.attrs.get('available_at',{}).items():
        if c not in x:continue
        for day,stamp in zip(x.index,stamps):
            d=x.attrs.get('decisions',{}).get(day,pd.Timestamp(day,tz='Asia/Kolkata')+pd.Timedelta(days=1,hours=9,minutes=10))
            if pd.Timestamp(stamp)>pd.Timestamp(d):raise ValueError('FUTURE_FEATURE_AVAILABILITY')

def fit(spec,x,labels,cutoff):
    y=labels.loc[x.index,'return'].to_numpy();validate(x,y,labels,cutoff)
    model={'spec':spec,'pool':y[-252:],'y':y,'training_dates':list(x.index)}
    if spec.get('kind')=='empirical':return model
    if spec.get('kind')=='experts':
        model['base']=fit({'kind':'ridge','alpha':100},x,labels,cutoff);model['threshold']=float(x.p_rv21.median());gate=x.p_rv21>model['threshold'] if spec['gate']=='volatility' else abs(x.p_ret21)>x.p_rv21*np.sqrt(21);model['experts']={}
        for value in [False,True]:
            xx=x[gate==value]
            if len(xx)>=40:model['experts'][value]=fit({'kind':'ridge','alpha':100},xx,labels,cutoff)
        return model
    scale=Scale().fit(x);a=scale.transform(x);model['scale']=scale
    if spec.get('preprocess')=='no_clip':
        arr=x[scale.cols].to_numpy(float);a=(np.where(np.isfinite(arr),arr,scale.med)-scale.mu)/scale.sd
    if spec.get('preprocess')=='robust':
        arr=x[scale.cols].to_numpy(float);arr=np.where(np.isfinite(arr),arr,scale.med);model['robust']=RobustScaler().fit(arr);a=np.clip(model['robust'].transform(arr),-5,5)
    if spec.get('residualize_size'):
        size=np.array([i for i,c in enumerate(scale.cols) if 'midcap' in c.lower() or 'smallcap' in c.lower()]);rest=np.array([i for i in range(a.shape[1]) if i not in size])
        projection=Ridge(alpha=100).fit(a[:,rest],a[:,size]);model['size_projection']={'model':projection,'size':size,'rest':rest};a[:,size]-=projection.predict(a[:,rest])
    if spec.get('defensive_pc') or spec.get('defensive_norm'):
        indices=np.array([i for i,c in enumerate(scale.cols) if any(n in c for n in ['i_nifty_fmcg','i_nifty_pharma','i_idx_NIFTY_HEALTHCARE'])]);rest=np.array([i for i in range(a.shape[1]) if i not in indices])
        if spec.get('defensive_pc'):
            from sklearn.decomposition import PCA
            pc=PCA(n_components=1,whiten=True).fit(a[:,indices]);model['defensive_pc']={'pc':pc,'indices':indices,'rest':rest};a=np.column_stack([a[:,rest],pc.transform(a[:,indices])])
        else:model['defensive_norm']=indices;a[:,indices]/=np.sqrt(len(indices))
    kind=spec.get('kind','ridge');alpha=spec.get('alpha',100)
    if kind=='elastic':estimator=ElasticNet(alpha=.001,l1_ratio=.5,max_iter=5000,random_state=SEED)
    elif kind=='huber':estimator=HuberRegressor(alpha=10,epsilon=1.35,max_iter=1000)
    elif kind=='bayes':estimator=BayesianRidge()
    elif kind=='forest':estimator=RandomForestRegressor(n_estimators=64,max_depth=3,min_samples_leaf=30,max_features=.7,n_jobs=1,random_state=SEED)
    elif kind=='spline':
        transform=SplineTransformer(n_knots=3,degree=2,include_bias=False).fit(a);model['transform']=transform;a=transform.transform(a);estimator=Ridge(alpha=100)
    elif kind in ['lgbm','lgbm_quantile']:
        params={'objective':'regression','verbosity':-1,'max_depth':2,'num_leaves':4,'min_data_in_leaf':40,'learning_rate':.04,'lambda_l2':10,'num_threads':1,'deterministic':True,'force_col_wise':True,'seed':SEED}
        model['estimator']=lgb.train(params,lgb.Dataset(a,label=y),num_boost_round=80)
        if kind=='lgbm_quantile':model['quantiles']=[lgb.train({**params,'objective':'quantile','alpha':q},lgb.Dataset(a,label=y),num_boost_round=80) for q in [.1,.25,.5,.75,.9]]
        return model
    elif kind=='quantile':
        estimator=Ridge(alpha=100);model['quantiles']=[QuantileRegressor(quantile=q,alpha=.005,solver='highs').fit(a,y) for q in [.1,.25,.5,.75,.9]]
    else:estimator=Ridge(alpha=alpha)
    model['estimator']=estimator.fit(a,y)
    if kind=='forest':model['train_leaves']=estimator.apply(a)
    return model
def matrix(model,x):
    s=model['scale'];a=s.transform(x)
    if model['spec'].get('preprocess')=='no_clip':
        arr=x[s.cols].to_numpy(float);a=(np.where(np.isfinite(arr),arr,s.med)-s.mu)/s.sd
    if 'robust' in model:
        arr=x[s.cols].to_numpy(float);a=np.clip(model['robust'].transform(np.where(np.isfinite(arr),arr,s.med)),-5,5)
    if 'transform' in model:a=model['transform'].transform(a)
    if 'defensive_pc' in model:
        p=model['defensive_pc'];a=np.column_stack([a[:,p['rest']],p['pc'].transform(a[:,p['indices']])])
    if 'defensive_norm' in model:a[:,model['defensive_norm']]/=np.sqrt(len(model['defensive_norm']))
    if 'size_projection' in model:
        p=model['size_projection'];a[:,p['size']]-=p['model'].predict(a[:,p['rest']])
    return a
def means(model,x):
    if model['spec'].get('kind')=='empirical':return np.full(len(x),model['pool'].mean())
    if model['spec'].get('kind')=='experts':
        base=means(model['base'],x);output=base.copy();gate=x.p_rv21>model['threshold'] if model['spec']['gate']=='volatility' else abs(x.p_ret21)>x.p_rv21*np.sqrt(21)
        for value,expert in model['experts'].items():
            mask=gate.to_numpy()==value
            if mask.any():output[mask]=.5*base[mask]+.5*means(expert,x.iloc[np.where(mask)[0]])
        return output
    return model['estimator'].predict(matrix(model,x))
def predict(model,x,residual):
    mu=means(model,x);pool=model['pool'];kind=model['spec'].get('kind','ridge');a=matrix(model,x) if 'scale' in model else None;out=[]
    for j in range(len(x)):
        if kind=='empirical':d=Distribution(pool)
        elif kind=='forest':
            matches=model['train_leaves']==model['estimator'].apply(a[j:j+1])[0];w=.65*(matches/np.maximum(1,matches.sum(axis=0))).mean(axis=1)+.35/len(model['y']);d=Distribution(model['y'],w)
        else:
            if 'quantiles' in model:
                raw=np.array([est.predict(a[j:j+1])[0] for est in model['quantiles']]);q=np.sort(raw);r=np.interp((np.arange(201)+.5)/201,[.1,.25,.5,.75,.9],q)
            elif model['spec'].get('law')=='student':
                scale=np.sqrt(.5*np.mean(np.asarray(residual)**2)+.5*np.var(pool))*np.sqrt(3/5);r=mu[j]+max(scale,.001)*t.ppf((np.arange(401)+.5)/401,df=5)
            elif model['spec'].get('law')=='bayes':
                _,sd=model['estimator'].predict(a[j:j+1],return_std=True);r=mu[j]+max(float(sd[0]),.001)*norm.ppf((np.arange(401)+.5)/401)
            else:r=mu[j]+np.asarray(residual)
            atoms=np.r_[np.maximum(r,-.999999),pool];w=np.r_[np.full(len(r),.65/len(r)),np.full(len(pool),.35/len(pool))];d=Distribution(atoms,w)
        out.append(d)
    return out
def mix(a,b,w):return Distribution(np.r_[a.a,b.a],np.r_[w*a.w,(1-w)*b.w])
def cross_abs(a,b):
    pos=np.searchsorted(b.a,a.a,side='right');cw=np.r_[0,np.cumsum(b.w)];cv=np.r_[0,np.cumsum(b.w*b.a)]
    return float(a.w@(a.a*(2*cw[pos]-1)+cv[-1]-2*cv[pos]))
