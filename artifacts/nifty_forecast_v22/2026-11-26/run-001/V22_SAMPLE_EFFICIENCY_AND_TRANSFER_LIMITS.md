# V22 Sample efficiency and transfer limits

Twenty cash indices provide country-specific labels, with substantial shared shocks across
the observations. A representative 21-session ex-India fit used median 2,901 eligible market rows across
161 distinct origin dates and 33 global weeks. The eigenvalue participation
ratio in the table describes cross-market dimensionality. It is an estimate of effective factor breadth and is not a
count of independent Indian forward outcomes.

The original 265 weekly and 217 monthly NIFTY origins yield only 53 and 11 disjoint windows. Overlap, related market regimes
and the reuse of the same historical outcomes further limit inference. Coefficient medians, interquartile range and sign
stability document parameter uncertainty. Negative transfer counts the markets whose later loss rose against the matched
reference. Distribution uncertainty in India remains the paired and dependence-adjusted interval width.

| horizon | markets | distinct dates | global week episodes | observed returns | effective rank | first eigen share | mean pair corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 20 | 492 | 99 | 9,327 | 4.975153 | 0.402337 | 0.343599 |
| 5 | 20 | 488 | 98 | 9,219 | 3.489972 | 0.512714 | 0.466074 |
| 21 | 20 | 472 | 95 | 8,792 | 3.538367 | 0.502903 | 0.454377 |

| horizon | model | metric | observed origins | n | gain | negative countries | countries observed | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | loco_transfer | brier | 1,775 | 96 | -0.005111 | 13 | 19 | -0.018394 | 0.008172 |
| 5 | loro_transfer | brier | 1,775 | 96 | -0.007922 | 16 | 19 | -0.021443 | 0.005599 |
| 5 | loco_transfer | rv_mae | 1,763 | 96 | 0.005886 | 2 | 19 | -0.001478 | 0.013249 |
| 5 | loro_transfer | rv_mae | 1,763 | 96 | 0.006474 | 3 | 19 | -0.002430 | 0.015378 |
| 5 | loco_transfer | expansion_brier | 1,763 | 96 | 0.009641 | 2 | 19 | 0.002615 | 0.016667 |
| 5 | loro_transfer | expansion_brier | 1,763 | 96 | 0.008724 | 4 | 19 | -0.000228 | 0.017675 |
| 21 | loco_transfer | brier | 1,474 | 80 | -0.026892 | 15 | 19 | -0.096247 | 0.042463 |
| 21 | loro_transfer | brier | 1,474 | 80 | -0.035391 | 14 | 19 | -0.099560 | 0.028777 |
| 21 | loco_transfer | rv_mae | 1,437 | 80 | 0.002448 | 9 | 19 | -0.003875 | 0.008771 |
| 21 | loro_transfer | rv_mae | 1,437 | 80 | 0.004870 | 8 | 19 | -0.006408 | 0.016148 |
| 21 | loco_transfer | expansion_brier | 1,437 | 80 | 0.041248 | 4 | 19 | 0.009007 | 0.073490 |
| 21 | loro_transfer | expansion_brier | 1,437 | 80 | 0.044473 | 3 | 19 | 0.009038 | 0.079907 |

## Controlled simulation

The six settings model stable shared slopes, separate country slopes, a shared shock with zero predictable return,
temporarily shared slopes, structural reversal, and an unrelated India. The generator uses correlated equity features,
46% common residual variance, and overlapping 5- or 21-session outcomes. Test windows are disjoint and use the real
evaluation counts. The two local budgets use 60 or 120 observed origins. We vary the foreign count from one to eight to
nineteen and refit four estimators per trial. The full experiment has 17,280 synthetic
trials. The representative table uses 60 local origins and 19 foreign markets. Positive gain means lower MSE than ordinary
zero-centered shrinkage. These are synthetic operating characteristics. Conclusions on NIFTY rely on the empirical study.

| horizon | data generator | model | test mse | parameter rmse | mean gain vs ordinary shrink | p10 gain vs ordinary shrink | p90 gain vs ordinary shrink | fraction beating ordinary shrink |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | stable_shared | india_only | 0.758639 | 0.105338 | -0.008127 | -0.053977 | 0.036906 | 0.458333 |
| 5 | stable_shared | foreign_only | 0.731036 | 0.046557 | 0.019476 | -0.022122 | 0.064319 | 0.687500 |
| 5 | stable_shared | partially_pooled | 0.739122 | 0.069095 | 0.011390 | -0.022586 | 0.054839 | 0.637500 |
| 5 | stable_shared | ordinary_zero_shrink | 0.750512 | 0.093185 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | country_specific | india_only | 0.743488 | 0.100514 | 0.014515 | -0.040292 | 0.072462 | 0.587500 |
| 5 | country_specific | foreign_only | 0.869851 | 0.220917 | -0.111847 | -0.235818 | -0.003612 | 0.091667 |
| 5 | country_specific | partially_pooled | 0.764187 | 0.125831 | -0.006184 | -0.026559 | 0.013900 | 0.362500 |
| 5 | country_specific | ordinary_zero_shrink | 0.758003 | 0.118813 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | global_shocks_no_signal | india_only | 0.762955 | 0.103707 | -0.022995 | -0.055015 | 0.002913 | 0.154167 |
| 5 | global_shocks_no_signal | foreign_only | 0.735361 | 0.044517 | 0.004599 | -0.026762 | 0.033661 | 0.570833 |
| 5 | global_shocks_no_signal | partially_pooled | 0.744079 | 0.068281 | -0.004119 | -0.016254 | 0.006555 | 0.366667 |
| 5 | global_shocks_no_signal | ordinary_zero_shrink | 0.739961 | 0.058262 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | temporary_shared | india_only | 0.756990 | 0.130371 | -0.031792 | -0.067033 | -0.000271 | 0.095833 |
| 5 | temporary_shared | foreign_only | 0.737321 | 0.094812 | -0.012123 | -0.051950 | 0.019415 | 0.316667 |
| 5 | temporary_shared | partially_pooled | 0.744050 | 0.110266 | -0.018852 | -0.045151 | 0.005569 | 0.204167 |
| 5 | temporary_shared | ordinary_zero_shrink | 0.725198 | 0.074442 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | structural_reversal | india_only | 0.957034 | 0.290610 | -0.105198 | -0.184247 | -0.035695 | 0.012500 |
| 5 | structural_reversal | foreign_only | 0.933025 | 0.272841 | -0.081188 | -0.169767 | -0.013479 | 0.058333 |
| 5 | structural_reversal | partially_pooled | 0.951808 | 0.286261 | -0.099971 | -0.152333 | -0.049202 | 0.004167 |
| 5 | structural_reversal | ordinary_zero_shrink | 0.851836 | 0.218570 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 5 | india_unrelated | india_only | 0.759177 | 0.105114 | -0.021781 | -0.053371 | 0.005085 | 0.175000 |
| 5 | india_unrelated | foreign_only | 0.790566 | 0.142534 | -0.053171 | -0.139358 | 0.020938 | 0.183333 |
| 5 | india_unrelated | partially_pooled | 0.755256 | 0.096026 | -0.017861 | -0.059125 | 0.017764 | 0.325000 |
| 5 | india_unrelated | ordinary_zero_shrink | 0.737395 | 0.059396 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 21 | stable_shared | india_only | 0.803382 | 0.101726 | -0.001455 | -0.089285 | 0.082667 | 0.545833 |
| 21 | stable_shared | foreign_only | 0.778671 | 0.044238 | 0.023256 | -0.066742 | 0.132981 | 0.575000 |
| 21 | stable_shared | partially_pooled | 0.784262 | 0.065713 | 0.017665 | -0.065628 | 0.095083 | 0.587500 |
| 21 | stable_shared | ordinary_zero_shrink | 0.801927 | 0.093570 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 21 | country_specific | india_only | 0.791031 | 0.103613 | 0.013723 | -0.103447 | 0.138483 | 0.545833 |
| 21 | country_specific | foreign_only | 0.917540 | 0.221803 | -0.112786 | -0.317261 | 0.056106 | 0.262500 |
| 21 | country_specific | partially_pooled | 0.812525 | 0.125827 | -0.007771 | -0.043665 | 0.023952 | 0.412500 |
| 21 | country_specific | ordinary_zero_shrink | 0.804754 | 0.118684 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 21 | global_shocks_no_signal | india_only | 0.721752 | 0.101100 | -0.022065 | -0.081189 | 0.020780 | 0.283333 |
| 21 | global_shocks_no_signal | foreign_only | 0.695736 | 0.042899 | 0.003952 | -0.051998 | 0.059067 | 0.537500 |
| 21 | global_shocks_no_signal | partially_pooled | 0.704521 | 0.067452 | -0.004834 | -0.024960 | 0.012128 | 0.416667 |
| 21 | global_shocks_no_signal | ordinary_zero_shrink | 0.699687 | 0.057705 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 21 | temporary_shared | india_only | 0.789094 | 0.131029 | -0.035795 | -0.119640 | 0.034982 | 0.275000 |
| 21 | temporary_shared | foreign_only | 0.765823 | 0.096192 | -0.012524 | -0.085469 | 0.055108 | 0.425000 |
| 21 | temporary_shared | partially_pooled | 0.774219 | 0.111794 | -0.020920 | -0.078747 | 0.032631 | 0.308333 |
| 21 | temporary_shared | ordinary_zero_shrink | 0.753299 | 0.074103 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 21 | structural_reversal | india_only | 0.962209 | 0.283436 | -0.097622 | -0.219242 | 0.003068 | 0.108333 |
| 21 | structural_reversal | foreign_only | 0.949672 | 0.273349 | -0.085085 | -0.207134 | 0.029069 | 0.162500 |
| 21 | structural_reversal | partially_pooled | 0.961033 | 0.282410 | -0.096446 | -0.216604 | -0.000756 | 0.100000 |
| 21 | structural_reversal | ordinary_zero_shrink | 0.864587 | 0.214175 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 21 | india_unrelated | india_only | 0.757193 | 0.102801 | -0.021920 | -0.071497 | 0.019957 | 0.337500 |
| 21 | india_unrelated | foreign_only | 0.779891 | 0.144605 | -0.044619 | -0.204355 | 0.112016 | 0.370833 |
| 21 | india_unrelated | partially_pooled | 0.747729 | 0.094358 | -0.012456 | -0.090222 | 0.064680 | 0.416667 |
| 21 | india_unrelated | ordinary_zero_shrink | 0.735273 | 0.058007 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

[synthetic-transfer-sample-efficiency.csv](synthetic-transfer-sample-efficiency.csv) · [synthetic-transfer-design.json](synthetic-transfer-design.json) · [international-dependence.csv](international-dependence.csv) · [transfer-coefficient-stability.csv](transfer-coefficient-stability.csv) · [international-fit-receipts-21.csv](international-fit-receipts-21.csv) · [india-search-adjusted-intervals.csv.gz](india-search-adjusted-intervals.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
