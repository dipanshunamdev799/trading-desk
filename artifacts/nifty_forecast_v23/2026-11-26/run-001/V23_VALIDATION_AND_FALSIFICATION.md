# V23 Validation and falsification

Registered 12 materially distinct hypotheses at 2026-11-26T07:36:02.611763+05:30 before the V23 tests.
Each specifies a mechanism, target, clock, parent, primary loss, negative control and budget. The data receipts
enforce strict label maturity. Source measurements, transformations, aggregation weights and residual fits enter
each historical replay at its decision cutoff. Equivalent laws and columns are checked for copy invariance.
The source clock poison and the archived case certifications are separate tests.

Negative controls include exact copies, near-duplicate downweighting, fixed random mixtures, a delayed residual,
blocked error permutations, conservative historical and neutral mixtures, and same-episode foreign swaps. Bootstrap
intervals pair dates and use circular blocks of 21 and 42 Indian origins. The simultaneous family limit uses the
maximum standardized deviation across the tested candidates. Individual disjoint phases, each omitted month and
omission of the largest realized or most favorable 21-origin episode quantify dependence on particular stretches.

| horizon | parent | metric | model | block | n | gain | low | high | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | protected_direction | brier | agg_loss_robust | 21 | 265 | -0.011640 | -0.025557 | 0.003953 | -0.031758 | 0.008479 |
| 5 | protected_direction | brier | component_historical_shape_only | 21 | 265 | -0.006256 | -0.020784 | 0.007794 | -0.026175 | 0.013662 |
| 5 | protected_direction | brier | equal_families | 21 | 265 | -0.012661 | -0.027594 | 0.003868 | -0.034320 | 0.008998 |
| 5 | protected_direction | brier | residual_worst_environment | 21 | 265 | 0.002036 | -0.009208 | 0.013564 | -0.013620 | 0.017691 |
| 5 | protected_direction | brier | agg_loss_robust | 42 | 265 | -0.011640 | -0.026862 | 0.004186 | -0.032770 | 0.009491 |
| 5 | protected_direction | brier | component_historical_shape_only | 42 | 265 | -0.006256 | -0.018471 | 0.005910 | -0.023127 | 0.010615 |
| 5 | protected_direction | brier | equal_families | 42 | 265 | -0.012661 | -0.029226 | 0.004297 | -0.035538 | 0.010216 |
| 5 | protected_direction | brier | residual_worst_environment | 42 | 265 | 0.002036 | -0.007494 | 0.010689 | -0.010498 | 0.014569 |
| 5 | protected_direction | crps | agg_loss_robust | 21 | 265 | -0.000138 | -0.000646 | 0.000376 | -0.000845 | 0.000569 |
| 5 | protected_direction | crps | component_historical_shape_only | 21 | 265 | -0.000069 | -0.000550 | 0.000469 | -0.000778 | 0.000640 |
| 5 | protected_direction | crps | equal_families | 21 | 265 | -0.000154 | -0.000694 | 0.000408 | -0.000924 | 0.000615 |
| 5 | protected_direction | crps | residual_worst_environment | 21 | 265 | 0.000065 | -0.000494 | 0.000625 | -0.000690 | 0.000819 |
| 5 | protected_direction | crps | agg_loss_robust | 42 | 265 | -0.000138 | -0.000601 | 0.000357 | -0.000779 | 0.000503 |
| 5 | protected_direction | crps | component_historical_shape_only | 42 | 265 | -0.000069 | -0.000562 | 0.000477 | -0.000779 | 0.000640 |
| 5 | protected_direction | crps | equal_families | 42 | 265 | -0.000154 | -0.000663 | 0.000385 | -0.000854 | 0.000545 |
| 5 | protected_direction | crps | residual_worst_environment | 42 | 265 | 0.000065 | -0.000440 | 0.000546 | -0.000597 | 0.000726 |
| 5 | protected_distribution | brier | agg_loss_robust | 21 | 265 | -0.009630 | -0.023473 | 0.006256 | -0.031278 | 0.012018 |
| 5 | protected_distribution | brier | component_historical_shape_only | 21 | 265 | -0.004247 | -0.014544 | 0.005501 | -0.018901 | 0.010407 |
| 5 | protected_distribution | brier | equal_families | 21 | 265 | -0.010652 | -0.025311 | 0.006024 | -0.033536 | 0.012233 |
| 5 | protected_distribution | brier | residual_worst_environment | 21 | 265 | 0.004045 | -0.003665 | 0.011908 | -0.007496 | 0.015587 |
| 5 | protected_distribution | brier | agg_loss_robust | 42 | 265 | -0.009630 | -0.024785 | 0.004527 | -0.030455 | 0.011194 |
| 5 | protected_distribution | brier | component_historical_shape_only | 42 | 265 | -0.004247 | -0.014855 | 0.005748 | -0.018913 | 0.010419 |
| 5 | protected_distribution | brier | equal_families | 42 | 265 | -0.010652 | -0.026804 | 0.004947 | -0.033137 | 0.011834 |
| 5 | protected_distribution | brier | residual_worst_environment | 42 | 265 | 0.004045 | -0.003400 | 0.011593 | -0.006438 | 0.014528 |
| 5 | protected_distribution | crps | agg_loss_robust | 21 | 265 | -0.000197 | -0.000827 | 0.000431 | -0.001105 | 0.000711 |
| 5 | protected_distribution | crps | component_historical_shape_only | 21 | 265 | -0.000129 | -0.000330 | 0.000062 | -0.000425 | 0.000167 |
| 5 | protected_distribution | crps | equal_families | 21 | 265 | -0.000214 | -0.000887 | 0.000457 | -0.001183 | 0.000755 |
| 5 | protected_distribution | crps | residual_worst_environment | 21 | 265 | 0.000005 | -0.000404 | 0.000406 | -0.000590 | 0.000600 |
| 5 | protected_distribution | crps | agg_loss_robust | 42 | 265 | -0.000197 | -0.000813 | 0.000352 | -0.001029 | 0.000634 |
| 5 | protected_distribution | crps | component_historical_shape_only | 42 | 265 | -0.000129 | -0.000380 | 0.000120 | -0.000476 | 0.000218 |
| 5 | protected_distribution | crps | equal_families | 42 | 265 | -0.000214 | -0.000877 | 0.000401 | -0.001112 | 0.000684 |
| 5 | protected_distribution | crps | residual_worst_environment | 42 | 265 | 0.000005 | -0.000340 | 0.000305 | -0.000439 | 0.000450 |
| 21 | protected_direction | brier | agg_loss_robust | 21 | 217 | -0.025468 | -0.048968 | -0.001098 | -0.059664 | 0.008727 |
| 21 | protected_direction | brier | component_historical_shape_only | 21 | 217 | 0.012935 | 0.004900 | 0.022825 | 0.000407 | 0.025464 |
| 21 | protected_direction | brier | equal_families | 21 | 217 | -0.027529 | -0.053961 | 0.003493 | -0.067960 | 0.012901 |
| 21 | protected_direction | brier | residual_worst_environment | 21 | 217 | 0.005324 | -0.024846 | 0.034301 | -0.036793 | 0.047440 |
| 21 | protected_direction | brier | agg_loss_robust | 42 | 217 | -0.025468 | -0.049196 | -0.002476 | -0.057812 | 0.006876 |
| 21 | protected_direction | brier | component_historical_shape_only | 42 | 217 | 0.012935 | 0.005939 | 0.021681 | 0.001619 | 0.024251 |
| 21 | protected_direction | brier | equal_families | 42 | 217 | -0.027529 | -0.052863 | -0.000767 | -0.064415 | 0.009356 |
| 21 | protected_direction | brier | residual_worst_environment | 42 | 217 | 0.005324 | -0.020316 | 0.034425 | -0.033368 | 0.044016 |
| 21 | protected_direction | crps | agg_loss_robust | 21 | 217 | -0.001475 | -0.003100 | 0.000081 | -0.003642 | 0.000692 |
| 21 | protected_direction | crps | component_historical_shape_only | 21 | 217 | 0.000263 | -0.001159 | 0.001399 | -0.001516 | 0.002042 |
| 21 | protected_direction | crps | equal_families | 21 | 217 | -0.001647 | -0.003462 | 0.000183 | -0.004106 | 0.000812 |
| 21 | protected_direction | crps | residual_worst_environment | 21 | 217 | 0.000052 | -0.001816 | 0.001837 | -0.002475 | 0.002579 |
| 21 | protected_direction | crps | agg_loss_robust | 42 | 217 | -0.001475 | -0.003180 | 0.000035 | -0.003617 | 0.000667 |
| 21 | protected_direction | crps | component_historical_shape_only | 42 | 217 | 0.000263 | -0.000944 | 0.001340 | -0.001264 | 0.001790 |
| 21 | protected_direction | crps | equal_families | 42 | 217 | -0.001647 | -0.003394 | -0.000017 | -0.003945 | 0.000651 |
| 21 | protected_direction | crps | residual_worst_environment | 42 | 217 | 0.000052 | -0.001724 | 0.001934 | -0.002430 | 0.002534 |
| 21 | protected_distribution | brier | agg_loss_robust | 21 | 217 | -0.025081 | -0.051622 | 0.007841 | -0.067223 | 0.017062 |
| 21 | protected_distribution | brier | component_historical_shape_only | 21 | 217 | 0.013323 | -0.000078 | 0.032833 | -0.010405 | 0.037051 |
| 21 | protected_distribution | brier | equal_families | 21 | 217 | -0.027142 | -0.057114 | 0.012504 | -0.076524 | 0.022240 |
| 21 | protected_distribution | brier | residual_worst_environment | 21 | 217 | 0.005711 | -0.026559 | 0.037731 | -0.039787 | 0.051209 |
| 21 | protected_distribution | brier | agg_loss_robust | 42 | 217 | -0.025081 | -0.051393 | 0.006115 | -0.064174 | 0.014012 |
| 21 | protected_distribution | brier | component_historical_shape_only | 42 | 217 | 0.013323 | -0.000232 | 0.031988 | -0.008770 | 0.035416 |
| 21 | protected_distribution | brier | equal_families | 42 | 217 | -0.027142 | -0.055715 | 0.008957 | -0.071696 | 0.017412 |
| 21 | protected_distribution | brier | residual_worst_environment | 42 | 217 | 0.005711 | -0.024552 | 0.040179 | -0.036601 | 0.048023 |
| 21 | protected_distribution | crps | agg_loss_robust | 21 | 217 | -0.001465 | -0.002736 | 0.000096 | -0.003451 | 0.000521 |
| 21 | protected_distribution | crps | component_historical_shape_only | 21 | 217 | 0.000273 | -0.001040 | 0.001421 | -0.001490 | 0.002037 |
| 21 | protected_distribution | crps | equal_families | 21 | 217 | -0.001637 | -0.003092 | 0.000193 | -0.003987 | 0.000713 |
| 21 | protected_distribution | crps | residual_worst_environment | 21 | 217 | 0.000062 | -0.001519 | 0.001803 | -0.002242 | 0.002366 |
| 21 | protected_distribution | crps | agg_loss_robust | 42 | 217 | -0.001465 | -0.002790 | -0.000004 | -0.003355 | 0.000425 |
| 21 | protected_distribution | crps | component_historical_shape_only | 42 | 217 | 0.000273 | -0.000699 | 0.001171 | -0.000962 | 0.001509 |
| 21 | protected_distribution | crps | equal_families | 42 | 217 | -0.001637 | -0.003101 | 0.000031 | -0.003764 | 0.000490 |
| 21 | protected_distribution | crps | residual_worst_environment | 42 | 217 | 0.000062 | -0.001386 | 0.001869 | -0.002097 | 0.002221 |

| horizon | model | metric | omission type | omitted | n | gain remaining |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | component_historical_shape_only | brier | largest_realized_episode | 2026-10-09 to 2026-11-08 | 244 | -0.005064 |
| 5 | component_historical_shape_only | brier | largest_favorable_episode | 2026-02-23 to 2026-03-24 | 244 | -0.007184 |
| 5 | equal_families | brier | largest_realized_episode | 2026-10-09 to 2026-11-08 | 244 | -0.007204 |
| 5 | equal_families | brier | largest_favorable_episode | 2025-11-27 to 2025-12-26 | 244 | -0.016300 |
| 5 | residual_worst_environment | brier | largest_realized_episode | 2026-10-09 to 2026-11-08 | 244 | 0.003933 |
| 5 | residual_worst_environment | brier | largest_favorable_episode | 2026-02-20 to 2026-03-23 | 244 | -0.000298 |
| 5 | component_historical_shape_only | crps | largest_realized_episode | 2026-10-09 to 2026-11-08 | 244 | -0.000160 |
| 5 | component_historical_shape_only | crps | largest_favorable_episode | 2026-09-30 to 2026-10-30 | 244 | -0.000195 |
| 5 | equal_families | crps | largest_realized_episode | 2026-10-09 to 2026-11-08 | 244 | 0.000024 |
| 5 | equal_families | crps | largest_favorable_episode | 2025-11-18 to 2025-12-16 | 244 | -0.000427 |
| 5 | residual_worst_environment | crps | largest_realized_episode | 2026-10-09 to 2026-11-08 | 244 | -0.000009 |
| 5 | residual_worst_environment | crps | largest_favorable_episode | 2026-02-20 to 2026-03-23 | 244 | -0.000226 |
| 21 | component_historical_shape_only | brier | largest_realized_episode | 2026-02-04 to 2026-03-05 | 196 | 0.012781 |
| 21 | component_historical_shape_only | brier | largest_favorable_episode | 2026-08-28 to 2026-09-28 | 196 | 0.002883 |
| 21 | equal_families | brier | largest_realized_episode | 2026-02-04 to 2026-03-05 | 196 | -0.016599 |
| 21 | equal_families | brier | largest_favorable_episode | 2026-08-28 to 2026-09-28 | 196 | -0.047817 |
| 21 | residual_worst_environment | brier | largest_realized_episode | 2026-02-04 to 2026-03-05 | 196 | 0.010950 |
| 21 | residual_worst_environment | brier | largest_favorable_episode | 2026-08-14 to 2026-09-11 | 196 | -0.006860 |
| 21 | component_historical_shape_only | crps | largest_realized_episode | 2026-02-04 to 2026-03-05 | 196 | -0.000064 |
| 21 | component_historical_shape_only | crps | largest_favorable_episode | 2026-08-26 to 2026-09-24 | 196 | -0.000077 |
| 21 | equal_families | crps | largest_realized_episode | 2026-02-04 to 2026-03-05 | 196 | -0.001083 |
| 21 | equal_families | crps | largest_favorable_episode | 2026-08-31 to 2026-09-29 | 196 | -0.002636 |
| 21 | residual_worst_environment | crps | largest_realized_episode | 2026-02-04 to 2026-03-05 | 196 | 0.000394 |
| 21 | residual_worst_environment | crps | largest_favorable_episode | 2026-08-11 to 2026-09-08 | 196 | -0.000743 |

| horizon | metric | phases | positive phases | min gain | max gain |
| --- | --- | --- | --- | --- | --- |
| 5 | brier | 5 | 1 | -0.008201 | 0.000663 |
| 5 | crps | 5 | 2 | -0.000251 | 0.000016 |
| 21 | brier | 21 | 20 | -0.006085 | 0.025544 |
| 21 | crps | 21 | 17 | -0.000167 | 0.001142 |

The monthly domestic substitution has positive family-adjusted bounds on the direction benchmark in this V23 search family. The broader comparison against the V21 distribution parent still spans zero. The 11 monthly disjoint outcomes and cumulative historical selection remain the relevant limits on an independent claim.

[registration.json](registration.json) · [leakage-and-duplication-checks.json](leakage-and-duplication-checks.json) · [original-horizon-search-adjusted-intervals.csv.gz](original-horizon-search-adjusted-intervals.csv.gz) · [leave-episodes-out.csv.gz](leave-episodes-out.csv.gz) · [disjoint-phase-comparisons.csv.gz](disjoint-phase-comparisons.csv.gz) · [bounded-refit-reselection-summary.csv](bounded-refit-reselection-summary.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
