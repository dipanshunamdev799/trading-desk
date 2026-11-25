# NIFTY V18 — Aggregate fundamental intelligence

The aggregate pipeline creates **1,604** clock-specific snapshots using **2-, 9-, 31- and 130-calendar-day** windows for publications, short events, and the latest eligible company results. It measures the count of positive and adverse disclosures, earnings improvement breadth, growth dispersion, financial-sector releases, materiality concentration, recent arrival intensity and discrepancies between text and price changes. Each eligible issuer can contribute its latest timely observation. We compared equal-company, sector-balanced and capped historical-liquidity weights from a January 2025 fixed basket. Dated firm market caps and index constituent weights were incomplete, so the weighting tables identify the available proxies. Archive availability and structured financial coverage are recorded separately. Scale estimates and baseline predictors are learned from earlier information, with price history, official equal-weight breadth, financial rotation and volatility already included in the structural parent.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | counts | clock_structural | brier | 265 | 53 | 0.243837 | 0.238274 | -0.005563 | -0.019659 | 0.008534 |
| 5 | preauction_0855 | counts | clock_structural | crps | 265 | 53 | 0.010874 | 0.010658 | -0.000216 | -0.000520 | 0.000089 |
| 5 | preauction_0855 | multi_timescale | clock_structural | brier | 265 | 53 | 0.244634 | 0.238274 | -0.006359 | -0.025281 | 0.012562 |
| 5 | preauction_0855 | multi_timescale | clock_structural | crps | 265 | 53 | 0.011056 | 0.010658 | -0.000398 | -0.001017 | 0.000220 |
| 5 | preauction_0855 | weighted_text | clock_structural | brier | 265 | 53 | 0.244613 | 0.238274 | -0.006339 | -0.020244 | 0.007566 |
| 5 | preauction_0855 | weighted_text | clock_structural | crps | 265 | 53 | 0.010906 | 0.010658 | -0.000247 | -0.000540 | 0.000045 |
| 5 | preauction_0855 | fundamental_augmentation | clock_structural | brier | 265 | 53 | 0.248263 | 0.238274 | -0.009989 | -0.031308 | 0.011331 |
| 5 | preauction_0855 | fundamental_augmentation | clock_structural | crps | 265 | 53 | 0.011103 | 0.010658 | -0.000445 | -0.001092 | 0.000202 |
| 5 | preauction_0855 | sector_liquidity_proxy | clock_structural | brier | 265 | 53 | 0.250934 | 0.238274 | -0.012659 | -0.030550 | 0.005231 |
| 5 | preauction_0855 | sector_liquidity_proxy | clock_structural | crps | 265 | 53 | 0.011178 | 0.010658 | -0.000519 | -0.001161 | 0.000122 |
| 5 | preauction_0855 | multi_timescale | component_plus_residual | brier | 265 | 53 | 0.244634 | 0.238003 | -0.006631 | -0.030752 | 0.017491 |
| 5 | preauction_0855 | multi_timescale | component_plus_residual | crps | 265 | 53 | 0.011056 | 0.010309 | -0.000748 | -0.001689 | 0.000193 |
| 5 | preauction_0855 | fundamental_augmentation | component_plus_residual | brier | 265 | 53 | 0.248263 | 0.238003 | -0.010260 | -0.033513 | 0.012994 |
| 5 | preauction_0855 | fundamental_augmentation | component_plus_residual | crps | 265 | 53 | 0.011103 | 0.010309 | -0.000795 | -0.001633 | 0.000044 |
| 5 | previous_1700 | counts | clock_structural | brier | 265 | 53 | 0.244096 | 0.238605 | -0.005491 | -0.018360 | 0.007377 |
| 5 | previous_1700 | counts | clock_structural | crps | 265 | 53 | 0.010935 | 0.010721 | -0.000214 | -0.000543 | 0.000115 |
| 5 | previous_1700 | multi_timescale | clock_structural | brier | 265 | 53 | 0.243827 | 0.238605 | -0.005223 | -0.024897 | 0.014452 |
| 5 | previous_1700 | multi_timescale | clock_structural | crps | 265 | 53 | 0.011134 | 0.010721 | -0.000413 | -0.001036 | 0.000210 |
| 5 | previous_1700 | weighted_text | clock_structural | brier | 265 | 53 | 0.243901 | 0.238605 | -0.005297 | -0.017903 | 0.007310 |
| 5 | previous_1700 | weighted_text | clock_structural | crps | 265 | 53 | 0.010936 | 0.010721 | -0.000214 | -0.000534 | 0.000105 |
| 5 | previous_1700 | fundamental_augmentation | clock_structural | brier | 265 | 53 | 0.248308 | 0.238605 | -0.009703 | -0.032993 | 0.013586 |
| 5 | previous_1700 | fundamental_augmentation | clock_structural | crps | 265 | 53 | 0.011194 | 0.010721 | -0.000473 | -0.001176 | 0.000231 |
| 5 | previous_1700 | sector_liquidity_proxy | clock_structural | brier | 265 | 53 | 0.252170 | 0.238605 | -0.013565 | -0.035164 | 0.008033 |
| 5 | previous_1700 | sector_liquidity_proxy | clock_structural | crps | 265 | 53 | 0.011271 | 0.010721 | -0.000549 | -0.001278 | 0.000180 |
| 5 | previous_1700 | multi_timescale | component_plus_residual | brier | 265 | 53 | 0.243827 | 0.236585 | -0.007243 | -0.029161 | 0.014675 |
| 5 | previous_1700 | multi_timescale | component_plus_residual | crps | 265 | 53 | 0.011134 | 0.010658 | -0.000476 | -0.001189 | 0.000237 |
| 5 | previous_1700 | fundamental_augmentation | component_plus_residual | brier | 265 | 53 | 0.248308 | 0.236585 | -0.011723 | -0.033590 | 0.010143 |
| 5 | previous_1700 | fundamental_augmentation | component_plus_residual | crps | 265 | 53 | 0.011194 | 0.010658 | -0.000536 | -0.001245 | 0.000174 |
| 21 | preauction_0855 | counts | clock_structural | brier | 217 | 11 | 0.347264 | 0.302805 | -0.044459 | -0.105497 | 0.016579 |
| 21 | preauction_0855 | counts | clock_structural | crps | 217 | 11 | 0.030236 | 0.028519 | -0.001717 | -0.004602 | 0.001169 |
| 21 | preauction_0855 | multi_timescale | clock_structural | brier | 217 | 11 | 0.313526 | 0.302805 | -0.010721 | -0.064798 | 0.043355 |
| 21 | preauction_0855 | multi_timescale | clock_structural | crps | 217 | 11 | 0.029870 | 0.028519 | -0.001351 | -0.004970 | 0.002269 |
| 21 | preauction_0855 | weighted_text | clock_structural | brier | 217 | 11 | 0.345244 | 0.302805 | -0.042439 | -0.102465 | 0.017586 |
| 21 | preauction_0855 | weighted_text | clock_structural | crps | 217 | 11 | 0.030224 | 0.028519 | -0.001705 | -0.004566 | 0.001156 |
| 21 | preauction_0855 | fundamental_augmentation | clock_structural | brier | 217 | 11 | 0.312599 | 0.302805 | -0.009794 | -0.072604 | 0.053015 |
| 21 | preauction_0855 | fundamental_augmentation | clock_structural | crps | 217 | 11 | 0.029850 | 0.028519 | -0.001331 | -0.005336 | 0.002675 |
| 21 | preauction_0855 | sector_liquidity_proxy | clock_structural | brier | 217 | 11 | 0.308291 | 0.302805 | -0.005486 | -0.052341 | 0.041368 |
| 21 | preauction_0855 | sector_liquidity_proxy | clock_structural | crps | 217 | 11 | 0.030122 | 0.028519 | -0.001603 | -0.005487 | 0.002282 |
| 21 | preauction_0855 | multi_timescale | component_plus_residual | brier | 217 | 11 | 0.313526 | 0.300952 | -0.012575 | -0.060703 | 0.035554 |
| 21 | preauction_0855 | multi_timescale | component_plus_residual | crps | 217 | 11 | 0.029870 | 0.028698 | -0.001172 | -0.004736 | 0.002393 |

[All then-available aggregate values](event-aggregate-features.csv.gz) · [Field coverage by clock](aggregate-feature-coverage.csv) · [Registered January liquidity cohort](issuer-seed.csv) · [Market-wide matched comparisons](endpoint-paired-comparisons.csv)
