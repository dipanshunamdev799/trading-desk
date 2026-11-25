# Reproduce V21

Run from the trading-desk root using the existing project environment. The forward module intentionally refreshes separately observed inputs and outcomes.

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:OPENBLAS_NUM_THREADS = "1"
.venv/Scripts/python.exe -m research.nifty_forecast_v21.common
.venv/Scripts/python.exe -m research.nifty_forecast_v21.acquire
.venv/Scripts/python.exe -m research.nifty_forecast_v21.reference
.venv/Scripts/python.exe -m research.nifty_forecast_v21.universe
.venv/Scripts/python.exe -m research.nifty_forecast_v21.reconstruction
.venv/Scripts/python.exe -m research.nifty_forecast_v21.panel
.venv/Scripts/python.exe -m research.nifty_forecast_v21.learning
.venv/Scripts/python.exe -m research.nifty_forecast_v21.joint
.venv/Scripts/python.exe -m research.nifty_forecast_v21.risk
.venv/Scripts/python.exe -m research.nifty_forecast_v21.power
.venv/Scripts/python.exe -m research.nifty_forecast_v21.specialization
.venv/Scripts/python.exe -m research.nifty_forecast_v21.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v21.forward
.venv/Scripts/python.exe -m research.nifty_forecast_v21.report
.venv/Scripts/python.exe -m research.nifty_forecast_v21.verify
```

The [research index](NIFTY_V21_RESEARCH.md) links the exact reports and the [manifest](manifest.json) binds reproducible data and code.
