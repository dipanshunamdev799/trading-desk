# V22 Global and country factor decomposition

Each local outcome includes total local log return, one global equity component, a regional-relative component and a remaining
local innovation. The economic decomposition uses two shrunken exposures from the last 116 eligible matched daily observations.
The common baskets exclude India and the evaluated market. Primary labels contribute once per market. ETF context cannot
multiply a common factor. Europe, North America and Asia Pacific pool by venue region. India’s regional comparison is Asia Pacific.

Realized international changes between the previous reference availability and the local target maturity are decomposition labels.
Forecast inputs use only earlier available closes. The PCA comparison fits on earlier foreign returns with a two-day completion
gap and is an explanatory context block. Strict leave-country and leave-region models use own-market state and FX only.

The first ex-India PCA component had median earlier-window variance share 41.14% and a median of 110 usable paired training dates.

| horizon | markets | distinct dates | global week episodes | observed returns | effective rank | first eigen share | mean pair corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 20 | 492 | 99 | 9,327 | 4.975153 | 0.402337 | 0.343599 |
| 5 | 20 | 488 | 98 | 9,219 | 3.489972 | 0.512714 | 0.466074 |
| 21 | 20 | 472 | 95 | 8,792 | 3.538367 | 0.502903 | 0.454377 |

| horizon | returns available | residual available | total variance | residual variance | residual variance ratio |
| --- | --- | --- | --- | --- | --- |
| 5 | 265 | 265 | 0.000416 | 0.000362 | 0.870599 |
| 21 | 217 | 217 | 0.001989 | 0.001684 | 0.846837 |

## Forward prediction of components

The table averages later held-time errors across foreign jurisdictions. Factor-only return prediction applies the lagged local
exposure to predicted foreign components. The companion arm adds a shrunken predicted country innovation.
GIFT and its opening-gap forecast are scored as controls in the Indian residual tests, so a fresh visible offshore move cannot
independently establish transferable country-specific alpha.

| horizon | model | global mae | innovation mae | brier | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | factor_and_innovation | 0.009897 | 0.015564 | 0.258256 | 0.014049 |
| 5 | factor_only | 0.009897 | 0.015564 | 0.257636 | 0.013976 |
| 5 | global_factor_only | 0.009394 | 0.016740 | 0.254492 | 0.014041 |
| 5 | local_history | 0.009196 | 0.016694 | 0.259971 | 0.014085 |
| 5 | loco_transfer | 0.009530 | 0.015492 | 0.255071 | 0.013310 |
| 5 | loro_transfer | 0.009705 | 0.015534 | 0.257939 | 0.013415 |
| 5 | pooled_with_context | 0.009897 | 0.015564 | 0.252321 | 0.013390 |
| 21 | factor_and_innovation | 0.029243 | 0.032266 | 0.289119 | 0.035105 |
| 21 | factor_only | 0.029243 | 0.032266 | 0.286747 | 0.034264 |
| 21 | global_factor_only | 0.022117 | 0.041515 | 0.299030 | 0.035878 |
| 21 | local_history | 0.022500 | 0.039877 | 0.308393 | 0.035113 |
| 21 | loco_transfer | 0.025472 | 0.032185 | 0.276787 | 0.029458 |
| 21 | loro_transfer | 0.025906 | 0.032886 | 0.285418 | 0.030322 |
| 21 | pooled_with_context | 0.029243 | 0.032266 | 0.282927 | 0.030924 |

[global-pca-receipts.csv](global-pca-receipts.csv) · [global-pca-loadings.csv](global-pca-loadings.csv) · [international-return-correlations-1.csv](international-return-correlations-1.csv) · [international-return-correlations-5.csv](international-return-correlations-5.csv) · [international-return-correlations-21.csv](international-return-correlations-21.csv) · [international-model-leaderboard.csv](international-model-leaderboard.csv) · [india-matched-comparisons.csv.gz](india-matched-comparisons.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
