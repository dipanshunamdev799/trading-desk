"""Causal five-minute stock signals; no fills, portfolio selection or DB access.

Input timestamps are bar starts. `known_at` is bar start plus five minutes.
RVOL is supplied by the data pipeline and must already exclude the current day
from its historical same-clock denominator. move is fractional: .08 means 8%.
"""
from __future__ import annotations

import math
from datetime import time

import numpy as np
import pandas as pd

MECHANISMS = ('cross8', 'cross10', 'breakout8', 'vwap_reclaim8', 'exhaustion8', 'cross8_no_volume')
IST = 'Asia/Kolkata'


def make_signals(bars: pd.DataFrame, prev_close: float, rvol: pd.Series, *, as_of=None) -> list[dict]:
    """Return all six mechanisms as chronological, explicitly labelled rows.

    cross8/cross10/cross8_no_volume fire once per direction at the first eligible
    morning qualification, including stocks already above the threshold at the
    first eligible clock. Other mechanisms can recur; the portfolio engine owns
    no-reentry, simultaneous-position and daily-trade-count limits.

    `as_of` excludes incomplete observations when supplied. Without it, the caller
    is explicitly supplying completed historical bars. No system clock is read.
    The no-volume ablation disables only RVOL>=1.5, not RVOL availability, ranking
    or positive traded volume; report it as "volume gate off".
    """
    if not math.isfinite(float(prev_close)) or prev_close <= 0:
        raise ValueError('prev_close must be finite and positive')
    if not isinstance(bars.index, pd.DatetimeIndex) or bars.index.tz is None:
        raise ValueError('bars require a timezone-aware DatetimeIndex')
    if not bars.index.is_unique or not bars.index.is_monotonic_increasing:
        raise ValueError('bar starts must be unique and chronological')
    required = ('open', 'high', 'low', 'close', 'volume')
    if any(k not in bars for k in required):
        raise ValueError('bars require open/high/low/close/volume')
    if not isinstance(rvol, pd.Series) or not isinstance(rvol.index, pd.DatetimeIndex) or rvol.index.tz is None or not rvol.index.is_unique:
        raise ValueError('rvol requires a unique timezone-aware DatetimeIndex')
    local = bars.copy()
    local.index = local.index.tz_convert(IST)
    if len({x.date() for x in local.index}) > 1:
        raise ValueError('pass one trading session at a time')
    if any(x.minute % 5 or x.second or x.microsecond for x in local.index):
        raise ValueError('timestamps must be five-minute bar starts')
    local = local.loc[[time(9, 15) <= x.time() < time(15, 30) for x in local.index]]
    if as_of is not None:
        cutoff = pd.Timestamp(as_of)
        if cutoff.tzinfo is None:
            raise ValueError('as_of must be timezone aware')
        local = local.loc[local.index + pd.Timedelta(minutes=5) <= cutoff]
    if local.empty:
        return []
    values = local.loc[:, required].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values[:, :4] <= 0).any() or (values[:, 4] < 0).any():
        raise ValueError('nonfinite/nonpositive OHLC or invalid volume')
    if ((local.high < local[['open', 'close', 'low']].max(axis=1)) |
            (local.low > local[['open', 'close', 'high']].min(axis=1))).any():
        raise ValueError('inconsistent OHLC')
    rv = rvol.copy()
    rv.index = rv.index.tz_convert(IST)
    rv = pd.to_numeric(rv.reindex(local.index), errors='coerce')
    typical = (local.high + local.low + local.close) / 3
    vw = (typical * local.volume).cumsum() / local.volume.cumsum().replace(0, np.nan)
    move = local.close / float(prev_close) - 1
    prior_high = local.high.shift(1).rolling(3, min_periods=3).max()
    prior_low = local.low.shift(1).rolling(3, min_periods=3).min()
    fired = set()
    result = []
    for i, start in enumerate(local.index):
        known = start + pd.Timedelta(minutes=5)
        if not time(9, 30) <= known.time() <= time(11, 30):
            continue
        row = local.iloc[i]
        ratio = float(rv.iloc[i]) if pd.notna(rv.iloc[i]) else float('nan')
        if (row.volume <= 0 or row.high <= row.low or not math.isfinite(ratio) or ratio <= 0 or
                not math.isfinite(float(vw.iloc[i]))):
            continue
        change = float(move.iloc[i]);direction = 1 if change > 0 else -1
        aligned = direction * (row.close - vw.iloc[i]) > 0
        magnitude = abs(change)
        volume_ok = ratio >= 1.5
        contiguous2 = i >= 1 and start - local.index[i-1] == pd.Timedelta(minutes=5)
        contiguous3 = contiguous2 and i >= 2 and local.index[i-1] - local.index[i-2] == pd.Timedelta(minutes=5)
        contiguous4 = contiguous3 and i >= 3 and local.index[i-2] - local.index[i-3] == pd.Timedelta(minutes=5)
        rules = {}
        if aligned:
            rules['cross8'] = magnitude >= .08 and volume_ok
            rules['cross10'] = magnitude >= .10 and volume_ok
            rules['cross8_no_volume'] = magnitude >= .08
            rules['breakout8'] = (magnitude >= .08 and volume_ok and contiguous4 and
                (row.close > prior_high.iloc[i] if direction > 0 else row.close < prior_low.iloc[i]))
            previous_wrong = (contiguous2 and math.isfinite(float(vw.iloc[i-1])) and
                direction * (local.close.iloc[i-1] - vw.iloc[i-1]) <= 0)
            rules['vwap_reclaim8'] = magnitude >= .08 and volume_ok and previous_wrong
        directional_previous = (contiguous3 and all(direction * (local.close.iloc[j] - local.open.iloc[j]) > 0
                                                   for j in (i-2, i-1)))
        reversal = (contiguous2 and (row.close < local.low.iloc[i-1] if direction > 0 else row.close > local.high.iloc[i-1]))
        rules['exhaustion8'] = magnitude >= .08 and volume_ok and directional_previous and reversal
        for mechanism in MECHANISMS:
            if not rules.get(mechanism, False):
                continue
            side = -direction if mechanism == 'exhaustion8' else direction
            if mechanism in ('cross8', 'cross10', 'cross8_no_volume'):
                key = mechanism, side
                if key in fired:
                    continue
                fired.add(key)
            result.append(dict(known_at=known, side=side, mechanism=mechanism,
                               raw_price=float(row.close), move=change, rvol=ratio,
                               score=magnitude * min(ratio, 10.)))
    return result
