"""Deterministic research calculations. Missing inputs never become zeroes.

Functions do no network or database I/O. Positioning and correlation describe
observations; none of these calculations establishes the next market move.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
TECHNICAL_IDS = ("nifty_spot", "daily_trend", "hourly_trend", "intraday_trend",
                 "support_resistance", "previous_high_low", "previous_close", "opening_gap",
                 "volume", "vwap", "ema", "rsi", "macd", "atr_volatility", "breakouts",
                 "market_structure", "opening_range", "momentum")
OPTION_IDS = ("pcr", "call_oi", "put_oi", "call_oi_change", "put_oi_change", "max_pain",
              "iv", "iv_skew", "option_greeks", "option_volume")


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError, OverflowError):
        return None


def _timestamp(value):
    if isinstance(value, datetime):
        result = value
    else:
        try:
            result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
    # Indian daily/session candles without an offset are interpreted in IST.
    return (result if result.tzinfo else result.replace(tzinfo=IST)).astimezone(timezone.utc)


def _metric(value=None, context="", **extra):
    result = {"value": value, "context": context}
    result.update(extra)
    return result


def _comparison(value, previous, context=""):
    change = value - previous if value is not None and previous is not None else None
    return _metric(value, context, previous_value=previous, change=change,
                   change_pct=change / abs(previous) * 100 if change is not None and previous else None,
                   trend="up" if change and change > 0 else "down" if change and change < 0 else "flat" if change == 0 else None)


def _candles(rows):
    result = {}
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        ts = _timestamp(raw.get("ts", raw.get("timestamp", raw.get("date"))))
        values = {key: _number(raw.get(key)) for key in ("open", "high", "low", "close")}
        if ts is None or any(value is None or value <= 0 for value in values.values()):
            continue
        if values["high"] < max(values["open"], values["close"], values["low"]) or values["low"] > min(values["open"], values["close"]):
            continue
        result[ts] = {**raw, **values, "ts": ts}
    return [result[ts] for ts in sorted(result)]


def _ema(values, period):
    result = [None] * len(values)
    if len(values) < period:
        return result
    current = statistics.fmean(values[:period])
    result[period - 1] = current
    alpha = 2 / (period + 1)
    for i in range(period, len(values)):
        current += alpha * (values[i] - current)
        result[i] = current
    return result


def _rsi(values, period=14):
    if len(values) <= period:
        return None
    changes = [b - a for a, b in zip(values, values[1:])]
    gain = statistics.fmean(max(value, 0) for value in changes[:period])
    loss = statistics.fmean(max(-value, 0) for value in changes[:period])
    for value in changes[period:]:
        gain = (gain * (period - 1) + max(value, 0)) / period
        loss = (loss * (period - 1) + max(-value, 0)) / period
    if gain == loss == 0:
        return 50.0
    return 100.0 if loss == 0 else 100 - 100 / (1 + gain / loss)


def _bar_kind(rows):
    intervals = {str(row.get("interval", "")).lower() for row in rows if row.get("interval")}
    if intervals & {"1day", "day", "daily", "1d", "days"}:
        return "daily", None
    times = [row["ts"] for row in rows]
    gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:]) if (b - a).total_seconds() > 0]
    gap = statistics.median(gaps) if gaps else None
    if intervals & {"1hour", "60minute", "1h", "hour", "hours"} or gap == 3600:
        return "hourly", 3600
    if intervals & {"1minute", "3minute", "5minute", "15minute", "30minute", "1m", "3m", "5m", "15m", "30m"} or gap is not None and gap < 86400:
        return "intraday", gap
    return "daily", None


def technical_snapshot(candles: list[dict]) -> dict:
    """Calculate indicators on sorted, deduplicated valid OHLC observations.

    One timeframe per invocation. Interval metadata is preferred; otherwise bar
    spacing infers the timeframe. No resampling or missing-bar forward filling.
    Index volume/VWAP is unavailable. Traded proxies require explicit
    ``volume_is_traded=True`` or a traded ``instrument_type`` on every used bar.
    """
    result = {key: _metric(context="No valid dated OHLC observations.") for key in TECHNICAL_IDS}
    rows = _candles(candles)
    if not rows:
        return result
    closes = [row["close"] for row in rows]
    kind, spacing = _bar_kind(rows)
    count = len(rows)
    label = f"{count} valid {kind} bars; duplicate timestamps use the last valid observation."
    for key in result:
        result[key] = _metric(context=label)
    sessions = defaultdict(list)
    for row in rows:
        sessions[row["ts"].astimezone(IST).date().isoformat()].append(row)
    days = sorted(sessions)
    current_session = sessions[days[-1]]
    prior_session = sessions[days[-2]] if len(days) > 1 else []
    previous_close = prior_session[-1]["close"] if prior_session else None
    result["nifty_spot"] = _comparison(closes[-1], previous_close, f"Latest observed {kind} close; previous value is the previous available session close.")
    if prior_session:
        prior_high, prior_low = max(row["high"] for row in prior_session), min(row["low"] for row in prior_session)
        result["previous_high_low"] = _metric({"high": prior_high, "low": prior_low}, f"Previous observed session: {days[-2]}.")
        result["previous_close"] = _metric(previous_close, f"Previous observed session: {days[-2]}.")
        opened = current_session[0]["open"]
        result["opening_gap"] = _metric({"points": opened - previous_close, "pct": (opened / previous_close - 1) * 100}, f"First observed open on {days[-1]} versus {days[-2]} close; verify session coverage for intraday input.")
    averages = {period: _ema(closes, period) for period in (9, 12, 21, 26, 50, 100, 200)}
    result["ema"] = _metric({str(period): averages[period][-1] for period in (9, 21, 50, 100, 200)}, f"SMA-seeded EMA; each period needs that many {kind} closes; null means insufficient warmup.")
    for timeframe in ("daily", "hourly", "intraday"):
        key = f"{timeframe}_trend"
        result[key] = _metric(context=f"Requires {timeframe} bars; supplied bars are {kind}.")
        if timeframe == kind:
            e21, e50 = averages[21][-1], averages[50][-1]
            if e50 is None:
                result[key] = _metric(context=f"Requires 50 {kind} closes; received {count}.")
            else:
                state = "uptrend" if closes[-1] > e21 > e50 else "downtrend" if closes[-1] < e21 < e50 else "mixed"
                result[key] = _metric(state, f"Close relative to EMA21 and EMA50 on {kind} bars.", trend=state)
    result["rsi"] = _comparison(_rsi(closes), _rsi(closes[:-1]), f"Wilder RSI14 on {kind} bars; requires 15 closes. Flat prices produce 50.")
    macd_line = [fast - slow for fast, slow in zip(averages[12], averages[26]) if fast is not None and slow is not None]
    if len(macd_line) >= 9:
        signal = _ema(macd_line, 9)[-1]
        result["macd"] = _metric({"macd": macd_line[-1], "signal": signal, "histogram": macd_line[-1] - signal}, f"EMA12−EMA26 and EMA9 signal on {kind} closes; SMA seeds.")
    else:
        result["macd"] = _metric(context=f"Complete MACD(12,26,9) needs 34 closes; received {count}.")
    ranges = [max(row["high"] - row["low"], abs(row["high"] - previous["close"]), abs(row["low"] - previous["close"])) for previous, row in zip(rows, rows[1:])]
    atr = None
    if len(ranges) >= 14:
        atr = statistics.fmean(ranges[:14])
        for true_range in ranges[14:]:
            atr = (atr * 13 + true_range) / 14
    realised = None
    if len(closes) >= 21 and kind == "daily":
        returns = [math.log(b / a) for a, b in zip(closes[-21:], closes[-20:])]
        realised = statistics.stdev(returns) * math.sqrt(252) * 100
    result["atr_volatility"] = _metric({"atr_14": atr, "realised_volatility_20d_pct": realised}, f"Wilder ATR14 needs 15 bars. Sample stdev of 20 daily log returns × sqrt(252) ×100; unavailable for non-daily bars.")
    if count >= 21:
        window = rows[-21:-1]
        support, resistance = min(row["low"] for row in window), max(row["high"] for row in window)
        result["support_resistance"] = _metric({"support": support, "resistance": resistance}, f"Previous 20 completed {kind} bars; latest bar excluded.")
        result["breakouts"] = _metric("breakout" if closes[-1] > resistance else "breakdown" if closes[-1] < support else "inside range", "Latest close versus preceding 20-bar extremes.")
    else:
        for key in ("support_resistance", "breakouts"):
            result[key] = _metric(context=f"Requires 21 bars including latest; received {count}.")
    swing_highs = [rows[i]["high"] for i in range(2, count - 2) if all(rows[i]["high"] > rows[j]["high"] for j in (i - 2, i - 1, i + 1, i + 2))]
    swing_lows = [rows[i]["low"] for i in range(2, count - 2) if all(rows[i]["low"] < rows[j]["low"] for j in (i - 2, i - 1, i + 1, i + 2))]
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        hh, hl = swing_highs[-1] > swing_highs[-2], swing_lows[-1] > swing_lows[-2]
        lh, ll = swing_highs[-1] < swing_highs[-2], swing_lows[-1] < swing_lows[-2]
        result["market_structure"] = _metric("higher highs / higher lows" if hh and hl else "lower highs / lower lows" if lh and ll else "mixed", "Last two confirmed swing highs/lows with two bars on each side; latest two bars cannot confirm pivots.")
    else:
        result["market_structure"] = _metric(context="Requires at least two confirmed swing highs and two swing lows; trending bars alone do not establish this pattern.")
    roc = (closes[-1] / closes[-15] - 1) * 100 if count >= 15 else None
    spread = (averages[21][-1] / averages[50][-1] - 1) * 100 if averages[50][-1] else None
    result["momentum"] = _metric({"roc_14_pct": roc, "ema_21_50_spread_pct": spread}, f"14-{kind}-bar rate of change and EMA21/50 spread; warmups 15 and 50 bars.")
    previous_range = None
    if prior_session:
        previous_range = {"high": max(r["high"] for r in prior_session), "low": min(r["low"] for r in prior_session)}
    opening_bars = [row for row in current_session if "09:15" <= row["ts"].astimezone(IST).strftime("%H:%M") < "09:45"]
    opening_range = None
    if kind == "intraday" and opening_bars and spacing and spacing <= 1800:
        times = [row["ts"].astimezone(IST) for row in opening_bars]
        # Do not label an incomplete opening window as the complete range.
        gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
        if times[0].strftime("%H:%M") == "09:15" and times[-1].hour * 3600 + times[-1].minute * 60 + spacing >= 9 * 3600 + 45 * 60 and all(gap <= spacing for gap in gaps):
            opening_range = {"high": max(row["high"] for row in opening_bars), "low": min(row["low"] for row in opening_bars)}
    result["opening_range"] = _metric({"opening_30min": opening_range, "previous_session": previous_range}, "09:15–09:45 IST requires a complete observed intraday window. Prior-session range uses available bars; verify coverage.")
    def traded(row):
        return row.get("volume_is_traded") is True or str(row.get("instrument_type", "")).upper() in {"EQ", "ETF", "FUT", "FUTIDX", "FUTSTK", "EQUITY", "FUTURES"}
    result["volume"] = _metric(context="NIFTY spot has no directly traded volume; use a named futures/ETF instrument with explicit traded-volume metadata.")
    result["vwap"] = _metric(context="NIFTY spot VWAP is unavailable. Requires intraday bars and actual volume for a named traded proxy.")
    if all(traded(row) for row in rows):
        volumes = [_number(row.get("volume")) for row in rows]
        if volumes[-1] is not None and volumes[-1] >= 0:
            history = volumes[-21:-1]
            average = statistics.fmean(history) if len(history) == 20 and all(v is not None and v >= 0 for v in history) else None
            result["volume"] = _metric({"volume": volumes[-1], "average_20": average, "spike_ratio": volumes[-1] / average if average else None}, f"Actual traded-proxy volume on {kind} bars; identify the instrument separately. Spike baseline excludes latest bar.")
        session_volumes = [_number(row.get("volume")) for row in current_session]
        if kind == "intraday" and all(v is not None and v >= 0 for v in session_volumes) and sum(session_volumes) > 0:
            vwap = sum((row["high"] + row["low"] + row["close"]) / 3 * volume for row, volume in zip(current_session, session_volumes)) / sum(session_volumes)
            result["vwap"] = _metric(vwap, "Typical-price × actual traded-proxy volume / session volume; available observed bars only, not NIFTY index VWAP.")
    return result


def option_snapshot(rows: list[dict]) -> dict:
    """One-expiry Upstox chain analytics, retaining strike-level missingness.

    Aggregates are unavailable if any included strike is missing a required side
    or field. Coverage refers to supplied strikes; the upstream adapter must
    establish that a fetched chain is complete. No absent OI/IV/Greek is zero.
    """
    result = {key: _metric(context="No option-chain observations.") for key in OPTION_IDS}
    unique, expiries = {}, set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        strike = _number(row.get("strike_price", row.get("strike")))
        if strike is None or strike <= 0:
            continue
        expiry = row.get("expiry") or row.get("expiry_date")
        if expiry:
            expiries.add(str(expiry))
        unique[(str(expiry or ""), strike)] = row
    if not unique:
        return result
    if len(expiries) > 1:
        return {key: _metric(context="Mixed expiries rejected; select one expiry before calculating option metrics.") for key in OPTION_IDS}
    parsed = []
    for (_, strike), row in sorted(unique.items(), key=lambda item: item[0][1]):
        item = {"strike": strike, "spot": _number(row.get("underlying_spot_price"))}
        for side, source_key in (("call", "call_options"), ("put", "put_options")):
            side_row = row.get(source_key) if isinstance(row.get(source_key), dict) else {}
            market = side_row.get("market_data") if isinstance(side_row.get("market_data"), dict) else {}
            greeks = side_row.get("option_greeks") if isinstance(side_row.get("option_greeks"), dict) else {}
            item[side] = {key: _number(market.get(key)) for key in ("oi", "prev_oi", "volume")}
            for key in ("oi", "prev_oi", "volume"):
                if item[side][key] is not None and item[side][key] < 0:
                    item[side][key] = None
            item[side]["greeks"] = {key: _number(greeks.get(key)) for key in ("delta", "gamma", "theta", "vega", "iv")}
            if item[side]["greeks"]["iv"] is not None and item[side]["greeks"]["iv"] <= 0:
                item[side]["greeks"]["iv"] = None
        parsed.append(item)
    def aggregate(side, field):
        values = [row[side][field] for row in parsed]
        return sum(values) if all(value is not None for value in values) else None
    totals = {side: aggregate(side, "oi") for side in ("call", "put")}
    for side in ("call", "put"):
        strikes = [{"strike": row["strike"], "open_interest": row[side]["oi"]} for row in parsed]
        complete = sum(row["open_interest"] is not None for row in strikes)
        previous_total = aggregate(side, "prev_oi")
        result[f"{side}_oi"] = {**_comparison(totals[side], previous_total, f"Provider OI units retained. {complete}/{len(parsed)} supplied strikes have {side} OI; incomplete totals remain unavailable."), "strikes": strikes}
        changes = [{"strike": row["strike"], "change": row[side]["oi"] - row[side]["prev_oi"] if row[side]["oi"] is not None and row[side]["prev_oi"] is not None else None} for row in parsed]
        total_change = sum(row["change"] for row in changes) if all(row["change"] is not None for row in changes) else None
        result[f"{side}_oi_change"] = _metric(total_change, "Current minus previous OI, matched by supplied strike and expiry; missing previous OI is unavailable.", strikes=changes)
    pcr = totals["put"] / totals["call"] if totals["put"] is not None and totals["call"] is not None and totals["call"] > 0 else None
    result["pcr"] = _metric(pcr, "Total supplied-strike put OI / call OI, one expiry. Zero call OI or incomplete fields gives unavailable; not a directional forecast.")
    curve = []
    if all(total is not None for total in totals.values()) and sum(totals.values()) > 0:
        for item in parsed:
            settlement = item["strike"]
            payout = sum(max(settlement - row["strike"], 0) * row["call"]["oi"] + max(row["strike"] - settlement, 0) * row["put"]["oi"] for row in parsed)
            curve.append({"strike": settlement, "payout": payout})
    if curve:
        minimum = min(row["payout"] for row in curve)
        tied = [row["strike"] for row in curve if row["payout"] == minimum]
        result["max_pain"] = _metric(tied[0], "Listed strike minimizing Σ(call OI×max(S−K,0) + put OI×max(K−S,0)); lowest strike returned on ties. Provider units retained; no premium adjustment.", payout_curve=curve, tied_strikes=tied)
    else:
        result["max_pain"] = _metric(context="Requires call and put OI at every supplied strike and positive total OI; no absent OI inferred.")
    spot_values = [row["spot"] for row in parsed if row["spot"] is not None and row["spot"] > 0]
    if spot_values and max(spot_values) - min(spot_values) <= max(0.01, min(spot_values) * 1e-6):
        spot = statistics.median(spot_values)
        atm = min(parsed, key=lambda row: (abs(row["strike"] - spot), row["strike"]))
        call_iv, put_iv = atm["call"]["greeks"]["iv"], atm["put"]["greeks"]["iv"]
        detail = f"Same strike {atm['strike']:g}, same expiry, nearest supplied strike to spot {spot:g}; lower strike on distance ties. Both positive IV fields required."
        result["iv"] = _metric((call_iv + put_iv) / 2 if call_iv is not None and put_iv is not None else None, "Mean ATM call/put provider IV (%). " + detail)
        result["iv_skew"] = _metric(put_iv - call_iv if call_iv is not None and put_iv is not None else None, "ATM same-strike put IV minus call IV in percentage points; this is not a 25-delta risk reversal. " + detail)
    else:
        for key in ("iv", "iv_skew"):
            result[key] = _metric(context="Requires a positive consistent underlying spot to select matching-moneyness call/put IV.")
    greek_strikes = [{"strike": row["strike"], "call": {key: row["call"]["greeks"][key] for key in ("delta", "gamma", "theta", "vega")}, "put": {key: row["put"]["greeks"][key] for key in ("delta", "gamma", "theta", "vega")}} for row in parsed]
    has_greeks = any(value is not None for row in greek_strikes for side in ("call", "put") for value in row[side].values())
    result["option_greeks"] = _metric({"strikes": greek_strikes} if has_greeks else None, "Provider Delta/Gamma/Theta/Vega by strike and side; null means missing, actual zero remains zero. No invalid portfolio summation.", strikes=greek_strikes)
    call_volume, put_volume = aggregate("call", "volume"), aggregate("put", "volume")
    result["option_volume"] = _metric(call_volume + put_volume if call_volume is not None and put_volume is not None else None, "Sum of supplied call and put traded volume; unavailable if any field is absent. Provider units retained.", strikes=[{"strike": row["strike"], "call_volume": row["call"]["volume"], "put_volume": row["put"]["volume"]} for row in parsed])
    return result


def correlate_series(left: list[dict], right: list[dict], min_samples: int = 20) -> dict:
    """Pearson correlation of daily simple returns on identical date intervals.

    Each series is first collapsed to its last valid observed close per local
    date. Returns are computed independently before intersection. Both start
    and end dates must match, so a missing holiday cannot turn a multi-session
    return into a daily return by silently bridging a gap in the other series.
    """
    minimum = max(3, int(min_samples))
    def returns(rows):
        dated = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            timestamp = _timestamp(row.get("ts", row.get("date")))
            value = _number(row.get("value"))
            if timestamp is None or value is None or value <= 0:
                continue
            # Preserve the supplied timestamp's local market date rather than
            # moving a US evening close onto the following Indian calendar day.
            raw = row.get("ts", row.get("date"))
            try:
                local_date = datetime.fromisoformat(str(raw).replace("Z", "+00:00")).date().isoformat()
            except (ValueError, TypeError):
                local_date = timestamp.date().isoformat()
            if local_date not in dated or timestamp >= dated[local_date][0]:
                dated[local_date] = (timestamp, value)
        days = sorted(dated)
        return {(previous, current): dated[current][1] / dated[previous][1] - 1 for previous, current in zip(days, days[1:])}
    left_returns, right_returns = returns(left), returns(right)
    matched = sorted(set(left_returns) & set(right_returns))
    result = {"coefficient": None, "sample_count": len(matched), "min_samples": minimum,
              "method": "Pearson correlation of daily matched close-to-close simple returns",
              "note": "Identical start/end local dates only; no forward filling. Non-synchronous market closes may affect comparison. Correlation does not establish causation or predict direction."}
    if len(matched) < minimum:
        result["note"] += f" Need at least {minimum} matched return intervals."
        return result
    xs, ys = [left_returns[key] for key in matched], [right_returns[key] for key in matched]
    x_mean, y_mean = statistics.fmean(xs), statistics.fmean(ys)
    x_var = sum((value - x_mean) ** 2 for value in xs)
    y_var = sum((value - y_mean) ** 2 for value in ys)
    if x_var <= 1e-24 or y_var <= 1e-24:
        result["note"] += " Correlation is undefined for constant or effectively constant returns."
        return result
    coefficient = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / math.sqrt(x_var * y_var)
    result["coefficient"] = max(-1.0, min(1.0, coefficient))
    result["from_date"], result["to_date"] = matched[0][0], matched[-1][1]
    return result
