# Community auction experiment

**Exploratory final-auction proxies, not a validated C0-R-X backtest.**

All community data/results are local. PostgreSQL was accessed through server-enforced read-only transactions.

| Archive | Window | Model | Total return | CAGR | Max drawdown | Avg exposure | Ending value (₹) | Filled orders |
|---|---|---|---:|---:|---:|---:|---:|---:|
| tkanhe | 2018-05-11 – 2023-03-31 | reference | 135.24% | 19.13% | -38.53% | 99.7% | 2,352,422 | 1726 |
| tkanhe | 2018-05-11 – 2023-03-31 | coverage_only | 55.40% | 9.44% | -20.98% | 56.1% | 1,554,011 | 856 |
| tkanhe | 2018-05-11 – 2023-03-31 | volume_proxy | 43.63% | 7.69% | -14.77% | 38.2% | 1,436,322 | 527 |
| howutrade | 2022-06-09 – 2024-05-28 | reference | 97.19% | 41.19% | -20.30% | 99.5% | 1,971,921 | 722 |
| howutrade | 2022-06-09 – 2024-05-28 | coverage_only | 91.85% | 39.23% | -18.94% | 97.3% | 1,918,462 | 711 |
| howutrade | 2022-06-09 – 2024-05-28 | volume_proxy | 55.44% | 25.11% | -15.84% | 77.2% | 1,554,358 | 562 |
| howutrade | 2022-06-09 – 2024-05-28 | zero_imbalance_proxy | 22.61% | 10.91% | -6.16% | 33.0% | 1,226,141 | 150 |
| ferozmd53 | 2026-07-01 – 2026-11-13 | reference | 9.28% | 27.15% | -10.00% | 99.0% | 1,092,834 | 111 |
| ferozmd53 | 2026-07-01 – 2026-11-13 | coverage_only | 3.04% | 8.43% | -3.55% | 44.8% | 1,030,382 | 52 |
| ferozmd53 | 2026-07-01 – 2026-11-13 | volume_proxy | 3.04% | 8.43% | -3.55% | 44.8% | 1,030,382 | 52 |

reference = C0-R official-open reference on the same dates; coverage_only = fills only where an archive row exists; volume_proxy = final-volume participation limit; zero_imbalance_proxy = additionally require zero ATO buy-minus-sell.

## Limits

- All proxy variants use final-auction information unavailable at the 09:05 decision; not an executable historical C0-R-X result
- Final volume substitutes for indicative quantity; ATO buy-minus-sell is only an assumed proxy for market imbalance
- Missing/conflicting observations block buys and delay sells; no synthetic fallback fills
- FO category archives cover cash equities eligible for derivatives, not the full momentum universe
- Frozen retained universe/industry labels introduce survivorship and later-information bias
- No dividends, spinoff credits or interest; older corporate actions incompletely audited
- Missing daily prices retain last marks; this reference replay does not enforce the paper worker operational data-pause gate
- No actual fills observed; no forced liquidation of outstanding holdings; windows overlap and are not independent
- Research-only source terms; archives are not guaranteed accurate or complete

## Source coverage

| Archive | Trading sessions | Observed sessions | Reference order intents with archive rows |
|---|---:|---:|---:|
| tkanhe | 1213 | 1197 | 702 / 1821 |
| howutrade | 488 | 482 | 717 / 758 |
| ferozmd53 | 95 | 94 | 40 / 117 |

Incomplete price sessions in each test (last marks retained; paper processing would pause):

```json
{
  "tkanhe": [
    {
      "session": "2018-11-07",
      "missing": 297,
      "required": 300
    },
    {
      "session": "2018-11-09",
      "missing": 2,
      "required": 23
    }
  ],
  "howutrade": [],
  "ferozmd53": []
}
```

## Fixed sensitivity checks

| Archive | Proxy | Participation | Cost/side | Total return | Max drawdown |
|---|---|---:|---:|---:|---:|
| tkanhe | volume_proxy | 1% | 0.225% | 16.06% | -10.31% |
| tkanhe | volume_proxy | 5% | 0.225% | 45.09% | -14.31% |
| tkanhe | volume_proxy | 10% | 0.450% | 34.93% | -16.53% |
| howutrade | volume_proxy | 1% | 0.225% | 28.05% | -12.44% |
| howutrade | volume_proxy | 5% | 0.225% | 51.90% | -15.64% |
| howutrade | volume_proxy | 10% | 0.450% | 44.72% | -17.15% |
| howutrade | zero_imbalance_proxy | 1% | 0.225% | 26.57% | -7.87% |
| howutrade | zero_imbalance_proxy | 5% | 0.225% | 24.02% | -5.45% |
| howutrade | zero_imbalance_proxy | 10% | 0.450% | 21.07% | -6.62% |
| ferozmd53 | volume_proxy | 1% | 0.225% | 2.76% | -4.08% |
| ferozmd53 | volume_proxy | 5% | 0.225% | 3.02% | -3.57% |
| ferozmd53 | volume_proxy | 10% | 0.450% | 2.48% | -3.93% |
