# NIFTY V18 — Corporate information database

The corporate database preserves all **345,226** exchange announcements acquired by V17. Each record keeps its issuer symbol and any supplied ISIN, exchange category and source sequence, source file and row, archival summary, filing and dissemination timestamps, attachment URL, revision cues, and reporting or event dates when explicitly stated. The eligible time is the exchange's dissemination timestamp plus **10 minutes**. A past reporting-period end never establishes when the market first learned the contents. The underlying archive is reproducible from the separately hashed 2025 and 2026 source files.

| source year | rows | timed | duplicates | issuers | attached | amendments |
| --- | --- | --- | --- | --- | --- | --- |
| 2,025 | 176,022 | 176,022 | 11,084 | 2,336 | 176,022 | 554 |
| 2,026 | 169,204 | 169,204 | 10,587 | 2,473 | 169,204 | 586 |

Publication duplicates are marked and tied to an earlier episode. These include identical URLs, otherwise identical issuer summaries within 36 hours, and additional earnings publications for a previously identified issuer/period. Distinct amendments retain their timestamps. The audit marked **21,671** duplicate rows. The fixed 240-name liquidity cohort had **230** observed issuer names and **52,121** deduplicated timed publications, including **13,266** high-materiality or direction-bearing rows. Source inventory spans a complete uploaded year for 2025 and a partial 2026 vintage. Category and listing changes can affect arrival frequency. The forecasts retain coverage fields and rolling same-clock normalization based on earlier values.

| family | rows | timed | duplicates | seed rows | material |
| --- | --- | --- | --- | --- | --- |
| routine_or_unclassified | 212,436 | 212,436 | 9,267 | 37,587 | 212 |
| earnings | 27,321 | 27,321 | 8,691 | 3,038 | 27,321 |
| management | 25,518 | 25,518 | 787 | 3,564 | 25,518 |
| shareholding | 17,787 | 17,787 | 165 | 1,714 | 1 |
| acquisition | 14,789 | 14,789 | 453 | 2,322 | 14,789 |
| presentation | 9,647 | 9,647 | 389 | 1,636 | 0 |
| dividend | 8,394 | 8,394 | 99 | 1,658 | 8,394 |
| earnings_followup | 6,947 | 6,947 | 842 | 486 | 0 |
| credit | 4,689 | 4,689 | 148 | 1,001 | 4,689 |
| regulatory | 3,745 | 3,745 | 192 | 805 | 3,745 |
| order_win | 2,863 | 2,863 | 227 | 553 | 2,863 |
| fundraising | 2,528 | 2,528 | 43 | 356 | 2,528 |
| litigation | 1,947 | 1,947 | 99 | 352 | 1,947 |
| business_update | 1,850 | 1,850 | 89 | 326 | 1,850 |
| action | 1,721 | 1,721 | 10 | 166 | 1,721 |
| debt | 1,292 | 1,292 | 132 | 657 | 1,292 |
| expansion | 624 | 624 | 15 | 62 | 624 |
| buyback | 401 | 401 | 8 | 48 | 401 |
| meeting_notice | 350 | 350 | 5 | 39 | 0 |
| divestment | 153 | 153 | 1 | 44 | 153 |
| earnings_schedule | 89 | 89 | 2 | 6 | 0 |
| order_cancellation | 69 | 69 | 3 | 14 | 69 |
| capex | 43 | 43 | 4 | 16 | 43 |
| guidance | 23 | 23 | 0 | 1 | 23 |

[Indexed SQLite data](corporate-information.sqlite) · [Archive provenance](announcement-inventory.json) · [Routine and material categories](archive-category-counts.csv) · [Research-issuer episode inventory](issuer-events.csv.gz) · [Official NSE announcements](https://www.nseindia.in/companies-listing/corporate-filings-announcements)
