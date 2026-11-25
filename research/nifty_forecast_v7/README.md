# Reproduce NIFTY V7

The original run is `artifacts/nifty_forecast_v7/2026-11-24/run-001`. `MISSION.md` is the supplied brief. This is a historical research pipeline. It uses earlier artifact directories as inputs and writes inside the V7 directory. `source-audit.json`, `preservation.json`, `intraday-audit.json` and `delivery-manifest.json` identify the input and output bytes.

Use the installed workspace Python environment. From the repository root, verify the delivered run with:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v7.verify --reports
```

For a fresh offline replay, select an unused V7 directory and copy the frozen intraday inputs before fitting. The eight Upstox archive payloads and recorded acquisition times are provided in the original run. The offline replay uses the checked intraday matrix to avoid provider revisions and network access.

```powershell
$env:NIFTY_V7_OUT = 'C:\Users\ME\Desktop\trading-desk\artifacts\nifty_forecast_v7\2026-11-24\replay-001'
New-Item -ItemType Directory -Path $env:NIFTY_V7_OUT
$original = 'artifacts\nifty_forecast_v7\2026-11-24\run-001'
Copy-Item -LiteralPath "$original\intraday-features.csv","$original\intraday-audit.json" -Destination $env:NIFTY_V7_OUT
.venv\Scripts\python.exe -m research.nifty_forecast_v7.reproduce
.venv\Scripts\python.exe -m research.nifty_forecast_v7.features
.venv\Scripts\python.exe -m research.nifty_forecast_v7.experiments
.venv\Scripts\python.exe -m research.nifty_forecast_v7.redundancy
.venv\Scripts\python.exe -m research.nifty_forecast_v7.auxiliary
.venv\Scripts\python.exe -m research.nifty_forecast_v7.integration
.venv\Scripts\python.exe -m research.nifty_forecast_v7.followup
.venv\Scripts\python.exe -m research.nifty_forecast_v7.analyze
.venv\Scripts\python.exe -m research.nifty_forecast_v7.reports
.venv\Scripts\python.exe -m research.nifty_forecast_v7.verify --preserve-only
.venv\Scripts\python.exe -m research.nifty_forecast_v7.verify --reports
```

The optional `intraday` module makes historical market-data requests using the locally configured Upstox analytics credential. The offline replay above uses saved data. The original chronology, initially failed global/integration attempts, corrected plan, and adaptive follow-up specifications are preserved in the original run. `verify` runs fresh fitted replays of three leading weekly configurations in addition to the broader artifact and chronology checks.
