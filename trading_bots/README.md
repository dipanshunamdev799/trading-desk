# Trading Bots

Eleven independent option-buying workers, connected to the existing Trading Desk
at [Trading Bots](http://127.0.0.1:3000/trading-bots). Execution defaults to
**PAPER**, with eligible paper bots started automatically when the application
starts. Development and verification place no real broker orders.

## Structure

```text
trading_bots/
  ema_trend_bot.py
  failed_breakout_bot.py
  pullback_bot.py
  donchian_bot.py
  momentum_bot.py
  compression_breakout_bot.py
  orb_bot.py
  ema_reversion_bot.py
  gap_follow_bot.py
  gap_fade_bot.py
  rsi_reversion_bot.py
  catalog.py                    # Explicit registry, no arbitrary module loading
  common/
    strategy.py                 # Causal indicators and common session filters
    market.py                   # Existing Upstox gateway, dated contracts, book checks
    broker.py                   # Paper broker and separately gated live adapter
    engine.py                   # Durable execution, fills, exits, shared risk gate
    store.py                    # Separate journals and atomic global reservations
    manager.py                  # Controls, worker spawning, restart recovery
    worker.py                   # Independent process, heartbeat, CLI
    config.py                   # Validated configuration models
  config/paper.example.json     # Complete default bot configuration
  logs/                        # Runtime files, ignored by Git
    <bot_id>.sqlite3             # ONE trade/signal/order/event journal per bot
    <bot_id>.worker.log          # Worker stdout/stderr
    control.sqlite3             # Global limits, leases and reservations ONLY
backend/app/routers/trading_bots.py
frontend/app/trading-bots/{page.tsx,bots.css}
backend/scripts/test_trading_bots.py
```

Signals carry a stable ID, decision time, spot direction/price, underlying,
indicators, strategy parameters and reason. The engine resolves the dated option,
records the quote, applies execution limits and calculates quantity/stop/target.
The persisted order intent contains the complete execution inputs before any
submission. Every bot uses this engine and cannot bypass the risk gate.

## Exact ranked entry rules

| Rank | Bot ID / script stem | Rule | Filter | Window |
|---:|---|---|---|---|
| 1 | `ema_trend` | EMA12/26 separation > 0.5 ATR | Trend | Afternoon |
| 2 | `failed_breakout` | Reject a prior 20-bar range break | Range | All |
| 3 | `pullback` | EMA9/21 pullback, 0.75 ATR tolerance | EMA alignment | Afternoon |
| 4 | `donchian` | Prior six-bar breakout, zero buffer | Trend | Afternoon |
| 5 | `momentum` | Three-bar movement > 0.5 ATR | Normal volatility | Morning |
| 6 | `compression_breakout` | Prior six-bar span < 3 ATR, body > 1 ATR | Trend | Afternoon |
| 7 | `orb` | 15-minute opening range, 0.25 ATR buffer | EMA alignment | Afternoon |
| 8 | `ema_reversion` | Distance > 2 ATR from EMA21 | Range | Morning |
| 9 | `gap_follow` | Follow gap > 3 ATR, before 11:00 | High volatility | All |
| 10 | `gap_fade` | Fade gap > 3 ATR | Range | All |
| 11 | `rsi_reversion` | RSI40/60 with corresponding EMA21 distance | Range | Morning |

Every script ends in `_bot.py` and owns its specific entry predicate and
definition. Shared mechanics are reused. The tests compare all eleven signal
arrays with the original `scripts/research_directional_lab.py` definitions.

Five-minute bars become eligible only after completion. Research bar-start
windows are morning 09:30–10:55, afternoon from 13:00, and all from 09:30 IST;
decisions occur five minutes later. The baseline holds 60 minutes, accepts no
entry whose planned exit exceeds 15:10, and allows one position per bot. Gap
strategies deliberately retain the previous complete **15:10 research close**.
They do not substitute the exchange's official close.

Entry rules and ranking are from the historical **index-direction** study.
Live/paper option selection is an explicit execution policy: buy CE for a bullish
signal or PE for a bearish signal, nearest listed expiry strictly after today,
ATM strike (lower strike wins a tie), and the contract's dated lot size. Expiry-day
contracts are excluded. This policy and optional premium exits have not been
established as profitable by the index ranking. The dashboard starts at zero and
reports only its own execution journals.

## Run and configure paper trading

Use the existing launcher, then open Trading Bots. **Global Start** starts or
resumes paper bots together and releases an active global kill switch. Paper
bots also start on API startup and on launcher invocation; existing healthy
workers are reused. A saved kill switch stays active across automatic startups.
Live bots still require individual confirmation, and retained positions/orders
needing recovery stay paused for review while protection continues.

Stop and flatten a bot before saving its configuration. Pause blocks entries while
continuing order reconciliation and position exits. Resume enables entries.
Stop & close requests closure and exits the worker when flat.

Run independently from the repository root with the same Python environment:

```powershell
# Foreground worker; starts this bot in its saved mode
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot

# Background controls and status, with no dashboard dependency
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot --command start
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot --command pause
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot --command resume
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot --command stop
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot --command status

# Save a complete JSON configuration; this command does not start the bot
.\.venv\Scripts\python.exe -m trading_bots.ema_trend_bot --config trading_bots\config\paper.example.json
```

Direct execution such as `python trading_bots\ema_trend_bot.py --command status`
also works. Substitute any bot ID from the table. Python dependencies are in
`backend/requirements.txt`. The market adapter reuses `UPSTOX_ANALYTICS_TOKEN`
and the existing configured PostgreSQL/TimescaleDB gateway. Bot journals use
SQLite. Docker is optional if that configured database is already available.
Fixtures and lifecycle unit tests do not need Docker or a working broker token.

| Setting | Default |
|---|---:|
| Allocated capital per bot | ₹250,000 |
| Maximum units | 650, rounded down to the dated lot |
| Maximum planned loss per trade / daily loss room | ₹1,250 / ₹2,500 |
| Daily trade attempts / per-bot simultaneous positions | 5 / 1 |
| Premium stop / target / trailing stop | All blank (time exit baseline) |
| Maximum quoted spread / quote age | 2% / 5 seconds |
| Maximum signal age | 10 seconds after completed bar |
| Monitor interval / unfilled order timeout | 5 / 15 seconds |
| Paper adverse slippage per unit / estimated brokerage per order | 0.05 / ₹20 |
| Shared positions / reserved capital / order attempts per minute | 3 / ₹750,000 / 20 |

With no stop, sizing reserves the whole premium plus estimated fees as possible
loss. A minimum lot commonly exceeds the default ₹1,250 budget: that signal is
skipped with an explanation. Increase a paper budget deliberately or configure
an optional premium stop for a different execution profile. Stops are polled
software conditions, not broker-held protective orders; price gaps, disconnects,
partial fills and slippage can exceed planned losses. Daily limits block entries
based on remaining realized-loss room; they cannot guarantee a loss ceiling.

Capital and order slots are reserved atomically across bots before submission.
Per-bot quantity/cash/risk/day-count checks also run inside that transaction.
Cash available for new trades cannot exceed configured capital and is reduced by
accumulated realized losses. A global entry budget reserves order capacity for
exits; cancellations count against the shared rate too. Limits cover these bots,
not unrelated programs or manual broker orders. One position per bot is fixed
to preserve the researched single-position lifecycle; shared concurrency is editable.

Global kill blocks entries immediately and requests Stop for every bot. Releasing
kill alone does not restart bots; **Global Start** releases it and starts eligible
paper bots. Individual Start cannot bypass an active kill switch.
No close is invented when a usable quote or broker
acknowledgment is missing: exposure stays visible as OPEN, STOPPING or UNKNOWN.

## Data, logs and recovery

Each worker warms recent five-minute NIFTY history and requests current intraday
bars at bar boundaries. It checks OHLC validity, session continuity, signal age,
actual session state, bid/ask/depth, spread, quote receipt time, source timestamp
and last trade time. Missing required context blocks trading. REST timestamps
are feed/last-trade proxies, not verified order-book event timestamps.

Paper fills cross the observed spread once, add adverse slippage, respect limit
price/depth and cancel the unfilled remainder. They do not model queue position
or subsequent liquidity. After a crash, an unacknowledged paper intent cancels
its unconfirmed remainder; recovery never replays an old quote into a new fill.
Partial exits submit only the remaining position after
the prior exit is terminal. Gross/net P&L and estimated fee components are
recorded separately; live charges require contract-note reconciliation.

Journals contain entry/exit reasons, signal and indicator inputs, order intents,
broker results/errors, cumulative fills, fees, holding time, rejected/skipped
signals, controls and configuration changes. Trades reference their full order
history by trade ID. Timestamps are UTC with offsets; the dashboard shows IST.
CSV exports have ordinary trade/order columns and an unabridged `data_json`
column. The dashboard shows the latest 200 signals/300 events; exports retain all.

Use `TRADING_BOTS_DATA_DIR` to select an isolated storage directory. All workers
and API instances controlling the same account must use the **same local**
directory for shared risk. Do not run separate live installations with separate
reservation databases on the same account. Do not delete journals to reset a bot
with unresolved exposure. Back up the complete directory while workers are
stopped; attached SQLite databases use full-sync rollback-journal transactions.

Workers have independent processes and 30-second heartbeat leases. Duplicate
workers cannot acquire the same bot lease; stale owners are fenced from writes.
On API restart, a healthy existing worker is reused. An interrupted bot with
retained exposure is restarted PAUSED for reconciliation and exits. Flat paper
bots are started automatically unless the global kill switch is active. Live
bots remain behind their individual confirmation gate. A process
failure is visible as ERROR; there is no claim that a crashed host can manage
positions until restarted.

Order intents survive a crash before acknowledgment. Reconciliation uses the
broker order ID or the stable tag, applies cumulative fills by deltas, and never
blindly repeats placement. Timeouts or ambiguous cancellations keep reservations.
A partial entry waits for terminal cancellation/confirmation before the remaining
position becomes eligible for an exit, avoiding an oversell. Orders that cannot
be matched, or have multiple tag matches, freeze entries for broker-side review.
There is no automatic assertion that an unmatched order never existed. Upstox's
ordinary order-detail/book endpoints have limited session retention, so unresolved
prior-session orders need manual broker reconciliation; this implementation does
not reconstruct them from a contract note or provide a manual accounting override.

Workers outlive the web/API processes. **Stop & close and verify flat before
using `stop_web_app.bat`, shutting down the computer, rotating live credentials,
or changing the execution account.** Ctrl+C requests graceful stop; it cannot
complete an unpriced exit. Keep the host awake for monitoring. If manually
intervening at the broker, stop entries and reconcile bot journals before resuming;
the engine does not import unrelated/manual fills or broker auto-square-offs.

## Live broker integration and activation

Live execution was not enabled or exercised during development. The adapter uses
Upstox V3 LIMIT placement/cancellation and V2 order details/book. It requests
intraday product `I`, disables slicing, uses one stable tag per intent and does
not retry placement after an exception. It is distinct from the analytics client.
Official references: [V3 placement](https://upstox.com/developer/api-documentation/v3/place-order/),
[cancellation](https://upstox.com/developer/api-documentation/v3/cancel-order/),
[order details](https://upstox.com/developer/api-documentation/get-order-details/),
[order book](https://upstox.com/developer/api-documentation/get-order-book/).

When ready for a separately supervised live rollout, configure these settings
privately in the root `.env` or process environment, then restart the API/workers:

```dotenv
TRADING_BOTS_LIVE_ENABLED=true
UPSTOX_TRADING_TOKEN=<separate current trading access token>
# Only for an applicable exchange-approved algo name configured in the broker app
UPSTOX_ALGO_NAME=
```

The app never copies the analytics token to execution, returns the trading token
to the dashboard, or writes it into source/journals. Keep `.env` outside Git.
Upstox documents registered-app/static-IP restrictions and an optional
`X-Algo-Name` header for applicable exchange-approved algos in its placement docs.
Confirm account/API permissions and current broker requirements before activation.
This app cannot grant them. It also does not reconcile broker available funds,
manual positions or external order traffic; allocate capital accordingly.

With the bot stopped and flat, choose Live in Configuration and type
`ENABLE LIVE <bot_id>` to save. Every live Start/Resume separately requires
`START LIVE <bot_id>`. For CLI activation, save a JSON with mode `live` using
`--config <file> --confirm "ENABLE LIVE ema_trend"`, then use
`--command start --confirm "START LIVE ema_trend"`. Environment gate, separate
token and explicit per-bot activation must all be present. Disabling the gate or
removing the token while exposed prevents reconciliation/closure too.

## API and verification

Routes under `/trading-bots`: GET `/dashboard`, POST `/global/start` (paper bots),
POST `/startup` (automatic policy, preserves a saved kill switch),
GET `/{id}`, POST `/{id}/control`,
PUT `/{id}/config` with `{config: {...}, confirmation: "..."}`, PUT `/global`, and
GET `/{id}/export?kind=trades|orders|signals|events`. The frontend proxies them at
`/api/trading-bots`. Mutations accept only configured `CORS_ORIGINS` when an
Origin header is supplied. Same-origin requests through a loopback frontend
proxy also work on preview ports when the forwarded origin and browser Fetch
Metadata match. Cross-site, opaque and mismatched origins stay blocked. This
remains a local app without multi-user auth; keep its API bound to loopback.
Other frontend deployments need an explicit origin in `CORS_ORIGINS`.

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe backend\scripts\test_trading_bots.py
# From frontend/: npm.cmd run build
```

Tests use temporary journals and deterministic fixtures. They cover complete
entry/exit accounting, invalid/stale inputs, risk and daily-loss rejection,
duplicate/restart protection, partial/rejected/uncertain orders, tag recovery,
shared concurrent reservations, throttling, live gates, global kill,
API/export/origin validation, independent worker failure and exact signal parity.
See `artifacts/trading_bots_verification.md` for the recorded run and UI checks.
These checks validate implementation behavior, not a profitable trading edge.
