# NIFTY V17 — New information discovery

The largest new timed source is NSE company announcements. The retained downloads contain **176,022** 2025 rows and **169,204** 2026 rows through the frozen vintage. The audit retained **748** tagged exchange publications for the basket. The usable timestamp is exchange dissemination plus five minutes, distinct from the company filing timestamp and the underlying event date. Models use counts of results, board schedule notices, corporate actions and financial-sector publications. A later result does not reconstruct any historical earnings expectation. Official EOD cash turnover and the exchange’s published EQ series provide trailing eligible input. Historical index-change notices and reconstitution policy are useful for membership audits. The study lacked a complete daily point-in-time member/weight panel and an authenticated historical auction tape.

| name | status | bytes | file |
| --- | --- | --- | --- |
| nse-preopen | 200 | 360720.000000 | sources/source-probes/nse-preopen.bin |
| nse-eod | 200 | 320326.000000 | sources/source-probes/nse-eod.bin |
| nse-index-method | 200 | 652279.000000 | sources/source-probes/nse-index-method.bin |
| nse-holiday | 200 | 176256.000000 | sources/source-probes/nse-holiday.bin |
| nse-actions | 200 | 369162.000000 | sources/source-probes/nse-actions.bin |
| nse-announcements | 200 | 406100.000000 | sources/source-probes/nse-announcements.bin |
| nse-bulk-block | 200 | 327521.000000 | sources/source-probes/nse-bulk-block.bin |
| nse-institutional | 200 | 308183.000000 | sources/source-probes/nse-institutional.bin |
| nse-index-dated | 200 | 79518.000000 | sources/source-probes/nse-index-dated.bin |
| upstox-candle | 200 | 656256.000000 | sources/source-probes/upstox-candle.bin |
| upstox-expired | 200 | 44964.000000 | sources/source-probes/upstox-expired.bin |
| upstox-live-depth | 200 | 240705.000000 | sources/source-probes/upstox-live-depth.bin |
| nseix-dated-contracts | 200 | 5498.000000 | sources/source-probes/nseix-dated-contracts.bin |
| corporate-action-2025 | 200 | 70196.000000 | sources/source-probes/corporate-action-2025.json.gz |
| announcements-2025 | 200 | 19472984.000000 | sources/source-probes/announcements-2025.json.gz |
| corporate-action-2026 | 200 | 73646.000000 | sources/source-probes/corporate-action-2026.json.gz |
| announcements-2026 | 200 | 19394911.000000 | sources/source-probes/announcements-2026.json.gz |
| fii-dii-history | 200 | 308183.000000 | sources/source-probes/fii-dii-history.bin |
| bulk-sample | 404 | — | — |
| block-sample | 404 | — | — |
| nifty-expiries | 401 | — | — |
| nifty-future-october | 401 | — | — |

The FII/DII probe returned the public report HTML, with the same byte count as the dated-history attempt. Historical bulk and block sample URLs returned 404. The cash archive and previous versions retain matched EOD derivatives, expiry, OI and option-surface data with previous-date guards. Upstox expired-instrument HTTP 401 limits new dated stock futures. The GIFT alias and prior V16 public futures/sector sources have independent timestamp and roll coverage diagnostics. Historical quote, depth, auction and full contract files need authenticated historical entitlement and timestamps. Revision risk remains for downloaded historical archives. The probes and cash/stock receipts retain source checksums, retrieval clocks and raw responses for verification.

| cutoff | target | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | r30 | announcements_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.251146 | 0.248972 | -0.002174 | -0.005107 | 0.000760 |
| 09:25 | r30 | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001266 | 0.001256 | -9.89e-06 | -0.000019 | -5.25e-07 |
| 09:25 | regular_residual | announcements_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.248768 | 0.247995 | -0.000773 | -0.003027 | 0.001481 |
| 09:25 | regular_residual | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.003540 | 0.003528 | -0.000012 | -0.000032 | 8.91e-06 |
| 09:25 | remaining_21 | announcements_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.302524 | 0.289840 | -0.012684 | -0.053785 | 0.028417 |
| 09:25 | remaining_21 | announcements_residual | frozen_parent_residual_history | crps | 238 | 12 | 0.031336 | 0.029515 | -0.001821 | -0.004634 | 0.000993 |
| 09:25 | remaining_5 | announcements_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.241083 | 0.239042 | -0.002041 | -0.008970 | 0.004887 |
| 09:25 | remaining_5 | announcements_residual | frozen_parent_residual_history | crps | 253 | 51 | 0.010783 | 0.010693 | -0.000090 | -0.000291 | 0.000111 |
| 09:25 | remaining_range | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002330 | 0.002238 | -0.000092 | -0.000233 | 0.000050 |
| 09:25 | remaining_vol | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.001035 | 0.000989 | -0.000046 | -0.000124 | 0.000032 |
| 10:20 | r30 | announcements_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.262082 | 0.260102 | -0.001980 | -0.004767 | 0.000807 |
| 10:20 | r30 | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000817 | 0.000813 | -4.12e-06 | -0.000010 | 1.88e-06 |
| 10:20 | regular_residual | announcements_residual | frozen_parent_residual_history | brier | 257 | 257 | 0.249080 | 0.247850 | -0.001230 | -0.005950 | 0.003490 |
| 10:20 | regular_residual | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002933 | 0.002921 | -0.000012 | -0.000033 | 9.89e-06 |
| 10:20 | remaining_21 | announcements_residual | frozen_parent_residual_history | brier | 238 | 12 | 0.302205 | 0.286803 | -0.015401 | -0.059207 | 0.028405 |
| 10:20 | remaining_21 | announcements_residual | frozen_parent_residual_history | crps | 238 | 12 | 0.030826 | 0.028955 | -0.001872 | -0.004753 | 0.001010 |
| 10:20 | remaining_5 | announcements_residual | frozen_parent_residual_history | brier | 253 | 51 | 0.254100 | 0.250678 | -0.003422 | -0.010305 | 0.003461 |
| 10:20 | remaining_5 | announcements_residual | frozen_parent_residual_history | crps | 253 | 51 | 0.010790 | 0.010695 | -0.000095 | -0.000271 | 0.000082 |
| 10:20 | remaining_range | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.002137 | 0.002043 | -0.000093 | -0.000237 | 0.000051 |
| 10:20 | remaining_vol | announcements_residual | frozen_parent_residual_history | crps | 257 | 257 | 0.000921 | 0.000888 | -0.000033 | -0.000101 | 0.000036 |

[Audit of source and history probes](new-source-availability.json) · [Auditable announcement dissemination times](announcement-availability.csv.gz) · [Cash turnover and identities](official-equity-receipt.json) · [NSE announced index reconstitutions](https://www.niftyindices.com/resources/index-reconstitution) · [NSE historical data inventory](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf)
