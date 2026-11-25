# NIFTY FORECASTING RESEARCH — V4
## Mission: Convert promising experiments into trustworthy predictive evidence

You have completed V1, V2 and V3 research using Upstox market data, NSE historical derivatives archives, and our internal market-analysis infrastructure.

V3 materially improved the dataset and evaluation framework, but still failed to establish a repeatable predictive advantage.

Your task is to critically diagnose V3, design a substantially more disciplined forecasting experiment, execute everything possible with the existing environment, and establish a prospective validation process.

**Do not begin by adding more indicators, models, or hyperparameter combinations.**

Your priority is to distinguish real predictive information from historical overfitting.

## 1. Audit the V3 findings

Read all ten V3 reports, source scripts, experiment registries, per-origin predictions, model-selection policies, and validation artifacts.

Investigate these specific findings:

- Weekly LightGBM: 66.30% accuracy, Brier 0.226049.
- Weekly selected policy: Brier 0.256118, worse than neutral.
- Weekly LightGBM improvement interval crosses zero widely.
- Monthly model selection: 60.53% accuracy versus 59.21% always-down.
- Only 19 disjoint weekly and four disjoint monthly evaluation windows.
- Zero individually significant features after multiple-testing correction.
- Monthly prediction intervals were severely undercovered.
- Direction classifiers and distribution models produced conflicting probabilities.

Reproduce these numbers and identify which failures are caused by model architecture, selection procedures, target definitions, data availability, sample limitations, or calibration.

Preserve all existing artifacts and forecasts.

## 2. Freeze a small set of candidate models

Do not run another unrestricted model competition.

For weekly direction, register these candidates:

1. The exact V3 LightGBM configuration.
2. The exact V3 price-plus-sector Ridge configuration.
3. The V3 fixed reversion baseline.
4. Neutral and historical-frequency probability baselines.

For monthly forecasts, prioritize simple historical and regularized distribution models over complicated nonlinear architectures.

Retain exact feature definitions, training rules, and hyperparameters for frozen comparisons.

Do not tune the frozen configurations on the V3 evaluation results.

Any modified model must be registered as a distinct exploratory candidate.

The previously inspected 2025–2026 dates are research-exposed. Replaying these models on those dates is reproduction or stress testing, not independent confirmation.

## 3. Develop coherent probabilistic forecasting

The previous system selected separate models for direction, expected return, median return, quantiles, volatility, and downside risk.

This generated contradictory forecasts.

Research an alternative where the primary output is a single conditional distribution of future NIFTY returns.

From that one distribution, derive:

- Probability of positive return.
- Probability of negative or zero return.
- Expected return.
- Median return.
- Return quantiles.
- Seven return-bucket probabilities.
- Endpoint price distribution.
- Expected movement magnitude.

All endpoint statistics must be mathematically consistent with the same probability distribution.

Investigate distribution forecasting approaches appropriate for the small sample:

- Shrunk empirical return distributions.
- Causal regime-conditioned historical distributions.
- Regularized parametric conditional distributions.
- Quantile regression with noncrossing constraints.
- Simple mixtures with strongly regularized parameters.

Choose complexity according to available independent outcomes.

Do not turn uncalibrated directional probabilities into invented return distributions.

Train and validate the entire distribution model causally.

For future path-breach probabilities and future realized volatility, either build separately validated path models or explicitly mark those quantities as unavailable from the endpoint-only distribution.

## 4. Diagnose probability calibration

Earlier calibration frequently degraded forecasting performance.

Investigate whether this resulted from:

- Insufficient independent training examples.
- Correlated overlapping forecast outcomes.
- Class-frequency shifts.
- Excessively flexible calibration maps.
- Crossing the 50% classification threshold.
- Overfitting calibration parameters.
- Changes in volatility or trend regimes.

Compare raw probabilities, training-only shrinkage toward an appropriate historical base rate, and extremely simple calibration methods.

Use proper scoring rules, not classification accuracy alone, to decide whether calibration adds value.

If calibration fails to improve an appropriate out-of-sample metric, do not activate it.

Do not recalibrate a frozen candidate using outcomes intended for its prospective evaluation.

## 5. Investigate the weekly LightGBM candidate

This is the most interesting V3 lead, but it remains unvalidated.

Conduct diagnostic studies without promoting retrospective improvements into new validated results.

Investigate:

- Predictions at each historical origin.
- Probability calibration by forecast-confidence bucket.
- Performance in different volatility conditions.
- Performance in trending versus sideways regimes.
- Feature-family contributions.
- Sensitivity to training-window changes.
- Sensitivity to the loss of individual feature groups.
- Performance across independent five-session evaluation windows.
- Performance relative to the fixed reversion and price-plus-sector controls.

Test whether its historical advantage depends on a small number of exceptional periods.

Calculate uncertainty using appropriate overlapping-outcome and multiple-comparison adjustments.

Do not treat 92 overlapping weekly origins as 92 independent weeks.

Most importantly, distinguish a promising retrospective configuration from an independently demonstrated predictive advantage.

## 6. Improve market information, not just indicator count

Inspect which existing information sources are still underused, especially:

- Genuine historical sector participation.
- Cross-sectional momentum dispersion.
- Authentic futures and options positioning.
- Futures basis and OI changes.
- Sector concentration and leadership.
- Intraday structure when complete.
- ETF activity.
- Relative Indian versus global market strength.

But do not automatically add every discovered feature.

For each proposed new feature, specify its distinct economic hypothesis, historical timestamp, incremental information over a price-only baseline, and expected failure modes.

Do not include today's constituent basket as historically accurate NIFTY membership.

If historical membership and index weights cannot be authenticated, keep those measures research-only.

Do not manufacture IV, Greeks, historical news sentiment, or unavailable publication timestamps.

Any new-feature research must be separated from the frozen candidate comparison.

## 7. Preserve the historical boundary

Use only 2025–2026 market observations and findings.

Do not retrieve older market data or initialize model statistics using pre-2025 observations.

Use fully completed outcomes only.

The prospective evaluation set begins with genuinely new, timestamped predictions and previously unseen resolved outcomes.

If extending observation into 2027 becomes necessary, document that the existing research restriction prevents it. Do not silently expand the date range.

Do not call another retrospective 2026 split a fresh independent test.

## 8. Establish prospective prediction tracking

Create a reproducible forecast process that can be executed at a fixed daily decision time.

On each eligible origin:

1. Verify the actual data availability cutoff.
2. Confirm the latest eligible NIFTY reference close.
3. Construct the feature matrix from permitted inputs.
4. Run the frozen baseline and candidate models.
5. Record every prediction before its outcome exists.
6. Save inputs, model versions, code hashes, and output hashes.
7. Resolve each outcome after the full five- or 21-session horizon has completed.
8. Score each prediction against its baseline on matched dates.

Persist predictions in an append-only research ledger.

Never overwrite an issued forecast after observing new prices.

Use appropriate authentication of forecast creation and source retrieval times.

Keep experimental forecasts separate from production-quality outputs.

Do not place trades.

## 9. Evaluate practical forecasting usefulness

Do not rely on directional accuracy as the primary criterion.

For binary forecasts, report:

- Brier score.
- Log loss.
- Calibration.
- Directional accuracy.
- Balanced accuracy.
- Improvement against appropriate fixed baselines.
- Coverage and accuracy of confidence-selected forecasts.
- Dependence-aware uncertainty estimates.

For return distributions, report:

- CRPS.
- Quantile loss.
- Calibration across return buckets.
- Central-50% coverage.
- Central-80% coverage.
- Interval width and sharpness.
- Performance against simple historical-return distributions.

For return point estimates, report:

- MAE.
- RMSE.
- Improvement over historical-mean and median forecasts.

Do not hide poor performance on one metric behind attractive results on another.

## 10. Define clear success, failure and stop conditions

A model does not qualify simply because it beats neutral Brier on one exploratory test.

Require:

- Consistent matched-date improvements over relevant baselines.
- Adequate prospective evidence.
- Proper scoring improvements, not just threshold accuracy.
- Acceptable distribution calibration.
- No identifiable look-ahead leakage.
- Robustness to reasonable perturbations.
- Evidence that improvements are not isolated to a few periods.

Before collecting prospective observations, conduct a power and sample-size assessment based on realistic effect sizes and forecast dependence.

The 2025–2026 restriction may make adequate prospective validation impossible.

If so, say so clearly rather than weakening the standards.

Do not promise a statistically validated monthly edge with four independent evaluation windows.

If no candidate qualifies, retain the best exploratory model and recommend NO DEPLOYMENT.

## 11. Create these deliverables

Produce:

- `V4_FAILURE_DIAGNOSIS.md`
- `V4_FROZEN_CANDIDATES.md`
- `V4_COHERENT_DISTRIBUTION_RESEARCH.md`
- `V4_WEEKLY_LIGHTGBM_AUDIT.md`
- `V4_DATA_AVAILABILITY_AUDIT.md`
- `V4_PROSPECTIVE_VALIDATION_PROTOCOL.md`
- `V4_MODEL_COMPARISON.md`
- `V4_FINAL_RESEARCH_DECISION.md`

Also create executable scripts, versioned configuration files, frozen predictions, and verification tests.

For each candidate, show its historical performance, statistical uncertainty, known limitations, and current validation status.

Distinguish:

- Reproduced historical evidence.
- New exploratory findings on research-exposed data.
- Genuine prospective observations.
- Independent validation, if eventually obtained.

## 12. Execution mandate

Begin by reproducing the V3 results.

Then audit the weekly LightGBM candidate and evaluate coherent distribution-forecasting alternatives using properly separated development procedures.

Freeze the limited candidate set and implement the prospective validation ledger.

Execute all feasible studies using existing data and tools.

Do not conduct uncontrolled trial-and-error model mining.

Do not silently extend the historical period.

Do not present unvalidated predictions as actionable trading signals.

**The objective of V4 is not to manufacture a higher accuracy percentage. It is to establish whether any repeatable forecasting advantage actually exists.**

If the answer is not yet demonstrable, deliver an auditable research system that can establish the answer from genuinely new evidence.

Start execution now.