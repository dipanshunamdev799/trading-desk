# V19 Aggregate Positioning Factors

Eight market-state families cover levels, changes, cross-category disagreement, abnormal delivery intensity, delivery breadth, transaction activity, concentration and position-price residuals. Market indexes and narrower stock/sector outcomes are evaluated in different units. The rotation experiment compares contemporaneously classified stocks with official sector relative returns, NIFTY 50, equal-weight breadth and native financial rotation. Grouped company regressions use dated label availability. The January liquidity weights and known-sector baskets are observable proxies. Full point-in-time index weights and historical market-cap weighting for this issuer universe are unconfirmed.

| cutoff | open interest observed | traded volume observed | delivery observed | deals observed | futures observed |
| --- | --- | --- | --- | --- | --- |
| 09:25 | 399 | 400 | 399 | 400 | 398 |
| 10:20 | 399 | 400 | 399 | 400 | 398 |
| preauction_0855 | 401 | 402 | 401 | 402 | 400 |
| previous_1700 | 401 | 402 | 401 | 402 | 400 |

| target | model | dates | case units | rank corr | mae | rmse |
| --- | --- | --- | --- | --- | --- | --- |
| target21 | sector_all | 349 | 2,792 | -0.046391 | 0.030875 | 0.039344 |
| target21 | sector_plus_delivery | 349 | 2,792 | -0.040388 | 0.030875 | 0.039374 |
| target21 | sector_plus_positions | 349 | 2,792 | -0.056079 | 0.030715 | 0.039138 |
| target21 | sector_price_turnover | 349 | 2,792 | -0.051303 | 0.030702 | 0.039152 |
| target5 | sector_all | 365 | 2,920 | -0.006915 | 0.014038 | 0.017971 |
| target5 | sector_plus_delivery | 365 | 2,920 | -0.004110 | 0.014045 | 0.017978 |
| target5 | sector_plus_positions | 365 | 2,920 | -0.021592 | 0.014019 | 0.017944 |
| target5 | sector_price_turnover | 365 | 2,920 | -0.016504 | 0.014018 | 0.017951 |

| horizon | cutoff | model | n | crps | brier |
| --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | delivery_25_window | 265 | 0.010825 | 0.242737 |
| 5 | preauction_0855 | delivery_ex_actions | 265 | 0.010845 | 0.244363 |
| 5 | preauction_0855 | delivery_liquidity_weight | 265 | 0.010855 | 0.244925 |
| 5 | preauction_0855 | delivery_random_half0 | 265 | 0.010827 | 0.244233 |
| 5 | preauction_0855 | delivery_random_half1 | 265 | 0.010860 | 0.244492 |
| 5 | preauction_0855 | delivery_without_top_15 | 265 | 0.010843 | 0.244259 |
| 5 | preauction_0855 | position_with_compact_factors | 265 | 0.010660 | 0.245234 |
| 5 | previous_1700 | delivery_25_window | 265 | 0.010870 | 0.243656 |
| 5 | previous_1700 | delivery_ex_actions | 265 | 0.010884 | 0.244324 |
| 5 | previous_1700 | delivery_liquidity_weight | 265 | 0.010899 | 0.244393 |
| 5 | previous_1700 | delivery_random_half0 | 265 | 0.010866 | 0.243967 |
| 5 | previous_1700 | delivery_random_half1 | 265 | 0.010899 | 0.244503 |
| 5 | previous_1700 | delivery_without_top_15 | 265 | 0.010881 | 0.244324 |
| 5 | previous_1700 | position_with_compact_factors | 265 | 0.010732 | 0.243871 |
| 21 | preauction_0855 | delivery_25_window | 217 | 0.030412 | 0.331012 |
| 21 | preauction_0855 | delivery_ex_actions | 217 | 0.030595 | 0.332711 |
| 21 | preauction_0855 | delivery_liquidity_weight | 217 | 0.030618 | 0.332184 |
| 21 | preauction_0855 | delivery_random_half0 | 217 | 0.030553 | 0.331862 |
| 21 | preauction_0855 | delivery_random_half1 | 217 | 0.030625 | 0.332460 |
| 21 | preauction_0855 | delivery_without_top_15 | 217 | 0.030588 | 0.332597 |
| 21 | preauction_0855 | position_with_compact_factors | 217 | 0.028197 | 0.294498 |
| 21 | previous_1700 | delivery_25_window | 217 | 0.030337 | 0.330212 |
| 21 | previous_1700 | delivery_ex_actions | 217 | 0.030511 | 0.332223 |
| 21 | previous_1700 | delivery_liquidity_weight | 217 | 0.030538 | 0.333390 |

[feature-receipt.json](feature-receipt.json) · [asof-positioning-features.csv.gz](asof-positioning-features.csv.gz) · [sector-delivery-features.csv.gz](sector-delivery-features.csv.gz) · [sector-transfer-daily.csv](sector-transfer-daily.csv) · [endpoint-config.json](endpoint-config.json) · [matched-comparisons.csv](matched-comparisons.csv)
