# NIFTY V8 · Joint Probability Distribution

Run `2026-11-24/run-001`. Retrospective research.

All complete forecasts use one finite return law. Up probability, median, expected endpoint price, ordered quantiles, tail probabilities and bucket masses are computed from its atoms and weights. The empirical reference uses conditional residuals with 35% historical shrinkage. Alternatives include Student df5 with shrunk residual scale, heavier weight on validation residuals in the same volatility or rotation-magnitude state, and regularized five-quantile interpolation with bounded tails. The latter limitation matters for very rare outcomes. Interval coverage is a separate diagnostic from endpoint tail mass, and neither estimates time-to-barrier or intra-period drawdown.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038767 |
| G_ROT_ELASTIC | 92 | 19 | 0.739130 | 0.716014 | 0.164496 | 0.507809 | 0.009499 | 0.012158 | 0.018420 | 0.004758 | 0.608696 | 0.793478 | 0.039427 |
| D_STUDENT | 92 | 19 | 0.619565 | 0.669811 | 0.215439 | 0.618943 | 0.010110 | 0.014195 | 0.018859 | 0.004991 | 0.478261 | 0.826087 | 0.042875 |
| D_RISK | 92 | 19 | 0.782609 | 0.791001 | 0.162853 | 0.506027 | 0.009854 | 0.012832 | 0.019107 | 0.004947 | 0.554348 | 0.771739 | 0.036819 |
| D_FACTOR | 92 | 19 | 0.782609 | 0.787615 | 0.162364 | 0.504999 | 0.009935 | 0.012858 | 0.019386 | 0.004991 | 0.521739 | 0.815217 | 0.038337 |
| D_QUANTILE | 92 | 19 | 0.554348 | 0.613208 | 0.254641 | 0.703889 | 0.010998 | 0.014941 | 0.019359 | 0.005368 | 0.391304 | 0.684783 | 0.037170 |
| D_ELASTIC_RISK | 92 | 19 | 0.782609 | 0.780842 | 0.184935 | 0.554948 | 0.009673 | 0.012612 | 0.018270 | 0.004883 | 0.521739 | 0.804348 | 0.043272 |
| J_EQUAL | 92 | 19 | 0.804348 | 0.806483 | 0.168397 | 0.519272 | 0.009530 | 0.012442 | 0.018550 | 0.004799 | 0.586957 | 0.826087 | 0.042975 |
| J_LEARNED | 92 | 19 | 0.815217 | 0.802371 | 0.166008 | 0.514548 | 0.009547 | 0.012274 | 0.018467 | 0.004824 | 0.597826 | 0.826087 | 0.043932 |
| J_ADJUSTED | 92 | 19 | 0.782609 | 0.753749 | 0.173213 | 0.530488 | 0.009845 | 0.012419 | 0.018860 | 0.004979 | 0.565217 | 0.815217 | 0.044196 |
| A_STRUCTURE_LEVEL | 92 | 19 | 0.760870 | 0.765360 | 0.161756 | 0.502146 | 0.009587 | 0.012564 | 0.018940 | 0.004827 | 0.543478 | 0.804348 | 0.037959 |
| A_STRUCTURE_CHANGE | 92 | 19 | 0.782609 | 0.787615 | 0.162875 | 0.504776 | 0.009472 | 0.012361 | 0.018824 | 0.004784 | 0.576087 | 0.804348 | 0.038362 |
| W_STRUCT_EMBARGO | 92 | 19 | 0.782609 | 0.794388 | 0.163355 | 0.504982 | 0.009453 | 0.012395 | 0.018644 | 0.004783 | 0.543478 | 0.826087 | 0.039774 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J_GRID0 | 92 | 19 | 0.771739 | 0.757862 | 0.184455 | 0.553935 | 0.009694 | 0.012635 | 0.018338 | 0.004886 | 0.532609 | 0.804348 | 0.042900 |
| J_GRID1 | 92 | 19 | 0.782609 | 0.774069 | 0.175181 | 0.533476 | 0.009545 | 0.012499 | 0.018371 | 0.004802 | 0.576087 | 0.804348 | 0.043084 |
| J_GRID2 | 92 | 19 | 0.804348 | 0.806483 | 0.168397 | 0.519272 | 0.009530 | 0.012442 | 0.018550 | 0.004799 | 0.586957 | 0.826087 | 0.042975 |
| J_GRID3 | 92 | 19 | 0.793478 | 0.800435 | 0.164101 | 0.510084 | 0.009647 | 0.012578 | 0.018870 | 0.004832 | 0.586957 | 0.815217 | 0.041418 |
| J_GRID4 | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038771 |


The grid shows the full predeclared five-point tradeoff between a cluster-balanced Elastic parent and a domestic rotation Ridge parent. A weight of zero means all Elastic. The learned mixture uses up to 84 resolved past forecast origins. A purged earlier partition fits regularized weights and score preferences, then uses an 18-origin trailing calibration gate. A sign tilt and return spread adjustment are disabled in folds where the gate fails to improve the combined losses or worsens nominal-80 coverage calibration. The first integration pass preserved all outer cutoffs but omitted purging inside this calibration gate. It is archived, then replaced in the comparative analyses by the stricter refit. The corrected adjustment still scores worse on the pooled weekly cohort than the raw learned mixture. Consequently calibration is retained as a failed improvement here. The earlier-cutoff structure model and the direct structure levels model show the most interesting proper-score tradeoff without forced calibration.

| horizon | fold | weight | tilt | spread | enabled | n_early | n_gate | gate_first_origin | calibration_fit_last_endpoint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 2026-07 | 0.200000 | -0.250000 | 1.100000 | True | 61 | 18 | 2026-05-26 | 2026-05-25 |
| 5 | 2026-08 | 0.500000 | 0.000000 | 1.000000 | False | 61 | 18 | 2026-06-30 | 2026-06-29 |
| 5 | 2026-09 | 0.500000 | 0.000000 | 1.000000 | False | 61 | 18 | 2026-07-29 | 2026-07-28 |
| 5 | 2026-10 | 0.500000 | -0.250000 | 0.900000 | True | 61 | 18 | 2026-08-27 | 2026-08-26 |
| 5 | 2026-11 | 0.500000 | -0.250000 | 0.900000 | True | 61 | 18 | 2026-09-25 | 2026-09-24 |
| 21 | 2026-07 | 0.500000 | 0.000000 | 1.000000 | False | 45 | 18 | 2026-05-04 | 2026-04-30 |
| 21 | 2026-08 | 0.900000 | 0.000000 | 1.100000 | True | 45 | 18 | 2026-06-05 | 2026-06-04 |
| 21 | 2026-09 | 0.900000 | 0.000000 | 1.000000 | False | 45 | 18 | 2026-07-07 | 2026-07-06 |
| 21 | 2026-10 | 0.500000 | 0.000000 | 1.000000 | False | 45 | 18 | 2026-08-05 | 2026-08-04 |


| model | condition | value | n | disjoint | brier_gain | CRPS_gain | leave_month_gain_min | leave_month_gain_max | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_STRUCTURE_CHANGE | historical_volatility_regime | high_vol | 52 | 11 | 0.001954 | 0.000192 | -0.000455 | 0.003513 | 0.769231 |
| A_STRUCTURE_CHANGE | historical_volatility_regime | low_vol | 40 | 8 | -0.005113 | 0.000016 | -0.011702 | 0.001444 | 0.850000 |
| R_RESIDUAL | historical_volatility_regime | high_vol | 52 | 11 | 0.002980 | 0.000027 | -0.000536 | 0.007158 | 0.769231 |
| R_RESIDUAL | historical_volatility_regime | low_vol | 40 | 8 | 0.002543 | 0.000067 | 0.002169 | 0.003004 | 0.875000 |


`metrics.json` records probability-bin calibration, central coverage, sharpness, quantile loss and bucket scores. `all-predictions.csv` carries both endpoint tails, absolute return and the per-origin 5/10/25/50/75/90/95 quantiles. The primary weekly cohort has 92 overlapping origins, 19 disjoint windows and a return-ACF ESS of about 12.36. Monthly evaluation has 76 overlapping origins and approximately four disjoint windows. Dependence diagnostics are not independent trials.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
