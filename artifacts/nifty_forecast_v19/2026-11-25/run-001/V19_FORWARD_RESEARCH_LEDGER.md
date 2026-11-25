# V19 Forward Research Ledger

The original V4/V5 ledger refresh used the earlier publication guard and exact stored target sessions. Its immutable issue hashes are retained in the V19 JSON. It was checked at 2026-11-25T18:44:20.222040+05:30. The November 24 cash holiday is documented in the official exchange schedule. Endpoint scoring requires 18:00 IST on the final original target date and a complete reconciled session sequence. An authenticated current-session OHLC quote can corroborate the published daily NSE bar when the historical API is one session behind. The original late-diagnostic classification governs how its score is interpreted.

| version | key | horizon | classification | original issued | reference | target | matched sessions | maturity | realized |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V4 | 2026-11-17\|LATE_DIAGNOSTIC | 21 | prospective before endpoint; late first-session diagnostic | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 2026-12-17 | 5 | pending completion and publication | — |
| V4 | 2026-11-17\|LATE_DIAGNOSTIC | 5 | prospective before endpoint; late first-session diagnostic | 2026-11-18T09:33:38.781325+05:30 | 2026-11-17 | 2026-11-25 | 5 | resolved on original target | 0.017010 |
| V5 | h5-L01 | 5 | forward experimental before first target session | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-11-26 | 4 | pending completion and publication | — |
| V5 | h5-I03_nosize | 5 | forward experimental before first target session | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-11-26 | 4 | pending completion and publication | — |
| V5 | h21-E00 | 21 | forward experimental before first target session | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-12-18 | 4 | pending completion and publication | — |
| V5 | h21-I01_legacy | 21 | forward experimental before first target session | 2026-11-18T22:51:50.449640+05:30 | 2026-11-18 | 2026-12-18 | 4 | pending completion and publication | — |

The V4 5-session diagnostic resolved at 2026-11-25T18:46:28.060739+05:30. The original reference of 25,387.40 and the completed close of 25,819.25 give a realized return of **1.7010%**. The source match used Published NSE daily OHLC and dated authenticated Upstox one-day OHLC and full quote. [forward/2026-11-25T184420/NSE-2026-11-25.csv](forward/2026-11-25T184420/NSE-2026-11-25.csv)

| version | due | track | model | p | brier | log loss | crps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V4 | 2026-11-25 | Direction | A00_sector | 0.680546 | 0.102051 | 0.384860 | — |
| V4 | 2026-11-25 | Direction | B00_empirical | 0.412698 | 0.344923 | 0.885038 | — |
| V4 | 2026-11-25 | Direction | M05_lgbm | 0.708441 | 0.085006 | 0.344688 | — |
| V4 | 2026-11-25 | Direction | Z_neutral | 0.500000 | 0.250000 | 0.693147 | — |
| V4 | 2026-11-25 | Direction | Z_reversion | 0.450000 | 0.302500 | 0.798508 | — |
| V4 | 2026-11-25 | Distribution | D00_empirical | 0.412698 | 0.344923 | 0.885038 | 0.012749 |
| V4 | 2026-11-25 | Distribution | D03_residual_shrunk | 0.095238 | 0.818594 | 2.351375 | 0.024018 |

The November 25 reference close is 25,819.25. NSE's closed status and dated OHLC match the authenticated Upstox quotes. New reference files contain the actual issue timestamp, quoted guard, exact target sessions, full distribution, source hashes and model settings. The monthly neutral band is an arithmetic price return. Both GJR rows show annualized realized volatility quantiles from their original simulated cash-close paths.

| model | horizon | issue | index close | target | p up | p10 | median | p90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| monthly_neutral_reference | 21 | 2026-11-25T16:56:31.987650+05:30 | 25819.250000 | 2026-12-24 | 0.500000 | -0.045990 | 0.000000 | 0.045990 |
| cash_close_GJR_risk | 5 | 2026-11-25T16:56:31.987650+05:30 | 25819.250000 | 2026-12-02 | — | 0.083130 | 0.145547 | 0.225188 |
| cash_close_GJR_risk | 21 | 2026-11-25T16:56:31.987650+05:30 | 25819.250000 | 2026-12-24 | — | 0.099963 | 0.134767 | 0.204366 |

The native opening-gap and weekly corporate registrations depend on the next session's proper premarket issue window. The monthly directional positioning result remains a candidate for a future locked test. A current same-clock options snapshot was unavailable for a comparable IV panel. The available neutral and GJR references use 2026 sessions exclusively.

[forward-ledger.json](forward-ledger.json) · [forward/alternate-market-receipts.json](forward/alternate-market-receipts.json) · [forward/certification-probes.json](forward/certification-probes.json) · [forward/new-issues.json](forward/new-issues.json) · [forward/monthly-neutral-law.npz](forward/monthly-neutral-law.npz) · [forward/gjr-risk-5.npz](forward/gjr-risk-5.npz) · [forward/gjr-risk-21.npz](forward/gjr-risk-21.npz) · [forward/nse-calendar.pdf](forward/nse-calendar.pdf) · [NSE 2026 cash calendar](https://archives.nseindia.com/content/circulars/CMTR71775.pdf) · [Upstox daily OHLC quote specification](https://upstox.com/developer/api-documentation/get-market-quote-ohlc-v3/)
