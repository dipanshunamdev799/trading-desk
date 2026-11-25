# Reproduce NIFTY V14

Use the repository virtual environment from the repository root. Set NIFTY_V14_OUT to a fresh subdirectory of the V14 artifact tree and copy the original MISSION.md into that directory. V14 reads the frozen Upstox, NSE and related archives from earlier runs. All generated V14 files stay beneath the new run directory. The daily OHLC scenario archive records prices as fixed-point log returns relative to the origin close, in open, high, low, close order. For the joint_pit model, pair path_mixture paths with joint_pit_weights. For all other model arrays, each row has equal mass. Multiply the integer array by the archive tick to obtain log prices.

~~~powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.data
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.replay protect
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.replay replay
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.volatility point
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.volatility process
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.generation
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.signals
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.path_score
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.endpoint endpoint
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.endpoint intervals
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.diagnostics anatomy
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.diagnostics simulation
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.diagnostics null
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.evaluate
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.forensics
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.verify check
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.report
.\.venv\Scripts\python.exe -m research.nifty_forecast_v14.verify deliver
~~~

[Study index](NIFTY_V14_RESEARCH.md) · [Registered design](registration.json) · [Archived joint laws](joint-path-ledger.json) · [Verification](verification.json).
