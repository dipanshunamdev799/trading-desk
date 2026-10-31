"""Expiry-specific ATM IV research from original, dated option-chain captures."""
from datetime import datetime, time, timedelta
import math

from .market_session import timestamp
from .market_store import IST


def positive(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) and value > 0 else None
    except (ValueError, TypeError):
        return None


def capture_point(capture, underlying, expiry, cutoff):
    at = timestamp(capture.get("observed_at"))
    rows = capture.get("payload")
    if not at or at > cutoff or not isinstance(rows, list) or not rows:
        return None
    local = at.astimezone(IST)
    day = local.date().isoformat()
    if day > expiry or not time(9, 15) <= local.time() <= time(15, 30, 59):
        return None
    meta = capture.get("provenance") or capture
    if meta.get("session_date") not in (None, day):
        return None
    if meta.get("transport") == "websocket":
        spot_at = timestamp(meta.get("spot_reported_at")) or timestamp(meta.get("rest_seed_at"))
        if not spot_at or spot_at.astimezone(IST).date().isoformat() != day or not 0 <= (at-spot_at).total_seconds() <= (30 if meta.get("spot_source") == "websocket" else 60):
            return None  # A stale spot cannot identify the current ATM strike.
    strikes, spot, seen = [], None, set()
    for row in rows:
        if not isinstance(row, dict) or row.get("underlying_key") != underlying or row.get("expiry") != expiry:
            return None
        strike = positive(row.get("strike_price"))
        current_spot = positive(row.get("underlying_spot_price"))
        if not strike or strike in seen or not current_spot or (spot is not None and abs(current_spot-spot) > .01):
            return None
        spot = current_spot
        seen.add(strike)
        strikes.append(row)
    # Select by spot before validating IV: never substitute a more distant strike.
    row = min(strikes, key=lambda r: (abs(float(r["strike_price"])-spot), float(r["strike_price"])))
    values, sources, identities = [], [], set()
    for side in ("call_options", "put_options"):
        leg = row.get(side) or {}
        key = leg.get("instrument_key")
        iv = positive((leg.get("option_greeks") or {}).get("iv"))
        if not isinstance(key, str) or not key or key in identities or iv is None:
            return None
        identities.add(key)
        source = "REST capture"
        if meta.get("transport") == "websocket":
            provenance = leg.get("_provenance") or {}
            source_at = timestamp(provenance.get("iv_at"))
            streamed = provenance.get("iv_source") == "websocket"
            if not source_at and not streamed:
                source_at = timestamp(meta.get("rest_seed_at"))
            if not source_at or source_at.astimezone(IST).date().isoformat() != day or not 0 <= (at-source_at).total_seconds() <= (30 if streamed else 60):
                return None
            source = "WebSocket" if streamed else "REST seed"
        values.append(iv); sources.append(source)
    iv = values[0]/2 + values[1]/2  # Chain IV is percent; feed adapter converts fraction once.
    if not math.isfinite(iv):
        return None
    expiry_at = datetime.combine(datetime.fromisoformat(expiry).date(), time(15, 30), IST)
    days = max(0, (expiry_at-at).total_seconds()/86400)
    move = spot * (iv/100) * math.sqrt(days/365)
    if move is not None and not math.isfinite(move):
        move = None
    return {"date": day, "time": local.strftime("%H:%M"), "observed_at": at.isoformat(),
            "iv": iv, "call_iv": values[0], "put_iv": values[1], "strike": float(row["strike_price"]),
            "spot": spot, "expected_move": move,
            "lower": max(0, spot-move) if move is not None else None,
            "upper": spot+move if move is not None else None, "days_to_expiry": days,
            "source": sources[0] if sources[0] == sources[1] else "Mixed REST / WebSocket"}


def minute_points(captures, underlying, expiry, cutoff):
    points = {}
    for capture in captures:
        point = capture_point(capture, underlying, expiry, cutoff)
        if point:
            key = (point["date"], point["time"])
            if key not in points or timestamp(point["observed_at"]) > timestamp(points[key]["observed_at"]):
                points[key] = point
    return [points[key] for key in sorted(points)]


def daily_samples(points, day, lookback=252):
    first = (datetime.fromisoformat(day)-timedelta(days=365)).date().isoformat()
    daily = {}
    for point in points:
        if first <= point["date"] < day:
            previous = daily.get(point["date"])
            if previous is None or timestamp(point["observed_at"]) > timestamp(previous["observed_at"]):
                daily[point["date"]] = point
    return [daily[key] for key in sorted(daily)][-lookback:]


def ranked(point, baseline):
    values = [row["iv"] for row in baseline]
    result = {**point, "iv_rank": None, "iv_percentile": None, "history_sessions": len(values)}
    # At least two distinct prior daily observations, rather than treating
    # hundreds of intraday ticks as hundreds of historical sessions.
    if len(values) < 2:
        return result
    low, high = min(*values, point["iv"]), max(*values, point["iv"])
    result["history_low"], result["history_high"] = low, high
    if high > low:
        result["iv_rank"] = 100*(point["iv"]-low)/(high-low)
    result["iv_percentile"] = 100*sum(value < point["iv"] for value in values)/len(values)
    return result
