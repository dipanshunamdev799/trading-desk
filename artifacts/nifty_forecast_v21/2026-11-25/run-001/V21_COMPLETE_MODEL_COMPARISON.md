# V21 Complete Model Comparison

All endpoint rows share the original **173 / 92 / 265 weekly** and **141 / 76 / 217 monthly** comparison cohorts. These represent **53** and **11** non-overlapping windows. Metric and source roles remain visible at each original forecast cutoff. Every leaderboard points to a separately archived case file and, where available, its law. The date-level stock tables describe prediction of security and sector targets. Index gains are evaluated on the index itself.

| horizon | metric | candidate | new | reference | prior | difference |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | omit_latest_21_training_origins | 0.221693 | omit_latest_21_training_origins | 0.221693 | 0.000000 |
| 5 | crps | anchor_asymmetry | 0.010167 | price_reaction | 0.010258 | 0.000091 |
| 21 | brier | anchor_aggregate_position | 0.223819 | eight_calendar_day_embargo | 0.228088 | 0.004269 |
| 21 | crps | anchor_aggregate_position | 0.023184 | smooth5 | 0.023786 | 0.000602 |

| horizon | cutoff | ranked by | model | n | active | disjoint | brier | crps | log loss | accuracy | balanced accuracy | mae | rmse | rank corr | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | brier | omit_latest_21_training_origins | 265 | 202 | 53 | 0.221693 | 0.010274 | 0.634612 | 0.660377 | 0.660141 | 0.014518 | 0.020728 | 0.366637 | 0.826415 | 0.045711 |
| 5 | native_0910 | brier | anchor_asymmetry | 265 | 216 | 53 | 0.222129 | 0.010167 | 0.635730 | 0.656604 | 0.654972 | 0.014480 | 0.020157 | 0.384557 | 0.822642 | 0.045819 |
| 5 | native_0910 | brier | price_reaction | 265 | 223 | 53 | 0.223384 | 0.010258 | 0.638699 | 0.660377 | 0.657456 | 0.014494 | 0.020518 | 0.374699 | 0.830189 | 0.045719 |
| 5 | native_0910 | brier | v18_corporate_native | 265 | 265 | 53 | 0.223481 | 0.010318 | 0.637789 | 0.641509 | 0.636983 | 0.014567 | 0.020797 | 0.343147 | 0.818868 | 0.045700 |
| 5 | native_0910 | crps | anchor_asymmetry | 265 | 216 | 53 | 0.222129 | 0.010167 | 0.635730 | 0.656604 | 0.654972 | 0.014480 | 0.020157 | 0.384557 | 0.822642 | 0.045819 |
| 5 | native_0910 | crps | price_reaction | 265 | 223 | 53 | 0.223384 | 0.010258 | 0.638699 | 0.660377 | 0.657456 | 0.014494 | 0.020518 | 0.374699 | 0.830189 | 0.045719 |
| 5 | native_0910 | crps | anchor_bias | 265 | 216 | 53 | 0.224355 | 0.010272 | 0.641204 | 0.660377 | 0.654770 | 0.014517 | 0.020640 | 0.364519 | 0.822642 | 0.045719 |
| 5 | native_0910 | crps | omit_latest_21_training_origins | 265 | 202 | 53 | 0.221693 | 0.010274 | 0.634612 | 0.660377 | 0.660141 | 0.014518 | 0.020728 | 0.366637 | 0.826415 | 0.045711 |
| 5 | preauction_0855 | brier | anchor_asymmetry | 265 | 216 | 53 | 0.237481 | 0.010238 | 0.665361 | 0.581132 | 0.580244 | 0.014238 | 0.019297 | 0.293652 | 0.777358 | 0.041823 |
| 5 | preauction_0855 | brier | archived_same_clock | 265 | 265 | 53 | 0.238113 | 0.010309 | 0.668373 | 0.577358 | 0.575970 | 0.014286 | 0.019532 | 0.290602 | 0.766038 | 0.041981 |
| 5 | preauction_0855 | brier | anchor_aggregate_position | 265 | 216 | 53 | 0.238595 | 0.010267 | 0.666339 | 0.569811 | 0.578165 | 0.014179 | 0.019328 | 0.317738 | 0.773585 | 0.041981 |
| 5 | preauction_0855 | brier | anchor_bias | 265 | 216 | 53 | 0.239468 | 0.010352 | 0.672365 | 0.581132 | 0.579349 | 0.014452 | 0.019670 | 0.281952 | 0.769811 | 0.041981 |
| 5 | preauction_0855 | crps | anchor_asymmetry | 265 | 216 | 53 | 0.237481 | 0.010238 | 0.665361 | 0.581132 | 0.580244 | 0.014238 | 0.019297 | 0.293652 | 0.777358 | 0.041823 |
| 5 | preauction_0855 | crps | anchor_location | 265 | 216 | 53 | 0.242460 | 0.010258 | 0.674901 | 0.550943 | 0.554112 | 0.014278 | 0.019121 | 0.284124 | 0.766038 | 0.041981 |
| 5 | preauction_0855 | crps | anchor_aggregate_position | 265 | 216 | 53 | 0.238595 | 0.010267 | 0.666339 | 0.569811 | 0.578165 | 0.014179 | 0.019328 | 0.317738 | 0.773585 | 0.041981 |
| 5 | preauction_0855 | crps | archived_same_clock | 265 | 265 | 53 | 0.238113 | 0.010309 | 0.668373 | 0.577358 | 0.575970 | 0.014286 | 0.019532 | 0.290602 | 0.766038 | 0.041981 |
| 21 | native_0910 | brier | anchor_aggregate_position | 217 | 152 | 11 | 0.223819 | 0.023184 | 0.646636 | 0.576037 | 0.615962 | 0.029737 | 0.043023 | 0.510715 | 0.714286 | 0.071940 |
| 21 | native_0910 | brier | anchor_corporate_proxy | 217 | 152 | 11 | 0.226577 | 0.023742 | 0.644528 | 0.571429 | 0.602545 | 0.031118 | 0.043623 | 0.408688 | 0.700461 | 0.071940 |
| 21 | native_0910 | brier | anchor_fixed_joint_mixture | 217 | 217 | 11 | 0.227694 | 0.023892 | 0.646753 | 0.580645 | 0.614236 | 0.031136 | 0.043564 | 0.458408 | 0.714286 | 0.074945 |
| 21 | native_0910 | brier | eight_calendar_day_embargo | 217 | 154 | 11 | 0.228088 | 0.024003 | 0.646729 | 0.534562 | 0.563934 | 0.031264 | 0.044004 | 0.310668 | 0.682028 | 0.071928 |
| 21 | native_0910 | crps | anchor_aggregate_position | 217 | 152 | 11 | 0.223819 | 0.023184 | 0.646636 | 0.576037 | 0.615962 | 0.029737 | 0.043023 | 0.510715 | 0.714286 | 0.071940 |
| 21 | native_0910 | crps | anchor_corporate_proxy | 217 | 152 | 11 | 0.226577 | 0.023742 | 0.644528 | 0.571429 | 0.602545 | 0.031118 | 0.043623 | 0.408688 | 0.700461 | 0.071940 |
| 21 | native_0910 | crps | smooth5 | 217 | 159 | 11 | 0.228602 | 0.023786 | 0.648584 | 0.571429 | 0.603710 | 0.031200 | 0.043695 | 0.409155 | 0.695853 | 0.071940 |
| 21 | native_0910 | crps | anchor_scale | 217 | 152 | 11 | 0.230314 | 0.023820 | 0.652949 | 0.571429 | 0.603710 | 0.031200 | 0.043695 | 0.409089 | 0.668203 | 0.069778 |
| 21 | preauction_0855 | brier | stock_gaussian_shrink | 217 | 217 | 11 | 0.236048 | 0.024729 | 0.668296 | 0.603687 | 0.606773 | 0.032186 | 0.044173 | 0.292687 | 0.718894 | 0.081773 |
| 21 | preauction_0855 | brier | stock_without_heavy5 | 217 | 217 | 11 | 0.237627 | 0.025127 | 0.671914 | 0.617512 | 0.643529 | 0.032285 | 0.044217 | 0.310149 | 0.760369 | 0.094735 |
| 21 | preauction_0855 | brier | anchor_aggregate_position | 217 | 152 | 11 | 0.238916 | 0.023894 | 0.670439 | 0.534562 | 0.581406 | 0.031577 | 0.043159 | 0.544242 | 0.746544 | 0.083754 |
| 21 | preauction_0855 | brier | stock_equal_weight | 217 | 217 | 11 | 0.241031 | 0.025136 | 0.677818 | 0.599078 | 0.616652 | 0.032048 | 0.043889 | 0.329335 | 0.751152 | 0.090753 |
| 21 | preauction_0855 | crps | anchor_aggregate_position | 217 | 152 | 11 | 0.238916 | 0.023894 | 0.670439 | 0.534562 | 0.581406 | 0.031577 | 0.043159 | 0.544242 | 0.746544 | 0.083754 |
| 21 | preauction_0855 | crps | anchor_fixed_joint_mixture | 217 | 217 | 11 | 0.245838 | 0.024586 | 0.684761 | 0.516129 | 0.560354 | 0.032437 | 0.044214 | 0.360042 | 0.728111 | 0.083775 |
| 21 | preauction_0855 | crps | anchor_corporate_proxy | 217 | 152 | 11 | 0.250796 | 0.024688 | 0.694656 | 0.465438 | 0.507118 | 0.033122 | 0.044507 | 0.174598 | 0.714286 | 0.083754 |
| 21 | preauction_0855 | crps | archived_joint_GJR | 217 | 217 | 11 | 0.251376 | 0.024694 | 0.695900 | 0.479263 | 0.524072 | 0.033162 | 0.044571 | 0.192655 | 0.709677 | 0.083754 |

[stock-leaderboard.csv](stock-leaderboard.csv) · [stock-probability-calibration.csv](stock-probability-calibration.csv) · [sector-forecast-leaderboard.csv](sector-forecast-leaderboard.csv) · [market-factor-leaderboard.csv](market-factor-leaderboard.csv) · [index-tracking-leaderboard.csv](index-tracking-leaderboard.csv) · [index-model-leaderboard.csv](index-model-leaderboard.csv) · [matched-index-comparisons.csv](matched-index-comparisons.csv) · [index-search-adjusted-intervals.csv](index-search-adjusted-intervals.csv) · [index-probability-calibration.csv](index-probability-calibration.csv) · [risk-leaderboard.csv](risk-leaderboard.csv) · [synthetic-power-summary.csv](synthetic-power-summary.csv) · [forecast-law-examples.json](forecast-law-examples.json)
