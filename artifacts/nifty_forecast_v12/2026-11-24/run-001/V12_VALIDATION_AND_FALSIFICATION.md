# V12 Validation And Falsification

The run checks chronological fit boundaries, fully matured labels, the strictly purged inner phase fit, train-only canonicalization and regularization, origin/endpoint equality, earlier option source dates, and immutable prior artifacts. Verified counts include **1,923** fit artifacts, **964** exact portfolio-of-experts duplication tests and **24** feature-copy and future-data sentinels. The option audit rejects invalid solutions and retains full refusal reasons. Market returns, listed expiries and U.S. inputs carry their own event clocks.

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | Q12_SMOOTH | Q12_RAW | brier | 265 | 53 | 0.267476 | 0.268655 | 0.001178 | -0.000701 | 0.003057 |
| 5 | combined | Q12_SMOOTH | Q12_RAW | crps | 265 | 53 | 0.011136 | 0.011151 | 0.000015 | -0.000049 | 0.000078 |
| 5 | combined | Q12_TRUNCATED | Q12_RAW | brier | 265 | 53 | 0.268702 | 0.268655 | -0.000047 | -0.000464 | 0.000371 |
| 5 | combined | Q12_TRUNCATED | Q12_RAW | crps | 265 | 53 | 0.011164 | 0.011151 | -0.000013 | -0.000042 | 0.000016 |
| 5 | combined | V12_CONTROL_NOISE | V12_IV_SCALE | brier | 265 | 53 | 0.245774 | 0.244588 | -0.001186 | -0.004341 | 0.001969 |
| 5 | combined | V12_CONTROL_NOISE | V12_IV_SCALE | crps | 265 | 53 | 0.010798 | 0.010750 | -0.000048 | -0.000188 | 0.000092 |
| 5 | combined | V12_CONTROL_PERMUTED | V12_IV_SCALE | brier | 265 | 53 | 0.244900 | 0.244588 | -0.000312 | -0.003877 | 0.003252 |
| 5 | combined | V12_CONTROL_PERMUTED | V12_IV_SCALE | crps | 265 | 53 | 0.010804 | 0.010750 | -0.000054 | -0.000207 | 0.000099 |
| 5 | combined | V12_CONTROL_ROLL21 | V12_IV_SCALE | brier | 265 | 53 | 0.244724 | 0.244588 | -0.000136 | -0.003911 | 0.003639 |
| 5 | combined | V12_CONTROL_ROLL21 | V12_IV_SCALE | crps | 265 | 53 | 0.010818 | 0.010750 | -0.000068 | -0.000164 | 0.000029 |
| 5 | combined | V12_CONTROL_ROLL42 | V12_IV_SCALE | brier | 265 | 53 | 0.245317 | 0.244588 | -0.000729 | -0.004252 | 0.002794 |
| 5 | combined | V12_CONTROL_ROLL42 | V12_IV_SCALE | crps | 265 | 53 | 0.010822 | 0.010750 | -0.000071 | -0.000239 | 0.000096 |
| 5 | combined | V12_IV_BRACKET | V12_IV_SCALE | brier | 264 | 53 | 0.243172 | 0.243227 | 0.000055 | -0.000305 | 0.000414 |
| 5 | combined | V12_IV_BRACKET | V12_IV_SCALE | crps | 264 | 53 | 0.010754 | 0.010756 | 0.000002 | -0.000006 | 0.000009 |
| 5 | combined | V12_IV_LAG2 | V12_IV_SCALE | brier | 265 | 53 | 0.244244 | 0.244588 | 0.000344 | -0.002277 | 0.002965 |
| 5 | combined | V12_IV_LAG2 | V12_IV_SCALE | crps | 265 | 53 | 0.010766 | 0.010750 | -0.000015 | -0.000090 | 0.000059 |
| 5 | combined | V12_IV_LAG5 | V12_IV_SCALE | brier | 265 | 53 | 0.244188 | 0.244588 | 0.000400 | -0.001909 | 0.002709 |
| 5 | combined | V12_IV_LAG5 | V12_IV_SCALE | crps | 265 | 53 | 0.010773 | 0.010750 | -0.000023 | -0.000125 | 0.000079 |
| 5 | combined | V12_IV_LIQUID | V12_IV_SCALE | brier | 265 | 53 | 0.244596 | 0.244588 | -0.000008 | -0.000181 | 0.000164 |
| 5 | combined | V12_IV_LIQUID | V12_IV_SCALE | crps | 265 | 53 | 0.010750 | 0.010750 | 0.000001 | -0.000002 | 0.000003 |
| 5 | combined | V12_IV_LONGER | V12_IV_SCALE | brier | 265 | 53 | 0.244570 | 0.244588 | 0.000018 | -0.000955 | 0.000990 |
| 5 | combined | V12_IV_LONGER | V12_IV_SCALE | crps | 265 | 53 | 0.010757 | 0.010750 | -0.000006 | -0.000046 | 0.000033 |
| 5 | combined | V12_IV_RATE_HIGH | V12_IV_SCALE | brier | 265 | 53 | 0.244594 | 0.244588 | -0.000006 | -0.000064 | 0.000052 |
| 5 | combined | V12_IV_RATE_HIGH | V12_IV_SCALE | crps | 265 | 53 | 0.010750 | 0.010750 | -0.000000 | -0.000001 | 0.000000 |
| 5 | combined | V12_IV_RATE_ZERO | V12_IV_SCALE | brier | 265 | 53 | 0.244600 | 0.244588 | -0.000013 | -0.000067 | 0.000042 |
| 5 | combined | V12_IV_RATE_ZERO | V12_IV_SCALE | crps | 265 | 53 | 0.010750 | 0.010750 | 0.000001 | -0.000001 | 0.000002 |
| 5 | combined | V12_IV_SAME_CLOSE | V12_IV_SCALE | brier | 265 | 53 | 0.244953 | 0.244588 | -0.000365 | -0.002596 | 0.001866 |
| 5 | combined | V12_IV_SAME_CLOSE | V12_IV_SCALE | crps | 265 | 53 | 0.010766 | 0.010750 | -0.000016 | -0.000078 | 0.000045 |
| 5 | combined | V12_IV_SETTLEMENT | V12_IV_SCALE | brier | 265 | 53 | 0.244430 | 0.244588 | 0.000158 | -0.000166 | 0.000483 |
| 5 | combined | V12_IV_SETTLEMENT | V12_IV_SCALE | crps | 265 | 53 | 0.010748 | 0.010750 | 0.000002 | -0.000004 | 0.000008 |
| 5 | combined | V12_RV_SCALE | V12_STAT | brier | 265 | 53 | 0.244584 | 0.244333 | -0.000250 | -0.009078 | 0.008577 |
| 5 | combined | V12_RV_SCALE | V12_STAT | crps | 265 | 53 | 0.010794 | 0.010777 | -0.000016 | -0.000248 | 0.000215 |
| 5 | combined | V12_STRADDLE_SCALE | V12_RV_SCALE | brier | 265 | 53 | 0.243390 | 0.244584 | 0.001193 | -0.002046 | 0.004432 |
| 5 | combined | V12_STRADDLE_SCALE | V12_RV_SCALE | crps | 265 | 53 | 0.010739 | 0.010794 | 0.000054 | -0.000044 | 0.000153 |
| 21 | combined | Q12_SMOOTH | Q12_RAW | brier | 199 | 11 | 0.281855 | 0.283476 | 0.001621 | — | — |
| 21 | combined | Q12_SMOOTH | Q12_RAW | crps | 199 | 11 | 0.026747 | 0.026814 | 0.000067 | — | — |
| 21 | combined | Q12_TRUNCATED | Q12_RAW | brier | 193 | 11 | 0.283287 | 0.282835 | -0.000452 | — | — |
| 21 | combined | Q12_TRUNCATED | Q12_RAW | crps | 193 | 11 | 0.026953 | 0.026961 | 0.000007 | — | — |
| 21 | combined | V12_CONTROL_NOISE | V12_IV_SCALE | brier | 217 | 11 | 0.316064 | 0.317103 | 0.001039 | — | — |
| 21 | combined | V12_CONTROL_NOISE | V12_IV_SCALE | crps | 217 | 11 | 0.029132 | 0.029135 | 0.000003 | — | — |
| 21 | combined | V12_CONTROL_PERMUTED | V12_IV_SCALE | brier | 217 | 11 | 0.313043 | 0.317103 | 0.004060 | — | — |
| 21 | combined | V12_CONTROL_PERMUTED | V12_IV_SCALE | crps | 217 | 11 | 0.029075 | 0.029135 | 0.000060 | — | — |
| 21 | combined | V12_CONTROL_ROLL21 | V12_IV_SCALE | brier | 217 | 11 | 0.314365 | 0.317103 | 0.002738 | — | — |
| 21 | combined | V12_CONTROL_ROLL21 | V12_IV_SCALE | crps | 217 | 11 | 0.029081 | 0.029135 | 0.000055 | — | — |
| 21 | combined | V12_CONTROL_ROLL42 | V12_IV_SCALE | brier | 217 | 11 | 0.316754 | 0.317103 | 0.000349 | — | — |
| 21 | combined | V12_CONTROL_ROLL42 | V12_IV_SCALE | crps | 217 | 11 | 0.029174 | 0.029135 | -0.000039 | — | — |
| 21 | combined | V12_IV_BRACKET | V12_IV_SCALE | brier | 217 | 11 | 0.315677 | 0.317103 | 0.001426 | — | — |
| 21 | combined | V12_IV_BRACKET | V12_IV_SCALE | crps | 217 | 11 | 0.029090 | 0.029135 | 0.000045 | — | — |
| 21 | combined | V12_IV_LAG2 | V12_IV_SCALE | brier | 217 | 11 | 0.316953 | 0.317103 | 0.000150 | — | — |
| 21 | combined | V12_IV_LAG2 | V12_IV_SCALE | crps | 217 | 11 | 0.029145 | 0.029135 | -0.000009 | — | — |
| 21 | combined | V12_IV_LAG5 | V12_IV_SCALE | brier | 217 | 11 | 0.315162 | 0.317103 | 0.001941 | — | — |
| 21 | combined | V12_IV_LAG5 | V12_IV_SCALE | crps | 217 | 11 | 0.029089 | 0.029135 | 0.000046 | — | — |
| 21 | combined | V12_IV_LIQUID | V12_IV_SCALE | brier | 217 | 11 | 0.317430 | 0.317103 | -0.000326 | — | — |
| 21 | combined | V12_IV_LIQUID | V12_IV_SCALE | crps | 217 | 11 | 0.029160 | 0.029135 | -0.000025 | — | — |
| 21 | combined | V12_IV_LONGER | V12_IV_SCALE | brier | 205 | 11 | 0.321838 | 0.323523 | 0.001684 | — | — |
| 21 | combined | V12_IV_LONGER | V12_IV_SCALE | crps | 205 | 11 | 0.029608 | 0.029651 | 0.000042 | — | — |
| 21 | combined | V12_IV_RATE_HIGH | V12_IV_SCALE | brier | 217 | 11 | 0.317119 | 0.317103 | -0.000015 | — | — |
| 21 | combined | V12_IV_RATE_HIGH | V12_IV_SCALE | crps | 217 | 11 | 0.029136 | 0.029135 | -0.000000 | — | — |
| 21 | combined | V12_IV_RATE_ZERO | V12_IV_SCALE | brier | 217 | 11 | 0.317074 | 0.317103 | 0.000029 | — | — |
| 21 | combined | V12_IV_RATE_ZERO | V12_IV_SCALE | crps | 217 | 11 | 0.029135 | 0.029135 | 0.000001 | — | — |
| 21 | combined | V12_IV_SAME_CLOSE | V12_IV_SCALE | brier | 217 | 11 | 0.316319 | 0.317103 | 0.000784 | — | — |
| 21 | combined | V12_IV_SAME_CLOSE | V12_IV_SCALE | crps | 217 | 11 | 0.029138 | 0.029135 | -0.000003 | — | — |
| 21 | combined | V12_IV_SETTLEMENT | V12_IV_SCALE | brier | 217 | 11 | 0.317399 | 0.317103 | -0.000296 | — | — |
| 21 | combined | V12_IV_SETTLEMENT | V12_IV_SCALE | crps | 217 | 11 | 0.029131 | 0.029135 | 0.000004 | — | — |
| 21 | combined | V12_RV_SCALE | V12_STAT | brier | 217 | 11 | 0.315551 | 0.306090 | -0.009461 | — | — |
| 21 | combined | V12_RV_SCALE | V12_STAT | crps | 217 | 11 | 0.029099 | 0.028994 | -0.000105 | — | — |
| 21 | combined | V12_STRADDLE_SCALE | V12_RV_SCALE | brier | 217 | 11 | 0.316529 | 0.315551 | -0.000978 | — | — |
| 21 | combined | V12_STRADDLE_SCALE | V12_RV_SCALE | crps | 217 | 11 | 0.029133 | 0.029099 | -0.000035 | — | — |

The uncertainty families use 2,000 paired circular block draws at lengths 5, 10 and 15. Weekly endpoint Brier and CRPS share a joint maximum. Weekly path-volatility and absolute-movement error have a separate joint maximum. These sets condition on the V12 design and observed archive. They cannot correct the entire V1–V12 adaptive search or create independent monthly observations.

| score family | scope | dates | tested contrasts | block-10 critical |
| --- | --- | --- | --- | --- |
| endpoint Brier and CRPS | early | 173 | 3896 | 3.783308 |
| endpoint Brier and CRPS | later | 92 | 4710 | 3.656797 |
| endpoint Brier and CRPS | combined | 265 | 3896 | 3.871478 |
| path risk and movement | early | 173 | 435 | 3.527800 |
| path risk and movement | later | 92 | 432 | 3.394553 |
| path risk and movement | combined | 265 | 435 | 3.533887 |

Twelve representative block-permuted refit-and-reselection draws recompute phase winners, market recalibration and constrained ensemble weighting while keeping held-out realized outcomes fixed. These small diagnostic subsets do not confer a precise cumulative p value.

| family | horizon | cohort | metric | observed best gain | null median | null p95 | null exceedance fraction | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deterministic phases | 5 | early | brier_gain | 0.077149 | 0.035896 | 0.122485 | 0.333333 | 3 |
| deterministic phases | 5 | early | crps_gain | 0.002971 | 0.001211 | 0.003763 | 0.166667 | 3 |
| deterministic phases | 5 | later | brier_gain | 0.192223 | 0.092409 | 0.163504 | 0.000000 | 3 |
| deterministic phases | 5 | later | crps_gain | 0.007278 | 0.003125 | 0.008958 | 0.166667 | 3 |
| deterministic phases | 21 | early | brier_gain | 0.127381 | 0.162780 | 0.247198 | 0.750000 | 3 |
| deterministic phases | 21 | early | crps_gain | 0.009229 | 0.014921 | 0.022251 | 0.916667 | 3 |
| deterministic phases | 21 | later | brier_gain | 0.104572 | 0.017833 | 0.146539 | 0.166667 | 3 |
| deterministic phases | 21 | later | crps_gain | 0.003302 | 0.000461 | 0.003180 | 0.083333 | 3 |
| ensemble weighting | 5 | early | brier_gain | 0.001737 | 0.001143 | 0.003964 | 0.416667 | 2 |
| ensemble weighting | 5 | early | crps_gain | 0.000019 | 0.000031 | 0.000090 | 0.666667 | 2 |
| ensemble weighting | 5 | later | brier_gain | -0.000962 | -0.005306 | -0.003054 | 0.000000 | 3 |
| ensemble weighting | 5 | later | crps_gain | -0.000090 | -0.000260 | -0.000140 | 0.083333 | 3 |
| ensemble weighting | 21 | early | brier_gain | 0.007868 | 0.025712 | 0.051419 | 0.750000 | 2 |
| ensemble weighting | 21 | early | crps_gain | 0.000244 | 0.000953 | 0.001776 | 0.666667 | 2 |
| ensemble weighting | 21 | later | brier_gain | 0.003505 | 0.004709 | 0.009126 | 0.583333 | 3 |
| ensemble weighting | 21 | later | crps_gain | 0.000157 | 0.000086 | 0.000249 | 0.250000 | 3 |
| market recalibration | 5 | early | brier_gain | 0.003422 | 0.013085 | 0.030139 | 1.000000 | 3 |
| market recalibration | 5 | early | crps_gain | 0.000328 | 0.000543 | 0.001324 | 0.750000 | 3 |
| market recalibration | 5 | later | brier_gain | 0.014228 | 0.014014 | 0.019672 | 0.500000 | 3 |
| market recalibration | 5 | later | crps_gain | -0.000587 | -0.000547 | -0.000310 | 0.666667 | 3 |
| market recalibration | 21 | early | brier_gain | 0.042913 | 0.032372 | 0.099173 | 0.416667 | 3 |
| market recalibration | 21 | early | crps_gain | 0.001584 | 0.001025 | 0.002651 | 0.416667 | 3 |
| market recalibration | 21 | later | brier_gain | 0.042195 | 0.006602 | 0.010861 | 0.000000 | 3 |
| market recalibration | 21 | later | crps_gain | 0.002351 | 0.000636 | 0.000943 | 0.000000 | 3 |

| batch | reason | unestimated |
| --- | --- | --- |
| priced | No valid option/price observations in fold | 2 |

[Paired intervals](paired-uncertainty.json) · [Null selections](refit-null-selected.csv) · [Block sensitivity](market-training-perturbations.csv) · [Verification](verification.json).
