# Fixed longer-horizon and earlier-regime research

6677 daily observations from 2000-01-03 to 2026-11-08. Four previously selected daily parameter sets, five fixed horizons (1/3/5/10/20 sessions), three baselines:35 rules, no new selection.

Signals at completed daily close; entry next observed session open; fixed exit close; no overlapping positions within a rule. Trades spanning a period boundary are excluded. Returns are underlying index basis points per trade after10 illustrative bps round-trip friction, not option premium or account returns.

Older2000–2016 observations provide backward replication. They are not a forward holdout for rules selected from2017–2025. The10/20-session extensions are exploratory and do not make weekly/monthly options profitable by inference. A20-session position can require a different expiry and includes overnight exposure. Some earliest index history predates the relevant options market.

|Rule|Period|Hold|N|Net10bps|95% conditional interval|Excess versus matched long|
|---|---|---:|---:|---:|---|---:|
|ema_trend / 10_30_gap0 / long_only / h10|backward_2000_2016|10|264|58.73|-1.16 to 110.51|0.00|
|ema_trend / 10_30_gap0 / long_only / h10|historical_final_2025_2026|10|27|-19.24|-93.78 to 44.81|0.00|
|ema_trend / 10_30_gap0 / long_only / h20|backward_2000_2016|20|145|135.36|20.44 to 239.07|0.00|
|ema_trend / 10_30_gap0 / long_only / h20|historical_final_2025_2026|20|15|-51.57|-264.13 to 105.09|0.00|
|momentum / lookback20_atr0 / ema_aligned / h10|backward_2000_2016|10|347|32.74|-13.13 to 79.63|-9.78|
|momentum / lookback20_atr0 / ema_aligned / h10|historical_final_2025_2026|10|39|-61.89|-124.31 to -5.06|-89.22|
|momentum / lookback20_atr0 / ema_aligned / h20|backward_2000_2016|20|185|34.98|-74.79 to 142.42|-59.28|
|momentum / lookback20_atr0 / ema_aligned / h20|historical_final_2025_2026|20|21|-37.83|-121.59 to 42.07|-73.34|
|donchian / lookback10_buffer0.25 / long_only / h10|backward_2000_2016|10|150|34.14|-43.35 to 108.36|0.00|
|donchian / lookback10_buffer0.25 / long_only / h10|historical_final_2025_2026|10|16|-28.70|-101.23 to 49.23|0.00|
|donchian / lookback10_buffer0.25 / long_only / h20|backward_2000_2016|20|105|163.25|35.62 to 289.44|0.00|
|donchian / lookback10_buffer0.25 / long_only / h20|historical_final_2025_2026|20|13|-74.77|-258.97 to 88.60|0.00|
|rsi_reversion / rsi30 / none / h10|backward_2000_2016|10|123|-83.66|-169.58 to 1.16|-163.59|
|rsi_reversion / rsi30 / none / h10|historical_final_2025_2026|10|8|33.70|-122.05 to 239.26|157.25|
|rsi_reversion / rsi30 / none / h20|backward_2000_2016|20|87|-118.98|-268.58 to 32.04|-304.89|
|rsi_reversion / rsi30 / none / h20|historical_final_2025_2026|20|5|-9.66|-293.51 to 262.53|-23.39|
|always_long / h10|backward_2000_2016|10|398|42.56|-6.46 to 90.09|0.00|
|always_long / h10|historical_final_2025_2026|10|44|-5.27|-70.81 to 62.39|0.00|
|always_long / h20|backward_2000_2016|20|199|102.84|2.49 to 201.01|0.00|
|always_long / h20|historical_final_2025_2026|20|22|-18.84|-161.11 to 127.42|0.00|
|always_short / h10|backward_2000_2016|10|398|-62.56|-110.09 to -13.54|-105.13|
|always_short / h10|historical_final_2025_2026|10|44|-14.73|-82.39 to 50.81|-9.46|
|always_short / h20|backward_2000_2016|20|199|-122.84|-221.01 to -22.49|-225.68|
|always_short / h20|historical_final_2025_2026|20|22|-1.16|-147.42 to 141.11|17.67|
|momentum252 / h10|backward_2000_2016|10|398|25.04|-22.34 to 72.41|-17.52|
|momentum252 / h10|historical_final_2025_2026|10|44|-45.21|-121.77 to 25.63|-39.94|
|momentum252 / h20|backward_2000_2016|20|199|39.45|-64.17 to 137.52|-63.39|
|momentum252 / h20|historical_final_2025_2026|20|22|-69.99|-234.59 to 71.69|-51.15|

Four feature-prefix checks and 154236 price/holding/nonoverlap assertions passed. All105 rule-period results are in long-results.csv; the full ledger is in long-trades.csv. Intervals use3000 moving60-session blocks and are not adjusted for prior or present searches. Compare baselines and dependence on market drift before interpreting positive averages.