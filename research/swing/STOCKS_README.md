# Individual stock transfer experiment

This extends the frozen ETF/index research without changing its trading rules.
The 15 ranked ETF/index rows comprise 13 distinct variants. Those 13 rules and
two simpler timing controls are applied to starting-period NIFTY50 constituents.

The fixed window remains 11 November 2024 through 9 November 2026 for direct
comparison with the original experiment. Start membership is read from the dated
11 November 2024 constituent PDF. Later index exits are retained. Forty-five
stocks support comparable whole-period replay; ADANIENT, HINDUNILVR, ITC,
TATAMOTORS and TRENT are quarantined because rights, demergers or fractional
bonus entitlements require an execution/accounting layer not supplied here.

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_stock_swing.py
.\.venv\Scripts\python.exe scripts\run_stock_swing.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_stock_swing.py'
```

Acquisition is read-only, rate limited, and cached. The first download is roughly
2,300 five-minute historical windows plus daily cross-checks. Subsequent runs
reuse local raw files. Existing Upstox analytics-token configuration is loaded
without displaying credentials. First-run constituent extraction additionally
requires `pypdf`; pandas, NumPy and Matplotlib use the existing project runtime.

`stocks.py` reconstructs contemporary share units using NSE split/bonus events
and provider continuity, creates split-neutral indicator inputs, and converts
stops/ATR back into actual units at the historical decision time. Its price-basis
inference is not independent certification of every exchange quote. Liquidity
uses a provider price/volume proxy and is explicitly exploratory.

`stock_engine.py` is a separate fork of the original engine, which is preserved.
It adjusts carried integer quantities and protective prices on split/bonus dates
and attributes cash dividend economic entitlement to overnight holders. Investor
tax/withholding, payment-date cash availability, historical spreads and market
impact are outside this model. No orders are submitted. Partial exits through
split events and fractional entitlements require additional accounting and are
explicitly rejected rather than approximated.

`stock_reporting.py` saves historical pair rankings separately from development-
selected stock lists, later-period transfer evidence, characteristic cutoffs,
common-calendar block uncertainty, search-wide diagnostics and reconciliations.
The continuous trade ledgers include original entry fills/quantities separately
from the share-basis-adjusted entry and position quantity shown after a split.

Outputs: `artifacts/stock_swing_research/report.md`, `pair-leaderboard.csv`,
`stock-summary.csv`, `variant-summary.csv`, `stock-type-results.csv`, all raw
source/audit files, independent sleeve journals, source hashes and verification.
The recorded result is historical stock-specific fit with no pair passing the
joint evidence gate. It does not establish an investment selection rule.
