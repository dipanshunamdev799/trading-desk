"""Frozen Upstox 5-minute data, strict regular-session validation, and provenance.

Run ``.venv/Scripts/python.exe -m research.swing.data --as-of 2026-11-10``.
The as-of date is exclusive: only earlier completed sessions are admitted.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TZ = "Asia/Kolkata"
COLS = ["ts", "open", "high", "low", "close", "volume", "oi"]
SPECS = {
    "NIFTY": {"key": "NSE_INDEX|Nifty 50", "kind": "nontradable_index", "legacy": [
        "artifacts/directional_research_phase2/expanded-nifty-5minute.json",
        "artifacts/directional_research/nifty-upstox-5minute.json"]},
    "NIFTYBEES": {"key": "NSE_EQ|INF204KB14I2", "kind": "cash_etf_long_only", "legacy": [
        "artifacts/directional_research_phase2/context-niftybees-5minute.json"]},
    "BANKBEES": {"key": "NSE_EQ|INF204KB15I9", "kind": "cash_etf_long_only", "legacy": []},
}
# Explicit observed special-session dates. No ordinary pre/post-market prints
# from otherwise complete regular sessions are admitted to execution replay.
SPECIAL_SESSION_DATES = {
    "2023-11-12": "observed Muhurat session outside normal hours",
    "2024-03-02": "observed short special trading session",
    "2024-05-18": "observed short special trading session",
    "2024-11-01": "observed Muhurat session outside normal hours",
    "2025-10-21": "observed short special/Muhurat session",
    "2026-11-08": "observed short special/Muhurat session",
}
_rate_lock = threading.Lock()
_last_request = 0.0


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frame(obj) -> pd.DataFrame:
    if isinstance(obj, dict):
        obj = obj.get("payload", obj)
        obj = obj.get("data", obj) if isinstance(obj, dict) else obj
        obj = obj.get("candles", []) if isinstance(obj, dict) else obj
    if not obj:
        return pd.DataFrame(columns=COLS[1:], dtype=float,
                            index=pd.DatetimeIndex([], tz=TZ, name="ts"))
    if isinstance(obj[0], list):
        obj = [dict(zip(COLS, row)) for row in obj]
    frame = pd.DataFrame(obj)
    frame["ts"] = pd.to_datetime(frame.ts, utc=True).dt.tz_convert(TZ)
    for col in COLS[1:]:
        frame[col] = pd.to_numeric(frame.get(col, 0), errors="coerce")
    return frame.set_index("ts")[COLS[1:]].sort_index(kind="stable")


def _windows(start: date, end: date):
    current = start.replace(day=1)
    while current <= end:
        nxt = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        yield max(start, current), min(end, nxt - timedelta(days=1))
        current = nxt


def _request_slot():
    global _last_request
    with _rate_lock:
        time.sleep(max(0, .35 - (time.monotonic() - _last_request)))
        _last_request = time.monotonic()


def _client():
    sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
    from app.config import get_settings
    from upstox_analytics import UpstoxAnalyticsClient
    return UpstoxAnalyticsClient(get_settings().upstox_analytics_token, timeout=25, max_retries=1)


def validate_sessions(frame: pd.DataFrame, start: str, as_of: str):
    """Require exactly all 75 regular-session bars; exclude special sessions explicitly."""
    frame = frame.loc[(frame.index >= pd.Timestamp(start, tz=TZ)) &
                      (frame.index < pd.Timestamp(as_of, tz=TZ))].copy()
    duplicates = int(frame.index.duplicated().sum())
    frame = frame.loc[~frame.index.duplicated(keep="last")].sort_index()
    minute = frame.index.hour * 60 + frame.index.minute
    off = (minute < 555) | (minute >= 930)
    off_session = {str(k): int(v) for k, v in pd.Series(off.astype(int), index=frame.index).groupby(frame.index.strftime("%Y-%m-%d")).sum().items() if v}
    frame = frame.loc[~off]
    valid = (np.isfinite(frame[["open", "high", "low", "close"]]).all(axis=1) &
             frame.low.gt(0) & frame.high.ge(frame[["open", "low", "close"]].max(axis=1)) &
             frame.low.le(frame[["open", "high", "close"]].min(axis=1)))
    invalid = int((~valid).sum())
    good, excluded = [], []
    expected = np.arange(555, 930, 5)
    for day, group in frame.groupby(frame.index.strftime("%Y-%m-%d")):
        times = group.index.hour * 60 + group.index.minute
        complete = len(group) == 75 and np.array_equal(times, expected)
        okay = bool(valid.reindex(group.index).all())
        if complete and okay:
            good.append(day)
        else:
            excluded.append({"day": day, "bars": len(group), "invalid_ohlc": not okay,
                             "reason": "incomplete_or_special_session" if not complete else "invalid_ohlc"})
    clean = frame.loc[frame.index.strftime("%Y-%m-%d").isin(good)]
    audit = {"raw_duplicate_timestamps": duplicates, "invalid_ohlc_rows": invalid,
             "off_session_bars_by_day": off_session, "excluded_sessions": excluded,
             "rows": len(clean), "sessions": len(good),
             "first": str(clean.index.min()) if len(clean) else None,
             "last": str(clean.index.max()) if len(clean) else None,
             "zero_volume_bars": int(clean.volume.eq(0).sum()),
             "missing_sessions_caveat": "Observed sessions checked for exact completeness; absent whole days are not independently reconciled to official holiday calendar."}
    return clean, audit


def special_execution_bars(frame: pd.DataFrame, regular: pd.DataFrame,
                           start: str, as_of: str):
    """Preserve raw, valid bars on explicitly known short/special sessions.

    These rows are for stops/targets and equity marks only. They must never be
    mixed into the regular-session indicator input. All raw clock times on each
    admitted special day are retained, including evening Muhurat candles.
    """
    bounded = frame.loc[(frame.index >= pd.Timestamp(start, tz=TZ)) &
                        (frame.index < pd.Timestamp(as_of, tz=TZ))].copy()
    bounded = bounded.loc[~bounded.index.duplicated(keep="last")].sort_index()
    regular_days = set(regular.index.strftime("%Y-%m-%d"))
    admitted_days = set(SPECIAL_SESSION_DATES) - regular_days
    raw_special = bounded.loc[bounded.index.strftime("%Y-%m-%d").isin(admitted_days)]
    valid = (np.isfinite(raw_special[["open", "high", "low", "close"]]).all(axis=1) &
             raw_special.low.gt(0) &
             raw_special.high.ge(raw_special[["open", "low", "close"]].max(axis=1)) &
             raw_special.low.le(raw_special[["open", "high", "close"]].min(axis=1)))
    result = raw_special.loc[valid].copy()
    counts = result.groupby(result.index.strftime("%Y-%m-%d")).size()
    audit = {"rows": len(result), "invalid_ohlc_excluded": int((~valid).sum()),
             "sessions": [{"day": day, "bars": int(count), "reason": SPECIAL_SESSION_DATES[day],
                           "first": str(result.loc[result.index.strftime("%Y-%m-%d") == day].index.min()),
                           "last": str(result.loc[result.index.strftime("%Y-%m-%d") == day].index.max())}
                          for day, count in counts.items()],
             "policy": "Execution only: replay valid unique raw candles on explicit known short/special dates, including evening bars. Ordinary stray pre/post-session prints on complete regular dates are excluded. Indicators remain based solely on complete regular sessions.",
             "timestamp_semantics": "Provider five-minute candle START in Asia/Kolkata; end=start+5min.",
             "calendar_caveat": "Session labels describe observed provider data; special session clock times are not independently certified against each exchange circular."}
    return result, audit


def prepare_data(output_path=None, as_of="2026-11-10", *, start="2023-01-01", offline=False):
    """Return symbol->DataFrame with Asia/Kolkata START DatetimeIndex; persist CSV+manifest.

    Legacy files are immutable inputs. New raw responses embed instrument identity,
    window, acquisition timestamp, and SHA256 fingerprints in a separate manifest.
    """
    out = Path(output_path or ROOT / "artifacts" / "swing_research")
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    begin, cutoff = date.fromisoformat(start), date.fromisoformat(as_of) - timedelta(days=1)

    def load_symbol(symbol):
        spec = SPECS[symbol]
        frames, sources, requests = [], [], []
        for relative in spec["legacy"]:
            path = ROOT / relative
            if path.exists():
                f = _frame(json.loads(path.read_text(encoding="utf-8")))
                frames.append(f)
                sources.append({"path": str(path), "sha256": _hash(path), "rows": len(f),
                                "instrument_key": spec["key"], "identity": "legacy_fetch_script_and_manifest"})
        previous = pd.concat(frames).sort_index() if frames else _frame([])
        client, auth_failed = None, False
        for first, last in _windows(begin, cutoff):
            path = raw / symbol / f"{first}-{last}-5m.json"
            # Freeze a new response when legacy has no coverage, or at the final month
            # where the legacy download may not include the most recent completed day.
            mask = (previous.index >= pd.Timestamp(first, tz=TZ)) & (previous.index < pd.Timestamp(last + timedelta(days=1), tz=TZ))
            need = not mask.any() or last == cutoff
            if not path.exists() and (not need or offline or auth_failed):
                if need:
                    requests.append({"from": str(first), "to": str(last), "status": "offline_or_auth_unavailable"})
                continue
            try:
                if path.exists():
                    wrapped = json.loads(path.read_text(encoding="utf-8"))
                    if wrapped.get("instrument_key") != spec["key"]:
                        raise ValueError("Cached instrument identity does not match request")
                else:
                    client = client or _client()
                    _request_slot()
                    payload = client.get_historical_candles_v3(spec["key"], "minutes", 5, str(last), str(first))
                    wrapped = {"instrument_key": spec["key"], "symbol": symbol, "unit": "minutes", "interval": 5,
                               "from": str(first), "to": str(last), "retrieved_at": pd.Timestamp.now(tz="UTC").isoformat(), "payload": payload}
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(wrapped), encoding="utf-8")
                f = _frame(wrapped)
                frames.append(f)
                sources.append({"path": str(path), "sha256": _hash(path), "rows": len(f),
                                "instrument_key": spec["key"], "identity": "embedded_and_verified"})
                requests.append({"from": str(first), "to": str(last), "rows": len(f), "status": "ok"})
                print(f"{symbol} {first} {len(f)} bars", flush=True)
            except Exception as exc:
                status = getattr(exc, "status_code", None)
                requests.append({"from": str(first), "to": str(last), "status": "error", "error_type": type(exc).__name__, "http_status": status})
                print(f"{symbol} {first} ERROR {type(exc).__name__} {status}", flush=True)
                auth_failed = status in (401, 403) or isinstance(exc, ValueError)
        combined = pd.concat(frames) if frames else _frame([])
        overlap_conflicts = []
        duplicated = combined.loc[combined.index.duplicated(keep=False)]
        if len(duplicated):
            spread = duplicated.groupby(level=0)[["open", "high", "low", "close"]].agg(lambda s: s.max() - s.min())
            overlap_conflicts = [str(t) for t in spread.index[(spread > .011).any(axis=1)]]
        clean, audit = validate_sessions(combined, start, as_of)
        audit.update({"instrument_key": spec["key"], "kind": spec["kind"], "sources": sources, "requests": requests,
                      "overlap_conflicting_timestamps": overlap_conflicts,
                      "price_adjustments": "Provider raw OHLC; corporate action adjustment status not certified; do not infer adjusted total returns.",
                      "futures_rolls": "not applicable; no futures used",
                      "research_start": "2024-11-10", "as_of_exclusive": as_of, "warmup_start": start})
        # Conflict observations are excluded as entire sessions, never averaged.
        if overlap_conflicts:
            days = {pd.Timestamp(t).strftime("%Y-%m-%d") for t in overlap_conflicts}
            clean = clean.loc[~clean.index.strftime("%Y-%m-%d").isin(days)]
            audit["excluded_conflict_sessions"] = sorted(days)
            audit["rows"] = len(clean)
            audit["sessions"] = clean.index.normalize().nunique()
        clean.to_csv(out / f"{symbol.lower()}-5minute.csv", index_label="ts")
        special, special_audit = special_execution_bars(combined, clean, start, as_of)
        special_path = out / f"{symbol.lower()}-special-execution.csv"
        special.to_csv(special_path, index_label="ts")
        special_audit.update(path=str(special_path), sha256=_hash(special_path))
        audit["special_execution"] = special_audit
        return symbol, clean, audit

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(load_symbol, SPECS))
    manifest = {"as_of_exclusive": as_of, "research_start": "2024-11-10", "warmup_start": start,
                "session": "09:15 <= start < 15:30 IST, all 75 five-minute bars required",
                "sources": {symbol: audit for symbol, _, audit in results},
                "reference_urls": ["https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/",
                                   "https://www.nseindia.com/static/market-data/market-timings"]}
    (out / "data-manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    supplement_path = out / "supplemental-audit.json"
    supplement = json.loads(supplement_path.read_text(encoding="utf-8")) if supplement_path.exists() else {}
    supplement["special_session_execution"] = {symbol: audit["special_execution"] for symbol, _, audit in results}
    supplement["execution_caveat"] = "Valid raw special-session bars are preserved separately for execution replay; concatenate them with regular bars for the backtester while keeping indicator inputs regular-only. Stops and targets still use conservative OHLC ordering, not tick-level sequencing."
    supplement_path.write_text(json.dumps(supplement, indent=2, default=str), encoding="utf-8")
    return {symbol: frame for symbol, frame, _ in results if len(frame)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default="2026-11-10")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "swing_research"))
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    frames = prepare_data(args.output, args.as_of, start=args.start, offline=args.offline)
    print(json.dumps({symbol: {"rows": len(f), "first": str(f.index.min()), "last": str(f.index.max())} for symbol, f in frames.items()}, indent=2))
