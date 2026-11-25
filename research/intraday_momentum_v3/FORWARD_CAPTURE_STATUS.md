# Forward observation status

Prepared on Sunday 15 November 2026. Prospective performance is `FORWARD_DATA_REQUIRED`. The current authoritative measured status is `artifacts/intraday_momentum_v3/forward-readiness.json`; plumbing checks are recorded separately in `verification.json`. Closed-market snapshots and all retained pre-freeze data are excluded from new forward evidence.

| Milestone | Requirement | Status at preparation |
|---|---|---|
| A, streaming | Real post-freeze regular-session quotes with source/receipt clocks | Not demonstrated; authorization returns UDAPI100058 |
| A, REST | Real post-freeze regular-session snapshots with clocks | Awaiting a manually observed market session |
| B, streaming | Five passing fresh sessions | Zero |
| B, REST | Five independently assessed snapshot sessions | Zero |
| C | 60 passing fresh sessions, 1,000 embargoed targets across 50 days, controls and separate evaluation | Not met |
| Profitability | Prospective statistical and economic qualification | Not demonstrated |

## Manual operation

From the project root, after the protocol is frozen:

```powershell
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture run --seconds 28800 --transport auto
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture status
.venv/Scripts/python.exe -m research.intraday_momentum_v3.capture stop
```

Start manually before the session, keep the machine awake and PostgreSQL/network available. An eight-hour bound started around 08:00 IST spans a normal trading day. The observer can wait for today's announced opening within its own duration. It verifies the Upstox NSE status and dated market timings; closed/holiday/nonregular sessions exit. It does not stay alive overnight awaiting tomorrow. Normal observations require `NORMAL_OPEN` plus an actual current NSE time window. There is no automatic startup, scheduled task or service. Nothing is enabled by launching the Trading Desk app.

`auto` attempts a V3 stream, then uses distinctly labeled REST snapshots if authorization is unavailable. `--transport ws` does not silently substitute snapshots. `--transport rest` requests snapshots explicitly. An optional `--smoke-closed` exercises authentic closed-market REST ingestion only; those records cannot pass the fresh-forward gates. No account/token modifications are automatic.

## Reliability and raw data

One process lock prevents duplicate V3 observers. Controlled stop uses a research-local stop request. Restarts preserve previous manifests and committed raw observations; they do not claim to fill gaps while the process was down. Health includes PID, transport, market phase, committed rows, source-fresh valid books, silent watchlist keys, queue length, raw bytes and data rate. Alerts record no-frame periods, connection generations, interruptions and REST/commit failures. No authorized URI or credential is logged.

Limits per run: 1-28,800 seconds, at most five million stream/quote rows, at most 8 GiB of raw serialized input and stop below 20 GiB free disk. The WebSocket queue holds at most 2,000 frames and commits batches of at most 50 frames to the existing PostgreSQL stream table. Payloads are processed for research only after commit; source, receipt and commit clocks remain distinct. Raw binary packets are also retained in compressed local backup. REST payloads go unchanged into existing `market_responses`. Derived features never enter authentic raw tables. Account profile data is not archived.

An abrupt process termination can leave the final compressed backup incomplete; PostgreSQL retains only committed batches. That run's manifest and health must be inspected before use. A failed raw commit stops this observer. Existing F&O/investment workers and switches are independent and unchanged.

## Transport-specific quality

Streaming: a valid uncrossed book, source age at most two seconds, receipt age at most two seconds, and actual availability no later than the decision. Source clock tolerance is at most one second ahead, but future-available data is never usable early. On a one-second grid from 09:15 to 15:10, every fixed control must be covered at least 95% to pass a session.

REST: use source and receipt ages at most ten seconds, independently on a five-second grid over the same interval; every fixed control must meet 95%. These looser snapshot rules do not qualify REST as streaming. The current funded shadow gate accepts only independently qualified streaming observations. Gaps and invalid books interrupt derived coverage; raw data is not forward-filled.

The recorder is an acquisition tool, not proof of an edge. There are fewer than 60 possible regular sessions remaining in 2026 from this preparation date. Completing the intended sample will require explicit approval to extend collection/evaluation into 2027. This version hard-rejects 2027 starts and predictions; it does not silently continue across the year boundary.
