# NIFTY V10 — SAMPLE-EFFICIENT LEARNING, TRAINING-DATA INTELLIGENCE & STRUCTURED MARKET FORECASTING

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global-market datasets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V9 of our NIFTY forecasting research.

We have explored hundreds of model configurations, thousands of benchmark comparisons, numerous feature representations, global-market relationships, sector dynamics, adaptive models and conditional return distributions.

Our best later-cohort weekly results remain:

- Brier: 0.159504.
- CRPS: 0.009453.

However, V9 demonstrated that these improvements do not transfer reliably across all historical periods.

The most important new finding is the extraordinary sensitivity of forecasting performance to training-history length and composition.

**V10 must investigate how to extract more useful predictive knowledge from the available data, rather than merely increasing feature counts or model complexity.**

We are continuing active research using 2025–2026 observations.

Do not terminate experimentation because independent validation is unavailable.

Do not fabricate independent validation either.

## PRIMARY OBJECTIVES

Predict NIFTY over:

- The next five trading sessions.
- The next 21 trading sessions.

Research directional probabilities, expected returns, median returns, coherent return distributions and uncertainty.

Secondary horizons and auxiliary targets are permitted when they help improve learning for the primary objectives.

### Research restrictions

- Use only 2025–2026 observations.
- Do not initialize models or indicators with pre-2025 market data.
- Preserve V1–V9 research artifacts.
- No live trading, capital deployment or broker orders.
- All previously inspected historical observations remain research-exposed.

---

# PHASE 1 — REPRODUCE V9 AND ESTABLISH STRONG BASELINES

Read the complete V9 research index, all 16 reports, model configurations, saved distributions, experiment registries, source scripts and verification artifacts.

Reproduce the exact training-history results:

| Training observations | Later weekly Brier |
|---|---:|
| 85 | 0.355902 |
| 126 | 0.213222 |
| 189 | 0.226963 |
| 252 | 0.210085 |
| 300 | 0.176506 |
| Expanding | 0.165232 |

Reproduce the broader 265-origin weekly results:

- Historical benchmark: Brier 0.259048, CRPS 0.011340.
- Cluster-balanced rotation: Brier 0.236386.
- Fixed historical blend: Brier 0.246239, CRPS 0.011029.
- Reliability/history blend: Brier 0.248725, CRPS 0.011014.

Preserve the protected V8 probability and distribution leaders.

Reproduce the exact-copy invariance property and retain it in applicable new models.

Recover actual model IDs and configurations from the repository rather than inferring implementations from descriptive names.

Investigate the errors of each system at individual forecast origins.

Deliver:

`V10_REPRODUCTION_AND_BASELINES.md`

---

# PHASE 2 — INVESTIGATE TRAINING-DATA COMPOSITION

V9 showed that increasing training length does not monotonically improve forecasting.

We need to determine whether particular historical observations, market episodes or distributions of training examples contribute disproportionately to useful learning.

## Research A: Separate training quantity from composition

At identical forecast origins, compare models trained on equal numbers of matured historical observations but different compositions.

Examples:

- Most recent observations.
- Older eligible observations.
- Chronologically distributed observations.
- Historical blocks sampled from multiple periods.
- Volatility-balanced observations.
- Trend-balanced observations.
- Sector-rotation-balanced observations.
- Representative market-state observations.

All selected training observations must precede the forecast origin.

Use equal training budgets and comparable preprocessing so that differences can be attributed more clearly to sample composition.

Use contiguous blocks where appropriate to preserve time dependence.

## Research B: Training observation importance

Investigate which historical periods contribute to the model's learned relationships.

Methods may include:

- Block removal.
- Leave-training-month-out tests.
- Coefficient sensitivity.
- Influence approximations.
- Training-set perturbation.
- Learning curves.
- Historical episode contribution analysis.

Distinguish retrospective influence diagnostics from methods that could actually select training observations in real time.

Never select historical examples using knowledge of the current forecast's future outcome.

## Research C: Training-state similarity

Investigate whether historical market conditions similar to the current market state are more informative than equally weighted observations.

Compare:

- Equal weighting.
- Recency weighting.
- State-similarity weighting.
- Regime-balanced weighting.
- Historical analogue weighting.
- Strongly regularized combinations.

V9's historical analogue and reliability findings must inform these experiments.

Do not assume similarity implies predictability.

Calculate effective weighted sample size and prevent weighting methods from concentrating almost entirely on a few market episodes.

Deliver:

`V10_TRAINING_DATA_INTELLIGENCE.md`

---

# PHASE 3 — RESEARCH THE OVERLAPPING-LABEL PROBLEM

This is a major new methodological investigation.

Our standard weekly target is:

R5(t) = Close(t+5) / Close(t) − 1

Our monthly target is:

R21(t) = Close(t+21) / Close(t) − 1

Adjacent targets share most of their underlying daily returns.

Consequently, hundreds of target rows can represent far fewer distinct market movements.

Investigate whether this affects model fitting as well as evaluation.

## Research A: Alternative training-label designs

Compare:

1. Standard overlapping endpoint targets.
2. Non-overlapping training targets.
3. Multiple staggered non-overlapping training phases.
4. Ensembles fitted across staggered phases.
5. Overlap-aware training weights.
6. Generalized least squares or covariance-aware estimation.
7. Block-aggregated training losses.

Do not treat staggered phases as independent datasets. Their outcomes still share underlying observations.

## Research B: Return covariance

Investigate the covariance structure created by overlapping return windows.

Explore whether covariance-aware loss functions or generalized least squares improve estimation efficiency.

Use approximate analytical overlap structures and training-derived covariance estimates where appropriate.

Regularize covariance estimates and investigate numerical conditioning.

Do not assume overlap-aware weighting automatically improves forecasts.

## Research C: Effective information

For every training design, report:

- Nominal training rows.
- Distinct underlying sessions.
- Disjoint return windows.
- Estimated dependence.
- Effective weighted sample size.
- Model coefficient stability.
- Prediction variance.
- Out-of-sample forecasting loss.

Investigate whether apparent training-size requirements partly reflect the redundancy of overlapping outcomes.

Deliver:

`V10_OVERLAPPING_LABEL_RESEARCH.md`

---

# PHASE 4 — DEVELOP SAMPLE-EFFICIENT MODELS

We need models that can learn economically useful relationships without estimating hundreds of unconstrained parameters.

## Track A: Economically structured regularization

Investigate:

- Feature-group-specific Ridge penalties.
- Hierarchical shrinkage.
- Cluster-aware Elastic Net.
- Bayesian shrinkage with zero-centered priors.
- Factor-plus-residual models.
- Low-rank regression.
- Partial pooling across related features.

Any prior or regularization strength selected from data must be estimated within historical training boundaries.

Do not use knowledge of the later-cohort winners as though it were available during earlier historical forecasts. Such designs can be tested retrospectively, but their research-exposed origin must be disclosed.

## Track B: Low-dimensional predictive models

Investigate whether useful forecasts can be produced using:

- Five structural inputs.
- Ten structural inputs.
- Twenty structural inputs.
- The existing native-internals feature family.

These are candidate complexity budgets, not forced feature counts.

Compare model complexity, effective degrees of freedom, estimation stability and forecasting quality.

Do not select the feature subset using evaluation outcomes and call the result independent.

## Track C: Parameter sharing

Research whether related market indicators can share coefficients or shrink toward common effects.

Examples:

- Financial-sector relative momentum.
- Defensive-sector relationships.
- Cyclical-sector relationships.
- Different lookback periods of the same economic variable.
- Volatility-normalized versions of related signals.

Compare shared parameters against unconstrained individual-feature coefficients.

Retain exact-duplicate invariance where applicable.

## Track D: Bias-variance investigation

Use training-block perturbations and repeated fitting to estimate how much model predictions vary when the training sample changes.

Distinguish empirical sensitivity diagnostics from formally identified bias and variance.

Determine whether the stronger expanding-history models mainly benefit from more stable coefficients, different training-period composition, or both.

Deliver:

`V10_SAMPLE_EFFICIENT_MODELS.md`

---

# PHASE 5 — RETHINK THE FORECASTING TARGETS

Previous research directly estimated five-session and 21-session endpoint returns.

Investigate whether alternative target representations make those returns easier to learn.

## Research A: Volatility-normalized returns

Compare forecasts of:

- Raw percentage returns.
- Log returns.
- Returns normalized by causally estimated volatility.
- Returns relative to a historical conditional expectation.
- Market-factor-adjusted return residuals.

Convert predictions back into coherent NIFTY endpoint-return distributions.

Do not use realized future volatility to normalize an input or reconstruct an issued forecast.

## Research B: Decompose future returns

A five-session return can be represented as the sum of five future daily log returns.

Investigate whether learning shorter components is more sample-efficient than directly fitting the entire endpoint.

Potential decompositions:

- First-session return.
- Sessions two through five.
- Overnight gaps.
- Intraday returns.
- First-week movement.
- Subsequent monthly movement.

For 21-session forecasting, research whether shorter, non-overlapping future subperiods have different predictable structures.

Use forecast-origin information only.

Do not insert actual future intermediate observations when constructing a multi-step prediction.

## Research C: Direction and magnitude decomposition

Investigate whether the determinants of direction differ from the determinants of movement magnitude.

Research coherent distributions composed of:

- Positive-return probability.
- Conditional positive-return magnitude.
- Conditional nonpositive-return magnitude.

Unlike the earlier disconnected classifiers and regressors, the combined law must be mathematically coherent and evaluated as one system.

Compare against direct conditional-distribution models.

## Research D: Rare versus ordinary market movements

Investigate whether predictive relationships differ between ordinary market fluctuations and large directional movements.

Use training-defined return buckets.

Evaluate probability quality across all buckets rather than selecting convenient thresholds after observing outcomes.

Deliver:

`V10_TARGET_ENGINEERING.md`

---

# PHASE 6 — CROSS-MARKET TRANSFER AND MULTI-TASK LEARNING

We have an extensive Upstox and global-market universe.

Previous transfer-learning attempts were unsuccessful, but that does not establish that all forms of parameter sharing are ineffective.

V10 should investigate more structured alternatives.

## Research A: Learn shared financial-market relationships

Build historically valid panels from:

- Indian broad-market indices.
- Sector indices.
- Liquid equities.
- ETFs.
- Available global equity indices.

Study whether relationships involving momentum, volatility, dispersion, liquidity and relative strength are shared across instruments.

Use instrument-specific normalization and clearly defined forecasting targets.

## Research B: Hierarchical transfer

Compare:

- NIFTY-only estimation.
- Pooled market models.
- Sector-specific models.
- Shared coefficients with instrument-specific adjustments.
- Shared factor representations followed by NIFTY-specific estimation.
- Panel-trained models with strongly regularized NIFTY adaptation.

Use chronological date-grouped training and validation.

At each forecast origin, auxiliary labels must be fully matured and available.

No future auxiliary outcomes may enter the fit.

## Research C: Transfer across horizons

Explore shared representations for:

- One-session returns.
- Three-session returns.
- Five-session returns.
- Ten-session returns.
- Fifteen-session returns.
- Twenty-one-session returns.
- Realized volatility.
- Sector leadership.

Investigate whether shorter-horizon tasks improve estimation of parameters useful for longer-horizon forecasts.

Use horizon-specific output layers or coefficients where appropriate.

Do not assume that a useful shared representation guarantees accurate monthly predictions.

## Research D: Transfer falsification

Compare genuine auxiliary tasks against:

- Randomized auxiliary labels.
- Block-shifted auxiliary targets.
- Unrelated instrument controls.
- Identical-complexity NIFTY-only models.

Determine whether improvements arise from transferable information, generic regularization or historical chance.

Remember:

**A panel of thousands of securities can improve estimation of common relationships, but does not create thousands of independent NIFTY outcomes.**

Deliver:

`V10_STRUCTURED_TRANSFER_LEARNING.md`

---

# PHASE 7 — DISCOVER UNDERUSED HISTORICAL INFORMATION

Continue exploring the available market-data universe.

Do not restrict V10 to features already present in V9.

Prioritize genuinely distinct information.

## A. Historical constituent and weighting data

Investigate whether authentic, dated NIFTY and sector-index membership and weighting information can be reconstructed from permitted sources.

Potential research applications:

- Historical constituent contribution.
- Genuine weighted breadth.
- Equal-weight versus cap-weight leadership.
- Index concentration.
- Financial-sector contribution.
- Changes in heavyweight-stock participation.

If historical membership or weights cannot be authenticated, do not substitute today's basket and label it accurate historical membership.

## B. Cash-market and derivatives relationships

Research:

- Futures basis adjusted for available carry information.
- Contract rollover behavior.
- OI changes normalized by market activity.
- Positioning concentration.
- Cash-versus-futures relative returns.
- Options-derived risk estimates when authentic historical information permits.

Distinguish option-implied risk-neutral distributions from forecasts of actual realized returns.

Do not interpret risk-neutral option probabilities as directly calibrated real-world directional probabilities.

## C. Intraday panel intelligence

Investigate whether synchronized intraday behavior across sectors provides useful daily market-state summaries.

Examples:

- Opening breadth.
- Sector synchronization.
- Intraday leadership changes.
- Closing pressure.
- Volatility concentration.
- Overnight versus intraday return contributions.

Only use complete, validated sessions and historically available data.

## D. Global-market information

Revisit global data as a source of:

- Shared market-risk factors.
- Volatility information.
- Cross-market relative strength.
- Conditional distributions.
- Transferable market dynamics.

Investigate whether global information is useful for estimation or risk prediction even when direct directional additions fail.

Every additional source must have a matched parent-model comparison.

Deliver:

`V10_NEW_INFORMATION_DISCOVERY.md`

---

# PHASE 8 — FINANCIALLY STRUCTURED FORECASTING

Investigate whether simple financial relationships can constrain models sufficiently to improve sample efficiency.

Potential approaches:

## A. Market-factor decomposition

Represent sector returns as:

- Common market component.
- Sector-specific component.
- Residual component.

Use causal estimates of factor exposures.

Investigate which component predicts future NIFTY behavior.

## B. Sector contribution models

If historically valid weights exist, investigate whether forecasting weighted sector or constituent contributions provides useful index-level forecasts.

Do not aggregate incompatible indices or overlapping sector exposures as though they partition NIFTY.

## C. Return and risk separation

Estimate conditional market volatility and expected return using distinct statistical mechanisms while maintaining one coherent endpoint distribution.

Compare with ordinary direct regressions.

## D. Structured state dynamics

Investigate compact models of the evolution of:

- Market direction.
- Financial leadership.
- Defensive/cyclical leadership.
- Volatility.
- Participation.
- Liquidity.

Compare explicit state-transition structures against ordinary lagged regression.

Require evidence that the structure improves forecasting rather than merely creating an interpretable description.

Deliver:

`V10_FINANCIALLY_STRUCTURED_MODELS.md`

---

# PHASE 9 — MONTHLY FORECASTING: DEVELOP A DIFFERENT ESTIMATION STRATEGY

The 21-session forecasting problem remains unresolved.

We now have 217 comparable monthly origins, but only 11 disjoint monthly windows.

Previous monthly results above 80% directional accuracy failed important shifted-state controls.

V10 must not repeat the same smoothed-state architecture with different arbitrary parameters.

Investigate:

1. Overlap-aware monthly estimation.
2. Strongly regularized distributed-lag models.
3. Multi-horizon parameter sharing.
4. Volatility-normalized monthly targets.
5. Forecasts composed of shorter future return components.
6. Persistent market-factor models.
7. Low-dimensional conditional distributions.
8. Transfer from related market instruments.

Compare each approach against:

- Historical monthly return distributions.
- Neutral probability.
- Reversion controls.
- V6 monthly state references.
- V8 monthly smoothing references.
- V9 monthly cluster-balanced rotation.
- Relevant lagged-state and shifted-state placebos.

All actual forecasts must use genuine causal data.

Shifted or randomized states are diagnostic controls, not deployable forecasts.

Do not fabricate precision from 11 disjoint outcomes.

Report whether each proposed monthly mechanism survives falsification, rather than ranking solely by accuracy.

Deliver:

`V10_MONTHLY_SAMPLE_EFFICIENCY.md`

---

# PHASE 10 — BUILD COHERENT FORECASTING DISTRIBUTIONS

Use the strongest new estimation methods to build complete return distributions.

Research:

- Conditional empirical residual distributions.
- Regularized Student-t distributions.
- Hierarchical location-scale models.
- Sign-and-magnitude decomposition.
- Mixtures of complete predictive laws.
- Shorter-horizon path-derived distributions.

Every complete law must consistently imply:

- Positive-return probability.
- Expected return.
- Median return.
- Quantiles.
- Return buckets.
- Expected NIFTY endpoint.
- Central 50% and 80% prediction intervals.

Evaluate probability calibration, CRPS, Brier, log loss, interval coverage and sharpness.

Report directional and distribution tradeoffs explicitly.

Do not mix separately selected outputs into one contradictory forecast.

Deliver:

`V10_COHERENT_FORECASTING.md`

---

# PHASE 11 — VALIDATE SAMPLE-EFFICIENCY CLAIMS

The main claim of V10 is not that a new model can achieve a marginally lower Brier on the later historical cohort.

It is that better estimation can extract more useful predictive information from limited historical observations.

## Required learning-curve comparisons

Evaluate promising V10 systems across eligible training lengths of:

- 85 observations.
- 126 observations.
- 189 observations.
- 252 observations.
- 300 observations.
- Expanding history.

Use identical forecast origins within each matched comparison.

Compare new methods against equivalent-complexity and equivalent-training-budget controls.

## Required historical cohorts

Report separately:

- Earlier weekly cohort.
- Later weekly cohort.
- Combined comparable weekly chronology.
- Earlier monthly cohort.
- Later monthly cohort.
- Combined comparable monthly chronology.

Preserve the original November 17 data vintage.

Separately acquire additional completed 2026 sessions where available.

Score newly matured old forecasts without modifying their original predictions.

Do not label reconstructed historical forecasts as prospective.

## Required metrics

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- Mean and median return errors.
- Interval coverage.
- Interval width.
- Model sensitivity.
- Effective sample size.
- Disjoint-window performance.
- Search-adjusted uncertainty.

A model that performs acceptably with 85 training observations may be more valuable for research than a model that achieves a spectacular later-cohort score but requires a particular 300-session history.

Deliver:

`V10_LEARNING_CURVES_AND_GENERALIZATION.md`

---

# PHASE 12 — SEARCH-RISK AND FALSIFICATION

V9 reconstructed 454 exact configuration fingerprints and 583 distinct stored prediction-vector fingerprints from earlier research.

The true cumulative search may be larger.

V10 must explicitly account for this extensive exposure.

## Research discipline

Register:

- Initial hypotheses.
- Model families.
- Parameter ranges.
- Training budgets.
- Evaluation metrics.
- Expansion criteria.
- Negative controls.

Adaptive follow-up experimentation is permitted but must be labeled as such.

## Negative controls

Perform:

- Block-permuted training targets.
- Shifted feature states.
- Randomized auxiliary tasks.
- Duplicate-feature perturbations.
- Training-period removal.
- Feature-group removal.
- Source-timing perturbations.
- Future-information sentinel tests.

Where feasible, rerun representative selection pipelines under null conditions rather than merely testing already-selected winners.

Compare the distribution of selected null improvements with the genuine research improvements.

Do not claim that a bounded V10 null search accounts for the complete V1–V10 adaptive discovery process.

Maintain causal preprocessing, fully matured labels, purging, embargoes and timestamp integrity throughout.

Deliver:

`V10_VALIDATION_AND_CUMULATIVE_SEARCH_AUDIT.md`

---

# PHASE 13 — RESEARCH LEADERBOARD

Create separate rankings for:

1. Combined weekly probability quality.
2. Combined weekly distribution quality.
3. Small-training-sample performance.
4. Temporal stability.
5. Earlier-cohort performance.
6. Later-cohort performance.
7. Monthly forecasting.
8. Incremental information value.

Include the strongest V4–V9 systems.

Do not force a universal winner.

Maintain a Pareto frontier showing tradeoffs between:

- Predictive quality.
- Training-data requirements.
- Model complexity.
- Calibration.
- Temporal stability.
- Statistical uncertainty.

Classify each research hypothesis as:

- REJECTED IMPLEMENTATION.
- INCONCLUSIVE.
- EXPLORATORY LEAD.
- ROBUST RETROSPECTIVE CANDIDATE.
- INDEPENDENTLY VALIDATED, only when genuinely supported.

Retain methodological achievements separately from predictive achievements.

A model can solve a statistical representation problem without establishing superior forecasting skill.

Deliver:

`V10_COMPLETE_COMPARISON.md`

---

# PHASE 14 — REQUIRED RESEARCH OUTPUTS

Produce:

1. `V10_REPRODUCTION_AND_BASELINES.md`
2. `V10_TRAINING_DATA_INTELLIGENCE.md`
3. `V10_OVERLAPPING_LABEL_RESEARCH.md`
4. `V10_SAMPLE_EFFICIENT_MODELS.md`
5. `V10_TARGET_ENGINEERING.md`
6. `V10_STRUCTURED_TRANSFER_LEARNING.md`
7. `V10_NEW_INFORMATION_DISCOVERY.md`
8. `V10_FINANCIALLY_STRUCTURED_MODELS.md`
9. `V10_MONTHLY_SAMPLE_EFFICIENCY.md`
10. `V10_COHERENT_FORECASTING.md`
11. `V10_LEARNING_CURVES_AND_GENERALIZATION.md`
12. `V10_VALIDATION_AND_CUMULATIVE_SEARCH_AUDIT.md`
13. `V10_COMPLETE_COMPARISON.md`
14. `V10_SIGNAL_DISCOVERIES.md`
15. `V10_FINAL_RESEARCH_CONCLUSIONS.md`
16. `V10_NEXT_EXPERIMENTS.md`

Preserve all reproducible Python code, configurations, source hashes, training selections, model coefficients, predictions, failed experiments and verification tests.

Keep V1–V9 artifacts and all previously frozen forecasts unchanged.

---

# EXECUTION STRATEGY

Proceed in five waves.

## Wave 1 — Understand the available learning information

Reproduce V9, investigate training composition, overlap and effective training information.

## Wave 2 — Improve estimation

Develop sample-efficient models, structured penalties, alternative targets and parameter-sharing methods.

## Wave 3 — Exploit the broader market universe

Investigate structured transfer learning, historical constituent information, derivatives relationships, intraday market structure and global-market knowledge.

## Wave 4 — Monthly forecasting

Apply the most promising estimation mechanisms to the monthly problem and perform extensive falsification.

## Wave 5 — Integrate and compare

Build coherent predictive laws, compare learning curves across periods, perform robustness tests and document all conclusions.

Allocate more computation to productive hypotheses.

Do not waste research effort repeatedly implementing approaches that have already failed unless a genuinely different mechanism is being tested.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing repository, access authenticated market data, write Python scripts, develop mathematical models, fit estimators, execute experiments and save reproducible research outputs.

Do not stop at writing a plan.

Execute the feasible research.

Continue using the extensive Upstox, NSE, Indian-equity and global-market datasets.

Use only 2025–2026 observations.

Do not deploy models or place trades.

## THE CENTRAL V10 QUESTION

We have a large amount of market information but a limited number of distinct NIFTY forecasting outcomes.

Can we overcome part of this limitation by improving:

- Training-data composition?
- Statistical estimation?
- Overlapping-label treatment?
- Target representations?
- Cross-market parameter sharing?
- Financially structured model design?

We are not simply looking for another record historical accuracy percentage.

We want to discover how to extract more useful predictive knowledge from the data we already possess.

Explore aggressively.

Challenge previous assumptions.

Develop substantially different approaches.

Preserve every important finding, including failures.

Do not confuse exploratory discoveries with independent evidence.

**BEGIN V10 RESEARCH.**