# V22 India-specific domain adaptation

India-specific adaptation used identical 60- and 120-origin samples at each available Indian date. Each row is chosen by
exact maturity time and is already complete at forecast issue. Zero-centered, ordinary-strength and strong ridge fits
anchor the comparison. A historical India prior uses an older preceding window where 45 mature rows exist. The international
initialization uses standardized foreign coefficients mapped back to local feature units. The random prior uses the same
foreign samples with within-date country labels permuted. A foreign-only law, hierarchical partial pooling, the domestic
residual law, and complete-law mixtures supply separate designs.

India retains guarded corporate reactions, financial rotation, official equal-weight breadth, participant positions and
concentration, dated constituent weights and earlier constituent contribution forecasts, ATM IV and trailing realized
volatility. The compared foreign prior requires only comparable market covariates. Residual overlays also combine a
visible GIFT quote proxy and its opening-gap model. The 08:55 availability and the original issue-time cohort remain explicit.

| horizon | model | n | coverage | brier | crps | mae | rank corr | coverage80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | adapt_foreign_prior_120 | 265 | 1.000000 | 0.262467 | 0.011696 | 0.015910 | -0.114351 | 0.773585 |
| 5 | adapt_foreign_prior_60 | 265 | 1.000000 | 0.317882 | 0.012780 | 0.017262 | -0.121275 | 0.686792 |
| 5 | adapt_foreign_random_120 | 265 | 1.000000 | 0.262506 | 0.011710 | 0.015932 | -0.114175 | 0.773585 |
| 5 | adapt_foreign_random_60 | 265 | 1.000000 | 0.319098 | 0.012790 | 0.017285 | -0.122376 | 0.683019 |
| 5 | adapt_foreign_strong_120 | 265 | 1.000000 | 0.261003 | 0.011590 | 0.015643 | -0.129395 | 0.773585 |
| 5 | adapt_foreign_strong_60 | 265 | 1.000000 | 0.304858 | 0.012558 | 0.016931 | -0.130685 | 0.690566 |
| 5 | adapt_historical_prior_120 | 265 | 1.000000 | 0.271964 | 0.011830 | 0.015915 | -0.185298 | 0.769811 |
| 5 | adapt_historical_prior_60 | 265 | 1.000000 | 0.316423 | 0.012806 | 0.017378 | -0.160914 | 0.698113 |
| 5 | adapt_ordinary_ridge_120 | 265 | 1.000000 | 0.270094 | 0.011993 | 0.016515 | -0.100983 | 0.777358 |
| 5 | adapt_ordinary_ridge_60 | 265 | 1.000000 | 0.338157 | 0.013777 | 0.018513 | -0.051133 | 0.641509 |
| 5 | adapt_strong_zero_120 | 265 | 1.000000 | 0.258903 | 0.011490 | 0.015497 | -0.130932 | 0.777358 |
| 5 | adapt_strong_zero_60 | 265 | 1.000000 | 0.302094 | 0.012464 | 0.016798 | -0.138938 | 0.686792 |
| 5 | adapt_zero_centered_120 | 265 | 1.000000 | 0.261919 | 0.011627 | 0.015800 | -0.117368 | 0.773585 |
| 5 | adapt_zero_centered_60 | 265 | 1.000000 | 0.316040 | 0.012732 | 0.017196 | -0.117861 | 0.686792 |
| 21 | adapt_foreign_prior_120 | 217 | 1.000000 | 0.376173 | 0.037749 | 0.052099 | -0.301516 | 0.465438 |
| 21 | adapt_foreign_prior_60 | 217 | 1.000000 | 0.449847 | 0.042019 | 0.057201 | -0.234913 | 0.276498 |
| 21 | adapt_foreign_random_120 | 217 | 1.000000 | 0.377161 | 0.037859 | 0.052282 | -0.306826 | 0.451613 |
| 21 | adapt_foreign_random_60 | 217 | 1.000000 | 0.450697 | 0.042050 | 0.057260 | -0.236908 | 0.285714 |
| 21 | adapt_foreign_strong_120 | 217 | 1.000000 | 0.351000 | 0.033427 | 0.047019 | -0.282573 | 0.529954 |
| 21 | adapt_foreign_strong_60 | 217 | 1.000000 | 0.426191 | 0.039313 | 0.054170 | -0.233902 | 0.341014 |
| 21 | adapt_historical_prior_120 | 217 | 1.000000 | 0.372219 | 0.035759 | 0.049886 | -0.277503 | 0.502304 |
| 21 | adapt_historical_prior_60 | 217 | 1.000000 | 0.428429 | 0.041698 | 0.056407 | -0.156688 | 0.294931 |
| 21 | adapt_ordinary_ridge_120 | 217 | 1.000000 | 0.400268 | 0.042077 | 0.057072 | -0.344287 | 0.396313 |
| 21 | adapt_ordinary_ridge_60 | 217 | 1.000000 | 0.476882 | 0.045004 | 0.060574 | -0.226472 | 0.248848 |
| 21 | adapt_strong_zero_120 | 217 | 1.000000 | 0.345147 | 0.032518 | 0.045814 | -0.313393 | 0.552995 |
| 21 | adapt_strong_zero_60 | 217 | 1.000000 | 0.420411 | 0.038516 | 0.053303 | -0.231696 | 0.364055 |
| 21 | adapt_zero_centered_120 | 217 | 1.000000 | 0.372348 | 0.036991 | 0.051240 | -0.312439 | 0.470046 |
| 21 | adapt_zero_centered_60 | 217 | 1.000000 | 0.446524 | 0.041683 | 0.056854 | -0.236197 | 0.276498 |

The fixed-budget archive contains 6,748 fits. All the reported foreign prior training outcomes precede the Indian cutoff.

## Domestic versus international residual attribution

| horizon | model | n | active | brier | crps | mae | rmse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | parent_location_beyond_gift | 265 | 216 | 0.221891 | 0.010256 | 0.014487 | 0.020205 |
| 5 | parent_location_combined | 265 | 216 | 0.223278 | 0.010342 | 0.014565 | 0.020429 |
| 5 | parent_location_domestic_only | 265 | 216 | 0.222142 | 0.010121 | 0.014352 | 0.019939 |
| 5 | parent_location_international_only | 265 | 216 | 0.225689 | 0.010464 | 0.014665 | 0.020929 |
| 5 | parent_location_offshore_only | 265 | 216 | 0.220463 | 0.010128 | 0.014385 | 0.020129 |
| 5 | parent_mixture_foreign_tail | 265 | 265 | 0.223100 | 0.010272 | 0.014485 | 0.020155 |
| 5 | parent_mixture_transfer | 265 | 265 | 0.230589 | 0.010289 | 0.014591 | 0.020184 |
| 5 | secondary_location_beyond_gift | 265 | 216 | 0.220133 | 0.010180 | 0.014217 | 0.020337 |
| 5 | secondary_location_domestic_only | 265 | 216 | 0.220368 | 0.010130 | 0.014221 | 0.020263 |
| 21 | parent_location_beyond_gift | 217 | 152 | 0.234212 | 0.024745 | 0.031898 | 0.045371 |
| 21 | parent_location_combined | 217 | 152 | 0.234085 | 0.024726 | 0.031941 | 0.045316 |
| 21 | parent_location_domestic_only | 217 | 152 | 0.236029 | 0.024783 | 0.031875 | 0.045737 |
| 21 | parent_location_international_only | 217 | 152 | 0.239825 | 0.024961 | 0.032248 | 0.045574 |
| 21 | parent_location_offshore_only | 217 | 152 | 0.233300 | 0.024068 | 0.031148 | 0.044654 |
| 21 | parent_mixture_foreign_tail | 217 | 217 | 0.223431 | 0.023174 | 0.029781 | 0.043039 |
| 21 | parent_mixture_transfer | 217 | 217 | 0.241146 | 0.024251 | 0.031419 | 0.045023 |
| 21 | secondary_location_beyond_gift | 217 | 152 | 0.249111 | 0.025865 | 0.033685 | 0.046848 |
| 21 | secondary_location_domestic_only | 217 | 152 | 0.252020 | 0.025915 | 0.033748 | 0.047202 |

Compare foreign-prior rows directly with zero-centered and randomized-prior rows at the same budget. Compare a foreign residual overlay with an otherwise identical India-plus-offshore overlay before attributing a gain to geographic transfer.

[india-adaptation-fit-receipts.csv.gz](india-adaptation-fit-receipts.csv.gz) · [india-residual-fit-receipts.csv.gz](india-residual-fit-receipts.csv.gz) · [india-return-leaderboard.csv](india-return-leaderboard.csv) · [india-matched-comparisons.csv.gz](india-matched-comparisons.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
