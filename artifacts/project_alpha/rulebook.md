# Project Alpha deterministic research rulebook

Version: `project-alpha-research-1`. Decision: **RESEARCH ONLY**. Primary validated strategy: **none**. Operational output: **NO TRADE**. These rules specify reproducible research profiles; a trading skill is conditional on passing validation, as required by the brief.

## Before a session

Load the versioned configuration, exchange calendar/segment state and dated contracts/lots. Verify source time, receipt time, completed-bar coverage, account/order reconciliation and premium cash funding. Record previous official close/high/low and released event context. Unknown event coverage is not a positive event-clearance signal. Overnight positions are disabled. Unresolved positions, failed data, unknown order state, missing metadata or unpassed strategy gates prevent new entries.

## Exact price-state and setup definitions

Use complete five-minute OHLC bars in the 09:15–15:10 research window. Confirm each bar only at its close. Discard incomplete preceding research sessions for EMA/ATR context, while allowing a contiguous current-session prefix. Do not backdate pivots or higher-timeframe confirmations.

Prior ATR is the rolling mean of14 earlier true ranges. True range uses the prior close within each session; overnight gaps are separate context. EMA uses `adjust=False` with spans9,12,21,26. Efficiency is absolute12-bar net displacement divided by sum of the12 absolute changes, resetting at each session. Eligible trend requires efficiency>=0.35 and absolute(EMA9−EMA21)/priorATR>=0.5. These are imperfect causal states, not knowledge of the future day type.

Research profiles, with deterministic priority:

1. **EMA continuation:** buy-side candidate when (EMA12−EMA26)/priorATR>0.5; put-side candidate below−0.5.
2. **Donchian20:** candidate above the highest high of the preceding20 completed session bars, or below the preceding20-bar low. The current bar is excluded from the boundary.
3. **Pullback:** for a call candidate, EMA9>EMA21, low<=EMA9+0.75ATR, close>EMA9 and close>open. For a put candidate, EMA9<EMA21, high>=EMA9−0.75ATR, close<EMA9 and close<open.

An entry confirmation must occur from13:05 through14:10 IST. The diagnostic engine cancels a missed decision after two seconds; an actual60-minute hold cannot extend past15:10. One directional position is allowed at a time. Conflicting simultaneous setups use the fixed EMA→Donchian→pullback priority, never retrospective profit. An unresolved position prevents re-entry.

Fifteen-minute confirmation is a separate experiment: three contiguous5mbars form a15mbar, and only already completed15mbars can contribute. EMA4/9 supplies its fixed direction. It is not silently added to the baseline profiles, because its incremental value was not established.

## Contract and entry

Use the exact dated available universe. CE corresponds to+1 direction, PE to−1. Nearest research expiry is strictly after the session; expiry-day trades are excluded from that profile. Baseline strike is nearest ATM, tie toward lower strike. ITM, OTM, month-end proxy and absolute-delta bands are separately named experiments. Current instrument masters cannot silently substitute for expired historical identities.

Require positive uncrossed bid/ask, at least one whole dated lot of best displayed depth on both sides and `(ask−bid)/mid <= 0.02`. A valid decision quote is at most two seconds old. Research snapshot orders use a marketable limit at the predecision ask plus0.5%, rounded upward to the0.05tick. Execution is a simulation using the first qualifying observed ask after250/1000ms latency within2/5seconds. Partial quantity, missed orders and remaining exposure must be recorded.

Recorded stream chronology uses actual local receipt time. Source frame and local clocks differ; snapshot experiments explicitly allow a fixed±1second offset and require provider-frame minus provider-LTT age0–30seconds. A provider frame timestamp is not a verified exchange-book event time. The stricter verified-book mode has no supported historical executions. Neither mode is evidence of actual broker fills.

## Exits and handling uncertainty

The baseline holds60minutes and squares off by15:10. A scheduled snapshot exit is dispatched latency+maximum-quote-wait seconds before its deadline; actual holding duration is recorded. Entry/exit uses ask/bid once, not an additional duplicated spread charge.

The research alternatives are explicitly enumerated in exit-preregister.json:30/60/120minute time exits,20%/30% premium stops,1/1.5ATR underlying invalidation, fixed reward targets and trailing variants. No variant is chosen as best from five sessions.

Premium stops trigger on observed bid, then use a later available exit after latency. Underlying invalidation requires a completed underlying bar and the next eligible option observation. A gap may exit below the stop. Candle studies report adverse-first/favourable-first path bounds when a stop and target could both occur; they do not invent an intrabar path. Observed/candle MAE/MFE are labeled bounds.

Missing prices never produce a zero-loss close. A position with no eligible exit remains unresolved with capital exposure preserved. Freeze entries, reconcile state, and require an operator decision if an actual position ever exists. A historical simulator cannot prove a future emergency order will fill.

## Capital hypotheses

Test capital₹100k/250k/500k/1m and planned per-trade risk0.25%/0.5%. Position size is the minimum of whole lots funded by cash and lots supported by the trade budget plus remaining daily/weekly headroom. Planned loss includes the specified stop and severe execution reserve; without a defined premium loss reserve, use full premium at risk. No averaging down, martingale or size increase after a loss.

Daily realized-loss gate is1% of initial allocated capital; weekly is3%. Before a new position, remaining planned-loss room also limits size. Price gaps and failed exits can still exceed these limits. The full-premium-loss scenario is reported separately. Capital protection has not been optimized or validated as sufficient for any individual's finances.

## Emergency behavior

Return NO TRADE for missing/stale data, unknown phase, failed acceptance, excessive spread, insufficient depth, invalid contract/lot, unvalidated state, exhausted loss budget, repeated rejection, unexpected positions or order-state uncertainty. Log exact causes. Distinguish quote rejections in research from real broker order failures; the latter frequency is not measurable without actual execution records.

The diagnostic implementation calls read-only market-data methods and sends no orders. Because no strategy passed acceptance, it leaves contract/entry/stop/size fields unapproved and reports zero lots. A detected historical pattern does not override that gate.

## After a session

Retain every setup, rejection, available feature vintage, contract decision, quote/depth snapshot, simulated/actual execution class, latency, fee assumption and exit event. Compare actual later costs with the registered assumptions. Track omitted sessions, losses, drawdown, unresolved exposure and rule deviations. No parameter changes follow individual wins or losses. Experimental, historical, prospective observational, paper and live records must stay separate.
