# Directional NIFTY research: project and prior-evidence audit

Audit date: 9 November 2026 (IST). This is a source/artifact audit, not a new market-data backtest. No application code or trading accounts were changed. Existing results below are explicitly historical and exploratory.

## What the project already contains

| Component | Useful inputs/outputs | Correct research role |
|---|---|---|
| `upstox_analytics.py`, `market_gateway.py`, `market_store.py`, SQL migrations | Historical and intraday OHLC/OI, contract identities, dated option analytics, durable raw responses, coverage metadata, cache statistics | Data acquisition and reproducibility; actual retention must be probed separately for each endpoint |
| `data_providers.py`, `tapetide_data.py` | Supported fallback quotes, candles and research datasets with provider attribution | Coverage fallback; do not silently splice providers into a single stationary feature series |
| `market_session.py`, `market_stream.py`, `market_stream_store.py`, `upstox_ws_v3.py` | Exchange session checks, received tick/chain history, source freshness and per-field provenance | Forward paper replay and freshness gates; collection exists only while the service runs and instruments are subscribed |
| `price_action.py` | 47 explicit OHLC concepts on 1m/5m/15m/30m/1h, `known_at` confirmation times, causal zones/levels, missing-bar checks | Main reusable intraday event engine; names such as order block/liquidity sweep are OHLC heuristics, not measured institutional order flow |
| `nifty_catalog.py`, `nifty_sources.py`, `nifty_analytics.py`, `nifty_service.py`, `nifty_store.py` | 127-factor research map; EMA9/21/50/100/200, RSI, MACD, ATR, realized volatility, gap and levels, sectors/breadth, global market proxies, cash flows, OI/PCR/IV, sourced macro imports | Regime/context candidates. The catalog is not 127 historically populated independent predictors |
| `nifty_max_pain.py`, `max_pain_service.py`, `pcr_service.py`, `volume_pcr.py` | Intrinsic payout minima, OI distribution/change, intraday OI PCR, separately captured cumulative volume PCR, historical session handling | Positioning context to test conditionally; payout minima are not price forecasts or directional option returns |
| `maxpain_greeks.py`, `iv_metrics.py`, `iv_service.py` | Retained/live option Greeks, same-strike ATM IV, expiry-specific IV rank/percentile and expected-move estimates | Contract/volatility context. Missing historical capture is a real data gap; current Greeks cannot be inserted into an old trade |
| `option_prices.py` | Exact daily option closes where available, explicitly dated carried-forward prices otherwise | Exploratory payoff illustration only when stale; actual trade evaluation must require valid contemporaneous premiums |
| `maxpain_study.py`, `run_maxpain_study.py` | One-year NSE official EOD archive study of frozen max-pain targets vs expiry close | Existing falsification/control study; not an option-strategy backtest |
| `analyze_47_concepts.py`, `verify_concept_research.py`, `artifacts/concept_research_2026-10-29/` | Event studies, chronological simple-model folds, proxy-volume features, cost sensitivities and causal checks | Strong starting harness for extending history and freezing hypotheses |
| `backtest_service.py`, frontend Backtests | Reads and normalizes JSON results from disk, charts reported metrics | A results viewer, not a general strategy engine. `sample-momentum-nifty.json` is sample data |
| `paper_service.py`, frontend Paper | Generic simulated orders and position accounting; marks use retained daily close then quote fallback | Interface/accounting scaffold; daily marks and explicit-limit fills are not realistic intraday option execution evidence |
| `credit_spreads.py`, frontend Credit Spreads | Exact contracts, fresh bid/ask checks, whole-lot/depth validation, adverse slippage, fees and durable transaction journal | Better execution/journal scaffold, but implements short credit spreads with manual confirmations; cannot be treated as a validated long-call/put bot |
| IPO services/pages | 24-company-research factors and subscription/GMP sources | Separate research product; no demonstrated incremental directional NIFTY feature here |
| Frontend NIFTY/Max Pain/charts/Data/Desk | Source-qualified visualizations, filters, capture timing, charts and coverage inspection | Research and operator UI. Chart marks and colored indicators are not independently validated trade decisions |

## Existing evidence: do not start the search from zero

### 47 concepts and model variants

Source: `FINDINGS_47_CONCEPTS_1M_5M_LAST_7_DAYS.md` and its archived `results.json`, features, events, prediction files and causal checks. Primary window: **23–29 October 2026 = five completed trading sessions**, with a seven-session sensitivity adding 21 and 22 October. Entry is next candle open after confirmation; primary horizon is 15 minutes, with 5/30-minute alternatives. Main analysis ends before 15:15 IST. Results are index points, not traded option returns.

| Candidate | Existing exploratory evidence | Qualification |
|---|---|---|
| 1m trendline break (#19) | N=54 nonoverlapping observations; 68.5% positive; +7.80 gross points/15m; +7.23 matched excess; seven-session mean +6.86 | BH q=.453; final day +4.38 points does not clear illustrative 5-point friction |
| 1m #19 + same-side EMA9/21 | N=24; 70.8% positive; +11.26 gross points; +3.52 matched excess; final day N=8, +8.51 | Post-selected extra variant, outside concept multiple-test correction; only 3/5 daily means positive; freeze before further evaluation |
| 1m CHoCH (#20) | N=37; +12.52 gross points/15m; same-cohort 5/15/30m means +0.92/+12.52/+22.44 | q=.408; final-day excess negative; slower reversal rather than immediate entry evidence; 5m version weak |
| 5m mitigation/retest (#47) | N=43; 60.5% positive; +8.95 gross points; +6.04 matched excess | q=.929; one day contributes more than pooled gain; seven-session mean +5.19 |
| 5m #47 + EMA agreement | N=32; +10.20 gross points; +6.76 matched excess | Post-selected; only 3/5 positive days and concentrated in 23 October |
| Opening-range breakout | 1m N=7, +32.93; 5m N=6, +34.75 gross points | Tiny sample, 26 October +132.80 outlier; negative matched excess and final-day 5m result -2.20 |
| BOS (#42) | 1m +10.09 gross points | Matched excess -4.37: largely market drift, not demonstrated timing skill |
| Displacement/FVG | 5m displacement -17.03, N=11; standalone FVG roughly flat or below drift | Chasing the large trigger bar was weak. Fading displacement is another post-hoc small-sample hypothesis, not a discovered reliable edge |

The archived study's overall conclusion is **no robust predictor established**: no eligible concept q<.05, and all tested ML strategies lose after its illustrative 2-point friction. Best ML gross mean was +1.01 points (1m) / +0.83 (5m). An always-up directional-drift benchmark beat reported model accuracy in the held-out dates. Mandatory RVOL and generic multi-timeframe agreement did not improve the simple setup rule. An indiscriminate all-47 voting composite has no supporting evidence here.

Positive integrity features: 48/48 prefix checks passed; pivots are timestamped only after confirming bars; model preprocessing uses training data; train/test boundaries are whole sessions; trades are deoverlapped per holding window; circular-shift and BH diagnostics are reported. Limits remain: five main days, only three forward model test days, overlapping information across related strategies, assumptions of immediate close availability, no premium/bid-ask execution, and data-driven follow-up variants.

### One-year max-pain study

Source: `backtests/max-pain-convergence-1y.json`, generated 25 October 2026. Research interval 25 October 2025–24 October 2026; **255 archived NSE EOD files** (including warmup dates), 246 NIFTY price sessions and 53 identified NIFTY expiries. This already disproves the idea that all useful project history consists of only seven days.

Primary group (T-1 frozen target, expiry-day open to close, initial target distance ≤1%, strict call/put coverage) across assets: N=73, closer-to-target rate 35.62%, equal-distance opposite-target control 36.99%. Difference -1.37 percentage points; expiry-cluster bootstrap difference interval roughly [-23.94, +20.00]. **NIFTY alone: N=45, convergence 24.44%, mirror control 37.78%, directional movement toward target 42.22%.** Its intraday range reached the target 62.22% of the time, which does not imply profitable entry/exit timing. A target touch and a good option trade are different outcomes.

The artifact explicitly excludes premiums, fees, slippage, margin and exact settlement differences. No simple "NIFTY must move to max pain" buying strategy is supported. Other horizons/proximity subsets are exploratory and cannot be cherry-picked without fresh data.

## Critical backtest boundaries

1. **Preserve information time.** `nifty_store.latest()` and `nifty_service.latest_revisions()` choose current/latest revisions. They are suitable for a dashboard but not point-in-time features. Historical replay must select records actually available by the decision (`observed_at` as well as a credible publication time), before resolving revisions. A historical reported date does not prove historical availability.
2. **No same-day closing data before the close.** Daily candles, cash flows, final OI and global closes must enter only after their actual release/availability. Midnight date anchors are labels, not tradable release times. Current constituent membership cannot reconstruct historical breadth or weights without survivorship bias.
3. **NIFTY spot volume is not traded volume.** Prior sample had no positive index volume. Existing code correctly rejects index VWAP/volume claims. Use identified futures/ETF volume; the prior NIFTYBEES RVOL compares with a preceding rolling median, not same-time-of-day historical volume. Candle-signed volume is not aggressor flow.
4. **Use exact contracts and capture times.** OI PCR, volume PCR and IV have different collection/retention paths. Dated OI and candle closes cannot reconstruct historical Greeks or bid/ask. Session-final retained chain snapshots must not be reused earlier in that session.
5. **Reject stale trade prices.** `historical_premiums()` may carry closes forward up to 365 days and flags them. These are unsuitable entry or exit fills even if a payoff diagram is drawable. Require an option observation at the chosen time, with trade volume/freshness and conservative bid/ask/spread treatment.
6. **Do not mistake an index result for option expectancy.** Long calls/puts need direction, magnitude, timing, premium, IV movement and time-to-expiry. Fixed delta times spot change is only an approximation and cannot validate large/near-expiry returns. Even with sizing postponed, costs and entry/exit definitions are part of measuring the edge.
7. **Replay confirmation delays faithfully.** Swing labels lag by two closed bars. ORB waits for a complete range. Multi-timeframe joins use only completed higher-timeframe bars. Stop/target paths inside a single candle need conservative resolution or finer bars.
8. **More bots do not create more independent evidence.** Keep a complete experiment ledger; use nested chronological selection, day/week-level uncertainty and a sealed later holdout. Related rules on the same five sessions are one search with multiple trials, not independent confirmations.
9. **Regimes must be classified prospectively.** A day's eventual trend/range is a future label. Only classify using prior-session context and information observed by entry; retain an explicit uncertain/no-trade state.
10. **Separate scope.** Credit-spread account rules describe short-premium strategies; they cannot justify buying naked directional options. IPO statistics are not substitutes for missing NIFTY directional data.

## Small, testable research slate

These are hypotheses to register before new testing, not recommended live trades.

| Market state using information known by entry | Entry family to compare | First useful comparison |
|---|---|---|
| Sustained directional movement; completed EMA9/21 agreement | Confirmed 1m trendline break, with and without EMA filter; later pullback/retest | Unfiltered #19, simple same-side momentum and identical-time drift baseline |
| Break of established structure after opposite trend | 1m CHoCH; optional subsequent retest | Fixed 15/30m exits, adverse excursion and reversal continuation vs immediate chase |
| Repeated failed range breaks / weak trend | Sweep or false break of an already known PDH/PDL/OR boundary, followed by reclaim | Plain range fade; decompose reversal triggers from volatility regime |
| Compression followed by observed expansion | ORB/compression breakout, with and without retest | Standalone breakout versus delayed retest; test whether delay removes payoff |
| Overnight gap aligned/opposed to prior trend | Opening gap continuation versus reclaim/fade | Same rule/time/exit with direction flipped; separate gap sizes fixed from training |
| Expiry approaching, expensive IV or uncertain event timing | Compare same directional trigger in nearer weekly vs later expiry contracts, or abstain | Exact contemporaneous premiums; compare spot skill with option net expectancy |

Start with a compact parameter grid, then test a predeclared second-stage conditional model only if basic rules survive out-of-time evaluation. Treat PCR/OI change, IV/skew, VIX, proxy activity, sectors and prior-day cash flow as **incremental ablations**, not mandatory confirmations. Prefer a small stable rule that survives later sessions over the highest retrospective return.

## Implementation priorities

1. Reuse the causal event engine and existing research harness; freeze data manifests, timestamps, hashes, rule versions and experiment IDs.
2. Audit actual historical availability per instrument/interval/contract and preserve an untouched newer test period. Monthly directional holds need considerably more calendar history than intraday studies.
3. Build a point-in-time feature panel; distinguish directly observed historical values, reconstructed candle features, delayed publications and missing captures.
4. Evaluate direction/magnitude with simple baselines first; then join eligible exact option contracts at next-bar execution times and report premium P&L separately.
5. Only survivors enter a forward paper journal with rejected signals, quoted spreads, timestamps and realized fills. The existing credit-spread journal/freshness patterns are reusable, but long-option orders require their own execution semantics.
6. Extend across trend, range, gap, event and volatility conditions. An all-condition system can deliberately abstain; it need not produce a trade every day.

No existing artifact establishes a deployable money-making system. The repository has substantial data/provenance infrastructure and a useful falsification baseline; the strongest next step is disciplined fresh-history testing of a few frozen hypotheses.
