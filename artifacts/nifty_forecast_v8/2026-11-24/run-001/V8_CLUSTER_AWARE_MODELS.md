# NIFTY V8 · Cluster Aware Models

Run `2026-11-24/run-001`. Retrospective research.

The sector relative-return block uses training-only absolute correlations, average linkage at distance .25, and fixed representation alternatives. Inverse square-root cluster-size scaling keeps all distinct features. The Bayesian variant uses a global precision on cluster-scaled coordinates, which induces different original-coordinate priors by cluster size. The hierarchical variant compounds economic group size and data-driven cluster weights. Factor-plus-residual projection uses signed cluster means and Ridge10 to estimate factor exposures, then adds residuals with half their original scale. Representative selection makes a 75/25 blend of within-cluster centrality and past target correlation. Assignments for every fitted cutoff are saved in the fit ledgers and models.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_NATIVE | 92 | 19 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.019635 | 0.005068 | 0.510870 | 0.793478 | 0.039009 |
| B_FULL | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| B_ROT | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038767 |
| G_CANON | 92 | 19 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.019807 | 0.005158 | 0.521739 | 0.760870 | 0.037711 |
| G_CLUSTER | 92 | 19 | 0.750000 | 0.759313 | 0.177513 | 0.540382 | 0.010195 | 0.013487 | 0.019879 | 0.005155 | 0.532609 | 0.782609 | 0.037611 |
| G_ELASTIC | 92 | 19 | 0.771739 | 0.757862 | 0.184455 | 0.553935 | 0.009694 | 0.012635 | 0.018338 | 0.004887 | 0.532609 | 0.804348 | 0.042882 |
| G_BAYES | 92 | 19 | 0.543478 | 0.529269 | 0.257741 | 0.710598 | 0.012760 | 0.016830 | 0.021673 | 0.006253 | 0.478261 | 0.771739 | 0.048903 |
| G_HIERARCHICAL | 92 | 19 | 0.760870 | 0.741655 | 0.191148 | 0.569839 | 0.010579 | 0.014045 | 0.020494 | 0.005352 | 0.532609 | 0.728261 | 0.035464 |
| G_COV | 92 | 19 | 0.760870 | 0.768747 | 0.192544 | 0.572218 | 0.010581 | 0.014204 | 0.020476 | 0.005338 | 0.521739 | 0.750000 | 0.035534 |
| G_RESID | 92 | 19 | 0.760870 | 0.772134 | 0.177935 | 0.541216 | 0.010169 | 0.013478 | 0.019852 | 0.005148 | 0.543478 | 0.771739 | 0.037847 |
| G_REPRESENT | 92 | 19 | 0.750000 | 0.762700 | 0.177860 | 0.540779 | 0.010263 | 0.013556 | 0.020038 | 0.005186 | 0.554348 | 0.782609 | 0.038377 |
| G_ROT_CLUSTER | 92 | 19 | 0.782609 | 0.791001 | 0.167469 | 0.516703 | 0.009914 | 0.012877 | 0.019387 | 0.004981 | 0.532609 | 0.804348 | 0.037714 |
| G_ROT_COV | 92 | 19 | 0.826087 | 0.828737 | 0.176844 | 0.538486 | 0.010228 | 0.013373 | 0.019956 | 0.005174 | 0.510870 | 0.771739 | 0.036441 |
| G_ROT_ELASTIC | 92 | 19 | 0.739130 | 0.716014 | 0.164496 | 0.507809 | 0.009499 | 0.012158 | 0.018420 | 0.004758 | 0.608696 | 0.793478 | 0.039427 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_NATIVE | 76 | 4 | 0.539474 | 0.575986 | 0.264309 | 0.726979 | 0.030275 | 0.038624 | 0.049682 | 0.015252 | 0.315789 | 0.500000 | 0.071598 |
| B_FULL | 76 | 4 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.014902 | 0.302632 | 0.500000 | 0.076238 |
| B_ROT | 76 | 4 | 0.552632 | 0.587097 | 0.257372 | 0.712354 | 0.030072 | 0.038406 | 0.049434 | 0.015152 | 0.315789 | 0.500000 | 0.072037 |
| G_CANON | 76 | 4 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.048112 | 0.014902 | 0.302632 | 0.500000 | 0.076238 |
| G_CLUSTER | 76 | 4 | 0.592105 | 0.640502 | 0.253136 | 0.705354 | 0.029434 | 0.038061 | 0.047703 | 0.014818 | 0.302632 | 0.513158 | 0.071572 |
| G_ELASTIC | 76 | 4 | 0.657895 | 0.670968 | 0.201414 | 0.591339 | 0.029193 | 0.040272 | 0.049924 | 0.014707 | 0.447368 | 0.750000 | 0.099279 |
| G_BAYES | 76 | 4 | 0.789474 | 0.782079 | 0.195233 | 0.575645 | 0.029361 | 0.039798 | 0.050488 | 0.014509 | 0.460526 | 0.763158 | 0.096503 |
| G_HIERARCHICAL | 76 | 4 | 0.460526 | 0.514337 | 0.304494 | 0.814302 | 0.029754 | 0.037945 | 0.047877 | 0.014641 | 0.302632 | 0.486842 | 0.066439 |
| G_COV | 76 | 4 | 0.526316 | 0.584946 | 0.284903 | 0.772787 | 0.029786 | 0.037400 | 0.047934 | 0.014877 | 0.302632 | 0.447368 | 0.070779 |
| G_RESID | 76 | 4 | 0.592105 | 0.640502 | 0.248188 | 0.693892 | 0.029234 | 0.037858 | 0.047494 | 0.014718 | 0.302632 | 0.500000 | 0.071446 |
| G_REPRESENT | 76 | 4 | 0.605263 | 0.656631 | 0.248603 | 0.694922 | 0.028844 | 0.037050 | 0.047071 | 0.014502 | 0.302632 | 0.500000 | 0.069945 |
| G_ROT_CLUSTER | 76 | 4 | 0.552632 | 0.587097 | 0.255676 | 0.709836 | 0.030098 | 0.038329 | 0.049149 | 0.015140 | 0.315789 | 0.500000 | 0.069297 |
| G_ROT_COV | 76 | 4 | 0.500000 | 0.542652 | 0.276038 | 0.751438 | 0.030093 | 0.037383 | 0.049129 | 0.015050 | 0.250000 | 0.473684 | 0.067956 |
| G_ROT_ELASTIC | 76 | 4 | 0.697368 | 0.694265 | 0.198707 | 0.587015 | 0.026928 | 0.035067 | 0.048410 | 0.013364 | 0.460526 | 0.789474 | 0.090068 |


Raw and canonical native Ridge are numerically equivalent on this matrix. Generic cluster balancing gives .177513 weekly Brier against .182047 raw, but targeted defensive deletion remains stronger at .169803. Cluster-balanced Elastic Net with rotation has .164496 Brier and .009499 CRPS, a joint point improvement over V6's CRPS system with tradeoffs against V7's Brier leader. Covariance penalties and generic hierarchical scaling are worse. Within-fold clustering cannot isolate which historical constituents created overlapping exposures. The observed designs also share NIFTY benchmark subtraction. Distinct sector residuals can carry information, as tested directly in the rotation wave, but generic unsupervised factor separation alone was weaker. The primary weekly cohort has 92 overlapping origins, 19 disjoint windows and a return-ACF ESS of about 12.36. Monthly evaluation has 76 overlapping origins and approximately four disjoint windows. Dependence diagnostics are not independent trials.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
