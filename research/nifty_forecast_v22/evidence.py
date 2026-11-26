"""Matched comparisons, episode influence, falsification and reproducible scoring."""
from .common import *
from .india import domestic_inputs
from .learning import train,eligible,DAY
from .panel import asof
from .reference import NATIVE_ANCHORS
from research.nifty_forecast_v21.evidence import model_stats
from research.nifty_forecast_v20.modeling import block_intervals,block_counts

METRICS=('brier','crps','log_loss','mae','tail_up_brier','tail_down_brier')
INTERNATIONAL=('loco_transfer','loro_transfer','partial_country','pooled_with_context','country_shuffle','date_block_null',
               'dominant_excluded','delayed_transfer','local_own_only','local_persistence','global_factor_only','factor_only','factor_and_innovation')
INTER_METRICS=('brier','crps','rv_mae','qlike','range_mae','expansion_brier','contraction_brier','reversal_brier','recovery_brier',
               'divergence_brier','breadth_deterioration_brier','global_mae','innovation_mae')


def scopes(u):
    return [('combined',u),('early',u[u.cohort.eq('early')]),('later',u[u.cohort.eq('later')]),('active',u[u.active.astype(bool)])]


def india(z):
    out=[];delta=[];bounds=[];phase=[];omit=[];cal=[];regimes=[]
    dates=cash().index
    for (h,clock),f in z.groupby(['horizon','cutoff']):
        if clock=='native_0910':
            anchor=NATIVE_ANCHORS[h][0]
            alt='omit_latest_21_training_origins' if h==5 else 'eight_calendar_day_embargo'
        else:
            anchor='archived_same_clock' if h==5 else 'archived_joint_GJR'
            alt='archived_joint_GJR' if h==5 else 'archived_same_clock'
        roles=f.set_index(['model','day'])
        p=roles.loc[anchor].sort_index()
        n0=p.groupby('cohort').size()
        assert tuple(n0.loc[['early','later']])==EXPECTED[h][:2]
        assert not f.duplicated(['day','model']).any()
        s=csv('international-feature-panel.csv.gz',usecols=['code','day','vol_level','synchronization'])
        s=s[s.code.eq('india')].set_index('day').sort_index().reindex(p.index)
        vol_threshold=s.vol_level.shift().rolling(95,min_periods=35).quantile(.66)
        high_vol=s.vol_level.ge(vol_threshold);high_sync=s.synchronization.ge(.55)
        for model,u in f.groupby('model'):
            u=u.sort_values('day')
            for scope,v in scopes(u):
                if len(v):
                    out.append(dict(horizon=h,cutoff=clock,model=model,kind=v.kind.iloc[0],scope=scope,coverage=len(v)/len(p) if scope=='active' else len(v)/len(p if scope=='combined' else p[p.cohort.eq(scope)]),
                        tail_up_brier=v.tail_up_brier.mean(),tail_down_brier=v.tail_down_brier.mean(),**model_stats(v)))
            y=u.assign(sign=u.actual.gt(0),bin=pd.cut(u.p,np.arange(0,1.0001,.2),include_lowest=True))
            for label,e in y.groupby('bin',observed=True):
                cal.append(dict(horizon=h,cutoff=clock,model=model,probability_bin=str(label),n=len(e),p=e.p.mean(),observed=e.sign.mean()))
        for ref in (anchor,alt):
            parent=roles.loc[ref].sort_index()
            use=f.set_index(['day','model']).active.unstack().reindex(parent.index).fillna(False)
            grouped=f.pivot(index='day',columns='model',values=list(METRICS)).reindex(parent.index)
            for metric in METRICS:
                losses=grouped[metric]
                gain=losses.rsub(parent[metric],axis=0)
                for model in losses:
                    u=roles.loc[model].reindex(parent.index)
                    assert u.actual.dropna().sub(parent.actual).dropna().abs().max()<1.e-10
                    a=u.target_end.notna()
                    assert u.target_end[a].eq(parent.target_end[a]).all()
                    for label,mask in (('combined',a),('early',a&u.cohort.eq('early')),('later',a&u.cohort.eq('later')),
                                       ('active_matched',a&use[model])):
                        if mask.any():
                            delta.append(dict(horizon=h,cutoff=clock,reference=ref,model=model,metric=metric,scope=label,n=int(mask.sum()),
                                 parent_loss=parent.loc[mask,metric].mean(),candidate=losses.loc[mask,model].mean(),gain=gain.loc[mask,model].mean(),
                                 coverage=float(mask.sum()/len(parent))))
                    if ref!=anchor or metric not in ('brier','crps') or model==ref:
                        continue
                    z0=gain[model]
                    ph=dates.get_indexer(z0.index)%h
                    for i in range(h):
                        z1=z0[ph==i].dropna()
                        phase.append(dict(horizon=h,cutoff=clock,reference=ref,model=model,metric=metric,phase=i,n=len(z1),gain=z1.mean()))
                    months=z0.index.str[:7]
                    for month in months.unique():
                        keep=z0[months!=month].dropna();removed=z0[months==month].dropna()
                        omit.append(dict(horizon=h,cutoff=clock,model=model,metric=metric,omitted=month,type='calendar_month',n=len(keep),
                                         removed_gain=removed.mean(),remaining_gain=keep.mean()))
                    arr=z0.dropna()
                    if len(arr)>=21:
                        tmp=parent.reindex(arr.index).actual
                        for label,z1 in (('largest_favorable_21',arr),('largest_absolute_market_21',tmp.abs())):
                            start=int(np.argmax(np.convolve(z1.to_numpy(),np.ones(21),'valid')))
                            sl=arr.iloc[start:start+21]
                            keep=arr.drop(sl.index)
                            omit.append(dict(horizon=h,cutoff=clock,model=model,metric=metric,omitted=f'{sl.index[0]} to {sl.index[-1]}',
                                 type=label,n=len(keep),removed_gain=sl.mean(),remaining_gain=keep.mean()))
                    for label,mask in (('high_known_volatility',high_vol),('typical_known_volatility',vol_threshold.notna()&~high_vol),
                                       ('synchronized',high_sync),('other_synchronization',~high_sync)):
                        g=z0[mask].dropna()
                        regimes.append(dict(horizon=h,cutoff=clock,model=model,metric=metric,regime=label,n=len(g),gain=g.mean()))
                if metric not in ('brier','crps','mae'):
                    continue
                for label,v in (('combined',gain),('active_matched',gain.where(use))):
                    v=v.loc[:,v.notna().sum().ge(30)]
                    for b in (h,21) if h!=21 else (21,42):
                        q=block_intervals(v.to_numpy(),b,1100,SEED+31*h+b)
                        bounds.append(q.assign(horizon=h,cutoff=clock,reference=ref,metric=metric,scope=label,model=v.columns,block=b))
    write('india-return-leaderboard.csv',pd.DataFrame(out))
    write('india-matched-comparisons.csv.gz',pd.DataFrame(delta))
    write('india-search-adjusted-intervals.csv.gz',pd.concat(bounds,ignore_index=True))
    write('india-disjoint-phase-results.csv.gz',pd.DataFrame(phase))
    write('india-episode-omission.csv.gz',pd.DataFrame(omit))
    write('india-probability-calibration.csv',pd.DataFrame(cal))
    write('india-regime-sensitivity.csv.gz',pd.DataFrame(regimes))


def international():
    pair=[];family=[];episode=[];risk=[]
    for h in HORIZONS:
        cols=['model','code','region','day','ret','mature_ns','target_day','p',*INTER_METRICS]
        a=csv(f'market-forecast-cases-{h}.csv.gz',usecols=cols)
        foreign=a[a.code.ne('india')].copy()
        foreign['scope']=np.where(foreign.day.ge('2026-07-01'),'later','earlier')
        for label,z in [('all',foreign),*list(foreign.groupby('scope'))]:
            for metric in INTER_METRICS:
                u=z.pivot(index=['day','code','region'],columns='model',values=metric)
                for parent in ('local_own_only','local_persistence'):
                    gains=u.rsub(u[parent],axis=0)
                    daily=gains.groupby(level='day').mean().sort_index()
                    countries=gains.groupby(level='code').mean()
                    regions=gains.groupby(level='region').mean()
                    q=block_intervals(daily.to_numpy(),max(h,10),850,SEED+h)
                    family.append(q.assign(horizon=h,scope=label,reference=parent,metric=metric,model=daily.columns,
                                          negative_countries=(countries.lt(0)&countries.notna()).sum().to_numpy(),
                                          countries_observed=countries.notna().sum().to_numpy(),
                                          observed_origins=gains.notna().sum().to_numpy(),
                                          n_regions=(regions.notna().sum()).to_numpy()))
                    for name in u:
                        for reg,v in gains[name].groupby(level='region'):
                            pair.append(dict(horizon=h,scope=label,reference=parent,metric=metric,model=name,group_type='region',
                                 group=reg,n=v.count(),gain=v.mean()))
                        for country,v in gains[name].groupby(level='code'):
                            pair.append(dict(horizon=h,scope=label,reference=parent,metric=metric,model=name,group_type='market',
                                 group=country,n=v.count(),gain=v.mean()))
                    if metric in ('brier','crps','rv_mae','expansion_brier') and parent=='local_persistence' and h in ORIGINAL:
                        week=pd.to_datetime(daily.index).to_period('W-SUN')
                        for group in week.unique():
                            lost=week==group;remaining=daily.loc[~lost].mean();removed=daily.loc[lost].mean()
                            for model in INTERNATIONAL:
                                episode.append(dict(horizon=h,scope=label,metric=metric,model=model,reference=parent,omitted_week=str(group),
                                               omitted_gain=removed[model],remaining_gain=remaining[model],n=int((~lost).sum())))
        t=foreign[foreign.model.isin(INTERNATIONAL)].copy()
        t['observed_up']=t.ret.gt(0)
        t['bin']=pd.cut(t.p,np.arange(0,1.0001,.2),include_lowest=True)
        q=t.groupby(['model','scope','bin'],observed=True).agg(n=('day','size'),p=('p','mean'),observed=('observed_up','mean')).reset_index()
        risk.append(q.assign(horizon=h))
    write('international-matched-country-region.csv.gz',pd.DataFrame(pair))
    write('international-matched-date-intervals.csv.gz',pd.concat(family,ignore_index=True))
    write('international-leave-global-episode-out.csv.gz',pd.DataFrame(episode))
    write('international-probability-calibration.csv',pd.concat(risk,ignore_index=True))
    coef=csv('international-coefficient-history.csv.gz')
    rows=[]
    for (h,model,field),z in coef.groupby(['horizon','model','feature']):
        for response in ('location','innovation','magnitude','volatility','expansion','contraction'):
            s=z[response];med=z.groupby('code')[response].median()
            rows.append(dict(horizon=h,model=model,feature=field,head=response,windows=len(s),n_entities=len(med),
                       median=s.median(),iqr=s.quantile(.75)-s.quantile(.25),positive_fraction=s.gt(0).mean(),
                       sign_agreement_country=max(med.gt(0).mean(),med.lt(0).mean()),
                       sign_agreement_time=max(s.gt(0).mean(),s.lt(0).mean()),
                       near_zero_fraction=s.abs().lt(.025).mean()))
    write('transfer-coefficient-stability.csv',pd.DataFrame(rows))


def nulls(z):
    f=csv('international-feature-panel.csv.gz')
    t=csv('international-target-panel.csv.gz',usecols=['row','horizon','mature_ns','cohort'])
    arms=['domestic','international','beyond_gift','low_dimensional']
    results=[];receipts=[]
    rng=np.random.default_rng(SEED+166)
    for h in ORIGINAL:
        parent=NATIVE_ANCHORS[h][0]
        a=z[z.horizon.eq(h)&z.cutoff.eq('native_0910')&z.model.eq(parent)].set_index('day').sort_index()
        features=f[f.code.eq('india')].set_index('day').join(t[t.horizon.eq(h)].set_index('row'),on='row').reindex(a.index)
        d=domestic_inputs(h).reindex(a.index)
        local=d[['reaction_mean','domestic_rotation_finance','allEQ_advance','FII_index_futures_d21','iv_prev']].to_numpy()
        away=features[['global5','relative5','cross_dispersion','synchronization','global_vix']].to_numpy()
        gift=d[['gift_proxy','expected_gap']].to_numpy()
        n=len(a);mature=features.mature_ns.to_numpy();origin=features.issue_ns.to_numpy();dd=a.index.to_numpy()
        sigma=features.raw_daily_sigma.to_numpy()*np.sqrt(h)
        y=a.actual.to_numpy();p=a.p.to_numpy()
        target=np.column_stack([(y-np.asarray(a['mean']))/sigma,(y>0)-p])
        past=[np.flatnonzero((mature<cut)&(origin<cut))[-140:] for cut in origin]
        active=np.array([len(q)>=45 for q in past])
        phases=block_counts(n,21,350,rng)
        for j in range(25):
            case='observed' if j==0 else 'blocked_refit_null'
            rules=[local,away,np.column_stack([local,away,gift]),np.column_stack([gift,away[:,[0,3]]])]
            pv=[];mv=[]
            for x in rules:
                pred=np.zeros((n,2))
                for i in np.flatnonzero(active):
                    ix=past[i]
                    sy=target[ix]
                    if j:
                        # Permute short contiguous groups wholly within the mature training window.
                        blocks=np.array_split(np.arange(len(ix)),max(3,len(ix)//min(10,h)))
                        r=np.random.default_rng(SEED+361*j+i+h)
                        order=np.concatenate([blocks[k] for k in r.permutation(len(blocks))])
                        sy=sy[order]
                    train0=train(x[ix],sy,dd[ix],tuple(range(x.shape[1])),1.35)
                    pred[i]=train0.predict(x[i:i+1])[0]
                p_hat=np.clip(p+.40*pred[:,1],.02,.98)
                p_hat[~active]=p[~active]
                pv.append((p-(y>0))**2-(p_hat-(y>0))**2)
                mu=a['mean'].to_numpy()+.45*sigma*np.clip(pred[:,0],-.75,.75)
                mv.append(np.abs(a['mean']-y)-np.abs(mu-y))
            for metric,g in (('brier',np.array(pv).T),('mae',np.array(mv).T)):
                means=g[active].mean(axis=0)
                keep=phases[:,active]
                bs=(keep@g[active])/keep.sum(axis=1,keepdims=True)
                for k in range(len(arms)):
                    results.append(dict(horizon=h,replicate=j,classification=case,metric=metric,variant=arms[k],n=int(active.sum()),
                                        gain=means[k],selected=k==int(np.argmax(means)),bootstrap_se=bs[:,k].std(ddof=1)))
        receipts.append(dict(horizon=h,base=parent,period_start=dd[0],period_end=dd[-1],n=n,active=int(active.sum()),
                         unpermuted=1,chronologically_refitted_and_reselected_nulls=24,variants=arms))
    b=pd.DataFrame(results)
    s=b[b.selected].groupby(['horizon','metric'])
    out=[]
    for (h,m),q in s:
        v=q[q.replicate.eq(0)].iloc[0];a=q[q.replicate.gt(0)].gain
        out.append(dict(horizon=h,metric=m,n=int(v.n),selected_model=v.variant,observed_gain=v.gain,nulls=len(a),
                  null_median=a.median(),null_p95=a.quantile(.95),tail_fraction=(1+a.ge(v.gain).sum())/(1+len(a))))
    write('representative-blocked-refit-reselection.csv',b)
    write('representative-blocked-refit-summary.csv',pd.DataFrame(out))
    save('representative-blocked-refit-design.json',receipts)


def risk():
    p=csv('india-risk-point-comparison-cases.csv.gz')
    q=csv('india-risk-path-comparison-cases.csv.gz')
    a=csv('india-protected-same-clock-path-cases.csv.gz')
    out=[];bounds=[]
    for h in ORIGINAL:
        for kind,frame,metrics in [
            ('point',p,('vol_mae','qlike','expand_brier','p_expand','actual_expand')),
            ('calibrated_paths',q,('rv_mae','qlike','range_crps','drawdown_crps','expand_brier','contract_brier','hit_down_brier',
                                  'hit_up_brier','rv_covered','range_covered','range_width')),
            ('same_clock_parent_paths',a,('vol_mae','variance_qlike','range_crps','drawdown_crps','expansion_brier','contraction_brier','touch_brier',
                                         'vol_coverage80','range_coverage80','range_width80'))]:
            frame=frame[frame.horizon.eq(h)].copy()
            if 'is_stress' in frame:
                frame=frame[~frame.is_stress]
            for scope,s in scopes(frame):
                z=s.groupby('model')[list(metrics)].agg('mean').reset_index()
                z['n']=z.model.map(s.groupby('model').size())
                out.append(z.assign(horizon=h,scope=scope,track=kind))
        for metric,ref in [('vol_mae','offshore_plus_domestic' if h==5 else 'GJR'),('qlike','offshore_plus_domestic' if h==5 else 'GJR'),
                           ('expand_brier','fixed_iv_rv' if h==5 else 'student_EGARCH')]:
            f=p[p.horizon.eq(h)].pivot(index='day',columns='model',values=metric)
            m=f.rsub(f[ref],axis=0)
            a0=block_intervals(m.to_numpy(),21,1100,SEED+211)
            bounds.append(a0.assign(horizon=h,reference=ref,model=m.columns,metric=metric,block=21))
        for metric,parent_key in [('range_crps','range_crps'),('drawdown_crps','drawdown_crps'),('rv_mae','vol_mae'),
                                  ('expand_brier','expansion_brier'),('contract_brier','contraction_brier')]:
            f=q[q.horizon.eq(h)&~q.is_stress].pivot(index='day',columns='model',values=metric)
            key='same_clock_IV' if h==5 else 'same_clock_GJR'
            old=a[a.horizon.eq(h)&a.model.eq(key)].set_index('day')[parent_key].reindex(f.index)
            m=f.rsub(old,axis=0)
            bounds.append(block_intervals(m.to_numpy(),21,1100,SEED+215).assign(horizon=h,reference=key,model=m.columns,metric=metric,block=21))
    write('india-risk-and-tail-leaderboard.csv',pd.concat(out,ignore_index=True))
    write('india-risk-matched-intervals.csv',pd.concat(bounds,ignore_index=True))


def controls():
    rng=np.random.default_rng(SEED)
    x=rng.normal(size=(220,3));y=(.17*x[:,0]+rng.normal(size=len(x)))[:,None]
    d=np.arange(len(x))//3
    a=train(x,y,d,(0,1,2))
    b=train(np.column_stack([x,x[:,0]]),y,d,(0,1,2,3))
    diff=float(np.abs(a.predict(x)-b.predict(np.column_stack([x,x[:,0]]))).max())
    assert diff<1.e-12
    cut=500
    q=pd.DataFrame(dict(mature_ns=[cut-1,cut,cut+1,cut-5],issue_ns=[100,100,100,cut],ret=[.1,.1,.1,.1],raw_daily_sigma=[.01]*4))
    assert eligible(q,cut).tolist()==[True,False,False,False]
    times=np.array([10,30,50,51],dtype='int64')
    v=np.array([1.,2.,3.,4.])
    scale=np.array([20,40,50],dtype='int64')
    ref=asof({'x':(times,v)},'x',scale)
    v[-1]=1.e9
    poison=asof({'x':(times,v)},'x',scale)
    assert np.array_equal(ref,poison)
    m=csv('analogue-law-members.csv.gz')
    z=csv('analogue-law-atlas.csv')
    assert not m.duplicated(['law','row']).any()
    b=m[['law','mature_ns']].merge(z[['law','issue_ns']],on='law',validate='m:1')
    assert b.mature_ns.lt(b.issue_ns).all()
    save('leakage-and-duplication-controls.json',dict(duplicate_factor_max_difference=diff,test_admitted=1,
           test_rejected_at_cutoff=1,test_rejected_later_outcomes=1,test_rejected_unissued_origin=1,future_feature_poison_max_change=float(np.max(abs(ref-poison))),
           analogue_memberships=len(m),analogue_unique_source_per_law=True,all_analogue_targets_strictly_matured=True))


def run(part='all'):
    if part in ('all','international'):
        international()
        controls()
    if part in ('all','india'):
        z=csv('india-forecast-cases.csv.gz')
        india(z)
        nulls(z)
    if part in ('all','india','risk'):
        risk()
    print('Matched evaluation and falsification complete for',part,flush=True)


if __name__=='__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else 'all')
