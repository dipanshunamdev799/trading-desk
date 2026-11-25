# Historical-error-weighted NIFTY inputs

Design frozen before this extension's model results were inspected. The first
17 November forecast stays unchanged. This extension learns feature coefficients
and learns group weights from earlier predictions' realized errors.

## Information and evaluation boundaries

Reuse the hashed price freezes, completed-session labels and conservative global
clock from the first experiment. Add separately frozen Upstox institutional
history, available only since April 2026, using overlapping 35-calendar-day
anchor requests plus the saved current window because the endpoint returns at
most 30 trading days. Actual returned session dates govern joins; the observed
windows end around the requested anchor despite its documented start-date name.
For a historical
decision after the preceding Indian session, institutional EOD values are assumed
available by 00:30 IST. Publication times/vintage revisions are not reconstructed;
this assumption is disclosed. No absolute cash amount is interpreted as crore.
Use (buy-sell)/(buy+sell), which cancels a common positive unit scale.

The latest 504 target sessions are a fixed outer evaluation, with the latest 126
also reported separately. Earlier history supplies model fitting and historical
predictions for learning weights. All fitted weights at a target use only labels
resolved by its preceding decision day. The outer period was already inspected
in the earlier study: this is exploratory reuse, not an untouched confirmatory
holdout. The next session outcome is still forward and unresolved.

## Two learned layers and probability calibration

1. Partition features into disjoint, interpretable groups: trend, short-term
   price, candle shape/gaps, volatility, banks/financials, other sectors,
   participation, global equities, oil/currency, GIFT Nifty, institutional cash,
   and FII derivative positioning. Each group's L2 logistic expert learns signed
   standardized input coefficients. Monthly refits use at most 1,260 completed
   targets, exponential recency weights with a 252-session half-life, and fixed
   L2 penalty 25. At least 252 observed training rows are required for established
   groups, 63 for the separate short-history institutional experts. Availability
   requires at least half of a group's raw features; imputation and scaling are
   fitted only on eligible training rows. Missingness flags are explicit.
2. Retain each expert's genuinely chronological out-of-sample predictions. At
   every next decision, fit nonnegative blend weights summing to one by minimizing
   recency-weighted Brier loss over the last 504 resolved predictions. Meta-loss
   half-life is 126 sessions. Include a neutral 50% expert. A fixed 0.005 squared
   penalty toward the neutral expert limits fragile concentration. A group needs
   at least 126 prior out-of-sample predictions, adequate current inputs, and at
   least 252 observed training rows before it can enter the primary blend.
   Experts with shorter history are recorded and scored in shadow, with zero
   primary allocation; zero here means insufficient evidence, not irrelevance.
3. The primary forecast is that adaptive blend passed through a monotone logistic
   calibrator fitted only to its preceding 252 chronological forecasts, with at
   least 126 examples. Fit an intercept and a nonnegative slope (maximum 3), with
   fixed penalty 10 toward intercept 0 and slope 1. A weighted-Brier adaptive
   blend and an equal-group blend are retained as controls; there is no result-
   based winner selection. Report the neutral 50/50 and prior experiment controls.

No parameter grid or performance-triggered replacement of this design. Preserve
monthly expert fits, daily group allocations, per-feature signed coefficients,
raw and calibrated forecasts, source hashes, all candidate scores and group
eligibility reasons. Expert intercepts and missingness effects are not invented
as named raw input weights. Group percentages are actual probability-blend
allocations; per-feature logistic coefficients act inside those groups. These
are distinct quantities and neither is a causal effect.

## Scoring and forward use

Report Brier loss, log loss, accuracy, calibration bins, first/second halves,
latest 126 sessions, neutral/frequency controls and 2,000 ten-session-block paired
intervals. Include the 503-session subset excluding Monday's provisional target.
Produce daily allocation and cumulative loss charts. Run targeted leakage tests
by changing future labels and inputs and confirming earlier weights are identical.

Save a new immutable, dated forecast rather than editing the first call. The
existing outcome scorer can evaluate this forecast in its own directory. Future
reruns learn new weights only after new outcomes have resolved. This is a local
research workflow, not an unattended watcher or a scheduled automation.
