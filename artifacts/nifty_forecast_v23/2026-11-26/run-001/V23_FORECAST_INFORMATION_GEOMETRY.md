# V23 Forecast information geometry

Compared 27,911 exact case laws across 44 distinct archived experts. Probability, expected return,
dispersion, asymmetry and positive/negative tail probabilities occupy different dimensions. The mean absolute distance
over 129 quantile levels approximates the first Wasserstein distance. We report the same distances during the
largest 10% of realized absolute outcomes. That episode definition is diagnostic and was unavailable at forecast time.

The first eigenvalue and the participation ratio describe the historical correlation matrix. Shared realized outcomes
contribute mechanically to highly correlated errors. The probability, location and tail matrices show how few
distinct forecast directions remain after accounting for that limitation. Redundancy-aware forecast weights use
only matured earlier quantiles. The full-sample geometry never drives historical fit weights.

## Native 09:10 dimensionality

| horizon | coordinate | dates | experts | first share | effective rank |
| --- | --- | --- | --- | --- | --- |
| 5 | p | 265 | 16 | 0.631689 | 2.319315 |
| 5 | mean | 265 | 16 | 0.651428 | 2.205052 |
| 5 | log_scale | 265 | 16 | 0.892010 | 1.244330 |
| 5 | asymmetry | 265 | 16 | 0.636148 | 2.271296 |
| 5 | p_tail_down | 265 | 16 | 0.794018 | 1.539130 |
| 5 | p_tail_up | 265 | 16 | 0.640272 | 2.065385 |
| 5 | brier | 265 | 16 | 0.618082 | 2.368575 |
| 5 | crps | 265 | 16 | 0.922074 | 1.171419 |
| 5 | prediction_error | 265 | 16 | 0.950721 | 1.104626 |
| 21 | p | 217 | 15 | 0.577440 | 2.516931 |
| 21 | mean | 217 | 15 | 0.560600 | 2.641916 |
| 21 | log_scale | 217 | 15 | 0.683394 | 1.869545 |
| 21 | asymmetry | 217 | 15 | 0.628992 | 2.344009 |
| 21 | p_tail_down | 217 | 15 | 0.711986 | 1.860885 |
| 21 | p_tail_up | 217 | 15 | 0.579571 | 2.368455 |
| 21 | brier | 217 | 15 | 0.599030 | 2.359628 |
| 21 | crps | 217 | 15 | 0.954504 | 1.096649 |
| 21 | prediction_error | 217 | 15 | 0.969108 | 1.064212 |

## Pairwise relationships and differences in extreme episodes

| horizon | clock | pairs | near law pairs | affine probability pairs | mean pairwise return error corr | mean crps corr | mean wasserstein | extreme wasserstein |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | native_0910 | 120 | 0 | 0 | 0.947122 | 0.915819 | 0.005568 | 0.008589 |
| 5 | preauction_0855 | 351 | 1 | 1 | 0.946958 | 0.919357 | 0.005666 | 0.009097 |
| 5 | previous_1700 | 105 | 0 | 0 | 0.967761 | 0.957350 | 0.004065 | 0.006446 |
| 21 | native_0910 | 105 | 0 | 0 | 0.966790 | 0.951031 | 0.012739 | 0.011976 |
| 21 | preauction_0855 | 378 | 1 | 0 | 0.946162 | 0.882524 | 0.017095 | 0.013142 |
| 21 | previous_1700 | 105 | 0 | 0 | 0.973136 | 0.950706 | 0.009899 | 0.007140 |

The weekly corporate versus domestic and monthly positioning versus offshore diagnostic compares the cross-family pairs available at the same native clock.

| horizon | pairs | probability correlation | location correlation | return error correlation | crps loss correlation |
| --- | --- | --- | --- | --- | --- |
| 5 | 12 | 0.877770 | 0.900863 | 0.983770 | 0.978035 |
| 21 | 8 | 0.606146 | 0.433652 | 0.979909 | 0.972719 |

Exact-law hashes include atom locations and weights. Affine probability signatures do not prove that two experts share identical source features. The V10 and V11 controlled input aliases supply direct evidence where the feature provenance is known. In V10, adding three naive ridge copies moved probability by up to 0.061905, while the required canonical controls passed. The simulation audit separately measures variation from atom sampling.

| version | source | method | variant | tests | max law delta | max probability change | recognized aliases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | invariance-effects.csv | canonical_cluster | affine_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | invariance-effects.csv | canonical_cluster | as_is | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_cluster | equivalent_formula | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_cluster | equivalent_units | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_cluster | one_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | invariance-effects.csv | canonical_cluster | reordered | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_cluster | three_copies | 5 | 0.000000 | 0.000000 | 18 |
| 10 | invariance-effects.csv | canonical_elastic | affine_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | invariance-effects.csv | canonical_elastic | as_is | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_elastic | equivalent_formula | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_elastic | equivalent_units | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_elastic | one_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | invariance-effects.csv | canonical_elastic | reordered | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_elastic | three_copies | 5 | 0.000000 | 0.000000 | 18 |
| 10 | invariance-effects.csv | canonical_ridge | affine_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | invariance-effects.csv | canonical_ridge | as_is | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_ridge | equivalent_formula | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_ridge | equivalent_units | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_ridge | one_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | invariance-effects.csv | canonical_ridge | reordered | 5 | 0.000000 | 0.000000 | 0 |
| 10 | invariance-effects.csv | canonical_ridge | three_copies | 5 | 0.000000 | 0.000000 | 18 |
| 10 | invariance-effects.csv | ridge | three_copies | 5 | 0.123810 | 0.123810 | 0 |
| 10 | sector-alias-effects.csv | canonical_cluster | as_is | 5 | 0.000000 | 0.000000 | 0 |
| 10 | sector-alias-effects.csv | canonical_cluster | one_copy | 5 | 0.000000 | 0.000000 | 6 |
| 10 | sector-alias-effects.csv | canonical_cluster | three_copies | 5 | 0.000000 | 0.000000 | 18 |

[forecast-geometry-effective-rank.csv](forecast-geometry-effective-rank.csv) · [forecast-geometry-pairwise.csv.gz](forecast-geometry-pairwise.csv.gz) · [forecast-exact-case-duplicates.csv](forecast-exact-case-duplicates.csv) · [range-geometry-pairwise.csv](range-geometry-pairwise.csv) · [matched-expert-family-map.csv](matched-expert-family-map.csv) · [matched-expert-laws.npz](matched-expert-laws.npz) · [v10-archived-feature-alias-audit.csv](v10-archived-feature-alias-audit.csv) · [v11-archived-affine-and-sentinel-audit.csv](v11-archived-affine-and-sentinel-audit.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
