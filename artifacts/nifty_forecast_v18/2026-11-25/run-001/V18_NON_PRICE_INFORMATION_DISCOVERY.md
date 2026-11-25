# NIFTY V18 — Non-price information discovery

V18 recovered the official dated security-delivery files and dated exchange reports of derivatives participant positioning, as well as historical bulk and block trade rows using a separate archival route. Earlier published cash histories extend issuer checks into the first months of 2025. Forecasts use a prior-day guard for these EOD files. The signed bulk-deal measure is a reported side proxy on a selection of disclosed trades. Timing is publication-guarded because the historical deal data identify trade dates. Derivatives participant categories, including FII and DII, refer to the corresponding positions in the published report. Cash FII/DII flows lacked a verified matching dated archive. Promoter transactions, shareholding changes and credit developments are inventoried from exchange metadata. A full point-in-time shareholding, credit rating level, or industry-activity panel remains unavailable.

| source | rows | days |
| --- | --- | --- |
| delivery-statistics.csv.gz | 109,980 | 466 |
| participant-open-interest.csv.gz | 1,532 | 383 |
| bulk-block-events.csv.gz | 2,970 | 151 |
| supplementary-equity-cash.csv.gz | 117,517 | 58 |

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | additional_nonprice | clock_structural | brier | 265 | 53 | 0.232338 | 0.238274 | 0.005936 | -0.014517 | 0.026389 |
| 5 | preauction_0855 | additional_nonprice | clock_structural | crps | 265 | 53 | 0.010352 | 0.010658 | 0.000307 | -0.000418 | 0.001031 |
| 5 | preauction_0855 | delivery_only | clock_structural | brier | 265 | 53 | 0.242313 | 0.238274 | -0.004038 | -0.014467 | 0.006390 |
| 5 | preauction_0855 | delivery_only | clock_structural | crps | 265 | 53 | 0.010780 | 0.010658 | -0.000122 | -0.000428 | 0.000184 |
| 5 | preauction_0855 | participant_positions | clock_structural | brier | 265 | 53 | 0.233299 | 0.238274 | 0.004976 | -0.009906 | 0.019858 |
| 5 | preauction_0855 | participant_positions | clock_structural | crps | 265 | 53 | 0.010389 | 0.010658 | 0.000269 | -0.000273 | 0.000811 |
| 5 | preauction_0855 | bulk_block_activity | clock_structural | brier | 265 | 53 | 0.241848 | 0.238274 | -0.003573 | -0.018561 | 0.011414 |
| 5 | preauction_0855 | bulk_block_activity | clock_structural | crps | 265 | 53 | 0.010742 | 0.010658 | -0.000084 | -0.000517 | 0.000349 |
| 5 | previous_1700 | additional_nonprice | clock_structural | brier | 265 | 53 | 0.233892 | 0.238605 | 0.004713 | -0.018726 | 0.028151 |
| 5 | previous_1700 | additional_nonprice | clock_structural | crps | 265 | 53 | 0.010431 | 0.010721 | 0.000290 | -0.000569 | 0.001150 |
| 5 | previous_1700 | delivery_only | clock_structural | brier | 265 | 53 | 0.244462 | 0.238605 | -0.005858 | -0.015899 | 0.004184 |
| 5 | previous_1700 | delivery_only | clock_structural | crps | 265 | 53 | 0.010848 | 0.010721 | -0.000126 | -0.000518 | 0.000265 |
| 5 | previous_1700 | participant_positions | clock_structural | brier | 265 | 53 | 0.233698 | 0.238605 | 0.004907 | -0.011103 | 0.020916 |
| 5 | previous_1700 | participant_positions | clock_structural | crps | 265 | 53 | 0.010491 | 0.010721 | 0.000230 | -0.000335 | 0.000795 |
| 5 | previous_1700 | bulk_block_activity | clock_structural | brier | 265 | 53 | 0.242130 | 0.238605 | -0.003526 | -0.021139 | 0.014087 |
| 5 | previous_1700 | bulk_block_activity | clock_structural | crps | 265 | 53 | 0.010812 | 0.010721 | -0.000091 | -0.000561 | 0.000380 |
| 21 | preauction_0855 | additional_nonprice | clock_structural | brier | 217 | 11 | 0.281552 | 0.302805 | 0.021253 | -0.046521 | 0.089028 |
| 21 | preauction_0855 | additional_nonprice | clock_structural | crps | 217 | 11 | 0.028746 | 0.028519 | -0.000226 | -0.004570 | 0.004117 |
| 21 | preauction_0855 | delivery_only | clock_structural | brier | 217 | 11 | 0.321335 | 0.302805 | -0.018530 | -0.038999 | 0.001940 |
| 21 | preauction_0855 | delivery_only | clock_structural | crps | 217 | 11 | 0.030307 | 0.028519 | -0.001787 | -0.003972 | 0.000397 |
| 21 | preauction_0855 | participant_positions | clock_structural | brier | 217 | 11 | 0.285467 | 0.302805 | 0.017338 | -0.054700 | 0.089377 |
| 21 | preauction_0855 | participant_positions | clock_structural | crps | 217 | 11 | 0.029112 | 0.028519 | -0.000592 | -0.004828 | 0.003643 |
| 21 | preauction_0855 | bulk_block_activity | clock_structural | brier | 217 | 11 | 0.324477 | 0.302805 | -0.021672 | -0.043561 | 0.000218 |
| 21 | preauction_0855 | bulk_block_activity | clock_structural | crps | 217 | 11 | 0.029899 | 0.028519 | -0.001380 | -0.002717 | -0.000043 |
| 21 | previous_1700 | additional_nonprice | clock_structural | brier | 217 | 11 | 0.288011 | 0.300452 | 0.012442 | -0.050446 | 0.075330 |
| 21 | previous_1700 | additional_nonprice | clock_structural | crps | 217 | 11 | 0.029099 | 0.028321 | -0.000778 | -0.004914 | 0.003357 |
| 21 | previous_1700 | delivery_only | clock_structural | brier | 217 | 11 | 0.320713 | 0.300452 | -0.020261 | -0.039993 | -0.000529 |
| 21 | previous_1700 | delivery_only | clock_structural | crps | 217 | 11 | 0.030303 | 0.028321 | -0.001983 | -0.004070 | 0.000105 |
| 21 | previous_1700 | participant_positions | clock_structural | brier | 217 | 11 | 0.289954 | 0.300452 | 0.010499 | -0.055910 | 0.076908 |
| 21 | previous_1700 | participant_positions | clock_structural | crps | 217 | 11 | 0.029209 | 0.028321 | -0.000889 | -0.004995 | 0.003218 |
| 21 | previous_1700 | bulk_block_activity | clock_structural | brier | 217 | 11 | 0.324991 | 0.300452 | -0.024539 | -0.047390 | -0.001687 |
| 21 | previous_1700 | bulk_block_activity | clock_structural | crps | 217 | 11 | 0.029799 | 0.028321 | -0.001479 | -0.002763 | -0.000194 |

[New daily source coverage and guards](non-price-receipt.json) · [Raw source and attempt hashes](non-price-sources.json) · [Official delivery report index](https://betanseapi.nseindia.com/all-reports) · [NSE archival market reports](https://betanseapi.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives) · [BLS CPI original publications](https://www.bls.gov/bls/news-release/cpi.htm)
