# V19 Market Positioning Database

The SQLite database, normalized CSVs and file receipts cover 466 authenticated NSE cash sessions. Delivery contains 1,439,636 security-series rows, 1,074,226 EQ rows and 1,328,266 numeric delivered quantities. All 109,980 V18 fixed-cohort price/ISIN links matched the official cash bhavcopy. The delivery percentage arithmetic audit flagged 3,478 records across all series at the raw source rounding tolerance. Research filters require the recomputed percentage to pass the tolerance, a verified ISIN and a matched close. Original missing entries remain blank.

The participant inventory expanded from 383 parsed OI days to 465 authenticated reports. The old parser skipped valid titles formatted like Jan 01,2025. There are 466 dated participant trade-volume reports. Exact values for the 1,532 earlier participant rows replayed. Ordinary NIFTY futures have 1,398 contract-session rows and recorded contract lots 25, 65, 75. Four OI/lot checks failed and affected daily aggregates use missing values. Stock cash sources are shares and turnover in rupees. Participant and contract fields use the units printed by the publisher.

The historical report publication allowance is 08:15 IST on the following NSE cash session. Previous-close 17:00 forecasts consequently use an older report than the following 08:55 forecast. Independent no-delay, +1 and +5 session versions are explicit. Historical first-print revision timestamps remain unobserved. The SQLite rows preserve the observation date, source file path and modeled eligibility timestamp. Failed and empty source probes remain visible below.

| day | kind | present | status |
| --- | --- | --- | --- |
| 2025-09-19 | open_interest | no | File unavailable |

| family | status | requested | archived |
| --- | --- | --- | --- |
| official probes | 200.000000 | 14 | 14 |
| official probes | 404.000000 | 18 | 0 |
| official probes | — | 1 | 0 |
| participant volume | 200.000000 | 466 | 466 |

| url | status | file |
| --- | --- | --- |
| https://nsearchives.nseindia.com/content/fo/fo_mwpl_15042025.csv | 404 | — |
| https://nsearchives.nseindia.com/content/fo/fo_secban_15042025.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/slbs/bhav/SLB_Bhavcopy_15042025.csv | 404 | — |
| https://nsearchives.nseindia.com/content/slbs/SLB_15042025.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/equities/mkt/MA150425.csv | 200 | sources/probes/cash-market-report-2025-04-15.csv.gz |
| https://nsearchives.nseindia.com/content/fo/fo_mwpl_20102025.csv | 404 | — |
| https://nsearchives.nseindia.com/content/fo/fo_secban_20102025.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/slbs/bhav/SLB_Bhavcopy_20102025.csv | 404 | — |
| https://nsearchives.nseindia.com/content/slbs/SLB_20102025.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/equities/mkt/MA201025.csv | 200 | sources/probes/cash-market-report-2025-10-20.csv.gz |
| https://nsearchives.nseindia.com/content/fo/fo_mwpl_15062026.csv | 404 | — |
| https://nsearchives.nseindia.com/content/fo/fo_secban_15062026.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/slbs/bhav/SLB_Bhavcopy_15062026.csv | 404 | — |
| https://nsearchives.nseindia.com/content/slbs/SLB_15062026.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/equities/mkt/MA150626.csv | 200 | sources/probes/cash-market-report-2026-06-15.csv.gz |
| https://nsearchives.nseindia.com/content/fo/fo_mwpl_17112026.csv | 404 | — |
| https://nsearchives.nseindia.com/content/fo/fo_secban_17112026.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/slbs/bhav/SLB_Bhavcopy_17112026.csv | 404 | — |
| https://nsearchives.nseindia.com/content/slbs/SLB_17112026.csv | 404 | — |
| https://nsearchives.nseindia.com/archives/equities/mkt/MA171126.csv | 200 | sources/probes/cash-market-report-2026-11-17.csv.gz |

[market-positioning.sqlite](market-positioning.sqlite) · [database-receipt.json](database-receipt.json) · [participant-audit.csv.gz](participant-audit.csv.gz) · [source-receipts.json](source-receipts.json) · [alternate-source-preflight.json](alternate-source-preflight.json) · [nifty-futures.csv.gz](nifty-futures.csv.gz) · [delivery-receipts.csv.gz](delivery-receipts.csv.gz) · [asof-positioning-coverage.csv](asof-positioning-coverage.csv) · [NSE derivatives archive](https://betanseapi.nseindia.com/all-reports-derivatives) · [NSE report publication note](https://nsearchives.nseindia.com/content/circulars/CMTR53595.pdf)
