# V12 Expectation Vs Reality

The baseline is V11’s stronger complete-law ensemble excluding the base rotation expert. Compare Q forecasts with that law and matured empirical history on identical dates. The Q quantities are what can be inferred from the archived marked option curve. The P candidates statistically calibrate realized returns using only prior matured observations. Transformations tested include retaining priced shape while taking the statistical center, a capped historical realized-to-priced width adjustment, strongly regularized logit calibration of option-derived positive mass, a fixed 25% calibrated priced-law mixture, and an additional 25% historical fallback. The raw Q mixture is diagnostic and remains tagged with its pricing provenance. The learned disagreement model requires 24 earlier mature matched option and statistical forecasts before adding a limited location correction.

## Observables against realized outcomes

| horizon | market_feature | target | n | mean_feature | mean_target | mae | spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | iv_nearest | realized_vol | 265 | 0.131751 | 0.123981 | 0.037814 | 0.611711 |
| 5 | iv_bracket | realized_vol | 265 | 0.132027 | 0.123981 | 0.038336 | 0.609690 |
| 5 | rv_forecast | realized_vol | 265 | 0.125370 | 0.123981 | 0.046394 | 0.503901 |
| 5 | straddle_horizon_scaled | absolute_return | 265 | 0.015102 | 0.015052 | 0.009468 | 0.316312 |
| 5 | iv_target_total_sd | absolute_return | 265 | 0.018772 | 0.015052 | 0.010572 | 0.316286 |
| 5 | iv_term | realized_vol | 265 | -0.000057 | 0.123981 | — | -0.395385 |
| 5 | iv_skew | realized_down | 265 | 0.015941 | 0.558491 | — | -0.048875 |
| 5 | density_priced_down5 | realized_down5 | 265 | 0.024247 | 0.003774 | — | 0.070814 |
| 5 | iv_nearest | realized_return | 265 | 0.131751 | -0.000025 | — | 0.134527 |
| 21 | iv_nearest | realized_vol | 217 | 0.134425 | 0.138004 | 0.039639 | 0.448765 |
| 21 | iv_bracket | realized_vol | 217 | 0.133599 | 0.138004 | 0.039406 | 0.444422 |
| 21 | rv_forecast | realized_vol | 217 | 0.129896 | 0.138004 | 0.048044 | 0.400273 |
| 21 | straddle_horizon_scaled | absolute_return | 217 | 0.031555 | 0.033371 | 0.023762 | -0.012108 |
| 21 | iv_target_total_sd | absolute_return | 217 | 0.039336 | 0.033371 | 0.026517 | -0.008345 |
| 21 | iv_term | realized_vol | 217 | -0.000571 | 0.138004 | — | -0.396329 |
| 21 | iv_skew | realized_down | 213 | 0.025407 | 0.563380 | — | -0.237855 |
| 21 | density_priced_down5 | realized_down5 | 199 | 0.093630 | 0.135678 | — | -0.255700 |
| 21 | iv_nearest | realized_return | 217 | 0.134425 | -0.007535 | — | 0.535212 |

## Priced-law versus statistical or calibrated parents

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | P12_Q_HIST_FALLBACK | P12_Q_PHYSICAL_MIX | brier | 265 | 53 | 0.245870 | 0.244491 | -0.001379 | -0.011027 | 0.008269 |
| 5 | combined | P12_Q_HIST_FALLBACK | P12_Q_PHYSICAL_MIX | crps | 265 | 53 | 0.010727 | 0.010704 | -0.000023 | -0.000503 | 0.000457 |
| 5 | combined | P12_Q_LOCATION | Q12_RAW | brier | 265 | 53 | 0.247555 | 0.268655 | 0.021100 | -0.032008 | 0.074209 |
| 5 | combined | P12_Q_LOCATION | Q12_RAW | crps | 265 | 53 | 0.010786 | 0.011151 | 0.000365 | -0.001794 | 0.002523 |
| 5 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | brier | 265 | 53 | 0.244491 | 0.244333 | -0.000158 | -0.006134 | 0.005818 |
| 5 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | crps | 265 | 53 | 0.010704 | 0.010777 | 0.000073 | -0.000173 | 0.000319 |
| 5 | combined | P12_Q_SCALE | P12_Q_LOCATION | brier | 265 | 53 | 0.250357 | 0.247555 | -0.002803 | -0.011479 | 0.005874 |
| 5 | combined | P12_Q_SCALE | P12_Q_LOCATION | crps | 265 | 53 | 0.010818 | 0.010786 | -0.000032 | -0.000245 | 0.000180 |
| 5 | combined | P12_Q_TILT | P12_Q_SCALE | brier | 265 | 53 | 0.248254 | 0.250357 | 0.002103 | -0.035375 | 0.039581 |
| 5 | combined | P12_Q_TILT | P12_Q_SCALE | crps | 265 | 53 | 0.010734 | 0.010818 | 0.000085 | -0.000863 | 0.001033 |
| 5 | combined | Q12_BLACK_ATM | Q12_RAW | brier | 265 | 53 | 0.256350 | 0.268655 | 0.012305 | -0.009907 | 0.034518 |
| 5 | combined | Q12_BLACK_ATM | Q12_RAW | crps | 265 | 53 | 0.010907 | 0.011151 | 0.000244 | -0.000235 | 0.000724 |
| 5 | combined | Q12_NATURALLY_ALIGNED | J11_EXCLUDE_B_ROT | brier | 55 | 43 | 0.280025 | 0.239770 | -0.040255 | -0.149649 | 0.069139 |
| 5 | combined | Q12_NATURALLY_ALIGNED | J11_EXCLUDE_B_ROT | crps | 55 | 43 | 0.012356 | 0.010924 | -0.001433 | -0.005043 | 0.002177 |
| 5 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | brier | 265 | 53 | 0.268655 | 0.244333 | -0.024322 | -0.077598 | 0.028954 |
| 5 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | crps | 265 | 53 | 0.011151 | 0.010777 | -0.000374 | -0.002583 | 0.001836 |
| 21 | combined | P12_Q_HIST_FALLBACK | P12_Q_PHYSICAL_MIX | brier | 199 | 11 | 0.306217 | 0.307439 | 0.001221 | — | — |
| 21 | combined | P12_Q_HIST_FALLBACK | P12_Q_PHYSICAL_MIX | crps | 199 | 11 | 0.028165 | 0.028819 | 0.000654 | — | — |
| 21 | combined | P12_Q_LOCATION | Q12_RAW | brier | 199 | 11 | 0.286603 | 0.283476 | -0.003127 | — | — |
| 21 | combined | P12_Q_LOCATION | Q12_RAW | crps | 199 | 11 | 0.028866 | 0.026814 | -0.002051 | — | — |
| 21 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | brier | 199 | 11 | 0.307439 | 0.307581 | 0.000143 | — | — |
| 21 | combined | P12_Q_PHYSICAL_MIX | J11_EXCLUDE_B_ROT | crps | 199 | 11 | 0.028819 | 0.029210 | 0.000392 | — | — |
| 21 | combined | P12_Q_SCALE | P12_Q_LOCATION | brier | 199 | 11 | 0.306959 | 0.286603 | -0.020356 | — | — |
| 21 | combined | P12_Q_SCALE | P12_Q_LOCATION | crps | 199 | 11 | 0.029414 | 0.028866 | -0.000548 | — | — |
| 21 | combined | P12_Q_TILT | P12_Q_SCALE | brier | 199 | 11 | 0.310807 | 0.306959 | -0.003847 | — | — |
| 21 | combined | P12_Q_TILT | P12_Q_SCALE | crps | 199 | 11 | 0.028355 | 0.029414 | 0.001059 | — | — |
| 21 | combined | Q12_BLACK_ATM | Q12_RAW | brier | 199 | 11 | 0.260996 | 0.283476 | 0.022479 | — | — |
| 21 | combined | Q12_BLACK_ATM | Q12_RAW | crps | 199 | 11 | 0.025925 | 0.026814 | 0.000890 | — | — |
| 21 | combined | Q12_NATURALLY_ALIGNED | J11_EXCLUDE_B_ROT | brier | 16 | 7 | 0.235106 | 0.276118 | 0.041012 | — | — |
| 21 | combined | Q12_NATURALLY_ALIGNED | J11_EXCLUDE_B_ROT | crps | 16 | 7 | 0.028557 | 0.030544 | 0.001987 | — | — |
| 21 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | brier | 199 | 11 | 0.283476 | 0.307581 | 0.024106 | — | — |
| 21 | combined | Q12_RAW | J11_EXCLUDE_B_ROT | crps | 199 | 11 | 0.026814 | 0.029210 | 0.002396 | — | — |

## Raw priced mass versus realized sign and fixed downside frequency

| horizon | cohort | event | n | priced_mass | statistical_mass | realized_frequency | priced_as_realized_brier | statistical_brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | actual_down5 | 265 | 0.021349 | 0.018002 | 0.003774 | 0.004954 | 0.005326 |
| 5 | combined | actual_sign | 265 | 0.560801 | 0.535208 | 0.441509 | 0.268655 | 0.244333 |
| 21 | combined | actual_down5 | 199 | 0.083651 | 0.091996 | 0.135678 | 0.132122 | 0.152517 |
| 21 | combined | actual_sign | 199 | 0.601737 | 0.626498 | 0.432161 | 0.283476 | 0.307581 |

In the full weekly study the priced law assigned 56.08% average positive mass against 44.15% realized positive returns, and its sign Brier was 0.268655 against 0.244333 for V11. Weekly downside below −5% occurred once in 265 observations. On the 199 monthly shape-eligible origins, the −5% downside occurred 13.57% of the time, against 8.37% priced mass and 9.20% statistical mass. The raw pricing diagnostic nevertheless had a lower downside Brier than the V11 statistical law on those dates, 0.132122 versus 0.152517. The monthly observations are overlapping and the priced mass is not a real-world calibration.

The comparison records numerical disagreement in positive mass, location, dispersion, absolute move, skew-sensitive tails and quantiles. Those measures can correlate with realized volatility or magnitude even when directional scores fail to improve. [Matched observed outcomes](expectations-vs-statistics.csv) · [Cross-law gap diagnostics](statistical-and-priced-gap-diagnostics.csv) · [Fixed-threshold and empirical-bucket checks](training-bucket-calibration.csv).
