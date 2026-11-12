# NIFTY directional options research

Research date: **9 November 2026**. Market-data cutoff: **8 November 2026**. Scope: directional buying of NIFTY calls and puts, with intraday and multi-session holding hypotheses. Position sizing and stop/target optimization are deferred as requested.

## What the evidence supports

**The project now has a reproducible research foundation, but the tests do not establish a dependable profitable strategy.** I tested 3,600 intraday configurations, 207 multi-session configurations, and replayed all 47 existing price-action detectors. None of the 11 intraday or four daily family finalists passed its final-period descriptive gate. This does not prove profitable NIFTY trading is impossible; it means these tested specifications have not supplied adequate evidence.

The most useful intraday candidates for further observation are afternoon EMA trend continuation, Donchian breakouts and trend pullbacks. Their positive averages have wide uncertainty intervals. The earlier seven-session trendline/mitigation findings weakened on longer history. Generic RSI fades, failed breakouts and gap continuation did not survive in their selected forms. The existing max-pain study also gives no support to a simple expiry-price magnet strategy.

The important distinction is **index direction versus option-premium profitability**. All strategy results below measure the former. Actual historical premiums, strikes, expiry selection, spreads, implied-volatility changes and fees are still required for the latter. Time decay and IV sensitivity can offset a correct directional call. [OIC Theta](https://www.optionseducation.org/advancedconcepts/theta), [OIC Vega](https://www.optionseducation.org/advancedconcepts/vega).

![Frozen finalist estimates and uncertainty](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/research-results.png)

## What was actually tested

|Research panel|Data|Experiment|Result|
|---|---|---|---|
|Intraday strategy lab|458 complete 09:15–15:10 research windows, 1 Jan 2025–6 Nov 2026; 32,518 five-minute bars|3,600 configurations, 11 families, 15/30/60-minute exits|185 development/validation eligible; 11 family finalists; zero gate passes|
|Existing project concepts|204 one-minute research sessions, Jan–Oct 2026; 458 five-minute sessions, Jan 2025–Nov 2026|47 detectors, five fixed EMA-filtered variants and displacement fade; 5/15/30-minute exits|Longer-history replication weakens several earlier candidates; full results disclosed, no significance claim|
|Multi-session study|2,442 daily observations, 2 Jan 2017–8 Nov 2026; first 200 reserved for warmup|207 configurations in four families; 1/3/5-session holds|36 development/validation eligible; four finalists; zero gate passes|
|Existing max-pain study|246 NIFTY price sessions and 53 expiries in the archived one-year study|Frozen pre-expiry target versus mirror control|No support for unconditional convergence buying|
|Current listed option probe|17 Nov 2026 expiry, 25,000 CE/PE, recent five-minute history|Access and coverage only|History available, but sparse; no premium strategy result|

These are correlated experiments on overlapping markets, not thousands of independent confirmations. The complete ledger includes losing configurations. All tests use next-open entry after a confirmed signal. Positions do not overlap within one configuration. Intraday trades close by 15:10; daily trades crossing development/validation/final boundaries are excluded. Friction assumptions are sensitivities in **index units**, not an estimate of option brokerage, taxes or spread costs.

The historical final period is not genuinely untouched: October 2026 had already been studied in this project. The first database-only run is retained, and broader history was subsequently added without changing that lab's grid or selector. Five newly observed November sessions are disclosed separately but are too small to establish an edge. The daily panel overlaps the intraday period and is not an independent replication. Conditional bootstrap intervals do not correct the complete parameter search. Repeated historical selection is precisely the problem highlighted in [The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).

## Intraday results

The chronological split was 274 development sessions through 6 February 2026, 92 validation sessions through 25 June, and 92 final sessions from 29 June through 6 November. One eligible candidate per family was selected using only development/validation means after two illustrative index points. Eligibility required at least 100/30 trades and positive means in both periods. The selector was saved before final evaluation.

The families were EMA trend, Donchian breakout, momentum, opening-range breakout, trend pullback, RSI reversion, EMA-distance reversion, compression breakout, gap fade, gap continuation and failed breakout. Six predefined filters and four time windows tested conditional behavior without labeling the eventual day type in advance.

Selected examples below are all frozen family finalists. Means and intervals are **index points per trade**.

|Frozen finalist|Final trades|Gross mean|After 2 points|After 5 points|95% block interval after 2 points|
|---|---:|---:|---:|---:|---|
|EMA12/26 separation >0.5 ATR; trend filter; afternoon; 60m|69|9.07|7.07|4.07|−6.34 to 21.05|
|Donchian20; trend filter; afternoon; 60m|42|8.83|6.83|3.83|−10.19 to 25.22|
|Pullback with EMA9/21; trend filter; afternoon; 60m|61|7.42|5.42|2.42|−6.95 to 19.55|
|60m opening range +0.25 ATR; trend filter; afternoon; 60m|55|7.58|5.58|2.58|−8.48 to 20.70|
|Momentum6 >0.5 ATR; trend filter; afternoon; 60m|69|5.18|3.18|0.18|−6.71 to 15.31|
|Failed breakout20; range filter; 60m|44|−2.33|−4.33|−7.33|−17.19 to 7.36|
|RSI40 reversion; EMA-aligned filter; 60m|41|−9.50|−11.50|−14.50|−27.76 to 3.98|

All 11 finalist intervals span zero. The descriptive gate required at least 30 final trades, positive mean after five points, and a positive lower interval bound after two points. **Zero passed.** The intervals use 3,000 resamples of five-session blocks to account for clustered outcomes; they remain conditional on the selected rules.

A simple preceding-30-minute momentum baseline held for 60 minutes produced +3.96 points after two points on 460 final trades, with interval −0.28 to +8.44. That is an important control: elaborate setups must demonstrate additional value beyond simple momentum. Always-up and always-down baselines were negative after two points at every tested horizon. This is not a matched-time causal comparison of each complex strategy; that remains part of stricter follow-up.

The trend regime here has an exact definition: the last 12 five-minute changes have directional efficiency of at least 0.35, and the absolute EMA9–EMA21 separation is at least 0.5 prior ATR. Efficiency is absolute net displacement divided by the sum of absolute changes. These are observations available at entry. They are not a label based on the day's eventual high, low or close. The regime filter itself does not require the sign of EMA9/21 to agree with every strategy; each saved rule determines its own direction.

For the shortlisted 60-minute afternoon rules, confirmed signals can enter from 13:05 through 14:10 IST and exit no later than 15:10. The pullback rule uses EMA9 relative to EMA21, a touch within 0.75 ATR of EMA9, a close back on the trend side and a same-direction candle body. These are reproducible research definitions, not live trade instructions.

All 11 finalists, baseline details and November diagnostics: [intraday lab report](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/lab-report.md). Every searched configuration: [experiment ledger](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/lab-all-configurations.csv).

## Did the existing signals replicate?

The production detector was replayed without changing its thresholds. Its events carry confirmation timestamps, including delayed pivot confirmation. The comparison below adds the same-side session-local EMA9/21 filter to the previously discussed candidates and uses a 15-minute hold.

|Existing signal|Chart|Later-period trades|Gross mean points|After 5 points|
|---|---|---:|---:|---:|
|Trendline break #19 + EMA|1m|145|3.99|−1.01|
|CHoCH #20 + EMA|1m|153|3.98|−1.02|
|Mitigation/retest #47 + EMA|1m|709|2.61|−2.39|
|Opening-range breakout #39 + EMA|1m|51|9.07|4.07|
|BOS #42 + EMA|1m|350|4.10|−0.90|
|Trendline break #19 + EMA|5m|96|−1.63|−6.63|
|Mitigation/retest #47 + EMA|5m|616|1.49|−3.51|
|Opening-range breakout #39 + EMA|5m|105|2.18|−2.82|

The later one-minute period starts 31 August 2026; the five-minute period starts 29 June. These different periods and sampling rules mean raw timeframe comparisons are descriptive. The one-minute ORB result deserves observation, but its weaker five-minute result and the many examined alternatives prevent treating it as a proven edge. The earlier #19 + EMA result of +11.26 points came from only 24 trades; the broader +3.99-point estimate is a useful warning against anchoring on a short successful window.

All 47 detectors were evaluated. Forty generated directional trades; seven reference/neutral concepts have explicit zero-trade rows with null returns. This panel contains 318 fixed rule/timeframe/horizon combinations and 636 partition summaries. No new winner or statistically significant predictor is declared from this panel. [Concept replication report](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/concept-report.md), [complete results](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/concept-replication.csv).

The prior max-pain study's strict NIFTY primary subset had 45 observations: 24.44% converged toward the frozen target versus 37.78% toward an equal-distance opposite target. A target being touched during a day is not an executable profitable option trade. Keep max pain as testable context, not a mandatory directional anchor. [Project and prior-evidence audit](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/project-audit.md).

## Multi-session results for longer holds

The daily panel used development dates from October 2017 through March 2023, validation through 15 January 2025, and a 449-session final period through 8 November 2026. The four families were EMA trend, Donchian, momentum and RSI reversion. Rules were tested unfiltered, EMA-aligned and long-only, with 1/3/5-session exits. Selection used development/validation results only.

These returns are **basis points of the underlying index per trade**, not percentage returns on an option premium. One basis point is 0.01%.

|Frozen finalist|Hold|Final trades|Gross bps|After 5 bps|95% interval after 5 bps|
|---|---|---:|---:|---:|---|
|EMA10/30, long-only|5 sessions|50|−5.66|−10.66|−53.09 to 33.18|
|Donchian10 +0.25 ATR, long-only|5 sessions|18|60.76|55.76|−35.25 to 118.52|
|20-session momentum, EMA-aligned|5 sessions|75|−26.16|−31.16|−69.91 to 8.57|
|RSI30 reversion|1 session|37|5.15|0.15|−12.19 to 22.04|

None passed the analogous daily gate. The positive Donchian result has only 18 final trades and wide uncertainty. The momentum finalist underperformed buying the index at exactly its own entry/exit times by 45.65 bps per trade. Long-only candidates have zero difference from that matched-direction control by construction; assessing their entry timing requires additional controls. Always-long/short baselines at all three horizons are also reported.

A one-session hold means next open to that session's close; three/five-session holds include intervening overnight exposure. This tests underlying timing at longer horizons. It does not establish that a monthly expiry, weekly expiry, or a multi-week option hold is profitable. Longer option holding periods remain untested here. [Daily study and baselines](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/daily-report.md).

## Data availability and the project components

The seven-day assumption is incorrect for ordinary NIFTY candle history. Upstox documents much longer V3 retention; I successfully retrieved January 2025 intraday candles and January 2017 daily candles. The one-month restriction for five-minute data is a **per-request window**, not total history. [Upstox V3 documentation](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).

Expired-option discovery returned HTTP 401 / `UDAPI1149`, requiring Upstox Plus. Its documentation describes up to six months of expired dates. That entitlement or another permitted historical source is the immediate data requirement for a broad premium study; even then, candle history will not recreate historical bid/ask depth. [Upstox expired contracts](https://upstox.com/developer/api-documentation/get-expiries/).

The current-contract probe retrieved 1,002 CE and 356 PE five-minute observations within the research clock window, of which 664 and 185 had positive volume. These were not complete sessions. The 25,000 strike was chosen retrospectively using the latest spot observation, so this probe must never be presented as an ATM backtest. The application database's existing option candles were daily only: 1,766 bars across 612 instruments, mostly September–October 2026.

|Project component|Use in the system|Required correction or qualification for research|
|---|---|---|
|47-concept price-action engine|Confirmed events and reference levels|Preserve `known_at`; OHLC “order blocks” are heuristics, not measured order flow|
|127-factor NIFTY dashboard|Candidate context library|Only 64 factors had stored observations; catalog size is not usable historical sample size|
|OI/PCR/max pain|Positioning context and optional conditional filters|Use contemporaneous captured snapshots; no automatic contrarian/continuation assumption|
|IV/Greeks/VIX|Contract choice and volatility context|Today's Greeks/IV must not be copied into historical trades|
|Market gateway/store/stream|Raw data, capture times, freshness, forward replay|Require completed bars and point-in-time observations; preserve missingness|
|Paper and backtest pages|Display/accounting scaffolding|Daily marks and sample JSONs are not an options execution simulator|
|Credit-spread engine|Reusable quote/depth checks and durable journal|Its strategy and short-premium accounting are different from directional option buying|
|IPO research|Separate product|No demonstrated incremental NIFTY timing signal|

The full service-by-service audit is [here](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/project-audit.md). In particular, a historical feature join must enforce `observed_at <= decision_time` before choosing revisions. A reported historical date does not establish that the value was then available. Sector breadth also needs historical constituents. NIFTY spot has no traded volume: use identified futures/ETF volume for VWAP or activity filters, with their own timing and basis qualifications.

The generic paper-price helper can carry old daily premiums forward for display. Such values must be rejected as execution prices. This is one reason the application’s visible paper profit cannot validate a strategy until an exact-contract, contemporaneous-price simulator is added.

## A systematic approach across market conditions

The system should decide **whether there is enough evidence to trade**, then select a trigger and contract. It does not need a trade in every condition. The table is a research policy to test, not a validated switching portfolio.

|Observed state at decision time|Candidate treatment|Current evidence and next comparison|
|---|---|---|
|Directional movement with efficient price path and EMA separation|Frozen afternoon EMA/Donchian/pullback candidates|Best remaining intraday research group; compare against simple momentum at matching opportunities|
|Early range formation or compression, followed by a confirmed break|ORB or compression breakout; optionally a separately registered retest|ORB has some positive estimates, weak transfer; compare entry delay without retuning thresholds|
|Low directional efficiency, repeated rejected breaks|Abstain by default; study fixed failed-break/reclaim rules|Selected range/RSI rules did not establish positive net expectancy|
|Large overnight gap|Separate continuation from fade; use official prior close in a new experiment|Current gap proxy is prior research-window close, sometimes across excluded days; it needs this correction before promotion|
|Scheduled event or unusual volatility|Separate evaluation bucket; require event timestamps and contemporaneous IV|No validated event-specific premium model; candles alone cannot establish cheap/expensive options|
|Conflicting signals, missing/stale data, wide or absent quotes|No trade; record reason and hypothetical signal|Abstention is a measurable output, not a failure to make a prediction|

For each signal, record the information available then, state label, rule version, direction, confirmation time and every rejection reason. Do not retrospectively relabel a losing day as “not a trend day.” A router combining strategies must be tested as a new portfolio, including simultaneous signals and correlated exposures; the individual mean returns cannot be added together.

OI change, PCR, IV/skew, VIX, futures/ETF activity, sector breadth and prior released cash flows should enter one at a time. Compare “price-only” with “price plus this one input” on identical opportunities and available timestamps. Then test a compact combination if the incremental contribution persists. Some of these histories are short or absent; reconstructing them from today's dashboard would manufacture evidence.

Academic intraday-momentum work supplies a reason to test continuation, not a NIFTY options guarantee. Reddit discussions contributed hypotheses about EMA context, ATM/ITM selection and spreads; identities and profitability were not verified, and one author explicitly reported inconsistent profits. Sources and their limits are documented in [external research](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research/external-research.md).

## How to test weekly versus monthly options properly

1. **Freeze the underlying signal first.** Preserve the shortlisted rule definitions, a simple momentum control and no-trade output. Do not change the trigger after seeing premium results.
2. **Resolve the actual contract at the decision time.** Load dated instrument identities, expiry, strike, lot size and listing availability. Current NSE rules specify Tuesday expiries with holiday adjustments; historical dates and quantities must come from dated records. [NSE contract specifications](https://www.nseindia.com/static/products-services/equity-derivatives-nifty50).
3. **Compare a small declared contract grid.** Nearest eligible weekly versus monthly expiry; ATM versus one modestly ITM alternative, or fixed absolute-delta buckets when contemporaneous Greeks are available. Treat expiry day separately. Deduplicate weekly/monthly when they refer to the same contract. Freeze tie-breaking and missing-quote behavior.
4. **Require executable price evidence.** Use entry ask and exit bid after realistic decision latency where quotes exist, with depth and freshness checks. OHLC-only runs need conservative fill sensitivities and must be labeled provisional. A candle's high or low is not a guaranteed fill. Never forward-fill an untraded premium into an entry or exit.
5. **Calculate premium P&L directly.** For one lot, `(exit premium − entry premium) × dated lot size − dated charges − modeled slippage`. Include brokerage, exchange/clearing charges, SEBI fees, GST, stamp duty and applicable STT according to the trade date and transaction type. Spread is already reflected by ask/bid; avoid counting it twice. Keep account-return and sizing claims out until capital rules are specified.
6. **Report the source of the result.** Separate direction, IV change, time-to-expiry, strike choice, spread, call/put side, time of day and market state. Greeks provide attribution approximations, not substitute execution prices. Show rejected trades and missing coverage alongside successful fills.
7. **Reserve new evidence before changes.** Use nested chronological development for additions, then freeze one final specification. Review after a predeclared sample/date, not after an attractive week. Require positive net premium expectancy under conservative execution, uncertainty bounds, stability across distinct periods and no dependence on a few outliers before considering deployment.

Position sizing and protective-exit design can follow this edge research. Entry, time exit, latency, spread and fees cannot be postponed because they define what a profitable observation means.

## Concrete build order

First add a point-in-time feature table and a long-option replay adapter using the existing storage/provenance infrastructure. Next obtain expired premium history and continuously archive currently listed contracts' quotes, Greeks and chains. Compare the frozen shortlist across a compact expiry/strike grid. Only survivors move to a forward paper journal with executable quotes and rejection logs. The current generic Paper page needs that adapter before it can serve as proof of performance.

A future bot should run this pipeline: **fresh data → available-information features → eligible market state → fixed signal → exact contract → executable quote → journal**. An “all conditions” model includes an abstain state. A bot skill or an LLM-written trading explanation would add no predictive evidence by itself.

## Reproduce and inspect

Frozen data and all outputs are under [the research directory](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research). Replays use local files and do not require Docker or a broker connection once these inputs exist. The application database remains separate; this research does not replace its retained history.

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts/research_directional_lab.py
.\.venv\Scripts\python.exe scripts/verify_directional_lab.py
.\.venv\Scripts\python.exe scripts/research_existing_concepts.py
.\.venv\Scripts\python.exe scripts/research_daily_directional.py
.\.venv\Scripts\python.exe scripts/plot_directional_research.py
```

These replay scripts overwrite their generated reports using frozen inputs. The fetch scripts preserve cached files; changing the date range requires a new experiment directory rather than silently extending a sealed evaluation set.

Verification completed: **27 feature/event prefix checks** across the three panels, **116 independent intraday ledger/selection checks**, and **5,425 daily trade-boundary/price/nonoverlap/P&L assertions**. Intraday aggregation agreed with native candles on all OHLC values for 14,535 overlapping bars. Source hashes, exclusions, frozen selectors and trade ledgers are retained. One-minute replay excludes the partial 30 October session; five-minute replay excludes two short/special windows. These checks establish implementation consistency, not future profitability.

Code: [intraday lab](C:/Users/ME/Desktop/trading-desk/scripts/research_directional_lab.py), [production-concept replay](C:/Users/ME/Desktop/trading-desk/scripts/research_existing_concepts.py), [multi-session lab](C:/Users/ME/Desktop/trading-desk/scripts/research_daily_directional.py), [history fetch](C:/Users/ME/Desktop/trading-desk/scripts/fetch_directional_history.py), [daily fetch](C:/Users/ME/Desktop/trading-desk/scripts/fetch_directional_daily.py).
