# NIFTY V8 · Global Conditional Signals

Run `2026-11-24/run-001`. Retrospective research.

V8 acquired actual NASDAQ Composite close observations and constant-maturity US ten-year Treasury yields, rather than relying on the earlier technology CFD proxy for the direct hypothesis. FRED also provided the CBOE VIX close series. The acquisition captured 471 Nasdaq, 469 yield and 485 VIX observations in the allowed data window. All new foreign completion times were reconstructed conservatively with two US business days plus a 23:00 New York time buffer. The stored archive receipt times do not establish the original historical provider receipt timestamps. Inherited dated Upstox FX, oil and Asian cash-market features retain their configured conservative as-of rules. [Nasdaq via FRED](https://fred.stlouisfed.org/series/NASDAQCOM) · [Federal Reserve H.15 yields](https://fred.stlouisfed.org/series/DGS10) · [CBOE VIX via FRED](https://fred.stlouisfed.org/series/VIXCLS)

The intermediate designs test Nasdaq to Indian IT relative returns, global VIX to sector synchronization, Brent/USDINR to defensive-cyclical returns, US yields to Indian Financial Services relative returns, and Asian dispersion to future Indian participation. Each intermediate compares own-state Ridge against the same own-state inputs plus the specified foreign information. The downstream tests use maturity-matched own-state, direct fields, prequential corrections and corrections interacted with weak participation. Each prequential correction uses a refit before its own origin.

| horizon | target | method | n | MAE |
| --- | --- | --- | --- | --- |
| 5 | asia | foreign | 92 | 0.273174 |
| 5 | asia | own | 92 | 0.268163 |
| 5 | oil_currency | foreign | 92 | 0.012785 |
| 5 | oil_currency | own | 92 | 0.012764 |
| 5 | rates | foreign | 92 | 0.008748 |
| 5 | rates | own | 92 | 0.008735 |
| 5 | technology | foreign | 92 | 0.030636 |
| 5 | technology | own | 92 | 0.030448 |
| 5 | volatility | foreign | 92 | 0.077096 |
| 5 | volatility | own | 92 | 0.076798 |
| 21 | asia | foreign | 76 | 0.296520 |
| 21 | asia | own | 76 | 0.291274 |
| 21 | oil_currency | foreign | 76 | 0.036253 |
| 21 | oil_currency | own | 76 | 0.034741 |
| 21 | rates | foreign | 76 | 0.012558 |
| 21 | rates | own | 76 | 0.012171 |
| 21 | technology | foreign | 76 | 0.075308 |
| 21 | technology | own | 76 | 0.074579 |
| 21 | volatility | foreign | 76 | 0.143200 |
| 21 | volatility | own | 76 | 0.140151 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_MATCH5 | 92 | 19 | 0.597826 | 0.637397 | 0.227906 | 0.645716 | 0.011291 | 0.015039 | 0.020779 | 0.005710 | 0.510870 | 0.771739 | 0.042352 |
| G_DIRECT5 | 92 | 19 | 0.543478 | 0.576681 | 0.242160 | 0.676335 | 0.011658 | 0.015419 | 0.021162 | 0.005848 | 0.543478 | 0.739130 | 0.045950 |
| G_MEDIATE5 | 92 | 19 | 0.652174 | 0.684567 | 0.223419 | 0.638023 | 0.011382 | 0.015243 | 0.020870 | 0.005720 | 0.543478 | 0.771739 | 0.041457 |
| G_CONDITIONAL5 | 92 | 19 | 0.641304 | 0.675133 | 0.229502 | 0.650501 | 0.011476 | 0.015215 | 0.020985 | 0.005770 | 0.554348 | 0.760870 | 0.041144 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_MATCH21 | 53 | 3 | 0.188679 | 0.384615 | 0.517739 | 1.329286 | 0.050292 | 0.067391 | 0.070398 | 0.024165 | 0.018868 | 0.245283 | 0.098205 |
| G_DIRECT21 | 53 | 3 | 0.188679 | 0.384615 | 0.523048 | 1.342512 | 0.050272 | 0.067028 | 0.070416 | 0.024214 | 0.037736 | 0.188679 | 0.097009 |
| G_MEDIATE21 | 53 | 3 | 0.169811 | 0.346154 | 0.512133 | 1.308988 | 0.049500 | 0.066018 | 0.069946 | 0.023892 | 0.018868 | 0.207547 | 0.094388 |
| G_CONDITIONAL21 | 53 | 3 | 0.188679 | 0.384615 | 0.508465 | 1.299151 | 0.049503 | 0.065754 | 0.069937 | 0.023962 | 0.018868 | 0.188679 | 0.093493 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| G_CONDITIONAL5 | G_MEDIATE5 | brier | 92 | -0.006083 |
| G_CONDITIONAL5 | G_MEDIATE5 | crps | 92 | -0.000095 |
| G_DIRECT5 | G_MATCH5 | brier | 92 | -0.014254 |
| G_DIRECT5 | G_MATCH5 | crps | 92 | -0.000367 |
| G_MATCH5 | B_ROT | brier | 92 | -0.065612 |
| G_MATCH5 | B_ROT | crps | 92 | -0.001394 |
| G_MEDIATE5 | G_MATCH5 | brier | 92 | 0.004487 |
| G_MEDIATE5 | G_MATCH5 | crps | 92 | -0.000091 |


All five overall intermediate MAEs weaken at both horizons. Weekly mediated Brier improves a little versus its short-history counterpart while CRPS worsens, and both remain materially behind full-history domestic rotation. Four July monthly downstream fits were unestimated under the inner maturity requirement. The monthly 53-origin group must be read on its own matched dates. Conditional effects on high risk and weak breadth are preserved below and in the auxiliary per-origin files, with too few independent regime windows for causal transmission conclusions.

| model | condition | value | n | disjoint | brier_gain | CRPS_gain | leave_month_gain_min | leave_month_gain_max | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G_CONDITIONAL5 | market_breadth | False | 52 | 14 | -0.010417 | -0.000110 | -0.015014 | 0.000319 | 0.769231 |
| G_CONDITIONAL5 | market_breadth | True | 40 | 12 | -0.000450 | -0.000075 | -0.004242 | 0.001352 | 0.750000 |
| G_CONDITIONAL5 | global_strength | False | 49 | 14 | -0.009225 | -0.000054 | -0.011802 | -0.001453 | 0.795918 |
| G_CONDITIONAL5 | global_strength | True | 43 | 14 | -0.002502 | -0.000142 | -0.006577 | 0.001205 | 0.720930 |
| G_CONDITIONAL5 | historical_volatility_regime | high_vol | 52 | 11 | 0.000450 | 0.000013 | -0.001449 | 0.001911 | 0.769231 |
| G_CONDITIONAL5 | historical_volatility_regime | low_vol | 40 | 8 | -0.014576 | -0.000235 | -0.025599 | -0.001624 | 0.750000 |
| G_MEDIATE5 | market_breadth | False | 52 | 14 | 0.005063 | 0.000050 | 0.001366 | 0.009134 | 0.788462 |
| G_MEDIATE5 | market_breadth | True | 40 | 12 | 0.003738 | -0.000274 | -0.002053 | 0.017052 | 0.750000 |
| G_MEDIATE5 | global_strength | False | 49 | 14 | 0.005435 | -0.000156 | 0.003913 | 0.006666 | 0.816327 |
| G_MEDIATE5 | global_strength | True | 43 | 14 | 0.003406 | -0.000017 | 0.002191 | 0.007801 | 0.720930 |
| G_MEDIATE5 | historical_volatility_regime | high_vol | 52 | 11 | 0.005031 | -0.000245 | 0.002103 | 0.011559 | 0.769231 |
| G_MEDIATE5 | historical_volatility_regime | low_vol | 40 | 8 | 0.003780 | 0.000109 | -0.002409 | 0.006685 | 0.775000 |

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
