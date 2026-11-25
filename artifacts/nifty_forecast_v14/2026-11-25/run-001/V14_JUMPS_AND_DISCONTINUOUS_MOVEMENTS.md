# V14 Jumps And Discontinuous Movements

Regular-session realized variance and finite-sample-corrected bipower variation use complete grids. Their positive difference is a jump-sensitive proxy. Sampling, jumps, volatility bursts and market microstructure can all affect it. The overnight move is measured separately from the regular-session log change. The jump probability uses a lagged training 90th-percentile proxy flag, a shrunken estimate of frequency and magnitude, and current known proxy history. Scheduled jumps are excluded from continuous within-step bridge correction. Jump simulations deduct expected jump variance from their continuous variance budget. Width-only, five-minute, one-minute, shifted-input, and deleted-largest-training-episode comparisons are scored on common dates. Extremes are sparse at the independent episode level, so the experiment uses shrunken empirical sizes and Student innovations.

| interval | sessions | median_excess_share | mean_overnight_log | median_intraday_variance |
| --- | --- | --- | --- | --- |
| 1 | 456 | 0.083268 | 0.000230 | 0.000029 |
| 5 | 459 | 0.109619 | 0.000248 | 0.000029 |

| horizon | target | cohort | model | n | disjoint | crps | mae | pinball | coverage80 | width80 | interval_score80 | coverage95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | range | combined | constant_iv | 265 | 53 | 0.005795 | 0.008197 | 0.002010 | 0.716981 | 0.021797 | 0.038142 | 0.901887 |
| 5 | range | combined | gjr_student | 265 | 53 | 0.006432 | 0.008569 | 0.002291 | 0.773585 | 0.021903 | 0.043306 | 0.932075 |
| 5 | range | combined | historical_innov | 265 | 53 | 0.006526 | 0.008585 | 0.002309 | 0.739623 | 0.021105 | 0.043896 | 0.928302 |
| 5 | range | combined | separate_gap | 265 | 53 | 0.006101 | 0.008097 | 0.002117 | 0.792453 | 0.021511 | 0.039681 | 0.932075 |
| 5 | range | combined | jump_diffusion | 265 | 53 | 0.006119 | 0.008116 | 0.002123 | 0.796226 | 0.021582 | 0.039746 | 0.932075 |
| 5 | range | combined | jump_1m | 265 | 53 | 0.006119 | 0.008117 | 0.002124 | 0.796226 | 0.021588 | 0.039780 | 0.932075 |
| 5 | range | combined | jump_shift | 265 | 53 | 0.006119 | 0.008117 | 0.002123 | 0.796226 | 0.021578 | 0.039764 | 0.932075 |
| 5 | range | combined | jump_no_episode | 265 | 53 | 0.006119 | 0.008115 | 0.002124 | 0.796226 | 0.021584 | 0.039788 | 0.932075 |
| 5 | range | combined | widened_gauss | 265 | 53 | 0.006555 | 0.009842 | 0.002251 | 0.652830 | 0.025727 | 0.042697 | 0.852830 |
| 21 | range | combined | constant_iv | 217 | 11 | 0.017280 | 0.023480 | 0.006346 | 0.566820 | 0.046187 | 0.123627 | 0.778802 |
| 21 | range | combined | gjr_student | 217 | 11 | 0.015422 | 0.019857 | 0.005389 | 0.764977 | 0.044758 | 0.100304 | 0.889401 |
| 21 | range | combined | historical_innov | 217 | 11 | 0.016051 | 0.020618 | 0.005570 | 0.682028 | 0.043285 | 0.106076 | 0.894009 |
| 21 | range | combined | separate_gap | 217 | 11 | 0.016460 | 0.021443 | 0.006067 | 0.672811 | 0.043642 | 0.115919 | 0.843318 |
| 21 | range | combined | jump_diffusion | 217 | 11 | 0.016476 | 0.021457 | 0.006067 | 0.682028 | 0.043587 | 0.116027 | 0.843318 |
| 21 | range | combined | jump_1m | 217 | 11 | 0.016475 | 0.021459 | 0.006067 | 0.677419 | 0.043555 | 0.116071 | 0.843318 |
| 21 | range | combined | jump_shift | 217 | 11 | 0.016477 | 0.021458 | 0.006067 | 0.682028 | 0.043572 | 0.116005 | 0.843318 |
| 21 | range | combined | jump_no_episode | 217 | 11 | 0.016477 | 0.021456 | 0.006069 | 0.682028 | 0.043570 | 0.116014 | 0.843318 |
| 21 | range | combined | widened_gauss | 217 | 11 | 0.018905 | 0.027735 | 0.006609 | 0.511521 | 0.054566 | 0.126343 | 0.723502 |

| horizon | removed | shock_session | removed_origins | model | n | disjoint | full_crps | ex_episode_crps | full_coverage80 | ex_episode_coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | largest_up_session | 2026-04-08 | 5 | jump_diffusion | 260 | 53 | 0.006119 | 0.005899 | 0.796226 | 0.803846 |
| 5 | largest_up_session | 2026-04-08 | 5 | jump_no_episode | 260 | 53 | 0.006119 | 0.005899 | 0.796226 | 0.803846 |
| 5 | largest_up_session | 2026-04-08 | 5 | widened_gauss | 260 | 53 | 0.006555 | 0.006458 | 0.652830 | 0.650000 |
| 5 | largest_down_session | 2026-03-19 | 5 | jump_diffusion | 260 | 53 | 0.006119 | 0.006069 | 0.796226 | 0.792308 |
| 5 | largest_down_session | 2026-03-19 | 5 | jump_no_episode | 260 | 53 | 0.006119 | 0.006069 | 0.796226 | 0.792308 |
| 5 | largest_down_session | 2026-03-19 | 5 | widened_gauss | 260 | 53 | 0.006555 | 0.006558 | 0.652830 | 0.646154 |
| 5 | largest_gap_session | 2026-02-03 | 5 | jump_diffusion | 260 | 53 | 0.006119 | 0.005695 | 0.796226 | 0.807692 |
| 5 | largest_gap_session | 2026-02-03 | 5 | jump_no_episode | 260 | 53 | 0.006119 | 0.005695 | 0.796226 | 0.807692 |
| 5 | largest_gap_session | 2026-02-03 | 5 | widened_gauss | 260 | 53 | 0.006555 | 0.006348 | 0.652830 | 0.661538 |
| 21 | largest_up_session | 2026-04-08 | 21 | jump_diffusion | 196 | 11 | 0.016476 | 0.016703 | 0.682028 | 0.658163 |
| 21 | largest_up_session | 2026-04-08 | 21 | jump_no_episode | 196 | 11 | 0.016477 | 0.016705 | 0.682028 | 0.658163 |
| 21 | largest_up_session | 2026-04-08 | 21 | widened_gauss | 196 | 11 | 0.018905 | 0.018588 | 0.511521 | 0.479592 |
| 21 | largest_down_session | 2026-03-19 | 21 | jump_diffusion | 196 | 10 | 0.016476 | 0.013895 | 0.682028 | 0.704082 |
| 21 | largest_down_session | 2026-03-19 | 21 | jump_no_episode | 196 | 10 | 0.016477 | 0.013895 | 0.682028 | 0.704082 |
| 21 | largest_down_session | 2026-03-19 | 21 | widened_gauss | 196 | 10 | 0.018905 | 0.017676 | 0.511521 | 0.515306 |
| 21 | largest_gap_session | 2026-02-03 | 21 | jump_diffusion | 196 | 11 | 0.016476 | 0.016504 | 0.682028 | 0.714286 |
| 21 | largest_gap_session | 2026-02-03 | 21 | jump_no_episode | 196 | 11 | 0.016477 | 0.016505 | 0.682028 | 0.714286 |
| 21 | largest_gap_session | 2026-02-03 | 21 | widened_gauss | 196 | 11 | 0.018905 | 0.019496 | 0.511521 | 0.494898 |

[Full intraday jump diagnostics](intraday-profile.csv) · [Drop-episode checks](jump-episode-deletion.csv) · [Joint path calibration and parameters](joint-path-ledger.json) · [Bipower variation method](https://doi.org/10.1093/jjfinec/nbh001).
