# Reproduce NIFTY V17

Run from the trading-desk root in PowerShell. The acquiring stages use the workspace’s configured read-only historical-data credentials. Reproduction of the frozen vintage uses the archived responses and hashes and requires no new model data after November 17, 2026. The forward command performs a distinct refresh using the execution clock. The `NIFTY_V17_OUT` environment variable can point to another run path under the V17 artifact root. Preserve the original mission in the new run and leave earlier versions in place.

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v17.common
.venv/Scripts/python.exe -m research.nifty_forecast_v17.replay opening
.venv/Scripts/python.exe -m research.nifty_forecast_v17.replay sessions
.venv/Scripts/python.exe -m research.nifty_forecast_v17.replay protect
.venv/Scripts/python.exe -m research.nifty_forecast_v17.acquire sources
.venv/Scripts/python.exe -m research.nifty_forecast_v17.acquire eod
.venv/Scripts/python.exe -m research.nifty_forecast_v17.acquire stocks
.venv/Scripts/python.exe -m research.nifty_forecast_v17.acquire reconcile_cash
.venv/Scripts/python.exe -m research.nifty_forecast_v17.acquire extensions
.venv/Scripts/python.exe -m research.nifty_forecast_v17.recover
.venv/Scripts/python.exe -m research.nifty_forecast_v17.gift
.venv/Scripts/python.exe -m research.nifty_forecast_v17.stocks
.venv/Scripts/python.exe -m research.nifty_forecast_v17.daily_equity
.venv/Scripts/python.exe -m research.nifty_forecast_v17.panel
.venv/Scripts/python.exe -m research.nifty_forecast_v17.network
.venv/Scripts/python.exe -m research.nifty_forecast_v17.residual
.venv/Scripts/python.exe -m research.nifty_forecast_v17.weekly
.venv/Scripts/python.exe -m research.nifty_forecast_v17.paths
.venv/Scripts/python.exe -m research.nifty_forecast_v17.postrisk
.venv/Scripts/python.exe -m research.nifty_forecast_v17.validation
.venv/Scripts/python.exe -m research.nifty_forecast_v17.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v17.acquire forward
.venv/Scripts/python.exe -m research.nifty_forecast_v17.report
.venv/Scripts/python.exe -m research.nifty_forecast_v17.delivery
```

## File layout

- `sources/` retains the underlying authenticated cash and candle responses along with official public documentation and dated probes. Relevant predecessor series are referenced in their original locations.
- `opening-forecasts.csv.gz`, `original-clock-forecasts.csv.gz`, and `residual-*-scores.csv.gz` use each row’s `law` as the atom-array index in their matching NPZ archive. Returns use native log atoms converted to arithmetic ratios for proper scoring. Scalar risk and binary cash-event laws use their native units. The exact smoothed probability is in the score row.
- `timed-paths/`, `convergence-laws/`, and `postopen-paths/` store joint integer OHLC log ticks. Associated manifests link the exact filed clocks, historical source dates, path naming conventions, and hashes.
- `*_receipt`, `*-fits`, `*-cutoff-audit` and `*-baseline-residual-ledger` retain eligibility and fitted-state traces. `*-matched` files show positive gain when candidate loss is lower.
- `forward/` and `forward-ledger.json` use official complete-session outcomes. They do not enter the frozen training panel.
