"""Durable streaming updates; callers publish to memory only after COMMIT."""
import json

from sqlalchemy import text

from .market_store import now


class MarketStreamStore:
    def __init__(self, store):
        self.store = store

    def ticks(self, frames):
        records = []
        for frame, received in frames:
            from .market_session import timestamp
            source_at = timestamp(frame.get("currentTs")) or received
            for key, value in frame.get("feeds", {}).items():
                records.append({"at": source_at, "key": key, "received": received,
                    "kind": frame.get("type", "unknown"), "data": json.dumps(value, allow_nan=False)})
        if not records:
            return
        self.store.initialize()
        with self.store.engine.begin() as conn:
            conn.execute(text("""INSERT INTO market_stream_ticks(source_at,instrument_key,received_at,feed_type,payload)
                VALUES(:at,:key,:received,:kind,CAST(:data AS jsonb)) ON CONFLICT DO NOTHING"""), records)
        self.store.count("stream_batches_committed")

    def chain(self, underlying, expiry, payload, provenance):
        self.store.initialize()
        with self.store.engine.begin() as conn:
            conn.execute(text("""INSERT INTO market_stream_chains(observed_at,underlying_key,expiry,session_date,payload,provenance)
                VALUES(:at,:key,CAST(:expiry AS date),CAST(:day AS date),CAST(:data AS jsonb),CAST(:provenance AS jsonb))
                ON CONFLICT DO NOTHING"""), {"at": provenance["observed_at"], "key": underlying, "expiry": expiry,
                "day": provenance["session_date"], "data": json.dumps(payload, allow_nan=False), "provenance": json.dumps(provenance, allow_nan=False)})

    def retained_chain(self, underlying, expiry, day):
        self.store.initialize()
        with self.store.engine.connect() as conn:
            row = conn.execute(text("""SELECT payload,provenance,observed_at FROM market_stream_chains
                WHERE underlying_key=:key AND expiry=CAST(:expiry AS date) AND session_date=CAST(:day AS date)
                AND observed_at<=:cutoff ORDER BY observed_at DESC LIMIT 1"""),
                {"key": underlying, "expiry": expiry, "day": day, "cutoff": now()}).mappings().first()
        return {"payload": row["payload"], **row["provenance"], "observed_at": row["observed_at"].isoformat()} if row else None
