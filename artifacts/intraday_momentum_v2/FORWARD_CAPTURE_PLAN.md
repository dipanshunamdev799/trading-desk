# Read-only forward observation plan

Implemented capture.py, independent of all bot workers. No scheduler/service
installed, no order API, no trading switches. Explicit bounded execution:

```powershell
.venv/Scripts/python.exe -m research.intraday_momentum_v2.capture audit
.venv/Scripts/python.exe -m research.intraday_momentum_v2.capture record --seconds 3600
```

One owned WebSocket connection,100LTPCscanner keys, richer5level Full for at
most20largest observed absolute movers, rerank30s with stable tie ordering.
Broad scanner cohort fixed before2025; zero-move ties provide controls.
D30off unless entitlement independently observed and budgetreserved; current
WSauth401means unavailable. Fallback RESTFullQuotes100keys every5s, clearly
labeled rest_5second rather than websocket. No promised update frequency.

Preserve unmodified primary feed payloads in existing PGmarket_stream_ticks
with source_at and received_at; REST responses in existing market_responses.
NoDDL, no reconstruction in raw tables. Local compressedJSONL records derived
features, transport, health, subscription changes, disconnect/reconnect
generations, no-frame5s, missing/stale timestamps and incompletecommitflags.
Derived source conversions never become raw Upstox feed observations.
Every snapshot retains source and lasttrade clocks separately: feed timestamp
age>5s or unknown is stale; tradeage>30s or unknown separately flagged. A closed
market snapshot is not an actionable or fresh forward trading observation.
Historical overwrite/conflict safeguards remain unchanged.

Required later H3panel:atleast60freshregularsessions,>=1000independent candidate
episodes across>=50sessions, matched controls in the same universe/time buckets;
rollingwatchlist residence and missingness recorded, not discarded on outcome.
Before any H3returns, freeze causal features/windows and walk-forward dates.
Use past1/5/15sspread/imbalance/persistence and observable price response;
no cancellation/aggressor identities inferred. Compare price-only,price+volume,
price+volume+depth on IDENTICAL episode timestamps and same executable-fill
assumptions. Purge overlapping target horizons across folds, group uncertainty
by market day, report imbalanced labels, calibration, feature increment and
neteconomic results after spread/impact/rejections, not accuracy alone.

Actual received updatecadence must be measured in open market. Require >=95%
covered candidate-minute windows with source age<=5s for snapshot tests;
define tick-level requirements separately if WSbecomesavailable. Estimate entry
spread, adversepricechanges after100/500/1000ms if timestamps support them,
and depth-walk capacity only as provisional execution bounds. Displayed depth
does not guarantee fills. Freeze a separate quote-fill model before strategy
validation; real orders remain prohibited. Current closed-session smoke capture
tests plumbing only. No fresh forward strategy results exist today.
