# Metric interpretation

The metrics.csv/report.json field `modeled_fill_rate` is candidate acceptance: closed modeled trades divided by all eligible signals, including portfolio/risk/stop-distance rejections. It is not a measured broker order-fill probability. execution-acceptance.csv separates candidate acceptance and modeled fills per attempted entry. Neither measures real fills; historical partial fills and queue execution remain unobserved.

Holding minutes and exposure use the time capital is reserved, conservatively to the end of an unresolved stop/target candle. They are modeled occupancy estimates, not exact tick execution times. Drawdown is end-of-day cash equity. Gross-before-slippage uses fixed modeled entries/exits/quantities and is a cost attribution, not a frictionless compounded backtest. Scenario returns rerun the whole portfolio. No leverage or funding cost is assumed.

Segment tables are exploratory, dependent and subject to multiple comparisons; a positive small bucket is not a selected strategy. Sector means the dated-industry peer proxy, not independently acquired historical sector-index performance. The 72 stress scenarios are not selectable additional models.

H3 first source-time-only diagnostic is invalidated; only depth-diagnostic-asof.json uses both availability clocks. The original artifacts are retained.
