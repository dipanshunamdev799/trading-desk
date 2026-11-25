# V21 Joint Equity Return Distributions

The main joint stock law keeps **256 simultaneous terminal stock scenarios per origin**, with one joint residual vector per draw and the paired historical index tracking-basis error. We also tested conditionally selected residual rows, Gaussian covariance with **25%** diagonal shrinkage, dynamic market/sector factor innovations, Student-t tail scaling, and independent permutations of the same marginal stock atoms. The independence control retains the same individual stock scenario samples and shuffles their alignment. This makes the cost of removing common shocks visible even when the marginal forecasts are identical. Starting constituent weights convert simultaneous simple returns into index endpoint scenarios with implicit buy-and-hold drift. Complete weighted index atoms give the mean, median, up probability, endpoint, quantiles and tails together.

| horizon | model | n | disjoint | brier | crps | coverage80 | width80 | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | stock_conditional_joint | 265 | 53 | 0.263077 | 0.011637 | 0.758491 | 0.041286 | 0.724597 |
| 5 | stock_dynamic_factor | 265 | 53 | 0.265255 | 0.011736 | 0.637736 | 0.031108 | 0.729559 |
| 5 | stock_factor_heads | 265 | 53 | 0.258607 | 0.011471 | 0.645283 | 0.031130 | 0.715344 |
| 5 | stock_gaussian_shrink | 265 | 53 | 0.267394 | 0.011627 | 0.769811 | 0.043153 | 0.732357 |
| 5 | stock_heavy_factor | 265 | 53 | 0.268496 | 0.011808 | 0.600000 | 0.028478 | 0.738714 |
| 5 | stock_history_joint | 265 | 53 | 0.261940 | 0.011430 | 0.803774 | 0.045641 | 0.717410 |
| 5 | stock_independent | 265 | 53 | 0.304882 | 0.012713 | 0.396226 | 0.015863 | 0.866707 |
| 5 | stock_pooled_joint | 265 | 53 | 0.267066 | 0.011575 | 0.781132 | 0.045600 | 0.731034 |
| 21 | stock_conditional_joint | 217 | 11 | 0.256173 | 0.026123 | 0.700461 | 0.097522 | 0.710337 |
| 21 | stock_dynamic_factor | 217 | 11 | 0.251064 | 0.026046 | 0.672811 | 0.087543 | 0.708257 |
| 21 | stock_factor_heads | 217 | 11 | 0.286871 | 0.029507 | 0.626728 | 0.086802 | 0.874074 |
| 21 | stock_gaussian_shrink | 217 | 11 | 0.236048 | 0.024729 | 0.718894 | 0.081773 | 0.668296 |
| 21 | stock_heavy_factor | 217 | 11 | 0.249160 | 0.025845 | 0.654378 | 0.078046 | 0.708383 |
| 21 | stock_history_joint | 217 | 11 | 0.282850 | 0.027603 | 0.728111 | 0.093341 | 0.764280 |
| 21 | stock_independent | 217 | 11 | 0.249218 | 0.027040 | 0.331797 | 0.029785 | 0.734094 |
| 21 | stock_pooled_joint | 217 | 11 | 0.243710 | 0.025348 | 0.751152 | 0.092897 | 0.680761 |

The archive includes **482** simultaneous stock/sector issues and paired basis atoms. Convergence checks synthesize **128, 256 and 1,024** draws from the same draw stream and compare average absolute differences. They quantify simulation variation on a fixed set of forecast dates. A nominal 80% interval that misses many outcomes is a visible failure even when its directional score looks competitive.

| horizon | draw count | compared to | mean | p up | q10 | q90 | std |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 128 | 1,024 | 0.001276 | 0.032577 | 0.002338 | 0.002753 | 0.001085 |
| 21 | 128 | 1,024 | 0.002340 | 0.030485 | 0.009074 | 0.003674 | 0.001969 |
| 5 | 256 | 1,024 | 0.000888 | 0.022560 | 0.001483 | 0.001812 | 0.000649 |
| 21 | 256 | 1,024 | 0.001527 | 0.020809 | 0.005920 | 0.002443 | 0.001314 |

[joint-simultaneous-laws.npz](joint-simultaneous-laws.npz) · [index-forecast-laws.npz](index-forecast-laws.npz) · [joint-fit-receipts.csv](joint-fit-receipts.csv) · [joint-forecast-config.json](joint-forecast-config.json) · [monte-carlo-convergence-cases.csv](monte-carlo-convergence-cases.csv) · [monte-carlo-convergence-summary.csv](monte-carlo-convergence-summary.csv) · [tracking-and-dependence.png](tracking-and-dependence.png)
