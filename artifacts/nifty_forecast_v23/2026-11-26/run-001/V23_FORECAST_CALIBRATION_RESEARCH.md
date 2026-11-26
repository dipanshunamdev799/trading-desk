# V23 Forecast calibration research

Sign probabilities are binned in deciles. The tables report observed rate, log loss, Brier reliability, resolution and
uncertainty. A within-bin remainder captures finite binning effects. The reported diagnostic calibration intercept and slope
summarize the scored cohort. The recalibrated laws themselves estimate a regularized sign map using earlier mature errors
and blend it with the original probability. The PIT warp uses only earlier realized randomized ranks and a monotone
quantile map. Fixed neutral shrinkage and both exact parents provide comparators.

The support-level randomized PIT uses the interval between strict and inclusive CDF at outcomes. Proper 80% interval
scores penalize coverage failures, and lower- and upper-tail misses remain separate. Conditional bins use prior rolling
medians of known volatility, forecast disagreement, positioning, analogue counts, participation and related states.
Each cell shows its sample size. Sparse conditional rows have correspondingly limited precision.

| horizon | model | n | brier | reliability | resolution | uncertainty | within bin remainder | diagnostic calibration intercept | diagnostic calibration slope | log loss | coverage80 | width80 | interval80 | tail down | tail up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | agg_bayesian | 265 | 0.231920 | 0.011181 | 0.020231 | 0.246579 | -0.005608 | -0.343994 | 2.174837 | 0.656435 | 0.826415 | 0.047067 | 0.068300 | 0.109434 | 0.064151 |
| 5 | calibration_pit_fit | 265 | 0.222437 | 0.011340 | 0.034843 | 0.246579 | -0.000640 | -0.174618 | 0.931352 | 0.637155 | 0.803774 | 0.043545 | 0.066057 | 0.105660 | 0.090566 |
| 5 | calibration_sign_fit | 265 | 0.222078 | 0.010114 | 0.033051 | 0.246579 | -0.001563 | -0.256536 | 1.097201 | 0.635340 | 0.837736 | 0.045688 | 0.065168 | 0.094340 | 0.067925 |
| 5 | component_historical_shape_only | 265 | 0.226389 | 0.012685 | 0.032178 | 0.246579 | -0.000696 | -0.305939 | 0.774204 | 0.645268 | 0.811321 | 0.045797 | 0.064100 | 0.113208 | 0.075472 |
| 5 | fixed_20pct_neutral | 265 | 0.223891 | 0.010561 | 0.033100 | 0.246579 | -0.000149 | -0.313417 | 1.459517 | 0.639382 | 0.826415 | 0.045766 | 0.066414 | 0.109434 | 0.064151 |
| 5 | fixed_neutral_sign | 265 | 0.223891 | 0.010561 | 0.033100 | 0.246579 | -0.000149 | -0.313417 | 1.459517 | 0.639382 | 0.830189 | 0.046284 | 0.065464 | 0.105660 | 0.064151 |
| 5 | protected_direction | 265 | 0.220133 | 0.009089 | 0.034995 | 0.246579 | -0.000539 | -0.338578 | 1.246837 | 0.630806 | 0.826415 | 0.045773 | 0.067622 | 0.101887 | 0.071698 |
| 5 | protected_distribution | 265 | 0.222142 | 0.012173 | 0.037191 | 0.246579 | 0.000582 | -0.315790 | 1.143915 | 0.635180 | 0.822642 | 0.045852 | 0.065066 | 0.109434 | 0.067925 |
| 21 | agg_bayesian | 217 | 0.248975 | 0.031752 | 0.027210 | 0.246130 | -0.001697 | -0.719692 | 1.197056 | 0.693500 | 0.723502 | 0.084749 | 0.181025 | 0.221198 | 0.055300 |
| 21 | calibration_pit_fit | 217 | 0.225646 | 0.075540 | 0.094548 | 0.246130 | -0.001476 | -0.482172 | 0.898769 | 0.649219 | 0.705069 | 0.070247 | 0.175089 | 0.202765 | 0.092166 |
| 21 | calibration_sign_fit | 217 | 0.225069 | 0.053257 | 0.073898 | 0.246130 | -0.000420 | -0.578304 | 0.950402 | 0.652587 | 0.705069 | 0.071973 | 0.174167 | 0.230415 | 0.064516 |
| 21 | component_historical_shape_only | 217 | 0.210496 | 0.037280 | 0.071221 | 0.246130 | -0.001692 | -0.676717 | 1.389314 | 0.605351 | 0.705069 | 0.071099 | 0.171275 | 0.188940 | 0.105991 |
| 21 | fixed_20pct_neutral | 217 | 0.222577 | 0.031775 | 0.056264 | 0.246130 | 0.000937 | -0.756546 | 1.575967 | 0.638591 | 0.714286 | 0.074437 | 0.169317 | 0.216590 | 0.069124 |
| 21 | fixed_neutral_sign | 217 | 0.222577 | 0.032505 | 0.056789 | 0.246130 | 0.000731 | -0.756546 | 1.575967 | 0.638591 | 0.714286 | 0.073716 | 0.169187 | 0.221198 | 0.064516 |
| 21 | protected_direction | 217 | 0.223431 | 0.051758 | 0.076212 | 0.246130 | 0.001756 | -0.726718 | 1.330502 | 0.642855 | 0.755760 | 0.094566 | 0.174451 | 0.207373 | 0.036866 |
| 21 | protected_distribution | 217 | 0.223819 | 0.056835 | 0.077841 | 0.246130 | -0.001306 | -0.723136 | 1.134402 | 0.646636 | 0.714286 | 0.071940 | 0.172783 | 0.230415 | 0.055300 |

| horizon | model | condition | group | n | observed | probability | brier | coverage | width | tail down | tail up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | component_historical_shape_only | observed_trailing_vol | higher | 114 | 0.500000 | 0.507573 | 0.247397 | 0.754386 | 0.052877 | 0.114035 | 0.131579 |
| 5 | component_historical_shape_only | observed_trailing_vol | lower | 121 | 0.338843 | 0.449480 | 0.209515 | 0.842975 | 0.041338 | 0.132231 | 0.024793 |
| 5 | component_historical_shape_only | family_prob_spread | higher | 129 | 0.457364 | 0.443251 | 0.215077 | 0.744186 | 0.048794 | 0.139535 | 0.116279 |
| 5 | component_historical_shape_only | family_prob_spread | lower | 106 | 0.367925 | 0.519537 | 0.243488 | 0.867925 | 0.044674 | 0.103774 | 0.028302 |
| 5 | component_historical_shape_only | positioning_concentration | higher | 155 | 0.400000 | 0.449537 | 0.240899 | 0.780645 | 0.049124 | 0.135484 | 0.083871 |
| 5 | component_historical_shape_only | positioning_concentration | lower | 80 | 0.450000 | 0.532152 | 0.202691 | 0.837500 | 0.042695 | 0.100000 | 0.062500 |
| 5 | component_historical_shape_only | analogue_effective_n | higher | 96 | 0.458333 | 0.456001 | 0.211803 | 0.770833 | 0.047558 | 0.114583 | 0.114583 |
| 5 | component_historical_shape_only | analogue_effective_n | lower | 139 | 0.388489 | 0.492620 | 0.239004 | 0.820144 | 0.046506 | 0.129496 | 0.050360 |
| 5 | component_historical_shape_only | original cohort | early | 173 | 0.450867 | 0.508777 | 0.255913 | 0.843931 | 0.048582 | 0.086705 | 0.069364 |
| 5 | component_historical_shape_only | original cohort | later | 92 | 0.423913 | 0.511719 | 0.170873 | 0.750000 | 0.040561 | 0.163043 | 0.086957 |
| 5 | protected_direction | observed_trailing_vol | higher | 114 | 0.500000 | 0.504826 | 0.235588 | 0.798246 | 0.052884 | 0.070175 | 0.131579 |
| 5 | protected_direction | observed_trailing_vol | lower | 121 | 0.338843 | 0.482642 | 0.208720 | 0.826446 | 0.041288 | 0.157025 | 0.016529 |
| 5 | protected_direction | family_prob_spread | higher | 129 | 0.457364 | 0.463485 | 0.210678 | 0.751938 | 0.048797 | 0.131783 | 0.116279 |
| 5 | protected_direction | family_prob_spread | lower | 106 | 0.367925 | 0.529815 | 0.235233 | 0.886792 | 0.044621 | 0.094340 | 0.018868 |
| 5 | protected_direction | positioning_concentration | higher | 155 | 0.400000 | 0.477930 | 0.233558 | 0.787097 | 0.049141 | 0.129032 | 0.083871 |
| 5 | protected_direction | positioning_concentration | lower | 80 | 0.450000 | 0.523384 | 0.198885 | 0.862500 | 0.042597 | 0.087500 | 0.050000 |
| 5 | protected_direction | analogue_effective_n | higher | 96 | 0.458333 | 0.468374 | 0.205661 | 0.791667 | 0.047525 | 0.114583 | 0.093750 |
| 5 | protected_direction | analogue_effective_n | lower | 139 | 0.388489 | 0.510691 | 0.232869 | 0.827338 | 0.046491 | 0.115108 | 0.057554 |
| 5 | protected_direction | original cohort | early | 173 | 0.450867 | 0.521216 | 0.240367 | 0.861272 | 0.048636 | 0.086705 | 0.052023 |
| 5 | protected_direction | original cohort | later | 92 | 0.423913 | 0.495611 | 0.182085 | 0.760870 | 0.040390 | 0.130435 | 0.108696 |
| 21 | component_historical_shape_only | observed_trailing_vol | higher | 81 | 0.432099 | 0.481612 | 0.185888 | 0.506173 | 0.077323 | 0.246914 | 0.246914 |
| 21 | component_historical_shape_only | observed_trailing_vol | lower | 106 | 0.500000 | 0.611427 | 0.218802 | 0.801887 | 0.066383 | 0.169811 | 0.028302 |
| 21 | component_historical_shape_only | family_prob_spread | higher | 103 | 0.320388 | 0.497670 | 0.216765 | 0.669903 | 0.071568 | 0.203883 | 0.126214 |
| 21 | component_historical_shape_only | family_prob_spread | lower | 84 | 0.654762 | 0.625736 | 0.189561 | 0.678571 | 0.070575 | 0.202381 | 0.119048 |
| 21 | component_historical_shape_only | positioning_concentration | higher | 126 | 0.547619 | 0.601312 | 0.211778 | 0.642857 | 0.072355 | 0.198413 | 0.158730 |
| 21 | component_historical_shape_only | positioning_concentration | lower | 61 | 0.311475 | 0.459944 | 0.189604 | 0.737705 | 0.068574 | 0.213115 | 0.049180 |
| 21 | component_historical_shape_only | analogue_effective_n | higher | 99 | 0.484848 | 0.565950 | 0.203250 | 0.666667 | 0.070932 | 0.202020 | 0.131313 |
| 21 | component_historical_shape_only | analogue_effective_n | lower | 88 | 0.454545 | 0.543100 | 0.206002 | 0.681818 | 0.071336 | 0.204545 | 0.113636 |
| 21 | component_historical_shape_only | original cohort | early | 141 | 0.453901 | 0.522586 | 0.189948 | 0.744681 | 0.073355 | 0.163121 | 0.092199 |
| 21 | component_historical_shape_only | original cohort | later | 76 | 0.407895 | 0.598399 | 0.248618 | 0.631579 | 0.066914 | 0.236842 | 0.131579 |
| 21 | protected_direction | observed_trailing_vol | higher | 81 | 0.432099 | 0.518152 | 0.192208 | 0.666667 | 0.108851 | 0.234568 | 0.098765 |
| 21 | protected_direction | observed_trailing_vol | lower | 106 | 0.500000 | 0.623518 | 0.237186 | 0.792453 | 0.088382 | 0.207547 | 0.000000 |
| 21 | protected_direction | family_prob_spread | higher | 103 | 0.320388 | 0.540347 | 0.240674 | 0.757282 | 0.097547 | 0.223301 | 0.019417 |
| 21 | protected_direction | family_prob_spread | lower | 84 | 0.654762 | 0.623899 | 0.189537 | 0.714286 | 0.096881 | 0.214286 | 0.071429 |
| 21 | protected_direction | positioning_concentration | higher | 126 | 0.547619 | 0.621786 | 0.226725 | 0.738095 | 0.099700 | 0.222222 | 0.039683 |
| 21 | protected_direction | positioning_concentration | lower | 61 | 0.311475 | 0.487182 | 0.199070 | 0.737705 | 0.092184 | 0.213115 | 0.049180 |
| 21 | protected_direction | analogue_effective_n | higher | 99 | 0.484848 | 0.581471 | 0.214194 | 0.686869 | 0.094727 | 0.242424 | 0.070707 |
| 21 | protected_direction | analogue_effective_n | lower | 88 | 0.454545 | 0.573837 | 0.221652 | 0.795455 | 0.100084 | 0.193182 | 0.011364 |
| 21 | protected_direction | original cohort | early | 141 | 0.453901 | 0.541835 | 0.199355 | 0.836879 | 0.099196 | 0.163121 | 0.000000 |
| 21 | protected_direction | original cohort | later | 76 | 0.407895 | 0.622051 | 0.268099 | 0.605263 | 0.085974 | 0.289474 | 0.105263 |

[calibration-reliability.png](calibration-reliability.png) · [probability-reliability-bins.csv.gz](probability-reliability-bins.csv.gz) · [randomized-pit-histogram.csv.gz](randomized-pit-histogram.csv.gz) · [conditional-calibration.csv.gz](conditional-calibration.csv.gz) · [forecast-calibration-leaderboard.csv](forecast-calibration-leaderboard.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
