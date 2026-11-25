# V14 Risk Informed Endpoint Forecasting

Endpoints retain the original V13 weekly direction and distribution leaders and the mandatory monthly symmetric forecast. The standalones separately change location, dispersion, skew, sign mass and tail shape. Pure shape changes preserve the archived mean and variance. The normalized-target regression uses training-only breadth, rotation and IV interactions. A sign-and-magnitude law predicts sign separately and attaches upstream matured magnitudes. GJR changes the confidence scale of structural laws and also generates its own joint endpoints.

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
| 5 | combined | V12_week_CRPS | 265 | 53 | 0.241437 | 0.676126 | 0.622642 | 0.637994 | 0.010677 | 0.014897 | 0.803774 | 0.043636 |
| 5 | combined | sign_magnitude_hybrid | 265 | 53 | 0.244268 | 0.684742 | 0.615094 | 0.616915 | 0.010994 | 0.015042 | 0.773585 | 0.043266 |
| 5 | combined | V11_later_Brier | 265 | 53 | 0.246747 | 0.696972 | 0.596226 | 0.610765 | 0.011869 | 0.016103 | 0.758491 | 0.042534 |
| 5 | combined | trend_shrink | 265 | 53 | 0.247349 | 0.687842 | 0.588679 | 0.569098 | 0.010703 | 0.015013 | 0.807547 | 0.047527 |
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
| 21 | combined | symmetric | 217 | 11 | 0.250000 | 0.693147 | 0.511521 | 0.460742 | 0.025420 | 0.033371 | 0.635945 | 0.068179 |
| 21 | combined | calibrated_iv | 217 | 11 | 0.250053 | 0.693253 | 0.516129 | 0.503279 | 0.025363 | 0.033288 | 0.709677 | 0.088171 |
| 21 | combined | constant_iv | 217 | 11 | 0.250062 | 0.693271 | 0.516129 | 0.503279 | 0.025281 | 0.033258 | 0.741935 | 0.100155 |
| 21 | combined | widened_gauss | 217 | 11 | 0.250066 | 0.693280 | 0.516129 | 0.503279 | 0.025441 | 0.033220 | 0.778802 | 0.118213 |

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
| 5 | combined | constant_iv | 265 | 53 | 0.250818 | 0.694783 | 0.430189 | 0.429891 | 0.010734 | 0.015086 | 0.807547 | 0.047585 |
| 5 | combined | trend_persistent | 265 | 53 | 0.248223 | 0.689580 | 0.554717 | 0.548539 | 0.010750 | 0.015017 | 0.777358 | 0.043320 |
| 5 | combined | separate_gap | 265 | 53 | 0.251211 | 0.695573 | 0.475472 | 0.521454 | 0.010768 | 0.015063 | 0.769811 | 0.042872 |
| 5 | combined | gjr_iv | 265 | 53 | 0.252084 | 0.697321 | 0.479245 | 0.523937 | 0.010771 | 0.015079 | 0.777358 | 0.043639 |
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
| 21 | combined | jump_no_episode | 217 | 11 | 0.250996 | 0.695143 | 0.483871 | 0.521182 | 0.025070 | 0.033357 | 0.741935 | 0.089701 |
| 21 | combined | jump_diffusion | 217 | 11 | 0.251135 | 0.695420 | 0.470046 | 0.506557 | 0.025071 | 0.033357 | 0.746544 | 0.089727 |
| 21 | combined | jump_1m | 217 | 11 | 0.251042 | 0.695234 | 0.479263 | 0.517084 | 0.025072 | 0.033359 | 0.746544 | 0.089680 |
| 21 | combined | gjr_dispersion_only | 217 | 11 | 0.250000 | 0.693147 | 0.437788 | 0.500000 | 0.025077 | 0.033371 | 0.631336 | 0.071794 |

| horizon | model | location_delta | width_delta | p_delta | lower_tail_mass | upper_tail_mass |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | domestic_location_gjr_scale | -0.000901 | -0.001169 | -0.029385 | 0.083166 | 0.085341 |
| 5 | domestic_location_only | -0.000901 | -0.000000 | -0.022759 | 0.093912 | 0.094037 |
| 5 | gjr_dispersion_only | 0.000000 | -0.001169 | -0.007171 | 0.084375 | 0.100523 |
| 5 | hybrid_gjr_group | 0.000444 | -0.000012 | 0.002307 | 0.067106 | 0.087426 |
| 5 | sign_magnitude_hybrid | -0.001794 | -0.001185 | -0.020562 | 0.086120 | 0.060562 |
| 5 | sign_shrinkage | -0.000059 | 0.000347 | -0.007308 | 0.089066 | 0.105309 |
| 5 | skew_only | -0.000000 | 0.000000 | 0.002447 | 0.094037 | 0.108409 |
| 5 | student_tail_only | -0.000000 | -0.000000 | 0.002975 | 0.093227 | 0.107158 |
| 21 | domestic_location_gjr_scale | -0.001041 | -0.002816 | -0.018568 | 0.180651 | 0.163252 |
| 21 | domestic_location_only | -0.001041 | 0.000000 | -0.014869 | 0.193413 | 0.177653 |
| 21 | gjr_dispersion_only | -0.000000 | -0.002816 | 0.000000 | 0.171128 | 0.171128 |
| 21 | hybrid_gjr_group | 0.000000 | -0.001971 | 0.000000 | 0.176060 | 0.176060 |
| 21 | sign_magnitude_hybrid | -0.006329 | -0.002539 | 0.030591 | 0.203747 | 0.124537 |
| 21 | sign_shrinkage | 0.000000 | -0.000000 | 0.000000 | 0.184440 | 0.184440 |
| 21 | skew_only | 0.000000 | -0.000000 | 0.007840 | 0.184035 | 0.184962 |
| 21 | student_tail_only | -0.000000 | -0.000000 | 0.000000 | 0.188645 | 0.188645 |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | endpoint_return | sign_shrinkage | symmetric | brier | 265 | 53 | 0.228529 | 0.250000 | 0.021471 | -0.009076 | 0.052018 | -0.011083 | 0.054025 |
| 5 | combined | endpoint_return | domestic_location_only | symmetric | brier | 265 | 53 | 0.228761 | 0.250000 | 0.021239 | -0.019055 | 0.061533 | -0.023590 | 0.066069 |
| 5 | combined | endpoint_return | skew_only | symmetric | brier | 265 | 53 | 0.230260 | 0.250000 | 0.019740 | -0.023801 | 0.063281 | -0.027413 | 0.066894 |
| 5 | combined | endpoint_return | student_tail_only | symmetric | brier | 265 | 53 | 0.230937 | 0.250000 | 0.019063 | -0.025627 | 0.063753 | -0.028941 | 0.067068 |
| 5 | combined | endpoint_return | domestic_location_gjr_scale | symmetric | brier | 265 | 53 | 0.231450 | 0.250000 | 0.018550 | -0.026799 | 0.063899 | -0.031764 | 0.068864 |
| 5 | combined | endpoint_return | gjr_dispersion_only | symmetric | brier | 265 | 53 | 0.233757 | 0.250000 | 0.016243 | -0.032620 | 0.065105 | -0.036354 | 0.068839 |
| 5 | combined | endpoint_return | hybrid_gjr_group | symmetric | brier | 265 | 53 | 0.235874 | 0.250000 | 0.014126 | -0.017406 | 0.045659 | -0.018970 | 0.047222 |
| 5 | combined | endpoint_return | sign_magnitude_hybrid | symmetric | brier | 265 | 53 | 0.244268 | 0.250000 | 0.005732 | -0.038378 | 0.049843 | -0.044658 | 0.056122 |
| 5 | combined | endpoint_return | sign_shrinkage | V13_week_Brier | brier | 265 | 53 | 0.228529 | 0.229587 | 0.001058 | -0.012781 | 0.014896 | -0.014447 | 0.016563 |
| 5 | combined | endpoint_return | domestic_location_only | V13_week_Brier | brier | 265 | 53 | 0.228761 | 0.229587 | 0.000826 | -0.011446 | 0.013097 | -0.010004 | 0.011656 |
| 5 | combined | endpoint_return | skew_only | V13_week_Brier | brier | 265 | 53 | 0.230260 | 0.229587 | -0.000673 | -0.002719 | 0.001373 | -0.002868 | 0.001522 |
| 5 | combined | endpoint_return | student_tail_only | V13_week_Brier | brier | 265 | 53 | 0.230937 | 0.229587 | -0.001350 | -0.002920 | 0.000220 | -0.002894 | 0.000194 |
| 5 | combined | endpoint_return | domestic_location_gjr_scale | V13_week_Brier | brier | 265 | 53 | 0.231450 | 0.229587 | -0.001864 | -0.018400 | 0.014673 | -0.017588 | 0.013861 |
| 5 | combined | endpoint_return | gjr_dispersion_only | V13_week_Brier | brier | 265 | 53 | 0.233757 | 0.229587 | -0.004171 | -0.013336 | 0.004995 | -0.013322 | 0.004980 |
| 5 | combined | endpoint_return | hybrid_gjr_group | V13_week_Brier | brier | 265 | 53 | 0.235874 | 0.229587 | -0.006287 | -0.025561 | 0.012987 | -0.027721 | 0.015147 |
| 5 | combined | endpoint_return | sign_magnitude_hybrid | V13_week_Brier | brier | 265 | 53 | 0.244268 | 0.229587 | -0.014681 | -0.038467 | 0.009104 | -0.038173 | 0.008811 |
| 21 | combined | endpoint_return | domestic_location_gjr_scale | symmetric | brier | 217 | 11 | 0.245042 | 0.250000 | 0.004958 | -0.013938 | 0.023854 | -0.018170 | 0.028086 |
| 21 | combined | endpoint_return | sign_magnitude_hybrid | symmetric | brier | 217 | 11 | 0.246277 | 0.250000 | 0.003723 | -0.039217 | 0.046662 | -0.047654 | 0.055099 |
| 21 | combined | endpoint_return | domestic_location_only | symmetric | brier | 217 | 11 | 0.246806 | 0.250000 | 0.003194 | -0.013644 | 0.020032 | -0.017200 | 0.023589 |
| 21 | combined | endpoint_return | skew_only | symmetric | brier | 217 | 11 | 0.249447 | 0.250000 | 0.000553 | -0.004238 | 0.005345 | -0.004028 | 0.005135 |
| 21 | combined | endpoint_return | gjr_dispersion_only | symmetric | brier | 217 | 11 | 0.250000 | 0.250000 | -0.000000 | -0.000000 | 0.000000 | -0.000000 | 0.000000 |
| 21 | combined | endpoint_return | hybrid_gjr_group | symmetric | brier | 217 | 11 | 0.250000 | 0.250000 | -0.000000 | -0.000000 | 0.000000 | -0.000000 | 0.000000 |
| 21 | combined | endpoint_return | sign_shrinkage | symmetric | brier | 217 | 11 | 0.250000 | 0.250000 | -0.000000 | -0.000000 | 0.000000 | -0.000000 | 0.000000 |
| 21 | combined | endpoint_return | student_tail_only | symmetric | brier | 217 | 11 | 0.250000 | 0.250000 | -0.000000 | -0.000000 | 0.000000 | -0.000000 | 0.000000 |

[Matched changes to archived location, spread and positive mass](endpoint-components.csv) · [Model fits](endpoint-fits.json) · [Standalone endpoint probability laws](standalone-endpoint-laws.npz) · [Frozen benchmark rows](benchmark-endpoint-origins.csv).
