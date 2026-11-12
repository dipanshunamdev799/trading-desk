"""Dated October 2024 Nifty 500 fund-holdings proxy and frozen daily panel.

The official AMC workbook was published 7 Nov 2024. This is a dated fund
portfolio proxy, not a claim to possess the exact historical index master.
Current instruments resolve identity only; unresolved historical holdings stay
in the universe and receive an explicit disposition. No post-start additions.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import threading
import time

import numpy as np
import pandas as pd

from research.swing.data import ROOT, TZ, _client, _frame

START = "2024-11-11"
END = "2026-11-09"
WARMUP = "2020-01-01"
SOURCE_URL = "https://www.motilaloswalmf.com/content/dam/motilal-mf/downloads/mf/month-end-portfolio/2024/nov/6f698-month-end-portfolio-october-2024.xls"
LEGACY = ROOT / "artifacts" / "stock_swing_research"
DEFAULT_OUT = ROOT / "artifacts" / "swing_discovery"
_LOCK = threading.Lock()
_LAST = 0.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def slot():
    global _LAST
    with _LOCK:
        time.sleep(max(0, .35 - (time.monotonic() - _LAST)))
        _LAST = time.monotonic()


def universe(out=DEFAULT_OUT):
    out = Path(out)
    source = out / "sources" / "motilal-month-end-oct2024.xls"
    if not source.exists():
        import requests
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(r.content)
    import xlrd
    book = xlrd.open_workbook(str(source))
    sheet = book.sheet_by_name("YO18")
    assert "October 31, 2024" in str(sheet.cell_value(1, 1))
    master_path = LEGACY / "instrument-master.json"
    if not master_path.exists():
        dump(out / "sources" / "instrument-master.json", _client().download_bod_instruments("NSE"))
        master_path = out / "sources" / "instrument-master.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    eq = [r for r in master if r.get("segment") == "NSE_EQ" and r.get("instrument_type") in ("EQ", "BE", "BZ")]
    by_isin = {r["isin"]: r for r in eq}
    by_symbol = {r["trading_symbol"]: r for r in eq}
    norm = lambda x: re.sub("[^A-Z0-9]", "", str(x).upper().replace("LIMITED", "").replace("LTD", ""))
    by_name = {norm(r["name"]): r for r in eq}
    # Unambiguous historical company-name identities, not membership selection.
    aliases = {
        "Info Edge (India) Limited": "NAUKRI",
        "Multi Commodity Exchange of India Limited": "MCX",
        "Computer Age Management Services Limited": "CAMS",
        "JB Chemicals & Pharmaceuticals Limited": "JBCHEPHARM",
        "Piramal Enterprises Limited": "PEL",
        "Mazagon Dock Shipbuilders Limited": "MAZDOCK",
        "Gujarat State Petronet Limited": "GSPL",
        "Tata Investment Corporation Limited": "TATAINVEST",
        "ICICI Securities Limited": "ISEC",
        "Nuvama Wealth Management Limited": "NUVAMA",
    }
    rows = []
    for i in range(sheet.nrows):
        r = sheet.row_values(i)
        if len(r) < 8 or not re.fullmatch(r"INE[A-Z0-9]{9}", str(r[3])):
            continue
        name, isin = r[1], r[3]
        current = by_isin.get(isin)
        resolution = "exact_isin"
        if current is None:
            current = by_name.get(norm(name)) or by_symbol.get(aliases.get(name))
            resolution = "exact_normalized_company_name_or_explicit_alias" if current else "historical_isin_only_unresolved_current_listing"
        symbol = current["trading_symbol"] if current else aliases.get(name, norm(name))
        # Keep historical symbol for an established later rename.
        if symbol == "ETERNAL": symbol = "ZOMATO"
        if symbol == "TMPV": symbol = "TATAMOTORS"
        rows.append({"symbol": symbol, "name_at_start": name, "isin_at_start": isin,
                     "weight_at_start": float(r[7]) * 100, "sector": str(r[4]),
                     "instrument_key": current["instrument_key"] if current else "NSE_EQ|" + isin,
                     "current_symbol": current["trading_symbol"] if current else None,
                     "identity_resolution": resolution})
    assert len(rows) == 500 and len({r["symbol"] for r in rows}) == 500
    rows.sort(key=lambda r: r["symbol"])
    fifty = json.loads((LEGACY / "universe.json").read_text(encoding="utf-8"))
    missing50 = [r["symbol"] for r in fifty["stocks"] if r["isin_at_start"] not in {x["isin_at_start"] for x in rows}]
    result = {"date": "2024-10-31", "publication_date": "2024-11-07", "research_start": START,
              "label": "Official dated Nifty 500 index-fund holdings proxy",
              "source_url": SOURCE_URL, "source_sha256": sha(source), "workbook_sheet": "YO18",
              "policy": "Freeze all 500 October 2024 fund holdings before test start. Retain later index exits, missing/delisted names and failures in dispositions; never select from current membership.",
              "limitation": "Fund portfolio proxy may differ from the exact index at the margin; not an independently certified historical constituent master. Frozen membership after start is a cohort experiment, not a reconstituted index strategy.",
              "historical_nifty50_crosscheck_missing_isins": missing50,
              "instrument_master": {"path": str(master_path), "sha256": sha(master_path), "role": "identity and rename resolution only"},
              "stocks": rows}
    dump(out / "universe.json", result)
    return result


def fetch_one(spec, out):
    symbol, key = spec["symbol"], spec["instrument_key"]
    path = Path(out) / "raw" / symbol / "daily.json"
    try:
        if path.exists():
            wrapped = json.loads(path.read_text(encoding="utf-8"))
            assert wrapped["instrument_key"] == key
        else:
            client = _client()
            slot()
            payload = client.get_historical_candles_v3(key, "days", 1, END, WARMUP)
            wrapped = {"instrument_key": key, "symbol": symbol, "unit": "days", "interval": 1,
                       "from": WARMUP, "to": END, "retrieved_at": pd.Timestamp.now(tz="UTC").isoformat(), "payload": payload}
            dump(path, wrapped)
        frame = _frame(wrapped)
        frame.index = frame.index.normalize()
        frame = frame.loc[(frame.index >= pd.Timestamp(WARMUP, tz=TZ)) & (frame.index <= pd.Timestamp(END, tz=TZ))]
        duplicates = int(frame.index.duplicated().sum())
        frame = frame.loc[~frame.index.duplicated(keep="last")]
        valid = (np.isfinite(frame[["open", "high", "low", "close"]]).all(axis=1) & frame.low.gt(0)
                 & frame.high.ge(frame[["open", "low", "close"]].max(axis=1))
                 & frame.low.le(frame[["open", "high", "close"]].min(axis=1)) & frame.volume.ge(0))
        audit = {"symbol": symbol, "instrument_key": key, "status": "ok", "path": str(path), "sha256": sha(path),
                 "rows": int(valid.sum()), "duplicate_dates": duplicates, "invalid_ohlc_rows": int((~valid).sum()),
                 "invalid_dates": [str(x.date()) for x in frame.index[~valid]],
                 "first": str(frame.index.min()), "last": str(frame.index.max())}
        print(symbol, "READY", int(valid.sum()), flush=True)
        return symbol, frame.loc[valid].copy(), audit
    except Exception as exc:
        audit = {"symbol": symbol, "instrument_key": key, "status": "unavailable", "error_type": type(exc).__name__,
                 "http_status": getattr(exc, "status_code", None)}
        dump(Path(out) / "raw" / symbol / "failure.json", audit)
        print(symbol, "UNAVAILABLE", type(exc).__name__, getattr(exc, "status_code", None), flush=True)
        return symbol, _frame([]), audit


def actions(out):
    """Keep certified 2023+ cache; request earlier actions for indicator warmup."""
    import requests
    source = LEGACY / "nse-actions-all.json"
    records = json.loads(source.read_text(encoding="utf-8"))
    early = Path(out) / "sources" / "nse-actions-2020-2022.json"
    status = {"research_action_source": str(source), "research_action_source_sha256": sha(source)}
    try:
        if not early.exists():
            r = requests.get("https://www.nseindia.com/api/corporates-corporateActions",
                             params={"index": "equities", "from_date": "01-01-2020", "to_date": "31-12-2022"},
                             headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/", "Accept": "application/json"}, timeout=20)
            r.raise_for_status()
            x = r.json()
            assert isinstance(x, list)
            dump(early, x)
        records = json.loads(early.read_text(encoding="utf-8")) + records
        status["warmup_actions"] = {"status": "available", "path": str(early), "sha256": sha(early)}
    except Exception as exc:
        status["warmup_actions"] = {"status": "unavailable", "error_type": type(exc).__name__,
            "policy": "Acquire 2020 prices, but discard pre-2023 signal warmup without complete corporate-action coverage."}
    return records, status


def events_for(spec, records):
    result, seen = [], set()
    symbols = {spec["symbol"], spec["current_symbol"]}
    isins = {spec["isin_at_start"], spec["instrument_key"].split("|")[-1]}
    for r in records:
        if (r.get("symbol") not in symbols and r.get("isin") not in isins) or r.get("series") not in ("EQ", "BE", "BZ"):
            continue
        try: day = pd.to_datetime(r["exDate"], format="%d-%b-%Y").strftime("%Y-%m-%d")
        except (ValueError, KeyError): continue
        subject = r.get("subject", "")
        if not WARMUP <= day <= END or (day, subject) in seen: continue
        seen.add((day, subject))
        lower, factor, dividend, kind = subject.lower(), 1., 0., "other"
        if "bonus" in lower:
            m = re.search(r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)", subject)
            if m: factor = 1 + float(m[1]) / float(m[2]); kind = "split_bonus"
            else: kind = "unresolved_capital_action"
        elif "split" in lower:
            nums = re.findall(r"(?:Rs\.?|Re\.?)\s*(\d+(?:\.\d+)?)", subject, re.I)
            if len(nums) >= 2: factor = float(nums[0]) / float(nums[1]); kind = "split_bonus"
            else: kind = "unresolved_capital_action"
        elif any(w in lower for w in ("demerg", "rights", "scheme", "amalgam", "merger")):
            kind = "unresolved_capital_action"
        elif "dividend" in lower:
            m = re.search(r"(?:Rs\.?|Re\.?)\s*(\d+(?:\.\d+)?)", subject, re.I)
            if m: dividend = float(m[1]); kind = "dividend"
            else: kind = "unresolved_dividend"
        if kind != "other":
            result.append({"date": day, "kind": kind, "factor": factor, "dividend": dividend, "subject": subject})
    return sorted(result, key=lambda x: x["date"])


def adjust_stock(spec, raw, records, warmup_actions_available):
    f = raw.copy()
    events = events_for(spec, records)
    reasons = [e for e in events if e["date"] >= START and (e["kind"].startswith("unresolved") or abs(e["factor"] - round(e["factor"])) > 1e-9)]
    audit = {"symbol": spec["symbol"], "events": events, "exclusion_reasons": reasons, "split_detections": []}
    if not len(f):
        audit["exclusion_reasons"].append({"reason": "daily_data_unavailable"})
        audit["eligible"] = False
        return f, f.copy(), audit
    reset_dates = [e["date"] for e in events if e["date"] < START and e["kind"].startswith("unresolved")]
    if not warmup_actions_available: reset_dates.append("2023-01-01")
    if reset_dates:
        reset = max(reset_dates)
        f = f.loc[f.index >= pd.Timestamp(reset, tz=TZ)].copy()
        audit["warmup_reset"] = reset
    multiplier = pd.Series(1., index=f.index)
    f["unit_factor"], f["split_factor"], f["dividend"] = 1., 1., 0.
    for e in events:
        day = pd.Timestamp(e["date"], tz=TZ)
        before, after = f.index < day, f.index >= day
        on = f.index == day
        if e["kind"] == "split_bonus" and before.any() and after.any():
            factor = e["factor"]
            ratio = float(f.loc[after, "open"].iloc[0] / f.loc[before, "close"].iloc[-1])
            adjusted = abs(np.log(ratio)) < abs(np.log(ratio * factor))
            residual = min(abs(np.log(ratio)), abs(np.log(ratio * factor)))
            if residual > .20 and e["date"] >= START:
                reasons.append({"date": e["date"], "reason": "ambiguous_split_price_basis", "ratio": ratio})
            if adjusted: multiplier.loc[before] *= factor
            f.loc[before, "unit_factor"] *= factor
            if on.any(): f.loc[on, "split_factor"] *= factor
            elif e["date"] >= START: reasons.append({"date": e["date"], "reason": "split_ex_date_missing"})
            audit["split_detections"].append(e | {"observed_open_previous_close_ratio": ratio, "provider_pre_event_adjusted": bool(adjusted), "continuity_log_error": residual})
        elif e["kind"] == "dividend":
            if on.any(): f.loc[on, "dividend"] += e["dividend"]
            elif e["date"] >= START: reasons.append({"date": e["date"], "reason": "dividend_ex_date_missing"})
    for col in ("open", "high", "low", "close"): f[col] *= multiplier
    gap = f.open * f.split_factor / f.close.shift() - 1
    unexplained = gap.abs() > .30
    research_gaps = unexplained & (f.index >= pd.Timestamp(START, tz=TZ))
    if research_gaps.any():
        reasons.append({"reason": "unexplained_overnight_gap_above_30pct", "dates": {str(d.date()): float(v) for d, v in gap[research_gaps].items()}})
    # Unknown warmup discontinuities cannot contaminate long-horizon indicators.
    early_gap = unexplained & (f.index < pd.Timestamp(START, tz=TZ))
    if early_gap.any():
        reset = f.index[early_gap][-1]
        f = f.loc[f.index >= reset]
        audit["warmup_gap_reset"] = str(reset.date())
    neutral = f.copy()
    for col in ("open", "high", "low", "close"): neutral[col] /= f.unit_factor
    audit["eligible"] = not bool(reasons)
    audit["first_usable"] = str(f.index.min())
    audit["last_usable"] = str(f.index.max())
    return f, neutral, audit


def prepare_data(out=DEFAULT_OUT):
    """Return arrays S x T, tz-aware daily calendar, frozen identity and audits."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "daily-panel.npz").exists() and (out / "data-audit.json").exists():
        cached_audit = json.loads((out / "data-audit.json").read_text(encoding="utf-8"))
        if cached_audit.get("panel_schema") == 3:
            idx = json.loads((out / "panel-index.json").read_text(encoding="utf-8"))
            with np.load(out / "daily-panel.npz") as a:
                panel = {k: a[k].copy() for k in ("unit_factor", "split_factor", "dividend", "niftyclose", "eligible", "liquidity_volume", "liquidity_turnover")}
                panel["actual"] = {k: a["actual_" + k].copy() for k in ("open", "high", "low", "close", "volume")}
                panel["neutral"] = {k: a["neutral_" + k].copy() for k in panel["actual"]}
            panel.update(symbols=idx["symbols"], dates=pd.DatetimeIndex(pd.to_datetime(idx["dates"], utc=True)).tz_convert(TZ), sector=idx["sector"], audit=cached_audit)
            panel["median_volume20"] = panel["liquidity_volume"]
            panel["liquidity_value"] = panel["liquidity_turnover"]
            return panel
    u = universe(out)
    records, action_audit = actions(out)
    specs = u["stocks"]
    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        fetched = list(pool.map(lambda x: fetch_one(x, out), specs + [{"symbol": "NIFTY", "instrument_key": "NSE_INDEX|Nifty 50"}]))
    raw = {s: f for s, f, a in fetched}
    acquisitions = {s: a for s, f, a in fetched}
    dump(out / "acquisition-summary.json", {"elapsed_seconds": time.monotonic() - start, "audits": acquisitions})
    dates = raw["NIFTY"].index
    if not len(dates): raise RuntimeError("Nifty daily benchmark unavailable; cannot certify shared calendar")
    assert dates.is_monotonic_increasing and not dates.has_duplicates
    n, t = len(specs), len(dates)
    actual = {c: np.full((n, t), np.nan) for c in ("open", "high", "low", "close", "volume")}
    neutral = {c: np.full((n, t), np.nan) for c in actual}
    unit_factor, split_factor, dividend = np.ones((n, t)), np.ones((n, t)), np.zeros((n, t))
    eligible, dispositions, audits = [], [], {}
    for i, spec in enumerate(specs):
        a, z, audit = adjust_stock(spec, raw[spec["symbol"]], records, action_audit["warmup_actions"]["status"] == "available")
        if len(a):
            for c in actual:
                actual[c][i] = a[c].reindex(dates).to_numpy(float)
                neutral[c][i] = z[c].reindex(dates).to_numpy(float)
            unit_factor[i] = a.unit_factor.reindex(dates).ffill().bfill().to_numpy(float)
            split_factor[i] = a.split_factor.reindex(dates).fillna(1).to_numpy(float)
            dividend[i] = a.dividend.reindex(dates).fillna(0).to_numpy(float)
        # Missing test-period data are retained in universe and excluded explicitly.
        observed = np.isfinite(actual["close"][i])
        test = dates >= pd.Timestamp(START, tz=TZ)
        if observed[test].sum() < 200:
            audit["exclusion_reasons"].append({"reason": "fewer_than_200_research_observations", "observations": int(observed[test].sum())})
            audit["eligible"] = False
        if not observed[-5:].any():
            audit["exclusion_reasons"].append({"reason": "no_executable_terminal_price_in_last_five_sessions"})
            audit["eligible"] = False
        audit["missing_nifty_calendar_sessions"] = [str(d.date()) for d in dates[test & ~observed]]
        if audit["missing_nifty_calendar_sessions"]:
            audit["exclusion_reasons"].append({"reason": "missing_research_calendar_session_conservative_execution_quarantine", "dates": audit["missing_nifty_calendar_sessions"]})
            audit["eligible"] = False
        audit["acquisition"] = acquisitions[spec["symbol"]]
        audits[spec["symbol"]] = audit
        eligible.append(audit["eligible"])
        dispositions.append({"symbol": spec["symbol"], "sector": spec["sector"], "eligible": audit["eligible"],
                             "status": "retained" if audit["eligible"] else "quarantined", "reasons": json.dumps(audit["exclusion_reasons"]),
                             "research_observations": int(observed[test].sum()), "identity_resolution": spec["identity_resolution"]})
    # Execution screens at today's open can use only yesterday and older volume.
    def lag_median(x):
        return pd.DataFrame(x.T).rolling(20, min_periods=20).median().shift(1).to_numpy().T
    # Fixed conservative volume hypothesis: if the provider inversely adjusted
    # volume alongside prices, neutral-price x provider-volume is turnover and
    # division by today's unit scale converts volume into today's share units.
    # If volume is unadjusted, these caps tend to understate pre-split capacity.
    liquidity_volume = lag_median(actual["volume"]) / unit_factor
    liquidity_turnover = lag_median(neutral["close"] * actual["volume"])
    caveats = [u["limitation"], "Historical warmup before 11 Nov 2024 is indicator context only, never a pre-universe performance test.",
               "Provider daily prices are not independently certified as unadjusted: split/bonus continuity detects and reconstructs historical share units; unmodeled capital events and enormous unexplained gaps are quarantined.",
               "Volume adjustment status is not certified. Fixed conservative hypothesis: lagged median(provider volume)/today unit_factor provides today's share capacity, and lagged median(split-neutral close times provider volume) proxies turnover. This assumes inverse price-volume adjustment; if volume is unadjusted, historical pre-split capacity is generally understated. No official historical rupee turnover or spread is available.",
               "Nifty provider sessions define the shared daily calendar including observed special/Muhurat sessions. Whole-day calendar is not independently certified against every NSE holiday circular.",
               "No OHLC forward fill. Current instrument master is used only for company identity; delisted/unresolved starting names remain in dispositions, preventing silent membership substitution."]
    caveats.append("Any missing research-period Nifty-calendar candle quarantines the whole stock before performance analysis because protective execution cannot be certified. This conservative completeness selection can favor surviving/data-complete companies; exclusions and starting membership are fully retained, and results do not establish returns for every historical Nifty 500 stock.")
    audit = {"panel_schema": 3, "universe": {k: v for k, v in u.items() if k != "stocks"}, "actions": action_audit,
             "stocks": len(specs), "eligible_stocks": int(sum(eligible)), "quarantined_stocks": int(n - sum(eligible)),
             "sessions": t, "first": str(dates.min()), "last": str(dates.max()), "research_start": START,
             "price_basis": "actual contemporaneous units reconstructed from known split/bonus; neutral=actual/unit_factor",
             "liquidity_basis": "Both arrays at entry t use completed observations through t-1; share volume already converted with unit_factor[t], never multiply again by split_factor[t]. Turnover uses neutral.close times provider volume under a fixed inverse-adjustment hypothesis.", "caveats": caveats,
             "stock_audits": audits}
    dump(out / "data-audit.json", audit)
    pd.DataFrame(dispositions).to_csv(out / "universe-dispositions.csv", index=False)
    dump(out / "raw-fingerprints.json", acquisitions)
    panel = {"symbols": [s["symbol"] for s in specs], "dates": dates, "actual": actual, "neutral": neutral,
             "unit_factor": unit_factor, "split_factor": split_factor, "dividend": dividend,
             "niftyclose": raw["NIFTY"].close.reindex(dates).to_numpy(float), "sector": [s["sector"] for s in specs],
             "eligible": np.asarray(eligible, dtype=bool), "liquidity_volume": liquidity_volume,
             "liquidity_turnover": liquidity_turnover, "audit": audit}
    panel["median_volume20"] = liquidity_volume
    panel["liquidity_value"] = liquidity_turnover
    arrays = {f"actual_{k}": v for k, v in actual.items()} | {f"neutral_{k}": v for k, v in neutral.items()}
    arrays.update(unit_factor=unit_factor, split_factor=split_factor, dividend=dividend, niftyclose=panel["niftyclose"],
                  eligible=panel["eligible"], liquidity_volume=liquidity_volume, liquidity_turnover=liquidity_turnover)
    np.savez_compressed(out / "daily-panel.npz", **arrays)
    dump(out / "panel-index.json", {"symbols": panel["symbols"], "dates": [str(d) for d in dates], "sector": panel["sector"]})
    print("PANEL READY", n, t, "eligible", sum(eligible), flush=True)
    return panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    prepare_data(args.out)
