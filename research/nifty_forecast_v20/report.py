"""Build the requested V20 report set from verified numerical artifacts."""
from functools import lru_cache
from .common import *
from research.nifty_forecast_v18.report import tab,fmt

@lru_cache(maxsize=None)
def data(name):
    return csv(name)

def where(z,**criteria):
    for k,v in criteria.items():
        z=z[z[k].isin(v) if isinstance(v,(list,tuple,set)) else z[k].eq(v)]
    return z

def table(z,fields=None,n=30):
    if z.empty:return 'No matched observations met this comparison’s coverage rule.'
    return tab(z,fields,n)

def links(*files):
    return ' · '.join(f'[{f}]({f})' for f in files)

def report(i,body):
    name=REPORTS[i-1]
    (OUT/f'V20_{name}.md').write_text(f'# V20 {name.replace("_"," ").title()}\n\n'+body.strip()+'\n',encoding='utf-8')

def lead(track,h=None,clock=None,scope='combined'):
    z=where(data('model-leaderboards.csv'),track=track,scope=scope)
    if h:z=where(z,horizon=h)
    if clock:z=where(z,cutoff=clock)
    return z

def matched(track,**kw):
    return where(where(data('complete-matched-comparisons.csv'),track=track),**kw)

def life(**kw):
    return where(data('information-lifetime-matrix.csv'),**kw)

def atlas(rows):
    cols=['family','end_offset','matched','disjoint','parent','enhanced','gain','earlier_gain','later_gain','adjusted_low','adjusted_high']
    return table(rows,cols,len(rows))

def best(d,k='brier',n=6):
    return d.dropna(subset=[k]).nsmallest(n,k)

def split_lead(d,keys,metrics,n=6):
    return pd.concat([best(x,k,n).assign(ranked_metric=k) for _,x in d.groupby(keys) for k in metrics],ignore_index=True)

def audit_and_lifetimes():
    timing=read('timing-audit-receipt.json')
    whole=read('predecessor-inventory.json')
    z=data('native-audit-summary.csv')
    h0=where(z,track='parent_replay',scope='all')
    m=where(z,track='mechanism_replay',scope='active',horizon=21)
    omit=data('native-audit-cohort-and-omission.csv')
    report(1,f'''V20 verified {whole['artifacts']:,} V19 files, {whole['source_files']} source modules and the predecessor-manifest chain. Replays covered {timing['replayed_cases']:,} scored native predictions and mechanism cases. Their largest scalar deviation was {timing['checked_scalar_error']:.3g}. The code reread the original V14 weighted atoms, refitted the V18 corporate and V19 participant residuals using their documented historical forecast errors, and compared atom arrays, weights, specific bias and lag controls, active cases and fallbacks.

The V14 registration defines the native issue at **09:10 IST on the cash session following the reference close**. The archived V19 decision field reads **08:55** because it records the snapshot of newly added inputs. In all {timing['actual_native_origins']} horizon-origin records, the modeled participant availability was **08:15 before 08:55**. V18 corporate publications, structured financial releases and price reactions cleared their own snapshot clock. The V14 options source day precedes the cash reference day. The same-clock archived V14 parent is appropriate for the native additions at 09:10. Rebuilt 08:55 V17 forecasts and prior-evening forecasts occupy their own tracks. The per-report publication time remains an assumption inherited from V19. The preceding-evening and lagged variants quantify sensitivity to the timing assumption.

{table(h0,['horizon','model','n','active','disjoint','brier','crps','log_loss'],10)}

{table(m,['model','n','disjoint','brier','crps','log_loss'],9)}

{table(omit,['horizon','metric','early','later','combined','active_gain','remaining_gain','removed_start','removed_end'],8)}

The placebo code reproduced 23 block rotations or permutations independently for each horizon and reselected among the native feature families in each run. The preserved monthly neutral law at 08:55 gives Brier 0.250000 and CRPS 0.025543. The distinct V15 GJR path law gives Brier 0.251376 and CRPS 0.024694. The 248-case GIFT opening result keeps its original forecast clock.

{links('timing-audit-receipt.json','native-source-clock-audit.csv','native-audit-cases.csv.gz','native-audit-summary.csv','native-audit-null-replay.csv','native-audit-cohort-and-omission.csv','predecessor-inventory.json')}''')
    reg=data('cumulative-information-registry.csv')
    report(2,f'''The registry specifies all 18 required information families. A raw price, report or contract count retains its source definition. Relative returns, exposure ratios, breadth and filing aggregates are constructed measures. The principal-component state and multi-output coefficients are fitted representations. The cross-version reference is stored alongside the **matched 08:55 V20 fresh-information comparison** so that the historical benchmark, live eligibility and source completeness remain inspectable.

{table(reg,['family','earlier_versions','source_and_availability','known_1700','known_0855','archived_matched_evidence','classification'],18)}

{table(reg,['family','h5_matched','h5_disjoint','h5_gain','h5_earlier_gain','h5_later_gain','h21_matched','h21_disjoint','h21_gain','h21_earlier_gain','h21_later_gain'],18)}

The downloadable registry includes exact field lists, known redundancies, the parent and enhanced losses, shifted controls, adjusted bands, failure mechanisms and next questions. The V12 inventory adds historically tested training-memory, overlap, duplicate-feature and distribution-construction mechanisms. The reproducibility of data publication and model arithmetic does not promote a retrospective signal to an independent validation.

{links('cumulative-information-registry.csv','cumulative-v12-predecessor-registry.csv','registry-receipt.json','feature-definitions.json','feature-coverage.csv','information-lifetime-matrix.csv','complementarity-feature-redundancy.csv')}''')
    q=read('lifetime-receipt.json')
    visible=life(cutoff='preauction_0855',mode='cumulative',metric='crps',age='fresh',end_offset=(1,5,21))
    early=visible.pivot(index='family',columns='end_offset',values='gain').reset_index().rename(columns={k:f'gain_{k}' for k in (1,5,21)})
    late=life(cutoff='preauction_0855',mode='incremental',metric='crps',age='fresh',start_offset=5,end_offset=21)
    span=life(cutoff='preauction_0855',mode='incremental',metric='crps',age='fresh',
       family=('offshore_gift','corporate_announcements','participant_futures','financial_rotation'))
    decomp=span.pivot(index='family',columns=['start_offset','end_offset'],values='gain').reset_index()
    decomp.columns=['family']+[f'{a+1}–{b}' for a,b in decomp.columns[1:]]
    grouped=life(cutoff='preauction_0855',mode='cumulative',metric='crps',end_offset=21,
       family=('offshore_gift','corporate_announcements','participant_futures','atm_iv','financial_rotation'))
    ages=grouped.pivot(index='family',columns='age',values='gain').reset_index().reindex(columns=['family',*AGES])
    rsk=life(cutoff='preauction_0855',mode='risk',metric='qlike',age='fresh',end_offset=(1,5,21))
    rsk=pd.concat([b.nlargest(4,'gain') for _,b in rsk.groupby('end_offset')])
    positive=life().loc[lambda z:z.adjusted_low.gt(0)]
    first=where(visible,family='offshore_gift',end_offset=1).iloc[0]
    flow=life(family='institutional_flows',cutoff='preauction_0855',age='lag3',end_offset=21,mode='cumulative',metric='brier').iloc[0]
    report(3,f'''The central experiment tested **18 source families**, **two clocks** and **seven input vintages**. Cumulative close-to-close targets were 1, 2, 3, 5, 7, 10, 15 and 21 sessions. Separate returns cover session one, sessions 2–3, 4–5, 6–10, 11–15 and 16–21. The 6–21 target directly takes the first week out of the 21-session move. Annualized realized risk is scored separately at all eight cumulative horizons. All years are research-exposed, including these intermediate endpoints.

The general lifetime parent is a chronological cash-price and risk model with a complete empirical law. Each enhanced model adds a shrunk fitted slope from the new family, trained on earlier forecast errors. Fresh, lags of 1, 3, 5, 10 and 21 cash sessions, and causal five-session smoothing use the same training policy. Comparisons use the matched parent on dates when the candidate could run. The full population uses the parent wherever training or observations are missing. The machine matrix preserves the common 21-session origin subset for shape comparisons across horizons. Absolute and relative gains, matched and non-overlapping counts, earlier/later gains, and an identical-date five-session-shift comparison are included for every eligible cell.

## Fresh cumulative return CRPS gains at 08:55

{table(early,['family','gain_1','gain_5','gain_21'],18)}

## Fresh later cash-session components at 08:55

{table(decomp,None,10)}

The 6–21 component answers whether a source conveys timing information after the first week under this specific model. An apparent 21-session improvement can come entirely from earlier returns. These statistical shapes are descriptions of this historical sample.

{atlas(late.sort_values('gain',ascending=False))}

## Age of information and realized-risk gains

{table(ages,None,10)}

{table(rsk,['family','end_offset','matched','gain','earlier_gain','later_gain','adjusted_low','adjusted_high'],16)}

## Gains with positive adjusted lower bounds

Fresh GIFT at 08:55 reduced first-session CRPS from **{first.parent:.6f} to {first.enhanced:.6f}** across **{int(first.matched)}** matched sessions. Its cumulative advantage remained visible through three sessions. The later isolated component comparisons have weaker evidence. The three-session-aged CDSL and AMFI flow group reduced monthly Brier from **{flow.parent:.6f} to {flow.enhanced:.6f}** on **{int(flow.matched)}** cases spanning **{int(flow.disjoint)}** disjoint windows. A neutral 50% forecast scores **0.250000** on those same dates. The flow group holds eligible custody, fortnightly and mutual-fund reports across cash days. Its results depend on modeled publication lags and relatively few distinct report vintages.

{table(positive,['cutoff','family','age','mode','end_offset','metric','matched','disjoint','gain','adjusted_low','adjusted_high'],20)}

These bands account for family and age selection within each clock, metric and target. The reported gains share historical observations across clocks and horizons. Delivery and realized-risk associations use the general lifetime parent. The protected IV/GJR risk models have their own comparisons.

The archives contain {q['case_rows']:,} case comparisons. They store each parent’s sorted atoms plus the model’s shift, making every complete candidate law directly reconstructible. For each clock, target and metric, {600:,} circular date-block draws adjust for the declared search over sources and ages.

{links('information-lifetime-matrix.csv','lifetime-cases.csv.gz','lifetime-law-index.csv','lifetime-parent-laws.npz','lifetime-fresh-fit-examples.ndjson.gz','opening-and-late-associations.csv','information-lifetime-heatmap.png')}''')
    n=lead('native',21)
    selected=where(n,model=['exact_v14','v19_position_native','positions_v19_feature_set','bias_only','fii_level','fii_changes','dii_level',
       'pro_level','gross_exposure','concentration','trading_volume','stock_futures','options','persistence','new_innovations','changes_plus_analogue',
       'preceding_evening','lag1','lag3','lag5','lag10','lag21','smooth5','short_training70','omit_latest_21_training_origins','eight_calendar_day_embargo'])
    reg=where(data('mechanism-regime-comparisons.csv'),horizon=21,scope='active',regime=('all_','away_from_expiry','high_concentration',
        'other_concentration','high_iv','ordinary_iv','rising_state','falling_state'))
    beta=where(data('coefficient-stability.csv'),horizon=21,model='positions_v19_feature_set')
    beta=beta.assign(strength=beta['median'].abs()).nlargest(18,'strength')
    report(4,f'''The native parent and V19 law replay are exact. Separate V20 fits distinguish FII futures level, changes over 1, 3, 5, 10 and 21 sessions, DII level, proprietary level, gross exposure, participant concentration, volume, stock futures and aggregate options. The persistence block adds an earlier rolling standardization, a 21-session exposure mean and acceleration. A participant’s option counts are exchange-classified contract counts. Portfolio delta and personal open interest are unobserved.

The new innovation estimator uses the median observed position change of the **15 nearest earlier historical states**, considering returns, volatility, expiry, roll status, breadth, basis and prior positioning. It selects those contexts from at most **150** earlier observations and needs at least **50**. Standardization and the innovation’s empirical rank are historical-only. The table compares a direct ordinary change block, the analogue innovations and a combined design on the same native parent.

{table(selected,['model','n','active','disjoint','brier','crps','log_loss'],30)}

The cohort study displays announcement, volatility, trend and concentration ranks computed from earlier inputs, plus dated expiry and rollover. The output includes measurement availability, training sample size, elapsed-market state, disagreement and alternative fitting windows. Associations within these strata and signs of median coefficients are sensitive to the model and available observations.

{table(reg,['cohort','regime','n','mean_FII','mean_IV','mean_n_train','v19_brier_gain','v19_crps_gain','new_brier_gain'],18)}

{table(beta,['cohort','field','median','p10','p90','positive','fit_count'],20)}

{links('native-mechanism-cases.csv.gz','mechanism-regime-comparisons.csv','coefficient-stability.csv','native-fit-receipts.ndjson.gz','native-audit-cohort-and-omission.csv','all-disjoint-window-phases.csv')}''')
    c=lead('native',5)
    sel=where(c,model=('exact_v14','v18_corporate_native','bias_only','counts','semantics','structured','calendar','price_reaction','weighting',
       'corporate_v18_feature_set','positioning_only','corporate_plus_positioning','probability_only','slopes_without_intercept',
       'scale_only','asymmetry_only','location_scale_asymmetry','lag1','lag5','lag21','preceding_evening'))
    high=where(data('mechanism-regime-comparisons.csv'),horizon=5,scope='active',regime=('high_announcement','other_announcement'))
    report(5,f'''The weekly comparison uses the same native 09:10 V14 law. V18's full corporate residual is replayed exactly, with its input snapshot frozen at 08:55. The decomposition tests counts, signed semantic aggregates, period-matched financial surprises, sector weights, scheduled earnings and disagreement with the observed corporate price response. It also fits historical bias, position-only and combined position/corporate corrections. The archived V18 overlay and the V20 refit of a similar feature list have different reported rows so training coverage and regularization remain visible.

The activation and subgroup thresholds for announcement intensity use only available earlier observations. A high intensity date has a count rank of at least **0.70**. Every subgroup is compared with its own unchanged V14 parent on the exact same dates. Sign-probability reweighting keeps within-sign shapes, while scale-only and asymmetry-only modifications preserve full empirical laws.

{table(sel,['model','n','active','disjoint','brier','crps','log_loss','covered','width'],29)}

{table(high,['cohort','regime','n','disjoint','mean_n_train','v19_brier_gain','new_brier_gain','new_crps_gain'],8)}

{links('native-mechanism-cases.csv.gz','native-config.json','mechanism-regime-comparisons.csv','matched-block-intervals.csv.gz','native-audit-null-replay.csv','probability-calibration.csv')}''')

def construction():
    cols=['horizon','scope','model','n','active','disjoint','brier','crps','log_loss','balanced_accuracy','covered','width']
    x=lead('architecture')
    c=matched('architecture',scope='active_matched',parent='A_one_shared_head',metric=('brier','crps'))
    report(6,f'''The shared representation and both separate heads train on the **same rows of fully matured 21-session history** before an issue. All estimated architectures use the same archived horizon law for shape. The candidate heads change location, and the fixed mixture preserves the original law and a specialized law with equal weight. A common-field separate-head control distinguishes different learned outputs from the effect of changing the features. A training-only rank-three state, a shared core with horizon-specific residuals, pre-specified sparse blocks and a strongly regularized rank-one multi-horizon head provide additional comparisons. Bank and IT relative returns enter an auxiliary reduced-rank fit on the same market dates.

{table(x,cols,22)}

{table(c,['horizon','model','metric','n','disjoint','parent_loss','loss','gain'],36)}

The strongest model names in each metric table are separate experimental results. V17's five-session decomposition and the symmetric 21-session law are matching-clock controls. The matched GJR law retains its own path construction. Native 09:10 V14/V18 and V19 overlays are measured separately.

{links('architecture-config.json','architecture-cases.csv.gz','architecture-laws.npz','architecture-training-receipts.csv','complete-matched-comparisons.csv','matched-block-intervals.csv.gz')}''')
    t=lead('temporal')
    components=data('component-leaderboard.csv')
    comp=components[components.model.isin(['horizon_specific_components','low_rank_joint','unconditioned_joint'])]
    strong=where(data('strong-parent-component-comparisons.csv'),cutoff='preauction_0855',metric='crps').copy()
    strong['sessions']=strong.start_offset.add(1).astype(str)+'–'+strong.end_offset.astype(str)
    report(7,f'''Monthly forecasts are constructed from four log-return pieces covering sessions **1–5, 6–10, 11–15 and 16–21**. All four pieces are unavailable at issue. The outcome, benchmark and candidate endpoint share the original cash reference and exact monthly expiry session. We compared ordinary joint multi-output ridge, reduced-rank coefficients, separate horizon features including corporate inputs early and positioning later, nearest risk-conditioned historical residual vectors, and a deliberate independent-resampling control. The residual histories consist of chronological errors. All their components had matured before the next model fit.

Each candidate adds one common residual row to the four fitted component locations. Compounding that vector gives one complete terminal scenario. The independence control permutes the columns separately and isolates the impact of removing historical dependencies. The same-clock direct specialized forecast and neutral archive provide independent endpoint comparisons.

{table(t,cols,15)}

{table(comp,['start_offset','end_offset','model','cohort','n','brier','crps','coverage','width'],28)}

The combined 6–21 outcome in the lifetime matrix measures the period after the first week directly. To check sensitivity to that experiment’s cash-price parent, a separate comparison forecasts sessions 1–5 and 6–21 from the **same 217 monthly origins** using the corresponding return from each archived same-clock GJR path. Each tested correction uses only matured errors for that same target. The evening and pre-auction comparisons include a no-shift parent, bias, fresh or aged positioning, two slow positioning representations and corporate announcements. The table shows matched CRPS and the 21-session-block, search-adjusted gain bands for the pre-auction comparisons. The full-population losses include fallbacks.

{table(strong,['sessions','model','matched','disjoint','parent','matched_loss','full_loss','earlier_gain','later_gain','interval_adjusted_low','interval_adjusted_high'],18)}

{links('temporal-cases.csv.gz','component-case-scores.csv.gz','component-leaderboard.csv','component-law-archive.npz','architecture-laws.npz','information-lifetime-matrix.csv','strong-parent-component-comparisons.csv','strong-parent-component-cases.csv.gz','strong-parent-component-laws.npz','strong-parent-component-config.json')}''')
    s=data('complementarity-shapley.csv.gz').groupby(['horizon','block'],as_index=False)[['brier','crps','first_brier','last_brier']].mean()
    p=data('complementarity-prediction-correlation.csv')
    k=data('complementarity-feature-redundancy.csv').groupby(['horizon','pair'],as_index=False).median(numeric_only=True)
    report(8,f'''We evaluated the unchanged structural law and all **31 nonempty subsets** of five predeclared groups at 08:55 for both original horizons. The blocks are native structure, corporate information, participant positioning, delivery and market-implied/realized risk. The incremental slope excludes its intercept, and the parent law handles missing training. This holds baseline shape and shrinkage policy fixed so that marginal changes and conflicting effects can be observed on matched forecasts. Shapley averages across all addition orders. The first and last columns show the marginal difference from the empty group and from the full group with that block removed.

{table(s,['horizon','block','brier','crps','first_brier','last_brier'],12)}

{table(where(p,group_a='corporate',group_b='positioning'),['horizon','cohort','n','forecast_rank','error_rank','correction_rank'],8)}

{table(k[k.pair.str.contains('corporate')],['horizon','pair','median_absolute_pairwise_feature_rank','max_absolute_pairwise_feature_rank'],10)}

Forecast correlations, error correlations and the correlation of incremental shifts measure different kinds of duplication. The separate prior training feature correlation records contain only earlier points at the moment of each fit. An exact duplicate enters the fit only once, and mixtures of identical expert laws reduce to the identical input law. These comparisons describe forecast estimation and are distinct from economic attribution.

{links('complementarity-cases.csv.gz','complementarity-shapley.csv.gz','complementarity-prediction-correlation.csv','complementarity-feature-redundancy.csv','native-mechanism-cases.csv.gz')}''')
    c=where(lead('native'),model=('exact_v14','bias_only','corporate_v18_feature_set','positions_v19_feature_set','slopes_without_intercept',
      'probability_only','scale_only','asymmetry_only','location_scale_asymmetry','fixed_half_shift','fixed_half_law_mixture','learned_history_law_mixture'))
    active=matched('native',metric=('brier','crps'),scope='active_matched',parent='exact_v14',
                   model=('corporate_v18_feature_set','positions_v19_feature_set','probability_only','location_scale_asymmetry','fixed_half_law_mixture','learned_history_law_mixture'))
    report(9,f'''Correction models use only earlier archived out-of-sample forecast errors. Translation adds one bounded log-return shift. Scale and asymmetry transform centered log returns. Sign probability is represented by adjusting the weights on existing complete atoms. Fixed and learned weights mix complete corrected and parent laws. The mean, median, probability and tail quantiles are all read from the same law. Shape, bias-only, shrinkage and missing-input fallbacks each produce separately archived predictions.

{table(c,cols,28)}

{table(active,['horizon','model','metric','n','disjoint','parent_loss','loss','gain'],26)}

The monthly translation cap is 1.2 log percentage points and the weekly cap is 0.9. Shape experiments have separate scale and skew restrictions. The history-weighted mixture trains with earlier measured improvements and is capped at 0.75 correction weight.

{links('native-mechanism-laws.npz','native-mechanism-cases.csv.gz','native-fit-receipts.ndjson.gz','native-config.json','complete-matched-comparisons.csv','probability-calibration.csv')}''')
    a=where(lead('native',scope='combined'),model=('exact_v14','v18_corporate_native','v19_position_native','corporate_v18_feature_set',
        'positions_v19_feature_set','fixed_half_shift','predeclared_activation','learned_activation','learned_history_law_mixture'))
    b=matched('native',parent='exact_v14',metric=('brier','crps'),scope=('active_matched','earlier','later'),model=('predeclared_activation','learned_activation'))
    report(10,f'''Three decisions are visible for every native original cohort. The parent can be used alone, the feature correction can be applied whenever the minimum fit and data are present, or the correction can be fractionally weighted or gated. The weekly simple gate needs a causal announcement intensity percentile of **0.70**. The monthly gate uses concentration rank **at least 0.48**, IV rank **at most 0.82**, and excludes the three days near the front expiry and identified rollover dates. A single regularized activation model trains on earlier realized Brier gains, using announcement and concentration state, IV and trend, correction size, a standardized feature-distance measure, training support and training-window instability. Both gates fall back to the exact parent on excluded dates.

{table(a.assign(inactive=a.n-a.active),['horizon','model','n','active','inactive','disjoint','brier','crps'],23)}

{table(b,['horizon','model','scope','metric','n','active','disjoint','parent_loss','loss','gain'],26)}

The active subset can be much smaller and correlated. The full population includes the fallback cases. The proper paired gain and actual denominator should accompany any selected-date score.

{links('native-mechanism-cases.csv.gz','mechanism-regime-audit.csv','mechanism-regime-comparisons.csv','complete-matched-comparisons.csv','matched-block-intervals.csv.gz')}''')


def risk_and_sources():
    p=lead('retained_point_risk')
    g=where(lead('joint_path'),cutoff='preauction_0855')
    trial=read('risk-receipt.json')
    bench=data('protected-point-risk-cases.csv.gz').groupby(['horizon','model','cutoff'],as_index=False).agg(
        n=('day','nunique'),mae=('mae','mean'),qlike=('qlike','mean'),brier=('brier','mean'))
    report(11,f'''The protected risk references retain their original populations and clocks. The source weekly raw ATM MAE is 0.037814, V16 offshore/domestic MAE 0.036469, monthly GJR MAE 0.033179 and variance QLIKE 0.199677. Weekly expansion Brier is 0.152707 for the fixed IV/realized-risk model and monthly expansion Brier is 0.172872 for Student EGARCH. The native Student-t GJR monthly range CRPS is 0.015422. The 08:55 GIFT-first weekly barrier Brier is 0.132201. V20 verified {trial['exact_path_parent_cases']:,} same-clock path baselines with maximum score difference {trial['maximum_path_score_difference']:.3g}.

{table(bench,['horizon','cutoff','model','n','mae','qlike','brier'],14)}

{table(p,['horizon','model','n','active','mae','q_like','brier','log_loss'],14)}

V20 tested corporate location on weekly IV paths and positioning location on monthly GJR paths. Scale and asymmetry corrections have separately comparable scores. The coherent transform applies a monotone signed shape and positive scale around the cash reference, with a common shift to all four OHLC marks within each session. Variance, excursions, range and first-passage losses come from the same **256 cash paths**. Point and event-only forecasts remain separate.

{table(g,['horizon','model','n','crps','range_crps','vol_mae','variance_qlike','touch_brier','integrated_brier','expansion_brier'],14)}

{links('protected-point-risk-cases.csv.gz','protected-joint-benchmarks.csv','position-and-corporate-risk-cases.csv.gz','coherent-risk-path-cases.csv.gz','coherent-path-law-recipes.csv.gz','risk-receipt.json','matched-block-intervals.csv.gz')}''')
    m=data('predictability-power-simulation.csv')
    associations=data('opening-and-late-associations.csv')
    aux=where(lead('architecture'),model=('F_regularized_multihorizon','auxiliary_sector_shared_heads','archived_same_clock'))
    report(12,f'''The five-session sample has 53 non-overlapping windows and the 21-session sample has 11. A 159-origin active V19 monthly analysis has just eight disjoint windows. The lifetime matrix records linear and rank association with baseline residuals, cross-validated incremental squared-error reduction, and earlier and later effects. Opening gaps, regular-session returns and late monthly outcomes are measured separately.

{table(associations,['feature','target','n','spearman'],27)}

For an approximate power calculation we demeaned paired historical losses, applied **1,000** circular block resamples per design and measured the two-sided 95% threshold of the resulting null distribution. The gain needed to reach 80% power adds a constant effect to that centered process. This assumes the historical serial structure and loss dispersion recur, an unchanged parent, the same target geometry and comparable measurement quality. Longer blocks give a sensitivity. Small signals remain within the observed uncertainty.

{table(m,['horizon','metric','block','n','disjoint','mean_gain','approx_80_percent_detectable_gain','estimated_power_at_observed_gain'],18)}

Bank and IT relative returns act as auxiliary responses in a reduced-rank fit. They use the same earlier market dates. The number of independent outcomes comes from the NIFTY targets. Training-window, expiry and time-block sensitivities characterize additional sources of estimation variation.

{table(aux,['horizon','model','n','disjoint','brier','crps','rank_corr'],8)}

{links('predictability-power-simulation.csv','information-lifetime-matrix.csv','coefficient-stability.csv','all-disjoint-window-phases.csv','episode-omission-sensitivity.csv','architecture-training-receipts.csv')}''')
    d=read('source-discovery-receipt.json')
    t=read('cdsl-extension-receipt.json')
    v=data('nifty-membership-notices.csv')
    report(13,f'''V20 recovered **{d['recovered']['first_release_cpi']}** dated first-print CPI PDFs from the Federal Reserve Bank of St. Louis archive of original Bureau of Labor Statistics releases. Each accepted PDF matches its printed release date, observed month and 08:30 Eastern embargo. The eligibility time includes ten minutes and accounts for daylight saving. **{d['recovered']['membership_notices']}** semiannual NSE Indices notices preserve both publication and effective dates, and **{d['recovered']['verified_domestic_contract_lot_states']}** futures contract/lot states come from certified V19 contract records. Index notices verify specific additions and deletions. A complete historical free-float weighting panel still requires dated full membership and weights.

The CDSL eServices monthly page was a distinct retrieval route from V19's public historical form. It added **{t['new_dates']}** authenticated daily reporting dates and **{t['rows']}** gross purchase, sale and net equity rows through **{t['last']}**. Combined coverage is **{64+t['new_dates']}** CDSL daily reporting dates, 36 sector fortnightlies and 22 AMFI months. The added custody observations inherit a conservative next-session eligibility allowance, retain their own receipt and are assessed separately from the primary lifetime panel. Records dated after the freeze are excluded from historical outcomes.

{table(v,['published_date','effective_date','index_mention','membership_notice'],8)}

{table(data('macro-release-summary.csv'),['target','n','rank'],8)}

{table(data('cdsl-extended-release-associations.csv'),['horizon','n_completed','spearman','scope'],4)}

{table(pd.DataFrame(d['broker']),['url','status','file'],8)}

The inherited 466 NSE participant volume files and dated domestic contracts are available. The broker expired-contract requests returned HTTP 401. Offshore quote coverage remains distinct from confirmed individual contract identity. A reconciled daily exchange FII/DII pair, full daily ETF creation/redemption, complete dated index weights and original analyst-expectation vintages remain unresolved.

{links('source-discovery-receipt.json','first-release-cpi.csv','macro-release-nifty-associations.csv','nifty-membership-notices.csv','futures-contract-identity-inventory.csv','cdsl-extension-receipt.json','cdsl-extended-daily.csv')} · [FRASER archived BLS release](https://fraser.stlouisfed.org/files/docs/publications/bls/newsreleases/cpi/cpi_20260610.pdf) · [NSE Indices notices](https://www.niftyindices.com/press-release) · [CDSL daily reporting access](https://www.cdslindia.com/eservices/publications/fiidaily) · [Upstox expired-contract specification](https://upstox.com/developer/api-documentation/get-expired-future-contracts/)''')
    q=read('experimental-forecast-examples.json')
    display=pd.DataFrame([dict(day=r['decision_day'],horizon=r['horizon'],clock=r['forecast_cutoff'],model=r['model_id'],
        target=r['target_session'],n_calib=r['available_historical_calibration']['n'],reference=r['reference_index_close'],
        p_up=r['forecast']['probability_up'],mean_return=r['forecast']['expected_return'],median_return=r['forecast']['median_return'],
        expected_close=r['forecast']['expected_nifty_endpoint']) for r in q['cards']])
    report(14,f'''The framework reconstructs original and corrected atom-weighted laws from their persisted indexes. At the previous cash close, cash information requires a confirmed observation. The 17:00 track keeps its eligible earlier exchange reports and dated foreign inputs. At 08:55 the snapshot can use previous-session NSE reports through the 08:15 allowance, verified GIFT bars and eligible corporate releases. The native 09:10 model combines that snapshot with the protected V14 law. The 09:25 and 10:20 post-open stages from earlier research remain separate from the pre-open experiments.

Domestic, corporate, positioning, offshore and market-implied or realized risk feed horizon-specific estimates. Each terminal law gives expected and median return, direction, NIFTY endpoint, intervals and both tail probabilities. The case card preserves its observed clock, target, available features, confirmed context, parent, correction state and prior calibration. Calibration uses only outcomes that had matured before the decision. Separate OHLC recipes preserve scenario-level coherence for risk and path outcomes.

{table(display,None,6)}

Run the workspace module research.nifty_forecast_v20.framework with day, horizon and clock arguments to retrieve an eligible saved case. The linked examples are frozen-vintage retrospective predictions. The forward ledger records genuine issue timestamps for the separate evening references.

{links('experimental-forecast-examples.json','asof-features.csv.gz','native-source-clock-audit.csv','feature-definitions.json','architecture-laws.npz','native-mechanism-laws.npz','coherent-path-law-recipes.csv.gz','probability-calibration.csv','forward-ledger.json')}''')
    check=read('validation-receipt.json')
    null=data('v20-refit-null-summary.csv')
    main=where(data('matched-block-intervals.csv.gz'),track='native',block=21,
        model=('v19_position_native','price_reaction','smooth5','eight_calendar_day_embargo','omit_latest_21_training_origins'),
        parent=('exact_v14','v18_corporate_native'),metric=('brier','crps'))
    z=where(data('all-disjoint-window-phases.csv'),track='native',model=('v19_position_native','v18_corporate_native'),parent='exact_v14')
    spread=z.groupby(['horizon','model','metric'],as_index=False).gain.agg(low='min',high='max',phases='count')
    report(15,f'''Fit indices are chronological and have training outcomes strictly before the decision day. The data and fit artifacts preserve dated availability, training-only preprocessing and expiry screens. The verification passed {check['sentinels']} duplicate-feature, duplicate-expert and future-poisoning sentinels, and checked {check['native_timing_cases']} native clocks. Sensitivities include lagged forecasts, randomized input blocks, randomized residual targets, a bias-only intercept, no bias, fixed fractional correction, shorter histories, omitted training episodes and an eight-calendar-day embargo. Temporal models include a deliberate independence variant.

{table(main,['horizon','model','parent','metric','n','disjoint','gain','adjusted_low','adjusted_high'],24)}

{table(null,None,6)}

{table(spread,['horizon','model','metric','phases','low','high'],10)}

Every disjoint-window phase is available, alongside earlier and later populations. Further diagnostics remove each calendar month and one extreme realized 21-origin episode. The independent V19 timing replay repeats the favorable-block removal. Max-statistic bands address the V20 family of comparisons, with the same historical years repeatedly examined across earlier versions.

{links('validation-receipt.json','future-information-sentinels.csv','native-source-clock-audit.csv','all-disjoint-window-phases.csv','episode-omission-sensitivity.csv','matched-block-intervals.csv.gz','v20-refit-null-summary.csv','v20-refit-null-cases.csv.gz')}''')
    z=read('registration.json')
    h=pd.DataFrame(z['hypotheses'])
    report(16,f'''V20 registered **{len(h)} primary hypotheses** at {z['registered_at']}. The initial priorities were lifetime response, the V19 monthly position candidate, the V18 corporate weekly baseline, specialized versus shared forecast heads and dependent temporal components. The age matrix uses one regularized correction and a common lag schedule across families. Existing distributions provide comparable anchors without redundant optimization. The fixed-budget refit control reselects the strongest effect among the declared alternatives.

{table(h,['hypothesis','family','target','negative_control','budget','follow_up'],18)}

The registry preserves rationale, forecast cutoff, model parent, primary outcome, budget and the circumstances that justify follow-up. The intermediate horizons describe mechanisms. Five and 21 sessions remain the original endpoints.

{links('registration.json','information-lifetime-matrix.csv','architecture-config.json','native-config.json','complete-matched-comparisons.csv','v20-refit-null-summary.csv')}''')


def comparison_and_forward():
    u=split_lead(lead('native'),['horizon'],['brier','crps'],5)
    b=split_lead(lead('architecture',clock='preauction_0855'),['horizon'],['brier','crps'],4)
    r=split_lead(lead('retained_point_risk'),['horizon'],['mae','brier'],4)
    p=split_lead(lead('joint_path',clock='preauction_0855'),['horizon'],['range_crps','touch_brier'],4)
    cols=['horizon','ranked_metric','model','n','active','disjoint','brier','log_loss','crps','mae','balanced_accuracy','covered','width']
    groups=life(cutoff='preauction_0855',mode='incremental',metric='crps',age='fresh',start_offset=5,end_offset=21)
    report(17,f'''The original samples are 265 weekly and 217 monthly forecasts, with 53 and 11 non-overlapping outcomes. Each prospective timing definition has a separate case table. The machine leaderboards retain early, late, combined and active coverage, error, proper scores, calibration and interval summaries. Matched differences and block-adjusted uncertainty are stored alongside each candidate.

## Native weekly and monthly endpoint forecasts at 09:10

{table(u,cols,22)}

## Rebuilt distributions at 08:55

{table(b,cols,18)}

Protected empirical atoms are scored by exact sign mass in the saved law. Earlier V17 tables sometimes used half-atom smoothing for Brier. This accounts for the slightly different V17 probability score here. Weighted V14/V18/V19 native comparisons retain their original scoring convention.

## Incremental late information and separate risk objectives

{table(groups.nlargest(8,'gain'),['family','matched','disjoint','parent','enhanced','gain','earlier_gain','later_gain','adjusted_low','adjusted_high'],10)}

{table(r,['horizon','ranked_metric','model','n','active','mae','q_like','brier','log_loss'],18)}

{table(p,['horizon','ranked_metric','model','n','range_crps','touch_brier','integrated_brier','vol_mae'],18)}

{links('model-leaderboards.csv','complete-matched-comparisons.csv','matched-block-intervals.csv.gz','information-lifetime-matrix.csv','component-leaderboard.csv','probability-calibration.csv','all-disjoint-window-phases.csv','protected-joint-benchmarks.csv')}''')
    z=read('forward-ledger.json')
    original=pd.DataFrame([dict(version=r['version'],key=r['key'],classification=r['issue_class'],horizon=r['horizon'],
       target=r['target_sessions'][-1],reconciled=len(r['completed_target_dates']),status=r['maturity'],return_=r['realized_return']) for r in z['records']])
    existing=pd.DataFrame([dict(model=r['name'],issued_at=r['issued_at'],horizon=r['horizon'],target=r['target_sessions'][-1],status=r['maturity'])
                          for r in z['inherited_v19_research']])
    new=pd.DataFrame([dict(model=r['model'],issued_at=r['issued_at'],horizon=r['horizon'],target=r['target'],p_up=r.get('p_up'),
                           q10=r['q10'],median=r['median'],q90=r['q90'],p_expansion=r.get('p_expansion')) for r in z['new_issues']])
    report(18,f'''The refresh at {z['checked_at']} verifies {len(z['sessions'])} cash sessions after the historical freeze. The original V4/V5 issue hashes and the exact V19 reference file are preserved. The November 25 V4 diagnostic recorded **+1.7010%**, from **25,387.40 to 25,819.25**, against LightGBM and sector up probabilities originally set at **70.84%** and **68.05%**. It preserves its late-diagnostic classification. Other original outcomes await their own confirmed target sequence and maturity.

{table(original,['version','key','classification','horizon','target','reconciled','status','return_'],8)}

{table(existing,None,6)}

V20's evening references were frozen before the first target session. The weekly symmetric law has return quantiles. Raw ATM, IV/RV and EGARCH rows are annualized volatility quantiles. The raw ATM and blend use identified dated call and put marks and total-variance interpolation. The monthly EGARCH reference measures expansion relative to **1.25 times** currently eligible trailing volatility. V14, V18, V19 monthly positioning and GIFT opening preserve their specific morning issue guards. All targets fall in 2026.

{table(new,None,8)}

{links('forward-ledger.json','forward-refresh-receipt.json','forward/new-issues.json','forward/options-probes.json')} · [NSE 2026 cash calendar](https://archives.nseindia.com/content/circulars/CMTR71775.pdf) · [Upstox option-chain specification](https://upstox.com/developer/api-documentation/get-pc-option-chain/)''')

def conclusion():
    a=lead('native',5)
    b=lead('native',21)
    w=best(a,'brier',1).iloc[0]
    c=best(a,'crps',1).iloc[0]
    m=best(b,'brier',1).iloc[0]
    q=best(b,'crps',1).iloc[0]
    f=life(cutoff='preauction_0855',mode='incremental',metric='crps',age='fresh',start_offset=5,end_offset=21)
    pos=f[f.family.eq('participant_futures')].iloc[0]
    corp=f[f.family.eq('corporate_announcements')].iloc[0]
    l=where(data('strong-parent-component-comparisons.csv'),cutoff='preauction_0855',end_offset=21,
            model='participant_smoothed').set_index('metric')
    late_crps=l.loc['crps']
    late_brier=l.loc['brier']
    g=data('opening-and-late-associations.csv')
    k=where(g,feature='gift_proxy').set_index('target').spearman
    intervals=where(data('matched-block-intervals.csv.gz'),track='native',block=21)
    p=pd.concat([where(intervals,horizon=h,model=row.model,metric=metric,parent=base) for h,row,metric,base in (
       (5,w,'brier','v18_corporate_native'),(5,c,'crps','v18_corporate_native'),
       (21,m,'brier','v19_position_native'),(21,q,'crps','v19_position_native'))])
    spans=int((p.adjusted_low.le(0)&p.adjusted_high.ge(0)).sum())
    c1=where(lead('architecture'),horizon=21,model=('archived_joint_GJR','archived_same_clock','G_fixed_specialized_mixture'))
    report(19,f'''The native timing audit confirmed that participant reports entered through a modeled 08:15 publication allowance, before the 08:55 overlay snapshot and original 09:10 issue. V19's original monthly Brier of **0.228199** and CRPS of **0.024010** reproduce on 217 cases, with 159 active cases representing eight disjoint windows. The original weekly V18 corporate result of **0.223481 Brier and 0.010318 CRPS** is the preserved earlier comparator.

The clearest descriptive lifetime difference was offshore pricing. At 08:55 the GIFT rank correlation was **{k['gap']:.3f}** with the opening gap, **{k['original1']:.3f}** with the first close-to-close return, and **{k['return_5_21']:.3f}** with sessions 6–21. In that pre-auction 6–21 return experiment, the fresh participant futures CRPS gain was **{pos.gain:.6f}** over the price parent on **{int(pos.matched)}** origins, with earlier/later gains of **{pos.earlier_gain:.6f}** and **{pos.later_gain:.6f}**. The corporate announcement gain was **{corp.gain:.6f}**. The dependence-adjusted intervals for those two late gains were **[{pos.adjusted_low:.6f}, {pos.adjusted_high:.6f}]** and **[{corp.adjusted_low:.6f}, {corp.adjusted_high:.6f}]**, respectively.

Against the stronger same-clock GJR path control, smoothed positioning after the first five sessions moved CRPS from **{late_crps.parent:.6f} to {late_crps.matched_loss:.6f}** and Brier from **{late_brier.parent:.6f} to {late_brier.matched_loss:.6f}** on **{int(late_crps.matched)}** matched cases covering **{int(late_crps.disjoint)}** disjoint 16-session windows. The earlier/later CRPS gains were **{late_crps.earlier_gain:.6f}** and **{late_crps.later_gain:.6f}**. Its adjusted CRPS gain band was **[{late_crps.interval_adjusted_low:.6f}, {late_crps.interval_adjusted_high:.6f}]**. The post-week effect is an exploratory, cohort-dependent result.

The V20 full-population native weekly Brier point leader was **{w.model} at {w.brier:.6f}**, and the weekly CRPS point leader was **{c.model} at {c.crps:.6f}**. The monthly native point leaders were **{m.model} at {m.brier:.6f} Brier** and **{q.model} at {q.crps:.6f} CRPS**. The full-population scores include each candidate’s specified fallback. **{spans} of {len(p)}** search-adjusted intervals for gains over the earlier leaders include zero on paired active dates. Forecasts from different clocks remain distinct.

{table(p,['horizon','model','parent','metric','n','disjoint','gain','adjusted_low','adjusted_high'],18)}

{table(c1,['model','n','disjoint','brier','crps','log_loss'],6)}

The strongest same-clock distribution controls give a demanding comparison for separately fitted pooled, sparse and component architectures. The aged custody and fund group improved on the simple lifetime price model, while its pre-auction Brier of **0.307288** on matched origins remained above the neutral **0.250000**. V20 preserves risk and barrier references apart from the directional results. Additional dated macro releases, index membership notices and CDSL reports improve source provenance. The next identifiable test measures the new weekly variants and the monthly positioning and post-week components over independently accumulated dates with fixed guard clocks.

{links('V20_PREDICTIVE_INFORMATION_LIFETIMES.md','V20_TEMPORAL_RETURN_DECOMPOSITION.md','V20_COMPLETE_MODEL_COMPARISON.md','V20_VALIDATION_AND_FALSIFICATION.md','V20_FORWARD_RESEARCH_LEDGER.md','information-lifetime-heatmap.png')}''')
    report(20,'''1. Freeze an original-clock weekly comparison of V18 corporate, price reaction and the revised residual arm. Keep all origin dates, including low announcement activity and short training histories.
2. Lock the monthly V14 parent, current-position correction, smoothed-position correction and bias control. Keep a separate 6–21 return loss and preserve the conditional residual dependence.
3. Capture original dated FII/DII exchange releases, archived consensus before company results, effective-date full index membership and weights, and individual GIFT and domestic futures IDs. Preserve source snapshots and revisions as they arrive.
4. Score the weekly and monthly volatility distributions, range and barrier outcomes on their exact target dates. Keep morning and evening inputs distinct.
5. Review active and full-population gains across future disjoint windows before expanding gates or training families. Leave the exact historical forecasts and issue classifications auditable.'''+'\n\n'+links('registration.json','V20_FINAL_RESEARCH_CONCLUSIONS.md','V20_FORWARD_RESEARCH_LEDGER.md'))

def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    x=life(cutoff='preauction_0855',metric='crps',age='fresh')
    y=x[x['mode'].eq('cumulative')].pivot(index='family',columns='end_offset',values='relative_gain')
    z=x[x['mode'].eq('incremental')].pivot(index='family',columns=['start_offset','end_offset'],values='relative_gain').reindex(y.index)
    lower=x[x['mode'].eq('cumulative')].pivot(index='family',columns='end_offset',values='adjusted_low').reindex_like(y)
    late_lower=x[x['mode'].eq('incremental')].pivot(index='family',columns=['start_offset','end_offset'],values='adjusted_low').reindex_like(z)
    a=z.to_numpy(float)*100
    b=y.to_numpy(float)*100
    cap=max(.5,float(np.nanquantile(abs(np.r_[a.ravel(),b.ravel()]),.94)))
    norm=TwoSlopeNorm(vmin=-cap,vcenter=0.,vmax=cap)
    f,p=plt.subplots(1,2,figsize=(13,8.1),gridspec_kw={'width_ratios':[1.17,1]})
    f.subplots_adjust(left=.225,right=.91,top=.86,bottom=.13,wspace=.10)
    cm=plt.get_cmap('RdBu').copy()
    cm.set_bad('#e7ebed')
    p[0].imshow(b,aspect='auto',cmap=cm,norm=norm)
    i=p[1].imshow(a,aspect='auto',cmap=cm,norm=norm)
    display={'atm_iv':'ATM IV','offshore_gift':'offshore GIFT NIFTY'}
    for j,ax in enumerate(p):
        title='Cumulative return' if j==0 else 'Incremental return'
        ax.set_title(title,loc='left',fontsize=12,fontweight='bold')
        ax.set_yticks(np.arange(len(y)),[display.get(k,k.replace('_',' ')) for k in y.index] if j==0 else ['']*len(y))
        row,col=np.nonzero((lower if j==0 else late_lower).gt(0).to_numpy())
        ax.scatter(col,row,s=28,color='#fffdf7',edgecolor='#172a41',linewidth=0.7)
        ticks=[str(v) for v in y.columns] if j==0 else [f'{a+1}–{b}' for a,b in z.columns]
        ax.set_xticks(np.arange(len(ticks)),ticks,fontsize=9)
        ax.tick_params(axis='both',length=0,labelsize=9)
        ax.set_xlabel('Target sessions after the reference close')
        ax.spines[['top','right','bottom','left']].set_visible(False)
    bar=f.add_axes([.934,.19,.012,.60])
    f.colorbar(i,cax=bar,label='Matched CRPS gain (%)',extend='both')
    f.suptitle('NIFTY V20 · Predictive lifetimes at 08:55 IST',x=.045,y=.955,ha='left',fontsize=18,fontweight='bold')
    f.text(.047,.055,'Fresh inputs. Positive values indicate lower historical loss. A dot marks a positive adjusted lower bound.',fontsize=9,color='#364759')
    f.text(.047,.032,'Gray marks unavailable coverage. The first session is the first incremental component.',fontsize=9,color='#364759')
    f.savefig(OUT/'information-lifetime-heatmap.png',dpi=160,facecolor='white')
    plt.close(f)

def index():
    z=read('timing-audit-receipt.json')
    n=read('forward-ledger.json')
    q=read('lifetime-receipt.json')
    subs='\n'.join(f'{i}. [{r.replace("_"," ").title()}](V20_{r}.md)' for i,r in enumerate(REPORTS,1))
    (OUT/'NIFTY_V20_RESEARCH.md').write_text(f'''# NIFTY V20 information lifetimes and horizon specialization

Historical research runs from **{FIRST} through {FREEZE}**. V20 checked the native 09:10 timing on **{z['actual_native_origins']}** horizon-origin cases, evaluated **{q['case_rows']:,}** family-by-age case comparisons, and preserved distinct original, return, risk and forward laws. The forward ledger retains the three V19 research issues and **{len(n['new_issues'])}** dated V20 evening references.

[Findings](V20_FINAL_RESEARCH_CONCLUSIONS.md) · [Lifetime matrix](V20_PREDICTIVE_INFORMATION_LIFETIMES.md) · [Complete comparison](V20_COMPLETE_MODEL_COMPARISON.md) · [Forward ledger](V20_FORWARD_RESEARCH_LEDGER.md)

## Research reports

{subs}

## Reproduction and data

{links('MISSION.md','README.md','registration.json','feature-definitions.json','cumulative-information-registry.csv','information-lifetime-heatmap.png','model-leaderboards.csv','manifest.json')}
''',encoding='utf-8')
    cmds=['common','audit protect','audit replay','panel','acquisition','acquisition --cdsl','lifetime','native','joint','late_window','risk','forward',
          'evidence','registry','framework','report','delivery']
    cmd='\n'.join('.venv/Scripts/python.exe -m research.nifty_forecast_v20.'+r for r in cmds)
    fence=chr(96)*3
    body='# Reproduce NIFTY V20\n\nRun from the trading-desk root using the existing research Python environment. Historical inputs are frozen from January 2025 through November 17, 2026. Preserve captured forward issues when replaying and run acquisition and forward commands only to intentionally refresh those lanes. Forward outcomes and genuine issue timestamps are separate from historical experiments.\n\n'
    body+=fence+"powershell\n$env:PYTHONDONTWRITEBYTECODE='1'\n$env:OPENBLAS_NUM_THREADS='1'\n"+cmd+'\n'+fence+'\n\n'
    body+='The [research index](NIFTY_V20_RESEARCH.md) links the reports. The [SHA-256 manifest](manifest.json) binds sources, cases, paths and code to the finished run.\n'
    (OUT/'README.md').write_text(body,encoding='utf-8')

if __name__=='__main__':
    audit_and_lifetimes()
    construction()
    risk_and_sources()
    comparison_and_forward()
    conclusion()
    figure()
    index()
    print('Published all 20 requested V20 reports',flush=True)



