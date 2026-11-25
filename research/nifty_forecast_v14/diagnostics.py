"""Episode accounting, simulation convergence, and representative refit nulls."""
from scipy.special import ndtr, expit
from scipy.stats import spearmanr

from .common import *
from .generation import dynamic_paths, random_panel, features_for_path
from .signals import fit_logistic, specifications, RISK_BASE, add_observable_mechanisms
from .volatility import design_apply, robust_design


def episode_map(events,y):
    episodes=[]
    current=[]
    stop=''
    for day in sorted(events):
        if day>=stop:
            if current:
                episodes.append(current)
            current=[]
            stop=''
        current.append(day)
        stop=max(stop,y.at[day,'endpoint'])
    if current:
        episodes.append(current)
    return episodes


def disjoint(events,y):
    stop=''
    count=0
    for day in sorted(events):
        if day>=stop:
            count+=1
            stop=y.at[day,'endpoint']
    return count


def anatomy():
    cells=[];grouped=[];relationship=[];case=[]
    for h in HORIZONS:
        y=matrix(f'targets-{h}.csv')
        x=matrix(f'features-{h}.csv')
        q=y[y.cohort.notna()]
        obs=['peak_shock_share','aligned_fraction','max_daily','max_gap','net_overnight','net_intraday','vol_first','vol_last','speed',
             'volatility','range','endpoint_return']
        pred=['atm','atm1','iv_skew','ssp', 'finance','breadth5','breadth21','sector_dispersion','sector_sync',
              'vix_move','jump_share_5','jump_share_1','fx_shock','oil_shock','global_gap_risk','vrp','overnight_share','trend5']
        x=add_observable_mechanisms(x)
        pred=[k for k in pred if k in x]
        for field in [k for k in q if k.startswith('event_')]:
            eligible=q[q[field].notna()]
            types=[('combined',eligible),('early',eligible[eligible.cohort.eq('early')]),('later',eligible[eligible.cohort.eq('later')])]
            for cohort,a in types:
                true=a[a[field].eq(1.)]
                false=a[a[field].eq(0.)]
                groups=episode_map(true.index,y)
                name=field[6:]
                cells.append(dict(horizon=h,event=name,cohort=cohort,eligible=len(a),count=len(true),
                                  frequency=len(true)/len(a) if len(a) else np.nan,
                                  distinct_episodes=len(groups),positive_disjoint=disjoint(true.index,y),
                                  eligible_disjoint=disjoint(a.index,y)))
                if cohort=='combined':
                    for j,list_ in enumerate(groups):
                        aa=a.loc[list_]
                        grouped.append(dict(horizon=h,event=name,episode=j+1,first_origin=list_[0],last_endpoint=aa.endpoint.max(),
                                            rolling_labels=len(list_),first_event_return=aa.endpoint_return.iloc[0],
                                            maximum_abs_return=aa.abs_return.max(),peak_vol=aa.volatility.max()))
                for k in obs:
                    relationship.append(dict(horizon=h,event=name,cohort=cohort,measurement=k,clock='realized decomposition',
                                         positive_avg=true[k].mean(),negative_avg=false[k].mean(),
                                         positive_median=true[k].median(),negative_median=false[k].median(),
                                         positive_n=len(true),negative_n=len(false)))
                for k in pred:
                    v=x.loc[true.index,k].dropna()
                    f=x.loc[false.index,k].dropna()
                    relationship.append(dict(horizon=h,event=name,cohort=cohort,measurement=k,clock='available at origin',
                                             positive_avg=v.mean(),negative_avg=f.mean(),positive_median=v.median(),
                                             negative_median=f.median(),positive_n=len(v),negative_n=len(f)))
        if DEMO in q.index:
            with np.load(OUT/f'observed-{h}.npz',allow_pickle=False) as z:
                o=z['paths'][y.index.get_loc(DEMO)]
            closes=np.r_[1.,o[:,3]]
            dates=x.index[x.index.get_loc(DEMO)+1:x.index.get_loc(DEMO)+1+h]
            assert dates[-1]==y.at[DEMO,'endpoint']
            for j,dt in enumerate(dates):
                case.append(dict(horizon=h,step=j+1,session=dt,open_rel=o[j,0]-1,high_rel=o[j,1]-1,low_rel=o[j,2]-1,close_rel=o[j,3]-1,
                                 overnight_log=np.log(o[j,0]/closes[j]),regular_log=np.log(o[j,3]/o[j,0]),
                                 change_log=np.log(o[j,3]/closes[j])))
    write('extreme-event-frequency.csv',pd.DataFrame(cells))
    write('distinct-extreme-episodes.csv',pd.DataFrame(grouped))
    write('extreme-anatomy-contrasts.csv',pd.DataFrame(relationship))
    write('october-case-realized-path.csv',pd.DataFrame(case))
    print('Counted',len(cells),'event/frequency cohorts and',len(grouped),'overlap-defined episode records',flush=True)


def refined_continuous_cross(rng,h,sd,n):
    # Keep extrema from the same 96-grid diffusion and compare coarser grids with
    # one-sided conditional Brownian-bridge no-hit products.
    fine=96
    r=rng.standard_normal((n,h*fine)).astype('float32')*sd/np.sqrt(fine)
    levels=np.column_stack([np.zeros(n,dtype='float32'),r.cumsum(axis=1)])
    results=[]
    for m in [12,24,48,96]:
        endpoints=levels[:,::fine//m]
        variance=sd**2/m
        for side,sign in [('upper',1.),('lower',-1.)]:
            x=sign*endpoints
            barrier=np.log1p(.02) if sign>0 else -np.log1p(-.02)
            touched=x.max(axis=1)>=barrier
            a=x[~touched]
            depth=barrier-a
            pc=np.exp(-2*depth[:,:-1]*depth[:,1:]/variance)
            clean=1-np.prod(1-pc,axis=1)
            results.append(dict(steps=m,side=side,raw_hit=float(touched.mean()),
                bridge_hit=float((touched.sum()+clean.sum())/n),analytic=float(2*ndtr(-barrier/(sd*np.sqrt(h)))),samples=n))
    return results


def convergence():
    states=read('process-states.json')
    daily=matrix('daily-process-features.csv')
    x=matrix('features-5.csv')
    labels={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    q={h:labels[h].index[labels[h].cohort.notna()] for h in HORIZONS}
    chosen=sorted(set(q[5][np.linspace(0,len(q[5])-1,8,dtype=int)])|{DEMO})
    records,grid=[],[]
    for i,d in enumerate(chosen):
        st=states[d]
        ctx,_=features_for_path(d,x,labels[5],labels[21],daily,np.nan,st)
        panel=random_panel(d,n=8192,steps=24)
        for name in ('constant_iv','gjr_iv','jump_diffusion'):
            samples=dynamic_paths(name,panel,st,ctx)
            for h in HORIZONS:
                if d not in q[h]:
                    continue
                for size in (512,2048,8192):
                    a=samples[:size,:h]
                    top=np.expm1(a[:,:,1].max(axis=1))
                    low=np.expm1(a[:,:,2].min(axis=1))
                    touch=float((top>=.02).mean())
                    r=(top-low)
                    records.append(dict(horizon=h,origin=d,model=name,n=size,p_upper2=touch,
                       p_lower2=float((low<=-.02).mean()),risk_mean=float(np.sqrt(252*np.mean(
                       np.diff(np.column_stack([np.zeros(size),a[:,:,3]]),axis=1)**2,axis=1)).mean()),
                       range80lo=float(np.quantile(r,.1)),range80hi=float(np.quantile(r,.9)),
                       mean_range=float(r.mean()),conditional_mc_se=float(np.sqrt(touch*(1-touch)/size))))
        for h in HORIZONS:
            if d not in q[h]:
                continue
            outcomes=refined_continuous_cross(np.random.default_rng(panel['seed']+h),h,ctx['ivdaily'],4096)
            grid.extend(dict(horizon=h,origin=d,scenario='continuous no overnight jump',**rec) for rec in outcomes)
    write('monte-carlo-convergence.csv',pd.DataFrame(records))
    write('continuous-bridge-check.csv',pd.DataFrame(grid))
    print('Convergence compared 512, 2048 and 8192 draws, with 12/24/48/96-step crossing diagnostics',flush=True)


def null_models():
    results=[]
    tested=['domestic','surface','intraday','domestic_global_interaction']
    endpoints=['expand','range_relative','upper_relative','lower_relative']
    specs=specifications()
    for h in HORIZONS:
        x=add_observable_mechanisms(matrix(f'features-{h}.csv'))
        y=matrix(f'targets-{h}.csv')
        q=y[y.cohort.notna()].iloc[::17]
        for case,dy in q.iterrows():
            t=mature(y,case,185)
            tr=x.reindex(y.index).iloc[t]
            dst=x.loc[[case]]
            actual=np.array([dy['event_'+e] for e in endpoints],float)
            hist=y.iloc[t][['event_'+e for e in endpoints]].to_numpy()
            a,b,_=robust_design(tr,dst,['atm','trailing'])
            ref=np.array([expit(design_apply(b,fit_logistic(a,hist[:,j])[0]))[0] for j in range(len(endpoints))])
            for choice in tested:
                a,b,note=robust_design(tr,dst,specs[choice])
                flag=np.array([n not in RISK_BASE for n in note['fields']])
                blocks=np.array_split(np.arange(len(a)),max(2,len(a)//13))
                rng=np.random.default_rng(SEED+h+pd.Timestamp(case).toordinal())
                for draw in range(-1,12):
                    if draw<0:
                        t0=a
                    else:
                        t0=a.copy()
                        pick=np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
                        t0[:,flag]=a[pick][:,flag]
                    for j,k in enumerate(endpoints):
                        beta,_=fit_logistic(t0,hist[:,j])
                        p=expit(design_apply(b,beta))[0]
                        result=(ref[j]-actual[j])**2-(p-actual[j])**2
                        results.append(dict(horizon=h,origin=case,event=k,model=choice,draw=draw,
                                p=p,p_baseline=ref[j],actual=actual[j],brier_gain=result))
    tab=pd.DataFrame(results)
    picked=tab.groupby(['horizon','event','draw','model']).brier_gain.mean().reset_index()
    picked=picked.sort_values('brier_gain').groupby(['horizon','event','draw']).tail(1)
    write('refit-null-origins.csv.gz',tab)
    write('refit-null-reselection.csv',picked)
    print('Finished',len(results),'block-permuted refit and winner comparisons',flush=True)


if __name__=='__main__':
    import sys
    {'anatomy':anatomy,'simulation':convergence,'null':null_models}[sys.argv[1]]()
