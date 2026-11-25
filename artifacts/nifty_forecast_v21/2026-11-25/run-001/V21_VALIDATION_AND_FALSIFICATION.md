# V21 Validation And Falsification

The validation checked **241,842** event clocks and **21,540** issued model-case training times against the historical snapshot. All feature preprocessing and target membership use earlier eligible data. The future-label sentinel perturbs unobservable targets. Named feature deduplication and identical expert-law invariance are tested. Weight timing, corporate actions, January eligible random baskets, dominant holdings, missing security weight and randomly assigned sector controls are individually preserved. The dependence lane includes independent, Gaussian, factor, historical conditional, heavy-tail and sample-size controls.

The paired gain intervals use **1,200 circular bootstraps with 21-session blocks**. They adjust within each tested clock, model family and metric. This adjustment does not cover the adaptive V1–V21 research program. The null study runs **23** representative chronological refits and reselects among **four** residual designs with the input history block-permuted. Its observed variant is a small, purpose-matched test with the same refit procedure. The broader leaderboard remains historical and exposed.

| horizon | metric | observed gain | simulations | null median | null 95 | exceedances | rank tail |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | 0.000553 | 23 | 0.000428 | 0.001650 | 9 | 0.416667 |
| 5 | crps | 0.000119 | 23 | 1.74e-07 | 0.000035 | 0 | 0.041667 |
| 21 | brier | 0.002978 | 23 | 0.000500 | 0.003082 | 2 | 0.125000 |
| 21 | crps | -0.000023 | 23 | -0.000015 | 0.000129 | 14 | 0.625000 |

| horizon | reference | model | metric | scope | n | active | disjoint | gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | price_reaction | anchor_aggregate_position | brier | early | 173 | 124 | 35 | 0.004183 |
| 5 | price_reaction | anchor_aggregate_position | brier | later | 92 | 92 | 19 | -0.009994 |
| 5 | price_reaction | anchor_asymmetry | brier | early | 173 | 124 | 35 | 0.002386 |
| 5 | price_reaction | anchor_asymmetry | brier | later | 92 | 92 | 19 | -0.000872 |
| 5 | price_reaction | anchor_aggregate_position | crps | early | 173 | 124 | 35 | 0.000203 |
| 5 | price_reaction | anchor_aggregate_position | crps | later | 92 | 92 | 19 | -0.000631 |
| 5 | price_reaction | anchor_asymmetry | crps | early | 173 | 124 | 35 | 0.000155 |
| 5 | price_reaction | anchor_asymmetry | crps | later | 92 | 92 | 19 | -0.000029 |
| 5 | omit_latest_21_training_origins | anchor_aggregate_position | brier | early | 173 | 124 | 35 | -0.004128 |
| 5 | omit_latest_21_training_origins | anchor_aggregate_position | brier | later | 92 | 92 | 19 | 0.000764 |
| 5 | omit_latest_21_training_origins | anchor_asymmetry | brier | early | 173 | 124 | 35 | -0.005925 |
| 5 | omit_latest_21_training_origins | anchor_asymmetry | brier | later | 92 | 92 | 19 | 0.009886 |
| 5 | omit_latest_21_training_origins | anchor_aggregate_position | crps | early | 173 | 124 | 35 | -0.000071 |
| 5 | omit_latest_21_training_origins | anchor_aggregate_position | crps | later | 92 | 92 | 19 | -0.000068 |
| 5 | omit_latest_21_training_origins | anchor_asymmetry | crps | early | 173 | 124 | 35 | -0.000120 |
| 5 | omit_latest_21_training_origins | anchor_asymmetry | crps | later | 92 | 92 | 19 | 0.000533 |
| 21 | smooth5 | anchor_aggregate_position | brier | early | 141 | 76 | 7 | 0.019699 |
| 21 | smooth5 | anchor_aggregate_position | brier | later | 76 | 76 | 4 | -0.022891 |

| horizon | reference | model | metric | type | omitted | n | omitted gain | remaining gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | price_reaction | anchor_aggregate_position | brier | largest_gain_21_origins | 2026-07-23 to 2026-08-20 | 244 | 0.034701 | -0.003789 |
| 5 | price_reaction | anchor_aggregate_position | brier | largest_market_21_origins | 2026-10-09 to 2026-11-08 | 244 | -0.005268 | -0.000349 |
| 5 | price_reaction | anchor_asymmetry | brier | largest_gain_21_origins | 2026-03-30 to 2026-04-30 | 244 | 0.017323 | -0.000129 |
| 5 | price_reaction | anchor_asymmetry | brier | largest_market_21_origins | 2026-10-09 to 2026-11-08 | 244 | 0.001496 | 0.001234 |
| 5 | price_reaction | stock_gaussian_shrink | brier | largest_gain_21_origins | 2025-11-27 to 2025-12-26 | 244 | 0.067828 | -0.053636 |
| 5 | price_reaction | stock_gaussian_shrink | brier | largest_market_21_origins | 2026-10-09 to 2026-11-08 | 244 | -0.002616 | -0.047573 |
| 5 | price_reaction | anchor_aggregate_position | crps | largest_gain_21_origins | 2026-05-14 to 2026-06-12 | 244 | 0.000888 | -0.000170 |
| 5 | price_reaction | anchor_aggregate_position | crps | largest_market_21_origins | 2026-10-09 to 2026-11-08 | 244 | -0.000588 | -0.000043 |
| 5 | price_reaction | anchor_asymmetry | crps | largest_gain_21_origins | 2026-03-30 to 2026-04-30 | 244 | 0.001197 | -4.48e-06 |
| 5 | price_reaction | anchor_asymmetry | crps | largest_market_21_origins | 2026-10-09 to 2026-11-08 | 244 | 0.000357 | 0.000068 |
| 5 | price_reaction | stock_gaussian_shrink | crps | largest_gain_21_origins | 2026-04-01 to 2026-05-04 | 244 | 0.003689 | -0.001805 |
| 5 | price_reaction | stock_gaussian_shrink | crps | largest_market_21_origins | 2026-10-09 to 2026-11-08 | 244 | -0.002156 | -0.001302 |
| 21 | smooth5 | anchor_aggregate_position | brier | largest_gain_21_origins | 2026-06-16 to 2026-07-15 | 196 | 0.091786 | -0.004539 |
| 21 | smooth5 | anchor_aggregate_position | brier | largest_market_21_origins | 2026-02-04 to 2026-03-05 | 196 | 0.000000 | 0.005295 |
| 21 | smooth5 | anchor_asymmetry | brier | largest_gain_21_origins | 2026-09-17 to 2026-10-16 | 196 | 0.008108 | -0.002321 |
| 21 | smooth5 | anchor_asymmetry | brier | largest_market_21_origins | 2026-02-04 to 2026-03-05 | 196 | 0.000000 | -0.001452 |
| 21 | smooth5 | stock_gaussian_shrink | brier | largest_gain_21_origins | 2026-08-28 to 2026-09-28 | 196 | 0.288290 | -0.039132 |
| 21 | smooth5 | stock_gaussian_shrink | brier | largest_market_21_origins | 2026-02-04 to 2026-03-05 | 196 | -0.076093 | -0.000091 |
| 21 | smooth5 | anchor_aggregate_position | crps | largest_gain_21_origins | 2026-03-06 to 2026-04-08 | 196 | 0.005716 | 0.000054 |
| 21 | smooth5 | anchor_aggregate_position | crps | largest_market_21_origins | 2026-02-04 to 2026-03-05 | 196 | 0.000000 | 0.000666 |
| 21 | smooth5 | anchor_asymmetry | crps | largest_gain_21_origins | 2026-09-17 to 2026-10-16 | 196 | 0.000879 | -0.000319 |
| 21 | smooth5 | anchor_asymmetry | crps | largest_market_21_origins | 2026-02-04 to 2026-03-05 | 196 | 0.000000 | -0.000225 |
| 21 | smooth5 | stock_gaussian_shrink | crps | largest_gain_21_origins | 2026-08-26 to 2026-09-24 | 196 | 0.015142 | -0.002666 |
| 21 | smooth5 | stock_gaussian_shrink | crps | largest_market_21_origins | 2026-02-04 to 2026-03-05 | 196 | -0.008826 | -0.000098 |

The full disjoint-phase record and all calendar-month removals accompany the separate earliest/later tests. Covered dates and changes in tracking error survive in the machine files.

[validation-receipt.json](validation-receipt.json) · [null-refit-cases.csv](null-refit-cases.csv) · [null-refit-summary.csv](null-refit-summary.csv) · [episode-removal-sensitivity.csv.gz](episode-removal-sensitivity.csv.gz) · [disjoint-outcome-phases.csv.gz](disjoint-outcome-phases.csv.gz) · [index-search-adjusted-intervals.csv](index-search-adjusted-intervals.csv) · [index-tracking-leaderboard.csv](index-tracking-leaderboard.csv) · [component-event-clock-audit.csv.gz](component-event-clock-audit.csv.gz)
