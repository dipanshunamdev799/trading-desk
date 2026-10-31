"""Causal, session-local OHLC research annotations; no trade recommendations.

Every event is stamped on the bar that confirms it, never on a past pivot.
Rules are intentionally explicit heuristics, not claims about order flow.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from math import isfinite
from statistics import mean
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MINUTES = {"1minute": 1, "5minute": 5, "15minute": 15, "30minute": 30, "1hour": 60}
GROUPS = [
    {"id": "structure", "label": "Structure"}, {"id": "levels", "label": "Key levels"},
    {"id": "setups", "label": "Breakouts & reversals"}, {"id": "candles", "label": "Candlesticks"},
    {"id": "momentum", "label": "Continuation"}, {"id": "advanced", "label": "Advanced zones"},
]
# The numbers match the user's 47-item checklist. Thresholds are product rules.
_RULES = [
    (1, "structure", "HH / HL", "Confirmed higher highs or higher lows; bullish structure requires both. Pivots require two bars on each side."),
    (2, "structure", "LH / LL", "Confirmed lower highs or lower lows; bearish structure requires both."),
    (3, "structure", "Sideways range", "Last 10 bars span at most 3 × prior ATR(14), with net movement below 1 ATR."),
    (4, "levels", "Support", "Two confirmed swing lows within the level tolerance form a reaction zone."),
    (5, "levels", "Resistance", "Two confirmed swing highs within the level tolerance form a reaction zone."),
    (6, "setups", "Support / resistance flip", "A closed break of a known level followed by a later retest holding its new side, within 8 bars."),
    (7, "levels", "Previous day high", "High of the previous available daily candle; its actual session date is shown."),
    (8, "levels", "Previous day low", "Low of the previous available daily candle; its actual session date is shown."),
    (9, "levels", "Day high / low", "Running extrema of completed session bars; no final-day level is drawn over earlier bars."),
    (10, "levels", "Equal highs / lows", "Two confirmed same-side pivots within tolerance; confirmed two bars after the second pivot."),
    (11, "setups", "Liquidity sweep", "Wick crosses a previously known level by more than tolerance and the close returns inside."),
    (12, "levels", "Psychological levels", "Fixed round-number spacing selected by you; these are reference levels, not measured support."),
    (13, "setups", "Breakout + retest", "Close above a known high, then a later touch within tolerance and close above it; expires after 8 bars."),
    (14, "setups", "Breakdown + retest", "Close below a known low, then a later touch within tolerance and close below it; expires after 8 bars."),
    (15, "setups", "False breakout / breakdown", "A closed break returns across the same level within the following 3 bars."),
    (16, "setups", "Double top / bottom", "Two similar confirmed pivots, an intervening opposite pivot, then a closed neckline break."),
    (17, "setups", "Head and shoulders", "Five alternating confirmed pivots; middle peak above similar shoulders, followed by a close below both neckline lows."),
    (18, "setups", "Inverse head and shoulders", "Five alternating confirmed pivots; middle trough below similar shoulders, then a close above both neckline highs."),
    (19, "setups", "Trendline break", "Close crosses the extrapolated line of the two latest rising swing lows or falling swing highs."),
    (20, "structure", "CHoCH", "First closed swing break against the previously established HH/HL or LH/LL structure."),
    (21, "candles", "Bullish engulfing", "Bullish body encloses the prior bearish body after a 3-bar decline."),
    (22, "candles", "Bearish engulfing", "Bearish body encloses the prior bullish body after a 3-bar advance."),
    (23, "candles", "Hammer", "After a 3-bar decline: lower wick ≥2 bodies, upper wick ≤20% of range, body ≤35%."),
    (24, "candles", "Shooting star", "After a 3-bar advance: upper wick ≥2 bodies, lower wick ≤20% of range, body ≤35%."),
    (25, "candles", "Doji", "Body is at most 10% of the high-low range; zero-range bars are excluded."),
    (26, "candles", "Inside bar", "High strictly below and low strictly above the preceding bar."),
    (27, "candles", "Outside bar", "High strictly above and low strictly below the preceding bar."),
    (28, "candles", "Marubozu", "Body at least 80% of range and each wick at most 10%."),
    (29, "candles", "Morning star", "Prior decline, large bearish body, middle body ≤30% of that body, bullish close above its midpoint. Intraday variant: no gap required."),
    (30, "candles", "Evening star", "Prior advance, large bullish body, middle body ≤30% of that body, bearish close below its midpoint. No gap required."),
    (31, "candles", "Pin bar / rejection", "One wick ≥60% of range, opposite wick ≤15%, body ≤30%; shape only."),
    (32, "momentum", "Pullback to support", "In established HH/HL structure, touch the latest confirmed swing low and close back above it."),
    (33, "momentum", "Pullback to resistance", "In established LH/LL structure, touch the latest confirmed swing high and close back below it."),
    (34, "momentum", "Bull flag", "3-bar rise ≥2 prior ATR, then 4 declining consolidation closes with ≤50% retracement; closed break above consolidation."),
    (35, "momentum", "Bear flag", "3-bar fall ≥2 prior ATR, then 4 rising consolidation closes with ≤50% retracement; closed break below consolidation."),
    (36, "momentum", "Ascending triangle", "Three confirmed highs nearly flat and three rising lows; later close above the upper boundary."),
    (37, "momentum", "Descending triangle", "Three confirmed lows nearly flat and three falling highs; later close below the lower boundary."),
    (38, "momentum", "Symmetrical triangle", "Three falling highs and three rising lows; close beyond an extrapolated boundary."),
    (39, "momentum", "Opening range breakout", "First closed break of the selected 5/15/30-minute range. All opening bars required; range must divide the chart timeframe."),
    (40, "momentum", "Momentum breakout", "Closed swing break with range ≥1.5 prior ATR and body ≥70% of range."),
    (41, "momentum", "Compression / expansion", "5-bar span ≤2 prior ATR; subsequent candle range ≥1.5 prior ATR is an expansion."),
    (42, "structure", "BOS", "First closed break beyond a confirmed swing in the established structure direction."),
    (43, "advanced", "Order block candidate", "Last opposite candle within 5 bars before a displacement that closes beyond a known swing; candle range defines the zone."),
    (44, "advanced", "Fair value gap", "Three consecutive candles: third low above first high, or third high below first low. Zone starts at third-bar confirmation."),
    (45, "advanced", "Supply / demand candidate", "Last opposite candle within 5 bars preceding a displacement; its full high-low range defines the zone."),
    (46, "advanced", "Displacement", "Candle range ≥1.5 prior ATR with body ≥70% of range."),
    (47, "advanced", "Mitigation / retest", "First later overlap of an existing FVG, supply/demand or order-block zone. Zone ends on full traversal."),
]
CATALOG = [{"id": n, "group": group, "label": label, "rule": rule} for n, group, label, rule in _RULES]
BY_ID = {x["id"]: x for x in CATALOG}


def _dt(value):
    try:
        stamp = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return stamp.astimezone(IST) if stamp.tzinfo else None
    except (ValueError, TypeError):
        return None


def _valid(rows):
    unique = {}
    for row in rows:
        stamp = _dt(row.get("ts"))
        values = [row.get(k) for k in ("open", "high", "low", "close")]
        if stamp is None or any(isinstance(v, bool) or not isinstance(v, (float, int)) or not isfinite(v) or v <= 0 for v in values):
            continue
        o, h, l, c = values
        if l > min(o, c) or h < max(o, c) or l > h:
            continue
        unique[stamp] = {**row, "dt": stamp, "ts": stamp.isoformat()}
    return [unique[key] for key in sorted(unique)]


def analyze(candles, interval, *, daily=(), session=None, now=None, orb_minutes=15, round_step=100):
    now = (now or datetime.now(timezone.utc)).astimezone(IST)
    grain = MINUTES.get(interval)
    rows = _valid(candles)
    sessions = sorted({b["dt"].date().isoformat() for b in rows if b["dt"] <= now})
    selected = session or (sessions[-1] if sessions else None)
    result = {"version": "1.0", "session": selected, "sessions": sessions, "groups": GROUPS,
              "catalog": CATALOG, "events": [], "lines": [], "zones": [], "trend": "Insufficient structure",
              "completed_bars": 0, "forming_bars": 0, "confirmed_through": None, "notes": [],
              "orb_minutes": orb_minutes, "round_step": round_step, "previous_session": None}
    if not grain:
        result["notes"].append("Price-action study uses intraday bars. Choose 5 or 15 minutes to follow the checklist.")
        return result
    if not selected:
        result["notes"].append("No dated candles available.")
        return result
    session_rows = [b for b in rows if b["dt"].date().isoformat() == selected and time(9, 15) <= b["dt"].time() < time(15, 30)]
    end = datetime.combine(datetime.fromisoformat(selected).date(), time(15, 30), IST)
    def close_at(b):
        return min(b["dt"] + timedelta(minutes=grain), end)
    bars = [b for b in session_rows if close_at(b) <= now]
    result["completed_bars"] = len(bars)
    result["forming_bars"] = sum(b["dt"] <= now < close_at(b) for b in session_rows)
    if not bars:
        result["notes"].append("No completed regular-session candles for this date; forming candles do not confirm patterns.")
        return result
    result["confirmed_through"] = close_at(bars[-1]).isoformat()
    start = datetime.combine(bars[0]["dt"].date(), time(9, 15), IST)
    expected = int((close_at(bars[-1]) - start).total_seconds() / 60)
    present = {b["dt"] for b in bars}
    missing = sum(start + timedelta(minutes=m) not in present for m in range(0, expected, grain))
    result["missing_bars"] = missing
    if missing:
        result["notes"].append(f"{missing} expected bars missing. Multi-bar patterns reset across gaps; day extrema reflect available bars only.")
    result["notes"].append("Markers appear on the confirmation candle; swing labels lag pivots by two closed bars. All times are IST.")
    events, lines, zones = result["events"], result["lines"], result["zones"]
    seen = set()
    def event(n, i, side=0, detail=None, label=None, level=None):
        if (n, i, side) in seen:
            return
        seen.add((n, i, side))
        events.append({"id": f"{n}:{i}:{side}", "concept": n, "group": BY_ID[n]["group"],
                       "label": label or BY_ID[n]["label"], "ts": bars[i]["ts"],
                       "known_at": close_at(bars[i]).isoformat(), "side": side,
                       "price": bars[i]["close"], "level": level, "detail": detail or BY_ID[n]["rule"]})
    def line(n, label, points, side=0):
        lines.append({"concept": n, "group": BY_ID[n]["group"], "label": label, "side": side, "points": points})
    def horizontal(n, label, value, first=0, side=0):
        line(n, label, [{"ts": bars[first]["ts"], "value": value}, {"ts": bars[-1]["ts"], "value": value}], side)
    def zone(n, i, low, high, side, label=None):
        zones.append({"concept": n, "group": BY_ID[n]["group"], "label": label or BY_ID[n]["label"],
                      "start": bars[i]["ts"], "end": bars[-1]["ts"], "low": low, "high": high,
                      "side": side, "created": i, "tested": False, "active": True})
    previous = [b for b in _valid(daily) if b["dt"].date().isoformat() < selected]
    known_levels = []
    if previous:
        prev = previous[-1]
        result["previous_session"] = prev["dt"].date().isoformat()
        for n, field, label, side in [(7, "high", "PDH", 1), (8, "low", "PDL", -1)]:
            horizontal(n, label, prev[field], side=side)
            known_levels.append({"name": label, "value": prev[field], "side": side, "born": -1})
    else:
        result["notes"].append("Previous recorded daily candle unavailable; PDH and PDL are not inferred from partial intraday bars.")
    # Round numbers are known in advance, but choose only a bounded local grid.
    center = round(bars[0]["open"] / round_step) * round_step
    for offset in range(-3, 4):
        value = center + offset * round_step
        if value > 0:
            horizontal(12, f"Round {value:g}", value)
    orb_end = start + timedelta(minutes=orb_minutes)
    orb_rows = [b for b in bars if start <= b["dt"] < orb_end]
    orb_ok = grain <= orb_minutes and orb_minutes % grain == 0 and len(orb_rows) == orb_minutes // grain and all(
        b["dt"] == start + timedelta(minutes=j * grain) for j, b in enumerate(orb_rows))
    if orb_ok:
        for field, label, side in [("high", "ORH", 1), ("low", "ORL", -1)]:
            value = (max if side == 1 else min)(b[field] for b in orb_rows)
            first = len(orb_rows) - 1
            horizontal(39, f"{orb_minutes}m {label}", value, first, side)
            known_levels.append({"name": label, "value": value, "side": side, "born": first})
    else:
        result["notes"].append("Opening range unavailable: choose a compatible timeframe and require every opening bar to close.")
    highs, lows, pivots, pending, shapes = [], [], [], [], []
    broken, shape_ids, orb_broken, trendline_broken = set(), set(), set(), set()
    trend, ranges, segment_start = 0, [], 0
    running_high, running_low = [], []
    day_hi, day_lo = bars[0]["high"], bars[0]["low"]
    previous_compression = False
    for i, b in enumerate(bars):
        o, h, l, c = (b[k] for k in ("open", "high", "low", "close"))
        r, body = h - l, abs(c - o)
        side = 1 if c > o else -1 if c < o else 0
        upper, lower = h - max(o, c), min(o, c) - l
        if i and b["dt"] - bars[i-1]["dt"] != timedelta(minutes=grain):
            segment_start = i
            highs, lows, pivots, pending, shapes, ranges = [], [], [], [], [], []
            trend = 0
            previous_compression = False
        count = i - segment_start + 1
        p = bars[i-1] if count > 1 else None
        atr = mean(ranges[-14:]) if len(ranges) >= 14 else None
        tolerance = max(c * 0.00015, (atr or 0) * 0.12)
        down = count >= 4 and bars[i-1]["close"] < bars[i-3]["close"]
        up = count >= 4 and bars[i-1]["close"] > bars[i-3]["close"]
        displacement = bool(atr and r >= atr * 1.5 and body >= r * 0.7)
        if r > 0:
            checks = [(25, body <= r * .1, 0), (28, body >= r * .8 and max(upper, lower) <= r * .1, side),
                      (23, down and body > 0 and lower >= 2*body and upper <= .2*r and body <= .35*r, 1),
                      (24, up and body > 0 and upper >= 2*body and lower <= .2*r and body <= .35*r, -1),
                      (31, body <= .3*r and max(upper, lower) >= .6*r and min(upper, lower) <= .15*r, 1 if lower > upper else -1)]
            if p:
                checks += [(21, down and c > o and p["close"] < p["open"] and o <= p["close"] and c >= p["open"], 1),
                           (22, up and c < o and p["close"] > p["open"] and o >= p["close"] and c <= p["open"], -1),
                           (26, h < p["high"] and l > p["low"], 0), (27, h > p["high"] and l < p["low"], side)]
            if count >= 5:
                a, mid = bars[i-2], bars[i-1]
                abody = abs(a["close"] - a["open"])
                small = abody > 0 and abs(mid["close"] - mid["open"]) <= .3*abody and abody >= .6*(a["high"]-a["low"])
                checks += [(29, small and a["close"] < a["open"] and bars[i-3]["close"] < bars[i-5 if count >= 6 else i-4]["close"] and c > o and c > (a["open"]+a["close"])/2, 1),
                           (30, small and a["close"] > a["open"] and bars[i-3]["close"] > bars[i-5 if count >= 6 else i-4]["close"] and c < o and c < (a["open"]+a["close"])/2, -1)]
            for n, matched, direction in checks:
                if matched:
                    event(n, i, direction)
        # Existing zones only: a creation candle can never mitigate its own zone.
        for z in zones:
            if not z["active"] or z["created"] >= i:
                continue
            if l <= z["high"] and h >= z["low"] and not z["tested"]:
                event(47, i, z["side"], f"First revisit of {z['label']} ({z['low']:.2f}–{z['high']:.2f}).", level=(z["high"]+z["low"])/2)
                z["tested"] = True
            if (z["side"] > 0 and l <= z["low"]) or (z["side"] < 0 and h >= z["high"]):
                z["active"], z["end"] = False, b["ts"]
        if count >= 3:
            a = bars[i-2]
            if l > a["high"]:
                event(44, i, 1); zone(44, i, a["high"], l, 1, "Bullish FVG")
            if h < a["low"]:
                event(44, i, -1); zone(44, i, h, a["low"], -1, "Bearish FVG")
        # Confirm the pivot i-2 using exactly two later closed bars.
        if count >= 5:
            j = i - 2
            window = bars[j-2:i+1]
            for field, seq, direction in [("high", highs, -1), ("low", lows, 1)]:
                value = bars[j][field]
                extremum = all(value > x[field] if field == "high" else value < x[field] for k, x in enumerate(window) if k != 2)
                if not extremum:
                    continue
                old = seq[-1] if seq else None
                tag = ("HH" if value > old["value"]+tolerance else "LH" if value < old["value"]-tolerance else "EQH") if field == "high" and old else (
                    ("HL" if value > old["value"]+tolerance else "LL" if value < old["value"]-tolerance else "EQL") if old else ("SH" if field == "high" else "SL"))
                pivot = {"i": j, "confirm": i, "value": value, "field": field, "tag": tag}
                seq.append(pivot)
                if pivots and pivots[-1]["field"] == field:
                    if (value > pivots[-1]["value"]) == (field == "high"):
                        pivots[-1] = pivot
                else:
                    pivots.append(pivot)
                if tag in ("HH", "HL", "LH", "LL"):
                    event(1 if tag in ("HH", "HL") else 2, i, 1 if tag in ("HH", "HL") else -1,
                          f"{tag} at {value:.2f}, pivot {bars[j]['dt']:%H:%M}; confirmed at {close_at(b):%H:%M}.", tag, value)
                if old and abs(value-old["value"]) <= tolerance:
                    n = 5 if field == "high" else 4
                    event(n, i, direction, level=value); event(10, i, direction, label="Equal highs" if field == "high" else "Equal lows", level=value)
                    zone(n, i, min(value, old["value"])-tolerance, max(value, old["value"])+tolerance, direction)
                    opposite = [x for x in (lows if field == "high" else highs) if old["i"] < x["i"] < j]
                    if opposite:
                        neck = (min if field == "high" else max)(x["value"] for x in opposite)
                        shapes.append({"id": (16, j, field), "concept": 16, "level": neck, "side": direction, "born": i, "invalid": max(value, old["value"])+tolerance if field == "high" else min(value, old["value"])-tolerance, "label": "Double top" if field == "high" else "Double bottom"})
            if len(highs) >= 2 and len(lows) >= 2:
                new_trend = 1 if highs[-1]["tag"] == "HH" and lows[-1]["tag"] == "HL" else -1 if highs[-1]["tag"] == "LH" and lows[-1]["tag"] == "LL" else 0
                if new_trend and new_trend != trend:
                    event(1 if new_trend == 1 else 2, i, new_trend, label="HH/HL structure" if new_trend == 1 else "LH/LL structure")
                # Mixed swings retain the established trend until its counter-break.
                trend = new_trend or trend
            if len(pivots) >= 5:
                a, b1, head, d, shoulder = pivots[-5:]
                top = a["field"] == "high"
                if a["field"] == head["field"] == shoulder["field"] and abs(a["value"]-shoulder["value"]) <= tolerance*2 and (
                    head["value"] > max(a["value"], shoulder["value"])+tolerance if top else head["value"] < min(a["value"], shoulder["value"])-tolerance):
                    n, direction = (17, -1) if top else (18, 1)
                    identity = (n, head["i"])
                    if identity not in shape_ids:
                        shape_ids.add(identity)
                        shapes.append({"id": identity, "concept": n, "level": min(b1["value"], d["value"]) if top else max(b1["value"], d["value"]), "side": direction, "born": i, "invalid": head["value"]+tolerance if top else head["value"]-tolerance, "label": BY_ID[n]["label"]})
        # Swing breaks only use pivots known before this candle.
        broke_swing = False
        for seq, direction in [(highs, 1), (lows, -1)]:
            candidates = [x for x in seq if x["confirm"] < i]
            if not candidates or not p:
                continue
            swing = candidates[-1]
            v = swing["value"]
            identity = (swing["i"], direction)
            crossed = p["close"] <= v+tolerance and c > v+tolerance if direction == 1 else p["close"] >= v-tolerance and c < v-tolerance
            if crossed and identity not in broken:
                broken.add(identity); broke_swing = True
                if trend:
                    event(42 if trend == direction else 20, i, direction, level=v)
                    if trend != direction:
                        trend = 0
                if displacement:
                    event(40, i, direction, level=v)
        levels = known_levels + [{"name": "Swing high", "value": highs[-1]["value"], "side": 1, "born": highs[-1]["confirm"]}] if highs else list(known_levels)
        if lows:
            levels.append({"name": "Swing low", "value": lows[-1]["value"], "side": -1, "born": lows[-1]["confirm"]})
        for level in levels:
            v, direction = level["value"], level["side"]
            if level["born"] >= i or not p:
                continue
            crossed = p["close"] <= v+tolerance and c > v+tolerance if direction == 1 else p["close"] >= v-tolerance and c < v-tolerance
            if crossed:
                pending.append({**level, "i": i, "tolerance": tolerance})
                if level["name"] in ("ORH", "ORL") and direction not in orb_broken:
                    orb_broken.add(direction)
                    event(39, i, direction, f"Closed beyond the complete {orb_minutes}-minute opening range.", "ORB ↑" if direction == 1 else "ORB ↓", v)
            sweep = p["close"] <= v and h > v+tolerance and c < v if direction == 1 else p["close"] >= v and l < v-tolerance and c > v
            if sweep:
                event(11, i, -direction, f"Swept {level['name']} {v:.2f} and closed back inside.", level=v)
        retained = []
        for trigger in pending:
            age, v, direction, tol = i-trigger["i"], trigger["value"], trigger["side"], trigger["tolerance"]
            if age == 0:
                retained.append(trigger); continue
            if age > 8:
                continue
            failed = c < v-tol if direction == 1 else c > v+tol
            if failed:
                if age <= 3:
                    event(15, i, -direction, f"{trigger['name']} break failed after {age} bars.", level=v)
                continue
            touched = l <= v+tol and c > v+tol if direction == 1 else h >= v-tol and c < v-tol
            if touched:
                event(13 if direction == 1 else 14, i, direction, f"Retest held {trigger['name']} {v:.2f} after {age} bars.", level=v)
                event(6, i, direction, level=v)
            else:
                retained.append(trigger)
        pending = retained
        for shape in shapes:
            v, direction = shape["level"], shape["side"]
            if (direction == -1 and c > shape["invalid"]) or (direction == 1 and c < shape["invalid"]):
                broken.add(shape["id"])
            if p and i > shape["born"] and i-shape["born"] <= 30 and shape["id"] not in broken and (
                p["close"] <= v and c > v+tolerance if direction == 1 else p["close"] >= v and c < v-tolerance):
                broken.add(shape["id"])
                event(shape["concept"], i, direction, label=shape["label"]+" · neckline", level=v)
        for seq, direction in [(lows, -1), (highs, 1)]:
            old = [x for x in seq if x["confirm"] < i]
            if len(old) < 2 or not p:
                continue
            a, z = old[-2:]
            slope = (z["value"]-a["value"])/(z["i"]-a["i"])
            v = z["value"]+slope*(i-z["i"])
            before = v-slope
            identity = (a["i"], z["i"], direction)
            if identity not in trendline_broken and ((slope > 0 and direction == -1 and p["close"] >= before and c < v-tolerance) or (slope < 0 and direction == 1 and p["close"] <= before and c > v+tolerance)):
                trendline_broken.add(identity); event(19, i, direction, level=v)
                line(19, "Broken trendline", [{"ts": bars[z["confirm"]]["ts"], "value": z["value"]+slope*(z["confirm"]-z["i"])}, {"ts": bars[i]["ts"], "value": v}], direction)
        if highs and lows and p:
            if trend == 1 and lows[-1]["confirm"] < i and p["low"] > lows[-1]["value"]+tolerance and l <= lows[-1]["value"]+tolerance and c > lows[-1]["value"]:
                event(32, i, 1, level=lows[-1]["value"])
            if trend == -1 and highs[-1]["confirm"] < i and p["high"] < highs[-1]["value"]-tolerance and h >= highs[-1]["value"]-tolerance and c < highs[-1]["value"]:
                event(33, i, -1, level=highs[-1]["value"])
        if displacement:
            event(46, i, side)
            opposite = [x for x in bars[max(segment_start, i-5):i] if (x["close"]-x["open"])*side < 0]
            if opposite:
                z = opposite[-1]
                event(45, i, side); zone(45, i, z["low"], z["high"], side, "Demand candidate" if side == 1 else "Supply candidate")
                if broke_swing:
                    event(43, i, side); zone(43, i, z["low"], z["high"], side)
        if atr and count >= 10:
            window = bars[i-9:i+1]
            span = max(x["high"] for x in window)-min(x["low"] for x in window)
            if span <= 3*atr and abs(c-window[0]["close"]) < atr:
                event(3, i, 0)
            consolidation = bars[i-4:i+1]
            compressed = max(x["high"] for x in consolidation)-min(x["low"] for x in consolidation) <= 2*atr
            if compressed and not previous_compression:
                event(41, i, 0, label="Compression")
            if previous_compression and r >= 1.5*atr:
                event(41, i, side, label="Expansion")
            previous_compression = compressed
            pole = bars[i-7:i-4]
            flag = bars[i-4:i]
            move = pole[-1]["close"]-pole[0]["open"]
            flag_hi, flag_lo = max(x["high"] for x in flag), min(x["low"] for x in flag)
            if move >= 2*atr and flag[-1]["close"] < flag[0]["close"] and pole[-1]["close"]-flag_lo <= .5*move and flag_lo >= pole[0]["open"] and c > flag_hi+tolerance:
                event(34, i, 1)
            if move <= -2*atr and flag[-1]["close"] > flag[0]["close"] and flag_hi-pole[-1]["close"] <= -.5*move and flag_hi <= pole[0]["open"] and c < flag_lo-tolerance:
                event(35, i, -1)
        hs, ls = [x for x in highs if x["confirm"] < i][-3:], [x for x in lows if x["confirm"] < i][-3:]
        if len(hs) == 3 and len(ls) == 3 and p and abs(hs[0]["i"]-ls[0]["i"]) <= 15:
            hv, lv = [x["value"] for x in hs], [x["value"] for x in ls]
            flat_h, flat_l = max(hv)-min(hv) <= 2*tolerance, max(lv)-min(lv) <= 2*tolerance
            rising, falling = lv[0] < lv[1] < lv[2], hv[0] > hv[1] > hv[2]
            def project(seq, index):
                a, z = seq[0], seq[-1]
                return z["value"]+(z["value"]-a["value"])*(index-z["i"])/(z["i"]-a["i"])
            upper_line, lower_line = project(hs, i), project(ls, i)
            patterns = [(36, flat_h and rising and p["close"] <= max(hv) and c > max(hv)+tolerance, 1),
                        (37, flat_l and falling and p["close"] >= min(lv) and c < min(lv)-tolerance, -1),
                        (38, rising and falling and lower_line < upper_line and p["close"] <= project(hs, i-1) and c > upper_line+tolerance, 1),
                        (38, rising and falling and lower_line < upper_line and p["close"] >= project(ls, i-1) and c < lower_line-tolerance, -1)]
            for n, matched, direction in patterns:
                identity = (n, hs[-1]["i"], ls[-1]["i"])
                if matched and identity not in shape_ids:
                    shape_ids.add(identity); event(n, i, direction, label=BY_ID[n]["label"]+" · break")
                    first = max(hs[-1]["confirm"], ls[-1]["confirm"])
                    for seq in (hs, ls):
                        line(n, BY_ID[n]["label"], [{"ts": bars[first]["ts"], "value": project(seq, first)}, {"ts": b["ts"], "value": project(seq, i)}], direction)
        day_hi, day_lo = max(day_hi, h), min(day_lo, l)
        running_high.append({"ts": b["ts"], "value": day_hi})
        running_low.append({"ts": b["ts"], "value": day_lo})
        ranges.append(max(r, abs(h-p["close"]), abs(l-p["close"])) if p else r)
    line(9, "Day high", running_high, 1); line(9, "Day low", running_low, -1)
    result["trend"] = "Bullish HH/HL" if trend == 1 else "Bearish LH/LL" if trend == -1 else "Mixed / unconfirmed"
    result["atr"] = mean(ranges[-14:]) if len(ranges) >= 14 else None
    result["level_tolerance"] = max(bars[-1]["close"]*.00015, (result["atr"] or 0)*.12)
    events.sort(key=lambda e: (e["ts"], e["concept"], e["side"]))
    return result
