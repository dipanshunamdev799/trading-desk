"""Secondary provider adapters. Primary and secondary storage never share keys."""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from urllib.parse import quote

import requests

from tapetide_data import ENDPOINTS, TapetideAPIError, TapetideClient
from upstox_analytics import UpstoxAPIError
from .market_store import IST, market_day, now


INDEX_NAMES = {"NSE_INDEX|Nifty 50": "Nifty 50", "NSE_INDEX|Nifty Bank": "Nifty Bank",
               "NSE_INDEX|Nifty Fin Service": "Nifty Financial Services", "NSE_INDEX|NIFTY MID SELECT": "Nifty Midcap Select"}
OPTION_SYMBOLS = dict(zip(INDEX_NAMES, ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")))
NATIVE_FALLBACKS = {
    "get_company_profile": ("get_stock_profile", {}),
    "get_balance_sheet": ("get_financials", {"section": "balance_sheet"}),
    "get_cash_flow": ("get_financials", {"section": "cash_flow"}),
    "get_income_statement": ("get_financials", {"section": "profit_loss"}),
    "get_share_holdings": ("get_shareholding", {}),
    "get_key_ratios": ("get_financials", {"section": "ratios"}),
    "get_corporate_actions": ("get_stock_events", {"type": "corporate_actions"}),
    "get_competitors": ("get_stock_profile", {"include": "peers"}),
    "get_ipos": ("list_ipos", {}),
    "get_news": ("get_stock_events", {"type": "news"}),
    "get_option_chain": ("get_option_chain", {}),
    "get_oi_data": ("get_option_chain", {}),
}
COMPATIBLE = frozenset({"get_full_market_quotes_v2", "get_full_market_quotes_v3", "get_ltp_quotes_v2",
    "get_ltp_quotes_v3", "get_fii_data", "get_dii_data", "get_pcr", "get_max_pain"})


def upstream_unavailable(error: Exception) -> bool:
    """Database, programming and invalid-input errors must not trigger failover."""
    if isinstance(error, UpstoxAPIError):
        return error.status_code in (401, 402, 403, 404, 410, 429) or error.status_code >= 500
    return (isinstance(error, (requests.RequestException, NotImplementedError)) or
            isinstance(error, RuntimeError) and str(error).startswith("UPSTOX_ANALYTICS_TOKEN is required"))


def available(payload) -> bool:
    if payload is None:
        return False
    if isinstance(payload, dict):
        if payload.get("error") or payload.get("status") == "error":
            return False
        if "data" in payload:
            return available(payload["data"])
        if "candles" in payload:
            return bool(payload["candles"])
        return any(available(v) for k, v in payload.items() if not k.startswith("_") and k not in ("meta", "links"))
    if isinstance(payload, (list, tuple)):
        return bool(payload)
    return True  # Numeric zero is an observation, not missing data.


def finite(value) -> bool:
    try:
        return value is not None and not isinstance(value, bool) and math.isfinite(float(value))
    except (ValueError, TypeError):
        return False


def provider_of(payload) -> str:
    if isinstance(payload, dict):
        if payload.get("_provider"):
            return payload["_provider"]
        providers = {row.get("_provider", "upstox") for row in payload.values()
                     if isinstance(row, dict) and "last_price" in row}
        if providers:
            return next(iter(providers)) if len(providers) == 1 else "mixed"
    return "upstox"


class TapetideFallback:
    def __init__(self, client: TapetideClient, store):
        self.client, self.store = client, store

    def native(self, endpoint: str, **parameters) -> dict:
        """Preserve the complete provider schema and metadata for future datasets."""
        if endpoint not in ENDPOINTS:
            raise ValueError(f"Unknown read-only Tapetide dataset: {endpoint}")
        def load():
            self.store.count("tapetide_calls")
            payload = self.client.call(endpoint, **parameters)
            path = ENDPOINTS[endpoint]["path"]
            for parameter in ENDPOINTS[endpoint]["parameters"]:
                if parameter["in"] == "path":
                    path = path.replace("{" + parameter["name"] + "}", quote(str(parameters[parameter["name"]]), safe=""))
            return {**payload, "_provider": "tapetide", "_provenance": {
                "endpoint": endpoint, "source_url": self.client.BASE_URL + path,
                "fetched_at": now().isoformat(), "schema": "tapetide"}}
        return self.store.read("tapetide." + endpoint, {"schema_version": 1, **parameters}, load)

    def symbol(self, key: str) -> str:
        """Resolve only an exact ISIN; never guess an exchange token's identity."""
        if not key.startswith("NSE_EQ|") or not key.split("|", 1)[1].startswith("IN"):
            raise ValueError("Tapetide equity fallback requires an NSE equity ISIN")
        isin = key.split("|", 1)[1]
        found = self.native("search_stocks", q=isin, limit=2)["data"]
        if not isinstance(found, list) or len(found) != 1 or not found[0].get("nse_symbol"):
            raise ValueError("No unambiguous Tapetide identity for the requested ISIN")
        symbol = found[0]["nse_symbol"]
        profile = self.native("get_stock_profile", symbol=symbol)["data"]
        if profile.get("company", {}).get("isin") != isin:
            raise ValueError("Tapetide returned a different ISIN")
        return symbol

    def compatible(self, method: str, params: dict, primary=None):
        if method in ("get_full_market_quotes_v2", "get_full_market_quotes_v3", "get_ltp_quotes_v2", "get_ltp_quotes_v3"):
            return self.quotes(params["instrument_keys"], primary)
        if method in ("get_fii_data", "get_dii_data"):
            return self.flows(method, params)
        if method in ("get_max_pain", "get_pcr", "get_oi_data"):
            return self.options(method, params)
        return None

    @staticmethod
    def quote_entry(payload, key):
        if not isinstance(payload, dict):
            return None
        entry = payload.get(key) or payload.get(key.replace("|", ":"))
        if entry is None:
            entry = next((v for v in payload.values() if isinstance(v, dict) and
                (v.get("instrument_token") or v.get("instrument_key")) == key), None)
        return entry if isinstance(entry, dict) and finite(entry.get("last_price")) else None

    def quotes(self, keys, primary=None) -> dict:
        keys = keys.split(",") if isinstance(keys, str) else keys
        result = dict(primary or {})
        for key in keys:
            if self.quote_entry(primary, key):
                continue
            try:
                symbol = self.symbol(key)
                raw = self.native("get_stock_quote", symbol=symbol)
                row = raw["data"]
                stamp = datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
                if stamp.tzinfo is None or stamp > now() or not finite(row.get("price")) or row.get("found") is False:
                    continue
                for alias in (key, key.replace("|", ":")):
                    result.pop(alias, None)
                result[key.replace("|", ":")] = {"instrument_token": key, "symbol": symbol,
                    "last_price": row["price"], "prev_close_price": row.get("prev_close"),
                    "net_change": row.get("change"), "volume": row.get("volume"),
                    "ohlc": {f: row.get(f) for f in ("open", "high", "low")},
                    "timestamp": stamp.isoformat(), "_provider": "tapetide",
                    "_provenance": {**raw["_provenance"], "reported_at": stamp.isoformat(), "grain": "quote"}}
            except (TapetideAPIError, ValueError, KeyError, TypeError):
                continue
        return result

    def candles(self, key: str, unit: str, interval, first: str, last: str, primary=None):
        if unit != "days" or int(interval) != 1 or key.count("|") != 1:
            return None
        start, end = date.fromisoformat(first), min(date.fromisoformat(last), market_day() - timedelta(days=1))
        if end < start:
            return None  # Never fill a running session with a daily/EOD observation.
        source = {}
        bars = {}
        if key.startswith("NSE_INDEX|"):
            name = INDEX_NAMES.get(key, key.split("|", 1)[1])
            index = self.native("list_indices", limit=200)
            if index.get("meta", {}).get("has_more"):
                return None
            matches = [r for r in index["data"] if r.get("exchange") == "NSE" and r.get("name", "").casefold() == name.casefold()]
            if len(matches) != 1:
                return None
            rows = []
            cursor = None
            for _ in range(20):
                raw = self.native("list_index_levels", slug=matches[0]["slug"], **{
                    "from": start.isoformat(), "to": end.isoformat(), "order": "asc", "limit": 1000, "cursor": cursor})
                rows.extend(raw["data"])
                meta = raw.get("meta", {})
                if not meta.get("has_more"):
                    break
                next_cursor = meta.get("next_cursor")
                if not next_cursor or next_cursor == cursor:
                    raise ValueError("Tapetide index history cursor did not advance")
                cursor = next_cursor
            else:
                raise ValueError("Tapetide index history exceeds bounded pagination")
            for row in rows:
                if start.isoformat() <= row["date"] <= end.isoformat() and all(finite(row.get(f)) for f in ("open", "high", "low", "close")):
                    ts = row["date"] + "T00:00:00+05:30"
                    bars[ts] = [ts, *[row[f] for f in ("open", "high", "low", "close")], None, None]
                    source[ts] = raw["_provenance"]
        else:
            symbol = self.symbol(key)
            # Page by actual dates rather than accepting a silently capped lookback.
            cursor = end.isoformat()
            for _ in range(20):
                days = min(2000, (date.fromisoformat(cursor) - start).days + 1)
                raw = self.native("get_price_history", symbol=symbol, days=days, interval="daily", end_date=cursor)
                rows = raw["data"]
                if not isinstance(rows, list):
                    raise ValueError("Invalid Tapetide candle response")
                for row in rows:
                    if not start.isoformat() <= row["date"] <= end.isoformat():
                        continue
                    # Upstox uses raw prices. Back-adjusted bars must never be
                    # spliced into that series without a valid raw price scale.
                    if not all(finite(row.get(f)) for f in ("open", "high", "low", "close", "raw_close")) or row["close"] <= 0 or row["raw_close"] <= 0:
                        continue
                    scale = row["raw_close"] / row["close"]
                    ts = row["date"] + "T00:00:00+05:30"
                    bars[ts] = [ts, *[row[f] * scale for f in ("open", "high", "low")], row["raw_close"], row.get("volume"), None]
                    source[ts] = {**raw["_provenance"], "price_basis": "raw", "scale": scale}
                if days < 2000 or not rows:
                    break
                next_day = min(r["date"] for r in rows)
                next_cursor = (date.fromisoformat(next_day) - timedelta(days=1)).isoformat()
                if next_cursor >= cursor:
                    raise ValueError("Tapetide history cursor did not advance")
                cursor = next_cursor
            else:
                raise ValueError("Tapetide history exceeds bounded pagination")
        if not bars:
            return None
        # Retained primary observations always win, even when Upstox was partial.
        for row in (primary or {}).get("candles", []):
            bars[row[0]] = row
            source.pop(row[0], None)
        return {"candles": [bars[ts] for ts in sorted(bars)], "_provider": "mixed" if primary and primary.get("candles") else "tapetide",
            "_source": "mixed" if primary and primary.get("candles") else "tapetide", "_written": 0,
            "_partial": bool((primary or {}).get("_partial")), "_fallback_sources": source}

    def flows(self, method: str, params: dict):
        types = params.get("data_types", "NSE_EQ|CASH")
        if params.get("interval", "1D") != "1D" or types not in ("NSE_EQ|CASH", ["NSE_EQ|CASH"]):
            return None
        # Upstox's 'from' is a backward cursor, not a lower bound.
        end = params.get("from_date") or market_day().isoformat()
        start = (date.fromisoformat(end) - timedelta(days=45)).isoformat()
        raw = self.native("list_institutional_flows", **{"from": start, "to": end, "order": "desc", "limit": 100})
        if raw.get("meta", {}).get("has_more"):
            return None
        side = "fii" if method == "get_fii_data" else "dii"
        rows = []
        for row in raw["data"]:
            if not start <= row["date"] <= end:
                continue
            if not all(finite(row.get(side + "_" + f + "_cr")) for f in ("buy", "sell")):
                continue
            rows.append({"time_stamp": int(datetime.fromisoformat(row["date"]).replace(tzinfo=IST).timestamp()*1000),
                # Existing Upstox consumers expect amounts in INR (its documented
                # unit). Tapetide explicitly supplies crore: convert exactly once.
                "buy_amount": row[side + "_buy_cr"] * 10_000_000,
                "sell_amount": row[side + "_sell_cr"] * 10_000_000,
                "_provider": "tapetide", "_provenance": {**raw["_provenance"], "amount_unit": "INR", "reported_date": row["date"]}})
        return {"NSE_EQ|CASH": rows, "_provider": "tapetide", "_provenance": raw["_provenance"]} if rows else None

    def options(self, method: str, params: dict):
        key, expiry, day = params["instrument_key"], params.get("expiry"), params.get("date")
        if key not in OPTION_SYMBOLS or not day or not expiry:
            return None
        try:
            date.fromisoformat(expiry)
        except ValueError:
            return None  # A rolling expiry alias cannot establish contract identity.
        if day >= market_day().isoformat() or day > expiry or method == "get_oi_data":
            return None  # A truncated chain is not a complete OI ladder.
        raw = self.native("get_option_chain", symbol=OPTION_SYMBOLS[key], expiry=expiry, strikes=1)
        row = raw["data"]
        stamp = datetime.fromisoformat(row["snapshot_ts"].replace("+00", "+00:00") if row["snapshot_ts"].endswith("+00") else row["snapshot_ts"])
        if stamp.tzinfo is None or stamp > now() or stamp.astimezone(IST).date().isoformat() != day or row.get("expiry_date") != expiry:
            return None
        field = "max_pain_strike" if method == "get_max_pain" else "pcr"
        if not finite(row.get(field)):
            return None
        return {"max_pain" if method == "get_max_pain" else "pcr": row[field], "expiry_date": expiry,
            "date": day, "instrument_key": key, "spot_closing_price": row.get("spot"), "insights": [],
            "_provider": "tapetide", "_provenance": {**raw["_provenance"], "reported_at": stamp.isoformat(), "grain": "eod"}}

    def dataset(self, method: str, params: dict):
        """Fallback for provider-native fundamentals/IPO schemas, via get_dataset."""
        definition = NATIVE_FALLBACKS.get(method)
        if not definition:
            return None
        endpoint, query = definition[0], dict(definition[1])
        if method in ("get_option_chain", "get_oi_data"):
            key = params.get("instrument_key")
            expiry = params.get("expiry_date") or params.get("expiry")
            if key not in OPTION_SYMBOLS or not expiry:
                return None
            raw = self.native(endpoint, symbol=OPTION_SYMBOLS[key], expiry=expiry, strikes=25)
            data = raw["data"]
            if data.get("expiry_date") != expiry:
                return None
            if params.get("date") and str(data.get("snapshot_ts", ""))[:10] != params["date"]:
                return None
            return raw
        if method == "get_news":
            keys = params.get("instrument_keys")
            if params.get("category", "instrument_keys") != "instrument_keys" or not keys or params.get("page_number", 1) != 1:
                return None
            keys = keys.split(",") if isinstance(keys, str) else keys
            if len(keys) != 1:
                return None
            query.update(symbol=self.symbol(keys[0]), limit=min(50, params.get("page_size", 20)))
        elif method == "get_ipos":
            if params.get("issue_type") is not None or params.get("page_number", 1) != 1:
                return None
            query.update(status=params.get("status", "open"), limit=params.get("records", 30))
        else:
            isin = params.get("isin")
            if not isin:
                return None
            query["symbol"] = self.symbol("NSE_EQ|" + isin)
            if method == "get_income_statement" and params.get("time_period", "yearly") != "yearly":
                query["section"] = "quarterly"
            if params.get("statement_type", "consolidated") != "consolidated":
                return None  # Do not substitute a consolidated statement for standalone.
        return self.native(endpoint, **query)
