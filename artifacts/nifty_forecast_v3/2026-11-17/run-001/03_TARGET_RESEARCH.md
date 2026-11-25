# 03 — Independently defined prediction targets

Weekly=5 and monthly=21 actual observed NSE sessions. Endpoint return is
C[t+h]/C[t]-1. Separate evaluated targets: direction, direct mean return, median,
absolute magnitude, full return distribution, annualized future RMS volatility,
and path breaches below -2% and -5%. Seven fixed endpoint-return buckets use
-5%, -2%, -.5%, +.5%, +2%, +5% boundaries. None was chosen using outer outcomes.

All labels carry endpoint dates. A row can train any layer only when its endpoint
is **strictly earlier** than the new decision's completed-session origin. The
extra-session embargo applies inside inner validation too. Actual session bars,
including valid special sessions, define horizon length; future dates use the
published NSE calendar. Known 2025/2026 historical index calendars were checked
in earlier audits; the fresh complete 465-session index agrees with official FO
underlying on all 465 dates, maximum difference 0 points.

Volatility is sqrt(252*mean(future daily log-return squared)). A path breach is
min(future daily closes)/origin close-1, not a reconstructed intraday drawdown.
The future trend/transition state is **NOT VALIDATED**: V3 tests causal origin-
regime-conditioned return forecasts, not a certified forecast of latent regimes.

Return models regress future returns directly. Linear residual distributions
use purged inner held-out residuals; boosted models directly fit seven quantiles.
Quantile crossings are sorted and counted. Beyond 5/95 percentiles, tail
extrapolation is explicitly NOT VALIDATED. This replaces the earlier sign-only
mixture, but it does not guarantee coverage. Independent target selectors can
disagree; no joint coherence or calibrated probability claim is made.

Direction: Brier/log loss/accuracy/balanced accuracy/calibration. Returns:
MAE/RMSE/median MAE. Distribution: empirical CRPS, pinball, seven-bucket Brier,
50/80% interval coverage and width. Risk: volatility MAE/QLIKE and path-tail Brier.
Origin regimes use only observed trend, training-median RV, participation, expiry,
global risk-off and preceding large moves. Conditional diagnostics are descriptive;
no favorable slice becomes an independently validated subgroup edge.

Novel insight: different targets prefer different methods, and selecting a model
for return MAE does not establish direction, volatility or interval skill. Current
cross-target inconsistencies are recorded in the final JSON rather than hidden.
