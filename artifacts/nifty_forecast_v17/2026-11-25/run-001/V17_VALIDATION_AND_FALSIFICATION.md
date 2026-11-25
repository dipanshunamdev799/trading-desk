# NIFTY V17 — Validation and falsification

Across 10 cutoff, target and date stress tests, 296 individual model distributions stayed exactly invariant after altering later inputs and outcomes that had yet to mature. All 3,200 cash decision snapshots and 125,125 stock/index snapshots passed completed-bar margins. Each official derivative or options feature with a recorded session is strictly earlier than the intraday decision. Historical opening examples link to an eligible mark and pre-auction forecast. The previous-close originals pass the guarded label-end check. The five- and 21-session V14 realized returns agree case by case with V17. Realized volatility and expansion agreed on 960 matched V16 risk cases. The V16 protection check matched 732 archive files and 15 code files, with the inherited hashes for earlier studies retained.

| day | cutoff | target | laws | changed future feature rows | changed unmatured labels | max difference |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-02-09 | 09:25 | r30 | 35 | 189 | 190 | 0 |
| 2026-08-10 | 09:25 | r30 | 35 | 67 | 68 | 0 |
| 2026-02-09 | 10:20 | regular_residual | 36 | 189 | 190 | 0 |
| 2026-08-10 | 10:20 | regular_residual | 36 | 67 | 68 | 0 |
| 2026-02-09 | 10:20 | remaining_21 | 36 | 189 | 191 | 0 |
| 2026-07-29 | 10:20 | remaining_21 | 36 | 75 | 77 | 0 |
| 2026-02-09 | 09:25 | remaining_vol | 35 | 189 | 190 | 0 |
| 2026-08-10 | 09:25 | remaining_vol | 35 | 67 | 68 | 0 |
| 2026-02-03 | 10:20 | touch_down | 6 | 193 | 194 | 0 |
| 2026-08-12 | 10:20 | touch_down | 6 | 65 | 66 | 0 |

## Falsification suite

The opening suite tests raw mechanical percentage, trailing basis, earlier and delayed quotes, approximate rollover exclusions, stale marks, nonordinary calendar breaks and sensitivity to the largest gaps. Stock checks vary the eligible members, remove one highest-turnover seed per sleeve, screen ex-actions, use training-only sector neutralization, delay the stock input by either a session or an observable earlier checkpoint, reorder feature blocks or chronological residual labels, and remove a training month. Direct feature specifications deduplicate identical columns before fitting. Selectors and fills use matured history. Counterfactual tests within the exposed dates help explain fragile associations. Date blocks of **5, 10, 21, 42** use **1,500** resamples and adjust overlapping candidate tests within fixed target and metric families. Beyond-brief claims about order imbalance or historical constituents would require independent sources.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | r30 | stock_delay1 | frozen_parent_residual_history | crps | 257 | 257 | 0.001262 | 0.001256 | -5.28e-06 | -0.000023 | 0.000012 |
| 09:25 | r30 | stock_block_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.001265 | 0.001256 | -9.07e-06 | -0.000024 | 6.34e-06 |
| 09:25 | r30 | residual_label_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.001259 | 0.001256 | -2.44e-06 | -0.000013 | 8.43e-06 |
| 09:25 | r30 | stock_without_heavy | frozen_parent_residual_history | crps | 257 | 257 | 0.001262 | 0.001256 | -5.57e-06 | -0.000014 | 2.41e-06 |
| 09:25 | r30 | stock_random_subset1 | frozen_parent_residual_history | crps | 257 | 257 | 0.001258 | 0.001256 | -2.05e-06 | -9.98e-06 | 5.88e-06 |
| 09:25 | r30 | stock_random_subset2 | frozen_parent_residual_history | crps | 257 | 257 | 0.001261 | 0.001256 | -4.87e-06 | -0.000013 | 3.76e-06 |
| 09:25 | r30 | action_screen_stock | frozen_parent_residual_history | crps | 257 | 257 | 0.001261 | 0.001256 | -4.90e-06 | -0.000013 | 3.66e-06 |
| 09:25 | r30 | proxy_open_surprise | frozen_parent_residual_history | crps | 248 | 248 | 0.001276 | 0.001280 | 3.24e-06 | -0.000018 | 0.000024 |
| 09:25 | r30 | surprise_delayed | frozen_parent_residual_history | crps | 240 | 240 | 0.001297 | 0.001292 | -5.01e-06 | -0.000019 | 8.97e-06 |
| 09:25 | r30 | training_month_removed | frozen_parent_residual_history | crps | 257 | 257 | 0.001264 | 0.001256 | -7.39e-06 | -0.000022 | 7.45e-06 |
| 09:25 | regular_residual | stock_delay1 | frozen_parent_residual_history | crps | 257 | 257 | 0.003545 | 0.003528 | -0.000017 | -0.000062 | 0.000028 |
| 09:25 | regular_residual | stock_block_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.003542 | 0.003528 | -0.000014 | -0.000055 | 0.000027 |
| 09:25 | regular_residual | residual_label_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.003536 | 0.003528 | -7.99e-06 | -0.000053 | 0.000037 |
| 09:25 | regular_residual | stock_without_heavy | frozen_parent_residual_history | crps | 257 | 257 | 0.003540 | 0.003528 | -0.000012 | -0.000024 | 1.92e-07 |
| 09:25 | regular_residual | stock_random_subset1 | frozen_parent_residual_history | crps | 257 | 257 | 0.003542 | 0.003528 | -0.000014 | -0.000025 | -2.49e-06 |
| 09:25 | regular_residual | stock_random_subset2 | frozen_parent_residual_history | crps | 257 | 257 | 0.003534 | 0.003528 | -5.73e-06 | -0.000025 | 0.000013 |
| 09:25 | regular_residual | action_screen_stock | frozen_parent_residual_history | crps | 257 | 257 | 0.003541 | 0.003528 | -0.000013 | -0.000027 | 1.35e-06 |
| 09:25 | regular_residual | proxy_open_surprise | frozen_parent_residual_history | crps | 248 | 248 | 0.003518 | 0.003517 | -9.57e-07 | -0.000027 | 0.000025 |
| 09:25 | regular_residual | surprise_delayed | frozen_parent_residual_history | crps | 240 | 240 | 0.003537 | 0.003549 | 0.000012 | -0.000040 | 0.000065 |
| 09:25 | regular_residual | training_month_removed | frozen_parent_residual_history | crps | 257 | 257 | 0.003552 | 0.003528 | -0.000024 | -0.000052 | 3.95e-06 |
| 09:25 | remaining_21 | stock_delay1 | frozen_parent_residual_history | crps | 238 | 12 | 0.031389 | 0.029515 | -0.001874 | -0.005167 | 0.001418 |
| 09:25 | remaining_21 | stock_block_shuffle | frozen_parent_residual_history | crps | 238 | 12 | 0.031387 | 0.029515 | -0.001872 | -0.004897 | 0.001153 |
| 09:25 | remaining_21 | residual_label_shuffle | frozen_parent_residual_history | crps | 238 | 12 | 0.031604 | 0.029515 | -0.002089 | -0.005112 | 0.000935 |
| 09:25 | remaining_21 | stock_without_heavy | frozen_parent_residual_history | crps | 238 | 12 | 0.031558 | 0.029515 | -0.002043 | -0.005203 | 0.001117 |
| 09:25 | remaining_21 | stock_random_subset1 | frozen_parent_residual_history | crps | 238 | 12 | 0.031394 | 0.029515 | -0.001879 | -0.004970 | 0.001211 |
| 09:25 | remaining_21 | stock_random_subset2 | frozen_parent_residual_history | crps | 238 | 12 | 0.031355 | 0.029515 | -0.001840 | -0.004769 | 0.001090 |
| 09:25 | remaining_21 | action_screen_stock | frozen_parent_residual_history | crps | 238 | 12 | 0.031496 | 0.029515 | -0.001981 | -0.005184 | 0.001222 |
| 09:25 | remaining_21 | proxy_open_surprise | frozen_parent_residual_history | crps | 230 | 12 | 0.031119 | 0.030172 | -0.000947 | -0.003147 | 0.001253 |
| 09:25 | remaining_21 | surprise_delayed | frozen_parent_residual_history | crps | 223 | 12 | 0.032473 | 0.030747 | -0.001726 | -0.004605 | 0.001154 |
| 09:25 | remaining_21 | training_month_removed | frozen_parent_residual_history | crps | 238 | 12 | 0.030760 | 0.029515 | -0.001245 | -0.004549 | 0.002059 |
| 09:25 | remaining_vol | stock_delay1 | frozen_parent_residual_history | crps | 257 | 257 | 0.000999 | 0.000989 | -9.65e-06 | -0.000096 | 0.000077 |
| 09:25 | remaining_vol | stock_block_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.001038 | 0.000989 | -0.000049 | -0.000130 | 0.000032 |
| 09:25 | remaining_vol | residual_label_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.001026 | 0.000989 | -0.000036 | -0.000116 | 0.000044 |
| 09:25 | remaining_vol | stock_without_heavy | frozen_parent_residual_history | crps | 257 | 257 | 0.001019 | 0.000989 | -0.000029 | -0.000106 | 0.000048 |
| 09:25 | remaining_vol | stock_random_subset1 | frozen_parent_residual_history | crps | 257 | 257 | 0.001016 | 0.000989 | -0.000027 | -0.000106 | 0.000052 |
| 09:25 | remaining_vol | stock_random_subset2 | frozen_parent_residual_history | crps | 257 | 257 | 0.001019 | 0.000989 | -0.000030 | -0.000111 | 0.000051 |
| 09:25 | remaining_vol | action_screen_stock | frozen_parent_residual_history | crps | 257 | 257 | 0.001013 | 0.000989 | -0.000024 | -0.000102 | 0.000054 |
| 09:25 | remaining_vol | proxy_open_surprise | frozen_parent_residual_history | crps | 248 | 248 | 0.000970 | 0.000948 | -0.000022 | -0.000072 | 0.000029 |
| 09:25 | remaining_vol | surprise_delayed | frozen_parent_residual_history | crps | 240 | 240 | 0.000964 | 0.000940 | -0.000024 | -0.000074 | 0.000026 |
| 09:25 | remaining_vol | training_month_removed | frozen_parent_residual_history | crps | 257 | 257 | 0.001000 | 0.000989 | -0.000011 | -0.000098 | 0.000076 |
| 10:20 | r30 | stock_delay1 | frozen_parent_residual_history | crps | 257 | 257 | 0.000815 | 0.000813 | -1.24e-06 | -8.33e-06 | 5.85e-06 |
| 10:20 | r30 | stock_clock_delay | frozen_parent_residual_history | crps | 257 | 257 | 0.000819 | 0.000813 | -6.06e-06 | -0.000014 | 2.15e-06 |
| 10:20 | r30 | stock_block_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.000820 | 0.000813 | -7.11e-06 | -0.000016 | 1.33e-06 |
| 10:20 | r30 | residual_label_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -4.07e-06 | -0.000013 | 5.30e-06 |
| 10:20 | r30 | stock_without_heavy | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -3.49e-06 | -6.04e-06 | -9.39e-07 |
| 10:20 | r30 | stock_random_subset1 | frozen_parent_residual_history | crps | 257 | 257 | 0.000815 | 0.000813 | -2.12e-06 | -6.35e-06 | 2.11e-06 |
| 10:20 | r30 | stock_random_subset2 | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -3.96e-06 | -8.14e-06 | 2.28e-07 |
| 10:20 | r30 | action_screen_stock | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -3.25e-06 | -5.87e-06 | -6.37e-07 |
| 10:20 | r30 | proxy_open_surprise | frozen_parent_residual_history | crps | 248 | 248 | 0.000802 | 0.000801 | -1.41e-06 | -7.44e-06 | 4.62e-06 |
| 10:20 | r30 | surprise_delayed | frozen_parent_residual_history | crps | 240 | 240 | 0.000800 | 0.000797 | -2.85e-06 | -8.54e-06 | 2.84e-06 |
| 10:20 | r30 | training_month_removed | frozen_parent_residual_history | crps | 257 | 257 | 0.000821 | 0.000813 | -7.43e-06 | -0.000017 | 2.13e-06 |
| 10:20 | regular_residual | stock_delay1 | frozen_parent_residual_history | crps | 257 | 257 | 0.002932 | 0.002921 | -0.000010 | -0.000054 | 0.000033 |
| 10:20 | regular_residual | stock_clock_delay | frozen_parent_residual_history | crps | 257 | 257 | 0.002945 | 0.002921 | -0.000023 | -0.000053 | 6.55e-06 |
| 10:20 | regular_residual | stock_block_shuffle | frozen_parent_residual_history | crps | 257 | 257 | 0.002920 | 0.002921 | 9.32e-07 | -0.000057 | 0.000059 |

[Full clock and outcome checks](validation-receipt.json) · [Protected predecessor chain](predecessor-protection.json) · [Future sentinels](future-sentinels.csv) · [Opening sensitivity](opening-clock-sensitivity.csv) · [Random historical subsets](stock-random-subsets.json) · [All falsification comparisons](postopen-matched-evidence.csv)
