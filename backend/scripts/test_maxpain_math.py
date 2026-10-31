"""Dimension and off-strike valuation regressions, without market requests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import nifty_max_pain as nmp


class QuantityTests(unittest.TestCase):
    def test_underlying_units_are_not_multiplied_by_lot_size_again(self):
        # One HDFC lot = 650 units. A ten-rupee intrinsic payout is Rs 6,500.
        for lot in (65, 650):
            result = nmp.compute_max_pain([100, 110], [650, 0], [0, 0], lot, oi_in_units=True)
            self.assertEqual(result.call_payout.tolist(), [0, 6500])
            pnl = nmp.compute_premium_pnl([100], [650], [0], [5], [0], lot,
                                          candidates=[100, 110], oi_in_units=True)
            self.assertEqual(pnl.premium_value, 3250)
            self.assertEqual(pnl.combined_pnl.tolist(), [3250, -3250])
            self.assertEqual(pnl.lot_size, lot)

    def test_explicit_lot_counts_and_unit_counts_produce_same_rupee_payoff(self):
        lots = nmp.compute_max_pain([100, 110], [1, 2], [3, 4], lot_size=650)
        units = nmp.compute_max_pain([100, 110], [650, 1300], [1950, 2600], lot_size=650, oi_in_units=True)
        self.assertEqual(lots.total_payout.tolist(), units.total_payout.tolist())
        self.assertEqual(lots.strike, units.strike)

    def test_pnl_at_spot_and_max_pain_use_exact_prices_not_nearest_strike(self):
        result = nmp.compute_premium_pnl([100], [10], [0], [5], [0],
                                          candidates=[90, 100, 110], spot=103, max_pain=115)
        self.assertEqual(result.pnl_at_spot, 20)
        self.assertEqual(result.pnl_at_max_pain, -100)


if __name__ == "__main__":
    unittest.main()
