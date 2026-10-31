"""Dated Max Pain IV panel. Raw history remains in the shared Timescale store."""
from datetime import date

from .iv_metrics import ranked
from .max_pain_service import _now, _session
from .upstox_service import get_upstox


def history(expiry, as_of=None, instrument_key="NSE_INDEX|Nifty 50"):
    at = _now()
    day = as_of or at.date().isoformat()
    date.fromisoformat(expiry); date.fromisoformat(day)
    client = get_upstox()
    valid, _, hint = _session(client, day, expiry, instrument_key)
    points, baseline, error = [], [], None
    if valid:
        try:
            saved = client.get_iv_history(instrument_key, expiry, day)
            baseline = saved["daily"]
            points = [ranked(point, baseline) for point in saved["points"]]
        except Exception:
            error = "Saved IV history could not be loaded. Refresh to retry."
    count = len(baseline)
    partial = count < 252
    rank_hint = (f"Only {count}/252 prior sessions saved for this expiry. At least 2 are required for sample rank and percentile."
                 if count < 2 else f"Partial history: {count}/252 prior sessions saved for this expiry. Rank and percentile describe this sample."
                 if partial else "252 prior saved session readings for this expiry in the preceding 365 calendar days.")
    return {"instrument_key": instrument_key, "expiry": expiry, "as_of": day,
            "points": points, "daily_history": baseline, "history_sessions": count, "history_target": 252,
            "history_partial": partial, "rank_hint": rank_hint,
            "data_available": bool(points), "fetched_at": at.isoformat(),
            "hint": None if points else hint or error or f"No usable regular-session ATM IV captures saved for {day}, expiry {expiry}.",
            "iv_basis": "Selected expiry, strike nearest spot (lower strike wins ties), mean of positive call and put IV at that same strike. IV is annualised percent.",
            "rank_basis": "Expiry-specific sample: up to 252 prior sessions within 365 calendar days, one last saved regular-session reading per day. Current IV is included in rank high/low. Percentile counts prior readings strictly below current IV; ties are excluded.",
            "move_basis": "Expected move = spot × IV/100 × sqrt(calendar time remaining to expiry at 15:30 IST / 365 days). Approximate one-standard-deviation amplitude in underlying points; spot ± amplitude is a model range, not a guaranteed boundary.",
            "source": "Saved Upstox option-chain / WebSocket captures"}
