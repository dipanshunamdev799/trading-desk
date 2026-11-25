# V20 Additional Information Discovery

V20 recovered **21** dated first-print CPI PDFs from the Federal Reserve Bank of St. Louis archive of original Bureau of Labor Statistics releases. Each accepted PDF matches its printed release date, observed month and 08:30 Eastern embargo. The eligibility time includes ten minutes and accounts for daylight saving. **4** semiannual NSE Indices notices preserve both publication and effective dates, and **26** futures contract/lot states come from certified V19 contract records. Index notices verify specific additions and deletions. A complete historical free-float weighting panel still requires dated full membership and weights.

The CDSL eServices monthly page was a distinct retrieval route from V19's public historical form. It added **12** authenticated daily reporting dates and **36** gross purchase, sale and net equity rows through **2026-11-17**. Combined coverage is **76** CDSL daily reporting dates, 36 sector fortnightlies and 22 AMFI months. The added custody observations inherit a conservative next-session eligibility allowance, retain their own receipt and are assessed separately from the primary lifetime panel. Records dated after the freeze are excluded from historical outcomes.

| published date | effective date | index mention | membership notice |
| --- | --- | --- | --- |
| 2025-02-21 | 2025-03-28 | yes | published additions and deletions, no daily full index weights |
| 2025-08-22 | 2025-09-30 | yes | published additions and deletions, no daily full index weights |
| 2026-02-23 | 2026-03-30 | yes | published additions and deletions, no daily full index weights |
| 2026-08-10 | 2026-09-30 | yes | published additions and deletions, no daily full index weights |

| target | n | rank |
| --- | --- | --- |
| return_1 | 21 | -0.127885 |
| return_5 | 21 | 0.110133 |
| return_21 | 20 | -0.017144 |
| late_6_21 | 20 | -0.088769 |
| risk_5 | 21 | 0.154186 |

| horizon | n completed | spearman | scope |
| --- | --- | --- | --- |
| 5 | 7 | -0.357143 | Descriptive on the dated reports; same report date is never used before the next cash session. |
| 21 | 0 | — | Descriptive on the dated reports; same report date is never used before the next cash session. |

| url | status | file |
| --- | --- | --- |
| https://api.upstox.com/v2/expired-instruments/expiries?instrument_key=NSE_INDEX%7CNifty+50 | 401 | — |
| https://api.upstox.com/v2/expired-instruments/expiries?instrument_key=GLOBAL_INDEX%7CSGX+NIFTY | 401 | — |

The inherited 466 NSE participant volume files and dated domestic contracts are available. The broker expired-contract requests returned HTTP 401. Offshore quote coverage remains distinct from confirmed individual contract identity. A reconciled daily exchange FII/DII pair, full daily ETF creation/redemption, complete dated index weights and original analyst-expectation vintages remain unresolved.

[source-discovery-receipt.json](source-discovery-receipt.json) · [first-release-cpi.csv](first-release-cpi.csv) · [macro-release-nifty-associations.csv](macro-release-nifty-associations.csv) · [nifty-membership-notices.csv](nifty-membership-notices.csv) · [futures-contract-identity-inventory.csv](futures-contract-identity-inventory.csv) · [cdsl-extension-receipt.json](cdsl-extension-receipt.json) · [cdsl-extended-daily.csv](cdsl-extended-daily.csv) · [FRASER archived BLS release](https://fraser.stlouisfed.org/files/docs/publications/bls/newsreleases/cpi/cpi_20260610.pdf) · [NSE Indices notices](https://www.niftyindices.com/press-release) · [CDSL daily reporting access](https://www.cdslindia.com/eservices/publications/fiidaily) · [Upstox expired-contract specification](https://upstox.com/developer/api-documentation/get-expired-future-contracts/)
