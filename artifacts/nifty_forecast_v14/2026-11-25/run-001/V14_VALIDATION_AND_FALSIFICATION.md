# V14 Validation And Falsification

Bootstrap uncertainty uses **1,600** paired circular blocks at lengths **5, 10, 21 and 42** across the frozen cohort calendar. Reported bands use the maximum standardized deviation within each declared family. Limited disjoint coverage remains visible, and adjustment covers the V14 comparisons only. Screening uses original source dates, guard clocks, chronological fits with matured outcomes, and duplicate and unreleased-label sentinels. The null experiment refits four competing feature specifications on permuted training blocks around the retained risk anchor. It then selects the best gain at each draw, within a bounded thinned origin panel. A handful of draws provide diagnostic evidence.

| horizon | event | null_draws | observed_gain | mean_null_gain | max_null_gain | worst_case_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | expand | 12 | -0.018104 | 0.021532 | 0.087957 | 0.916667 |
| 5 | lower_relative | 12 | 0.037088 | 0.015749 | 0.053503 | 0.250000 |
| 5 | range_relative | 12 | -0.000561 | -0.003720 | 0.028806 | 0.416667 |
| 5 | upper_relative | 12 | 0.028551 | 0.006969 | 0.041523 | 0.166667 |
| 21 | expand | 12 | 0.081478 | 0.051510 | 0.131261 | 0.250000 |
| 21 | lower_relative | 12 | 0.004243 | 0.011839 | 0.072854 | 0.750000 |
| 21 | range_relative | 12 | 0.085229 | 0.066095 | 0.106453 | 0.250000 |
| 21 | upper_relative | 12 | 0.002148 | 0.006780 | 0.023657 | 0.916667 |

| horizon | model | n | touch_diff | range_hi_diff | conditional_mc_se |
| --- | --- | --- | --- | --- | --- |
| 5 | constant_iv | 512 | 0.011895 | 0.000769 | 0.018674 |
| 5 | constant_iv | 2048 | 0.008884 | 0.000233 | 0.009242 |
| 5 | constant_iv | 8192 | 0.000000 | 0.000000 | 0.004624 |
| 5 | gjr_iv | 512 | 0.011230 | 0.000517 | 0.017857 |
| 5 | gjr_iv | 2048 | 0.008843 | 0.000215 | 0.008779 |
| 5 | gjr_iv | 8192 | 0.000000 | 0.000000 | 0.004402 |
| 5 | jump_diffusion | 512 | 0.015286 | 0.000873 | 0.017434 |
| 5 | jump_diffusion | 2048 | 0.005710 | 0.000483 | 0.008587 |
| 5 | jump_diffusion | 8192 | 0.000000 | 0.000000 | 0.004324 |
| 21 | constant_iv | 512 | 0.019880 | 0.001743 | 0.021133 |
| 21 | constant_iv | 2048 | 0.006766 | 0.000946 | 0.010537 |
| 21 | constant_iv | 8192 | 0.000000 | 0.000000 | 0.005259 |
| 21 | gjr_iv | 512 | 0.018154 | 0.001505 | 0.021533 |
| 21 | gjr_iv | 2048 | 0.006923 | 0.000684 | 0.010755 |
| 21 | gjr_iv | 8192 | 0.000000 | 0.000000 | 0.005372 |
| 21 | jump_diffusion | 512 | 0.021938 | 0.001753 | 0.021470 |
| 21 | jump_diffusion | 2048 | 0.008266 | 0.000539 | 0.010773 |
| 21 | jump_diffusion | 8192 | 0.000000 | 0.000000 | 0.005395 |

| horizon | steps | raw_error | bridge_error |
| --- | --- | --- | --- |
| 5 | 12 | 0.031408 | 0.002857 |
| 5 | 24 | 0.022619 | 0.003229 |
| 5 | 48 | 0.016366 | 0.003285 |
| 5 | 96 | 0.011795 | 0.003151 |
| 21 | 12 | 0.025485 | 0.004582 |
| 21 | 24 | 0.018178 | 0.004727 |
| 21 | 48 | 0.013394 | 0.004911 |
| 21 | 96 | 0.010324 | 0.004906 |

Bridge probabilities in the last table are for one-sided hits in a continuous log-price diffusion. They use conditional no-cross probabilities within each simulated step. The bridge test uses a common fine grid and omits overnight jumps. Full joint models keep discrete kicks and overnight moves separate. Parameter perturbations, shortened training history, altered jump sampling and removed extremes are compared on matched dates.

[Registration](registration.json) · [All matched bands](matched-search-adjusted.csv) · [Refit null per-origin data](refit-null-origins.csv.gz) · [Bridge experiment](continuous-bridge-check.csv) · [Fit and timing verification](timing-verification.json).
