# NIFTY V8 · Etf Liquidity Intraday

Run `2026-11-24/run-001`. Retrospective research.

Turnover is close times traded ETF volume, normalized by its own lagged 21-session median. We test turnover, changes in abnormal volume, participation across five ETFs, NIFTYBEES versus its underlying return, ETF volatility and absolute-return-over-turnover price impact proxies. The interaction tests abnormal activity during strong normalized rotation. Lagged archive futures basis, OI changes and options concentrations provide a separate derivatives test. No native spot index volume is inferred.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038767 |
| T_DAY_ETF | 92 | 19 | 0.782609 | 0.791001 | 0.166525 | 0.515537 | 0.009974 | 0.013004 | 0.019415 | 0.005035 | 0.521739 | 0.804348 | 0.038902 |
| A_ETF_ACTIVITY | 92 | 19 | 0.793478 | 0.797049 | 0.165208 | 0.512929 | 0.009836 | 0.012852 | 0.019155 | 0.004978 | 0.554348 | 0.793478 | 0.038378 |
| A_ETF_EXPOSURE | 92 | 19 | 0.793478 | 0.793662 | 0.166258 | 0.514854 | 0.009869 | 0.012900 | 0.019217 | 0.005007 | 0.565217 | 0.815217 | 0.038259 |
| A_ETF_GATE | 92 | 19 | 0.793478 | 0.797049 | 0.166522 | 0.515674 | 0.009843 | 0.012879 | 0.019148 | 0.004978 | 0.554348 | 0.793478 | 0.038437 |
| A_INTRADAY_BASE | 91 | 19 | 0.802198 | 0.807845 | 0.164001 | 0.509284 | 0.009958 | 0.012990 | 0.019436 | 0.005018 | 0.538462 | 0.813187 | 0.038643 |
| A_INTRADAY | 91 | 19 | 0.769231 | 0.772095 | 0.169132 | 0.520965 | 0.010022 | 0.013053 | 0.019565 | 0.005056 | 0.483516 | 0.802198 | 0.039137 |
| A_INTRADAY_STRICT_BASE | 89 | 18 | 0.764045 | 0.766892 | 0.174906 | 0.533193 | 0.010390 | 0.013490 | 0.019871 | 0.005249 | 0.561798 | 0.786517 | 0.040077 |
| A_INTRADAY_STRICT | 89 | 18 | 0.775281 | 0.780405 | 0.177397 | 0.538421 | 0.010456 | 0.013536 | 0.020010 | 0.005290 | 0.550562 | 0.797753 | 0.040469 |
| A_POSITION | 92 | 19 | 0.793478 | 0.797049 | 0.167904 | 0.516713 | 0.010135 | 0.013063 | 0.019878 | 0.005116 | 0.500000 | 0.815217 | 0.038254 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| A_ETF_ACTIVITY | B_ROT | brier | 92 | -0.002914 |
| A_ETF_ACTIVITY | B_ROT | crps | 92 | 0.000061 |
| A_ETF_EXPOSURE | A_ETF_ACTIVITY | brier | 92 | -0.001051 |
| A_ETF_EXPOSURE | A_ETF_ACTIVITY | crps | 92 | -0.000034 |
| A_ETF_GATE | A_ETF_ACTIVITY | brier | 92 | -0.001314 |
| A_ETF_GATE | A_ETF_ACTIVITY | crps | 92 | -0.000007 |
| A_INTRADAY | A_INTRADAY_BASE | brier | 91 | -0.005131 |
| A_INTRADAY | A_INTRADAY_BASE | crps | 91 | -0.000063 |
| A_INTRADAY_BASE | B_ROT | brier | 91 | -0.000539 |
| A_INTRADAY_BASE | B_ROT | crps | 91 | 0.000005 |
| A_INTRADAY_STRICT | A_INTRADAY_STRICT_BASE | brier | 89 | -0.002491 |
| A_INTRADAY_STRICT | A_INTRADAY_STRICT_BASE | crps | 89 | -0.000066 |
| A_INTRADAY_STRICT_BASE | B_ROT | brier | 89 | -0.012079 |
| A_INTRADAY_STRICT_BASE | B_ROT | crps | 89 | -0.000420 |
| A_POSITION | B_ROT | brier | 92 | -0.005609 |
| A_POSITION | B_ROT | crps | 92 | -0.000238 |
| B_ROT | B_NATIVE | brier | 92 | 0.007509 |
| B_ROT | B_NATIVE | crps | 92 | 0.000171 |


The ETF activity increment improves CRPS slightly versus rotation but worsens Brier. Adding tracked-price exposures and activity interactions produces no decisive further gain. Leading results for intrinsic daily ETF state remain sensitive to the presence of the rotation parent. The new complete-session intraday reconstruction uses **6,976** archived 25-minute Upstox candles, with exact IST regular-session grids and OHLC checks. **396** aligned sessions pass, and **7** observed nonregular or invalid sessions are excluded. Opening and closing features span 50 minutes each given bar resolution. The last intraday close differs from the frozen daily underlying close by **7.15** points at the median and **85.70** points at the maximum. **49** sessions exceed 10 basis points. Late range share, conditional downside variation, realized volatility and reversal use the intraday path with the daily reference kept separately. The discrepancy could include closing index calculation conventions or provider differences. No replacement daily label is justified. Intraday loses on both scores on the 91-origin complete-session subset and the stricter 89-origin reconciliation subset. [Upstox historical candle documentation](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE archive reports](https://www.nseindia.com/all-reports)

| model | condition | value | n | disjoint | brier_gain | CRPS_gain | leave_month_gain_min | leave_month_gain_max | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_ETF_ACTIVITY | market_breadth | False | 52 | 14 | -0.009661 | -0.000095 | -0.012297 | -0.000197 | 0.807692 |
| A_ETF_ACTIVITY | market_breadth | True | 40 | 12 | 0.005859 | 0.000263 | 0.002813 | 0.010531 | 0.775000 |
| A_ETF_ACTIVITY | global_strength | False | 49 | 14 | -0.005199 | -0.000010 | -0.008992 | 0.005048 | 0.836735 |
| A_ETF_ACTIVITY | global_strength | True | 43 | 14 | -0.000310 | 0.000142 | -0.002839 | 0.003349 | 0.744186 |
| A_ETF_ACTIVITY | rotation_intensity | False | 52 | 14 | -0.006008 | -0.000065 | -0.014001 | 0.001896 | 0.884615 |
| A_ETF_ACTIVITY | rotation_intensity | True | 40 | 12 | 0.001110 | 0.000225 | -0.002943 | 0.004623 | 0.675000 |
| A_ETF_ACTIVITY | recent_large_index_move | False | 68 | 17 | -0.004664 | -0.000074 | -0.007708 | -0.001679 | 0.794118 |
| A_ETF_ACTIVITY | recent_large_index_move | True | 24 | 8 | 0.002045 | 0.000443 | -0.005437 | 0.015794 | 0.791667 |
| A_ETF_ACTIVITY | historical_volatility_regime | high_vol | 52 | 11 | 0.005726 | 0.000164 | 0.003472 | 0.008140 | 0.769231 |
| A_ETF_ACTIVITY | historical_volatility_regime | low_vol | 40 | 8 | -0.014145 | -0.000072 | -0.020905 | -0.004473 | 0.825000 |
| A_INTRADAY | market_breadth | False | 52 | 14 | -0.002275 | 0.000014 | -0.003469 | -0.000666 | 0.826923 |
| A_INTRADAY | market_breadth | True | 39 | 12 | -0.008939 | -0.000166 | -0.011990 | -0.007421 | 0.769231 |
| A_INTRADAY | global_strength | False | 48 | 14 | -0.002178 | -0.000002 | -0.003432 | -0.000409 | 0.833333 |
| A_INTRADAY | global_strength | True | 43 | 14 | -0.008427 | -0.000132 | -0.010077 | -0.006759 | 0.767442 |
| A_INTRADAY | rotation_intensity | False | 52 | 14 | -0.001644 | -0.000019 | -0.002897 | -0.000036 | 0.903846 |
| A_INTRADAY | rotation_intensity | True | 39 | 12 | -0.009780 | -0.000123 | -0.011117 | -0.008403 | 0.666667 |
| A_INTRADAY | recent_large_index_move | False | 68 | 17 | -0.003504 | -0.000017 | -0.005257 | -0.001897 | 0.808824 |
| A_INTRADAY | recent_large_index_move | True | 23 | 8 | -0.009942 | -0.000201 | -0.013943 | -0.003295 | 0.782609 |
| A_INTRADAY | historical_volatility_regime | high_vol | 51 | 11 | -0.005376 | -0.000043 | -0.006654 | -0.004120 | 0.764706 |
| A_INTRADAY | historical_volatility_regime | low_vol | 40 | 8 | -0.004819 | -0.000089 | -0.005226 | -0.003818 | 0.850000 |

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
