# V20 Predictive Information Lifetimes

The central experiment tested **18 source families**, **two clocks** and **seven input vintages**. Cumulative close-to-close targets were 1, 2, 3, 5, 7, 10, 15 and 21 sessions. Separate returns cover session one, sessions 2–3, 4–5, 6–10, 11–15 and 16–21. The 6–21 target directly takes the first week out of the 21-session move. Annualized realized risk is scored separately at all eight cumulative horizons. All years are research-exposed, including these intermediate endpoints.

The general lifetime parent is a chronological cash-price and risk model with a complete empirical law. Each enhanced model adds a shrunk fitted slope from the new family, trained on earlier forecast errors. Fresh, lags of 1, 3, 5, 10 and 21 cash sessions, and causal five-session smoothing use the same training policy. Comparisons use the matched parent on dates when the candidate could run. The full population uses the parent wherever training or observations are missing. The machine matrix preserves the common 21-session origin subset for shape comparisons across horizons. Absolute and relative gains, matched and non-overlapping counts, earlier/later gains, and an identical-date five-session-shift comparison are included for every eligible cell.

## Fresh cumulative return CRPS gains at 08:55

| family | gain 1 | gain 5 | gain 21 |
| --- | --- | --- | --- |
| atm_iv | -0.000035 | -0.000197 | -0.001851 |
| corporate_announcements | -0.000017 | -0.000123 | -0.000666 |
| delivery | -5.76e-06 | -0.000065 | -0.000644 |
| domestic_internals | -0.000012 | 0.000052 | -0.000705 |
| equal_weight_breadth | 0.000012 | 0.000112 | -0.000591 |
| financial_rotation | 6.78e-06 | 0.000064 | -0.000822 |
| global_equities | 0.000067 | -0.000080 | -0.000042 |
| institutional_flows | 6.02e-06 | 0.000133 | 0.000075 |
| intraday_structure | -0.000018 | -0.000078 | -0.000065 |
| large_transactions | -0.000028 | -0.000153 | -0.000589 |
| offshore_gift | 0.000479 | 0.000173 | 0.000054 |
| option_surface | -0.000030 | -0.000034 | -0.000984 |
| participant_futures | 0.000028 | 0.000272 | 0.000645 |
| participant_options | -0.000022 | -0.000051 | 0.001240 |
| participant_volume | 3.39e-06 | 4.27e-06 | -0.000382 |
| realized_volatility | -0.000046 | -0.000223 | -0.002454 |
| stock_participation | -0.000040 | -0.000096 | -0.000743 |
| structured_financials | -0.000014 | -0.000118 | -0.001104 |

## Fresh later cash-session components at 08:55

| family | 2–3 | 4–5 | 6–10 | 11–15 | 16–21 | 6–21 |
| --- | --- | --- | --- | --- | --- | --- |
| corporate_announcements | -0.000020 | -0.000089 | -0.000207 | -0.000030 | -0.000049 | -0.000305 |
| financial_rotation | 0.000023 | -4.74e-06 | -0.000146 | -0.000247 | -0.000318 | -0.000839 |
| offshore_gift | -0.000011 | -0.000018 | -9.85e-06 | -0.000019 | 0.000010 | 0.000100 |
| participant_futures | 0.000137 | 0.000020 | -0.000154 | -0.000175 | 0.000157 | -9.86e-06 |

The 6–21 component answers whether a source conveys timing information after the first week under this specific model. An apparent 21-session improvement can come entirely from earlier returns. These statistical shapes are descriptions of this historical sample.

| family | end offset | matched | disjoint | parent | enhanced | gain | earlier gain | later gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| participant_options | 21 | 217 | 14 | 0.026969 | 0.026381 | 0.000587 | 0.000461 | 0.000822 | -0.001611 | 0.002785 |
| offshore_gift | 21 | 212 | 14 | 0.027349 | 0.027249 | 0.000100 | 0.000154 | -1.24e-06 | -0.000136 | 0.000336 |
| participant_futures | 21 | 217 | 14 | 0.026969 | 0.026978 | -9.86e-06 | -0.000047 | 0.000058 | -0.002805 | 0.002786 |
| intraday_structure | 21 | 217 | 14 | 0.026969 | 0.027024 | -0.000055 | -0.000065 | -0.000037 | -0.000334 | 0.000223 |
| global_equities | 21 | 217 | 14 | 0.026969 | 0.027027 | -0.000059 | -0.000165 | 0.000139 | -0.000444 | 0.000326 |
| equal_weight_breadth | 21 | 217 | 14 | 0.026969 | 0.027265 | -0.000297 | -0.000373 | -0.000154 | -0.001437 | 0.000843 |
| corporate_announcements | 21 | 217 | 14 | 0.026969 | 0.027274 | -0.000305 | -0.001266 | 0.001478 | -0.003021 | 0.002410 |
| institutional_flows | 21 | 168 | 11 | 0.029776 | 0.030111 | -0.000335 | -0.001266 | 0.000791 | -0.002450 | 0.001779 |
| participant_volume | 21 | 217 | 14 | 0.026969 | 0.027336 | -0.000368 | -0.000454 | -0.000208 | -0.001068 | 0.000333 |
| large_transactions | 21 | 217 | 14 | 0.026969 | 0.027351 | -0.000383 | -0.000542 | -0.000087 | -0.001044 | 0.000278 |
| delivery | 21 | 216 | 14 | 0.027001 | 0.027473 | -0.000472 | -0.000575 | -0.000277 | -0.001063 | 0.000120 |
| stock_participation | 21 | 217 | 14 | 0.026969 | 0.027507 | -0.000539 | -0.000692 | -0.000254 | -0.001447 | 0.000370 |
| option_surface | 21 | 217 | 14 | 0.026969 | 0.027726 | -0.000758 | -0.001456 | 0.000538 | -0.003141 | 0.001625 |
| financial_rotation | 21 | 217 | 14 | 0.026969 | 0.027808 | -0.000839 | 0.000127 | -0.002631 | -0.003188 | 0.001509 |
| domestic_internals | 21 | 217 | 14 | 0.026969 | 0.027812 | -0.000843 | -0.001573 | 0.000511 | -0.002108 | 0.000421 |
| structured_financials | 21 | 217 | 14 | 0.026969 | 0.028048 | -0.001080 | -0.001280 | -0.000708 | -0.005915 | 0.003755 |
| atm_iv | 21 | 217 | 14 | 0.026969 | 0.028578 | -0.001610 | -0.002578 | 0.000186 | -0.005263 | 0.002043 |
| realized_volatility | 21 | 217 | 14 | 0.026969 | 0.028835 | -0.001866 | -0.003647 | 0.001437 | -0.006277 | 0.002545 |

## Age of information and realized-risk gains

| family | fresh | lag1 | lag3 | lag5 | lag10 | lag21 | smooth5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| atm_iv | -0.001851 | -0.001928 | -0.002029 | -0.002163 | -0.001484 | -0.000223 | -0.002168 |
| corporate_announcements | -0.000666 | -0.000609 | -0.000391 | -0.000271 | -0.000136 | 0.000133 | -0.000798 |
| financial_rotation | -0.000822 | -0.000843 | -0.000872 | -0.000927 | -0.000439 | -0.000396 | -0.000928 |
| offshore_gift | 0.000054 | 0.000054 | 0.000095 | 0.000054 | 0.000038 | 6.20e-06 | 0.000169 |
| participant_futures | 0.000645 | 0.000568 | 0.000570 | 0.000773 | 0.000721 | -0.002654 | 0.000572 |

| family | end offset | matched | gain | earlier gain | later gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| atm_iv | 1 | 265 | 0.229888 | 0.395275 | -0.081110 | -0.186196 | 0.645972 |
| option_surface | 1 | 265 | 0.159860 | 0.290730 | -0.086233 | -0.176004 | 0.495724 |
| realized_volatility | 1 | 265 | 0.090981 | 0.141912 | -0.004792 | -0.229991 | 0.411952 |
| stock_participation | 1 | 265 | 0.071555 | 0.135325 | -0.048360 | -0.164161 | 0.307272 |
| participant_options | 5 | 265 | 0.056674 | 0.070801 | 0.030110 | -0.019766 | 0.133115 |
| atm_iv | 5 | 265 | 0.052401 | 0.073470 | 0.012782 | -0.036426 | 0.141227 |
| structured_financials | 5 | 265 | 0.044672 | 0.082247 | -0.025985 | -0.045698 | 0.135042 |
| option_surface | 5 | 265 | 0.040988 | 0.052825 | 0.018729 | -0.054218 | 0.136194 |
| delivery | 21 | 216 | 0.054728 | 0.062479 | 0.040157 | -0.031111 | 0.140568 |
| structured_financials | 21 | 217 | 0.047396 | 0.066178 | 0.012550 | -0.117297 | 0.212088 |
| financial_rotation | 21 | 217 | 0.042421 | 0.060262 | 0.009321 | -0.071873 | 0.156715 |
| domestic_internals | 21 | 217 | 0.036425 | 0.041924 | 0.026224 | -0.058249 | 0.131100 |

## Gains with positive adjusted lower bounds

Fresh GIFT at 08:55 reduced first-session CRPS from **0.004978 to 0.004499** across **256** matched sessions. Its cumulative advantage remained visible through three sessions. The later isolated component comparisons have weaker evidence. The three-session-aged CDSL and AMFI flow group reduced monthly Brier from **0.324643 to 0.307288** on **165** cases spanning **8** disjoint windows. A neutral 50% forecast scores **0.250000** on those same dates. The flow group holds eligible custody, fortnightly and mutual-fund reports across cash days. Its results depend on modeled publication lags and relatively few distinct report vintages.

| cutoff | family | age | mode | end offset | metric | matched | disjoint | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| previous_1700 | institutional_flows | lag3 | cumulative | 21 | brier | 163 | 8 | 0.014847 | 0.003533 | 0.026160 |
| previous_1700 | delivery | lag5 | risk | 2 | crps | 264 | 132 | 0.001313 | 0.000020 | 0.002605 |
| previous_1700 | realized_volatility | lag3 | risk | 2 | crps | 265 | 133 | 0.002368 | 0.000018 | 0.004718 |
| previous_1700 | delivery | lag5 | risk | 3 | crps | 264 | 89 | 0.001504 | 0.000144 | 0.002863 |
| previous_1700 | stock_participation | lag5 | risk | 5 | crps | 265 | 53 | 0.001097 | 0.000062 | 0.002133 |
| previous_1700 | delivery | lag3 | risk | 5 | crps | 264 | 53 | 0.001504 | 0.000040 | 0.002968 |
| preauction_0855 | offshore_gift | fresh | cumulative | 1 | brier | 256 | 256 | 0.031635 | 0.014556 | 0.048715 |
| preauction_0855 | offshore_gift | fresh | cumulative | 1 | crps | 256 | 256 | 0.000479 | 0.000232 | 0.000725 |
| preauction_0855 | offshore_gift | fresh | cumulative | 2 | brier | 256 | 130 | 0.014156 | 0.004704 | 0.023609 |
| preauction_0855 | offshore_gift | fresh | cumulative | 2 | crps | 256 | 130 | 0.000314 | 0.000124 | 0.000503 |
| preauction_0855 | offshore_gift | fresh | cumulative | 3 | brier | 256 | 88 | 0.009481 | 0.000380 | 0.018583 |
| preauction_0855 | offshore_gift | fresh | cumulative | 3 | crps | 256 | 88 | 0.000295 | 0.000087 | 0.000502 |
| preauction_0855 | institutional_flows | lag3 | cumulative | 21 | brier | 165 | 8 | 0.017355 | 0.000037 | 0.034673 |
| preauction_0855 | institutional_flows | lag5 | cumulative | 21 | brier | 163 | 8 | 0.010148 | 0.003336 | 0.016960 |
| preauction_0855 | realized_volatility | lag5 | risk | 2 | qlike | 265 | 133 | 0.120100 | 0.000555 | 0.239645 |
| preauction_0855 | delivery | lag1 | risk | 7 | crps | 216 | 31 | 0.001650 | 0.000013 | 0.003287 |
| preauction_0855 | delivery | lag10 | risk | 7 | crps | 216 | 31 | 0.001421 | 6.28e-06 | 0.002835 |

These bands account for family and age selection within each clock, metric and target. The reported gains share historical observations across clocks and horizons. Delivery and realized-risk associations use the general lifetime parent. The protected IV/GJR risk models have their own comparisons.

The archives contain 1,324,008 case comparisons. They store each parent’s sorted atoms plus the model’s shift, making every complete candidate law directly reconstructible. For each clock, target and metric, 600 circular date-block draws adjust for the declared search over sources and ages.

[information-lifetime-matrix.csv](information-lifetime-matrix.csv) · [lifetime-cases.csv.gz](lifetime-cases.csv.gz) · [lifetime-law-index.csv](lifetime-law-index.csv) · [lifetime-parent-laws.npz](lifetime-parent-laws.npz) · [lifetime-fresh-fit-examples.ndjson.gz](lifetime-fresh-fit-examples.ndjson.gz) · [opening-and-late-associations.csv](opening-and-late-associations.csv) · [information-lifetime-heatmap.png](information-lifetime-heatmap.png)
