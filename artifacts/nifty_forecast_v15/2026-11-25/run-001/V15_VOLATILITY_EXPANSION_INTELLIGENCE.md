# V15 volatility transitions and expansion

The five transition targets are a 25% increase in H-session realized volatility, a 50% increase, a 20% contraction, entry into the training-only high-volatility state and elevated volatility across both halves of the future window. The high-volatility threshold is the 75th percentile of earlier matured volatility. High entry uses only eligible initially lower-risk observations, and persistence uses the V14 two-half definition. The extra 50% expansion was fixed before evaluating V15. Volatility magnitude is evaluated separately in annualized units. The same trailing-risk anchor sets expansion and contraction thresholds.

## Transition scores

| horizon | event | model | n | p | actual rate | brier | log loss | brier gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | contract | V14_IV_GJR | 265 | 0.294314 | 0.286792 | 0.131189 | 0.402972 | 0.000527 |
| 5 | contract | iv_offsets_delayed | 265 | 0.284799 | 0.286792 | 0.131471 | 0.405538 | 0.000245 |
| 5 | contract | iv_raw | 265 | 0.293246 | 0.286792 | 0.131716 | 0.405392 | 0.000000 |
| 5 | contract | historical | 265 | 0.248034 | 0.286792 | 0.205321 | 0.601384 | -0.073605 |
| 5 | enter_high | iv_offsets_delayed | 170 | 0.230455 | 0.247059 | 0.143264 | 0.455064 | 0.008561 |
| 5 | enter_high | iv_change_only | 170 | 0.217923 | 0.247059 | 0.146593 | 0.463288 | 0.005233 |
| 5 | enter_high | iv_offset_intercept | 170 | 0.218196 | 0.247059 | 0.147252 | 0.465418 | 0.004573 |
| 5 | enter_high | iv_raw | 170 | 0.256830 | 0.247059 | 0.151825 | 0.478338 | 0.000000 |
| 5 | enter_high | historical | 170 | 0.150774 | 0.247059 | 0.200170 | 0.657184 | -0.048345 |
| 5 | expand | fixed_75IV25RV | 265 | 0.327067 | 0.328302 | 0.152707 | 0.461636 | 0.002949 |
| 5 | expand | iv_frequency_mix | 265 | 0.352924 | 0.328302 | 0.154727 | 0.469056 | 0.000930 |
| 5 | expand | iv_change_only | 265 | 0.333522 | 0.328302 | 0.155111 | 0.466824 | 0.000546 |
| 5 | expand | iv_raw | 265 | 0.356195 | 0.328302 | 0.155657 | 0.466192 | 0.000000 |
| 5 | expand | historical | 265 | 0.329628 | 0.328302 | 0.222296 | 0.636990 | -0.066639 |
| 5 | expand50 | fixed_75IV25RV | 265 | 0.190047 | 0.188679 | 0.114950 | 0.363446 | 0.003851 |
| 5 | expand50 | iv_frequency_mix | 265 | 0.218516 | 0.188679 | 0.115764 | 0.366484 | 0.003037 |
| 5 | expand50 | iv_change_only | 265 | 0.199293 | 0.188679 | 0.117305 | 0.371212 | 0.001495 |
| 5 | expand50 | iv_raw | 265 | 0.225829 | 0.188679 | 0.118801 | 0.374791 | 0.000000 |
| 5 | expand50 | historical | 265 | 0.162453 | 0.188679 | 0.154076 | 0.488374 | -0.035275 |
| 5 | persist_high | iv_raw | 265 | 0.190417 | 0.200000 | 0.103090 | 0.346090 | 0.000000 |
| 5 | persist_high | V14_IV_GJR | 265 | 0.177521 | 0.200000 | 0.104226 | 0.356155 | -0.001136 |
| 5 | persist_high | iv_offset_intercept | 265 | 0.181533 | 0.200000 | 0.104379 | 0.348879 | -0.001289 |
| 5 | persist_high | historical | 265 | 0.132492 | 0.200000 | 0.188428 | 0.695758 | -0.085338 |
| 21 | contract | V13_GJR | 217 | 0.212490 | 0.235023 | 0.107854 | 0.343784 | 0.063397 |
| 21 | contract | V14_IV_GJR | 217 | 0.248002 | 0.235023 | 0.122742 | 0.365486 | 0.048509 |
| 21 | contract | V14_EGARCH_t | 217 | 0.170014 | 0.235023 | 0.123863 | 0.382266 | 0.047388 |
| 21 | contract | iv_raw | 217 | 0.176689 | 0.235023 | 0.171251 | 0.520177 | 0.000000 |
| 21 | contract | historical | 217 | 0.154306 | 0.235023 | 0.200138 | 0.628775 | -0.028887 |
| 21 | enter_high | fixed_75IV25RV | 150 | 0.244313 | 0.266667 | 0.181016 | 0.713917 | 0.010418 |
| 21 | enter_high | iv_offsets_random | 150 | 0.231439 | 0.266667 | 0.181067 | 0.639809 | 0.010367 |
| 21 | enter_high | iv_offset_intercept | 150 | 0.230243 | 0.266667 | 0.181208 | 0.639821 | 0.010226 |
| 21 | enter_high | iv_raw | 150 | 0.292806 | 0.266667 | 0.191434 | 0.671911 | 0.000000 |
| 21 | enter_high | historical | 150 | 0.127648 | 0.266667 | 0.241019 | 1.029585 | -0.049585 |
| 21 | expand | V14_EGARCH_t | 217 | 0.287098 | 0.373272 | 0.172872 | 0.689982 | 0.013164 |
| 21 | expand | iv_raw | 217 | 0.278692 | 0.373272 | 0.186036 | 0.829771 | 0.000000 |
| 21 | expand | iv_frequency_mix | 217 | 0.271542 | 0.373272 | 0.186445 | 0.632147 | -0.000409 |
| 21 | expand | historical | 217 | 0.210386 | 0.373272 | 0.299434 | 0.910763 | -0.113397 |
| 21 | expand50 | India_VIX | 217 | 0.152652 | 0.253456 | 0.132865 | 0.537817 | 0.013139 |
| 21 | expand50 | iv_raw | 217 | 0.096835 | 0.253456 | 0.146004 | 0.662092 | 0.000000 |
| 21 | expand50 | iv_offsets_random | 217 | 0.099850 | 0.253456 | 0.149681 | 0.565463 | -0.003677 |
| 21 | expand50 | historical | 217 | 0.129934 | 0.253456 | 0.229320 | 0.967097 | -0.083315 |
| 21 | persist_high | V14_IV_GJR | 217 | 0.288493 | 0.350230 | 0.083961 | 0.304345 | 0.017942 |
| 21 | persist_high | fixed_75IV25RV | 217 | 0.318559 | 0.350230 | 0.091713 | 0.312041 | 0.010190 |
| 21 | persist_high | V13_GJR | 217 | 0.342538 | 0.350230 | 0.094005 | 0.314075 | 0.007898 |
| 21 | persist_high | iv_raw | 217 | 0.321310 | 0.350230 | 0.101904 | 0.335821 | 0.000000 |
| 21 | persist_high | historical | 217 | 0.231175 | 0.350230 | 0.364541 | 1.451884 | -0.262637 |

## Paired 25% expansion tests

| horizon | model | n | gain | low10 | high10 | family low21 | family high21 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_EGARCH_t | 265 | -0.022209 | -0.046849 | 0.001750 | -0.058389 | 0.013971 |
| 5 | fixed_75IV25RV | 265 | 0.002949 | -0.005733 | 0.011970 | -0.009143 | 0.015042 |
| 5 | historical | 265 | -0.066639 | -0.104912 | -0.028606 | -0.115320 | -0.017958 |
| 5 | iv_change_only | 265 | 0.000546 | -0.004451 | 0.005966 | -0.008068 | 0.009160 |
| 5 | iv_level_change | 265 | -0.001024 | -0.007378 | 0.004822 | -0.010843 | 0.008794 |
| 5 | iv_offsets_all | 265 | -0.007522 | -0.019575 | 0.001248 | -0.022903 | 0.007860 |
| 21 | V14_EGARCH_t | 217 | 0.013164 | -0.040531 | 0.068282 | -0.074974 | 0.101302 |
| 21 | fixed_75IV25RV | 217 | -0.008331 | -0.030423 | 0.015453 | -0.044105 | 0.027443 |
| 21 | historical | 217 | -0.113397 | -0.233756 | -0.013504 | -0.307384 | 0.080589 |
| 21 | iv_change_only | 217 | -0.010774 | -0.044517 | 0.019172 | -0.062801 | 0.041253 |
| 21 | iv_level_change | 217 | -0.013375 | -0.045164 | 0.014977 | -0.064203 | 0.037454 |
| 21 | iv_offsets_all | 217 | -0.022574 | -0.053282 | 0.007561 | -0.074581 | 0.029434 |

## Volatility point estimates

| horizon | model | n | forecast vol | true vol | mae | qlike |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_GJR_IVx | 265 | 0.120794 | 0.123981 | 0.037402 | 0.299575 |
| 5 | iv_raw | 265 | 0.131751 | 0.123981 | 0.037814 | 0.276187 |
| 5 | V14_IV_GJR | 265 | 0.127865 | 0.123981 | 0.037978 | 0.287184 |
| 5 | fixed_75IV25RV | 265 | 0.130858 | 0.123981 | 0.038484 | 0.286114 |
| 5 | V14_EGARCH_t | 265 | 0.133987 | 0.123981 | 0.039960 | 0.327199 |
| 5 | iv_level_change_risk | 265 | 0.120707 | 0.123981 | 0.040246 | 0.354978 |
| 5 | V14_GJR_t | 265 | 0.121007 | 0.123981 | 0.040250 | 0.370739 |
| 5 | V13_GJR | 265 | 0.126852 | 0.123981 | 0.040318 | 0.359870 |
| 5 | persistence_ewma | 265 | 0.125995 | 0.123981 | 0.043105 | 0.369007 |
| 5 | India_VIX | 265 | 0.142175 | 0.123981 | 0.044013 | 0.320104 |
| 5 | same_horizon_trailing | 265 | 0.122699 | 0.123981 | 0.048282 | 0.878672 |
| 21 | V13_GJR | 217 | 0.128738 | 0.138004 | 0.033179 | 0.199677 |
| 21 | V14_IV_GJR | 217 | 0.122337 | 0.138004 | 0.033780 | 0.247374 |
| 21 | V14_GJR_t | 217 | 0.118584 | 0.138004 | 0.035464 | 0.263397 |
| 21 | V14_EGARCH_t | 217 | 0.135372 | 0.138004 | 0.035730 | 0.207684 |
| 21 | V14_GJR_IVx | 217 | 0.122269 | 0.138004 | 0.037160 | 0.310001 |
| 21 | India_VIX | 217 | 0.144170 | 0.138004 | 0.039352 | 0.206322 |
| 21 | iv_raw | 217 | 0.133599 | 0.138004 | 0.039406 | 0.267623 |
| 21 | fixed_75IV25RV | 217 | 0.133372 | 0.138004 | 0.040894 | 0.257953 |
| 21 | persistence_ewma | 217 | 0.130703 | 0.138004 | 0.043294 | 0.370716 |
| 21 | same_horizon_trailing | 217 | 0.129820 | 0.138004 | 0.046593 | 0.440755 |
| 21 | iv_level_change_risk | 217 | 0.128768 | 0.138004 | 0.050170 | 0.479093 |

Raw-IV probability retains the V14 chi-square mapping. The persistence experiment also tests a product of independent chi-square tails over two chunks, a diagnostic approximation. GJR, EGARCH, India VIX, trailing RV, EWMA and simple variance mixtures each enter that same mapping. V15's fixed 75/25 risk event substitute uses H-session RV. The reproduced V13 point mixture uses the older HAR volatility input. Regularized offsets operate on the raw IV log odds, with an intercept-only control. The level-only, change-only, level-and-change, full risk and delayed or permuted controls distinguish calibration from extra information. Weekly full and placebo scores, monthly log loss and probability-versus-frequency gaps remain visible. Magnitude MAE and variance QLIKE can favor separate processes. Every fitted row enforces the earlier maturity cut.

[Complete transition leaderboard](volatility-transition-evidence.csv) [Per-origin probabilities](volatility-transition-scores.csv.gz) [Volatility levels by origin](volatility-level-scores.csv) [Fitted transition offsets](volatility-transition-fit-ledger.json) [Paired uncertainty](secondary-paired-evidence.csv)
