"""Render the V13 research reports from the scored and verified archives."""
from .common import *
from .paths import div_close, from_steps, scale_steps

REPORTS=['REPRODUCTION_AND_BENCHMARKS','ADVANCED_VOLATILITY_RESEARCH','OPTIONS_SURFACE_DYNAMICS',
         'RISK_PREMIUM_AND_EXPECTATIONS','FUTURE_RANGE_FORECASTING','FIRST_PASSAGE_AND_BARRIER_PROBABILITIES',
         'COHERENT_MARKET_PATH_MODELS','GLOBAL_VOLATILITY_TRANSMISSION','STRIKE_POSITIONING_RESEARCH',
         'EVENT_CONDITIONED_RISK','RISK_INFORMED_DIRECTIONAL_MODELS','MONTHLY_RISK_AND_RETURN_RESEARCH',
         'DATA_QUALITY_AND_NEW_SOURCES','VALIDATION_AND_FALSIFICATION','COMPLETE_MODEL_COMPARISON',
         'EXPERIMENTAL_FORECAST_REPORT','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS']
RISK=['horizon','cohort','model','n','disjoint','mae','rmse','qlike','bias','spearman']
DIST=['horizon','cohort','model','target','n','disjoint','mae','crps','pinball','coverage50','coverage80','width80']
END=['horizon','cohort','model','n','disjoint','brier','log_loss','accuracy','balanced_accuracy','crps','mae','pinball','coverage80','width80']
PAIRS=['horizon','cohort','model','baseline','target','metric','n','disjoint','candidate','control','gain','low10','high10','low21','high21']
BARS=['horizon','barrier','event','model','n','disjoint','predicted','observed','brier','log_loss','mc_se']

def csv(name):
    return pd.read_csv(OUT/(name+'.csv'),low_memory=False)

def fmt(value):
    if pd.isna(value):
        return '—'
    return f'{value:.6f}' if isinstance(value,(float,np.floating)) else str(value).replace('|','\\|')

def table(frame,cols=None):
    if frame.empty:
        return '_No eligible observations._'
    a=frame.reindex(columns=cols) if cols else frame
    return '| '+' | '.join(a.columns)+' |\n| '+' | '.join(['---']*len(a.columns))+' |\n'+'\n'.join(
        '| '+' | '.join(map(fmt,r))+' |' for r in a.itertuples(index=False,name=None))

def emit(n,body):
    tag=REPORTS[n-1]
    (OUT/f'V13_{tag}.md').write_text('# V13 '+tag.replace('_',' ').title()+'\n\n'+body.strip()+'\n',encoding='utf-8')


def demo():
    import hashlib
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d=csv('distribution-predictions')
    origin=min(d[d.horizon.eq(h)&d.model.eq('iv_scaled')].origin.max() for h in HORIZONS)
    b=pd.read_csv(OUT/'barrier-predictions.csv.gz')
    v=csv('scored-volatility')
    receipts=loads(OUT/'path-ledger.json')['fits']
    sections=[]
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for h,ax in zip(HORIZONS,axes):
        y=matrix(f'targets-{h}.csv',OUT); x=matrix(f'features-{h}.csv',OUT)
        j=y.index.get_loc(origin)
        target=y.loc[origin]
        with np.load(OUT/f'observed-paths-{h}.npz') as z:
            observed=z['paths']
        with np.load(OUT/f'joint-path-target-atoms-{h}.npz') as z:
            keys=z['keys']
            idx=np.flatnonzero((keys[:,0]==origin)&(keys[:,1]=='iv_scaled'))[0]
            samples=pd.DataFrame(z['values'][idx],columns=z['targets'])
        t=y.index[y.endpoint.lt(origin)][-210:]
        r=np.random.default_rng(SEED+h*10000+j).choice(len(t),N_PATHS)
        iv=x.iv_nearest if h==5 else x.iv_bracket
        k=np.clip(iv.at[origin]/iv.fillna(x.har21).loc[t].to_numpy().clip(.035),.44,2.3)
        paths=from_steps(scale_steps(div_close(observed)[y.index.get_indexer(t)[r]],k[r]))
        receipt=next(s for s in receipts if s['horizon']==h and s['origin']==origin and s['model']=='iv_scaled')
        assert hashlib.sha256(paths.tobytes()).hexdigest()==receipt['hash']
        cl=paths[:,:,3]*target.reference
        curve=pd.DataFrame({'session':range(1,h+1),'median_close':np.median(cl,axis=0),
              'q10_close':np.quantile(cl,.1,axis=0),'q90_close':np.quantile(cl,.9,axis=0),
              'mean_daily_high':paths[:,:,1].mean(axis=0)*target.reference,'mean_daily_low':paths[:,:,2].mean(axis=0)*target.reference})
        write(f'demo-{h}-path.csv',curve,index=False)
        write(f'demo-{h}-sample-outcomes.csv',samples,index=False)
        ax.fill_between(curve.session,curve.q10_close,curve.q90_close,color='#4188a7',alpha=.26,label='Central 80%')
        ax.plot(curve.session,curve.median_close,c='#17384e',lw=2,label='Median close')
        ax.set(title=f'{h} trading sessions',xlabel='Session after origin',ylabel='NIFTY 50 points')
        ax.legend(frameon=False);ax.grid(alpha=.18)
        s=d[d.horizon.eq(h)&d.origin.eq(origin)&d.model.eq('iv_scaled')&
            d.target.isin(['endpoint_return','high','low','range','drawdown','volatility'])]
        barriers=b[b.horizon.eq(h)&b.model.eq('iv_scaled')&b.origin.eq(origin)&b.barrier.isin(list('01234'))]
        barrier=barriers.pivot(index='threshold',columns='event',values='p').reset_index()
        barrier['upper_price']=target.reference*(1+barrier.threshold)
        barrier['lower_price']=target.reference*(1-barrier.threshold)
        rr=v[v.horizon.eq(h)&v.origin.eq(origin)&v.model.isin(['iv_nearest','iv_bracket','har21','har_iv','fixed_iv_rv_0.50'])]
        sections.append(f"""
## {h} trading sessions

**{origin}** close **{target.reference:,.2f}**. Historical decision cutoff **{y.index[j+1]} 09:10 IST**. Target endpoint **{target.endpoint}**. V13 iv_scaled drew **{N_PATHS}** paths from **{len(t)}** matured windows using seed **{receipt['seed']}**, with IV from **{x.at[origin,'option_day']}**. Endpoint up probability **{(samples.endpoint_return>0).mean():.2%}**. Endpoint probability below −2% **{(samples.endpoint_return<=-.02).mean():.2%}** and above +2% **{(samples.endpoint_return>=.02).mean():.2%}**. The q25–q75 and q10–q90 columns give central 50% and 80% intervals.

{table(s,['target','predicted_mean','q10','q25','q50','q75','q90','actual'])}

Standalone volatility estimates

{table(rr,['model','prediction'])}

Reference-relative price and hit probabilities

{table(barrier,['threshold','upper_price','lower_price','upper_touch','lower_touch','upper_close','lower_close','upper_endpoint','lower_endpoint','both','neither','first_upper_definite','first_lower_definite','first_ambiguous'])}

[Day-by-day conditional path](demo-{h}-path.csv) · [Joint sample outcomes](demo-{h}-sample-outcomes.csv).
""")
    fig.savefig(OUT/'historical-path-fan.png',dpi=165)
    plt.close(fig)
    emit(16,"""
Research-only demonstration replayed on a historical origin with mature outcomes. The reported endpoint, highs, lows, range, barriers and drawdowns come from one joint ensemble. The standalone volatility estimates come from their separately named models. Observations appear in their own column.

![Median and central 80% historical conditional close trajectories](historical-path-fan.png)
"""+'\n'.join(sections)+"""
[Historical endpoint calibration](endpoint-calibration.csv) · [Historical barrier calibration](barrier-calibration.csv) · [Fit and simulation receipts](path-ledger.json).
""")


def run():
    v=loads(OUT/'verification.json')
    dq=loads(OUT/'data-quality.json')
    refresh=loads(OUT/'refresh-reconciliation.json')
    r=csv('volatility-leaderboard'); p=csv('distribution-and-path-leaderboard')
    b=csv('barrier-leaderboard'); m=csv('paired-search-adjusted')
    e=p[p.target.eq('endpoint_return')]
    rc=r[r.cohort.eq('combined')]; pc=p[p.cohort.eq('combined')]; mc=m[m.cohort.eq('combined')]
    fullr=rc[rc.n.eq(rc.horizon.map({5:265,21:217}))]
    fullp=pc[pc.n.eq(pc.horizon.map({5:265,21:217}))]
    fulle=fullp[fullp.target.eq('endpoint_return')]
    core=['empirical','empirical_exact','rv_scaled','iv_scaled','hybrid_scaled','state_iv','global_iv','event_iv','position_iv',
          'surface_iv','domestic_drift','diffusion_iv','asymmetry_iv','random_state_iv','shift_state_iv']
    def risk(names):
        return table(r[r.model.isin(names)].sort_values(['horizon','model','cohort']),RISK)
    def pair(names,targets=None,control=None,metrics=None):
        a=mc[mc.model.isin(names)]
        if targets:
            a=a[a.target.isin(targets)]
        if control:
            a=a[a.baseline.isin(control)]
        if metrics:
            a=a[a.metric.isin(metrics)]
        return table(a.sort_values(['horizon','target','metric','gain'],ascending=[True,True,True,False]),PAIRS)
    def top(a,metric,n):
        return a.sort_values(['horizon',metric]).groupby('horizon').head(n)
    vrefs=['prior_trailing','iv_nearest','iv_bracket','prior_fitted_rv','prior_fitted_iv','prior_fitted_lag5','prior_etf','prior_intraday']
    erefs=['V12_NATIVE_RV','J12_Q_GROUP','O_NATIVE_PHASE0','J11_EXCLUDE_B_ROT','B_CHANGE',
           'V8_W_STRUCT_EMBARGO_EQ','NEUTRAL','J11_BREADTH_ALL','J10_STRUCTURAL_BLEND','PH_NATIVE_PHASE_MIXTURE']
    emit(1,f"""
Rebuilt the exact frozen target windows with the inherited cash reference and return convention. Annualized volatility is the square root of 252 times mean squared daily close-to-close log return. Raw IV uses ACT/365, and converted variants match the planned horizon total variance to H trading sessions. Decision timestamps retain next-session 09:10 IST and the V12 archive delay.

Replayed **{v['v12_replay']['complete_laws']:,}** V12 atom-level endpoint distributions, **{loads(OUT/'protected-endpoint-replay.json')['atom_laws_replayed']:,}** additional protected laws and **{v['fitted_v12_replay']['forecasts']:,}** volatility point forecasts from the original saved coefficients. The maximum risk replay difference was **{v['fitted_v12_replay']['maximum_difference']:.2g}**. Verified **{v['protected']:,}** earlier-version files.

{table(rc[rc.model.isin(vrefs)],RISK)}

{table(e[e.model.isin(erefs)&(e.cohort.eq('combined')|(e.horizon.eq(5)&e.cohort.eq('later')&e.model.isin(['B_CHANGE','V8_W_STRUCT_EMBARGO_EQ'])))],END)}

[Saved fit IDs and replay receipt](v12-fitted-replay.json) · [Exact V12 per-origin scores](reproduced-endpoint.csv) · [Earlier model replay](protected-endpoint-replay.json) · [V12 research](../../../nifty_forecast_v12/2026-11-24/run-001/NIFTY_V12_RESEARCH.md).
""")
    emit(2,f"""
Rolling and EWMA measures track squared log returns. Parkinson, Garman–Klass and Rogers–Satchell estimate regular-session risk from OHLC. Gap variants add overnight squared returns, while Yang–Zhang blends overnight variance, open-to-close variance and Rogers–Satchell. Complete-grid intraday models use one-, five- or 25-minute increments. ARCH, GARCH, GJR and EGARCH refit at the first eligible origin each month and update daily. EGARCH uses a plug-in multi-step log-variance recursion. HAR, ridge and IV calibration use only matured targets. Fixed mixtures operate on variance. QLIKE compares annualized **variances**.

{table(top(fullr,'mae',15),RISK)}

{risk(vrefs+['har_rv','garch','egarch','gjr','intraday_5m','fixed_iv_rv_0.50','adaptive_variance_mix'])}

{pair(['har_iv','iv_calibrated','iv_session','iv_bracket_session','adaptive_variance_mix','fixed_iv_rv_0.25','fixed_iv_rv_0.50','fixed_iv_rv_0.75','intraday_5m'],['volatility'],['iv_nearest','iv_bracket'])}

[Volatility origin ledger](scored-volatility.csv) · [Risk calibration](volatility-calibration.csv) · [Expansion and contraction](volatility-expansion-contraction.csv) · [Fit receipts and failures](volatility-fit-ledger.json).
""")
    shapes=['shape_level','shape_change','shape_combined','shape_pca','shape_block_permute','shape_shift21','sstrip_var7_sd','sstrip_var30_sd']
    emit(3,f"""
Built constant-calendar-maturity histories at 7, 14, 30 and 45 days from **{dq['implied_expiries']:,}** liquid V12 expiry snapshots, preserving an earlier source day. Level summaries include ATM IV, upside and downside skew, curvature, implied quantiles, tail masses and term slope/curvature. One- and five-session changes, skew acceleration, slope sign transitions and same-listed-contract changes distinguish dynamics from rolls. A truncated OTM variance strip integrates only observed strikes. Four-factor PCA and regularized summaries are fit on matured rows. Missing wing or bracket support remains visible.

{risk(shapes)}

{pair(shapes,['volatility'],['iv_nearest','iv_bracket','shape_level'])}

[Fixed-tenor surface inputs](constant-maturity-surface.csv) · [V12 priced density archive](../../../nifty_forecast_v12/2026-11-24/run-001/option-density-atoms.npz) · [NSE variance methodology](https://nsearchives.nseindia.com/s3fs-public/inline-files/white_paper_IndiaVIX.pdf).
""")
    emit(4,f"""
The ex-ante proxy is nearest ATM IV squared less trailing HAR21 risk squared. The ex-post implied-minus-realized error remains an outcome. Pricing tiers use the matured training quartiles. The regressions test pricing changes, downside shape and interactions with breadth and financial rotation. For a physical candidate, option-derived endpoint dispersion is adjusted on matured forecasts and sign mass receives a strongly regularized logit calibration. The fixed mixture gives calibrated shape 25% weight.

{table(csv('variance-premium-regimes'))}

{pair(['premium_ridge','regime_iv'],['volatility'],['iv_nearest','iv_bracket','har_iv'])}

{table(e[e.cohort.eq('combined')&e.model.isin(['Q12_RAW','q_physical_adjusted','q_physical_mix25','P12_Q_PHYSICAL_MIX','V12_STAT','NEUTRAL'])],END)}

[Ex-ante and ex-post variance ledgers](variance-premium-origins.csv) · [Timing and fit parameters](path-ledger.json).
""")
    focus=pc[pc.target.isin(['range','high','low','drawdown','abs_return'])&
             pc.model.isin(['empirical_exact','rv_scaled','iv_scaled','diffusion_iv','state_iv','separate_range_ridge'])]
    emit(5,f"""
Maximum relative high and minimum relative low use the realized daily highs and lows after the reference close. Their difference is the reference-normalized range. Close-only excursions use future closes. Peak-to-trough drawdown and rebound are measured on ordered closes, keeping their definition independent of an unknown same-bar order. Separate labels cover overnight and regular-session variance, positive-day count, largest one-session log return magnitude, and terminal return magnitude. Empirical, volatility-scaled, state-conditioned and diffusion paths compete against standalone regularized residual range distributions.

{table(focus.sort_values(['horizon','target','mae']),DIST)}

{pair(['iv_scaled','state_iv','separate_range_ridge','diffusion_iv'],['range','high','low'],['empirical_exact','rv_scaled'],['mae','crps'])}

[Five-session labels](targets-5.csv) · [21-session labels](targets-21.csv) · [All origin forecasts](distribution-predictions.csv).
""")
    bb=b[b.cohort.eq('combined')&b.model.eq('iv_scaled')&b.barrier.isin(list('01234'))]
    ords=csv('observed-order-resolution')
    emit(6,f"""
Fixed barriers are ±0.5%, ±1%, ±2%, ±3% and ±5%. Volatility-relative barriers are 0.5, 1, 1.5 and 2 times the origin-time IV-scaled horizon move. A touch uses the high or low. Any-close and last-close events use their own observations. Both-sided and neither-sided hits are distinct. When both sides are first hit on the same day, a recorded opening gap may resolve the order. Otherwise, complete reconciled one- or five-minute candles resolve it when their order is observable. Same-bar ambiguity is recorded explicitly. The model's ordering scores use common daily-resolution events, with intraday refinement retained in the observed-label audit.

A fixed-model follow-up computes exact empirical hit frequencies over the mature path library. The continuous driftless log-price diffusion benchmark uses the reflection principle, which makes a one-sided touch probability twice the respective endpoint tail probability at the same barrier.

{table(bb[bb.event.isin(['upper_touch','lower_touch','upper_close','lower_close','upper_endpoint','lower_endpoint'])],BARS)}

{table(ords[ords.resolution.ne('daily')].groupby(['horizon','resolution']).n.sum().reset_index())}

{pair(['iv_scaled','state_iv','separate_barrier_logit','diffusion_iv','analytic_iv_diffusion','random_state_iv'],['touch_family'],['empirical_exact','rv_scaled','iv_scaled','analytic_iv_diffusion'])}

[All barrier and order scores](barrier-leaderboard.csv) · [Calibration](barrier-calibration.csv) · [Ordering receipt](observed-order-resolution.csv).
""")
    sim=csv('monte-carlo-checks')
    emit(7,f"""
Each ensemble has **{N_PATHS}** OHLC paths. Empirical candidates draw contiguous matured windows, maintaining dependence between overnight gaps, regular-session returns, highs, lows and closes. State weights use training-scaled features. Rival specifications use historical and implied-risk scaling, domestic drift, asymmetric scale, event and offshore conditioning, or Gaussian diffusion at 24 intraday steps. Every high, low, endpoint, touch and drawdown prediction in a joint forecast derives from that ensemble. Separate regressions are labeled independently. Conditional binomial Monte Carlo error is at most **{np.sqrt(.25/N_PATHS):.4f}** for a hit probability. Statistical uncertainty comes from the historical block resampling.

{table(pc[pc.target.isin(['endpoint_return','range','volatility'])&pc.model.isin(core)].sort_values(['horizon','target','crps']),DIST)}

{table(sim.assign(abs_difference=sim.split_delta.abs()).groupby(['horizon','model']).abs_difference.agg(['mean','max']).reset_index())}

[Joint target atoms for five sessions](joint-path-target-atoms-5.npz) · [Joint target atoms for 21 sessions](joint-path-target-atoms-21.npz) · [Simulation seeds and hashes](path-ledger.json).
""")
    global_models=['global_only','global_plus_iv','global_divergence','gold_nasdaq_risk','global_iv_plus_new_sources']
    emit(8,f"""
The offshore set uses dated U.S. VIX, S&P 500, Nasdaq and Asian equity risk, USD/INR and Brent realized risk, U.S. rate changes and global dispersion and synchronization. The frozen global source clocks use earlier foreign dates and explicit availability estimates. The supplemental run fits an Indian gold ETF proxy and attempts official-series Nasdaq implied volatility. Joint offshore weighting competes with the simple domestic IV-scaled path.

{risk(global_models+['iv_nearest','iv_bracket','prior_fitted_rv'])}

{pair(global_models+['global_iv'],None,['iv_nearest','iv_bracket','har_iv','iv_scaled'],['mae','qlike','crps','brier'])}

[Foreign clock](foreign-risk-clock.csv) · [Supplemental receipts](supplemental-sources.json) · [FRED VIX](https://fred.stlouisfed.org/series/VIXCLS) · [FRED Nasdaq volatility](https://fred.stlouisfed.org/series/VXNCLS).
""")
    emit(9,f"""
Matched **{dq['position_rows']:,}** date-expiry option chains. Unsigned features capture OI concentration, put share, near-forward interest, OI changes, volume relative to OI, distance to large call and put concentrations and cross-expiry differences. This dataset establishes aggregate unsigned positioning and activity. Net dealer inventory and gamma require participant-side information. Compare the added feature heads to price-surface risk and priced-volatility path models.

{pair(['position_ridge','position_iv'],None,['shape_level','iv_nearest','iv_bracket','iv_scaled'],['mae','qlike','crps','brier'])}

[Unsigned strike and expiry features](unsigned-strike-positioning.csv) · [Complete matched contrasts](paired-search-adjusted.csv).
""")
    a=csv('events-risk-and-path')
    event=a[a.active&a.target.eq('volatility')&a.model.isin(['iv_nearest','iv_bracket','har_iv'])]
    emit(10,f"""
Scheduled and observed flags distinguish expiry, a completed futures roll, verified policy schedules, partial index reviews, previous cash moves, sector stress, breadth deterioration and IV changes. Large changes use the preceding mature training 80th percentile. The event path model applies a 35% conditional weight after at least 12 prior comparables. Sparse event sets remain descriptive.

{table(event.sort_values(['horizon','event','model']))}

{pair(['event_iv'],['range','touch_family','high','low'],['iv_scaled','empirical_exact'],['brier','crps'])}

[Full volatility, range, movement and ±2% outcome profiles](events-risk-and-path.csv) · [Active origin flags](events.csv) · [Federal Reserve schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) · [RBI schedule](https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62422).
""")
    variants=e[e.cohort.eq('combined')&e.model.str.contains('rotation_iv|domestic_drift|asymmetry_iv|V12_NATIVE_RV|J12_Q_GROUP|NEUTRAL')]
    emit(11,f"""
Archived endpoint forecasts are replayed on their own origins. IV scaling uses an equal-probability grid, the archived location, and bounded width changes. The half-scaled variant contracts toward the original width. A separate domestic model fits returns divided by the origin-time risk estimate and maps them back to returns. Domestic and option interactions can change location, while the scale variants measure confidence separately.

{table(top(fulle,'brier',16),END)}

{table(variants,END)}

[All endpoint calibrations](endpoint-calibration.csv) · [Exact archived endpoints](reproduced-endpoint.csv) · [Paired comparisons and sensitivity](paired-search-adjusted.csv).
""")
    emit(12,f"""
The 217 monthly rolling outcomes comprise 11 non-overlapping windows. The symmetric statistical benchmark and phase-accounted forecasts remain separate from monthly range and volatility candidates. Market-priced direction and exact-expiry scores use the corresponding matched subsets. The tables give separate risk and endpoint rankings.

{table(top(fulle[fulle.horizon.eq(21)],'brier',14),END)}

{table(top(fullr[fullr.horizon.eq(21)],'mae',18),RISK)}

{table(focus[focus.horizon.eq(21)].sort_values(['target','crps']),DIST)}

[Monthly probabilities and paths](distribution-and-path-leaderboard.csv) · [Monthly results by event](events-risk-and-path.csv).
""")
    req=loads(OUT/'acquisition.json')
    sources=pd.DataFrame(loads(OUT/'supplemental-sources.json'))
    vix=loads(OUT/'sources/upstox/india-vix.json')['data']['candles']
    latest=pd.Series({str(pd.Timestamp(z[0]).date()):z[4] for z in vix},name='refreshed_india_vix')
    original=matrix('features-5.csv',OUT).vix_level
    vix_comparison=pd.concat([original,latest],axis=1).dropna()
    vix_comparison['difference']=vix_comparison.refreshed_india_vix-vix_comparison.vix_level
    write('india-vix-reconciliation.csv',vix_comparison,index=True)
    emit(13,f"""
V13 validated **{dq['daily_sessions']}** frozen OHLC sessions from **{dq['first']}** to **{dq['last']}** and found **{dq['official_difference_gt_005']}** spot-close discrepancies over 0.05 index point against the official file. Upstox returned **{sum('path' in q for q in req)} of {len(req)}** requested historical payloads. The IST regular-session grid spans 09:15 through 15:30. Separate daily and intraday audits cover special sessions, missing bars, and differences between daily official anchors and final intraday marks. Intraday ordering requires complete grids and daily high/low agreement within one index point. India VIX agreed within 0.05 on **{int(vix_comparison.difference.abs().le(.05).sum())} of {len(vix_comparison)}** overlapping observations.

{table(pd.DataFrame(dq['intraday']))}

{table(sources,['name','rows','complete_normal_grids','http','unavailable','source'])}

{table(pd.DataFrame(refresh['rows']),['day','upstox_close','nse_close','delta','failure'])}

[Market data archive receipts](acquisition.json) · [Intraday audit](intraday-audit.csv) · [VIX source comparison](india-vix-reconciliation.csv) · [Refresh reconciliation](refresh-reconciliation.json) · [Upstox historical specification](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [India VIX definition](https://www.nseindia.com/static/products-services/indices-indiavix-index).
""")
    null=csv('refit-null-winners')
    alternatives=['iv_lag2','iv_lag5','iv_same_close','iv_rate_high','iv_rate_zero','iv_longer','iv_liquid','iv_settlement',
                  'iv_truncated','iv_smooth','iv_future_forward','shape_shift21','shape_block_permute','shift_state_iv','random_state_iv']
    emit(14,f"""
Walk-forward fits enforce target maturity, train-only preprocessing and earlier option source dates. Archived duplicate inputs preserve the fitted design and future-perturbation sentinels preserve mature inputs and outcomes. The dependence-aware bootstrap uses **{N_BOOT:,}** paired circular block resamples at lengths 5, 10, 21 and 42. The maximum standardized deviation adjusts the bands within each scored family. Monthly thin cells and sparse events retain disjoint counts. Search adjustment applies to the declared V13 contrasts and leaves prior adaptive search exposure.

For each horizon, twelve refit-and-reselection draws shuffle feature blocks around the retained raw IV anchor on an every-tenth-origin panel across five model specifications. Below are the winning null and unpermuted gains. This limited panel provides a falsification diagnostic.

{table(null)}

{pair(alternatives,None,['iv_nearest','iv_bracket','iv_scaled'],['mae','crps','brier'])}

[Initial specification](initial-registry.json) · [Null forecast artifacts](refit-null-origins.csv) · [Complete intervals](paired-search-adjusted.csv) · [Verification](verification.json).
""")
    touch=csv('touch-family-loss')
    touch=touch.groupby(['horizon','model']).agg(n=('origin','size'),brier=('brier','mean'),log_loss=('log_loss','mean')).reset_index()
    emit(15,f"""
Rankings keep the objectives separate. Full-denominator tables use 265 weekly and 217 monthly scored origins. The linked tables retain eligibility changes, earlier and later cohorts, effective sample diagnostics, search-adjusted intervals, and matched immediate parents.

## Directional probabilities

{table(top(fulle,'brier',10),END)}

## Endpoint distributions

{table(top(fulle,'crps',10),END)}

## Realized volatility

{table(top(fullr,'mae',12),RISK)}

## Absolute movement, range and drawdown

{table(fullp[fullp.target.isin(['range','abs_return','drawdown'])].sort_values(['horizon','target','mae']).groupby(['horizon','target']).head(5),DIST)}

## Fixed price-level touch probability

{table(touch.sort_values(['horizon','brier']))}

[Volatility metrics](volatility-leaderboard.csv) · [Endpoint and path metrics](distribution-and-path-leaderboard.csv) · [All barrier metrics](barrier-leaderboard.csv) · [Cross-cohort matched comparisons](paired-search-adjusted.csv).
""")
    demo()
    outcome=[]
    for h in HORIZONS:
        vol=fullr[fullr.horizon.eq(h)&~fullr.model.eq('iv_same_close')].sort_values('mae').iloc[0]
        raw=rc[rc.horizon.eq(h)&rc.model.eq('iv_nearest' if h==5 else 'iv_bracket')].iloc[0]
        future=fullp[fullp.horizon.eq(h)&fullp.target.eq('range')].sort_values('crps').iloc[0]
        barrier=touch[touch.horizon.eq(h)].sort_values('brier').iloc[0]
        bi=fulle[fulle.horizon.eq(h)].sort_values('brier').iloc[0]
        cr=fulle[fulle.horizon.eq(h)].sort_values('crps').iloc[0]
        outcome.append(dict(horizon=h,raw_iv_mae=raw.mae,vol_model=vol.model,vol_mae=vol.mae,range_model=future.model,
                            range_crps=future.crps,touch_model=barrier.model,touch_brier=barrier.brier,
                            direction_model=bi.model,endpoint_brier=bi.brier,distribution_model=cr.model,endpoint_crps=cr.crps))
    outcomes=pd.DataFrame(outcome)
    write('headline-results.csv',outcomes,index=False)
    strong=mc[(mc.horizon.eq(5)&mc.low10.gt(0))|(mc.horizon.eq(21)&mc.low21.gt(0))]
    highlighted=mc[((mc.target.eq('volatility'))&mc.metric.eq('mae')&
                  (((mc.horizon.eq(5))&mc.model.eq('iv_calibrated')&mc.baseline.eq('iv_nearest'))|
                   ((mc.horizon.eq(21))&mc.model.eq('gjr')&mc.baseline.eq('iv_bracket'))))|
                  (mc.model.eq('diffusion_iv')&mc.baseline.isin(['empirical_exact','iv_scaled'])&
                   ((mc.target.eq('range')&mc.metric.eq('crps'))|(mc.target.eq('touch_family')&mc.metric.eq('brier'))))]
    emit(17,f"""
These are point leaders from the same frozen historical study. Raw implied volatility, the empirical and RV-scaled paths, and the original V12 endpoint leaders remain explicit competing benchmarks. Different outcome types and effective sample sizes explain why the leaders may differ. The comparisons are historical and research-exposed.

{table(outcomes)}

## Principal benchmark comparisons

{table(highlighted,PAIRS)}

## Adjusted historical gains

{table(strong.sort_values(['horizon','family','gain'],ascending=[True,True,False]).groupby(['horizon','family']).head(10),PAIRS) if not strong.empty else 'No matched gains in these families cleared the simultaneous bands.'}

[All comparisons](paired-search-adjusted.csv) · [Research forecast replay](V13_EXPERIMENTAL_FORECAST_REPORT.md) · [Verification](verification.json).
""")
    emit(18,"""
1. Freeze the strongest simple risk and OHLC-path controls with actual input timestamps. Track risk MAE, range CRPS and monotone touch Brier per newly matured window.
2. Validate tail behavior on verified strikes with dated bid/ask and funding. Carry the latest reconstruction and source delay controls forward.
3. Preserve origin-time class definitions before re-evaluating event, volatility-state or unsigned OI effects. Compare to raw risk and a simple scaled path.
4. Compare five-minute and one-minute ordering with a stable index close anchor. Record remaining same-bar uncertainty in paired passage tests.
5. Collect more independent monthly outcomes for fixed variance, downside and range hypotheses. Preserve the symmetric model for monthly endpoint probability.

[Complete comparison](V13_COMPLETE_MODEL_COMPARISON.md).
""")
    listing='\n'.join(f'{i}. [{n.replace("_"," ").title()}](V13_{n}.md)' for i,n in enumerate(REPORTS,1))
    (OUT/'NIFTY_V13_RESEARCH.md').write_text(f'# NIFTY V13 Research\n\nFrozen through {FREEZE}. Research on 5- and 21-session endpoint returns, volatility, OHLC paths and barriers.\n\n{listing}\n\n[Run instructions](README.md) · [Mission](MISSION.md) · [Manifest](manifest.json) · [Verification](verification.json)\n',encoding='utf-8')
    steps=['acquire','data','volatility protect','volatility replay','volatility risk','paths','legacy','supplement','controls',
           'evaluate','verify fits','verify refresh','verify check','report','verify delivery']
    command='\n'.join('.\\.venv\\Scripts\\python.exe -m research.nifty_forecast_v13.'+s for s in steps)
    (OUT/'README.md').write_text('# Reproduce V13\n\nUse the repository Python environment. Set NIFTY_V13_OUT to a new directory under the V13 artifact tree and copy the mission first. Each command below runs from the repository root. Read-only refreshes are separate from the frozen model inputs. Supplemental source acquisition follows the pre-registered core models.\n\n~~~powershell\n'+command+'\n~~~\n\n[Registration](initial-registry.json) · [Research reports](NIFTY_V13_RESEARCH.md).\n',encoding='utf-8')


if __name__=='__main__':
    run()
