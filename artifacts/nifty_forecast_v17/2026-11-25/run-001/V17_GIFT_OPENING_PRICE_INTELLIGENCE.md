# NIFTY V17 — GIFT NIFTY opening-price intelligence

GIFT prices progressively narrowed the opening-price distribution before the regular NSE session. On 246 matched mornings, the same anchored method scored 0.264968 Brier at 17:00 on the prior Indian cash session and 0.100024 using 08:55 data. The latter beat earlier checkpoints most clearly on prior-close, completed-US and 07:00 comparisons. The 06:00 clock lacked enough fresh observations. The archived 08:45 and 08:55 comparisons are nearly indistinguishable on their common mornings. The historical auction begins at 09:00 IST under the regular NSE timetable. GIFT observation time means the bar’s latest permissible end plus the publication buffer. The US checkpoint is the latest eligible NY cash close plus 60 minutes.

| cutoff | raw eligible marks |
| --- | --- |
| prior_close | 397 |
| us_complete | 373 |
| 06:00 | 3 |
| 07:00 | 391 |
| 08:00 | 393 |
| 08:30 | 393 |
| 08:45 | 395 |
| 08:55 | 395 |

| cutoff | n | Brier | CRPS | accuracy | MAE | MdAE | coverage80 | width80 | median age |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior_close | 252 | 0.264567 | 0.003364 | 0.531746 | 0.004319 | 0.002670 | 0.746032 | 0.010932 | 5.000000 |
| us_complete | 230 | 0.167095 | 0.002456 | 0.773913 | 0.003110 | 0.001874 | 0.765217 | 0.007632 | 10.000000 |
| 07:00 | 245 | 0.126935 | 0.001619 | 0.820408 | 0.002212 | 0.001681 | 0.767347 | 0.006063 | 5.000000 |
| 08:00 | 247 | 0.112573 | 0.001515 | 0.850202 | 0.002058 | 0.001585 | 0.748988 | 0.005759 | 5.000000 |
| 08:30 | 247 | 0.105354 | 0.001470 | 0.854251 | 0.001991 | 0.001470 | 0.777328 | 0.005772 | 5.000000 |
| 08:45 | 248 | 0.101647 | 0.001441 | 0.879032 | 0.001962 | 0.001466 | 0.786290 | 0.005689 | 5.000000 |
| 08:55 | 248 | 0.101285 | 0.001451 | 0.866935 | 0.001961 | 0.001428 | 0.774194 | 0.005623 | 5.000000 |

## Mechanical marks and statistical fits

The mechanical reference is the latest GIFT mark divided by a same-instrument previous-session anchor. The prior cash-level model uses the prior NIFTY close directly. The rolling-basis model subtracts the trailing median of the contemporaneous futures/cash differential. The linear mapping uses earlier realized gaps. Its scale-aware variant fits the absolute errors of earlier genuine out-of-sample mappings. Raw overnight uses the same historical shape centered on the literal GIFT price change. The anchored variant lets the historical residual median displace the forecast. On its own 08:55 cohort, it scored 0.101285 Brier and 0.001451 CRPS with 77.42% central 80% coverage and 0.56% width. The protected V16 interval covered 76.61%.

The raw overnight method achieved 0.100795 Brier, 88.71% accuracy and 0.001459 CRPS on the 248 mornings. Variance scaling reached 78.63% coverage with 0.55% width and 0.100075 Brier. Its CRPS of 0.001565 shows the distribution tradeoff. The raw offshore move accounts for most of the opening result on these dates.

| model | n | Brier | CRPS | log loss | accuracy | MAE | MdAE | RMSE | coverage80 | width80 | interval80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| anchored_1515 | 248 | 0.101824 | 0.001518 | 0.351299 | 0.866935 | 0.002040 | 0.001482 | 0.002925 | 0.774194 | 0.005684 | 0.010562 |
| anchored_1530 | 248 | 0.101285 | 0.001451 | 0.348004 | 0.866935 | 0.001961 | 0.001428 | 0.002763 | 0.774194 | 0.005623 | 0.009982 |
| anchored_1540 | 248 | 0.102294 | 0.001454 | 0.350104 | 0.879032 | 0.001953 | 0.001398 | 0.002777 | 0.778226 | 0.005537 | 0.010123 |
| anchored_1700 | 248 | 0.109962 | 0.001602 | 0.374951 | 0.858871 | 0.002137 | 0.001437 | 0.003395 | 0.778226 | 0.005698 | 0.011391 |
| delayed_15 | 247 | 0.104001 | 0.001441 | 0.345211 | 0.854251 | 0.001945 | 0.001416 | 0.002725 | 0.777328 | 0.005682 | 0.009880 |
| last_night_move | 249 | 0.239071 | 0.002725 | 0.693345 | 0.610442 | 0.003517 | 0.002187 | 0.005734 | 0.755020 | 0.008927 | 0.020428 |
| mapped_linear | 248 | 0.102155 | 0.001595 | 0.342216 | 0.879032 | 0.002077 | 0.001377 | 0.003747 | 0.754032 | 0.005263 | 0.011760 |
| raw_cash_level | 252 | 0.157251 | 0.001962 | 0.509624 | 0.765873 | 0.002732 | 0.002114 | 0.003527 | 0.722222 | 0.006796 | 0.012676 |
| raw_overnight | 248 | 0.100795 | 0.001459 | 0.346917 | 0.887097 | 0.001964 | 0.001464 | 0.002777 | 0.766129 | 0.005622 | 0.010056 |
| roll_guarded | 180 | 0.095394 | 0.001197 | 0.308584 | 0.872222 | 0.001656 | 0.001297 | 0.002182 | 0.794444 | 0.004868 | 0.007823 |
| rolling_basis | 252 | 0.100633 | 0.001560 | 0.340012 | 0.880952 | 0.002092 | 0.001486 | 0.003016 | 0.797619 | 0.006805 | 0.010821 |
| variance_scaled | 248 | 0.100075 | 0.001565 | 0.338140 | 0.875000 | 0.002079 | 0.001382 | 0.003744 | 0.786290 | 0.005546 | 0.011023 |

| candidate | control | metric | n | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- |
| raw_overnight | anchored_1530 | brier | 248 | 0.000490 | -0.002463 | 0.003444 |
| raw_overnight | anchored_1530 | crps | 248 | -7.82e-06 | -0.000036 | 0.000020 |
| raw_overnight | anchored_1530 | interval_score | 248 | -0.000073 | -0.000362 | 0.000216 |
| mapped_linear | anchored_1530 | brier | 248 | -0.000870 | -0.005701 | 0.003961 |
| mapped_linear | anchored_1530 | crps | 248 | -0.000144 | -0.000518 | 0.000230 |
| mapped_linear | anchored_1530 | interval_score | 248 | -0.001778 | -0.005554 | 0.001998 |
| variance_scaled | anchored_1530 | brier | 248 | 0.001210 | -0.003449 | 0.005869 |
| variance_scaled | anchored_1530 | crps | 248 | -0.000114 | -0.000468 | 0.000240 |
| variance_scaled | anchored_1530 | interval_score | 248 | -0.001040 | -0.004397 | 0.002316 |
| rolling_basis | anchored_1530 | brier | 248 | 0.000580 | -0.026354 | 0.027514 |
| rolling_basis | anchored_1530 | crps | 248 | -0.000111 | -0.000328 | 0.000106 |
| rolling_basis | anchored_1530 | interval_score | 248 | -0.000907 | -0.002314 | 0.000499 |

## Contract, anchor and event checks

The inherited Yahoo vendor alias has archived historical observations and unresolved dated expiry identifiers. The study tracked the calendar rollover window, allowed anchor ages and price availability, then tested 15:15, 15:30, 15:40 and 17:00 prior marks, delayed observations, gaps after weekends or holidays and large observed outliers. Historical trading-hour or expiry changes can also affect missing-clock eligibility. The newest bar in an eligible regular morning can be only as fresh as the documented guard. The NSE IX page does not supply a compatible dated-contract tape in this workspace. Calibration is archived separately for direction and the ±0.5% and ±1.0% events with case counts by probability bin.

| screen | model | n | brier | crps | accuracy | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| after_weekend_or_holiday | anchored_1530 | 60 | 0.076591 | 0.001787 | 0.916667 | 0.716667 | 0.005599 |
| age_5_or_less | anchored_1530 | 243 | 0.102100 | 0.001463 | 0.864198 | 0.769547 | 0.005632 |
| all | anchored_1530 | 248 | 0.101285 | 0.001451 | 0.866935 | 0.774194 | 0.005623 |
| excluding_largest_10 | anchored_1530 | 238 | 0.105540 | 0.001324 | 0.861345 | 0.802521 | 0.005637 |
| excluding_largest_20 | anchored_1530 | 228 | 0.110166 | 0.001313 | 0.855263 | 0.802632 | 0.005634 |
| excluding_largest_5 | anchored_1530 | 243 | 0.103369 | 0.001389 | 0.864198 | 0.790123 | 0.005630 |
| not_roll | anchored_1530 | 180 | 0.097355 | 0.001217 | 0.866667 | 0.822222 | 0.005618 |
| ordinary_calendar_day | anchored_1530 | 188 | 0.109167 | 0.001344 | 0.851064 | 0.792553 | 0.005631 |

[Clock-matched score gaps](opening-clock-matched.csv) · [Per-clock model comparisons](opening-matched.csv) · [Opening sensitivity](opening-clock-sensitivity.csv) · [Opening distribution calibration](opening-calibration.csv) · [Eligible source timestamps](gift-decision-clock.csv) · [Regular NSE auction schedule](https://www.nseindia.com/static/products-services/equity-market-pre-open)
