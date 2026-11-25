"""Matched model comparison, disjoint targets, calibration and refit/reselection controls."""
from .common import *
from research.nifty_forecast_v17.evidence import match,summarize

RETURNS=('brier','crps','log_loss','abs_error','sq_error','quantile_loss','interval_score','down_brier','up_brier')

def comparisons(x,key,metrics,parents):
    x=x.copy()
    if 'actual' in x and 'down1' in x:
        x['down_brier']=(x.down1-(x.actual<=-.01).astype(float))**2
        x['up_brier']=(x.up1-(x.actual>=.01).astype(float))**2
    return match(x,key,metrics,parents,True)

def group_parents(key,g):
    local=list(g[['model','parent']].drop_duplicates().itertuples(index=False,name=None))
    return list(dict.fromkeys(local+[(m,'clock_structural') for m in g.model.unique() if m not in ('V14_exact','V14_event_overlay')]+
        [(m,'component_plus_residual') for m in ('multi_timescale','fundamental_augmentation','expectation_repricing','fixed_event_mixture','event_conditioned_law')]))

def risk_parents(key,g):
    ref='risk_calibrated_iv' if 'risk_calibrated_iv' in set(g.model) else 'V17_postopen_cash_risk'
    names=list(g.model.unique())
    q=[(a,ref) for a in names]
    for a in ('scheduled_risk','fundamental_risk','scheduled_then_fundamental','non_price_risk','scheduled_risk_transition',
              'fundamental_risk_transition','scheduled_then_fundamental_transition'):
        for b in ('atm_centered_empirical_law','raw_atm_point_same_clock','protected_raw_iv','protected_GJR','protected_fixed_iv_rv','protected_student_EGARCH','protected_offshore_plus_domestic'):
            q.append((a,b))
    q.extend(('postopen_event_risk',k) for k in names if k.startswith('protected_postopen_'))
    return q

def barrier():
    z=csv('event-barrier-scores.csv.gz')
    metrics=('brier_by_1','touch_brier','conditional_brier','integrated_brier','event_time_log','brier_by_3','brier_by_5','brier_by_10','brier_by_21')
    contrasts=[('event_scale_on_IV','same_clock_IV'),('event_scale_on_IV','same_clock_GJR'),
               ('event_scale_on_IV','same_clock_GIFT_first'),('schedule_scale_on_GJR','same_clock_GJR'),('schedule_scale_on_GJR','same_clock_IV')]
    packed=[];matched=[]
    for (h,c),g in z.groupby(['horizon','cutoff']):
        for a,b in contrasts:
            t0=g[g.model.eq(a)].set_index(['day','barrier','side'])
            t1=g[g.model.eq(b)].set_index(['day','barrier','side'])
            if not len(t0) or not len(t1):continue
            p=t0.join(t1[list(metrics)],how='inner',rsuffix='_baseline')
            for key in metrics:
                if key not in p:continue
                t=p[p[key].notna()&p[key+'_baseline'].notna()].copy()
                if not len(t):continue
                count=t.reset_index().day.nunique()
                packed.append(dict(horizon=h,cutoff=c,candidate=a,control=b,metric=key,dates=count,side_barrier_cases=len(t)))
                d=t.groupby(level='day').agg(cohort=('cohort','first'),target_end=('target_end','first'),candidate=(key,'mean'),control=(key+'_baseline','mean')).reset_index()
                one=d[['day','cohort','target_end']].copy()
                left=one.assign(model=a,value=d.candidate)
                right=one.assign(model=b,value=d.control)
                for k in (left,right):k['slice']=key
                u=match(pd.concat([left,right],ignore_index=True),['slice'],['value'],lambda *_:[(a,b)],True)
                matched.append(u.assign(horizon=h,cutoff=c,metric=key,side_barrier_cases=len(t)))
    write('event-barrier-sample-counts.csv',pd.DataFrame(packed))
    write('event-barrier-matched.csv',pd.concat(matched,ignore_index=True).drop(columns='slice'))

def null_table(returns):
    base=csv('refit-null-case-gains.csv.gz')
    v=base.groupby(['horizon','seed','arm'],as_index=False).agg(brier=('brier_gain','mean'),crps=('crps_gain','mean'))
    maxima=v.groupby('seed')[['brier','crps']].max().reset_index()
    real=returns[(returns.cutoff=='preauction_0855')&(returns.control=='clock_structural')&
         returns.candidate.isin(['counts','text_given_counts','fundamental_augmentation'])&
         returns.metric.isin(['brier','crps'])]
    rows=[]
    for k in ('brier','crps'):
        a=real[real.metric.eq(k)]
        ref=a.loc[a.gain.idxmax()]
        rows.append(dict(metric=k,observed_selected_gain=ref.gain,candidate=ref.candidate,horizon=int(ref.horizon),
          null_replicates=len(maxima),null_median_selected_gain= float(maxima[k].median()),
          null_95_percentile=float(maxima[k].quantile(.95)),
          tail_probability=(1+int(maxima[k].ge(ref.gain).sum()))/(1+len(maxima))))
    write('refit-reselection-nulls.csv',maxima)
    write('refit-reselection-summary.csv',pd.DataFrame(rows))

def run():
    ret=csv('original-event-forecasts.csv.gz')
    leg=csv('protected-v14-event-overlays.csv.gz')
    po=csv('postopen-event-overlays.csv.gz')
    risk=csv('event-volatility-predictions.csv.gz')
    path=csv('event-path-scores.csv.gz')
    keys=['horizon','cutoff']
    s,r=summarize(pd.concat([ret,leg],ignore_index=True),keys)
    write('endpoint-leaderboard.csv',s)
    write('endpoint-calibration.csv',r)
    a=comparisons(ret,keys,RETURNS,group_parents)
    write('endpoint-paired-comparisons.csv',a)
    l=comparisons(leg,keys,RETURNS,lambda *_:[('V14_event_overlay','V14_exact')]).assign(subset='full')
    used=leg[leg.adapted.eq(1)][['horizon','day']].drop_duplicates()
    lr=comparisons(leg.merge(used,on=['horizon','day']),keys,RETURNS,lambda *_:[('V14_event_overlay','V14_exact')]).assign(subset='adjustment_mature')
    write('protected-v14-matched-overlays.csv',pd.concat([l,lr],ignore_index=True))
    a0=comparisons(po,['cutoff','target'],RETURNS,lambda _,g:[(m,'V17_postopen_parent') for m in g.model.unique()])
    write('postopen-event-matched.csv',a0)
    n,cal=summarize(risk,keys,'event')
    write('risk-leaderboard.csv',n)
    write('risk-calibration.csv',cal)
    av=comparisons(risk,keys,('brier','log_loss','crps','abs_error','sq_error','qlike'),risk_parents)
    write('risk-paired-comparisons.csv',av)
    metrics=('brier','endpoint_crps','range_crps','vol_mae','variance_qlike','energy','touch_brier','integrated_brier')
    pr=[('event_scale_on_IV','same_clock_IV'),('event_scale_on_IV','same_clock_GJR'),
        ('event_scale_on_IV','same_clock_GIFT_first'),('schedule_scale_on_GJR','same_clock_GJR'),('schedule_scale_on_GJR','same_clock_IV')]
    path_summary=path.groupby(['horizon','cutoff','model'],as_index=False).agg(n=('day','nunique'),**{k:(k,'mean') for k in metrics})
    write('joint-path-leaderboard.csv',path_summary)
    write('path-paired-comparisons.csv',comparisons(path,keys,metrics,lambda *_:pr))
    barrier()
    null_table(a)
    print('Evaluated',len(a),'original return contrasts and',len(av),'risk contrasts',flush=True)

if __name__=='__main__':
    run()
