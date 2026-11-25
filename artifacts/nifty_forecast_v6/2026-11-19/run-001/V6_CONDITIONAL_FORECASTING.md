# NIFTY V6 — Conditional Forecasting

Generated 2026-11-20T20:42:49.611145+05:30. Run `2026-11-19/run-001`; historical input boundary 2025-01-01 through 2026-11-17. All evaluation history is research-exposed. No independent forecasting edge is established. No trading or deployment.

## Rules fixed for the analysis batch

Before computing this batch's slice scores, the analysis registry recorded directional confidence cutoffs.55/.65/.75 on both bullish and bearish sides, their either-side union, I03/L01 parent agreement, and a forecast80% interval narrower than.8 times the same-origin training historical interval. This is an exposed-history analysis plan, not a pre-history preregistration. All135 system/horizon rows were examined; these slices introduce further multiplicity beyond whole-system search.

“Agreement” refers to I03 and L01's signs; it does not guarantee that another candidate agrees with them. A narrow conditional interval measures model uncertainty, not independently validated reliability. Coverage below is the fraction of all eligible candidate origins selected by the rule; `coverage80` is interval coverage within those selected outcomes. They are different quantities.

| model | rule | n | coverage | disjoint_n | accuracy | brier | crps | coverage80 | I03_matched_accuracy | I03_matched_brier | L01_matched_crps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F_NO_DEFENSIVE | either_conf_0.55 | 89 | 0.967391 | 19 | 0.797753 | 0.166982 | 0.010039 | 0.797753 | 0.764045 | 0.178633 | 0.009875 |
| F_NO_DEFENSIVE | either_conf_0.65 | 64 | 0.695652 | 16 | 0.828125 | 0.147044 | 0.009583 | 0.796875 | 0.828125 | 0.150793 | 0.009008 |
| F_NO_DEFENSIVE | either_conf_0.75 | 19 | 0.206522 | 7 | 0.947368 | 0.081724 | 0.011946 | 0.684211 | 0.947368 | 0.107538 | 0.009962 |
| F_NO_DEFENSIVE | agree_I03_L01 | 71 | 0.771739 | 17 | 0.760563 | 0.169998 | 0.010827 | 0.788732 | 0.774648 | 0.173314 | 0.010477 |
| F_NO_DEFENSIVE | narrow80_vs_historical | 12 | 0.130435 | 5 | 0.666667 | 0.200322 | 0.017193 | 0.583333 | 0.583333 | 0.254967 | 0.019049 |
| Q_ETF_VOLUME | either_conf_0.55 | 76 | 0.826087 | 18 | 0.815789 | 0.167661 | 0.010149 | 0.750000 | 0.802632 | 0.166854 | 0.010284 |
| Q_ETF_VOLUME | either_conf_0.65 | 45 | 0.489130 | 13 | 0.844444 | 0.142326 | 0.012380 | 0.644444 | 0.844444 | 0.143795 | 0.012158 |
| Q_ETF_VOLUME | either_conf_0.75 | 14 | 0.152174 | 4 | 0.928571 | 0.087651 | 0.016159 | 0.642857 | 0.928571 | 0.089715 | 0.015065 |
| Q_ETF_VOLUME | agree_I03_L01 | 71 | 0.771739 | 17 | 0.760563 | 0.175607 | 0.010634 | 0.746479 | 0.774648 | 0.173314 | 0.010477 |
| Q_ETF_VOLUME | narrow80_vs_historical | 9 | 0.097826 | 2 | 0.555556 | 0.263266 | 0.012426 | 0.777778 | 0.555556 | 0.256539 | 0.013396 |
| W2_DEF_NORM | either_conf_0.55 | 85 | 0.923913 | 18 | 0.788235 | 0.164455 | 0.009526 | 0.776471 | 0.764706 | 0.176806 | 0.009399 |
| W2_DEF_NORM | either_conf_0.65 | 54 | 0.586957 | 14 | 0.907407 | 0.117410 | 0.009904 | 0.759259 | 0.907407 | 0.132372 | 0.009590 |
| W2_DEF_NORM | either_conf_0.75 | 14 | 0.152174 | 6 | 0.928571 | 0.091345 | 0.013414 | 0.571429 | 0.928571 | 0.094263 | 0.010963 |
| W2_DEF_NORM | agree_I03_L01 | 71 | 0.771739 | 17 | 0.760563 | 0.168018 | 0.010888 | 0.774648 | 0.774648 | 0.173314 | 0.010477 |
| W2_DEF_NORM | narrow80_vs_historical | 13 | 0.141304 | 4 | 0.615385 | 0.233221 | 0.017433 | 0.615385 | 0.538462 | 0.268679 | 0.018309 |
| W2_NOAUTO_VOLUME | either_conf_0.55 | 75 | 0.815217 | 18 | 0.813333 | 0.162880 | 0.010089 | 0.760000 | 0.800000 | 0.167434 | 0.010393 |
| W2_NOAUTO_VOLUME | either_conf_0.65 | 48 | 0.521739 | 14 | 0.895833 | 0.124336 | 0.011597 | 0.666667 | 0.875000 | 0.135398 | 0.011718 |
| W2_NOAUTO_VOLUME | either_conf_0.75 | 19 | 0.206522 | 6 | 0.894737 | 0.107016 | 0.014623 | 0.631579 | 0.894737 | 0.104914 | 0.013703 |
| W2_NOAUTO_VOLUME | agree_I03_L01 | 71 | 0.771739 | 17 | 0.746479 | 0.172252 | 0.010462 | 0.746479 | 0.774648 | 0.173314 | 0.010477 |
| W2_NOAUTO_VOLUME | narrow80_vs_historical | 12 | 0.130435 | 4 | 0.500000 | 0.295217 | 0.011906 | 0.666667 | 0.333333 | 0.319684 | 0.012719 |


Every displayed I03 accuracy/Brier and L01 CRPS is calculated on the candidate's exact selected dates. A selective accuracy can rise simply by selecting an easy market period for every method, so the matched control matters more than its unfiltered full-sample score. Small tail/high-conviction subsets have very few disjoint outcomes. No narrower confidence interval, optimized new threshold, annualized trading result or selective win-rate claim is inferred from them.

## Calibration and regime inspection

`confidence-slices.json` contains every nonempty bullish, bearish, either-side, agreement and narrow-interval slice, including unattractive ones and monthly slices. `regime-slices.json` separates the original predetermined volatility, trend and global-risk labels and reports sample size, disjoint count, coverage, proper scores and matched I03 Brier gain. Thresholds based on regime medians are derived from the corresponding training partition; no future regime assignment enters fits.

`metrics.json` includes fixed probability-bin counts, predicted versus observed rates and expected calibration error for every complete candidate. Conditional bins are descriptive, not independently calibrated confidence guarantees. High confidence with poor observed frequency can be worse than a modest probability even when classification accuracy looks attractive. There is no external calibration holdout because the entire available history has been used for research.

## Decision

Use the registered slices to specify future falsifiable questions, not to cherry-pick an attractive threshold. Retain coverage, matched control and interval calibration alongside accuracy. Weekly parent agreement and conservative group-regularized probabilities are leads for future collection; this sample does not establish a dependable selective forecasting policy. Monthly confidence claims remain especially weak with about four disjoint windows before subdivision. No signal is used to place orders or change the existing desk.

The primary weekly sample has 92 overlapping origins and 19 greedily selected disjoint five-session outcomes. The monthly sample has 76 overlapping origins and only four disjoint 21-session outcomes. These are not 92 and 76 independent trials. All configurations and their selection were developed on exposed 2025–2026 history.

Returns, interval widths, return MAE/RMSE and CRPS use fractional returns: 0.01 is one percentage point. Accuracy, coverage and probabilities are fractions. Brier and CRPS are losses; lower is better. Improvement/gain means parent or benchmark loss minus candidate loss.
