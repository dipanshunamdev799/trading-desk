# NIFTY V18 — Event calendar and forward risk

The schedule corpus combines **1,839** already public earnings-board notices and dated RBI and Federal Reserve announcements. A calendar row is eligible only once its source was public. The earliest company notice, its scheduled date, and a later reschedule or cancellation remain separate records. The February/other policy dates are drawn from the schedule then available, and release outcomes are excluded from the schedule exposure. The estimated horizon uses business weekdays and therefore approximates the number of sessions around holiday changes. The nearest where available NIFTY futures expiry comes from the strictly earlier exchange contract state and receives its own source-date guard. V18 preserved **3,208** horizon-specific exposure rows. The Federal Reserve's prior announcement supplies dates for 2025–2026 and is calendar metadata. Complete original economic-release calendar and index-rebalance announcement histories remain unresolved.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | brier | 265 | 53 | 0.158265 | 0.156619 | -0.001646 | -0.035240 | 0.031949 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | crps | 265 | 53 | 0.027240 | 0.026149 | -0.001090 | -0.004056 | 0.001875 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.038369 | 0.037785 | -0.000584 | -0.005630 | 0.004462 |
| 5 | preauction_0855 | scheduled_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.328413 | 0.278256 | -0.050156 | -0.137622 | 0.037310 |
| 5 | preauction_0855 | scheduled_then_fundamental | risk_calibrated_iv | brier | 265 | 53 | 0.154844 | 0.156619 | 0.001775 | -0.039000 | 0.042550 |
| 5 | preauction_0855 | scheduled_then_fundamental | risk_calibrated_iv | crps | 265 | 53 | 0.026683 | 0.026149 | -0.000534 | -0.003719 | 0.002651 |
| 5 | preauction_0855 | scheduled_then_fundamental | risk_calibrated_iv | abs_error | 265 | 53 | 0.037266 | 0.037785 | 0.000519 | -0.004886 | 0.005923 |
| 5 | preauction_0855 | scheduled_then_fundamental | risk_calibrated_iv | qlike | 265 | 53 | 0.325288 | 0.278256 | -0.047032 | -0.141974 | 0.047910 |
| 5 | preauction_0855 | schedule_delayed | risk_calibrated_iv | brier | 265 | 53 | 0.162747 | 0.156619 | -0.006128 | -0.031383 | 0.019126 |
| 5 | preauction_0855 | schedule_delayed | risk_calibrated_iv | crps | 265 | 53 | 0.027000 | 0.026149 | -0.000851 | -0.003652 | 0.001950 |
| 5 | preauction_0855 | schedule_delayed | risk_calibrated_iv | abs_error | 265 | 53 | 0.038227 | 0.037785 | -0.000442 | -0.005119 | 0.004235 |
| 5 | preauction_0855 | schedule_delayed | risk_calibrated_iv | qlike | 265 | 53 | 0.320171 | 0.278256 | -0.041914 | -0.127265 | 0.043436 |
| 5 | preauction_0855 | scheduled_risk | protected_raw_iv | brier | 265 | 53 | 0.158265 | 0.155657 | -0.002608 | -0.031309 | 0.026092 |
| 5 | preauction_0855 | scheduled_risk | protected_raw_iv | abs_error | 265 | 53 | 0.038369 | 0.037814 | -0.000555 | -0.006443 | 0.005334 |
| 5 | preauction_0855 | scheduled_risk | protected_raw_iv | qlike | 265 | 53 | 0.328413 | 0.276187 | -0.052226 | -0.148058 | 0.043607 |
| 5 | preauction_0855 | scheduled_risk | protected_fixed_iv_rv | brier | 265 | 53 | 0.158265 | 0.152707 | -0.005558 | -0.025184 | 0.014069 |
| 5 | preauction_0855 | scheduled_risk | protected_fixed_iv_rv | abs_error | 265 | 53 | 0.038369 | 0.038484 | 0.000115 | -0.004625 | 0.004855 |
| 5 | preauction_0855 | scheduled_risk | protected_fixed_iv_rv | qlike | 265 | 53 | 0.328413 | 0.286114 | -0.042299 | -0.121768 | 0.037170 |
| 5 | preauction_0855 | scheduled_then_fundamental | protected_raw_iv | brier | 265 | 53 | 0.154844 | 0.155657 | 0.000813 | -0.034490 | 0.036116 |
| 5 | preauction_0855 | scheduled_then_fundamental | protected_raw_iv | abs_error | 265 | 53 | 0.037266 | 0.037814 | 0.000548 | -0.005628 | 0.006724 |
| 5 | preauction_0855 | scheduled_then_fundamental | protected_raw_iv | qlike | 265 | 53 | 0.325288 | 0.276187 | -0.049101 | -0.151907 | 0.053704 |
| 5 | preauction_0855 | scheduled_then_fundamental | protected_fixed_iv_rv | brier | 265 | 53 | 0.154844 | 0.152707 | -0.002136 | -0.026681 | 0.022409 |
| 5 | preauction_0855 | scheduled_then_fundamental | protected_fixed_iv_rv | abs_error | 265 | 53 | 0.037266 | 0.038484 | 0.001218 | -0.003420 | 0.005856 |
| 5 | preauction_0855 | scheduled_then_fundamental | protected_fixed_iv_rv | qlike | 265 | 53 | 0.325288 | 0.286114 | -0.039175 | -0.123060 | 0.044711 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | brier | 265 | 53 | 0.158752 | 0.157572 | -0.001180 | -0.030936 | 0.028576 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | crps | 265 | 53 | 0.027259 | 0.026176 | -0.001082 | -0.004011 | 0.001847 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | abs_error | 265 | 53 | 0.038379 | 0.037858 | -0.000521 | -0.004646 | 0.003605 |
| 5 | previous_1700 | scheduled_risk | risk_calibrated_iv | qlike | 265 | 53 | 0.329932 | 0.278972 | -0.050959 | -0.124865 | 0.022946 |
| 5 | previous_1700 | scheduled_then_fundamental | risk_calibrated_iv | brier | 265 | 53 | 0.157207 | 0.157572 | 0.000365 | -0.035526 | 0.036256 |
| 5 | previous_1700 | scheduled_then_fundamental | risk_calibrated_iv | crps | 265 | 53 | 0.027010 | 0.026176 | -0.000834 | -0.004070 | 0.002402 |
| 5 | previous_1700 | scheduled_then_fundamental | risk_calibrated_iv | abs_error | 265 | 53 | 0.037797 | 0.037858 | 0.000061 | -0.004463 | 0.004586 |
| 5 | previous_1700 | scheduled_then_fundamental | risk_calibrated_iv | qlike | 265 | 53 | 0.336172 | 0.278972 | -0.057200 | -0.144437 | 0.030037 |
| 5 | previous_1700 | schedule_delayed | risk_calibrated_iv | brier | 265 | 53 | 0.162985 | 0.157572 | -0.005413 | -0.028292 | 0.017466 |
| 5 | previous_1700 | schedule_delayed | risk_calibrated_iv | crps | 265 | 53 | 0.026994 | 0.026176 | -0.000818 | -0.003590 | 0.001954 |
| 5 | previous_1700 | schedule_delayed | risk_calibrated_iv | abs_error | 265 | 53 | 0.038159 | 0.037858 | -0.000300 | -0.004120 | 0.003519 |
| 5 | previous_1700 | schedule_delayed | risk_calibrated_iv | qlike | 265 | 53 | 0.321472 | 0.278972 | -0.042500 | -0.115121 | 0.030120 |
| 21 | preauction_0855 | scheduled_risk | risk_calibrated_iv | brier | 217 | 11 | 0.273720 | 0.221396 | -0.052324 | -0.112320 | 0.007673 |
| 21 | preauction_0855 | scheduled_risk | risk_calibrated_iv | crps | 217 | 11 | 0.041797 | 0.031821 | -0.009976 | -0.018855 | -0.001098 |

The BLS first-release retrieval produced **0** usable records under the archive and publication requirements. The CPI fields remained missing in that case. ATM IV, path-based GJR and the native published IV/RV and EGARCH probabilities are separate controls.

[Verified board notices](scheduled-board-results.csv.gz) · [Policy schedule and provenance](policy-schedule.csv) · [Horizon exposure audit](event-schedule-exposures.csv.gz) · [Matched risk forecasts](risk-paired-comparisons.csv) · [Federal Reserve dated schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) · [RBI 2025 schedule release](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60062) · [RBI 2026 schedule publication](https://rbi.org.in/scripts/PublicationsView.aspx?Id=23809) · [NSE expiry revision circular](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAOP68747.pdf)
