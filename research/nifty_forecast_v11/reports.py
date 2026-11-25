"""Generate all fifteen requested V11 research reports."""
from .common import *

TITLES=['REPRODUCTION_AND_BASELINES','OFFICIAL_BREADTH_RESEARCH','MARKET_CONCENTRATION_AND_LEADERSHIP',
 'INTELLIGENT_TRAINING_MEMORY','PERSISTENT_MARKET_RELATIONSHIPS','OVERLAP_AND_TRAINING_DIVERSITY',
 'STRUCTURAL_ENSEMBLE_RESEARCH','DISTRIBUTIONAL_LEARNING','ADDITIONAL_MARKET_INTELLIGENCE',
 'MONTHLY_FORECASTING_RESEARCH','COMPLETE_MODEL_COMPARISON','VALIDATION_AND_SEARCH_AUDIT',
 'SIGNAL_DISCOVERIES','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS']
LOSS=['model','n','disjoint','brier','crps','log_loss','accuracy','balanced_accuracy','mae','median_mae','pinball','coverage50','coverage80','width80','ECE']
PAIR=['horizon','cohort','model','baseline','metric','n','candidate','control','gain','low10','high10']


def csv(n):return pd.read_csv(OUT/f'{n}.csv')


def fmt(x):
    if pd.isna(x):return '—'
    return f'{x:.6f}' if isinstance(x,(float,np.floating)) else str(x).replace('|','\\|')


def table(a,cols=None):
    if a.empty:return '_No eligible comparison._'
    if cols is not None:a=a.reindex(columns=cols)
    rows=[a.columns,['---']*len(a.columns),*a.itertuples(index=False,name=None)]
    return '\n'.join('| '+' | '.join(fmt(x) for x in r)+' |' for r in rows)


def emit(i,s):
    k=TITLES[i-1]
    (OUT/f'V11_{k}.md').write_text('# V11 '+k.replace('_',' ').title()+'\n\n'+s.strip()+'\n',encoding='utf-8')


def run():
    scores=csv('leaderboard');p=csv('matched-comparisons');inc=p[p.is_parent]
    dates=csv('training-support-by-fold');registry=read('registry.json');v=read('verification.json');src=read('official-source-audit.json')
    previous=read('protected-hash-verification.json');us=read('global-breadth-audit.json');refresh=read('refresh-summary.json')
    r=read('v10-replay.json');boot=read('comparison-uncertainty.json')
    reasons=pd.DataFrame([x for x in registry['attempts'] if x['status']!='ok']).groupby(['batch','reason']).size().reset_index(name='unestimated')
    references=['P_HIST','P_CLUSTER','P_ROT','P_STRUCTURE','J9_STATIC','J9_REL_SHRINK','J10_STRUCTURAL_BLEND',
       'J10_HISTORY_SHRINK','NEUTRAL','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO']
    legacy=['V8_R_RESIDUAL_EQ','V8_W_STRUCT_EMBARGO_EQ','V8_A_STRUCTURE_CHANGE_EQ','P_ROT_EQ','P_STRUCTURE_EQ','P_CLUSTER_EQ']
    bcols=['B_NATIVE_EQ','B_ROT_EQ','B_TEN_EQ','B_SPARSE_EQ','B_STUD_EQ','B_EQ_SIZE_RISK','B_EQ_MOMO_DROP','B_FIN_INTERACT','B_PAIR100','B_STYLE',
       'B_EQ_LAG5','B_EQ_SHIFT21','B_EQ_SHIFT42','B_EQ_PERM','B_EQUAL_ONLY','B_CAP_ONLY','B_CHANGE','B_PERSIST']
    memory=['M_RECENT_85','M_SPREAD_85','M_EARLIEST_85','M_DIVERSE_85','M_RANDOM_BLOCKS_85','M_USEFULNESS_85','M_BALANCE_VOL_85',
       'M_BALANCE_ROTATION_85','M_OMIT_RECENT1','M_OMIT_RECENT2','M_OMIT_RECENT3','M_OMIT_SPREAD1','M_OMIT_SPREAD2','M_OMIT_SPREAD3']
    persist=['B_ROT','P_SHORT','P_RECENT_SHRINK','P_RECENT_FREE','P_LONG_SHORT','P_BLOCK_EXPERTS','P_HIER','P_BREADTH_PERSIST']
    overlap=[k for k in registry['configurations'] if k.startswith(('O_NATIVE','O_COMPACT','O_ROT','O85_'))]
    addon=['I_CAP_PARENT','I_EQ','I_DIVERGE','I_RISK_PARENT','I_RISK_EQ','D_DERIV_RISK','D_INTRA','D_INTRA_TIMING','D_GLOBAL_RISK','D_ETF']
    laws=[n for n in registry['configurations'] if n.startswith(('D_ROT_','D_EQ_','D_NATIVE_'))]

    def rows(h=5,c='combined',only=None):
        a=scores[scores.horizon.eq(h)&scores.cohort.eq(c)]
        return a if only is None else a[a.model.isin(only)]

    def value(n,k,h=5,c='combined'):
        a=rows(h,c,[n]);return fmt(a[k].iloc[0]) if len(a) else '—'

    def panel(names,h=5):
        a=scores[scores.model.isin(names)&scores.horizon.eq(h)].pivot(index='model',columns='cohort',values=['brier','crps'])
        a.columns=[f'{c} {m}' for m,c in a.columns]
        return table(a.reset_index().sort_values('combined brier'),['model','early brier','later brier','combined brier','early crps','later crps','combined crps'])

    def compare(names,h=None,scopes=('early','later','combined'),metrics=('brier','crps')):
        a=inc[inc.model.isin(names)&inc.cohort.isin(scopes)&inc.metric.isin(metrics)]
        if h:a=a[a.horizon.eq(h)]
        return table(a.sort_values(['horizon','model','cohort','metric']),PAIR)

    emit(1,f"""
V11 used the November 17 frozen vintage and archived query and maturity dates. It freshly reproduced **{v['legacy_v10_refits']:,}** V10 model and transfer forecasts and **{v['legacy_v10_mixtures']}** mixture forecasts using their exact expert laws and weights. The largest V10 fit-score discrepancy was **{max(g['max_delta'] for g in r['checks']):.3g}**. Included are official breadth, oldest/latest/spread, phase and GLS, block averaging, Student-t, sign and magnitude, transfer with randomized and displaced controls, neutral monthly, and dated futures/straddle. The prior-reference replay also verifies 1,612 V9 and 184 V8 forecasts and recreates 125 required duplicate invariance cases.

{panel(references)}

The previously reported V9 weekly training-length Brier sequence is 0.355902, 0.213222, 0.226963, 0.210085, 0.176506 and 0.165232 at 85, 126, 189, 252, 300 and expanding, respectively. V10's compact later weekly comparison was 0.376831 recent, 0.243061 spread and 0.242128 earliest at 85. V8's 0.159504 Brier and 0.009453 CRPS values belong to their original models, dates and cohorts.

[V10 exact replay](v10-replay.json) · [V9 and V8 replay](replay/older/reproduction.json) · [Duplicate replay](replay/invariance/invariance-effects.csv).
""")
    emit(2,f"""
V11 parsed **{src['archives']}** official NSE daily files containing **{src['distinct_indices']}** distinct index labels. The inventory covers equal-weight, cap-weight, broad, sector, quality, momentum, value, dividend, low-volatility and thematic families. It admits 22 documented close series and inventories the others outside the fitted panel. Launch or dated publication evidence supports admissibility. The two V10 equal-weight pairs match the frozen prices exactly. NIFTY 100 Equal Weight and Top 15 provide alternative documented breadth and leadership proxies. Top 10, NIFTY500 Quality 50 and NIFTY500 Low Volatility 50 carry a conservative July 2025 floor. Archive values enter the main experiments with a one-observed-session lag. An independent same-close diagnostic and documented launch windows reduce false backfill assumptions. Exact historical distribution timestamps and later data corrections remain unverified. [NSE index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf) · [NIFTY500 Equal Weight launch](https://www.niftyindices.com/Press_Release/ind_prs31052024.pdf) · [Top 15 launch](https://www.niftyindices.com/Factsheet/Factsheet_NiftyTop15EqualWeight.pdf) · [2025 benchmark publications](https://www.niftyindices.com/Nifty_Passive_Insights/Nifty%20Passive%20Insights%20Quarterly%20Update%20-%20April%2025%20to%20June%2025.pdf).

Five- and 21-session changes in official log-price relatives define the core breadth measures. We compare individual equal-weight and cap-weight returns, a separate NIFTY100 pair, breadth acceleration and persistence, interaction with bank rotation and prior risk, five-session lag, circular shifts of 21 or 42 dates, and block permutations. Explicit momentum removal and training-only residualization control common momentum, size and relative volatility. Index composition and rebalancing can still affect the spreads. Exact V8 and V9 augmentations retain their actual fit partitions and implementation. Weekly improvements in V9 residual rotation and structure coexist with weaker Brier in the cluster-balanced parent. Width, magnitude error, and calibrated probability are separate outcomes.

The combined weekly conditional slices did not show a simple continuation rule. The 140 origins with a positive broad-market spread had a 37.86% subsequent positive rate and −0.349% mean weekly return. The 125 remaining origins had a 51.20% positive rate and +0.385% mean return. The 50 narrow-rise cases had a 44.00% positive rate and +0.054% mean return. The 67 broad-rise cases had a 38.81% positive rate and +0.014% mean return. These descriptive groups overlap in time and have different volatility and sector states.

{compare(legacy+bcols,5,('early','later'))}

[Archive coverage](official-index-inventory.csv) · [Sources and eligibility](official-source-audit.json) · [Narrow vs broad and high/low risk results](breadth-mechanism-slices.csv) · [Matched legacy fit replay](legacy-ledger.json).
""")
    emit(3,f"""
NIFTY Top 15 Equal Weight versus NIFTY 50 Equal Weight, NIFTY 50 versus NIFTY 500, sector return dispersion, sector rank changes, squared shares of absolute sector returns, and bank-relative moves are concentration or leadership proxies. They capture different features of a market that may be driven by a few large names. The compact seven-state design uses breadth, concentration, financial leadership, defensive/cyclical rotation, volatility, liquidity and global relative strength. Compare levels, five-day changes, persistent states, and the no-financial feature ablation.

{panel(['B_ROT','B_ROT_EQ','L_CONC','L_EQ_CONC','L_BASIC','L_CHANGE','L_PERSIST','L_NO_FIN','B_FIN_INTERACT'])}

Daily dated memberships and weights needed for actual constituent contribution remained unavailable. The index spread does not directly measure advancing stocks. The exact duplicate/affine alias check operates on the strong rotation and breadth representation across both horizons. [NSE constituent-data description](https://www.niftyindices.com/offerings/data-subscription) · [Conditional leadership slices](breadth-mechanism-slices.csv) · [Concentration matched results](incremental-comparisons.csv).
""")
    med=dates[dates.model.isin(memory)&dates.cohort.eq('later')].groupby(['horizon','model'])[['training','distinct_return_sessions','disjoint_training_windows','kish_ESS','overlap_effective_count']].median().reset_index()
    emit(4,f"""
V10's oldest 85 had almost the same Brier as the spread 85 while using about 17.326 overlap-adjusted effective observations versus 62.392. V11 tests the same idea using a stronger rotation family and budgets **85, 126, 189, 252, 300 and expanding**, with exact date eligibility for every contest. Recent, earliest, even-spread, neighboring blocks, random blocks, balanced risk/rotation and diverse volatility/trend/bank episodes hold nominal rows fixed where possible. Random blocks and removing one to three likely influential recent months serve as sensitivity controls. Larger budgets skip folds with insufficient mature observations. The distinct return-session and information counts cannot generally both match when comparing spread against contiguous rows.

The new adaptive selector retains half the dates across history and fills remaining places using previously matured monthly loss results with a 12-observation shrinkage prior and rotation across months. This estimates prior forecasting conditions for a historical block. The bookkeeping does not identify the causal effect of training on that block. The initialized methods and their exact date lists remain available.

On the full weekly chronology, spread 85 reduced Brier from **{value('M_RECENT_85','brier')}** to **{value('M_SPREAD_85','brier')}**. The learned selector scored **{value('M_USEFULNESS_85','brier')}**, and random blocks scored **{value('M_RANDOM_BLOCKS_85','brier')}**. Spread improved both cohorts against the recent window, with much more of the improvement late. It scored better than random blocks on combined Brier. Random blocks achieved lower combined CRPS.

{panel(memory)}

## Median later-cohort training information

{table(med)}

[All eligible budget comparisons](memory-exact-budget-comparisons.csv) · [Forecast-date and phase stress](stress-comparisons.csv) · [Perturbed forecasts and selected dates](block-perturbation.csv).
""")
    pert=csv('block-perturbation')
    ps=pert.groupby(['horizon','expert','query'])[['p','mean','width80','q10','brier','crps']].std().groupby(level=[0,1]).median().reset_index()
    co=csv('block-perturbation-coefficients').groupby(['horizon','expert','feature']).coefficient.agg(std_coefficient='std',fraction_positive=lambda z:(z>0).mean()).reset_index()
    write('coefficient-stability.csv',co)
    emit(5,f"""
The long fit is expanding, the unconstrained recent fit uses 85 and the 65/35 estimator combines their locations. The temporary residual fit uses a penalty of 650 and half weight on its recent adjustment. A more flexible hierarchical variation uses a 325 penalty and a centered recent component. The historical-block architecture pools three past episode fits and half the long history, with a separate variant including official breadth persistence. The early and late results show the price of changing the balance between a long relationship and a short adjustment.

{panel(persist)}

{panel(persist,21)}

Ten block perturbations recompute probabilities, expected returns, widths, lower quantiles and score losses on each chosen forecast date. A small 85-row sample and a two-episode long-history diagnostic with 20% block dropout have different sources of dispersion. A complete-law mixture is also scored across these perturbations. Coefficient sign consistency measures descriptive estimation stability.

{table(ps)}

[Coefficient stability](coefficient-stability.csv) · [Original model coefficients](memory-coefficients.csv) · [Perturbation detail](block-perturbation.csv).
""")
    os=dates[dates.model.isin(overlap)&dates.cohort.eq('later')].groupby(['horizon','model'])[['training','nominal_rows','distinct_return_sessions','disjoint_training_windows','overlap_effective_count']].median().reset_index()
    emit(6,f"""
We crossed compact, native and residual-rotation families with block equations, fixed phases zero and two, staggered mixtures, inverse-overlap weights, analytical GLS and regularized empirical GLS. The 85-label sample adds recent versus spread diversity with the same date masks. A separate disjoint screen holds the maximum label budget at 14 and uses a compact six-column design for recent/spread. The original scaler requires 30 finite inputs and the first low-count fallback produced a coefficient shape error. Both attempts remain in the ledger. The corrected fits record selected counts, geometry, and penalties. The phase contrasts use exactly the same scored origins.

{panel(overlap)}

{table(os)}

The native phase-zero configuration reached **{value('O_NATIVE_PHASE0','brier')} Brier** and **{value('O_NATIVE_PHASE0','crps')} CRPS** combined. Staggering and training phase choice re-express overlapping returns from the same observed market history. Compare alternative phases, matched parent gains, and leave-month ranges. [Window support](training-support-by-fold.csv) · [Phase and calendar stress](stress-comparisons.csv).
""")
    ens=rows(5);ens=ens[ens.family.str.startswith('ensemble')].sort_values('brier')
    div=csv('expert-diversity');div=div[div.horizon.eq(5)&div.cohort.eq('combined')].sort_values('error_corr')
    emit(7,f"""
The frozen mixture uses weights 40% base rotation, 30% sparse rotation and 30% volatility Student-t. V10 shrinkage allocates half to this mixture and half to empirical history. The strictly matched V11 breadth version adds official breadth to all three original component designs without changing their weights. Broader equal-weight, memory, historical shrinkage, ETF and derivatives mixtures test different inputs. Leave-one-expert-out fits test marginal value. Doubling the native expert counts its mass twice in a deliberate redundancy control.

The restricted simplex learns Brier- or CRPS-targeted weights using only mature, earlier archived outcomes. It uses at least 20 such outcomes, regularizes toward equal weights, and bounds individual weights from 2.5% to 55%. High-volatility weights draw 70% from the all-regime rule. Every assembled distribution produces its own direction, point, quantiles, buckets and endpoint. Forecast error correlation, shared bad dates and disagreement are more informative than feature-name differences alone.

{table(ens,LOSS)}

{table(div,['expert1','expert2','n','probability_corr','error_corr','crps_corr','classification_disagreement','shared_worst_decile','energy_distance'])}

[Weight fit history](ensemble-ledger.json) · [Leave-one-out and full-law comparisons](incremental-comparisons.csv) · [Risk-conditional calibration](expert-conditional-calibration.csv) · [Exact breadth mixture](ensemble-exact-registry.json).
""")
    tail=csv('training-return-buckets')
    tail=tail[tail.model.isin(['D_ROT_RAW','D_EQ_STUDENT','D_EQ_SIGNMAG','D_EQ_TAIL','D_NATIVE_SIGNMAG'])&tail.cohort.eq('combined')&tail.bucket.isin([0,5])]
    emit(8,f"""
Raw and normalized empirical residual laws, normalized Student-t, sign-conditioned magnitudes, asymmetric scale, 6% historical downside-tail shrinkage and conditional scale are compared on native, rotation and breadth parents. A reduced-rank two-output model combines short and remaining future endpoint components, with paired estimation residuals. Daily future observations are reserved for scoring. The scale head models endpoint absolute return separately from location; its annualized path-volatility prediction has a distinct outcome and metric.

{table(rows(5,only=laws).sort_values('crps'),LOSS)}

{table(rows(21,only=laws).sort_values('crps'),LOSS)}

The six historical buckets use the 10th, 30th, 50th, 70th and 90th training percentiles. Diagnostic lower and upper tails follow. Read sharper intervals together with observed coverage and report both Brier and CRPS.

{table(tail,['horizon','model','bucket','n','expected','actual','brier'])}

[All six calibrated buckets](training-return-buckets.csv) · [Probability bins](calibration-bins.csv).
""")
    emit(9,f"""
Nasdaq archive acquisition gave **{us['common_US_sessions']}** matched dates for RSP, SPY, XLF and XLK. RSP/SPY is a traded equal-weight/cap-weight proxy and XLF/XLK is a US sector control. US data enter only if their session date precedes the Indian origin. Exchange closes can carry corporate-action and tracking effects. Models compare US cap/sector context, genuine ETF weighting spreads, the domestic–US breadth gap and a scale extension. [Nasdaq RSP history](https://www.nasdaq.com/market-activity/etf/rsp/historical) · [Nasdaq SPY history](https://www.nasdaq.com/market-activity/etf/spy/historical).

The official NSE derivatives history includes observed same-contract cash/futures relatives, maturity-normalized curve, true expiry switches, matched OI changes per underlying turnover, and a near-ATM traded straddle premium. It enters separately from location in the derivatives risk model. The premium proxies priced risk. The endpoint forecast law represents realized returns. The four Upstox sector indices contribute **458** synchronized 15-bar sessions with newly derived midday participation, opening follow-through, financial rotation and a closing concentration proxy. Validated eligibility is shared by the corresponding parents. [NSE archives](https://www.nseindia.com/all-reports) · [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).

{compare(addon,None,('combined',),('brier','crps','abs_return_error','path_risk_abs_error'))}

The separate refresh reacquired **{refresh['validated_rows']:,}** records through **{refresh['last_completed']}**, with four post-freeze sessions and **{len(refresh['additional_vs_V10'])}** completed dates beyond V10. The prior dated late-diagnostic issue still had pending endpoints on 25 November and 17 December. [Official NSE trading calendar](https://betanseapi.nseindia.com/resources/exchange-communication-holidays) · [Refresh receipts](refresh-summary.json) · [US source audit](global-breadth-audit.json) · [US alignment](international-availability.csv).
""")
    month=['NEUTRAL','HISTORY','REVERSION','V6_MONTH_STATE','V6_MONTH_LAG1','V8_MS_WINDOW','V8_MS_ROLL','P_CLUSTER','T_VOL_STUDENT','T_SIGNMAG',
           'B_PERSIST','L_PERSIST','M_EARLIEST_85','O_ROT_PHASE1','D_EQ_STUDENT','D_EQ_SHARED','D_DERIV_RISK','I_RISK_EQ',
           'J11_MEMORY','J11_STACK_CRPS','J11_BREADTH_ALL_HIST','B_EQ_SHIFT21','B_EQ_PERM']
    emit(10,f"""
There are 141 earlier and 76 later monthly origins, with 217 combined and only 11 disjoint windows. The earlier state references and later V8 smooth/lag/roll tests retain their historical evaluation slices. The 0.108239 later Brier of the V8 rolled state is a warning about interpreting the 0.132367 later smooth-state number. New tests use persistent breadth, concentration, phase selection, historical memory, normalized volatility, conditional risk and coherent mixtures.

{panel(month,21)}

The symmetric neutral reference scores **{value('NEUTRAL','brier',21)} Brier** and **{value('NEUTRAL','crps',21)} CRPS**. Large scores from isolated phases or heavily overlapping dates warrant a matched check and comparison against shifted cases. Full monthly endpoint results and realized volatility are distinct, and monthly uncertainty is summarized descriptively with disjoint dates and deletion tests. [Monthly phase stress](stress-comparisons.csv) · [Monthly calibration](leaderboard.csv).
""")
    weekly=rows();weekly=weekly[weekly.coverage&~weekly.diagnostic]
    newer=weekly[weekly.family.ne('frozen')]
    topb=newer.sort_values('brier').model.iloc[0];topc=newer.sort_values('crps').model.iloc[0]
    m=rows(21);m=m[m.coverage&~m.diagnostic]
    late=rows(5,'later');late=late[late.coverage&~late.diagnostic]
    s=p[p.model.isin([topb,topc,*legacy,'J11_BREADTH_ALL','J11_BREADTH_ALL_HIST'])&p.horizon.eq(5)&p.cohort.isin(['combined','later'])&
        p.baseline.isin(['P_CLUSTER','J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO'])&p.metric.isin(['brier','crps'])]
    emit(11,f"""
Reference cohorts contain 173 earlier and 92 later weekly origins and 141 earlier and 76 later monthly origins. Combined headline rankings require full coverage. All paired results use identical origin, endpoint and realized return. Candidate rank varies across probability quality, distribution quality, cohort, sample efficiency and calibration. The Pareto tables retain early and late Brier and CRPS, and calibration. The sample-efficiency frontier adds training support and complexity where defined.

## Weekly probability leaders

{table(weekly.sort_values('brier').head(12),LOSS)}

## Weekly distribution leaders

{table(weekly.sort_values('crps').head(12),LOSS)}

## Later weekly leaders

{table(late.sort_values('brier').head(10),LOSS)}

## Monthly full-coverage leaders

{table(m.sort_values('brier').head(10),LOSS)}

## Selected overlapping weekly comparisons

{table(s,PAIR)}

[Full leaderboard](leaderboard.csv) · [Forecast Pareto frontier](pareto.csv) · [Efficiency frontier](pareto-efficiency.csv) · [All comparisons](matched-comparisons.csv).
""")
    null=csv('null-selected');nsummary=[]
    for (h,c,k),z in null.groupby(['horizon','cohort','metric']):
        real=z.loc[z.draw.eq(-1),'best_gain'].iloc[0];nulls=z.loc[z.draw.ge(0),'best_gain']
        nsummary.append({'horizon':h,'cohort':c,'score':k,'selected genuine gain':real,'null median':nulls.median(),
                         'null p95':nulls.quantile(.95),'fraction null at least genuine':(nulls>=real).mean()})
    uncertainty=pd.DataFrame([(k,vv['origins'],vv['contrasts'],vv['critical']['10']) for k,vv in boot['scope'].items()],
                             columns=['scope','origin count','weekly contrasts','block 10 max statistic'])
    emit(12,f"""
V9 inventoried 454 different configuration fingerprints and 583 archived prediction fingerprints. V10 recorded 155 configurations and 266 prediction fingerprints under its schema. V11 evaluated {v['model_configurations']} registered configurations. These counts document different schemas and an adaptive historical search on overlapping market observations. Bootstrap adjustment is bounded to recorded V11 families.

V11 checked **{v['artifact_fits']:,}** chronological fit artifacts, **{v['weight_vectors']:,}** simplex weight vectors, **{v['complete_laws']:,}** archive laws, **{v['invariance_future_sentinel']}** exact-copy and future-data tests, and **{previous['checked']:,}** unchanged protected files. Fit-label maturities strictly precede prediction and inner calibration boundaries. The procedure uses 2,000 shared circular resamples at blocks 5, 10 and 15, with maximized standardized deviations across weekly Brier and CRPS comparisons in each cohort. All timing, training-budget and source masks remain explicit.

{table(uncertainty)}

Six model and selector mechanisms compete under twelve block-permuted training-label draws over three earlier and three later origins at each horizon. Realized holdout returns remain fixed, randomized blocks reselect dates, and the usefulness selector sees randomized earlier eligible merit. This replay is a small falsification family. Weekly conclusions also face lag, state shift, source timing, input removal and date deletion. Monthly uncertainty is described with recorded phase checks.

{table(pd.DataFrame(nsummary))}

## Failed and ineligible folds

{table(reasons)}

[Full verification](verification.json) · [Null selection results](null-selected.csv) · [Simultaneous bounds](comparison-uncertainty.json) · [Past-only source timestamps](international-availability.csv).
""")
    claims=pd.DataFrame([
      ['Official lagged breadth in rotation/structure','Exploratory lead','Gains on both V9 weekly cohorts in two exact designs.'],
      ['Official breadth in cluster-balanced rotation','Mixed','Weekly Brier worsened in both cohorts; later distribution score improved.'],
      ['Index and sector concentration proxies','Exploratory lead','Chronologically valid proxy information; individual weighted contributions remain unavailable.'],
      ['Training-memory composition versus redundancy','Exploratory lead','Changing dates at equal budget changes errors and effective support.'],
      ['Learned historical usefulness and recent residual','Inconclusive','Compare alternative phases, fixed spread and training-window removal.'],
      ['Native disjoint phase','Exploratory lead','Improved combined weekly point Brier with phase sensitivity and exposed selection.'],
      ['Complete-law ensembles and tail modeling','Exploratory lead','Probability scores, CRPS and calibration favor different combinations.'],
      ['Cross-market or derivative scale inputs','Inconclusive','Endpoint performance and path-volatility outcomes have separate measured effects.'],
      ['Monthly direction','Unresolved','Few disjoint windows and competitive placebo outcomes.'],
      ['Purging and duplicate robustness','Methodological result','Existing exact-copy invariance extends to new breadth fits.'],
    ],columns=['hypothesis','status','evidence'])
    write('signal-classifications.csv',claims)
    emit(13,f"""
The strongest evidence is an observed effect conditional on a specific historical model and chronology. The classifications account for source provenance, exact parent results, sensitivity and search exposure. No independent forecasting edge was established.

{table(claims)}

[Paired increments](incremental-comparisons.csv) · [Phase and episode stability](stress-comparisons.csv).
""")
    emit(14,f"""
V11 scored **{v['predictions']:,}** predictions across **{v['model_configurations']}** registered configurations and **{len(p):,}** matched contrasts. On the full 265-origin weekly sample the best new Brier came from **{topb}**, with **{value(topb,'brier')} Brier** and **{value(topb,'crps')} CRPS**. The best new CRPS came from **{topc}**, with **{value(topc,'crps')} CRPS** and **{value(topc,'brier')} Brier**. V10's distinct references were 0.236181 Brier and 0.010892 CRPS. On the original 92 later origins official breadth yielded **{value('V8_R_RESIDUAL_EQ','brier',5,'later')} Brier** on the V8 residual design and **{value('V8_W_STRUCT_EMBARGO_EQ','crps',5,'later')} CRPS** on the embargoed structure design. The archived models retain their own unchanged scores. These are point estimates conditional on historical design search and the reported intervals.

For the full weekly sample, the search-adjusted block-10 gain interval was **−0.043549 to +0.052456** for the Brier leader versus V10, and **−0.001082 to +0.001311** for the CRPS leader. The later matched breadth improvements also have intervals that cross zero. The point changes support continued retrospective research and provide no independent evidence of an edge.

Breadth interacted materially with the underlying estimator. The data show genuine, archived measures of differential weighting and leadership, with source dates and exact matched additions. Same-budget fit dates, overlap handling and memory remain distinguishable mechanisms. The full monthly chronology has just 11 disjoint return windows, and all evaluated periods remain exposed. [Comparison and uncertainty](V11_COMPLETE_MODEL_COMPARISON.md) · [Audit](verification.json).
""")
    emit(15,"""
1. Freeze the exact V8 and V9 breadth additions, post-publication source rules, and the original parent comparisons before prospective scoring. Retain the native disjoint phase and all-phase ensemble together.
2. Test preservation of historical episodes under equal label budget and overlap geometry. Compare any learned rule with randomized blocks and fixed temporal spread.
3. Hold the weight-learning window and fixed ensemble control stable. Track whether gains reflect complementary errors or simply probability shrinkage.
4. Evaluate endpoint distributions and annualized path volatility separately. Accumulate disjoint monthly outcomes and retain the neutral, historical and lagged-placebo controls.
5. Pursue authenticated constituent histories and a point-in-time corporate-action record for traded global breadth proxies before attributing index contribution or measuring clean total-return breadth.

[V11 research index](NIFTY_V11_RESEARCH.md).
""")
    items='\n'.join(f'{i}. [{n.replace("_"," ").title()}](V11_{n}.md)' for i,n in enumerate(TITLES,1))
    (OUT/'NIFTY_V11_RESEARCH.md').write_text(f"""# NIFTY V11 Research

**{v['predictions']:,} scored predictions · {v['model_configurations']} configurations · {len(p):,} paired comparisons · 15 reports**

All model inputs and outcomes come from 2025–2026. The research freeze ends on November 17. The separately verified close refresh ends on {refresh['last_completed']}. All tested cohorts are research-exposed.

## Reports

{items}

## Reproducibility

[Mission](MISSION.md) · [Run instructions](README.md) · [Verification](verification.json) · [Complete ledger](registry.json) · [All predictions](all-predictions.csv) · [Full distribution archive](full-law-archive.json) · [Delivery manifest](manifest.json)
""",encoding='utf-8')


if __name__=='__main__':run()
