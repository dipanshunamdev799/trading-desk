# NIFTY V6 research

Research-only native-index study; no trading/deployment. Run outputs are versioned under `artifacts/nifty_forecast_v6/2026-11-19/run-001`. Reports were finalized at their actual timestamp. All history is exposed; scope is2025–2026, frozen history through17November2026.

The authoritative mission is in `MISSION.md`. Existing V1–V5 data/code/ledger files are read-only inputs. Output overrides must resolve inside `artifacts/nifty_forecast_v6` and must use a fresh directory. Existing fitted-batch registries refuse overwrite.

Use the repository `.venv` (Python3.15 plus existing pinned research packages). `environment.json` records actual versions; no dependency changes were made by V6.

To verify the delivered run from the repository root:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v6.verify --require-replay --require-reports
```

To replay all fitted candidate batches against frozen matrices/parent laws/mediator features into a NEW directory:

```powershell
.venv\Scripts\python.exe -m research.nifty_forecast_v6.replay --out artifacts/nifty_forecast_v6/2026-11-19/replay-your-id
```

The full original construction order is `common`, `reproduce`, `features`, `forensics`, `prequential`, `mediation`, `experiments`, `monthly`, `forensic_audit`, `monthly_followup`, `followups`, `analyze`, `distribution_audit`, `reporting`, `verify`. For an independent full construction, set `NIFTY_V6_OUT` to a fresh V6 folder first; retain the raw V3/V5 upstream inputs. `common` freezes prior hashes and `features` creates matrices. `forensic_audit` must run after forensics and prequential. Original batch-source archives preserve exact historical source hashes; later guards/PC additions are recorded amendments. The candidate replay deliberately uses frozen independently audited parent/mediator artifacts, so it is not a new provider-data acquisition test.

`reporting` derives the13 reports, expanded tables and root index from recorded results. `verify` checks preservation, source hashes, labels, causal transforms, fitted artifacts, mixtures, scores, retained failures and report delivery. It does not certify economic causation, future calibration or an independent edge. No API credentials, broker order code, automatic forward watcher or deployment is part of this module.
