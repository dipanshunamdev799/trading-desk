# NIFTY V9 · Monthly Multiscale Research

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

V8's prominent published monthly candidate, smoothed weekly state with the 126-date fit, scored **.132367 Brier, .020474 CRPS and 85.53%** nominal-80 coverage, but rolling the smoothed inputs produced **.108239 Brier**. V9 newly separates fast contemporaneous factors from 21-session trailing leadership, breadth, synchronization and risk averages. Distributed-lag Ridge adds authentic 0/5/10/21-session financial rotation lags. A second distribution uses previously reconstructed weekly state averages at delayed 0/5/21-session offsets. For multi-task learning, a two-factor reduced-rank Ridge fit shares location across 1/3/5/10/15/21-session returns. All auxiliary labels have ended by the longest-horizon fit boundary. The point prediction shrinks the shared estimate halfway toward ordinary direct monthly Ridge. Neither shared labels nor simulations multiply observed NIFTY outcomes.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_HIST | 141.000000 | 7.000000 | 10.184356 | 0.453901 | 0.500000 | 0.324122 | 0.860553 | 0.027004 | 0.034685 | 0.046848 | 0.013288 | 0.290780 | 0.567376 | 0.061732 |
| P_REVERT | 141.000000 | 7.000000 | 10.184356 | 0.617021 | 0.628247 | 0.275046 | 0.812606 | 0.026717 | 0.033546 | 0.044253 | 0.013321 | 0.425532 | 0.560284 | 0.069226 |
| P_MOMENTUM | 141.000000 | 7.000000 | 10.184356 | 0.510638 | 0.512378 | 0.314329 | 0.849428 | 0.029470 | 0.036053 | 0.047736 | 0.014914 | 0.489362 | 0.574468 | 0.089366 |
| P_CLUSTER | 141.000000 | 7.000000 | 10.184356 | 0.503546 | 0.523032 | 0.332152 | 0.915162 | 0.035523 | 0.047287 | 0.062495 | 0.017196 | 0.368794 | 0.617021 | 0.088085 |
| M_FAST | 141.000000 | 7.000000 | 10.184356 | 0.468085 | 0.481331 | 0.378201 | 1.094509 | 0.032657 | 0.042429 | 0.054808 | 0.016528 | 0.333333 | 0.531915 | 0.078837 |
| M_SLOW | 141.000000 | 7.000000 | 10.184356 | 0.482270 | 0.496956 | 0.388187 | 1.116761 | 0.031623 | 0.040107 | 0.053988 | 0.016070 | 0.347518 | 0.553191 | 0.075139 |
| M_FAST_SLOW | 141.000000 | 7.000000 | 10.184356 | 0.482270 | 0.496956 | 0.396509 | 1.140268 | 0.032476 | 0.041584 | 0.054617 | 0.016441 | 0.319149 | 0.546099 | 0.077007 |
| M_DISTRIBUTED | 141.000000 | 7.000000 | 10.184356 | 0.503546 | 0.520394 | 0.372854 | 1.071855 | 0.030646 | 0.038974 | 0.052129 | 0.015592 | 0.333333 | 0.517730 | 0.073474 |
| M_MULTITASK | 141.000000 | 7.000000 | 10.184356 | 0.503546 | 0.520394 | 0.375018 | 1.082419 | 0.030751 | 0.039119 | 0.051996 | 0.015632 | 0.312057 | 0.517730 | 0.072729 |
| PATH_EMPIRICAL | 141.000000 | 7.000000 | 10.184356 | 0.453901 | 0.500000 | 0.324122 | 0.860553 | 0.027004 | 0.034685 | 0.046848 | 0.013303 | 0.290780 | 0.567376 | 0.061732 |
| PATH_REGIME | 141.000000 | 7.000000 | 10.184356 | 0.453901 | 0.500000 | 0.333401 | 0.880306 | 0.027076 | 0.034947 | 0.047078 | 0.013304 | 0.269504 | 0.645390 | 0.068197 |
| PATH_AR_REGIME | 141.000000 | 7.000000 | 10.184356 | 0.453901 | 0.500000 | 0.333341 | 0.880161 | 0.027074 | 0.034943 | 0.047077 | 0.013303 | 0.269504 | 0.631206 | 0.068172 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_HIST | 76 | 4 | 4.698728 | 0.407895 | 0.500000 | 0.279282 | 0.752849 | 0.028363 | 0.037393 | 0.048794 | 0.014010 | 0.263158 | 0.618421 | 0.072749 |
| P_REVERT | 76 | 4 | 4.698728 | 0.105263 | 0.103943 | 0.475499 | 1.220294 | 0.036790 | 0.045547 | 0.055759 | 0.018749 | 0.078947 | 0.263158 | 0.049045 |
| P_MOMENTUM | 76 | 4 | 4.698728 | 0.381579 | 0.352330 | 0.383061 | 0.991655 | 0.036190 | 0.045954 | 0.059147 | 0.018477 | 0.223684 | 0.407895 | 0.061187 |
| P_CLUSTER | 76 | 4 | 4.698728 | 0.592105 | 0.600358 | 0.241883 | 0.675385 | 0.028950 | 0.036773 | 0.049991 | 0.014675 | 0.513158 | 0.605263 | 0.084227 |
| M_FAST | 76 | 4 | 4.698728 | 0.131579 | 0.131183 | 0.540190 | 1.390406 | 0.041160 | 0.051635 | 0.062048 | 0.020897 | 0.105263 | 0.289474 | 0.059999 |
| M_SLOW | 76 | 4 | 4.698728 | 0.118421 | 0.135125 | 0.540765 | 1.385625 | 0.045942 | 0.059719 | 0.071456 | 0.022852 | 0.131579 | 0.355263 | 0.080080 |
| M_FAST_SLOW | 76 | 4 | 4.698728 | 0.131579 | 0.146237 | 0.543063 | 1.392144 | 0.046679 | 0.061109 | 0.072214 | 0.023113 | 0.131579 | 0.368421 | 0.082463 |
| M_DISTRIBUTED | 76 | 4 | 4.698728 | 0.105263 | 0.124014 | 0.539987 | 1.381633 | 0.044025 | 0.056389 | 0.068064 | 0.022122 | 0.157895 | 0.355263 | 0.073495 |
| M_MULTITASK | 76 | 4 | 4.698728 | 0.105263 | 0.124014 | 0.537378 | 1.374158 | 0.043949 | 0.056319 | 0.067978 | 0.022073 | 0.131579 | 0.355263 | 0.073772 |
| M_SLOW_MATCH | 76 | 4 | 4.698728 | 0.144737 | 0.177419 | 0.556036 | 1.426433 | 0.049854 | 0.064715 | 0.074285 | 0.023695 | 0.157895 | 0.328947 | 0.101209 |
| M_SMOOTH | 76 | 4 | 4.698728 | 0.263158 | 0.257348 | 0.446494 | 1.165258 | 0.037911 | 0.049582 | 0.061673 | 0.018680 | 0.157895 | 0.394737 | 0.078897 |
| M_STATE_LAGS | 76 | 4 | 4.698728 | 0.421053 | 0.405735 | 0.344089 | 0.936095 | 0.032396 | 0.039608 | 0.057338 | 0.016032 | 0.526316 | 0.631579 | 0.082846 |
| PATH_EMPIRICAL | 76 | 4 | 4.698728 | 0.407895 | 0.500000 | 0.279282 | 0.752849 | 0.028363 | 0.037393 | 0.048794 | 0.013962 | 0.263158 | 0.618421 | 0.072749 |
| PATH_REGIME | 76 | 4 | 4.698728 | 0.407895 | 0.500000 | 0.283976 | 0.763071 | 0.028588 | 0.037836 | 0.048952 | 0.014046 | 0.263158 | 0.605263 | 0.071325 |
| PATH_AR_REGIME | 76 | 4 | 4.698728 | 0.407895 | 0.500000 | 0.283976 | 0.763071 | 0.028590 | 0.037837 | 0.048951 | 0.014051 | 0.263158 | 0.605263 | 0.071350 |
| V8_MS_WINDOW | 76 | 4 | 4.698728 | 0.855263 | 0.822581 | 0.132367 | 0.432753 | 0.020474 | 0.023172 | 0.038494 | 0.010393 | 0.763158 | 0.855263 | 0.085563 |
| V8_MS_ROLL | 76 | 4 | 4.698728 | 0.907895 | 0.917204 | 0.108239 | 0.381136 | 0.024107 | 0.027235 | 0.039497 | 0.011809 | 0.618421 | 0.763158 | 0.091329 |


## Placebo distribution and availability

The placebo family shifts only historical training states by nine predeclared offsets in both directions and adds three block permutations. It retains query features and genuine price controls. Availability matching requires full 21-session smooth states and a genuinely lagged history. Most earlier monthly fits cannot meet the common state history requirement. Later matched states therefore use fewer dates than the principal 76-origin cohort. Every insufficient fold remains visible. Reversal, momentum and empirical history supply persistence benchmarks.

| model | n | disjoint | brier | crps | coverage80 |
| --- | --- | --- | --- | --- | --- |
| M_PERM_1 | 76 | 4 | 0.490300 | 0.043639 | 0.394737 |
| M_PERM_2 | 76 | 4 | 0.451043 | 0.041212 | 0.407895 |
| M_PERM_3 | 76 | 4 | 0.621155 | 0.065334 | 0.250000 |
| M_SHIFT_+10 | 76 | 4 | 0.490880 | 0.042144 | 0.289474 |
| M_SHIFT_+21 | 76 | 4 | 0.428013 | 0.036666 | 0.447368 |
| M_SHIFT_+42 | 76 | 4 | 0.511525 | 0.051728 | 0.381579 |
| M_SHIFT_+5 | 76 | 4 | 0.444362 | 0.039865 | 0.342105 |
| M_SHIFT_+63 | 76 | 4 | 0.510210 | 0.050054 | 0.342105 |
| M_SHIFT_-10 | 76 | 4 | 0.314453 | 0.039755 | 0.421053 |
| M_SHIFT_-21 | 76 | 4 | 0.490645 | 0.048594 | 0.447368 |
| M_SHIFT_-42 | 76 | 4 | 0.585758 | 0.051852 | 0.197368 |
| M_SHIFT_-5 | 76 | 4 | 0.315876 | 0.037713 | 0.539474 |


| model | metric | test | minimum | maximum | positive |
| --- | --- | --- | --- | --- | --- |
| M_DISTRIBUTED | brier | disjoint_phase | -0.373060 | -0.150075 | 0/5 |
| M_DISTRIBUTED | brier | leave_month | -0.318583 | -0.217412 | 0/4 |
| M_DISTRIBUTED | brier | omit_best | -0.305991 | -0.265770 | 0/4 |
| M_DISTRIBUTED | crps | disjoint_phase | -0.023906 | -0.010734 | 0/5 |
| M_DISTRIBUTED | crps | leave_month | -0.018366 | -0.013198 | 0/4 |
| M_DISTRIBUTED | crps | omit_best | -0.018219 | -0.015919 | 0/4 |
| M_MULTITASK | brier | disjoint_phase | -0.373060 | -0.160834 | 0/5 |
| M_MULTITASK | brier | leave_month | -0.317631 | -0.213807 | 0/4 |
| M_MULTITASK | brier | omit_best | -0.302718 | -0.262837 | 0/4 |
| M_MULTITASK | crps | disjoint_phase | -0.023719 | -0.010675 | 0/5 |
| M_MULTITASK | crps | leave_month | -0.018519 | -0.013205 | 0/4 |
| M_MULTITASK | crps | omit_best | -0.018132 | -0.015849 | 0/4 |
| M_SLOW | brier | disjoint_phase | -0.381891 | -0.171186 | 0/5 |
| M_SLOW | brier | leave_month | -0.324150 | -0.216548 | 0/4 |
| M_SLOW | brier | omit_best | -0.311352 | -0.267340 | 0/4 |
| M_SLOW | crps | disjoint_phase | -0.027363 | -0.013077 | 0/5 |
| M_SLOW | crps | leave_month | -0.020806 | -0.014833 | 0/4 |
| M_SLOW | crps | omit_best | -0.020438 | -0.017866 | 0/4 |
| M_SMOOTH | brier | disjoint_phase | -0.291196 | -0.084313 | 0/5 |
| M_SMOOTH | brier | leave_month | -0.262327 | -0.127599 | 0/4 |
| M_SMOOTH | brier | omit_best | -0.212682 | -0.171806 | 0/4 |
| M_SMOOTH | crps | disjoint_phase | -0.014929 | -0.005922 | 0/5 |
| M_SMOOTH | crps | leave_month | -0.014635 | -0.006336 | 0/4 |
| M_SMOOTH | crps | omit_best | -0.012030 | -0.009835 | 0/4 |
| PATH_REGIME | brier | disjoint_phase | 0.003437 | 0.008943 | 5/5 |
| PATH_REGIME | brier | leave_month | -0.008464 | 0.003000 | 1/4 |
| PATH_REGIME | brier | omit_best | -0.009575 | -0.005443 | 0/4 |
| PATH_REGIME | crps | disjoint_phase | -0.000184 | 0.000602 | 3/5 |
| PATH_REGIME | crps | leave_month | -0.000505 | 0.000247 | 1/4 |
| PATH_REGIME | crps | omit_best | -0.000567 | -0.000288 | 0/4 |


## Path-derived distributions

One model reuses contiguous historical log-return blocks. A second reweights them by similar initial trend/risk using normalized distances. A third fits a modest AR(2) daily mean and recursively simulates contiguous historical residual blocks. Every full block ends before the forecast anchor. Daily log returns are compounded into endpoint laws, and every path weight is preserved for sample reconstruction. The separate risk outcomes are future daily RMS and **daily-close** path touches below −2%, with no tick-level barrier inference. Raw block sampling reproduces the empirical endpoint law. Conditioning does not broadly improve endpoint scores or resolve the V8 monthly timing question.

| cohort | model | n | vol_mae | barrier_brier | mean_atom_ESS |
| --- | --- | --- | --- | --- | --- |
| early | PATH_AR_REGIME | 141 | 0.047854 | 0.375606 | 171.814060 |
| early | PATH_EMPIRICAL | 141 | 0.051668 | 0.361523 | 201.773050 |
| early | PATH_REGIME | 141 | 0.047856 | 0.374701 | 171.814060 |
| later | PATH_AR_REGIME | 76 | 0.027635 | 0.285881 | 224.563463 |
| later | PATH_EMPIRICAL | 76 | 0.031798 | 0.271542 | 252.000000 |
| later | PATH_REGIME | 76 | 0.027635 | 0.285496 | 224.563463 |


The later monthly cohort contains only four disjoint returns. The earlier monthly cohort has more origins and different behavior, which remains research-exposed. V9 does not replace V8's exploratory state system with a validated monthly model.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
