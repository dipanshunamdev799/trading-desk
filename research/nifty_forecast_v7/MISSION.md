# NIFTY V7 — MARKET STRUCTURE, SIGNAL COMPRESSION & ADVANCED PREDICTIVE DISCOVERY

## MISSION

You are continuing our autonomous quantitative forecasting research using Upstox, NSE archives, Indian equity-market data, global-market datasets, and our existing Python research environment.

V1 through V6 are complete.

We have made considerable retrospective progress, particularly in forecasting NIFTY's next five trading sessions.

Our latest V6 results include:

- Best weekly Brier: **0.169803**.
- Best weekly directional accuracy: **78.26% (72/92 origins)**.
- Best weekly CRPS: **0.009756**.
- V5 best Brier: 0.182047.
- V5 best CRPS: 0.009963.
- 135 model/horizon combinations evaluated in V6.
- 3,240 matched benchmark comparisons.
- Evidence that compressing or downweighting correlated sector inputs improves some model configurations.
- Monthly directional accuracy as high as 81.58% in one exploratory model, but with weak distribution coverage and failed falsification checks.

All these results are **retrospective, research-exposed, and not independently validated**.

No trading or deployment is authorized.

### Main objective

Investigate whether the information contained in Indian market internals, sector relationships, cross-market structure, liquidity, and volatility can be represented more effectively to improve forecasts over:

1. **Five future trading sessions.**
2. **Twenty-one future trading sessions.**

We are deliberately continuing research on 2025–2026 observations.

Do not stop simply because independent validation is unavailable.

However, preserve statistical honesty: improvements found on previously examined data are discoveries to investigate, not proof of forecasting superiority.

The objective is not to create the most complex model.

The objective is to discover increasingly informative, stable, and economically interpretable representations of market behavior.

---

# PHASE 1 — REPRODUCE AND UNDERSTAND V6

Read the complete V6 research index, all 13 reports, saved predictions, model configurations, source code, and experiment registry.

Reproduce:

- V6 best weekly Brier model.
- V6 best weekly CRPS model.
- V5 I03_nosize.
- V5 I00.
- V5 L01.
- Relevant V4 coherent-distribution and frozen direction controls.

Do not use the high-level summaries as substitutes for actual configurations.

Before changing any models, determine:

1. Exactly which model achieved the V6 best Brier.
2. Exactly which model achieved the V6 best CRPS.
3. Which sector features were removed, compressed, or downweighted.
4. How those transformations changed predictions.
5. Whether the improvement was concentrated in particular market regimes.
6. Whether performance depends on a small number of difficult or favorable origins.
7. Whether any preprocessing or source-availability assumptions explain the gains.

Calculate paired per-origin changes rather than comparing only aggregate metrics.

Preserve all historical predictions and existing research artifacts.

Deliver `V7_V6_REPRODUCTION_AND_DIAGNOSIS.md`.

---

# PHASE 2 — CORRELATED SIGNALS AND FEATURE COMPRESSION

This is the highest-priority V7 investigation.

V6 suggests that correlated sector features can cause redundant information to dominate prediction models.

We need to determine whether that explanation is correct, which model classes are affected, and which compression methods preserve the most useful predictive information.

## Experiment A: Feature redundancy mapping

Construct a training-only correlation and redundancy map of the Indian market features.

Investigate:

- Sector return correlations.
- Correlations across multiple lookback periods.
- Sector volatility relationships.
- Cross-index momentum redundancy.
- Overlapping market-cap-weighted index exposures.
- Feature clustering.
- Conditional versus unconditional redundancy.
- Effective dimensionality of the feature matrix.

Distinguish economic correlation from duplicate feature construction.

Create a graph or cluster map of feature relationships.

Do not use future evaluation data to construct training-time clusters.

## Experiment B: Alternative feature compression

Compare carefully controlled alternatives:

1. Correlation-based feature pruning.
2. Hierarchical feature clustering.
3. Cluster representative selection.
4. Equal-weight feature-cluster aggregation.
5. Principal component analysis.
6. Shrunk covariance PCA.
7. Sparse PCA when identifiable.
8. Group Lasso or group-wise shrinkage.
9. Elastic Net with correlated-feature control.
10. Factor-based sector aggregation.
11. Regularized model coefficients.
12. Cluster-balanced feature weights.

Do not run an unlimited Cartesian search.

Register a small, diverse initial batch and expand only where useful.

## Experiment C: Prevent sector duplication

Investigate whether the model effectively counts the same market movement multiple times.

For example, banking and financial-services indices may represent overlapping economic exposures.

Test whether feature families should receive group-level regularization or normalization rather than individual-feature penalties alone.

Evaluate whether reducing the influence of overlapping sectors improves predictions without discarding their underlying information.

## Experiment D: Stable versus unstable factors

Determine whether sector correlation structures remain consistent throughout 2025–2026.

Research:

- Rolling PCA.
- Rolling factor loadings.
- Correlation regime changes.
- Factor-loading drift.
- Static versus adaptive compression.
- Structural-break sensitivity.

Fit every transformation using only available training observations.

Report whether adaptive methods genuinely improve the forecasts or merely introduce estimation noise.

### Deliverables

- `V7_FEATURE_REDUNDANCY.md`
- `V7_COMPRESSION_EXPERIMENTS.md`
- `V7_FACTOR_STABILITY.md`

---

# PHASE 3 — MARKET STRUCTURE AND SECTOR SYNCHRONIZATION

Previous research relied heavily on individual feature values.

Investigate whether the **structure of relationships between sectors and indices** contains additional predictive information.

## Candidate hypotheses

- Sector correlations increase before large NIFTY moves.
- Broad sector synchronization precedes trend continuation.
- A breakdown in sector participation precedes index weakness.
- Leadership concentration precedes mean reversion.
- Rapid sector rotation precedes volatility expansion.
- Financial-sector divergence contains information about future NIFTY behavior.
- Defensive-versus-cyclical dispersion predicts return asymmetry.
- Changes in sector relationships predict future direction more effectively than current sector returns.

## Research methods

Evaluate:

- Rolling sector-correlation matrices.
- Correlation dispersion.
- Effective number of independent sector factors.
- Eigenvalue concentration.
- Sector-network connectivity.
- Return and volatility synchronization.
- Leadership persistence and rotation.
- Sector rank transitions.
- Rolling factor-exposure changes.
- Market breadth transitions.
- Cross-index divergences.

Do not assume sophisticated network measures are useful.

Start with simple, interpretable statistics and expand only when they provide incremental information.

Benchmark every new structural feature against the strongest V6 native-internals model.

### Deliverable

`V7_MARKET_STRUCTURE_RESEARCH.md`

---

# PHASE 4 — INFORMATION CHANGE AND STATE TRANSITIONS

Research whether forecasting improves when models learn **how market structure is changing**, rather than only its current condition.

Potential features:

- Changes in sector correlations.
- Momentum acceleration.
- Leadership acceleration.
- Breadth expansion/contraction.
- Volatility regime transitions.
- Dispersion acceleration.
- Changes in global versus Indian market relative strength.
- Liquidity expansion/contraction.
- Rapid changes in factor loadings.

Explore first differences, normalized changes, rolling slopes, and simple state-transition representations.

Investigate whether market-state transitions predict:

- Five-session direction.
- Five-session return magnitude.
- Twenty-one-session volatility.
- Large moves or regime breaks.

Condition all transition probabilities on historical information available at the origin.

Compare dynamic features against static models containing the corresponding original feature levels.

### Deliverable

`V7_STATE_TRANSITION_RESEARCH.md`

---

# PHASE 5 — REVISIT THE FULL UPSTOX AND GLOBAL DATA UNIVERSE

Do not abandon global markets simply because V5 and V6 failed to establish direct incremental value.

But do not repeat unsuccessful feature-block concatenation.

Investigate **targeted relationships**.

Examples:

- Nasdaq leadership → Indian IT relative strength → NIFTY.
- Crude oil and USD/INR changes → relevant Indian sector returns.
- Global volatility shocks → Indian sector synchronization.
- Asian equity dispersion → Indian market breadth.
- US yield changes → Indian financial-sector performance.
- Domestic liquidity and ETF activity → conditional NIFTY return distribution.

Test whether global inputs improve forecasts of intermediate Indian states before testing whether they improve NIFTY.

Research whether global-market inputs are useful only during particular volatility or correlation regimes.

Avoid claims of mediation or causality without a design capable of establishing them.

### Additional data investigation

Explore whether available historical Upstox data supports more useful features from:

- Individual liquid stocks.
- Sector ETFs.
- Intraday volatility.
- Opening versus closing price behavior.
- Intraday market participation.
- Futures and options positioning.
- Liquidity.
- Trading volume.
- Market-wide price dispersion.

Use only authentic, correctly timestamped observations.

Stock panels from the same dates do not create additional independent NIFTY outcomes.

Spot NIFTY volume must not be invented.

Exclude incomplete intraday sessions.

### Deliverable

`V7_GLOBAL_AND_LIQUIDITY_RESEARCH.md`

---

# PHASE 6 — RESEARCH ADVANCED REGULARIZATION AND MODEL ARCHITECTURES

Use the strongest Indian-internals and compressed-feature systems as foundations.

Research whether their forecasting performance can be improved with better estimation and model structures.

## Statistical approaches

- Ridge with alternative structured penalties.
- Elastic Net.
- Group Lasso.
- Bayesian shrinkage.
- Generalized additive models.
- Robust return regression.
- Hierarchical factor models.

## Machine-learning approaches

- Shallow boosted trees.
- LightGBM.
- XGBoost.
- CatBoost.
- Carefully regularized random forests.
- Mixture-of-experts models.
- Compact temporal models when sample sizes justify them.

## Novel combinations

Investigate:

- Cluster-balanced learning.
- Factor models followed by nonlinear residual models.
- Sector-factor mixtures.
- Regime-conditioned regularization.
- Low-dimensional feature interaction models.
- Simple multi-horizon shared representations.

The main objective is to determine whether better representation and regularization improve forecasts, not to maximize architecture count.

Every new model must beat or meaningfully complement simpler alternatives before receiving more research effort.

### Deliverable

`V7_ADVANCED_MODEL_RESEARCH.md`

---

# PHASE 7 — IMPROVE JOINT DIRECTION AND RETURN-DISTRIBUTION FORECASTS

V6 improved Brier and CRPS in separate models.

Investigate whether we can improve both with a coherent conditional-return distribution.

Research:

1. Shrunk empirical conditional distributions.
2. Regularized Student-t distributions.
3. Conditional residual distributions.
4. Quantile-regression distributions.
5. Mixtures of predictive distributions.
6. Probability-aware distribution tilting.
7. Joint proper-score optimization where mathematically appropriate.

Every distribution should consistently imply its own:

- Directional probability.
- Mean return.
- Median return.
- Quantiles.
- Return buckets.
- Endpoint price distribution.

Do not combine unrelated model outputs into an inconsistent final forecast.

## Evaluation

Measure:

- Brier.
- Log loss.
- CRPS.
- Mean and median return error.
- Quantile loss.
- Central 50% coverage.
- Central 80% coverage.
- Interval width.
- Probability calibration.
- Conditional coverage by volatility regime.

Investigate the tradeoff between interval sharpness and reliable coverage.

Do not optimize only CRPS while accepting severely miscalibrated intervals.

All distribution-mixture weights and calibration parameters must be estimated using training-only information.

### Deliverable

`V7_COHERENT_DISTRIBUTION_RESEARCH.md`

---

# PHASE 8 — MONTHLY FORECASTING: FALSIFY BEFORE CELEBRATING

V6 produced an exploratory monthly accuracy of 81.58%.

This looks attractive but did not survive its mechanism-falsification tests.

Nominal 80% interval coverage was only 65.79%, and shifted-state controls sometimes performed better.

Do not treat the 81.58% result as established predictive skill.

Investigate:

1. Whether state features genuinely precede outcomes.
2. Whether shifted-state controls retain or exceed performance.
3. Whether overlapping labels drive apparent accuracy.
4. Whether the prediction is exploiting persistent class imbalance.
5. Whether the apparent gain depends on a narrow market period.
6. Whether model behavior survives different training-window choices.
7. Whether coherent distributions provide better results than classification.
8. Whether persistent low-dimensional factors are more useful than short-term state features.

Explore 10-session and 15-session targets as additional diagnostic horizons.

Keep five and 21 sessions as the primary targets.

### Strict requirement

Only approximately four disjoint monthly evaluation windows were available in V5/V6.

Do not create unjustifiably precise monthly confidence intervals.

Do not interpret 76 overlapping monthly origins as 76 independent months.

### Deliverable

`V7_MONTHLY_FALSIFICATION.md`

---

# PHASE 9 — RESEARCH SEARCH-RISK AND ROBUSTNESS

We have conducted many experiments across V1–V6.

The best historical model is subject to substantial winner-selection bias.

Research must account for this explicitly.

## Validation requirements

- Chronological walk-forward evaluation.
- Fully matured labels.
- Purging and embargoes.
- Training-only feature transformations.
- Source timestamp verification.
- Matched-origin comparisons.
- Dependence-aware confidence intervals.
- Multiple-testing adjustments.
- Feature perturbation.
- Regime sensitivity.
- Leave-one-month-out stress testing.
- Source revision sensitivity.
- Negative controls.

## Additional falsification tests

For the leading V7 candidates:

- Perturb correlated features jointly.
- Remove individual sector groups.
- Shift market states by valid time offsets.
- Replace selected feature groups with lagged placebo features.
- Vary training-window length.
- Test dependence on individual periods.
- Test alternative reasonable forecast cutoffs.
- Examine calibration across market regimes.

Avoid treating an experiment performed on previously exposed dates as independent validation.

## Search discipline

Maintain a complete experiment ledger containing:

- Every hypothesis.
- Every model configuration.
- Every attempted feature family.
- Every trial result.
- Every failure.
- The reason an experiment was expanded or stopped.
- Whether a feature/model was selected after examining evaluation results.

For an exploratory leaderboard, report raw results and search-adjusted uncertainty separately.

Do not force significance.

### Deliverable

`V7_VALIDATION_AND_SEARCH_AUDIT.md`

---

# PHASE 10 — BUILD A TRUE COMPARATIVE LEADERBOARD

Compare V7 against the strongest earlier systems.

At minimum include:

- V6 best Brier model.
- V6 best CRPS model.
- V5 I03_nosize.
- V5 I00.
- V5 L01.
- V4 student-shrunk distribution.
- V4 residual-shrunk distribution.
- V4 LightGBM.
- Neutral and simple historical baselines.

Use identical origins for matched comparisons.

Evaluate weekly and monthly separately.

## Required metrics

| Metric | Requirement |
|---|---|
| Accuracy | Directional correctness |
| Balanced accuracy | Class-adjusted accuracy |
| Brier | Probability forecast quality |
| Log loss | Probability forecast quality |
| CRPS | Distribution forecast quality |
| MAE/RMSE | Return estimate quality |
| 50/80 coverage | Interval calibration |
| Interval width | Forecast sharpness |
| Disjoint count / ESS | Dependence diagnostics |
| Leave-month performance | Temporal stability |
| Adjusted uncertainty | Search-aware comparison |
| Leakage status | Data integrity |

Rank whole systems separately from feature-family incremental improvements.

An impressive result over a weak baseline does not automatically demonstrate improvement over the strongest V6 model.

---

# PHASE 11 — FINAL RESEARCH ARTIFACTS

Produce:

1. `V7_V6_REPRODUCTION_AND_DIAGNOSIS.md`
2. `V7_FEATURE_REDUNDANCY.md`
3. `V7_COMPRESSION_EXPERIMENTS.md`
4. `V7_FACTOR_STABILITY.md`
5. `V7_MARKET_STRUCTURE_RESEARCH.md`
6. `V7_STATE_TRANSITION_RESEARCH.md`
7. `V7_GLOBAL_AND_LIQUIDITY_RESEARCH.md`
8. `V7_ADVANCED_MODEL_RESEARCH.md`
9. `V7_COHERENT_DISTRIBUTION_RESEARCH.md`
10. `V7_MONTHLY_FALSIFICATION.md`
11. `V7_VALIDATION_AND_SEARCH_AUDIT.md`
12. `V7_COMPLETE_COMPARISON.md`
13. `V7_SIGNAL_DISCOVERIES.md`
14. `V7_FINAL_RESEARCH_CONCLUSIONS.md`
15. `V7_NEXT_EXPERIMENTS.md`

Also save reproducible Python code, experimental configurations, feature maps, cluster definitions, factor loadings, source/data hashes, per-origin predictions, uncertainty calculations, negative-control results, and the complete experiment registry.

Do not modify any V1–V6 artifacts or frozen forecasts.

---

# PHASE 12 — EXECUTION PRIORITIES

Execute this program in the following order:

**Priority 1: V6 mechanism discovery**

Reproduce the winners and determine why reducing correlated sector inputs improved their historical forecasting performance.

**Priority 2: Feature compression**

Evaluate whether stable, low-dimensional market factors outperform raw and redundant sector features.

**Priority 3: Market structure**

Research sector synchronization, leadership transitions, correlation changes, and market concentration.

**Priority 4: Better conditional distributions**

Investigate whether stronger directional and magnitude information can be represented coherently in one predictive distribution.

**Priority 5: Advanced models and global interactions**

Expand only those directions supported by useful intermediate evidence.

**Priority 6: Monthly falsification**

Challenge apparently successful monthly models with shifted states, controls, time sensitivity, and dependence-aware diagnostics.

## FINAL DIRECTIVE

Do not stop at creating a research plan.

Execute feasible experiments using the available infrastructure.

Continue actively investigating 2025–2026 market data.

Explore new ideas, but keep every result reproducible.

Do not claim independence or statistical significance where it is unavailable.

Do not deploy models or place trades.

### THE CENTRAL V7 QUESTION

**Can we improve NIFTY forecasting by learning the underlying structure and evolution of Indian markets, instead of supplying models with hundreds of overlapping indicators?**

V6 suggests that reducing redundant information improves predictions.

Determine whether this is a stable structural insight, a particular regularization effect, or another result of historical model selection.

Use the full market-data universe where it helps answer that question.

Find stronger representations.

Challenge them aggressively.

Retain promising findings even when they remain exploratory.

**BEGIN V7 RESEARCH.**