"""Memory cache -> PostgreSQL -> upstream, with durable TimescaleDB series.

The cache is disposable. PostgreSQL records successful fetch coverage and the
original responses; TimescaleDB retains candles, intraday points and observations.
No API result is returned until its database transaction has committed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import threading
import time
from collections import Counter, OrderedDict
from datetime import date, datetime, time as day_time, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo
from weakref import WeakValueDictionary

from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert

from ..models import Candle

IST = ZoneInfo("Asia/Kolkata")
UTC = timezone.utc


def now() -> datetime:
    return datetime.now(UTC)


def market_day() -> date:
    return now().astimezone(IST).date()


def request_key(method: str, parameters: dict) -> str:
    encoded = json.dumps([method, parameters], sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode()).hexdigest()


def canonical_interval(unit: str, interval: int | str) -> str:
    names = {"minutes": "minute", "hours": "hour", "days": "day", "weeks": "week", "months": "month"}
    if unit not in names:
        raise ValueError(f"Unsupported candle unit: {unit}")
    return f"{int(interval)}{names[unit]}"


def present(payload: Any) -> bool:
    if isinstance(payload, dict) and "candles" in payload:
        return bool(payload["candles"])
    return payload is not None and payload != {} and payload != []


def expiry_time(method: str, parameters: dict, payload: Any, at: datetime) -> datetime | None:
    """Only positive completed history is immutable. Empty results are retried."""
    today = at.astimezone(IST).date().isoformat()
    day = parameters.get("date") or parameters.get("day")
    exp = parameters.get("expiry_date") or parameters.get("expiry")
    historical = bool(day and str(day) < today) or bool("expired" in method and exp and str(exp) < today)
    if method.startswith("tapetide."):
        # Secondary data never makes a historical Upstox miss immutable. Keep
        # its namespace refreshable, including dated data and provider revisions.
        return at + timedelta(seconds=5 if "quote" in method else 3600 if method in
            ("tapetide.search_stocks", "tapetide.get_stock_profile") else 300)
    if method in ("get_ipos", "get_ipo_details"):
        status = parameters.get("status") if method == "get_ipos" else (payload or {}).get("status")
        start = (payload or {}).get("bidding_start_date") if isinstance(payload, dict) else None
        seconds = (60 if status == "open" and (not start or start <= today) else
                   86400 if status == "listed" else 21600 if method == "get_ipo_details" and not start else 300)
        return at + timedelta(seconds=seconds)
    if method.startswith("ipo_public_"):
        kind = method.removeprefix("ipo_public_")
        seconds = {"index": 300, "subscriptions": 60, "gmp": 300,
                   "fundamentals": 21600, "subscription_detail": 900, "recommendations": 3600}[kind]
        return at + timedelta(seconds=seconds)
    # An empty successful calendar response means no exchange session, rather
    # than an absent price. Retain that evidence instead of retrying each minute.
    if method == "get_market_timings" and isinstance(payload, list):
        return None if historical else at + timedelta(days=1)
    if historical and present(payload):
        return None
    if not present(payload):
        return at + timedelta(seconds=86400 if historical else 60)
    if "contract" in method or "expiries" in method:
        return at + timedelta(hours=6)
    if "search" in method:
        return at + timedelta(hours=1)
    if "market_timings" in method or "market_holidays" in method:
        return at + timedelta(days=1)
    if "quote" in method or "ltp" in method or "market_status" in method:
        return at + timedelta(seconds=5)
    return at.replace(second=0, microsecond=0) + timedelta(minutes=1)


class MemoryCache:
    def __init__(self, max_entries: int = 512, max_bytes: int = 16 * 1024 * 1024):
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self.entries: OrderedDict[str, tuple[float, Any, int]] = OrderedDict()
        self.size = 0
        self.lock = threading.Lock()

    def get(self, key: str) -> tuple[bool, Any]:
        with self.lock:
            entry = self.entries.get(key)
            if entry is None:
                return False, None
            deadline, payload, size = entry
            if deadline <= time.monotonic():
                self.entries.pop(key)
                self.size -= size
                return False, None
            self.entries.move_to_end(key)
            return True, copy.deepcopy(payload)

    def put(self, key: str, payload: Any, ttl: float):
        size = len(json.dumps(payload, default=str))
        if size > self.max_bytes // 2 or ttl <= 0:
            return
        with self.lock:
            old = self.entries.pop(key, None)
            if old:
                self.size -= old[2]
            self.entries[key] = (time.monotonic() + min(ttl, 3600), copy.deepcopy(payload), size)
            self.size += size
            while len(self.entries) > self.max_entries or self.size > self.max_bytes:
                self.size -= self.entries.popitem(last=False)[1][2]

    def clear(self):
        with self.lock:
            self.entries.clear()
            self.size = 0


class MarketStore:
    def __init__(self, url: str, *, cache: MemoryCache | None = None):
        self.engine = create_engine(url, pool_pre_ping=True, pool_size=12, max_overflow=12)
        self.cache = cache or MemoryCache()
        self.locks: WeakValueDictionary = WeakValueDictionary()
        self.locks_guard = threading.Lock()
        self.metrics: Counter = Counter()
        self.metrics_lock = threading.Lock()
        self.schema_lock = threading.Lock()
        self.initialized = False

    def initialize(self):
        with self.schema_lock:
            if self.initialized:
                return
            migrations = sorted((Path(__file__).resolve().parents[2] / "sql").glob("*.sql"))
            with self.engine.begin() as conn:
                conn.execute(text("SELECT pg_advisory_xact_lock(73182042)"))
                conn.execute(text("""CREATE TABLE IF NOT EXISTS market_schema_migrations (
                    version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"""))
                for migration in migrations:
                    if migration.name < "002_market_integration.sql":
                        continue  # Base application tables are managed separately.
                    applied = conn.execute(text("SELECT 1 FROM market_schema_migrations WHERE version=:version"),
                                           {"version": migration.name}).scalar()
                    if not applied:
                        conn.exec_driver_sql(migration.read_text())
                        conn.execute(text("INSERT INTO market_schema_migrations(version) VALUES(:version)"),
                                     {"version": migration.name})
            self.initialized = True

    def count(self, name: str):
        with self.metrics_lock:
            self.metrics[name] += 1

    def _lock(self, key: str):
        with self.locks_guard:
            lock = self.locks.get(key)
            if lock is None:
                lock = threading.RLock()
                self.locks[key] = lock
            return lock

    @staticmethod
    def _db_lock(conn, key: str):
        conn.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int(key[:15], 16)})

    @staticmethod
    def _cache_ttl(valid_until: datetime | None, at: datetime) -> float:
        return 3600 if valid_until is None else max(0, (valid_until - at).total_seconds())

    def _archive(self, conn, key: str, method: str, parameters: dict, payload: Any, at: datetime):
        conn.execute(text("""INSERT INTO market_responses(recorded_at,request_key,method,parameters,payload)
            VALUES (:at,:key,:method,CAST(:params AS jsonb),CAST(:payload AS jsonb))
            ON CONFLICT DO NOTHING"""), {"at": at, "key": key, "method": method,
            "params": json.dumps(parameters, default=str), "payload": json.dumps(payload, allow_nan=False)})

    def read(self, method: str, parameters: dict, load: Callable[[], Any], *,
             normalize: Callable | None = None, force: bool = False) -> Any:
        self.initialize()
        key = request_key(method, parameters)
        if not force:
            hit, payload = self.cache.get(key)
            if hit:
                self.count("cache_hits")
                return payload
        with self._lock(key):
            if not force:
                hit, payload = self.cache.get(key)
                if hit:
                    self.count("cache_hits")
                    return payload
            with self.engine.begin() as conn:
                self._db_lock(conn, key)
                record = conn.execute(text("SELECT * FROM market_datasets WHERE request_key=:key"), {"key": key}).mappings().first()
                at = now()
                if not force and record and (record["valid_until"] is None or record["valid_until"] > at):
                    payload, valid_until = record["payload"], record["valid_until"]
                    self.count("db_hits")
                else:
                    # Exceptions do not create a successful/empty coverage record.
                    self.count("misses")
                    payload = load()
                    at = now()
                    valid_until = expiry_time(method, parameters, payload, at)
                    self._archive(conn, key, method, parameters, payload, at)
                    if normalize:
                        normalize(conn, payload, at)
                    # Retain the last successful value in the archive, but a failed
                    # live fetch never masquerades as a fresh successful response.
                    conn.execute(text("""INSERT INTO market_datasets
                        (request_key,method,parameters,payload,fetched_at,valid_until,data_present)
                        VALUES (:key,:method,CAST(:params AS jsonb),CAST(:payload AS jsonb),:at,:until,:present)
                        ON CONFLICT(request_key) DO UPDATE SET payload=excluded.payload,
                        fetched_at=excluded.fetched_at,valid_until=excluded.valid_until,data_present=excluded.data_present"""),
                        {"key": key, "method": method, "params": json.dumps(parameters, default=str),
                         "payload": json.dumps(payload, allow_nan=False), "at": at, "until": valid_until,
                         "present": present(payload)})
            # Populate memory only after COMMIT succeeds.
            self.cache.put(key, payload, self._cache_ttl(valid_until, now()))
            return copy.deepcopy(payload)

    def option_chain_snapshot(self, underlying: str, expiry: str, day: str) -> dict | None:
        """Latest original acquisition on one IST day, without any upstream call.

        The archive, rather than the most recent dataset, is needed after the live
        cache has moved to another session. Receipt time is not an exchange time.
        """
        self.initialize()
        start = datetime.fromisoformat(day).replace(tzinfo=IST)
        end = start + timedelta(days=1)
        key = request_key("get_option_chain", {
            "instrument_key": underlying, "expiry_date": expiry, "observed_on": day,
        })
        with self.engine.connect() as conn:
            row = conn.execute(text("""SELECT payload,recorded_at FROM market_responses
                WHERE request_key=:key AND method='get_option_chain'
                  AND recorded_at>=:start AND recorded_at<:end AND recorded_at<=:cutoff
                ORDER BY recorded_at DESC LIMIT 1"""),
                {"key": key, "start": start, "end": end, "cutoff": now()}).mappings().first()
        self.count("db_hits")
        return {"payload": row["payload"], "observed_at": row["recorded_at"].isoformat()} if row else None

    def recorded_session_dates(self, underlying: str, first: str, last: str) -> list[str]:
        """Chains archived by the active-session collector are dated session evidence."""
        self.initialize()
        with self.engine.connect() as conn:
            rows = conn.execute(text("""SELECT DISTINCT session_date FROM market_stream_chains
                WHERE underlying_key=:key AND session_date BETWEEN CAST(:first AS date) AND CAST(:last AS date)
                  AND observed_at<=:cutoff AND provenance->>'transport'='websocket'
                  AND provenance->>'session_date'=session_date::text
                  AND (observed_at AT TIME ZONE 'Asia/Kolkata')::date=session_date
                ORDER BY session_date DESC"""), {"key": underlying, "first": first, "last": last, "cutoff": now()})
            return [row[0].isoformat() for row in rows]

    def option_chain_history(self, underlying: str, expiry: str, day: str) -> list[dict]:
        """Original captures only; project volume fields to avoid loading every Greek."""
        self.initialize()
        start = datetime.fromisoformat(day).replace(tzinfo=IST)
        key = request_key("get_option_chain", {"instrument_key": underlying, "expiry_date": expiry, "observed_on": day})
        with self.engine.connect() as conn:
            rows = conn.execute(text("""WITH captures AS (
                SELECT recorded_at AS observed_at,payload,'{}'::jsonb AS provenance FROM market_responses
                WHERE request_key=:request AND method='get_option_chain' AND recorded_at>=:start AND recorded_at<:end AND recorded_at<=:cutoff
                UNION ALL
                SELECT observed_at,payload,provenance FROM market_stream_chains
                WHERE underlying_key=:key AND expiry=CAST(:expiry AS date) AND session_date=CAST(:day AS date)
                  AND observed_at>=:start AND observed_at<:end AND observed_at<=:cutoff
                ) SELECT observed_at,provenance,(SELECT jsonb_agg(jsonb_build_object(
                    'expiry',r->'expiry','underlying_key',r->'underlying_key','strike_price',r->'strike_price',
                    'underlying_spot_price',r->'underlying_spot_price',
                    'call_options',jsonb_build_object('instrument_key',r->'call_options'->'instrument_key','market_data',jsonb_build_object('volume',r->'call_options'->'market_data'->'volume')),
                    'put_options',jsonb_build_object('instrument_key',r->'put_options'->'instrument_key','market_data',jsonb_build_object('volume',r->'put_options'->'market_data'->'volume'))))
                    FROM jsonb_array_elements(CASE WHEN jsonb_typeof(payload)='array' THEN payload ELSE '[]'::jsonb END) AS r) AS payload
                FROM captures ORDER BY observed_at"""),
                {"request": key, "key": underlying, "expiry": expiry, "day": day,
                 "start": start, "end": start + timedelta(days=1), "cutoff": now()}).mappings().all()
        self.count("db_hits")
        return [dict(row) for row in rows]

    def iv_captures(self, underlying: str, expiry: str, first: str, last: str) -> list[dict]:
        """Project IV fields from original REST and Timescale captures; never fetch history from today's chain."""
        self.initialize()
        start = datetime.fromisoformat(first).replace(tzinfo=IST)
        end = datetime.fromisoformat(last).replace(tzinfo=IST) + timedelta(days=1)
        with self.engine.connect() as conn:
            rows = conn.execute(text("""WITH captures AS (
                SELECT recorded_at AS observed_at,payload,'{}'::jsonb AS provenance FROM market_responses
                WHERE method='get_option_chain' AND parameters->>'instrument_key'=:key AND parameters->>'expiry_date'=:expiry
                  AND recorded_at>=:start AND recorded_at<:end AND recorded_at<=:cutoff
                UNION ALL
                SELECT observed_at,payload,provenance FROM market_stream_chains
                WHERE underlying_key=:key AND expiry=CAST(:expiry AS date)
                  AND session_date BETWEEN CAST(:first AS date) AND CAST(:last AS date)
                  AND observed_at>=:start AND observed_at<:end AND observed_at<=:cutoff
                ) SELECT observed_at,provenance,(SELECT jsonb_agg(jsonb_build_object(
                    'expiry',r->'expiry','underlying_key',r->'underlying_key','strike_price',r->'strike_price',
                    'underlying_spot_price',r->'underlying_spot_price',
                    'call_options',jsonb_build_object('instrument_key',r->'call_options'->'instrument_key',
                        'option_greeks',jsonb_build_object('iv',r->'call_options'->'option_greeks'->'iv'),
                        '_provenance',r->'call_options'->'_provenance'),
                    'put_options',jsonb_build_object('instrument_key',r->'put_options'->'instrument_key',
                        'option_greeks',jsonb_build_object('iv',r->'put_options'->'option_greeks'->'iv'),
                        '_provenance',r->'put_options'->'_provenance')))
                    FROM jsonb_array_elements(CASE WHEN jsonb_typeof(payload)='array' THEN payload ELSE '[]'::jsonb END) AS r) AS payload
                FROM captures ORDER BY observed_at"""), {"key": underlying, "expiry": expiry, "first": first, "last": last,
                    "start": start, "end": end, "cutoff": now()}).mappings().all()
        self.count("db_hits")
        return [dict(row) for row in rows]

    def contracts(self, underlying: str, expiry: str | None = None) -> list[dict]:
        self.initialize()
        with self.engine.connect() as conn:
            records = conn.execute(text("""SELECT raw FROM option_contracts WHERE underlying_key=:key
                AND (CAST(:expiry AS date) IS NULL OR expiry=CAST(:expiry AS date))
                ORDER BY expiry,strike,option_type"""), {"key": underlying, "expiry": expiry})
            return [row[0] for row in records]

    def known_expiries(self, underlying: str) -> list[dict]:
        """Only actual contract identities or successfully retained analytics."""
        self.initialize()
        with self.engine.connect() as conn:
            return [dict(row) for row in conn.execute(text("""SELECT expiry, bool_or(observed) AS available FROM (
                SELECT expiry::text AS expiry, false AS observed FROM option_contracts WHERE underlying_key=:key
                UNION ALL
                SELECT parameters->>'expiry' AS expiry, true AS observed FROM market_datasets
                WHERE method IN ('get_max_pain','get_oi_data') AND data_present
                AND parameters->>'instrument_key'=:key
                AND parameters->>'expiry' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                ) AS known GROUP BY expiry ORDER BY expiry"""), {"key": underlying}).mappings()]

    def save_contracts(self, conn, underlying: str, rows: Any, at: datetime):
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            expiry = row.get("expiry") or row.get("expiry_date")
            strike = row.get("strike_price")
            kind = row.get("instrument_type") or row.get("option_type")
            key = row.get("instrument_key") or row.get("expired_instrument_key")
            if not expiry or strike is None or kind not in ("CE", "PE") or not key:
                continue
            conn.execute(text("""INSERT INTO option_contracts
                (underlying_key,expiry,strike,option_type,instrument_key,lot_size,raw,fetched_at)
                VALUES (:underlying,CAST(:expiry AS date),:strike,:kind,:key,:lot,CAST(:raw AS jsonb),:at)
                ON CONFLICT(underlying_key,expiry,strike,option_type) DO UPDATE
                SET instrument_key=excluded.instrument_key,lot_size=excluded.lot_size,
                raw=excluded.raw,fetched_at=excluded.fetched_at"""),
                {"underlying": underlying, "expiry": expiry, "strike": strike, "kind": kind,
                 "key": key, "lot": row.get("lot_size"), "raw": json.dumps(row), "at": at})

    def save_max_pain(self, conn, parameters: dict, payload: Any, at: datetime):
        if not payload:
            return
        day = parameters["date"]
        for row in payload.get("insights") or []:
            try:
                ts = datetime.fromisoformat(f"{day}T{row['time'][:5]}:00").replace(tzinfo=IST)
                mp, spot = row.get("max_pain"), row.get("spot_price")
                if any(value is not None and not math.isfinite(float(value)) for value in (mp, spot)):
                    continue
            except (KeyError, TypeError, ValueError):
                continue
            if ts > at or mp is None and spot is None:
                continue
            conn.execute(text("""INSERT INTO max_pain_points
                (instrument_key,expiry,bucket_minutes,ts,max_pain,spot,fetched_at)
                VALUES (:key,CAST(:expiry AS date),:bucket,:ts,:mp,:spot,:at)
                ON CONFLICT(instrument_key,expiry,bucket_minutes,ts) DO UPDATE
                SET max_pain=excluded.max_pain,spot=excluded.spot,fetched_at=excluded.fetched_at"""),
                {"key": parameters["instrument_key"], "expiry": parameters["expiry"],
                 "bucket": parameters["bucket_interval"], "ts": ts, "mp": mp, "spot": spot, "at": at})

    @staticmethod
    def _upsert_bars(conn, key: str, interval: str, rows: list):
        payload = []
        for row in rows:
            ts = datetime.fromisoformat(str(row[0]).replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=IST)
            payload.append({"instrument_key": key, "interval": interval, "ts": ts,
                "open": float(row[1]), "high": float(row[2]), "low": float(row[3]), "close": float(row[4]),
                "volume": row[5] if len(row) > 5 else None, "oi": row[6] if len(row) > 6 else None, "source": "upstox"})
        for offset in range(0, len(payload), 500):
            stmt = insert(Candle).values(payload[offset:offset + 500])
            stmt = stmt.on_conflict_do_update(index_elements=[Candle.instrument_key, Candle.interval, Candle.ts],
                set_={name: getattr(stmt.excluded, name) for name in ("open", "high", "low", "close", "volume", "oi", "source")})
            conn.execute(stmt)

    def latest_option_candle_day(self, key: str, first: date, last: date) -> date | None:
        """Locate retained traded daily bars; callers still verify newer coverage."""
        self.initialize()
        with self.engine.connect() as conn:
            ts = conn.execute(text("""SELECT max(ts) FROM candles WHERE instrument_key=:key
                AND interval='1day' AND ts>=:start AND ts<:end AND close>=0
                AND (volume IS NULL OR volume>0)"""), {"key": key,
                "start": datetime.combine(first, day_time.min, IST),
                "end": datetime.combine(last + timedelta(days=1), day_time.min, IST)}).scalar()
        return ts.astimezone(IST).date() if ts else None

    def candles(self, key: str, unit: str, interval: int | str, start: str, end: str,
                load: Callable[[str, str], Any], *, force: bool = False) -> dict:
        self.initialize()
        first, last = date.fromisoformat(start), date.fromisoformat(end)
        if last < first:
            raise ValueError("to_date must be on or after from_date")
        last = min(last, market_day())
        if last < first:
            return {"candles": []}
        grain = canonical_interval(unit, interval)
        params = {"instrument_key": key, "interval": grain, "from_date": start, "to_date": last.isoformat()}
        cache_key = request_key("candle_range", params)
        if not force:
            hit, result = self.cache.get(cache_key)
            if hit:
                self.count("cache_hits")
                return {**result, "_source": "db_partial" if result.get("_partial") else "cache", "_written": 0}
        # Serialize overlapping range fills for this instrument/grain, across workers too.
        lock_key = request_key("candle_fill", {"key": key, "interval": grain})
        with self._lock(lock_key):
            with self.engine.begin() as conn:
                self._db_lock(conn, lock_key)
                coverage = {row["day"]: row for row in conn.execute(text("""SELECT * FROM candle_coverage
                    WHERE instrument_key=:key AND interval=:grain AND day BETWEEN :first AND :last"""),
                    {"key": key, "grain": grain, "first": first, "last": last}).mappings()}
                at = now()
                current_period = (market_day() - timedelta(days=market_day().weekday()) if unit == "weeks" else
                                  market_day().replace(day=1) if unit == "months" else market_day())
                days = [first + timedelta(days=i) for i in range((last - first).days + 1)]
                # Daily bars saved by the earlier integration are already complete
                # for their own dated sessions, even without new coverage metadata.
                if grain == "1day":
                    retained = conn.execute(text("""SELECT DISTINCT (ts AT TIME ZONE 'Asia/Kolkata')::date AS day
                        FROM candles WHERE instrument_key=:key AND interval=:grain
                        AND ts>=:start AND ts<:end"""), {"key": key, "grain": grain,
                        "start": datetime.combine(first, day_time.min, IST),
                        "end": datetime.combine(last + timedelta(days=1), day_time.min, IST)}).scalars()
                    for day in retained:
                        if day < market_day() and day not in coverage:
                            conn.execute(text("""INSERT INTO candle_coverage(instrument_key,interval,day,checked_at,valid_until,row_count)
                                VALUES(:key,:grain,:day,:at,NULL,1) ON CONFLICT DO NOTHING"""),
                                {"key": key, "grain": grain, "day": day, "at": at})
                            coverage[day] = {"valid_until": None}
                missing = [d for d in days if force or d not in coverage or
                           coverage[d]["valid_until"] is not None and coverage[d]["valid_until"] <= at]
                # Fill holes, not just the first/last edge. Bound each API window.
                max_days = 3650 if unit in ("days", "weeks", "months") else 28 if unit == "minutes" and int(interval) <= 15 else 80
                windows = []
                for day in missing:
                    if windows and day == windows[-1][1] + timedelta(days=1) and (day - windows[-1][0]).days < max_days:
                        windows[-1][1] = day
                    else:
                        windows.append([day, day])
                written = 0
                partial = False
                for lo, hi in windows:
                    self.count("misses")
                    try:
                        raw = load(lo.isoformat(), hi.isoformat())
                    except Exception:
                        existing = conn.execute(text("""SELECT count(*) FROM candles WHERE instrument_key=:key
                            AND interval=:grain AND ts>=:start AND ts<:end"""), {"key": key, "grain": grain,
                            "start": datetime.combine(lo, day_time.min, IST),
                            "end": datetime.combine(hi + timedelta(days=1), day_time.min, IST)}).scalar()
                        if force or not existing:
                            raise
                        # Preserve real legacy observations without claiming that
                        # an upstream failure proves this whole range is complete.
                        partial = True
                        continue
                    rows = (raw or {}).get("candles", []) if isinstance(raw, dict) else raw or []
                    valid = []
                    for row in rows:
                        if not isinstance(row, (list, tuple)) or len(row) < 5:
                            continue
                        try:
                            ts = datetime.fromisoformat(str(row[0]).replace("Z", "+00:00"))
                            ts = ts.replace(tzinfo=IST) if ts.tzinfo is None else ts
                            if lo <= ts.astimezone(IST).date() <= hi and ts <= now() and all(math.isfinite(float(v)) for v in row[1:5]):
                                valid.append(row)
                        except (ValueError, TypeError):
                            continue
                    fetched = now()
                    window_params = {**params, "from_date": lo.isoformat(), "to_date": hi.isoformat()}
                    counts = Counter(str(row[0])[:10] for row in valid)
                    # Commit each successful window independently. A later upstream
                    # failure must not discard already received history.
                    with self.engine.begin() as writer:
                        self._upsert_bars(writer, key, grain, valid)
                        self._archive(writer, request_key("candles", window_params), "candles", window_params, {"candles": valid}, fetched)
                        for i in range((hi - lo).days + 1):
                            day = lo + timedelta(days=i)
                            count = counts[day.isoformat()]
                            until = (None if day < current_period and valid else
                                     fetched.replace(second=0, microsecond=0) + timedelta(minutes=1)
                                     if day >= current_period else fetched + timedelta(days=1))
                            writer.execute(text("""INSERT INTO candle_coverage(instrument_key,interval,day,checked_at,valid_until,row_count)
                                VALUES(:key,:grain,:day,:at,:until,:count)
                                ON CONFLICT(instrument_key,interval,day) DO UPDATE SET checked_at=excluded.checked_at,
                                valid_until=excluded.valid_until,row_count=excluded.row_count"""),
                                {"key": key, "grain": grain, "day": day, "at": fetched, "until": until, "count": count})
                    written += len(valid)
                start_ts = datetime.combine(first, day_time.min, IST)
                end_ts = datetime.combine(last + timedelta(days=1), day_time.min, IST)
                stored = conn.execute(text("""SELECT ts,open,high,low,close,volume,oi FROM candles
                    WHERE instrument_key=:key AND interval=:grain AND ts>=:start AND ts<:end ORDER BY ts"""),
                    {"key": key, "grain": grain, "start": start_ts, "end": end_ts})
                result = {"candles": [[row[0].astimezone(IST).isoformat(), *row[1:]] for row in stored],
                          "_source": "db_partial" if partial else "upstox" if missing else "db", "_written": written,
                          "_partial": partial}
                if not missing:
                    self.count("db_hits")
                # Empty/history gaps get a bounded negative cache, never permanent.
                ttl = ((now().replace(second=0, microsecond=0) + timedelta(minutes=1) - now()).total_seconds()
                       if last >= current_period else 60 if partial else 3600)
            if force:
                self.cache.clear()
            self.cache.put(cache_key, result, ttl)
            return result

    def status(self) -> dict:
        self.initialize()
        with self.engine.connect() as conn:
            hypertables = list(conn.execute(text("SELECT hypertable_name FROM timescaledb_information.hypertables WHERE hypertable_schema='public'")).scalars())
            datasets = [dict(row) for row in conn.execute(text("""SELECT method,count(*) AS requests,
                count(*) FILTER(WHERE data_present) AS with_data,max(fetched_at) AS latest_fetch
                FROM market_datasets GROUP BY method ORDER BY method""")).mappings()]
            counts = dict(conn.execute(text("""SELECT
                (SELECT count(*) FROM candles) AS candle_rows,
                (SELECT count(*) FROM candles WHERE instrument_key LIKE 'NSE_FO|%') AS option_candle_rows,
                (SELECT count(*) FROM option_contracts) AS option_contracts,
                (SELECT count(*) FROM max_pain_points) AS max_pain_points,
                (SELECT count(*) FROM market_responses) AS archived_responses,
                (SELECT count(*) FROM candle_coverage) AS covered_days,
                (SELECT count(*) FROM ipo_companies) AS ipo_companies,
                (SELECT count(*) FROM ipo_research) AS ipo_research_records,
                (SELECT count(*) FROM ipo_observations) AS ipo_observations,
                (SELECT count(*) FROM market_stream_ticks) AS market_stream_ticks,
                (SELECT count(*) FROM market_stream_chains) AS market_stream_chains""")).mappings().one())
        return {"path": ["memory_cache", "postgresql", "upstox"], "hypertables": hypertables,
                "retention": "No automatic deletion of market data", "counts": counts,
                "process_metrics": dict(self.metrics), "datasets": datasets}
