# V13 Validation And Falsification

Walk-forward fits enforce target maturity, train-only preprocessing and earlier option source dates. Archived duplicate inputs preserve the fitted design and future-perturbation sentinels preserve mature inputs and outcomes. The dependence-aware bootstrap uses **1,500** paired circular block resamples at lengths 5, 10, 21 and 42. The maximum standardized deviation adjusts the bands within each scored family. Monthly thin cells and sparse events retain disjoint counts. Search adjustment applies to the declared V13 contrasts and leaves prior adaptive search exposure.

For each horizon, twelve refit-and-reselection draws shuffle feature blocks around the retained raw IV anchor on an every-tenth-origin panel across five model specifications. Below are the winning null and unpermuted gains. This limited panel provides a falsification diagnostic.

| horizon | draw | model | gain |
| --- | --- | --- | --- |
| 21 | 8 | position_ridge | -0.005975 |
| 21 | 2 | shape_level | -0.005132 |
| 21 | 6 | shape_level | -0.004600 |
| 21 | 5 | shape_change | -0.004170 |
| 21 | 0 | shape_combined | -0.004007 |
| 21 | 3 | shape_level | -0.003842 |
| 21 | 1 | shape_level | -0.003204 |
| 21 | 11 | shape_level | -0.003193 |
| 21 | 9 | position_ridge | -0.002566 |
| 21 | 10 | position_ridge | -0.001629 |
| 21 | 4 | global_plus_iv | -0.001544 |
| 21 | 7 | shape_level | 0.002093 |
| 5 | 1 | global_plus_iv | 0.003785 |
| 5 | 3 | global_plus_iv | 0.004820 |
| 5 | 10 | shape_change | 0.005394 |
| 5 | 7 | global_plus_iv | 0.005997 |
| 5 | 4 | shape_change | 0.006743 |
| 5 | 9 | shape_level | 0.006962 |
| 5 | 6 | position_ridge | 0.007124 |
| 5 | 11 | global_plus_iv | 0.007590 |
| 5 | 2 | position_ridge | 0.007758 |
| 5 | 5 | shape_combined | 0.007982 |
| 5 | 0 | shape_level | 0.008208 |
| 5 | 8 | shape_change | 0.008330 |
| 21 | unpermuted | shape_change | -0.001427 |
| 5 | unpermuted | global_plus_iv | 0.007526 |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | shift_state_iv | iv_scaled | abs_return | crps | 265 | 53 | 0.006547 | 0.006563 | 0.000016 | -0.000116 | 0.000148 | -0.000130 | 0.000162 |
| 5 | combined | random_state_iv | iv_scaled | abs_return | crps | 265 | 53 | 0.006577 | 0.006563 | -0.000014 | -0.000152 | 0.000124 | -0.000157 | 0.000129 |
| 5 | combined | shift_state_iv | iv_scaled | abs_return | mae | 265 | 53 | 0.009455 | 0.009464 | 0.000009 | -0.000229 | 0.000246 | -0.000258 | 0.000275 |
| 5 | combined | random_state_iv | iv_scaled | abs_return | mae | 265 | 53 | 0.009477 | 0.009464 | -0.000013 | -0.000191 | 0.000165 | -0.000179 | 0.000153 |
| 5 | combined | random_state_iv | iv_scaled | close_high | crps | 265 | 53 | 0.007602 | 0.007645 | 0.000043 | -0.000056 | 0.000141 | -0.000072 | 0.000157 |
| 5 | combined | shift_state_iv | iv_scaled | close_high | crps | 265 | 53 | 0.007645 | 0.007645 | -0.000000 | -0.000152 | 0.000152 | -0.000119 | 0.000119 |
| 5 | combined | random_state_iv | iv_scaled | close_high | mae | 265 | 53 | 0.010148 | 0.010197 | 0.000050 | -0.000104 | 0.000203 | -0.000110 | 0.000210 |
| 5 | combined | shift_state_iv | iv_scaled | close_high | mae | 265 | 53 | 0.010187 | 0.010197 | 0.000011 | -0.000248 | 0.000269 | -0.000200 | 0.000221 |
| 5 | combined | random_state_iv | iv_scaled | close_low | crps | 265 | 53 | 0.007586 | 0.007607 | 0.000021 | -0.000124 | 0.000167 | -0.000136 | 0.000179 |
| 5 | combined | shift_state_iv | iv_scaled | close_low | crps | 265 | 53 | 0.007669 | 0.007607 | -0.000062 | -0.000338 | 0.000214 | -0.000338 | 0.000214 |
| 5 | combined | random_state_iv | iv_scaled | close_low | mae | 265 | 53 | 0.010702 | 0.010721 | 0.000019 | -0.000185 | 0.000222 | -0.000190 | 0.000227 |
| 5 | combined | shift_state_iv | iv_scaled | close_low | mae | 265 | 53 | 0.010775 | 0.010721 | -0.000054 | -0.000409 | 0.000301 | -0.000429 | 0.000321 |
| 5 | combined | random_state_iv | iv_scaled | drawdown | crps | 265 | 53 | 0.006180 | 0.006170 | -0.000010 | -0.000135 | 0.000115 | -0.000163 | 0.000143 |
| 5 | combined | shift_state_iv | iv_scaled | drawdown | crps | 265 | 53 | 0.006285 | 0.006170 | -0.000115 | -0.000521 | 0.000290 | -0.000542 | 0.000312 |
| 5 | combined | random_state_iv | iv_scaled | drawdown | mae | 265 | 53 | 0.008872 | 0.008891 | 0.000019 | -0.000133 | 0.000172 | -0.000133 | 0.000171 |
| 5 | combined | shift_state_iv | iv_scaled | drawdown | mae | 265 | 53 | 0.008947 | 0.008891 | -0.000056 | -0.000523 | 0.000412 | -0.000557 | 0.000445 |
| 5 | combined | random_state_iv | iv_scaled | high | crps | 265 | 53 | 0.007078 | 0.007131 | 0.000052 | -0.000052 | 0.000157 | -0.000075 | 0.000179 |
| 5 | combined | shift_state_iv | iv_scaled | high | crps | 265 | 53 | 0.007103 | 0.007131 | 0.000027 | -0.000136 | 0.000190 | -0.000115 | 0.000169 |
| 5 | combined | random_state_iv | iv_scaled | high | mae | 265 | 53 | 0.009641 | 0.009702 | 0.000061 | -0.000109 | 0.000231 | -0.000120 | 0.000242 |
| 5 | combined | shift_state_iv | iv_scaled | high | mae | 265 | 53 | 0.009701 | 0.009702 | 0.000001 | -0.000248 | 0.000250 | -0.000230 | 0.000232 |
| 5 | combined | random_state_iv | iv_scaled | low | crps | 265 | 53 | 0.007309 | 0.007327 | 0.000018 | -0.000130 | 0.000166 | -0.000142 | 0.000178 |
| 5 | combined | shift_state_iv | iv_scaled | low | crps | 265 | 53 | 0.007367 | 0.007327 | -0.000040 | -0.000256 | 0.000177 | -0.000251 | 0.000172 |
| 5 | combined | random_state_iv | iv_scaled | low | mae | 265 | 53 | 0.010301 | 0.010301 | 0.000001 | -0.000218 | 0.000219 | -0.000218 | 0.000219 |
| 5 | combined | shift_state_iv | iv_scaled | low | mae | 265 | 53 | 0.010367 | 0.010301 | -0.000066 | -0.000404 | 0.000272 | -0.000421 | 0.000290 |
| 5 | combined | random_state_iv | iv_scaled | max_daily | crps | 265 | 53 | 0.002986 | 0.002991 | 0.000006 | -0.000079 | 0.000091 | -0.000087 | 0.000098 |
| 5 | combined | shift_state_iv | iv_scaled | max_daily | crps | 265 | 53 | 0.003033 | 0.002991 | -0.000041 | -0.000189 | 0.000107 | -0.000189 | 0.000106 |
| 5 | combined | random_state_iv | iv_scaled | max_daily | mae | 265 | 53 | 0.004195 | 0.004196 | 0.000001 | -0.000090 | 0.000092 | -0.000099 | 0.000101 |
| 5 | combined | shift_state_iv | iv_scaled | max_daily | mae | 265 | 53 | 0.004278 | 0.004196 | -0.000082 | -0.000283 | 0.000120 | -0.000290 | 0.000127 |
| 5 | combined | random_state_iv | iv_scaled | overnight_sd | crps | 265 | 53 | 0.026084 | 0.026120 | 0.000035 | -0.000501 | 0.000571 | -0.000520 | 0.000590 |
| 5 | combined | shift_state_iv | iv_scaled | overnight_sd | crps | 265 | 53 | 0.026381 | 0.026120 | -0.000261 | -0.001146 | 0.000625 | -0.001153 | 0.000631 |
| 5 | combined | random_state_iv | iv_scaled | overnight_sd | mae | 265 | 53 | 0.033624 | 0.033709 | 0.000086 | -0.000766 | 0.000937 | -0.000878 | 0.001049 |
| 5 | combined | shift_state_iv | iv_scaled | overnight_sd | mae | 265 | 53 | 0.034224 | 0.033709 | -0.000515 | -0.002291 | 0.001261 | -0.002188 | 0.001159 |
| 5 | combined | shift_state_iv | iv_scaled | positive_days | crps | 265 | 53 | 0.633389 | 0.633540 | 0.000151 | -0.024043 | 0.024346 | -0.024515 | 0.024818 |
| 5 | combined | random_state_iv | iv_scaled | positive_days | crps | 265 | 53 | 0.634462 | 0.633540 | -0.000922 | -0.014342 | 0.012498 | -0.014166 | 0.012321 |
| 5 | combined | random_state_iv | iv_scaled | positive_days | mae | 265 | 53 | 0.958749 | 0.961874 | 0.003125 | -0.017980 | 0.024230 | -0.016280 | 0.022530 |
| 5 | combined | shift_state_iv | iv_scaled | positive_days | mae | 265 | 53 | 0.962043 | 0.961874 | -0.000170 | -0.029447 | 0.029108 | -0.028060 | 0.027721 |
| 5 | combined | random_state_iv | iv_scaled | range | crps | 265 | 53 | 0.005982 | 0.005961 | -0.000021 | -0.000139 | 0.000096 | -0.000126 | 0.000083 |
| 5 | combined | shift_state_iv | iv_scaled | range | crps | 265 | 53 | 0.006005 | 0.005961 | -0.000044 | -0.000233 | 0.000144 | -0.000217 | 0.000128 |
| 5 | combined | random_state_iv | iv_scaled | range | mae | 265 | 53 | 0.008220 | 0.008191 | -0.000029 | -0.000192 | 0.000134 | -0.000155 | 0.000097 |
| 5 | combined | shift_state_iv | iv_scaled | range | mae | 265 | 53 | 0.008305 | 0.008191 | -0.000114 | -0.000392 | 0.000163 | -0.000387 | 0.000159 |
| 5 | combined | random_state_iv | iv_scaled | rebound | crps | 265 | 53 | 0.005872 | 0.005925 | 0.000053 | -0.000039 | 0.000144 | -0.000038 | 0.000144 |
| 5 | combined | shift_state_iv | iv_scaled | rebound | crps | 265 | 53 | 0.005923 | 0.005925 | 0.000001 | -0.000188 | 0.000191 | -0.000191 | 0.000194 |
| 5 | combined | random_state_iv | iv_scaled | rebound | mae | 265 | 53 | 0.008084 | 0.008139 | 0.000055 | -0.000104 | 0.000214 | -0.000099 | 0.000209 |
| 5 | combined | shift_state_iv | iv_scaled | rebound | mae | 265 | 53 | 0.008207 | 0.008139 | -0.000068 | -0.000343 | 0.000206 | -0.000366 | 0.000229 |
| 5 | combined | shift_state_iv | iv_scaled | regular_sd | crps | 265 | 53 | 0.022307 | 0.022467 | 0.000160 | -0.000592 | 0.000912 | -0.000580 | 0.000900 |
| 5 | combined | random_state_iv | iv_scaled | regular_sd | crps | 265 | 53 | 0.022553 | 0.022467 | -0.000087 | -0.000509 | 0.000336 | -0.000495 | 0.000322 |
| 5 | combined | shift_state_iv | iv_scaled | regular_sd | mae | 265 | 53 | 0.031781 | 0.031999 | 0.000217 | -0.001033 | 0.001467 | -0.000995 | 0.001429 |
| 5 | combined | random_state_iv | iv_scaled | regular_sd | mae | 265 | 53 | 0.032061 | 0.031999 | -0.000062 | -0.000645 | 0.000521 | -0.000567 | 0.000443 |
| 5 | combined | random_state_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.147156 | 0.147679 | 0.000523 | -0.001589 | 0.002635 | -0.001918 | 0.002964 |
| 5 | combined | shift_state_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.147844 | 0.147679 | -0.000166 | -0.003065 | 0.002734 | -0.002578 | 0.002247 |
| 5 | combined | random_state_iv | iv_scaled | volatility | crps | 265 | 53 | 0.027427 | 0.027462 | 0.000035 | -0.000631 | 0.000701 | -0.000722 | 0.000792 |
| 5 | combined | shift_state_iv | iv_scaled | volatility | crps | 265 | 53 | 0.028071 | 0.027462 | -0.000609 | -0.002033 | 0.000814 | -0.002061 | 0.000843 |
| 5 | combined | random_state_iv | iv_scaled | volatility | mae | 265 | 53 | 0.038141 | 0.038225 | 0.000083 | -0.000823 | 0.000990 | -0.000976 | 0.001143 |
| 5 | combined | iv_rate_zero | iv_nearest | volatility | mae | 265 | 53 | 0.037776 | 0.037814 | 0.000039 | -0.000028 | 0.000106 | -0.000043 | 0.000120 |
| 5 | combined | iv_settlement | iv_nearest | volatility | mae | 265 | 53 | 0.037814 | 0.037814 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | combined | iv_smooth | iv_nearest | volatility | mae | 265 | 53 | 0.037814 | 0.037814 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | combined | iv_truncated | iv_nearest | volatility | mae | 265 | 53 | 0.037814 | 0.037814 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | combined | iv_liquid | iv_nearest | volatility | mae | 265 | 53 | 0.037815 | 0.037814 | -0.000000 | -0.000004 | 0.000003 | -0.000003 | 0.000002 |
| 5 | combined | iv_same_close | iv_nearest | volatility | mae | 265 | 53 | 0.037820 | 0.037814 | -0.000005 | -0.002616 | 0.002605 | -0.002627 | 0.002617 |
| 5 | combined | iv_future_forward | iv_nearest | volatility | mae | 265 | 53 | 0.037829 | 0.037814 | -0.000015 | -0.000115 | 0.000086 | -0.000121 | 0.000091 |
| 5 | combined | iv_rate_high | iv_nearest | volatility | mae | 265 | 53 | 0.037830 | 0.037814 | -0.000016 | -0.000050 | 0.000018 | -0.000057 | 0.000025 |
| 5 | combined | shift_state_iv | iv_scaled | volatility | mae | 265 | 53 | 0.039104 | 0.038225 | -0.000879 | -0.002916 | 0.001157 | -0.003108 | 0.001349 |
| 5 | combined | shape_shift21 | iv_nearest | volatility | mae | 265 | 53 | 0.038882 | 0.037814 | -0.001068 | -0.008776 | 0.006640 | -0.010436 | 0.008301 |
| 5 | combined | iv_lag2 | iv_nearest | volatility | mae | 265 | 53 | 0.039178 | 0.037814 | -0.001363 | -0.004614 | 0.001888 | -0.004899 | 0.002173 |
| 5 | combined | iv_longer | iv_nearest | volatility | mae | 265 | 53 | 0.039249 | 0.037814 | -0.001435 | -0.003656 | 0.000787 | -0.003515 | 0.000646 |
| 5 | combined | shape_block_permute | iv_nearest | volatility | mae | 265 | 53 | 0.040362 | 0.037814 | -0.002548 | -0.012814 | 0.007718 | -0.014427 | 0.009332 |
| 5 | combined | iv_lag5 | iv_nearest | volatility | mae | 265 | 53 | 0.042874 | 0.037814 | -0.005059 | -0.012385 | 0.002267 | -0.012869 | 0.002751 |
| 21 | combined | shift_state_iv | iv_scaled | abs_return | crps | 217 | 11 | 0.017264 | 0.017290 | 0.000026 | -0.000740 | 0.000792 | -0.000844 | 0.000897 |
| 21 | combined | random_state_iv | iv_scaled | abs_return | crps | 217 | 11 | 0.017351 | 0.017290 | -0.000061 | -0.000275 | 0.000153 | -0.000275 | 0.000153 |
| 21 | combined | shift_state_iv | iv_scaled | abs_return | mae | 217 | 11 | 0.022692 | 0.022767 | 0.000074 | -0.001213 | 0.001361 | -0.001438 | 0.001587 |
| 21 | combined | random_state_iv | iv_scaled | abs_return | mae | 217 | 11 | 0.022864 | 0.022767 | -0.000098 | -0.000385 | 0.000190 | -0.000366 | 0.000171 |
| 21 | combined | random_state_iv | iv_scaled | close_high | crps | 217 | 11 | 0.012706 | 0.012672 | -0.000034 | -0.000195 | 0.000128 | -0.000204 | 0.000136 |
| 21 | combined | shift_state_iv | iv_scaled | close_high | crps | 217 | 11 | 0.012888 | 0.012672 | -0.000216 | -0.000768 | 0.000336 | -0.000792 | 0.000360 |
| 21 | combined | random_state_iv | iv_scaled | close_high | mae | 217 | 11 | 0.017411 | 0.017413 | 0.000002 | -0.000258 | 0.000262 | -0.000239 | 0.000243 |
| 21 | combined | shift_state_iv | iv_scaled | close_high | mae | 217 | 11 | 0.017721 | 0.017413 | -0.000307 | -0.001136 | 0.000521 | -0.001208 | 0.000593 |
| 21 | combined | random_state_iv | iv_scaled | close_low | crps | 217 | 11 | 0.020071 | 0.020052 | -0.000019 | -0.000240 | 0.000202 | -0.000237 | 0.000199 |
| 21 | combined | shift_state_iv | iv_scaled | close_low | crps | 217 | 11 | 0.020146 | 0.020052 | -0.000094 | -0.001148 | 0.000959 | -0.001080 | 0.000891 |
| 21 | combined | shift_state_iv | iv_scaled | close_low | mae | 217 | 11 | 0.026284 | 0.026538 | 0.000255 | -0.001861 | 0.002370 | -0.002132 | 0.002641 |
| 21 | combined | random_state_iv | iv_scaled | close_low | mae | 217 | 11 | 0.026505 | 0.026538 | 0.000033 | -0.000384 | 0.000450 | -0.000286 | 0.000352 |
| 21 | combined | shift_state_iv | iv_scaled | drawdown | crps | 217 | 11 | 0.016691 | 0.016754 | 0.000063 | -0.001234 | 0.001360 | -0.001211 | 0.001337 |
| 21 | combined | random_state_iv | iv_scaled | drawdown | crps | 217 | 11 | 0.016797 | 0.016754 | -0.000043 | -0.000207 | 0.000121 | -0.000193 | 0.000107 |
| 21 | combined | shift_state_iv | iv_scaled | drawdown | mae | 217 | 11 | 0.022138 | 0.022961 | 0.000824 | -0.001834 | 0.003481 | -0.002283 | 0.003930 |
| 21 | combined | random_state_iv | iv_scaled | drawdown | mae | 217 | 11 | 0.023022 | 0.022961 | -0.000061 | -0.000505 | 0.000383 | -0.000450 | 0.000328 |
| 21 | combined | random_state_iv | iv_scaled | high | crps | 217 | 11 | 0.012417 | 0.012385 | -0.000032 | -0.000205 | 0.000140 | -0.000208 | 0.000144 |
| 21 | combined | shift_state_iv | iv_scaled | high | crps | 217 | 11 | 0.012648 | 0.012385 | -0.000263 | -0.000767 | 0.000241 | -0.000785 | 0.000260 |
| 21 | combined | random_state_iv | iv_scaled | high | mae | 217 | 11 | 0.017104 | 0.017124 | 0.000020 | -0.000220 | 0.000261 | -0.000195 | 0.000235 |
| 21 | combined | shift_state_iv | iv_scaled | high | mae | 217 | 11 | 0.017459 | 0.017124 | -0.000335 | -0.001045 | 0.000374 | -0.001111 | 0.000441 |
| 21 | combined | random_state_iv | iv_scaled | low | crps | 217 | 11 | 0.020440 | 0.020449 | 0.000009 | -0.000210 | 0.000227 | -0.000215 | 0.000232 |
| 21 | combined | shift_state_iv | iv_scaled | low | crps | 217 | 11 | 0.020486 | 0.020449 | -0.000037 | -0.001135 | 0.001061 | -0.001052 | 0.000978 |
| 21 | combined | shift_state_iv | iv_scaled | low | mae | 217 | 11 | 0.026816 | 0.027137 | 0.000321 | -0.001945 | 0.002588 | -0.002243 | 0.002885 |
| 21 | combined | random_state_iv | iv_scaled | low | mae | 217 | 11 | 0.027124 | 0.027137 | 0.000013 | -0.000416 | 0.000443 | -0.000324 | 0.000351 |
| 21 | combined | random_state_iv | iv_scaled | max_daily | crps | 217 | 11 | 0.004631 | 0.004633 | 0.000001 | -0.000072 | 0.000075 | -0.000081 | 0.000084 |
| 21 | combined | shift_state_iv | iv_scaled | max_daily | crps | 217 | 11 | 0.004905 | 0.004633 | -0.000273 | -0.001078 | 0.000533 | -0.001154 | 0.000609 |
| 21 | combined | random_state_iv | iv_scaled | max_daily | mae | 217 | 11 | 0.005492 | 0.005509 | 0.000017 | -0.000114 | 0.000148 | -0.000130 | 0.000164 |
| 21 | combined | shift_state_iv | iv_scaled | max_daily | mae | 217 | 11 | 0.005825 | 0.005509 | -0.000316 | -0.001234 | 0.000602 | -0.001351 | 0.000719 |
| 21 | combined | random_state_iv | iv_scaled | overnight_sd | crps | 217 | 11 | 0.034889 | 0.035018 | 0.000130 | -0.000380 | 0.000639 | -0.000464 | 0.000723 |
| 21 | combined | shift_state_iv | iv_scaled | overnight_sd | crps | 217 | 11 | 0.035694 | 0.035018 | -0.000676 | -0.003342 | 0.001991 | -0.003461 | 0.002110 |
| 21 | combined | random_state_iv | iv_scaled | overnight_sd | mae | 217 | 11 | 0.042007 | 0.042256 | 0.000249 | -0.000812 | 0.001310 | -0.000991 | 0.001489 |
| 21 | combined | shift_state_iv | iv_scaled | overnight_sd | mae | 217 | 11 | 0.043261 | 0.042256 | -0.001005 | -0.005067 | 0.003057 | -0.005593 | 0.003584 |
| 21 | combined | random_state_iv | iv_scaled | positive_days | crps | 217 | 11 | 1.359925 | 1.358696 | -0.001229 | -0.025303 | 0.022845 | -0.025343 | 0.022885 |
| 21 | combined | shift_state_iv | iv_scaled | positive_days | crps | 217 | 11 | 1.408140 | 1.358696 | -0.049444 | -0.119028 | 0.020140 | -0.118008 | 0.019120 |
| 21 | combined | random_state_iv | iv_scaled | positive_days | mae | 217 | 11 | 1.954502 | 1.952423 | -0.002079 | -0.028890 | 0.024732 | -0.026929 | 0.022770 |
| 21 | combined | shift_state_iv | iv_scaled | positive_days | mae | 217 | 11 | 2.012214 | 1.952423 | -0.059791 | -0.155962 | 0.036381 | -0.165714 | 0.046133 |
| 21 | combined | random_state_iv | iv_scaled | range | crps | 217 | 11 | 0.018107 | 0.018162 | 0.000055 | -0.000215 | 0.000326 | -0.000192 | 0.000303 |
| 21 | combined | shift_state_iv | iv_scaled | range | crps | 217 | 11 | 0.018257 | 0.018162 | -0.000095 | -0.001732 | 0.001542 | -0.001854 | 0.001664 |
| 21 | combined | random_state_iv | iv_scaled | range | mae | 217 | 11 | 0.024587 | 0.024620 | 0.000033 | -0.000456 | 0.000522 | -0.000443 | 0.000509 |
| 21 | combined | shift_state_iv | iv_scaled | range | mae | 217 | 11 | 0.024596 | 0.024620 | 0.000024 | -0.002642 | 0.002689 | -0.003060 | 0.003107 |
| 21 | combined | random_state_iv | iv_scaled | rebound | crps | 217 | 11 | 0.011969 | 0.012055 | 0.000086 | -0.000155 | 0.000327 | -0.000175 | 0.000347 |
| 21 | combined | shift_state_iv | iv_scaled | rebound | crps | 217 | 11 | 0.012857 | 0.012055 | -0.000802 | -0.002070 | 0.000466 | -0.002102 | 0.000498 |
| 21 | combined | random_state_iv | iv_scaled | rebound | mae | 217 | 11 | 0.016836 | 0.016983 | 0.000148 | -0.000196 | 0.000491 | -0.000235 | 0.000530 |
| 21 | combined | shift_state_iv | iv_scaled | rebound | mae | 217 | 11 | 0.017675 | 0.016983 | -0.000692 | -0.002252 | 0.000868 | -0.002273 | 0.000890 |
| 21 | combined | shift_state_iv | iv_scaled | regular_sd | crps | 217 | 11 | 0.023859 | 0.024651 | 0.000792 | -0.000711 | 0.002294 | -0.000789 | 0.002373 |
| 21 | combined | random_state_iv | iv_scaled | regular_sd | crps | 217 | 11 | 0.024708 | 0.024651 | -0.000057 | -0.000444 | 0.000330 | -0.000380 | 0.000266 |
| 21 | combined | shift_state_iv | iv_scaled | regular_sd | mae | 217 | 11 | 0.032780 | 0.034418 | 0.001638 | -0.001150 | 0.004426 | -0.001450 | 0.004726 |
| 21 | combined | random_state_iv | iv_scaled | regular_sd | mae | 217 | 11 | 0.034485 | 0.034418 | -0.000067 | -0.000624 | 0.000490 | -0.000541 | 0.000407 |
| 21 | combined | random_state_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.197389 | 0.197163 | -0.000226 | -0.002452 | 0.002000 | -0.002219 | 0.001767 |
| 21 | combined | shift_state_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.199980 | 0.197163 | -0.002817 | -0.010115 | 0.004481 | -0.009426 | 0.003792 |
| 21 | combined | random_state_iv | iv_scaled | volatility | crps | 217 | 11 | 0.030757 | 0.030795 | 0.000038 | -0.000386 | 0.000462 | -0.000408 | 0.000484 |
| 21 | combined | shift_state_iv | iv_scaled | volatility | crps | 217 | 11 | 0.031696 | 0.030795 | -0.000901 | -0.005413 | 0.003611 | -0.005600 | 0.003797 |
| 21 | combined | iv_same_close | iv_bracket | volatility | mae | 217 | 11 | 0.038369 | 0.039406 | 0.001037 | -0.001423 | 0.003497 | -0.001213 | 0.003287 |
| 21 | combined | iv_longer | iv_bracket | volatility | mae | 205 | 11 | 0.038470 | 0.039111 | 0.000642 | -0.002030 | 0.003313 | -0.002238 | 0.003522 |
| 21 | combined | shift_state_iv | iv_scaled | volatility | mae | 217 | 11 | 0.041291 | 0.041537 | 0.000246 | -0.004260 | 0.004752 | -0.004115 | 0.004608 |
| 21 | combined | random_state_iv | iv_scaled | volatility | mae | 217 | 11 | 0.041561 | 0.041537 | -0.000023 | -0.000850 | 0.000803 | -0.000835 | 0.000788 |
| 21 | combined | iv_rate_zero | iv_bracket | volatility | mae | 217 | 11 | 0.039527 | 0.039406 | -0.000121 | -0.001495 | 0.001254 | -0.001469 | 0.001228 |
| 21 | combined | iv_smooth | iv_bracket | volatility | mae | 217 | 11 | 0.039639 | 0.039406 | -0.000232 | -0.001882 | 0.001417 | -0.001940 | 0.001475 |
| 21 | combined | iv_truncated | iv_bracket | volatility | mae | 217 | 11 | 0.039639 | 0.039406 | -0.000232 | -0.001882 | 0.001417 | -0.001940 | 0.001475 |
| 21 | combined | iv_rate_high | iv_bracket | volatility | mae | 217 | 11 | 0.039677 | 0.039406 | -0.000271 | -0.002058 | 0.001516 | -0.002172 | 0.001630 |
| 21 | combined | iv_future_forward | iv_bracket | volatility | mae | 217 | 11 | 0.039687 | 0.039406 | -0.000280 | -0.002040 | 0.001479 | -0.002111 | 0.001550 |
| 21 | combined | iv_settlement | iv_bracket | volatility | mae | 217 | 11 | 0.039782 | 0.039406 | -0.000376 | -0.001972 | 0.001220 | -0.002095 | 0.001343 |
| 21 | combined | iv_liquid | iv_bracket | volatility | mae | 217 | 11 | 0.039939 | 0.039406 | -0.000532 | -0.002701 | 0.001637 | -0.002654 | 0.001589 |
| 21 | combined | iv_lag2 | iv_bracket | volatility | mae | 217 | 11 | 0.041223 | 0.039406 | -0.001816 | -0.004496 | 0.000863 | -0.004366 | 0.000733 |
| 21 | combined | shape_shift21 | iv_bracket | volatility | mae | 217 | 11 | 0.043658 | 0.039406 | -0.004252 | -0.014838 | 0.006335 | -0.017261 | 0.008757 |
| 21 | combined | iv_lag5 | iv_bracket | volatility | mae | 217 | 11 | 0.044884 | 0.039406 | -0.005477 | -0.012489 | 0.001534 | -0.011649 | 0.000694 |
| 21 | combined | shape_block_permute | iv_bracket | volatility | mae | 217 | 11 | 0.050366 | 0.039406 | -0.010959 | -0.027455 | 0.005537 | -0.029855 | 0.007936 |

[Initial specification](initial-registry.json) · [Null forecast artifacts](refit-null-origins.csv) · [Complete intervals](paired-search-adjusted.csv) · [Verification](verification.json).
