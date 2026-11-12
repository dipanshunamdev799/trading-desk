# Frozen EMA conditional validation

Read `artifacts/ema_validation/REPORT.md` and `DESIGN.md`. This phase preserves
the earlier discovery/diagnosis code and results. The eight factorial cells are
four EMA/random × gate/no-gate comparisons with RS eligibility on, plus the same
four with only the RS eligibility filter removed. Momentum candidate ranking
remains fixed; this is not removal of all momentum information.

Use the repository virtual environment from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts/validate_ema.py
.\.venv\Scripts\python.exe scripts/ema_analyze.py
.\.venv\Scripts\python.exe scripts/ema_sensitivity.py
.\.venv\Scripts\python.exe scripts/ema_benchmarks.py
.\.venv\Scripts\python.exe scripts/report_ema_validation.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_ema_validation.py'
```

`freeze.json` fixes parameters, definitions,1000seeds and source/input hashes
before random outcomes. Resume refuses changed engine/definition/input hashes.
Each seed retains8 funded runs (two gates × two RS eligibility settings × two
horizons). `random_paths/{seed}.npz` retains all daily equity, cash, utilization,
position count, calendar indices and numeric trade records. Each companion JSON
retains metrics and rejection counts. `freeze.json` defines trade-column/reason
codes; `calendar.json` resolves stock/date indices. No seed is selected. The
optimized scalar engine reproduces prior funded-account paths in regression tests.

## Prospective local paper recorder

The recorder is initialized in `artifacts/ema_validation/paper`, starting flat
Rs1m. It has no broker/order API and no background schedule or automatic market
feed. It records only supplied, verified, completed daily observations. Its frozen
code/input hashes, immutable accepted snapshots, append-only receipts, pending
next-open candidates, hypothetical executions and marked account state are retained.
No prospective observation or return is invented while waiting for new bars.
An earlier initialization-only snapshot is retained in
`paper-initialization-before-tests`; it contains no trades or observed bars.

```powershell
.\.venv\Scripts\python.exe -m research.ema_validation.paper status
.\.venv\Scripts\python.exe -m research.ema_validation.paper record --input C:\absolute\verified-session.json
```

The JSON feed contract is:

```json
{
  "date": "YYYY-MM-DD",
  "previous_session_date": "YYYY-MM-DD",
  "source": "verified feed identifier and acquisition provenance",
  "calendar_source": "verified exchange/NIFTY observed-session calendar",
  "price_basis": "actual_unadjusted",
  "corporate_actions_verified": true,
  "nifty_close": 25000,
  "bars": {
    "FROZEN_SYMBOL": {
      "open": 100, "high": 102, "low": 99, "close": 101,
      "volume": 100000, "split_factor": 1, "dividend": 0
    }
  }
}
```

All470frozen eligible symbols are required, not just this one-row schema example.
Actions must be independently verified and all dividend components included.
Prices/volume must be actual contemporaneous units. Future/noncompleted candles,
missing companies, unverified actions, fractional entitlements, altered historical
inputs or changed frozen code fail closed. Feed the observed Nov10/11 sessions
as warmup bridges after the frozen Nov9 panel before the first Nov12decision.
The first signal close is on/after12Nov2026; first possible trade is the following
observed open. A prior decision receipt must predate the execution-session09:15IST,
so late historical ingestion cannot fabricate prospective fills. Regular session
completion is checked at15:30IST; special-session completion requires upstream
verified handling and should not be supplied before its actual close. Hypothetical
daily-open fills remain models, not contemporaneously observed broker executions.

Do not auto-approve uncertain corporate actions or infer missing bars. Prospective
recording needs a verified feed operator/adapter. No service was started to poll
or submit orders, and no claim is made that signals are being captured unattended.
