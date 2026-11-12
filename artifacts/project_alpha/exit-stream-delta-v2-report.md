# Project Alpha: actual received book-snapshot replay

Source selection has 33 records, expanded to 33 explicit contract-policy opportunities. 51267 received book snapshots; 0 have a verified exchange-book event timestamp. 48 fixed contract/exit/latency/wait configurations and two quality modes are disclosed, with no selected winner.

**Strict exchange-book execution is unsupported.** The frame_snapshot mode replays actual historical bid/ask states observed at local receipt, not verified exchange-book events or actual broker fills. This is stronger price evidence than OHLC, but it is still a provisional execution proxy.

## Timing and model assumptions
- Received timestamps determine information availability and order chronology. Provider frame clocks lead local receipt in some records. A fixed±1second crossclock tolerance is an explicit research assumption, not calibrated clock synchronization.
- Last-trade age uses provider frame timestamp minus provider LTT (same clock), requiring0–30seconds. Receipt/source offset distribution is reported rather than silently corrected.
- Entry uses the most recent valid predecision ask, no older than2seconds, to set a0.5% marketablelimit, roundedup0.05. Execution uses the first qualifying ask after250/1000ms latency within2/5seconds, with2%maxspread and one full dated lot at best bid/ask.
- Stops20/30% and an optional20%stop/2Rtarget trigger on an observed bid, then apply the same latency and quote deadline. A gap can realize more than planned stop loss. No valid exit leaves the position unresolved; a loss is not replaced with zero.
- Scheduled time exit is dispatched(latency+waitbudget)seconds before the original fixed60-minute exit; actual holding time is reported. No fill is accepted after the fixed due time or15:10cutoff.
- One-position routing uses EMA>Donchian>pullback priority. Missing-chain signals remain rejected opportunities. No new entry is admitted while an earlier position is unresolved.
- Ask-to-bid P&L already includes observed spread. Base net adds dated saleSTT andINR100other-feeallowance. Severe net adds2premiumpointsimpact andINR200other-feeallowance. These are sensitivities, not fully verified historical charges.
- Observed bid MAE/MFE are lower bounds on full-path excursions between snapshots. Repeated frames do not establish liquidity replenishment, queue priority, fill probability or market impact.

## Frame-snapshot results:250ms latency /2second quote wait
|Contract policy|Exit|N|Sessions|Gross INR|Base net INR|Severe net INR|Unresolved|
|---|---|---:|---:|---:|---:|---:|---:|
|ATM|time60|3|3|582.83|466.26|236.26|0|
|ATM|premium20|3|3|582.83|466.26|236.26|0|
|ATM|premium30|3|3|582.83|466.26|236.26|0|
|ATM|premium20_target2R|3|3|582.83|466.26|236.26|0|
|abs_delta_0.4_0.6|time60|3|3|507.00|391.50|161.50|0|
|abs_delta_0.4_0.6|premium20|3|3|507.00|391.50|161.50|0|
|abs_delta_0.4_0.6|premium30|3|3|507.00|391.50|161.50|0|
|abs_delta_0.4_0.6|premium20_target2R|3|3|507.00|391.50|161.50|0|
|abs_delta_0.6_0.8|time60|3|3|645.67|518.47|288.47|0|
|abs_delta_0.6_0.8|premium20|3|3|645.67|518.47|288.47|0|
|abs_delta_0.6_0.8|premium30|3|3|645.67|518.47|288.47|0|
|abs_delta_0.6_0.8|premium20_target2R|3|3|645.67|518.47|288.47|0|

Allotherlatency/waitcombinationsandstrict-mode rejections are exported. The captured window is small, selected rules were already studied on overlapping dates, and missing-chain/quote coverage is nonrandom. Positive proxy means, if any, do not establish a repeatable or executable edge.

Clock offset distribution (source minus receipt seconds): {"min": -4.961864, "p01": -0.11529292000000002, "median": 0.104571, "p99": 0.21834659999999934, "max": 0.237016}

Verification: 592 price/timing/nonoverlap assertions passed. Full contracts, quoted prices, limits, rejection causes, unresolved capital risk and exact events are retained in exit-stream-delta-v2-trades.csv and exit-stream-delta-v2-events.csv. No actual orders were sent.

## Delta availability extension
This is a new exploratory availability experiment after the original stream outcomes were inspected. It uses latest actual provider Greeks received before the decision, within30seconds, and fixed absolute-delta bands0.4–0.6(target0.5) and0.6–0.8(target0.7). The original dated expiry/universe andATMcontrol remain unchanged. It is not an untouched holdout, and original zero-eligible-delta results remain preserved. IVmetadata has source-specific units/inherited timestamp limitations and is not used in this experiment. Detailed protocol provenance is in exit-stream-delta-v2-methodology.json.
