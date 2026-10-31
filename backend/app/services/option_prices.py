"""Retrieve dated option close prices through the persistent market gateway."""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from .market_store import IST, market_day


def latest_traded_close(candles: list, first: str, last: str) -> dict | None:
    """Select a dated daily close, rejecting future/invalid/non-traded bars."""
    prices = []
    for candle in candles:
        if not isinstance(candle, (list, tuple)) or len(candle) < 5:
            continue
        try:
            timestamp = datetime.fromisoformat(str(candle[0]).replace("Z", "+00:00"))
            timestamp = timestamp.replace(tzinfo=IST) if timestamp.tzinfo is None else timestamp
            day = timestamp.astimezone(IST).date().isoformat()
            close = float(candle[4])
            volume = candle[5] if len(candle) > 5 else None
            if (first <= day <= last and math.isfinite(close) and close >= 0
                    and (volume is None or float(volume) > 0)):
                prices.append({"close": close, "price_date": day})
        except (TypeError, ValueError, OverflowError):
            continue
    return max(prices, key=lambda value: value["price_date"]) if prices else None


def historical_premiums(client: Any, underlying: str, expiry: str, day: str, rows: list) -> dict:
    contract_error = None
    try:
        contracts = client.get_option_contracts(underlying, expiry_date=expiry) or []
    except Exception as exc:
        contracts = []
        contract_error = f"contract metadata unavailable ({type(exc).__name__})"
    mapping = {}
    for contract in contracts:
        if str(contract.get("expiry") or contract.get("expiry_date")) != expiry:
            continue
        try:
            strike = float(contract["strike_price"])
        except (KeyError, TypeError, ValueError):
            continue
        mapping[(strike, contract.get("instrument_type") or contract.get("option_type"))] = contract

    requested = [(row, side) for row in rows for side in ("CE", "PE")
                 if (row.call_oi if side == "CE" else row.put_oi) > 0]

    def fetch(item):
        row, side = item
        contract = mapping.get((row.strike, side))
        if not contract:
            return row.strike, side, None, contract_error or "contract unavailable"
        key = contract.get("expired_instrument_key") or contract.get("instrument_key")
        if expiry < market_day().isoformat() and str(key).count("|") == 1:
            key = f"{key}|{date.fromisoformat(expiry).strftime('%d-%m-%Y')}"
        try:
            # Expired keys include their expiry suffix. Regular live keys use V3.
            if contract.get("expired_instrument_key") or str(key).count("|") > 1:
                raw = client.get_expired_historical_candles(key, "day", day, day)
            else:
                raw = client.get_historical_candles_v3(key, "days", 1, day, day)
            candles = raw.get("candles", []) if isinstance(raw, dict) else raw or []
            price = latest_traded_close(candles, day, day)
            if not price:
                price = client.get_previous_option_close(key, day)
            # Independently enforce the cutoff even if a provider/cache is wrong.
            if (not price or not math.isfinite(float(price["close"])) or float(price["close"]) < 0
                    or not day >= price["price_date"] >= (date.fromisoformat(day) - timedelta(days=365)).isoformat()):
                return row.strike, side, None, "traded close unavailable within 365 days on or before as-of"
            return row.strike, side, price, None
        except Exception as exc:
            # Every successful contract fetch remains committed even if another
            # contract is missing, rate-limited or outside upstream retention.
            return row.strike, side, None, type(exc).__name__

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="option-closes") as workers:
        results = list(workers.map(fetch, requested))
    prices = {(strike, side): value for strike, side, value, error in results if value is not None}
    missing = [{"strike": strike, "side": side, "reason": error} for strike, side, value, error in results if value is None]
    for row in rows:
        row.call_ltp = prices.get((row.strike, "CE"), {}).get("close", 0.0)
        row.put_ltp = prices.get((row.strike, "PE"), {}).get("close", 0.0)
    details = [{"strike": strike, "side": side, **price,
                "age_days": (date.fromisoformat(day) - date.fromisoformat(price["price_date"])).days,
                "carried_forward": price["price_date"] != day} for (strike, side), price in prices.items()]
    carried = [price for price in details if price["carried_forward"]]
    return {"basis": "last_available_close" if carried else "session_close", "date": day,
            "source": "stored_option_daily_candles", "exact": len(prices) - len(carried),
            "carried_forward": len(carried), "carried": carried,
            "required": len(requested), "available": len(prices), "missing": missing,
            "prices": details,
            "complete": bool(requested) and not missing}
