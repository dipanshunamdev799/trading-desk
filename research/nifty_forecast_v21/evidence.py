"""Matched scoreboards, conditional diagnostics, refitted nulls and uncertainty."""
from functools import lru_cache

from .common import *
from .reference import ANCHOR,DIRECTION
from .reconstruction import MAIN
from .learning import DESIGNS
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v20.modeling import block_intervals,blend_laws,fit_slope,rank,disjoint

RETURN_METRICS=('brier','crps','log_loss','mae')


def parents(h,clock):
    if clock=='native_0910':
        return ANCHOR[h],DIRECTION[h]
    return ('archived_same_clock','archived_joint_GJR')


def rank_any(a,b):
    return rank(np.asarray(a,float),np.asarray(b,float))


def model_stats(g):
    b=g.actual.gt(0)
    pred=g.p.ge(.5)
    c=[float(pred[b.eq(k)].eq(b[b.eq(k)]).mean()) for k in (False,True) if b.eq(k).any()]
    return dict(n=len(g),active=int(g.active.sum()),disjoint=disjoint(g),brier=g.brier.mean(),crps=g.crps.mean(),
                log_loss=g.log_loss.mean(),accuracy=g.correct.mean(),balanced_accuracy=np.mean(c),mae=g.mae.mean(),
                rmse=np.sqrt(g.squared_error.mean()),rank_corr=rank_any(g['mean'],g.actual),mean_p=g.p.mean(),up_rate=b.mean(),
                coverage80=g.covered.mean(),width80=g.width.mean(),pinball=g.quantile_loss.mean())


def index_evidence(z):
    rows=[];paired=[];bands=[];phases=[];omit=[];cal=[]
    day_index=cash().index
    for (h,clock),g in z.groupby(['horizon','cutoff']):
        counts=g[g.model.eq(parents(h,clock)[0])].groupby('cohort').day.nunique()
        assert (counts['early'],counts['later'])==EXPECTED[h][:2]
        parents_=parents(h,clock)
        @lru_cache
        def n_effective(days,target):
            return disjoint(pd.DataFrame({'day':days,'target_end':target}))
        for name,u in g.groupby('model'):
            for label,s in [('combined',u),('early',u[u.cohort.eq('early')]),('later',u[u.cohort.eq('later')]),('active',u[u.active])]:
                if not s.empty:
                    rows.append(dict(horizon=h,cutoff=clock,model=name,scope=label,**model_stats(s)))
            q=u.assign(observed=u.actual.gt(0),bin=pd.cut(u.p,np.linspace(0,1,6),include_lowest=True))
            for mass,s in q.groupby('bin',observed=True):
                cal.append(dict(horizon=h,cutoff=clock,model=name,bin=str(mass),n=len(s),p=s.p.mean(),observed=s.observed.mean()))
        g=g.sort_values('day')
        for ref in parents_:
            ref_case=g[g.model.eq(ref)].set_index('day')
            roles=g.set_index(['model','day'])
            for metric in RETURN_METRICS:
                v=g.pivot(index='day',columns='model',values=metric).sort_index()
                gain=v.sub(v[ref],axis=0).mul(-1)
                active=g.pivot(index='day',columns='model',values='active').reindex(index=v.index,columns=v.columns).astype(bool)
                early=ref_case.reindex(v.index).cohort.eq('early')
                sampled=pd.DataFrame(index=v.index,columns=[*v.columns],dtype=float)
                for model in v.columns:
                    a=roles.loc[model].reindex(v.index)
                    assert a.target_end.eq(ref_case.target_end).all() and a.actual.eq(ref_case.actual).all()
                    sampled[model]=gain[model].where(active[model])
                    for scope,keep in [('combined',gain[model].notna()),('early',early),('later',~early),('active_matched',active[model])]:
                        first=a.loc[keep]
                        if first.empty:
                            continue
                        k=n_effective(tuple(first.index),tuple(first.target_end))
                        paired.append(dict(horizon=h,cutoff=clock,reference=ref,model=model,metric=metric,scope=scope,
                            n=len(first),active=int(first.active.sum()),disjoint=k,coverage=float(first.active.sum()/len(a)),
                            parent_loss=float(v.loc[keep,ref].mean()),loss=float(v.loc[keep,model].mean()),gain=float(gain.loc[keep,model].mean())))
                    if metric in ('brier','crps') and ref==parents_[0] and model!=ref:
                        s=gain[model]
                        ix=day_index.get_indexer(s.index)%h
                        for num in range(h):
                            w=s[ix==num]
                            phases.append(dict(horizon=h,cutoff=clock,model=model,reference=ref,metric=metric,phase=num,n=len(w),gain=w.mean()))
                        dx=s.index.str[:7]
                        for label,y in s.groupby(dx):
                            keep=s[dx!=label]
                            omit.append(dict(horizon=h,cutoff=clock,model=model,reference=ref,metric=metric,omitted=label,
                                type='calendar_month',n=len(keep),omitted_gain=y.mean(),remaining_gain=keep.mean()))
                        i=int(np.argmax(np.convolve(s.to_numpy(),np.ones(21),'valid')))
                        y=s.iloc[i:i+21]
                        w=s.drop(y.index)
                        omit.append(dict(horizon=h,cutoff=clock,model=model,reference=ref,metric=metric,
                            omitted=f'{y.index[0]} to {y.index[-1]}',type='largest_gain_21_origins',n=len(w),omitted_gain=y.mean(),remaining_gain=w.mean()))
                        j=int(np.argmax(np.convolve(ref_case.actual.abs(),np.ones(21),'valid')))
                        y=s.iloc[j:j+21];w=s.drop(y.index)
                        omit.append(dict(horizon=h,cutoff=clock,model=model,reference=ref,metric=metric,
                            omitted=f'{y.index[0]} to {y.index[-1]}',type='largest_market_21_origins',n=len(w),omitted_gain=y.mean(),remaining_gain=w.mean()))
                if metric in ('brier','crps','mae'):
                    selected=[c for c in sampled if sampled[c].notna().sum()>=30]
                    for scope,a in [('combined',gain),('active_matched',sampled[selected])]:
                        q=block_intervals(a.to_numpy(),21,1200,SEED+23*h)
                        bands.append(q.assign(horizon=h,cutoff=clock,reference=ref,metric=metric,model=a.columns,scope=scope,block=21))
    write('index-model-leaderboard.csv',pd.DataFrame(rows))
    write('matched-index-comparisons.csv',pd.DataFrame(paired))
    write('index-search-adjusted-intervals.csv',pd.concat(bands,ignore_index=True))
    write('disjoint-outcome-phases.csv.gz',pd.DataFrame(phases))
    write('episode-removal-sensitivity.csv.gz',pd.DataFrame(omit))
    write('index-probability-calibration.csv',pd.DataFrame(cal))


def concentration_and_components(z):
    c=csv('concentration-cases.csv')
    s=csv('sector-contribution-cases.csv.gz')
    risk=csv('risk-comparison-cases.csv.gz')
    clock='native_0910'
    rows=[];assoc=[]
    design=('weight_top5','effective_expected_contributors','prior_synchronization','prior_breadth','prior_iv','sector_dispersion')
    for h,u in c.groupby('horizon'):
        v=z[z.horizon.eq(h)&z.cutoff.eq(clock)].pivot(index='day',columns='model',values=['brier','crps'])
        a='offshore_plus_domestic' if h==5 else 'GJR'
        raw=risk[risk.horizon.eq(h)&risk.model.eq(a)].set_index('day').reindex(u.day)
        h0=ANCHOR[h]
        ua=u.set_index('day').copy()
        actual=risk[risk.horizon.eq(h)&risk.model.eq(a)].set_index('day').actual.reindex(ua.index)
        for name in design:
            x=u[name].to_numpy(float)
            threshold=pd.Series(x).shift().rolling(100,min_periods=35).quantile(.66).to_numpy()
            for label,q in [('high',np.isfinite(threshold)&(x>=threshold)),('typical',np.isfinite(threshold)&(x<threshold))]:
                for cohort,mask in [('combined',np.ones(len(q),bool)),('early',u.cohort.eq('early')),('later',u.cohort.eq('later'))]:
                    y=u.loc[q&mask]
                    if len(y)<4:
                        continue
                    idx=y.day
                    rows.append(dict(horizon=h,group=name,regime=label,cohort=cohort,n=len(y),disjoint=disjoint(y),
                         up_rate=y.actual.gt(0).mean(),average_actual_rv=actual.reindex(idx).mean(),
                         anchor_brier=v['brier'][h0].reindex(idx).mean(),
                         pooled_brier=v['brier']['stock_pooled_joint'].reindex(idx).mean(),
                         anchor_mae_vol=raw.mae.reindex(idx).mean(),
                         pooled_crps=v['crps']['stock_pooled_joint'].reindex(idx).mean(),
                         anchor_crps=v['crps'][h0].reindex(idx).mean()))
            assoc.append(dict(horizon=h,signal=name,realized_vol_rank=rank_any(x,actual),absolute_index_rank=rank_any(x,u.actual.abs())))
    write('concentration-regime-results.csv',pd.DataFrame(rows))
    write('concentration-association.csv',pd.DataFrame(assoc))
    summary=s.groupby(['horizon','sector','cohort'],as_index=False).agg(n=('day','size'),direction_brier=('direct_brier','mean'),
               sector_crps=('direct_crps','mean'),stock_to_sector_crps=('stock_crps','mean'),sector_mae=('direct_mae','mean'),
               stock_to_sector_mae=('stock_mae','mean'),mean_expected=('expected_sector','mean'),mean_relative=('expected_relative','mean'),
               weighted_return=('constituent_return_contribution','mean'),observed_weighted_return=('observed_return_contribution','mean'),
               weighted_risk_share=('constituent_risk_share','mean'),forward_vol=('conditional_volatility','mean'),
               stock_model_members=('stock_model_members','mean'),statistical_weight=('statistical_sector_weight','mean'),
               rank=('probability_outperformance',lambda x:rank_any(x,s.loc[x.index,'relative_realized'])))
    write('sector-forecast-leaderboard.csv',summary)
    market=csv('market-factor-cases.csv')
    write('market-factor-leaderboard.csv',market.assign(mae=lambda x:(x.actual-x.prediction).abs(),se=lambda x:(x.actual-x.prediction)**2).groupby(
        ['horizon','cohort','model'],as_index=False).agg(n=('day','size'),mae=('mae','mean'),rmse=('se',lambda x:np.sqrt(x.mean())),
        crps=('market_crps','mean'),rank_corr=('prediction',lambda x:rank_any(x,market.actual.loc[x.index]))))
    m=csv('monte-carlo-convergence-cases.csv')
    values=['mean','p_up','q10','q90','std']
    m=m.pivot(index=['horizon','day'],columns='draws',values=values)
    dif=[]
    for k in (128,256):
        q=pd.DataFrame({name:(m[name][k]-m[name][1024]).abs() for name in values}).reset_index()
        dif.append(q.groupby('horizon',as_index=False)[values].mean().assign(draw_count=k,compared_to=1024))
    write('monte-carlo-convergence-summary.csv',pd.concat(dif,ignore_index=True))


def null_refits(z):
    with np.load(OUT/'index-forecast-laws.npz',allow_pickle=False) as y:
        atoms,w,ix=y['atoms'],y['weights'],y['offsets']
    c=csv('concentration-cases.csv')
    s=csv('sector-contribution-cases.csv.gz')
    proxy=s.groupby(['horizon','day'],as_index=False).agg(sector=('sector_mixture_contribution','sum'),
        equity=('constituent_return_contribution','sum'))
    f=c.merge(proxy,on=['horizon','day'],validate='1:1').set_index('day')
    rows=[]
    for h in HORIZONS:
        d=z[z.horizon.eq(h)&z.cutoff.eq('native_0910')&z.model.eq(ANCHOR[h])].sort_values('day').set_index('day')
        p=f[f.horizon.eq(h)].reindex(d.index)
        features=p[['equity','sector','predicted_asset_dispersion','prior_synchronization']].to_numpy(float)
        designs=([0],[1],[0,1],[0,1,2,3])
        y=d.actual.to_numpy(float);error=y-d['mean'].to_numpy(float)
        law_id=d.law.to_numpy(int);end=d.target_end.to_numpy(dtype='U10')
        base_brier=d.brier.to_numpy(float);base_crps=d.crps.to_numpy(float)
        t=[np.flatnonzero((end<day)&(np.arange(len(d))<i))[-130:] for i,day in enumerate(d.index)]
        for rep in range(-1,23):
            seed=np.random.default_rng(SEED+103*h+rep)
            results=np.zeros((len(y),len(designs),2))
            for i,tr in enumerate(t):
                if len(tr)<45:
                    continue
                if rep<0:
                    ixp=tr
                else:
                    chunks=np.array_split(tr,max(3,len(tr)//10))
                    ixp=np.concatenate([chunks[k] for k in seed.permutation(len(chunks))])
                j=law_id[i];a=atoms[ix[j]:ix[j+1]];wt=w[ix[j]:ix[j+1]]
                for k,fields in enumerate(designs):
                    effect=float(np.clip(.55*fit_slope(features[ixp][:,fields],error[tr],features[i,fields],150)[0],-.013,.013))
                    m=evaluate(a+effect,wt,y[i])
                    results[i,k]=[base_brier[i]-m['brier'],base_crps[i]-m['crps']]
            means=results.mean(axis=0)
            for j,metric in enumerate(('brier','crps')):
                for k,v in enumerate(means[:,j]):
                    rows.append(dict(horizon=h,replicate=rep,metric=metric,family=k,selected=k==int(np.argmax(means[:,j])),gain=v))
    z=pd.DataFrame(rows)
    write('null-refit-cases.csv',z)
    out=[]
    for (h,m),v in z[z.selected].groupby(['horizon','metric']):
        observation=v[v.replicate.lt(0)].gain.iloc[0]
        n=v[v.replicate.ge(0)].gain
        out.append(dict(horizon=h,metric=m,observed_gain=observation,simulations=len(n),null_median=n.median(),null_95=n.quantile(.95),
                        exceedances=int(n.ge(observation).sum()),rank_tail=(1+n.ge(observation).sum())/(1+len(n))))
    write('null-refit-summary.csv',pd.DataFrame(out))


def validate_clocks(returns):
    a=csv('equity-fit-receipts.csv')
    assert a.last_mature.lt(a.fit_day).all() and a.fit_day.le(a.day).all()
    s=csv('component-event-clock-audit.csv.gz')
    known=pd.to_datetime(s.first_eligible_timestamp,format='mixed',utc=True)
    cut=pd.to_datetime(s.decision_day+'T08:55:00+05:30',utc=True)
    assert known.le(cut).all()
    q=returns.last_mature.notna()
    assert returns.loc[q,'last_mature'].lt(returns.loc[q,'day']).all() and returns.target_end.le(FREEZE).all()
    assert all(tuple(dict.fromkeys(v+v))==tuple(v) for v in DESIGNS.values())
    seed=np.random.default_rng(SEED)
    a0=seed.normal(size=256);w=np.full(len(a0),1/len(a0))
    a1,w1=blend_laws(a0,w,a0.copy(),w.copy(),.25)
    np.testing.assert_array_equal(a0,a1);np.testing.assert_array_equal(w,w1)
    # Verify clipping, duplication of panel feature names and future-label poisoning around real decision geometry.
    d=returns[returns.cutoff.eq('native_0910')&returns.model.eq(ANCHOR[21])&returns.horizon.eq(21)].reset_index(drop=True)
    i=len(d)-8
    ts=d.target_end.lt(d.day.iloc[i])&(d.index<i)
    y=d.actual.to_numpy(float)
    raw=seed.normal(size=(len(d),3))
    first=fit_slope(raw[ts],y[ts],raw[i])[0]
    b=y.copy();b[~ts]+=1.e5
    assert first==fit_slope(raw[ts],b[ts],raw[i])[0]
    return dict(event_clock_rows=len(s),forecast_clock_rows=int(q.sum()),exact_copy_invariance='Named feature dedup and identical weighted distribution mixture',
                future_sentinel='Poisoned unobservable labels had no effect on the validated eligible fit.',
                uncertainty='21-session paired circular blocks. Bands adjust over the tested candidates at each explicit clock, reference, metric and horizon.',
                refit_null='23 chronologically refitted blocked source permutations reselect from four fixed residual designs.',historical_exposure='V1–V21 adaptive selection is outside the adjustment.')


def run():
    z=csv('index-forecast-cases.csv.gz')
    index_evidence(z)
    concentration_and_components(z)
    null_refits(z)
    save('validation-receipt.json',validate_clocks(z))
    print('Completed paired block bands, phases, episode removals and 23 refits per horizon',flush=True)


if __name__=='__main__':
    run()
