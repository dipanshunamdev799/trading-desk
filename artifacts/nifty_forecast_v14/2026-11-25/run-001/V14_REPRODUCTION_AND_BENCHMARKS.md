# V14 Reproduction And Benchmarks

Continuing the exact frozen 2025–2026 study, with H actual trading sessions following the cash reference. Close-to-close risk is the square root of 252 times future mean squared daily log returns. The V13 options series uses calendar maturity and recorded lagged alignment. Variance QLIKE uses the realized-to-forecast annualized **variance** ratio.

Recomputed **3,374** V13 volatility forecasts, **1,928** range distributions, **19,280** fixed touch comparisons and **3,448** endpoint score rows. Volatility point replay error was at most **0**. Float32 V13 range atoms account for the maximum **6.6e-10** score discrepancy. Verified **22,672** protected predecessor hashes.

| horizon | model | n | disjoint | mae | qlike | bias |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | egarch | 265 | 53 | 0.039975 | 0.361354 | 0.003677 |
| 5 | fixed_iv_rv_0.75 | 265 | 53 | 0.038196 | 0.273634 | 0.006907 |
| 5 | gjr | 265 | 53 | 0.040318 | 0.359870 | 0.002871 |
| 5 | iv_bracket | 265 | 53 | 0.038336 | 0.277849 | 0.008045 |
| 5 | iv_calibrated | 265 | 53 | 0.037517 | 0.338910 | -0.010390 |
| 5 | iv_nearest | 265 | 53 | 0.037814 | 0.276187 | 0.007769 |
| 5 | prior_trailing | 265 | 53 | 0.046394 | 0.418006 | 0.001389 |
| 21 | egarch | 217 | 11 | 0.034943 | 0.302016 | -0.010128 |
| 21 | fixed_iv_rv_0.75 | 217 | 11 | 0.040894 | 0.257953 | -0.004632 |
| 21 | gjr | 217 | 11 | 0.033179 | 0.199677 | -0.009266 |
| 21 | iv_bracket | 217 | 11 | 0.039406 | 0.267623 | -0.004405 |
| 21 | iv_calibrated | 217 | 11 | 0.040652 | 0.586417 | -0.030326 |
| 21 | iv_nearest | 217 | 11 | 0.039639 | 0.266465 | -0.003579 |
| 21 | prior_trailing | 217 | 11 | 0.048044 | 0.487043 | -0.008108 |

| horizon | model | n | crps | mae | cov80 | width80 |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V13_diffusion_iv | 265 | 0.005793 | 0.008182 | 0.716981 | 0.021638 |
| 5 | V13_empirical_exact | 265 | 0.007918 | 0.010385 | 0.747170 | 0.027029 |
| 5 | V13_iv_scaled | 265 | 0.005961 | 0.008191 | 0.766038 | 0.022660 |
| 5 | V13_rv_scaled | 265 | 0.006910 | 0.009824 | 0.743396 | 0.027269 |
| 21 | V13_diffusion_iv | 217 | 0.016275 | 0.022336 | 0.599078 | 0.045217 |
| 21 | V13_empirical_exact | 217 | 0.019522 | 0.023677 | 0.617512 | 0.058296 |
| 21 | V13_iv_scaled | 217 | 0.018162 | 0.024620 | 0.695853 | 0.055644 |
| 21 | V13_rv_scaled | 217 | 0.018419 | 0.026264 | 0.585253 | 0.064755 |

| horizon | model | size | mean |
| --- | --- | --- | --- |
| 5 | analytic_iv_diffusion | 265 | 0.145264 |
| 5 | diffusion_iv | 265 | 0.144154 |
| 5 | empirical_exact | 265 | 0.156019 |
| 5 | iv_scaled | 265 | 0.147679 |
| 21 | analytic_iv_diffusion | 217 | 0.184067 |
| 21 | diffusion_iv | 217 | 0.185037 |
| 21 | empirical_exact | 217 | 0.206812 |
| 21 | iv_scaled | 217 | 0.197163 |

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | B_CHANGE | 265 | 53 | 0.246747 | 0.696972 | 0.596226 | 0.610765 | 0.011869 | 0.016103 | 0.758491 | 0.042534 |
| 5 | later | B_CHANGE | 92 | 19 | 0.156795 | 0.493055 | 0.771739 | 0.774794 | 0.009851 | 0.012852 | 0.771739 | 0.035836 |
| 5 | combined | J12_GROUP_BALANCED__scale_only | 265 | 53 | 0.236495 | 0.665957 | 0.630189 | 0.644751 | 0.010472 | 0.014903 | 0.788679 | 0.043399 |
| 5 | later | J12_GROUP_BALANCED__scale_only | 92 | 19 | 0.205959 | 0.603052 | 0.771739 | 0.781567 | 0.010593 | 0.014321 | 0.760870 | 0.038954 |
| 5 | combined | J12_Q_GROUP | 265 | 53 | 0.241437 | 0.676126 | 0.622642 | 0.637994 | 0.010677 | 0.014897 | 0.803774 | 0.043636 |
| 5 | later | J12_Q_GROUP | 92 | 19 | 0.212198 | 0.616417 | 0.782609 | 0.791001 | 0.010666 | 0.014379 | 0.771739 | 0.040289 |
| 5 | combined | NEUTRAL | 265 | 53 | 0.250000 | 0.693147 | 0.528302 | 0.488190 | 0.011058 | 0.015052 | 0.735849 | 0.039228 |
| 5 | later | NEUTRAL | 92 | 19 | 0.250000 | 0.693147 | 0.576087 | 0.500000 | 0.011996 | 0.016249 | 0.750000 | 0.043017 |
| 5 | combined | NEUTRAL__scale_only | 265 | 53 | 0.250000 | 0.693147 | 0.441509 | 0.500000 | 0.010817 | 0.015052 | 0.732075 | 0.040086 |
| 5 | later | NEUTRAL__scale_only | 92 | 19 | 0.250000 | 0.693147 | 0.423913 | 0.500000 | 0.011905 | 0.016249 | 0.706522 | 0.039882 |
| 5 | combined | PH_NATIVE_PHASE_MIXTURE__scale_only | 265 | 53 | 0.229587 | 0.651757 | 0.626415 | 0.636001 | 0.010609 | 0.015013 | 0.807547 | 0.044748 |
| 5 | later | PH_NATIVE_PHASE_MIXTURE__scale_only | 92 | 19 | 0.189445 | 0.564961 | 0.750000 | 0.759313 | 0.010473 | 0.013815 | 0.760870 | 0.039558 |
| 5 | combined | V12_NATIVE_RV | 265 | 53 | 0.229715 | 0.655524 | 0.626415 | 0.633316 | 0.010896 | 0.014687 | 0.781132 | 0.041415 |
| 5 | later | V12_NATIVE_RV | 92 | 19 | 0.220177 | 0.629600 | 0.641304 | 0.658200 | 0.012153 | 0.015863 | 0.717391 | 0.038620 |
| 5 | combined | V8_W_STRUCT_EMBARGO_EQ | 92 | 19 | 0.161638 | 0.501592 | 0.771739 | 0.781567 | 0.009262 | 0.012228 | 0.804348 | 0.039726 |
| 5 | later | V8_W_STRUCT_EMBARGO_EQ | 92 | 19 | 0.161638 | 0.501592 | 0.771739 | 0.781567 | 0.009262 | 0.012228 | 0.804348 | 0.039726 |
| 21 | combined | B_CHANGE | 217 | 11 | 0.332742 | 0.939315 | 0.493088 | 0.516566 | 0.032497 | 0.041961 | 0.488479 | 0.074518 |
| 21 | later | B_CHANGE | 76 | 4 | 0.297966 | 0.805137 | 0.473684 | 0.495341 | 0.031766 | 0.038738 | 0.473684 | 0.061187 |
| 21 | combined | J12_GROUP_BALANCED__scale_only | 217 | 11 | 0.288318 | 0.779408 | 0.488479 | 0.526445 | 0.027282 | 0.036491 | 0.658986 | 0.087833 |
| 21 | later | J12_GROUP_BALANCED__scale_only | 76 | 4 | 0.274618 | 0.744305 | 0.447368 | 0.528315 | 0.028201 | 0.036674 | 0.539474 | 0.074777 |
| 21 | combined | J12_Q_GROUP | 199 | 11 | 0.300552 | 0.811255 | 0.487437 | 0.529224 | 0.028081 | 0.036410 | 0.648241 | 0.085699 |
| 21 | later | J12_Q_GROUP | 71 | 4 | 0.270974 | 0.736506 | 0.478873 | 0.548780 | 0.028599 | 0.037009 | 0.577465 | 0.077463 |
| 21 | combined | NEUTRAL | 217 | 11 | 0.250000 | 0.693147 | 0.511521 | 0.460742 | 0.025420 | 0.033371 | 0.635945 | 0.068179 |
| 21 | later | NEUTRAL | 76 | 4 | 0.250000 | 0.693147 | 0.592105 | 0.500000 | 0.027460 | 0.037221 | 0.618421 | 0.075268 |
| 21 | combined | NEUTRAL__scale_only | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025220 | 0.033371 | 0.672811 | 0.077357 |
| 21 | later | NEUTRAL__scale_only | 76 | 4 | 0.250000 | 0.693147 | 0.407895 | 0.500000 | 0.027821 | 0.037221 | 0.565789 | 0.071797 |
| 21 | combined | PH_NATIVE_PHASE_MIXTURE__scale_only | 217 | 11 | 0.284302 | 0.774921 | 0.470046 | 0.499569 | 0.028227 | 0.038703 | 0.635945 | 0.092555 |
| 21 | later | PH_NATIVE_PHASE_MIXTURE__scale_only | 76 | 4 | 0.268939 | 0.734032 | 0.447368 | 0.508244 | 0.028576 | 0.037411 | 0.539474 | 0.080052 |
| 21 | combined | V12_NATIVE_RV | 217 | 11 | 0.363025 | 0.974514 | 0.345622 | 0.349310 | 0.032602 | 0.042037 | 0.529954 | 0.074254 |
| 21 | later | V12_NATIVE_RV | 76 | 4 | 0.353661 | 0.917664 | 0.250000 | 0.226165 | 0.033785 | 0.043926 | 0.394737 | 0.061954 |

The QLIKE decomposition conditions on actual annualized volatility relative to raw ATM IV. Strong underprediction produces large variance ratios and disproportionately high loss. The extreme-ratio bucket below explains where the weekly MAE/QLIKE trade-off came from.

| model | bucket | n | mean_actual | mean_forecast | mae | qlike | mean_error | total_qlike |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_iv_rv_0.75 | 100-135% of IV | 68 | 0.162032 | 0.139386 | 0.023156 | 0.070439 | -0.022647 | 4.789865 |
| fixed_iv_rv_0.75 | 65-100% of IV | 107 | 0.102725 | 0.124972 | 0.022734 | 0.099015 | 0.022247 | 10.594628 |
| fixed_iv_rv_0.75 | actual <= 65% of IV | 55 | 0.069549 | 0.134137 | 0.064588 | 0.652084 | 0.064588 | 35.864619 |
| fixed_iv_rv_0.75 | actual > 135% of IV | 35 | 0.200575 | 0.127364 | 0.073211 | 0.607537 | -0.073211 | 21.263788 |
| iv_calibrated | 100-135% of IV | 68 | 0.162032 | 0.121010 | 0.041022 | 0.259749 | -0.041022 | 17.662908 |
| iv_calibrated | 65-100% of IV | 107 | 0.102725 | 0.108031 | 0.012574 | 0.040590 | 0.005306 | 4.343113 |
| iv_calibrated | actual <= 65% of IV | 55 | 0.069549 | 0.117508 | 0.047959 | 0.471677 | 0.047959 | 25.942231 |
| iv_calibrated | actual > 135% of IV | 35 | 0.200575 | 0.110022 | 0.090553 | 1.196085 | -0.090553 | 41.862967 |
| iv_nearest | 100-135% of IV | 68 | 0.162032 | 0.141341 | 0.020692 | 0.060063 | -0.020692 | 4.084280 |
| iv_nearest | 65-100% of IV | 107 | 0.102725 | 0.125776 | 0.023050 | 0.099846 | 0.023050 | 10.683549 |
| iv_nearest | actual <= 65% of IV | 55 | 0.069549 | 0.134521 | 0.064973 | 0.661186 | 0.064973 | 36.365204 |
| iv_nearest | actual > 135% of IV | 35 | 0.200575 | 0.127034 | 0.073541 | 0.630187 | -0.073541 | 22.056530 |

[Exact replay](reproduction.json) · [V13 study](../../../nifty_forecast_v13/2026-11-25/run-001/NIFTY_V13_RESEARCH.md).
