# NIFTY V7 · Signal Discoveries

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

1. Defensive duplication changes the fitted Ridge law without any new information. Weekly Brier changes .182047 → .188090. Compensating copy weights restore .182047. Targeted six-feature downweighting works better historically than generic PCA, supporting the V6 regularization explanation. It does not resolve the economic value of the underlying defensive indices.
2. Domestic rotation differences give the best V7 probability point result. The domestic two-feature addition gains .007658 Brier against the frozen V6 Brier leader. Its short-window failure and the competitive lagged broader rotation control limit the timing inference.
3. Cluster-balanced Elastic Net and the earlier-cutoff sensitivity improve distribution score while giving up direction quality. Raw Elastic Net is much worse in the directly matched scaling contrast. Shorter training is a material failure mode.
4. Daily opening/closing and actual ETF activity are a complementary weekly lead. Direct intraday realized-volatility and position data do not presently add value to their matched controls. Current-stock results require historical membership verification.
5. Current sector topology, rolling factors, global correction models and most nonlinear alternatives give weak or negative additions. The smaller domain-specific representation outperformed broad unsupervised compression in weekly direction.
6. Monthly lagged-state probability gains survive some comparisons but shifted controls remain competitive in CRPS. Separate persistent factors, Student laws and the global block do not establish robust monthly performance.

| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| C_CLUSTER_BAL | C_RAW | brier | 92 | 0.004533 |
| C_CLUSTER_BAL | C_RAW | crps | 92 | 0.000004 |
| C_DEF | C_RAW | brier | 92 | 0.012184 |
| C_DEF | C_RAW | crps | 92 | 0.000104 |
| C_ELASTIC | C_CLUSTER_BAL | brier | 92 | -0.007094 |
| C_ELASTIC | C_CLUSTER_BAL | crps | 92 | 0.000500 |
| C_PRUNE | C_RAW | brier | 92 | 0.008041 |
| C_PRUNE | C_RAW | crps | 92 | 0.000190 |
| G_DIRECT5 | G_BASE5 | brier | 92 | -0.007388 |
| G_DIRECT5 | G_BASE5 | crps | 92 | -0.000141 |
| G_INTERMEDIATE5 | G_BASE5 | brier | 92 | -0.023178 |
| G_INTERMEDIATE5 | G_BASE5 | crps | 92 | -0.000470 |
| L_DAILY | C_NO_DEF | brier | 92 | 0.003079 |
| L_DAILY | C_NO_DEF | crps | 92 | 0.000175 |
| S_STATE | S_LEVEL | brier | 92 | -0.005940 |
| S_STATE | S_LEVEL | crps | 92 | -0.000320 |
| S_STATE_ACCEL | S_LEVEL | brier | 92 | 0.005146 |
| S_STATE_ACCEL | S_LEVEL | crps | 92 | 0.000179 |
| T_DAY_ETF | C_NO_DEF | brier | 92 | 0.003278 |
| T_DAY_ETF | C_NO_DEF | crps | 92 | 0.000094 |
| T_DAY_OC | C_NO_DEF | brier | 92 | 0.001322 |
| T_DAY_OC | C_NO_DEF | crps | 92 | 0.000075 |
| T_ROT_DOMESTIC | C_NO_DEF | brier | 92 | 0.007658 |
| T_ROT_DOMESTIC | C_NO_DEF | crps | 92 | 0.000141 |


This ordering is an interpretation of paired experiments, separate from the numerical whole-system leaderboards. Each hypothesis retains its immediate control. A higher full-system rank can come from weaker regularization, sample restriction or several jointly changed inputs. The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.
