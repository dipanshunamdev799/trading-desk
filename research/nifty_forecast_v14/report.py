"""Generate the requested V14 reports from verified research outputs."""
from .common import *
from .generation import TICK
from .path_score import Q_NAMES

TITLES=[
 'REPRODUCTION_AND_BENCHMARKS','EXTREME_MOVEMENT_ANATOMY','VOLATILITY_TRANSITION_MODELS',
 'STOCHASTIC_AND_ASYMMETRIC_VOLATILITY','JUMPS_AND_DISCONTINUOUS_MOVEMENTS','TREND_PERSISTENCE_AND_PATH_DIRECTION',
 'OPTIONS_TAIL_INTELLIGENCE','INTRADAY_VOLATILITY_STRUCTURE','ADVANCED_JOINT_PATH_MODELS',
 'PREDICTIVE_CALIBRATION_AND_INTERVALS','BARRIER_AND_FIRST_PASSAGE_DYNAMICS','GLOBAL_SHOCK_TRANSMISSION',
 'RISK_INFORMED_ENDPOINT_FORECASTING','FORECAST_FAILURE_FORENSICS','VALIDATION_AND_FALSIFICATION',
 'COMPLETE_MODEL_COMPARISON','EXPERIMENTAL_MARKET_INTELLIGENCE','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS']
PAIR=['horizon','scope','target','model','baseline','metric','n','disjoint','candidate','control','gain','low10','high10','low21','high21']
RISK=['horizon','cohort','model','n','disjoint','mae','rmse','qlike','bias','rank_correlation']
DIST=['horizon','target','cohort','model','n','disjoint','crps','mae','pinball','coverage80','width80','interval_score80','coverage95']
END=['horizon','cohort','model','n','disjoint','brier','log_loss','accuracy','balanced_accuracy','crps','mae','coverage80','width80']
EVENTS=['horizon','cohort','event','model','n','disjoint','brier','log_loss','p','actual']
INTERVAL=['horizon','cohort','model','method','target','central','n','disjoint','coverage','width','interval_score','lower_miss','upper_miss','fitted']
PATH_EVENT_SELECTION=['upper_fixed','lower_fixed','range_relative','upper_relative','lower_relative','variance_extreme',
                      'gap_relative','persist_up','persist_down','expand','enter_high','contract','persist_high']
EXPECTED={5:265,21:217}


def csv(name):
    return pd.read_csv(OUT/(name+'.csv'),low_memory=False)


def fmt(v):
    if pd.isna(v):
        return '—'
    return f'{v:.6f}' if isinstance(v,(float,np.floating)) else str(v).replace('|','\\|')


def table(f,cols=None):
    if f.empty:
        return '_No eligible rows._'
    f=f.reindex(columns=cols) if cols else f
    return ('| '+' | '.join(map(str,f.columns))+' |\n| '+' | '.join(['---']*len(f.columns))+' |\n'
            +'\n'.join('| '+' | '.join(fmt(x) for x in r)+' |' for r in f.itertuples(index=False,name=None)))


def report(i,body):
    tag=TITLES[i-1]
    dest=OUT/f'V14_{tag}.md'
    dest.write_text('# V14 '+tag.replace('_',' ').title()+'\n\n'+body.strip()+'\n',encoding='utf-8')


def combined(a):
    return a[a.cohort.eq('combined')]


def full(a):
    return combined(a)[lambda g:g.n.eq(g.horizon.map(EXPECTED))]


def top(a,order,n,keys=('horizon',)):
    return a.sort_values([*keys,order]).groupby(list(keys)).head(n)


def figure_calibration(cal):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    f=cal[cal.cohort.eq('combined')&cal.target.eq('range')&cal.central.eq(80)]
    f=f[(f.model.isin(['V13_diffusion_iv','V13_iv_scaled','joint_pit','joint_tail_width','path_mixture','gjr_iv','gjr_student']) & f.method.eq('whole_law')) |
        (f.model.eq('path_mixture')&f.method.isin(['asymmetric_residual','rolling_cqr','calendar_block_cqr']))].copy()
    names={'V13_diffusion_iv':'V13 diffusion','V13_iv_scaled':'V13 IV-scaled blocks','joint_pit':'Reweighted paths',
           'joint_tail_width':'Mixed-width paths','path_mixture':'V14 path mixture','asymmetric_residual':'Asymmetric intervals',
           'rolling_cqr':'Rolling residual intervals','calendar_block_cqr':'Block residual intervals',
           'gjr_iv':'IV-GJR paths','gjr_student':'Student-t GJR paths'}
    colors=dict(zip(names,['#9b5236','#814795','#dc7b39','#3a7952','#1c7192','#7b7b15','#294d86','#646b74','#174f59','#b42836']))
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    known={}
    for (h,ax) in zip(HORIZONS,axes):
        for r in f[f.horizon.eq(h)].itertuples():
            k=r.model if r.method=='whole_law' else r.method
            title=names[k]
            hh=ax.scatter(r.width*100,r.coverage*100,c=colors[k],s=59,edgecolor='white',linewidth=.55,zorder=3,
                          marker='D' if k.startswith('gjr_') else 'o')
            known[title]=hh
        ax.axhline(80,c='#727981',lw=1,ls='--')
        ax.set(title=f'{h} trading sessions',xlabel='Mean interval width (% of reference)',ylabel='Realized coverage (%)')
        ax.grid(alpha=.18)
    fig.legend(known.values(),known.keys(),loc='outside lower center',ncol=5,frameon=False,fontsize=8)
    fig.savefig(OUT/'range-calibration.png',dpi=165)
    plt.close(fig)


def historical_demo():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    b=pd.read_csv(OUT/'path-passage.csv.gz',low_memory=False,dtype={'barrier':str})
    order=pd.read_csv(OUT/'path-ordering.csv.gz',low_memory=False,dtype={'barrier':str})
    e=pd.read_csv(OUT/'path-tail-and-transition-probabilities.csv.gz',low_memory=False)
    m=pd.read_csv(OUT/'path-marginals.csv.gz',low_memory=False)
    q=csv('process-risk-predictions')
    p=csv('point-risk-models')
    f=csv('october-case-realized-path')
    parent='joint_tail_width'
    with np.load(OUT/f'joint-paths/{DEMO}.npz',allow_pickle=False) as z:
        runner=np.exp(z[parent].astype(float)*TICK)
    fig,axes=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
    sections=[]
    for h,ax in zip(HORIZONS,axes):
        y=matrix(f'targets-{h}.csv')
        x=matrix(f'features-{h}.csv')
        y0=y.loc[DEMO];x0=x.loc[DEMO]
        close=runner[:,:h,3]*y0.reference
        dates=np.arange(1,h+1)
        levels=np.quantile(close,[.025,.10,.50,.90,.975],axis=0)
        observed=(f[f.horizon.eq(h)].close_rel+1)*y0.reference
        fan=pd.DataFrame(dict(session=dates,median=levels[2],q10=levels[1],q90=levels[3],
                              q025=levels[0],q975=levels[4],actual=observed.to_numpy()))
        write(f'demo-{h}-conditional-path.csv',fan)
        ax.fill_between(dates,levels[0],levels[4],color='#92bdcf',label='Central 95%',alpha=.34)
        ax.fill_between(dates,levels[1],levels[3],color='#37758e',label='Central 80%',alpha=.31)
        ax.plot(dates,levels[2],color='#19465b',lw=2,label='Forecast median')
        ax.plot(dates,observed,color='#a6402b',lw=1.8,label='Realized close')
        ax.set(title=f'{h} trading sessions',xlabel='Trading session after origin',ylabel='NIFTY 50 index points')
        ax.grid(alpha=.18)
        x1=m[m.horizon.eq(h)&m.origin.eq(DEMO)&m.model.eq(parent)]
        ep=x1[x1.target.eq('endpoint_return')].iloc[0]
        prob=e[e.horizon.eq(h)&e.origin.eq(DEMO)&e.model.eq(parent)&e.event.isin(PATH_EVENT_SELECTION)]
        barriers=b[b.horizon.eq(h)&b.origin.eq(DEMO)&b.model.eq(parent)&b.barrier.isin(list('01234'))].copy()
        barriers['index_level']=y0.reference*np.where(barriers.side.eq('upper'),1+barriers.threshold,1-barriers.threshold)
        joint=order[order.horizon.eq(h)&order.origin.eq(DEMO)&order.model.eq(parent)&order.barrier.isin(list('01234'))]
        rough=pd.concat([q,p],ignore_index=True)
        rough=rough[rough.horizon.eq(h)&rough.origin.eq(DEMO)&rough.model.isin(['gjr_student','blend_gjr_iv','raw_iv','latent_iv','har','intraday_har'])].copy()
        rough['realized']=y0.volatility
        full_table=['target','predicted_mean','predicted_median','q025','q10','q25','q75','q90','q975','actual']
        mid=x1[x1.target.isin(['endpoint_return','abs_return','volatility','range','high','low','drawdown','rebound'])]
        alternatives=m[m.horizon.eq(h)&m.origin.eq(DEMO)&m.target.isin(['endpoint_return','range','volatility'])&
                       m.model.isin(['constant_iv','gjr_iv','gjr_student','path_mixture','joint_tail_width'])]
        after=x.index[x.index.get_loc(DEMO)+1]
        sections.append(f"""
## {h} trading sessions

**{DEMO}** reference close **{y0.reference:,.2f}**. Inherited decision clock **{after} 09:10 IST**, with options marks dated **{x0.option_day}**. Endpoint **{y0.endpoint}**. The V14 joint_tail_width law contains **{N:,}** paths. It assigned **{ep.p_up:.2%}** to a positive endpoint. Forecast quantiles below are relative to the reference, except annualized volatility. The interval columns are paired at q25–q75, q10–q90 and q025–q975.

{table(mid,full_table)}

### Volatility and extreme events

The joint path already supplies a realized-volatility law. The following point estimates use separate daily risk models.

{table(rough,['model','prediction','realized'])}

{table(prob,['event','p','actual'])}

### Passage probability and time

Expected time is measured in trading sessions conditional on a hit by the horizon. Survival is cumulative no-touch probability at the horizon.

{table(barriers,['side','threshold','index_level','p_touch','p_close','p_endpoint','expected_time_given_touch','survival','actual_time'])}

{table(joint,['threshold','p_both','p_neither','p_upper_first','p_lower_first','p_same_candle','intraday_resolved_order'])}

### Sensitivity to the chosen path model

These are separate model projections at the same forecast cutoff. The spread across models measures forecast disagreement.

{table(alternatives,['model','target','p_up','predicted_mean','q10','q90'])}

[Day-by-day conditional path](demo-{h}-conditional-path.csv).
""")
    ax.legend(loc='lower left',frameon=False,fontsize=8)
    fig.savefig(OUT/'historical-joint-paths.png',dpi=165)
    plt.close(fig)
    return """This research-only case uses a frozen historical origin. The realized series is shown separately. Probabilities for endpoint, extrema, range, drawdown, passage and volatility expansion are projections of one archived OHLC law. Stronger point risk models and standalone interval adjustments are reported elsewhere. The model missed important outcomes in the October episode, and the observed series is included to make those misses visible. In the barrier table an observed time of H+1 means the threshold was untouched at H.

![Historical conditional NIFTY paths and realized closes](historical-joint-paths.png)

"""+'\n'.join(sections)+"""[Historical calibration](V14_PREDICTIVE_CALIBRATION_AND_INTERVALS.md) · [Model uncertainty](matched-search-adjusted.csv) · [Case forensics](V14_FORECAST_FAILURE_FORENSICS.md).
"""


def run():
    rep=read('reproduction.json'); check=read('verification.json'); counts=read('evaluation-counts.json')
    risk=csv('volatility-leaderboard'); margins=csv('path-marginal-leaderboard'); endpoint=csv('endpoint-leaderboard')
    paths=csv('joint-leaderboard'); events=csv('transition-and-tail-leaderboard')
    touch=csv('touch-and-passage-family'); passage=csv('barrier-leaderboard')
    ordering=csv('ordering-leaderboard'); cal=csv('interval-calibration-leaderboard')
    cmp=csv('matched-search-adjusted'); pairs=cmp[cmp.scope.eq('combined')]
    ranges=margins[margins.target.eq('range')]
    frequencies=csv('extreme-event-frequency'); anatomy=csv('extreme-anatomy-contrasts')
    risk_lists=lambda models: table(risk[risk.model.isin(models)].sort_values(['horizon','model','cohort']),RISK)
    def selected(family,models,targets=None,refs=None,metrics=None):
        t=pairs[pairs.family.eq(family)&pairs.model.isin(models)]
        if targets:
            t=t[t.target.isin(targets)]
        if refs:
            t=t[t.baseline.isin(refs)]
        if metrics:
            t=t[t.metric.isin(metrics)]
        return table(t.sort_values(['horizon','target','metric','gain'],ascending=[True,True,True,False]),PAIR)

    report(1,f"""
Continuing the exact frozen 2025–2026 study, with H actual trading sessions following the cash reference. Close-to-close risk is the square root of 252 times future mean squared daily log returns. The V13 options series uses calendar maturity and recorded lagged alignment. Variance QLIKE uses the realized-to-forecast annualized **variance** ratio.

Recomputed **{rep['risk_rows']:,}** V13 volatility forecasts, **{rep['range_rows']:,}** range distributions, **{rep['barrier_rows']:,}** fixed touch comparisons and **{rep['endpoint_rows']:,}** endpoint score rows. Volatility point replay error was at most **{rep['risk_max_abs_error']:.2g}**. Float32 V13 range atoms account for the maximum **{rep['maximum_range_replay_delta']:.2g}** score discrepancy. Verified **{check['previous_hashes']:,}** protected predecessor hashes.

{table(csv('benchmark-volatility'))}

{table(csv('benchmark-range'))}

{table(csv('benchmark-touch'))}

{table(csv('benchmark-endpoint')[lambda a:a.cohort.eq('combined')|a.cohort.eq('later')],END)}

The QLIKE decomposition conditions on actual annualized volatility relative to raw ATM IV. Strong underprediction produces large variance ratios and disproportionately high loss. The extreme-ratio bucket below explains where the weekly MAE/QLIKE trade-off came from.

{table(csv('calibration-qlike-anatomy'))}

[Exact replay](reproduction.json) · [V13 study](../../../nifty_forecast_v13/2026-11-25/run-001/NIFTY_V13_RESEARCH.md).
""")
    a=anatomy[(anatomy.cohort.eq('combined'))&anatomy.event.isin(['upper_fixed','lower_fixed','range_relative','persist_up','persist_down'])
           &anatomy.measurement.isin(['aligned_fraction','peak_shock_share','net_overnight','net_intraday','atm1','breadth5','finance','sector_sync'])]
    report(2,f"""
Fixed targets span large positive and negative endpoints, high–low ranges, ±5% excursions and 1.2% opening gaps. Five-session endpoint limits are ±3%, and 21-session limits are ±5%. Fixed range levels are 5.5% and 10%. Relative tails use the 10th/90th training quantiles, and IV-relative endpoint tails use ±1.5 origin-time horizon standard deviations. A persistent extreme also requires at least 65% of daily moves to align with the final direction and a largest-shock share of absolute movement at or below one-half. Acceleration compares signed mean log changes in the first and last portions of the realized window. An episode merges overlapping positive-label windows. Greedy disjoint outcome counts are also retained.

{table(combined(frequencies),['horizon','event','eligible','count','frequency','distinct_episodes','positive_disjoint','eligible_disjoint'])}

{table(a,['horizon','event','clock','measurement','positive_avg','negative_avg','positive_n','negative_n'])}

Conditional associations use matched cohort histories. Future path components explain realized moves after the fact. The predictors in the as-of rows were available when forecasts were issued.

[All episodes and dates](distinct-extreme-episodes.csv) · [All cohort and antecedent contrasts](extreme-anatomy-contrasts.csv) · [Event definitions and chronology](thresholds-5.csv).
""")
    transitions=['expand','contract','enter_high','exit_high','persist_high','variance_extreme','rapid_risk']
    report(3,f"""
Expansion and contraction require future volatility above 1.25 or below 0.80 times the trailing H-session realized level. Entry and exit score only the eligible initial state, using a rolling 75th percentile of matured outcomes for the high-state boundary. Elevated volatility persistence requires both parts of the future window to exceed the high threshold. Speed and acceleration are scored separately. State probabilities use observed data or filtering available at the origin. Retrospectively smoothed values appear only in hidden-state parameter fitting on already observed training returns.

{table(top(combined(events)[lambda a:a.event.isin(transitions)],'brier',4,('horizon','event')),EVENTS)}

{selected('volatility_transition',['domestic','surface','intraday','markov_state','regime_state','gjr_control','gjr_iv','joint_pit'],
    ['expand','enter_high','exit_high'],['historical','iv_raw','gjr_control'],['brier'])}

{table(combined(csv('continuous-transition-leaderboard')).sort_values(['horizon','target','mae']))}

[As-of classification probabilities](transition-and-tail-probabilities.csv.gz) · [Training boundaries and coefficients](signal-fit-ledger.json).
""")
    fits=pd.DataFrame([dict(origin=r['origin'],method=r['method'],**{k:r['parameters'].get(k,np.nan)
          for k in ['alpha','beta','gamma','xi','nu','skew','leverage']}) for r in read('process-fits.json')])
    fitted_stats=fits.groupby('method')[['alpha','beta','gamma','xi','nu','skew','leverage']].median().reset_index()
    fitted_stats2=fits[fits.method.isin(['gjr_student','gjr_skew','gjr_ivx','egarch_student'])].assign(
        period=lambda f:np.where(f.origin<'2026-07-01','2025 to June 2026','July 2026 onward')).groupby(['method','period'])[
        ['alpha','beta','gamma','xi','nu','skew','leverage']].median().reset_index()
    report(4,f"""
The process study fits Gaussian GARCH and GJR, variance-standardized Student-t and bounded skew-t GJR, and Student-t EGARCH. GJR limits the combined persistence coefficients and changes volatility after negative shocks. EGARCH uses a bounded causal log-variance filter and plug-in multistep expectation. Exogenous GJR uses IV or India VIX with lagged predictors in the likelihood. The IV anchor moves from near to longer maturity through the forecast. A fixed hybrid gives near-term IV greater weight and gradually shifts to GJR. Other competitors include a realized-measure log-volatility Kalman filter, an IV-anchored latent variant, a filtered two-state variance model, HAR and fast/slow component risk. Each process refit shares its initial state across the five- and 21-session forecasts.

{table(top(full(risk),'mae',16),RISK)}

{table(fitted_stats)}

{table(fitted_stats2)}

{selected('volatility',['gjr_ivx','blend_gjr_iv','gjr_student','egarch_student','latent_iv','gjr_t_short','gjr_t_perturbed'],
    ['volatility'],['V13_raw_ATM','V13_bracketed_IV','V13_GJR'],['mae','qlike'])}

[Process coefficients and optimizer status](process-fits.json) · [Per-origin variance curves](process-states.json) · [Original GJR model](https://doi.org/10.1111/j.1540-6261.1993.tb05128.x) · [Hansen skewed Student-t density](https://users.ssc.wisc.edu/~behansen/papers/ier_94.pdf).
""")
    jnames=['constant_iv','separate_gap','jump_diffusion','jump_1m','jump_shift','jump_no_episode','widened_gauss','gjr_student','historical_innov']
    deletion=csv('jump-episode-deletion')
    report(5,f"""
Regular-session realized variance and finite-sample-corrected bipower variation use complete grids. Their positive difference is a jump-sensitive proxy. Sampling, jumps, volatility bursts and market microstructure can all affect it. The overnight move is measured separately from the regular-session log change. The jump probability uses a lagged training 90th-percentile proxy flag, a shrunken estimate of frequency and magnitude, and current known proxy history. Scheduled jumps are excluded from continuous within-step bridge correction. Jump simulations deduct expected jump variance from their continuous variance budget. Width-only, five-minute, one-minute, shifted-input, and deleted-largest-training-episode comparisons are scored on common dates. Extremes are sparse at the independent episode level, so the experiment uses shrunken empirical sizes and Student innovations.

{table(csv('intraday-summary'))}

{table(combined(ranges)[lambda a:a.model.isin(jnames)],DIST)}

{table(deletion[deletion.model.isin(['jump_diffusion','jump_no_episode','widened_gauss'])])}

[Full intraday jump diagnostics](intraday-profile.csv) · [Drop-episode checks](jump-episode-deletion.csv) · [Joint path calibration and parameters](joint-path-ledger.json) · [Bipower variation method](https://doi.org/10.1093/jjfinec/nbh001).
""")
    trend=['constant_iv','simple_drift','trend_persistent','trend_shrink','trend_blocks','iv_scaled_blocks','regime_state']
    report(6,f"""
The path comparison varies estimated AR continuation, an explicitly shrunken historical drift, a domestic-location correction, a filtered variance/sign-state path, and conditional historical resampling. Drift inputs use mature volatility-normalized five-session forecasts and earlier breadth, rotation, synchronization and sign-streak measurements. Foreseen drift decays through the forecast. Realized directional persistence is scored separately from a one-session shock and from the terminal sign.

{table(endpoint[endpoint.model.isin(trend)],END)}

{table(combined(events)[lambda a:a.model.isin(trend)&a.event.isin(['persist_up','persist_down'])],EVENTS)}

[Realized October daily/overnight decomposition](october-case-realized-path.csv) · [Forecast-only feature contrasts](extreme-anatomy-contrasts.csv).
""")
    surface=['iv_raw','raw_iv_logistic','historical','gjr_control','surface','surface_lag5','surface_shift21',
             'surface_permuted','surface_liquid','surface_truncated','iv_scaled_blocks']
    report(7,f"""
Option additions cover constant-tenor up and down IV, skew acceleration, curvature, tail probabilities, quantile spreads, term transitions, unsigned concentration and traded volume. Trained physical-event regressions use those measures as predictors. The reconstructed risk-neutral probabilities remain in their own columns. Liquidity, truncation, delayed actual chains and shifted or block-permuted inputs compete with the raw ATM and the simple historical controls.

{table(combined(events)[lambda a:a.model.isin(surface)&a.event.isin(['upper_relative','lower_relative','range_relative'])],EVENTS)}

{selected('extremes',surface,['upper_relative','lower_relative','range_relative','lower_excursion_fixed'],
    ['iv_raw','historical','iv_scaled_blocks'],['brier'])}

[Fixed-time features](features-5.csv) · [Original expiry and price data](../../../nifty_forecast_v12/2026-11-24/run-001/V12_OPTION_IMPLIED_DISTRIBUTIONS.md) · [All tail and transition losses](transition-and-tail-leaderboard.csv).
""")
    intr=csv('intraday-profile').groupby('interval')[['firsthour_share','midday_share','closing_share','upshare','downshare',
        'sign_consistency','var_concentration','max_abs_intraday']].mean().reset_index()
    report(8,f"""
Only audited complete bars contribute to session-level measurements. Features include opening gaps, first hour, midday and last-hour variance shares, bipower excess, up/down semivariance, reversal and directional persistence, relative excursions, and inherited synchronized sector factors. Overnight, regular-session and close-to-close variance remain separate. The frozen cash close anchors every outcome.

{table(intr)}

{risk_lists(['raw_iv','har','har_iv','intraday_har','overnight_decomposition','offshore_gap','latent_kalman'])}

{selected('range_path',['intraday_blocks'],['range','max_gap','overnight_sd','regular_sd'],['constant_iv','V13_iv_scaled'],['crps','mae'])}

[Complete session profiles](intraday-profile.csv) · [Rejected sessions](intraday-rejections.csv) · [Separate opening-gap forecasts](opening-gap-forecasts.csv) · [Separate horizon risk components](gap-channel-forecasts.csv).
""")
    report(9,f"""
The archive contains **{check['verified_joint_models']:,}** model/date laws over **265** origins. Each law has **{N:,}** complete 21-session OHLC paths. On common origins the five-session forecast is the exact prefix with identical weights. Candidate mechanisms include raw and calibrated constant IV, Gaussian and heavy-tailed asymmetric GARCH, IV-GARCH, latent and regime variance, historical innovations, overnight gaps, jumps, empirical blocks and fixed complete-path mixtures. All target probabilities, drawdowns, ranges and realized returns come from the same paths. A shared mixture gives 30% each to constant IV and IV-GJR and 20% each to jump and IV-scaled blocks. Reweighting and width calibration retain coherent complete paths.

Energy and variogram loss act on endpoint return, range, high, low, realized volatility and drawdown. Coordinates use only scales fitted on matured training data. A fixed common 1,024-pair sample estimates the energy pair term. Per-origin seeds and encoded OHLC scenarios are available for exact verification.

{table(top(full(paths),'energy_score',15),['horizon','model','n','disjoint','energy_score','variogram_score'])}

{table(top(full(ranges),'crps',15),DIST)}

[Joint law catalog and SHA-256 digests](joint-path-ledger.json) · [Joint score ledger](multivariate-path-scores.csv) · [Independent forecast-law verification](verification.json).
""")
    cal_models=['V13_diffusion_iv','V13_iv_scaled','constant_iv','iv_scaled_blocks','gjr_student','gjr_iv',
                'path_mixture','joint_pit','joint_tail_width','jump_diffusion']
    chosen=combined(cal)[lambda a:a.target.eq('range')&a.model.isin(cal_models)&
        ((a.method.eq('whole_law')&a.central.isin([50,80,90,95]))|
        (a.model.eq('path_mixture')&a.central.isin([80,95])))]
    conditional=csv('conditional-interval-calibration')
    figure_calibration(cal)
    report(10,f"""
Central 50%, 80%, 90% and 95% ranges are scored jointly with interval width, interval score and the two miss directions. PIT reweighting uses the frequency with which matured observations fell in each forecast rank bin, with strong shrinkage toward equal weights across the same set of OHLC paths. A separate width mixture changes complete paths using prior residual tail ratios. Both variants retain joint and cross-horizon relationships. Standalone normalized residual, asymmetric, risk-matched and calendar-block corrections fit on matured prior forecast errors. Those intervals have separate scores and may differ from marginal intervals of a joint predictive distribution. The dependence and regime variation in rolling outcomes limit the applicability of standard exchangeability-based coverage guarantees.

![Trade-off between central range coverage and interval width](range-calibration.png)

{table(chosen.sort_values(['horizon','central','method','interval_score']),INTERVAL)}

{table(conditional[conditional.model.isin(['V13_diffusion_iv','joint_tail_width','gjr_student'])&
    conditional.method.eq('whole_law')].sort_values(['horizon','model','origin_state']))}

[All cohort and calibration scores](interval-calibration-leaderboard.csv) · [Coverage by origin risk and subsequent expansion](conditional-interval-calibration.csv) · [Standalone intervals and cutoffs](standalone-calibrated-intervals.csv.gz) · [Conformalized quantile regression method](https://proceedings.neurips.cc/paper_files/paper/2019/hash/5103c3584b063c431bd1268e9b5e76fb-Abstract.html).
""")
    bb=combined(passage)[lambda a:a.barrier.isin(['2','4','iv1.0'])&a.model.isin(['constant_iv','gjr_iv','gjr_student','path_mixture','joint_pit','joint_tail_width','logistic_barrier'])]
    report(11,f"""
Every fixed and IV-scaled barrier has distinct probabilities for touching, closing at some point beyond the level, and terminal exceedance. Larger thresholds receive weakly smaller probabilities, and the cumulative hit distribution cannot fall with time. Survivors form the H+1 category. Reported expected time is conditional on a touch within H. The daily order categories are upper first, lower first, both first appearing in the same candle with ambiguous order, and neither. A recorded opening gap can identify order within a daily candle. Reconciled intraday ordering is retained separately. The standalone monotone logistic model supplies fixed-horizon hit probabilities. The simulated laws also supply daily survival, time and order scores.

{table(top(full(touch),'brier',14),['horizon','model','n','disjoint','brier','log_loss','integrated_brier','passage_log_loss'])}

{table(bb,['horizon','model','barrier','side','n','disjoint','p_touch','actual','p_endpoint','actual_endpoint',
           'integrated_brier','expected_time_given_touch','diagnostic_time_error'])}

{table(combined(ordering)[lambda a:a.barrier.eq('2')&a.model.isin(['constant_iv','gjr_student','gjr_iv','joint_pit','joint_tail_width'])],
       ['horizon','model','n','p_both','actual_both','p_neither','actual_neither','p_upper_first','p_lower_first','p_same_candle','order_brier'])}

[All barrier scores](barrier-leaderboard.csv) · [Passage day CDF and expected time](path-passage.csv.gz) · [First-order and ambiguity observations](path-ordering.csv.gz) · [Independent consistency checks](verification.json).
""")
    report(12,f"""
The global mechanism uses foreign risk as a predictor for the next NIFTY opening gap, horizon overnight risk and the interaction between foreign shocks and weak local participation. Verified earlier dates feed VIX, Nasdaq volatility, U.S. and Asian equity moves, currency and oil risk, the dated gold ETF proxy, interest-rate changes and global dispersion. Each known observation precedes the historical decision cutoff under conservative availability rules.

{table(csv('global-gap-leaderboard'))}

{selected('offshore_gap',['opening_gap_offshore'],['next_gap'],['opening_gap_domestic'])}

{selected('volatility_transition',['offshore_opening','domestic_global_interaction'],
    ['expand','enter_high','variance_extreme'],['historical','iv_raw','gjr_control'],['brier'])}

[Opening gap forecasts](opening-gap-forecasts.csv) · [Separate overnight risk](gap-channel-forecasts.csv) · [Foreign risk source alignment](../../../nifty_forecast_v13/2026-11-25/run-001/foreign-risk-clock.csv) · [Gold and Nasdaq supplemental timing](supplemental-clock.csv).
""")
    new_end=['gjr_dispersion_only','hybrid_gjr_group','domestic_location_only','domestic_location_gjr_scale',
             'skew_only','sign_shrinkage','student_tail_only','sign_magnitude_hybrid']
    components=csv('endpoint-components')
    components['location_delta']=components['mean']-components.reference_mean
    components['width_delta']=components.width-components.reference_width
    components['p_delta']=components.p-components.reference_p
    change=components.groupby(['horizon','model'])[['location_delta','width_delta','p_delta','lower_tail_mass','upper_tail_mass']].mean().reset_index()
    report(13,f"""
Endpoints retain the original V13 weekly direction and distribution leaders and the mandatory monthly symmetric forecast. The standalones separately change location, dispersion, skew, sign mass and tail shape. Pure shape changes preserve the archived mean and variance. The normalized-target regression uses training-only breadth, rotation and IV interactions. A sign-and-magnitude law predicts sign separately and attaches upstream matured magnitudes. GJR changes the confidence scale of structural laws and also generates its own joint endpoints.

{table(top(full(endpoint),'brier',14),END)}

{table(top(full(endpoint),'crps',14),END)}

{table(change)}

{selected('direction',new_end,None,['V13_week_Brier','symmetric'],['brier'])}

[Matched changes to archived location, spread and positive mass](endpoint-components.csv) · [Model fits](endpoint-fits.json) · [Standalone endpoint probability laws](standalone-endpoint-laws.npz) · [Frozen benchmark rows](benchmark-endpoint-origins.csv).
""")
    failure=csv('failure-casebook')
    together=csv('synchronized-range-misses')
    warning=csv('failure-warning-matched')
    witness=csv('october-case-model-comparison')
    session=csv('october-case-realized-path')
    g=session.groupby('horizon').agg(up_days=('change_log',lambda a:int((a>0).sum())),
        largest_daily_log_move=('change_log',lambda a:abs(a).max()),overnight_log=('overnight_log','sum'),
        regular_log=('regular_log','sum'),net_log=('change_log','sum')).reset_index()
    miss_stats=warning.groupby('horizon').agg(n=('origin','size'),warning_brier=('model_brier','mean'),
                    historical_brier=('base_brier','mean'),rate=('actual','mean')).reset_index()
    report(14,f"""
The casebook separates information visible at the origin from realized path decomposition. It lists the largest probability and distribution losses, unexpected upside and downside, range and volatility underestimates, and missed price levels. Cases repeated across origins may describe the same shock. The October 15 origin was fixed as a diagnostic example before the V14 comparisons. The realized upside case below is decomposed across days, overnight and regular trading without assuming a single causal explanation.

{table(g)}

{table(witness[witness.target.isin(['endpoint_return','range'])],['horizon','model','target','predicted_mean','q10','q90','q975','actual'])}

{table(together.sort_values(['horizon','under','actual'],ascending=[True,False,False]).groupby('horizon').head(10))}

### As-of warning for an upper range miss

The simple warning model uses only prior resolved V13 forecast errors and dated features. Matched controls use earlier observed miss frequencies.

{table(miss_stats)}

[Full failure casebook with observed and as-of values](failure-casebook.csv) · [Cross-model misses](synchronized-range-misses.csv) · [Historical episode removal](jump-episode-deletion.csv).
""")
    null=csv('refit-null-reselection')
    ordinary=null[null.draw.eq(-1)].set_index(['horizon','event']).brier_gain
    random=null[null.draw.ge(0)].copy()
    random['unpermuted']=random.set_index(['horizon','event']).index.map(ordinary)
    random['null_ge_unpermuted']=random.brier_gain.ge(random.unpermuted)
    null_summary=random.groupby(['horizon','event']).agg(null_draws=('draw','size'),
        observed_gain=('unpermuted','first'),mean_null_gain=('brier_gain','mean'),max_null_gain=('brier_gain','max'),
        worst_case_fraction=('null_ge_unpermuted','mean')).reset_index()
    mc=csv('monte-carlo-convergence')
    mc0=mc[mc.n.eq(8192)][['horizon','origin','model','p_upper2','range80hi']].rename(
        columns={'p_upper2':'p_8192','range80hi':'range_hi_8192'})
    diff=mc.merge(mc0,on=['horizon','origin','model']).assign(touch_diff=lambda a:abs(a.p_upper2-a.p_8192),
        range_hi_diff=lambda a:abs(a.range80hi-a.range_hi_8192))
    d=diff.groupby(['horizon','model','n'])[['touch_diff','range_hi_diff','conditional_mc_se']].mean().reset_index()
    bridge=csv('continuous-bridge-check')
    bridge['raw_error']=abs(bridge.raw_hit-bridge.analytic)
    bridge['bridge_error']=abs(bridge.bridge_hit-bridge.analytic)
    sd=bridge.groupby(['horizon','steps'])[['raw_error','bridge_error']].mean().reset_index()
    report(15,f"""
Bootstrap uncertainty uses **{BOOT:,}** paired circular blocks at lengths **5, 10, 21 and 42** across the frozen cohort calendar. Reported bands use the maximum standardized deviation within each declared family. Limited disjoint coverage remains visible, and adjustment covers the V14 comparisons only. Screening uses original source dates, guard clocks, chronological fits with matured outcomes, and duplicate and unreleased-label sentinels. The null experiment refits four competing feature specifications on permuted training blocks around the retained risk anchor. It then selects the best gain at each draw, within a bounded thinned origin panel. A handful of draws provide diagnostic evidence.

{table(null_summary)}

{table(d)}

{table(sd)}

Bridge probabilities in the last table are for one-sided hits in a continuous log-price diffusion. They use conditional no-cross probabilities within each simulated step. The bridge test uses a common fine grid and omits overnight jumps. Full joint models keep discrete kicks and overnight moves separate. Parameter perturbations, shortened training history, altered jump sampling and removed extremes are compared on matched dates.

[Registration](registration.json) · [All matched bands](matched-search-adjusted.csv) · [Refit null per-origin data](refit-null-origins.csv.gz) · [Bridge experiment](continuous-bridge-check.csv) · [Fit and timing verification](timing-verification.json).
""")
    stable=csv('pareto-frontiers')
    report(16,f"""
Independent objective rankings below use full expected coverage of 265 and 217 origins. Other cohorts, conditional events and matched subsets appear in the full tables. The Pareto view uses an objective-specific loss, absolute early–late gap, a stated coarse model-complexity tier, and nominal coverage error for interval-related views. The date counts and effective sample diagnostics are retained. Separate likelihood and error metrics lead to distinct statistical choices.

## Endpoint direction

{table(top(full(endpoint),'brier',10),END)}

## Full endpoint distribution

{table(top(full(endpoint),'crps',10),END)}

## Realized risk

{table(top(full(risk),'mae',10),RISK)}

## Range, passage and calibration

{table(top(full(ranges),'crps',9),DIST)}

{table(top(full(touch),'brier',10),['horizon','model','n','disjoint','brier','log_loss','integrated_brier','passage_log_loss'])}

{table(top(full(paths),'energy_score',8))}

{table(stable[stable.pareto].sort_values(['horizon','objective','loss']),['horizon','objective','model','loss','absolute_cohort_gap','coverage80_error','complexity_tier'])}

[Extreme and transition ranks](transition-and-tail-leaderboard.csv) · [Full path projections](path-marginal-leaderboard.csv) · [First-hit timing and order](barrier-leaderboard.csv) · [All interval calibration](interval-calibration-leaderboard.csv) · [All matched uncertainty](matched-search-adjusted.csv).
""")
    report(17,historical_demo())

    headline=[]
    for h in HORIZONS:
        for objective,metric,a in [('volatility','mae',risk),('range','crps',ranges),('direction','brier',endpoint),
                                    ('endpoint_distribution','crps',endpoint),('touch','brier',touch),
                                    ('joint','energy_score',paths)]:
            s=full(a)[lambda z:z.horizon.eq(h)].sort_values(metric).iloc[0]
            headline.append(dict(horizon=h,objective=objective,metric=metric,model=s.model,loss=s[metric],n=s.n,disjoint=s.disjoint))
    out=pd.DataFrame(headline)
    write('headline-results.csv',out)
    principal=pairs[(
        (pairs.family.eq('volatility')&pairs.model.isin(['gjr_ivx','blend_gjr_iv'])&pairs.baseline.isin(['V13_raw_ATM','V13_bracketed_IV','V13_GJR'])&pairs.metric.eq('mae'))|
        (pairs.family.eq('range_path')&pairs.target.eq('range')&pairs.model.isin(['gjr_iv','gjr_student','joint_tail_width'])&
            pairs.baseline.eq('V13_diffusion_iv')&pairs.metric.eq('crps'))|
        (pairs.family.eq('endpoint_return')&pairs.model.isin(['sign_shrinkage','regime_state'])&
            pairs.baseline.isin(['V13_week_CRPS','V13_IV_scaled_symmetric']))|
        (pairs.family.eq('touch')&pairs.model.isin(['gjr_iv','gjr_student','regime_state','path_mixture','joint_tail_width'])&
            pairs.baseline.isin(['V13_diffusion_iv','V13_analytic_iv_diffusion'])))]
    report(18,f"""
V14 evaluated **{counts['risk_rows']:,}** volatility rows, **{counts['distribution_rows']:,}** marginal distribution rows,
**{counts['event_rows']:,}** transition and extreme-event rows, **{counts['passage_rows']:,}** passage probabilities, and
**{counts['matched']:,}** matched uncertainty comparisons. Full-horizon point leaders appear below. Strong predecessors remain in the rankings, and adjusted comparison bands condition on the frozen historical study.

{table(out)}

## Direct comparisons with strong predecessors

{table(principal,PAIR)}

Many extreme labels share the same realized episode. Independent evidence still requires new disjoint outcomes. The October replay documents how dispersion and path calibration can improve average metrics while substantial upside moves remain difficult.

[All 19 reports](NIFTY_V14_RESEARCH.md) · [Calibration](V14_PREDICTIVE_CALIBRATION_AND_INTERVALS.md) · [Failure cases](V14_FORECAST_FAILURE_FORENSICS.md).
""")
    report(19,"""
1. Register a short candidate list for future disjoint outcomes, keeping raw weekly IV, the original monthly GJR fit and V14 Student-GJR paths as explicit competitors.
2. Track central range coverage and interval score alongside endpoint loss. Freeze complete-path calibration weights and update them only when outcomes mature.
3. Preserve source timestamps for option marks, funding and foreign observations. Prioritize directly observed wings and independent episodes over adding more surface features.
4. Check gap and jump components against alternative bar grids and the same-variance Gaussian benchmark. Evaluate touches at fixed and IV-relative distances on the same origin dates.
5. Audit severe forecast misses by episode, with known-at-origin warnings separated from realized decomposition. Freeze any conditional warning rule before the next review.

[Benchmark and verification index](NIFTY_V14_RESEARCH.md).
""")
    index='\n'.join(f'{i}. [{tag.replace("_"," ").title()}](V14_{tag}.md)' for i,tag in enumerate(TITLES,1))
    (OUT/'NIFTY_V14_RESEARCH.md').write_text(f'''# NIFTY V14 Research

Frozen through **{FREEZE}**. Historical research on extreme movements, volatility transitions, calibrated paths and first passage over five and 21 trading sessions.

{index}

[Reproduction instructions](README.md) · [Original mission](MISSION.md) · [Verification](verification.json) · [Artifact manifest](manifest.json).
''',encoding='utf-8')
    steps=['data','replay protect','replay replay','volatility point','volatility process','generation','signals',
           'path_score','endpoint endpoint','endpoint intervals','diagnostics anatomy','diagnostics simulation',
           'diagnostics null','evaluate','forensics','verify check','report','verify deliver']
    commands='\n'.join('.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v14.'+k for k in steps)
    (OUT/'README.md').write_text("""# Reproduce NIFTY V14

Use the repository virtual environment from the repository root. Set NIFTY_V14_OUT to a fresh subdirectory of the V14 artifact tree and copy the original MISSION.md into that directory. V14 reads the frozen Upstox, NSE and related archives from earlier runs. All generated V14 files stay beneath the new run directory. The daily OHLC scenario archive records prices as fixed-point log returns relative to the origin close, in open, high, low, close order. For the joint_pit model, pair path_mixture paths with joint_pit_weights. For all other model arrays, each row has equal mass. Multiply the integer array by the archive tick to obtain log prices.

~~~powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
"""+commands+"""
~~~

[Study index](NIFTY_V14_RESEARCH.md) · [Registered design](registration.json) · [Archived joint laws](joint-path-ledger.json) · [Verification](verification.json).
""",encoding='utf-8')


if __name__=='__main__':
    run()
