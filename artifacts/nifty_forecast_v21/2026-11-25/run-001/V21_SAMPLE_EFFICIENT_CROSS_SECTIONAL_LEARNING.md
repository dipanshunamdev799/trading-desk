# V21 Sample Efficient Cross Sectional Learning

V21 compared independent equity models, fully pooled coefficients, sector-specific pooling, shared estimates shrunk toward sector and issuer estimates, a separate common plus relative return head, and factor-residual pooling. The simple historical and technical controls use the same dated universe. The random target control permutes issuer outcomes within already-matured dates. It retains the common market shock, exposing gains that survive after genuine issuer alignment has been removed. A five-session feature shift, randomized sectors and a shorter 70-date variant offer distinct negative or instability controls. All equity models use complete outcome dates before the next issue, with at most **135 historical dates** and eight-session coefficient refreshes. A separate date-only index model uses the same information cutoff and a comparable regularized fit.

| horizon | min dates | max dates | median rows | predicted dates |
| --- | --- | --- | --- | --- |
| 5 | 45 | 135 | 33283.000000 | 377 |
| 21 | 45 | 135 | 33227.000000 | 361 |

| horizon | model | target | dates | stock cases | rank corr | mae | rmse | brier | crps | coverage | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | common_relative | absolute | 265 | 65,785 | -0.008794 | 0.034513 | 0.047587 | 0.252360 | 0.025265 | 0.786544 | 0.111298 |
| 5 | common_relative | market_relative | 265 | 65,785 | -0.008793 | 0.030494 | 0.042678 | 0.253518 | 0.022445 | 0.742394 | 0.086813 |
| 5 | factor_residual | absolute | 265 | 65,785 | -0.013173 | 0.034550 | 0.047657 | 0.252557 | 0.025300 | 0.786793 | 0.111298 |
| 5 | factor_residual | market_relative | 265 | 65,785 | -0.008793 | 0.030494 | 0.042678 | 0.253518 | 0.022445 | 0.742394 | 0.086813 |
| 5 | history | absolute | 265 | 65,785 | 0.021325 | 0.034773 | 0.047882 | 0.254095 | 0.025432 | 0.785268 | 0.111298 |
| 5 | history | market_relative | 265 | 65,785 | 0.021239 | 0.030613 | 0.042867 | 0.254697 | 0.022543 | 0.739672 | 0.086813 |
| 5 | independent | absolute | 265 | 65,785 | 0.008086 | 0.035717 | 0.049497 | 0.259333 | 0.026136 | 0.777611 | 0.111298 |
| 5 | independent | market_relative | 265 | 65,785 | 0.008586 | 0.031605 | 0.044552 | 0.263150 | 0.023317 | 0.730749 | 0.086813 |
| 5 | partial_company | absolute | 265 | 65,785 | -0.005565 | 0.034837 | 0.048082 | 0.254773 | 0.025493 | 0.782655 | 0.111298 |
| 5 | partial_company | market_relative | 265 | 65,785 | -0.002059 | 0.030532 | 0.042763 | 0.253610 | 0.022478 | 0.741965 | 0.086813 |
| 5 | partial_sector | absolute | 265 | 65,785 | -0.017132 | 0.034857 | 0.048090 | 0.255214 | 0.025506 | 0.782133 | 0.111298 |
| 5 | partial_sector | market_relative | 265 | 65,785 | -0.008450 | 0.030509 | 0.042695 | 0.253728 | 0.022457 | 0.742361 | 0.086813 |
| 5 | pooled | absolute | 265 | 65,785 | -0.014346 | 0.034854 | 0.048081 | 0.255160 | 0.025502 | 0.782072 | 0.111298 |
| 5 | pooled | market_relative | 265 | 65,785 | -0.008793 | 0.030494 | 0.042678 | 0.253518 | 0.022445 | 0.742394 | 0.086813 |
| 5 | random_aux_labels | absolute | 265 | 65,785 | -0.040601 | 0.034868 | 0.048060 | 0.255150 | 0.025502 | 0.782813 | 0.111298 |
| 5 | random_aux_labels | market_relative | 265 | 65,785 | -0.029268 | 0.030511 | 0.042652 | 0.253745 | 0.022450 | 0.741694 | 0.086813 |
| 5 | random_sector | absolute | 265 | 65,785 | -0.013103 | 0.034921 | 0.048134 | 0.255587 | 0.025540 | 0.781511 | 0.111298 |
| 5 | random_sector | market_relative | 265 | 65,785 | -0.007217 | 0.030591 | 0.042782 | 0.254682 | 0.022511 | 0.740962 | 0.086813 |
| 5 | sector_pool | absolute | 265 | 65,785 | -0.019853 | 0.035042 | 0.048292 | 0.257065 | 0.025642 | 0.779778 | 0.111298 |
| 5 | sector_pool | market_relative | 265 | 65,785 | -0.015477 | 0.030743 | 0.042931 | 0.256696 | 0.022634 | 0.737971 | 0.086813 |
| 5 | shifted_company | absolute | 265 | 65,785 | -0.024534 | 0.034918 | 0.048105 | 0.255919 | 0.025533 | 0.781865 | 0.111298 |
| 5 | shifted_company | market_relative | 265 | 65,785 | -0.011394 | 0.030473 | 0.042652 | 0.253351 | 0.022431 | 0.741679 | 0.086813 |
| 5 | short_pool | absolute | 265 | 65,785 | 0.014403 | 0.035218 | 0.048408 | 0.259263 | 0.025743 | 0.777992 | 0.111298 |
| 5 | short_pool | market_relative | 265 | 65,785 | 0.019942 | 0.030419 | 0.042591 | 0.253081 | 0.022403 | 0.742803 | 0.086813 |
| 5 | technical | absolute | 265 | 65,785 | -0.020677 | 0.034865 | 0.048094 | 0.255226 | 0.025509 | 0.782390 | 0.111298 |
| 5 | technical | market_relative | 265 | 65,785 | -0.011672 | 0.030495 | 0.042677 | 0.253462 | 0.022445 | 0.742318 | 0.086813 |
| 21 | common_relative | absolute | 217 | 53,784 | -0.023149 | 0.076292 | 0.102189 | 0.253808 | 0.055191 | 0.754777 | 0.232796 |
| 21 | common_relative | market_relative | 217 | 53,784 | -0.023149 | 0.068037 | 0.094073 | 0.257850 | 0.049936 | 0.710107 | 0.181581 |
| 21 | factor_residual | absolute | 217 | 53,784 | -0.015684 | 0.076355 | 0.102409 | 0.254157 | 0.055282 | 0.755488 | 0.232796 |
| 21 | factor_residual | market_relative | 217 | 53,784 | -0.023149 | 0.068037 | 0.094073 | 0.257850 | 0.049936 | 0.710107 | 0.181581 |
| 21 | history | absolute | 217 | 53,784 | 0.027036 | 0.077779 | 0.104850 | 0.258823 | 0.056426 | 0.747042 | 0.232796 |
| 21 | history | market_relative | 217 | 53,784 | 0.027565 | 0.069533 | 0.096084 | 0.266112 | 0.051124 | 0.700484 | 0.181581 |
| 21 | independent | absolute | 217 | 53,784 | 0.031978 | 0.083695 | 0.115833 | 0.274031 | 0.060813 | 0.726505 | 0.232796 |
| 21 | independent | market_relative | 217 | 53,784 | 0.028611 | 0.075540 | 0.107475 | 0.287411 | 0.055960 | 0.671030 | 0.181581 |
| 21 | partial_company | absolute | 217 | 53,784 | 0.013690 | 0.075972 | 0.103392 | 0.248968 | 0.055213 | 0.760594 | 0.232796 |
| 21 | partial_company | market_relative | 217 | 53,784 | 0.018888 | 0.068345 | 0.094625 | 0.258300 | 0.050201 | 0.710264 | 0.181581 |
| 21 | partial_sector | absolute | 217 | 53,784 | -0.013462 | 0.075693 | 0.103075 | 0.248839 | 0.055056 | 0.761219 | 0.232796 |
| 21 | partial_sector | market_relative | 217 | 53,784 | -0.010005 | 0.068201 | 0.094231 | 0.258849 | 0.050045 | 0.708849 | 0.181581 |
| 21 | pooled | absolute | 217 | 53,784 | -0.025418 | 0.075526 | 0.102877 | 0.247727 | 0.054919 | 0.762744 | 0.232796 |
| 21 | pooled | market_relative | 217 | 53,784 | -0.023149 | 0.068037 | 0.094073 | 0.257850 | 0.049936 | 0.710107 | 0.181581 |
| 21 | random_aux_labels | absolute | 217 | 53,784 | 0.000901 | 0.075427 | 0.102487 | 0.247512 | 0.054781 | 0.763491 | 0.232796 |
| 21 | random_aux_labels | market_relative | 217 | 53,784 | 0.013568 | 0.067875 | 0.093576 | 0.258124 | 0.049792 | 0.710109 | 0.181581 |
| 21 | random_sector | absolute | 217 | 53,784 | -0.017067 | 0.076101 | 0.103546 | 0.250384 | 0.055313 | 0.759323 | 0.232796 |
| 21 | random_sector | market_relative | 217 | 53,784 | -0.013021 | 0.068663 | 0.094839 | 0.260844 | 0.050388 | 0.707349 | 0.181581 |
| 21 | sector_pool | absolute | 217 | 53,784 | -0.010775 | 0.077221 | 0.104990 | 0.255331 | 0.056288 | 0.751965 | 0.232796 |
| 21 | sector_pool | market_relative | 217 | 53,784 | -0.008135 | 0.069957 | 0.096093 | 0.266974 | 0.051404 | 0.697748 | 0.181581 |
| 21 | shifted_company | absolute | 217 | 53,784 | -0.027557 | 0.077145 | 0.105110 | 0.254771 | 0.056063 | 0.753159 | 0.232796 |
| 21 | shifted_company | market_relative | 217 | 53,784 | -0.024145 | 0.068281 | 0.094364 | 0.258954 | 0.050096 | 0.708134 | 0.181581 |
| 21 | short_pool | absolute | 217 | 53,784 | -0.019203 | 0.078374 | 0.105611 | 0.263368 | 0.056817 | 0.740312 | 0.232796 |
| 21 | short_pool | market_relative | 217 | 53,784 | -0.015691 | 0.068647 | 0.094594 | 0.262269 | 0.050349 | 0.706866 | 0.181581 |
| 21 | technical | absolute | 217 | 53,784 | -0.026399 | 0.075517 | 0.102859 | 0.247729 | 0.054913 | 0.762577 | 0.232796 |
| 21 | technical | market_relative | 217 | 53,784 | -0.024675 | 0.068008 | 0.094024 | 0.257744 | 0.049916 | 0.710165 | 0.181581 |

| horizon | cohort | model | n | mae | rmse | crps | rank corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | early | date_only_no_position | 173 | 0.015507 | 0.021666 | 0.011620 | -0.136974 |
| 5 | early | date_only_ridge | 173 | 0.014652 | 0.020189 | 0.010837 | 0.141876 |
| 5 | early | pooled_market_factor | 173 | 0.014957 | 0.020574 | 0.011164 | -0.062214 |
| 5 | later | date_only_no_position | 92 | 0.014765 | 0.021765 | 0.011477 | 0.343218 |
| 5 | later | date_only_ridge | 92 | 0.015346 | 0.022205 | 0.011823 | 0.235917 |
| 5 | later | pooled_market_factor | 92 | 0.015814 | 0.022827 | 0.012031 | 0.057581 |
| 21 | early | date_only_no_position | 141 | 0.042342 | 0.056640 | 0.033653 | -0.132989 |
| 21 | early | date_only_ridge | 141 | 0.039614 | 0.054878 | 0.032479 | 0.005582 |
| 21 | early | pooled_market_factor | 141 | 0.044976 | 0.059280 | 0.036144 | -0.119907 |
| 21 | later | date_only_no_position | 76 | 0.036805 | 0.048194 | 0.027237 | 0.066111 |
| 21 | later | date_only_ridge | 76 | 0.033178 | 0.046087 | 0.026651 | 0.349692 |
| 21 | later | pooled_market_factor | 76 | 0.036213 | 0.047477 | 0.026817 | 0.121367 |

Pooled observations can reduce per-stock estimation error. The independent comparison and the date-only comparison answer different questions. The former tests security parameters and the latter tests whether that accuracy reaches the index.

[equity-fit-receipts.csv](equity-fit-receipts.csv) · [equity-model-config.json](equity-model-config.json) · [pooled-coefficients-5.json](pooled-coefficients-5.json) · [pooled-coefficients-21.json](pooled-coefficients-21.json) · [stock-leaderboard.csv](stock-leaderboard.csv) · [market-factor-leaderboard.csv](market-factor-leaderboard.csv) · [synthetic-power-summary.csv](synthetic-power-summary.csv)
