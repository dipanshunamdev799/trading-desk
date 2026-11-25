# NIFTY V9 — ADAPTIVE MARKET INTELLIGENCE, PREDICTABILITY DISCOVERY & REGIME-AWARE FORECASTING

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research environment, Upstox integrations, NSE archives, global-market datasets, Indian equities, derivatives, ETFs, historical candles, databases, and Python execution capabilities.

We have completed eight versions of NIFTY forecasting research.

We have progressively improved selected retrospective weekly forecasting results:

- V4 Brier: 0.206257
- V5 Brier: 0.182047
- V6 Brier: 0.169803
- V7 Brier: 0.162145
- V8 Brier: 0.159504

V8 also achieved a weekly CRPS of 0.009453.

However, we have discovered an important limitation: the models that perform well in the later historical period perform poorly in an earlier evaluation cohort.

We have not established independently validated forecasting superiority.

**We are not stopping research.**

V9 must investigate why predictive relationships appear to change, whether those changes can be identified in advance, and whether the extensive market-data universe can help build a more adaptable forecasting system.

Continue exploring new approaches rather than merely optimizing the same historical model.

### Primary forecasting objectives

- NIFTY return over the next five trading sessions.
- NIFTY return over the next 21 trading sessions.
- Directional probabilities.
- Expected and median returns.
- Coherent conditional return distributions.
- Forecast uncertainty.
- Identifiable conditions under which forecasting models become more or less useful.

### Research scope

Use only 2025–2026 observations.

No pre-2025 market data, fitted parameters, indicator initialization, or training labels.

No live trading or capital deployment.

Retrospective exploration is explicitly authorized. Independent validation must not be fabricated.

---

# PHASE 1 — REPRODUCE AND UNDERSTAND V8

Read the complete V8 research index, all 17 reports, source code, feature definitions, saved distributions, model artifacts, experiment registry, and verification results.

Reproduce the following systems:

| Model | Weekly Brier | Weekly CRPS |
|---|---:|---:|
| V7 domestic rotation | 0.162145 | 0.009927 |
| V7 cluster-balanced Elastic Net | 0.184134 | 0.009665 |
| V8 residualized rotation | 0.159504 | 0.009852 |
| V8 structure levels | 0.161756 | 0.009587 |
| V8 structure changes | 0.162875 | 0.009472 |
| V8 earlier-cutoff structure | 0.163355 | 0.009453 |
| V8 cluster-balanced rotation | 0.164496 | 0.009499 |

Recover their exact model IDs and configurations from the repository. Do not infer implementation details from these descriptive names.

Also reproduce:

- Earlier historical-cohort results.
- Monthly smoothed-state results.
- Shifted-state falsification controls.
- Training-window sensitivity.
- Duplicate-invariance tests.
- ETF and global incremental experiments.

Preserve every earlier artifact and frozen forecast.

Keep V9 in a separate versioned workspace.

---

# PHASE 2 — SOLVE THE EARLIER-VERSUS-LATER PERFORMANCE MYSTERY

This is the highest-priority research task.

V8's earlier weekly evaluation contained 173 origins.

The full rotation model achieved:

- Brier: 0.299536
- CRPS: 0.013243

The matched historical benchmark achieved:

- Brier: 0.259447
- CRPS: 0.010878

Yet the later weekly cohort produced much stronger rotation-model results.

Determine why.

## Hypothesis A: Insufficient training history

Investigate whether the earlier model simply lacked sufficient matured training observations.

Construct learning curves using controlled training-history lengths:

- 85 observations.
- 126 observations.
- 189 observations.
- 252 observations.
- 300 observations.
- Maximum available expanding history.

Use only eligible lengths at each origin.

Compare different training lengths on identical later evaluation dates wherever possible.

Do not attribute differences to market regimes before controlling for sample size.

## Hypothesis B: Changing market relationships

Investigate whether the relationship between sector rotation and future NIFTY returns changed during 2025–2026.

Measure:

- Rolling coefficient behavior.
- Changing predictive signs.
- Rolling residual correlations.
- Changes in feature importance.
- Sector leadership changes.
- Conditional return distributions.
- Structural breaks in forecasting errors.

Distinguish causal online change detection from retrospective break identification.

A break identified using future outcomes cannot serve as a historical real-time trading signal.

## Hypothesis C: Changes in market conditions

Compare earlier and later cohorts using:

- Trend strength.
- Realized volatility.
- Market breadth.
- Financial-sector leadership.
- Defensive/cyclical leadership.
- Sector dispersion.
- Global risk conditions.
- Liquidity.
- Cross-market correlation.
- Return autocorrelation.
- Momentum and mean-reversion behavior.

Determine whether the same model behaves differently under comparable market conditions.

## Hypothesis D: Differences in experimental design

Audit whether performance differences arise from:

- Training eligibility.
- Feature warm-up.
- Residual-distribution estimation.
- Inner-validation length.
- Regularization.
- Missing-data treatment.
- Feature availability.
- Label-maturity requirements.
- Forecast-origin timing.

Perform matched experimental-design comparisons.

Do not compare an 85-observation earlier model against a 300-observation later model and attribute the entire difference to changing market behavior.

### Required outcome

Provide a quantitative decomposition where possible of how much performance deterioration can be associated with training history, market conditions, feature representation, and experimental design.

If the effects cannot be separated reliably, explicitly report the identification limitation.

Deliver `V9_TEMPORAL_GENERALIZATION_DIAGNOSIS.md`.

---

# PHASE 3 — DISCOVER WHEN NIFTY IS PREDICTABLE

Instead of assuming every market state is equally predictable, investigate whether forecast quality itself can be estimated.

Develop a research framework that asks:

**Given today's market conditions, which forecasting approach is most likely to be useful over the next five or 21 sessions?**

## Candidate predictability indicators

Investigate:

- Sector synchronization.
- Financial-sector divergence.
- Rotation persistence.
- Market concentration.
- Trend consistency.
- Market breadth.
- Volatility stability.
- Cross-market correlation.
- Disagreement between forecasting models.
- Similarity to historical training states.
- Recent resolved forecasting errors.
- Feature-distribution changes.
- Coefficient stability.
- Distance from familiar market conditions.

## Define predictability correctly

Potential supervised targets include:

- Future Brier loss of a frozen model.
- Future CRPS loss.
- Whether a model beats a fixed baseline on an origin.
- Whether the model's directional prediction is correct.
- Whether the realized return falls within its predictive interval.

These targets must come from genuine chronological historical predictions, not in-sample fitted values.

A forecast-error label becomes available only after its full horizon resolves.

Do not accidentally train a reliability model on unresolved forecast errors.

## Selective forecasting

Research whether the system can identify:

- Relatively predictable bullish conditions.
- Relatively predictable bearish conditions.
- High-uncertainty conditions.
- Conditions favoring simpler baselines.
- Conditions where the model should abstain from making a strong directional call.

Report coverage, accuracy, Brier, CRPS, and matched-origin baseline performance.

A model that predicts correctly on a small selected subset is not automatically superior.

Deliver `V9_PREDICTABILITY_DISCOVERY.md`.

---

# PHASE 4 — ADAPTIVE AND REGIME-AWARE MODELING

Investigate whether adaptation can improve forecasting across both earlier and later historical periods.

Do not assume adaptation is beneficial. Previous learned weighting experiments often failed.

## Track A: Time-varying coefficients

Research:

- Exponentially weighted regression.
- Regularized time-varying parameter models.
- State-space regression.
- Kalman-filter coefficient estimation.
- Bayesian dynamic regression.
- Slowly changing coefficient shrinkage.

Compare them against fixed-coefficient models.

Investigate whether adaptation reduces instability or merely follows historical noise.

## Track B: Adaptive training windows

Compare:

- Expanding history.
- Fixed rolling windows.
- Recency-weighted expanding history.
- Change-point-triggered window adjustments.
- Blended short- and long-history models.

Predefine adaptation rules or learn them within properly purged historical training.

Do not choose the best window after observing the future result.

## Track C: Causal market-regime models

Research regimes based on:

- Trend.
- Volatility.
- Sector leadership.
- Participation.
- Liquidity.
- Global risk.
- Correlation structure.

Evaluate simple threshold regimes before more complex hidden-state models.

If using Hidden Markov Models, employ filtered probabilities available at the forecast origin rather than smoothed states that incorporate future observations.

Test whether regime conditioning provides incremental value beyond ordinary regression.

## Track D: Mixture of forecasting experts

Create a limited set of distinct experts representing:

1. Native Indian market internals.
2. Residualized financial-sector rotation.
3. Market-structure evolution.
4. Cluster-balanced return distributions.
5. ETF and liquidity information.
6. Historical momentum/reversion controls.
7. Neutral or historical distribution fallback.

Research:

- Equal-weight combinations.
- Strongly regularized dynamic weights.
- Regime-dependent mixtures.
- Performance-weighted combinations using resolved forecasts.
- Uncertainty-dependent shrinkage toward baselines.

All expert outputs must be generated causally.

Any mixture of predictive laws must remain mathematically coherent.

Compare against static mixtures and frozen individual experts.

Deliver `V9_ADAPTIVE_MODEL_RESEARCH.md`.

---

# PHASE 5 — INVESTIGATE FINANCIAL-SECTOR INFORMATION TRANSMISSION

V8 showed that the bank-versus-financial-services momentum change was the strongest individual rotation addition.

Investigate this relationship in much greater depth.

## Research universe

Use historically valid data from:

- BANK NIFTY.
- NIFTY FINANCIAL SERVICES.
- Private-bank indices.
- PSU-bank indices.
- Insurance and financial-sector proxies where available.
- Broader banking and financial equities.
- Financial-sector ETFs.
- NIFTY 50.
- NIFTY 500.

Audit actual instrument availability.

Do not assume every requested index exists in the available data.

## Research hypotheses

1. Financial-sector divergence anticipates changes in broad-market risk appetite.
2. Leadership rotation within financial stocks precedes index-level movement.
3. Changes in banking momentum are more informative than absolute momentum.
4. Banking dispersion contains information about market concentration.
5. Financial-sector weakness matters differently during bullish and bearish regimes.
6. Persistent financial-sector divergence differs from sudden rotation shocks.

## Feature development

Investigate:

- Relative strength.
- Residual returns.
- Beta-adjusted spreads.
- Momentum changes.
- Volatility-adjusted spreads.
- Rolling correlation changes.
- Leadership rank changes.
- Spread persistence.
- Spread acceleration.
- Cross-sectional dispersion.

Separate common NIFTY exposure from financial-specific residual information.

Compare simple spread models against richer financial-sector representations.

V8 used a 63-session beta lagged one session. Test reasonable alternative residualization designs in registered batches without conducting uncontrolled parameter mining.

## Critical requirement

Test whether financial-sector relationships survive:

- Earlier and later cohorts.
- Different volatility regimes.
- Different training-history lengths.
- Feature timing perturbations.
- Removal of specific sectors.
- Redundancy-aware feature normalization.

Deliver `V9_FINANCIAL_SECTOR_INTELLIGENCE.md`.

---

# PHASE 6 — MARKET INFORMATION INNOVATIONS

Previous experiments largely used observed market states, their levels, and changes.

V9 should investigate unexpected changes in those states.

## Central hypothesis

Information that the market has not already absorbed may be more predictive than the absolute value of an indicator.

Research features defined as:

Observed value minus its causally estimated expected value.

Examples:

- Unexpected BANK NIFTY performance relative to NIFTY.
- Unexpected sector rotation.
- Unexpected ETF turnover.
- Unexpected volatility changes.
- Unexpected futures basis changes.
- Unexpected market breadth.
- Unexpected global-market performance relative to domestic behavior.

Estimate expectations using only historical information.

## Candidate methods

- Rolling regression residuals.
- Autoregressive innovations.
- Conditional z-scores.
- Robust historical surprise measures.
- Factor-adjusted returns.
- Forecast residuals.
- Cross-market residuals.

Compare innovations against the original feature levels and ordinary feature changes.

Distinguish statistical innovations from actual macroeconomic announcement surprises.

Do not describe a residual as genuinely unpriced information unless evidence supports that stronger interpretation.

Deliver `V9_MARKET_INNOVATION_RESEARCH.md`.

---

# PHASE 7 — USE GLOBAL DATA MORE CREATIVELY

Previous global feature additions generally failed to improve NIFTY directly.

Do not simply append another set of global-market indicators.

Investigate whether global information helps answer a different question:

**Which Indian forecasting model should be trusted under current global conditions?**

## Research tracks

### A. Global regime conditioning

Use global equities, yields, currencies, commodities and volatility to construct a compact global risk state.

Investigate whether it modifies the performance of Indian-native models.

### B. Global-domestic divergence

Study whether India behaving unexpectedly strongly or weakly relative to global markets predicts continuation, reversal or volatility expansion.

### C. Global shocks

Investigate whether unusual global movements affect:

- Domestic rotation reliability.
- Forecast confidence.
- Distribution asymmetry.
- Future volatility.
- Large-move probability.

### D. Changing relationships

Study whether rolling changes in global-to-Indian relationships are more informative than fixed correlations.

### E. Alternative information roles

Evaluate global data separately as:

- Direct directional features.
- Regime inputs.
- Forecast-reliability inputs.
- Conditional-volatility inputs.
- Return-distribution inputs.

A data family may be unhelpful for predicting direction but useful for estimating risk or model reliability.

Use exact source timing or conservative documented availability assumptions.

Every global experiment must have a matched domestic-only parent.

Deliver `V9_GLOBAL_CONDITIONAL_INTELLIGENCE.md`.

---

# PHASE 8 — EXPLORE STRUCTURED CROSS-SECTIONAL LEARNING

We have access to a substantial universe of Indian securities.

Investigate how this universe can improve estimation of market structure rather than simply increasing the number of input columns.

Potential research directions:

- Shared sector factor estimation.
- Cross-sectional residual momentum.
- Common market risk factors.
- Hierarchical equity-sector-index relationships.
- Cross-sectional dispersion.
- Sector leadership transitions.
- Low-dimensional market representations.
- Multi-task estimation of related Indian indices.
- Market-wide correlation and synchronization.

Use dated historical membership and weights wherever possible.

If these are unavailable, clearly separate survivorship-exposed proxies from primary research candidates.

Do not count individual stock-date observations as independent NIFTY outcomes.

Use date-grouped validation.

Compare against authentic native-index representations.

Deliver `V9_CROSS_SECTIONAL_STRUCTURE.md`.

---

# PHASE 9 — RETHINK MONTHLY FORECASTING USING MULTI-SCALE DYNAMICS

Monthly forecasting remains unresolved.

V8's smoothed weekly-state model reached:

- Brier: 0.132367
- Accuracy: 85.53%
- CRPS: 0.020474
- Nominal-80% interval coverage: 85.53%

However, shifted-state controls sometimes performed better.

This is not sufficient evidence of a genuine information-timing mechanism.

V9 must investigate fundamentally different monthly approaches.

## Track A: Slow and fast market factors

Separate market information into:

- Fast-changing daily conditions.
- Weekly sector rotation.
- Medium-term momentum.
- Slowly changing volatility states.
- Persistent market leadership.

Investigate whether monthly returns depend more on slow-moving states than fast signals.

## Track B: Distributed-lag models

Research whether future monthly returns are associated with a regularized combination of past states.

Compare current, lagged, smoothed and distributed-lag representations.

Fit lag structures inside training-only procedures.

Use genuine causal lags as candidates and shifted-state controls strictly for falsification.

## Track C: Multi-horizon learning

Research joint relationships among:

- One-session returns.
- Three-session returns.
- Five-session returns.
- Ten-session returns.
- Fifteen-session returns.
- Twenty-one-session returns.

Investigate whether shorter-horizon tasks improve estimation of persistent market factors.

Do not assume shorter-horizon predictive skill automatically transfers to monthly returns.

## Track D: Path-based forecasting

Investigate an alternative to direct monthly endpoint prediction.

Build simple causal models of daily return and market-state evolution.

Generate conditional five- and 21-session return paths using methods such as:

- Conditional residual block simulation.
- Regularized autoregressive dynamics.
- Simple regime-transition models.
- Volatility-conditioned historical path resampling.

Preserve serial dependence, volatility clustering, and coherent return compounding.

Simulated paths do not create additional observed outcomes.

Compare the resulting endpoint distributions against direct weekly and monthly models.

## Track E: Monthly falsification

Repeat the strongest tests from V7 and V8:

- Lagged-state comparisons.
- Block-permuted training-state controls.
- Phase-shift controls.
- Current-state versus persistence baselines.
- Common-availability cohort comparisons.
- Disjoint-window analysis.
- Removal of individual market periods.

Investigate many prespecified placebo offsets rather than relying on one convenient shifted control.

Keep the distribution of placebo outcomes, not only the best placebo result.

If the proposed monthly mechanism repeatedly fails falsification, classify it as unresolved or rejected rather than celebrating high accuracy.

Deliver `V9_MONTHLY_MULTISCALE_RESEARCH.md`.

---

# PHASE 10 — FORECAST UNCERTAINTY AND MODEL SELF-ASSESSMENT

Develop methods that estimate whether current market conditions differ materially from the historical training experience.

Investigate:

- Feature-space distance.
- Covariance changes.
- Historical analogue distance.
- Model disagreement.
- Predictive entropy.
- Parameter uncertainty.
- Out-of-distribution diagnostics.
- Recent matured forecast errors.

Research whether uncertainty-aware shrinkage improves Brier and CRPS.

For example, a model encountering historically unfamiliar conditions could produce a distribution closer to a simple baseline.

Test this hypothesis rather than assuming it works.

Separate:

1. Uncertainty in the future market return.
2. Uncertainty in estimated model parameters.
3. Uncertainty about whether the model remains applicable.

Evaluate all three where feasible.

Deliver `V9_FORECAST_RELIABILITY.md`.

---

# PHASE 11 — BUILD COHERENT ADAPTIVE RETURN DISTRIBUTIONS

Combine the most promising ideas into complete predictive distributions.

Investigate:

- Regime-conditioned empirical distributions.
- Adaptive Student-t distributions.
- Cluster-balanced conditional residual models.
- Mixtures of complete predictive laws.
- State-dependent location and scale estimation.
- Shrinkage based on estimated model reliability.
- Path-derived distributions.

Derive all endpoint statistics from the same law:

- Probability of a positive return.
- Expected return.
- Median return.
- Quantiles.
- Return buckets.
- Expected endpoint price.
- Central prediction intervals.

Compare probability quality, distribution quality, interval calibration and sharpness.

Do not allow independently selected classifiers and regressors to generate contradictory final forecasts.

Deliver `V9_ADAPTIVE_DISTRIBUTIONS.md`.

---

# PHASE 12 — EXPAND THE HISTORICAL EVALUATION

We now have two important historical cohorts:

- The later 92-origin weekly and 76-origin monthly cohorts.
- The earlier 173-origin weekly and 141-origin monthly cohorts.

V9 must evaluate performance across both.

Where possible, establish a broader common chronological evaluation using predeclared eligibility requirements.

## Required comparisons

- Earlier period.
- Later period.
- Combined eligible chronology.
- Individual months.
- Volatility regimes.
- Trend regimes.
- Training-history lengths.
- Disjoint target windows.

Do not simply combine cohorts if their model definitions or training rules differ.

Create comparable cohorts and explain any unavoidable differences.

## Refresh available data

Retain the frozen November 17 data vintage for exact historical reproduction.

Separately acquire additional completed 2026 sessions available at execution time.

Keep data revisions and newly acquired observations separate from the frozen vintage.

Do not incorporate incomplete target outcomes.

Any newly reconstructed historical forecast remains retrospective.

If issuing new experimental forecasts, record them separately before their target outcomes exist.

Deliver `V9_EXTENDED_HISTORICAL_EVALUATION.md`.

---

# PHASE 13 — CUMULATIVE SEARCH-RISK AUDIT

V1–V8 have generated many thousands of model comparisons.

The best selected score may reflect substantial historical selection.

V9 must explicitly investigate this cumulative research risk.

## Required tests

- Reconstruct the experiment registry across V1–V8 where artifacts permit.
- Identify repeated, duplicated and materially distinct model configurations.
- Estimate correlations between competing model predictions and errors.
- Examine how often historical point winners subsequently deteriorated under changed experimental conditions.
- Compare complete research families, not only version-level winners.
- Run dependence-aware null or placebo search experiments where computationally feasible.
- Examine how much apparent improvement the same search process can produce when genuine predictive relationships are disrupted.

Where feasible, rerun representative parts of the actual model-selection pipeline under block-preserving nulls.

Distinguish this from merely shuffling the outcomes of one already-selected model.

Do not claim that an adjustment limited to V9 removes all adaptive selection across V1–V9.

## Standard validation requirements

Maintain:

- Exact-duplicate invariance tests.
- Future-information rejection.
- Matured-label enforcement.
- Training-only feature transformations.
- Purging and embargoes.
- Matched-origin comparisons.
- Dependence-aware uncertainty.
- Multiple-comparison controls.
- Negative controls.
- Leave-period diagnostics.
- Complete experiment accounting.

All historical discoveries remain research-exposed.

Deliver `V9_CUMULATIVE_SEARCH_AUDIT.md`.

---

# PHASE 14 — RESEARCH LEADERBOARD AND MODEL SELECTION

Do not select winners solely by the lowest later-cohort Brier.

Construct separate rankings for:

1. Weekly probability quality.
2. Weekly distribution quality.
3. Monthly probability quality.
4. Monthly distribution quality.
5. Earlier-period performance.
6. Temporal stability.
7. Conditional forecasting usefulness.

### Core metrics

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- MAE and RMSE.
- Quantile loss.
- Interval coverage.
- Interval width.
- Conditional calibration.
- Effective sample size.
- Disjoint windows.
- Adjusted uncertainty.

### Mandatory comparisons

Include the strongest V4–V8 references.

Measure incremental improvements against the immediate parent models, not merely against neutral or weak historical baselines.

A V9 model with a slightly worse later-cohort Brier may be a more interesting research candidate if it materially improves the earlier cohort and reduces temporal instability.

Maintain a Pareto frontier rather than forcing one universal winner.

Deliver `V9_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 15 — REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V9_TEMPORAL_GENERALIZATION_DIAGNOSIS.md`
2. `V9_PREDICTABILITY_DISCOVERY.md`
3. `V9_ADAPTIVE_MODEL_RESEARCH.md`
4. `V9_FINANCIAL_SECTOR_INTELLIGENCE.md`
5. `V9_MARKET_INNOVATION_RESEARCH.md`
6. `V9_GLOBAL_CONDITIONAL_INTELLIGENCE.md`
7. `V9_CROSS_SECTIONAL_STRUCTURE.md`
8. `V9_MONTHLY_MULTISCALE_RESEARCH.md`
9. `V9_FORECAST_RELIABILITY.md`
10. `V9_ADAPTIVE_DISTRIBUTIONS.md`
11. `V9_EXTENDED_HISTORICAL_EVALUATION.md`
12. `V9_CUMULATIVE_SEARCH_AUDIT.md`
13. `V9_COMPLETE_MODEL_COMPARISON.md`
14. `V9_SIGNAL_DISCOVERIES.md`
15. `V9_FINAL_RESEARCH_CONCLUSIONS.md`
16. `V9_NEXT_EXPERIMENTS.md`

Preserve all code, model weights, source hashes, configurations, feature definitions, predictions, failed experiments, null simulations, and verification results.

Keep V1–V8 artifacts unchanged.

---

# EXECUTION STRATEGY

Execute V9 in waves.

## Wave 1 — Understand the historical performance discrepancy

Reproduce V8.

Investigate training-size effects, temporal instability and earlier-versus-later cohort differences.

## Wave 2 — Develop adaptive forecasting approaches

Research time-varying parameters, regime conditioning, expert mixtures and predictability estimation.

## Wave 3 — Discover new information representations

Investigate financial-sector dynamics, market innovations, global-domestic divergence and cross-sectional market structure.

## Wave 4 — Rethink monthly forecasting

Research slow and fast market factors, distributed lags, multi-horizon learning and conditional return paths.

## Wave 5 — Integrate and challenge

Build coherent adaptive distributions.

Compare all promising systems across the extended historical chronology.

Perform cumulative search-risk and robustness audits.

Allocate additional research effort to genuinely interesting discoveries.

Do not abandon exploration because statistical qualification is unavailable.

Do not force a positive result.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect our research repository, access authenticated Upstox and other available historical market sources, write Python code, execute experiments, develop new models, and save research artifacts.

Do not stop after proposing a plan.

Execute the feasible experiments.

Use the entire available 2025–2026 market-data universe intelligently.

Do not merely add thousands of correlated indicators.

Investigate relationships, information changes, market structure, regime transitions, and forecast reliability.

Do not place trades, alter live trading systems, or deploy capital.

## CENTRAL RESEARCH QUESTION

Can we build a forecasting system that learns not only where NIFTY may be heading, but also which market relationships are currently informative, when those relationships change, and how much confidence the system should place in them?

We have improved our selected retrospective forecasting scores through eight research versions.

Now investigate whether we can improve their consistency across different historical market conditions.

Be creative.

Challenge existing assumptions.

Explore substantially different forecasting approaches.

Keep the research scientifically honest.

**BEGIN V9 RESEARCH.**