# Project Alpha: event engine and exit research

The engine adds deterministic entry/exit events, conservative stop translation, unknown-price states and single-position routing. All48 predefined exit/contract configurations and both intrabar path bounds are disclosed. No configuration was selected using these results.

The actual option sample contains only17 underlying signals across five already-inspected sessions, repeated across contract and exit policies. The test is a descriptive engineering/exit sensitivity panel, not an independent strategy discovery or an execution-quality backtest.

## Rules and execution boundaries
- Entry is the exact next option candle open for the frozen underlying signal. The option first-trade time within that candle is unknown.
- A single router prioritizes EMA, Donchian, then pullback. It holds at most one position per tested configuration; same-time lower-priority signals and later overlapping signals are logged as rejections.
- Premium stops20/30%, fixed1R/2R targets, trailing20%, underlying1/1.5ATR and prior-three-bar structure invalidation, and30/60/120-minute exits are tested in a small fixed slate. All trades close by15:10;120-minute holds can be cut short.
- Premium gaps exit at the worse observed open. A stop price does not guarantee the loss. If stop and target occur in one candle, adverse-first and favorable-first outcomes bound the path assumption; neither is asserted executable.
- Trailing stops update only after the preceding candle close. Underlying threshold touches become known at bar close and translate into the following option open; the option exit can gap substantially.
- Missing/invalid/zero-volume bars after entry leave the position unresolved and reserve capacity until session cutoff. No stale or fabricated exit is added. Full-day/future candle volume is an ex-post evidence check, not an entry-time liquidity oracle.
- MAE/MFE use full exit-bar extrema and are labeled candle bounds. They may include movements after a modeled intrabar exit and cannot identify exact entry/exit efficiency.
- Both net scenarios include dated sale STT plus the same illustrative non-STT fee/execution allowances used in phase2:2premiumpoints+INR100 or5points+INR200. These are not actual historical bid/ask costs. [NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).

## All adverse-first results
|Expiry|Strike|Exit policy|N|Mean gross INR|Mean illustrative net INR|Mean severe net INR|Ambiguous trades|Unresolved|
|---|---|---|---:|---:|---:|---:|---:|---:|
|month_end_proxy|ATM|time30|7|1144.00|879.66|584.66|0|0|
|month_end_proxy|ATM|time60|7|2055.39|1789.69|1494.69|0|0|
|month_end_proxy|ATM|time120|5|2658.50|2392.75|2097.75|0|0|
|month_end_proxy|ATM|premium20|7|2055.39|1789.69|1494.69|0|0|
|month_end_proxy|ATM|premium30|7|2055.39|1789.69|1494.69|0|0|
|month_end_proxy|ATM|premium20_target1R|7|1319.96|1055.36|760.36|0|0|
|month_end_proxy|ATM|premium20_target2R|7|2055.39|1789.69|1494.69|0|0|
|month_end_proxy|ATM|premium30_target2R|7|2055.39|1789.69|1494.69|0|0|
|month_end_proxy|ATM|premium20_trail20|7|2055.39|1789.69|1494.69|0|0|
|month_end_proxy|ATM|underlying1ATR|7|1515.43|1250.54|955.54|0|0|
|month_end_proxy|ATM|underlying1.5ATR|7|1432.79|1168.02|873.02|0|0|
|month_end_proxy|ATM|underlying_prior3bar_structure|7|1386.36|1121.66|826.66|0|0|
|month_end_proxy|one_step_ITM|time30|7|1221.54|954.43|659.43|0|0|
|month_end_proxy|one_step_ITM|time60|7|2100.89|1832.47|1537.47|0|0|
|month_end_proxy|one_step_ITM|time120|5|2835.30|2566.60|2271.60|0|0|
|month_end_proxy|one_step_ITM|premium20|7|2100.89|1832.47|1537.47|0|0|
|month_end_proxy|one_step_ITM|premium30|7|2100.89|1832.47|1537.47|0|0|
|month_end_proxy|one_step_ITM|premium20_target1R|7|1444.30|1176.86|881.86|0|0|
|month_end_proxy|one_step_ITM|premium20_target2R|7|2100.89|1832.47|1537.47|0|0|
|month_end_proxy|one_step_ITM|premium30_target2R|7|2100.89|1832.47|1537.47|0|0|
|month_end_proxy|one_step_ITM|premium20_trail20|7|2100.89|1832.47|1537.47|0|0|
|month_end_proxy|one_step_ITM|underlying1ATR|7|1592.04|1324.37|1029.37|0|0|
|month_end_proxy|one_step_ITM|underlying1.5ATR|7|1476.43|1208.94|913.94|0|0|
|month_end_proxy|one_step_ITM|underlying_prior3bar_structure|7|1414.21|1146.82|851.82|0|0|
|nearest_nonexpiry_day|ATM|time30|6|1075.75|827.46|532.46|0|0|
|nearest_nonexpiry_day|ATM|time60|6|2596.21|2345.64|2050.64|0|0|
|nearest_nonexpiry_day|ATM|time120|4|4306.25|4053.39|3758.39|0|0|
|nearest_nonexpiry_day|ATM|premium20|6|2391.46|2141.19|1846.19|0|0|
|nearest_nonexpiry_day|ATM|premium30|6|2596.21|2345.64|2050.64|0|0|
|nearest_nonexpiry_day|ATM|premium20_target1R|7|1039.35|791.15|496.15|0|0|
|nearest_nonexpiry_day|ATM|premium20_target2R|6|1446.68|1197.83|902.83|0|0|
|nearest_nonexpiry_day|ATM|premium30_target2R|6|2295.69|2045.57|1750.57|0|0|
|nearest_nonexpiry_day|ATM|premium20_trail20|6|2123.01|1873.14|1578.14|0|0|
|nearest_nonexpiry_day|ATM|underlying1ATR|6|1948.92|1699.31|1404.31|0|0|
|nearest_nonexpiry_day|ATM|underlying1.5ATR|6|1796.17|1546.79|1251.79|0|0|
|nearest_nonexpiry_day|ATM|underlying_prior3bar_structure|6|1796.17|1546.79|1251.79|0|0|
|nearest_nonexpiry_day|one_step_ITM|time30|6|1223.62|972.44|677.44|0|0|
|nearest_nonexpiry_day|one_step_ITM|time60|6|2804.21|2550.66|2255.66|0|0|
|nearest_nonexpiry_day|one_step_ITM|time120|4|4617.44|4361.46|4066.46|0|0|
|nearest_nonexpiry_day|one_step_ITM|premium20|6|2568.04|2314.84|2019.84|0|0|
|nearest_nonexpiry_day|one_step_ITM|premium30|6|2804.21|2550.66|2255.66|0|0|
|nearest_nonexpiry_day|one_step_ITM|premium20_target1R|7|1235.84|984.65|689.65|0|0|
|nearest_nonexpiry_day|one_step_ITM|premium20_target2R|6|1707.77|1455.86|1160.86|0|0|
|nearest_nonexpiry_day|one_step_ITM|premium30_target2R|6|2706.82|2453.41|2158.41|0|0|
|nearest_nonexpiry_day|one_step_ITM|premium20_trail20|6|2595.77|2342.53|2047.53|0|0|
|nearest_nonexpiry_day|one_step_ITM|underlying1ATR|6|2077.29|1824.83|1529.83|0|0|
|nearest_nonexpiry_day|one_step_ITM|underlying1.5ATR|6|1924.00|1671.77|1376.77|0|0|
|nearest_nonexpiry_day|one_step_ITM|underlying_prior3bar_structure|6|1924.00|1671.77|1376.77|0|0|

The favorable-first ledger and paired path outcomes remain available for every configuration. Five sessions cannot support stop/target optimization, tail-risk estimation or a promotion gate. No exit is declared best, and differences are not adjusted for all prior strategy research.

## Quote mode and unsupported history
alpha_event_engine.quote_fill requires verified source-book and received timestamps, healthy market state, noncrossed depth, a marketable limit, whole-lot depth, latency and deadline checks. Missing fills remain missed; permitted partial fills report both filled and cancelled quantities, without assuming replenishment. quote_exit evaluates observed bid triggers, then applies latency to a later eligible book. A gap below a stop exits at the observed worse bid; no valid later quote leaves the position unresolved.

Fourteen synthetic regression fixtures test ambiguous paths, stop gaps, delayed underlying invalidation, causal trailing, unavailable bars, session truncation, latency/limits, depth/partial accounting, invalid/stale/future books, strict-versus-frame snapshot evidence, predecision limits, missing exit quotes and cutoff timing. Fixtures are not market trades. Actual captured historical quote/depth coverage is audited separately and replayed in exit-stream-report.md with explicit timestamp-quality limitations.

Verification: 2544 trade/source/portfolio assertions passed. The ledger contains every source-policy decision, including rejections and unsupported outcomes. exit-preregister.json freezes policy definitions and source hashes; exit-events.csv gives timestamped events; exit-trades.csv contains exact contract and price/cost evidence.