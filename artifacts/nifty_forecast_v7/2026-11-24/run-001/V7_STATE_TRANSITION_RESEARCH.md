# NIFTY V7 · State Transition Research

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The matched levels parent uses mean correlation, first eigenvalue share, volatility synchronization, participation, concentration and bank/financial spread. The state model adds five-session differences, five-session loading drift and a regularized next-session high-correlation transition frequency. The high-correlation state uses mean pair correlation >.60. The transition estimate conditions on the observed current state, counts transitions ending by the origin over a trailing 63-session window, and uses Beta(2,2) smoothing. The acceleration model adds second differences with a five-session spacing. Added changes are delayed five sessions in the placebo. The frozen labels remain endpoint returns at 5 and 21 trading sessions.

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S_LEVEL | 92 | 0.760870 | 0.768747 | 0.175319 | 0.532980 | 0.010030 | 0.013122 | 0.012654 | 0.019680 | 0.576087 | 0.771739 | 0.038273 |
| S_STATE | 92 | 0.782609 | 0.794388 | 0.181259 | 0.546605 | 0.010350 | 0.013340 | 0.012954 | 0.020236 | 0.532609 | 0.793478 | 0.038281 |
| S_STATE_LAG | 92 | 0.728261 | 0.733672 | 0.197292 | 0.582443 | 0.010602 | 0.013938 | 0.013518 | 0.020778 | 0.521739 | 0.793478 | 0.037765 |
| S_STATE_ACCEL | 92 | 0.760870 | 0.768747 | 0.170173 | 0.521355 | 0.009851 | 0.012809 | 0.012492 | 0.019384 | 0.565217 | 0.782609 | 0.037953 |
| S_ROTATION | 92 | 0.793478 | 0.800435 | 0.164548 | 0.510719 | 0.010041 | 0.012926 | 0.012534 | 0.019425 | 0.554348 | 0.815217 | 0.040028 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S_LEVEL | 76 | 0.552632 | 0.582079 | 0.261143 | 0.721265 | 0.030293 | 0.038702 | 0.037279 | 0.050369 | 0.315789 | 0.526316 | 0.072308 |
| S_STATE | 76 | 0.394737 | 0.448746 | 0.349191 | 0.930600 | 0.033935 | 0.042505 | 0.042272 | 0.053460 | 0.263158 | 0.460526 | 0.069128 |
| S_STATE_LAG | 76 | 0.407895 | 0.459857 | 0.322731 | 0.860027 | 0.032633 | 0.040849 | 0.041180 | 0.052220 | 0.250000 | 0.500000 | 0.070944 |
| S_STATE_ACCEL | 76 | 0.565789 | 0.593190 | 0.256470 | 0.718019 | 0.029931 | 0.037963 | 0.037376 | 0.050055 | 0.355263 | 0.513158 | 0.071628 |
| S_ROTATION | 76 | 0.526316 | 0.564875 | 0.259650 | 0.716482 | 0.030235 | 0.038728 | 0.037848 | 0.049712 | 0.355263 | 0.500000 | 0.071515 |
| M_PERSIST | 76 | 0.526316 | 0.584946 | 0.275166 | 0.751994 | 0.028337 | 0.037843 | 0.038689 | 0.047264 | 0.342105 | 0.526316 | 0.084017 |


| horizon | target | method | n | mae | rmse | actual_mean |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | large_move | CHANGE | 92 | 0.353377 | 0.451549 | 0.282609 |
| 5 | large_move | LEVEL | 92 | 0.351630 | 0.451138 | 0.282609 |
| 5 | magnitude | CHANGE | 92 | 0.010747 | 0.016319 | 0.016249 |
| 5 | magnitude | LEVEL | 92 | 0.010454 | 0.016376 | 0.016249 |
| 5 | volatility | CHANGE | 92 | 0.039296 | 0.050506 | 0.115858 |
| 5 | volatility | LEVEL | 92 | 0.039804 | 0.052460 | 0.115858 |
| 21 | large_move | CHANGE | 76 | 0.400317 | 0.506760 | 0.342105 |
| 21 | large_move | LEVEL | 76 | 0.365290 | 0.480435 | 0.342105 |
| 21 | magnitude | CHANGE | 76 | 0.023536 | 0.032548 | 0.037221 |
| 21 | magnitude | LEVEL | 76 | 0.022236 | 0.031560 | 0.037221 |
| 21 | volatility | CHANGE | 76 | 0.021716 | 0.025343 | 0.114772 |
| 21 | volatility | LEVEL | 76 | 0.022377 | 0.026226 | 0.114772 |


The risk comparisons add matched changes beyond their own corresponding levels. For 21-session realized volatility, change inputs reduce annualized volatility MAE from .022377 to .021716. For five-session absolute returns, MAE increases from .010454 to .010747. The large-move target is |return| above 2% at five sessions or 4% at 21 sessions. Its probabilities are bounded Ridge estimates and RMSE squared is Brier. Both large-move changes are weaker by MAE. The risk tests score dependent dates and provide no independent evidence of regime-break skill. Absolute-return forecasts and forward realized volatility are separate targets with distinct units.

The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.
