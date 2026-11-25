# NIFTY V18 — Event-driven transfer learning

The transfer experiment forecast stock excess returns at **one, five and 21 sessions** from the first eligible full open and the next open after the reaction. It compares the price-only model, a price model with added nonlinear terms, a company-specific correction without sharing event effects, pooled business and event-category inputs, a sector-specific fit, and a regularized hierarchical sector and issuer correction. Matched non-event stock responses supply a separate training reference. The event-permutation control draws labels from completed earlier months, and the lagged control uses the prior issuer event. Fitting uses earlier fully resolved dates and never treats multiple firms releasing on one date as distinct index outcomes. MAE gains are paired and clustered by date and issuer, with distinct episodes recorded. Sector and issuer cells with few earlier observations shrink toward the pooled or simpler fit.

| horizon | stage | model | n | different dates | issuers | episodes | mae | rmse | accuracy | rank correlation | mean | low | high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | after_reaction | company_only_adjustment | 2,915 | 367 | 88 | 2,915 | 0.012045 | 0.016734 | 0.499828 | -0.021135 | -0.000053 | -0.000092 | -0.000014 |
| 1 | after_reaction | matched_non_event_model | 2,915 | 367 | 88 | 2,915 | 0.011930 | 0.016624 | 0.510120 | -0.029633 | 0.000062 | 9.19e-06 | 0.000115 |
| 1 | after_reaction | ordinary_pooled | 2,915 | 367 | 88 | 2,915 | 0.012112 | 0.016776 | 0.518696 | 0.003739 | -0.000120 | -0.000205 | -0.000035 |
| 1 | after_reaction | price_equivalent_complexity | 2,915 | 367 | 88 | 2,915 | 0.012004 | 0.016657 | 0.514237 | 0.014054 | -0.000012 | -0.000060 | 0.000036 |
| 1 | after_reaction | price_only | 2,915 | 367 | 88 | 2,915 | 0.011992 | 0.016675 | 0.518353 | -0.027399 | 0.000000 | 0.000000 | 0.000000 |
| 1 | after_reaction | prior_issuer_event | 2,915 | 367 | 88 | 2,915 | 0.012076 | 0.016767 | 0.504631 | -0.003379 | -0.000084 | -0.000159 | -8.14e-06 |
| 1 | after_reaction | randomized_category | 2,915 | 367 | 88 | 2,915 | 0.012059 | 0.016796 | 0.510120 | -0.014883 | -0.000067 | -0.000127 | -6.03e-06 |
| 1 | after_reaction | sector_issuer_partial_pool | 2,915 | 367 | 88 | 2,915 | 0.012170 | 0.016838 | 0.511492 | 0.000772 | -0.000178 | -0.000270 | -0.000086 |
| 1 | after_reaction | sector_specific | 2,915 | 367 | 88 | 2,915 | 0.012104 | 0.016755 | 0.504974 | -0.006017 | -0.000112 | -0.000192 | -0.000031 |
| 1 | first_open | company_only_adjustment | 2,909 | 366 | 88 | 2,909 | 0.013466 | 0.019141 | 0.511860 | -0.004183 | -0.000039 | -0.000084 | 6.00e-06 |
| 1 | first_open | matched_non_event_model | 2,909 | 366 | 88 | 2,909 | 0.013453 | 0.019125 | 0.515641 | 0.011930 | -0.000026 | -0.000104 | 0.000052 |
| 1 | first_open | ordinary_pooled | 2,909 | 366 | 88 | 2,909 | 0.013499 | 0.019187 | 0.507735 | -0.021356 | -0.000072 | -0.000117 | -0.000026 |
| 1 | first_open | price_equivalent_complexity | 2,909 | 366 | 88 | 2,909 | 0.013445 | 0.019128 | 0.524235 | -0.013918 | -0.000018 | -0.000064 | 0.000028 |
| 1 | first_open | price_only | 2,909 | 366 | 88 | 2,909 | 0.013427 | 0.019107 | 0.528360 | -0.012862 | 0.000000 | 0.000000 | 0.000000 |
| 1 | first_open | prior_issuer_event | 2,909 | 366 | 88 | 2,909 | 0.013516 | 0.019175 | 0.521829 | -0.017542 | -0.000089 | -0.000153 | -0.000026 |
| 1 | first_open | randomized_category | 2,909 | 366 | 88 | 2,909 | 0.013511 | 0.019205 | 0.518735 | 0.001027 | -0.000084 | -0.000149 | -0.000019 |
| 1 | first_open | sector_issuer_partial_pool | 2,909 | 366 | 88 | 2,909 | 0.013541 | 0.019243 | 0.523204 | -0.013867 | -0.000114 | -0.000186 | -0.000042 |
| 1 | first_open | sector_specific | 2,909 | 366 | 88 | 2,909 | 0.013532 | 0.019222 | 0.516672 | -0.020026 | -0.000105 | -0.000176 | -0.000034 |
| 5 | after_reaction | company_only_adjustment | 2,873 | 359 | 88 | 2,873 | 0.026738 | 0.036413 | 0.504003 | -0.012578 | -0.000151 | -0.000236 | -0.000065 |
| 5 | after_reaction | matched_non_event_model | 2,873 | 359 | 88 | 2,873 | 0.026481 | 0.036093 | 0.516185 | 0.017642 | 0.000107 | -0.000045 | 0.000258 |
| 5 | after_reaction | ordinary_pooled | 2,873 | 359 | 88 | 2,873 | 0.026812 | 0.036525 | 0.509224 | -0.014013 | -0.000224 | -0.000365 | -0.000083 |
| 5 | after_reaction | price_equivalent_complexity | 2,873 | 359 | 88 | 2,873 | 0.026711 | 0.036375 | 0.510964 | 0.002491 | -0.000123 | -0.000266 | 0.000020 |
| 5 | after_reaction | price_only | 2,873 | 359 | 88 | 2,873 | 0.026588 | 0.036249 | 0.505743 | -0.005523 | 0.000000 | 0.000000 | 0.000000 |
| 5 | after_reaction | prior_issuer_event | 2,873 | 359 | 88 | 2,873 | 0.026732 | 0.036433 | 0.510616 | -0.004278 | -0.000144 | -0.000258 | -0.000030 |
| 5 | after_reaction | randomized_category | 2,873 | 359 | 88 | 2,873 | 0.026759 | 0.036471 | 0.508876 | -0.007070 | -0.000172 | -0.000300 | -0.000044 |
| 5 | after_reaction | sector_issuer_partial_pool | 2,873 | 359 | 88 | 2,873 | 0.026966 | 0.036674 | 0.495301 | -0.025588 | -0.000379 | -0.000546 | -0.000211 |
| 5 | after_reaction | sector_specific | 2,873 | 359 | 88 | 2,873 | 0.026815 | 0.036447 | 0.503307 | -0.014614 | -0.000227 | -0.000387 | -0.000067 |
| 5 | first_open | company_only_adjustment | 2,867 | 359 | 88 | 2,867 | 0.028225 | 0.038815 | 0.508894 | -0.008460 | -0.000184 | -0.000307 | -0.000062 |
| 5 | first_open | matched_non_event_model | 2,867 | 359 | 88 | 2,867 | 0.028069 | 0.038594 | 0.502965 | 0.006998 | -0.000028 | -0.000226 | 0.000170 |
| 5 | first_open | ordinary_pooled | 2,867 | 359 | 88 | 2,867 | 0.028222 | 0.038915 | 0.512033 | -0.019865 | -0.000181 | -0.000323 | -0.000039 |
| 5 | first_open | price_equivalent_complexity | 2,867 | 359 | 88 | 2,867 | 0.028154 | 0.038718 | 0.520056 | -0.003670 | -0.000113 | -0.000203 | -0.000023 |
| 5 | first_open | price_only | 2,867 | 359 | 88 | 2,867 | 0.028041 | 0.038632 | 0.518661 | 0.002717 | 0.000000 | 0.000000 | 0.000000 |
| 5 | first_open | prior_issuer_event | 2,867 | 359 | 88 | 2,867 | 0.028286 | 0.038846 | 0.513777 | -0.021733 | -0.000245 | -0.000364 | -0.000126 |
| 5 | first_open | randomized_category | 2,867 | 359 | 88 | 2,867 | 0.028280 | 0.038809 | 0.519358 | 0.013197 | -0.000239 | -0.000374 | -0.000103 |
| 5 | first_open | sector_issuer_partial_pool | 2,867 | 359 | 88 | 2,867 | 0.028411 | 0.039089 | 0.509941 | -0.023800 | -0.000370 | -0.000580 | -0.000160 |
| 5 | first_open | sector_specific | 2,867 | 359 | 88 | 2,867 | 0.028274 | 0.038862 | 0.505406 | -0.023309 | -0.000233 | -0.000426 | -0.000040 |
| 21 | after_reaction | company_only_adjustment | 2,610 | 327 | 88 | 2,610 | 0.058222 | 0.079728 | 0.496169 | -0.017381 | -0.000422 | -0.000916 | 0.000071 |
| 21 | after_reaction | matched_non_event_model | 2,610 | 327 | 88 | 2,610 | 0.057111 | 0.078002 | 0.511494 | 0.044458 | 0.000689 | 0.000177 | 0.001201 |
| 21 | after_reaction | ordinary_pooled | 2,610 | 327 | 88 | 2,610 | 0.058342 | 0.079386 | 0.504215 | -0.001688 | -0.000542 | -0.000924 | -0.000160 |
| 21 | after_reaction | price_equivalent_complexity | 2,610 | 327 | 88 | 2,610 | 0.058301 | 0.079293 | 0.494253 | -0.004618 | -0.000501 | -0.000880 | -0.000121 |
| 21 | after_reaction | price_only | 2,610 | 327 | 88 | 2,610 | 0.057800 | 0.078955 | 0.501533 | -0.004164 | 0.000000 | 0.000000 | 0.000000 |
| 21 | after_reaction | prior_issuer_event | 2,610 | 327 | 88 | 2,610 | 0.058162 | 0.079273 | 0.502682 | -0.010811 | -0.000362 | -0.000676 | -0.000048 |
| 21 | after_reaction | randomized_category | 2,610 | 327 | 88 | 2,610 | 0.058249 | 0.079360 | 0.508046 | -0.007106 | -0.000449 | -0.000791 | -0.000107 |
| 21 | after_reaction | sector_issuer_partial_pool | 2,610 | 327 | 88 | 2,610 | 0.058880 | 0.080254 | 0.483908 | -0.006618 | -0.001080 | -0.001660 | -0.000500 |
| 21 | after_reaction | sector_specific | 2,610 | 327 | 88 | 2,610 | 0.058269 | 0.079539 | 0.486207 | -0.009348 | -0.000469 | -0.001087 | 0.000150 |
| 21 | first_open | company_only_adjustment | 2,610 | 327 | 88 | 2,610 | 0.059150 | 0.079921 | 0.490421 | -0.026957 | -0.000565 | -0.000988 | -0.000142 |
| 21 | first_open | matched_non_event_model | 2,610 | 327 | 88 | 2,610 | 0.058009 | 0.078102 | 0.517241 | 0.068027 | 0.000577 | 0.000080 | 0.001073 |
| 21 | first_open | ordinary_pooled | 2,610 | 327 | 88 | 2,610 | 0.058972 | 0.079323 | 0.499234 | 0.003094 | -0.000387 | -0.000714 | -0.000059 |
| 21 | first_open | price_equivalent_complexity | 2,610 | 327 | 88 | 2,610 | 0.058865 | 0.079150 | 0.486207 | -0.005598 | -0.000280 | -0.000579 | 0.000019 |
| 21 | first_open | price_only | 2,610 | 327 | 88 | 2,610 | 0.058585 | 0.079044 | 0.493870 | -0.007002 | 0.000000 | 0.000000 | 0.000000 |
| 21 | first_open | prior_issuer_event | 2,610 | 327 | 88 | 2,610 | 0.058954 | 0.079301 | 0.501916 | -0.000508 | -0.000369 | -0.000708 | -0.000030 |
| 21 | first_open | randomized_category | 2,610 | 327 | 88 | 2,610 | 0.058756 | 0.079075 | 0.503065 | 0.020567 | -0.000171 | -0.000561 | 0.000219 |
| 21 | first_open | sector_issuer_partial_pool | 2,610 | 327 | 88 | 2,610 | 0.059613 | 0.080256 | 0.480077 | -0.012822 | -0.001028 | -0.001518 | -0.000538 |
| 21 | first_open | sector_specific | 2,610 | 327 | 88 | 2,610 | 0.059124 | 0.079513 | 0.474713 | -0.018571 | -0.000539 | -0.001048 | -0.000029 |

[All event-transfer results](event-transfer-comparison.csv) · [Case predictions and training end dates](stock-transfer-predictions.csv.gz) · [Pooled event coefficients and transforms](stock-transfer-fit-receipts.json) · [Matched security controls](stock-event-pairs.csv.gz)
