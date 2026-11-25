# V19 Validation And Falsification

All 49,164 original endpoint case forecasts passed their event-clock and target-maturity guards. Moving-block inference uses 1,500 draws at 5, 10, 21 and 42 sessions. Search-adjusted intervals use maximum standardized deviations across every eligible contrast in the same track, target, decision clock, horizon and primary metric. Published active comparisons use identical dates. Full intended cohorts include their prespecified fallbacks.

| horizon | model | parent | metric | n | disjoint | gain | low | high | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_plus_positions | V14_exact | brier | 223 | 45 | -0.007436 | -0.024376 | 0.011562 | -0.026680 | 0.011809 |
| 5 | V14_plus_positions | V14_exact | crps | 223 | 45 | -0.000107 | -0.000621 | 0.000532 | -0.000725 | 0.000511 |
| 21 | V14_plus_positions | V14_exact | brier | 159 | 8 | 0.022988 | -0.051573 | 0.077818 | -0.046412 | 0.092387 |
| 21 | V14_plus_positions | V14_exact | crps | 159 | 8 | 0.001336 | -0.001605 | 0.003286 | -0.001223 | 0.003896 |

| horizon | metric | n | gain | remaining gain | removed from | removed to |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | 223 | -0.007436 | -0.013393 | 2026-02-16 | 2026-03-17 |
| 5 | crps | 223 | -0.000107 | -0.000396 | 2026-02-16 | 2026-03-17 |
| 21 | brier | 159 | 0.022988 | 0.007685 | 2026-07-02 | 2026-07-30 |
| 21 | crps | 159 | 0.001336 | 0.000925 | 2026-09-30 | 2026-10-16 |

The month's directional gain weakens from 0.026437 in the earlier cohort to −0.000954 in the later cohort. After dropping one influential 21-origin block, the active directional gain is 0.007685. Exposure variants compare exact reports, one- and five-session delays, alternative category gross denominators, strict completeness, a five-session training embargo and expiry/roll filters. The case sentinels replace future inputs or immature labels with extreme values and add exact duplicate columns. All 36 sentinels returned zero change at their registered numeric tolerance. The futures audit tracks four noninteger OI-conversion cases.

| horizon | model | n | active | brier gain | crps gain |
| --- | --- | --- | --- | --- | --- |
| 5 | complete_reporting_only | 265 | 264 | -0.001896 | 0.000032 |
| 5 | five_session_embargo | 265 | 265 | -0.002357 | -3.39e-06 |
| 5 | own_gross_normalization | 265 | 265 | -0.002270 | 0.000112 |
| 21 | complete_reporting_only | 217 | 217 | 0.019862 | 0.000854 |
| 21 | five_session_embargo | 217 | 217 | 0.012853 | 0.000532 |
| 21 | own_gross_normalization | 217 | 217 | 0.008522 | -0.000824 |

| metric | observed best | rotations | null 95 | exceedances | finite reselection tail |
| --- | --- | --- | --- | --- | --- |
| brier | 0.017455 | 23 | 0.013685 | 1 | 0.083333 |
| crps | 0.000951 | 23 | 0.000542 | 1 | 0.083333 |

| horizon | metric | best observed increment | rotation median | rotation 95 | exceedances | runs |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | -0.002716 | 0.001577 | 0.006323 | 20 | 23 |
| 5 | crps | 0.000016 | 0.000066 | 0.000235 | 13 | 23 |
| 21 | brier | 0.039860 | 0.023926 | 0.053576 | 5 | 23 |
| 21 | crps | 0.001758 | 0.001017 | 0.002178 | 4 | 23 |

The null fits rotate or permute earlier training blocks and reselect the strongest tested mechanism. The finite null exercise and all block intervals address V19 comparisons. The repeated examination of related outcomes in V1–V19 remains a separate source of selection.

[validation-receipt.json](validation-receipt.json) · [future-information-sentinels.csv](future-information-sentinels.csv) · [matched-comparisons.csv](matched-comparisons.csv) · [block-bootstrap-intervals.csv.gz](block-bootstrap-intervals.csv.gz) · [episode-omission.csv](episode-omission.csv) · [refit-reselection-nulls.csv](refit-reselection-nulls.csv) · [native-refit-null-summary.csv](native-refit-null-summary.csv) · [native-bias-control-bands.csv](native-bias-control-bands.csv) · [mechanism-sensitivities-summary.csv](mechanism-sensitivities-summary.csv)
