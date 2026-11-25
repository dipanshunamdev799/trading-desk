# V13 Global Volatility Transmission

The offshore set uses dated U.S. VIX, S&P 500, Nasdaq and Asian equity risk, USD/INR and Brent realized risk, U.S. rate changes and global dispersion and synchronization. The frozen global source clocks use earlier foreign dates and explicit availability estimates. The supplemental run fits an Indian gold ETF proxy and attempts official-series Nasdaq implied volatility. Joint offshore weighting competes with the simple domestic IV-scaled path.

| horizon | cohort | model | n | disjoint | mae | rmse | qlike | bias | spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | global_divergence | 265 | 53 | 0.039662 | 0.053761 | 0.417479 | -0.011701 | 0.555640 |
| 5 | early | global_divergence | 173 | 35 | 0.039126 | 0.054362 | 0.383383 | -0.010057 | 0.625580 |
| 5 | later | global_divergence | 92 | 19 | 0.040671 | 0.052613 | 0.481595 | -0.014792 | 0.370436 |
| 5 | combined | global_iv_plus_new_sources | 265 | 53 | 0.039063 | 0.053067 | 0.400730 | -0.012433 | 0.575643 |
| 5 | early | global_iv_plus_new_sources | 173 | 35 | 0.038187 | 0.053382 | 0.358644 | -0.010873 | 0.651028 |
| 5 | later | global_iv_plus_new_sources | 92 | 19 | 0.040710 | 0.052469 | 0.479869 | -0.015366 | 0.381255 |
| 5 | combined | global_only | 265 | 53 | 0.047284 | 0.066945 | 0.728439 | -0.019946 | 0.225713 |
| 5 | early | global_only | 173 | 35 | 0.048291 | 0.070982 | 0.800705 | -0.026253 | 0.332778 |
| 5 | later | global_only | 92 | 19 | 0.045389 | 0.058603 | 0.592548 | -0.008087 | -0.040180 |
| 5 | combined | global_plus_iv | 265 | 53 | 0.039031 | 0.052933 | 0.404126 | -0.012360 | 0.569511 |
| 5 | early | global_plus_iv | 173 | 35 | 0.038256 | 0.053340 | 0.368531 | -0.011080 | 0.642617 |
| 5 | later | global_plus_iv | 92 | 19 | 0.040488 | 0.052159 | 0.471058 | -0.014766 | 0.379067 |
| 5 | combined | gold_nasdaq_risk | 265 | 53 | 0.038161 | 0.051269 | 0.366952 | -0.010708 | 0.602668 |
| 5 | early | gold_nasdaq_risk | 173 | 35 | 0.037069 | 0.051039 | 0.319826 | -0.008340 | 0.676956 |
| 5 | later | gold_nasdaq_risk | 92 | 19 | 0.040213 | 0.051698 | 0.455570 | -0.015160 | 0.429527 |
| 5 | combined | iv_bracket | 265 | 53 | 0.038336 | 0.048394 | 0.277849 | 0.008045 | 0.609690 |
| 5 | early | iv_bracket | 173 | 35 | 0.037322 | 0.048537 | 0.243821 | 0.011690 | 0.679107 |
| 5 | later | iv_bracket | 92 | 19 | 0.040244 | 0.048125 | 0.341837 | 0.001192 | 0.473129 |
| 5 | combined | iv_nearest | 265 | 53 | 0.037814 | 0.048184 | 0.276187 | 0.007769 | 0.611711 |
| 5 | early | iv_nearest | 173 | 35 | 0.036518 | 0.047954 | 0.237563 | 0.011551 | 0.689298 |
| 5 | later | iv_nearest | 92 | 19 | 0.040253 | 0.048615 | 0.348818 | 0.000658 | 0.452183 |
| 5 | combined | prior_fitted_rv | 265 | 53 | 0.043246 | 0.060737 | 0.533594 | -0.022608 | 0.510969 |
| 5 | early | prior_fitted_rv | 173 | 35 | 0.043453 | 0.063684 | 0.537572 | -0.025106 | 0.591846 |
| 5 | later | prior_fitted_rv | 92 | 19 | 0.042855 | 0.054768 | 0.526114 | -0.017911 | 0.353976 |
| 21 | combined | global_divergence | 217 | 11 | 0.048101 | 0.064427 | 0.668963 | -0.020899 | 0.191627 |
| 21 | early | global_divergence | 141 | 7 | 0.057484 | 0.075654 | 0.918326 | -0.028733 | 0.209097 |
| 21 | later | global_divergence | 76 | 4 | 0.030694 | 0.035117 | 0.206328 | -0.006366 | 0.337143 |
| 21 | combined | global_iv_plus_new_sources | 217 | 11 | 0.045654 | 0.062505 | 0.637916 | -0.022580 | 0.229698 |
| 21 | early | global_iv_plus_new_sources | 141 | 7 | 0.054406 | 0.073425 | 0.876229 | -0.030609 | 0.227005 |
| 21 | later | global_iv_plus_new_sources | 76 | 4 | 0.029416 | 0.033954 | 0.195783 | -0.007685 | 0.445714 |
| 21 | combined | global_only | 217 | 11 | 0.050488 | 0.070839 | 0.941663 | -0.029546 | -0.373173 |
| 21 | early | global_only | 141 | 7 | 0.056579 | 0.081371 | 1.289936 | -0.049098 | -0.261000 |
| 21 | later | global_only | 76 | 4 | 0.039187 | 0.045212 | 0.295525 | 0.006728 | -0.505947 |
| 21 | combined | global_plus_iv | 217 | 11 | 0.046865 | 0.063271 | 0.648954 | -0.021434 | 0.203726 |
| 21 | early | global_plus_iv | 141 | 7 | 0.056018 | 0.074393 | 0.893551 | -0.029919 | 0.213220 |
| 21 | later | global_plus_iv | 76 | 4 | 0.029882 | 0.034096 | 0.195161 | -0.005693 | 0.363281 |
| 21 | combined | gold_nasdaq_risk | 217 | 11 | 0.045703 | 0.061488 | 0.576043 | -0.018855 | 0.248411 |
| 21 | early | gold_nasdaq_risk | 141 | 7 | 0.054101 | 0.072113 | 0.781564 | -0.025485 | 0.242134 |
| 21 | later | gold_nasdaq_risk | 76 | 4 | 0.030124 | 0.033873 | 0.194747 | -0.006555 | 0.395407 |
| 21 | combined | iv_bracket | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | early | iv_bracket | 141 | 7 | 0.043885 | 0.055899 | 0.309888 | -0.006590 | 0.408297 |
| 21 | later | iv_bracket | 76 | 4 | 0.031097 | 0.034276 | 0.189211 | -0.000350 | 0.318961 |
| 21 | combined | iv_nearest | 217 | 11 | 0.039639 | 0.049835 | 0.266465 | -0.003579 | 0.448765 |
| 21 | early | iv_nearest | 141 | 7 | 0.044220 | 0.056459 | 0.307816 | -0.005269 | 0.415553 |
| 21 | later | iv_nearest | 76 | 4 | 0.031140 | 0.034310 | 0.189748 | -0.000445 | 0.316446 |
| 21 | combined | prior_fitted_rv | 217 | 11 | 0.040910 | 0.058706 | 0.504587 | -0.029663 | 0.263429 |
| 21 | early | prior_fitted_rv | 141 | 7 | 0.045488 | 0.067546 | 0.648227 | -0.040220 | 0.281429 |
| 21 | later | prior_fitted_rv | 76 | 4 | 0.032416 | 0.037090 | 0.238097 | -0.010077 | 0.142584 |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | global_iv | iv_scaled | abs_return | crps | 265 | 53 | 0.006541 | 0.006563 | 0.000023 | -0.000097 | 0.000142 | -0.000104 | 0.000149 |
| 5 | combined | global_iv | iv_scaled | abs_return | mae | 265 | 53 | 0.009395 | 0.009464 | 0.000069 | -0.000086 | 0.000223 | -0.000087 | 0.000224 |
| 5 | combined | global_iv | iv_scaled | close_high | crps | 265 | 53 | 0.007638 | 0.007645 | 0.000007 | -0.000089 | 0.000103 | -0.000093 | 0.000108 |
| 5 | combined | global_iv | iv_scaled | close_high | mae | 265 | 53 | 0.010183 | 0.010197 | 0.000014 | -0.000139 | 0.000168 | -0.000147 | 0.000176 |
| 5 | combined | global_iv | iv_scaled | close_low | crps | 265 | 53 | 0.007600 | 0.007607 | 0.000007 | -0.000167 | 0.000180 | -0.000198 | 0.000211 |
| 5 | combined | global_iv | iv_scaled | close_low | mae | 265 | 53 | 0.010737 | 0.010721 | -0.000016 | -0.000266 | 0.000235 | -0.000311 | 0.000280 |
| 5 | combined | global_iv | iv_scaled | drawdown | crps | 265 | 53 | 0.006158 | 0.006170 | 0.000011 | -0.000152 | 0.000175 | -0.000198 | 0.000221 |
| 5 | combined | global_iv | iv_scaled | drawdown | mae | 265 | 53 | 0.008882 | 0.008891 | 0.000009 | -0.000197 | 0.000216 | -0.000229 | 0.000248 |
| 5 | combined | global_iv | iv_scaled | high | crps | 265 | 53 | 0.007115 | 0.007131 | 0.000015 | -0.000083 | 0.000114 | -0.000084 | 0.000115 |
| 5 | combined | global_iv | iv_scaled | high | mae | 265 | 53 | 0.009640 | 0.009702 | 0.000062 | -0.000103 | 0.000227 | -0.000114 | 0.000239 |
| 5 | combined | global_iv | iv_scaled | low | crps | 265 | 53 | 0.007308 | 0.007327 | 0.000019 | -0.000138 | 0.000177 | -0.000145 | 0.000183 |
| 5 | combined | global_iv | iv_scaled | low | mae | 265 | 53 | 0.010347 | 0.010301 | -0.000046 | -0.000307 | 0.000215 | -0.000337 | 0.000245 |
| 5 | combined | global_iv | iv_scaled | max_daily | crps | 265 | 53 | 0.003002 | 0.002991 | -0.000010 | -0.000119 | 0.000098 | -0.000107 | 0.000087 |
| 5 | combined | global_iv | iv_scaled | max_daily | mae | 265 | 53 | 0.004255 | 0.004196 | -0.000059 | -0.000174 | 0.000057 | -0.000158 | 0.000040 |
| 5 | combined | global_iv | iv_scaled | overnight_sd | crps | 265 | 53 | 0.026107 | 0.026120 | 0.000013 | -0.001057 | 0.001083 | -0.000964 | 0.000989 |
| 5 | combined | global_iv | iv_scaled | overnight_sd | mae | 265 | 53 | 0.033776 | 0.033709 | -0.000067 | -0.001496 | 0.001363 | -0.001318 | 0.001184 |
| 5 | combined | global_iv | iv_scaled | positive_days | crps | 265 | 53 | 0.632969 | 0.633540 | 0.000571 | -0.014279 | 0.015420 | -0.016802 | 0.017943 |
| 5 | combined | global_iv | iv_scaled | positive_days | mae | 265 | 53 | 0.961387 | 0.961874 | 0.000486 | -0.021540 | 0.022513 | -0.024898 | 0.025871 |
| 5 | combined | global_iv | iv_scaled | range | crps | 265 | 53 | 0.005970 | 0.005961 | -0.000009 | -0.000148 | 0.000131 | -0.000138 | 0.000121 |
| 5 | combined | global_iv | iv_scaled | range | mae | 265 | 53 | 0.008262 | 0.008191 | -0.000071 | -0.000262 | 0.000120 | -0.000264 | 0.000122 |
| 5 | combined | global_iv | iv_scaled | rebound | crps | 265 | 53 | 0.005906 | 0.005925 | 0.000018 | -0.000075 | 0.000112 | -0.000078 | 0.000115 |
| 5 | combined | global_iv | iv_scaled | rebound | mae | 265 | 53 | 0.008087 | 0.008139 | 0.000052 | -0.000090 | 0.000194 | -0.000093 | 0.000197 |
| 5 | combined | global_iv | iv_scaled | regular_sd | crps | 265 | 53 | 0.022187 | 0.022467 | 0.000280 | -0.000247 | 0.000807 | -0.000229 | 0.000789 |
| 5 | combined | global_iv | iv_scaled | regular_sd | mae | 265 | 53 | 0.031862 | 0.031999 | 0.000137 | -0.000545 | 0.000818 | -0.000391 | 0.000664 |
| 5 | combined | global_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.147467 | 0.147679 | 0.000211 | -0.001975 | 0.002398 | -0.001855 | 0.002277 |
| 5 | combined | global_iv | iv_scaled | volatility | crps | 265 | 53 | 0.027484 | 0.027462 | -0.000022 | -0.000731 | 0.000687 | -0.000661 | 0.000617 |
| 5 | combined | gold_nasdaq_risk | har_iv | volatility | mae | 265 | 53 | 0.038161 | 0.039714 | 0.001553 | -0.002570 | 0.005677 | -0.003421 | 0.006527 |
| 5 | combined | global_plus_iv | har_iv | volatility | mae | 265 | 53 | 0.039031 | 0.039714 | 0.000683 | -0.003409 | 0.004775 | -0.004054 | 0.005421 |
| 5 | combined | global_iv_plus_new_sources | har_iv | volatility | mae | 265 | 53 | 0.039063 | 0.039714 | 0.000651 | -0.003778 | 0.005079 | -0.004451 | 0.005753 |
| 5 | combined | global_iv | iv_scaled | volatility | mae | 265 | 53 | 0.038460 | 0.038225 | -0.000235 | -0.001199 | 0.000728 | -0.001188 | 0.000717 |
| 5 | combined | gold_nasdaq_risk | iv_nearest | volatility | mae | 265 | 53 | 0.038161 | 0.037814 | -0.000346 | -0.008790 | 0.008098 | -0.010932 | 0.010240 |
| 5 | combined | global_plus_iv | iv_nearest | volatility | mae | 265 | 53 | 0.039031 | 0.037814 | -0.001216 | -0.010288 | 0.007856 | -0.012772 | 0.010340 |
| 5 | combined | global_iv_plus_new_sources | iv_nearest | volatility | mae | 265 | 53 | 0.039063 | 0.037814 | -0.001249 | -0.010480 | 0.007983 | -0.012903 | 0.010406 |
| 5 | combined | global_divergence | iv_nearest | volatility | mae | 265 | 53 | 0.039662 | 0.037814 | -0.001848 | -0.011044 | 0.007348 | -0.013595 | 0.009899 |
| 5 | combined | global_only | har_iv | volatility | mae | 265 | 53 | 0.047284 | 0.039714 | -0.007570 | -0.022566 | 0.007426 | -0.025115 | 0.009975 |
| 5 | combined | global_only | iv_nearest | volatility | mae | 265 | 53 | 0.047284 | 0.037814 | -0.009469 | -0.029096 | 0.010158 | -0.034484 | 0.015545 |
| 5 | combined | gold_nasdaq_risk | har_iv | volatility | qlike | 265 | 53 | 0.366952 | 0.367964 | 0.001012 | -0.070574 | 0.072598 | -0.080120 | 0.082144 |
| 5 | combined | global_iv_plus_new_sources | har_iv | volatility | qlike | 265 | 53 | 0.400730 | 0.367964 | -0.032766 | -0.108064 | 0.042533 | -0.114172 | 0.048641 |
| 5 | combined | global_plus_iv | har_iv | volatility | qlike | 265 | 53 | 0.404126 | 0.367964 | -0.036162 | -0.095482 | 0.023158 | -0.099448 | 0.027125 |
| 5 | combined | gold_nasdaq_risk | iv_nearest | volatility | qlike | 265 | 53 | 0.366952 | 0.276187 | -0.090765 | -0.237132 | 0.055602 | -0.268810 | 0.087281 |
| 5 | combined | global_iv_plus_new_sources | iv_nearest | volatility | qlike | 265 | 53 | 0.400730 | 0.276187 | -0.124543 | -0.295859 | 0.046774 | -0.339067 | 0.089982 |
| 5 | combined | global_plus_iv | iv_nearest | volatility | qlike | 265 | 53 | 0.404126 | 0.276187 | -0.127939 | -0.303688 | 0.047810 | -0.352912 | 0.097035 |
| 5 | combined | global_divergence | iv_nearest | volatility | qlike | 265 | 53 | 0.417479 | 0.276187 | -0.141292 | -0.327885 | 0.045301 | -0.380908 | 0.098324 |
| 5 | combined | global_only | har_iv | volatility | qlike | 265 | 53 | 0.728439 | 0.367964 | -0.360475 | -0.887934 | 0.166984 | -0.974887 | 0.253937 |
| 5 | combined | global_only | iv_nearest | volatility | qlike | 265 | 53 | 0.728439 | 0.276187 | -0.452252 | -1.051398 | 0.146894 | -1.195539 | 0.291035 |
| 21 | combined | global_iv | iv_scaled | abs_return | crps | 217 | 11 | 0.017274 | 0.017290 | 0.000017 | -0.000324 | 0.000358 | -0.000331 | 0.000365 |
| 21 | combined | global_iv | iv_scaled | abs_return | mae | 217 | 11 | 0.022770 | 0.022767 | -0.000003 | -0.000449 | 0.000443 | -0.000335 | 0.000329 |
| 21 | combined | global_iv | iv_scaled | close_high | crps | 217 | 11 | 0.012727 | 0.012672 | -0.000054 | -0.000292 | 0.000184 | -0.000280 | 0.000171 |
| 21 | combined | global_iv | iv_scaled | close_high | mae | 217 | 11 | 0.017396 | 0.017413 | 0.000017 | -0.000387 | 0.000421 | -0.000392 | 0.000426 |
| 21 | combined | global_iv | iv_scaled | close_low | crps | 217 | 11 | 0.019829 | 0.020052 | 0.000223 | -0.000227 | 0.000673 | -0.000282 | 0.000728 |
| 21 | combined | global_iv | iv_scaled | close_low | mae | 217 | 11 | 0.026393 | 0.026538 | 0.000145 | -0.000454 | 0.000745 | -0.000477 | 0.000768 |
| 21 | combined | global_iv | iv_scaled | drawdown | crps | 217 | 11 | 0.016571 | 0.016754 | 0.000183 | -0.000201 | 0.000566 | -0.000277 | 0.000642 |
| 21 | combined | global_iv | iv_scaled | drawdown | mae | 217 | 11 | 0.022804 | 0.022961 | 0.000157 | -0.000338 | 0.000652 | -0.000336 | 0.000650 |
| 21 | combined | global_iv | iv_scaled | high | crps | 217 | 11 | 0.012442 | 0.012385 | -0.000057 | -0.000306 | 0.000191 | -0.000286 | 0.000171 |
| 21 | combined | global_iv | iv_scaled | high | mae | 217 | 11 | 0.017119 | 0.017124 | 0.000005 | -0.000395 | 0.000404 | -0.000391 | 0.000400 |
| 21 | combined | global_iv | iv_scaled | low | crps | 217 | 11 | 0.020193 | 0.020449 | 0.000256 | -0.000224 | 0.000735 | -0.000309 | 0.000820 |
| 21 | combined | global_iv | iv_scaled | low | mae | 217 | 11 | 0.026996 | 0.027137 | 0.000142 | -0.000494 | 0.000778 | -0.000554 | 0.000837 |
| 21 | combined | global_iv | iv_scaled | max_daily | crps | 217 | 11 | 0.004879 | 0.004633 | -0.000246 | -0.000518 | 0.000026 | -0.000597 | 0.000105 |
| 21 | combined | global_iv | iv_scaled | max_daily | mae | 217 | 11 | 0.005697 | 0.005509 | -0.000188 | -0.000517 | 0.000141 | -0.000599 | 0.000223 |
| 21 | combined | global_iv | iv_scaled | overnight_sd | crps | 217 | 11 | 0.035463 | 0.035018 | -0.000444 | -0.001218 | 0.000329 | -0.001330 | 0.000442 |
| 21 | combined | global_iv | iv_scaled | overnight_sd | mae | 217 | 11 | 0.042169 | 0.042256 | 0.000087 | -0.001002 | 0.001175 | -0.001120 | 0.001294 |
| 21 | combined | global_iv | iv_scaled | positive_days | crps | 217 | 11 | 1.366947 | 1.358696 | -0.008251 | -0.047320 | 0.030819 | -0.052211 | 0.035709 |
| 21 | combined | global_iv | iv_scaled | positive_days | mae | 217 | 11 | 1.958894 | 1.952423 | -0.006471 | -0.060816 | 0.047873 | -0.069486 | 0.056543 |
| 21 | combined | global_iv | iv_scaled | range | crps | 217 | 11 | 0.018060 | 0.018162 | 0.000102 | -0.000254 | 0.000459 | -0.000270 | 0.000475 |
| 21 | combined | global_iv | iv_scaled | range | mae | 217 | 11 | 0.024601 | 0.024620 | 0.000019 | -0.000513 | 0.000551 | -0.000546 | 0.000584 |
| 21 | combined | global_iv | iv_scaled | rebound | crps | 217 | 11 | 0.012051 | 0.012055 | 0.000004 | -0.000367 | 0.000375 | -0.000328 | 0.000336 |
| 21 | combined | global_iv | iv_scaled | rebound | mae | 217 | 11 | 0.016901 | 0.016983 | 0.000082 | -0.000429 | 0.000594 | -0.000386 | 0.000550 |
| 21 | combined | global_iv | iv_scaled | regular_sd | crps | 217 | 11 | 0.024651 | 0.024651 | 0.000000 | -0.000609 | 0.000610 | -0.000693 | 0.000694 |
| 21 | combined | global_iv | iv_scaled | regular_sd | mae | 217 | 11 | 0.034232 | 0.034418 | 0.000186 | -0.000542 | 0.000914 | -0.000607 | 0.000979 |
| 21 | combined | global_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.195179 | 0.197163 | 0.001984 | -0.002200 | 0.006169 | -0.002550 | 0.006519 |
| 21 | combined | global_iv | iv_scaled | volatility | crps | 217 | 11 | 0.031589 | 0.030795 | -0.000795 | -0.001765 | 0.000176 | -0.002019 | 0.000429 |
| 21 | combined | global_iv_plus_new_sources | har_iv | volatility | mae | 217 | 11 | 0.045654 | 0.051513 | 0.005859 | -0.012310 | 0.024028 | -0.016104 | 0.027822 |
| 21 | combined | gold_nasdaq_risk | har_iv | volatility | mae | 217 | 11 | 0.045703 | 0.051513 | 0.005809 | -0.009825 | 0.021444 | -0.013383 | 0.025002 |
| 21 | combined | global_plus_iv | har_iv | volatility | mae | 217 | 11 | 0.046865 | 0.051513 | 0.004648 | -0.012799 | 0.022095 | -0.015657 | 0.024953 |
| 21 | combined | global_only | har_iv | volatility | mae | 217 | 11 | 0.050488 | 0.051513 | 0.001025 | -0.024453 | 0.026502 | -0.029142 | 0.031191 |
| 21 | combined | global_iv | iv_scaled | volatility | mae | 217 | 11 | 0.041914 | 0.041537 | -0.000377 | -0.001601 | 0.000847 | -0.001822 | 0.001069 |
| 21 | combined | global_iv_plus_new_sources | iv_bracket | volatility | mae | 217 | 11 | 0.045654 | 0.039406 | -0.006248 | -0.021308 | 0.008812 | -0.024246 | 0.011751 |
| 21 | combined | gold_nasdaq_risk | iv_bracket | volatility | mae | 217 | 11 | 0.045703 | 0.039406 | -0.006297 | -0.019284 | 0.006690 | -0.022086 | 0.009492 |
| 21 | combined | global_plus_iv | iv_bracket | volatility | mae | 217 | 11 | 0.046865 | 0.039406 | -0.007458 | -0.022320 | 0.007403 | -0.024823 | 0.009907 |
| 21 | combined | global_divergence | iv_bracket | volatility | mae | 217 | 11 | 0.048101 | 0.039406 | -0.008695 | -0.023860 | 0.006471 | -0.026297 | 0.008908 |
| 21 | combined | global_only | iv_bracket | volatility | mae | 217 | 11 | 0.050488 | 0.039406 | -0.011082 | -0.033236 | 0.011073 | -0.039043 | 0.016879 |
| 21 | combined | gold_nasdaq_risk | har_iv | volatility | qlike | 217 | 11 | 0.576043 | 0.577685 | 0.001643 | -0.123813 | 0.127098 | -0.132577 | 0.135862 |
| 21 | combined | global_iv_plus_new_sources | har_iv | volatility | qlike | 217 | 11 | 0.637916 | 0.577685 | -0.060231 | -0.259339 | 0.138878 | -0.285551 | 0.165090 |
| 21 | combined | global_plus_iv | har_iv | volatility | qlike | 217 | 11 | 0.648954 | 0.577685 | -0.071268 | -0.262934 | 0.120397 | -0.293467 | 0.150930 |
| 21 | combined | gold_nasdaq_risk | iv_bracket | volatility | qlike | 217 | 11 | 0.576043 | 0.267623 | -0.308420 | -0.796947 | 0.180108 | -0.941880 | 0.325040 |
| 21 | combined | global_only | har_iv | volatility | qlike | 217 | 11 | 0.941663 | 0.577685 | -0.363978 | -1.170817 | 0.442861 | -1.279235 | 0.551279 |
| 21 | combined | global_iv_plus_new_sources | iv_bracket | volatility | qlike | 217 | 11 | 0.637916 | 0.267623 | -0.370293 | -0.945067 | 0.204481 | -1.123315 | 0.382729 |
| 21 | combined | global_plus_iv | iv_bracket | volatility | qlike | 217 | 11 | 0.648954 | 0.267623 | -0.381331 | -0.965188 | 0.202527 | -1.148592 | 0.385931 |
| 21 | combined | global_divergence | iv_bracket | volatility | qlike | 217 | 11 | 0.668963 | 0.267623 | -0.401340 | -0.998844 | 0.196165 | -1.186370 | 0.383691 |
| 21 | combined | global_only | iv_bracket | volatility | qlike | 217 | 11 | 0.941663 | 0.267623 | -0.674040 | -1.733297 | 0.385217 | -2.014280 | 0.666199 |

[Foreign clock](foreign-risk-clock.csv) · [Supplemental receipts](supplemental-sources.json) · [FRED VIX](https://fred.stlouisfed.org/series/VIXCLS) · [FRED Nasdaq volatility](https://fred.stlouisfed.org/series/VXNCLS).
