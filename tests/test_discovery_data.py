"""Frozen source/panel facts; skips cleanly outside this retained research run."""
import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / 'artifacts' / 'swing_discovery'


@unittest.skipUnless((OUT / 'daily-panel.npz').exists(), 'frozen research artifact not present')
class FrozenDiscoveryDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arrays = np.load(OUT / 'daily-panel.npz')
        cls.index = json.loads((OUT / 'panel-index.json').read_text(encoding='utf-8'))
        cls.universe = json.loads((OUT / 'universe.json').read_text(encoding='utf-8'))
        cls.audit = json.loads((OUT / 'data-audit.json').read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        cls.arrays.close()

    def test_dated_source_precedes_performance_and_keeps_all_names(self):
        self.assertEqual(self.universe['date'], '2024-10-31')
        self.assertLess(self.universe['publication_date'], self.universe['research_start'])
        self.assertEqual(len(self.universe['stocks']), 500)
        self.assertEqual(self.universe['historical_nifty50_crosscheck_missing_isins'], [])

    def test_eligible_research_prices_are_complete(self):
        dates = pd.to_datetime(self.index['dates'], utc=True)
        test = dates >= pd.Timestamp('2024-11-11', tz='Asia/Kolkata')
        eligible = self.arrays['eligible']
        self.assertEqual(self.arrays['actual_close'].shape, (500, 1704))
        self.assertEqual(int(test.sum()), 495)
        self.assertEqual(int(eligible.sum()), 470)
        self.assertTrue(np.isfinite(self.arrays['actual_close'][eligible][:, test]).all())

    def test_price_unit_identity(self):
        actual = self.arrays['actual_close']
        reconstructed = self.arrays['neutral_close'] * self.arrays['unit_factor']
        valid = np.isfinite(actual)
        self.assertTrue(np.allclose(actual[valid], reconstructed[valid]))

    def test_unavailable_original_holdings_are_explicitly_retained(self):
        rows = self.audit['stock_audits']
        for symbol in ('GSPL', 'ISEC', 'JBCHEPHARM', 'PEL'):
            self.assertFalse(rows[symbol]['eligible'])
            self.assertEqual(rows[symbol]['acquisition']['status'], 'unavailable')
            self.assertTrue(rows[symbol]['exclusion_reasons'])


if __name__ == '__main__':
    unittest.main()
