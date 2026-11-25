# Reproduce V15

Run from the trading-desk repository in PowerShell with the existing Python environment and archived market sources. The authenticated acquisition commands expect the read-only Upstox access already configured by the workspace. The protected archive manifests are read-only. Sources and results remain inside this V15 run. To replay into an isolated run, set NIFTY_V15_OUT under artifacts/nifty_forecast_v15 first and copy the mission to that run.

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v15.replay scores
.venv/Scripts/python.exe -m research.nifty_forecast_v15.replay protect
.venv/Scripts/python.exe -m research.nifty_forecast_v15.sources intraday
.venv/Scripts/python.exe -m research.nifty_forecast_v15.sources forward
.venv/Scripts/python.exe -m research.nifty_forecast_v15.data
.venv/Scripts/python.exe -m research.nifty_forecast_v15.sequential
.venv/Scripts/python.exe -m research.nifty_forecast_v15.scores
.venv/Scripts/python.exe -m research.nifty_forecast_v15.sessions
.venv/Scripts/python.exe -m research.nifty_forecast_v15.volatility
.venv/Scripts/python.exe -m research.nifty_forecast_v15.forensics
.venv/Scripts/python.exe -m research.nifty_forecast_v15.mechanisms
.venv/Scripts/python.exe -m research.nifty_forecast_v15.mechanical
.venv/Scripts/python.exe -m research.nifty_forecast_v15.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v15.comparisons
.venv/Scripts/python.exe -m research.nifty_forecast_v15.demo
.venv/Scripts/python.exe -m research.nifty_forecast_v15.verify
.venv/Scripts/python.exe -m research.nifty_forecast_v15.report
.venv/Scripts/python.exe -m research.nifty_forecast_v15.delivery
```

The main score job evaluates all forecast checkpoints and eligible barrier survivors. Path archives store integer log OHLC ratios against the latest cash close. Reconstruct each updated joint law by converting the ticks using the manifest scale and multiplying by the cash-anchor ratio, then prepending the realized OHLC history from the original issue. The frozen law uses the immutable prior NPZ and the model key recorded in every per-window receipt. Some weak and earlier systems have shorter support. Interpret metrics from common-origin comparisons and refer to the checkpoint codes for the corresponding remaining horizon.

Archived research definitions retain the exact 2025–2026 domain and the November 17 frozen timeline. The additional completed-session refresh is timestamped separately and can be run again without changing the historical evidence. Prospective score status derives from the original issue, original session list and authoritative outcome.
