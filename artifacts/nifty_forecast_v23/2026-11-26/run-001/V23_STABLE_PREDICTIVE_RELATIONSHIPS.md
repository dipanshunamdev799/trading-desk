# V23 Stable predictive relationships

On exactly the same training origins, the ordinary ridge competes with Huber regression, volatility and positioning
environment weights, hierarchical shrinkage toward the earlier half, and an incrementally upweighted worst past
group. Smaller environments receive a regularized fallback. Training transformations and group thresholds use only
complete earlier cases. Volatility, participation, trend, positioning concentration, corporate activity and the
global environment also enter the conditional evaluation as origin-observable states.

V21's monthly aggregate positioning correction gained 0.019699 Brier on the earlier 141 origins against V20 smooth5
and lost 0.022891 on the later 76. The new robustness arms retain earlier/later rows. Ranking their worst cohort is
a separate criterion from optimizing a single average. The delayed and block-permuted controls can retain apparent
skill when too much of the input is shared or when repeatedly assessed periods favor a residual tilt.

| cohort | brier | crps | dates |
| --- | --- | --- | --- |
| early | 0.019699 | 0.001281 | 141 |
| later | -0.022891 | -0.000658 | 76 |

| horizon | scope | model | n | active | brier | crps | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | early | protected_direction | 173 | 173 | 0.240367 | 0.010111 | 0.861272 |
| 5 | early | protected_distribution | 173 | 173 | 0.245529 | 0.010241 | 0.861272 |
| 5 | early | residual_block_permuted | 173 | 133 | 0.251654 | 0.010506 | 0.867052 |
| 5 | early | residual_delayed_5 | 173 | 133 | 0.247998 | 0.010452 | 0.838150 |
| 5 | early | residual_environment_balanced | 173 | 133 | 0.245469 | 0.010366 | 0.849711 |
| 5 | early | residual_hierarchical | 173 | 133 | 0.245977 | 0.010357 | 0.849711 |
| 5 | early | residual_huber | 173 | 133 | 0.248522 | 0.010469 | 0.832370 |
| 5 | early | residual_ordinary_ridge | 173 | 133 | 0.245292 | 0.010360 | 0.849711 |
| 5 | early | residual_worst_environment | 173 | 133 | 0.245045 | 0.010322 | 0.855491 |
| 21 | early | protected_direction | 141 | 141 | 0.199355 | 0.020753 | 0.836879 |
| 21 | early | protected_distribution | 141 | 141 | 0.194994 | 0.020572 | 0.794326 |
| 21 | early | residual_block_permuted | 141 | 85 | 0.206879 | 0.021239 | 0.773050 |
| 21 | early | residual_delayed_5 | 141 | 85 | 0.200388 | 0.021053 | 0.787234 |
| 21 | early | residual_environment_balanced | 141 | 85 | 0.206418 | 0.021344 | 0.780142 |
| 21 | early | residual_hierarchical | 141 | 85 | 0.205608 | 0.021338 | 0.780142 |
| 21 | early | residual_huber | 141 | 85 | 0.200472 | 0.021094 | 0.780142 |
| 21 | early | residual_ordinary_ridge | 141 | 85 | 0.205350 | 0.021311 | 0.780142 |
| 21 | early | residual_worst_environment | 141 | 85 | 0.203838 | 0.021228 | 0.780142 |
| 5 | later | protected_direction | 92 | 92 | 0.182085 | 0.010311 | 0.760870 |
| 5 | later | protected_distribution | 92 | 92 | 0.178166 | 0.009895 | 0.750000 |
| 5 | later | residual_block_permuted | 92 | 92 | 0.180402 | 0.010180 | 0.750000 |
| 5 | later | residual_delayed_5 | 92 | 92 | 0.171219 | 0.009709 | 0.739130 |
| 5 | later | residual_environment_balanced | 92 | 92 | 0.168618 | 0.009751 | 0.760870 |
| 5 | later | residual_hierarchical | 92 | 92 | 0.168472 | 0.009739 | 0.771739 |
| 5 | later | residual_huber | 92 | 92 | 0.171075 | 0.009756 | 0.760870 |
| 5 | later | residual_ordinary_ridge | 92 | 92 | 0.168525 | 0.009754 | 0.760870 |
| 5 | later | residual_worst_environment | 92 | 92 | 0.167424 | 0.009727 | 0.760870 |
| 21 | later | protected_direction | 76 | 76 | 0.268099 | 0.027666 | 0.605263 |
| 21 | later | protected_distribution | 76 | 76 | 0.277296 | 0.028030 | 0.565789 |
| 21 | later | residual_block_permuted | 76 | 76 | 0.265313 | 0.027561 | 0.578947 |
| 21 | later | residual_delayed_5 | 76 | 76 | 0.253246 | 0.026546 | 0.605263 |
| 21 | later | residual_environment_balanced | 76 | 76 | 0.249215 | 0.026851 | 0.631579 |
| 21 | later | residual_hierarchical | 76 | 76 | 0.243857 | 0.026564 | 0.644737 |
| 21 | later | residual_huber | 76 | 76 | 0.258289 | 0.026939 | 0.631579 |
| 21 | later | residual_ordinary_ridge | 76 | 76 | 0.249234 | 0.026843 | 0.631579 |
| 21 | later | residual_worst_environment | 76 | 76 | 0.244581 | 0.026636 | 0.618421 |
| 5 | combined | protected_direction | 265 | 265 | 0.220133 | 0.010180 | 0.826415 |
| 5 | combined | protected_distribution | 265 | 265 | 0.222142 | 0.010121 | 0.822642 |
| 5 | combined | residual_block_permuted | 265 | 225 | 0.226918 | 0.010393 | 0.826415 |
| 5 | combined | residual_delayed_5 | 265 | 225 | 0.221343 | 0.010194 | 0.803774 |
| 5 | combined | residual_environment_balanced | 265 | 225 | 0.218789 | 0.010152 | 0.818868 |
| 5 | combined | residual_hierarchical | 265 | 225 | 0.219070 | 0.010142 | 0.822642 |
| 5 | combined | residual_huber | 265 | 225 | 0.221634 | 0.010221 | 0.807547 |
| 5 | combined | residual_ordinary_ridge | 265 | 225 | 0.218641 | 0.010150 | 0.818868 |
| 5 | combined | residual_worst_environment | 265 | 225 | 0.218097 | 0.010116 | 0.822642 |
| 21 | combined | protected_direction | 217 | 217 | 0.223431 | 0.023174 | 0.755760 |
| 21 | combined | protected_distribution | 217 | 217 | 0.223819 | 0.023184 | 0.714286 |
| 21 | combined | residual_block_permuted | 217 | 161 | 0.227344 | 0.023453 | 0.705069 |
| 21 | combined | residual_delayed_5 | 217 | 161 | 0.218900 | 0.022977 | 0.723502 |
| 21 | combined | residual_environment_balanced | 217 | 161 | 0.221407 | 0.023273 | 0.728111 |
| 21 | combined | residual_hierarchical | 217 | 161 | 0.219004 | 0.023168 | 0.732719 |
| 21 | combined | residual_huber | 217 | 161 | 0.220721 | 0.023141 | 0.728111 |
| 21 | combined | residual_ordinary_ridge | 217 | 161 | 0.220719 | 0.023248 | 0.728111 |
| 21 | combined | residual_worst_environment | 217 | 161 | 0.218108 | 0.023122 | 0.723502 |

| horizon | model | fit cases | weekly term | vol term | position term | earnings term | position iqr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | residual_block_permuted | 225 | -0.006097 | -0.002276 | 0.005663 | -0.002257 | 0.063608 |
| 5 | residual_delayed_5 | 225 | 0.009539 | 0.060801 | -0.086320 | 0.029722 | 0.120604 |
| 5 | residual_environment_balanced | 225 | 0.008775 | 0.060024 | -0.086889 | 0.028912 | 0.121651 |
| 5 | residual_hierarchical | 225 | 0.008333 | 0.068874 | -0.094649 | 0.035748 | 0.141435 |
| 5 | residual_huber | 225 | 0.006129 | 0.061703 | -0.070739 | 0.016685 | 0.129710 |
| 5 | residual_ordinary_ridge | 225 | 0.009539 | 0.060801 | -0.086320 | 0.029722 | 0.120604 |
| 5 | residual_worst_environment | 225 | 0.011472 | 0.065418 | -0.086196 | 0.028267 | 0.115118 |
| 21 | residual_block_permuted | 161 | -0.010164 | 0.013401 | 0.002891 | 0.009211 | 0.163189 |
| 21 | residual_delayed_5 | 161 | -0.025294 | -0.007578 | -0.327439 | -0.019206 | 0.159029 |
| 21 | residual_environment_balanced | 161 | -0.019454 | -0.008567 | -0.340356 | -0.014536 | 0.167406 |
| 21 | residual_hierarchical | 161 | -0.030295 | -0.020711 | -0.350268 | -0.037099 | 0.185853 |
| 21 | residual_huber | 161 | -0.034933 | 0.004222 | -0.234960 | -0.038797 | 0.141521 |
| 21 | residual_ordinary_ridge | 161 | -0.025294 | -0.007578 | -0.327439 | -0.019206 | 0.159029 |
| 21 | residual_worst_environment | 161 | -0.028854 | -0.002690 | -0.328873 | -0.038093 | 0.145678 |

[return-residual-coefficient-history.csv.gz](return-residual-coefficient-history.csv.gz) · [training-period-stability-receipts.csv.gz](training-period-stability-receipts.csv.gz) · [conditional-calibration.csv.gz](conditional-calibration.csv.gz) · [leave-episodes-out.csv.gz](leave-episodes-out.csv.gz) · [forecast-pareto-frontier.csv](forecast-pareto-frontier.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
