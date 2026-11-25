# V20 Validation And Falsification

Fit indices are chronological and have training outcomes strictly before the decision day. The data and fit artifacts preserve dated availability, training-only preprocessing and expiry screens. The verification passed 12 duplicate-feature, duplicate-expert and future-poisoning sentinels, and checked 482 native clocks. Sensitivities include lagged forecasts, randomized input blocks, randomized residual targets, a bias-only intercept, no bias, fixed fractional correction, shorter histories, omitted training episodes and an eight-calendar-day embargo. Temporal models include a deliberate independence variant.

| horizon | model | parent | metric | n | disjoint | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | v19_position_native | exact_v14 | brier | 223 | 45 | -0.007436 | -0.036885 | 0.022014 |
| 5 | v19_position_native | v18_corporate_native | brier | 223 | 45 | -0.013435 | -0.039873 | 0.013003 |
| 5 | price_reaction | exact_v14 | brier | 223 | 45 | 0.006114 | -0.014795 | 0.027023 |
| 5 | price_reaction | v18_corporate_native | brier | 223 | 45 | 0.000115 | -0.019267 | 0.019497 |
| 5 | smooth5 | exact_v14 | brier | 223 | 45 | -0.003040 | -0.034799 | 0.028720 |
| 5 | smooth5 | v18_corporate_native | brier | 223 | 45 | -0.009039 | -0.020128 | 0.002050 |
| 5 | omit_latest_21_training_origins | exact_v14 | brier | 202 | 41 | 0.008968 | -0.014808 | 0.032743 |
| 5 | omit_latest_21_training_origins | v18_corporate_native | brier | 202 | 41 | 0.000387 | -0.017387 | 0.018160 |
| 5 | eight_calendar_day_embargo | exact_v14 | brier | 217 | 44 | 0.008056 | -0.020966 | 0.037078 |
| 5 | eight_calendar_day_embargo | v18_corporate_native | brier | 217 | 44 | 0.000131 | -0.017201 | 0.017464 |
| 5 | v19_position_native | exact_v14 | crps | 223 | 45 | -0.000107 | -0.001085 | 0.000872 |
| 5 | v19_position_native | v18_corporate_native | crps | 223 | 45 | -0.000272 | -0.001096 | 0.000552 |
| 5 | price_reaction | exact_v14 | crps | 223 | 45 | 0.000236 | -0.000673 | 0.001146 |
| 5 | price_reaction | v18_corporate_native | crps | 223 | 45 | 0.000071 | -0.000969 | 0.001112 |
| 5 | smooth5 | exact_v14 | crps | 223 | 45 | -0.000136 | -0.001273 | 0.001001 |
| 5 | smooth5 | v18_corporate_native | crps | 223 | 45 | -0.000301 | -0.000726 | 0.000124 |
| 5 | omit_latest_21_training_origins | exact_v14 | crps | 202 | 41 | 0.000240 | -0.000898 | 0.001378 |
| 5 | omit_latest_21_training_origins | v18_corporate_native | crps | 202 | 41 | 0.000028 | -0.000562 | 0.000617 |
| 5 | eight_calendar_day_embargo | exact_v14 | crps | 217 | 44 | 0.000147 | -0.001131 | 0.001424 |
| 5 | eight_calendar_day_embargo | v18_corporate_native | crps | 217 | 44 | -0.000068 | -0.000658 | 0.000522 |
| 21 | v19_position_native | exact_v14 | brier | 159 | 8 | 0.022988 | -0.086520 | 0.132495 |
| 21 | smooth5 | exact_v14 | brier | 159 | 8 | 0.022438 | -0.079499 | 0.124375 |
| 21 | omit_latest_21_training_origins | exact_v14 | brier | 138 | 7 | 0.011465 | -0.124885 | 0.147814 |
| 21 | eight_calendar_day_embargo | exact_v14 | brier | 154 | 8 | 0.023890 | -0.091756 | 0.139536 |

| metric | observed | null median | null 95 | exceedances | runs | rank tail |
| --- | --- | --- | --- | --- | --- | --- |
| brier_gain | 0.015119 | 0.017247 | 0.043132 | 13 | 23 | 0.583333 |
| crps_gain | 0.001628 | 0.000844 | 0.002221 | 6 | 23 | 0.291667 |

| horizon | model | metric | phases | low | high |
| --- | --- | --- | --- | --- | --- |
| 5 | v18_corporate_native | brier | 5 | -0.003319 | 0.018439 |
| 5 | v18_corporate_native | crps | 5 | 0.000069 | 0.000192 |
| 5 | v19_position_native | brier | 5 | -0.012397 | 0.000216 |
| 5 | v19_position_native | crps | 5 | -0.000241 | 0.000145 |
| 21 | v18_corporate_native | brier | 21 | -0.058851 | 0.033413 |
| 21 | v18_corporate_native | crps | 21 | -0.001153 | 0.000367 |
| 21 | v19_position_native | brier | 21 | -0.051274 | 0.061405 |
| 21 | v19_position_native | crps | 21 | -0.001556 | 0.003834 |

Every disjoint-window phase is available, alongside earlier and later populations. Further diagnostics remove each calendar month and one extreme realized 21-origin episode. The independent V19 timing replay repeats the favorable-block removal. Max-statistic bands address the V20 family of comparisons, with the same historical years repeatedly examined across earlier versions.

[validation-receipt.json](validation-receipt.json) · [future-information-sentinels.csv](future-information-sentinels.csv) · [native-source-clock-audit.csv](native-source-clock-audit.csv) · [all-disjoint-window-phases.csv](all-disjoint-window-phases.csv) · [episode-omission-sensitivity.csv](episode-omission-sensitivity.csv) · [matched-block-intervals.csv.gz](matched-block-intervals.csv.gz) · [v20-refit-null-summary.csv](v20-refit-null-summary.csv) · [v20-refit-null-cases.csv.gz](v20-refit-null-cases.csv.gz)
