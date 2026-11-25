# 01 — V3 data and availability audit

Scope: observations dated 2025-01-01 through the latest completed session,
2026-11-16. No pre-2025 values, warmup statistics or fitted parameters enter V3.
All earlier research is preserved. `legacy-review.json` inventories and hashes
223 prior reports, source/configuration files and structured artifacts; JSON/CSV
contents and source ASTs were inspected. Their explored dates remain exposed.

## Measured source inventory

Fresh read-only Upstox acquisition: 70 successful identities, zero failed jobs.
Thirteen index/VIX series, NIFTYBEES, six globals and 50 current constituent
identities are retained with source-date filtering, acquisition clocks and hashes.
All 13 domestic index/VIX series now have 465 complete daily observations through
16 November, including NIFTY 500. The prior provisional Monday-bar problem is
resolved in this fresh source vintage; old frozen records remain unchanged.
NIFTY spot volume is zero on every day and cannot support volume/VWAP claims.
NIFTYBEES has actual positive traded volume on all 465 dates.

Official NSE FO archives: 465 successful of 465 requested dates.
Authentic 2025-01-02 and 2026-11-16 archive probes succeeded. Existing Project
Alpha sources retain 260 dated chain sessions plus raw futures archives. The
new archive batch extends the previously untested forecast information set to
earlier 2025. Actual source session and listed expiry/contract identity are checked.

Database: 181 public schema fields inspected; all API-method counts and bounded
coverage summaries are saved. Initial payload/coverage inventories were capped
at 1,000/10,000 rows and are not described as exhaustive row scans. Corrected
response inventory uses `recorded_at` (not nonexistent `fetched_at`). The local
NIFTY 5-minute source contains 34,692 bars dated
2025-01-01 03:45:00+00:00 to 2026-11-16 04:10:00+00:00.
Its 16 November session is partial and cannot be treated as a complete intraday
day. Per-session completeness gates precede intraday feature engineering.

## Point-in-time classification and forecast admissibility

|Category|Classification|Historical decision rule / limitation|
|---|---|---|
|Index/sector daily returns|Usable with explicit limitations|Completed previous session, revised vendor history; source delivery/vintage not replayed|
|NIFTYBEES volume/turnover|Usable with explicit limitations|Actual ETF volume; never assigned to non-traded NIFTY spot|
|Global daily prices|Usable with explicit limitations|Conservative source date strictly before origin date; excludes unfinished prior US session at 00:30 IST|
|Intraday summaries|Usable with explicit limitations|Only valid complete previous sessions; incomplete/special sessions are missing, not zero|
|Official NSE FO futures/OI/chain|Usable with explicit limitations|One extra Indian-session publication lag; source and expiry IDs checked; OI is not writer intent|
|Vendor Greeks/IV/skew|Current-context-only|No archived historical quote-time/IV surface panel; not reverse engineered from today's chain|
|FII/DII|Usable with explicit limitations / short history|Since April 2026, unit-free ratios, one extra session lag; 2025 coverage absent|
|Current 50-stock basket|Research-only|Survivorship/current-membership proxy, not historical NIFTY breadth or index contribution|
|Genuine historical NIFTY membership/weights|Unavailable for full 2025–2026|Recovered membership-event file stops in 2020; a 2024 PDF cannot satisfy 2025-only input constraints|
|Corporate-action unit records|Research-only quality metadata|Past split-adjusted return consistency checked; no future announcement used as signal; dividends/adjustment vintage not fully reconstructed|
|Retained live depth/options snapshots|Current-context-only for these horizons|Captures start late October 2026, with only a handful of distinct sessions; 32m updates are not 32m weekly/monthly outcomes|
|News, earnings, macro releases, event surprises|Unavailable as authenticated historical numeric panels|Empty news or missing event table is not proof of no events|
|Calendar/expiry|Usable with explicit limitations|Historical sessions from valid index bars, future published NSE calendar; unexpected changes require review|

## Integrity review

Historical auto duplicates were largely before the permitted window: this fresh
2025–2026 auto response has zero duplicates. Source-invalid global bars remain
and are rejected; the table below measures this vintage rather than repeating
the old all-history count of 177. Duplicate elimination is deterministic and
conflicting identities/large stock returns are quarantined. A changing archive
or failed hash check invalidates reproducibility. Historical corporate-action
metadata cannot certify a stock-selection universe; current basket results are
reported separately and cannot qualify primary index-breadth claims.

Actual historical acquisition timestamps are absent for most reconstructed
prices and official EOD archives. These are explicitly conditional publication
assumptions, not a genuine as-delivered replay. Current observations are never
backfilled as old option/macro snapshots. Candidate gains must survive removing
derivatives and the survivorship-biased basket.

|Identity|Source-date coverage|Valid sessions|Duplicate rows|Rejected invalid OHLC|Class|
|---|---|---:|---:|---:|---|
|bank_nifty|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|global_brent|2025-01-01–2026-11-14|544|0|0|usable with revised-history/publication limitations|
|global_dow|2025-01-01–2026-11-13|463|0|10|usable with revised-history/publication limitations|
|global_gift|2025-01-01–2026-11-16|491|0|3|usable with revised-history/publication limitations|
|global_hang_seng|2025-01-02–2026-11-16|454|0|5|usable with revised-history/publication limitations|
|global_sp500|2025-01-01–2026-11-16|488|0|0|usable with revised-history/publication limitations|
|global_usdinr|2025-01-01–2026-11-15|557|0|0|usable with revised-history/publication limitations|
|india_vix|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_500|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_auto|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_energy|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_financial|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_fmcg|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_it|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_metal|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_pharma|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_psu_bank|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_realty|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|nifty_spot|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|niftybees|2025-01-01–2026-11-16|465|0|0|usable with revised-history/publication limitations|
|stock_ADANIENT|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ADANIPORTS|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_APOLLOHOSP|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ASIANPAINT|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_AXISBANK|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_BAJAJ-AUTO|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_BAJAJFINSV|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_BAJFINANCE|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_BEL|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_BHARTIARTL|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_BSE|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_CIPLA|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_COALINDIA|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_DRREDDY|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_EICHERMOT|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ETERNAL|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_GRASIM|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_HCLTECH|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_HDFCBANK|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_HDFCLIFE|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_HINDALCO|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_HINDUNILVR|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ICICIBANK|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_INDIGO|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_INFY|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ITC|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_JIOFIN|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_JSWSTEEL|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_KOTAKBANK|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_LT|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_M&M|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_MARUTI|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_MAXHEALTH|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_NESTLEIND|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_NTPC|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ONGC|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_POWERGRID|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_RELIANCE|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_SBILIFE|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_SBIN|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_SHRIRAMFIN|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_SUNPHARMA|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TATACONSUM|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TATASTEEL|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TCS|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TECHM|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TITAN|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TMPV|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_TRENT|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|
|stock_ULTRACEMCO|2025-01-01–2026-11-16|465|0|0|research-only current stock basket|

## Priorities identified at audit time

Items 1–3 below were subsequently tested in V3; their results are in reports
02–08. Genuine dated stock membership and weights remain unavailable.

1. Official dated FO futures basis/OI and same-contract option OI changes, with
   expiry/lot-roll controls and conservative publication lag.
2. Complete prior-session intraday structure, ETF activity, downside volatility,
   VIX versus realized risk, and changes in sector participation.
3. Conditional magnitude/volatility/tail forecasting instead of forced direction.
4. Current-basket participation as a clearly marked proxy ablation; genuine
   dated membership and weights remain a collection priority.

Fresh acquisition happens after the 17 November market open. Final artifacts
must distinguish a late-issued 16 November as-of reconstruction from a valid new
forward forecast. No claim of an untouched pre-market call is permissible.

## Primary source references

Upstox documents the historical candle endpoint, interval choices, date bounds
and global instrument support in its
[Historical Candle Data V3 documentation](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).
These API capabilities do not establish the historical delivery time or vintage
of a particular candle. The acquired files and their measured coverage are the
evidence for this run's usable observations.

The official [NSE derivatives reports catalogue](https://www.nseindia.com/all-reports-derivatives)
identifies the UDiFF common bhavcopy replacement and the historical report
families. This study uses dated final archives, not reconstructed live chains.
Exact URLs, acquisition times and content hashes are in fo-acquisition.json.
