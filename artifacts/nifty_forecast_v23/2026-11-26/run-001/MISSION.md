# NIFTY V23 — ROBUST FORECAST INTELLIGENCE, DISTRIBUTION DECOMPOSITION & MODEL UNCERTAINTY

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, international markets, derivatives, corporate disclosures, participant positioning, historical candles, databases and Python execution capabilities.

We have completed V1 through V22 of our NIFTY forecasting research.

We have accumulated an enormous archive of forecasting models, historical predictions, complete predictive distributions, market-path simulations, feature definitions, experimental results and failed hypotheses.

V22 alone preserved 75,891 weighted NIFTY forecast laws.

Despite this extensive research, original weekly and monthly directional improvements remain small, historically unstable and statistically inconclusive.

However, different models appear to contain useful information about different aspects of future market behavior.

V23 must investigate a new central hypothesis:

**Can we extract complementary information from our entire forecasting archive and construct more robust predictive distributions than any individual model provides?**

Do not simply average all previous forecasts.

Do not merely repeat previous stacking, adaptive gating or ensemble-weight optimization experiments.

Investigate forecast components, shared model errors, estimation uncertainty, complementary information and distribution construction.

Continue actively experimenting using 2025–2026 observations.

---

## PRIMARY OBJECTIVES

Retain the original objectives:

- Next five NIFTY trading sessions.
- Next 21 NIFTY trading sessions.
- Directional probability.
- Expected return.
- Median return.
- Complete predictive return distribution.

Additionally investigate:

- Forecast disagreement.
- Model uncertainty.
- Complementary predictive information.
- Shared forecast errors.
- Distribution location, scale and asymmetry.
- Tail representation.
- Robust forecast aggregation.
- Conditional market paths.
- Historical model stability.

## RESTRICTIONS

- Use only 2025–2026 market observations.
- Preserve the November 17, 2026 frozen historical vintage.
- Acquire additional completed 2026 sessions separately.
- No pre-2025 observations, warm-up histories or fitted model states.
- Preserve all V1–V22 artifacts and issued forecasts.
- No live trading, broker orders or capital deployment.
- All previously examined historical outcomes remain research-exposed.
- Do not manufacture independent statistical evidence.

---

# PHASE 1 — REPRODUCE V22 AND ESTABLISH STRONG BENCHMARKS

Read the complete V22 research index, all 17 reports, source code, experiment registry, forecast distributions and verification artifacts.

## Original weekly references

| Model | Brier | CRPS |
|---|---:|---:|
| V14 weekly parent | 0.228529 | 0.010457 |
| V18 corporate residual correction | 0.223481 | 0.010318 |
| V20 weekly direction leader | 0.221693 | 0.010274 |
| V21 asymmetry correction | 0.222129 | 0.010167 |
| V22 combined correction | 0.220133 | Recover exact law |
| V22 domestic correction | 0.220368 | 0.010121 |

## Original monthly references

| Model | Brier | CRPS |
|---|---:|---:|
| Neutral probability | 0.250000 | Recover matching law |
| V14 monthly parent | 0.245042 | 0.024989 |
| V19 positioning correction | 0.228199 | 0.024010 |
| V20 smoothed positioning | 0.228602 | 0.023786 |
| V21 aggregate positioning correction | 0.223819 | 0.023184 |
| V22 foreign-tail mixture | 0.223431 | 0.023174 |

## Monthly range references at 08:55

- Original GJR path: 0.015488 CRPS.
- India-only volatility-scaled paths: 0.014409 CRPS.
- India plus international paths: 0.014195 CRPS.

Reproduce the V22 weak-source exclusions, episode-removal sensitivities and foreign-prior placebo comparisons.

Audit the reported domestic-only weekly scores against the exact saved model identifiers.

Keep native 09:10, pre-auction 08:55, previous-evening and post-open forecasts separate.

Do not combine separate metric leaders into one fictitious forecasting system.

Deliver `V23_REPRODUCTION_AND_BENCHMARKS.md`.

---

# PHASE 2 — BUILD THE MASTER FORECAST ARCHIVE

Consolidate all accessible V1–V22 historical forecasts into a standardized research database.

## Required fields

For every forecast, preserve:

- Model identifier.
- Research version.
- Forecast origin.
- Decision timestamp.
- Information cutoff.
- Target session.
- Forecast horizon.
- Feature families.
- Training interval.
- Training eligibility.
- Model configuration hash.
- Predictive law.
- Expected return.
- Median return.
- Directional probability.
- Predictive variance.
- Quantiles.
- Realized outcome.
- Per-origin forecast losses.

Where only summary forecasts survive, label those records as incomplete.

Do not reconstruct a supposedly exact historical predictive law from an incomplete set of summary statistics.

## Critical distinction

Historical predictions may have been generated chronologically while their model specifications were selected using later research findings.

Separate:

1. Chronological historical predictions.
2. Retrospectively selected model specifications.
3. Genuine frozen prospective forecasts.
4. Late-diagnostic forecasts.
5. Invalid or unresolved forecast records.

Do not present a retrospective ensemble of later-discovered models as a strategy that could genuinely have been selected historically.

## Deduplication

Identify:

- Exact duplicate predictions.
- Affine-equivalent feature models.
- Near-identical predictive laws.
- Models sharing the same parent.
- Models differing only by minor calibration.
- Models differing only by simulation noise.

Construct a model-family registry.

Deliver `V23_MASTER_FORECAST_ARCHIVE.md`.

---

# PHASE 3 — FORECAST INFORMATION GEOMETRY

Investigate how much distinct predictive information exists across our enormous collection of models.

Thousands of model configurations may represent only a small number of genuinely different forecasting mechanisms.

## Compare models using

- Directional probability correlation.
- Expected-return correlation.
- Prediction-error correlation.
- Per-origin Brier-loss correlation.
- CRPS-loss correlation.
- Predictive quantile distances.
- Wasserstein distances between return distributions.
- Disagreement during extreme market episodes.

Construct separate similarity representations for:

- Direction.
- Return location.
- Dispersion.
- Asymmetry.
- Tail probabilities.
- Range predictions.

## Research questions

1. How many effectively distinct forecast families exist?
2. Which models make nearly identical errors?
3. Which models disagree for economically or statistically meaningful reasons?
4. Which apparent differences arise only from simulation noise?
5. Are weekly and monthly forecast families geometrically different?
6. Do corporate and positioning corrections provide genuinely distinct information?

Use training-only clustering when constructing historical forecasts.

Full-sample clustering is permitted only as explicitly labeled retrospective diagnostics.

Deliver `V23_FORECAST_INFORMATION_GEOMETRY.md`.

---

# PHASE 4 — DECOMPOSE PREDICTIVE DISTRIBUTIONS

Instead of comparing complete forecasting systems alone, investigate their individual distribution components.

## Components

A. Return location.

B. Conditional dispersion.

C. Directional probability.

D. Distribution asymmetry.

E. Tail thickness.

F. Extreme-return probabilities.

G. Temporal path shape.

## Core experiment

Determine which model family estimates each component most effectively.

For example, investigate whether:

- V18–V22 corporate corrections provide useful weekly location or asymmetry information.
- V19–V22 positioning corrections provide useful monthly location information.
- Raw IV provides useful weekly scale information.
- GJR-GARCH provides useful monthly scale information.
- Historical path resampling provides useful range and tail shape.

These are hypotheses, not predetermined assignments.

## Distribution construction

Investigate coherent location-scale transformations, standardized residual distributions, valid probability-law mixtures and monotone quantile constructions.

An independently selected probability, mean, variance and set of quantiles may not describe a mathematically possible distribution.

Never combine incompatible statistics and label them a coherent forecast.

Report whether improvements arise from:

- Location estimation.
- Dispersion estimation.
- Probability shrinkage.
- Asymmetry.
- Tail representation.
- Calibration.

Deliver `V23_DISTRIBUTION_COMPONENT_INTELLIGENCE.md`.

---

# PHASE 5 — ROBUST FORECAST AGGREGATION

Previous learned ensemble weights and adaptive gating frequently failed.

Investigate whether conservative and uncertainty-aware aggregation can improve robustness.

## Strong baseline aggregators

- Best archived individual model.
- Equal-weight model mixture.
- Equal-weight model-family mixture.
- Historical distribution mixture.
- Fixed neutral shrinkage.
- Strong previous V11–V14 ensemble methods.

## New candidate mechanisms

### A. Family-balanced aggregation

Allocate weights to distinct information families rather than individual configurations.

### B. Redundancy-aware aggregation

Reduce the influence of nearly identical predictive distributions.

### C. Robust loss-based aggregation

Investigate whether weights selected using robust historical loss estimates are more stable than weights selected using average loss alone.

### D. Distributionally robust aggregation

Investigate conservative optimization across defensibly defined training environments and plausible weight uncertainty.

### E. Bayesian model averaging

Use strongly regularized model weights and account for uncertainty about their estimation.

### F. Component-level aggregation

Combine different models' useful location, scale, asymmetry and tail information into a coherent law.

### G. Complete-law pooling

Compare linear probability-law mixtures and valid quantile pooling.

Keep joint path laws separate when marginal pooling does not preserve their dependence structure.

## Required safeguards

- Exact-copy invariance.
- Near-duplicate sensitivity.
- Training-only weight estimation.
- Matured forecast-loss enforcement.
- Strong equal-weight controls.
- Zero-weight and fixed-shrinkage controls.

Do not use the entire evaluation history to choose a supposedly operational ensemble.

Deliver `V23_ROBUST_FORECAST_AGGREGATION.md`.

---

# PHASE 6 — MODEL UNCERTAINTY AND FORECAST DISAGREEMENT

A probability forecast may be uncertain not only because future prices are uncertain, but also because we are uncertain which forecasting model is appropriate.

Investigate these separately.

## Sources of uncertainty

- Future return randomness.
- Parameter-estimation uncertainty.
- Model-specification uncertainty.
- Feature measurement uncertainty.
- Historical source availability.
- Structural instability.
- Training-period sensitivity.
- Limited effective sample size.

## Model disagreement

Research whether disagreement among distinct forecast families predicts:

- Larger forecast errors.
- Volatility expansion.
- Larger market ranges.
- Directional overconfidence.
- Tail misses.
- Distribution miscalibration.

Compare genuine model disagreement against:

- Historical volatility.
- ATM implied volatility.
- Ordinary prediction dispersion.
- Parameter uncertainty.
- Feature-distribution distance.

Previous reliability and error-warning models frequently failed.

Do not assume forecast disagreement provides useful predictive information merely because it is intuitively appealing.

## Probability uncertainty

Where justified, estimate uncertainty around the predicted directional probability.

Distinguish:

- Predicted probability of a positive return.
- Uncertainty about that probability estimate.
- Prediction intervals for future returns.

These are different quantities.

Deliver `V23_MODEL_UNCERTAINTY_AND_DISAGREEMENT.md`.

---

# PHASE 7 — STABLE PREDICTIVE RELATIONSHIPS

Investigate which information mechanisms survive changes in historical training composition.

## Candidate environment definitions

- Earlier and later historical periods.
- High and low volatility.
- Broad and concentrated market participation.
- Positive and negative recent trends.
- Different positioning states.
- Different corporate-announcement activity levels.
- Distinct global market conditions.

Any environment used operationally must be identifiable at the forecast origin.

Retrospective environment definitions may be used only for diagnostics.

## Research methods

Investigate:

- Environment-balanced estimation.
- Robust regression.
- Hierarchical parameter shrinkage.
- Stable coefficient estimation.
- Conservative worst-environment optimization.
- Leave-episode-out diagnostics.

Do not overfit a worst-case objective to extremely small historical groups.

## Required experiments

Compare each method against ordinary regularization using identical eligible histories.

Determine whether robustness improves:

- Average forecast quality.
- Cross-cohort stability.
- Worst-period performance.
- Parameter stability.
- Calibration.

Preserve the V21 monthly model's earlier improvement and later deterioration as a central failure case.

Deliver `V23_STABLE_PREDICTIVE_RELATIONSHIPS.md`.

---

# PHASE 8 — INVESTIGATE THE SHAPE OF HISTORICAL MARKET PATHS

V22 produced a promising monthly range result using volatility-scaled historical paths.

Investigate why.

## Separate the following components

1. Future volatility level.
2. Volatility evolution during the forecast window.
3. Overnight-gap behavior.
4. Intraday high-low excursions.
5. Directional persistence.
6. Return asymmetry.
7. Cross-session dependence.
8. Extreme movements.

## Mandatory experiments

Compare:

- Original GJR paths.
- Constant-volatility diffusion.
- Student-t GJR paths.
- Random India-only historical paths.
- Volatility-matched India-only paths.
- State-matched India-only paths.
- India plus international paths.
- International paths alone.
- Temporally shuffled historical paths.
- Independent daily-return resampling.
- Contiguous historical path resampling.

Use identical forecast-origin risk anchors where appropriate.

Determine whether performance improves because of historical path shape, better volatility scaling, serial dependence or simple distribution widening.

All selected historical paths must have fully completed before the forecast cutoff.

Historical donor-path volatility may be used for normalization only when that entire donor path is already known.

Do not condition simulations on future realized NIFTY volatility.

Test whether forcing every simulated path to have an identical volatility level removes genuine uncertainty about future realized risk.

Deliver `V23_HISTORICAL_PATH_SHAPE_RESEARCH.md`.

---

# PHASE 9 — INTERNATIONAL PATH INTELLIGENCE

Continue the strongest part of V22's international research.

The monthly range CRPS improvement was:

- Original GJR: 0.015488.
- India-only historical paths: 0.014409.
- Mixed-market historical paths: 0.014195.

Most of the gain came from domestic historical paths.

V23 must isolate whether international paths add meaningful information beyond the domestic alternative.

## Research questions

- Do foreign paths improve the upper range tail?
- Do they improve drawdown distributions?
- Do they improve the representation of persistent directional movements?
- Do they improve volatility-expansion probabilities?
- Do they provide useful scenarios absent from recent Indian history?

## Foreign-source quality audit

V22 reported inconsistent agreement between some foreign data sources.

Investigate:

- Price-index versus total-return mismatches.
- Currency mismatches.
- Trading-calendar differences.
- Timestamp alignment.
- Missing or stale prices.
- Vendor-specific historical discrepancies.

Use independently verified sources where feasible.

Where discrepancies remain unresolved, exclude the affected series from the strict primary test and preserve broader results as sensitivity analyses.

## Required controls

- Equal-size domestic analogue libraries.
- Equal effective episode counts.
- Random foreign paths.
- Volatility-only matching.
- Region exclusions.
- Source-quality exclusions.
- Global-episode deduplication.

Compare mixed-market paths directly against the stronger India-only path benchmark, not merely the original GJR model.

Deliver `V23_INTERNATIONAL_PATH_COMPLEMENTARITY.md`.

---

# PHASE 10 — DEVELOP BETTER ORIGINAL WEEKLY AND MONTHLY FORECASTS

Our original objective remains central.

## Weekly candidates

Investigate:

- V22 domestic distribution correction.
- Corporate-informed asymmetry.
- Family-balanced return distributions.
- Robust location estimation.
- IV-informed scale estimation.
- Complementary residual corrections.

## Monthly candidates

Investigate:

- V21 positioning correction.
- V22 foreign-tail mixture.
- Smoothed-positioning corrections.
- Robust location shrinkage.
- GJR-informed dispersion.
- Domestic historical path shapes.
- Carefully constrained foreign-path contributions.

## Required comparisons

A. Strongest archived parent.

B. Unchanged parent with ordinary shrinkage.

C. Robust complete-law mixture.

D. Component-level mixture.

E. Historically conditioned distribution.

F. Robust residual correction.

G. Uncertainty-aware distribution construction.

Do not expand candidate complexity unless a simpler mechanism demonstrates useful incremental information.

## Coherence requirements

Every predictive law must produce internally consistent:

- Up probability.
- Expected return.
- Median return.
- Endpoint quantiles.
- Prediction intervals.
- Tail probabilities.

Maintain original five-session and 21-session targets.

Do not replace the original forecasting problem with easier auxiliary targets.

Deliver `V23_ORIGINAL_HORIZON_FORECASTING.md`.

---

# PHASE 11 — IMPROVE FORECAST CALIBRATION

Investigate whether our selected forecasts are systematically overconfident or underconfident.

## Directional calibration

Evaluate:

- Brier reliability and resolution components, with appropriate finite-sample qualification.
- Log loss.
- Calibration intercept.
- Calibration slope.
- Reliability diagrams.
- Probability-bin coverage.
- Training-only probability recalibration.

## Distribution calibration

Evaluate:

- PIT diagnostics.
- Randomized PIT where discrete laws require it.
- Quantile calibration.
- Interval coverage.
- Interval width.
- Proper interval scores.
- Upper and lower tail misses.
- CRPS.

## Conditional calibration

Investigate calibration by:

- Volatility state.
- Model disagreement.
- Forecast probability.
- Positioning concentration.
- Historical analogue availability.
- Earlier and later cohorts.

Report actual sample sizes.

Avoid strong conclusions from sparse conditional groups.

Compare recalibrated laws against simple fixed shrinkage and unmodified parents.

Deliver `V23_FORECAST_CALIBRATION_RESEARCH.md`.

---

# PHASE 12 — SIMULATION PRECISION AND NUMERICAL VALIDITY

V21 found that 256 scenarios could differ from 1,024 scenarios by approximately two percentage points in estimated up probability.

Many historical improvements are small enough for simulation noise to matter.

## Required experiments

Investigate forecast stability with:

- 256 scenarios.
- 1,024 scenarios.
- 4,096 scenarios.
- 16,384 scenarios where computationally feasible.

Use multiple independent simulation seeds and common random numbers for matched comparisons.

Where a finite weighted empirical distribution exists, calculate probabilities and proper scores directly from its weights rather than unnecessarily resampling it.

## Measure

- Directional probability variation.
- Expected-return variation.
- Quantile variation.
- Brier variation.
- CRPS variation.
- Range and barrier-probability variation.

Separate numerical simulation uncertainty from statistical model uncertainty.

Do not declare a new model superior when its apparent improvement is smaller than unresolved numerical variation.

Deliver `V23_SIMULATION_PRECISION_AND_NUMERICAL_AUDIT.md`.

---

# PHASE 13 — CUMULATIVE SEARCH-RISK ANALYSIS

We have completed 22 extensive research versions.

Version-specific multiple-comparison adjustments do not eliminate the selection effects of the complete adaptive research history.

## Build a cumulative registry

Recover where feasible:

- All materially distinct model families.
- Feature configurations.
- Forecasting objectives.
- Selected winners.
- Failed experiments.
- Adaptive follow-ups.
- Repeatedly examined historical episodes.

Quantify what proportion of the historical search can actually be reconstructed.

Do not pretend the recovered registry contains experiments that were never archived.

## Representative null research

Construct manageable refit-and-reselection experiments representing the major research mechanisms.

Investigate:

- How often random features produce apparent leaderboard improvements.
- How much repeated selection can improve retrospective point scores.
- Whether robust model families remain competitive under perturbations.
- Whether apparent ensemble gains survive model-selection controls.

Clearly distinguish bounded representative null experiments from full cumulative search adjustment.

Deliver `V23_CUMULATIVE_SEARCH_RISK.md`.

---

# PHASE 14 — FALSIFICATION AND RESEARCH DISCIPLINE

Begin with no more than 12 materially distinct primary hypotheses.

Register the mechanism, target, information cutoff, parent, primary metric, negative control and computational budget.

Prioritize:

1. Forecast-family redundancy.
2. Component-level distribution construction.
3. Robust aggregation.
4. Model uncertainty.
5. Historical path shape.
6. Incremental international path information.

## Mandatory controls

- Chronological fitting.
- Fully matured forecast errors.
- Training-only transformations.
- Exact forecast-cutoff matching.
- Future-information sentinels.
- Duplicate-feature and duplicate-expert invariance.
- Delayed information.
- Block-permuted residual targets.
- Randomized model weights.
- Equal-family-weight controls.
- Strong historical distribution controls.
- Leave-month-out diagnostics.
- Leave-extreme-episode-out diagnostics.
- Dependence-aware uncertainty.

If a research mechanism fails, preserve its negative findings and investigate a genuinely different mechanism.

Do not generate thousands of minor variations merely to report a larger search.

Continue retrospective experimentation independently of prospective validation.

Deliver `V23_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 15 — COMPLETE MODEL COMPARISON

Preserve the original cohorts:

- Weekly: 173 earlier, 92 later, 265 total.
- Monthly: 141 earlier, 76 later, 217 total.

These contain only 53 and 11 non-overlapping outcome windows.

## Maintain separate leaderboards

- Weekly direction.
- Monthly direction.
- Weekly return distributions.
- Monthly return distributions.
- Robust forecast aggregation.
- Distribution-component forecasting.
- Volatility forecasting.
- Volatility expansion.
- Monthly range forecasting.
- Drawdown forecasting.
- Tail calibration.
- Cross-cohort stability.

Report matched parent comparisons, coverage, disjoint windows, episode counts, proper scores and adjusted uncertainty.

Use a Pareto frontier describing forecast quality, calibration, complexity and historical stability.

Do not force one universal winning model.

Deliver `V23_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 16 — FORWARD RESEARCH PANEL

V22 staged 15 configurations for valid morning forecast cutoffs but had issued zero new prospective forecasts at its recorded capture.

The forward research process must become operationally reliable without interrupting retrospective experimentation.

## Existing ledger

Preserve all 13 prior issues, including:

- Original V4 and V5 records.
- The resolved V4 late diagnostic.
- V19 frozen references.
- V20 frozen references.

Resolve matured forecasts only after authoritative outcomes are available.

## Frozen directional candidates

Where feasible, issue a predefined research panel including:

### Weekly

- Neutral benchmark.
- V14 parent.
- V18 corporate correction.
- V20 directional candidate.
- V22 domestic distribution candidate.

### Monthly

- Symmetric benchmark.
- V14 parent.
- V19 positioning correction.
- V20 smoothed-positioning candidate.
- V21 aggregate-positioning candidate.
- V22 foreign-tail mixture.

### Additional capabilities

- GIFT opening-gap forecast.
- Weekly ATM IV.
- Monthly GJR.
- Volatility-expansion references.
- India-only monthly historical paths.
- Mixed-market monthly historical paths.

Do not wait for V23 research completion before issuing previously frozen models if their authentic decision cutoff becomes available.

Archive exact issue timestamps, source receipts, model hashes, complete predictive laws and target dates.

If an issue cutoff has passed, record the missed issue rather than backdating a forecast.

Identify operational blockers explicitly.

Do not extend forecast targets into 2027 without authorization.

Deliver `V23_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED ARTIFACTS

Produce:

1. V23_REPRODUCTION_AND_BENCHMARKS.md
2. V23_MASTER_FORECAST_ARCHIVE.md
3. V23_FORECAST_INFORMATION_GEOMETRY.md
4. V23_DISTRIBUTION_COMPONENT_INTELLIGENCE.md
5. V23_ROBUST_FORECAST_AGGREGATION.md
6. V23_MODEL_UNCERTAINTY_AND_DISAGREEMENT.md
7. V23_STABLE_PREDICTIVE_RELATIONSHIPS.md
8. V23_HISTORICAL_PATH_SHAPE_RESEARCH.md
9. V23_INTERNATIONAL_PATH_COMPLEMENTARITY.md
10. V23_ORIGINAL_HORIZON_FORECASTING.md
11. V23_FORECAST_CALIBRATION_RESEARCH.md
12. V23_SIMULATION_PRECISION_AND_NUMERICAL_AUDIT.md
13. V23_CUMULATIVE_SEARCH_RISK.md
14. V23_VALIDATION_AND_FALSIFICATION.md
15. V23_COMPLETE_MODEL_COMPARISON.md
16. V23_FORWARD_RESEARCH_LEDGER.md
17. V23_FINAL_RESEARCH_CONCLUSIONS.md
18. V23_NEXT_EXPERIMENTS.md

Preserve complete reproducible Python code, model configurations, source hashes, experiment registries, predictive distributions, failed hypotheses and verification artifacts.

Keep all V1–V22 files unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Unlock the existing forecast archive

Reproduce V22.

Consolidate previous predictive distributions.

Identify duplicate and complementary model families.

## Wave 2 — Discover distribution-component intelligence

Investigate location, scale, asymmetry, tails and shared forecast errors.

Test robust aggregation against strong simple controls.

## Wave 3 — Investigate historical path behavior

Explain the V22 monthly range improvement.

Isolate the contribution of domestic and international path shapes.

## Wave 4 — Improve original NIFTY forecasts

Develop coherent weekly and monthly distributions.

Investigate robust estimation and calibration.

## Wave 5 — Challenge and synthesize

Audit numerical precision, model uncertainty, cumulative search exposure and cross-cohort stability.

Preserve prospective research separately.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect our existing repository, retrieve authenticated historical market observations, access available Upstox and NSE data, write Python code, develop quantitative models and execute feasible experiments.

Do not stop at producing a research plan.

Execute the research.

Continue actively exploiting the complete 2025–2026 market-data universe.

Do not import pre-2025 observations.

Do not extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V23 QUESTIONS

How many genuinely distinct predictive mechanisms have we discovered across V1–V22?

Can different models contribute useful components to one coherent predictive distribution?

Can robust forecast aggregation reduce the historical instability of our directional models?

Can we separate market uncertainty from uncertainty about the forecasting model itself?

Why do volatility-scaled historical paths improve monthly range forecasting?

Does international history contribute meaningful path information beyond domestic history?

Can we improve our original five-session and 21-session forecasts using knowledge accumulated across all twenty-two research versions?

We have spent twenty-two research versions discovering individual forecasting mechanisms.

V23 must investigate whether those mechanisms can be combined intelligently, while avoiding redundancy, overconfidence and repeated historical overfitting.

Explore creatively.

Execute meaningful experiments.

Preserve negative findings.

Do not manufacture predictive certainty.

**BEGIN V23 RESEARCH.**