# V11 Reproduction And Baselines

V11 used the November 17 frozen vintage and archived query and maturity dates. It freshly reproduced **12,050** V10 model and transfer forecasts and **964** mixture forecasts using their exact expert laws and weights. The largest V10 fit-score discrepancy was **2.78e-17**. Included are official breadth, oldest/latest/spread, phase and GLS, block averaging, Student-t, sign and magnitude, transfer with randomized and displaced controls, neutral monthly, and dated futures/straddle. The prior-reference replay also verifies 1,612 V9 and 184 V8 forecasts and recreates 125 required duplicate invariance cases.

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| J10_STRUCTURAL_BLEND | 0.262428 | 0.186826 | 0.236181 | 0.011451 | 0.010275 | 0.011043 |
| P_CLUSTER | 0.260773 | 0.190529 | 0.236386 | 0.012473 | 0.010463 | 0.011775 |
| J10_HISTORY_SHRINK | 0.255692 | 0.217307 | 0.242366 | 0.010797 | 0.011071 | 0.010892 |
| J9_STATIC | 0.259548 | 0.221214 | 0.246239 | 0.010933 | 0.011211 | 0.011029 |
| J9_REL_SHRINK | 0.261291 | 0.225095 | 0.248725 | 0.010899 | 0.011230 | 0.011014 |
| NEUTRAL | 0.250000 | 0.250000 | 0.250000 | 0.010559 | 0.011996 | 0.011058 |
| P_STRUCTURE | 0.296317 | 0.165337 | 0.250845 | 0.013358 | 0.009608 | 0.012056 |
| P_ROT | 0.298696 | 0.164236 | 0.252015 | 0.013232 | 0.009995 | 0.012108 |
| P_HIST | 0.259447 | 0.258296 | 0.259048 | 0.010878 | 0.012210 | 0.011340 |
| V8_R_RESIDUAL | — | 0.159504 | — | — | 0.009852 | — |
| V8_W_STRUCT_EMBARGO | — | 0.163355 | — | — | 0.009453 | — |

The previously reported V9 weekly training-length Brier sequence is 0.355902, 0.213222, 0.226963, 0.210085, 0.176506 and 0.165232 at 85, 126, 189, 252, 300 and expanding, respectively. V10's compact later weekly comparison was 0.376831 recent, 0.243061 spread and 0.242128 earliest at 85. V8's 0.159504 Brier and 0.009453 CRPS values belong to their original models, dates and cohorts.

[V10 exact replay](v10-replay.json) · [V9 and V8 replay](replay/older/reproduction.json) · [Duplicate replay](replay/invariance/invariance-effects.csv).
