# Project Alpha: existing system and evidence audit

Audit date: 9 November 2026. This supplements the phase-one component audit and phase-two research. It distinguishes the user's account of a profitable trader from the independently recovered evidence. It does not establish that the trader was unprofitable.

## Principal finding

The repository contains a research desk and data collectors, not a recovered, fully specified version of the original trader's decision process. A trader can use this desk profitably through selection, contract choice, exits and discretion that are not encoded in the indicator displays. Many different trading rules are compatible with the same dashboard. Profitability by itself does not identify which rule was used.

The code, available Git history, research artifacts and database were inspected for an actual tradebook or original parameter record. The three available commits are dated 28/31 October 2026. No professional broker-fill journal, signed contract-note series or complete original strategy configuration was recovered. The database contains one simulated paper order/fill dated 23 October, one paper position, zero credit-spread trades and zero credit-spread orders. These are not an audited professional performance record. A bounded read-only FO historical-trade request for October 2026 returned HTTP401/`UDAPI1221`; that is an access failure, not evidence that no trades occurred. No account identifiers or token values are retained in this report.

The highest-information missing evidence for reverse engineering is the original trader's timestamped entries, exits, contract identities, quantities, actual costs and contemporaneous reasons, including days deliberately skipped. If recovered, divide that tradebook chronologically before using it to infer a compact candidate policy; preserve a later set for imitation and P&L evaluation. Do not repeatedly fit explanations to the entire tradebook.

## Important correction to the prior data audit

**Historical depth data exists for a short window.** The live-stream tables contain 22,535,186 persisted updates from 26–30 October 2026, including 15,771,359 FO rows across 704 subscribed instruments. Sample FO updates contain five book levels, IV, Greeks, OI, cumulative volume and last-trade timestamps. Earlier statements about unavailable historical bid/ask must therefore be qualified: broad multi-year quote history is unavailable, but this captured short window supports a real bid/ask replay attempt.

|Segment|Rows|Subscribed instrument keys|
|---|---:|---:|
|NSE equity|3,826,062|50|
|NSE FO|15,771,359|704|
|NSE index|2,937,765|12|

The full source-time range is 26 October 09:15:22.174 IST to 30 October 13:37:37.763 IST. Source receipt begins approximately183ms after the first frame; a latest sampled frame had roughly57ms receipt delay. Those examples are not a latency distribution. Capture coverage is not continuous across all days: 28 October starts09:38 and 30 October starts10:16 and ends13:37. Instrument-level coverage and freshness must be checked at every entry and exit.

There are also 2,037 archived NIFTY chain snapshots covering three expiries:27October,3November and9November. Snapshots are concentrated on different dates/expiries; this is not a complete historical chain universe for every day or expiry. See `stream-inventory.json` for segment counts, dated coverage, chain ranges and actual sanitized market-data samples.

The raw stream's `source_at` comes from WebSocket frame `currentTs`, and `received_at` is local receipt time. The book levels do not have an independent exchange-book-event timestamp. For historical decisions, enforce both source and receipt availability, reject future-dated or stale fields, preserve source-clock/receipt-clock diagnostics, and apply latency sensitivity. Do not treat a fresh frame timestamp as proof that every carried field changed then. Last-trade time is a separate field, not a depth timestamp. Initial-feed records and partial feed updates require explicit treatment. [Upstox V3 protocol](https://upstox.com/developer/api-documentation/v3/get-market-data-feed/).

## Architecture and reusable components

|Component|Recovered capability|Research/operational boundary|
|---|---|---|
|`upstox_analytics.py`|Historical/intraday candles, option contracts, chains, quotes, Greeks, expiry history and read-only account/trade endpoints|No place/modify/cancel broker-order implementation found; the sole POST is a margin calculation. An endpoint being present does not prove this token can access it|
|`upstox_ws_v3.py`, stream services/store|Protobuf feed, shared subscriptions, queues, durable raw updates, per-field live provenance and dated chains|Subscriptions/capture are conditional on the collector running and watched instruments; historical receipt coverage is finite|
|Market gateway/store/providers|Database-first reads, raw response archives, persistent candles, explicit fallbacks and data-presence metadata|Preserve provider identity and available time; a fallback is not proof of interchangeable price vintages|
|Price-action engine|47 explicit, causal OHLC detectors and delayed confirmation timestamps|“Liquidity sweep”, “order block” and similar terms are measurable price heuristics, not direct evidence of institutional flow|
|NIFTY research components|127-factor catalog, candle factors, context sources, revisions and capture metadata|64 factors have stored observations, mostly captured24October–1November; historical reporting labels are not contemporaneous availability|
|OI/PCR/max pain/IV/Greeks|Dated retained analytics plus short-window stream/chain histories|Separate volume PCR from OI PCR; OI change requires the same instrument/expiry universe and a valid earlier observation|
|Generic Paper page/service|Simulated orders, positions and accounting|Instant fills at supplied limits/daily marks, zero default fees and stale marks are not executable long-option evidence|
|Credit-spread engine|Exact contracts, lot/depth/freshness checks, adverse slippage, journal and failure handling|A useful operational scaffold for a different short-premium strategy; no demonstrated long-call/put edge follows|
|Backtest viewer|Normalizes disk JSON, plots metrics and trade results|Does not itself establish simulation correctness; the sample momentum file is sample data|
|IPO research|Separate data product|No demonstrated incremental NIFTY timing variable|

Existing paper and credit-spread routes simulate trades. The inspected application does not send live broker orders. Execution authorization and order-state reconciliation would be separate deployment work; having market-data access does not establish execution permissions.

## Available data and important missing data

The frozen research now includes1,196 complete09:15–15:10 five-minute research windows in2022–2026,6,677 daily observations in2000–2026,204 complete one-minute sessions in2026, VIX/ETF context in2025–2026, dated NSE EOD option records,93 downloaded entry archives, and a recent29-contract intraday option-candle diagnostic. Existing candle storage also contains15-minute/hourly/daily intervals. Fifteen-minute research bars can be rebuilt from three contiguous five-minute bars anchored09:15; incomplete end buckets must not be padded or used as complete higher-timeframe signals.

Data still missing for broad validation includes a multi-regime stream of timestamped option books, historical per-contract IV/Greeks at each intended entry, exact historical delivery/latency, comprehensive release-time vintages for macro inputs, and dated index constituents/weights for broad constituent tests. A currently available contract master cannot reconstruct instruments that expired before it was downloaded. Exact dated NSE identities are therefore preferable to mapping historical tokens through today's master.

The expired-instrument API returned Plus-required errors in prior tested access. Tapetide returned an API-not-in-plan notice with null data. Those are verified availability restrictions, not evidence about strategy expectancy. Historical NSE daily reports provide actual premiums and OI, but daily opens and closing values remain asynchronous execution proxies. Intraday candles also lack a guaranteed fill at their time boundary.

## Why prior approaches failed: distinguish the causes

|Observed problem|Evidence class|What can be concluded|
|Short47-concept/ML study did not clear multiple-testing/cost checks|Insufficient sample, correlated search and small directional effect|No reliable predictor established on that sample; it does not refute every discretionary use of those concepts|
|Original seven-session trendline/mitigation estimates weakened on longer samples|Transfer failure and initial selection uncertainty|The short successful estimates were not stable enough to promote|
|Frozen afternoon trends had weak2022–2024 averages and wide recent intervals|Regime instability and low signal-to-noise|The fixed rules lack robust incremental evidence over momentum|
|Removing five best recent winners reverses averages|Trade concentration stress|Payoff depends on a few tails; this is not evidence those winners were illegitimate. Exit rules that truncate them require especially careful testing|
|Longer daily option-family proxies mostly negative|Actual premium outcomes under declared proxy/cost assumptions|The tested daily expressions were weak; distinguish them from short intraday positions and executable quotes|
|Five-session recent intraday premium test positive|Small, historically inspected diagnostic|Data access/replay works; confidence and all-regime profitability remain unsupported|
|Latest revision joins, carried premiums and generic paper fills unsuitable for replay|Implementation/modeling hazards|These must be corrected or excluded before interpretation; a dashboard displaying them is not itself a strategy failure|
|Broad IV/PCR/macros capture histories absent|Data limitation|Do not label their predictive value rejected merely because a valid test cannot be built|
|Original trader's complete process absent|Identification limitation|Do not claim to have disproved the trader's profitability or replicated his strategy|

The one-year max-pain convergence study did not support an unconditional expiry magnet. Directional accuracy, a target touch and profitable premium execution are different outcomes. The current studies also repeatedly inspect related historical periods. No existing final period should be described as a genuinely untouched prospective test.

## Verified market-structure changes that affect reproducibility

NSE's October2024 circular revised new NIFTY contract lots from25 to75 for contracts introduced from20November2024. The October2025 circular subsequently revised75 to65 with explicit expiry-dependent transition rules; existing weekly/monthly lots remained75 through December2025 expiries. Read the lot in each dated contract instead of assigning today's65 to all history. [2024 lot revision](https://nsearchives.nseindia.com/content/circulars/FAOP64625.pdf), [2025 lot revision](https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf).

The June2025 expiry circular retains existing expiries through August2025 and introduces Tuesday expiries for dates from September2025, with separate changes to long-dated contracts. Calendar reconstruction must follow that transition and holiday adjustments. [NSE expiry revision](https://nsearchives.nseindia.com/content/circulars/FAOP68747.pdf).

CAS went live3August2026. The current official CAS page distinguishes CAS-eligible cash stocks, non-CAS stocks and derivatives; derivatives are listed09:15–15:40. The studies'15:10 exit is a conservative research cutoff, not a statement of official closing time. The previously investigated15:28–15:29 spot-index jump was supported by the official daily close and CAS rules; it should not be silently deleted as a bad candle. [CAS implementation](https://nsearchives.nseindia.com/content/circulars/CMTR75479.pdf), [operating schedule](https://www.nseindia.com/static/products-services/closing-auction-session).

For current fees, distinguish exchange transaction charges and IPFT allocation. From1March2026, NSE option charges are₹3,552.99 per crore of premium per side plus₹0.01 IPFT, a combined₹3,553. Previously₹3,503+₹50 had the same combined outflow. Applying the revised combined number and also charging the old IPFT would double-count part of costs. Brokerage depends on the account plan; the standard published rate card is not a recovered historical client tariff. [NSE fee circular](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf).

## Priorities ranked by expected information value

1. Replay the short persisted five-level book window using actual receipt times, adverse ask/bid prices, depth, contract identity, latency and rejection logs. It directly tests a previously unsupported execution assumption.
2. Recover the original professional tradebook or contemporaneous rule notes if they become available. Infer a compact process using an earlier sample and assess it on later withheld trades rather than fitting indicator stories to all observations.
3. Use prior completed NSE EOD OI/PCR and same-expiry changes as valid coarse context, then compare incremental value at exactly the frozen price-signal opportunities. This can extend positioning evidence beyond the short dashboard capture window.
4. Evaluate exits, stops, adverse paths,15-minute confirmation and one-position policy without optimizing on the tiny favorable option sample. Report path ambiguity and missing quotes instead of guaranteed stop fills.
5. Measure all economics and capital feasibility using dated lots and realistic costs. A minimum lot may make proposed0.25%–0.5% planned risk infeasible for a small account.
6. Keep final evaluation sealed after rule changes and collect future quotes/signals/rejections. No elapsed computation can substitute for prospective market observations.

This audit supports a research-only process until statistically and operationally adequate evidence exists. Phase11's validated trading skill is conditional on passing those gates; an observation protocol can be implemented now, but it must not be mislabeled a validated trading strategy.
