# V13 Event Conditioned Risk

Scheduled and observed flags distinguish expiry, a completed futures roll, verified policy schedules, partial index reviews, previous cash moves, sector stress, breadth deterioration and IV changes. Large changes use the preceding mature training 80th percentile. The event path model applies a 35% conditional weight after at least 12 prior comparables. Sparse event sets remain descriptive.

| horizon | event | active | model | target | n | disjoint | predicted | observed | loss | loss_type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | breadth_decay | True | har_iv | volatility | 56 | 17 | 0.107995 | 0.116568 | 0.035102 | MAE |
| 5 | breadth_decay | True | iv_nearest | volatility | 56 | 17 | 0.125101 | 0.116568 | 0.037614 | MAE |
| 5 | fomc_during_window | True | har_iv | volatility | 45 | 9 | 0.122171 | 0.133134 | 0.036270 | MAE |
| 5 | fomc_during_window | True | iv_nearest | volatility | 45 | 9 | 0.140840 | 0.133134 | 0.034728 | MAE |
| 5 | global_jump | True | har_iv | volatility | 51 | 18 | 0.142108 | 0.148582 | 0.047263 | MAE |
| 5 | global_jump | True | iv_nearest | volatility | 51 | 18 | 0.153901 | 0.148582 | 0.040059 | MAE |
| 5 | index_review_during_window | True | har_iv | volatility | 5 | 1 | 0.253261 | 0.273066 | 0.061973 | MAE |
| 5 | index_review_during_window | True | iv_nearest | volatility | 5 | 1 | 0.265165 | 0.273066 | 0.057042 | MAE |
| 5 | iv_jump | True | har_iv | volatility | 73 | 26 | 0.155862 | 0.163702 | 0.055007 | MAE |
| 5 | iv_jump | True | iv_nearest | volatility | 73 | 26 | 0.172378 | 0.163702 | 0.047521 | MAE |
| 5 | near_monthly_expiry | True | har_iv | volatility | 25 | 13 | 0.123074 | 0.124599 | 0.025475 | MAE |
| 5 | near_monthly_expiry | True | iv_nearest | volatility | 25 | 13 | 0.138121 | 0.124599 | 0.024560 | MAE |
| 5 | near_weekly_expiry | True | har_iv | volatility | 57 | 43 | 0.117218 | 0.127928 | 0.039095 | MAE |
| 5 | near_weekly_expiry | True | iv_nearest | volatility | 57 | 43 | 0.133012 | 0.127928 | 0.034155 | MAE |
| 5 | prior_move | True | har_iv | volatility | 66 | 29 | 0.149773 | 0.161486 | 0.055113 | MAE |
| 5 | prior_move | True | iv_nearest | volatility | 66 | 29 | 0.165933 | 0.161486 | 0.045581 | MAE |
| 5 | rbi_during_window | True | har_iv | volatility | 30 | 6 | 0.141599 | 0.139864 | 0.036022 | MAE |
| 5 | rbi_during_window | True | iv_nearest | volatility | 30 | 6 | 0.151797 | 0.139864 | 0.035727 | MAE |
| 5 | roll_observed | True | har_iv | volatility | 13 | 13 | 0.124546 | 0.142147 | 0.042627 | MAE |
| 5 | roll_observed | True | iv_nearest | volatility | 13 | 13 | 0.138422 | 0.142147 | 0.034544 | MAE |
| 5 | sector_shock | True | har_iv | volatility | 70 | 33 | 0.131294 | 0.140461 | 0.046677 | MAE |
| 5 | sector_shock | True | iv_nearest | volatility | 70 | 33 | 0.150371 | 0.140461 | 0.042622 | MAE |
| 21 | breadth_decay | True | har_iv | volatility | 24 | 5 | 0.115028 | 0.132188 | 0.036538 | MAE |
| 21 | breadth_decay | True | iv_bracket | volatility | 24 | 5 | 0.130826 | 0.132188 | 0.033280 | MAE |
| 21 | fomc_during_window | True | har_iv | volatility | 146 | 8 | 0.134372 | 0.145197 | 0.056738 | MAE |
| 21 | fomc_during_window | True | iv_bracket | volatility | 146 | 8 | 0.136744 | 0.145197 | 0.041913 | MAE |
| 21 | global_jump | True | har_iv | volatility | 37 | 6 | 0.169192 | 0.163235 | 0.081384 | MAE |
| 21 | global_jump | True | iv_bracket | volatility | 37 | 6 | 0.160299 | 0.163235 | 0.051722 | MAE |
| 21 | index_review_during_window | True | har_iv | volatility | 21 | 1 | 0.153342 | 0.256744 | 0.113661 | MAE |
| 21 | index_review_during_window | True | iv_bracket | volatility | 21 | 1 | 0.185435 | 0.256744 | 0.082413 | MAE |
| 21 | iv_jump | True | har_iv | volatility | 75 | 9 | 0.161194 | 0.160712 | 0.069710 | MAE |
| 21 | iv_jump | True | iv_bracket | volatility | 75 | 9 | 0.159988 | 0.160712 | 0.045919 | MAE |
| 21 | near_monthly_expiry | True | har_iv | volatility | 19 | 7 | 0.138413 | 0.136477 | 0.049871 | MAE |
| 21 | near_monthly_expiry | True | iv_bracket | volatility | 19 | 7 | 0.138832 | 0.136477 | 0.036703 | MAE |
| 21 | near_weekly_expiry | True | har_iv | volatility | 47 | 10 | 0.129765 | 0.137880 | 0.051515 | MAE |
| 21 | near_weekly_expiry | True | iv_bracket | volatility | 47 | 10 | 0.134318 | 0.137880 | 0.037898 | MAE |
| 21 | prior_move | True | har_iv | volatility | 61 | 9 | 0.159723 | 0.172384 | 0.079025 | MAE |
| 21 | prior_move | True | iv_bracket | volatility | 61 | 9 | 0.159911 | 0.172384 | 0.053848 | MAE |
| 21 | rbi_during_window | True | har_iv | volatility | 97 | 6 | 0.132198 | 0.131376 | 0.040927 | MAE |
| 21 | rbi_during_window | True | iv_bracket | volatility | 97 | 6 | 0.138879 | 0.131376 | 0.035980 | MAE |
| 21 | roll_observed | True | har_iv | volatility | 10 | 7 | 0.139668 | 0.141097 | 0.055637 | MAE |
| 21 | roll_observed | True | iv_bracket | volatility | 10 | 7 | 0.141122 | 0.141097 | 0.041465 | MAE |
| 21 | sector_shock | True | har_iv | volatility | 62 | 9 | 0.138078 | 0.159240 | 0.065000 | MAE |
| 21 | sector_shock | True | iv_bracket | volatility | 62 | 9 | 0.146856 | 0.159240 | 0.049459 | MAE |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | event_iv | empirical_exact | high | crps | 265 | 53 | 0.007110 | 0.007726 | 0.000616 | -0.000657 | 0.001888 | -0.000653 | 0.001885 |
| 5 | combined | event_iv | iv_scaled | high | crps | 265 | 53 | 0.007110 | 0.007131 | 0.000021 | -0.000117 | 0.000159 | -0.000125 | 0.000167 |
| 5 | combined | event_iv | empirical_exact | low | crps | 265 | 53 | 0.007291 | 0.007608 | 0.000317 | -0.001346 | 0.001980 | -0.001644 | 0.002278 |
| 5 | combined | event_iv | iv_scaled | low | crps | 265 | 53 | 0.007291 | 0.007327 | 0.000036 | -0.000128 | 0.000200 | -0.000140 | 0.000212 |
| 5 | combined | event_iv | empirical_exact | range | crps | 265 | 53 | 0.005997 | 0.007918 | 0.001922 | -0.001449 | 0.005292 | -0.002266 | 0.006109 |
| 5 | combined | event_iv | iv_scaled | range | crps | 265 | 53 | 0.005997 | 0.005961 | -0.000036 | -0.000200 | 0.000129 | -0.000200 | 0.000128 |
| 5 | combined | event_iv | empirical_exact | touch_family | brier | 265 | 53 | 0.147306 | 0.156019 | 0.008713 | -0.004775 | 0.022201 | -0.007141 | 0.024567 |
| 5 | combined | event_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.147306 | 0.147679 | 0.000373 | -0.002246 | 0.002992 | -0.002119 | 0.002866 |
| 21 | combined | event_iv | empirical_exact | high | crps | 217 | 11 | 0.012425 | 0.014082 | 0.001656 | -0.002402 | 0.005714 | -0.002498 | 0.005810 |
| 21 | combined | event_iv | iv_scaled | high | crps | 217 | 11 | 0.012425 | 0.012385 | -0.000040 | -0.000290 | 0.000209 | -0.000283 | 0.000202 |
| 21 | combined | event_iv | iv_scaled | low | crps | 217 | 11 | 0.020495 | 0.020449 | -0.000046 | -0.000396 | 0.000304 | -0.000435 | 0.000344 |
| 21 | combined | event_iv | empirical_exact | low | crps | 217 | 11 | 0.020495 | 0.019695 | -0.000800 | -0.003903 | 0.002303 | -0.004275 | 0.002674 |
| 21 | combined | event_iv | empirical_exact | range | crps | 217 | 11 | 0.018299 | 0.019522 | 0.001223 | -0.005676 | 0.008122 | -0.006874 | 0.009319 |
| 21 | combined | event_iv | iv_scaled | range | crps | 217 | 11 | 0.018299 | 0.018162 | -0.000137 | -0.000435 | 0.000161 | -0.000422 | 0.000148 |
| 21 | combined | event_iv | empirical_exact | touch_family | brier | 217 | 11 | 0.198598 | 0.206812 | 0.008214 | -0.014524 | 0.030952 | -0.017053 | 0.033481 |
| 21 | combined | event_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.198598 | 0.197163 | -0.001435 | -0.005014 | 0.002145 | -0.004611 | 0.001742 |

[Full volatility, range, movement and ±2% outcome profiles](events-risk-and-path.csv) · [Active origin flags](events.csv) · [Federal Reserve schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) · [RBI schedule](https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62422).
