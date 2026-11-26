# V22 International forecast tasks

The panel contains 9,361 timestamped market states and 46,805 rows across five horizons.
Each horizon measures 1, 3, 5, 10, 21 local trading sessions, with the original NIFTY definitions retained
at five and 21. The starting price is the previous local official close. The endpoint is the last scheduled close of the
horizon. The target is usable in a fit only after its end session and its publication guard.

The model issues 20 minutes before ordinary exchange opening. India starts at 08:55 IST, and V22 inputs also qualify for
the separately scored 09:10 comparator. Intraday venue information after that day's Indian snapshot cannot enter the
Indian V22 forecast. The pre-open clock and future observation timestamp are archived for every usable task.

## Outcome coverage in the canonical panel

| horizon | rows | return rows | volatility rows | ohlc range rows | global rows | residual rows | usd rows | reversal rows | expansion rows | breadth rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9,361 | 9,327 | 9,327 | 9,327 | 9,339 | 8,647 | 9,311 | 6,553 | 9,007 | 1,800 |
| 3 | 9,361 | 9,287 | 9,273 | 9,273 | 9,299 | 8,607 | 9,271 | 6,524 | 8,953 | 1,792 |
| 5 | 9,361 | 9,247 | 9,219 | 9,219 | 9,259 | 8,567 | 9,231 | 6,493 | 8,899 | 1,784 |
| 10 | 9,361 | 9,147 | 9,084 | 9,084 | 9,159 | 8,467 | 9,131 | 6,415 | 8,764 | 1,764 |
| 21 | 9,361 | 8,928 | 8,792 | 8,792 | 8,939 | 8,248 | 8,912 | 6,280 | 8,472 | 1,720 |

Forecast heads cover return location, sign probability from a full law, move magnitude, realized volatility, future range,
expansion and contraction, reversal, recovery, cross-market divergence, and limited breadth deterioration. Each OHLC law
starts at the same prior price, preserving endpoint and path geometry. Volatility is annualized RMS log close-to-close
returns times the square root of 252. The normalized target divides log return by trailing daily RMS volatility times the
square root of the horizon. Future high minus low is measured relative to the original close.

A local return and its USD-translated equivalent are separate fields. Dispersion, asynchronous breadth, sector leadership,
currency, volatility and rates join by published time where supported. Broad participation is proxied locally only where
a valid dated breadth or sector partner was available. The missingness is explicit, including targets that cross the freeze.

Local feature fields include shock, mom3, mom5, mom10, mom21, vol_level, vol_ratio, drawdown, trend_efficiency, down_share, fx5, local_breadth, local_sector, local_innovation5. Global and contextual fields include global1, global5, regional1, regional5, cross_dispersion, synchronization, global_vix, tech_lead, global_finance, oil5, rates5, pc_global.

[feature-definitions.json](feature-definitions.json) · [local-task-coverage.csv](local-task-coverage.csv) · [market-issue-clock-receipts.csv.gz](market-issue-clock-receipts.csv.gz) · [international-feature-panel.csv.gz](international-feature-panel.csv.gz) · [international-target-panel.csv.gz](international-target-panel.csv.gz) · [local-observed-paths.npz](local-observed-paths.npz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
