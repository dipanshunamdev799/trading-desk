# NIFTY V8 — STRUCTURAL ALPHA DISCOVERY, ROBUST FEATURE LEARNING & COHERENT FORECASTING

## MISSION

You are continuing our autonomous quantitative forecasting research using the existing Upstox, NSE, Indian equity, global-market, derivatives, ETF, and Python research infrastructure.

We have completed V1–V7.

The research has generated increasingly promising retrospective weekly forecasts, but **no independently validated forecasting edge has been established**.

V8 must continue active experimentation using 2025–2026 observations.

We are not stopping research, restricting ourselves to prospective validation, or abandoning alternative hypotheses.

Instead, we will use the discoveries from V7 to investigate how market information should be represented, how domestic sector rotation affects NIFTY, and whether better conditional return distributions can be learned.

### Primary targets

- **Weekly:** Next 5 NIFTY trading sessions.
- **Monthly:** Next 21 NIFTY trading sessions.

Auxiliary horizons and targets are permitted for mechanism discovery, but they must not replace the primary targets based on retrospective performance.

### Core objectives

1. Find better representations of Indian market information.
2. Build models less sensitive to duplicated and correlated inputs.
3. Understand the predictive relationships behind domestic sector rotation.
4. Explore changes in market structure rather than only indicator levels.
5. Improve directional probabilities and complete return distributions.
6. Reinvestigate global, derivatives, ETF and intraday information through targeted hypotheses.
7. Identify whether monthly lagged-state performance reflects genuine information or historical selection.
8. Produce stronger exploratory candidates where the evidence supports them.

Do not optimize solely for the highest historical classification accuracy.

We want predictive information that can survive reasonable changes in features, model design, training windows, and market conditions.

**Status: RESEARCH ONLY. NO TRADING. NO DEPLOYMENT.**

---

# PHASE 1 — REPRODUCE V7 AND IDENTIFY THE TRUE RESEARCH LEADS

Read the complete V7 research index, 15 reports, model configurations, full prediction CSV, comparison data, feature clusters, saved source files, and verification artifacts.

Reproduce the following exact weekly systems:

| System | Brier | CRPS | Research importance |
|---|---:|---:|---|
| T_ROT_DOMESTIC | 0.162145 | 0.009927 | Best probability result |
| T_ROT_EMBARGO | 0.164792 | 0.009935 | Highest reported accuracy, 82.61% |
| T_ROT_LAG5 | 0.164382 | 0.010040 | Tests sensitivity to timing |
| T_DAY_ETF | 0.166525 | 0.009974 | ETF-based weekly lead |
| T_ELASTIC_EMBARGO | 0.184134 | 0.009665 | Best full-distribution result |
| V6_BRIER | 0.169803 | 0.010068 | Prior probability benchmark |
| V6_CRPS | 0.178802 | 0.009756 | Prior distribution benchmark |

Also preserve the strongest V5 and V4 reference models.

Investigate why each system succeeded or failed on individual historical origins.

For each system, reconstruct:

- Exact data sources.
- Input definitions and timestamp rules.
- Model coefficients or fitted parameters.
- Training-window boundaries.
- Feature scaling.
- Missing-data handling.
- Regularization.
- Per-origin predictive distributions.
- Correct and incorrect directional calls.
- Periods of improvement or deterioration.

Calculate matched per-origin differences, not merely aggregate metric changes.

### Important diagnostics

V7's strongest probability model correctly classified 74 of 92 origins, but those forecasts represent only 19 disjoint return windows, with an effective-sample diagnostic near 12.36.

The selection process examined thousands of contrasts, and the adjusted gain interval crossed zero.

Preserve that distinction throughout V8.

Deliver `V8_REPRODUCTION_AND_WINNER_DIAGNOSIS.md`.

---

# PHASE 2 — SOLVE THE DUPLICATED-FEATURE PROBLEM

This is the highest-priority theoretical and empirical research task.

V7 demonstrated that duplicating six defensive-sector inputs changed the Ridge model's Brier from 0.182047 to 0.188090 despite adding no information.

Rescaling duplicated columns restored the original predictions.

This indicates that regularization geometry and feature representation materially influence the model.

## Objective

Develop and test feature-learning methods that do not arbitrarily change forecasts when informationally identical features are duplicated.

### Research A: Exact-duplicate invariance

Construct controlled tests where features are:

- Duplicated once.
- Duplicated several times.
- Reordered.
- Expressed in equivalent units.
- Duplicated and appropriately rescaled.
- Replaced by mathematically equivalent representations.

Determine which existing models are sensitive to these transformations.

For a model explicitly designed to be duplicate-invariant, require identical predictions within numerical tolerance when exact copies are added.

Do not treat invariance to arbitrary nonlinear transformations as an automatic requirement.

### Research B: Correlated-feature group regularization

Investigate:

1. Canonical exact-feature deduplication.
2. Correlation-cluster normalization.
3. Group-wise penalty scaling.
4. Cluster-balanced Ridge.
5. Cluster-balanced Elastic Net.
6. Group-aware Bayesian shrinkage.
7. Hierarchical shrinkage.
8. Covariance-aware regularization.
9. Factor and residual separation.
10. Within-cluster representative learning.

Cluster definitions and transformations must be fitted on historical training data only.

### Research C: Overlapping information versus independent information

Determine whether correlated indices contain:

- Redundant market-direction information.
- Shared benchmark subtraction.
- Overlapping constituent exposures.
- Genuine economically distinct sector signals.
- Useful residual information after removing common factors.

Where historical constituents and weights are unavailable, do not assert that correlations arise from particular holdings.

### Research D: Stability

Test the methods across:

- Different training-window lengths.
- Different months.
- Different volatility regimes.
- Different feature counts.
- Different numbers of duplicated columns.
- Reasonable regularization settings.

Measure prediction stability, not just average Brier.

### Success criteria

A useful method should reduce arbitrary duplication sensitivity while retaining predictive information.

It must demonstrate more than a lower score on the same selected historical dates.

Deliver:

- `V8_REGULARIZATION_GEOMETRY.md`
- `V8_DUPLICATE_INVARIANCE_TESTS.md`
- `V8_CLUSTER_AWARE_MODELS.md`

---

# PHASE 3 — UNDERSTAND DOMESTIC SECTOR ROTATION

V7's strongest weekly probability improvement came from two features:

1. The five-session change in Bank Nifty versus financial-services momentum.
2. The five-session change in defensive versus cyclical momentum.

Investigate these features deeply.

## Research questions

- Are these signals genuinely informative individually?
- Does their combination add value?
- Are they detecting sector rotation or simply market momentum?
- Do they anticipate NIFTY reversals?
- Do they predict trend continuation?
- Are they primarily volatility proxies?
- Do they work differently in bullish and bearish markets?
- Are the features identifying financial-sector concentration?
- Does defensive leadership contain information after controlling for broad-market returns?

## Controlled feature experiments

Evaluate:

- Bank versus financial-services spread alone.
- Defensive versus cyclical spread alone.
- Both features jointly.
- Original momentum levels without their changes.
- Changes without the levels.
- Relative-return residuals after controlling for NIFTY.
- Normalized spread changes.
- Rolling slopes.
- Momentum acceleration.
- Sign changes in leadership.
- Extreme rotation events.
- Interaction with volatility.
- Interaction with market breadth.

Keep the number of variants controlled and registered.

### Timing investigation

V7's five-session-lagged rotation model remained relatively competitive.

This raises an important possibility: the useful information may be persistent market conditions rather than the precise latest rotation observation.

Compare:

- Current-state rotation.
- Lagged rotation.
- Moving averages of rotation.
- Rotation changes.
- Long-term rotation persistence.
- Shifted-state placebo controls.

Use genuine past observations for forecast candidates.

Use circular shifts only as explicitly labeled falsification controls; never permit circularly wrapped future states into a live-compatible forecast.

Determine whether the mechanism requires recent information or merely captures persistent trends.

### Market-regime investigation

Test behavior across:

- High versus low volatility.
- Uptrends versus downtrends.
- Broad participation versus narrow leadership.
- Financial-sector strength versus weakness.
- Defensive versus cyclical leadership.
- Strong versus weak global markets.

Report conditional sample sizes and uncertainty.

### Required output

`V8_DOMESTIC_ROTATION_MECHANISMS.md`

Identify the smallest, most interpretable feature set capable of reproducing the useful V7 historical behavior.

---

# PHASE 4 — DISCOVER MARKET-STRUCTURE FEATURES

Do not stop at the two successful rotation features.

Investigate related structural information available in the broader NSE and Upstox universe.

Research:

- Sector momentum dispersion.
- Sector leadership persistence.
- Rotation speed.
- Correlation regime transitions.
- Financial-sector concentration.
- Defensive/cyclical spread dynamics.
- Large-cap versus broader-index leadership.
- Sector return asymmetry.
- Sector volatility divergence.
- Cross-index residual momentum.
- ETF activity relative to index movements.
- Market-wide return synchronization.

### New research approach

Instead of engineering hundreds of independent technical indicators, construct a small number of economically interpretable market-state variables.

Examples:

**Financial leadership state:** Relative momentum and changes in banks, financial services, and the broad index.

**Cyclical risk state:** Relative performance and dispersion across cyclical and defensive sectors.

**Market participation state:** Breadth and index-level participation proxies constructed without historical membership leakage.

**Liquidity state:** ETF and stock-volume activity, normalized by historical conditions.

**Volatility transition state:** Changes in realized risk and available implied-risk proxies.

Test whether these structural states improve predictions beyond individual indicator levels.

Use training-only definitions and comparisons.

Deliver `V8_MARKET_STRUCTURE_DISCOVERY.md`.

---

# PHASE 5 — IMPROVE COHERENT RETURN DISTRIBUTIONS

The best V7 CRPS model achieved 0.009665, while the best Brier model achieved 0.162145.

These were different forecasting systems.

V8 should investigate whether better distributional learning can improve both metrics without sacrificing calibration.

## Research A: Stronger conditional distributions

Evaluate:

- Cluster-balanced Elastic Net distributions.
- Conditional residual distributions.
- Shrunk Student-t distributions.
- Low-dimensional factor-conditioned distributions.
- Regularized quantile models.
- Mixtures of coherent return distributions.
- Distributional regression.
- Probability-adjusted conditional distributions.

Keep the models small enough to fit the available data.

## Research B: Joint scoring

Investigate controlled combinations of Brier and CRPS objectives.

Do not invent an arbitrary mixture solely because it scores well historically.

If optimizing a weighted objective, determine its weight using training-only evaluation.

Report the full tradeoff curve between probability quality and distribution quality.

## Research C: Distribution coherence

From every complete predictive law, derive:

- Probability of positive return.
- Expected return.
- Median return.
- Return quantiles.
- Return-bucket probabilities.
- Endpoint price distribution.

These quantities must be mathematically compatible.

Never combine a classifier's probability with an unrelated return-distribution model and present them as one unified forecast.

## Research D: Calibration

Evaluate:

- Probability calibration.
- Quantile calibration.
- Central 50% interval coverage.
- Central 80% interval coverage.
- Conditional coverage by volatility regime.
- Interval sharpness.
- Tail-probability behavior.

Evaluate raw and adjusted distributions separately.

Fit any adjustment using only earlier resolved predictions.

Disable adjustments that fail historical out-of-sample improvement tests.

Deliver `V8_JOINT_PROBABILITY_DISTRIBUTION.md`.

---

# PHASE 6 — RESEARCH ETF, VOLUME AND INTRADAY INFORMATION

V7 identified additional weekly leads involving ETF activity and opening/closing behavior.

However, the historical intraday candles produced discrepancies against the authoritative daily reference.

Investigate this carefully.

## Research A: ETF intelligence

Examine:

- Relative ETF turnover.
- Volume shocks.
- Abnormal volume.
- ETF price versus underlying-index returns.
- Changes in participation.
- ETF volatility and price impact proxies.
- Volume activity conditional on sector rotation.

Determine whether ETF data adds independent information beyond the domestic-rotation model.

## Research B: Intraday market behavior

Investigate only historically complete and correctly aligned sessions.

Potential features:

- Opening return.
- First-hour momentum.
- Closing-hour movement.
- Intraday reversal.
- Realized volatility.
- Price range concentration.
- Day-end directional pressure.
- Intraday volatility asymmetry.

Audit source instruments, timestamps, candle construction, and historical session completeness.

The research previously found meaningful discrepancies between last intraday prices and official daily closes.

Do not quietly substitute intraday values for the official reference close.

## Research C: Conditional integration

Test whether ETF or intraday information matters more during:

- Strong sector rotation.
- High volatility.
- Large index moves.
- Weak breadth.
- Global risk-off conditions.

Use parent-versus-added-feature comparisons to isolate incremental value.

Deliver `V8_ETF_LIQUIDITY_INTRADAY.md`.

---

# PHASE 7 — TARGETED GLOBAL-MARKET RESEARCH

We have access to global-market information, but previous direct additions generally failed.

Do not abandon it, and do not repeat indiscriminate global feature concatenation.

Focus on carefully defined pathways.

Candidate hypotheses:

- Nasdaq movement predicts Indian IT relative performance.
- Global volatility affects Indian sector synchronization.
- Oil and currency shocks affect cyclical/defensive rotation.
- US rate changes affect Indian financial leadership.
- Asian market dispersion anticipates Indian market participation changes.

For each pathway:

1. Verify authentic historical data and its availability cutoff.
2. Test the proposed intermediate Indian-market target.
3. Test whether the intermediate information improves NIFTY forecasts.
4. Compare against the domestic-only parent model.
5. Test across different regimes.
6. Document negative results.

Use conservative foreign-session alignment.

Do not interpret correlations as causal transmission without appropriate evidence.

If global information fails to add value, document why the tested implementation failed and move on.

Deliver `V8_GLOBAL_CONDITIONAL_SIGNALS.md`.

---

# PHASE 8 — MONTHLY FORECASTING: INVESTIGATE LAGGED STATES AND PERSISTENCE

Monthly forecasting remains unresolved.

V7 found:

- V6_MONTH_STATE: 81.58% directional accuracy, Brier 0.178345.
- V6_MONTH_LAG1: Brier 0.175091, CRPS 0.024530.
- M_STATE_LAG21: Brier 0.171774, CRPS 0.025530 and 84.21% nominal-80% coverage.
- Shifted-state controls sometimes improved CRPS beyond genuine current-state models.

These findings require careful investigation.

Only four disjoint monthly evaluation windows were available.

## Research A: Is the apparent signal really persistence?

Test whether the successful lagged forecasts rely on:

- Persistent market trends.
- Autocorrelated state indicators.
- Broad market regimes.
- Delayed sector relationships.
- Label overlap.
- Class imbalance.
- Specific historical episodes.

Compare against simple persistence, reversion, lagged-return and historical-frequency controls.

## Research B: Separate state information from price information

Evaluate:

- Price-only models.
- State-only models.
- State plus price.
- Lagged state plus current price.
- Lagged price plus current state.
- Training-state permutation controls.
- State shift and alignment controls.

Ensure placebo tests do not introduce future information.

## Research C: Temporal structure

Investigate whether monthly signals are better represented through:

- Persistent sector factors.
- Low-frequency rotation.
- Longer-window momentum.
- Smoothed volatility.
- Average state over prior weeks.
- Market-state transitions.

Avoid excessive complexity.

## Research D: Intermediate horizons

Study 10-session and 15-session forecasts diagnostically.

Determine whether information disappears gradually as the horizon increases.

Do not redefine the primary monthly target based on whichever horizon looks strongest.

### Monthly validation requirement

Do not treat overlapping monthly origins as independent observations.

Do not report artificially narrow confidence intervals.

Keep retrospective monthly discoveries explicitly exploratory.

Deliver `V8_MONTHLY_PERSISTENCE_AND_FALSIFICATION.md`.

---

# PHASE 9 — EXPLORE ADDITIONAL INFORMATION WITHOUT INFLATING SAMPLE SIZE

We have substantial intraday and cross-sectional datasets.

Research whether they can improve estimation of market states and features.

Possible approaches:

- Sector-index panel models.
- Shared factor estimation across individual stocks.
- Cross-sectional volatility models.
- Liquid-stock breadth indicators.
- Intraday-derived liquidity states.
- Multi-task learning across related indices.
- Auxiliary shorter-horizon predictions.

However:

**Thousands of instruments and millions of rows do not create thousands of independent future NIFTY outcomes.**

Use date-grouped validation and appropriate dependence handling.

Keep historical constituent-membership limitations explicit.

Use auxiliary tasks to improve representation learning, not to manufacture independent validation.

Deliver `V8_CROSS_SECTIONAL_RESEARCH.md`.

---

# PHASE 10 — EXPAND VALID HISTORICAL EVIDENCE WHERE POSSIBLE

Our current main evaluations contain 92 weekly and 76 monthly origins.

Investigate whether additional chronologically valid research origins can be produced from 2025–2026 data using alternative predeclared training designs.

Examples:

- Smaller but appropriately regularized training histories.
- Rolling versus expanding training.
- Reduced indicator warm-up requirements where mathematically valid.
- Low-dimensional model variants that need fewer fitting observations.
- Alternate fixed forecast cutoffs.
- Earlier evaluation periods when sufficient matured labels exist.

Do not weaken timestamp or label-maturity rules.

Do not cherry-pick training requirements to increase performance.

If new designs permit more historical origins, clearly separate them into new evaluation cohorts.

Compare models on identical dates within each cohort.

Do not claim newly reconstructed historical dates are untouched confirmation if prior research examined them.

Report whether conclusions remain stable across cohort choices.

Deliver `V8_HISTORICAL_COVERAGE_AND_SENSITIVITY.md`.

---

# PHASE 11 — EXPERIMENTAL SEARCH AND STATISTICAL DISCIPLINE

V1–V7 have already examined many models and hypotheses.

The risk of repeated historical selection is substantial.

V8 must remain exploratory without disguising this limitation.

## Required controls

- Chronological walk-forward evaluation.
- Matured target labels only.
- Appropriate purge and embargo handling.
- Training-only scaling and feature selection.
- Timestamp and revision checks.
- Matched-origin baselines.
- Dependence-aware uncertainty.
- Multiple-comparison adjustments.
- Leave-month diagnostics.
- Training-window sensitivity.
- Shifted-feature negative controls.
- Block-preserving randomized controls.
- Exact reproducibility tests.

### Search accounting

Record all attempted configurations, not just successful ones.

Distinguish:

- Predeclared first-stage experiments.
- Diagnostic perturbations.
- Post-result follow-up experiments.
- New hypotheses discovered during V8.
- Frozen reference models.

The number of previous research versions must not be ignored when interpreting newly selected point winners.

An adjustment for comparisons within V8 alone is not sufficient to establish independent superiority across the entire adaptive V1–V8 process.

### Stress-testing priorities

For any new weekly leader, investigate:

1. Removal of individual months.
2. Removal of the highest-gain observations.
3. Alternative disjoint-window phases.
4. Feature duplication.
5. Correlated-group perturbation.
6. Changed training-window length.
7. Source-timing sensitivity.
8. Sector-rotation lag sensitivity.
9. Calibration stability.
10. Comparison against the strongest V7 models.

A model that improves only one selected historical episode should not be promoted as robust.

Deliver `V8_VALIDATION_AND_SEARCH_RISK.md`.

---

# PHASE 12 — BUILD THE V8 RESEARCH LEADERBOARD

Maintain separate leaderboards for:

**Weekly directional/probability forecasting**

Primary metric: Brier.

Secondary metrics: log loss, balanced accuracy, calibration and stability.

**Weekly return-distribution forecasting**

Primary metric: CRPS.

Secondary metrics: coverage, width, quantile loss, return error and probability quality.

**Monthly forecasting**

Report all relevant metrics, but avoid ranking based on headline accuracy alone.

### Mandatory reference models

Include:

- T_ROT_DOMESTIC.
- T_ROT_EMBARGO.
- T_ELASTIC_EMBARGO.
- T_DAY_ETF.
- V6_BRIER.
- V6_CRPS.
- V5 I03_nosize.
- V5 L01.
- V4 coherent-distribution controls.
- Neutral and historical-frequency baselines.

Do not compare different evaluation cohorts as though they contained identical forecasts.

### Required statistics

- Origin count.
- Disjoint-window count.
- Effective-sample estimate.
- Accuracy and balanced accuracy.
- Brier and log loss.
- CRPS.
- MAE and RMSE.
- Quantile loss.
- Central-50% and central-80% coverage.
- Interval widths.
- Leave-month sensitivity.
- Parent-model incremental gain.
- Matched reference-model gain.
- Search-adjusted uncertainty.
- Current evidence classification.

Rank complete forecasting systems separately from the incremental value of individual information sources.

Deliver `V8_COMPLETE_COMPARISON.md`.

---

# PHASE 13 — REQUIRED ARTIFACTS

Produce the following versioned reports:

1. `V8_REPRODUCTION_AND_WINNER_DIAGNOSIS.md`
2. `V8_REGULARIZATION_GEOMETRY.md`
3. `V8_DUPLICATE_INVARIANCE_TESTS.md`
4. `V8_CLUSTER_AWARE_MODELS.md`
5. `V8_DOMESTIC_ROTATION_MECHANISMS.md`
6. `V8_MARKET_STRUCTURE_DISCOVERY.md`
7. `V8_JOINT_PROBABILITY_DISTRIBUTION.md`
8. `V8_ETF_LIQUIDITY_INTRADAY.md`
9. `V8_GLOBAL_CONDITIONAL_SIGNALS.md`
10. `V8_MONTHLY_PERSISTENCE_AND_FALSIFICATION.md`
11. `V8_CROSS_SECTIONAL_RESEARCH.md`
12. `V8_HISTORICAL_COVERAGE_AND_SENSITIVITY.md`
13. `V8_VALIDATION_AND_SEARCH_RISK.md`
14. `V8_COMPLETE_COMPARISON.md`
15. `V8_SIGNAL_DISCOVERIES.md`
16. `V8_FINAL_RESEARCH_CONCLUSIONS.md`
17. `V8_NEXT_EXPERIMENTS.md`

Preserve:

- Complete Python source code.
- Exact configurations and random seeds.
- Source and model hashes.
- Feature definitions.
- Cluster assignments.
- Per-origin predictions.
- Score and calibration files.
- Hypothesis registry.
- Failed experiments.
- Negative controls.
- Reproduction tests.
- Full search history.

Do not modify V1–V7 artifacts.

Do not modify the existing V4 prospective ledger or any frozen issued forecasts.

If new experimental forecasts are issued, store them separately with immutable timestamps and explicit exploratory status.

---

# PHASE 14 — EXECUTION STRATEGY

Do not attempt every hypothesis in one enormous uncontrolled search.

Proceed in structured waves.

### Wave 1 — Mechanism research

Reproduce V7, test duplicate invariance, explain regularization effects, and isolate the domestic-rotation mechanism.

### Wave 2 — Focused model improvement

Research cluster-aware regularization, improved rotation representations, and conditional return distributions.

### Wave 3 — Additional information

Investigate ETF activity, market-state changes, intraday structure, targeted global relationships and cross-sectional factors.

### Wave 4 — Monthly research

Study lagged state persistence, time alignment, falsification controls, and low-dimensional monthly models.

### Wave 5 — Stress testing and synthesis

Evaluate promising candidates against all strong prior controls, calculate dependence- and search-aware uncertainty, and produce an integrated research conclusion.

Allocate additional research effort to promising directions, but preserve the failed hypotheses and their evidence.

Do not sacrifice scientific integrity simply to obtain a new record Brier score.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing research repository, access authenticated historical market sources, write scripts, engineer features, fit models, conduct experiments, and save reproducible results.

Do not stop after writing an execution plan.

Execute feasible research.

Use only 2025–2026 observations.

Do not import pre-2025 fitted states or historical data.

Do not silently extend the scope into 2027.

Do not place trades, modify trading systems, or deploy capital.

### THE CENTRAL V8 QUESTIONS

**1. Can we build models whose predictions are not arbitrarily distorted by duplicated or correlated market inputs?**

**2. Does changing domestic sector leadership contain repeatable predictive information about NIFTY's next five sessions?**

**3. Can stronger feature representations improve both directional probability and the full distribution of future returns?**

**4. Is monthly forecasting being driven by genuine market-state persistence, or by overlapping outcomes and historical model selection?**

Use the extensive Upstox, NSE, Indian-equity and global-market data universe to answer these questions.

Continue exploring new approaches, but make every improvement traceable to a specific hypothesis.

Our goal is not merely to achieve 82%, 85%, or 90% retrospective accuracy.

Our goal is to discover forecasting relationships that remain meaningful when challenged.

**BEGIN V8 RESEARCH.**