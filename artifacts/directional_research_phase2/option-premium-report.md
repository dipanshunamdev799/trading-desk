# Exact-contract daily premium study

Four frozen daily finalists supplied 1085 trades; 106 signal/entry/exit dates fit the retained NSE archive (13 October 2025–23 October 2026). Four expiry/strike buckets produce 424 attempts and 424 usable premium proxies, representing 374 distinct signal/contract outcomes within strategy (50 duplicate policy rows).

**These are actual historical option premiums, but daily first-trade opens and official closing values are asynchronous price proxies. They do not establish executable fills at the underlying signal times.** Missing bid/ask, trade-time, latency and statutory fee histories prevent a deployable profitability claim. The first option trade can occur after the underlying open; a closing value need not be a fill available at the intended exit instant.

Contract choice used the signal-day dated contract universe and signal-time underlying close, before loading entry premiums. Positive signal-day volume is known at selection; entry/exit full-day volumes are ex-post coverage checks, not filters available at entry. All424attempts currently pass those checks, so they exclude no additional outcomes. Require unchanged identity/lot. ATM tie breaks toward lower strike; ITM is one listed strike in the money. Expiry is strictly beyond the planned exit. “Nearest surviving” may be a weekly or monthly expiry; “month-end proxy” is the last listed expiry in its calendar month, inferred from the dated archive. When both policies pick the same contract, rows are duplicate policy comparisons, not independent trades.

Gross P&L uses the dated lot size. Both net scenarios deduct dated sale STT: 0.10% through 31 March 2026, 0.15% from 1 April 2026. Illustrative net additionally deducts 2 premium points plus INR100 per round trip; severe additionally deducts 5 points plus INR200. These extra amounts cover other fees/execution illustratively, not verified actual spreads or a complete statutory charge calculation. The dated STT protocol update occurred during source download, before any premium outcomes were viewed. [NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).

|Frozen family|Expiry bucket|Strike|N|Gross INR/lot|Illustrative net INR/lot|Severe net INR/lot|95% month-block interval, illustrative net|
|---|---|---|---:|---:|---:|---:|---|
|donchian|month_end_proxy|ATM|9|-3519.53|-3775.04|-4076.70|-8508.88, 541.02|
|donchian|month_end_proxy|one_step_ITM|9|-3662.53|-3920.30|-4221.97|-9377.33, 1201.95|
|donchian|nearest_surviving|ATM|9|-3652.50|-3899.51|-4201.17|-7720.37, -12.51|
|donchian|nearest_surviving|one_step_ITM|9|-4050.69|-4299.84|-4601.51|-8899.34, 305.01|
|ema_trend|month_end_proxy|ATM|28|-3397.81|-3658.30|-3964.02|-8314.99, -11.52|
|ema_trend|month_end_proxy|one_step_ITM|28|-3503.83|-3766.58|-4072.29|-8834.04, 103.16|
|ema_trend|nearest_surviving|ATM|28|-3494.75|-3746.21|-4051.92|-8604.63, 93.54|
|ema_trend|nearest_surviving|one_step_ITM|28|-3667.81|-3921.48|-4227.20|-8796.38, -53.32|
|momentum|month_end_proxy|ATM|42|-2925.01|-3184.12|-3485.55|-8762.41, 2334.36|
|momentum|month_end_proxy|one_step_ITM|42|-3089.75|-3350.94|-3652.37|-8967.11, 2239.91|
|momentum|nearest_surviving|ATM|42|-3733.33|-3984.20|-4285.63|-9742.95, 1507.70|
|momentum|nearest_surviving|one_step_ITM|42|-3256.88|-3509.74|-3811.17|-9667.20, 2609.80|
|rsi_reversion|month_end_proxy|ATM|27|367.33|106.58|-195.09|-1183.00, 1726.83|
|rsi_reversion|month_end_proxy|one_step_ITM|27|678.71|415.49|113.82|-1192.98, 2416.74|
|rsi_reversion|nearest_surviving|ATM|27|-147.81|-398.28|-699.95|-1859.17, 1570.75|
|rsi_reversion|nearest_surviving|one_step_ITM|27|279.36|26.39|-275.28|-1793.48, 2024.25|

## Coverage and limitations

{
  "premium_proxy_observed": 424
}

All outcomes are disclosed; no premium winner is selected or promoted. The daily finalist selection was already historical and the source window overlaps other inspected data. Confidence intervals resample calendar months and are conditional, not adjusted for parameter or contract search. Small numbers of months/trades yield unreliable precision. Price-based Greeks, IV attribution and option drawdown paths are unavailable from these EOD records. The planned exit date assumes the exchange calendar was known; archived announcement timestamps were not available.

Entry ZIPs and SHA256 hashes are preserved; exit closes, volumes and dated lots come from the already retained official NSE archive whose source hashes were preserved by the earlier study. Raw ZIP parsing rejects date mismatches. Fixed selection file, source manifest, full accepted/rejected ledger and summaries are in this directory.

[Official NSE daily reports](https://www.nseindia.com/all-reports-derivatives). This source provides daily reports, not historical intraday order-book quotes.