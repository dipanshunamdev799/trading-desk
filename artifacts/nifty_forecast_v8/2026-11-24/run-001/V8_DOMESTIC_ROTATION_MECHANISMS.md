# NIFTY V8 · Domestic Rotation Mechanisms

Run `2026-11-24/run-001`. Retrospective research.

The smallest successful incremental feature is the five-session **change in the difference** between Bank Nifty and Financial Services five-session returns. It gives .161633 Brier by itself, versus .169803 for the same native base, .170473 for the defensive change by itself, and .162294 for the two raw differences together. The baseline still contains 51 native inputs, so “one feature” describes the addition rather than a single-input forecasting system. Defensive spread uses mean pharma and FMCG returns minus mean auto, metals and energy returns. The combined residual specification removes common market exposure using a trailing 63-session spread-on-NIFTY beta lagged one session before differencing. This gives the lowest unperturbed weekly Brier, **.159504**. It is a predictive residualization exercise. No constituent-level bank exposures or causal rotation mechanism were identified.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_NATIVE | 92 | 19 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.019635 | 0.005068 | 0.510870 | 0.793478 | 0.039009 |
| B_ROT | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038767 |
| R_BANK | 92 | 19 | 0.804348 | 0.809869 | 0.161633 | 0.503976 | 0.009918 | 0.012892 | 0.019358 | 0.004982 | 0.554348 | 0.815217 | 0.038770 |
| R_DEF | 92 | 19 | 0.793478 | 0.800435 | 0.170473 | 0.524057 | 0.010048 | 0.013040 | 0.019593 | 0.005068 | 0.510870 | 0.793478 | 0.038976 |
| R_LEVEL | 92 | 19 | 0.782609 | 0.791001 | 0.170114 | 0.523185 | 0.010072 | 0.013076 | 0.019617 | 0.005083 | 0.500000 | 0.804348 | 0.038958 |
| R_LEVEL_CHANGE | 92 | 19 | 0.782609 | 0.791001 | 0.161616 | 0.503888 | 0.009959 | 0.012828 | 0.019428 | 0.005018 | 0.500000 | 0.815217 | 0.038447 |
| R_RESIDUAL | 92 | 19 | 0.804348 | 0.809869 | 0.159504 | 0.499670 | 0.009852 | 0.012801 | 0.019329 | 0.004980 | 0.521739 | 0.815217 | 0.038406 |
| R_NORMAL | 92 | 19 | 0.782609 | 0.787615 | 0.163545 | 0.508767 | 0.009902 | 0.012886 | 0.019376 | 0.004994 | 0.510870 | 0.815217 | 0.038776 |
| R_SLOPE | 92 | 19 | 0.782609 | 0.791001 | 0.167287 | 0.516897 | 0.010058 | 0.013089 | 0.019559 | 0.005093 | 0.489130 | 0.815217 | 0.039154 |
| R_ACCEL | 92 | 19 | 0.793478 | 0.803822 | 0.163400 | 0.507907 | 0.009913 | 0.012862 | 0.019359 | 0.004988 | 0.532609 | 0.815217 | 0.039090 |
| R_SWITCH | 92 | 19 | 0.793478 | 0.797049 | 0.164290 | 0.509993 | 0.009906 | 0.012788 | 0.019433 | 0.005004 | 0.510870 | 0.815217 | 0.038932 |
| R_EXTREME | 92 | 19 | 0.793478 | 0.800435 | 0.162219 | 0.505717 | 0.009934 | 0.012913 | 0.019336 | 0.005019 | 0.500000 | 0.815217 | 0.039111 |
| R_INTERACT | 92 | 19 | 0.804348 | 0.809869 | 0.163545 | 0.508030 | 0.009881 | 0.012888 | 0.019269 | 0.004980 | 0.532609 | 0.815217 | 0.037799 |
| R_LAG1 | 92 | 19 | 0.804348 | 0.809869 | 0.165693 | 0.513659 | 0.010005 | 0.013051 | 0.019486 | 0.005060 | 0.510870 | 0.804348 | 0.039005 |
| R_LAG5 | 92 | 19 | 0.793478 | 0.803822 | 0.162741 | 0.506419 | 0.010005 | 0.012982 | 0.019503 | 0.005065 | 0.543478 | 0.804348 | 0.039164 |
| R_LAG10 | 92 | 19 | 0.793478 | 0.800435 | 0.166941 | 0.516610 | 0.010043 | 0.013102 | 0.019607 | 0.005079 | 0.532609 | 0.804348 | 0.039327 |
| R_SMOOTH | 92 | 19 | 0.782609 | 0.784228 | 0.163778 | 0.508776 | 0.010172 | 0.012969 | 0.019795 | 0.005178 | 0.554348 | 0.782609 | 0.038010 |
| R_WRAP | 92 | 19 | 0.771739 | 0.774794 | 0.176970 | 0.538457 | 0.010402 | 0.013618 | 0.020315 | 0.005242 | 0.510870 | 0.782609 | 0.039063 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| B_NATIVE | B_NATIVE | brier | 92 | 0.000000 |
| B_NATIVE | B_NATIVE | crps | 92 | 0.000000 |
| B_ROT | B_NATIVE | brier | 92 | 0.007509 |
| B_ROT | B_NATIVE | crps | 92 | 0.000171 |
| R_ACCEL | B_ROT | brier | 92 | -0.001106 |
| R_ACCEL | B_ROT | crps | 92 | -0.000016 |
| R_BANK | B_NATIVE | brier | 92 | 0.008170 |
| R_BANK | B_NATIVE | crps | 92 | 0.000150 |
| R_DEF | B_NATIVE | brier | 92 | -0.000670 |
| R_DEF | B_NATIVE | crps | 92 | 0.000020 |
| R_EXTREME | B_ROT | brier | 92 | 0.000075 |
| R_EXTREME | B_ROT | crps | 92 | -0.000037 |
| R_INTERACT | B_ROT | brier | 92 | -0.001251 |
| R_INTERACT | B_ROT | crps | 92 | 0.000015 |
| R_LAG1 | B_ROT | brier | 92 | -0.003399 |
| R_LAG1 | B_ROT | crps | 92 | -0.000108 |
| R_LAG10 | B_ROT | brier | 92 | -0.004647 |
| R_LAG10 | B_ROT | crps | 92 | -0.000146 |
| R_LAG5 | B_ROT | brier | 92 | -0.000447 |
| R_LAG5 | B_ROT | crps | 92 | -0.000109 |
| R_LEVEL | B_NATIVE | brier | 92 | -0.000311 |
| R_LEVEL | B_NATIVE | crps | 92 | -0.000004 |
| R_LEVEL_CHANGE | B_ROT | brier | 92 | 0.000678 |
| R_LEVEL_CHANGE | B_ROT | crps | 92 | -0.000062 |
| R_NORMAL | B_ROT | brier | 92 | -0.001251 |
| R_NORMAL | B_ROT | crps | 92 | -0.000005 |
| R_RESIDUAL | B_ROT | brier | 92 | 0.002790 |
| R_RESIDUAL | B_ROT | crps | 92 | 0.000045 |
| R_SLOPE | B_ROT | brier | 92 | -0.004993 |
| R_SLOPE | B_ROT | crps | 92 | -0.000162 |
| R_SMOOTH | B_ROT | brier | 92 | -0.001484 |
| R_SMOOTH | B_ROT | crps | 92 | -0.000276 |
| R_SWITCH | B_ROT | brier | 92 | -0.001996 |
| R_SWITCH | B_ROT | crps | 92 | -0.000009 |
| R_WRAP | B_ROT | brier | 92 | -0.014676 |
| R_WRAP | B_ROT | crps | 92 | -0.000505 |


Levels alone are weaker than changes. Slope, scale normalization, acceleration, sign-crossing and extreme-event variants do not consistently beat the residualized result. Five-session-lagged raw changes still give .162741 Brier. Ten-session lag reaches .166941. Wrapping the fit-only rotation fields gives .176970, worse than genuine alignment. Delaying the residualized lead itself by five sessions gives .166000 and shrinking its window to 189 fits gives .223071. These contrasts support both short-run information and regime persistence as plausible explanations.

| model | condition | value | n | disjoint | brier_gain | CRPS_gain | leave_month_gain_min | leave_month_gain_max | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R_RESIDUAL | trend_sign | False | 48 | 11 | 0.005835 | 0.000142 | 0.004140 | 0.008530 | 0.791667 |
| R_RESIDUAL | trend_sign | True | 44 | 10 | -0.000532 | -0.000062 | -0.007514 | 0.003886 | 0.840909 |
| R_RESIDUAL | market_breadth | False | 52 | 14 | 0.001309 | 0.000048 | -0.000658 | 0.003699 | 0.846154 |
| R_RESIDUAL | market_breadth | True | 40 | 12 | 0.004715 | 0.000040 | 0.001266 | 0.010781 | 0.775000 |
| R_RESIDUAL | financial_strength | False | 50 | 13 | -0.001084 | 0.000086 | -0.005387 | 0.001996 | 0.740000 |
| R_RESIDUAL | financial_strength | True | 42 | 13 | 0.007402 | -0.000005 | 0.005126 | 0.009526 | 0.904762 |
| R_RESIDUAL | defensive_leadership | False | 39 | 9 | 0.004968 | 0.000073 | 0.001171 | 0.007457 | 0.923077 |
| R_RESIDUAL | defensive_leadership | True | 53 | 14 | 0.001187 | 0.000024 | -0.000384 | 0.003082 | 0.735849 |
| R_RESIDUAL | global_strength | False | 49 | 14 | 0.002806 | 0.000083 | 0.000821 | 0.005765 | 0.836735 |
| R_RESIDUAL | global_strength | True | 43 | 14 | 0.002772 | 0.000001 | 0.000143 | 0.005544 | 0.790698 |
| R_RESIDUAL | historical_volatility_regime | high_vol | 52 | 11 | 0.002980 | 0.000027 | -0.000536 | 0.007158 | 0.769231 |
| R_RESIDUAL | historical_volatility_regime | low_vol | 40 | 8 | 0.002543 | 0.000067 | 0.002169 | 0.003004 | 0.875000 |
| R_RESIDUAL | reversal_realized | False | 47 | 14 | 0.000939 | -0.000065 | -0.004895 | 0.005282 | 0.765957 |
| R_RESIDUAL | reversal_realized | True | 45 | 11 | 0.004723 | 0.000159 | 0.002280 | 0.008492 | 0.866667 |


The reversal slice conditions on what actually happened, which cannot serve as a decision-time filter. Conditional tables report counts, disjoint counts and leave-month ranges as descriptive uncertainty. They do not furnish independent confidence intervals on thin strata.

| model | baseline | metric | n | gain | simultaneous95_block10 |
| --- | --- | --- | --- | --- | --- |
| B_ROT | T_ROT_DOMESTIC | brier | 92 | -0.000149 | [-0.002796, 0.002498] |
| B_ROT | T_ROT_DOMESTIC | crps | 92 | 0.000030 | [-0.000026, 0.000086] |
| B_ROT | T_ELASTIC_EMBARGO | brier | 92 | 0.021840 | [-0.036814, 0.080493] |
| B_ROT | T_ELASTIC_EMBARGO | crps | 92 | -0.000231 | [-0.003003, 0.002541] |
| R_BANK | T_ROT_DOMESTIC | brier | 92 | 0.000512 | [-0.002144, 0.003169] |
| R_BANK | T_ROT_DOMESTIC | crps | 92 | 0.000009 | [-0.000044, 0.000061] |
| R_BANK | T_ELASTIC_EMBARGO | brier | 92 | 0.022501 | [-0.033610, 0.078612] |
| R_BANK | T_ELASTIC_EMBARGO | crps | 92 | -0.000252 | [-0.003070, 0.002565] |
| R_LEVEL_CHANGE | T_ROT_DOMESTIC | brier | 92 | 0.000529 | [-0.007498, 0.008556] |
| R_LEVEL_CHANGE | T_ROT_DOMESTIC | crps | 92 | -0.000032 | [-0.000267, 0.000203] |
| R_LEVEL_CHANGE | T_ELASTIC_EMBARGO | brier | 92 | 0.022517 | [-0.035265, 0.080300] |
| R_LEVEL_CHANGE | T_ELASTIC_EMBARGO | crps | 92 | -0.000293 | [-0.003133, 0.002546] |
| R_RESIDUAL | T_ROT_DOMESTIC | brier | 92 | 0.002641 | [-0.006632, 0.011914] |
| R_RESIDUAL | T_ROT_DOMESTIC | crps | 92 | 0.000075 | [-0.000223, 0.000372] |
| R_RESIDUAL | T_ELASTIC_EMBARGO | brier | 92 | 0.024630 | [-0.031447, 0.080707] |
| R_RESIDUAL | T_ELASTIC_EMBARGO | crps | 92 | -0.000187 | [-0.002952, 0.002579] |


The primary weekly cohort has 92 overlapping origins, 19 disjoint windows and a return-ACF ESS of about 12.36. Monthly evaluation has 76 overlapping origins and approximately four disjoint windows. Dependence diagnostics are not independent trials.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
