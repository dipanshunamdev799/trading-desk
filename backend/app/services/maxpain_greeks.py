"""Expose provider Greeks from original, exact-session option-chain captures.

No Greeks are estimated from closing premiums or OI. The gateway already archives
the complete live chain in TimescaleDB, so inspecting Greeks needs no extra API.
"""
from __future__ import annotations

import math
from datetime import datetime, time

from .market_store import IST

FIELDS = ("delta", "gamma", "theta", "vega", "iv")
SOURCE_URL = "https://upstox.com/developer/api-documentation/get-pc-option-chain/"


def number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def normalize(payload, instrument_key: str, expiry: str):
    if not isinstance(payload, list):
        raise ValueError("Saved option-chain format is unavailable")
    rows, seen, spot = [], set(), None
    for item in payload:
        if not isinstance(item, dict) or item.get("expiry", expiry) != expiry or item.get("underlying_key", instrument_key) != instrument_key:
            raise ValueError("Saved option-chain identity does not match the selection")
        strike = number(item.get("strike_price"))
        if strike is None or strike <= 0 or strike in seen:
            raise ValueError("Saved option chain has invalid or duplicate strikes")
        seen.add(strike)
        current_spot = number(item.get("underlying_spot_price"))
        if spot is None and current_spot is not None and current_spot > 0:
            spot = current_spot
        row = {"strike": strike}
        for side, name in (("call", "call_options"), ("put", "put_options")):
            option = item.get(name)
            data = option.get("option_greeks") if isinstance(option, dict) else None
            data = data if isinstance(data, dict) else {}
            values = {field: number(data.get(field)) for field in FIELDS}
            # Preserve signed put Delta and Theta, and genuine zeros. Reject
            # impossible ranges rather than converting a missing field to zero.
            for field in ("gamma", "vega", "iv"):
                if values[field] is not None and values[field] < 0:
                    values[field] = None
            if values["delta"] is not None and not -1 <= values["delta"] <= 1:
                values["delta"] = None
            row[side] = values
            if isinstance(option, dict) and option.get("_provenance"):
                row[side + "_provenance"] = option["_provenance"]
        rows.append(row)
    return sorted(rows, key=lambda row: row["strike"]), spot


def snapshot(client, instrument_key: str, expiry: str, as_of: str, *, valid_session: bool,
             checked_at: datetime, session_hint: str | None = None, latest=False, market_context=None) -> dict:
    result = {"instrument_key": instrument_key, "expiry": expiry, "as_of": as_of,
              "source": "Upstox option chain", "source_url": SOURCE_URL, "reported_at": None,
              "observed_at": None, "status": "unavailable", "data_available": False,
              "required": 0, "available": 0, "complete_legs": 0, "complete": False,
              "rows": [], "spot": None, "hint": None,
              "basis": "Per-option provider values; no lot or OI scaling. IV is the chain endpoint's percentage value. Capture time is not an exchange timestamp."}
    if not valid_session:
        result["hint"] = session_hint or f"No verified trading-session data for {as_of}; option Greeks are unavailable."
        return result
    try:
        if latest and (not market_context or market_context.get("session_date") != as_of or market_context.get("phase") == "unknown"):
            result["hint"] = "The latest provider snapshot's trading-session context could not be verified."
            return result
        saved = (client.get_current_option_chain_snapshot(instrument_key, expiry) if latest else
                 client.get_retained_option_chain(instrument_key, expiry, as_of))
        if not isinstance(saved, dict) or not saved.get("observed_at"):
            result["hint"] = f"No option Greeks snapshot was saved for {as_of}, expiry {expiry}. Dated OI and daily closing premiums do not contain Greeks."
            return result
        stamp = datetime.fromisoformat(saved["observed_at"])
        if stamp.tzinfo is None or (not latest and stamp.astimezone(IST).date().isoformat() != as_of) or stamp > checked_at:
            raise ValueError("Saved option-chain capture date does not match the selected session")
        if not latest and stamp.astimezone(IST).time() < time(9, 15):
            raise ValueError("Only a pre-open undated option-chain capture was saved; its market session cannot be verified")
        rows, spot = normalize(saved["payload"], instrument_key, expiry)
    except (KeyError, TypeError, ValueError) as exc:
        result["hint"] = str(exc)
        return result
    except Exception:
        result["hint"] = "Saved option Greeks could not be read. Refresh to retry; other snapshot data may still be available."
        return result
    legs = [row[side] for row in rows for side in ("call", "put")]
    available = sum(any(value is not None for value in leg.values()) for leg in legs)
    complete = sum(all(value is not None for value in leg.values()) for leg in legs)
    historical = as_of != checked_at.astimezone(IST).date().isoformat()
    retained = not historical and stamp.replace(second=0, microsecond=0) < checked_at.replace(second=0, microsecond=0)
    result.update({"rows": rows, "spot": spot, "observed_at": stamp.isoformat(),
                   "required": len(legs), "available": available, "complete_legs": complete,
                   "complete": bool(legs) and complete == len(legs), "data_available": bool(available),
                   "status": "historical" if historical else "retained" if retained else "snapshot"})
    if latest:
        transport = saved.get("transport", "rest")
        result.update(status="live" if transport == "websocket" and saved.get("live_legs", 0) else "rest_fallback" if market_context["active"] else "latest_rest",
                      source="Upstox WebSocket + REST seed" if transport == "websocket" else "Upstox option chain",
                      reported_at=saved.get("greeks_reported_at"), market_context=market_context,
                      live_legs=saved.get("live_legs", 0), transport=transport,
                      basis="Latest available provider values; per option, without lot/OI scaling. IV is shown as a percentage. Capture time and market timestamps are separate.")
        if not market_context["active"]:
            result["hint"] = (f"Market closed. Latest provider snapshot; last underlying trade/session {as_of}. "
                              "The provider does not timestamp each Greek, so this is not a certified historical closing-Greeks snapshot.")
        elif transport != "websocket":
            result["hint"] = "REST fallback while the live feed connects or recovers. This reading is not labelled live."
        elif saved.get("live_legs", 0) < len(legs):
            result["hint"] = f"{saved.get('live_legs', 0)}/{len(legs)} legs have fresh streamed Greeks; other legs retain their latest REST snapshot values."
    if not available:
        result.update(status="unavailable", hint="The saved option chain does not include usable Greeks for this selection.")
    elif complete != len(legs):
        result["hint"] = (result["hint"] + " " if result["hint"] else "") + f"Complete Delta/Gamma/Theta/Vega/IV for {complete}/{len(legs)} option legs; unavailable fields remain empty."
    return result
