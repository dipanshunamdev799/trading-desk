# V12 Event Conditioned Forecasting

Weekly and monthly expiry proximity is obtained from the listed chain and dated traded fronts. Futures roll is an already observed contract switch. Exchange notices provide scheduled broad-index review dates, FOMC and RBI official calendars provide decision dates, and the FOMC announcement becomes observable to India after that U.S. day. The review-event history is partial and March 2026’s broad review contains no NIFTY50 replacements. Large moves, extreme bank rotation, weakening breadth, IV jumps and global moves use the preceding mature-fit sample’s 80th percentile. Economic surprise magnitudes and retrospectively chosen market shocks are excluded. [FOMC official schedule](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm) · [RBI 2025–26 schedule](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60062) · [RBI 2026–27 schedule](https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62422) · [Verified September 2025 index notice](https://niftyindices.com/Press_Release/ind_prs22082025.pdf) · [March 2026 review](https://www.niftyindices.com/Press_Release/ind_prs23022026.pdf).

The simple event baseline blends earlier like-event returns with normal historical returns using fixed 35% event weight, only after the event has at least 12 mature training origins. Other tests compare event-conditioned realized risk, market risk, and unconditioned IV scales on exact origins. Counts include both rolling dates and disjoint outcome windows. Sparse scheduled-event cells are descriptive and are kept as such.

| horizon | model | event | n | disjoint | brier | crps | coverage80 | V12_STAT_brier_gain | V12_STAT_crps_gain | path_volatility_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V12_EVENT_HISTORY | breadth_decay | 48 | 16 | 0.244857 | 0.010243 | 0.750000 | 0.001054 | -0.000066 | — |
| 5 | V12_EVENT_HISTORY | fomc_during_window | 45 | 9 | 0.262764 | 0.011188 | 0.688889 | -0.023093 | -0.001058 | — |
| 5 | V12_EVENT_HISTORY | fomc_recent | 17 | 9 | 0.296495 | 0.014788 | 0.764706 | -0.017702 | -0.001655 | — |
| 5 | V12_EVENT_HISTORY | global_jump | 56 | 21 | 0.251882 | 0.014599 | 0.642857 | -0.020929 | -0.000705 | — |
| 5 | V12_EVENT_HISTORY | index_review_during_window | 5 | 1 | 0.266021 | 0.011282 | 0.600000 | 0.013182 | 0.000597 | — |
| 5 | V12_EVENT_HISTORY | iv_jump | 77 | 28 | 0.262698 | 0.014396 | 0.623377 | 0.015512 | 0.000102 | — |
| 5 | V12_EVENT_HISTORY | near_monthly_expiry | 25 | 13 | 0.253659 | 0.014360 | 0.560000 | -0.026741 | -0.001390 | — |
| 5 | V12_EVENT_HISTORY | near_weekly_expiry | 57 | 43 | 0.262049 | 0.012426 | 0.631579 | -0.019568 | -0.000551 | — |
| 5 | V12_EVENT_HISTORY | prior_move | 67 | 30 | 0.265470 | 0.015639 | 0.582090 | -0.008784 | -0.000608 | — |
| 5 | V12_EVENT_HISTORY | rbi_during_window | 30 | 6 | 0.255153 | 0.013094 | 0.766667 | 0.037153 | 0.001305 | — |
| 5 | V12_EVENT_HISTORY | rbi_recent | 12 | 6 | 0.265340 | 0.009351 | 0.750000 | 0.018353 | 0.000559 | — |
| 5 | V12_EVENT_HISTORY | roll_observed | 13 | 13 | 0.263454 | 0.014658 | 0.692308 | -0.003046 | -0.001512 | — |
| 5 | V12_EVENT_HISTORY | sector_shock | 68 | 31 | 0.264207 | 0.011294 | 0.779412 | 0.011815 | -0.000219 | — |
| 5 | V12_EVENT_IV | breadth_decay | 48 | 16 | 0.244456 | 0.010114 | 0.750000 | 0.001455 | 0.000063 | 0.031965 |
| 5 | V12_EVENT_IV | fomc_during_window | 45 | 9 | 0.242773 | 0.010236 | 0.711111 | -0.003102 | -0.000105 | 0.040771 |
| 5 | V12_EVENT_IV | fomc_recent | 17 | 9 | 0.281394 | 0.013178 | 0.823529 | -0.002600 | -0.000044 | 0.062566 |
| 5 | V12_EVENT_IV | global_jump | 56 | 21 | 0.226598 | 0.013807 | 0.696429 | 0.004355 | 0.000088 | 0.049276 |
| 5 | V12_EVENT_IV | index_review_during_window | 5 | 1 | 0.234166 | 0.011161 | 0.800000 | 0.045038 | 0.000718 | 0.072826 |
| 5 | V12_EVENT_IV | iv_jump | 77 | 28 | 0.285043 | 0.014533 | 0.688312 | -0.006834 | -0.000034 | 0.054755 |
| 5 | V12_EVENT_IV | near_monthly_expiry | 25 | 13 | 0.221892 | 0.013110 | 0.720000 | 0.005026 | -0.000139 | 0.026523 |
| 5 | V12_EVENT_IV | near_weekly_expiry | 57 | 43 | 0.237963 | 0.011838 | 0.771930 | 0.004518 | 0.000038 | 0.042690 |
| 5 | V12_EVENT_IV | prior_move | 67 | 30 | 0.253685 | 0.015098 | 0.656716 | 0.003001 | -0.000067 | 0.059882 |
| 5 | V12_EVENT_IV | rbi_during_window | 30 | 6 | 0.296675 | 0.014480 | 0.833333 | -0.004369 | -0.000081 | 0.049350 |
| 5 | V12_EVENT_IV | rbi_recent | 12 | 6 | 0.300728 | 0.010216 | 0.750000 | -0.017035 | -0.000305 | 0.054304 |
| 5 | V12_EVENT_IV | roll_observed | 13 | 13 | 0.276310 | 0.013519 | 0.538462 | -0.015902 | -0.000374 | 0.056971 |
| 5 | V12_EVENT_IV | sector_shock | 68 | 31 | 0.274436 | 0.011006 | 0.808824 | 0.001586 | 0.000068 | 0.046711 |
| 21 | V12_EVENT_HISTORY | breadth_decay | 22 | 5 | 0.213115 | 0.013124 | 0.954545 | 0.021372 | 0.003595 | — |
| 21 | V12_EVENT_HISTORY | fomc_during_window | 146 | 8 | 0.278223 | 0.027968 | 0.602740 | 0.005557 | 0.002445 | — |
| 21 | V12_EVENT_HISTORY | fomc_recent | 13 | 7 | 0.330606 | 0.013227 | 0.846154 | -0.024293 | -0.000747 | — |
| 21 | V12_EVENT_HISTORY | global_jump | 40 | 6 | 0.289463 | 0.024244 | 0.525000 | -0.046486 | 0.001150 | — |
| 21 | V12_EVENT_HISTORY | index_review_during_window | 21 | 1 | 0.251347 | 0.038333 | 0.238095 | 0.036643 | -0.000220 | — |
| 21 | V12_EVENT_HISTORY | iv_jump | 73 | 8 | 0.264165 | 0.025555 | 0.602740 | -0.030068 | 0.002171 | — |
| 21 | V12_EVENT_HISTORY | near_monthly_expiry | 19 | 7 | 0.289123 | 0.024915 | 0.631579 | 0.004773 | 0.004633 | — |
| 21 | V12_EVENT_HISTORY | near_weekly_expiry | 47 | 10 | 0.304468 | 0.025900 | 0.617021 | -0.018128 | 0.001913 | — |
| 21 | V12_EVENT_HISTORY | prior_move | 64 | 9 | 0.283623 | 0.030129 | 0.562500 | -0.018285 | 0.001849 | — |
| 21 | V12_EVENT_HISTORY | rbi_during_window | 97 | 6 | 0.244874 | 0.017736 | 0.721649 | -0.000776 | 0.001774 | — |
| 21 | V12_EVENT_HISTORY | rbi_recent | 12 | 6 | 0.347604 | 0.040365 | 0.583333 | -0.084135 | -0.000289 | — |
| 21 | V12_EVENT_HISTORY | roll_observed | 10 | 7 | 0.286626 | 0.031700 | 0.600000 | 0.048358 | 0.005889 | — |
| 21 | V12_EVENT_HISTORY | sector_shock | 62 | 9 | 0.293059 | 0.033295 | 0.532258 | 0.010247 | 0.001887 | — |
| 21 | V12_EVENT_IV | breadth_decay | 22 | 5 | 0.281161 | 0.017715 | 0.727273 | -0.046673 | -0.000996 | 0.039257 |
| 21 | V12_EVENT_IV | fomc_during_window | 146 | 8 | 0.296435 | 0.030649 | 0.568493 | -0.012654 | -0.000237 | 0.043578 |
| 21 | V12_EVENT_IV | fomc_recent | 13 | 7 | 0.310591 | 0.011997 | 1.000000 | -0.004278 | 0.000484 | 0.041045 |
| 21 | V12_EVENT_IV | global_jump | 40 | 6 | 0.248533 | 0.025509 | 0.600000 | -0.005557 | -0.000115 | 0.053170 |
| 21 | V12_EVENT_IV | index_review_during_window | 21 | 1 | 0.289184 | 0.038219 | 0.666667 | -0.001194 | -0.000106 | 0.124704 |
| 21 | V12_EVENT_IV | iv_jump | 73 | 8 | 0.247856 | 0.027667 | 0.657534 | -0.013758 | 0.000059 | 0.049063 |
| 21 | V12_EVENT_IV | near_monthly_expiry | 19 | 7 | 0.298303 | 0.029520 | 0.631579 | -0.004407 | 0.000027 | 0.032684 |
| 21 | V12_EVENT_IV | near_weekly_expiry | 47 | 10 | 0.289961 | 0.028061 | 0.595745 | -0.003620 | -0.000248 | 0.040707 |
| 21 | V12_EVENT_IV | prior_move | 64 | 9 | 0.268127 | 0.031793 | 0.703125 | -0.002789 | 0.000185 | 0.056268 |
| 21 | V12_EVENT_IV | rbi_during_window | 97 | 6 | 0.280349 | 0.019996 | 0.711340 | -0.036250 | -0.000486 | 0.033935 |
| 21 | V12_EVENT_IV | rbi_recent | 12 | 6 | 0.232045 | 0.039470 | 0.500000 | 0.031424 | 0.000606 | 0.041753 |
| 21 | V12_EVENT_IV | roll_observed | 10 | 7 | 0.384835 | 0.038033 | 0.500000 | -0.049851 | -0.000443 | 0.038769 |
| 21 | V12_EVENT_IV | sector_shock | 62 | 9 | 0.308614 | 0.035100 | 0.596774 | -0.005307 | 0.000082 | 0.051890 |

[Full active and inactive event scores](event-conditioned-scores.csv) · [Origin flags and training cutoffs](event-origin-states.csv).
