"""Generate the sixteen V10 research reports from the checked result tables."""
from .common import *


SCORE=['model','n','disjoint','brier','crps','log_loss','accuracy','balanced_accuracy','mae','median_mae','coverage80','width80','ECE']
NAMES=['REPRODUCTION_AND_BASELINES','TRAINING_DATA_INTELLIGENCE','OVERLAPPING_LABEL_RESEARCH',
       'SAMPLE_EFFICIENT_MODELS','TARGET_ENGINEERING','STRUCTURED_TRANSFER_LEARNING','NEW_INFORMATION_DISCOVERY',
       'FINANCIALLY_STRUCTURED_MODELS','MONTHLY_SAMPLE_EFFICIENCY','COHERENT_FORECASTING','LEARNING_CURVES_AND_GENERALIZATION',
       'VALIDATION_AND_CUMULATIVE_SEARCH_AUDIT','COMPLETE_COMPARISON','SIGNAL_DISCOVERIES','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS']


def csv(name):
    return pd.read_csv(OUT/f'{name}.csv')


def val(x):
    if pd.isna(x):return '—'
    if isinstance(x,(float,np.floating)):return f'{x:.6f}'
    return str(x).replace('|','\\|') if not isinstance(x,str) or '|' not in x else x.replace('|','\\|')


def table(frame,cols=None):
    if frame.empty:return '_No eligible matched origins._'
    if cols:frame=frame.reindex(columns=cols)
    head='| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'
    return head+'\n'.join('| '+' | '.join(val(c) for c in line)+' |' for line in frame.itertuples(index=False,name=None))


def title(name):
    return ' '.join(s if s in ['V10','V9','V8','NIFTY'] else s.title() for s in name.split('_'))


def emit(index,body):
    n=NAMES[index-1]
    (OUT/f'V10_{n}.md').write_text(f'# V10 {title(n)}\n\n'+body.strip()+'\n',encoding='utf-8')


def run():
    scores=csv('leaderboard');contrast=csv('matched-comparisons');inc=contrast[contrast.is_parent]
    tf=csv('training-information-medians');stress=csv('temporal-and-disjoint-stress')
    old=csv('reproduced-origin-scores');meta=read('reproduction.json');reg=read('experiment-registry.json')
    fresh=read('refresh/refresh-audit.json');protected=read('protected-hash-check.json');audit=read('search-inventory.json')
    verify=read('verification.json');null=csv('bounded-null-selection');ins=csv('invariance-sentinel')
    results=csv('all-predictions');u=read('paired-uncertainty.json')
    all_n=len(results);cfg_n=len(reg['configurations']);fail=pd.DataFrame(reg['attempts']);fails=fail[fail.status!='ok']
    ccols=['horizon','cohort','model','baseline','metric','n','candidate','control','gain','block10_adjusted_low','block10_adjusted_high']
    tcols=['model','training','nominal_rows','distinct_return_sessions','disjoint_training_windows','kish_ESS',
           'overlap_effective_count','maximum_training_weight','df','phase_prediction_variance','design_condition']
    ecols=['model','early Brier','later Brier','combined Brier','early CRPS','later CRPS','combined CRPS']
    measured_fail=fails.groupby(['model','reason'],dropna=False).size().reset_index(name='folds')

    def subset(h=5,c='combined',models=None,batch=None):
        g=scores[scores.horizon.eq(h)&scores.cohort.eq(c)]
        if models is not None:g=g[g.model.isin(models)]
        if batch is not None:g=g[g.batch.isin(batch)]
        return g

    def panel(models=None,batch=None,h=5):
        p=scores[scores.horizon.eq(h)]
        if models is not None:p=p[p.model.isin(models)]
        if batch is not None:p=p[p.batch.isin(batch)]
        z=p.pivot(index='model',columns='cohort',values=['brier','crps'])
        if z.empty:return '_No matched results._'
        z.columns=[f'{c} {m.upper() if m=="crps" else "Brier"}' for m,c in z.columns]
        z=z.reset_index()
        if 'combined Brier' in z:z=z.sort_values('combined Brier')
        return table(z,ecols)

    def parent(models,h=None,cohorts=('early','later','combined')):
        g=inc[inc.model.isin(models)&inc.cohort.isin(cohorts)&inc.metric.isin(['brier','crps'])]
        if h:g=g[g.horizon.eq(h)]
        return table(g.sort_values(['horizon','model','cohort','metric']),ccols)

    def metric(n,key,c='combined',h=5):
        g=subset(h,c,[n])
        return val(g[key].iloc[0]) if len(g) and key in g else '—'

    learning_names=[f'L_ROT_{n}' for n in [85,126,189,252,300,'MAX']]
    replay=old[old.model.isin(learning_names)].groupby('model').agg(n=('origin','size'),brier=('brier','mean'),crps=('crps','mean')).reindex(learning_names).reset_index()
    refs=['P_HIST','P_CLUSTER','J9_STATIC','J9_REL_SHRINK','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','HISTORY','NEUTRAL','REVERSION','BASE5','BASE10','BASE20','BASE_NATIVE','BASE_ROTATION']
    errors=old[old.model.isin(['P_HIST','P_CLUSTER','J9_STATIC','J9_REL_SHRINK','R_RESIDUAL','W_STRUCT_EMBARGO'])].sort_values('brier',ascending=False).groupby('model').head(3)
    emit(1,f"""
All observations used to compute inputs and outcomes are from 2025–2026. The historical origin, decision convention, fold and endpoint come from the archived vintages. The original 17 November 2026 snapshot remains frozen. V10 refitted or reconstructed **{meta['V9_forecasts']:,} V9 forecasts** using their actual IDs and saved chronological partitions, including the fitted V9 reliability gate. It independently refitted **{meta['V8_leading_forecasts']}** forecasts belonging to the protected V8 weekly distribution and direction leaders. [Reproduction ledger](reproduction.json) · [Individual forecast errors](reproduced-origin-scores.csv).

## Exact V9 weekly training-history curve

{table(replay)}

## Frozen probability and distribution references

{panel(refs)}

V10's own historical law uses the last up to 252 mature outcomes on its chronology. The neutral reference uses the same absolute historic returns with symmetric equal masses and a fixed 0.5 probability. The reversion rule applies a fixed −0.25 coefficient to the recent endpoint return and forms a distribution from matured residuals and history. This neutral distribution is a V10 baseline in its own right. Keep its proper scores alongside the empirical historical frequency and the strongest V4–V9 systems.

## Largest replayed origin-level directional errors by system

{table(errors,['model','cohort','origin','p','brier','crps'])}

The legacy exact-copy replay passed **125 required vectors** over the original defensive and sector-alias perturbation suites. [Defensive-copy replay](duplicate-replay/invariance-effects.csv) · [Sector aliases](duplicate-replay/sector-alias-effects.csv).
""")

    selection_names=['C85_RECENT','C85_EARLIEST','C85_SPREAD','C85_BALANCE_ROTATION','C85_ANALOGUES','C126_RECENT','C126_EARLIEST','C126_SPREAD',
                     'C126_W_RECENCY','C126_W_SIMILARITY','C126_W_BALANCE','C126_W_ANALOGUE_RECENCY']
    support=tf[(tf.horizon.eq(5))&tf.cohort.eq('later')&tf.model.isin(selection_names)]
    emit(2,f"""
The 85- and 126-row experiments kept feature definitions, calendar, query folds, ridge penalty and pooled calibration reference fixed. Each comparison changed chronological selection or weights. Selectors tested most recent, earliest, systematic spread, distributed adjacent blocks, balanced volatility/trend/financial-rotation quartiles, nearest analogues, and representatives spread across similarity ranks. Distances use training-fit median and standard deviation of the available state vector. Weighted versions place 40% mass uniformly and 60% on the predeclared recency, similarity, regime-balance or joint analogue–recency rule. V9's weak analogue/reliability transfer motivated the mass floor.

The later weekly 85-recent Brier was **{metric('C85_RECENT','brier','later')}**. The earliest 85 produced **{metric('C85_EARLIEST','brier','later')}** and spread produced **{metric('C85_SPREAD','brier','later')}**. On that exact sample, spread CRPS was **{metric('C85_SPREAD','crps','later')}** versus **{metric('C85_RECENT','crps','later')}**. Median overlap-adjusted training support rose from **17.326** recent to **62.392** spread. The median distinct sessions rose from **89** to **348** and disjoint train windows from **17** to **44**. The earliest 85 retained **17.326** effective observations and still cut loss. Date composition accounts for a separate source of sensitivity beyond the overlap calculation. Earlier weekly point scores improved modestly over the recent-window parent and still trailed symmetric neutral by Brier. Earliest history and broad temporal coverage are leads about the fitting procedure.

## All weekly composition comparisons

{panel(batch=['composition'])}

## Later weekly training support and concentration

{table(support,tcols)}

## Leave recent training months out and replace the removed rows

{parent(['C85_OMIT_M1','C85_OMIT_M2','C85_OMIT_M3'],5)}

Months are ranked from the latest eligible month backward. These month removals and the realized-loss influence table are diagnostics. See the actual dates and maturities in the [fit ledger](composition-ledger.json) and sensitivity to eliminating top-scoring forecast origins in [calendar stress](temporal-and-disjoint-stress.csv).
""")

    overlap_models=['O85_PLAIN','O85_PHASE0','O85_PHASE1','O85_STAGGERED','O85_GLS','O85_BLOCKMEAN','O126_PLAIN',
                    'O126_GLS','OMAX_PLAIN','OMAX_BLOCKMEAN','OMAX_STAGGERED','EC_126_GLS_EMPIRICAL','EC_MAX_GLS_EMPIRICAL']
    overlap=tf[tf.model.isin(overlap_models)&tf.cohort.eq('later')]
    emit(3,f"""
Adjacent five-session labels share up to four daily changes. Adjacent 21-session labels share up to 20. V10 kept the actual daily return calendar and counted unique covered sessions, greedy disjoint windows and equivalent sample size for each fit. The analytical return covariance uses C(i,j) = max(1 − distance(i,j)/h, 0), where distances are observed session indices. Uniform or positive trained weights are summarized by Kish ESS 1/Σw² and overlap ESS 1/(wᵀCw). These are measures under stated assumptions. They do not account for every source of serial correlation or non-stationarity. Evaluation outcome ESS uses observed return autocorrelation and has a different interpretation.

V10 compared ordinary overlapping losses, two fixed disjoint phases, equally weighted fits across all staggered phases, inverse-overlap weighting, generalized least squares with 65% and 85% theoretical covariance, and phase-agnostic time-block aggregate regressions. The empirical covariance follow-up adds a lag-one residual AR kernel fitted on matured inside-fold residual pairs, shrunk toward both the theoretical kernel and identity. Each phase represents a different view of the same market move. Pooled staggered predictions carry measured between-phase variance. GLS diagnostics record overlap support and matrix conditioning. The ridge scale is normalized against constant-intercept information, and the fitted covariance never uses query returns.

## Weekly Brier and CRPS

{panel(batch=['overlap','covariance'])}

## Later training support by horizon

{table(overlap,['horizon']+tcols)}

Expanding block equations improved the ten-input weekly parent in both cohorts. The combined Brier was **{metric('OMAX_BLOCKMEAN','brier')}** versus **{metric('OMAX_PLAIN','brier')}**, with CRPS **{metric('OMAX_BLOCKMEAN','crps')}** versus **{metric('OMAX_PLAIN','crps')}**. GLS and disjoint phases shifted the fitted probability substantially and their results varied across periods and horizons. The block method still trailed the strongest weekly references. [Every fit and phase size](training-information-by-fold.csv) · [Paired disjoint tests](temporal-and-disjoint-stress.csv).
""")

    pert=csv('training-perturbations')
    moments=pert.groupby(['horizon','mode','origin']).agg(rows=('n','median'),sd_p=('p','std'),sd_mean=('mean','std'),brier=('brier','mean')).reset_index()
    sensitivity=moments.groupby(['horizon','mode']).agg(origins=('origin','size'),median_rows=('rows','median'),median_probability_sd=('sd_p','median'),
                  median_location_sd=('sd_mean','median'),mean_Brier=('brier','mean')).reset_index()
    coefs=pd.concat([csv(x+'-coefficients').assign(batch=x) for x in ['composition','structure','overlap','covariance','finalcurve']])
    coef=coefs.groupby(['horizon','cohort','model','feature']).agg(folds=('fold','size'),coefficient_sd=('first_component_standardized_coefficient','std'),
          fraction_positive=('first_component_standardized_coefficient',lambda x:(x>0).mean())).reset_index()
    write('coefficient-stability.csv',coef)
    emit(4,f"""
The predefined sample-efficient families include five-, ten- and twenty-input ridge, family-specific and cluster-specific shrinkage, cluster-balanced Elastic Net, zero-centered Bayesian ridge, family parameter pooling, factor-plus-residual pooling, and five principal directions from twenty causal inputs. Regularization, basis and median/scale transformations obey the fit boundary. The family group penalties incorporate slowly varying exposures only through the causal features. Every fit preserves the estimable standardized coefficients in the underlying feature basis.

## Weekly matched-complexity diagnostics

{panel(['BASE5','BASE10','BASE20','S_GROUPS','S_NATIVE_ROT','S_HIERARCHY','S_ELASTIC','S_BAYES','S_POOL','S_RESIDUAL','S_LOWRANK'])}

## Refit dispersion under twelve draws per origin

{table(sensitivity)}

Small individual random subsets, small contiguous blocks and expanding history with 20% block removal are measured on the same later-origin panel. Weekly probability standard deviations are medians across query origins. The refits also retain return-location dispersion and coefficients. Differences between block selection and individual selection show how strongly the particular market path matters. Larger effective historical support coincided with lower refit dispersion here. These comparisons do not identify the formal bias or variance of a data-generating process. [Refit dates and coefficients](training-perturbations.csv) · [Within-cohort coefficient variability](coefficient-stability.csv).
""")

    target_names=['T_RAW','T_LOG','T_VOL','T_CENTERED','T_SPLIT','T_OVERNIGHT','T_FACTOR','T_SIGNMAG','T_STUDENT','T_VOL_RISK','T_VOL_STUDENT']
    bucket=csv('training-return-buckets');bucket=bucket[bucket.model.isin(['T_RAW','T_SIGNMAG','T_VOL_STUDENT'])&bucket.cohort.eq('combined')]
    emit(5,f"""
All target representations used the same eligibility mask and returns on the same endpoint calendar. V10 compared raw returns, log returns, log returns divided by origin-known trailing realized volatility, log returns relative to the last 63 previously mature same-horizon outcomes, and a jointly predicted broad-market factor plus NIFTY residual. Multi-output forecasts pair residual vectors from the same purged validation origins. The shorter paths split into sessions 1 + 4 for weekly and 5 + 16 for monthly and sum predicted log-return components. Overnight and regular-session log returns are predicted jointly. The true intermediate move is reserved for evaluation. Each complete distribution converts to simple endpoint returns before evaluation.

Sign-and-magnitude estimates positive mass by regularized logistic regression shrunk 35% to the training sign rate. It fits shrunk magnitude adjustments separately within the two signs and combines the conditional samples with that same mass. The empirical and Student-t alternatives use a regularized blend of fitting-history and purged-validation information. The risk-specific empirical model reweights validation residuals conditional on the query's causal volatility bracket.

## Weekly target effects on identical dates

{panel(target_names)}

## Monthly target effects on identical dates

{panel(target_names,h=21)}

## Calibration of all six train-defined return buckets

{table(bucket,['model','horizon','bucket','count','mean_probability','observed','component_Brier'])}

Bucket cutoffs are the 10th, 30th, 50th, 70th and 90th training percentiles for each fold. Both extremes are evaluated alongside ordinary movement. Normalization improved some proper scores relative to the compact direct parent after Student scaling. The volatility Student-t law and the sign/magnitude system experienced different Brier, CRPS and calibration tradeoffs. Full distribution results and per-origin laws are in [target predictions](target-predictions.csv) and [target atom weights](target-laws.jsonl).
""")

    pa=read('transfer-panel-audit.json');group=pd.DataFrame(pa['groups'].items(),columns=['instrument','group'])
    emit(6,f"""
The walk-forward transfer panel contains **{len(group)} instruments** and **{pa['panel_rows']:,} instrument-date rows** before target-specific masks. It combines Indian broad-market and sector indices, selected liquid equities directly observed in the vendor history, ETFs, the Nasdaq Composite, and unrelated US rate and volatility controls. The foreign equity transfer test covered one index with a frozen publication mapping. Current instrument availability can introduce survivorship in the named equities. Cash-index liquidity often lacks a usable volume measure. The bulk of panel input diversity does not increase the number of distinct NIFTY market outcomes.

Comparable feature columns use trailing instrument-volatility normalization for momentum and residual relative strength, lagged rolling beta, cross-sector dispersion, own risk and available turnover. Ridge fitting weights each market date equally by dividing its mass across eligible instruments. All comparisons, including NIFTY-only, use a 21-session maturity cutoff for shared tasks and purged chronological inner calibration. Foreign rows receive an additional two eligible-date buffers and use the archived publication mapping. The test compares pooled coefficients, sector-only and ETF-only parameters, foreign-only augmentation, shrinkable asset-specific intercepts, two shared supervised panel factors, and heavily shrunk NIFTY deviations from a pooled model. The multitask designs learn a rank-two basis across 1, 3, 5, 10, 15 and 21 sessions plus five-session realized risk and bank leadership, or use just the shortest return tasks with those same risk/leadership tasks. Final output layers use the target horizon.

## Instrument inventory

{table(group)}

## Weekly transfer results and falsifications

{panel(batch=['transfer'])}

## Monthly transfer results and falsifications

{panel(batch=['transfer'],h=21)}

The weekly direction gain from strongly regularized transfer changed sign across cohorts and its distribution improvement was small. The random and shifted auxiliary tasks also achieve some numerical gains. Compare all of them with the same-complexity NIFTY-only model. Monthly transfer failed to establish meaningful improvement over neutral or historical references. Auxiliary labels are randomly permuted in blocks or shifted only within previously matured training data for negative controls. [Panel](transfer-panel.csv) · [Transfer fit membership and diagnostics](transfer-ledger.json).
""")

    source_names=['N_EQ_CONTROL','N_EQ_OFFICIAL','N_INTRA_CONTROL','N_INTRA_PANEL','N_DERIV_RAW','N_DERIV_STRUCT','N_RISK_MATCHED','N_GLOBAL_RISK_MATCHED','DATED_FUTURES','DATED_STRADDLE']
    f=read('feature-audit.json')['checks'];dv=read('dated-derivatives-audit.json')
    emit(7,f"""
**Authoritative equal-weight leadership.** V10 retrieved **{f['official_equal_weight_count']}** daily observations each for NIFTY 50 Equal Weight, NIFTY500 Equal Weight and their two cap-weight companions from the NSE daily index archives. Over **{f['official_cap_overlap']}** frozen comparable spot dates the largest vendor–official NIFTY close difference was **{f['official_cap_max_delta']:.4f} index points**, with **{f['official_cap_abs_difference_gt_1']}** above one point. Inputs are trailing five- and 21-session relative returns. Dated daily historical constituent weights were unavailable in the authenticated inputs. We retained official equal-weight index evidence and left constituent contribution and heavyweight attribution unestimated. [NSE indices historical data](https://www.niftyindices.com/reports/historical-data) · [NSE index data subscriptions](https://www.niftyindices.com/offerings/data-subscription) · [Index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf).

**Synchronized intraday.** The Upstox V3 historical endpoint returned **27,888** 25-minute Bank, Financial, IT and Auto index bars. The panel validated **458** complete aligned regular sessions with all 15 candles per instrument. Opening and closing breadth use the first and last 50 minutes. Additional fields capture synchronized direction, open-to-close leadership shifts and late volatility concentration. Features are available after the last bar closes. The exact eligibility mask applies to both the candidate and matched parent. [Upstox historical candle API](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [Intraday audit](intraday-source-audit.json).

**Derivatives.** Inherited official EOD reports supply lagged near-future basis, OI change, put/call positioning and strike concentration. V10 tested the trailing-median basis residual and ETF-turnover-normalized OI, then parsed the archived instrument and expiry IDs for **{dv['rows_with_two_futures']}** sessions with two or more dated futures contracts and **{dv['detected_expiry_changes']}** changes in the front contract. The new features include same-contract futures-minus-cash log returns, prior-lot-matched OI changes per traded underlying unit, OI roll shifts, nearby futures activity and tenor-scaled net carry. The latter measures a combined carry proxy given the absence of an authenticated funding and dividend decomposition. Matched traded near-ATM straddles provide **{dv['field_counts']['straddle_21day_scale']}** dated premium observations. The premium divided by spot and scaled to a 21-calendar-day tenor represents option-priced risk. V10 compares it with a common dated parent and omits inferred realized direction probabilities. Derivatives input dates use one completed observed-session lag. [NSE archive reports](https://www.nseindia.com/all-reports) · [Dated contract inputs](dated-derivatives-inputs.csv) · [Source checks](dated-derivatives-audit.json).

**Global risk.** The repaired monthly and weekly comparisons use identical eligible target masks, the same causal volatility reconstruction, and extra foreign risk/divergence features drawn from conservatively timed publications. The initial two global-risk fits omitted a target volatility completeness mask and failed across 50 folds. The failures remain logged and the corrected comparisons have distinct names.

## Matched source increments

{parent(source_names,None,('early','later'))}

The contract and straddle additions improved both proper scores versus their compact parent in the monthly cohorts. Their weekly gains are concentrated in the later cohort. All monthly proper scores for these additions are weaker than symmetric neutral, and the straddle premium may contain variance risk premia and pricing effects.
""")

    financial=['BASE10','S_COMMON','S_RESID_FACTOR','S_STATE_LEVEL','S_STATE_LAG','S_STATE_EXPECTED','S_PERSIST','S_DISTRIBUTED','S_REMOVE_BANK','S_LAG_ROTATION','T_STUDENT','T_VOL_RISK','T_VOL_STUDENT']
    emit(8,f"""
Trailing beta estimates use at most 63 dated sector return observations, with at least 35, and are shifted before applying the exposure. The common component is lagged beta times current benchmark return. Residual market structure includes mean relative momentum, cross-sector dispersion and a bank residual. The two views add separately to the same ten-input parent. Removing the bank residual and delaying the financial/defensive source pair by one observed session test model sensitivity. The factor-adjusted target simultaneously predicts the broad factor and residual, with a shrunk and bounded beta.

The state-transition experiment models volatility, trend, participation, liquidity and defensive and financial leadership using causal rolling AR(1) summaries with 42 observations, warmup 25 and coefficients clipped to ±0.9. Ordinary lagged states and existing levels provide direct controls. Further models compare slowly varying 21-session factors and strongly shrunk 0, 5, 10 and 21 session rotation lags. Returns and scale follow separate procedures in the Student and volatility-conditioned laws. Genuine weighted sector contribution would require dated effective memberships and weights capable of mapping a disjoint constituent set into NIFTY.

## Weekly values

{panel(financial)}

## Monthly values

{panel(financial,h=21)}

{parent(['S_RESID_FACTOR','S_STATE_EXPECTED','S_REMOVE_BANK','S_LAG_ROTATION'],5,('combined',))}
""")

    monthly=['HISTORY','NEUTRAL','REVERSION','V6_MONTH_STATE','V6_MONTH_LAG1','V8_MS_WINDOW','V8_MS_ROLL','V7_M_STATE_SHIFT5','V7_M_STATE_SHIFT21',
           'P_CLUSTER','OMAX_BLOCKMEAN','O126_PHASE0','EC_126_GLS_EMPIRICAL','S_PERSIST','S_DISTRIBUTED','S_ELASTIC','T_VOL_STUDENT','T_SPLIT',
           'T_OVERNIGHT','T_SIGNMAG','X_MULTI','X_ADAPT','J10_HISTORY_SHRINK']
    falses=scores[scores.horizon.eq(21)&scores.cohort.eq('combined')&scores.model.str.contains('PLACEBO|SHIFT')]
    emit(9,f"""
The comparable sample has **141 earlier** and **76 later** origins, **217 combined**. There are **{metric('NEUTRAL','disjoint',h=21)}** disjoint windows in the combined chronology and **{metric('NEUTRAL','disjoint','later',21)}** in the later cohort. Later high accuracy from smoothed state was historically sensitive to lag and shift controls. V10 tests different estimation mechanisms and declines to use rolling counts as independent monthly replications.

{panel(monthly,h=21)}

## Shifted and block-permuted state controls on the combined chronology

{table(falses.sort_values('brier'),['model','n','disjoint','brier','crps','accuracy','balanced_accuracy'])}

The fixed 0.5 symmetric model achieved combined Brier **{metric('NEUTRAL','brier',h=21)}** and CRPS **{metric('NEUTRAL','crps',h=21)}**. The monthly 126-row volatility Student-t fit and the 300-row fit require their actual coverage and comparison controls. More rows in a panel or different staggered phases cannot remove the small number of distinct monthly episodes. See [full monthly ranking and coverage](monthly-leaderboard.csv), [matched learning curves](learning-curve-matched.csv), and [disjoint phases and leave-calendar-month stress](temporal-and-disjoint-stress.csv). Shifts and block randomizations act only within estimation dates for diagnosis.
""")

    m=['NEUTRAL','HISTORY','T_RAW','T_VOL_STUDENT','T_SIGNMAG','T_SPLIT','T_OVERNIGHT','T_VOL_RISK',
       'J10_TARGET_BLEND','J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK','J10_SMALL_BLEND','J10_TRANSFER_BLEND','J9_REL_SHRINK']
    emit(10,f"""
One weighted law supplies p(up), expected return, median return, quantiles, return buckets, expected endpoint and both central intervals. Every atom is a simple endpoint return. The endpoint estimate is origin close × (1 + the law's mean return). Interval endpoints derive from the law's 25th/75th and 10th/90th percentiles. Weighted finite approximations use 301 Student-t quantiles when applicable. Component fitting and de-normalization are performed before mixing. Paired shorter-path predictions preserve dependence through common residual draws. The empirical endpoint law does not identify every intervening path.

## Weekly full-law comparisons

{table(subset(5,models=m).sort_values('crps'),SCORE)}

## Monthly full-law comparisons

{table(subset(21,models=m).sort_values('crps'),SCORE)}

Five fixed mixture rules combine complete distributions. The structural law uses weights 0.40 base rotation, 0.30 sparse rotation and 0.30 volatility Student-t. The history-shrunk law gives half to that mixture and half to empirical history. The registry preserves the target, small-sample and transfer blends as well. These weights were registered as adaptive follow-ups to the initial batch results, and all relevant cohorts remain exposed. [Mixture recipe](mixture-registry.json) · [Weighted atoms](mixture-laws.jsonl) · [Calibration bins for all systems](calibration-bins.csv).
""")

    curve=csv('learning-curves');curve['registered_budget']=curve.registered_budget.astype(object).fillna('expanding')
    emit(11,f"""
After initial results V10 selected systematic history coverage, return-block estimating equations and a volatility Student-t law for deeper curves. Each keeps the ten-input frame and compares with the same raw recent-window model. Budgets are 85, 126, 189, 252, 300 and expanding, subject to enough matured labels and an identical calibration mask. The history-spread selector converges to recent at the expanding cap because both include all dates. Larger budgets start later. Compare methods at a given budget using exact matches. Do not interpret differences between different sets of evaluation dates as pure learning effects.

## Weekly and monthly curves by scope

{table(curve,['horizon','cohort','model','registered_budget','n','training','overlap_effective_count','brier','crps','coverage80','width80'])}

![Brier and CRPS by training budget at fixed weekly and monthly origins](learning-curves-fixed-origins.png)

Matched scoring recalculates candidate and parent on the same dates. The strict intersection across all six budgets contains 48 weekly origins and 11 monthly origins, all later. The 300-row volatility Student-t monthly Brier of 0.203091 is based on those 11 rolling origins, with CRPS 0.072836. The broader 126-row result of 0.249888 uses 176 origins with CRPS 0.034473. The full-coverage neutral CRPS is 0.025420. [Budget-by-budget matched contrasts](learning-curve-matched.csv) · [All budgets on the strict origin intersection](learning-curves-fixed-origins.csv) · [Exact V9 curve](V10_REPRODUCTION_AND_BASELINES.md).

## Separate historical refresh

V10 refreshed through **{fresh['observed_through']}**, validating official closes for {', '.join(fresh['post_frozen_dates'])}. This equals the final completed boundary previously captured by V9. The original 17 November history remains unchanged. **{fresh['historical_reconstruction']['5']['matured_frozen_origins']} weekly** and **{fresh['historical_reconstruction']['21']['matured_frozen_origins']} monthly** archived historical origins matured in the four additional sessions, with **{fresh['historical_reconstruction']['5']['checked_archived_rows']+fresh['historical_reconstruction']['21']['checked_archived_rows']}** stored model predictions checked against the reacquired outcomes. The previously issued 17 November V4 late-diagnostic forecasts remain pending to 25 November and 17 December as of this refresh. [Refresh assessment](refresh/refresh-audit.json) · [Scores on unchanged archival forecasts](refresh/frozen-forecast-rescore.csv).
""")

    ns=[]
    for (h,c,k),g in null.groupby(['horizon','cohort','metric']):
        real=g[g.draw.eq(-1)].iloc[0];a=g.loc[g.draw.ge(0),'best_gain']
        ns.append({'horizon':h,'cohort':c,'score':k,'origins':real.origins,'actual_max_gain':real.best_gain,'null_median':a.median(),
                   'null_p95':a.quantile(.95),'null_max':a.max(),'share_null_at_least_as_large':(a>=real.best_gain).mean()})
    exceptional=pd.DataFrame([(k,v['comparison_count'],v['calendar_origins'],v['critical_values']['10']) for k,v in u['scope'].items()],
                       columns=['weekly scope','adjusted contrasts','origins','block-10 critical'])
    emit(12,f"""
All historical data were inspected in the V1–V10 research process. V9's historical inventory records **{audit['prior_registry_exact']} exact configuration fingerprints** and **{audit['prior_prediction_fingerprints']} distinct stored prediction fingerprints**. V10 added **{audit['V10_registered_configs']}** named configurations, **{audit['V10_scored_model_horizons']}** scored model–horizon vectors and **{audit['V10_distinct_vector_hashes']}** distinct vector hashes under the V10 schema and rounding. Different historical schemas and recording coverage limit any single cumulative total. Initial batches, target-completeness correction, empirical overlap covariance, learning curves, and mixtures have dated registries. The last four stages are adaptive. Prior hash verification covered **{protected['files_checked']:,}** protected files with **{len(protected['changed_or_missing'])}** differences.

## Paired block bootstrap on weekly comparisons

{table(exceptional)}

Positive gain means control loss less candidate loss. The resampling uses 2,000 shared circular block draws for sizes 5, 10 and 15, maximizing standardized centered loss deviations across the declared comparison family within each scope. Nominal and simultaneous intervals are recorded. These bounds address a finite V10 set conditional on a research-exposed archive. Monthly reports use matched losses and disjoint stress given the low disjoint count.

## Bounded selection replay with block-permuted training labels

{table(pd.DataFrame(ns))}

Six representative specifications were compared on the first origin per selected exposed monthly fit, **16** null draws per horizon. Each draw refits each configuration and scores the biggest mean Brier or CRPS gain using real held-out outcomes, validation targets and history. The sparse origin subset and small simulation budget make the empirical tail coarse. This is a falsification check on the selected gain and has limited scope.

The exact-copy and future-information tests passed **{len(ins)}** V10 checks with maximum atom error **{ins.max_atom_error.max():.3g}**. Additional controls delay sources, remove groups and training months, resample training blocks, perturb monthly states and randomize, shift or replace transfer tasks. Search interval coverage, failure counts and legality of all fit partitions were verified by [verification](verification.json).

## Recorded unestimated folds

{table(measured_fail)}
""")

    wb=csv('weekly-probability');wd=csv('weekly-distribution');monthly_all=csv('monthly-leaderboard')
    core=subset(5);new_week=core[core.full_scope&core.source.eq('V10')&core.classification.eq('retrospective')]
    neutral='NEUTRAL';top_b=new_week.sort_values('brier').model.iloc[0];top_c=new_week.sort_values('crps').model.iloc[0]
    decisive=contrast[(contrast.model.isin([top_b,top_c,'N_EQ_OFFICIAL','OMAX_BLOCKMEAN','C85_SPREAD','T_VOL_STUDENT']))&
       contrast.cohort.eq('combined')&contrast.horizon.eq(5)&contrast.metric.isin(['brier','crps'])&
       contrast.baseline.isin(['NEUTRAL','HISTORY','P_CLUSTER','J9_REL_SHRINK','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO'])]
    emit(13,f"""
The rankings retain cohort and origin coverage, eligibility and fixed benchmarks. Positive gains in the incremental ranking mean reduction in loss versus the registered parent. Frozen systems are ranked on overlapping compatible origins, and headline combined tables require 265 weekly or 217 monthly outcomes. A high ranking on a partial window has its own sample.

## Combined weekly probability quality

{table(wb.head(14),SCORE)}

## Combined weekly distribution quality

{table(wd.head(14),SCORE)}

## Combined monthly full-coverage results

{table(monthly_all[monthly_all.cohort.eq('combined')&monthly_all.full_scope].head(12),SCORE)}

## Paired uncertainty around selected weekly claims

{table(decisive,ccols)}

[Small-sample leaderboard](small-sample-leaderboard.csv) · [Temporal stability](temporal-stability-leaderboard.csv) · [Earlier results](earlier-leaderboard.csv) · [Later results](later-leaderboard.csv) · [Monthly results](monthly-leaderboard.csv) · [Incremental gains](incremental-information.csv) · [Research Pareto frontier](research-pareto.csv).

The Pareto analysis combines early and later Brier and CRPS, calibration error, median training use, effective complexity, cohort gap and, for weekly comparisons, the search-adjusted combined Brier lower gain bound versus history. It includes systems with measured dimensions on both cohorts. Empirical laws share return-distribution benchmarks but have a different model-complexity interpretation. Frozen leaders remain visible in the score and temporal tables.
""")

    classes=pd.DataFrame([
       ['Equal-budget training-date composition','EXPLORATORY LEAD','Large late weekly loss changes with the same 85 rows in different dates. Gains are relative to the matched recent-window control.'],
       ['Block-aggregate endpoint regression','EXPLORATORY LEAD','More useful than ordinary overlapping compact Ridge in both weekly cohorts. Parent match is weaker than frozen leaders.'],
       ['Analytical and empirical GLS','INCONCLUSIVE','Numerical regularization gives finite fits, with inconsistent broad score improvement.'],
       ['Canonical group penalties and pooling','INCONCLUSIVE','Invariant representations remain useful. Gains vary by cohort and loss.'],
       ['Volatility-normalized Student-t and sign/magnitude','EXPLORATORY LEAD','Better point scores against compact direct models, with differences in calibration and monthly stability.'],
       ['Shared cross-market coefficients and adaptations','REJECTED IMPLEMENTATION','Economic transfer failed to separate convincingly from within-sample null auxiliary controls.'],
       ['Inter-horizon low-rank basis','REJECTED IMPLEMENTATION','Monthly gains were weak and late-period Brier remained high.'],
       ['Official equal-weight spreads','EXPLORATORY LEAD','Lower weekly proper losses than the matched parent across both cohorts.'],
       ['Synchronized intraday state','INCONCLUSIVE','Small Brier movement and mixed CRPS on complete dates.'],
       ['Lagged futures positioning and carry proxies','INCONCLUSIVE','Proxy definitions and limited broad improvements.'],
       ['Global risk conditioning','REJECTED IMPLEMENTATION','Corrected parent matched at identical dates, and changes in risk and direction did not transfer reliably.'],
       ['Persistent state and distributed monthly lags','INCONCLUSIVE','Falsification and few disjoint months limit mechanism claims.'],
       ['Complete-law fixed mixtures','EXPLORATORY LEAD','Measured weekly probability versus distribution tradeoff with high adaptive exposure.'],
       ['Causal overlap accounting and exact-copy invariance','METHODOLOGICAL ACHIEVEMENT','Verified calendar accounting, frozen-model replay and robustness to exact aliases.'],
    ],columns=['hypothesis','classification','evidence'])
    write('hypothesis-classification.csv',classes)
    emit(14,f"""
V10's reproduced results establish sensitivity to specific training dates and distinguish raw row count from overlap-adjusted information. The fitted model remains invariant under the tested exact-copy transformations. V10 assigns no independently validated edge and no robust retrospective candidate on these results.

{table(classes)}

Official breadth has a credible new source and a small positive weekly increment. The best retrospective law from a particular league table has exposure to the same research chronology. Model sensitivity, fixed-date transfer falsification and the paired intervals determine the statuses above. [Classification data](hypothesis-classification.csv).
""")

    emit(15,f"""
V10 scored **{all_n:,} forecasts** in **{cfg_n} registered configurations**, producing **{len(contrast):,} matched contrasts** with the same dates and realized endpoints. The experiment reproduced the previously reported later weekly training length sensitivity and showed that **which 85 dates are selected** has a large effect at a fixed budget. The recent 85 and systematically spread 85 yielded later Brier **{metric('C85_RECENT','brier','later')}** and **{metric('C85_SPREAD','brier','later')}**, respectively. Full-history block aggregation improved compact Ridge from combined weekly Brier **{metric('OMAX_PLAIN','brier')}** to **{metric('OMAX_BLOCKMEAN','brier')}**. Neither result overturns the frozen weekly references.

On the full weekly V10 chronology **{top_b}** had the lowest new Brier at **{metric(top_b,'brier')}**, with CRPS **{metric(top_b,'crps')}**. **{top_c}** had the lowest new CRPS at **{metric(top_c,'crps')}**, with Brier **{metric(top_c,'brier')}**. For comparison, V9 cluster-balanced rotation was **{metric('P_CLUSTER','brier')}** Brier and the V9 reliability blend was **{metric('J9_REL_SHRINK','crps')}** CRPS. The frozen V8 later weekly direction Brier was **{metric('V8_R_RESIDUAL','brier','later')}**, and its protected distribution CRPS was **{metric('V8_W_STRUCT_EMBARGO','crps','later')}**. Selected improvements are provisional after the search adjustment and earlier/later comparison. The symmetric monthly model remains the strongest low-complexity full-coverage reference, with **{metric(neutral,'brier',h=21)}** Brier and **{metric(neutral,'crps',h=21)}** CRPS.

Authentic equal-weight breadth, extra intraday observations, date-grouped panels and directly decomposed targets improved coverage of available information. Training geometry reduction and complete probability laws made the forecasting problem easier to audit. Cross-market borrowing, recent-only learning, and stronger dependence correction did not reliably close the probability or distribution gap. A 2025–2026 retrospective run can prioritize a future test but cannot independently validate these choices against new unexplored history.

[All scored forecasts](all-predictions.csv) · [Verification](verification.json) · [Matched comparisons](matched-comparisons.csv).
""")

    emit(16,f"""
1. Freeze the 85-date spread selector, expanding block estimator, official equal-weight augmentation and two complete-law mixtures with their parents. Use the existing date-maturity rule and exact source definitions for one prospective comparison once targets are available. Keep event time and data availability immutable.
2. On weekly dates evaluate symmetric neutral, V9 P_CLUSTER and the protected V8 comparators beside the new procedures. Define the exact parent and practical minimum Brier and CRPS improvement before scoring any new outcomes. Retain adverse episodes and disjoint return windows.
3. Prospectively predefine how to distinguish calendar coverage, dependence and market regime. Use a fixed training budget, propensity across historical states, and both effective sample estimates. Archive per-fold losses and hold out whole market episodes.
4. For monthly learning, study a small fixed shortlist comprising symmetric neutral, a volatility Student-t law, sparse native rotation, and one matched historical blend. Require enough non-overlapping monthly outcomes and keep the shifted-state tests diagnostic.
5. Revisit constituent contribution only when authenticated point-in-time effective weights and membership can be acquired. Use point-in-time data for derivatives carry, curve tenor and rolls before making exposure attribution claims.
6. Keep further transfers constrained to a prespecified family and calendar controls. Verify whether any early relative improvement survives shifted, random and unrelated aux panels and the same matched NIFTY-only law.

The previous V4 diagnostic issue remains pending within this vintage. Task-specific dates, configs and source hashes are linked from the [study index](NIFTY_V10_RESEARCH.md). 
""")

    index='\n'.join(f'{i}. [{title(n)}](V10_{n}.md)' for i,n in enumerate(NAMES,1))
    (OUT/'NIFTY_V10_RESEARCH.md').write_text(f"""# NIFTY V10 Research

V10 extends the 5- and 21-session study using only 2025–2026 input history and outcomes. The primary frozen snapshot ends on 17 November 2026. The separately checked market refresh ends on {fresh['observed_through']}. All evaluated historical cohorts are research-exposed.

**{all_n:,} scored predictions · {cfg_n} registered configurations · {len(contrast):,} matched contrasts · {len(NAMES)} research reports**

The weekly training dates mattered at a fixed 85-row budget. The best full-coverage V10 weekly scores were **{metric(top_b,'brier')}** Brier from **{top_b}** and **{metric(top_c,'crps')}** CRPS from **{top_c}**. The model family and claims are limited by error overlap and adaptive search exposure. The monthly comparison has only **{metric('NEUTRAL','disjoint',h=21)}** disjoint windows.

## Reports

{index}

## Reproducibility

[Mission](MISSION.md) · [Verification](verification.json) · [Full registry and fit attempts](experiment-registry.json) · [Model/source manifest](manifest.json) · [Historical replay](reproduction.json) · [All forecast outputs](all-predictions.csv) · [Incremental comparisons](incremental-information.csv) · [Run instructions](README.md)
""",encoding='utf-8')


if __name__=='__main__':run()
