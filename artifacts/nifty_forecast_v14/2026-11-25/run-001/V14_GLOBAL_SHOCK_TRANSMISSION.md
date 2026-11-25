# V14 Global Shock Transmission

The global mechanism uses foreign risk as a predictor for the next NIFTY opening gap, horizon overnight risk and the interaction between foreign shocks and weak local participation. Verified earlier dates feed VIX, Nasdaq volatility, U.S. and Asian equity moves, currency and oil risk, the dated gold ETF proxy, interest-rate changes and global dispersion. Each known observation precedes the historical decision cutoff under conservative availability rules.

| horizon | model | cohort | n | disjoint | prediction_rows | ess | mae | brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | opening_gap_domestic | combined | 265 | 53 | 265 | 49.381274 | 0.002679 | 0.254334 |
| 5 | opening_gap_offshore | combined | 265 | 53 | 265 | 49.381274 | 0.002693 | 0.251982 |
| 21 | opening_gap_domestic | combined | 217 | 11 | 217 | 43.171602 | 0.002994 | 0.267577 |
| 21 | opening_gap_offshore | combined | 217 | 11 | 217 | 43.171602 | 0.002986 | 0.264465 |
| 5 | opening_gap_domestic | early | 173 | 35 | 173 | 32.382462 | 0.003037 | 0.257910 |
| 5 | opening_gap_offshore | early | 173 | 35 | 173 | 32.382462 | 0.003029 | 0.259056 |
| 21 | opening_gap_domestic | early | 141 | 7 | 141 | 108.057455 | 0.003596 | 0.277083 |
| 21 | opening_gap_offshore | early | 141 | 7 | 141 | 108.057455 | 0.003562 | 0.273657 |
| 5 | opening_gap_domestic | later | 92 | 19 | 92 | 92.000000 | 0.002006 | 0.247609 |
| 5 | opening_gap_offshore | later | 92 | 19 | 92 | 92.000000 | 0.002061 | 0.238681 |
| 21 | opening_gap_domestic | later | 76 | 4 | 76 | 68.578636 | 0.001876 | 0.249940 |
| 21 | opening_gap_offshore | later | 76 | 4 | 76 | 68.578636 | 0.001919 | 0.247411 |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | next_gap | opening_gap_offshore | opening_gap_domestic | brier | 265 | 53 | 0.251982 | 0.254334 | 0.002352 | -0.009041 | 0.013744 | -0.008687 | 0.013390 |
| 5 | combined | next_gap | opening_gap_offshore | opening_gap_domestic | mae | 265 | 53 | 0.002693 | 0.002679 | -0.000014 | -0.000065 | 0.000037 | -0.000062 | 0.000034 |
| 21 | combined | next_gap | opening_gap_offshore | opening_gap_domestic | brier | 217 | 11 | 0.264465 | 0.267577 | 0.003112 | -0.007829 | 0.014053 | -0.006992 | 0.013216 |
| 21 | combined | next_gap | opening_gap_offshore | opening_gap_domestic | mae | 217 | 11 | 0.002986 | 0.002994 | 0.000007 | -0.000052 | 0.000067 | -0.000064 | 0.000079 |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | enter_high | offshore_opening | gjr_control | brier | 170 | 40 | 0.172613 | 0.200352 | 0.027739 | -0.104390 | 0.159869 | -0.144100 | 0.199578 |
| 5 | combined | enter_high | offshore_opening | historical | brier | 170 | 40 | 0.172613 | 0.200170 | 0.027557 | -0.038563 | 0.093676 | -0.047983 | 0.103096 |
| 5 | combined | enter_high | domestic_global_interaction | gjr_control | brier | 170 | 40 | 0.177063 | 0.200352 | 0.023289 | -0.113571 | 0.160150 | -0.154496 | 0.201074 |
| 5 | combined | enter_high | domestic_global_interaction | historical | brier | 170 | 40 | 0.177063 | 0.200170 | 0.023107 | -0.031804 | 0.078018 | -0.032783 | 0.078997 |
| 5 | combined | enter_high | offshore_opening | iv_raw | brier | 170 | 40 | 0.172613 | 0.151825 | -0.020788 | -0.141945 | 0.100368 | -0.181105 | 0.139529 |
| 5 | combined | enter_high | domestic_global_interaction | iv_raw | brier | 170 | 40 | 0.177063 | 0.151825 | -0.025238 | -0.154326 | 0.103849 | -0.194102 | 0.143626 |
| 5 | combined | expand | offshore_opening | historical | brier | 265 | 53 | 0.214144 | 0.222296 | 0.008152 | -0.035962 | 0.052266 | -0.037194 | 0.053498 |
| 5 | combined | expand | offshore_opening | gjr_control | brier | 265 | 53 | 0.214144 | 0.191054 | -0.023089 | -0.096218 | 0.050039 | -0.089898 | 0.043719 |
| 5 | combined | expand | domestic_global_interaction | historical | brier | 265 | 53 | 0.247780 | 0.222296 | -0.025484 | -0.085592 | 0.034624 | -0.087152 | 0.036184 |
| 5 | combined | expand | domestic_global_interaction | gjr_control | brier | 265 | 53 | 0.247780 | 0.191054 | -0.056726 | -0.137224 | 0.023773 | -0.134880 | 0.021429 |
| 5 | combined | expand | offshore_opening | iv_raw | brier | 265 | 53 | 0.214144 | 0.155657 | -0.058487 | -0.128565 | 0.011591 | -0.125254 | 0.008279 |
| 5 | combined | expand | domestic_global_interaction | iv_raw | brier | 265 | 53 | 0.247780 | 0.155657 | -0.092123 | -0.177611 | -0.006635 | -0.173305 | -0.010942 |
| 5 | combined | variance_extreme | domestic_global_interaction | historical | brier | 265 | 53 | 0.125245 | 0.167442 | 0.042198 | -0.113105 | 0.197500 | -0.143772 | 0.228167 |
| 5 | combined | variance_extreme | offshore_opening | historical | brier | 265 | 53 | 0.146101 | 0.167442 | 0.021342 | -0.164384 | 0.207067 | -0.189011 | 0.231695 |
| 5 | combined | variance_extreme | domestic_global_interaction | gjr_control | brier | 265 | 53 | 0.125245 | 0.069122 | -0.056123 | -0.147215 | 0.034969 | -0.156498 | 0.044252 |
| 5 | combined | variance_extreme | domestic_global_interaction | iv_raw | brier | 265 | 53 | 0.125245 | 0.052940 | -0.072305 | -0.173960 | 0.029351 | -0.189215 | 0.044606 |
| 5 | combined | variance_extreme | offshore_opening | gjr_control | brier | 265 | 53 | 0.146101 | 0.069122 | -0.076979 | -0.218445 | 0.064487 | -0.234397 | 0.080439 |
| 5 | combined | variance_extreme | offshore_opening | iv_raw | brier | 265 | 53 | 0.146101 | 0.052940 | -0.093161 | -0.238416 | 0.052095 | -0.259894 | 0.073573 |
| 21 | combined | enter_high | domestic_global_interaction | historical | brier | 150 | 8 | 0.240946 | 0.241019 | 0.000074 | -0.029683 | 0.029830 | -0.031207 | 0.031354 |
| 21 | combined | enter_high | offshore_opening | historical | brier | 150 | 8 | 0.241116 | 0.241019 | -0.000097 | -0.012887 | 0.012693 | -0.011459 | 0.011266 |
| 21 | combined | enter_high | domestic_global_interaction | gjr_control | brier | 150 | 8 | 0.240946 | 0.206600 | -0.034346 | -0.419179 | 0.350488 | -0.493522 | 0.424830 |
| 21 | combined | enter_high | offshore_opening | gjr_control | brier | 150 | 8 | 0.241116 | 0.206600 | -0.034516 | -0.421275 | 0.352243 | -0.498350 | 0.429318 |
| 21 | combined | enter_high | domestic_global_interaction | iv_raw | brier | 150 | 8 | 0.240946 | 0.191434 | -0.049512 | -0.413659 | 0.314635 | -0.505988 | 0.406965 |
| 21 | combined | enter_high | offshore_opening | iv_raw | brier | 150 | 8 | 0.241116 | 0.191434 | -0.049682 | -0.414582 | 0.315219 | -0.507615 | 0.408252 |
| 21 | combined | expand | domestic_global_interaction | historical | brier | 217 | 11 | 0.300172 | 0.299434 | -0.000739 | -0.059885 | 0.058408 | -0.071618 | 0.070141 |
| 21 | combined | expand | offshore_opening | historical | brier | 217 | 11 | 0.320263 | 0.299434 | -0.020830 | -0.105040 | 0.063380 | -0.132161 | 0.090502 |
| 21 | combined | expand | domestic_global_interaction | gjr_control | brier | 217 | 11 | 0.300172 | 0.225582 | -0.074590 | -0.331403 | 0.182223 | -0.379269 | 0.230089 |
| 21 | combined | expand | offshore_opening | gjr_control | brier | 217 | 11 | 0.320263 | 0.225582 | -0.094681 | -0.373089 | 0.183727 | -0.425893 | 0.236531 |
| 21 | combined | expand | domestic_global_interaction | iv_raw | brier | 217 | 11 | 0.300172 | 0.186036 | -0.114136 | -0.324886 | 0.096614 | -0.368157 | 0.139886 |
| 21 | combined | expand | offshore_opening | iv_raw | brier | 217 | 11 | 0.320263 | 0.186036 | -0.134227 | -0.365756 | 0.097302 | -0.414061 | 0.145607 |
| 21 | combined | variance_extreme | domestic_global_interaction | historical | brier | 217 | 11 | 0.237465 | 0.181993 | -0.055473 | -0.244450 | 0.133505 | -0.286910 | 0.175965 |
| 21 | combined | variance_extreme | offshore_opening | historical | brier | 217 | 11 | 0.254972 | 0.181993 | -0.072979 | -0.282055 | 0.136097 | -0.335002 | 0.189044 |
| 21 | combined | variance_extreme | domestic_global_interaction | gjr_control | brier | 217 | 11 | 0.237465 | 0.108529 | -0.128936 | -0.332873 | 0.075001 | -0.396068 | 0.138196 |
| 21 | combined | variance_extreme | domestic_global_interaction | iv_raw | brier | 217 | 11 | 0.237465 | 0.093622 | -0.143844 | -0.374399 | 0.086711 | -0.429270 | 0.141582 |
| 21 | combined | variance_extreme | offshore_opening | gjr_control | brier | 217 | 11 | 0.254972 | 0.108529 | -0.146442 | -0.367479 | 0.074594 | -0.442424 | 0.149539 |
| 21 | combined | variance_extreme | offshore_opening | iv_raw | brier | 217 | 11 | 0.254972 | 0.093622 | -0.161350 | -0.402674 | 0.079973 | -0.469635 | 0.146935 |

[Opening gap forecasts](opening-gap-forecasts.csv) · [Separate overnight risk](gap-channel-forecasts.csv) · [Foreign risk source alignment](../../../nifty_forecast_v13/2026-11-25/run-001/foreign-risk-clock.csv) · [Gold and Nasdaq supplemental timing](supplemental-clock.csv).
