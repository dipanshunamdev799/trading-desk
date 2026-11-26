# V23 Original horizon forecasting

Every law predicts next-five-session or next-21-session NIFTY cash-close return from the original prior close. The original
173/92 and 141/76 splits are reproduced at the native and pre-auction clocks. The previous evening study separately
omits the few origins for which the cash reference was not yet available under the declared guard. Original clocks remain
distinct in all leaderboards. A candidate's sign, mean, median, expected index, quantiles and tail probabilities are
computed directly from the same weights.

The 09:10 weekly worst-environment residual scored 0.218097 Brier versus 0.220133 for V22's protected direction
leader. The corporate location-only experiment scored 0.010090 CRPS versus 0.010121 for the protected distribution.
The 09:10 monthly shape substitution reduced Brier to 0.210496 from 0.223431, improved Brier in both original cohorts,
and reached 0.022911 CRPS against 0.023174. In the later monthly cohort its CRPS rose slightly against that reference.
The main Brier improvement comes from the new shape's implied sign mass. Full and matched active rows account for
train-only warm-up fallbacks in the residual and calibration models.

| horizon | scope | model | n | active | disjoint | brier | crps | log loss | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | agg_loss_robust | 265 | 225 | 53 | 0.231773 | 0.010318 | 0.656106 | 0.826415 |
| 5 | combined | complementary_residual_component | 265 | 225 | 53 | 0.220580 | 0.010148 | 0.632334 | 0.852830 |
| 5 | combined | component_coherent_joint | 265 | 265 | 53 | 0.221733 | 0.010181 | 0.634877 | 0.856604 |
| 5 | combined | component_historical_shape_only | 265 | 265 | 53 | 0.226389 | 0.010250 | 0.645268 | 0.811321 |
| 5 | combined | component_location_only | 265 | 265 | 53 | 0.220248 | 0.010090 | 0.631442 | 0.830189 |
| 5 | combined | fixed_20pct_history | 265 | 265 | 53 | 0.224221 | 0.010112 | 0.640200 | 0.822642 |
| 5 | combined | fixed_20pct_neutral | 265 | 265 | 53 | 0.223891 | 0.010093 | 0.639382 | 0.826415 |
| 5 | combined | protected_direction | 265 | 265 | 53 | 0.220133 | 0.010180 | 0.630806 | 0.826415 |
| 5 | combined | protected_distribution | 265 | 265 | 53 | 0.222142 | 0.010121 | 0.635180 | 0.822642 |
| 5 | combined | residual_delayed_5 | 265 | 225 | 53 | 0.221343 | 0.010194 | 0.634603 | 0.803774 |
| 5 | combined | residual_ordinary_ridge | 265 | 225 | 53 | 0.218641 | 0.010150 | 0.628151 | 0.818868 |
| 5 | combined | residual_worst_environment | 265 | 225 | 53 | 0.218097 | 0.010116 | 0.626754 | 0.822642 |
| 5 | combined | uncertainty_guarded_mixture | 265 | 225 | 53 | 0.223552 | 0.010135 | 0.638498 | 0.833962 |
| 21 | combined | agg_loss_robust | 217 | 161 | 11 | 0.248899 | 0.024649 | 0.693458 | 0.718894 |
| 21 | combined | complementary_residual_component | 217 | 161 | 11 | 0.221205 | 0.023010 | 0.635743 | 0.760369 |
| 21 | combined | component_coherent_joint | 217 | 217 | 11 | 0.225508 | 0.023243 | 0.644452 | 0.778802 |
| 21 | combined | component_historical_shape_only | 217 | 217 | 11 | 0.210496 | 0.022911 | 0.605351 | 0.705069 |
| 21 | combined | component_location_only | 217 | 217 | 11 | 0.223058 | 0.023277 | 0.640526 | 0.700461 |
| 21 | combined | fixed_20pct_history | 217 | 217 | 11 | 0.230132 | 0.023484 | 0.654356 | 0.723502 |
| 21 | combined | fixed_20pct_neutral | 217 | 217 | 11 | 0.222577 | 0.023298 | 0.638591 | 0.714286 |
| 21 | combined | protected_direction | 217 | 217 | 11 | 0.223431 | 0.023174 | 0.642855 | 0.755760 |
| 21 | combined | protected_distribution | 217 | 217 | 11 | 0.223819 | 0.023184 | 0.646636 | 0.714286 |
| 21 | combined | residual_delayed_5 | 217 | 161 | 11 | 0.218900 | 0.022977 | 0.628996 | 0.723502 |
| 21 | combined | residual_ordinary_ridge | 217 | 161 | 11 | 0.220719 | 0.023248 | 0.631886 | 0.728111 |
| 21 | combined | residual_worst_environment | 217 | 161 | 11 | 0.218108 | 0.023122 | 0.624068 | 0.723502 |
| 21 | combined | uncertainty_guarded_mixture | 217 | 161 | 11 | 0.224475 | 0.023326 | 0.644135 | 0.728111 |
| 5 | early | agg_loss_robust | 173 | 133 | 35 | 0.245210 | 0.010085 | 0.683369 | 0.867052 |
| 5 | early | complementary_residual_component | 173 | 133 | 35 | 0.242558 | 0.010260 | 0.678433 | 0.884393 |
| 5 | early | component_coherent_joint | 173 | 173 | 35 | 0.241083 | 0.010220 | 0.675016 | 0.890173 |
| 5 | early | component_historical_shape_only | 173 | 173 | 35 | 0.255913 | 0.010581 | 0.710021 | 0.843931 |
| 5 | early | component_location_only | 173 | 173 | 35 | 0.241248 | 0.010074 | 0.675287 | 0.861272 |
| 5 | early | fixed_20pct_history | 173 | 173 | 35 | 0.244775 | 0.010133 | 0.682631 | 0.849711 |
| 5 | early | fixed_20pct_neutral | 173 | 173 | 35 | 0.242639 | 0.010062 | 0.678040 | 0.855491 |
| 5 | early | protected_direction | 173 | 173 | 35 | 0.240367 | 0.010111 | 0.673723 | 0.861272 |
| 5 | early | protected_distribution | 173 | 173 | 35 | 0.245529 | 0.010241 | 0.684273 | 0.861272 |
| 5 | early | residual_delayed_5 | 173 | 133 | 35 | 0.247998 | 0.010452 | 0.692481 | 0.838150 |
| 5 | early | residual_ordinary_ridge | 173 | 133 | 35 | 0.245292 | 0.010360 | 0.685519 | 0.849711 |
| 5 | early | residual_worst_environment | 173 | 133 | 35 | 0.245045 | 0.010322 | 0.684750 | 0.855491 |
| 5 | early | uncertainty_guarded_mixture | 173 | 133 | 35 | 0.243583 | 0.010177 | 0.679921 | 0.867052 |
| 21 | early | agg_loss_robust | 141 | 85 | 7 | 0.239018 | 0.022937 | 0.669273 | 0.794326 |
| 21 | early | complementary_residual_component | 141 | 85 | 7 | 0.202695 | 0.020933 | 0.592435 | 0.815603 |
| 21 | early | component_coherent_joint | 141 | 141 | 7 | 0.208114 | 0.021136 | 0.605562 | 0.843972 |
| 21 | early | component_historical_shape_only | 141 | 141 | 7 | 0.189948 | 0.020224 | 0.562529 | 0.744681 |
| 21 | early | component_location_only | 141 | 141 | 7 | 0.200165 | 0.020992 | 0.586842 | 0.780142 |
| 21 | early | fixed_20pct_history | 141 | 141 | 7 | 0.212186 | 0.021469 | 0.612357 | 0.780142 |
| 21 | early | fixed_20pct_neutral | 141 | 141 | 7 | 0.202611 | 0.021187 | 0.593224 | 0.773050 |
| 21 | early | protected_direction | 141 | 141 | 7 | 0.199355 | 0.020753 | 0.585237 | 0.836879 |
| 21 | early | protected_distribution | 141 | 141 | 7 | 0.194994 | 0.020572 | 0.573756 | 0.794326 |
| 21 | early | residual_delayed_5 | 141 | 85 | 7 | 0.200388 | 0.021053 | 0.582910 | 0.787234 |
| 21 | early | residual_ordinary_ridge | 141 | 85 | 7 | 0.205350 | 0.021311 | 0.592118 | 0.780142 |
| 21 | early | residual_worst_environment | 141 | 85 | 7 | 0.203838 | 0.021228 | 0.588882 | 0.780142 |
| 21 | early | uncertainty_guarded_mixture | 141 | 85 | 7 | 0.201647 | 0.021017 | 0.590629 | 0.801418 |
| 5 | later | agg_loss_robust | 92 | 92 | 19 | 0.206505 | 0.010756 | 0.604841 | 0.750000 |
| 5 | later | complementary_residual_component | 92 | 92 | 19 | 0.179253 | 0.009937 | 0.545648 | 0.793478 |
| 5 | later | component_coherent_joint | 92 | 92 | 19 | 0.185345 | 0.010108 | 0.559398 | 0.793478 |
| 5 | later | component_historical_shape_only | 92 | 92 | 19 | 0.170873 | 0.009626 | 0.523505 | 0.750000 |
| 5 | later | component_location_only | 92 | 92 | 19 | 0.180760 | 0.010120 | 0.548993 | 0.771739 |
| 5 | later | fixed_20pct_history | 92 | 92 | 19 | 0.185570 | 0.010072 | 0.560412 | 0.771739 |
| 5 | later | fixed_20pct_neutral | 92 | 92 | 19 | 0.188637 | 0.010150 | 0.566690 | 0.771739 |
| 5 | later | protected_direction | 92 | 92 | 19 | 0.182085 | 0.010311 | 0.550103 | 0.760870 |
| 5 | later | protected_distribution | 92 | 92 | 19 | 0.178166 | 0.009895 | 0.542865 | 0.750000 |
| 5 | later | residual_delayed_5 | 92 | 92 | 19 | 0.171219 | 0.009709 | 0.525768 | 0.739130 |
| 5 | later | residual_ordinary_ridge | 92 | 92 | 19 | 0.168525 | 0.009754 | 0.520273 | 0.760870 |
| 5 | later | residual_worst_environment | 92 | 92 | 19 | 0.167424 | 0.009727 | 0.517698 | 0.760870 |
| 5 | later | uncertainty_guarded_mixture | 92 | 92 | 19 | 0.185885 | 0.010057 | 0.560606 | 0.771739 |
| 21 | later | agg_loss_robust | 76 | 76 | 4 | 0.267233 | 0.027826 | 0.738329 | 0.578947 |
| 21 | later | complementary_residual_component | 76 | 76 | 4 | 0.255546 | 0.026865 | 0.716093 | 0.657895 |
| 21 | later | component_coherent_joint | 76 | 76 | 4 | 0.257778 | 0.027153 | 0.716604 | 0.657895 |
| 21 | later | component_historical_shape_only | 76 | 76 | 4 | 0.248618 | 0.027895 | 0.684798 | 0.631579 |
| 21 | later | component_location_only | 76 | 76 | 4 | 0.265529 | 0.027515 | 0.740124 | 0.552632 |
| 21 | later | fixed_20pct_history | 76 | 76 | 4 | 0.263426 | 0.027221 | 0.732275 | 0.618421 |
| 21 | later | fixed_20pct_neutral | 76 | 76 | 4 | 0.259620 | 0.027215 | 0.722760 | 0.605263 |
| 21 | later | protected_direction | 76 | 76 | 4 | 0.268099 | 0.027666 | 0.749750 | 0.605263 |
| 21 | later | protected_distribution | 76 | 76 | 4 | 0.277296 | 0.028030 | 0.781847 | 0.565789 |
| 21 | later | residual_delayed_5 | 76 | 76 | 4 | 0.253246 | 0.026546 | 0.714498 | 0.605263 |
| 21 | later | residual_ordinary_ridge | 76 | 76 | 4 | 0.249234 | 0.026843 | 0.705665 | 0.631579 |
| 21 | later | residual_worst_environment | 76 | 76 | 4 | 0.244581 | 0.026636 | 0.689348 | 0.618421 |
| 21 | later | uncertainty_guarded_mixture | 76 | 76 | 4 | 0.266826 | 0.027611 | 0.743402 | 0.592105 |

| horizon | parent | model | metric | block | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | protected_direction | component_historical_shape_only | brier | 21 | 265 | -0.006256 | -0.026175 | 0.013662 |
| 5 | protected_direction | component_location_only | brier | 21 | 265 | -0.000115 | -0.012601 | 0.012370 |
| 5 | protected_direction | residual_worst_environment | brier | 21 | 265 | 0.002036 | -0.013620 | 0.017691 |
| 5 | protected_direction | component_historical_shape_only | brier | 42 | 265 | -0.006256 | -0.023127 | 0.010615 |
| 5 | protected_direction | component_location_only | brier | 42 | 265 | -0.000115 | -0.009720 | 0.009489 |
| 5 | protected_direction | residual_worst_environment | brier | 42 | 265 | 0.002036 | -0.010498 | 0.014569 |
| 5 | protected_direction | component_historical_shape_only | crps | 21 | 265 | -0.000069 | -0.000778 | 0.000640 |
| 5 | protected_direction | component_location_only | crps | 21 | 265 | 0.000090 | -0.000353 | 0.000533 |
| 5 | protected_direction | residual_worst_environment | crps | 21 | 265 | 0.000065 | -0.000690 | 0.000819 |
| 5 | protected_direction | component_historical_shape_only | crps | 42 | 265 | -0.000069 | -0.000779 | 0.000640 |
| 5 | protected_direction | component_location_only | crps | 42 | 265 | 0.000090 | -0.000293 | 0.000474 |
| 5 | protected_direction | residual_worst_environment | crps | 42 | 265 | 0.000065 | -0.000597 | 0.000726 |
| 5 | protected_distribution | component_historical_shape_only | brier | 21 | 265 | -0.004247 | -0.018901 | 0.010407 |
| 5 | protected_distribution | component_location_only | brier | 21 | 265 | 0.001894 | -0.005946 | 0.009734 |
| 5 | protected_distribution | residual_worst_environment | brier | 21 | 265 | 0.004045 | -0.007496 | 0.015587 |
| 5 | protected_distribution | component_historical_shape_only | brier | 42 | 265 | -0.004247 | -0.018913 | 0.010419 |
| 5 | protected_distribution | component_location_only | brier | 42 | 265 | 0.001894 | -0.006443 | 0.010231 |
| 5 | protected_distribution | residual_worst_environment | brier | 42 | 265 | 0.004045 | -0.006438 | 0.014528 |
| 5 | protected_distribution | component_historical_shape_only | crps | 21 | 265 | -0.000129 | -0.000425 | 0.000167 |
| 5 | protected_distribution | component_location_only | crps | 21 | 265 | 0.000031 | -0.000345 | 0.000406 |
| 5 | protected_distribution | residual_worst_environment | crps | 21 | 265 | 0.000005 | -0.000590 | 0.000600 |
| 5 | protected_distribution | component_historical_shape_only | crps | 42 | 265 | -0.000129 | -0.000476 | 0.000218 |
| 5 | protected_distribution | component_location_only | crps | 42 | 265 | 0.000031 | -0.000364 | 0.000425 |
| 5 | protected_distribution | residual_worst_environment | crps | 42 | 265 | 0.000005 | -0.000439 | 0.000450 |
| 21 | protected_direction | component_historical_shape_only | brier | 21 | 217 | 0.012935 | 0.000407 | 0.025464 |
| 21 | protected_direction | component_location_only | brier | 21 | 217 | 0.000374 | -0.006926 | 0.007673 |
| 21 | protected_direction | residual_worst_environment | brier | 21 | 217 | 0.005324 | -0.036793 | 0.047440 |
| 21 | protected_direction | component_historical_shape_only | brier | 42 | 217 | 0.012935 | 0.001619 | 0.024251 |
| 21 | protected_direction | component_location_only | brier | 42 | 217 | 0.000374 | -0.005833 | 0.006580 |
| 21 | protected_direction | residual_worst_environment | brier | 42 | 217 | 0.005324 | -0.033368 | 0.044016 |
| 21 | protected_direction | component_historical_shape_only | crps | 21 | 217 | 0.000263 | -0.001516 | 0.002042 |
| 21 | protected_direction | component_location_only | crps | 21 | 217 | -0.000103 | -0.001214 | 0.001009 |
| 21 | protected_direction | residual_worst_environment | crps | 21 | 217 | 0.000052 | -0.002475 | 0.002579 |
| 21 | protected_direction | component_historical_shape_only | crps | 42 | 217 | 0.000263 | -0.001264 | 0.001790 |
| 21 | protected_direction | component_location_only | crps | 42 | 217 | -0.000103 | -0.001094 | 0.000888 |
| 21 | protected_direction | residual_worst_environment | crps | 42 | 217 | 0.000052 | -0.002430 | 0.002534 |
| 21 | protected_distribution | component_historical_shape_only | brier | 21 | 217 | 0.013323 | -0.010405 | 0.037051 |
| 21 | protected_distribution | component_location_only | brier | 21 | 217 | 0.000761 | -0.016537 | 0.018059 |
| 21 | protected_distribution | residual_worst_environment | brier | 21 | 217 | 0.005711 | -0.039787 | 0.051209 |
| 21 | protected_distribution | component_historical_shape_only | brier | 42 | 217 | 0.013323 | -0.008770 | 0.035416 |
| 21 | protected_distribution | component_location_only | brier | 42 | 217 | 0.000761 | -0.015444 | 0.016966 |
| 21 | protected_distribution | residual_worst_environment | brier | 42 | 217 | 0.005711 | -0.036601 | 0.048023 |
| 21 | protected_distribution | component_historical_shape_only | crps | 21 | 217 | 0.000273 | -0.001490 | 0.002037 |
| 21 | protected_distribution | component_location_only | crps | 21 | 217 | -0.000093 | -0.001081 | 0.000896 |
| 21 | protected_distribution | residual_worst_environment | crps | 21 | 217 | 0.000062 | -0.002242 | 0.002366 |
| 21 | protected_distribution | component_historical_shape_only | crps | 42 | 217 | 0.000273 | -0.000962 | 0.001509 |
| 21 | protected_distribution | component_location_only | crps | 42 | 217 | -0.000093 | -0.000863 | 0.000678 |
| 21 | protected_distribution | residual_worst_environment | crps | 42 | 217 | 0.000062 | -0.002097 | 0.002221 |

[v23-return-cases.csv.gz](v23-return-cases.csv.gz) · [v23-return-laws.npz](v23-return-laws.npz) · [original-horizon-matched-comparisons.csv.gz](original-horizon-matched-comparisons.csv.gz) · [forecast-pareto-frontier.csv](forecast-pareto-frontier.csv) · [domestic-shape-attribution-leaderboard.csv](domestic-shape-attribution-leaderboard.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
