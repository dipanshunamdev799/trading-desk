# Investment paper bots

## Gradual paper deployment

The active test can now use `staged-paper-v1`, a separate execution/allocation
variant of the source strategies. Its default limits per Rs10 lakh portfolio are:

- At most 10% of capital in new buys per trading session (no more than Rs1 lakh;
  the allowance decreases if equity falls below starting capital).
- New buys cannot take total invested exposure above 50% of current equity.
  Price movements after entry can change the marked exposure; they do not force
  an unrequested liquidation.
- At most two filled buy orders per session, including C1-R top-ups. All five
  C2-S books share these limits; each retains its own cash.
- A 5% per-stock entry cap, applied across all five C2-S books together.

Entries that exceed an allocation limit stay queued for another session. A new
five-session selection replaces the stale queue. Auction evidence still gates
C0-R-X; rejected auction buys are dropped as before. C1-R does not concentrate
its exposure target into the few positions already opened during the ramp.
Sells remain available without consuming the buy allowance.

`POST /investment-bots/paper-testing` accepts `mode: fresh|keep` and a policy.
A fresh run starts with Rs10 lakh per strategy and no positions. It has its own
ID, start date, immutable session records and capital counters in PostgreSQL.
No fill is backdated to before the new run. The first completed selection session
produces intentions for a later open; results are reconciled the following morning.
Restarting or re-running a paper cycle does not reset limits or duplicate entries.

The original reference ledger remains intact and can be viewed with
`GET /investment-bots/{id}/archive` or exported with `scope=reference`.
Dashboard exports default to the active paper run. Once a staged run is active,
the original reference run is no longer advanced. These new allocation results
are separate from the historically verified original strategy: source selection
rules and frozen research files are preserved, while paced execution is versioned
and independently tested. Paper-run settings never change F&O controls.

```powershell
.venv/Scripts/python.exe backend/scripts/test_investment_pacing.py
```

Community auction research is separate from all application data and controls.
`python -m investment_bots.community_auction --download` downloads three pinned
public archives and writes results under `artifacts/investment_bots/community-auction/`.
Install the optional `backend/requirements-community-auction.txt` reader first.
Existing Upstox candles/metadata are read through server-enforced READ ONLY
PostgreSQL transactions and cached locally. Community observations and research
results are **never written to PostgreSQL**. Raw downloads and panel caches are
gitignored. The archive date/freshness audit cannot establish a strict C0-R-X
replay; final-volume and zero-imbalance approximations are clearly labelled.
The [local experiment report](../artifacts/investment_bots/community-auction/RESULTS.md)
contains same-window C0-R comparisons, exposure, data coverage and cost/size checks.

The separate ten-year research replay covers **2016-11-15 through 2026-11-13**.
Its results, yearly breakdowns and quality audit are in
[the research report](../artifacts/investment_bots/ten-year/RESULTS.md).
Run `python -m investment_bots.long_history` to replay the PostgreSQL history.
The optional `--source PATH_TO_DUCKDB` flag performs a one-time read-only import of
older bars and both benchmark indices into PostgreSQL. Research runs, daily curves
and order ledgers use the `investment_research` schema. This is a separately
versioned extension with a pre-test warmup, fixed current-universe membership and
INE-only common-equity classification; it does not extend the frozen paper mandate
or place orders. It includes phase, cost, whole-share and missing-day stress checks.
C0-R-X has no validated decade result because the historical auction evidence is absent.

The `/investment-bots` page contains C0-R, C1-R, C2-S and C0-R-X. The source documents
are preserved verbatim in `specs/`, with their file checksums and original research
fingerprints exposed by the API. The implementation is an independent
`specification-adapter-v1`; **the original source archive has now been imported into PostgreSQL**. The verification claims inside the attached documents describe
the original implementation. This adapter is independently cross-checked against the unmodified simulators; full historical universe, signal and portfolio parity has now been verified on the supplied daily dataset.

These are NSE cash-equity, long-only reference paper portfolios. They do not import
the F&O broker or use its journals, capital limits, controls or kill switch. There
is no live-mode option and no broker order-submission interface. Each strategy has
₹10,00,000 notional capital; C2-S has five independent ₹2,00,000 books. They are
enabled on first application startup. Pauses and the investment kill switch persist
across application restarts. F&O Global Start and Global Kill Switch affect only F&O.

## Imported research inputs

All required source inputs have been received and imported into the application's PostgreSQL:

- `market_data.duckdb`: 1,087,045 completed daily equity/NIFTY bars from 2025-01-01 through 2026-11-13, plus 617 corporate-action records. Existing identical bars were reused; conflicting values are rejected without overwrites.
- `dpanel_meta.csv`: the original 2,284 instruments, in frozen column order, with static industry labels (`Other` for empty labels).
- `dpanel.npz.zip`: the frozen NPZ container (its extension is ZIP). Every OHLCV cell and NIFTY OHLC value in the 464-session research slice matches the supplied DuckDB source exactly, including missing cells.
- `dpanel.py`: original loader retained as checksummed evidence; its filesystem imports and CLI were not executed.

DuckDB is a **one-time read-only source reader**. Market bars use the shared `public.candles` table. Frozen metadata, controls, reference portfolio records, audit events, quote snapshots, verification results and source evidence use the `investment_bots` PostgreSQL schema. No bot reads DuckDB, NPZ, CSV or SQLite for runtime prices or portfolio state.

The completed import can be reproduced with the optional reader dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-research-import.txt
.\.venv\Scripts\python.exe -m investment_bots.import_duckdb "C:\Users\ME\Downloads\market_data.duckdb" --loader "C:\Users\ME\Downloads\dpanel.py" --metadata "C:\Users\ME\Downloads\dpanel_meta.csv" --panel "C:\Users\ME\Downloads\dpanel.npz.zip"
```

Source file hashes and frozen identity are pinned. Repeating an identical import is idempotent. Conflicting source data or metadata are refused, rather than silently altering a strategy version. Input bundle import via `python -m investment_bots.data FOLDER` remains available for `instruments.csv,daily.csv,corporate_actions.json`; see that command's validation messages for its interchange columns.

## Historical verification

`python -m investment_bots.verification` reads the imported market data from PostgreSQL, recreates the original universe using the frozen `D25` and `inputs_fixed` function definitions, and compares the adapter with unmodified `sim5`/`xsim` engines. The original pipeline's unrelated imports, filesystem setup and CLI are not run.

The verification through 2026-11-13 passed:

- Zero universe-cell, score-presence or score-value differences across all 464 sessions.
- All nine original integrity checks pass, including 19 split/bonus event checks; the 20 large-move events were persistent, with no reverted bad-print branch.
- All 512 historical C0-R orders and 247 closed reference positions reproduce; net reference total return is 0.5442439307942586. Historical results remain research evidence and are never credited to the new paper account.
- Maximum normalized equity errors: C0-R 2.45e-15, C1-R 1.12e-15, C2-S 8.89e-16. C0-R-X mechanics under a deterministic synthetic gate differ by less than 8.89e-16; this is not prospective execution evidence.
- All 80 day-zero whole-share intentions match the supplied original file: 78 valid and 2 rejected zero-share intentions in C2-S.

The nine integrity checks and independent universe/score comparison also gate ongoing paper reconciliation. Historical verification is stored as `investment_bots.metadata['historical_parity']`; the latest ongoing check is `latest_integrity`. The imported cache/source comparison is in `duckdb_import`. Any unresolved reference-rule disagreement fails closed.

## Processing and accounting

The API owns a 15-second scheduler. At/after 07:45 IST it checks completed sessions
through the previous calendar day, capped at 2026-12-31. It refreshes only the fixed
panel through primary Upstox historical daily candles; it does not switch vendors.
Stored NIFTY daily bars define trading sessions, including special weekend sessions.
Exchange calendar evidence checks for absent expected sessions. Missing inputs,
malformed prices, non-equity classification, zero volatility, an ADV boundary tie,
more than 2% missing prior-universe/holding closes, or a conflicting stored record
block processing and preserve existing records.

The adapter implements 63-session median traded value with 50 observations, a
top-300 universe, 63-session momentum divided by 42-session sample log-return
volatility (36 observations, scaled by √63), a causal six-session mask after >40%
price moves, 20 holdings, retention rank <40, and a six-name industry cap for new
selections. The fixed paper anchor is 2026-11-13 and rebalances count actual panel
sessions. C1-R targets 15% annualized volatility from the 20-return C0-R shadow
portfolio anchored on 2025-04-01, with daily exposure checks and a 10-point band.
C2-S maintains five staggered books with separate cash and no cross-book funding.

Records replay deterministically from the fixed anchor. Repeated runs compare
each stored session's payload and SHA-256; conflicting recomputations raise
`record_conflict` and never overwrite history. Sessions recovered after downtime
are explicitly **reconstructed reference history**, not observed forward orders.
The UI and exports label that convention. Stopping/pausing preserves positions and
halts reconciliation; resuming replays from the anchor. Pausing is not liquidation.

The supplied specifications intentionally use **fractional-share value accounting**
with 0.225% costs per side. Whole-share intentions are a separate report, sized at
the decision close. The adapter preserves this distinction rather than silently
changing the strategy to whole-share execution. A zero-share intention is rejected
in that report; the reference book can still differ due to fractional accounting.
Execution exports explicitly say `reference_quantity` and `real_orders_submitted=0`.

For C0-R-X, prospective raw quotes are captured only while the API is running at
the specified morning slots. Missed snapshots are not reconstructed or backdated.
The last snapshot label ≤09:05 and first in [09:12,09:15) feed the ordered classifier;
their actual timezone-aware receipt times must also fall inside those session
windows. A request finishing after the decision cutoff cannot justify an entry.
staleness is 120 seconds and size participation is 10%. Missing evidence drops buys
and carries sells. Snapshots are checksummed; quote failures are retained. A
`likely` classification permits a theoretical official-open fill, not a claim that
an actual order filled. Auction fields follow the
[Upstox Full Market Quotes V3 schema](https://upstox.com/developer/api-documentation/get-full-market-quote-v3/).
Special-session auction timing realism remains unresolved, as in the source specs.

## API and verification

- `GET /investment-bots/dashboard`, `GET /investment-bots/{id}`
- `POST /investment-bots/run` queues a reconciliation
- `POST /investment-bots/{id}/control` with `{"action":"start"}` or `pause`
- `POST /investment-bots/global/control` with `{"action":"start"}` or `pause`
- `GET /investment-bots/{id}/specification` returns the attached Markdown
- `GET /investment-bots/{id}/export?kind=orders|executions|equity`

Browser mutations use the same application-origin checks as F&O controls.
No endpoint accepts a live execution mode or an order submission.

```powershell
.\.venv\Scripts\python.exe backend\scripts\test_investment_bots.py
.\.venv\Scripts\python.exe backend\scripts\test_investment_import.py
```

Tests use isolated temporary PostgreSQL schemas and synthetic inputs; they never use a SQLite fallback or write market fixtures into public tables. The schemas are removed after each test. They check the formulas, ranking,
retention and industry rules, causal masking, next-session sequencing, costs,
pending sell replacement, missing opens, minimum buys, staggered cash, C1 rescaling,
auction gate, session/replay immutability, pause fencing, origin restrictions and
paper-only API. Cross-engine tests compare C0-R, C1-R and C2-S against the supplied unmodified `sim5.py`, and C0-R-X against the supplied unmodified `xsim.py`, to 1e-12 equity tolerance on deterministic price/score paths. The six frozen-source hashes match the attached specifications. Historical comparisons now also pass against the supplied full daily dataset, including all 512 C0-R orders and the nine integrity checks.

## Supplied archive provenance

Import the ZIP directly without running its scripts:

```powershell
.\.venv\Scripts\python.exe -m investment_bots.archive "C:\Users\ME\Downloads\swing_2025_2026.zip"
```

The importer verifies the six frozen code hashes and stores 84 relevant source/specification and day-zero paper files in PostgreSQL as checksummed source evidence. It does not unpickle research caches or fabricate daily data from the intraday arrays. The first archive’s intraday `panel25.npz` describes 643 stocks. The separately supplied daily `dpanel.npz.zip` contains the required 2,284-column panel and has now been verified. Research paper intentions in the archive remain source evidence, not newly executed portfolio orders.
