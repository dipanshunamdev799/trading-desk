# NIFTY V8 research

The supplied research brief is in `MISSION.md`. V8 reads the protected V1–V7 archive tree and writes into `artifacts/nifty_forecast_v8`. The delivered run is `2026-11-24/run-001`. Source acquisition records and SHA-256 hashes are saved alongside the outputs. The available API credentials are used only for historical data access. The study covers retrospective observations from 2025–2026.

From the repository root, verify the delivered run:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v8.verify --reports
```

For a fresh replay, set `NIFTY_V8_OUT` to an unused V8 artifact directory before running. Copy the original `sources` folder into that directory to use the exact FRED payloads offline. The prior V7 intraday payloads and daily archives are read-only inputs. `data` reads existing snapshots and fetches the three FRED files if missing. The command sequence is:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v8.reproduce
.venv\Scripts\python.exe -m research.nifty_forecast_v8.data
.venv\Scripts\python.exe -m research.nifty_forecast_v8.experiments geometry
.venv\Scripts\python.exe -m research.nifty_forecast_v8.invariance
.venv\Scripts\python.exe -m research.nifty_forecast_v8.invariance --sector-alias
.venv\Scripts\python.exe -m research.nifty_forecast_v8.experiments rotation
.venv\Scripts\python.exe -m research.nifty_forecast_v8.experiments distribution
.venv\Scripts\python.exe -m research.nifty_forecast_v8.experiments additional
.venv\Scripts\python.exe -m research.nifty_forecast_v8.global_research
.venv\Scripts\python.exe -m research.nifty_forecast_v8.integration
.venv\Scripts\python.exe -m research.nifty_forecast_v8.experiments monthly
.venv\Scripts\python.exe -m research.nifty_forecast_v8.followup coverage
.venv\Scripts\python.exe -m research.nifty_forecast_v8.followup intermediate
.venv\Scripts\python.exe -m research.nifty_forecast_v8.followup stress
.venv\Scripts\python.exe -m research.nifty_forecast_v8.followup smoothmatch
.venv\Scripts\python.exe -m research.nifty_forecast_v8.analyze
.venv\Scripts\python.exe -m research.nifty_forecast_v8.verify --prior
.venv\Scripts\python.exe -m research.nifty_forecast_v8.figures
.venv\Scripts\python.exe -m research.nifty_forecast_v8.reports
.venv\Scripts\python.exe -m research.nifty_forecast_v8.verify --reports
.venv\Scripts\python.exe -m research.nifty_forecast_v8.pack
```

The original run retains its exploratory registration chronology and the superseded first calibration pass. Replays run the corrected, purged calibration stage. Numeric comparisons are matched by horizon, cohort, model and exact origin. Order of coefficient and law equivalence is verified separately from sample predictive performance. Exact active package versions and artifact hashes are in `delivery-manifest.json`.
