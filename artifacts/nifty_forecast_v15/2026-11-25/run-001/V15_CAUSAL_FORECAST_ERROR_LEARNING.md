# V15 learning from resolved forecast errors

V14's **712** severe records represent **108** unique horizon–origin windows. The ledger separates unexpected upside/downside, volatility underestimation/overestimation, range errors, overconfident direction, tail misses and barrier errors. Causal error features become eligible only when the original target session is strictly earlier than the current origin. At each origin the experiment fits on up to 120 eligible original forecast errors and uses up to 12 resolved errors for the recent state. Disagreement comes from the original dispersion of volatility and probability models, standardized error histories, analogue diversity, relative feature scales, parameter shifts, and implied versus trailing risk. It compares historical frequency, recent frequency and a nominal threshold, as well as asymmetric and width-only interval corrections and shrunken direction scores.

## Range diagnostics on identical origins

| horizon | task | model | cases | brier | log loss | coverage | width | interval score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | interval80 | asymmetric_error_quantiles | 235 | — | — | 0.795745 | 0.022552 | 0.043339 |
| 5 | interval80 | original_interval | 235 | — | — | 0.774468 | 0.021675 | 0.040641 |
| 5 | interval80 | width_only | 235 | — | — | 0.744681 | 0.021382 | 0.045887 |
| 5 | overestimated_lower | causal_error_features | 235 | 0.057173 | 0.229703 | — | — | — |
| 5 | overestimated_lower | matured_frequency | 235 | 0.057086 | 0.235266 | — | — | — |
| 5 | overestimated_lower | nominal_fixed | 235 | 0.057660 | 0.236259 | — | — | — |
| 5 | overestimated_lower | recent_frequency | 235 | 0.057851 | 0.230963 | — | — | — |
| 5 | underestimated_upper | causal_error_features | 235 | 0.154284 | 0.539191 | — | — | — |
| 5 | underestimated_upper | matured_frequency | 235 | 0.149479 | 0.511781 | — | — | — |
| 5 | underestimated_upper | nominal_fixed | 235 | 0.142766 | 0.470006 | — | — | — |
| 5 | underestimated_upper | recent_frequency | 235 | 0.143388 | 0.475940 | — | — | — |
| 21 | interval80 | asymmetric_error_quantiles | 171 | — | — | 0.766082 | 0.053581 | 0.126832 |
| 21 | interval80 | original_interval | 171 | — | — | 0.771930 | 0.044870 | 0.113196 |
| 21 | interval80 | width_only | 171 | — | — | 0.713450 | 0.053370 | 0.134719 |
| 21 | overestimated_lower | causal_error_features | 171 | 0.003580 | 0.048305 | — | — | — |
| 21 | overestimated_lower | matured_frequency | 171 | 0.010193 | 0.080397 | — | — | — |
| 21 | overestimated_lower | nominal_fixed | 171 | 0.010000 | 0.105361 | — | — | — |
| 21 | overestimated_lower | recent_frequency | 171 | 0.002066 | 0.046520 | — | — | — |
| 21 | underestimated_upper | causal_error_features | 171 | 0.266520 | 0.825186 | — | — | — |
| 21 | underestimated_upper | matured_frequency | 171 | 0.221187 | 0.706708 | — | — | — |
| 21 | underestimated_upper | nominal_fixed | 171 | 0.192456 | 0.606482 | — | — | — |
| 21 | underestimated_upper | recent_frequency | 171 | 0.193490 | 0.575052 | — | — | — |

## Archived failure families

| horizon | kind | rows | origins | worst | first | last |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | large_barrier_error | 60 | 13 | 1.000000 | 2025-10-14 | 2026-11-04 |
| 5 | largest_brier | 32 | 15 | 0.777704 | 2025-11-18 | 2026-06-16 |
| 5 | largest_crps | 32 | 8 | 0.079401 | 2026-03-30 | 2026-11-04 |
| 5 | range_underestimate | 64 | 9 | 0.041025 | 2026-01-28 | 2026-11-03 |
| 5 | unexpected_down | 56 | 13 | 0.028144 | 2026-01-02 | 2026-09-24 |
| 5 | unexpected_up | 56 | 11 | 0.064231 | 2026-03-30 | 2026-11-04 |
| 5 | volatility_underestimate | 48 | 15 | 0.197230 | 2026-01-28 | 2026-11-04 |
| 21 | large_barrier_error | 60 | 19 | 0.986375 | 2025-12-31 | 2026-09-09 |
| 21 | largest_brier | 32 | 21 | 0.493951 | 2025-12-10 | 2026-10-15 |
| 21 | largest_crps | 32 | 9 | 0.107020 | 2026-02-11 | 2026-10-14 |
| 21 | range_underestimate | 72 | 15 | 0.070232 | 2026-02-12 | 2026-10-15 |
| 21 | unexpected_down | 64 | 9 | 0.098399 | 2026-02-11 | 2026-02-26 |
| 21 | unexpected_up | 64 | 9 | 0.085138 | 2026-03-30 | 2026-10-15 |
| 21 | volatility_underestimate | 40 | 12 | 0.164359 | 2026-02-19 | 2026-03-18 |

The monthly lower miss was extremely sparse. Brier comparisons on that subset were dominated by predicted false positives. The monthly upper warning and weekly upper warning remain difficult, including against a constant nominal-probability control. Width or asymmetry correction is scored for both coverage and interval loss. V15 retains the larger uncertainty in the central law and keeps stress paths separate.

[Failure features and outcome maturation](causal-error-scores.csv.gz) [All error comparisons](causal-error-evidence.csv) [Warning model coefficients](causal-error-fit-ledger.json) [V14 archived negative warning comparison](../../../nifty_forecast_v14/2026-11-25/run-001/failure-warning-matched.csv)
