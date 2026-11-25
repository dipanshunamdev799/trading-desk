# V20 Horizon Specialized Risk Models

The protected risk references retain their original populations and clocks. The source weekly raw ATM MAE is 0.037814, V16 offshore/domestic MAE 0.036469, monthly GJR MAE 0.033179 and variance QLIKE 0.199677. Weekly expansion Brier is 0.152707 for the fixed IV/realized-risk model and monthly expansion Brier is 0.172872 for Student EGARCH. The native Student-t GJR monthly range CRPS is 0.015422. The 08:55 GIFT-first weekly barrier Brier is 0.132201. V20 verified 1,928 same-clock path baselines with maximum score difference 0.

| horizon | cutoff | model | n | mae | qlike | brier |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 08:55 | GJR | 265 | 0.040318 | 0.359870 | 0.188310 |
| 5 | 08:55 | V14_IV_GJR | 265 | 0.037978 | 0.287184 | 0.165100 |
| 5 | 08:55 | fixed_iv_rv | 265 | 0.038484 | 0.286114 | 0.152707 |
| 5 | 08:55 | offshore_plus_domestic | 265 | 0.036469 | 0.290334 | 0.160327 |
| 5 | 08:55 | raw_iv | 265 | 0.037814 | 0.276187 | 0.155657 |
| 5 | 08:55 | student_EGARCH | 265 | 0.039960 | 0.327199 | 0.177866 |
| 21 | 08:55 | GJR | 217 | 0.033179 | 0.199677 | 0.198788 |
| 21 | 08:55 | V14_IV_GJR | 217 | 0.033780 | 0.247374 | 0.211163 |
| 21 | 08:55 | fixed_iv_rv | 217 | 0.040894 | 0.257953 | 0.194367 |
| 21 | 08:55 | offshore_plus_domestic | 217 | 0.049953 | 0.484730 | 0.207382 |
| 21 | 08:55 | raw_iv | 217 | 0.039406 | 0.267623 | 0.186036 |
| 21 | 08:55 | student_EGARCH | 217 | 0.035730 | 0.207684 | 0.172872 |

| horizon | model | n | active | mae | q like | brier | log loss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | fixed_iv_rv | 265 | 265 | 0.038484 | 0.286114 | 0.152707 | 0.461636 |
| 5 | fixed_iv_rv+risk_level | 265 | 223 | 0.038916 | 0.290789 | 0.152707 | 0.461636 |
| 5 | fixed_iv_rv+transition | 265 | 223 | 0.038484 | 0.286114 | 0.153782 | 0.462959 |
| 5 | offshore_plus_domestic | 265 | 265 | 0.036469 | 0.290334 | 0.160327 | 0.476147 |
| 5 | offshore_plus_domestic+risk_level | 265 | 223 | 0.037455 | 0.296965 | 0.160327 | 0.476147 |
| 5 | offshore_plus_domestic+transition | 265 | 223 | 0.036469 | 0.290334 | 0.162960 | 0.480432 |
| 21 | GJR | 217 | 217 | 0.033179 | 0.199677 | 0.198781 | 0.769605 |
| 21 | GJR+risk_level | 217 | 159 | 0.034431 | 0.191663 | 0.198781 | 0.769605 |
| 21 | GJR+transition | 217 | 159 | 0.033179 | 0.199677 | 0.195397 | 0.679825 |
| 21 | student_EGARCH | 217 | 217 | 0.035730 | 0.207684 | 0.172864 | 0.689982 |
| 21 | student_EGARCH+risk_level | 217 | 159 | 0.038311 | 0.215952 | 0.172864 | 0.689982 |
| 21 | student_EGARCH+transition | 217 | 159 | 0.035730 | 0.207684 | 0.170994 | 0.636613 |

V20 tested corporate location on weekly IV paths and positioning location on monthly GJR paths. Scale and asymmetry corrections have separately comparable scores. The coherent transform applies a monotone signed shape and positive scale around the cash reference, with a common shift to all four OHLC marks within each session. Variance, excursions, range and first-passage losses come from the same **256 cash paths**. Point and event-only forecasts remain separate.

| horizon | model | n | crps | range crps | vol mae | variance qlike | touch brier | integrated brier | expansion brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | asymmetric_specialized | 265 | 0.010670 | 0.005768 | 0.036793 | 0.281461 | 0.144418 | 0.120146 | 0.157989 |
| 5 | coherent_all | 265 | 0.010691 | 0.005862 | 0.037318 | 0.280297 | 0.144415 | 0.119738 | 0.160950 |
| 5 | location_specialized | 265 | 0.010667 | 0.005760 | 0.036803 | 0.280652 | 0.143873 | 0.119678 | 0.157837 |
| 5 | same_clock_GJR | 265 | 0.010922 | 0.006493 | 0.040097 | 0.410096 | 0.148396 | 0.122458 | 0.184671 |
| 5 | same_clock_IV | 265 | 0.010672 | 0.005768 | 0.036801 | 0.281463 | 0.144562 | 0.120331 | 0.157940 |
| 5 | scale_specialized | 265 | 0.010668 | 0.005868 | 0.037325 | 0.281163 | 0.144951 | 0.120451 | 0.160432 |
| 21 | asymmetric_specialized | 217 | 0.024545 | 0.015467 | 0.037397 | 0.302998 | 0.182813 | 0.160926 | 0.208439 |
| 21 | coherent_all | 217 | 0.024133 | 0.016012 | 0.038408 | 0.402569 | 0.185458 | 0.163978 | 0.217803 |
| 21 | location_specialized | 217 | 0.024014 | 0.015246 | 0.037172 | 0.299002 | 0.183315 | 0.161946 | 0.207248 |
| 21 | same_clock_GJR | 217 | 0.024694 | 0.015488 | 0.037244 | 0.300435 | 0.183861 | 0.161061 | 0.207983 |
| 21 | same_clock_IV | 217 | 0.025198 | 0.017179 | 0.040023 | 0.308248 | 0.184372 | 0.159680 | 0.203507 |
| 21 | scale_specialized | 217 | 0.024819 | 0.016231 | 0.038346 | 0.401471 | 0.185089 | 0.161881 | 0.217634 |

[protected-point-risk-cases.csv.gz](protected-point-risk-cases.csv.gz) · [protected-joint-benchmarks.csv](protected-joint-benchmarks.csv) · [position-and-corporate-risk-cases.csv.gz](position-and-corporate-risk-cases.csv.gz) · [coherent-risk-path-cases.csv.gz](coherent-risk-path-cases.csv.gz) · [coherent-path-law-recipes.csv.gz](coherent-path-law-recipes.csv.gz) · [risk-receipt.json](risk-receipt.json) · [matched-block-intervals.csv.gz](matched-block-intervals.csv.gz)
