# Stronger controls for frozen intraday candidates

1196 complete research sessions, 2022-01-03 through 2026-11-06. Historical final period 2026-06-29–2026-11-06 (92 sessions). All numbers are index points per trade, not option returns.

The rules were chosen from phase-one observations. These are retrospective diagnostics. The six-contrast Bonferroni intervals cover net2 and matched-momentum excess for the fixed three-rule set, conditional on that set. They do not correct the original strategy search. The router is an additional exploratory portfolio, outside those six comparisons.

|Rule|N|Gross|Net2|Net5|Matched long net2|Matched momentum net2|Excess over momentum|Net2 conditional six-test interval|Excess conditional six-test interval|
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
|ema_trend|69|9.07|7.07|4.07|-0.05|1.76|5.32|-9.97, 26.14|-14.88, 23.56|
|donchian|42|8.83|6.83|3.83|-9.46|6.83|0.00|-15.38, 33.65|0.00, 0.00|
|pullback|61|7.42|5.42|2.42|-5.92|2.20|3.21|-10.47, 25.08|-17.10, 21.90|
|fixed_router|73|8.32|6.32|3.32|-2.59|1.96|4.37|-10.14, 25.47|-14.81, 22.16|

Same-time controls use the identical entry/exit prices with long, short or preceding-30-minute momentum direction. They isolate direction choice at those times. The all-opportunity momentum baseline (60m hold) had 460 trades, net2 mean 3.96.

|Rule|Session sign-flip two-sided p|One-bar-delay N|One-bar-delay net2|Drop best five net2|Drop best day net2|
|---|---:|---:|---:|---:|---:|
|ema_trend|0.2194|61|7.78|-4.91|3.09|
|donchian|0.3848|41|6.80|-9.27|0.21|
|pullback|0.3354|60|3.84|-5.79|0.87|
|fixed_router|0.2322|65|6.46|-5.01|2.55|

## Earlier-history replication (2022–2024)
Frozen rules motivated by the2025–2026 study are replayed on earlier history without refitting. This is backward replication, not a future holdout. Separate year/quarter rows disclose changing regimes.

|Rule|N|Gross|Net2|Excess over same-time momentum|Net2 conditional six-test interval|Excess conditional six-test interval|
|---|---:|---:|---:|---:|---|---|
|ema_trend|511|2.54|0.54|0.25|-5.42, 6.48|-1.76, 2.34|
|donchian|368|4.63|2.63|0.00|-5.21, 10.73|0.00, 0.00|
|pullback|469|2.76|0.76|0.54|-5.65, 7.15|-2.28, 3.30|
|fixed_router|552|2.23|0.23|0.38|-5.67, 6.17|-1.76, 2.48|

Sign flips randomize a whole session together to retain within-day clustering. Their p-values are conditional directional-null diagnostics, not proof that the market is stationary or an option premium would profit.

## Router and chronological adaptation
The fixed router gives EMA priority over Donchian, then pullback when signals coincide. It holds one position for60minutes; no new entry before exit. Only the predefined afternoon trend state is eligible. It does not add the individual strategy profits.

The monthly past-only selector chooses among fixed three rules using the preceding120 completed sessions, requiring30 trades and positive mean after5 points; otherwise it abstains. Final result: N=57, net2=6.38. This is a new retrospective policy, not a prospective test.

## Full diagnostics
All36 ablations, all-history year/quarter diagnostics, final-period side/month breakdowns, exact trade ledger and monthly selection decisions are exported. No candidate is promoted from those tables. Removing a profitable outlier is a stress test, not a reason to exclude the original trade from the official result.

Verification: 35265 exact timing, source-price, holding-period, nonoverlap, signed-PnL, phase-one reconciliation and feature-prefix assertions passed. Data hashes and script version are in the preregistration.

Future rules must be frozen and tested on new market data, with actual option contracts and executable premium prices before profitability claims.