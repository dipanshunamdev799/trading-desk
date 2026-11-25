"""Small, reusable forecast estimators and proper scores for dated session tests."""
from scipy.special import expit, logit
from scipy.stats import t as student
from .common import *
from research.nifty_forecast_v15.fitting import fit

Q=(np.arange(160)+.5)/160
STUDENT=student.ppf(Q,6)*np.sqrt(4/6)


def history(days,events,y,i,extra=None,n=HIST):
    good=(events<days[i])&(np.arange(len(days))<i)&np.isfinite(y)
    if extra is not None:
        good&=extra
    return np.flatnonzero(good)[-n:]


def logistic_offset(a,y,base,penalty=85):
    """Estimates a small regularized feature correction on historical labels."""
    std=fit(a,y,penalty)
    t=a[:,std.active]
    z=(np.where(np.isfinite(t),t,std.median)-std.center)/std.sd
    x=np.column_stack((np.ones(len(t)),z.clip(-5,5)))
    reg=np.diag([12.]+[penalty]*(x.shape[1]-1))
    b=np.zeros(x.shape[1])
    l=logit(np.clip(base,.006,.994))
    for _ in range(8):
        pred=expit(l+x@b)
        denom=pred*(1-pred)
        b-=np.linalg.solve((x.T*denom)@x+reg,x.T@(pred-y)+reg@b)
    return std,b


def predict_probability(fit_parameters,b,base,weight=1.):
    std,coef=fit_parameters
    a=b[std.active]
    z=(np.where(np.isfinite(a),a,std.median)-std.center)/std.sd
    return expit(logit(np.clip(base,.006,.994))+weight*(coef[0]+z.clip(-5,5)@coef[1:]))


def quantify(x,y,conversion=True):
    if conversion:
        y=np.expm1(y)
        x=np.expm1(x)
    x=np.sort(x)
    q=np.quantile(x,[.10,.50,.90])
    p=(np.sum(x>0)+.5)/(len(x)+1)
    b=(p-(y>0))**2
    l=-np.log(p if y>0 else 1-p)
    crps=np.abs(x-y).mean()-x@(2*np.arange(len(x))-len(x)+1)/len(x)**2
    m=float(x.mean())
    lower,upper=.005,.005
    a=(x<=-lower).mean();c=(x>=upper).mean()
    return dict(actual=y,p_up=p,brier=b,log_loss=l,correct=int((p>=.5)==(y>0)),mean=m,median=q[1],lo=q[0],hi=q[2],
                crps=crps,mae=abs(q[1]-y),sq_error=(m-y)**2,covered=int(q[0]<=y<=q[2]),width=q[2]-q[0],
                interval_score=q[2]-q[0]+10*(max(q[0]-y,0)+max(y-q[2],0)),p_down05=a,p_up05=c,
                p_down10=(x<=-.01).mean(),p_up10=(x>=.01).mean(),pit=(x<=y).mean(),
                down05_brier=(a-(y<=-.005))**2,up05_brier=(c-(y>=.005))**2)


def law(a,b,y,kind='ridge',penalty=95,rng=None,permuted=None,cluster=None):
    data_fit=a; response=y
    if kind=='cluster':
        # Thin volatility-event clusters chronologically with an ex-ante block phase, then combine two phases.
        assert cluster is not None
        m1=fit(a[cluster%2==0],y[cluster%2==0],penalty*.70)
        m2=fit(a[cluster%2==1],y[cluster%2==1],penalty*.70)
        loc=.70*(m1.values(b)+m2.values(b))/2
        return loc+np.quantile(y-np.median(y),Q),None
    if kind=='logistic_magnitude':
        z=int((y>0).sum())
        base=(z+.75)/(len(y)+1.5)
        pars=logistic_offset(a,(y>0).astype(float),base,72)
        p=predict_probability(pars,b,base,.85)
        h0=y[y<=0]
        h1=y[y>0]
        nh=int(np.clip(round(len(Q)*p),1,len(Q)-1))
        atoms=np.r_[np.quantile(h0,(np.arange(len(Q)-nh)+.5)/(len(Q)-nh)),np.quantile(h1,(np.arange(nh)+.5)/nh)]
        return atoms,pars[0]
    md=fit(data_fit,response,penalty,rng,permuted)
    loc=.70*float(md.values(b))
    if kind=='student':
        r=y-.70*md.values(a)
        unconditional=max((np.quantile(r,.90)-np.quantile(r,.10))/2.46,.0001)
        scales=np.log(np.maximum(abs(r),unconditional*.12)/unconditional)
        sd=fit(a,scales,penalty*1.6)
        scale=unconditional*np.clip(np.exp(.5*(sd.values(b)-np.median(scales))),.55,1.65)
        return loc+scale*STUDENT,md
    return loc+np.quantile(y-np.median(y),Q),md
