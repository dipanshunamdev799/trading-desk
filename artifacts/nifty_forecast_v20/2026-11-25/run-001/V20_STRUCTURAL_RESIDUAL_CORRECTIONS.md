# V20 Structural Residual Corrections

Correction models use only earlier archived out-of-sample forecast errors. Translation adds one bounded log-return shift. Scale and asymmetry transform centered log returns. Sign probability is represented by adjusting the weights on existing complete atoms. Fixed and learned weights mix complete corrected and parent laws. The mean, median, probability and tail quantiles are all read from the same law. Shape, bias-only, shrinkage and missing-input fallbacks each produce separately archived predictions.

| horizon | scope | model | n | active | disjoint | brier | crps | log loss | balanced accuracy | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | asymmetry_only | 265 | 223 | 53 | 0.228104 | 0.010399 | 0.648044 | 0.636001 | 0.826415 | 0.045761 |
| 5 | combined | bias_only | 265 | 223 | 53 | 0.226018 | 0.010396 | 0.644569 | 0.648013 | 0.818868 | 0.045703 |
| 5 | combined | corporate_v18_feature_set | 265 | 223 | 53 | 0.223838 | 0.010326 | 0.638662 | 0.640362 | 0.818868 | 0.045704 |
| 5 | combined | exact_v14 | 265 | 265 | 53 | 0.228529 | 0.010457 | 0.648943 | 0.636001 | 0.826415 | 0.045780 |
| 5 | combined | fixed_half_law_mixture | 265 | 223 | 53 | 0.224446 | 0.010322 | 0.640566 | 0.632912 | 0.818868 | 0.045902 |
| 5 | combined | fixed_half_shift | 265 | 223 | 53 | 0.224020 | 0.010324 | 0.639617 | 0.639669 | 0.818868 | 0.045742 |
| 5 | combined | learned_history_law_mixture | 265 | 178 | 53 | 0.226770 | 0.010449 | 0.645697 | 0.646830 | 0.826415 | 0.045855 |
| 5 | combined | location_scale_asymmetry | 265 | 223 | 53 | 0.221956 | 0.010420 | 0.633662 | 0.636983 | 0.815094 | 0.045789 |
| 5 | combined | probability_only | 265 | 223 | 53 | 0.225928 | 0.010457 | 0.643400 | 0.640362 | 0.830189 | 0.045594 |
| 5 | combined | scale_only | 265 | 223 | 53 | 0.227652 | 0.010503 | 0.647336 | 0.631728 | 0.803774 | 0.045901 |
| 5 | combined | slopes_without_intercept | 265 | 223 | 53 | 0.225022 | 0.010341 | 0.641167 | 0.628840 | 0.807547 | 0.045775 |
| 21 | combined | asymmetry_only | 217 | 159 | 11 | 0.244242 | 0.024755 | 0.681482 | 0.513201 | 0.654378 | 0.071955 |
| 21 | combined | bias_only | 217 | 159 | 11 | 0.272920 | 0.025984 | 0.741578 | 0.421441 | 0.645161 | 0.071357 |
| 21 | combined | exact_v14 | 217 | 217 | 11 | 0.245042 | 0.024989 | 0.683095 | 0.502675 | 0.668203 | 0.071794 |
| 21 | combined | fixed_half_law_mixture | 217 | 159 | 11 | 0.232452 | 0.024342 | 0.656922 | 0.561044 | 0.649770 | 0.072405 |
| 21 | combined | fixed_half_shift | 217 | 159 | 11 | 0.230941 | 0.024371 | 0.653528 | 0.556946 | 0.654378 | 0.071857 |
| 21 | combined | learned_history_law_mixture | 217 | 99 | 11 | 0.238075 | 0.024527 | 0.668617 | 0.554012 | 0.672811 | 0.071996 |
| 21 | combined | location_scale_asymmetry | 217 | 159 | 11 | 0.231117 | 0.024196 | 0.655216 | 0.568637 | 0.640553 | 0.066804 |
| 21 | combined | positions_v19_feature_set | 217 | 159 | 11 | 0.228199 | 0.024010 | 0.647076 | 0.568637 | 0.672811 | 0.071921 |
| 21 | combined | probability_only | 217 | 159 | 11 | 0.241145 | 0.024726 | 0.674313 | 0.504875 | 0.649770 | 0.071320 |
| 21 | combined | scale_only | 217 | 159 | 11 | 0.244596 | 0.025303 | 0.682153 | 0.497412 | 0.599078 | 0.066591 |
| 21 | combined | slopes_without_intercept | 217 | 159 | 11 | 0.232635 | 0.024136 | 0.657346 | 0.610656 | 0.677419 | 0.072217 |

| horizon | model | metric | n | disjoint | parent loss | loss | gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | corporate_v18_feature_set | brier | 223 | 45 | 0.224529 | 0.218954 | 0.005574 |
| 5 | corporate_v18_feature_set | crps | 223 | 45 | 0.011239 | 0.011084 | 0.000155 |
| 5 | location_scale_asymmetry | brier | 223 | 45 | 0.224529 | 0.216718 | 0.007811 |
| 5 | location_scale_asymmetry | crps | 223 | 45 | 0.011239 | 0.011195 | 0.000044 |
| 5 | probability_only | brier | 223 | 45 | 0.224529 | 0.221438 | 0.003091 |
| 5 | probability_only | crps | 223 | 45 | 0.011239 | 0.011239 | -6.52e-07 |
| 5 | fixed_half_law_mixture | brier | 223 | 45 | 0.224529 | 0.219676 | 0.004852 |
| 5 | fixed_half_law_mixture | crps | 223 | 45 | 0.011239 | 0.011079 | 0.000160 |
| 5 | learned_history_law_mixture | brier | 178 | 36 | 0.221976 | 0.219357 | 0.002619 |
| 5 | learned_history_law_mixture | crps | 178 | 36 | 0.012136 | 0.012124 | 0.000011 |
| 21 | positions_v19_feature_set | brier | 159 | 8 | 0.241294 | 0.218307 | 0.022988 |
| 21 | positions_v19_feature_set | crps | 159 | 8 | 0.025046 | 0.023710 | 0.001336 |
| 21 | location_scale_asymmetry | brier | 159 | 8 | 0.241294 | 0.222290 | 0.019004 |
| 21 | location_scale_asymmetry | crps | 159 | 8 | 0.025046 | 0.023964 | 0.001082 |
| 21 | probability_only | brier | 159 | 8 | 0.241294 | 0.235976 | 0.005318 |
| 21 | probability_only | crps | 159 | 8 | 0.025046 | 0.024687 | 0.000359 |
| 21 | fixed_half_law_mixture | brier | 159 | 8 | 0.241294 | 0.224111 | 0.017183 |
| 21 | fixed_half_law_mixture | crps | 159 | 8 | 0.025046 | 0.024163 | 0.000883 |
| 21 | learned_history_law_mixture | brier | 99 | 5 | 0.249953 | 0.234682 | 0.015271 |
| 21 | learned_history_law_mixture | crps | 99 | 5 | 0.024681 | 0.023669 | 0.001013 |

The monthly translation cap is 1.2 log percentage points and the weekly cap is 0.9. Shape experiments have separate scale and skew restrictions. The history-weighted mixture trains with earlier measured improvements and is capped at 0.75 correction weight.

[native-mechanism-laws.npz](native-mechanism-laws.npz) · [native-mechanism-cases.csv.gz](native-mechanism-cases.csv.gz) · [native-fit-receipts.ndjson.gz](native-fit-receipts.ndjson.gz) · [native-config.json](native-config.json) · [complete-matched-comparisons.csv](complete-matched-comparisons.csv) · [probability-calibration.csv](probability-calibration.csv)
