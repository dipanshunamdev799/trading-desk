# V11 Validation And Search Audit

V9 inventoried 454 different configuration fingerprints and 583 archived prediction fingerprints. V10 recorded 155 configurations and 266 prediction fingerprints under its schema. V11 evaluated 205 registered configurations. These counts document different schemas and an adaptive historical search on overlapping market observations. Bootstrap adjustment is bounded to recorded V11 families.

V11 checked **4,105** chronological fit artifacts, **1,050** simplex weight vectors, **20,190** archive laws, **24** exact-copy and future-data tests, and **15,367** unchanged protected files. Fit-label maturities strictly precede prediction and inner calibration boundaries. The procedure uses 2,000 shared circular resamples at blocks 5, 10 and 15, with maximized standardized deviations across weekly Brier and CRPS comparisons in each cohort. All timing, training-budget and source masks remain explicit.

| scope | origin count | weekly contrasts | block 10 max statistic |
| --- | --- | --- | --- |
| early | 173 | 5274 | 4.000666 |
| later | 92 | 6410 | 3.761477 |
| combined | 265 | 5274 | 3.977085 |

Six model and selector mechanisms compete under twelve block-permuted training-label draws over three earlier and three later origins at each horizon. Realized holdout returns remain fixed, randomized blocks reselect dates, and the usefulness selector sees randomized earlier eligible merit. This replay is a small falsification family. Weekly conclusions also face lag, state shift, source timing, input removal and date deletion. Monthly uncertainty is described with recorded phase checks.

| horizon | cohort | score | selected genuine gain | null median | null p95 | fraction null at least genuine |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | early | brier_gain | 0.069184 | 0.010398 | 0.046818 | 0.000000 |
| 5 | early | crps_gain | 0.003001 | 0.000253 | 0.002521 | 0.000000 |
| 5 | later | brier_gain | 0.165893 | 0.069442 | 0.129011 | 0.000000 |
| 5 | later | crps_gain | 0.006831 | 0.001722 | 0.005083 | 0.000000 |
| 21 | early | brier_gain | -0.050579 | 0.141431 | 0.256290 | 1.000000 |
| 21 | early | crps_gain | -0.004000 | 0.008170 | 0.016315 | 1.000000 |
| 21 | later | brier_gain | -0.147564 | -0.052478 | 0.028193 | 0.833333 |
| 21 | later | crps_gain | -0.009780 | -0.004633 | 0.002694 | 0.833333 |

## Failed and ineligible folds

| batch | reason | unestimated |
| --- | --- | --- |
| breadth | Insufficient mature outer budget | 10 |
| memory | Insufficient mature outer budget | 333 |
| overlap | arrays used as indices must be of integer (or boolean) type | 50 |
| repair | all the input arrays must have same number of dimensions, but the array at index 0 has 2 dimension(s) and the array at index 1 has 1 dimension(s) | 50 |

[Full verification](verification.json) · [Null selection results](null-selected.csv) · [Simultaneous bounds](comparison-uncertainty.json) · [Past-only source timestamps](international-availability.csv).
