# V16 Multiscale directional forecasting

At the fixed 08:55 cutoff before the first opening auction, the decomposition estimates the first gap, the first regular-session return and the remaining four or twenty sessions from separate matured labels. Sampled historical joint residuals preserve correlation across components. The GIFT variant forecasts the first gap from the eligible futures mark and estimates residual gap width on earlier paired cases. Its coverage diagnostic compares originals with an eligible quote and excludes fallback dates on both sides. Subsequent gaps, sessions, financial leadership and global risk states are drawn from already resolved coherent historical blocks rather than future observations. The state layer updates variance with the initial IV/GJR state and simulated innovations. For the multitask branch, gap, regular return, 1-, 3-, 5- and 21-session endpoints and a volatility ratio share a rank-two map reconstructed from labeled samples that all completed before the decision. The fixed mixture selects complete simulated paths from the historical IV, direct domestic and decomposed-GIFT laws.

## Common original endpoints

| horizon | model | n | brier | log loss | endpoint crps | endpoint coverage80 | endpoint width80 | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.228529 | 0.648943 | 0.010457 | 0.826415 | 0.045780 | 0.636001 |
| 5 | V15_gjr_restart | 265 | 0.250763 | 0.694695 | 0.010922 | 0.773585 | 0.041706 | 0.573516 |
| 5 | decomposed | 265 | 0.246549 | 0.686758 | 0.010870 | 0.784906 | 0.042800 | 0.569300 |
| 5 | decomposed_gift | 265 | 0.242618 | 0.681034 | 0.010493 | 0.750943 | 0.041429 | 0.608166 |
| 5 | direct_domestic | 265 | 0.243813 | 0.681519 | 0.010799 | 0.773585 | 0.042836 | 0.607964 |
| 5 | direct_global | 265 | 0.245662 | 0.685002 | 0.010854 | 0.781132 | 0.042843 | 0.595345 |
| 5 | fixed_mixture | 265 | 0.241548 | 0.676422 | 0.010570 | 0.777358 | 0.043204 | 0.593353 |
| 5 | historical_iv | 265 | 0.256325 | 0.706286 | 0.011043 | 0.766038 | 0.042832 | 0.511175 |
| 5 | matured_historical | 265 | 0.254407 | 0.702309 | 0.011233 | 0.743396 | 0.039788 | 0.485245 |
| 5 | multitask | 265 | 0.256368 | 0.706912 | 0.011485 | 0.743396 | 0.042769 | 0.497748 |
| 5 | neutral | 265 | 0.250000 | 0.693147 | 0.011055 | 0.758491 | 0.042434 | 0.500000 |
| 5 | session_state | 265 | 0.239546 | 0.673356 | 0.010466 | 0.777358 | 0.041712 | 0.598724 |
| 21 | V14_domestic_GJR | 217 | 0.245042 | 0.683095 | 0.024989 | 0.668203 | 0.071794 | 0.502675 |
| 21 | V15_gjr_restart | 217 | 0.251376 | 0.695900 | 0.024694 | 0.705069 | 0.083033 | 0.524072 |
| 21 | decomposed | 217 | 0.269590 | 0.737147 | 0.026979 | 0.658986 | 0.092117 | 0.480500 |
| 21 | decomposed_gift | 217 | 0.273803 | 0.760809 | 0.027288 | 0.654378 | 0.091569 | 0.501553 |
| 21 | direct_domestic | 217 | 0.283087 | 0.779673 | 0.027741 | 0.668203 | 0.091922 | 0.482830 |
| 21 | direct_global | 217 | 0.282919 | 0.779274 | 0.027832 | 0.663594 | 0.091949 | 0.481665 |
| 21 | fixed_mixture | 217 | 0.270677 | 0.739064 | 0.026890 | 0.672811 | 0.094070 | 0.483995 |
| 21 | historical_iv | 217 | 0.293496 | 0.790282 | 0.027152 | 0.695853 | 0.093143 | 0.490811 |
| 21 | matured_historical | 217 | 0.294673 | 0.792754 | 0.027117 | 0.686636 | 0.081566 | 0.499612 |
| 21 | multitask | 217 | 0.296143 | 0.800896 | 0.027882 | 0.640553 | 0.092000 | 0.417903 |
| 21 | neutral | 217 | 0.250000 | 0.693147 | 0.025435 | 0.682028 | 0.075143 | 0.500000 |
| 21 | session_state | 217 | 0.270103 | 0.749273 | 0.027116 | 0.654378 | 0.087465 | 0.507420 |

## Matched gains and uncertainty

| horizon | candidate | control | metric | n | gain | early gain | later gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | decomposed | V14_sign_shrinkage | brier | 265 | -0.018020 | -0.013700 | -0.026143 | -0.042333 | 0.006294 |
| 5 | decomposed | V14_sign_shrinkage | endpoint_crps | 265 | -0.000413 | -0.000358 | -0.000516 | -0.001375 | 0.000549 |
| 5 | decomposed | V15_gjr_restart | brier | 265 | 0.004214 | -0.002400 | 0.016652 | -0.020276 | 0.028705 |
| 5 | decomposed | V15_gjr_restart | endpoint_crps | 265 | 0.000052 | -0.000389 | 0.000880 | -0.001027 | 0.001130 |
| 5 | decomposed | historical_iv | brier | 265 | 0.009776 | -0.001584 | 0.031138 | -0.018714 | 0.038266 |
| 5 | decomposed | historical_iv | endpoint_crps | 265 | 0.000173 | -0.000286 | 0.001035 | -0.000909 | 0.001255 |
| 5 | decomposed_gift | V14_sign_shrinkage | brier | 265 | -0.014090 | -0.010418 | -0.020994 | -0.043483 | 0.015304 |
| 5 | decomposed_gift | V14_sign_shrinkage | endpoint_crps | 265 | -0.000036 | 0.000146 | -0.000379 | -0.001138 | 0.001065 |
| 5 | decomposed_gift | V15_gjr_restart | brier | 265 | 0.008144 | 0.000882 | 0.021800 | -0.024723 | 0.041012 |
| 5 | decomposed_gift | V15_gjr_restart | endpoint_crps | 265 | 0.000429 | 0.000115 | 0.001017 | -0.000768 | 0.001625 |
| 5 | decomposed_gift | historical_iv | brier | 265 | 0.013706 | 0.001698 | 0.036286 | -0.023313 | 0.050725 |
| 5 | decomposed_gift | historical_iv | endpoint_crps | 265 | 0.000550 | 0.000219 | 0.001173 | -0.000584 | 0.001684 |
| 5 | session_state | V14_sign_shrinkage | brier | 265 | -0.011018 | -0.007049 | -0.018481 | -0.038117 | 0.016082 |
| 5 | session_state | V14_sign_shrinkage | endpoint_crps | 265 | -0.000009 | 0.000215 | -0.000429 | -0.001101 | 0.001083 |
| 5 | session_state | V15_gjr_restart | brier | 265 | 0.011216 | 0.004251 | 0.024314 | -0.019816 | 0.042249 |
| 5 | session_state | V15_gjr_restart | endpoint_crps | 265 | 0.000456 | 0.000184 | 0.000967 | -0.000564 | 0.001476 |
| 5 | session_state | historical_iv | brier | 265 | 0.016778 | 0.005067 | 0.038800 | -0.016890 | 0.050446 |
| 5 | session_state | historical_iv | endpoint_crps | 265 | 0.000577 | 0.000287 | 0.001122 | -0.000386 | 0.001540 |
| 5 | multitask | V14_sign_shrinkage | brier | 265 | -0.027839 | -0.018498 | -0.045406 | -0.063263 | 0.007584 |
| 5 | multitask | V14_sign_shrinkage | endpoint_crps | 265 | -0.001028 | -0.000840 | -0.001382 | -0.002555 | 0.000498 |
| 5 | multitask | V15_gjr_restart | brier | 265 | -0.005605 | -0.007198 | -0.002611 | -0.038393 | 0.027183 |
| 5 | multitask | V15_gjr_restart | endpoint_crps | 265 | -0.000564 | -0.000871 | 0.000014 | -0.001664 | 0.000536 |
| 5 | multitask | historical_iv | brier | 265 | -0.000044 | -0.006382 | 0.011875 | -0.025172 | 0.025085 |
| 5 | multitask | historical_iv | endpoint_crps | 265 | -0.000442 | -0.000768 | 0.000170 | -0.001454 | 0.000569 |
| 5 | fixed_mixture | V14_sign_shrinkage | brier | 265 | -0.013019 | -0.005736 | -0.026714 | -0.035402 | 0.009364 |
| 5 | fixed_mixture | V14_sign_shrinkage | endpoint_crps | 265 | -0.000113 | 0.000126 | -0.000563 | -0.001177 | 0.000951 |
| 5 | fixed_mixture | V15_gjr_restart | brier | 265 | 0.009215 | 0.005564 | 0.016081 | -0.011454 | 0.029884 |
| 5 | fixed_mixture | V15_gjr_restart | endpoint_crps | 265 | 0.000352 | 0.000096 | 0.000834 | -0.000517 | 0.001221 |
| 5 | fixed_mixture | historical_iv | brier | 265 | 0.014777 | 0.006380 | 0.030567 | -0.010172 | 0.039726 |
| 5 | fixed_mixture | historical_iv | endpoint_crps | 265 | 0.000473 | 0.000199 | 0.000989 | -0.000373 | 0.001319 |
| 21 | decomposed | V14_domestic_GJR | brier | 217 | -0.024548 | -0.047788 | 0.018569 | -0.106725 | 0.057630 |
| 21 | decomposed | V14_domestic_GJR | endpoint_crps | 217 | -0.001990 | -0.003331 | 0.000497 | -0.006928 | 0.002948 |
| 21 | decomposed | V15_gjr_restart | brier | 217 | -0.018213 | -0.038978 | 0.020311 | -0.123505 | 0.087079 |
| 21 | decomposed | V15_gjr_restart | endpoint_crps | 217 | -0.002285 | -0.003405 | -0.000206 | -0.008262 | 0.003693 |
| 21 | decomposed | historical_iv | brier | 217 | 0.023906 | 0.027176 | 0.017841 | -0.089735 | 0.137548 |
| 21 | decomposed | historical_iv | endpoint_crps | 217 | 0.000173 | -0.000133 | 0.000742 | -0.004451 | 0.004798 |
| 21 | decomposed_gift | V14_domestic_GJR | brier | 217 | -0.028761 | -0.055102 | 0.020108 | -0.112046 | 0.054524 |
| 21 | decomposed_gift | V14_domestic_GJR | endpoint_crps | 217 | -0.002300 | -0.003863 | 0.000601 | -0.007629 | 0.003029 |
| 21 | decomposed_gift | V15_gjr_restart | brier | 217 | -0.022427 | -0.046292 | 0.021850 | -0.128734 | 0.083881 |
| 21 | decomposed_gift | V15_gjr_restart | endpoint_crps | 217 | -0.002594 | -0.003937 | -0.000102 | -0.008954 | 0.003766 |
| 21 | decomposed_gift | historical_iv | brier | 217 | 0.019693 | 0.019862 | 0.019380 | -0.092403 | 0.131789 |
| 21 | decomposed_gift | historical_iv | endpoint_crps | 217 | -0.000136 | -0.000665 | 0.000845 | -0.005292 | 0.005020 |
| 21 | session_state | V14_domestic_GJR | brier | 217 | -0.025060 | -0.048127 | 0.017734 | -0.107657 | 0.057537 |
| 21 | session_state | V14_domestic_GJR | endpoint_crps | 217 | -0.002127 | -0.003788 | 0.000955 | -0.007519 | 0.003265 |
| 21 | session_state | V15_gjr_restart | brier | 217 | -0.018726 | -0.039317 | 0.019476 | -0.125847 | 0.088395 |
| 21 | session_state | V15_gjr_restart | endpoint_crps | 217 | -0.002421 | -0.003863 | 0.000252 | -0.008774 | 0.003931 |
| 21 | session_state | historical_iv | brier | 217 | 0.023394 | 0.026837 | 0.017006 | -0.089818 | 0.136605 |
| 21 | session_state | historical_iv | endpoint_crps | 217 | 0.000036 | -0.000591 | 0.001200 | -0.005019 | 0.005091 |
| 21 | multitask | V14_domestic_GJR | brier | 217 | -0.051101 | -0.090595 | 0.022172 | -0.160578 | 0.058377 |
| 21 | multitask | V14_domestic_GJR | endpoint_crps | 217 | -0.002893 | -0.004721 | 0.000499 | -0.008697 | 0.002911 |
| 21 | multitask | V15_gjr_restart | brier | 217 | -0.044766 | -0.081785 | 0.023914 | -0.176631 | 0.087099 |
| 21 | multitask | V15_gjr_restart | endpoint_crps | 217 | -0.003187 | -0.004796 | -0.000203 | -0.010013 | 0.003639 |
| 21 | multitask | historical_iv | brier | 217 | -0.002647 | -0.015631 | 0.021444 | -0.121582 | 0.116289 |
| 21 | multitask | historical_iv | endpoint_crps | 217 | -0.000729 | -0.001524 | 0.000744 | -0.005775 | 0.004316 |
| 21 | fixed_mixture | V14_domestic_GJR | brier | 217 | -0.025635 | -0.048829 | 0.017397 | -0.089390 | 0.038120 |
| 21 | fixed_mixture | V14_domestic_GJR | endpoint_crps | 217 | -0.001901 | -0.003112 | 0.000347 | -0.005873 | 0.002071 |
| 21 | fixed_mixture | V15_gjr_restart | brier | 217 | -0.019300 | -0.040020 | 0.019140 | -0.103920 | 0.065319 |
| 21 | fixed_mixture | V15_gjr_restart | endpoint_crps | 217 | -0.002195 | -0.003186 | -0.000356 | -0.007211 | 0.002820 |
| 21 | fixed_mixture | historical_iv | brier | 217 | 0.022819 | 0.026134 | 0.016669 | -0.058975 | 0.104613 |
| 21 | fixed_mixture | historical_iv | endpoint_crps | 217 | 0.000263 | 0.000086 | 0.000591 | -0.003315 | 0.003841 |

## Genuine GIFT coverage and isolated gap substitution

| horizon | candidate | control | metric | n | control loss | candidate loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | decomposed_gift | decomposed | brier | 253 | 0.249405 | 0.245288 | 0.004117 | -0.010983 | 0.019216 |
| 5 | decomposed_gift | decomposed | endpoint_crps | 253 | 0.011181 | 0.010786 | 0.000395 | -0.000193 | 0.000982 |
| 5 | session_state | decomposed | brier | 253 | 0.249405 | 0.241440 | 0.007965 | -0.005317 | 0.021246 |
| 5 | session_state | decomposed | endpoint_crps | 253 | 0.011181 | 0.010750 | 0.000431 | -0.000107 | 0.000969 |
| 5 | fixed_mixture | decomposed | brier | 253 | 0.249405 | 0.243355 | 0.006049 | -0.001802 | 0.013901 |
| 5 | fixed_mixture | decomposed | endpoint_crps | 253 | 0.011181 | 0.010855 | 0.000326 | -0.000076 | 0.000728 |
| 21 | decomposed_gift | decomposed | brier | 210 | 0.271139 | 0.275493 | -0.004354 | -0.017671 | 0.008963 |
| 21 | decomposed_gift | decomposed | endpoint_crps | 210 | 0.027530 | 0.027850 | -0.000320 | -0.001046 | 0.000407 |
| 21 | session_state | decomposed | brier | 210 | 0.271139 | 0.270901 | 0.000239 | -0.011933 | 0.012410 |
| 21 | session_state | decomposed | endpoint_crps | 210 | 0.027530 | 0.027688 | -0.000158 | -0.000867 | 0.000550 |
| 21 | fixed_mixture | decomposed | brier | 210 | 0.271139 | 0.270714 | 0.000425 | -0.028586 | 0.029436 |
| 21 | fixed_mixture | decomposed | endpoint_crps | 210 | 0.027530 | 0.027411 | 0.000119 | -0.000859 | 0.001096 |

## Cohort-specific direction probes by horizon

| target | model | n | brier | crps | balanced accuracy |
| --- | --- | --- | --- | --- | --- |
| five | domestic | 265 | 0.244661 | 0.010992 | 0.589282 |
| five | eq_fresh | 265 | 0.245016 | 0.010999 | 0.580042 |
| five | gift_conditional | 253 | 0.242828 | 0.011097 | 0.617483 |
| five | network_stack | 265 | 0.243146 | 0.010875 | 0.593555 |
| one | domestic | 258 | 0.254857 | 0.005007 | 0.522536 |
| one | eq_fresh | 258 | 0.248569 | 0.004892 | 0.550060 |
| one | gift_conditional | 248 | 0.207457 | 0.004226 | 0.733984 |
| one | network_stack | 258 | 0.229712 | 0.004511 | 0.604507 |
| ten | domestic | 249 | 0.287822 | 0.019291 | 0.503427 |
| ten | eq_fresh | 249 | 0.289623 | 0.019348 | 0.487172 |
| ten | gift_conditional | 241 | 0.285699 | 0.019536 | 0.506534 |
| three | domestic | 256 | 0.241090 | 0.008520 | 0.542968 |
| three | eq_fresh | 256 | 0.242762 | 0.008515 | 0.539870 |
| three | gift_conditional | 246 | 0.228590 | 0.008174 | 0.632974 |
| three | network_stack | 256 | 0.236439 | 0.008307 | 0.605226 |
| twentyone | domestic | 217 | 0.295068 | 0.031064 | 0.495125 |
| twentyone | eq_fresh | 217 | 0.294996 | 0.031064 | 0.495125 |
| twentyone | gift_conditional | 210 | 0.297077 | 0.031861 | 0.492480 |
| twentyone | network_stack | 217 | 0.293658 | 0.031308 | 0.523210 |
| two | domestic | 257 | 0.253172 | 0.006972 | 0.530660 |
| two | eq_fresh | 257 | 0.247718 | 0.006896 | 0.557606 |
| two | gift_conditional | 247 | 0.232798 | 0.006625 | 0.617062 |

The first-session mechanism carries most of the measured opening information. Short multi-session aggregates can retain that component. Stronger archived original-weekly and monthly direction models remain the primary tests of long-horizon gains. Forecasting a later session conditional on an observed first gap is evaluated in the post-opening research, at a separately stated clock.

[All original cohort comparisons](original-endpoint-leaderboard.csv) · [Exact quote-support ablation](path-gift-common-support.csv) · [All paired tests](multiscale-matched.csv) · [GJR and model-state ledger](path-fit-ledger.json) · [Model score rows](original-endpoint-scores.csv.gz)
