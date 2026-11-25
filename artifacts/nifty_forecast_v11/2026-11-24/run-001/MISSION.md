# NIFTY V11 — MARKET BREADTH, CONCENTRATION, TRAINING MEMORY & STRUCTURAL ENSEMBLE INTELLIGENCE

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global markets, derivatives, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V10 of our NIFTY forecasting research.

We have accumulated substantial knowledge about market relationships, feature redundancy, sector rotation, statistical estimation, training-data composition, overlapping outcomes and coherent predictive distributions.

However, we have not established an independently validated forecasting edge.

**We are deliberately continuing research using 2025–2026 observations.**

Do not stop experimenting merely because previous studies failed to establish independent statistical significance.

V11 must investigate the most promising new discoveries from V10 while remaining open to fundamentally different approaches.

### Primary forecasting objectives

- NIFTY return over the next five trading sessions.
- NIFTY return over the next 21 trading sessions.
- Directional probabilities.
- Expected and median returns.
- Coherent conditional return distributions.
- Forecast uncertainty.
- Conditions under which particular forecasting mechanisms are more useful.

### Core V11 research directions

1. Genuine market breadth using official equal-weight indices.
2. Market concentration and heavyweight-stock leadership.
3. Intelligent selection of historical training observations.
4. Persistent versus temporary predictive relationships.
5. Overlap-aware estimation.
6. Structural ensemble forecasting.
7. Underused information from our broader market-data universe.
8. Alternative monthly forecasting mechanisms.

Use only 2025–2026 observations.

All previously inspected historical periods remain research-exposed.

NO LIVE TRADING. NO CAPITAL DEPLOYMENT.

---

# PHASE 1 — REPRODUCE AND UNDERSTAND V10

Read the complete V10 research index, all 16 reports, experiment registry, source scripts, configurations, model artifacts and saved predictions.

Recover exact implementations from the repository.

Reproduce the following references:

| System | Combined weekly Brier | Combined weekly CRPS |
|---|---:|---:|
| Historical benchmark | 0.259048 | 0.011340 |
| V9 cluster-balanced rotation | 0.236386 | Recover from artifacts |
| V9 fixed historical blend | 0.246239 | 0.011029 |
| V9 reliability/history blend | 0.248725 | 0.011014 |
| J10_STRUCTURAL_BLEND | 0.236181 | 0.011043 |
| J10_HISTORY_SHRINK | 0.242366 | 0.010892 |

Preserve V8's later-cohort records of 0.159504 Brier and 0.009453 CRPS on their original evaluation dates.

Also reproduce:

- Official equal-weight breadth experiments.
- Earliest, latest and distributed training-date experiments.
- Overlapping-label and block-aggregation experiments.
- Volatility-normalized Student-t forecasts.
- Sign-and-magnitude forecasts.
- Structured transfer-learning controls.
- Monthly futures and straddle additions.
- Monthly symmetric-distribution baseline.
- Duplicate-invariance verification.

Do not modify V1–V10 artifacts or frozen predictions.

Create an independent V11 research workspace.

---

# PHASE 2 — DEEP OFFICIAL MARKET BREADTH RESEARCH

This is the highest-priority new information-discovery task.

V10 acquired authentic historical observations for:

- NIFTY 50 Equal Weight.
- NIFTY500 Equal Weight.
- Their cap-weighted counterparts.

Adding these inputs improved weekly Brier and CRPS in both historical cohorts.

Investigate this relationship deeply.

## 2.1 Expand the available index universe

Audit authentic historical data for:

- Equal-weight indices.
- Cap-weighted indices.
- Broad-market indices.
- Sector indices.
- Quality indices.
- Momentum indices.
- Value indices.
- Low-volatility indices.
- Dividend indices.
- Available strategy indices.
- Sector-specific equal-weight alternatives.
- Relevant ETFs.

These are research candidates, not assumptions about data availability.

Verify their methodology, historical coverage, publication timing and source provenance.

Distinguish contemporaneously published historical index observations from retrospectively calculated or backfilled index histories.

Do not silently use a backfilled index as though it were available at the historical forecast origin.

## 2.2 Breadth and concentration indicators

Develop controlled features representing:

- NIFTY 50 Equal Weight relative to NIFTY 50.
- NIFTY500 Equal Weight relative to NIFTY 500.
- Broad-market equal-weight versus cap-weight divergence.
- Changes in those divergences.
- Relative momentum.
- Relative volatility.
- Breadth acceleration.
- Breadth persistence.
- Concentration expansion and contraction.
- Divergence between broad-market participation and large-cap performance.

Use relative log returns or another explicitly consistent mathematical representation.

Test multiple economically meaningful horizons.

Do not generate hundreds of arbitrary lookback combinations.

## 2.3 Research hypotheses

Investigate whether:

1. Rising NIFTY with weakening equal-weight performance predicts future weakness.
2. Improving equal-weight participation precedes index continuation.
3. Narrow market leadership predicts mean reversion.
4. Broad participation predicts more persistent trends.
5. Equal-weight divergence is informative primarily under particular volatility conditions.
6. Changes in breadth contain more information than absolute breadth levels.
7. Breadth and financial-sector rotation interact.
8. Equal-weight information improves return magnitude and volatility forecasts independently of direction.

These are hypotheses, not established facts.

## 2.4 Mechanism falsification

Determine whether apparent breadth improvements merely reflect:

- Existing momentum information.
- Common NIFTY exposure.
- Shared sector exposures.
- Size effects.
- Volatility differences.
- Index rebalancing.
- Different weighting methodologies.
- Historical selection.

Compare against the individual equal-weight and cap-weight returns, their spread, and residualized versions.

Do not interpret equal-weight outperformance as a direct measurement of the number of advancing stocks.

Do not infer individual constituent contributions without authentic historical membership and weights.

### Required comparison

Add the breadth features independently to:

- V8 residualized rotation.
- V8 market-structure models.
- V9 cluster-balanced rotation.
- V10 sparse rotation.
- V10 structural blend components.

Use matched parent models to determine incremental value.

Beating a weak parent is insufficient to establish superiority over the strongest existing systems.

Deliver:

`V11_OFFICIAL_BREADTH_RESEARCH.md`

---

# PHASE 3 — MARKET CONCENTRATION AND INTERNAL LEADERSHIP

Investigate whether NIFTY forecasting improves when we understand the distribution of market leadership rather than simply the aggregate index return.

## Research questions

- Is index performance driven by widespread participation or concentrated leadership?
- Does financial-sector leadership reinforce or contradict broader-market participation?
- Does equal-weight weakness during index strength precede corrections?
- Do concentration changes predict future volatility?
- Does sector participation interact with broad-market breadth?
- Is narrow leadership more persistent during certain market conditions?

## Candidate information

Research:

- Equal-weight/cap-weight spreads.
- Financial-sector relative returns.
- Defensive/cyclical leadership.
- Sector dispersion.
- Cross-index synchronization.
- Residual market momentum.
- Relative volatility.
- Leadership concentration proxies.
- Sector rank transitions.

Where authentic historical constituent weights are available, investigate actual weighted contribution and concentration.

Otherwise, explicitly label index-spread and dispersion measures as proxies.

## Structural market states

Investigate whether a compact representation consisting of the following states can outperform large feature matrices:

1. Broad-market participation.
2. Market concentration.
3. Financial-sector leadership.
4. Defensive/cyclical rotation.
5. Volatility.
6. Liquidity.
7. Global-relative strength.

Compare levels, changes, residuals and persistence.

Preserve the exact-duplicate invariance property established in V8.

Deliver:

`V11_MARKET_CONCENTRATION_AND_LEADERSHIP.md`

---

# PHASE 4 — INTELLIGENT HISTORICAL TRAINING MEMORY

V10 demonstrated that the same model trained on the same number of observations can produce dramatically different forecasts depending on the historical dates selected.

This deserves a dedicated investigation.

## 4.1 Reproduce the central result

On the same later weekly origins, the ten-input model achieved:

| Training design | Brier |
|---|---:|
| Most recent 85 observations | 0.376831 |
| 85 observations distributed across history | 0.243061 |
| Earliest 85 observations | 0.242128 |

The distributed sample increased distinct underlying sessions and overlap-adjusted effective observations.

However, the earliest contiguous sample achieved nearly the same forecasting performance without the same increase in effective observations.

Therefore, investigate training-period composition separately from overlapping-label dependence.

## 4.2 Historical episode analysis

Identify how different eligible historical blocks influence:

- Learned coefficients.
- Probability forecasts.
- Expected returns.
- Conditional distribution width.
- Tail estimates.
- Forecast stability.
- Incremental feature value.

Use block removal, block replacement, coefficient perturbation and training influence diagnostics.

Retrospective analysis may identify informative periods, but those results must not directly become an operational training-selection rule.

## 4.3 Training-memory architectures

Investigate:

- Long-term historical memory.
- Recent market memory.
- Distributed historical memory.
- Regime-balanced memory.
- Volatility-balanced memory.
- Diverse market-episode memory.
- Mixtures of long-term and short-term models.
- Stratified historical replay.

Test whether models benefit from retaining older observations rather than continuously discarding them.

Explore training sets that preserve multiple market conditions even when the current regime appears different.

## 4.4 Control the training budget

Compare designs using equal training budgets:

- 85 observations.
- 126 observations.
- 189 observations.
- 252 observations.
- 300 observations.
- Expanding history.

Where possible, additionally match the number of disjoint return windows and distinct underlying daily sessions.

Report when these quantities cannot be held constant simultaneously.

This helps distinguish:

- Number of training labels.
- Degree of target overlap.
- Historical market episodes.
- Recency.
- Diversity.
- Feature-distribution changes.

## 4.5 Learn historical block usefulness

Investigate whether past forecasting results can identify useful historical training blocks.

At each forecast origin, use only previously matured forecast errors.

Potential approaches:

- Block-level historical loss.
- Regularized block weights.
- Training-state diversity.
- Stability-based weighting.
- Historical coefficient consistency.
- Similarity combined with diversity.

Compare learned selection against simple fixed distributed sampling.

V10's similarity and recency weighting often failed. Do not merely recreate those methods with new parameters.

A useful training-memory method should demonstrate improvements across historical cohorts, not only on the selected later period.

Deliver:

`V11_INTELLIGENT_TRAINING_MEMORY.md`

---

# PHASE 5 — PERSISTENT VERSUS TEMPORARY MARKET RELATIONSHIPS

Investigate which forecasting relationships are stable over the available 2025–2026 period.

## Hypotheses

- Some relationships are structurally persistent.
- Some relationships are temporary and regime-dependent.
- Some apparent relationships are artifacts of historical model selection.
- Recent data may overwhelm useful longer-term relationships.
- A mixture of persistent and temporary effects may improve forecasting.

## Research approaches

Compare:

1. Long-history fixed coefficients.
2. Short-history coefficients.
3. Long-history coefficients with strongly regularized recent adjustments.
4. Shared persistent effects plus temporary residual effects.
5. Historical block ensembles.
6. Hierarchical shrinkage toward stable coefficients.

One possible model structure is:

Prediction = persistent market component + recent market adjustment.

The recent adjustment must be regularized and learned causally.

Evaluate whether this representation performs better than unrestricted adaptive coefficients, which frequently disappointed us in V9.

Investigate coefficient sign stability and prediction sensitivity across training blocks.

Do not confuse coefficient stability with proven predictive usefulness.

Deliver:

`V11_PERSISTENT_MARKET_RELATIONSHIPS.md`

---

# PHASE 6 — OVERLAP-AWARE TRAINING AND DATA DIVERSITY

Continue the overlap investigation from V10.

Block averaging improved some compact weekly models in both historical cohorts, while GLS and disjoint-phase methods produced mixed results.

Investigate:

- Training-block averaging.
- Distributed non-overlapping observations.
- Staggered-phase ensembles.
- Overlap-aware loss weighting.
- Regularized covariance-aware estimation.
- Block-based training diversity.
- Ensembles trained on different historical blocks.

Evaluate these methods using both compact models and the stronger native/rotation systems.

Do not limit overlap-aware estimation to weak compact parents.

Report:

- Nominal training observations.
- Distinct underlying daily returns.
- Disjoint target windows.
- Effective training information diagnostics.
- Prediction sensitivity under block resampling.
- Forecasting performance.

Investigate whether improved training diversity and overlap handling work together or address largely separate problems.

Staggered phases and resampled blocks do not create independent market history.

Deliver:

`V11_OVERLAP_AND_TRAINING_DIVERSITY.md`

---

# PHASE 7 — STRUCTURAL ENSEMBLE INTELLIGENCE

V10's strongest combined weekly results came from mixtures of complete return distributions.

We must investigate why those combinations helped.

## 7.1 Preserve the original mixtures

J10_STRUCTURAL_BLEND:

- 40% base rotation.
- 30% sparse rotation.
- 30% volatility Student-t.

J10_HISTORY_SHRINK:

- 50% structural blend.
- 50% empirical historical distribution.

These are research references, not permanent optimal weights.

## 7.2 Expert diversity

Investigate whether the different experts genuinely capture complementary information.

Compare:

- Per-origin probability predictions.
- Per-origin distribution forecasts.
- Correlation between model errors.
- Shared failure periods.
- Directional disagreement.
- Distribution disagreement.
- Conditional calibration.
- Performance in different market conditions.

An ensemble of several nearly identical models may provide little independent value.

## 7.3 New expert families

Develop a limited number of distinct experts:

- Native Indian market internals.
- Financial-sector rotation.
- Official equal-weight breadth.
- Market concentration and leadership.
- Cluster-balanced structural forecasts.
- Volatility-normalized Student-t forecasts.
- Sign-and-magnitude forecasts.
- Historical return distributions.
- ETF and liquidity information.

Include derivatives or global experts only when they have a clearly distinct hypothesis and useful intermediate evidence.

## 7.4 Ensemble approaches

Compare:

- Equal weighting.
- Fixed structural weighting.
- Strongly regularized stacking.
- Historical-distribution shrinkage.
- Diverse training-memory ensembles.
- Regime-conditioned mixtures.
- Constrained mixture optimization.
- Brier-focused versus CRPS-focused mixtures.

Any weights learned from data must use only earlier matured forecasts.

Do not optimize mixture weights on the final evaluation cohort and present the result as unbiased performance.

## 7.5 Investigate expert complementarity

For each expert, calculate whether adding it improves the complete ensemble relative to:

- Its strongest parent ensemble.
- Equal-weight alternatives.
- Simple historical shrinkage.
- The best individual expert.

Perform leave-one-expert-out tests.

Determine whether a new expert provides distinct information or merely additional regularization.

## 7.6 Forecast coherence

Mix complete predictive return laws.

All final quantities must come from the same mixture:

- Directional probability.
- Mean return.
- Median return.
- Return quantiles.
- Return-bucket probabilities.
- Expected endpoint price.
- Prediction intervals.

Do not mix inconsistent statistics from unrelated models.

Deliver:

`V11_STRUCTURAL_ENSEMBLE_RESEARCH.md`

---

# PHASE 8 — IMPROVE RETURN-DISTRIBUTION LEARNING

V10 found that volatility-normalized Student-t and sign-and-magnitude approaches improved substantially over their raw-target parent.

Investigate these mechanisms using stronger native, breadth and rotation representations.

## Research tracks

### A. Location-scale forecasting

Estimate conditional return location and scale using different statistically appropriate mechanisms.

Build one coherent predictive distribution.

### B. Sign-and-magnitude forecasting

Investigate whether positive and negative returns have meaningfully different conditional magnitude distributions.

Use a coherent law combining sign probability and sign-conditional magnitude.

### C. Tail calibration

V10 identified underestimation of the lowest return bucket.

Investigate:

- Tail probability calibration.
- Volatility-dependent tail behavior.
- Distribution asymmetry.
- Heavy-tailed residual models.
- Shrinkage toward empirical tail distributions.

Use training-defined buckets and proper scoring rules.

### D. Distribution mixtures

Explore whether breadth, rotation and historical-return experts produce complementary information about different parts of the return distribution.

Compare against fixed mixtures before introducing dynamic weights.

Evaluate:

- Brier.
- Log loss.
- CRPS.
- Quantile loss.
- Return errors.
- Bucket calibration.
- 50% and 80% coverage.
- Interval width.
- Tail calibration.

Deliver:

`V11_DISTRIBUTIONAL_LEARNING.md`

---

# PHASE 9 — EXPLOIT ADDITIONAL UPSTOX AND GLOBAL INFORMATION

Continue investigating the full market-data universe.

Do not assume previous unsuccessful implementations prove an entire information family is useless.

However, prioritize hypotheses that materially differ from earlier experiments.

## A. Cross-market breadth

Investigate authentic global equal-weight, cap-weight, sector and breadth indicators where available.

Research whether domestic-versus-global breadth divergence provides information beyond headline global index returns.

## B. Derivatives and market-priced risk

V10 found that futures and traded-straddle additions improved monthly performance against compact parents in both cohorts, although they still trailed the symmetric baseline.

Investigate:

- Futures curve structure.
- Same-contract futures/cash divergence.
- Rollover behavior.
- OI changes.
- Near-ATM traded straddles.
- Expiry-normalized market-priced risk.
- Realized versus priced risk.

Test derivatives as conditional distribution and volatility inputs, rather than forcing them into directional prediction.

Do not interpret option-implied risk-neutral probabilities as actual return probabilities.

## C. Intraday breadth

Research synchronized opening, midday and closing behavior across authentic sector indices.

Investigate whether:

- Broad opening strength persists.
- Closing participation contains information beyond daily returns.
- Intraday sector rotation anticipates daily or weekly rotation.
- Late-day concentration predicts subsequent volatility.

Use complete, validated sessions and preserve the authoritative daily target reference.

## D. Historical constituent information

Continue seeking authentic dated membership and weighting information using permitted sources.

If unavailable, document that limitation.

Do not fabricate historical constituent weights.

For every new information source, use matched incremental comparisons against strong parent systems.

Deliver:

`V11_ADDITIONAL_MARKET_INTELLIGENCE.md`

---

# PHASE 10 — MONTHLY FORECASTING: BREADTH, PERSISTENCE AND DISTRIBUTIONS

Monthly forecasting remains unresolved.

The combined monthly comparison contains 217 origins but only 11 disjoint windows.

The symmetric forecast remains the strongest full-sample reference on the reported probability and distribution metrics.

Do not celebrate another 80% monthly accuracy result without strong falsification.

## Research directions

Investigate:

1. Persistent equal-weight/cap-weight divergence.
2. Longer-term market concentration.
3. Slow financial-sector leadership.
4. Historical training-memory mixtures.
5. Volatility-normalized monthly distributions.
6. Derivatives-based conditional risk.
7. Structured multi-horizon learning.
8. Monthly location-scale models.
9. Historical return shrinkage.
10. Mixtures of complete monthly return laws.

Use simple, strongly regularized models.

Compare against:

- Symmetric monthly forecast.
- Historical monthly distribution.
- Reversion.
- V6 monthly-state references.
- V8 smoothed-state references.
- V9 cluster-balanced rotation.
- V10 volatility Student-t.
- V10 sign-and-magnitude.
- Shifted-state and randomized-state controls.

Investigate whether monthly direction is less predictable than monthly volatility or return magnitude.

Keep endpoint prediction and path-risk prediction distinct.

Do not manufacture precise uncertainty intervals from 11 disjoint outcomes.

Deliver:

`V11_MONTHLY_FORECASTING_RESEARCH.md`

---

# PHASE 11 — ROBUST MODEL COMPARISON

V11 must not optimize exclusively for the later 92-origin weekly cohort.

## Mandatory evaluation cohorts

- Earlier weekly: 173 origins.
- Later weekly: 92 origins.
- Combined weekly: 265 origins.
- Earlier monthly: 141 origins.
- Later monthly: 76 origins.
- Combined monthly: 217 origins.

These are reference cohort sizes. If particular models have different eligibility, disclose it and use matched-origin comparisons.

Keep the frozen November 17 vintage for reproduction.

Separately acquire any additional completed 2026 observations available at execution time.

Do not overwrite earlier data vintages or frozen forecasts.

## Research success dimensions

Measure:

1. Combined weekly Brier improvement.
2. Combined weekly CRPS improvement.
3. Earlier-cohort performance.
4. Later-cohort performance.
5. Calibration and interval sharpness.
6. Training-sample efficiency.
7. Sensitivity to historical episode selection.
8. Incremental value of official breadth.
9. Robustness across disjoint-window phases.
10. Search-adjusted uncertainty.

A model that substantially improves both historical cohorts deserves more research attention than one that slightly improves the later record while failing earlier.

Maintain a Pareto frontier instead of forcing a single winner.

Deliver:

`V11_COMPLETE_MODEL_COMPARISON.md`

---

# PHASE 12 — VALIDATION AND CUMULATIVE SEARCH AUDIT

We have now evaluated a very large number of hypotheses across V1–V10.

Repeated historical selection is a serious limitation.

V11 remains exploratory.

## Required controls

- Chronological walk-forward fitting.
- Matured-label enforcement.
- Training-only preprocessing.
- Purging and embargoes.
- Source-timestamp verification.
- Exact-duplicate invariance.
- Matched-origin comparisons.
- Block-bootstrap uncertainty.
- Disjoint-window diagnostics.
- Multiple-comparison adjustments.
- Training-block perturbation.
- Feature-family removal.
- Shifted-state placebos.
- Block-permuted target controls.
- Future-information sentinel tests.

## New falsification requirements

For the official breadth hypotheses:

- Compare genuine breadth with matched lagged and block-shifted controls.
- Remove existing momentum information.
- Control for size and volatility.
- Test alternative legitimate index pairs.
- Audit publication and backfill assumptions.

For training-memory methods:

- Compare against equal-budget random and distributed historical blocks.
- Refit and reselect under representative null searches.
- Test sensitivity to removing historically favorable blocks.
- Distinguish the retrospective best training set from a causally selectable training set.

For ensembles:

- Compare against fixed-weight controls.
- Test whether redundant experts create misleading diversification.
- Report the distribution of performance across training perturbations.

Register all initial experiments and subsequent adaptive follow-ups.

Preserve every failure.

Do not claim that V11's search adjustment accounts for the entire V1–V11 adaptive research process.

Deliver:

`V11_VALIDATION_AND_SEARCH_AUDIT.md`

---

# PHASE 13 — RESEARCH OUTPUTS

Produce:

1. `V11_REPRODUCTION_AND_BASELINES.md`
2. `V11_OFFICIAL_BREADTH_RESEARCH.md`
3. `V11_MARKET_CONCENTRATION_AND_LEADERSHIP.md`
4. `V11_INTELLIGENT_TRAINING_MEMORY.md`
5. `V11_PERSISTENT_MARKET_RELATIONSHIPS.md`
6. `V11_OVERLAP_AND_TRAINING_DIVERSITY.md`
7. `V11_STRUCTURAL_ENSEMBLE_RESEARCH.md`
8. `V11_DISTRIBUTIONAL_LEARNING.md`
9. `V11_ADDITIONAL_MARKET_INTELLIGENCE.md`
10. `V11_MONTHLY_FORECASTING_RESEARCH.md`
11. `V11_COMPLETE_MODEL_COMPARISON.md`
12. `V11_VALIDATION_AND_SEARCH_AUDIT.md`
13. `V11_SIGNAL_DISCOVERIES.md`
14. `V11_FINAL_RESEARCH_CONCLUSIONS.md`
15. `V11_NEXT_EXPERIMENTS.md`

Preserve complete reproducible source code, feature definitions, experiment configurations, selected training dates, model parameters, predictive distributions, benchmark comparisons, failed experiments and verification tests.

Keep all V1–V10 artifacts unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Breadth discovery

Deeply investigate official equal-weight indices and concentration-related information.

Determine whether they add value to the strongest existing forecasting systems.

## Wave 2 — Training memory

Investigate historical episode diversity, training composition, overlap-aware sampling and persistent versus temporary predictive relationships.

## Wave 3 — Structural ensembles

Combine genuinely complementary breadth, rotation, volatility and historical-distribution experts.

Investigate probability and distribution improvements.

## Wave 4 — Additional information

Explore targeted derivatives, global breadth, synchronized intraday behavior and historical constituent information.

## Wave 5 — Monthly research

Investigate persistent breadth, structural risk and coherent monthly return distributions.

## Wave 6 — Falsification and synthesis

Compare all promising models across earlier, later and combined cohorts.

Challenge apparent winners.

Quantify search uncertainty.

Document new discoveries and unresolved hypotheses.

---

# FINAL EXECUTION DIRECTIVE

Do not stop after producing a research plan.

Execute the feasible experiments using our available systems.

Continue exploiting the complete Upstox, NSE, Indian-equity and global-market universe.

Be creative, but do not repeat previously unsuccessful approaches without a genuinely different hypothesis.

Use only 2025–2026 observations.

Do not deploy capital, place trades or alter live trading systems.

## CENTRAL V11 QUESTIONS

Can official equal-weight market breadth reveal predictive information that conventional cap-weighted indices conceal?

Can historical training memory preserve useful market relationships better than conventional rolling windows?

Can we distinguish persistent market relationships from temporary effects?

Can combining complementary forecasting distributions produce more consistent performance across different historical periods?

We are not simply trying to manufacture another historical accuracy record.

We are trying to discover how to extract predictive intelligence from the substantial market-data universe we already possess.

Continue researching aggressively.

Preserve scientific integrity.

**BEGIN V11 RESEARCH.**