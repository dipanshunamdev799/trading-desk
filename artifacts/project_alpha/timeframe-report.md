# Fifteen-minute confirmation and regime diagnostics

This is a fixed confirmation ablation of three frozen5mstrategies, not a newly optimized15mstrategy. All history has already been inspected; no new final holdout is claimed.

|Rule|Period|Policy|Trades|Net2points|95% conditional interval|
|---|---|---|---:|---:|---|
|ema_trend|backward2022_2024|baseline|511|0.54|-4.01 to 5.02|
|ema_trend|backward2022_2024|confirm15m|511|0.54|-4.01 to 5.02|
|ema_trend|historical_final|baseline|69|7.07|-6.06 to 20.99|
|ema_trend|historical_final|confirm15m|69|7.07|-6.06 to 20.99|
|donchian|backward2022_2024|baseline|368|2.63|-3.08 to 8.37|
|donchian|backward2022_2024|confirm15m|360|2.50|-2.96 to 8.15|
|donchian|historical_final|baseline|42|6.83|-9.81 to 26.23|
|donchian|historical_final|confirm15m|41|7.98|-8.87 to 27.57|
|pullback|backward2022_2024|baseline|469|0.76|-3.87 to 5.61|
|pullback|backward2022_2024|confirm15m|467|0.86|-3.71 to 5.76|
|pullback|historical_final|baseline|61|5.42|-6.92 to 19.24|
|pullback|historical_final|confirm15m|61|5.42|-6.92 to 19.24|

Aggregation requires three complete contiguous5mbars per15mbar; only already closed15mbars enter the confirmation. Signals, price entry/exit and costs remain unchanged. Intervals use3000five-sessionblock samples and are not selection-adjusted.

Regime confusion compares a causal current efficiency/EMA classifier with subsequently realized60mprice-path efficiency. Future labels appear only in evaluation. Imperfect agreement demonstrates the uncertainty of state identification; it is not a causal proof of market-state truth. Confusion counts are exported without training a new classifier.

Time-of-day volatility is a descriptive profile of candle ranges/absolutechanges across regular research windows. It does not establish that options were cheap at those times.

3 completed-bar prefix checks passed. All exact trade joins, state confusion and clock profiles are retained.