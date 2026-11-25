# V16 Complete model comparison

Targets have their own loss units, support and historical comparisons. Leaders below use the corresponding coverage and objective. Current-session return after an observed opening prefix remains in its own experiment. Some earlier endpoint systems cover a subset of original windows. The full tables retain their usable dates, earlier/later and combined cohorts, calibration, matched alternatives, block uncertainty, dependence checks and failure controls.

## Opening gap direction

| target | model | n | disjoint | brier | crps | mae | rmse | log loss | balanced accuracy | covered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gap | gift_roll_screened | 180 | 180 | 0.095052 | 0.001203 | 0.001667 | 0.002194 | 0.309946 | 0.889081 | 0.800000 |
| gap | gift_disagreement | 248 | 248 | 0.099592 | 0.001456 | 0.001955 | 0.002778 | 0.346683 | 0.883065 | 0.774194 |
| gap | gift_raw | 248 | 248 | 0.100841 | 0.001459 | 0.001965 | 0.002777 | 0.348603 | 0.887097 | 0.766129 |
| gap | gift_calibrated | 248 | 248 | 0.100937 | 0.001451 | 0.001959 | 0.002763 | 0.349021 | 0.870968 | 0.778226 |
| gap | gift_delay10 | 248 | 248 | 0.101678 | 0.001443 | 0.001957 | 0.002728 | 0.349605 | 0.875000 | 0.770161 |

## Opening-gap distribution and magnitude

| target | model | n | disjoint | brier | crps | mae | rmse | log loss | balanced accuracy | covered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gap | gift_roll_screened | 180 | 180 | 0.095052 | 0.001203 | 0.001667 | 0.002194 | 0.309946 | 0.889081 | 0.800000 |
| gap | gift_delay10 | 248 | 248 | 0.101678 | 0.001443 | 0.001957 | 0.002728 | 0.349605 | 0.875000 | 0.770161 |
| gap | gift_calibrated | 248 | 248 | 0.100937 | 0.001451 | 0.001959 | 0.002763 | 0.349021 | 0.870968 | 0.778226 |
| gap | gift_disagreement | 248 | 248 | 0.099592 | 0.001456 | 0.001955 | 0.002778 | 0.346683 | 0.883065 | 0.774194 |
| gap | gift_raw | 248 | 248 | 0.100841 | 0.001459 | 0.001965 | 0.002777 | 0.348603 | 0.887097 | 0.766129 |

## Next opening gap

| target | model | n | disjoint | brier | crps | mae | rmse | log loss | balanced accuracy | covered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| next_gap | historical | 257 | 129 | 0.253179 | 0.003202 | 0.004086 | 0.006725 | 0.699591 | 0.484040 | 0.723735 |
| next_gap | eq_smooth | 257 | 129 | 0.261507 | 0.003195 | 0.004065 | 0.006825 | 0.728298 | 0.527983 | 0.727626 |
| next_gap | eq_lag1 | 257 | 129 | 0.265082 | 0.003227 | 0.004120 | 0.006840 | 0.733773 | 0.493186 | 0.731518 |
| next_gap | gift_conditional | 247 | 125 | 0.265189 | 0.003260 | 0.004132 | 0.006928 | 0.730156 | 0.530094 | 0.740891 |
| next_gap | asia_fresh | 257 | 129 | 0.265940 | 0.003221 | 0.004088 | 0.006853 | 0.736425 | 0.524046 | 0.735409 |

## Regular-session return

| target | model | n | disjoint | brier | crps | mae | rmse | log loss | balanced accuracy | covered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| regular | gift_conditional | 248 | 248 | 0.246197 | 0.003651 | 0.004966 | 0.006572 | 0.686088 | 0.567330 | 0.754032 |
| regular | eq_lag1 | 258 | 258 | 0.247930 | 0.003680 | 0.005034 | 0.006635 | 0.689487 | 0.535714 | 0.748062 |
| regular | historical | 258 | 258 | 0.251404 | 0.003684 | 0.005049 | 0.006624 | 0.695971 | 0.493867 | 0.748062 |
| regular | asia_stale | 258 | 258 | 0.249375 | 0.003686 | 0.005024 | 0.006644 | 0.693084 | 0.532107 | 0.751938 |
| regular | eq_lag17 | 258 | 258 | 0.249230 | 0.003690 | 0.005032 | 0.006653 | 0.692938 | 0.543651 | 0.740310 |

## Single-session endpoint

| target | model | n | disjoint | brier | crps | mae | rmse | log loss | balanced accuracy | covered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| one | gift_conditional | 248 | 248 | 0.207457 | 0.004226 | 0.005776 | 0.007606 | 0.603684 | 0.733984 | 0.770161 |
| one | rich_fresh | 258 | 258 | 0.221361 | 0.004398 | 0.006015 | 0.007921 | 0.630766 | 0.635577 | 0.786822 |
| one | network_stack | 258 | 258 | 0.229712 | 0.004511 | 0.006222 | 0.008140 | 0.648810 | 0.604507 | 0.751938 |
| one | disagreement | 258 | 258 | 0.247558 | 0.004833 | 0.006601 | 0.008707 | 0.688571 | 0.554087 | 0.732558 |
| one | eq_fresh | 258 | 258 | 0.248569 | 0.004892 | 0.006634 | 0.008827 | 0.690323 | 0.550060 | 0.720930 |

## Gap continuation and reversal

| cutoff | target | model | n | brier | log loss | actual |
| --- | --- | --- | --- | --- | --- | --- |
| 09:25 | close_beyond_previous_close_in_gap_direction | gap_sign_size | 257 | 0.196061 | 0.583248 | 0.731518 |
| 09:25 | close_beyond_previous_close_in_gap_direction | cash_prefix_only | 257 | 0.197084 | 0.582756 | 0.731518 |
| 09:25 | next_regular_day_same_direction | cash_prefix_only | 256 | 0.246950 | 0.686987 | 0.519531 |
| 09:25 | next_regular_day_same_direction | sector_offshore_full | 256 | 0.247092 | 0.687261 | 0.519531 |
| 09:25 | open_to_close_continuation | history | 257 | 0.249887 | 0.692944 | 0.536965 |
| 09:25 | open_to_close_continuation | cash_prefix_only | 257 | 0.253386 | 0.699982 | 0.536965 |
| 09:25 | remaining_same_gap_direction | history | 257 | 0.249997 | 0.693227 | 0.544747 |
| 09:25 | remaining_same_gap_direction | cash_prefix_only | 257 | 0.252737 | 0.698922 | 0.544747 |
| 10:20 | close_beyond_previous_close_in_gap_direction | gap_sign_size | 257 | 0.196061 | 0.583248 | 0.731518 |
| 10:20 | close_beyond_previous_close_in_gap_direction | history | 257 | 0.197100 | 0.583528 | 0.731518 |
| 10:20 | next_regular_day_same_direction | cash_prefix_only | 256 | 0.247348 | 0.687788 | 0.519531 |
| 10:20 | next_regular_day_same_direction | sector_offshore_full | 256 | 0.247442 | 0.688029 | 0.519531 |
| 10:20 | open_to_close_continuation | history | 257 | 0.249887 | 0.692944 | 0.536965 |
| 10:20 | open_to_close_continuation | cash_prefix_only | 257 | 0.253206 | 0.699609 | 0.536965 |
| 10:20 | remaining_same_gap_direction | history | 257 | 0.249667 | 0.692494 | 0.540856 |
| 10:20 | remaining_same_gap_direction | gap_sign_size | 257 | 0.254515 | 0.702593 | 0.540856 |

## Gap-fill survivors

| cutoff | threshold | model | n | brier | integrated brier | conditional abs minutes |
| --- | --- | --- | --- | --- | --- | --- |
| 09:25 | 0.500000 | survivor_history | 136 | 0.258645 | 0.236353 | 92.224920 |
| 09:25 | 0.500000 | calibrated_survival | 136 | 0.258177 | 0.236558 | 93.412006 |
| 09:25 | 1.000000 | gap_matched_survival | 177 | 0.214533 | 0.168113 | 78.543368 |
| 09:25 | 1.000000 | calibrated_survival | 177 | 0.217341 | 0.169709 | 78.543368 |
| 10:20 | 0.500000 | gap_matched_survival | 86 | 0.198614 | 0.108199 | 69.705976 |
| 10:20 | 0.500000 | survivor_history | 86 | 0.203875 | 0.109240 | 69.853597 |
| 10:20 | 1.000000 | gap_matched_survival | 152 | 0.167881 | 0.111552 | 65.900001 |
| 10:20 | 1.000000 | survivor_history | 152 | 0.171677 | 0.114831 | 67.262810 |

## Original five- and 21-session direction

| horizon | model | n | brier | log loss | accuracy | balanced accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.228529 | 0.648943 | 0.626415 | 0.636001 |
| 5 | V13_IV_all_phase | 265 | 0.229587 | 0.651757 | 0.626415 | 0.636001 |
| 5 | V12_NATIVE_RV | 265 | 0.229715 | 0.655524 | 0.626415 | 0.633316 |
| 5 | J11_BREADTH_ALL | 265 | 0.236138 | 0.667636 | 0.637736 | 0.650612 |
| 5 | V13_weekly_CRPS | 265 | 0.236495 | 0.665957 | 0.630189 | 0.644751 |
| 21 | V14_domestic_GJR | 217 | 0.245042 | 0.683095 | 0.511521 | 0.502675 |
| 21 | V15_iv_restart | 217 | 0.247721 | 0.688575 | 0.534562 | 0.537144 |
| 21 | prev_mean_reversion | 217 | 0.248912 | 0.690913 | 0.488479 | 0.496160 |
| 21 | V14_trend_shrink | 217 | 0.249894 | 0.692947 | 0.511521 | 0.475884 |
| 21 | V13_NEUTRAL | 217 | 0.250000 | 0.693147 | 0.511521 | 0.460742 |

## Weekly and monthly endpoint distributions

| horizon | model | n | endpoint crps | endpoint mae | endpoint coverage80 | endpoint width80 |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V14_sign_shrinkage | 265 | 0.010457 | 0.014842 | 0.826415 | 0.045780 |
| 5 | session_state | 265 | 0.010466 | 0.014084 | 0.777358 | 0.041712 |
| 5 | V13_weekly_CRPS | 265 | 0.010472 | 0.014903 | 0.788679 | 0.043399 |
| 5 | decomposed_gift | 265 | 0.010493 | 0.014275 | 0.750943 | 0.041429 |
| 5 | fixed_mixture | 265 | 0.010570 | 0.014535 | 0.777358 | 0.043204 |
| 21 | V15_gjr_restart | 217 | 0.024694 | 0.033162 | 0.705069 | 0.083033 |
| 21 | V14_gjr_student | 217 | 0.024788 | 0.033343 | 0.718894 | 0.083186 |
| 21 | V14_domestic_GJR | 217 | 0.024989 | 0.033042 | 0.668203 | 0.071794 |
| 21 | V15_iv_restart | 217 | 0.025027 | 0.033014 | 0.751152 | 0.097887 |
| 21 | V14_gjr_iv | 217 | 0.025060 | 0.033295 | 0.737327 | 0.090005 |

## Volatility expansion

| horizon | model | n | brier | log loss | mae | qlike | expansion rate | forecast rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | fixed_iv_rv | 265 | 0.152707 | 0.461636 | 0.038484 | 0.286114 | 0.328302 | 0.327067 |
| 5 | gift_risk | 265 | 0.154689 | 0.465130 | 0.036867 | 0.295909 | 0.328302 | 0.329895 |
| 5 | global_disagreement | 265 | 0.155643 | 0.467080 | 0.036828 | 0.293215 | 0.328302 | 0.330628 |
| 5 | raw_iv | 265 | 0.155657 | 0.466192 | 0.037814 | 0.276187 | 0.328302 | 0.356195 |
| 21 | student_EGARCH | 217 | 0.172872 | 0.689982 | 0.035730 | 0.207684 | 0.373272 | 0.287098 |
| 21 | raw_iv | 217 | 0.186036 | 0.829771 | 0.039406 | 0.267623 | 0.373272 | 0.278692 |
| 21 | fixed_iv_rv | 217 | 0.194367 | 0.831798 | 0.040894 | 0.257953 | 0.373272 | 0.225716 |
| 21 | GJR | 217 | 0.198788 | 0.769605 | 0.033179 | 0.199677 | 0.373272 | 0.292719 |

## Range and joint path leaders

| horizon | model | n | range crps | range coverage80 | range width80 | energy |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | V15_iv_restart | 265 | 0.005795 | 0.743396 | 0.021616 | 0.670200 |
| 5 | V14_constant_iv | 265 | 0.005795 | 0.716981 | 0.021765 | 0.673829 |
| 5 | V14_trend_shrink | 265 | 0.005801 | 0.720755 | 0.021797 | 0.672452 |
| 5 | V14_gjr_iv | 265 | 0.005850 | 0.788679 | 0.021190 | 0.679282 |
| 5 | V14_trend_persistent | 265 | 0.005872 | 0.781132 | 0.021110 | 0.678365 |
| 21 | V14_gjr_student | 217 | 0.015422 | 0.764977 | 0.044677 | 0.770958 |
| 21 | V15_gjr_restart | 217 | 0.015488 | 0.737327 | 0.043381 | 0.766246 |
| 21 | V15_iv_restart | 217 | 0.016288 | 0.612903 | 0.044844 | 0.778134 |
| 21 | V14_gjr_iv | 217 | 0.016304 | 0.640553 | 0.042795 | 0.779156 |
| 21 | V14_trend_persistent | 217 | 0.016309 | 0.640553 | 0.042403 | 0.780724 |

## Barrier touch and cumulative time-to-event

| horizon | model | n | touch brier | integrated brier | drawdown crps | energy |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | decomposed_gift | 265 | 0.132201 | 0.100551 | 0.005887 | 0.672264 |
| 5 | session_state | 265 | 0.132616 | 0.100939 | 0.005851 | 0.663195 |
| 5 | fixed_mixture | 265 | 0.137431 | 0.109601 | 0.005958 | 0.677746 |
| 5 | V14_trend_shrink | 265 | 0.143371 | 0.119424 | 0.005913 | 0.672452 |
| 5 | V14_trend_persistent | 265 | 0.144178 | 0.119660 | 0.005959 | 0.678365 |
| 21 | session_state | 217 | 0.180163 | 0.149012 | 0.015738 | 0.845088 |
| 21 | V14_trend_persistent | 217 | 0.181085 | 0.157875 | 0.014864 | 0.780724 |
| 21 | V14_trend_shrink | 217 | 0.182220 | 0.158161 | 0.015529 | 0.798757 |
| 21 | V15_iv_restart | 217 | 0.183126 | 0.159269 | 0.014889 | 0.778134 |
| 21 | V14_gjr_iv | 217 | 0.183138 | 0.159133 | 0.014867 | 0.779156 |

[Full session targets and eligibility](session-leaderboard.csv) · [All matched decay gains](session-matched-evidence.csv) · [All original endpoint controls](original-endpoint-leaderboard.csv) · [Original direction adjusted gains](multiscale-matched.csv) · [First-touch conditional results](passage-age-matched.csv) · [Volatility matched scores](volatility-matched.csv) · [All path scores](joint-path-leaderboard.csv)
