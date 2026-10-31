"""Shared exchange-session decisions; quote receipt is not a source trade time."""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

from .market_store import IST, now


def timestamp(value):
    try:
        if isinstance(value, (int, float)) or str(value).isdigit():
            numeric = float(value)
            return datetime.fromtimestamp(numeric / 1000 if numeric > 1e11 else numeric, timezone.utc)
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result if result.tzinfo else None
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def quote_entry(payload, key):
    if not isinstance(payload, dict):
        return {}
    return next((value for name, value in payload.items() if isinstance(value, dict) and
                 (value.get("instrument_token") == key or value.get("instrument_key") == key or
                  name in (key, key.replace("|", ":"), key.replace("|", "_")))), {})


def session_context(key, status, timings, quote, at, segment_status=None):
    exchange = key.split("_", 1)[0]
    segment = {"NSE_FO": "NFO", "BSE_FO": "BFO"}.get(key.split("|", 1)[0], exchange)
    today = at.astimezone(IST).date().isoformat()
    state = segment_status or (status.get("status") if isinstance(status, dict) else None)
    status_at = timestamp(status.get("last_updated")) if isinstance(status, dict) else None
    windows = [row for row in timings or [] if row.get("exchange") == segment]
    scheduled = None if timings is None else any(timestamp(row.get("start_time")) and timestamp(row.get("end_time")) and
        timestamp(row["start_time"]) <= at < timestamp(row["end_time"]) for row in windows)
    recent_status = status_at is not None and status_at.astimezone(IST).date().isoformat() == today and status_at <= at
    active = state == "NORMAL_OPEN" and scheduled is not False and (recent_status or bool(segment_status))
    entry = quote_entry(quote, key)
    traded = timestamp(entry.get("last_trade_time"))
    ohlc = entry.get("ohlc") or {}
    if isinstance(ohlc, list):
        ohlc = next((row for row in ohlc if row.get("interval") == "1d"), {})
    dated_bar = timestamp(ohlc.get("ts")) if isinstance(ohlc, dict) else None
    source_at = traded or dated_bar
    if source_at and source_at > at:
        source_at = None
    day = today if active else source_at.astimezone(IST).date().isoformat() if source_at else None
    return {"instrument_key": key, "exchange": exchange, "segment": segment,
        "market_status": state or "UNKNOWN", "active": active,
        "phase": "open" if active else "closed" if (state and state != "NORMAL_OPEN") or scheduled is False else "unknown",
        "session_date": day, "last_trade_at": traded.isoformat() if traded and traded <= at else None,
        "status_updated_at": status_at.isoformat() if status_at else None, "checked_at": at.isoformat(),
        "timestamp_basis": "Last trade time" if traded else "Dated daily OHLC" if dated_bar else "Not supplied",
        "source": "Upstox exchange status, session calendar and quote"}


class MarketSessions:
    def __init__(self, gateway):
        self.gateway = gateway
        self.lock = threading.RLock()
        self.cache = {}
        self.segments = {}

    def update_segments(self, values):
        with self.lock:
            self.segments = {key: (value, time.monotonic()) for key, value in values.items()}
            self.cache.clear()

    def context(self, key):
        at = now()
        cache_key = (key, at.astimezone(IST).date().isoformat())
        with self.lock:
            cached = self.cache.get(cache_key)
            if cached and cached[0] > time.monotonic():
                return dict(cached[1])
        errors = []
        def read(method, *args):
            try:
                return self.gateway._cached_rest(method, *args)
            except Exception as exc:
                errors.append(f"{method}: {type(exc).__name__}")
                return None
        exchange = key.split("_", 1)[0]
        status = read("get_market_status", exchange)
        timings = read("get_market_timings", cache_key[1])
        live = getattr(self.gateway, "live", None)
        quotes = live.quotes([key]) if live else {}
        if not quotes:
            quotes = read("get_full_market_quotes_v3", [key])
        with self.lock:
            value = self.segments.get(key.split("|", 1)[0])
        stream_status = value[0] if value and time.monotonic() - value[1] < 60 else None
        result = session_context(key, status, timings, quotes, at, stream_status)
        result["errors"] = errors
        with self.lock:
            self.cache[cache_key] = (time.monotonic() + 30, result)
            if len(self.cache) > 1800:
                self.cache = {cache_key: self.cache[cache_key]}
        return dict(result)
