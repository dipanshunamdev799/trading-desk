# V20 Monthly Positioning Mechanisms

The native parent and V19 law replay are exact. Separate V20 fits distinguish FII futures level, changes over 1, 3, 5, 10 and 21 sessions, DII level, proprietary level, gross exposure, participant concentration, volume, stock futures and aggregate options. The persistence block adds an earlier rolling standardization, a 21-session exposure mean and acceleration. A participant’s option counts are exchange-classified contract counts. Portfolio delta and personal open interest are unobserved.

The new innovation estimator uses the median observed position change of the **15 nearest earlier historical states**, considering returns, volatility, expiry, roll status, breadth, basis and prior positioning. It selects those contexts from at most **150** earlier observations and needs at least **50**. Standardization and the innovation’s empirical rank are historical-only. The table compares a direct ordinary change block, the analogue innovations and a combined design on the same native parent.

| model | n | active | disjoint | brier | crps | log loss |
| --- | --- | --- | --- | --- | --- | --- |
| bias_only | 217 | 159 | 11 | 0.272920 | 0.025984 | 0.741578 |
| changes_plus_analogue | 217 | 159 | 11 | 0.243751 | 0.024768 | 0.678118 |
| concentration | 217 | 159 | 11 | 0.250186 | 0.025023 | 0.693394 |
| dii_level | 217 | 159 | 11 | 0.294068 | 0.026974 | 0.786865 |
| eight_calendar_day_embargo | 217 | 154 | 11 | 0.228088 | 0.024003 | 0.646729 |
| exact_v14 | 217 | 217 | 11 | 0.245042 | 0.024989 | 0.683095 |
| fii_changes | 217 | 159 | 11 | 0.245687 | 0.024840 | 0.682402 |
| fii_level | 217 | 159 | 11 | 0.241067 | 0.024910 | 0.673482 |
| gross_exposure | 217 | 159 | 11 | 0.262033 | 0.025373 | 0.718048 |
| lag1 | 217 | 159 | 11 | 0.233140 | 0.024080 | 0.657232 |
| lag10 | 217 | 159 | 11 | 0.271259 | 0.025836 | 0.737855 |
| lag21 | 217 | 159 | 11 | 0.295817 | 0.026884 | 0.792177 |
| lag3 | 217 | 159 | 11 | 0.250572 | 0.024736 | 0.693785 |
| lag5 | 217 | 159 | 11 | 0.257619 | 0.025011 | 0.709840 |
| new_innovations | 217 | 159 | 11 | 0.265863 | 0.025788 | 0.726465 |
| omit_latest_21_training_origins | 217 | 138 | 11 | 0.237751 | 0.024312 | 0.667303 |
| options | 217 | 159 | 11 | 0.248139 | 0.025138 | 0.688699 |
| persistence | 217 | 159 | 11 | 0.247585 | 0.024817 | 0.686735 |
| positions_v19_feature_set | 217 | 159 | 11 | 0.228199 | 0.024010 | 0.647076 |
| preceding_evening | 217 | 159 | 11 | 0.233140 | 0.024080 | 0.657232 |
| pro_level | 217 | 159 | 11 | 0.262852 | 0.025481 | 0.719318 |
| short_training70 | 217 | 159 | 11 | 0.228961 | 0.024184 | 0.647897 |
| smooth5 | 217 | 159 | 11 | 0.228602 | 0.023786 | 0.648584 |
| stock_futures | 217 | 159 | 11 | 0.256866 | 0.025780 | 0.708096 |
| trading_volume | 217 | 159 | 11 | 0.275703 | 0.026113 | 0.748578 |
| v19_position_native | 217 | 159 | 11 | 0.228199 | 0.024010 | 0.647076 |

The cohort study displays announcement, volatility, trend and concentration ranks computed from earlier inputs, plus dated expiry and rollover. The output includes measurement availability, training sample size, elapsed-market state, disagreement and alternative fitting windows. Associations within these strata and signs of median coefficients are sensitive to the model and available observations.

| cohort | regime | n | mean FII | mean IV | mean n train | v19 brier gain | v19 crps gain | new brier gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | all_ | 83 | -0.251660 | 0.180609 | 79.000000 | 0.044910 | 0.002210 | 0.044910 |
| later | all_ | 76 | -0.311264 | 0.110498 | 137.500000 | -0.000954 | 0.000382 | -0.000954 |
| early | away_from_expiry | 74 | -0.253749 | 0.181228 | 79.554054 | 0.046388 | 0.002236 | 0.046388 |
| later | away_from_expiry | 69 | -0.310418 | 0.110187 | 137.521739 | -0.010417 | 0.000337 | -0.010417 |
| early | high_concentration | 39 | -0.248952 | 0.206619 | 65.461538 | 0.046496 | 0.002870 | 0.046496 |
| later | high_concentration | 35 | -0.320381 | 0.108196 | 137.571429 | -0.091420 | -0.002875 | -0.091420 |
| early | other_concentration | 44 | -0.254061 | 0.157554 | 91.000000 | 0.043505 | 0.001625 | 0.043505 |
| later | other_concentration | 41 | -0.303481 | 0.112462 | 137.439024 | 0.076273 | 0.003162 | 0.076273 |
| early | high_iv | 35 | -0.234025 | 0.219023 | 55.942857 | 0.038932 | 0.002160 | 0.038932 |
| later | high_iv | 4 | -0.337826 | 0.138579 | 140.000000 | 0.077116 | 0.005105 | 0.077116 |
| early | ordinary_iv | 48 | -0.264519 | 0.152599 | 95.812500 | 0.049270 | 0.002247 | 0.049270 |
| later | ordinary_iv | 72 | -0.309788 | 0.108938 | 137.361111 | -0.005292 | 0.000119 | -0.005292 |
| early | rising_state | 36 | -0.250319 | 0.153234 | 89.694444 | 0.036293 | 0.001842 | 0.036293 |
| later | rising_state | 37 | -0.299877 | 0.110464 | 134.972973 | 0.096668 | 0.003398 | 0.096668 |
| early | falling_state | 47 | -0.252687 | 0.201576 | 70.808511 | 0.051511 | 0.002493 | 0.051511 |
| later | falling_state | 39 | -0.322066 | 0.110529 | 139.897436 | -0.093571 | -0.002480 | -0.093571 |

| cohort | field | median | p10 | p90 | positive | fit count |
| --- | --- | --- | --- | --- | --- | --- |
| later | FII_index_futures_d21 | -0.007925 | -0.008717 | -0.007690 | 0.000000 | 76 |
| early | FII_index_futures_d21 | -0.006372 | -0.007790 | 0.001004 | 0.156627 | 83 |
| later | Pro_index_futures_level | 0.006018 | 0.005386 | 0.007049 | 1.000000 | 76 |
| later | index_futures_detail_hhi_z | 0.005109 | 0.003576 | 0.005288 | 1.000000 | 76 |
| early | DII_index_futures_level | -0.005027 | -0.005389 | -0.001325 | 0.000000 | 83 |
| early | Pro_index_futures_level | 0.004914 | 0.000923 | 0.005506 | 1.000000 | 83 |
| later | FII_index_futures_level | -0.004732 | -0.005238 | -0.003862 | 0.000000 | 76 |
| later | DII_index_futures_level | -0.004456 | -0.004908 | -0.000131 | 0.105263 | 76 |
| later | index_calls_disagree | 0.004317 | 0.003267 | 0.005550 | 1.000000 | 76 |
| early | FII_index_futures_level | -0.004064 | -0.004986 | -0.000504 | 0.000000 | 83 |
| early | index_futures_detail_hhi_z | 0.003973 | 0.000881 | 0.005094 | 1.000000 | 83 |
| later | index_futures_disagree | 0.003827 | 0.001886 | 0.004396 | 0.986842 | 76 |
| early | index_futures_disagree | 0.003290 | 0.000343 | 0.004096 | 1.000000 | 83 |
| later | DII_index_futures_d5 | 0.003267 | 0.002783 | 0.004191 | 1.000000 | 76 |
| later | innovation_dii | 0.003233 | 0.002235 | 0.003473 | 1.000000 | 76 |
| early | index_calls_disagree | 0.002975 | 0.000406 | 0.004065 | 1.000000 | 83 |
| early | innovation_dii | 0.002088 | -0.000264 | 0.002257 | 0.831325 | 83 |
| early | DII_index_futures_d5 | 0.002023 | -0.000236 | 0.002641 | 0.819277 | 83 |

[native-mechanism-cases.csv.gz](native-mechanism-cases.csv.gz) · [mechanism-regime-comparisons.csv](mechanism-regime-comparisons.csv) · [coefficient-stability.csv](coefficient-stability.csv) · [native-fit-receipts.ndjson.gz](native-fit-receipts.ndjson.gz) · [native-audit-cohort-and-omission.csv](native-audit-cohort-and-omission.csv) · [all-disjoint-window-phases.csv](all-disjoint-window-phases.csv)
