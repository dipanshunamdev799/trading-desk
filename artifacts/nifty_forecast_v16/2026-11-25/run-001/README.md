# Reproduce the V16 research

Run the following commands from the trading-desk root in PowerShell with the existing configured read-only Upstox analytics credential. The dated outputs remain under the V16 root. Set NIFTY_V16_OUT within artifacts/nifty_forecast_v16 for a different run and place a copy of the mission there. Preserve the saved receipts and fixed data files when reproducing the frozen historical results. The forward command deliberately refreshes separately using the execution timestamp.

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v16.common
.venv/Scripts/python.exe -m research.nifty_forecast_v16.acquire sources
.venv/Scripts/python.exe -m research.nifty_forecast_v16.acquire intraday
.venv/Scripts/python.exe -m research.nifty_forecast_v16.acquire forward
.venv/Scripts/python.exe -m research.nifty_forecast_v16.replay gap
.venv/Scripts/python.exe -m research.nifty_forecast_v16.replay protect
.venv/Scripts/python.exe -m research.nifty_forecast_v16.data
.venv/Scripts/python.exe -m research.nifty_forecast_v16.session_models opening
.venv/Scripts/python.exe -m research.nifty_forecast_v16.session_models decay
.venv/Scripts/python.exe -m research.nifty_forecast_v16.transmission
.venv/Scripts/python.exe -m research.nifty_forecast_v16.absorption
.venv/Scripts/python.exe -m research.nifty_forecast_v16.volatility
.venv/Scripts/python.exe -m research.nifty_forecast_v16.paths
.venv/Scripts/python.exe -m research.nifty_forecast_v16.validation clock
.venv/Scripts/python.exe -m research.nifty_forecast_v16.validation offshore
.venv/Scripts/python.exe -m research.nifty_forecast_v16.validation docs
.venv/Scripts/python.exe -m research.nifty_forecast_v16.validation null
.venv/Scripts/python.exe -m research.nifty_forecast_v16.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v16.extra_comparisons
.venv/Scripts/python.exe -m research.nifty_forecast_v16.report
.venv/Scripts/python.exe -m research.nifty_forecast_v16.delivery
```

Session distribution files archive the row-indexed log-return atoms. The row's law field gives the atom-array position. Per-case metrics use arithmetic ratios except for the direct archived V15 log-return reproduction and realized risk outcomes. The joint archives contain integer OHLC log ticks relative to the original official cash close, with separate simulated state diagnostics. The path manifest records the scale and predecessor pointers. The separate forward ledger preserves exact original target dates and issue hashes.
