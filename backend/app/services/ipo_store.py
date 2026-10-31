"""IPO persistence shares the market gateway's engine and transaction boundary."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import text

from .market_store import MarketStore, market_day, now


class IpoStore:
    def __init__(self, store: MarketStore):
        self.store = store

    @staticmethod
    def save_company(conn, row: dict, at: datetime, source: str = "Upstox"):
        if not isinstance(row, dict) or not row.get("id") or not row.get("name"):
            return
        conn.execute(text("""INSERT INTO ipo_companies(id,payload,source,fetched_at)
            VALUES(:id,CAST(:data AS jsonb),:source,:at) ON CONFLICT(id) DO UPDATE SET
            payload=ipo_companies.payload || excluded.payload, source=excluded.source,fetched_at=excluded.fetched_at"""),
            {"id": row["id"], "data": json.dumps(row, allow_nan=False), "source": source, "at": at})
        value = row.get("total_subscription")
        start = row.get("bidding_start_date")
        if value is not None and start and start <= market_day().isoformat():
            try:
                numeric = float(value)
            except (ValueError, TypeError):
                return
            IpoStore.save_observation(conn, row["id"], source, "total_subscription", numeric, at,
                                      {"start_date": start})

    @staticmethod
    def save_upstox(conn, payload: Any, at: datetime):
        rows = payload.get("data", []) if isinstance(payload, dict) and "data" in payload else payload
        for row in rows if isinstance(rows, list) else [rows]:
            IpoStore.save_company(conn, row, at)

    @staticmethod
    def save_observation(conn, ipo_id, source, metric, value, at, payload, reported_at=None):
        import math
        if value is not None and not math.isfinite(float(value)):
            return
        conn.execute(text("""INSERT INTO ipo_observations(observed_at,ipo_id,source,metric,value,reported_at,payload)
            VALUES(:at,:id,:source,:metric,:value,:reported,CAST(:data AS jsonb)) ON CONFLICT DO NOTHING"""),
            {"at": at, "id": ipo_id, "source": source, "metric": metric, "value": value,
             "reported": reported_at, "data": json.dumps(payload, allow_nan=False)})

    @staticmethod
    def save_research(conn, payload: dict, at: datetime):
        conn.execute(text("""INSERT INTO ipo_research(ipo_id,kind,source_url,payload,fetched_at)
            VALUES(:id,:kind,:url,CAST(:data AS jsonb),:at) ON CONFLICT(ipo_id,kind) DO UPDATE SET
            source_url=excluded.source_url,payload=excluded.payload,fetched_at=excluded.fetched_at"""),
            {"id": payload["ipo_id"], "kind": payload["kind"], "url": payload["source_url"],
             "data": json.dumps(payload, allow_nan=False), "at": at})
        for metric, value in payload.get("metrics", {}).items():
            IpoStore.save_observation(conn, payload["ipo_id"], payload["kind"], metric, value, at,
                                      {"source_url": payload["source_url"]}, payload.get("reported_at"))

    def companies(self) -> list[dict]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return [{**row["payload"], "catalog_source": row["source"], "fetched_at": row["fetched_at"].isoformat()}
                    for row in conn.execute(text("SELECT * FROM ipo_companies ORDER BY fetched_at DESC,id")).mappings()]

    @staticmethod
    def save_feed(conn, name: str, ids: list[str], at: datetime):
        conn.execute(text("""INSERT INTO ipo_feeds(name,ipo_ids,checked_at) VALUES(:name,CAST(:ids AS jsonb),:at)
            ON CONFLICT(name) DO UPDATE SET ipo_ids=excluded.ipo_ids,checked_at=excluded.checked_at"""),
            {"name": name, "ids": json.dumps(ids), "at": at})

    def set_feed(self, name: str, ids: list[str]):
        with self.store.engine.begin() as conn:
            self.save_feed(conn, name, ids, now())

    def active_ids(self) -> set[str]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return set(value for ids in conn.execute(text("SELECT ipo_ids FROM ipo_feeds")).scalars() for value in ids)

    def research(self, ipo_id: str) -> dict:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return {row["kind"]: {**row["payload"], "fetched_at": row["fetched_at"].isoformat()}
                    for row in conn.execute(text("SELECT * FROM ipo_research WHERE ipo_id=:id"), {"id": ipo_id}).mappings()}

    def all_research(self) -> dict[str, dict]:
        self.store.initialize()
        result = {}
        with self.store.engine.connect() as conn:
            for row in conn.execute(text("SELECT * FROM ipo_research")).mappings():
                result.setdefault(row["ipo_id"], {})[row["kind"]] = {
                    **row["payload"], "fetched_at": row["fetched_at"].isoformat()}
        return result

    def observations(self, ipo_id: str) -> list[dict]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return [{**dict(row), "observed_at": row["observed_at"].isoformat(),
                     "reported_at": row["reported_at"].isoformat() if row["reported_at"] else None}
                    for row in conn.execute(text("""SELECT observed_at,source,metric,value,reported_at,payload
                        FROM ipo_observations WHERE ipo_id=:id ORDER BY observed_at DESC LIMIT 2000"""),
                        {"id": ipo_id}).mappings()][::-1]

    def sync(self, source: str, error: str | None = None):
        self.store.initialize()
        at = now()
        with self.store.engine.begin() as conn:
            conn.execute(text("""INSERT INTO ipo_sync_state(source,attempted_at,succeeded_at,error)
                VALUES(:source,:at,:success,:error) ON CONFLICT(source) DO UPDATE SET
                attempted_at=excluded.attempted_at,succeeded_at=COALESCE(excluded.succeeded_at,ipo_sync_state.succeeded_at),
                error=excluded.error"""), {"source": source, "at": at, "success": None if error else at, "error": error})

    def health(self) -> list[dict]:
        self.store.initialize()
        with self.store.engine.connect() as conn:
            return [{key: value.isoformat() if isinstance(value, datetime) else value for key, value in row.items()}
                    for row in conn.execute(text("SELECT * FROM ipo_sync_state ORDER BY source")).mappings()]
