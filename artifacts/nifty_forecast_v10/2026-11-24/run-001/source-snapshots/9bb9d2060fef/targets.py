"""Target transforms and direct reconstruction of coherent endpoint laws."""
from sklearn.linear_model import LogisticRegression,Ridge
from scipy.stats import t
from .common import *
from .estimators import Distribution


def target_store(h,labels,price,broad):
    log_price=np.log(price.close);log_ret=np.log1p(labels['return'])
    k=1 if h==5 else 5
    overnight=np.log(price.open/price.close.shift());session=np.log(price.close/price.open)
    first=log_price.shift(-k)-log_price
    overnight_sum=overnight.rolling(h).sum().shift(-h);session_sum=session.rolling(h).sum().shift(-h)
    valid=(overnight_sum+session_sum).dropna()
    np.testing.assert_allclose(valid,log_ret.loc[valid.index],atol=1e-11)
    own_vol=price.close.pct_change(fill_method=None).rolling(21,min_periods=15).std().clip(lower=.001)*np.sqrt(h)
    history=np.full(len(labels),np.nan)
    for j,d in enumerate(labels.index):
        y=log_ret[labels.endpoint.notna()&(labels.endpoint<d)].iloc[-63:]
        if len(y)>=25:history[j]=y.mean()
    factor=np.log(broad.reindex(price.index)).diff(h).shift(-h)
    return pd.DataFrame({'raw':labels['return'],'log':log_ret,'vol_scale':own_vol,'conditional_offset':history,'first':first,
                         'tail':log_ret-first,'overnight':overnight_sum,'session':session_sum,'future_factor':factor},index=labels.index)


def transformed(store,kind,train):
    if kind=='raw':return store[['raw']].to_numpy(),{}
    if kind=='log':return store[['log']].to_numpy(),{}
    if kind=='vol':return (store.log/store.vol_scale).to_numpy()[:,None],{}
    if kind=='centered':return (store.log-store.conditional_offset).to_numpy()[:,None],{}
    if kind=='split':return store[['first','tail']].to_numpy(),{}
    if kind=='overnight':return store[['overnight','session']].to_numpy(),{}
    if kind=='factor':
        ten=store.loc[train,['log','future_factor']].dropna();factor=ten.future_factor.to_numpy();r=ten.log.to_numpy()
        x=factor-factor.mean();slope=float(np.clip(x@(r-r.mean())/(x@x+.015),-.5,1.5))
        return np.c_[store.log-slope*store.future_factor,store.future_factor],{'factor_beta':slope}
    if kind=='signmag':return store[['raw']].to_numpy(),{}
    raise ValueError(kind)


def inverse(a,q,kind,context):
    if kind in ['raw','signmag']:return np.maximum(a[:,0],-.999999)
    if kind=='vol':log=a[:,0]*q.vol_scale
    elif kind=='centered':log=a[:,0]+q.conditional_offset
    elif kind=='factor':log=a[:,0]+context['factor_beta']*a[:,1]
    else:log=a.sum(axis=1)
    return np.expm1(np.clip(log,-8,3))


def paired_laws(context,target_kind,store,query,outer_prediction,resids,pool,method='empirical',risk=None):
    result=[]
    for j,d in enumerate(query):
        q=store.loc[d];w=np.full(len(resids),1/len(resids));atoms=outer_prediction[j]+resids
        if method=='student':
            err=inverse(atoms,q,target_kind,context);point=float(inverse(outer_prediction[j:j+1],q,target_kind,context)[0])
            sigma=np.sqrt(.5*np.mean((err-point)**2)+.5*np.var(pool))*np.sqrt(3/5);a=point+max(sigma,.001)*t.ppf((np.arange(301)+.5)/301,df=5)
            atoms=np.maximum(a,-.999999);w=np.full(len(atoms),1/len(atoms))
        else:
            if method=='risk' and risk is not None:
                med=np.median(risk);mask=(risk>med)==(q.vol_scale>med)
                if mask.sum()>=6:w=.5*w+.5*mask/mask.sum()
            atoms=inverse(atoms,q,target_kind,context)
        result.append(Distribution(np.r_[atoms,pool],np.r_[.65*w,np.full(len(pool),.35/len(pool))]))
    return result


def sign_magnitude(model,x,y,tr,query):
    a=model['scale'].transform(x.loc[tr])@model['basis'];z=model['scale'].transform(x.loc[query])@model['basis']
    observed=y.loc[tr,'return'].to_numpy();positive=observed>0
    if min(positive.sum(),(~positive).sum())<12:raise ValueError('Insufficient observations per conditional sign')
    p=LogisticRegression(C=.06,max_iter=1000).fit(a,positive).predict_proba(z)[:,1]
    p=.65*p+.35*np.mean(positive);branch=[]
    for sign in [False,True]:
        mask=positive==sign;mag=np.log(np.maximum(abs(observed[mask]),.0001));rr=Ridge(alpha=120).fit(a[mask],mag)
        ratio=np.exp(np.clip(rr.predict(z)-mag.mean(),-.6,.6));branch.append((abs(observed[mask]),ratio))
    ds=[]
    for j,v in enumerate(p):
        low,lo=branch[0];hi,up=branch[1]
        a=np.r_[-low*lo[j],hi*up[j]];w=np.r_[np.full(len(low),(1-v)/len(low)),np.full(len(hi),v/len(hi))]
        ds.append(Distribution(np.maximum(a,-.999999),w))
    return ds


def buckets(law,realized,cuts):
    p=np.bincount(np.digitize(law.a,cuts),weights=law.w,minlength=len(cuts)+1);index=np.digitize(realized,cuts)
    d={'train_bucket_actual':int(index),'train_bucket_brier':float(np.sum((p-np.eye(len(p))[index])**2))}
    for j,value in enumerate(p):d[f'train_bucket{j}_p']=float(value)
    for j,value in enumerate(cuts):d[f'train_bucket_cut{j}']=float(value)
    return d
