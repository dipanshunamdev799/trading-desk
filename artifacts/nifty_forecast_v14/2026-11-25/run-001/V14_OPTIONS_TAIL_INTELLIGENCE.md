# V14 Options Tail Intelligence

Option additions cover constant-tenor up and down IV, skew acceleration, curvature, tail probabilities, quantile spreads, term transitions, unsigned concentration and traded volume. Trained physical-event regressions use those measures as predictors. The reconstructed risk-neutral probabilities remain in their own columns. Liquidity, truncation, delayed actual chains and shifted or block-permuted inputs compete with the raw ATM and the simple historical controls.

| horizon | cohort | event | model | n | disjoint | brier | log_loss | p | actual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | upper_relative | iv_scaled_blocks | 265 | 53 | 0.113777 | 0.379308 | 0.146844 | 0.132075 |
| 5 | combined | lower_relative | iv_scaled_blocks | 265 | 53 | 0.117628 | 0.408537 | 0.103864 | 0.139623 |
| 5 | combined | range_relative | iv_scaled_blocks | 265 | 53 | 0.076391 | 0.258817 | 0.126386 | 0.169811 |
| 5 | combined | upper_relative | raw_iv_logistic | 265 | 53 | 0.116679 | 0.416380 | 0.056325 | 0.132075 |
| 5 | combined | lower_relative | raw_iv_logistic | 265 | 53 | 0.141244 | 0.483675 | 0.167907 | 0.139623 |
| 5 | combined | range_relative | raw_iv_logistic | 265 | 53 | 0.142212 | 0.541059 | 0.157606 | 0.169811 |
| 5 | combined | upper_relative | surface | 265 | 53 | 0.121966 | 0.480785 | 0.050160 | 0.132075 |
| 5 | combined | lower_relative | surface | 265 | 53 | 0.167526 | 0.623910 | 0.168651 | 0.139623 |
| 5 | combined | range_relative | surface | 265 | 53 | 0.157203 | 0.638751 | 0.183249 | 0.169811 |
| 5 | combined | upper_relative | surface_lag5 | 265 | 53 | 0.118794 | 0.434692 | 0.054500 | 0.132075 |
| 5 | combined | lower_relative | surface_lag5 | 265 | 53 | 0.161588 | 0.602463 | 0.175654 | 0.139623 |
| 5 | combined | range_relative | surface_lag5 | 265 | 53 | 0.176132 | 0.694461 | 0.179962 | 0.169811 |
| 5 | combined | upper_relative | surface_shift21 | 265 | 53 | 0.120484 | 0.485723 | 0.049253 | 0.132075 |
| 5 | combined | lower_relative | surface_shift21 | 265 | 53 | 0.165436 | 0.614173 | 0.167711 | 0.139623 |
| 5 | combined | range_relative | surface_shift21 | 265 | 53 | 0.168920 | 0.645209 | 0.178108 | 0.169811 |
| 5 | combined | upper_relative | surface_permuted | 265 | 53 | 0.122809 | 0.480953 | 0.065955 | 0.132075 |
| 5 | combined | lower_relative | surface_permuted | 265 | 53 | 0.160567 | 0.607828 | 0.164691 | 0.139623 |
| 5 | combined | range_relative | surface_permuted | 265 | 53 | 0.182705 | 0.645682 | 0.171320 | 0.169811 |
| 5 | combined | upper_relative | surface_liquid | 265 | 53 | 0.121938 | 0.449733 | 0.062865 | 0.132075 |
| 5 | combined | lower_relative | surface_liquid | 265 | 53 | 0.153681 | 0.588174 | 0.158954 | 0.139623 |
| 5 | combined | range_relative | surface_liquid | 265 | 53 | 0.141702 | 0.587397 | 0.179024 | 0.169811 |
| 5 | combined | upper_relative | surface_truncated | 265 | 53 | 0.121115 | 0.451438 | 0.060415 | 0.132075 |
| 5 | combined | lower_relative | surface_truncated | 265 | 53 | 0.153411 | 0.590343 | 0.159696 | 0.139623 |
| 5 | combined | range_relative | surface_truncated | 265 | 53 | 0.136579 | 0.557956 | 0.175602 | 0.169811 |
| 5 | combined | upper_relative | historical | 265 | 53 | 0.116943 | 0.420673 | 0.060713 | 0.132075 |
| 5 | combined | lower_relative | historical | 265 | 53 | 0.127029 | 0.430002 | 0.164090 | 0.139623 |
| 5 | combined | range_relative | historical | 265 | 53 | 0.168059 | 0.654726 | 0.124106 | 0.169811 |
| 5 | combined | upper_relative | iv_raw | 265 | 53 | 0.108191 | 0.357757 | 0.153029 | 0.132075 |
| 5 | combined | lower_relative | iv_raw | 265 | 53 | 0.112677 | 0.383767 | 0.137316 | 0.139623 |
| 5 | combined | upper_relative | gjr_control | 265 | 53 | 0.113039 | 0.384467 | 0.139199 | 0.132075 |
| 5 | combined | lower_relative | gjr_control | 265 | 53 | 0.112153 | 0.375200 | 0.126003 | 0.139623 |
| 21 | combined | upper_relative | iv_scaled_blocks | 217 | 11 | 0.118663 | 0.394494 | 0.114656 | 0.152074 |
| 21 | combined | lower_relative | iv_scaled_blocks | 217 | 11 | 0.189443 | 0.601938 | 0.131397 | 0.221198 |
| 21 | combined | range_relative | iv_scaled_blocks | 217 | 11 | 0.207973 | 0.654377 | 0.192000 | 0.350230 |
| 21 | combined | upper_relative | raw_iv_logistic | 217 | 11 | 0.136144 | 0.489335 | 0.066637 | 0.152074 |
| 21 | combined | lower_relative | raw_iv_logistic | 217 | 11 | 0.188872 | 0.560864 | 0.287502 | 0.221198 |
| 21 | combined | range_relative | raw_iv_logistic | 217 | 11 | 0.360772 | 1.030318 | 0.338143 | 0.350230 |
| 21 | combined | upper_relative | surface | 217 | 11 | 0.132905 | 0.510450 | 0.059410 | 0.152074 |
| 21 | combined | lower_relative | surface | 217 | 11 | 0.287110 | 1.162210 | 0.292600 | 0.221198 |
| 21 | combined | range_relative | surface | 217 | 11 | 0.408859 | 1.386032 | 0.338960 | 0.350230 |
| 21 | combined | upper_relative | surface_lag5 | 217 | 11 | 0.143781 | 0.652734 | 0.053850 | 0.152074 |
| 21 | combined | lower_relative | surface_lag5 | 217 | 11 | 0.265394 | 0.951943 | 0.319129 | 0.221198 |
| 21 | combined | range_relative | surface_lag5 | 217 | 11 | 0.407481 | 1.464915 | 0.311465 | 0.350230 |
| 21 | combined | upper_relative | surface_shift21 | 217 | 11 | 0.142665 | 0.571333 | 0.055827 | 0.152074 |
| 21 | combined | lower_relative | surface_shift21 | 217 | 11 | 0.357789 | 1.478428 | 0.358026 | 0.221198 |
| 21 | combined | range_relative | surface_shift21 | 217 | 11 | 0.331828 | 1.092044 | 0.261552 | 0.350230 |
| 21 | combined | upper_relative | surface_permuted | 217 | 11 | 0.161919 | 0.649261 | 0.074278 | 0.152074 |
| 21 | combined | lower_relative | surface_permuted | 217 | 11 | 0.225712 | 0.673149 | 0.307339 | 0.221198 |
| 21 | combined | range_relative | surface_permuted | 217 | 11 | 0.386279 | 1.229828 | 0.320644 | 0.350230 |
| 21 | combined | upper_relative | surface_liquid | 217 | 11 | 0.142034 | 0.567865 | 0.056767 | 0.152074 |
| 21 | combined | lower_relative | surface_liquid | 217 | 11 | 0.274842 | 0.934237 | 0.308736 | 0.221198 |
| 21 | combined | range_relative | surface_liquid | 217 | 11 | 0.419819 | 1.347393 | 0.333348 | 0.350230 |
| 21 | combined | upper_relative | surface_truncated | 217 | 11 | 0.141172 | 0.582851 | 0.056546 | 0.152074 |
| 21 | combined | lower_relative | surface_truncated | 217 | 11 | 0.273554 | 0.935166 | 0.322515 | 0.221198 |
| 21 | combined | range_relative | surface_truncated | 217 | 11 | 0.424541 | 1.350332 | 0.348647 | 0.350230 |
| 21 | combined | upper_relative | historical | 217 | 11 | 0.134916 | 0.474669 | 0.080556 | 0.152074 |
| 21 | combined | lower_relative | historical | 217 | 11 | 0.174374 | 0.531861 | 0.262836 | 0.221198 |
| 21 | combined | range_relative | historical | 217 | 11 | 0.331941 | 0.963337 | 0.286589 | 0.350230 |
| 21 | combined | upper_relative | iv_raw | 217 | 11 | 0.110628 | 0.367025 | 0.193256 | 0.152074 |
| 21 | combined | lower_relative | iv_raw | 217 | 11 | 0.164785 | 0.523842 | 0.171569 | 0.221198 |
| 21 | combined | upper_relative | gjr_control | 217 | 11 | 0.113575 | 0.375831 | 0.174168 | 0.152074 |
| 21 | combined | lower_relative | gjr_control | 217 | 11 | 0.154039 | 0.488405 | 0.150940 | 0.221198 |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | lower_excursion_fixed | iv_scaled_blocks | historical | brier | 265 | 53 | 0.014934 | 0.015353 | 0.000419 | -0.003952 | 0.004790 | -0.003723 | 0.004561 |
| 5 | combined | lower_excursion_fixed | raw_iv_logistic | historical | brier | 265 | 53 | 0.015434 | 0.015353 | -0.000082 | -0.000688 | 0.000525 | -0.000696 | 0.000533 |
| 5 | combined | lower_excursion_fixed | historical | iv_scaled_blocks | brier | 265 | 53 | 0.015353 | 0.014934 | -0.000419 | -0.004790 | 0.003952 | -0.004561 | 0.003723 |
| 5 | combined | lower_excursion_fixed | raw_iv_logistic | iv_scaled_blocks | brier | 265 | 53 | 0.015434 | 0.014934 | -0.000500 | -0.004746 | 0.003745 | -0.004589 | 0.003588 |
| 5 | combined | lower_excursion_fixed | surface_permuted | historical | brier | 265 | 53 | 0.017742 | 0.015353 | -0.002389 | -0.009609 | 0.004830 | -0.009928 | 0.005150 |
| 5 | combined | lower_excursion_fixed | surface_permuted | iv_scaled_blocks | brier | 265 | 53 | 0.017742 | 0.014934 | -0.002808 | -0.009978 | 0.004362 | -0.010343 | 0.004727 |
| 5 | combined | lower_excursion_fixed | surface_liquid | historical | brier | 265 | 53 | 0.018950 | 0.015353 | -0.003598 | -0.016857 | 0.009662 | -0.016246 | 0.009051 |
| 5 | combined | lower_excursion_fixed | surface | historical | brier | 265 | 53 | 0.019244 | 0.015353 | -0.003892 | -0.018121 | 0.010338 | -0.017404 | 0.009621 |
| 5 | combined | lower_excursion_fixed | surface_truncated | historical | brier | 265 | 53 | 0.019273 | 0.015353 | -0.003921 | -0.018349 | 0.010508 | -0.017665 | 0.009823 |
| 5 | combined | lower_excursion_fixed | surface_liquid | iv_scaled_blocks | brier | 265 | 53 | 0.018950 | 0.014934 | -0.004017 | -0.016723 | 0.008690 | -0.016413 | 0.008379 |
| 5 | combined | lower_excursion_fixed | surface | iv_scaled_blocks | brier | 265 | 53 | 0.019244 | 0.014934 | -0.004310 | -0.018142 | 0.009521 | -0.018160 | 0.009539 |
| 5 | combined | lower_excursion_fixed | surface_truncated | iv_scaled_blocks | brier | 265 | 53 | 0.019273 | 0.014934 | -0.004340 | -0.018157 | 0.009478 | -0.017759 | 0.009080 |
| 5 | combined | lower_excursion_fixed | surface_lag5 | historical | brier | 265 | 53 | 0.022647 | 0.015353 | -0.007295 | -0.030084 | 0.015494 | -0.030409 | 0.015820 |
| 5 | combined | lower_excursion_fixed | surface_lag5 | iv_scaled_blocks | brier | 265 | 53 | 0.022647 | 0.014934 | -0.007714 | -0.029600 | 0.014173 | -0.030324 | 0.014896 |
| 5 | combined | lower_excursion_fixed | surface_shift21 | historical | brier | 265 | 53 | 0.024156 | 0.015353 | -0.008804 | -0.031504 | 0.013897 | -0.033514 | 0.015907 |
| 5 | combined | lower_excursion_fixed | surface_shift21 | iv_scaled_blocks | brier | 265 | 53 | 0.024156 | 0.014934 | -0.009222 | -0.030746 | 0.012301 | -0.032737 | 0.014292 |
| 5 | combined | lower_relative | gjr_control | historical | brier | 265 | 53 | 0.112153 | 0.127029 | 0.014876 | -0.017337 | 0.047088 | -0.016396 | 0.046148 |
| 5 | combined | lower_relative | iv_raw | historical | brier | 265 | 53 | 0.112677 | 0.127029 | 0.014352 | -0.019947 | 0.048651 | -0.019231 | 0.047935 |
| 5 | combined | lower_relative | iv_scaled_blocks | historical | brier | 265 | 53 | 0.117628 | 0.127029 | 0.009401 | -0.014173 | 0.032975 | -0.014144 | 0.032946 |
| 5 | combined | lower_relative | gjr_control | iv_scaled_blocks | brier | 265 | 53 | 0.112153 | 0.117628 | 0.005475 | -0.020284 | 0.031233 | -0.018613 | 0.029563 |
| 5 | combined | lower_relative | iv_raw | iv_scaled_blocks | brier | 265 | 53 | 0.112677 | 0.117628 | 0.004951 | -0.018921 | 0.028824 | -0.017655 | 0.027557 |
| 5 | combined | lower_relative | gjr_control | iv_raw | brier | 265 | 53 | 0.112153 | 0.112677 | 0.000524 | -0.011381 | 0.012428 | -0.009889 | 0.010936 |
| 5 | combined | lower_relative | iv_scaled_blocks | iv_raw | brier | 265 | 53 | 0.117628 | 0.112677 | -0.004951 | -0.028824 | 0.018921 | -0.027557 | 0.017655 |
| 5 | combined | lower_relative | historical | iv_scaled_blocks | brier | 265 | 53 | 0.127029 | 0.117628 | -0.009401 | -0.032975 | 0.014173 | -0.032946 | 0.014144 |
| 5 | combined | lower_relative | raw_iv_logistic | historical | brier | 265 | 53 | 0.141244 | 0.127029 | -0.014215 | -0.045151 | 0.016722 | -0.048485 | 0.020055 |
| 5 | combined | lower_relative | historical | iv_raw | brier | 265 | 53 | 0.127029 | 0.112677 | -0.014352 | -0.048651 | 0.019947 | -0.047935 | 0.019231 |
| 5 | combined | lower_relative | raw_iv_logistic | iv_scaled_blocks | brier | 265 | 53 | 0.141244 | 0.117628 | -0.023616 | -0.066679 | 0.019448 | -0.069905 | 0.022674 |
| 5 | combined | lower_relative | surface_truncated | historical | brier | 265 | 53 | 0.153411 | 0.127029 | -0.026382 | -0.089243 | 0.036479 | -0.097032 | 0.044268 |
| 5 | combined | lower_relative | surface_liquid | historical | brier | 265 | 53 | 0.153681 | 0.127029 | -0.026653 | -0.089969 | 0.036664 | -0.097758 | 0.044453 |
| 5 | combined | lower_relative | raw_iv_logistic | iv_raw | brier | 265 | 53 | 0.141244 | 0.112677 | -0.028567 | -0.080459 | 0.023326 | -0.084042 | 0.026908 |
| 5 | combined | lower_relative | surface_permuted | historical | brier | 265 | 53 | 0.160567 | 0.127029 | -0.033538 | -0.083397 | 0.016320 | -0.090481 | 0.023404 |
| 5 | combined | lower_relative | surface_lag5 | historical | brier | 265 | 53 | 0.161588 | 0.127029 | -0.034559 | -0.099713 | 0.030596 | -0.108700 | 0.039582 |
| 5 | combined | lower_relative | surface_truncated | iv_scaled_blocks | brier | 265 | 53 | 0.153411 | 0.117628 | -0.035783 | -0.108286 | 0.036721 | -0.115125 | 0.043559 |
| 5 | combined | lower_relative | surface_liquid | iv_scaled_blocks | brier | 265 | 53 | 0.153681 | 0.117628 | -0.036054 | -0.108652 | 0.036545 | -0.115633 | 0.043526 |
| 5 | combined | lower_relative | surface_shift21 | historical | brier | 265 | 53 | 0.165436 | 0.127029 | -0.038407 | -0.094048 | 0.017234 | -0.104196 | 0.027381 |
| 5 | combined | lower_relative | surface | historical | brier | 265 | 53 | 0.167526 | 0.127029 | -0.040497 | -0.112167 | 0.031172 | -0.121689 | 0.040694 |
| 5 | combined | lower_relative | surface_truncated | iv_raw | brier | 265 | 53 | 0.153411 | 0.112677 | -0.040734 | -0.120289 | 0.038821 | -0.127479 | 0.046010 |
| 5 | combined | lower_relative | surface_liquid | iv_raw | brier | 265 | 53 | 0.153681 | 0.112677 | -0.041005 | -0.120518 | 0.038508 | -0.127881 | 0.045872 |
| 5 | combined | lower_relative | surface_permuted | iv_scaled_blocks | brier | 265 | 53 | 0.160567 | 0.117628 | -0.042939 | -0.100205 | 0.014326 | -0.106643 | 0.020764 |
| 5 | combined | lower_relative | surface_lag5 | iv_scaled_blocks | brier | 265 | 53 | 0.161588 | 0.117628 | -0.043960 | -0.118216 | 0.030297 | -0.126431 | 0.038512 |
| 5 | combined | lower_relative | surface_shift21 | iv_scaled_blocks | brier | 265 | 53 | 0.165436 | 0.117628 | -0.047808 | -0.111312 | 0.015695 | -0.122038 | 0.026421 |
| 5 | combined | lower_relative | surface_permuted | iv_raw | brier | 265 | 53 | 0.160567 | 0.112677 | -0.047891 | -0.114830 | 0.019049 | -0.120783 | 0.025001 |
| 5 | combined | lower_relative | surface_lag5 | iv_raw | brier | 265 | 53 | 0.161588 | 0.112677 | -0.048911 | -0.129912 | 0.032090 | -0.138134 | 0.040312 |
| 5 | combined | lower_relative | surface | iv_scaled_blocks | brier | 265 | 53 | 0.167526 | 0.117628 | -0.049898 | -0.127398 | 0.027601 | -0.136757 | 0.036961 |
| 5 | combined | lower_relative | surface_shift21 | iv_raw | brier | 265 | 53 | 0.165436 | 0.112677 | -0.052759 | -0.125415 | 0.019897 | -0.135761 | 0.030242 |
| 5 | combined | lower_relative | surface | iv_raw | brier | 265 | 53 | 0.167526 | 0.112677 | -0.054850 | -0.138582 | 0.028883 | -0.148151 | 0.038451 |
| 5 | combined | range_relative | iv_scaled_blocks | historical | brier | 265 | 53 | 0.076391 | 0.168059 | 0.091668 | -0.062823 | 0.246159 | -0.083123 | 0.266458 |
| 5 | combined | range_relative | surface_truncated | historical | brier | 265 | 53 | 0.136579 | 0.168059 | 0.031480 | -0.150688 | 0.213648 | -0.155042 | 0.218002 |
| 5 | combined | range_relative | surface_liquid | historical | brier | 265 | 53 | 0.141702 | 0.168059 | 0.026357 | -0.165738 | 0.218451 | -0.170188 | 0.222901 |
| 5 | combined | range_relative | raw_iv_logistic | historical | brier | 265 | 53 | 0.142212 | 0.168059 | 0.025846 | -0.072119 | 0.123812 | -0.076919 | 0.128612 |
| 5 | combined | range_relative | surface | historical | brier | 265 | 53 | 0.157203 | 0.168059 | 0.010856 | -0.169898 | 0.191610 | -0.177059 | 0.198771 |
| 5 | combined | range_relative | surface_shift21 | historical | brier | 265 | 53 | 0.168920 | 0.168059 | -0.000862 | -0.167675 | 0.165952 | -0.173044 | 0.171321 |
| 5 | combined | range_relative | surface_lag5 | historical | brier | 265 | 53 | 0.176132 | 0.168059 | -0.008073 | -0.186517 | 0.170372 | -0.188528 | 0.172383 |
| 5 | combined | range_relative | surface_permuted | historical | brier | 265 | 53 | 0.182705 | 0.168059 | -0.014646 | -0.155937 | 0.126644 | -0.160662 | 0.131370 |
| 5 | combined | range_relative | surface_truncated | iv_scaled_blocks | brier | 265 | 53 | 0.136579 | 0.076391 | -0.060188 | -0.172940 | 0.052565 | -0.172107 | 0.051731 |
| 5 | combined | range_relative | surface_liquid | iv_scaled_blocks | brier | 265 | 53 | 0.141702 | 0.076391 | -0.065311 | -0.190207 | 0.059585 | -0.191075 | 0.060453 |
| 5 | combined | range_relative | raw_iv_logistic | iv_scaled_blocks | brier | 265 | 53 | 0.142212 | 0.076391 | -0.065821 | -0.156085 | 0.024443 | -0.163627 | 0.031984 |
| 5 | combined | range_relative | surface | iv_scaled_blocks | brier | 265 | 53 | 0.157203 | 0.076391 | -0.080812 | -0.206659 | 0.045036 | -0.215534 | 0.053910 |
| 5 | combined | range_relative | historical | iv_scaled_blocks | brier | 265 | 53 | 0.168059 | 0.076391 | -0.091668 | -0.246159 | 0.062823 | -0.266458 | 0.083123 |
| 5 | combined | range_relative | surface_shift21 | iv_scaled_blocks | brier | 265 | 53 | 0.168920 | 0.076391 | -0.092529 | -0.222691 | 0.037632 | -0.235825 | 0.050767 |
| 5 | combined | range_relative | surface_lag5 | iv_scaled_blocks | brier | 265 | 53 | 0.176132 | 0.076391 | -0.099740 | -0.253615 | 0.054134 | -0.266765 | 0.067285 |
| 5 | combined | range_relative | surface_permuted | iv_scaled_blocks | brier | 265 | 53 | 0.182705 | 0.076391 | -0.106314 | -0.248890 | 0.036262 | -0.268715 | 0.056087 |
| 5 | combined | upper_relative | iv_raw | historical | brier | 265 | 53 | 0.108191 | 0.116943 | 0.008752 | -0.038543 | 0.056047 | -0.030303 | 0.047808 |
| 5 | combined | upper_relative | iv_raw | iv_scaled_blocks | brier | 265 | 53 | 0.108191 | 0.113777 | 0.005586 | -0.008931 | 0.020103 | -0.008312 | 0.019485 |
| 5 | combined | upper_relative | gjr_control | historical | brier | 265 | 53 | 0.113039 | 0.116943 | 0.003904 | -0.034241 | 0.042049 | -0.027645 | 0.035452 |
| 5 | combined | upper_relative | iv_scaled_blocks | historical | brier | 265 | 53 | 0.113777 | 0.116943 | 0.003166 | -0.041520 | 0.047851 | -0.033765 | 0.040097 |
| 5 | combined | upper_relative | gjr_control | iv_scaled_blocks | brier | 265 | 53 | 0.113039 | 0.113777 | 0.000738 | -0.011125 | 0.012602 | -0.009782 | 0.011258 |
| 5 | combined | upper_relative | raw_iv_logistic | historical | brier | 265 | 53 | 0.116679 | 0.116943 | 0.000264 | -0.002910 | 0.003438 | -0.002738 | 0.003266 |
| 5 | combined | upper_relative | surface_lag5 | historical | brier | 265 | 53 | 0.118794 | 0.116943 | -0.001852 | -0.011392 | 0.007689 | -0.009975 | 0.006272 |
| 5 | combined | upper_relative | raw_iv_logistic | iv_scaled_blocks | brier | 265 | 53 | 0.116679 | 0.113777 | -0.002902 | -0.046289 | 0.040485 | -0.038755 | 0.032951 |
| 5 | combined | upper_relative | historical | iv_scaled_blocks | brier | 265 | 53 | 0.116943 | 0.113777 | -0.003166 | -0.047851 | 0.041520 | -0.040097 | 0.033765 |
| 5 | combined | upper_relative | surface_shift21 | historical | brier | 265 | 53 | 0.120484 | 0.116943 | -0.003541 | -0.011347 | 0.004265 | -0.011306 | 0.004224 |
| 5 | combined | upper_relative | surface_truncated | historical | brier | 265 | 53 | 0.121115 | 0.116943 | -0.004173 | -0.014817 | 0.006471 | -0.014344 | 0.005998 |
| 5 | combined | upper_relative | gjr_control | iv_raw | brier | 265 | 53 | 0.113039 | 0.108191 | -0.004848 | -0.025085 | 0.015389 | -0.023410 | 0.013713 |
| 5 | combined | upper_relative | surface_liquid | historical | brier | 265 | 53 | 0.121938 | 0.116943 | -0.004996 | -0.019242 | 0.009251 | -0.018413 | 0.008421 |
| 5 | combined | upper_relative | surface_lag5 | iv_scaled_blocks | brier | 265 | 53 | 0.118794 | 0.113777 | -0.005017 | -0.046211 | 0.036176 | -0.039430 | 0.029395 |
| 5 | combined | upper_relative | surface | historical | brier | 265 | 53 | 0.121966 | 0.116943 | -0.005024 | -0.015296 | 0.005249 | -0.014807 | 0.004760 |
| 5 | combined | upper_relative | iv_scaled_blocks | iv_raw | brier | 265 | 53 | 0.113777 | 0.108191 | -0.005586 | -0.020103 | 0.008931 | -0.019485 | 0.008312 |
| 5 | combined | upper_relative | surface_permuted | historical | brier | 265 | 53 | 0.122809 | 0.116943 | -0.005867 | -0.032017 | 0.020283 | -0.033530 | 0.021796 |
| 5 | combined | upper_relative | surface_shift21 | iv_scaled_blocks | brier | 265 | 53 | 0.120484 | 0.113777 | -0.006707 | -0.054643 | 0.041229 | -0.047152 | 0.033738 |
| 5 | combined | upper_relative | surface_truncated | iv_scaled_blocks | brier | 265 | 53 | 0.121115 | 0.113777 | -0.007339 | -0.050015 | 0.035338 | -0.042584 | 0.027907 |
| 5 | combined | upper_relative | surface_liquid | iv_scaled_blocks | brier | 265 | 53 | 0.121938 | 0.113777 | -0.008162 | -0.049341 | 0.033018 | -0.042523 | 0.026200 |
| 5 | combined | upper_relative | surface | iv_scaled_blocks | brier | 265 | 53 | 0.121966 | 0.113777 | -0.008189 | -0.052817 | 0.036439 | -0.044628 | 0.028249 |
| 5 | combined | upper_relative | raw_iv_logistic | iv_raw | brier | 265 | 53 | 0.116679 | 0.108191 | -0.008488 | -0.054765 | 0.037789 | -0.046979 | 0.030002 |
| 5 | combined | upper_relative | historical | iv_raw | brier | 265 | 53 | 0.116943 | 0.108191 | -0.008752 | -0.056047 | 0.038543 | -0.047808 | 0.030303 |
| 5 | combined | upper_relative | surface_permuted | iv_scaled_blocks | brier | 265 | 53 | 0.122809 | 0.113777 | -0.009033 | -0.056828 | 0.038763 | -0.055101 | 0.037036 |
| 5 | combined | upper_relative | surface_lag5 | iv_raw | brier | 265 | 53 | 0.118794 | 0.108191 | -0.010604 | -0.055544 | 0.034337 | -0.048761 | 0.027553 |
| 5 | combined | upper_relative | surface_shift21 | iv_raw | brier | 265 | 53 | 0.120484 | 0.108191 | -0.012293 | -0.063271 | 0.038684 | -0.055409 | 0.030822 |
| 5 | combined | upper_relative | surface_truncated | iv_raw | brier | 265 | 53 | 0.121115 | 0.108191 | -0.012925 | -0.059525 | 0.033675 | -0.051879 | 0.026029 |
| 5 | combined | upper_relative | surface_liquid | iv_raw | brier | 265 | 53 | 0.121938 | 0.108191 | -0.013748 | -0.058889 | 0.031393 | -0.051876 | 0.024381 |
| 5 | combined | upper_relative | surface | iv_raw | brier | 265 | 53 | 0.121966 | 0.108191 | -0.013776 | -0.062619 | 0.035068 | -0.054300 | 0.026748 |
| 5 | combined | upper_relative | surface_permuted | iv_raw | brier | 265 | 53 | 0.122809 | 0.108191 | -0.014619 | -0.063861 | 0.034623 | -0.061864 | 0.032626 |
| 21 | combined | lower_excursion_fixed | iv_scaled_blocks | historical | brier | 217 | 11 | 0.228758 | 0.238416 | 0.009657 | -0.066807 | 0.086122 | -0.080601 | 0.099916 |
| 21 | combined | lower_excursion_fixed | raw_iv_logistic | historical | brier | 217 | 11 | 0.242262 | 0.238416 | -0.003847 | -0.014178 | 0.006485 | -0.015979 | 0.008286 |
| 21 | combined | lower_excursion_fixed | historical | iv_scaled_blocks | brier | 217 | 11 | 0.238416 | 0.228758 | -0.009657 | -0.086122 | 0.066807 | -0.099916 | 0.080601 |
| 21 | combined | lower_excursion_fixed | raw_iv_logistic | iv_scaled_blocks | brier | 217 | 11 | 0.242262 | 0.228758 | -0.013504 | -0.092633 | 0.065625 | -0.106388 | 0.079381 |
| 21 | combined | lower_excursion_fixed | surface_lag5 | historical | brier | 217 | 11 | 0.278750 | 0.238416 | -0.040334 | -0.147804 | 0.067135 | -0.167077 | 0.086408 |
| 21 | combined | lower_excursion_fixed | surface_liquid | historical | brier | 217 | 11 | 0.286283 | 0.238416 | -0.047867 | -0.169155 | 0.073420 | -0.188293 | 0.092559 |
| 21 | combined | lower_excursion_fixed | surface_permuted | historical | brier | 217 | 11 | 0.287929 | 0.238416 | -0.049514 | -0.181117 | 0.082090 | -0.195213 | 0.096186 |
| 21 | combined | lower_excursion_fixed | surface_lag5 | iv_scaled_blocks | brier | 217 | 11 | 0.278750 | 0.228758 | -0.049992 | -0.169623 | 0.069640 | -0.193056 | 0.093072 |
| 21 | combined | lower_excursion_fixed | surface_liquid | iv_scaled_blocks | brier | 217 | 11 | 0.286283 | 0.228758 | -0.057525 | -0.185988 | 0.070939 | -0.208374 | 0.093325 |
| 21 | combined | lower_excursion_fixed | surface_permuted | iv_scaled_blocks | brier | 217 | 11 | 0.287929 | 0.228758 | -0.059171 | -0.186610 | 0.068269 | -0.197719 | 0.079377 |
| 21 | combined | lower_excursion_fixed | surface_shift21 | historical | brier | 217 | 11 | 0.306356 | 0.238416 | -0.067940 | -0.184218 | 0.048338 | -0.200892 | 0.065011 |
| 21 | combined | lower_excursion_fixed | surface | historical | brier | 217 | 11 | 0.310803 | 0.238416 | -0.072388 | -0.242690 | 0.097914 | -0.273953 | 0.129178 |
| 21 | combined | lower_excursion_fixed | surface_truncated | historical | brier | 217 | 11 | 0.313605 | 0.238416 | -0.075189 | -0.251644 | 0.101266 | -0.284084 | 0.133706 |
| 21 | combined | lower_excursion_fixed | surface_shift21 | iv_scaled_blocks | brier | 217 | 11 | 0.306356 | 0.228758 | -0.077598 | -0.194861 | 0.039666 | -0.214335 | 0.059140 |
| 21 | combined | lower_excursion_fixed | surface | iv_scaled_blocks | brier | 217 | 11 | 0.310803 | 0.228758 | -0.082045 | -0.249679 | 0.085589 | -0.279223 | 0.115133 |
| 21 | combined | lower_excursion_fixed | surface_truncated | iv_scaled_blocks | brier | 217 | 11 | 0.313605 | 0.228758 | -0.084846 | -0.258157 | 0.088464 | -0.289949 | 0.120256 |
| 21 | combined | lower_relative | gjr_control | iv_scaled_blocks | brier | 217 | 11 | 0.154039 | 0.189443 | 0.035404 | -0.050405 | 0.121213 | -0.042580 | 0.113388 |
| 21 | combined | lower_relative | iv_raw | iv_scaled_blocks | brier | 217 | 11 | 0.164785 | 0.189443 | 0.024657 | -0.054280 | 0.103595 | -0.047288 | 0.096603 |
| 21 | combined | lower_relative | gjr_control | historical | brier | 217 | 11 | 0.154039 | 0.174374 | 0.020335 | -0.032198 | 0.072869 | -0.037795 | 0.078466 |
| 21 | combined | lower_relative | historical | iv_scaled_blocks | brier | 217 | 11 | 0.174374 | 0.189443 | 0.015069 | -0.080692 | 0.110829 | -0.085236 | 0.115373 |
| 21 | combined | lower_relative | gjr_control | iv_raw | brier | 217 | 11 | 0.154039 | 0.164785 | 0.010747 | -0.001376 | 0.022870 | -0.002237 | 0.023730 |
| 21 | combined | lower_relative | iv_raw | historical | brier | 217 | 11 | 0.164785 | 0.174374 | 0.009589 | -0.041991 | 0.061169 | -0.047009 | 0.066186 |
| 21 | combined | lower_relative | raw_iv_logistic | iv_scaled_blocks | brier | 217 | 11 | 0.188872 | 0.189443 | 0.000571 | -0.111995 | 0.113137 | -0.123263 | 0.124405 |
| 21 | combined | lower_relative | historical | iv_raw | brier | 217 | 11 | 0.174374 | 0.164785 | -0.009589 | -0.061169 | 0.041991 | -0.066186 | 0.047009 |
| 21 | combined | lower_relative | raw_iv_logistic | historical | brier | 217 | 11 | 0.188872 | 0.174374 | -0.014498 | -0.057852 | 0.028857 | -0.063760 | 0.034765 |
| 21 | combined | lower_relative | iv_scaled_blocks | historical | brier | 217 | 11 | 0.189443 | 0.174374 | -0.015069 | -0.110829 | 0.080692 | -0.115373 | 0.085236 |
| 21 | combined | lower_relative | raw_iv_logistic | iv_raw | brier | 217 | 11 | 0.188872 | 0.164785 | -0.024086 | -0.103286 | 0.055113 | -0.111826 | 0.063654 |
| 21 | combined | lower_relative | iv_scaled_blocks | iv_raw | brier | 217 | 11 | 0.189443 | 0.164785 | -0.024657 | -0.103595 | 0.054280 | -0.096603 | 0.047288 |
| 21 | combined | lower_relative | surface_permuted | iv_scaled_blocks | brier | 217 | 11 | 0.225712 | 0.189443 | -0.036269 | -0.215929 | 0.143391 | -0.245628 | 0.173090 |
| 21 | combined | lower_relative | surface_permuted | historical | brier | 217 | 11 | 0.225712 | 0.174374 | -0.051338 | -0.176937 | 0.074262 | -0.192980 | 0.090305 |
| 21 | combined | lower_relative | surface_permuted | iv_raw | brier | 217 | 11 | 0.225712 | 0.164785 | -0.060926 | -0.217868 | 0.096015 | -0.239552 | 0.117699 |
| 21 | combined | lower_relative | surface_lag5 | iv_scaled_blocks | brier | 217 | 11 | 0.265394 | 0.189443 | -0.075951 | -0.316478 | 0.164576 | -0.364580 | 0.212677 |
| 21 | combined | lower_relative | surface_truncated | iv_scaled_blocks | brier | 217 | 11 | 0.273554 | 0.189443 | -0.084111 | -0.325111 | 0.156888 | -0.372387 | 0.204164 |
| 21 | combined | lower_relative | surface_liquid | iv_scaled_blocks | brier | 217 | 11 | 0.274842 | 0.189443 | -0.085400 | -0.316478 | 0.145679 | -0.358943 | 0.188144 |
| 21 | combined | lower_relative | surface_lag5 | historical | brier | 217 | 11 | 0.265394 | 0.174374 | -0.091020 | -0.294946 | 0.112906 | -0.329011 | 0.146972 |
| 21 | combined | lower_relative | surface | iv_scaled_blocks | brier | 217 | 11 | 0.287110 | 0.189443 | -0.097667 | -0.333760 | 0.138426 | -0.379548 | 0.184213 |
| 21 | combined | lower_relative | surface_truncated | historical | brier | 217 | 11 | 0.273554 | 0.174374 | -0.099180 | -0.299801 | 0.101441 | -0.334162 | 0.135802 |
| 21 | combined | lower_relative | surface_liquid | historical | brier | 217 | 11 | 0.274842 | 0.174374 | -0.100468 | -0.297293 | 0.096357 | -0.327256 | 0.126320 |
| 21 | combined | lower_relative | surface_lag5 | iv_raw | brier | 217 | 11 | 0.265394 | 0.164785 | -0.100609 | -0.331355 | 0.130138 | -0.369180 | 0.167962 |
| 21 | combined | lower_relative | surface_truncated | iv_raw | brier | 217 | 11 | 0.273554 | 0.164785 | -0.108769 | -0.336678 | 0.119141 | -0.374726 | 0.157189 |
| 21 | combined | lower_relative | surface_liquid | iv_raw | brier | 217 | 11 | 0.274842 | 0.164785 | -0.110057 | -0.332371 | 0.112257 | -0.365623 | 0.145509 |
| 21 | combined | lower_relative | surface | historical | brier | 217 | 11 | 0.287110 | 0.174374 | -0.112736 | -0.321275 | 0.095803 | -0.353672 | 0.128200 |
| 21 | combined | lower_relative | surface | iv_raw | brier | 217 | 11 | 0.287110 | 0.164785 | -0.122325 | -0.353456 | 0.108806 | -0.388850 | 0.144200 |
| 21 | combined | lower_relative | surface_shift21 | iv_scaled_blocks | brier | 217 | 11 | 0.357789 | 0.189443 | -0.168346 | -0.461056 | 0.124365 | -0.535403 | 0.198711 |
| 21 | combined | lower_relative | surface_shift21 | historical | brier | 217 | 11 | 0.357789 | 0.174374 | -0.183414 | -0.436125 | 0.069296 | -0.493897 | 0.127068 |
| 21 | combined | lower_relative | surface_shift21 | iv_raw | brier | 217 | 11 | 0.357789 | 0.164785 | -0.193003 | -0.472854 | 0.086848 | -0.537919 | 0.151913 |
| 21 | combined | range_relative | iv_scaled_blocks | historical | brier | 217 | 11 | 0.207973 | 0.331941 | 0.123969 | -0.010800 | 0.258737 | -0.018116 | 0.266053 |
| 21 | combined | range_relative | surface_shift21 | historical | brier | 217 | 11 | 0.331828 | 0.331941 | 0.000114 | -0.096120 | 0.096347 | -0.098387 | 0.098614 |
| 21 | combined | range_relative | raw_iv_logistic | historical | brier | 217 | 11 | 0.360772 | 0.331941 | -0.028831 | -0.123932 | 0.066271 | -0.143905 | 0.086244 |
| 21 | combined | range_relative | surface_permuted | historical | brier | 217 | 11 | 0.386279 | 0.331941 | -0.054338 | -0.190889 | 0.082213 | -0.215850 | 0.107174 |
| 21 | combined | range_relative | surface_lag5 | historical | brier | 217 | 11 | 0.407481 | 0.331941 | -0.075539 | -0.218686 | 0.067607 | -0.249127 | 0.098048 |
| 21 | combined | range_relative | surface | historical | brier | 217 | 11 | 0.408859 | 0.331941 | -0.076918 | -0.247469 | 0.093634 | -0.279143 | 0.125308 |
| 21 | combined | range_relative | surface_liquid | historical | brier | 217 | 11 | 0.419819 | 0.331941 | -0.087878 | -0.261054 | 0.085298 | -0.300865 | 0.125110 |
| 21 | combined | range_relative | surface_truncated | historical | brier | 217 | 11 | 0.424541 | 0.331941 | -0.092600 | -0.285353 | 0.100153 | -0.330014 | 0.144815 |
| 21 | combined | range_relative | surface_shift21 | iv_scaled_blocks | brier | 217 | 11 | 0.331828 | 0.207973 | -0.123855 | -0.311628 | 0.063918 | -0.320992 | 0.073282 |
| 21 | combined | range_relative | historical | iv_scaled_blocks | brier | 217 | 11 | 0.331941 | 0.207973 | -0.123969 | -0.258737 | 0.010800 | -0.266053 | 0.018116 |
| 21 | combined | range_relative | raw_iv_logistic | iv_scaled_blocks | brier | 217 | 11 | 0.360772 | 0.207973 | -0.152799 | -0.287439 | -0.018159 | -0.306807 | 0.001209 |
| 21 | combined | range_relative | surface_permuted | iv_scaled_blocks | brier | 217 | 11 | 0.386279 | 0.207973 | -0.178307 | -0.368316 | 0.011703 | -0.396199 | 0.039586 |
| 21 | combined | range_relative | surface_lag5 | iv_scaled_blocks | brier | 217 | 11 | 0.407481 | 0.207973 | -0.199508 | -0.428383 | 0.029367 | -0.460778 | 0.061762 |
| 21 | combined | range_relative | surface | iv_scaled_blocks | brier | 217 | 11 | 0.408859 | 0.207973 | -0.200886 | -0.425092 | 0.023320 | -0.452720 | 0.050948 |
| 21 | combined | range_relative | surface_liquid | iv_scaled_blocks | brier | 217 | 11 | 0.419819 | 0.207973 | -0.211846 | -0.445697 | 0.022004 | -0.488062 | 0.064370 |
| 21 | combined | range_relative | surface_truncated | iv_scaled_blocks | brier | 217 | 11 | 0.424541 | 0.207973 | -0.216568 | -0.456140 | 0.023003 | -0.501928 | 0.068791 |
| 21 | combined | upper_relative | iv_raw | historical | brier | 217 | 11 | 0.110628 | 0.134916 | 0.024288 | -0.074852 | 0.123427 | -0.073278 | 0.121854 |
| 21 | combined | upper_relative | gjr_control | historical | brier | 217 | 11 | 0.113575 | 0.134916 | 0.021340 | -0.061658 | 0.104338 | -0.061893 | 0.104573 |
| 21 | combined | upper_relative | iv_scaled_blocks | historical | brier | 217 | 11 | 0.118663 | 0.134916 | 0.016253 | -0.061124 | 0.093630 | -0.063008 | 0.095513 |
| 21 | combined | upper_relative | iv_raw | iv_scaled_blocks | brier | 217 | 11 | 0.110628 | 0.118663 | 0.008035 | -0.043903 | 0.059973 | -0.041734 | 0.057805 |
| 21 | combined | upper_relative | gjr_control | iv_scaled_blocks | brier | 217 | 11 | 0.113575 | 0.118663 | 0.005088 | -0.034185 | 0.044360 | -0.032969 | 0.043144 |
| 21 | combined | upper_relative | surface | historical | brier | 217 | 11 | 0.132905 | 0.134916 | 0.002011 | -0.013946 | 0.017967 | -0.013166 | 0.017188 |
| 21 | combined | upper_relative | raw_iv_logistic | historical | brier | 217 | 11 | 0.136144 | 0.134916 | -0.001228 | -0.013519 | 0.011063 | -0.013763 | 0.011307 |
| 21 | combined | upper_relative | gjr_control | iv_raw | brier | 217 | 11 | 0.113575 | 0.110628 | -0.002948 | -0.023344 | 0.017449 | -0.022103 | 0.016207 |
| 21 | combined | upper_relative | surface_truncated | historical | brier | 217 | 11 | 0.141172 | 0.134916 | -0.006257 | -0.024849 | 0.012335 | -0.025880 | 0.013366 |
| 21 | combined | upper_relative | surface_liquid | historical | brier | 217 | 11 | 0.142034 | 0.134916 | -0.007119 | -0.027202 | 0.012964 | -0.027836 | 0.013599 |
| 21 | combined | upper_relative | surface_shift21 | historical | brier | 217 | 11 | 0.142665 | 0.134916 | -0.007750 | -0.028078 | 0.012578 | -0.028302 | 0.012803 |
| 21 | combined | upper_relative | iv_scaled_blocks | iv_raw | brier | 217 | 11 | 0.118663 | 0.110628 | -0.008035 | -0.059973 | 0.043903 | -0.057805 | 0.041734 |
| 21 | combined | upper_relative | surface_lag5 | historical | brier | 217 | 11 | 0.143781 | 0.134916 | -0.008865 | -0.030283 | 0.012554 | -0.031198 | 0.013468 |
| 21 | combined | upper_relative | surface | iv_scaled_blocks | brier | 217 | 11 | 0.132905 | 0.118663 | -0.014242 | -0.093255 | 0.064771 | -0.096439 | 0.067955 |
| 21 | combined | upper_relative | historical | iv_scaled_blocks | brier | 217 | 11 | 0.134916 | 0.118663 | -0.016253 | -0.093630 | 0.061124 | -0.095513 | 0.063008 |
| 21 | combined | upper_relative | raw_iv_logistic | iv_scaled_blocks | brier | 217 | 11 | 0.136144 | 0.118663 | -0.017481 | -0.095207 | 0.060246 | -0.097715 | 0.062754 |
| 21 | combined | upper_relative | surface | iv_raw | brier | 217 | 11 | 0.132905 | 0.110628 | -0.022277 | -0.122617 | 0.078062 | -0.123249 | 0.078695 |
| 21 | combined | upper_relative | surface_truncated | iv_scaled_blocks | brier | 217 | 11 | 0.141172 | 0.118663 | -0.022509 | -0.106546 | 0.061527 | -0.109022 | 0.064003 |
| 21 | combined | upper_relative | surface_liquid | iv_scaled_blocks | brier | 217 | 11 | 0.142034 | 0.118663 | -0.023371 | -0.105735 | 0.058992 | -0.107640 | 0.060897 |
| 21 | combined | upper_relative | surface_shift21 | iv_scaled_blocks | brier | 217 | 11 | 0.142665 | 0.118663 | -0.024002 | -0.106747 | 0.058743 | -0.108468 | 0.060463 |
| 21 | combined | upper_relative | historical | iv_raw | brier | 217 | 11 | 0.134916 | 0.110628 | -0.024288 | -0.123427 | 0.074852 | -0.121854 | 0.073278 |
| 21 | combined | upper_relative | surface_lag5 | iv_scaled_blocks | brier | 217 | 11 | 0.143781 | 0.118663 | -0.025118 | -0.110806 | 0.060571 | -0.112755 | 0.062520 |
| 21 | combined | upper_relative | raw_iv_logistic | iv_raw | brier | 217 | 11 | 0.136144 | 0.110628 | -0.025516 | -0.128050 | 0.077018 | -0.127264 | 0.076233 |
| 21 | combined | upper_relative | surface_permuted | historical | brier | 217 | 11 | 0.161919 | 0.134916 | -0.027003 | -0.093861 | 0.039854 | -0.103569 | 0.049562 |
| 21 | combined | upper_relative | surface_truncated | iv_raw | brier | 217 | 11 | 0.141172 | 0.110628 | -0.030545 | -0.140536 | 0.079446 | -0.139060 | 0.077971 |
| 21 | combined | upper_relative | surface_liquid | iv_raw | brier | 217 | 11 | 0.142034 | 0.110628 | -0.031407 | -0.141033 | 0.078220 | -0.139177 | 0.076364 |
| 21 | combined | upper_relative | surface_shift21 | iv_raw | brier | 217 | 11 | 0.142665 | 0.110628 | -0.032037 | -0.143334 | 0.079259 | -0.141144 | 0.077069 |
| 21 | combined | upper_relative | surface_lag5 | iv_raw | brier | 217 | 11 | 0.143781 | 0.110628 | -0.033153 | -0.146612 | 0.080306 | -0.144641 | 0.078335 |
| 21 | combined | upper_relative | surface_permuted | iv_scaled_blocks | brier | 217 | 11 | 0.161919 | 0.118663 | -0.043256 | -0.143637 | 0.057125 | -0.147739 | 0.061227 |
| 21 | combined | upper_relative | surface_permuted | iv_raw | brier | 217 | 11 | 0.161919 | 0.110628 | -0.051291 | -0.167980 | 0.065397 | -0.166028 | 0.063446 |

[Fixed-time features](features-5.csv) · [Original expiry and price data](../../../nifty_forecast_v12/2026-11-24/run-001/V12_OPTION_IMPLIED_DISTRIBUTIONS.md) · [All tail and transition losses](transition-and-tail-leaderboard.csv).
