"""Descriptive 8->10 and 10->12 percentage-point stock-day extension study.

These are price-path events, not fills or P&L. Each threshold/direction chooses
the first completed morning qualification with RVOL>=1.5, including gappers.
The race starts at the raw next-bar open. Extension is +2 percentage points of
the prior close; the competing reversal is 1% against that raw entry. They are
different price distances. Entry already at/beyond extension is excluded.

At each later bar, opening gaps resolve before high/low. If both boundaries are
touched in an unresolved first-touch candle, reversal wins and ambiguity=1.
The endpoint open is included, but its bar's later high/low is not. Missing or
unobserved bars before a first touch censor that event. Horizons are 60 minutes
from entry and through 15:10 IST. Nested thresholds, repeated stock-days and the
two horizons are not independent observations.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import time
import math

import numpy as np
import pandas as pd

THRESHOLDS = (.08, .10)
HORIZONS = ('60min', '15:10')
RACE_OUTCOMES = ('extension_first', 'reversal_first', 'neither')
OTHER_OUTCOMES = ('already_at_extension', 'missing_next_open', 'censored')
IST = 'Asia/Kolkata'


def _ge(value,level):
    return value>=level-1e-12*max(1.,abs(value),abs(level))


def _le(value,level):
    return value<=level+1e-12*max(1.,abs(value),abs(level))


def _valid_bar(row):
    values = [row.get(k) for k in ('open', 'high', 'low', 'close', 'volume')]
    try:
        o, h, l, c, v = map(float, values)
    except (TypeError, ValueError):
        return False
    return (all(math.isfinite(x) for x in (o,h,l,c,v)) and min(o,h,l,c)>0 and v>0 and
            h>=max(o,l,c) and l<=min(o,h,c))


def _race(bars, entry_at, end, side, target, reversal):
    """Return first observable boundary outcome without using endpoint H/L."""
    for at in pd.date_range(entry_at, end, freq='5min'):
        if at not in bars.index:
            return dict(outcome='censored', ambiguous_count=0, touch_bar_start=None, touch_known_at=None)
        row = bars.loc[at]
        try:opening=float(row.open)
        except (ValueError,TypeError):opening=float('nan')
        if not math.isfinite(opening) or opening<=0:
            return dict(outcome='censored', ambiguous_count=0, touch_bar_start=None, touch_known_at=None)
        ext_open = _ge(opening,target) if side>0 else _le(opening,target)
        rev_open = _le(opening,reversal) if side>0 else _ge(opening,reversal)
        if ext_open or rev_open:
            return dict(outcome='reversal_first' if rev_open else 'extension_first', ambiguous_count=0,
                        touch_bar_start=at.isoformat(), touch_known_at=at.isoformat())
        if at == end:
            break
        if not _valid_bar(row):
            return dict(outcome='censored', ambiguous_count=0, touch_bar_start=None, touch_known_at=None)
        ext = _ge(float(row.high),target) if side>0 else _le(float(row.low),target)
        rev = _le(float(row.low),reversal) if side>0 else _ge(float(row.high),reversal)
        if ext or rev:
            return dict(outcome='reversal_first' if rev else 'extension_first', ambiguous_count=int(ext and rev),
                        touch_bar_start=at.isoformat(), touch_known_at=(at+pd.Timedelta(minutes=5)).isoformat())
    return dict(outcome='neither', ambiguous_count=0, touch_bar_start=None, touch_known_at=None)


def make_events(records) -> list[dict]:
    """Build JSON-native event rows from data.load_sessions records.

    Required record fields: bars, prev_close, rvol, key, day, symbol. Bars are
    timestamped by timezone-aware five-minute start; RVOL is a causal same-clock
    cumulative-volume ratio supplied by the data pipeline. No VWAP alignment or
    hindsight winner filter is applied to this descriptive event definition.
    """
    result = []
    for record in records:
        previous = float(record['prev_close'])
        if not math.isfinite(previous) or previous<=0:
            raise ValueError('prev_close must be finite and positive')
        bars = record['bars'].copy()
        if not isinstance(bars.index,pd.DatetimeIndex) or bars.index.tz is None:
            raise ValueError('event bars require timezone-aware starts')
        if not bars.index.is_unique or not bars.index.is_monotonic_increasing:
            raise ValueError('event bar starts must be unique and chronological')
        bars.index = bars.index.tz_convert(IST)
        if any(x.minute%5 or x.second or x.microsecond for x in bars.index):
            raise ValueError('event bars must start on five-minute boundaries')
        if any(x.date().isoformat()!=str(record['day']) for x in bars.index):
            raise ValueError('event bars must match the record session')
        if any(k not in bars for k in ('open','high','low','close','volume')):
            raise ValueError('event bars require OHLCV')
        bars = bars.loc[[time(9,15)<=x.time()<time(15,30) for x in bars.index]]
        rvol = record['rvol'].copy()
        if not isinstance(rvol,pd.Series) or not isinstance(rvol.index,pd.DatetimeIndex) or rvol.index.tz is None or not rvol.index.is_unique:
            raise ValueError('event RVOL requires a unique timezone-aware index')
        rvol.index = rvol.index.tz_convert(IST)
        rvol = pd.to_numeric(rvol.reindex(bars.index),errors='coerce')
        chosen = {}
        for at,bar in bars.iterrows():
            known = at+pd.Timedelta(minutes=5)
            if not time(9,30)<=known.time()<=time(11,30) or not _valid_bar(bar):
                continue
            ratio = float(rvol.loc[at]) if pd.notna(rvol.loc[at]) else float('nan')
            if not math.isfinite(ratio) or ratio<1.5:
                continue
            move = float(bar.close)/previous-1
            for threshold in THRESHOLDS:
                for side in (1,-1):
                    # Numerical tolerance only avoids rejecting an exact 8% or
                    # 10% decimal price represented just below its float value.
                    if side*move+1e-12>=threshold and (threshold,side) not in chosen:
                        chosen[(threshold,side)] = (at,known,float(bar.close),move,ratio)
        for (threshold,side),(signal_start,known,price,move,ratio) in sorted(chosen.items()):
            entry_at = known
            target = previous*(1+side*(threshold+.02))
            entry_bar = bars.loc[entry_at] if entry_at in bars.index else None
            try:entry_price=float(entry_bar.open) if entry_bar is not None else None
            except (ValueError,TypeError):entry_price=None
            if entry_price is not None and (not math.isfinite(entry_price) or entry_price<=0):entry_price=None
            reversal = entry_price*(1-side*.01) if entry_price is not None else None
            overshot = entry_price is not None and side*(entry_price-target)>=-1e-12
            direction = 'up' if side>0 else 'down'
            for horizon in HORIZONS:
                end = (entry_at+pd.Timedelta(minutes=60) if horizon=='60min' else
                       entry_at.normalize()+pd.Timedelta(hours=15,minutes=10))
                row = dict(key=record['key'],symbol=record.get('symbol',record['key']),day=str(record['day']),
                    threshold=threshold,extension_daily_return=threshold+.02,side=side,direction=direction,
                    horizon=horizon,known_at=known.isoformat(),signal_bar_start=signal_start.isoformat(),
                    raw_signal_price=price,move=move,rvol=ratio,prev_close=previous,
                    entry=entry_at.isoformat(),entry_at=entry_at.isoformat(),entry_price=entry_price,
                    target_price=target,reversal_price=reversal,horizon_end=end.isoformat(),
                    qualification_overshot=bool(side*(price-target)>=-1e-12),
                    entry_already_at_extension=bool(overshot))
                if entry_price is None:
                    event = dict(outcome='missing_next_open',ambiguous_count=0,touch_bar_start=None,touch_known_at=None)
                elif overshot:
                    event = dict(outcome='already_at_extension',ambiguous_count=0,touch_bar_start=None,touch_known_at=None)
                else:
                    event = _race(bars,entry_at,end,side,target,reversal)
                row.update(event)
                row['race_eligible'] = row['outcome'] in RACE_OUTCOMES
                row['event_id'] = f"{record['key']}|{record['day']}|{threshold:.2f}|{direction}|{horizon}"
                result.append(row)
    return sorted(result,key=lambda r:(r['day'],r['known_at'],r['key'],r['threshold'],r['side'],HORIZONS.index(r['horizon'])))


def summarize_events(rows) -> dict:
    """Summaries condition on the acquisition cohort and observed qualification.

    Filter rows to a development/validation/final date span before calling to
    get chronological summaries. Denominator excludes entry overshoots, missing
    entries and censored paths; all excluded counts remain visible.
    """
    grouped = defaultdict(list)
    for row in rows:
        if row['outcome'] not in RACE_OUTCOMES+OTHER_OUTCOMES:
            raise ValueError('Unknown event outcome')
        grouped[(float(row['threshold']),row['horizon'],row['direction'])].append(row)
    groups = []
    for (threshold,horizon,direction),items in sorted(grouped.items(),key=lambda x:(x[0][0],HORIZONS.index(x[0][1]),x[0][2])):
        counts = Counter(r['outcome'] for r in items)
        observed = sum(counts[o] for o in RACE_OUTCOMES)
        groups.append(dict(threshold=threshold,extension_daily_return=threshold+.02,horizon=horizon,direction=direction,
            qualifications=len(items),race_count=observed,
            **{o:counts[o] for o in RACE_OUTCOMES+OTHER_OUTCOMES},
            qualification_overshoots=sum(r.get('qualification_overshot',False) for r in items),
            ambiguous_count=sum(r['ambiguous_count'] for r in items),
            stock_days=len({(r['key'],r['day']) for r in items}),sessions=len({r['day'] for r in items}),
            extension_rate=counts['extension_first']/observed if observed else None,
            reversal_rate=counts['reversal_first']/observed if observed else None,
            neither_rate=counts['neither']/observed if observed else None))
    return dict(groups=groups,notes=[
        'Descriptive raw-price paths only; no fill, P&L, leverage or strategy-profitability claim.',
        'Extension is +2 percentage points of daily return from prior close; reversal is 1% of raw next-open entry.',
        'First RVOL-qualified completed morning observation per threshold/direction includes gappers; no VWAP filter.',
        'Entry already at/beyond extension, missing next opens and censored paths are excluded from race rates but counted.',
        'Endpoint open is included; its subsequent high/low is excluded. Unresolved first-touch dual-hit candles count reversal first.',
        'Thresholds, the two horizons, multiple stocks in one session and repeated stock-days are dependent observations.',
        'Rates are conditional on the acquired cohort and available data, not population probabilities for all NSE stocks.'])
