# NIFTY V8 · Market Structure Discovery

Run `2026-11-24/run-001`. Retrospective research.

The level block contains seven economically interpretable summaries: financial momentum relative to NIFTY, dispersion across cyclical and defensive sectors, NIFTY 500 leadership, relative sector volatility dispersion, sector correlation, concentration and rank-rotation speed. The changes treatment adds their five-session differences alongside the same levels. The breadth treatment uses participation trend, broad-index momentum and rank persistence. The risk structure treatment uses cross-sector downside variance, persistence/transition in correlation and change in implied risk relative to realized volatility. All are trailing transforms on authentic native index histories. Index participation remains a sector-index proxy for dispersion across traded names.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038767 |
| A_STRUCTURE_LEVEL | 92 | 19 | 0.760870 | 0.765360 | 0.161756 | 0.502146 | 0.009587 | 0.012564 | 0.018940 | 0.004827 | 0.543478 | 0.804348 | 0.037959 |
| A_STRUCTURE_CHANGE | 92 | 19 | 0.782609 | 0.787615 | 0.162875 | 0.504776 | 0.009472 | 0.012361 | 0.018824 | 0.004784 | 0.576087 | 0.804348 | 0.038362 |
| A_PARTICIPATION | 92 | 19 | 0.793478 | 0.797049 | 0.162243 | 0.505575 | 0.009882 | 0.012847 | 0.019348 | 0.004964 | 0.543478 | 0.815217 | 0.038442 |
| A_RISK_STRUCTURE | 92 | 19 | 0.760870 | 0.772134 | 0.180343 | 0.544895 | 0.010295 | 0.013255 | 0.020069 | 0.005221 | 0.521739 | 0.793478 | 0.038175 |
| A_NATIVE_PANEL | 92 | 19 | 0.804348 | 0.809869 | 0.160086 | 0.501285 | 0.009892 | 0.012916 | 0.019379 | 0.004981 | 0.543478 | 0.804348 | 0.038499 |
| W_STRUCT_EMBARGO | 92 | 19 | 0.782609 | 0.794388 | 0.163355 | 0.504982 | 0.009453 | 0.012395 | 0.018644 | 0.004783 | 0.543478 | 0.826087 | 0.039774 |
| W_STRUCT_WINDOW | 92 | 19 | 0.652174 | 0.684567 | 0.204556 | 0.596243 | 0.010671 | 0.013874 | 0.020462 | 0.005397 | 0.532609 | 0.793478 | 0.042310 |
| W_STRUCT_LAG | 92 | 19 | 0.771739 | 0.771408 | 0.176574 | 0.535724 | 0.009833 | 0.013018 | 0.019230 | 0.004935 | 0.554348 | 0.826087 | 0.040840 |
| W_STRUCT_PERTURB | 92 | 19 | 0.782609 | 0.791001 | 0.164449 | 0.507886 | 0.009421 | 0.012329 | 0.018684 | 0.004754 | 0.565217 | 0.804348 | 0.038585 |
| W_STRUCT_TARGET_NULL | 92 | 19 | 0.413043 | 0.372037 | 0.319960 | 0.848498 | 0.014678 | 0.019293 | 0.026916 | 0.007338 | 0.391304 | 0.706522 | 0.045435 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| A_NATIVE_PANEL | B_ROT | brier | 92 | 0.002208 |
| A_NATIVE_PANEL | B_ROT | crps | 92 | 0.000005 |
| A_PARTICIPATION | B_ROT | brier | 92 | 0.000051 |
| A_PARTICIPATION | B_ROT | crps | 92 | 0.000015 |
| A_RISK_STRUCTURE | B_ROT | brier | 92 | -0.018049 |
| A_RISK_STRUCTURE | B_ROT | crps | 92 | -0.000398 |
| A_STRUCTURE_CHANGE | A_STRUCTURE_LEVEL | brier | 92 | -0.001119 |
| A_STRUCTURE_CHANGE | A_STRUCTURE_LEVEL | crps | 92 | 0.000115 |
| A_STRUCTURE_LEVEL | B_ROT | brier | 92 | 0.000538 |
| A_STRUCTURE_LEVEL | B_ROT | crps | 92 | 0.000309 |
| B_ROT | B_NATIVE | brier | 92 | 0.007509 |
| B_ROT | B_NATIVE | crps | 92 | 0.000171 |
| W_STRUCT_EMBARGO | A_STRUCTURE_CHANGE | brier | 92 | -0.000480 |
| W_STRUCT_EMBARGO | A_STRUCTURE_CHANGE | crps | 92 | 0.000019 |
| W_STRUCT_LAG | A_STRUCTURE_CHANGE | brier | 92 | -0.013699 |
| W_STRUCT_LAG | A_STRUCTURE_CHANGE | crps | 92 | -0.000360 |
| W_STRUCT_PERTURB | A_STRUCTURE_CHANGE | brier | 92 | -0.001574 |
| W_STRUCT_PERTURB | A_STRUCTURE_CHANGE | crps | 92 | 0.000051 |
| W_STRUCT_TARGET_NULL | A_STRUCTURE_CHANGE | brier | 92 | -0.157085 |
| W_STRUCT_TARGET_NULL | A_STRUCTURE_CHANGE | crps | 92 | -0.005206 |
| W_STRUCT_WINDOW | A_STRUCTURE_CHANGE | brier | 92 | -0.041681 |
| W_STRUCT_WINDOW | A_STRUCTURE_CHANGE | crps | 92 | -0.001199 |


Levels reach **.161756 Brier and .009587 CRPS**, both improving V7's best point benchmarks across their different scores. Adding the corresponding differences lowers **CRPS to .009472** and raises Brier slightly to **.162875**. An adaptive earlier-cutoff stress fit reaches **.009453 CRPS**. Scaling deviations in the grouped inputs gives .009421 in a synthetic query perturbation. That is a sensitivity experiment, excluded from candidate selection. A 189-observation window yields .010671, a five-session lag .009833, and block-permuted targets .014678. The paired effects support investigating the few interpretable inputs further, with time and cohort dependence preserved.

| model | metric | kind | min_gain | max_gain | positive |
| --- | --- | --- | --- | --- | --- |
| A_STRUCTURE_CHANGE | brier | disjoint_phase | -0.011400 | 0.006125 | 3/5 |
| A_STRUCTURE_CHANGE | brier | leave_month | -0.004233 | 0.003272 | 2/5 |
| A_STRUCTURE_CHANGE | brier | remove_top_gain | -0.011758 | -0.002715 | 0/4 |
| A_STRUCTURE_CHANGE | crps | disjoint_phase | 0.000181 | 0.000738 | 5/5 |
| A_STRUCTURE_CHANGE | crps | leave_month | 0.000234 | 0.000540 | 5/5 |
| A_STRUCTURE_CHANGE | crps | remove_top_gain | 0.000054 | 0.000400 | 4/4 |
| A_STRUCTURE_LEVEL | brier | disjoint_phase | -0.005462 | 0.009180 | 2/5 |
| A_STRUCTURE_LEVEL | brier | leave_month | -0.002074 | 0.001671 | 4/5 |
| A_STRUCTURE_LEVEL | brier | remove_top_gain | -0.009005 | -0.001477 | 0/4 |
| A_STRUCTURE_LEVEL | crps | disjoint_phase | 0.000162 | 0.000597 | 5/5 |
| A_STRUCTURE_LEVEL | crps | leave_month | 0.000217 | 0.000400 | 5/5 |
| A_STRUCTURE_LEVEL | crps | remove_top_gain | 0.000035 | 0.000300 | 4/4 |
| W_STRUCT_EMBARGO | brier | disjoint_phase | -0.012559 | 0.013628 | 3/5 |
| W_STRUCT_EMBARGO | brier | leave_month | -0.004552 | 0.002562 | 1/5 |
| W_STRUCT_EMBARGO | brier | remove_top_gain | -0.011861 | -0.003425 | 0/4 |
| W_STRUCT_EMBARGO | crps | disjoint_phase | 0.000223 | 0.000697 | 5/5 |
| W_STRUCT_EMBARGO | crps | leave_month | 0.000237 | 0.000564 | 5/5 |
| W_STRUCT_EMBARGO | crps | remove_top_gain | -0.000010 | 0.000405 | 3/4 |


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
| W_STRUCT_EMBARGO | T_ROT_DOMESTIC | brier | 92 | -0.001210 | [-0.018498, 0.016077] |
| W_STRUCT_EMBARGO | T_ROT_DOMESTIC | crps | 92 | 0.000474 | [-0.000319, 0.001266] |
| W_STRUCT_EMBARGO | T_ELASTIC_EMBARGO | brier | 92 | 0.020778 | [-0.045486, 0.087043] |
| W_STRUCT_EMBARGO | T_ELASTIC_EMBARGO | crps | 92 | 0.000212 | [-0.002108, 0.002533] |

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
