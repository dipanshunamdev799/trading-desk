"""Causal, session-anchored MACD/EMA/structure research signals.

Input timestamps are the START of complete five-minute candles. Output timestamps
are information-availability times: a 09:15--11:15 candle is known at 11:15.
No feature uses a not-yet-complete aggregation bucket or an unconfirmed pivot.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np
import pandas as pd

TZ = "Asia/Kolkata"
_AGG_CACHE: dict[tuple, pd.DataFrame] = {}
_FEATURE_CACHE: dict[tuple, pd.DataFrame] = {}
_LEVEL_CACHE: dict[tuple, tuple[pd.DataFrame, pd.DataFrame]] = {}
_REFERENCES: dict[int, pd.DataFrame] = {}


def clear_cache() -> None:
    _AGG_CACHE.clear()
    _FEATURE_CACHE.clear()
    _LEVEL_CACHE.clear()
    _REFERENCES.clear()


def _key(frame: pd.DataFrame) -> tuple:
    # References prevent Python object IDs being recycled while cached.
    _REFERENCES[id(frame)] = frame
    return (id(frame), len(frame), frame.index[0] if len(frame) else None,
            frame.index[-1] if len(frame) else None)


def aggregate(bars: pd.DataFrame, minutes: int, policy: str = "partial") -> pd.DataFrame:
    """Aggregate complete 5m bars inside the regular 09:15--15:30 session.

    partial: anchor at session open, retain the *completed* shortened last candle.
    full: same anchor, discard shortened last candles from indicators.
    right_anchor: anchor at close, retain the shortened first candle.
    Missing internal base bars invalidate their entire bucket. Special sessions
    outside regular hours are excluded and must be reported by the data audit.
    """
    if minutes not in (30, 60, 120, 240, 375):
        raise ValueError("Supported research timeframes: 30,60,120,240,375 minutes")
    if policy not in ("partial", "full", "right_anchor"):
        raise ValueError("policy must be partial, full or right_anchor")
    cache_key = (_key(bars), minutes, policy)
    if cache_key in _AGG_CACHE:
        return _AGG_CACHE[cache_key]
    d = bars.copy()
    idx = pd.DatetimeIndex(d.index)
    if idx.tz is None:
        raise ValueError("Base candles require timezone-aware timestamps")
    d.index = idx.tz_convert(TZ)
    if not d.index.is_monotonic_increasing or d.index.has_duplicates:
        raise ValueError("Base candles must be unique and sorted")
    elapsed = d.index.hour * 60 + d.index.minute - 555
    good = (elapsed >= 0) & (elapsed < 375) & (elapsed % 5 == 0)
    d = d.loc[good].copy()
    elapsed = np.asarray(elapsed[good])
    if "volume" not in d:
        d["volume"] = 0.0
    if not len(d):
        result = pd.DataFrame(columns=["open", "high", "low", "close", "volume", "duration", "bar_start"],
                              index=pd.DatetimeIndex([], tz=TZ, name="available_at"))
        _AGG_CACHE[cache_key] = result
        return result
    if policy == "right_anchor" and minutes != 375:
        remainder = 375 % minutes
        starts = np.where(elapsed < remainder, 0,
                          remainder + ((elapsed - remainder) // minutes) * minutes) if remainder else (elapsed // minutes) * minutes
        ends = np.where(elapsed < remainder, remainder, starts + minutes) if remainder else starts + minutes
    else:
        starts = (elapsed // minutes) * minutes
        ends = np.minimum(starts + minutes, 375)
    day = d.index.normalize()
    d["_bucket_start"] = day + pd.to_timedelta(555 + starts, unit="m")
    d["_bucket_end"] = day + pd.to_timedelta(555 + ends, unit="m")
    d["_base_start"] = d.index
    grouped = d.groupby("_bucket_end", sort=True)
    out = grouped.agg(open=("open", "first"), high=("high", "max"),
                      low=("low", "min"), close=("close", "last"), volume=("volume", "sum"),
                      bar_start=("_bucket_start", "first"), first=("_base_start", "first"),
                      last=("_base_start", "last"), count=("close", "size"))
    out["duration"] = (out.index.to_series() - out.bar_start).dt.total_seconds() / 60
    complete = ((out["count"] == out.duration / 5) & (out["first"] == out.bar_start)
                & (out["last"] + pd.Timedelta(minutes=5) == out.index))
    if policy == "full":
        complete &= out.duration == minutes
    result = out.loc[complete, ["open", "high", "low", "close", "volume", "duration", "bar_start"]].copy()
    result.index.name = "available_at"
    _AGG_CACHE[cache_key] = result
    return result


def features(aggregated: pd.DataFrame, ema: int = 100,
             macd: tuple[int, int, int] = (12, 26, 9), pivot: int = 2,
             slope: int = 5) -> pd.DataFrame:
    """Only trailing features; a pivot is released after `pivot` right bars."""
    key = (_key(aggregated), ema, tuple(macd), pivot, slope)
    if key in _FEATURE_CACHE:
        return _FEATURE_CACHE[key]
    d = aggregated.copy()
    previous = d.close.shift()
    tr = pd.concat([d.high - d.low, (d.high - previous).abs(), (d.low - previous).abs()], axis=1).max(axis=1)
    d["atr"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    d["ema"] = d.close.ewm(span=ema, adjust=False, min_periods=ema).mean()
    d["ema_fast"] = d.close.ewm(span=20, adjust=False, min_periods=20).mean()
    d["slope"] = (d.ema - d.ema.shift(slope)) / (slope * d.atr)
    fast, slow, signal = macd
    d["macd"] = (d.close.ewm(span=fast, adjust=False, min_periods=fast).mean()
                 - d.close.ewm(span=slow, adjust=False, min_periods=slow).mean())
    d["macd_signal"] = d.macd.ewm(span=signal, adjust=False, min_periods=signal).mean()
    d["hist"] = d.macd - d.macd_signal
    d["cross_up"] = (d["hist"] > 0) & (d["hist"].shift() <= 0)
    d["cross_down"] = (d["hist"] < 0) & (d["hist"].shift() >= 0)
    d["hist_change"] = d["hist"].diff()
    # Candidate lies p bars behind the CURRENT confirmation candle.
    high_event = d.high.shift(pivot)
    low_event = d.low.shift(pivot)
    high_ok = high_event.notna()
    low_ok = low_event.notna()
    for k in range(2 * pivot + 1):
        if k != pivot:
            high_ok &= high_event > d.high.shift(k)
            low_ok &= low_event < d.low.shift(k)
    high_event = high_event.where(high_ok)
    low_event = low_event.where(low_ok)
    d["pivot_high"] = high_event.ffill()
    d["pivot_low"] = low_event.ffill()
    d["previous_pivot_high"] = d.pivot_high.shift().where(high_event.notna()).ffill()
    d["previous_pivot_low"] = d.pivot_low.shift().where(low_event.notna()).ffill()
    d["bull_structure"] = (d.pivot_high > d.previous_pivot_high) & (d.pivot_low > d.previous_pivot_low)
    d["bear_structure"] = (d.pivot_high < d.previous_pivot_high) & (d.pivot_low < d.previous_pivot_low)
    d["range_high"] = d.high.shift().rolling(20, min_periods=20).max()
    d["range_low"] = d.low.shift().rolling(20, min_periods=20).min()
    d["break_up"] = (d.close > d.range_high) & (d.close.shift() <= d.range_high.shift())
    d["break_down"] = (d.close < d.range_low) & (d.close.shift() >= d.range_low.shift())
    d["break_level_up"] = d.range_high.where(d.break_up).ffill()
    d["break_level_down"] = d.range_low.where(d.break_down).ffill()
    seq = pd.Series(np.arange(len(d)), index=d.index, dtype=float)
    d["break_age_up"] = seq - seq.where(d.break_up).ffill()
    d["break_age_down"] = seq - seq.where(d.break_down).ffill()
    clock = pd.Series(d.index, index=d.index)
    d["break_time_up"] = clock.where(d.break_up).ffill()
    d["break_time_down"] = clock.where(d.break_down).ffill()
    # Daily/weekly group maxima are shifted by a complete day/week before mapping.
    # No current day's/week's eventual high enters a current decision.
    day = d.index.normalize()
    daily = d.groupby(day).agg(high=("high", "max"), low=("low", "min")).shift()
    d["prior_day_high"] = day.map(daily.high)
    d["prior_day_low"] = day.map(daily.low)
    week = d.index.tz_localize(None).to_period("W-FRI")
    weekly = d.groupby(week).agg(high=("high", "max"), low=("low", "min")).shift()
    d["prior_week_high"] = week.map(weekly.high)
    d["prior_week_low"] = week.map(weekly.low)
    d["source_at"] = d.index
    _FEATURE_CACHE[key] = d
    return d


def _event(mask: pd.Series) -> pd.Series:
    return mask & ~mask.shift(fill_value=False)


def make_signals(bars: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Return exact completed-LTF decisions with backward-only HTF synchronization."""
    cfg = {"htf": 240, "ltf": 120, "ema": 100, "slope": 5,
           "slope_filter": True, "slope_threshold": 0, "macd": [12, 26, 9],
           "pivot": 2, "zone": .5, "buffer": .2, "stop_mode": "swing",
           "structure_filter": False, "policy": "partial", **config}
    hi = features(aggregate(bars, cfg["htf"], cfg["policy"]), cfg["ema"],
                  tuple(cfg["macd"]), cfg["pivot"], cfg["slope"])
    lo = features(aggregate(bars, cfg["ltf"], cfg["policy"]), cfg["ema"],
                  tuple(cfg["macd"]), cfg["pivot"], cfg["slope"])
    if not len(lo) or not len(hi):
        return pd.DataFrame(columns=["side", "stop", "atr", "regime", "exit_long", "exit_short"], index=lo.index)
    d = pd.merge_asof(lo, hi.add_prefix("h_"), left_index=True, right_index=True,
                      direction="backward", allow_exact_matches=True)
    # Calendar barriers must include all regular-session prices even if the
    # indicator policy deliberately discards its last shortened HTF candle.
    level_key = _key(bars)
    if level_key not in _LEVEL_CACHE:
        daily = aggregate(bars, 375, "partial")[["high", "low"]].copy()
        week = daily.index.tz_localize(None).to_period("W-FRI")
        weekly = daily.groupby(week).agg(high=("high", "max"), low=("low", "min"))
        all_weeks = pd.period_range(bars.index[0].tz_convert(TZ).tz_localize(None),
                                   bars.index[-1].tz_convert(TZ).tz_localize(None), freq="W-FRI")
        weekly = weekly.reindex(all_weeks).shift()
        _LEVEL_CACHE[level_key] = daily, weekly
    daily, weekly = _LEVEL_CACHE[level_key]
    day_levels = pd.merge_asof(pd.DataFrame(index=d.index), daily, left_index=True,
                               right_index=True, direction="backward", allow_exact_matches=False)
    d["h_prior_day_high"], d["h_prior_day_low"] = day_levels.high, day_levels.low
    current_week = d.index.tz_localize(None).to_period("W-FRI")
    d["h_prior_week_high"] = current_week.map(weekly.high)
    d["h_prior_week_low"] = current_week.map(weekly.low)
    up = d.h_close > d.h_ema
    down = d.h_close < d.h_ema
    if cfg["slope_filter"]:
        up &= d.h_slope > cfg["slope_threshold"]
        down &= d.h_slope < -cfg["slope_threshold"]
    if cfg.get("dual_ema", False):
        up &= d.h_ema_fast > d.h_ema
        down &= d.h_ema_fast < d.h_ema
    cross_up, cross_down = d.cross_up, d.cross_down
    near_support = (d.low <= d.h_pivot_low + cfg["zone"] * d.h_atr) & (d.close >= d.h_pivot_low)
    near_resistance = (d.high >= d.h_pivot_high - cfg["zone"] * d.h_atr) & (d.close <= d.h_pivot_high)
    ema_touch_up = (d.low <= d.h_ema + cfg["zone"] * d.h_atr) & (d.close >= d.h_ema)
    ema_touch_down = (d.high >= d.h_ema - cfg["zone"] * d.h_atr) & (d.close <= d.h_ema)
    recover_up = (d.hist_change > 0) & (d.hist_change.shift() <= 0)
    recover_down = (d.hist_change < 0) & (d.hist_change.shift() >= 0)
    family = cfg.get("family", "A")
    if family == "baseline":
        buy = up & d.h_bull_structure.fillna(False) & (near_support | ema_touch_up) & cross_up
        sell = down & d.h_bear_structure.fillna(False) & (near_resistance | ema_touch_down) & cross_down
    elif family == "A":
        buy, sell = up & cross_up, down & cross_down
    elif family == "B":
        accel_up = (d.hist_change > 0) & (d.hist_change.shift() > 0)
        accel_down = (d.hist_change < 0) & (d.hist_change.shift() < 0)
        buy, sell = up & _event(accel_up), down & _event(accel_down)
    elif family == "C":
        body = (d.close - d.open).abs()
        reject_up = (d.close > d.open) & (np.minimum(d.open, d.close) - d.low >= body * .5)
        reject_down = (d.close < d.open) & (d.high - np.maximum(d.open, d.close) >= body * .5)
        buy = up & _event(near_support & reject_up & (d.hist_change > 0))
        sell = down & _event(near_resistance & reject_down & (d.hist_change < 0))
    elif family == "D":
        older_up = d.h_break_time_up < pd.Series(d.index, index=d.index)
        older_down = d.h_break_time_down < pd.Series(d.index, index=d.index)
        retest_up = ((d.low <= d.h_break_level_up + cfg["zone"] * d.h_atr)
                     & (d.close > d.h_break_level_up) & (d.h_break_age_up < 3) & older_up)
        retest_down = ((d.high >= d.h_break_level_down - cfg["zone"] * d.h_atr)
                       & (d.close < d.h_break_level_down) & (d.h_break_age_down < 3) & older_down)
        buy = up & _event(retest_up & (d["hist"] > 0))
        sell = down & _event(retest_down & (d["hist"] < 0))
    elif family == "D0":
        newly_closed = d.h_source_at.ne(d.h_source_at.shift())
        buy = up & d.h_break_up.fillna(False) & newly_closed & (d["hist"] > 0)
        sell = down & d.h_break_down.fillna(False) & newly_closed & (d["hist"] < 0)
    elif family == "E":
        buy, sell = up & ema_touch_up & recover_up, down & ema_touch_down & recover_down
    elif family == "F":
        buy, sell = up & (d.h_hist > 0) & cross_up, down & (d.h_hist < 0) & cross_down
    elif family == "G":
        buy, sell = up & cross_up & (d.macd > 0), down & cross_down & (d.macd < 0)
    elif family == "G_early":
        buy, sell = up & cross_up & (d.macd < 0), down & cross_down & (d.macd > 0)
    elif family in ("H", "structure_only"):
        break_up = (d.close > d.h_pivot_high) & (d.close.shift() <= d.h_pivot_high.shift())
        break_down = (d.close < d.h_pivot_low) & (d.close.shift() >= d.h_pivot_low.shift())
        if family == "H":
            buy, sell = up & break_up & (d["hist"] > 0), down & break_down & (d["hist"] < 0)
        else:
            buy, sell = break_up, break_down
    elif family == "I":
        strength = d.h_slope.abs()
        regime = cfg.get("regime_filter", "strong")
        allowed = strength >= .10 if regime == "strong" else ((strength >= .02) & (strength < .10))
        buy, sell = up & allowed & cross_up, down & allowed & cross_down
    elif family == "J":
        strong = d.h_slope.abs() >= .10
        moderate = (d.h_slope.abs() >= .02) & ~strong
        buy = up & ((strong & cross_up) | (moderate & ema_touch_up & recover_up))
        sell = down & ((strong & cross_down) | (moderate & ema_touch_down & recover_down))
    elif family == "ema_only":
        buy, sell = _event(up), _event(down)
    elif family == "macd_only":
        buy, sell = cross_up, cross_down
    elif family == "zero_cross":
        buy = up & (d.macd > 0) & (d.macd.shift() <= 0)
        sell = down & (d.macd < 0) & (d.macd.shift() >= 0)
    else:
        raise ValueError(f"Unknown strategy family: {family}")
    if cfg.get("structure_filter", False) and family != "baseline":
        buy &= d.h_bull_structure.fillna(False)
        sell &= d.h_bear_structure.fillna(False)
    if cfg.get("momentum_alignment", False):
        buy &= d.h_hist > 0
        sell &= d.h_hist < 0
    if cfg["stop_mode"] == "atr":
        long_stop = d.close - cfg.get("atr_stop", 1.5) * d.h_atr
        short_stop = d.close + cfg.get("atr_stop", 1.5) * d.h_atr
    else:
        long_stop = d.h_pivot_low - cfg["buffer"] * d.h_atr
        short_stop = d.h_pivot_high + cfg["buffer"] * d.h_atr
    # Distance is measured at decision time; engine rechecks executable entry risk.
    risk_long, risk_short = d.close - long_stop, short_stop - d.close
    valid_long = (risk_long >= cfg.get("min_stop_atr", .5) * d.h_atr) & (risk_long <= cfg.get("max_stop_atr", 5) * d.h_atr)
    valid_short = (risk_short >= cfg.get("min_stop_atr", .5) * d.h_atr) & (risk_short <= cfg.get("max_stop_atr", 5) * d.h_atr)
    above = pd.concat([d.h_pivot_high, d.h_prior_day_high, d.h_prior_week_high], axis=1)
    below = pd.concat([d.h_pivot_low, d.h_prior_day_low, d.h_prior_week_low], axis=1)
    target_long = above.where(above.gt(d.close, axis=0)).min(axis=1)
    target_short = below.where(below.lt(d.close, axis=0)).max(axis=1)
    if cfg.get("resistance_room", False):
        buy &= target_long.isna() | ((target_long - d.close) >= cfg.get("reward", 2) * risk_long)
        sell &= target_short.isna() | ((d.close - target_short) >= cfg.get("reward", 2) * risk_short)
    ready = d.atr.gt(0) & d.h_atr.gt(0)
    if family not in ("ema_only", "structure_only"):
        ready &= d.macd_signal.notna()
    side = np.select([buy.fillna(False) & valid_long & ready,
                      sell.fillna(False) & valid_short & ready], [1, -1], default=0)
    result = pd.DataFrame(index=d.index)
    result["side"] = side.astype(np.int8)
    result["stop"] = np.where(side > 0, long_stop, np.where(side < 0, short_stop, np.nan))
    result["atr"] = d.h_atr
    result["close"] = d.close
    strength = d.h_slope.abs()
    result["regime"] = np.select([strength >= .10, strength >= .02],
        [np.where(d.h_slope > 0, "strong_bull", "strong_bear"),
         np.where(d.h_slope > 0, "weak_bull", "weak_bear")], default="range")
    if cfg.get("exit") == "ema":
        result["exit_long"] = d.h_close < d.h_ema
        result["exit_short"] = d.h_close > d.h_ema
    else:
        result["exit_long"] = cross_down
        result["exit_short"] = cross_up
    if cfg.get("exit") == "ema":
        result["trail_stop_long"] = d.h_ema - cfg["buffer"] * d.h_atr
        result["trail_stop_short"] = d.h_ema + cfg["buffer"] * d.h_atr
    elif cfg.get("exit") == "structure":
        result["trail_stop_long"] = d.h_pivot_low - cfg["buffer"] * d.h_atr
        result["trail_stop_short"] = d.h_pivot_high + cfg["buffer"] * d.h_atr
    else:
        result["trail_stop_long"] = d.close - 2 * d.h_atr
        result["trail_stop_short"] = d.close + 2 * d.h_atr
    result["target_long"] = target_long
    result["target_short"] = target_short
    result["target"] = np.where(side > 0, result.target_long, np.where(side < 0, result.target_short, np.nan))
    result["trail_stop"] = np.where(side > 0, result.trail_stop_long,
                                     np.where(side < 0, result.trail_stop_short, np.nan))
    result["htf_available_at"] = d.h_source_at
    return result


def catalog() -> list[dict[str, Any]]:
    """Preregisterable small, hypothesis-led one-component-at-a-time grid.

    All variants are disclosed, including the original restrictive baseline.
    Additional exit interactions are limited to A/B/E, rather than an exhaustive
    Cartesian optimization across every parameter.
    """
    base = {"htf": 240, "ltf": 120, "ema": 100, "slope": 5,
            "slope_filter": True, "slope_threshold": 0, "macd": [12, 26, 9],
            "pivot": 2, "zone": .5, "buffer": .2, "reward": 2.0,
            "exit": "fixed", "stop_mode": "swing", "policy": "partial",
            "max_hold_sessions": 10, "risk_fraction": .005,
            "initial_capital": 1_000_000, "structure_filter": False}
    rows: list[dict[str, Any]] = []
    def add(name: str, family: str, **changes: Any) -> None:
        rows.append({**deepcopy(base), "id": name, "family": family, **changes})
    families = ["baseline", "A", "B", "C", "D", "D0", "E", "F", "G", "G_early", "H", "I", "J"]
    for family in families:
        add(f"{family}_base", family)
    for family in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]:
        for period in [20, 34, 50, 150, 200]:
            add(f"{family}_ema{period}", family, ema=period)
    for family in ["A", "B", "E"]:
        for period in [90, 110]:
            add(f"{family}_ema{period}", family, ema=period)
    for family in ["baseline", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]:
        for reward in [1, 1.5, 2.5, 3, 4]:
            add(f"{family}_r{reward}", family, reward=reward)
    for family in ["A", "E", "F"]:
        for htf, ltf in [(240, 60), (375, 240), (375, 120), (120, 30)]:
            add(f"{family}_tf{htf}_{ltf}", family, htf=htf, ltf=ltf)
    for family in ["A", "B", "E"]:
        for setting in [(8, 21, 5), (5, 35, 5), (16, 32, 9)]:
            add(f"{family}_macd{'_'.join(map(str, setting))}", family, macd=list(setting))
        for policy in ["full", "right_anchor"]:
            add(f"{family}_{policy}", family, policy=policy)
        for exit_kind in ["atr_trail", "ema", "macd", "time", "partial", "structure"]:
            add(f"{family}_exit_{exit_kind}", family, exit=exit_kind)
        add(f"{family}_atr_stop", family, stop_mode="atr")
        add(f"{family}_no_slope", family, slope_filter=False)
        add(f"{family}_structure", family, structure_filter=True)
        add(f"{family}_dual_ema", family, dual_ema=True)
    for family in ["A", "C", "E"]:
        for pivot in [1, 3]:
            add(f"{family}_pivot{pivot}", family, pivot=pivot)
        if family != "A":
            for zone in [.25, 1.0]:
                add(f"{family}_zone{zone}", family, zone=zone)
        for buffer in [0., .4]:
            add(f"{family}_buffer{buffer}", family, buffer=buffer)
    for slope in [1, 10]:
        add(f"A_slope{slope}", "A", slope=slope)
    for threshold in [.02, .10]:
        add(f"A_slope_threshold{threshold}", "A", slope_threshold=threshold)
    add("I_weak", "I", regime_filter="weak")
    add("A_resistance_room", "A", resistance_room=True)
    for family in ["ema_only", "macd_only", "structure_only"]:
        add(f"{family}_base", family, stop_mode="atr")
    add("zero_cross_base", "zero_cross")
    assert len({row["id"] for row in rows}) == len(rows)
    return rows

