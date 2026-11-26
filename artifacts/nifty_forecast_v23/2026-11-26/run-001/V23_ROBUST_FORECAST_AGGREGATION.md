# V23 Robust forecast aggregation

The candidate panel compares distinct historical, domestic, positioning, corporate, risk, breadth, offshore and
transferred mechanisms with the original same-clock leaders. Cases weight whole probability laws. Equal-family
weighting fixes total mass across groups and divides it among their deduplicated members. Redundancy-aware weights
use earlier quantile distances. The robust rule clips mature paired loss excursions. The worst-environment rule
scores both earlier volatility groups only when each has 18 usable observations. Bayesian weights average a bounded
Dirichlet pseudo-posterior driven by date-block loss draws. Quantile pooling averages ordered quantiles into a valid
marginal law. Joint path dependence is scored separately on full OHLC laws.

Every adaptive fit uses at most 120 earlier complete labels with a minimum of 36. An identical expert over the fit
history and current support is one vote. Fixed zero-weight, neutral shrinkage, historical shrinkage, equal-weight
and randomized expert controls all face the same origins. Most pooled laws diluted the strongest native signal.
The exact V11 ensemble archive supplies an earlier-clock context. Previous 17:00 V17 structural pooling is directly scored on that clock.

| horizon | model | n | active | brier | crps | log loss | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | agg_bayesian | 265 | 225 | 0.231920 | 0.010322 | 0.656435 | 0.826415 | 0.047067 |
| 5 | agg_loss_mean | 265 | 225 | 0.231626 | 0.010317 | 0.655834 | 0.826415 | 0.047034 |
| 5 | agg_loss_robust | 265 | 225 | 0.231773 | 0.010318 | 0.656106 | 0.826415 | 0.047080 |
| 5 | agg_minimax_env | 265 | 225 | 0.231256 | 0.010311 | 0.655087 | 0.826415 | 0.046978 |
| 5 | agg_redundancy | 265 | 225 | 0.236616 | 0.010467 | 0.665994 | 0.815094 | 0.047627 |
| 5 | equal_families | 265 | 265 | 0.232794 | 0.010335 | 0.658198 | 0.826415 | 0.047240 |
| 5 | equal_models | 265 | 265 | 0.230024 | 0.010247 | 0.652507 | 0.830189 | 0.046887 |
| 5 | fixed_20pct_history | 265 | 265 | 0.224221 | 0.010112 | 0.640200 | 0.822642 | 0.045713 |
| 5 | fixed_20pct_neutral | 265 | 265 | 0.223891 | 0.010093 | 0.639382 | 0.826415 | 0.045766 |
| 5 | history_only | 265 | 265 | 0.254538 | 0.011221 | 0.702284 | 0.762264 | 0.041541 |
| 5 | protected_direction | 265 | 265 | 0.220133 | 0.010180 | 0.630806 | 0.826415 | 0.045773 |
| 5 | protected_distribution | 265 | 265 | 0.222142 | 0.010121 | 0.635180 | 0.822642 | 0.045852 |
| 5 | quantile_family_pool | 265 | 265 | 0.229988 | 0.010356 | 0.652358 | 0.815094 | 0.046387 |
| 5 | randomized_fixed_weights | 265 | 265 | 0.224696 | 0.010142 | 0.641459 | 0.826415 | 0.045841 |
| 5 | uncertainty_guarded_mixture | 265 | 225 | 0.223552 | 0.010135 | 0.638498 | 0.833962 | 0.046153 |
| 21 | agg_bayesian | 217 | 161 | 0.248975 | 0.024660 | 0.693500 | 0.723502 | 0.084749 |
| 21 | agg_loss_mean | 217 | 161 | 0.248648 | 0.024625 | 0.693113 | 0.723502 | 0.084329 |
| 21 | agg_loss_robust | 217 | 161 | 0.248899 | 0.024649 | 0.693458 | 0.718894 | 0.084670 |
| 21 | agg_minimax_env | 217 | 161 | 0.248371 | 0.024614 | 0.692516 | 0.723502 | 0.083863 |
| 21 | agg_redundancy | 217 | 161 | 0.255773 | 0.025117 | 0.706641 | 0.723502 | 0.090596 |
| 21 | equal_families | 217 | 217 | 0.250961 | 0.024821 | 0.696780 | 0.723502 | 0.086581 |
| 21 | equal_models | 217 | 217 | 0.255985 | 0.025052 | 0.707535 | 0.705069 | 0.084124 |
| 21 | fixed_20pct_history | 217 | 217 | 0.230132 | 0.023484 | 0.654356 | 0.723502 | 0.075145 |
| 21 | fixed_20pct_neutral | 217 | 217 | 0.222577 | 0.023298 | 0.638591 | 0.714286 | 0.074437 |
| 21 | history_only | 217 | 217 | 0.299993 | 0.027228 | 0.799994 | 0.718894 | 0.091466 |
| 21 | protected_direction | 217 | 217 | 0.223431 | 0.023174 | 0.642855 | 0.755760 | 0.094566 |
| 21 | protected_distribution | 217 | 217 | 0.223819 | 0.023184 | 0.646636 | 0.714286 | 0.071940 |
| 21 | quantile_family_pool | 217 | 217 | 0.253890 | 0.025009 | 0.703873 | 0.714286 | 0.083160 |
| 21 | randomized_fixed_weights | 217 | 217 | 0.257405 | 0.024632 | 0.711784 | 0.723502 | 0.082017 |
| 21 | uncertainty_guarded_mixture | 217 | 161 | 0.224475 | 0.023326 | 0.644135 | 0.728111 | 0.076276 |

## Earlier-clock controls and previous ensembles

| horizon | model | n | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | agg_redundancy | 263 | 0.240301 | 0.010694 |
| 5 | equal_families | 263 | 0.240349 | 0.010703 |
| 5 | equal_models | 263 | 0.240493 | 0.010714 |
| 5 | protected_direction | 263 | 0.239416 | 0.010698 |
| 5 | protected_distribution | 263 | 0.239910 | 0.010734 |
| 5 | quantile_family_pool | 263 | 0.240537 | 0.010727 |
| 21 | agg_redundancy | 216 | 0.285249 | 0.027571 |
| 21 | equal_families | 216 | 0.287416 | 0.027759 |
| 21 | equal_models | 216 | 0.289240 | 0.027930 |
| 21 | protected_direction | 216 | 0.250000 | 0.025642 |
| 21 | protected_distribution | 216 | 0.306401 | 0.028855 |
| 21 | quantile_family_pool | 216 | 0.295697 | 0.027901 |

[ensemble-date-weights.csv.gz](ensemble-date-weights.csv.gz) · [original-horizon-search-adjusted-intervals.csv.gz](original-horizon-search-adjusted-intervals.csv.gz) · [v11-exact-ensemble-benchmarks.csv](v11-exact-ensemble-benchmarks.csv) · [leakage-and-duplication-checks.json](leakage-and-duplication-checks.json)

[Back to the research index](NIFTY_V23_RESEARCH.md)
