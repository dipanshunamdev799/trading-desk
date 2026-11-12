"""Synthetic causality and Indian-session boundary checks for swing research."""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from research.swing.signals import TZ, aggregate, catalog, clear_cache, features, make_signals


def synthetic(sessions: int = 1) -> pd.DataFrame:
    pieces = []
    for day in pd.bdate_range("2024-01-01", periods=sessions, tz=TZ):
        pieces.extend(pd.date_range(day + pd.Timedelta(hours=9, minutes=15), periods=75, freq="5min"))
    idx = pd.DatetimeIndex(pieces)
    seq = np.arange(len(idx))
    close = 100 + .003 * seq + 3 * np.sin(seq / 39) + .3 * np.sin(seq / 4)
    opening = np.r_[close[0], close[:-1]]
    return pd.DataFrame({"open": opening, "high": np.maximum(opening, close) + .15,
                         "low": np.minimum(opening, close) - .15, "close": close,
                         "volume": 1000}, index=idx)


class SessionAggregationTests(unittest.TestCase):
    def setUp(self):
        clear_cache()

    def test_open_anchor_and_completed_partial_candles(self):
        bars = synthetic()
        out = aggregate(bars, 120)
        self.assertEqual([x.strftime("%H:%M") for x in out.index], ["11:15", "13:15", "15:15", "15:30"])
        self.assertEqual(out.duration.tolist(), [120, 120, 120, 15])
        out4 = aggregate(bars, 240)
        self.assertEqual([x.strftime("%H:%M") for x in out4.index], ["13:15", "15:30"])
        self.assertEqual(out4.duration.tolist(), [240, 135])
        self.assertEqual(aggregate(bars, 240, "full").duration.tolist(), [240])

    def test_unfinished_last_candle_is_never_released(self):
        bars = synthetic()
        before_1115 = bars.iloc[:23]
        self.assertTrue(aggregate(before_1115, 120).empty)
        at_1115 = bars.iloc[:24]
        out = aggregate(at_1115, 120)
        self.assertEqual(len(out), 1)
        self.assertEqual(out.index[0], bars.index[0] + pd.Timedelta(hours=2))
        self.assertTrue(aggregate(bars.iloc[:-1], 375).empty)

    def test_missing_internal_bar_invalidates_bucket(self):
        bars = synthetic().drop(synthetic().index[10])
        out = aggregate(bars, 120)
        self.assertEqual([x.strftime("%H:%M") for x in out.index], ["13:15", "15:15", "15:30"])

    def test_close_anchor_has_completed_first_partial(self):
        out = aggregate(synthetic(), 240, "right_anchor")
        self.assertEqual([x.strftime("%H:%M") for x in out.index], ["11:30", "15:30"])
        self.assertEqual(out.duration.tolist(), [135, 240])

    def test_session_boundary_never_combines_overnight_prices(self):
        bars = synthetic(2)
        out = aggregate(bars, 240)
        self.assertEqual(len(out), 4)
        self.assertTrue((out.bar_start.dt.normalize() == out.index.normalize()).all())


class CausalFeatureTests(unittest.TestCase):
    def setUp(self):
        clear_cache()

    def test_pivot_is_released_only_after_two_right_bars(self):
        idx = pd.date_range("2024-01-01 10:00", periods=8, freq="h", tz=TZ)
        h = np.array([1, 2, 5, 3, 2, 1, 4, 2], dtype=float)
        d = pd.DataFrame({"open": h - .5, "high": h, "low": h - 1, "close": h - .5, "volume": 1}, index=idx)
        out = features(d, ema=2, pivot=2, slope=1)
        self.assertTrue(out.pivot_high.iloc[:4].isna().all())
        self.assertEqual(out.pivot_high.iloc[4], 5)
        self.assertEqual(out.pivot_high.iloc[-1], 5)

    def test_features_do_not_repaint_when_future_rows_arrive(self):
        bars = synthetic(32)
        whole = aggregate(bars, 60)
        full = features(whole, ema=20)
        for size in [53, 107, 190]:
            cut = whole.iloc[:size].copy()
            prefix = features(cut, ema=20)
            pd.testing.assert_frame_equal(full.iloc[:size], prefix)

    def test_signal_prefix_invariance_and_only_closed_htf(self):
        bars = synthetic(90)
        cfg = {"family": "A", "ema": 20}
        full = make_signals(bars, cfg)
        for size in [2823, 5061, len(bars) - 17]:
            prefix = make_signals(bars.iloc[:size].copy(), cfg)
            pd.testing.assert_frame_equal(full.loc[prefix.index], prefix)
            observed = prefix.htf_available_at.dropna()
            self.assertTrue((observed <= observed.index).all())

    def test_parameter_catalog_has_unique_ids_and_requested_timeframes(self):
        rows = catalog()
        self.assertEqual(len(rows), len({x["id"] for x in rows}))
        combinations = {(x["htf"], x["ltf"]) for x in rows}
        self.assertTrue({(240, 120), (240, 60), (375, 240), (375, 120), (120, 30)} <= combinations)
        self.assertTrue({1, 1.5, 2, 2.5, 3, 4} <= {x["reward"] for x in rows})

    def test_prior_day_barrier_uses_afternoon_even_when_partial_indicators_discarded(self):
        bars = synthetic(90)
        bars[["open", "close"]] = 100.
        bars["high"], bars["low"] = 101., 99.
        bars.iloc[-75:, bars.columns.get_indexer(["open", "close"])] = 150.
        bars.iloc[-75:, bars.columns.get_loc("high")] = 151.
        bars.iloc[-75:, bars.columns.get_loc("low")] = 149.
        # A last-5m high on the preceding day lies outside the retained morning
        # 4H candle under full-only policy, but remains a real known barrier.
        bars.iloc[-76, bars.columns.get_loc("high")] = 200.
        out = make_signals(bars, {"family": "A", "ema": 20, "policy": "full"})
        final_day = out.index.normalize() == bars.index[-1].normalize()
        self.assertTrue((out.loc[final_day, "target_long"] == 200.).all())


if __name__ == "__main__":
    unittest.main()
