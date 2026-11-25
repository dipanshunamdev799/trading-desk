# V20 Correction Activation Research

Three decisions are visible for every native original cohort. The parent can be used alone, the feature correction can be applied whenever the minimum fit and data are present, or the correction can be fractionally weighted or gated. The weekly simple gate needs a causal announcement intensity percentile of **0.70**. The monthly gate uses concentration rank **at least 0.48**, IV rank **at most 0.82**, and excludes the three days near the front expiry and identified rollover dates. A single regularized activation model trains on earlier realized Brier gains, using announcement and concentration state, IV and trend, correction size, a standardized feature-distance measure, training support and training-window instability. Both gates fall back to the exact parent on excluded dates.

| horizon | model | n | active | inactive | disjoint | brier | crps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | corporate_v18_feature_set | 265 | 223 | 42 | 53 | 0.223838 | 0.010326 |
| 5 | exact_v14 | 265 | 265 | 0 | 53 | 0.228529 | 0.010457 |
| 5 | fixed_half_shift | 265 | 223 | 42 | 53 | 0.224020 | 0.010324 |
| 5 | learned_activation | 265 | 103 | 162 | 53 | 0.223870 | 0.010394 |
| 5 | learned_history_law_mixture | 265 | 178 | 87 | 53 | 0.226770 | 0.010449 |
| 5 | predeclared_activation | 265 | 78 | 187 | 53 | 0.232479 | 0.010616 |
| 5 | v18_corporate_native | 265 | 265 | 0 | 53 | 0.223481 | 0.010318 |
| 5 | v19_position_native | 265 | 223 | 42 | 53 | 0.234786 | 0.010547 |
| 21 | exact_v14 | 217 | 217 | 0 | 11 | 0.245042 | 0.024989 |
| 21 | fixed_half_shift | 217 | 159 | 58 | 11 | 0.230941 | 0.024371 |
| 21 | learned_activation | 217 | 92 | 125 | 11 | 0.241063 | 0.024632 |
| 21 | learned_history_law_mixture | 217 | 99 | 118 | 11 | 0.238075 | 0.024527 |
| 21 | positions_v19_feature_set | 217 | 159 | 58 | 11 | 0.228199 | 0.024010 |
| 21 | predeclared_activation | 217 | 86 | 131 | 11 | 0.246481 | 0.024847 |
| 21 | v18_corporate_native | 217 | 217 | 0 | 11 | 0.259808 | 0.025409 |
| 21 | v19_position_native | 217 | 159 | 58 | 11 | 0.228199 | 0.024010 |

| horizon | model | scope | metric | n | active | disjoint | parent loss | loss | gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | predeclared_activation | active_matched | brier | 78 | 78 | 21 | 0.241091 | 0.254512 | -0.013420 |
| 5 | predeclared_activation | earlier | brier | 173 | 45 | 35 | 0.242767 | 0.247739 | -0.004972 |
| 5 | predeclared_activation | later | brier | 92 | 33 | 19 | 0.201754 | 0.203783 | -0.002029 |
| 5 | predeclared_activation | active_matched | crps | 78 | 78 | 21 | 0.013391 | 0.013931 | -0.000540 |
| 5 | predeclared_activation | earlier | crps | 173 | 45 | 35 | 0.010340 | 0.010518 | -0.000177 |
| 5 | predeclared_activation | later | crps | 92 | 33 | 19 | 0.010676 | 0.010800 | -0.000125 |
| 5 | learned_activation | active_matched | brier | 103 | 103 | 24 | 0.225790 | 0.213804 | 0.011986 |
| 5 | learned_activation | earlier | brier | 173 | 55 | 35 | 0.242767 | 0.241482 | 0.001285 |
| 5 | learned_activation | later | brier | 92 | 48 | 19 | 0.201754 | 0.190752 | 0.011003 |
| 5 | learned_activation | active_matched | crps | 103 | 103 | 24 | 0.012521 | 0.012358 | 0.000163 |
| 5 | learned_activation | earlier | crps | 173 | 55 | 35 | 0.010340 | 0.010323 | 0.000017 |
| 5 | learned_activation | later | crps | 92 | 48 | 19 | 0.010676 | 0.010526 | 0.000150 |
| 21 | predeclared_activation | active_matched | brier | 86 | 86 | 6 | 0.235095 | 0.238725 | -0.003630 |
| 21 | predeclared_activation | earlier | brier | 141 | 40 | 7 | 0.244618 | 0.224897 | 0.019721 |
| 21 | predeclared_activation | later | brier | 76 | 46 | 4 | 0.245829 | 0.286524 | -0.040695 |
| 21 | predeclared_activation | active_matched | crps | 86 | 86 | 6 | 0.022972 | 0.022615 | 0.000357 |
| 21 | predeclared_activation | earlier | crps | 141 | 40 | 7 | 0.023451 | 0.022563 | 0.000888 |
| 21 | predeclared_activation | later | crps | 76 | 46 | 4 | 0.027843 | 0.029086 | -0.001243 |
| 21 | learned_activation | active_matched | brier | 92 | 92 | 5 | 0.244760 | 0.235374 | 0.009386 |
| 21 | learned_activation | earlier | brier | 141 | 23 | 7 | 0.244618 | 0.235009 | 0.009609 |
| 21 | learned_activation | later | brier | 76 | 69 | 4 | 0.245829 | 0.252295 | -0.006466 |
| 21 | learned_activation | active_matched | crps | 92 | 92 | 5 | 0.018992 | 0.018151 | 0.000841 |
| 21 | learned_activation | earlier | crps | 141 | 23 | 7 | 0.023451 | 0.022896 | 0.000555 |
| 21 | learned_activation | later | crps | 76 | 69 | 4 | 0.027843 | 0.027854 | -0.000011 |

The active subset can be much smaller and correlated. The full population includes the fallback cases. The proper paired gain and actual denominator should accompany any selected-date score.

[native-mechanism-cases.csv.gz](native-mechanism-cases.csv.gz) · [mechanism-regime-audit.csv](mechanism-regime-audit.csv) · [mechanism-regime-comparisons.csv](mechanism-regime-comparisons.csv) · [complete-matched-comparisons.csv](complete-matched-comparisons.csv) · [matched-block-intervals.csv.gz](matched-block-intervals.csv.gz)
