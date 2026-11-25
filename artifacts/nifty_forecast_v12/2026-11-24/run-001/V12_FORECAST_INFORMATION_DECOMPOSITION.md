# V12 Forecast Information Decomposition

Expert novelty is measured using matched p(up), expected returns, distribution widths, signed directional and return errors, shared worst-decile dates, directional disagreement, and the energy distance between complete laws. Earlier, later and prior-volatility slices repeat the diagnostics. A high correlation can coexist with some information that matters in a tail. The fixed additions and leave-one-out experiments score the remaining law on identical endpoints, including calibration.

Exact aliases are canonicalized using a saved source identity and byte-exact atom/weight checks. There are **964** matched equality checks after appending two literal copies, including learned stacking after canonicalization. The naive extra-weight variant verifies what happens when copies are counted again. Similarity clustering sets equal cluster weight and keeps each distinct member with positive mass. Group balance separately uses statistical, phase, market-risk, historical and calibrated-shape roles.

| first | second | n | probability_corr | location_corr | width_corr | directional_error_corr | return_error_corr | shared_worst_decile | direction_disagreement | energy_distance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V12_STAT | V12_IV_SCALE | 265 | 0.990047 | 1.000000 | 0.844301 | 0.997844 | 1.000000 | 0.090566 | 0.000000 | 0.000149 |
| V12_STAT | V12_JOINT_IV | 265 | 0.952231 | 0.975685 | 0.820479 | 0.996296 | 0.992765 | 0.083019 | 0.098113 | 0.000289 |
| V12_STAT | PH_NATIVE_PHASE_MIXTURE | 265 | 0.856828 | 0.891328 | 0.809986 | 0.981549 | 0.979577 | 0.075472 | 0.173585 | 0.000813 |
| V12_STAT | V12_HIST | 265 | 0.343973 | 0.324525 | 0.221762 | 0.968397 | 0.934801 | 0.060377 | 0.483019 | 0.001676 |
| V12_IV_SCALE | V12_JOINT_IV | 265 | 0.953500 | 0.975685 | 0.957923 | 0.992880 | 0.992765 | 0.083019 | 0.098113 | 0.000220 |
| V12_IV_SCALE | PH_NATIVE_PHASE_MIXTURE | 265 | 0.866238 | 0.891328 | 0.580785 | 0.983378 | 0.979577 | 0.075472 | 0.173585 | 0.000899 |
| V12_IV_SCALE | V12_HIST | 265 | 0.292728 | 0.324525 | 0.027278 | 0.953884 | 0.934801 | 0.052830 | 0.483019 | 0.001765 |
| V12_JOINT_IV | PH_NATIVE_PHASE_MIXTURE | 265 | 0.826232 | 0.864808 | 0.553652 | 0.977098 | 0.970144 | 0.060377 | 0.218868 | 0.001221 |
| V12_JOINT_IV | V12_HIST | 265 | 0.255185 | 0.315858 | -0.020690 | 0.973150 | 0.962411 | 0.064151 | 0.483019 | 0.001116 |
| PH_NATIVE_PHASE_MIXTURE | V12_HIST | 265 | 0.222312 | 0.213174 | 0.358475 | 0.939114 | 0.906265 | 0.049057 | 0.505660 | 0.002890 |

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | J12_ADD_PH_NATIVE_PHASE_MIXTURE | J12_STAT_HIST_CONTROL | brier | 265 | 53 | 0.239468 | 0.247718 | 0.008249 | -0.006444 | 0.022943 |
| 5 | combined | J12_ADD_PH_NATIVE_PHASE_MIXTURE | J12_STAT_HIST_CONTROL | crps | 265 | 53 | 0.010734 | 0.010849 | 0.000115 | -0.000425 | 0.000656 |
| 5 | combined | J12_ADD_V12_HIST | J12_STAT_HIST_CONTROL | brier | 265 | 53 | 0.247718 | 0.247718 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_ADD_V12_HIST | J12_STAT_HIST_CONTROL | crps | 265 | 53 | 0.010849 | 0.010849 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_ADD_V12_IV_SCALE | J12_STAT_HIST_CONTROL | brier | 265 | 53 | 0.244899 | 0.247718 | 0.002819 | -0.007150 | 0.012787 |
| 5 | combined | J12_ADD_V12_IV_SCALE | J12_STAT_HIST_CONTROL | crps | 265 | 53 | 0.010756 | 0.010849 | 0.000093 | -0.000273 | 0.000458 |
| 5 | combined | J12_ADD_V12_JOINT_IV | J12_STAT_HIST_CONTROL | brier | 265 | 53 | 0.246317 | 0.247718 | 0.001401 | -0.006307 | 0.009109 |
| 5 | combined | J12_ADD_V12_JOINT_IV | J12_STAT_HIST_CONTROL | crps | 265 | 53 | 0.010807 | 0.010849 | 0.000043 | -0.000213 | 0.000298 |
| 5 | combined | J12_ADD_V12_STAT | J12_STAT_HIST_CONTROL | brier | 265 | 53 | 0.247718 | 0.247718 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_ADD_V12_STAT | J12_STAT_HIST_CONTROL | crps | 265 | 53 | 0.010849 | 0.010849 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_CANONICAL | J12_EQUAL | brier | 265 | 53 | 0.240787 | 0.240787 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_CANONICAL | J12_EQUAL | crps | 265 | 53 | 0.010712 | 0.010712 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_DUPLICATE_CANONICAL | J12_CANONICAL | brier | 265 | 53 | 0.240787 | 0.240787 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_DUPLICATE_CANONICAL | J12_CANONICAL | crps | 265 | 53 | 0.010712 | 0.010712 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_DUPLICATE_NAIVE | J12_EQUAL | brier | 265 | 53 | 0.241626 | 0.240787 | -0.000839 | -0.003786 | 0.002108 |
| 5 | combined | J12_DUPLICATE_NAIVE | J12_EQUAL | crps | 265 | 53 | 0.010716 | 0.010712 | -0.000004 | -0.000177 | 0.000170 |
| 5 | combined | J12_EQUAL | V12_STAT | brier | 265 | 53 | 0.240787 | 0.244333 | 0.003547 | -0.006874 | 0.013967 |
| 5 | combined | J12_EQUAL | V12_STAT | crps | 265 | 53 | 0.010712 | 0.010777 | 0.000065 | -0.000535 | 0.000666 |
| 5 | combined | J12_GROUP_BALANCED | J12_EQUAL | brier | 265 | 53 | 0.240188 | 0.240787 | 0.000599 | -0.002341 | 0.003539 |
| 5 | combined | J12_GROUP_BALANCED | J12_EQUAL | crps | 265 | 53 | 0.010715 | 0.010712 | -0.000003 | -0.000108 | 0.000101 |
| 5 | combined | J12_HISTORICAL_MARKET | V12_STAT | brier | 265 | 53 | 0.244444 | 0.244333 | -0.000111 | -0.009223 | 0.009002 |
| 5 | combined | J12_HISTORICAL_MARKET | V12_STAT | crps | 265 | 53 | 0.010739 | 0.010777 | 0.000038 | -0.000497 | 0.000573 |
| 5 | combined | J12_OMIT_PH_NATIVE_PHASE_MIXTURE | J12_EQUAL | brier | 265 | 53 | 0.244827 | 0.240787 | -0.004041 | -0.011843 | 0.003761 |
| 5 | combined | J12_OMIT_PH_NATIVE_PHASE_MIXTURE | J12_EQUAL | crps | 265 | 53 | 0.010758 | 0.010712 | -0.000046 | -0.000333 | 0.000241 |
| 5 | combined | J12_OMIT_V12_HIST | J12_EQUAL | brier | 265 | 53 | 0.239910 | 0.240787 | 0.000877 | -0.008687 | 0.010441 |
| 5 | combined | J12_OMIT_V12_HIST | J12_EQUAL | crps | 265 | 53 | 0.010719 | 0.010712 | -0.000007 | -0.000421 | 0.000407 |
| 5 | combined | J12_OMIT_V12_IV_SCALE | J12_EQUAL | brier | 265 | 53 | 0.240587 | 0.240787 | 0.000200 | -0.003657 | 0.004057 |
| 5 | combined | J12_OMIT_V12_IV_SCALE | J12_EQUAL | crps | 265 | 53 | 0.010728 | 0.010712 | -0.000016 | -0.000161 | 0.000128 |
| 5 | combined | J12_OMIT_V12_JOINT_IV | J12_EQUAL | brier | 265 | 53 | 0.239895 | 0.240787 | 0.000891 | -0.002757 | 0.004539 |
| 5 | combined | J12_OMIT_V12_JOINT_IV | J12_EQUAL | crps | 265 | 53 | 0.010706 | 0.010712 | 0.000006 | -0.000106 | 0.000118 |
| 5 | combined | J12_OMIT_V12_STAT | J12_EQUAL | brier | 265 | 53 | 0.240167 | 0.240787 | 0.000620 | -0.001942 | 0.003182 |
| 5 | combined | J12_OMIT_V12_STAT | J12_EQUAL | crps | 265 | 53 | 0.010718 | 0.010712 | -0.000006 | -0.000160 | 0.000147 |
| 5 | combined | J12_PHASE_MARKET | PH_NATIVE_PHASE_MIXTURE | brier | 265 | 53 | 0.236247 | 0.233211 | -0.003036 | -0.021971 | 0.015898 |
| 5 | combined | J12_PHASE_MARKET | PH_NATIVE_PHASE_MIXTURE | crps | 265 | 53 | 0.010718 | 0.010980 | 0.000262 | -0.000567 | 0.001091 |
| 5 | combined | J12_Q_CROSS | P12_Q_PHYSICAL_MIX | brier | 265 | 53 | 0.244623 | 0.244491 | -0.000132 | -0.003586 | 0.003322 |
| 5 | combined | J12_Q_CROSS | P12_Q_PHYSICAL_MIX | crps | 265 | 53 | 0.010709 | 0.010704 | -0.000005 | -0.000137 | 0.000127 |
| 5 | combined | J12_Q_EQUAL | J12_EQUAL | brier | 265 | 53 | 0.241666 | 0.240787 | -0.000880 | -0.003997 | 0.002238 |
| 5 | combined | J12_Q_EQUAL | J12_EQUAL | crps | 265 | 53 | 0.010680 | 0.010712 | 0.000032 | -0.000076 | 0.000139 |
| 5 | combined | J12_Q_GROUP | J12_Q_EQUAL | brier | 265 | 53 | 0.241437 | 0.241666 | 0.000229 | -0.002442 | 0.002900 |
| 5 | combined | J12_Q_GROUP | J12_Q_EQUAL | crps | 265 | 53 | 0.010677 | 0.010680 | 0.000004 | -0.000089 | 0.000096 |
| 5 | combined | J12_Q_HISTORICAL | P12_Q_HIST_FALLBACK | brier | 265 | 53 | 0.247102 | 0.245870 | -0.001231 | -0.006002 | 0.003539 |
| 5 | combined | J12_Q_HISTORICAL | P12_Q_HIST_FALLBACK | crps | 265 | 53 | 0.010759 | 0.010727 | -0.000032 | -0.000257 | 0.000193 |
| 5 | combined | J12_Q_STACK | J12_Q_EQUAL | brier | 265 | 53 | 0.242103 | 0.241666 | -0.000437 | -0.001401 | 0.000527 |
| 5 | combined | J12_Q_STACK | J12_Q_EQUAL | crps | 265 | 53 | 0.010699 | 0.010680 | -0.000019 | -0.000060 | 0.000022 |
| 5 | combined | J12_SIMILARITY_CLUSTERS | J12_EQUAL | brier | 265 | 53 | 0.240520 | 0.240787 | 0.000266 | -0.002796 | 0.003328 |
| 5 | combined | J12_SIMILARITY_CLUSTERS | J12_EQUAL | crps | 265 | 53 | 0.010730 | 0.010712 | -0.000018 | -0.000163 | 0.000127 |
| 5 | combined | J12_STACK_BRIER | J12_CANONICAL | brier | 265 | 53 | 0.241245 | 0.240787 | -0.000459 | -0.003021 | 0.002104 |
| 5 | combined | J12_STACK_BRIER | J12_CANONICAL | crps | 265 | 53 | 0.010758 | 0.010712 | -0.000046 | -0.000148 | 0.000057 |
| 5 | combined | J12_STACK_CRPS | J12_CANONICAL | brier | 265 | 53 | 0.241140 | 0.240787 | -0.000353 | -0.001248 | 0.000542 |
| 5 | combined | J12_STACK_CRPS | J12_CANONICAL | crps | 265 | 53 | 0.010732 | 0.010712 | -0.000020 | -0.000060 | 0.000021 |
| 5 | combined | J12_STACK_DEDUP | J12_STACK_CRPS | brier | 265 | 53 | 0.241140 | 0.241140 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_STACK_DEDUP | J12_STACK_CRPS | crps | 265 | 53 | 0.010732 | 0.010732 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | J12_STAT_HIST_CONTROL | V12_STAT | brier | 265 | 53 | 0.247718 | 0.244333 | -0.003385 | -0.025703 | 0.018934 |
| 5 | combined | J12_STAT_HIST_CONTROL | V12_STAT | crps | 265 | 53 | 0.010849 | 0.010777 | -0.000072 | -0.001134 | 0.000990 |

[All horizons and conditional redundancy](expert-information.csv) · [Duplicate checks](ensemble-exact-invariance.csv) · [Mature weight fits](ensemble-ledger.json).
