# V21 Reproduction And Prior Transfer Forensics

The V20 manifest binds **151 files and 16 code files**. V21 re-scored **2,892 complete weighted laws** directly from their archived atoms and weights. The native forecasts still use the next-session **09:10 IST** issue clock, with V20’s **08:55** input snapshot. The separate matched pre-auction controls retain the V17 weekly session decomposition and the monthly neutral and GJR laws. The exchange publication allowance used in V20 remains an assumption where historical first timestamps are missing.

| horizon | cutoff | model | n | active | brier | crps | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | exact_v14 | 265 | 265 | 0.228529 | 0.010457 | 0.648943 |
| 5 | native_0910 | omit_latest_21_training_origins | 265 | 202 | 0.221693 | 0.010274 | 0.634612 |
| 5 | native_0910 | price_reaction | 265 | 223 | 0.223384 | 0.010258 | 0.638699 |
| 5 | native_0910 | v18_corporate_native | 265 | 265 | 0.223481 | 0.010318 | 0.637789 |
| 5 | preauction_0855 | archived_joint_GJR | 265 | 265 | 0.250763 | 0.010922 | 0.694695 |
| 5 | preauction_0855 | archived_same_clock | 265 | 265 | 0.238113 | 0.010309 | 0.668373 |
| 21 | native_0910 | eight_calendar_day_embargo | 217 | 154 | 0.228088 | 0.024003 | 0.646729 |
| 21 | native_0910 | exact_v14 | 217 | 217 | 0.245042 | 0.024989 | 0.683095 |
| 21 | native_0910 | smooth5 | 217 | 159 | 0.228602 | 0.023786 | 0.648584 |
| 21 | native_0910 | v19_position_native | 217 | 159 | 0.228199 | 0.024010 | 0.647076 |
| 21 | preauction_0855 | archived_joint_GJR | 217 | 217 | 0.251376 | 0.024694 | 0.695900 |
| 21 | preauction_0855 | archived_same_clock | 217 | 217 | 0.250000 | 0.025543 | 0.693147 |

V10 transfer was a shared-coefficient and auxiliary-task experiment. The shifted and randomized tasks approached or beat some genuine transfers, and the monthly sector arm had weak direct NIFTY scores. V19 tested stock-relative and sector-relative delivery signals. Delivery moved the five-session stock rank correlation from about **−0.00318 to +0.00300** when added to price and volume, with very small error changes. Its 21-session sector MAE was **0.030875** compared with **0.030702** for price and turnover. V18’s corporate pooling used firm-event responses, where a price-based control stayed competitive. These failure modes concern the estimated signal before propagation to the index. V20’s dependence-aware temporal pieces also lost to the neutral endpoint distribution, a separate failure at the final index forecast. The post-week GJR component test showed a small cohort-dependent positioning gain with a zero-inclusive interval.

| horizon | cohort | model | n | brier | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | early | X_FACTORS | 173 | 0.258998 | 0.010575 |
| 5 | early | X_ONLY | 173 | 0.260823 | 0.010730 |
| 5 | early | X_POOL | 173 | 0.260818 | 0.010668 |
| 5 | early | X_RANDOM | 173 | 0.258603 | 0.010569 |
| 5 | early | X_SECTORS | 173 | 0.263780 | 0.010690 |
| 5 | early | X_SHIFT | 173 | 0.257102 | 0.010590 |
| 5 | later | X_FACTORS | 92 | 0.292772 | 0.013552 |
| 5 | later | X_ONLY | 92 | 0.298846 | 0.013760 |
| 5 | later | X_POOL | 92 | 0.292584 | 0.013743 |
| 5 | later | X_RANDOM | 92 | 0.294780 | 0.013668 |
| 5 | later | X_SECTORS | 92 | 0.293476 | 0.013668 |
| 5 | later | X_SHIFT | 92 | 0.295531 | 0.013767 |
| 21 | early | X_FACTORS | 141 | 0.298015 | 0.028999 |
| 21 | early | X_ONLY | 141 | 0.299461 | 0.030590 |
| 21 | early | X_POOL | 141 | 0.302234 | 0.029242 |
| 21 | early | X_RANDOM | 141 | 0.299506 | 0.029153 |
| 21 | early | X_SECTORS | 141 | 0.299016 | 0.028812 |
| 21 | early | X_SHIFT | 141 | 0.290979 | 0.028744 |
| 21 | later | X_FACTORS | 76 | 0.471285 | 0.035963 |
| 21 | later | X_ONLY | 76 | 0.482538 | 0.036466 |
| 21 | later | X_POOL | 76 | 0.493695 | 0.036542 |
| 21 | later | X_RANDOM | 76 | 0.486258 | 0.036259 |
| 21 | later | X_SECTORS | 76 | 0.484257 | 0.036206 |
| 21 | later | X_SHIFT | 76 | 0.501959 | 0.037141 |

| horizon | model | n | dates | issuers | mae | accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | matched_non_event_model | 2,915 | 367 | 88 | 0.011930 | 0.510120 |
| 1 | ordinary_pooled | 2,915 | 367 | 88 | 0.012112 | 0.518696 |
| 1 | price_only | 2,915 | 367 | 88 | 0.011992 | 0.518353 |
| 1 | randomized_category | 2,915 | 367 | 88 | 0.012059 | 0.510120 |
| 1 | sector_issuer_partial_pool | 2,915 | 367 | 88 | 0.012170 | 0.511492 |
| 5 | matched_non_event_model | 2,873 | 359 | 88 | 0.026481 | 0.516185 |
| 5 | ordinary_pooled | 2,873 | 359 | 88 | 0.026812 | 0.509224 |
| 5 | price_only | 2,873 | 359 | 88 | 0.026588 | 0.505743 |
| 5 | randomized_category | 2,873 | 359 | 88 | 0.026759 | 0.508876 |
| 5 | sector_issuer_partial_pool | 2,873 | 359 | 88 | 0.026966 | 0.495301 |

| target | model | dates | case units | rank corr | mae | rmse |
| --- | --- | --- | --- | --- | --- | --- |
| target21 | delivery_only | 349 | 81,462 | -0.006211 | 0.065508 | 0.092437 |
| target21 | price_volume | 349 | 81,462 | -0.042823 | 0.065872 | 0.092902 |
| target21 | price_volume_delivery | 349 | 81,462 | -0.029442 | 0.065835 | 0.092893 |
| target5 | delivery_only | 365 | 85,427 | 0.014511 | 0.029885 | 0.043874 |
| target5 | price_volume | 365 | 85,427 | -0.003185 | 0.029924 | 0.043912 |
| target5 | price_volume_delivery | 365 | 85,427 | 0.002997 | 0.029922 | 0.043915 |

| model | cohort | n | brier | crps |
| --- | --- | --- | --- | --- |
| direct_specialized | early | 141 | 0.343505 | 0.033553 |
| direct_specialized | later | 76 | 0.264139 | 0.026154 |
| horizon_specific_components | early | 141 | 0.380708 | 0.038189 |
| horizon_specific_components | later | 76 | 0.253973 | 0.025416 |
| independent_components_control | early | 141 | 0.349806 | 0.037827 |
| independent_components_control | later | 76 | 0.219737 | 0.023979 |
| same_clock_neutral | early | 141 | 0.250000 | 0.024873 |
| same_clock_neutral | later | 76 | 0.250000 | 0.026786 |

[predecessor-receipt.json](predecessor-receipt.json) · [protected-return-cases.csv.gz](protected-return-cases.csv.gz) · [protected-return-laws.npz](protected-return-laws.npz) · [v7-auxiliary-reference.csv](v7-auxiliary-reference.csv) · [v10-transfer-replay.csv](v10-transfer-replay.csv) · [v18-event-transfer-replay.csv](v18-event-transfer-replay.csv) · [v19-stock-transfer-replay.csv](v19-stock-transfer-replay.csv) · [v19-sector-transfer-replay.csv](v19-sector-transfer-replay.csv) · [v20-temporal-replay.csv](v20-temporal-replay.csv) · [v20-late-component-reference.csv](v20-late-component-reference.csv)
