# Upstox data and execution audit

Checked15November2026. Probe outputs in artifacts/intraday_momentum_v2/
api-audit.json,inventory-probes.json,retained-depth-audit.json. Authenticated
redirect URLs and credentials never stored or printed.

## Existing sources and independent additions

PG public.candles: raw Upstox daily history for496/500datedcohort; prior study
7.34m5m candles covering8%-conditioned stock-months, inadequate to independently
test earlier movers. One-minute coverage is selective: bounded HDFCBANK,
RELIANCE,ICICIBANKprobes first show24September2026; NIFTY1m startsJanuary2026
in the same2025–26probe. These are point probes, not universal start dates.
Historical PG daily/5m inputs supply previous close, OHLCV-derivedVWAP, ADV,
RVOL and volatility. Frozen2024industry labels support a contemporaneous peer
proxy; it is not independently acquired historical sector-index membership.
Original ISIN/rename mappings and certified split/bonus restoration retained.

V2 independently acquires24fullmonthsDec2024..Nov2026 for100pre2025liquid
cohort names plusNIFTY:2424sourcejobs;579exact preexisting HTTP source jobs
reused;1845missing at plan freeze. Every source must be OK before returns.
Raw Upstox only into existing PG tables, noDDL or rawprice replacements.
Results, corporate-action metadata and local unit reconstruction stay local.
A broad aggregate inventory timed out and is reported unavailable, rather than
misrepresented as an exhaustive database scan. Per-source manifests and
bounded index probes preserve the actual evidence.

## Official capabilities, checked against primary documentation

[HistoricalV3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/):
minute/hour history documented fromJanuary2022;1–15minute requests <=1month;
daily fromJanuary2000. Response OHLCV/OI is not historical spread/depth or
individual order events. Availability bounds do not guarantee every identity/day.

[FullQuotesV3](https://upstox.com/developer/api-documentation/get-full-market-quote-v3/):
<=500keys/request, live five-level depth, bid/askquantity, price, lasttrade time,
volume, totalbuy/sellquantities, circuitlimits and metadata. Our actual REST
probe returned100/100instruments,5bid/askarray slots (not proof of five positive
executable levels). REST did not supply lasttrade quantity in this response;
that field is documented for WebSocket LTPC, which remains unverified here.
Lasttrade dates are from the
previous session; market status CLOSING_END. No active-session cadence measured.

[FeedV3](https://upstox.com/developer/api-documentation/v3/get-market-data-feed/):
full=5levels;full_d30=30levels. Normal2connections;individualFull2000keys,
combinedmodes1500keys. Plus5connections,D30individual50keys. These are published
limits, not proof of this account's entitlement. Actual authorization endpoint
returnedHTTP401 with the configured analytics credential. No separate access
credential is configured. Streaming5level andD30entitlement UNVERIFIED;
authentication failure does not establish that the account lacks Plus.

[Rate limits](https://upstox.com/developer/api-documentation/rate-limiting/):
standard50/s,500/min,2000/30min, per API/user. Historical downloader <=1750
dispatches/1801s with >=0.26s spacing, leaving headroom; snapshots5s/batch
consume360requests/30min on their separate API. Broker throttling still wins.

[Instruments](https://upstox.com/developer/api-documentation/instruments/):
current MIS/suspended/instrument files exist, but cannot certify2025eligibility.
No historical short, margin, surveillance or price-band series reconstructed.
Existing source_at/received_at streaming archives contain real retained equity
depth: a RELIANCE13Nov2026point-count found30350updates across334source minutes.
The restricted09:15..15:10diagnostic reads29563updates. This is one researched
stock-day, not a broad history or post-freeze forward evidence. H3_DIAGNOSTIC.md
freezes its limited feasibility test. A source-clock-only first implementation
was invalidated; H3_IMPLEMENTATION_CORRECTION.md documents the availability fix.

## Costs and mechanism evidence

[Upstox fees](https://upstox.com/brokerage-charges/):basicplanintradaylower₹20
or0.1%/order;STT0.025%sell,stamp0.003%buy,SEBI₹10/crore,GST18%applicablebase.
[October2024notice](https://upstox.com/announcements/updates/revision-in-transaction-charges-from-1-october-2024/)
and [NSEFA73061](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf)
support combined cash transaction/IPFT₹307/crore/side through2025–2026;
March2026 reallocates297+10to306.99+0.01, unchangedcombinedcost. Historical
account brokerage plan/contract-note rounding unverified. Intraday noDP/funding
charge under noleverage, same-session model. Slippage5/10/25bps scenarios are
ALL-IN modeled spread/adverse-selection/impact, not calibrated observations.

[Cont,Kukanov,Stoikov](https://arxiv.org/abs/1011.6402) relates order-flow
imbalance to short-horizon price changes in USstocks, not certified NSE alpha.
[Xu,Gould,Howison](https://arxiv.org/abs/1907.06230) studies multilevel flow
and contemporaneous mid-price changes. These motivate H3, but contemporaneous
association does not prove future executable net returns. Our snapshot feed
cannot recover every event in those datasets or label aggressor trades.

## Measurement boundary

Direct:quoted prices/quantities, displayed totals, LTP/LTQ where supplied,
source/receipt timestamps, sourcevolume. Derived:spread, snapshotimbalance,
price/depth persistence, trade-price response and explicitly labeled volume
proxies. Unavailable:full event sequence, true cancellations/replenishment
identities, aggressive-side executed totals, queue position and guaranteed
fills. Do not sum repeated LTQ snapshots into tradedvolume. Do not fabricate
historical depth. REST5s fallback supports snapshot research, not a tick-complete
microstructure claim. Historical fills/partialfills remain provisional.
