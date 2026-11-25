# V2 retrospective backtest

NO STRATEGY QUALIFIED

Only2025–2026performance. Fixed pre2025liquid100cohort; ₹10lakh, noleverage, max3sharedentries/day. Baseline10bps/side ALL-IN friction plus fees; not calibrated live execution. All dates previously research-exposed.

Development-selected: None. Fresh forward observations:0.

| Strategy | Dev return | Val return | Eval return | Full trades | Full return | PF | Net bps | EOD DD | Eval25bps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H5-A-main-long | -2.75% | -3.04% | -0.60% | 48 | -6.27% | 0.20 | -29.70 | 6.45% | -1.45% |
| H5-S-main-long | -3.13% | -4.26% | 0.13% | 54 | -7.13% | 0.18 | -29.15 | 7.37% | -1.21% |
| H4-S-main-long | -4.76% | -1.83% | -2.71% | 81 | -9.04% | 0.52 | -22.25 | 9.46% | -5.56% |
| H5-F-main-long | -4.70% | -4.54% | -0.91% | 60 | -9.85% | 0.12 | -38.07 | 9.94% | -2.41% |
| H4-A-main-long | -4.58% | -5.44% | -4.70% | 91 | -14.01% | 0.47 | -22.00 | 14.72% | -10.16% |
| H4-F-main-long | -6.84% | -4.96% | -6.34% | 110 | -17.07% | 0.47 | -21.66 | 19.57% | -13.07% |
| H1-S-main-long | -11.37% | -6.08% | -10.06% | 312 | -25.14% | 0.55 | -18.37 | 25.70% | -21.91% |
| H1-A-main-long | -15.84% | -12.53% | -17.44% | 374 | -39.23% | 0.47 | -26.24 | 41.38% | -28.89% |
| H2-A-main-long | -20.63% | -26.72% | -26.71% | 698 | -57.37% | 0.47 | -23.73 | 58.39% | -49.49% |
| H2-S-main-long | -24.15% | -28.33% | -30.08% | 758 | -61.99% | 0.43 | -22.98 | 62.58% | -53.84% |
| H1-F-main-long | -32.92% | -24.39% | -31.05% | 617 | -65.03% | 0.45 | -24.89 | 65.15% | -47.61% |
| H2-F-main-long | -33.71% | -29.82% | -40.01% | 835 | -72.09% | 0.38 | -24.10 | 72.42% | -56.47% |

## Limits

- All dates research-exposed; no fresh out-of-sample evidence
- Fixed liquid100 cohort; no all-NSE inference
- Candle fills/partial fills and MIS/circuits unverified
- All-in friction scenarios not live-calibrated; no separate spread double count
- Peer proxy uses dated industry labels, not a historical sector index
- Complete-session coverage is conditional; short special sessions excluded
- Conditional bootstrap does not undo prior research exposure

## Resolution audit

{
  "chosen": 20,
  "matched": 20,
  "selection": "First20 chronological development trades, fixed before evaluation; no outcome-based sample selection",
  "limitation": "Fixed entries/quantities; original completed5m trailing/failure decisions,1m price paths. Not an alternate portfolio or certified fills."
}

Full primary/control/short diagnostics and segments are in metrics.csv/segments.csv; signals/rejections/trades preserve chronology. Failed runs: []
