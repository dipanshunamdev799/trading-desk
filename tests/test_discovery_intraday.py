"""Synthetic matched-entry path checks, independent of finalist outcomes."""
import numpy as np
import pandas as pd
import unittest

from scripts.verify_discovery_intraday import replay_trade, TZ


def fixture():
    dates = pd.date_range('2026-01-05', periods=2, tz=TZ)
    daily = pd.DataFrame({'open': [100., 100.], 'high': [111., 111.],
                          'low': [94., 94.], 'close': [100., 100.]}, index=dates)
    ix = pd.DatetimeIndex([dates[0] + pd.Timedelta(hours=9, minutes=15),
                           dates[0] + pd.Timedelta(hours=9, minutes=20)])
    bars = pd.DataFrame({'open': [100., 106.], 'high': [111., 107.],
                         'low': [99., 94.], 'close': [106., 100.]}, index=ix)
    sessions = {dates[0]: bars, dates[1]: bars.set_axis(ix + pd.Timedelta(days=1))}
    row = {'symbol': 'TEST', 'signal_day': dates[0] - pd.Timedelta(days=1),
           'entry_day': dates[0], 'exit_day': dates[0], 'entry_fill': 100.05,
           'entry_quantity': 10, 'entry_adjusted': 100.05, 'quantity': 10,
           'stop': 95., 'target': 110., 'initial_cash_risk': 100.,
           'net_pnl': -100., 'net_r': -1., 'reason': 'stop'}
    return row, sessions, daily, pd.Series(1., index=dates), pd.Series(0., index=dates)


def test_intraday_known_target_first_resolves_daily_both_hit():
    row, sessions, daily, split, div = fixture()
    result = replay_trade(row, {'exit': 'fixed'}, sessions, daily, split, div)
    assert result['status'] == 'matched'
    assert result['daily_both_hit']
    assert result['five_minute_reason'] == 'five_minute_target'
    assert result['five_minute_both_hit_bars'] == 0
    assert np.isclose(result['five_minute_exit_fill'], 110 * .9995)


def test_within_five_minute_both_hit_keeps_stop_first():
    row, sessions, daily, split, div = fixture()
    sessions[day := daily.index[0]].iloc[0, sessions[day].columns.get_loc('low')] = 94
    result = replay_trade(row, {'exit': 'fixed'}, sessions, daily, split, div)
    assert result['five_minute_reason'] == 'five_minute_stop'
    assert result['five_minute_both_hit_bars'] == 1


def test_carried_split_is_rejected_without_guessing_units():
    row, sessions, daily, split, div = fixture()
    row.update(exit_day=daily.index[1], quantity=20, entry_adjusted=50.025)
    split.iloc[1] = 2
    assert replay_trade(row, {'exit': 'fixed'}, sessions, daily, split, div)['rejection'] == 'carried_split_or_share_basis_change'


def test_time_only_ignores_target_then_credits_carried_dividend():
    row, sessions, daily, split, div = fixture()
    row.update(exit_day=daily.index[1], reason='signal_or_time', stop=90.)
    div.iloc[1] = 1.5
    result = replay_trade(row, {'exit': 'time'}, sessions, daily, split, div)
    assert result['five_minute_reason'] == 'scheduled_daily_time_exit'
    assert result['five_minute_dividends'] == 15.


def test_missing_path_and_unsupported_trail_are_explicit():
    row, sessions, daily, split, div = fixture()
    assert 'requires_daily_stop_reconstruction' in replay_trade(row, {'exit': 'atr_trail'}, sessions, daily, split, div)['rejection']
    sessions.clear()
    assert replay_trade(row, {'exit': 'fixed'}, sessions, daily, split, div)['rejection'] == 'missing_complete_five_minute_session'


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(function) for name, function in globals().items() if name.startswith('test_'))


if __name__ == '__main__':
    unittest.main()
