"""Same-anchor historical path ablations and episode-matched foreign replacement."""
from collections import defaultdict

from .common import *
from .laws import Law
from research.nifty_forecast_v22.analogues import path_variables,crps
from research.nifty_forecast_v22.learning import target_block
from research.nifty_forecast_v16.paths import logs_to_path
from research.nifty_forecast_v14.generation import student

STATE=('mom3','mom5','mom21','vol_level','vol_ratio','drawdown','trend_efficiency','relative5','cross_dispersion','synchronization','global_vix')
POINT={5:'offshore_plus_domestic',21:'GJR'}
K=24
FOREIGN=6
SIM=192


def localize(z):
    before=np.column_stack([np.zeros(len(z)),z[:,:-1,3]])
    return z-before[:,:,None]


def daily_to_paths(x,permute=False,rng=None):
    q=localize(x)
    if permute:
        order=np.argsort(rng.random(q.shape[:2]),axis=1)
        q=q[np.arange(len(q))[:,None],order]
    return logs_to_path(q)


def scale_paths(z,anchor,remove_center=True,individual=False):
    # Coherent monotone maps apply to all marks of a session together.
    z=z.astype(float,copy=True)
    if remove_center:
        z-=float(z[:,-1,3].mean())*(np.arange(1,z.shape[1]+1)[None,:,None]/z.shape[1])
    sd=path_variables(z)['rv']
    ratio=anchor/np.maximum(.001,sd if individual else sd.mean())
    return z*ratio[:,None,None] if individual else z*ratio


def state_distance(x,q):
    med=np.nanmedian(x,axis=0)
    rec=np.nanquantile(x,[.25,.75],axis=0)
    sd=np.maximum(.08,(rec[1]-rec[0])/1.349)
    d=np.clip((x-q)/sd,-5,5)
    n=np.maximum(1,np.isfinite(d).sum(axis=1))
    return np.nansum(d*d,axis=1)/n+.32*(1-n/max(1,np.isfinite(q).sum()))


def ordered_episodes(z,distance,week):
    groups={}
    for j in z[np.argsort(distance[z],kind='stable')]:
        if week[j] not in groups:
            groups[week[j]]=int(j)
    return groups


def strict_donors(frame,h):
    audit=csv('foreign-full-ohlc-pairs.csv.gz',usecols=['code','day','strict_bar'])
    ok=set(zip(audit.loc[audit.strict_bar,'code'],audit.loc[audit.strict_bar,'day']))
    x=np.array([(c,d) in ok for c,d in zip(frame.code,frame.day,strict=True)])
    starts=np.zeros(len(frame),dtype=bool)
    for k,sub in frame.groupby('code',sort=False):
        if k=='india':
            continue
        loc=sub.row.to_numpy()
        if len(loc)<=h:
            continue
        a=np.lib.stride_tricks.sliding_window_view(x[loc],h+1).all(axis=1)
        starts[loc[1:len(a)+1]]=a
    return starts


def synth(h,anchor,shock,gap,bridge,student_gjr=False):
    steps=bridge.shape[-1]
    if student_gjr:
        innovation=student(shock,7.)
        vari=np.ones(len(shock))
        daily_shock=np.empty_like(shock)
        intra=np.empty_like(shock)
        for k in range(h):
            daily_shock[:,k]=np.sqrt(vari)*innovation[:,k]
            intra[:,k]=np.sqrt(vari)*.88
            vari=.055+(.055+.13*(innovation[:,k]<0))*daily_shock[:,k]**2+.825*vari
    else:
        daily_shock=shock
        intra=np.full_like(shock,.88)
    fraction=(np.arange(steps)+1)/steps
    excursion=(bridge.cumsum(axis=2)-bridge.sum(axis=2)[:,:,None]*fraction)/np.sqrt(steps)
    # Common shocks and bridge compare the mobility of volatility without a different random draw.
    gap_part=.36*gap*intra/.88
    regular=gap_part[:,:,None]+intra[:,:,None]*excursion+(daily_shock-gap_part)[:,:,None]*fraction
    high=np.maximum(np.maximum(gap_part,daily_shock),regular.max(axis=2))
    low=np.minimum(np.minimum(gap_part,daily_shock),regular.min(axis=2))
    path=logs_to_path(np.stack([gap_part,high,low,daily_shock],axis=2))
    return scale_paths(path,anchor)


def profile(p):
    ans=path_variables(p)
    local=localize(p)
    ret=local[:,:,3];gap=local[:,:,0]
    m=max(1,p.shape[1]//2)
    ans.update(gap_sd=np.sqrt(np.square(gap).mean(axis=1)*252),
               gap_share=np.square(gap).sum(axis=1)/np.maximum(1e-12,np.square(ret).sum(axis=1)),
               volatility_evolution=np.sqrt((1.e-5+np.square(ret[:,m:]).mean(axis=1))/(1.e-5+np.square(ret[:,:m]).mean(axis=1))),
               persistence=(np.sign(ret[:,1:])==np.sign(ret[:,:-1])).mean(axis=1),
               excursion=np.mean(local[:,:,1]-local[:,:,2]-abs(local[:,:,3]-local[:,:,0]),axis=1),
               rebound=np.max(np.exp(np.column_stack([np.zeros(len(p)),p[:,:,3]])-
                                    np.minimum.accumulate(np.column_stack([np.zeros(len(p)),p[:,:,3]]),axis=1))-1,axis=1))
    return ans


def score_path(z,val,threshold,h):
    v=profile(z)
    out={}
    for k,a in v.items():
        s=Law.build(a);y=val[k]
        q=s.quantiles([.1,.5,.9])
        mn,var=s.moments()
        out.update({f'{k}_actual':y,f'{k}_crps':s.crps(y),f'{k}_mean':mn,f'{k}_mae':abs(mn-y),f'{k}_width':q[2]-q[0],
                    f'{k}_covered':int(q[0]<=y<=q[2]),f'{k}_q10':q[0],f'{k}_q50':q[1],f'{k}_q90':q[2],f'{k}_sd':np.sqrt(var)})
    h_cut=.02 if h==5 else .05
    barrier=.015 if h==5 else .04
    events={'expansion':('rv',1.25*threshold,1.),'contraction':('rv',.80*threshold,-1.),'upper_range_tail':('range',.04 if h==5 else .08,1.),
            'terminal_up':('terminal',h_cut,1.),'terminal_down':('terminal',-h_cut,-1.),'hit_up':('path_high',barrier,1.),
            'hit_down':('path_low',-barrier,-1.),'persistent_direction':('persistence',.70,1.),'tail_drawdown':('drawdown',h_cut,1.)}
    for theme,(k,th,d) in events.items():
        y=bool(d*(val[k]-th)>0)
        probability=float((d*(v[k]-th)>0).mean())
        out.update({f'{theme}_p':probability,f'{theme}_event':y,f'{theme}_brier':(probability-y)**2})
    q=max(.0001,(val['rv']/max(.001,out['rv_mean']))**2)
    return out|dict(qlike=q-np.log(q)-1)


class Donors:
    """Use a fixed domestic episode census when evaluating foreign replacements."""
    def __init__(self,h,features,book):
        self.h=h
        self.x=target_block(features,h)
        self.day=self.x.day.to_numpy()
        self.market=self.x.code.to_numpy()
        self.region=self.x.region.to_numpy()
        self.week=pd.to_datetime(self.x.day).dt.to_period('W-SUN').astype(str).to_numpy()
        self.mature=self.x.mature_ns.to_numpy(np.int64)
        self.issue=self.x.issue_ns.to_numpy(np.int64)
        self.state=self.x[list(STATE)].to_numpy(float)
        self.sigma=self.x.raw_daily_sigma.to_numpy(float)
        self.p=book[f'path_{h}']
        self.good=np.isfinite(self.p).all(axis=(1,2))&np.isfinite(self.sigma)
        self.strict=strict_donors(self.x,h)
        self.verified=defaultdict(int)

    def raw(self,ids):
        return self.p[ids].astype(float)/self.sigma[ids,None,None]

    def select(self,cutoff,state,rng):
        eligible=np.flatnonzero(self.good&(self.mature<cutoff)&(self.issue<cutoff)&(self.issue>=cutoff-365*DAY))
        local=eligible[self.market[eligible]=='india']
        foreign=eligible[self.market[eligible]!='india']
        dist=np.full(len(self.x),np.inf)
        dist[eligible]=state_distance(self.state[eligible],state)
        india=ordered_episodes(local,dist,self.week)
        ep=list(india)[:K]
        if len(ep)<K:
            raise ValueError('Insufficient matched domestic episodes')
        base=np.array([india[k] for k in ep])
        stoch=np.full(len(self.x),np.inf);stoch[eligible]=rng.random(len(eligible))
        vol=np.full(len(self.x),np.inf)
        cols=[STATE.index('vol_level'),STATE.index('vol_ratio')]
        vol[eligible]=state_distance(self.state[np.ix_(eligible,cols)],state[cols])
        rand=ordered_episodes(local,stoch,self.week)
        vv=ordered_episodes(local,vol,self.week)
        result={
            'india_state_matched':base,
            'india_random_same_episodes':np.array([rand[k] for k in ep]),
            'india_vol_same_episodes':np.array([vv[k] for k in ep]),
        }
        kinds={
            'mixed_broad':(foreign,dist),'mixed_random_foreign':(foreign,stoch),
            'mixed_vol_only':(foreign,vol),'mixed_strict':(foreign[self.strict[foreign]],dist),
            'mixed_omit_asia':(foreign[self.region[foreign]!='Asia Pacific'],dist),
            'mixed_omit_disputed':(foreign[~np.isin(self.market[foreign],('us','japan','uk'))],dist),
            'mixed_strict_omit_asia':(foreign[self.strict[foreign]&(self.region[foreign]!='Asia Pacific')],dist),
        }
        for name,(index,score) in kinds.items():
            mapping=ordered_episodes(index,score,self.week)
            ordered=sorted((j for j,k in enumerate(ep) if k in mapping),key=lambda j:score[mapping[ep[j]]])
            pick=base.copy()
            for j in ordered[:FOREIGN]:
                pick[j]=mapping[ep[j]]
            result[name]=pick
            if name in ('mixed_broad','mixed_strict'):
                result[name+'_india_control']=base.copy()
            if name=='mixed_broad':
                if len(ordered)==len(ep):
                    result['foreign_only_same_episodes']=np.array([mapping[k] for k in ep])
                else:
                    pure=np.array(list(mapping.values())[:K])
                    if len(pure)==K:
                        result['foreign_only_unmatched_episodes']=pure
        return result,local,dist


def score():
    x=csv('international-feature-panel.csv.gz',V22)
    raw=np.load(V22/'local-observed-paths.npz')
    anchors=csv('india-protected-point-risk-cases.csv.gz',V22)
    rows=[];members=[];draws={};recipes=[];precision=[]
    for h in HORIZONS:
        t=Donors(h,x,raw)
        q=anchors[anchors.horizon.eq(h)&anchors.model.eq(POINT[h])].set_index('day')
        pre=csv(f'targets-{h}.csv',root_for(14)).set_index('day')
        full=t.x[t.x.cohort.notna()]
        precision_days=set(full.day.iloc[np.linspace(0,len(full)-1,12).astype(int)])
        for row in full.itertuples(index=False):
            i=row.row;day=row.day;clock=int(row.issue_ns)
            rng=np.random.default_rng(SEED+17*i+h)
            rt=q.loc[day]
            anchor=float(rt.pred_vol)
            threshold=float(pre.loc[rt.origin,'trailing_at_origin'])
            actual={k:float(v[0]) for k,v in profile(t.p[i:i+1].astype(float)).items()}
            assert abs(actual['rv']-rt.actual_vol)<1.e-6
            seeds,local,dist=t.select(clock,t.state[i],rng)
            # Whole donor paths are selected first. Per-path realized volatility is only observed on admitted donors.
            ordinary={}
            path_receipt={}
            for key,idx in seeds.items():
                assert (t.mature[idx]<clock).all() and len(set(t.week[idx]))==K
                ordinary[key]=scale_paths(t.raw(idx),anchor)
                ng=int((t.market[idx]!='india').sum())
                for slot,j in enumerate(idx):
                    members.append(dict(day=day,horizon=h,model=key,slot=slot,source_row=j,market=t.market[j],region=t.region[j],
                              source_day=t.day[j],target_day=t.x.target_day[j],source_mature_ns=int(t.mature[j]),issue_ns=clock,
                              episode=t.week[j],verified_source=bool(t.strict[j]),distance=float(dist[j]),weight=1/K))
                path_receipt[key]=(ng,int(t.mature[idx].max()),key)
            hist=t.raw(seeds['india_state_matched'])
            mixed=t.raw(seeds['mixed_broad'])
            for key,pth in (('india_temporally_shuffled',hist),('mixed_temporally_shuffled',mixed)):
                ordinary[key]=scale_paths(daily_to_paths(pth,True,rng),anchor)
            ordinary['india_constant_scenario_risk']=scale_paths(hist,anchor,individual=True)
            ordinary['india_realized_donor_norm']=scale_paths(hist/np.maximum(.01,path_variables(hist)['rv'])[:,None,None],anchor)
            ordinary['india_state_widened']=ordinary['india_state_matched']*1.12
            iii=localize(hist)
            v=iii.copy()
            # Keep the closes identical and transfer the gap to the first regular-session move.
            v[:,:,0]=0.
            v[:,:,1]=np.maximum(v[:,:,1],0.)
            v[:,:,2]=np.minimum(v[:,:,2],0.)
            ordinary['india_gap_removed']=scale_paths(logs_to_path(v),anchor)
            v=iii.copy()
            v[:,:,1]=np.maximum(v[:,:,0],v[:,:,3]);v[:,:,2]=np.minimum(v[:,:,0],v[:,:,3])
            ordinary['india_no_intraday_excursions']=scale_paths(logs_to_path(v),anchor)
            day_pool=t.p[local,0,:].astype(float)/t.sigma[local,None]
            fresh=day_pool[rng.integers(len(day_pool),size=(SIM,h))]
            ordinary['india_independent_days']=scale_paths(logs_to_path(fresh),anchor)
            common_z=rng.normal(size=(SIM,h));gap=rng.normal(size=(SIM,h));bridge=rng.normal(size=(SIM,h,16))
            ordinary['constant_vol_diffusion']=synth(h,anchor,common_z,gap,bridge)
            ordinary['student_t_gjr_same_anchor']=synth(h,anchor,common_z,gap,bridge,True)
            for key,pth in ordinary.items():
                val=score_path(pth,actual,threshold,h)
                donors=path_receipt.get(key)
                if donors is None:
                    expected='mixed_broad' if key.startswith('mixed_') else 'india_state_matched'
                    donors=path_receipt[expected] if key not in ('india_independent_days','constant_vol_diffusion','student_t_gjr_same_anchor') else (
                        0,int(t.mature[local].max()) if key=='india_independent_days' else 0,key)
                count,last_ma,source=donors
                rows.append(dict(horizon=h,day=day,target=row.target_day,cohort=row.cohort,clock='preauction_0855',model=key,anchor=anchor,
                                 foreign_paths=count,simulations=len(pth),threshold=threshold,last_mature_ns=last_ma,issue_ns=clock,
                                 active=len(pth)>0,**val))
                recipes.append(dict(horizon=h,day=day,model=key,anchor=anchor,rng_seed=SEED+17*i+h,donor_arm=source,
                                   shape='log-relative open, high, low, close; deterministic selection and transformations'))
                if day in precision_days and key in ('india_state_matched','mixed_broad','mixed_strict','student_t_gjr_same_anchor'):
                    v=f'{h}_{day}_{key}'
                    draws[v]=pth.astype(np.float32)
                    precision.append(dict(horizon=h,day=day,model=key,key=v,anchor=anchor,
                                   actual_range=actual['range'],actual_return=actual['terminal'],actual_rv=actual['rv']))
        print('Paths',h,len(full),'origins and',int(t.strict.sum()),'strict donor windows in the source panel.',flush=True)
    write('v23-path-cases.csv.gz',pd.DataFrame(rows))
    write('path-donor-members.csv.gz',pd.DataFrame(members))
    write('path-law-recipes.csv.gz',pd.DataFrame(recipes))
    write('precision-path-index.csv',pd.DataFrame(precision))
    np.savez_compressed(OUT/'precision-joint-paths.npz',**draws)
    summary=pd.DataFrame(rows).groupby(['horizon','model'],as_index=False).agg(n=('day','size'),foreign_paths=('foreign_paths','mean'),
           range_crps=('range_crps','mean'),rv_mae=('rv_mae','mean'),drawdown_crps=('drawdown_crps','mean'),expansion_brier=('expansion_brier','mean'),
           range_tail_brier=('upper_range_tail_brier','mean'),persistence_brier=('persistent_direction_brier','mean'))
    write('preliminary-path-summary.csv',summary)


if __name__=='__main__':
    score()
