"""Phase 8 Priority A (prospective): NSE pre-open auction / opening execution evidence. READ-ONLY - no order capability.

Rules in force (since 2026-09-07; secondary sources - NSE primary page not retrievable, see AUCTION_EXECUTION_VALIDATION.md):
  09:00-09:05 market + limit orders; 09:05-close limit orders only; random close 09:08-09:10; matching 09:10-09:12;
  transition 09:12-09:15; normal market 09:15. Equilibrium = max matched qty -> min imbalance -> closest to prev close.
  Market orders matched first. Unmatched orders move to the normal market at their own limit price.

Modes
  session [--date YYYY-MM-DD]   (start ~08:58 IST on a trading day) timestamped v3 quote snapshots on SCHEDULE for the
                                instruments in orders/<date>.json + holdings + universe; then intraday 1-minute candles for
                                order instruments. Raw payloads gzip + sha256 + manifest. Never fills gaps.
  evaluate --date YYYY-MM-DD    (next morning) per-order execution evidence for orders planned for that date, appended
                                idempotently to execution_evidence.jsonl.
Observation vs assumption: each evidence record has 'observed' (raw fields), 'estimates' (statistical, labelled) and
'classification' (rule-based, labelled ASSUMPTION). A classification is never a fill.
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

import p8common as P
from ops import Ops, atomic_write

CAP_DIR = P.OUT / "capture"
ORD_DIR = P.OUT / "paper" / "orders"
EVID = P.OUT / "execution_evidence.jsonl"
SCHEDULE = ["09:00:30", "09:02:00", "09:03:30", "09:04:30", "09:06:00", "09:07:30", "09:09:00", "09:11:00",
            "09:12:30", "09:14:00", "09:15:30", "09:20:00", "09:30:00", "09:45:30"]
DECISION_MARKET = "09:05:00"     # last moment to enter a pre-open MARKET order
DECISION_LIMIT = "09:08:00"      # earliest possible random close of pre-open order entry
POST_MATCH = "09:12:00"
STALE_SECONDS = 120
FIELDS = ["indicative_equilibrium_price", "indicative_equilibrium_quantity", "indicative_imbalance_quantity_total",
          "indicative_imbalance_quantity_market", "total_buy_quantity", "total_sell_quantity", "last_price", "volume",
          "reference_price", "prev_close_price", "cas_eligible", "timestamp", "last_trade_time", "ohlc", "depth"]


# ------------------------------------------------------------------ HTTP (read-only)
def _hdr():
    sys.path.insert(0, str(P.ROOT / "swing_mtf"))
    import data as D
    return {"Accept": "application/json", "Authorization": f"Bearer {D._token_cached()}"}


def http_get(url, params=None, timeout=20, session=None):
    import requests
    s = session or requests
    return s.get(url, headers=_hdr(), params=params, timeout=timeout)


def snapshot(keys, label, day_dir: Path, ops: Ops, getter=http_get):
    """One timestamped v3 full-quote snapshot. Failures are recorded, never filled."""
    day_dir.mkdir(parents=True, exist_ok=True)
    parts, ok = [], True
    for i in range(0, len(keys), 400):
        sent = dt.datetime.now().isoformat(timespec="milliseconds")
        try:
            r = getter("https://api.upstox.com/v3/market-quote/quotes", params={"instrument_key": ",".join(keys[i:i + 400])})
            body, status = r.text, r.status_code
        except Exception as e:  # unavailable API / network
            body, status, ok = json.dumps({"error": type(e).__name__, "detail": str(e)[:200]}), -1, False
        parts.append({"sent_at": sent, "received_at": dt.datetime.now().isoformat(timespec="milliseconds"),
                      "status": status, "n_keys": len(keys[i:i + 400]), "body": body})
        if status != 200:
            ok = False
    raw = json.dumps({"label": label, "parts": parts}).encode()
    fn = day_dir / f"snap_{label.replace(':', '')}.json.gz"
    with gzip.open(fn, "wb") as f:
        f.write(raw)
    man = {"file": fn.name, "label": label, "sha256": P.sha(raw), "parts": [{k: v for k, v in p.items() if k != "body"} for p in parts],
           "ok": ok}
    with (day_dir / "manifest.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(man) + "\n")
    if not ok:
        ops.alert("quote_snapshot_failed", f"snapshot {label} incomplete (statuses {[p['status'] for p in parts]})",
                  severity="WARN", label=label)
    return man


def parse_snapshot(fn: Path):
    """{instrument_key: {field: value}} plus capture time, from a stored raw snapshot."""
    js = json.loads(gzip.open(fn, "rb").read())
    out, t_recv = {}, None
    for p in js["parts"]:
        t_recv = p["received_at"]
        if p["status"] != 200:
            continue
        data = (json.loads(p["body"]).get("data") or {})
        for _, q in data.items():
            k = q.get("instrument_token")
            out[k] = {f: q.get(f) for f in FIELDS}
            out[k]["_received_at"] = p["received_at"]
    return js["label"], t_recv, out


def verify_manifest(day_dir: Path):
    bad = []
    for line in (day_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines():
        m = json.loads(line)
        raw = gzip.open(day_dir / m["file"], "rb").read()
        if P.sha(raw) != m["sha256"]:
            bad.append(m["file"])
    return bad


# ------------------------------------------------------------------ classification (pure; unit-tested)
def best_quotes(depth):
    if not depth:
        return None, None
    b = [x for x in depth.get("buy") or [] if (x.get("price") or 0) > 0]
    s = [x for x in depth.get("sell") or [] if (x.get("price") or 0) > 0]
    return (b[0]["price"] if b else None), (s[0]["price"] if s else None)


def is_stale(q, captured_at: str, max_age=STALE_SECONDS):
    ts = q.get("timestamp")
    if not ts:
        return True
    try:
        a = pd.Timestamp(ts).tz_localize(None) if pd.Timestamp(ts).tzinfo is None else pd.Timestamp(ts).tz_convert("Asia/Kolkata").tz_localize(None)
        b = pd.Timestamp(captured_at)
        return abs((b - a).total_seconds()) > max_age
    except Exception:
        return True


def classify_auction(qty, dec, final, captured_at_dec=None, part_likely=0.10):
    """ASSUMPTION-based classification of a pre-open MARKET order of `qty` shares submitted before 09:05.
    dec  : quote fields at the market-order decision point (last snapshot <= 09:05:00) or None
    final: quote fields after matching (first snapshot >= 09:12:00) or None
    Returns (status, reasons). Status in: unobserved, stale_quote, no_auction_indicated, uncertain_market_imbalance,
    uncertain_size, no_auction_final, likely."""
    if dec is None:
        return "unobserved", ["no snapshot before the market-order cutoff"]
    if captured_at_dec and is_stale(dec, captured_at_dec):
        return "stale_quote", ["decision-point quote timestamp older than %ds" % STALE_SECONDS]
    iep, ieq = dec.get("indicative_equilibrium_price") or 0, dec.get("indicative_equilibrium_quantity") or 0
    if iep <= 0 or ieq <= 0:
        return "no_auction_indicated", ["indicative equilibrium price/quantity absent or zero"]
    imb_m = dec.get("indicative_imbalance_quantity_market")
    if imb_m is None:
        return "uncertain_market_imbalance", ["market-order imbalance field missing"]
    if imb_m != 0:
        return "uncertain_market_imbalance", ["unmatched market-order quantity %s (sign convention unverified)" % imb_m]
    if qty > part_likely * ieq:
        return "uncertain_size", [f"order {qty} > {part_likely:.0%} of indicative matched quantity {ieq}"]
    if final is not None:
        fv = final.get("volume") or 0
        if fv <= 0:
            return "no_auction_final", ["no matched volume after the auction"]
        if qty > part_likely * fv:
            return "uncertain_size", [f"order {qty} > {part_likely:.0%} of final matched volume {fv}"]
    return "likely", ["small vs indicative matched quantity, no market-order imbalance" + ("" if final else "; final volume unobserved")]


# ------------------------------------------------------------------ session mode
def instrument_list(date: str, ops: Ops):
    keys = set()
    f = ORD_DIR / f"{date}.json"
    if f.exists():
        js = json.loads(f.read_text(encoding="utf-8"))
        keys |= set(js.get("capture_instruments", []))
    else:
        ops.alert("no_orders_file", f"orders file for {date} missing; capturing the universe only", date=date)
    if not keys or len(keys) < 50:
        I = P.C.inputs_fixed()
        U = I["U"][-1]
        keys |= set(np.array(I["d"].keys).astype(str)[U])
    return sorted(keys)


def trading_holidays(ops: Ops):
    """Holiday list from the paper pipeline's cache, else the API; failure -> weekday calendar with an alert."""
    cache = P.OUT / "paper" / "ops" / "holidays_cache.json"
    if cache.exists():
        return set(json.loads(cache.read_text(encoding="utf-8"))["holidays"])
    try:
        import paper8
        return set(paper8._upstox_holidays())
    except Exception as e:
        ops.alert("calendar_api_unavailable", f"capture: holiday list unavailable ({type(e).__name__}); weekday calendar used")
        return set()


def run_session(date: str | None = None, sleep=time.sleep, clock=dt.datetime.now, getter=http_get, holidays=None):
    ops = Ops(P.OUT)
    date = date or clock().strftime("%Y-%m-%d")
    if pd.Timestamp(date) > P.WINDOW_END:
        ops.alert("window_closed", "research window ends 2026-12-31: capture refused", severity="INFO")
        return None
    hol = trading_holidays(ops) if holidays is None else set(holidays)
    if pd.Timestamp(date).weekday() >= 5 or date in hol:
        print(f"{date} is not a trading session: no capture")
        return None
    with ops.lock(f"capture_{date}") as L:
        if not L.acquired:
            return None
        day_dir = CAP_DIR / date
        if (day_dir / "manifest.jsonl").exists():
            done = {json.loads(x)["label"] for x in (day_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines()}
        else:
            done = set()
        keys = instrument_list(date, ops)
        for lab in SCHEDULE:
            if lab in done:
                continue  # replay after interruption: never duplicate a snapshot
            target = dt.datetime.combine(pd.Timestamp(date).date(), dt.time.fromisoformat(lab))
            wait = (target - clock()).total_seconds()
            if wait < -90:
                ops.alert("snapshot_missed", f"snapshot {lab} missed (started late)", severity="INFO", label=lab)
                continue
            if wait > 0:
                sleep(wait)
            snapshot(keys, lab, day_dir, ops, getter)
        # intraday 1-minute candles for order instruments (raw evidence before any vendor revision)
        f = ORD_DIR / f"{date}.json"
        order_keys = sorted(json.loads(f.read_text(encoding="utf-8")).get("order_instruments", [])) if f.exists() else []
        raw = {}
        for k in order_keys:
            try:
                import urllib.parse
                r = getter(f"https://api.upstox.com/v3/historical-candle/intraday/{urllib.parse.quote(k, safe='')}/minutes/1")
                raw[k] = {"status": r.status_code, "body": r.text}
            except Exception as e:
                raw[k] = {"status": -1, "error": str(e)[:200]}
        if order_keys:
            b = json.dumps(raw).encode()
            with gzip.open(day_dir / "intraday_1min_0946.json.gz", "wb") as fz:
                fz.write(b)
            with (day_dir / "manifest.jsonl").open("a", encoding="utf-8") as fm:
                fm.write(json.dumps({"file": "intraday_1min_0946.json.gz", "label": "intraday_1min", "sha256": P.sha(b), "ok": True}) + "\n")
        return day_dir


# ------------------------------------------------------------------ evaluate mode
def _minutes(key, date):
    con = P.CDB._con(read_only=True)
    df = con.execute("""SELECT ts, open, high, low, close, volume FROM candles WHERE instrument_key=? AND interval='1minute'
                        AND CAST(ts AS DATE) = CAST(? AS DATE) ORDER BY ts""", [key, date]).df()
    day = con.execute("""SELECT open, high, low, close, volume FROM candles WHERE instrument_key=? AND interval='1day'
                         AND CAST(ts AS DATE) = CAST(? AS DATE)""", [key, date]).df()
    con.close()
    return df, day


def ensure_minutes(keys, date):
    """Fetch (DB-first) the day's historical 1-minute bars for order instruments."""
    sys.path.insert(0, str(P.ROOT / "swing_mtf"))
    import data as D
    con = P.CDB._con(read_only=True)
    have = set(con.execute("""SELECT DISTINCT instrument_key FROM candles WHERE interval='1minute' AND CAST(ts AS DATE)=CAST(? AS DATE)""",
                           [date]).df().instrument_key)
    con.close()
    d = pd.Timestamp(date).date()
    for k in keys:
        if k in have:
            continue
        rows, sc = D._get(k, "minutes", 1, d, d)
        if rows:
            P.CDB.write(k, "1minute", D._to_frame(rows))


def evaluate(date: str):
    ops = Ops(P.OUT)
    f = ORD_DIR / f"{date}.json"
    if not f.exists():
        ops.alert("evaluate_no_orders", f"no orders file for {date}: nothing to evaluate", severity="INFO", date=date)
        return []
    orders = json.loads(f.read_text(encoding="utf-8"))
    day_dir = CAP_DIR / date
    snaps = {}
    if (day_dir / "manifest.jsonl").exists():
        bad = verify_manifest(day_dir)
        if bad:
            ops.alert("capture_checksum_mismatch", f"raw snapshot files fail their checksum: {bad}", severity="ERROR", date=date)
        for fn in sorted(day_dir.glob("snap_*.json.gz")):
            lab, t_recv, data = parse_snapshot(fn)
            snaps[lab] = (t_recv, data)
    else:
        ops.alert("auction_data_unavailable", f"no pre-open/opening snapshots captured for {date}", severity="WARN", date=date)
    keys = sorted({o["key"] for o in orders["orders"]})
    try:
        ensure_minutes(keys, date)
    except Exception as e:
        ops.alert("minute_data_unavailable", f"1-minute bars for {date} could not be fetched: {e}", date=date)
    have = set()
    if EVID.exists():
        have = {json.loads(x)["id"] for x in EVID.read_text(encoding="utf-8").splitlines() if x.strip()}
    labs_dec = [l for l in sorted(snaps) if l <= DECISION_MARKET]
    labs_lim = [l for l in sorted(snaps) if l <= DECISION_LIMIT]
    labs_fin = [l for l in sorted(snaps) if POST_MATCH <= l < "09:15:00"]
    lab_915 = "09:15:30" if "09:15:30" in snaps else None
    new = []
    for o in orders["orders"]:
        rid = f"{date}|{o['strategy']}|{o.get('book', '')}|{o['key']}|{o['side']}"
        if rid in have:
            continue
        k, q = o["key"], o.get("qty") or 0
        dec = snaps[labs_dec[-1]][1].get(k) if labs_dec else None
        lim = snaps[labs_lim[-1]][1].get(k) if labs_lim else None
        fin = snaps[labs_fin[0]][1].get(k) if labs_fin else None
        q915 = snaps[lab_915][1].get(k) if lab_915 else None
        mn, day = _minutes(k, date)
        observed = {"decision_market_snapshot": labs_dec[-1] if labs_dec else None,
                    "at_market_cutoff": {f: dec.get(f) for f in FIELDS if f != "depth"} if dec else None,
                    "at_limit_cutoff": {f: lim.get(f) for f in FIELDS if f != "depth"} if lim else None,
                    "post_match": {f: fin.get(f) for f in FIELDS if f != "depth"} if fin else None,
                    "official_open": float(day.open.iloc[0]) if len(day) else None,
                    "first_traded_price": float(mn.open.iloc[0]) if len(mn) else None,
                    "first_bar_time": str(mn.ts.iloc[0]) if len(mn) else None}
        if q915:
            b, a = best_quotes(q915.get("depth"))
            observed["quote_0915_30"] = {"bid": b, "ask": a, "spread_bp_MEASURED": (a - b) / ((a + b) / 2) * 1e4 if a and b else None,
                                         "timestamp": q915.get("timestamp")}
        est = {}
        if len(mn):
            mins = ((mn.ts - mn.ts.dt.normalize()).dt.total_seconds() / 60 - 555).values
            tp = ((mn.high + mn.low + mn.close) / 3).values
            v = mn.volume.values.astype(float)
            for w in (5, 15, 30):
                kk = mins < w
                observed[f"volume_first{w}"] = float(v[kk].sum())
                observed[f"vwap_first{w}"] = float((tp[kk] * v[kk]).sum() / v[kk].sum()) if v[kk].sum() > 0 else None
            for n in (5, 15, 30, 60):
                kk = np.flatnonzero(mins == n)
                est[f"delay{n}_bar_open"] = float(mn.open.values[kk[0]]) if len(kk) else None
            v0, v1 = (v[0], v[1]) if len(v) > 1 else (v[0], 0.0)
            est["auction_qty_bounds_from_0915_bar_ESTIMATE"] = {"upper": float(v0), "central": float(max(0, v0 - v1)), "lower": float(max(0, v0 - 2 * v1))}
        status, why = classify_auction(q, dec, fin, snaps[labs_dec[-1]][0] if labs_dec else None)
        dec_px = o.get("ref_price")
        sg = 1.0 if o["side"] == "BUY" else -1.0
        if observed["official_open"] and dec_px:
            est["gap_vs_decision_close_bp"] = sg * (observed["official_open"] / dec_px - 1) * 1e4
        rec = {"id": rid, "date": date, "strategy": o["strategy"], "book": o.get("book"), "key": k, "side": o["side"],
               "intended_qty": q, "ref_price_decision_close": dec_px, "observed": observed, "estimates": est,
               "classification_ASSUMPTION": {"auction_market_order": status, "reasons": why,
                                             "rule": "likely iff IEP/IEQ>0 at 09:05 cutoff, no market imbalance, qty<=10% of IEQ and of final volume"},
               "recorded_at": dt.datetime.now().isoformat(timespec="seconds")}
        rec["hash"] = P.sha_obj({k2: v2 for k2, v2 in rec.items() if k2 != "recorded_at"})
        new.append(rec)
    with EVID.open("a", encoding="utf-8") as fo:
        for r in new:
            fo.write(json.dumps(r, default=str) + "\n")
    return new


def evidence_status(date: str, key: str, side: str, strategy="C0_R"):
    if not EVID.exists():
        return None
    for x in EVID.read_text(encoding="utf-8").splitlines():
        r = json.loads(x)
        if r["date"] == date and r["key"] == key and r["side"] == side and r["strategy"] == strategy:
            return r["classification_ASSUMPTION"]["auction_market_order"]
    return None


if __name__ == "__main__":
    args = sys.argv[1:]
    dd = args[args.index("--date") + 1] if "--date" in args else None
    if args and args[0] == "session":
        print(run_session(dd))
    elif args and args[0] == "evaluate":
        if not dd:
            sys.exit("evaluate needs --date YYYY-MM-DD")
        print(len(evaluate(dd)), "evidence records appended")
    else:
        sys.exit(__doc__)
