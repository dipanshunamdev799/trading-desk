# V23 Reproduction and benchmarks

Replayed 75,891 V22 law summaries from stored weights and recomputed 3,157
original case scores in full. Independently checked the V22 research index, all 17 reports, the preregistration,
verification receipt, 249 archived files and 14 source files against the frozen manifest.
Weekly and monthly comparisons preserve their literal original target sessions and published information clocks.

| horizon | clock | model | n | mean up | brier | crps |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | anchor_asymmetry | 265 | 0.497072 | 0.222129 | 0.010167 |
| 5 | native_0910 | exact_v14 | 265 | 0.517051 | 0.228529 | 0.010457 |
| 5 | native_0910 | omit_latest_21_training_origins | 265 | 0.488924 | 0.221693 | 0.010274 |
| 5 | native_0910 | parent_location_domestic_only | 265 | 0.509821 | 0.222142 | 0.010121 |
| 5 | native_0910 | secondary_location_beyond_gift | 265 | 0.512326 | 0.220133 | 0.010180 |
| 5 | native_0910 | secondary_location_domestic_only | 265 | 0.503110 | 0.220368 | 0.010130 |
| 5 | native_0910 | v18_corporate_native | 265 | 0.480288 | 0.223481 | 0.010318 |
| 21 | native_0910 | anchor_aggregate_position | 217 | 0.579178 | 0.223819 | 0.023184 |
| 21 | native_0910 | exact_v14 | 217 | 0.481432 | 0.245042 | 0.024989 |
| 21 | native_0910 | parent_mixture_foreign_tail | 217 | 0.569929 | 0.223431 | 0.023174 |
| 21 | native_0910 | smooth5 | 217 | 0.514950 | 0.228602 | 0.023786 |
| 21 | native_0910 | v19_position_native | 217 | 0.514707 | 0.228199 | 0.024010 |
| 21 | preauction_0855 | archived_same_clock | 217 | 0.500000 | 0.250000 | 0.025543 |

The brief listed a weekly domestic-only Brier of 0.220368 and CRPS of 0.010121 together. The law records assign them to
different models. The V20-parent domestic correction, `secondary_location_domestic_only`, scored 0.220368 Brier and
0.010130 CRPS. The V21-parent domestic correction, `parent_location_domestic_only`, scored 0.222142 Brier and
0.010121 CRPS. The V20-parent correction beyond GIFT scored 0.220133 Brier and 0.010180 CRPS. The archived monthly neutral
law assigns exactly 50% up probability at 08:55 and scores 0.250000 Brier and 0.025543 CRPS.

## Protected path and source audit

| horizon | model | n | range crps | drawdown crps |
| --- | --- | --- | --- | --- |
| 5 | analogue_global_on_IV_GJR | 265 | 0.006155 | 0.006205 |
| 5 | analogue_india_on_IV_GJR | 265 | 0.006159 | 0.006139 |
| 5 | same_clock_GJR | 265 | 0.006493 | 0.005956 |
| 21 | analogue_global_on_IV_GJR | 217 | 0.014195 | 0.013894 |
| 21 | analogue_india_on_IV_GJR | 217 | 0.014409 | 0.013974 |
| 21 | same_clock_GJR | 217 | 0.015488 | 0.014113 |

| horizon | model | n | range crps |
| --- | --- | --- | --- |
| 5 | all_matched_sources | 265 | 0.006155 |
| 5 | drop_low_agreement_sources | 265 | 0.006196 |
| 21 | all_matched_sources | 217 | 0.014195 |
| 21 | drop_low_agreement_sources | 217 | 0.014260 |

## Protection against favorable subperiods and foreign-prior placebos

| horizon | parent | model | metric | lo | hi | omitted gain | remaining gain | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | anchor_asymmetry | secondary_location_beyond_gift | brier | 2026-03-13 | 2026-04-16 | 0.057255 | -0.002760 | 265 |
| 5 | anchor_asymmetry | secondary_location_beyond_gift | crps | 2026-03-13 | 2026-04-16 | 0.002032 | -0.000189 | 265 |
| 21 | anchor_aggregate_position | parent_mixture_foreign_tail | brier | 2026-08-28 | 2026-09-28 | 0.052741 | -0.005222 | 217 |
| 21 | anchor_aggregate_position | parent_mixture_foreign_tail | crps | 2026-02-04 | 2026-03-05 | 0.002723 | -0.000280 | 217 |

| horizon | model | n | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | adapt_foreign_prior_120 | 265 | 0.262467 | 0.011696 |
| 5 | adapt_foreign_prior_60 | 265 | 0.317882 | 0.012780 |
| 5 | adapt_foreign_random_120 | 265 | 0.262506 | 0.011710 |
| 5 | adapt_foreign_random_60 | 265 | 0.319098 | 0.012790 |
| 5 | adapt_strong_zero_120 | 265 | 0.258903 | 0.011490 |
| 5 | adapt_strong_zero_60 | 265 | 0.302094 | 0.012464 |
| 5 | adapt_zero_centered_120 | 265 | 0.261919 | 0.011627 |
| 5 | adapt_zero_centered_60 | 265 | 0.316040 | 0.012732 |
| 21 | adapt_foreign_prior_120 | 217 | 0.376173 | 0.037749 |
| 21 | adapt_foreign_prior_60 | 217 | 0.449847 | 0.042019 |
| 21 | adapt_foreign_random_120 | 217 | 0.377161 | 0.037859 |
| 21 | adapt_foreign_random_60 | 217 | 0.450697 | 0.042050 |
| 21 | adapt_strong_zero_120 | 217 | 0.345147 | 0.032518 |
| 21 | adapt_strong_zero_60 | 217 | 0.420411 | 0.038516 |
| 21 | adapt_zero_centered_120 | 217 | 0.372348 | 0.036991 |
| 21 | adapt_zero_centered_60 | 217 | 0.446524 | 0.041683 |

V11 exact-law ensemble benchmarks remain in their original archive clock. The 08:55, 09:10, prior-evening and post-open tracks remain separately identifiable.

[exact-v22-benchmark-cases.csv.gz](exact-v22-benchmark-cases.csv.gz) · [predecessor-verification.json](predecessor-verification.json) · [v11-exact-ensemble-benchmarks.csv](v11-exact-ensemble-benchmarks.csv) · [Original V22 research index](../../../nifty_forecast_v22/2026-11-26/run-001/NIFTY_V22_RESEARCH.md)

[Back to the research index](NIFTY_V23_RESEARCH.md)
