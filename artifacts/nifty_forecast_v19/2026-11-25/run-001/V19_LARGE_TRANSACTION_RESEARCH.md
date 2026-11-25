# V19 Large Transaction Research

V19 retained all 46 official archive windows across 23 months. The 2,970 reported legs reduce to 2,969 unique disclosed legs after exact duplicate removal. There are 2,593 date, issuer, category, size and price groups on 151 dates. Equal-size, equal-price opposite block legs contribute 252 potential same-transfer pairs. The corresponding proxy totals ₹201,874.6 crore versus ₹231,962.6 crore from retained leg sums. Bulk legs retain their original sides. Disclosed side describes the reported transaction leg. Equal-sized verification and a published buyer/seller match do not resolve undisclosed counterparties or economic ownership.

Same-date comparison peers have high turnover, no deal records in the verified archive on that date, matched industry where known, and similar price and turnover characteristics. Matched issuer follow-through and absolute excess are date-weighted. Premium and discount use the last known previous close. Nine event dates have missing premium and turnover ratios because their quotes lacked direct cash references. The lagged size cap removes unusually large events. Endpoint comparisons also use shifted activity and the alternative all-leg sum.

| horizon | category | subset | events | dates | excess return | absolute excess | signed premium rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | block | all | 40 | 22 | 0.007225 | 0.000060 | -0.016482 |
| 5 | block | no_large | 14 | 10 | 0.000637 | -0.003917 | -0.186678 |
| 5 | block | recurrent | 25 | 19 | 0.013371 | 0.003941 | 0.035970 |
| 5 | block | premium | 6 | 5 | -0.009328 | -0.007662 | 0.542857 |
| 5 | block | discount | 18 | 13 | 0.005409 | 0.003690 | 0.296182 |
| 5 | bulk | all | 3 | 3 | -0.027592 | 0.008522 | — |
| 5 | bulk | no_large | 0 | 0 | — | — | — |
| 5 | bulk | recurrent | 2 | 2 | -0.047133 | 0.016881 | — |
| 5 | bulk | premium | 3 | 3 | -0.027592 | 0.008522 | — |
| 5 | bulk | discount | 0 | 0 | — | — | — |
| 21 | block | all | 39 | 21 | 0.024997 | -0.000603 | 0.047410 |
| 21 | block | no_large | 13 | 9 | 0.013735 | -0.010296 | -0.403321 |
| 21 | block | recurrent | 24 | 18 | 0.030013 | 0.001420 | 0.084603 |
| 21 | block | premium | 6 | 5 | 0.005234 | -0.004331 | 0.314286 |
| 21 | block | discount | 17 | 12 | 0.022903 | 0.012830 | 0.174020 |
| 21 | bulk | all | 3 | 3 | -0.073240 | 0.007024 | — |
| 21 | bulk | no_large | 0 | 0 | — | — | — |
| 21 | bulk | recurrent | 2 | 2 | -0.092530 | 0.008600 | — |
| 21 | bulk | premium | 3 | 3 | -0.073240 | 0.007024 | — |
| 21 | bulk | discount | 0 | 0 | — | — | — |

| horizon | model | n | active | brier | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | deals_all_reported_legs | 265 | 265 | 0.246702 | 0.010942 |
| 5 | deals_beyond_turnover | 265 | 223 | 0.254543 | 0.011135 |
| 5 | deals_date_shift | 265 | 265 | 0.244882 | 0.010851 |
| 5 | deals_without_largest | 265 | 265 | 0.246916 | 0.010944 |
| 5 | transactions | 265 | 265 | 0.247469 | 0.010952 |
| 21 | deals_all_reported_legs | 217 | 217 | 0.334139 | 0.030453 |
| 21 | deals_beyond_turnover | 217 | 159 | 0.358317 | 0.033190 |
| 21 | deals_date_shift | 217 | 217 | 0.329236 | 0.030350 |
| 21 | deals_without_largest | 217 | 217 | 0.333029 | 0.030427 |
| 21 | transactions | 217 | 217 | 0.334182 | 0.030454 |

[deal-archives.csv.gz](deal-archives.csv.gz) · [deal-legs.csv.gz](deal-legs.csv.gz) · [deal-audited.csv.gz](deal-audited.csv.gz) · [transaction-matched-cases.csv.gz](transaction-matched-cases.csv.gz) · [transaction-event-summary.csv](transaction-event-summary.csv) · [matched-comparisons.csv](matched-comparisons.csv)
