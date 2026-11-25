# V13 Future Range Forecasting

Maximum relative high and minimum relative low use the realized daily highs and lows after the reference close. Their difference is the reference-normalized range. Close-only excursions use future closes. Peak-to-trough drawdown and rebound are measured on ordered closes, keeping their definition independent of an unknown same-bar order. Separate labels cover overnight and regular-session variance, positive-day count, largest one-session log return magnitude, and terminal return magnitude. Empirical, volatility-scaled, state-conditioned and diffusion paths compete against standalone regularized residual range distributions.

| horizon | cohort | model | target | n | disjoint | mae | crps | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | diffusion_iv | abs_return | 265 | 53 | 0.009334 | 0.006405 | 0.003157 | 0.524528 | 0.822642 | 0.028000 |
| 5 | combined | state_iv | abs_return | 265 | 53 | 0.009450 | 0.006548 | 0.003226 | 0.490566 | 0.792453 | 0.026164 |
| 5 | combined | iv_scaled | abs_return | 265 | 53 | 0.009464 | 0.006563 | 0.003227 | 0.483019 | 0.784906 | 0.026085 |
| 5 | combined | empirical_exact | abs_return | 265 | 53 | 0.009873 | 0.007092 | 0.003513 | 0.456604 | 0.769811 | 0.024683 |
| 5 | combined | rv_scaled | abs_return | 265 | 53 | 0.009881 | 0.006801 | 0.003339 | 0.486792 | 0.777358 | 0.028694 |
| 5 | combined | diffusion_iv | drawdown | 265 | 53 | 0.008608 | 0.005899 | 0.002875 | 0.422642 | 0.769811 | 0.024957 |
| 5 | combined | iv_scaled | drawdown | 265 | 53 | 0.008891 | 0.006170 | 0.003000 | 0.471698 | 0.754717 | 0.025641 |
| 5 | combined | empirical_exact | drawdown | 265 | 53 | 0.008965 | 0.006540 | 0.003246 | 0.494340 | 0.750943 | 0.024845 |
| 5 | combined | state_iv | drawdown | 265 | 53 | 0.009060 | 0.006299 | 0.003064 | 0.449057 | 0.762264 | 0.026423 |
| 5 | combined | rv_scaled | drawdown | 265 | 53 | 0.009287 | 0.006446 | 0.003151 | 0.467925 | 0.758491 | 0.028354 |
| 5 | combined | iv_scaled | high | 265 | 53 | 0.009702 | 0.007131 | 0.003544 | 0.509434 | 0.739623 | 0.027384 |
| 5 | combined | state_iv | high | 265 | 53 | 0.009710 | 0.007149 | 0.003556 | 0.520755 | 0.743396 | 0.027568 |
| 5 | combined | diffusion_iv | high | 265 | 53 | 0.009913 | 0.006936 | 0.003435 | 0.501887 | 0.735849 | 0.028806 |
| 5 | combined | separate_range_ridge | high | 265 | 53 | 0.009919 | 0.007418 | 0.003695 | 0.486792 | 0.709434 | 0.023015 |
| 5 | combined | rv_scaled | high | 265 | 53 | 0.010350 | 0.007393 | 0.003681 | 0.505660 | 0.739623 | 0.028592 |
| 5 | combined | empirical_exact | high | 265 | 53 | 0.010556 | 0.007726 | 0.003834 | 0.494340 | 0.716981 | 0.025733 |
| 5 | combined | diffusion_iv | low | 265 | 53 | 0.009997 | 0.007125 | 0.003511 | 0.490566 | 0.762264 | 0.027827 |
| 5 | combined | empirical_exact | low | 265 | 53 | 0.010132 | 0.007608 | 0.003770 | 0.528302 | 0.747170 | 0.027814 |
| 5 | combined | iv_scaled | low | 265 | 53 | 0.010301 | 0.007327 | 0.003631 | 0.486792 | 0.758491 | 0.030995 |
| 5 | combined | state_iv | low | 265 | 53 | 0.010508 | 0.007418 | 0.003675 | 0.494340 | 0.769811 | 0.031501 |
| 5 | combined | separate_range_ridge | low | 265 | 53 | 0.010636 | 0.007950 | 0.003946 | 0.460377 | 0.686792 | 0.026824 |
| 5 | combined | rv_scaled | low | 265 | 53 | 0.010694 | 0.007598 | 0.003779 | 0.475472 | 0.762264 | 0.034226 |
| 5 | combined | diffusion_iv | range | 265 | 53 | 0.008182 | 0.005793 | 0.002864 | 0.449057 | 0.716981 | 0.021638 |
| 5 | combined | iv_scaled | range | 265 | 53 | 0.008191 | 0.005961 | 0.002951 | 0.464151 | 0.766038 | 0.022660 |
| 5 | combined | state_iv | range | 265 | 53 | 0.008267 | 0.006000 | 0.002967 | 0.456604 | 0.750943 | 0.022719 |
| 5 | combined | separate_range_ridge | range | 265 | 53 | 0.008774 | 0.006540 | 0.003267 | 0.426415 | 0.709434 | 0.020278 |
| 5 | combined | rv_scaled | range | 265 | 53 | 0.009824 | 0.006910 | 0.003411 | 0.452830 | 0.743396 | 0.027269 |
| 5 | combined | empirical_exact | range | 265 | 53 | 0.010385 | 0.007918 | 0.003972 | 0.464151 | 0.747170 | 0.027029 |
| 21 | combined | rv_scaled | abs_return | 217 | 11 | 0.022306 | 0.016303 | 0.008068 | 0.400922 | 0.691244 | 0.053947 |
| 21 | combined | empirical_exact | abs_return | 217 | 11 | 0.022307 | 0.017260 | 0.008585 | 0.405530 | 0.682028 | 0.047341 |
| 21 | combined | iv_scaled | abs_return | 217 | 11 | 0.022767 | 0.017290 | 0.008549 | 0.364055 | 0.714286 | 0.053119 |
| 21 | combined | diffusion_iv | abs_return | 217 | 11 | 0.023434 | 0.016843 | 0.008351 | 0.428571 | 0.700461 | 0.058036 |
| 21 | combined | state_iv | abs_return | 217 | 11 | 0.023643 | 0.017791 | 0.008886 | 0.373272 | 0.658986 | 0.054734 |
| 21 | combined | empirical_exact | drawdown | 217 | 11 | 0.019789 | 0.016452 | 0.008255 | 0.465438 | 0.714286 | 0.042709 |
| 21 | combined | diffusion_iv | drawdown | 217 | 11 | 0.020242 | 0.014985 | 0.007476 | 0.474654 | 0.682028 | 0.046982 |
| 21 | combined | iv_scaled | drawdown | 217 | 11 | 0.022961 | 0.016754 | 0.008390 | 0.460829 | 0.686636 | 0.050562 |
| 21 | combined | rv_scaled | drawdown | 217 | 11 | 0.023597 | 0.016094 | 0.008151 | 0.373272 | 0.682028 | 0.055226 |
| 21 | combined | state_iv | drawdown | 217 | 11 | 0.023667 | 0.017018 | 0.008553 | 0.447005 | 0.672811 | 0.053713 |
| 21 | combined | state_iv | high | 217 | 11 | 0.016974 | 0.012347 | 0.006102 | 0.419355 | 0.705069 | 0.044298 |
| 21 | combined | iv_scaled | high | 217 | 11 | 0.017124 | 0.012385 | 0.006116 | 0.414747 | 0.732719 | 0.044989 |
| 21 | combined | separate_range_ridge | high | 217 | 11 | 0.018427 | 0.013877 | 0.006891 | 0.410138 | 0.640553 | 0.039639 |
| 21 | combined | diffusion_iv | high | 217 | 11 | 0.018442 | 0.012447 | 0.006164 | 0.552995 | 0.797235 | 0.060312 |
| 21 | combined | empirical_exact | high | 217 | 11 | 0.019401 | 0.014082 | 0.007002 | 0.377880 | 0.658986 | 0.043022 |
| 21 | combined | rv_scaled | high | 217 | 11 | 0.019623 | 0.013551 | 0.006661 | 0.396313 | 0.705069 | 0.051689 |
| 21 | combined | diffusion_iv | low | 217 | 11 | 0.024121 | 0.018444 | 0.009167 | 0.479263 | 0.686636 | 0.056232 |
| 21 | combined | empirical_exact | low | 217 | 11 | 0.024650 | 0.019695 | 0.009812 | 0.414747 | 0.714286 | 0.057502 |
| 21 | combined | iv_scaled | low | 217 | 11 | 0.027137 | 0.020449 | 0.010227 | 0.405530 | 0.700461 | 0.066274 |
| 21 | combined | rv_scaled | low | 217 | 11 | 0.027399 | 0.019794 | 0.009907 | 0.400922 | 0.668203 | 0.068957 |
| 21 | combined | state_iv | low | 217 | 11 | 0.027786 | 0.020739 | 0.010418 | 0.428571 | 0.677419 | 0.068665 |
| 21 | combined | separate_range_ridge | low | 217 | 11 | 0.028895 | 0.022607 | 0.011278 | 0.281106 | 0.539171 | 0.048451 |
| 21 | combined | diffusion_iv | range | 217 | 11 | 0.022336 | 0.016275 | 0.008039 | 0.313364 | 0.599078 | 0.045217 |
| 21 | combined | empirical_exact | range | 217 | 11 | 0.023677 | 0.019522 | 0.009963 | 0.502304 | 0.617512 | 0.058296 |
| 21 | combined | iv_scaled | range | 217 | 11 | 0.024620 | 0.018162 | 0.008980 | 0.341014 | 0.695853 | 0.055644 |
| 21 | combined | state_iv | range | 217 | 11 | 0.025364 | 0.018534 | 0.009225 | 0.359447 | 0.649770 | 0.057972 |
| 21 | combined | rv_scaled | range | 217 | 11 | 0.026264 | 0.018419 | 0.009041 | 0.299539 | 0.585253 | 0.064755 |
| 21 | combined | separate_range_ridge | range | 217 | 11 | 0.027376 | 0.021603 | 0.010850 | 0.322581 | 0.460829 | 0.044909 |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | diffusion_iv | empirical_exact | high | crps | 265 | 53 | 0.006936 | 0.007726 | 0.000790 | -0.000932 | 0.002511 | -0.000909 | 0.002488 |
| 5 | combined | iv_scaled | empirical_exact | high | crps | 265 | 53 | 0.007131 | 0.007726 | 0.000595 | -0.000659 | 0.001850 | -0.000657 | 0.001847 |
| 5 | combined | state_iv | empirical_exact | high | crps | 265 | 53 | 0.007149 | 0.007726 | 0.000577 | -0.000599 | 0.001754 | -0.000601 | 0.001756 |
| 5 | combined | diffusion_iv | rv_scaled | high | crps | 265 | 53 | 0.006936 | 0.007393 | 0.000457 | -0.000493 | 0.001408 | -0.000586 | 0.001500 |
| 5 | combined | separate_range_ridge | empirical_exact | high | crps | 265 | 53 | 0.007418 | 0.007726 | 0.000308 | -0.000736 | 0.001351 | -0.000834 | 0.001450 |
| 5 | combined | iv_scaled | rv_scaled | high | crps | 265 | 53 | 0.007131 | 0.007393 | 0.000263 | -0.000456 | 0.000982 | -0.000588 | 0.001113 |
| 5 | combined | state_iv | rv_scaled | high | crps | 265 | 53 | 0.007149 | 0.007393 | 0.000245 | -0.000460 | 0.000950 | -0.000578 | 0.001068 |
| 5 | combined | separate_range_ridge | rv_scaled | high | crps | 265 | 53 | 0.007418 | 0.007393 | -0.000025 | -0.001036 | 0.000986 | -0.001174 | 0.001124 |
| 5 | combined | iv_scaled | empirical_exact | high | mae | 265 | 53 | 0.009702 | 0.010556 | 0.000853 | -0.000661 | 0.002368 | -0.000676 | 0.002382 |
| 5 | combined | state_iv | empirical_exact | high | mae | 265 | 53 | 0.009710 | 0.010556 | 0.000845 | -0.000638 | 0.002329 | -0.000678 | 0.002369 |
| 5 | combined | iv_scaled | rv_scaled | high | mae | 265 | 53 | 0.009702 | 0.010350 | 0.000648 | -0.000556 | 0.001852 | -0.000771 | 0.002068 |
| 5 | combined | diffusion_iv | empirical_exact | high | mae | 265 | 53 | 0.009913 | 0.010556 | 0.000642 | -0.001323 | 0.002608 | -0.001220 | 0.002504 |
| 5 | combined | state_iv | rv_scaled | high | mae | 265 | 53 | 0.009710 | 0.010350 | 0.000640 | -0.000655 | 0.001935 | -0.000867 | 0.002148 |
| 5 | combined | separate_range_ridge | empirical_exact | high | mae | 265 | 53 | 0.009919 | 0.010556 | 0.000636 | -0.000838 | 0.002111 | -0.000998 | 0.002270 |
| 5 | combined | diffusion_iv | rv_scaled | high | mae | 265 | 53 | 0.009913 | 0.010350 | 0.000437 | -0.001016 | 0.001891 | -0.001228 | 0.002102 |
| 5 | combined | separate_range_ridge | rv_scaled | high | mae | 265 | 53 | 0.009919 | 0.010350 | 0.000431 | -0.000773 | 0.001635 | -0.000910 | 0.001773 |
| 5 | combined | diffusion_iv | empirical_exact | low | crps | 265 | 53 | 0.007125 | 0.007608 | 0.000484 | -0.001274 | 0.002241 | -0.001600 | 0.002568 |
| 5 | combined | diffusion_iv | rv_scaled | low | crps | 265 | 53 | 0.007125 | 0.007598 | 0.000473 | -0.000408 | 0.001354 | -0.000303 | 0.001249 |
| 5 | combined | iv_scaled | empirical_exact | low | crps | 265 | 53 | 0.007327 | 0.007608 | 0.000281 | -0.001314 | 0.001876 | -0.001600 | 0.002163 |
| 5 | combined | iv_scaled | rv_scaled | low | crps | 265 | 53 | 0.007327 | 0.007598 | 0.000271 | -0.000422 | 0.000963 | -0.000354 | 0.000896 |
| 5 | combined | state_iv | empirical_exact | low | crps | 265 | 53 | 0.007418 | 0.007608 | 0.000191 | -0.001366 | 0.001747 | -0.001623 | 0.002005 |
| 5 | combined | state_iv | rv_scaled | low | crps | 265 | 53 | 0.007418 | 0.007598 | 0.000180 | -0.000543 | 0.000903 | -0.000468 | 0.000828 |
| 5 | combined | separate_range_ridge | empirical_exact | low | crps | 265 | 53 | 0.007950 | 0.007608 | -0.000342 | -0.001896 | 0.001212 | -0.001908 | 0.001225 |
| 5 | combined | separate_range_ridge | rv_scaled | low | crps | 265 | 53 | 0.007950 | 0.007598 | -0.000352 | -0.001798 | 0.001094 | -0.002060 | 0.001356 |
| 5 | combined | diffusion_iv | rv_scaled | low | mae | 265 | 53 | 0.009997 | 0.010694 | 0.000697 | -0.000633 | 0.002027 | -0.000527 | 0.001921 |
| 5 | combined | iv_scaled | rv_scaled | low | mae | 265 | 53 | 0.010301 | 0.010694 | 0.000393 | -0.000665 | 0.001451 | -0.000635 | 0.001420 |
| 5 | combined | state_iv | rv_scaled | low | mae | 265 | 53 | 0.010508 | 0.010694 | 0.000186 | -0.000839 | 0.001211 | -0.000761 | 0.001133 |
| 5 | combined | diffusion_iv | empirical_exact | low | mae | 265 | 53 | 0.009997 | 0.010132 | 0.000135 | -0.001826 | 0.002097 | -0.002093 | 0.002364 |
| 5 | combined | separate_range_ridge | rv_scaled | low | mae | 265 | 53 | 0.010636 | 0.010694 | 0.000058 | -0.001445 | 0.001562 | -0.001625 | 0.001742 |
| 5 | combined | iv_scaled | empirical_exact | low | mae | 265 | 53 | 0.010301 | 0.010132 | -0.000169 | -0.001926 | 0.001588 | -0.002158 | 0.001820 |
| 5 | combined | state_iv | empirical_exact | low | mae | 265 | 53 | 0.010508 | 0.010132 | -0.000376 | -0.002164 | 0.001412 | -0.002365 | 0.001614 |
| 5 | combined | separate_range_ridge | empirical_exact | low | mae | 265 | 53 | 0.010636 | 0.010132 | -0.000503 | -0.002357 | 0.001350 | -0.002429 | 0.001422 |
| 5 | combined | diffusion_iv | empirical_exact | range | crps | 265 | 53 | 0.005793 | 0.007918 | 0.002126 | -0.001547 | 0.005799 | -0.002492 | 0.006743 |
| 5 | combined | iv_scaled | empirical_exact | range | crps | 265 | 53 | 0.005961 | 0.007918 | 0.001958 | -0.001348 | 0.005264 | -0.002168 | 0.006083 |
| 5 | combined | state_iv | empirical_exact | range | crps | 265 | 53 | 0.006000 | 0.007918 | 0.001918 | -0.001406 | 0.005242 | -0.002222 | 0.006058 |
| 5 | combined | separate_range_ridge | empirical_exact | range | crps | 265 | 53 | 0.006540 | 0.007918 | 0.001379 | -0.001276 | 0.004033 | -0.001757 | 0.004515 |
| 5 | combined | diffusion_iv | rv_scaled | range | crps | 265 | 53 | 0.005793 | 0.006910 | 0.001117 | -0.000478 | 0.002712 | -0.000821 | 0.003054 |
| 5 | combined | iv_scaled | rv_scaled | range | crps | 265 | 53 | 0.005961 | 0.006910 | 0.000949 | -0.000612 | 0.002510 | -0.000787 | 0.002685 |
| 5 | combined | state_iv | rv_scaled | range | crps | 265 | 53 | 0.006000 | 0.006910 | 0.000910 | -0.000564 | 0.002383 | -0.000731 | 0.002550 |
| 5 | combined | separate_range_ridge | rv_scaled | range | crps | 265 | 53 | 0.006540 | 0.006910 | 0.000370 | -0.000867 | 0.001607 | -0.000953 | 0.001694 |
| 5 | combined | diffusion_iv | empirical_exact | range | mae | 265 | 53 | 0.008182 | 0.010385 | 0.002204 | -0.002150 | 0.006557 | -0.003235 | 0.007642 |
| 5 | combined | iv_scaled | empirical_exact | range | mae | 265 | 53 | 0.008191 | 0.010385 | 0.002195 | -0.001895 | 0.006284 | -0.002892 | 0.007281 |
| 5 | combined | state_iv | empirical_exact | range | mae | 265 | 53 | 0.008267 | 0.010385 | 0.002118 | -0.001991 | 0.006228 | -0.002987 | 0.007224 |
| 5 | combined | diffusion_iv | rv_scaled | range | mae | 265 | 53 | 0.008182 | 0.009824 | 0.001643 | -0.000889 | 0.004175 | -0.001504 | 0.004789 |
| 5 | combined | iv_scaled | rv_scaled | range | mae | 265 | 53 | 0.008191 | 0.009824 | 0.001634 | -0.000939 | 0.004206 | -0.001386 | 0.004653 |
| 5 | combined | separate_range_ridge | empirical_exact | range | mae | 265 | 53 | 0.008774 | 0.010385 | 0.001611 | -0.001789 | 0.005011 | -0.002397 | 0.005620 |
| 5 | combined | state_iv | rv_scaled | range | mae | 265 | 53 | 0.008267 | 0.009824 | 0.001557 | -0.000929 | 0.004043 | -0.001355 | 0.004469 |
| 5 | combined | separate_range_ridge | rv_scaled | range | mae | 265 | 53 | 0.008774 | 0.009824 | 0.001051 | -0.000976 | 0.003077 | -0.001201 | 0.003302 |
| 21 | combined | state_iv | empirical_exact | high | crps | 217 | 11 | 0.012347 | 0.014082 | 0.001735 | -0.002162 | 0.005632 | -0.002188 | 0.005658 |
| 21 | combined | iv_scaled | empirical_exact | high | crps | 217 | 11 | 0.012385 | 0.014082 | 0.001697 | -0.002258 | 0.005652 | -0.002301 | 0.005694 |
| 21 | combined | diffusion_iv | empirical_exact | high | crps | 217 | 11 | 0.012447 | 0.014082 | 0.001635 | -0.003344 | 0.006613 | -0.003432 | 0.006701 |
| 21 | combined | state_iv | rv_scaled | high | crps | 217 | 11 | 0.012347 | 0.013551 | 0.001204 | -0.001272 | 0.003681 | -0.001840 | 0.004249 |
| 21 | combined | iv_scaled | rv_scaled | high | crps | 217 | 11 | 0.012385 | 0.013551 | 0.001166 | -0.001203 | 0.003535 | -0.001785 | 0.004117 |
| 21 | combined | diffusion_iv | rv_scaled | high | crps | 217 | 11 | 0.012447 | 0.013551 | 0.001104 | -0.001491 | 0.003699 | -0.001790 | 0.003997 |
| 21 | combined | separate_range_ridge | empirical_exact | high | crps | 217 | 11 | 0.013877 | 0.014082 | 0.000205 | -0.003201 | 0.003611 | -0.003749 | 0.004159 |
| 21 | combined | separate_range_ridge | rv_scaled | high | crps | 217 | 11 | 0.013877 | 0.013551 | -0.000326 | -0.003576 | 0.002925 | -0.003792 | 0.003141 |
| 21 | combined | state_iv | rv_scaled | high | mae | 217 | 11 | 0.016974 | 0.019623 | 0.002648 | -0.001735 | 0.007031 | -0.002672 | 0.007969 |
| 21 | combined | iv_scaled | rv_scaled | high | mae | 217 | 11 | 0.017124 | 0.019623 | 0.002499 | -0.001571 | 0.006569 | -0.002511 | 0.007509 |
| 21 | combined | state_iv | empirical_exact | high | mae | 217 | 11 | 0.016974 | 0.019401 | 0.002427 | -0.002112 | 0.006965 | -0.002369 | 0.007223 |
| 21 | combined | iv_scaled | empirical_exact | high | mae | 217 | 11 | 0.017124 | 0.019401 | 0.002277 | -0.002438 | 0.006993 | -0.002793 | 0.007348 |
| 21 | combined | separate_range_ridge | rv_scaled | high | mae | 217 | 11 | 0.018427 | 0.019623 | 0.001196 | -0.003890 | 0.006281 | -0.004400 | 0.006792 |
| 21 | combined | diffusion_iv | rv_scaled | high | mae | 217 | 11 | 0.018442 | 0.019623 | 0.001180 | -0.003050 | 0.005411 | -0.003752 | 0.006113 |
| 21 | combined | separate_range_ridge | empirical_exact | high | mae | 217 | 11 | 0.018427 | 0.019401 | 0.000974 | -0.003273 | 0.005221 | -0.004097 | 0.006045 |
| 21 | combined | diffusion_iv | empirical_exact | high | mae | 217 | 11 | 0.018442 | 0.019401 | 0.000959 | -0.006291 | 0.008209 | -0.006786 | 0.008703 |
| 21 | combined | diffusion_iv | rv_scaled | low | crps | 217 | 11 | 0.018444 | 0.019794 | 0.001350 | -0.002401 | 0.005101 | -0.003117 | 0.005817 |
| 21 | combined | diffusion_iv | empirical_exact | low | crps | 217 | 11 | 0.018444 | 0.019695 | 0.001250 | -0.003423 | 0.005924 | -0.004358 | 0.006859 |
| 21 | combined | iv_scaled | rv_scaled | low | crps | 217 | 11 | 0.020449 | 0.019794 | -0.000655 | -0.004829 | 0.003519 | -0.005985 | 0.004675 |
| 21 | combined | iv_scaled | empirical_exact | low | crps | 217 | 11 | 0.020449 | 0.019695 | -0.000754 | -0.003755 | 0.002247 | -0.004035 | 0.002527 |
| 21 | combined | state_iv | rv_scaled | low | crps | 217 | 11 | 0.020739 | 0.019794 | -0.000945 | -0.005206 | 0.003316 | -0.006471 | 0.004581 |
| 21 | combined | state_iv | empirical_exact | low | crps | 217 | 11 | 0.020739 | 0.019695 | -0.001045 | -0.004006 | 0.001917 | -0.004347 | 0.002258 |
| 21 | combined | separate_range_ridge | rv_scaled | low | crps | 217 | 11 | 0.022607 | 0.019794 | -0.002813 | -0.009807 | 0.004181 | -0.012089 | 0.006463 |
| 21 | combined | separate_range_ridge | empirical_exact | low | crps | 217 | 11 | 0.022607 | 0.019695 | -0.002913 | -0.006422 | 0.000597 | -0.007152 | 0.001327 |
| 21 | combined | diffusion_iv | rv_scaled | low | mae | 217 | 11 | 0.024121 | 0.027399 | 0.003279 | -0.001165 | 0.007722 | -0.001633 | 0.008191 |
| 21 | combined | diffusion_iv | empirical_exact | low | mae | 217 | 11 | 0.024121 | 0.024650 | 0.000530 | -0.005699 | 0.006758 | -0.006643 | 0.007702 |
| 21 | combined | iv_scaled | rv_scaled | low | mae | 217 | 11 | 0.027137 | 0.027399 | 0.000262 | -0.004088 | 0.004612 | -0.004910 | 0.005434 |
| 21 | combined | state_iv | rv_scaled | low | mae | 217 | 11 | 0.027786 | 0.027399 | -0.000387 | -0.003948 | 0.003173 | -0.004746 | 0.003972 |
| 21 | combined | separate_range_ridge | rv_scaled | low | mae | 217 | 11 | 0.028895 | 0.027399 | -0.001496 | -0.008478 | 0.005486 | -0.009829 | 0.006837 |
| 21 | combined | iv_scaled | empirical_exact | low | mae | 217 | 11 | 0.027137 | 0.024650 | -0.002487 | -0.006892 | 0.001918 | -0.006912 | 0.001938 |
| 21 | combined | state_iv | empirical_exact | low | mae | 217 | 11 | 0.027786 | 0.024650 | -0.003136 | -0.008120 | 0.001848 | -0.008689 | 0.002417 |
| 21 | combined | separate_range_ridge | empirical_exact | low | mae | 217 | 11 | 0.028895 | 0.024650 | -0.004245 | -0.009979 | 0.001489 | -0.011204 | 0.002714 |
| 21 | combined | diffusion_iv | empirical_exact | range | crps | 217 | 11 | 0.016275 | 0.019522 | 0.003247 | -0.005369 | 0.011863 | -0.007400 | 0.013893 |
| 21 | combined | diffusion_iv | rv_scaled | range | crps | 217 | 11 | 0.016275 | 0.018419 | 0.002143 | -0.005575 | 0.009861 | -0.007089 | 0.011376 |
| 21 | combined | iv_scaled | empirical_exact | range | crps | 217 | 11 | 0.018162 | 0.019522 | 0.001360 | -0.005549 | 0.008269 | -0.006738 | 0.009458 |
| 21 | combined | state_iv | empirical_exact | range | crps | 217 | 11 | 0.018534 | 0.019522 | 0.000988 | -0.005744 | 0.007719 | -0.006838 | 0.008813 |
| 21 | combined | iv_scaled | rv_scaled | range | crps | 217 | 11 | 0.018162 | 0.018419 | 0.000257 | -0.007842 | 0.008355 | -0.010155 | 0.010669 |
| 21 | combined | state_iv | rv_scaled | range | crps | 217 | 11 | 0.018534 | 0.018419 | -0.000116 | -0.008293 | 0.008061 | -0.010657 | 0.010426 |
| 21 | combined | separate_range_ridge | empirical_exact | range | crps | 217 | 11 | 0.021603 | 0.019522 | -0.002081 | -0.007379 | 0.003217 | -0.008955 | 0.004792 |
| 21 | combined | separate_range_ridge | rv_scaled | range | crps | 217 | 11 | 0.021603 | 0.018419 | -0.003184 | -0.012166 | 0.005797 | -0.014121 | 0.007752 |
| 21 | combined | diffusion_iv | rv_scaled | range | mae | 217 | 11 | 0.022336 | 0.026264 | 0.003928 | -0.004783 | 0.012639 | -0.006262 | 0.014118 |
| 21 | combined | iv_scaled | rv_scaled | range | mae | 217 | 11 | 0.024620 | 0.026264 | 0.001644 | -0.007328 | 0.010615 | -0.009646 | 0.012934 |
| 21 | combined | diffusion_iv | empirical_exact | range | mae | 217 | 11 | 0.022336 | 0.023677 | 0.001341 | -0.010616 | 0.013299 | -0.013638 | 0.016320 |
| 21 | combined | state_iv | rv_scaled | range | mae | 217 | 11 | 0.025364 | 0.026264 | 0.000900 | -0.007455 | 0.009255 | -0.009696 | 0.011495 |
| 21 | combined | iv_scaled | empirical_exact | range | mae | 217 | 11 | 0.024620 | 0.023677 | -0.000943 | -0.011750 | 0.009865 | -0.014027 | 0.012141 |
| 21 | combined | separate_range_ridge | rv_scaled | range | mae | 217 | 11 | 0.027376 | 0.026264 | -0.001113 | -0.012075 | 0.009850 | -0.014055 | 0.011829 |
| 21 | combined | state_iv | empirical_exact | range | mae | 217 | 11 | 0.025364 | 0.023677 | -0.001687 | -0.012844 | 0.009470 | -0.015175 | 0.011802 |
| 21 | combined | separate_range_ridge | empirical_exact | range | mae | 217 | 11 | 0.027376 | 0.023677 | -0.003699 | -0.012338 | 0.004940 | -0.015099 | 0.007701 |

[Five-session labels](targets-5.csv) · [21-session labels](targets-21.csv) · [All origin forecasts](distribution-predictions.csv).
