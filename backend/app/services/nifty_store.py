"""Durable NIFTY observations, source snapshots and event provenance."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from .market_store import MarketStore, now


def content_key(payload: dict) -> str:
    """Collection time is not a new source observation; revisions still differ."""
    stable = {key: value for key, value in payload.items()
              if key not in {"observed_at", "fetched_at", "saved_at", "observation_key"}}
    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":"), allow_nan=False, default=str)
    return hashlib.sha256(encoded.encode()).hexdigest()


def timestamp(value: Any, *, required: bool = False) -> datetime | None:
    if value is None:
        if required:
            raise ValueError("observed_at is required")
        return None
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        # Date-only official daily series identify a reporting date, not a clock
        # publication time. Midnight UTC is only their normalized date anchor.
        if len(str(value)) != 10:
            raise ValueError("Timestamps must include a timezone")
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class NiftyStore:
    def __init__(self, market_store: MarketStore):
        self.store = market_store

    def save_observations(self, observations: list[dict]) -> int:
        if not observations:
            return 0
        records = []
        for row in observations:
            if not row.get("factor_id") or not row.get("source") or not row.get("source_url"):
                raise ValueError("factor_id, source and source_url are required")
            if "reported_at" not in row:
                raise ValueError("reported_at must be explicit, including when unknown")
            records.append({"key": content_key(row), "factor": row["factor_id"], "source": row["source"],
                            "reported": timestamp(row["reported_at"]),
                            "observed": timestamp(row.get("observed_at"), required=True),
                            "data": json.dumps(row, allow_nan=False, default=str)})
        self.store.initialize()
        # executemany avoids a network round trip per historical market session.
        with self.store.engine.begin() as conn:
            result = conn.execute(text("""INSERT INTO nifty_observations
                (observation_key,factor_id,source,reported_at,observed_at,payload)
                VALUES(:key,:factor,:source,:reported,:observed,CAST(:data AS jsonb))
                ON CONFLICT(observation_key) DO NOTHING"""), records)
            return max(0, result.rowcount)

    def latest(self) -> dict[str, dict]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            rows = conn.execute(text("""SELECT DISTINCT ON (factor_id) factor_id,payload
                FROM nifty_observations ORDER BY factor_id,
                COALESCE(reported_at,observed_at) DESC,
                CASE WHEN factor_id IN ('fii_cash','dii_cash') AND payload->>'quality'='exchange_report'
                    THEN 0 ELSE 1 END,
                observed_at DESC,observation_key DESC""")).mappings()
            return {row["factor_id"]: row["payload"] for row in rows}

    def history(self, factor_id: str, limit: int = 365) -> list[dict]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            rows = conn.execute(text("""SELECT payload FROM nifty_observations
                WHERE factor_id=:factor ORDER BY COALESCE(reported_at,observed_at) DESC,
                observed_at DESC,observation_key DESC LIMIT :limit"""),
                {"factor": factor_id, "limit": max(1, min(10000, int(limit)))})
            return [row[0] for row in rows][::-1]

    def save_state(self, payload: dict) -> None:
        """Save the caller's merged state without changing any data timestamps."""
        self.store.initialize()
        with self.store.engine.begin() as conn:
            conn.execute(text("""INSERT INTO nifty_research_state(singleton,payload,saved_at)
                VALUES(TRUE,CAST(:data AS jsonb),:at) ON CONFLICT(singleton) DO UPDATE
                SET payload=excluded.payload,saved_at=excluded.saved_at"""),
                {"data": json.dumps(payload, allow_nan=False, default=str), "at": now()})

    def state(self) -> dict:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return conn.execute(text("SELECT payload FROM nifty_research_state WHERE singleton=TRUE")).scalar() or {}

    def save_events(self, events: list[dict]) -> int:
        if not events:
            return 0
        records = [{"key": content_key(row), "event": timestamp(row.get("event_at") or row.get("date")),
                    "observed": timestamp(row.get("observed_at")) or now(),
                    "data": json.dumps(row, allow_nan=False, default=str)} for row in events]
        self.store.initialize()
        with self.store.engine.begin() as conn:
            result = conn.execute(text("""INSERT INTO nifty_research_events(event_key,event_at,observed_at,payload)
                VALUES(:key,:event,:observed,CAST(:data AS jsonb)) ON CONFLICT(event_key) DO NOTHING"""), records)
            return max(0, result.rowcount)

    def events(self, limit: int = 100) -> list[dict]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return [row[0] for row in conn.execute(text("""SELECT payload FROM (
                SELECT DISTINCT ON (COALESCE(payload->>'id',event_key)) payload,event_at,observed_at
                FROM nifty_research_events ORDER BY COALESCE(payload->>'id',event_key),observed_at DESC,event_key DESC
                ) latest ORDER BY event_at DESC NULLS LAST,observed_at DESC LIMIT :limit"""),
                {"limit": max(1, min(1000, int(limit)))})]
