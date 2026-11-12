# NIFTY research: deeper validation and actual option premiums

Completed 9 November 2026. Historical strategy inputs end 8 November; the separate quote capture is dated 9 November. This extends [the first research report](C:/Users/ME/Desktop/trading-desk/NIFTY_DIRECTIONAL_RESEARCH.md) without changing its frozen experiments.

## Result

**The additional research has not established a deployable profitable strategy.** It did establish that the project can obtain and replay real historical option premiums, reconstruct causal context, compare fixed strategies against controls, and record forward observations with explicit abstentions.

The distinction matters in the results: the recent five-session intraday option diagnostic was positive, while the longer daily-option study was generally negative. The underlying trend rules were much weaker in 2022–2024, and their apparent 2026 gains depended heavily on a few large winners. Neither more indicators nor a changing strategy selector resolved the uncertainty.

This research covers the concrete next stages proposed in the first report. It cannot complete future forward validation today or reconstruct historical quotes and publication times that were never captured. Those boundaries are listed explicitly below. Position sizing and stop/target optimization remain outside this study, as requested.

![Actual option premium results](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/option-premium-results.png)

## Work completed

|Stage|Implementation and evidence|Outcome|
|---|---|---|
|Expand market history|1,196 complete five-minute research windows, January 2022–November 2026; 6,677 daily observations, January 2000–November 2026|Earlier regimes weaken the intraday shortlist; longer holds do not transfer consistently|
|Stronger controls|Matched entry/exit controls, session direction randomization, conditional multiple-comparison intervals, latency, outlier, month/quarter/side diagnostics, 36 ablations|No incremental directional edge established|
|Combine rules properly|Fixed one-position router and monthly selector using only prior 120 sessions|Positive recent averages remain uncertain; combining rules does not validate them|
|Build point-in-time features|32,518 decision rows; VIX, ETF activity, official gaps, missingness and 35,348 captured dashboard revisions|No tested added context filter has a positive lower final-period return interval|
|Correct gap measurement|Replaced prior 15:10 research close with official prior daily close, preserving rule parameters|Gap fade remains uncertain; continuation worsens|
|Test exact historical options|106 daily signals; 424 contract-policy comparisons using dated official NSE contract records and premiums|EMA, Donchian and momentum negative; positive RSI variant uncertain|
|Test recent intraday premiums|17 fixed signals over 2–6 November; 68 attempts, 62 usable option-candle outcomes|Positive small diagnostic; insufficient for a profitability claim|
|Capture forward data|Eight current ATM/ITM CE/PE contracts, depth, quote/LTT timestamps, Greeks and market status|Market closed; eight abstentions, zero fills|
|Preserve decisions|Versioned, idempotent SQLite observation journal; explicit timing, rule, side, expiry, depth and quote gates|Recorded actual capture and tested invalid/stale cases without invented fills|

Different rows reuse overlapping signals and market periods. Counts must not be added as independent evidence.

## 1. Stronger controls and earlier regimes

The three frozen candidates were afternoon EMA12/26 trend continuation, Donchian20 breakout and EMA9/21 pullback, all with 60-minute exits. Entries and parameters were preserved. The fixed router prioritizes EMA, then Donchian, then pullback, with one position at a time. This evaluates the actual combined opportunity set rather than adding three strategy profits.

Earlier 2022–2024 observations are a **backward replication** of rules motivated by 2025–2026 research, not a prospective holdout. Results below are index points per trade after two illustrative points. The intervals adjust six comparisons for the three fixed rules' net means and momentum excess, conditional on this shortlist; they do not correct the original strategy search. Router intervals are exploratory.

|Frozen rule|2022–2024 trades|Mean after 2 points|Conditional interval|Excess over same-time 30m momentum|
|---|---:|---:|---|---:|
|EMA trend|511|0.54|−5.42 to 6.48|0.25|
|Donchian|368|2.63|−5.21 to 10.73|0.00|
|Pullback|469|0.76|−5.65 to 7.15|0.54|
|Fixed router|552|0.23|−5.67 to 6.17|0.38|

In the final 29 June–6 November 2026 period, the rule means remained +7.07, +6.83 and +5.42 points. Their excess over momentum at the identical entry/exit times was +5.32, 0.00 and +3.21, with intervals spanning zero. Donchian selected exactly the same direction as the 30-minute momentum control on all 42 comparable trades. Its extra machinery did not add direction-choice value at those timestamps.

Session-wide sign randomization produced two-sided diagnostic p-values of 0.219, 0.385 and 0.335. These are conditional directional-null diagnostics, not proof of market stationarity. Removing each strategy's best five final-period trades turns its mean negative: EMA −4.91, Donchian −9.27 and pullback −5.79 points. Such removal is a stress test, not permission to discard those legitimate trades from the official result.

The fixed router returned +6.32 points on 73 final trades, but +0.23 in the earlier regime. A monthly selector using only the preceding 120 completed sessions, at least 30 trades and positive mean after five points returned +6.38 points on 57 final trades, with interval −8.05 to 21.49. Adaptation did not establish a reliable edge.

One-bar entry delay, different holding periods, time windows, omitted trend filters, monthly/quarterly stability and call/put direction splits are all disclosed. They were not used to choose a replacement winner. [Full control report](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/control-expanded-report.md), [all control trades](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/control-expanded-trades.csv).

## 2. Longer holding periods and historical drift

The daily study now spans 6,677 observations from 2000 through 2026. The four already selected daily parameter sets were evaluated at fixed 1/3/5/10/20-session holds, with always-long, always-short and 252-session momentum controls: 35 rules and 105 rule-period summaries. No new winner was selected.

Some long-only 20-session rules were positive in 2000–2016. EMA returned +135.36 underlying basis points after ten illustrative bps per trade; always-long returned +102.84. These are different entry schedules, so their difference is not a matched statistical proof of timing skill. In the 2025–2026 historical final period, the EMA 20-session result was −51.57 bps on 15 trades. The Donchian 20-session result changed from +163.25 bps in the earlier period to −74.77 on 13 recent trades. RSI's longer holds were generally weak in the earlier sample.

The earlier positive estimates do not establish option profitability. Long-only outcomes contain market drift, the earliest history predates the relevant options market, and ten/twenty-session holds may require different expiries. Twenty-session option premiums, IV exposure and overnight gaps were not reconstructed by an index test. [Longer-horizon report and complete comparisons](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/long-report.md).

## 3. Did VIX, volume or other context help?

The feature panel joins only completed candles available by the decision. It uses actual NIFTYBEES reported volume, a same-clock median over the preceding 20 observed ETF sessions with at least five valid observations, and a clearly labeled candle-derived VWAP proxy. It does not assign traded volume or VWAP to NIFTY spot.

The VIX median threshold was learned only from development data. Official gaps use the strictly preceding daily close. Historical candle reconstruction assumes availability at bar completion; it does not prove the broker delivered each bar with zero latency or that today's historical candles are an unrevised vintage.

Examples from the fixed final period, in index points after two points of illustrative friction:

|EMA trend context|Trades|Mean|95% conditional interval|Change versus baseline interval|
|---|---:|---:|---|---|
|No added context|69|7.07|−6.34 to 21.05|Reference|
|VIX below development median|28|−0.62|−13.22 to 14.42|−25.99 to 10.90|
|VIX not rising|27|−1.25|−13.79 to 13.40|−22.58 to 5.53|
|ETF relative volume ≥1|49|12.16|−6.21 to 29.13|−2.27 to 12.19|
|Direction agrees with official gap|38|15.87|−4.22 to 37.29|−1.72 to 21.44|

Gap agreement and ETF activity raised some averages, but their uncertainty and improvement intervals include zero. Filtering also changes the sample; this is not evidence that the added feature caused better returns. Low/not-rising VIX weakened the shortlist. ETF VWAP agreement mostly retained the same trades. All three candidates and all fixed filters are in the 54-row results table; none is promoted.

Correcting the gap rules' prior close gave gap-fade +3.29 points on 64 final trades, interval −7.49 to 13.35. Gap continuation fell to −12.98 on 47 trades, interval −36.98 to 4.90. The original thresholds and exit definitions were retained.

The 64 dashboard factors have 35,348 stored observations, first captured on 24 October 2026 and last captured on 1 November. A June reporting date does not make a record available in June. The panel requires both observation and reporting timestamps to precede the decision, then resolves revisions. Availability age, reported-data age and revision identity are preserved. Only ten replay sessions have any prior captures; some values are stale after collection stopped.

Consequently broad 2025–2026 PCR, IV, max-pain, cash-flow or macro ablations would require missing information. Their captured values are exported for inspection, with freshness flags, but were not inserted retrospectively into earlier trades. Sector breadth additionally requires dated constituents and weights. [Feature report](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/feature-report.md), [SQLite feature panel](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/feature-panel.sqlite).

## 4. Actual historical option premiums

The NSE archive supplied a permitted alternative to Upstox's expired-instrument entitlement. The retained archive covers 13 October 2025–23 October 2026. I downloaded 93 additional official entry-day source files and used dated exit records already retained by the project.

Contract choice was frozen using each signal day's actual listed contract universe and underlying closing level. Comparisons used ATM versus one listed strike ITM, and nearest expiry surviving the fixed exit versus a month-end expiry proxy. Expiry had to be strictly after exit. Identity and dated lot size had to remain unchanged. The month-end label is inferred from the last listed expiry in its calendar month; it is not an independently reconstructed contract classification.

Of 1,085 frozen daily signals across the full earlier study, 106 fit this source window. Four policies produced 424 rows, representing **374 distinct signal/contract outcomes within strategies**; 50 rows duplicate the same contract across expiry policies. Strategies can also overlap. These cannot be pooled as 424 independent trades or added into one account return.

Entry uses each option's first-trade daily open and exit its official daily closing value. **These are asynchronous price proxies.** The first trade need not occur at the underlying open, and the closing value need not be an executable exit. Entry/exit full-day volume checks are retrospective coverage checks, not decision-time filters; all 424 passed in this sample.

Both modeled net scenarios deduct dated sale STT, with the rate change from 0.10% to 0.15% on 1 April 2026. The illustrative scenario also subtracts two premium points plus ₹100 per round trip; the severe scenario subtracts five points plus ₹200. These allowances represent other fees/execution sensitively, not a fully reconstructed statutory charge or historical spread schedule. The date-specific STT protocol was updated during source download before premium results were viewed. [Official NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).

|Daily family / contract policy|Trades|Illustrative net ₹ per dated lot|Severe net ₹ per lot|95% month-block interval, illustrative net|
|---|---:|---:|---:|---|
|EMA, nearest ATM|28|−3,746|−4,052|−8,605 to 94|
|Donchian, nearest ATM|9|−3,900|−4,201|−7,720 to −13|
|Momentum, nearest ATM|42|−3,984|−4,286|−9,743 to 1,508|
|RSI, nearest ATM|27|−398|−700|−1,859 to 1,571|
|RSI, month-end proxy ATM|27|107|−195|−1,183 to 1,727|
|RSI, month-end proxy ITM|27|415|114|−1,193 to 2,417|

All EMA, Donchian and momentum contract-policy means were negative after illustrative costs. RSI's positive variants have intervals spanning losses and gains. They do not establish a winner. All 16 groups, accepted/rejected policy rows, source hashes, exact identities and dated lot sizes are disclosed. No premium result was used to retune the underlying signals. [Daily premium report](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/option-premium-report.md), [full premium ledger](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/option-premium-trades.csv).

## 5. Recent intraday option diagnostic

The five sessions from 2–6 November were tested separately using the frozen intraday shortlist. The prior completed session's official NSE universe determined eligible contracts. Signal-time underlying close selected ATM/ITM strikes. Current Upstox instrument keys were accepted only when token, expiry, strike and option type matched exactly. Missing expired mappings were rejected rather than replaced with another expiry.

Seventeen signals produced 68 fixed policy attempts; 62 had complete positive-volume entry/exit candle evidence and six lacked exact current mappings. These are still candle-price proxies without bid/ask or precise option-trade timestamps. The study excludes same-day expiry from its nearest-expiry policy. The volume checks are retrospective coverage requirements.

All twelve group averages were positive, on only four to seven trades each. For example, EMA nearest ATM returned +₹2,427 illustrative net per lot on six trades, or +₹2,132 in the severe scenario. Its month-end ATM comparison returned +₹1,718 / +₹1,423 on seven trades. Pullback nearest ATM returned +₹2,611 illustrative net on four trades.

This is consistent with the strong underlying trend week already observed in phase one. It is a useful data-access and replay demonstration, with **no confidence or profitability claim** from five sessions. The positive week cannot override the weak broader index evidence or validate year-round option expectancy. [Recent intraday premium report](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2/option-intraday-report.md).

## 6. Forward observation and execution readiness

The bounded capture collected eight ATM/ITM CE/PE contracts across nearest and monthly expiries, with exact metadata, bid/ask, quantities, quote time, last-trade time, raw response, Greeks and market status. The exchange was in `CLOSING_END`; no quote qualified. The journal recorded eight abstentions and zero fills.

The journal is deliberately an observation/decision store. An eligible quote proxy is not automatically a fill. HTTP feed-update or last-trade timestamps do not independently establish a fresh exchange-depth event timestamp. Future quote observations need that distinction preserved; stale trades, spread/depth problems and missed signal times remain explicit rejection reasons. [Upstox full quote fields](https://upstox.com/developer/api-documentation/get-full-market-quote/).

The versioned policy allowlists the frozen rules, requires exact completed-bar timing and integer direction, checks quote ages, depth, spread and expiry, and enforces the 15:10 research exit boundary. It is idempotent within a policy version. Earlier policy observations remain stored when policy logic changes. Synthetic in-memory checks cover duplicates, closed markets, future signals, invalid rules/sides, malformed expiry and exits beyond the boundary; they are not included as real market outcomes.

One capture cannot establish forward performance. The existing app's daily paper marks and credit-spread accounting also cannot supply missing long-option executions. A future long-option paper adapter needs a stream of actual signal-time quotes and exit observations, dated total charges and a predeclared review sample. Account sizing and protective exits can then be designed using measured premium behavior.

## What remains unavailable or inherently unfinished

|Requirement|What was tried|Remaining boundary|
|---|---|---|
|Broad expired intraday option history|Upstox entitlement rechecked; NSE daily archive used instead; active contracts mapped exactly|Upstox still returns Plus-required `UDAPI1149`; daily files do not recover intraday books|
|Alternate broker dataset|Tapetide endpoint probed using configured access|HTTP 200 contained `data:null` and an API-not-in-plan notice; it is not usable data|
|Historical bid/ask, depth, trade latency and Greeks|Current read-only quote/Greek capture; raw option candles and NSE EOD prices retained|No broad historical quote stream; no fully executable premium backtest or IV/theta attribution|
|Long-history PCR/OI/IV/macro/sector features|All stored revisions audited with real availability gates|Capture window is short; delayed release times and historical constituents are missing|
|Event-specific model across RBI/Budget/news conditions|Coverage/availability audit; volatility and gaps tested as observable context|No point-in-time event/news calendar in the frozen dataset; realized surprise cannot be inserted before announcement|
|Prospective paper validation|Bounded actual quote capture and durable abstention journal|Future sessions have not happened; performance cannot be manufactured by a retrospective rerun|

Missing data is not a reason to call an untested strategy profitable. It is also not evidence that no strategy could ever work. The justified operational conclusion is to retain the frozen shortlist as research candidates and allow abstention until actual execution evidence and new outcomes support promotion.

## System specification supported by this work

Use completed price data to classify an eligible trend state, then apply a fixed trigger and deterministic router. Select the exact contract using information available then. Check source timing, market state, expiry, quote freshness, spread and depth; record every signal and rejection. Evaluate options using actual bid/ask and dated costs when available. Keep parameter changes out of a sealed evaluation period.

Range, gap, news and uncertain states have no positively validated policy here. The system can abstain in those states. A professional interface can expose price context, positioning context and data quality, but it should not turn an unvalidated collection of green indicators into a trade recommendation. A new combination is a new experiment and requires its own evaluation.

## Reproduce and verify

Outputs are in [the phase-two research directory](C:/Users/ME/Desktop/trading-desk/artifacts/directional_research_phase2). Source archives, selections, rejections, trade ledgers, provenance and standalone reports are retained. Replay commands use frozen files; fetch/capture commands require the configured provider access.

```powershell
.\.venv\Scripts\python.exe scripts/research_stronger_controls.py --extra artifacts/directional_research_phase2/expanded-nifty-5minute.json --label expanded
.\.venv\Scripts\python.exe scripts/build_research_features.py
.\.venv\Scripts\python.exe scripts/research_long_horizons.py
.\.venv\Scripts\python.exe scripts/research_option_premiums.py
.\.venv\Scripts\python.exe scripts/research_intraday_premiums.py
.\.venv\Scripts\python.exe scripts/research_shadow_journal.py --self-test
.\.venv\Scripts\python.exe scripts/plot_research_phase2.py
.\.venv\Scripts\python.exe scripts/verify_research_phase2.py
```

To obtain a new bounded forward observation and record it:

```powershell
.\.venv\Scripts\python.exe scripts/capture_option_research.py
.\.venv\Scripts\python.exe scripts/research_shadow_journal.py
```

Without a separately supplied contemporaneous signal file, this records observations and abstentions. It does not send broker orders or create profits from historical quote timestamps.

Completed validation includes 35,265 expanded-control assertions; four long-horizon feature-prefix checks and 154,236 trade assertions; 13 contextual availability/source checks; 1,272 daily premium assertions; 248 recent intraday premium checks; journal timing/idempotency cases; and independent source/ledger review of the daily premiums and control studies. Hashes and script versions are retained. These checks support implementation consistency, not a promise of future returns.

The final persisted-output audit verifies 261 previously recorded source hashes and reconciles panel sizes, SQLite counts, premium groups, duplicate policies, prior-day universes, journal outcomes and local links. Its results and full source/output inventory are in `phase2-verification.json` and `phase2-manifest.json`.
