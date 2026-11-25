# Reproduce NIFTY V18

Run from the trading-desk workspace in PowerShell. The fixed research vintage ends on **2026-11-17**. Published data and receipts archived by V17 are dependencies and remain in their original locations. The authenticated read-only forward refresh runs independently. Preserve MISSION.md in the chosen V18 output directory.

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v18.common
.venv/Scripts/python.exe -m research.nifty_forecast_v18.baseline replay
.venv/Scripts/python.exe -m research.nifty_forecast_v18.baseline protect
.venv/Scripts/python.exe -m research.nifty_forecast_v18.baseline native_paths
.venv/Scripts/python.exe -m research.nifty_forecast_v18.inventory
.venv/Scripts/python.exe -m research.nifty_forecast_v18.sources additional
.venv/Scripts/python.exe -m research.nifty_forecast_v18.macro
.venv/Scripts/python.exe -m research.nifty_forecast_v18.fundamentals
.venv/Scripts/python.exe -m research.nifty_forecast_v18.events
.venv/Scripts/python.exe -m research.nifty_forecast_v18.events intraday
.venv/Scripts/python.exe -m research.nifty_forecast_v18.attachments
.venv/Scripts/python.exe -m research.nifty_forecast_v18.attachments compare
.venv/Scripts/python.exe -m research.nifty_forecast_v18.aggregate
.venv/Scripts/python.exe -m research.nifty_forecast_v18.forecast
.venv/Scripts/python.exe -m research.nifty_forecast_v18.risk
.venv/Scripts/python.exe -m research.nifty_forecast_v18.risk point_controls
.venv/Scripts/python.exe -m research.nifty_forecast_v18.transfer
.venv/Scripts/python.exe -m research.nifty_forecast_v18.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v18.validation
.venv/Scripts/python.exe -m research.nifty_forecast_v18.sources forward
.venv/Scripts/python.exe -m research.nifty_forecast_v18.report
.venv/Scripts/python.exe -m research.nifty_forecast_v18.delivery
```

Corporate SQLite data retains source-row keys and local IST publication time. Text and financial tables reference source documents. Each forecast's law index identifies its immutable atom row. Original return atoms are log returns. Volatility atoms are annualized volatility ratios. Joint path files preserve signed OHLC log ticks, with the conversion factor in the path archive. Exact native-model overlays store the shift and reference the weighted V14 atom archive. Prior studies' cutoffs, legal bases, source manifests and case counts remain in their own receipts. See the reports for the simple and exact comparators for each target.
