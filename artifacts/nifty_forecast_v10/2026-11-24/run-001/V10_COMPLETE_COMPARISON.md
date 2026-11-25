# V10 Complete Comparison

The rankings retain cohort and origin coverage, eligibility and fixed benchmarks. Positive gains in the incremental ranking mean reduction in loss versus the registered parent. Frozen systems are ranked on overlapping compatible origins, and headline combined tables require 265 weekly or 217 monthly outcomes. A high ranking on a partial window has its own sample.

## Combined weekly probability quality

| model | n | disjoint | brier | crps | log_loss | accuracy | balanced_accuracy | mae | median_mae | coverage80 | width80 | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J10_STRUCTURAL_BLEND | 265 | 53 | 0.236181 | 0.011043 | 0.667575 | 0.637736 | 0.651507 | 0.015172 | 0.014723 | 0.815094 | 0.048713 | 0.081780 |
| P_CLUSTER | 265 | 53 | 0.236386 | 0.011775 | 0.675954 | 0.649057 | 0.652691 | 0.016092 | 0.015714 | 0.762264 | 0.050935 | 0.135838 |
| S_NATIVE_ROT | 265 | 53 | 0.236785 | 0.011207 | 0.673015 | 0.633962 | 0.640073 | 0.015166 | 0.015059 | 0.754717 | 0.041400 | 0.106839 |
| BASE_NATIVE | 265 | 53 | 0.237197 | 0.011261 | 0.674289 | 0.645283 | 0.654684 | 0.015232 | 0.015078 | 0.750943 | 0.041446 | 0.125146 |
| S_ELASTIC | 265 | 53 | 0.241025 | 0.012013 | 0.687758 | 0.630189 | 0.634904 | 0.016362 | 0.016235 | 0.803774 | 0.052570 | 0.135521 |
| J10_HISTORY_SHRINK | 265 | 53 | 0.242366 | 0.010892 | 0.678095 | 0.615094 | 0.627657 | 0.014988 | 0.014609 | 0.800000 | 0.045068 | 0.081103 |
| J9_STATIC | 265 | 53 | 0.246239 | 0.011029 | 0.686175 | 0.581132 | 0.595461 | 0.015152 | 0.014746 | 0.792453 | 0.044527 | 0.087850 |
| V4_M05_lgbm | 265 | 53 | 0.247539 | 0.011580 | 0.690229 | 0.566038 | 0.559569 | 0.016128 | 0.015564 | 0.671698 | 0.035806 | 0.112546 |
| J9_REL_SHRINK | 265 | 53 | 0.248725 | 0.011014 | 0.691291 | 0.566038 | 0.576577 | 0.015100 | 0.014820 | 0.769811 | 0.041599 | 0.093883 |
| V4_Z_neutral | 265 | 53 | 0.250000 | 0.011339 | 0.693147 | 0.441509 | 0.500000 | 0.015448 | 0.015264 | 0.713208 | 0.037330 | 0.058491 |
| NEUTRAL | 265 | 53 | 0.250000 | 0.011058 | 0.693147 | 0.528302 | 0.488190 | 0.015052 | 0.015062 | 0.735849 | 0.039228 | 0.058491 |
| BASE_ROTATION | 265 | 53 | 0.251066 | 0.012061 | 0.706419 | 0.603774 | 0.616626 | 0.016353 | 0.016077 | 0.754717 | 0.042775 | 0.126488 |
| P_ROT | 265 | 53 | 0.252015 | 0.012108 | 0.710508 | 0.611321 | 0.622488 | 0.016418 | 0.016150 | 0.754717 | 0.043418 | 0.125979 |
| L_ROT_MAX | 265 | 53 | 0.252909 | 0.012134 | 0.712522 | 0.611321 | 0.623383 | 0.016429 | 0.016165 | 0.762264 | 0.043617 | 0.122416 |

## Combined weekly distribution quality

| model | n | disjoint | brier | crps | log_loss | accuracy | balanced_accuracy | mae | median_mae | coverage80 | width80 | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J10_HISTORY_SHRINK | 265 | 53 | 0.242366 | 0.010892 | 0.678095 | 0.615094 | 0.627657 | 0.014988 | 0.014609 | 0.800000 | 0.045068 | 0.081103 |
| J9_REL_SHRINK | 265 | 53 | 0.248725 | 0.011014 | 0.691291 | 0.566038 | 0.576577 | 0.015100 | 0.014820 | 0.769811 | 0.041599 | 0.093883 |
| J9_STATIC | 265 | 53 | 0.246239 | 0.011029 | 0.686175 | 0.581132 | 0.595461 | 0.015152 | 0.014746 | 0.792453 | 0.044527 | 0.087850 |
| J10_STRUCTURAL_BLEND | 265 | 53 | 0.236181 | 0.011043 | 0.667575 | 0.637736 | 0.651507 | 0.015172 | 0.014723 | 0.815094 | 0.048713 | 0.081780 |
| NEUTRAL | 265 | 53 | 0.250000 | 0.011058 | 0.693147 | 0.528302 | 0.488190 | 0.015052 | 0.015062 | 0.735849 | 0.039228 | 0.058491 |
| S_NATIVE_ROT | 265 | 53 | 0.236785 | 0.011207 | 0.673015 | 0.633962 | 0.640073 | 0.015166 | 0.015059 | 0.754717 | 0.041400 | 0.106839 |
| J10_TARGET_BLEND | 265 | 53 | 0.255725 | 0.011242 | 0.706972 | 0.550943 | 0.543370 | 0.015346 | 0.015294 | 0.743396 | 0.039475 | 0.107991 |
| T_SIGNMAG | 265 | 53 | 0.257489 | 0.011259 | 0.710847 | 0.524528 | 0.514351 | 0.015137 | 0.015249 | 0.705660 | 0.037795 | 0.096094 |
| BASE_NATIVE | 265 | 53 | 0.237197 | 0.011261 | 0.674289 | 0.645283 | 0.654684 | 0.015232 | 0.015078 | 0.750943 | 0.041446 | 0.125146 |
| V4_D02_student_shrunk | 265 | 53 | 0.263802 | 0.011301 | 0.746821 | 0.539623 | 0.567250 | 0.015149 | 0.015149 | 0.698113 | 0.041323 | 0.160110 |
| J10_SMALL_BLEND | 265 | 53 | 0.255845 | 0.011315 | 0.706213 | 0.554717 | 0.543168 | 0.015376 | 0.015160 | 0.735849 | 0.038322 | 0.103294 |
| J10_TRANSFER_BLEND | 265 | 53 | 0.259148 | 0.011321 | 0.712051 | 0.475472 | 0.471327 | 0.015591 | 0.015554 | 0.769811 | 0.043354 | 0.114838 |
| LC_STUDENT_MAX | 265 | 53 | 0.254899 | 0.011323 | 0.705107 | 0.588679 | 0.587000 | 0.015627 | 0.015414 | 0.739623 | 0.041352 | 0.078344 |
| T_VOL_STUDENT | 265 | 53 | 0.254899 | 0.011323 | 0.705107 | 0.588679 | 0.587000 | 0.015627 | 0.015414 | 0.739623 | 0.041352 | 0.078344 |

## Combined monthly full-coverage results

| model | n | disjoint | brier | crps | log_loss | accuracy | balanced_accuracy | mae | median_mae | coverage80 | width80 | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V4_Z_neutral | 217 | 11 | 0.250000 | 0.027486 | 0.693147 | 0.437788 | 0.500000 | 0.035633 | 0.035609 | 0.585253 | 0.065591 | 0.062212 |
| NEUTRAL | 217 | 11 | 0.250000 | 0.025420 | 0.693147 | 0.511521 | 0.460742 | 0.033371 | 0.033392 | 0.635945 | 0.068179 | 0.062212 |
| LC_STUDENT_MAX | 217 | 11 | 0.266992 | 0.029111 | 0.729691 | 0.479263 | 0.486799 | 0.040148 | 0.041351 | 0.645161 | 0.089092 | 0.174313 |
| T_VOL_STUDENT | 217 | 11 | 0.266992 | 0.029111 | 0.729691 | 0.479263 | 0.486799 | 0.040148 | 0.041351 | 0.645161 | 0.089092 | 0.174313 |
| T_STUDENT | 217 | 11 | 0.271448 | 0.027926 | 0.740926 | 0.511521 | 0.515487 | 0.036871 | 0.036731 | 0.622120 | 0.079665 | 0.128560 |
| J10_TARGET_BLEND | 217 | 11 | 0.282285 | 0.027543 | 0.765207 | 0.470046 | 0.498404 | 0.037787 | 0.035415 | 0.594470 | 0.082115 | 0.148037 |
| J10_STRUCTURAL_BLEND | 217 | 11 | 0.286258 | 0.030036 | 0.779483 | 0.497696 | 0.521829 | 0.040356 | 0.039793 | 0.645161 | 0.090629 | 0.211167 |
| M_PERSIST_PLACEBO_BLOCKS | 217 | 11 | 0.287825 | 0.028033 | 0.788331 | 0.557604 | 0.573943 | 0.034814 | 0.033412 | 0.534562 | 0.068307 | 0.205136 |
| J10_HISTORY_SHRINK | 217 | 11 | 0.288388 | 0.027539 | 0.781163 | 0.479263 | 0.510095 | 0.035862 | 0.034673 | 0.649770 | 0.085226 | 0.177770 |
| S_ELASTIC | 217 | 11 | 0.291443 | 0.033110 | 0.810165 | 0.525346 | 0.542925 | 0.043480 | 0.044228 | 0.626728 | 0.088017 | 0.219786 |
| P_CLUSTER | 217 | 11 | 0.300537 | 0.033221 | 0.831185 | 0.534562 | 0.553451 | 0.043605 | 0.043810 | 0.612903 | 0.086734 | 0.230629 |
| J9_STATIC | 217 | 11 | 0.302141 | 0.027909 | 0.816006 | 0.470046 | 0.503063 | 0.035493 | 0.035334 | 0.608295 | 0.079193 | 0.208504 |

## Paired uncertainty around selected weekly claims

| horizon | cohort | model | baseline | metric | n | candidate | control | gain | block10_adjusted_low | block10_adjusted_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | C85_SPREAD | HISTORY | brier | 265 | 0.263788 | 0.259048 | -0.004740 | -0.053540 | 0.044059 |
| 5 | combined | C85_SPREAD | HISTORY | crps | 265 | 0.011713 | 0.011340 | -0.000373 | -0.001928 | 0.001183 |
| 5 | combined | C85_SPREAD | NEUTRAL | brier | 265 | 0.263788 | 0.250000 | -0.013788 | -0.065712 | 0.038136 |
| 5 | combined | C85_SPREAD | NEUTRAL | crps | 265 | 0.011713 | 0.011058 | -0.000655 | -0.002245 | 0.000935 |
| 5 | combined | C85_SPREAD | P_CLUSTER | brier | 265 | 0.263788 | 0.236386 | -0.027402 | -0.092941 | 0.038137 |
| 5 | combined | C85_SPREAD | P_CLUSTER | crps | 265 | 0.011713 | 0.011775 | 0.000062 | -0.003415 | 0.003540 |
| 5 | combined | C85_SPREAD | J9_REL_SHRINK | brier | 265 | 0.263788 | 0.248725 | -0.015063 | -0.055916 | 0.025790 |
| 5 | combined | C85_SPREAD | J9_REL_SHRINK | crps | 265 | 0.011713 | 0.011014 | -0.000699 | -0.002104 | 0.000705 |
| 5 | combined | J10_HISTORY_SHRINK | HISTORY | brier | 265 | 0.242366 | 0.259048 | 0.016682 | -0.011416 | 0.044779 |
| 5 | combined | J10_HISTORY_SHRINK | HISTORY | crps | 265 | 0.010892 | 0.011340 | 0.000448 | -0.000637 | 0.001533 |
| 5 | combined | J10_HISTORY_SHRINK | NEUTRAL | brier | 265 | 0.242366 | 0.250000 | 0.007634 | -0.025994 | 0.041263 |
| 5 | combined | J10_HISTORY_SHRINK | NEUTRAL | crps | 265 | 0.010892 | 0.011058 | 0.000166 | -0.000868 | 0.001200 |
| 5 | combined | J10_HISTORY_SHRINK | P_CLUSTER | brier | 265 | 0.242366 | 0.236386 | -0.005979 | -0.063239 | 0.051280 |
| 5 | combined | J10_HISTORY_SHRINK | P_CLUSTER | crps | 265 | 0.010892 | 0.011775 | 0.000883 | -0.002052 | 0.003819 |
| 5 | combined | J10_HISTORY_SHRINK | J9_REL_SHRINK | brier | 265 | 0.242366 | 0.248725 | 0.006359 | -0.004824 | 0.017543 |
| 5 | combined | J10_HISTORY_SHRINK | J9_REL_SHRINK | crps | 265 | 0.010892 | 0.011014 | 0.000122 | -0.000360 | 0.000604 |
| 5 | combined | J10_STRUCTURAL_BLEND | HISTORY | brier | 265 | 0.236181 | 0.259048 | 0.022866 | -0.032861 | 0.078593 |
| 5 | combined | J10_STRUCTURAL_BLEND | HISTORY | crps | 265 | 0.011043 | 0.011340 | 0.000298 | -0.001994 | 0.002589 |
| 5 | combined | J10_STRUCTURAL_BLEND | NEUTRAL | brier | 265 | 0.236181 | 0.250000 | 0.013819 | -0.044333 | 0.071970 |
| 5 | combined | J10_STRUCTURAL_BLEND | NEUTRAL | crps | 265 | 0.011043 | 0.011058 | 0.000015 | -0.002165 | 0.002196 |
| 5 | combined | J10_STRUCTURAL_BLEND | P_CLUSTER | brier | 265 | 0.236181 | 0.236386 | 0.000205 | -0.044983 | 0.045393 |
| 5 | combined | J10_STRUCTURAL_BLEND | P_CLUSTER | crps | 265 | 0.011043 | 0.011775 | 0.000733 | -0.001421 | 0.002887 |
| 5 | combined | J10_STRUCTURAL_BLEND | J9_REL_SHRINK | brier | 265 | 0.236181 | 0.248725 | 0.012543 | -0.021248 | 0.046335 |
| 5 | combined | J10_STRUCTURAL_BLEND | J9_REL_SHRINK | crps | 265 | 0.011043 | 0.011014 | -0.000029 | -0.001625 | 0.001568 |
| 5 | combined | N_EQ_OFFICIAL | HISTORY | brier | 265 | 0.263910 | 0.259048 | -0.004862 | -0.067553 | 0.057829 |
| 5 | combined | N_EQ_OFFICIAL | HISTORY | crps | 265 | 0.011803 | 0.011340 | -0.000462 | -0.002568 | 0.001644 |
| 5 | combined | N_EQ_OFFICIAL | NEUTRAL | brier | 265 | 0.263910 | 0.250000 | -0.013910 | -0.078722 | 0.050902 |
| 5 | combined | N_EQ_OFFICIAL | NEUTRAL | crps | 265 | 0.011803 | 0.011058 | -0.000745 | -0.002808 | 0.001318 |
| 5 | combined | N_EQ_OFFICIAL | P_CLUSTER | brier | 265 | 0.263910 | 0.236386 | -0.027524 | -0.092377 | 0.037330 |
| 5 | combined | N_EQ_OFFICIAL | P_CLUSTER | crps | 265 | 0.011803 | 0.011775 | -0.000027 | -0.003183 | 0.003128 |
| 5 | combined | N_EQ_OFFICIAL | J9_REL_SHRINK | brier | 265 | 0.263910 | 0.248725 | -0.015185 | -0.061015 | 0.030645 |
| 5 | combined | N_EQ_OFFICIAL | J9_REL_SHRINK | crps | 265 | 0.011803 | 0.011014 | -0.000789 | -0.002436 | 0.000859 |
| 5 | combined | OMAX_BLOCKMEAN | HISTORY | brier | 265 | 0.260245 | 0.259048 | -0.001197 | -0.058174 | 0.055780 |
| 5 | combined | OMAX_BLOCKMEAN | HISTORY | crps | 265 | 0.011660 | 0.011340 | -0.000320 | -0.002126 | 0.001487 |
| 5 | combined | OMAX_BLOCKMEAN | NEUTRAL | brier | 265 | 0.260245 | 0.250000 | -0.010245 | -0.066782 | 0.046293 |
| 5 | combined | OMAX_BLOCKMEAN | NEUTRAL | crps | 265 | 0.011660 | 0.011058 | -0.000602 | -0.002322 | 0.001118 |
| 5 | combined | OMAX_BLOCKMEAN | P_CLUSTER | brier | 265 | 0.260245 | 0.236386 | -0.023858 | -0.091028 | 0.043311 |
| 5 | combined | OMAX_BLOCKMEAN | P_CLUSTER | crps | 265 | 0.011660 | 0.011775 | 0.000115 | -0.003157 | 0.003388 |
| 5 | combined | OMAX_BLOCKMEAN | J9_REL_SHRINK | brier | 265 | 0.260245 | 0.248725 | -0.011520 | -0.058822 | 0.035783 |
| 5 | combined | OMAX_BLOCKMEAN | J9_REL_SHRINK | crps | 265 | 0.011660 | 0.011014 | -0.000646 | -0.002191 | 0.000899 |
| 5 | combined | T_VOL_STUDENT | HISTORY | brier | 265 | 0.254899 | 0.259048 | 0.004149 | -0.035340 | 0.043638 |
| 5 | combined | T_VOL_STUDENT | HISTORY | crps | 265 | 0.011323 | 0.011340 | 0.000017 | -0.001298 | 0.001332 |
| 5 | combined | T_VOL_STUDENT | NEUTRAL | brier | 265 | 0.254899 | 0.250000 | -0.004899 | -0.048515 | 0.038718 |
| 5 | combined | T_VOL_STUDENT | NEUTRAL | crps | 265 | 0.011323 | 0.011058 | -0.000265 | -0.001621 | 0.001090 |
| 5 | combined | T_VOL_STUDENT | P_CLUSTER | brier | 265 | 0.254899 | 0.236386 | -0.018512 | -0.101942 | 0.064917 |
| 5 | combined | T_VOL_STUDENT | P_CLUSTER | crps | 265 | 0.011323 | 0.011775 | 0.000452 | -0.003267 | 0.004172 |
| 5 | combined | T_VOL_STUDENT | J9_REL_SHRINK | brier | 265 | 0.254899 | 0.248725 | -0.006174 | -0.039827 | 0.027479 |
| 5 | combined | T_VOL_STUDENT | J9_REL_SHRINK | crps | 265 | 0.011323 | 0.011014 | -0.000309 | -0.001340 | 0.000722 |

[Small-sample leaderboard](small-sample-leaderboard.csv) · [Temporal stability](temporal-stability-leaderboard.csv) · [Earlier results](earlier-leaderboard.csv) · [Later results](later-leaderboard.csv) · [Monthly results](monthly-leaderboard.csv) · [Incremental gains](incremental-information.csv) · [Research Pareto frontier](research-pareto.csv).

The Pareto analysis combines early and later Brier and CRPS, calibration error, median training use, effective complexity, cohort gap and, for weekly comparisons, the search-adjusted combined Brier lower gain bound versus history. It includes systems with measured dimensions on both cohorts. Empirical laws share return-distribution benchmarks but have a different model-complexity interpretation. Frozen leaders remain visible in the score and temporal tables.
