# Historical expansion feasibility and official benchmark provenance

## Verified acquisitions

- [NSE Indices historical-data page](https://www.niftyindices.com/reports/historical-data) exposes separate total-return and price-index downloads. We downloaded 2,690 daily TRI levels per index for Nifty50, Nifty500, NiftyBank, NiftyIT and NiftyPharma, from1Jan2016 through9Nov2026. Source rows retain `TotalReturnsIndex`; NTR is not substituted for TRI.
- The official [current website JavaScript](https://liveindexsa.niftyindices.com/assets/js/IISLComponet.js), function `TotalReturnindexHistoricalData`, lines1723-1735 of our retained file, calls [the current endpoint](https://www.niftyindices.com/BackPage/getTotalReturnIndexString). POST JSON contains `cinfo` with indexname/start/end. The retired `/Backpage.aspx/getTotalReturnIndexString` route returned HTTP200homepageHTML and was rejected, not parsed as data. Both failed and successful acquisition logs/raw responses are preserved.
- [Official inclusion/exclusion workbook](https://archives.nseindia.com/content/indices/IndexInclExcl.xls): 37sheets downloaded and parsed. Nifty500 has2,495eventrows from1998-01-08 to2020-09-14; Nifty50 ends2020-07-31. This file is stale for2021-2026 and does not supply a certified full historical membership master. Events contain company names, dates and description, not a complete ISIN-based historical identity/sector ledger.
- [Upstox historical daily API documentation](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) advertises daily history fromJanuary2000 and a ten-year per-request range. Actual authenticated read-only probes for2016-2019 returned986Niftydailycandles,986Reliance,983Infosys and983TCS. These cached sample successes demonstrate availability for these instruments, not coverage or adjustment quality for every historical stock.
- [NSE securities page](https://www.nseindia.com/static/market-data/securities-available-for-trading) provides symbol/name-change files. Those are identity aids; today's available-for-trading list is not a historical universe or proof of delisted-price coverage.

## What can and cannot be extended now

**Verified fact:** 5-10years of official total-return index history is available and has been retained. Dailyprice retrieval before2020 succeeds for the four sampled instruments. The existing500namepanel alreadyhas2020-2026warmup prices but was selected usingOctober2024holdings.

**Unresolved:** a full historical2016-2026 stock identity/membership ledger; delisted/merged/suspended-instrument raw history and liquidation entitlements; all earlier corporateaction records and dividend component parsing; historically valid sector labels; true quote-depth/spread and volume-adjustment status. Four current surviving instrument probes do not resolve these.

**Methodological limit:** backtesting2016-2024 using theOctober2024selected cohort would inject survival/selection bias. We did not label that exercise a historically investable ten-year test. The downloaded membership workbook requires a known starting snapshot, identity resolution, and newer announcements before it can become a complete reconstitution ledger.

**Exact next data experiment:** reconstruct and audit one historical2016starting snapshot, including every later exit/delist, before acquiring an entire decade. Match known changeevents against month-end snapshots, manually resolve mergers/demergers and keep missing identities in the ledger. Expand only when cash/price/unit/action reconciliation passes. If complete membership cannot be obtained, label the result a fixed historical cohort, retain all starting identities, and state missing/delist coverage explicitly.

**Chronological design proposal:** freeze hypotheses and code before reading strategy outcomes on earlier2016-2024 data; use2016-2020development,2021-2022validation,2023-2024retrospective held segment. Earlier years contain familiar market events and the design follows2024-2026research, so this is temporal transfer evidence, not pristine discovery independent of all prior knowledge. November2024-November2026 remains contaminated. A genuinely new performance holdout must collect future data after the next preregistration, with a fixed calendar horizon and no retuning.

## Index comparison conventions

For each segment, total return runs from the last published close before its start through the last published close before its exclusive end. DailyTRI includes dividends reinvested by index methodology. NoETFfees, tradingcosts or capacity constraint are applied to published index levels. All benchmark paths use genuine observed index values; no missing price history is fabricated. Dailyreturn Sharpe assumes zero cash rate, annualizes bysqrt252, and is descriptive. Exposure100% refers to the published fullyinvested index. Turnover of a replicating fund cannot be inferred from indexlevels and is left unavailable.

Independent-sleeve buyhold/control results have different capital utilization, equal starting stock capital and a dated frozen cohort, so their differences from cap-weighted reconstituted TRI are not automatically alpha. SectorBank/IT/Pharma are contextual controls, not coverage of every sector in the universe.
