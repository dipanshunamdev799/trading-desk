# V16 Validation and falsification

V16 independently checked **68,390** eligibility timestamps in the decision panels, including earlier domestic quote times, foreign session marks, intraday closes and delayed GIFT controls. The pre-auction tape is separate from the during-auction 09:10 observation. The same-morning audit covers official label identity, exchange-clock changes, minute bar end-plus-buffer, holidays, missing or nonstandard sessions, the expiry guard, alternative prior reference marks, large gaps and month deletions. The largest status risks for GIFT are the absence of per-contract IDs and historical quote-receipt timestamps. The chronological training masks require every model outcome to finish before the decision trading date. Priors, scalers, shrinkage, rank truncation and calibration estimate from earlier labeled data. At issue the monthly 21-session residual model cannot see any realized future gap, sector return or offshore price.

## Alternate age, source removal, noise and shuffled controls

| candidate | control | n | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gift_delay10 | gift_raw | 248 | 0.101678 | 0.100841 | -0.000836 | -0.005267 | 0.003595 |
| gift_delay25 | gift_raw | 248 | 0.104765 | 0.100841 | -0.003923 | -0.013384 | 0.005538 |
| gift_roll_screened | gift_raw | 180 | 0.095052 | 0.097792 | 0.002740 | -0.002078 | 0.007557 |
| noisy_foreign | six_cash | 258 | 0.257884 | 0.225079 | -0.032805 | -0.077667 | 0.012057 |
| shuffled_foreign | six_cash | 258 | 0.261665 | 0.225079 | -0.036586 | -0.083938 | 0.010765 |
| without_dax | six_cash | 258 | 0.223650 | 0.225079 | 0.001429 | -0.001947 | 0.004805 |
| without_dow | six_cash | 258 | 0.235426 | 0.225079 | -0.010347 | -0.017805 | -0.002890 |
| without_ftse | six_cash | 258 | 0.223524 | 0.225079 | 0.001555 | -0.002950 | 0.006061 |
| without_hsi | six_cash | 258 | 0.225033 | 0.225079 | 0.000046 | -0.005638 | 0.005730 |
| without_nikkei | six_cash | 258 | 0.223148 | 0.225079 | 0.001931 | -0.013348 | 0.017209 |
| without_spx | six_cash | 258 | 0.226707 | 0.225079 | -0.001629 | -0.012122 | 0.008865 |

## Calendar and unusual-gap cuts for the raw vendor signal

| case filter | n | loss | base | gain |
| --- | --- | --- | --- | --- |
| all | 248 | 0.100841 | 0.233717 | 0.132876 |
| ordinary | 248 | 0.100841 | 0.233717 | 0.132876 |
| no_large_gaps | 229 | 0.109204 | 0.238798 | 0.129594 |
| non_roll | 180 | 0.097792 | 0.236406 | 0.138614 |
| holiday_or_special | 16 | 0.118220 | 0.233170 | 0.114950 |
| strict_ordinary_non_roll | 170 | 0.094003 | 0.237271 | 0.143268 |

## Influence of omitted dates

| control | deletion | cases | lowest Brier gain | highest Brier gain | lowest CRPS gain |
| --- | --- | --- | --- | --- | --- |
| asia_partial | calendar_month | 13 | 0.101317 | 0.118564 | 0.001128 |
| asia_partial | large_gap_episode | 10 | 0.104653 | 0.110987 | 0.001277 |
| equal_six | calendar_month | 13 | 0.127145 | 0.139066 | 0.001304 |
| equal_six | large_gap_episode | 10 | 0.130652 | 0.135153 | 0.001466 |
| single_US | calendar_month | 13 | 0.117528 | 0.133802 | 0.001308 |
| single_US | large_gap_episode | 10 | 0.123392 | 0.125561 | 0.001449 |
| six_cash | calendar_month | 13 | 0.117245 | 0.133848 | 0.001263 |
| six_cash | large_gap_episode | 10 | 0.123664 | 0.126974 | 0.001396 |

## Pre-registered shared endpoints and future-state checks

| horizon | origin | decision | archive equal | future unchanged | fit equal | clone exact | laws |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 2025-10-14 | 2025-10-15 | Yes | Yes | Yes | Yes | 10 |
| 5 | 2026-04-29 | 2026-04-30 | Yes | Yes | Yes | Yes | 10 |
| 5 | 2026-09-22 | 2026-09-23 | Yes | Yes | Yes | Yes | 10 |
| 21 | 2025-12-01 | 2025-12-02 | Yes | Yes | Yes | Yes | 10 |
| 21 | 2026-05-12 | 2026-05-13 | Yes | Yes | Yes | Yes | 10 |
| 21 | 2026-09-07 | 2026-09-08 | Yes | Yes | Yes | Yes | 10 |

## Representative re-fit and re-selection with shuffled foreign blocks

| target | n origins | challengers | refit draws | observed best | null median | null 95 | null tail |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gap | 23 | 3 | 39 | 0.048443 | 0.001675 | 0.011727 | 0.025000 |
| five | 23 | 3 | 39 | 0.005019 | 0.002352 | 0.009904 | 0.300000 |
| twentyone | 23 | 3 | 39 | -0.002042 | 0.004858 | 0.019982 | 0.875000 |

The refit null uses earlier labels, fixed domestic anchors, 23 thinned dates and 39 block-shuffled refits, reselecting among three models per draw. The gap result is bounded by that discrete test design and all historical research exposures. Pairwise comparisons use 1,500 circular block resamples at lengths 5, 10, 21, 42. The 10- and 21-session adjusted bands use the maximum standardized contrast within each recorded family. Across the 482 original endpoint dates, **53** weekly and **11** monthly windows were disjoint. Verification reloaded **616** V15 artifact hashes and **18** unchanged V15 source files, preserving V15’s earlier receipt of **23,060** hashes. The comparisons remain exposed to choices accumulated across V1–V16.

[Decision timestamp verification](point-in-time-verification.json) · [Future perturbation checks](no-future-and-copy-verification.json) · [V15 protection](predecessor-protection.json) · [Null fit outputs](refit-null-forecasts.csv.gz) · [Open-gap date sensitivities](opening-gap-deletion.csv) · [Validation and archive integrity receipt](validation-receipt.json)
