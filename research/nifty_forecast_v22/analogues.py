"""Chronological retrieval and coherent empirical OHLC outcome laws."""
from collections import Counter

from .common import *
from .learning import target_block,DAY
from .panel import STATE

STATE_FIELDS=STATE+('local_breadth','local_sector','down_share','mom10')
PATH_STATE=('shock','mom3','mom5','mom10','mom21','vol_ratio','drawdown','trend_efficiency')
METHODS=('india_nearest','foreign_nearest','mixed_nearest','mixed_mahalanobis','mixed_metric',
         'mixed_factor','mixed_path','mixed_sector','random_eligible','india_volatility','foreign_uncapped',
         'foreign_outside_asia','domestic_history','foreign_stress')


def weighted_quantile(a,w,p):
    i=np.argsort(a,kind='stable')
    return a[i[np.searchsorted(np.cumsum(w[i]),p,side='left').clip(0,len(i)-1)]]


def crps(a,w,y):
    i=np.argsort(a,kind='stable');a=a[i];w=w[i]
    return float(w@np.abs(a-y)-np.sum(w*a*(2*np.cumsum(w)-w-1)))


def state_space(x,x0):
    center=np.zeros(x.shape[1]);spread=np.ones(x.shape[1])
    for j in range(x.shape[1]):
        col=x[:,j];col=col[np.isfinite(col)]
        if len(col)>=20:
            center[j]=np.median(col)
            spread[j]=max(.08,float(np.subtract(*np.quantile(col,[.75,.25])))/1.349)
    a=np.clip((x-center)/spread,-5,5)
    q=np.clip((x0-center)/spread,-5,5)
    d=a-q
    both=np.isfinite(d)
    d=np.nan_to_num(d)
    n=both.sum(axis=1)
    surcharge=(1-n/np.maximum(1,np.isfinite(q).sum()))*.35
    return np.nan_to_num(a),d,n,surcharge


def matches(order,pool,code,region,week,max_per_week=2,max_per_region=27,n=48):
    if max_per_week is None:
        return pool[order[:n]]
    weeks=Counter();regions=Counter();paired=set();out=[]
    for j in pool[order]:
        t=week[j];g=region[j];key=(t,code[j])
        if weeks[t]>=max_per_week or regions[g]>=max_per_region or key in paired:
            continue
        weeks[t]+=1;regions[g]+=1;paired.add(key);out.append(j)
        if len(out)==n:
            break
    return np.array(out,dtype=int)


def member_weights(j,dist,week,uncapped=False):
    d=dist[j]
    w=np.exp(-np.minimum((d-np.min(d))/(np.median(np.abs(d-np.min(d)))+.25),5)*.45)
    if uncapped:
        return w/w.sum()
    _,group=np.unique(week[j],return_inverse=True)
    denominations=np.bincount(group,weights=w)[group]
    return w/denominations/len(np.unique(group))


def path_variables(a):
    logs=a[:,:,3]
    p=np.column_stack([np.zeros(len(a)),logs])
    vol=np.sqrt(np.mean(np.diff(p,axis=1)**2,axis=1)*252)
    return dict(terminal=np.expm1(logs[:,-1]),rv=vol,
                range=np.exp(a[:,:,1]).max(axis=1)-np.exp(a[:,:,2]).min(axis=1),
                drawdown=(1-np.exp(p-np.maximum.accumulate(p,axis=1))).max(axis=1),
                path_low=np.expm1(a[:,:,2].min(axis=1)),path_high=np.expm1(a[:,:,1].max(axis=1)))


def risk_values(v,w,actual,sd,h):
    out={}
    for field in ('terminal','rv','range','drawdown','path_low','path_high'):
        a=v[field];y=actual[field];mean=w@a
        lo,hi=weighted_quantile(a,w,[.1,.9])
        out.update({field+'_mean':mean,field+'_crps':crps(a,w,y),field+'_mae':abs(mean-y),
                    field+'_lo':lo,field+'_hi':hi,field+'_covered':lo<=y<=hi,field+'_width':hi-lo})
    s=sd*np.sqrt(252)
    d=.02 if h==5 else .05
    events={'expand':(v['rv']>s*1.25,actual['rv']>s*1.25),'contract':(v['rv']<s*.80,actual['rv']<s*.80),
          'terminal_down':(v['terminal']<-d,actual['terminal']<-d),'terminal_up':(v['terminal']>d,actual['terminal']>d),
          'hit_down':(v['path_low']<-d,actual['path_low']<-d),'hit_up':(v['path_high']>d,actual['path_high']>d),
          'large_drawdown':(v['drawdown']>d,actual['drawdown']>d)}
    for key,(a,y) in events.items():
        p=w@a
        out.update({key+'_p':p,key+'_actual':bool(y),key+'_brier':(p-y)**2})
    var=max(.0001,(actual['rv']/max(.001,out['rv_mean']))**2)
    return out|dict(qlike=var-np.log(var)-1)


def run():
    feats=csv('international-feature-panel.csv.gz')
    paths=np.load(OUT/'local-observed-paths.npz')
    atlas=[];all_members=[];risk=[];paths_by_h={}
    for h in ORIGINAL:
        frame=target_block(feats,h)
        path=paths[f'path_{h}']
        past=frame[list(STATE_FIELDS)].to_numpy(float)
        sigma=frame.raw_daily_sigma.to_numpy(float)
        mature=frame.mature_ns.to_numpy('int64');issues=frame.issue_ns.to_numpy('int64')
        days=frame.day.to_numpy();code=frame.code.to_numpy();region=frame.region.to_numpy()
        week=pd.to_datetime(frame.day).dt.to_period('W-SUN').astype(str).to_numpy()
        good=np.isfinite(path).all(axis=(1,2))&np.isfinite(sigma)
        values=frame.normalized.to_numpy(float)
        this_h=[]
        for i in frame.index[frame.cohort.notna()]:
            cut=issues[i]
            use0=np.where(good&(mature<cut)&(issues<cut)&(issues>=cut-330*DAY))[0]
            a,d,n,surcharge=state_space(past[use0],past[i])
            mse=(d*d).sum(axis=1)/n.clip(1)+surcharge
            cov=np.cov(a,rowvar=False)
            cov=.60*cov+.40*np.eye(a.shape[1])
            iv=np.linalg.inv(cov)
            mahal=np.einsum('ij,jk,ik->i',d,iv,d)/n.clip(1)+surcharge
            # Fit feature relevance from earlier realized normalized magnitude only.
            ac=a-a.mean(axis=0);mag=np.abs(values[use0]);mag-=mag.mean()
            relevance=np.linalg.solve(ac.T@ac/len(a)+1.75*np.eye(a.shape[1]),ac.T@mag/len(a))
            relevance=1.+1.75*np.minimum(1.,np.abs(relevance)/max(.01,np.median(np.abs(relevance))))
            metric=(d*d*relevance).sum(axis=1)/(n.clip(1)*relevance.mean())+surcharge
            _,ev=np.linalg.eigh(cov)
            factor=np.mean((d@ev[:,-4:])**2,axis=1)+surcharge
            path_i=np.array([STATE_FIELDS.index(f) for f in PATH_STATE if f in STATE_FIELDS])
            trail=np.mean(d[:,path_i]**2,axis=1)+.20*mse
            weights=np.array([1.35 if q in ('local_breadth','local_sector','relative5','synchronization','cross_dispersion') else .8 for q in STATE_FIELDS])
            sectors=(d*d*weights).sum(axis=1)/n.clip(1)+surcharge
            vol=d[:,STATE_FIELDS.index('vol_level')]**2+d[:,STATE_FIELDS.index('vol_ratio')]**2
            rng=np.random.default_rng(SEED+200*h+i)
            stress=-np.abs(values[use0])-.25*np.maximum(frame.future_range.to_numpy()[use0]/(sigma[use0]*np.sqrt(h)),0)
            ds={'india_nearest':mse,'foreign_nearest':mse,'mixed_nearest':mse,'mixed_mahalanobis':mahal,'mixed_metric':metric,
                'mixed_factor':factor,'mixed_path':trail,'mixed_sector':sectors,'random_eligible':rng.random(len(use0)),
                'india_volatility':vol,'foreign_uncapped':mse,'foreign_outside_asia':mse,'domestic_history':np.zeros(len(use0)),
                'foreign_stress':stress}
            actual={key:float(row[0]) for key,row in path_variables(path[i:i+1].astype(float)).items()}
            for name,distance in ds.items():
                domestic=name.startswith('india_') or name=='domestic_history'
                foreign=name.startswith('foreign_')
                f=(code[use0]=='india') if domestic else ((code[use0]!='india') if foreign else np.ones(len(use0),bool))
                if name=='foreign_outside_asia':
                    f&=region[use0]!='Asia Pacific'
                u=use0[f]
                if len(u)<42:
                    continue
                loc=np.where(f)[0]
                if name=='domestic_history':
                    order=np.arange(len(u))[::-1]
                else:
                    order=np.argsort(distance[loc],kind='stable')
                uncapped=name=='foreign_uncapped'
                j=matches(order,u,code,region,week,max_per_week=None if uncapped else 2,
                          max_per_region=48 if domestic else 24,n=24 if name=='foreign_stress' else 48)
                if len(j)<12:
                    continue
                absolute=np.searchsorted(use0,j)
                dist=np.zeros(len(frame));dist[j]=distance[absolute]
                if name=='random_eligible':
                    dist[j]=0.
                w=member_weights(j,dist,week,uncapped)
                p=path[j].astype(float)*(sigma[i]/sigma[j])[:,None,None]
                assert (mature[j]<cut).all()
                var=path_variables(p)
                assert np.all(p[:,:,1]>=p[:,:,2]-1.e-8)
                idx=len(atlas);start=len(this_h)
                this_h.extend(p.astype(np.float32))
                g=pd.Series(w).groupby(week[j]).sum()
                r=pd.Series(w).groupby(region[j]).sum()
                atlas.append(dict(law=idx,day=days[i],cohort=frame.cohort[i],horizon=h,model=name,issue_ns=cut,
                       last_mature_ns=int(mature[j].max()),candidate_pool=len(u),members=len(j),ess=1/(w@w),
                       dates=len(set(days[j])),weeks=len(g),regions=len(r),markets=len(set(code[j])),max_week_weight=g.max(),
                       max_region_weight=r.max(),path_from=start,path_to=len(this_h),is_stress=name=='foreign_stress',
                       empirical_path_geometry='scaled_log_ohlc',causal_volatility=sigma[i]))
                risk.append(dict(law=idx,day=days[i],cohort=frame.cohort[i],horizon=h,model=name,
                            **{k+'_actual':v for k,v in actual.items()},**risk_values(var,w,actual,sigma[i],h)))
                all_members.extend(dict(law=idx,order=b,row=int(k),market=code[k],region=region[k],origin=days[k],
                           endpoint=frame.target_day[k],mature_ns=int(mature[k]),episode=week[k],weight=v,distance=dist[k],
                           source_sigma=sigma[k],mapped_terminal=float(t)) for b,(k,v,t) in enumerate(zip(j,w,var['terminal'])))
        paths_by_h[f'p{h}']=np.array(this_h,dtype=np.float32)
        print('Analogue path laws finished for',h,'sessions',len(this_h),'mapped OHLC scenarios',flush=True)
    np.savez_compressed(OUT/'analogue-observed-path-laws.npz',**paths_by_h)
    write('analogue-law-atlas.csv',pd.DataFrame(atlas))
    write('analogue-law-members.csv.gz',pd.DataFrame(all_members))
    write('analogue-risk-cases.csv.gz',pd.DataFrame(risk))


if __name__=='__main__':
    run()
