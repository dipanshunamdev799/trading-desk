"""Same-remaining-horizon estimation and controlled fresh-information ablations."""
from dataclasses import dataclass

from .common import *
from .data import Daily, PRICE, RISK, DOMESTIC, DERIVATIVES, GLOBAL, LIQUIDITY

GROUPS={'domestic':DOMESTIC,'surface':DERIVATIVES,'global':GLOBAL,'liquidity':LIQUIDITY}
NESTS={'refit':('domestic','surface','global','liquidity'),'domestic':('domestic',),
       'derivatives_first':('surface',),'full':('domestic','surface','global','liquidity')}


def clone_columns(a):
    active=[]; seen=set()
    for j in range(a.shape[1]):
        col=a[:,j]
        if np.isfinite(col).sum()<14:
            continue
        key=np.nan_to_num(col,nan=7.e120).tobytes()
        if key in seen:
            continue
        seen.add(key)
        active.append(j)
    return np.array(active,int)


@dataclass
class Fitted:
    active: np.ndarray
    center: np.ndarray
    sd: np.ndarray
    median: np.ndarray
    coefficient: np.ndarray

    def values(self,b):
        b=b[...,self.active]
        b=np.where(np.isfinite(b),b,self.median)
        z=np.clip((b-self.center)/self.sd,-5,5)
        return self.coefficient[0]+z@self.coefficient[1:]

    def receipt(self,names):
        return dict(columns=[names[i] for i in self.active],center=self.center.tolist(),sd=self.sd.tolist(),
                    median=self.median.tolist(),parameters=self.coefficient.tolist())


def fit(a,y,penalty,rng=None,permuted_columns=None):
    chosen=clone_columns(a)
    a=a[:,chosen]
    med=np.nanmedian(a,axis=0) if a.shape[1] else np.empty(0)
    clean=np.where(np.isfinite(a),a,med)
    center=clean.mean(axis=0); sd=clean.std(axis=0).clip(.000001)
    z=((clean-center)/sd).clip(-5,5)
    if rng is not None:
        permuted_columns=np.asarray(permuted_columns,bool)[chosen]
        chunks=np.array_split(np.arange(len(a)),max(2,len(a)//11))
        order=np.concatenate([chunks[i] for i in rng.permutation(len(chunks))])
        z[:,permuted_columns]=z[order][:,permuted_columns]
    design=np.column_stack([np.ones(len(a)),z])
    regular=np.eye(design.shape[1])*penalty
    regular[0,0]=1.e-10
    coef=np.linalg.solve(design.T@design+regular,design.T@y)
    return Fitted(chosen,center,sd,med,coef)


class RevisionDesign:
    def __init__(self,d:Daily,iv):
        self.d=d
        self.iv=iv.pivot(index='asof',columns='remaining',values='iv').reindex(d.sessions).to_numpy()
        self.iv=np.clip(self.iv,.035,.70)
        self.logp=np.log(d.prices.close.to_numpy())
        self.base=d.features.reindex(columns=tuple(dict.fromkeys(PRICE+RISK))).to_numpy()
        self.groups={k:d.features.reindex(columns=v).to_numpy() for k,v in GROUPS.items()}
        self.cache={}
        self.responses={}
        diff=np.diff(self.logp,prepend=self.logp[0])
        acc=np.cumsum(diff*diff)
        for remain in range(1,22):
            z=self.iv[:,remain-1]
            y=np.full((len(z),2),np.nan)
            y[:-remain,0]=(self.logp[remain:]-self.logp[:-remain])/(z[:-remain]*np.sqrt(remain/252.))
            v=np.sqrt(252*(acc[remain:]-acc[:-remain])/remain)
            y[:-remain,1]=np.log(np.maximum(v,.009)/z[:-remain])
            self.responses[remain]=y

    def columns(self,stage,remain,nest):
        key=(stage,remain,nest)
        if key in self.cache:
            return self.cache[key]
        n=len(self.logp)
        previous=np.maximum(0,np.arange(n)-stage)
        ret=self.logp-self.logp[previous]
        risk=self.iv[:,remain-1]
        blocks=[self.base,risk[:,None],ret[:,None]]
        names=list(dict.fromkeys(PRICE+RISK))+['remaining_atm','observed_prefix_logreturn']
        spans={}
        for group in NESTS[nest]:
            a=self.groups[group]
            start=len(names)
            blocks.append(a)
            names.extend(GROUPS[group])
            if nest!='refit':
                blocks.append(a-a[previous])
                names.extend('revision_'+s for s in GROUPS[group])
            spans[group]=slice(start,len(names))
        features=np.column_stack(blocks)
        result=(features,names,spans)
        self.cache[key]=result
        return result

    def fit_part(self,i,h,k,name):
        remain=h-k
        x,names,spans=self.columns(k,remain,name)
        last=i-remain
        first=max(k,last-HIST)
        t=np.arange(first,last)
        assert len(t)>=44 and int(t[-1])+remain<i
        y=self.responses[remain][t]
        assert np.isfinite(y).all()
        model=fit(x[t],y,180 if name=='refit' else 225)
        current=x[i]
        score=model.values(current)
        note=dict(model=name,training_first=self.d.sessions[t[0]],training_last=self.d.sessions[t[-1]],
                  last_outcome=self.d.sessions[t[-1]+remain],train_n=len(t),**model.receipt(names))
        variants={name:score}
        s=i-k
        if name=='domestic':
            stale=current.copy()
            a=self.groups['domestic'][s]
            offset=spans['domestic']
            stale[offset]=np.r_[a,np.zeros_like(a)]
            variants['domestic_stale']=model.values(stale)
        if name=='full':
            for group in ('surface','global'):
                stale=current.copy()
                a=self.groups[group][s]
                stale[spans[group]]=np.r_[a,np.zeros_like(a)]
                variants['full_stale_'+group]=model.values(stale)
            delayed=current.copy()
            noise=current.copy()
            rng=np.random.default_rng(SEED+h*100000+i*31+k)
            d=max(s,i-5)
            for group,off in spans.items():
                values=self.groups[group]
                a=values[d]
                delayed[off]=np.r_[a,a-values[s]]
                aa=x[t,off]
                std=np.nanstd(aa,axis=0)
                aa0=delayed[off]
                noise[off]=aa0+np.nan_to_num(std,nan=0.)*.55*rng.standard_normal(len(aa0))
            variants['full_delayed']=model.values(delayed)
            variants['full_noise']=model.values(noise)
            perm_cols=np.zeros(x.shape[1],bool)
            for k0 in ('surface','global','liquidity'):
                perm_cols[spans[k0]]=True
            f=fit(x[t],y,225,rng,perm_cols)
            variants['full_permuted']=f.values(current)
            note['permuted_parameters']=f.receipt(names)
        return variants,note

    def models(self,i,h,k):
        r=h-k
        raw=self.iv[i,r-1]
        result={}
        receipts=[]
        for name in NESTS:
            variants,note=self.fit_part(i,h,k,name)
            for tag,vector in variants.items():
                mu=float(np.clip(vector[0]*.60,-.65,.65)*raw*np.sqrt(r/252.))
                risk=float(raw*np.exp(np.clip(.42*vector[1],-.38,.38)))
                result[tag]=(mu,risk)
            receipts.append(note)
        return result,receipts
