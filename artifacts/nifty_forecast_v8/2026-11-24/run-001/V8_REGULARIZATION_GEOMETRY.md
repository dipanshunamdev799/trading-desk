# NIFTY V8 · Regularization Geometry

Run `2026-11-24/run-001`. Retrospective research.

Exact copies identify a prediction effect without introducing a single market observation. In linear Ridge, if two standardized columns are copies, their two coefficients can sum to the original coefficient and each take half the original value. The sum of their squared penalties is then half the original. Four copies including the original reduce the effective penalty to one quarter. Dividing each standardized copy by √k restores the original direction's cost for k identical columns. This is why interacting sector representations can influence Ridge even when the signal set itself has not grown. Scaling duplicate features similarly is generally insufficient to preserve Elastic Net's mixed L1/L2 geometry.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I_ridge_as_is | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| I_ridge_one_copy | 92 | 19 | 0.750000 | 0.752540 | 0.188090 | 0.562591 | 0.010317 | 0.013717 | 0.019858 | 0.005209 | 0.554348 | 0.771739 | 0.038691 |
| I_ridge_three_copies | 92 | 19 | 0.739130 | 0.743106 | 0.195062 | 0.577838 | 0.010470 | 0.013909 | 0.019934 | 0.005260 | 0.521739 | 0.782609 | 0.039265 |
| I_ridge_balanced_three | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| I_canonical_ridge_three_copies | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| I_elastic_as_is | 92 | 19 | 0.554348 | 0.552250 | 0.245135 | 0.685822 | 0.011334 | 0.014563 | 0.020383 | 0.005648 | 0.510870 | 0.771739 | 0.044411 |
| I_elastic_three_copies | 92 | 19 | 0.554348 | 0.552250 | 0.245104 | 0.685767 | 0.011338 | 0.014569 | 0.020385 | 0.005650 | 0.510870 | 0.771739 | 0.044479 |
| I_canonical_elastic_three_copies | 92 | 19 | 0.771739 | 0.757862 | 0.184455 | 0.553935 | 0.009694 | 0.012635 | 0.018338 | 0.004887 | 0.532609 | 0.804348 | 0.042882 |


V8 eliminates exact standardized-copy families before constructing transformations, and proves numerical invariance by testing atoms and weights. It also compares covariance-aware coefficient scaling through `(I + 0.65 Σ_shrunk)^(-1/2)` and compounded cluster and sector-group penalties. Those choices change the cost of a fitted direction even with no actual copies. Covariance Ridge and the hierarchical penalty worsen the primary weekly Brier versus raw native Ridge in this study. The positive conclusion is representation invariance under known transformations. It does not require a selected post-hoc shrinkage geometry to also improve a proper score.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_FULL | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| G_CANON | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| G_CLUSTER | 92 | 19 | 0.750000 | 0.759313 | 0.177513 | 0.540382 | 0.010195 | 0.013487 | 0.019879 | 0.005155 | 0.532609 | 0.782609 | 0.037611 |
| G_COV | 92 | 19 | 0.760870 | 0.768747 | 0.192544 | 0.572218 | 0.010581 | 0.014204 | 0.020476 | 0.005338 | 0.521739 | 0.750000 | 0.035534 |
| G_HIERARCHICAL | 92 | 19 | 0.760870 | 0.741655 | 0.191148 | 0.569839 | 0.010579 | 0.014045 | 0.020494 | 0.005352 | 0.532609 | 0.728261 | 0.035464 |
| G_RESID | 92 | 19 | 0.760870 | 0.772134 | 0.177935 | 0.541216 | 0.010169 | 0.013478 | 0.019852 | 0.005148 | 0.543478 | 0.771739 | 0.037847 |
| G_ROT_CLUSTER | 92 | 19 | 0.782609 | 0.791001 | 0.167469 | 0.516703 | 0.009914 | 0.012877 | 0.019387 | 0.004981 | 0.532609 | 0.804348 | 0.037714 |
| G_ROT_COV | 92 | 19 | 0.826087 | 0.828737 | 0.176844 | 0.538486 | 0.010228 | 0.013373 | 0.019956 | 0.005174 | 0.510870 | 0.771739 | 0.036441 |
| G_ROT_ELASTIC | 92 | 19 | 0.739130 | 0.716014 | 0.164496 | 0.507809 | 0.009499 | 0.012158 | 0.018420 | 0.004758 | 0.608696 | 0.793478 | 0.039427 |

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
