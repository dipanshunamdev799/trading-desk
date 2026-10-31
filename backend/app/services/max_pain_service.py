"""
Thin FastAPI adapter around `nifty_max_pain.py`.

All option-chain math (max pain, payout curves, premium-adjusted P&L, PCR,
history series) lives in the research script. This module only:
  - injects the Upstox client
  - orchestrates fetch / fallback / API JSON shapes
  - maps CLI dataclasses → response dicts

Do not add formulas here — extend `nifty_max_pain.py` instead.
"""
from __future__ import annotations

import sys
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import nifty_max_pain as nmp  # noqa: E402

from .upstox_service import get_upstox  # noqa: E402
from .option_prices import historical_premiums  # noqa: E402
from .maxpain_greeks import snapshot as greek_snapshot  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")


def _now() -> datetime:
    return datetime.now(IST)


def _number(value: Any) -> Optional[float]:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _session(client: Any, day: str, expiry: str, key: str) -> tuple[bool, Optional[float], Optional[str]]:
    """Require an actual dated underlying candle; analytics carry forward on holidays."""
    selected = date.fromisoformat(day)
    today = _now().date()
    if selected > today:
        return False, None, f"No data for {day}: this date is in the future (IST)."
    if day > expiry:
        return False, None, f"No data for {day}: selected expiry {expiry} has already expired."
    if selected == today:
        try:
            timings = client.get_market_timings(day)
        except Exception:
            timings = None  # Retained dated candles remain valid if the calendar is unavailable.
        if isinstance(timings, list) and all(isinstance(row, dict) and row.get("exchange") for row in timings):
            exchange = key.split("_", 1)[0]
            if not any(row["exchange"] == exchange for row in timings):
                return False, None, f"No {exchange} trading session scheduled for {day} (IST)."
    closes = nmp.fetch_daily_closes(client, to_date=day, from_date=day, key=key)
    close = _number(closes.get(day))
    if close is not None:
        return True, close, None
    if selected == today:
        # Today's completed daily candle may not exist while the session is open.
        raw = client.get_intraday_candles_v3(key, "minutes", 1) or {}
        candles = raw.get("candles", []) if isinstance(raw, dict) else raw
        if any(isinstance(row, (list, tuple)) and row and str(row[0])[:10] == day for row in candles):
            return True, None, None
    # A previously committed active-session feed capture also proves this was
    # a trading day when the daily-candle source has a gap. REST receipt alone
    # is not session evidence and can never enable this fallback.
    if client.has_retained_market_session(key, day) is True:
        return True, None, None
    return False, None, f"No trading-session data available for {day} (IST)."


def _series(provider: dict[str, Any], day: str) -> list[dict[str, Any]]:
    rows = nmp.insights_to_series(provider)
    cutoff = _now().strftime("%H:%M") if day == _now().date().isoformat() else "23:59"
    result = []
    for row in rows:
        time = str(row.get("time") or "")[:5]
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            continue
        mp, spot = _number(row.get("max_pain")), _number(row.get("spot_price"))
        if time <= cutoff and (mp is not None or spot is not None):
            result.append({"time": time, "max_pain": mp, "spot_price": spot})
    return sorted(result, key=lambda row: row["time"])


def list_expiries(
    instrument_key: str = nmp.NIFTY_KEY,
    include_past: bool = True,
    past_days: int = 120,
    include_unverified: bool = True,
) -> list[dict[str, Any]]:
    """Return listed contracts and actual expiries retained in PostgreSQL.

    A weekly/monthly calendar does not establish an expiry: holidays shift dates,
    and most underlyings do not have weekly contracts. Dates known only from
    retained analytics keep their cycle unknown until contract metadata is saved.
    """
    from datetime import timedelta

    client = get_upstox()
    today = _now().date()
    earliest = today - timedelta(days=max(7, past_days))
    listed = nmp.list_expiries(client, instrument_key)
    known = {row["expiry"]: row for row in client.get_known_expiries(instrument_key)}
    result = {}
    for row in listed:
        day = date.fromisoformat(str(row["expiry"]))
        if day < today and (not include_past or day < earliest):
            continue
        result[row["expiry"]] = {**row, "past": day < today, "verified": True,
            "available": known.get(row["expiry"], {}).get("available", day >= today),
            "cycle": "weekly" if row.get("weekly") else "monthly"}
    if include_past:
        for expiry, row in known.items():
            day = date.fromisoformat(expiry)
            if expiry in result or not earliest <= day < today:
                continue
            if not include_unverified and not row["available"]:
                continue
            result[expiry] = {"expiry": expiry, "weekly": False, "cycle": "unknown",
                "lot_size": None, "n_contracts": 0, "past": True, "verified": True,
                "available": row["available"]}
    return [result[expiry] for expiry in sorted(result)]


def resolve_expiry(
    expiry: Optional[str], instrument_key: str = nmp.NIFTY_KEY
) -> tuple[str, int]:
    return nmp.resolve_expiry(get_upstox(), expiry, instrument_key)


def sessions(expiry: str, instrument_key: str = nmp.NIFTY_KEY) -> dict[str, Any]:
    """Selectable exchange sessions, not a claim of option/Greek coverage on each day."""
    from datetime import timedelta

    end = min(date.fromisoformat(expiry), _now().date())
    start = end - timedelta(days=365)
    client = get_upstox()
    closes = nmp.fetch_daily_closes(client, to_date=end.isoformat(), from_date=start.isoformat(), key=instrument_key)
    days = {day for day, close in closes.items()
            if start.isoformat() <= day <= end.isoformat() and (_number(close) or 0) > 0}
    retained = client.get_recorded_session_dates(instrument_key, start.isoformat(), end.isoformat())
    if isinstance(retained, list):
        days.update(day for day in retained if isinstance(day, str) and start.isoformat() <= day <= end.isoformat())
    if end == _now().date() and end.isoformat() not in days:
        valid, _, _ = _session(client, end.isoformat(), expiry, instrument_key)
        if valid:
            days.add(end.isoformat())
    return {"instrument_key": instrument_key, "expiry": expiry, "dates": sorted(days, reverse=True)}


def intraday(
    expiry: str,
    as_of: Optional[str] = None,
    instrument_key: str = nmp.NIFTY_KEY,
) -> dict[str, Any]:
    """Fetch genuine one-minute provider insights without rebuilding the full snapshot."""
    now = _now()
    day = as_of or now.date().isoformat()
    client = get_upstox()
    valid, close, hint = _session(client, day, expiry, instrument_key)
    if day == now.date().isoformat():
        close = None  # Closing spot can refer to yesterday during an open session.
    provider = {}
    if valid:
        provider = client.get_max_pain(instrument_key, expiry=expiry, date=day, bucket_interval=1) or {}
        if not nmp.dated_payload_matches(provider, expiry, day, instrument_key, close):
            provider = {}
    insights = _series(provider, day)
    return {
        "expiry": expiry,
        "as_of": day,
        "instrument_key": instrument_key,
        "bucket_minutes": 1,
        "insights": insights,
        "data_available": bool(insights),
        "hint": None if insights else hint or f"No verified one-minute insights for {day}, expiry {expiry}.",
        "fetched_at": _now().isoformat(timespec="seconds"),
    }


def snapshot(
    expiry: Optional[str] = None,
    as_of: Optional[str] = None,
    instrument_key: str = nmp.NIFTY_KEY,
    bucket: int = 15,
    view: str = "historical",
) -> dict[str, Any]:
    """Full max-pain snapshot: chain, local calc, provider insights, metrics."""
    client = get_upstox()
    market_context = client.get_market_session(instrument_key) if view == "latest" else None
    as_of = (market_context.get("session_date") if market_context else None) or as_of or _now().date().isoformat()
    try:
        contracts = nmp.list_expiries(client, instrument_key, expiry=expiry)
    except Exception:
        if not expiry:
            raise
        contracts = []  # Retained analytics remain readable without a contract master.
    exp = expiry or next((str(row["expiry"]) for row in contracts if str(row["expiry"]) >= as_of), None)
    if not exp:
        raise ValueError("No expiry selected or listed for this underlying.")
    lot = next((int(row["lot_size"]) for row in contracts if row["expiry"] == exp
                and (_number(row.get("lot_size")) or 0) > 0), None)
    valid, session_close, hint = _session(client, as_of, exp, instrument_key)
    if view == "latest" and market_context and market_context["active"] and as_of <= exp:
        valid, session_close, hint = True, None, None
    historical = view != "latest" and as_of != _now().date().isoformat()
    if as_of == _now().date().isoformat():
        session_close = None
    chain = nmp.ChainSnapshot(exp, float("nan"), lot or 1, [], _now(), source="upstox.empty")
    provider = {}
    if valid:
        try:
            provider = nmp.fetch_max_pain_insights(client, exp, as_of, bucket, instrument_key) or {}
        except Exception:
            provider = {}  # Independent chain/OI data can still be usable.
        if not nmp.dated_payload_matches(provider, exp, as_of, instrument_key, session_close):
            provider = {}
    if valid and not historical:
        try:
            chain = nmp.fetch_chain(client, expiry=exp, lot_size=lot or 1, key=instrument_key)
            chain.fetched_at = _now()
        except Exception:
            pass  # Attempt the independently dated OI endpoint below.
    # The option-chain endpoint has no date parameter. Never use it for past dates.
    if valid and (historical or not chain.rows):
        try:
            oi = client.get_oi_data(instrument_key, expiry=exp, date=as_of) or {}
        except Exception:
            oi = {}
        if not nmp.dated_payload_matches(oi, exp, as_of, instrument_key, session_close):
            oi = {}
        # Missing strike-side OI must not be silently converted into zero.
        if any(not isinstance(row, dict) or any(_number(row.get(field)) is None or _number(row.get(field)) < 0
               for field in ("strike_price", "call_oi", "put_oi"))
               or _number(row.get("strike_price")) == 0
               for row in oi.get("call_put_oi_data_list") or []):
            oi = {}
        rows, oi_spot = nmp.oi_payload_to_rows(oi)
        if rows:
            chain.rows = rows
            chain.spot = float(oi_spot) if oi_spot is not None else float("nan")
            chain.source = "upstox.oi_snapshot"

    pain = nmp.compute_max_pain(chain.strikes, chain.call_oi, chain.put_oi, lot or 1, oi_in_units=True)
    provider_mp = _number(provider.get("max_pain"))
    provider_spot = _number(provider.get("spot_closing_price"))
    insights = _series(provider, as_of)
    has_data = bool(chain.rows) or bool(insights) or provider_mp is not None

    call_sum = float(sum(r.call_oi for r in chain.rows)) if chain.rows else None
    put_sum = float(sum(r.put_oi for r in chain.rows)) if chain.rows else None
    pcr = nmp.compute_pcr([r.call_oi for r in chain.rows], [r.put_oi for r in chain.rows])
    spot = _number(chain.spot) if chain.rows else provider_spot
    if spot is None and has_data:
        spot = provider_spot
    mp = _number(pain.strike) if chain.rows else provider_mp

    # Upstox OI already counts underlying units. A lot multiplier is unnecessary,
    # including for retained observations whose contract master is unavailable.
    payout_available = bool(chain.rows) and any(r.call_oi > 0 or r.put_oi > 0 for r in chain.rows)
    strikes = [float(x) for x in pain.candidates] if payout_available else []
    call_pay = [float(x) for x in pain.call_payout] if payout_available else []
    put_pay = [float(x) for x in pain.put_payout] if payout_available else []
    total_pay = [float(x) for x in pain.total_payout] if payout_available else []
    premium_prices = None
    priced_legs = {}
    if historical and payout_available:
        premium_prices = historical_premiums(client, instrument_key, exp, as_of, chain.rows)
        priced_legs = {(value["strike"], value["side"]): value for value in premium_prices.pop("prices", [])}
    live_legs = [(oi, price) for row in chain.rows for oi, price in
                 ((row.call_oi, row.call_ltp), (row.put_oi, row.put_ltp)) if oi > 0]
    live_available = sum(math.isfinite(price) and price > 0 for _, price in live_legs)
    has_premiums = (bool(premium_prices and premium_prices["complete"]) if historical else
                    chain.source == "upstox.option_chain" and bool(live_legs) and live_available == len(live_legs))
    premium_hint = None if has_premiums else (
        f"Historical premiums available for {premium_prices['available']}/{premium_prices['required']} OI-bearing option legs on or before {as_of}; P&L requires complete coverage."
        if premium_prices else
        f"Snapshot premiums available for {live_available}/{len(live_legs)} OI-bearing option legs; P&L requires complete coverage."
        if not historical and live_legs else
        f"Option premiums are unavailable for {as_of}; hypothetical P&L cannot be calculated."
    )

    # --- Premium-adjusted hypothetical short-option P&L ---
    premium_block: Optional[dict[str, Any]] = None
    if payout_available and has_premiums:
        try:
            scenarios = nmp.premium_pnl_scenarios(
                [r.strike for r in chain.rows],
                [r.call_oi for r in chain.rows],
                [r.put_oi for r in chain.rows],
                [r.call_ltp for r in chain.rows],
                [r.put_ltp for r in chain.rows],
                lot_size=lot or 1,
                oi_in_units=True,
                spot=spot,
                max_pain=mp,
                candidates=strikes or [r.strike for r in chain.rows],
            )
            premium_block = {
                "assumption": (
                    ((f"Hypothetical short-option portfolio; entry premium = latest traded option daily close on or before {as_of}; "
                      f"{premium_prices['carried_forward']} prices carried forward with original trade dates. "
                      if premium_prices and premium_prices.get("carried_forward") else
                      f"Hypothetical short-option portfolio; entry premium = {as_of} option daily candle close. ")
                     if historical else "Hypothetical short-option portfolio; entry premium = snapshot LTP. ") +
                    "Not actual market-wide P&L. OI does not identify sellers."
                ),
                "price_basis": premium_prices,
                "identity": "PnL(S) = PremiumValue - total_intrinsic_payout(S)",
                "min_pnl_is_max_payout": True,
                "scenarios": {
                    name: {
                        **res.summary(),
                        "candidates": [float(x) for x in res.candidates],
                        "call_pnl": [float(x) for x in res.call_pnl],
                        "put_pnl": [float(x) for x in res.put_pnl],
                        "combined_pnl": [float(x) for x in res.combined_pnl],
                        "buyer_call_pnl": [float(x) for x in res.buyer_call_pnl],
                        "buyer_put_pnl": [float(x) for x in res.buyer_put_pnl],
                        "buyer_combined_pnl": [float(x) for x in res.buyer_combined_pnl],
                    }
                    for name, res in scenarios.items()
                },
            }
        except Exception as exc:  # noqa: BLE001
            premium_block = {"error": str(exc), "scenarios": {}}

    greeks = greek_snapshot(client, instrument_key, exp, as_of, valid_session=valid,
                           checked_at=_now(), session_hint=hint, latest=view == "latest", market_context=market_context)
    pcr_observation = None
    if pcr is not None and chain.rows and market_context and market_context.get("active"):
        saved = client.get_current_option_chain_snapshot(instrument_key, exp)
        if isinstance(saved, dict) and saved.get("transport") == "websocket" and saved.get("live_oi_legs") == len(chain.rows) * 2:
            try:
                source_at = datetime.fromisoformat(saved["oi_reported_at"])
                if source_at.tzinfo and source_at.astimezone(IST).date().isoformat() == as_of and 0 <= (_now() - source_at).total_seconds() <= 30:
                    pcr_observation = {"at": source_at.isoformat(), "pcr": pcr, "source": "websocket"}
            except (KeyError, ValueError, TypeError):
                pass

    return {
        "expiry": exp,
        "as_of": as_of,
        "view": view,
        "market_context": market_context,
        "instrument_key": instrument_key,
        "lot_size": lot,
        "oi_unit": "underlying_units",
        "spot": spot,
        "max_pain": mp,
        "min_payout": _number(pain.min_payout) if payout_available else None,
        "tied_strikes": pain.tied_strikes,
        "broadness_pts": pain.broadness_pts if pain.broadness_pts == pain.broadness_pts else None,
        "warnings": pain.warnings,
        "provider_max_pain": provider_mp,
        "provider_spot": provider_spot,
        "call_oi_total": call_sum,
        "put_oi_total": put_sum,
        "pcr": pcr,
        "pcr_observation": pcr_observation,
        "spot_minus_max_pain": (spot - mp) if (spot is not None and mp is not None) else None,
        "data_available": has_data,
        "hint": None if has_data else hint or f"No verified data for {as_of} (IST), expiry {exp}.",
        "availability": {
            "payout": None if payout_available else ("No positive OI; payout curve unavailable." if chain.rows else f"No dated OI for {as_of}; payout unavailable."),
            "oi": None if chain.rows else f"No dated OI for {as_of}, expiry {exp}.",
            "oi_change": None if chain.source == "upstox.option_chain" and any(
                r.call_prev_oi is not None or r.put_prev_oi is not None for r in chain.rows
            ) else "Previous-session OI is not included in this snapshot; OI change is unavailable.",
            "premiums": premium_hint,
            "greeks": greeks["hint"],
        },
        "fallback": provider.get("_provenance") if provider.get("_provider") == "tapetide" else None,
        "requested_expiry": exp,
        "strikes": [
            {
                "strike": r.strike,
                "call_oi": r.call_oi,
                "put_oi": r.put_oi,
                "call_prev_oi": r.call_prev_oi if chain.source == "upstox.option_chain" else None,
                "put_prev_oi": r.put_prev_oi if chain.source == "upstox.option_chain" else None,
                "call_ltp": r.call_ltp if (r.strike, "CE") in priced_legs or not historical and math.isfinite(r.call_ltp) and r.call_ltp > 0 else None,
                "put_ltp": r.put_ltp if (r.strike, "PE") in priced_legs or not historical and math.isfinite(r.put_ltp) and r.put_ltp > 0 else None,
                "call_premium_date": priced_legs.get((r.strike, "CE"), {}).get("price_date"),
                "put_premium_date": priced_legs.get((r.strike, "PE"), {}).get("price_date"),
            }
            for r in chain.rows
        ],
        "payout_curve": {
            "candidates": strikes,
            "call_payout": call_pay,
            "put_payout": put_pay,
            "total_payout": total_pay,
        },
        "insights": insights,
        "fetched_at": chain.fetched_at.isoformat(timespec="seconds"),
        "source": chain.source if chain.rows else (("tapetide.max_pain" if provider.get("_provider") == "tapetide" else "upstox.max_pain") if has_data else "upstox.empty"),
        "premium_pnl": premium_block,
        "premium_prices": premium_prices,
        "option_greeks": greeks,
    }


def history(
    selected_expiry: Optional[str] = None,
    as_of: Optional[str] = None,
    history_days: int = 40,
    signal_time: str = nmp.SIGNAL_TIME,
    instrument_key: str = nmp.NIFTY_KEY,
) -> list[dict[str, Any]]:
    from datetime import date as date_cls

    as_of = as_of or _now().date().isoformat()
    if date_cls.fromisoformat(as_of) > _now().date():
        return []
    client = get_upstox()
    exps = [] if selected_expiry else nmp.list_expiries(client, instrument_key)
    exp = selected_expiry or next((str(row["expiry"]) for row in exps if str(row["expiry"]) >= as_of), None)
    if not exp:
        return []
    points = nmp.build_history(
        client,
        exps,
        selected_expiry=exp,
        as_of=as_of,
        history_days=history_days,
        signal_time=signal_time,
        key=instrument_key,
        include_other_expiries=False,
    )
    return [
        {
            "expiry": h.expiry,
            "obs_date": h.obs_date,
            "obs_time": h.obs_time,
            "max_pain": h.max_pain,
            "spot": h.spot,
            "expiry_close": h.expiry_close,
            "kind": h.kind,
            "error_pts": h.error_pts,
        }
        for h in points
        if h.obs_date < _now().date().isoformat() or h.obs_time[:5] <= _now().strftime("%H:%M")
    ]
