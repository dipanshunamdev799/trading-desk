# V10 Monthly Sample Efficiency

The comparable sample has **141 earlier** and **76 later** origins, **217 combined**. There are **11** disjoint windows in the combined chronology and **4** in the later cohort. Later high accuracy from smoothed state was historically sensitive to lag and shift controls. V10 tests different estimation mechanisms and declines to use rolling counts as independent monthly replications.

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| NEUTRAL | 0.250000 | 0.250000 | 0.250000 | 0.024320 | 0.027460 | 0.025420 |
| T_VOL_STUDENT | 0.249400 | 0.299630 | 0.266992 | 0.028983 | 0.029349 | 0.029111 |
| J10_HISTORY_SHRINK | 0.300622 | 0.265691 | 0.288388 | 0.027150 | 0.028262 | 0.027539 |
| S_ELASTIC | 0.329191 | 0.221413 | 0.291443 | 0.035809 | 0.028102 | 0.033110 |
| P_CLUSTER | 0.332152 | 0.241883 | 0.300537 | 0.035523 | 0.028950 | 0.033221 |
| T_SIGNMAG | 0.283906 | 0.341502 | 0.304078 | 0.025359 | 0.030337 | 0.027102 |
| HISTORY | 0.324122 | 0.279282 | 0.308418 | 0.027004 | 0.028363 | 0.027480 |
| O126_PHASE0 | 0.251668 | 0.460707 | 0.324880 | 0.028795 | 0.039260 | 0.032460 |
| EC_126_GLS_EMPIRICAL | 0.266536 | 0.450144 | 0.330841 | 0.031972 | 0.039184 | 0.034498 |
| REVERSION | 0.275046 | 0.475499 | 0.345251 | 0.026717 | 0.036790 | 0.030245 |
| T_SPLIT | 0.282421 | 0.474538 | 0.349707 | 0.031716 | 0.040113 | 0.034657 |
| T_OVERNIGHT | 0.282421 | 0.474538 | 0.349707 | 0.031716 | 0.040113 | 0.034657 |
| S_DISTRIBUTED | 0.293326 | 0.484978 | 0.360448 | 0.028672 | 0.038211 | 0.032013 |
| OMAX_BLOCKMEAN | 0.309712 | 0.458426 | 0.361796 | 0.029361 | 0.038219 | 0.032463 |
| X_ADAPT | 0.300547 | 0.488334 | 0.366316 | 0.030205 | 0.036499 | 0.032409 |
| X_MULTI | 0.305125 | 0.479849 | 0.366318 | 0.029841 | 0.036288 | 0.032099 |
| S_PERSIST | 0.348047 | 0.439146 | 0.379952 | 0.032911 | 0.036475 | 0.034159 |
| V6_MONTH_LAG1 | — | 0.175091 | — | — | 0.024530 | — |
| V6_MONTH_STATE | — | 0.178345 | — | — | 0.024823 | — |
| V7_M_STATE_SHIFT21 | — | 0.187515 | — | — | 0.024168 | — |
| V7_M_STATE_SHIFT5 | — | 0.190366 | — | — | 0.023773 | — |
| V8_MS_ROLL | — | 0.108239 | — | — | 0.024107 | — |
| V8_MS_WINDOW | — | 0.132367 | — | — | 0.020474 | — |

## Shifted and block-permuted state controls on the combined chronology

| model | n | disjoint | brier | crps | accuracy | balanced_accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| M_PERSIST_PLACEBO_BLOCKS | 217 | 11 | 0.287825 | 0.028033 | 0.557604 | 0.573943 |
| M_DISTRIBUTED_PLACEBO_BLOCKS | 217 | 11 | 0.341702 | 0.030785 | 0.447005 | 0.459275 |
| M_DISTRIBUTED_PLACEBO_42 | 217 | 11 | 0.362187 | 0.032680 | 0.433180 | 0.445815 |
| X_SHIFT | 217 | 11 | 0.364871 | 0.031685 | 0.442396 | 0.448188 |
| M_PERSIST_PLACEBO_21 | 217 | 11 | 0.369211 | 0.031990 | 0.433180 | 0.445815 |
| M_DISTRIBUTED_PLACEBO_5 | 217 | 11 | 0.370719 | 0.032523 | 0.387097 | 0.393184 |
| M_PERSIST_PLACEBO_5 | 217 | 11 | 0.374566 | 0.033979 | 0.400922 | 0.415962 |
| M_DISTRIBUTED_PLACEBO_21 | 217 | 11 | 0.378169 | 0.032511 | 0.428571 | 0.438223 |
| M_PERSIST_PLACEBO_42 | 217 | 11 | 0.380291 | 0.034205 | 0.364055 | 0.372692 |

The fixed 0.5 symmetric model achieved combined Brier **0.250000** and CRPS **0.025420**. The monthly 126-row volatility Student-t fit and the 300-row fit require their actual coverage and comparison controls. More rows in a panel or different staggered phases cannot remove the small number of distinct monthly episodes. See [full monthly ranking and coverage](monthly-leaderboard.csv), [matched learning curves](learning-curve-matched.csv), and [disjoint phases and leave-calendar-month stress](temporal-and-disjoint-stress.csv). Shifts and block randomizations act only within estimation dates for diagnosis.
