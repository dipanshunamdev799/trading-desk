# V20 Predictability And Information Limits

The five-session sample has 53 non-overlapping windows and the 21-session sample has 11. A 159-origin active V19 monthly analysis has just eight disjoint windows. The lifetime matrix records linear and rank association with baseline residuals, cross-validated incremental squared-error reduction, and earlier and later effects. Opening gaps, regular-session returns and late monthly outcomes are measured separately.

| feature | target | n | spearman |
| --- | --- | --- | --- |
| gift_proxy | gap | 387 | 0.829703 |
| gift_proxy | initial_rth | 387 | 0.097117 |
| gift_proxy | original1 | 387 | 0.589065 |
| gift_proxy | return_0_5 | 383 | 0.182527 |
| gift_proxy | return_5_21 | 369 | -0.036635 |
| eq6 | gap | 402 | 0.344761 |
| eq6 | initial_rth | 402 | -0.077275 |
| eq6 | original1 | 402 | 0.157157 |
| eq6 | return_0_5 | 398 | 0.004556 |
| eq6 | return_5_21 | 382 | -0.023711 |
| domestic_rotation_finance | gap | 402 | -0.032333 |
| domestic_rotation_finance | initial_rth | 402 | -0.048611 |
| domestic_rotation_finance | original1 | 402 | -0.057875 |
| domestic_rotation_finance | return_0_5 | 398 | -0.134110 |
| domestic_rotation_finance | return_5_21 | 382 | 0.181412 |
| FII_index_futures_d21 | gap | 400 | -0.035119 |
| FII_index_futures_d21 | initial_rth | 400 | -0.021473 |
| FII_index_futures_d21 | original1 | 400 | -0.054980 |
| FII_index_futures_d21 | return_0_5 | 396 | -0.079766 |
| FII_index_futures_d21 | return_5_21 | 380 | -0.200075 |
| count9 | gap | 402 | -0.019050 |
| count9 | initial_rth | 402 | 0.008562 |
| count9 | original1 | 402 | 0.008665 |
| count9 | return_0_5 | 398 | 0.108993 |
| count9 | return_5_21 | 382 | -0.142099 |

For an approximate power calculation we demeaned paired historical losses, applied **1,000** circular block resamples per design and measured the two-sided 95% threshold of the resulting null distribution. The gain needed to reach 80% power adds a constant effect to that centered process. This assumes the historical serial structure and loss dispersion recur, an unchanged parent, the same target geometry and comparable measurement quality. Longer blocks give a sensitivity. Small signals remain within the observed uncertainty.

| horizon | metric | block | n | disjoint | mean gain | approx 80 percent detectable gain | estimated power at observed gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | 5 | 265 | 53 | 0.005048 | 0.020896 | 0.099000 |
| 5 | brier | 10 | 265 | 53 | 0.005048 | 0.023293 | 0.090000 |
| 5 | brier | 21 | 265 | 53 | 0.005048 | 0.022183 | 0.104000 |
| 5 | brier | 42 | 265 | 53 | 0.005048 | 0.022105 | 0.106000 |
| 5 | crps | 5 | 265 | 53 | 0.000139 | 0.000793 | 0.082000 |
| 5 | crps | 10 | 265 | 53 | 0.000139 | 0.000909 | 0.064000 |
| 5 | crps | 21 | 265 | 53 | 0.000139 | 0.000906 | 0.074000 |
| 5 | crps | 42 | 265 | 53 | 0.000139 | 0.000865 | 0.094000 |
| 21 | brier | 5 | 217 | 11 | 0.016844 | 0.045237 | 0.171000 |
| 21 | brier | 10 | 217 | 11 | 0.016844 | 0.055396 | 0.142000 |
| 21 | brier | 21 | 217 | 11 | 0.016844 | 0.068920 | 0.114000 |
| 21 | brier | 42 | 217 | 11 | 0.016844 | 0.071299 | 0.104000 |
| 21 | crps | 5 | 217 | 11 | 0.000979 | 0.001786 | 0.346000 |
| 21 | crps | 10 | 217 | 11 | 0.000979 | 0.002234 | 0.217000 |
| 21 | crps | 21 | 217 | 11 | 0.000979 | 0.002452 | 0.216000 |
| 21 | crps | 42 | 217 | 11 | 0.000979 | 0.002303 | 0.242000 |

Bank and IT relative returns act as auxiliary responses in a reduced-rank fit. They use the same earlier market dates. The number of independent outcomes comes from the NIFTY targets. Training-window, expiry and time-block sensitivities characterize additional sources of estimation variation.

| horizon | model | n | disjoint | brier | crps | rank corr |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | F_regularized_multihorizon | 265 | 53 | 0.256197 | 0.011641 | -0.044554 |
| 5 | archived_same_clock | 265 | 53 | 0.238113 | 0.010309 | 0.290602 |
| 5 | auxiliary_sector_shared_heads | 265 | 53 | 0.258921 | 0.011649 | -0.062237 |
| 21 | F_regularized_multihorizon | 217 | 11 | 0.317080 | 0.031224 | -0.121656 |
| 21 | archived_same_clock | 217 | 11 | 0.250000 | 0.025543 | 0.141568 |
| 21 | auxiliary_sector_shared_heads | 217 | 11 | 0.312506 | 0.031056 | -0.094403 |

[predictability-power-simulation.csv](predictability-power-simulation.csv) · [information-lifetime-matrix.csv](information-lifetime-matrix.csv) · [coefficient-stability.csv](coefficient-stability.csv) · [all-disjoint-window-phases.csv](all-disjoint-window-phases.csv) · [episode-omission-sensitivity.csv](episode-omission-sensitivity.csv) · [architecture-training-receipts.csv](architecture-training-receipts.csv)
