# Two-year swing research

Research only. These modules never submit broker orders.

The frozen experiment covers 10 November 2024 (first regular session 11 November)
through 9 November 2026, with pre-window warmup from 2023. It tests 207 controlled
MACD/EMA/structure configurations on NIFTY direction and cash long-only NIFTYBEES
and BANKBEES. The reserved final period overlaps earlier project research; it is
not a genuinely untouched holdout.

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_swing*.py'
.\.venv\Scripts\python.exe -m unittest research.swing.test_data
.\.venv\Scripts\python.exe scripts\run_swing_research.py --offline
.\.venv\Scripts\python.exe scripts\verify_swing_research.py
```

Omit `--offline` to fetch missing Upstox windows using the existing read-only
analytics-token configuration. The historical endpoint uses an exclusive research
cutoff of 10 November 2026; this frozen study does not silently extend its window.
Existing raw caches are reused, and older research artifacts are preserved.

- `data.py`: authenticated read-only ingestion, immutable raw caches, OHLC/session
  validation, corporate-action/calendar audit references and special-session data.
- `signals.py`: session-boundary alternatives, EMA/MACD/ATR, delayed confirmed
  pivots, structure and support/resistance, causal multi-timeframe signals, catalog.
- `engine.py`: chronological next-open fills, fee-inclusive risk sizing and fixed
  targets, gaps, conservative same-candle ambiguity, exits and marked equity.
- `validation.py`: ten-session block intervals and approximate joint max-t search
  control. Resampling frequencies are not probabilities that a true edge exists.
- `finalize.py` and `reporting.py`: reconciled confidence calendars, explicit
  diagnostic gates, reports and static figures.
- `scripts/run_swing_research.py`: fixed split screening, frozen selection,
  reserved final batch, cost stress, randomized controls and walk-forward policy.
- `scripts/extend_swing_evidence.py`: all-variant continuous two-year ledgers,
  monthly NAV and year/regime/side/exit summaries without changing selection.
- `scripts/verify_swing_research.py`: independent journal/accounting/causality
  verification. Exact library versions and source hashes are in environment.json.

Outputs are in `artifacts/swing_research/`. Begin with `report.md`; the concise
entry point is `SWING_RESEARCH_RESULTS.md` at the repository root. The final
verdict is insufficient evidence of a durable positive edge. No live playbook or
option/futures profitability is inferred from these results.
