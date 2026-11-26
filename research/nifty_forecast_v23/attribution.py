"""Stress-test the domestic shape result and re-simulate the leading risk controls."""
from .common import *
from .laws import Law,loaded,piece,metrics,logshape,mix
from .paths import Donors,scale_paths,synth,profile,POINT
from research.nifty_forecast_v16.paths import logs_to_path
from research.nifty_forecast_v20.modeling import block_intervals


def shape():
    z=csv('v23-return-cases.csv.gz')
    arr=loaded(OUT,'v23-return-laws.npz')
    s=z[z.model.isin(('protected_distribution','protected_direction','component_historical_shape_only'))]
    rows=[]
    for key,p in s.groupby(['horizon','clock','day']):
        h,clock,day=key
        p=p.set_index('model')
        a=piece(arr,int(p.law.protected_distribution))
        b=piece(arr,int(p.law.component_historical_shape_only))
        c=piece(arr,int(p.law.protected_direction))
        mu,scale,_=logshape(a)
        abs_res=np.abs(np.log1p(b.quantiles((np.arange(192)+.5)/192))-mu)
        sym=Law.build(np.expm1(np.r_[-abs_res,abs_res]))
        sym=sym.transform(location=mu,scale=scale/max(.001,logshape(sym)[1]))
        candidates={
            'unchanged_distribution_parent':a,'unchanged_direction_parent':c,
            'domestic_shape_full':b,'parent_with_domestic_sign_mass':a.reweight_sign(b.positive()),
            'domestic_shape_with_parent_sign_mass':b.reweight_sign(a.positive()),
            'symmetrized_domestic_shape':sym,'half_parent_half_domestic':mix([a,b],[.50,.50]),
        }
        for name,law in candidates.items():
            loc,spread,skew=logshape(law)
            q=p.loc['protected_distribution']
            rows.append(dict(horizon=h,clock=clock,day=day,cohort=q.cohort,model=name,log_location=loc,log_scale=spread,asymmetry=skew,
                       **metrics(law,q.actual,h)))
    f=pd.DataFrame(rows)
    a=[];q=[];mass=[]
    for (h,c),z in f.groupby(['horizon','clock']):
        for label,b in [('combined',z),*z.groupby('cohort')]:
            u=b.groupby('model',as_index=False).agg(n=('day','size'),brier=('brier','mean'),crps=('crps','mean'),
                      probability=('p','mean'),var=('var','mean'),mean=('mean','mean'),coverage80=('cover80','mean'),width80=('width80','mean'),
                      log_location=('log_location','mean'),log_scale=('log_scale','mean'),asymmetry=('asymmetry','mean'))
            a.append(u.assign(horizon=h,clock=c,scope=label))
            p=b[b.model.eq('domestic_shape_full')].set_index('day')
            for ref in ('unchanged_distribution_parent','unchanged_direction_parent'):
                r=b[b.model.eq(ref)].set_index('day').reindex(p.index)
                err=r.p-r.actual.gt(0)
                shift=p.p-r.p
                average=shift.mean()
                constant=-2*err.mean()*average-average**2
                varying=-2*((err-err.mean())*(shift-average)).mean()-shift.var(ddof=0)
                gain=(r.brier-p.brier).mean()
                assert abs(constant+varying-gain)<1.e-11
                mass.append(dict(horizon=h,clock=c,scope=label,reference=ref,n=len(p),realized_up=p.actual.gt(0).mean(),
                         parent_mean_probability=r.p.mean(),shape_mean_probability=p.p.mean(),brier_gain=gain,
                         uniform_mean_shift_gain=constant,date_varying_gain=varying))
        for m in ('brier','crps'):
            side=z.pivot(index='day',columns='model',values=m)
            change=side.rsub(side.unchanged_direction_parent,axis=0)
            for b in (21,42):
                q.append(block_intervals(change,b,1800,SEED+b+h).assign(horizon=h,clock=c,block=b,metric=m,model=change.columns))
    write('domestic-shape-attribution-cases.csv.gz',f)
    write('domestic-shape-attribution-leaderboard.csv',pd.concat(a,ignore_index=True))
    write('domestic-shape-attribution-intervals.csv',pd.concat(q,ignore_index=True))
    write('domestic-shape-brier-decomposition.csv',pd.DataFrame(mass))
    print('Shape attribution',len(f),'component cases.',flush=True)


def repeat_path_scores():
    from .paths import K
    x=csv('international-feature-panel.csv.gz',V22)
    raw=np.load(V22/'local-observed-paths.npz')
    bench=csv('v23-path-cases.csv.gz',usecols=['horizon','day','threshold','range_actual','rv_actual','drawdown_actual']).drop_duplicates(['horizon','day']).set_index(['horizon','day'])
    anchors=csv('india-protected-point-risk-cases.csv.gz',V22)
    rows=[]
    for h in HORIZONS:
        donors=Donors(h,x,raw)
        q=anchors[anchors.horizon.eq(h)&anchors.model.eq(POINT[h])].set_index('day')
        for t in donors.x[donors.x.cohort.notna()].itertuples(index=False):
            j=t.row;day=t.day
            actual=bench.loc[(h,day),:]
            anchor=float(q.loc[day].pred_vol)
            ix=np.flatnonzero(donors.good&(donors.mature<t.issue_ns)&(donors.issue>=t.issue_ns-365*DAY)&(donors.market=='india'))
            assert len(ix)>K
            d=donors.p[ix,0,:].astype(float)/donors.sigma[ix,None]
            for seed in (1,2):
                rng=np.random.default_rng(SEED+20*j+391*seed+h)
                daily=d[rng.integers(len(d),size=(4096,h))]
                z=rng.standard_normal((4096,h));g=rng.standard_normal((4096,h));b=rng.standard_normal((4096,h,16),dtype=np.float32)
                for n in (1024,4096):
                    variants={
                        'india_independent_days':scale_paths(logs_to_path(daily[:n]),anchor),
                        'constant_vol_diffusion':synth(h,anchor,z[:n],g[:n],b[:n]),
                        'student_t_gjr_same_anchor':synth(h,anchor,z[:n],g[:n],b[:n],True),
                    }
                    for name,paths in variants.items():
                        stat=profile(paths)
                        rv=stat['rv']
                        event=actual.rv_actual>1.25*actual.threshold
                        p=float(np.mean(rv>1.25*actual.threshold))
                        rows.append(dict(horizon=h,day=day,model=name,n_draws=n,seed=seed,anchor=anchor,
                             range_crps=Law.build(stat['range']).crps(actual.range_actual),range_coverage=int(
                                 np.quantile(stat['range'],.10)<=actual.range_actual<=np.quantile(stat['range'],.90)),
                             drawdown_crps=Law.build(stat['drawdown']).crps(actual.drawdown_actual),rv_mae=abs(rv.mean()-actual.rv_actual),
                             expansion_brier=(p-event)**2,last_training_maturity=int(donors.mature[ix].max()),issue_ns=t.issue_ns))
        print('High-budget path robustness finished for',h,'sessions.',flush=True)
    v=pd.DataFrame(rows)
    write('larger-simulation-path-cases.csv.gz',v)
    write('larger-simulation-path-summary.csv',v.groupby(['horizon','model','n_draws','seed'],as_index=False).agg(
           n=('day','size'),range_crps=('range_crps','mean'),drawdown_crps=('drawdown_crps','mean'),
           volatility_mae=('rv_mae','mean'),range_coverage=('range_coverage','mean'),expansion_brier=('expansion_brier','mean')))


def large_path_comparisons():
    a=csv('larger-simulation-path-cases.csv.gz')
    a=a[a.n_draws.eq(4096)].groupby(['horizon','day','model'],as_index=False).mean(numeric_only=True)
    p=csv('india-protected-same-clock-path-cases.csv.gz',V22)
    q=csv('v23-path-cases.csv.gz')
    rows=[]
    for h in HORIZONS:
        reference='same_clock_IV' if h==5 else 'same_clock_GJR'
        protected=p[p.horizon.eq(h)&p.model.eq(reference)].set_index('day')
        sub=q[q.horizon.eq(h)&q.model.eq('india_state_matched')].set_index('day')
        for metric,old_metric in [('range_crps','range_crps'),('drawdown_crps','drawdown_crps'),('expansion_brier','expansion_brier')]:
            table=a[a.horizon.eq(h)].pivot(index='day',columns='model',values=metric).sort_index()
            for r,anchor in ((reference,protected),('india_state_matched',sub)):
                gains=table.rsub(anchor[old_metric].reindex(table.index),axis=0)
                for b in (21,42):
                    rows.append(block_intervals(gains,b,1600,SEED+239*h+b).assign(horizon=h,model=table.columns,reference=r,metric=metric,block=b))
    write('larger-simulation-path-matched-intervals.csv',pd.concat(rows,ignore_index=True))


if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='paths':
        repeat_path_scores()
        large_path_comparisons()
    else:
        shape()
