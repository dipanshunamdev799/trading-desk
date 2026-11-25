# NIFTY V17 — Volume, liquidity and order flow

Trade-derived features use actual volume in authenticated stock/ETF candles. The study audited 125,125 stock and index snapshots across 401 days and intentionally left native-index volume missing in 19,649 index rows. Relative volume and turnover are same-clock comparisons against earlier sessions. VWAP uses typical bar price multiplied by observed candle volume as a proxy for transaction VWAP. Turnover inferred from candle prices is approximate and the official cash-file turnover series is reserved for later clocks. Other features are dispersion and concentration of activity, conditional negative-side activity, returns per unit of activity, and a sign-of-price-move × volume proxy. Historical auction order records, quotes, historical depth and prints were unavailable in the study’s stored authentic data. The candle signs measure price changes and trading activity. Trade initiation, bid/ask imbalance, dealer inventory and executable spreads require genuine historical records. Upstox’s candle and live-feed documentation describe distinct capabilities.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | r30 | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.250670 | 0.248972 | -0.001698 | -0.007988 | 0.004593 |
| 09:25 | r30 | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001265 | 0.001256 | -8.98e-06 | -0.000026 | 7.73e-06 |
| 09:25 | regular_residual | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249277 | 0.247995 | -0.001282 | -0.007601 | 0.005036 |
| 09:25 | regular_residual | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.003553 | 0.003528 | -0.000025 | -0.000064 | 0.000014 |
| 09:25 | remaining_range | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002302 | 0.002238 | -0.000064 | -0.000256 | 0.000129 |
| 09:25 | remaining_range | liquidity_residual | frozen_parent_residual_history | qlike | 257 | 257 | 0.457556 | 0.444014 | -0.013543 | -0.057344 | 0.030258 |
| 09:25 | remaining_range | liquidity_residual | native_control | crps | 257 | 257 | 0.002302 | 0.002218 | -0.000084 | -0.000285 | 0.000117 |
| 09:25 | remaining_range | liquidity_residual | native_control | qlike | 257 | 257 | 0.457556 | 0.435407 | -0.022149 | -0.081678 | 0.037380 |
| 09:25 | remaining_vol | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000997 | 0.000989 | -7.35e-06 | -0.000103 | 0.000088 |
| 09:25 | remaining_vol | liquidity_residual | frozen_parent_residual_history | qlike | 257 | 257 | 0.239091 | 0.225481 | -0.013610 | -0.048749 | 0.021530 |
| 09:25 | remaining_vol | liquidity_residual | native_control | crps | 257 | 257 | 0.000997 | 0.000974 | -0.000023 | -0.000121 | 0.000074 |
| 09:25 | remaining_vol | liquidity_residual | native_control | qlike | 257 | 257 | 0.239091 | 0.218998 | -0.020093 | -0.060298 | 0.020112 |
| 09:25 | touch_down | dispersion_touch | native_control | brier | 257 | 257 | 0.229719 | 0.229799 | 0.000080 | -0.003503 | 0.003663 |
| 09:25 | touch_down | dispersion_touch | native_control | crps | 257 | 257 | 0.229719 | 0.229799 | 0.000080 | -0.003503 | 0.003663 |
| 09:25 | touch_up | dispersion_touch | native_control | brier | 257 | 257 | 0.214907 | 0.215722 | 0.000815 | -0.002758 | 0.004389 |
| 09:25 | touch_up | dispersion_touch | native_control | crps | 257 | 257 | 0.214907 | 0.215722 | 0.000815 | -0.002758 | 0.004389 |
| 10:20 | r30 | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.264868 | 0.260102 | -0.004766 | -0.008449 | -0.001084 |
| 10:20 | r30 | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000821 | 0.000813 | -7.30e-06 | -0.000015 | 3.21e-07 |
| 10:20 | regular_residual | liquidity_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.253292 | 0.247850 | -0.005442 | -0.012699 | 0.001815 |
| 10:20 | regular_residual | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002964 | 0.002921 | -0.000043 | -0.000076 | -0.000011 |
| 10:20 | remaining_range | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002120 | 0.002043 | -0.000076 | -0.000239 | 0.000086 |
| 10:20 | remaining_range | liquidity_residual | frozen_parent_residual_history | qlike | 257 | 257 | 0.563558 | 0.517955 | -0.045603 | -0.146141 | 0.054935 |
| 10:20 | remaining_range | liquidity_residual | native_control | crps | 257 | 257 | 0.002120 | 0.002017 | -0.000102 | -0.000284 | 0.000080 |
| 10:20 | remaining_range | liquidity_residual | native_control | qlike | 257 | 257 | 0.563558 | 0.512221 | -0.051337 | -0.161455 | 0.058781 |
| 10:20 | remaining_vol | liquidity_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000900 | 0.000888 | -0.000011 | -0.000083 | 0.000060 |
| 10:20 | remaining_vol | liquidity_residual | frozen_parent_residual_history | qlike | 257 | 257 | 0.281902 | 0.259638 | -0.022264 | -0.079915 | 0.035386 |
| 10:20 | remaining_vol | liquidity_residual | native_control | crps | 257 | 257 | 0.000900 | 0.000874 | -0.000025 | -0.000096 | 0.000046 |
| 10:20 | remaining_vol | liquidity_residual | native_control | qlike | 257 | 257 | 0.281902 | 0.254150 | -0.027752 | -0.092844 | 0.037340 |
| 10:20 | touch_down | dispersion_touch | native_control | brier | 257 | 257 | 0.221265 | 0.220445 | -0.000819 | -0.004468 | 0.002830 |
| 10:20 | touch_down | dispersion_touch | native_control | crps | 257 | 257 | 0.221265 | 0.220445 | -0.000819 | -0.004468 | 0.002830 |
| 10:20 | touch_up | dispersion_touch | native_control | brier | 257 | 257 | 0.169132 | 0.170104 | 0.000972 | -0.000955 | 0.002898 |
| 10:20 | touch_up | dispersion_touch | native_control | crps | 257 | 257 | 0.169132 | 0.170104 | 0.000972 | -0.000955 | 0.002898 |

[Intraday source and price audit](stock-identity-and-price-audit.csv.gz) · [Official traded cash data](official-equity-receipt.json) · [Historical Upstox candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [NSE historical order and trade data](https://www.nseindia.com/static/market-data/eod-historical-data-subscription)
