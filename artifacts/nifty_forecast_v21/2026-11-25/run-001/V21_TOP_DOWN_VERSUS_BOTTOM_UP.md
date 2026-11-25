# V21 Top Down Versus Bottom Up

A common case book scores the original five- and 21-session cohorts at both historical cutoffs. At 08:55 the rebuilt weekly V17 law and archived neutral/GJR monthly laws remain the available benchmarks. At 09:10 the strongest V20 forecast for each metric is kept as an exact weighted reference. V21’s stand-alone candidates use only the earlier pre-auction data when carried into the 09:10 comparison. Hybrid candidates apply a bias, location, scale, asymmetry, market-wide positioning or weighted corporate reaction correction to the exact existing NIFTY law, using only earlier matured errors. The fixed distribution mixture assigns **25%** to the entire bottom-up stock law. Separate stock, sector and common-factor candidates forecast independently of the archived anchor.

| horizon | metric | candidate | new | reference | prior | difference |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | omit_latest_21_training_origins | 0.221693 | omit_latest_21_training_origins | 0.221693 | 0.000000 |
| 5 | crps | anchor_asymmetry | 0.010167 | price_reaction | 0.010258 | 0.000091 |
| 21 | brier | anchor_aggregate_position | 0.223819 | eight_calendar_day_embargo | 0.228088 | 0.004269 |
| 21 | crps | anchor_aggregate_position | 0.023184 | smooth5 | 0.023786 | 0.000602 |

| horizon | cutoff | model | n | active | brier | crps | log loss | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | anchor_aggregate_position | 265 | 216 | 0.224123 | 0.010344 | 0.637852 | 0.818868 | 0.045719 |
| 5 | native_0910 | anchor_asymmetry | 265 | 216 | 0.222129 | 0.010167 | 0.635730 | 0.822642 | 0.045819 |
| 5 | native_0910 | anchor_bias | 265 | 216 | 0.224355 | 0.010272 | 0.641204 | 0.822642 | 0.045719 |
| 5 | native_0910 | anchor_corporate_proxy | 265 | 216 | 0.225091 | 0.010333 | 0.642488 | 0.811321 | 0.045719 |
| 5 | native_0910 | anchor_fixed_joint_mixture | 265 | 265 | 0.229273 | 0.010327 | 0.650894 | 0.841509 | 0.046157 |
| 5 | native_0910 | anchor_location | 265 | 216 | 0.227322 | 0.010288 | 0.646216 | 0.815094 | 0.045719 |
| 5 | native_0910 | anchor_scale | 265 | 216 | 0.224178 | 0.010319 | 0.640471 | 0.822642 | 0.046800 |
| 5 | native_0910 | date_only_ridge | 265 | 265 | 0.249081 | 0.011179 | 0.693428 | 0.747170 | 0.040845 |
| 5 | native_0910 | omit_latest_21_training_origins | 265 | 202 | 0.221693 | 0.010274 | 0.634612 | 0.826415 | 0.045711 |
| 5 | native_0910 | pooled_market_factor | 265 | 265 | 0.255866 | 0.011465 | 0.706151 | 0.739623 | 0.040780 |
| 5 | native_0910 | price_reaction | 265 | 223 | 0.223384 | 0.010258 | 0.638699 | 0.830189 | 0.045719 |
| 5 | native_0910 | sector_direct_joint | 265 | 265 | 0.256047 | 0.011348 | 0.715718 | 0.754717 | 0.040803 |
| 5 | native_0910 | stock_gaussian_shrink | 265 | 265 | 0.267394 | 0.011627 | 0.732357 | 0.769811 | 0.043153 |
| 5 | native_0910 | stock_pooled_joint | 265 | 265 | 0.267066 | 0.011575 | 0.731034 | 0.781132 | 0.045600 |
| 5 | native_0910 | stocks_to_sectors | 265 | 265 | 0.261856 | 0.011368 | 0.719897 | 0.754717 | 0.040803 |
| 5 | preauction_0855 | anchor_aggregate_position | 265 | 216 | 0.238595 | 0.010267 | 0.666339 | 0.773585 | 0.041981 |
| 5 | preauction_0855 | anchor_asymmetry | 265 | 216 | 0.237481 | 0.010238 | 0.665361 | 0.777358 | 0.041823 |
| 5 | preauction_0855 | anchor_bias | 265 | 216 | 0.239468 | 0.010352 | 0.672365 | 0.769811 | 0.041981 |
| 5 | preauction_0855 | anchor_corporate_proxy | 265 | 216 | 0.239951 | 0.010356 | 0.672840 | 0.766038 | 0.041981 |
| 5 | preauction_0855 | anchor_fixed_joint_mixture | 265 | 265 | 0.239534 | 0.010360 | 0.671911 | 0.781132 | 0.043395 |
| 5 | preauction_0855 | anchor_location | 265 | 216 | 0.242460 | 0.010258 | 0.674901 | 0.766038 | 0.041981 |
| 5 | preauction_0855 | anchor_scale | 265 | 216 | 0.239951 | 0.010388 | 0.674802 | 0.777358 | 0.042430 |
| 5 | preauction_0855 | archived_joint_GJR | 265 | 265 | 0.250763 | 0.010922 | 0.694695 | 0.773585 | 0.042067 |
| 5 | preauction_0855 | archived_same_clock | 265 | 265 | 0.238113 | 0.010309 | 0.668373 | 0.766038 | 0.041981 |
| 5 | preauction_0855 | date_only_ridge | 265 | 265 | 0.249081 | 0.011179 | 0.693428 | 0.747170 | 0.040845 |
| 5 | preauction_0855 | pooled_market_factor | 265 | 265 | 0.255866 | 0.011465 | 0.706151 | 0.739623 | 0.040780 |
| 5 | preauction_0855 | sector_direct_joint | 265 | 265 | 0.256047 | 0.011348 | 0.715718 | 0.754717 | 0.040803 |
| 5 | preauction_0855 | stock_gaussian_shrink | 265 | 265 | 0.267394 | 0.011627 | 0.732357 | 0.769811 | 0.043153 |
| 5 | preauction_0855 | stock_pooled_joint | 265 | 265 | 0.267066 | 0.011575 | 0.731034 | 0.781132 | 0.045600 |
| 5 | preauction_0855 | stocks_to_sectors | 265 | 265 | 0.261856 | 0.011368 | 0.719897 | 0.754717 | 0.040803 |
| 21 | native_0910 | anchor_aggregate_position | 217 | 152 | 0.223819 | 0.023184 | 0.646636 | 0.714286 | 0.071940 |
| 21 | native_0910 | anchor_asymmetry | 217 | 152 | 0.229913 | 0.023989 | 0.651659 | 0.663594 | 0.071940 |
| 21 | native_0910 | anchor_bias | 217 | 152 | 0.242675 | 0.024671 | 0.674004 | 0.677419 | 0.071940 |
| 21 | native_0910 | anchor_corporate_proxy | 217 | 152 | 0.226577 | 0.023742 | 0.644528 | 0.700461 | 0.071940 |
| 21 | native_0910 | anchor_fixed_joint_mixture | 217 | 217 | 0.227694 | 0.023892 | 0.646753 | 0.714286 | 0.074945 |
| 21 | native_0910 | anchor_location | 217 | 152 | 0.247685 | 0.025167 | 0.687218 | 0.631336 | 0.071940 |
| 21 | native_0910 | anchor_scale | 217 | 152 | 0.230314 | 0.023820 | 0.652949 | 0.668203 | 0.069778 |
| 21 | native_0910 | date_only_ridge | 217 | 217 | 0.305232 | 0.030438 | 1.026716 | 0.658986 | 0.089271 |
| 21 | native_0910 | eight_calendar_day_embargo | 217 | 154 | 0.228088 | 0.024003 | 0.646729 | 0.682028 | 0.071928 |
| 21 | native_0910 | pooled_market_factor | 217 | 217 | 0.329543 | 0.032878 | 1.107154 | 0.603687 | 0.087976 |
| 21 | native_0910 | sector_direct_joint | 217 | 217 | 0.312685 | 0.030661 | 1.034398 | 0.668203 | 0.088779 |
| 21 | native_0910 | smooth5 | 217 | 159 | 0.228602 | 0.023786 | 0.648584 | 0.695853 | 0.071940 |
| 21 | native_0910 | stock_gaussian_shrink | 217 | 217 | 0.236048 | 0.024729 | 0.668296 | 0.718894 | 0.081773 |
| 21 | native_0910 | stock_pooled_joint | 217 | 217 | 0.243710 | 0.025348 | 0.680761 | 0.751152 | 0.092897 |
| 21 | native_0910 | stocks_to_sectors | 217 | 217 | 0.263975 | 0.026253 | 0.726260 | 0.728111 | 0.088779 |
| 21 | preauction_0855 | anchor_aggregate_position | 217 | 152 | 0.238916 | 0.023894 | 0.670439 | 0.746544 | 0.083754 |
| 21 | preauction_0855 | anchor_asymmetry | 217 | 152 | 0.251588 | 0.024897 | 0.696327 | 0.686636 | 0.083792 |
| 21 | preauction_0855 | anchor_bias | 217 | 152 | 0.255480 | 0.025164 | 0.704057 | 0.714286 | 0.083754 |
| 21 | preauction_0855 | anchor_corporate_proxy | 217 | 152 | 0.250796 | 0.024688 | 0.694656 | 0.714286 | 0.083754 |
| 21 | preauction_0855 | anchor_fixed_joint_mixture | 217 | 217 | 0.245838 | 0.024586 | 0.684761 | 0.728111 | 0.083775 |
| 21 | preauction_0855 | anchor_location | 217 | 152 | 0.269622 | 0.025990 | 0.733909 | 0.649770 | 0.083754 |
| 21 | preauction_0855 | anchor_scale | 217 | 152 | 0.251165 | 0.024760 | 0.695477 | 0.672811 | 0.081701 |
| 21 | preauction_0855 | archived_joint_GJR | 217 | 217 | 0.251376 | 0.024694 | 0.695900 | 0.709677 | 0.083754 |
| 21 | preauction_0855 | archived_same_clock | 217 | 217 | 0.250000 | 0.025543 | 0.693147 | 0.700461 | 0.081016 |
| 21 | preauction_0855 | date_only_ridge | 217 | 217 | 0.305232 | 0.030438 | 1.026716 | 0.658986 | 0.089271 |
| 21 | preauction_0855 | pooled_market_factor | 217 | 217 | 0.329543 | 0.032878 | 1.107154 | 0.603687 | 0.087976 |
| 21 | preauction_0855 | sector_direct_joint | 217 | 217 | 0.312685 | 0.030661 | 1.034398 | 0.668203 | 0.088779 |
| 21 | preauction_0855 | stock_gaussian_shrink | 217 | 217 | 0.236048 | 0.024729 | 0.668296 | 0.718894 | 0.081773 |
| 21 | preauction_0855 | stock_pooled_joint | 217 | 217 | 0.243710 | 0.025348 | 0.680761 | 0.751152 | 0.092897 |
| 21 | preauction_0855 | stocks_to_sectors | 217 | 217 | 0.263975 | 0.026253 | 0.726260 | 0.728111 | 0.088779 |

The weekly pure equity and sector laws were below the original weekly anchors. At the pre-auction monthly cutoff the shrunk-covariance stock law improved the direction point estimate over both archived controls. The strongest rebuilt monthly GJR reference remained competitive on full-distribution loss. The most favorable native monthly result adds aggregate positioning to the existing smoothed-positioning law. This tests an additional common-market forecast correction. The size and direction of the remaining uncertainty are recorded on matched dates.

| horizon | cutoff | model | reference | metric | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | anchor_aggregate_position | price_reaction | brier | 265 | -0.000739 | -0.013900 | 0.012422 |
| 5 | native_0910 | anchor_asymmetry | price_reaction | brier | 265 | 0.001254 | -0.002336 | 0.004845 |
| 5 | native_0910 | anchor_location | price_reaction | brier | 265 | -0.003938 | -0.021820 | 0.013944 |
| 5 | native_0910 | stock_gaussian_shrink | price_reaction | brier | 265 | -0.044011 | -0.102281 | 0.014260 |
| 5 | native_0910 | anchor_aggregate_position | price_reaction | crps | 265 | -0.000086 | -0.000498 | 0.000325 |
| 5 | native_0910 | anchor_asymmetry | price_reaction | crps | 265 | 0.000091 | -0.000158 | 0.000339 |
| 5 | native_0910 | anchor_location | price_reaction | crps | 265 | -0.000030 | -0.000510 | 0.000449 |
| 5 | native_0910 | stock_gaussian_shrink | price_reaction | crps | 265 | -0.001369 | -0.003608 | 0.000869 |
| 5 | native_0910 | anchor_aggregate_position | omit_latest_21_training_origins | brier | 265 | -0.002430 | -0.019049 | 0.014190 |
| 5 | native_0910 | anchor_asymmetry | omit_latest_21_training_origins | brier | 265 | -0.000436 | -0.014037 | 0.013165 |
| 5 | native_0910 | anchor_location | omit_latest_21_training_origins | brier | 265 | -0.005629 | -0.028134 | 0.016877 |
| 5 | native_0910 | stock_gaussian_shrink | omit_latest_21_training_origins | brier | 265 | -0.045701 | -0.105396 | 0.013993 |
| 5 | native_0910 | anchor_aggregate_position | omit_latest_21_training_origins | crps | 265 | -0.000070 | -0.000666 | 0.000525 |
| 5 | native_0910 | anchor_asymmetry | omit_latest_21_training_origins | crps | 265 | 0.000107 | -0.000626 | 0.000839 |
| 5 | native_0910 | anchor_location | omit_latest_21_training_origins | crps | 265 | -0.000014 | -0.000868 | 0.000839 |
| 5 | native_0910 | stock_gaussian_shrink | omit_latest_21_training_origins | crps | 265 | -0.001353 | -0.003673 | 0.000966 |
| 5 | preauction_0855 | anchor_aggregate_position | archived_same_clock | brier | 265 | -0.000482 | -0.022055 | 0.021091 |
| 5 | preauction_0855 | anchor_asymmetry | archived_same_clock | brier | 265 | 0.000632 | -0.003962 | 0.005226 |
| 5 | preauction_0855 | anchor_location | archived_same_clock | brier | 265 | -0.004347 | -0.029972 | 0.021279 |
| 5 | preauction_0855 | stock_gaussian_shrink | archived_same_clock | brier | 265 | -0.029281 | -0.086609 | 0.028047 |
| 5 | preauction_0855 | anchor_aggregate_position | archived_same_clock | crps | 265 | 0.000042 | -0.000577 | 0.000661 |
| 5 | preauction_0855 | anchor_asymmetry | archived_same_clock | crps | 265 | 0.000071 | -0.000133 | 0.000274 |
| 5 | preauction_0855 | anchor_location | archived_same_clock | crps | 265 | 0.000051 | -0.000647 | 0.000748 |
| 5 | preauction_0855 | stock_gaussian_shrink | archived_same_clock | crps | 265 | -0.001319 | -0.003429 | 0.000791 |
| 5 | preauction_0855 | anchor_aggregate_position | archived_joint_GJR | brier | 265 | 0.012168 | -0.021851 | 0.046186 |
| 5 | preauction_0855 | anchor_asymmetry | archived_joint_GJR | brier | 265 | 0.013282 | -0.017550 | 0.044115 |
| 5 | preauction_0855 | anchor_location | archived_joint_GJR | brier | 265 | 0.008303 | -0.022334 | 0.038941 |
| 5 | preauction_0855 | stock_gaussian_shrink | archived_joint_GJR | brier | 265 | -0.016631 | -0.060730 | 0.027467 |
| 5 | preauction_0855 | anchor_aggregate_position | archived_joint_GJR | crps | 265 | 0.000655 | -0.000727 | 0.002037 |
| 5 | preauction_0855 | anchor_asymmetry | archived_joint_GJR | crps | 265 | 0.000684 | -0.000739 | 0.002106 |
| 5 | preauction_0855 | anchor_location | archived_joint_GJR | crps | 265 | 0.000664 | -0.000739 | 0.002066 |
| 5 | preauction_0855 | stock_gaussian_shrink | archived_joint_GJR | crps | 265 | -0.000706 | -0.002367 | 0.000956 |
| 21 | native_0910 | anchor_aggregate_position | smooth5 | brier | 217 | 0.004783 | -0.049645 | 0.059211 |
| 21 | native_0910 | anchor_asymmetry | smooth5 | brier | 217 | -0.001311 | -0.004349 | 0.001726 |
| 21 | native_0910 | anchor_location | smooth5 | brier | 217 | -0.019084 | -0.050822 | 0.012655 |
| 21 | native_0910 | stock_gaussian_shrink | smooth5 | brier | 217 | -0.007446 | -0.086163 | 0.071270 |
| 21 | native_0910 | anchor_aggregate_position | smooth5 | crps | 217 | 0.000602 | -0.002026 | 0.003230 |
| 21 | native_0910 | anchor_asymmetry | smooth5 | crps | 217 | -0.000203 | -0.000643 | 0.000237 |
| 21 | native_0910 | anchor_location | smooth5 | crps | 217 | -0.001381 | -0.003127 | 0.000366 |
| 21 | native_0910 | stock_gaussian_shrink | smooth5 | crps | 217 | -0.000943 | -0.005739 | 0.003853 |
| 21 | native_0910 | anchor_aggregate_position | eight_calendar_day_embargo | brier | 217 | 0.004269 | -0.048885 | 0.057424 |
| 21 | native_0910 | anchor_asymmetry | eight_calendar_day_embargo | brier | 217 | -0.001825 | -0.019235 | 0.015584 |
| 21 | native_0910 | anchor_location | eight_calendar_day_embargo | brier | 217 | -0.019598 | -0.050632 | 0.011437 |
| 21 | native_0910 | stock_gaussian_shrink | eight_calendar_day_embargo | brier | 217 | -0.007960 | -0.088680 | 0.072759 |

[index-model-leaderboard.csv](index-model-leaderboard.csv) · [matched-index-comparisons.csv](matched-index-comparisons.csv) · [index-search-adjusted-intervals.csv](index-search-adjusted-intervals.csv) · [index-forecast-cases.csv.gz](index-forecast-cases.csv.gz) · [index-forecast-laws.npz](index-forecast-laws.npz) · [joint-forecast-config.json](joint-forecast-config.json) · [forecast-law-examples.json](forecast-law-examples.json)
