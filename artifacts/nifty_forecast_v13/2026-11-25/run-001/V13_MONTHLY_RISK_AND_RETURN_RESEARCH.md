# V13 Monthly Risk And Return Research

The 217 monthly rolling outcomes comprise 11 non-overlapping windows. The symmetric statistical benchmark and phase-accounted forecasts remain separate from monthly range and volatility candidates. Market-priced direction and exact-expiry scores use the corresponding matched subsets. The tables give separate risk and endpoint rankings.

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | pinball | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | combined | NEUTRAL | 217 | 11 | 0.250000 | 0.693147 | 0.511521 | 0.460742 | 0.025420 | 0.033371 | 0.012678 | 0.635945 | 0.068179 |
| 21 | combined | NEUTRAL__half_scale | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025283 | 0.033371 | 0.012616 | 0.654378 | 0.072109 |
| 21 | combined | NEUTRAL__scale_only | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025220 | 0.033371 | 0.012574 | 0.672811 | 0.077357 |
| 21 | combined | diffusion_iv | 217 | 11 | 0.253656 | 0.700479 | 0.442396 | 0.441199 | 0.025337 | 0.033688 | 0.012639 | 0.741935 | 0.098063 |
| 21 | combined | J10_STRUCTURAL_BLEND__half_scale | 217 | 11 | 0.281459 | 0.762615 | 0.497696 | 0.521829 | 0.029671 | 0.040350 | 0.014806 | 0.645161 | 0.089603 |
| 21 | combined | J10_STRUCTURAL_BLEND__scale_only | 217 | 11 | 0.281773 | 0.767019 | 0.493088 | 0.517731 | 0.029575 | 0.040351 | 0.014761 | 0.622120 | 0.090442 |
| 21 | combined | PH_NATIVE_PHASE_MIXTURE__scale_only | 217 | 11 | 0.284302 | 0.774921 | 0.470046 | 0.499569 | 0.028227 | 0.038703 | 0.014103 | 0.635945 | 0.092555 |
| 21 | combined | PH_NATIVE_POOLED__scale_only | 217 | 11 | 0.285370 | 0.769641 | 0.447005 | 0.463934 | 0.028821 | 0.038235 | 0.014360 | 0.589862 | 0.086452 |
| 21 | combined | PH_NATIVE_PHASE_MIXTURE__half_scale | 217 | 11 | 0.285978 | 0.779070 | 0.460829 | 0.490207 | 0.028676 | 0.038703 | 0.014370 | 0.631336 | 0.092890 |
| 21 | combined | J10_STRUCTURAL_BLEND | 217 | 11 | 0.286258 | 0.779483 | 0.497696 | 0.521829 | 0.030036 | 0.040356 | 0.015057 | 0.645161 | 0.090629 |
| 21 | combined | J12_GROUP_BALANCED__scale_only | 217 | 11 | 0.288318 | 0.779408 | 0.488479 | 0.526445 | 0.027282 | 0.036491 | 0.013707 | 0.658986 | 0.087833 |
| 21 | combined | PH_NATIVE_PHASE_MIXTURE | 217 | 11 | 0.290905 | 0.795663 | 0.456221 | 0.483779 | 0.029347 | 0.038706 | 0.014760 | 0.599078 | 0.095326 |
| 21 | combined | J12_GROUP_BALANCED__half_scale | 217 | 11 | 0.292127 | 0.789596 | 0.483871 | 0.521182 | 0.027602 | 0.036491 | 0.013877 | 0.649770 | 0.086003 |
| 21 | combined | PH_NATIVE_POOLED__half_scale | 217 | 11 | 0.296070 | 0.797873 | 0.456221 | 0.473296 | 0.029571 | 0.038234 | 0.014818 | 0.594470 | 0.083994 |

| horizon | cohort | model | n | disjoint | mae | rmse | qlike | bias | spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | combined | gjr | 217 | 11 | 0.033179 | 0.043304 | 0.199677 | -0.009266 | 0.528229 |
| 21 | combined | egarch | 217 | 11 | 0.034943 | 0.047496 | 0.302016 | -0.010128 | 0.406027 |
| 21 | combined | iv_same_close | 217 | 11 | 0.038369 | 0.047998 | 0.247182 | -0.003464 | 0.478775 |
| 21 | combined | iv_bracket_session | 217 | 11 | 0.038961 | 0.048676 | 0.248656 | -0.002596 | 0.481541 |
| 21 | combined | prior_intraday | 217 | 11 | 0.039122 | 0.054761 | 0.419481 | -0.026428 | 0.337372 |
| 21 | combined | iv_session | 217 | 11 | 0.039186 | 0.049268 | 0.248078 | -0.001740 | 0.487523 |
| 21 | combined | prior_etf | 217 | 11 | 0.039290 | 0.055809 | 0.450064 | -0.028341 | 0.318725 |
| 21 | combined | india_vix | 217 | 11 | 0.039352 | 0.046684 | 0.206322 | 0.006166 | 0.497809 |
| 21 | combined | iv_bracket | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | combined | iv_legacy_bracket | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | combined | iv_rate_zero | 217 | 11 | 0.039527 | 0.049790 | 0.269100 | -0.004253 | 0.448168 |
| 21 | combined | iv_nearest | 217 | 11 | 0.039639 | 0.049835 | 0.266465 | -0.003579 | 0.448765 |
| 21 | combined | iv_smooth | 217 | 11 | 0.039639 | 0.049835 | 0.266465 | -0.003579 | 0.448765 |
| 21 | combined | iv_truncated | 217 | 11 | 0.039639 | 0.049835 | 0.266465 | -0.003579 | 0.448765 |
| 21 | combined | iv_rate_high | 217 | 11 | 0.039677 | 0.049831 | 0.265154 | -0.003262 | 0.448572 |
| 21 | combined | iv_future_forward | 217 | 11 | 0.039687 | 0.049904 | 0.266547 | -0.003466 | 0.448094 |
| 21 | combined | iv_settlement | 217 | 11 | 0.039782 | 0.049937 | 0.267237 | -0.003480 | 0.447294 |
| 21 | combined | iv_liquid | 217 | 11 | 0.039939 | 0.050100 | 0.276596 | -0.004023 | 0.439040 |

| horizon | cohort | model | target | n | disjoint | mae | crps | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | combined | rv_scaled | abs_return | 217 | 11 | 0.022306 | 0.016303 | 0.008068 | 0.400922 | 0.691244 | 0.053947 |
| 21 | combined | diffusion_iv | abs_return | 217 | 11 | 0.023434 | 0.016843 | 0.008351 | 0.428571 | 0.700461 | 0.058036 |
| 21 | combined | empirical_exact | abs_return | 217 | 11 | 0.022307 | 0.017260 | 0.008585 | 0.405530 | 0.682028 | 0.047341 |
| 21 | combined | iv_scaled | abs_return | 217 | 11 | 0.022767 | 0.017290 | 0.008549 | 0.364055 | 0.714286 | 0.053119 |
| 21 | combined | state_iv | abs_return | 217 | 11 | 0.023643 | 0.017791 | 0.008886 | 0.373272 | 0.658986 | 0.054734 |
| 21 | combined | diffusion_iv | drawdown | 217 | 11 | 0.020242 | 0.014985 | 0.007476 | 0.474654 | 0.682028 | 0.046982 |
| 21 | combined | rv_scaled | drawdown | 217 | 11 | 0.023597 | 0.016094 | 0.008151 | 0.373272 | 0.682028 | 0.055226 |
| 21 | combined | empirical_exact | drawdown | 217 | 11 | 0.019789 | 0.016452 | 0.008255 | 0.465438 | 0.714286 | 0.042709 |
| 21 | combined | iv_scaled | drawdown | 217 | 11 | 0.022961 | 0.016754 | 0.008390 | 0.460829 | 0.686636 | 0.050562 |
| 21 | combined | state_iv | drawdown | 217 | 11 | 0.023667 | 0.017018 | 0.008553 | 0.447005 | 0.672811 | 0.053713 |
| 21 | combined | state_iv | high | 217 | 11 | 0.016974 | 0.012347 | 0.006102 | 0.419355 | 0.705069 | 0.044298 |
| 21 | combined | iv_scaled | high | 217 | 11 | 0.017124 | 0.012385 | 0.006116 | 0.414747 | 0.732719 | 0.044989 |
| 21 | combined | diffusion_iv | high | 217 | 11 | 0.018442 | 0.012447 | 0.006164 | 0.552995 | 0.797235 | 0.060312 |
| 21 | combined | rv_scaled | high | 217 | 11 | 0.019623 | 0.013551 | 0.006661 | 0.396313 | 0.705069 | 0.051689 |
| 21 | combined | separate_range_ridge | high | 217 | 11 | 0.018427 | 0.013877 | 0.006891 | 0.410138 | 0.640553 | 0.039639 |
| 21 | combined | empirical_exact | high | 217 | 11 | 0.019401 | 0.014082 | 0.007002 | 0.377880 | 0.658986 | 0.043022 |
| 21 | combined | diffusion_iv | low | 217 | 11 | 0.024121 | 0.018444 | 0.009167 | 0.479263 | 0.686636 | 0.056232 |
| 21 | combined | empirical_exact | low | 217 | 11 | 0.024650 | 0.019695 | 0.009812 | 0.414747 | 0.714286 | 0.057502 |
| 21 | combined | rv_scaled | low | 217 | 11 | 0.027399 | 0.019794 | 0.009907 | 0.400922 | 0.668203 | 0.068957 |
| 21 | combined | iv_scaled | low | 217 | 11 | 0.027137 | 0.020449 | 0.010227 | 0.405530 | 0.700461 | 0.066274 |
| 21 | combined | state_iv | low | 217 | 11 | 0.027786 | 0.020739 | 0.010418 | 0.428571 | 0.677419 | 0.068665 |
| 21 | combined | separate_range_ridge | low | 217 | 11 | 0.028895 | 0.022607 | 0.011278 | 0.281106 | 0.539171 | 0.048451 |
| 21 | combined | diffusion_iv | range | 217 | 11 | 0.022336 | 0.016275 | 0.008039 | 0.313364 | 0.599078 | 0.045217 |
| 21 | combined | iv_scaled | range | 217 | 11 | 0.024620 | 0.018162 | 0.008980 | 0.341014 | 0.695853 | 0.055644 |
| 21 | combined | rv_scaled | range | 217 | 11 | 0.026264 | 0.018419 | 0.009041 | 0.299539 | 0.585253 | 0.064755 |
| 21 | combined | state_iv | range | 217 | 11 | 0.025364 | 0.018534 | 0.009225 | 0.359447 | 0.649770 | 0.057972 |
| 21 | combined | empirical_exact | range | 217 | 11 | 0.023677 | 0.019522 | 0.009963 | 0.502304 | 0.617512 | 0.058296 |
| 21 | combined | separate_range_ridge | range | 217 | 11 | 0.027376 | 0.021603 | 0.010850 | 0.322581 | 0.460829 | 0.044909 |

[Monthly probabilities and paths](distribution-and-path-leaderboard.csv) · [Monthly results by event](events-risk-and-path.csv).
