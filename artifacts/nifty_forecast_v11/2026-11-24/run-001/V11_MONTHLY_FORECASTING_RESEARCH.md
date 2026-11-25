# V11 Monthly Forecasting Research

There are 141 earlier and 76 later monthly origins, with 217 combined and only 11 disjoint windows. The earlier state references and later V8 smooth/lag/roll tests retain their historical evaluation slices. The 0.108239 later Brier of the V8 rolled state is a warning about interpreting the 0.132367 later smooth-state number. New tests use persistent breadth, concentration, phase selection, historical memory, normalized volatility, conditional risk and coherent mixtures.

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| NEUTRAL | 0.250000 | 0.250000 | 0.250000 | 0.024320 | 0.027460 | 0.025420 |
| T_VOL_STUDENT | 0.249400 | 0.299630 | 0.266992 | 0.028983 | 0.029349 | 0.029111 |
| O_ROT_PHASE1 | 0.299597 | 0.257930 | 0.285004 | 0.029673 | 0.029043 | 0.029452 |
| J11_BREADTH_ALL_HIST | 0.308519 | 0.269662 | 0.294910 | 0.027818 | 0.028533 | 0.028068 |
| M_EARLIEST_85 | 0.316382 | 0.268587 | 0.299643 | 0.028196 | 0.030207 | 0.028900 |
| P_CLUSTER | 0.332152 | 0.241883 | 0.300537 | 0.035523 | 0.028950 | 0.033221 |
| D_EQ_STUDENT | 0.304721 | 0.295300 | 0.301422 | 0.031587 | 0.027256 | 0.030070 |
| T_SIGNMAG | 0.283906 | 0.341502 | 0.304078 | 0.025359 | 0.030337 | 0.027102 |
| J11_STACK_CRPS | 0.321454 | 0.282331 | 0.307752 | 0.027871 | 0.027821 | 0.027854 |
| HISTORY | 0.324122 | 0.279282 | 0.308418 | 0.027004 | 0.028363 | 0.027480 |
| J11_MEMORY | 0.331359 | 0.312877 | 0.324886 | 0.030088 | 0.030678 | 0.030295 |
| B_EQ_PERM | 0.353647 | 0.283691 | 0.329146 | 0.032286 | 0.030692 | 0.031728 |
| B_PERSIST | 0.344198 | 0.304435 | 0.330272 | 0.032216 | 0.031485 | 0.031960 |
| L_PERSIST | 0.350425 | 0.331584 | 0.343827 | 0.030479 | 0.031883 | 0.030971 |
| REVERSION | 0.275046 | 0.475499 | 0.345251 | 0.026717 | 0.036790 | 0.030245 |
| B_EQ_SHIFT21 | 0.349267 | 0.345500 | 0.347948 | 0.031803 | 0.033362 | 0.032349 |
| D_EQ_SHARED | 0.320015 | 0.457015 | 0.367997 | 0.033847 | 0.042071 | 0.036727 |
| D_DERIV_RISK | 0.335096 | 0.437531 | 0.370972 | 0.042892 | 0.037251 | 0.040917 |
| I_RISK_EQ | 0.340080 | 0.500798 | 0.396368 | 0.038414 | 0.036805 | 0.037850 |
| V6_MONTH_LAG1 | — | 0.175091 | — | — | 0.024530 | — |
| V6_MONTH_STATE | — | 0.178345 | — | — | 0.024823 | — |
| V8_MS_ROLL | — | 0.108239 | — | — | 0.024107 | — |
| V8_MS_WINDOW | — | 0.132367 | — | — | 0.020474 | — |

The symmetric neutral reference scores **0.250000 Brier** and **0.025420 CRPS**. Large scores from isolated phases or heavily overlapping dates warrant a matched check and comparison against shifted cases. Full monthly endpoint results and realized volatility are distinct, and monthly uncertainty is summarized descriptively with disjoint dates and deletion tests. [Monthly phase stress](stress-comparisons.csv) · [Monthly calibration](leaderboard.csv).
