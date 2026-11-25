"""Replay fixed-window forecast updates and archive every remaining OHLC law."""
import gzip
from dataclasses import dataclass

from scipy.special import ndtr, stdtrit

from .common import *
from .data import Daily
from .fitting import RevisionDesign
from research.nifty_forecast_v14.generation import TICK, log_ticks, numpy_zip


@dataclass
class RandomPanel:
    local: np.ndarray
    tail: np.ndarray
    uniform: np.ndarray
    seed: int

    @classmethod
    def create(cls,day,size=N):
        seed=SEED+pd.Timestamp(day).toordinal()*19
        r=np.random.default_rng(seed)
        g=r.normal(size=(size,21))*.24
        u=r.random((size,21,4))
        intr=r.normal(size=(size,21,12))*np.sqrt((1-.24**2)/12)
        timeline=np.concatenate([np.zeros((size,21,1)),np.cumsum(intr,axis=2)],axis=2)+g[:,:,None]
        o=np.stack([g,timeline.max(axis=2),timeline.min(axis=2),timeline[:,:,-1]],axis=-1)
        zn=(o[:,:,3]-g)/np.sqrt(1-.24**2)
        zt=stdtrit(6,ndtr(zn).clip(1.e-8,1-1.e-8))*np.sqrt(4/6)
        shock=(zt-zn)*np.sqrt(1-.24**2)
        fat=o.copy()
        fat[:,:,3]+=shock
        fat[:,:,1]=np.maximum(fat[:,:,1],fat[:,:,3])
        fat[:,:,2]=np.minimum(fat[:,:,2],fat[:,:,3])
        tail=np.where((u[:,0,0]>.78)[:,None,None],fat,o)
        return cls(o.astype(np.float32),tail.astype(np.float32),u.astype(np.float32),seed)


def from_local(x):
    prefix=np.column_stack([np.zeros(len(x)),np.cumsum(x[:,:-1,3],axis=1)])
    return x+prefix[:,:,None]


def continuous(p:RandomPanel,remaining,annual,mean=0.,thick=False):
    s=(p.tail if thick else p.local)[:,:remaining].astype(float)*(annual/np.sqrt(252.))
    if mean:
        s[:,:,3]+=mean/remaining
        s[:,:,1]=np.maximum(s[:,:,1],s[:,:,3])
        s[:,:,2]=np.minimum(s[:,:,2],s[:,:,3])
    return from_local(s)


def garch_paths(panel,r,s,anchor=None):
    v=np.full(len(panel.local),s['next_variance'])
    if anchor is not None:
        initial=anchor**2*10000/252
        v=.42*v+.58*initial
    out=np.empty((len(panel.local),r,4))
    for j in range(r):
        sigma=np.sqrt(np.clip(v,.02,72.))/100
        shock=panel.tail[:,j] if anchor is not None else panel.local[:,j]
        row=shock*sigma[:,None]
        out[:,j]=row
        err=100*row[:,3]
        v=s['omega']+(s['alpha']+s['gamma']*(err<0))*err*err+s['beta']*v
        if anchor is not None:
            blend=.36*np.exp(-j/2.7)
            v=(1-blend)*v+blend*initial
    return from_local(out)


def relative_suffix(logs,k):
    if k==0:
        return logs
    return logs[:,k:]-logs[:,k-1,3][:,None,None]


def resample(weights,uniform):
    return np.searchsorted(np.cumsum(weights),uniform,side='right').clip(0,len(weights)-1)


def sampled(data,uniform):
    return data[(uniform*len(data)).astype(int).clip(0,len(data)-1)]


def particle(prior,known,sigma0,u):
    k=len(known)
    if k==0:
        q=np.ones(len(prior))/len(prior)
    else:
        obs=known[:,3]
        vol=sigma0/np.sqrt(252.)
        scale=max(vol,.003)*np.sqrt(np.arange(1,k+1))
        errors=(prior[:,:k,3]-obs)/scale
        raw=.6*np.mean(errors**2,axis=1)+.7*errors[:,-1]**2
        if k>=2:
            prior_r=np.diff(np.column_stack([np.zeros(len(prior)),prior[:,:k,3]]),axis=1)
            r=np.diff(np.r_[0.,obs])
            v=np.sqrt(np.mean(prior_r**2,axis=1)).clip(.0015)
            raw+=.55*np.log(v/max(.0015,np.sqrt(np.mean(r*r))))**2
        z=np.exp(np.clip(-.95*(raw-raw.min()),-75,0))
        q=z/z.sum()
    ess=float(1/(q@q))
    if ess<24:
        alpha=.88
        q=alpha*q+(1-alpha)/len(q)
    return relative_suffix(prior[resample(q,u)],k),ess


def innovation_state(known,prior,near,vol_seq,features,origin):
    if not len(known):
        return dict(posterior=float(np.mean(prior[:,-1,3]))/prior.shape[1],last_z=0.,
            cusum=0.,repeat=0.,persistent=False,trigger='issue',mean=0.,risk_multiplier=1.)
    prefix=np.diff(np.r_[0.,known[:,3]])
    mu=float(np.mean(prior[:,-1,3]))/prior.shape[1]
    first=mu
    base=(near/np.sqrt(252.))**2
    drift_var=base/60.
    innovations=[]
    for y,s0 in zip(prefix,vol_seq):
        obs=(max(s0,.035)/np.sqrt(252.))**2
        z=(y-mu)/np.sqrt(obs+drift_var)
        innovations.append(z)
        gain=drift_var/(drift_var+obs)
        mu+=gain*(y-mu)
        drift_var=(1-gain)*drift_var+obs/270.
        mu=.97*mu+.03*first
    a=np.asarray(innovations)
    # CUSUM threshold is a registered sequential diagnostic, not a regime label computed from future outcomes.
    cu_up=cu_down=0.
    for z in a:
        cu_up=max(0.,cu_up+z-.45)
        cu_down=min(0.,cu_down+z+.45)
    sig=np.sign(prefix[-1])
    repeat=float((prefix[-min(3,len(prefix)):]*sig>0).mean())
    delta=float(features.breadth5-origin.breadth5) if np.isfinite(features.breadth5-origin.breadth5) else 0.
    financial=float(features.finance-origin.finance) if np.isfinite(features.finance-origin.finance) else 0.
    corroborates=(delta*sig>0) or (financial*sig>0)
    extreme=abs(a[-1])>2.15 or max(cu_up,-cu_down)>2.75
    persistent=bool(extreme and len(prefix)>=2 and repeat>.65 and corroborates)
    impulse=np.clip(prefix[-1],-.018,.018)
    new_mu=float(np.clip((.17 if persistent else -.085)*impulse,-.0014,.0014))
    risk=float(1+np.clip(.085*(max(abs(a[-1]),max(cu_up,-cu_down)/2)-1.08),0,.31))
    return dict(posterior=float(mu),last_z=float(a[-1]),cusum=float(max(cu_up,-cu_down)),repeat=repeat,
        persistent=persistent,trigger='persistent candidate' if persistent else 'shock' if extreme else 'ordinary',
        mean=new_mu,risk_multiplier=risk)


class Simulator:
    def __init__(self):
        self.d=Daily.load()
        self.iv_table=pd.read_csv(OUT/'remaining-tenor-availability.csv',low_memory=False)
        self.iv=self.iv_table.set_index(['asof','remaining'])
        self.fits=RevisionDesign(self.d,self.iv_table)
        self.all_prices=self.d.prices.to_numpy()
        self.rng={}
        self.hist={}
        self.states=read('daily-gjr-states.json')
        for h in HORIZONS:
            with np.load(V14/f'observed-{h}.npz',allow_pickle=False) as z:
                blocks=np.log(z['paths'])
                idx=z['origins']
            assert np.array_equal(idx,self.d.labels[h].index)
            self.hist[h]=blocks
        self.calendar=pd.read_csv(OUT/'update-calendar.csv',low_memory=False)
        self.vintage=read('joint-path-ledger.json',V14)
        self.archive={r['origin']:r for r in self.vintage['rows']}

    def panel(self,day):
        t=self.rng.get(day)
        if t is None:
            t=RandomPanel.create(day)
            self.rng[day]=t
        return t

    def prior(self,h,day):
        r=self.archive[day]
        file=V14/r['file']
        with np.load(file,allow_pickle=False) as z:
            return z[PREDECESSOR_PATH[h]][:,:h].astype(float)*TICK

    def update(self,w,prior,override=None):
        day=w.asof
        h,k,r=int(w.horizon),int(w.checkpoint),int(w.remaining)
        t=self.d.positions[w.origin]
        i=t+k
        assert self.d.sessions[i]==day and r==h-k
        s=self.states[day]
        panel=self.panel(day) if override is None else override
        n=len(panel.local)
        params,receipts=self.fits.models(i,h,k)
        active=self.iv.loc[day,r]
        iv=float(active.iv)
        iv0=float(self.iv.at[(w.origin,h),'iv'])
        raw_var=np.sqrt(np.mean(s['variance_curve'][:r])*252)/100.
        known=np.log(self.all_prices[t+1:i+1]/w.origin_reference)
        iv_trace=self.fits.iv[t:i,0]
        current=self.d.features.iloc[i];origin=self.d.features.iloc[t]
        innovation=innovation_state(known,prior,iv0,iv_trace,current,origin)
        zero=np.zeros((n,r,4))
        uniform=panel.uniform
        path={'zero_remaining':zero,'price_only':continuous(panel,r,iv0),'iv_restart':continuous(panel,r,iv),
              'gjr_restart':garch_paths(panel,r,s),'vol_state':garch_paths(panel,r,s,iv)}
        for name,value in params.items():
            path[name]=continuous(panel,r,value[1],value[0])
        dec=np.exp(-np.arange(1,r+1)/max(4.,r))
        daily_mu=np.clip(innovation['posterior'],-.0015,.0015)
        path['incremental']=continuous(panel,r,np.sqrt(.72*iv**2+.28*raw_var**2),float(daily_mu*dec.sum()))
        path['vol_only_shock']=continuous(panel,r,iv*innovation['risk_multiplier'])
        path['shock_persistence']=continuous(panel,r,iv*innovation['risk_multiplier'],innovation['mean']*dec.sum())

        # All empirical endpoints finish strictly earlier than the latest observed close.
        ids=np.arange(max(0,i-r-HIST),i-r)
        historical=np.log(self.all_prices[ids[:,None]+np.arange(1,r+1)]/self.all_prices[ids,3][:,None,None])
        path['historical']=sampled(historical,uniform[:,0,0])
        left=max(0,i-h-210)
        pool=self.hist[h][left:i-h]
        assert len(pool)>=40
        logged_iv=self.fits.iv[left:i-h,h-1]
        d0=((logged_iv/iv0-1)*1.5)**2
        if k:
            baseline=iv0*np.sqrt(np.arange(1,k+1)/252.)
            close_gap=(pool[:,:k,3]-known[:,3])/baseline
            d0+=.7*np.mean(close_gap**2,axis=1)+.35*close_gap[:,-1]**2
        w0=np.exp(-.65*(d0-d0.min()))
        w0=w0/w0.sum()
        effective=float(1/(w0@w0))
        w0=.65*w0+.35/len(w0)
        ids_a=resample(w0,uniform[:,0,1])
        z=relative_suffix(pool[ids_a],k)
        scale=np.clip(iv/logged_iv[ids_a],.50,1.8)
        path['analogue']=z*scale[:,None,None]

        weighted_episodes=np.bincount(np.arange(len(ids))//max(1,r))
        raw_weight=(1/weighted_episodes[np.arange(len(ids))//max(1,r)])
        raw_weight/=raw_weight.sum()
        ep=resample(raw_weight,uniform[:,0,0])
        episode=historical[ep]*np.clip(iv/self.fits.iv[ids[ep],r-1],.5,1.8)[:,None,None]
        repeated=uniform[:,0,1]>.75
        path['episode_tail']=np.where(repeated[:,None,None],episode,path['iv_restart'])
        path['heavy_tail']=continuous(panel,r,iv,thick=True)

        # Replace only endpoint location by a conditional sign-and-magnitude law. Preserve OHLC inequalities.
        tau=iv*np.sqrt(r/252.)
        p_up=.60*float(ndtr(params['domestic'][0]/tau))+.40*(.5+np.mean(historical[:,-1,3]>0))/2
        use_positive=uniform[:,0,2]<p_up
        normalized=np.abs(historical[:,-1,3])/(self.fits.iv[ids,r-1]*np.sqrt(r/252.))
        med=sampled(normalized,uniform[:,0,3])*tau
        base=path['iv_restart']
        joint=base.copy()
        change=(np.where(use_positive,med,-med)-base[:,-1,3])/r
        # Apply daily location differences. Widen high/low to contain each new close.
        for j in range(r):
            joint[:,j]+=change[:,None]*j
            joint[:,j,3]+=change
            joint[:,j,1]=np.maximum(joint[:,j,1],joint[:,j,3])
            joint[:,j,2]=np.minimum(joint[:,j,2],joint[:,j,3])
        path['sign_magnitude']=joint
        particles,ess=particle(prior,known,iv0,uniform[:,0,3])
        share=float(np.clip(.10+.42*ess/len(prior),.10,.52))
        path['particle']=particles
        path['hybrid']=np.where((uniform[:,0,2]<share)[:,None,None],particles,path['vol_state'])
        assert set(path)==set(MODELS)-{'frozen'}
        note=dict(horizon=h,origin=w.origin,checkpoint=k,asof=day,observed_sessions=k,remaining=r,
                 known_source=active.source_day if isinstance(active.source_day,str) else None,
                 scheduled_remaining_endpoint=active.scheduled_remaining_endpoint,
                 seed=panel.seed,raw_iv=iv,old_iv=iv0,gjr_risk=float(raw_var),
                 particle_ess=ess,analogue_ess=effective,analogue_count=len(pool),hybrid_prior_fraction=share,
                 analogue_last_outcome=self.d.sessions[i-1],history_last_outcome=self.d.sessions[i-1],
                 posterior=innovation,estimated_models={n:[float(a),float(b)] for n,(a,b) in params.items()})
        return path,note,receipts


def run():
    register()
    sim=Simulator()
    folder=OUT/'updated-paths'
    folder.mkdir(exist_ok=True)
    ledger=[];archive=[]
    grouped=sim.calendar.groupby(['horizon','origin'],sort=True)
    with gzip.open(OUT/'fitted-update-models.ndjson.gz','wt',encoding='utf-8',compresslevel=2) as f:
        for j,((h,day),group) in enumerate(grouped,1):
            prior=sim.prior(h,day)
            files={}
            for rec in group.sort_values('checkpoint').itertuples(index=False):
                predictions,note,receipts=sim.update(rec,prior)
                assert rec.checkpoint+rec.remaining==h
                for name,path in predictions.items():
                    ticks=log_ticks(path)
                    assert np.isfinite(path).all() and np.all(ticks[:,:,1]>=np.maximum(ticks[:,:,0],ticks[:,:,3]))
                    assert np.all(ticks[:,:,2]<=np.minimum(ticks[:,:,0],ticks[:,:,3]))
                    files[f'k{rec.checkpoint:02}_{name}']=ticks
                ledger.append(note)
                f.write(json.dumps(dict(horizon=h,origin=day,target=rec.target,asof=rec.asof,checkpoint=rec.checkpoint,
                                         fits=receipts),allow_nan=False,separators=(',',':'))+'\n')
            filename=folder/f'{h}-{day}.npz'
            numpy_zip(filename,files)
            archive.append(dict(horizon=int(h),origin=day,checkpoints=len(group),
                file=filename.relative_to(OUT).as_posix(),sha256=sha(filename),
                frozen_file=sim.archive[day]['file'],frozen_sha256=sim.archive[day]['sha256'],frozen_model=PREDECESSOR_PATH[h]))
            if j%60==0:
                print('Archived',j,'/',len(grouped),'original windows and',len(ledger),'forecast updates',flush=True)
    save('joint-update-archive.json',dict(n=N,tick=TICK,models=MODELS,files=archive,
        format='kNN_model integer log OHLC prices relative to the current cash anchor. Equal path weights. Prepend exactly the observed OHLC prefix and preserve original reference. Frozen uses the exact V14 law cited per row.'))
    save('joint-update-receipts.json',ledger)
    print('Archived',len(archive),'fixed forecasts and',len(ledger),'joint update cases',flush=True)


if __name__=='__main__':
    run()
