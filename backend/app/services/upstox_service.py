from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from upstox_analytics import UpstoxAnalyticsClient  # noqa: E402

from ..config import get_settings  # noqa: E402
from .market_gateway import MarketGateway  # noqa: E402
from .market_store import MarketStore  # noqa: E402


_client: Optional[MarketGateway] = None
_store: Optional[MarketStore] = None
_init_lock = threading.RLock()


def get_market_store() -> MarketStore:
    global _store
    with _init_lock:
        if _store is None:
            _store = MarketStore(get_settings().database_url_sync)
    return _store


def get_upstox() -> MarketGateway:
    """Lazy singleton so the API can boot without a token and degrade gracefully."""
    global _client
    with _init_lock:
        if _client is None:
            settings = get_settings()
            token = settings.upstox_analytics_token
            _client = MarketGateway(UpstoxAnalyticsClient(analytics_token=token, allow_missing_token=True), get_market_store(), settings.upstox_requests_per_second)
            if settings.tapetide_fallback_enabled and settings.tapetide_token.get_secret_value():
                from tapetide_data import TapetideClient
                from .data_providers import TapetideFallback
                _client.fallback = TapetideFallback(TapetideClient(
                    settings.tapetide_token.get_secret_value(), settings.tapetide_timeout_seconds,
                    settings.tapetide_requests_per_second), get_market_store())
            from .market_stream import MarketStream
            _client.live = MarketStream(_client, settings)
    return _client


def has_token() -> bool:
    return bool(get_settings().upstox_analytics_token)


def fetch_candles(
    instrument_key: str,
    interval: str,
    to_date: str,
    from_date: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Fetch historical candles from Upstox.

    interval accepts either V3 unit style ("1minute"/"1day") or V3 numeric unit
    via a small mapping so the API layer stays simple.
    """
    client = get_upstox()
    unit, unit_interval = _parse_interval(interval)

    raw = client.get_historical_candles_v3(
        instrument_key=instrument_key,
        unit=unit,
        interval=unit_interval,
        to_date=to_date,
        from_date=from_date,
    )
    return _normalize_candles(raw)


def fetch_intraday(instrument_key: str, interval: str = "1minute") -> list[dict[str, Any]]:
    client = get_upstox()
    unit, unit_interval = _parse_interval(interval)
    raw = client.get_intraday_candles_v3(
        instrument_key=instrument_key,
        unit=unit,
        interval=unit_interval,
    )
    return _normalize_candles(raw)


def fetch_ltp(instrument_keys: list[str]) -> dict[str, Any]:
    client = get_upstox()
    return client.get_ltp_quotes_v3(instrument_keys)


def fetch_market_status(exchange: str = "NSE") -> Any:
    client = get_upstox()
    return client.get_market_status(exchange)


def search_instruments(query: str, records: int = 20) -> Any:
    client = get_upstox()
    return client.search_instruments(query=query, records=records)


def _parse_interval(interval: str) -> tuple[str, int]:
    """Map friendly interval strings to Upstox V3 unit + interval."""
    mapping = {
        "1minute": ("minutes", 1),
        "3minute": ("minutes", 3),
        "5minute": ("minutes", 5),
        "15minute": ("minutes", 15),
        "30minute": ("minutes", 30),
        "60minute": ("hours", 1),
        "1hour": ("hours", 1),
        "1day": ("days", 1),
        "day": ("days", 1),
        "1week": ("weeks", 1),
        "week": ("weeks", 1),
        "1month": ("months", 1),
        "month": ("months", 1),
    }
    if interval in mapping:
        return mapping[interval]
    # allow "5m" / "1d" style
    aliases = {
        "1m": ("minutes", 1),
        "3m": ("minutes", 3),
        "5m": ("minutes", 5),
        "15m": ("minutes", 15),
        "30m": ("minutes", 30),
        "1h": ("hours", 1),
        "1d": ("days", 1),
        "1w": ("weeks", 1),
        "1M": ("months", 1),
    }
    if interval in aliases:
        return aliases[interval]
    raise ValueError(f"Unsupported interval: {interval}")


def _normalize_candles(raw: Any) -> list[dict[str, Any]]:
    """Upstox returns [[ts, o, h, l, c, vol, oi], ...] or {"candles": [...]}."""
    if isinstance(raw, dict):
        rows = raw.get("candles", [])
    else:
        rows = raw or []

    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 5:
            continue
        out.append(
            {
                "ts": row[0],
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]) if len(row) > 5 and row[5] is not None else None,
                "oi": float(row[6]) if len(row) > 6 and row[6] is not None else None,
            }
        )
    out.sort(key=lambda x: x["ts"])
    return out
