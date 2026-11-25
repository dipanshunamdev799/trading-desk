# Morning stock momentum research

**Research only. No intraday bot was created or started.**

Study: 14 November 2024–13 November 2026. Dated 500-stock fund cohort; prior-only liquidity, as-of-time ≥8% movers, same-clock RVOL, VWAP and next-open entries. ₹10 lakh cash, up to three trades/day across all stocks, one position at a time.

Development-selected primary rule: **none qualified**. Paper-candidate evidence gate: **False**.

Selection uses positive development mean net bps/trade with ≥50 development trades; no validation/final replacement is selected.

| Rule | Dev trades | Dev return | Validation return | Final trades | Final return | Final PF | Final net bps/trade | Final EOD drawdown | Final 25bps return |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cross10-sl100-long_only | 176 | -5.04% | -0.01% | 163 | -16.67% | 0.57 | -27.62 | -17.30% | -26.84% |
| cross8-sl100-long_only | 311 | -18.62% | -6.29% | 287 | -23.19% | 0.63 | -23.49 | -23.47% | -44.19% |
| cross8_no_volume-sl100-long_only | 311 | -18.62% | -6.29% | 287 | -23.19% | 0.63 | -23.49 | -23.47% | -44.19% |
| cross10-sl50-long_only | 181 | -22.11% | -13.69% | 166 | -31.80% | 0.36 | -33.17 | -32.68% | -43.64% |
| vwap_reclaim8-sl50-long_only | 61 | -11.11% | -5.89% | 79 | -19.86% | 0.27 | -38.13 | -19.86% | -23.34% |
| cross8-sl50-long_only | 325 | -45.69% | -29.00% | 302 | -48.14% | 0.37 | -34.28 | -48.14% | -64.58% |
| cross8_no_volume-sl50-long_only | 325 | -45.69% | -29.00% | 302 | -48.14% | 0.37 | -34.28 | -48.14% | -64.58% |
| breakout8-sl100-long_only | 307 | -32.57% | -3.89% | 277 | -23.32% | 0.62 | -23.55 | -23.60% | -42.93% |
| vwap_reclaim8-sl100-long_only | 60 | -7.42% | -5.17% | 77 | -13.03% | 0.41 | -42.35 | -13.03% | -17.08% |
| breakout8-sl50-long_only | 311 | -48.42% | -23.06% | 283 | -43.03% | 0.41 | -32.31 | -43.03% | -61.45% |

## Interpretation

- No primary model met the preregistered development-only eligibility rule

## Fixed-entry one-minute audit

No development-selected trades were available for the fixed chronological audit.

## Descriptive 8→10 / 10→12 extension events

First completed morning qualification per stock-day/threshold/direction with RVOL≥1.5, including gappers. The race starts at the raw next open: extension is two percentage points of daily return from the prior close; the competing reversal is 1% against that entry. These are price paths, not trade returns.

| Daily-return step | Direction | Horizon | Qualified | Races | Extension first | Reversal first | Neither | Excluded: overshot / missing / censored | Ambiguous |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| -8%→-10% | down | 60min | 397 | 350 | 100 (28.6%) | 179 (51.1%) | 71 (20.3%) | 47 / 0 / 0 | 2 |
| 8%→10% | up | 60min | 1151 | 1024 | 360 (35.2%) | 528 (51.6%) | 136 (13.3%) | 127 / 0 / 0 | 17 |
| -8%→-10% | down | 15:10 | 397 | 350 | 111 (31.7%) | 225 (64.3%) | 14 (4.0%) | 47 / 0 / 0 | 2 |
| 8%→10% | up | 15:10 | 1151 | 1024 | 417 (40.7%) | 575 (56.2%) | 32 (3.1%) | 127 / 0 / 0 | 17 |
| -10%→-12% | down | 60min | 152 | 98 | 42 (42.9%) | 46 (46.9%) | 10 (10.2%) | 54 / 0 / 0 | 2 |
| 10%→12% | up | 60min | 502 | 433 | 197 (45.5%) | 196 (45.3%) | 40 (9.2%) | 69 / 0 / 0 | 12 |
| -10%→-12% | down | 15:10 | 152 | 98 | 47 (48.0%) | 48 (49.0%) | 3 (3.1%) | 54 / 0 / 0 | 2 |
| 10%→12% | up | 15:10 | 502 | 433 | 220 (50.8%) | 207 (47.8%) | 6 (1.4%) | 69 / 0 / 0 | 12 |

Rates use observed race outcomes only. An entry already at/beyond the extension level is excluded, along with missing entries and censored paths; qualifying-price overshoot flags remain in the event CSV/JSON. Ambiguous first-touch candles count reversal first. Thresholds, horizons and stocks from the same session are dependent observations. Rates are conditional on the acquired cohort. Chronological split summaries are in report.json.

Baseline includes 10bps adverse slippage each side and estimated Indian intraday fees. Stress applies 25bps each side and reruns the full execution model. All 12 families/stops and short/exhaustion diagnostics are in summary.csv; these tables are ordered by development evidence.

## Data and execution limits

- Dated October2024 fund-holdings cohort is a fixed cohort proxy, not all Indian stocks or a reconstituted historical index
- Unavailable historical members, missing regular sessions and insufficient RVOL remain explicit in the source/load audits; complete-case prices do not establish universal availability
- Candle OHLCV cannot reconstruct active orders, historical spread/depth, queue priority, circuits, or broker intraday eligibility
- Short portfolios are diagnostic; historical short-sale eligibility and forced-close/auction costs are unverified
- Current basic-plan brokerage and tax estimates are modeled historically; 10/25bps slippage is an assumption
- Known capital-action/dividend exdates excluded; the NSE action calendar was extended through 13 November 2026, but source histories are not certified exhaustively
- Split/bonus price and volume units are restored locally; original Upstox PostgreSQL candles remain unchanged. The unit audit covers 57 event dates across 56 companies; 41 companies require restoration during the study. It includes 112 company-day checks against three NSE bhavcopies; maximum sampled price residual is 5.89bp and volume residual 1.99bp. This limited certification does not validate every bar or historical action
- Five-minute same-bar stop/target ambiguity uses stop-first; exit liquidity and within-bar gaps remain uncertain
- Future entry-bar flatness is not an admission filter; historical circuits, opening queue priority and available executable depth remain unverified
- Drawdown uses end-of-day cash equity; transient intraday path drawdown can be worse
- Calendar appeared in earlier research: held-out results are pseudo-out-of-sample, not a new live forward track record
- No leverage in primary results; scaling capital or leverage does not establish an edge

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m research.intraday_momentum.data plan
.\.venv\Scripts\python.exe -m research.intraday_momentum.data acquire
.\.venv\Scripts\python.exe scripts\run_intraday_momentum.py
```

Do not regenerate a frozen plan in an existing run directory. Source data/imports go only to primary Upstox candles in PostgreSQL. Protocols, source metadata, rankings, trade logs and results remain local.
