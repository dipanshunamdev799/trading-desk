# Strict two-calendar-year rerun

User-directed restriction: only 17 November 2024 through 16 November 2026 may
contribute raw market observations, feature initialization, training labels,
prediction-error history, calibration or empirical return bands. Today's target
remains 17 November 2026. The first available Indian session is 18 November 2024.
Reuse the original dated input freeze; this isolates the history-window change.
Raw archived files contain earlier records, but clip every series before deriving
any feature. Do not import fitted states, coefficients, analogues or predictions
from a longer-history run.

Keep the existing 71-feature / 12-group method, penalties, recency half-lives,
252-row expert requirement, 126-prior-OOS evidence gate and monotone calibration.
The former 504-row overall startup holdoff cannot fit within a strict two-year
sample. Start expert predictions after 252 eligible feature rows, the existing
expert minimum. Rolling indicators consume their required observations inside
the window; EMAs and RSI initialize at its first observation. Monthly historical
refits and a fresh current fit remain unchanged.

Report all chronological predictions after initial expert training, then
separately report decisions with at least 126 resolved meta-training and
calibration examples. Select that evaluation by information availability, not
performance. Compare all fixed controls on the identical dates and disclose
their sample sizes. No claim of two full years of out-of-sample tests when the
same two years must also train the model. No hyperparameter search.

Recalculate current weights, coefficients, both directional estimates and the
trailing-252 empirical bands. Do not copy longer-history analogue statistics into
the new forecast. Preserve the earlier forecasts. Verify that changing values
before the boundary leaves the bounded features unchanged and that every fitted
training / calibration / meta label stays inside the window and precedes the
corresponding decision.

The data vintage, publication-clock assumptions, undated-options exclusions and
Monday provisional quote reconstruction remain as disclosed in the earlier
reports. This reused historical period is exploratory; today's outcome remains
unresolved.
