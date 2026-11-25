# Intraday microstructure V3

Read `V3_FINDINGS.md` first. This folder implements read-only research, not an application bot. No order API, scheduler, worker modification or token regeneration is included. Preserve V1/V2 outputs; do not use the exposed archive as independent forward alpha evidence.

Dependencies use the existing project environment: Python, NumPy, pandas, psycopg2, requests, python-dotenv, websockets and the existing Upstox protobuf decoder. PostgreSQL connection and read-only token come from the existing settings; an optional explicit `UPSTOX_MARKET_DATA_TOKEN` can override the market-data token in memory. Never print or commit credentials.

From the project root:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_intraday*.py'
.venv/Scripts/python.exe -m research.intraday_momentum_v3.auth
.venv/Scripts/python.exe -m research.intraday_momentum_v3.metadata
.venv/Scripts/python.exe -m research.intraday_momentum_v3.archive
.venv/Scripts/python.exe -m research.intraday_momentum_v3.quality
.venv/Scripts/python.exe -m research.intraday_momentum_v3.universe
.venv/Scripts/python.exe -m research.intraday_momentum_v3.readiness freeze
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture run --seconds 28800 --transport auto
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture status
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture stop
.venv/Scripts/python.exe -m research.intraday_momentum_v3.readiness audit
.venv/Scripts/python.exe -m research.intraday_momentum_v3.model fit
.venv/Scripts/python.exe -m research.intraday_momentum_v3.model calibrate
.venv/Scripts/python.exe -m research.intraday_momentum_v3.evaluate
```

Inventory and detailed replay are bounded PostgreSQL reads and reuse completed versioned chunk results; read the archive module before rerunning against a growing database. Refresh metadata/universe on a new market day; same-day universe plans are immutable. Freeze is immutable and verifies document/code hashes on every observer start. Edit a frozen protocol only under a new version with an explicit new future boundary.

For closed-market plumbing only:

```powershell
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture run --seconds 20 --transport rest --smoke-closed
```

This stores authentic snapshots but never counts them as new fresh-market evidence. Nothing in this command enables automatic collection tomorrow. Raw acquisition and source provenance are in `artifacts/intraday_momentum_v3/metadata/` and `runs/`; derived events are local compressed JSONL. Authentic raw responses/decoded stream payloads also go to existing PostgreSQL tables. See `FORWARD_CAPTURE_STATUS.md` for operating bounds and failure behavior.

Important artifacts: `auth-audit.json`, `metadata-audit.json`, `metadata-reconciliation.csv`, `archive-inventory.json`, `archive-coverage.csv`, `archive-depth-type-sample.csv`, `detailed-quality.json`, `universe-current.json`, `protocol-frozen.json`, `forward-readiness.json`, `model-status.json`, `evaluation-status.json` and `verification.json`. Full provenance/checksums are generated separately after verification so they do not alter the frozen protocol.

No 2027 collection or evaluation is enabled. Missing future sessions remain a dependency; the scripts refuse to fabricate a trained model or profitability result from historical/closed-market data.
