# IPO research

Open `/ipos` in the frontend. The watchlist covers every page of Upstox upcoming
and open issues, scheduled public-feed additions absent from Upstox, a separate
undated announcement pipeline, and the latest 30 closed / 30 listed records.
Previously collected records remain in PostgreSQL even after leaving these feeds.

The selected issue always presents the requested 24 factors, in the original
order. `unavailable`, `pending`, `stale`, and `needs review` have distinct meanings.
Coverage counts populated factors, including descriptive items needing review;
it is not a rating or an assertion that every factor has a complete assessment.

## Sources and interpretation

- [Upstox IPO list](https://upstox.com/developer/api-documentation/get-ipos/) and
  [IPO details](https://upstox.com/developer/api-documentation/get-ipo-details/):
  identity, stage, bidding dates, price band, issue size, lot and minimum quantity,
  overall subscription, timeline, documents, registrar, listing and other provider
  fields. The additional-inputs drawer retains every available Upstox field.
- [InvestorGain](https://www.investorgain.com/report/ipo-gmp-live/331/): public
  discovery, dated GMP history, issue structure, financial tables, valuation,
  proceeds, managers, disclosed anchor allocations and broker tables when present.
- [IPOWatch](https://ipowatch.in/ipo-subscription-status-today/): current QIB, NII,
  retail and overall multiples when a matching issue is published.

Upstox does not expose all 24 research factors through these two IPO endpoints.
Public feeds are supplementary and not exchange-certified. Source names, links,
retrieval time, publisher time when supplied, and financial periods accompany
values. A time-only publisher label is not turned into a fabricated date. Missing
GMP is distinct from an explicitly reported zero. Missing subscription is never
turned into zero, and pre-bidding provider zeroes remain pending.

Public issue matching requires compatible company names, price and closing date.
Each detail page must also identify the selected issuer in its heading; an HTTP
200 response for a different issuer is rejected. Mainboard/SME and subscription
conflicts remain visible. Announced bidding dates determine the displayed stage
when a provider prematurely labels an issue open.

Category splits and publisher-dated Day 1/2/3 history are parsed when the connected
source actually publishes them. Some current pages contain neither. Earlier
bidding days are not reconstructed from today's aggregate. Collected snapshots
are separately inspectable with their observation and publication timestamps.
History begins when collection starts; this service cannot recover unrecorded
past intraday readings from an undated current total.

Financial growth compares consecutive full March fiscal years, never a quarter
against a year. Growth from zero or negative prior profit is unavailable. Ratios
use a disclosed annual period where present; borrowings use the latest disclosed
period. Fresh/OFS percentages use one source's total. A market-maker reservation
or an unspecified difference is not assumed to be OFS. Source discrepancies in
gross/net issue definitions must be reviewed against the RHP.

Anchor names do not establish investor quality. Manager track records and peer
listing returns use only retained matched managers / reported industries and
actual issue/listing prices. Business context, disclosed certifications and
industry classification do not establish a moat, customer diversification or
sector tailwinds. Those judgments, seller classifications and an absent broker
opinion remain explicitly unassessed rather than receiving an invented score.

## Collection and storage

The existing `MarketGateway` / `MarketStore` supplies
**UI → bounded memory cache → PostgreSQL → upstream**. Successful responses and
normalized records commit before entering memory. Public HTTP uses a separate
unauthenticated transport, an HTTPS host allowlist and validated redirects; the
Upstox authorization token is never passed to public providers.

Migration `sql/003_ipo_research.sql` creates:

- `ipo_companies`: merged original company fields and their source / retrieval time.
- `ipo_research`: the latest parsed source payload for each issuer and feed kind.
- `ipo_observations`: a TimescaleDB hypertable of observed subscription and GMP
  values, with separate capture / publication timestamps. No retention policy.
- `ipo_feeds`: current universe membership; a failed fetch does not replace it.
- `ipo_sync_state`: source success/error state, preserving the last success.

Original successful upstream responses also enter `market_responses`, the existing
TimescaleDB archive. DB cache hits after a process restart do not create another
observation or call the provider. Raw HTML is parsed on an actual source fetch;
the parsed response and source URL are retained.

The frontend checks once per minute while visible and on return to the page.
The background collector runs while the backend is running, even with no IPO page
open. It starts at backend startup and waits at least 60 seconds between completed
collection rounds; provider latency can lengthen a round. Configure with
`IPO_COLLECTOR_ENABLED` and `IPO_REFRESH_SECONDS` (minimum 60 seconds).

Freshness policy:

| Feed | Cache lifetime |
| --- | --- |
| Upstox open list / already-open issue details | 60 seconds |
| Other current Upstox lists / dated details | 5 minutes |
| Listed Upstox list / details | 24 hours |
| Undated Upstox issue details | 6 hours |
| Public category subscription index | 60 seconds |
| Public discovery / GMP | 5 minutes |
| Public category history / anchor detail | 15 minutes |
| Public recommendations | 1 hour |
| Public issue financials / structure | 6 hours |

Automatic public-feed retries back off five minutes on failure. Failed refreshes
keep the last successful data with original timestamps and visible error/stale
status; they do not convert a page check into a fresh market observation.
`GET /data/integration` includes IPO row counts and
`ipo_public_source_fetches` alongside existing cache/DB/Upstox counters.

## Verification

Run the backend unittest suite with `RUN_MARKET_DB_TESTS=1` for real PostgreSQL
coverage. IPO tests check wrong-issuer rejection, missing versus zero values,
date parsing, pending demand, financial periods, issue-structure ambiguity,
freshness and complete upcoming pagination. DB tests verify durable normalized
research and original fields survive a new store instance without another fetch.
In `frontend`, run `npm run test:ipos`, `npm run test:charts`, and `npx tsc --noEmit`.
