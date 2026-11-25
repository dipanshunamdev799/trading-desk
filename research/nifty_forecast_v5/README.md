# NIFTY V5 research

Read [the research index](../../NIFTY_V5_RESEARCH.md). All historical results are
research-exposed. **No independently validated edge; NO DEPLOYMENT.** V4's frozen
sources, candidates, protocol and ledger remain unchanged.

The delivered run is `artifacts/nifty_forecast_v5/2026-11-18/run-001`.
It includes fourteen reports, 193 instrument histories, source metadata/provenance,
176 initial features plus separate ETF/volume inputs, all 34 evaluated systems,
per-origin scores, searchable registries, fitted models, failures/repairs,
conditional/lead-lag studies, uncertainty, rankings and frozen experimental laws.

The historical comparison ends at the original matched V3/V4 evaluation origins.
The broker history initially stopped at 17 November. A separate official NSE
index/cash snapshot authenticated 18 November OHLC and actual ETF volume; NIFTY
25,227.95 matched the official derivatives underlying. Those inputs produced four
experimental laws at 22:51:50 IST before the next target session. No earlier
prediction was overwritten; no unfinished US close was used. Coherent probability,
mean, median, buckets and intervals agree within each law, but are not calibrated
guarantees. Distinct models' outputs must not be combined.

## Repeat the complete historical experiment

Use the existing Python 3.15 venv and numerical dependencies recorded in V3's
`requirements.txt`. Application settings dependencies are also required.
From the repository root, choose a **new output directory**:

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast_v5.reproduce --out artifacts/nifty_forecast_v5/2026-11-18/reproduction-004
```

This copies and hash-checks the frozen inputs, runs all registered historical
models in isolation without new market requests, and compares probabilities,
point predictions, CRPS, Brier, quantile loss and coverage numerically. It does
not reissue the current forecast or turn repeatability into independent evidence.
The corrected forest code does not repeat the original unused-metadata bug;
original failed attempts remain preserved in run-001.

To run assertions without rewriting the saved verification record:

```powershell
.\.venv\Scripts\python.exe -m unittest research.nifty_forecast_v5.verify
```

`common.py` creates the preservation audit. `data.py`, `extras.py` and
`database_audit.py` implement source discovery and read-only acquisition.
`features.py` records causal source/decision joins. `experiment.py` registers and
runs the initial two-stage model batch. `expansion.py`, `liquidity.py` and
`attribution.py` are separately registered follow-ups. `repair.py` records the
single failed implementation's correction. `discovery.py`, `conditions.py`,
`negative_controls.py` and `analyze.py` retain all inspected effects, proper scores
and uncertainty. `freeze.py` refuses to overwrite an existing issue.

## Resolve frozen experimental forecasts later

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast_v5.score
```

Before a complete horizon matures it makes no network request or ledger mutation.
After endpoint 18:00 IST, it verifies actual observed target sessions, uses the
original frozen reference close, scores all same-horizon laws and their frozen
historical baseline on matched dates, and appends to V5's own hash-chain ledger.
Duplicate resolution is refused/skipped. It never writes V4's ledger. A missing
broker endpoint remains pending; a calendar mismatch requires review. There is
no automatic watcher or schedule, trade API call or live deployment.

The scope remains 2025–2026. The manual scorer refuses a run outside that date
boundary. Adequate monthly validation is not available from four historical
disjoint windows or one newly issued month. Future scope changes require user
instruction.

## Provenance limits

Historical vendor daily anchors are not proven publication clocks; revised source
vintages and unknown futures/CFD close conventions remain limitations. Named
exchange spot close assumptions use IANA timezones/DST plus a two-hour allowance;
unknown conventions use a conservative full extra UTC day. FRED/Treasury access
failures are documented, never filled with invented observations. Current-stock
membership remains a research-only survivorship approximation.

Exact initial fit source and exact issued source are archived separately.
Postfit schema/availability/maturity guards do not change numerical results;
verification independently refits the native lead. Report/reproduction hardening
is separately traceable in the delivery manifest. Keep frozen inputs, predictions
and ledger heads unchanged. Hashes and server Date headers are not external
timestamp notarization.
