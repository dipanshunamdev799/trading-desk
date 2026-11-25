# V14 Intraday Volatility Structure

Only audited complete bars contribute to session-level measurements. Features include opening gaps, first hour, midday and last-hour variance shares, bipower excess, up/down semivariance, reversal and directional persistence, relative excursions, and inherited synchronized sector factors. Overnight, regular-session and close-to-close variance remain separate. The frozen cash close anchors every outcome.

| interval | firsthour_share | midday_share | closing_share | upshare | downshare | sign_consistency | var_concentration | max_abs_intraday |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.360606 | 0.479002 | 0.160391 | 0.499459 | 0.500541 | 0.498939 | 0.041226 | 0.002007 |
| 5 | 0.360612 | 0.486971 | 0.152417 | 0.495192 | 0.504808 | 0.490108 | 0.091348 | 0.002633 |

| horizon | cohort | model | n | disjoint | mae | rmse | qlike | bias | rank_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | har | 265 | 53 | 0.048371 | 0.068361 | 0.526069 | -0.007586 | 0.476946 |
| 5 | early | har | 173 | 35 | 0.050697 | 0.075350 | 0.540296 | -0.007740 | 0.553717 |
| 5 | later | har | 92 | 19 | 0.043998 | 0.052772 | 0.499318 | -0.007296 | 0.331273 |
| 5 | combined | har_iv | 265 | 53 | 0.040951 | 0.054617 | 0.402545 | -0.007734 | 0.564322 |
| 5 | early | har_iv | 173 | 35 | 0.041936 | 0.057044 | 0.397941 | -0.005885 | 0.623360 |
| 5 | later | har_iv | 92 | 19 | 0.039098 | 0.049733 | 0.411203 | -0.011211 | 0.438250 |
| 5 | combined | intraday_har | 265 | 53 | 0.040036 | 0.052919 | 0.393189 | -0.008708 | 0.570104 |
| 5 | early | intraday_har | 173 | 35 | 0.040802 | 0.054677 | 0.386035 | -0.006916 | 0.613370 |
| 5 | later | intraday_har | 92 | 19 | 0.038597 | 0.049443 | 0.406641 | -0.012079 | 0.465746 |
| 5 | combined | latent_kalman | 265 | 53 | 0.040317 | 0.056154 | 0.429234 | -0.019689 | 0.588232 |
| 5 | early | latent_kalman | 173 | 35 | 0.040490 | 0.057243 | 0.370382 | -0.019382 | 0.653019 |
| 5 | later | latent_kalman | 92 | 19 | 0.039994 | 0.054046 | 0.539900 | -0.020266 | 0.462679 |
| 5 | combined | offshore_gap | 265 | 53 | 0.039947 | 0.053864 | 0.424555 | -0.012221 | 0.586514 |
| 5 | early | offshore_gap | 173 | 35 | 0.041353 | 0.056497 | 0.453306 | -0.010995 | 0.608719 |
| 5 | later | offshore_gap | 92 | 19 | 0.037304 | 0.048525 | 0.370489 | -0.014526 | 0.529060 |
| 5 | combined | overnight_decomposition | 265 | 53 | 0.041350 | 0.054420 | 0.397445 | -0.013580 | 0.601074 |
| 5 | early | overnight_decomposition | 173 | 35 | 0.043205 | 0.057533 | 0.419749 | -0.013365 | 0.624945 |
| 5 | later | overnight_decomposition | 92 | 19 | 0.037862 | 0.048022 | 0.355503 | -0.013985 | 0.567144 |
| 5 | combined | raw_iv | 265 | 53 | 0.037814 | 0.048184 | 0.276187 | 0.007769 | 0.611711 |
| 5 | early | raw_iv | 173 | 35 | 0.036518 | 0.047954 | 0.237563 | 0.011551 | 0.689298 |
| 5 | later | raw_iv | 92 | 19 | 0.040253 | 0.048615 | 0.348818 | 0.000658 | 0.452183 |
| 21 | combined | har | 217 | 11 | 0.055621 | 0.074958 | 0.572027 | -0.009711 | 0.257435 |
| 21 | early | har | 141 | 7 | 0.064189 | 0.086888 | 0.646044 | -0.013238 | 0.354780 |
| 21 | later | har | 76 | 4 | 0.039724 | 0.045129 | 0.434706 | -0.003167 | -0.083800 |
| 21 | combined | har_iv | 217 | 11 | 0.054214 | 0.075699 | 0.557269 | -0.006013 | 0.296629 |
| 21 | early | har_iv | 141 | 7 | 0.068614 | 0.091110 | 0.768350 | -0.007651 | 0.310668 |
| 21 | later | har_iv | 76 | 4 | 0.027499 | 0.030995 | 0.165658 | -0.002974 | 0.431852 |
| 21 | combined | intraday_har | 217 | 11 | 0.053216 | 0.072747 | 0.655843 | -0.008667 | 0.253935 |
| 21 | early | intraday_har | 141 | 7 | 0.066562 | 0.086950 | 0.905354 | -0.010808 | 0.258911 |
| 21 | later | intraday_har | 76 | 4 | 0.028454 | 0.032927 | 0.192935 | -0.004695 | 0.323144 |
| 21 | combined | latent_kalman | 217 | 11 | 0.052283 | 0.067505 | 0.862577 | -0.050942 | 0.629288 |
| 21 | early | latent_kalman | 141 | 7 | 0.058229 | 0.075081 | 0.953400 | -0.057109 | 0.595972 |
| 21 | later | latent_kalman | 76 | 4 | 0.041251 | 0.050524 | 0.694075 | -0.039502 | 0.582256 |
| 21 | combined | offshore_gap | 217 | 11 | 0.045862 | 0.061943 | 0.484910 | -0.009246 | 0.373731 |
| 21 | early | offshore_gap | 141 | 7 | 0.055469 | 0.073302 | 0.659194 | -0.015985 | 0.217167 |
| 21 | later | offshore_gap | 76 | 4 | 0.028039 | 0.031416 | 0.161568 | 0.003255 | 0.547970 |
| 21 | combined | overnight_decomposition | 217 | 11 | 0.048242 | 0.064019 | 0.492411 | -0.006464 | 0.357951 |
| 21 | early | overnight_decomposition | 141 | 7 | 0.057357 | 0.075247 | 0.651008 | -0.011230 | 0.249604 |
| 21 | later | overnight_decomposition | 76 | 4 | 0.031330 | 0.034603 | 0.198170 | 0.002380 | 0.425755 |
| 21 | combined | raw_iv | 217 | 11 | 0.039406 | 0.049414 | 0.267623 | -0.004405 | 0.444422 |
| 21 | early | raw_iv | 141 | 7 | 0.043885 | 0.055899 | 0.309888 | -0.006590 | 0.408297 |
| 21 | later | raw_iv | 76 | 4 | 0.031097 | 0.034276 | 0.189211 | -0.000350 | 0.318961 |

| horizon | scope | target | model | baseline | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | max_gap | intraday_blocks | constant_iv | crps | 265 | 53 | 0.003269 | 0.004971 | 0.001702 | 0.000318 | 0.003086 | 0.000210 | 0.003193 |
| 5 | combined | max_gap | intraday_blocks | constant_iv | mae | 265 | 53 | 0.004224 | 0.005553 | 0.001329 | -0.000397 | 0.003056 | -0.000490 | 0.003149 |
| 5 | combined | overnight_sd | intraday_blocks | constant_iv | crps | 265 | 53 | 0.026808 | 0.041598 | 0.014790 | 0.004058 | 0.025523 | 0.003262 | 0.026318 |
| 5 | combined | overnight_sd | intraday_blocks | V13_iv_scaled | crps | 265 | 53 | 0.026808 | 0.026120 | -0.000688 | -0.002671 | 0.001294 | -0.002824 | 0.001448 |
| 5 | combined | overnight_sd | intraday_blocks | constant_iv | mae | 265 | 53 | 0.033892 | 0.046928 | 0.013036 | 0.000242 | 0.025831 | -0.000363 | 0.026436 |
| 5 | combined | overnight_sd | intraday_blocks | V13_iv_scaled | mae | 265 | 53 | 0.033892 | 0.033709 | -0.000182 | -0.002970 | 0.002605 | -0.002761 | 0.002396 |
| 5 | combined | range | intraday_blocks | V13_iv_scaled | crps | 265 | 53 | 0.006076 | 0.005961 | -0.000115 | -0.000442 | 0.000211 | -0.000440 | 0.000210 |
| 5 | combined | range | intraday_blocks | constant_iv | crps | 265 | 53 | 0.006076 | 0.005795 | -0.000281 | -0.001049 | 0.000488 | -0.001096 | 0.000535 |
| 5 | combined | range | intraday_blocks | constant_iv | mae | 265 | 53 | 0.008253 | 0.008197 | -0.000056 | -0.000859 | 0.000747 | -0.000851 | 0.000739 |
| 5 | combined | range | intraday_blocks | V13_iv_scaled | mae | 265 | 53 | 0.008253 | 0.008191 | -0.000063 | -0.000491 | 0.000365 | -0.000442 | 0.000317 |
| 5 | combined | regular_sd | intraday_blocks | constant_iv | crps | 265 | 53 | 0.022649 | 0.028098 | 0.005448 | -0.004223 | 0.015120 | -0.006627 | 0.017524 |
| 5 | combined | regular_sd | intraday_blocks | V13_iv_scaled | crps | 265 | 53 | 0.022649 | 0.022467 | -0.000182 | -0.001067 | 0.000702 | -0.001072 | 0.000707 |
| 5 | combined | regular_sd | intraday_blocks | constant_iv | mae | 265 | 53 | 0.032301 | 0.041762 | 0.009461 | -0.004760 | 0.023682 | -0.008390 | 0.027312 |
| 5 | combined | regular_sd | intraday_blocks | V13_iv_scaled | mae | 265 | 53 | 0.032301 | 0.031999 | -0.000303 | -0.001528 | 0.000923 | -0.001424 | 0.000819 |
| 21 | combined | max_gap | intraday_blocks | constant_iv | crps | 217 | 11 | 0.006988 | 0.011133 | 0.004145 | 0.000745 | 0.007544 | -0.000078 | 0.008367 |
| 21 | combined | max_gap | intraday_blocks | constant_iv | mae | 217 | 11 | 0.009272 | 0.011725 | 0.002453 | -0.002878 | 0.007783 | -0.004006 | 0.008911 |
| 21 | combined | overnight_sd | intraday_blocks | constant_iv | crps | 217 | 11 | 0.033192 | 0.057614 | 0.024421 | 0.011946 | 0.036896 | 0.008788 | 0.040055 |
| 21 | combined | overnight_sd | intraday_blocks | V13_iv_scaled | crps | 217 | 11 | 0.033192 | 0.035018 | 0.001826 | -0.001940 | 0.005592 | -0.002092 | 0.005744 |
| 21 | combined | overnight_sd | intraday_blocks | constant_iv | mae | 217 | 11 | 0.041080 | 0.060859 | 0.019779 | 0.002734 | 0.036824 | 0.000462 | 0.039096 |
| 21 | combined | overnight_sd | intraday_blocks | V13_iv_scaled | mae | 217 | 11 | 0.041080 | 0.042256 | 0.001176 | -0.003356 | 0.005708 | -0.003923 | 0.006275 |
| 21 | combined | range | intraday_blocks | V13_iv_scaled | crps | 217 | 11 | 0.017842 | 0.018162 | 0.000320 | -0.002432 | 0.003071 | -0.003068 | 0.003708 |
| 21 | combined | range | intraday_blocks | constant_iv | crps | 217 | 11 | 0.017842 | 0.017280 | -0.000562 | -0.003690 | 0.002565 | -0.003939 | 0.002814 |
| 21 | combined | range | intraday_blocks | V13_iv_scaled | mae | 217 | 11 | 0.024733 | 0.024620 | -0.000113 | -0.003598 | 0.003371 | -0.004176 | 0.003949 |
| 21 | combined | range | intraday_blocks | constant_iv | mae | 217 | 11 | 0.024733 | 0.023480 | -0.001253 | -0.004969 | 0.002463 | -0.005412 | 0.002906 |
| 21 | combined | regular_sd | intraday_blocks | constant_iv | crps | 217 | 11 | 0.025004 | 0.034646 | 0.009642 | -0.010333 | 0.029617 | -0.014515 | 0.033799 |
| 21 | combined | regular_sd | intraday_blocks | V13_iv_scaled | crps | 217 | 11 | 0.025004 | 0.024651 | -0.000353 | -0.005251 | 0.004546 | -0.005806 | 0.005100 |
| 21 | combined | regular_sd | intraday_blocks | constant_iv | mae | 217 | 11 | 0.035043 | 0.044022 | 0.008979 | -0.010916 | 0.028873 | -0.015024 | 0.032981 |
| 21 | combined | regular_sd | intraday_blocks | V13_iv_scaled | mae | 217 | 11 | 0.035043 | 0.034418 | -0.000625 | -0.006364 | 0.005114 | -0.007136 | 0.005886 |

[Complete session profiles](intraday-profile.csv) · [Rejected sessions](intraday-rejections.csv) · [Separate opening-gap forecasts](opening-gap-forecasts.csv) · [Separate horizon risk components](gap-channel-forecasts.csv).
