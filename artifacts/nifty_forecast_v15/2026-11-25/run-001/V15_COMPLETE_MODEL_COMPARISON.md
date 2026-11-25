# V15 objective-by-objective comparison

The comparisons below use the frozen research-exposed sample. Each row is a specific target, model and support. Reading each objective separately preserves the distinct winners. Metric-specific origin counts and cross-vintage exact matching are in the linked artifacts. Gain in paired tables is control loss minus candidate loss. The normalized multivariate energy score, coverage, calibration, mean forecasts, mean biases, and per-origin distribution metrics are available in the larger tables.

## Original weekly and monthly direction

| horizon | model | origins | brier | log loss | correct | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.228529 | 0.648943 | 0.626415 | 0.636001 |
| 5 | V13_IV_all_phase | 265 | 0.229587 | 0.651757 | 0.626415 | 0.636001 |
| 5 | V12_NATIVE_RV | 265 | 0.229715 | 0.655524 | 0.626415 | 0.633316 |
| 5 | J11_BREADTH_ALL | 265 | 0.236138 | 0.667636 | 0.637736 | 0.650612 |
| 21 | V14_domestic_GJR | 217 | 0.245042 | 0.683095 | 0.511521 | 0.502675 |
| 21 | heavy_tail | 217 | 0.247524 | 0.688176 | 0.543779 | 0.548835 |
| 21 | incremental | 217 | 0.247623 | 0.688373 | 0.539171 | 0.544737 |
| 21 | iv_restart | 217 | 0.247721 | 0.688575 | 0.534562 | 0.537144 |

## Original weekly and monthly return distributions

| horizon | model | origins | endpoint crps | endpoint pinball | endpoint mae | endpoint cov80 | endpoint width80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.010457 | 0.003627 | 0.014842 | 0.826415 | 0.045780 |
| 5 | V13_weekly_CRPS | 265 | 0.010472 | 0.005166 | 0.014903 | 0.788679 | 0.043399 |
| 5 | V13_IV_all_phase | 265 | 0.010609 | 0.005235 | 0.015013 | 0.807547 | 0.044748 |
| 5 | iv_restart | 265 | 0.010682 | 0.004362 | 0.014979 | 0.800000 | 0.047500 |
| 21 | gjr_restart | 217 | 0.024694 | 0.010262 | 0.033162 | 0.709677 | 0.083754 |
| 21 | hybrid | 217 | 0.024715 | 0.010317 | 0.033184 | 0.714286 | 0.085546 |
| 21 | V14_regime_state_joint | 217 | 0.024750 | 0.008795 | 0.033593 | 0.741935 | 0.091201 |
| 21 | particle | 217 | 0.024756 | 0.010296 | 0.033248 | 0.700461 | 0.083348 |

## Volatility levels and expansion

| horizon | model | n | mae | qlike |
| --- | --- | --- | --- | --- |
| 5 | V14_GJR_IVx | 265 | 0.037402 | 0.299575 |
| 5 | iv_raw | 265 | 0.037814 | 0.276187 |
| 5 | V14_IV_GJR | 265 | 0.037978 | 0.287184 |
| 21 | V13_GJR | 217 | 0.033179 | 0.199677 |
| 21 | V14_IV_GJR | 217 | 0.033780 | 0.247374 |
| 21 | V14_GJR_t | 217 | 0.035464 | 0.263397 |
| 5 | fixed_75IV25RV | 265 | 0.038484 | 0.286114 |
| 21 | India_VIX | 217 | 0.039352 | 0.206322 |
| 21 | V14_EGARCH_t | 217 | 0.035730 | 0.207684 |

| horizon | model | n | brier | log loss | p | actual rate |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | fixed_75IV25RV | 265 | 0.152707 | 0.461636 | 0.327067 | 0.328302 |
| 5 | iv_frequency_mix | 265 | 0.154727 | 0.469056 | 0.352924 | 0.328302 |
| 5 | iv_change_only | 265 | 0.155111 | 0.466824 | 0.333522 | 0.328302 |
| 5 | iv_offset_intercept | 265 | 0.155409 | 0.467000 | 0.334426 | 0.328302 |
| 21 | V14_EGARCH_t | 217 | 0.172872 | 0.689982 | 0.287098 | 0.373272 |
| 21 | iv_raw | 217 | 0.186036 | 0.829771 | 0.278692 | 0.373272 |
| 21 | iv_frequency_mix | 217 | 0.186445 | 0.632147 | 0.271542 | 0.373272 |
| 21 | India_VIX | 217 | 0.187341 | 0.700282 | 0.380623 | 0.373272 |

## Trading ranges and coherent joint scores

| horizon | model | origins | range crps | range cov80 | range width80 | range is80 | joint energy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | incremental | 265 | 0.005763 | 0.781132 | 0.021414 | 0.037504 | 0.669712 |
| 5 | iv_restart | 265 | 0.005795 | 0.747170 | 0.021822 | 0.037857 | 0.670200 |
| 5 | price_only | 265 | 0.005795 | 0.747170 | 0.021822 | 0.037857 | 0.670200 |
| 5 | shock_persistence | 265 | 0.005795 | 0.747170 | 0.021822 | 0.037857 | 0.670200 |
| 21 | frozen | 217 | 0.015422 | 0.764977 | 0.044758 | 0.100304 | 0.767308 |
| 21 | particle | 217 | 0.015438 | 0.760369 | 0.044820 | 0.100568 | 0.771126 |
| 21 | gjr_restart | 217 | 0.015488 | 0.737327 | 0.043768 | 0.101794 | 0.766246 |
| 21 | incremental | 217 | 0.015513 | 0.658986 | 0.044025 | 0.106779 | 0.763496 |

## Barrier touch at issue

| horizon | model | origins | n | brier | log loss | integrated brier |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | hybrid | 265 | 2,650 | 0.144009 | 0.440666 | 0.119656 |
| 5 | full_permuted | 265 | 2,650 | 0.144159 | 0.441315 | 0.120105 |
| 5 | episode_tail | 265 | 2,650 | 0.144427 | 0.439948 | 0.120293 |
| 5 | incremental | 265 | 2,650 | 0.144546 | 0.440974 | 0.120046 |
| 5 | iv_restart | 265 | 2,650 | 0.144592 | 0.438884 | 0.120264 |
| 21 | incremental | 217 | 2,170 | 0.181938 | 0.547509 | 0.158928 |
| 21 | vol_state | 217 | 2,170 | 0.183015 | 0.547999 | 0.159466 |
| 21 | episode_tail | 217 | 2,170 | 0.183111 | 0.549952 | 0.158906 |
| 21 | iv_restart | 217 | 2,170 | 0.183126 | 0.551006 | 0.159269 |
| 21 | price_only | 217 | 2,170 | 0.183126 | 0.551006 | 0.159269 |

## First passage during updates

| horizon | model | origins | n | brier | integrated brier | passage log loss |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | hybrid | 265 | 15,430 | 0.078278 | 0.060308 | 0.378474 |
| 5 | price_only | 265 | 15,430 | 0.078037 | 0.060343 | 0.380280 |
| 5 | incremental | 265 | 15,430 | 0.078331 | 0.060403 | 0.380753 |
| 5 | particle | 265 | 15,430 | 0.078531 | 0.060450 | 0.383708 |
| 5 | vol_state | 265 | 15,430 | 0.078419 | 0.060462 | 0.379343 |
| 21 | incremental | 217 | 54,600 | 0.107851 | 0.072138 | 0.829002 |
| 21 | vol_state | 217 | 54,600 | 0.108246 | 0.072209 | 0.824253 |
| 21 | vol_only_shock | 217 | 54,600 | 0.108536 | 0.072213 | 0.833745 |
| 21 | episode_tail | 217 | 54,600 | 0.108917 | 0.072266 | 0.837401 |
| 21 | iv_restart | 217 | 54,600 | 0.108726 | 0.072306 | 0.834246 |

## Fixed-endpoint and sequential gain on matched windows

| horizon | metric | candidate | n | model | control | gain | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | brier | domestic | 265 | 0.159648 | 0.162131 | 0.002484 | -0.007784 | 0.012752 |
| 5 | brier | refit | 265 | 0.160464 | 0.162131 | 0.001667 | -0.008631 | 0.011965 |
| 5 | brier | sign_magnitude | 265 | 0.160809 | 0.162131 | 0.001322 | -0.004072 | 0.006716 |
| 5 | brier | full | 265 | 0.161190 | 0.162131 | 0.000942 | -0.011126 | 0.013010 |
| 5 | endpoint_crps | vol_only_shock | 265 | 0.007261 | 0.007264 | 0.000003 | -0.000015 | 0.000022 |
| 5 | endpoint_crps | heavy_tail | 265 | 0.007265 | 0.007264 | -0.000001 | -0.000007 | 0.000006 |
| 5 | endpoint_crps | incremental | 265 | 0.007270 | 0.007264 | -0.000006 | -0.000057 | 0.000045 |
| 5 | endpoint_crps | episode_tail | 265 | 0.007277 | 0.007264 | -0.000013 | -0.000092 | 0.000066 |
| 5 | remaining_brier | incremental | 265 | 0.249090 | 0.249133 | 0.000044 | -0.002990 | 0.003077 |
| 5 | remaining_brier | vol_only_shock | 265 | 0.249133 | 0.249133 | 0.000000 | -0.000000 | 0.000000 |
| 5 | remaining_brier | heavy_tail | 265 | 0.249452 | 0.249133 | -0.000318 | -0.000523 | -0.000114 |
| 5 | remaining_brier | episode_tail | 265 | 0.249509 | 0.249133 | -0.000376 | -0.003631 | 0.002880 |
| 5 | remaining_return_crps | vol_only_shock | 265 | 0.007251 | 0.007255 | 0.000003 | -0.000015 | 0.000021 |
| 5 | remaining_return_crps | heavy_tail | 265 | 0.007255 | 0.007255 | -0.000001 | -0.000007 | 0.000006 |
| 5 | remaining_return_crps | incremental | 265 | 0.007261 | 0.007255 | -0.000006 | -0.000057 | 0.000044 |
| 5 | remaining_return_crps | episode_tail | 265 | 0.007267 | 0.007255 | -0.000013 | -0.000091 | 0.000065 |
| 21 | brier | vol_only_shock | 217 | 0.166696 | 0.166627 | -0.000069 | -0.000557 | 0.000418 |
| 21 | brier | heavy_tail | 217 | 0.166699 | 0.166627 | -0.000072 | -0.000255 | 0.000111 |
| 21 | brier | vol_state | 217 | 0.168162 | 0.166627 | -0.001535 | -0.005772 | 0.002702 |
| 21 | brier | incremental | 217 | 0.168683 | 0.166627 | -0.002056 | -0.008021 | 0.003908 |
| 21 | endpoint_crps | vol_only_shock | 217 | 0.016877 | 0.016893 | 0.000016 | -0.000035 | 0.000066 |
| 21 | endpoint_crps | vol_state | 217 | 0.016880 | 0.016893 | 0.000013 | -0.000309 | 0.000335 |
| 21 | endpoint_crps | incremental | 217 | 0.016893 | 0.016893 | -0.000000 | -0.000653 | 0.000653 |
| 21 | endpoint_crps | heavy_tail | 217 | 0.016897 | 0.016893 | -0.000004 | -0.000016 | 0.000009 |
| 21 | remaining_brier | vol_only_shock | 217 | 0.249073 | 0.249073 | 0.000000 | -0.000000 | 0.000000 |
| 21 | remaining_brier | heavy_tail | 217 | 0.249172 | 0.249073 | -0.000099 | -0.000324 | 0.000127 |
| 21 | remaining_brier | incremental | 217 | 0.250609 | 0.249073 | -0.001536 | -0.015819 | 0.012748 |
| 21 | remaining_brier | vol_state | 217 | 0.251170 | 0.249073 | -0.002097 | -0.009702 | 0.005509 |
| 21 | remaining_return_crps | vol_only_shock | 217 | 0.016995 | 0.017010 | 0.000016 | -0.000034 | 0.000066 |
| 21 | remaining_return_crps | vol_state | 217 | 0.017001 | 0.017010 | 0.000009 | -0.000311 | 0.000330 |
| 21 | remaining_return_crps | incremental | 217 | 0.017008 | 0.017010 | 0.000002 | -0.000664 | 0.000668 |
| 21 | remaining_return_crps | heavy_tail | 217 | 0.017014 | 0.017010 | -0.000004 | -0.000016 | 0.000009 |

## Interval calibration at original issue

| horizon | model | n | endpoint cov50 | endpoint cov80 | endpoint width80 | endpoint pinball | endpoint is80 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | iv_restart | 265 | 0.532075 | 0.800000 | 0.047500 | 0.004362 | 0.068489 |
| 5 | price_only | 265 | 0.532075 | 0.800000 | 0.047500 | 0.004362 | 0.068489 |
| 5 | shock_persistence | 265 | 0.532075 | 0.800000 | 0.047500 | 0.004362 | 0.068489 |
| 5 | vol_only_shock | 265 | 0.532075 | 0.800000 | 0.047500 | 0.004362 | 0.068489 |
| 5 | heavy_tail | 265 | 0.535849 | 0.807547 | 0.047279 | 0.004364 | 0.068575 |
| 21 | gjr_restart | 217 | 0.437788 | 0.709677 | 0.083754 | 0.010262 | 0.167267 |
| 21 | frozen | 217 | 0.419355 | 0.718894 | 0.083314 | 0.010323 | 0.167613 |
| 21 | particle | 217 | 0.428571 | 0.700461 | 0.083348 | 0.010296 | 0.168319 |
| 21 | hybrid | 217 | 0.442396 | 0.714286 | 0.085546 | 0.010317 | 0.168655 |
| 21 | vol_state | 217 | 0.447005 | 0.732719 | 0.087732 | 0.010370 | 0.169313 |

[Incremental block comparison](V15_INCREMENTAL_INFORMATION_VALUE.md) [Disjoint phases and adjusted uncertainty](V15_EPISODE_LEVEL_EVALUATION.md) [Volatility transitions](V15_VOLATILITY_EXPANSION_INTELLIGENCE.md) [Calibration, raw and joint losses](checkpoint-leaderboard.csv) [Full cross-vintage comparison](cross-vintage-endpoint-leaderboard.csv) [All first-passage comparisons](passage-leaderboard.csv)
