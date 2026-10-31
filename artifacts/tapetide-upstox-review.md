# Tapetide versus our Upstox data

Verified 2026-10-24 (America/Los_Angeles). Read-only calls; no application integration changes. Credentials are excluded from artifacts.

## Price history
- Nifty 50: 64 daily bars, July 23–October 23, 2026. All OHLC values agree within 0.011 index points; no missing dates on either side.
- Reliance, TCS and HDFC Bank: 14 daily bars each, October 5–23, 2026. All OHLC values agree within INR 0.011; volumes agree exactly; no missing dates on either side.
- Total: 106 bars, 466 field comparisons, no mismatches at those tolerances.
- Latest quotes for all three stocks agree on price, volume, previous close and absolute change (floating point rounding allowed). These are closed-market observations, not a test of intraday latency.

## Nifty options
Session October 23, expiry October 27, 2026. Tapetide snapshot: 10:00 UTC / 15:30 IST. Upstox dated daily analytics include later observations (max-pain insights end at 15:40 IST); exact OI capture-time equivalence is not established.

| Field | Tapetide | Upstox |
|---|---:|---:|
| Spot | 22,600 | 22,600 |
| Max pain | 22,700 | 22,700 |
| Total call OI | 269,964,500 | 270,037,105 |
| Total put OI | 199,557,085 | 199,282,655 |
| PCR | 0.7392 | 0.7379824895 |

- Call OI differs by -0.0269%; put OI by +0.1377%.
- 37 of 38 returned strike legs differ in OI. At strike 22,600, call OI is 6,315,335 versus 5,635,370 (+12.07%). Therefore small aggregate differences conceal larger strike-level differences.
- Tapetide PCR recomputes correctly from its own full-expiry OI totals, rounded to four decimal places.
- Independently minimizing expiry payout using the entire returned Upstox OI ladder gives max pain 22,700.
- Tapetide returns a truncated 19-strike ladder, while its totals describe the full chain. Do not compute whole-chain PCR or max pain from that displayed subset.
- These differences do not establish which provider is wrong: timestamps, source and settlement revisions need to be aligned. IV/Greeks and individual premiums have not been independently verified.

## Institutional flows
- FII: 16 overlapping dated cash-flow records; 0 buy/sell/net mismatches at INR 0.011 crore tolerance.
- DII: 16 overlapping dated cash-flow records; 0 buy/sell/net mismatches at INR 0.011 crore tolerance.

Upstox returned observations before October 1 for the supplied from_date, so only actual overlapping dates were compared; this does not verify the latest October flows.

## Conclusion
The sampled prices and volumes agree with our Upstox source. Options agree on spot and max pain, but OI/PCR are not interchangeable without resolving snapshot timing and source differences. This sample does not validate the entire stock universe, fundamentals, corporate-action adjustments, IV/Greeks, historical backtest safety or live freshness.

Raw responses and detailed differences: tapetide-upstox-comparison.json. Reproducible probe: verify_tapetide.py (token supplied on stdin).
