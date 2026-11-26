# V22 Internationally informed NIFTY forecasts

Weekly return is close to close over five eligible NSE cash sessions in the original research calendar, from the prior NIFTY
cash close. The monthly definition uses 21 sessions and the same prior-close convention. The five-session population has
173 early and 92 late origins. The 21-session population has 141 early and 76 late origins.

Every coherent candidate probability, arithmetic expected return, median, quantile, interval and terminal tail probability
comes from the same normalized atom weights. Location shifts use log-price units and carry the full empirical distribution.
Dispersion and signed asymmetry are separate interventions. Sign recalibration changes positive and negative mass while
retaining within-sign shapes. A historic distribution and the alternative law enter through true mixtures. The foreign
tail mixture uses twelve percent tail-only analogue mass translated to the archived parent log location.

Native weekly gains are small and mostly coincide with corporate, domestic or already visible offshore information. The
selected weekly directional overlay beats the original V20 Brier score in this retrospective sample, and the winner for
CRPS is a domestic residual fit. The monthly distribution has a small gain when sharing tail mass with a foreign law. Both
gains have intervals that span zero. The native and pre-auction comparisons have separately preserved benchmark instances.

## Best native candidates across Brier and CRPS

| horizon | model | n | active | brier | crps | log loss | accuracy | balanced accuracy | mae | rmse | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | secondary_location_beyond_gift | 265 | 216 | 0.220133 | 0.010180 | 0.630806 | 0.652830 | 0.656965 | 0.014217 | 0.020337 | 0.826415 | 0.045773 |
| 5 | secondary_location_domestic_only | 265 | 216 | 0.220368 | 0.010130 | 0.631135 | 0.641509 | 0.644144 | 0.014221 | 0.020263 | 0.830189 | 0.045758 |
| 5 | parent_location_offshore_only | 265 | 216 | 0.220463 | 0.010128 | 0.632621 | 0.660377 | 0.654770 | 0.014385 | 0.020129 | 0.818868 | 0.045776 |
| 5 | secondary_location_offshore_only | 265 | 216 | 0.220630 | 0.010257 | 0.632556 | 0.649057 | 0.644635 | 0.014420 | 0.020794 | 0.822642 | 0.045662 |
| 5 | parent_scale_only | 265 | 216 | 0.221168 | 0.010208 | 0.633526 | 0.664151 | 0.662624 | 0.014482 | 0.020166 | 0.815094 | 0.044235 |
| 5 | secondary_location_combined | 265 | 216 | 0.221234 | 0.010266 | 0.633184 | 0.645283 | 0.648418 | 0.014334 | 0.020562 | 0.818868 | 0.045773 |
| 5 | parent_location_domestic_only | 265 | 216 | 0.222142 | 0.010121 | 0.635180 | 0.645283 | 0.645732 | 0.014352 | 0.019939 | 0.822642 | 0.045852 |
| 5 | anchor_asymmetry | 265 | 265 | 0.222129 | 0.010167 | 0.635730 | 0.656604 | 0.654972 | 0.014480 | 0.020157 | 0.822642 | 0.045819 |
| 21 | parent_mixture_foreign_tail | 217 | 217 | 0.223431 | 0.023174 | 0.642855 | 0.580645 | 0.620060 | 0.029781 | 0.043039 | 0.755760 | 0.094566 |
| 21 | anchor_aggregate_position | 217 | 217 | 0.223819 | 0.023184 | 0.646636 | 0.576037 | 0.615962 | 0.029737 | 0.043023 | 0.714286 | 0.071940 |
| 21 | secondary_asymmetry_only | 217 | 152 | 0.224894 | 0.023982 | 0.640169 | 0.576037 | 0.611303 | 0.031246 | 0.044028 | 0.672811 | 0.071870 |
| 21 | parent_asymmetry_only | 217 | 152 | 0.227765 | 0.023262 | 0.654508 | 0.562212 | 0.605997 | 0.029737 | 0.043022 | 0.709677 | 0.071879 |
| 21 | eight_calendar_day_embargo | 217 | 217 | 0.228088 | 0.024003 | 0.646729 | 0.534562 | 0.563934 | 0.031264 | 0.044004 | 0.682028 | 0.071928 |
| 21 | v19_position_native | 217 | 217 | 0.228199 | 0.024010 | 0.647076 | 0.543779 | 0.568637 | 0.031248 | 0.044030 | 0.672811 | 0.071921 |
| 21 | parent_scale_only | 217 | 152 | 0.229818 | 0.023395 | 0.668247 | 0.576037 | 0.615962 | 0.029722 | 0.043000 | 0.718894 | 0.073327 |
| 21 | parent_historical_shrinkage | 217 | 217 | 0.231242 | 0.023604 | 0.655060 | 0.562212 | 0.603667 | 0.030739 | 0.044022 | 0.728111 | 0.078110 |
| 21 | parent_sign_only | 217 | 152 | 0.235956 | 0.023605 | 0.711767 | 0.589862 | 0.621268 | 0.029874 | 0.043675 | 0.695853 | 0.069170 |

## Incremental skill against the protected V21 distribution parent

Gain is parent loss minus candidate loss. An active estimate replays the parent on the same subset. Early and later rows retain their original benchmark populations.

| horizon | model | scope | n | brier | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | parent_asymmetry_only | active_matched | 216 | -0.002777 | -0.000057 |
| 5 | parent_asymmetry_only | combined | 265 | -0.002263 | -0.000047 |
| 5 | parent_asymmetry_only | early | 173 | -0.000901 | -0.000045 |
| 5 | parent_asymmetry_only | later | 92 | -0.004825 | -0.000051 |
| 5 | parent_historical_shrinkage | active_matched | 265 | -0.003806 | -0.000067 |
| 5 | parent_historical_shrinkage | combined | 265 | -0.003806 | -0.000067 |
| 5 | parent_historical_shrinkage | early | 173 | 0.000430 | 0.000103 |
| 5 | parent_historical_shrinkage | later | 92 | -0.011772 | -0.000385 |
| 5 | parent_location_domestic_only | active_matched | 216 | -0.000016 | 0.000057 |
| 5 | parent_location_domestic_only | combined | 265 | -0.000013 | 0.000046 |
| 5 | parent_location_domestic_only | early | 173 | -0.004109 | -0.000026 |
| 5 | parent_location_domestic_only | later | 92 | 0.007690 | 0.000182 |
| 5 | parent_location_international_only | active_matched | 216 | -0.004367 | -0.000364 |
| 5 | parent_location_international_only | combined | 265 | -0.003560 | -0.000296 |
| 5 | parent_location_international_only | early | 173 | -0.007287 | -0.000401 |
| 5 | parent_location_international_only | later | 92 | 0.003448 | -0.000099 |
| 5 | parent_location_offshore_only | active_matched | 216 | 0.002044 | 0.000048 |
| 5 | parent_location_offshore_only | combined | 265 | 0.001666 | 0.000039 |
| 5 | parent_location_offshore_only | early | 173 | 0.001912 | 0.000056 |
| 5 | parent_location_offshore_only | later | 92 | 0.001204 | 0.000008 |
| 5 | parent_scale_only | active_matched | 216 | 0.001180 | -0.000050 |
| 5 | parent_scale_only | combined | 265 | 0.000962 | -0.000041 |
| 5 | parent_scale_only | early | 173 | 0.000378 | -0.000045 |
| 5 | parent_scale_only | later | 92 | 0.002059 | -0.000034 |
| 5 | parent_sign_only | active_matched | 216 | -0.004135 | -0.000192 |
| 5 | parent_sign_only | combined | 265 | -0.003371 | -0.000156 |
| 5 | parent_sign_only | early | 173 | -0.011042 | -0.000284 |
| 5 | parent_sign_only | later | 92 | 0.011055 | 0.000084 |
| 5 | secondary_location_beyond_gift | active_matched | 216 | 0.001656 | -0.000042 |
| 5 | secondary_location_beyond_gift | combined | 265 | 0.001996 | -0.000013 |
| 5 | secondary_location_beyond_gift | early | 173 | 0.001052 | 0.000104 |
| 5 | secondary_location_beyond_gift | later | 92 | 0.003771 | -0.000234 |
| 21 | parent_asymmetry_only | active_matched | 152 | -0.005634 | -0.000111 |
| 21 | parent_asymmetry_only | combined | 217 | -0.003947 | -0.000078 |
| 21 | parent_asymmetry_only | early | 141 | -0.003219 | 0.000039 |
| 21 | parent_asymmetry_only | later | 76 | -0.005296 | -0.000295 |
| 21 | parent_historical_shrinkage | active_matched | 217 | -0.007423 | -0.000420 |
| 21 | parent_historical_shrinkage | combined | 217 | -0.007423 | -0.000420 |
| 21 | parent_historical_shrinkage | early | 141 | -0.022095 | -0.000955 |
| 21 | parent_historical_shrinkage | later | 76 | 0.019797 | 0.000572 |
| 21 | parent_location_beyond_gift | active_matched | 152 | -0.014837 | -0.002229 |
| 21 | parent_location_beyond_gift | combined | 217 | -0.010393 | -0.001561 |
| 21 | parent_location_beyond_gift | early | 141 | -0.021660 | -0.002445 |
| 21 | parent_location_beyond_gift | later | 76 | 0.010510 | 0.000078 |
| 21 | parent_location_international_only | active_matched | 152 | -0.022851 | -0.002536 |
| 21 | parent_location_international_only | combined | 217 | -0.016006 | -0.001777 |
| 21 | parent_location_international_only | early | 141 | -0.030451 | -0.002934 |
| 21 | parent_location_international_only | later | 76 | 0.010792 | 0.000371 |
| 21 | parent_mixture_foreign_tail | active_matched | 217 | 0.000388 | 0.000010 |
| 21 | parent_mixture_foreign_tail | combined | 217 | 0.000388 | 0.000010 |
| 21 | parent_mixture_foreign_tail | early | 141 | -0.004361 | -0.000181 |
| 21 | parent_mixture_foreign_tail | later | 76 | 0.009197 | 0.000365 |
| 21 | parent_scale_only | active_matched | 152 | -0.008565 | -0.000301 |
| 21 | parent_scale_only | combined | 217 | -0.006000 | -0.000211 |
| 21 | parent_scale_only | early | 141 | -0.002972 | -0.000013 |
| 21 | parent_scale_only | later | 76 | -0.011617 | -0.000578 |
| 21 | parent_sign_only | active_matched | 152 | -0.017327 | -0.000602 |
| 21 | parent_sign_only | combined | 217 | -0.012137 | -0.000421 |
| 21 | parent_sign_only | early | 141 | -0.003211 | -0.000153 |
| 21 | parent_sign_only | later | 76 | -0.028697 | -0.000920 |

[india-return-leaderboard.csv](india-return-leaderboard.csv) · [india-matched-comparisons.csv.gz](india-matched-comparisons.csv.gz) · [india-forecast-cases.csv.gz](india-forecast-cases.csv.gz) · [india-forecast-laws.npz](india-forecast-laws.npz) · [india-probability-calibration.csv](india-probability-calibration.csv) · [india-search-adjusted-intervals.csv.gz](india-search-adjusted-intervals.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
