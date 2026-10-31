"""Historical premiums use exact contracts and verified prices before the cutoff."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

import nifty_max_pain as nmp
from app.services.option_prices import historical_premiums, latest_traded_close


class OptionPriceTests(unittest.TestCase):
    def client(self):
        client = Mock()
        client.get_option_contracts.return_value = [
            {"expiry": "2026-10-27", "strike_price": 22500, "instrument_type": side, "instrument_key": side}
            for side in ("CE", "PE")
        ]
        client.get_historical_candles_v3.side_effect = lambda key, *args: {"candles": [
            ["2026-10-23T00:00:00+05:30", 0, 0, 0, 100 if key == "CE" else 75]
        ]}
        client.get_previous_option_close.return_value = None
        return client

    def test_complete_dated_prices_enable_pnl_inputs(self):
        rows = [nmp.StrikeRow(22500, 10, 20)]
        result = historical_premiums(self.client(), "NIFTY", "2026-10-27", "2026-10-23", rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["required"], 2)
        self.assertEqual(result["available"], 2)
        self.assertEqual(rows[0].call_ltp, 100)
        self.assertEqual(rows[0].put_ltp, 75)
        self.assertEqual(result["exact"], 2)
        self.assertEqual(result["carried_forward"], 0)

    def test_undated_or_unverified_nearby_response_does_not_establish_a_price(self):
        client = self.client()
        client.get_historical_candles_v3.side_effect = None
        client.get_historical_candles_v3.return_value = {"candles": [["2026-10-22T00:00:00+05:30", 0, 0, 0, 100]]}
        result = historical_premiums(client, "NIFTY", "2026-10-27", "2026-10-23", [nmp.StrikeRow(22500, 10, 20)])
        self.assertFalse(result["complete"])
        self.assertEqual(result["available"], 0)

    def test_verified_earlier_close_completes_coverage_with_original_date_and_age(self):
        client = self.client()
        client.get_historical_candles_v3.side_effect = lambda key, *args: {"candles": [] if key == "CE" else [
            ["2026-10-23T00:00:00+05:30", 0, 0, 0, 75, 10]]}
        client.get_previous_option_close.return_value = {"close": 99.05, "price_date": "2026-10-14"}
        rows = [nmp.StrikeRow(22500, 10, 20)]
        result = historical_premiums(client, "NIFTY", "2026-10-27", "2026-10-23", rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["basis"], "last_available_close")
        self.assertEqual((result["exact"], result["carried_forward"]), (1, 1))
        self.assertEqual(result["carried"][0], {"strike": 22500, "side": "CE", "close": 99.05,
                                             "price_date": "2026-10-14", "age_days": 9, "carried_forward": True})
        self.assertEqual(rows[0].call_ltp, 99.05)
        client.get_previous_option_close.assert_called_once_with("CE", "2026-10-23")
        client.get_ltp_quotes_v3.assert_not_called()

    def test_future_and_excessively_old_fallback_prices_cannot_complete_coverage(self):
        for day in ("2026-10-24", "2025-10-22"):
            with self.subTest(day=day):
                client = self.client()
                client.get_historical_candles_v3.side_effect = None
                client.get_historical_candles_v3.return_value = {"candles": []}
                client.get_previous_option_close.return_value = {"close": 100, "price_date": day}
                result = historical_premiums(client, "NIFTY", "2026-10-27", "2026-10-23", [nmp.StrikeRow(22500, 10, 20)])
                self.assertFalse(result["complete"])
                self.assertEqual(result["available"], 0)

    def test_price_selection_handles_order_ist_cutoff_invalid_and_zero_volume_bars(self):
        candles = [[day, 0, 0, 0, close, volume] for day, close, volume in [
            ("2026-10-22T00:00:00+05:30", 67.05, 10),
            ("2026-10-14T00:00:00+05:30", 99.05, 10),
            ("2026-10-23T00:00:00+05:30", 999, 0),
            ("2026-10-23T20:00:00Z", 999, 10),  # October 24 IST
            ("2026-10-23T00:00:00+05:30", float("nan"), 10),
        ]]
        self.assertEqual(latest_traded_close(candles, "2026-10-01", "2026-10-23"),
                         {"close": 67.05, "price_date": "2026-10-22"})

    def test_failed_latest_price_verification_keeps_pnl_unavailable(self):
        client = self.client()
        client.get_historical_candles_v3.side_effect = None
        client.get_historical_candles_v3.return_value = {"candles": []}
        client.get_previous_option_close.side_effect = RuntimeError("retention or coverage gap")
        result = historical_premiums(client, "NIFTY", "2026-10-27", "2026-10-23", [nmp.StrikeRow(22500, 10, 20)])
        self.assertFalse(result["complete"])
        self.assertEqual(result["missing"][0]["reason"], "RuntimeError")

    def test_missing_or_wrong_contract_blocks_full_portfolio_pnl(self):
        client = self.client()
        client.get_option_contracts.return_value[0]["expiry"] = "2026-11-03"
        result = historical_premiums(client, "NIFTY", "2026-10-27", "2026-10-23", [nmp.StrikeRow(22500, 10, 20)])
        self.assertFalse(result["complete"])
        self.assertEqual(result["available"], 1)
        self.assertEqual(result["missing"][0]["side"], "CE")

    def test_contracts_without_oi_do_not_require_a_price(self):
        rows = [nmp.StrikeRow(22500, 10, 0)]
        result = historical_premiums(self.client(), "NIFTY", "2026-10-27", "2026-10-23", rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["required"], 1)

    def test_contract_master_failure_returns_missing_coverage_not_a_page_failure(self):
        client = self.client()
        client.get_option_contracts.side_effect = RuntimeError("contract master offline")
        result = historical_premiums(client, "NIFTY", "2026-10-27", "2026-10-23", [nmp.StrikeRow(22500, 10, 20)])
        self.assertFalse(result["complete"])
        self.assertEqual(result["available"], 0)
        self.assertIn("contract metadata unavailable", result["missing"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
