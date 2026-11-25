"""Diagnose severe errors with separated as-of inputs and realized path facts."""
from .common import *
from .diagnostics import disjoint
from .evaluate import EXPECTED, V13_END

FORECAST_SIGNALS=('atm','trailing','atm1','iv_skew','term_slope','breadth5','breadth21','finance','sector_sync','jump_share_5',
                  'vix_move','fx_shock','oil_shock','sign_streak','overnight_share','trade_q_up3','trade_q_down3')
OUTCOMES=('endpoint_return','volatility','high','low','range','peak_shock_share','aligned_fraction','max_daily',
          'max_gap','net_overnight','net_intraday','vol_first','vol_last','speed','drawdown','rebound')


def model_winners(a,h,k,limit=4):
    m=a[a.horizon.eq(h)&a.cohort.eq('combined')&a.n.eq(EXPECTED[h])&a[k].notna()]
    return m.nsmallest(limit,k).model.tolist()


def run():
    scores=pd.read_csv(OUT/'path-marginals.csv.gz',low_memory=False)
    old_paths=pd.read_csv(V13/'distribution-predictions.csv',low_memory=False)
    old_exact=pd.read_csv(V13/'exact-and-analytic-path-controls.csv',low_memory=False)
    old_paths=pd.concat([old_paths[old_paths.model.isin(['diffusion_iv','iv_scaled','rv_scaled'])],
                        old_exact[old_exact.model.eq('empirical_exact')]],ignore_index=True)
    old_paths['model']='V13_'+old_paths.model.replace({'empirical_exact':'empirical_range'})
    old_paths=old_paths.rename(columns={'p':'p_up'})
    endpoint=pd.read_csv(OUT/'endpoint-attribution.csv')
    benchmarks=pd.read_csv(OUT/'benchmark-endpoint-origins.csv',low_memory=False).rename(columns={'p':'p_up'})
    benchmarks['model']=benchmarks.model.map(V13_END)
    benchmarks['target']='endpoint_return'
    ends=pd.concat([scores[scores.target.eq('endpoint_return')],endpoint,benchmarks,
                   old_paths[old_paths.target.eq('endpoint_return')]],ignore_index=True)
    risk=pd.read_csv(OUT/'risk-scores-per-origin.csv')
    vol=pd.read_csv(OUT/'volatility-leaderboard.csv')
    dist=pd.read_csv(OUT/'endpoint-leaderboard.csv')
    lead=pd.read_csv(OUT/'path-marginal-leaderboard.csv')
    passage=pd.read_csv(OUT/'path-passage.csv.gz',low_memory=False,dtype={'barrier':str})
    prior_touch=pd.read_csv(V13/'barrier-predictions.csv.gz',low_memory=False,dtype={'barrier':str})
    analytic=pd.read_csv(V13/'exact-and-analytic-barrier-controls.csv',low_memory=False,dtype={'barrier':str})
    prior_touch=pd.concat([prior_touch[prior_touch.model.isin(['diffusion_iv','iv_scaled'])],
                           analytic[analytic.model.isin(['analytic_iv_diffusion','empirical_exact'])]],ignore_index=True)
    prior_touch=prior_touch[prior_touch.barrier.isin(list('01234'))&
                          prior_touch.event.isin(['upper_touch','lower_touch'])].copy()
    prior_touch['model']='V13_'+prior_touch.model
    prior_touch['side']=prior_touch.event.str.split('_').str[0]
    prior_touch['brier']=(prior_touch.p-prior_touch.actual)**2
    passage=pd.concat([passage,prior_touch.rename(columns={'p':'p_touch'})],ignore_index=True)
    touch=pd.read_csv(OUT/'touch-and-passage-family.csv')
    warning=pd.read_csv(OUT/'failure-warning-forecasts.csv')
    anatomy={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    input_={h:matrix(f'features-{h}.csv') for h in HORIZONS}
    counts=[]
    misses=[]
    temporal=[]
    worries=[]
    removal=[]
    october=[]
    for h in HORIZONS:
        y,x=anatomy[h],input_[h]
        yq=y[y.cohort.notna()]
        for a,b in [('up','q90'),('down','q10')]:
            z=ends[ends.horizon.eq(h)].copy()
            z['failure']=(z.actual-z[b]) if a=='up' else (z[b]-z.actual)
            z=z[z.failure.gt(0)]
            for model in list(dict.fromkeys(model_winners(dist,h,'crps')+['V13_week_CRPS','V13_IV_scaled_symmetric','constant_iv','joint_tail_width'])):
                f=z[z.model.eq(model)].nlargest(8,'failure')
                for r in f.itertuples():
                    misses.append(dict(horizon=h,model=model,kind='unexpected_'+a,origin=r.origin,
                                      loss=r.failure,prediction=getattr(r,b),actual=r.actual))
        z=ends[ends.horizon.eq(h)]
        for metric in ['brier','crps']:
            for model in model_winners(dist,h,metric):
                for r in z[z.model.eq(model)].nlargest(8,metric).itertuples():
                    misses.append(dict(horizon=h,model=model,kind='largest_'+metric,origin=r.origin,
                                      loss=getattr(r,metric),prediction=r.p_up if metric=='brier' else r.predicted_mean,actual=r.actual))
        z=risk[risk.horizon.eq(h)].assign(shortfall=lambda f:f.actual-f.prediction)
        for model in list(dict.fromkeys(model_winners(vol,h,'mae')+['raw_iv','V13_GJR'])):
            for r in z[z.model.eq(model)&z.shortfall.gt(0)].nlargest(8,'shortfall').itertuples():
                misses.append(dict(horizon=h,model=model,kind='volatility_underestimate',origin=r.origin,
                                  loss=r.shortfall,prediction=r.prediction,actual=r.actual))
        a=pd.concat([scores[scores.horizon.eq(h)&scores.target.eq('range')],
                     old_paths[old_paths.horizon.eq(h)&old_paths.target.eq('range')]],ignore_index=True)
        a['shortfall']=a.actual-a.q90
        panels=list(dict.fromkeys(model_winners(lead[lead.target.eq('range')],h,'crps')+
                     ['constant_iv','path_mixture','joint_pit','joint_tail_width','jump_diffusion']))
        for model in panels:
            for r in a[a.model.eq(model)&a.shortfall.gt(0)].nlargest(8,'shortfall').itertuples():
                misses.append(dict(horizon=h,model=model,kind='range_underestimate',origin=r.origin,
                                  loss=r.shortfall,prediction=r.q90,actual=r.actual))
        flags=a[a.model.isin(panels)].assign(miss=lambda z:z.actual>z.q90)
        aggregates=flags.groupby('origin').agg(models=('model','size'),under=('miss','sum'),average_q90=('q90','mean'),
                                               actual=('actual','first')).reset_index()
        aggregates['horizon']=h
        temporal.extend(aggregates.to_dict('records'))
        b=passage[passage.horizon.eq(h)&passage.barrier.isin(list('01234'))]
        for model in model_winners(touch,h,'brier')+['constant_iv','gjr_iv']:
            for r in b[b.model.eq(model)].nlargest(10,'brier').itertuples():
                misses.append(dict(horizon=h,model=model,kind='large_barrier_error',origin=r.origin,
                                  loss=r.brier,prediction=r.p_touch,actual=r.actual,barrier=r.threshold,side=r.side,
                                  actual_time=r.actual_time))

        s=warning[warning.horizon.eq(h)].dropna().copy()
        for day,r in s.set_index('origin').iterrows():
            prior=s[s.origin.map(y.endpoint).lt(day)]
            if prior.empty:
                continue
            prob=(prior.actual.sum()+.75)/(len(prior)+1.5)
            worries.append(dict(horizon=h,origin=day,cohort=y.at[day,'cohort'],warning=r.p_warning,actual=r.actual,
                                base=prob,model_brier=(r.p_warning-r.actual)**2,base_brier=(prob-r.actual)**2))
        # Remove the window containing each actual extreme return from evaluation as a sensitivity check.
        # The resulting cohorts are diagnostic subsets, separate from the historical fit.
        daily=matrix('daily-process-features.csv')
        sample=daily.loc[yq.index[0]:yq.endpoint.max()]
        dates={'largest_up_session':sample.daily_log_return.idxmax(),
               'largest_down_session':sample.daily_log_return.idxmin(),'largest_gap_session':sample.gap.abs().idxmax()}
        for name,shock in dates.items():
            affected=yq.index[(yq.index<shock)&yq.endpoint.ge(shock)]
            for model in ['jump_diffusion','jump_1m','jump_shift','jump_no_episode','widened_gauss','constant_iv','path_mixture']:
                w=a[a.model.eq(model)]
                subset=w[~w.origin.isin(affected)]
                removal.append(dict(horizon=h,removed=name,shock_session=shock,removed_origins=len(affected),
                                    model=model,n=len(subset),disjoint=disjoint(subset.origin,y),
                                    full_crps=w.crps.mean(),ex_episode_crps=subset.crps.mean(),
                                    full_coverage80=w.coverage80.mean(),ex_episode_coverage80=subset.coverage80.mean()))
        for kind in ['endpoint_return','range','high','low','volatility','drawdown','max_gap']:
            demo=scores[scores.horizon.eq(h)&scores.origin.eq(DEMO)&scores.target.eq(kind)&scores.model.isin(
                ['constant_iv','gjr_iv','jump_diffusion','path_mixture','joint_tail_width','joint_pit','iv_scaled_blocks'])]
            october.extend(demo[['horizon','origin','model','target','actual','predicted_mean','q50','q10','q90','q025','q975']].to_dict('records'))
    a=pd.DataFrame(misses)
    for h in HORIZONS:
        m=a.horizon.eq(h)
        x=input_[h]
        y=anatomy[h]
        for k in FORECAST_SIGNALS:
            if k in x:
                a.loc[m,'asof_'+k]=a.loc[m,'origin'].map(x[k])
        for k in OUTCOMES:
            a.loc[m,'realized_'+k]=a.loc[m,'origin'].map(y[k])
    write('failure-casebook.csv',a)
    write('synchronized-range-misses.csv',pd.DataFrame(temporal))
    write('failure-warning-matched.csv',pd.DataFrame(worries))
    write('jump-episode-deletion.csv',pd.DataFrame(removal))
    write('october-case-model-comparison.csv',pd.DataFrame(october))
    print('Archived',len(a),'largest-loss and tail failure case records',flush=True)


if __name__=='__main__':
    run()
