# Five-session and twenty-one-session forecast experiment

Retain the user's strict two-year input boundary: 17 November 2024 through
16 November 2026, with no older indicator initialization. Reuse the earlier
frozen price context and separately saved institutional history. Forecast from
the 16 November 2026 close for the next 5 observed NSE trading sessions (week)
and 21 sessions (month). Expected endpoint dates use a separately frozen current
Upstox NSE calendar, corroborated by the official NSE 2026 holiday circular.
Trading-session count is the outcome definition if the future calendar changes.

## Targets and when an answer becomes available

For a decision after session t's close, label the return C[t+h]/C[t]-1, h=5 or
21. A training, weighting or calibration row is eligible only if its endpoint
session has closed by the decision. Merely being an earlier forecast origin is
not sufficient. Fit horizon-specific coefficients, group allocations and
calibrators. Do not compound or stretch the daily forecast.

Use the same 71 features, 12 disjoint groups, fixed logistic penalty 25,
252-session expert recency half-life, 126-session meta half-life, 0.005 neutral
shrinkage, and monotone calibrator penalty 10. No parameter search. Historical
experts refit monthly, with the current call freshly fitted. Established groups
need 252 matured training labels; short-history institutional experts need 63
for shadow predictions and 252 plus 126 matured OOS errors for primary use.
The first expert decision starts after 252+h-1 feature rows, allowing 252
matured h-session labels. Primary weighting and calibration each require 126
earlier, fully matured out-of-sample outcomes. All these thresholds count
overlapping rows, not independent weeks/months; disclose that limitation.

## Return magnitudes and ranges

At each decision retain up to the latest 252 matured horizon returns. Separate
their positive and nonpositive observations, allocating total probability p
to the positive sample and 1-p to the nonpositive sample, where p is the
predeclared calibrated adaptive sign estimate. Inside each subset distribute
mass equally. Report mixture median/mean, central 50% and 80% quantiles and
corresponding index levels. This assumes historical conditional move sizes
persist; it is not a separately fitted return regressor or a guaranteed range.
Also retain unconditional empirical reference quantiles and score median MAE
and interval coverage chronologically. Never use unfinished h-session returns
for a current magnitude distribution.

## Honest evaluation of overlapping outcomes

Report all post-training forecasts and separately those with fully learned
weights/calibration, selected by evidence availability, not performance.
Compare neutral 50/50, rolling matured-label frequency, equal eligible groups,
raw adaptive weights and the predeclared calibrated primary on identical dates.
Include always-up/always-down direction accuracies and an unconditional median
return control. Count a greedily selected non-overlapping evaluation subset
whose next origin is no earlier than the previous endpoint. Score it separately.

Use 2,000 paired moving-block resamples with block length 2*h, only when at
least 8*h evaluated origin rows exist. Otherwise omit the interval and report
insufficient independent history. Do not use daily ten-session blocks for
21-session targets or label overlapping monthly forecasts independent tests.
Report published-only subsets excluding targets whose endpoint uses Monday's
provisional quote. This is exploratory reuse of the same historical period.

## Forward record

Freeze separate week/month outcomes, endpoint dates, horizon-native levels,
probabilities, weights, inputs/code hashes and unresolved outcome fields. A
manual scorer may write a separate outcome artifact once each horizon has
enough published daily candles. Preserve all earlier daily and two-year calls.
No unattended watcher, scheduled automation or orders are part of this request.
