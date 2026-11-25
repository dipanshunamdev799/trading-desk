# V16 Advanced opening-gap forecasting

The opening target is the official NIFTY 50 open divided by the previous official NIFTY 50 close minus one. The consecutive date comes from the frozen NSE cash sequence and is verified independently from archive identity. The primary table scores arithmetic gap returns. The V15 exact benchmark replay preserves its log-return CRPS. Cross-version distribution comparisons transform the original forecast atoms to arithmetic returns before computing the paired loss. Direction accuracy uses a 0.5 probability threshold. Balanced accuracy averages hit rates for up and down. CRPS, absolute median error, root mean square error of the mean and central 80% coverage score magnitude and uncertainty directly.

## 08:55 pre-auction distributions

| model | n | brier | log loss | correct | balanced accuracy | crps | mae | rmse | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gift_roll_screened | 180 | 0.095052 | 0.309946 | 0.888889 | 0.889081 | 0.001203 | 0.001667 | 0.002194 | 0.800000 | 0.004874 |
| gift_raw | 248 | 0.100841 | 0.348603 | 0.887097 | 0.887097 | 0.001459 | 0.001965 | 0.002777 | 0.766129 | 0.005638 |
| gift_calibrated | 248 | 0.100937 | 0.349021 | 0.870968 | 0.870968 | 0.001451 | 0.001959 | 0.002763 | 0.778226 | 0.005639 |
| gift_plus_global | 248 | 0.102878 | 0.353112 | 0.866935 | 0.866935 | 0.001482 | 0.001992 | 0.002823 | 0.766129 | 0.005637 |
| rich_global_ridge | 258 | 0.195252 | 0.573719 | 0.713178 | 0.713101 | 0.002569 | 0.003348 | 0.005423 | 0.806202 | 0.010090 |
| sign_magnitude | 258 | 0.205212 | 0.596147 | 0.686047 | 0.685397 | 0.002930 | 0.003761 | 0.006155 | 0.759690 | 0.009746 |
| asia_partial | 258 | 0.209165 | 0.610449 | 0.686047 | 0.685817 | 0.002831 | 0.003638 | 0.006098 | 0.790698 | 0.010090 |
| cluster_balanced | 258 | 0.221330 | 0.639448 | 0.674419 | 0.674099 | 0.002907 | 0.003741 | 0.006208 | 0.782946 | 0.010090 |
| single_US | 258 | 0.224937 | 0.642687 | 0.631783 | 0.631190 | 0.002999 | 0.003832 | 0.006412 | 0.771318 | 0.010091 |
| six_cash | 258 | 0.225079 | 0.651462 | 0.662791 | 0.662440 | 0.002939 | 0.003779 | 0.006224 | 0.767442 | 0.010091 |
| student_location_scale | 258 | 0.229549 | 0.662560 | 0.643411 | 0.643209 | 0.002928 | 0.003855 | 0.006232 | 0.705426 | 0.008447 |
| disagreement | 258 | 0.230063 | 0.659555 | 0.655039 | 0.654748 | 0.002963 | 0.003826 | 0.006287 | 0.779070 | 0.010091 |
| shallow_interactions | 258 | 0.232109 | 0.668256 | 0.627907 | 0.627404 | 0.002966 | 0.003847 | 0.006294 | 0.790698 | 0.010091 |
| equal_six | 258 | 0.237415 | 0.670114 | 0.600775 | 0.600060 | 0.003037 | 0.003895 | 0.006425 | 0.763566 | 0.010090 |
| neutral | 258 | 0.250000 | 0.693147 | 0.503876 | 0.500000 | 0.003171 | 0.004054 | 0.006695 | 0.728682 | 0.010140 |
| historical | 258 | 0.253615 | 0.700465 | 0.484496 | 0.482933 | 0.003194 | 0.004076 | 0.006718 | 0.728682 | 0.010091 |
| domestic | 258 | 0.257213 | 0.723334 | 0.577519 | 0.576983 | 0.003238 | 0.004115 | 0.006800 | 0.720930 | 0.010091 |
| prior_return | 258 | 0.263743 | 0.734012 | 0.457364 | 0.455589 | 0.003249 | 0.004128 | 0.006808 | 0.701550 | 0.010091 |

## Matched comparison with exact V15 baseline

| candidate | control | metric | n | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single_US | V15_offshore_fresh | brier | 258 | 0.224937 | 0.227947 | 0.003010 | -0.017130 | 0.023151 |
| single_US | V15_offshore_fresh | crps | 258 | 0.002999 | 0.002924 | -0.000075 | -0.000210 | 0.000060 |
| gift_raw | V15_offshore_fresh | brier | 248 | 0.100841 | 0.230235 | 0.129393 | 0.095394 | 0.163392 |
| gift_raw | V15_offshore_fresh | crps | 248 | 0.001459 | 0.002985 | 0.001526 | 0.000443 | 0.002608 |
| asia_partial | V15_offshore_fresh | brier | 258 | 0.209165 | 0.227947 | 0.018782 | -0.010665 | 0.048230 |
| asia_partial | V15_offshore_fresh | crps | 258 | 0.002831 | 0.002924 | 0.000093 | -0.000094 | 0.000279 |

## Matched comparison with the simple offshore factor

| candidate | metric | n | candidate loss | control loss | gain | early gain | later gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gift_raw | brier | 248 | 0.100841 | 0.233717 | 0.132876 | 0.120182 | 0.144969 | 0.100207 | 0.165544 |
| gift_raw | crps | 248 | 0.001459 | 0.003075 | 0.001616 | 0.002018 | 0.001232 | 0.000269 | 0.002963 |
| gift_raw | log_loss | 248 | 0.348603 | 0.662008 | 0.313405 | 0.281028 | 0.344253 | 0.186132 | 0.440679 |
| gift_raw | mae | 248 | 0.001965 | 0.003929 | 0.001965 | 0.002325 | 0.001621 | 0.000360 | 0.003569 |

Neutral uses symmetric empirical magnitudes. Other baselines include matured historical frequencies and distances, previous domestic state, S&P alone and an equally weighted six-market factor. The larger linear model uses robust train-only imputation, center and scales. Student-t distributional regression forecasts conditional location and scale, while the sign/magnitude system estimates the two tail masses separately. The cluster-balanced fit combines two disjoint date blocks in rotation, and the shallow-interaction model adds a small set of normalized cross-market products. The fit ledger records the terms and eligible labels. Macroeconomic source date checks use the clock map. Reliability is recorded for sign and for ±0.5% and ±1% thresholds, with sparse bins kept visible. Domestic or GIFT plus additional global terms are compared on exact common dates at each deadline.

[Leaderboard by clock, cohort and target](session-leaderboard.csv) · [Brier and tail reliability bins](gap-reliability.csv) · [All matched gains and adjusted bounds](session-matched-evidence.csv) · [Replayed V15 on common return units](v15-v16-opening-matched.csv) · [08:55 forecast atoms](opening-0855-laws.npz) · [08:55 per-origin forecasts](opening-0855-scores.csv.gz) · [08:55 fitted parameters](opening-0855-fits.ndjson.gz)
