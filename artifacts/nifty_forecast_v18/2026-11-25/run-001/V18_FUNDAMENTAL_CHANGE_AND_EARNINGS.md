# NIFTY V18 — Fundamental change and earnings

We used NSE's original Integrated Filing financial documents and chose a bounded sample before inspecting forecast performance. The audit recovered truncated issuer listings using smaller dated queries and preserved both retrieval receipts. The final listings contain **3,574** verified issuer-filing rows. Of **1,280** selected documents, **1,278** supplied admissible facts. The **10,621** facts cover **7** quarters and **152** issuers. Each fact retains its exact XBRL name, unit, context, document version and broadcast eligibility. The extraction accepted quarter-duration figures of **65–105 days**, dated balance-sheet facts and separately labeled longer current-year operating cash flow. It excluded contexts beginning before January 2025 and conflicting values for an otherwise identical fact. Missing operating-profit and capex facts remain missing when the mapped tags did not verify comparability. Cash-flow aggregates use a quarter-equivalent normalization with the filed duration. Profit/revenue comparisons retain their basis and account definition.

| metric | accepted count |
| --- | --- |
| total_income | 1,250 |
| finance_cost | 1,234 |
| profit | 1,234 |
| pre_tax | 1,149 |
| revenue | 1,133 |
| eps | 1,131 |
| assets | 757 |
| cash | 681 |
| debt_noncurrent | 581 |
| debt_current | 581 |
| op_cash | 457 |
| interest_income | 266 |
| debt | 167 |

There were **1,063** first usable company-period observations, **870** quarter-over-quarter revenue comparisons, **427** year-over-year profit comparisons and **711** historical profit-expectation errors. The expectation uses the most recent comparable published profit and a shrunk historical change learned from earlier disclosures. It is separate from an ordinary reported change. Historical analyst consensus and comparable pre-announcement company guidance were unavailable for this sample. A revision is eligible at the revision's own timestamp, and an original document is assigned to its own release. Standalone and consolidated observations are compared only within their own basis.

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | fundamental_only | clock_structural | brier | 265 | 53 | 0.257659 | 0.238274 | -0.019385 | -0.060329 | 0.021560 |
| 5 | preauction_0855 | fundamental_only | clock_structural | crps | 265 | 53 | 0.011245 | 0.010658 | -0.000587 | -0.002127 | 0.000953 |
| 5 | preauction_0855 | fundamental_augmentation | counts | brier | 265 | 53 | 0.248263 | 0.243837 | -0.004426 | -0.022388 | 0.013536 |
| 5 | preauction_0855 | fundamental_augmentation | counts | crps | 265 | 53 | 0.011103 | 0.010874 | -0.000229 | -0.000815 | 0.000356 |
| 5 | preauction_0855 | sector_liquidity_proxy | fundamental_augmentation | brier | 265 | 53 | 0.250934 | 0.248263 | -0.002671 | -0.015818 | 0.010477 |
| 5 | preauction_0855 | sector_liquidity_proxy | fundamental_augmentation | crps | 265 | 53 | 0.011178 | 0.011103 | -0.000075 | -0.000456 | 0.000307 |
| 5 | preauction_0855 | fundamental_augmentation | clock_structural | brier | 265 | 53 | 0.248263 | 0.238274 | -0.009989 | -0.031308 | 0.011331 |
| 5 | preauction_0855 | fundamental_augmentation | clock_structural | crps | 265 | 53 | 0.011103 | 0.010658 | -0.000445 | -0.001092 | 0.000202 |
| 5 | preauction_0855 | sector_liquidity_proxy | clock_structural | brier | 265 | 53 | 0.250934 | 0.238274 | -0.012659 | -0.030550 | 0.005231 |
| 5 | preauction_0855 | sector_liquidity_proxy | clock_structural | crps | 265 | 53 | 0.011178 | 0.010658 | -0.000519 | -0.001161 | 0.000122 |
| 5 | preauction_0855 | fundamental_augmentation | component_plus_residual | brier | 265 | 53 | 0.248263 | 0.238003 | -0.010260 | -0.033513 | 0.012994 |
| 5 | preauction_0855 | fundamental_augmentation | component_plus_residual | crps | 265 | 53 | 0.011103 | 0.010309 | -0.000795 | -0.001633 | 0.000044 |
| 5 | previous_1700 | fundamental_only | clock_structural | brier | 265 | 53 | 0.257782 | 0.238605 | -0.019177 | -0.065336 | 0.026981 |
| 5 | previous_1700 | fundamental_only | clock_structural | crps | 265 | 53 | 0.011296 | 0.010721 | -0.000574 | -0.002262 | 0.001113 |
| 5 | previous_1700 | fundamental_augmentation | counts | brier | 265 | 53 | 0.248308 | 0.244096 | -0.004212 | -0.025565 | 0.017141 |
| 5 | previous_1700 | fundamental_augmentation | counts | crps | 265 | 53 | 0.011194 | 0.010935 | -0.000259 | -0.000919 | 0.000401 |
| 5 | previous_1700 | sector_liquidity_proxy | fundamental_augmentation | brier | 265 | 53 | 0.252170 | 0.248308 | -0.003862 | -0.018083 | 0.010359 |
| 5 | previous_1700 | sector_liquidity_proxy | fundamental_augmentation | crps | 265 | 53 | 0.011271 | 0.011194 | -0.000077 | -0.000522 | 0.000368 |
| 5 | previous_1700 | fundamental_augmentation | clock_structural | brier | 265 | 53 | 0.248308 | 0.238605 | -0.009703 | -0.032993 | 0.013586 |
| 5 | previous_1700 | fundamental_augmentation | clock_structural | crps | 265 | 53 | 0.011194 | 0.010721 | -0.000473 | -0.001176 | 0.000231 |
| 5 | previous_1700 | sector_liquidity_proxy | clock_structural | brier | 265 | 53 | 0.252170 | 0.238605 | -0.013565 | -0.035164 | 0.008033 |
| 5 | previous_1700 | sector_liquidity_proxy | clock_structural | crps | 265 | 53 | 0.011271 | 0.010721 | -0.000549 | -0.001278 | 0.000180 |
| 5 | previous_1700 | fundamental_augmentation | component_plus_residual | brier | 265 | 53 | 0.248308 | 0.236585 | -0.011723 | -0.033590 | 0.010143 |
| 5 | previous_1700 | fundamental_augmentation | component_plus_residual | crps | 265 | 53 | 0.011194 | 0.010658 | -0.000536 | -0.001245 | 0.000174 |
| 21 | preauction_0855 | fundamental_only | clock_structural | brier | 217 | 11 | 0.295998 | 0.302805 | 0.006807 | -0.098750 | 0.112365 |

[Source and version inventory](structured-results-listing.csv.gz) · [All accepted financial facts and contexts](structured-financial-facts.csv.gz) · [Point-in-time changes and expectation errors](fundamental-comparisons.csv.gz) · [Loading and pagination audit](structured-listing-coverage.csv) · [Official Integrated Filing archive](https://www.nseindia.in/companies-listing/corporate-integrated-filing)
