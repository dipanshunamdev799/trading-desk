# NIFTY V7 · Global And Liquidity Research

Run `2026-11-24/run-001`. Historical inputs cover 2025–2026 through the frozen November 17 close.

The frozen V5 availability map contains 6042 selected foreign origin/series rows. Every selected source availability time precedes its recorded decision. Known cash-index series use exchange time zones and a two-hour close buffer. Uncertain CFD and FX conventions use a two-UTC-day delay. Historical receipt timestamps remain reconstructed. `IXIX` is a provider US technology proxy. Verified Nasdaq cash-index and US yield histories were unavailable in the retained input set, so the tested technology link is narrower than an exchange-authenticated Nasdaq transmission study.

The registered intermediate tests add limited foreign inputs to own-state controls. Targets include IT and energy future relative returns, endpoint sector synchrony and breadth, absolute return, future realized volatility and large moves. The breadth branch uses HSI/Nikkei five-session returns and their absolute divergence. Each correction uses only matured targets in its historical monthly refit. A fixed .60 correlation gate and past-training-median volatility split assess whether performance is concentrated in identifiable regimes. `auxiliary-comparison.csv` contains those slices. Downstream direct and reconstructed intermediate corrections share the same eligible training and query dates.

| horizon | target | method | n | mae | rmse |
| --- | --- | --- | --- | --- | --- |
| 5 | breadth | BASE | 92 | 0.261506 | 0.296006 |
| 5 | breadth | GLOBAL | 92 | 0.265449 | 0.300767 |
| 5 | energy | BASE | 92 | 0.013616 | 0.018230 |
| 5 | energy | GLOBAL | 92 | 0.013608 | 0.018304 |
| 5 | it | BASE | 92 | 0.031697 | 0.039988 |
| 5 | it | GLOBAL | 92 | 0.031701 | 0.039967 |
| 5 | large_move | BASE | 92 | 0.351630 | 0.451138 |
| 5 | large_move | GLOBAL | 92 | 0.362415 | 0.454314 |
| 5 | magnitude | BASE | 92 | 0.010454 | 0.016376 |
| 5 | magnitude | GLOBAL | 92 | 0.010735 | 0.016688 |
| 5 | synchrony | BASE | 92 | 0.082237 | 0.112233 |
| 5 | synchrony | GLOBAL | 92 | 0.083494 | 0.113256 |
| 5 | volatility | BASE | 92 | 0.039804 | 0.052460 |
| 5 | volatility | GLOBAL | 92 | 0.040661 | 0.053464 |
| 21 | breadth | BASE | 76 | 0.291346 | 0.325631 |
| 21 | breadth | GLOBAL | 76 | 0.296089 | 0.329563 |
| 21 | energy | BASE | 76 | 0.038451 | 0.047668 |
| 21 | energy | GLOBAL | 76 | 0.039016 | 0.048493 |
| 21 | it | BASE | 76 | 0.073751 | 0.094905 |
| 21 | it | GLOBAL | 76 | 0.074338 | 0.095949 |
| 21 | large_move | BASE | 76 | 0.366688 | 0.480513 |
| 21 | large_move | GLOBAL | 76 | 0.382527 | 0.485088 |
| 21 | magnitude | BASE | 76 | 0.022236 | 0.031560 |
| 21 | magnitude | GLOBAL | 76 | 0.023132 | 0.031706 |
| 21 | synchrony | BASE | 76 | 0.147753 | 0.175830 |
| 21 | synchrony | GLOBAL | 76 | 0.149205 | 0.176973 |
| 21 | volatility | BASE | 76 | 0.022377 | 0.026226 |
| 21 | volatility | GLOBAL | 76 | 0.025144 | 0.028801 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_BASE5 | 92 | 0.630435 | 0.665699 | 0.225969 | 0.642739 | 0.011468 | 0.015278 | 0.015096 | 0.021117 | 0.543478 | 0.760870 | 0.043712 |
| G_DIRECT5 | 92 | 0.597826 | 0.634011 | 0.233357 | 0.657029 | 0.011609 | 0.015158 | 0.015078 | 0.021124 | 0.543478 | 0.750000 | 0.044423 |
| G_INTERMEDIATE5 | 92 | 0.608696 | 0.653604 | 0.249147 | 0.693440 | 0.011938 | 0.016120 | 0.015517 | 0.021900 | 0.521739 | 0.750000 | 0.042594 |
| V6_BRIER | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |


| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_BASE21 | 53 | 0.188679 | 0.384615 | 0.518423 | 1.330585 | 0.050388 | 0.067580 | 0.073803 | 0.070600 | 0.018868 | 0.245283 | 0.098487 |
| G_DIRECT21 | 53 | 0.169811 | 0.346154 | 0.528683 | 1.359812 | 0.050780 | 0.067445 | 0.073329 | 0.070685 | 0.018868 | 0.207547 | 0.096322 |
| G_INTERMEDIATE21 | 53 | 0.113208 | 0.230769 | 0.538067 | 1.378009 | 0.051753 | 0.067810 | 0.074829 | 0.071363 | 0.018868 | 0.169811 | 0.093108 |
| V6_BRIER | 76 | 0.539474 | 0.575986 | 0.264309 | 0.726979 | 0.030275 | 0.038624 | 0.037553 | 0.049682 | 0.315789 | 0.500000 | 0.071598 |


Weekly energy MAE falls only by about 0.000008. The other weekly overall intermediates and every monthly overall intermediate worsen. The NIFTY models lose to their own eligible-date controls. Three July monthly downstream fits lack the minimum purged intermediate history and remain unestimated. The resulting monthly comparison has 53 origins. These are predictive transmission tests with regime and sample restrictions. They do not identify economic causation.

## Domestic activity and actual intraday candles

Upstox supplied 6,976 archived 25-minute index bars across eight bounded requests. Exact 15-bar regular-session grid and OHLC checks retained 396 sessions from the 403 aligned daily dates and excluded 7 observed sessions with invalid or nonregular grids. The median difference between the last intraday bar and the daily close was 7.15 points in absolute terms, and the max was 85.70. We use intraday increments, 50-minute opening and closing behavior, and leave the official daily return target anchored to archived daily closes. Index volume is excluded. Daily opening/closing features use gap and open-to-close logs, trailing range, and actual traded ETF volume ratios. Positioning inputs come from the inherited NSE daily derivatives archives with one-session lag. The liquid-stock panel is a marked survivorship-exposed proxy study using real historical observations from a later selected basket. [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE archive reports](https://www.nseindia.com/all-reports)

| model | n | accuracy | balanced_accuracy | brier | log_loss | crps | mae | median_mae | rmse | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_NO_DEF | 92 | 0.782609 | 0.791001 | 0.169803 | 0.522347 | 0.010068 | 0.013095 | 0.012614 | 0.019635 | 0.510870 | 0.793478 | 0.039009 |
| L_ETF | 92 | 0.760870 | 0.765360 | 0.175312 | 0.533128 | 0.009873 | 0.013138 | 0.012833 | 0.018992 | 0.521739 | 0.782609 | 0.038203 |
| L_DAILY | 92 | 0.782609 | 0.791001 | 0.166724 | 0.515487 | 0.009893 | 0.012946 | 0.012465 | 0.019186 | 0.532609 | 0.804348 | 0.038713 |
| L_INTRADAY_BASE | 91 | 0.791209 | 0.798411 | 0.170731 | 0.524774 | 0.010138 | 0.013247 | 0.012750 | 0.019760 | 0.494505 | 0.813187 | 0.038773 |
| L_INTRADAY | 91 | 0.791209 | 0.798411 | 0.171549 | 0.526774 | 0.010183 | 0.013346 | 0.012784 | 0.019853 | 0.494505 | 0.813187 | 0.038780 |
| L_POSITION | 92 | 0.771739 | 0.774794 | 0.172553 | 0.527998 | 0.010288 | 0.013276 | 0.012880 | 0.020170 | 0.500000 | 0.782609 | 0.038660 |
| L_STOCK_PROXY | 92 | 0.782609 | 0.787615 | 0.169969 | 0.522932 | 0.010133 | 0.013105 | 0.012590 | 0.019779 | 0.521739 | 0.815217 | 0.039125 |
| T_DAY_OC | 92 | 0.782609 | 0.791001 | 0.168481 | 0.519107 | 0.009993 | 0.013042 | 0.012568 | 0.019412 | 0.500000 | 0.793478 | 0.038901 |
| T_DAY_ETF | 92 | 0.782609 | 0.791001 | 0.166525 | 0.515537 | 0.009974 | 0.013004 | 0.012523 | 0.019415 | 0.521739 | 0.804348 | 0.038902 |
| T_DAY_LAG | 92 | 0.782609 | 0.791001 | 0.174936 | 0.534458 | 0.010144 | 0.013282 | 0.012887 | 0.019663 | 0.500000 | 0.793478 | 0.039320 |
| T_DAY_WINDOW | 92 | 0.706522 | 0.718191 | 0.211277 | 0.612468 | 0.011300 | 0.014784 | 0.014354 | 0.021699 | 0.554348 | 0.750000 | 0.042914 |


The intraday result has 91 weekly matched origins and is slightly worse than its identical-availability control. Positioning and the stock-proxy additions do not improve the weekly Brier benchmark. Daily opening/closing and ETF terms jointly give Brier .166724, CRPS .009893 and 80.43% interval coverage. The open-close and activity feature sets are individually competitive. A shorter training window reduces both. The activity evidence is a representation lead, not proof of a liquidity premium.

The weekly cohort contains 92 overlapping forecasts and 19 disjoint return windows. The monthly cohort contains 76 overlapping forecasts and four disjoint windows. All reported scores come from research-exposed history.
