"""Verified institutional cash flows from NSE's own report and column schema.

NSE's combined NSE/BSE/MSEI table explicitly labels amounts in rupees crore.
Upstox is corroborating evidence only: its contradictory INR documentation must
not determine the conversion or silently establish units for unmatched history.
"""
from __future__ import annotations

import re
from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import requests

NSE_REPORT_URL = "https://www.nseindia.com/reports/fii-dii"
NSE_CASH_URL = "https://www.nseindia.com/api/fiidiiTradeReact"
NSE_COLUMNS_URL = "https://www.nseindia.com/json/reports/fii-dii.json"
SOURCE = "NSE provisional cash report"
IST = ZoneInfo("Asia/Kolkata")
MONTHS = {name: index for index, name in enumerate(
    ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}


def _money(value) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError("NSE cash amount is missing")
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except InvalidOperation as exc:
        raise ValueError("NSE cash amount is invalid") from exc
    if not result.is_finite():
        raise ValueError("NSE cash amount must be finite")
    return result


def _session(value: str) -> date:
    match = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})", str(value).strip())
    if not match or match[2].title() not in MONTHS:
        raise ValueError("NSE cash reporting date has an unexpected format")
    return date(int(match[3]), MONTHS[match[2].title()], int(match[1]))


def validate_crore_columns(schema: dict) -> None:
    columns = {row.get("name"): row for row in schema.get("columns", []) if isinstance(row, dict)}
    for field in ("buyValue", "sellValue", "netValue"):
        column = columns.get(field, {})
        label = " ".join(str(column.get(key, "")) for key in ("heading", "subHead"))
        if not re.search(r"\bcrores?\b", label, re.I) or not re.search(r"₹|\bINR\b|\bRs\.?", label, re.I):
            raise ValueError("NSE cash columns do not explicitly identify rupees crore")


def parse_nse_cash(payload: list, schema: dict, observed_at: str, *, today: date | None = None) -> list[dict]:
    validate_crore_columns(schema)
    if not isinstance(payload, list):
        raise ValueError("NSE cash report must be a list")
    today = today or datetime.now(IST).date()
    result, seen, sessions = [], set(), set()
    categories = {"DII": "dii_cash", "FII/FPI": "fii_cash"}
    for raw in payload:
        if not isinstance(raw, dict):
            raise ValueError("NSE cash report contains an invalid row")
        factor_id = categories.get(str(raw.get("category", "")).strip().upper())
        if factor_id is None:
            raise ValueError("NSE cash report has an unknown investor category")
        day = _session(raw.get("date"))
        if day > today:
            raise ValueError("NSE cash report is dated in the future")
        if factor_id in seen:
            raise ValueError("NSE cash report contains duplicate investor categories")
        seen.add(factor_id)
        sessions.add(day)
        buy, sell, net = (_money(raw.get(key)) for key in ("buyValue", "sellValue", "netValue"))
        if buy < 0 or sell < 0 or abs(buy - sell - net) > Decimal("0.01"):
            raise ValueError("NSE cash buy, sell and net amounts do not reconcile")
        result.append({"factor_id": factor_id, "value": float(net), "previous_value": None,
            "change": None, "change_pct": None, "unit": "₹ crore", "source": SOURCE,
            "source_url": NSE_REPORT_URL, "reported_at": datetime.combine(day, time(), IST).isoformat(),
            "observed_at": observed_at, "reporting_date": day.isoformat(), "cadence": "daily after close",
            "quality": "exchange_report", "context": {"session_date": day.isoformat(),
                "gross_buy_cr": float(buy), "gross_sell_cr": float(sell), "net_cr": float(net),
                "provisional": True, "unit_status": "verified", "unit_source_url": NSE_COLUMNS_URL,
                "data_source_url": NSE_CASH_URL, "market_scope": "NSE, BSE and MSEI capital market segment",
                "timestamp_basis": "Reporting date only; the exchange does not supply a release clock time"},
            "basis": "NSE provisional report; buy minus sell in explicitly labelled rupees crore. Timestamp is a reporting-date anchor, not publication time."})
    if seen != {"fii_cash", "dii_cash"} or len(sessions) != 1:
        raise ValueError("NSE cash report must contain both categories for the same session")
    return result


def fetch_nse_cash(client=None) -> list[dict]:
    def load():
        with requests.Session() as session:
            session.headers.update({"User-Agent": "Mozilla/5.0 NiftyResearch/1.0",
                "Accept": "application/json,text/plain,*/*", "Referer": NSE_REPORT_URL})
            def read(url):
                response = session.get(url, timeout=(4, 12), allow_redirects=False)
                response.raise_for_status()
                if response.is_redirect:
                    raise ValueError("NSE cash source redirected its fixed endpoint")
                return response
            read(NSE_REPORT_URL)  # Establish the public report session normally.
            schema, payload = read(NSE_COLUMNS_URL).json(), read(NSE_CASH_URL).json()
        at = datetime.now(timezone.utc).isoformat()
        return {"observations": parse_nse_cash(payload, schema, at)}
    if client is not None and getattr(client, "store", None) is not None:
        result = client.store.read("get_nifty_nse_cash", {"source_url": NSE_CASH_URL, "schema_version": 1}, load)
    else:
        result = load()
    return result["observations"]


def corroborate_upstox(official: list[dict], provider: list[dict]) -> list[dict]:
    """Compare BOTH gross legs on the SAME reporting date, without a scale guess."""
    for row in official:
        context = row["context"]
        context["upstox_verification"] = {"matched": False, "note": "No matching provider snapshot for this report date"}
        candidates = []
        for other in provider:
            if other.get("factor_id") != row["factor_id"] or other.get("source") != "Upstox":
                continue
            try:
                stamp = datetime.fromisoformat(str(other.get("reported_at")).replace("Z", "+00:00"))
                if stamp.astimezone(IST).date().isoformat() == row["reporting_date"]:
                    candidates.append(other)
            except (ValueError, TypeError):
                continue
        if not candidates:
            continue
        other = max(candidates, key=lambda item: str(item.get("observed_at", "")))
        raw = other.get("context") or {}
        try:
            buy, sell = _money(raw.get("raw_buy_amount")), _money(raw.get("raw_sell_amount"))
            official_buy, official_sell = _money(context["gross_buy_cr"]), _money(context["gross_sell_cr"])
            matches = [scale for scale in (Decimal(1), Decimal(10_000_000))
                       if abs(buy / scale - official_buy) <= Decimal("0.01")
                       and abs(sell / scale - official_sell) <= Decimal("0.01")]
        except ValueError:
            matches = []
        context["upstox_verification"] = {"matched": len(matches) == 1,
            "reported_at": other.get("reported_at"), "source_url": other.get("source_url"),
            "provider_documented_unit": raw.get("provider_amount_unit"),
            "verified_raw_unit": "₹ crore" if matches == [Decimal(1)] else "INR" if matches == [Decimal(10_000_000)] else None,
            "note": "Both gross legs match NSE for the same reporting date" if len(matches) == 1 else "Provider legs differ; authoritative NSE figures retained"}
    return official
