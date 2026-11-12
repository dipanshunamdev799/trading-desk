# PROJECT ALPHA — results across phases 0–12

Report date: **10 November 2026, IST**. Historical strategy data ends8November unless explicitly stated; the read-only live diagnostic was exercised10November before the market opened. This report answers the supplied Project Alpha brief and incorporates the two earlier research packages.

## Decision and answer

**Deployment decision: RESEARCH ONLY. No primary or complementary strategy is validated.**

Using the actual inherited data, there are repeatable mechanical setups and some positive historical estimates. We have **not demonstrated a specific NIFTY option-buying situation with sufficiently reliable positive net expectancy and acceptable execution/capital risk to promote it**. The strongest new execution example has only three routed trades. Prior-session PCR provides an interesting conditional result, but its incremental and multiple-comparison tests fail.

That does not establish that the previous trader was unprofitable. You confirmed that only the inherited system is available. No professional tradebook or complete decision rule was found in the repository/database. One paper fill is not his audited trading history, and a rejected read-only broker-history request is not evidence of an empty account. The tested mechanical hypotheses cannot automatically be identified with his personal strategy.

**A material correction to earlier summaries:** historical bid/ask data does exist in the local streaming tables. Earlier experiments did not examine it at this depth. I found and used a short October window. Broad historical execution data is still missing, but describing all historical quote evidence as unavailable was incomplete.

## What changed in this research

|Evidence|Coverage and result|
|---|---|
|Inherited stream database|22,535,186 records:15,771,359 FO updates across704 instruments,3,826,062 equity updates across50 instruments,2,937,765 index updates across12 indices;26–30October2026, with30October partial|
|Actual book replay|63,633 targeted received snapshots;11 frozen signal opportunities;80 contract/exit/latency/wait configurations and two evidence modes|
|Delta-selection extension|Fresh provider Greeks actually received before entry;48 configurations;51,267 referenced snapshots; ATM controls exactly reconcile with original replay|
|Positioning|260 dated NSE EOD sessions;513 covered signals;1,026 expiry-policy feature rows;126 ablation summaries; zero tests passed both corrected return and incremental gates|
|Exits|48 exit/contract configurations, two path bounds;12 simple exit policies;612 observed candle-proxy rows across five November sessions|
|15m/context|Fixed15-minute confirmation on1,196 research sessions;12 comparison summaries;56,212 causal-state/future-outcome diagnostic labels|
|Capital|48 performance panels and384 capital/risk scenarios; whole-lot cash/risk feasibility and remaining daily/weekly loss room enforced|
|Costs|1,854 rate/scenario rows separating brokerage, exchange, IPFT, SEBI, STT, stamp duty and GST; three account-tariff assumptions|
|Operational check|Read-only live engine returned NO TRADE before opening, with stale-bar/phase/window/validation reasons; no candidate order or position created|

These counts reuse overlapping data and related policies. They are not independent market samples. Source quotes are genuine observations; simulated fills are not actual broker executions.

## Phase-by-phase disposition

|Phase|Work and evidence|Disposition|
|---|---|---|
|0: existing system|Code/pipelines/integrations/storage/order capabilities/history/experiments audited; short persisted depth history recovered|Completed audit; original professional process unidentified|
|1: market research|Primary literature, price formation, Greeks/convexity, variance premium, public OI information, Indian contract and fee changes; hypotheses have mechanisms and falsifiers|Completed research review; some empirical inputs unavailable|
|2: scientific framework|Causal/prefix checks, chronological selection, explicit missing/revision rules, event-driven quote/candle replay, limits/latency/partial/missed orders, unresolved exits, hashes|Implemented; strict exchange-book execution unsupported by timestamp evidence|
|3: competing families|Trend, ORB, compression, reversals, momentum, option expression, OI and abstention mapped to all completed panels|Tested where supported; breadth/event/long IV-vintage studies remain data-limited|
|4: incremental edge|Matched momentum/randomization, feature ablations, prior-EOD PCR/OI, paired intervals and conditional multiplicity checks|No robust incremental option edge established|
|5: option selection|Dated ATM/ITM/OTM, expiry alternatives and as-of received delta bands|Exploratory comparisons; no optimized selection promoted|
|6: exact entries/exits|Mechanical rulebook, deterministic routing, stop/target/trailing/time alternatives, gap/missing-exit behavior|Implemented for research; no best validated exit|
|7: regimes|Causal trend/range/transition logic, completed15m confirmation, forward-label confusion diagnostics, explicit abstention|Diagnostic engine; no proven all-regime classifier|
|8: adversarial tests|Longer/earlier history, walk-forward, cost/latency/nearby parameters, sequence uncertainty, concentration and gap/missing-data checks|No candidate passed the full statistical/operational gates|
|9: metrics|Expectancy, PF, wins/losses, drawdown at closes, recovery in trade counts, months, adverse/favourable bounds, holding periods, scenario returns|Reported with limits; actual broker-fill failure and reliable future ruin probabilities unavailable|
|10: protection|Whole lots, cash funding,0.25%/0.5% planned risk,1%/3% daily/weekly hypotheses, one position, no averaging or martingale, full-premium shocks|Scenario-tested; small-account feasibility often fails|
|11: trading skill|Pre/live/post-market protocol, configuration, read-only decision engine and versioned experiment separation|Conditional requirement unmet: no validated strategy to operationalize as a trading skill|
|12: package|Report, leaderboard, exact research rulebook, JSON configuration, scripts/tests, ledgers, charts, registry and decision|Delivered; RESEARCH ONLY|

Machine-readable disposition: [phase audit](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/phase-audit.json). The distinction between work performed and a validation gate passed is deliberate.

## Price signals, positioning and fifteen-minute confirmation

The earlier work tested3,600 intraday configurations,207 multi-session configurations and all47 existing price-action detectors. The frozen afternoon EMA, Donchian and pullback families had positive recent averages, but wide uncertainty and weak earlier-regime performance. Removing their five best recent trades turned their averages negative. Donchian's same-time direction matched simple30-minute momentum on all42 final-period trades. These findings remain relevant; this project did not silently restart selection from the best-looking new number.

This pass added a valid public positioning history: **exactly the preceding NIFTY session's NSE EOD chain**, with expiry determined from that dated universe. It tests PCR level/change, volume PCR, OI walls and max-pain alignment. Same-expiry changes match dated contracts rather than mix rolling expiries. Publication before the next open is assumed; historical release times were not captured. It is not an intraday OI-flow dataset.

An interesting result was pullback with month-end PCR contrarian agreement:35 final observations, +16.03 index points after two illustrative points, ordinary interval+1.61 to+36.40. However, improvement over the same covered price-only baseline had interval **−2.45 to+24.05**, and the conditional72-contrast gate failed. No positioning variant passed both corrected return and incremental criteria. Max-pain direction generally worsened the tested outcomes. The one-ATR OI-wall exclusion changed no final entries, so that specification was uninformative rather than validated.

Joining the positioning filters to62 recent actual option-candle outcomes produced84 small summary cells. Apparent PCR improvement largely removed one shared loss. Those correlated five-day comparisons are not independent validation. Prior futures-price/OI confirmation had too few covered opportunities for inference. [Positioning report](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/positioning-report.md).

Fifteen-minute confirmation used only closed15m bars aggregated from three complete5m bars. EMA4/9 direction retained all69 recent EMA entries and all61 pullback entries. It removed one of42 Donchian entries, changing its average from+6.83 to+7.98 points with an interval still spanning zero. Earlier-history effects were similarly small. **This extra confirmation largely duplicated information already present.** It is an ablation of existing5m rules, not a claim that every possible15m strategy was tested.

Causal state labels were compared with subsequently realized60-minute path efficiency for evaluation only. Of14,861 observations labeled trend at the decision,4,905 subsequently met the chosen future-trend label;9,956 did not. That demonstrates unstable state persistence under this definition, not an ability to know a future trend day. Time-of-day candle range/absolute-change profiles are exported as descriptive statistics; high activity does not by itself mean options are underpriced. [Timeframe and regime diagnostics](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/timeframe-report.md).

## Actual received bid/ask replay

The recovered full-feed snapshots include five book levels, last-trade time, OI, IV and provider Greeks. Local receipt time is recorded. The provider frame clock sometimes leads local receipt; median source-minus-receipt offset in the extracted sample was approximately+98ms,99th percentile+215ms, with some materially delayed frames. There is no independently verified book-level exchange-event timestamp.

Two evidence modes were kept separate:

- **Verified exchange-book mode:** unsupported; no observation has the required independently verified event clock.
- **Received frame-snapshot mode:** simulated execution against actual quotes available at local receipt, under fixed stated timing/freshness/depth assumptions.

Entry limits were anchored to a valid predecision ask. Later fills required250/1000ms latency,2/5second deadlines, at most2% relative spread and one dated lot of best depth. Last-trade freshness uses the provider clock consistently; cross-clock tolerance was fixed at±1second and was not called clock calibration. Square-off dispatch occurs latency+wait-budget seconds before the deadline. Missing chains, quotes and unresolved exits remain explicit outcomes.

With the fixed250ms/two-second assumptions, deterministic routing yielded only **three trades**, on26,28 and29October.27October had no qualifying fresh prior chain.

|Contract and exit|Trades|Gross ₹/lot|Base net ₹/lot|Severe net ₹/lot|
|---|---:|---:|---:|---:|
|ATM,60m|3|582.83|466.26|236.26|
|One step ITM,60m|3|633.75|514.14|284.14|
|One step OTM,60m|3|469.08|355.33|125.33|
|One step OTM,20% stop|3|329.33|215.79|−14.21|

Base snapshot net includes dated sale STT and₹100 other-fee allowance. Severe net adds two premium points of impact and₹200 other fees. Ask/bid already contains the observed spread. The ATM sample includes a losing trade of approximately₹1,975 per lot. These are modeled historical outcomes, not actual order fills, and do not support a confidence or positive-expectancy claim from three observations.

The initial delta-band comparison had no eligible contracts because the chain snapshot's Greeks were older than the freshness rule. A separately registered availability extension then used **provider Greeks actually received before the decision**, retaining the original dated universe. It did not replace the original experiment or create a new holdout.

|Expression of the same routed profile|Trades|Base net ₹/lot|Severe net ₹/lot|
|---|---:|---:|---:|
|Unchanged ATM control|3|466.26|236.26|
|Absolute delta0.4–0.6|3|391.50|161.50|
|Absolute delta0.6–0.8|3|518.47|288.47|

**No delta-band advantage is established.** The control reconciles exactly. IV was unused in these outcomes; chain IV percentages and raw stream IV fractions were discovered to have different units and inherited metadata timestamps. A separate normalized provenance artifact records availability and units without rewriting frozen inputs. These fields must not be pooled blindly for an IV study.

Reports: [original book replay](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/exit-stream-report.md), [received-Greeks extension](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/exit-stream-delta-v2-report.md), [IV provenance](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/delta-iv-provenance.json).

## Exits, stops and capital protection

Twelve simple exit alternatives were combined with four existing strike/expiry policies and two candle path bounds. The global router kept one position at a time. Depending on the configuration, there were only5–7 trades across five November sessions. No exit was selected as optimal.

The event engine handles stop/target ordering bounds, underlying invalidation translated to a later option observation, time/structure/trailing alternatives, session cutoff, partial/missed execution and unresolved exposure. Stops trigger an attempted later exit; a gap can produce worse loss. Synthetic regression cases validate these semantics, but they are not counted as market results. Actual same-bar path ambiguity happened to be absent in this small accepted sample; that does not eliminate the risk generally. [Exit study](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/exit-report.md).

For a fixed reference—month-end ATM,60-minute exit, adverse-first candle convention—the severe-cost result was seven trades,57.1% wins, profit factor3.09, average win₹3,867, average loss₹1,668 and total₹10,463 per one dated lot. Drawdown at trade closes was₹3,227; observed consecutive losses were two. These attractive-looking figures come from one inspected week and include modeled asynchronous prices. **They are not a validated account return or evidence that PF3.09 will persist.** Candle/observed MAE and MFE are explicitly bounds, not tick-perfect paths.

![Reference sample paths and drawdowns](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/equity-drawdown.png)

The384 capital/risk cases used₹100k/250k/500k/1m, risk fractions0.25%/0.5%, one position, full cash premium funding, severe fee reserves and remaining daily/weekly planned-loss headroom. Without a defined loss reserve, full premium was budgeted. In this sample:

- At₹100k and₹250k, both risk fractions admitted zero trades across all48 configurations.
- At₹500k and0.5%, only four configurations admitted even one trade.
- At₹1m and0.5%,20 configurations admitted trades; full-premium shocks still frequently exceeded a1% daily budget.

These are **feasibility scenarios**, not a recommendation to allocate₹1m or raise risk. Different premiums, costs or validated stops could change feasibility. A minimum lot can make a sensible percentage limit impossible; correct behavior is to skip, not round upward. A stop cannot guarantee a maximum loss or repair negative expectancy.

The Monte Carlo file resamples the five observed daily blocks2,000times per configuration. Its intervals are conditional on that tiny sample. It cannot supply a credible real-world ruin or future risk-limit-breach probability, and missing tail events are not assigned zero probability. Separate full-premium-loss scenarios expose this limitation. [Risk/metrics report](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/risk-metrics-report.md), [capital scenarios](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/risk-feasibility.csv).

## Costs and market-structure corrections

The detailed fee sensitivity now separates brokerage, exchange, IPFT, SEBI levy, STT, buy-side stamp duty and GST. It evaluates₹10/20/30 executed-order brokerage assumptions and0/2/5 premium-point impact sensitivities. Historical client tariff, rounding, rebates and contract-note reconciliation remain unverified. Results remain provisional rather than being relabeled as exact realized charges.

NSE's March2026 circular reallocates option exchange/IPFT charges while retaining combined₹3,553 per crore per side. Adding the old IPFT again to the revised combined rate would double-count fees. STT changes on1April2026 are dated explicitly. The model does not count spread twice. [NSE exchange/IPFT circular](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf), [STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf), [broker rate card](https://upstox.com/brokerage-charges/).

Dated lot and expiry transitions are documented in the literature/audit; current rules are not projected backward. CAS went live3August2026, changing closing-session behavior. The15:10 research cutoff is a strategy boundary, not a claim about official closing time. [NSE CAS implementation](https://nsearchives.nseindia.com/content/circulars/CMTR75479.pdf).

## What the trader's profitability tells us

It is a reason to investigate the inherited workflow, not a substitute for the missing trade-level information. A dashboard can support a discretionary trader without fully specifying when he acted, which opportunities he ignored, how he chose contracts, or how he managed exits. Our current records do not identify those choices. Neither the failed mechanical tests nor the three positive book-replay averages prove or disprove his complete method.

The most useful remaining research leads are a compact price-only trend reference, carefully isolated prior-positioning context and better execution observations. The readiness leaderboard prioritizes information value and evidence quality, not the biggest historical return. No weak candidates are combined into a claimed validated strategy. [Leaderboard](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/strategy-leaderboard.md).

## Exact rules, engine and forward protocol

The [rulebook](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/rulebook.md) defines price-state thresholds, signal priority, contract selection, timing/depth/spread gates, tested exits, lot sizing, re-entry, square-off and emergency handling. The [machine configuration](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/alpha-config.json) records all gates and leaves `primary_validated_strategy:null` and production/orders disabled.

The [diagnostic engine](C:/Users/ME/Desktop/trading-desk/scripts/alpha_signal_engine.py) can read current Upstox candles/status or replay frozen input. It reports causal regime/patterns and reasons, while operational action stays NO TRADE. Before opening on10November it correctly suppressed stale/closed/outside-window candidates. Empty/malformed data, conflicting duplicates, misaligned clocks, late cutoffs and unpassed validation also abstain. Contract/entry/stop/size remain unapproved rather than inventing a live trade.

The brief makes a validated trading skill conditional on surviving validation. That condition is not met. The delivered [forward protocol](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/forward-protocol.md) therefore defines prospective observation and promotion requirements rather than calling the research a production skill. Reserve genuinely new sessions after freezing rules. Use training-only variance and an economically meaningful effect for a cluster-adjusted sample target;60 sessions/200 opportunities are minimums, not proof of adequacy. Do not stop early because P&L looks good. No real orders were placed.

## Reproducibility and remaining limits

The [research directory](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha) contains exact ledgers, rejected opportunities, event journals, protocols, source hashes, metrics, monthly breakdowns, curves, cost sensitivities and independent verification. The [hypothesis catalogue](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/hypotheses.json) specifies mechanisms, measurements, baselines and falsifiers. The [experiment registry](C:/Users/ME/Desktop/trading-desk/artifacts/project_alpha/experiment-registry.json) records code/data versions and links all prior grid ledgers, including failures.

Key replay commands, from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts/research_alpha_positioning.py
.\.venv\Scripts\python.exe scripts/research_alpha_exits.py
.\.venv\Scripts\python.exe scripts/research_alpha_streams.py
.\.venv\Scripts\python.exe scripts/research_alpha_streams.py --selection artifacts/project_alpha/stream-selection-delta-v2.json --prefix exit-stream-delta-v2 --policies ATM,abs_delta_0.4_0.6,abs_delta_0.6_0.8
.\.venv\Scripts\python.exe scripts/research_alpha_15m.py
.\.venv\Scripts\python.exe scripts/research_alpha_costs.py
.\.venv\Scripts\python.exe scripts/research_alpha_metrics.py
.\.venv\Scripts\python.exe scripts/test_alpha_event_engine.py
.\.venv\Scripts\python.exe scripts/test_alpha_risk_signals.py
.\.venv\Scripts\python.exe scripts/test_alpha_safety_review.py
.\.venv\Scripts\python.exe scripts/alpha_signal_engine.py --live
```

Replays overwrite only their own generated outputs. Database extraction scripts require the existing local database; frozen studies use retained files. The live diagnostic is a bounded read-only call and does not start an order bot. The original stream script source is archived under its registered hash, so its protocol remains reproducible after the CLI extension.

Outstanding evidence is specific: a broader multiregime historical/forward book sample, independently characterized clocks and fill behavior, longer point-in-time IV/positioning/context vintages, full event/breadth histories, actual account-cost reconciliation and new prospective outcomes. No amount of rerunning the already inspected dates can produce those observations.

**Answer to the brief's final question: not yet demonstrated.** We can identify and replay defined situations, but the current evidence does not establish consistently positive executable expectancy with proven acceptable capital risk. The package makes that conclusion auditable and defines what evidence must change before promotion.
