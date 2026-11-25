# V4 data availability audit

No new indicator search was conducted. Existing feature definitions are frozen.
The underused-source hypotheses below are an information inventory, not a claim
that adding each source improves a price-only benchmark. The matched V3 price/
sector controls and V4 removal diagnostics are the measured comparisons.

|source|hypothesis|availability|evidence/risks|
|---|---|---|---|
|Sector indices/participation|Independent leadership/breadth beyond index price|Completed dated sector bars; no constituent-membership claim|Sector removal harms tree point score; sector definition drift/correlation remain|
|Stock momentum dispersion|Cross-sectional fragility beyond aggregate price|Current-basket backcast only|RESEARCH ONLY; no authenticated dated membership/weights|
|FO basis/OI/PCR|Positioning adds incremental state information|Official dated archives; additional 1-session lag|Separate FO ablation .228148 vs original .226049; roll/lot/report delays|
|Institutional positioning|Flow/position shifts condition future return|Short authenticated history; new missing reports not fabricated|Removal identical tree outputs here; missingness/prevalence drift|
|Complete intraday structure|Path persistence/range adds information beyond daily bars|At least 70 bars, start09:15/reach15:20; authenticated new capture|Removal .226082; partial sessions remain missing|
|ETF volume/turnover|Tradable activity proxies participation|Real ETF candles, not spot volume|Removal identical tree outputs; development ETF q~.296|
|Indian/global relative strength|Domestic resilience conditions global shocks|Conservative strictly preceding global source dates|Existing global/sector features only; no new indicator added; timezone/revision risk|
|IV/Greeks/news/events|Potential new state/surprise information|No authenticated historical panel for this study|UNAVAILABLE; never manufactured or backfilled|

Live rehearsal reference: 2026-11-17, NIFTY close
25,387.40; fresh daily sources and the official
underlying crosscheck corroborate the reference. Capture contains
22 successful HTTP responses with actual
local send/receive clocks, available HTTPS server Date, raw bytes and SHA256.
Observed overlapping daily source revisions: 0.
Missing latest feature names are saved verbatim in availability.json. Stock proxy
inputs are not refreshed or admitted to frozen primary features. Institutional
history is not silently extended; absent new values remain missing and the exact
frozen train-median imputer handles them. This operational limitation is disclosed.

Incremental acquisition starts16 November and ends at the previous completed
reference, merges the immutable2025-onward base, and never retrieves pre-2025
prices. All new reference/target dates are scope-checked. Primary runs halt on
overlap revisions, stale required domestic sources, mismatched official close,
missing reference, failed HTTP/clock checks, or data received after the decision.
Incomplete intraday sessions do not become complete daily intraday features.

The first rehearsal failed before issuance because mixed timestamp formats
needed explicit pandas parsing; the parser was corrected and regression-tested.
One successful later issue is permanently LATE_DIAGNOSTIC, excluded from primary.
Subsequent hardening checks all domestic source freshness, adds explicit matched
score deltas and snapshots source before each issue. The original issue code was
reconstructed from recorded edits and matched against every original code hash;
its exact archive is retained, and no issued prediction was changed.

Local clocks plus server dates are useful authentication evidence, not independent
notarization. A hash chain detects mutations relative to a retained head, not a
malicious wholesale rewrite with a replaced head. Historical vendor revision
vintages/publication clocks are still incomplete. Cached exchange calendars can
change: resolver requires the exact observed target-session sequence and halts
for review on an unexpected closure or missing bar. API structure is documented
by [Upstox Historical V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).
No production-quality availability guarantee is claimed.
