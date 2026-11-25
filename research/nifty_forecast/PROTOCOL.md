# NIFTY session direction experiment

Frozen design for the 17 November 2026 pre-market experiment. This is a
prediction study of the cash index, with no orders or option profit claims.

## Questions and information cutoff

Primary: will the official NIFTY daily close exceed the preceding session's
official close? Secondary: will the close exceed today's opening level?
These are separate labels. A positive overnight gap need not mean a positive
open-to-close session. Also estimate the distribution of closing returns.

Freeze raw inputs with acquisition times and hashes. Use only completed Indian
sessions before the forecast date. Daily bar timestamps identify sessions, not
their publication times. Historical reconstruction assumes a completed bar was
available by the next session; it is not a vintage or broker-latency replay.
Today's global partial-session quotes are commentary inputs, not historical
final-close features. Undated or stale options are disclosed, never treated as
fresh. Preserve the complete dashboard catalog, including unavailable concepts
(127 concepts in the current catalog).

## Fixed candidates (no parameter search)

1. Rolling unconditional upward frequency (the main probability baseline).
2. Previous-day direction and 20-session trend (simple directional baselines).
3. L2 logistic regression on NIFTY's own completed price features.
4. L2 logistic regression with sector leadership, breadth, India VIX and the
   latest safely completed global daily sessions (if the provider supplies history).
5. Distance-weighted 60-nearest historical analogues using the same context.
6. Nonlinear logistic regression using 64 fixed random Fourier features.
7. Equal-weight ensemble of candidates 4, 5 and 6, fixed before evaluation.

Use the most recent 504 eligible completed target sessions for chronological
walk-forward evaluation, at least 504 training examples and at most the
preceding 1,260. Refit on each target calendar month. At a refit all training
labels must already be resolved before that month's first decision. Scaling,
imputation and all fitted coefficients use that training set alone. Bound
probabilities to [0.05, 0.95]. Logistic penalty is fixed at 10; nonlinear penalty
at 20; seed 20261117. Missing contextual inputs use training-set medians with
missingness flags. No model is promoted by its final-period result; report the
predeclared ensemble even if a baseline beats it.

## Scoring and uncertainty

Report sample count, direction accuracy, Brier score, log loss and calibration
bins for both labels. Compare paired Brier losses with the unconditional
baseline using 2,000 resamples of consecutive ten-session blocks. Include the
two halves of the evaluation period and high-confidence coverage. These are
conditional diagnostic intervals after an exploratory choice of models, not
confirmatory significance tests or a market-stationarity assumption.

Construct central 50% and 80% closing-return prediction intervals from the
preceding 252 resolved sessions' realized returns; compare with the 60 analogues'
empirical distribution. They are empirical forecast distributions, not confidence
intervals for the mean and not a guarantee that the intraday path stays inside.
Report walk-forward interval coverage. Session-high/low excursions are separate.

Dashboard options, international markets, flows and news can inform a written
scenario assessment. Without adequate timestamped historical coverage they do
not acquire invented fitted weights or an invented probability of success.
Correlated technical indicators and overlapping sectors are not independent votes.
For a 00:30 IST decision, a US daily bar for the previous calendar date may
still be in progress. Global history therefore requires its session date to
be strictly earlier than target date minus one calendar day. This conservative
daily convention discards partial US information instead of leaking its final close.

## Forward record

Save a timestamped, immutable forecast with the target date, reference close,
probabilities, intervals, raw-input hashes, model definition and unresolved
outcome fields. A later score command may write a separate outcome artifact;
it must not rewrite the original call. Do not use a scheduled automation.
