"""Volume PCR from complete, dated option-chain captures. Volumes are day-to-time totals."""
import math
from datetime import time

from .market_session import timestamp
from .market_store import IST


def number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) and result >= 0 else None
    except (TypeError, ValueError):
        return None


def chain_point(capture, underlying, expiry, day, cutoff):
    at = timestamp(capture.get("observed_at"))
    rows = capture.get("payload")
    if not at or at > cutoff or at.astimezone(IST).date().isoformat() != day or day > expiry or not isinstance(rows, list) or not rows:
        return None
    # REST has acquisition times, not exchange timestamps. Do not relabel an
    # overnight/current response as an earlier session or as its closing minute.
    clock = at.astimezone(IST).time()
    if not time(9, 15) <= clock <= time(15, 30, 59):
        return None
    meta = capture.get("provenance") or capture
    if meta.get("session_date") not in (None, day):
        return None
    source = "rest_capture"
    if meta.get("transport") == "websocket":
        volume_at = timestamp(meta.get("volume_reported_at"))
        if meta.get("live_volume_legs") == len(rows) * 2 and volume_at and volume_at.astimezone(IST).date().isoformat() == day and -5 <= (at - volume_at).total_seconds() <= 30:
            source = "websocket_capture"
        else:
            # Legacy/mixed captures lack per-field volume provenance. Accept
            # only a recent full REST baseline, never an arbitrarily old seed.
            seed = timestamp(meta.get("rest_seed_at"))
            if not seed or seed.astimezone(IST).date().isoformat() != day or not 0 <= (at - seed).total_seconds() <= 60:
                return None
            source = "mixed_capture"
    totals = {"call_options": 0.0, "put_options": 0.0}
    strikes, legs = set(), set()
    for row in rows:
        if not isinstance(row, dict) or row.get("expiry") != expiry or row.get("underlying_key") != underlying:
            return None
        strike = number(row.get("strike_price"))
        if not strike or strike in strikes:
            return None
        strikes.add(strike)
        for side in totals:
            option = row.get(side)
            if not isinstance(option, dict):
                return None
            key = option.get("instrument_key")
            volume = number((option.get("market_data") or {}).get("volume"))
            if not isinstance(key, str) or not key or key in legs or volume is None:
                return None
            legs.add(key)
            totals[side] += volume
    call, put = totals["call_options"], totals["put_options"]
    if call <= 0 or not math.isfinite(call + put):
        return None
    spot = number(rows[0].get("underlying_spot_price"))
    return {"time": at.astimezone(IST).strftime("%H:%M"), "volume_pcr": put / call,
            "call_volume": call, "put_volume": put, "spot": spot if spot and spot > 0 else None,
            "volume_observed_at": at.isoformat(), "volume_source": source}


def chain_series(captures, underlying, expiry, day, cutoff):
    points = {}
    for capture in captures:
        point = chain_point(capture, underlying, expiry, day, cutoff)
        if point and (point["time"] not in points or timestamp(point["volume_observed_at"]) > timestamp(points[point["time"]]["volume_observed_at"])):
            points[point["time"]] = point
    return [points[minute] for minute in sorted(points)]
