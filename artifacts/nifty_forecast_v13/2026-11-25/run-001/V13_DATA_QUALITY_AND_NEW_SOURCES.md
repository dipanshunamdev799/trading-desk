# V13 Data Quality And New Sources

V13 validated **403** frozen OHLC sessions from **2025-04-02** to **2026-11-17** and found **0** spot-close discrepancies over 0.05 index point against the official file. Upstox returned **49 of 49** requested historical payloads. The IST regular-session grid spans 09:15 through 15:30. Separate daily and intraday audits cover special sessions, missing bars, and differences between daily official anchors and final intraday marks. Intraday ordering requires complete grids and daily high/low agreement within one index point. India VIX agreed within 0.05 on **403 of 403** overlapping observations.

| interval | sessions | complete | reconciled |
| --- | --- | --- | --- |
| 1 | 403 | 394 | 393 |
| 5 | 403 | 396 | 395 |
| 25 | 403 | 396 | 395 |

| name | rows | complete_normal_grids | http | unavailable | source |
| --- | --- | --- | --- | --- | --- |
| gold_proxy | 466 | — | 200 | — | https://api.upstox.com/v3/historical-candle/NSE_EQ%7CINF204KB17I5/days/1/2026-11-17/2025-01-01 |
| sector_sample | 839 | 11.000000 | 200 | — | https://api.upstox.com/v3/historical-candle/NSE_INDEX%7CNifty%20Bank/minutes/5/2026-11-17/2026-11-01 |
| etf_sample | 839 | 11.000000 | 200 | — | https://api.upstox.com/v3/historical-candle/NSE_EQ%7CINF204KB14I2/minutes/5/2026-11-17/2026-11-01 |
| nasdaq_implied | 489 | — | 200 | — | https://fred.stlouisfed.org/graph/fredgraph.csv?id=VXNCLS&cosd=2025-01-01&coed=2026-11-17 |

| day | upstox_close | nse_close | delta | failure |
| --- | --- | --- | --- | --- |
| 2026-11-18 | 25227.950000 | 25227.950000 | 0.000000 | — |
| 2026-11-19 | 25514.300000 | 25514.300000 | 0.000000 | — |
| 2026-11-20 | 25800.600000 | 25800.600000 | 0.000000 | — |
| 2026-11-23 | 25349.650000 | 25349.650000 | 0.000000 | — |

[Market data archive receipts](acquisition.json) · [Intraday audit](intraday-audit.csv) · [VIX source comparison](india-vix-reconciliation.csv) · [Refresh reconciliation](refresh-reconciliation.json) · [Upstox historical specification](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [India VIX definition](https://www.nseindia.com/static/products-services/indices-indiavix-index).
