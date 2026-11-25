# Bot readiness audit — 15 November 2026

Checked ahead of Monday 16 November 2026. All execution remains paper.

- API, configured PostgreSQL, both bot dashboards, frontend API proxy and referenced JS/CSS respond successfully.
- Upstox calendar confirms NSE/NFO sessions on 16 November. Direct historical candles, current contract master and V2/V3 quote requests succeed.
- All 11 F&O paper bots started after explicit user authorization; global kill released; healthy worker heartbeats verified. The later approved one-lot paper setup is recorded below.
- All four investment bots enabled with no control errors, latest processed session 13 November; 80 whole-share intentions, including two explicit zero-share rejections in C2-S.
- Investment reference accounts reconcile completed sessions the following morning. Monday reference fills appear after Monday daily bars are available (normally Tuesday morning); C0-R-X additionally depends on live auction evidence.
- Credit-spread paper monitor is running without errors. Spread entries are manual; this is not an automatic-entry bot.
- Market is closed on Sunday; retained Friday quotes and an idle WebSocket are expected. Live-session fills/freshness cannot be certified before the session opens.
- Fixed C0-R-X eligibility to use actual timezone-aware receipt time as well as slot label: responses received after the 09:05 cutoff cannot justify earlier entries. Wrong-session/undated receipts are excluded. API restarted to load the change.
- Sleep-after is disabled for both AC/DC in the current power scheme. The machine and API still need to remain running.

## Validation

130 tests passed: 41 F&O lifecycle/signal tests, 40 investment tests, 26 credit-spread tests including isolated PostgreSQL lifecycle tests, 16 stream tests, 7 application-origin tests.

## Approved one-lot paper setup

Applied after explicit approval: virtual capital ₹250,000 per bot; maximum loss budget ₹15,000/trade and ₹30,000/day; max_lots=1, max_quantity=null. Quantity uses the selected contract’s dated lot size, with no fixed unit ceiling. The 60-minute/time-cutoff exit remains in force.

Friday ATM 65-unit CE/PE lots required about ₹9,100 including modeled slippage and estimated fees. Without a stop, sizing reserves the whole premium as possible loss, so these lots exceed the ₹1,250 budget. Prior valid signals show this exact rejection.

All 11 bots have the approved one-lot setup in persistent paper configuration. New dynamic-lot and compatibility tests passed for contract sizes 25, 65, 175 and 1,000; the complete F&O suite passes 46 tests. The production frontend build passes. Previous trade/order journals are unchanged. Monday prices can differ; valid signals and fresh executable quotes are still required.

Community research data and results remain local; no community observations were inserted into PostgreSQL.
