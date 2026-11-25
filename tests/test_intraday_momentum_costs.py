"""Independent arithmetic and input-boundary checks; no data or database access."""
import unittest

from research.intraday_momentum.costs import adverse_price, fees


class FeeTests(unittest.TestCase):
    def test_known_round_trip_arithmetic(self):
        buy = fees('BUY', 1000.0, 100)
        sell = fees('SELL', 1010.0, 100)
        # Independently expanded charges for ₹100,000 and ₹101,000 turnovers.
        expected = (40 + 6.1707 + .201 + 25.25 + 3
                    + .18 * (40 + 6.1707 + .201))
        self.assertAlmostEqual(buy['total'] + sell['total'], expected, places=10)
        self.assertAlmostEqual(expected, 82.968606, places=6)
        self.assertEqual(round(expected, 2), 82.97)

    def test_side_specific_taxes_and_no_delivery_fee(self):
        buy = fees('BUY', 100.0, 100)
        sell = fees('SELL', 100.0, 100)
        self.assertEqual(buy['stt'], 0)
        self.assertAlmostEqual(buy['stamp'], .3)
        self.assertAlmostEqual(sell['stt'], 2.5)
        self.assertEqual(sell['stamp'], 0)
        self.assertEqual(buy['dp'], 0)
        self.assertEqual(sell['dp'], 0)

    def test_brokerage_cap_and_combined_exchange_charge(self):
        small = fees('BUY', 100.0, 10)
        large = fees('BUY', 1000.0, 100)
        self.assertEqual(small['brokerage'], 1)
        self.assertEqual(large['brokerage'], 20)
        self.assertAlmostEqual(large['exchange_ipft'], 3.07)
        self.assertAlmostEqual(large['gst'], .18 * (20 + 3.07 + .1))
        self.assertAlmostEqual(large['total'], sum(
            large[k] for k in ('brokerage', 'exchange_ipft', 'sebi', 'gst', 'stt', 'stamp', 'dp')))

    def test_price_and_quantity_must_be_valid(self):
        for value in (0, -1, float('nan'), float('inf'), -float('inf'), True, '100', None):
            with self.subTest(price=value), self.assertRaises(ValueError):
                fees('BUY', value, 1)
        for value in (0, -1, 1.5, 1.0, float('nan'), float('inf'), True, '1', None):
            with self.subTest(quantity=value), self.assertRaises(ValueError):
                fees('BUY', 100, value)
        for value in ('SHORT', '', ' BUY ', None, True):
            with self.subTest(side=value), self.assertRaises(ValueError):
                fees(value, 100, 1)
        with self.assertRaises(ValueError):
            fees('BUY', 1e308, 100)


class SlippageTests(unittest.TestCase):
    def test_adverse_direction_and_basis_points(self):
        self.assertAlmostEqual(adverse_price(100, 'BUY', 10), 100.1)
        self.assertAlmostEqual(adverse_price(100, 'SELL', 10), 99.9)
        self.assertAlmostEqual(adverse_price(100, 'BUY', 25), 100.25)
        self.assertAlmostEqual(adverse_price(100, 'SELL', 25), 99.75)
        self.assertEqual(adverse_price(100, 'BUY', 0), 100)
        self.assertEqual(adverse_price(100, 'SELL', 0), 100)

    def test_invalid_slippage_cannot_create_a_fill(self):
        for value in (-1, 10000, 10001, float('nan'), float('inf'), True, '10', None):
            with self.subTest(bps=value), self.assertRaises(ValueError):
                adverse_price(100, 'BUY', value)
        for value in (0, -1, float('nan'), float('inf'), True, '100', None):
            with self.subTest(raw=value), self.assertRaises(ValueError):
                adverse_price(value, 'SELL', 10)
        with self.assertRaises(ValueError):
            adverse_price(100, 'SHORT', 10)
        with self.assertRaises(ValueError):
            adverse_price(1.7e308, 'BUY', 9999)


if __name__ == '__main__':
    unittest.main(verbosity=2)
