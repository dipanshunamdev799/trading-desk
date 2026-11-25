"""Combine metrics, test stability, refit placebos and estimate detectable effects."""
from collections import defaultdict
from itertools import combinations
from scipy.stats import spearmanr
from .common import *
from .panel import GROUPS,CORE,WEEKLY,MONTHLY,cash
from .modeling import matrix,fit,timed,fit_slope,rank,block_intervals,block_counts,blend_laws,disjoint
from research.nifty_forecast_v17.weekly import evaluate
from .native import native_books

def read_tracks():
    meta={
       'native':'native-mechanism-cases.csv.gz','architecture':'architecture-cases.csv.gz','temporal':'temporal-cases.csv.gz',
       'complementarity':'complementarity-cases.csv.gz','retained_point_risk':'position-and-corporate-risk-cases.csv.gz',
       'joint_path':'coherent-risk-path-cases.csv.gz'}
    for name,path in meta.items():
        z=csv(path)
        if name=='joint_path':
            z['actual']=z.actual_endpoint
            z['mean']=z.endpoint_mean
            z['crps']=z.endpoint_crps
            z['mae']=z.endpoint_mae
            z['p']=z.p_up
            z['covered']=z.endpoint_coverage80
            z['width']=z.endpoint_width80
        z['track']=name
        yield name,z

def prior_names(m,q):
    if m=='architecture':
        yield from ((k,b) for k in q.model.unique() for b in ('archived_same_clock','archived_joint_GJR','A_one_shared_head') if k!=b)
    elif m=='native':
        bases=['exact_v14','v18_corporate_native'] if q.horizon.iloc[0]==5 else ['exact_v14','v19_position_native','bias_only']
        yield from ((k,b) for k in q.model.unique() for b in bases if k!=b)
    elif m=='temporal':
        yield from ((k,b) for k in q.model.unique() for b in ('direct_specialized','same_clock_neutral','unconditioned_joint') if k!=b)
    else:
        yield from ((r,q[q.model.eq(r)].parent.iloc[0]) for r in q.model.unique() if r!=q[q.model.eq(r)].parent.iloc[0])

def outcomes():
    stats=[];cases=[];intervals=[];phases=[];drops=[];cal=[]
    cols={'native':('brier','crps','mae','log_loss'),'architecture':('brier','crps','mae','log_loss'),
       'complementarity':('brier','crps','log_loss'),'temporal':('brier','crps','mae','log_loss'),
       'joint_path':('brier','crps','mae','vol_mae','vol_crps','range_crps','variance_qlike','touch_brier','integrated_brier','expansion_brier','contraction_brier','energy'),
       'retained_point_risk':('brier','q_like','mae','log_loss')}
    basis=cash().index
    for j,(name,z) in enumerate(read_tracks()):
        if 'squared_error' in z:z['rmse_point']=z.squared_error
        if 'sq_error' in z:z['rmse_point']=z.sq_error
        for (h,c),g in z.groupby(['horizon','cutoff']):
            ids=np.sort(g.day.unique())
            tests=defaultdict(list)
            for m,k in g.groupby('model'):
                for lbl,sel in [('combined',k),('early',k[k.cohort.eq('early')]),('later',k[k.cohort.eq('later')]),('active',k[k.active.eq(1)])]:
                    if sel.empty:continue
                    p=sel.p.to_numpy(float)
                    actual=sel.event.to_numpy(float) if 'event' in sel else sel.actual.gt(0).to_numpy(float)
                    good=(p>=.5)==(actual>=.5)
                    use=['p','log_loss','covered','width','range_coverage80','range_width80',*cols[name]]
                    detail={key:sel[key].mean() for key in dict.fromkeys(use) if key in sel and sel[key].notna().any()}
                    stats.append(dict(track=name,horizon=h,cutoff=c,model=m,scope=lbl,n=len(sel),active=int(sel.active.sum()),
                        intended=len(k),disjoint=disjoint(sel),rank_corr=rank(sel['mean'],sel.actual),
                        accuracy=good.mean(),balanced_accuracy=np.mean([good[actual==v].mean() for v in np.unique(actual)]),
                        rmse=float(np.sqrt(sel.rmse_point.mean())) if 'rmse_point' in sel else np.nan,**detail))
                alarm=k.event if 'event' in k else k.actual.gt(0)
                bins=pd.cut(k.p,np.linspace(0,1,6),include_lowest=True)
                for bin_,p0 in k.assign(observed=alarm,bin=bins).groupby('bin',observed=True):
                    cal.append(dict(track=name,horizon=h,cutoff=c,model=m,bin=str(bin_),n=len(p0),predicted=p0.p.mean(),observed=p0.observed.mean()))
            for a,b in prior_names(name,g):
                A=g[g.model.eq(a)].set_index('day').sort_index()
                B=g[g.model.eq(b)].set_index('day').sort_index()
                ids_ab=A.index.intersection(B.index)
                if not len(ids_ab):continue
                A=A.reindex(ids_ab);B=B.reindex(ids_ab)
                assert A.target_end.eq(B.target_end).all() and A.cohort.eq(B.cohort).all()
                active=A.active.eq(1)&B.active.eq(1)
                for k in cols[name]:
                    if not (k in A and k in B):continue
                    v=B[k]-A[k]
                    detail=dict(track=name,horizon=h,cutoff=c,model=a,parent=b,metric=k)
                    for lbl,keep in [('combined',v.notna()),('active_matched',active&v.notna()),
                                     ('earlier',A.cohort.eq('early')&v.notna()),('later',A.cohort.eq('later')&v.notna())]:
                        if keep.sum()==0:continue
                        sl=A.loc[keep].reset_index()
                        pscore=B.loc[keep,k].mean()
                        t=detail|dict(scope=lbl,n=int(keep.sum()),active=int(active[keep].sum()),disjoint=disjoint(sl),
                            coverage=int(active[keep].sum())/len(A),parent_loss=pscore,loss=A.loc[keep,k].mean(),gain=v[keep].mean())
                        cases.append(t)
                        if lbl=='active_matched' and keep.sum()>=25 and k in ('brier','crps','mae','q_like','vol_mae','range_crps','touch_brier'):
                            tests[k].append((t,v[keep]))
                    important=(name in ('native','architecture','temporal') and k in ('brier','crps') and b in ('exact_v14','archived_same_clock','direct_specialized'))
                    if important:
                        allv=v.dropna()
                        ph=basis.get_indexer(allv.index)%h
                        for p in range(h):
                            q=allv[ph==p]
                            phases.append(detail|dict(phase=p,n=len(q),gain=q.mean()))
                        pieces=allv.groupby(allv.index.str[:7]).agg(['sum','size'])
                        for month,w in pieces.iterrows():
                            if w['size']==len(allv):continue
                            drops.append(detail|dict(omitted=month,n=len(allv)-w['size'],
                                gain=(allv.sum()-w['sum'])/(len(allv)-w['size']),omission_type='calendar_month'))
                        extreme=A.actual.abs().rolling(21,center=True,min_periods=5).mean().idxmax()
                        p=A.index.get_loc(extreme)
                        bad=A.index[max(0,p-10):p+11]
                        q=allv[~allv.index.isin(bad)]
                        drops.append(detail|dict(omitted=f'{bad[0]} to {bad[-1]}',n=len(q),gain=q.mean(),omission_type='extreme_realized_episode'))
            for k,t in tests.items():
                a=np.column_stack([v.reindex(ids).to_numpy() for row,v in t])
                for n in (5,10,21,42):
                    res=block_intervals(a,n,1500,SEED+97*j+h+n)
                    for (line,_),pr in zip(t,res.to_dict('records')):
                        intervals.append(line|pr|dict(block=n,adjusted_family=len(t)))
    write('model-leaderboards.csv',pd.DataFrame(stats))
    write('complete-matched-comparisons.csv',pd.DataFrame(cases))
    write('matched-block-intervals.csv.gz',pd.DataFrame(intervals))
    write('probability-calibration.csv',pd.DataFrame(cal))
    write('all-disjoint-window-phases.csv',pd.DataFrame(phases))
    write('episode-omission-sensitivity.csv',pd.DataFrame(drops))
    # Component-level directional scores are separately keyed at the relevant outcome intervals.
    g=csv('component-case-scores.csv.gz')
    write('component-leaderboard.csv',g.groupby(['start_offset','end_offset','model','cohort'],as_index=False).agg(
      n=('day','size'),brier=('brier','mean'),crps=('crps','mean'),log_loss=('log_loss','mean'),
      mae=('mae','mean'),coverage=('covered','mean'),width=('width','mean')))

def gates_and_coef():
    g=csv('mechanism-regime-audit.csv')
    rows=[]
    masks=dict(all_=np.ones(len(g),bool),away_from_expiry=~g.near_expiry_or_roll,
         high_announcement=g.announcement_rank.ge(.70),other_announcement=g.announcement_rank.lt(.70),
         high_concentration=g.concentration_rank.ge(.70),other_concentration=g.concentration_rank.lt(.70),
         high_iv=g.volatility_rank.ge(.75),ordinary_iv=g.volatility_rank.lt(.75),
         rising_state=g.trend_rank.ge(.50),falling_state=g.trend_rank.lt(.50),
         reasonably_close_feature_state=g.feature_distance.le(1.1),distant_feature_state=g.feature_distance.gt(1.1))
    for k,live in masks.items():
        z=g[live]
        for (h,c),v in z.groupby(['horizon','cohort']):
            for scope,q in [('eligible',v),('active',v[v.active])]:
                rows.append(dict(horizon=h,cohort=c,regime=k,scope=scope,n=len(q),disjoint=disjoint(q),
                  mean_FII=q.FII_level.mean(),mean_IV=q.IV.mean(),mean_concentration_rank=q.concentration_rank.mean(),
                  mean_trend=q.rolling_return.mean(),mean_n_train=q.eligible_past.mean(),n_train_zeroes=int(q.eligible_past.eq(0).sum()),
                  model_disagreement=q.model_disagreement.mean(),v19_brier_gain=q.v19_brier_gain.mean(),v19_crps_gain=q.v19_crps_gain.mean(),
                  new_brier_gain=q.mechanism_brier_gain.mean(),new_crps_gain=q.mechanism_crps_gain.mean()))
    write('mechanism-regime-comparisons.csv',pd.DataFrame(rows))
    inventory={}
    for h,z in g.groupby('horizon'):
        inventory[h]=z.set_index('day').cohort.to_dict()
    rr=[]
    with gzip.open(OUT/'native-fit-receipts.ndjson.gz','rt',encoding='utf-8') as w:
        for line in w:
            d=json.loads(line)
            for col,b in zip(d['columns'],d['parameters'][1:]):
                rr.append(dict(horizon=d['horizon'],model=d['model'],cohort=inventory[d['horizon']][d['day']],field=col,coefficient=b,n=d['n']))
    c=pd.DataFrame(rr)
    f=c.groupby(['horizon','model','cohort','field'],as_index=False).coefficient.agg(
        median='median',p10=lambda s:s.quantile(.1),p90=lambda s:s.quantile(.9),positive=lambda s:s.gt(0).mean(),fit_count='size')
    write('coefficient-stability.csv',f)

def refit_nulls():
    f=csv('asof-features.csv.gz').query("cutoff == 'preauction_0855'").set_index('day')
    y=csv('multi-horizon-targets.csv').set_index('day').reindex(f.index)
    native=native_books()
    bases={'corporate':GROUPS['corporate_announcements']+GROUPS['structured_financials'],
           'positioning':GROUPS['participant_futures'],'financial':GROUPS['financial_rotation'],'volatility':GROUPS['atm_iv']}
    xs={k:matrix(f,col) for k,col in bases.items()}
    days=f.index.to_numpy(dtype='U10');cut=f.decision.str[:10].to_numpy(dtype='U10')
    record=[];sentinel=[];power=[]
    for h in HORIZONS:
        target=y[f'return_0_{h}'].to_numpy(float)
        en=y[f'end_0_{h}'].fillna('9999-12-31').to_numpy(dtype='U10')
        ix=np.flatnonzero(y[f'cohort_{h}'].notna())
        err=np.full(len(y),np.nan)
        for i in ix:
            a,w=native[h,days[i],'V14_exact']
            err[i]=target[i]-np.log1p(w@a)
        use=ix[::3]
        for i in use:
            t=timed(en,cut,i,err)
            if len(t)<38:continue
            a,w=native[h,days[i],'V14_exact'];val=np.expm1(target[i])
            base=evaluate(a,w,val)
            for label,x in xs.items():
                if not np.isfinite(x[i]).any():continue
                real,fit0=fit_slope(x[t],err[t],x[i])
                if i in use[::19] and label in ('positioning','corporate'):
                    copied=np.column_stack((x,x[:,0],x[:,1]))
                    s,_=fit_slope(copied[t],err[t],copied[i])
                    poison=x.copy();poison[i+1:]=1.e12
                    response=err.copy();response[en>=cut[i]]=-1.e18
                    ts=timed(en,cut,i,response)
                    q,_=fit_slope(poison[ts],response[ts],poison[i])
                    la,wa=blend_laws(a,w,a.copy(),w.copy(),.30)
                    assert abs(q-real)<1.e-12 and abs(s-real)<1.e-12 and np.array_equal(la,a) and np.array_equal(wa,w)
                    sentinel.append(dict(day=days[i],horizon=h,family=label,last_mature=max(en[t]),duplicate_delta=abs(s-real),future_delta=abs(q-real)))
                for seed in range(-1,23):
                    if seed==-1:
                        estimate=real
                    else:
                        rng=np.random.default_rng(SEED+seed)
                        blocks=np.array_split(np.arange(len(t)),max(2,len(t)//21))
                        j=np.concatenate([blocks[k] for k in rng.permutation(len(blocks))])
                        if seed%2==0:
                            estimate,_=fit_slope(x[t[j]],err[t],x[i])
                        else:
                            estimate,_=fit_slope(x[t],err[t[j]],x[i])
                    shift=np.clip(.58*estimate,-.012,.012)
                    valq=evaluate(np.expm1(np.log1p(a)+shift),w,val)
                    record.append(dict(horizon=h,seed=seed,family=label,day=days[i],last_mature=max(en[t]),
                                       brier_gain=base['brier']-valq['brier'],crps_gain=base['crps']-valq['crps']))
    z=pd.DataFrame(record)
    write('v20-refit-null-cases.csv.gz',z)
    strength=z.groupby(['horizon','family','seed'])[['brier_gain','crps_gain']].mean().groupby('seed').max()
    n=[]
    for k,v in strength.items():
        actual=v[-1]
        sim=v[v.index>=0]
        n.append(dict(metric=k,observed=actual,null_median=sim.median(),null_95=sim.quantile(.95),
                       exceedances=int(sim.ge(actual).sum()),runs=len(sim),rank_tail=(int(sim.ge(actual).sum())+1)/(len(sim)+1)))
    write('v20-refit-null-summary.csv',pd.DataFrame(n))
    write('future-information-sentinels.csv',pd.DataFrame(sentinel))
    h0=csv('native-audit-cases.csv.gz').query("track == 'parent_replay'")
    power=[]
    for h in HORIZONS:
        z=h0[h0.horizon.eq(h)]
        model='V14_event_overlay' if h==5 else 'V14_plus_positions'
        q=z[z.model.eq('V14_exact')].set_index('day')
        v=z[z.model.eq(model)].set_index('day').reindex(q.index)
        for k in ('brier','crps'):
            y=q[k]-v[k]
            for length in (5,10,21,42):
                rng=np.random.default_rng(SEED+h+length)
                weights=block_counts(len(y),length,1000,rng)
                residual=y.to_numpy()-y.mean()
                noise=(weights@residual)/len(y)
                limit=np.quantile(abs(noise),.95)
                detectable=max(0.,limit-np.quantile(noise,.20))
                power.append(dict(horizon=h,metric=k,block=length,n=len(y),disjoint=disjoint(q.reset_index()),
                     mean_gain=y.mean(),threshold_two_sided_95=limit,approx_80_percent_detectable_gain=detectable,
                     estimated_power_at_observed_gain=float((abs(noise+y.mean())>limit).mean()),draws=len(noise)))
    write('predictability-power-simulation.csv',pd.DataFrame(power))

def new_source_associations():
    panel=csv('asof-features.csv.gz').query("cutoff == 'preauction_0855'")
    y=csv('multi-horizon-targets.csv')
    g=panel.merge(y,on=['day','origin'],validate='1:1')
    tgt=csv('original-target-panel.csv',V17)[['day','gap','initial_rth','original1']]
    j=g.merge(tgt,on='day',validate='1:1')
    out=[]
    for var in ('gift_proxy','eq6','domestic_rotation_finance','FII_index_futures_d21','count9'):
        for k in ('gap','initial_rth','original1','return_0_5','return_5_21'):
            t=j[[var,k]].dropna()
            out.append(dict(feature=var,target=k,n=len(t),spearman=rank(t[var],t[k])))
    write('opening-and-late-associations.csv',pd.DataFrame(out))
    c=csv('first-release-cpi.csv')
    tests=[]
    cal=pd.to_datetime(g.decision,utc=True,format='mixed')
    for i,r in c.sort_values('eligible').iterrows():
        next_=np.flatnonzero(cal.ge(pd.Timestamp(r.eligible).tz_convert('UTC')))
        if not len(next_):continue
        v=g.iloc[next_[0]]
        tests.append(dict(release=r.release,eligible=r.eligible,first_nifty_day=v.day,observed_month=r.observed_month,mom_first=r.mom_first,
              return_1=v.return_0_1,return_5=v.return_0_5,return_21=v.return_0_21,late_6_21=v.return_5_21,risk_5=v.risk_0_5))
    d=pd.DataFrame(tests,columns=['release','eligible','first_nifty_day','observed_month','mom_first','return_1','return_5','return_21','late_6_21','risk_5'])
    write('macro-release-nifty-associations.csv',d)
    k=[]
    for z in ('return_1','return_5','return_21','late_6_21','risk_5'):
        t=d[['mom_first',z]].dropna()
        k.append(dict(target=z,n=len(t),rank=rank(t.mom_first,t[z])))
    write('macro-release-summary.csv',pd.DataFrame(k))

def main():
    outcomes()
    gates_and_coef()
    refit_nulls()
    new_source_associations()
    s=csv('future-information-sentinels.csv')
    a=csv('native-source-clock-audit.csv')
    assert len(a)==482 and a.participant_guard.le(a.parent_decision).all()
    assert s.last_mature.lt(s.day).all()
    save('validation-receipt.json',dict(sentinels=len(s),native_timing_cases=len(a),checked_within_time='Locations, risk laws, and future component forecasts use distinct archives with exact decision clocks.',
      uncertainty='Paired circular date blocks, max standardized error by registered family. Losing months and extreme episodes are omitted one at a time. All original disjoint phases are retained.',
      null='23 rotated/blocked/shuffled fits on the same thinned mature past sample. Best arm reselected within each draw.',
      limitations='Native parent and V19 historical comparisons share data exposed across versions. Power conditional on the observed paired error process. Flow timing uses explicit allowances.'))
    print('Evidence, robustness, calibration and historical power checks complete',flush=True)

if __name__=='__main__':
    main()

