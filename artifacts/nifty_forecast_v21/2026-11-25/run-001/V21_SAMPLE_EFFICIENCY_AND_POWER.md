# V21 Sample Efficiency And Power

V21 scored **119,569 absolute equity cases** across the two original horizons. They belong to **265** weekly and **217** monthly market dates. Within horizon there are **53** and **11** non-overlapping outcomes, respectively. The panel’s company rows can help estimate shared coefficients. Their common shocks, overlapping outcome windows and related sectors limit what they contribute to learning a broad-market effect. Weight concentration and the stock-to-index variance ratio are reported alongside nominal company counts.

| horizon | dates | stock cases | rank corr | mae | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | 265 | 65,785 | -0.014346 | 0.034854 | 0.025502 |
| 21 | 217 | 53,784 | -0.025418 | 0.075526 | 0.054919 |

| horizon | train rows median | distinct dates median | training issuers median |
| --- | --- | --- | --- |
| 5 | 33283.000000 | 135.000000 | 249.000000 |
| 21 | 33227.000000 | 135.000000 | 249.000000 |

The simulation uses **300 replications per design**, **8, 32 and 128** securities, **eight groups**, **53 or 11** distinct training windows, and **128** synthetic test dates. It varies shared slopes, offsetting sector slopes, common shocks, correlated issuer noise and spurious training relationships. Neutral, date-only, pooled and partial-sector estimates see the same simulated dates. The oracle forecast RMSE focuses on the difference from the simulated conditional mean rather than the irreducible realized noise. The estimates apply to the declared simulation only.

| horizon | scenario | market windows | model | index rmse | oracle rmse | coef rmse | better share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | correlated_idiosyncratic_noise | 53 | date_only | 0.016022 | 0.002145 | 0.003570 | 0.000000 |
| 5 | correlated_idiosyncratic_noise | 53 | partial_sector | 0.015864 | 0.000256 | 0.000619 | 0.733333 |
| 5 | correlated_idiosyncratic_noise | 53 | shared_pool | 0.015864 | 0.000254 | 0.000417 | 0.733333 |
| 5 | no_index_predictability_even_with_stock_signal | 53 | date_only | 0.015761 | 0.002151 | 0.010231 | 0.000000 |
| 5 | no_index_predictability_even_with_stock_signal | 53 | partial_sector | 0.015611 | 2.99e-33 | 0.010000 | 0.703333 |
| 5 | no_index_predictability_even_with_stock_signal | 53 | shared_pool | 0.015611 | 3.11e-33 | 0.010000 | 0.703333 |
| 5 | pure_common_market_noise | 53 | date_only | 0.030317 | 0.003975 | 0.006486 | 0.000000 |
| 5 | pure_common_market_noise | 53 | partial_sector | 0.030077 | 0.000072 | 0.000183 | 0.673333 |
| 5 | pure_common_market_noise | 53 | shared_pool | 0.030077 | 0.000072 | 0.000117 | 0.666667 |
| 5 | sector_specific_cancellation | 53 | date_only | 0.009951 | 0.001680 | 0.014180 | 0.000000 |
| 5 | sector_specific_cancellation | 53 | partial_sector | 0.009820 | 0.000621 | 0.007950 | 0.826667 |
| 5 | sector_specific_cancellation | 53 | shared_pool | 0.009857 | 0.001031 | 0.014008 | 0.716667 |
| 5 | shared_relationship | 53 | date_only | 0.009054 | 0.001261 | 0.002093 | 0.000000 |
| 5 | shared_relationship | 53 | partial_sector | 0.008975 | 0.000245 | 0.000592 | 0.646667 |
| 5 | shared_relationship | 53 | shared_pool | 0.008975 | 0.000243 | 0.000402 | 0.660000 |
| 5 | spurious_training_relationship | 53 | date_only | 0.018616 | 0.005924 | 0.009796 | 0.000000 |
| 5 | spurious_training_relationship | 53 | partial_sector | 0.018422 | 0.005291 | 0.009151 | 0.493333 |
| 5 | spurious_training_relationship | 53 | shared_pool | 0.018422 | 0.005287 | 0.008760 | 0.493333 |
| 21 | correlated_idiosyncratic_noise | 11 | date_only | 0.016377 | 0.004159 | 0.006828 | 0.000000 |
| 21 | correlated_idiosyncratic_noise | 11 | partial_sector | 0.015862 | 0.000686 | 0.001455 | 0.800000 |
| 21 | correlated_idiosyncratic_noise | 11 | shared_pool | 0.015862 | 0.000682 | 0.001137 | 0.806667 |
| 21 | no_index_predictability_even_with_stock_signal | 11 | date_only | 0.016165 | 0.004356 | 0.010910 | 0.000000 |
| 21 | no_index_predictability_even_with_stock_signal | 11 | partial_sector | 0.015595 | 1.64e-33 | 0.010000 | 0.806667 |
| 21 | no_index_predictability_even_with_stock_signal | 11 | shared_pool | 0.015595 | 1.68e-33 | 0.010000 | 0.806667 |
| 21 | pure_common_market_noise | 11 | date_only | 0.031208 | 0.007931 | 0.013018 | 0.000000 |
| 21 | pure_common_market_noise | 11 | partial_sector | 0.030165 | 0.000129 | 0.000347 | 0.840000 |
| 21 | pure_common_market_noise | 11 | shared_pool | 0.030165 | 0.000128 | 0.000211 | 0.840000 |
| 21 | sector_specific_cancellation | 11 | date_only | 0.010073 | 0.002465 | 0.014497 | 0.000000 |
| 21 | sector_specific_cancellation | 11 | partial_sector | 0.009799 | 0.000806 | 0.008643 | 0.830000 |
| 21 | sector_specific_cancellation | 11 | shared_pool | 0.009831 | 0.001144 | 0.014032 | 0.776667 |
| 21 | shared_relationship | 11 | date_only | 0.009278 | 0.002528 | 0.004173 | 0.000000 |
| 21 | shared_relationship | 11 | partial_sector | 0.008964 | 0.000700 | 0.001440 | 0.760000 |
| 21 | shared_relationship | 11 | shared_pool | 0.008964 | 0.000695 | 0.001149 | 0.766667 |
| 21 | spurious_training_relationship | 11 | date_only | 0.018753 | 0.006323 | 0.010474 | 0.000000 |
| 21 | spurious_training_relationship | 11 | partial_sector | 0.018253 | 0.004781 | 0.008328 | 0.520000 |
| 21 | spurious_training_relationship | 11 | shared_pool | 0.018252 | 0.004781 | 0.007952 | 0.520000 |

[synthetic-power-summary.csv](synthetic-power-summary.csv) · [synthetic-power-cases.csv.gz](synthetic-power-cases.csv.gz) · [synthetic-power-config.json](synthetic-power-config.json) · [concentration-cases.csv](concentration-cases.csv) · [equity-fit-receipts.csv](equity-fit-receipts.csv) · [index-search-adjusted-intervals.csv](index-search-adjusted-intervals.csv)
