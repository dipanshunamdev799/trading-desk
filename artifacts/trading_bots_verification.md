# Trading Bots verification — 10 November 2026

## Automated checks

`python backend/scripts/test_trading_bots.py`: **31 tests passed** in 52.181s.
Tests use temporary SQLite journals and deterministic market/broker fixtures.
No live trading token is used; the process-isolation test explicitly disables
the live environment gate and clears its trading token.

Coverage includes:

- Full paper entry, paused position monitoring, time exit and durable P&L/fees.
- Invalid OHLC, stale quotes, expired signals and disconnected entry inputs.
- Per-trade risk, daily-loss room, capital, quantity and daily trade counts.
- Persisted duplicate prevention and restart with an open position.
- Partial entries/exits, cumulative live-adapter-style fill updates and cancellation.
- Rejected orders, ambiguous placement without a retry, and tag-based recovery.
- Unacknowledged paper-intent recovery cancels its remainder without replaying
  historical quotes or fabricating fills after a restart.
- Lease ownership/fencing and concurrent bots reserving the final global slot.
- Shared order throttling with exit capacity, global kill and unpriced stop.
- Optional premium stop, target and trailing high-water recovery after restart.
- Configuration locking, execution-mode races and the separate live gate.
- Actual independent worker processes: one reports an activation error while
  the other stays healthy; both stop cleanly without remote placement.
- CLI configuration saving without starting a bot.
- FastAPI routes, validation, origin guard and CSV exports.
- Exact signal-array parity for all eleven ranked configurations against the
  frozen research implementation.

`npm.cmd run build` in `frontend/`: production compilation, type checks and
generation of all 14 pages passed, including `/trading-bots`. Repeated after the
browser check's date-input compatibility correction.

## Browser and process checks

Preview used a separate API on port 8107, frontend on 3001, and journals ONLY in
`data/bots-ui-test/`. No production bot trade history was seeded.

- All eleven bots initially appeared STOPPED/PAPER with zero P&L.
- Start created a real worker and showed RUNNING plus a fresh heartbeat.
- Pause and Resume changed the persisted states and visible controls correctly.
- Stop ended the worker; the final API check confirmed STOPPED, no healthy
  worker, no orders and no positions before creating the isolated history fixture.
- Paper configuration saved through the UI. Its preview origin was explicitly
  allowed through `CORS_ORIGINS`; the application's default origin guard remained.
- A deterministic `NIFTY TEST CE` fixture was opened/closed through the paper
  engine in the isolated preview journal. Its hypothetical gross ₹643.50,
  estimated charges ₹63.85 and net ₹579.65 are **test data**, not strategy evidence.
- Symbol/status/bot/date filters and the complete trade-details modal were
  exercised. The date filter correctly excludes the 6 November fixture when its
  start date is 7 November, and includes it for 6–6 November.
- Native date-input compatibility required listening to input updates as well
  as change events; this was corrected and verified in the browser.
- Both the preview and default journal sets were finally checked: all bots
  stopped, no running workers and no open/unresolved positions. Preview servers
  were shut down after verification. No live activation or real broker order
  was performed.

Screenshots: [dashboard](trading_bots/dashboard-paper-test.png) and
[filtered history](trading_bots/history-paper-test.png). The history screenshot
uses the explicitly named test instrument and isolated journal above.

## Limits of this verification

This validates execution/control/persistence behavior and research rule parity.
It does not validate option profitability or production broker execution. Real
Upstox placement, fills, cancellations, static-IP permissions and account-side
reconciliation remain unexercised. Use the broker integration instructions in
`trading_bots/README.md` before a separately supervised live rollout. Charges
are estimates, software stops can be exceeded, and unmatched prior-session
orders/manual broker interventions require reconciliation outside this app.
