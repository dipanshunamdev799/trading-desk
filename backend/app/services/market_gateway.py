"""The only application-facing Upstox client: cache, durable store, then API."""
from __future__ import annotations

import inspect
import threading
import time
from datetime import date, datetime, timedelta
from typing import Any

from .market_store import IST, MarketStore, market_day, now, request_key


class MarketGateway:
    def __init__(self, remote: Any, store: MarketStore, requests_per_second: float = 5, *, fallback=None):
        self.remote, self.store = remote, store
        self.fallback = fallback
        self.rate_lock = threading.Lock()
        self.next_request = 0.0
        self.request_spacing = 1.0 / max(0.1, requests_per_second)
        self.live = None

    def _remote_call(self, method: str, *args, **kwargs):
        # Bounded historical option fan-out must not overwhelm the provider.
        with self.rate_lock:
            delay = self.next_request - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            self.next_request = time.monotonic() + self.request_spacing
        self.store.count("upstream_calls")
        return getattr(self.remote, method)(*args, **kwargs)

    def __getattr__(self, name: str):
        remote_method = getattr(self.remote, name)
        if not callable(remote_method) or not name.startswith(("get_", "search_")):
            raise AttributeError(f"Market gateway does not expose {name}")

        def cached(*args, **kwargs):
            return self._cached_rest(name, *args, **kwargs)
        return cached

    def _cached_rest(self, name, *args, **kwargs):
        bound = inspect.signature(getattr(self.remote, name)).bind(*args, **kwargs)
        bound.apply_defaults()
        parameters = dict(bound.arguments)
        if not parameters.get("date"):
            parameters["observed_on"] = market_day().isoformat()
        error = None
        try:
            result = self.store.read(name, parameters, lambda: self._remote_call(name, *args, **kwargs))
        except Exception as exc:
            from .data_providers import upstream_unavailable
            if not upstream_unavailable(exc):
                raise
            result, error = None, exc
        return self._with_fallback(name, dict(bound.arguments), result, error)

    def _with_fallback(self, name, parameters, primary, error=None):
        from .data_providers import COMPATIBLE, TapetideAPIError, available, provider_of
        if self.fallback and name in COMPATIBLE:
            quotes = "quotes" in name
            if quotes or not available(primary):
                params = dict(parameters)
                if name in ("get_max_pain", "get_pcr"):
                    params["date"] = params.get("date") or market_day().isoformat()
                try:
                    secondary = self.fallback.compatible(name, params, primary)
                except (TapetideAPIError, ValueError, KeyError, TypeError):
                    secondary = None
                if available(secondary):
                    if provider_of(secondary) in ("tapetide", "mixed"):
                        self.store.count("tapetide_fallback_hits")
                    return secondary
        if error:
            raise error
        return primary

    def get_data_catalog(self):
        from tapetide_data import ENDPOINTS
        from .data_providers import COMPATIBLE, NATIVE_FALLBACKS
        return {"primary": "upstox", "fallback": "tapetide", "fallback_configured": bool(self.fallback),
            "automatic_fallback": sorted(COMPATIBLE - {"get_oi_data"}) + ["get_historical_candles_v3 (daily NSE equity/index)"],
            "native_fallback": {name: target[0] for name, target in NATIVE_FALLBACKS.items()},
            "tapetide_datasets": {name: {"path": entry["path"], "summary": entry["summary"],
                "parameters": entry["parameters"]} for name, entry in ENDPOINTS.items()}}

    def get_dataset(self, name: str, **parameters):
        """Provider-native schemas in an explicit envelope; Upstox always first.

        Use Upstox method names for shared datasets, e.g. get_balance_sheet.
        Additional Tapetide-only endpoint names come from get_data_catalog().
        """
        from tapetide_data import ENDPOINTS, TapetideAPIError
        from .data_providers import NATIVE_FALLBACKS, available, provider_of, upstream_unavailable
        if callable(getattr(self.remote, name, None)) and name.startswith(("get_", "search_")):
            error = None
            try:
                payload = getattr(self, name)(**parameters)
            except Exception as exc:
                if not upstream_unavailable(exc):
                    raise
                payload, error = None, exc
            if available(payload):
                provider = provider_of(payload)
                return {"provider": provider, "dataset": name, "data": payload}
            if self.fallback and name in NATIVE_FALLBACKS:
                try:
                    secondary = self.fallback.dataset(name, parameters)
                except (TapetideAPIError, ValueError, KeyError, TypeError):
                    secondary = None
                if available(secondary):
                    return {"provider": "tapetide", "dataset": name, "data": secondary,
                            "schema": "tapetide", "fallback": True}
            if error:
                raise error
            return {"provider": "upstox", "dataset": name, "data": payload}
        if name not in ENDPOINTS:
            raise ValueError(f"Unknown dataset: {name}")
        overlaps = {target[0]: primary for primary, target in NATIVE_FALLBACKS.items()}
        overlaps.update({"get_stock_quote": "get_full_market_quotes_v3", "get_batch_quotes": "get_full_market_quotes_v3",
                         "get_price_history": "get_historical_candles_v3", "get_index_history": "get_historical_candles_v3",
                         "get_fii_dii": "get_fii_data"})
        if name in overlaps:
            raise ValueError(f"Use {overlaps[name]} with Upstox parameters so the primary source is tried first")
        if not self.fallback:
            raise ValueError("Tapetide fallback is not configured")
        return {"provider": "tapetide", "dataset": name, "data": self.fallback.native(name, **parameters), "schema": "tapetide"}

    def get_market_session(self, instrument_key):
        if self.live:
            return self.live.sessions.context(instrument_key)
        from .market_session import MarketSessions
        return MarketSessions(self).context(instrument_key)

    def get_option_chain(self, instrument_key: str, expiry_date: str):
        if self.live:
            self.live.watch([instrument_key], renew_group=True)
            context = self.get_market_session(instrument_key)
            if context["active"]:
                captured = self.live.chain(instrument_key, expiry_date)
                from .market_session import timestamp
                seed_at = timestamp(captured[1].get("rest_seed_at")) if captured else None
                if captured and captured[1].get("transport") == "websocket" and seed_at and (now() - seed_at).total_seconds() < 60:
                    self.store.count("stream_hits")
                    return captured[0]
        rows = self._cached_rest("get_option_chain", instrument_key, expiry_date)
        if self.live:
            saved = self.store.option_chain_snapshot(instrument_key, expiry_date, market_day().isoformat())
            metadata = {"observed_at": saved["observed_at"] if saved else None,
                        "rest_seed_at": saved["observed_at"] if saved else None,
                        "reported_at": None, "transport": "rest", "session_date": context.get("session_date"), "live_legs": 0}
            self.live.seed_chain(instrument_key, expiry_date, rows, metadata)
            merged = self.live.chain(instrument_key, expiry_date) if context["active"] else None
            if merged:
                return merged[0]
        return rows

    def get_current_option_chain_snapshot(self, instrument_key: str, expiry_date: str):
        if self.live:
            captured = self.live.chain(instrument_key, expiry_date)
            if captured:
                return {"payload": captured[0], **captured[1]}
        return self.store.option_chain_snapshot(instrument_key, expiry_date, market_day().isoformat())

    def _quotes(self, method, instrument_keys):
        keys = instrument_keys.split(",") if isinstance(instrument_keys, str) else list(instrument_keys)
        streamed = self.live.quotes(keys) if self.live else {}
        missing = [key for key in keys if key not in streamed]
        result = self._cached_rest(method, missing) if missing else {}
        for key, value in streamed.items():
            result[key] = value
        if streamed:
            self.store.count("stream_hits")
        return result

    def get_option_greeks_v3(self, instrument_keys):
        keys = instrument_keys.split(",") if isinstance(instrument_keys, str) else list(instrument_keys)
        quotes = self.live.quotes(keys) if self.live else {}
        streamed = {key: {**value["option_greeks"], "iv": value["iv"], "instrument_token": key,
                          "last_price": value["last_price"], "timestamp": value["timestamp"]}
                    for key, value in quotes.items() if "option_greeks" in value and "iv" in value}
        missing = [key for key in keys if key not in streamed]
        return {**(self._cached_rest("get_option_greeks_v3", missing) if missing else {}), **streamed}

    def get_full_market_quotes_v3(self, instrument_keys):
        return self._quotes("get_full_market_quotes_v3", instrument_keys)

    def get_ltp_quotes_v3(self, instrument_keys):
        return self._quotes("get_ltp_quotes_v3", instrument_keys)

    def get_ipos(self, status="open", issue_type=None, page_number=1, records=30):
        from .ipo_store import IpoStore
        params = {"status": status, "issue_type": issue_type, "page_number": page_number, "records": records}
        return self.store.read("get_ipos", params,
            lambda: self._remote_call("get_ipos", **params), normalize=IpoStore.save_upstox)

    def get_ipo_details(self, ipo_id: str):
        from .ipo_store import IpoStore
        return self.store.read("get_ipo_details", {"ipo_id": ipo_id},
            lambda: self._remote_call("get_ipo_details", ipo_id), normalize=IpoStore.save_upstox)

    def get_option_contracts(self, instrument_key: str, expiry_date: str | None = None) -> list[dict]:
        archive_key = request_key("contract_archive", {"key": instrument_key, "expiry": expiry_date})
        hit, retained = self.store.cache.get(archive_key)
        if not hit:
            retained = self.store.contracts(instrument_key, expiry_date)
            self.store.cache.put(archive_key, retained, 60)
        if expiry_date and retained:
            self.store.count("db_hits" if not hit else "cache_hits")
            return retained
        method = "get_expired_option_contracts" if expiry_date and expiry_date < market_day().isoformat() else "get_option_contracts"
        params = {"instrument_key": instrument_key, "expiry_date": expiry_date}
        try:
            rows = self.store.read(method, params,
                lambda: self._remote_call(method, instrument_key, expiry_date) if expiry_date else self._remote_call(method, instrument_key),
                normalize=lambda conn, payload, at: self.store.save_contracts(conn, instrument_key, payload, at)) or []
        except Exception:
            if not retained:
                raise
            # Contract identities remain usable after their master entry is purged.
            return retained
        # Keep historical contract identifiers after they disappear from the master.
        merged = {(r.get("expiry"), r.get("strike_price"), r.get("instrument_type")): r for r in retained}
        merged.update({(r.get("expiry"), r.get("strike_price"), r.get("instrument_type")): r for r in rows})
        result = list(merged.values())
        self.store.cache.put(archive_key, result, 60)
        return result

    def get_expired_option_contracts(self, underlying_instrument_key: str, expiry_date: str):
        return self.get_option_contracts(underlying_instrument_key, expiry_date)

    def get_known_expiries(self, instrument_key: str):
        return self.store.known_expiries(instrument_key)

    def get_retained_option_chain(self, instrument_key: str, expiry_date: str, as_of: str):
        """Read the exact dated capture only. Never request today's chain for history."""
        saved = self.store.option_chain_snapshot(instrument_key, expiry_date, as_of)
        from .market_stream_store import MarketStreamStore
        streamed = MarketStreamStore(self.store).retained_chain(instrument_key, expiry_date, as_of)
        from .market_session import timestamp
        if streamed and (not saved or timestamp(streamed["observed_at"]) > timestamp(saved["observed_at"])):
            return streamed
        return saved

    def get_historical_candles_v3(self, instrument_key: str, unit: str, interval: int | str,
                                  to_date: str, from_date: str | None = None, *, force_refresh: bool = False):
        from .data_providers import TapetideAPIError, available, upstream_unavailable
        error = None
        try:
            primary = self._upstox_historical_candles_v3(instrument_key, unit, interval, to_date, from_date, force_refresh=force_refresh)
        except Exception as exc:
            if not upstream_unavailable(exc):
                raise
            primary, error = None, exc
        if self.fallback and (not available(primary) or primary.get("_partial")):
            first = from_date or (date.fromisoformat(to_date) - timedelta(days=3649)).isoformat()
            try:
                secondary = self.fallback.candles(instrument_key, unit, interval, first, to_date, primary)
            except (TapetideAPIError, ValueError, KeyError, TypeError):
                secondary = None
            if available(secondary):
                self.store.count("tapetide_fallback_hits")
                return secondary
        if error:
            raise error
        return primary

    def _upstox_historical_candles_v3(self, instrument_key: str, unit: str, interval: int | str,
                                  to_date: str, from_date: str | None = None, *, force_refresh: bool = False):
        if from_date is None:
            lookback = 28 if unit == "minutes" else 80 if unit == "hours" else 3650
            from_date = (date.fromisoformat(to_date) - timedelta(days=lookback - 1)).isoformat()
        if instrument_key.count("|") > 1:
            expired_interval = "day" if unit == "days" else f"{interval}minute" if unit == "minutes" else None
            if expired_interval is None:
                raise ValueError("Use day or a supported minute interval for expired contracts")
            return self.get_expired_historical_candles(instrument_key, expired_interval, to_date, from_date, force_refresh=force_refresh)

        def load_window(lo: str, hi: str):
            today = market_day().isoformat()
            if hi != today or unit not in ("minutes", "hours"):
                return self._remote_call("get_historical_candles_v3", instrument_key, unit, interval, hi, lo)
            rows = []
            if lo < today:
                yesterday = (market_day() - timedelta(days=1)).isoformat()
                historical = self._remote_call("get_historical_candles_v3", instrument_key, unit, interval, yesterday, lo) or {}
                rows.extend(historical.get("candles", []) if isinstance(historical, dict) else historical)
            intraday = self._remote_call("get_intraday_candles_v3", instrument_key, unit, interval) or {}
            rows.extend(intraday.get("candles", []) if isinstance(intraday, dict) else intraday)
            return {"candles": rows}
        return self.store.candles(instrument_key, unit, interval, from_date, to_date,
            load_window, force=force_refresh)

    def get_expired_historical_candles(self, expired_instrument_key: str, interval: str, to_date: str, from_date: str, *, force_refresh: bool = False):
        from .upstox_service import _parse_interval
        unit, grain = _parse_interval(interval)
        # Reuse bars retained while the token was active. Date bounds disambiguate
        # reused tokens; the upstream request still uses the exact expired key.
        parts = expired_instrument_key.split("|")
        storage_key = "|".join(parts[:2]) if len(parts) == 3 else expired_instrument_key
        return self.store.candles(storage_key, unit, grain, from_date, to_date,
            lambda lo, hi: self._remote_call("get_expired_historical_candles", expired_instrument_key, interval, hi, lo), force=force_refresh)

    def get_intraday_candles_v3(self, instrument_key: str, unit: str = "minutes", interval: int | str = 1):
        day = market_day().isoformat()
        return self.store.candles(instrument_key, unit, interval, day, day,
            lambda lo, hi: self._remote_call("get_intraday_candles_v3", instrument_key, unit, interval))

    def get_previous_option_close(self, instrument_key: str, as_of: str):
        """Find the most recent traded close strictly before the as-of session.

        Search at most one year, through the same durable candle gateway. A retained
        candidate narrows the search, but never bypasses checking for newer trades.
        No current quote is used and no synthetic candle is stored on the as-of day.
        """
        from .option_prices import latest_traded_close
        cutoff = date.fromisoformat(as_of)
        if cutoff > market_day():
            raise ValueError("Cannot price a future session")
        last = cutoff - timedelta(days=1)
        first = cutoff - timedelta(days=365)
        storage_key = "|".join(instrument_key.split("|")[:2])
        retained = self.store.latest_option_candle_day(storage_key, first, last)
        for span in ([None] if retained else [7, 30, 90, 365]):
            start = retained or cutoff - timedelta(days=span)
            raw = self.get_historical_candles_v3(instrument_key, "days", 1, last.isoformat(), start.isoformat())
            if raw.get("_partial"):
                raise ValueError("Cannot verify the latest price with incomplete candle coverage")
            price = latest_traded_close(raw.get("candles", []), start.isoformat(), last.isoformat())
            if price:
                return price
        return None

    def _validated_analytics(self, method: str, instrument_key: str, expiry: str, day: str, bucket: int):
        # Validate *before storing*: Upstox carries Friday's analytics into weekends.
        if day > market_day().isoformat() or day > expiry:
            return {}
        candles = self.get_historical_candles_v3(instrument_key, "days", 1, day, day)["candles"]
        exact = [row for row in candles if str(row[0])[:10] == day]
        close = float(exact[-1][4]) if exact else None
        if close is None:
            if day != market_day().isoformat() or not self.get_intraday_candles_v3(instrument_key)["candles"]:
                return {}
        payload = self._remote_call(method, instrument_key, expiry=expiry, date=day, bucket_interval=bucket) or {}
        import nifty_max_pain as nmp
        if not nmp.dated_payload_matches(payload, expiry, day, instrument_key,
                                         close if day < market_day().isoformat() else None):
            return {}
        return payload

    def get_max_pain(self, instrument_key: str, expiry: str = "current_week", date: str | None = None,
                     bucket_interval: int = 60):
        day = date or market_day().isoformat()
        params = {"instrument_key": instrument_key, "expiry": expiry, "date": day, "bucket_interval": 1}
        error = None
        try:
            payload = self.store.read("get_max_pain", params,
                lambda: self._validated_analytics("get_max_pain", instrument_key, expiry, day, 1),
                normalize=lambda conn, value, at: self.store.save_max_pain(conn, params, value, at))
        except Exception as exc:
            from .data_providers import upstream_unavailable
            if not upstream_unavailable(exc):
                raise
            payload, error = None, exc
        payload = self._with_fallback("get_max_pain", params, payload, error)
        if bucket_interval <= 1 or not payload:
            return payload
        # Retain one-minute source points once and reuse them for coarser requests.
        def included(row):
            try:
                hh, mm = map(int, str(row["time"])[:5].split(":"))
                return (hh * 60 + mm - (9 * 60 + 15)) % bucket_interval == 0
            except (KeyError, ValueError):
                return False
        return {**payload, "insights": [row for row in payload.get("insights") or [] if included(row)]}

    def get_recorded_session_dates(self, instrument_key: str, first: str, last: str):
        key = request_key("recorded_session_dates", {"key": instrument_key, "first": first, "last": last})
        hit, dates = self.store.cache.get(key)
        if not hit:
            dates = self.store.recorded_session_dates(instrument_key, first, last)
            self.store.cache.put(key, dates, 30)
        return dates

    def has_retained_market_session(self, instrument_key: str, day: str):
        return day in self.get_recorded_session_dates(instrument_key, day, day)

    def get_volume_pcr_history(self, instrument_key: str, expiry: str, day: str):
        from .volume_pcr import chain_series
        cache_key = request_key("volume_pcr_captures_v1", {"key": instrument_key, "expiry": expiry, "day": day})
        hit, points = self.store.cache.get(cache_key)
        if not hit:
            captures = self.store.option_chain_history(instrument_key, expiry, day)
            points = chain_series(captures, instrument_key, expiry, day, now())
            self.store.cache.put(cache_key, points, 30)
        if day == market_day().isoformat() and self.get_market_session(instrument_key).get("active"):
            # Existing REST cache seeds the chain; fresh feed fields take priority.
            self.get_option_chain(instrument_key, expiry)
            captured = self.get_current_option_chain_snapshot(instrument_key, expiry)
            if isinstance(captured, dict):
                fresh = chain_series([captured], instrument_key, expiry, day, now())
                merged = {point["time"]: point for point in points}
                merged.update({point["time"]: point for point in fresh})
                return [merged[minute] for minute in sorted(merged)]
        return points

    def get_iv_history(self, instrument_key: str, expiry: str, day: str):
        from .iv_metrics import minute_points, daily_samples
        key = request_key("iv_history_v1", {"key": instrument_key, "expiry": expiry, "day": day})
        hit, result = self.store.cache.get(key)
        if not hit:
            first = (date.fromisoformat(day)-timedelta(days=365)).isoformat()
            captures = self.store.iv_captures(instrument_key, expiry, first, day)
            cutoff = min(now(), datetime.fromisoformat(day).replace(tzinfo=IST)+timedelta(days=1)-timedelta(microseconds=1))
            all_points = minute_points(captures, instrument_key, expiry, cutoff)
            result = {"points": [point for point in all_points if point["date"] == day],
                      "daily": daily_samples(all_points, day)}
            self.store.cache.put(key, result, 30)
        if day == market_day().isoformat() and self.get_market_session(instrument_key).get("active"):
            self.get_option_chain(instrument_key, expiry)
            capture = self.get_current_option_chain_snapshot(instrument_key, expiry)
            fresh = minute_points([capture], instrument_key, expiry, now()) if isinstance(capture, dict) else []
            points = {point["time"]: point for point in result["points"]}
            points.update({point["time"]: point for point in fresh if point["date"] == day})
            return {**result, "points": [points[minute] for minute in sorted(points)]}
        return result

    def get_oi_data(self, instrument_key: str, expiry: str, date: str, bucket_interval: int | None = None):
        params = {"instrument_key": instrument_key, "expiry": expiry, "date": date, "bucket_interval": bucket_interval}
        return self.store.read("get_oi_data", params,
            lambda: self._validated_analytics("get_oi_data", instrument_key, expiry, date, bucket_interval))

    def get_pcr(self, instrument_key: str, expiry: str = "current_week", date: str | None = None,
                bucket_interval: int = 1):
        day = date or market_day().isoformat()
        params = {"instrument_key": instrument_key, "expiry": expiry, "date": day, "bucket_interval": 1}
        error = None
        try:
            payload = self.store.read("get_pcr", params,
                lambda: self._validated_analytics("get_pcr", instrument_key, expiry, day, 1))
        except Exception as exc:
            from .data_providers import upstream_unavailable
            if not upstream_unavailable(exc):
                raise
            payload, error = None, exc
        payload = self._with_fallback("get_pcr", params, payload, error)
        if bucket_interval <= 1 or not payload:
            return payload
        def included(row):
            try:
                hour, minute = map(int, str(row["time"])[:5].split(":"))
                return (hour * 60 + minute - 555) % bucket_interval == 0
            except (KeyError, ValueError):
                return False
        return {**payload, "insights": [row for row in payload.get("insights") or [] if included(row)]}
