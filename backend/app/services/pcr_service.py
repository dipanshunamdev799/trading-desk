"""Dated PCR history, using the same durable gateway and session checks as Max Pain."""
import math
import re

from .max_pain_service import _now, _session
import nifty_max_pain as nmp
from .upstox_service import get_upstox


def number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None
    except (ValueError, TypeError):
        return None


def series(payload, day, at):
    points = {}
    cutoff = at.strftime("%H:%M") if day == at.date().isoformat() else "23:59"
    for row in payload.get("insights") or []:
        if not isinstance(row, dict):
            continue
        clock = str(row.get("time") or "")
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", clock) or clock > cutoff:
            continue
        if any(row.get(field) not in (None, day) for field in ("date", "as_of", "session_date")):
            continue
        points[clock] = {"time": clock, "pcr": number(row.get("pcr")), "spot": number(row.get("spot_price"))}
    return [points[key] for key in sorted(points)]


def intraday(expiry, as_of=None, instrument_key=nmp.NIFTY_KEY):
    at = _now()
    day = as_of or at.date().isoformat()
    client = get_upstox()
    valid, close, hint = _session(client, day, expiry, instrument_key)
    payload = {}
    volume_points = []
    oi_error = volume_error = None
    if valid:
        try:
            payload = client.get_pcr(instrument_key, expiry=expiry, date=day, bucket_interval=1) or {}
        except Exception:
            oi_error = "OI PCR history could not be loaded."
        if not nmp.dated_payload_matches(payload, expiry, day, instrument_key,
                                         close if day != at.date().isoformat() else None):
            payload = {}
        try:
            retained = client.get_volume_pcr_history(instrument_key, expiry, day)
            if isinstance(retained, list):
                volume_points = retained
        except Exception:
            volume_error = "Volume PCR history could not be loaded."
    by_time = {point["time"]: point for point in series(payload, day, at)}
    for point in volume_points:
        minute = point["time"]
        existing = by_time.setdefault(minute, {"time": minute, "pcr": None, "spot": None})
        existing.update({key: value for key, value in point.items() if key != "spot"})
        if existing["spot"] is None:
            existing["spot"] = point.get("spot")
    points = [by_time[minute] for minute in sorted(by_time)]
    oi_available = any(point["pcr"] is not None for point in points)
    volume_available = any(point.get("volume_pcr") is not None for point in points)
    available = oi_available or volume_available
    return {"instrument_key": instrument_key, "expiry": expiry, "as_of": day,
            "bucket_minutes": 1, "points": points, "data_available": available,
            "oi_pcr_available": oi_available, "volume_pcr_available": volume_available,
            "volume_basis": "Total put traded volume / total call traded volume, cumulative for the session through each capture; selected expiry only.",
            "volume_hint": None if volume_available else hint or volume_error or f"No complete intraday option-volume captures saved for {day}, expiry {expiry}.",
            "oi_hint": None if oi_available else hint or oi_error or f"No verified OI PCR observations for {day}, expiry {expiry}.",
            "source": "Tapetide" if payload.get("_provider") == "tapetide" else "Upstox",
            "fetched_at": at.isoformat(timespec="seconds"),
            "hint": None if available else hint or oi_error or f"No verified intraday PCR observations for {day}, expiry {expiry}."}
