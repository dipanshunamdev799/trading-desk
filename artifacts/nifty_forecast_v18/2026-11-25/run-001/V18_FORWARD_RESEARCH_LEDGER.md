# NIFTY V18 — Forward research ledger

The separate historical-forward refresh used the time **2026-11-25T15:08:30.243630+05:30** and calendar bound **2026-11-24**. The research fit remains frozen through **November 17, 2026**. Official close reconciliation compares NSE and Upstox prices and respects each original session sequence and the **18:00 IST** publication guard. The NSE-confirmed November 24 closure remains in the receipt. The ledger retains the **six** V4 and V5 issues and their original hashes, probabilities, full distribution references, and completed sessions. V4 was a late first-session diagnostic and the V5 issues precede their first target sessions. There were **0** new timestamped V18 issues. The captured source window and issue clocks did not allow a fresh pre-auction or completed-close panel at the refresh.

| day | status | open | close | receipt |
| --- | --- | --- | --- | --- |
| 2026-11-18 | verified | 25323.150000 | 25227.950000 | forward/2026-11-25T150830/NSE-2026-11-18.csv |
| 2026-11-19 | verified | 25186.800000 | 25514.300000 | forward/2026-11-25T150830/NSE-2026-11-19.csv |
| 2026-11-20 | verified | 25368.000000 | 25800.600000 | forward/2026-11-25T150830/NSE-2026-11-20.csv |
| 2026-11-23 | verified | 25929.150000 | 25349.650000 | forward/2026-11-25T150830/NSE-2026-11-23.csv |

| version | key | horizon | issued | reference | target | verified sessions | status | return realized | original p up | issue hash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V4 | 2026-11-17\|LATE_DIAGNOSTIC | 21 | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 2026-12-17 | 4 | pending completion and publication | — | B00_empirical 0.488095, D00_empirical 0.488095, D03_residual_shrunk 0.000000 | 27b9a03e5de25d2df52bde928809f67578a7954190925a06a419ab7580cb8f84 |
| V4 | 2026-11-17\|LATE_DIAGNOSTIC | 5 | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 2026-11-25 | 4 | pending completion and publication | — | A00_sector 0.680546, B00_empirical 0.412698, M05_lgbm 0.708441, Z_neutral 0.500000, Z_reversion 0.450000, D00_empirical 0.412698, D03_residual_shrunk 0.095238 | 27b9a03e5de25d2df52bde928809f67578a7954190925a06a419ab7580cb8f84 |
| V5 | h5-L01 | 5 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-11-26 | 3 | pending completion and publication | — | 0.790079 | 0f4908480d4d4d56b7013d62267489f2526cd77e58647c5eec60ad2b4bf99a9a |
| V5 | h5-I03_nosize | 5 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-11-26 | 3 | pending completion and publication | — | 0.681746 | 0f4908480d4d4d56b7013d62267489f2526cd77e58647c5eec60ad2b4bf99a9a |
| V5 | h21-E00 | 21 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-12-18 | 3 | pending completion and publication | — | 0.488095 | 0f4908480d4d4d56b7013d62267489f2526cd77e58647c5eec60ad2b4bf99a9a |
| V5 | h21-I01_legacy | 21 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-12-18 | 3 | pending completion and publication | — | 0.588690 | 0f4908480d4d4d56b7013d62267489f2526cd77e58647c5eec60ad2b4bf99a9a |

[Append-only source snapshots and original issue hashes](forward-ledger.json) · [NSE closure calendar](https://archives.nseindia.com/content/circulars/CMTR71775.pdf)
