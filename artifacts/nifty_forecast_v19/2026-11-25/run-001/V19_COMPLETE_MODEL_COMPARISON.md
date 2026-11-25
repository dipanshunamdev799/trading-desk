# V19 Complete Model Comparison

The combined population contains 265 original weekly and 217 original monthly outcomes across 53 and 11 disjoint windows. All leaderboard rows retain original forecast clocks and include earlier and later results. The linked machine tables contain every available metric, including error, coverage, width, variance QLIKE, rank correlation and probability calibration. The comparison table lists like-for-like reference scores and origin counts. Lower proper loss marks the top point estimate within a table.

## Weekly and monthly directions at 08:55

| horizon | cutoff | model | n | disjoint | brier | log loss | accuracy | balanced accuracy | crps | abs error | rmse | covered | width | rank corr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | V18_nonprice_same_clock | 265 | 53 | 0.232338 | 0.654878 | 0.581132 | 0.590985 | 0.010352 | 0.014154 | 0.019973 | 0.769811 | 0.041058 | 0.349311 |
| 5 | preauction_0855 | component_plus_residual | 265 | 53 | 0.238003 | 0.668084 | 0.577358 | 0.575970 | 0.010309 | 0.014062 | 0.019532 | 0.758491 | 0.041019 | 0.290602 |
| 5 | preauction_0855 | clock_structural | 265 | 53 | 0.238274 | 0.668337 | 0.569811 | 0.571004 | 0.010658 | 0.014594 | 0.020380 | 0.766038 | 0.041040 | 0.205777 |
| 5 | preauction_0855 | participant | 265 | 53 | 0.239255 | 0.672214 | 0.573585 | 0.597655 | 0.010619 | 0.014478 | 0.020093 | 0.735849 | 0.041111 | 0.354567 |
| 5 | preauction_0855 | structural_position_mixture | 265 | 53 | 0.240213 | 0.672372 | 0.562264 | 0.572303 | 0.010622 | 0.014570 | 0.020271 | 0.762264 | 0.041225 | 0.260785 |
| 21 | preauction_0855 | neutral | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025543 | 0.033371 | 0.044875 | 0.691244 | 0.078299 | 0.141568 |
| 21 | preauction_0855 | V18_nonprice_same_clock | 217 | 11 | 0.281552 | 0.837379 | 0.562212 | 0.544262 | 0.028746 | 0.036599 | 0.052623 | 0.649770 | 0.089372 | 0.050214 |
| 21 | preauction_0855 | participant | 217 | 11 | 0.285350 | 0.820461 | 0.552995 | 0.559362 | 0.027800 | 0.035749 | 0.050222 | 0.654378 | 0.089951 | 0.079265 |
| 21 | preauction_0855 | delivery + participant | 217 | 11 | 0.287643 | 0.832486 | 0.566820 | 0.572821 | 0.027917 | 0.035879 | 0.050375 | 0.649770 | 0.089912 | 0.087140 |
| 21 | preauction_0855 | participant + transactions | 217 | 11 | 0.287704 | 0.826740 | 0.539171 | 0.544737 | 0.027955 | 0.035951 | 0.050440 | 0.649770 | 0.089940 | 0.067209 |

## Weekly and monthly endpoint distributions at 08:55

| horizon | cutoff | model | n | disjoint | brier | log loss | accuracy | balanced accuracy | crps | abs error | rmse | covered | width | rank corr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | decomposition_position | 265 | 53 | 0.240270 | 0.671979 | 0.558491 | 0.570715 | 0.010264 | 0.014138 | 0.019204 | 0.739623 | 0.041085 | 0.352199 |
| 5 | preauction_0855 | component_plus_residual | 265 | 53 | 0.238003 | 0.668084 | 0.577358 | 0.575970 | 0.010309 | 0.014062 | 0.019532 | 0.758491 | 0.041019 | 0.290602 |
| 5 | preauction_0855 | V18_nonprice_same_clock | 265 | 53 | 0.232338 | 0.654878 | 0.581132 | 0.590985 | 0.010352 | 0.014154 | 0.019973 | 0.769811 | 0.041058 | 0.349311 |
| 5 | preauction_0855 | participant | 265 | 53 | 0.239255 | 0.672214 | 0.573585 | 0.597655 | 0.010619 | 0.014478 | 0.020093 | 0.735849 | 0.041111 | 0.354567 |
| 5 | preauction_0855 | structural_position_mixture | 265 | 53 | 0.240213 | 0.672372 | 0.562264 | 0.572303 | 0.010622 | 0.014570 | 0.020271 | 0.762264 | 0.041225 | 0.260785 |
| 21 | preauction_0855 | neutral | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025543 | 0.033371 | 0.044875 | 0.691244 | 0.078299 | 0.141568 |
| 21 | preauction_0855 | historical | 217 | 11 | 0.294519 | 0.785955 | 0.313364 | 0.332269 | 0.026743 | 0.035796 | 0.047257 | 0.682028 | 0.090738 | -0.423964 |
| 21 | preauction_0855 | participant | 217 | 11 | 0.285350 | 0.820461 | 0.552995 | 0.559362 | 0.027800 | 0.035749 | 0.050222 | 0.654378 | 0.089951 | 0.079265 |
| 21 | preauction_0855 | participant_delay1 | 217 | 11 | 0.290813 | 0.833988 | 0.552995 | 0.555867 | 0.027905 | 0.035947 | 0.050343 | 0.654378 | 0.089936 | 0.069855 |
| 21 | preauction_0855 | delivery + participant | 217 | 11 | 0.287643 | 0.832486 | 0.566820 | 0.572821 | 0.027917 | 0.035879 | 0.050375 | 0.649770 | 0.089912 | 0.087140 |

## Native weighted laws

| horizon | cutoff | model | n | disjoint | brier | log loss | accuracy | balanced accuracy | crps | abs error | rmse | covered | width | rank corr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_v14_guard | V14_event_overlay | 265 | 53 | 0.223481 | 0.637789 | 0.641509 | 0.636983 | 0.010318 | 0.014567 | 0.020797 | 0.818868 | 0.045700 | 0.343147 |
| 5 | native_v14_guard | V14_exact | 265 | 53 | 0.228529 | 0.648943 | 0.626415 | 0.636001 | 0.010457 | 0.014842 | 0.020794 | 0.826415 | 0.045780 | 0.349532 |
| 5 | native_v14_guard | V14_plus_positions | 265 | 53 | 0.234786 | 0.662234 | 0.581132 | 0.585614 | 0.010547 | 0.015082 | 0.020951 | 0.818868 | 0.045758 | 0.308728 |
| 5 | native_v14_guard | V18_plus_positions | 265 | 53 | 0.232431 | 0.658622 | 0.607547 | 0.611053 | 0.010467 | 0.014810 | 0.020842 | 0.781132 | 0.045724 | 0.322425 |
| 21 | native_v14_guard | V14_event_overlay | 217 | 11 | 0.259808 | 0.713467 | 0.456221 | 0.436022 | 0.025409 | 0.033504 | 0.046743 | 0.677419 | 0.071355 | -0.072469 |
| 21 | native_v14_guard | V14_exact | 217 | 11 | 0.245042 | 0.683095 | 0.511521 | 0.502675 | 0.024989 | 0.033042 | 0.045216 | 0.668203 | 0.071794 | -0.032590 |
| 21 | native_v14_guard | V14_plus_positions | 217 | 11 | 0.228199 | 0.647076 | 0.543779 | 0.568637 | 0.024010 | 0.031248 | 0.044030 | 0.672811 | 0.071921 | 0.327353 |
| 21 | native_v14_guard | V18_plus_positions | 217 | 11 | 0.234879 | 0.655320 | 0.506912 | 0.506730 | 0.024537 | 0.032048 | 0.045197 | 0.682028 | 0.071548 | 0.117491 |

## Incremental participant, delivery, transaction and interaction scores

| horizon | model | parent | metric | n | gain |
| --- | --- | --- | --- | --- | --- |
| 5 | corporate_position_interactions | V18_corporate_same_clock | brier | 264 | 0.001488 |
| 5 | corporate_position_interactions | V18_corporate_same_clock | crps | 264 | 0.000091 |
| 5 | delivery | clock_structural | brier | 264 | -0.004155 |
| 5 | delivery | clock_structural | crps | 264 | -0.000168 |
| 5 | delivery | V18_corporate_same_clock | brier | 264 | 0.005764 |
| 5 | delivery | V18_corporate_same_clock | crps | 264 | 0.000278 |
| 5 | participant | clock_structural | brier | 265 | -0.000981 |
| 5 | participant | clock_structural | crps | 265 | 0.000040 |
| 5 | participant | V18_corporate_same_clock | brier | 265 | 0.009008 |
| 5 | participant | V18_corporate_same_clock | crps | 265 | 0.000485 |
| 5 | transactions | clock_structural | brier | 265 | -0.009195 |
| 5 | transactions | clock_structural | crps | 265 | -0.000293 |
| 5 | transactions | V18_corporate_same_clock | brier | 265 | 0.000794 |
| 5 | transactions | V18_corporate_same_clock | crps | 265 | 0.000151 |
| 21 | corporate_position_interactions | V18_corporate_same_clock | brier | 216 | 0.015227 |
| 21 | corporate_position_interactions | V18_corporate_same_clock | crps | 216 | 0.000955 |
| 21 | delivery | clock_structural | brier | 216 | -0.033431 |
| 21 | delivery | clock_structural | crps | 216 | -0.002381 |
| 21 | participant | clock_structural | brier | 217 | 0.017455 |
| 21 | participant | clock_structural | crps | 217 | 0.000719 |

## Standalone realized risk and volatility expansion at 08:55

| horizon | model | n | abs error | qlike | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | protected_offshore_plus_domestic | 265 | 0.036469 | 0.290334 | — |
| 5 | fundamental_risk | 265 | 0.036944 | 0.319097 | 0.026395 |
| 5 | combined_positioning_risk | 265 | 0.037158 | 0.307856 | 0.026249 |
| 5 | non_price_risk | 265 | 0.037189 | 0.307498 | 0.026249 |
| 21 | protected_GJR | 217 | 0.033179 | 0.199677 | — |
| 21 | protected_V14_IV_GJR | 217 | 0.033780 | 0.247374 | — |
| 21 | protected_student_EGARCH | 217 | 0.035730 | 0.207684 | — |
| 21 | protected_raw_iv | 217 | 0.039406 | 0.267623 | — |

| horizon | model | n | brier | log loss | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | protected_fixed_iv_rv | 265 | 0.152707 | — | — |
| 5 | fundamental_risk | 265 | 0.154673 | — | 0.026395 |
| 5 | non_price_risk | 265 | 0.154819 | — | 0.026249 |
| 5 | scheduled_then_fundamental | 265 | 0.154844 | — | 0.026683 |
| 21 | protected_student_EGARCH | 217 | 0.172872 | — | — |
| 21 | protected_raw_iv | 217 | 0.186036 | — | — |
| 21 | protected_fixed_iv_rv | 217 | 0.194367 | — | — |
| 21 | protected_GJR | 217 | 0.198788 | — | — |

## Joint future ranges and tails at 08:55

| horizon | model | n | range crps | vol mae | touch brier |
| --- | --- | --- | --- | --- | --- |
| 5 | position_on_IV | 265 | 0.005692 | 0.036111 | 0.144420 |
| 5 | same_clock_IV | 265 | 0.005768 | 0.036801 | 0.144562 |
| 5 | same_clock_GIFT_first | 265 | 0.006209 | 0.038994 | 0.132201 |
| 5 | same_clock_GJR | 265 | 0.006493 | 0.040097 | 0.148396 |
| 21 | same_clock_GJR | 217 | 0.015488 | 0.037244 | 0.183861 |
| 21 | position_on_GJR | 217 | 0.016512 | 0.041073 | 0.186580 |
| 21 | position_on_IV | 217 | 0.017142 | 0.039843 | 0.185053 |
| 21 | same_clock_IV | 217 | 0.017179 | 0.040023 | 0.184372 |

| horizon | model | n | drawdown crps | high crps | low crps | touch brier | integrated brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | same_clock_GIFT_first | 265 | 0.005887 | 0.006424 | 0.006592 | 0.132201 | 0.100551 |
| 5 | position_on_IV | 265 | 0.005987 | 0.006823 | 0.007241 | 0.144420 | 0.120310 |
| 5 | same_clock_IV | 265 | 0.005926 | 0.006913 | 0.007179 | 0.144562 | 0.120331 |
| 5 | same_clock_GJR | 265 | 0.005956 | 0.007256 | 0.007287 | 0.148396 | 0.122458 |
| 21 | same_clock_GJR | 217 | 0.014113 | 0.012364 | 0.017770 | 0.183861 | 0.161061 |
| 21 | same_clock_IV | 217 | 0.015369 | 0.012286 | 0.018725 | 0.184372 | 0.159680 |
| 21 | same_clock_GIFT_first | 217 | 0.016041 | 0.012421 | 0.019549 | 0.184421 | 0.149470 |
| 21 | position_on_IV | 217 | 0.015180 | 0.012213 | 0.018740 | 0.185053 | 0.160413 |

[model-leaderboards.csv](model-leaderboards.csv) · [matched-comparisons.csv](matched-comparisons.csv) · [native-mechanism-summary.csv](native-mechanism-summary.csv) · [probability-calibration.csv](probability-calibration.csv) · [block-bootstrap-intervals.csv.gz](block-bootstrap-intervals.csv.gz) · [barrier-leaderboard.csv](barrier-leaderboard.csv) · [crowding-leaderboard.csv](crowding-leaderboard.csv) · [stock-transfer-leaderboard.csv](stock-transfer-leaderboard.csv) · [sector-transfer-leaderboard.csv](sector-transfer-leaderboard.csv) · [transaction-event-summary.csv](transaction-event-summary.csv) · [protected-native-joint-models.csv](protected-native-joint-models.csv)
