# Findings: morning NSE stock momentum

**Result: no configuration qualified for paper-bot selection.** All ten primary long-only configurations, both exhaustion diagnostics, and all twelve hypothetical long/short configurations lost money over the complete study window.

Study: **14 November 2024–13 November 2026**, 495 market sessions. Fixed October 2024 500-name fund-holdings cohort, with 496 names having available daily history. Acquired 7,343,068 authentic Upstox five-minute bars in 4,855 source jobs. Loaded 4,293/4,300 possible mover stock-days; seven short afternoon-only sessions contain no morning entry window. Every loaded candidate has 18–20 valid prior same-clock volume histories.

₹10 lakh initial cash, whole shares, no leverage, up to three entries per day across all stocks, one open position, 1% target, 60-minute maximum holding period, 09:30–11:30 entries. Quantity uses prior completed volume and stop-risk/cash limits. Baseline uses 10 basis points adverse slippage on each side plus modeled Indian intraday charges. Stress uses 25 basis points on each side.

## Full-period descriptive ranking

Ranked by full-period funded return. The two exhaustion rows were excluded from primary selection in advance; their lower activity and smaller total losses do not establish better per-trade edge. Every row has negative mean net basis points per trade. The volume-gate ablations produced identical primary trades to the corresponding 8% rules in this sample.

| Rank | Configuration | Stop | Trades | Net return | Net P&L | Profit factor | Net bps/trade | EOD max drawdown | 25bps/side return |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8% exhaustion / rejection (diagnostic) | 1% | 80 | -6.40% | ₹-64,035 | 0.62 | -20.03 | 6.40% | -14.53% |
| 2 | 8% exhaustion / rejection (diagnostic) | 0.5% | 81 | -8.59% | ₹-85,911 | 0.58 | -17.75 | 9.61% | -21.31% |
| 3 | 10% mover + RVOL/VWAP | 1% | 417 | -20.88% | ₹-208,792 | 0.76 | -14.58 | 21.67% | -47.89% |
| 4 | 8% mover + VWAP reclaim | 1% | 170 | -23.65% | ₹-236,497 | 0.45 | -38.78 | 23.73% | -31.66% |
| 5 | 8% mover + VWAP reclaim | 0.5% | 173 | -32.96% | ₹-329,610 | 0.36 | -32.38 | 32.96% | -40.76% |
| 6 | 8% mover + RVOL/VWAP | 1% | 741 | -41.42% | ₹-414,219 | 0.70 | -18.76 | 41.67% | -75.55% |
| 7 | 8% mover, volume gate off | 1% | 741 | -41.42% | ₹-414,219 | 0.70 | -18.76 | 41.67% | -75.55% |
| 8 | 8% mover + 3-bar breakout | 1% | 732 | -50.31% | ₹-503,071 | 0.60 | -23.51 | 50.35% | -77.71% |
| 9 | 10% mover + RVOL/VWAP | 0.5% | 426 | -54.15% | ₹-541,525 | 0.49 | -26.85 | 54.45% | -74.90% |
| 10 | 8% mover + 3-bar breakout | 0.5% | 743 | -77.39% | ₹-773,916 | 0.40 | -32.03 | 77.43% | -91.28% |
| 11 | 8% mover + RVOL/VWAP | 0.5% | 776 | -80.00% | ₹-800,031 | 0.40 | -31.80 | 80.04% | -92.69% |
| 12 | 8% mover, volume gate off | 0.5% | 776 | -80.00% | ₹-800,031 | 0.40 | -31.80 | 80.04% | -92.69% |

## Chronological check

Development (14 November 2024–31 August 2025) selected **none**: no primary model had positive mean net bps/trade with at least 50 closed trades. No later-period replacement was promoted. All primary configurations also lost in validation (September 2025–February 2026), final (March–13 November 2026) and the trailing-year slice (14 November 2025–13 November 2026). These periods appeared in earlier project research, so the later periods are pseudo-out-of-sample evidence.

The least-loss full-period primary rule was the 10% mover with a 1% stop: **−20.88%**, 417 trades, profit factor **0.76**, EOD maximum drawdown **21.67%**. It returned **−19.84%** over the trailing year and **−16.67%** in the final period. Its full-period 25bps/side stress return was **−47.89%**.

For that rule, the same fixed entries and quantities have ₹190,513 of gross price-path P&L before slippage, offset by ₹322,769 modeled slippage and ₹76,536 fees, leaving **−₹208,792 net**. This arithmetic is a cost attribution for the fixed trades, not a separate zero-cost portfolio backtest. Only 5/417 trades have unresolved five-minute stop/target dual touches; ambiguity alone is not an explanation for the overall result.

## The 8→10 and 10→12 claims

For upward moves, within 60 minutes of the first qualified morning observation:

| Daily-return extension | Eligible races | Extension before 1% reversal | 1% reversal first | Neither | Entry already beyond extension, excluded |
|---|---:|---:|---:|---:|---:|
| 8% → 10% | 1024 | 360 (35.2%) | 528 (51.6%) | 136 (13.3%) | 127 |
| 10% → 12% | 433 | 197 (45.5%) | 196 (45.3%) | 40 (9.2%) | 69 |

The extension is two percentage points of daily return, measured from the prior close; the competing reversal is 1% from raw next-open entry. These have different and entry-dependent distances. Outcomes use conservative reversal-first ordering for ambiguous candles. Rates are conditional descriptive price paths, without transaction costs, and are not strategy win rates. Stock-day events, thresholds and horizons are dependent.

## Interpretation and next research

The tested mechanical version does not justify a paper bot yet. A discretionary trader may add selection, timing or depth information absent from the supplied post; the screenshot supplies no audited rule set or full tradebook.

A separate next protocol could test earlier momentum detection and collect live spread/depth observations to measure whether tiny target exits are practical. It should use a newly frozen search and fresh forward observations. Re-optimizing these stops or thresholds on the inspected final period would weaken the evidence.

The four-percent control remains NOT_TESTED_DATA_COVERAGE because the 8% download superset cannot evaluate it independently. No one-minute audit or selected-model bootstrap was triggered: there was no development-selected candidate. No bot was created and no real orders were submitted.

## Verification and limits

66 synthetic regression tests passed before returns. Post-run verification reconciled all 24 base cash ledgers, fees and summaries; all source/code hashes matched. The audit reported zero failed execution configurations. Historical spreads, circuits, queue position, broker intraday eligibility and short availability remain unverified. Daily/intraday source checks found no missed 8% close qualification within 90,776 observed complete stock-days; four unavailable cohort members and unacquired months remain coverage limitations.

Original Upstox candles remain unmodified in PostgreSQL. Share-unit reconstruction, NSE evidence, community text and results are local. Primary source references are in `research/intraday_momentum/SOURCES.md`.

Full chronological tables and event counts: `REPORT.md`. Machine-readable outputs: `report.json`, `summary.csv`, `stress.csv`, `trades.csv`, `daily-equity.csv`. Frozen source/code lineage: `research-manifest.json`, `development-selection-frozen.json`, `plan-amendment.json`.
