# V23 Simulation precision and numerical audit

Eight independent seeds and four scenario counts estimate numerical sampling error against exact finite weighted
probability laws. Twelve origins per horizon were spread across the original evaluation calendar, for 24 NIFTY
return dates and 24 joint path dates. Within each seed the models use common random uniforms and nested 256, 1,024,
4,096 and 16,384 prefixes. A high-side touch is sampled on the same joint path supports as the range. The volume of
simulations does not create additional realized market outcomes.

Exact scoring is used wherever the finite empirical law is already saved. Forecast probability noise at 256 draws
is several percentage points for many individual cases and falls as the count increases. The paired study measures
how much the finite draw can change the direction or size of an apparent gain. Higher-budget generative robustness
covers the main three synthetic or independent-day path baselines separately. Statistical and specification uncertainty
remain after we remove numerical resampling uncertainty.

| horizon | track | n | measure | trials | mae | p90 abs | rmse | bias |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | range | 256 | crps | 384 | 0.000334 | 0.000706 | 0.000449 | 0.000044 |
| 5 | range | 256 | high_touch_probability | 384 | 0.024597 | 0.047786 | 0.030018 | -0.003377 |
| 5 | range | 256 | probability | 384 | 0.016225 | 0.037760 | 0.022653 | 0.000397 |
| 5 | range | 1,024 | crps | 384 | 0.000163 | 0.000343 | 0.000226 | 0.000031 |
| 5 | range | 1,024 | high_touch_probability | 384 | 0.011728 | 0.023438 | 0.014895 | -0.001452 |
| 5 | range | 1,024 | probability | 384 | 0.008033 | 0.020085 | 0.011112 | 0.000183 |
| 5 | range | 4,096 | crps | 384 | 0.000083 | 0.000215 | 0.000122 | 0.000016 |
| 5 | range | 4,096 | high_touch_probability | 384 | 0.005971 | 0.012044 | 0.007585 | 0.000135 |
| 5 | range | 4,096 | probability | 384 | 0.003799 | 0.009391 | 0.005491 | 0.000638 |
| 5 | range | 16,384 | crps | 384 | 0.000037 | 0.000087 | 0.000052 | 0.000014 |
| 5 | range | 16,384 | high_touch_probability | 384 | 0.002853 | 0.005752 | 0.003523 | 0.000509 |
| 5 | range | 16,384 | probability | 384 | 0.001820 | 0.004655 | 0.002583 | 0.000182 |
| 5 | return | 256 | crps | 384 | 0.000623 | 0.001588 | 0.000902 | -0.000070 |
| 5 | return | 256 | probability | 384 | 0.026012 | 0.052672 | 0.031990 | 0.001624 |
| 5 | return | 1,024 | crps | 384 | 0.000291 | 0.000652 | 0.000405 | -0.000002 |
| 5 | return | 1,024 | probability | 384 | 0.012143 | 0.023319 | 0.015385 | 0.000724 |
| 5 | return | 4,096 | crps | 384 | 0.000144 | 0.000289 | 0.000211 | 0.000009 |
| 5 | return | 4,096 | probability | 384 | 0.005816 | 0.011289 | 0.007240 | 0.000599 |
| 5 | return | 16,384 | crps | 384 | 0.000064 | 0.000153 | 0.000088 | -0.000004 |
| 5 | return | 16,384 | probability | 384 | 0.002779 | 0.005577 | 0.003465 | -0.000270 |
| 21 | range | 256 | crps | 384 | 0.000667 | 0.001463 | 0.000985 | 0.000073 |
| 21 | range | 256 | high_touch_probability | 384 | 0.021471 | 0.046875 | 0.027296 | 0.001302 |
| 21 | range | 256 | probability | 384 | 0.016880 | 0.039974 | 0.021985 | 0.002984 |
| 21 | range | 1,024 | crps | 384 | 0.000345 | 0.000736 | 0.000536 | -0.000005 |
| 21 | range | 1,024 | high_touch_probability | 384 | 0.010641 | 0.021484 | 0.013396 | 0.001106 |
| 21 | range | 1,024 | probability | 384 | 0.007564 | 0.016602 | 0.010145 | 0.001237 |
| 21 | range | 4,096 | crps | 384 | 0.000170 | 0.000414 | 0.000270 | -0.000010 |
| 21 | range | 4,096 | high_touch_probability | 384 | 0.005310 | 0.010311 | 0.006640 | 0.000650 |
| 21 | range | 4,096 | probability | 384 | 0.004105 | 0.009798 | 0.005402 | 0.001689 |
| 21 | range | 16,384 | crps | 384 | 0.000084 | 0.000179 | 0.000119 | 0.000008 |
| 21 | range | 16,384 | high_touch_probability | 384 | 0.002872 | 0.005902 | 0.003605 | 0.000479 |
| 21 | range | 16,384 | probability | 384 | 0.001871 | 0.004281 | 0.002531 | 0.000126 |
| 21 | return | 256 | crps | 384 | 0.000861 | 0.001829 | 0.001221 | -0.000029 |
| 21 | return | 256 | probability | 384 | 0.024257 | 0.051194 | 0.030683 | 0.002279 |
| 21 | return | 1,024 | crps | 384 | 0.000421 | 0.000881 | 0.000641 | -0.000037 |
| 21 | return | 1,024 | probability | 384 | 0.011888 | 0.023262 | 0.014360 | 0.001077 |
| 21 | return | 4,096 | crps | 384 | 0.000199 | 0.000441 | 0.000307 | -0.000004 |
| 21 | return | 4,096 | probability | 384 | 0.005900 | 0.013624 | 0.007553 | 0.001652 |
| 21 | return | 16,384 | crps | 384 | 0.000106 | 0.000200 | 0.000154 | 0.000010 |
| 21 | return | 16,384 | probability | 384 | 0.002931 | 0.005879 | 0.003733 | 0.000793 |

| horizon | track | n | measure | replicates | exact gain | gain error mae | sign inversion rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | range | 256 | brier | 96 | -0.003472 | 0.005287 | 0.000000 |
| 5 | range | 256 | crps | 96 | -0.000169 | 0.000073 | 0.000000 |
| 5 | range | 1,024 | brier | 96 | -0.003472 | 0.003536 | 0.000000 |
| 5 | range | 1,024 | crps | 96 | -0.000169 | 0.000036 | 0.000000 |
| 5 | range | 4,096 | brier | 96 | -0.003472 | 0.001516 | 0.000000 |
| 5 | range | 4,096 | crps | 96 | -0.000169 | 0.000020 | 0.000000 |
| 5 | range | 16,384 | brier | 96 | -0.003472 | 0.000657 | 0.000000 |
| 5 | range | 16,384 | crps | 96 | -0.000169 | 0.000010 | 0.000000 |
| 21 | range | 256 | brier | 96 | -0.000579 | 0.003292 | 0.000000 |
| 21 | range | 256 | crps | 96 | -0.000712 | 0.000179 | 0.000000 |
| 21 | range | 1,024 | brier | 96 | -0.000579 | 0.001643 | 0.000000 |
| 21 | range | 1,024 | crps | 96 | -0.000712 | 0.000084 | 0.000000 |
| 21 | range | 4,096 | brier | 96 | -0.000579 | 0.000861 | 0.000000 |
| 21 | range | 4,096 | crps | 96 | -0.000712 | 0.000047 | 0.000000 |
| 21 | range | 16,384 | brier | 96 | -0.000579 | 0.000436 | 0.000000 |
| 21 | range | 16,384 | crps | 96 | -0.000712 | 0.000023 | 0.000000 |
| 5 | return | 256 | brier | 96 | -0.024675 | 0.009756 | 0.000000 |
| 5 | return | 256 | crps | 96 | -0.000374 | 0.000176 | 0.104167 |
| 5 | return | 1,024 | brier | 96 | -0.024675 | 0.006450 | 0.000000 |
| 5 | return | 1,024 | crps | 96 | -0.000374 | 0.000091 | 0.072917 |
| 5 | return | 4,096 | brier | 96 | -0.024675 | 0.002762 | 0.000000 |
| 5 | return | 4,096 | crps | 96 | -0.000374 | 0.000041 | 0.020833 |
| 5 | return | 16,384 | brier | 96 | -0.024675 | 0.001378 | 0.000000 |
| 5 | return | 16,384 | crps | 96 | -0.000374 | 0.000019 | 0.000000 |
| 21 | return | 256 | brier | 96 | -0.035428 | 0.012102 | 0.010417 |
| 21 | return | 256 | crps | 96 | -0.001732 | 0.000180 | 0.000000 |
| 21 | return | 1,024 | brier | 96 | -0.035428 | 0.006147 | 0.000000 |
| 21 | return | 1,024 | crps | 96 | -0.001732 | 0.000119 | 0.000000 |
| 21 | return | 4,096 | brier | 96 | -0.035428 | 0.003025 | 0.000000 |
| 21 | return | 4,096 | crps | 96 | -0.001732 | 0.000059 | 0.000000 |
| 21 | return | 16,384 | brier | 96 | -0.035428 | 0.001332 | 0.000000 |
| 21 | return | 16,384 | crps | 96 | -0.001732 | 0.000028 | 0.000000 |

[simulation-precision-cases.csv.gz](simulation-precision-cases.csv.gz) · [simulation-paired-gain-noise.csv](simulation-paired-gain-noise.csv) · [simulation-precision-design.json](simulation-precision-design.json) · [precision-joint-paths.npz](precision-joint-paths.npz) · [larger-simulation-path-summary.csv](larger-simulation-path-summary.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
