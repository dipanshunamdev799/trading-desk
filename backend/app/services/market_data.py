from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from sqlalchemy import delete, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from .market_store import IST, canonical_interval

from ..models import Candle, Instrument
from . import upstox_service

Source = Literal["cache", "db", "db_partial", "upstox", "tapetide", "mixed", "empty"]

# asyncpg rejects >32767 bind params per statement (10 cols * 500 rows = 5000).
UPSERT_CHUNK = 500

# How far back to go when the caller does not pass from_date.
_DEFAULT_LOOKBACK_DAYS = {
    "1minute": 90,
    "3minute": 90,
    "5minute": 120,
    "15minute": 180,
    "30minute": 180,
    "1hour": 365,
    "60minute": 365,
    "1h": 365,
    "1m": 90,
    "3m": 90,
    "5m": 120,
    "15m": 180,
    "30m": 180,
    "1day": 3650,
    "day": 3650,
    "1d": 3650,
    "1week": 3650,
    "week": 3650,
}

def _as_datetime(value: str, *, end_of_day: bool = False) -> datetime:
    """Accept a date in IST or a timezone-aware full timestamp."""
    text = value.strip().replace("Z", "+00:00")
    if len(text) == 10:
        text = f"{text}T23:59:59.999999+05:30" if end_of_day else f"{text}T00:00:00+05:30"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid date: {value}") from exc
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    # Upstox sometimes returns "YYYY-MM-DDTHH:MM:SS+05:30" or without tz
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        dt = datetime.strptime(str(value)[:19], "%Y-%m-%dT%H:%M:%S")
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def backfill_candles(
    db: AsyncSession,
    instrument_key: str,
    interval: str,
    from_date: str,
    to_date: Optional[str] = None,
) -> int:
    """Fill only uncovered dates; the gateway commits each fetched window."""
    unit, grain = upstox_service._parse_interval(interval)
    result = await run_in_threadpool(
        upstox_service.get_upstox().get_historical_candles_v3,
        instrument_key, unit, grain,
        to_date or datetime.now(IST).date().isoformat(), from_date,
    )
    return int(result.get("_written", 0))


async def get_candles(
    db: AsyncSession,
    instrument_key: str,
    interval: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    force_refresh: bool = False,
) -> tuple[list[Candle], Source]:
    """One shared cache/DB/API path for chart, option and research candles."""
    current = datetime.now(IST)
    effective_from = from_date or (current - timedelta(days=_DEFAULT_LOOKBACK_DAYS.get(interval, 365))).date().isoformat()
    effective_to = to_date or current.date().isoformat()
    start_dt, end_dt = _as_datetime(effective_from), _as_datetime(effective_to, end_of_day=True)
    if end_dt < start_dt:
        raise ValueError("to_date must be on or after from_date")
    unit, grain = upstox_service._parse_interval(interval)
    result = await run_in_threadpool(
        upstox_service.get_upstox().get_historical_candles_v3,
        instrument_key, unit, grain,
        end_dt.astimezone(IST).date().isoformat(), start_dt.astimezone(IST).date().isoformat(),
        force_refresh=force_refresh,
    )
    canonical = canonical_interval(unit, grain)
    # A memory hit already contains persisted bars; do not query PostgreSQL again.
    rows = [Candle(instrument_key=instrument_key, interval=canonical, ts=_parse_ts(c[0]),
        open=c[1], high=c[2], low=c[3], close=c[4], volume=c[5], oi=c[6],
        source="tapetide" if c[0] in result.get("_fallback_sources", {}) else "upstox")
        for c in result["candles"] if start_dt <= _parse_ts(c[0]) <= end_dt]
    return rows, ("db_partial" if result.get("_partial") else result.get("_source", "db")) if rows else "empty"


async def upsert_candles(
    db: AsyncSession,
    instrument_key: str,
    interval: str,
    candles: list[dict[str, Any]],
    source: str = "upstox",
) -> int:
    if not candles:
        return 0

    payload = [
        {
            "instrument_key": instrument_key,
            "interval": interval,
            "ts": _parse_ts(c["ts"]),
            "open": c["open"],
            "high": c["high"],
            "low": c["low"],
            "close": c["close"],
            "volume": c.get("volume"),
            "oi": c.get("oi"),
            "source": source,
        }
        for c in candles
    ]

    written = 0
    for start in range(0, len(payload), UPSERT_CHUNK):
        chunk = payload[start : start + UPSERT_CHUNK]
        stmt = pg_insert(Candle).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Candle.instrument_key, Candle.interval, Candle.ts],
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "volume": stmt.excluded.volume,
                "oi": stmt.excluded.oi,
                "source": stmt.excluded.source,
            },
        )
        result = await db.execute(stmt)
        written += result.rowcount or len(chunk)
    return written


async def list_instruments(db: AsyncSession, limit: int = 200) -> list[Instrument]:
    stmt = select(Instrument).order_by(Instrument.instrument_key).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


async def upsert_instrument(db: AsyncSession, data: dict[str, Any]) -> Instrument:
    key = data.get("instrument_key") or data.get("instrumentKey")
    if not key:
        raise ValueError("instrument_key required")

    existing = await db.get(Instrument, key)
    if existing is None:
        existing = Instrument(instrument_key=key)

    for field in (
        "name",
        "exchange",
        "segment",
        "instrument_type",
        "isin",
        "trading_symbol",
        "expiry",
        "strike",
        "option_type",
    ):
        if field in data and data[field] is not None:
            setattr(existing, field, data[field])
    existing.raw = data
    existing.fetched_at = datetime.now(timezone.utc)
    db.add(existing)
    await db.commit()
    await db.refresh(existing)
    return existing


async def coverage_summary(db: AsyncSession) -> list[dict[str, Any]]:
    from sqlalchemy import func

    # Hundreds of Timescale chunks can make JIT compilation dwarf the aggregate.
    # Limit the setting to this transaction, rather than changing PostgreSQL globally.
    await db.execute(text("SET LOCAL jit = off"))
    stmt = (
        select(
            Candle.instrument_key,
            Candle.interval,
            func.count().label("bars"),
            func.min(Candle.ts).label("first_ts"),
            func.max(Candle.ts).label("last_ts"),
        )
        .group_by(Candle.instrument_key, Candle.interval)
        .order_by(Candle.instrument_key, Candle.interval)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "instrument_key": r.instrument_key,
            "interval": r.interval,
            "bars": r.bars,
            "first_ts": r.first_ts,
            "last_ts": r.last_ts,
        }
        for r in rows
    ]


async def clear_candles(db: AsyncSession, instrument_key: Optional[str] = None) -> int:
    stmt = delete(Candle)
    if instrument_key:
        stmt = stmt.where(Candle.instrument_key == instrument_key)
    result = await db.execute(stmt)
    if instrument_key:
        await db.execute(text("DELETE FROM candle_coverage WHERE instrument_key=:key"), {"key": instrument_key})
    else:
        await db.execute(text("DELETE FROM candle_coverage"))
    await db.commit()
    upstox_service.get_market_store().cache.clear()
    return result.rowcount or 0
