# V12 Options Data And Availability

The inventory covers **466** authenticated daily UDiFF archives from **2025-01-01** to **2026-11-17**. The extraction retained **787,100** NIFTY records with trading/business date, actual and listed expiry, strike, call/put, traded OHLC, last, previous close, close, settlement, transaction count, volume, open interest, lot, identifier and session record code. Native ZIP hashes reconcile to the frozen source receipts, and core close, settlement and volume fields were checked against the earlier slim archives. The official daily NIFTY close supplies a separate underlying denominator.

| measure | count |
| --- | --- |
| all_rows | 17573689 |
| nifty_rows | 787100 |
| option_rows | 785702 |
| futures_rows | 1398 |
| traded_option_rows | 463084 |
| zero_volume_close_positive | 322618 |
| no_trade_or_no_valid_close | 322618 |
| complete_traded_ohlc | 463084 |
| traded_ohlc_consistent | 463084 |
| price_equals_previous_on_trade | 3637 |
| traded_close_neq_last | 343612 |
| traded_close_neq_settlement | 86366 |
| same_expiry_strike_traded_pairs | 173910 |
| unpaired_traded_strikes | 115264 |
| duplicate_contract_session_rows | 0 |
| nonzero_underlying_mismatch_gt_05 | 0 |
| actual_expiry_differs_from_listed | 0 |
| actual_expiry_after_2026_rows | 102094 |

A positive close on a zero-trade row is an unverified mark. Main price reconstruction requires observed volume on both sides where parity is used. Stale-close flags, unpaired strikes, relative value bounds, option-price distortions, parity scatter and strike gaps are retained. Historical bid/ask spreads, quote timestamps, instrument Greeks, and matched-tenor MIBOR are unavailable in this archive. NSE’s India VIX uses order-book bids and asks and a relevant maturity funding input. V12 estimates implied risk from end-of-day traded-contract marks. The settlement-price check uses settlement values for the same eligible traded contracts, treating those values as reference marks. [NSE daily archives](https://www.nseindia.com/all-reports) · [India VIX definition](https://www.nseindia.com/static/products-services/indices-indiavix-index) · [Native contract specifications](https://betanseapi.nseindia.com/static/products-services/equity-derivatives-contract-specifications).

All main option and futures data are at least one observed NSE archive session old at the cash-origin close. The inherited decision clock is 09:10 IST on the next session. Foreign availability estimates are checked against that clock as well as an earlier source date. Two- and five-session options buffers and a same-close diagnostic test sensitivity to receipt assumptions. Both observed expiries and scheduled event publications have explicit evidence. A separate refresh reacquired **2,946** valid records, last complete NIFTY date **2026-11-23**, with **0** additional completed dates beyond V11. [Raw NIFTY extraction](sources/nifty-udiff.csv.gz) · [Daily quality audit](daily-options-audit.csv) · [Published source receipts](publication-source-receipts.json) · [Market refresh](refresh-summary.json).
