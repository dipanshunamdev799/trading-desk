# NIFTY V4

Read [the delivered research](../../NIFTY_V4_RESEARCH.md). Decision: **NO
DEPLOYMENT**. Historical evidence is research-exposed; no independently validated
edge exists. No scheduler or trading process was installed.

The completed run is `artifacts/nifty_forecast_v4/2026-11-18/run-001`.
Its registry, eight reports, source/data audit, reproduction, diagnostics,
distribution forecasts, uncertainty, power assumptions and append-only ledger are
preserved separately from V3. Dependencies are the existing application environment
and the numerical versions recorded in the V3 requirements file (Python 3.15).

## Daily process

From the repository root, start the process at **09:00–09:09 IST** on an eligible
future NSE session, with the existing configured Upstox analytics credentials:

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective run
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective resolve
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.prospective status
```

The issue time is 09:10–09:12, with all newly retrieved inputs received by 09:10.
If acquisition/fitting takes too long, the process rejects the origin. It records
the previous completed session close, exact target sessions, raw inputs, source
clocks, source/model versions and predictions. It rejects source revisions,
duplicate forecasts, out-of-scope dates and timing violations. There are no order
API calls. No unattended run has been scheduled.

`diagnostic-late` explicitly issues into a separate excluded cohort. A successful
18 November late rehearsal is already frozen; a duplicate is refused. Its
extreme finite-support outputs are not calibrated probabilities or trading signals.
No endpoint-only distribution claims future path-breach risk or realized volatility.

Resolution appends outcomes only after endpoint 18:00 IST and matching completed
session bars exist. It reports revised reference closes but scores against the
original frozen close. Candidates/baselines share exactly the same outcome.
Do not edit ledger lines, captures, frozen inputs or model artifacts. A stale lock
or corrupt ledger requires explicit review; it is not automatically repaired.

The ledger is hash chained and fsynced under an exclusive writer lock. Preserve a
trusted external copy of its head for stronger auditability: local file hashes,
local times and server Date headers do not constitute external notarization.
The existing scope prohibits targets or resolution beyond 2026. Adequate power
is not achievable within the remaining scope, and no future extension is assumed.

## Reproduction and verification

```powershell
# Recomputes named V3 candidate probabilities and two independent refits:
.\.venv\Scripts\python.exe -m research.nifty_forecast_v4.reproduce
# Assertions without rewriting the saved test result:
.\.venv\Scripts\python.exe -m unittest research.nifty_forecast_v4.verify
```

`common.py` creates the initial immutable registry/audit and refuses to overwrite
it. `distributions.py` and `diagnostics.py` likewise refuse to overwrite completed
studies. Do not delete those guards or rerun a new search into run-001.
`statistics.py` implements registered matched comparisons and power planning;
`reports.py` generates the eight reports from saved results. Copies of the exact
first-issued code are hash verified in `source-at-first-issue`; later hardening is
documented in `operational-rehearsal.json`. Future issues snapshot source before
execution and reject a code change during issuance.

No new indicators or model competition were added. The four coherent laws and
bounded stress/calibration diagnostics are registered as exploratory, separate
from the exact frozen V3 binary comparisons. Failed results remain in the reports.
