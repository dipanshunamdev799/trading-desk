"""Coherent arithmetic-return laws and exact weighted proper scores."""
from .common import *
from scipy.special import logit, expit

GRID = (np.arange(129) + .5) / 129
LEVELS = np.array([.01,.025,.05,.1,.25,.5,.75,.9,.95,.975,.99])


@dataclass
class Law:
    atoms: np.ndarray
    weights: np.ndarray

    @classmethod
    def build(cls, atoms, weights=None):
        x = np.asarray(atoms, dtype=float)
        w = np.ones(len(x)) if weights is None else np.asarray(weights,dtype=float)
        assert x.ndim == w.ndim == 1 and len(x) == len(w) and len(x) and np.isfinite(x).all()
        assert np.isfinite(w).all() and np.min(w) >= 0 and w.sum() > 0
        ix = np.argsort(x[w>0],kind='stable')
        a = x[w>0][ix]
        b = w[w>0][ix]
        return cls(a,b/b.sum())

    def eq_id(self):
        a = np.round(self.atoms,12)
        q,start = np.unique(a,return_index=True)
        w = np.round(np.add.reduceat(self.weights,start),12)
        # Compression removes representation differences such as repeated atoms.
        return hashlib.sha256(np.column_stack([q+0.,w]).astype('<f8').tobytes()).hexdigest()

    def quantiles(self, q=LEVELS):
        return self.atoms[np.searchsorted(np.cumsum(self.weights),q,side='left').clip(0,len(self.atoms)-1)]

    def moments(self):
        y=float(self.weights@self.atoms)
        return y,float(self.weights@((self.atoms-y)**2))

    def positive(self):
        return float(self.weights[self.atoms>0].sum())

    def cdf(self,x,inclusive=True):
        q=self.atoms<=x if inclusive else self.atoms<x
        return float(self.weights[q].sum())

    def crps(self,y):
        return float(self.weights@np.abs(self.atoms-y)-np.sum(self.weights*self.atoms*(2*np.cumsum(self.weights)-self.weights-1)))

    def reweight_sign(self,prob):
        p=self.positive()
        if not 1.e-10 < p < 1-1.e-10:
            return self
        prob=np.clip(prob,.02,.98)
        w=self.weights*np.where(self.atoms>0,prob/p,(1-prob)/(1-p))
        return Law(self.atoms,w/w.sum())

    def transform(self,location=None,scale=1.,asymmetry=0.):
        """Apply a monotone transform in log-price units."""
        x=np.log1p(self.atoms)
        med=float(np.log1p(self.quantiles(.50)))
        deviations=x-med
        end=(med if location is None else location)+scale*deviations*np.where(deviations>=0,1.+asymmetry,1.-asymmetry)
        return Law(np.expm1(np.clip(end,-5.,2.5)),self.weights)


def mix(laws, weights=None):
    if weights is None:
        weights=np.full(len(laws),1./len(laws))
    return Law.build(np.concatenate([x.atoms for x in laws]),np.concatenate([a.weights*w for a,w in zip(laws,weights,strict=True)]))


def transport(laws,weights=None,q=GRID):
    if weights is None:
        weights=np.full(len(laws),1./len(laws))
    a=np.average(np.array([l.quantiles(q) for l in laws]),axis=0,weights=weights)
    assert np.all(np.diff(a)>=-1.e-12)
    return Law.build(a)


def logshape(law):
    lo,mid,hi=np.log1p(law.quantiles([.10,.50,.90]))
    width=max(hi-lo,.001)
    return float(mid),float(width/2.563103),float((hi+lo-2*mid)/width)


def metrics(law,y,h,pit_draw=.5):
    p=law.positive()
    mu,var=law.moments()
    q=law.quantiles()
    lo,hi=q[3],q[-4]
    tail=.02 if h==5 else .05
    d=law.cdf(-tail,False)
    u=1.-law.cdf(tail)
    inc=law.cdf(y,True);exc=law.cdf(y,False)
    s=np.clip(p,.0005,.9995)
    prob_score=(p-(y>0))**2
    quantile_loss=np.maximum(LEVELS*(y-q),(LEVELS-1)*(y-q))
    gap=np.maximum(lo-y,0.)+np.maximum(y-hi,0.)
    other=law.quantiles(GRID)
    a=dict(actual=y,p=p,mean=mu,median=q[5],var=var,brier=prob_score,crps=law.crps(y),
           log_loss=-np.log(s if y>0 else 1-s),correct=int((p>=.5)==(y>0)),mae=abs(mu-y),squared_error=(mu-y)**2,
           width80=hi-lo,cover80=int(lo<=y<=hi),interval80=hi-lo+10*gap,
           miss_low80=int(y<lo),miss_high80=int(y>hi),pinball=float(quantile_loss.mean()),
           quantile_low_loss=quantile_loss[2],quantile_high_loss=quantile_loss[-3],
           p_tail_down=d,p_tail_up=u,tail_down_brier=(d-(y<-tail))**2,tail_up_brier=(u-(y>tail))**2,
           tail_miss=int(y<q[2] or y>q[-3]),pit=exc+(inc-exc)*pit_draw,pit_left=exc,pit_right=inc,
           lower_tail_mass=float(np.mean(other<q[3])),upper_tail_mass=float(np.mean(other>q[-4])))
    return a|{f'q{str(k*100).rstrip("0").rstrip(".").replace(".","p")}':float(v) for k,v in zip(LEVELS,q,strict=True)}


def loaded(root,name):
    with np.load(root/name,allow_pickle=False) as z:
        return z['atoms'],z['weights'],z['offsets']


def piece(arr,i):
    a,w,e=arr
    return Law.build(a[e[i]:e[i+1]],w[e[i]:e[i+1]])


def store(name,laws):
    size=np.array([len(a.atoms) for a in laws])
    np.savez_compressed(OUT/name,atoms=np.concatenate([x.atoms for x in laws]),
                        weights=np.concatenate([x.weights for x in laws]),offsets=np.r_[0,np.cumsum(size)])


def invariant_test():
    a=Law.build([-.02,.01,.04],[.2,.2,.6])
    b=Law.build([.04,-.02,.01,-.02],[.6,.1,.2,.1])
    assert a.eq_id()==b.eq_id()
    assert abs(a.crps(.015)-b.crps(.015))<1.e-12
