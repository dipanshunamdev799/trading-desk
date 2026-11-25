# V14 Stochastic And Asymmetric Volatility

The process study fits Gaussian GARCH and GJR, variance-standardized Student-t and bounded skew-t GJR, and Student-t EGARCH. GJR limits the combined persistence coefficients and changes volatility after negative shocks. EGARCH uses a bounded causal log-variance filter and plug-in multistep expectation. Exogenous GJR uses IV or India VIX with lagged predictors in the likelihood. The IV anchor moves from near to longer maturity through the forecast. A fixed hybrid gives near-term IV greater weight and gradually shifts to GJR. Other competitors include a realized-measure log-volatility Kalman filter, an IV-anchored latent variant, a filtered two-state variance model, HAR and fast/slow component risk. Each process refit shares its initial state across the five- and 21-session forecasts.

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
| 5 | combined | offshore_gap | 265 | 53 | 0.039947 | 0.053864 | 0.424555 | -0.012221 | 0.586514 |
| 5 | combined | egarch_student | 265 | 53 | 0.039960 | 0.051556 | 0.327199 | 0.010006 | 0.558812 |
| 5 | combined | gjr_skew | 265 | 53 | 0.039970 | 0.051985 | 0.363838 | -0.003229 | 0.475051 |
| 5 | combined | V13_EGARCH | 265 | 53 | 0.039975 | 0.051609 | 0.361354 | 0.003677 | 0.489534 |
| 5 | combined | intraday_har | 265 | 53 | 0.040036 | 0.052919 | 0.393189 | -0.008708 | 0.570104 |
| 5 | combined | gjr_t_perturbed | 265 | 53 | 0.040124 | 0.053553 | 0.397134 | -0.009479 | 0.473415 |
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
| 21 | combined | two_state | 217 | 11 | 0.039319 | 0.053548 | 0.319764 | -0.009237 | 0.129516 |
| 21 | combined | V13_bracketed_IV | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | combined | raw_iv | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | combined | V13_fitted_IV | 217 | 11 | 0.040178 | 0.056412 | 0.457758 | -0.029281 | 0.306180 |
| 21 | combined | v14_iv_calibrated | 217 | 11 | 0.040523 | 0.057970 | 0.579558 | -0.030193 | 0.373829 |
| 21 | combined | V13_calibrated_IV | 217 | 11 | 0.040652 | 0.058100 | 0.586417 | -0.030326 | 0.368541 |

| method | alpha | beta | gamma | xi | nu | skew | leverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| egarch_student | 0.132920 | 0.977931 | — | — | 14.051036 | 0.000000 | -0.147648 |
| garch_gauss | 0.080786 | 0.904336 | 0.000000 | 0.000000 | 8.000000 | 0.000000 | — |
| gjr_gauss | 0.019922 | 0.864915 | 0.106530 | 0.000000 | 8.000000 | 0.000000 | — |
| gjr_ivx | 0.000460 | 0.249428 | 0.230958 | 0.457272 | 18.855285 | 0.000000 | — |
| gjr_skew | 0.012937 | 0.791137 | 0.178660 | 0.000000 | 11.316892 | -0.054441 | — |
| gjr_student | 0.019653 | 0.773973 | 0.195296 | 0.000000 | 11.551857 | 0.000000 | — |
| gjr_t_short | 0.000052 | 0.849809 | 0.138261 | 0.000000 | 22.000000 | 0.000000 | — |
| gjr_vixx | 0.006660 | 0.613653 | 0.216654 | 0.100905 | 13.501429 | 0.000000 | — |
| latent_kalman | — | — | — | — | — | — | — |
| two_state | — | — | — | — | — | — | — |

| method | period | alpha | beta | gamma | xi | nu | skew | leverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| egarch_student | 2025 to June 2026 | 0.141445 | 0.976288 | — | — | 11.229921 | 0.000000 | -0.164594 |
| egarch_student | July 2026 onward | 0.062746 | 0.979586 | — | — | 22.000000 | 0.000000 | -0.146229 |
| gjr_ivx | 2025 to June 2026 | 0.000490 | 0.030389 | 0.271074 | 0.536872 | 16.405131 | 0.000000 | — |
| gjr_ivx | July 2026 onward | 0.000381 | 0.395398 | 0.125020 | 0.410766 | 22.000000 | 0.000000 | — |
| gjr_skew | 2025 to June 2026 | 0.024794 | 0.729394 | 0.229652 | 0.000000 | 10.059212 | -0.004512 | — |
| gjr_skew | July 2026 onward | 0.000040 | 0.884354 | 0.104647 | 0.000000 | 17.915608 | -0.109058 | — |
| gjr_student | 2025 to June 2026 | 0.024827 | 0.724083 | 0.242313 | 0.000000 | 11.283579 | 0.000000 | — |
| gjr_student | July 2026 onward | 0.000040 | 0.880812 | 0.108213 | 0.000000 | 16.331977 | 0.000000 | — |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | volatility | gjr_ivx | V13_GJR | mae | 265 | 53 | 0.037402 | 0.040318 | 0.002916 | -0.003588 | 0.009420 | -0.004085 | 0.009918 |
| 5 | combined | volatility | latent_iv | V13_GJR | mae | 265 | 53 | 0.037671 | 0.040318 | 0.002647 | -0.005987 | 0.011281 | -0.007550 | 0.012844 |
| 5 | combined | volatility | blend_gjr_iv | V13_GJR | mae | 265 | 53 | 0.037978 | 0.040318 | 0.002341 | -0.003197 | 0.007878 | -0.003168 | 0.007849 |
| 5 | combined | volatility | gjr_ivx | V13_raw_ATM | mae | 265 | 53 | 0.037402 | 0.037814 | 0.000412 | -0.004650 | 0.005475 | -0.005030 | 0.005854 |
| 5 | combined | volatility | egarch_student | V13_GJR | mae | 265 | 53 | 0.039960 | 0.040318 | 0.000359 | -0.008620 | 0.009338 | -0.008556 | 0.009274 |
| 5 | combined | volatility | gjr_t_perturbed | V13_GJR | mae | 265 | 53 | 0.040124 | 0.040318 | 0.000194 | -0.006110 | 0.006499 | -0.006721 | 0.007109 |
| 5 | combined | volatility | latent_iv | V13_raw_ATM | mae | 265 | 53 | 0.037671 | 0.037814 | 0.000143 | -0.008882 | 0.009168 | -0.009567 | 0.009853 |
| 5 | combined | volatility | gjr_student | V13_GJR | mae | 265 | 53 | 0.040250 | 0.040318 | 0.000069 | -0.004543 | 0.004680 | -0.004855 | 0.004992 |
| 5 | combined | volatility | blend_gjr_iv | V13_raw_ATM | mae | 265 | 53 | 0.037978 | 0.037814 | -0.000163 | -0.004328 | 0.004002 | -0.004517 | 0.004190 |
| 5 | combined | volatility | gjr_t_short | V13_GJR | mae | 265 | 53 | 0.042061 | 0.040318 | -0.001742 | -0.010470 | 0.006985 | -0.011650 | 0.008165 |
| 5 | combined | volatility | egarch_student | V13_raw_ATM | mae | 265 | 53 | 0.039960 | 0.037814 | -0.002145 | -0.009454 | 0.005164 | -0.009850 | 0.005560 |
| 5 | combined | volatility | gjr_t_perturbed | V13_raw_ATM | mae | 265 | 53 | 0.040124 | 0.037814 | -0.002310 | -0.011410 | 0.006791 | -0.010967 | 0.006348 |
| 5 | combined | volatility | gjr_student | V13_raw_ATM | mae | 265 | 53 | 0.040250 | 0.037814 | -0.002435 | -0.010520 | 0.005649 | -0.010228 | 0.005357 |
| 5 | combined | volatility | gjr_t_short | V13_raw_ATM | mae | 265 | 53 | 0.042061 | 0.037814 | -0.004246 | -0.014084 | 0.005591 | -0.014428 | 0.005935 |
| 5 | combined | volatility | blend_gjr_iv | V13_GJR | qlike | 265 | 53 | 0.287184 | 0.359870 | 0.072685 | -0.034382 | 0.179752 | -0.035286 | 0.180656 |
| 5 | combined | volatility | gjr_ivx | V13_GJR | qlike | 265 | 53 | 0.299575 | 0.359870 | 0.060295 | -0.052744 | 0.173335 | -0.060078 | 0.180669 |
| 5 | combined | volatility | latent_iv | V13_GJR | qlike | 265 | 53 | 0.322511 | 0.359870 | 0.037358 | -0.083929 | 0.158646 | -0.106950 | 0.181666 |
| 5 | combined | volatility | egarch_student | V13_GJR | qlike | 265 | 53 | 0.327199 | 0.359870 | 0.032671 | -0.047962 | 0.113304 | -0.042308 | 0.107650 |
| 5 | combined | volatility | gjr_student | V13_GJR | qlike | 265 | 53 | 0.370739 | 0.359870 | -0.010870 | -0.074753 | 0.053014 | -0.081269 | 0.059529 |
| 5 | combined | volatility | blend_gjr_iv | V13_raw_ATM | qlike | 265 | 53 | 0.287184 | 0.276187 | -0.010997 | -0.055336 | 0.033341 | -0.058418 | 0.036423 |
| 5 | combined | volatility | gjr_ivx | V13_raw_ATM | qlike | 265 | 53 | 0.299575 | 0.276187 | -0.023388 | -0.088310 | 0.041535 | -0.090693 | 0.043918 |
| 5 | combined | volatility | gjr_t_perturbed | V13_GJR | qlike | 265 | 53 | 0.397134 | 0.359870 | -0.037264 | -0.128654 | 0.054125 | -0.132459 | 0.057930 |
| 5 | combined | volatility | latent_iv | V13_raw_ATM | qlike | 265 | 53 | 0.322511 | 0.276187 | -0.046324 | -0.160113 | 0.067464 | -0.164947 | 0.072298 |
| 5 | combined | volatility | egarch_student | V13_raw_ATM | qlike | 265 | 53 | 0.327199 | 0.276187 | -0.051012 | -0.176530 | 0.074507 | -0.185792 | 0.083768 |
| 5 | combined | volatility | gjr_t_short | V13_GJR | qlike | 265 | 53 | 0.411713 | 0.359870 | -0.051843 | -0.198462 | 0.094775 | -0.205762 | 0.102076 |
| 5 | combined | volatility | gjr_student | V13_raw_ATM | qlike | 265 | 53 | 0.370739 | 0.276187 | -0.094552 | -0.249716 | 0.060611 | -0.247612 | 0.058508 |
| 5 | combined | volatility | gjr_t_perturbed | V13_raw_ATM | qlike | 265 | 53 | 0.397134 | 0.276187 | -0.120947 | -0.312160 | 0.070266 | -0.303257 | 0.061363 |
| 5 | combined | volatility | gjr_t_short | V13_raw_ATM | qlike | 265 | 53 | 0.411713 | 0.276187 | -0.135526 | -0.360334 | 0.089282 | -0.358493 | 0.087440 |
| 21 | combined | volatility | blend_gjr_iv | V13_bracketed_IV | mae | 217 | 11 | 0.033780 | 0.039406 | 0.005626 | -0.005548 | 0.016801 | -0.008300 | 0.019553 |
| 21 | combined | volatility | gjr_student | V13_bracketed_IV | mae | 217 | 11 | 0.035464 | 0.039406 | 0.003942 | -0.007503 | 0.015388 | -0.009762 | 0.017646 |
| 21 | combined | volatility | egarch_student | V13_bracketed_IV | mae | 217 | 11 | 0.035730 | 0.039406 | 0.003677 | -0.004172 | 0.011525 | -0.005675 | 0.013029 |
| 21 | combined | volatility | gjr_ivx | V13_bracketed_IV | mae | 217 | 11 | 0.037160 | 0.039406 | 0.002246 | -0.004798 | 0.009289 | -0.006952 | 0.011444 |
| 21 | combined | volatility | blend_gjr_iv | V13_GJR | mae | 217 | 11 | 0.033780 | 0.033179 | -0.000601 | -0.006422 | 0.005220 | -0.007932 | 0.006731 |
| 21 | combined | volatility | gjr_t_short | V13_bracketed_IV | mae | 217 | 11 | 0.041387 | 0.039406 | -0.001981 | -0.015858 | 0.011897 | -0.019149 | 0.015188 |
| 21 | combined | volatility | gjr_student | V13_GJR | mae | 217 | 11 | 0.035464 | 0.033179 | -0.002285 | -0.008415 | 0.003845 | -0.009941 | 0.005371 |
| 21 | combined | volatility | egarch_student | V13_GJR | mae | 217 | 11 | 0.035730 | 0.033179 | -0.002550 | -0.015210 | 0.010109 | -0.017341 | 0.012240 |
| 21 | combined | volatility | gjr_t_perturbed | V13_bracketed_IV | mae | 217 | 11 | 0.043344 | 0.039406 | -0.003938 | -0.017762 | 0.009887 | -0.020583 | 0.012707 |
| 21 | combined | volatility | gjr_ivx | V13_GJR | mae | 217 | 11 | 0.037160 | 0.033179 | -0.003981 | -0.013102 | 0.005139 | -0.014425 | 0.006463 |
| 21 | combined | volatility | gjr_t_short | V13_GJR | mae | 217 | 11 | 0.041387 | 0.033179 | -0.008208 | -0.020846 | 0.004430 | -0.023776 | 0.007361 |
| 21 | combined | volatility | latent_iv | V13_bracketed_IV | mae | 217 | 11 | 0.047729 | 0.039406 | -0.008322 | -0.025995 | 0.009351 | -0.029511 | 0.012866 |
| 21 | combined | volatility | gjr_t_perturbed | V13_GJR | mae | 217 | 11 | 0.043344 | 0.033179 | -0.010165 | -0.023593 | 0.003263 | -0.027213 | 0.006883 |
| 21 | combined | volatility | latent_iv | V13_GJR | mae | 217 | 11 | 0.047729 | 0.033179 | -0.014549 | -0.031314 | 0.002215 | -0.034921 | 0.005822 |
| 21 | combined | volatility | egarch_student | V13_bracketed_IV | qlike | 217 | 11 | 0.207684 | 0.267623 | 0.059939 | -0.081364 | 0.201242 | -0.112925 | 0.232803 |
| 21 | combined | volatility | blend_gjr_iv | V13_bracketed_IV | qlike | 217 | 11 | 0.247374 | 0.267623 | 0.020249 | -0.066539 | 0.107036 | -0.070012 | 0.110510 |
| 21 | combined | volatility | gjr_student | V13_bracketed_IV | qlike | 217 | 11 | 0.263397 | 0.267623 | 0.004226 | -0.116633 | 0.125084 | -0.115610 | 0.124061 |
| 21 | combined | volatility | egarch_student | V13_GJR | qlike | 217 | 11 | 0.207684 | 0.199677 | -0.008007 | -0.109479 | 0.093464 | -0.115754 | 0.099740 |
| 21 | combined | volatility | gjr_ivx | V13_bracketed_IV | qlike | 217 | 11 | 0.310001 | 0.267623 | -0.042378 | -0.126693 | 0.041937 | -0.149942 | 0.065186 |
| 21 | combined | volatility | blend_gjr_iv | V13_GJR | qlike | 217 | 11 | 0.247374 | 0.199677 | -0.047697 | -0.152711 | 0.057316 | -0.179562 | 0.084168 |
| 21 | combined | volatility | gjr_student | V13_GJR | qlike | 217 | 11 | 0.263397 | 0.199677 | -0.063720 | -0.177700 | 0.050259 | -0.209615 | 0.082174 |
| 21 | combined | volatility | gjr_ivx | V13_GJR | qlike | 217 | 11 | 0.310001 | 0.199677 | -0.110324 | -0.313322 | 0.092674 | -0.349735 | 0.129087 |
| 21 | combined | volatility | gjr_t_short | V13_bracketed_IV | qlike | 217 | 11 | 0.407741 | 0.267623 | -0.140118 | -0.328002 | 0.047766 | -0.358622 | 0.078386 |
| 21 | combined | volatility | gjr_t_short | V13_GJR | qlike | 217 | 11 | 0.407741 | 0.199677 | -0.208064 | -0.459222 | 0.043094 | -0.525597 | 0.109468 |
| 21 | combined | volatility | gjr_t_perturbed | V13_bracketed_IV | qlike | 217 | 11 | 0.476011 | 0.267623 | -0.208388 | -0.463971 | 0.047194 | -0.524681 | 0.107905 |
| 21 | combined | volatility | gjr_t_perturbed | V13_GJR | qlike | 217 | 11 | 0.476011 | 0.199677 | -0.276334 | -0.598316 | 0.045647 | -0.695887 | 0.143219 |
| 21 | combined | volatility | latent_iv | V13_bracketed_IV | qlike | 217 | 11 | 0.714432 | 0.267623 | -0.446809 | -0.842252 | -0.051366 | -0.943300 | 0.049682 |
| 21 | combined | volatility | latent_iv | V13_GJR | qlike | 217 | 11 | 0.714432 | 0.199677 | -0.514755 | -0.988101 | -0.041409 | -1.109009 | 0.079500 |

[Process coefficients and optimizer status](process-fits.json) · [Per-origin variance curves](process-states.json) · [Original GJR model](https://doi.org/10.1111/j.1540-6261.1993.tb05128.x) · [Hansen skewed Student-t density](https://users.ssc.wisc.edu/~behansen/papers/ier_94.pdf).
