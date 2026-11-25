# V15 market-window and episode evidence

Chronological origin and unique fixed endpoint counts describe forecast coverage. After aligning matched methods at the exact checkpoint, the comparison collapses updates within each original window. Fixed-date groups retain the target's shared realized value. Phase-indexed disjoint comparisons use calendar/trading order and label windows (origin, target]. Resampling uses 1,500 paired circular block draws at lengths of 5, 10, 21 and 42 original windows. At 10 and 21, bands use the maximum absolute standardized bootstrap deviation inside the registered comparison family, metric and checkpoint. Fixed-date clusters, disjoint calendar buckets, paired source cohorts and leave-month/event-out results quantify sensitivity. The benchmark history through V14 remains exposed.

## Dependence units

| horizon | rolling | fixed targets | greedily disjoint | early | later | updates | calendar match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 265 | 265 | 53 | 173 | 92 | 1,325 | 263 |
| 21 | 217 | 217 | 11 | 141 | 76 | 4,557 | 203 |

## Distinct extreme episodes

| horizon | event | eligible | count | distinct episodes | positive disjoint | eligible disjoint |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | upper_fixed | 265 | 23 | 6 | 8 | 53 |
| 5 | lower_fixed | 265 | 10 | 4 | 5 | 53 |
| 5 | range_fixed | 265 | 19 | 4 | 7 | 53 |
| 5 | expand | 265 | 87 | 23 | 28 | 53 |
| 5 | persist_up | 265 | 19 | 7 | 8 | 53 |
| 5 | persist_down | 265 | 18 | 8 | 9 | 53 |
| 5 | gap_fixed | 265 | 49 | 4 | 10 | 53 |
| 21 | upper_fixed | 217 | 18 | 2 | 2 | 11 |
| 21 | lower_fixed | 217 | 29 | 2 | 2 | 11 |
| 21 | range_fixed | 217 | 34 | 2 | 3 | 11 |
| 21 | expand | 217 | 81 | 3 | 6 | 11 |
| 21 | persist_up | 217 | 5 | 2 | 2 | 11 |
| 21 | persist_down | 217 | 5 | 2 | 2 | 11 |
| 21 | gap_fixed | 217 | 101 | 2 | 7 | 11 |

## Disjoint phase sensitivity

| horizon | checkpoint | candidate | metric | phases | smallest n | largest n | positive phases | worst gain | best gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | issue | analogue | brier | 5 | 53 | 53 | 1 | -0.018245 | 0.006220 |
| 5 | issue | analogue | range_crps | 5 | 53 | 53 | 1 | -0.000993 | 0.000256 |
| 5 | issue | domestic | brier | 5 | 53 | 53 | 2 | -0.009601 | 0.006381 |
| 5 | issue | domestic | range_crps | 5 | 53 | 53 | 1 | -0.000429 | 0.000069 |
| 5 | issue | incremental | brier | 5 | 53 | 53 | 2 | -0.000935 | 0.000851 |
| 5 | issue | incremental | range_crps | 5 | 53 | 53 | 4 | -0.000080 | 0.000108 |
| 5 | issue | refit | brier | 5 | 53 | 53 | 3 | -0.012967 | 0.010426 |
| 5 | issue | refit | range_crps | 5 | 53 | 53 | 1 | -0.000488 | 0.000045 |
| 5 | issue | vol_state | brier | 5 | 53 | 53 | 0 | -0.002787 | -0.000677 |
| 5 | issue | vol_state | range_crps | 5 | 53 | 53 | 2 | -0.000230 | 0.000207 |
| 5 | updated | analogue | brier | 5 | 53 | 53 | 1 | -0.009438 | 0.004311 |
| 5 | updated | analogue | range_crps | 5 | 53 | 53 | 1 | -0.000349 | 0.000058 |
| 5 | updated | domestic | brier | 5 | 53 | 53 | 4 | -0.005051 | 0.008280 |
| 5 | updated | domestic | range_crps | 5 | 53 | 53 | 0 | -0.000293 | -0.000018 |
| 5 | updated | incremental | brier | 5 | 53 | 53 | 2 | -0.001085 | 0.000554 |
| 5 | updated | incremental | range_crps | 5 | 53 | 53 | 3 | -0.000062 | 0.000081 |
| 5 | updated | refit | brier | 5 | 53 | 53 | 3 | -0.008211 | 0.011308 |
| 5 | updated | refit | range_crps | 5 | 53 | 53 | 0 | -0.000365 | -0.000044 |
| 5 | updated | vol_state | brier | 5 | 53 | 53 | 0 | -0.001967 | -0.000060 |
| 5 | updated | vol_state | range_crps | 5 | 53 | 53 | 3 | -0.000130 | 0.000120 |
| 21 | issue | analogue | brier | 21 | 10 | 11 | 1 | -0.096013 | 0.004706 |
| 21 | issue | analogue | range_crps | 21 | 10 | 11 | 2 | -0.003669 | 0.000902 |
| 21 | issue | domestic | brier | 21 | 10 | 11 | 8 | -0.047207 | 0.029855 |
| 21 | issue | domestic | range_crps | 21 | 10 | 11 | 0 | -0.003348 | -0.001787 |
| 21 | issue | incremental | brier | 21 | 10 | 11 | 11 | -0.003229 | 0.004669 |
| 21 | issue | incremental | range_crps | 21 | 10 | 11 | 21 | 0.000387 | 0.001434 |
| 21 | issue | refit | brier | 21 | 10 | 11 | 7 | -0.078641 | 0.036772 |
| 21 | issue | refit | range_crps | 21 | 10 | 11 | 0 | -0.002399 | -0.001148 |
| 21 | issue | vol_state | brier | 21 | 10 | 11 | 6 | -0.011008 | 0.003558 |
| 21 | issue | vol_state | range_crps | 21 | 10 | 11 | 17 | -0.000881 | 0.002212 |
| 21 | updated | analogue | brier | 21 | 10 | 11 | 0 | -0.037639 | -0.005538 |
| 21 | updated | analogue | range_crps | 21 | 10 | 11 | 0 | -0.001669 | -0.000238 |
| 21 | updated | domestic | brier | 21 | 10 | 11 | 6 | -0.027204 | 0.012032 |
| 21 | updated | domestic | range_crps | 21 | 10 | 11 | 0 | -0.001202 | -0.000392 |
| 21 | updated | incremental | brier | 21 | 10 | 11 | 7 | -0.013811 | 0.006046 |
| 21 | updated | incremental | range_crps | 21 | 10 | 11 | 21 | 0.000002 | 0.000399 |
| 21 | updated | refit | brier | 21 | 10 | 11 | 6 | -0.040637 | 0.012416 |
| 21 | updated | refit | range_crps | 21 | 10 | 11 | 0 | -0.001099 | -0.000261 |
| 21 | updated | vol_state | brier | 21 | 10 | 11 | 8 | -0.006683 | 0.004722 |
| 21 | updated | vol_state | range_crps | 21 | 10 | 11 | 16 | -0.000288 | 0.000456 |

## Deleting target months and overlapping extreme episodes

| horizon | checkpoint | candidate | metric | deletion type | exclusions | gain min | gain max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | issue | analogue | brier | overlapping_extreme_episode | 14 | -0.010244 | -0.002085 |
| 5 | issue | analogue | brier | target_month | 14 | -0.010971 | -0.001781 |
| 5 | issue | analogue | range_crps | overlapping_extreme_episode | 14 | -0.000459 | -0.000120 |
| 5 | issue | analogue | range_crps | target_month | 14 | -0.000490 | -0.000183 |
| 5 | issue | incremental | brier | overlapping_extreme_episode | 14 | -0.000326 | 0.000212 |
| 5 | issue | incremental | brier | target_month | 14 | -0.000279 | 0.000172 |
| 5 | issue | incremental | range_crps | overlapping_extreme_episode | 14 | -0.000012 | 0.000107 |
| 5 | issue | incremental | range_crps | target_month | 14 | -0.000029 | 0.000106 |
| 5 | issue | refit | brier | overlapping_extreme_episode | 14 | -0.002590 | 0.008360 |
| 5 | issue | refit | brier | target_month | 14 | -0.004447 | 0.005603 |
| 5 | issue | refit | range_crps | overlapping_extreme_episode | 14 | -0.000306 | -0.000172 |
| 5 | issue | refit | range_crps | target_month | 14 | -0.000312 | -0.000164 |
| 5 | issue | vol_state | brier | overlapping_extreme_episode | 14 | -0.001916 | -0.000718 |
| 5 | issue | vol_state | brier | target_month | 14 | -0.001859 | -0.000483 |
| 5 | issue | vol_state | range_crps | overlapping_extreme_episode | 14 | -0.000063 | 0.000058 |
| 5 | issue | vol_state | range_crps | target_month | 14 | -0.000100 | 0.000056 |
| 5 | updated | analogue | brier | overlapping_extreme_episode | 14 | -0.004928 | -0.002333 |
| 5 | updated | analogue | brier | target_month | 14 | -0.004897 | -0.002568 |
| 5 | updated | analogue | range_crps | overlapping_extreme_episode | 14 | -0.000202 | -0.000089 |
| 5 | updated | analogue | range_crps | target_month | 14 | -0.000211 | -0.000106 |
| 5 | updated | incremental | brier | overlapping_extreme_episode | 14 | -0.000665 | -0.000199 |
| 5 | updated | incremental | brier | target_month | 14 | -0.000689 | -0.000157 |
| 5 | updated | incremental | range_crps | overlapping_extreme_episode | 14 | 0.000002 | 0.000033 |
| 5 | updated | incremental | range_crps | target_month | 14 | -0.000006 | 0.000035 |
| 5 | updated | refit | brier | overlapping_extreme_episode | 14 | 0.000223 | 0.003431 |
| 5 | updated | refit | brier | target_month | 14 | 0.000288 | 0.004294 |
| 5 | updated | refit | range_crps | overlapping_extreme_episode | 14 | -0.000220 | -0.000167 |
| 5 | updated | refit | range_crps | target_month | 14 | -0.000249 | -0.000174 |
| 5 | updated | vol_state | brier | overlapping_extreme_episode | 14 | -0.001520 | -0.000684 |
| 5 | updated | vol_state | brier | target_month | 14 | -0.001347 | -0.000771 |
| 5 | updated | vol_state | range_crps | overlapping_extreme_episode | 14 | -0.000019 | 0.000023 |
| 5 | updated | vol_state | range_crps | target_month | 14 | -0.000037 | 0.000024 |
| 21 | issue | analogue | brier | overlapping_extreme_episode | 6 | -0.060120 | -0.055534 |
| 21 | issue | analogue | brier | target_month | 12 | -0.065686 | -0.040898 |
| 21 | issue | analogue | range_crps | overlapping_extreme_episode | 6 | -0.002636 | 0.000470 |
| 21 | issue | analogue | range_crps | target_month | 12 | -0.002592 | -0.001151 |
| 21 | issue | incremental | brier | overlapping_extreme_episode | 6 | -0.000192 | 0.000379 |
| 21 | issue | incremental | brier | target_month | 12 | -0.000148 | 0.000299 |
| 21 | issue | incremental | range_crps | overlapping_extreme_episode | 6 | 0.000469 | 0.001048 |
| 21 | issue | incremental | range_crps | target_month | 12 | 0.000501 | 0.000916 |
| 21 | issue | refit | brier | overlapping_extreme_episode | 6 | -0.036829 | 0.018060 |
| 21 | issue | refit | brier | target_month | 12 | -0.023085 | -0.002549 |
| 21 | issue | refit | range_crps | overlapping_extreme_episode | 6 | -0.002526 | 0.000249 |
| 21 | issue | refit | range_crps | target_month | 12 | -0.002181 | -0.000777 |
| 21 | issue | vol_state | brier | overlapping_extreme_episode | 6 | -0.003442 | -0.000662 |
| 21 | issue | vol_state | brier | target_month | 12 | -0.005917 | -0.001505 |
| 21 | issue | vol_state | range_crps | overlapping_extreme_episode | 6 | 0.000680 | 0.001991 |
| 21 | issue | vol_state | range_crps | target_month | 12 | -0.000198 | 0.001535 |
| 21 | updated | analogue | brier | overlapping_extreme_episode | 6 | -0.022800 | -0.018866 |
| 21 | updated | analogue | brier | target_month | 12 | -0.021673 | -0.013405 |
| 21 | updated | analogue | range_crps | overlapping_extreme_episode | 6 | -0.001213 | -0.000352 |
| 21 | updated | analogue | range_crps | target_month | 12 | -0.001092 | -0.000637 |
| 21 | updated | incremental | brier | overlapping_extreme_episode | 6 | -0.004023 | -0.001487 |
| 21 | updated | incremental | brier | target_month | 12 | -0.003070 | -0.001063 |
| 21 | updated | incremental | range_crps | overlapping_extreme_episode | 6 | 0.000126 | 0.000295 |
| 21 | updated | incremental | range_crps | target_month | 12 | 0.000137 | 0.000266 |
| 21 | updated | refit | brier | overlapping_extreme_episode | 6 | -0.021019 | 0.002563 |
| 21 | updated | refit | brier | target_month | 12 | -0.014926 | -0.003321 |
| 21 | updated | refit | range_crps | overlapping_extreme_episode | 6 | -0.001037 | 0.000021 |
| 21 | updated | refit | range_crps | target_month | 12 | -0.000899 | -0.000467 |
| 21 | updated | vol_state | brier | overlapping_extreme_episode | 6 | -0.002129 | 0.000504 |
| 21 | updated | vol_state | brier | target_month | 12 | -0.002444 | -0.000708 |
| 21 | updated | vol_state | range_crps | overlapping_extreme_episode | 6 | 0.000081 | 0.000503 |
| 21 | updated | vol_state | range_crps | target_month | 12 | -0.000184 | 0.000297 |

[Complete original windows](original-windows.csv) [Per-endpoint and grouped scores](endpoint-cluster-evidence.csv.gz) [All phases](disjoint-phase-evidence.csv) [All deletions](leave-group-out-evidence.csv) [Dependence-aware comparisons](matched-window-evidence.csv) [V14 independent episode definitions](../../../nifty_forecast_v14/2026-11-25/run-001/distinct-extreme-episodes.csv)
