# NIFTY V18 — Fundamental risk intelligence

V18 separates annualized point-volatility forecasts, transitions, and joint paths. Expansion is the inherited realized volatility event threshold at **1.25×** the trajectory's trailing volatility. The raw same-clock ATM IV point and a distinct empirical law centered on ATM in log units both enter the comparisons. India VIX and historical realized volatility are state controls. At their documented 08:55 clock, archived GJR, Student-t EGARCH, fixed IV/RV, V14 IV/GJR, and V16 offshore/domestic forecasts preserve their original predictions. Post-open event additions are assessed on matched V17 cash-risk cases at **09:25 and 10:20**, with the other archived V17 risk arms retained and matched separately. The empirical risk-law event probability is read from the same forecast atoms. A separate event-probability correction tests transition information under the same time guards.

Corporate intensity, earnings dispersion, financial news and already announced event exposure were used to estimate scale corrections. For joint simulation, each origin's previously saved log OHLC scenario is transformed by a positive factor, preserving high/open/close/low order. GIFT-first and the constant-IV and GJR path roots keep their correct historical timestamps. Day-one, cumulative first passage and later probability conditional on surviving day one are kept distinct. Common cases align the same **date, barrier and side** before averaging within date. The native V14 laws and published path references remain available without a clock reinterpretation.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 09:25 | postopen_event_risk | V17_postopen_cash_risk | brier | 221 | 45 | 0.243880 | 0.229647 | -0.014233 | -0.022290 | -0.006176 |
| 5 | 09:25 | postopen_event_risk | V17_postopen_cash_risk | abs_error | 221 | 45 | 0.038717 | 0.040408 | 0.001691 | -0.003354 | 0.006735 |
| 5 | 09:25 | postopen_event_risk | V17_postopen_cash_risk | qlike | 221 | 45 | 0.301964 | 0.272128 | -0.029836 | -0.104996 | 0.045323 |
| 5 | 10:20 | postopen_event_risk | V17_postopen_cash_risk | brier | 221 | 45 | 0.242901 | 0.228575 | -0.014326 | -0.022527 | -0.006124 |
| 5 | 10:20 | postopen_event_risk | V17_postopen_cash_risk | abs_error | 221 | 45 | 0.038681 | 0.040524 | 0.001842 | -0.003339 | 0.007023 |
| 5 | 10:20 | postopen_event_risk | V17_postopen_cash_risk | qlike | 221 | 45 | 0.301224 | 0.272737 | -0.028487 | -0.104028 | 0.047054 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | brier | 265 | 53 | 0.158265 | 0.156619 | -0.001646 | -0.035240 | 0.031949 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | crps | 265 | 53 | 0.027240 | 0.026149 | -0.001090 | -0.004056 | 0.001875 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.038369 | 0.037785 | -0.000584 | -0.005630 | 0.004462 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.328413 | 0.278256 | -0.050156 | -0.137622 | 0.037310 |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | brier | 265 | 53 | 0.154673 | 0.156619 | 0.001946 | -0.035220 | 0.039113 |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026395 | 0.026149 | -0.000246 | -0.003376 | 0.002884 |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.036944 | 0.037785 | 0.000841 | -0.004492 | 0.006174 |
| 5 | preauction_0855 | fundamental_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.319097 | 0.278256 | -0.040841 | -0.132673 | 0.050991 |
| 5 | preauction_0855 | material_events_risk | risk_calibrated_iv | brier | 265 | 53 | 0.160752 | 0.156619 | -0.004133 | -0.039548 | 0.031281 |
| 5 | preauction_0855 | material_events_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026959 | 0.026149 | -0.000809 | -0.003699 | 0.002080 |
| 5 | preauction_0855 | material_events_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037713 | 0.037785 | 0.000072 | -0.004645 | 0.004789 |
| 5 | preauction_0855 | material_events_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.328318 | 0.278256 | -0.050062 | -0.147437 | 0.047313 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | brier | 265 | 53 | 0.154819 | 0.156619 | 0.001800 | -0.030131 | 0.033732 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026249 | 0.026149 | -0.000100 | -0.003021 | 0.002821 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037189 | 0.037785 | 0.000596 | -0.004754 | 0.005946 |
| 5 | preauction_0855 | non_price_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.307498 | 0.278256 | -0.029241 | -0.110742 | 0.052259 |
| 5 | preauction_0855 | scheduled_risk | protected_raw_iv | brier | 265 | 53 | 0.158265 | 0.155657 | -0.002608 | -0.031309 | 0.026092 |
| 5 | preauction_0855 | scheduled_risk | protected_raw_iv | abs_error | 265 | 53 | 0.038369 | 0.037814 | -0.000555 | -0.006443 | 0.005334 |
| 5 | preauction_0855 | scheduled_risk | protected_raw_iv | qlike | 265 | 53 | 0.328413 | 0.276187 | -0.052226 | -0.148058 | 0.043607 |
| 5 | preauction_0855 | fundamental_risk | protected_raw_iv | brier | 265 | 53 | 0.154673 | 0.155657 | 0.000984 | -0.030632 | 0.032599 |
| 5 | preauction_0855 | fundamental_risk | protected_raw_iv | abs_error | 265 | 53 | 0.036944 | 0.037814 | 0.000870 | -0.005211 | 0.006951 |
| 5 | preauction_0855 | fundamental_risk | protected_raw_iv | qlike | 265 | 53 | 0.319097 | 0.276187 | -0.042910 | -0.142616 | 0.056796 |
| 5 | preauction_0855 | non_price_risk | protected_raw_iv | brier | 265 | 53 | 0.154819 | 0.155657 | 0.000838 | -0.026618 | 0.028294 |
| 5 | preauction_0855 | non_price_risk | protected_raw_iv | abs_error | 265 | 53 | 0.037189 | 0.037814 | 0.000625 | -0.005457 | 0.006707 |
| 5 | preauction_0855 | non_price_risk | protected_raw_iv | qlike | 265 | 53 | 0.307498 | 0.276187 | -0.031311 | -0.121182 | 0.058561 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | brier | 265 | 53 | 0.158752 | 0.157572 | -0.001180 | -0.030936 | 0.028576 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | crps | 265 | 53 | 0.027259 | 0.026176 | -0.001082 | -0.004011 | 0.001847 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.038379 | 0.037858 | -0.000521 | -0.004646 | 0.003605 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.329932 | 0.278972 | -0.050959 | -0.124865 | 0.022946 |
| 5 | previous_1700 | fundamental_risk | risk_calibrated_iv | brier | 265 | 53 | 0.156939 | 0.157572 | 0.000633 | -0.031322 | 0.032589 |
| 5 | previous_1700 | fundamental_risk | risk_calibrated_iv | crps | 265 | 53 | 0.026707 | 0.026176 | -0.000530 | -0.003672 | 0.002612 |
| 5 | previous_1700 | fundamental_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037485 | 0.037858 | 0.000374 | -0.004023 | 0.004771 |
| 5 | previous_1700 | fundamental_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.329356 | 0.278972 | -0.050384 | -0.134106 | 0.033338 |
| 5 | previous_1700 | material_events_risk | risk_calibrated_iv | brier | 265 | 53 | 0.160414 | 0.157572 | -0.002842 | -0.034213 | 0.028529 |
| 5 | previous_1700 | material_events_risk | risk_calibrated_iv | crps | 265 | 53 | 0.027148 | 0.026176 | -0.000972 | -0.003821 | 0.001877 |
| 5 | previous_1700 | material_events_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.037774 | 0.037858 | 0.000084 | -0.003838 | 0.004006 |
| 5 | previous_1700 | material_events_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.332955 | 0.278972 | -0.053983 | -0.135605 | 0.027639 |
| 5 | previous_1700 | non_price_risk | risk_calibrated_iv | brier | 265 | 53 | 0.156077 | 0.157572 | 0.001495 | -0.025237 | 0.028227 |

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | endpoint_crps | 265 | 53 | 0.010718 | 0.010672 | -0.000045 | -0.000232 | 0.000141 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | range_crps | 265 | 53 | 0.006303 | 0.005768 | -0.000535 | -0.001291 | 0.000222 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | vol_mae | 265 | 53 | 0.036952 | 0.036801 | -0.000152 | -0.004307 | 0.004004 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | touch_brier | 265 | 53 | 0.147399 | 0.144562 | -0.002837 | -0.006530 | 0.000857 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | endpoint_crps | 265 | 53 | 0.010718 | 0.010922 | 0.000204 | -3.44e-06 | 0.000411 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | range_crps | 265 | 53 | 0.006303 | 0.006493 | 0.000190 | -0.000542 | 0.000923 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | vol_mae | 265 | 53 | 0.036952 | 0.040097 | 0.003145 | -0.001899 | 0.008188 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | touch_brier | 265 | 53 | 0.147399 | 0.148396 | 0.000998 | -0.001967 | 0.003962 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | endpoint_crps | 265 | 53 | 0.010978 | 0.010922 | -0.000056 | -0.000192 | 0.000080 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | range_crps | 265 | 53 | 0.006996 | 0.006493 | -0.000503 | -0.001121 | 0.000116 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | vol_mae | 265 | 53 | 0.040729 | 0.040097 | -0.000632 | -0.004127 | 0.002863 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | touch_brier | 265 | 53 | 0.151531 | 0.148396 | -0.003135 | -0.006885 | 0.000616 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | endpoint_crps | 265 | 53 | 0.010978 | 0.010672 | -0.000306 | -0.000696 | 0.000085 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | range_crps | 265 | 53 | 0.006996 | 0.005768 | -0.001228 | -0.002678 | 0.000223 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | vol_mae | 265 | 53 | 0.040729 | 0.036801 | -0.003928 | -0.010571 | 0.002715 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | touch_brier | 265 | 53 | 0.151531 | 0.144562 | -0.006969 | -0.015411 | 0.001473 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | endpoint_crps | 265 | 53 | 0.010728 | 0.010672 | -0.000056 | -0.000241 | 0.000129 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | range_crps | 265 | 53 | 0.006349 | 0.005768 | -0.000581 | -0.001323 | 0.000162 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | vol_mae | 265 | 53 | 0.037309 | 0.036801 | -0.000509 | -0.004508 | 0.003491 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | touch_brier | 265 | 53 | 0.147557 | 0.144562 | -0.002995 | -0.006463 | 0.000472 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | endpoint_crps | 265 | 53 | 0.010728 | 0.010922 | 0.000193 | -2.69e-06 | 0.000390 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | range_crps | 265 | 53 | 0.006349 | 0.006493 | 0.000144 | -0.000576 | 0.000865 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | vol_mae | 265 | 53 | 0.037309 | 0.040097 | 0.002788 | -0.002373 | 0.007948 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | touch_brier | 265 | 53 | 0.147557 | 0.148396 | 0.000839 | -0.001963 | 0.003641 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_GJR | endpoint_crps | 265 | 53 | 0.010975 | 0.010922 | -0.000053 | -0.000184 | 0.000078 |

| horizon | cutoff | candidate | control | metric | n | side barrier cases | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | brier_by_1 | 265 | 2,650 | 0.083666 | 0.082219 | -0.001447 | -0.002494 | -0.000399 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | touch_brier | 265 | 2,650 | 0.147399 | 0.144562 | -0.002837 | -0.005668 | -6.10e-06 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_IV | conditional_brier | 265 | 2,305 | 0.144801 | 0.143017 | -0.001784 | -0.004032 | 0.000464 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | brier_by_1 | 265 | 2,650 | 0.083666 | 0.082407 | -0.001259 | -0.002598 | 0.000081 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | touch_brier | 265 | 2,650 | 0.147399 | 0.148396 | 0.000998 | -0.001369 | 0.003365 |
| 5 | preauction_0855 | event_scale_on_IV | same_clock_GJR | conditional_brier | 265 | 2,305 | 0.144801 | 0.146007 | 0.001206 | -0.001272 | 0.003684 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | brier_by_1 | 265 | 2,650 | 0.083855 | 0.082407 | -0.001448 | -0.002682 | -0.000215 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | touch_brier | 265 | 2,650 | 0.151531 | 0.148396 | -0.003135 | -0.006013 | -0.000256 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_GJR | conditional_brier | 265 | 2,305 | 0.147908 | 0.146007 | -0.001901 | -0.004033 | 0.000231 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | brier_by_1 | 265 | 2,650 | 0.083855 | 0.082219 | -0.001637 | -0.003435 | 0.000162 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | touch_brier | 265 | 2,650 | 0.151531 | 0.144562 | -0.006969 | -0.013489 | -0.000450 |
| 5 | preauction_0855 | schedule_scale_on_GJR | same_clock_IV | conditional_brier | 265 | 2,305 | 0.147908 | 0.143017 | -0.004891 | -0.010186 | 0.000404 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | brier_by_1 | 265 | 2,650 | 0.083679 | 0.082219 | -0.001460 | -0.002531 | -0.000389 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | touch_brier | 265 | 2,650 | 0.147557 | 0.144562 | -0.002995 | -0.005818 | -0.000173 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_IV | conditional_brier | 265 | 2,305 | 0.144934 | 0.143017 | -0.001917 | -0.004169 | 0.000336 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | brier_by_1 | 265 | 2,650 | 0.083679 | 0.082407 | -0.001272 | -0.002609 | 0.000065 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | touch_brier | 265 | 2,650 | 0.147557 | 0.148396 | 0.000839 | -0.001524 | 0.003202 |
| 5 | previous_1700 | event_scale_on_IV | same_clock_GJR | conditional_brier | 265 | 2,305 | 0.144934 | 0.146007 | 0.001073 | -0.001393 | 0.003539 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_GJR | brier_by_1 | 265 | 2,650 | 0.083840 | 0.082407 | -0.001432 | -0.002655 | -0.000210 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_GJR | touch_brier | 265 | 2,650 | 0.151534 | 0.148396 | -0.003138 | -0.006018 | -0.000258 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_GJR | conditional_brier | 265 | 2,305 | 0.147897 | 0.146007 | -0.001890 | -0.004023 | 0.000243 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_IV | brier_by_1 | 265 | 2,650 | 0.083840 | 0.082219 | -0.001621 | -0.003429 | 0.000187 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_IV | touch_brier | 265 | 2,650 | 0.151534 | 0.144562 | -0.006973 | -0.013536 | -0.000409 |
| 5 | previous_1700 | schedule_scale_on_GJR | same_clock_IV | conditional_brier | 265 | 2,305 | 0.147897 | 0.143017 | -0.004880 | -0.010225 | 0.000465 |
| 21 | preauction_0855 | event_scale_on_IV | same_clock_IV | brier_by_1 | 217 | 2,170 | 0.085883 | 0.084044 | -0.001840 | -0.002822 | -0.000857 |
| 21 | preauction_0855 | event_scale_on_IV | same_clock_IV | touch_brier | 217 | 2,170 | 0.189736 | 0.184372 | -0.005364 | -0.009562 | -0.001166 |
| 21 | preauction_0855 | event_scale_on_IV | same_clock_IV | conditional_brier | 217 | 1,882 | 0.213055 | 0.207997 | -0.005058 | -0.009836 | -0.000279 |
| 21 | preauction_0855 | event_scale_on_IV | same_clock_GJR | brier_by_1 | 217 | 2,170 | 0.085883 | 0.083745 | -0.002139 | -0.003687 | -0.000590 |

[All risk comparisons](risk-paired-comparisons.csv) · [Archived point and transition scores](protected-risk-predictions.csv.gz) · [Archived V17 stock risk observations](protected-v17-postopen-risk.csv.gz) · [Native V14–V16 joint score references](protected-native-joint-models.csv) · [Scenario files and hashes](event-path-archive.json) · [Matched first passage and survival](event-barrier-matched.csv) · [Joint path comparison](joint-path-leaderboard.csv)
