# V20 Complete Model Comparison

The original samples are 265 weekly and 217 monthly forecasts, with 53 and 11 non-overlapping outcomes. Each prospective timing definition has a separate case table. The machine leaderboards retain early, late, combined and active coverage, error, proper scores, calibration and interval summaries. Matched differences and block-adjusted uncertainty are stored alongside each candidate.

## Native weekly and monthly endpoint forecasts at 09:10

| horizon | ranked metric | model | n | active | disjoint | brier | log loss | crps | mae | balanced accuracy | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | omit_latest_21_training_origins | 265 | 202 | 53 | 0.221693 | 0.634612 | 0.010274 | 0.014518 | 0.660141 | 0.826415 | 0.045711 |
| 5 | brier | eight_calendar_day_embargo | 265 | 217 | 53 | 0.221932 | 0.635160 | 0.010337 | 0.014519 | 0.665107 | 0.815094 | 0.045698 |
| 5 | brier | location_scale_asymmetry | 265 | 223 | 53 | 0.221956 | 0.633662 | 0.010420 | 0.014589 | 0.636983 | 0.815094 | 0.045789 |
| 5 | brier | price_reaction | 265 | 223 | 53 | 0.223384 | 0.638699 | 0.010258 | 0.014494 | 0.657456 | 0.830189 | 0.045719 |
| 5 | brier | preceding_evening | 265 | 223 | 53 | 0.223393 | 0.637967 | 0.010347 | 0.014593 | 0.640362 | 0.811321 | 0.045703 |
| 5 | crps | price_reaction | 265 | 223 | 53 | 0.223384 | 0.638699 | 0.010258 | 0.014494 | 0.657456 | 0.830189 | 0.045719 |
| 5 | crps | omit_latest_21_training_origins | 265 | 202 | 53 | 0.221693 | 0.634612 | 0.010274 | 0.014518 | 0.660141 | 0.826415 | 0.045711 |
| 5 | crps | corporate_robust_market | 265 | 223 | 53 | 0.224191 | 0.639440 | 0.010302 | 0.014623 | 0.618503 | 0.815094 | 0.045717 |
| 5 | crps | counts | 265 | 223 | 53 | 0.224304 | 0.639830 | 0.010307 | 0.014702 | 0.636290 | 0.822642 | 0.045735 |
| 5 | crps | v18_corporate_native | 265 | 265 | 53 | 0.223481 | 0.637789 | 0.010318 | 0.014567 | 0.636983 | 0.818868 | 0.045700 |
| 21 | brier | eight_calendar_day_embargo | 217 | 154 | 11 | 0.228088 | 0.646729 | 0.024003 | 0.031264 | 0.563934 | 0.682028 | 0.071928 |
| 21 | brier | positions_v19_feature_set | 217 | 159 | 11 | 0.228199 | 0.647076 | 0.024010 | 0.031248 | 0.568637 | 0.672811 | 0.071921 |
| 21 | brier | v19_position_native | 217 | 159 | 11 | 0.228199 | 0.647076 | 0.024010 | 0.031248 | 0.568637 | 0.672811 | 0.071921 |
| 21 | brier | smooth5 | 217 | 159 | 11 | 0.228602 | 0.648584 | 0.023786 | 0.031200 | 0.603710 | 0.695853 | 0.071940 |
| 21 | brier | short_training70 | 217 | 159 | 11 | 0.228961 | 0.647897 | 0.024184 | 0.031432 | 0.545815 | 0.668203 | 0.071892 |
| 21 | crps | smooth5 | 217 | 159 | 11 | 0.228602 | 0.648584 | 0.023786 | 0.031200 | 0.603710 | 0.695853 | 0.071940 |
| 21 | crps | eight_calendar_day_embargo | 217 | 154 | 11 | 0.228088 | 0.646729 | 0.024003 | 0.031264 | 0.563934 | 0.682028 | 0.071928 |
| 21 | crps | positions_v19_feature_set | 217 | 159 | 11 | 0.228199 | 0.647076 | 0.024010 | 0.031248 | 0.568637 | 0.672811 | 0.071921 |
| 21 | crps | v19_position_native | 217 | 159 | 11 | 0.228199 | 0.647076 | 0.024010 | 0.031248 | 0.568637 | 0.672811 | 0.071921 |
| 21 | crps | lag1 | 217 | 159 | 11 | 0.233140 | 0.657232 | 0.024080 | 0.031508 | 0.563374 | 0.682028 | 0.071891 |

## Rebuilt distributions at 08:55

| horizon | ranked metric | model | n | active | disjoint | brier | log loss | crps | mae | balanced accuracy | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | G_fixed_specialized_mixture | 265 | 265 | 53 | 0.237729 | 0.667909 | 0.010516 | 0.014424 | 0.574469 | 0.807547 | 0.043375 |
| 5 | brier | archived_same_clock | 265 | 265 | 53 | 0.238113 | 0.668373 | 0.010309 | 0.014286 | 0.575970 | 0.766038 | 0.041981 |
| 5 | brier | archived_joint_GJR | 265 | 265 | 53 | 0.250763 | 0.694695 | 0.010922 | 0.015006 | 0.573516 | 0.773585 | 0.042067 |
| 5 | brier | C_shared_state_two_heads | 265 | 265 | 53 | 0.253065 | 0.697054 | 0.011328 | 0.015257 | 0.460874 | 0.758491 | 0.041919 |
| 5 | crps | archived_same_clock | 265 | 265 | 53 | 0.238113 | 0.668373 | 0.010309 | 0.014286 | 0.575970 | 0.766038 | 0.041981 |
| 5 | crps | G_fixed_specialized_mixture | 265 | 265 | 53 | 0.237729 | 0.667909 | 0.010516 | 0.014424 | 0.574469 | 0.807547 | 0.043375 |
| 5 | crps | archived_joint_GJR | 265 | 265 | 53 | 0.250763 | 0.694695 | 0.010922 | 0.015006 | 0.573516 | 0.773585 | 0.042067 |
| 5 | crps | C_shared_state_two_heads | 265 | 265 | 53 | 0.253065 | 0.697054 | 0.011328 | 0.015257 | 0.460874 | 0.758491 | 0.041919 |
| 21 | brier | archived_same_clock | 217 | 217 | 11 | 0.250000 | 0.693147 | 0.025543 | 0.033404 | 0.500000 | 0.700461 | 0.081016 |
| 21 | brier | archived_joint_GJR | 217 | 217 | 11 | 0.251376 | 0.695900 | 0.024694 | 0.033162 | 0.524072 | 0.709677 | 0.083754 |
| 21 | brier | G_fixed_specialized_mixture | 217 | 217 | 11 | 0.261585 | 0.717663 | 0.026360 | 0.034043 | 0.500259 | 0.682028 | 0.083690 |
| 21 | brier | E_sparse_horizon_inputs | 217 | 217 | 11 | 0.295546 | 0.823077 | 0.029178 | 0.037557 | 0.500259 | 0.631336 | 0.080472 |
| 21 | crps | archived_joint_GJR | 217 | 217 | 11 | 0.251376 | 0.695900 | 0.024694 | 0.033162 | 0.524072 | 0.709677 | 0.083754 |
| 21 | crps | archived_same_clock | 217 | 217 | 11 | 0.250000 | 0.693147 | 0.025543 | 0.033404 | 0.500000 | 0.700461 | 0.081016 |
| 21 | crps | G_fixed_specialized_mixture | 217 | 217 | 11 | 0.261585 | 0.717663 | 0.026360 | 0.034043 | 0.500259 | 0.682028 | 0.083690 |
| 21 | crps | E_sparse_horizon_inputs | 217 | 217 | 11 | 0.295546 | 0.823077 | 0.029178 | 0.037557 | 0.500259 | 0.631336 | 0.080472 |

Protected empirical atoms are scored by exact sign mass in the saved law. Earlier V17 tables sometimes used half-atom smoothing for Brier. This accounts for the slightly different V17 probability score here. Weighted V14/V18/V19 native comparisons retain their original scoring convention.

## Incremental late information and separate risk objectives

| family | matched | disjoint | parent | enhanced | gain | earlier gain | later gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| participant_options | 217 | 14 | 0.026969 | 0.026381 | 0.000587 | 0.000461 | 0.000822 | -0.001611 | 0.002785 |
| offshore_gift | 212 | 14 | 0.027349 | 0.027249 | 0.000100 | 0.000154 | -1.24e-06 | -0.000136 | 0.000336 |
| participant_futures | 217 | 14 | 0.026969 | 0.026978 | -9.86e-06 | -0.000047 | 0.000058 | -0.002805 | 0.002786 |
| intraday_structure | 217 | 14 | 0.026969 | 0.027024 | -0.000055 | -0.000065 | -0.000037 | -0.000334 | 0.000223 |
| global_equities | 217 | 14 | 0.026969 | 0.027027 | -0.000059 | -0.000165 | 0.000139 | -0.000444 | 0.000326 |
| equal_weight_breadth | 217 | 14 | 0.026969 | 0.027265 | -0.000297 | -0.000373 | -0.000154 | -0.001437 | 0.000843 |
| corporate_announcements | 217 | 14 | 0.026969 | 0.027274 | -0.000305 | -0.001266 | 0.001478 | -0.003021 | 0.002410 |
| institutional_flows | 168 | 11 | 0.029776 | 0.030111 | -0.000335 | -0.001266 | 0.000791 | -0.002450 | 0.001779 |

| horizon | ranked metric | model | n | active | mae | q like | brier | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | mae | offshore_plus_domestic | 265 | 265 | 0.036469 | 0.290334 | 0.160327 | 0.476147 |
| 5 | mae | offshore_plus_domestic+transition | 265 | 223 | 0.036469 | 0.290334 | 0.162960 | 0.480432 |
| 5 | mae | offshore_plus_domestic+risk_level | 265 | 223 | 0.037455 | 0.296965 | 0.160327 | 0.476147 |
| 5 | mae | fixed_iv_rv | 265 | 265 | 0.038484 | 0.286114 | 0.152707 | 0.461636 |
| 5 | brier | fixed_iv_rv | 265 | 265 | 0.038484 | 0.286114 | 0.152707 | 0.461636 |
| 5 | brier | fixed_iv_rv+risk_level | 265 | 223 | 0.038916 | 0.290789 | 0.152707 | 0.461636 |
| 5 | brier | fixed_iv_rv+transition | 265 | 223 | 0.038484 | 0.286114 | 0.153782 | 0.462959 |
| 5 | brier | offshore_plus_domestic | 265 | 265 | 0.036469 | 0.290334 | 0.160327 | 0.476147 |
| 21 | mae | GJR | 217 | 217 | 0.033179 | 0.199677 | 0.198781 | 0.769605 |
| 21 | mae | GJR+transition | 217 | 159 | 0.033179 | 0.199677 | 0.195397 | 0.679825 |
| 21 | mae | GJR+risk_level | 217 | 159 | 0.034431 | 0.191663 | 0.198781 | 0.769605 |
| 21 | mae | student_EGARCH | 217 | 217 | 0.035730 | 0.207684 | 0.172864 | 0.689982 |
| 21 | brier | student_EGARCH+transition | 217 | 159 | 0.035730 | 0.207684 | 0.170994 | 0.636613 |
| 21 | brier | student_EGARCH | 217 | 217 | 0.035730 | 0.207684 | 0.172864 | 0.689982 |
| 21 | brier | student_EGARCH+risk_level | 217 | 159 | 0.038311 | 0.215952 | 0.172864 | 0.689982 |
| 21 | brier | GJR+transition | 217 | 159 | 0.033179 | 0.199677 | 0.195397 | 0.679825 |

| horizon | ranked metric | model | n | range crps | touch brier | integrated brier | vol mae |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | range_crps | location_specialized | 265 | 0.005760 | 0.143873 | 0.119678 | 0.036803 |
| 5 | range_crps | asymmetric_specialized | 265 | 0.005768 | 0.144418 | 0.120146 | 0.036793 |
| 5 | range_crps | same_clock_IV | 265 | 0.005768 | 0.144562 | 0.120331 | 0.036801 |
| 5 | range_crps | coherent_all | 265 | 0.005862 | 0.144415 | 0.119738 | 0.037318 |
| 5 | touch_brier | location_specialized | 265 | 0.005760 | 0.143873 | 0.119678 | 0.036803 |
| 5 | touch_brier | coherent_all | 265 | 0.005862 | 0.144415 | 0.119738 | 0.037318 |
| 5 | touch_brier | asymmetric_specialized | 265 | 0.005768 | 0.144418 | 0.120146 | 0.036793 |
| 5 | touch_brier | same_clock_IV | 265 | 0.005768 | 0.144562 | 0.120331 | 0.036801 |
| 21 | range_crps | location_specialized | 217 | 0.015246 | 0.183315 | 0.161946 | 0.037172 |
| 21 | range_crps | asymmetric_specialized | 217 | 0.015467 | 0.182813 | 0.160926 | 0.037397 |
| 21 | range_crps | same_clock_GJR | 217 | 0.015488 | 0.183861 | 0.161061 | 0.037244 |
| 21 | range_crps | coherent_all | 217 | 0.016012 | 0.185458 | 0.163978 | 0.038408 |
| 21 | touch_brier | asymmetric_specialized | 217 | 0.015467 | 0.182813 | 0.160926 | 0.037397 |
| 21 | touch_brier | location_specialized | 217 | 0.015246 | 0.183315 | 0.161946 | 0.037172 |
| 21 | touch_brier | same_clock_GJR | 217 | 0.015488 | 0.183861 | 0.161061 | 0.037244 |
| 21 | touch_brier | same_clock_IV | 217 | 0.017179 | 0.184372 | 0.159680 | 0.040023 |

[model-leaderboards.csv](model-leaderboards.csv) · [complete-matched-comparisons.csv](complete-matched-comparisons.csv) · [matched-block-intervals.csv.gz](matched-block-intervals.csv.gz) · [information-lifetime-matrix.csv](information-lifetime-matrix.csv) · [component-leaderboard.csv](component-leaderboard.csv) · [probability-calibration.csv](probability-calibration.csv) · [all-disjoint-window-phases.csv](all-disjoint-window-phases.csv) · [protected-joint-benchmarks.csv](protected-joint-benchmarks.csv)
