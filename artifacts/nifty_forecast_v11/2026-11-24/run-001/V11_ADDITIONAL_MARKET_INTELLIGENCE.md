# V11 Additional Market Intelligence

Nasdaq archive acquisition gave **471** matched dates for RSP, SPY, XLF and XLK. RSP/SPY is a traded equal-weight/cap-weight proxy and XLF/XLK is a US sector control. US data enter only if their session date precedes the Indian origin. Exchange closes can carry corporate-action and tracking effects. Models compare US cap/sector context, genuine ETF weighting spreads, the domestic–US breadth gap and a scale extension. [Nasdaq RSP history](https://www.nasdaq.com/market-activity/etf/rsp/historical) · [Nasdaq SPY history](https://www.nasdaq.com/market-activity/etf/spy/historical).

The official NSE derivatives history includes observed same-contract cash/futures relatives, maturity-normalized curve, true expiry switches, matched OI changes per underlying turnover, and a near-ATM traded straddle premium. It enters separately from location in the derivatives risk model. The premium proxies priced risk. The endpoint forecast law represents realized returns. The four Upstox sector indices contribute **458** synchronized 15-bar sessions with newly derived midday participation, opening follow-through, financial rotation and a closing concentration proxy. Validated eligibility is shared by the corresponding parents. [NSE archives](https://www.nseindia.com/all-reports) · [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).

| horizon | cohort | model | baseline | metric | n | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | abs_return_error | 265 | 0.012377 | 0.012376 | -0.000001 | — | — |
| 5 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | brier | 265 | 0.280117 | 0.279870 | -0.000247 | -0.003732 | 0.003237 |
| 5 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | crps | 265 | 0.013404 | 0.013372 | -0.000032 | -0.000118 | 0.000054 |
| 5 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | path_risk_abs_error | 265 | 0.044916 | 0.045492 | 0.000576 | — | — |
| 5 | combined | D_ETF | D_ETF_PARENT | abs_return_error | 265 | 0.012612 | 0.012376 | -0.000236 | — | — |
| 5 | combined | D_ETF | D_ETF_PARENT | brier | 265 | 0.281935 | 0.279870 | -0.002064 | -0.014140 | 0.010011 |
| 5 | combined | D_ETF | D_ETF_PARENT | crps | 265 | 0.013417 | 0.013372 | -0.000045 | -0.000500 | 0.000411 |
| 5 | combined | D_ETF | D_ETF_PARENT | path_risk_abs_error | 265 | 0.045574 | 0.045492 | -0.000083 | — | — |
| 5 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | abs_return_error | 265 | 0.012334 | 0.012376 | 0.000042 | — | — |
| 5 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | brier | 265 | 0.280133 | 0.279870 | -0.000263 | -0.002900 | 0.002374 |
| 5 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | crps | 265 | 0.013347 | 0.013372 | 0.000025 | -0.000034 | 0.000083 |
| 5 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | path_risk_abs_error | 265 | 0.045608 | 0.045492 | -0.000116 | — | — |
| 5 | combined | D_INTRA | D_INTRA_PARENT | abs_return_error | 263 | 0.012259 | 0.012532 | 0.000274 | — | — |
| 5 | combined | D_INTRA | D_INTRA_PARENT | brier | 263 | 0.279152 | 0.281868 | 0.002716 | -0.011869 | 0.017301 |
| 5 | combined | D_INTRA | D_INTRA_PARENT | crps | 263 | 0.013366 | 0.013543 | 0.000177 | -0.000199 | 0.000553 |
| 5 | combined | D_INTRA | D_INTRA_PARENT | path_risk_abs_error | 263 | 0.045792 | 0.045646 | -0.000146 | — | — |
| 5 | combined | D_INTRA_TIMING | D_INTRA_PARENT | abs_return_error | 263 | 0.012545 | 0.012532 | -0.000013 | — | — |
| 5 | combined | D_INTRA_TIMING | D_INTRA_PARENT | brier | 263 | 0.281434 | 0.281868 | 0.000434 | -0.008691 | 0.009558 |
| 5 | combined | D_INTRA_TIMING | D_INTRA_PARENT | crps | 263 | 0.013443 | 0.013543 | 0.000100 | -0.000224 | 0.000425 |
| 5 | combined | D_INTRA_TIMING | D_INTRA_PARENT | path_risk_abs_error | 263 | 0.045674 | 0.045646 | -0.000029 | — | — |
| 5 | combined | I_CAP_PARENT | B_ROT_EQ | abs_return_error | 265 | 0.010998 | 0.010880 | -0.000118 | — | — |
| 5 | combined | I_CAP_PARENT | B_ROT_EQ | brier | 265 | 0.250437 | 0.248343 | -0.002094 | -0.011950 | 0.007762 |
| 5 | combined | I_CAP_PARENT | B_ROT_EQ | crps | 265 | 0.012157 | 0.011951 | -0.000206 | -0.000634 | 0.000222 |
| 5 | combined | I_DIVERGE | I_CAP_PARENT | abs_return_error | 265 | 0.011015 | 0.010998 | -0.000016 | — | — |
| 5 | combined | I_DIVERGE | I_CAP_PARENT | brier | 265 | 0.253388 | 0.250437 | -0.002951 | -0.009247 | 0.003344 |
| 5 | combined | I_DIVERGE | I_CAP_PARENT | crps | 265 | 0.012193 | 0.012157 | -0.000037 | -0.000205 | 0.000132 |
| 5 | combined | I_EQ | I_CAP_PARENT | abs_return_error | 265 | 0.010706 | 0.010998 | 0.000292 | — | — |
| 5 | combined | I_EQ | I_CAP_PARENT | brier | 265 | 0.258895 | 0.250437 | -0.008459 | -0.034555 | 0.017638 |
| 5 | combined | I_EQ | I_CAP_PARENT | crps | 265 | 0.012120 | 0.012157 | 0.000037 | -0.000840 | 0.000913 |
| 5 | combined | I_RISK_EQ | I_RISK_PARENT | abs_return_error | 265 | 0.012157 | 0.012698 | 0.000541 | — | — |
| 5 | combined | I_RISK_EQ | I_RISK_PARENT | brier | 265 | 0.276624 | 0.278536 | 0.001912 | -0.019306 | 0.023130 |
| 5 | combined | I_RISK_EQ | I_RISK_PARENT | crps | 265 | 0.013242 | 0.013525 | 0.000283 | -0.001282 | 0.001849 |
| 5 | combined | I_RISK_EQ | I_RISK_PARENT | path_risk_abs_error | 265 | 0.045608 | 0.045365 | -0.000243 | — | — |
| 5 | combined | I_RISK_PARENT | D_EQ_SCALE | abs_return_error | 265 | 0.012698 | 0.012364 | -0.000334 | — | — |
| 5 | combined | I_RISK_PARENT | D_EQ_SCALE | brier | 265 | 0.278536 | 0.279833 | 0.001297 | -0.008341 | 0.010936 |
| 5 | combined | I_RISK_PARENT | D_EQ_SCALE | crps | 265 | 0.013525 | 0.013255 | -0.000270 | -0.000893 | 0.000352 |
| 5 | combined | I_RISK_PARENT | D_EQ_SCALE | path_risk_abs_error | 265 | 0.045365 | 0.045694 | 0.000329 | — | — |
| 21 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | abs_return_error | 217 | 0.040201 | 0.040461 | 0.000261 | — | — |
| 21 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | brier | 217 | 0.370972 | 0.370298 | -0.000674 | — | — |
| 21 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | crps | 217 | 0.040917 | 0.041092 | 0.000176 | — | — |
| 21 | combined | D_DERIV_RISK | D_DERIV_RISK_PARENT | path_risk_abs_error | 217 | 0.045559 | 0.045461 | -0.000098 | — | — |
| 21 | combined | D_ETF | D_ETF_PARENT | abs_return_error | 217 | 0.041809 | 0.040461 | -0.001347 | — | — |
| 21 | combined | D_ETF | D_ETF_PARENT | brier | 217 | 0.368318 | 0.370298 | 0.001980 | — | — |
| 21 | combined | D_ETF | D_ETF_PARENT | crps | 217 | 0.041810 | 0.041092 | -0.000718 | — | — |
| 21 | combined | D_ETF | D_ETF_PARENT | path_risk_abs_error | 217 | 0.045648 | 0.045461 | -0.000188 | — | — |
| 21 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | abs_return_error | 217 | 0.040598 | 0.040461 | -0.000137 | — | — |
| 21 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | brier | 217 | 0.370383 | 0.370298 | -0.000084 | — | — |
| 21 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | crps | 217 | 0.041159 | 0.041092 | -0.000066 | — | — |
| 21 | combined | D_GLOBAL_RISK | D_GLOBAL_RISK_PARENT | path_risk_abs_error | 217 | 0.045435 | 0.045461 | 0.000025 | — | — |
| 21 | combined | D_INTRA | D_INTRA_PARENT | abs_return_error | 217 | 0.040390 | 0.040434 | 0.000044 | — | — |
| 21 | combined | D_INTRA | D_INTRA_PARENT | brier | 217 | 0.368362 | 0.370727 | 0.002365 | — | — |
| 21 | combined | D_INTRA | D_INTRA_PARENT | crps | 217 | 0.040935 | 0.041128 | 0.000192 | — | — |
| 21 | combined | D_INTRA | D_INTRA_PARENT | path_risk_abs_error | 217 | 0.045280 | 0.045414 | 0.000135 | — | — |
| 21 | combined | D_INTRA_TIMING | D_INTRA_PARENT | abs_return_error | 217 | 0.040569 | 0.040434 | -0.000135 | — | — |
| 21 | combined | D_INTRA_TIMING | D_INTRA_PARENT | brier | 217 | 0.369007 | 0.370727 | 0.001720 | — | — |
| 21 | combined | D_INTRA_TIMING | D_INTRA_PARENT | crps | 217 | 0.041103 | 0.041128 | 0.000025 | — | — |
| 21 | combined | D_INTRA_TIMING | D_INTRA_PARENT | path_risk_abs_error | 217 | 0.045349 | 0.045414 | 0.000066 | — | — |
| 21 | combined | I_CAP_PARENT | B_ROT_EQ | abs_return_error | 217 | 0.029294 | 0.028925 | -0.000369 | — | — |
| 21 | combined | I_CAP_PARENT | B_ROT_EQ | brier | 217 | 0.360755 | 0.332754 | -0.028001 | — | — |
| 21 | combined | I_CAP_PARENT | B_ROT_EQ | crps | 217 | 0.033883 | 0.032570 | -0.001314 | — | — |
| 21 | combined | I_DIVERGE | I_CAP_PARENT | abs_return_error | 217 | 0.029328 | 0.029294 | -0.000034 | — | — |
| 21 | combined | I_DIVERGE | I_CAP_PARENT | brier | 217 | 0.366646 | 0.360755 | -0.005891 | — | — |
| 21 | combined | I_DIVERGE | I_CAP_PARENT | crps | 217 | 0.034144 | 0.033883 | -0.000260 | — | — |
| 21 | combined | I_EQ | I_CAP_PARENT | abs_return_error | 217 | 0.026551 | 0.029294 | 0.002743 | — | — |
| 21 | combined | I_EQ | I_CAP_PARENT | brier | 217 | 0.387050 | 0.360755 | -0.026294 | — | — |
| 21 | combined | I_EQ | I_CAP_PARENT | crps | 217 | 0.033222 | 0.033883 | 0.000661 | — | — |
| 21 | combined | I_RISK_EQ | I_RISK_PARENT | abs_return_error | 217 | 0.034033 | 0.040605 | 0.006572 | — | — |
| 21 | combined | I_RISK_EQ | I_RISK_PARENT | brier | 217 | 0.396368 | 0.378575 | -0.017794 | — | — |
| 21 | combined | I_RISK_EQ | I_RISK_PARENT | crps | 217 | 0.037850 | 0.041719 | 0.003869 | — | — |
| 21 | combined | I_RISK_EQ | I_RISK_PARENT | path_risk_abs_error | 217 | 0.044907 | 0.044974 | 0.000068 | — | — |
| 21 | combined | I_RISK_PARENT | D_EQ_SCALE | abs_return_error | 217 | 0.040605 | 0.040831 | 0.000226 | — | — |
| 21 | combined | I_RISK_PARENT | D_EQ_SCALE | brier | 217 | 0.378575 | 0.373376 | -0.005198 | — | — |
| 21 | combined | I_RISK_PARENT | D_EQ_SCALE | crps | 217 | 0.041719 | 0.041905 | 0.000186 | — | — |
| 21 | combined | I_RISK_PARENT | D_EQ_SCALE | path_risk_abs_error | 217 | 0.044974 | 0.046126 | 0.001151 | — | — |

The separate refresh reacquired **2,946** records through **2026-11-23**, with four post-freeze sessions and **0** completed dates beyond V10. The prior dated late-diagnostic issue still had pending endpoints on 25 November and 17 December. [Official NSE trading calendar](https://betanseapi.nseindia.com/resources/exchange-communication-holidays) · [Refresh receipts](refresh-summary.json) · [US source audit](global-breadth-audit.json) · [US alignment](international-availability.csv).
