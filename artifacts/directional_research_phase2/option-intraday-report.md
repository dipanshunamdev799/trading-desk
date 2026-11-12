# Recent intraday premium diagnostic

17 fixed EMA/Donchian/pullback signals from 2–6 November 2026 generated 68 predeclared contract-policy attempts; 62 had complete positive-volume entry/exit candle evidence.

The prior completed session's official NSE contract universe was used before the decision. Strike choice used the underlying candle close at the frozen signal, with next-five-minute option open entry and original fixed-time candle close exit. Current Upstox instrument keys were accepted only for exact dated token/expiry/strike/type matches. Missing expired mappings were rejected. Nearest expiry excludes same-day expiry; month-end expiry is a listed-calendar inference. ATM versus one listed strike ITM are disclosed in full, including duplicate contracts across policies.

**This is a tiny, historically inspected candle-price diagnostic, not executable option-profit validation.** Option opens can occur after the candle boundary, and no bid/ask or exact trade timestamps establish latency/fills. Future entry/exit volume is a retrospective coverage requirement, not a claim that those fills could be anticipated. Do not combine correlated policy rows as independent trades.

Both net scenarios deduct dated 0.15% sale STT. Additional allowances are 2 premium points + INR100 or 5 points + INR200 per round trip, covering other fees/execution illustratively; no fully reconstructed statutory cost claim.

|Family|Expiry|Strike|N|Sessions|Gross INR/lot|Illustrative net INR/lot|Severe net INR/lot|
|---|---|---|---:|---:|---:|---:|---:|
|donchian|month_end_proxy|ATM|5|5|1832.35|1567.63|1272.63|
|donchian|month_end_proxy|one_step_ITM|5|5|1925.30|1657.81|1362.81|
|donchian|nearest_nonexpiry_day|ATM|4|4|2494.38|2244.06|1949.06|
|donchian|nearest_nonexpiry_day|one_step_ITM|4|4|2670.69|2417.41|2122.41|
|ema_trend|month_end_proxy|ATM|7|5|1983.43|1718.00|1423.00|
|ema_trend|month_end_proxy|one_step_ITM|7|5|2052.14|1783.98|1488.98|
|ema_trend|nearest_nonexpiry_day|ATM|6|4|2677.46|2426.79|2131.79|
|ema_trend|nearest_nonexpiry_day|one_step_ITM|6|4|2895.75|2642.09|2347.09|
|pullback|month_end_proxy|ATM|5|5|2056.60|1791.46|1496.46|
|pullback|month_end_proxy|one_step_ITM|5|5|2193.75|1925.76|1630.76|
|pullback|nearest_nonexpiry_day|ATM|4|4|2861.62|2610.66|2315.66|
|pullback|nearest_nonexpiry_day|one_step_ITM|4|4|3085.88|2831.89|2536.89|

Coverage: {"observed_candle_proxy": 62, "expired_or_missing_exact_current_mapping": 6}

No confidence or profitability claim is made from this five-session window. Full selections, rejected rows, raw option candles and prior-day official source ZIPs are retained. [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/). [NSE dated STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).