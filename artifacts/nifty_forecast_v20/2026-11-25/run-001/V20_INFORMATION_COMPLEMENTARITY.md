# V20 Information Complementarity

We evaluated the unchanged structural law and all **31 nonempty subsets** of five predeclared groups at 08:55 for both original horizons. The blocks are native structure, corporate information, participant positioning, delivery and market-implied/realized risk. The incremental slope excludes its intercept, and the parent law handles missing training. This holds baseline shape and shrinkage policy fixed so that marginal changes and conflicting effects can be observed on matched forecasts. Shapley averages across all addition orders. The first and last columns show the marginal difference from the empty group and from the full group with that block removed.

| horizon | block | brier | crps | first brier | last brier |
| --- | --- | --- | --- | --- | --- |
| 5 | corporate | -0.002408 | -0.000052 | -0.003105 | -0.002488 |
| 5 | delivery | 0.000916 | 0.000022 | 0.001434 | 0.000106 |
| 5 | native_market | -0.001631 | -0.000026 | -0.002346 | -0.000869 |
| 5 | positioning | -0.000914 | 0.000064 | -0.001026 | -0.001175 |
| 5 | volatility | 0.004630 | 0.000046 | 0.003710 | 0.004956 |
| 21 | corporate | 0.006728 | 0.000162 | 0.010967 | 0.002046 |
| 21 | delivery | -0.002187 | -0.000025 | -0.004322 | -0.000687 |
| 21 | native_market | 0.003059 | 0.000111 | 0.003234 | 0.002180 |
| 21 | positioning | 0.023165 | 0.000955 | 0.023911 | 0.019829 |
| 21 | volatility | -0.003332 | -0.000091 | -0.008205 | -0.000522 |

| horizon | cohort | n | forecast rank | error rank | correction rank |
| --- | --- | --- | --- | --- | --- |
| 5 | early | 173 | 0.929979 | 0.992895 | -0.052864 |
| 5 | later | 92 | 0.792519 | 0.923678 | -0.171678 |
| 21 | early | 141 | -0.094559 | 0.985685 | -0.120426 |
| 21 | later | 76 | 0.218592 | 0.959289 | 0.333832 |

| horizon | pair | median absolute pairwise feature rank | max absolute pairwise feature rank |
| --- | --- | --- | --- |
| 5 | corporate / delivery | 0.077178 | 0.347119 |
| 5 | corporate / positioning | 0.124356 | 0.434477 |
| 5 | corporate / volatility | 0.163849 | 0.539231 |
| 5 | native_market / corporate | 0.074002 | 0.378575 |
| 21 | corporate / delivery | 0.088473 | 0.367664 |
| 21 | corporate / positioning | 0.109033 | 0.504025 |
| 21 | corporate / volatility | 0.158183 | 0.751007 |
| 21 | native_market / corporate | 0.079113 | 0.467471 |

Forecast correlations, error correlations and the correlation of incremental shifts measure different kinds of duplication. The separate prior training feature correlation records contain only earlier points at the moment of each fit. An exact duplicate enters the fit only once, and mixtures of identical expert laws reduce to the identical input law. These comparisons describe forecast estimation and are distinct from economic attribution.

[complementarity-cases.csv.gz](complementarity-cases.csv.gz) · [complementarity-shapley.csv.gz](complementarity-shapley.csv.gz) · [complementarity-prediction-correlation.csv](complementarity-prediction-correlation.csv) · [complementarity-feature-redundancy.csv](complementarity-feature-redundancy.csv) · [native-mechanism-cases.csv.gz](native-mechanism-cases.csv.gz)
