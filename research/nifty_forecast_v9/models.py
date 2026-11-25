"""Regularized dynamic location models and coherent return laws."""
from scipy.stats import t
from sklearn.linear_model import Ridge
from research.nifty_forecast_v8.models import fit as fit_parent, Scale, Distribution, mix
from .common import *


def shift_size(a):
    if len(a)<70:return 0.
    old=a[-84:-21];recent=a[-21:]
    return float(np.sqrt(np.mean(((recent.mean(axis=0)-old.mean(axis=0))/np.maximum(old.std(axis=0),.25))**2)))


def fit(s,x,y,aux=None):
    mode=s.get('kind','ridge')
    if mode in ['ridge','elastic']:
        model=fit_parent(s,x,y)
        return {'parent':model,'mode':mode,'pool':y[-252:],'training':list(x.index),'spec':s}
    scale=Scale().fit(x);a=scale.transform(x);alpha=s.get('alpha',100)
    m={'mode':mode,'scale':scale,'pool':y[-252:],'training':list(x.index),'spec':s}
    if mode in ['ew','trigger','blend','expert','multitask']:
        weight=None
        if mode=='ew':weight=np.exp(-np.log(2)*(len(y)-1-np.arange(len(y)))/s.get('half_life',90));weight=weight/weight.mean()
        m['ridge']=Ridge(alpha=alpha).fit(a,y,sample_weight=weight)
        if mode in ['trigger','blend']:
            m['shift']=shift_size(a);m['short']=Ridge(alpha=alpha).fit(a[-126:],y[-126:]);m['short_weight']=.5 if mode=='blend' else (.60 if m['shift']>.75 else .15)
        if mode=='expert':
            key=s.get('gate','s_vol');vals=x[key].to_numpy();threshold=np.nanmedian(vals);hi=vals>threshold
            m.update(gate=key,threshold=float(threshold),experts={})
            if min(hi.sum(),(~hi).sum())>=25:
                m['experts']={True:Ridge(alpha=2*alpha).fit(a[hi],y[hi]),False:Ridge(alpha=2*alpha).fit(a[~hi],y[~hi])}
        if mode=='multitask':
            if aux is None:raise ValueError('Multitask design requires matured auxiliary endpoints')
            targets=aux.to_numpy();mu=targets.mean(axis=0);sd=targets.std(axis=0).clip(min=1e-6)
            joint=Ridge(alpha=150).fit(a,(targets-mu)/sd)
            uu,values,vv=np.linalg.svd(joint.coef_,full_matrices=False)
            shared=(uu[:,:2]*values[:2])@vv[:2]
            m['multi_beta']=shared[-1]*sd[-1];m['multi_intercept']=joint.intercept_[-1]*sd[-1]+mu[-1]
    elif mode=='kalman':
        # Small dynamic coefficient random walk. Targets arrive in endpoint order.
        a=np.c_[np.ones(len(a)),a];k=a.shape[1];b=np.zeros(k);b[0]=y.mean()
        noise=max(np.var(y),1e-6);cov=np.eye(k)*noise/40;cov[0,0]=noise/10
        evolution=np.eye(k)*noise*s.get('process',.00025)/k
        for xx,yy in zip(a,y):
            cov=cov+evolution;innov=cov@xx;gain=innov/(noise+xx@innov)
            b=b+gain*(yy-xx@b);cov=cov-np.outer(gain,innov);cov=(cov+cov.T)/2
        m.update(beta=b,covariance=cov,process_variance=float(np.trace(evolution)))
    else:raise ValueError(mode)
    return m


def info(m):
    if 'parent' in m:
        p=m['parent'];est=p['estimator'];scale=p['scale']
        return scale.cols,p['transform']@est.coef_,float(est.intercept_)
    s=m['scale']
    if m['mode']=='kalman':return s.cols,m['beta'][1:],float(m['beta'][0])
    if m['mode']=='multitask':return s.cols,m['multi_beta'],float(m['multi_intercept'])
    return s.cols,m['ridge'].coef_,float(m['ridge'].intercept_)


def location(m,x):
    if 'parent' in m:
        p=m['parent'];return p['estimator'].predict(p['scale'].transform(x)@p['transform'])
    a=m['scale'].transform(x)
    if m['mode']=='kalman':return np.c_[np.ones(len(a)),a]@m['beta']
    pred=m['ridge'].predict(a)
    if m['mode'] in ['trigger','blend']:
        w=m['short_weight'];pred=(1-w)*pred+w*m['short'].predict(a)
    if m.get('experts'):
        high=x[m['gate']].to_numpy()>m['threshold'];pred=.6*pred+.4*np.where(high,m['experts'][True].predict(a),m['experts'][False].predict(a))
    if m['mode']=='multitask':pred=.5*pred+.5*(a@m['multi_beta']+m['multi_intercept'])
    return pred


def laws(m,x,residual,validation_vol,validation_state=None):
    means=location(m,x);pool=m['pool'];mode=m['spec'].get('law','empirical');values=[]
    historical=Distribution(pool)
    for j,mean in enumerate(means):
        if mode=='history':values.append(historical);continue
        w=np.full(len(residual),1/len(residual));a=mean+residual
        if mode in ['student','student_scale']:
            scale=np.sqrt(.5*np.mean(residual**2)+.5*np.var(pool))*np.sqrt(3/5)
            ratio=np.clip(x.p_rv21.iloc[j]/np.nanmedian(validation_vol),.7,1.5) if mode=='student_scale' else 1
            a=mean+max(scale,.001)*ratio*t.ppf((np.arange(301)+.5)/301,df=5);w=np.full(len(a),1/len(a))
        elif mode in ['risk','global_risk']:
            var=validation_vol if mode=='risk' else validation_state
            current=x.p_rv21.iloc[j] if mode=='risk' else x.q_global_shock.iloc[j]
            threshold=np.nanmedian(var);near=(var>threshold)==(current>threshold)
            if near.sum()>=8:w=.50*w+.50*near/near.sum()
        d=Distribution(np.r_[np.maximum(a,-.999999),pool],np.r_[.65*w,np.full(len(pool),.35/len(pool))]);values.append(d)
    return values
