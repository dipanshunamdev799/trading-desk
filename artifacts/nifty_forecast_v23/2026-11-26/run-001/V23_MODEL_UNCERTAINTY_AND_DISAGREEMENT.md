# V23 Model uncertainty and disagreement

The predictive return law measures uncertainty about prices. The total variance of an expert pool is the average
within-expert outcome variance plus the between-expert variance of conditional means. The weight-model probability
band measures instability in estimated sign probability across block and weight draws. Its bounds are a conditional
sensitivity calculation, with no claim to cover full model-specification or source-measurement uncertainty.

The diagnostic forecast asks whether genuinely different families improve warning of larger future absolute errors,
range, expansion, adverse tail events and poor probability or distribution scores. The mature-only benchmark
includes previous volatility, IV, ordinary probability dispersion, estimated parameter instability, the current
directional probability and feature-distribution distance. The challenger adds family disagreement and training
period sensitivity. A five-session delayed disagreement variant tests timeliness.

| horizon | clock | n | families | typical within | typical between | typical parameter se | mean family disagreement | mean plain disagreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | 265 | 6.000000 | 0.000305 | 0.000014 | 0.006314 | 0.094631 | 0.089928 |
| 5 | preauction_0855 | 265 | 9.000000 | 0.000293 | 0.000009 | 0.005103 | 0.090519 | 0.091447 |
| 5 | previous_1700 | 263 | 6.000000 | 0.000267 | 0.000006 | 0.003467 | 0.068673 | 0.071263 |
| 21 | native_0910 | 217 | 7.000000 | 0.001195 | 0.000086 | 0.005837 | 0.119845 | 0.117080 |
| 21 | preauction_0855 | 217 | 9.000000 | 0.001154 | 0.000144 | 0.013595 | 0.152455 | 0.151809 |
| 21 | previous_1700 | 216 | 6.000000 | 0.001047 | 0.000043 | 0.011122 | 0.105723 | 0.103852 |

| horizon | measure | model | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | abs_error | delayed_disagreement | 225 | 0.000155 | 0.000003 | 0.000307 |
| 5 | abs_error | model_disagreement | 225 | 0.000113 | -0.000040 | 0.000267 |
| 5 | direction_brier_error | delayed_disagreement | 225 | -0.003650 | -0.006680 | -0.000619 |
| 5 | direction_brier_error | model_disagreement | 225 | -0.000797 | -0.004362 | 0.002768 |
| 5 | distribution_crps_error | delayed_disagreement | 225 | 0.000029 | -0.000087 | 0.000145 |
| 5 | distribution_crps_error | model_disagreement | 225 | 0.000064 | -0.000014 | 0.000142 |
| 5 | range | delayed_disagreement | 225 | 0.000012 | -0.000315 | 0.000339 |
| 5 | range | model_disagreement | 225 | 0.000066 | -0.000263 | 0.000396 |
| 5 | terminal_tail_miss | delayed_disagreement | 225 | -0.001542 | -0.004748 | 0.001665 |
| 5 | terminal_tail_miss | model_disagreement | 225 | -0.000659 | -0.003307 | 0.001989 |
| 5 | upper_range_tail | delayed_disagreement | 225 | 0.000756 | -0.008995 | 0.010507 |
| 5 | upper_range_tail | model_disagreement | 225 | -0.000018 | -0.006752 | 0.006716 |
| 5 | vol_expansion | delayed_disagreement | 225 | -0.006131 | -0.013467 | 0.001206 |
| 5 | vol_expansion | model_disagreement | 225 | -0.003979 | -0.008508 | 0.000551 |
| 21 | abs_error | delayed_disagreement | 161 | 0.000519 | -0.000464 | 0.001503 |
| 21 | abs_error | model_disagreement | 161 | 0.000254 | -0.000670 | 0.001178 |
| 21 | direction_brier_error | delayed_disagreement | 161 | 0.001246 | -0.004646 | 0.007137 |
| 21 | direction_brier_error | model_disagreement | 161 | 0.003168 | -0.001753 | 0.008089 |
| 21 | distribution_crps_error | delayed_disagreement | 161 | 0.000477 | -0.000786 | 0.001739 |
| 21 | distribution_crps_error | model_disagreement | 161 | 0.000479 | -0.000707 | 0.001666 |
| 21 | range | delayed_disagreement | 161 | -0.000909 | -0.005283 | 0.003466 |
| 21 | range | model_disagreement | 161 | -0.000763 | -0.005483 | 0.003957 |
| 21 | terminal_tail_miss | delayed_disagreement | 161 | -0.006531 | -0.030180 | 0.017117 |
| 21 | terminal_tail_miss | model_disagreement | 161 | -0.006009 | -0.031511 | 0.019494 |
| 21 | upper_range_tail | delayed_disagreement | 161 | 0.011558 | -0.017795 | 0.040911 |
| 21 | upper_range_tail | model_disagreement | 161 | 0.020772 | -0.007441 | 0.048984 |
| 21 | vol_expansion | delayed_disagreement | 161 | -0.013823 | -0.040936 | 0.013290 |
| 21 | vol_expansion | model_disagreement | 161 | -0.004096 | -0.031480 | 0.023287 |

## Re-estimated coefficients and source perturbations

A separate 64-draw block refit varies the historical regression coefficients. Changing the active memory from 120 to 60 cases and perturbing observed standardized inputs by 0.20 units measure two further sensitivities. The source perturbation is a scenario and preserves the missing-data mask. The return standard deviation and interval width still come from the complete market law.

| horizon | clock | n | probability estimation sd | weight uncertainty sd | feature stress probability sd | training span sensitivity | family disagreement | future return sd | market interval width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | 225 | 0.038080 | 0.006314 | 0.008526 | 0.026614 | 0.092953 | 0.018019 | 0.045429 |
| 5 | preauction_0855 | 225 | 0.045615 | 0.005103 | 0.009962 | 0.031250 | 0.086524 | 0.017242 | 0.041939 |
| 21 | native_0910 | 161 | 0.049941 | 0.005837 | 0.011122 | 0.042969 | 0.114246 | 0.033545 | 0.068017 |
| 21 | preauction_0855 | 161 | 0.055051 | 0.013595 | 0.012767 | 0.050781 | 0.168791 | 0.032535 | 0.081176 |

| horizon | clock | model | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | IV_RV_and_weight_variation | 185 | 0.000000 | 0.000000 | 0.000000 |
| 5 | native_0910 | plus_family_and_measurement | 185 | -0.000089 | -0.000188 | 0.000011 |
| 5 | native_0910 | plus_fit_parameter_variation | 185 | -0.000004 | -0.000059 | 0.000051 |
| 5 | preauction_0855 | IV_RV_and_weight_variation | 185 | 0.000000 | 0.000000 | 0.000000 |
| 5 | preauction_0855 | plus_family_and_measurement | 185 | -0.000069 | -0.000138 | 0.000001 |
| 5 | preauction_0855 | plus_fit_parameter_variation | 185 | -0.000043 | -0.000123 | 0.000037 |
| 21 | native_0910 | IV_RV_and_weight_variation | 105 | 0.000000 | 0.000000 | 0.000000 |
| 21 | native_0910 | plus_family_and_measurement | 105 | -0.000996 | -0.002610 | 0.000618 |
| 21 | native_0910 | plus_fit_parameter_variation | 105 | 0.000126 | -0.000021 | 0.000272 |
| 21 | preauction_0855 | IV_RV_and_weight_variation | 105 | 0.000000 | 0.000000 | 0.000000 |
| 21 | preauction_0855 | plus_family_and_measurement | 105 | -0.000478 | -0.002005 | 0.001049 |
| 21 | preauction_0855 | plus_fit_parameter_variation | 105 | 0.000381 | -0.000109 | 0.000872 |

Directional overconfidence and tail misses are evaluated as separate target or calibration outcomes. The adjusted paired evidence does not support disagreement as a dependable volatility-expansion warning at the native clock.

[model-uncertainty-cases.csv.gz](model-uncertainty-cases.csv.gz) · [disagreement-future-risk-cases.csv.gz](disagreement-future-risk-cases.csv.gz) · [disagreement-future-risk-leaderboard.csv](disagreement-future-risk-leaderboard.csv) · [conditional-calibration.csv.gz](conditional-calibration.csv.gz) · [training-period-stability-receipts.csv.gz](training-period-stability-receipts.csv.gz) · [simulation-precision-summary.csv](simulation-precision-summary.csv) · [parameter-and-source-uncertainty-cases.csv.gz](parameter-and-source-uncertainty-cases.csv.gz)

[Back to the research index](NIFTY_V23_RESEARCH.md)
