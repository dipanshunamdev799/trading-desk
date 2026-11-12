"""Dependence-aware uncertainty and search-wide controls, with reproducible seeds."""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261110


def block_indices(n: int, draws: int = 3000, block: int = 10, seed: int = SEED):
    if not n:
        return np.empty((draws, 0), dtype=int)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n, (draws, int(np.ceil(n / block)), 1))
    return ((starts + np.arange(block)) % n).reshape(draws, -1)[:, :n]


def trade_uncertainty(trades: pd.DataFrame, sessions, draws: int = 3000):
    """Resample 10-session blocks of trade exits, retaining zero-trade sessions.

    Confidence intervals are conditional on frozen strategy choice. They do not
    undo earlier use of the same historical market period.
    """
    def local_day(value):
        stamp = pd.Timestamp(value)
        if stamp.tzinfo is not None:
            stamp = stamp.tz_convert('Asia/Kolkata')
        return stamp.strftime('%Y-%m-%d')
    days = pd.Index([local_day(x) for x in sessions]).unique().sort_values()
    if trades.empty:
        return {'r_ci95': [None, None], 'positive_probability': None,
                'block_sessions': 10, 'draws': draws}
    value_col = 'net_r' if 'net_r' in trades else 'r_multiple'
    exit_col = 'exit_time' if 'exit_time' in trades else 'exit_ts'
    t = trades.copy()
    t['day'] = t[exit_col].map(local_day)
    # Special-session protective exits remain real outcomes even if callers
    # supplied only the regular indicator calendar. Never silently discard them.
    days = days.union(pd.Index(t['day'].unique())).sort_values()
    n = len(days)
    g = t.groupby('day')[value_col].agg(['sum', 'count']).reindex(days, fill_value=0)
    ix = block_indices(n, draws=draws)
    counts = g['count'].to_numpy()[ix].sum(axis=1)
    sums = g['sum'].to_numpy()[ix].sum(axis=1)
    samples = sums[counts > 0] / counts[counts > 0]
    return {'r_ci95': np.quantile(samples, [.025, .975]).tolist(),
            'positive_probability': float((samples > 0).mean()),
            'block_sessions': 10, 'draws': draws}


def search_max_t(daily_returns: dict[str, pd.Series], draws: int = 2000):
    """Single-step max-|t| style one-sided familywise bootstrap control.

    All strategies share the same resampled 10-session calendar blocks, preserving
    cross-strategy dependence. The null subtracts each sample mean. This is an
    approximate search-wide diagnostic, not proof of a deployable edge.
    """
    if not daily_returns:
        return {}
    panel = pd.DataFrame(daily_returns).fillna(0)
    x = panel.to_numpy(float)
    n = len(x)
    scale = x.std(axis=0, ddof=1) / np.sqrt(max(n, 1))
    valid = scale > 1e-12
    observed = np.divide(x.mean(axis=0), scale, out=np.zeros(x.shape[1]), where=valid)
    ix = block_indices(n, draws=draws)
    centered = x - x.mean(axis=0)
    maxima = np.zeros(draws)
    # Bounded memory even when the hypothesis grid grows.
    for lo in range(0, draws, 100):
        boot = centered[ix[lo:lo+100]].mean(axis=1)
        t = np.divide(boot, scale, out=np.zeros_like(boot), where=valid)
        maxima[lo:lo+len(t)] = np.max(t, axis=1)
    return {str(k): {'validation_t': float(observed[j]),
                    'max_t_adjusted_p': float((1+(maxima >= observed[j]).sum())/(draws+1)),
                    'hypotheses': len(panel.columns), 'block_sessions': 10}
            for j, k in enumerate(panel.columns)}


def daily_returns(equity: pd.DataFrame, initial_capital=1_000_000):
    if equity.empty:
        return pd.Series(dtype=float)
    col = 'equity' if 'equity' in equity else 'nav'
    series = equity[col].copy()
    if not isinstance(series.index, pd.DatetimeIndex):
        time_col = 'timestamp' if 'timestamp' in equity else 'ts'
        series.index = pd.to_datetime(equity[time_col])
    daily = series.groupby(series.index.normalize()).last()
    prev = daily.shift(1).fillna(initial_capital)
    return daily/prev-1
