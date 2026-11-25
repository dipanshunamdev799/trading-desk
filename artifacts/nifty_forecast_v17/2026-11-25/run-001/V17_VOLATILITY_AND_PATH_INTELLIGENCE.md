# NIFTY V17 — Volatility and path intelligence

Volatility studies preserve separate point and expansion benchmarks. Weekly V16 offshore/domestic volatility MAE was **0.036469**, while raw ATM IV achieved **0.037814** with its own QLIKE. Monthly GJR-GARCH MAE was **0.033179**. The fixed IV/RV blend and Student-t EGARCH remain expansion benchmarks. V17 starts a same-clock cash-risk baseline from known implied volatility, observed opening gap and completed-prefix realized variance. Earlier fitted errors train the incremental opening-surprise, stock-participation, liquidity/disagreement and option-surface corrections. Expansion means realized volatility at least **1.25×** the original trailing volatility. The expansion classifier is separately calibrated. The joint path study separately samples a past cash-path suffix conditioned on the known open and path prefix, including the interval from the last available bar to the decision as unknown. Analog choices and IV scales only use earlier mature dates. The known cash prefix contributes observed highs and lows. The scenario archives preserve one coherent OHLC law per model and origin.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 09:25 | opening_surprise | cash_risk | brier | 263 | 53 | 0.225092 | 0.224636 | -0.000456 | -0.002213 | 0.001301 |
| 5 | 09:25 | opening_surprise | cash_risk | crps | 263 | 53 | 0.025355 | 0.026370 | 0.001015 | -0.001149 | 0.003178 |
| 5 | 09:25 | opening_surprise | cash_risk | abs_error | 263 | 53 | 0.036117 | 0.038648 | 0.002532 | -0.001499 | 0.006562 |
| 5 | 09:25 | opening_surprise | cash_risk | qlike | 263 | 53 | 0.269115 | 0.266156 | -0.002959 | -0.057395 | 0.051477 |
| 5 | 09:25 | participation | cash_risk | brier | 263 | 53 | 0.224597 | 0.224636 | 0.000039 | -0.001109 | 0.001186 |
| 5 | 09:25 | participation | cash_risk | crps | 263 | 53 | 0.025565 | 0.026370 | 0.000805 | -0.001332 | 0.002942 |
| 5 | 09:25 | participation | cash_risk | abs_error | 263 | 53 | 0.036685 | 0.038648 | 0.001963 | -0.002070 | 0.005997 |
| 5 | 09:25 | participation | cash_risk | qlike | 263 | 53 | 0.271087 | 0.266156 | -0.004931 | -0.058429 | 0.048567 |
| 5 | 09:25 | liquidity_disagreement | cash_risk | brier | 263 | 53 | 0.224520 | 0.224636 | 0.000115 | -0.001975 | 0.002206 |
| 5 | 09:25 | liquidity_disagreement | cash_risk | crps | 263 | 53 | 0.025421 | 0.026370 | 0.000949 | -0.001205 | 0.003104 |
| 5 | 09:25 | liquidity_disagreement | cash_risk | abs_error | 263 | 53 | 0.036550 | 0.038648 | 0.002098 | -0.001954 | 0.006150 |
| 5 | 09:25 | liquidity_disagreement | cash_risk | qlike | 263 | 53 | 0.267291 | 0.266156 | -0.001135 | -0.054269 | 0.052000 |
| 5 | 09:25 | option_surface | cash_risk | brier | 263 | 53 | 0.225833 | 0.224636 | -0.001198 | -0.002459 | 0.000064 |
| 5 | 09:25 | option_surface | cash_risk | crps | 263 | 53 | 0.025726 | 0.026370 | 0.000644 | -0.001738 | 0.003026 |
| 5 | 09:25 | option_surface | cash_risk | abs_error | 263 | 53 | 0.036875 | 0.038648 | 0.001773 | -0.002631 | 0.006177 |
| 5 | 09:25 | option_surface | cash_risk | qlike | 263 | 53 | 0.274232 | 0.266156 | -0.008076 | -0.068889 | 0.052738 |
| 5 | 09:25 | raw_IV | cash_risk | brier | 263 | 53 | 0.166847 | 0.224636 | 0.057789 | -0.003200 | 0.118779 |
| 5 | 09:25 | raw_IV | cash_risk | crps | 263 | 53 | 0.026686 | 0.026370 | -0.000316 | -0.001251 | 0.000619 |
| 5 | 09:25 | raw_IV | cash_risk | abs_error | 263 | 53 | 0.038688 | 0.038648 | -0.000040 | -0.001633 | 0.001553 |
| 5 | 09:25 | raw_IV | cash_risk | qlike | 263 | 53 | 0.274816 | 0.266156 | -0.008660 | -0.026667 | 0.009348 |
| 5 | 10:20 | opening_surprise | cash_risk | brier | 263 | 53 | 0.223954 | 0.223747 | -0.000208 | -0.001962 | 0.001547 |
| 5 | 10:20 | opening_surprise | cash_risk | crps | 263 | 53 | 0.025377 | 0.026490 | 0.001113 | -0.001111 | 0.003337 |
| 5 | 10:20 | opening_surprise | cash_risk | abs_error | 263 | 53 | 0.036206 | 0.038821 | 0.002615 | -0.001559 | 0.006789 |
| 5 | 10:20 | opening_surprise | cash_risk | qlike | 263 | 53 | 0.269001 | 0.267418 | -0.001583 | -0.055923 | 0.052757 |
| 5 | 10:20 | participation | cash_risk | brier | 263 | 53 | 0.223852 | 0.223747 | -0.000105 | -0.001447 | 0.001237 |
| 5 | 10:20 | participation | cash_risk | crps | 263 | 53 | 0.025487 | 0.026490 | 0.001003 | -0.001166 | 0.003173 |
| 5 | 10:20 | participation | cash_risk | abs_error | 263 | 53 | 0.036545 | 0.038821 | 0.002276 | -0.001893 | 0.006444 |
| 5 | 10:20 | participation | cash_risk | qlike | 263 | 53 | 0.269963 | 0.267418 | -0.002545 | -0.056735 | 0.051646 |
| 5 | 10:20 | liquidity_disagreement | cash_risk | brier | 263 | 53 | 0.223595 | 0.223747 | 0.000152 | -0.002521 | 0.002824 |
| 5 | 10:20 | liquidity_disagreement | cash_risk | crps | 263 | 53 | 0.025458 | 0.026490 | 0.001033 | -0.001182 | 0.003247 |
| 5 | 10:20 | liquidity_disagreement | cash_risk | abs_error | 263 | 53 | 0.036549 | 0.038821 | 0.002272 | -0.001846 | 0.006390 |
| 5 | 10:20 | liquidity_disagreement | cash_risk | qlike | 263 | 53 | 0.266873 | 0.267418 | 0.000545 | -0.052822 | 0.053913 |
| 5 | 10:20 | option_surface | cash_risk | brier | 263 | 53 | 0.224992 | 0.223747 | -0.001245 | -0.002488 | -1.39e-06 |
| 5 | 10:20 | option_surface | cash_risk | crps | 263 | 53 | 0.025757 | 0.026490 | 0.000733 | -0.001695 | 0.003160 |
| 5 | 10:20 | option_surface | cash_risk | abs_error | 263 | 53 | 0.036930 | 0.038821 | 0.001890 | -0.002603 | 0.006384 |
| 5 | 10:20 | option_surface | cash_risk | qlike | 263 | 53 | 0.274255 | 0.267418 | -0.006837 | -0.067836 | 0.054161 |
| 5 | 10:20 | raw_IV | cash_risk | brier | 263 | 53 | 0.166733 | 0.223747 | 0.057013 | -0.003863 | 0.117890 |
| 5 | 10:20 | raw_IV | cash_risk | crps | 263 | 53 | 0.026701 | 0.026490 | -0.000211 | -0.001199 | 0.000777 |

## Barrier risk sets and dispersion

The full-horizon touch law comes from the first observed crossing on simulated paths. The survival calculation restricts each observed origin × side × barrier to episodes surviving day one, and reconditions each simulated law on its own day-one survivors. The post-open analysis also restricts the comparison to barriers still untouched in the known cash prefix. `n` is the number of dates. The side-barrier counts retain additional evidence within each date and each bootstrap contribution first aggregates the identically eligible side-barrier comparisons within a date. Day 1, 3, 5, 10 and 21 Brier and passage-time log scores are archived where the horizon supports them.

| horizon | cutoff | screen | candidate | control | metric | n | side barrier cases | candidate loss | control loss | gain | lo21 | hi21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | original | decomposed_gift | decomposed | brier_by_1 | 265 | 2,650 | 0.054292 | 0.081817 | 0.027526 | 0.015710 | 0.044127 |
| 5 | preauction_0855 | original | decomposed_gift | decomposed | touch_brier | 265 | 2,650 | 0.132201 | 0.145973 | 0.013772 | 0.006225 | 0.023098 |
| 5 | preauction_0855 | original | decomposed_gift | decomposed | conditional_brier | 265 | 2,303 | 0.139330 | 0.143956 | 0.004626 | 0.000555 | 0.009380 |
| 5 | preauction_0855 | original | decomposed_gift | decomposed | integrated_brier | 265 | 2,650 | 0.100551 | 0.120942 | 0.020391 | 0.011673 | 0.031116 |
| 5 | preauction_0855 | original | decomposed_gift | same_clock_IV | brier_by_1 | 265 | 2,650 | 0.054292 | 0.082219 | 0.027927 | 0.016132 | 0.044222 |
| 5 | preauction_0855 | original | decomposed_gift | same_clock_IV | touch_brier | 265 | 2,650 | 0.132201 | 0.144562 | 0.012360 | 0.004793 | 0.021383 |
| 5 | preauction_0855 | original | decomposed_gift | same_clock_IV | conditional_brier | 265 | 2,303 | 0.139330 | 0.142857 | 0.003527 | -0.003468 | 0.011305 |
| 5 | preauction_0855 | original | decomposed_gift | same_clock_IV | integrated_brier | 265 | 2,650 | 0.100551 | 0.120331 | 0.019780 | 0.012275 | 0.029370 |
| 5 | previous_1700 | original | decomposed_gift | decomposed | brier_by_1 | 265 | 2,650 | 0.084341 | 0.084989 | 0.000648 | -0.002692 | 0.003690 |
| 5 | previous_1700 | original | decomposed_gift | decomposed | touch_brier | 265 | 2,650 | 0.146161 | 0.147623 | 0.001462 | -0.002259 | 0.005873 |
| 5 | previous_1700 | original | decomposed_gift | decomposed | conditional_brier | 265 | 2,305 | 0.144543 | 0.144608 | 0.000065 | -0.001798 | 0.002326 |
| 5 | previous_1700 | original | decomposed_gift | decomposed | integrated_brier | 265 | 2,650 | 0.121800 | 0.123227 | 0.001426 | -0.001775 | 0.005134 |
| 5 | previous_1700 | original | decomposed_gift | same_clock_IV | brier_by_1 | 265 | 2,650 | 0.084341 | 0.082219 | -0.002122 | -0.006830 | 0.001583 |
| 5 | previous_1700 | original | decomposed_gift | same_clock_IV | touch_brier | 265 | 2,650 | 0.146161 | 0.144562 | -0.001599 | -0.008477 | 0.004842 |
| 5 | previous_1700 | original | decomposed_gift | same_clock_IV | conditional_brier | 265 | 2,305 | 0.144543 | 0.143017 | -0.001525 | -0.008625 | 0.004704 |
| 5 | previous_1700 | original | decomposed_gift | same_clock_IV | integrated_brier | 265 | 2,650 | 0.121800 | 0.120331 | -0.001470 | -0.006619 | 0.003240 |
| 21 | preauction_0855 | original | decomposed_gift | decomposed | brier_by_1 | 217 | 2,170 | 0.052252 | 0.085112 | 0.032860 | 0.017024 | 0.052819 |
| 21 | preauction_0855 | original | decomposed_gift | decomposed | touch_brier | 217 | 2,170 | 0.184421 | 0.185829 | 0.001408 | -0.006045 | 0.009990 |
| 21 | preauction_0855 | original | decomposed_gift | decomposed | conditional_brier | 217 | 1,880 | 0.212578 | 0.212106 | -0.000473 | -0.008720 | 0.009147 |
| 21 | preauction_0855 | original | decomposed_gift | decomposed | integrated_brier | 217 | 2,170 | 0.149470 | 0.160756 | 0.011286 | 0.003350 | 0.020624 |
| 21 | preauction_0855 | original | decomposed_gift | same_clock_IV | brier_by_1 | 217 | 2,170 | 0.052252 | 0.084044 | 0.031792 | 0.017980 | 0.048695 |
| 21 | preauction_0855 | original | decomposed_gift | same_clock_IV | touch_brier | 217 | 2,170 | 0.184421 | 0.184372 | -0.000049 | -0.027312 | 0.029718 |
| 21 | preauction_0855 | original | decomposed_gift | same_clock_IV | conditional_brier | 217 | 1,880 | 0.212578 | 0.207689 | -0.004889 | -0.035844 | 0.029717 |
| 21 | preauction_0855 | original | decomposed_gift | same_clock_IV | integrated_brier | 217 | 2,170 | 0.149470 | 0.159680 | 0.010210 | -0.004929 | 0.026253 |
| 21 | previous_1700 | original | decomposed_gift | decomposed | brier_by_1 | 217 | 2,170 | 0.086684 | 0.088720 | 0.002035 | -0.001359 | 0.005321 |
| 21 | previous_1700 | original | decomposed_gift | decomposed | touch_brier | 217 | 2,170 | 0.186245 | 0.187188 | 0.000943 | -0.003078 | 0.004694 |
| 21 | previous_1700 | original | decomposed_gift | decomposed | conditional_brier | 217 | 1,882 | 0.212335 | 0.213506 | 0.001171 | -0.002884 | 0.005073 |
| 21 | previous_1700 | original | decomposed_gift | decomposed | integrated_brier | 217 | 2,170 | 0.160658 | 0.162348 | 0.001689 | -0.002233 | 0.005909 |
| 21 | previous_1700 | original | decomposed_gift | same_clock_IV | brier_by_1 | 217 | 2,170 | 0.086684 | 0.084044 | -0.002640 | -0.008766 | 0.002628 |
| 21 | previous_1700 | original | decomposed_gift | same_clock_IV | touch_brier | 217 | 2,170 | 0.186245 | 0.184372 | -0.001872 | -0.027507 | 0.028329 |
| 21 | previous_1700 | original | decomposed_gift | same_clock_IV | conditional_brier | 217 | 1,882 | 0.212335 | 0.207997 | -0.004338 | -0.034281 | 0.029841 |
| 21 | previous_1700 | original | decomposed_gift | same_clock_IV | integrated_brier | 217 | 2,170 | 0.160658 | 0.159680 | -0.000979 | -0.015976 | 0.016575 |

| horizon | cutoff | screen | candidate | control | metric | n | side barrier cases | candidate loss | control loss | gain | lo21 | hi21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | brier_by_1 | 263 | 2,478 | 0.044069 | 0.043506 | -0.000563 | -0.001229 | 0.000131 |
| 5 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 263 | 2,478 | 0.135569 | 0.134899 | -0.000670 | -0.003107 | 0.001345 |
| 5 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | conditional_brier | 263 | 2,285 | 0.138481 | 0.137867 | -0.000614 | -0.003366 | 0.001548 |
| 5 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | integrated_brier | 263 | 2,478 | 0.099705 | 0.099007 | -0.000698 | -0.002090 | 0.000459 |
| 5 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | brier_by_1 | 263 | 2,424 | 0.033378 | 0.032970 | -0.000407 | -0.000845 | 0.000039 |
| 5 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 263 | 2,424 | 0.130238 | 0.132186 | 0.001948 | 0.000209 | 0.003805 |
| 5 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | conditional_brier | 263 | 2,285 | 0.132953 | 0.134960 | 0.002007 | 0.000165 | 0.004168 |
| 5 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | integrated_brier | 263 | 2,424 | 0.092095 | 0.092867 | 0.000772 | -0.000088 | 0.001638 |
| 21 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | brier_by_1 | 217 | 2,033 | 0.041562 | 0.041526 | -0.000036 | -0.000690 | 0.000502 |
| 21 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 217 | 2,033 | 0.198405 | 0.198510 | 0.000104 | -0.002073 | 0.002290 |
| 21 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | conditional_brier | 217 | 1,882 | 0.213167 | 0.213054 | -0.000113 | -0.002360 | 0.002223 |
| 21 | 09:25 | prefix_survivor | cash_IV_stock | cash_IV | integrated_brier | 217 | 2,033 | 0.155682 | 0.156787 | 0.001105 | -0.000234 | 0.002701 |
| 21 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | brier_by_1 | 217 | 1,990 | 0.032232 | 0.032411 | 0.000179 | -0.000329 | 0.000642 |
| 21 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | touch_brier | 217 | 1,990 | 0.197995 | 0.198789 | 0.000794 | -0.001815 | 0.003274 |
| 21 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | conditional_brier | 217 | 1,882 | 0.208823 | 0.209678 | 0.000855 | -0.001739 | 0.003381 |
| 21 | 10:20 | prefix_survivor | cash_IV_stock | cash_IV | integrated_brier | 217 | 1,990 | 0.154572 | 0.155888 | 0.001316 | -0.000493 | 0.003750 |

## Monte Carlo convergence

The V16 GIFT-first and session-state methods were redrawn at **256, 2,048 and 8,192** paths on **32 fixed origins per horizon**, for **384 model/origin/draw-count combinations**. Each 256-path archive reproduced exactly. The random uniforms use nested prefixes across path counts to reduce comparison noise. Sample centering inside the archived models causes some paths to move when the number of samples changes. RMS and median absolute deviations from 8,192 measure simulation sensitivity on the fixed dates. Forecast uncertainty remains the underlying predictive distribution’s spread.

| horizon | model | metric | paths | origins | average | median abs MC delta | rms MC delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | decomposed_gift | brier | 256 | 32 | 0.213023 | 0.017363 | 0.029165 |
| 5 | decomposed_gift | brier | 2,048 | 32 | 0.215189 | 0.005328 | 0.011349 |
| 5 | decomposed_gift | brier | 8,192 | 32 | 0.212362 | 0.000000 | 0.000000 |
| 5 | decomposed_gift | endpoint_crps | 256 | 32 | 0.009438 | 0.000308 | 0.000570 |
| 5 | decomposed_gift | endpoint_crps | 2,048 | 32 | 0.009522 | 0.000101 | 0.000229 |
| 5 | decomposed_gift | endpoint_crps | 8,192 | 32 | 0.009475 | 0.000000 | 0.000000 |
| 5 | decomposed_gift | range_crps | 256 | 32 | 0.004863 | 0.000107 | 0.000348 |
| 5 | decomposed_gift | range_crps | 2,048 | 32 | 0.004888 | 0.000048 | 0.000102 |
| 5 | decomposed_gift | range_crps | 8,192 | 32 | 0.004859 | 0.000000 | 0.000000 |
| 5 | decomposed_gift | touch_brier | 256 | 32 | 0.105319 | 0.004548 | 0.007655 |
| 5 | decomposed_gift | touch_brier | 2,048 | 32 | 0.105831 | 0.001682 | 0.003302 |
| 5 | decomposed_gift | touch_brier | 8,192 | 32 | 0.106677 | 0.000000 | 0.000000 |
| 5 | decomposed_gift | day_one_Brier | 256 | 32 | 0.057788 | 0.002494 | 0.005297 |
| 5 | decomposed_gift | day_one_Brier | 2,048 | 32 | 0.058101 | 0.001083 | 0.002304 |
| 5 | decomposed_gift | day_one_Brier | 8,192 | 32 | 0.058054 | 0.000000 | 0.000000 |
| 5 | decomposed_gift | survivor_Brier | 256 | 32 | 0.111987 | 0.004086 | 0.007451 |
| 5 | decomposed_gift | survivor_Brier | 2,048 | 32 | 0.113250 | 0.002634 | 0.003519 |
| 5 | decomposed_gift | survivor_Brier | 8,192 | 32 | 0.113545 | 0.000000 | 0.000000 |
| 5 | session_state | brier | 256 | 32 | 0.209444 | 0.014270 | 0.024545 |
| 5 | session_state | brier | 2,048 | 32 | 0.211005 | 0.006293 | 0.019361 |
| 5 | session_state | brier | 8,192 | 32 | 0.208709 | 0.000000 | 0.000000 |
| 5 | session_state | endpoint_crps | 256 | 32 | 0.009700 | 0.000318 | 0.001033 |
| 5 | session_state | endpoint_crps | 2,048 | 32 | 0.009541 | 0.000116 | 0.000386 |
| 5 | session_state | endpoint_crps | 8,192 | 32 | 0.009597 | 0.000000 | 0.000000 |
| 5 | session_state | range_crps | 256 | 32 | 0.004672 | 0.000164 | 0.000497 |
| 5 | session_state | range_crps | 2,048 | 32 | 0.004621 | 0.000061 | 0.000124 |
| 5 | session_state | range_crps | 8,192 | 32 | 0.004606 | 0.000000 | 0.000000 |
| 5 | session_state | touch_brier | 256 | 32 | 0.106379 | 0.003807 | 0.009701 |
| 5 | session_state | touch_brier | 2,048 | 32 | 0.104841 | 0.001152 | 0.003382 |
| 5 | session_state | touch_brier | 8,192 | 32 | 0.104641 | 0.000000 | 0.000000 |
| 5 | session_state | day_one_Brier | 256 | 32 | 0.058172 | 0.002895 | 0.004916 |
| 5 | session_state | day_one_Brier | 2,048 | 32 | 0.059138 | 0.000802 | 0.001816 |
| 5 | session_state | day_one_Brier | 8,192 | 32 | 0.059326 | 0.000000 | 0.000000 |
| 5 | session_state | survivor_Brier | 256 | 32 | 0.113951 | 0.005911 | 0.012258 |
| 5 | session_state | survivor_Brier | 2,048 | 32 | 0.111587 | 0.001947 | 0.004447 |
| 5 | session_state | survivor_Brier | 8,192 | 32 | 0.111578 | 0.000000 | 0.000000 |
| 21 | decomposed_gift | brier | 256 | 32 | 0.337682 | 0.015450 | 0.031614 |
| 21 | decomposed_gift | brier | 2,048 | 32 | 0.348754 | 0.012038 | 0.019912 |
| 21 | decomposed_gift | brier | 8,192 | 32 | 0.345899 | 0.000000 | 0.000000 |
| 21 | decomposed_gift | endpoint_crps | 256 | 32 | 0.029151 | 0.000404 | 0.001081 |
| 21 | decomposed_gift | endpoint_crps | 2,048 | 32 | 0.029284 | 0.000298 | 0.000416 |
| 21 | decomposed_gift | endpoint_crps | 8,192 | 32 | 0.029260 | 0.000000 | 0.000000 |
| 21 | decomposed_gift | range_crps | 256 | 32 | 0.018603 | 0.000313 | 0.000857 |
| 21 | decomposed_gift | range_crps | 2,048 | 32 | 0.018286 | 0.000211 | 0.000413 |
| 21 | decomposed_gift | range_crps | 8,192 | 32 | 0.018293 | 0.000000 | 0.000000 |
| 21 | decomposed_gift | touch_brier | 256 | 32 | 0.201787 | 0.004606 | 0.010239 |
| 21 | decomposed_gift | touch_brier | 2,048 | 32 | 0.202350 | 0.002630 | 0.004536 |
| 21 | decomposed_gift | touch_brier | 8,192 | 32 | 0.202016 | 0.000000 | 0.000000 |
| 21 | decomposed_gift | day_one_Brier | 256 | 32 | 0.074196 | 0.001877 | 0.004695 |
| 21 | decomposed_gift | day_one_Brier | 2,048 | 32 | 0.072392 | 0.001208 | 0.001616 |
| 21 | decomposed_gift | day_one_Brier | 8,192 | 32 | 0.072303 | 0.000000 | 0.000000 |
| 21 | decomposed_gift | survivor_Brier | 256 | 32 | 0.228421 | 0.006166 | 0.012587 |
| 21 | decomposed_gift | survivor_Brier | 2,048 | 32 | 0.227858 | 0.003576 | 0.006192 |
| 21 | decomposed_gift | survivor_Brier | 8,192 | 32 | 0.227508 | 0.000000 | 0.000000 |
| 21 | session_state | brier | 256 | 32 | 0.334115 | 0.015251 | 0.046015 |
| 21 | session_state | brier | 2,048 | 32 | 0.337013 | 0.006046 | 0.020401 |
| 21 | session_state | brier | 8,192 | 32 | 0.339653 | 0.000000 | 0.000000 |
| 21 | session_state | endpoint_crps | 256 | 32 | 0.028789 | 0.000518 | 0.001583 |
| 21 | session_state | endpoint_crps | 2,048 | 32 | 0.029023 | 0.000293 | 0.000504 |
| 21 | session_state | endpoint_crps | 8,192 | 32 | 0.029125 | 0.000000 | 0.000000 |
| 21 | session_state | range_crps | 256 | 32 | 0.017844 | 0.000375 | 0.000851 |
| 21 | session_state | range_crps | 2,048 | 32 | 0.017860 | 0.000183 | 0.000355 |
| 21 | session_state | range_crps | 8,192 | 32 | 0.017909 | 0.000000 | 0.000000 |
| 21 | session_state | touch_brier | 256 | 32 | 0.196049 | 0.008241 | 0.016123 |
| 21 | session_state | touch_brier | 2,048 | 32 | 0.196508 | 0.003434 | 0.006101 |
| 21 | session_state | touch_brier | 8,192 | 32 | 0.196340 | 0.000000 | 0.000000 |
| 21 | session_state | day_one_Brier | 256 | 32 | 0.072556 | 0.003358 | 0.006684 |
| 21 | session_state | day_one_Brier | 2,048 | 32 | 0.070101 | 0.000862 | 0.002907 |
| 21 | session_state | day_one_Brier | 8,192 | 32 | 0.070232 | 0.000000 | 0.000000 |
| 21 | session_state | survivor_Brier | 256 | 32 | 0.220719 | 0.012780 | 0.021202 |
| 21 | session_state | survivor_Brier | 2,048 | 32 | 0.221486 | 0.004536 | 0.007102 |
| 21 | session_state | survivor_Brier | 8,192 | 32 | 0.220868 | 0.000000 | 0.000000 |

[Inherited volatility benchmarks](../../../nifty_forecast_v16/2026-11-25/run-001/volatility-leaderboard.csv) · [Post-open volatility comparisons](postopen-volatility-matched.csv) · [Post-open joint paths and receipt](postopen-path-archive.json) · [Monte Carlo evidence](path-convergence-summary.csv) · [Convergence archive locations](path-convergence-archive.json) · [Matched day-one and surviving paths](retimed-barrier-matched.csv) · [Post-open conditional barrier comparison](postopen-barrier-matched.csv)
