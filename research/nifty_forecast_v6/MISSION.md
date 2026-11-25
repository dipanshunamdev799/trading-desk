# NIFTY V6 — DEEP SIGNAL DISCOVERY AND PREDICTIVE MODEL IMPROVEMENT

## MISSION

You are continuing our autonomous quantitative research program using 2025–2026 market data.

V1–V5 have now been completed.

V5 discovered promising retrospective weekly models based on Indian native-market internals, with directional accuracy reaching 76.09% and Brier loss improving to 0.182047.

We also identified coherent distribution models with CRPS as low as 0.009963.

**These are exploratory results, not independently validated forecasting advantages.**

Our mission for V6 is to investigate the mechanisms behind these improvements, identify genuinely informative features, test additional architectures and carefully controlled combinations, and attempt to improve weekly and monthly predictive performance.

We are deliberately continuing research on 2025–2026 data.

Do not stop experimentation merely because historical dates are already exposed.

However, never describe an exposed-history improvement as independent confirmation.

NO LIVE TRADING. NO DEPLOYMENT.

---

# PHASE 1 — REVERSE-ENGINEER THE V5 WINNERS

Read all V5 reports, source code, model configurations, per-origin predictions, feature definitions, and experiment registries.

Focus on:

- I03_nosize.
- I00.
- I01_legacy.
- I02_newindices.
- L01.
- L02.
- V4_D02_student_shrunk.
- V4_D03_residual_shrunk.
- V4_M05_lgbm.

Reproduce their historical forecasts exactly before modifying them.

## Investigate the 76.09% result

For I03_nosize, determine:

1. Which features enter the model?
2. Which features produce the largest prediction changes?
3. Which variables have stable conditional relationships with future NIFTY returns?
4. Does the model depend on specific dates or market events?
5. Are its predictions concentrated on one side of the market?
6. Does performance deteriorate in certain volatility regimes?
7. Does it primarily capture momentum, reversion, sector rotation, volatility, or another relationship?
8. Are any features redundant or unintentionally leaking future information?
9. How sensitive are results to source timestamps, missingness, preprocessing, and target alignment?
10. Does its advantage persist under reasonable structural changes?

Do not mistake model feature importance for causal influence.

### Essential forensic tests

Perform:

- Feature-family removal.
- Individual-feature removal for the most influential features.
- Grouped permutation tests respecting time dependence.
- Leave-one-month-out diagnostics.
- Leave-one-regime-out diagnostics.
- Rolling performance analysis.
- Training-window sensitivity.
- Model-parameter perturbation.
- Data-source revision sensitivity.
- Timestamp and forecast-origin alignment tests.
- Block-preserving negative controls.

Explain exactly why removing mid/small-cap inputs improved the I03 model relative to I00 in V5.

Determine whether the effect appears related to noise, redundancy, scale differences, missingness, unstable relationships, or overfitting.

Treat these explanations as hypotheses until tested.

Produce `V6_WINNER_FORENSICS.md`.

---

# PHASE 2 — DEEP INDIAN MARKET INTERNALS RESEARCH

V5's strongest directional improvements came from Indian native indices.

Investigate this family much more deeply.

## Study index relationships

Potential signals:

- NIFTY versus BANK NIFTY.
- NIFTY versus FINANCIAL SERVICES.
- NIFTY versus NIFTY 500.
- Broad indices versus sector indices.
- Defensive versus cyclical sectors.
- IT versus financial-sector leadership.
- Auto, metals, pharma, FMCG and other sectors.
- Changes in sector return dispersion.
- Short-term sector momentum versus long-term sector momentum.
- Sector momentum acceleration.
- Relative volatility among sectors.
- Sector trend synchronization.
- Leadership concentration.
- Breadth deterioration while the headline index rises.

Prioritize authentic historical index data rather than today's constituent-membership proxies.

## Look for early warning signals

Research whether patterns in sector indices precede changes in NIFTY.

Examples:

- Banks losing momentum while NIFTY remains strong.
- Several cyclical sectors weakening simultaneously.
- A small group of sectors supporting most index gains.
- Broad-market weakness preceding large-cap weakness.
- Sharp changes in correlations between sectors.
- Defensive-sector outperformance during apparent index strength.

For each hypothesis, test its incremental contribution over a simpler Indian-index model.

## Multi-scale feature engineering

Investigate:

- 1/2/3/5/10/20-session changes.
- Momentum acceleration.
- Relative strength at multiple horizons.
- Volatility-normalized divergences.
- Rolling correlations.
- Correlation breakdowns.
- Sector-return dispersion.
- Trend persistence.
- Relative drawdown.
- Distance from rolling extrema.
- Cross-index changes in market leadership.

Avoid indiscriminately adding all possible permutations.

Develop hypotheses and test them in registered batches.

---

# PHASE 3 — STUDY INFORMATION EVOLUTION

Previous research emphasized market states measured at a particular time.

V6 should investigate whether the evolution of those states is more informative.

Examples:

- Is the rate at which BANK NIFTY weakens useful?
- Does sector leadership rotation accelerate before broad-index reversals?
- Does a rapid increase in inter-sector correlations precede volatility expansion?
- Is momentum deceleration more informative than negative momentum?
- Do changes in the relationship between NIFTY and NIFTY 500 predict future index returns?

Explore:

- First differences.
- Second differences.
- Rolling slopes.
- Rolling acceleration.
- Moving-window structural changes.
- Conditional interactions.
- Event-driven transitions.
- Regime-transition probabilities.

Study whether a small number of carefully engineered dynamic features outperform larger static feature matrices.

---

# PHASE 4 — REVISIT GLOBAL MARKETS INTELLIGENTLY

V5 did not establish incremental value from adding global-market feature blocks.

Do not simply rerun the same global-plus-domestic model.

Instead, investigate why the additions failed.

Potential explanations:

- Indian market variables already reflect global information.
- Global inputs are noisy at weekly/monthly horizons.
- Feature timestamps are misaligned.
- Relationship strength changes by regime.
- Linear relationships are inadequate.
- Some global indicators predict Indian sectors rather than NIFTY directly.
- The added feature count exceeds the useful sample capacity.

Research narrower hypotheses.

For example:

1. Does Nasdaq predict Indian IT-sector returns?
2. Do crude oil and USD/INR jointly predict energy-sensitive Indian sectors?
3. Does global risk-off behavior predict Indian bank-relative performance?
4. Does rising global volatility forecast NIFTY magnitude rather than direction?
5. Are global shocks informative only when Indian market breadth is weak?

Test the intermediate relationships first, then determine whether they incrementally improve NIFTY forecasting.

Research market-specific lead-lag structures with exact availability constraints.

Compare direct global-to-NIFTY models against global-to-sector-to-NIFTY models.

Do not claim causal transmission merely because a predictive relationship appears.

---

# PHASE 5 — EXPLORE MORE MODEL ARCHITECTURES

Use the successful Indian-internals feature family as the foundation.

Evaluate controlled alternatives.

## A. Nonlinear models
- LightGBM.
- XGBoost.
- CatBoost.
- Random forests.
- Shallow boosted trees.
- Regularized generalized additive models.

## B. Statistical models
- Ridge.
- Elastic Net.
- Robust regression.
- Quantile regression.
- Bayesian regularized regression where computationally appropriate.

## C. Regime-conditioned models
- Trend-conditioned models.
- Volatility-conditioned models.
- Sector leadership regimes.
- Global risk regimes.
- Simple mixtures of experts.

## D. Temporal approaches
- Lagged feature models.
- Compact temporal convolution.
- Small sequence models when justified by sample size.

## E. Distribution forecasting
- Regularized Student-t models.
- Shrunk empirical distributions.
- Conditional residual distributions.
- Quantile-based models.
- Simple mixture distributions.

Models must be evaluated on identical origins.

Do not equate testing more algorithms with discovering more predictive information.

Preserve a small frozen reference set while treating new V6 configurations as exploratory.

---

# PHASE 6 — INVESTIGATE DIRECTION AND DISTRIBUTION SEPARATELY

V5 produced two different leads.

I03_nosize was strongest on directional classification and Brier score.

L01 was strongest on CRPS and had comparatively good interval coverage.

Determine whether they extract different information.

Investigate:

- Directional probability quality.
- Conditional expected returns.
- Return magnitude estimation.
- Distribution asymmetry.
- Tail behavior.
- Confidence-conditioned accuracy.
- Conditional probability calibration.

## Coherent integration experiments

Research whether an internally consistent conditional distribution can combine useful aspects of these systems.

Possible approaches:

- Training-only probability-aware distribution adjustment.
- Regularized mixtures of predictive distributions.
- Conditional residual distributions.
- Jointly optimized proper scoring rules.
- Distributional regression.

Any mixture weights or adjustments must be learned from historical training data available at the forecast origin.

Do not select weights using final evaluation outcomes and label that result out-of-sample.

Derive probability, mean, median, quantiles and return buckets from the same final distribution.

Compare every integrated model against I03, L01, and the strongest V4 coherent controls.

---

# PHASE 7 — RETHINK MONTHLY FORECASTING

The 21-session horizon remains the weakest part of our research.

Do not simply apply the weekly model to monthly returns.

Investigate alternative monthly forecasting structures.

### Hypothesis A: Weekly-state aggregation

Does the evolution of shorter-term forecast states help predict longer-term outcomes?

Do not multiply or compound uncalibrated weekly probabilities.

### Hypothesis B: Persistent regimes

Do persistent trends, volatility conditions or sector-leadership patterns contain more information at 21 sessions than individual short-term indicators?

### Hypothesis C: Probabilistic return distributions

Does a highly regularized monthly distribution outperform directional classifiers?

### Hypothesis D: Intermediate horizons

Research 10-session and 15-session targets as additional diagnostic horizons.

Determine whether predictability decays gradually or changes sharply with horizon.

Do not choose a new primary horizon based solely on retrospective success.

### Hypothesis E: Cross-sectional auxiliary learning

Investigate whether broader instrument panels help estimate common market-risk and volatility factors.

Do not treat stock-date observations as independent monthly NIFTY labels.

Every monthly report must clearly state that approximately four disjoint evaluation windows were available in the existing V5 comparison.

Do not manufacture narrow monthly confidence intervals.

---

# PHASE 8 — RESEARCH CONFIDENCE-CONDITIONED FORECASTING

Investigate whether the strongest weekly models make better predictions under identifiable conditions.

Evaluate:

- Probability thresholds.
- Forecast-confidence buckets.
- Agreement between models.
- Market-regime conditioning.
- Volatility conditioning.
- Directional conviction.
- Distribution uncertainty.

Measure both accuracy and coverage.

For example, if a model issues high-conviction forecasts on only 20% of origins, compare it with relevant baselines on those same origins.

Do not cherry-pick thresholds after examining evaluation outcomes.

Look for genuine conditional forecasting usefulness rather than simply maximizing headline accuracy.

---

# PHASE 9 — ADVANCED VALIDATION AND SEARCH CONTROLS

Our experiment history now contains substantial model-selection exposure.

Make that explicit in V6.

## Data boundary

Only use 2025–2026 observations.

Do not initialize indicators with pre-2025 data.

All training labels must have fully matured.

Maintain causal source timestamps.

## Evaluation

Use:

- Chronological walk-forward testing.
- Purged training and embargo rules.
- Training-only preprocessing.
- Matched-date benchmarks.
- Dependence-aware uncertainty.
- Multiple-comparison adjustments.
- Leave-month stress tests.
- Regime sensitivity.
- Block-preserving randomization tests.
- Forecast and source reconstruction tests.

Track the number of hypotheses, architectures and configurations attempted.

Do not treat the 92 weekly origins as 92 independent five-session outcomes.

Do not present small-sample monthly uncertainty as precise.

## Strong benchmark requirement

Every promising candidate must be compared against:

- I03_nosize.
- I00.
- L01.
- V4_D02_student_shrunk.
- V4_D03_residual_shrunk.
- V4_M05_lgbm.
- Relevant neutral and simple historical baselines.

Use proper matched-date comparisons.

An apparent improvement over a weak baseline is not enough to claim superiority over the prior best systems.

New models may still be retained as exploratory leads when independent significance is unavailable.

---

# PHASE 10 — BUILD A V6 RESEARCH LEADERBOARD

Rank complete systems separately from incremental feature hypotheses.

For each system, report:

- Forecast horizon.
- Feature family.
- Model architecture.
- Number of origins.
- Disjoint-window count.
- Effective sample-size estimate.
- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- Return MAE and RMSE.
- 50% and 80% interval coverage.
- Interval width.
- Stability across time.
- Leave-month sensitivity.
- Improvement over V5 and V4 controls.
- Statistical uncertainty.
- Leakage risk.
- Research status.

Do not use a custom ranking score as a substitute for proper-score comparisons or statistical evidence.

For each new input family, separately quantify its incremental contribution over its immediate parent system.

Preserve failed experiments.

---

# PHASE 11 — REQUIRED OUTPUTS

Create:

1. `V6_WINNER_FORENSICS.md`
2. `V6_INDIAN_INTERNALS_DEEP_DIVE.md`
3. `V6_MARKET_STATE_EVOLUTION.md`
4. `V6_GLOBAL_INCREMENTAL_RESEARCH.md`
5. `V6_MODEL_ARCHITECTURES.md`
6. `V6_COHERENT_DISTRIBUTIONS.md`
7. `V6_MONTHLY_RESEARCH.md`
8. `V6_CONDITIONAL_FORECASTING.md`
9. `V6_VALIDATION_AND_LEAKAGE_AUDIT.md`
10. `V6_COMPLETE_MODEL_COMPARISON.md`
11. `V6_SIGNAL_RANKING.md`
12. `V6_FINAL_RESEARCH_DECISION.md`
13. `V6_NEXT_EXPERIMENTS.md`

Preserve reproducible Python scripts, frozen configurations, feature matrices, model outputs, and per-origin predictions.

Keep all V1–V5 artifacts unchanged.

Do not modify the frozen V4 prospective ledger.

Any new V6 forward snapshots must have their own timestamps, versions and research-only status.

---

# EXECUTION DIRECTIVE

Execute the research. Do not merely write a plan.

Begin by reproducing and explaining I03_nosize, I00 and L01.

Then expand into deeper native-market relationships, feature evolution, conditional signals, distribution forecasting and alternative architectures.

Use existing Upstox and global-market datasets wherever they are historically valid.

Pursue promising hypotheses even when they are not statistically conclusive, but record their limitations honestly.

Do not force a winner.

Do not deploy capital or place trades.

Do not extend beyond the agreed 2025–2026 observations.

## FINAL OBJECTIVE

We are trying to understand **what information available today can help predict NIFTY's market behavior over the next week and month**.

V5 suggests that relationships between Indian indices may contain information that traditional NIFTY technical indicators miss.

Investigate that finding deeply.

Determine which signals are responsible.

Find out whether those signals can be improved, combined, or modeled differently.

Continue experimenting with the data we have.

**Deliver discoveries, reproducible evidence, failure diagnoses, and the strongest possible exploratory forecasting candidates—not unsupported claims of predictive certainty.**

BEGIN V6 RESEARCH.