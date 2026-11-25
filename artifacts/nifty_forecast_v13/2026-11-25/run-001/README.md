# Reproduce V13

Use the repository Python environment. Set NIFTY_V13_OUT to a new directory under the V13 artifact tree and copy the mission first. Each command below runs from the repository root. Read-only refreshes are separate from the frozen model inputs. Supplemental source acquisition follows the pre-registered core models.

~~~powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.acquire
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.data
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.volatility protect
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.volatility replay
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.volatility risk
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.paths
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.legacy
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.supplement
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.controls
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.evaluate
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.verify fits
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.verify refresh
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.verify check
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.report
.\.venv\Scripts\python.exe -m research.nifty_forecast_v13.verify delivery
~~~

[Registration](initial-registry.json) · [Research reports](NIFTY_V13_RESEARCH.md).
