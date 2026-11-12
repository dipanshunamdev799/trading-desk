# Trading Desk

Local NIFTY research, option analytics, IPO research, backtests and paper trading.

## Find your way around

Start with **Overview** for a suggested path through the desk. **Learn the desk**
(`/learn`) contains three hands-on exercises, a local P&L calculator and a searchable
glossary. Check off exercises as you try them; progress stays in this browser when
local storage is available. The calculator uses illustrative values and works even
when market connections are unavailable.

Navigation groups the tools into **Explore markets**, **Practise & review** and
**Advanced tools**. Use **Find a tool** (or `Ctrl+K`) to search all destinations.
Each research and practice page has a **First time here?** guide with a workflow,
definitions and a suggested next step.

NIFTY starts with a focused **Overview**; **Full research** opens the complete
factor map, observations, positioning, calendar and import tools. The paper order
form provides familiar stock names, a custom instrument option and an order review.
Its chosen-price simulation fills immediately at the entered price; it does not
wait for a limit-order trigger.

Directional strategy research, frozen experiments and premium-validation requirements:
[NIFTY research report](C:/Users/ME/Desktop/trading-desk/NIFTY_DIRECTIONAL_RESEARCH.md).
The report distinguishes index-direction experiments from option-premium profitability.
The [deeper validation and option-premium study](C:/Users/ME/Desktop/trading-desk/NIFTY_RESEARCH_PHASE2.md)
adds longer history, controls, contextual features, exact-contract premium replays
and a forward observation journal.

## Run on Windows

Install Python 3.11 or newer and Node.js 20 or newer. If a configured
PostgreSQL/TimescaleDB instance is already available, Docker is optional.
Otherwise install and start Docker Desktop for the bundled database. Then
double-click `launch_web_app.bat`.

The launcher creates `.venv`, installs missing/changed dependencies, connects to
the existing configured database (or starts TimescaleDB), applies all SQL
migrations, builds the frontend, and opens <http://localhost:3000> only after the
web app and API connection are ready. Repeating the launch reuses healthy
services. The initial installation/build can take a few minutes.
Readiness includes the JavaScript/CSS referenced by the Desk and IPO pages.
If a build was replaced underneath a running frontend, launching again repairs
that managed frontend automatically. The launcher does not stop an unrelated
process occupying the port.

- Web: <http://localhost:3000>
- API documentation: <http://127.0.0.1:8000/docs>
- Diagnostics: `data/logs/` (including dependency, build and service logs)
- Stop: double-click `stop_web_app.bat`. This stops only processes recorded by
  this launcher, preserving the database container and its stored history.
- After editing source files, stop and launch again to rebuild the web app and
  restart the API. For development, run the API separately and `npm run dev`
  from `frontend/`.

Command-line launch without opening a browser:

```powershell
.\launch_web_app.bat -NoBrowser
```

## Configuration and data

Backend settings load from the repository-root `.env` regardless of the launch
directory. Use `UPSTOX_ANALYTICS_TOKEN` for Upstox and optionally
`TAPETIDE_TOKEN` for the supported fallback datasets. The token indicator reports
whether a token is configured; it does not certify provider availability.
Retained history stays readable when providers have no new observations.

The default database is PostgreSQL/TimescaleDB at `127.0.0.1:5432`, database
`trading`, user/password `trading`. For a different TimescaleDB instance, set
both `DATABASE_URL` (`postgresql+asyncpg://...`) and `DATABASE_URL_SYNC`
(`postgresql+psycopg2://...`) to the same database. Web/API ports are 3000/8000.
If an unrelated process owns either port, the launcher reports the conflict
instead of opening a different port or terminating that process.

The Compose project has a stable `trading_v2` name, preserving the original
`trading_v2_trading_pgdata` volume when this folder is moved or cloned.
Database initialization runs all `backend/sql/*.sql` migrations, including the
base tables on an empty database. Do not delete volumes to resolve a startup
problem.

Pages: Overview, Learn the desk, NIFTY, Options & max pain, IPOs, Backtests, Strategies,
Paper, Trading Bots, NIFTY Credit Spreads and Data. `/charts` redirects to NIFTY,
whose OHLCV explorer provides custom ranges.
The Data page reports retained candle coverage and storage statistics.
Paper orders and credit spreads never send real broker orders.

IPO subscription collection uses the public JSON feed behind the
[IPOWatch tracker](https://ipowatch.in/ipo-subscription-status-today/).
Published bidding dates and category history are retained separately from
retrieval timestamps. Missing readings remain distinct from zero; differing
Upstox/public totals retain their source notes. Failed or malformed responses
raise a source warning instead of being recorded as an empty successful feed.

The [Trading Bots section](http://localhost:3000/trading-bots) runs the eleven
ranked directional strategies as independent workers with separate journals,
paper execution, shared risk limits and a global kill switch. Live execution
requires a separate trading token and explicit activation. See the
[bot architecture, configuration and run instructions](trading_bots/README.md).
Paper bots start automatically with the application. Global Start starts/resumes
eligible paper bots together; a saved global kill switch blocks automatic startup
until it is deliberately released. Live bots still require individual activation.
Stop bots and verify they are flat before shutting down the application/host;
workers continue independently of the web/API processes.

The [Strategies desk](http://localhost:3000/strategies) assesses all eleven
directional families against one market snapshot. It shows strategy-specific
weights, signed contributions, dependence groups, source age, conflicts and
missing-data penalties. See [the scoring method](STRATEGY_EVALUATION.md) for the
confidence formula and requirements for historical factor validation. Assessment
confidence is a research score, not a calibrated probability of profit.

Place backtest JSON outputs in `backtests/`; use the included files as format
examples. `sample-momentum-nifty.json` is sample data, not a live strategy result.

## Verification

With the app running, exercise every page, primary data endpoints and the
websocket connection through the frontend proxy:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_web_app.py
```

Backend tests, including local database integration tests with isolated test
instrument keys:

```powershell
$env:RUN_MARKET_DB_TESTS = '1'
.\.venv\Scripts\python.exe -m unittest discover -s backend/scripts -p 'test_*.py'
```

Frontend tests (from `frontend/`):

```powershell
node --test scripts/test-*.cjs
```

Use the launcher to rebuild and restart production after stopping the app.
For a build check while the app is running, isolate the output so its active
JavaScript files are preserved:

```powershell
$env:TRADING_DESK_NEXT_DIST = '.next-check'
npm.cmd run build
Remove-Item Env:\TRADING_DESK_NEXT_DIST
```
