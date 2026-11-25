# V15 how forecasts revise through time

The study compares complete rolling refits, a Bayesian/Kalman-style persistent drift estimate, conservative fixed fractional revisions, a shrunken shock-state drift, and supervised risk-normalized residual corrections. The incremental filter starts with the issued path law's average daily log drift and a small prior variance. It updates from observed standardized close innovations, adding a small process-variance term and pulling the state toward the initial drift. The reported 50/50 blend is a standalone probability check. A predictable revision given earlier information is a conditional forecast diagnostic. The study leaves open long-run and conditional drift.

## Direction probability revisions

| horizon | model | n | n origins | old brier | new brier | half update brier | mean abs revision | earlier level corr | revision response slope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | domestic | 1,060 | 265 | 0.198381 | 0.159648 | 0.169122 | 0.151246 | 0.010933 | 0.986155 |
| 5 | full | 1,060 | 265 | 0.198908 | 0.161190 | 0.169701 | 0.152340 | -0.012647 | 0.947183 |
| 5 | incremental | 1,060 | 265 | 0.200247 | 0.162531 | 0.172237 | 0.149783 | 0.010162 | 1.005389 |
| 5 | iv_restart | 1,060 | 265 | 0.199780 | 0.162131 | 0.171961 | 0.147815 | 0.011379 | 1.013292 |
| 5 | refit | 1,060 | 265 | 0.198908 | 0.160464 | 0.169479 | 0.151990 | -0.009900 | 0.961343 |
| 5 | vol_state | 1,060 | 265 | 0.201303 | 0.163227 | 0.173088 | 0.150140 | 0.010065 | 1.004511 |
| 21 | domestic | 4,340 | 217 | 0.184901 | 0.174321 | 0.176755 | 0.073428 | -0.026455 | 0.963426 |
| 21 | full | 4,340 | 217 | 0.188993 | 0.178250 | 0.180336 | 0.079429 | -0.053882 | 0.906237 |
| 21 | incremental | 4,340 | 217 | 0.178889 | 0.168683 | 0.170332 | 0.083942 | -0.058849 | 0.867558 |
| 21 | iv_restart | 4,340 | 217 | 0.176810 | 0.166627 | 0.168995 | 0.075443 | -0.019613 | 0.963452 |
| 21 | refit | 4,340 | 217 | 0.188051 | 0.177144 | 0.179326 | 0.079612 | -0.054314 | 0.913867 |
| 21 | vol_state | 4,340 | 217 | 0.178501 | 0.168162 | 0.170465 | 0.076533 | -0.028541 | 0.943656 |

## Changes in location, tails and width

| horizon | model | quantity | mean revision | mean abs revision | earlier level corr | revision response slope |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | domestic | endpoint_mean | 0.000234 | 0.006598 | -0.048409 | 1.084154 |
| 5 | domestic | endpoint_q50 | 0.000262 | 0.006597 | -0.050479 | — |
| 5 | domestic | remaining_vol_mean | -0.008924 | 0.014880 | -0.284440 | — |
| 5 | domestic | endpoint_width80 | -0.007097 | 0.007683 | -0.388497 | — |
| 5 | domestic | endpoint_q10 | 0.003782 | 0.007989 | -0.160210 | — |
| 5 | domestic | endpoint_q90 | -0.003316 | 0.007248 | -0.061659 | — |
| 5 | domestic | remaining_range_mean | -0.004381 | 0.004603 | -0.417467 | — |
| 5 | full | endpoint_mean | 0.000020 | 0.006648 | -0.037036 | 1.059331 |
| 5 | full | endpoint_q50 | 0.000047 | 0.006617 | -0.037490 | — |
| 5 | full | remaining_vol_mean | -0.008446 | 0.015222 | -0.294859 | — |
| 5 | full | endpoint_width80 | -0.007029 | 0.007645 | -0.395834 | — |
| 5 | full | endpoint_q10 | 0.003533 | 0.007851 | -0.155016 | — |
| 5 | full | endpoint_q90 | -0.003496 | 0.007313 | -0.058098 | — |
| 5 | full | remaining_range_mean | -0.004326 | 0.004575 | -0.416589 | — |
| 5 | incremental | endpoint_mean | -0.000052 | 0.006798 | -0.008666 | 1.001854 |
| 5 | incremental | endpoint_q50 | -0.000031 | 0.006774 | -0.009744 | — |
| 5 | incremental | remaining_vol_mean | -0.004925 | 0.011201 | -0.210164 | — |
| 5 | incremental | endpoint_width80 | -0.006427 | 0.006918 | -0.331200 | — |
| 5 | incremental | endpoint_q10 | 0.003165 | 0.007754 | -0.074500 | — |
| 5 | incremental | endpoint_q90 | -0.003262 | 0.007452 | -0.056319 | — |
| 5 | incremental | remaining_range_mean | -0.004037 | 0.004147 | -0.320768 | — |
| 5 | iv_restart | endpoint_mean | -0.000053 | 0.006595 | 0.002160 | 1.030762 |
| 5 | iv_restart | endpoint_q50 | -0.000030 | 0.006563 | 0.001805 | — |
| 5 | iv_restart | remaining_vol_mean | -0.005147 | 0.013804 | -0.252756 | — |
| 5 | iv_restart | endpoint_width80 | -0.006569 | 0.007418 | -0.367695 | — |
| 5 | iv_restart | endpoint_q10 | 0.003236 | 0.007430 | -0.074254 | — |
| 5 | iv_restart | endpoint_q90 | -0.003333 | 0.007581 | -0.088428 | — |
| 5 | iv_restart | remaining_range_mean | -0.004134 | 0.004402 | -0.366975 | — |
| 5 | refit | endpoint_mean | 0.000005 | 0.006520 | -0.021160 | 1.099242 |
| 5 | refit | endpoint_q50 | 0.000033 | 0.006498 | -0.021567 | — |
| 5 | refit | remaining_vol_mean | -0.008676 | 0.015228 | -0.302633 | — |
| 5 | refit | endpoint_width80 | -0.007048 | 0.007715 | -0.398647 | — |
| 5 | refit | endpoint_q10 | 0.003528 | 0.007811 | -0.155374 | — |
| 5 | refit | endpoint_q90 | -0.003520 | 0.007151 | -0.039154 | — |
| 5 | refit | remaining_range_mean | -0.004363 | 0.004614 | -0.424235 | — |
| 5 | vol_state | endpoint_mean | -0.000050 | 0.006602 | 0.002291 | 1.031403 |
| 5 | vol_state | endpoint_q50 | -0.000154 | 0.006585 | 0.001099 | — |
| 5 | vol_state | remaining_vol_mean | -0.004734 | 0.010825 | -0.184912 | — |
| 5 | vol_state | endpoint_width80 | -0.006179 | 0.006699 | -0.295403 | — |
| 5 | vol_state | endpoint_q10 | 0.003112 | 0.007611 | -0.063376 | — |
| 5 | vol_state | endpoint_q90 | -0.003066 | 0.007112 | -0.028270 | — |
| 5 | vol_state | remaining_range_mean | -0.003950 | 0.004062 | -0.271980 | — |
| 21 | domestic | endpoint_mean | -0.000093 | 0.006811 | -0.011962 | 1.128614 |
| 21 | domestic | endpoint_q50 | -0.000053 | 0.006979 | -0.019984 | — |
| 21 | domestic | remaining_vol_mean | -0.002052 | 0.010744 | -0.135165 | — |
| 21 | domestic | endpoint_width80 | -0.003983 | 0.007733 | -0.102005 | — |
| 21 | domestic | endpoint_q10 | 0.001874 | 0.008285 | -0.049381 | — |
| 21 | domestic | endpoint_q90 | -0.002109 | 0.007844 | -0.029058 | — |
| 21 | domestic | remaining_range_mean | -0.002509 | 0.004104 | -0.070765 | — |
| 21 | full | endpoint_mean | -0.000278 | 0.007210 | -0.025783 | 1.095034 |
| 21 | full | endpoint_q50 | -0.000239 | 0.007372 | -0.034745 | — |
| 21 | full | remaining_vol_mean | -0.001859 | 0.011180 | -0.154128 | — |
| 21 | full | endpoint_width80 | -0.003884 | 0.007734 | -0.105001 | — |
| 21 | full | endpoint_q10 | 0.001641 | 0.008579 | -0.064936 | — |
| 21 | full | endpoint_q90 | -0.002243 | 0.008039 | -0.028397 | — |
| 21 | full | remaining_range_mean | -0.002445 | 0.004207 | -0.075461 | — |
| 21 | incremental | endpoint_mean | -0.000413 | 0.008273 | -0.037778 | 0.894354 |
| 21 | incremental | endpoint_q50 | -0.000377 | 0.008360 | -0.041415 | — |
| 21 | incremental | remaining_vol_mean | -0.000924 | 0.008519 | -0.136886 | — |
| 21 | incremental | endpoint_width80 | -0.003711 | 0.006910 | -0.075685 | — |
| 21 | incremental | endpoint_q10 | 0.001421 | 0.009100 | -0.043826 | — |
| 21 | incremental | endpoint_q90 | -0.002290 | 0.009149 | -0.058613 | — |
| 21 | incremental | remaining_range_mean | -0.002310 | 0.003437 | 0.005292 | — |
| 21 | iv_restart | endpoint_mean | -0.000410 | 0.006974 | 0.011600 | 1.042889 |
| 21 | iv_restart | endpoint_q50 | -0.000371 | 0.007085 | 0.005176 | — |
| 21 | iv_restart | remaining_vol_mean | -0.001017 | 0.010884 | -0.173785 | — |
| 21 | iv_restart | endpoint_width80 | -0.003823 | 0.007908 | -0.117289 | — |
| 21 | iv_restart | endpoint_q10 | 0.001479 | 0.007847 | -0.008591 | — |
| 21 | iv_restart | endpoint_q90 | -0.002344 | 0.008520 | -0.046102 | — |
| 21 | iv_restart | remaining_range_mean | -0.002385 | 0.004062 | -0.063279 | — |
| 21 | refit | endpoint_mean | -0.000303 | 0.007296 | -0.027742 | 1.094606 |
| 21 | refit | endpoint_q50 | -0.000265 | 0.007441 | -0.036034 | — |
| 21 | refit | remaining_vol_mean | -0.001854 | 0.011145 | -0.145451 | — |
| 21 | refit | endpoint_width80 | -0.003882 | 0.007725 | -0.102286 | — |
| 21 | refit | endpoint_q10 | 0.001614 | 0.008738 | -0.068093 | — |
| 21 | refit | endpoint_q90 | -0.002267 | 0.008037 | -0.027542 | — |
| 21 | refit | remaining_range_mean | -0.002449 | 0.004193 | -0.072519 | — |
| 21 | vol_state | endpoint_mean | -0.000403 | 0.006965 | 0.012512 | 1.048554 |
| 21 | vol_state | endpoint_q50 | -0.000475 | 0.007044 | 0.006636 | — |
| 21 | vol_state | remaining_vol_mean | -0.000607 | 0.007554 | -0.107769 | — |
| 21 | vol_state | endpoint_width80 | -0.003323 | 0.006303 | -0.017009 | — |
| 21 | vol_state | endpoint_q10 | 0.001298 | 0.008053 | -0.008347 | — |
| 21 | vol_state | endpoint_q90 | -0.002025 | 0.007609 | 0.004859 | — |
| 21 | vol_state | remaining_range_mean | -0.002112 | 0.003024 | 0.113698 | — |

## One-step 2% barrier revisions in the historical example

| horizon | checkpoint | asof | side | cdf | actual by step |
| --- | --- | --- | --- | --- | --- |
| 5 | 1 | 2026-10-16 | upper | 0.027344 | 0 |
| 5 | 1 | 2026-10-16 | lower | 0.003906 | 0 |
| 5 | 3 | 2026-10-21 | upper | 0.000000 | 0 |
| 5 | 3 | 2026-10-21 | lower | 0.085938 | 0 |
| 21 | 1 | 2026-10-16 | upper | 0.035156 | 0 |
| 21 | 1 | 2026-10-16 | lower | 0.003906 | 0 |
| 21 | 3 | 2026-10-21 | upper | 0.000000 | 0 |
| 21 | 3 | 2026-10-21 | lower | 0.109375 | 0 |
| 21 | 5 | 2026-10-23 | upper | 0.000000 | 0 |
| 21 | 10 | 2026-10-30 | upper | 0.039062 | 0 |

The response slope regresses the realized target minus the previous expectation on the following revision. A slope near one is consistent with a well-scaled revision in this diagnostic. The earlier-level correlation uses only the forecast quantity available at the preceding decision, and both statistics are descriptive under shared outcome dependence. For range and volatility, the archived errors and coverage compare the previous uncertainty band with fully updated path laws. Each barrier's future probability is evaluated only while the side is still at risk.

[Per-update changes](revision-attribution.csv.gz) [Revision metrics](revision-evidence.csv) [Historical passage curves](historical-example-passage.csv) [Original linear filtering paper](https://doi.org/10.1115/1.3662552)
