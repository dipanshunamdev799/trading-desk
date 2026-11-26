# V22 Transfer validation and falsification

Historical validation uses chronological blocks, whole-country and whole-region exclusion, a fixed July 1, 2026 later
partition for the international task, and the original India cohorts. Within-date label permutations retain common dates.
Other controls use date-block randomization, stale foreign inputs, own-market models, common-factor-only prediction,
highly concentrated market removal, random retrieval, and a duplicated standardized series test. A mechanical feature
copy changed predictions by 8.33e-17. Injecting an extreme future feature changed
earlier certified lookups by 0.00e+00. Every archived analogue member had a fully
matured outcome at the recorded decision cutoff.

Dependence is handled by aggregating international paired losses within dated blocks and by bootstrapping consecutive
Indian origins. India also reports every disjoint phase, high and low regime slices, global episode and calendar month
omissions, and the deletion of the largest favorable and largest absolute market blocks. The issue-time rule excludes labels
whose maturity is equal to the cutoff. The direct foreign and local comparison has the same local feature family.

| horizon | n | disjoint |
| --- | --- | --- |
| 5 | 265 | 53 |
| 21 | 217 | 11 |

## Native 21-origin block bootstrap for selected claims

| horizon | reference | model | metric | n | gain | low | high | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | anchor_asymmetry | parent_location_domestic_only | brier | 265 | -0.000013 | -0.008817 | 0.006996 | -0.012630 | 0.012604 |
| 5 | anchor_asymmetry | secondary_location_beyond_gift | brier | 265 | 0.001996 | -0.011174 | 0.012584 | -0.016475 | 0.020468 |
| 5 | anchor_asymmetry | parent_location_domestic_only | crps | 265 | 0.000046 | -0.000294 | 0.000346 | -0.000432 | 0.000525 |
| 5 | anchor_asymmetry | secondary_location_beyond_gift | crps | 265 | -0.000013 | -0.000480 | 0.000401 | -0.000711 | 0.000685 |
| 5 | omit_latest_21_training_origins | parent_location_domestic_only | brier | 265 | -0.000449 | -0.018024 | 0.015254 | -0.024741 | 0.023843 |
| 5 | omit_latest_21_training_origins | secondary_location_beyond_gift | brier | 265 | 0.001560 | -0.012074 | 0.014184 | -0.018909 | 0.022029 |
| 5 | omit_latest_21_training_origins | parent_location_domestic_only | crps | 265 | 0.000153 | -0.000604 | 0.000933 | -0.000980 | 0.001286 |
| 5 | omit_latest_21_training_origins | secondary_location_beyond_gift | crps | 265 | 0.000094 | -0.000413 | 0.000614 | -0.000650 | 0.000837 |
| 21 | anchor_aggregate_position | parent_mixture_foreign_tail | brier | 217 | 0.000388 | -0.006505 | 0.010429 | -0.012328 | 0.013103 |
| 21 | anchor_aggregate_position | parent_mixture_foreign_tail | crps | 217 | 0.000010 | -0.000600 | 0.000719 | -0.000943 | 0.000963 |
| 21 | eight_calendar_day_embargo | parent_mixture_foreign_tail | brier | 217 | 0.004657 | -0.024426 | 0.030584 | -0.038780 | 0.048093 |
| 21 | eight_calendar_day_embargo | parent_mixture_foreign_tail | crps | 217 | 0.000829 | -0.001188 | 0.002729 | -0.002075 | 0.003733 |

## Influence of the largest episodes

| horizon | model | metric | type | omitted | n | removed gain | remaining gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | parent_location_domestic_only | brier | largest_favorable_21 | 2026-03-13 to 2026-04-16 | 244 | 0.037952 | -0.003281 |
| 5 | parent_location_domestic_only | brier | largest_absolute_market_21 | 2026-10-09 to 2026-11-08 | 244 | 0.012142 | -0.001059 |
| 5 | secondary_location_beyond_gift | brier | largest_favorable_21 | 2026-03-13 to 2026-04-16 | 244 | 0.057255 | -0.002760 |
| 5 | secondary_location_beyond_gift | brier | largest_absolute_market_21 | 2026-10-09 to 2026-11-08 | 244 | -0.000827 | 0.002239 |
| 5 | parent_location_domestic_only | crps | largest_favorable_21 | 2026-03-16 to 2026-04-17 | 244 | 0.001712 | -0.000097 |
| 5 | parent_location_domestic_only | crps | largest_absolute_market_21 | 2026-10-09 to 2026-11-08 | 244 | 0.000416 | 0.000015 |
| 5 | secondary_location_beyond_gift | crps | largest_favorable_21 | 2026-03-13 to 2026-04-16 | 244 | 0.002032 | -0.000189 |
| 5 | secondary_location_beyond_gift | crps | largest_absolute_market_21 | 2026-10-09 to 2026-11-08 | 244 | -0.001851 | 0.000145 |
| 21 | parent_mixture_foreign_tail | brier | largest_favorable_21 | 2026-08-28 to 2026-09-28 | 196 | 0.052741 | -0.005222 |
| 21 | parent_mixture_foreign_tail | brier | largest_absolute_market_21 | 2026-02-04 to 2026-03-05 | 196 | 0.000282 | 0.000399 |
| 21 | parent_mixture_foreign_tail | crps | largest_favorable_21 | 2026-02-04 to 2026-03-05 | 196 | 0.002723 | -0.000280 |
| 21 | parent_mixture_foreign_tail | crps | largest_absolute_market_21 | 2026-02-04 to 2026-03-05 | 196 | 0.002723 | -0.000280 |

## Representative refit and reselection stress test

For each horizon, four simpler residual variants were fit on the original chronological data and independently
refit on 24 blocked training-label permutations. Each draw reselects the strongest member by its own paired score.
The representative null can be centered below zero when an arbitrary correction degrades a strong parent. A small tail
fraction against that null can accompany a negative absolute improvement, as illustrated by monthly MAE.
Bootstrap and permutation evidence apply to the tested arms and these research-exposed dates. They cannot undo the
accumulated search through V1–V22.

| horizon | metric | n | selected model | observed gain | nulls | null median | null p95 | tail fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | 216 | beyond_gift | 0.002325 | 24 | -0.000386 | 0.001317 | 0.080000 |
| 5 | mae | 216 | beyond_gift | 0.000069 | 24 | -0.000035 | 0.000060 | 0.080000 |
| 21 | brier | 152 | domestic | 0.008804 | 24 | -0.005115 | -0.002877 | 0.040000 |
| 21 | mae | 152 | domestic | -0.000982 | 24 | -0.002324 | -0.001760 | 0.040000 |

[leakage-and-duplication-controls.json](leakage-and-duplication-controls.json) · [international-matched-date-intervals.csv.gz](international-matched-date-intervals.csv.gz) · [international-leave-global-episode-out.csv.gz](international-leave-global-episode-out.csv.gz) · [india-search-adjusted-intervals.csv.gz](india-search-adjusted-intervals.csv.gz) · [india-disjoint-phase-results.csv.gz](india-disjoint-phase-results.csv.gz) · [india-episode-omission.csv.gz](india-episode-omission.csv.gz) · [india-regime-sensitivity.csv.gz](india-regime-sensitivity.csv.gz) · [representative-blocked-refit-reselection.csv](representative-blocked-refit-reselection.csv) · [representative-blocked-refit-design.json](representative-blocked-refit-design.json)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
