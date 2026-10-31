"""Cash-flow source units, reconciliation and same-session verification."""
import copy
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from app.services.nifty_cash_flows import corroborate_upstox, parse_nse_cash
from app.services.nifty_sources import parse_flows

SCHEMA = {"columns": [{"name": name, "heading": name, "subHead": "(₹ Crores)"}
                       for name in ("buyValue", "sellValue", "netValue")]}
PAYLOAD = [
    {"category": "FII/FPI", "date": "23-Oct-2026", "buyValue": "14,445.54", "sellValue": "13,557.89", "netValue": "887.65"},
    {"category": "DII", "date": "23-Oct-2026", "buyValue": "19,232.31", "sellValue": "15,996.95", "netValue": "3235.36"},
]
AT = "2026-10-24T17:00:00+00:00"


class CashFlowTests(unittest.TestCase):
    def parse(self, payload=None, schema=None):
        return parse_nse_cash(payload if payload is not None else PAYLOAD,
                              schema if schema is not None else SCHEMA, AT, today=date(2026, 10, 24))

    def test_crore_values_are_not_divided_again_and_report_date_is_not_release_time(self):
        fii, dii = self.parse()
        self.assertEqual(fii["value"], 887.65)
        self.assertEqual(dii["value"], 3235.36)
        self.assertEqual(fii["context"]["gross_buy_cr"], 14445.54)
        self.assertEqual(fii["context"]["gross_sell_cr"], 13557.89)
        self.assertEqual(fii["reporting_date"], "2026-10-23")
        self.assertEqual(fii["reported_at"], "2026-10-23T00:00:00+05:30")
        self.assertIn("not publication time", fii["basis"])
        self.assertTrue(fii["context"]["provisional"])
        self.assertEqual(fii["quality"], "exchange_report")
        self.assertNotIn("quality_note", fii)

    def test_units_must_be_explicit_for_every_money_column(self):
        for label in ("INR", "Crores", "USD Crores", "(₹ Lakhs)", ""):
            schema = copy.deepcopy(SCHEMA)
            schema["columns"][1]["subHead"] = label
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.parse(schema=schema)

    def test_bad_totals_missing_values_nonfinite_and_negative_gross_are_rejected(self):
        for changes in ({"netValue": "999"}, {"buyValue": None}, {"buyValue": "NaN"},
                        {"sellValue": "Infinity"}, {"sellValue": "-12"}):
            rows = copy.deepcopy(PAYLOAD)
            rows[0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.parse(rows)

    def test_zero_and_net_selling_are_valid(self):
        rows = copy.deepcopy(PAYLOAD)
        rows[0].update(buyValue="100", sellValue="100", netValue="0")
        rows[1].update(buyValue="100", sellValue="120", netValue="-20")
        fii, dii = self.parse(rows)
        self.assertEqual(fii["value"], 0)
        self.assertEqual(dii["value"], -20)

    def test_categories_dates_duplicates_and_future_sessions_are_validated(self):
        cases = [PAYLOAD[:1], [PAYLOAD[0], PAYLOAD[0]],
                 [PAYLOAD[0], {**PAYLOAD[1], "date": "22-Oct-2026"}],
                 [{**PAYLOAD[0], "date": "25-Oct-2026"}, PAYLOAD[1]],
                 [{**PAYLOAD[0], "date": "bad"}, PAYLOAD[1]],
                 [{**PAYLOAD[0], "category": "Unknown"}, PAYLOAD[1]]]
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.parse(rows)

    def test_provider_corroboration_requires_same_session_and_both_legs(self):
        provider = parse_flows({"NSE_EQ|CASH": [{"time_stamp": "2026-10-23T00:00:00+05:30",
            "buy_amount": 14445.54, "sell_amount": 13557.89}]}, "fii_cash", AT)
        official = corroborate_upstox(self.parse(), provider)
        proof = official[0]["context"]["upstox_verification"]
        self.assertTrue(proof["matched"])
        self.assertEqual(proof["verified_raw_unit"], "₹ crore")
        self.assertFalse(official[1]["context"]["upstox_verification"]["matched"])
        provider[0]["context"]["raw_sell_amount"] = 13000
        self.assertFalse(corroborate_upstox(self.parse(), provider)[0]["context"]["upstox_verification"]["matched"])
        provider[0]["reported_at"] = "2026-10-22T00:00:00+05:30"
        self.assertFalse(corroborate_upstox(self.parse(), provider)[0]["context"]["upstox_verification"]["matched"])

    def test_missing_provider_is_not_a_blocker_for_an_explicit_exchange_unit(self):
        official = corroborate_upstox(self.parse(), [])
        self.assertEqual(official[0]["value"], 887.65)
        self.assertEqual(official[0]["context"]["unit_status"], "verified")


if __name__ == "__main__":
    unittest.main()
