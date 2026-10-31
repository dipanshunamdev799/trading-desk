"""Bounded, independently failing data collectors for NIFTY research.

Upstox reads go through MarketGateway (memory -> PostgreSQL -> upstream).
Yahoo's public chart endpoint is unofficial and may be delayed or unavailable.
Its futures are explicitly identified as futures, never relabelled as spot.
No fetched time is substituted for a publisher/market timestamp.
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
from sqlalchemy import text

from .market_store import market_day, now, request_key

NIFTY_KEY = "NSE_INDEX|Nifty 50"
QUOTE_URL = "https://upstox.com/developer/api-documentation/get-full-market-quote-v3/"
CHAIN_URL = "https://upstox.com/developer/api-documentation/get-pc-option-chain/"
CONTRACT_URL = "https://upstox.com/developer/api-documentation/get-option-contracts/"
MEMBERS_URL = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
GLOBAL_URL = "https://assets.upstox.com/market-quote/instruments/exchange/global.json.gz"
INDEX_KEYS = {
    "nifty_spot": NIFTY_KEY, "india_vix": "NSE_INDEX|India VIX",
    "bank_nifty": "NSE_INDEX|Nifty Bank", "nifty_financial": "NSE_INDEX|Nifty Fin Service",
    "nifty_it": "NSE_INDEX|Nifty IT", "nifty_auto": "NSE_INDEX|Nifty Auto",
    "nifty_fmcg": "NSE_INDEX|Nifty FMCG", "nifty_pharma": "NSE_INDEX|Nifty Pharma",
    "nifty_metal": "NSE_INDEX|Nifty Metal", "nifty_energy": "NSE_INDEX|Nifty Energy",
    "nifty_realty": "NSE_INDEX|Nifty Realty", "nifty_psu_bank": "NSE_INDEX|Nifty PSU Bank",
}
# (symbol, units, exact instrument interpretation). ^TNX chart prices already
# quote yield percent (e.g. 4.988), not the exchange's ten-times index convention.
YAHOO_SYMBOLS = {
    "sp500": ("^GSPC", "points", "S&P 500 index"),
    "nasdaq": ("^IXIC", "points", "Nasdaq Composite index"),
    "dow": ("^DJI", "points", "Dow Jones Industrial Average index"),
    "us_futures": ("ES=F", "points", "S&P 500 E-mini futures continuous front contract"),
    "nikkei": ("^N225", "points", "Nikkei 225 index"),
    "hang_seng": ("^HSI", "points", "Hang Seng index"),
    "shanghai": ("000001.SS", "points", "Shanghai Composite index"),
    "europe": ("^STOXX50E", "points", "EURO STOXX 50 index; euro area market proxy"),
    "brent": ("BZ=F", "USD/barrel", "Brent crude futures continuous front contract"),
    "wti": ("CL=F", "USD/barrel", "WTI crude futures continuous front contract"),
    "gold": ("GC=F", "USD/troy oz", "COMEX gold futures continuous front contract"),
    "silver": ("SI=F", "USD/troy oz", "COMEX silver futures continuous front contract"),
    "usdinr": ("INR=X", "INR/USD", "USD/INR indicative exchange rate"),
    "dxy": ("DX-Y.NYB", "points", "US Dollar Index"),
    "natural_gas": ("NG=F", "USD/MMBtu", "Henry Hub natural gas futures continuous front contract"),
    "copper": ("HG=F", "USD/lb", "COMEX copper futures continuous front contract"),
    "us_10y": ("^TNX", "%", "Cboe 10-year Treasury yield; Yahoo chart values in percent, scale 1"),
}


def number(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def source_time(value) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        if isinstance(value, (int, float)) or str(value).replace(".", "", 1).isdigit():
            epoch = float(value)
            return datetime.fromtimestamp(epoch / 1000 if epoch > 100_000_000_000 else epoch,
                                          timezone.utc).isoformat()
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).isoformat() if parsed.tzinfo else None
    except (ValueError, OverflowError, OSError, TypeError):
        return None


def observation(factor_id, value, *, source, source_url, reported_at, observed_at, unit=None,
                previous_value=None, cadence="daily", context=None, basis=None):
    previous, current = number(previous_value), number(value)
    change = current - previous if current is not None and previous is not None else None
    return {"factor_id": factor_id, "value": value, "previous_value": previous,
            "change": change, "change_pct": change / abs(previous) * 100 if change is not None and previous else None,
            "unit": unit, "source": source, "source_url": source_url, "reported_at": reported_at,
            "observed_at": observed_at, "cadence": cadence, "context": context or {}, "basis": basis}


def public_get(url, *, params=None):
    # All callers use fixed public hosts, without credentials or user URLs.
    response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0 NiftyResearch/1.0"},
                            timeout=(3.05, 10), allow_redirects=False)
    response.raise_for_status()
    if response.is_redirect:
        raise ValueError("Provider redirected the fixed data endpoint")
    return response


def parse_quotes(payload: dict, factor_keys: dict[str, str], observed_at: str) -> list[dict]:
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    if not isinstance(payload, dict):
        raise ValueError("Full quote response is not an instrument map")
    keyed = {row.get("instrument_token") or row.get("instrument_key") or key: row
             for key, row in payload.items() if isinstance(row, dict)}
    result = []
    for factor, key in factor_keys.items():
        row = keyed.get(key) or payload.get(key.replace("|", ":")) or payload.get(key)
        if not isinstance(row, dict) or number(row.get("last_price")) is None:
            continue
        streamed = row.get("_transport") == "websocket"
        reported = (source_time(row.get("timestamp")) if streamed else
                    source_time(row.get("last_trade_time")) or source_time(row.get("timestamp")))
        if not reported:
            continue  # Never turn a cache retrieval time into a market timestamp.
        previous = number(row.get("prev_close_price"))
        if previous is None and number(row.get("net_change")) is not None:
            previous = float(row["last_price"]) - float(row["net_change"])
        secondary = row.get("_provider") == "tapetide"
        provenance = row.get("_provenance") or {}
        result.append(observation(factor, float(row["last_price"]), source="Tapetide" if secondary else "Upstox",
            source_url=provenance.get("source_url", QUOTE_URL),
            reported_at=reported, observed_at=observed_at, unit="points", previous_value=previous,
            cadence="intraday", context={"instrument_key": key, "ohlc": row.get("ohlc", {}), "transport": "websocket" if streamed else "rest",
                **({"fallback": True, "provenance": provenance} if secondary else {})},
            basis="Tapetide quote update timestamp" if secondary else "Exchange feed timestamp" if streamed else "Last trade timestamp when supplied; otherwise source quote timestamp"))
    return result


def parse_candles(payload) -> list[dict]:
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    if isinstance(payload, dict) and payload.get("_partial"):
        raise ValueError("Historical candle coverage is incomplete")
    rows = payload.get("candles", []) if isinstance(payload, dict) else payload
    result = {}
    for row in rows or []:
        if not isinstance(row, (list, tuple)) or len(row) < 5 or not source_time(row[0]):
            continue
        values = [number(item) for item in row[1:5]]
        if any(value is None for value in values):
            continue
        result[str(row[0])] = {"ts": str(row[0]), "open": values[0], "high": values[1],
            "low": values[2], "close": values[3], "volume": number(row[5]) if len(row) > 5 else None,
            "oi": number(row[6]) if len(row) > 6 else None}
    if not result:
        raise ValueError("No valid dated daily candles returned")
    return sorted(result.values(), key=lambda item: item["ts"])


def parse_flows(payload, factor_id: str, observed_at: str) -> list[dict]:
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    rows = payload.get("NSE_EQ|CASH") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Expected NSE_EQ|CASH flow records")
    valid = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        reported = source_time(row.get("time_stamp"))
        buy, sell = number(row.get("buy_amount")), number(row.get("sell_amount"))
        if reported and buy is not None and sell is not None:
            valid.append((reported, buy, sell, row))
    if not valid:
        raise ValueError("No valid dated institutional flow records")
    previous, result = None, []
    for reported, buy, sell, original in sorted(valid, key=lambda item: item[0]):
        # The live cash endpoint has returned daily NSE gross totals around
        # 10,000, while its schema labels those amounts INR. Such records cannot
        # establish the unit scale; do not silently reinterpret them as crore.
        secondary = original.get("_provider") == "tapetide"
        provenance = original.get("_provenance") or {}
        uncertain_units = not secondary and 0 < abs(buy) + abs(sell) < 10_000_000
        value = None if uncertain_units and buy != sell else (buy - sell) / 10_000_000
        row = observation(factor_id, value, previous_value=previous, unit="₹ crore", source="Tapetide" if secondary else "Upstox",
            source_url=provenance.get("source_url", f"https://upstox.com/developer/api-documentation/get-{'fii' if factor_id == 'fii_cash' else 'dii'}-data/"),
            reported_at=reported, observed_at=observed_at, context={"segment": "NSE_EQ|CASH",
                "raw_buy_amount": buy, "raw_sell_amount": sell, "raw_net_amount": buy - sell,
                "gross_buy_cr": None if uncertain_units else buy / 10_000_000,
                "gross_sell_cr": None if uncertain_units else sell / 10_000_000,
                "provider_amount_unit": "INR", "unit_status": "unverified" if uncertain_units else "documented",
                **({"fallback": True, "provenance": provenance} if secondary else {}),
                "unit_check": "Positive aggregate NSE institutional gross amounts below INR 1 crore require scale verification"},
            basis="Daily net cash flow; Tapetide crore amounts normalized to INR by the integration adapter" if secondary else
                "Daily net cash flow, buy minus sell; converted only when documented INR scale passes aggregate-size check")
        if uncertain_units:
            row["quality"] = "unverified_units"
            row["quality_note"] = ("Provider documents INR, but this daily NSE cash gross total is below INR 1 crore. "
                                   "Raw amounts are retained; nonzero converted flow is withheld until the source unit scale is verified.")
        result.append(row)
        previous = value
    return result


def parse_positioning(payload, factor_id: str, observed_at: str) -> list[dict]:
    """Documented FII participant totals; missing fields stay unknown."""
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    segment = "NSE_FO|INDEX_FUTURES" if factor_id == "fii_index_futures" else "NSE_FO|INDEX_OPTIONS"
    rows = payload.get(segment) if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f"Expected {segment} positioning records")
    fields = ("total_long_contracts", "total_short_contracts", "total_call_long_contracts",
              "total_put_long_contracts", "total_call_short_contracts", "total_put_short_contracts",
              "buy_contracts", "sell_contracts", "oi_contracts", "buy_amount", "sell_amount", "oi_amount")
    dated = [(source_time(row.get("time_stamp")), row) for row in rows if isinstance(row, dict)]
    previous, result = None, []
    for reported, row in sorted(((at, row) for at, row in dated if at), key=lambda item: item[0]):
        value = {key: number(row.get(key)) for key in fields}
        relevant = ("total_long_contracts", "total_short_contracts") if factor_id == "fii_index_futures" else fields[2:6]
        if all(value[key] is None for key in relevant):
            continue
        if factor_id == "fii_index_futures":
            long, short = value["total_long_contracts"], value["total_short_contracts"]
            value["net_contracts"] = long - short if long is not None and short is not None else None
        changes = {key: value[key] - previous[key] if previous and value[key] is not None and previous.get(key) is not None else None
                   for key in value}
        result.append(observation(factor_id, value, source="Upstox",
            source_url="https://upstox.com/developer/api-documentation/get-fii-data/",
            reported_at=reported, observed_at=observed_at, unit="contracts / INR", context={
                "segment": segment, "amount_unit": "INR", "previous_positioning": previous,
                "changes": changes, "note": "Participant open interest and traded activity describe positioning; they do not establish the next index move"},
            basis="Daily FII participant positions; amounts and contracts retain provider units"))
        previous = value
    if not result:
        raise ValueError("No valid dated FII positioning records")
    return result


def parse_yahoo(payload: dict, factor_id: str, observed_at: str) -> list[dict]:
    chart = payload.get("chart", {})
    if chart.get("error") or not chart.get("result"):
        raise ValueError("Yahoo chart has no successful result")
    result = chart["result"][0]
    meta = result.get("meta", {})
    symbol, unit, interpretation = YAHOO_SYMBOLS[factor_id]
    if meta.get("symbol", "").casefold() != symbol.casefold():
        raise ValueError("Yahoo returned a different instrument")
    timestamps = result.get("timestamp") or []
    quotes = (result.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    latest_time = source_time(meta.get("regularMarketTime"))
    if not latest_time:
        raise ValueError("Yahoo quote has no market timestamp")
    try:
        exchange_tz = ZoneInfo(meta.get("exchangeTimezoneName") or "UTC")
    except (KeyError, ValueError):
        exchange_tz = timezone.utc
    session = datetime.fromisoformat(latest_time).astimezone(exchange_tz).date()
    context = {"symbol": symbol, "quoted_instrument": interpretation, "currency": meta.get("currency"),
               "unofficial": True, "delayed": True, "exchange": meta.get("fullExchangeName"),
               "exchange_timezone": str(exchange_tz)}
    url = f"https://finance.yahoo.com/quote/{quote(symbol, safe='')}/"
    rows, previous = [], None
    # Exclude the still-forming last quote session from completed daily history.
    valid = sorted((int(at), number(value)) for at, value in zip(timestamps, quotes)
                   if number(at) is not None and number(value) is not None)
    for epoch, value in valid:
        day = datetime.fromtimestamp(epoch, timezone.utc).astimezone(exchange_tz).date()
        if day >= session:
            continue
        # Daily bar timestamps denote the session's start, not its close or a
        # publisher release instant; this basis is preserved in every observation.
        rows.append(observation(factor_id, value, previous_value=previous, source="Yahoo Finance (unofficial)",
            source_url=url, reported_at=source_time(epoch), observed_at=observed_at, unit=unit,
            context={**context, "session_date": day.isoformat()}, basis="Completed daily bar; source timestamp is session start"))
        previous = value
    rows = rows[-90:]
    latest = number(meta.get("regularMarketPrice"))
    if latest is not None:
        prior = number(meta.get("previousClose"))
        if prior is None:
            prior = previous  # chartPreviousClose is start-of-range, NOT previous session.
        rows.append(observation(factor_id, latest, previous_value=prior, source="Yahoo Finance (unofficial)",
            source_url=url, reported_at=latest_time, observed_at=observed_at, unit=unit, cadence="intraday",
            context=context, basis="Delayed indicative quote; regularMarketTime supplied by provider"))
    if not rows:
        raise ValueError("Yahoo chart contains no finite market values")
    return rows


def fetch_yahoo(factor_id: str, observed_at: str) -> list[dict]:
    symbol = YAHOO_SYMBOLS[factor_id][0]
    response = public_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}",
                          params={"range": "6mo", "interval": "1d"})
    return parse_yahoo(response.json(), factor_id, observed_at)


def parse_fred(text_value: str, observed_at: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text_value.lstrip("\ufeff")))
    if not reader.fieldnames or not {"observation_date", "DGS2"}.issubset(reader.fieldnames):
        raise ValueError("FRED DGS2 CSV schema is missing required columns")
    values = []
    for row in reader:
        try:
            day = date.fromisoformat(row["observation_date"])
        except ValueError:
            continue
        value = number(row["DGS2"])
        if value is not None and day <= now().date():
            values.append((day.isoformat(), value))
    if not values:
        raise ValueError("No dated FRED DGS2 observations returned")
    previous, result = None, []
    for day, value in sorted(values):
        result.append(observation("us_2y", value, previous_value=previous, unit="%",
            source="Federal Reserve H.15 via FRED", source_url="https://fred.stlouisfed.org/series/DGS2",
            reported_at=day, observed_at=observed_at, context={"series": "DGS2", "frequency": "daily",
                "change_unit": "percentage points", "release_timestamp_available": False},
            basis="Official daily observation date; publication time is not supplied by CSV"))
        previous = value
    return result[-90:]


def parse_members(text_value: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text_value.lstrip("\ufeff")))
    if not reader.fieldnames or not {"Company Name", "Symbol", "ISIN Code"}.issubset(reader.fieldnames):
        raise ValueError("NIFTY membership CSV schema is missing required columns")
    rows = [{"name": row["Company Name"].strip(), "symbol": row["Symbol"].strip(),
             "isin": row["ISIN Code"].strip(), "sector": row.get("Industry", "").strip(),
             "instrument_key": "NSE_EQ|" + row["ISIN Code"].strip()} for row in reader]
    if len(rows) != 50 or len({row["isin"] for row in rows}) != 50 or any(not row["isin"].startswith("IN") for row in rows):
        raise ValueError("Official NIFTY 50 membership is incomplete or duplicated")
    return rows


def _capture_time(client, method: str, parameters: dict) -> str | None:
    """Original gateway acquisition timestamp for APIs without market timestamps."""
    if not hasattr(client, "store"):
        return None
    parameters = {**parameters, "observed_on": market_day().isoformat()}
    with client.store.engine.connect() as conn:
        value = conn.execute(text("SELECT fetched_at FROM market_datasets WHERE request_key=:key"),
                             {"key": request_key(method, parameters)}).scalar()
        return value.isoformat() if isinstance(value, datetime) else None


def _safe_error(error: Exception) -> str:
    # No provider bodies/headers/URLs: they can contain credentials or HTML.
    if isinstance(error, requests.Timeout):
        return "Provider request timed out"
    if isinstance(error, requests.HTTPError):
        return f"Provider returned HTTP {error.response.status_code}" if error.response is not None else "Provider HTTP error"
    if isinstance(error, requests.RequestException):
        return "Provider connection failed"
    if isinstance(error, ValueError):
        return str(error)[:240]
    if hasattr(error, "status_code"):
        return f"Provider returned HTTP {error.status_code}"
    return f"Collection failed ({type(error).__name__})"


def collect_market_data(client=None, *, include_public: bool = True) -> dict:
    if client is None:
        from .upstox_service import get_upstox
        client = get_upstox()
    at = now().isoformat()
    payload = {"observations": [], "candles": [], "option_chain": [], "expiries": [],
               "source_errors": [], "events": [], "collected_at": at}

    def attempt(source, operation):
        try:
            return operation()
        except Exception as error:
            payload["source_errors"].append({"source": source, "error": _safe_error(error)})
            return None

    quotes = attempt("Upstox index quotes", lambda: parse_quotes(client.get_full_market_quotes_v3(list(INDEX_KEYS.values())), INDEX_KEYS, at))
    if quotes is not None:
        payload["observations"].extend(quotes)
        missing = sorted(set(INDEX_KEYS) - {row["factor_id"] for row in quotes})
        if missing:
            payload["source_errors"].append({"source": "Upstox index quotes", "error": "Missing valid dated quotes: " + ", ".join(missing)})
    yesterday = market_day() - timedelta(days=1)
    candle_payload = attempt("Upstox daily NIFTY candles", lambda: client.get_historical_candles_v3(
        NIFTY_KEY, "days", 1, yesterday.isoformat(), (yesterday - timedelta(days=450)).isoformat()))
    candles = attempt("Upstox daily NIFTY candles", lambda: parse_candles(candle_payload)) if candle_payload is not None else None
    if candles:
        payload["candles"] = [row for row in candles if str(row["ts"])[:10] <= yesterday.isoformat()]
        secondary = isinstance(candle_payload, dict) and candle_payload.get("_provider") in ("tapetide", "mixed")
        payload["candles_meta"] = {"source": candle_payload["_provider"].title() if secondary else "Upstox",
            "source_url": "https://developers.tapetide.com/api/operations/listindexlevels/" if secondary else "https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/",
            **({"fallback_sources": candle_payload.get("_fallback_sources", {})} if secondary else {}),
            "reported_at": payload["candles"][-1]["ts"] if payload["candles"] else None, "observed_at": at,
            "basis": "Completed daily bars; source timestamps are session starts"}
        if len(payload["candles"]) < 200:
            payload["source_errors"].append({"source": "Upstox daily NIFTY candles", "error": "Fewer than 200 completed bars; long-period indicators need more history"})
    contracts = attempt("Upstox NIFTY contracts", lambda: client.get_option_contracts(NIFTY_KEY))
    if isinstance(contracts, list):
        expiries = {}
        for row in contracts:
            if not isinstance(row, dict):
                continue
            expiry = str(row.get("expiry", ""))[:10]
            try:
                day = date.fromisoformat(expiry)
            except ValueError:
                continue
            if day < market_day():
                continue
            current = expiries.setdefault(expiry, {"expiry": expiry, "weekly": row.get("weekly"), "lot_sizes": [],
                "source": "Upstox", "source_url": CONTRACT_URL})
            if row.get("lot_size") is not None and row["lot_size"] not in current["lot_sizes"]:
                current["lot_sizes"].append(row["lot_size"])
        payload["expiries"] = [expiries[key] for key in sorted(expiries)]
        if payload["expiries"]:
            expiry = payload["expiries"][0]["expiry"]
            chain = attempt("Upstox NIFTY option chain", lambda: client.get_option_chain(NIFTY_KEY, expiry))
            if isinstance(chain, list) and chain:
                validated = [row for row in chain if isinstance(row, dict) and row.get("expiry") == expiry and row.get("underlying_key", NIFTY_KEY) == NIFTY_KEY]
                if len(validated) == len(chain):
                    payload["option_chain"] = validated
                    captured = attempt("Upstox option chain provenance", lambda: _capture_time(client, "get_option_chain", {"instrument_key": NIFTY_KEY, "expiry_date": expiry}))
                    payload["option_chain_meta"] = {"source": "Upstox", "source_url": CHAIN_URL, "reported_at": None,
                        "observed_at": captured, "expiry": expiry, "basis": "API omits source market timestamp; original gateway acquisition time only"}
                    if getattr(client, "live", None):
                        current = client.get_current_option_chain_snapshot(NIFTY_KEY, expiry)
                        if current and current.get("transport") == "websocket":
                            payload["option_chain_meta"].update({key: value for key, value in current.items() if key != "payload"})
                else:
                    payload["source_errors"].append({"source": "Upstox NIFTY option chain", "error": "Expiry or underlying mismatch"})
            elif chain is not None:
                payload["source_errors"].append({"source": "Upstox NIFTY option chain", "error": "No option chain rows returned for actual contract expiry"})
        else:
            payload["source_errors"].append({"source": "Upstox NIFTY contracts", "error": "No active dated NIFTY contracts returned"})
    elif contracts is not None:
        payload["source_errors"].append({"source": "Upstox NIFTY contracts", "error": "Option contracts response is not a list"})
    fii = attempt("Upstox FII activity", lambda: client.get_fii_data(
        data_types=["NSE_EQ|CASH", "NSE_FO|INDEX_FUTURES", "NSE_FO|INDEX_OPTIONS"], interval="1D"))
    if fii is not None:
        for factor, parser in (("fii_cash", parse_flows), ("fii_index_futures", parse_positioning), ("fii_index_options", parse_positioning)):
            rows = attempt(f"Upstox {factor}", lambda factor=factor, parser=parser: parser(fii, factor, at))
            if rows:
                payload["observations"].extend(rows)
    for factor, method in (("dii_cash", "get_dii_data"),):
        rows = attempt(f"Upstox {factor}", lambda factor=factor, method=method: parse_flows(getattr(client, method)(interval="1D"), factor, at))
        if rows:
            payload["observations"].extend(rows)
    if include_public:
        from .nifty_cash_flows import corroborate_upstox, fetch_nse_cash
        official_cash = attempt("NSE FII/DII cash report", lambda: fetch_nse_cash(client))
        if official_cash:
            payload["observations"].extend(corroborate_upstox(official_cash, payload["observations"]))
        # Public collectors have no token, retries or shared requests session.
        # Bounded parallelism keeps one failed host from serializing the batch.
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(fetch_yahoo, factor, at): factor for factor in YAHOO_SYMBOLS}
            for future in as_completed(futures):
                factor = futures[future]
                rows = attempt(f"Yahoo {factor}", future.result)
                if rows:
                    payload["observations"].extend(rows)
        fred = attempt("FRED US 2-year yield", lambda: parse_fred(public_get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv",
            params={"id": "DGS2", "cosd": (market_day() - timedelta(days=190)).isoformat()}).text, at))
        if fred:
            payload["observations"].extend(fred)
        members = attempt("NSE NIFTY membership", lambda: parse_members(public_get(MEMBERS_URL).text))
        if members:
            payload["constituents"] = {"members": members, "source": "NSE Indices", "source_url": MEMBERS_URL,
                "observed_at": now().isoformat(), "reported_at": None, "basis": "Current membership file; effective/publication date and weights not supplied"}
            member_keys = {member["symbol"]: member["instrument_key"] for member in members}
            member_quotes = attempt("Upstox constituent quotes", lambda: parse_quotes(
                client.get_full_market_quotes_v3(list(member_keys.values())), member_keys, at))
            if member_quotes:
                payload["constituents"]["quotes"] = member_quotes
                dated_changes = [row for row in member_quotes if row.get("change") is not None]
                sessions = {datetime.fromisoformat(row["reported_at"]).astimezone(ZoneInfo("Asia/Kolkata")).date()
                            for row in dated_changes}
                available = len(dated_changes)
                advances = sum(row["change"] > 0 for row in dated_changes)
                declines = sum(row["change"] < 0 for row in dated_changes)
                complete = available == 50 and len(sessions) == 1
                payload["observations"].append(observation("advance_decline", {
                    "ratio": advances / declines if complete and declines else None, "advances": advances,
                    "declines": declines, "unchanged": available - advances - declines,
                    "available_constituents": available, "universe_size": 50},
                    source="NSE membership + " + "/".join(sorted({row["source"] for row in member_quotes})),
                    source_url=QUOTE_URL, reported_at=min(row["reported_at"] for row in member_quotes),
                    observed_at=at, cadence="intraday", context={"membership_url": MEMBERS_URL,
                        "complete": complete, "note": "Ratio requires all 50 dated quotes from one source date; zero decliners is undefined"},
                    basis="Advance/decline counts against previous close for current official membership"))
        def gift():
            response = public_get(GLOBAL_URL)
            master = json.loads(gzip.decompress(response.content))
            matches = [row for row in master if row.get("name", "").upper() == "GIFT NIFTY" and row.get("instrument_key")]
            if len(matches) != 1:
                raise ValueError("GIFT NIFTY identity missing or ambiguous in official global master")
            key = matches[0]["instrument_key"]
            rows = parse_quotes(client.get_full_market_quotes_v3([key]), {"gift_nifty": key}, at)
            if not rows:
                raise ValueError("GIFT NIFTY quote has no valid source timestamp")
            for row in rows:
                row["context"].update({"latency": matches[0].get("latency"), "instrument_master_url": GLOBAL_URL})
            return rows
        rows = attempt("Upstox GIFT NIFTY", gift)
        if rows:
            payload["observations"].extend(rows)
    return payload
