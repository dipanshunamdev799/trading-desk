"""Frozen daily long-only hypothesis catalog and causal panel signal generation.

The grid is mechanism-first: five documented oscillator tuples, three broad EMA
pairs or structural settings, and one-factor execution/filter changes around each
family's central control. It deliberately does not form a Cartesian product.
All decisions use completed daily bars. Weekly values are conservatively released
on the first observed session of the following calendar week. Neighbors have no
access to outcomes and are explicitly marked for development-only selection.
"""
from __future__ import annotations

import hashlib
import json
import numpy as np
import pandas as pd


OSCILLATORS = ((5, 13, 4), (8, 21, 5), (12, 26, 9), (16, 32, 9), (24, 52, 18))
EMA_PAIRS = ((9, 20), (9, 21), (20, 50), (20, 100), (50, 200))
FILTERS = ('volume', 'adx', 'rsi', 'volatility', 'market', 'rs', 'breadth', 'sector')
EXECUTION = dict(exit='fixed', stop_mode='atr', stop_atr=2., buffer=.2,
                 reward=2., max_hold_sessions=10, risk_fraction=.005)


def lag(a, n=1):
    a = np.asarray(a)
    out = np.full(a.shape, np.nan, dtype=float)
    if n == 0:
        return a.copy()
    if n < a.shape[-1]:
        out[..., n:] = a[..., :-n]
    return out


def rolling(a, window, how='mean'):
    """Trailing complete windows; no per-stock pandas objects."""
    a = np.asarray(a, float)
    out = np.full_like(a, np.nan)
    window = int(window)
    if a.shape[-1] < window:
        return out
    if how in ('sum', 'mean', 'std'):
        good = np.isfinite(a)
        z = np.where(good, a, 0.)
        cs = np.concatenate([np.zeros((*a.shape[:-1], 1)), np.cumsum(z, axis=-1)], axis=-1)
        count = np.concatenate([np.zeros((*a.shape[:-1], 1)), np.cumsum(good, axis=-1)], axis=-1)
        val = cs[..., window:] - cs[..., :-window]
        ok = (count[..., window:] - count[..., :-window]) == window
        if how == 'mean':
            val /= window
        elif how == 'std':
            sq = np.concatenate([np.zeros((*a.shape[:-1], 1)), np.cumsum(z*z, axis=-1)], axis=-1)
            val = np.sqrt(np.maximum((sq[..., window:] - sq[..., :-window])/window - (val/window)**2, 0.))
        out[..., window-1:] = np.where(ok, val, np.nan)
    else:
        view = np.lib.stride_tricks.sliding_window_view(a, window, axis=-1)
        fn = {'min': np.min, 'max': np.max, 'median': np.median}[how]
        out[..., window-1:] = fn(view, axis=-1)
    return out


def smooth(a, period, alpha=None):
    """SMA-seeded exponential/Wilder average; missing observations reset state."""
    a = np.asarray(a, float)
    period = int(period)
    alpha = 2./(period+1) if alpha is None else alpha
    out = np.full_like(a, np.nan)
    value = np.zeros(a.shape[0]); total = value.copy(); count = np.zeros(a.shape[0], int)
    for t in range(a.shape[1]):
        x = a[:, t]; valid = np.isfinite(x)
        count = np.where(valid, count+1, 0)
        total = np.where(valid, total+x, 0.)
        seed = valid & (count == period)
        live = valid & (count > period)
        value[seed] = total[seed]/period
        value[live] += alpha*(x[live]-value[live])
        out[:, t] = np.where(valid & (count >= period), value, np.nan)
    return out


def _ema(f, period):
    period = int(period)
    if period not in f['ema']:
        f['ema'][period] = smooth(f['close'], period)
    return f['ema'][period]


def _kama(f, period):
    period = int(period)
    if period not in f['kama']:
        c = f['close']; displacement = np.abs(c-lag(c, period))
        travel = rolling(np.abs(c-lag(c)), period, 'sum')
        er = np.divide(displacement, travel, out=np.zeros_like(c), where=travel > 0)
        sc = (er*(2/3-2/31)+2/31)**2
        out = np.full_like(c, np.nan); value = np.full(c.shape[0], np.nan)
        for t in range(c.shape[1]):
            valid = np.isfinite(c[:, t]) & np.isfinite(travel[:, t])
            seed = valid & ~np.isfinite(value)
            value[seed] = c[seed, t]
            update = valid & ~seed
            value[update] += sc[update, t]*(c[update, t]-value[update])
            value[~valid] = np.nan
            out[:, t] = value
        f['kama'][period] = out
    return f['kama'][period]


def _osc(f, fast, slow, signal, ppo=False):
    key = (int(fast), int(slow), int(signal), bool(ppo))
    if key not in f['osc']:
        a, b = _ema(f, fast), _ema(f, slow)
        line = a-b
        if ppo:
            line = np.divide(100*line, b, out=np.full_like(line, np.nan), where=b > 0)
        sig = smooth(line, signal)
        f['osc'][key] = (line, sig, line-sig)
    return f['osc'][key]


def _completed_week_closes(c, dates):
    """Compact completed calendar weeks and their next-week release indices."""
    dates = pd.DatetimeIndex(dates)
    naive = dates.tz_localize(None) if dates.tz is not None else dates
    periods = naive.to_period('W-SUN').asi8
    if not len(periods):
        return np.asarray([], dtype=int), c[:, :0].copy()
    starts = np.r_[0, np.flatnonzero(periods[1:] != periods[:-1])+1]
    # Only weeks followed by an observed new week are complete for release.
    closes = c[:, starts[1:]-1].copy()
    if closes.shape[1] and dates[0].weekday() != 0:
        closes[:, 0] = np.nan  # Do not treat an initial partial history as a week.
    return starts, closes


def _weekly_averages(c, dates, fast=10, slow=30):
    """Prior complete calendar week only; an unfinished tail is never released."""
    starts, closes = _completed_week_closes(c, dates)
    wf = smooth(closes, fast); ws = smooth(closes, slow)
    a = np.full_like(c, np.nan); b = a.copy()
    for j in range(1, len(starts)):
        end = starts[j+1] if j+1 < len(starts) else c.shape[1]
        a[:, starts[j]:end] = wf[:, j-1, None]
        b[:, starts[j]:end] = ws[:, j-1, None]
    return a, b


def _weekly_oscillator(c, dates, fast=12, slow=26, signal=9):
    """Weekly MACD evaluated on completed weeks, released in the following week."""
    starts, closes = _completed_week_closes(c, dates)
    line = smooth(closes, fast)-smooth(closes, slow)
    sig = smooth(line, signal)
    result = [np.full_like(c, np.nan) for _ in range(3)]
    for j in range(1, len(starts)):
        end = starts[j+1] if j+1 < len(starts) else c.shape[1]
        for out, weekly in zip(result, (line, sig, line-sig)):
            out[:, starts[j]:end] = weekly[:, j-1, None]
    return tuple(result)


def build_features(panel):
    """Build shared indicators once; entry/EMA/structure caches populate lazily."""
    n = panel['neutral']
    o, h, l, c, v = (np.asarray(n[k], float) for k in ('open', 'high', 'low', 'close', 'volume'))
    prev = lag(c)
    tr = np.fmax(h-l, np.fmax(np.abs(h-prev), np.abs(l-prev)))
    atr = smooth(tr, 14, 1/14)
    change = c-prev
    gain = smooth(np.maximum(change, 0), 14, 1/14)
    loss = smooth(np.maximum(-change, 0), 14, 1/14)
    rs = np.divide(gain, loss, out=np.full_like(c, np.inf), where=loss > 0)
    rsi = np.where(np.isfinite(gain), np.where((gain == 0) & (loss == 0), 50., 100-100/(1+rs)), np.nan)
    up = h-lag(h); down = lag(l)-l
    plus = smooth(np.where((up > down) & (up > 0), up, 0), 14, 1/14)
    minus = smooth(np.where((down > up) & (down > 0), down, 0), 14, 1/14)
    dx = np.divide(100*np.abs(plus-minus), plus+minus, out=np.zeros_like(c), where=(plus+minus) > 0)
    dx[~np.isfinite(plus+minus)] = np.nan
    adx = smooth(dx, 14, 1/14)
    f = dict(open=o, high=h, low=l, close=c, volume=v, atr=atr, rsi=rsi, adx=adx,
             ema={}, kama={}, osc={}, structure={}, channel={}, entries={}, weekly={}, weekly_osc={})
    f['volume20'] = rolling(lag(v), 20)
    f['return20'] = c/lag(c, 20)-1
    f['return60'] = c/lag(c, 60)-1
    market = np.asarray(panel.get('nifty', np.full(c.shape[1], np.nan)), float).reshape(1, -1)
    f['market'] = market
    f['market50'] = smooth(market, 50)
    f['market200'] = smooth(market, 200)
    f['market_return60'] = market/lag(market, 60)-1
    above = c > _ema(f, 50)
    valid = np.isfinite(_ema(f, 50)) & np.isfinite(c)
    count = valid.sum(axis=0)
    f['breadth'] = np.divide((above & valid).sum(axis=0), count, out=np.full(c.shape[1], np.nan), where=count > 0)
    # Peer momentum excludes the stock itself. Missing sector labels have no peer
    # signal rather than silently turning the sector filter into a market filter.
    sectors = panel.get('sector', [None]*c.shape[0])
    peer = np.full_like(c, np.nan)
    for sector in set(x for x in sectors if x is not None and not pd.isna(x) and str(x).strip()):
        ids = np.asarray([i for i, x in enumerate(sectors) if x == sector], dtype=int)
        a = f['return20'][ids]; valid = np.isfinite(a)
        total = np.nansum(a, axis=0); count = valid.sum(axis=0)
        for i, row in zip(ids, a):
            own = np.isfinite(row); denom = count-own
            peer[i] = np.divide(total-np.where(own, row, 0), denom,
                                out=np.full(c.shape[1], np.nan), where=denom > 0)
    f['sector_momentum'] = peer
    return f


def _structure(panel, f, pivot=2):
    pivot = int(pivot)
    if pivot not in f['structure']:
        from .structure import build_structure
        f['structure'][pivot] = build_structure(panel, pivot=pivot, lookback=20, zone=.5, atr=f['atr'])
    return f['structure'][pivot]


def _channel(f, period):
    period = int(period)
    if period not in f['channel']:
        f['channel'][period] = (rolling(lag(f['high']), period, 'max'), rolling(lag(f['low']), period, 'min'))
    return f['channel'][period]


def _cross(a, b=0.):
    return (a > b) & (lag(a) <= (lag(b) if isinstance(b, np.ndarray) else b))


def _rejection(f, level, zone=.5):
    c, l, o, h, a = (f[k] for k in ('close', 'low', 'open', 'high', 'atr'))
    lower_wick = np.minimum(o, c)-l
    return (np.abs(l-level) <= zone*a) & (c > level) & (c > o) & (lower_wick >= .25*(h-l))


def _at_indices(a, indices):
    idx = np.where(np.isfinite(indices), indices, 0).astype(int)
    result = np.take_along_axis(a, np.clip(idx, 0, a.shape[1]-1), axis=1)
    return np.where(np.isfinite(indices) & (indices >= 0), result, np.nan)


def _divergence(f, structure, oscillator, hidden=False):
    p, q = structure['pivot_low'], structure['prev_pivot_low']
    i, j = structure['pivot_low_idx'], structure['prev_pivot_low_idx']
    current, previous = _at_indices(oscillator, i), _at_indices(oscillator, j)
    price = (p > q) if hidden else (p < q)
    momentum = (current < previous) if hidden else (current > previous)
    return structure['pivot_low_event'] & (i > j) & (j >= 0) & price & momentum


def _entry(panel, config, f):
    family = config['family']; p = config.get('params', {})
    # Flattened values are authoritative for neighbors and runner compatibility.
    p = {**p, **{k: v for k, v in config.items() if k not in ('params', 'description')}}
    key = (family, json.dumps({k: p[k] for k in ENTRY_KEYS if k in p}, sort_keys=True))
    if key in f['entries']:
        return f['entries'][key]
    c, o, h, l, a = (f[k] for k in ('close', 'open', 'high', 'low', 'atr'))
    fast, slow, sig = int(p.get('fast', 12)), int(p.get('slow', 26)), int(p.get('signal', 9))
    zone = float(p.get('zone', .5)); pivot = int(p.get('pivot', 2))
    level = np.full_like(c, np.nan)
    if family.startswith(('macd_', 'ppo_')):
        ppo = family.startswith('ppo_')
        line, signal, hist = _osc(f, fast, slow, sig, ppo)
        kind = family.split('_', 1)[1]
        cross = _cross(line, signal)
        if kind == 'cross': entry = cross
        elif kind == 'zero_cross': entry = _cross(line)
        elif kind == 'hist_recovery': entry = (hist > lag(hist)) & (lag(hist) <= lag(hist, 2)) & (hist < 0)
        elif kind == 'hist_accel': entry = (hist > lag(hist)) & (lag(hist) > lag(hist, 2)) & (lag(hist, 2) <= lag(hist, 3))
        elif kind == 'strength_cross':
            strength = np.abs(line-signal)/(np.maximum(a/c*100, 1e-20) if ppo else np.maximum(a, 1e-20))
            entry = cross & (strength >= float(p.get('strength', .05)))
        elif kind == 'above_zero': entry = cross & (line > 0)
        elif kind == 'below_zero': entry = cross & (line < 0)
        elif kind == 'weekly':
            wk = (int(p.get('weekly_fast', 12)), int(p.get('weekly_slow', 26)), int(p.get('weekly_signal', 9)))
            if wk not in f['weekly_osc']:
                f['weekly_osc'][wk] = _weekly_oscillator(c, panel['dates'], *wk)
            wl, ws, _ = f['weekly_osc'][wk]
            entry = cross & (wl > ws)
        elif kind in ('divergence', 'hidden_divergence'):
            s = _structure(panel, f, pivot)
            entry = _divergence(f, s, line, kind == 'hidden_divergence'); level = s['pivot_low']
        else: raise ValueError('Unknown oscillator family '+family)
    elif family.startswith('ema_'):
        ef, es = _ema(f, fast), _ema(f, slow)
        trend = (ef > es) & (es > lag(es, 3))
        kind = family[4:]
        if kind == 'cross': entry = _cross(ef, es)
        elif kind == 'reclaim': entry = _cross(c, ef) & trend
        elif kind == 'pullback': entry = _rejection(f, ef, zone) & trend
        elif kind == 'contraction':
            prior_range = rolling(lag(h-l), 5)
            entry = (prior_range < float(p.get('contraction', .8))*lag(a)) & (c > lag(h)) & trend
        elif kind == 'ribbon':
            mid = _ema(f, int(p.get('middle', 20)))
            stacked = (ef > mid) & (mid > es) & (es > lag(es, 3))
            entry = stacked & ~np.asarray(lag(stacked.astype(float)) == 1)
        elif kind == 'slope':
            normalized = (ef-lag(ef, 3))/a
            entry = _cross(normalized, float(p.get('slope', .25))) & (c > es)
        elif kind == 'weekly':
            wk = (int(p.get('weekly_fast', 10)), int(p.get('weekly_slow', 30)))
            if wk not in f['weekly']: f['weekly'][wk] = _weekly_averages(c, panel['dates'], *wk)
            wf, ws = f['weekly'][wk]
            entry = _cross(c, ef) & trend & (wf > ws)
        else: raise ValueError('Unknown EMA family '+family)
        level = es
    elif family.startswith('kama_'):
        kf, ks = _kama(f, fast), _kama(f, slow)
        trend = (kf > ks) & (ks > lag(ks, 3))
        if family == 'kama_cross': entry = _cross(kf, ks)
        elif family == 'kama_reclaim': entry = _cross(c, kf) & trend
        else: entry = _rejection(f, kf, zone) & trend
        level = ks
    elif family == 'donchian_breakout':
        top, _ = _channel(f, p.get('lookback', 20))
        level = top
        entry = (c > top+float(p.get('break_buffer', 0))*a) & (lag(c) <= lag(top+float(p.get('break_buffer', 0))*a))
    else:
        s = _structure(panel, f, pivot)
        line, signal, hist = _osc(f, fast, slow, sig)
        ef, es = _ema(f, 20), _ema(f, 50)
        trend = (ef > es) & (es > lag(es, 3))
        recovery = (hist > lag(hist)) & (lag(hist) <= lag(hist, 2))
        level = s['pivot_low']
        if family == 'pivot_bounce': entry = _rejection(f, level, zone)
        elif family == 'cluster_bounce':
            level = s['cluster_support']
            entry = _rejection(f, level, zone) & (s['cluster_support_touches'] >= int(p.get('touches', 2)))
        elif family in ('breakout_retest', 'role_reversal'):
            level = s['retest_level']; age = s['retest_age']
            entry = (age >= 1) & (age <= int(p.get('retest_window', 5))) & _rejection(f, level, zone)
            if family == 'role_reversal': entry &= (lag(c) > lag(level)) & trend
        elif family == 'support_sweep':
            entry = (l < level-float(p.get('sweep_buffer', .1))*a) & (c > level) & (c > o)
        elif family in ('previous_day', 'previous_week', 'previous_month'):
            period = family.split('_')[1]; level = s['prev_'+period+'_low']
            entry = _rejection(f, level, zone)
        elif family == 'floor_pivot':
            level = s['floor_'+p.get('floor_level', 's1')]
            entry = _rejection(f, level, zone)
        elif family == 'fib_pullback':
            ratio = float(p.get('ratio', .5)); level = s['fib_high']-ratio*(s['fib_high']-s['fib_low'])
            entry = _rejection(f, level, zone) & (s['fib_high'] > s['fib_low'])
        elif family == 'round_bounce':
            level = s['round_support']; entry = _rejection(f, level, zone)
        elif family == 'anchored_vwap':
            level = s['avwap_low']; entry = _cross(c, level) & trend
        elif family == 'htf_confluence':
            level = s['prev_week_low']
            near = np.abs(level-s['pivot_low']) <= zone*a
            entry = _rejection(f, level, zone) & near
        elif family == 'hybrid_trend_macd_support': entry = _cross(line, signal) & trend & (c-level <= 2*a) & (c > level)
        elif family == 'hybrid_support_hist': entry = _rejection(f, level, zone) & recovery
        elif family == 'hybrid_reclaim_zero':
            level = ef
            entry = _cross(c, ef) & trend & (line > 0)
        elif family == 'hybrid_breakout_momentum':
            level, _ = _channel(f, p.get('lookback', 20))
            entry = _cross(c, level) & trend & (hist > 0)
        elif family == 'hybrid_divergence_support':
            entry = _divergence(f, s, line) & (np.abs(s['pivot_low']-s['cluster_support']) <= zone*a)
        elif family == 'hybrid_ribbon_pullback':
            middle = _ema(f, int(p.get('middle', 20)))
            top, bottom = _ema(f, fast), _ema(f, slow)
            level = middle
            entry = _rejection(f, middle, zone) & (top > middle) & (middle > bottom) & (bottom > lag(bottom, 3))
        elif family == 'hybrid_sweep_reversal': entry = (l < level) & (c > level) & (c > o) & recovery
        else: raise ValueError('Unknown family '+family)
    entry = np.asarray(entry, bool) & np.isfinite(c) & np.isfinite(a) & (a > 0)
    f['entries'][key] = (entry, level)
    return entry, level


def generate(panel, config, features=None):
    """Return completed-day decisions in neutral share units for next-open fills."""
    f = build_features(panel) if features is None else features
    entry, level = _entry(panel, config, f)
    entry = entry.copy()
    which = config.get('filter', config.get('params', {}).get('filter', 'none'))
    c, a = f['close'], f['atr']
    if which == 'volume': entry &= f['volume'] >= 1.25*f['volume20']
    elif which == 'adx': entry &= f['adx'] >= 20
    elif which == 'rsi': entry &= (f['rsi'] >= 40) & (f['rsi'] <= 70)
    elif which == 'volatility': entry &= (a/c >= .01) & (a/c <= .06)
    elif which == 'market': entry &= (f['market'] > f['market200']) & (f['market50'] > f['market200'])
    elif which == 'rs': entry &= f['return60'] > f['market_return60']
    elif which == 'breadth': entry &= f['breadth'][None, :] >= .5
    elif which == 'sector': entry &= f['sector_momentum'] > 0
    elif which != 'none': raise ValueError('Unknown single-factor filter '+str(which))
    fast = int(config.get('fast', 12)); slow = int(config.get('slow', 26)); sig = int(config.get('signal', 9))
    line, signal, _ = _osc(f, fast, slow, sig, config['family'].startswith('ppo_'))
    e20, e50, e200 = _ema(f, 20), _ema(f, 50), _ema(f, 200)
    mode = config.get('exit', 'fixed')
    exit_signal = np.zeros_like(entry)
    if mode == 'macd': exit_signal = (line < signal) & (lag(line) >= lag(signal))
    elif mode == 'ema': exit_signal = c < e20
    elif mode == 'trend': exit_signal = (c < e50) | (e50 < e200)
    regime = np.zeros_like(entry, dtype=np.int8)
    valid = np.isfinite(e200)
    regime[valid & (e50 > e200) & (c > e200)] = 1
    regime[valid & ((e50 < e200) | (c < e200))] = -1
    if config.get('stop_mode') == 'swing':
        level = _structure(panel, f, int(config.get('pivot', 2)))['pivot_low']
    return dict(entry=entry, exit=exit_signal, level=level, atr=a, regime=regime, trail=e20)


ENTRY_KEYS = ('fast', 'slow', 'signal', 'strength', 'zone', 'pivot', 'middle', 'contraction', 'slope',
              'weekly_fast', 'weekly_slow', 'weekly_signal', 'lookback', 'break_buffer', 'touches', 'retest_window',
              'sweep_buffer', 'floor_level', 'ratio')


def _config(family, params, description, variant='control', **execution):
    flat = {**EXECUTION, 'filter': 'none', **params, **execution}
    identity = json.dumps([family, flat], sort_keys=True, separators=(',', ':'))
    ident = family+'_'+hashlib.sha256(identity.encode()).hexdigest()[:12]
    return dict(id=ident, family=family, description=description, variant=variant,
                params=flat.copy(), **flat)


def _family_grids():
    """Mechanism-coherent grids frozen before observing any simulated outcome."""
    out = []
    descriptions = dict(cross='signal-line bullish crossover', zero_cross='oscillator zero-line recovery',
                        hist_recovery='first histogram recovery below zero', hist_accel='new two-bar histogram acceleration',
                        strength_cross='ATR-normalized crossover strength', above_zero='above-zero crossover continuation',
                        below_zero='below-zero crossover reversal', divergence='released regular bullish divergence',
                        hidden_divergence='released hidden bullish divergence',
                        weekly='daily signal cross aligned with completed-week MACD momentum')
    for oscillator in ('macd', 'ppo'):
        kinds = tuple(descriptions) if oscillator == 'macd' else tuple(descriptions)[:7]
        for kind in kinds:
            grid = [dict(fast=a, slow=b, signal=s) for a, b, s in OSCILLATORS]
            if kind == 'strength_cross':
                grid = [{**p, 'strength': .05} for p in grid]
            if kind in ('divergence', 'hidden_divergence'):
                grid = [{**p, 'pivot': 2} for p in grid]
            if kind == 'weekly':
                grid = [{**p, 'weekly_fast': 12, 'weekly_slow': 26, 'weekly_signal': 9} for p in grid]
            out.append((oscillator+'_'+kind, grid, oscillator.upper()+' '+descriptions[kind]))
    for kind in ('cross', 'reclaim', 'pullback', 'contraction', 'slope', 'weekly'):
        extras = {'pullback': dict(zone=.5), 'contraction': dict(contraction=.8),
                  'slope': dict(slope=.25), 'weekly': dict(weekly_fast=10, weekly_slow=30)}.get(kind, {})
        out.append(('ema_'+kind, [dict(fast=a, slow=b, **extras) for a, b in EMA_PAIRS], 'EMA '+kind.replace('_', ' ')))
    out.append(('ema_ribbon', [dict(fast=a, middle=b, slow=c) for a, b, c in ((5, 13, 34), (9, 20, 50), (20, 50, 100))], 'new aligned EMA ribbon'))
    for kind in ('cross', 'reclaim', 'pullback'):
        extras = dict(zone=.5) if kind == 'pullback' else {}
        out.append(('kama_'+kind, [dict(fast=a, slow=b, **extras) for a, b in ((5, 20), (10, 30), (20, 50))], 'efficiency-ratio KAMA '+kind))
    structural = {
      'pivot_bounce': [dict(pivot=x, zone=.5) for x in (1, 2, 3, 5)],
      'cluster_bounce': [dict(pivot=2, zone=z, touches=t) for z, t in ((.25, 2), (.5, 2), (.75, 3))],
      'donchian_breakout': [dict(lookback=w, break_buffer=b) for w, b in ((20, 0), (55, .25), (100, .5))],
      'breakout_retest': [dict(pivot=2, zone=.5, retest_window=w) for w in (1, 3, 5)],
      'role_reversal': [dict(pivot=2, zone=z, retest_window=5) for z in (.25, .5, .75)],
      'support_sweep': [dict(pivot=2, sweep_buffer=b) for b in (0, .1, .25)],
      'previous_day': [dict(zone=z) for z in (.25, .5, .75)],
      'previous_week': [dict(zone=z) for z in (.25, .5, .75)],
      'previous_month': [dict(zone=z) for z in (.25, .5, .75)],
      'floor_pivot': [dict(floor_level=x, zone=.5) for x in ('s1', 's2', 'pivot')],
      'fib_pullback': [dict(ratio=x, pivot=2, zone=.5) for x in (.382, .4, .5, .6, .618)],
      'round_bounce': [dict(zone=z) for z in (.25, .5, .75)],
      'anchored_vwap': [dict(pivot=p) for p in (1, 2, 3)],
      'htf_confluence': [dict(pivot=2, zone=z) for z in (.25, .5, .75)],
    }
    for family, grid in structural.items(): out.append((family, grid, family.replace('_', ' ')))
    for family in ('trend_macd_support', 'support_hist', 'reclaim_zero', 'breakout_momentum',
                   'divergence_support', 'ribbon_pullback', 'sweep_reversal'):
        grid = [dict(fast=a, slow=b, signal=s) for a, b, s in (OSCILLATORS[0], OSCILLATORS[2], OSCILLATORS[4])]
        if family in ('trend_macd_support', 'support_hist', 'divergence_support', 'sweep_reversal'):
            grid = [{**p, 'pivot': 2, 'zone': .5} for p in grid]
        if family == 'breakout_momentum':
            grid = [{**p, 'lookback': 20} for p in grid]
        if family == 'ribbon_pullback':
            grid = [dict(fast=a, middle=b, slow=c, zone=.5) for a, b, c in ((5, 13, 34), (9, 20, 50), (20, 50, 100))]
        out.append(('hybrid_'+family, grid, family.replace('_', ' ')))
    return out


def _execution_changes(family):
    changes = [('stop_atr', 1.5), ('stop_atr', 3.), ('reward', 1.5), ('reward', 3.),
               ('max_hold_sessions', 5), ('max_hold_sessions', 20), ('exit', 'time'),
               ('exit', 'atr_trail'), ('exit', 'ema'), ('exit', 'macd'), ('exit', 'trend'), ('stop_mode', 'swing')]
    # S&R and hybrid families also contrast their actual entry reference level
    # with the generic released swing-pivot stop; no unsupported NaN levels.
    if not family.startswith(('macd_', 'ppo_', 'ema_', 'kama_')):
        changes.append(('stop_mode', 'level'))
    return changes


def catalog():
    """Coarse controls, single-factor filters, and single-factor execution changes.

    Stop 1.5/2/3 ATR, reward 1.5/2/3 R, and hold 5/10/20 sessions describe
    distinct risk/time scales. Only one axis changes at a time; this prevents
    multiplying every entry grid by an uninterpretable risk/exit Cartesian grid.
    """
    result = []
    for family, grid, description in _family_grids():
        for params in grid: result.append(_config(family, params, description))
        center = grid[len(grid)//2]
        for filt in FILTERS:
            result.append(_config(family, center, description+'; '+filt+' filter', 'filter_'+filt, filter=filt))
        for key, value in _execution_changes(family):
            result.append(_config(family, center, description+'; '+key+' '+str(value), key+'_'+str(value), **{key: value}))
    return result


def catalog_manifest():
    """Exact pre-outcome grid and neighborhood specification for persistence."""
    configs = catalog()
    return dict(
        protocol='daily_swing_discovery_v1', configurations=len(configs),
        families=len(_family_grids()),
        counts=dict(entry_controls=sum(c['variant'] == 'control' for c in configs),
                    filter_ablations=sum(c['variant'].startswith('filter_') for c in configs),
                    execution_ablations=sum(c['variant'] != 'control' and not c['variant'].startswith('filter_') for c in configs)),
        construction='All entry grids unfiltered; one central entry per family receives one filter or execution change at a time; no Cartesian product.',
        common_execution=EXECUTION.copy(),
        central_entry='entry_grid[len(entry_grid)//2]',
        filter_definitions=dict(none='unfiltered control', volume='completed-day volume >= 1.25 * mean of prior20 volumes',
            adx='Wilder ADX14 >=20', rsi='40 <= Wilder RSI14 <=70', volatility='.01 <= ATR14/close <=.06',
            market='completed NIFTY close > EMA200 and EMA50 > EMA200',
            rs='stock60-session return > NIFTY60-session return', breadth='>=50% of finite panel names close above EMA50',
            sector='mean20-session return of other finite same-sector names >0'),
        indicator_convention='SMA-seeded EMA and Wilder smoothing; missing daily observations reset smoother warmup; KAMA ER fast2 slow30 squared.',
        weekly_availability='Calendar Monday-Sunday bars released only in following observed week; first partial historical week withheld.',
        divergence='Oscillator comparisons at the two confirmed price-pivot indices; entry only on the second pivot release candle.',
        parameter_neighborhood=dict(scope='development_only', shape='one-coordinate changes only',
            periods='integer +/-1 for <=20, else +/-round(10%); floor2; fast<slow and fast<middle<slow',
            pivot_touches_retest='integer +/-1 bounded1..5', ratio_strength='+/-.025; ratio bounded.25..75; strength floor0',
            other_thresholds='+/-.1 with floor0', stop_atr='+/-.25 bounded1..4', reward='+/-.25 bounded1..4',
            max_hold_sessions='+/-2 bounded3..25'),
        family_grids=[dict(family=family, description=description, entry_grid=grid,
                           filters=list(FILTERS), execution_changes=[{k: v} for k, v in _execution_changes(family)])
                      for family, grid, description in _family_grids()])


def neighbors(config):
    """Predeclared one-coordinate development-only neighborhoods, never outcomes.

    Selection must use training/development metrics. Validation or final-stage
    tagged configurations are rejected, protecting against accidental reuse by
    the stage runner. Nearby integers and fixed threshold steps are frozen here.
    """
    allowed = ('development', 'training', 'train', 'development_only')
    if any(config.get(key, 'development') not in allowed for key in ('selection_scope', 'stage')):
        raise ValueError('Parameter neighborhoods are restricted to development selection')
    params = {k: config.get(k, config.get('params', {}).get(k)) for k in ENTRY_KEYS}
    params = {k: v for k, v in params.items() if v is not None}
    execution = {k: config.get(k, EXECUTION.get(k)) for k in EXECUTION}
    execution['filter'] = config.get('filter', 'none')
    candidates = []
    for key, value in params.items():
        if key == 'floor_level': continue
        if key in ('fast', 'slow', 'signal', 'middle', 'weekly_fast', 'weekly_slow', 'weekly_signal', 'lookback'):
            delta = 1 if value <= 20 else max(1, int(round(value*.1)))
            nearby = (max(2, int(value-delta)), int(value+delta))
        elif key in ('pivot', 'touches', 'retest_window'):
            nearby = (max(1, int(value)-1), min(5, int(value)+1))
        else:
            step = .025 if key in ('ratio', 'strength') else .1
            nearby = (round(max(0., value-step), 6), round(value+step, 6))
        for new in nearby:
            if new == value: continue
            p = {**params, key: new}
            if p.get('fast', 0) >= p.get('slow', np.inf): continue
            if p.get('weekly_fast', 0) >= p.get('weekly_slow', np.inf): continue
            if 'middle' in p and not p['fast'] < p['middle'] < p['slow']: continue
            if key == 'ratio' and not .25 <= new <= .75: continue
            c = _config(config['family'], p, config['description']+'; development neighbor '+key,
                        'development_neighbor', **execution)
            c.update(parent_id=config['id'], selection_scope='development_only', neighbor_axis=key)
            candidates.append(c)
    # Only execution axes already under study are perturbed around that setting.
    for key, step, lower, upper in (('stop_atr', .25, 1., 4.), ('reward', .25, 1., 4.), ('max_hold_sessions', 2, 3, 25)):
        for value in (execution[key]-step, execution[key]+step):
            if lower <= value <= upper:
                changed = {**execution, key: value}
                c = _config(config['family'], params, config['description']+'; development neighbor '+key,
                            'development_neighbor', **changed)
                c.update(parent_id=config['id'], selection_scope='development_only', neighbor_axis=key)
                candidates.append(c)
    return list({c['id']: c for c in candidates}.values())
