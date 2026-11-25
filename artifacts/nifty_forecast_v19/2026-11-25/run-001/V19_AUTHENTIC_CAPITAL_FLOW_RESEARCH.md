# V19 Authentic Capital Flow Research

The official data routes yielded three different series. CDSL daily publications record custodian-reported purchases and sales by route in ₹ crore. CDSL fortnightly records show sector-level equity net investment and separately report assets under custody. AMFI monthly publications report actual scheme-level fund mobilization and redemptions with separate AUM. The fund series include funds with material price effects in AUM and different gross transaction coverage. None of the three series supplies a complete point-in-time daily NSE exchange FII/DII pair. The daily NSE endpoint exposed a current report, and the parameterized depository forms returned empty or undated historical selections. Formal ETF creation/redemption counts and a complete DII trade series remain unavailable in the audited feeds.

| family | rows | dates |
| --- | --- | --- |
| cdsl-sector | 900 | 36 |
| cdsl-daily | 192 | 64 |
| amfi-monthly | 72 | 22 |

First-release times and historical revisions remain unverified. The descriptives start on the first observed NSE cash session after one day for CDSL daily, ten calendar days for CDSL fortnightly and twenty for AMFI. The reporting date can follow the underlying trade date. The usable number of independent flow releases is the release count. Stratified Spearman figures below are descriptive and kept outside the primary endpoint panel.

| series | category | horizon | test | n | spearman |
| --- | --- | --- | --- | --- | --- |
| daily | Stock Exchange | 5 | future_return | 59 | -0.036149 |
| daily | Stock Exchange | 5 | future_realized_vol | 59 | 0.178144 |
| daily | Stock Exchange | 5 | lag_net | 58 | 0.274117 |
| daily | Stock Exchange | 21 | future_return | 59 | 0.150820 |
| daily | Stock Exchange | 21 | future_realized_vol | 59 | 0.346791 |
| daily | Stock Exchange | 21 | lag_net | 58 | 0.274117 |
| daily | Sub-total | 5 | future_return | 59 | -0.015167 |
| daily | Sub-total | 5 | future_realized_vol | 59 | 0.201347 |
| daily | Sub-total | 5 | lag_net | 58 | 0.301003 |
| daily | Sub-total | 21 | future_return | 59 | 0.138255 |
| daily | Sub-total | 21 | future_realized_vol | 59 | 0.324055 |
| daily | Sub-total | 21 | lag_net | 58 | 0.301003 |
| monthly | equity_etf | 5 | future_return | 2 | — |
| monthly | equity_etf | 5 | future_realized_vol | 2 | — |
| monthly | equity_etf | 5 | lag_net | 1 | — |
| monthly | equity_etf | 21 | future_return | 1 | — |
| monthly | equity_etf | 21 | future_realized_vol | 1 | — |
| monthly | equity_etf | 21 | lag_net | 0 | — |
| monthly | open_end_equity | 5 | future_return | 2 | — |
| monthly | open_end_equity | 5 | future_realized_vol | 2 | — |
| monthly | open_end_equity | 5 | lag_net | 1 | — |
| monthly | open_end_equity | 21 | future_return | 1 | — |
| monthly | open_end_equity | 21 | future_realized_vol | 1 | — |
| monthly | open_end_equity | 21 | lag_net | 0 | — |
| fortnight | sector_sum | 5 | future_return | 35 | 0.094118 |
| fortnight | sector_sum | 5 | future_realized_vol | 35 | -0.117367 |
| fortnight | sector_sum | 5 | lag_net | 34 | 0.165470 |
| fortnight | sector_sum | 21 | future_return | 33 | 0.024398 |
| fortnight | sector_sum | 21 | future_realized_vol | 33 | -0.170789 |
| fortnight | sector_sum | 21 | lag_net | 32 | 0.206745 |

| day | sector | net equity inr crore |
| --- | --- | --- |
| 2026-11-15 | Financial Services | 43102.000000 |
| 2026-11-15 | Telecommunication | 7570.000000 |
| 2026-11-15 | Automobile and Auto Components | 7551.000000 |
| 2026-11-15 | Consumer Services | 6519.000000 |
| 2026-11-15 | Information Technology | 5080.000000 |
| 2026-11-15 | Fast Moving Consumer Goods | 3042.000000 |

[capital-flow-receipt.json](capital-flow-receipt.json) · [flow-source-receipts.json](flow-source-receipts.json) · [flow-parsing-audit.csv](flow-parsing-audit.csv) · [cdsl-daily-observations.csv.gz](cdsl-daily-observations.csv.gz) · [cdsl-sector-observations.csv.gz](cdsl-sector-observations.csv.gz) · [cdsl-sector-reconciliation.csv](cdsl-sector-reconciliation.csv) · [amfi-monthly-observations.csv.gz](amfi-monthly-observations.csv.gz) · [capital-flow-associations.csv](capital-flow-associations.csv) · [cash-form-probes.json](cash-form-probes.json) · [SEBI data directory](https://www.sebi.gov.in/curation/fpi.html) · [CDSL archives](https://www.cdslindia.com/Publications/ForeignPortInvestor.html) · [CDSL interpretation notes](https://www.cdslindia.com/publications/fiinote.html) · [AMFI monthly archives](https://www.amfiindia.com/research-information/amfi-monthly)
