import unittest

import numpy as np
import pandas as pd

from research.swing_discovery.structure import build_structure


def make_panel(low, high=None, close=None, dates=None, unit=None):
    low = np.asarray(low, float)
    if low.ndim == 1:
        low = low[None, :]
    high = low + 4 if high is None else np.asarray(high, float).reshape(low.shape)
    close = (high + low) / 2 if close is None else np.asarray(close, float).reshape(low.shape)
    unit = np.ones_like(low) if unit is None else np.asarray(unit, float).reshape(low.shape)
    neutral = dict(open=close.copy(), high=high, low=low, close=close,
                   volume=np.full(low.shape, 100.))
    actual = {key: value * unit if key != 'volume' else value / unit
              for key, value in neutral.items()}
    return dict(neutral=neutral, actual=actual, unit_factor=unit,
                dates=pd.date_range('2025-01-06', periods=low.shape[1], freq='B')
                if dates is None else pd.DatetimeIndex(dates))


def prefix(panel, n):
    return dict(neutral={key: value[:, :n] for key, value in panel['neutral'].items()},
                actual={key: value[:, :n] for key, value in panel['actual'].items()},
                unit_factor=panel['unit_factor'][:, :n], dates=panel['dates'][:n])


class DiscoveryStructureTests(unittest.TestCase):
    def test_strict_pivot_released_after_right_confirmation(self):
        panel = make_panel([10, 9, 8, 9, 10, 9, 7, 9, 10])
        result = build_structure(panel, pivot=2, atr=np.ones((1, 9)))
        self.assertTrue(np.isnan(result['pivot_low'][0, :4]).all())
        np.testing.assert_equal(result['pivot_low'][0, 4:8], [8, 8, 8, 8])
        self.assertEqual(result['pivot_low'][0, 8], 7)
        self.assertEqual(result['prev_pivot_low'][0, 8], 8)
        self.assertEqual(result['pivot_low_idx'][0, 8], 6)
        self.assertEqual(result['prev_pivot_low_idx'][0, 8], 2)
        np.testing.assert_equal(np.flatnonzero(result['pivot_low_event'][0]), [4, 8])
        tied = build_structure(make_panel([10, 9, 8, 8, 10, 11]), pivot=1)
        self.assertFalse(tied['pivot_low_event'].any())

    def test_every_output_is_prefix_invariant(self):
        rng = np.random.default_rng(705)
        close = 100 + np.cumsum(rng.normal(0, 1, (3, 85)), axis=1)
        panel = make_panel(close - rng.uniform(.1, 2, close.shape),
                           close + rng.uniform(.1, 2, close.shape), close)
        atr = np.full(close.shape, 2.)
        full = build_structure(panel, pivot=2, lookback=5, atr=atr)
        for count in [1, 4, 5, 12, 24, 43, 64]:
            short = build_structure(prefix(panel, count), pivot=2, lookback=5, atr=atr[:, :count])
            self.assertEqual(full.keys(), short.keys())
            for key in full:
                np.testing.assert_allclose(short[key], full[key][:, :count], equal_nan=True,
                                           err_msg=f'{key} at prefix {count}')

    def test_prior_channel_excludes_current_extreme(self):
        result = build_structure(make_panel([8, 9, 10, 11, 1],
                                            [12, 13, 14, 15, 100]), lookback=3)
        self.assertTrue(np.isnan(result['donchian_high'][0, :3]).all())
        self.assertEqual(result['donchian_high'][0, 4], 15)
        self.assertEqual(result['donchian_low'][0, 4], 9)

    def test_previous_week_and_month_use_completed_period(self):
        dates = pd.bdate_range('2025-01-27', '2025-02-11')
        low = np.arange(len(dates)) + 10.
        result = build_structure(make_panel(low, dates=dates), pivot=1)
        # Jan27-31's highs 14..18 are released only on MondayFeb3.
        monday = dates.get_loc('2025-02-03')
        self.assertTrue(np.isnan(result['prev_week_high'][0, :monday]).all())
        np.testing.assert_equal(result['prev_week_high'][0, monday:monday+5], [18]*5)
        self.assertEqual(result['prev_week_low'][0, monday], 10)
        # January is partial in this input and cannot be called complete.
        self.assertTrue(np.isnan(result['prev_month_high']).all())
        dates = pd.bdate_range('2025-01-01', '2025-02-05')
        low = np.arange(len(dates)) + 10.
        result = build_structure(make_panel(low, dates=dates), pivot=1)
        feb = dates.get_loc('2025-02-03')
        self.assertEqual(result['prev_month_high'][0, feb], low[feb-1] + 4)
        self.assertEqual(result['prev_month_low'][0, feb], low[0])
        self.assertTrue(np.isnan(result['prev_month_high'][0, :feb]).all())

    def test_round_levels_are_defined_in_actual_rupees(self):
        panel = make_panel([60, 60, 60], close=[61.5, 61.5, 61.5], unit=[2, 2, 1])
        result = build_structure(panel, pivot=1)
        # First actual close123 uses50-rupee rounds before conversion by2.
        self.assertEqual(result['round_support'][0, 0], 50)
        self.assertEqual(result['round_resistance'][0, 0], 75)
        self.assertEqual(result['round_step'][0, 0], 25)
        self.assertEqual(result['round_10_support'][0, 0], 60)
        # Actual close61.5 uses10-rupee rounds, even though neutral price agrees.
        self.assertEqual(result['round_support'][0, 2], 60)
        self.assertEqual(result['round_resistance'][0, 2], 70)

    def test_breakout_level_frozen_and_retest_age_bounded(self):
        high = [10, 10, 10, 13, 14, 15, 16, 17, 18, 17, 16]
        close = [9, 9, 9, 12, 13, 14, 15, 16, 17, 16, 15]
        result = build_structure(make_panel(np.asarray(close)-1, high, close), lookback=3)
        self.assertTrue(result['breakout_event'][0, 3])
        np.testing.assert_equal(result['breakout_level'][0, 3:9], [10]*6)
        np.testing.assert_equal(result['breakout_age'][0, 3:9], np.arange(6))
        self.assertTrue(np.isnan(result['breakout_level'][0, 9]))
        self.assertEqual(result['breakout_age'][0, 9], -1)

    def test_cluster_and_anchored_vwap_wait_for_confirmation(self):
        panel = make_panel([12, 10, 12, 10.1, 12, 10.2, 12, 12],
                           close=[13, 12, 13, 12, 13, 12, 13, 13])
        result = build_structure(panel, pivot=1, zone=.5, atr=np.ones((1, 8)))
        self.assertTrue(np.isnan(result['cluster_support'][0, :4]).all())
        self.assertEqual(result['cluster_support_touches'][0, 4], 2)
        self.assertEqual(result['cluster_support_touches'][0, 6], 3)
        self.assertAlmostEqual(result['cluster_support'][0, 6], 10.1, places=5)
        self.assertTrue(np.isnan(result['avwap_low'][0, :2]).all())
        typical = sum(panel['neutral'][key] for key in ['high', 'low', 'close']) / 3
        self.assertAlmostEqual(result['avwap_low'][0, 2], typical[0, 1:3].mean(), places=5)

    def test_floor_pivots_use_prior_hlc(self):
        result = build_structure(make_panel([9, 50], [15, 70], [12, 60]), pivot=1)
        self.assertTrue(np.isnan(result['floor_pivot'][0, 0]))
        self.assertEqual(result['floor_pivot'][0, 1], 12)
        self.assertEqual(result['floor_s1'][0, 1], 9)
        self.assertEqual(result['floor_r1'][0, 1], 15)

    def test_fibonacci_anchors_are_ordered_and_frozen_until_new_high(self):
        panel = make_panel([10, 9, 8, 9, 10, 11, 9, 10, 11, 12, 13, 12],
                           [15, 14, 13, 16, 20, 17, 16, 15, 17, 21, 18, 16])
        result = build_structure(panel, pivot=1, atr=np.ones((1, 12)))
        self.assertTrue(np.isnan(result['fib_high'][0, :5]).all())
        self.assertEqual(result['fib_low'][0, 5], 8)
        self.assertEqual(result['fib_high'][0, 5], 20)
        # A subsequently confirmed low is a pullback, not a rewrite of the leg.
        self.assertEqual(result['pivot_low'][0, 7], 9)
        self.assertEqual(result['fib_low'][0, 7], 8)
        self.assertEqual(result['fib_500'][0, 7], 14)
        # The next released high can establish a fresh ordered bullish leg.
        self.assertEqual(result['fib_low'][0, 10], 9)
        self.assertEqual(result['fib_high'][0, 10], 21)
        self.assertTrue(result['higher_high_higher_low'][0, 10])


if __name__ == '__main__':
    unittest.main()
