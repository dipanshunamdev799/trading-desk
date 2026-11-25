"""Small chronological estimators and proper scores shared by V20 experiments."""
from itertools import chain
from scipy.special import expit,logit
from scipy.stats import spearmanr
from .common import *
from research.nifty_forecast_v16.model import fit
from research.nifty_forecast_v19.evidence import disjoint

def matrix(f,fields):
    return f.reindex(columns=list(dict.fromkeys(fields))).to_numpy(float)

def timed(ends,cut,i,response,n=140,minimum_gap=None):
    threshold=cut[i] if minimum_gap is None else minimum_gap
    return np.flatnonzero((np.arange(len(ends))<i)&(ends<threshold)&np.isfinite(response))[-n:]

def fit_slope(a,y,x,penalty=160):
    """Return a feature-only, centered ridge estimate without its intercept."""
    m=fit(a,y,penalty)
    return float(m.values(x)-m.coefficient[0]),m

def center_projection(a,y,x):
    m=fit(a,y,150)
    return float(.67*m.values(x)+.33*np.median(y))

def curves(atoms,shifts,truth,risk=False):
    """Score laws obtained by adding each shift to sorted log atoms."""
    base=np.asarray(atoms).reshape(1,-1)
    delta=np.asarray(shifts).reshape(-1,1)
    forecast=np.exp(base+delta) if risk else np.expm1(base+delta)
    target=np.exp(truth) if risk else np.expm1(truth)
    a=forecast.shape[1]
    coefficient=(2*np.arange(a)-a+1)/a**2
    mae=np.abs(forecast-target).mean(axis=1)
    crps=mae-np.einsum('ij,j->i',forecast,coefficient)
    y=forecast.mean(axis=1)
    p=((forecast>0).sum(axis=1)+.5)/(a+1)
    decision=float(target>0)
    ix=(int(.1*a),int(.5*a),int(.9*a))
    lo,mid,hi=[forecast[:,j] for j in ix]
    if risk:
        v=(np.maximum(target,.005)/np.maximum(y,.005))**2
        principal=v-np.log(v)-1
        log=np.full(len(y),np.nan)
    else:
        principal=(p-decision)**2
        log=-np.log(np.where(decision,p,1-p))
    return np.column_stack([principal,crps,log,y,mid,p,lo,hi,(lo<=target)&(target<=hi),np.abs(y-target),np.square(y-target)])

MEASURES=('primary','crps','log_loss','mean','median','p','lo','hi','covered','mae','se')

def center_book(frame,y,end,cut,n=140,min_train=45):
    x=matrix(frame,('prior_ret5','prior_ret21','rolling_rv5','trailing_vol'))
    center=np.full(len(y),np.nan)
    atoms=np.full((len(y),len(Q)),np.nan)
    used=np.zeros(len(y),int)
    last=np.full(len(y),'',dtype='U10')
    for i in range(len(y)):
        tr=timed(end,cut,i,y,n)
        if len(tr)<min_train:continue
        center[i]=center_projection(x[tr],y[tr],x[i])
        errors=y[tr]-center[tr]
        errors=errors[np.isfinite(errors)]
        if len(errors)<30:errors=y[tr]-np.median(y[tr])
        atoms[i]=center[i]+np.quantile(errors-np.median(errors),Q)
        used[i]=len(tr)
        last[i]=max(end[tr])
    return center,atoms,used,last

def variant_matrix(frame,fields,calendar,ages=AGES):
    core=frame.reindex(columns=fields).reindex(calendar)
    out={}
    for age in ages:
        if age=='fresh':v=core
        elif age=='smooth5':v=core.rolling(5,min_periods=3).mean()
        else:v=core.shift(int(age[3:]))
        out[age]=v.reindex(frame.index).to_numpy(float)
    return out

def rank(x,y):
    a,b=np.asarray(x,float),np.asarray(y,float)
    use=np.isfinite(a)&np.isfinite(b)
    if use.sum()<8 or np.std(a[use])<1.e-10 or np.std(b[use])<1.e-10:return np.nan
    return float(spearmanr(a[use],b[use]).statistic)

def block_counts(n,block,draws,rng):
    starts=rng.integers(n,size=(draws,int(np.ceil(n/block)),1))
    ids=((starts+np.arange(block))%n).reshape(draws,-1)[:,:n]
    w=np.zeros((draws,n),dtype=float)
    i=np.broadcast_to(np.arange(draws)[:,None],ids.shape)
    np.add.at(w,(i,ids),1.)
    return w

def block_intervals(a,block=21,draws=1500,seed=SEED):
    """Rows are consecutive eligible calendar observations, columns paired losses."""
    a=np.asarray(a,float)
    if a.ndim==1:a=a[:,None]
    present=np.isfinite(a)
    n=present.sum(axis=0)
    if len(a)<4:return None
    w=block_counts(len(a),block,draws,np.random.default_rng(seed))
    total=w@present
    bs=np.divide(w@np.nan_to_num(a),total,out=np.full(total.shape,np.nan),where=total>0)
    lo,hi=np.nanquantile(bs,[.025,.975],axis=0)
    m=np.nanmean(a,axis=0)
    sd=np.nanstd(bs,axis=0,ddof=1)
    z=np.abs(bs-m)/np.where(sd>1.e-12,sd,np.inf)
    maxstat=np.nanquantile(np.nanmax(z,axis=1),.95)
    return pd.DataFrame(dict(n=n,gain=m,low=lo,high=hi,adjusted_low=m-maxstat*sd,adjusted_high=m+maxstat*sd,sd=sd))

def direction_weights(a,w,p):
    """Change sign mass on a complete empirical law, preserving conditional shapes."""
    yes=a>0
    old=float(w[yes].sum())
    if old<1.e-9 or old>1-1.e-9:return w.copy()
    p=float(np.clip(p,.02,.98))
    nw=np.where(yes,w*(p/old),w*((1-p)/(1-old)))
    return nw/nw.sum()

def blend_laws(a,w,b,v,share):
    # Identical experts should return exactly the same law and score.
    if np.array_equal(a,b) and np.array_equal(w,v):
        return a.copy(),w.copy()
    return np.r_[a,b],np.r_[(1-share)*w,share*v]

def sample_law(a,w,q=Q):
    i=np.argsort(a)
    p=np.cumsum(w[i])
    return a[i][np.searchsorted(p,q,side='left').clip(0,len(a)-1)]

def logit_shift(p,correction):
    return float(expit(logit(np.clip(p,.02,.98))+np.clip(correction,-.45,.45)))

def weighted_store(file,entries):
    size=np.array([len(a) for a,w in entries])
    np.savez_compressed(OUT/file,atoms=np.concatenate([a for a,w in entries]),
                        weights=np.concatenate([w for a,w in entries]),offsets=np.r_[0,np.cumsum(size)])

