"""Matched comparisons, disagreement calibration, and holdout-style falsification."""
from .common import *
from .forecast import past_rows,asof_features,standardize,ridge,exact_unique,family_base,F,MIN
from .laws import Law,mix,expit,logit
from research.nifty_forecast_v20.modeling import block_intervals,rank
from research.nifty_forecast_v19.evidence import disjoint

RETURN_LOSS=('brier','crps','log_loss','mae','interval80','tail_down_brier','tail_up_brier','quantile_low_loss','quantile_high_loss')
PATH_LOSS=('range_crps','drawdown_crps','rv_mae','qlike','expansion_brier','contraction_brier','upper_range_tail_brier',
           'terminal_up_brier','terminal_down_brier','hit_up_brier','hit_down_brier','persistent_direction_brier','tail_drawdown_brier')


def scopes(frame):
    return [('combined',frame),('early',frame[frame.cohort.eq('early')]),('later',frame[frame.cohort.eq('later')]),
            ('active',frame[frame.active.astype(bool)])]


def scores(p):
    y=p.actual.gt(0)
    t=p.p.ge(.5)
    bal=np.mean([t[y==x].eq(y[y==x]).mean() for x in (False,True) if y.eq(x).any()])
    m={k:float(p[k].mean()) for k in RETURN_LOSS if k in p}
    return m|dict(n=len(p),active=int(p.active.sum()),disjoint=disjoint(p.rename(columns={'target':'target_end'})),
       episodes=pd.to_datetime(p.day).dt.to_period('W-SUN').nunique(),rank_corr=rank(p['mean'],p.actual),
       rmse=float(np.sqrt(p.squared_error.mean())),accuracy=p.correct.mean(),balanced_accuracy=bal,up_rate=y.mean(),
       probability=p.p.mean(),coverage80=p.cover80.mean(),width80=p.width80.mean(),pit_mean=p.pit.mean(),
       miss_lower=p.miss_low80.mean(),miss_upper=p.miss_high80.mean())


def risk_compare():
    x=csv('v23-path-cases.csv.gz')
    old=csv('india-protected-same-clock-path-cases.csv.gz',V22)
    old=old[old.model.isin(('same_clock_GJR','same_clock_IV'))].rename(columns={'vol_mae':'rv_mae','variance_qlike':'qlike','target_end':'target',
                      'vol_coverage80':'rv_covered','range_coverage80':'range_covered','range_width80':'range_width'})
    pp=csv('india-risk-path-comparison-cases.csv.gz',V22)
    pp=pp[pp.model.isin(('analogue_india_on_IV_GJR','analogue_global_on_IV_GJR'))].rename(columns={'expand_brier':'expansion_brier','contract_brier':'contraction_brier'})
    z=pd.concat([x,old,pp],ignore_index=True)
    cols=(*PATH_LOSS,'range_covered','range_width','range_sd','range_q90','rv_covered','rv_sd','gap_sd_crps','gap_share_crps',
          'volatility_evolution_crps','persistence_crps','excursion_crps','rebound_crps','foreign_paths')
    summary=[];bounds=[];active=[]
    for h,g in z.groupby('horizon'):
        parent='same_clock_IV' if h==5 else 'same_clock_GJR'
        v=x[x.horizon.eq(h)].pivot(index='day',columns='model',values='foreign_paths').sort_index()
        for model,k in g.groupby('model'):
            for scope,t in scopes(k):
                if len(t):
                    r={m:float(t[m].mean()) for m in cols}
                    summary.append(dict(horizon=h,clock='preauction_0855',model=model,scope=scope,n=len(t),
                               episodes=pd.to_datetime(t.day).dt.to_period('W-SUN').nunique(),**r))
        for ref in ('india_state_matched',parent,'analogue_india_on_IV_GJR'):
            for metric in PATH_LOSS:
                a=g.pivot(index='day',columns='model',values=metric).sort_index()
                if a[ref].notna().sum()<20:
                    continue
                a=a.loc[:,a.notna().sum()>=20]
                b=a.rsub(a[ref],axis=0)
                for k,paired in [('combined',b),('active_foreign_only',b.where(v.reindex(index=b.index,columns=b.columns).gt(0)))]:
                    paired=paired.loc[:,paired.notna().sum()>=20]
                    if not len(paired.columns):
                        continue
                    s=block_intervals(paired,21,1500,SEED+h)
                    bounds.append(s.assign(horizon=h,clock='preauction_0855',reference=ref,metric=metric,model=paired.columns,scope=k,block=21))
                for name,y in b.items():
                    for cohort,q in g[g.model.eq(ref)].groupby('cohort'):
                        w=y.reindex(q.day).dropna()
                        active.append(dict(horizon=h,model=name,reference=ref,metric=metric,cohort=cohort,gain=w.mean(),n=len(w)))
    write('path-risk-leaderboard.csv',pd.DataFrame(summary))
    write('path-risk-matched-intervals.csv.gz',pd.concat(bounds,ignore_index=True))
    write('path-risk-cohort-deltas.csv.gz',pd.DataFrame(active))
    r=csv('india-protected-point-risk-cases.csv.gz',V22)
    p=r.groupby(['horizon','model'],as_index=False).agg(n=('day','size'),mae=('mae','mean'),qlike=('qlike','mean'),brier=('brier','mean'))
    write('protected-volatility-and-expansion-leaderboard.csv',p)


def original(z):
    result=[];diffs=[];intervals=[];epochs=[];phase=[]
    calendar=cash().index
    for (h,clock),g in z.groupby(['horizon','clock']):
        for model,s in g.groupby('model'):
            for k,a in scopes(s):
                if len(a):
                    result.append(dict(horizon=h,clock=clock,model=model,kind=a.kind.iloc[0],scope=k,forecast_coverage=len(a)/len(s) if k=='active' else 1.,**scores(a)))
        t=g.set_index(['model','day']).sort_index()
        for parent in ('protected_direction','protected_distribution'):
            ar=t.loc[parent]
            kept=g.pivot(index='day',columns='model',values='active').astype(bool).reindex(ar.index)
            months=ar.index.str[:7]
            for metric in RETURN_LOSS:
                c=g.pivot(index='day',columns='model',values=metric).reindex(ar.index)
                d=c.rsub(ar[metric],axis=0)
                for column in d:
                    for label,eligible in [('combined',d[column].notna()),('early',ar.cohort.eq('early')),('later',ar.cohort.eq('later')),
                                           ('active_matched',kept[column])]:
                        if eligible.any():
                            diffs.append(dict(horizon=h,clock=clock,model=column,parent=parent,metric=metric,scope=label,n=eligible.sum(),
                              candidate=c.loc[eligible,column].mean(),protected=ar.loc[eligible,metric].mean(),gain=d.loc[eligible,column].mean()))
                    if metric not in ('brier','crps') or parent!='protected_distribution':
                        continue
                    a=d[column]
                    for k in range(h):
                        s=a[calendar.get_indexer(a.index)%h==k]
                        phase.append(dict(horizon=h,clock=clock,model=column,parent=parent,metric=metric,phase=k,n=s.count(),gain=s.mean()))
                    for month in np.unique(months):
                        sample=a[months!=month]
                        epochs.append(dict(horizon=h,clock=clock,model=column,parent=parent,metric=metric,omission_type='month',
                                           omitted=month,n=len(sample),gain_remaining=sample.mean(),omitted_gain=a[months==month].mean()))
                    for kind,series in [('largest_realized_episode',ar.actual.abs()),('largest_favorable_episode',a)]:
                        j=int(np.argmax(np.convolve(series,np.ones(21),'valid')))
                        omit=a.iloc[j:j+21];remain=a.drop(omit.index)
                        epochs.append(dict(horizon=h,clock=clock,model=column,parent=parent,metric=metric,omission_type=kind,
                                omitted=f'{omit.index[0]} to {omit.index[-1]}',n=len(remain),gain_remaining=remain.mean(),omitted_gain=omit.mean()))
                if metric not in ('brier','crps','log_loss','mae'):
                    continue
                for label,x in [('combined',d),('active_matched',d.where(kept))]:
                    x=x.loc[:,x.notna().sum()>=30]
                    for b in (21,42):
                        y=block_intervals(x,b,1500,SEED+17*h+b)
                        intervals.append(y.assign(horizon=h,clock=clock,parent=parent,metric=metric,scope=label,model=x.columns,block=b))
    l=pd.DataFrame(result)
    b=pd.DataFrame(diffs)
    write('original-horizon-leaderboard.csv',l)
    write('original-horizon-matched-comparisons.csv.gz',b)
    write('original-horizon-search-adjusted-intervals.csv.gz',pd.concat(intervals,ignore_index=True))
    write('leave-episodes-out.csv.gz',pd.DataFrame(epochs))
    write('disjoint-phase-comparisons.csv.gz',pd.DataFrame(phase))
    cost={'benchmark':0,'control':0,'baseline':0,'aggregation':2,'component':3,'calibration':1,'stability':2,'uncertainty':3}
    rows=[]
    for (h,clock),g in l[l.scope.eq('combined')].groupby(['horizon','clock']):
        p=g[['model','brier','crps','coverage80','kind']].copy()
        p['coverage_error']=abs(p.pop('coverage80')-.8)
        worst=l[l.horizon.eq(h)&l.clock.eq(clock)&l.scope.isin(('early','later'))].groupby('model').crps.max()
        p['worst_cohort_crps']=p.model.map(worst)
        p['complexity']=p.kind.map(cost)
        a=p[['brier','crps','coverage_error','worst_cohort_crps','complexity']].to_numpy()
        dominates=(a[:,None,:]<=a[None,:,:]).all(axis=2)&(a[:,None,:]<a[None,:,:]).any(axis=2)
        p['dominated_by']=dominates.sum(axis=0)
        rows.append(p.assign(horizon=h,clock=clock,on_pareto_frontier=p.dominated_by.eq(0)))
    write('forecast-pareto-frontier.csv',pd.concat(rows,ignore_index=True))
    old=csv('ensemble-exact-predictions.csv',root_for(11)).groupby(['horizon','model'],as_index=False).agg(
        n=('origin','size'),brier=('brier','mean'),crps=('crps','mean'))
    old['clock']='V11 archive historical cutoff as recorded; not assumed native 09:10'
    write('v11-exact-ensemble-benchmarks.csv',old)


def calibration(z,states):
    rel=[];summ=[];conditions=[];pits=[]
    cols=('observed_trailing_vol','family_prob_spread','positioning_concentration','analogue_effective_n','snapshot_probability',
          'breadth','recent_trend','earnings_activity','global_environment')
    for (h,clock),group in z.groupby(['horizon','clock']):
        ss=states[states.horizon.eq(h)&states.clock.eq(clock)].set_index('day').sort_index()
        for key,x0 in group.groupby('model'):
            x=x0.set_index('day').sort_index()
            y=x.actual.gt(0).astype(int)
            fc=x.p.clip(.002,.998)
            d=pd.DataFrame(dict(y=y,p=x.p,bin=pd.cut(x.p,np.linspace(0,1,11),include_lowest=True)))
            bins=d.groupby('bin',observed=True).agg(n=('p','size'),forecast=('p','mean'),observed=('y','mean')).reset_index()
            coeff=logit(fc.to_numpy())
            design=np.column_stack([np.ones(len(x)),coeff])
            v=np.array([0.,1.])
            for _ in range(12):
                p=expit(design@v)
                grad=design.T@(y-p)-.001*(v-np.array([0.,1.]))
                v+=np.linalg.solve((design*(p*(1-p))[:,None]).T@design+.001*np.eye(2),grad)
            freq=bins.n/len(x)
            reliability=float(freq@np.square(bins.forecast-bins.observed))
            resolution=float(freq@np.square(bins.observed-y.mean()))
            uncertainty=y.mean()*(1-y.mean())
            summ.append(dict(horizon=h,clock=clock,model=key,n=len(x),brier=x.brier.mean(),reliability=reliability,resolution=resolution,
                      uncertainty=uncertainty,within_bin_remainder=x.brier.mean()-(reliability-resolution+uncertainty),log_loss=x.log_loss.mean(),
                      diagnostic_calibration_intercept=v[0],diagnostic_calibration_slope=v[1] if np.std(coeff)>1.e-8 else np.nan,
                      coverage80=x.cover80.mean(),width80=x.width80.mean(),interval80=x.interval80.mean(),
                      tail_down=x.miss_low80.mean(),tail_up=x.miss_high80.mean()))
            rel.append(bins.assign(horizon=h,clock=clock,model=key,bin=bins.bin.astype(str)))
            hs=pd.cut(x.pit,np.linspace(0,1,11),include_lowest=True).value_counts(sort=False)
            for bin0,value in hs.items():
                pits.append(dict(horizon=h,clock=clock,model=key,bin=str(bin0),n=value,share=value/len(x)))
            for name in cols:
                a=ss[name].reindex(x.index)
                threshold=a.shift(1).rolling(90,min_periods=30).median()
                for lab,keep in [('higher',a.gt(threshold)),('lower',a.le(threshold))]:
                    r=x[keep]
                    if len(r):
                        conditions.append(dict(horizon=h,clock=clock,model=key,condition=name,group=lab,n=len(r),observed=r.actual.gt(0).mean(),
                             probability=r.p.mean(),brier=r.brier.mean(),crps=r.crps.mean(),coverage=r.cover80.mean(),width=r.width80.mean(),
                             tail_down=r.miss_low80.mean(),tail_up=r.miss_high80.mean(),fit_only_prior_median=True))
            for cohort,r in x.groupby('cohort'):
                conditions.append(dict(horizon=h,clock=clock,model=key,condition='original cohort',group=cohort,n=len(r),observed=r.actual.gt(0).mean(),
                     probability=r.p.mean(),brier=r.brier.mean(),crps=r.crps.mean(),coverage=r.cover80.mean(),width=r.width80.mean(),
                     tail_down=r.miss_low80.mean(),tail_up=r.miss_high80.mean(),fit_only_prior_median=False))
    write('probability-reliability-bins.csv.gz',pd.concat(rel,ignore_index=True))
    write('forecast-calibration-leaderboard.csv',pd.DataFrame(summ))
    write('conditional-calibration.csv.gz',pd.DataFrame(conditions))
    write('randomized-pit-histogram.csv.gz',pd.DataFrame(pits))


def disagreement(a):
    risk=csv('v23-path-cases.csv.gz')
    q=risk[risk.model.eq('india_state_matched')][['horizon','day','range_actual','expansion_event','upper_range_tail_event']]
    a=a.merge(q,on=['horizon','day'],validate='m:1')
    out=[];inter=[]
    control=['implied_volatility','observed_trailing_vol','ordinary_prob_spread','probability_parameter_se','feature_distance','snapshot_probability']
    added=['family_prob_spread','conditional_mean_disagreement','training_period_shift']
    for (h,clock),f in a.groupby(['horizon','clock']):
        z=f.sort_values('day').reset_index(drop=True)
        q=z[control+added].to_numpy(float)
        y=z[['future_abs_error','range_actual','expansion_event','tail_miss','conditional_loss_brier','conditional_loss_crps','upper_range_tail_event']].to_numpy(float)
        training_y=y.copy()
        training_y[:,[0,1,4,5]]=np.log(np.maximum(.0002,y[:,[0,1,4,5]]))
        mature=z.mature_ns.to_numpy()
        decisions=z.issue_ns.to_numpy()
        for i in range(len(z)):
            tr=past_rows(mature,decisions,int(decisions[i]))
            if len(tr)<MIN:
                continue
            c=np.ones(len(tr))
            for name,variables,lag in [('history',0,0),('known_risk_controls',len(control),0),('model_disagreement',q.shape[1],0),('delayed_disagreement',q.shape[1],5)]:
                a0=q[tr,:variables]
                point=q[i,:variables].copy()
                if lag:
                    point[len(control):]=q[max(0,i-lag),len(control):]
                if variables:
                    train,test=standardize(a0,point)
                else:
                    train=np.ones((len(tr),1));test=np.ones(1)
                for k,metric in enumerate(('abs_error','range','vol_expansion','terminal_tail_miss','direction_brier_error','distribution_crps_error','upper_range_tail')):
                    pred=float(test@ridge(train,training_y[tr,k],c,1.8))
                    discrete=k in (2,3,6)
                    guess=float(np.clip(pred,.01,.99) if discrete else np.exp(np.clip(pred,-9.,1.)))
                    loss=(guess-y[i,k])**2 if discrete else abs(guess-y[i,k])
                    out.append(dict(horizon=h,clock=clock,day=z.day[i],cohort=z.cohort[i],model=name,measure=metric,actual=y[i,k],point=guess,
                                    loss=loss,fit_n=len(tr),mature_ns=int(mature[tr].max()),decision_ns=int(decisions[i])))
    z=pd.DataFrame(out)
    for (h,clock,m),s in z.groupby(['horizon','clock','measure']):
        g=s.pivot(index='day',columns='model',values='loss').sort_index()
        delta=g.rsub(g.known_risk_controls,axis=0)
        p=block_intervals(delta,21,1500,SEED+h)
        inter.append(p.assign(horizon=h,clock=clock,measure=m,model=g.columns,reference='known_risk_controls'))
    write('disagreement-future-risk-cases.csv.gz',z)
    write('disagreement-risk-matched-intervals.csv',pd.concat(inter,ignore_index=True))
    write('disagreement-future-risk-leaderboard.csv',z.groupby(['horizon','clock','measure','model'],as_index=False).agg(
        n=('day','size'),loss=('loss','mean'),prediction=('point','mean'),actual=('actual','mean')))


def controls():
    t=np.array([5,11,12,14],dtype=int)
    x=np.array([2,4,4,10],dtype=int)
    ix=past_rows(t,x,11)
    assert ix.tolist()==[0]
    labels=np.array([1.,.2,.2,.7])
    base=labels[ix].mean()
    labels[1:]=1.e9
    assert labels[ix].mean()==base
    e=Law.build([-.02,.03],[.50,.50])
    twin=Law.build([.03,-.02,-.02],[.50,.22,.28])
    alt=Law.build([-.01,.02],[.68,.32])
    select=exact_unique([e.eq_id(),twin.eq_id(),alt.eq_id()])
    assert select.tolist()==[0,2]
    new=mix([e,alt],family_base(['a','b']))
    old=mix(np.array([e,twin,alt],dtype=object)[select],family_base(np.array(['a','a','b'])[select]))
    assert new.eq_id()==old.eq_id()
    # An exact regressor copy would otherwise change shrinkage. Remove its column using train-only signatures.
    x=np.column_stack([np.ones(20),np.arange(20)/20])
    z=np.column_stack([x,x[:,1]])
    y=np.linspace(.005,.03,20)
    choose=exact_unique([tuple(a) for a in z.T])
    e0=ridge(x,y,np.ones(len(y)),1.6)
    e1=ridge(z[:,choose],y,np.ones(len(y)),1.6)
    assert np.allclose(e0,e1,atol=1e-14,rtol=0)
    save('leakage-and-duplication-checks.json',dict(outcomes_at_or_after_cut_rejected=3,forecast_poison_max_difference=0.,
         exact_expert_copy_changes=0,exact_duplicate_feature_max_difference=float(np.max(abs(e0-e1))),scope='Explicit synthetic sentinels and observed timestamp receipts'))


def run(part='all'):
    if part in ('all','risk'):
        risk_compare()
    if part in ('all','return'):
        z=csv('v23-return-cases.csv.gz')
        a=csv('model-uncertainty-cases.csv.gz')
        original(z)
        calibration(z,a)
        disagreement(a)
        controls()
    print('Matched evidence complete for',part,flush=True)


if __name__=='__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else 'all')
