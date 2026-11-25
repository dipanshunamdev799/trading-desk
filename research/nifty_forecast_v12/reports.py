"""Generate the complete V12 research report set from archived results."""
from .common import *
from .knowledge import build as knowledge

TITLES=[
 'REPRODUCTION_AND_BASELINES','OPTIONS_DATA_AND_AVAILABILITY','OPTION_IMPLIED_DISTRIBUTIONS',
 'HORIZON_AND_EXPIRY_ALIGNMENT','EXPECTATION_VS_REALITY','CROSS_INSTRUMENT_DISAGREEMENT',
 'EVENT_CONDITIONED_FORECASTING','PHASE_INVARIANT_LEARNING','FORECAST_INFORMATION_DECOMPOSITION',
 'COMPLEMENTARY_MARKET_INFORMATION','MARKET_INFORMED_DISTRIBUTIONS','MONTHLY_MARKET_EXPECTATIONS',
 'CUMULATIVE_KNOWLEDGE_BASE','VALIDATION_AND_FALSIFICATION','COMPLETE_COMPARISON','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS',
]
PAIR=['horizon','cohort','model','baseline','metric','n','disjoint','candidate','control','gain','low10','high10']
SCORE=['model','n','disjoint','brier','crps','log_loss','accuracy','balanced_accuracy','mae','rmse','median_mae','pinball','coverage50','coverage80','width80','ECE']
RISK=['model','n','disjoint','path_volatility_mae','absolute_return_error','fixed_down2_forecast_mass','fixed_down2_observed','fixed_down2_tail_brier']


def csv(name):return pd.read_csv(OUT/f'{name}.csv',low_memory=False)


def fmt(x):
    if pd.isna(x):return '—'
    return f'{x:.6f}' if isinstance(x,(float,np.floating)) else str(x).replace('|','\\|')


def table(a,cols=None):
    if a.empty:return '_No eligible observations._'
    if cols is not None:a=a.reindex(columns=cols)
    head='| '+' | '.join(map(str,a.columns))+' |\n| '+' | '.join(['---']*len(a.columns))+' |\n'
    return head+'\n'.join('| '+' | '.join(fmt(i) for i in r)+' |' for r in a.itertuples(index=False,name=None))


def emit(i,body):
    name=TITLES[i-1]
    (OUT/f'V12_{name}.md').write_text('# V12 '+name.replace('_',' ').title()+'\n\n'+body.strip()+'\n',encoding='utf-8')


def sections():
    sidebar=read('verification.json')
    refresh=read('refresh-summary.json')
    src=read('options-source-audit.json')
    surface=csv('surface-quality');quality=csv('daily-options-audit');alignment=csv('alignment-coverage')
    mate=csv('matched-comparisons');scores=csv('leaderboard');inc=mate[mate.is_parent]
    registry=read('registry.json');replay=read('exact-replay.json');legacy=read('legacy-breadth-replay.json')
    earlier=read('reproduction.json',OUT/'replay/older')
    docs=read('publication-source-receipts.json');un=read('paired-uncertainty.json')

    def score(h=5,c='combined',names=None):
        a=scores[scores.horizon.eq(h)&scores.cohort.eq(c)]
        return a if names is None else a[a.model.isin(names)]

    def value(n,k,h=5,c='combined'):
        a=score(h,c,[n])
        return fmt(a[k].iloc[0]) if len(a) and k in a else '—'

    def panel(names,h=5):
        a=scores[scores.model.isin(names)&scores.horizon.eq(h)].pivot(index='model',columns='cohort',values=['brier','crps'])
        a.columns=[f'{c} {m}' for m,c in a.columns]
        cols=['model','early brier','later brier','combined brier','early crps','later crps','combined crps']
        return table(a.reset_index().reindex(columns=cols).sort_values('combined brier'))

    def paired(names,horizons=(5,21),scopes=('early','later','combined'),metrics=('brier','crps'),refs=None):
        a=mate if refs is not None else inc
        a=a[a.model.isin(names)&a.horizon.isin(horizons)&a.cohort.isin(scopes)&a.metric.isin(metrics)]
        if refs is not None:a=a[a.baseline.isin(refs)]
        return table(a.sort_values(['horizon','model','cohort','metric']),PAIR)

    benchmarks=['P_HIST','P_CLUSTER','J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK','O_NATIVE_PHASE0','J11_BREADTH_ALL',
                'J11_BREADTH_ALL_HIST','J11_EXCLUDE_B_ROT','B_CHANGE','V8_W_STRUCT_EMBARGO_EQ','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO']
    emit(1,f"""
V12 retains the previously inspected 2025–2026 chronology and freezes data at **17 November 2026**. It reproduced **{replay['forecasts']:,}** reference forecasts using the original V11 walk-forward fits and V10/V11 mixture recipes, with maximum discrepancy **{replay['max_abs_delta']:.3g}**. These include original phase zero and its alternative or staggered phase designs, oldest/recent/spread memory, strong later breadth, native/sparse and shape components, and the original structural mixtures. A separate exact V11 replay reproduced **{legacy['predictions']:,}** official-breadth forecasts based on authentic V8 and V9 parent designs and fit dates. The earlier protected replay recovered **{earlier['V9_forecasts']} V9** and **{earlier['V8_leading_forecasts']} V8** forecasts, and the symmetric monthly source was also rebuilt over 217 origins.

## Reference weekly Brier and CRPS

{panel(benchmarks)}

The symmetric 21-session reference has **{value('NEUTRAL','brier',21)} Brier** and **{value('NEUTRAL','crps',21)} CRPS**. On later weekly origins, 0.156795 Brier and 0.009262 CRPS are V11 records from different designs. The V8 protected values are 0.159504 and 0.009453. Re-searching historical parameters provides additional evidence about model robustness on the same exposed data. The market-price comparisons use matched dates and independently scored outcomes.

[Exact replay ledger](exact-replay.json) · [Each replayed score](exact-replay.csv) · [Breadth replay](legacy-breadth-replay.json) · [Frozen artifact hashes](protected-verification.json).
""")
    columns=['all_rows','nifty_rows','option_rows','futures_rows','traded_option_rows','zero_volume_close_positive','no_trade_or_no_valid_close',
        'complete_traded_ohlc','traded_ohlc_consistent','price_equals_previous_on_trade','traded_close_neq_last',
        'traded_close_neq_settlement','same_expiry_strike_traded_pairs','unpaired_traded_strikes','duplicate_contract_session_rows',
        'nonzero_underlying_mismatch_gt_05','actual_expiry_differs_from_listed','actual_expiry_after_2026_rows']
    raw_total=pd.DataFrame([{'measure':k,'count':quality[k].sum()} for k in columns])
    emit(2,f"""
The inventory covers **{src['sessions']}** authenticated daily UDiFF archives from **{src['first_day']}** to **{src['end_day']}**. The extraction retained **{src['nifty_raw_rows']:,}** NIFTY records with trading/business date, actual and listed expiry, strike, call/put, traded OHLC, last, previous close, close, settlement, transaction count, volume, open interest, lot, identifier and session record code. Native ZIP hashes reconcile to the frozen source receipts, and core close, settlement and volume fields were checked against the earlier slim archives. The official daily NIFTY close supplies a separate underlying denominator.

{table(raw_total)}

A positive close on a zero-trade row is an unverified mark. Main price reconstruction requires observed volume on both sides where parity is used. Stale-close flags, unpaired strikes, relative value bounds, option-price distortions, parity scatter and strike gaps are retained. Historical bid/ask spreads, quote timestamps, instrument Greeks, and matched-tenor MIBOR are unavailable in this archive. NSE’s India VIX uses order-book bids and asks and a relevant maturity funding input. V12 estimates implied risk from end-of-day traded-contract marks. The settlement-price check uses settlement values for the same eligible traded contracts, treating those values as reference marks. [NSE daily archives](https://www.nseindia.com/all-reports) · [India VIX definition](https://www.nseindia.com/static/products-services/indices-indiavix-index) · [Native contract specifications](https://betanseapi.nseindia.com/static/products-services/equity-derivatives-contract-specifications).

All main option and futures data are at least one observed NSE archive session old at the cash-origin close. The inherited decision clock is 09:10 IST on the next session. Foreign availability estimates are checked against that clock as well as an earlier source date. Two- and five-session options buffers and a same-close diagnostic test sensitivity to receipt assumptions. Both observed expiries and scheduled event publications have explicit evidence. A separate refresh reacquired **{refresh['validated_records']:,}** valid records, last complete NIFTY date **{refresh['closed_sessions'][-1]}**, with **{len(refresh['additional_vs_V11'])}** additional completed dates beyond V11. [Raw NIFTY extraction](sources/nifty-udiff.csv.gz) · [Daily quality audit](daily-options-audit.csv) · [Published source receipts](publication-source-receipts.json) · [Market refresh](refresh-summary.json).
""")
    bars=[]
    for n,g in surface.groupby('method'):
        valid=g[g.iv_status.eq('accepted')];d=g[g.density_status.eq('accepted')]
        bars.append({'method':n,'date-expiries':len(g),'accepted IV':len(valid),'valid strike IV':int(g.valid_iv.sum()),'attempted strike IV':int(g.iv_trials.sum()),
             'accepted density':len(d),'median ATM IV':valid.atm_iv.median(),'median outside mass':d.external_mass.median(),
             'median price RMSE (bp of forward)':1e4*d.density_call_rmse_fraction_forward.median(),
             'q10 outside support count':int(d.lower_extrapolated_quantile.eq(True).sum()),
             'q90 outside support count':int(d.upper_extrapolated_quantile.eq(True).sum())})
    bars=pd.DataFrame(bars)
    core=surface[surface.method.eq('TRADE')]
    parity=core[core.iv_status.eq('accepted')&core.future_parity_gap.notna()]
    emit(3,f"""
V12 estimates an expiry forward using the median of up to 13 liquid near-money put-call-parity pairs. Call minus put over the discount factor plus strike gives the individual forwards. The same-expiry native futures contract is an audit and an alternative anchor where it exists. The central synthetic discount is 6% annual continuous with 0% and 9% sensitivities. A matched bank funding series and dividend schedule were unavailable. An option forward or cash–futures basis also contains carry and market frictions. There are **{len(parity):,}** accepted main date-expiries with a traded corresponding future. The median absolute future–parity gap is **{1e4*abs(parity.future_parity_gap).median():.2f} basis points** of the parity forward.

The Black-76 inversion works in forward units, uses the traded out-of-money side, rejects prices outside model bounds, checks two-sided coverage, and records the ATM, put/call, skew and curvature measures. An ATM-only lognormal is an explicit diagnostic fallback rather than a reconstructed smile. A Breeden–Litzenberger-style finite-difference procedure estimates vertical-spread probabilities, smooths and projects them to a non-increasing [0, 1] curve, differences to nonnegative interior mass, and treats the boundary mass as extrapolated. Two exterior atoms use bounded endpoint-premium extrapolation. A small exponential reweighting enforces the forward moment. The price-fit, support and mass-movement tests reject unreliable surfaces. The accepted law fits priced **risk-neutral** information. Atoms outside the observed strike region carry an explicit flag and their exact tails are unidentified. [Breeden and Litzenberger](https://doi.org/10.1086/296025).

{table(bars)}

The strike IV counts use the priced out-of-money strikes that passed the initial liquidity, parity and moneyness screens. The accepted-IV and accepted-density counts use all tested date-expiries as their denominator. The tighter volume screen, settlement marks, two alternate rates, actual-futures anchor, denser smoothing and narrower strike truncation rerun identical date-expiry candidates with separate coverage. The archived exercise prices, signed slopes, strike IVs, density masses and boundary flags are reproducible. [Expiry/shape quality and rejections](surface-quality.csv) · [Per-strike Black IV](strike-implied-volatility.csv.gz) · [Accepted priced laws](option-density-atoms.npz).

![Observed option marks, fitted curve and extrapolated priced tails]({(OUT/'option-curve-check.png').as_posix()})
""")
    ac=alignment[alignment.cohort.eq('combined')]
    natural_weekly=score(5,names=['Q12_NATURALLY_ALIGNED']).iloc[0]
    natural_monthly=score(21,names=['Q12_NATURALLY_ALIGNED']).iloc[0]
    emit(4,f"""
Planned endpoints use the published weekday, holiday and special-session schedule as known at each cash origin. Actual endpoint dates are independently retained from the frozen label calendar. The main option selection takes the nearest listed future expiry to the *planned* 5- or 21-session endpoint from a previous completed source date. The naturally aligned diagnostic is scored only when the selected expiry also equals the actual endpoint, and uses the quoted absolute-strike law divided by the later origin’s cash close. A longer-expiry variant requires an expiry at least four calendar days farther out than planned. [2025 NSE calendar](https://nsearchives.nseindia.com/content/circulars/CMTR65587.pdf) · [2026 NSE calendar](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf) · [Observed 2026 budget-session notice](https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf).

For bracketing expiries the interpolation operates on total variance and requires a non-decreasing pair. A missing or inverted bracket receives a flag, and the strict bracket comparison uses paired eligible dates. Approximate priced laws recenter the observed forward and scale log-strike shape by the square-root calendar tenor ratio. This explicitly reuses a different maturity shape and gives no model-free identification at the desired endpoint. Bracketing supplies a volatility measure only.

{table(ac,['horizon','version','queries','valid_iv','valid_density','exact_listed_actual','planned_equals_actual','bracketed_monotone',
           'median_abs_gap_days','p90_abs_gap','nonmonotone_brackets'])}

The table’s `valid_density` column measures usable curves at the forecast-time expiry choice. Scoring the `NATURAL` diagnostic additionally requires that the actual trading-session endpoint matches that expiry, leaving **{natural_weekly.n} weekly** and **{natural_monthly.n} monthly** origins, with **{natural_weekly.disjoint}** and **{natural_monthly.disjoint}** non-overlapping windows respectively. The December 26, 2025 forecast used the January 27, 2026 expiry, which matched the planned 21-session endpoint. The subsequently announced January 15 market holiday moved the actual endpoint to January 28, making that expiry ineligible for exact-match scoring. [Matched scores](V12_EXPECTATION_VS_REALITY.md) · [January 15 market holiday notice](https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf).

[Origin-by-origin dates including planned, actual, shorter and longer expiry](horizon-alignment.csv) · [Earlier and later coverage](alignment-coverage.csv) · [Calendar notices](calendar-audit.json).
""")
    obs=csv('observable-priced-risk');qtail=csv('priced-raw-event-calibration')
    qp=['Q12_RAW','Q12_NATURALLY_ALIGNED','Q12_BLACK_ATM','P12_Q_LOCATION','P12_Q_SCALE','P12_Q_TILT','P12_Q_PHYSICAL_MIX','P12_Q_HIST_FALLBACK']
    emit(5,f"""
The baseline is V11’s stronger complete-law ensemble excluding the base rotation expert. Compare Q forecasts with that law and matured empirical history on identical dates. The Q quantities are what can be inferred from the archived marked option curve. The P candidates statistically calibrate realized returns using only prior matured observations. Transformations tested include retaining priced shape while taking the statistical center, a capped historical realized-to-priced width adjustment, strongly regularized logit calibration of option-derived positive mass, a fixed 25% calibrated priced-law mixture, and an additional 25% historical fallback. The raw Q mixture is diagnostic and remains tagged with its pricing provenance. The learned disagreement model requires 24 earlier mature matched option and statistical forecasts before adding a limited location correction.

## Observables against realized outcomes

{table(obs[obs.cohort.eq('combined')],['horizon','market_feature','target','n','mean_feature','mean_target','mae','spearman'])}

## Priced-law versus statistical or calibrated parents

{paired(qp,(5,21),('combined',))}

## Raw priced mass versus realized sign and fixed downside frequency

{table(qtail[qtail.cohort.eq('combined')])}

In the full weekly study the priced law assigned 56.08% average positive mass against 44.15% realized positive returns, and its sign Brier was 0.268655 against 0.244333 for V11. Weekly downside below −5% occurred once in 265 observations. On the 199 monthly shape-eligible origins, the −5% downside occurred 13.57% of the time, against 8.37% priced mass and 9.20% statistical mass. The raw pricing diagnostic nevertheless had a lower downside Brier than the V11 statistical law on those dates, 0.132122 versus 0.152517. The monthly observations are overlapping and the priced mass is not a real-world calibration.

The comparison records numerical disagreement in positive mass, location, dispersion, absolute move, skew-sensitive tails and quantiles. Those measures can correlate with realized volatility or magnitude even when directional scores fail to improve. [Matched observed outcomes](expectations-vs-statistics.csv) · [Cross-law gap diagnostics](statistical-and-priced-gap-diagnostics.csv) · [Fixed-threshold and empirical-bucket checks](training-bucket-calibration.csv).
""")
    cross=['V12_DOM_LOCATION','V12_FUTURES_LOCATION','V12_JOINT_LOCATION','V12_DOM_IV','V12_JOINT_IV','V12_DIVERGENCE',
           'V12_IV_ASYMMETRY','V12_SURFACE_TAIL_SCALE']
    emit(6,f"""
Joint features express cash momentum relative to dated futures basis, finance rotation interacting with option skew, official breadth interacting with IV above trailing realized risk, futures OI against participation, momentum against IV change, concentration against downside skew, ETF activity against IV change, and the gap between liquid parity and the traded future. Each uses a trailing-63 past scale or a training-fit transformation. Futures curves use actual expiries. Same-contract changes require matching ID and lot, and roll and activity records remain distinct. The location-only comparison retains the strong statistical distribution and fits a capped partial location change. The market-risk scale models have separate output heads for terminal magnitude and annualized realized volatility. Skew effects are clipped and recentered before scoring.

{paired(cross,(5,21),('early','later','combined'),('brier','crps','path_volatility_mae','absolute_return_error'))}

Look for repeated gains against the same strong parent in both cohorts and coherent width/tail tradeoffs. Metadata and comparisons separate raw option additions, role-conditioned sources, interactions and earlier/later changes. [Futures curve and contract data](futures-observed.csv) · [Feature definitions](feature-receipts.json) · [Incremental scores](incremental-value.csv).
""")
    events=csv('event-conditioned-scores')
    e=events[events.event_active&events.cohort.eq('combined')&events.model.isin(['V12_EVENT_IV','V12_EVENT_HISTORY'])]
    emit(7,f"""
Weekly and monthly expiry proximity is obtained from the listed chain and dated traded fronts. Futures roll is an already observed contract switch. Exchange notices provide scheduled broad-index review dates, FOMC and RBI official calendars provide decision dates, and the FOMC announcement becomes observable to India after that U.S. day. The review-event history is partial and March 2026’s broad review contains no NIFTY50 replacements. Large moves, extreme bank rotation, weakening breadth, IV jumps and global moves use the preceding mature-fit sample’s 80th percentile. Economic surprise magnitudes and retrospectively chosen market shocks are excluded. [FOMC official schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) · [RBI 2025–26 schedule](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60062) · [RBI 2026–27 schedule](https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62422) · [Verified September 2025 index notice](https://niftyindices.com/Press_Release/ind_prs22082025.pdf) · [March 2026 review](https://www.niftyindices.com/Press_Release/ind_prs23022026.pdf).

The simple event baseline blends earlier like-event returns with normal historical returns using fixed 35% event weight, only after the event has at least 12 mature training origins. Other tests compare event-conditioned realized risk, market risk, and unconditioned IV scales on exact origins. Counts include both rolling dates and disjoint outcome windows. Sparse scheduled-event cells are descriptive and are kept as such.

{table(e,['horizon','model','event','n','disjoint','brier','crps','coverage80','V12_STAT_brier_gain','V12_STAT_crps_gain','path_volatility_mae'])}

[Full active and inactive event scores](event-conditioned-scores.csv) · [Origin flags and training cutoffs](event-origin-states.csv).
""")

    phase=scores[scores.model.str.match(r'PH_NATIVE_\d\d$')&scores.cohort.eq('combined')]
    supports=csv('phase-training-support')
    med=supports[supports.cohort.eq('later')&supports.model.isin(['PH_NATIVE_00','PH_NATIVE_06','PH_NATIVE_PLAIN',
      'PH_NATIVE_PHASE_MIXTURE','PH_MEM85_RECENT_PLAIN','PH_MEM85_SPREAD_PLAIN','PH_MEM85_PHASE_BALANCE_PLAIN',
      'PH_MEM85_DIVERSE_PHASE_MIXTURE','PH_MEM85_RANDOM_BLOCKS_PHASE_MIXTURE','PH_NATIVE_POOLED'])]
    fields=['training','nominal_rows','distinct_return_sessions','disjoint_training_windows','overlap_effective_count','member_location_sd','member_coefficient_sd']
    med=med.groupby(['horizon','model'])[fields].median().reset_index()
    emit(8,f"""
The deterministic calendar anchor is **{read('phase-registry.json')['phase_calendar_anchor']}**, the first date of the inherited frozen market matrix. Each observed session position modulo 5 or 21 defines one phase. Every phase is evaluated on the same historical origins where its inner and outer samples have enough matured rows. The full phase ensemble assigns equal weight to each fitted complete law. Averaging predicted locations and calibrating residuals once is a different comparison. Shared coefficients use phase-normalized equations and a block-average prior, while pooled coefficients combine block fits and the phase average.

{table(phase,['horizon','model','n','disjoint','brier','crps','accuracy','coverage80','width80'])}

The weekly native phase-zero result **{value('PH_NATIVE_00','brier')} / {value('PH_NATIVE_00','crps')}** reproduces V11. The all-phase weekly law achieves **{value('PH_NATIVE_PHASE_MIXTURE','brier')} / {value('PH_NATIVE_PHASE_MIXTURE','crps')}**. The monthly all-phase law reaches **{value('PH_NATIVE_PHASE_MIXTURE','brier',21)} / {value('PH_NATIVE_PHASE_MIXTURE','crps',21)}**. The lowest monthly phase Brier is a hindsight comparison and requires its own CRPS, alternative phase results and bounded null-reselection check.

![Weekly and monthly scores by fixed training phase]({(OUT/'phase-sensitivity.png').as_posix()})

Both the 85- and 126-row tests include fixed recent/spread dates, historical state diversity, random contiguous blocks, and approximately equal phase coverage. The following support estimates distinguish copied rolling labels from distinct underlying return dates. The phase location and coefficient dispersion measures are calculated within each fit. Across-phase tests still share the same period history.

{table(med)}

[All phases](leaderboard.csv) · [Matured training samples and row budgets](phase-ledger.json) · [Disjoint phases and episode deletion](phase-and-episode-stress.csv).
""")
    sim=csv('expert-information')
    sim=sim[sim.horizon.eq(5)&sim.cohort.eq('combined')&sim.condition.eq('all')]
    ename=[n for n in registry['configurations'] if n.startswith('J12_')]
    e=score(5,names=ename).sort_values('crps')
    inc_ensemble=inc[inc.model.isin(ename)&inc.horizon.eq(5)&inc.cohort.eq('combined')&inc.metric.isin(['brier','crps'])]
    emit(9,f"""
Expert novelty is measured using matched p(up), expected returns, distribution widths, signed directional and return errors, shared worst-decile dates, directional disagreement, and the energy distance between complete laws. Earlier, later and prior-volatility slices repeat the diagnostics. A high correlation can coexist with some information that matters in a tail. The fixed additions and leave-one-out experiments score the remaining law on identical endpoints, including calibration.

Exact aliases are canonicalized using a saved source identity and byte-exact atom/weight checks. There are **{sidebar['ensemble_exact_copy_checks']}** matched equality checks after appending two literal copies, including learned stacking after canonicalization. The naive extra-weight variant verifies what happens when copies are counted again. Similarity clustering sets equal cluster weight and keeps each distinct member with positive mass. Group balance separately uses statistical, phase, market-risk, historical and calibrated-shape roles.

{table(sim,['first','second','n','probability_corr','location_corr','width_corr','directional_error_corr','return_error_corr',
            'shared_worst_decile','direction_disagreement','energy_distance'])}

{table(inc_ensemble,PAIR)}

[All horizons and conditional redundancy](expert-information.csv) · [Duplicate checks](ensemble-exact-invariance.csv) · [Mature weight fits](ensemble-ledger.json).
""")
    addons=['V12_GLOBAL_SCALE','V12_INTRA_SCALE','V12_ETF_SCALE','V12_FUTURES_SCALE','V12_SURFACE_TAIL_SCALE','V12_IV_SCALE',
            'V12_DOM_LOCATION','V12_JOINT_LOCATION','V12_JOINT_IV','V12_EVENT_IV']
    legacy_path=csv('legacy-risk-comparisons')
    lp=legacy_path[legacy_path.cohort.eq('combined')&legacy_path.model.isin(['V12_IV_SCALE','V12_INTRA_SCALE','V12_IV_BRACKET'])&
       legacy_path.baseline.isin(['D_ROT_SCALE','D_DERIV_RISK','I_RISK_EQ'])]
    emit(10,f"""
Domestic location uses official breadth, slow breadth, financial and defensive rotation, cash momentum, sector dispersion and leadership concentration. Comparable uncertainty heads use observed trailing volatility, straddles, term/skew, price-curve tails and futures information. Additional tests hold the strong statistical location fixed while bringing in synchronized Upstox sector risk, ETF activity, global risk, or the dated futures curve. The international group uses V11’s earlier-date Nasdaq breadth, lagged global context, published U.S. volatility and yields, USD/INR, and Brent. Direct foreign observations carry an earlier source date and are checked against the archived 09:10 decision timestamp using the original conservative publication estimates. [FRED VIX](https://fred.stlouisfed.org/series/VIXCLS) · [FRED 10-year Treasury yield](https://fred.stlouisfed.org/series/DGS10) · [Nasdaq RSP close archive](https://www.nasdaq.com/market-activity/etf/rsp/historical).

{paired(addons,(5,21),('combined',),('brier','crps','absolute_return_error','path_volatility_mae'))}

## Matched comparison with prior V11 annualized risk heads

{table(lp,['horizon','model','baseline','n','market_mae','V11_mae','gain','low10','high10'])}

Purpose-specific gains in path volatility or movement error should be read independently from direction and from a whole-law score. The authentic domestic and global weighting proxies do not identify individual stock contributions. [Timestamp audit](external-publication-alignment.csv) · [Training feature definitions](feature-receipts.json) · [Matched coverage](matched-comparisons.csv) · [All cross-version risk estimates](legacy-risk-comparisons.csv).
""")
    candidates=['V12_STAT','V12_NATIVE_STAT','V12_IV_SCALE','V12_IV_NATIVE','V12_IV_ASYMMETRY','V12_JOINT_IV','P12_Q_PHYSICAL_MIX',
      'P12_Q_HIST_FALLBACK','PH_NATIVE_PHASE_MIXTURE','J12_PHASE_MARKET','J12_HISTORICAL_MARKET','J12_Q_EQUAL','J12_Q_STACK',
      'J12_STACK_BRIER','J12_STACK_CRPS','J12_Q_HISTORICAL']
    tails=csv('training-bucket-calibration')
    tail=tails[tails.model.isin(['V12_STAT','V12_IV_SCALE','V12_JOINT_IV','P12_Q_PHYSICAL_MIX','J12_PHASE_MARKET','V12_NEUTRAL'])&
                 tails.cohort.eq('combined')&tails.bucket.isin([0,5])]
    emit(11,f"""
The six architecture types are statistical baseline, priced scale, breadth/rotation location with priced uncertainty, calibrated statistical–market mixture, phase-balanced structural ensemble, and historical fallback. Fixed combinations precede learned comparisons. Learned stacking uses matured out-of-sample forecasts, at least 20 complete previous rows, simplex constraints and strong shrinkage to equal weights. Brier optimization and CRPS optimization target different proper scores.

Each complete return law generates its p(up), mean, median, endpoint price, quantiles and central intervals. Endpoint risk, downside bucket probabilities and training-defined relative tails are direct properties of that same law. Annualized path volatility is evaluated independently of the endpoint law. Maximum adverse excursion is outside the scope of an endpoint distribution. The column n distinguishes the subset carrying a priced curve.

## Weekly coherent forecast laws

{table(score(5,names=candidates).sort_values('crps'),SCORE)}

## Monthly coherent forecast laws

{table(score(21,names=candidates).sort_values('crps'),SCORE)}

## Bottom and top historically defined return buckets

{table(tail,['horizon','model','bucket','n','probability','observed','brier'])}

[Complete normalized probability laws](full-law-archive.json) · [All six buckets](training-bucket-calibration.csv) · [Probability calibration](calibration-bins.csv).
""")
    monthly=['NEUTRAL','HISTORY','REVERSION','V6_MONTH_LAG1','V8_MS_WINDOW','V8_MS_ROLL','P_CLUSTER','V12_STAT','V12_IV_SCALE',
             'V12_IV_NEUTRAL','V12_GLOBAL_SCALE','V12_JOINT_IV','V12_IV_BRACKET','V12_IV_LONGER','V12_IV_LAG5','V12_FUTURES_SCALE',
             'P12_Q_PHYSICAL_MIX','P12_Q_HIST_FALLBACK','Q12_NATURALLY_ALIGNED','PH_NATIVE_06','PH_NATIVE_PHASE_MIXTURE','J12_PHASE_MARKET']
    emit(12,f"""
Monthly endpoint forecasts have **217 rolling origins** and **11 disjoint windows**. The full symmetric reference remains **0.250000 Brier** and **0.025420 CRPS**. Expiry-matched prices, longer maturities, skew, term variance, futures curve, 21-session breadth, slow sector leadership, path-risk calibration and historical shrinkage are new interpretable inputs. Evidence for direction, full endpoint law, movement, path volatility and tail calibration can differ. The V8 monthly smooth result still faces its earlier shifted-state falsification.

{panel(monthly,21)}

{table(score(21,names=monthly),RISK)}

The isolated phase-six and naturally aligned subset results are reported with full sample eligibility and disjoint diagnostics. The monthly tables do not infer tight sampling uncertainty from so few independent return periods. As-of source timing and weak casewise coverage deserve at least as much attention as rank. [Monthly probability](monthly-probability-ranking.csv) · [Monthly distribution](monthly-distribution-ranking.csv) · [Matched risk errors](observable-priced-risk.csv) · [Disjoint and deletion diagnostics](phase-and-episode-stress.csv).
""")
    k=knowledge()
    emit(13,f"""
The evidence registry retains the implemented mechanisms, supporting cohorts, strongest matched evidence, passed and failed falsifications, benchmark strength, replication, and unanswered mechanism in each line of research. Predictive discoveries remain separate from reproducible engineering achievements such as exact-copy canonicalization, archived forecasts, phase accounting, and mature-only fit clocks. Earlier configuration schemas differ and their distinct counts represent cumulative exposure rather than independent trials.

{table(k)}

[Machine-readable cumulative hypotheses](cumulative-hypothesis-registry.csv) · [Search exposure inventory](cumulative-search-sources.json) · [V11 source preservation](protected-inputs.json).
""")
    selected=csv('refit-null-selected');rstats=[]
    for key,g in selected.groupby(['family','horizon','cohort','metric']):
        true=g[g.draw.eq(-1)].iloc[0];fake=g[g.draw.ge(0)].best_gain
        rstats.append(dict(zip(['family','horizon','cohort','metric'],key))|{'observed best gain':true.best_gain,
            'null median':fake.median(),'null p95':fake.quantile(.95),'null exceedance fraction':(fake>=true.best_gain).mean(),'n':true.origins})
    a=pd.DataFrame([{'score family':family,'scope':c,'dates':d['calendar_dates'],'tested contrasts':d['contrasts'],'block-10 critical':d['max_t']['10']}
                    for family,key in [('endpoint Brier and CRPS','scopes'),('path risk and movement','risk_and_magnitude_scopes')]
                    for c,d in un[key].items()])
    fail=pd.DataFrame([f for f in registry['attempts'] if f['status']!='ok'])
    failure=fail.groupby(['batch','reason'],dropna=False).size().reset_index(name='unestimated') if len(fail) else fail
    control=[n for n in registry['configurations'] if n.startswith('V12_CONTROL_') or n.startswith('V12_IV_LAG') or n in [
             'V12_RV_SCALE','V12_STRADDLE_SCALE','V12_IV_SAME_CLOSE','V12_IV_LIQUID','V12_IV_SETTLEMENT','V12_IV_BRACKET',
             'V12_IV_LONGER','V12_IV_RATE_ZERO','V12_IV_RATE_HIGH','Q12_SMOOTH','Q12_TRUNCATED']]
    emit(14,f"""
The run checks chronological fit boundaries, fully matured labels, the strictly purged inner phase fit, train-only canonicalization and regularization, origin/endpoint equality, earlier option source dates, and immutable prior artifacts. Verified counts include **{sidebar['distinct_fit_artifacts']:,}** fit artifacts, **{sidebar['ensemble_exact_copy_checks']}** exact portfolio-of-experts duplication tests and **{sidebar['casewise_timing_and_copy_checks']}** feature-copy and future-data sentinels. The option audit rejects invalid solutions and retains full refusal reasons. Market returns, listed expiries and U.S. inputs carry their own event clocks.

{paired(control,(5,21),('combined',))}

The uncertainty families use 2,000 paired circular block draws at lengths 5, 10 and 15. Weekly endpoint Brier and CRPS share a joint maximum. Weekly path-volatility and absolute-movement error have a separate joint maximum. These sets condition on the V12 design and observed archive. They cannot correct the entire V1–V12 adaptive search or create independent monthly observations.

{table(a)}

Twelve representative block-permuted refit-and-reselection draws recompute phase winners, market recalibration and constrained ensemble weighting while keeping held-out realized outcomes fixed. These small diagnostic subsets do not confer a precise cumulative p value.

{table(pd.DataFrame(rstats))}

{table(failure)}

[Paired intervals](paired-uncertainty.json) · [Null selections](refit-null-selected.csv) · [Block sensitivity](market-training-perturbations.csv) · [Verification](verification.json).
""")
    full=score(5);full=full[full.full_scope&~full.diagnostic]
    m=score(21);m=m[m.full_scope&~m.diagnostic]
    higher=score(5,'later');higher=higher[higher.full_scope&~higher.diagnostic]
    physical=['V12_IV_SCALE','V12_IV_ASYMMETRY','V12_JOINT_IV','P12_Q_PHYSICAL_MIX','P12_Q_TILT','J12_Q_STACK',
             'J12_PHASE_MARKET','J12_HISTORICAL_MARKET','PH_NATIVE_PHASE_MIXTURE','PH_NATIVE_00']
    quart=mate[mate.model.isin(physical)&mate.cohort.eq('combined')&mate.metric.isin(['brier','crps'])&
              mate.baseline.isin(['NEUTRAL','O_NATIVE_PHASE0','J11_EXCLUDE_B_ROT','V12_RV_SCALE'])]
    emit(15,f"""
V12 scored **{sidebar['predictions']:,}** research forecasts in **{len(registry['configurations'])}** registered systems and **{len(mate):,}** exact paired comparisons. Earlier weekly 173, later weekly 92, combined weekly 265, earlier monthly 141, later monthly 76 and combined monthly 217 remain the headline coverage. Market-priced systems with different coverage have separately recomputed benchmarks and visible n. Q diagnostics are excluded from the physical leaderboard. All comparison columns use lower-is-better loss; positive gain is the control loss less candidate loss.

## Weekly full-coverage probability leaders

{table(full.sort_values('brier').head(12),SCORE)}

## Weekly full-coverage distribution leaders

{table(full.sort_values('crps').head(12),SCORE)}

## Later weekly full-coverage probability leaders

{table(higher.sort_values('brier').head(10),SCORE)}

## Monthly full-coverage probability

{table(m.sort_values('brier').head(10),SCORE)}

## Monthly full-coverage distributions

{table(m.sort_values('crps').head(10),SCORE)}

## Market and phase candidates on exact dates against strong controls

{table(quart,PAIR)}

[Earlier/later Pareto comparison](cohort-pareto.csv) · [Volatility and movement](volatility-and-movement-ranking.csv) · [Incremental source value](incremental-value.csv) · [All rows](all-predictions.csv).
""")
    new=full[full.family.ne('frozen')]
    b=new.sort_values('brier').iloc[0];c=new.sort_values('crps').iloc[0]
    rv_all=score(5);rv=rv_all[rv_all.path_volatility_mae.notna()&rv_all.full_scope].sort_values('path_volatility_mae')
    mrv=score(21);mrv=mrv[mrv.path_volatility_mae.notna()&mrv.full_scope].sort_values('path_volatility_mae')
    def riskline(d):
        if d.empty:return 'The scale comparisons have different eligibility and use paired controls.'
        x=d.iloc[0]
        return f"{x.model} has annualized path-volatility MAE {x.path_volatility_mae:.6f} over {int(x.n)} origins."
    evalrisk=inc[inc.cohort.eq('combined')&inc.model.isin(['V12_IV_SCALE','V12_IV_LEVEL','V12_IV_BRACKET','V12_GLOBAL_SCALE',
           'V12_FUTURES_SCALE','V12_INTRA_SCALE','V12_ETF_SCALE'])&inc.metric.eq('path_volatility_mae')]
    qvs=mate[mate.cohort.eq('combined')&mate.model.isin(['Q12_RAW','P12_Q_PHYSICAL_MIX','P12_Q_HIST_FALLBACK'])&
          mate.baseline.isin(['J11_EXCLUDE_B_ROT','NEUTRAL'])&mate.metric.isin(['brier','crps'])]
    stronger=mate[mate.cohort.eq('combined')&mate.model.isin(['V12_IV_SCALE','V12_IV_BRACKET','V12_IV_LAG5','V12_STRADDLE_SCALE',
      'V12_INTRA_SCALE','V12_RV_SCALE','V12_CONTROL_NOISE'])&
      mate.baseline.isin(['V12_RV_SCALE','V12_RV_PATH'])&mate.metric.eq('path_volatility_mae')]
    weekly_obs=obs[obs.horizon.eq(5)&obs.cohort.eq('combined')&obs.target.eq('realized_vol')].set_index('market_feature')
    matched_iv=stronger[stronger.horizon.eq(5)&stronger.model.eq('V12_IV_SCALE')&stronger.baseline.eq('V12_RV_SCALE')].iloc[0]
    direct=mate[mate.horizon.eq(5)&mate.cohort.eq('combined')&mate.model.eq(c.model)&
                mate.baseline.eq('J11_EXCLUDE_B_ROT')&mate.metric.eq('crps')]
    delta='' if direct.empty else f"The matched CRPS gain versus V11 is {direct.gain.iloc[0]:.6f}, with block-10 adjusted interval {direct.low10.iloc[0]:+.6f} to {direct.high10.iloc[0]:+.6f}."
    dd=mate[mate.horizon.eq(5)&mate.cohort.eq('combined')&mate.model.eq(b.model)&
             mate.baseline.eq('O_NATIVE_PHASE0')&mate.metric.eq('brier')]
    brier_delta='' if dd.empty else f"The gain against the original native phase-zero Brier is {dd.gain.iloc[0]:.6f}, with adjusted interval {dd.low10.iloc[0]:+.6f} to {dd.high10.iloc[0]:+.6f}."
    emit(16,f"""
V12 reconstructed **{sidebar['priced_expiry_distributions_checked']:,}** accepted risk-neutral expiry laws across the declared methods from authenticated historical option prices. Main traded-mark curves had **{int(bars.loc[bars.method.eq('TRADE'),'accepted density'].iloc[0]):,}** supported date-expiries. The bounded convex-price interpolation, exact mass normalization and forward constraint are reproducible. Option-price shape and forecasts of realized returns remain distinct estimands.

On full combined weekly coverage, the strongest V12 point Brier is **{b.brier:.6f}** from **{b.model}**, and the strongest V12 point CRPS is **{c.crps:.6f}** from **{c.model}**. {brier_delta} {delta} The weekly Brier leader scales the frozen native phase-zero law by realized-risk information. A repeated prior phase under a new ID should be read as a replay. The complete equal-phase mixture produces **{value('PH_NATIVE_PHASE_MIXTURE','brier')} / {value('PH_NATIVE_PHASE_MIXTURE','crps')}**. Weekly {riskline(rv)} Monthly {riskline(mrv)} These rankings answer different questions.

The simple weekly nearest-expiry at-the-money IV observable had annualized realized-volatility MAE **{weekly_obs.at['iv_nearest','mae']:.6f}** against **{weekly_obs.at['rv_forecast','mae']:.6f}** for trailing realized volatility on the same {weekly_obs.at['iv_nearest','n']} origins. Adding the IV inputs to the fitted realized-risk model changed MAE from **{matched_iv.control:.6f} to {matched_iv.candidate:.6f}**. The search-adjusted gain interval was **{matched_iv.low10:+.6f} to {matched_iv.high10:+.6f}**. The sign probability and full-distribution scores assess the endpoint return, while these risk scores assess the path of returns to that endpoint. [Market observables](V12_EXPECTATION_VS_REALITY.md).

## Path-volatility increments against exact eligible parents

{table(evalrisk,PAIR)}

{table(stronger,PAIR)}

## Raw and calibrated pricing laws against realized-return references

{table(qvs,PAIR)}

The main evidence is conditional, historical and exposed. The full monthly symmetric forecast remains the primary reference. Point rankings over selected calendar phases or maturity subsets require their adjusted or disjoint checks. There is no independently validated prediction edge in this study. [Full comparisons](V12_COMPLETE_COMPARISON.md) · [Verified laws](verification.json).
""")
    emit(17,"""
1. Freeze the liquid-strike selection, parity-forward estimator, quote delay, and exact statistical parent before evaluating additional years or truly prospective 2026 origins. Archive timing receipts with the prices.
2. Choose the realized path-risk metric independently from endpoint CRPS and Brier. Compare priced risk, trailing realized risk and straddles on the same naturally aligned and approximate samples.
3. Prespecify the complete equal-phase mixture and optional shrinkage. Keep the phase-zero replay and all other phase scores so phase selection can be diagnosed.
4. Add authenticated bid/ask timestamps and dated near-tenor funding where available. Improve coverage only inside the observed strike support and report wing uncertainty separately.
5. Keep exact duplicate canonicalization, group diversity, simple fixed mixture controls, and realized-curve calibration distinct in future archive scoring. Gather independent episodes before inferring a physical risk-premium relationship.

[Reference index](NIFTY_V12_RESEARCH.md).
""")
    listing='\n'.join(f'{i}. [{n.replace("_"," ").title()}](V12_{n}.md)' for i,n in enumerate(TITLES,1))
    (OUT/'NIFTY_V12_RESEARCH.md').write_text(f"""# NIFTY V12 Market-Implied Research

**{sidebar['predictions']:,} scored predictions · {len(registry['configurations'])} configurations · {len(mate):,} paired comparisons · 17 reports**

Frozen market history ends November 17, 2026. All evaluated origins are historical and research-exposed. The refresh separately verifies completed dates through {refresh['closed_sessions'][-1]}.

## Reports

{listing}

## Reproducibility

[Research mission](MISSION.md) · [Run instructions](README.md) · [Verification](verification.json) · [Experiment registry](registry.json) · [Full physical and diagnostic law archive](full-law-archive.json) · [Manifest](manifest.json)
""",encoding='utf-8')


if __name__=='__main__':sections()
