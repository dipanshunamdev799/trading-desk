# NIFTY V8 · Final Research Conclusions

Run `2026-11-24/run-001`. Retrospective research.

V8 establishes exact duplicate invariance in the tested fitted laws. It improves selected historical weekly point scores. It does not establish independent forecasting superiority. Residualized domestic rotation gives an unperturbed **.159504 Brier** versus V7 **.162145**. The stronger early-cutoff structure-change law gives **.009453 CRPS** versus **.009665** in V7, with **.009472** as the first-stage structure-change result. The level-only state law gives **.161756 Brier and .009587 CRPS**, point improvements against both distinct prior leader scores, but small enough that neither provides confirmatory evidence. The synthetic perturbation rows are deliberately separate from practical candidate selection.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T_ROT_DOMESTIC | 92 | 19 | 0.804348 | 0.809869 | 0.162145 | 0.505266 | 0.009927 | 0.012893 | 0.019361 | 0.004989 | 0.543478 | 0.815217 | 0.038873 |
| T_ELASTIC_EMBARGO | 92 | 19 | 0.728261 | 0.699806 | 0.184134 | 0.552228 | 0.009665 | 0.012308 | 0.017693 | 0.004888 | 0.576087 | 0.815217 | 0.047453 |
| R_RESIDUAL | 92 | 19 | 0.804348 | 0.809869 | 0.159504 | 0.499670 | 0.009852 | 0.012801 | 0.019329 | 0.004980 | 0.521739 | 0.815217 | 0.038406 |
| A_STRUCTURE_LEVEL | 92 | 19 | 0.760870 | 0.765360 | 0.161756 | 0.502146 | 0.009587 | 0.012564 | 0.018940 | 0.004827 | 0.543478 | 0.804348 | 0.037959 |
| A_STRUCTURE_CHANGE | 92 | 19 | 0.782609 | 0.787615 | 0.162875 | 0.504776 | 0.009472 | 0.012361 | 0.018824 | 0.004784 | 0.576087 | 0.804348 | 0.038362 |
| W_STRUCT_EMBARGO | 92 | 19 | 0.782609 | 0.794388 | 0.163355 | 0.504982 | 0.009453 | 0.012395 | 0.018644 | 0.004783 | 0.543478 | 0.826087 | 0.039774 |
| G_ROT_ELASTIC | 92 | 19 | 0.739130 | 0.716014 | 0.164496 | 0.507809 | 0.009499 | 0.012158 | 0.018420 | 0.004758 | 0.608696 | 0.793478 | 0.039427 |


| model | baseline | metric | n | gain | simultaneous95_block10 |
| --- | --- | --- | --- | --- | --- |
| A_STRUCTURE_CHANGE | T_ROT_DOMESTIC | brier | 92 | -0.000730 | [-0.017337, 0.015877] |
| A_STRUCTURE_CHANGE | T_ROT_DOMESTIC | crps | 92 | 0.000455 | [-0.000125, 0.001034] |
| A_STRUCTURE_CHANGE | T_ELASTIC_EMBARGO | brier | 92 | 0.021259 | [-0.043935, 0.086453] |
| A_STRUCTURE_CHANGE | T_ELASTIC_EMBARGO | crps | 92 | 0.000193 | [-0.002361, 0.002748] |
| A_STRUCTURE_LEVEL | T_ROT_DOMESTIC | brier | 92 | 0.000389 | [-0.012729, 0.013507] |
| A_STRUCTURE_LEVEL | T_ROT_DOMESTIC | crps | 92 | 0.000339 | [-0.000035, 0.000714] |
| A_STRUCTURE_LEVEL | T_ELASTIC_EMBARGO | brier | 92 | 0.022377 | [-0.036755, 0.081510] |
| A_STRUCTURE_LEVEL | T_ELASTIC_EMBARGO | crps | 92 | 0.000078 | [-0.002446, 0.002602] |
| G_ROT_ELASTIC | T_ROT_DOMESTIC | brier | 92 | -0.002351 | [-0.040499, 0.035798] |
| G_ROT_ELASTIC | T_ROT_DOMESTIC | crps | 92 | 0.000428 | [-0.000517, 0.001373] |
| G_ROT_ELASTIC | T_ELASTIC_EMBARGO | brier | 92 | 0.019638 | [-0.036638, 0.075913] |
| G_ROT_ELASTIC | T_ELASTIC_EMBARGO | crps | 92 | 0.000167 | [-0.002145, 0.002479] |
| R_RESIDUAL | T_ROT_DOMESTIC | brier | 92 | 0.002641 | [-0.006632, 0.011914] |
| R_RESIDUAL | T_ROT_DOMESTIC | crps | 92 | 0.000075 | [-0.000223, 0.000372] |
| R_RESIDUAL | T_ELASTIC_EMBARGO | brier | 92 | 0.024630 | [-0.031447, 0.080707] |
| R_RESIDUAL | T_ELASTIC_EMBARGO | crps | 92 | -0.000187 | [-0.002952, 0.002579] |
| W_STRUCT_EMBARGO | T_ROT_DOMESTIC | brier | 92 | -0.001210 | [-0.018498, 0.016077] |
| W_STRUCT_EMBARGO | T_ROT_DOMESTIC | crps | 92 | 0.000474 | [-0.000319, 0.001266] |
| W_STRUCT_EMBARGO | T_ELASTIC_EMBARGO | brier | 92 | 0.020778 | [-0.045486, 0.087043] |
| W_STRUCT_EMBARGO | T_ELASTIC_EMBARGO | crps | 92 | 0.000212 | [-0.002108, 0.002533] |


Two constraints determine the research decision. Earlier-weekly rotation scores lose to a simple historical law, so the later lead has not shown chronological transfer. And monthly smoothed-state controls score comparably or better after deliberate misalignment, so the timing story lacks falsification support. Even the best monthly CRPS .020474 and nominal calibration at 85.53% are historical point estimates based on four disjoint outcomes. Keep the unperturbed weekly residual rotation, structural levels/change, and cluster-balanced rotation laws as distinct hypotheses. Keep the month model in falsification research. The primary weekly cohort has 92 overlapping origins, 19 disjoint windows and a return-ACF ESS of about 12.36. Monthly evaluation has 76 overlapping origins and approximately four disjoint windows. Dependence diagnostics are not independent trials.

[Weekly proper-score tradeoff figure](weekly-proper-score-tradeoff.png)

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
