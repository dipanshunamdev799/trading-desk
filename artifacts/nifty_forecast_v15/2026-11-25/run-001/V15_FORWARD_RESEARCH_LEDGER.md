# V15 immutable forward research ledger

At **2026-11-25T08:51:00.934493+05:30** the independent refresh matched **4** completed NIFTY 50 sessions from authenticated Upstox and the official NSE daily index archive. The historical November 17 vintage is preserved as a separate replay. NSE and Upstox values matched exactly at the verified closing marks. The refresh also archives India VIX, NIFTY Bank and NIFTY 500 payloads separately. November 24 is an NSE trading holiday. The expected publication guard is 18:00 IST on the original target date, followed by reconciliation of the complete originally named session sequence.

## Reconciled closes after the historical freeze

| day | upstox open | upstox high | upstox low | upstox close | nse close | delta | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-18 | 25323.150000 | 25390.800000 | 25141.800000 | 25227.950000 | 25227.950000 | 0.000000 | verified |
| 2026-11-19 | 25186.800000 | 25514.300000 | 25104.800000 | 25514.300000 | 25514.300000 | 0.000000 | verified |
| 2026-11-20 | 25368.000000 | 25808.800000 | 25345.200000 | 25800.600000 | 25800.600000 | 0.000000 | verified |
| 2026-11-23 | 25929.150000 | 25992.600000 | 25343.850000 | 25349.650000 | 25349.650000 | 0.000000 | verified |

## Original immutable target slots

| version | slot | horizon | issued | reference session | reference close | target | completed | maturity | realized return |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V4 | V4 21-session late diagnostic | 21 | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 25387.400000 | 2026-12-17 | 4 | pending completion and publication | — |
| V4 | V4 5-session late diagnostic | 5 | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 25387.400000 | 2026-11-25 | 4 | pending completion and publication | — |
| V5 | h5-L01 | 5 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-11-26 | 3 | pending completion and publication | — |
| V5 | h5-I03_nosize | 5 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-11-26 | 3 | pending completion and publication | — |
| V5 | h21-E00 | 21 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-12-18 | 3 | pending completion and publication | — |
| V5 | h21-I01_legacy | 21 | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 25227.950000 | 2026-12-18 | 3 | pending completion and publication | — |

V4 issued after the first target session began and qualifies as a late diagnostic. V5 preserved four experimental laws before its first target session opened. V15 resolves each original forecast only after its own endpoint is published with the original session list intact. The November 18 V4 issue chain and V5 frozen issue file retain their original hashes. The V15 October path case is historical, and this ledger tracks the immutable preexisting V4 and V5 submissions.

[Authenticated refresh, chain hashes and original forecast probabilities](forward-ledger.json) [NSE 2026 trading holidays](https://archives.nseindia.com/content/circulars/CMTR71775.pdf)
