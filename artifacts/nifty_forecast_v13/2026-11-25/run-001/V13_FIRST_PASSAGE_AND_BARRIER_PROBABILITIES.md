# V13 First Passage And Barrier Probabilities

Fixed barriers are ±0.5%, ±1%, ±2%, ±3% and ±5%. Volatility-relative barriers are 0.5, 1, 1.5 and 2 times the origin-time IV-scaled horizon move. A touch uses the high or low. Any-close and last-close events use their own observations. Both-sided and neither-sided hits are distinct. When both sides are first hit on the same day, a recorded opening gap may resolve the order. Otherwise, complete reconciled one- or five-minute candles resolve it when their order is observable. Same-bar ambiguity is recorded explicitly. The model's ordering scores use common daily-resolution events, with intraday refinement retained in the observed-label audit.

A fixed-model follow-up computes exact empirical hit frequencies over the mature path library. The continuous driftless log-price diffusion benchmark uses the reflection principle, which makes a one-sided touch probability twice the respective endpoint tail probability at the same barrier.

| horizon | barrier | event | model | n | disjoint | predicted | observed | brier | log_loss | mc_se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0 | lower_close | iv_scaled | 265 | 53 | 0.571448 | 0.618868 | 0.249683 | 0.693968 | 0.021496 |
| 5 | 0 | lower_endpoint | iv_scaled | 265 | 53 | 0.387802 | 0.445283 | 0.263085 | 0.722072 | 0.021197 |
| 5 | 0 | lower_touch | iv_scaled | 265 | 53 | 0.712515 | 0.777358 | 0.182876 | 0.553284 | 0.019446 |
| 5 | 0 | upper_close | iv_scaled | 265 | 53 | 0.574742 | 0.569811 | 0.236841 | 0.666483 | 0.021698 |
| 5 | 0 | upper_endpoint | iv_scaled | 265 | 53 | 0.380366 | 0.362264 | 0.231153 | 0.654442 | 0.021335 |
| 5 | 0 | upper_touch | iv_scaled | 265 | 53 | 0.694015 | 0.671698 | 0.213208 | 0.616939 | 0.020113 |
| 5 | 1 | lower_close | iv_scaled | 265 | 53 | 0.407857 | 0.422642 | 0.253040 | 0.702880 | 0.020784 |
| 5 | 1 | lower_endpoint | iv_scaled | 265 | 53 | 0.264166 | 0.275472 | 0.208895 | 0.616616 | 0.018800 |
| 5 | 1 | lower_touch | iv_scaled | 265 | 53 | 0.526563 | 0.596226 | 0.256917 | 0.709652 | 0.021239 |
| 5 | 1 | upper_close | iv_scaled | 265 | 53 | 0.384898 | 0.392453 | 0.222879 | 0.635353 | 0.021008 |
| 5 | 1 | upper_endpoint | iv_scaled | 265 | 53 | 0.268300 | 0.237736 | 0.181737 | 0.547559 | 0.019259 |
| 5 | 1 | upper_touch | iv_scaled | 265 | 53 | 0.482532 | 0.467925 | 0.224830 | 0.641277 | 0.021629 |
| 5 | 2 | lower_close | iv_scaled | 265 | 53 | 0.183343 | 0.196226 | 0.156463 | 0.503074 | 0.015911 |
| 5 | 2 | lower_endpoint | iv_scaled | 265 | 53 | 0.118728 | 0.139623 | 0.122136 | 0.423670 | 0.013341 |
| 5 | 2 | lower_touch | iv_scaled | 265 | 53 | 0.256287 | 0.275472 | 0.199289 | 0.601065 | 0.017710 |
| 5 | 2 | upper_close | iv_scaled | 265 | 53 | 0.155027 | 0.143396 | 0.116392 | 0.377725 | 0.014931 |
| 5 | 2 | upper_endpoint | iv_scaled | 265 | 53 | 0.121698 | 0.124528 | 0.106029 | 0.355219 | 0.013686 |
| 5 | 2 | upper_touch | iv_scaled | 265 | 53 | 0.215419 | 0.177358 | 0.139489 | 0.441554 | 0.017168 |
| 5 | 3 | lower_close | iv_scaled | 265 | 53 | 0.079032 | 0.075472 | 0.067389 | 0.251239 | 0.010311 |
| 5 | 3 | lower_endpoint | iv_scaled | 265 | 53 | 0.053501 | 0.037736 | 0.036897 | 0.160015 | 0.008675 |
| 5 | 3 | lower_touch | iv_scaled | 265 | 53 | 0.120961 | 0.128302 | 0.106182 | 0.357967 | 0.012972 |
| 5 | 3 | upper_close | iv_scaled | 265 | 53 | 0.050708 | 0.098113 | 0.084979 | 0.298411 | 0.008120 |
| 5 | 3 | upper_endpoint | iv_scaled | 265 | 53 | 0.041170 | 0.086792 | 0.077022 | 0.274897 | 0.007588 |
| 5 | 3 | upper_touch | iv_scaled | 265 | 53 | 0.084847 | 0.120755 | 0.099121 | 0.333769 | 0.010498 |
| 5 | 4 | lower_close | iv_scaled | 265 | 53 | 0.011910 | 0.007547 | 0.007434 | 0.036520 | 0.002772 |
| 5 | 4 | lower_endpoint | iv_scaled | 265 | 53 | 0.010584 | 0.003774 | 0.003997 | 0.025218 | 0.002637 |
| 5 | 4 | lower_touch | iv_scaled | 265 | 53 | 0.029717 | 0.015094 | 0.015540 | 0.080860 | 0.005463 |
| 5 | 4 | upper_close | iv_scaled | 265 | 53 | 0.004577 | 0.033962 | 0.033183 | 0.182605 | 0.001454 |
| 5 | 4 | upper_endpoint | iv_scaled | 265 | 53 | 0.004142 | 0.030189 | 0.029817 | 0.172187 | 0.001407 |
| 5 | 4 | upper_touch | iv_scaled | 265 | 53 | 0.010532 | 0.041509 | 0.039337 | 0.189797 | 0.002408 |
| 21 | 0 | lower_close | iv_scaled | 217 | 11 | 0.789225 | 0.889401 | 0.123202 | 0.422204 | 0.017579 |
| 21 | 0 | lower_endpoint | iv_scaled | 217 | 11 | 0.321078 | 0.502304 | 0.311476 | 0.838880 | 0.020118 |
| 21 | 0 | lower_touch | iv_scaled | 217 | 11 | 0.869672 | 0.949309 | 0.062853 | 0.264288 | 0.014357 |
| 21 | 0 | upper_close | iv_scaled | 217 | 11 | 0.830546 | 0.728111 | 0.207287 | 0.613404 | 0.016461 |
| 21 | 0 | upper_endpoint | iv_scaled | 217 | 11 | 0.531835 | 0.377880 | 0.274988 | 0.745080 | 0.021711 |
| 21 | 0 | upper_touch | iv_scaled | 217 | 11 | 0.889662 | 0.792627 | 0.172027 | 0.542071 | 0.013625 |
| 21 | 1 | lower_close | iv_scaled | 217 | 11 | 0.656187 | 0.801843 | 0.212678 | 0.620231 | 0.020237 |
| 21 | 1 | lower_endpoint | iv_scaled | 217 | 11 | 0.271439 | 0.447005 | 0.308085 | 0.851684 | 0.019016 |
| 21 | 1 | lower_touch | iv_scaled | 217 | 11 | 0.746724 | 0.903226 | 0.132977 | 0.441800 | 0.018455 |
| 21 | 1 | upper_close | iv_scaled | 217 | 11 | 0.719452 | 0.603687 | 0.238108 | 0.668606 | 0.019591 |
| 21 | 1 | upper_endpoint | iv_scaled | 217 | 11 | 0.423063 | 0.294931 | 0.224257 | 0.640404 | 0.021554 |
| 21 | 1 | upper_touch | iv_scaled | 217 | 11 | 0.791421 | 0.663594 | 0.224270 | 0.638831 | 0.017736 |
| 21 | 2 | lower_close | iv_scaled | 217 | 11 | 0.421434 | 0.622120 | 0.326788 | 0.861851 | 0.020863 |
| 21 | 2 | lower_endpoint | iv_scaled | 217 | 11 | 0.203809 | 0.391705 | 0.302883 | 0.876010 | 0.017165 |
| 21 | 2 | lower_touch | iv_scaled | 217 | 11 | 0.515454 | 0.695853 | 0.297352 | 0.795476 | 0.020993 |
| 21 | 2 | upper_close | iv_scaled | 217 | 11 | 0.456752 | 0.359447 | 0.208665 | 0.606526 | 0.021307 |
| 21 | 2 | upper_endpoint | iv_scaled | 217 | 11 | 0.231873 | 0.193548 | 0.147952 | 0.475164 | 0.018302 |
| 21 | 2 | upper_touch | iv_scaled | 217 | 11 | 0.538666 | 0.437788 | 0.223141 | 0.637984 | 0.021312 |
| 21 | 3 | lower_close | iv_scaled | 217 | 11 | 0.281583 | 0.479263 | 0.345626 | 0.985088 | 0.018559 |
| 21 | 3 | lower_endpoint | iv_scaled | 217 | 11 | 0.147195 | 0.290323 | 0.254851 | 0.854550 | 0.014457 |
| 21 | 3 | lower_touch | iv_scaled | 217 | 11 | 0.336190 | 0.552995 | 0.356130 | 0.975850 | 0.019301 |
| 21 | 3 | upper_close | iv_scaled | 217 | 11 | 0.258353 | 0.230415 | 0.154872 | 0.480819 | 0.018374 |
| 21 | 3 | upper_endpoint | iv_scaled | 217 | 11 | 0.118664 | 0.152074 | 0.121598 | 0.408559 | 0.013747 |
| 21 | 3 | upper_touch | iv_scaled | 217 | 11 | 0.319529 | 0.271889 | 0.168956 | 0.512562 | 0.019470 |
| 21 | 4 | lower_close | iv_scaled | 217 | 11 | 0.140841 | 0.221198 | 0.214084 | 0.804329 | 0.013000 |
| 21 | 4 | lower_endpoint | iv_scaled | 217 | 11 | 0.086172 | 0.133641 | 0.136106 | 0.639182 | 0.010471 |
| 21 | 4 | lower_touch | iv_scaled | 217 | 11 | 0.168914 | 0.253456 | 0.235319 | 0.808626 | 0.014618 |
| 21 | 4 | upper_close | iv_scaled | 217 | 11 | 0.071762 | 0.119816 | 0.096330 | 0.378875 | 0.009822 |
| 21 | 4 | upper_endpoint | iv_scaled | 217 | 11 | 0.029693 | 0.082949 | 0.077491 | 0.400446 | 0.006371 |
| 21 | 4 | upper_touch | iv_scaled | 217 | 11 | 0.099375 | 0.129032 | 0.098606 | 0.351630 | 0.011490 |

| horizon | resolution | n |
| --- | --- | --- |
| 5 | intraday | 10 |
| 5 | open | 6 |
| 21 | intraday | 7 |
| 21 | open | 5 |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | diffusion_iv | empirical_exact | touch_family | brier | 265 | 53 | 0.144154 | 0.156019 | 0.011864 | -0.004748 | 0.028476 | -0.007469 | 0.031197 |
| 5 | combined | analytic_iv_diffusion | empirical_exact | touch_family | brier | 265 | 53 | 0.145264 | 0.156019 | 0.010754 | -0.006539 | 0.028047 | -0.009236 | 0.030745 |
| 5 | combined | random_state_iv | empirical_exact | touch_family | brier | 265 | 53 | 0.147156 | 0.156019 | 0.008863 | -0.005572 | 0.023298 | -0.008656 | 0.026382 |
| 5 | combined | diffusion_iv | rv_scaled | touch_family | brier | 265 | 53 | 0.144154 | 0.152724 | 0.008570 | -0.002359 | 0.019499 | -0.003479 | 0.020619 |
| 5 | combined | iv_scaled | empirical_exact | touch_family | brier | 265 | 53 | 0.147679 | 0.156019 | 0.008340 | -0.004993 | 0.021672 | -0.007396 | 0.024076 |
| 5 | combined | state_iv | empirical_exact | touch_family | brier | 265 | 53 | 0.148519 | 0.156019 | 0.007500 | -0.004563 | 0.019563 | -0.006934 | 0.021934 |
| 5 | combined | analytic_iv_diffusion | rv_scaled | touch_family | brier | 265 | 53 | 0.145264 | 0.152724 | 0.007460 | -0.003996 | 0.018916 | -0.005113 | 0.020033 |
| 5 | combined | random_state_iv | rv_scaled | touch_family | brier | 265 | 53 | 0.147156 | 0.152724 | 0.005568 | -0.001575 | 0.012712 | -0.002774 | 0.013911 |
| 5 | combined | iv_scaled | rv_scaled | touch_family | brier | 265 | 53 | 0.147679 | 0.152724 | 0.005045 | -0.001646 | 0.011737 | -0.002542 | 0.012633 |
| 5 | combined | state_iv | rv_scaled | touch_family | brier | 265 | 53 | 0.148519 | 0.152724 | 0.004206 | -0.002850 | 0.011262 | -0.003839 | 0.012250 |
| 5 | combined | diffusion_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.144154 | 0.147679 | 0.003524 | -0.005408 | 0.012457 | -0.006657 | 0.013706 |
| 5 | combined | analytic_iv_diffusion | iv_scaled | touch_family | brier | 265 | 53 | 0.145264 | 0.147679 | 0.002415 | -0.006735 | 0.011565 | -0.007849 | 0.012678 |
| 5 | combined | diffusion_iv | analytic_iv_diffusion | touch_family | brier | 265 | 53 | 0.144154 | 0.145264 | 0.001110 | -0.001061 | 0.003281 | -0.001051 | 0.003270 |
| 5 | combined | random_state_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.147156 | 0.147679 | 0.000523 | -0.001589 | 0.002635 | -0.001918 | 0.002964 |
| 5 | combined | state_iv | iv_scaled | touch_family | brier | 265 | 53 | 0.148519 | 0.147679 | -0.000840 | -0.003442 | 0.001763 | -0.003541 | 0.001862 |
| 5 | combined | random_state_iv | analytic_iv_diffusion | touch_family | brier | 265 | 53 | 0.147156 | 0.145264 | -0.001892 | -0.011291 | 0.007508 | -0.012505 | 0.008722 |
| 5 | combined | iv_scaled | analytic_iv_diffusion | touch_family | brier | 265 | 53 | 0.147679 | 0.145264 | -0.002415 | -0.011565 | 0.006735 | -0.012678 | 0.007849 |
| 5 | combined | state_iv | analytic_iv_diffusion | touch_family | brier | 265 | 53 | 0.148519 | 0.145264 | -0.003254 | -0.013095 | 0.006587 | -0.014331 | 0.007822 |
| 5 | combined | separate_barrier_logit | empirical_exact | touch_family | brier | 265 | 53 | 0.162306 | 0.156019 | -0.006287 | -0.021873 | 0.009299 | -0.021635 | 0.009061 |
| 5 | combined | separate_barrier_logit | rv_scaled | touch_family | brier | 265 | 53 | 0.162306 | 0.152724 | -0.009581 | -0.032219 | 0.013056 | -0.036204 | 0.017041 |
| 5 | combined | separate_barrier_logit | iv_scaled | touch_family | brier | 265 | 53 | 0.162306 | 0.147679 | -0.014627 | -0.037392 | 0.008139 | -0.041656 | 0.012402 |
| 5 | combined | separate_barrier_logit | analytic_iv_diffusion | touch_family | brier | 265 | 53 | 0.162306 | 0.145264 | -0.017041 | -0.042089 | 0.008006 | -0.046739 | 0.012656 |
| 5 | combined | diffusion_iv | empirical_exact | touch_family | log_loss | 265 | 53 | 0.438711 | 0.485526 | 0.046815 | -0.012748 | 0.106378 | -0.023418 | 0.117048 |
| 5 | combined | analytic_iv_diffusion | empirical_exact | touch_family | log_loss | 265 | 53 | 0.440291 | 0.485526 | 0.045234 | -0.015730 | 0.106198 | -0.026628 | 0.117097 |
| 5 | combined | random_state_iv | empirical_exact | touch_family | log_loss | 265 | 53 | 0.451690 | 0.485526 | 0.033836 | -0.025904 | 0.093575 | -0.038886 | 0.106557 |
| 5 | combined | iv_scaled | empirical_exact | touch_family | log_loss | 265 | 53 | 0.452616 | 0.485526 | 0.032909 | -0.022854 | 0.088672 | -0.034248 | 0.100066 |
| 5 | combined | state_iv | empirical_exact | touch_family | log_loss | 265 | 53 | 0.454745 | 0.485526 | 0.030781 | -0.022037 | 0.083598 | -0.033371 | 0.094932 |
| 5 | combined | diffusion_iv | rv_scaled | touch_family | log_loss | 265 | 53 | 0.438711 | 0.465005 | 0.026294 | -0.008078 | 0.060666 | -0.012657 | 0.065245 |
| 5 | combined | analytic_iv_diffusion | rv_scaled | touch_family | log_loss | 265 | 53 | 0.440291 | 0.465005 | 0.024713 | -0.011426 | 0.060853 | -0.016553 | 0.065980 |
| 5 | combined | diffusion_iv | iv_scaled | touch_family | log_loss | 265 | 53 | 0.438711 | 0.452616 | 0.013906 | -0.016134 | 0.043946 | -0.020817 | 0.048628 |
| 5 | combined | random_state_iv | rv_scaled | touch_family | log_loss | 265 | 53 | 0.451690 | 0.465005 | 0.013315 | -0.017575 | 0.044204 | -0.022223 | 0.048853 |
| 5 | combined | iv_scaled | rv_scaled | touch_family | log_loss | 265 | 53 | 0.452616 | 0.465005 | 0.012388 | -0.016952 | 0.041729 | -0.021008 | 0.045785 |
| 5 | combined | analytic_iv_diffusion | iv_scaled | touch_family | log_loss | 265 | 53 | 0.440291 | 0.452616 | 0.012325 | -0.020603 | 0.045253 | -0.025415 | 0.050065 |
| 5 | combined | state_iv | rv_scaled | touch_family | log_loss | 265 | 53 | 0.454745 | 0.465005 | 0.010260 | -0.020166 | 0.040685 | -0.024555 | 0.045075 |
| 5 | combined | diffusion_iv | analytic_iv_diffusion | touch_family | log_loss | 265 | 53 | 0.438711 | 0.440291 | 0.001581 | -0.005039 | 0.008200 | -0.005174 | 0.008335 |
| 5 | combined | random_state_iv | iv_scaled | touch_family | log_loss | 265 | 53 | 0.451690 | 0.452616 | 0.000926 | -0.005378 | 0.007231 | -0.006107 | 0.007959 |
| 5 | combined | state_iv | iv_scaled | touch_family | log_loss | 265 | 53 | 0.454745 | 0.452616 | -0.002129 | -0.009121 | 0.004864 | -0.009340 | 0.005083 |
| 5 | combined | random_state_iv | analytic_iv_diffusion | touch_family | log_loss | 265 | 53 | 0.451690 | 0.440291 | -0.011399 | -0.045657 | 0.022859 | -0.050868 | 0.028070 |
| 5 | combined | iv_scaled | analytic_iv_diffusion | touch_family | log_loss | 265 | 53 | 0.452616 | 0.440291 | -0.012325 | -0.045253 | 0.020603 | -0.050065 | 0.025415 |
| 5 | combined | separate_barrier_logit | empirical_exact | touch_family | log_loss | 265 | 53 | 0.498511 | 0.485526 | -0.012985 | -0.057245 | 0.031275 | -0.055226 | 0.029256 |
| 5 | combined | state_iv | analytic_iv_diffusion | touch_family | log_loss | 265 | 53 | 0.454745 | 0.440291 | -0.014454 | -0.048666 | 0.019758 | -0.053910 | 0.025002 |
| 5 | combined | separate_barrier_logit | rv_scaled | touch_family | log_loss | 265 | 53 | 0.498511 | 0.465005 | -0.033506 | -0.112697 | 0.045685 | -0.125268 | 0.058256 |
| 5 | combined | separate_barrier_logit | iv_scaled | touch_family | log_loss | 265 | 53 | 0.498511 | 0.452616 | -0.045894 | -0.124857 | 0.033068 | -0.138328 | 0.046539 |
| 5 | combined | separate_barrier_logit | analytic_iv_diffusion | touch_family | log_loss | 265 | 53 | 0.498511 | 0.440291 | -0.058219 | -0.140973 | 0.024534 | -0.154799 | 0.038360 |
| 21 | combined | analytic_iv_diffusion | empirical_exact | touch_family | brier | 217 | 11 | 0.184067 | 0.206812 | 0.022744 | -0.009410 | 0.054899 | -0.015199 | 0.060688 |
| 21 | combined | diffusion_iv | empirical_exact | touch_family | brier | 217 | 11 | 0.185037 | 0.206812 | 0.021775 | -0.009256 | 0.052805 | -0.014865 | 0.058414 |
| 21 | combined | analytic_iv_diffusion | rv_scaled | touch_family | brier | 217 | 11 | 0.184067 | 0.204506 | 0.020438 | -0.002189 | 0.043065 | -0.005282 | 0.046158 |
| 21 | combined | diffusion_iv | rv_scaled | touch_family | brier | 217 | 11 | 0.185037 | 0.204506 | 0.019468 | -0.002182 | 0.041119 | -0.004836 | 0.043773 |
| 21 | combined | analytic_iv_diffusion | iv_scaled | touch_family | brier | 217 | 11 | 0.184067 | 0.197163 | 0.013096 | -0.008393 | 0.034585 | -0.011174 | 0.037366 |
| 21 | combined | diffusion_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.185037 | 0.197163 | 0.012126 | -0.008300 | 0.032552 | -0.010727 | 0.034979 |
| 21 | combined | iv_scaled | empirical_exact | touch_family | brier | 217 | 11 | 0.197163 | 0.206812 | 0.009649 | -0.012029 | 0.031326 | -0.014147 | 0.033444 |
| 21 | combined | random_state_iv | empirical_exact | touch_family | brier | 217 | 11 | 0.197389 | 0.206812 | 0.009423 | -0.012467 | 0.031312 | -0.014415 | 0.033260 |
| 21 | combined | state_iv | empirical_exact | touch_family | brier | 217 | 11 | 0.197597 | 0.206812 | 0.009215 | -0.012518 | 0.030948 | -0.014496 | 0.032926 |
| 21 | combined | iv_scaled | rv_scaled | touch_family | brier | 217 | 11 | 0.197163 | 0.204506 | 0.007342 | -0.004035 | 0.018720 | -0.004978 | 0.019663 |
| 21 | combined | random_state_iv | rv_scaled | touch_family | brier | 217 | 11 | 0.197389 | 0.204506 | 0.007117 | -0.004169 | 0.018403 | -0.005098 | 0.019331 |
| 21 | combined | state_iv | rv_scaled | touch_family | brier | 217 | 11 | 0.197597 | 0.204506 | 0.006908 | -0.005906 | 0.019723 | -0.007779 | 0.021596 |
| 21 | combined | random_state_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.197389 | 0.197163 | -0.000226 | -0.002452 | 0.002000 | -0.002219 | 0.001767 |
| 21 | combined | state_iv | iv_scaled | touch_family | brier | 217 | 11 | 0.197597 | 0.197163 | -0.000434 | -0.005400 | 0.004532 | -0.005943 | 0.005075 |
| 21 | combined | diffusion_iv | analytic_iv_diffusion | touch_family | brier | 217 | 11 | 0.185037 | 0.184067 | -0.000970 | -0.003863 | 0.001924 | -0.004069 | 0.002130 |
| 21 | combined | iv_scaled | analytic_iv_diffusion | touch_family | brier | 217 | 11 | 0.197163 | 0.184067 | -0.013096 | -0.034585 | 0.008393 | -0.037366 | 0.011174 |
| 21 | combined | random_state_iv | analytic_iv_diffusion | touch_family | brier | 217 | 11 | 0.197389 | 0.184067 | -0.013322 | -0.035075 | 0.008432 | -0.037759 | 0.011116 |
| 21 | combined | state_iv | analytic_iv_diffusion | touch_family | brier | 217 | 11 | 0.197597 | 0.184067 | -0.013530 | -0.033705 | 0.006646 | -0.036900 | 0.009841 |
| 21 | combined | separate_barrier_logit | empirical_exact | touch_family | brier | 217 | 11 | 0.222898 | 0.206812 | -0.016086 | -0.055470 | 0.023298 | -0.060044 | 0.027872 |
| 21 | combined | separate_barrier_logit | rv_scaled | touch_family | brier | 217 | 11 | 0.222898 | 0.204506 | -0.018392 | -0.074395 | 0.037611 | -0.084812 | 0.048028 |
| 21 | combined | separate_barrier_logit | iv_scaled | touch_family | brier | 217 | 11 | 0.222898 | 0.197163 | -0.025734 | -0.077731 | 0.026262 | -0.086700 | 0.035231 |
| 21 | combined | separate_barrier_logit | analytic_iv_diffusion | touch_family | brier | 217 | 11 | 0.222898 | 0.184067 | -0.038830 | -0.096952 | 0.019292 | -0.109021 | 0.031361 |
| 21 | combined | analytic_iv_diffusion | empirical_exact | touch_family | log_loss | 217 | 11 | 0.552037 | 0.624294 | 0.072257 | -0.023915 | 0.168429 | -0.042210 | 0.186725 |
| 21 | combined | diffusion_iv | empirical_exact | touch_family | log_loss | 217 | 11 | 0.555374 | 0.624294 | 0.068920 | -0.024890 | 0.162730 | -0.042746 | 0.180585 |
| 21 | combined | analytic_iv_diffusion | rv_scaled | touch_family | log_loss | 217 | 11 | 0.552037 | 0.617312 | 0.065275 | -0.024194 | 0.154744 | -0.034172 | 0.164721 |
| 21 | combined | diffusion_iv | rv_scaled | touch_family | log_loss | 217 | 11 | 0.555374 | 0.617312 | 0.061937 | -0.025673 | 0.149548 | -0.034454 | 0.158329 |
| 21 | combined | analytic_iv_diffusion | iv_scaled | touch_family | log_loss | 217 | 11 | 0.552037 | 0.596912 | 0.044875 | -0.033202 | 0.122952 | -0.039561 | 0.129311 |
| 21 | combined | diffusion_iv | iv_scaled | touch_family | log_loss | 217 | 11 | 0.555374 | 0.596912 | 0.041537 | -0.034457 | 0.117531 | -0.039883 | 0.122958 |
| 21 | combined | iv_scaled | empirical_exact | touch_family | log_loss | 217 | 11 | 0.596912 | 0.624294 | 0.027382 | -0.042680 | 0.097445 | -0.050856 | 0.105621 |
| 21 | combined | state_iv | empirical_exact | touch_family | log_loss | 217 | 11 | 0.598258 | 0.624294 | 0.026036 | -0.041661 | 0.093732 | -0.049271 | 0.101343 |
| 21 | combined | random_state_iv | empirical_exact | touch_family | log_loss | 217 | 11 | 0.598857 | 0.624294 | 0.025437 | -0.045475 | 0.096349 | -0.052970 | 0.103844 |
| 21 | combined | iv_scaled | rv_scaled | touch_family | log_loss | 217 | 11 | 0.596912 | 0.617312 | 0.020400 | -0.022383 | 0.063183 | -0.028472 | 0.069272 |
| 21 | combined | state_iv | rv_scaled | touch_family | log_loss | 217 | 11 | 0.598258 | 0.617312 | 0.019053 | -0.027691 | 0.065797 | -0.036173 | 0.074280 |
| 21 | combined | random_state_iv | rv_scaled | touch_family | log_loss | 217 | 11 | 0.598857 | 0.617312 | 0.018455 | -0.025890 | 0.062800 | -0.031879 | 0.068788 |
| 21 | combined | state_iv | iv_scaled | touch_family | log_loss | 217 | 11 | 0.598258 | 0.596912 | -0.001347 | -0.016335 | 0.013641 | -0.018152 | 0.015458 |
| 21 | combined | random_state_iv | iv_scaled | touch_family | log_loss | 217 | 11 | 0.598857 | 0.596912 | -0.001945 | -0.009610 | 0.005719 | -0.008732 | 0.004842 |
| 21 | combined | diffusion_iv | analytic_iv_diffusion | touch_family | log_loss | 217 | 11 | 0.555374 | 0.552037 | -0.003337 | -0.011813 | 0.005138 | -0.012016 | 0.005341 |
| 21 | combined | iv_scaled | analytic_iv_diffusion | touch_family | log_loss | 217 | 11 | 0.596912 | 0.552037 | -0.044875 | -0.122952 | 0.033202 | -0.129311 | 0.039561 |
| 21 | combined | state_iv | analytic_iv_diffusion | touch_family | log_loss | 217 | 11 | 0.598258 | 0.552037 | -0.046222 | -0.118463 | 0.026020 | -0.125874 | 0.033431 |
| 21 | combined | random_state_iv | analytic_iv_diffusion | touch_family | log_loss | 217 | 11 | 0.598857 | 0.552037 | -0.046820 | -0.125536 | 0.031896 | -0.132178 | 0.038538 |
| 21 | combined | separate_barrier_logit | empirical_exact | touch_family | log_loss | 217 | 11 | 0.702002 | 0.624294 | -0.077708 | -0.244781 | 0.089365 | -0.266693 | 0.111277 |
| 21 | combined | separate_barrier_logit | rv_scaled | touch_family | log_loss | 217 | 11 | 0.702002 | 0.617312 | -0.084690 | -0.318460 | 0.149079 | -0.360575 | 0.191194 |
| 21 | combined | separate_barrier_logit | iv_scaled | touch_family | log_loss | 217 | 11 | 0.702002 | 0.596912 | -0.105090 | -0.324163 | 0.113983 | -0.360468 | 0.150287 |
| 21 | combined | separate_barrier_logit | analytic_iv_diffusion | touch_family | log_loss | 217 | 11 | 0.702002 | 0.552037 | -0.149965 | -0.380033 | 0.080102 | -0.424911 | 0.124981 |

[All barrier and order scores](barrier-leaderboard.csv) · [Calibration](barrier-calibration.csv) · [Ordering receipt](observed-order-resolution.csv).
