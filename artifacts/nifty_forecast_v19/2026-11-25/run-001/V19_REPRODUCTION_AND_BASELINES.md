# V19 Reproduction And Baselines

The historical vintage opens on 2025-01-01 and freezes on 2026-11-17. V19 verified 4,226 V18 artifacts and 16 predecessor code hashes. The V18 opening GIFT replay covers 248 origins with Brier 0.100841 and accuracy 88.71%. The stored opening and native path files retain their original decision clocks.

V19 rebuilt 964 weighted V14 and V18 endpoint distributions and 3856 V18 delivery, participant, deal and combined predictions. Their maximum scalar replay error was 1.86e-10. The activity atom arrays reproduced the archival float32 values exactly. The V18 native corporate update was active on 223 weekly origins and 159 monthly origins.

| track | cutoff | horizon | model | metric | n | value |
| --- | --- | --- | --- | --- | --- | --- |
| opening | 08:55 | 1 | V16_GIFT | brier | 248 | 0.100841 |
| opening | 08:55 | 1 | V16_GIFT | accuracy | 248 | 0.887097 |
| protected_return | native_v14_guard | 5 | V14_sign_shrinkage | brier | 265 | 0.228529 |
| protected_return | native_v14_guard | 5 | V14_sign_shrinkage | crps | 265 | 0.010457 |
| protected_return | native_v14_guard | 21 | V14_domestic_GJR | brier | 217 | 0.245042 |
| protected_return | native_v14_guard | 21 | V14_domestic_GJR | crps | 217 | 0.024989 |
| same_clock_refit | preauction_0855 | 5 | clock_structural | crps | 265 | 0.010658 |
| same_clock_refit | preauction_0855 | 5 | component_plus_residual | crps | 265 | 0.010309 |
| same_clock_refit | previous_1700 | 5 | clock_structural | crps | 265 | 0.010721 |
| same_clock_refit | previous_1700 | 5 | component_plus_residual | crps | 265 | 0.010658 |
| same_clock_refit | preauction_0855 | 21 | clock_structural | crps | 217 | 0.028519 |
| same_clock_refit | preauction_0855 | 21 | component_plus_residual | crps | 217 | 0.028698 |
| same_clock_refit | previous_1700 | 21 | clock_structural | crps | 217 | 0.028321 |
| same_clock_refit | previous_1700 | 21 | component_plus_residual | crps | 217 | 0.028360 |
| protected_distribution | 08:55 | 21 | V15_GJR_restart | crps | 217 | 0.024694 |
| symmetric | all | 21 | equal_probability | brier | 217 | 0.250000 |
| protected_risk | 08:55 | 5 | offshore_plus_domestic | mae | 265 | 0.036469 |
| protected_risk | 08:55 | 21 | GJR | mae | 217 | 0.033179 |
| protected_risk | 08:55 | 5 | fixed_iv_rv | brier | 265 | 0.152707 |
| protected_risk | 08:55 | 21 | student_EGARCH | brier | 217 | 0.172872 |
| protected_risk | 08:55 | 5 | raw_iv | mae | 265 | 0.037814 |
| neutral_distribution | preauction_0855 | 21 | neutral | crps | 217 | 0.025543 |
| neutral_distribution | previous_1700 | 21 | neutral | crps | 217 | 0.025545 |
| protected_distribution | 08:55 | 21 | V15_GJR_restart | brier | 217 | 0.251376 |

The eight same-clock activity subsets recover each marginal addition across six orders. Positive contributions indicate reduced loss.

| horizon | cutoff | block | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | preauction_0855 | deals | -0.001524 | 2.00e-06 |
| 5 | preauction_0855 | delivery | 0.000040 | -0.000033 |
| 5 | preauction_0855 | participant | 0.007420 | 0.000338 |
| 5 | previous_1700 | deals | -0.001487 | -3.88e-06 |
| 5 | previous_1700 | delivery | -0.001604 | -0.000029 |
| 5 | previous_1700 | participant | 0.007803 | 0.000323 |
| 21 | preauction_0855 | deals | -0.006765 | -0.000405 |
| 21 | preauction_0855 | delivery | -0.003175 | -0.000472 |
| 21 | preauction_0855 | participant | 0.031193 | 0.000651 |
| 21 | previous_1700 | deals | -0.008852 | -0.000480 |
| 21 | previous_1700 | delivery | -0.004166 | -0.000666 |
| 21 | previous_1700 | participant | 0.025459 | 0.000368 |

[baseline-replay-receipt.json](baseline-replay-receipt.json) · [predecessor-protection.json](predecessor-protection.json) · [v18-activity-leaderboard.csv](v18-activity-leaderboard.csv) · [v18-activity-replay-and-subsets.csv.gz](v18-activity-replay-and-subsets.csv.gz) · [v18-activity-shapley-by-origin.csv.gz](v18-activity-shapley-by-origin.csv.gz) · [v18-native-replayed-laws.npz](v18-native-replayed-laws.npz) · [protected-native-joint-models.csv](protected-native-joint-models.csv)
