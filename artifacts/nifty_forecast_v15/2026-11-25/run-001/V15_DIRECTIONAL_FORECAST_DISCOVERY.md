# V15 directional and return-distribution discovery

Original five- and 21-session issue performance is evaluated separately from updates. The reference table keeps V8 residualized rotation, V11 official breadth, V12 phase-zero risk rescaling, V13 all-phase IV mixtures, V14 weekly probability shrinkage, V14 domestic location plus GJR dispersion, and neutral/historical controls. Archived earlier relationships are compared on the common origin dates specific to each reference, so historical availability and subset sizes remain visible. V15 tests pure location replacement at fixed IV, pure fitted-risk scale at zero drift, scale plus trained location, moment-matched empirical asymmetry, a conditional sign-and-magnitude law, and probability shrinkage. Those pieces estimate different features of a forecast.

## Issue-time endpoints across vintages

| horizon | version | model | origins | p up | brier | log loss | endpoint crps | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | Protected reference systems | V8_R_RESIDUAL | 92 | 0.485074 | 0.159504 | 0.499670 | 0.009852 | 0.809869 |
| 5 | Protected reference systems | V8_W_STRUCT_EMBARGO_EQ | 92 | 0.509722 | 0.161638 | 0.501592 | 0.009262 | 0.781567 |
| 5 | Protected reference systems | V14_sign_shrinkage | 265 | 0.517051 | 0.228529 | 0.648943 | 0.010457 | 0.636001 |
| 5 | Protected reference systems | V13_IV_all_phase | 265 | 0.524469 | 0.229587 | 0.651757 | 0.010609 | 0.636001 |
| 5 | Protected reference systems | V12_NATIVE_RV | 265 | 0.525530 | 0.229715 | 0.655524 | 0.010896 | 0.633316 |
| 5 | Protected reference systems | J11_BREADTH_ALL | 265 | 0.525444 | 0.236138 | 0.667636 | 0.010960 | 0.650612 |
| 5 | Protected reference systems | V13_weekly_CRPS | 265 | 0.529872 | 0.236495 | 0.665957 | 0.010472 | 0.644751 |
| 5 | Protected reference systems | J11_EXCLUDE_B_ROT | 265 | 0.535208 | 0.244333 | 0.682878 | 0.010777 | 0.602218 |
| 5 | Protected reference systems | B_CHANGE | 265 | 0.537374 | 0.246747 | 0.696972 | 0.011869 | 0.610765 |
| 5 | Protected reference systems | NEUTRAL | 265 | 0.500000 | 0.250000 | 0.693147 | 0.011058 | 0.488190 |
| 5 | Protected reference systems | V13_IV_symmetric | 265 | 0.500000 | 0.250000 | 0.693147 | 0.010817 | 0.500000 |
| 5 | V15 joint laws | full_noise | 265 | 0.501636 | 0.246351 | 0.686255 | 0.010926 | 0.589888 |
| 5 | V15 joint laws | full | 265 | 0.500531 | 0.247450 | 0.688854 | 0.010985 | 0.571206 |
| 5 | V15 joint laws | full_delayed | 265 | 0.500531 | 0.247450 | 0.688854 | 0.010985 | 0.571206 |
| 5 | V15 joint laws | full_stale_global | 265 | 0.500531 | 0.247450 | 0.688854 | 0.010985 | 0.571206 |
| 5 | V15 joint laws | full_stale_surface | 265 | 0.500531 | 0.247450 | 0.688854 | 0.010985 | 0.571206 |
| 21 | Protected reference systems | V14_domestic_GJR | 217 | 0.481432 | 0.245042 | 0.683095 | 0.024989 | 0.502675 |
| 21 | Protected reference systems | NEUTRAL | 217 | 0.500000 | 0.250000 | 0.693147 | 0.025420 | 0.460742 |
| 21 | Protected reference systems | V13_IV_symmetric | 217 | 0.500000 | 0.250000 | 0.693147 | 0.025220 | 0.500000 |
| 21 | Protected reference systems | V14_regime_state_joint | 217 | 0.501895 | 0.250994 | 0.695137 | 0.024750 | 0.489129 |
| 21 | Protected reference systems | V8_R_RESIDUAL | 76 | 0.583850 | 0.257806 | 0.712817 | 0.030146 | 0.587097 |
| 21 | Protected reference systems | V13_IV_all_phase | 217 | 0.549674 | 0.284302 | 0.774921 | 0.028227 | 0.499569 |
| 21 | Protected reference systems | V13_weekly_CRPS | 217 | 0.588935 | 0.288318 | 0.779408 | 0.027282 | 0.526445 |
| 21 | Protected reference systems | J11_BREADTH_ALL | 217 | 0.586752 | 0.299436 | 0.812371 | 0.031283 | 0.480285 |
| 21 | Protected reference systems | J11_EXCLUDE_B_ROT | 217 | 0.628724 | 0.306090 | 0.831132 | 0.028994 | 0.536411 |
| 21 | Protected reference systems | B_CHANGE | 217 | 0.623339 | 0.332742 | 0.939315 | 0.032497 | 0.516566 |
| 21 | Protected reference systems | V12_NATIVE_RV | 217 | 0.566496 | 0.363025 | 0.974514 | 0.032602 | 0.349310 |
| 21 | V15 joint laws | heavy_tail | 217 | 0.500288 | 0.247524 | 0.688176 | 0.025020 | 0.548835 |
| 21 | V15 joint laws | incremental | 217 | 0.500198 | 0.247623 | 0.688373 | 0.024840 | 0.544737 |
| 21 | V15 joint laws | iv_restart | 217 | 0.500486 | 0.247721 | 0.688575 | 0.025027 | 0.537144 |
| 21 | V15 joint laws | price_only | 217 | 0.500486 | 0.247721 | 0.688575 | 0.025027 | 0.537144 |
| 21 | V15 joint laws | shock_persistence | 217 | 0.500486 | 0.247721 | 0.688575 | 0.025027 | 0.537144 |

## Issue-time mechanism decomposition

| horizon | model | n | p | brier | log loss | crps | pinball |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | common_raw_iv | 265 | 0.502712 | 0.248408 | 0.689963 | 0.010682 | 0.004362 |
| 5 | fitted_risk_without_drift | 265 | 0.502712 | 0.248408 | 0.689963 | 0.010683 | 0.004364 |
| 5 | tail_t6_mixture | 265 | 0.503007 | 0.248471 | 0.690094 | 0.010686 | 0.004364 |
| 5 | episode_tails | 265 | 0.499558 | 0.248903 | 0.690931 | 0.010725 | 0.004377 |
| 5 | state_risk_only | 265 | 0.520740 | 0.250763 | 0.694695 | 0.010922 | 0.004493 |
| 5 | location_plus_risk | 265 | 0.479481 | 0.250765 | 0.696154 | 0.011120 | 0.004531 |
| 5 | empirical_sign_magnitude | 265 | 0.486144 | 0.250858 | 0.695003 | 0.010960 | 0.004488 |
| 5 | risk_matched_asymmetry | 265 | 0.479452 | 0.251090 | 0.696186 | 0.011119 | 0.004527 |
| 5 | location_at_raw_iv | 265 | 0.479142 | 0.251896 | 0.698574 | 0.011152 | 0.004557 |
| 5 | analogue_asymmetry | 265 | 0.497877 | 0.255993 | 0.705383 | 0.011121 | 0.004606 |
| 21 | tail_t6_mixture | 217 | 0.500288 | 0.247524 | 0.688176 | 0.025020 | 0.010580 |
| 21 | common_raw_iv | 217 | 0.500486 | 0.247721 | 0.688575 | 0.025027 | 0.010586 |
| 21 | fitted_risk_without_drift | 217 | 0.500486 | 0.247721 | 0.688575 | 0.025197 | 0.010706 |
| 21 | state_risk_only | 217 | 0.528586 | 0.251376 | 0.695900 | 0.024694 | 0.010262 |
| 21 | location_at_raw_iv | 217 | 0.447563 | 0.252494 | 0.698057 | 0.026714 | 0.011244 |
| 21 | episode_tails | 217 | 0.523185 | 0.254765 | 0.702819 | 0.025272 | 0.010677 |
| 21 | location_plus_risk | 217 | 0.454079 | 0.255166 | 0.703960 | 0.026910 | 0.011373 |
| 21 | empirical_sign_magnitude | 217 | 0.490171 | 0.257477 | 0.708475 | 0.026051 | 0.011212 |
| 21 | risk_matched_asymmetry | 217 | 0.532060 | 0.262026 | 0.720072 | 0.026502 | 0.011434 |
| 21 | analogue_asymmetry | 217 | 0.617007 | 0.303891 | 0.811996 | 0.027264 | 0.011819 |

## Standalone probability shrinkage

| horizon | checkpoint | model | n | brier | log loss |
| --- | --- | --- | --- | --- | --- |
| 5 | 0 | bounded_domestic_probability | 265 | 0.250474 | 0.695361 |
| 5 | 1 | bounded_domestic_probability | 265 | 0.217616 | 0.623192 |
| 5 | 4 | bounded_domestic_probability | 265 | 0.095475 | 0.301035 |
| 5 | 0 | domestic_probability | 265 | 0.250765 | 0.696154 |
| 5 | 1 | domestic_probability | 265 | 0.217839 | 0.623650 |
| 5 | 4 | domestic_probability | 265 | 0.095831 | 0.307230 |
| 5 | 0 | historical_prior_mix | 265 | 0.250827 | 0.695551 |
| 5 | 1 | historical_prior_mix | 265 | 0.218905 | 0.626082 |
| 5 | 4 | historical_prior_mix | 265 | 0.095772 | 0.299497 |
| 5 | 0 | raw_probability | 265 | 0.248408 | 0.689963 |
| 5 | 1 | raw_probability | 265 | 0.222898 | 0.633063 |
| 5 | 4 | raw_probability | 265 | 0.097811 | 0.308124 |
| 5 | 0 | sign_shrink_half | 265 | 0.248113 | 0.689511 |
| 5 | 1 | sign_shrink_half | 265 | 0.219192 | 0.625435 |
| 5 | 4 | sign_shrink_half | 265 | 0.096189 | 0.303401 |
| 21 | 0 | bounded_domestic_probability | 217 | 0.254427 | 0.702355 |
| 21 | 1 | bounded_domestic_probability | 217 | 0.250819 | 0.699692 |
| 21 | 20 | bounded_domestic_probability | 217 | 0.043662 | 0.146892 |
| 21 | 0 | domestic_probability | 217 | 0.255166 | 0.703960 |
| 21 | 1 | domestic_probability | 217 | 0.251585 | 0.702499 |
| 21 | 20 | domestic_probability | 217 | 0.043576 | 0.132657 |
| 21 | 0 | historical_prior_mix | 217 | 0.257832 | 0.709272 |
| 21 | 1 | historical_prior_mix | 217 | 0.253170 | 0.707441 |
| 21 | 20 | historical_prior_mix | 217 | 0.043868 | 0.135441 |
| 21 | 0 | raw_probability | 217 | 0.247721 | 0.688575 |
| 21 | 1 | raw_probability | 217 | 0.241767 | 0.677024 |
| 21 | 20 | raw_probability | 217 | 0.044056 | 0.137864 |
| 21 | 0 | sign_shrink_half | 217 | 0.248006 | 0.689094 |
| 21 | 1 | sign_shrink_half | 217 | 0.243364 | 0.681955 |
| 21 | 20 | sign_shrink_half | 217 | 0.043527 | 0.134339 |

## Updated whole and remaining endpoint scores

| horizon | checkpoint | model | n | brier | endpoint crps | remaining brier | remaining return crps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 1 | full | 265 | 0.217210 | 0.009657 | 0.250015 | 0.009647 |
| 5 | 1 | gjr_restart | 265 | 0.228304 | 0.009666 | 0.252144 | 0.009652 |
| 5 | 1 | incremental | 265 | 0.223657 | 0.009496 | 0.251124 | 0.009483 |
| 5 | 1 | iv_restart | 265 | 0.222898 | 0.009471 | 0.250734 | 0.009458 |
| 5 | 1 | price_only | 265 | 0.222718 | 0.009457 | 0.250734 | 0.009445 |
| 5 | 2 | full | 265 | 0.182023 | 0.008487 | 0.251653 | 0.008472 |
| 5 | 2 | gjr_restart | 265 | 0.186700 | 0.008436 | 0.251830 | 0.008417 |
| 5 | 2 | incremental | 265 | 0.182627 | 0.008296 | 0.250484 | 0.008279 |
| 5 | 2 | iv_restart | 265 | 0.182228 | 0.008280 | 0.250446 | 0.008263 |
| 5 | 2 | price_only | 265 | 0.181173 | 0.008285 | 0.250446 | 0.008269 |
| 5 | 3 | full | 265 | 0.148947 | 0.006946 | 0.263043 | 0.006938 |
| 5 | 3 | gjr_restart | 265 | 0.148805 | 0.006720 | 0.248840 | 0.006711 |
| 5 | 3 | incremental | 265 | 0.146173 | 0.006643 | 0.247216 | 0.006637 |
| 5 | 3 | iv_restart | 265 | 0.145588 | 0.006652 | 0.247771 | 0.006645 |
| 5 | 3 | price_only | 265 | 0.145114 | 0.006644 | 0.247786 | 0.006638 |
| 5 | 4 | full | 265 | 0.096578 | 0.004892 | 0.260801 | 0.004890 |
| 5 | 4 | gjr_restart | 265 | 0.097863 | 0.004682 | 0.247597 | 0.004678 |
| 5 | 4 | incremental | 265 | 0.097668 | 0.004648 | 0.247535 | 0.004645 |
| 5 | 4 | iv_restart | 265 | 0.097811 | 0.004655 | 0.247583 | 0.004652 |
| 5 | 4 | price_only | 265 | 0.097616 | 0.004679 | 0.247568 | 0.004677 |
| 21 | 1 | full | 217 | 0.255090 | 0.026849 | 0.266132 | 0.026866 |
| 21 | 1 | gjr_restart | 217 | 0.241962 | 0.024220 | 0.250368 | 0.024239 |
| 21 | 1 | incremental | 217 | 0.240118 | 0.024397 | 0.247559 | 0.024418 |
| 21 | 1 | iv_restart | 217 | 0.241767 | 0.024591 | 0.248577 | 0.024610 |
| 21 | 1 | price_only | 217 | 0.241733 | 0.024638 | 0.248577 | 0.024657 |
| 21 | 5 | full | 217 | 0.235624 | 0.024892 | 0.268800 | 0.025012 |
| 21 | 5 | gjr_restart | 217 | 0.221244 | 0.022025 | 0.249470 | 0.022132 |
| 21 | 5 | incremental | 217 | 0.222079 | 0.022184 | 0.252080 | 0.022284 |
| 21 | 5 | iv_restart | 217 | 0.218092 | 0.022203 | 0.249491 | 0.022306 |
| 21 | 5 | price_only | 217 | 0.218198 | 0.022524 | 0.249491 | 0.022625 |
| 21 | 10 | full | 217 | 0.187909 | 0.020933 | 0.263611 | 0.021191 |
| 21 | 10 | gjr_restart | 217 | 0.178601 | 0.018725 | 0.251429 | 0.018919 |
| 21 | 10 | incremental | 217 | 0.176964 | 0.018645 | 0.251576 | 0.018818 |
| 21 | 10 | iv_restart | 217 | 0.173269 | 0.018509 | 0.246323 | 0.018689 |
| 21 | 10 | price_only | 217 | 0.174910 | 0.019132 | 0.246358 | 0.019316 |
| 21 | 15 | full | 217 | 0.142165 | 0.014016 | 0.256882 | 0.014190 |
| 21 | 15 | gjr_restart | 217 | 0.137542 | 0.013367 | 0.258755 | 0.013505 |
| 21 | 15 | incremental | 217 | 0.134905 | 0.013046 | 0.253560 | 0.013175 |
| 21 | 15 | iv_restart | 217 | 0.132261 | 0.013080 | 0.253138 | 0.013213 |
| 21 | 15 | price_only | 217 | 0.133400 | 0.013511 | 0.253138 | 0.013648 |
| 21 | 20 | full | 217 | 0.045719 | 0.005178 | 0.253003 | 0.005268 |
| 21 | 20 | gjr_restart | 217 | 0.044799 | 0.005039 | 0.247928 | 0.005123 |
| 21 | 20 | incremental | 217 | 0.043511 | 0.005006 | 0.248610 | 0.005089 |
| 21 | 20 | iv_restart | 217 | 0.044056 | 0.005016 | 0.247910 | 0.005097 |
| 21 | 20 | price_only | 217 | 0.043775 | 0.005239 | 0.247892 | 0.005333 |

When the realized price moves far from S₀, the original-window final sign often becomes easier for every model. The remaining direction Brier and CRPS isolate the unresolved component around Sₜ. Under a price-anchored sign threshold, dispersion and asymmetry can change probabilities even when the mean remains similar. The exact neutral, zero-return, and price-only rows serve different purposes and retain individual score columns.

[All original references on common origins](cross-vintage-endpoint-leaderboard.csv) [All endpoint mechanism forecasts](endpoint-mechanism-scores.csv.gz) [Search-adjusted issue comparisons](cross-vintage-matched-uncertainty.csv) [Same-time remaining-return comparisons](matched-window-evidence.csv)
