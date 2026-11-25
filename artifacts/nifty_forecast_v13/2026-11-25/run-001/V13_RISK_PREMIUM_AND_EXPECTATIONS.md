# V13 Risk Premium And Expectations

The ex-ante proxy is nearest ATM IV squared less trailing HAR21 risk squared. The ex-post implied-minus-realized error remains an outcome. Pricing tiers use the matured training quartiles. The regressions test pricing changes, downside shape and interactions with breadth and financial rotation. For a physical candidate, option-derived endpoint dispersion is adjusted on matured forecasts and sign mass receives a strongly regularized logit calibration. The fixed mixture gives calibrated shape 25% weight.

| horizon | regime | n | mean_implied | mean_realized | var_gap | expanded | magnitude | mean_return |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | cheap | 77 | 0.130702 | 0.129230 | -0.011341 | 0.311688 | 0.016054 | 0.000044 |
| 5 | expensive | 82 | 0.160412 | 0.147645 | 0.011958 | 0.695122 | 0.017187 | 0.000865 |
| 5 | middle | 106 | 0.110342 | 0.101863 | 0.001722 | 0.424528 | 0.012672 | -0.000763 |
| 21 | cheap | 51 | 0.146550 | 0.165859 | -0.015870 | 0.450980 | 0.055954 | -0.038080 |
| 21 | expensive | 58 | 0.148972 | 0.156000 | 0.009611 | 0.741379 | 0.025886 | 0.004893 |
| 21 | middle | 108 | 0.119227 | 0.115185 | 0.002062 | 0.462963 | 0.026727 | 0.000215 |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | premium_ridge | har_iv | volatility | mae | 265 | 53 | 0.039695 | 0.039714 | 0.000019 | -0.004050 | 0.004087 | -0.004046 | 0.004084 |
| 5 | combined | regime_iv | har_iv | volatility | mae | 265 | 53 | 0.041212 | 0.039714 | -0.001499 | -0.004787 | 0.001790 | -0.004992 | 0.001994 |
| 5 | combined | premium_ridge | iv_nearest | volatility | mae | 265 | 53 | 0.039695 | 0.037814 | -0.001881 | -0.011261 | 0.007500 | -0.014020 | 0.010258 |
| 5 | combined | regime_iv | iv_nearest | volatility | mae | 265 | 53 | 0.041212 | 0.037814 | -0.003398 | -0.012768 | 0.005972 | -0.015839 | 0.009043 |
| 5 | combined | premium_ridge | har_iv | volatility | qlike | 265 | 53 | 0.409416 | 0.367964 | -0.041452 | -0.137414 | 0.054510 | -0.143796 | 0.060892 |
| 5 | combined | regime_iv | har_iv | volatility | qlike | 265 | 53 | 0.413977 | 0.367964 | -0.046013 | -0.179190 | 0.087164 | -0.165928 | 0.073901 |
| 5 | combined | premium_ridge | iv_nearest | volatility | qlike | 265 | 53 | 0.409416 | 0.276187 | -0.133229 | -0.328012 | 0.061554 | -0.393787 | 0.127328 |
| 5 | combined | regime_iv | iv_nearest | volatility | qlike | 265 | 53 | 0.413977 | 0.276187 | -0.137790 | -0.359769 | 0.084188 | -0.420145 | 0.144565 |
| 21 | combined | premium_ridge | har_iv | volatility | mae | 217 | 11 | 0.056048 | 0.051513 | -0.004535 | -0.014161 | 0.005091 | -0.012576 | 0.003505 |
| 21 | combined | regime_iv | har_iv | volatility | mae | 217 | 11 | 0.057244 | 0.051513 | -0.005731 | -0.018485 | 0.007022 | -0.019979 | 0.008516 |
| 21 | combined | premium_ridge | iv_bracket | volatility | mae | 217 | 11 | 0.056048 | 0.039406 | -0.016642 | -0.041277 | 0.007993 | -0.044709 | 0.011426 |
| 21 | combined | regime_iv | iv_bracket | volatility | mae | 217 | 11 | 0.057244 | 0.039406 | -0.017838 | -0.046263 | 0.010587 | -0.051911 | 0.016235 |
| 21 | combined | premium_ridge | har_iv | volatility | qlike | 217 | 11 | 0.668066 | 0.577685 | -0.090381 | -0.197121 | 0.016359 | -0.204723 | 0.023962 |
| 21 | combined | regime_iv | har_iv | volatility | qlike | 217 | 11 | 0.677450 | 0.577685 | -0.099765 | -0.353616 | 0.154086 | -0.337314 | 0.137784 |
| 21 | combined | premium_ridge | iv_bracket | volatility | qlike | 217 | 11 | 0.668066 | 0.267623 | -0.400443 | -0.951522 | 0.150636 | -1.098429 | 0.297542 |
| 21 | combined | regime_iv | iv_bracket | volatility | qlike | 217 | 11 | 0.677450 | 0.267623 | -0.409827 | -1.055145 | 0.235490 | -1.182780 | 0.363125 |

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | pinball | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | NEUTRAL | 265 | 53 | 0.250000 | 0.693147 | 0.528302 | 0.488190 | 0.011058 | 0.015052 | 0.005498 | 0.735849 | 0.039228 |
| 5 | combined | P12_Q_PHYSICAL_MIX | 265 | 53 | 0.244491 | 0.682747 | 0.588679 | 0.604008 | 0.010704 | 0.014972 | 0.005288 | 0.811321 | 0.046216 |
| 5 | combined | Q12_RAW | 265 | 53 | 0.268655 | 0.731434 | 0.433962 | 0.484292 | 0.011151 | 0.015417 | 0.005490 | 0.781132 | 0.047002 |
| 5 | combined | V12_STAT | 265 | 53 | 0.244333 | 0.682878 | 0.588679 | 0.602218 | 0.010777 | 0.015044 | 0.005343 | 0.807547 | 0.048008 |
| 5 | combined | q_physical_adjusted | 236 | 48 | 0.256579 | 0.706673 | 0.491525 | 0.445430 | 0.011456 | 0.015762 | 0.005636 | 0.716102 | 0.040496 |
| 5 | combined | q_physical_mix25 | 236 | 48 | 0.246746 | 0.687812 | 0.610169 | 0.617865 | 0.011204 | 0.015672 | 0.005529 | 0.792373 | 0.046467 |
| 21 | combined | NEUTRAL | 217 | 11 | 0.250000 | 0.693147 | 0.511521 | 0.460742 | 0.025420 | 0.033371 | 0.012678 | 0.635945 | 0.068179 |
| 21 | combined | P12_Q_PHYSICAL_MIX | 199 | 11 | 0.307439 | 0.831921 | 0.492462 | 0.532260 | 0.028819 | 0.037772 | 0.014580 | 0.633166 | 0.089227 |
| 21 | combined | Q12_RAW | 199 | 11 | 0.283476 | 0.762276 | 0.437186 | 0.501646 | 0.026814 | 0.034804 | 0.013417 | 0.718593 | 0.099362 |
| 21 | combined | V12_STAT | 217 | 11 | 0.306090 | 0.831132 | 0.502304 | 0.536411 | 0.028994 | 0.038419 | 0.014686 | 0.626728 | 0.089992 |
| 21 | combined | q_physical_adjusted | 154 | 9 | 0.271401 | 0.737198 | 0.538961 | 0.494048 | 0.031363 | 0.041623 | 0.015557 | 0.610390 | 0.089996 |
| 21 | combined | q_physical_mix25 | 154 | 9 | 0.266752 | 0.729026 | 0.519481 | 0.530952 | 0.031337 | 0.041634 | 0.015869 | 0.649351 | 0.099945 |

[Ex-ante and ex-post variance ledgers](variance-premium-origins.csv) · [Timing and fit parameters](path-ledger.json).
