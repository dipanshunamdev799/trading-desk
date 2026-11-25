# V14 Complete Model Comparison

Independent objective rankings below use full expected coverage of 265 and 217 origins. Other cohorts, conditional events and matched subsets appear in the full tables. The Pareto view uses an objective-specific loss, absolute early–late gap, a stated coarse model-complexity tier, and nominal coverage error for interval-related views. The date counts and effective sample diagnostics are retained. Separate likelihood and error metrics lead to distinct statistical choices.

## Endpoint direction

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | sign_shrinkage | 265 | 53 | 0.228529 | 0.648943 | 0.626415 | 0.636001 | 0.010457 | 0.014842 | 0.826415 | 0.045780 |
| 5 | combined | domestic_location_only | 265 | 53 | 0.228761 | 0.650324 | 0.641509 | 0.645934 | 0.010609 | 0.014946 | 0.811321 | 0.044748 |
| 5 | combined | V13_week_Brier | 265 | 53 | 0.229587 | 0.651757 | 0.626415 | 0.636001 | 0.010609 | 0.015013 | 0.807547 | 0.044748 |
| 5 | combined | V12_week_Brier | 265 | 53 | 0.229715 | 0.655524 | 0.626415 | 0.633316 | 0.010896 | 0.014687 | 0.781132 | 0.041415 |
| 5 | combined | skew_only | 265 | 53 | 0.230260 | 0.653114 | 0.622642 | 0.633518 | 0.010619 | 0.015013 | 0.807547 | 0.044793 |
| 5 | combined | student_tail_only | 265 | 53 | 0.230937 | 0.654835 | 0.637736 | 0.647927 | 0.010617 | 0.015013 | 0.807547 | 0.044626 |
| 5 | combined | domestic_location_gjr_scale | 265 | 53 | 0.231450 | 0.659310 | 0.630189 | 0.633114 | 0.010787 | 0.014946 | 0.781132 | 0.041771 |
| 5 | combined | gjr_dispersion_only | 265 | 53 | 0.233757 | 0.666573 | 0.622642 | 0.631728 | 0.010793 | 0.015013 | 0.784906 | 0.041771 |
| 5 | combined | hybrid_gjr_group | 265 | 53 | 0.235874 | 0.664707 | 0.630189 | 0.644751 | 0.010512 | 0.014904 | 0.788679 | 0.042576 |
| 5 | combined | V13_week_CRPS | 265 | 53 | 0.236495 | 0.665957 | 0.630189 | 0.644751 | 0.010472 | 0.014903 | 0.788679 | 0.043399 |
| 21 | combined | domestic_location_gjr_scale | 217 | 11 | 0.245042 | 0.683095 | 0.511521 | 0.502675 | 0.024989 | 0.033042 | 0.668203 | 0.071794 |
| 21 | combined | sign_magnitude_hybrid | 217 | 11 | 0.246277 | 0.685528 | 0.603687 | 0.617256 | 0.025830 | 0.034209 | 0.709677 | 0.084910 |
| 21 | combined | domestic_location_only | 217 | 11 | 0.246806 | 0.686707 | 0.516129 | 0.507938 | 0.025185 | 0.033042 | 0.672811 | 0.077357 |
| 21 | combined | skew_only | 217 | 11 | 0.249447 | 0.692039 | 0.437788 | 0.500000 | 0.025214 | 0.033371 | 0.663594 | 0.077335 |
| 21 | combined | trend_shrink | 217 | 11 | 0.249894 | 0.692947 | 0.511521 | 0.475884 | 0.025347 | 0.033495 | 0.755760 | 0.099802 |
| 21 | combined | gjr_dispersion_only | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025077 | 0.033371 | 0.631336 | 0.071794 |
| 21 | combined | hybrid_gjr_group | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025087 | 0.033371 | 0.654378 | 0.073449 |
| 21 | combined | sign_shrinkage | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025220 | 0.033371 | 0.672811 | 0.077357 |
| 21 | combined | student_tail_only | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025195 | 0.033371 | 0.686636 | 0.078767 |
| 21 | combined | V13_IV_scaled_symmetric | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025220 | 0.033371 | 0.672811 | 0.077357 |

## Full endpoint distribution

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | sign_shrinkage | 265 | 53 | 0.228529 | 0.648943 | 0.626415 | 0.636001 | 0.010457 | 0.014842 | 0.826415 | 0.045780 |
| 5 | combined | V13_week_CRPS | 265 | 53 | 0.236495 | 0.665957 | 0.630189 | 0.644751 | 0.010472 | 0.014903 | 0.788679 | 0.043399 |
| 5 | combined | hybrid_gjr_group | 265 | 53 | 0.235874 | 0.664707 | 0.630189 | 0.644751 | 0.010512 | 0.014904 | 0.788679 | 0.042576 |
| 5 | combined | domestic_location_only | 265 | 53 | 0.228761 | 0.650324 | 0.641509 | 0.645934 | 0.010609 | 0.014946 | 0.811321 | 0.044748 |
| 5 | combined | V13_week_Brier | 265 | 53 | 0.229587 | 0.651757 | 0.626415 | 0.636001 | 0.010609 | 0.015013 | 0.807547 | 0.044748 |
| 5 | combined | student_tail_only | 265 | 53 | 0.230937 | 0.654835 | 0.637736 | 0.647927 | 0.010617 | 0.015013 | 0.807547 | 0.044626 |
| 5 | combined | skew_only | 265 | 53 | 0.230260 | 0.653114 | 0.622642 | 0.633518 | 0.010619 | 0.015013 | 0.807547 | 0.044793 |
| 5 | combined | V12_week_CRPS | 265 | 53 | 0.241437 | 0.676126 | 0.622642 | 0.637994 | 0.010677 | 0.014897 | 0.803774 | 0.043636 |
| 5 | combined | V13_diffusion_iv | 265 | 53 | 0.248272 | 0.689695 | 0.569811 | 0.569213 | 0.010695 | 0.015051 | 0.815094 | 0.047355 |
| 5 | combined | trend_shrink | 265 | 53 | 0.247349 | 0.687842 | 0.588679 | 0.569098 | 0.010703 | 0.015013 | 0.807547 | 0.047527 |
| 21 | combined | regime_state | 217 | 11 | 0.250994 | 0.695137 | 0.479263 | 0.489129 | 0.024750 | 0.033593 | 0.741935 | 0.091201 |
| 21 | combined | gjr_student | 217 | 11 | 0.253372 | 0.699905 | 0.442396 | 0.502934 | 0.024788 | 0.033343 | 0.718894 | 0.083314 |
| 21 | combined | gjr_skew | 217 | 11 | 0.254059 | 0.701281 | 0.442396 | 0.502934 | 0.024801 | 0.033344 | 0.714286 | 0.083346 |
| 21 | combined | gjr_gauss | 217 | 11 | 0.255124 | 0.703419 | 0.437788 | 0.497670 | 0.024827 | 0.033353 | 0.705069 | 0.082012 |
| 21 | combined | historical_innov | 217 | 11 | 0.254685 | 0.702533 | 0.442396 | 0.502934 | 0.024887 | 0.033423 | 0.705069 | 0.082029 |
| 21 | combined | latent_sv | 217 | 11 | 0.253531 | 0.700223 | 0.451613 | 0.508801 | 0.024959 | 0.033359 | 0.705069 | 0.082190 |
| 21 | combined | domestic_location_gjr_scale | 217 | 11 | 0.245042 | 0.683095 | 0.511521 | 0.502675 | 0.024989 | 0.033042 | 0.668203 | 0.071794 |
| 21 | combined | gjr_iv | 217 | 11 | 0.251098 | 0.695344 | 0.465438 | 0.498965 | 0.025060 | 0.033295 | 0.737327 | 0.090148 |
| 21 | combined | separate_gap | 217 | 11 | 0.251176 | 0.695503 | 0.497696 | 0.532312 | 0.025067 | 0.033336 | 0.741935 | 0.089537 |
| 21 | combined | jump_shift | 217 | 11 | 0.251009 | 0.695168 | 0.483871 | 0.521182 | 0.025070 | 0.033357 | 0.746544 | 0.089717 |

## Realized risk

| horizon | cohort | model | n | disjoint | mae | rmse | qlike | bias | rank_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | gjr_ivx | 265 | 53 | 0.037402 | 0.048229 | 0.299575 | -0.003188 | 0.603550 |
| 5 | combined | V13_calibrated_IV | 265 | 53 | 0.037517 | 0.049633 | 0.338910 | -0.010390 | 0.605180 |
| 5 | combined | v14_iv_calibrated | 265 | 53 | 0.037517 | 0.049633 | 0.338906 | -0.010389 | 0.605180 |
| 5 | combined | latent_iv | 265 | 53 | 0.037671 | 0.050451 | 0.322511 | -0.010127 | 0.620629 |
| 5 | combined | V13_raw_ATM | 265 | 53 | 0.037814 | 0.048184 | 0.276187 | 0.007769 | 0.611711 |
| 5 | combined | raw_iv | 265 | 53 | 0.037814 | 0.048184 | 0.276187 | 0.007769 | 0.611711 |
| 5 | combined | blend_gjr_iv | 265 | 53 | 0.037978 | 0.047839 | 0.287184 | 0.003883 | 0.609993 |
| 5 | combined | V13_75IV25RV | 265 | 53 | 0.038196 | 0.049083 | 0.273634 | 0.006907 | 0.627273 |
| 5 | combined | gjr_vixx | 265 | 53 | 0.039213 | 0.051257 | 0.341651 | -0.004401 | 0.534024 |
| 5 | combined | gjr_gauss | 265 | 53 | 0.039549 | 0.052567 | 0.373883 | -0.006296 | 0.512237 |
| 21 | combined | V13_GJR | 217 | 11 | 0.033179 | 0.043304 | 0.199677 | -0.009266 | 0.528229 |
| 21 | combined | blend_gjr_iv | 217 | 11 | 0.033780 | 0.046696 | 0.247374 | -0.015667 | 0.518708 |
| 21 | combined | gjr_vixx | 217 | 11 | 0.033960 | 0.046803 | 0.264056 | -0.018533 | 0.522921 |
| 21 | combined | V13_EGARCH | 217 | 11 | 0.034943 | 0.047496 | 0.302016 | -0.010128 | 0.406027 |
| 21 | combined | gjr_student | 217 | 11 | 0.035464 | 0.048172 | 0.263397 | -0.019420 | 0.544649 |
| 21 | combined | gjr_skew | 217 | 11 | 0.035540 | 0.048175 | 0.264589 | -0.019713 | 0.535694 |
| 21 | combined | egarch_student | 217 | 11 | 0.035730 | 0.045772 | 0.207684 | -0.002631 | 0.605278 |
| 21 | combined | gjr_ivx | 217 | 11 | 0.037160 | 0.049204 | 0.310001 | -0.015734 | 0.474324 |
| 21 | combined | gjr_gauss | 217 | 11 | 0.037829 | 0.050582 | 0.305103 | -0.022342 | 0.446467 |
| 21 | combined | V13_IV_intraday | 217 | 11 | 0.039122 | 0.054761 | 0.419481 | -0.026428 | 0.337372 |

## Range, passage and calibration

| horizon | target | cohort | model | n | disjoint | crps | mae | pinball | coverage80 | width80 | interval_score80 | coverage95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | range | combined | V13_diffusion_iv | 265 | 53 | 0.005793 | 0.008182 | 0.002010 | 0.716981 | 0.021638 | 0.038161 | 0.898113 |
| 5 | range | combined | simple_drift | 265 | 53 | 0.005795 | 0.008200 | 0.002011 | 0.720755 | 0.021795 | 0.038154 | 0.905660 |
| 5 | range | combined | constant_iv | 265 | 53 | 0.005795 | 0.008197 | 0.002010 | 0.716981 | 0.021797 | 0.038142 | 0.901887 |
| 5 | range | combined | trend_shrink | 265 | 53 | 0.005801 | 0.008210 | 0.002012 | 0.720755 | 0.021833 | 0.038167 | 0.901887 |
| 5 | range | combined | gjr_iv | 265 | 53 | 0.005850 | 0.007997 | 0.002042 | 0.788679 | 0.021226 | 0.038165 | 0.920755 |
| 5 | range | combined | trend_persistent | 265 | 53 | 0.005872 | 0.008020 | 0.002054 | 0.784906 | 0.021144 | 0.038451 | 0.920755 |
| 5 | range | combined | path_mixture | 265 | 53 | 0.005882 | 0.008124 | 0.002049 | 0.781132 | 0.022215 | 0.038225 | 0.932075 |
| 5 | range | combined | joint_tail_width | 265 | 53 | 0.005924 | 0.008239 | 0.002068 | 0.788679 | 0.023445 | 0.038917 | 0.932075 |
| 5 | range | combined | latent_sv | 265 | 53 | 0.005955 | 0.007990 | 0.002078 | 0.818868 | 0.022208 | 0.039232 | 0.928302 |
| 21 | range | combined | gjr_student | 217 | 11 | 0.015422 | 0.019857 | 0.005389 | 0.764977 | 0.044758 | 0.100304 | 0.889401 |
| 21 | range | combined | gjr_skew | 217 | 11 | 0.015440 | 0.019897 | 0.005382 | 0.741935 | 0.044847 | 0.100705 | 0.889401 |
| 21 | range | combined | regime_state | 217 | 11 | 0.015942 | 0.021402 | 0.005499 | 0.755760 | 0.055702 | 0.106861 | 0.898618 |
| 21 | range | combined | historical_innov | 217 | 11 | 0.016051 | 0.020618 | 0.005570 | 0.682028 | 0.043285 | 0.106076 | 0.894009 |
| 21 | range | combined | gjr_gauss | 217 | 11 | 0.016079 | 0.020621 | 0.005598 | 0.663594 | 0.042861 | 0.106888 | 0.889401 |
| 21 | range | combined | V13_diffusion_iv | 217 | 11 | 0.016275 | 0.022336 | 0.005872 | 0.599078 | 0.045217 | 0.111077 | 0.824885 |
| 21 | range | combined | gjr_iv | 217 | 11 | 0.016304 | 0.021538 | 0.005994 | 0.640553 | 0.042866 | 0.114532 | 0.843318 |
| 21 | range | combined | trend_persistent | 217 | 11 | 0.016309 | 0.021433 | 0.006019 | 0.640553 | 0.042467 | 0.115056 | 0.834101 |
| 21 | range | combined | latent_sv | 217 | 11 | 0.016375 | 0.021030 | 0.005874 | 0.677419 | 0.043848 | 0.112200 | 0.870968 |

| horizon | model | n | disjoint | brier | log_loss | integrated_brier | passage_log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | trend_shrink | 265 | 53 | 0.143371 | 0.435874 | 0.119424 | 0.873409 |
| 5 | V13_diffusion_iv | 265 | 53 | 0.144154 | — | — | — |
| 5 | trend_persistent | 265 | 53 | 0.144178 | 0.440338 | 0.119660 | 0.876398 |
| 5 | constant_iv | 265 | 53 | 0.144532 | 0.438896 | 0.120174 | 0.876001 |
| 5 | gjr_iv | 265 | 53 | 0.145105 | 0.441552 | 0.120214 | 0.877932 |
| 5 | V13_analytic_iv_diffusion | 265 | 53 | 0.145264 | — | — | — |
| 5 | simple_drift | 265 | 53 | 0.145305 | 0.441119 | 0.120540 | 0.878575 |
| 5 | path_mixture | 265 | 53 | 0.145614 | 0.443850 | 0.120748 | 0.881279 |
| 5 | latent_sv | 265 | 53 | 0.145653 | 0.444288 | 0.120522 | 0.879406 |
| 5 | joint_tail_width | 265 | 53 | 0.145731 | 0.444220 | 0.120824 | 0.881482 |
| 21 | trend_persistent | 217 | 11 | 0.181085 | 0.545527 | 0.157875 | 1.918553 |
| 21 | trend_shrink | 217 | 11 | 0.182220 | 0.551684 | 0.158161 | 1.925139 |
| 21 | gjr_iv | 217 | 11 | 0.183138 | 0.551160 | 0.159133 | 1.925006 |
| 21 | gjr_student | 217 | 11 | 0.183636 | 0.548173 | 0.160668 | 1.931649 |
| 21 | separate_gap | 217 | 11 | 0.183814 | 0.553701 | 0.160187 | 1.926073 |
| 21 | gjr_skew | 217 | 11 | 0.183932 | 0.548757 | 0.160748 | 1.928677 |
| 21 | jump_no_episode | 217 | 11 | 0.183973 | 0.553984 | 0.160336 | 1.928130 |
| 21 | jump_shift | 217 | 11 | 0.183997 | 0.554067 | 0.160348 | 1.927602 |
| 21 | jump_diffusion | 217 | 11 | 0.184022 | 0.554169 | 0.160363 | 1.927303 |
| 21 | jump_1m | 217 | 11 | 0.184053 | 0.554191 | 0.160375 | 1.927672 |

| horizon | model | cohort | n | disjoint | prediction_rows | energy_score | variogram_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V13_diffusion_iv | combined | 265 | 53 | 265 | 1.562100 | 0.148752 |
| 5 | trend_shrink | combined | 265 | 53 | 265 | 1.562593 | 0.149603 |
| 5 | constant_iv | combined | 265 | 53 | 265 | 1.567506 | 0.149968 |
| 5 | simple_drift | combined | 265 | 53 | 265 | 1.571698 | 0.150017 |
| 5 | trend_persistent | combined | 265 | 53 | 265 | 1.595744 | 0.155640 |
| 5 | path_mixture | combined | 265 | 53 | 265 | 1.597853 | 0.155510 |
| 5 | gjr_iv | combined | 265 | 53 | 265 | 1.598766 | 0.156669 |
| 5 | joint_tail_width | combined | 265 | 53 | 265 | 1.599321 | 0.156406 |
| 21 | gjr_student | combined | 217 | 11 | 217 | 2.487703 | 0.281181 |
| 21 | gjr_skew | combined | 217 | 11 | 217 | 2.488983 | 0.281942 |
| 21 | V13_diffusion_iv | combined | 217 | 11 | 217 | 2.510707 | 0.285451 |
| 21 | trend_persistent | combined | 217 | 11 | 217 | 2.529082 | 0.297548 |
| 21 | path_mixture | combined | 217 | 11 | 217 | 2.531511 | 0.298393 |
| 21 | gjr_iv | combined | 217 | 11 | 217 | 2.534279 | 0.299556 |
| 21 | joint_pit | combined | 217 | 11 | 217 | 2.537546 | 0.300182 |
| 21 | joint_tail_width | combined | 217 | 11 | 217 | 2.539067 | 0.300965 |

| horizon | objective | model | loss | absolute_cohort_gap | coverage80_error | complexity_tier |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | endpoint_distribution | sign_shrinkage | 0.010457 | 0.000335 | 0.026415 | 2 |
| 5 | endpoint_distribution | V13_week_CRPS | 0.010472 | 0.000186 | 0.011321 | 2 |
| 5 | endpoint_distribution | domestic_location_only | 0.010609 | 0.000173 | 0.011321 | 2 |
| 5 | endpoint_distribution | V13_week_Brier | 0.010609 | 0.000208 | 0.007547 | 2 |
| 5 | endpoint_distribution | V12_week_CRPS | 0.010677 | 0.000016 | 0.003774 | 2 |
| 5 | endpoint_distribution | constant_iv | 0.010734 | 0.001675 | 0.007547 | 1 |
| 5 | endpoint_distribution | simple_drift | 0.010823 | 0.001858 | 0.000000 | 2 |
| 5 | endpoint_distribution | symmetric | 0.011058 | 0.001437 | 0.064151 | 1 |
| 5 | joint | V13_diffusion_iv | 1.562100 | 0.331737 | — | 2 |
| 5 | joint | constant_iv | 1.567506 | 0.340439 | — | 1 |
| 5 | joint | simple_drift | 1.571698 | 0.330005 | — | 2 |
| 5 | joint | joint_pit | 1.601604 | 0.328873 | — | 3 |
| 5 | range | V13_diffusion_iv | 0.005793 | 0.000490 | 0.083019 | 2 |
| 5 | range | simple_drift | 0.005795 | 0.000461 | 0.079245 | 2 |
| 5 | range | constant_iv | 0.005795 | 0.000461 | 0.083019 | 1 |
| 5 | range | trend_shrink | 0.005801 | 0.000457 | 0.079245 | 2 |
| 5 | range | gjr_iv | 0.005850 | 0.000623 | 0.011321 | 2 |
| 5 | range | path_mixture | 0.005882 | 0.000509 | 0.018868 | 3 |
| 5 | range | joint_tail_width | 0.005924 | 0.000474 | 0.011321 | 3 |
| 5 | range | latent_sv | 0.005955 | 0.000572 | 0.018868 | 2 |
| 5 | range | V13_iv_scaled | 0.005961 | 0.000291 | 0.033962 | 2 |
| 5 | range | intraday_blocks | 0.006076 | 0.000210 | 0.041509 | 3 |
| 5 | range | separate_gap | 0.006101 | 0.000375 | 0.007547 | 2 |
| 5 | range | jump_no_episode | 0.006119 | 0.000394 | 0.003774 | 2 |
| 5 | range | jump_diffusion | 0.006119 | 0.000388 | 0.003774 | 2 |
| 5 | range | jump_1m | 0.006119 | 0.000386 | 0.003774 | 2 |
| 5 | range | V13_empirical_range | 0.007918 | 0.001614 | 0.045283 | 1 |
| 5 | touch | trend_shrink | 0.143371 | 0.004920 | — | 2 |
| 5 | touch | constant_iv | 0.144532 | 0.006913 | — | 1 |
| 5 | touch | regime_state | 0.150884 | 0.001630 | — | 3 |
| 5 | touch | V13_empirical_exact | 0.156019 | 0.003794 | — | 1 |
| 5 | volatility | gjr_ivx | 0.037402 | 0.003718 | — | 2 |
| 5 | volatility | V13_calibrated_IV | 0.037517 | 0.003114 | — | 2 |
| 5 | volatility | v14_iv_calibrated | 0.037517 | 0.003113 | — | 2 |
| 5 | volatility | latent_iv | 0.037671 | 0.002217 | — | 2 |
| 5 | volatility | V13_raw_ATM | 0.037814 | 0.003735 | — | 1 |
| 5 | volatility | raw_iv | 0.037814 | 0.003735 | — | 1 |
| 5 | volatility | gjr_vixx | 0.039213 | 0.002041 | — | 2 |
| 5 | volatility | egarch_student | 0.039960 | 0.001428 | — | 2 |
| 5 | volatility | latent_kalman | 0.040317 | 0.000496 | — | 2 |
| 5 | volatility | garch_gauss | 0.043828 | 0.000338 | — | 2 |
| 5 | weekly_and_monthly_direction | sign_shrinkage | 0.228529 | 0.041013 | — | 2 |
| 5 | weekly_and_monthly_direction | V12_week_Brier | 0.229715 | 0.014609 | — | 2 |
| 5 | weekly_and_monthly_direction | trend_shrink | 0.247349 | 0.008377 | — | 2 |
| 5 | weekly_and_monthly_direction | trend_persistent | 0.248223 | 0.007999 | — | 2 |
| 5 | weekly_and_monthly_direction | V13_diffusion_iv | 0.248272 | 0.001009 | — | 2 |
| 5 | weekly_and_monthly_direction | symmetric | 0.250000 | 0.000000 | — | 1 |
| 21 | endpoint_distribution | regime_state | 0.024750 | 0.003135 | 0.058065 | 3 |
| 21 | endpoint_distribution | gjr_student | 0.024788 | 0.004174 | 0.081106 | 2 |
| 21 | endpoint_distribution | gjr_gauss | 0.024827 | 0.004165 | 0.094931 | 2 |
| 21 | endpoint_distribution | gjr_iv | 0.025060 | 0.003763 | 0.062673 | 2 |
| 21 | endpoint_distribution | separate_gap | 0.025067 | 0.003748 | 0.058065 | 2 |
| 21 | endpoint_distribution | jump_shift | 0.025070 | 0.003726 | 0.053456 | 2 |
| 21 | endpoint_distribution | jump_1m | 0.025072 | 0.003725 | 0.053456 | 2 |
| 21 | endpoint_distribution | constant_iv | 0.025281 | 0.003237 | 0.058065 | 1 |
| 21 | endpoint_distribution | trend_shrink | 0.025347 | 0.003399 | 0.044240 | 2 |
| 21 | endpoint_distribution | symmetric | 0.025420 | 0.003141 | 0.164055 | 1 |
| 21 | endpoint_distribution | widened_gauss | 0.025441 | 0.002202 | 0.021198 | 2 |
| 21 | endpoint_distribution | V13_week_CRPS | 0.027282 | 0.001415 | 0.141014 | 2 |
| 21 | endpoint_distribution | V13_week_Brier | 0.028227 | 0.000536 | 0.164055 | 2 |
| 21 | joint | gjr_student | 2.487703 | 1.453217 | — | 2 |
| 21 | joint | path_mixture | 2.531511 | 1.436855 | — | 3 |
| 21 | joint | joint_pit | 2.537546 | 1.406361 | — | 3 |
| 21 | joint | constant_iv | 2.553926 | 1.564348 | — | 1 |
| 21 | range | gjr_student | 0.015422 | 0.002045 | 0.035023 | 2 |
| 21 | range | constant_iv | 0.017280 | 0.005135 | 0.233180 | 1 |
| 21 | range | V13_empirical_range | 0.019522 | 0.009961 | 0.187097 | 1 |
| 21 | touch | trend_persistent | 0.181085 | 0.028185 | — | 2 |
| 21 | touch | trend_shrink | 0.182220 | 0.023262 | — | 2 |
| 21 | touch | V13_analytic_iv_diffusion | 0.184067 | 0.027136 | — | 1 |
| 21 | touch | constant_iv | 0.185046 | 0.024671 | — | 1 |
| 21 | touch | widened_gauss | 0.186522 | 0.022387 | — | 2 |
| 21 | touch | regime_state | 0.186681 | 0.020714 | — | 3 |
| 21 | touch | calibrated_iv | 0.190294 | 0.021986 | — | 2 |
| 21 | touch | V13_iv_scaled | 0.197163 | 0.011242 | — | 2 |
| 21 | touch | trend_blocks | 0.197704 | 0.008826 | — | 3 |
| 21 | touch | iv_scaled_blocks | 0.198752 | 0.007968 | — | 3 |
| 21 | touch | V13_empirical_exact | 0.206812 | 0.011096 | — | 1 |
| 21 | volatility | V13_GJR | 0.033179 | 0.005595 | — | 2 |
| 21 | volatility | blend_gjr_iv | 0.033780 | 0.004213 | — | 2 |
| 21 | volatility | V13_bracketed_IV | 0.039406 | 0.012788 | — | 1 |
| 21 | volatility | raw_iv | 0.039406 | 0.012788 | — | 1 |
| 21 | volatility | gjr_t_short | 0.041387 | 0.000383 | — | 2 |
| 21 | weekly_and_monthly_direction | domestic_location_gjr_scale | 0.245042 | 0.001210 | — | 2 |
| 21 | weekly_and_monthly_direction | skew_only | 0.249447 | 0.000010 | — | 2 |
| 21 | weekly_and_monthly_direction | symmetric | 0.250000 | 0.000000 | — | 1 |

[Extreme and transition ranks](transition-and-tail-leaderboard.csv) · [Full path projections](path-marginal-leaderboard.csv) · [First-hit timing and order](barrier-leaderboard.csv) · [All interval calibration](interval-calibration-leaderboard.csv) · [All matched uncertainty](matched-search-adjusted.csv).
