"""NIFTY research orchestration, provenance, freshness and retained history.

Dashboard reads never wait for providers. Collection is bounded, isolated from
the request path, and stores actual observations rather than manufactured scores.
"""
from __future__ import annotations

import logging
import math
import threading
import time
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..config import get_settings
from .nifty_catalog import FACTORS, FACTOR_MAP, SECTIONS
from .nifty_analytics import correlate_series, option_snapshot, technical_snapshot
from .nifty_sources import collect_market_data, parse_quotes, INDEX_KEYS, NIFTY_KEY
from .nifty_store import NiftyStore
from .upstox_service import get_market_store

LOG = logging.getLogger(__name__)
PRICE_FACTORS = {
    "sp500", "nasdaq", "dow", "us_futures", "nikkei", "hang_seng", "shanghai",
    "europe", "gift_nifty", "brent", "wti", "gold", "silver", "usdinr", "dxy",
    "natural_gas", "copper", "india_vix", "bank_nifty", "nifty_financial",
    "nifty_it", "nifty_auto", "nifty_fmcg", "nifty_pharma", "nifty_metal",
    "nifty_energy", "nifty_realty", "nifty_psu_bank",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parsed_time(value: Any) -> datetime | None:
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def has_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(has_value(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_value(item) for item in value)
    if isinstance(value, float) and not math.isfinite(value):
        return False
    return value is not None and value != ""


def latest_revisions(rows: list[dict]) -> list[dict]:
    """Resolve publisher revisions before inspecting values or quality flags.

    A later null or rejected reading supersedes the old numeric reading too.
    Original dictionaries remain untouched so raw evidence can retain revisions.
    """
    selected = {}
    earliest = datetime.min.replace(tzinfo=timezone.utc)
    for index, row in enumerate(rows):
        stamp = parsed_time(row.get("reported_at"))
        key = (row.get("source"), row.get("unit"), stamp.isoformat() if stamp else row.get("reported_at"))
        rank = (parsed_time(row.get("observed_at")) or earliest, index)
        if key not in selected or rank >= selected[key][0]:
            selected[key] = (rank, row)
    return sorted((item[1] for item in selected.values()),
                  key=lambda row: (parsed_time(row.get("reported_at")) or earliest,
                                   parsed_time(row.get("observed_at")) or earliest))


def _market_session_date(row: dict) -> str | None:
    """Retain a publisher's trading date when timestamps were normalized UTC."""
    context = row.get("context") if isinstance(row.get("context"), dict) else {}
    session = context.get("session_date")
    if isinstance(session, str) and len(session) == 10:
        try:
            return date.fromisoformat(session).isoformat()
        except ValueError:
            pass
    stamp = parsed_time(row.get("reported_at"))
    if stamp is None:
        return None
    exchange_zone = context.get("exchange_timezone")
    if isinstance(exchange_zone, str) and exchange_zone:
        try:
            return stamp.astimezone(ZoneInfo(exchange_zone)).date().isoformat()
        except (ZoneInfoNotFoundError, ValueError):
            pass
    # Without an exchange zone, preserve the source's supplied calendar date.
    try:
        return date.fromisoformat(str(row.get("reported_at"))[:10]).isoformat()
    except ValueError:
        return None


def _metric_observation(factor_id: str, metric: dict, basis: dict, reported_at: str | None) -> dict:
    return {
        **metric, "factor_id": factor_id, "reported_at": reported_at,
        "observed_at": basis.get("observed_at") or utc_now(),
        "source": basis.get("source") or "Derived from retained market data",
        "source_url": basis.get("source_url"),
        "unit": FACTOR_MAP.get(factor_id, {}).get("unit", ""),
        "basis": basis.get("basis") or "Derived from sourced observations; see calculation context",
        "expiry": basis.get("expiry"),
    }


class NiftyService:
    def __init__(self, repo=None, collector=None):
        self.repo = repo if repo is not None else NiftyStore(get_market_store())
        self.collector = collector if collector is not None else collect_market_data
        self.refresh_lock = threading.Lock()
        self.last_attempt = 0.0
        self.last_error: str | None = None
        self.stream_lock = threading.Lock()
        self.last_stream_read = 0.0

    def refresh_streamed(self):
        """Project committed feed updates into research without calling providers."""
        if not isinstance(self.repo, NiftyStore) or time.monotonic() - self.last_stream_read < 3 or not self.stream_lock.acquire(blocking=False):
            return
        try:
            self.last_stream_read = time.monotonic()
            from .upstox_service import get_upstox
            stream = get_upstox().live
            if not stream or not stream.status()["fresh"]:
                return
            rows = parse_quotes(stream.quotes(list(INDEX_KEYS.values())), INDEX_KEYS, utc_now())
            state = self.repo.state() or {}
            chain = state.get("option_chain") or []
            expiry = chain[0].get("expiry") if chain else None
            captured = stream.chain(NIFTY_KEY, expiry) if expiry else None
            if captured and captured[1].get("live_oi_legs") == len(captured[0]) * 2:
                payload, meta = captured
                basis = {"source": "Upstox option chain", "source_url": "https://upstox.com/developer/api-documentation/v3/get-market-data-feed/",
                         "observed_at": meta["observed_at"], "expiry": expiry,
                         "basis": "Derived from fresh streamed OI at every supplied strike; prior-session OI from retained REST seed"}
                for factor_id, metric in option_snapshot(payload).items():
                    if factor_id in {"call_oi", "put_oi", "call_oi_change", "put_oi_change", "pcr", "max_pain"}:
                        rows.append(_metric_observation(factor_id, metric, basis, meta["reported_at"]))
            self.repo.save_observations(rows)
        except Exception:
            LOG.exception("Could not project retained live quotes into NIFTY research")
        finally:
            self.stream_lock.release()

    @property
    def refreshing(self) -> bool:
        return self.refresh_lock.locked()

    def request_refresh(self) -> str:
        if not self.refresh_lock.acquire(blocking=False):
            return "running"
        self.last_attempt = time.monotonic()
        thread = threading.Thread(target=self._refresh_locked, name="nifty-refresh", daemon=True)
        thread.start()
        return "started"

    def refresh(self) -> dict:
        if not self.refresh_lock.acquire(blocking=False):
            return {"status": "running"}
        self.last_attempt = time.monotonic()
        return self._refresh_locked()

    def _refresh_locked(self) -> dict:
        try:
            collected = self.collector()
            prior = self.repo.state() or {}
            observations = list(collected.get("observations") or [])
            state = {**prior, "source_errors": collected.get("source_errors") or [], "last_refresh": utc_now()}
            # An upstream failure never replaces retained successes with emptiness.
            for key in ("candles", "candles_meta", "option_chain", "option_chain_meta", "expiries", "constituents", "events"):
                if collected.get(key):
                    state[key] = collected[key]
            candles = collected.get("candles") or []
            if candles:
                candle_meta = collected.get("candles_meta") or {}
                last_bar = max(candles, key=lambda row: str(row.get("ts", "")))
                reported = last_bar.get("ts")
                basis = {"source": candle_meta.get("source", "Upstox historical candles"),
                         "source_url": candle_meta.get("source_url", "https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/"),
                         "observed_at": candle_meta.get("observed_at", utc_now()),
                         "basis": candle_meta.get("basis", "Daily NIFTY spot candles; source timestamp is session start")}
                for factor_id, metric in technical_snapshot(candles).items():
                    if factor_id in FACTOR_MAP:
                        observations.append(_metric_observation(factor_id, metric, basis, reported))
            chain = collected.get("option_chain") or []
            if chain:
                # Option chain endpoints may omit an exchange timestamp. Collection
                # time remains separate and cannot turn an undated chain into live data.
                chain_meta = collected.get("option_chain_meta") or {}
                chain_time = chain_meta.get("reported_at") or collected.get("option_chain_reported_at")
                basis = {"source": "Upstox option chain", "source_url": "https://upstox.com/developer/api-documentation/get-pc-option-chain/",
                         "observed_at": chain_meta.get("observed_at") or collected.get("option_chain_observed_at") or utc_now(),
                         "expiry": chain_meta.get("expiry") or chain[0].get("expiry") or chain[0].get("expiry_date"),
                         "basis": "Nearest listed unexpired NIFTY contract; snapshot, not prediction"}
                for factor_id, metric in option_snapshot(chain).items():
                    if factor_id in FACTOR_MAP:
                        observations.append(_metric_observation(factor_id, metric, basis, chain_time))
                state["option_chain_reported_at"] = chain_time
                state["option_chain_observed_at"] = basis["observed_at"]
            expiries = collected.get("expiries") or []
            if expiries and "expiry_calendar" in FACTOR_MAP:
                observations.append({"factor_id": "expiry_calendar", "value": expiries,
                    "source": "Upstox listed option contracts", "source_url": "https://upstox.com/developer/api-documentation/get-option-contracts/",
                    "reported_at": None, "observed_at": utc_now(), "context": "Dates come from listed contracts. Master publication time is not supplied."})
                specifications = [{"expiry": row.get("expiry"), "weekly": row.get("weekly"),
                                   "lot_sizes": row.get("lot_sizes") or []}
                                  for row in expiries if row.get("lot_sizes")]
                if specifications:
                    observations.append({"factor_id": "contract_specs", "value": specifications,
                        "source": "Upstox listed option contracts", "source_url": "https://upstox.com/developer/api-documentation/get-option-contracts/",
                        "reported_at": None, "observed_at": utc_now(),
                        "context": "Current lot sizes from listed contracts by expiry. Changes require a dated prior specification or exchange circular; no historical change is inferred."})
            count = self.repo.save_observations([row for row in observations if row.get("factor_id") in FACTOR_MAP])
            if collected.get("events"):
                self.repo.save_events(collected["events"])
            self.repo.save_state(state)
            self.last_error = None
            return {"status": "completed", "observations_saved": count, "source_errors": state["source_errors"], "last_refresh": state["last_refresh"]}
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {str(exc)[:300]}"
            LOG.exception("NIFTY collection failed; previous observations remain available")
            return {"status": "failed", "error": self.last_error}
        finally:
            self.refresh_lock.release()

    def _factor(self, definition: dict, observation: dict | None, history: list, at: datetime) -> dict:
        row = dict(observation or {})
        history = [point for point in latest_revisions(history) if not point.get("quality_note")]
        value = row.get("value")
        stamp = parsed_time(row.get("reported_at"))
        max_age = definition.get("stale_after_seconds", 86400)
        if not has_value(value):
            status = "missing"
            note = row.get("context") if isinstance(row.get("context"), str) and row.get("context") else "No sourced observation collected. Open the suggested source or import a published reading."
        elif stamp is None:
            status, note = "stale", "Publisher time is unavailable. Collection time is shown separately; freshness cannot be verified."
        elif stamp > at + timedelta(minutes=5):
            status, note = "stale", "Source timestamp is in the future; verify this observation."
        elif (at - stamp).total_seconds() > max_age:
            status, note = "stale", f"Retained source reading exceeds the {definition.get('cadence', 'configured')} freshness window."
        else:
            status, note = "available", "Source reading is within the configured freshness window."
        if row.get("quality_note"):
            status = "stale" if has_value(value) else "missing"
            note = str(row["quality_note"])
        previous = row.get("previous_value")
        if row.get("quality_note"):
            previous = None
        if previous is None and numeric(value) and not row.get("quality_note"):
            candidates = [point for point in history if numeric(point.get("value"))
                          and point.get("source") == row.get("source")
                          and point.get("unit") == row.get("unit")
                          and point.get("reported_at") != row.get("reported_at")
                          and parsed_time(point.get("reported_at")) is not None
                          and (stamp is None or parsed_time(point.get("reported_at")) < stamp)]
            if candidates:
                previous = candidates[-1]["value"]
        change, change_pct = row.get("change"), row.get("change_pct")
        if row.get("quality_note"):
            change, change_pct = None, None
        if numeric(value) and numeric(previous) and not row.get("quality_note"):
            if change is None:
                change = value - previous
            if change_pct is None and previous != 0:
                change_pct = (value - previous) / abs(previous) * 100
        points = [{"ts": point["reported_at"], "value": point["value"]} for point in history
                  if numeric(point.get("value")) and point.get("reported_at")
                  and point.get("source") == row.get("source") and point.get("unit") == row.get("unit")]
        context = row.get("context") or definition.get("description", "")
        historical_context = None
        values = [p["value"] for p in points]
        if numeric(value) and not row.get("quality_note") and len(values) >= 5:
            historical_context = {"samples": len(values), "low": min(values), "high": max(values),
                                  "percentile": round(100 * sum(v <= value for v in values) / len(values), 1),
                                  "note": "Empirical rank among retained observations; descriptive, not predictive."}
        trend = None if row.get("quality_note") else row.get("trend")
        if not trend and numeric(change):
            trend = "up" if change > 0 else "down" if change < 0 else "flat"
        return {**definition, "unit": row.get("unit") or definition.get("unit", ""),
                "value": value, "previous_value": previous, "change": change,
                "change_pct": change_pct, "trend": trend,
                "context": context, "source": row.get("source"), "source_url": row.get("source_url") or definition.get("source_url"),
                "reported_at": row.get("reported_at"), "observed_at": row.get("observed_at"),
                "reporting_date": row.get("reporting_date"),
                "status": status, "availability_note": note, "history": points[-60:],
                "historical_context": historical_context, "basis": row.get("basis"), "strikes": row.get("strikes"), "expiry": row.get("expiry"),
                "quality": row.get("quality"), "quality_note": row.get("quality_note")}

    def dashboard(self, auto_refresh=True) -> dict:
        self.refresh_streamed()
        at = datetime.now(timezone.utc)
        errors, state, latest = [], {}, {}
        try:
            state, latest = self.repo.state() or {}, self.repo.latest()
            events = self.repo.events(limit=100)
        except Exception as exc:
            errors.append({"source": "Research database", "error": f"{type(exc).__name__}: {str(exc)[:240]}"})
            events = []
        settings = get_settings()
        if auto_refresh and settings.nifty_collector_enabled and time.monotonic() - self.last_attempt >= max(60, settings.nifty_refresh_seconds):
            self.request_refresh()
        factors = []
        for definition in FACTORS:
            observation = latest.get(definition["id"])
            history = []
            if observation and numeric(observation.get("value")):
                try:
                    history = self.repo.history(definition["id"], limit=120)
                except Exception:
                    pass
            factors.append(self._factor(definition, observation, history, at))
        errors.extend(state.get("source_errors") or [])
        if self.last_error:
            errors.append({"source": "NIFTY collector", "error": self.last_error})
        return {"generated_at": at.isoformat(), "last_refresh": state.get("last_refresh"), "refreshing": self.refreshing,
                "summary": {"total": len(factors), **{status: sum(f["status"] == status for f in factors) for status in ("available", "stale", "missing")},
                            "drivers": sum(f["kind"] == "driver" for f in factors), "indicators": sum(f["kind"] == "indicator" for f in factors)},
                "sections": [{**section, "factors": [f for f in factors if f["section_id"] == section["id"]]} for section in SECTIONS],
                "candles": state.get("candles") or [], "source_errors": errors, "events": events,
                "expiries": state.get("expiries") or [], "notes": [
                    "Drivers, positioning indicators and contextual events have different roles. No composite buy/sell forecast is inferred.",
                    "Source time and collection time are separate. Stale includes undated readings; freshness uses elapsed time, including market holidays.",
                    "Public global quotes may be delayed. Commodity futures are contract proxies; inspect the source and basis.",
                    "Coverage is populated readings, not research completeness. Missing factors require an additional source or a sourced import.",
                    "Correlations align daily returns by date. Markets close in different time zones; a correlation is not a causal or tradable lead signal.",
                ]}

    def history(self, factor_id: str, limit=365) -> dict:
        if factor_id not in FACTOR_MAP:
            raise KeyError(factor_id)
        return {"factor_id": factor_id, "observations": self.repo.history(factor_id, limit=limit)}

    def correlations(self, factor_id: str) -> dict:
        if factor_id not in FACTOR_MAP:
            raise KeyError(factor_id)
        if factor_id not in PRICE_FACTORS:
            return {"factor_id": factor_id, "coefficient": None, "sample_count": 0,
                    "method": "Pearson correlation of aligned daily percentage returns",
                    "note": "Select a price or index series. Returns of rates, signed flows or qualitative data are not computed."}
        state = self.repo.state() or {}
        left = [{"ts": row["ts"], "value": row["close"]} for row in state.get("candles") or []]
        latest = self.repo.latest().get(factor_id) or {}
        sessions = {}
        for row in latest_revisions(self.repo.history(factor_id, limit=1000)):
            if row.get("source") != latest.get("source") or row.get("unit") != latest.get("unit"):
                continue
            day, stamp = _market_session_date(row), parsed_time(row.get("reported_at"))
            if day is None or stamp is None:
                continue
            revision = parsed_time(row.get("observed_at")) or stamp
            rank = (stamp, revision)
            if day not in sessions or rank >= sessions[day][0]:
                sessions[day] = (rank, row)
        right = [{"ts": day, "value": sessions[day][1]["value"]} for day in sorted(sessions)
                 if numeric(sessions[day][1].get("value")) and not sessions[day][1].get("quality_note")]
        return {"factor_id": factor_id, "source": latest.get("source"), "unit": latest.get("unit"),
                **correlate_series(left, right)}


@lru_cache
def get_nifty_service() -> NiftyService:
    return NiftyService()
