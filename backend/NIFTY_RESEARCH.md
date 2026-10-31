# NIFTY research backend

The NIFTY workspace replaces the Charts navigation entry at `/nifty`; old
`/charts` links redirect there. The original OHLCV explorer is available inside
the workspace. The supplied checklist is represented by **127 factors in ten
sections**, with the requested P1–P4 priorities and separate driver, indicator
and context classifications.

The price-action chart includes index, sector and stock ticker presets, an
instrument search, seven timeframes, selectable history, and candle/line/area
views. Axis and crosshair times use IST. Maximize fills the viewport while keeping
these controls available; Restore or Escape returns to the embedded chart.

### Intraday price-action checklist

The chart now opens on five-minute candles and the latest **available** session.
The study session dropdown is populated from actual returned candle dates. The
history selector widens that list; it does not invent missing sessions. Switch to
15 minutes to inspect a slower structure. Daily and weekly views remain available
as price charts and explicitly disable this intraday study.

`app/services/price_action.py` implements the supplied 47-concept checklist:
structure, previous-day/running-day/round levels, reactions and sweeps, closed
breaks/retests, candlestick patterns, continuation patterns, opening ranges,
BOS/CHoCH, displacement and candidate zones. Every concept includes its exact
rule in the returned catalog. `GET /nifty/price-action` returns the candle series
and annotations together. Parameters include instrument_key, interval, from_date,
to_date, session, orb_minutes (5/15/30) and round_step.

Both intraday candles and prior daily references use the existing shared
memory → TimescaleDB → provider gateway. Derived annotations are recomputed from
those retained candles; no extra provider feed or duplicate raw-data store is
introduced. A daily-reference failure leaves intraday analysis available, with
PDH/PDL unavailable. The actual previous recorded daily date is always visible.
NIFTY index volume is hidden because it is not directly traded volume.

Use **Layers → Core checklist** for a restrained starting view, **All 47
concepts** or individual groups for a broader study, and **Clean chart** to hide
annotations. Expand **Inspect checklist & matches** for searchable definitions,
per-concept availability, confirmed event times, and click-to-focus candles.
Hover markers for full names; compact chart labels are spaced to reduce overlap.
These controls and shaded zones also work in fullscreen.

Only completed 09:15–15:30 IST bars confirm signals. A live candle can remain on
the price chart while annotations wait for its close and next minute refresh.
Two bars on either side confirm pivots; markers appear on the confirming candle,
with the original pivot time in the explanation. Multi-bar calculations reset
across missing bars. Opening ranges require every constituent bar and a compatible
timeframe; future/current daily bars cannot supply prior-day levels. Running day
highs/lows use each bar's information, rather than projecting final extrema into
the past. Simple ATR(14) uses preceding true ranges; level tolerance is
max(price × 0.00015, prior ATR × 0.12). Neckline patterns expire after 30 bars or
a close beyond their pattern extreme. Break/retest candidates expire after eight
bars; a false break requires a return within three bars.

Flags, triangles and order-block/supply/demand zones are transparent heuristic
definitions, not verified institutional activity or CE/PE trading instructions.
Zone shading records whether a subsequent touch/full traversal has occurred;
historical confirmed events are not revised using later bars. The interface
separates no match from unavailable references, and links to supporting educational
context. Coverage counts describe detected concepts, not predictive confidence.

Validation: `python backend/scripts/test_price_action.py`, `npm run test:nifty`,
`npm run test:charts`, and `npm run build`. Tests include prefix-invariance (future
bars cannot alter earlier events), missing/invalid candles, forming bars, gaps,
opening-range coverage, neckline confirmation, FVG lifecycle, source failures,
overlay filtering, coordinate projection, IST clocks and chart focus.

Every factor is visible even when its source is unavailable. Coverage describes
stored readings, not predictive confidence or completeness of the research.
There is no composite directional score or order execution.

## Python modules

| Module | Responsibility |
| --- | --- |
| `app/services/nifty_catalog.py` | Complete checklist, units, priorities, roles, suggested primary sources and freshness windows |
| `app/services/nifty_sources.py` | Bounded collection, provider schema validation, timestamps, units and isolated errors |
| `app/services/nifty_analytics.py` | Technical indicators, strike-level options calculations and aligned daily return correlations |
| `app/services/nifty_store.py` | PostgreSQL observations, revisions, state and calendar events |
| `app/services/nifty_service.py` | Collection orchestration, factor coverage, historical context and dashboard assembly |
| `app/routers/nifty.py` | Read APIs, asynchronous refresh trigger and validated research imports |
| `scripts/nifty_research.py` | Standalone collector, inspection, export and import commands |

`sql/004_nifty_research.sql` is applied automatically by the existing market-store
migration runner. It creates research tables alongside the existing TimescaleDB
market data, without replacing the candle or options stores.

## Automated sources and coverage

| Source | Collected data | Interpretation |
| --- | --- | --- |
| Existing Upstox gateway | NIFTY spot, India VIX, ten sector indices | Provider timestamps and previous closes; existing memory → PostgreSQL → Upstox path |
| Upstox daily candles | 450 calendar days of completed NIFTY daily bars | Daily trend, previous-session levels, gap, EMA 9/21/50/100/200, RSI, MACD, ATR, realised volatility, range breakouts, market structure and momentum where warmups are satisfied |
| Upstox option contracts and chain | Actual active expiries, listed lot sizes, nearest expiry chain | Strike OI, OI changes, PCR, max pain, ATM IV, same-strike IV skew, volume and available Greeks; original acquisition time is separate from unavailable publisher time |
| Upstox institutional activity | Dated FII/DII cash net flows and available index derivatives positioning | Provider INR amounts converted to INR crore; long/short contracts retained as positioning data |
| NSE provisional FII/DII cash report | Gross buying, gross selling and net flow for the report session | Authoritative combined NSE/BSE/MSEI figures; crore units verified against NSE's own column schema; both gross legs reconciled against Upstox for the same date |
| Official NSE membership CSV + Upstox | Current 50-member identity and quoted advances/declines | Complete same-session coverage required for the ratio; membership file supplies no weight or effective date |
| Upstox official global master + quotes | GIFT NIFTY instrument identity and dated quote | Identity discovered from the master; provider latency retained |
| Yahoo public chart endpoint | S&P 500, Nasdaq Composite, Dow, US futures, Nikkei, Hang Seng, Shanghai, EURO STOXX 50, Brent/WTI, gold/silver, USD/INR, DXY, natural gas, copper and US 10-year yield | Unofficial, potentially delayed public data; continuous commodity/index futures are labelled as proxies; 90 completed sessions plus latest quote retained |
| FRED DGS2 | US 2-year Treasury yield | Official daily series date anchor; a reporting date is not a claimed release clock time |

Cash cards now use NSE's provisional report, whose table schema explicitly labels
buy/sell/net values in rupees crore. Net must reconcile to buy minus sell, and both
categories must carry the same reporting date. The original Upstox cash readings
remain in history with their unit warnings; a same-date, both-leg comparison is
stored as corroborating evidence. This does not establish units for unmatched
historical records. A later ambiguous provider refresh cannot replace a verified
NSE observation for the same session. Cards show the reporting session and
provisional status; a midnight date anchor is not labelled as a publication time.

Refresh only these two factors with:

```powershell
./.venv/Scripts/python.exe backend/scripts/refresh_cash_flows.py
```

Adapters fail independently. An outage does not overwrite successful retained
series with an empty response. The dashboard lists the source failures and
assesses freshness from the original reported time. A successful collection does
not imply every provider or factor succeeded.

Economic releases, RBI policy/liquidity, government actions, earnings, index
weights and exact point contributions, EMA breadth, futures basis/buildup, fund
flows, broad geopolitical coverage and some event calendars need additional
licensed/official feeds or sourced imports. Their checklist cards remain visible
with an unavailable status until populated. Current membership alone is never
used to invent historical membership, index weights or point contributions.

## Run

The existing `launch_web_app.bat` starts the database, backend and frontend. NIFTY
collection also starts with the FastAPI lifespan by default:

```dotenv
NIFTY_COLLECTOR_ENABLED=true
NIFTY_REFRESH_SECONDS=300
```

The existing `UPSTOX_ANALYTICS_TOKEN` configuration is reused. Some market data
requires provider access. Public-source failures are visible in the workspace.
Dashboard reads use retained data and never block on a full provider collection.
When collection is enabled, the first read can trigger background collection; refresh requests coalesce with
an in-progress collection in the same process. The UI reads the latest snapshot
each minute and checks in-progress refreshes more frequently.

Standalone commands from the project root (PowerShell):

```powershell
./.venv/Scripts/python.exe backend/scripts/nifty_research.py refresh
./.venv/Scripts/python.exe backend/scripts/nifty_research.py watch --seconds 300
./.venv/Scripts/python.exe backend/scripts/nifty_research.py catalog --output data/nifty-catalog.json
./.venv/Scripts/python.exe backend/scripts/nifty_research.py dashboard --output data/nifty-dashboard.json
./.venv/Scripts/python.exe backend/scripts/nifty_research.py history sp500 --limit 365
./.venv/Scripts/python.exe backend/scripts/nifty_research.py import research.json
```

## API

| Method | Endpoint | Result |
| --- | --- | --- |
| GET | `/nifty/catalog` | Ten sections, complete factor definitions and stable IDs |
| GET | `/nifty/dashboard` | Coverage, factor values/changes, status, provenance, context, retained daily candles, expiries and calendar |
| POST | `/nifty/refresh` | HTTP 202 with `started` or `running`; provider work runs in the background |
| GET | `/nifty/factors/{id}/history?limit=365` | Ascending observations with source times and collection times; corrections retained |
| GET | `/nifty/correlations?factor_id=sp500` | Pearson correlation of aligned NIFTY/factor daily percentage returns, sample count and limitations |
| POST | `/nifty/observations` | Validated sourced factor observations |
| POST | `/nifty/events` | Validated sourced calendar entries, including future dates |

Interactive request schemas are available at `/docs`.

## Sourced imports

The workspace has an expandable JSON import form. The CLI accepts a UTF-8 JSON
object with `observations` and/or `events` arrays. Each observation must include
`factor_id` from the catalog, a nonmissing JSON `value`, timezone-aware
`reported_at`, `source` and HTTP(S) `source_url`. Optional `unit` and `context`
preserve reporting periods, definitions, revisions and qualifications.

Use the publisher timestamp for `reported_at`; collection/import time is recorded
separately. Future observations, unknown factors, nonfinite values and unsafe
URL schemes are rejected. Planned releases belong in `events`, which require a
stable `id`, `title`, timezone-aware `event_at`, `source` and `source_url`.
Optional `category`, `impact`, `actual`, `forecast` and `previous` supply context.
Reimporting an unchanged snapshot is idempotent; corrections remain in history.
The calendar shows the latest revision for each event ID.

## Calculation and provenance rules

- Missing is distinct from actual zero. Composite calculations retain missing
  subfields and require appropriate warmup/coverage before claiming a value.
- NIFTY spot has no directly traded volume. Its volume and VWAP stay unavailable;
  a named traded proxy with explicit volume metadata is required.
- Daily bar timestamps identify the source session start, not a claimed closing
  publication time. Completed daily bars are collected through the previous day.
- Options OI preserves provider units. Incomplete OI prevents complete totals,
  PCR and max pain; available partial strike rows remain inspectable.
- Max pain minimises total intrinsic payout across the supplied strikes. IV skew
  compares put and call IV at the same nearest-to-spot strike and expiry.
- A chain without a publisher timestamp is marked stale/undated even when newly
  collected. Refresh cannot manufacture a market timestamp.
- Technical trend means the observed price/EMA relationship, not a forecast.
- Correlations use at least 20 return samples with matching start **and** end
  session dates. Missing sessions are not forward filled. Sources and units are
  not silently combined. Constant series produce an unavailable coefficient.
- Market closing times differ. Same-date correlation does not prove causality or
  establish information that was available before an Indian market move.
- Suggested source links in empty cards are references, not claimed evidence of
  a successful collection. Populated cards link to their actual adapter/import.
- Freshness uses the catalog's elapsed-time windows. It is not an exchange holiday
  calendar or a guarantee of live prices; source and collection times are visible.

## Validation

```powershell
./.venv/Scripts/python.exe -m unittest discover -s backend/scripts -p 'test_nifty*.py' -v
$env:RUN_MARKET_DB_TESTS='1'
./.venv/Scripts/python.exe backend/scripts/test_nifty_store.py
cd frontend
npm run build
```

Database tests create uniquely named fixtures and clean only those records.
No provider calls are made by the unit tests or database retention tests.

Provider references: [Upstox FII](https://upstox.com/developer/api-documentation/get-fii-data/),
[Upstox DII](https://upstox.com/developer/api-documentation/get-dii-data/),
[Upstox option chain](https://upstox.com/developer/api-documentation/get-pc-option-chain/),
[NSE membership](https://archives.nseindia.com/content/indices/ind_nifty50list.csv),
[FRED DGS2](https://fred.stlouisfed.org/series/DGS2).
