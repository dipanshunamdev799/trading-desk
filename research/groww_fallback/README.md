# Groww fallback capability check

The supplied access token is stored in the Git-ignored `.env.groww.local`, not the existing tracked `.env`. The latter was left unchanged. Never commit the local credential file. Environment variable `GROWW_ACCESS_TOKEN` can override it in memory.

The user confirmed that only a free token was generated. Groww's free API plan excludes live market data; the initial NSE cash quote request returned HTTP403. Therefore the fallback is NOT enabled. A token's existence or future expiry does not demonstrate live-data entitlement. No subscription was purchased, account settings changed, order submitted or PostgreSQL data written.

Recheck after enabling live-data access and configuring a current token locally:

```powershell
.venv/Scripts/python.exe -m research.groww_fallback.probe
.venv/Scripts/python.exe -m unittest discover -s tests -p test_groww_fallback.py
```

The probe has an allowlist of two market-data GET routes, disables redirects and prints only whitelisted capability/expiry metadata. It never prints the credential, JWT subject, account identifiers, server error bodies or authenticated redirect URLs. Result: `artifacts/groww_fallback/capability-audit.json`. This is a capability probe, not an integrated recorder or automatic provider switch.

An eventual adapter needs independently tested source/receipt clocks, actual cadence, price/depth/volume fields, instrument mapping, provider separation and a newly frozen research boundary. Groww data must remain outside the existing Upstox-only PostgreSQL data. Existing V3 protocol, workers, bot controls and schedules are unchanged.

Official sources checked 16 November2026:

- https://groww.in/trade-api/docs/curl/live-data
- https://groww.in/trade-api/docs/python-sdk/feed
- https://groww.in/trade-api/docs/curl
- https://groww.in/blog/api-trading-on-groww
- https://groww.in/trade-api

The marketing page advertises Rs499/month plus taxes; exact billing and access must be confirmed in the account before purchase. Standard access tokens expire daily; this token's expiry metadata is displayed by the probe rather than inferred from the screenshot's relative “tomorrow” label.
