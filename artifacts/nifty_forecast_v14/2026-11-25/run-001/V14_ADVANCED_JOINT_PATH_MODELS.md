# V14 Advanced Joint Path Models

The archive contains **6,360** model/date laws over **265** origins. Each law has **2,048** complete 21-session OHLC paths. On common origins the five-session forecast is the exact prefix with identical weights. Candidate mechanisms include raw and calibrated constant IV, Gaussian and heavy-tailed asymmetric GARCH, IV-GARCH, latent and regime variance, historical innovations, overnight gaps, jumps, empirical blocks and fixed complete-path mixtures. All target probabilities, drawdowns, ranges and realized returns come from the same paths. A shared mixture gives 30% each to constant IV and IV-GJR and 20% each to jump and IV-scaled blocks. Reweighting and width calibration retain coherent complete paths.

Energy and variogram loss act on endpoint return, range, high, low, realized volatility and drawdown. Coordinates use only scales fitted on matured training data. A fixed common 1,024-pair sample estimates the energy pair term. Per-origin seeds and encoded OHLC scenarios are available for exact verification.

| horizon | model | n | disjoint | energy_score | variogram_score |
| --- | --- | --- | --- | --- | --- |
| 5 | V13_diffusion_iv | 265 | 53 | 1.562100 | 0.148752 |
| 5 | trend_shrink | 265 | 53 | 1.562593 | 0.149603 |
| 5 | constant_iv | 265 | 53 | 1.567506 | 0.149968 |
| 5 | simple_drift | 265 | 53 | 1.571698 | 0.150017 |
| 5 | trend_persistent | 265 | 53 | 1.595744 | 0.155640 |
| 5 | path_mixture | 265 | 53 | 1.597853 | 0.155510 |
| 5 | gjr_iv | 265 | 53 | 1.598766 | 0.156669 |
| 5 | joint_tail_width | 265 | 53 | 1.599321 | 0.156406 |
| 5 | joint_pit | 265 | 53 | 1.601604 | 0.156683 |
| 5 | widened_gauss | 265 | 53 | 1.610581 | 0.157339 |
| 5 | latent_sv | 265 | 53 | 1.615709 | 0.160381 |
| 5 | separate_gap | 265 | 53 | 1.626226 | 0.163749 |
| 5 | jump_diffusion | 265 | 53 | 1.627791 | 0.164112 |
| 5 | jump_no_episode | 265 | 53 | 1.627808 | 0.164085 |
| 5 | jump_shift | 265 | 53 | 1.628042 | 0.164142 |
| 21 | gjr_student | 217 | 11 | 2.487703 | 0.281181 |
| 21 | gjr_skew | 217 | 11 | 2.488983 | 0.281942 |
| 21 | V13_diffusion_iv | 217 | 11 | 2.510707 | 0.285451 |
| 21 | trend_persistent | 217 | 11 | 2.529082 | 0.297548 |
| 21 | path_mixture | 217 | 11 | 2.531511 | 0.298393 |
| 21 | gjr_iv | 217 | 11 | 2.534279 | 0.299556 |
| 21 | joint_pit | 217 | 11 | 2.537546 | 0.300182 |
| 21 | joint_tail_width | 217 | 11 | 2.539067 | 0.300965 |
| 21 | trend_shrink | 217 | 11 | 2.542329 | 0.294840 |
| 21 | gjr_gauss | 217 | 11 | 2.543834 | 0.291849 |
| 21 | historical_innov | 217 | 11 | 2.549786 | 0.294525 |
| 21 | separate_gap | 217 | 11 | 2.552047 | 0.308549 |
| 21 | jump_no_episode | 217 | 11 | 2.553107 | 0.308880 |
| 21 | jump_1m | 217 | 11 | 2.553112 | 0.308910 |
| 21 | jump_shift | 217 | 11 | 2.553493 | 0.308910 |

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
| 5 | range | combined | V13_iv_scaled | 265 | 53 | 0.005961 | 0.008191 | 0.002043 | 0.766038 | 0.022660 | 0.039164 | 0.939623 |
| 5 | range | combined | joint_pit | 265 | 53 | 0.005969 | 0.008272 | 0.002081 | 0.773585 | 0.022727 | 0.039285 | 0.928302 |
| 5 | range | combined | intraday_blocks | 265 | 53 | 0.006076 | 0.008253 | 0.002084 | 0.758491 | 0.022133 | 0.039537 | 0.943396 |
| 5 | range | combined | trend_blocks | 265 | 53 | 0.006078 | 0.008276 | 0.002096 | 0.750943 | 0.022411 | 0.039723 | 0.939623 |
| 5 | range | combined | iv_scaled_blocks | 265 | 53 | 0.006098 | 0.008289 | 0.002089 | 0.754717 | 0.022369 | 0.039779 | 0.943396 |
| 5 | range | combined | separate_gap | 265 | 53 | 0.006101 | 0.008097 | 0.002117 | 0.792453 | 0.021511 | 0.039681 | 0.932075 |
| 21 | range | combined | gjr_student | 217 | 11 | 0.015422 | 0.019857 | 0.005389 | 0.764977 | 0.044758 | 0.100304 | 0.889401 |
| 21 | range | combined | gjr_skew | 217 | 11 | 0.015440 | 0.019897 | 0.005382 | 0.741935 | 0.044847 | 0.100705 | 0.889401 |
| 21 | range | combined | regime_state | 217 | 11 | 0.015942 | 0.021402 | 0.005499 | 0.755760 | 0.055702 | 0.106861 | 0.898618 |
| 21 | range | combined | historical_innov | 217 | 11 | 0.016051 | 0.020618 | 0.005570 | 0.682028 | 0.043285 | 0.106076 | 0.894009 |
| 21 | range | combined | gjr_gauss | 217 | 11 | 0.016079 | 0.020621 | 0.005598 | 0.663594 | 0.042861 | 0.106888 | 0.889401 |
| 21 | range | combined | V13_diffusion_iv | 217 | 11 | 0.016275 | 0.022336 | 0.005872 | 0.599078 | 0.045217 | 0.111077 | 0.824885 |
| 21 | range | combined | gjr_iv | 217 | 11 | 0.016304 | 0.021538 | 0.005994 | 0.640553 | 0.042866 | 0.114532 | 0.843318 |
| 21 | range | combined | trend_persistent | 217 | 11 | 0.016309 | 0.021433 | 0.006019 | 0.640553 | 0.042467 | 0.115056 | 0.834101 |
| 21 | range | combined | latent_sv | 217 | 11 | 0.016375 | 0.021030 | 0.005874 | 0.677419 | 0.043848 | 0.112200 | 0.870968 |
| 21 | range | combined | separate_gap | 217 | 11 | 0.016460 | 0.021443 | 0.006067 | 0.672811 | 0.043642 | 0.115919 | 0.843318 |
| 21 | range | combined | jump_1m | 217 | 11 | 0.016475 | 0.021459 | 0.006067 | 0.677419 | 0.043555 | 0.116071 | 0.843318 |
| 21 | range | combined | jump_diffusion | 217 | 11 | 0.016476 | 0.021457 | 0.006067 | 0.682028 | 0.043587 | 0.116027 | 0.843318 |
| 21 | range | combined | jump_no_episode | 217 | 11 | 0.016477 | 0.021456 | 0.006069 | 0.682028 | 0.043570 | 0.116014 | 0.843318 |
| 21 | range | combined | jump_shift | 217 | 11 | 0.016477 | 0.021458 | 0.006067 | 0.682028 | 0.043572 | 0.116005 | 0.843318 |
| 21 | range | combined | path_mixture | 217 | 11 | 0.016784 | 0.023071 | 0.005963 | 0.617512 | 0.051225 | 0.116043 | 0.852535 |

[Joint law catalog and SHA-256 digests](joint-path-ledger.json) · [Joint score ledger](multivariate-path-scores.csv) · [Independent forecast-law verification](verification.json).
