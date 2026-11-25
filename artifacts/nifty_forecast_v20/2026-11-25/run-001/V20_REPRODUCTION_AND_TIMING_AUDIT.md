# V20 Reproduction And Timing Audit

V20 verified 1,725 V19 files, 14 source modules and the predecessor-manifest chain. Replays covered 4,820 scored native predictions and mechanism cases. Their largest scalar deviation was 2.26e-16. The code reread the original V14 weighted atoms, refitted the V18 corporate and V19 participant residuals using their documented historical forecast errors, and compared atom arrays, weights, specific bias and lag controls, active cases and fallbacks.

The V14 registration defines the native issue at **09:10 IST on the cash session following the reference close**. The archived V19 decision field reads **08:55** because it records the snapshot of newly added inputs. In all 482 horizon-origin records, the modeled participant availability was **08:15 before 08:55**. V18 corporate publications, structured financial releases and price reactions cleared their own snapshot clock. The V14 options source day precedes the cash reference day. The same-clock archived V14 parent is appropriate for the native additions at 09:10. Rebuilt 08:55 V17 forecasts and prior-evening forecasts occupy their own tracks. The per-report publication time remains an assumption inherited from V19. The preceding-evening and lagged variants quantify sensitivity to the timing assumption.

| horizon | model | n | active | disjoint | brier | crps | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_event_overlay | 265 | 223 | 53 | 0.223481 | 0.010318 | 0.637789 |
| 5 | V14_exact | 265 | 265 | 53 | 0.228529 | 0.010457 | 0.648943 |
| 5 | V14_plus_positions | 265 | 223 | 53 | 0.234786 | 0.010547 | 0.662234 |
| 5 | V18_plus_positions | 265 | 223 | 53 | 0.232431 | 0.010467 | 0.658622 |
| 21 | V14_event_overlay | 217 | 159 | 11 | 0.259808 | 0.025409 | 0.713467 |
| 21 | V14_exact | 217 | 217 | 11 | 0.245042 | 0.024989 | 0.683095 |
| 21 | V14_plus_positions | 217 | 159 | 11 | 0.228199 | 0.024010 | 0.647076 |
| 21 | V18_plus_positions | 217 | 159 | 11 | 0.234879 | 0.024537 | 0.655320 |

| model | n | disjoint | brier | crps | log loss |
| --- | --- | --- | --- | --- | --- |
| V14_bias_only | 159 | 8 | 0.279342 | 0.026404 | 0.755367 |
| V14_exact | 159 | 8 | 0.241294 | 0.025046 | 0.675550 |
| V14_plus_positions | 159 | 8 | 0.218307 | 0.023710 | 0.626392 |
| V14_position_increment_without_bias | 159 | 8 | 0.227153 | 0.024182 | 0.647290 |
| positions_delay1 | 159 | 8 | 0.225051 | 0.023806 | 0.640253 |
| positions_delay5 | 159 | 8 | 0.258460 | 0.025077 | 0.712051 |

| horizon | metric | early | later | combined | active gain | remaining gain | removed start | removed end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | -0.006904 | -0.005040 | -0.006257 | -0.007436 | -0.013393 | 2026-02-16 | 2026-03-17 |
| 5 | crps | -0.000029 | -0.000204 | -0.000090 | -0.000107 | -0.000396 | 2026-02-16 | 2026-03-17 |
| 21 | brier | 0.026437 | -0.000954 | 0.016844 | 0.022988 | 0.007685 | 2026-07-02 | 2026-07-30 |
| 21 | crps | 0.001301 | 0.000382 | 0.000979 | 0.001336 | 0.000925 | 2026-09-30 | 2026-10-16 |

The placebo code reproduced 23 block rotations or permutations independently for each horizon and reselected among the native feature families in each run. The preserved monthly neutral law at 08:55 gives Brier 0.250000 and CRPS 0.025543. The distinct V15 GJR path law gives Brier 0.251376 and CRPS 0.024694. The 248-case GIFT opening result keeps its original forecast clock.

[timing-audit-receipt.json](timing-audit-receipt.json) · [native-source-clock-audit.csv](native-source-clock-audit.csv) · [native-audit-cases.csv.gz](native-audit-cases.csv.gz) · [native-audit-summary.csv](native-audit-summary.csv) · [native-audit-null-replay.csv](native-audit-null-replay.csv) · [native-audit-cohort-and-omission.csv](native-audit-cohort-and-omission.csv) · [predecessor-inventory.json](predecessor-inventory.json)
