# Causal quote features

`features.py` retains source time, local receipt time and availability time = max(source, receipt, PostgreSQL commit). Processing/decision time is also logged. An observation cannot influence a decision before availability. Unknown/naive timestamps are rejected. Negative receipt-minus-source values are clock differences, not negative network latency.

## Authentic observations and derived values

Keep best and available-depth bid/ask prices and quantities, total displayed buy/sell quantity, LTP, previous close, cumulative volume, last quantity and last-trade time where supplied. WS frame time is the source clock; last-trade time remains a separate field. REST response timestamp is separate from local receipt. The original payload and binary frame remain untouched.

Books require positive prices/quantities and best ask at least best bid. Crossed, empty and incomplete books remain raw observations but cannot create an executable signal. Research buffers reject backward source or availability time and exact repeated source-plus-payload observations. Equal source times with different payloads are not automatically duplicates. WS and REST buffers are separate even for the same stock.

Latest-known values may be queried as-of a decision timestamp only within the transport freshness limit. This is an explicitly derived reuse, not a new raw quote. A future observation cannot change an earlier feature query. Buffers are bounded to 5,000 observations and 30 minutes per stock/transport; unavailable lookback anchors produce missing features. Higher update rates may shorten usable history rather than silently create data.

## Frozen features

| Feature | Causal definition |
|---|---|
| Mid and spread | (best bid + best ask)/2; (ask - bid)/mid in bps |
| Return 5/60/300 seconds | Current mid versus latest valid as-of quote no later than each lookback boundary; boundary must satisfy source freshness |
| Daily return | Current mid / observed previous close - 1 |
| Volume60 | Current cumulative volume minus its 60-second anchor; negative resets are missing |
| Volume acceleration | Volume60 divided by median of five previous nonoverlapping 60-second volume increments; all five must be observed |
| Imbalance1/5 | (summed bid quantity - summed ask quantity)/(their sum), at one/five supported levels |
| Persistence | Last quote per observed second over ten seconds; equal weight to each observed second, not each message in a burst |
| Support fraction | Fraction of those observed seconds with imbalance5 above +0.2 or below -0.2; minimum observed-second count is recorded |
| Imbalance mean/std | Mean and population standard deviation of the observed-second imbalance values |
| Spread baseline | Median valid observed spread in the previous 60 seconds |
| Depth depletion proxy | Current five-level bid depth relative to median bid depth observed 10-30 seconds ago |
| Breakout bounds | Maximum/minimum valid observed mid 5-300 seconds ago, excluding the last five seconds |
| Breakout holding | Minimum/maximum mid and count of distinct observed seconds in the last three seconds |
| Stop anchors | Lowest/highest valid observed mid over 60 seconds |

Five-level quantities can include fewer supported levels; the actual raw book exposes how many existed. A persistence ratio based on two seconds is not treated as ten seconds of evidence. Last quantity is not summed to fabricate traded volume. Turnover, depth depletion/replenishment and trade/quote response are observation proxies. They cannot identify individual orders, cancellations, aggressors, genuine buy-versus-sell executed totals or spoofing.

For modeling, returns, daily return and signed imbalance are multiplied by the candidate direction, and bid/ask depths swap for shorts. Spread, volume and imbalance variability retain their magnitudes. All feature groups are evaluated on the same timestamps with complete PVD inputs; missing-depth rows are reported as missing, not selectively given to an easier baseline.

## Outcomes and context

Each event stores the exact pre-entry quote, source/receipt/availability clocks, feature vector, metadata state and fresh NIFTY/VIX context when available. Outcomes use the first later observation at or after each predefined horizon, with endpoint lateness at most two seconds for WS or ten seconds for REST. Later favorable quotes are not substituted. Invalid/late endpoints are censored; shutdown before a future horizon means uncollected future data. Event-horizon missingness and unmatched controls remain in the logs.

All candidate timestamps are produced by common price conditions. Volume and depth confirmation are logged as additional inputs. Thus adding a depth feature cannot rewrite the baseline's event times after inspecting returns. A 30-minute within-stock embargo marks the analysis sample; simultaneous events in correlated stocks are not claimed independent. Inference resamples whole market days.
