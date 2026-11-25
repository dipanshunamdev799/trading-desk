# V14 Volatility Transition Models

Expansion and contraction require future volatility above 1.25 or below 0.80 times the trailing H-session realized level. Entry and exit score only the eligible initial state, using a rolling 75th percentile of matured outcomes for the high-state boundary. Elevated volatility persistence requires both parts of the future window to exceed the high threshold. Speed and acceleration are scored separately. State probabilities use observed data or filtering available at the origin. Retrospectively smoothed values appear only in hidden-state parameter fitting on already observed training returns.

| horizon | cohort | event | model | n | disjoint | brier | log_loss | p | actual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | contract | iv_raw | 265 | 53 | 0.131716 | 0.405392 | 0.293246 | 0.286792 |
| 5 | combined | contract | simple_drift | 265 | 53 | 0.132584 | 0.407090 | 0.292906 | 0.286792 |
| 5 | combined | contract | constant_iv | 265 | 53 | 0.132753 | 0.407668 | 0.293245 | 0.286792 |
| 5 | combined | contract | trend_shrink | 265 | 53 | 0.132755 | 0.407690 | 0.292768 | 0.286792 |
| 5 | combined | enter_high | iv_scaled_blocks | 170 | 40 | 0.147499 | 0.471098 | 0.198624 | 0.247059 |
| 5 | combined | enter_high | intraday_blocks | 170 | 40 | 0.147651 | 0.472082 | 0.193285 | 0.247059 |
| 5 | combined | enter_high | trend_blocks | 170 | 40 | 0.147927 | 0.469024 | 0.197243 | 0.247059 |
| 5 | combined | enter_high | simple_drift | 170 | 40 | 0.151495 | 0.475078 | 0.257132 | 0.247059 |
| 5 | combined | exit_high | latent_sv | 95 | 23 | 0.182801 | 0.540358 | 0.468827 | 0.431579 |
| 5 | combined | exit_high | gjr_control | 95 | 23 | 0.184518 | 0.565110 | 0.435515 | 0.431579 |
| 5 | combined | exit_high | gjr_skew | 95 | 23 | 0.184731 | 0.561950 | 0.503212 | 0.431579 |
| 5 | combined | exit_high | gjr_student | 95 | 23 | 0.185273 | 0.563843 | 0.501655 | 0.431579 |
| 5 | combined | expand | iv_raw | 265 | 53 | 0.155657 | 0.466192 | 0.356195 | 0.328302 |
| 5 | combined | expand | simple_drift | 265 | 53 | 0.155718 | 0.466511 | 0.356797 | 0.328302 |
| 5 | combined | expand | constant_iv | 265 | 53 | 0.155824 | 0.466851 | 0.356431 | 0.328302 |
| 5 | combined | expand | trend_shrink | 265 | 53 | 0.156071 | 0.467372 | 0.357098 | 0.328302 |
| 5 | combined | persist_high | constant_iv | 265 | 53 | 0.103402 | 0.345746 | 0.190137 | 0.200000 |
| 5 | combined | persist_high | simple_drift | 265 | 53 | 0.103420 | 0.346358 | 0.190371 | 0.200000 |
| 5 | combined | persist_high | trend_shrink | 265 | 53 | 0.103461 | 0.346062 | 0.190592 | 0.200000 |
| 5 | combined | persist_high | gjr_iv | 265 | 53 | 0.105886 | 0.355157 | 0.156281 | 0.200000 |
| 5 | combined | rapid_risk | jump_no_episode | 265 | 53 | 0.111275 | 0.376417 | 0.139035 | 0.132075 |
| 5 | combined | rapid_risk | jump_1m | 265 | 53 | 0.111292 | 0.376366 | 0.139109 | 0.132075 |
| 5 | combined | rapid_risk | jump_shift | 265 | 53 | 0.111324 | 0.376660 | 0.139116 | 0.132075 |
| 5 | combined | rapid_risk | jump_diffusion | 265 | 53 | 0.111344 | 0.376687 | 0.139101 | 0.132075 |
| 5 | combined | variance_extreme | iv_raw | 265 | 53 | 0.052940 | 0.197735 | 0.150359 | 0.166038 |
| 5 | combined | variance_extreme | constant_iv | 265 | 53 | 0.053015 | 0.198429 | 0.150380 | 0.166038 |
| 5 | combined | variance_extreme | simple_drift | 265 | 53 | 0.053036 | 0.198900 | 0.150603 | 0.166038 |
| 5 | combined | variance_extreme | trend_shrink | 265 | 53 | 0.053066 | 0.198965 | 0.150910 | 0.166038 |
| 21 | combined | contract | gjr_control | 217 | 11 | 0.125079 | 0.368522 | 0.276851 | 0.235023 |
| 21 | combined | contract | separate_gap | 217 | 11 | 0.150456 | 0.440655 | 0.296920 | 0.235023 |
| 21 | combined | contract | jump_1m | 217 | 11 | 0.150480 | 0.440860 | 0.296204 | 0.235023 |
| 21 | combined | contract | jump_shift | 217 | 11 | 0.150501 | 0.441016 | 0.296301 | 0.235023 |
| 21 | combined | enter_high | regime_state | 150 | 8 | 0.173263 | 0.524416 | 0.346100 | 0.266667 |
| 21 | combined | enter_high | latent_sv | 150 | 8 | 0.173874 | 0.551432 | 0.173818 | 0.266667 |
| 21 | combined | enter_high | gjr_student | 150 | 8 | 0.174950 | 0.556470 | 0.215576 | 0.266667 |
| 21 | combined | enter_high | gjr_skew | 150 | 8 | 0.176104 | 0.550451 | 0.218864 | 0.266667 |
| 21 | combined | exit_high | gjr_control | 67 | 5 | 0.040560 | 0.176979 | 0.237744 | 0.164179 |
| 21 | combined | exit_high | state_variance_control | 67 | 5 | 0.044060 | 0.179289 | 0.190629 | 0.164179 |
| 21 | combined | exit_high | latent_sv | 67 | 5 | 0.098834 | 0.344916 | 0.339144 | 0.164179 |
| 21 | combined | exit_high | gjr_student | 67 | 5 | 0.102844 | 0.361581 | 0.380830 | 0.164179 |
| 21 | combined | expand | iv_raw | 217 | 11 | 0.186036 | 0.829771 | 0.278692 | 0.373272 |
| 21 | combined | expand | path_mixture | 217 | 11 | 0.202223 | 0.661013 | 0.216756 | 0.373272 |
| 21 | combined | expand | gjr_iv_control | 217 | 11 | 0.203735 | 0.913900 | 0.180202 | 0.373272 |
| 21 | combined | expand | trend_shrink | 217 | 11 | 0.204619 | 0.902525 | 0.254840 | 0.373272 |
| 21 | combined | persist_high | constant_iv | 217 | 11 | 0.117375 | 0.430039 | 0.307833 | 0.350230 |
| 21 | combined | persist_high | trend_shrink | 217 | 11 | 0.117383 | 0.427690 | 0.308056 | 0.350230 |
| 21 | combined | persist_high | simple_drift | 217 | 11 | 0.117497 | 0.430249 | 0.308027 | 0.350230 |
| 21 | combined | persist_high | trend_persistent | 217 | 11 | 0.118748 | 0.388445 | 0.237743 | 0.350230 |
| 21 | combined | rapid_risk | gjr_skew | 217 | 11 | 0.132355 | 0.405525 | 0.102352 | 0.179724 |
| 21 | combined | rapid_risk | separate_gap | 217 | 11 | 0.132817 | 0.411397 | 0.120956 | 0.179724 |
| 21 | combined | rapid_risk | gjr_student | 217 | 11 | 0.132866 | 0.407793 | 0.100494 | 0.179724 |
| 21 | combined | rapid_risk | gjr_gauss | 217 | 11 | 0.133132 | 0.404835 | 0.089061 | 0.179724 |
| 21 | combined | variance_extreme | path_mixture | 217 | 11 | 0.084441 | 0.290560 | 0.130389 | 0.165899 |
| 21 | combined | variance_extreme | joint_pit | 217 | 11 | 0.084527 | 0.281076 | 0.138782 | 0.165899 |
| 21 | combined | variance_extreme | joint_tail_width | 217 | 11 | 0.086560 | 0.293514 | 0.136595 | 0.165899 |
| 21 | combined | variance_extreme | gjr_iv_control | 217 | 11 | 0.088872 | 0.562716 | 0.093619 | 0.165899 |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | enter_high | joint_pit | gjr_control | brier | 170 | 40 | 0.154250 | 0.200352 | 0.046102 | -0.023448 | 0.115652 | -0.020262 | 0.112466 |
| 5 | combined | enter_high | joint_pit | historical | brier | 170 | 40 | 0.154250 | 0.200170 | 0.045920 | -0.088408 | 0.180248 | -0.124717 | 0.216557 |
| 5 | combined | enter_high | gjr_iv | gjr_control | brier | 170 | 40 | 0.156440 | 0.200352 | 0.043912 | -0.012781 | 0.100606 | -0.014148 | 0.101973 |
| 5 | combined | enter_high | gjr_iv | historical | brier | 170 | 40 | 0.156440 | 0.200170 | 0.043730 | -0.087837 | 0.175297 | -0.128775 | 0.216235 |
| 5 | combined | enter_high | markov_state | gjr_control | brier | 170 | 40 | 0.162688 | 0.200352 | 0.037665 | -0.080926 | 0.156256 | -0.113285 | 0.188614 |
| 5 | combined | enter_high | markov_state | historical | brier | 170 | 40 | 0.162688 | 0.200170 | 0.037483 | -0.027800 | 0.102765 | -0.033039 | 0.108004 |
| 5 | combined | enter_high | domestic | gjr_control | brier | 170 | 40 | 0.168586 | 0.200352 | 0.031767 | -0.104989 | 0.168522 | -0.143752 | 0.207285 |
| 5 | combined | enter_high | domestic | historical | brier | 170 | 40 | 0.168586 | 0.200170 | 0.031584 | -0.031485 | 0.094653 | -0.033430 | 0.096599 |
| 5 | combined | enter_high | intraday | gjr_control | brier | 170 | 40 | 0.169596 | 0.200352 | 0.030756 | -0.104243 | 0.165756 | -0.138574 | 0.200086 |
| 5 | combined | enter_high | intraday | historical | brier | 170 | 40 | 0.169596 | 0.200170 | 0.030574 | -0.047711 | 0.108859 | -0.054615 | 0.115763 |
| 5 | combined | enter_high | surface | gjr_control | brier | 170 | 40 | 0.170825 | 0.200352 | 0.029528 | -0.108434 | 0.167490 | -0.147571 | 0.206626 |
| 5 | combined | enter_high | surface | historical | brier | 170 | 40 | 0.170825 | 0.200170 | 0.029345 | -0.051673 | 0.110364 | -0.059122 | 0.117813 |
| 5 | combined | enter_high | gjr_control | historical | brier | 170 | 40 | 0.200352 | 0.200170 | -0.000182 | -0.138221 | 0.137857 | -0.187032 | 0.186667 |
| 5 | combined | enter_high | joint_pit | iv_raw | brier | 170 | 40 | 0.154250 | 0.151825 | -0.002425 | -0.026728 | 0.021878 | -0.030308 | 0.025458 |
| 5 | combined | enter_high | regime_state | gjr_control | brier | 170 | 40 | 0.204757 | 0.200352 | -0.004404 | -0.047138 | 0.038329 | -0.052465 | 0.043656 |
| 5 | combined | enter_high | regime_state | historical | brier | 170 | 40 | 0.204757 | 0.200170 | -0.004587 | -0.112073 | 0.102900 | -0.151018 | 0.141845 |
| 5 | combined | enter_high | gjr_iv | iv_raw | brier | 170 | 40 | 0.156440 | 0.151825 | -0.004615 | -0.033012 | 0.023782 | -0.033084 | 0.023854 |
| 5 | combined | enter_high | markov_state | iv_raw | brier | 170 | 40 | 0.162688 | 0.151825 | -0.010863 | -0.130529 | 0.108804 | -0.159653 | 0.137928 |
| 5 | combined | enter_high | domestic | iv_raw | brier | 170 | 40 | 0.168586 | 0.151825 | -0.016761 | -0.142867 | 0.109345 | -0.181704 | 0.148183 |
| 5 | combined | enter_high | intraday | iv_raw | brier | 170 | 40 | 0.169596 | 0.151825 | -0.017771 | -0.141640 | 0.106098 | -0.178270 | 0.142728 |
| 5 | combined | enter_high | surface | iv_raw | brier | 170 | 40 | 0.170825 | 0.151825 | -0.019000 | -0.138226 | 0.100226 | -0.180386 | 0.142387 |
| 5 | combined | enter_high | gjr_control | iv_raw | brier | 170 | 40 | 0.200352 | 0.151825 | -0.048527 | -0.120976 | 0.023921 | -0.116849 | 0.019794 |
| 5 | combined | enter_high | regime_state | iv_raw | brier | 170 | 40 | 0.204757 | 0.151825 | -0.052932 | -0.132847 | 0.026984 | -0.129809 | 0.023945 |
| 5 | combined | exit_high | gjr_control | historical | brier | 95 | 23 | 0.184518 | 0.356318 | 0.171800 | -0.024073 | 0.367672 | -0.047393 | 0.390992 |
| 5 | combined | exit_high | gjr_iv | historical | brier | 95 | 23 | 0.190807 | 0.356318 | 0.165511 | 0.001029 | 0.329992 | -0.021574 | 0.352595 |
| 5 | combined | exit_high | joint_pit | historical | brier | 95 | 23 | 0.199134 | 0.356318 | 0.157184 | -0.022130 | 0.336497 | -0.049577 | 0.363944 |
| 5 | combined | exit_high | regime_state | historical | brier | 95 | 23 | 0.229062 | 0.356318 | 0.127256 | -0.002293 | 0.256805 | -0.019781 | 0.274293 |
| 5 | combined | exit_high | markov_state | historical | brier | 95 | 23 | 0.287484 | 0.356318 | 0.068834 | -0.032040 | 0.169708 | -0.056352 | 0.194021 |
| 5 | combined | exit_high | surface | historical | brier | 95 | 23 | 0.302855 | 0.356318 | 0.053463 | -0.061126 | 0.168051 | -0.081118 | 0.188043 |
| 5 | combined | exit_high | intraday | historical | brier | 95 | 23 | 0.318628 | 0.356318 | 0.037690 | -0.070087 | 0.145467 | -0.085563 | 0.160944 |
| 5 | combined | exit_high | domestic | historical | brier | 95 | 23 | 0.321584 | 0.356318 | 0.034734 | -0.063506 | 0.132974 | -0.084286 | 0.153754 |
| 5 | combined | exit_high | gjr_control | iv_raw | brier | 95 | 23 | 0.184518 | 0.199344 | 0.014826 | -0.057858 | 0.087510 | -0.061767 | 0.091419 |
| 5 | combined | exit_high | gjr_iv | iv_raw | brier | 95 | 23 | 0.190807 | 0.199344 | 0.008537 | -0.043661 | 0.060734 | -0.055966 | 0.073039 |
| 5 | combined | exit_high | joint_pit | iv_raw | brier | 95 | 23 | 0.199134 | 0.199344 | 0.000210 | -0.025038 | 0.025457 | -0.027995 | 0.028414 |
| 5 | combined | exit_high | gjr_iv | gjr_control | brier | 95 | 23 | 0.190807 | 0.184518 | -0.006289 | -0.081617 | 0.069038 | -0.083742 | 0.071164 |
| 5 | combined | exit_high | joint_pit | gjr_control | brier | 95 | 23 | 0.199134 | 0.184518 | -0.014616 | -0.094545 | 0.065312 | -0.098823 | 0.069591 |
| 5 | combined | exit_high | regime_state | iv_raw | brier | 95 | 23 | 0.229062 | 0.199344 | -0.029718 | -0.140133 | 0.080697 | -0.165300 | 0.105865 |
| 5 | combined | exit_high | regime_state | gjr_control | brier | 95 | 23 | 0.229062 | 0.184518 | -0.044544 | -0.146161 | 0.057074 | -0.161456 | 0.072369 |
| 5 | combined | exit_high | markov_state | iv_raw | brier | 95 | 23 | 0.287484 | 0.199344 | -0.088140 | -0.257520 | 0.081240 | -0.283594 | 0.107315 |
| 5 | combined | exit_high | markov_state | gjr_control | brier | 95 | 23 | 0.287484 | 0.184518 | -0.102966 | -0.281900 | 0.075968 | -0.297705 | 0.091773 |
| 5 | combined | exit_high | surface | iv_raw | brier | 95 | 23 | 0.302855 | 0.199344 | -0.103511 | -0.261366 | 0.054343 | -0.267713 | 0.060691 |
| 5 | combined | exit_high | surface | gjr_control | brier | 95 | 23 | 0.302855 | 0.184518 | -0.118337 | -0.295898 | 0.059223 | -0.300836 | 0.064161 |
| 5 | combined | exit_high | intraday | iv_raw | brier | 95 | 23 | 0.318628 | 0.199344 | -0.119284 | -0.272007 | 0.033439 | -0.285788 | 0.047221 |
| 5 | combined | exit_high | domestic | iv_raw | brier | 95 | 23 | 0.321584 | 0.199344 | -0.122240 | -0.285410 | 0.040931 | -0.302251 | 0.057771 |
| 5 | combined | exit_high | intraday | gjr_control | brier | 95 | 23 | 0.318628 | 0.184518 | -0.134110 | -0.309729 | 0.041510 | -0.322047 | 0.053828 |
| 5 | combined | exit_high | domestic | gjr_control | brier | 95 | 23 | 0.321584 | 0.184518 | -0.137066 | -0.322533 | 0.048401 | -0.338778 | 0.064646 |
| 5 | combined | expand | gjr_iv | historical | brier | 265 | 53 | 0.158643 | 0.222296 | 0.063652 | -0.004358 | 0.131662 | -0.002618 | 0.129923 |
| 5 | combined | expand | joint_pit | historical | brier | 265 | 53 | 0.159110 | 0.222296 | 0.063185 | -0.005231 | 0.131601 | 0.000339 | 0.126032 |
| 5 | combined | expand | gjr_iv | gjr_control | brier | 265 | 53 | 0.158643 | 0.191054 | 0.032411 | -0.013116 | 0.077938 | -0.009848 | 0.074670 |
| 5 | combined | expand | joint_pit | gjr_control | brier | 265 | 53 | 0.159110 | 0.191054 | 0.031944 | -0.023531 | 0.087419 | -0.015580 | 0.079468 |
| 5 | combined | expand | gjr_control | historical | brier | 265 | 53 | 0.191054 | 0.222296 | 0.031241 | -0.044664 | 0.107147 | -0.036588 | 0.099070 |
| 5 | combined | expand | regime_state | historical | brier | 265 | 53 | 0.196728 | 0.222296 | 0.025568 | -0.047579 | 0.098715 | -0.032760 | 0.083895 |
| 5 | combined | expand | intraday | historical | brier | 265 | 53 | 0.207146 | 0.222296 | 0.015149 | -0.024749 | 0.055048 | -0.024159 | 0.054457 |
| 5 | combined | expand | markov_state | historical | brier | 265 | 53 | 0.208593 | 0.222296 | 0.013702 | -0.028555 | 0.055959 | -0.028376 | 0.055781 |
| 5 | combined | expand | gjr_iv | iv_raw | brier | 265 | 53 | 0.158643 | 0.155657 | -0.002987 | -0.028739 | 0.022766 | -0.028449 | 0.022475 |
| 5 | combined | expand | joint_pit | iv_raw | brier | 265 | 53 | 0.159110 | 0.155657 | -0.003454 | -0.023855 | 0.016947 | -0.025430 | 0.018522 |
| 5 | combined | expand | surface | historical | brier | 265 | 53 | 0.227227 | 0.222296 | -0.004932 | -0.069809 | 0.059946 | -0.076563 | 0.066700 |
| 5 | combined | expand | regime_state | gjr_control | brier | 265 | 53 | 0.196728 | 0.191054 | -0.005673 | -0.034792 | 0.023445 | -0.032908 | 0.021561 |
| 5 | combined | expand | domestic | historical | brier | 265 | 53 | 0.234857 | 0.222296 | -0.012561 | -0.073063 | 0.047940 | -0.077462 | 0.052339 |
| 5 | combined | expand | intraday | gjr_control | brier | 265 | 53 | 0.207146 | 0.191054 | -0.016092 | -0.087928 | 0.055744 | -0.075854 | 0.043669 |
| 5 | combined | expand | markov_state | gjr_control | brier | 265 | 53 | 0.208593 | 0.191054 | -0.017539 | -0.088387 | 0.053309 | -0.078709 | 0.043631 |
| 5 | combined | expand | gjr_control | iv_raw | brier | 265 | 53 | 0.191054 | 0.155657 | -0.035398 | -0.090734 | 0.019938 | -0.081146 | 0.010350 |
| 5 | combined | expand | surface | gjr_control | brier | 265 | 53 | 0.227227 | 0.191054 | -0.036173 | -0.126410 | 0.054064 | -0.123039 | 0.050693 |
| 5 | combined | expand | regime_state | iv_raw | brier | 265 | 53 | 0.196728 | 0.155657 | -0.041071 | -0.098887 | 0.016744 | -0.081102 | -0.001041 |
| 5 | combined | expand | domestic | gjr_control | brier | 265 | 53 | 0.234857 | 0.191054 | -0.043803 | -0.127821 | 0.040216 | -0.127529 | 0.039924 |
| 5 | combined | expand | intraday | iv_raw | brier | 265 | 53 | 0.207146 | 0.155657 | -0.051490 | -0.119441 | 0.016461 | -0.110357 | 0.007377 |
| 5 | combined | expand | markov_state | iv_raw | brier | 265 | 53 | 0.208593 | 0.155657 | -0.052937 | -0.125558 | 0.019684 | -0.120368 | 0.014494 |
| 5 | combined | expand | surface | iv_raw | brier | 265 | 53 | 0.227227 | 0.155657 | -0.071571 | -0.150535 | 0.007394 | -0.151782 | 0.008641 |
| 5 | combined | expand | domestic | iv_raw | brier | 265 | 53 | 0.234857 | 0.155657 | -0.079200 | -0.163566 | 0.005165 | -0.162781 | 0.004380 |
| 21 | combined | enter_high | regime_state | historical | brier | 150 | 8 | 0.173263 | 0.241019 | 0.067756 | -0.231882 | 0.367394 | -0.284788 | 0.420301 |
| 21 | combined | enter_high | gjr_iv | historical | brier | 150 | 8 | 0.181728 | 0.241019 | 0.059291 | -0.233584 | 0.352166 | -0.305139 | 0.423721 |
| 21 | combined | enter_high | gjr_control | historical | brier | 150 | 8 | 0.206600 | 0.241019 | 0.034419 | -0.353921 | 0.422760 | -0.432819 | 0.501658 |
| 21 | combined | enter_high | regime_state | gjr_control | brier | 150 | 8 | 0.173263 | 0.206600 | 0.033337 | -0.128530 | 0.195203 | -0.175898 | 0.242571 |
| 21 | combined | enter_high | joint_pit | historical | brier | 150 | 8 | 0.209485 | 0.241019 | 0.031534 | -0.240601 | 0.303669 | -0.300234 | 0.363302 |
| 21 | combined | enter_high | gjr_iv | gjr_control | brier | 150 | 8 | 0.181728 | 0.206600 | 0.024872 | -0.170052 | 0.219795 | -0.201657 | 0.251400 |
| 21 | combined | enter_high | regime_state | iv_raw | brier | 150 | 8 | 0.173263 | 0.191434 | 0.018171 | -0.159886 | 0.196228 | -0.204883 | 0.241225 |
| 21 | combined | enter_high | intraday | historical | brier | 150 | 8 | 0.231096 | 0.241019 | 0.009923 | -0.012565 | 0.032412 | -0.010462 | 0.030309 |
| 21 | combined | enter_high | gjr_iv | iv_raw | brier | 150 | 8 | 0.181728 | 0.191434 | 0.009706 | -0.106835 | 0.126247 | -0.132571 | 0.151983 |
| 21 | combined | enter_high | joint_pit | gjr_control | brier | 150 | 8 | 0.209485 | 0.206600 | -0.002885 | -0.245714 | 0.239944 | -0.279906 | 0.274136 |
| 21 | combined | enter_high | markov_state | historical | brier | 150 | 8 | 0.245837 | 0.241019 | -0.004818 | -0.062653 | 0.053017 | -0.059260 | 0.049624 |
| 21 | combined | enter_high | domestic | historical | brier | 150 | 8 | 0.246556 | 0.241019 | -0.005537 | -0.025269 | 0.014195 | -0.026349 | 0.015275 |
| 21 | combined | enter_high | gjr_control | iv_raw | brier | 150 | 8 | 0.206600 | 0.191434 | -0.015166 | -0.240181 | 0.209849 | -0.310506 | 0.280174 |
| 21 | combined | enter_high | joint_pit | iv_raw | brier | 150 | 8 | 0.209485 | 0.191434 | -0.018051 | -0.147701 | 0.111599 | -0.167549 | 0.131446 |
| 21 | combined | enter_high | intraday | gjr_control | brier | 150 | 8 | 0.231096 | 0.206600 | -0.024496 | -0.414459 | 0.365467 | -0.493380 | 0.444389 |
| 21 | combined | enter_high | surface | historical | brier | 150 | 8 | 0.265968 | 0.241019 | -0.024949 | -0.113502 | 0.063604 | -0.128163 | 0.078265 |
| 21 | combined | enter_high | markov_state | gjr_control | brier | 150 | 8 | 0.245837 | 0.206600 | -0.039237 | -0.428519 | 0.350044 | -0.506151 | 0.427676 |
| 21 | combined | enter_high | intraday | iv_raw | brier | 150 | 8 | 0.231096 | 0.191434 | -0.039662 | -0.404471 | 0.325147 | -0.499429 | 0.420105 |
| 21 | combined | enter_high | domestic | gjr_control | brier | 150 | 8 | 0.246556 | 0.206600 | -0.039956 | -0.425777 | 0.345865 | -0.502483 | 0.422570 |
| 21 | combined | enter_high | markov_state | iv_raw | brier | 150 | 8 | 0.245837 | 0.191434 | -0.054403 | -0.406862 | 0.298056 | -0.497646 | 0.388840 |
| 21 | combined | enter_high | domestic | iv_raw | brier | 150 | 8 | 0.246556 | 0.191434 | -0.055122 | -0.413344 | 0.303100 | -0.504308 | 0.394064 |
| 21 | combined | enter_high | surface | gjr_control | brier | 150 | 8 | 0.265968 | 0.206600 | -0.059368 | -0.456800 | 0.338064 | -0.540894 | 0.422158 |
| 21 | combined | enter_high | surface | iv_raw | brier | 150 | 8 | 0.265968 | 0.191434 | -0.074534 | -0.409561 | 0.260494 | -0.494800 | 0.345732 |
| 21 | combined | exit_high | gjr_control | historical | brier | 67 | 5 | 0.040560 | 0.305538 | 0.264979 | -0.118060 | 0.648017 | -0.288575 | 0.818533 |
| 21 | combined | exit_high | regime_state | historical | brier | 67 | 5 | 0.129574 | 0.305538 | 0.175964 | -0.214033 | 0.565962 | -0.294016 | 0.645945 |
| 21 | combined | exit_high | gjr_iv | historical | brier | 67 | 5 | 0.133805 | 0.305538 | 0.171733 | -0.139642 | 0.483107 | -0.272150 | 0.615615 |
| 21 | combined | exit_high | joint_pit | historical | brier | 67 | 5 | 0.146322 | 0.305538 | 0.159216 | -0.067641 | 0.386074 | -0.191506 | 0.509939 |
| 21 | combined | exit_high | gjr_control | iv_raw | brier | 67 | 5 | 0.040560 | 0.142043 | 0.101483 | -0.172713 | 0.375679 | -0.250474 | 0.453440 |
| 21 | combined | exit_high | regime_state | iv_raw | brier | 67 | 5 | 0.129574 | 0.142043 | 0.012469 | -0.283924 | 0.308862 | -0.362354 | 0.387292 |
| 21 | combined | exit_high | gjr_iv | iv_raw | brier | 67 | 5 | 0.133805 | 0.142043 | 0.008237 | -0.186049 | 0.202523 | -0.245847 | 0.262321 |
| 21 | combined | exit_high | domestic | historical | brier | 67 | 5 | 0.305178 | 0.305538 | 0.000360 | -0.001739 | 0.002459 | -0.007579 | 0.008298 |
| 21 | combined | exit_high | markov_state | historical | brier | 67 | 5 | 0.305438 | 0.305538 | 0.000100 | -0.000483 | 0.000683 | -0.002105 | 0.002305 |
| 21 | combined | exit_high | surface | historical | brier | 67 | 5 | 0.305483 | 0.305538 | 0.000055 | -0.000267 | 0.000377 | -0.001163 | 0.001273 |
| 21 | combined | exit_high | intraday | historical | brier | 67 | 5 | 0.306067 | 0.305538 | -0.000529 | -0.003617 | 0.002559 | -0.012207 | 0.011148 |
| 21 | combined | exit_high | joint_pit | iv_raw | brier | 67 | 5 | 0.146322 | 0.142043 | -0.004279 | -0.095651 | 0.087093 | -0.126138 | 0.117580 |
| 21 | combined | exit_high | regime_state | gjr_control | brier | 67 | 5 | 0.129574 | 0.040560 | -0.089014 | -0.181954 | 0.003925 | -0.343815 | 0.165786 |
| 21 | combined | exit_high | gjr_iv | gjr_control | brier | 67 | 5 | 0.133805 | 0.040560 | -0.093246 | -0.259092 | 0.072600 | -0.286157 | 0.099665 |
| 21 | combined | exit_high | joint_pit | gjr_control | brier | 67 | 5 | 0.146322 | 0.040560 | -0.105762 | -0.328368 | 0.116844 | -0.372732 | 0.161208 |
| 21 | combined | exit_high | domestic | iv_raw | brier | 67 | 5 | 0.305178 | 0.142043 | -0.163136 | -0.335115 | 0.008843 | -0.440750 | 0.114478 |
| 21 | combined | exit_high | markov_state | iv_raw | brier | 67 | 5 | 0.305438 | 0.142043 | -0.163396 | -0.334888 | 0.008097 | -0.436546 | 0.109755 |
| 21 | combined | exit_high | surface | iv_raw | brier | 67 | 5 | 0.305483 | 0.142043 | -0.163440 | -0.334851 | 0.007970 | -0.435827 | 0.108947 |
| 21 | combined | exit_high | intraday | iv_raw | brier | 67 | 5 | 0.306067 | 0.142043 | -0.164025 | -0.334390 | 0.006341 | -0.426572 | 0.098523 |
| 21 | combined | exit_high | domestic | gjr_control | brier | 67 | 5 | 0.305178 | 0.040560 | -0.264619 | -0.648167 | 0.118929 | -0.823317 | 0.294080 |
| 21 | combined | exit_high | markov_state | gjr_control | brier | 67 | 5 | 0.305438 | 0.040560 | -0.264879 | -0.648057 | 0.118300 | -0.819855 | 0.290097 |
| 21 | combined | exit_high | surface | gjr_control | brier | 67 | 5 | 0.305483 | 0.040560 | -0.264923 | -0.648039 | 0.118192 | -0.819263 | 0.289416 |
| 21 | combined | exit_high | intraday | gjr_control | brier | 67 | 5 | 0.306067 | 0.040560 | -0.265508 | -0.647815 | 0.116800 | -0.811616 | 0.280601 |
| 21 | combined | expand | joint_pit | historical | brier | 217 | 11 | 0.204985 | 0.299434 | 0.094448 | -0.068212 | 0.257108 | -0.084424 | 0.273320 |
| 21 | combined | expand | gjr_iv | historical | brier | 217 | 11 | 0.205464 | 0.299434 | 0.093970 | -0.087644 | 0.275584 | -0.117810 | 0.305750 |
| 21 | combined | expand | regime_state | historical | brier | 217 | 11 | 0.215056 | 0.299434 | 0.084377 | -0.126850 | 0.295604 | -0.159507 | 0.328262 |
| 21 | combined | expand | gjr_control | historical | brier | 217 | 11 | 0.225582 | 0.299434 | 0.073851 | -0.194593 | 0.342295 | -0.243795 | 0.391497 |
| 21 | combined | expand | joint_pit | gjr_control | brier | 217 | 11 | 0.204985 | 0.225582 | 0.020597 | -0.168286 | 0.209480 | -0.182797 | 0.223990 |
| 21 | combined | expand | gjr_iv | gjr_control | brier | 217 | 11 | 0.205464 | 0.225582 | 0.020119 | -0.112762 | 0.152999 | -0.122788 | 0.163025 |
| 21 | combined | expand | regime_state | gjr_control | brier | 217 | 11 | 0.215056 | 0.225582 | 0.010526 | -0.085538 | 0.106590 | -0.108632 | 0.129684 |
| 21 | combined | expand | domestic | historical | brier | 217 | 11 | 0.299065 | 0.299434 | 0.000368 | -0.103231 | 0.103968 | -0.123946 | 0.124683 |
| 21 | combined | expand | markov_state | historical | brier | 217 | 11 | 0.311593 | 0.299434 | -0.012159 | -0.146738 | 0.122420 | -0.147233 | 0.122915 |
| 21 | combined | expand | surface | historical | brier | 217 | 11 | 0.311606 | 0.299434 | -0.012173 | -0.135592 | 0.111247 | -0.164172 | 0.139827 |
| 21 | combined | expand | joint_pit | iv_raw | brier | 217 | 11 | 0.204985 | 0.186036 | -0.018949 | -0.128283 | 0.090385 | -0.145777 | 0.107878 |
| 21 | combined | expand | gjr_iv | iv_raw | brier | 217 | 11 | 0.205464 | 0.186036 | -0.019427 | -0.093973 | 0.055118 | -0.104097 | 0.065243 |
| 21 | combined | expand | intraday | historical | brier | 217 | 11 | 0.327952 | 0.299434 | -0.028519 | -0.095319 | 0.038282 | -0.116373 | 0.059336 |
| 21 | combined | expand | regime_state | iv_raw | brier | 217 | 11 | 0.215056 | 0.186036 | -0.029020 | -0.129107 | 0.071067 | -0.126385 | 0.068345 |
| 21 | combined | expand | gjr_control | iv_raw | brier | 217 | 11 | 0.225582 | 0.186036 | -0.039546 | -0.158349 | 0.079257 | -0.176711 | 0.097619 |
| 21 | combined | expand | domestic | gjr_control | brier | 217 | 11 | 0.299065 | 0.225582 | -0.073483 | -0.372312 | 0.225346 | -0.427168 | 0.280202 |
| 21 | combined | expand | markov_state | gjr_control | brier | 217 | 11 | 0.311593 | 0.225582 | -0.086010 | -0.430599 | 0.258579 | -0.473609 | 0.301589 |
| 21 | combined | expand | surface | gjr_control | brier | 217 | 11 | 0.311606 | 0.225582 | -0.086024 | -0.379825 | 0.207777 | -0.438573 | 0.266525 |
| 21 | combined | expand | intraday | gjr_control | brier | 217 | 11 | 0.327952 | 0.225582 | -0.102370 | -0.366821 | 0.162082 | -0.413591 | 0.208851 |
| 21 | combined | expand | domestic | iv_raw | brier | 217 | 11 | 0.299065 | 0.186036 | -0.113029 | -0.353515 | 0.127457 | -0.402730 | 0.176672 |
| 21 | combined | expand | markov_state | iv_raw | brier | 217 | 11 | 0.311593 | 0.186036 | -0.125556 | -0.419262 | 0.168149 | -0.463288 | 0.212176 |
| 21 | combined | expand | surface | iv_raw | brier | 217 | 11 | 0.311606 | 0.186036 | -0.125570 | -0.360173 | 0.109033 | -0.413682 | 0.162542 |
| 21 | combined | expand | intraday | iv_raw | brier | 217 | 11 | 0.327952 | 0.186036 | -0.141916 | -0.366420 | 0.082588 | -0.406770 | 0.122938 |

| horizon | target | model | cohort | n | disjoint | prediction_rows | ess | mae | rmse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | speed | domestic_global_interaction | combined | 265 | 53 | 265 | 151.598881 | 0.059846 | 0.082125 |
| 5 | speed | persist | combined | 265 | 53 | 265 | 151.598881 | 0.059984 | 0.081705 |
| 5 | speed | surface | combined | 265 | 53 | 265 | 151.598881 | 0.060386 | 0.081688 |
| 5 | speed | intraday | combined | 265 | 53 | 265 | 151.598881 | 0.060655 | 0.082354 |
| 5 | vol_acceleration | persist | combined | 265 | 53 | 265 | 119.942848 | 0.067878 | 0.092941 |
| 5 | vol_acceleration | intraday | combined | 265 | 53 | 265 | 119.942848 | 0.068282 | 0.092960 |
| 5 | vol_acceleration | surface | combined | 265 | 53 | 265 | 119.942848 | 0.068611 | 0.093078 |
| 5 | vol_acceleration | domestic_global_interaction | combined | 265 | 53 | 265 | 119.942848 | 0.068885 | 0.093373 |
| 5 | vol_change | intraday | combined | 265 | 53 | 265 | 78.435311 | 0.044756 | 0.060181 |
| 5 | vol_change | surface | combined | 265 | 53 | 265 | 78.435311 | 0.045218 | 0.061921 |
| 5 | vol_change | domestic_global_interaction | combined | 265 | 53 | 265 | 78.435311 | 0.045556 | 0.060377 |
| 5 | vol_change | persist | combined | 265 | 53 | 265 | 78.435311 | 0.048120 | 0.064847 |
| 21 | speed | intraday | combined | 217 | 11 | 217 | 21.653774 | 0.042355 | 0.054266 |
| 21 | speed | domestic_global_interaction | combined | 217 | 11 | 217 | 21.653774 | 0.042793 | 0.053092 |
| 21 | speed | surface | combined | 217 | 11 | 217 | 21.653774 | 0.044309 | 0.054732 |
| 21 | speed | persist | combined | 217 | 11 | 217 | 21.653774 | 0.044664 | 0.056070 |
| 21 | vol_acceleration | intraday | combined | 217 | 11 | 217 | 17.721175 | 0.054235 | 0.071079 |
| 21 | vol_acceleration | persist | combined | 217 | 11 | 217 | 17.721175 | 0.054520 | 0.071912 |
| 21 | vol_acceleration | domestic_global_interaction | combined | 217 | 11 | 217 | 17.721175 | 0.055155 | 0.069834 |
| 21 | vol_acceleration | surface | combined | 217 | 11 | 217 | 17.721175 | 0.059009 | 0.075747 |
| 21 | vol_change | surface | combined | 217 | 11 | 217 | 10.010061 | 0.047848 | 0.062914 |
| 21 | vol_change | domestic_global_interaction | combined | 217 | 11 | 217 | 10.010061 | 0.049557 | 0.063016 |
| 21 | vol_change | persist | combined | 217 | 11 | 217 | 10.010061 | 0.051519 | 0.066982 |
| 21 | vol_change | intraday | combined | 217 | 11 | 217 | 10.010061 | 0.052041 | 0.068405 |

[As-of classification probabilities](transition-and-tail-probabilities.csv.gz) · [Training boundaries and coefficients](signal-fit-ledger.json).
