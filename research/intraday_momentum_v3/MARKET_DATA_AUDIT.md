# Market-data audit

Audit date: 15 November 2026. Machine-readable evidence is in `artifacts/intraday_momentum_v3/`. PostgreSQL remains the source for retained market data; authentic new Upstox payloads are appended only to existing raw-response/stream tables. Derived research stays in local versioned artifacts. No database schema or bot state was changed.

## The precise authorization failure

The configured read-only token successfully fetched a full market quote. Local, unverified JWT metadata indicates issue time 16 September 2026 and expiry 16 September 2027. It has no surrounding whitespace or embedded Bearer prefix. Tokens, raw claims, account identifiers and authorized WebSocket URLs are excluded from reports.

Both documented V3 GET authorization routes returned HTTP 401 and `UDAPI100058`. The broker's returned message is:

> No segments for these users are active. Manual reactivation is recommended from Upstox app/web.

This fails before subscription, so it does not diagnose the subscription limit or 30-level depth entitlement. Successful REST data and the unexpired token argue against a general invalid/expired-token explanation. A whitelisted profile-field probe separately returned 401 `UDAPI1221`; its exact meaning was not confirmed from official documentation, and it is not treated as evidence of account entitlement. No profile PII was saved.

“Segment” means an account's exchange/market permission, such as NSE cash equity. The API's public/static access does not by itself establish those account permissions. Crucially, the [official Analytics Token documentation](https://upstox.com/developer/api-documentation/analytics-token/) explicitly supports market data and WebSockets without a whitelisted static IP. Account/user APIs have different restrictions. Therefore there is no evidence that buying a static IP or replacing the token will solve this stream error.

Upstox documents this inactive-segment error on [Get Profile](https://upstox.com/developer/api-documentation/get-profile/). Its recommended intervention is an account/segment check in the app or website. If the user sees NSE active, support should explain why an Analytics Token works for REST quotes but feed authorization returns UDAPI100058. We cannot independently confirm why the broker considers it inactive. No reactivation, token regeneration or account modification has been performed. Only one Analytics Token is allowed per account, so automatic regeneration could disrupt existing workers.

## Feed limits and entitlement

The [V3 feed documentation](https://upstox.com/developer/api-documentation/v3/get-market-data-feed/) describes two normal connections per user; LTPC 5,000 individual/2,000 combined keys; full depth 2,000 individual/1,500 combined keys. Full provides five levels. Plus describes five connections and at most 50 D30 keys. V3 proposes ONE additional owned connection, at most 480 equity scanner keys plus two indices, with at most 40 in full mode. Limits are account-wide and existing clients may consume capacity. Authorization must succeed before entitlement can be measured. V2 streaming was discontinued in August 2025 and is not a fallback. D30 is not assumed or enabled by the observer.

## Complete retained archive inventory

All four Timescale stream chunks were covered using existing primary-key indexes. Complete instrument/session row and timestamp coverage is in `archive-coverage.csv`; sampled feed type/mode/depth is separate in `archive-depth-type-sample.csv`. Chunk-level results and timings are retained.

| Item | Complete inventory |
|---|---:|
| Total updates | 32,370,042 |
| Instruments, all segments | 1,050 |
| NSE cash-equity updates | 5,506,783 |
| Cash-equity instruments | 50 |
| F&O updates | 22,502,223 |
| Index updates | 4,361,036 |
| Sessions | 26-30 October and 11-13 November 2026 |
| Receipt minus source greater than five seconds | 120,472 |
| Repeated source timestamps | 78 |

Repeated timestamps are not necessarily duplicate payloads. A source-minute containing an update is occupied, not necessarily continuously covered. The deterministic payload sample contains 141,631 rows, including 125,577 with at least five depth levels and none with 30. Those depth counts are SAMPLED, not complete-archive depth totals or proof that D30 is unavailable.

Only 47 of the 50 cash equities are inside the old liquid-100 cohort; three are outside. The larger archive corrects the earlier impression of only one useful RELIANCE day, but it provides little evidence about the broad universe of unusually volatile smaller stocks.

## Detailed descriptive replay

A prespecified subset selected the five most liquid archived core names and up to five outside-core names; only three outsiders exist. The latest two sessions with at least 300 occupied source minutes per stock produced eight stocks, 16 stock-days and 348,484 payloads. No exact source-plus-payload duplicates were found in this subset.

At a one-second 09:15-15:10 grid requiring a valid book and source/receipt freshness within two seconds, coverage ranged from 65.48% to 97.72%, median 82.49%. The largest interarrival gap was 2,238.49 seconds. Median spread by stock-day ranged from 0.625 to 3.682 bps, with median 1.655 bps. Negative receipt-minus-source differences also occur; local/exchange clock skew means these differences are not pure network latency.

As-of reconstruction is possible only when source, receipt and availability clocks and quote validity permit it. Sparse intervals remain missing. Latency bounds and quoted capacity are useful descriptively; this replay does not establish independent alpha, actual fills, or full-market feed completeness.

## MIS/suspension reconciliation

Current instrument, MIS and suspension files were fetched separately, with original compressed bytes, retrieval dates, URL, SHA-256, Last-Modified and ETag preserved. An ISIN-derived `instrument_key` can occur in multiple cash trading series. The old key-only comparison incorrectly mixed current EQ identities with suspended BE/AF/BL/IQ/RL/TL identities.

V3 joins on exchange, segment, instrument type, exchange token AND instrument key. For example, RELIANCE's current EQ token 2885 is different from the suspended series tokens sharing its ISIN. Of 2,763 current ordinary EQ identities, 1,372 are MIS-listed and 1,391 are not; ZERO current exact-identity MIS/suspension conflicts remain. Account activation, past eligibility and executable short sales remain unverified. HFCL's current identity is BE, token 21954; it is excluded from the ordinary-EQ observer instead of silently substituting another series.
