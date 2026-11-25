# NIFTY V18 — Reproduction and baselines

V18 retained the **November 17, 2026** historical freeze and the original five- and 21-session endpoints. The published opening-gap model reproduced on **248** mornings using the V16 implementation. V18 also replayed **482** protected V14 weighted endpoint laws, **1,928** V17 same-clock parent and component forecasts with exact stored atom agreement, and **217** archived GJR restart laws. Realized-volatility and expansion scores were recomputed from the frozen V16 case inputs. Relative rankings below refer to their own task and clock. The native V14 guard stays distinct from the reconstructed prior-session 17:00 and next-morning 08:55 forecasts. The V17 post-open parents retain the 09:25 and 10:20 clocks with their original eligible information and price reference.

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

The hash audit verified **3,010** V17 files and **17** source modules. It retains the predecessor protection record. The same-clock weekly component CRPS is **0.010309**, and the structural parent is **0.010658** on identical origins. The symmetric monthly benchmark is **0.250000 Brier**. Native model comparisons remain separately labeled.

[Exact opening scores](opening-exact-replay.csv) · [Protected weighted laws replay](protected-exact-law-replay.csv) · [Exact same-clock retraining](same-clock-refit.csv.gz) · [Protected risk cases](protected-risk-predictions.csv.gz) · [Predecessor protection](predecessor-protection.json)
