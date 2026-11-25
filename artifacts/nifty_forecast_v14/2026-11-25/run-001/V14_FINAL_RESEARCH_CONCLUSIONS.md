# V14 Final Research Conclusions

V14 evaluated **14,940** volatility rows, **184,198** marginal distribution rows,
**517,668** transition and extreme-event rows, **208,224** passage probabilities, and
**49,076** matched uncertainty comparisons. Full-horizon point leaders appear below. Strong predecessors remain in the rankings, and adjusted comparison bands condition on the frozen historical study.

| horizon | objective | metric | model | loss | n | disjoint |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | volatility | mae | gjr_ivx | 0.037402 | 265 | 53 |
| 5 | range | crps | V13_diffusion_iv | 0.005793 | 265 | 53 |
| 5 | direction | brier | sign_shrinkage | 0.228529 | 265 | 53 |
| 5 | endpoint_distribution | crps | sign_shrinkage | 0.010457 | 265 | 53 |
| 5 | touch | brier | trend_shrink | 0.143371 | 265 | 53 |
| 5 | joint | energy_score | V13_diffusion_iv | 1.562100 | 265 | 53 |
| 21 | volatility | mae | V13_GJR | 0.033179 | 217 | 11 |
| 21 | range | crps | gjr_student | 0.015422 | 217 | 11 |
| 21 | direction | brier | domestic_location_gjr_scale | 0.245042 | 217 | 11 |
| 21 | endpoint_distribution | crps | regime_state | 0.024750 | 217 | 11 |
| 21 | touch | brier | trend_persistent | 0.181085 | 217 | 11 |
| 21 | joint | energy_score | gjr_student | 2.487703 | 217 | 11 |

## Direct comparisons with strong predecessors

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | volatility | blend_gjr_iv | V13_raw_ATM | mae | 265 | 53 | 0.037978 | 0.037814 | -0.000163 | -0.004328 | 0.004002 | -0.004517 | 0.004190 |
| 5 | combined | volatility | gjr_ivx | V13_raw_ATM | mae | 265 | 53 | 0.037402 | 0.037814 | 0.000412 | -0.004650 | 0.005475 | -0.005030 | 0.005854 |
| 5 | combined | volatility | blend_gjr_iv | V13_GJR | mae | 265 | 53 | 0.037978 | 0.040318 | 0.002341 | -0.003197 | 0.007878 | -0.003168 | 0.007849 |
| 5 | combined | volatility | gjr_ivx | V13_GJR | mae | 265 | 53 | 0.037402 | 0.040318 | 0.002916 | -0.003588 | 0.009420 | -0.004085 | 0.009918 |
| 21 | combined | volatility | blend_gjr_iv | V13_bracketed_IV | mae | 217 | 11 | 0.033780 | 0.039406 | 0.005626 | -0.005548 | 0.016801 | -0.008300 | 0.019553 |
| 21 | combined | volatility | gjr_ivx | V13_bracketed_IV | mae | 217 | 11 | 0.037160 | 0.039406 | 0.002246 | -0.004798 | 0.009289 | -0.006952 | 0.011444 |
| 21 | combined | volatility | blend_gjr_iv | V13_GJR | mae | 217 | 11 | 0.033780 | 0.033179 | -0.000601 | -0.006422 | 0.005220 | -0.007932 | 0.006731 |
| 21 | combined | volatility | gjr_ivx | V13_GJR | mae | 217 | 11 | 0.037160 | 0.033179 | -0.003981 | -0.013102 | 0.005139 | -0.014425 | 0.006463 |
| 5 | combined | endpoint_return | regime_state | V13_week_CRPS | crps | 265 | 53 | 0.010956 | 0.010472 | -0.000484 | -0.001584 | 0.000615 | -0.001617 | 0.000649 |
| 5 | combined | endpoint_return | sign_shrinkage | V13_week_CRPS | crps | 265 | 53 | 0.010457 | 0.010472 | 0.000015 | -0.000594 | 0.000624 | -0.000661 | 0.000691 |
| 21 | combined | endpoint_return | regime_state | V13_IV_scaled_symmetric | crps | 217 | 11 | 0.024750 | 0.025220 | 0.000470 | -0.000394 | 0.001334 | -0.000492 | 0.001433 |
| 21 | combined | endpoint_return | sign_shrinkage | V13_IV_scaled_symmetric | crps | 217 | 11 | 0.025220 | 0.025220 | 0.000000 | -0.000000 | 0.000000 | -0.000000 | 0.000000 |
| 5 | combined | range | gjr_iv | V13_diffusion_iv | crps | 265 | 53 | 0.005850 | 0.005793 | -0.000058 | -0.000881 | 0.000766 | -0.000913 | 0.000797 |
| 5 | combined | range | gjr_student | V13_diffusion_iv | crps | 265 | 53 | 0.006432 | 0.005793 | -0.000639 | -0.002399 | 0.001120 | -0.002255 | 0.000976 |
| 5 | combined | range | joint_tail_width | V13_diffusion_iv | crps | 265 | 53 | 0.005924 | 0.005793 | -0.000132 | -0.000612 | 0.000349 | -0.000649 | 0.000385 |
| 21 | combined | range | gjr_iv | V13_diffusion_iv | crps | 217 | 11 | 0.016304 | 0.016275 | -0.000029 | -0.002716 | 0.002658 | -0.003272 | 0.003214 |
| 21 | combined | range | gjr_student | V13_diffusion_iv | crps | 217 | 11 | 0.015422 | 0.016275 | 0.000854 | -0.003811 | 0.005518 | -0.004407 | 0.006115 |
| 21 | combined | range | joint_tail_width | V13_diffusion_iv | crps | 217 | 11 | 0.017072 | 0.016275 | -0.000797 | -0.003848 | 0.002255 | -0.004432 | 0.002838 |
| 5 | combined | fixed_touch_family | gjr_iv | V13_diffusion_iv | brier | 265 | 53 | 0.145105 | 0.144154 | -0.000951 | -0.004686 | 0.002785 | -0.004784 | 0.002883 |
| 5 | combined | fixed_touch_family | gjr_student | V13_diffusion_iv | brier | 265 | 53 | 0.148325 | 0.144154 | -0.004170 | -0.011723 | 0.003383 | -0.011439 | 0.003098 |
| 5 | combined | fixed_touch_family | joint_tail_width | V13_diffusion_iv | brier | 265 | 53 | 0.145731 | 0.144154 | -0.001576 | -0.006240 | 0.003088 | -0.006176 | 0.003023 |
| 5 | combined | fixed_touch_family | path_mixture | V13_diffusion_iv | brier | 265 | 53 | 0.145614 | 0.144154 | -0.001460 | -0.006139 | 0.003220 | -0.006089 | 0.003170 |
| 5 | combined | fixed_touch_family | regime_state | V13_diffusion_iv | brier | 265 | 53 | 0.150884 | 0.144154 | -0.006729 | -0.014799 | 0.001340 | -0.014813 | 0.001355 |
| 21 | combined | fixed_touch_family | gjr_iv | V13_analytic_iv_diffusion | brier | 217 | 11 | 0.183138 | 0.184067 | 0.000930 | -0.004508 | 0.006367 | -0.005019 | 0.006879 |
| 21 | combined | fixed_touch_family | gjr_student | V13_analytic_iv_diffusion | brier | 217 | 11 | 0.183636 | 0.184067 | 0.000431 | -0.009705 | 0.010567 | -0.009403 | 0.010266 |
| 21 | combined | fixed_touch_family | joint_tail_width | V13_analytic_iv_diffusion | brier | 217 | 11 | 0.187823 | 0.184067 | -0.003756 | -0.015630 | 0.008119 | -0.016530 | 0.009019 |
| 21 | combined | fixed_touch_family | path_mixture | V13_analytic_iv_diffusion | brier | 217 | 11 | 0.187516 | 0.184067 | -0.003448 | -0.015328 | 0.008431 | -0.016230 | 0.009334 |
| 21 | combined | fixed_touch_family | regime_state | V13_analytic_iv_diffusion | brier | 217 | 11 | 0.186681 | 0.184067 | -0.002614 | -0.015030 | 0.009802 | -0.015066 | 0.009838 |

Many extreme labels share the same realized episode. Independent evidence still requires new disjoint outcomes. The October replay documents how dispersion and path calibration can improve average metrics while substantial upside moves remain difficult.

[All 19 reports](NIFTY_V14_RESEARCH.md) · [Calibration](V14_PREDICTIVE_CALIBRATION_AND_INTERVALS.md) · [Failure cases](V14_FORECAST_FAILURE_FORENSICS.md).
