"""Synthetic execution tests: outcomes have independently known solutions."""
import unittest

import pandas as pd

from research.swing.engine import simulate, transaction_cost


def candles(rows, dates=None):
    index = pd.DatetimeIndex(dates) if dates is not None else pd.date_range("2025-01-06 09:15", periods=len(rows), freq="5min", tz="Asia/Kolkata")
    if index.tz is None:
        index = index.tz_localize("Asia/Kolkata")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=index)


def signals(bars, stops=95, side=1, at=None, **extra):
    return pd.DataFrame({"side": [side], "stop": [stops], "atr": [2.0], **{k: [v] for k, v in extra.items()}},
                        index=pd.DatetimeIndex([bars.index[0] if at is None else at]))


class SwingEngineTest(unittest.TestCase):
    def run_sim(self, bars, signal, config=None, **kwargs):
        return simulate(bars, signal, {"initial_capital": 10_000, "risk_fraction": .01,
                                      "reward": 2, **(config or {})},
                        "2025-01-01", "2025-02-01", cost_multiplier=0,
                        slippage_bps=0, **kwargs)

    def test_signal_not_available_until_next_open(self):
        bars = candles([[100, 130, 90, 110], [110, 111, 109, 110]])
        result = self.run_sim(bars, signals(bars, stops=105, at=bars.index[1]))
        trade = result["trades"].iloc[0]
        self.assertEqual(trade.entry, 110)
        self.assertEqual(trade.entry_time, bars.index[1])
        self.assertEqual(trade.reason, "segment_end")

    def test_both_barriers_stop_first(self):
        bars = candles([[100, 115, 94, 110]])
        trade = self.run_sim(bars, signals(bars))["trades"].iloc[0]
        self.assertEqual(trade.exit, 95)
        self.assertAlmostEqual(trade.net_r, -1)

    def test_overnight_gap_fills_worse_than_stop(self):
        bars = candles([[100, 101, 99, 100], [90, 92, 89, 91]],
                       ["2025-01-03 15:25", "2025-01-06 09:15"])
        trade = self.run_sim(bars, signals(bars))["trades"].iloc[0]
        self.assertEqual(trade.exit, 90)
        self.assertEqual(trade.reason, "gap_stop")
        self.assertAlmostEqual(trade.net_r, -2)

    def test_target_gap_gets_no_beneficial_open(self):
        bars = candles([[100, 101, 99, 100], [120, 122, 119, 121]])
        trade = self.run_sim(bars, signals(bars))["trades"].iloc[0]
        self.assertEqual(trade.exit, 110)
        self.assertAlmostEqual(trade.net_r, 2)

    def test_integer_capital_cap(self):
        bars = candles([[100, 100.01, 99.99, 100]])
        trade = self.run_sim(bars, signals(bars, stops=99.9), {"risk_fraction": .5, "stop_constraints": False})["trades"].iloc[0]
        self.assertEqual(trade.quantity, 100)

    def test_short_symmetry(self):
        bars = candles([[100, 101, 89, 90]])
        trade = self.run_sim(bars, signals(bars, stops=105, side=-1))["trades"].iloc[0]
        self.assertEqual(trade.exit, 90)
        self.assertAlmostEqual(trade.net_r, 2)

    def test_delivery_cannot_short(self):
        bars = candles([[100, 101, 89, 90]])
        result = self.run_sim(bars, signals(bars, stops=105, side=-1), {"cost_model": "equity_delivery"})
        self.assertTrue(result["trades"].empty)

    def test_ending_excludes_future_candle(self):
        bars = candles([[100, 101, 99, 101], [150, 151, 149, 150]],
                       ["2025-01-31 15:25", "2025-02-03 09:15"])
        trade = self.run_sim(bars, signals(bars))["trades"].iloc[0]
        self.assertEqual(trade.exit, 101)
        self.assertEqual(trade.reason, "segment_end")

    def test_partial_known_payoff(self):
        bars = candles([[100, 105.1, 99, 104], [104, 110.1, 103, 110]])
        trade = self.run_sim(bars, signals(bars), {"exit": "partial"})["trades"].iloc[0]
        self.assertEqual(trade.exit_legs, 2)
        self.assertAlmostEqual(trade.net_r, 1.5)

    def test_cash_equity_reconciles(self):
        bars = candles([[100, 101, 99, 100], [100, 111, 99, 110]])
        result = simulate(bars, signals(bars), {"initial_capital": 10_000, "risk_fraction": .01},
                          "2025-01-01", "2025-02-01", slippage_bps=2)
        self.assertAlmostEqual(result["equity"].equity.iloc[-1], 10_000 + result["trades"].net_pnl.sum())
        self.assertGreater(result["trades"].fees.sum(), 0)

    def test_no_pre_segment_signal(self):
        bars = candles([[100, 101, 99, 100]])
        s = signals(bars, at=bars.index[0] - pd.Timedelta(days=10))
        self.assertTrue(self.run_sim(bars, s)["trades"].empty)

    def test_fee_schedule_known_difference(self):
        # Only exchange/IPFT schedule changes: other taxes are identical.
        before = transaction_cost(100, 1000, "buy", "2026-02-28", "equity_delivery")
        after = transaction_cost(100, 1000, "buy", "2026-03-01", "equity_delivery")
        self.assertAlmostEqual(after - before, .0001 * 1.18, places=7)
        etf_buy = transaction_cost(100, 1000, "buy", "2026-03-01", "etf_delivery")
        self.assertAlmostEqual(after - etf_buy, 100)

    def test_target_is_two_cash_risk_after_fees(self):
        bars = candles([[100, 101, 99, 100], [100, 120, 99, 115]])
        result = simulate(bars, signals(bars), {"initial_capital": 100_000, "risk_fraction": .01},
                          "2025-01-01", "2025-02-01", slippage_bps=2)
        trade = result["trades"].iloc[0]
        self.assertEqual(trade.reason, "target")
        self.assertAlmostEqual(trade.net_r, 2, places=9)

    def test_gap_distorted_risk_is_rejected(self):
        bars = candles([[115, 116, 114, 115]])
        self.assertTrue(self.run_sim(bars, signals(bars, stops=95))["trades"].empty)

    def test_holiday_gap_fills_first_tradable_open(self):
        bars = candles([[100, 101, 99, 100], [100, 101, 99, 100]],
                       ["2025-01-03 15:25", "2025-01-09 09:15"])
        result = self.run_sim(bars, signals(bars, at=bars.index[0] + pd.Timedelta(minutes=5)))
        self.assertEqual(result["trades"].iloc[0].entry_time, bars.index[1])

    def test_resting_target_precedes_signal_exit_at_gap_open(self):
        bars = candles([[100, 101, 99, 100], [120, 122, 119, 121]])
        s = pd.concat([signals(bars), signals(bars, side=0, at=bars.index[1], exit_long=True)])
        trade = self.run_sim(bars, s, {"exit": "macd"})["trades"].iloc[0]
        self.assertEqual(trade.exit, 110)
        self.assertEqual(trade.reason, "target")

    def test_future_trail_does_not_change_earlier_bar(self):
        bars = candles([[100, 101, 99, 100], [100, 103, 99, 102]])
        s = pd.concat([signals(bars), signals(bars, side=0, at=bars.index[1], trail_stop_long=101)])
        trade = self.run_sim(bars, s, {"exit": "ema"})["trades"].iloc[0]
        self.assertEqual(trade.exit_time, bars.index[1])
        self.assertEqual(trade.exit, 100)

    def test_fee_inclusive_risk_budget(self):
        bars = candles([[100, 101, 99, 100], [100, 111, 99, 110]])
        result = simulate(bars, signals(bars), {"initial_capital": 10_000, "risk_fraction": .01,
                                               "cost_model": "equity_delivery"},
                          "2025-01-01", "2025-02-01", slippage_bps=2)
        trade = result["trades"].iloc[0]
        self.assertLessEqual(trade.initial_cash_risk, 100)
        self.assertLessEqual(trade.quantity * trade.entry, 10_000)


if __name__ == "__main__":
    unittest.main()
