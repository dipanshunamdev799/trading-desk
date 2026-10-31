# NIFTY credit spread paper desk

Open [the strategy desk](http://localhost:3000/credit-spreads), or choose
**NIFTY Credit Spreads** in the sidebar. The general Paper page also links here.
Use the existing `launch_web_app.bat` to start the database, API and frontend.
Migration `006_credit_spreads.sql` runs automatically at API startup and preserves
existing paper orders and market history.

## Use

1. Set the paper starting capital and execution assumptions in **Account settings**.
   Defaults: ₹10,00,000, ₹25 per leg order, 0.05 points adverse slippage per leg,
   automatic exits enabled. Fees are an editable all-in estimate, not a broker tax
   calculation. Capital means the starting balance; realized P&L is added to it.
2. Review Daily, 1-hour and 15-minute candles. Select Bear Call or Bull Put, a listed
   expiry, short and protective strikes, whole lots and the actual chart level.
   Delta-based initial selections are convenience inputs, not trade recommendations.
3. Write an entry thesis. Confirm structure, a completed 15-minute candle, and
   event/gap-risk review. These three observations require manual review.
4. All 15 entry checks must pass. The first nine follow the supplied checklist;
   the others enforce portfolio risk, session/time, contract structure, liquidity
   and no averaging. Risk limits include maximum theoretical loss plus estimated
   round-trip fees. The sizing balance is starting capital plus realized P&L.
5. Open the paper spread. Both simulated leg fills, their fees, a spread position
   and its entry checklist commit atomically in PostgreSQL. Request identifiers
   prevent duplicate fills after retry. Rejected entries are also recorded.
6. Use **Positions** for open spreads and manual/technical exits; **Journal &
   analytics** for recorded trades and results; **Order log** for each leg fill,
   rejection and exit request. Both journals support CSV export.

## Data and exits

- Existing Upstox gateway and contract master supply expiry, strike, lot size,
  bid/ask, available quantities, delta and IV. No fabricated prices or fixed
  expiry weekdays/lot sizes are used. Chains are matched by exact contract identity.
- Account polling is every 5 seconds. Bid/ask is normally retained at a one-minute
  REST cadence and is rejected after 65 seconds. Candles refresh every minute;
  stream notifications also trigger account refreshes. This is an auto-updating
  paper simulation, not tick-by-tick or exchange execution.
- Streaming LTP and Greek updates cannot make old bid/ask depth fresh. The REST
  seed acquisition timestamp is shown; it is not an exchange trade timestamp.
- Entries sell at bid and buy at ask. Closes buy the short at ask and sell the
  hedge at bid. Slippage worsens each fill. Both sides require enough displayed
  units for the entire order; there are no partial or naked-leg simulated fills.
- The backend monitor runs every 10 seconds while the API is running, even if the
  browser is closed. It checks net debit against 50% credit, 2× credit, and 2 DTE.
  Session closure or unusable quotes defer a fill; requests persist across restart.
  Stops use the actual available debit, including worse prices after a gap.
- If the 2-DTE deadline falls on a closed exchange day, the monitor exits in the
  preceding available session. An unverifiable near-expiry calendar triggers a
  conservative early time exit, rather than assuming a future session exists.
- Technical invalidation is a manual exit reason after reviewing the hourly
  candle and failed retest. There is no automated macro-event calendar.
- No simulator can execute during backend downtime. Resume the API to resume
  monitoring. The page flags a delayed monitor and stale marks. Expired contracts
  without executable quotes are not silently settled with invented prices.

## Accounting and limits

Trade records retain entry delta, IV, calendar DTE, spread width, quantity, entry
credit, theoretical risk, fees, target/stop debit, actual exit debit, entry/exit
reasons and observed MAE/MFE. Journal P&L includes entry and exit fees, with
slippage already in each fill. Open MTM includes estimated exit fees. Unknown
marks stay null; stale marks are labelled. MAE/MFE reflect captured observations
and can miss movement between updates.

Equity and drawdown charts use closed trades; account equity also includes the
last available open MTM. Expectancy and win rate use closed net results. Profit
factor is unavailable without a losing trade. Return on risk uses total reserved
theoretical risk. Account assumptions are locked while any spread remains open;
completed trades retain their original costs. One same-direction spread can be
open at a time. This stricter no-averaging implementation also avoids adding
correlated positions.

Storage: `credit_spread_account`, `credit_spread_trades`, `credit_spread_orders`,
`credit_spread_marks`. Every writer takes a transaction lock on the account row
before risk checks and mutations. Existing generic paper tables are independent.
The order screen shows the latest 500 records; CSV includes the full order log.
The debit chart loads the selected spread's latest 3,000 observations separately
from account polling. Older observations remain retained in the database.

## Verification

From the workspace root in PowerShell:

```powershell
$env:RUN_MARKET_DB_TESTS = '1'
.venv\Scripts\python.exe backend/scripts/test_credit_spreads.py
cd frontend
npm run test:credit-spreads
npx tsc --noEmit
```

PostgreSQL lifecycle tests create and remove a uniquely named isolated test schema;
they do not write test trades to the user's strategy account. Coverage includes
both directions, contract sizing, stale/missing fields, session/time rules,
credit/risk gates, concurrent retry, fills and fees, stop gaps, manual/technical
exits, persistent requests, restarts, and journal export.
