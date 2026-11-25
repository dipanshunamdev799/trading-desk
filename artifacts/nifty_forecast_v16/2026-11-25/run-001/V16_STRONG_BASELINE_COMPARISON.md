# V16 Strong directional baselines

The primary weekly references are the historical V14 weekly sign-shrinkage Brier 0.228529 and return CRPS 0.010457. The primary monthly references are the V14 domestic location/GJR Brier 0.245042 and V15 restarted-GJR CRPS 0.024694. Neutral symmetric sign gives Brier 0.250000. We also score a matured empirical frequency and distribution, lagged momentum and mean reversion applied to centered joint paths, domestic rotation and official breadth, simple additive global and domestic state and fixed mixture. The protected V8 residualized rotation and V11, V12 and V13 comparators retain their documented coverage. Pre-auction single-US and simple equal-global returns are shown alongside the GIFT price-change rule.

## Simple same-morning baselines

| model | n | brier | crps | log loss | correct | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| gift_raw | 248 | 0.100841 | 0.001459 | 0.348603 | 0.887097 | 0.887097 |
| gift_calibrated | 248 | 0.100937 | 0.001451 | 0.349021 | 0.870968 | 0.870968 |
| single_US | 258 | 0.224937 | 0.002999 | 0.642687 | 0.631783 | 0.631190 |
| equal_six | 258 | 0.237415 | 0.003037 | 0.670114 | 0.600775 | 0.600060 |
| neutral | 258 | 0.250000 | 0.003171 | 0.693147 | 0.503876 | 0.500000 |
| historical | 258 | 0.253615 | 0.003194 | 0.700465 | 0.484496 | 0.482933 |
| domestic | 258 | 0.257213 | 0.003238 | 0.723334 | 0.577519 | 0.576983 |
| prior_return | 258 | 0.263743 | 0.003249 | 0.734012 | 0.457364 | 0.455589 |

## Original weekly and monthly benchmarks on available cases

| horizon | model | n | brier | endpoint crps | log loss | accuracy | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V8_R_RESIDUAL | 92 | 0.159504 | 0.009852 | 0.499670 | 0.804348 | 0.809869 |
| 5 | V14_sign_shrinkage | 265 | 0.228529 | 0.010457 | 0.648943 | 0.626415 | 0.636001 |
| 5 | V13_IV_all_phase | 265 | 0.229587 | 0.010609 | 0.651757 | 0.626415 | 0.636001 |
| 5 | V12_NATIVE_RV | 265 | 0.229715 | 0.010896 | 0.655524 | 0.626415 | 0.633316 |
| 5 | J11_BREADTH_ALL | 265 | 0.236138 | 0.010960 | 0.667636 | 0.637736 | 0.650612 |
| 5 | session_state | 265 | 0.239546 | 0.010466 | 0.673356 | 0.603774 | 0.598724 |
| 5 | fixed_mixture | 265 | 0.241548 | 0.010570 | 0.676422 | 0.603774 | 0.593353 |
| 5 | decomposed_gift | 265 | 0.242618 | 0.010493 | 0.681034 | 0.611321 | 0.608166 |
| 5 | direct_domestic | 265 | 0.243813 | 0.010799 | 0.681519 | 0.615094 | 0.607964 |
| 5 | direct_global | 265 | 0.245662 | 0.010854 | 0.685002 | 0.600000 | 0.595345 |
| 5 | V15_iv_restart | 265 | 0.248408 | 0.010682 | 0.689963 | 0.528302 | 0.537422 |
| 5 | neutral | 265 | 0.250000 | 0.011055 | 0.693147 | 0.441509 | 0.500000 |
| 5 | V15_gjr_restart | 265 | 0.250763 | 0.010922 | 0.694695 | 0.539623 | 0.573516 |
| 5 | prev_mean_reversion | 265 | 0.252927 | 0.010927 | 0.699259 | 0.520755 | 0.523504 |
| 5 | prev_momentum | 265 | 0.253152 | 0.010858 | 0.699498 | 0.464151 | 0.464772 |
| 5 | matured_historical | 265 | 0.254407 | 0.011233 | 0.702309 | 0.483019 | 0.485245 |
| 5 | historical_iv | 265 | 0.256325 | 0.011043 | 0.706286 | 0.516981 | 0.511175 |
| 21 | V14_domestic_GJR | 217 | 0.245042 | 0.024989 | 0.683095 | 0.511521 | 0.502675 |
| 21 | V15_iv_restart | 217 | 0.247721 | 0.025027 | 0.688575 | 0.534562 | 0.537144 |
| 21 | prev_mean_reversion | 217 | 0.248912 | 0.025900 | 0.690913 | 0.488479 | 0.496160 |
| 21 | neutral | 217 | 0.250000 | 0.025435 | 0.693147 | 0.437788 | 0.500000 |
| 21 | V15_gjr_restart | 217 | 0.251376 | 0.024694 | 0.695900 | 0.479263 | 0.524072 |
| 21 | prev_momentum | 217 | 0.253503 | 0.026002 | 0.700209 | 0.479263 | 0.479810 |
| 21 | V8_R_RESIDUAL | 76 | 0.257806 | 0.030146 | 0.712817 | 0.552632 | 0.587097 |
| 21 | session_state | 217 | 0.270103 | 0.027116 | 0.749273 | 0.529954 | 0.507420 |
| 21 | fixed_mixture | 217 | 0.270677 | 0.026890 | 0.739064 | 0.502304 | 0.483995 |
| 21 | decomposed_gift | 217 | 0.273803 | 0.027288 | 0.760809 | 0.520737 | 0.501553 |
| 21 | direct_global | 217 | 0.282919 | 0.027832 | 0.779274 | 0.502304 | 0.481665 |
| 21 | direct_domestic | 217 | 0.283087 | 0.027741 | 0.779673 | 0.502304 | 0.482830 |
| 21 | V13_IV_all_phase | 217 | 0.284302 | 0.028227 | 0.774921 | 0.470046 | 0.499569 |
| 21 | historical_iv | 217 | 0.293496 | 0.027152 | 0.790282 | 0.465438 | 0.490811 |
| 21 | matured_historical | 217 | 0.294673 | 0.027117 | 0.792754 | 0.479263 | 0.499612 |
| 21 | J11_BREADTH_ALL | 217 | 0.299436 | 0.031283 | 0.812371 | 0.456221 | 0.480285 |
| 21 | V12_NATIVE_RV | 217 | 0.363025 | 0.032602 | 0.974514 | 0.345622 | 0.349310 |

## Direction gain over the strongest earlier directional references

| horizon | candidate | control | n | candidate loss | control loss | gain | early gain | later gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | historical_iv | V14_sign_shrinkage | 265 | 0.256325 | 0.228529 | -0.027796 | -0.012116 | -0.057281 | -0.063243 | 0.007652 |
| 5 | direct_domestic | V14_sign_shrinkage | 265 | 0.243813 | 0.228529 | -0.015284 | -0.014045 | -0.017614 | -0.039085 | 0.008518 |
| 5 | direct_global | V14_sign_shrinkage | 265 | 0.245662 | 0.228529 | -0.017133 | -0.012917 | -0.025060 | -0.044640 | 0.010374 |
| 5 | prev_momentum | V14_sign_shrinkage | 265 | 0.253152 | 0.228529 | -0.024623 | -0.011401 | -0.049487 | -0.053746 | 0.004499 |
| 5 | prev_mean_reversion | V14_sign_shrinkage | 265 | 0.252927 | 0.228529 | -0.024398 | -0.008605 | -0.054095 | -0.059809 | 0.011013 |
| 5 | decomposed_gift | V14_sign_shrinkage | 265 | 0.242618 | 0.228529 | -0.014090 | -0.010418 | -0.020994 | -0.043483 | 0.015304 |
| 5 | session_state | V14_sign_shrinkage | 265 | 0.239546 | 0.228529 | -0.011018 | -0.007049 | -0.018481 | -0.038117 | 0.016082 |
| 5 | fixed_mixture | V14_sign_shrinkage | 265 | 0.241548 | 0.228529 | -0.013019 | -0.005736 | -0.026714 | -0.035402 | 0.009364 |
| 5 | neutral | V14_sign_shrinkage | 265 | 0.250000 | 0.228529 | -0.021471 | -0.007233 | -0.048246 | -0.052536 | 0.009593 |
| 5 | matured_historical | V14_sign_shrinkage | 265 | 0.254407 | 0.228529 | -0.025878 | -0.013137 | -0.049836 | -0.060114 | 0.008359 |
| 21 | historical_iv | V14_domestic_GJR | 217 | 0.293496 | 0.245042 | -0.048454 | -0.074963 | 0.000728 | -0.123288 | 0.026380 |
| 21 | direct_domestic | V14_domestic_GJR | 217 | 0.283087 | 0.245042 | -0.038045 | -0.062018 | 0.006430 | -0.140607 | 0.064516 |
| 21 | direct_global | V14_domestic_GJR | 217 | 0.282919 | 0.245042 | -0.037877 | -0.064036 | 0.010656 | -0.140634 | 0.064880 |
| 21 | prev_momentum | V14_domestic_GJR | 217 | 0.253503 | 0.245042 | -0.008461 | -0.010580 | -0.004529 | -0.032169 | 0.015247 |
| 21 | prev_mean_reversion | V14_domestic_GJR | 217 | 0.248912 | 0.245042 | -0.003870 | -0.002418 | -0.006565 | -0.031229 | 0.023489 |
| 21 | decomposed_gift | V14_domestic_GJR | 217 | 0.273803 | 0.245042 | -0.028761 | -0.055102 | 0.020108 | -0.112046 | 0.054524 |
| 21 | session_state | V14_domestic_GJR | 217 | 0.270103 | 0.245042 | -0.025060 | -0.048127 | 0.017734 | -0.107657 | 0.057537 |
| 21 | fixed_mixture | V14_domestic_GJR | 217 | 0.270677 | 0.245042 | -0.025635 | -0.048829 | 0.017397 | -0.089390 | 0.038120 |
| 21 | neutral | V14_domestic_GJR | 217 | 0.250000 | 0.245042 | -0.004958 | -0.005382 | -0.004171 | -0.029499 | 0.019583 |
| 21 | matured_historical | V14_domestic_GJR | 217 | 0.294673 | 0.245042 | -0.049631 | -0.074953 | -0.002653 | -0.126141 | 0.026879 |

Earlier standalone probabilities may have different empirical support and score distributions from the coherent path benchmarks. The protected historical benchmark results remain comparable on matched dates. The core forward assumption remains that all outcomes after the original decision must be forecast or integrated out.

[Original cohort-level leaderboard](original-endpoint-leaderboard.csv) · [Original endpoint scores](original-endpoint-scores.csv.gz) · [Matched original-horizon uncertainty](multiscale-matched.csv) · [Frozen V15 model ranking](../../../nifty_forecast_v15/2026-11-25/run-001/NIFTY_V15_RESEARCH.md)
