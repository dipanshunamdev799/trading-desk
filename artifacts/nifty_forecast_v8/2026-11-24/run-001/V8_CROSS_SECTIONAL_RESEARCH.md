# NIFTY V8 · Cross Sectional Research

Run `2026-11-24/run-001`. Retrospective research.

The date-level sector panel uses nine native NSE indices. NIFTY-conditional residuals remove a trailing 63-session sector market beta, used with one-session lag. Four aggregates capture common five-session return, residual return and residual dispersion across the nine sectors, and mean sector volatility. One observation per date enters the NIFTY target fit. The underlying panel contains repeated market dates and shared prices, so cross-sectional observations do not increase the count of independent NIFTY outcomes. A separate current-selected stock-basket proxy tests historical observed participation, volume and dispersion while retaining the selection/survivorship limitation. It is a diagnostic rather than a broad-market membership history.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 92 | 19 | 0.804348 | 0.809869 | 0.162294 | 0.505451 | 0.009897 | 0.012856 | 0.019324 | 0.004981 | 0.554348 | 0.815217 | 0.038767 |
| A_NATIVE_PANEL | 92 | 19 | 0.804348 | 0.809869 | 0.160086 | 0.501285 | 0.009892 | 0.012916 | 0.019379 | 0.004981 | 0.543478 | 0.804348 | 0.038499 |
| A_STOCK_PROXY | 92 | 19 | 0.793478 | 0.800435 | 0.166866 | 0.515793 | 0.009963 | 0.012852 | 0.019475 | 0.005014 | 0.554348 | 0.815217 | 0.038796 |
| A_PARTICIPATION | 92 | 19 | 0.793478 | 0.797049 | 0.162243 | 0.505575 | 0.009882 | 0.012847 | 0.019348 | 0.004964 | 0.543478 | 0.815217 | 0.038442 |


| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_ROT | 76 | 4 | 0.552632 | 0.587097 | 0.257372 | 0.712354 | 0.030072 | 0.038406 | 0.049434 | 0.015152 | 0.315789 | 0.500000 | 0.072037 |
| A_NATIVE_PANEL | 76 | 4 | 0.539474 | 0.575986 | 0.266763 | 0.734185 | 0.030620 | 0.039153 | 0.049976 | 0.015446 | 0.315789 | 0.500000 | 0.071785 |
| A_STOCK_PROXY | 76 | 4 | 0.552632 | 0.587097 | 0.249669 | 0.693540 | 0.029782 | 0.038150 | 0.049386 | 0.015054 | 0.328947 | 0.513158 | 0.071221 |
| A_PARTICIPATION | 76 | 4 | 0.552632 | 0.587097 | 0.262352 | 0.723516 | 0.030236 | 0.038543 | 0.049839 | 0.015219 | 0.328947 | 0.500000 | 0.072154 |


| model | parent | metric | n | gain |
| --- | --- | --- | --- | --- |
| A_NATIVE_PANEL | B_ROT | brier | 92 | 0.002208 |
| A_NATIVE_PANEL | B_ROT | crps | 92 | 0.000005 |
| A_PARTICIPATION | B_ROT | brier | 92 | 0.000051 |
| A_PARTICIPATION | B_ROT | crps | 92 | 0.000015 |
| A_STOCK_PROXY | B_ROT | brier | 92 | -0.004572 |
| A_STOCK_PROXY | B_ROT | crps | 92 | -0.000066 |


The native residual panel reduces weekly Brier from .162294 to .160086 with similar CRPS. Matching dates shows a modest candidate increment. The monthly panel does not improve the stronger persistence controls. The current-selected stock proxy worsens both weekly rotation scores; original membership listings and historical weights remain necessary to interpret that family beyond sensitivity. Findings favor a compact native panel representation over pooling current constituent rows as labels.

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
