# NIFTY V8 · Historical Coverage And Sensitivity

Run `2026-11-24/run-001`. Retrospective research.

We reconstructed earlier V3-exposed origins with low-dimensional price/rotation designs, a fixed 85-date mature training minimum, 40-date purged fitting minimum, and 28-date residual validation. The simpler models use Ridge150. The rolling version caps both eligible fitting histories at 126. A full native rotation configuration and historical return law share the same earlier dates. The endpoint embargo conditions were unchanged. We retained the same earlier design at both horizons regardless of results. This adds 173 weekly and 141 monthly research origins, separated from the later 92/76 origin cohorts. These earlier dates are exposed research history.

| cohort | horizon | origins | first | last | last_endpoint |
| --- | --- | --- | --- | --- | --- |
| diagnostic | 10 | 76 | 2026-06-30 | 2026-10-15 | 2026-10-30 |
| diagnostic | 15 | 76 | 2026-06-30 | 2026-10-15 | 2026-11-06 |
| early | 5 | 173 | 2025-10-14 | 2026-06-29 | 2026-07-06 |
| early | 21 | 141 | 2025-12-01 | 2026-06-29 | 2026-07-28 |
| primary | 5 | 92 | 2026-06-30 | 2026-11-08 | 2026-11-16 |
| primary | 21 | 76 | 2026-06-30 | 2026-10-15 | 2026-11-16 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E_HIST | 173 | 35 | 0.445087 | 0.482119 | 0.259447 | 0.712156 | 0.010878 | 0.014956 | 0.019931 | 0.005409 | 0.473988 | 0.710983 | 0.036450 |
| E_SMALL | 173 | 35 | 0.445087 | 0.464912 | 0.325783 | 0.876855 | 0.013289 | 0.017803 | 0.024394 | 0.006583 | 0.439306 | 0.693642 | 0.042323 |
| E_ROT | 173 | 35 | 0.456647 | 0.477733 | 0.324257 | 0.874530 | 0.013195 | 0.017647 | 0.024302 | 0.006556 | 0.450867 | 0.699422 | 0.042514 |
| E_SMALL_126 | 173 | 35 | 0.491329 | 0.502429 | 0.298942 | 0.811265 | 0.013351 | 0.018004 | 0.025226 | 0.006512 | 0.410405 | 0.693642 | 0.042721 |
| E_ROT_126 | 173 | 35 | 0.479769 | 0.489609 | 0.299837 | 0.813185 | 0.013305 | 0.018040 | 0.025228 | 0.006513 | 0.398844 | 0.705202 | 0.043377 |
| E_FULL_ROT | 173 | 35 | 0.508671 | 0.522807 | 0.299536 | 0.819912 | 0.013243 | 0.018254 | 0.024750 | 0.006476 | 0.410405 | 0.751445 | 0.047413 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E_HIST | 141 | 7 | 0.453901 | 0.500000 | 0.324122 | 0.860553 | 0.027004 | 0.034685 | 0.046848 | 0.013288 | 0.290780 | 0.567376 | 0.061732 |
| E_SMALL | 141 | 7 | 0.496454 | 0.512581 | 0.370052 | 1.066219 | 0.031297 | 0.040018 | 0.052737 | 0.015871 | 0.319149 | 0.517730 | 0.073979 |
| E_ROT | 141 | 7 | 0.482270 | 0.496956 | 0.371184 | 1.070299 | 0.031341 | 0.040159 | 0.052792 | 0.015895 | 0.333333 | 0.510638 | 0.074692 |
| E_SMALL_126 | 141 | 7 | 0.631206 | 0.638596 | 0.299491 | 0.879647 | 0.032311 | 0.042611 | 0.053631 | 0.015876 | 0.375887 | 0.539007 | 0.085468 |
| E_ROT_126 | 141 | 7 | 0.631206 | 0.638596 | 0.303368 | 0.889414 | 0.032307 | 0.042639 | 0.053586 | 0.015870 | 0.368794 | 0.531915 | 0.086114 |
| E_FULL_ROT | 141 | 7 | 0.503546 | 0.524351 | 0.348509 | 0.998372 | 0.032235 | 0.042982 | 0.055849 | 0.016232 | 0.340426 | 0.517730 | 0.081200 |


The earlier weekly historical law beats the full native rotation system by **.040089 Brier** and **.002365 CRPS**. The compact rotation addition barely improves its own expanding-window earlier control. At 21 sessions, the compact 126-date models improve earlier Brier over the historical law while delivering worse CRPS. The prominence of rotation in the later cohort therefore does not carry across these earlier dates. Training horizon and regime differ. This is evidence against robustness across design/cohort, with no universal explanation identified.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K_HIST | 76 | 8 | 0.657895 | 0.500000 | 0.250716 | 0.694695 | 0.011598 | 0.016481 | 0.019898 | 0.005652 | 0.447368 | 0.855263 | 0.058981 |
| K_BASE | 76 | 8 | 0.605263 | 0.635385 | 0.220947 | 0.630628 | 0.010612 | 0.015395 | 0.018076 | 0.005185 | 0.434211 | 0.802632 | 0.049570 |
| K_ROT | 76 | 8 | 0.605263 | 0.644615 | 0.220587 | 0.630611 | 0.010591 | 0.015314 | 0.018033 | 0.005190 | 0.434211 | 0.802632 | 0.049839 |
| K_STRUCTURE | 76 | 8 | 0.605263 | 0.653846 | 0.218071 | 0.624409 | 0.010475 | 0.014668 | 0.017851 | 0.005162 | 0.473684 | 0.802632 | 0.052059 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K_HIST | 76 | 6 | 0.539474 | 0.568027 | 0.256856 | 0.706880 | 0.017622 | 0.024709 | 0.030263 | 0.008395 | 0.368421 | 0.802632 | 0.071611 |
| K_BASE | 76 | 6 | 0.565789 | 0.621693 | 0.240860 | 0.670946 | 0.019384 | 0.026662 | 0.030840 | 0.009401 | 0.263158 | 0.671053 | 0.062128 |
| K_ROT | 76 | 6 | 0.565789 | 0.621693 | 0.240605 | 0.670616 | 0.019323 | 0.026650 | 0.030778 | 0.009347 | 0.276316 | 0.657895 | 0.062499 |
| K_STRUCTURE | 76 | 6 | 0.565789 | 0.613379 | 0.231235 | 0.650181 | 0.018849 | 0.026099 | 0.030277 | 0.009101 | 0.302632 | 0.736842 | 0.063617 |


On the same 76 origins, the 10-session structure change improves CRPS versus the 10-session historical law, .010475 versus .011598. At 15 sessions it scores .018849, worse than the horizon-local historical .017622. These are dependence-limited diagnostic cohorts rather than a horizon selection rule. Important shorter-window fail cases for the weekly lead and extra-cutoff fits are preserved in `stress-results.csv` and `fit-attempts.csv`.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
