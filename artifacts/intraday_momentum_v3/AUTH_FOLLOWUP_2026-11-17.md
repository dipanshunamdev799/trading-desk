# Upstox authorization follow-up — 17 November 2026 IST

The user-provided account screen shows NSE EQ and BSE EQ under opted segments; derivatives and commodities remain pending. A read-only recheck returned HTTP200 from V3 feed authorization and successfully opened the authorized WebSocket. The prior UDAPI100058 failure did not recur. REST quotes also work.

This was a closed-market connection probe: it did not verify live five-level depth, D30 entitlement, fresh regular-session observations, or any research milestone. The profile request still returns UDAPI1221, so profile-based account entitlement remains unverified. No account settings, token, bots or schedules were changed; the bounded connection is closed.

Next: run the existing bounded observer manually during a regular session to measure actual timestamp freshness, depth and control coverage. The previous reports remain frozen historical findings; this is a dated follow-up.
