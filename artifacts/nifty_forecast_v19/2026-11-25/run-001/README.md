# Reproduce NIFTY V19

Run from the trading-desk workspace root with the existing research environment and V11–V18 artifacts. V19 writes to its own dated run directory. Sources are public archive data except the authenticated read-only Upstox quote references. To regenerate the historical research from the retained snapshots, omit the archive-fetch and forward-refresh commands. The source receipts record expected or failed alternative retrievals separately.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OPENBLAS_NUM_THREADS='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v19.common
.venv/Scripts/python.exe -m research.nifty_forecast_v19.acquire
.venv/Scripts/python.exe -m research.nifty_forecast_v19.acquire alternatives
.venv/Scripts/python.exe -m research.nifty_forecast_v19.baseline replay
.venv/Scripts/python.exe -m research.nifty_forecast_v19.baseline protect
.venv/Scripts/python.exe -m research.nifty_forecast_v19.database
.venv/Scripts/python.exe -m research.nifty_forecast_v19.features
.venv/Scripts/python.exe -m research.nifty_forecast_v19.flows
.venv/Scripts/python.exe -m research.nifty_forecast_v19.forecast
.venv/Scripts/python.exe -m research.nifty_forecast_v19.risk
.venv/Scripts/python.exe -m research.nifty_forecast_v19.structure
.venv/Scripts/python.exe -m research.nifty_forecast_v19.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v19.native_controls
.venv/Scripts/python.exe -m research.nifty_forecast_v19.forward --reuse-refresh
.venv/Scripts/python.exe -m research.nifty_forecast_v19.report
.venv/Scripts/python.exe -m research.nifty_forecast_v19.delivery
```

Review [the research index](NIFTY_V19_RESEARCH.md) and [manifest](manifest.json). Each NPZ is keyed by its corresponding score table, receipt or origin-specific filename. The timing assumptions and benchmarks were locked before scoring, and prior model laws are verified against their hashes. The freeze date excludes later sessions from every historical result. Current observations and any original target resolutions belong to the [forward ledger](V19_FORWARD_RESEARCH_LEDGER.md).
