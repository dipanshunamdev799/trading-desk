# V12 Complementary Market Information

Domestic location uses official breadth, slow breadth, financial and defensive rotation, cash momentum, sector dispersion and leadership concentration. Comparable uncertainty heads use observed trailing volatility, straddles, term/skew, price-curve tails and futures information. Additional tests hold the strong statistical location fixed while bringing in synchronized Upstox sector risk, ETF activity, global risk, or the dated futures curve. The international group uses V11’s earlier-date Nasdaq breadth, lagged global context, published U.S. volatility and yields, USD/INR, and Brent. Direct foreign observations carry an earlier source date and are checked against the archived 09:10 decision timestamp using the original conservative publication estimates. [FRED VIX](https://fred.stlouisfed.org/series/VIXCLS) · [FRED 10-year Treasury yield](https://fred.stlouisfed.org/series/DGS10) · [Nasdaq RSP close archive](https://www.nasdaq.com/market-activity/etf/rsp/historical).

| horizon | cohort | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | V12_DOM_LOCATION | V12_STAT | absolute_return_error | 265 | 53 | 0.010194 | 0.010347 | 0.000154 | -0.000071 | 0.000378 |
| 5 | combined | V12_DOM_LOCATION | V12_STAT | brier | 265 | 53 | 0.247461 | 0.244333 | -0.003128 | -0.018659 | 0.012404 |
| 5 | combined | V12_DOM_LOCATION | V12_STAT | crps | 265 | 53 | 0.010866 | 0.010777 | -0.000089 | -0.000639 | 0.000461 |
| 5 | combined | V12_ETF_SCALE | V12_IV_SCALE | absolute_return_error | 265 | 53 | 0.009704 | 0.009706 | 0.000002 | -0.000126 | 0.000129 |
| 5 | combined | V12_ETF_SCALE | V12_IV_SCALE | brier | 265 | 53 | 0.244586 | 0.244588 | 0.000002 | -0.001934 | 0.001938 |
| 5 | combined | V12_ETF_SCALE | V12_IV_SCALE | crps | 265 | 53 | 0.010752 | 0.010750 | -0.000001 | -0.000046 | 0.000044 |
| 5 | combined | V12_ETF_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.040642 | 0.040918 | 0.000276 | -0.001791 | 0.002342 |
| 5 | combined | V12_EVENT_IV | V12_EVENT_RV | absolute_return_error | 265 | 53 | 0.009727 | 0.009839 | 0.000113 | -0.000124 | 0.000350 |
| 5 | combined | V12_EVENT_IV | V12_EVENT_RV | brier | 265 | 53 | 0.243241 | 0.243484 | 0.000244 | -0.002053 | 0.002541 |
| 5 | combined | V12_EVENT_IV | V12_EVENT_RV | crps | 265 | 53 | 0.010742 | 0.010759 | 0.000017 | -0.000064 | 0.000099 |
| 5 | combined | V12_EVENT_IV | V12_EVENT_RV | path_volatility_mae | 265 | 53 | 0.040857 | 0.042653 | 0.001796 | -0.001467 | 0.005059 |
| 5 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | absolute_return_error | 265 | 53 | 0.009692 | 0.009706 | 0.000014 | -0.000153 | 0.000181 |
| 5 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | brier | 265 | 53 | 0.245662 | 0.244588 | -0.001074 | -0.003800 | 0.001653 |
| 5 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | crps | 265 | 53 | 0.010782 | 0.010750 | -0.000032 | -0.000118 | 0.000055 |
| 5 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.041031 | 0.040918 | -0.000113 | -0.001266 | 0.001039 |
| 5 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | absolute_return_error | 265 | 53 | 0.009735 | 0.009706 | -0.000029 | -0.000237 | 0.000180 |
| 5 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | brier | 265 | 53 | 0.245716 | 0.244588 | -0.001129 | -0.003764 | 0.001507 |
| 5 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | crps | 265 | 53 | 0.010788 | 0.010750 | -0.000037 | -0.000113 | 0.000039 |
| 5 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.040877 | 0.040918 | 0.000041 | -0.002654 | 0.002737 |
| 5 | combined | V12_INTRA_SCALE | V12_IV_SCALE | absolute_return_error | 263 | 53 | 0.009709 | 0.009747 | 0.000038 | -0.000154 | 0.000229 |
| 5 | combined | V12_INTRA_SCALE | V12_IV_SCALE | brier | 263 | 53 | 0.244210 | 0.244655 | 0.000445 | -0.002161 | 0.003051 |
| 5 | combined | V12_INTRA_SCALE | V12_IV_SCALE | crps | 263 | 53 | 0.010767 | 0.010788 | 0.000021 | -0.000048 | 0.000091 |
| 5 | combined | V12_INTRA_SCALE | V12_IV_SCALE | path_volatility_mae | 263 | 53 | 0.040569 | 0.041008 | 0.000439 | -0.001161 | 0.002039 |
| 5 | combined | V12_IV_SCALE | V12_IV_LEVEL | absolute_return_error | 265 | 53 | 0.009706 | 0.009828 | 0.000122 | -0.000144 | 0.000388 |
| 5 | combined | V12_IV_SCALE | V12_IV_LEVEL | brier | 265 | 53 | 0.244588 | 0.243690 | -0.000898 | -0.004287 | 0.002491 |
| 5 | combined | V12_IV_SCALE | V12_IV_LEVEL | crps | 265 | 53 | 0.010750 | 0.010750 | -0.000000 | -0.000125 | 0.000124 |
| 5 | combined | V12_IV_SCALE | V12_IV_LEVEL | path_volatility_mae | 265 | 53 | 0.040918 | 0.041503 | 0.000585 | -0.001953 | 0.003123 |
| 5 | combined | V12_JOINT_IV | V12_DOM_IV | absolute_return_error | 265 | 53 | 0.009639 | 0.009584 | -0.000055 | -0.000266 | 0.000155 |
| 5 | combined | V12_JOINT_IV | V12_DOM_IV | brier | 265 | 53 | 0.245999 | 0.246194 | 0.000195 | -0.008281 | 0.008672 |
| 5 | combined | V12_JOINT_IV | V12_DOM_IV | crps | 265 | 53 | 0.010816 | 0.010812 | -0.000004 | -0.000205 | 0.000197 |
| 5 | combined | V12_JOINT_IV | V12_DOM_IV | path_volatility_mae | 265 | 53 | 0.041537 | 0.040918 | -0.000619 | -0.002124 | 0.000887 |
| 5 | combined | V12_JOINT_LOCATION | V12_FUTURES_LOCATION | absolute_return_error | 265 | 53 | 0.010181 | 0.010169 | -0.000012 | -0.000239 | 0.000216 |
| 5 | combined | V12_JOINT_LOCATION | V12_FUTURES_LOCATION | brier | 265 | 53 | 0.253923 | 0.246368 | -0.007555 | -0.035317 | 0.020207 |
| 5 | combined | V12_JOINT_LOCATION | V12_FUTURES_LOCATION | crps | 265 | 53 | 0.011107 | 0.010828 | -0.000279 | -0.001166 | 0.000608 |
| 5 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | absolute_return_error | 265 | 53 | 0.009676 | 0.009706 | 0.000030 | -0.000047 | 0.000107 |
| 5 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | brier | 265 | 53 | 0.244627 | 0.244588 | -0.000039 | -0.001194 | 0.001115 |
| 5 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | crps | 265 | 53 | 0.010752 | 0.010750 | -0.000002 | -0.000041 | 0.000038 |
| 5 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | path_volatility_mae | 265 | 53 | 0.041104 | 0.040918 | -0.000186 | -0.001005 | 0.000632 |
| 21 | combined | V12_DOM_LOCATION | V12_STAT | absolute_return_error | 217 | 11 | 0.025694 | 0.025920 | 0.000226 | — | — |
| 21 | combined | V12_DOM_LOCATION | V12_STAT | brier | 217 | 11 | 0.307317 | 0.306090 | -0.001227 | — | — |
| 21 | combined | V12_DOM_LOCATION | V12_STAT | crps | 217 | 11 | 0.028655 | 0.028994 | 0.000339 | — | — |
| 21 | combined | V12_ETF_SCALE | V12_IV_SCALE | absolute_return_error | 217 | 11 | 0.024678 | 0.024523 | -0.000155 | — | — |
| 21 | combined | V12_ETF_SCALE | V12_IV_SCALE | brier | 217 | 11 | 0.318872 | 0.317103 | -0.001769 | — | — |
| 21 | combined | V12_ETF_SCALE | V12_IV_SCALE | crps | 217 | 11 | 0.029225 | 0.029135 | -0.000089 | — | — |
| 21 | combined | V12_ETF_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.039290 | 0.040178 | 0.000888 | — | — |
| 21 | combined | V12_EVENT_IV | V12_EVENT_RV | absolute_return_error | 217 | 11 | 0.024349 | 0.024421 | 0.000072 | — | — |
| 21 | combined | V12_EVENT_IV | V12_EVENT_RV | brier | 217 | 11 | 0.316777 | 0.318458 | 0.001680 | — | — |
| 21 | combined | V12_EVENT_IV | V12_EVENT_RV | crps | 217 | 11 | 0.029082 | 0.029098 | 0.000016 | — | — |
| 21 | combined | V12_EVENT_IV | V12_EVENT_RV | path_volatility_mae | 217 | 11 | 0.040848 | 0.041165 | 0.000317 | — | — |
| 21 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | absolute_return_error | 217 | 11 | 0.024591 | 0.024523 | -0.000068 | — | — |
| 21 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | brier | 217 | 11 | 0.318401 | 0.317103 | -0.001298 | — | — |
| 21 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | crps | 217 | 11 | 0.029195 | 0.029135 | -0.000059 | — | — |
| 21 | combined | V12_FUTURES_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.041006 | 0.040178 | -0.000828 | — | — |
| 21 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | absolute_return_error | 217 | 11 | 0.024647 | 0.024523 | -0.000124 | — | — |
| 21 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | brier | 217 | 11 | 0.317953 | 0.317103 | -0.000849 | — | — |
| 21 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | crps | 217 | 11 | 0.029222 | 0.029135 | -0.000087 | — | — |
| 21 | combined | V12_GLOBAL_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.041936 | 0.040178 | -0.001758 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_IV_SCALE | absolute_return_error | 217 | 11 | 0.024625 | 0.024523 | -0.000102 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_IV_SCALE | brier | 217 | 11 | 0.315239 | 0.317103 | 0.001864 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_IV_SCALE | crps | 217 | 11 | 0.029117 | 0.029135 | 0.000019 | — | — |
| 21 | combined | V12_INTRA_SCALE | V12_IV_SCALE | path_volatility_mae | 217 | 11 | 0.039122 | 0.040178 | 0.001056 | — | — |
| 21 | combined | V12_IV_SCALE | V12_IV_LEVEL | absolute_return_error | 217 | 11 | 0.024523 | 0.024556 | 0.000033 | — | — |
| 21 | combined | V12_IV_SCALE | V12_IV_LEVEL | brier | 217 | 11 | 0.317103 | 0.316874 | -0.000230 | — | — |
| 21 | combined | V12_IV_SCALE | V12_IV_LEVEL | crps | 217 | 11 | 0.029135 | 0.029136 | 0.000001 | — | — |
| 21 | combined | V12_IV_SCALE | V12_IV_LEVEL | path_volatility_mae | 217 | 11 | 0.040178 | 0.039995 | -0.000182 | — | — |
| 21 | combined | V12_JOINT_IV | V12_DOM_IV | absolute_return_error | 217 | 11 | 0.024324 | 0.023986 | -0.000338 | — | — |
| 21 | combined | V12_JOINT_IV | V12_DOM_IV | brier | 217 | 11 | 0.313047 | 0.309458 | -0.003589 | — | — |
| 21 | combined | V12_JOINT_IV | V12_DOM_IV | crps | 217 | 11 | 0.028792 | 0.028535 | -0.000257 | — | — |
| 21 | combined | V12_JOINT_IV | V12_DOM_IV | path_volatility_mae | 217 | 11 | 0.040399 | 0.040178 | -0.000221 | — | — |
| 21 | combined | V12_JOINT_LOCATION | V12_FUTURES_LOCATION | absolute_return_error | 217 | 11 | 0.025500 | 0.025776 | 0.000275 | — | — |
| 21 | combined | V12_JOINT_LOCATION | V12_FUTURES_LOCATION | brier | 217 | 11 | 0.306663 | 0.308120 | 0.001457 | — | — |
| 21 | combined | V12_JOINT_LOCATION | V12_FUTURES_LOCATION | crps | 217 | 11 | 0.028636 | 0.028714 | 0.000077 | — | — |
| 21 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | absolute_return_error | 199 | 11 | 0.024877 | 0.024888 | 0.000012 | — | — |
| 21 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | brier | 199 | 11 | 0.316795 | 0.316330 | -0.000465 | — | — |
| 21 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | crps | 199 | 11 | 0.029347 | 0.029320 | -0.000027 | — | — |
| 21 | combined | V12_SURFACE_TAIL_SCALE | V12_IV_SCALE | path_volatility_mae | 199 | 11 | 0.039929 | 0.040084 | 0.000155 | — | — |

## Matched comparison with prior V11 annualized risk heads

| horizon | model | baseline | n | market_mae | V11_mae | gain | low10 | high10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V12_INTRA_SCALE | D_DERIV_RISK | 263 | 0.040569 | 0.045121 | 0.004551 | -0.003032 | 0.012134 |
| 5 | V12_INTRA_SCALE | D_ROT_SCALE | 263 | 0.040569 | 0.045691 | 0.005122 | -0.002925 | 0.013169 |
| 5 | V12_INTRA_SCALE | I_RISK_EQ | 263 | 0.040569 | 0.045839 | 0.005270 | -0.001996 | 0.012535 |
| 5 | V12_IV_BRACKET | D_DERIV_RISK | 264 | 0.041010 | 0.044762 | 0.003752 | -0.002880 | 0.010384 |
| 5 | V12_IV_BRACKET | D_ROT_SCALE | 264 | 0.041010 | 0.045319 | 0.004309 | -0.002814 | 0.011432 |
| 5 | V12_IV_BRACKET | I_RISK_EQ | 264 | 0.041010 | 0.045420 | 0.004410 | -0.001857 | 0.010677 |
| 5 | V12_IV_SCALE | D_DERIV_RISK | 265 | 0.040918 | 0.044916 | 0.003998 | -0.002877 | 0.010873 |
| 5 | V12_IV_SCALE | D_ROT_SCALE | 265 | 0.040918 | 0.045492 | 0.004574 | -0.002792 | 0.011940 |
| 5 | V12_IV_SCALE | I_RISK_EQ | 265 | 0.040918 | 0.045608 | 0.004690 | -0.001835 | 0.011215 |
| 21 | V12_INTRA_SCALE | D_DERIV_RISK | 217 | 0.039122 | 0.045559 | 0.006437 | — | — |
| 21 | V12_INTRA_SCALE | D_ROT_SCALE | 217 | 0.039122 | 0.045461 | 0.006339 | — | — |
| 21 | V12_INTRA_SCALE | I_RISK_EQ | 217 | 0.039122 | 0.044907 | 0.005785 | — | — |
| 21 | V12_IV_BRACKET | D_DERIV_RISK | 217 | 0.039542 | 0.045559 | 0.006017 | — | — |
| 21 | V12_IV_BRACKET | D_ROT_SCALE | 217 | 0.039542 | 0.045461 | 0.005919 | — | — |
| 21 | V12_IV_BRACKET | I_RISK_EQ | 217 | 0.039542 | 0.044907 | 0.005365 | — | — |
| 21 | V12_IV_SCALE | D_DERIV_RISK | 217 | 0.040178 | 0.045559 | 0.005381 | — | — |
| 21 | V12_IV_SCALE | D_ROT_SCALE | 217 | 0.040178 | 0.045461 | 0.005283 | — | — |
| 21 | V12_IV_SCALE | I_RISK_EQ | 217 | 0.040178 | 0.044907 | 0.004729 | — | — |

Purpose-specific gains in path volatility or movement error should be read independently from direction and from a whole-law score. The authentic domestic and global weighting proxies do not identify individual stock contributions. [Timestamp audit](external-publication-alignment.csv) · [Training feature definitions](feature-receipts.json) · [Matched coverage](matched-comparisons.csv) · [All cross-version risk estimates](legacy-risk-comparisons.csv).
