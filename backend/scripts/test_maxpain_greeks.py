"""Greeks are sourced per option, with strict capture-date / expiry isolation."""
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.services import maxpain_greeks as greeks
from app.services.market_store import IST

KEY, EXPIRY, DAY = "NSE_INDEX|Nifty 50", "2026-10-27", "2026-10-23"


def chain():
    return [{"underlying_key": KEY, "expiry": EXPIRY, "strike_price": 22600,
        "underlying_spot_price": 22620,
        "call_options": {"option_greeks": {"delta": .52, "gamma": .000123, "theta": -12.5, "vega": 8.3, "iv": 15.2}},
        "put_options": {"option_greeks": {"delta": -.48, "gamma": 0, "theta": -11.2, "vega": 8.3, "iv": 16.1}}}]


class GreeksTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.saved = {"payload": chain(), "observed_at": DAY + "T15:25:00+05:30"}
        self.client.get_retained_option_chain.return_value = self.saved
        self.at = datetime(2026, 10, 26, 12, tzinfo=IST)

    def result(self, **kwargs):
        return greeks.snapshot(self.client, KEY, EXPIRY, DAY, valid_session=True, checked_at=self.at, **kwargs)

    def test_saved_history_keeps_negative_greeks_zero_gamma_and_percentage_iv(self):
        result = self.result()
        self.assertEqual(result["status"], "historical")
        self.assertTrue(result["complete"])
        self.assertEqual((result["available"], result["complete_legs"], result["required"]), (2, 2, 2))
        self.assertEqual(result["rows"][0]["put"]["delta"], -.48)
        self.assertEqual(result["rows"][0]["put"]["gamma"], 0)
        self.assertEqual(result["rows"][0]["call"]["theta"], -12.5)
        self.assertEqual(result["rows"][0]["call"]["iv"], 15.2)
        self.assertIsNone(result["reported_at"])
        self.assertEqual(result["observed_at"], self.saved["observed_at"])
        self.client.get_retained_option_chain.assert_called_once_with(KEY, EXPIRY, DAY)
        self.client.get_option_chain.assert_not_called()
        self.client.get_option_greeks_v3.assert_not_called()

    def test_missing_or_invalid_fields_stay_null_and_do_not_blank_a_valid_side(self):
        values = self.saved["payload"][0]["call_options"]["option_greeks"]
        values.update(delta=1.2, gamma="NaN", theta=None, vega=False, iv=-1)
        result = self.result()
        self.assertEqual(result["rows"][0]["call"], dict.fromkeys(greeks.FIELDS))
        self.assertTrue(result["data_available"])
        self.assertFalse(result["complete"])
        self.assertEqual(result["complete_legs"], 1)
        self.assertEqual(result["available"], 1)
        self.assertIn("1/2", result["hint"])

    def test_missing_capture_does_not_fetch_current_data_or_synthesize_from_oi(self):
        self.client.get_retained_option_chain.return_value = None
        result = self.result()
        self.assertFalse(result["data_available"])
        self.assertEqual(result["rows"], [])
        self.assertIn("No option Greeks snapshot was saved", result["hint"])
        self.client.get_option_chain.assert_not_called()
        self.client.get_option_greeks_v3.assert_not_called()

    def test_nontrading_missing_future_or_post_expiry_session_never_reads_the_archive(self):
        result = greeks.snapshot(self.client, KEY, EXPIRY, "2026-10-24", valid_session=False,
                                 checked_at=self.at, session_hint="No NSE trading session")
        self.assertEqual(result["hint"], "No NSE trading session")
        self.assertFalse(result["data_available"])
        self.client.get_retained_option_chain.assert_not_called()

    def test_wrong_day_future_naive_and_preopen_captures_are_rejected(self):
        for value in ("2026-10-24T15:25:00+05:30", "2026-10-27T15:25:00+05:30", "2026-10-23T15:25:00", "2026-10-23T08:25:00+05:30"):
            with self.subTest(value=value):
                self.saved["observed_at"] = value
                self.assertFalse(self.result()["data_available"])
        self.at = datetime(2026, 10, 23, 12, tzinfo=IST)
        self.saved["observed_at"] = DAY + "T15:25:00+05:30"
        self.assertFalse(self.result()["data_available"])

    def test_wrong_expiry_underlying_duplicate_or_nonfinite_strike_is_rejected(self):
        for field, value in (("expiry", "2026-11-03"), ("underlying_key", "NSE_INDEX|Nifty Bank"), ("strike_price", "nan")):
            with self.subTest(field=field):
                raw = chain()
                raw[0][field] = value
                self.saved["payload"] = raw
                self.assertFalse(self.result()["data_available"])
        self.saved["payload"] = chain() * 2
        self.assertFalse(self.result()["data_available"])

    def test_current_cache_timestamp_is_not_replaced_with_page_check_time(self):
        self.saved["observed_at"] = "2026-10-26T11:59:59+05:30"
        result = greeks.snapshot(self.client, KEY, EXPIRY, "2026-10-26", valid_session=True, checked_at=self.at)
        self.assertEqual(result["status"], "retained")
        self.assertEqual(result["observed_at"], self.saved["observed_at"])
        self.saved["observed_at"] = "2026-10-26T12:00:01+05:30"
        self.at = datetime(2026, 10, 26, 12, 0, 20, tzinfo=IST)
        result = greeks.snapshot(self.client, KEY, EXPIRY, "2026-10-26", valid_session=True, checked_at=self.at)
        self.assertEqual(result["status"], "snapshot")

    def test_a_chain_without_greeks_is_not_presented_as_zero_risk(self):
        self.saved["payload"][0]["call_options"].pop("option_greeks")
        self.saved["payload"][0]["put_options"]["option_greeks"] = None
        result = self.result()
        self.assertFalse(result["data_available"])
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["rows"][0]["put"]["gamma"])
        self.assertEqual(result["available"], 0)


if __name__ == "__main__":
    unittest.main()
