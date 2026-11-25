# V10 Reproduction And Baselines

All observations used to compute inputs and outcomes are from 2025–2026. The historical origin, decision convention, fold and endpoint come from the archived vintages. The original 17 November 2026 snapshot remains frozen. V10 refitted or reconstructed **1,612 V9 forecasts** using their actual IDs and saved chronological partitions, including the fitted V9 reliability gate. It independently refitted **184** forecasts belonging to the protected V8 weekly distribution and direction leaders. [Reproduction ledger](reproduction.json) · [Individual forecast errors](reproduced-origin-scores.csv).

## Exact V9 weekly training-history curve

| model | n | brier | crps |
| --- | --- | --- | --- |
| L_ROT_85 | 92 | 0.355902 | 0.015585 |
| L_ROT_126 | 92 | 0.213222 | 0.011160 |
| L_ROT_189 | 92 | 0.226963 | 0.011438 |
| L_ROT_252 | 92 | 0.210085 | 0.010848 |
| L_ROT_300 | 92 | 0.176506 | 0.010362 |
| L_ROT_MAX | 92 | 0.165232 | 0.010048 |

## Frozen probability and distribution references

| model | early Brier | later Brier | combined Brier | early CRPS | later CRPS | combined CRPS |
| --- | --- | --- | --- | --- | --- | --- |
| P_CLUSTER | 0.260773 | 0.190529 | 0.236386 | 0.012473 | 0.010463 | 0.011775 |
| BASE_NATIVE | 0.264194 | 0.186431 | 0.237197 | 0.011590 | 0.010645 | 0.011261 |
| J9_STATIC | 0.259548 | 0.221214 | 0.246239 | 0.010933 | 0.011211 | 0.011029 |
| J9_REL_SHRINK | 0.261291 | 0.225095 | 0.248725 | 0.010899 | 0.011230 | 0.011014 |
| NEUTRAL | 0.250000 | 0.250000 | 0.250000 | 0.010559 | 0.011996 | 0.011058 |
| BASE_ROTATION | 0.296554 | 0.165528 | 0.251066 | 0.013094 | 0.010118 | 0.012061 |
| HISTORY | 0.259447 | 0.258296 | 0.259048 | 0.010878 | 0.012210 | 0.011340 |
| P_HIST | 0.259447 | 0.258296 | 0.259048 | 0.010878 | 0.012210 | 0.011340 |
| BASE10 | 0.285113 | 0.256111 | 0.275044 | 0.012005 | 0.012152 | 0.012056 |
| BASE20 | 0.302169 | 0.242351 | 0.281402 | 0.012822 | 0.011591 | 0.012395 |
| BASE5 | 0.289767 | 0.272880 | 0.283905 | 0.012242 | 0.012696 | 0.012400 |
| REVERSION | 0.282031 | 0.303548 | 0.289501 | 0.012038 | 0.013659 | 0.012601 |
| V8_R_RESIDUAL | — | 0.159504 | — | — | 0.009852 | — |
| V8_W_STRUCT_EMBARGO | — | 0.163355 | — | — | 0.009453 | — |

V10's own historical law uses the last up to 252 mature outcomes on its chronology. The neutral reference uses the same absolute historic returns with symmetric equal masses and a fixed 0.5 probability. The reversion rule applies a fixed −0.25 coefficient to the recent endpoint return and forms a distribution from matured residuals and history. This neutral distribution is a V10 baseline in its own right. Keep its proper scores alongside the empirical historical frequency and the strongest V4–V9 systems.

## Largest replayed origin-level directional errors by system

| model | cohort | origin | p | brier | crps |
| --- | --- | --- | --- | --- | --- |
| P_CLUSTER | early | 2025-10-31 | 0.861511 | 0.742201 | 0.019782 |
| P_CLUSTER | early | 2025-11-26 | 0.861511 | 0.742201 | 0.020401 |
| P_CLUSTER | early | 2025-11-03 | 0.861511 | 0.742201 | 0.017232 |
| J9_REL_SHRINK | early | 2026-01-23 | 0.728527 | 0.530751 | 0.010662 |
| J9_REL_SHRINK | early | 2025-12-11 | 0.702801 | 0.493930 | 0.006668 |
| J9_STATIC | early | 2025-12-11 | 0.702801 | 0.493930 | 0.006668 |
| J9_STATIC | early | 2025-12-03 | 0.701143 | 0.491602 | 0.009951 |
| J9_REL_SHRINK | early | 2025-12-03 | 0.701143 | 0.491602 | 0.009951 |
| J9_STATIC | early | 2025-11-28 | 0.701143 | 0.491602 | 0.005434 |
| P_HIST | early | 2025-11-27 | 0.604317 | 0.365198 | 0.006194 |
| P_HIST | early | 2025-11-26 | 0.604317 | 0.365198 | 0.006965 |
| P_HIST | early | 2025-11-17 | 0.604317 | 0.365198 | 0.004378 |

The legacy exact-copy replay passed **125 required vectors** over the original defensive and sector-alias perturbation suites. [Defensive-copy replay](duplicate-replay/invariance-effects.csv) · [Sector aliases](duplicate-replay/sector-alias-effects.csv).
