# V19 Delivery Participation Research

The 240 issuer seed was fixed from January 2025 turnover and included only after its dated anchor. The audited delivery panel uses each issuer's past-60 or past-25 observations, where the current observation is outside its normalization window. Activity includes changes in delivery share, delivered quantity, delivery-to-traded shares, concentration of the close-marked quantity value and persistence. Daily rollups include equal-company, represented-sector-equal and historical liquidity weights. We counted company outcomes on their common dates before pooling scores. The date count captures overlapping return windows, and the match uses identical shares for delivery and ordinary traded-volume regressions.

| horizon | state | stock dates | dates | mean market relative | mean absolute relative |
| --- | --- | --- | --- | --- | --- |
| 5 | up_high | 7,139 | 418 | -0.001899 | 0.030663 |
| 21 | up_high | 6,920 | 403 | -0.003110 | 0.064032 |
| 5 | up_low | 9,085 | 434 | -0.001787 | 0.033111 |
| 21 | up_low | 8,537 | 418 | -0.002882 | 0.068743 |
| 5 | down_high | 10,706 | 433 | -0.001217 | 0.032016 |
| 21 | down_high | 10,510 | 417 | -0.003734 | 0.069983 |
| 5 | down_low | 6,040 | 430 | -0.001353 | 0.031837 |
| 21 | down_low | 5,651 | 414 | -0.000052 | 0.067191 |
| 5 | consolidation_high | 4,976 | 424 | -0.000536 | 0.030699 |
| 21 | consolidation_high | 4,860 | 410 | -0.002715 | 0.064299 |
| 5 | volatile_high | 8,471 | 434 | -0.000976 | 0.036391 |
| 21 | volatile_high | 8,237 | 418 | -0.001164 | 0.079089 |
| 5 | ordinary_participation | 68,970 | 435 | -0.000425 | 0.030810 |
| 21 | ordinary_participation | 66,266 | 419 | -0.000668 | 0.065474 |

| target | model | dates | case units | rank corr | mae | rmse |
| --- | --- | --- | --- | --- | --- | --- |
| target21 | delivery_only | 349 | 81,462 | -0.006211 | 0.065508 | 0.092437 |
| target21 | price_volume | 349 | 81,462 | -0.042823 | 0.065872 | 0.092902 |
| target21 | price_volume_delivery | 349 | 81,462 | -0.029442 | 0.065835 | 0.092893 |
| target5 | delivery_only | 365 | 85,427 | 0.014511 | 0.029885 | 0.043874 |
| target5 | price_volume | 365 | 85,427 | -0.003185 | 0.029924 | 0.043912 |
| target5 | price_volume_delivery | 365 | 85,427 | 0.002997 | 0.029922 | 0.043915 |

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

Check the alternate 25-day feature, corporate-action and outlier sensitivity, removal of the top 15 seed stocks and both deterministic random halves in the endpoint comparison. Six price-and-delivery states are tracked, with independent consolidation/high-volatility screens. Quantity times the closing mark estimates delivery value for weighting purposes. Investor direction and new cash subscriptions are unobserved.

[stock-delivery-features.csv.gz](stock-delivery-features.csv.gz) · [stock-delivery-states.csv](stock-delivery-states.csv) · [stock-transfer-cases.csv.gz](stock-transfer-cases.csv.gz) · [sector-transfer-cases.csv.gz](sector-transfer-cases.csv.gz) · [transfer-fit-receipts.ndjson.gz](transfer-fit-receipts.ndjson.gz) · [endpoint-config.json](endpoint-config.json) · [matched-comparisons.csv](matched-comparisons.csv)
