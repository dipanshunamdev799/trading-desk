# V16 Forward research ledger

The independent refresh at **2026-11-25T09:40:47.562960+05:30** covered completed cash sessions through the calendar bound **2026-11-24**. Authenticated Upstox read-only historical snapshots for NIFTY 50, India VIX, Bank NIFTY and NIFTY 500 are archived. Official NSE index reports independently verify the complete cash OHLC fields. November 24 was an NSE cash market holiday for Guru Nanak Jayanti. The archive records its status explicitly regardless of missing provider rows. No historical window in the November 17 main vintage uses these observations. [NSE capital market holiday circular](https://archives.nseindia.com/content/circulars/CMTR71775.pdf)

## Authoritatively reconciled dated bars

| day | status | source status | official open | official close | upstox close |
| --- | --- | --- | --- | --- | --- |
| 2026-11-18 | verified | 200 | 25323.150000 | 25227.950000 | 25227.950000 |
| 2026-11-19 | verified | 200 | 25186.800000 | 25514.300000 | 25514.300000 |
| 2026-11-20 | verified | 200 | 25368.000000 | 25800.600000 | 25800.600000 |
| 2026-11-23 | verified | 200 | 25929.150000 | 25349.650000 | 25349.650000 |

## Original locked target slots, 0 matured

| version | key | horizon | issued | reference session | reference close | target | sessions verified | maturity | realized return |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V4 | 2026-11-17/LATE_DIAGNOSTIC | 21 | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 25387.400000 | 2026-12-17 | 4 | pending completion and publication | — |
| V4 | 2026-11-17/LATE_DIAGNOSTIC | 5 | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 25387.400000 | 2026-11-25 | 4 | pending completion and publication | — |
| V5 | h5-L01 | 5 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-11-26 | 3 | pending completion and publication | — |
| V5 | h5-I03_nosize | 5 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-11-26 | 3 | pending completion and publication | — |
| V5 | h21-E00 | 21 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-12-18 | 3 | pending completion and publication | — |
| V5 | h21-I01_legacy | 21 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-12-18 | 3 | pending completion and publication | — |

The V4 late diagnostics target November 25 and December 17. Their issue comes after the original opening process on November 18. Four V5 forecasts are frozen before their first target session and target November 26 and December 18. The original files retain their verified issue and prediction hashes. A valid resolution requires the original session sequence, completed target, official cash close and a publication guard at 18:00 IST. A search of archived issue records located these six forecasts as genuine prior issues. The V16 historical clocks are reconstructions and the V16 forward issuance count is zero.

[Authentication, forecast hashes and status](forward-ledger.json) · [V15 original immutable tracking](../../../nifty_forecast_v15/2026-11-25/run-001/V15_FORWARD_RESEARCH_LEDGER.md)
