# NIFTY V18 — Event-informed NIFTY forecasting

Both original objectives keep the same price reference and realized endpoints, with **265 five-session and 217 21-session origins**. The forecasts at prior-session **17:00 IST** and next-morning **08:55** use their own availability matrices. V14 native scores appear at their original guard. The V14 overlay uses incremental event inputs fixed at 08:55 against the archived distribution whose publication guard is later. The study tests fundamentals alone, corporate events on top of the structural parent, additive corrections of chronological past errors, a two-to-130-day information representation, event-conditioned location and tail width, and a fixed mixture. The fixed mixture uses order-spaced atoms from two laws. Each empirical law is retained or reproducible from the case ledger and preserved parent.

| horizon | cutoff | model | n | disjoint | brier | crps | log loss | rank correlation | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_v14_guard | V14_event_overlay | 265 | 53 | 0.223481 | 0.010318 | 0.637789 | 0.343147 | 0.818868 | 0.045700 |
| 5 | native_v14_guard | V14_exact | 265 | 53 | 0.228529 | 0.010457 | 0.648943 | 0.349532 | 0.826415 | 0.045780 |
| 5 | preauction_0855 | clock_structural | 265 | 53 | 0.238274 | 0.010658 | 0.668337 | 0.205777 | 0.766038 | 0.041040 |
| 5 | preauction_0855 | component_plus_residual | 265 | 53 | 0.238003 | 0.010309 | 0.668084 | 0.290602 | 0.758491 | 0.041019 |
| 5 | preauction_0855 | event_conditioned_law | 265 | 53 | 0.253840 | 0.011342 | 0.707006 | 0.100025 | 0.694340 | 0.036921 |
| 5 | preauction_0855 | expectation_repricing | 265 | 53 | 0.243264 | 0.011068 | 0.679955 | 0.140211 | 0.743396 | 0.040988 |
| 5 | preauction_0855 | fixed_event_mixture | 265 | 53 | 0.241239 | 0.010829 | 0.674750 | 0.169969 | 0.762264 | 0.041328 |
| 5 | preauction_0855 | fundamental_augmentation | 265 | 53 | 0.248263 | 0.011103 | 0.689668 | 0.140003 | 0.732075 | 0.040994 |
| 5 | preauction_0855 | fundamental_only | 265 | 53 | 0.257659 | 0.011245 | 0.709475 | -0.027437 | 0.747170 | 0.040975 |
| 5 | preauction_0855 | neutral | 265 | 53 | 0.250000 | 0.011089 | 0.693147 | -0.017280 | 0.754717 | 0.042146 |
| 5 | preauction_0855 | text_given_counts | 265 | 53 | 0.244526 | 0.010928 | 0.681494 | 0.147523 | 0.747170 | 0.041044 |
| 5 | previous_1700 | clock_structural | 265 | 53 | 0.238605 | 0.010721 | 0.669387 | 0.183676 | 0.762264 | 0.040973 |
| 5 | previous_1700 | component_plus_residual | 265 | 53 | 0.236585 | 0.010658 | 0.665638 | 0.221722 | 0.766038 | 0.040965 |
| 5 | previous_1700 | event_conditioned_law | 265 | 53 | 0.251206 | 0.011444 | 0.703475 | 0.077329 | 0.675472 | 0.036926 |
| 5 | previous_1700 | expectation_repricing | 265 | 53 | 0.242793 | 0.011141 | 0.681602 | 0.138831 | 0.739623 | 0.040913 |
| 5 | previous_1700 | fixed_event_mixture | 265 | 53 | 0.239885 | 0.010879 | 0.672989 | 0.162069 | 0.762264 | 0.041304 |
| 5 | previous_1700 | fundamental_augmentation | 265 | 53 | 0.248308 | 0.011194 | 0.690496 | 0.122314 | 0.720755 | 0.040923 |
| 5 | previous_1700 | fundamental_only | 265 | 53 | 0.257782 | 0.011296 | 0.709525 | -0.034085 | 0.747170 | 0.040906 |
| 5 | previous_1700 | neutral | 265 | 53 | 0.250000 | 0.011089 | 0.693147 | -0.019629 | 0.762264 | 0.042115 |
| 5 | previous_1700 | text_given_counts | 265 | 53 | 0.241012 | 0.010927 | 0.675256 | 0.142268 | 0.739623 | 0.040973 |
| 21 | native_v14_guard | V14_event_overlay | 217 | 11 | 0.259808 | 0.025409 | 0.713467 | -0.072469 | 0.677419 | 0.071355 |
| 21 | native_v14_guard | V14_exact | 217 | 11 | 0.245042 | 0.024989 | 0.683095 | -0.032590 | 0.668203 | 0.071794 |
| 21 | preauction_0855 | clock_structural | 217 | 11 | 0.302805 | 0.028519 | 0.859339 | -0.135280 | 0.663594 | 0.089469 |
| 21 | preauction_0855 | component_plus_residual | 217 | 11 | 0.300952 | 0.028698 | 0.865588 | -0.124873 | 0.617512 | 0.089434 |
| 21 | preauction_0855 | event_conditioned_law | 217 | 11 | 0.317850 | 0.030435 | 0.930412 | -0.082564 | 0.552995 | 0.088053 |
| 21 | preauction_0855 | expectation_repricing | 217 | 11 | 0.304356 | 0.029786 | 0.872965 | -0.128954 | 0.649770 | 0.089096 |
| 21 | preauction_0855 | fixed_event_mixture | 217 | 11 | 0.306346 | 0.029038 | 0.871928 | -0.106592 | 0.663594 | 0.087881 |
| 21 | preauction_0855 | fundamental_augmentation | 217 | 11 | 0.312599 | 0.029850 | 0.899025 | -0.109586 | 0.612903 | 0.089011 |
| 21 | preauction_0855 | fundamental_only | 217 | 11 | 0.295998 | 0.027676 | 0.801835 | -0.283800 | 0.691244 | 0.089578 |
| 21 | preauction_0855 | neutral | 217 | 11 | 0.250000 | 0.025543 | 0.693147 | 0.141568 | 0.691244 | 0.078299 |
| 21 | preauction_0855 | text_given_counts | 217 | 11 | 0.346838 | 0.030377 | 0.976685 | -0.167449 | 0.612903 | 0.089336 |
| 21 | previous_1700 | clock_structural | 217 | 11 | 0.300452 | 0.028321 | 0.847591 | -0.118709 | 0.658986 | 0.089081 |
| 21 | previous_1700 | component_plus_residual | 217 | 11 | 0.299021 | 0.028360 | 0.846990 | -0.116868 | 0.654378 | 0.089079 |
| 21 | previous_1700 | event_conditioned_law | 217 | 11 | 0.314119 | 0.029895 | 0.914393 | -0.047608 | 0.562212 | 0.087696 |
| 21 | previous_1700 | expectation_repricing | 217 | 11 | 0.301053 | 0.029415 | 0.862033 | -0.089404 | 0.640553 | 0.088698 |
| 21 | previous_1700 | fixed_event_mixture | 217 | 11 | 0.302573 | 0.028691 | 0.857259 | -0.067575 | 0.663594 | 0.087468 |
| 21 | previous_1700 | fundamental_augmentation | 217 | 11 | 0.306809 | 0.029362 | 0.879321 | -0.067764 | 0.626728 | 0.088611 |
| 21 | previous_1700 | fundamental_only | 217 | 11 | 0.285929 | 0.027118 | 0.775898 | -0.230175 | 0.705069 | 0.089173 |
| 21 | previous_1700 | neutral | 217 | 11 | 0.250000 | 0.025545 | 0.693147 | 0.148183 | 0.691244 | 0.078141 |
| 21 | previous_1700 | text_given_counts | 217 | 11 | 0.347494 | 0.030319 | 0.976809 | -0.161132 | 0.608295 | 0.088947 |

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | fundamental_only | clock_structural | brier | 265 | 53 | 0.257659 | 0.238274 | -0.019385 | -0.060329 | 0.021560 |
| 5 | preauction_0855 | fundamental_only | clock_structural | crps | 265 | 53 | 0.011245 | 0.010658 | -0.000587 | -0.002127 | 0.000953 |
| 5 | preauction_0855 | multi_timescale | clock_structural | brier | 265 | 53 | 0.244634 | 0.238274 | -0.006359 | -0.025281 | 0.012562 |
| 5 | preauction_0855 | multi_timescale | clock_structural | crps | 265 | 53 | 0.011056 | 0.010658 | -0.000398 | -0.001017 | 0.000220 |
| 5 | preauction_0855 | event_conditioned_law | clock_structural | brier | 265 | 53 | 0.253840 | 0.238274 | -0.015566 | -0.049381 | 0.018250 |
| 5 | preauction_0855 | event_conditioned_law | clock_structural | crps | 265 | 53 | 0.011342 | 0.010658 | -0.000684 | -0.001739 | 0.000372 |
| 5 | preauction_0855 | fixed_event_mixture | clock_structural | brier | 265 | 53 | 0.241239 | 0.238274 | -0.002964 | -0.013013 | 0.007084 |
| 5 | preauction_0855 | fixed_event_mixture | clock_structural | crps | 265 | 53 | 0.010829 | 0.010658 | -0.000170 | -0.000504 | 0.000163 |
| 5 | preauction_0855 | clock_component_event | component_plus_residual | brier | 265 | 53 | 0.246855 | 0.238003 | -0.008852 | -0.027118 | 0.009414 |
| 5 | preauction_0855 | clock_component_event | component_plus_residual | crps | 265 | 53 | 0.010802 | 0.010309 | -0.000493 | -0.001142 | 0.000156 |
| 5 | preauction_0855 | text_given_counts | clock_structural | brier | 265 | 53 | 0.244526 | 0.238274 | -0.006251 | -0.020548 | 0.008045 |
| 5 | preauction_0855 | text_given_counts | clock_structural | crps | 265 | 53 | 0.010928 | 0.010658 | -0.000270 | -0.000586 | 0.000045 |
| 5 | preauction_0855 | fundamental_augmentation | clock_structural | brier | 265 | 53 | 0.248263 | 0.238274 | -0.009989 | -0.031308 | 0.011331 |
| 5 | preauction_0855 | fundamental_augmentation | clock_structural | crps | 265 | 53 | 0.011103 | 0.010658 | -0.000445 | -0.001092 | 0.000202 |
| 5 | preauction_0855 | clock_component_event | clock_structural | brier | 265 | 53 | 0.246855 | 0.238274 | -0.008581 | -0.038241 | 0.021080 |
| 5 | preauction_0855 | clock_component_event | clock_structural | crps | 265 | 53 | 0.010802 | 0.010658 | -0.000144 | -0.001244 | 0.000957 |
| 5 | preauction_0855 | multi_timescale | component_plus_residual | brier | 265 | 53 | 0.244634 | 0.238003 | -0.006631 | -0.030752 | 0.017491 |
| 5 | preauction_0855 | multi_timescale | component_plus_residual | crps | 265 | 53 | 0.011056 | 0.010309 | -0.000748 | -0.001689 | 0.000193 |
| 5 | preauction_0855 | fundamental_augmentation | component_plus_residual | brier | 265 | 53 | 0.248263 | 0.238003 | -0.010260 | -0.033513 | 0.012994 |
| 5 | preauction_0855 | fundamental_augmentation | component_plus_residual | crps | 265 | 53 | 0.011103 | 0.010309 | -0.000795 | -0.001633 | 0.000044 |
| 5 | preauction_0855 | fixed_event_mixture | component_plus_residual | brier | 265 | 53 | 0.241239 | 0.238003 | -0.003235 | -0.022014 | 0.015543 |
| 5 | preauction_0855 | fixed_event_mixture | component_plus_residual | crps | 265 | 53 | 0.010829 | 0.010309 | -0.000520 | -0.001287 | 0.000247 |
| 5 | preauction_0855 | event_conditioned_law | component_plus_residual | brier | 265 | 53 | 0.253840 | 0.238003 | -0.015837 | -0.053337 | 0.021663 |
| 5 | preauction_0855 | event_conditioned_law | component_plus_residual | crps | 265 | 53 | 0.011342 | 0.010309 | -0.001033 | -0.002340 | 0.000274 |
| 5 | previous_1700 | fundamental_only | clock_structural | brier | 265 | 53 | 0.257782 | 0.238605 | -0.019177 | -0.065336 | 0.026981 |
| 5 | previous_1700 | fundamental_only | clock_structural | crps | 265 | 53 | 0.011296 | 0.010721 | -0.000574 | -0.002262 | 0.001113 |
| 5 | previous_1700 | multi_timescale | clock_structural | brier | 265 | 53 | 0.243827 | 0.238605 | -0.005223 | -0.024897 | 0.014452 |
| 5 | previous_1700 | multi_timescale | clock_structural | crps | 265 | 53 | 0.011134 | 0.010721 | -0.000413 | -0.001036 | 0.000210 |
| 5 | previous_1700 | event_conditioned_law | clock_structural | brier | 265 | 53 | 0.251206 | 0.238605 | -0.012601 | -0.047289 | 0.022087 |
| 5 | previous_1700 | event_conditioned_law | clock_structural | crps | 265 | 53 | 0.011444 | 0.010721 | -0.000723 | -0.001859 | 0.000414 |
| 5 | previous_1700 | fixed_event_mixture | clock_structural | brier | 265 | 53 | 0.239885 | 0.238605 | -0.001281 | -0.011996 | 0.009434 |
| 5 | previous_1700 | fixed_event_mixture | clock_structural | crps | 265 | 53 | 0.010879 | 0.010721 | -0.000157 | -0.000512 | 0.000197 |
| 5 | previous_1700 | clock_component_event | component_plus_residual | brier | 265 | 53 | 0.243625 | 0.236585 | -0.007040 | -0.028280 | 0.014200 |
| 5 | previous_1700 | clock_component_event | component_plus_residual | crps | 265 | 53 | 0.011094 | 0.010658 | -0.000436 | -0.001168 | 0.000295 |
| 5 | previous_1700 | text_given_counts | clock_structural | brier | 265 | 53 | 0.241012 | 0.238605 | -0.002407 | -0.015052 | 0.010238 |
| 5 | previous_1700 | text_given_counts | clock_structural | crps | 265 | 53 | 0.010927 | 0.010721 | -0.000206 | -0.000532 | 0.000121 |
| 5 | previous_1700 | fundamental_augmentation | clock_structural | brier | 265 | 53 | 0.248308 | 0.238605 | -0.009703 | -0.032993 | 0.013586 |
| 5 | previous_1700 | fundamental_augmentation | clock_structural | crps | 265 | 53 | 0.011194 | 0.010721 | -0.000473 | -0.001176 | 0.000231 |
| 5 | previous_1700 | clock_component_event | clock_structural | brier | 265 | 53 | 0.243625 | 0.238605 | -0.005020 | -0.033094 | 0.023054 |
| 5 | previous_1700 | clock_component_event | clock_structural | crps | 265 | 53 | 0.011094 | 0.010721 | -0.000373 | -0.001274 | 0.000528 |
| 5 | previous_1700 | multi_timescale | component_plus_residual | brier | 265 | 53 | 0.243827 | 0.236585 | -0.007243 | -0.029161 | 0.014675 |
| 5 | previous_1700 | multi_timescale | component_plus_residual | crps | 265 | 53 | 0.011134 | 0.010658 | -0.000476 | -0.001189 | 0.000237 |
| 5 | previous_1700 | fundamental_augmentation | component_plus_residual | brier | 265 | 53 | 0.248308 | 0.236585 | -0.011723 | -0.033590 | 0.010143 |

| horizon | cutoff | subset | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_v14_guard | full | brier | 265 | 53 | 0.223481 | 0.228529 | 0.005048 | -0.010429 | 0.020526 |
| 5 | native_v14_guard | full | crps | 265 | 53 | 0.010318 | 0.010457 | 0.000139 | -0.000477 | 0.000755 |
| 21 | native_v14_guard | full | brier | 217 | 11 | 0.259808 | 0.245042 | -0.014766 | -0.068653 | 0.039121 |
| 21 | native_v14_guard | full | crps | 217 | 11 | 0.025409 | 0.024989 | -0.000420 | -0.003014 | 0.002173 |
| 5 | native_v14_guard | adjustment_mature | brier | 223 | 45 | 0.218529 | 0.224529 | 0.005999 | -0.011843 | 0.023841 |
| 5 | native_v14_guard | adjustment_mature | crps | 223 | 45 | 0.011074 | 0.011239 | 0.000165 | -0.000588 | 0.000918 |
| 21 | native_v14_guard | adjustment_mature | brier | 159 | 8 | 0.261447 | 0.241294 | -0.020153 | -0.093935 | 0.053630 |
| 21 | native_v14_guard | adjustment_mature | crps | 159 | 8 | 0.025620 | 0.025046 | -0.000574 | -0.003983 | 0.002836 |

[Full endpoint forecast list](original-event-forecasts.csv.gz) · [Original horizon return laws](original-event-laws.npz) · [Full identical-cutoff comparisons](endpoint-paired-comparisons.csv) · [Native V14 overlays](protected-v14-matched-overlays.csv) · [Post-open residual horizon overlays](postopen-event-matched.csv)
