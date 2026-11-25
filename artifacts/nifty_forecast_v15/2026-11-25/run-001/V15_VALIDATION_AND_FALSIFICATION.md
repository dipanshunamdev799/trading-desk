# V15 chronology and falsification

Verified **482** archived fixed windows, **5,882** cutoff/target identities, **147,050** updated joint laws, **23,528** fit receipts, **8,463** tenor-availability rows and **1,323,450** order rows. 3,950 sampled saved laws independently passed shape, price positivity and OHLC bounds after all laws were checked at generation. The archive check verified 265 distinct immutable V14 scenario files plus SHA-256 for every V15 joint archive. 23,060 predecessor file hashes match. The valid scope starts in 2025. A fit's latest label end precedes the decision's cash as-of session. Training-only scales, medians, support deduplication and bootstrap pair matching all retain the same chronology.

## Sentinel tests

| horizon | checkpoint | asof | future prices and inputs changed | unobserved historical labels and paths perturbed | trained coefficients identical | exact clones removed | archive exact | total model laws compared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 0 | 2026-10-15 | Yes | Yes | Yes | Yes | Yes | 25 |
| 5 | 2 | 2026-10-19 | Yes | Yes | Yes | Yes | Yes | 25 |
| 5 | 4 | 2026-10-22 | Yes | Yes | Yes | Yes | Yes | 25 |
| 21 | 0 | 2026-10-15 | Yes | Yes | Yes | Yes | Yes | 25 |
| 21 | 5 | 2026-10-23 | Yes | Yes | Yes | Yes | Yes | 25 |
| 21 | 10 | 2026-10-30 | Yes | Yes | Yes | Yes | Yes | 25 |
| 21 | 20 | 2026-11-13 | Yes | Yes | Yes | Yes | Yes | 25 |

## Block-shuffled refit and reselection

| horizon | origins | refitted draws | candidate slots | selected observed | null max mean | null max q95 | monte carlo tail |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 19 | 32 | 4 | 0.010925 | 0.008865 | 0.027544 | 0.393939 |
| 21 | 19 | 32 | 4 | -0.029742 | -0.019339 | -0.004135 | 0.878788 |

The refit null permutes contiguous training blocks of the additional feature groups, refits standardized ridge slopes and reselects among four issue/update slots. It uses a 19-origin grid and 32 randomized fits per horizon. The Monte Carlo result is a diagnostic. Ordinary paired intervals, sensitivity to block length, dependency and selection-adjusted bands retain their own columns. Delayed, stale, randomized and noisy update models use the original as-of baseline. Exact-copy invariance is checked after perturbing unavailable historical targets, market features, maturities and future cash observations. The V15 search adjustments do not account for all choices across V1–V15.

[Verification receipt](validation-receipt.json) [Pre-score registration](registration.json) [Immutable predecessor receipt](protected-receipt.json) [Refit null realized paths](refit-reselection-null.csv.gz) [All first-passage shape and risk set counts](sequential-score-counts.json)
