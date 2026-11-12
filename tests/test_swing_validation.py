"""Known-outcome tests for marked daily returns and clustered inference."""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from research.swing.validation import block_indices, daily_returns, search_max_t, trade_uncertainty

TZ = "Asia/Kolkata"


class DailyReturnTests(unittest.TestCase):
    def test_last_mark_per_local_session_and_initial_capital(self):
        idx = pd.DatetimeIndex(["2026-01-05 10:00", "2026-01-05 15:30", "2026-01-06 15:30"], tz=TZ)
        equity = pd.DataFrame({"equity": [105., 110., 121.]}, index=idx)
        out = daily_returns(equity, initial_capital=100.)
        np.testing.assert_allclose(out.to_numpy(), [.1, .1])
        self.assertEqual(len(out), 2)

    def test_timestamp_column_and_legacy_nav(self):
        equity = pd.DataFrame({"nav": [100., 90.], "ts": ["2026-01-05T15:30:00+05:30", "2026-01-06T15:30:00+05:30"]})
        np.testing.assert_allclose(daily_returns(equity, 100.).to_numpy(), [0., -.1])

    def test_empty_and_flat(self):
        self.assertTrue(daily_returns(pd.DataFrame()).empty)
        idx = pd.date_range("2026-01-05", periods=12, freq="B", tz=TZ)
        out = daily_returns(pd.DataFrame({"equity": 1_000_000.}, index=idx))
        self.assertTrue((out == 0).all())


class BlockBootstrapTests(unittest.TestCase):
    def test_calendar_blocks_are_contiguous_circular_and_reproducible(self):
        ix = block_indices(25, draws=20, block=10, seed=7)
        self.assertEqual(ix.shape, (20, 25))
        self.assertTrue(((ix >= 0) & (ix < 25)).all())
        for begin, end in [(0, 10), (10, 20), (20, 25)]:
            np.testing.assert_array_equal(np.diff(ix[:, begin:end], axis=1) % 25,
                                          np.ones((20, end - begin - 1), dtype=int))
        np.testing.assert_array_equal(ix, block_indices(25, draws=20, block=10, seed=7))

    def test_empty_trade_sample_is_explicitly_uninformative(self):
        result = trade_uncertainty(pd.DataFrame(), [], draws=100)
        self.assertEqual(result["r_ci95"], [None, None])
        self.assertIsNone(result["positive_probability"])

    def test_constant_zero_outcomes_have_zero_interval(self):
        sessions = pd.date_range("2026-01-01", periods=40, freq="B", tz=TZ)
        trades = pd.DataFrame({"exit_time": sessions[::4] + pd.Timedelta(hours=15), "net_r": 0.})
        result = trade_uncertainty(trades, sessions, draws=300)
        self.assertEqual(result["r_ci95"], [0., 0.])
        self.assertEqual(result["positive_probability"], 0.)

    def test_constant_winners_retain_zero_trade_sessions(self):
        sessions = pd.date_range("2026-01-01", periods=50, freq="B", tz=TZ)
        trades = pd.DataFrame({"exit_time": sessions[::5] + pd.Timedelta(hours=15), "net_r": 1.5})
        result = trade_uncertainty(trades, sessions, draws=300)
        self.assertEqual(result["r_ci95"], [1.5, 1.5])
        self.assertEqual(result["positive_probability"], 1.)

    def test_special_session_exit_is_included_even_if_calendar_omits_it(self):
        # Sunday special-session exit is the only trade. Omitting it previously
        # silently discarded its loss and caused an empty-quantile exception.
        sessions = pd.date_range("2026-11-02", periods=5, freq="B", tz=TZ)
        trades = pd.DataFrame({"exit_time": ["2026-11-08T15:30:00+05:30"], "net_r": [-2.]})
        result = trade_uncertainty(trades, sessions, draws=100)
        self.assertEqual(result["r_ci95"], [-2., -2.])
        self.assertEqual(result["positive_probability"], 0.)

    def test_exit_utc_timestamp_uses_local_session_date(self):
        trades = pd.DataFrame({"exit_time": ["2026-01-05T20:00:00Z"], "net_r": [2.]})
        sessions = pd.date_range("2026-01-06", periods=1, tz=TZ)
        result = trade_uncertainty(trades, sessions, draws=100)
        self.assertEqual(result["r_ci95"], [2., 2.])


class SearchControlTests(unittest.TestCase):
    def test_no_hypotheses_and_zero_returns(self):
        self.assertEqual(search_max_t({}), {})
        idx = pd.date_range("2026-01-01", periods=40, freq="B")
        out = search_max_t({"zero": pd.Series(0., index=idx)}, draws=200)
        self.assertEqual(out["zero"]["validation_t"], 0.)
        self.assertEqual(out["zero"]["max_t_adjusted_p"], 1.)

    def test_identical_dependent_hypotheses_share_bootstrap_and_p_value(self):
        idx = pd.date_range("2026-01-01", periods=80, freq="B")
        x = pd.Series(np.random.default_rng(8).normal(.0003, .01, len(idx)), index=idx)
        single = search_max_t({"first": x}, draws=300)
        duplicate = search_max_t({"first": x, "identical": x.copy()}, draws=300)
        self.assertEqual(duplicate["first"]["max_t_adjusted_p"], single["first"]["max_t_adjusted_p"])
        self.assertEqual(duplicate["identical"]["max_t_adjusted_p"], single["first"]["max_t_adjusted_p"])
        self.assertEqual(duplicate["first"]["hypotheses"], 2)

    def test_adding_other_hypotheses_cannot_reduce_familywise_p(self):
        idx = pd.date_range("2026-01-01", periods=90, freq="B")
        rng = np.random.default_rng(32)
        x, y = [pd.Series(rng.normal(.0001, .01, len(idx)), index=idx) for _ in range(2)]
        one = search_max_t({"x": x}, draws=300)
        two = search_max_t({"x": x, "y": y}, draws=300)
        self.assertGreaterEqual(two["x"]["max_t_adjusted_p"], one["x"]["max_t_adjusted_p"])
        for row in two.values():
            self.assertTrue(np.isfinite(row["validation_t"]))
            self.assertGreaterEqual(row["max_t_adjusted_p"], 1 / 301)
            self.assertLessEqual(row["max_t_adjusted_p"], 1.)


if __name__ == "__main__":
    unittest.main()
