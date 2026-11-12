"""Causal daily price structure, vectorized across independent stock rows.

All price outputs use split-neutral units. Pivot values become visible only on
their right-confirmation day; indices refer to the original pivot candle. Round
prices are formed in contemporary actual rupees before unit conversion. No
feature in this module reads beyond the current completed session.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _prior_extreme(a, window, high=True):
    """Full trailing window excluding the current bar (finite bars required)."""
    s, n = a.shape
    out = np.full((s, n), np.nan, np.float32)
    if n > window:
        view = np.lib.stride_tricks.sliding_window_view(a, window, axis=1)
        result = (np.max if high else np.min)(view[:, :-1], axis=-1)
        out[:, window:] = result
    return out


def _atr(high, low, close, length=14):
    previous = np.concatenate([np.full((len(close), 1), np.nan), close[:, :-1]], axis=1)
    tr = np.maximum(high - low, np.maximum(np.abs(high - previous), np.abs(low - previous)))
    if close.shape[1]:
        tr[:, 0] = high[:, 0] - low[:, 0]
    # Match pandas' adjust=False, min_periods=14 convention used by the research
    # indicators. Missing bars carry state but do not contribute warmup counts.
    out = np.full(close.shape, np.nan, np.float32)
    state = np.full(len(close), np.nan)
    count = np.zeros(len(close), int)
    for t in range(close.shape[1]):
        valid = np.isfinite(tr[:, t])
        seed = valid & ~np.isfinite(state)
        state[seed] = tr[seed, t]
        update = valid & ~seed
        state[update] += (tr[update, t] - state[update]) / length
        count += valid
        out[:, t] = np.where(valid & (count >= length), state, np.nan)
    return out


def _completed_periods(high, low, close, dates, kind):
    """Last completed calendar week/month, never current-period extrema.

    An initial partial period is withheld. A first Monday starts a complete
    observed week; a first weekday of a month starts a complete observed month.
    Subsequent periods are observed from their boundary regardless of holidays.
    """
    shape = close.shape
    out = [np.full(shape, np.nan, np.float32) for _ in range(3)]
    if not shape[1]:
        return out
    if kind == 'week':
        iso = dates.isocalendar()
        keys = np.asarray(iso['year'], int) * 100 + np.asarray(iso['week'], int)
        initial_complete = dates[0].weekday() == 0
    else:
        keys = dates.year.to_numpy() * 12 + dates.month.to_numpy()
        first_weekday = pd.offsets.BMonthBegin().rollback(dates[0].normalize())
        initial_complete = dates[0].normalize() == first_weekday
    cur_h = np.full(shape[0], -np.inf)
    cur_l = np.full(shape[0], np.inf)
    cur_c = np.full(shape[0], np.nan)
    previous = [np.full(shape[0], np.nan) for _ in range(3)]
    complete = initial_complete
    for t in range(shape[1]):
        if t and keys[t] != keys[t - 1]:
            if complete:
                valid = np.isfinite(cur_h) & np.isfinite(cur_l) & np.isfinite(cur_c)
                previous = [np.where(valid, x, np.nan) for x in (cur_h, cur_l, cur_c)]
            cur_h.fill(-np.inf)
            cur_l.fill(np.inf)
            cur_c.fill(np.nan)
            complete = True
        for result, prev in zip(out, previous):
            result[:, t] = prev
        valid = np.isfinite(high[:, t]) & np.isfinite(low[:, t]) & np.isfinite(close[:, t])
        cur_h = np.where(valid, np.maximum(cur_h, high[:, t]), cur_h)
        cur_l = np.where(valid, np.minimum(cur_l, low[:, t]), cur_l)
        cur_c = np.where(valid, close[:, t], cur_c)
    return out


class _PivotZones:
    """Bounded released-pivot zones with tolerance frozen at anchor release.

    At most 32 pivots from the last 252 sessions enter a zone. Each pivot is a
    distinct touch; strict pivots are naturally separated by > right-bar count.
    Membership and means are refreshed only when a pivot arrives or expires.
    """

    def __init__(self, stocks, size=32, history=252):
        self.price = np.full((stocks, size), np.nan)
        self.index = np.full((stocks, size), -1, int)
        self.tolerance = np.full((stocks, size), np.nan)
        self.center = np.full((stocks, size), np.nan)
        self.count = np.zeros((stocks, size), np.int16)
        self.pointer = np.zeros(stocks, int)
        self.history = history

    def update(self, event, values, indices, tolerance, t):
        expired = (self.index >= 0) & ((t - self.index) > self.history)
        changed = expired.any(axis=1) | event
        self.index[expired] = -1
        self.price[expired] = np.nan
        rows = np.flatnonzero(event)
        slots = self.pointer[rows]
        self.price[rows, slots] = values[rows]
        self.index[rows, slots] = indices[rows]
        self.tolerance[rows, slots] = tolerance[rows]
        self.pointer[rows] = (slots + 1) % self.price.shape[1]
        rows = np.flatnonzero(changed)
        if len(rows):
            values = self.price[rows]
            valid = np.isfinite(values)
            distance = np.abs(values[:, :, None] - values[:, None, :])
            members = (distance <= self.tolerance[rows, :, None]) & valid[:, :, None] & valid[:, None, :]
            counts = members.sum(axis=2)
            sums = np.sum(np.where(members, values[:, None, :], 0.), axis=2)
            self.center[rows] = np.divide(sums, counts, out=np.full(sums.shape, np.nan), where=counts > 0)
            self.count[rows] = counts

    def nearest(self, close, support):
        eligible = self.count >= 2
        eligible &= self.center <= close[:, None] if support else self.center >= close[:, None]
        distance = np.where(eligible, np.abs(self.center - close[:, None]), np.inf)
        slot = distance.argmin(axis=1)
        rows = np.arange(len(close))
        valid = np.isfinite(distance[rows, slot])
        return np.where(valid, self.center[rows, slot], np.nan), np.where(valid, self.count[rows, slot], 0)


def build_structure(panel, pivot=2, lookback=20, zone=.5, atr=None):
    """Return causal S x T structure arrays for neutral OHLCV ``panel``.

    ``pivot`` is both left and right confirmation width. ``lookback`` supplies
    the prior Donchian channel. ``zone`` is an ATR radius fixed separately when
    each cluster anchor is released. An optional supplied ATR avoids recomputing
    an indicator cache. Levels are float32, flags bool, and pivot indices int32.
    Missing/unavailable levels are NaN; unavailable indices and breakout age -1.
    """
    if not isinstance(pivot, (int, np.integer)) or pivot < 1:
        raise ValueError('pivot must be a positive integer')
    if not isinstance(lookback, (int, np.integer)) or lookback < 1:
        raise ValueError('lookback must be a positive integer')
    if not np.isfinite(zone) or zone <= 0:
        raise ValueError('zone must be finite and positive')
    data = panel['neutral']
    h, l, c = (np.asarray(data[k], float) for k in ['high', 'low', 'close'])
    if c.ndim != 2 or h.shape != c.shape or l.shape != c.shape:
        raise ValueError('neutral OHLC must have matching stock x date shapes')
    s, n = c.shape
    dates = pd.DatetimeIndex(panel['dates'])
    if len(dates) != n or not dates.is_monotonic_increasing or dates.has_duplicates:
        raise ValueError('dates must be unique, ascending and match OHLC columns')
    atr = _atr(h, l, c) if atr is None else np.asarray(atr, float)
    if atr.shape != c.shape:
        raise ValueError('atr must have the same shape as neutral OHLC')
    out = {}
    for key in ['pivot_low', 'prev_pivot_low', 'pivot_high', 'prev_pivot_high',
                'cluster_support', 'cluster_resistance', 'breakout_level',
                'fib_low', 'fib_high', 'avwap_low', 'avwap_high']:
        out[key] = np.full(c.shape, np.nan, np.float32)
    for key in ['pivot_low_idx', 'prev_pivot_low_idx', 'pivot_high_idx', 'prev_pivot_high_idx']:
        out[key] = np.full(c.shape, -1, np.int32)
    out['pivot_low_event'] = np.zeros(c.shape, bool)
    out['pivot_high_event'] = np.zeros(c.shape, bool)
    out['breakout_event'] = np.zeros(c.shape, bool)
    out['breakout_age'] = np.full(c.shape, -1, np.int16)
    out['cluster_support_touches'] = np.zeros(c.shape, np.int16)
    out['cluster_resistance_touches'] = np.zeros(c.shape, np.int16)
    out['donchian_high'] = _prior_extreme(h, lookback, True)
    out['donchian_low'] = _prior_extreme(l, lookback, False)
    # Strict comparisons exclude plateau pivots and any missing neighboring bar.
    if n > 2 * pivot:
        middle_low = l[:, pivot:n-pivot]
        middle_high = h[:, pivot:n-pivot]
        lows = np.isfinite(middle_low)
        highs = np.isfinite(middle_high)
        for shift in range(-pivot, pivot + 1):
            if shift:
                lows &= middle_low < l[:, pivot+shift:n-pivot+shift]
                highs &= middle_high > h[:, pivot+shift:n-pivot+shift]
        out['pivot_low_event'][:, 2*pivot:] = lows
        out['pivot_high_event'][:, 2*pivot:] = highs
    vol = np.asarray(data.get('volume', np.zeros_like(c)), float)
    if vol.shape != c.shape:
        raise ValueError('volume must have the same shape as neutral OHLC')
    typical = (h + l + c) / 3
    valid_volume = np.isfinite(typical) & np.isfinite(vol) & (vol > 0)
    volume = np.where(valid_volume, vol, 0.)
    weighted = np.where(valid_volume, typical, 0.) * volume
    cum_v = np.concatenate([np.zeros((s, 1)), np.cumsum(volume, axis=1)], axis=1)
    cum_pv = np.concatenate([np.zeros((s, 1)), np.cumsum(weighted, axis=1)], axis=1)
    last_low = np.full(s, np.nan)
    last_high = np.full(s, np.nan)
    previous_low = np.full(s, np.nan)
    previous_high = np.full(s, np.nan)
    low_idx = np.full(s, -1, int)
    high_idx = np.full(s, -1, int)
    previous_low_idx = np.full(s, -1, int)
    previous_high_idx = np.full(s, -1, int)
    fib_low = np.full(s, np.nan)
    fib_high = np.full(s, np.nan)
    frozen_break = np.full(s, np.nan)
    break_at = np.full(s, -100, int)
    low_zones, high_zones = _PivotZones(s), _PivotZones(s)
    rows = np.arange(s)
    for t in range(n):
        low_event = out['pivot_low_event'][:, t]
        high_event = out['pivot_high_event'][:, t]
        original = t - pivot
        previous_low = np.where(low_event, last_low, previous_low)
        previous_high = np.where(high_event, last_high, previous_high)
        previous_low_idx = np.where(low_event, low_idx, previous_low_idx)
        previous_high_idx = np.where(high_event, high_idx, previous_high_idx)
        if original >= 0:
            last_low = np.where(low_event, l[:, original], last_low)
            last_high = np.where(high_event, h[:, original], last_high)
            low_idx = np.where(low_event, original, low_idx)
            high_idx = np.where(high_event, original, high_idx)
        for name, state in [('pivot_low', last_low), ('prev_pivot_low', previous_low),
                            ('pivot_high', last_high), ('prev_pivot_high', previous_high),
                            ('pivot_low_idx', low_idx), ('prev_pivot_low_idx', previous_low_idx),
                            ('pivot_high_idx', high_idx), ('prev_pivot_high_idx', previous_high_idx)]:
            out[name][:, t] = state
        low_zones.update(low_event, last_low, low_idx, zone * atr[:, t], t)
        high_zones.update(high_event, last_high, high_idx, zone * atr[:, t], t)
        out['cluster_support'][:, t], out['cluster_support_touches'][:, t] = low_zones.nearest(c[:, t], True)
        out['cluster_resistance'][:, t], out['cluster_resistance_touches'][:, t] = high_zones.nearest(c[:, t], False)
        # A new confirmed high freezes an ordered bullish swing. A subsequent
        # confirmed pullback low cannot retroactively move its original anchor.
        ordered = high_event & (low_idx >= 0) & (low_idx < high_idx) & (last_high > last_low)
        fib_low = np.where(ordered, last_low, fib_low)
        fib_high = np.where(ordered, last_high, fib_high)
        out['fib_low'][:, t] = fib_low
        out['fib_high'][:, t] = fib_high
        for key, anchor in [('avwap_low', low_idx), ('avwap_high', high_idx)]:
            start = np.maximum(anchor, 0)
            den = cum_v[:, t+1] - cum_v[rows, start]
            num = cum_pv[:, t+1] - cum_pv[rows, start]
            out[key][:, t] = np.divide(num, den, out=np.full(s, np.nan), where=(anchor >= 0) & (den > 0))
        age = t - break_at
        active = age <= 5
        if t:
            level = out['donchian_high'][:, t]
            event = (~active) & np.isfinite(level) & (c[:, t] > level) & (c[:, t-1] <= level)
            frozen_break = np.where(event, level, frozen_break)
            break_at = np.where(event, t, break_at)
            age = t - break_at
            active = age <= 5
            out['breakout_event'][:, t] = event
        out['breakout_level'][:, t] = np.where(active, frozen_break, np.nan)
        out['breakout_age'][:, t] = np.where(active, age, -1)
    out['higher_high_higher_low'] = (out['pivot_low'] > out['prev_pivot_low']) & (out['pivot_high'] > out['prev_pivot_high'])
    out['retest_level'] = out['breakout_level']
    out['retest_age'] = out['breakout_age']
    for key, data_array in [('high', h), ('low', l), ('close', c)]:
        shifted = np.full(c.shape, np.nan, np.float32)
        shifted[:, 1:] = data_array[:, :-1]
        out['prev_day_' + key] = shifted
    for period in ['week', 'month']:
        values = _completed_periods(h, l, c, dates, period)
        for key, value in zip(['high', 'low', 'close'], values):
            out['prev_' + period + '_' + key] = value
    ph, pl, pc = (out['prev_day_' + k] for k in ['high', 'low', 'close'])
    pp = (ph + pl + pc) / 3
    out.update(floor_pivot=pp, floor_s1=2*pp-ph, floor_r1=2*pp-pl,
               floor_s2=pp-(ph-pl), floor_r2=pp+(ph-pl))
    for label, ratio in [('382', .382), ('500', .5), ('618', .618), ('400', .4), ('600', .6)]:
        out['fib_' + label] = out['fib_high'] - ratio * (out['fib_high'] - out['fib_low'])
    unit = np.asarray(panel.get('unit_factor', np.ones_like(c)), float)
    actual_close = np.asarray(panel.get('actual', data)['close'], float)
    if unit.shape != c.shape or actual_close.shape != c.shape:
        raise ValueError('actual close and unit_factor must match neutral OHLC')
    valid_unit = np.isfinite(unit) & (unit > 0) & np.isfinite(actual_close) & (actual_close > 0)
    step = np.select([actual_close < 100, actual_close < 500, actual_close < 1000, actual_close < 5000], [10., 50., 100., 500.], default=1000.)
    for label, amount in [('', step), ('10_', 10.), ('50_', 50.), ('100_', 100.)]:
        for key, rounding in [('support', np.floor), ('resistance', np.ceil)]:
            actual_level = rounding(actual_close / amount) * amount
            result = np.divide(actual_level, unit, out=np.full(c.shape, np.nan), where=valid_unit)
            out['round_' + label + key] = result.astype(np.float32)
    out['round_step'] = np.divide(step, unit, out=np.full(c.shape, np.nan), where=valid_unit).astype(np.float32)
    return out
