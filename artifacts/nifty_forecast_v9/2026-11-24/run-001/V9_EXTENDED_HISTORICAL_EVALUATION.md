# NIFTY V9 · Extended Historical Evaluation

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

We preserve the frozen November 17 vintage for V8 reproduction. In a separate acquisition directory Upstox returned completed November 18, 19, 20 and 23, 2026 daily bars. The four NIFTY closes agree with the NSE daily index archive to displayed precision. The older overlap days and every difference are separately recorded in `source-overlap.csv`. Acquisition receipts, URLs, instrument keys and content hashes stay next to the new payloads. [Upstox daily historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE daily archives](https://www.nseindia.com/all-reports)

| origin | status | upstox_close | official_close | delta |
| --- | --- | --- | --- | --- |
| 2026-11-18 | verified | 25227.950000 | 25227.950000 | 0.000000 |
| 2026-11-19 | verified | 25514.300000 | 25514.300000 | 0.000000 |
| 2026-11-20 | verified | 25800.600000 | 25800.600000 | 0.000000 |
| 2026-11-23 | verified | 25349.650000 | 25349.650000 | 0.000000 |


| cohort | horizon | unique_origins | first | last_origin | last_endpoint |
| --- | --- | --- | --- | --- | --- |
| early | 5 | 173 | 2025-10-14 | 2026-06-29 | 2026-07-06 |
| early | 21 | 141 | 2025-12-01 | 2026-06-29 | 2026-07-28 |
| later | 5 | 92 | 2026-06-30 | 2026-11-08 | 2026-11-16 |
| later | 21 | 76 | 2026-06-30 | 2026-10-15 | 2026-11-16 |
| refresh | 5 | 4 | 2026-11-11 | 2026-11-16 | 2026-11-23 |
| refresh | 21 | 4 | 2026-10-19 | 2026-10-23 | 2026-11-23 |


The four sessions resolve four additional prior origins at each horizon. They are reconstructed after outcomes, with mature input labels only and a separate fit calendar for the newly resolved subset. There were fewer than five completed post-vintage sessions, so none of the truly new feature-origin rows was given a fully resolved five/21-session score. The score rows below originate on preexisting historical dates with refreshed endpoints. Their substantial path overlap precludes a new validation claim.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E9_HIST | 4 | 1 | — | 0.250000 | 0.500000 | 0.293383 | 0.780624 | 0.008712 | 0.009848 | 0.014252 | 0.004210 | 0.750000 | 0.750000 | 0.047797 |
| E9_ROT | 4 | 1 | — | 0.750000 | 0.500000 | 0.183200 | 0.549391 | 0.008003 | 0.012520 | 0.013931 | 0.004014 | 0.500000 | 1.000000 | 0.065124 |
| E9_STRUCT | 4 | 1 | — | 0.750000 | 0.500000 | 0.202931 | 0.603104 | 0.007428 | 0.011437 | 0.012465 | 0.003766 | 0.500000 | 1.000000 | 0.065498 |
| E9_COMPACT | 4 | 1 | — | 0.250000 | 0.500000 | 0.301554 | 0.797122 | 0.008604 | 0.008542 | 0.011776 | 0.004396 | 0.750000 | 1.000000 | 0.066290 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E9_HIST | 4 | 1 | — | 1.000000 | 1.000000 | 0.234379 | 0.661895 | 0.106818 | 0.126766 | 0.127374 | 0.054177 | 0.000000 | 0.000000 | 0.087001 |
| E9_ROT | 4 | 1 | — | 0.000000 | 0.000000 | 0.412068 | 1.032114 | 0.114020 | 0.127762 | 0.128309 | 0.057201 | 0.000000 | 0.000000 | 0.058170 |
| E9_STRUCT | 4 | 1 | — | 0.000000 | 0.000000 | 0.478944 | 1.178926 | 0.116999 | 0.130785 | 0.131337 | 0.058299 | 0.000000 | 0.000000 | 0.056700 |
| E9_COMPACT | 4 | 1 | — | 0.000000 | 0.000000 | 0.671489 | 1.711717 | 0.133824 | 0.149762 | 0.150115 | 0.066292 | 0.000000 | 0.000000 | 0.070946 |


The main combined leaderboards require the exact same model, feature definition, eligibility and maturity design on all **265 weekly** or **217 monthly** origins. Discontinuous date exposure, missed earlier state eligibility and trailing-month changes are visible. We do not pool partial or refresh samples into the combined leaderboard. Mature dates are frozen per vintage. The combined chronology retains **53** disjoint weekly and **11** disjoint monthly windows under the greedy selection rule, while the later 21-session subset still has four.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
