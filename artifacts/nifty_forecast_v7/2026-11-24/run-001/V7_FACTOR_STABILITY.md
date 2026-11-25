# NIFTY V7 · Factor Stability

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

Each fold uses an expanding supervised fit. For diagnostics, loadings also come from the first and latest 126 matured training-origin observations. PC signs are oriented by their largest absolute loading for display. Structural drift is measured using an absolute first-factor dot product and principal angles for the six-dimensional subspaces, both insensitive to sign. Cluster stability uses the Jaccard similarity of pairs assigned to a common cluster at successive cutoffs.

| horizon | fold | training_n | clusters | effective_rank | residual_rank | first_share | early_rank | recent_rank | early_recent_top_factor_abs_cosine | early_recent_max_principal_angle_deg | prior_fold_cluster_pair_jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 2026-07 | 300 | 25 | 12.470290 | 13.122827 | 0.268895 | 10.035574 | 9.537322 | 0.418346 | 80.134154 | — |
| 5 | 2026-08 | 323 | 26 | 12.778413 | 13.316477 | 0.264244 | 10.028723 | 9.911357 | 0.570908 | 77.711737 | 0.818182 |
| 5 | 2026-09 | 344 | 25 | 12.886202 | 13.396853 | 0.262024 | 10.045413 | 9.392477 | 0.578485 | 78.924080 | 0.947368 |
| 5 | 2026-10 | 365 | 25 | 12.959603 | 13.458463 | 0.262018 | 10.034908 | 8.979697 | 0.624781 | 83.978340 | 1.000000 |
| 5 | 2026-11 | 385 | 25 | 12.752177 | 13.164247 | 0.278768 | 10.039395 | 8.431032 | 0.609935 | 76.203698 | 1.000000 |
| 21 | 2026-07 | 284 | 25 | 12.261115 | 13.058475 | 0.273799 | 10.043947 | 8.688049 | 0.529728 | 82.213536 | — |
| 21 | 2026-08 | 307 | 25 | 12.548802 | 13.158263 | 0.266661 | 10.045980 | 9.738681 | 0.471449 | 77.289231 | 1.000000 |
| 21 | 2026-09 | 328 | 26 | 12.755828 | 13.238676 | 0.264419 | 10.023420 | 9.863079 | 0.607262 | 85.952668 | 0.818182 |
| 21 | 2026-10 | 349 | 25 | 12.927281 | 13.430418 | 0.261422 | 10.043961 | 9.313110 | 0.578149 | 81.488262 | 0.947368 |


The first weekly fold has first-factor cosine 0.418 between early and recent training windows and worst six-factor angle 80.1°. The cluster groupings can stay relatively stable while factor directions drift. The windows compare overlapping market histories across folds, so these are descriptive structural diagnostics.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_RAW | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.012959 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| C_PCA | 92 | 0.706522 | 0.714804 | 0.192759 | 0.573758 | 0.011034 | 0.014152 | 0.013829 | 0.021020 | 0.554348 | 0.760870 | 0.042095 |
| C_PCA_ROLL | 92 | 0.706522 | 0.714804 | 0.207871 | 0.606140 | 0.011273 | 0.014718 | 0.014295 | 0.021525 | 0.543478 | 0.760870 | 0.039362 |
| C_PCA_WHITE | 92 | 0.717391 | 0.714078 | 0.199695 | 0.588701 | 0.011275 | 0.014593 | 0.014104 | 0.021574 | 0.510870 | 0.739130 | 0.038624 |
| C_PCA_LW | 92 | 0.717391 | 0.714078 | 0.199401 | 0.588048 | 0.011266 | 0.014577 | 0.014092 | 0.021556 | 0.521739 | 0.739130 | 0.038765 |
| C_SPARSE | 92 | 0.717391 | 0.724238 | 0.198999 | 0.587460 | 0.011183 | 0.014516 | 0.013862 | 0.021522 | 0.554348 | 0.771739 | 0.040904 |


Rolling PCA estimates directions from the latest 126 observations while keeping the supervised regression training dates fixed. The weekly Brier rises from .192759 with full training PCA to .207871 with recent directions. At 21 sessions it rises from .292750 to .402258. Adaptation did not overcome estimated loading variation in this cohort. Generalization to a future break is unresolved. `factor-loadings.csv`, `factor-stability.csv` and `cluster-definitions.json` retain the loadings and reconstruction details. A feature map can identify recurring redundancy without resolving stable predictive factors.

The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.
