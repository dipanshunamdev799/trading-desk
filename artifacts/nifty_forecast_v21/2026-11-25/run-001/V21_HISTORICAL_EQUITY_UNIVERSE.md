# V21 Historical Equity Universe

The frozen observation universe contains **1,384,549 security-date rows** for **3,852 dated symbols** across **466 sessions**. V21 reused **408** checked cash files and acquired the missing **58** from the official NSE UDiFF archive. Stable security identifiers, observed series, OHLC, volume and turnover remain traceable to cash files. EQ, BE, BZ, SM and ST rows enter the inventory. The fixed January research cohort selected the **240** highest median-turnover securities with at least **12** traded EQ sessions by January 31. It became eligible in February. The union of that cohort with the source-supported index holdings produced **272 modeled series**. A security can cease trading or leave an index without disappearing from the historical inventory.

The two official archive families yielded **22 complete monthly NIFTY 50 and Next 50 source vintages**, held under a five-completed-session publication allowance, plus dated holdings reports for several sector indices. The archives contain **6,673 parsed constituent-weight rows**. The PDF closing prices matched the cash tape on **4,447 of 4,447 available comparisons**. The CSVs preserve reported weight, equity capital in rupees and index free-float capitalization. Normalized market caps supply the main weights. Two Next 50 files have less than 99.75% in their rounded weight columns and are separately flagged. The NIFTY 50 plus Next 50 membership union informs broad eligibility. The dated 200 and 500 constituent books, full share and face-value history and daily investible-weight-factor and divisor series remain incomplete.

| flavor | index name | vintages | minimum members | maximum members | mean reported sum |
| --- | --- | --- | --- | --- | --- |
| official_monthly_csv | NIFTY 50 | 22 | 50 | 51 | 100.001818 |
| official_monthly_csv | NIFTY Next 50 | 22 | 50 | 54 | 99.917273 |
| official_monthly_pdf | NIFTY 50 | 22 | 50 | 51 | 99.996818 |
| official_monthly_pdf | NIFTY Bank | 22 | 12 | 14 | 100.000909 |
| official_monthly_pdf | NIFTY Financial Services | 22 | 20 | 20 | 100.000909 |
| official_monthly_pdf | NIFTY IT | 22 | 10 | 10 | 99.998636 |
| official_monthly_pdf | NIFTY India FPI 150 | 5 | 150 | 150 | 100.028000 |
| official_monthly_pdf | NIFTY Midcap Select | 22 | 25 | 25 | 100.006364 |
| official_monthly_pdf | NIFTY Next 50 | 22 | 50 | 54 | 100.007727 |

| month | index name | status | count | rounded sum |
| --- | --- | --- | --- | --- |
| 2025-04-30 | NIFTY Next 50 | mcap normalized; weight total discrepancy | 50 | 99.010000 |
| 2025-05-31 | NIFTY Next 50 | mcap normalized; weight total discrepancy | 50 | 99.100000 |

The target is a cash **price index**. Ordinary dividends stay in the observed price changes. Unit changes are handled with dated split and bonus ratios, including simultaneous changes. Confirmed cash resets and the Tata Motors demerger receive separate audit rows. Missing holdings are carried at the last mark in tracking diagnostics and missing outcomes are excluded from component model fitting. Constituents and issuer group labels follow the latest eligible dated files. Industry mapping and any unclassified names are disclosed. Standalone exchange participant OI stays at the market level. V18 timestamped issuer events and first financial results, V19 delivery and completed bulk/block activity enter only through their own verified or declared eligibility rules.

[source-receipt.json](source-receipt.json) · [historical-equity-inventory.csv](historical-equity-inventory.csv) · [january-liquidity-universe.csv](january-liquidity-universe.csv) · [universe-receipt.json](universe-receipt.json) · [dated-weights.csv.gz](dated-weights.csv.gz) · [weight-snapshot-audit.csv](weight-snapshot-audit.csv) · [official-weight-cash-reconciliation.csv.gz](official-weight-cash-reconciliation.csv.gz) · [cash-identity-and-actions.csv.gz](cash-identity-and-actions.csv.gz) · [equity-panel.npz](equity-panel.npz) · [NSE Indices monthly archives](https://niftyindices.com/reports/monthly-reports) · [NSE capital-market historical reports](https://betanseapi.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives)
