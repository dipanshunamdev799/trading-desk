# V11 Intelligent Training Memory

V10's oldest 85 had almost the same Brier as the spread 85 while using about 17.326 overlap-adjusted effective observations versus 62.392. V11 tests the same idea using a stronger rotation family and budgets **85, 126, 189, 252, 300 and expanding**, with exact date eligibility for every contest. Recent, earliest, even-spread, neighboring blocks, random blocks, balanced risk/rotation and diverse volatility/trend/bank episodes hold nominal rows fixed where possible. Random blocks and removing one to three likely influential recent months serve as sensitivity controls. Larger budgets skip folds with insufficient mature observations. The distinct return-session and information counts cannot generally both match when comparing spread against contiguous rows.

The new adaptive selector retains half the dates across history and fills remaining places using previously matured monthly loss results with a 12-observation shrinkage prior and rotation across months. This estimates prior forecasting conditions for a historical block. The bookkeeping does not identify the causal effect of training on that block. The initialized methods and their exact date lists remain available.

On the full weekly chronology, spread 85 reduced Brier from **0.314853** to **0.248811**. The learned selector scored **0.272490**, and random blocks scored **0.256744**. Spread improved both cohorts against the recent window, with much more of the improvement late. It scored better than random blocks on combined Brier. Random blocks achieved lower combined CRPS.

| model | early brier | later brier | combined brier | early crps | later crps | combined crps |
| --- | --- | --- | --- | --- | --- | --- |
| M_OMIT_SPREAD1 | 0.268136 | 0.204061 | 0.245891 | 0.011423 | 0.010946 | 0.011257 |
| M_SPREAD_85 | 0.280790 | 0.188677 | 0.248811 | 0.012378 | 0.010954 | 0.011883 |
| M_DIVERSE_85 | 0.278472 | 0.208059 | 0.254027 | 0.012177 | 0.011398 | 0.011907 |
| M_OMIT_SPREAD2 | 0.283715 | 0.202072 | 0.255371 | 0.012721 | 0.011449 | 0.012279 |
| M_RANDOM_BLOCKS_85 | 0.273939 | 0.224410 | 0.256744 | 0.011971 | 0.011449 | 0.011790 |
| M_EARLIEST_85 | 0.274014 | 0.224423 | 0.256798 | 0.011492 | 0.012486 | 0.011838 |
| M_OMIT_SPREAD3 | 0.291656 | 0.193014 | 0.257410 | 0.012426 | 0.011264 | 0.012023 |
| M_BALANCE_ROTATION_85 | 0.289115 | 0.204836 | 0.259856 | 0.012504 | 0.011335 | 0.012098 |
| M_USEFULNESS_85 | 0.291552 | 0.236643 | 0.272490 | 0.012555 | 0.012055 | 0.012382 |
| M_OMIT_RECENT3 | 0.284586 | 0.280783 | 0.283266 | 0.013881 | 0.012396 | 0.013365 |
| M_BALANCE_VOL_85 | 0.324936 | 0.248171 | 0.298285 | 0.013822 | 0.012245 | 0.013274 |
| M_OMIT_RECENT2 | 0.308755 | 0.278610 | 0.298290 | 0.014793 | 0.013277 | 0.014267 |
| M_OMIT_RECENT1 | 0.297119 | 0.317054 | 0.304040 | 0.013583 | 0.014174 | 0.013788 |
| M_RECENT_85 | 0.291540 | 0.358692 | 0.314853 | 0.014007 | 0.015234 | 0.014433 |

## Median later-cohort training information

| horizon | model | training | distinct_return_sessions | disjoint_training_windows | kish_ESS | overlap_effective_count |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | M_BALANCE_ROTATION_85 | 85.000000 | 258.000000 | 44.000000 | 85.000000 | 42.550059 |
| 5 | M_BALANCE_VOL_85 | 85.000000 | 288.000000 | 45.000000 | 85.000000 | 49.016282 |
| 5 | M_DIVERSE_85 | 85.000000 | 257.000000 | 41.000000 | 85.000000 | 42.954816 |
| 5 | M_EARLIEST_85 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 |
| 5 | M_OMIT_RECENT1 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 |
| 5 | M_OMIT_RECENT2 | 85.000000 | 93.000000 | 17.000000 | 85.000000 | 17.665037 |
| 5 | M_OMIT_RECENT3 | 85.000000 | 93.000000 | 18.000000 | 85.000000 | 17.665037 |
| 5 | M_OMIT_SPREAD1 | 85.000000 | 333.000000 | 43.000000 | 85.000000 | 59.318555 |
| 5 | M_OMIT_SPREAD2 | 85.000000 | 326.000000 | 43.000000 | 85.000000 | 57.985554 |
| 5 | M_OMIT_SPREAD3 | 85.000000 | 328.000000 | 43.000000 | 85.000000 | 58.360258 |
| 5 | M_RANDOM_BLOCKS_85 | 85.000000 | 137.000000 | 17.000000 | 85.000000 | 22.507788 |
| 5 | M_RECENT_85 | 85.000000 | 89.000000 | 17.000000 | 85.000000 | 17.326139 |
| 5 | M_SPREAD_85 | 85.000000 | 348.000000 | 44.000000 | 85.000000 | 62.392055 |
| 5 | M_USEFULNESS_85 | 85.000000 | 262.000000 | 42.000000 | 85.000000 | 40.005537 |
| 21 | M_BALANCE_ROTATION_85 | 85.000000 | 331.500000 | 14.000000 | 85.000000 | 14.186353 |
| 21 | M_BALANCE_VOL_85 | 85.000000 | 333.000000 | 13.500000 | 85.000000 | 14.143871 |
| 21 | M_DIVERSE_85 | 85.000000 | 324.000000 | 13.500000 | 85.000000 | 13.872417 |
| 21 | M_EARLIEST_85 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 |
| 21 | M_OMIT_RECENT1 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 |
| 21 | M_OMIT_RECENT2 | 85.000000 | 125.000000 | 5.000000 | 85.000000 | 4.842957 |
| 21 | M_OMIT_RECENT3 | 85.000000 | 124.000000 | 5.000000 | 85.000000 | 4.843266 |
| 21 | M_OMIT_SPREAD1 | 85.000000 | 326.000000 | 15.000000 | 85.000000 | 14.958592 |
| 21 | M_OMIT_SPREAD2 | 85.000000 | 334.000000 | 14.500000 | 85.000000 | 14.752359 |
| 21 | M_OMIT_SPREAD3 | 85.000000 | 336.500000 | 14.500000 | 85.000000 | 14.960853 |
| 21 | M_RANDOM_BLOCKS_85 | 85.000000 | 235.000000 | 9.000000 | 85.000000 | 9.011006 |
| 21 | M_RECENT_85 | 85.000000 | 105.000000 | 5.000000 | 85.000000 | 4.409969 |
| 21 | M_SPREAD_85 | 85.000000 | 337.500000 | 15.000000 | 85.000000 | 15.491215 |
| 21 | M_USEFULNESS_85 | 85.000000 | 337.500000 | 15.000000 | 85.000000 | 15.282253 |

[All eligible budget comparisons](memory-exact-budget-comparisons.csv) · [Forecast-date and phase stress](stress-comparisons.csv) · [Perturbed forecasts and selected dates](block-perturbation.csv).
