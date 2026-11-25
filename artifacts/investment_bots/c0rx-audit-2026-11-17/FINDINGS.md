# C0-R-X operational audit — 17 November 2026

Checked at09:40 IST. The bot is enabled, its investment kill switch is off, the scheduler is checking inputs, and its latest completed-session data is16 November. No trading-rule failure was found in the saved decisions.

## Why it has no trades

- The13 November decision generated20 initial buy intentions for16 November.
- The application captured all14 scheduled auction/opening snapshots on16 November, covering all20 names. Their stored checksums match. The selected09:04:30 decision snapshot arrived09:04:44.643513, before the09:05 cutoff; the09:12:30 post-match snapshot arrived09:12:41.616703.
- Every stock had a nonzero `indicative_imbalance_quantity_market` at the decision snapshot. The frozen C0-R-X rule requires exactly zero; each candidate was classified `uncertain_market_imbalance` and logged `DROPPED / fill_not_assumed`.
- Independent read-only classification of all20 intentions and a pure replay using authentic PostgreSQL opening/closing bars reproduce the saved executions and portfolio exactly.
- The portfolio therefore holds no positions, has no pending buys/sells, and retains its fullRs1,000,000 cash.
- Today17 November is not a five-session rebalance date, so the dropped buys are not automatically retried. Missing fresh capture today is expected because there are no positions or current intentions to observe.

## Schedule and reporting convention

The anchor is13 November. Actual session offsets are13Nov=0,16Nov=1,17Nov=2,18Nov=3,19Nov=4,20Nov=5. Upstox's calendar confirms the upcoming sessions and21-22 November closure. The next scheduled selection review is20 November close; next possible paper fills are23 November open, provided stock selection and that morning's auction evidence pass. They are not guaranteed. This is a next-morning reference reconciliation: any23 November execution would normally appear in the24 November morning ledger, rather than intraday on23 November.

The earlier16 November DNS error is retained in logs, but it did not prevent the14 genuine snapshots or explain these gate rejections. Current worker status has no error. Forty investment tests passed, including the auction classifier, timing, replay, frozen-engine comparisons and independent controls. Existing strategy rules, controls and portfolio records were not changed. No broker order was submitted.

See `candidate-gates.csv` for every symbol, intended quantity, actual decision snapshot values and saved/recomputed rejection. Reproduce with `.venv/Scripts/python.exe scripts/audit_c0rx.py`; it uses server-enforced read-only PostgreSQL transactions and writes only local audit artifacts.
