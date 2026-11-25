# V20 Temporal Return Decomposition

Monthly forecasts are constructed from four log-return pieces covering sessions **1–5, 6–10, 11–15 and 16–21**. All four pieces are unavailable at issue. The outcome, benchmark and candidate endpoint share the original cash reference and exact monthly expiry session. We compared ordinary joint multi-output ridge, reduced-rank coefficients, separate horizon features including corporate inputs early and positioning later, nearest risk-conditioned historical residual vectors, and a deliberate independent-resampling control. The residual histories consist of chronological errors. All their components had matured before the next model fit.

Each candidate adds one common residual row to the four fitted component locations. Compounding that vector gives one complete terminal scenario. The independence control permutes the columns separately and isolates the impact of removing historical dependencies. The same-clock direct specialized forecast and neutral archive provide independent endpoint comparisons.

| horizon | scope | model | n | active | disjoint | brier | crps | log loss | balanced accuracy | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | combined | conditional_history_components | 217 | 217 | 11 | 0.395215 | 0.037568 | 1.548904 | 0.392666 | 0.529954 | 0.097832 |
| 21 | combined | direct_specialized | 217 | 217 | 11 | 0.315709 | 0.030962 | 0.896263 | 0.518982 | 0.617512 | 0.080412 |
| 21 | combined | horizon_specific_components | 217 | 217 | 11 | 0.336322 | 0.033715 | 1.264243 | 0.463978 | 0.677419 | 0.109142 |
| 21 | combined | independent_components_control | 217 | 217 | 11 | 0.304252 | 0.032977 | 1.155955 | 0.496204 | 0.691244 | 0.094740 |
| 21 | combined | joint_multioutput | 217 | 217 | 11 | 0.346278 | 0.034333 | 1.291259 | 0.469802 | 0.663594 | 0.109590 |
| 21 | combined | low_rank_joint | 217 | 217 | 11 | 0.352791 | 0.034982 | 1.302784 | 0.457506 | 0.663594 | 0.109683 |
| 21 | combined | same_clock_neutral | 217 | 217 | 11 | 0.250000 | 0.025543 | 0.693147 | 0.500000 | 0.700461 | 0.081016 |
| 21 | combined | unconditioned_joint | 217 | 217 | 11 | 0.345872 | 0.031427 | 1.250041 | 0.352286 | 0.691244 | 0.108942 |

| start offset | end offset | model | cohort | n | brier | crps | coverage | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 5 | horizon_specific_components | early | 141 | 0.303584 | 0.013491 | 0.624113 | 0.037145 |
| 0 | 5 | horizon_specific_components | later | 76 | 0.217364 | 0.008406 | 0.907895 | 0.050340 |
| 0 | 5 | low_rank_joint | early | 141 | 0.293532 | 0.013230 | 0.645390 | 0.037218 |
| 0 | 5 | low_rank_joint | later | 76 | 0.215005 | 0.008193 | 0.855263 | 0.050630 |
| 0 | 5 | unconditioned_joint | early | 141 | 0.269665 | 0.012470 | 0.673759 | 0.037166 |
| 0 | 5 | unconditioned_joint | later | 76 | 0.226780 | 0.008475 | 0.894737 | 0.050474 |
| 5 | 10 | horizon_specific_components | early | 141 | 0.317636 | 0.013925 | 0.638298 | 0.037719 |
| 5 | 10 | horizon_specific_components | later | 76 | 0.225399 | 0.008957 | 0.868421 | 0.055179 |
| 5 | 10 | low_rank_joint | early | 141 | 0.330391 | 0.014212 | 0.645390 | 0.037750 |
| 5 | 10 | low_rank_joint | later | 76 | 0.245491 | 0.009232 | 0.881579 | 0.055255 |
| 5 | 10 | unconditioned_joint | early | 141 | 0.295061 | 0.013039 | 0.673759 | 0.037726 |
| 5 | 10 | unconditioned_joint | later | 76 | 0.233089 | 0.008829 | 0.881579 | 0.055074 |
| 10 | 15 | horizon_specific_components | early | 141 | 0.321439 | 0.014704 | 0.609929 | 0.038935 |
| 10 | 15 | horizon_specific_components | later | 76 | 0.233931 | 0.011207 | 0.855263 | 0.055625 |
| 10 | 15 | low_rank_joint | early | 141 | 0.324076 | 0.014640 | 0.602837 | 0.038930 |
| 10 | 15 | low_rank_joint | later | 76 | 0.255141 | 0.011953 | 0.828947 | 0.055614 |
| 10 | 15 | unconditioned_joint | early | 141 | 0.285756 | 0.013044 | 0.645390 | 0.038955 |
| 10 | 15 | unconditioned_joint | later | 76 | 0.238358 | 0.011312 | 0.855263 | 0.055480 |
| 15 | 21 | horizon_specific_components | early | 141 | 0.295166 | 0.016911 | 0.638298 | 0.044764 |
| 15 | 21 | horizon_specific_components | later | 76 | 0.241911 | 0.014483 | 0.802632 | 0.064833 |
| 15 | 21 | low_rank_joint | early | 141 | 0.291382 | 0.016334 | 0.659574 | 0.044779 |
| 15 | 21 | low_rank_joint | later | 76 | 0.272341 | 0.015493 | 0.789474 | 0.064766 |
| 15 | 21 | unconditioned_joint | early | 141 | 0.286399 | 0.015017 | 0.687943 | 0.044804 |
| 15 | 21 | unconditioned_joint | later | 76 | 0.247806 | 0.015034 | 0.776316 | 0.064631 |

The combined 6–21 outcome in the lifetime matrix measures the period after the first week directly. To check sensitivity to that experiment’s cash-price parent, a separate comparison forecasts sessions 1–5 and 6–21 from the **same 217 monthly origins** using the corresponding return from each archived same-clock GJR path. Each tested correction uses only matured errors for that same target. The evening and pre-auction comparisons include a no-shift parent, bias, fresh or aged positioning, two slow positioning representations and corporate announcements. The table shows matched CRPS and the 21-session-block, search-adjusted gain bands for the pre-auction comparisons. The full-population losses include fallbacks.

| sessions | model | matched | disjoint | parent | matched loss | full loss | earlier gain | later gain | interval adjusted low | interval adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1–5 | archived_GJR_component | 217 | 44 | 0.010292 | 0.010292 | 0.010292 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 1–5 | bias_only | 168 | 34 | 0.011122 | 0.010985 | 0.010186 | 0.000043 | 0.000251 | -0.000503 | 0.000777 |
| 1–5 | corporate_now | 168 | 34 | 0.011122 | 0.011351 | 0.010470 | -0.000199 | -0.000266 | -0.000608 | 0.000150 |
| 1–5 | participant_lag5 | 168 | 34 | 0.011122 | 0.011471 | 0.010562 | -6.84e-06 | -0.000763 | -0.001123 | 0.000426 |
| 1–5 | participant_now | 168 | 34 | 0.011122 | 0.010894 | 0.010116 | 0.000573 | -0.000189 | -0.000499 | 0.000956 |
| 1–5 | participant_persistent | 168 | 34 | 0.011122 | 0.011550 | 0.010624 | 0.000128 | -0.001102 | -0.001592 | 0.000735 |
| 1–5 | participant_smoothed | 168 | 34 | 0.011122 | 0.011118 | 0.010289 | 0.000284 | -0.000336 | -0.000741 | 0.000749 |
| 6–21 | archived_GJR_component | 217 | 14 | 0.022428 | 0.022428 | 0.022428 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 6–21 | bias_only | 152 | 10 | 0.020084 | 0.021192 | 0.023204 | -0.002220 | 3.91e-06 | -0.004186 | 0.001970 |
| 6–21 | corporate_now | 152 | 10 | 0.020084 | 0.019908 | 0.022305 | -0.001427 | 0.001778 | -0.003045 | 0.003396 |
| 6–21 | participant_lag5 | 152 | 10 | 0.020084 | 0.020001 | 0.022370 | 0.000518 | -0.000352 | -0.003579 | 0.003744 |
| 6–21 | participant_now | 152 | 10 | 0.020084 | 0.019898 | 0.022297 | 0.001253 | -0.000881 | -0.004172 | 0.004544 |
| 6–21 | participant_persistent | 152 | 10 | 0.020084 | 0.019903 | 0.022301 | 0.001002 | -0.000639 | -0.003479 | 0.003842 |
| 6–21 | participant_smoothed | 152 | 10 | 0.020084 | 0.019717 | 0.022171 | 0.000996 | -0.000262 | -0.004074 | 0.004808 |

[temporal-cases.csv.gz](temporal-cases.csv.gz) · [component-case-scores.csv.gz](component-case-scores.csv.gz) · [component-leaderboard.csv](component-leaderboard.csv) · [component-law-archive.npz](component-law-archive.npz) · [architecture-laws.npz](architecture-laws.npz) · [information-lifetime-matrix.csv](information-lifetime-matrix.csv) · [strong-parent-component-comparisons.csv](strong-parent-component-comparisons.csv) · [strong-parent-component-cases.csv.gz](strong-parent-component-cases.csv.gz) · [strong-parent-component-laws.npz](strong-parent-component-laws.npz) · [strong-parent-component-config.json](strong-parent-component-config.json)
