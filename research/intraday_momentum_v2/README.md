# NSE intraday momentum phase2

New versioned research only. RESEARCH_PLAN.md freezes budget/selection;
STRATEGY_DEFINITIONS.md specifies rules; UPSTOX_DATA_AUDIT.md distinguishes
verified capabilities and missing data; FORWARD_CAPTURE_PLAN.md documents
the independent bounded recorder. No live/paper execution bot is created.

```powershell
.venv/Scripts/python.exe -m research.intraday_momentum_v2.data plan
.venv/Scripts/python.exe -m research.intraday_momentum_v2.data acquire
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_intraday_v2*.py"
.venv/Scripts/python.exe scripts/run_intraday_momentum_v2.py
```

Plan is one-time; acquire resumes verified jobs and persists every25completions.
Incomplete source jobs prevent any strategy return. V2 fixes v1manifest-loop
variable shadowing locally; frozen v1code and outputs remain unchanged. Results
are under artifacts/intraday_momentum_v2/: BACKTEST_REPORT.md,FINAL_DECISION.md,
metrics/stress/segments/trades/signals/rejections/daily-equity CSVs and hashes.
Do not overwrite frozen study manifests with changed code/data; use a new version.
Only2025–26performance and selection,2024warmup only. The whole history has
been previously researched. All stats remain conditional retrospective evidence.
