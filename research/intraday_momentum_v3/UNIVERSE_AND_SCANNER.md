# Point-in-time universe and scanner

The 15 November plan contains 479 current ordinary NSE EQ identities: 99 surviving V2 core stocks, 300 broader stocks and 80 observation-only names without usable local daily history. This is a broader experimental cohort, not unrestricted coverage of every listed stock. `universe-current.json`, the dated `universes/` snapshot and the metadata hashes reproduce it.

## Before-session selection

Use only authentic Upstox daily bars already in PostgreSQL, strictly before the local session date. Read up to 180 calendar days and retain the last 63 available daily observations. Calculate median daily close-times-volume turnover, median daily high-low divided by close, last close and history age. This turnover is a close-price proxy, not actual exchange traded value.

Retain current ordinary-EQ identities from the frozen V2 core. Among the original approximately 500-stock cohort, admit broader stocks with at least 20 available daily observations, median turnover at least Rs50 million and last close at least Rs50. Rank by lagged median daily range, with a date/key hash tie-break, taking at most 300. Add at most 80 current MIS-listed names outside this set that lack local history, by deterministic date/key hash. Lack of history does NOT establish liquidity, new-listing status or trading eligibility; the group label means new to this observation cohort only.

Daily history older than seven calendar days is stale. Unknown/stale history permits observation but rejects funded shadow sizing. Membership is frozen per local day; same-day restarts reuse it. Metadata refreshes on a new day's startup. HFCL is documented as excluded because it currently trades in BE rather than ordinary EQ. A current listing is not a historical point-in-time eligibility certificate.

## Controls and subscription budget

Choose up to five deterministic controls in each of four pre-session bins: turnover above/below Rs1 billion and last close above/below Rs500. Today's plan has 20 controls. Keep those plus up to ten core instruments continuously in full mode, with a maximum fixed cohort of 30. Rich subscriptions are capped at 40, leaving at least ten dynamic slots. The 479-stock broad stream uses LTPC; NIFTY 50 and India VIX add two context keys. One connection is owned by this observer. D30 remains off.

REST is a separately labeled product: a broad full-quote request approximately every 30 seconds and at most 40 watchlist snapshots approximately every five seconds. Actual wall-clock cadence includes request and commit time and is measured, not promised. Requests batch at most 500 keys. The broad snapshot supplies occasional volume/turnover information that LTPC does not contain; absent data is not invented.

## Causal intraday rotation

Every 30 seconds rank only observations available by that time and still fresh under their transport rule. Score = absolute return from previous close + twice absolute return from the previous observed update + min(last-price times cumulative-volume / Rs10 billion, 0.02). Missing volume contributes zero to this coarse ranking. This is a watchlist score, not an alpha forecast or a calibrated relative-volume statistic. Its update-to-update acceleration depends on observed cadence.

Keep fixed controls regardless of rank. Fill remaining slots from the highest scores with stable key tie-breaking. Log each rotation, added/removed keys, score components, membership reason and subscription generation. Reject source-time rollback; past selections exclude future-available observations. Unknown-liquidity names can enter observation slots but cannot automatically become economic trades. Do not select stocks using eventual daily returns, end-of-day volume or later news.

The signal evaluator receives only actually observed rich quotes. Rapid rotation may leave too little history for 5- or 6-minute features; that candidate is missing until sufficient causal data exists. Continuous controls measure this selection-related missingness. Matched controls at each event must share the current price and pre-session turnover bins, be fresh at the same timestamp and use the same transport. Missing matches are logged, not discarded because their later outcome is inconvenient.
