# IPO subscription source repair — 10 November 2026

IPOWatch replaced the subscription page's server-rendered table with a
JavaScript tracker. The tracker uses the public endpoint
`https://ipowatch.in/server/api/ipo/GetIpoAubscription`. A successful HTML fetch
therefore returned a loading shell rather than the table expected by the old
adapter. The page's initial “0 open IPOs” text was a loading placeholder and was
not accepted as evidence of an empty feed.

The adapter now validates the JSON success envelope and nested issuer records,
maps QIB/NII/sNII/bNII/retail/total categories, and selects the latest published
snapshot without carrying missing categories forward from an earlier day.
The cache namespace includes the current endpoint and parser version 2. The
old HTML table parser remains available for legacy responses. Invalid responses,
conflicting readings and malformed numbers still raise genuine source errors.

Publication dates retain day precision. The database keeps those dates in the
research/observation payloads and does not invent publisher timestamps. Dated
history supplies the demand chart with correct IPOWatch attribution; a newer
publication takes precedence over older or undated detail readings. Upstox's
separate total remains attributed to Upstox and any public-source discrepancy
remains visible.

## Verification

- `python backend/scripts/test_ipo_research.py`: **25 tests passed**.
- A captured public feed fixture covers six published bidding days, issuer/date
  matching, category splits, explicit missing values, exact zeros, invalid
  envelopes, loading shells, malformed numbers, conflicts and source provenance.
- Real ingestion succeeded through the database transaction and normal source
  health update, without deleting or manually clearing the warning record.
- The managed API was restarted after checking there were no active bot workers
  or retained positions. The existing frontend/database were reused.
- The live frontend API returns 53 retained issuers and **zero source errors**.
- Antala's refreshed readings match the captured feed: QIB 66.72, NII 49.94,
  sNII 8.30, bNII 70.40 and retail 5.22. Publication date: 2026-11-05.
- The six daily snapshots appear in the demand history. The Upstox total 12.72
  and public total 12.79 discrepancy is retained as a note.
- Browser verification confirmed the warning is absent and the updated figures,
  dates, source links and history are displayed.

Evidence: `live-verification.json`, `after-ingestion.json`, and
`verified-source.png`. These are observed application/provider results, not a
recommendation or a guarantee of complete market coverage.
