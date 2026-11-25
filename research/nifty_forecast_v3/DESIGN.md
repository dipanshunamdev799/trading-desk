# V3 predeclared experimental design

2025-01-01 onward only; all previous historical dates are research-exposed.
Fresh source acquisition is a revised vintage, not independent confirmation.
No trained model or preprocessing state from earlier work is imported.

Targets separately at 5 and 21 observed NSE sessions: endpoint direction and
return, median, seven fixed return buckets at -5/-2/-0.5/+0.5/+2/+5 percent,
absolute move, annualized future RMS volatility, and path breach below -2%/-5%.
Causal origin regimes: sign/trend-strength, training-median volatility, sector
participation, expiry proximity, global risk-off, preceding-large-move status.

Fixed outer stress evaluation: forecast origins from 2026-07-01 onward whose
complete horizon has matured by 2026-11-16. Also report earlier prequential
development origins from first 126 matured training targets. Monthly outer
refits. One extra-session embargo: training endpoint strictly before the current
decision close, and strictly before inner validation decision closes. Last 42
eligible training origins are inner validation; earlier targets purge by their
endpoint. A candidate/configuration selection may use only that inner set.
Minimum inner training 80 labels; no test-driven feature selection.

Predeclared batch (15 configurations, independently trained per horizon):
- Empirical unconditional distribution (rolling latest252 matured labels).
- Recency-weighted empirical distribution (half-life63).
- Realized-risk-scaled historical distribution (RV21, scale clipped .5..2).
- VIX-based risk scaling of historical residual returns (same clip).
- Momentum-conditioned distribution, positive/negative 21-day trend; shrink
  conditional sample toward unconditional with 30 pseudo-observations.
- Mean-reversion-conditioned distribution, sign of 5-day return reversed.
- Causal regime-conditioned distribution (trend sign x high/low RV; same shrink).
- Ridge/logistic price-only (alpha100, classifier C=.1).
- Ridge/logistic full eligible context (same; direct RV and tail targets).
- ElasticNet/logistic elastic net (alpha .001/.01; L1 ratio .5; two configs).
- Training-only correlation-pruned Ridge (threshold .9, alpha100).
- LightGBM shallow interaction/distribution model (depth2, 4 leaves, 80 trees,
  minimum40 rows/leaf, learning_rate .04, L2=10; direct mean, seven quantiles,
  direction, future log-volatility and -2% path-breach targets).
- Historical analogues, 30 nearest robust-scaled price/volatility/sector/FO
  states, distance weights and 30-observation unconditional shrinkage.
- Structured lags (1/3/5 prior sessions of core features), Ridge alpha100.

Full context includes price/sector/global/ETF/intraday/official-FO features.
FII data are short-history and explicitly sparse. Official FO and FII values
are lagged one extra domestic session. Current-member basket features are
research-only and excluded from primary candidate/selector eligibility.
Prespecified ablations: price+sectors, full-minus-FO, full-plus-current-basket,
and full context with four fixed interactions (momentum x RV, breadth x return,
sector dispersion x RV, FII positioning x trend). These are four extra configs;
thus 19 total configurations, no further expansion based on outer results.

Inner-only selectors independently choose direction by Brier, mean return by
MAE, distribution by CRPS, volatility by QLIKE, and path-breach by Brier.
For final descriptive leaderboard, best outer candidate is explicitly post-
selection/exploratory; it cannot become independently validated. Report selector
versus strongest fixed baseline and all configs, including failures.

No posthoc calibration of weak classifiers into precise price intervals. Linear
models use residual sizes from purged inner validation (fallback empirical
distribution is flagged). LightGBM directly fits quantiles; crossings are sorted
and count is reported. Quantile-grid distribution tails are extrapolated and
marked NOT VALIDATED. Each classifier and return distribution's implied direction
are separate outputs. Return/quantile/volatility/tail models scored separately.

Distribution scores: empirical CRPS, pinball, bucket Brier, 50/80 coverage and
width, mean MAE/RMSE, volatility QLIKE/MAE, tail Brier; direction Brier/log loss/
accuracy/balanced accuracy/calibration. Report regime and temporal splits.
Paired bootstrap block2H, 2,000 resamples only with at least8H origin rows;
non-overlapping subsets and loss autocorrelation effective-size diagnostics.
Multiple-configuration comparisons use simultaneous bootstrap max-deviation
intervals and are still exploratory. Monthly independent counts remain small.

Feature discovery and stability selection use only pre-2026-07-01 matured
development labels: rank IC, block-shift nulls, train-only redundancy clustering,
univariate OOS and coefficient signs. No final-test feature ranking as selection.

Negative controls: future-column sentinel rejected via availability metadata;
future/raw/pre-2025 perturbation invariance; unfinished-label exclusion; a
block-shifted target control with the same purging; independent randomized
direction labels. Thresholds for selective forecasts (training-only 80th
percentile absolute distance from .5, floor .05) freeze before test; report
coverage and matched-date baselines. No neural sequence architecture: fewer
than500 daily rows and at most about22 independent monthly targets cannot support
credible validation of additional RNN/Transformer parameters. HMM, XGBoost and
CatBoost not added as near-duplicate sweeps; causal regime model, structured lags
and one shallow boosted implementation cover the mechanisms with a finite budget.

Practical utility only if a candidate survives forecasting qualification. Without
that, record NOT QUALIFIED rather than optimize a trading strategy on the same
sample. No orders, live settings, unattended schedules or future-2027 scope.
