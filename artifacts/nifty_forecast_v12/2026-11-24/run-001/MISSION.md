# NIFTY V12 — MARKET-IMPLIED INTELLIGENCE, EXPECTATION DISCOVERY & STRUCTURAL FORECASTING

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE historical archives, Indian equities, global markets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V11 of our NIFTY forecasting research.

We have extensively investigated:

- Technical indicators.
- Indian market internals.
- Sector rotation.
- Global-market relationships.
- Feature compression.
- Machine learning.
- Adaptive forecasting.
- Market regimes.
- Training-data composition.
- Cross-sectional learning.
- Overlapping-label estimation.
- Equal-weight market breadth.
- Structural forecasting ensembles.

Our historical forecasting results have improved, but no independently validated predictive edge exists.

**We are deliberately continuing research using 2025–2026 observations.**

V12 must investigate a substantially different source of predictive intelligence:

**What does the market itself imply about its future behavior, and can differences between market-implied expectations, statistical expectations and observed market structure improve our forecasts?**

Do not simply repeat the previous eleven research versions with additional hyperparameters.

## PRIMARY OBJECTIVES

Forecast NIFTY over:

- The next five trading sessions.
- The next 21 trading sessions.

Produce research into:

- Directional probabilities.
- Expected and median returns.
- Full conditional return distributions.
- Return magnitude.
- Volatility.
- Distribution asymmetry.
- Tail probabilities.
- Forecast uncertainty.

Secondary horizons are permitted for mechanism discovery.

Use only 2025–2026 observations.

Preserve all existing research artifacts.

No live trading, broker orders or capital deployment.

---

# PHASE 1 — REPRODUCE V11 AND ESTABLISH THE RESEARCH BASELINE

Read the complete V11 research index, reports, model configurations, experiment registry, full-law archive and per-origin predictions.

Reproduce the strongest reference systems.

## Combined weekly benchmarks

| System | Brier | CRPS |
|---|---:|---:|
| Historical distribution | 0.259048 | 0.011340 |
| V9 cluster-balanced rotation | 0.236386 | 0.011775 |
| V10 structural blend | 0.236181 | 0.011043 |
| V10 historical shrinkage | 0.242366 | 0.010892 |
| V11 native disjoint phase zero | 0.231728 | 0.011001 |
| V11 breadth-augmented structural mixture | 0.236138 | 0.010960 |
| V11 ensemble excluding base rotation | 0.244333 | 0.010777 |

Also preserve:

- V11 later-cohort Brier leader: 0.156795.
- V11 later-cohort CRPS leader: 0.009262.
- V8 protected weekly leaders.
- V11 official-breadth additions to strong parent models.
- V11 alternative disjoint-phase fits.
- Earlier, later and combined training-memory results.
- V11 monthly symmetric benchmark: Brier 0.250000 and CRPS 0.025420.

Recover exact model IDs and configurations from the repository.

Do not infer implementations from their descriptive names.

Preserve V1–V11 artifacts and frozen predictions.

Create an isolated V12 workspace.

Deliver `V12_REPRODUCTION_AND_BASELINES.md`.

---

# PHASE 2 — AUDIT THE COMPLETE HISTORICAL OPTIONS UNIVERSE

This is the highest-priority new information investigation.

We have authenticated historical NSE derivatives archives covering substantial portions of 2025–2026.

Investigate whether those records support reconstructing historical option-implied market expectations.

## 2.1 Historical data inventory

Audit available NIFTY option records for:

- Trading date.
- Expiration date.
- Strike price.
- Call or put designation.
- Open, high, low and close.
- Settlement price.
- Traded volume.
- Open interest.
- Contract identifiers.
- Lot size.
- Corresponding futures prices.
- Underlying index closes.
- Bid/ask observations, where genuinely archived.
- Relevant interest-rate information.

Determine actual data availability and quality.

Do not assume that historical bid/ask quotes, IV surfaces or Greeks exist.

## 2.2 Historical price quality

Identify:

- Stale option prices.
- Zero-volume contracts.
- Missing strikes.
- Illiquid wings.
- Inconsistent call/put pairs.
- Settlement-versus-traded-price differences.
- Expiry effects.
- Contract changes.
- Cross-contract timing differences.
- Potential arbitrage inconsistencies caused by nonsynchronous observations.

Distinguish executable market quotes from end-of-day traded or settlement prices.

Do not interpret settlement prices as guaranteed tradable prices.

## 2.3 Availability timing

Determine when historical derivatives archives could reasonably have been available.

Use conservative, documented delays where original receipt timestamps are unavailable.

Ensure every forecast uses information available before its decision cutoff.

Do not use the same session's derivatives close for a forecast issued before that session completed.

Deliver `V12_OPTIONS_DATA_AND_AVAILABILITY.md`.

---

# PHASE 3 — RECONSTRUCT OPTION-IMPLIED MARKET EXPECTATIONS

Investigate whether the historical option surface supports extracting meaningful forward-looking information.

## Track A: Implied forward prices

Research forward-price estimates using:

- Actual corresponding futures contracts.
- Put-call parity.
- Multiple near-ATM strike pairs.
- Robust aggregation across liquid strikes.

Compare futures-implied and option-implied forward estimates.

Account for discounting, carry, expiry and source-timing assumptions.

Where funding or dividend information is unavailable, disclose approximation limitations.

Do not interpret the futures premium as a direct forecast of actual expected spot returns.

## Track B: Historical implied volatility

Where prices and contract information permit, reconstruct implied volatility using an appropriate pricing framework.

Research:

- Near-ATM implied volatility.
- Call/put differences.
- Term structure.
- Volatility skew.
- Downside versus upside implied volatility.
- Volatility curvature.
- Changes in implied volatility.
- Implied-versus-realized volatility.

Reject invalid solutions.

Record the fraction of strikes and dates where reconstruction is reliable.

Do not fabricate IV observations to fill missing historical surfaces.

## Track C: Option-implied return distributions

Where strike coverage and price quality are sufficient, investigate recovery of risk-neutral endpoint distributions using:

- Vertical spread relationships.
- Convex option-price curves.
- Breeden–Litzenberger density estimation.
- Arbitrage-constrained interpolation.
- Regularized implied-volatility surfaces.
- Robust parametric density approximations.

Ensure nonnegative probability mass and correct normalization.

Measure sensitivity to strike truncation, noisy prices, smoothing and tail extrapolation.

Distinguish directly supported strike regions from extrapolated tails.

### Critical requirement

An option-implied risk-neutral distribution is **not** automatically a real-world predictive distribution.

Do not present risk-neutral probabilities as calibrated probabilities of future NIFTY movements.

Risk premiums, liquidity, hedging demand and other factors may cause differences.

If historical prices cannot support reliable full-density reconstruction, retain simpler observable quantities such as straddle cost, skew proxies and vertical-spread information.

Do not force a synthetic distribution from inadequate data.

Deliver `V12_OPTION_IMPLIED_DISTRIBUTIONS.md`.

---

# PHASE 4 — MAP MARKET EXPECTATIONS TO OUR FORECAST HORIZONS

Our primary targets are five and 21 actual trading sessions.

Listed option expiries will not always align exactly with those endpoints.

Investigate defensible methods for handling this mismatch.

Compare:

- Naturally aligned expiry subsets.
- Nearest available maturity.
- Bracketing expiries.
- Total implied variance interpolation where appropriate.
- Maturity-normalized risk measures.
- Term-structure representations.

Do not linearly interpolate entire probability distributions without examining the mathematical implications.

Do not assume that interpolating implied variance identifies a complete future return distribution.

Keep naturally aligned comparisons separate from approximated-horizon comparisons.

Report actual expiration dates, forecast endpoints and maturity differences.

Investigate whether shorter or longer option maturities provide useful information about the desired forecast horizon.

Deliver `V12_HORIZON_AND_EXPIRY_ALIGNMENT.md`.

---

# PHASE 5 — EXPECTATIONS VERSUS REALITY

This is the central predictive hypothesis of V12.

The options and futures markets may contain forward-looking information, but their prices also reflect risk premiums and hedging behavior.

Investigate whether the relationship between market-implied expectations and subsequently realized outcomes can be learned.

## Research A: Market-priced risk versus realized risk

Compare:

- Implied volatility versus future realized volatility.
- Straddle-implied movement versus actual movement.
- Downside skew versus realized negative-return frequency.
- Implied tail risk versus actual tail frequency.
- Changes in implied risk versus subsequent returns.
- Term-structure changes versus subsequent volatility.

Estimate all mappings causally.

Do not normalize historical features using future realized volatility.

## Research B: Statistical versus market-implied distributions

Compare complete statistical forecasting distributions against market-implied distributions on matched origins.

Investigate disagreements in:

- Location.
- Dispersion.
- Skewness.
- Tail behavior.
- Probability of positive returns.
- Expected absolute movement.
- Distribution quantiles.

Determine whether these disagreements contain useful predictive information.

## Research C: Risk-neutral to physical distribution mappings

Where data quality permits, investigate simple, strongly regularized adjustments such as:

- Location shifts.
- Scale adjustments.
- Probability tilting.
- Historical calibration mappings.
- Risk-premium-conditioned adjustments.
- Mixtures of statistical and market-implied distributions.

Learn adjustments from fully matured historical outcomes only.

Preserve probability normalization and mathematical coherence.

Compare against:

1. Unadjusted option-implied diagnostics.
2. Historical return distributions.
3. V11 statistical forecasts.
4. Simple fixed mixtures.
5. Training-only calibrated mixtures.

Do not use risk-neutral probabilities as evidence of actual return probabilities without empirical evaluation.

Deliver `V12_EXPECTATION_VS_REALITY.md`.

---

# PHASE 6 — CASH, FUTURES AND OPTIONS MARKET DISAGREEMENT

Investigate whether disagreement across different market instruments contains useful information.

Potential relationships:

- Cash-market strength versus futures basis.
- Financial-sector rotation versus option skew.
- Broad-market breadth versus implied volatility.
- Futures positioning versus sector participation.
- Equity-index momentum versus changes in option-implied movement.
- Market concentration versus downside pricing.
- ETF activity versus changes in market-priced risk.

Research the joint state of these markets rather than adding their raw feature blocks independently.

## Candidate hypotheses

1. Strong cash-market momentum combined with deteriorating derivatives conditions predicts different outcomes from ordinary momentum.

2. Improving breadth combined with declining market-priced downside risk predicts a different return distribution from improving breadth alone.

3. Unusual futures and options disagreement contains more information about volatility or magnitude than direction.

4. Implied volatility changes have different predictive value under broad and narrow market leadership.

5. Domestic sector rotation provides directional context while derivatives provide distribution-scale information.

Test these as hypotheses, not assumed trading rules.

Use matched parent-model comparisons.

Deliver `V12_CROSS_INSTRUMENT_DISAGREEMENT.md`.

---

# PHASE 7 — EVENT-CONDITIONED PREDICTABILITY

Previous experiments largely treated each market session as another forecasting observation.

Investigate whether certain identifiable market events create different forecasting conditions.

## Event categories

- Weekly or monthly derivative expiry.
- Futures rollover.
- Verified index rebalancing.
- Large preceding index movements.
- Extreme sector rotation.
- Sharp breadth deterioration.
- Large changes in implied volatility.
- Unusually large overnight global-market movements.
- RBI policy announcements.
- Federal Reserve policy announcements.
- Other verified scheduled macroeconomic events.

Only use event dates and information whose historical availability can be established.

Do not fabricate historical economic surprise data.

Distinguish:

- Events known in advance.
- Events already observed at the forecast origin.
- Events identifiable only retrospectively.

## Research questions

- Does forecasting performance change around specific event types?
- Do market relationships become stronger after large shocks?
- Are volatility forecasts more useful around expiry or policy events?
- Does financial-sector rotation become more informative after unusual market moves?
- Does option-implied information improve forecasts around scheduled events?

Use training-defined event thresholds.

Compare event-conditioned models with event-conditioned simple baselines.

Report coverage, event counts, disjoint outcome counts and uncertainty.

Avoid creating tiny event subgroups merely to obtain unusually high accuracy.

Deliver `V12_EVENT_CONDITIONED_FORECASTING.md`.

---

# PHASE 8 — PHASE-INVARIANT AND OVERLAP-AWARE LEARNING

V11's best combined weekly Brier came from the native disjoint phase-zero model.

However, alternative phases produced different results.

Investigate whether this advantage arises from reduced overlap, historical sample composition or favorable phase selection.

## Required experiments

For the weekly horizon, evaluate all five deterministic disjoint training phases.

For the monthly horizon, evaluate all 21 phases where adequate matured labels exist.

Use a fixed historical calendar anchor.

Do not choose the phase that happens to perform best on the final evaluation dates.

Compare:

- Individual phases.
- Equal-weight phase ensembles.
- Complete-law phase mixtures.
- Regularized phase pooling.
- Block aggregation.
- Overlap-weighted fitting.
- Shared parameters across phases.
- Phase-balanced historical training samples.

Investigate whether pooling parameters can retain information across phases without restoring the same degree of overlapping-target redundancy.

## Training-memory integration

Combine overlap-aware methods with:

- Spread training dates.
- Historical episode diversity.
- Expanding history.
- Fixed-budget training.
- Random historical block controls.

Match nominal training counts and overlap geometry where feasible.

Keep training-date composition and overlap effects analytically separate.

Different phases do not constitute independent datasets.

Deliver `V12_PHASE_INVARIANT_LEARNING.md`.

---

# PHASE 9 — FORECAST INFORMATION DECOMPOSITION

V11 found experts whose prediction-error correlation reached 0.994.

Adding a new expert may contribute almost no distinct forecasting information.

Develop a systematic framework for measuring information redundancy at the forecast level.

## Research A: Expert similarity

Measure:

- Probability correlation.
- Return-forecast correlation.
- Distribution similarity.
- Forecast-error correlation.
- Shared failure periods.
- Conditional disagreement.

Investigate whether apparently different models are effectively learning the same underlying market factor.

## Research B: Marginal expert contribution

For every candidate expert, evaluate:

- Standalone predictive quality.
- Incremental contribution to a fixed ensemble.
- Leave-one-expert-out performance.
- Contribution to Brier.
- Contribution to CRPS.
- Contribution to calibration.
- Contribution across earlier and later periods.

## Research C: Ensemble duplication invariance

Investigate whether an ensemble can be constructed such that adding an exact copy of an existing expert does not arbitrarily change the final predictive distribution.

Test:

- Canonical expert deduplication.
- Similarity-cluster weighting.
- Group-balanced mixtures.
- Equal weighting across distinct forecasting mechanisms.
- Regularized stacking after expert deduplication.

Unlike exact copies, correlated but distinct experts may contain additional information.

Do not automatically discard economically distinct models merely because their forecasts are correlated.

Deliver `V12_FORECAST_INFORMATION_DECOMPOSITION.md`.

---

# PHASE 10 — USE THE FULL MARKET-DATA UNIVERSE TO FIND COMPLEMENTARY INFORMATION

Continue exploring Upstox, NSE and available global-market data.

Focus on discovering information that addresses weaknesses in existing forecasts.

## Domestic direction

Investigate:

- Official equal-weight breadth.
- Financial-sector rotation.
- Market structure.
- Leadership concentration.
- Sector residual returns.

## Market-priced uncertainty

Investigate:

- Option-implied volatility.
- Straddles.
- Skew.
- Futures curve structure.
- Market-implied tail measures.

## Realized market risk

Investigate:

- Intraday realized volatility.
- Cross-sector volatility.
- Return dispersion.
- Correlation transitions.
- ETF activity.

## External market conditions

Investigate:

- Global equity breadth.
- Global volatility.
- Currency risk.
- Interest rates.
- Oil and commodities.
- Cross-market divergences.

Instead of assigning every information source the task of forecasting direction, investigate its most appropriate role.

For example:

- Breadth may help estimate return location.
- Options may help estimate conditional scale.
- Global volatility may help estimate uncertainty.
- Sector rotation may help estimate directional asymmetry.

These are research hypotheses.

Each proposed information source must demonstrate incremental value against the strongest appropriate parent model.

Deliver `V12_COMPLEMENTARY_MARKET_INFORMATION.md`.

---

# PHASE 11 — BUILD MARKET-INFORMED COHERENT FORECASTING DISTRIBUTIONS

Construct candidate distributions using complementary information.

Research the following systems.

## Candidate A: Statistical baseline

The strongest existing V11 structural return-distribution model.

## Candidate B: Market-priced scale

Statistical return location combined with a causally calibrated measure of option-implied risk.

## Candidate C: Breadth and rotation distribution

Domestic market structure determines location and potentially asymmetry, while volatility and derivatives determine scale.

## Candidate D: Market-statistical mixture

A coherent mixture of statistical and appropriately adjusted market-implied distributions.

## Candidate E: Phase-balanced structural ensemble

An ensemble constructed from overlap-aware statistical models and distinct market-implied information.

## Candidate F: Historical fallback mixture

A complete predictive distribution incorporating historical shrinkage to control estimation instability.

These are candidate research architectures, not predetermined winners.

Investigate simple fixed combinations before introducing learned weights.

Every complete law must consistently produce:

- Probability of a positive return.
- Expected return.
- Median return.
- Return quantiles.
- Expected NIFTY endpoint.
- Return-bucket probabilities.
- Central 50% and 80% intervals.
- Tail probabilities supported by the law.

Keep endpoint-return risk separate from maximum adverse excursion and realized path volatility.

Deliver `V12_MARKET_INFORMED_DISTRIBUTIONS.md`.

---

# PHASE 12 — MONTHLY FORECASTING THROUGH MARKET-PRICED EXPECTATIONS

Monthly forecasting remains the most difficult problem.

The combined monthly evaluation contains 217 rolling origins and only 11 disjoint outcomes.

Previous smoothed-state models achieved impressive retrospective directional accuracy but failed important placebo tests.

V12 must investigate whether market-implied information provides a different source of monthly predictability.

Research:

- Longer-dated implied volatility.
- Monthly option skew.
- Volatility term structure.
- Futures curve dynamics.
- Persistent breadth divergence.
- Slow sector leadership.
- Implied-versus-realized volatility.
- Risk-premium adjustments.
- Conditional location-scale models.
- Market-informed historical distribution mixtures.

Compare against the strong symmetric reference:

- Brier: 0.250000.
- CRPS: 0.025420.

Evaluate whether market-implied information improves:

1. Direction.
2. Return magnitude.
3. Volatility.
4. Distribution calibration.
5. Tail probabilities.

A model that improves volatility prediction without improving direction may still provide a useful research discovery.

Do not claim monthly directional superiority on the basis of isolated favorable periods.

Deliver `V12_MONTHLY_MARKET_EXPECTATIONS.md`.

---

# PHASE 13 — CUMULATIVE RESEARCH SYNTHESIS

We have now completed eleven substantial research versions.

Before conducting another enormous model search, extract the scientific knowledge already accumulated.

Build a consolidated hypothesis registry covering:

- Native market internals.
- Financial-sector rotation.
- Defensive-sector redundancy.
- Global-market relationships.
- Derivatives information.
- ETF activity.
- Intraday structure.
- Feature invariance.
- Training-memory composition.
- Overlapping-label estimation.
- Official breadth.
- Structural ensembles.
- Monthly state persistence.

For every hypothesis, classify:

- What was tested.
- Which implementation succeeded or failed.
- Which historical cohorts supported it.
- Which falsification tests it survived.
- Which falsification tests it failed.
- Whether it improved a strong or weak baseline.
- Whether subsequent research replicated the result.
- What remains genuinely unexplored.

Avoid repeating an unsuccessful implementation unless the new experiment introduces a materially different mechanism.

Preserve methodological achievements separately from predictive results.

Deliver `V12_CUMULATIVE_KNOWLEDGE_BASE.md`.

---

# PHASE 14 — VALIDATION AND FALSIFICATION

Maintain all existing research safeguards.

## Core requirements

- Chronological fitting.
- Matured labels only.
- Point-in-time data alignment.
- Training-only preprocessing.
- Purging and embargoes.
- Exact-copy invariance.
- Matched-origin comparisons.
- Dependence-aware uncertainty.
- Search-adjusted inference.
- Complete experiment accounting.

## New market-implied controls

- Lagged option-surface information.
- Shifted training-state controls.
- Block-permuted derivatives features.
- Realized-volatility-only controls.
- Straddle-only controls.
- Synthetic noise features with comparable dimensions.
- Alternative liquidity filters.
- Alternative option-price reconstruction methods.
- Maturity-alignment sensitivity.
- Tail-extrapolation sensitivity.
- Source-timestamp perturbations.

Investigate whether apparent gains survive the removal of exact option-surface timing.

If shifted or delayed information performs equally well, investigate persistence or model-selection explanations.

For all major research families, run representative refit-and-reselection null experiments where computationally feasible.

Do not imply that a bounded V12 search adjustment accounts for all previous V1–V12 adaptive experimentation.

Deliver `V12_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 15 — EVALUATION AND LEADERBOARD

Preserve the frozen November 17, 2026 vintage.

Use the established historical reference cohorts:

- Earlier weekly: 173 origins.
- Later weekly: 92 origins.
- Combined weekly: 265 origins.
- Earlier monthly: 141 origins.
- Later monthly: 76 origins.
- Combined monthly: 217 origins.

Option-history eligibility may reduce available origins.

When this happens, recompute all relevant benchmarks on the identical subset.

Never compare an option model evaluated on a favorable subset against a full-cohort baseline.

Separately acquire additional completed 2026 observations available at execution time.

Do not overwrite existing forecasts or historical source versions.

## Required metrics

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- MAE and RMSE.
- Quantile losses.
- Interval coverage.
- Interval width.
- Return-bucket calibration.
- Tail calibration.
- Disjoint outcome count.
- Effective sample diagnostics.
- Search-adjusted uncertainty.

Maintain separate rankings for:

1. Weekly probability forecasts.
2. Weekly return distributions.
3. Combined-cohort robustness.
4. Monthly probability forecasts.
5. Monthly return distributions.
6. Volatility and movement-magnitude forecasts.
7. Incremental value of market-implied information.

Do not force a single universal winner.

Deliver `V12_COMPLETE_COMPARISON.md`.

---

# PHASE 16 — REQUIRED RESEARCH OUTPUTS

Produce:

1. `V12_REPRODUCTION_AND_BASELINES.md`
2. `V12_OPTIONS_DATA_AND_AVAILABILITY.md`
3. `V12_OPTION_IMPLIED_DISTRIBUTIONS.md`
4. `V12_HORIZON_AND_EXPIRY_ALIGNMENT.md`
5. `V12_EXPECTATION_VS_REALITY.md`
6. `V12_CROSS_INSTRUMENT_DISAGREEMENT.md`
7. `V12_EVENT_CONDITIONED_FORECASTING.md`
8. `V12_PHASE_INVARIANT_LEARNING.md`
9. `V12_FORECAST_INFORMATION_DECOMPOSITION.md`
10. `V12_COMPLEMENTARY_MARKET_INFORMATION.md`
11. `V12_MARKET_INFORMED_DISTRIBUTIONS.md`
12. `V12_MONTHLY_MARKET_EXPECTATIONS.md`
13. `V12_CUMULATIVE_KNOWLEDGE_BASE.md`
14. `V12_VALIDATION_AND_FALSIFICATION.md`
15. `V12_COMPLETE_COMPARISON.md`
16. `V12_FINAL_RESEARCH_CONCLUSIONS.md`
17. `V12_NEXT_EXPERIMENTS.md`

Preserve complete reproducible source code, historical option-price reconstructions, surface-quality diagnostics, configurations, predictive distributions, benchmark comparisons, failed experiments and verification results.

Keep all V1–V11 artifacts unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Market expectations

Audit historical option data.

Determine whether credible historical implied volatility and risk-neutral distributions can be reconstructed.

If not, identify the strongest defensible alternatives.

## Wave 2 — Predictive information

Investigate market-priced expectations versus realized outcomes.

Test disagreement between cash, futures, options, sector rotation and breadth.

## Wave 3 — Statistical improvements

Investigate phase-invariant learning, overlapping-label treatment, historical training diversity and expert deduplication.

## Wave 4 — Integrated forecasting

Construct coherent market-informed distributions.

Research weekly and monthly horizons independently.

## Wave 5 — Falsification and synthesis

Compare all promising mechanisms against strong V11 references.

Investigate source quality, time alignment, placebo performance and temporal stability.

Update the cumulative research knowledge base.

Allocate additional research effort to productive hypotheses.

Do not spend most of the experiment budget repeating previous architectures.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing research environment, retrieve authenticated historical market observations, write Python code, reconstruct historical market measures, develop models and execute experiments.

Do not stop at producing a research plan.

Execute everything feasible with available data and computational resources.

Continue actively exploring 2025–2026 market observations.

Do not silently import pre-2025 data.

Do not extend beyond 2026.

Do not place trades or deploy capital.

## CENTRAL V12 RESEARCH QUESTIONS

**What future market behavior is implied by actual historical option prices?**

**Can the difference between market-implied expectations and statistical expectations help forecast NIFTY?**

**Can domestic breadth and financial-sector rotation supply directional information while derivatives supply uncertainty and distribution information?**

**Can we construct forecasting ensembles that combine genuinely distinct information rather than counting the same signal repeatedly?**

We have spent eleven versions learning from historical market behavior.

V12 must investigate whether we can additionally learn from the market's own forward-looking pricing of risk and uncertainty.

Explore aggressively.

Challenge existing assumptions.

Retain negative findings.

Do not manufacture predictive certainty.

**BEGIN V12 RESEARCH.**