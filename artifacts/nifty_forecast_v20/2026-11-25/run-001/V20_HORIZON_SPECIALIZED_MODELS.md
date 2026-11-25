# V20 Horizon Specialized Models

The shared representation and both separate heads train on the **same rows of fully matured 21-session history** before an issue. All estimated architectures use the same archived horizon law for shape. The candidate heads change location, and the fixed mixture preserves the original law and a specialized law with equal weight. A common-field separate-head control distinguishes different learned outputs from the effect of changing the features. A training-only rank-three state, a shared core with horizon-specific residuals, pre-specified sparse blocks and a strongly regularized rank-one multi-horizon head provide additional comparisons. Bank and IT relative returns enter an auxiliary reduced-rank fit on the same market dates.

| horizon | scope | model | n | active | disjoint | brier | crps | log loss | balanced accuracy | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | A_one_shared_head | 265 | 265 | 53 | 0.260646 | 0.011876 | 0.713437 | 0.490789 | 0.728302 | 0.041852 |
| 5 | combined | B_equal_fields_control | 265 | 265 | 53 | 0.261836 | 0.011798 | 0.715286 | 0.473695 | 0.747170 | 0.041905 |
| 5 | combined | B_separate_heads | 265 | 265 | 53 | 0.262007 | 0.011794 | 0.715432 | 0.452125 | 0.743396 | 0.041873 |
| 5 | combined | C_shared_state_two_heads | 265 | 265 | 53 | 0.253065 | 0.011328 | 0.697054 | 0.460874 | 0.758491 | 0.041919 |
| 5 | combined | D_core_with_horizon_residual | 265 | 265 | 53 | 0.259756 | 0.011825 | 0.710791 | 0.477275 | 0.735849 | 0.041881 |
| 5 | combined | E_sparse_horizon_inputs | 265 | 265 | 53 | 0.256167 | 0.011400 | 0.703718 | 0.466938 | 0.769811 | 0.041901 |
| 5 | combined | F_regularized_multihorizon | 265 | 265 | 53 | 0.256197 | 0.011641 | 0.703899 | 0.474590 | 0.747170 | 0.041863 |
| 5 | combined | G_fixed_specialized_mixture | 265 | 265 | 53 | 0.237729 | 0.010516 | 0.667909 | 0.574469 | 0.807547 | 0.043375 |
| 5 | combined | archived_joint_GJR | 265 | 265 | 53 | 0.250763 | 0.010922 | 0.694695 | 0.573516 | 0.773585 | 0.042067 |
| 5 | combined | archived_same_clock | 265 | 265 | 53 | 0.238113 | 0.010309 | 0.668373 | 0.575970 | 0.766038 | 0.041981 |
| 5 | combined | auxiliary_sector_shared_heads | 265 | 265 | 53 | 0.258921 | 0.011649 | 0.709520 | 0.463560 | 0.747170 | 0.041920 |
| 21 | combined | A_one_shared_head | 217 | 217 | 11 | 0.315740 | 0.031204 | 0.894628 | 0.444176 | 0.626728 | 0.079908 |
| 21 | combined | B_equal_fields_control | 217 | 217 | 11 | 0.322838 | 0.031517 | 0.915489 | 0.441846 | 0.626728 | 0.079898 |
| 21 | combined | B_separate_heads | 217 | 217 | 11 | 0.315709 | 0.030962 | 0.896263 | 0.518982 | 0.617512 | 0.080412 |
| 21 | combined | C_shared_state_two_heads | 217 | 217 | 11 | 0.300192 | 0.030085 | 0.862450 | 0.486368 | 0.622120 | 0.079844 |
| 21 | combined | D_core_with_horizon_residual | 217 | 217 | 11 | 0.320592 | 0.031366 | 0.906064 | 0.454098 | 0.612903 | 0.080036 |
| 21 | combined | E_sparse_horizon_inputs | 217 | 217 | 11 | 0.295546 | 0.029178 | 0.823077 | 0.500259 | 0.631336 | 0.080472 |
| 21 | combined | F_regularized_multihorizon | 217 | 217 | 11 | 0.317080 | 0.031224 | 0.901273 | 0.452373 | 0.608295 | 0.079908 |
| 21 | combined | G_fixed_specialized_mixture | 217 | 217 | 11 | 0.261585 | 0.026360 | 0.717663 | 0.500259 | 0.682028 | 0.083690 |
| 21 | combined | archived_joint_GJR | 217 | 217 | 11 | 0.251376 | 0.024694 | 0.695900 | 0.524072 | 0.709677 | 0.083754 |
| 21 | combined | archived_same_clock | 217 | 217 | 11 | 0.250000 | 0.025543 | 0.693147 | 0.500000 | 0.700461 | 0.081016 |
| 21 | combined | auxiliary_sector_shared_heads | 217 | 217 | 11 | 0.312506 | 0.031056 | 0.891078 | 0.456471 | 0.626728 | 0.079880 |

| horizon | model | metric | n | disjoint | parent loss | loss | gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | archived_same_clock | brier | 265 | 53 | 0.260646 | 0.238113 | 0.022533 |
| 5 | archived_same_clock | crps | 265 | 53 | 0.011876 | 0.010309 | 0.001567 |
| 5 | archived_joint_GJR | brier | 265 | 53 | 0.260646 | 0.250763 | 0.009883 |
| 5 | archived_joint_GJR | crps | 265 | 53 | 0.011876 | 0.010922 | 0.000954 |
| 5 | B_separate_heads | brier | 265 | 53 | 0.260646 | 0.262007 | -0.001361 |
| 5 | B_separate_heads | crps | 265 | 53 | 0.011876 | 0.011794 | 0.000082 |
| 5 | B_equal_fields_control | brier | 265 | 53 | 0.260646 | 0.261836 | -0.001190 |
| 5 | B_equal_fields_control | crps | 265 | 53 | 0.011876 | 0.011798 | 0.000077 |
| 5 | C_shared_state_two_heads | brier | 265 | 53 | 0.260646 | 0.253065 | 0.007581 |
| 5 | C_shared_state_two_heads | crps | 265 | 53 | 0.011876 | 0.011328 | 0.000548 |
| 5 | D_core_with_horizon_residual | brier | 265 | 53 | 0.260646 | 0.259756 | 0.000890 |
| 5 | D_core_with_horizon_residual | crps | 265 | 53 | 0.011876 | 0.011825 | 0.000051 |
| 5 | E_sparse_horizon_inputs | brier | 265 | 53 | 0.260646 | 0.256167 | 0.004479 |
| 5 | E_sparse_horizon_inputs | crps | 265 | 53 | 0.011876 | 0.011400 | 0.000475 |
| 5 | F_regularized_multihorizon | brier | 265 | 53 | 0.260646 | 0.256197 | 0.004449 |
| 5 | F_regularized_multihorizon | crps | 265 | 53 | 0.011876 | 0.011641 | 0.000234 |
| 5 | G_fixed_specialized_mixture | brier | 265 | 53 | 0.260646 | 0.237729 | 0.022918 |
| 5 | G_fixed_specialized_mixture | crps | 265 | 53 | 0.011876 | 0.010516 | 0.001359 |
| 5 | auxiliary_sector_shared_heads | brier | 265 | 53 | 0.260646 | 0.258921 | 0.001726 |
| 5 | auxiliary_sector_shared_heads | crps | 265 | 53 | 0.011876 | 0.011649 | 0.000226 |
| 21 | archived_same_clock | brier | 217 | 11 | 0.315740 | 0.250000 | 0.065740 |
| 21 | archived_same_clock | crps | 217 | 11 | 0.031204 | 0.025543 | 0.005662 |
| 21 | archived_joint_GJR | brier | 217 | 11 | 0.315740 | 0.251376 | 0.064364 |
| 21 | archived_joint_GJR | crps | 217 | 11 | 0.031204 | 0.024694 | 0.006510 |
| 21 | B_separate_heads | brier | 217 | 11 | 0.315740 | 0.315709 | 0.000031 |
| 21 | B_separate_heads | crps | 217 | 11 | 0.031204 | 0.030962 | 0.000243 |
| 21 | B_equal_fields_control | brier | 217 | 11 | 0.315740 | 0.322838 | -0.007098 |
| 21 | B_equal_fields_control | crps | 217 | 11 | 0.031204 | 0.031517 | -0.000312 |
| 21 | C_shared_state_two_heads | brier | 217 | 11 | 0.315740 | 0.300192 | 0.015548 |
| 21 | C_shared_state_two_heads | crps | 217 | 11 | 0.031204 | 0.030085 | 0.001120 |
| 21 | D_core_with_horizon_residual | brier | 217 | 11 | 0.315740 | 0.320592 | -0.004852 |
| 21 | D_core_with_horizon_residual | crps | 217 | 11 | 0.031204 | 0.031366 | -0.000161 |
| 21 | E_sparse_horizon_inputs | brier | 217 | 11 | 0.315740 | 0.295546 | 0.020194 |
| 21 | E_sparse_horizon_inputs | crps | 217 | 11 | 0.031204 | 0.029178 | 0.002026 |
| 21 | F_regularized_multihorizon | brier | 217 | 11 | 0.315740 | 0.317080 | -0.001340 |
| 21 | F_regularized_multihorizon | crps | 217 | 11 | 0.031204 | 0.031224 | -0.000019 |

The strongest model names in each metric table are separate experimental results. V17's five-session decomposition and the symmetric 21-session law are matching-clock controls. The matched GJR law retains its own path construction. Native 09:10 V14/V18 and V19 overlays are measured separately.

[architecture-config.json](architecture-config.json) · [architecture-cases.csv.gz](architecture-cases.csv.gz) · [architecture-laws.npz](architecture-laws.npz) · [architecture-training-receipts.csv](architecture-training-receipts.csv) · [complete-matched-comparisons.csv](complete-matched-comparisons.csv) · [matched-block-intervals.csv.gz](matched-block-intervals.csv.gz)
