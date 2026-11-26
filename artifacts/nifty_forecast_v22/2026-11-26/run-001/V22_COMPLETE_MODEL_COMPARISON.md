# V22 Complete model comparison

The original 265 weekly and 217 monthly forecasts are retained on the exact same Indian calendar, with 173/92 and
141/76 early/later outcomes and 53/11 disjoint windows. Forecasts with limited eligibility are scored both with their
declared fallback on the original population and on their active dates against the parent replayed on those dates.
Model coverage and realized opportunity coverage are both observable.

Brier, log loss, CRPS, mean absolute and squared error, hit and balanced accuracy, rank correlation, reliability bins,
interval calibration and forecast coverage accompany the return distributions. QLIKE scores variance ratios in the risk
lane. Independence-aware intervals and episode omission are paired by forecast day. The refit and reselection experiment
probes recent variant selection and the historical record remains exposed to V1–V22 research.

## Evidence index

| comparison | evidence | coverage |
| --- | --- | --- |
| International direction and distributions | [international-model-leaderboard.csv](international-model-leaderboard.csv) | Country-level and chronological model comparisons with Brier, log loss, CRPS, accuracy, balanced accuracy, MAE, RMSE, rank, interval coverage and risk. |
| Country and region generalization | [international-matched-country-region.csv.gz](international-matched-country-region.csv.gz) | Matched loss by market and by held-out region, with the opportunity count for each event. |
| International mechanisms and uncertainty | [international-matched-date-intervals.csv.gz](international-matched-date-intervals.csv.gz) | Date-weighted comparisons, negative countries, raw and family-adjusted block limits. |
| Historical analogue retrieval | [analogue-law-atlas.csv](analogue-law-atlas.csv) | Membership, distinct dates, weeks and regions, Kish effective count, and weights. |
| Standalone analogue paths | [analogue-risk-cases.csv.gz](analogue-risk-cases.csv.gz) | Terminal, point and tail/path outcomes from the retrieved OHLC scenarios. |
| India adaptation | [india-adaptation-fit-receipts.csv.gz](india-adaptation-fit-receipts.csv.gz) | Exact local budgets, pool maturity, penalties and local or foreign priors. |
| Original NIFTY direction and coherent distributions | [india-return-leaderboard.csv](india-return-leaderboard.csv) | Both horizons and clocks, early, later, combined, and active results. |
| Matched NIFTY effects | [india-matched-comparisons.csv.gz](india-matched-comparisons.csv.gz) | Both protected reference families, active coverage, explicit paired comparisons. |
| Volatility and market risk | [india-risk-and-tail-leaderboard.csv](india-risk-and-tail-leaderboard.csv) | Protected point and path risk versus new hybrids at same definitions. |
| Tail and path results | [india-risk-path-comparison-cases.csv.gz](india-risk-path-comparison-cases.csv.gz) | Calibrated range, drawdown, move/touch tails, expansion and contraction. |

## Best in each retrospective clock and horizon

| horizon | cutoff | model | n | active | brier | crps | mae | rmse | accuracy | balanced accuracy | rank corr | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | secondary_location_beyond_gift | 265 | 216 | 0.220133 | 0.010180 | 0.014217 | 0.020337 | 0.652830 | 0.656965 | 0.395852 | 0.826415 | 0.045773 |
| 5 | native_0910 | secondary_location_domestic_only | 265 | 216 | 0.220368 | 0.010130 | 0.014221 | 0.020263 | 0.641509 | 0.644144 | 0.389772 | 0.830189 | 0.045758 |
| 5 | native_0910 | parent_location_offshore_only | 265 | 216 | 0.220463 | 0.010128 | 0.014385 | 0.020129 | 0.660377 | 0.654770 | 0.393046 | 0.818868 | 0.045776 |
| 5 | native_0910 | parent_location_domestic_only | 265 | 216 | 0.222142 | 0.010121 | 0.014352 | 0.019939 | 0.645283 | 0.645732 | 0.403171 | 0.822642 | 0.045852 |
| 5 | preauction_0855 | parent_location_beyond_gift | 265 | 216 | 0.235660 | 0.010336 | 0.014316 | 0.019519 | 0.615094 | 0.616915 | 0.313061 | 0.762264 | 0.042019 |
| 5 | preauction_0855 | parent_robust_location | 265 | 216 | 0.236033 | 0.010395 | 0.014456 | 0.019783 | 0.615094 | 0.611544 | 0.307243 | 0.769811 | 0.041975 |
| 5 | preauction_0855 | parent_location_combined | 265 | 216 | 0.236139 | 0.010322 | 0.014317 | 0.019489 | 0.626415 | 0.627945 | 0.322914 | 0.762264 | 0.042018 |
| 5 | preauction_0855 | parent_mixture_analogues | 265 | 265 | 0.238483 | 0.010270 | 0.014116 | 0.019324 | 0.596226 | 0.602708 | 0.308291 | 0.792453 | 0.044332 |
| 5 | preauction_0855 | parent_location_domestic_only | 265 | 216 | 0.237134 | 0.010281 | 0.014234 | 0.019418 | 0.600000 | 0.598031 | 0.306109 | 0.769811 | 0.041996 |
| 5 | preauction_0855 | archived_same_clock | 265 | 265 | 0.238113 | 0.010309 | 0.014286 | 0.019532 | 0.577358 | 0.575970 | 0.290602 | 0.766038 | 0.041981 |
| 21 | native_0910 | parent_mixture_foreign_tail | 217 | 217 | 0.223431 | 0.023174 | 0.029781 | 0.043039 | 0.580645 | 0.620060 | 0.510741 | 0.755760 | 0.094566 |
| 21 | native_0910 | anchor_aggregate_position | 217 | 217 | 0.223819 | 0.023184 | 0.029737 | 0.043023 | 0.576037 | 0.615962 | 0.510715 | 0.714286 | 0.071940 |
| 21 | native_0910 | secondary_asymmetry_only | 217 | 152 | 0.224894 | 0.023982 | 0.031246 | 0.044028 | 0.576037 | 0.611303 | 0.328275 | 0.672811 | 0.071870 |
| 21 | native_0910 | parent_asymmetry_only | 217 | 152 | 0.227765 | 0.023262 | 0.029737 | 0.043022 | 0.562212 | 0.605997 | 0.511114 | 0.709677 | 0.071879 |
| 21 | preauction_0855 | stock_gaussian_shrink | 217 | 217 | 0.236048 | 0.024729 | 0.032186 | 0.044173 | 0.603687 | 0.606773 | 0.292687 | 0.718894 | 0.081773 |
| 21 | preauction_0855 | secondary_location_beyond_gift | 217 | 152 | 0.245374 | 0.025174 | 0.033531 | 0.046081 | 0.502304 | 0.511950 | 0.016966 | 0.718894 | 0.083311 |
| 21 | preauction_0855 | secondary_location_domestic_only | 217 | 152 | 0.245375 | 0.025135 | 0.033508 | 0.046254 | 0.479263 | 0.484469 | -0.068630 | 0.709677 | 0.083292 |
| 21 | preauction_0855 | secondary_mixture_foreign_tail | 217 | 217 | 0.251138 | 0.024577 | 0.033197 | 0.044586 | 0.460829 | 0.503020 | 0.199660 | 0.778802 | 0.099521 |
| 21 | preauction_0855 | archived_joint_GJR | 217 | 217 | 0.251376 | 0.024694 | 0.033162 | 0.044571 | 0.479263 | 0.524072 | 0.192655 | 0.709677 | 0.083754 |
| 21 | preauction_0855 | secondary_sign_only | 217 | 152 | 0.255438 | 0.024728 | 0.033064 | 0.044588 | 0.470046 | 0.486756 | 0.095582 | 0.691244 | 0.082251 |

[international-probability-calibration.csv](international-probability-calibration.csv) · [india-probability-calibration.csv](india-probability-calibration.csv) · [india-search-adjusted-intervals.csv.gz](india-search-adjusted-intervals.csv.gz) · [india-risk-matched-intervals.csv](india-risk-matched-intervals.csv) · [representative-blocked-refit-summary.csv](representative-blocked-refit-summary.csv)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
