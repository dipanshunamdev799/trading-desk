# NIFTY V3 research

Executed 17 November 2026 using observations dated 1 January 2025 through
16 November 2026. Read [the research summary](../../NIFTY_V3_RESEARCH.md) and
[the frozen design](DESIGN.md) before interpreting results.

The result is **no independently established predictive edge**. All historical
evaluation dates were already exposed to research. The final numerical scenarios
were issued after the market opened and are explicitly late-issued as-of
reconstructions, not fresh premarket forecasts or calibrated trading signals.

## Reproduce the numerical experiment

Run from the repository root, using the existing application environment. The
research-specific numerical library versions are in `requirements.txt`; the
application's backend dependencies are also needed for settings/database imports.
The original execution used Python 3.15.0. This command does not download new
data, overwrite run-001, send orders or create an automation:

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast_v3.reproduce --out artifacts/nifty_forecast_v3/2026-11-17/reproduction-002
```

Choose a new destination for each repetition. It verifies frozen dataset hashes,
refits the registered configurations and compares the numerical predictions to
run-001. Reproduction is a repeatability check, not independent validation.

To inspect the existing run's verification suite:

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast_v3.verify
```

The suite writes `verification.json`; regenerating it changes its file hash, so
retain the original frozen record when checking forecast provenance. To run the
same assertions without rewriting that record:

```powershell
.\.venv\Scripts\python.exe -m unittest research.nifty_forecast_v3.verify
```

## Files and provenance

- `MISSION.md` preserves the user's complete research request.
- `DESIGN.md` and `registry-config.json` record the finite model budget and
  chronological design; the registry is inside the artifact run directory.
- `audit.py`, `data.py`, `audit_report.py` and `features.py` implement discovery,
  acquisition, source classification, features and matured labels.
- `models.py` and `experiment.py` implement model fitting, purged inner selection,
  refits, per-origin predictions and target-specific scoring.
- `discovery.py`, `analyze.py`, `negative_controls.py`, `legacy_diagnosis.py` and
  `verify.py` implement the information search, comparisons and failure audits.
- `freeze.py` refuses to overwrite an existing forecast. Its original output
  remains unchanged. `reports.py` generates the research reports from saved scores.

Artifact directory: `artifacts/nifty_forecast_v3/2026-11-17/run-001`.
It includes all ten required reports, source/dataset hashes, original-fit source,
532 configuration/fold records, model files, predictions, conditional diagnostics,
negative controls, frozen scenarios, verification and the delivery manifest.

Schema/availability guards and explicit contract-ID exclusion were added after the
first batch. `source-at-first-fit`, `fit-source-archive.json` and
`guard-amendment.json` distinguish the initial fitted code from that amendment.
Checks reproduced the exact feature matrix and representative linear/boosted
predictions. No model settings or outcome-driven selection changed.

Historical source delivery clocks and revision vintages are incompletely archived.
One additional domestic-session lag for derivatives/institutional reports and
conservative global joins reduce timing risk but do not establish vintage fidelity.
Current-member stock breadth is a research-only proxy excluded from selectors.
Do not rerun acquisition scripts into the frozen directory.
