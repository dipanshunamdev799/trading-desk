# Reproduce NIFTY V20

Run from the trading-desk root using the existing research Python environment. Historical inputs are frozen from January 2025 through November 17, 2026. Preserve captured forward issues when replaying and run acquisition and forward commands only to intentionally refresh those lanes. Forward outcomes and genuine issue timestamps are separate from historical experiments.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OPENBLAS_NUM_THREADS='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v20.common
.venv/Scripts/python.exe -m research.nifty_forecast_v20.audit protect
.venv/Scripts/python.exe -m research.nifty_forecast_v20.audit replay
.venv/Scripts/python.exe -m research.nifty_forecast_v20.panel
.venv/Scripts/python.exe -m research.nifty_forecast_v20.acquisition
.venv/Scripts/python.exe -m research.nifty_forecast_v20.acquisition --cdsl
.venv/Scripts/python.exe -m research.nifty_forecast_v20.lifetime
.venv/Scripts/python.exe -m research.nifty_forecast_v20.native
.venv/Scripts/python.exe -m research.nifty_forecast_v20.joint
.venv/Scripts/python.exe -m research.nifty_forecast_v20.late_window
.venv/Scripts/python.exe -m research.nifty_forecast_v20.risk
.venv/Scripts/python.exe -m research.nifty_forecast_v20.forward
.venv/Scripts/python.exe -m research.nifty_forecast_v20.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v20.registry
.venv/Scripts/python.exe -m research.nifty_forecast_v20.framework
.venv/Scripts/python.exe -m research.nifty_forecast_v20.report
.venv/Scripts/python.exe -m research.nifty_forecast_v20.delivery
```

The [research index](NIFTY_V20_RESEARCH.md) links the reports. The [SHA-256 manifest](manifest.json) binds sources, cases, paths and code to the finished run.
