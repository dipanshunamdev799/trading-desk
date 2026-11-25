# V13 Final Research Conclusions

These are point leaders from the same frozen historical study. Raw implied volatility, the empirical and RV-scaled paths, and the original V12 endpoint leaders remain explicit competing benchmarks. Different outcome types and effective sample sizes explain why the leaders may differ. The comparisons are historical and research-exposed.

| horizon | raw_iv_mae | vol_model | vol_mae | range_model | range_crps | touch_model | touch_brier | direction_model | endpoint_brier | distribution_model | endpoint_crps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.037814 | iv_calibrated | 0.037517 | diffusion_iv | 0.005793 | diffusion_iv | 0.144154 | PH_NATIVE_PHASE_MIXTURE__scale_only | 0.229587 | J12_GROUP_BALANCED__scale_only | 0.010472 |
| 21 | 0.039406 | gjr | 0.033179 | diffusion_iv | 0.016275 | analytic_iv_diffusion | 0.184067 | NEUTRAL | 0.250000 | NEUTRAL__scale_only | 0.025220 |

## Principal benchmark comparisons

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | iv_calibrated | iv_nearest | volatility | mae | 265 | 53 | 0.037517 | 0.037814 | 0.000297 | -0.007117 | 0.007712 | -0.009132 | 0.009727 |
| 21 | combined | gjr | iv_bracket | volatility | mae | 217 | 11 | 0.033179 | 0.039406 | 0.006227 | -0.005154 | 0.017609 | -0.007197 | 0.019651 |
| 5 | combined | diffusion_iv | empirical_exact | range | crps | 265 | 53 | 0.005793 | 0.007918 | 0.002126 | -0.001547 | 0.005799 | -0.002492 | 0.006743 |
| 5 | combined | diffusion_iv | iv_scaled | range | crps | 265 | 53 | 0.005793 | 0.005961 | 0.000168 | -0.000376 | 0.000712 | -0.000458 | 0.000794 |
| 21 | combined | diffusion_iv | empirical_exact | range | crps | 217 | 11 | 0.016275 | 0.019522 | 0.003247 | -0.005369 | 0.011863 | -0.007400 | 0.013893 |
| 21 | combined | diffusion_iv | iv_scaled | range | crps | 217 | 11 | 0.016275 | 0.018162 | 0.001887 | -0.002212 | 0.005985 | -0.003495 | 0.007268 |
| 5 | combined | diffusion_iv | empirical_exact | touch_family | brier | 265 | 53 | 0.144154 | 0.156019 | 0.011864 | -0.004748 | 0.028476 | -0.007469 | 0.031197 |
| 5 | combined | diffusion_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.144154 | 0.147679 | 0.003524 | -0.005408 | 0.012457 | -0.006657 | 0.013706 |
| 21 | combined | diffusion_iv | empirical_exact | touch_family | brier | 217 | 11 | 0.185037 | 0.206812 | 0.021775 | -0.009256 | 0.052805 | -0.014865 | 0.058414 |
| 21 | combined | diffusion_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.185037 | 0.197163 | 0.012126 | -0.008300 | 0.032552 | -0.010727 | 0.034979 |

## Adjusted historical gains

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | V8_R_RESIDUAL | NEUTRAL | endpoint_return | brier | 92 | 19 | 0.159504 | 0.250000 | 0.090496 | 0.012753 | 0.168239 | -0.016598 | 0.197590 |
| 5 | combined | V8_R_RESIDUAL__half_scale | NEUTRAL | endpoint_return | brier | 92 | 19 | 0.161214 | 0.250000 | 0.088786 | 0.007875 | 0.169698 | -0.023043 | 0.200616 |
| 5 | combined | V8_W_STRUCT_EMBARGO_EQ | NEUTRAL | endpoint_return | brier | 92 | 19 | 0.161638 | 0.250000 | 0.088362 | 0.000056 | 0.176669 | -0.030228 | 0.206953 |
| 5 | combined | V8_R_RESIDUAL__scale_only | NEUTRAL | endpoint_return | brier | 92 | 19 | 0.162178 | 0.250000 | 0.087822 | 0.005509 | 0.170135 | -0.025592 | 0.201236 |
| 5 | combined | J10_STRUCTURAL_BLEND__half_scale | J10_STRUCTURAL_BLEND | endpoint_return | crps | 265 | 53 | 0.010838 | 0.011043 | 0.000205 | 0.000006 | 0.000403 | -0.000026 | 0.000435 |
| 21 | combined | O_NATIVE_PHASE0__scale_only | O_NATIVE_PHASE0 | endpoint_return | crps | 217 | 11 | 0.031454 | 0.033337 | 0.001883 | 0.000582 | 0.003184 | 0.000537 | 0.003229 |
| 21 | combined | O_NATIVE_PHASE0__half_scale | O_NATIVE_PHASE0 | endpoint_return | crps | 217 | 11 | 0.032320 | 0.033337 | 0.001017 | 0.000361 | 0.001674 | 0.000305 | 0.001729 |

[All comparisons](paired-search-adjusted.csv) · [Research forecast replay](V13_EXPERIMENTAL_FORECAST_REPORT.md) · [Verification](verification.json).
