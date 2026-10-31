"""AS OF choices must come from observed sessions and respect expiry/today boundaries."""
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.services import max_pain_service as service

KEY = "NSE_INDEX|Nifty 50"
NOW = datetime(2026, 10, 28, 12, tzinfo=service.IST)


class SessionsTests(unittest.TestCase):
    def result(self, expiry, closes, active=False):
        with patch.object(service, "get_upstox", return_value=Mock()), \
             patch.object(service, "_now", return_value=NOW), \
             patch.object(service.nmp, "fetch_daily_closes", return_value=closes) as fetch, \
             patch.object(service, "_session", return_value=(active, None, None)) as today:
            result = service.sessions(expiry, KEY)
        return result, fetch, today

    def test_only_actual_dated_positive_closes_are_choices(self):
        result, fetch, _ = self.result("2026-11-03", {
            "2026-10-23": 22600, "2026-10-26": 22700, "2026-10-27": None,
            "2026-10-28": 22698, "2026-10-29": 22700, "2025-10-20": 22000,
            "2026-10-22": float("nan"), "2026-10-21": 0,
        })
        self.assertEqual(result["dates"], ["2026-10-28", "2026-10-26", "2026-10-23"])
        self.assertEqual(result["instrument_key"], KEY)
        fetch.assert_called_once_with(fetch.call_args.args[0], to_date="2026-10-28", from_date="2025-10-28", key=KEY)

    def test_expired_chain_never_offers_post_expiry_sessions(self):
        result, fetch, today = self.result("2026-10-27", {"2026-10-28": 22700, "2026-10-26": 22700})
        self.assertEqual(result["dates"], ["2026-10-26"])
        self.assertEqual(fetch.call_args.kwargs["to_date"], "2026-10-27")
        today.assert_not_called()

    def test_open_session_can_be_offered_before_daily_candle_exists(self):
        result, _, today = self.result("2026-11-03", {"2026-10-26": 22700}, active=True)
        self.assertEqual(result["dates"], ["2026-10-28", "2026-10-26"])
        self.assertEqual(today.call_args.args[1:], ("2026-10-28", "2026-11-03", KEY))

    def test_missing_data_does_not_create_calendar_or_weekday_dates(self):
        result, _, _ = self.result("2026-11-03", {}, active=False)
        self.assertEqual(result["dates"], [])


if __name__ == "__main__":
    unittest.main()
