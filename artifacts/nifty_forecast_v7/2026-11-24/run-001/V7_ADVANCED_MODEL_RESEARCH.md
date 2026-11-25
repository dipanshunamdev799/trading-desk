# NIFTY V7 · Advanced Model Research

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

Configuration-level tests compare structured Ridge, Elastic Net, economic group lasso, Bayesian Ridge, Huber, quadratic splines, shallow forest, shallow histogram gradient boosting, a residual boosting correction, two fixed interactions and volatility-gated Ridge experts. All fitted transforms use only allowed historical rows. The residual model fits on training residuals then adds half its predicted correction. Experts retain 60% of the pooled Ridge location with 40% from the historical high/low-risk expert. Fixed-knot GAM-style splines and the shallow-tree and forest parameters are in `models.py`. Forecast error comparisons keep the common empirical law across location architectures.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_RAW | 92 | 0.760870 | 0.768747 | 0.182047 | 0.549215 | 0.010199 | 0.013506 | 0.012959 | 0.019807 | 0.521739 | 0.760870 | 0.037711 |
| C_NO_DEF | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| C_PCA_WHITE | 92 | 0.717391 | 0.714078 | 0.199695 | 0.588701 | 0.011275 | 0.014593 | 0.014104 | 0.021574 | 0.510870 | 0.739130 | 0.038624 |
| C_ELASTIC | 92 | 0.771739 | 0.757862 | 0.184607 | 0.554242 | 0.009695 | 0.012635 | 0.011999 | 0.018339 | 0.532609 | 0.804348 | 0.042881 |
| C_GROUP_LASSO | 92 | 0.760870 | 0.745041 | 0.201743 | 0.593338 | 0.010910 | 0.014553 | 0.014253 | 0.021072 | 0.543478 | 0.750000 | 0.036402 |
| A_BAL_RIDGE | 92 | 0.760870 | 0.751814 | 0.196238 | 0.581115 | 0.010866 | 0.014344 | 0.013809 | 0.021071 | 0.543478 | 0.739130 | 0.036101 |
| A_PCA_BAYES | 92 | 0.728261 | 0.730285 | 0.188403 | 0.563062 | 0.011110 | 0.014148 | 0.014209 | 0.020938 | 0.543478 | 0.771739 | 0.044000 |
| A_PCA_HUBER | 92 | 0.695652 | 0.688437 | 0.186634 | 0.555972 | 0.011378 | 0.014822 | 0.014676 | 0.021158 | 0.532609 | 0.826087 | 0.047294 |
| A_PCA_GAM | 92 | 0.695652 | 0.688437 | 0.202737 | 0.594946 | 0.011385 | 0.014657 | 0.014269 | 0.021735 | 0.510870 | 0.750000 | 0.038680 |
| A_PCA_FOREST | 92 | 0.619565 | 0.612240 | 0.238799 | 0.671124 | 0.011963 | 0.015909 | 0.015483 | 0.022901 | 0.423913 | 0.717391 | 0.037969 |
| A_PCA_BOOST | 92 | 0.619565 | 0.588534 | 0.244721 | 0.684384 | 0.011973 | 0.015899 | 0.015599 | 0.023033 | 0.445652 | 0.750000 | 0.038836 |
| A_PCA_RESID | 92 | 0.663043 | 0.663522 | 0.201465 | 0.591650 | 0.011284 | 0.014489 | 0.014234 | 0.021583 | 0.500000 | 0.750000 | 0.039143 |
| A_PCA_EXPERTS | 92 | 0.641304 | 0.631108 | 0.218413 | 0.628351 | 0.011774 | 0.015346 | 0.014920 | 0.022511 | 0.489130 | 0.739130 | 0.038072 |
| A_PCA_INTERACT | 92 | 0.717391 | 0.714078 | 0.200392 | 0.590006 | 0.011283 | 0.014623 | 0.014172 | 0.021618 | 0.510870 | 0.739130 | 0.038509 |
| T_RAW_ELASTIC | 92 | 0.554348 | 0.552250 | 0.245135 | 0.685822 | 0.011334 | 0.014563 | 0.014911 | 0.020383 | 0.510870 | 0.771739 | 0.044411 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_RAW | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.037168 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| C_NO_DEF | 76 | 0.539474 | 0.575986 | 0.264309 | 0.726979 | 0.030275 | 0.038624 | 0.037553 | 0.049682 | 0.315789 | 0.500000 | 0.071598 |
| C_PCA_WHITE | 76 | 0.381579 | 0.387455 | 0.340176 | 0.896002 | 0.030872 | 0.041181 | 0.041514 | 0.049154 | 0.131579 | 0.500000 | 0.067004 |
| C_ELASTIC | 76 | 0.657895 | 0.670968 | 0.201414 | 0.591339 | 0.029193 | 0.040274 | 0.041771 | 0.049925 | 0.447368 | 0.750000 | 0.099270 |
| C_GROUP_LASSO | 76 | 0.565789 | 0.603226 | 0.245426 | 0.686586 | 0.029693 | 0.039128 | 0.036803 | 0.048524 | 0.289474 | 0.513158 | 0.073188 |
| A_BAL_RIDGE | 76 | 0.460526 | 0.529391 | 0.293892 | 0.793711 | 0.030153 | 0.037229 | 0.037772 | 0.047830 | 0.276316 | 0.434211 | 0.064671 |
| A_PCA_BAYES | 76 | 0.578947 | 0.554122 | 0.278937 | 0.762510 | 0.028294 | 0.038622 | 0.038934 | 0.047687 | 0.289474 | 0.618421 | 0.078537 |
| A_PCA_HUBER | 76 | 0.526316 | 0.509677 | 0.292743 | 0.795432 | 0.030709 | 0.041765 | 0.042116 | 0.051058 | 0.328947 | 0.565789 | 0.089302 |
| A_PCA_GAM | 76 | 0.394737 | 0.398566 | 0.344587 | 0.906257 | 0.031205 | 0.041661 | 0.042002 | 0.049535 | 0.118421 | 0.486842 | 0.067162 |
| A_PCA_FOREST | 76 | 0.250000 | 0.276344 | 0.393246 | 1.025510 | 0.033504 | 0.042914 | 0.043501 | 0.051206 | 0.197368 | 0.552632 | 0.072206 |
| A_PCA_BOOST | 76 | 0.131579 | 0.136201 | 0.475637 | 1.235660 | 0.041077 | 0.052986 | 0.056237 | 0.062378 | 0.184211 | 0.500000 | 0.078687 |
| A_PCA_RESID | 76 | 0.263158 | 0.267384 | 0.374161 | 0.971402 | 0.033120 | 0.043823 | 0.044350 | 0.051858 | 0.118421 | 0.500000 | 0.069060 |
| A_PCA_EXPERTS | 76 | 0.289474 | 0.309677 | 0.374757 | 0.976047 | 0.032612 | 0.043225 | 0.044106 | 0.050843 | 0.092105 | 0.460526 | 0.066948 |
| A_PCA_INTERACT | 76 | 0.328947 | 0.332975 | 0.339341 | 0.891611 | 0.031208 | 0.041681 | 0.042135 | 0.049600 | 0.105263 | 0.513158 | 0.067279 |


The learned representation mattered more than searching for additional tree or sequence estimators. Sparse compressed regression did better at some scores, while broad factor compression and flexible residual models struggled. Since clustered Elastic Net outperformed raw Elastic Net here, a separate regularization change can improve prediction with the same underlying market inputs. Parameters were held fixed per family. V7 keeps the existing V4 LightGBM vector as a strong frozen benchmark. XGBoost, CatBoost, neural temporal models and an extra hyperparameter grid were not run. The sample contains 19 weekly and four monthly disjoint windows. Training and numerical warnings appear in `fit-ledger.csv`.

Brier and log loss score sign probabilities. CRPS scores the entire endpoint return distribution. Lower scores are better. CRPS, MAE and interval widths are in fractional return units. A width of .04 spans four percentage points. Gain means matched control loss minus candidate loss.
