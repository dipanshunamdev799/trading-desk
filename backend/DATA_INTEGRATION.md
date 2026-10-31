# Market data storage

## One-year Max Pain research

Run `python backend/scripts/run_maxpain_study.py` from the workspace's Python
environment to reproduce the Backtests report. It uses the trailing 365 calendar
days ending yesterday in IST, plus 14 warmup days. Ten fixed NSE underlyings are
listed in `maxpain_study.py`; this is not the complete historical F&O universe.

Underlying daily OHLC follows the normal gateway. When historic Upstox Max Pain
is no longer supplied, the study reconstructs targets from official NSE UDiFF
derivatives bhavcopies. Each successful dated file is validated and its selected
option legs, original OI units, token/strike/side/lot data, source URL and SHA-256
are committed through `MarketStore.read` as `research_nse_fo_eod`. Re-runs reuse
these immutable database records. The complete report is also archived through
the gateway as `research_maxpain_convergence`; the JSON in `backtests/` is the
UI artifact, not the only retained copy.

Targets use prior-session EOD information. Evaluation begins at the next open
and ends at expiry close; the target remains fixed. Primary settings are T−1,
initial gap ≤1%, and fully paired published strikes. T−3/T−5, all starting
distances and all-published-contract results are labelled sensitivity views.
Unmatched strikes are excluded from strict evidence; the sensitivity sums only
actual published contracts without asserting absent counterpart OI is zero.
Missing files/candles, inconsistent cross-source closes and observable contract
adjustments are counted. Entire expiry dates are resampled for 95% bootstrap
intervals, because several chains share the same market session. No equity curve,
strategy returns, option fills or Sharpe ratio are manufactured for this spot
convergence study.

Application reads use `upstox_service.get_upstox()`, which returns `MarketGateway`.
The raw `UpstoxAnalyticsClient` is only the upstream transport. Do not instantiate
the raw client inside application services.

## Provider priority and Tapetide fallback

`get_upstox()` remains the shared gateway for existing callers. It now registers
Upstox as the primary provider and Tapetide as the secondary provider. A valid
Upstox response, including retained Upstox history and usable live stream data,
always wins. Missing values are not inferred from falsy numeric values: zero is
valid data. Quote batches fill missing instruments without replacing good
Upstox rows or combining fields from observations taken at different times.

On an empty result or upstream availability failure (missing credentials,
401/402/403/404/410/429, 5xx, transport failure or an unimplemented endpoint),
compatible reads can fall back. Invalid arguments, database failures and
programming errors are not treated as provider outages. If both sources fail,
the original Upstox error remains visible. Tapetide has no automatic retries on
quota errors. Its request rate and timeouts are bounded independently.

Automatic adapters currently cover:

- NSE equity full/LTP quotes, for V2 and V3, including partial batches. Identity
  resolution verifies the ISIN against Tapetide's company profile. The original
  quote update timestamp is retained; retrieval time never becomes trade time.
- Completed daily NSE equity and index candles. Equity prices use a raw-close
  scale to normalize split/bonus-adjusted OHLC; missing raw closes are omitted,
  rather than spliced into an unadjusted series. Index history uses the paged
  daily levels endpoint. Existing Upstox bars win during a partial-range merge.
- Daily FII/DII cash flows, with explicit conversion from Tapetide's crore
  amounts to the Upstox contract's documented INR units. Other segments and
  monthly aggregation are not silently substituted. The Upstox `from_date`
  parameter acts as a backward cursor, so the adapter bounds the same direction.
- Nifty-family max pain and PCR, for an explicit expiry and completed date that
  exactly match Tapetide's snapshot. These are labelled EOD scalars with no
  invented intraday insight points. Rolling expiry aliases are not guessed.

Tapetide's EOD/truncated option chain is **not** substituted into live chains,
complete strike OI ladders, Greeks, expired-contract identities or intraday
candles. Those return unavailable when an equivalent observation cannot be
established. Native Tapetide datasets remain available explicitly through the
dataset interface, with their timestamps, units, pagination and coverage flags.

Secondary data is stored in `market_datasets` and `market_responses` under
`tapetide.<endpoint>` identities. It never enters canonical Upstox candle rows,
coverage, contract masters, live stream caches or one-minute max-pain series.
The shared gateway checks the primary path before using this secondary cache on
each request. Existing primary cache/negative-cache expiry policies still apply.
Tapetide cache entries expire in five seconds for quotes, one hour for identity
search/profile data and five minutes for other datasets, even for dated history.
This keeps provider revisions refreshable and does not freeze a primary miss
into a successful historical response. Fallback dictionaries/rows carry
`_provider`, `_provenance` and original provider metadata; candle responses carry
per-bar `_fallback_sources`. Research source adapters preserve those labels.

### Shared endpoint library

The root `tapetide_data.py` client and `tapetide_endpoints.json` catalog register
104 public, read-only REST endpoints from the published OpenAPI specification
(verified October 24, 2026). This includes future-use datasets such as forecasts,
filings, scoring, ownership, screening, macro series, corporate adjustments and
options volatility. Account, portfolio and watchlist mutations are excluded.
No arbitrary URL or unregistered operation can be passed to the client.

```python
from app.services.upstox_service import get_upstox

data = get_upstox()
catalog = data.get_data_catalog()

# Existing calls use compatible fallback automatically.
quotes = data.get_full_market_quotes_v3(["NSE_EQ|INE002A01018"])

# Provider-native statements have different schemas. The shared dataset API
# tries the Upstox method first and labels a native Tapetide fallback explicitly.
statement = data.get_dataset("get_balance_sheet", isin="INE002A01018")
# {"provider": "upstox" | "tapetide", "dataset": ..., "data": ...}
# A native fallback also includes schema="tapetide" and fallback=True.

# Additional datasets without a matching Upstox method use their catalog names.
forecasts = data.get_dataset("get_forecasts", symbol="RELIANCE")
volatility = data.get_dataset("get_option_iv_history", symbol="NIFTY", range="1y")
```

Fundamentals, statements, shareholding, corporate actions, peers, single-stock
news, IPOs and native option-chain snapshots use `get_dataset` for fallback,
because their provider schemas are different. Existing raw Upstox-shaped getters
keep their contracts. Native pagination links and cursors are preserved; callers
must read coverage before treating a returned page as the entire dataset.
Overlapping Tapetide convenience aliases are rejected with the primary method
name, so callers use Upstox's parameter contract rather than bypassing priority.

Configure `TAPETIDE_TOKEN` in the local, ignored `.env`. It is loaded as a secret
setting and is never included in status, exceptions or persisted responses.
Optional settings: `TAPETIDE_FALLBACK_ENABLED=true`,
`TAPETIDE_TIMEOUT_SECONDS=15`, `TAPETIDE_REQUESTS_PER_SECOND=2`.
The gateway registers the provider lazily; no network call occurs at import or
startup. A restarted backend picks up configuration changes.

Validation: `python -m unittest backend.scripts.test_data_providers` covers
priority, recovery, partial quotes, namespace separation, dates/expiry, currency
units, price adjustment, provenance and error handling without network access.
`artifacts/tapetide-integration-check.json` records bounded live smoke checks:
simulated primary outage, actual Upstox recovery, daily fallback and EOD PCR.

The path is **UI → bounded process memory cache → PostgreSQL → Upstox**. Successful
API data is committed before it is returned or added to memory. Restarting the
backend discards memory, not retained market history. The standalone research CLI
still supports the original direct client; web requests use the gateway.

## Session-aware live feed

During verified active sessions, one shared Upstox V3 `full` WebSocket supplies
supported quotes, OI, option Greeks, IV and provider OHLC bars. Exchange status,
the exact session calendar and feed segment status decide whether to stream;
weekdays alone do not establish a session. Outside trading, reads use the normal
cache → PostgreSQL → REST path. Unavailable, disconnected or stale streaming
fields fall back to REST and are not labelled live.

Every received instrument update is committed to the `market_stream_ticks`
Timescale hypertable before publication to the in-memory live view. The raw
provider fields, source frame time and separate receipt time are preserved.
Active option chains are also retained once per minute in the
`market_stream_chains` hypertable, with per-leg source timestamps and dated
session metadata. Migration `005_market_stream.sql` creates these tables without
deleting existing data. Neither has an automatic drop policy.

The browser shares one `/market/live` subscription across dashboard components;
the backend shares one upstream connection across browsers. Demand subscriptions
expire after ten minutes without renewal, with a default cap of 1,500 instruments.
Keep one API worker for this connection manager (each additional worker would
create its own upstream connection). Freshness is checked independently for
prices, Greeks, IV and OI, with a default 30-second threshold. Reconnection clears
the old connection's live view. Queue/storage failures stop the feed and prevent
uncommitted ticks from becoming visible. REST chain seeds refresh at most once
per minute to cover instruments that are not updating on the stream. Feed IV
fractions are converted to percentage values when merged into option-chain data.

Max Pain's **Latest available** mode automatically uses the verified most recent
underlying trading session when markets are closed. Capture time remains visible;
an undated current Greek is never certified as a historical closing Greek.
**Historical as of** continues to require a snapshot captured on the selected day.
A weekend REST capture is never backdated to Friday. Thus Friday's historical
Greeks may be unavailable even while Latest available shows the provider's
current response for that contract.

Live pushes refresh Max Pain and NIFTY quote/OI research from committed feed
updates. Current 1-minute, 30-minute and daily chart bars use exact provider bars;
other chart grains retain their normal minute refresh instead of constructing
incomplete bars from a partial tick history. Historical chart ranges stay fixed.
Provider max-pain analytics continue at one-minute REST grain because they are
not a V3 streaming field. IPOs, institutional flows, public macro sources and
historical data also retain their source-specific collection schedules.

The Max Pain PCR chart reads the provider's dated one-minute PCR insights through
the same memory/database/API gateway. Full responses, including every minute,
remain in the Timescale `market_responses` archive and durable `market_datasets`
cache. Exact expiry, underlying, trading session and closing spot are checked;
weekend responses are not relabelled as trading sessions. Missing minutes remain
gaps. During trading, a current chart point can also be calculated from committed
streamed OI, but only when every included option leg has fresh OI. The chart uses
PCR 1 as an equal-OI reference, without interpreting it as a directional signal.

Volume PCR is the ratio of total put traded volume to total call traded volume
for the selected expiry, cumulative through each capture (not each minute's
incremental trades). It is reconstructed from the original `market_responses`
and `market_stream_chains` Timescale captures, with a short disposable memory
cache. Historical replay makes no option-chain API calls. All supplied legs must
have valid nonnegative volume, unique identities and matching expiry/underlying;
zero total call volume is unavailable, while genuine zero put volume gives zero.
Capture dates and regular-session hours are checked. Stream volume freshness is
tracked separately from OI/price. Mixed or legacy stream captures require a full
REST seed at most 60 seconds old unless every leg has fresh streamed volume.
The chart uses dashed segments and diamonds for volume, solid segments for OI,
and retains gaps. Overnight REST receipts are never backdated into a close.
Committed active-session stream captures also establish selectable trading
dates when daily-candle history has a gap; REST receipts alone do not.

Controls: `MARKET_STREAM_ENABLED`, `MARKET_STREAM_MAX_INSTRUMENTS`, and
`MARKET_STREAM_STALE_SECONDS`. The sidebar and `/market/live/status` expose
connection, session and fallback status. A live connection covers subscribed
instruments; it does not archive the entire exchange or recover missed historical
Greeks. The API and collectors must remain running to retain future updates.

## Storage

- `candles`: existing TimescaleDB hypertable, canonical interval and IST session
  boundaries; includes underlying and option OHLCV/OI.
- `candle_coverage`: per instrument, interval and date. Overlapping requests fill
  only uncovered dates, including interior gaps. A successful empty response is
  recorded separately from an error and retried later.
  A completed nonempty fetch window also records its intervening non-trading
  dates as covered, avoiding repeated requests for weekends and holidays.
- `market_datasets`: durable request identities and most recent response, with
  exact date, expiry, instrument and grain included in the key.
- `market_responses`: TimescaleDB hypertable retaining every successful gateway
  fetch, including OI, live option chains, quotes, contract masters and searches.
  `recorded_at` is receipt time; original observation dates remain in parameters
  and payloads. Undated live requests include the IST observation date.
- `max_pain_points`: TimescaleDB hypertable with dated one-minute provider points.
  Coarser chart requests reuse the one-minute source.
- `option_contracts`: contract identities and lot sizes retained by underlying,
  expiry, strike and option type, including expired contracts. Instrument tokens
  can be reused, so a token alone is not a historical contract identity.

Migration `sql/002_market_integration.sql` runs idempotently at API startup and on
first repository access. It does not delete or rebuild existing candle data.
No retention/drop policy is installed. Market capture is on demand while the
application is queried; this is not an unattended archive of every exchange
instrument. IPOs additionally have a background collector while the API runs;
see [IPO_RESEARCH.md](IPO_RESEARCH.md) for sources, cadence and coverage limits.

## Freshness and failures

Positive, completed historical responses and fetched candle days are immutable.
Live analytics and candles expire at the next minute boundary; quotes use a
five-second TTL, masters six hours, and search results one hour. Empty historical
fetches are retried after one day, rather than treated as permanent absence.
The memory cache is capped at 512 entries / 16 MiB and at one hour per entry.

Concurrent identical requests share a fetch. Database advisory locks also protect
overlapping candle fills across backend workers. Each successful candle window is
committed independently, preserving progress if a later window fails. Failed API
calls are not recorded as successful coverage. Failed database writes do not
populate memory or return unpersisted data. Failed live refreshes remain visible.
The gateway limits outbound calls to five per second per backend process by
default (`UPSTOX_REQUESTS_PER_SECOND`); option price requests use four workers.
Stored history can be read without an API token. Only an actual cache/database
miss requires credentials. Existing daily bars are adopted without a refetch;
legacy intraday bars remain readable during an outage with partial coverage marked.

Analytics that carry another session's data forward are rejected before storage,
using dated underlying candles and contract/session metadata. Future and
post-expiry observations are not substituted. Existing historical data does not
depend on a fresh live contract-master request.

## Historical hypothetical P&L

Provider OI is retained as underlying quantities, with `oi_unit=underlying_units`
in snapshots. Payout and premium valuation use `oi_in_units=True`: quantities
are multiplied by per-unit intrinsic/premium prices once, without another lot
multiplier. The generic research functions can still accept explicit lot counts.
P&L at spot is evaluated at the exact price, including between observed strikes.
Live P&L, like historical P&L, requires a usable premium for every OI-bearing leg.
Missing previous-session OI stays null rather than becoming a zero baseline.
Successful session calendars, including an empty calendar for a closed day, are
cached for a day. The page skips candle/analytics probes when that calendar
confirms the underlying exchange is closed, while respecting special sessions.

Expiry selection combines listed contract metadata with actual expiry identities
retained in PostgreSQL. It does not invent dates from a weekly/monthly calendar.
If only analytics establish an expiry, its cycle and lot size remain unknown.
This keeps history usable when the expired-instrument API requires Upstox Plus.

Completed storage migrations are recorded in `market_schema_migrations` under a
database advisory lock. A new store instance skips already-applied hypertable
DDL, avoiding schema lock upgrades while other workers are writing snapshots.

For the exact selected expiry and observation date, the adapter joins retained
contracts to dated OI and fetches each OI-bearing option's daily closing candle
through the gateway. Available closing prices persist in `candles` and remain
visible in strike details. If the option did not trade that session, the adapter
looks for its latest traded daily close on or before the selected date (up to
365 calendar days back). It first checks retained candles, verifies coverage
between a retained candidate and the cutoff, and fills only missing history
through the gateway. Current quotes and later trades are never substituted.

Full-portfolio P&L requires a dated premium for every leg with positive OI.
Missing legs are reported in `premium_prices`; they are not valued at zero.
Earlier traded closes can complete coverage, with the original price date,
calendar-day age and carried-forward flag exposed in the API and chart.
Zero-volume daily bars do not establish a traded close. The original candle
date remains unchanged in TimescaleDB: carrying a premium into a hypothetical
calculation never creates a candle for a session in which it did not trade.
If the latest earlier price cannot be verified, full-portfolio P&L stays unavailable.
This premium policy does not relax exact-session validation for OI or Max Pain.

Expired requests reuse bars saved under the active token and only call the
expired-instrument API for missing dates. The request includes the expiry suffix
documented by [Upstox](https://upstox.com/developer/api-documentation/get-expired-option-contracts/).
The [expired candle endpoint](https://upstox.com/developer/api-documentation/get-expired-historical-candle-data/)
is used for those misses. Hypertables follow the installed TimescaleDB
[create_hypertable API](https://www.tigerdata.com/docs/reference/timescaledb/hypertables/create_hypertable).

## Option Greeks in Max Pain

The `option_greeks` block exposes strike-wise call/put Delta, Gamma, Theta, Vega
and IV from the original Upstox option chain. Values are per option, with no lot
or OI multiplier; IV uses the chain endpoint's percentage representation. The
API's separate Greek-quote endpoint is not needed, avoiding redundant API calls.
The complete chain is already retained in the `market_responses` TimescaleDB
hypertable. No additional schema or synthetic Greek model is introduced.

Greeks are read from the latest capture for the exact underlying, expiry and IST
observation date, with the original acquisition time. Historical requests never
call today's option-chain or Greek-quote API. Only dates with verified session
data are eligible; pre-open undated captures are rejected. Missing captures or
fields remain unavailable, including when historical OI and closing premiums
exist. Captures need not be closing snapshots, and acquisition time is not an
exchange timestamp. An older current-session capture is explicitly labelled
retained. Signed put Delta/Theta and actual zero Gamma survive normalization.

## Verification

`GET /data/integration` reports the active storage path, hypertables, row counts,
dataset methods and process cache/DB/API counters. The Data page shows retained
data counts. Request-level identities and original responses are available in
PostgreSQL for audit.

### Max Pain IV history

`GET /options/iv/history` reads original REST chain responses and TimescaleDB
stream-chain captures through the gateway's 30-second memory cache. Historical
requests do not fetch today's option chain. An active current session can merge
fresh field-specific WebSocket values with the existing persisted REST seed;
the chart refreshes each minute. No separate duplicate raw store is introduced.

IV uses the selected expiry's closest-to-spot strike (lower strike on an exact
tie), averaging positive call and put chain IV percentages. Both legs and a
valid spot are required; a missing ATM IV does not fall back to a distant strike.
Only original regular-session acquisition times are accepted. A newer OI/price
tick cannot refresh old IV. Stream IV must be within 30 seconds, REST seed IV
within 60 seconds, and spot provenance must also be fresh to identify ATM.
Original per-leg IV times and spot field times are retained in stream captures.

The reference distribution is **expiry-specific**, with one last saved regular
session IV per prior day, up to 252 sessions in the preceding 365 calendar days.
Different expiries and underlyings are never mixed. This is an available-history
sample, not a constant-maturity underlying volatility index. The response and
chart show the session count and mark samples below 252 as partial. At least two
prior sessions are needed. Rank uses the prior range plus current IV; percentile
counts prior readings strictly below current IV. Constant ranges have no rank;
percentile ties are excluded. Future dates/readings cannot enter the baseline.
Captures near the close are not relabelled as official closing IV observations.

Expected move is `spot * IV/100 * sqrt(calendar_seconds_to_expiry / (365*86400))`,
using 15:30 IST on expiry day. The chart shows the positive ± amplitude in points
and the tooltip gives the model range around that capture's spot. A true zero
at expiry is preserved. This approximation is a one-standard-deviation model
range; it provides no directional or guaranteed-price-boundary claim. Missing
minutes and unavailable metrics remain gaps. Fullscreen has an independent AS OF.

Validation: `backend/scripts/test_iv_metrics.py` (with `RUN_MARKET_DB_TESTS=1`
for durable replay without provider calls), `frontend/scripts/test-iv.cjs`, and
the existing market-stream, Max Pain and chart regression suites.

Run from the workspace root in PowerShell:

```powershell
$env:RUN_MARKET_DB_TESTS = '1'
.venv\Scripts\python.exe -m unittest discover -s backend/scripts -p 'test_*.py'
.venv\Scripts\python.exe backend/scripts/test_premium_pnl.py
```

Database tests use unique `TEST_CACHE|...` fixture keys and remove only their own
rows. They cover memory/DB hits after restart, concurrent workers, interior gaps,
overlapping ranges, missing data retries, partial fetch failures, IST boundaries,
forced refresh, immutable history, retained contracts and TimescaleDB archives.
