# Phase 2 findings: no strategy qualified

**Decision: NO STRATEGY QUALIFIED.** No primary configuration had positive development expectancy; no later-period replacement was promoted. All 30 base portfolios lost over the complete window, including controls and hypothetical shorts. All 12 primary portfolios also lost in both 5bps and 25bps all-in friction scenarios, and every predefined full-period latency/capital/participation scenario remained negative.

## What was actually tested

Only **1 January 2025–13 November 2026** contributed performance or model-selection observations; 2024 was universe/indicator warmup. The dated 500-company cohort was ranked using liquidity known at the end of 2024; its top 100 liquid names were frozen before 2025. We acquired complete December 2024–November 2026 months for all 100 plus NIFTY, without any end-of-day mover screen. This removes the old 8%-conditioned acquisition bias for earlier signals within this cohort, while retaining fixed-cohort/survivorship/identity limitations.

All **2,424 source jobs** completed successfully, containing **3,661,321 authentic Upstox five-minute observations**, including 579 exact reused jobs. PostgreSQL supplied all candle runtime inputs. The loader accepted **45,740/45,939 eligible stock-days**. The 199 exclusions were afternoon-only special sessions: 100 on 21 October 2025 and 99 on 8 November 2026. Every admitted stock-day had 18–20 prior same-clock RVOL histories. No additional stock-days were dropped for missing NIFTY context. The calendar contains 464 exchange sessions and 462 regular sessions represented in the signal panel.

The budget was 12 primary long-only rules (four mechanisms × three exits), four ablations, two common-cohort v1-style baselines and 12 hypothetical short-only diagnostics: **30 base configurations**, plus **72 nonselectable stress scenarios**. A separate three-model depth feasibility experiment uses one archived stock-day. There were **16,154 generated signal rows** across mechanisms/directions/controls; those are dependent opportunities, not independent statistical observations.

Every portfolio started with ₹10 lakh, no leverage, whole shares, at most three shared entries per day and one simultaneous position. Risk allowances were 0.5% per position and 1% daily, with cash, fees and prior completed volume restricting quantity. Orders used next-open modeling, an adverse chase limit, conservative stops/gaps and forced intraday exits. Baseline friction was 10bps per side, modeled as all-in spread/adverse-selection/impact plus statutory/brokerage fees; it is not an observed universal execution rate.

## Primary configurations ranked by complete-window net return

Ranking here is descriptive. A smaller loss from infrequent trading does not establish better expectancy. No rule met development selection.

| Rank | Mechanism | Exit | Trades | Active sessions | Net return | PF | Net bps/trade | EOD drawdown |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Failed-breakout reversal | ATR stop / trailing / 2% target | 48 | 37 | -6.27% | 0.20 | -29.70 | 6.45% |
| 2 | Failed-breakout reversal | Swing stop / 2R bounded target | 54 | 40 | -7.13% | 0.18 | -29.15 | 7.37% |
| 3 | Persistent extreme mover | Swing stop / 2R bounded target | 81 | 67 | -9.04% | 0.52 | -22.25 | 9.46% |
| 4 | Failed-breakout reversal | 0.5% fixed stop / 1% target | 60 | 46 | -9.85% | 0.12 | -38.07 | 9.94% |
| 5 | Persistent extreme mover | ATR stop / trailing / 2% target | 91 | 72 | -14.01% | 0.47 | -22.00 | 14.72% |
| 6 | Persistent extreme mover | 0.5% fixed stop / 1% target | 110 | 80 | -17.07% | 0.47 | -21.66 | 19.57% |
| 7 | Early ignition | Swing stop / 2R bounded target | 312 | 260 | -25.14% | 0.55 | -18.37 | 25.70% |
| 8 | Early ignition | ATR stop / trailing / 2% target | 374 | 302 | -39.23% | 0.47 | -26.24 | 41.38% |
| 9 | Controlled pullback | ATR stop / trailing / 2% target | 698 | 333 | -57.37% | 0.47 | -23.73 | 58.39% |
| 10 | Controlled pullback | Swing stop / 2R bounded target | 758 | 340 | -61.99% | 0.43 | -22.98 | 62.58% |
| 11 | Early ignition | 0.5% fixed stop / 1% target | 617 | 328 | -65.03% | 0.45 | -24.89 | 65.15% |
| 12 | Controlled pullback | 0.5% fixed stop / 1% target | 835 | 346 | -72.09% | 0.38 | -24.10 | 72.42% |

The least-loss primary, failed-breakout reversal with the ATR/trailing exit, lost **6.27%**, but traded only 48 times and had PF **0.20** and **−29.70bps/trade**. It is not the best economic edge. The least-negative primary mean net expectancy was early ignition with a swing stop: **−18.37bps/trade**, 312 trades, **−25.14%** funded return and PF **0.55**. It lost **13.47% even at 5bps/side** and **48.02% at 25bps/side**. Its evaluation-period 20-session-block conditional 95% return interval was **−15.04% to −4.31%**; this is conditional on exposed data/model assumptions, not a fresh-market forecast.

## Cost and failure mechanisms

For early ignition/swing exit, the same fixed trades generated **₹67,590 gross before slippage**, with **₹258,400 modeled slippage** and **₹60,547 fees**, producing **−₹251,358 net**. Mean gross movement advantage was only **6.35bps**, against approximately **19.99bps friction + 4.73bps fees**. The observed gross advantage was much too small for those costs. This attribution is not a separate zero-cost portfolio backtest.

Early ignition/fixed exits produced 365 stops, 154 time exits and only 98 targets across 617 trades. The structural exit had 183 time exits, 77 stops, 34 momentum-failure exits and 18 targets. Controlled pullback/swing had 269 stops, 248 time exits, 153 momentum-failure exits and 88 targets. These are observed exit distributions, not proof that every losing trade was identifiable beforehand. Mechanical trend/volume conditions frequently failed to produce enough subsequent displacement within the holding window.

## Answers to the twelve research questions

1. **Best stage of entry:** no profitable stage was established. Early ignition/swing had the least-negative primary mean expectancy; it still lost. Within that model, entries below 3% had −15.88bps versus −23.96bps at 3–5%, but both were negative and those post-hoc buckets cannot select a new rule.

2. **Early momentum versus spikes:** the predefined opening-range breakout, acceleration, candle-location, VWAP, RVOL and market-relative filters did not create positive net expectancy. This rejects those specific mechanical combinations under the tested assumptions, not the general possibility of separating the regimes.

3. **Depth increment:** actual retained RELIANCE data from 13 November 2026 supported 29,563 in-window updates, 206 training episodes and 199 later test episodes. Receipt-time-corrected price/volume/depth MAE was **2.266bps**, versus **2.293bps** for price+volume; prediction/target correlation was only **0.0137**. Directional accuracy was **53.77%**, close to the test set’s **53.27% non-up frequency**. None of the three models generated a long quote-markout clearing the predefined cost/buffer threshold. There is one independent stock-day and only **85.9%** fresh-grid coverage, below the proposed 95% forward coverage gate. This is insufficient for a predictive or profitable-depth conclusion. H3 remains FORWARD_DATA_REQUIRED.

4. **Recognising exhaustion:** persistent-extreme long variants and failed-breakout reversals remained negative. The latter’s low total losses came with few trades and poor per-trade economics. We have no validated causal exhaustion classifier. Do not infer individual orders or cancellations from displayed snapshot changes.

5. **Market and sector confirmation:** H1 fixed with the peer proxy lost **50.43% on 381 trades**, compared with **65.03% loss on 617 trades** for the base, but net expectancy worsened from **−24.89 to −25.47bps**. The apparent NAV improvement reflects lower activity, not demonstrated stronger edge. Removing market confirmation produced **−70.11% on 747 trades**, with **−24.19bps/trade**; the market filter reduced activity without demonstrating superior net per-trade expectancy. Only the documented peer proxy was tested, not actual historical sector indices.

6. **Pullback versus chasing:** controlled pullback/swing lost **61.99% and −22.98bps/trade**, versus early ignition/swing **25.14% loss and −18.37bps/trade**. These are different entry populations and cash paths, so this does not isolate a pure causal benefit of pullbacks. No pullback implementation qualified.

7. **Movements large enough for costs:** target distance is not realized mean advantage. The early/swing model needs roughly **24.72bps gross average advantage** for its modeled round-trip costs, while observing only **6.35bps**. Fixed 1%, structural 0.75–2% and ATR/trailing 2% objectives did not yield adequate net expectancy. An accurately forecast price direction at a 30-second horizon is economically insufficient when its expected move is only a few basis points.

8. **Long versus short:** every hypothetical short portfolio also lost at the baseline. The closest to breakeven was persistent-extreme/ATR short: **−2.84%**, **−2.91bps/trade**, 48 trades and 37 active sessions. It is a sparse, ineligible diagnostic, not a paper candidate; lower-cost hypothetical arithmetic would not establish broker eligibility or a new selected rule. No conditional bidirectional meta-strategy was trained or validated.

9. **Recognisable causes of losers:** cost drag and failure to reach targets are observable aggregate causes. Trend/market/volume conditions did not reliably eliminate them. Removing H1’s volume gate increased activity to 820 trades and worsened funded loss to **70.17%**, although mean net expectancy became slightly less negative (**−23.18bps**); that does not establish the RVOL gate as a useful economic selector. Removing H2’s VWAP momentum-failure exit barely changed the swing model (**−61.88% versus −61.99%**). No post-hoc loser filter was promoted.

10. **Zero to three trades without forcing activity:** the simulator enforced this globally. Pullback/swing averaged **1.63 trades per calendar session**, or **2.23 per active session**, but lost money. Early/swing averaged **0.67 per calendar session**. Frequency targets cannot justify unprofitable activity. Sparse positive exploratory buckets, such as early/swing range-efficiency cases (15 trades), are insufficient and were not selected.

11. **Capital, size and latency:** every primary remained negative in the full-period ₹5lakh/₹20lakh, quarter-participation and additional-five-minute latency scenarios. Early/swing returned **−25.98%, −25.14%, −24.24%** at ₹5/10/20lakh. Quarter participation reduced NAV loss to **19.16%**, but mean net expectancy remained **−19.06bps**. Reduced deployment limits damage; it does not establish an edge. No leverage was used to rescue negative expectancy.

12. **Credible systematic edge versus new information:** none was demonstrated in the frozen candle search. That does not prove no NSE intraday edge exists. More threshold searching on this exposed history is not the next evidentiary step. Depth-based questions require better-covered, matched post-freeze observations, live execution calibration and eligibility evidence before a separately frozen next experiment.

## Execution and data qualification

The fixed first 20 chronological H1 fixed-exit development trades were audited using authentic Upstox one-minute candles. **20/20 matched; all had zero fixed-trade P&L difference** from the five-minute replay. This is a narrow path-resolution check, not validation of all fills or a one-minute portfolio. Historical queue position and partial fills remain unavailable. The current simulator assumes full modeled quantities once its candle conditions pass; it does not observe broker fills.

REST Full Quotes was verified for 100 names with five bid/ask array slots. WebSocket authorization returned HTTP401; no separate access credential is configured. Therefore neither streaming cadence nor D30 entitlement is verified. The bounded recorder was smoke-tested through its five-second REST fallback. Closed-session snapshots do not count as fresh forward trading evidence. Current-session metadata is separately archived by scripts/capture_intraday_metadata_v2.py. Today’s MIS/suspension lists must never be backdated into 2025 eligibility.

The current MIS file listed 99 of the 100 cohort keys, but the public suspended-instrument file unexpectedly contained all 100, including those MIS-listed names. Raw responses are retained. This conflicting broad overlap is **not interpreted as confirmation of either tradability or suspension**; it requires reconciliation before any execution eligibility decision. Existing workers were not altered based on these files.

## Integrity, limitations and deliverables

**83 regression tests passed.** A separate arithmetic audit reconciled all **30 base portfolios, 9,394 ledger rows and 120 summaries** with zero discrepancies (maximum numeric delta about2.1e−9), and checked completeness of **96 cost-stress rows and 192 capacity/latency rows**. Individual stress ledgers were not retained for independent fee-by-fee re-audit. Source, code and plan fingerprints match. There were no unresolved simulator runs and no missing market-context candidate days.

Only 2025–2026 performance is reported, but these dates are research-exposed. The liquid100 fixed cohort is not all NSE stocks; costs are scenarios rather than live-calibrated fills; peer labels are frozen industry metadata; ATR uses documented early-session warmup; and drawdown is EOD cash equity. All subgroup results are exploratory and dependent. Conditional block intervals and Bonferroni correction do not erase earlier research exposure.

An acquisition-manifest integration fault was fixed only in the v2 helper, recovering durable source logs/hashes; v1 frozen code/results were preserved. The first depth diagnostic used source time alone and was invalidated; corrected results use max(source_at,received_at). Both attempts and their reason for correction are preserved. No parameters or candidates were selected from evaluation-period returns.

The authoritative definitions/audit/capture plans are copied beside this file. BACKTEST_REPORT.md contains chronological primary tables; FINAL_DECISION.md classifies all rules. full-ranking.csv includes all controls/short diagnostics; metrics.csv, stress.csv, capacity-and-latency.csv and segments.csv provide comparisons. signals.csv, rejections.csv, trades.csv and daily-equity.csv preserve the ledgers. METRIC_NOTES.md explains modeled acceptance versus actual fill rates. Original Upstox candles remain raw in PostgreSQL; all reconstructions/results remain local. No paper execution bot or real orders were created, and existing F&O/investment bots and switches were unchanged.

## Forward collection commands

```powershell
.venv/Scripts/python.exe scripts/capture_intraday_metadata_v2.py
.venv/Scripts/python.exe -m research.intraday_momentum_v2.capture audit
.venv/Scripts/python.exe -m research.intraday_momentum_v2.capture record --seconds 3600
```

These explicitly bounded commands collect data only. No unattended service was installed. WebSocket access must be restored before streaming-depth validation; five-second REST snapshots are labeled separately and cannot recover event-complete order flow. The forward plan requires at least60freshsessions and adequate matched episode coverage. Future, uncollected observations remain a dependency, not a completed result.
