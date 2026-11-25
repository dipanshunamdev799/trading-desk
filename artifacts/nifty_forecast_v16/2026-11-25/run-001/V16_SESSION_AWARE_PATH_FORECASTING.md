# V16 Session-aware OHLC paths

Each joint law generates a whole open, high, low and close path relative to the original official close. Overnight and regular increments have separate predicted locations and first-gap uncertainty, preserving empirical signed covariance. Shifts preserve the candle constraints by maintaining excursions around the adjusted open and close. Future daily volatility evolves with simulated return and an earlier IV/GJR state. Foreign and financial leadership are modeled through joint draws of earlier resolved state blocks. The same ensemble produces the endpoint, highs, lows, range, volatility, barriers, drawdown and rebound. Energy is a normalized four-dimensional score for endpoint, range, volatility and drawdown. Every joint model generated **256** atoms per each of **482** original windows. Archived V14 and V15 joint laws, including both predecessor barrier leaders, are re-scored on the same reference and target.

## Joint marginals and proper scores

| horizon | model | n | range crps | range coverage80 | vol mae | touch brier | integrated brier | drawdown crps | energy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_constant_iv | 265 | 0.005795 | 0.716981 | 0.036961 | 0.144532 | 0.120174 | 0.005926 | 0.673829 |
| 5 | V14_gjr_iv | 265 | 0.005850 | 0.788679 | 0.037394 | 0.145105 | 0.120214 | 0.005997 | 0.679282 |
| 5 | V14_gjr_student | 265 | 0.006432 | 0.773585 | 0.040339 | 0.148325 | 0.122066 | 0.006002 | 0.702839 |
| 5 | V14_iv_scaled_blocks | 265 | 0.006098 | 0.754717 | 0.039143 | 0.148755 | 0.122931 | 0.006281 | 0.708176 |
| 5 | V14_trend_persistent | 265 | 0.005872 | 0.781132 | 0.037422 | 0.144178 | 0.119660 | 0.005959 | 0.678365 |
| 5 | V14_trend_shrink | 265 | 0.005801 | 0.720755 | 0.037001 | 0.143371 | 0.119424 | 0.005913 | 0.672452 |
| 5 | V15_gjr_restart | 265 | 0.006493 | 0.766038 | 0.040097 | 0.148396 | 0.122458 | 0.005956 | 0.697903 |
| 5 | V15_iv_restart | 265 | 0.005795 | 0.743396 | 0.037205 | 0.144592 | 0.120264 | 0.005942 | 0.670200 |
| 5 | decomposed | 265 | 0.006197 | 0.769811 | 0.040712 | 0.145973 | 0.120942 | 0.006071 | 0.693960 |
| 5 | decomposed_gift | 265 | 0.006209 | 0.769811 | 0.038994 | 0.132201 | 0.100551 | 0.005887 | 0.672264 |
| 5 | fixed_mixture | 265 | 0.006209 | 0.762264 | 0.039926 | 0.137431 | 0.109601 | 0.005958 | 0.677746 |
| 5 | multitask | 265 | 0.006302 | 0.739623 | 0.041084 | 0.151162 | 0.124131 | 0.006501 | 0.724639 |
| 5 | session_state | 265 | 0.006057 | 0.754717 | 0.036582 | 0.132616 | 0.100939 | 0.005851 | 0.663195 |
| 21 | V14_constant_iv | 217 | 0.017280 | 0.566820 | 0.040072 | 0.185046 | 0.159814 | 0.015383 | 0.796607 |
| 21 | V14_gjr_iv | 217 | 0.016304 | 0.640553 | 0.037475 | 0.183138 | 0.159133 | 0.014867 | 0.779156 |
| 21 | V14_gjr_student | 217 | 0.015422 | 0.764977 | 0.037813 | 0.183636 | 0.160668 | 0.014301 | 0.770958 |
| 21 | V14_iv_scaled_blocks | 217 | 0.017743 | 0.728111 | 0.041101 | 0.198752 | 0.165952 | 0.016425 | 0.854681 |
| 21 | V14_trend_persistent | 217 | 0.016309 | 0.640553 | 0.037480 | 0.181085 | 0.157875 | 0.014864 | 0.780724 |
| 21 | V14_trend_shrink | 217 | 0.017266 | 0.571429 | 0.040087 | 0.182220 | 0.158161 | 0.015529 | 0.798757 |
| 21 | V15_gjr_restart | 217 | 0.015488 | 0.737327 | 0.037244 | 0.183861 | 0.161061 | 0.014113 | 0.766246 |
| 21 | V15_iv_restart | 217 | 0.016288 | 0.612903 | 0.039209 | 0.183126 | 0.159269 | 0.014889 | 0.778134 |
| 21 | decomposed | 217 | 0.018551 | 0.691244 | 0.044261 | 0.185829 | 0.160756 | 0.016086 | 0.853027 |
| 21 | decomposed_gift | 217 | 0.018570 | 0.691244 | 0.044048 | 0.184421 | 0.149470 | 0.016041 | 0.858223 |
| 21 | fixed_mixture | 217 | 0.018592 | 0.700461 | 0.044075 | 0.185646 | 0.154611 | 0.015985 | 0.851681 |
| 21 | multitask | 217 | 0.018440 | 0.700461 | 0.044278 | 0.190638 | 0.163094 | 0.016362 | 0.870555 |
| 21 | session_state | 217 | 0.018090 | 0.654378 | 0.040394 | 0.180163 | 0.149012 | 0.015738 | 0.845088 |

## Age of the barrier benefit

| horizon | candidate | control | metric | n | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | decomposed_gift | V14_trend_shrink | touch_brier | 265 | 0.132201 | 0.143371 | 0.011169 | 0.002519 | 0.019820 |
| 5 | decomposed_gift | V14_trend_shrink | integrated_brier | 265 | 0.100551 | 0.119424 | 0.018873 | 0.009628 | 0.028119 |
| 5 | decomposed_gift | V14_trend_shrink | brier_by_1 | 265 | 0.054292 | 0.081827 | 0.027535 | 0.012251 | 0.042819 |
| 5 | decomposed_gift | V14_trend_shrink | brier_by_3 | 265 | 0.106793 | 0.125427 | 0.018635 | 0.010231 | 0.027038 |
| 5 | decomposed_gift | V14_trend_shrink | brier_by_5 | 265 | 0.132201 | 0.143371 | 0.011169 | 0.002519 | 0.019820 |
| 5 | session_state | V14_trend_shrink | touch_brier | 265 | 0.132616 | 0.143371 | 0.010755 | 0.001802 | 0.019707 |
| 5 | session_state | V14_trend_shrink | integrated_brier | 265 | 0.100939 | 0.119424 | 0.018484 | 0.009360 | 0.027609 |
| 5 | session_state | V14_trend_shrink | brier_by_1 | 265 | 0.054621 | 0.081827 | 0.027206 | 0.012727 | 0.041684 |
| 5 | session_state | V14_trend_shrink | brier_by_3 | 265 | 0.107000 | 0.125427 | 0.018427 | 0.010078 | 0.026776 |
| 5 | session_state | V14_trend_shrink | brier_by_5 | 265 | 0.132616 | 0.143371 | 0.010755 | 0.001802 | 0.019707 |
| 21 | decomposed_gift | V14_trend_persistent | touch_brier | 217 | 0.184421 | 0.181085 | -0.003336 | -0.036356 | 0.029684 |
| 21 | decomposed_gift | V14_trend_persistent | integrated_brier | 217 | 0.149470 | 0.157875 | 0.008405 | -0.008730 | 0.025540 |
| 21 | decomposed_gift | V14_trend_persistent | brier_by_1 | 217 | 0.052252 | 0.083008 | 0.030756 | 0.014047 | 0.047465 |
| 21 | decomposed_gift | V14_trend_persistent | brier_by_3 | 217 | 0.106520 | 0.126840 | 0.020320 | 0.012291 | 0.028349 |
| 21 | decomposed_gift | V14_trend_persistent | brier_by_5 | 217 | 0.129786 | 0.142556 | 0.012770 | 0.002989 | 0.022551 |
| 21 | session_state | V14_trend_persistent | touch_brier | 217 | 0.180163 | 0.181085 | 0.000922 | -0.028352 | 0.030196 |
| 21 | session_state | V14_trend_persistent | integrated_brier | 217 | 0.149012 | 0.157875 | 0.008863 | -0.005376 | 0.023101 |
| 21 | session_state | V14_trend_persistent | brier_by_1 | 217 | 0.051476 | 0.083008 | 0.031532 | 0.014975 | 0.048088 |
| 21 | session_state | V14_trend_persistent | brier_by_3 | 217 | 0.106745 | 0.126840 | 0.020094 | 0.012531 | 0.027657 |
| 21 | session_state | V14_trend_persistent | brier_by_5 | 217 | 0.131061 | 0.142556 | 0.011495 | 0.002845 | 0.020145 |
| 5 | decomposed_gift | V14_trend_shrink | conditional_brier | 265 | 0.139330 | 0.141434 | 0.002104 | -0.004448 | 0.008657 |
| 5 | session_state | V14_trend_shrink | conditional_brier | 265 | 0.140301 | 0.141434 | 0.001133 | -0.006805 | 0.009071 |
| 21 | decomposed_gift | V14_trend_persistent | conditional_brier | 217 | 0.212578 | 0.204420 | -0.008159 | -0.045693 | 0.029376 |
| 21 | session_state | V14_trend_persistent | conditional_brier | 217 | 0.207446 | 0.204325 | -0.003121 | -0.036844 | 0.030602 |

## Matched risk and range tests

| horizon | candidate | control | metric | n | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | decomposed_gift | V14_gjr_student | range_crps | 265 | 0.000223 | -0.000756 | 0.001203 |
| 5 | decomposed_gift | V14_gjr_student | vol_mae | 265 | 0.001345 | -0.003117 | 0.005807 |
| 5 | decomposed_gift | V14_gjr_student | energy | 265 | 0.030575 | -0.033675 | 0.094825 |
| 5 | decomposed_gift | V15_iv_restart | range_crps | 265 | -0.000413 | -0.001143 | 0.000317 |
| 5 | decomposed_gift | V15_iv_restart | vol_mae | 265 | -0.001789 | -0.007604 | 0.004027 |
| 5 | decomposed_gift | V15_iv_restart | energy | 265 | -0.002064 | -0.051584 | 0.047455 |
| 5 | decomposed_gift | decomposed | range_crps | 265 | -0.000011 | -0.000034 | 0.000012 |
| 5 | decomposed_gift | decomposed | vol_mae | 265 | 0.001718 | -0.001735 | 0.005170 |
| 5 | decomposed_gift | decomposed | energy | 265 | 0.021696 | -0.017156 | 0.060548 |
| 5 | session_state | V14_gjr_student | range_crps | 265 | 0.000375 | -0.000326 | 0.001077 |
| 5 | session_state | V14_gjr_student | vol_mae | 265 | 0.003756 | -0.001093 | 0.008605 |
| 5 | session_state | V14_gjr_student | energy | 265 | 0.039644 | -0.017492 | 0.096780 |
| 5 | session_state | V15_iv_restart | range_crps | 265 | -0.000261 | -0.000763 | 0.000240 |
| 5 | session_state | V15_iv_restart | vol_mae | 265 | 0.000623 | -0.003417 | 0.004663 |
| 5 | session_state | V15_iv_restart | energy | 265 | 0.007005 | -0.030159 | 0.044168 |
| 5 | session_state | decomposed | range_crps | 265 | 0.000141 | -0.000369 | 0.000650 |
| 5 | session_state | decomposed | vol_mae | 265 | 0.004129 | -0.003884 | 0.012142 |
| 5 | session_state | decomposed | energy | 265 | 0.030765 | -0.024964 | 0.086493 |
| 21 | decomposed_gift | V14_gjr_student | range_crps | 217 | -0.003149 | -0.008271 | 0.001973 |
| 21 | decomposed_gift | V14_gjr_student | vol_mae | 217 | -0.006236 | -0.020169 | 0.007697 |
| 21 | decomposed_gift | V14_gjr_student | energy | 217 | -0.087265 | -0.212982 | 0.038452 |
| 21 | decomposed_gift | V15_iv_restart | range_crps | 217 | -0.002282 | -0.005847 | 0.001283 |
| 21 | decomposed_gift | V15_iv_restart | vol_mae | 217 | -0.004839 | -0.012934 | 0.003256 |
| 21 | decomposed_gift | V15_iv_restart | energy | 217 | -0.080089 | -0.214025 | 0.053848 |
| 21 | decomposed_gift | decomposed | range_crps | 217 | -0.000020 | -0.000095 | 0.000056 |
| 21 | decomposed_gift | decomposed | vol_mae | 217 | 0.000213 | -0.000932 | 0.001359 |
| 21 | decomposed_gift | decomposed | energy | 217 | -0.005196 | -0.021450 | 0.011058 |
| 21 | session_state | V14_gjr_student | range_crps | 217 | -0.002668 | -0.007355 | 0.002018 |
| 21 | session_state | V14_gjr_student | vol_mae | 217 | -0.002582 | -0.013611 | 0.008447 |
| 21 | session_state | V14_gjr_student | energy | 217 | -0.074130 | -0.200063 | 0.051803 |
| 21 | session_state | V15_iv_restart | range_crps | 217 | -0.001802 | -0.005035 | 0.001432 |
| 21 | session_state | V15_iv_restart | vol_mae | 217 | -0.001185 | -0.010408 | 0.008037 |
| 21 | session_state | V15_iv_restart | energy | 217 | -0.066954 | -0.201271 | 0.067364 |
| 21 | session_state | decomposed | range_crps | 217 | 0.000461 | -0.001060 | 0.001982 |
| 21 | session_state | decomposed | vol_mae | 217 | 0.003867 | -0.001513 | 0.009247 |
| 21 | session_state | decomposed | energy | 217 | 0.007939 | -0.014230 | 0.030107 |

Passage probabilities come from the cumulative first occurrence on each path. We use five fixed up/down barrier pairs from 0.5% to 5%. The barrier probability test at day one, later cumulative tests and the event-by-end score all use the same root. The conditional table scores only realized survivors that remained untouched after session one, conditioning each law on the corresponding survival event. An early hit remains resolved. The improvement concentrated in first-session timing, while the range and residual monthly horizon remained difficult. Side-level survival counts, numerical monotonicity checks and archive hashes are preserved.

[Path archive format and hashes](path-archive.json) · [All per-origin joint marginal scores](path-scores.csv.gz) · [First touch and after-day-one survival](path-passage-scores.csv.gz) · [By-session comparison](passage-by-session.csv) · [Matched timing gains](passage-age-matched.csv) · [Common surviving barrier support](passage-conditional-support.csv) · [Previous exact joint laws](../../../nifty_forecast_v15/2026-11-25/run-001/NIFTY_V15_RESEARCH.md)
