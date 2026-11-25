# V12 Monthly Market Expectations

Monthly endpoint forecasts have **217 rolling origins** and **11 disjoint windows**. The full symmetric reference remains **0.250000 Brier** and **0.025420 CRPS**. Expiry-matched prices, longer maturities, skew, term variance, futures curve, 21-session breadth, slow sector leadership, path-risk calibration and historical shrinkage are new interpretable inputs. Evidence for direction, full endpoint law, movement, path volatility and tail calibration can differ. The V8 monthly smooth result still faces its earlier shifted-state falsification.

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| Q12_NATURALLY_ALIGNED | 0.213414 | 0.282829 | 0.235106 | 0.030169 | 0.025009 | 0.028557 |
| PH_NATIVE_06 | 0.253960 | 0.215771 | 0.240585 | 0.027923 | 0.024757 | 0.026814 |
| V12_IV_NEUTRAL | 0.250000 | 0.250000 | 0.250000 | 0.024157 | 0.028074 | 0.025529 |
| NEUTRAL | 0.250000 | 0.250000 | 0.250000 | 0.024320 | 0.027460 | 0.025420 |
| PH_NATIVE_PHASE_MIXTURE | 0.303459 | 0.267615 | 0.290905 | 0.029659 | 0.028768 | 0.029347 |
| J12_PHASE_MARKET | 0.308225 | 0.269086 | 0.294518 | 0.028178 | 0.028258 | 0.028206 |
| P_CLUSTER | 0.332152 | 0.241883 | 0.300537 | 0.035523 | 0.028950 | 0.033221 |
| V12_STAT | 0.324648 | 0.271660 | 0.306090 | 0.029529 | 0.028000 | 0.028994 |
| P12_Q_HIST_FALLBACK | 0.326020 | 0.270517 | 0.306217 | 0.028047 | 0.028378 | 0.028165 |
| P12_Q_PHYSICAL_MIX | 0.328590 | 0.269306 | 0.307439 | 0.029062 | 0.028380 | 0.028819 |
| HISTORY | 0.324122 | 0.279282 | 0.308418 | 0.027004 | 0.028363 | 0.027480 |
| V12_JOINT_IV | 0.320854 | 0.298563 | 0.313047 | 0.028433 | 0.029456 | 0.028792 |
| V12_IV_LAG5 | 0.337955 | 0.272875 | 0.315162 | 0.029448 | 0.028423 | 0.029089 |
| V12_IV_BRACKET | 0.338374 | 0.273567 | 0.315677 | 0.029525 | 0.028285 | 0.029090 |
| V12_IV_SCALE | 0.340916 | 0.272924 | 0.317103 | 0.029543 | 0.028380 | 0.029135 |
| V12_GLOBAL_SCALE | 0.342367 | 0.272657 | 0.317953 | 0.029607 | 0.028508 | 0.029222 |
| V12_FUTURES_SCALE | 0.342787 | 0.273157 | 0.318401 | 0.029631 | 0.028384 | 0.029195 |
| V12_IV_LONGER | 0.345133 | 0.279717 | 0.321838 | 0.029810 | 0.029244 | 0.029608 |
| REVERSION | 0.275046 | 0.475499 | 0.345251 | 0.026717 | 0.036790 | 0.030245 |
| V6_MONTH_LAG1 | — | 0.175091 | — | — | 0.024530 | — |
| V8_MS_ROLL | — | 0.108239 | — | — | 0.024107 | — |
| V8_MS_WINDOW | — | 0.132367 | — | — | 0.020474 | — |

| model | n | disjoint | path_volatility_mae | absolute_return_error | fixed_down2_forecast_mass | fixed_down2_observed | fixed_down2_tail_brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q12_NATURALLY_ALIGNED | 16 | 7 | — | 0.029561 | 0.223069 | 0.375000 | 0.261494 |
| PH_NATIVE_06 | 217 | 11 | — | — | 0.266900 | 0.391705 | 0.247262 |
| NEUTRAL | 217 | 11 | — | — | 0.208346 | 0.391705 | 0.274932 |
| V12_IV_NEUTRAL | 217 | 11 | 0.040178 | 0.022438 | 0.190509 | 0.391705 | 0.283944 |
| PH_NATIVE_PHASE_MIXTURE | 217 | 11 | — | — | 0.250747 | 0.391705 | 0.289427 |
| J12_PHASE_MARKET | 217 | 11 | — | 0.025396 | 0.222528 | 0.391705 | 0.288353 |
| P_CLUSTER | 217 | 11 | — | — | 0.257700 | 0.391705 | 0.312850 |
| V12_STAT | 217 | 11 | — | 0.025920 | 0.209280 | 0.391705 | 0.294259 |
| P12_Q_HIST_FALLBACK | 199 | 11 | — | 0.024459 | 0.201167 | 0.396985 | 0.295754 |
| P12_Q_PHYSICAL_MIX | 199 | 11 | — | 0.025534 | 0.205712 | 0.396985 | 0.299596 |
| HISTORY | 217 | 11 | — | — | 0.187335 | 0.391705 | 0.290375 |
| V12_JOINT_IV | 217 | 11 | 0.040399 | 0.024324 | 0.175671 | 0.391705 | 0.306394 |
| V12_IV_LAG5 | 217 | 11 | 0.041475 | 0.024489 | 0.197237 | 0.391705 | 0.302308 |
| V12_IV_BRACKET | 217 | 11 | 0.039542 | 0.024457 | 0.200714 | 0.391705 | 0.303092 |
| V12_IV_SCALE | 217 | 11 | 0.040178 | 0.024523 | 0.198961 | 0.391705 | 0.302830 |
| V12_GLOBAL_SCALE | 217 | 11 | 0.041936 | 0.024647 | 0.195580 | 0.391705 | 0.305720 |
| V12_FUTURES_SCALE | 217 | 11 | 0.041006 | 0.024591 | 0.196357 | 0.391705 | 0.304370 |
| V12_IV_LONGER | 205 | 11 | 0.040455 | 0.024278 | 0.198014 | 0.409756 | 0.310064 |
| REVERSION | 217 | 11 | — | — | 0.202927 | 0.391705 | 0.317633 |

The isolated phase-six and naturally aligned subset results are reported with full sample eligibility and disjoint diagnostics. The monthly tables do not infer tight sampling uncertainty from so few independent return periods. As-of source timing and weak casewise coverage deserve at least as much attention as rank. [Monthly probability](monthly-probability-ranking.csv) · [Monthly distribution](monthly-distribution-ranking.csv) · [Matched risk errors](observable-priced-risk.csv) · [Disjoint and deletion diagnostics](phase-and-episode-stress.csv).
