# NIFTY V7 · Monthly Falsification

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The earlier 81.58% figure came from 62 of 76 overlapping origins. Those forecasts comprise only four disjoint outcomes. V7 rebuilds weekly forecast levels and slopes on genuine past data, using V6’s frozen historical reconstruction. The current, lagged, longer-window, and shuffled-state comparisons share origins and restrict training to dates where a 21-session lag and current state inputs both existed. Consequently `M_STATE` is a changed eligibility refit. The exact earlier recipe retains the frozen `V6_MONTH_STATE` result. None of the historical states were issued prospectively.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V6_MONTH_STATE | 76 | 0.815789 | 0.834409 | 0.178345 | 0.543811 | 0.024823 | 0.033410 | 0.033957 | 0.043058 | 0.381579 | 0.657895 | 0.076202 |
| V6_MONTH_LAG1 | 76 | 0.750000 | 0.763799 | 0.175091 | 0.534801 | 0.024530 | 0.032281 | 0.033132 | 0.043442 | 0.328947 | 0.605263 | 0.072894 |
| V6_BRIER | 76 | 0.539474 | 0.575986 | 0.264309 | 0.726979 | 0.030275 | 0.038624 | 0.037553 | 0.049682 | 0.315789 | 0.500000 | 0.071598 |
| I03_nosize | 76 | 0.565789 | 0.618280 | 0.255858 | 0.708978 | 0.029489 | 0.038723 | 0.037168 | 0.048112 | 0.302632 | 0.500000 | 0.076238 |
| L01 | 76 | 0.447368 | 0.518280 | 0.313912 | 0.837404 | 0.029553 | 0.036865 | 0.039246 | 0.046465 | 0.328947 | 0.486842 | 0.073482 |
| E00 | 76 | 0.407895 | 0.500000 | 0.279282 | 0.752849 | 0.028363 | 0.037393 | 0.038330 | 0.048794 | 0.263158 | 0.618421 | 0.072749 |
| V4_Z_neutral | 76 | 0.407895 | 0.500000 | 0.250000 | 0.693147 | 0.028369 | 0.037393 | 0.038330 | 0.048794 | 0.263158 | 0.618421 | 0.072749 |
| M_STATE_BASE | 76 | 0.368421 | 0.451613 | 0.403612 | 1.058280 | 0.035156 | 0.042882 | 0.047590 | 0.053508 | 0.250000 | 0.421053 | 0.078529 |
| M_STATE | 76 | 0.500000 | 0.577778 | 0.239924 | 0.670084 | 0.029723 | 0.038149 | 0.041833 | 0.046115 | 0.302632 | 0.447368 | 0.073641 |
| M_STATE_LAG5 | 76 | 0.565789 | 0.583154 | 0.197396 | 0.574743 | 0.026503 | 0.032420 | 0.032975 | 0.046052 | 0.368421 | 0.513158 | 0.065738 |
| M_STATE_LAG21 | 76 | 0.763158 | 0.734767 | 0.171774 | 0.520543 | 0.025530 | 0.029936 | 0.033063 | 0.048493 | 0.697368 | 0.842105 | 0.093292 |
| M_STATE_SHIFT5 | 76 | 0.684211 | 0.718280 | 0.190366 | 0.561496 | 0.023773 | 0.030176 | 0.031576 | 0.042107 | 0.368421 | 0.644737 | 0.073489 |
| M_STATE_SHIFT21 | 76 | 0.631579 | 0.663799 | 0.187515 | 0.548883 | 0.024168 | 0.027607 | 0.030140 | 0.042551 | 0.631579 | 0.710526 | 0.080660 |
| M_STATE_126 | 76 | 0.697368 | 0.744444 | 0.206789 | 0.600169 | 0.027378 | 0.035485 | 0.039360 | 0.043322 | 0.355263 | 0.539474 | 0.074921 |
| M_PERSIST | 76 | 0.526316 | 0.584946 | 0.275166 | 0.751994 | 0.028337 | 0.037843 | 0.038689 | 0.047264 | 0.342105 | 0.526316 | 0.084017 |
| C_ELASTIC | 76 | 0.657895 | 0.670968 | 0.201414 | 0.591339 | 0.029193 | 0.040274 | 0.041771 | 0.049925 | 0.447368 | 0.750000 | 0.099270 |


The stricter matched-date current state achieves .239924 Brier, .029723 CRPS and 44.74% coverage. Taking the features back by a full 21 sessions reaches .171774 Brier, 58/76 correct and 84.21% nominal-80% coverage, but CRPS .025530 is worse than V6’s .024530 one-lag candidate. Circularly rolling the training state by five or 21 observations leaves the genuine price features intact, breaks exact state/label alignment and beats the current-state CRPS. The attractive lagged result can reflect persistent regimes and selected history. Neutral and historical forecasts are controls for base rates. Observed up frequency is 40.79% on the 76 dates. An always-majority classifier would get 59.21%, below the retrospective lagged rate. This comparison does not remove label overlap or narrow-period dependence.

| model | score | test | least_gain | most_gain | positive |
| --- | --- | --- | --- | --- | --- |
| M_STATE | brier | omit_fold | -0.001604 | 0.075658 | 2/4 |
| M_STATE | brier | omit_largest_gains | -0.008611 | 0.020345 | 3/4 |
| M_STATE | brier | disjoint_phase | -0.001326 | 0.122002 | 4/5 |
| M_STATE | crps | omit_fold | -0.006414 | -0.002401 | 0/4 |
| M_STATE | crps | omit_largest_gains | -0.006273 | -0.005035 | 0/4 |
| M_STATE | crps | disjoint_phase | -0.005119 | -0.001961 | 0/5 |
| M_STATE_LAG21 | brier | omit_fold | -0.013874 | 0.156936 | 3/4 |
| M_STATE_LAG21 | brier | omit_largest_gains | 0.035551 | 0.086531 | 4/4 |
| M_STATE_LAG21 | brier | disjoint_phase | -0.014230 | 0.148023 | 4/5 |
| M_STATE_LAG21 | crps | omit_fold | -0.004538 | 0.003762 | 2/4 |
| M_STATE_LAG21 | crps | omit_largest_gains | -0.004278 | -0.001136 | 0/4 |
| M_STATE_LAG21 | crps | disjoint_phase | 0.000602 | 0.003413 | 5/5 |
| C_ELASTIC | brier | omit_fold | 0.021010 | 0.084482 | 4/4 |
| C_ELASTIC | brier | omit_largest_gains | 0.032311 | 0.059739 | 4/4 |
| C_ELASTIC | brier | disjoint_phase | -0.021278 | 0.112408 | 4/5 |
| C_ELASTIC | crps | omit_fold | -0.006869 | -0.002434 | 0/4 |
| C_ELASTIC | crps | omit_largest_gains | -0.006468 | -0.004665 | 0/4 |
| C_ELASTIC | crps | disjoint_phase | -0.007267 | -0.001912 | 0/5 |


| horizon | model | n | brier_gain | crps_gain | hist_crps | relative_crps_gain |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | H_NATIVE | 76 | 0.029769 | 0.000987 | 0.011598 | 0.085084 |
| 10 | H_PCA | 76 | 0.035221 | 0.000785 | 0.011598 | 0.067697 |
| 10 | H_STATE | 76 | -0.024595 | -0.000993 | 0.011598 | -0.085617 |
| 10 | H_STUDENT | 76 | -0.017064 | -0.000940 | 0.011598 | -0.081069 |
| 15 | H_NATIVE | 76 | 0.015996 | -0.001762 | 0.017622 | -0.099994 |
| 15 | H_PCA | 76 | 0.005113 | -0.000049 | 0.017622 | -0.002770 |
| 15 | H_STATE | 76 | -0.022478 | -0.003535 | 0.017622 | -0.200595 |
| 15 | H_STUDENT | 76 | -0.024981 | -0.000599 | 0.017622 | -0.034012 |


Ten- and 15-session forecasts use the same 76 original monthly origins with respective maturity windows and own historical benchmarks. Their results remain diagnostic. Expanding horizons increases score units and dependence, so relative CRPS gain normalizes by the appropriate historical-law loss. No redefinition of either primary horizon follows from these observations. All monthly intervals are withheld given four disjoint windows. The lagged state is retained as a persistence hypothesis, and the information-timing mechanism remains unresolved.
