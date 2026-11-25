# MISSION: DISCOVER A GENUINE PREDICTIVE EDGE IN NIFTY USING UPSTOX DATA

## 1. Your Role

You are an autonomous quantitative research scientist, financial data engineer, machine-learning researcher, and statistical validation specialist.

You have access to our existing trading research environment, Upstox API integrations, market databases, historical candle data, derivatives information, dashboard signals, and the ability to execute Python research scripts.

Your mission is to **discover, rigorously test, and improve predictive models for NIFTY 50 over the next 1 week and 1 month.**

Do not merely generate predictions using complicated formulas.

Your goal is to identify statistically defensible relationships between information available today and future market movements.

You are explicitly encouraged to explore alternative methods, engineer features, write experimental code, challenge previous assumptions, and discover approaches we have not attempted.

However, every claimed improvement must survive honest out-of-sample testing.

**The objective is predictive accuracy, calibration, practical usefulness, and reproducibility—not model complexity or impressive-looking probabilities.**

---

## 2. Existing Research: Read This First

Our previous research produced four studies:

1. Initial NIFTY daily forecasting.
2. Adaptive feature weighting based on historical prediction errors.
3. A restricted historical-data study.
4. Dedicated 5-session and 21-session forecasting.

Read all existing reports, source code, configurations, predictions, feature definitions, and validation artifacts before modifying anything.

Known problems include:

- The daily models struggled to outperform neutral probability baselines.
- Learned feature weights were unstable.
- Probability calibration sometimes made predictions worse.
- The weekly model did not demonstrate a reliable advantage over elementary directional baselines.
- The monthly model performed especially poorly.
- Historical sample sizes were limited.
- Overlapping weekly/monthly targets reduced effective sample sizes.
- Several potentially useful signals lacked trustworthy historical timestamps.
- Some source datasets had duplicate or invalid candles.
- Thousands of dashboard observations included repeated snapshots rather than independent outcomes.

Do not ignore these findings.

**Treat the earlier research as failed or inconclusive experiments that can teach us something. Do not treat its selected parameters as established truths.**

Preserve all existing reports and frozen forecasts.

Create a separately versioned V3 research workspace.

### Historical scope

Use only observations dated **2025–2026**, consistent with our research constraints.

Do not import pre-2025 market observations, training labels, fitted model parameters, indicator warm-up values, or feature statistics.

Use 2025 through the latest fully resolved eligible session available when executing the research.

Historical dates already explored in prior studies must be marked as research-exposed. Chronological testing on those dates is useful for development but cannot become genuinely untouched confirmation simply by rerunning a different model.

---

# PHASE 1: AUDIT EVERYTHING WE ALREADY HAVE

Before building another predictive model, investigate the available information.

### 1.1 Complete data discovery

Inspect the Upstox integration, internal APIs, raw databases, historical files, feature pipelines, cached datasets, and dashboard concepts.

Do not restrict yourself to the existing 71 engineered features.

Discover all usable historical input categories, including:

- NIFTY 50 price, volume where available, and OHLCV derivatives.
- BANK NIFTY and other broad market indices.
- Individual NIFTY constituents.
- Sector indices and relative strength.
- Market breadth and constituent participation.
- Intraday and multi-timeframe candles.
- Futures prices, basis, and open interest.
- Options OI, changes in OI, PCR, IV, skew, Greeks, and option-chain structure.
- FII/DII cash flows and derivatives positioning.
- India VIX and realized volatility.
- Global equity indices and futures.
- Currency, crude oil, metals, and interest rates.
- Market calendar, expiry, and event information.
- Earnings, corporate announcements, and macroeconomic releases.
- News, sentiment, and event-related signals where historical timestamps are provable.
- Existing dashboard indicators and derived signals.

Discover additional useful signals if the available data supports them.

For every input, establish:

1. Historical coverage.
2. Frequency and granularity.
3. Source and source timestamp.
4. Actual historical availability time.
5. Missingness and data quality.
6. Point-in-time reliability.
7. Whether it can be reconstructed at previous forecast origins.
8. Whether it can legally enter a historical model without look-ahead bias.

Classify inputs as:

- Historically usable.
- Usable with explicit limitations.
- Research-only.
- Current-context-only.
- Unavailable or invalid.

**Never invent unavailable historical data or treat today's data as though it existed in the past.**

If historical option-chain snapshots do not exist, do not simulate their historical predictive power from current snapshots.

### 1.2 Data integrity

Specifically revisit previously discovered defects:

- Duplicate OHLC rows.
- Conflicting auto-index candles.
- Invalid global-market OHLC.
- Delayed daily candle publication.
- Missing NIFTY 500 observations.
- US-session completion timing.
- GIFT NIFTY futures basis and timing.
- Institutional report publication delays.
- Missing or revised corporate-action data.

Create automatic data validation tests.

Ensure all preprocessing is based only on information available at each historical forecast origin.

### Deliverable

Produce `01_DATA_AUDIT.md`, including an inventory of inputs, historical coverage, usable sample counts, availability limitations, and the most promising untested information sources.

---

# PHASE 2: REDEFINE WHAT WE ARE TRYING TO PREDICT

Our previous research focused heavily on binary UP/DOWN prediction.

That may not be the most useful target.

Research multiple prediction targets independently.

## 2.1 Primary prediction horizons

**Weekly:** Five future NIFTY trading sessions.

**Monthly:** Twenty-one future NIFTY trading sessions.

Use exact trading-session calendars, excluding weekends and exchange holidays.

For each horizon, estimate:

| Target | Research objective |
|---|---|
| Direction | Probability that the future close exceeds the reference close |
| Return | Expected percentage return |
| Median return | Robust central directional estimate |
| Magnitude | Likely size of the movement |
| Distribution | Probabilities of different return ranges |
| Volatility | Expected movement and uncertainty |
| Market regime | Trending, sideways, high-volatility, or transitioning |
| Material move | Probability of exceeding meaningful positive/negative thresholds |

Consider the following return buckets for research:

- Below −5%.
- −5% to −2%.
- −2% to −0.5%.
- −0.5% to +0.5%.
- +0.5% to +2%.
- +2% to +5%.
- Above +5%.

You may adapt these buckets to the horizon using training data, but define them before evaluating a test period.

These targets should be evaluated independently.

A model that cannot predict direction might still predict volatility or large-move risk.

A model that predicts next-month return poorly might identify the probability of a large drawdown meaningfully better than a baseline.

Explore these possibilities rather than forcing everything into a binary classifier.

## 2.2 Predictability by market conditions

Investigate whether forecast quality changes across:

- Strong trends.
- Sideways markets.
- High-volatility periods.
- Low-volatility periods.
- Bullish versus bearish broader-market participation.
- Expiry-related periods.
- Major global risk-off episodes.
- Large preceding market moves.

Market regimes must be calculated using historical information available at forecast time.

Do not classify a historical regime using future data.

Check whether predictive signals are useful only in particular conditions.

**A conditional edge can be more valuable than a weak universal model, provided it survives independent testing.**

---

# PHASE 3: RESEARCH ALTERNATIVE PREDICTION APPROACHES

Do not assume our previous logistic regression and adaptive weighted ensemble are the correct architectures.

Research a diverse but controlled set of model families.

## Approach A: Strong statistical baselines

Start with:

- Constant historical directional frequency.
- Neutral 50/50 probabilities.
- Always-up and always-down classifiers.
- Momentum and trend continuation.
- Mean reversion.
- Rolling historical conditional averages.
- Regularized linear and logistic models.

All baselines must be trained or defined using only past available information.

The new models must beat relevant simple alternatives.

## Approach B: Gradient-boosted decision trees

Evaluate suitable implementations of:

- LightGBM.
- XGBoost.
- CatBoost.

These can capture nonlinear interactions among signals.

Examples of candidate hypotheses:

- Does negative FII positioning matter differently when VIX is elevated?
- Does breadth deterioration predict future weakness after NIFTY rallies?
- Does sector divergence precede corrections?
- Does momentum behave differently under different volatility regimes?
- Do large options-positioning changes contain additional information beyond price movement?

Treat these as hypotheses, not established trading facts.

Control depth, regularization, feature count, and hyperparameter search to avoid overfitting the limited dataset.

## Approach C: Regularized feature selection

Try:

- Elastic Net.
- L1/L2 penalties.
- Stability selection.
- Correlation clustering.
- Redundancy-aware feature groups.
- Training-only dimensionality reduction.
- Feature ablations.

Our system may contain hundreds of related indicators that mostly repeat the same price information.

Determine whether a small number of independent, reliable signals work better than a massive feature set.

Do not rank features using the test outcomes and then claim unbiased performance on those same outcomes.

## Approach D: Market regime models

Investigate:

- Hidden Markov Models.
- Change-point detection.
- Volatility regime models.
- Trend-strength classifications.
- Regime-conditioned models.
- Mixture-of-experts architectures.

Ask whether the conditional distribution of future returns is more predictable than the unconditional direction.

Keep regime inference strictly causal.

A sophisticated regime classifier is not useful if it cannot improve future forecasts.

## Approach E: Historical analogues

Improve upon our earlier 60-nearest-analogue approach.

Research similarity based on:

- Price structure.
- Volatility.
- Trend strength.
- Sector rotation.
- Global-market conditions.
- Market breadth.
- Derivatives positioning, when historically available.

Try different similarity metrics and feature subsets.

Evaluate analogue quality on historical unseen origins.

Do not assume that two visually similar markets will have similar future outcomes.

## Approach F: Cross-sectional and sector intelligence

This is an important new research direction.

Instead of predicting NIFTY directly from only its index-level indicators, investigate the internal behavior of its constituent stocks.

Candidate signals:

- Percentage of stocks above major moving averages.
- Distribution of stock momentum.
- Number of stocks making new highs/lows.
- Breadth divergence versus NIFTY.
- Sector leadership concentration.
- Equal-weight versus market-cap-weight performance.
- Relative strength of banks and heavyweight constituents.
- Dispersion of constituent returns.
- Contribution from the largest index weights.
- Correlation and volatility across constituents.

Use genuine historical membership and weights where available.

If membership or weight history cannot be reconstructed, clearly label the approximation and test whether the result depends on it.

Investigate whether constituent-level information predicts index-level moves better than aggregate indicators.

## Approach G: Direct return and distribution forecasting

Instead of only producing directional probabilities, evaluate:

- Regularized return regression.
- Quantile regression.
- Direct conditional-return distributions.
- Volatility-adjusted return predictions.
- Conditional tail-risk forecasts.
- Conformal intervals where the assumptions and sample sizes permit meaningful validation.

Do not convert a weak classifier into a supposedly precise price distribution without evaluating conditional magnitude and historical interval coverage.

The prior monthly intervals performed poorly. Their methodology must be challenged, not carried forward unchanged.

## Approach H: Temporal and sequence models

Investigate lightweight sequence models only if the available sample size supports them.

Examples include:

- Models using several preceding sessions as structured sequences.
- Temporal convolutional models.
- Small recurrent models.

Do not automatically use LSTMs or Transformers merely because the dataset has many columns.

First establish whether they improve appropriately controlled out-of-sample results over simpler models.

If the dataset is too small, record that limitation and skip the architecture.

---

# PHASE 4: INTELLIGENT FEATURE ENGINEERING

Raw market inputs are not necessarily the best predictors.

Research transformations that encode market relationships.

Candidate feature families include:

### Trend and momentum
- Multi-horizon returns.
- Momentum acceleration/deceleration.
- Trend persistence.
- Distance from moving averages.
- Volatility-adjusted momentum.
- Relative sector momentum.

### Market participation
- Participation strength.
- Breadth changes.
- Index-versus-breadth divergences.
- Sector concentration.
- Leadership rotation.
- Stock-level return dispersion.

### Volatility and risk
- VIX term changes where available.
- Realized-versus-implied volatility.
- Volatility compression/expansion.
- Range behavior.
- Downside volatility.
- Volatility clustering.

### Derivatives
- Futures basis changes.
- OI changes relative to price.
- Put/call positioning changes.
- IV skew and relative IV.
- Option-chain concentration changes.
- Expiry-dependent effects.

Only use derivatives features with authenticated historical observations.

### Global context
- Relative performance versus global indices.
- Currency and commodity shocks.
- Overnight risk indicators.
- Global volatility regime.
- Changes in global/Indian market relationships.

### Interaction features

Examples:

- Momentum × volatility.
- Breadth × index return.
- FII positioning × market trend.
- Sector dispersion × volatility.
- Global weakness × Indian relative strength.

These interactions may reveal conditional signals missed by linear models.

But adding hundreds of interactions increases the risk of finding accidental patterns.

Use regularization, training-only selection, and explicit hypothesis limits.

### Temporal behavior

Research whether the **change in an indicator** is more informative than its absolute value.

Examples:

- Is rapidly deteriorating breadth more informative than simply weak breadth?
- Is VIX acceleration more useful than the VIX level?
- Are changes in sector leadership more informative than current leadership?
- Is the combination of slowing momentum and widening dispersion useful?

Evaluate each claim empirically.

---

# PHASE 5: SEARCH FOR PREDICTIVE INFORMATION, NOT CORRELATION

Before expensive model training, investigate whether each feature family adds information about future returns.

Use tools such as:

- Rank correlation with future returns.
- Conditional return distributions.
- Mutual-information estimates, with appropriate bias controls.
- Out-of-sample univariate forecasting.
- Feature-family ablation.
- Permutation-based importance on valid test structures.
- Stability across time.
- Redundancy analysis.

For each feature or feature group, ask:

1. Does it predict future outcomes at all?
2. Does the relationship survive chronological testing?
3. Does it provide information unavailable in simpler price features?
4. Is the sign of the relationship stable?
5. Is the effect economically meaningful?
6. Does it work across multiple market regimes?
7. Could the apparent edge arise from leakage, selection bias, or chance?

Do not interpret feature importance as causal influence.

Do not select features on the final test period.

Document both failed and successful hypotheses.

---

# PHASE 6: REBUILD THE VALIDATION FRAMEWORK

This is the most important phase.

A model that looks excellent because of data leakage is worse than an honest model that admits uncertainty.

## 6.1 Chronological testing

Use rolling-origin or expanding-window evaluation.

At every forecast origin:

1. Load only information actually available by the decision timestamp.
2. Fit preprocessing using historical training data only.
3. Train using fully matured outcomes only.
4. Produce predictions without accessing future prices.
5. Freeze predictions.
6. Resolve and score them only after the full target horizon completes.

Do not permit unclosed weekly or monthly labels into training.

## 6.2 Multiple decision timestamps

Research the existing pre-market forecast timing first.

Potentially evaluate separate forecast systems for:

- Previous-day close.
- Pre-market decision.
- After-market-open decision.

Only create an additional timing experiment if reliable historical as-of reconstruction is possible.

Do not compare results across different forecast timestamps as though their information sets were identical.

## 6.3 Purging and overlap control

Five-session targets overlap heavily.

Twenty-one-session targets overlap even more.

Use purging and appropriate embargoes in validation where necessary.

Report both:

- All eligible chronological forecast origins.
- Non-overlapping or dependence-adjusted evaluation results.

Never present overlapping monthly predictions as independent observations.

Estimate effective sample sizes and uncertainty.

Given the 2025–2026 constraint, monthly independent evaluation opportunities will be limited. Explicitly acknowledge this rather than manufacturing statistical confidence.

## 6.4 Nested model selection

Separate:

- Training.
- Hyperparameter tuning.
- Model and feature selection.
- Final evaluation.

Where practical, implement nested chronological validation.

Record every configuration tried and every evaluation inspected.

The research agent must not repeatedly optimize against the same evaluation set while calling it untouched.

## 6.5 Realistic baselines

For every target, compare against relevant baselines on identical dates:

- Neutral probability.
- Historical directional frequency.
- Always-up.
- Always-down.
- Momentum.
- Mean reversion.
- Historical unconditional median return.
- Historical quantile distribution.
- Simple volatility forecasts.

A 60% directional accuracy score is not impressive if an elementary baseline scores 63%.

## 6.6 Statistical uncertainty

Evaluate:

- Brier score.
- Log loss.
- Accuracy and balanced accuracy.
- Probability calibration.
- Expected return MAE/RMSE.
- Interval coverage.
- Interval width.
- Quantile or proper distribution scores.
- Performance by volatility regime.
- Performance stability through time.

Use dependence-aware uncertainty estimates such as suitable moving-block bootstrap procedures.

Report confidence intervals for improvements over the strongest relevant baseline.

Do not claim robust significance from only a handful of independent monthly outcomes.

## 6.7 Negative controls

Implement automated tests that deliberately:

- Shuffle or shift targets.
- Insert future information into a sentinel feature.
- Check model output sensitivity to future data changes.
- Verify that timestamp filters exclude future observations.
- Verify that incomplete horizon outcomes are unavailable to training.

The correct pipeline should reject leakage and show no credible predictive skill from randomized targets.

---

# PHASE 7: CONTROLLED EXPERIMENTATION

Do not perform an enormous uncontrolled search and report only the best experiment.

Create a research registry.

For every experiment, record:

- Unique experiment ID.
- Hypothesis.
- Input features.
- Target and horizon.
- Data availability cutoff.
- Training/evaluation dates.
- Algorithm.
- Hyperparameters.
- Number of model configurations tried.
- Random seed.
- Benchmark results.
- Out-of-sample metrics.
- Dependence-aware uncertainty.
- Failure analysis.
- Relevant code and artifacts.

Start with a small, diverse, predeclared experiment batch.

Use the results to eliminate clearly ineffective approaches.

Only expand promising hypotheses using new validation evidence or appropriately separated development data.

### Experiment priority

Prioritize in this order:

1. Data quality and historical availability improvements.
2. Stronger simple baselines.
3. Cross-sectional breadth and sector information.
4. Regularized feature selection.
5. Nonlinear interactions.
6. Regime-conditioned forecasting.
7. Direct return/distribution forecasting.
8. More complex sequence architectures, only when justified.

Do not assume this order guarantees the best performance; it is a research-efficiency priority.

---

# PHASE 8: CHALLENGE OUR PREVIOUS MODELS DIRECTLY

Reproduce the earlier weekly and monthly evaluations where the source data and artifacts permit.

Then investigate these specific questions:

### Question 1
Why did learned weights frequently underperform equal-weight combinations?

### Question 2
Why did probability calibration degrade historical performance?

Was the calibration dataset too small, the probability mapping unstable, or the original predictions already close to neutral?

### Question 3
Why did monthly directional accuracy collapse?

Investigate overlapping outcomes, changing market regimes, possible model misspecification, unstable features, and probability-to-classification thresholds.

### Question 4
Were important predictive relationships lost by modeling every feature group independently?

Would suitable interaction models perform better?

### Question 5
Are weekly and monthly horizons fundamentally different predictive problems?

Train them independently.

Avoid forcing them to share feature rankings, model families, or learned allocations.

### Question 6
Is NIFTY direction intrinsically difficult to forecast, while constituent behavior, market breadth, volatility, or return distributions are easier to predict?

Evaluate this as an empirical question.

### Question 7
Does a model predict better only when its confidence is high?

Investigate selective forecasting:

- High-confidence bullish.
- High-confidence bearish.
- Neutral/no-edge.

Thresholds must be determined using training data, and coverage must be reported.

A model predicting only 10% of days must not be compared to an always-active baseline using accuracy alone.

---

# PHASE 9: DEFINE WHAT COUNTS AS AN IMPROVEMENT

Do not select a winner based on accuracy alone.

Assess candidates using four dimensions.

## A. Probability quality

The model should improve proper probabilistic scores, particularly Brier and log loss, against relevant baselines.

## B. Directional usefulness

The model should identify directional outcomes better than suitable naive classifiers.

## C. Return/distribution quality

The model should improve return estimates, conditional probabilities, or distribution forecasts relative to historical controls.

## D. Robustness

The improvement should remain reasonably stable across time, regimes, and validation designs.

### Research qualification

A model can be described as promising if it demonstrates meaningful out-of-sample improvements that are not obviously explained by leakage, overlap, or post-selection.

A model can be considered independently validated only after genuinely fresh or otherwise untouched evaluation, adequate independent evidence, and defensible uncertainty estimates.

Do not silently weaken qualification standards because results are disappointing.

If the 2025–2026 sample is too small for reliable monthly validation, explicitly classify the result as exploratory.

**A null finding is preferable to a fabricated edge.**

---

# PHASE 10: INVESTIGATE PRACTICAL PREDICTIVE UTILITY

Accuracy is not the same as trading profitability.

After identifying a candidate with evidence of forecasting skill, independently investigate whether its forecasts could support useful decisions.

For research purposes, evaluate:

- Predicted positive versus negative return regimes.
- Selective participation.
- Risk reduction during predicted negative periods.
- Volatility-aware exposure.
- Confidence-conditioned decisions.
- Trading frictions and turnover.
- Benchmark comparisons.

Do not optimize an investment strategy against the same observations used to discover the predictive model and then claim the result is independently validated.

Keep forecasting research separate from trading strategy development.

Do not place real orders or modify live trading settings.

---

# PHASE 11: PRODUCE FINAL FORECASTS

Only after completing the experiments, produce separately frozen forecasts for:

**Horizon A:** Next five NIFTY trading sessions.

**Horizon B:** Next twenty-one NIFTY trading sessions.

Each forecast must include:

1. Exact issue timestamp and information cutoff.
2. Reference NIFTY close and source timestamp.
3. Exact future target session/date.
4. Probability of a positive return.
5. Probability of a negative or zero return.
6. Expected return.
7. Median return.
8. Expected endpoint price.
9. Central 50% and 80% endpoint intervals.
10. Predicted volatility or movement magnitude where supported.
11. Bullish, bearish, and neutral scenarios.
12. Main historically supported contributing signals.
13. Model and feature versions.
14. Out-of-sample performance of that specific frozen method.
15. Baseline comparisons.
16. Calibration and interval-coverage history.
17. Effective independent evaluation sample size.
18. Explicit limitations and uncertainty.

If a quantity cannot be estimated reliably, mark it **NOT VALIDATED** instead of presenting false precision.

Do not turn weak evidence into exaggerated statements like "high confidence bullish."

Every numerical probability must be clearly distinguished from a historically calibrated probability.

---

# PHASE 12: REQUIRED RESEARCH ARTIFACTS

Create versioned Markdown reports:

- `01_DATA_AUDIT.md`
- `02_FEATURE_DISCOVERY.md`
- `03_TARGET_RESEARCH.md`
- `04_MODEL_EXPERIMENTS.md`
- `05_VALIDATION_AND_LEAKAGE_AUDIT.md`
- `06_WEEKLY_FORECAST_RESEARCH.md`
- `07_MONTHLY_FORECAST_RESEARCH.md`
- `08_MODEL_COMPARISON.md`
- `09_FINAL_FORECASTS.md`
- `10_NEXT_RESEARCH_PRIORITIES.md`

Also save:

- Reproducible Python scripts.
- Frozen experiment configurations.
- Dataset/source hashes.
- Model artifacts.
- Out-of-sample predictions.
- Per-origin forecast and outcome records.
- Metrics and uncertainty calculations.
- Feature definitions.
- Rejected experiments and reasons.
- Leakage and data-quality test results.

Every result must be traceable back to the exact source observations, parameters, and executable code.

### Final comparison table

Include at least:

| Model | Horizon | OOS origins | Effective sample | Brier | Accuracy | MAE | Interval coverage | Baseline improvement |
|---|---|---|---|---|---|---|---|---|
| Neutral baseline | Weekly | | | | | | | |
| Momentum baseline | Weekly | | | | | | | |
| Best validated candidate | Weekly | | | | | | | |
| Neutral baseline | Monthly | | | | | | | |
| Momentum baseline | Monthly | | | | | | | |
| Best validated candidate | Monthly | | | | | | | |

Use actual results only. Do not fill unmeasured cells with estimates.

---

# EXECUTION INSTRUCTIONS

You are an autonomous research agent with permission to inspect existing research code, create new scripts, perform data analysis, execute backtests, and record findings.

**Do not stop after proposing a research plan. Execute the experiments that are feasible with the available data and computational resources.**

Work systematically:

1. Audit the environment and available historical inputs.
2. Reproduce and diagnose the old baselines.
3. Define valid forecasting targets and evaluation procedures.
4. Build a research-quality feature matrix.
5. Test diverse simple and nonlinear model families.
6. Investigate genuinely new signal combinations.
7. Compare all candidates on fair, matched historical evaluations.
8. Perform statistical and leakage audits.
9. Freeze new forward forecasts only when their information cutoff is valid.
10. Report findings, including failures and limitations.

Use efficient, reproducible computational experiments.

Do not waste compute on architectures that cannot reasonably be validated using the available observations.

Do not discard negative findings.

Do not claim that a model has discovered an edge simply because it produced an attractive backtest.

When multiple experiments fail, diagnose why instead of blindly increasing model complexity.

## MOST IMPORTANT DIRECTIVE

**I do not care whether you use 10 features or 1,000 features, logistic regression or sophisticated machine learning.**

I care whether you can demonstrate that information available today improves forecasts of NIFTY's future behavior.

Be creative in discovering predictive signals.

Be rigorous in validating them.

Challenge every assumption.

Separate predictive skill from randomness.

Optimize for genuine forecasting usefulness, not impressive-looking historical performance.

**Success means a repeatable predictive advantage supported by credible evidence. If that advantage cannot be demonstrated, explain precisely what is missing and what future observations would be needed to establish it.**

Begin with the existing research artifacts and execute Phase 1 immediately.