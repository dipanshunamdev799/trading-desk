# Reproduce NIFTY V9

`MISSION.md` contains the supplied brief. The delivered historical run is `artifacts/nifty_forecast_v9/2026-11-24/run-001`. Inputs from earlier versions are read-only. Every output lives inside the V9 artifact directory, except its top-level index. The separate 2026 refresh was acquired for matured endpoint scoring only.

From the repository root, verify the completed run:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v9.verify --reports
```

To rebuild, set `NIFTY_V9_OUT` to a fresh path under `artifacts/nifty_forecast_v9`. For an offline replay copy `acquired-candles.csv`, `source-overlap.csv`, `acquisition.json`, and `market-sources` from the original V9 run into that output folder. These copies retain the original endpoint dates and receipt times. Running `acquire` instead makes historical read-only requests and can return newer sessions and revised source data. Run the modules in this order:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v9.reproduce
.venv\Scripts\python.exe -m research.nifty_forecast_v9.features
.venv\Scripts\python.exe -m research.nifty_forecast_v9.run_models learning
.venv\Scripts\python.exe -m research.nifty_forecast_v9.run_models base
.venv\Scripts\python.exe -m research.nifty_forecast_v9.run_models adapt
.venv\Scripts\python.exe -m research.nifty_forecast_v9.run_models information
.venv\Scripts\python.exe -m research.nifty_forecast_v9.run_models monthly
.venv\Scripts\python.exe -m research.nifty_forecast_v9.paths
.venv\Scripts\python.exe -m research.nifty_forecast_v9.extended
.venv\Scripts\python.exe -m research.nifty_forecast_v9.reliability
.venv\Scripts\python.exe -m research.nifty_forecast_v9.temporal
.venv\Scripts\python.exe -m research.nifty_forecast_v9.search_audit
.venv\Scripts\python.exe -m research.nifty_forecast_v9.duplicate_replay
.venv\Scripts\python.exe -m research.nifty_forecast_v9.analyze
.venv\Scripts\python.exe -m research.nifty_forecast_v9.combined_uncertainty
.venv\Scripts\python.exe -m research.nifty_forecast_v9.verify --prior
.venv\Scripts\python.exe -m research.nifty_forecast_v9.figures
.venv\Scripts\python.exe -m research.nifty_forecast_v9.reports
.venv\Scripts\python.exe -m research.nifty_forecast_v9.verify --reports
.venv\Scripts\python.exe -m research.nifty_forecast_v9.pack
```

The original path registry before a corrected function call is retained separately. Insufficient fitting histories remain in fold ledgers. `verify` independently refits 276 forecasts with sentinel future labels and checks the archived path simulations, complete laws and earlier artifacts. `delivery-manifest.json` gives content checksums and actual Python package versions.
