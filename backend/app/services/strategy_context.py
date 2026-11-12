"""Causal market adapters for the directional strategy assessment engine.

The five-minute definitions intentionally match research_directional_lab.py.
Daily dashboard technicals are audited but never substituted for intraday bars.
"""
from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

IST = ZoneInfo("Asia/Kolkata")
FAMILIES = ("ema_trend", "failed_breakout", "pullback", "donchian", "momentum",
            "compression", "orb", "ema_reversion", "gap_continuation", "gap_fade", "rsi_reversion")


def timestamp(value):
    try:
        stamp = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return stamp.astimezone(timezone.utc) if stamp.tzinfo else None
    except (ValueError, TypeError, OverflowError):
        return None


def number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError, OverflowError):
        return None


def factor(key, label, group, signal=None, *, available=True, reliability=1., reason="", **extra):
    return {"id": key, "label": label, "group": group,
            "signal": max(-1., min(1., signal)) if signal is not None else None,
            "available": bool(available and signal is not None),
            "reliability": reliability if available and signal is not None else 0.,
            "measurement_reliability": 1. if available and signal is not None else 0.,
            "reason": reason, "source": None, "reported_at": None, **extra}


def candle_factors(candles, at, source="Retained NIFTY five-minute candles"):
    """Use only closed regular-session bars; reject ambiguous clocks and OHLC.

    This is a current-context adapter, not a historical availability replay.
    Historical candles lack first-receipt/revision vintages; caller discloses it.
    """
    at = timestamp(at)
    if at is None:
        raise ValueError("A timezone-aware decision timestamp is required")
    base = {"regime": "unknown", "spot": None, "atr": None, "bar_at": None,
            "session_phase": "unknown", "fresh": False, "errors": []}
    ids = [("ema_trend", "EMA12/26 alignment", "price"), ("ema_alignment", "EMA9/21 alignment", "price"), ("momentum", "Three-bar momentum", "price"),
           ("structure", "Six-bar price structure", "price"), ("rsi", "RSI14 reversal pressure", "price"),
           ("extension", "Distance from EMA21", "price"), ("regime_trend", "Trend versus range regime", "regime"),
           ("volatility", "ATR versus preceding volatility baseline", "regime")]
    out = {key: factor(key, label, group, reason="Insufficient valid completed five-minute history") for key, label, group in ids}
    for family in FAMILIES:
        key = "setup_" + family
        out[key] = factor(key, family.replace("_", " ").title() + " setup", "price",
                          reason="Insufficient valid completed five-minute history", value={"triggered": False})
    try:
        d = pd.DataFrame(candles)
        if d.empty or not {"ts", "open", "high", "low", "close"}.issubset(d):
            return out, base
        # Reject naive timestamps rather than let pandas silently assume UTC.
        if any(timestamp(v) is None for v in d.ts):
            raise ValueError("Undated or timezone-naive candle timestamp")
        d["ts"] = pd.to_datetime(d.ts, utc=True).dt.tz_convert(IST)
        d = d[d.ts + pd.Timedelta(minutes=5) <= at].sort_values("ts", kind="stable").copy()
        if d.empty:
            return out, base
        for col in ("open", "high", "low", "close"):
            d[col] = pd.to_numeric(d[col], errors="coerce")
        if (d.groupby("ts")[["open", "high", "low", "close"]].nunique(dropna=False) > 1).any().any():
            raise ValueError("Conflicting duplicate candles")
        if ((d.ts.dt.minute % 5 != 0) | (d.ts.dt.second != 0) | (d.ts.dt.microsecond != 0)).any():
            raise ValueError("Misaligned five-minute candle clock")
        d = d.drop_duplicates("ts")
        minute = d.ts.dt.hour * 60 + d.ts.dt.minute
        d = d[(minute >= 555) & (minute < 910)].copy()
        valid = d[["open", "high", "low", "close"]].map(lambda v: number(v) is not None).all(axis=1)
        valid &= (d.low > 0) & (d.high >= d[["open", "close", "low"]].max(axis=1)) & (d.low <= d[["open", "close", "high"]].min(axis=1))
        if not valid.all():
            raise ValueError("Invalid OHLC values in context")
        d["day"] = d.ts.dt.strftime("%Y-%m-%d")
        # Prior sessions must be complete research sessions; current session only
        # needs bars observed so far, never future end-of-day completeness.
        today = at.astimezone(IST).date().isoformat()
        complete = [day for day, g in d.groupby("day") if day == today or
                    list(g.ts.dt.hour * 60 + g.ts.dt.minute) == list(range(555, 910, 5))]
        d = d[d.day.isin(complete)].reset_index(drop=True)
        if len(d) < 40:
            return out, base
        g = d.groupby("day")
        previous = g.close.shift()
        tr = pd.concat([d.high-d.low, (d.high-previous).abs(), (d.low-previous).abs()], axis=1).max(axis=1)
        d["atr"] = tr.shift().rolling(14, min_periods=14).mean()
        d["vol_ratio"] = d.atr / d.atr.shift().rolling(200, min_periods=100).median()
        delta = g.close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        d["rsi"] = 100*gain/(gain+loss)
        for length in (9, 12, 21, 26):
            d[f"ema{length}"] = d.close.ewm(span=length, adjust=False).mean()
        d["ret3"] = g.close.diff(3)/d.atr
        for length in (6, 20):
            d[f"high{length}"] = g.high.transform(lambda s: s.shift().rolling(length, min_periods=length).max())
            d[f"low{length}"] = g.low.transform(lambda s: s.shift().rolling(length, min_periods=length).min())
        d["efficiency"] = g.close.diff(12).abs()/delta.abs().groupby(d.day).transform(lambda s: s.rolling(12, min_periods=12).sum())
        d["trend"] = (d.ema9-d.ema21)/d.atr
        d["distance"] = (d.close-d.ema21)/d.atr
        prior_close = g.close.last().shift()
        d["gap"] = (g.open.transform("first")-d.day.map(prior_close))/d.atr
        r = d.iloc[-1]
        bar_at = r.ts.to_pydatetime() + timedelta(minutes=5)
        current = d[d.day == r.day]
        contiguous = current.ts.diff().dropna().eq(pd.Timedelta(minutes=5)).all()
        starts_open = current.ts.iloc[0].hour * 60 + current.ts.iloc[0].minute == 555
        fresh = r.day == today and 0 <= (at-bar_at).total_seconds() <= 360
        common_ok = bool(contiguous and starts_open and fresh and number(r.atr) is not None and r.atr > 0)
        common_reason = ("Latest completed bar; contiguous current-session history from 09:15" if common_ok else
                         "Stale signal bar or missing current-session bars from 09:15")
        meta = {"source": source, "reported_at": bar_at.isoformat(), "observed_at": at.isoformat(), "ttl_seconds": 360,
                "measurement_basis": "Completed five-minute OHLC; first-receipt vintages unavailable"}
        atr = number(r.atr)
        if not atr or atr <= 0:
            return out, base
        trend = bool(r.efficiency >= .35 and abs(r.trend) >= .5)
        ranging = bool(r.efficiency < .25)
        base.update(regime=("uptrend" if r.trend > 0 else "downtrend") if trend else "range" if ranging else "transition",
                    spot=float(r.close), atr=atr, bar_at=bar_at.isoformat(), fresh=fresh,
                    efficiency=number(r.efficiency), volatility_ratio=number(r.vol_ratio),
                    current_session_complete_so_far=bool(contiguous and starts_open))
        def put(key, signal, value, reason, available=True):
            prior = out[key]
            out[key] = factor(key, prior["label"], prior["group"], number(signal), available=common_ok and available,
                              reason=reason+". "+common_reason, value=value, **meta)
        put("ema_trend", (r.ema12-r.ema26)/atr, {"fast": float(r.ema12), "slow": float(r.ema26)}, "EMA12−EMA26 divided by ATR; shared price information")
        put("ema_alignment", r.trend, {"fast": float(r.ema9), "slow": float(r.ema21)}, "EMA9−EMA21 divided by ATR; exact pullback/ORB alignment timeframe")
        put("momentum", r.ret3, number(r.ret3), "Three completed bars' close change divided by ATR")
        structure = 1 if r.close > r.high6 else -1 if r.close < r.low6 else 0
        put("structure", structure, {"high": number(r.high6), "low": number(r.low6)}, "Close beyond preceding six-bar extrema", number(r.high6) is not None)
        put("rsi", (50-r.rsi)/50, number(r.rsi), "Contrarian RSI pressure; not evidence of a reversal by itself", number(r.rsi) is not None)
        put("extension", -r.distance/2, number(r.distance), "Contrarian distance from EMA21 in ATR units")
        put("regime_trend", 1 if trend else -1 if ranging else 0, {"efficiency": number(r.efficiency), "trend_atr": number(r.trend)}, "Trend: efficiency ≥0.35 and |EMA9−EMA21|/ATR ≥0.5; range: efficiency <0.25", number(r.efficiency) is not None)
        put("volatility", (r.vol_ratio-1.2)/1.2, number(r.vol_ratio), "Current lagged ATR relative to prior 200-bar median; normal <1.2, high ≥1.2", number(r.vol_ratio) is not None)
        minute = r.ts.hour*60+r.ts.minute
        morning, afternoon = 570 <= minute < 660, minute >= 780
        exit_ok = minute+5+60 <= 910
        all_window = minute >= 570
        ema_side = 1 if r.trend > 0 else -1 if r.trend < 0 else 0
        def side(long, short):
            return 1 if long and not short else -1 if short and not long else 0
        opening = current[current.ts.dt.hour*60+current.ts.dt.minute < 570]
        orb_ok = len(opening) == 3 and minute >= 570
        orb_hi, orb_lo = (opening.high.max(), opening.low.min()) if orb_ok else (math.nan, math.nan)
        setups = {
            "ema_trend": (side((r.ema12-r.ema26)/atr > .5, (r.ema12-r.ema26)/atr < -.5), trend, afternoon),
            "failed_breakout": (side(r.low < r.low20 and r.close > r.low20 and r.close > r.open, r.high > r.high20 and r.close < r.high20 and r.close < r.open), ranging, all_window),
            "pullback": (side(r.ema9 > r.ema21 and r.low <= r.ema9+.75*atr and r.close > r.ema9 and r.close > r.open, r.ema9 < r.ema21 and r.high >= r.ema9-.75*atr and r.close < r.ema9 and r.close < r.open), True, afternoon),
            "donchian": (side(r.close > r.high6, r.close < r.low6), trend, afternoon),
            "momentum": (side(r.ret3 > .5, r.ret3 < -.5), bool(r.vol_ratio < 1.2), morning),
            "compression": (side((r.high6-r.low6)/atr < 3 and r.close > r.high6 and (r.close-r.open)/atr > 1, (r.high6-r.low6)/atr < 3 and r.close < r.low6 and (r.close-r.open)/atr < -1), trend, afternoon),
            "orb": (side(r.close > orb_hi+.25*atr, r.close < orb_lo-.25*atr), True, afternoon),
            "ema_reversion": (side(r.distance < -2, r.distance > 2), ranging, morning),
            "gap_continuation": (side(r.gap > 3 and minute < 660, r.gap < -3 and minute < 660), bool(r.vol_ratio >= 1.2), all_window),
            "gap_fade": (side(r.gap < -3 and minute < 660, r.gap > 3 and minute < 660), ranging, all_window),
            "rsi_reversion": (side(r.rsi < 40 and r.distance < 0, r.rsi > 60 and r.distance > 0), ranging, morning),
        }
        for family, (direction, filter_ok, window_ok) in setups.items():
            if family in {"pullback", "orb"}:
                filter_ok = bool(direction and direction == ema_side)
            failed = []
            if not direction: failed.append("No completed-bar setup geometry")
            if not filter_ok: failed.append("Required strategy regime/alignment filter not met")
            if not window_ok: failed.append("Outside the configuration's signal-bar time window")
            if not exit_ok: failed.append("60-minute holding horizon exceeds 15:10 research cutoff")
            if not common_ok: failed.append(common_reason)
            put("setup_"+family, direction, {"triggered": bool(direction and filter_ok and window_ok and exit_ok and common_ok),
                "direction": direction, "geometry_triggered": bool(direction), "hard_filter_passed": bool(filter_ok),
                "failed_requirements": failed}, "; ".join(failed) if failed else "All frozen configuration prerequisites met")
        return out, base
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        base["errors"].append(str(exc))
        return out, base


def dashboard_factors(dashboard, at, spot=None, atr=None):
    """Audit every input and transform only interpretable, dated observations."""
    at = timestamp(at)
    rows = {f["id"]: f for section in dashboard.get("sections", []) for f in section.get("factors", [])}
    audit, signals = [], {}
    used = set()
    def observation(key, max_age=900):
        r = rows.get(key, {})
        pub, received = timestamp(r.get("reported_at")), timestamp(r.get("observed_at"))
        ok = bool(r.get("status") == "available" and pub and received and pub <= at and received <= at
                  and (at-pub).total_seconds() <= max_age and not r.get("quality_note") and r.get("source"))
        if r.get("section_id") == "derivatives_options" or key in {"pcr", "max_pain", "call_oi", "put_oi", "call_oi_change", "put_oi_change"}:
            expiry = timestamp(str(r.get("expiry"))+"T15:30:00+05:30")
            ok = bool(ok and expiry and expiry > at)
        return r, ok
    def add(key, label, members, signal, reason, value=None, group="context", max_age=900, reliability=1.):
        observed = [observation(member, max_age) for member in members]
        ok = all(valid for _, valid in observed)
        used.update(members)
        meta = observed[0][0] if observed else {}
        signals[key] = factor(key, label, group, number(signal), available=ok, reliability=reliability,
            value=value, reason=reason+("" if ok else "; missing, stale, undated, future, or quality-rejected source"),
            source=meta.get("source"), reported_at=meta.get("reported_at"), observed_at=meta.get("observed_at"),
            expiry=meta.get("expiry"), ttl_seconds=max_age)
    mp, _ = observation("max_pain")
    exp = timestamp(str(mp.get("expiry"))+"T15:30:00+05:30")
    dte = (exp-at).total_seconds()/86400 if exp else None
    mp_value = number(mp.get("value"))
    # Duration relevance is explicit: pinning is an expiry hypothesis. A raw
    # payout minimum has no validated directional predictive performance here.
    mp_signal = (mp_value-spot)/atr if mp_value and spot and atr else None
    add("max_pain", "Max Pain expiry alignment", ["max_pain"], mp_signal,
        "Direction toward the payout minimum is a hypothesis; prior incremental tests failed. Expiry-distance relevance retained in value; no learned edge assumed",
        {"max_pain": mp_value, "spot": spot, "dte": dte, "expiry_relevance": 1/(1+dte) if dte is not None and dte >= 0 else 0}, group="positioning", reliability=0.)
    signals["max_pain"]["relevance_multiplier"] = min(1., 60/(dte*1440)) if dte is not None and dte > 0 else 0.
    pcr, _ = observation("pcr")
    p = number(pcr.get("value"))
    add("pcr", "OI put/call positioning", ["pcr"], (p-1)/(p+1) if p is not None and p >= 0 else None,
        "OI ratio alone does not identify buyers versus writers or a reliable bullish direction; prior incremental tests failed", p, group="positioning", reliability=0.)
    call, _ = observation("call_oi_change"); put, _ = observation("put_oi_change")
    c, p = number(call.get("value")), number(put.get("value"))
    same_expiry = call.get("expiry") and call.get("expiry") == put.get("expiry")
    balance = (p-c)/(abs(p)+abs(c)) if same_expiry and p is not None and c is not None and abs(p)+abs(c) > 0 else None
    add("oi_balance", "Matched-expiry OI change balance", ["call_oi_change", "put_oi_change"], balance,
        "Put-versus-call OI change descriptor; requires identical expiry. Trade initiation and historical incremental edge unverified", {"call_change": c, "put_change": p}, group="positioning", reliability=0.)
    calls, _ = observation("call_oi"); puts, _ = observation("put_oi")
    def wall(row, above):
        strikes = row.get("strikes") or []
        if not spot or not strikes:
            return None
        valid = [(number(s.get("strike")), number(s.get("open_interest"))) for s in strikes if isinstance(s, dict)]
        valid = [(strike, oi) for strike, oi in valid if strike is not None and oi is not None and oi > 0 and (strike >= spot if above else strike <= spot)]
        return max(valid, key=lambda p: (p[1], -abs(p[0]-spot)))[0] if valid else None
    call_wall, put_wall = wall(calls, True), wall(puts, False)
    wall_signal = None
    if calls.get("expiry") and calls.get("expiry") == puts.get("expiry") and call_wall and put_wall and call_wall > put_wall:
        wall_signal = ((call_wall-spot)-(spot-put_wall))/(call_wall-put_wall)
    add("oi_walls", "OI wall proximity", ["call_oi", "put_oi"], wall_signal,
        "Largest positive call OI above spot and put OI below spot; relative distance is only a geometry descriptor until directional mapping passes incremental validation",
        {"call_resistance": call_wall, "put_support": put_wall, "spot": spot}, group="positioning", reliability=0.)
    r, ok = observation("advance_decline")
    v = r.get("value") or {}
    if isinstance(v, dict):
        adv, dec, total, count = (number(v.get(k)) for k in ("advances", "declines", "universe_size", "available_constituents"))
        breadth = (adv-dec)/total if adv is not None and dec is not None and total and count == total else None
    else:
        breadth = None
    add("breadth", "Complete-universe market breadth", ["advance_decline"], breadth,
        "Advances minus declines divided by complete constituent universe; equity participation shares one context budget", v)
    # Overseas equities are pooled rather than counted as separate votes. Use
    # source session changes only; no unsupported daily-to-five-minute mapping.
    global_members, normalized_returns = [], []
    for key in ("sp500", "nasdaq", "nikkei", "hang_seng", "shanghai", "europe", "gift_nifty"):
        r, valid = observation(key)
        change = number(r.get("change_pct"))
        # Source-matched history is already supplied by NiftyService. Retain at
        # most one close per local source date to avoid intraday capture counts
        # artificially shrinking normal market volatility.
        history = {}
        for point in r.get("history", []):
            t, value = timestamp(point.get("ts")), number(point.get("value"))
            if t and t <= at and value is not None and value > 0:
                day = str(point["ts"])[:10]
                if day not in history or t > history[day][0]:
                    history[day] = (t, value)
        values = [history[day][1] for day in sorted(history)]
        returns = [(b/a-1)*100 for a, b in zip(values, values[1:])]
        scale = statistics.stdev(returns[-20:]) if len(returns) >= 20 else None
        if valid and change is not None and scale and scale > 0:
            global_members.append(key)
            normalized_returns.append(math.tanh(change/scale))
    if global_members:
        changes = [rows[key]["change_pct"] for key in global_members]
        add("global_markets", "Overseas equity context", global_members,
            sum(normalized_returns)/len(normalized_returns),
            "Only source changes within 15 minutes are compared; each return is scaled by its preceding 20 observed daily-return sample standard deviation before tanh", {"members": global_members, "change_pct": changes})
    else:
        add("global_markets", "Overseas equity context", ["sp500"], None,
            "No contemporaneous overseas equity change; prior closes remain context, not intraday directional votes")
    add("flows", "Institutional flow context", ["fii_cash", "dii_cash"], None,
        "Daily provisional net flow is not a five-minute entry signal; no validated causal transformation", reliability=0.)
    # A known imminent high-impact event is risk against either direction.
    near_events, event_rows = [], []
    for event in dashboard.get("events", []):
        t = timestamp(event.get("event_at"))
        received, published = timestamp(event.get("observed_at")), timestamp(event.get("reported_at"))
        known = received and received <= at and (published is None or published <= at)
        sourced = event.get("source") and event.get("source_url")
        imminent = t and 0 <= (t-at).total_seconds() <= 3600 and str(event.get("impact", "")).lower() == "high"
        if imminent and known and sourced:
            near_events.append(event.get("title", "High-impact event"))
            event_rows.append(event)
        elif imminent:
            audit.append({"id": "event_"+str(event.get("id", len(audit))), "label": event.get("title", "Unverified event"),
                "group": "risk", "available": False, "signal": None, "reliability": 0., "value": event.get("event_at"),
                "source": event.get("source"), "reported_at": event.get("reported_at"), "observed_at": event.get("observed_at"),
                "reason": "Event publication/receipt not known before decision or source is unverified", "scored": False})
    knowledge_at = max((timestamp(e["observed_at"]) for e in event_rows), default=None)
    signals["event_risk"] = factor("event_risk", "Known scheduled event risk", "risk", -1. if near_events else None,
        value=near_events, reason="Sourced high-impact event within the 60-minute research horizon; timestamp records calendar receipt, not event publication" if near_events else
        "No known imminent high-impact event; incomplete calendar cannot establish clearance",
        source="Retained sourced event calendar" if near_events else None,
        reported_at=knowledge_at.isoformat() if knowledge_at else None,
        observed_at=knowledge_at.isoformat() if knowledge_at else None, timestamp_basis="Calendar observation receipt")
    for key, r in rows.items():
        _, valid = observation(key)
        reason = ("Mapped into a grouped assessment factor; see factors below" if key in used else
                  "Daily technical overlaps intraday price; audited without adding another vote" if r.get("section_id") == "technicals" else
                  "Context only: no validated strategy-specific directional transformation at the five-minute horizon")
        audit.append({"id": "input_"+key, "label": r.get("label", key), "group": r.get("section_id", "context"),
            "available": valid, "signal": None, "reliability": 0., "value": r.get("value"),
            "source": r.get("source"), "reported_at": r.get("reported_at"), "observed_at": r.get("observed_at"),
            "reason": reason, "scored": False, "status": r.get("status"), "expiry": r.get("expiry")})
    return signals, audit
