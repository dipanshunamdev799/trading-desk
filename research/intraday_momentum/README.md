# Intraday stock momentum research

This folder evaluates a cash-equity intraday hypothesis. It does not start a
worker, create an application bot, change the global switches, or place orders.
The frozen strategy definitions and chronological splits are in `PROTOCOL.md`;
source and cost references are in `SOURCES.md`.

The completed first study found **no eligible paper-bot candidate**. All tested
full-period portfolios lost after modeled costs. See
[`FINDINGS.md`](../../artifacts/intraday_momentum/FINDINGS.md) for the complete
descriptive ranking and interpretation, and
[`REPORT.md`](../../artifacts/intraday_momentum/REPORT.md) for chronological
results and event rates. This result did not install or start an intraday bot.

## Data boundary

All runtime price/volume inputs come from `public.candles` in the existing
PostgreSQL database, explicitly filtered to `source='upstox'`. Acquisition may
insert authentic, unmodified Upstox observations into that table. It performs no
DDL and refuses conflicting existing rows rather than replacing them. Plans,
source responses, NSE audit evidence, community text and study results stay in
local files under `artifacts/intraday_momentum/`.

The cohort is all 500 names in the dated October 2024 index-fund holdings proxy,
published 7 November 2024, at `artifacts/swing_discovery/universe.json`. It is a
fixed historical cohort, not a reconstituted historical index. Missing or later
delisted identities remain in the dispositions. The test window is 14 November
2024 through 13 November 2026; daily warmup begins 1 July 2024.

## Download selection and causal decisions

Daily eligibility uses the previous completed session's price of at least
₹50 in that day's actual share units and the prior 63-session median daily
`close × volume` of at least ₹5 crore, requiring 50 prior observations. Known
capital-action and dividend ex-dates are excluded using local dated NSE metadata.

A daily high at least 8% above the previous close, or low at least 8% below it,
identifies a **download superset**. Each selected stock-month and its preceding
month are acquired in full. The actual scanner must still wait for the
qualifying completed intraday bar. No later daily extreme, eventual gain or
full-day volume may enter a trade decision. This acquisition does not support
an independent 4% mover comparison.

Five-minute sessions require the complete 09:15–15:10 start-time grid of 72
valid bars. Data after the forced exit are unnecessary, so changes to the later
closing-auction schedule do not censor usable mornings. Missing, duplicate or
invalid required bars quarantine the session. A full-grid Saturday is allowed;
a short special session is not silently treated as a normal day. No synthetic
bars or forward fills are introduced.

Cumulative RVOL divides current cumulative volume by the median cumulative
volume at the same clock bucket in the previous 20 exchange sessions, requiring
10 valid histories. The denominator excludes missing/quarantined sessions and
months whose acquisition job was refused. An unavailable denominator remains
NaN and cannot qualify a signal, including the volume-gate ablation.

## Historical share units

Upstox prices in these inputs are back-adjusted around the verified splits and
equity bonuses, with reciprocally adjusted volume. `units.py` combines same-date
equity actions, excludes preference-security bonuses, and checks the convention
against local official NSE bhavcopies. Its audit records source hashes and
per-company residuals. An uncertified future factor blocks the affected day.

The loader computes RVOL on the raw common adjusted basis **before** restoring
the execution day's bars locally: prices multiply by the verified future-action
factor and volume divides by it. The prior close uses the current session's
factor. This preserves traded value while expressing integer shares, cash and
the ₹50 floor in historical units. PostgreSQL observations remain unchanged.
Known event dates are still excluded; this is not a claim that every corporate
action or historical tradability restriction has been reconstructed.

## Reproducibility and commands

Use the repository virtual environment, with the normal application database
and Upstox settings. These commands are operational steps, not a single command
to rerun during an existing acquisition:

```powershell
.venv/Scripts/python.exe -m research.intraday_momentum.data plan
.venv/Scripts/python.exe -m research.intraday_momentum.data acquire
.venv/Scripts/python.exe -m research.intraday_momentum.data load
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_intraday_momentum*.py"
.venv/Scripts/python.exe scripts/run_intraday_momentum.py
```

`plan` can retrieve missing daily Upstox observations and writes a new plan;
`acquire` can retrieve and insert primary Upstox bars. `load` only reads market
data from PostgreSQL and writes its local audit. Do not regenerate the plan while
an acquisition is active. For an amended plan, archive its predecessor, retain
the verified source-job lineage, and acquire the explicit delta before results.
The synthetic test command covers signals, data validation, share units, costs,
portfolio execution, extension events, resolution and result freezing (66 tests
at the first study freeze). The runner validates source manifests, loads the
candidate data, freezes development-only selection, and writes local research
outputs. It may acquire primary one-minute data for the fixed resolution audit;
it does not activate an application bot.

The completed share-unit correction used the one-time
`scripts/amend_intraday_unit_plan.py` before strategy results. It requires every
original job to be OK, verifies response hashes, archives the original plan and
manifest under `plan-versions/v1-before-unit-correction/`, and accepts only the
independently audited candidate/request delta. `plan-amendment.json` records the
old and new hashes and the reused source jobs. The amendment added one MSUMI
stock-day (7 April 2025) and its March/April requests: 4,299 became 4,300 candidate
days, and 4,853 became 4,855 jobs. Existing request identities were unchanged.
All 4,855 source jobs subsequently completed OK, with 7,343,068 source bars;
usable candidate coverage is reported separately by the loader.

The amended plan spans 495 exchange sessions. Of the original 500 cohort names,
496 have daily observations, 489 are eligible on at least one study day, and 462
have a candidate event day. GSPL, ISEC, JBCHEPHARM and PEL have no daily coverage
and retain their source-error dispositions. No candidate day is blocked by an
uncertified share-unit factor. The 4,300 candidate days divide into 2,177
development, 723 validation and 1,400 final-period days. These are download
candidates, not trades or a claim of complete historical tradability.

The first frozen load admitted 4,293/4,300 candidates (99.84%): all 2,177
development days, 721/723 validation days and 1,395/1,400 final days. All 462
candidate stocks remain represented. The seven rejected candidates have only
short afternoon source sessions: TATAINVEST and JUBLPHARMA on 21 October 2025
(12 bars, 13:45–14:40), and EMCURE, ASTERDM, FINCABLES, RRKABEL and DIVISLAB on
8 November 2026 (14 bars, 14:20–15:25). They contain no morning entry window.
The loader's 329 missing-grid count covers all fetched history stock-days; it
does not mean 329 candidate days were excluded. RVOL has 20 valid histories for
3,999 admitted candidates, 19 for 291, and 18 for three, with no insufficient
history disposition. `unit-audit/load-coverage-summary.json` preserves the
period counts and seven individual dispositions.

Important local artifacts:

| Artifact | Purpose |
|---|---|
| `jobs-plan.json`, `daily-context.json` | Fixed cohort, eligible contexts, candidate days, exact stock-month requests, hashes and dispositions |
| `raw/` | Compressed primary HTTP responses with request identity |
| `acquisition-manifest.json`, `acquisition-jobs.jsonl` | Source SHA256, status, imported counts and resume lineage |
| `plan-amendment.json`, `plan-versions/` | Explicit pre-result correction and archived original acquisition provenance |
| `load-audit.json` | Loaded candidates, missing/invalid sessions and RVOL history counts |
| `unit-audit/unit-adjustment-audit.json` | Dated actions, independent raw-unit checks and verification classifications |
| `unit-audit/daily-intraday-consistency.json` | Independent daily/intraday envelope check; coverage scope is recorded |

An `ok` job certifies its request/response provenance, not that every session has
usable data. Both the manifest and load dispositions are required to describe
coverage. A resumed job must match the plan and response hashes. Non-OK jobs
must be resolved or explicitly reported as incomplete before interpreting a
portfolio comparison.

## Checks performed before strategy returns

The independent source check found only `upstox` in the study's scoped daily
and five-minute rows. The daily/intraday envelope audit matched 90,776 complete
75-bar stock-days across 444 stocks in acquired months, with no missing daily
record and no observed qualifying completed-close 8% event omitted by the daily
screen. That audit deliberately uses the older full-day 75-bar subset; it is
not a proof for entirely unacquired months. Small vendor daily/intraday extrema
differences and broader volume residuals are retained in its companion audits.
There were 52 daily-high and 43 daily-low differences over one basis point,
with maximum absolute differences of 28.61 and 111.02 basis points. Most larger
differences give the daily series a wider envelope, which safely adds downloads.
The median full-day five-minute/daily volume difference was −4.41 basis points.
These comparisons validate the download screen on observed months; they do not
replace execution, missing-session or share-unit checks.

Data completeness does not establish executable liquidity. Candles do not
reconstruct historical spreads, market depth, circuits, stock-specific MIS
eligibility, short-sale availability or queue position. The protocol keeps
these limitations separate from the primary long-only simulation and applies
fixed cost/execution stress assumptions before any bot deployment decision.
