"""As-of isolation and missing-data regression tests, without network access."""
import copy
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

import nifty_max_pain as nmp
from app.services import max_pain_service as service
from app.services.option_prices import historical_premiums

KEY = "NSE_INDEX|Nifty 50"
EXPIRY = "2026-10-27"
DAY = "2026-10-22"
CLOSE = 22687.65


class AsOfTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.get_historical_candles_v3.return_value = {
            "candles": [[DAY + "T00:00:00+05:30", 0, 0, 0, CLOSE]]
        }
        self.provider = {
            "instrument_key": KEY, "expiry_date": "27-10-2026",
            "spot_closing_price": CLOSE, "max_pain": 22850,
            "insights": [{"time": "10:15", "spot_price": 22677.35, "max_pain": 22800}],
        }
        self.oi = {
            "expiry": "27-10-2026", "spot_closing_price": CLOSE,
            "call_put_oi_data_list": [
                {"strike_price": 22500, "call_oi": 10, "put_oi": 30},
                {"strike_price": 23000, "call_oi": 40, "put_oi": 20},
            ],
        }
        self.client.get_max_pain.return_value = copy.deepcopy(self.provider)
        self.client.get_oi_data.return_value = copy.deepcopy(self.oi)
        self.client.get_intraday_candles_v3.return_value = {"candles": []}
        self.patches = [
            patch.object(service, "get_upstox", return_value=self.client),
            patch.object(service, "_now", return_value=datetime(2026, 10, 24, 16, 0, tzinfo=ZoneInfo("Asia/Kolkata"))),
            patch.object(nmp, "list_expiries", return_value=[{"expiry": EXPIRY, "lot_size": 65}]),
            patch.object(service, "historical_premiums", return_value={"complete": False, "available": 0, "required": 4}),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def test_historical_snapshot_never_reads_current_chain_quotes_or_premiums(self):
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.client.get_option_chain.assert_not_called()
        self.client.get_ltp_quotes_v3.assert_not_called()
        self.client.get_oi_data.assert_called_once_with(KEY, expiry=EXPIRY, date=DAY)
        self.assertEqual(result["spot"], CLOSE)
        self.assertEqual(result["call_oi_total"], 50)
        self.assertEqual(result["put_oi_total"], 50)
        self.assertEqual(result["source"], "upstox.oi_snapshot")
        self.assertIsNone(result["premium_pnl"])
        self.assertIsNone(result["strikes"][0]["call_prev_oi"])
        self.assertIsNone(result["strikes"][0]["call_ltp"])
        self.assertTrue(result["payout_curve"]["candidates"])

    def test_saved_greeks_are_exposed_without_using_current_chain_for_history(self):
        self.client.get_retained_option_chain.return_value = {
            "observed_at": DAY + "T15:25:00+05:30",
            "payload": [{"underlying_key": KEY, "expiry": EXPIRY, "strike_price": 22500,
                "underlying_spot_price": 22620,
                "call_options": {"option_greeks": {"delta": .65, "gamma": 0, "theta": -12, "vega": 5, "iv": 15}},
                "put_options": {"option_greeks": {"delta": -.35, "gamma": 0, "theta": -10, "vega": 5, "iv": 16}}}],
        }
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertTrue(result["option_greeks"]["complete"])
        self.assertEqual(result["option_greeks"]["as_of"], DAY)
        self.assertEqual(result["option_greeks"]["status"], "historical")
        self.assertEqual(result["option_greeks"]["rows"][0]["put"]["delta"], -.35)
        self.assertIsNone(result["availability"]["greeks"])
        self.client.get_option_chain.assert_not_called()
        self.client.get_option_greeks_v3.assert_not_called()

    def test_complete_historical_closes_feed_pnl_with_the_correct_premium_basis(self):
        self.client.get_option_contracts.return_value = [
            {"expiry": EXPIRY, "strike_price": strike, "instrument_type": side, "instrument_key": f"{strike}{side}"}
            for strike in (22500, 23000) for side in ("CE", "PE")
        ]
        prices = {"22500CE": 100, "22500PE": 75, "23000CE": 50, "23000PE": 200}
        def candles(key, *args):
            return {"candles": [[DAY + "T00:00:00+05:30", 0, 0, 0, prices.get(key, CLOSE)]]}
        self.client.get_historical_candles_v3.side_effect = candles
        with patch.object(service, "historical_premiums", side_effect=historical_premiums):
            result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertTrue(result["premium_prices"]["complete"])
        self.assertEqual(result["premium_pnl"]["scenarios"]["snapshot"]["premium_value"], 9250)
        self.assertIn(DAY + " option daily candle close", result["premium_pnl"]["assumption"])
        self.client.get_option_chain.assert_not_called()

    def test_carried_premium_enables_pnl_and_exposes_original_price_date(self):
        self.client.get_option_contracts.return_value = [
            {"expiry": EXPIRY, "strike_price": strike, "instrument_type": side, "instrument_key": f"{strike}{side}"}
            for strike in (22500, 23000) for side in ("CE", "PE")
        ]
        prices = {"22500PE": 75, "23000CE": 50, "23000PE": 200}
        def candles(key, *args):
            return {"candles": [] if key == "22500CE" else [[DAY + "T00:00:00+05:30", 0, 0, 0, prices.get(key, CLOSE)]]}
        self.client.get_historical_candles_v3.side_effect = candles
        self.client.get_previous_option_close.return_value = {"close": 100, "price_date": "2026-10-14"}
        with patch.object(service, "historical_premiums", side_effect=historical_premiums):
            result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertTrue(result["premium_prices"]["complete"])
        self.assertEqual(result["premium_prices"]["carried_forward"], 1)
        self.assertEqual(result["premium_pnl"]["scenarios"]["snapshot"]["premium_value"], 9250)
        self.assertIn("1 prices carried forward", result["premium_pnl"]["assumption"])
        self.assertEqual(result["strikes"][0]["call_premium_date"], "2026-10-14")
        self.assertEqual(result["strikes"][0]["put_premium_date"], DAY)
        self.assertIsNone(result["availability"]["premiums"])
        self.client.get_option_chain.assert_not_called()
        self.client.get_full_market_quote_v3.assert_not_called()

    def test_missing_date_stays_empty_and_never_switches_expiry(self):
        self.client.get_max_pain.return_value = {}
        self.client.get_oi_data.return_value = {}
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertFalse(result["data_available"])
        self.assertEqual(result["expiry"], EXPIRY)
        self.assertEqual(result["as_of"], DAY)
        self.assertIsNone(result["fallback"])
        for field in ("spot", "max_pain", "call_oi_total", "put_oi_total", "pcr", "premium_pnl"):
            self.assertIsNone(result[field], field)
        self.assertEqual(result["strikes"], [])
        self.assertEqual(result["insights"], [])
        self.assertEqual(result["payout_curve"]["candidates"], [])
        self.client.get_option_chain.assert_not_called()
        nmp.list_expiries.assert_called_once()

    def test_nontrading_day_rejects_carried_forward_analytics(self):
        self.client.get_historical_candles_v3.return_value = {"candles": []}
        self.client.get_intraday_candles_v3.return_value = {
            "candles": [["2026-10-23T15:29:00+05:30", 0, 0, 0, 22600]]
        }
        result = service.snapshot(EXPIRY, "2026-10-24", KEY)
        intraday = service.intraday(EXPIRY, "2026-10-24", KEY)
        self.assertFalse(result["data_available"])
        self.assertFalse(intraday["data_available"])
        self.assertEqual(intraday["insights"], [])
        self.client.get_max_pain.assert_not_called()
        self.client.get_oi_data.assert_not_called()
        self.client.get_option_chain.assert_not_called()

    def test_future_and_after_expiry_dates_do_not_fetch_market_values(self):
        for expiry, day in [(EXPIRY, "2026-10-25"), ("2026-10-20", DAY)]:
            with self.subTest(expiry=expiry, day=day):
                self.assertFalse(service.snapshot(expiry, day, KEY)["data_available"])
                self.assertEqual(service.intraday(expiry, day, KEY)["insights"], [])
        self.client.get_max_pain.assert_not_called()
        self.client.get_oi_data.assert_not_called()
        self.client.get_historical_candles_v3.assert_not_called()

    def test_wrong_expiry_date_underlying_or_closing_spot_is_rejected(self):
        for change in [
            {"expiry_date": "03-11-2026"}, {"date": "2026-10-23"},
            {"instrument_key": "NSE_EQ|INE040A01034"}, {"spot_closing_price": 22600},
        ]:
            with self.subTest(change=change):
                self.client.get_max_pain.return_value = {**self.provider, **change}
                self.client.get_oi_data.return_value = {**self.oi, **change}
                result = service.snapshot(EXPIRY, DAY, KEY)
                self.assertFalse(result["data_available"])
                self.assertEqual(service.intraday(EXPIRY, DAY, KEY)["insights"], [])

    def test_partial_provider_data_does_not_invent_oi_or_premiums(self):
        self.client.get_oi_data.return_value = {}
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertEqual(result["max_pain"], 22850)
        self.assertEqual(result["spot"], CLOSE)
        self.assertIsNone(result["call_oi_total"])
        self.assertIsNone(result["premium_pnl"])
        self.assertEqual(result["payout_curve"]["candidates"], [])

    def test_missing_strike_oi_is_not_replaced_with_zero(self):
        self.client.get_oi_data.return_value["call_put_oi_data_list"][0]["call_oi"] = None
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertIsNone(result["call_oi_total"])
        self.assertEqual(result["strikes"], [])
        self.assertEqual(result["payout_curve"]["candidates"], [])

    def test_empty_or_invalid_intraday_measurements_are_not_data_points(self):
        self.client.get_max_pain.return_value["insights"] = [
            {"time": "10:15", "spot_price": None, "max_pain": None},
            {"time": "invalid", "spot_price": 22600},
        ]
        result = service.intraday(EXPIRY, DAY, KEY)
        self.assertFalse(result["data_available"])
        self.assertEqual(result["insights"], [])

    def test_unknown_lot_does_not_block_payout_from_known_underlying_quantities(self):
        nmp.list_expiries.return_value = []
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertTrue(result["data_available"])
        self.assertIsNone(result["lot_size"])
        self.assertIsNotNone(result["max_pain"])
        self.assertEqual(result["payout_curve"]["candidates"], [22500, 23000])
        self.assertEqual(result["min_payout"], 5000)
        self.assertEqual(result["oi_unit"], "underlying_units")

    def test_unavailable_contract_master_does_not_hide_retained_analytics(self):
        nmp.list_expiries.side_effect = RuntimeError("contract master unavailable")
        result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertTrue(result["data_available"])
        self.assertIsNone(result["lot_size"])
        self.assertEqual(result["spot"], CLOSE)

    def test_current_session_uses_chain_but_only_after_dated_session_evidence(self):
        with patch.object(service, "_now", return_value=datetime(2026, 10, 22, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))):
            self.client.get_option_chain.return_value = [{
                "strike_price": 22500, "underlying_spot_price": 22650,
                "call_options": {"market_data": {"oi": 100, "prev_oi": 80, "ltp": 150}},
                "put_options": {"market_data": {"oi": 200, "prev_oi": 190, "ltp": 20}},
            }]
            self.client.get_max_pain.return_value["insights"].append({"time": "13:15", "max_pain": 23000})
            result = service.snapshot(EXPIRY, DAY, KEY)
            self.assertEqual(result["spot"], 22650)
            self.assertEqual(result["call_oi_total"], 100)
            self.assertEqual(result["source"], "upstox.option_chain")
            self.assertIsNotNone(result["premium_pnl"])
            self.assertEqual([row["time"] for row in result["insights"]], ["10:15"])
            self.client.get_oi_data.assert_not_called()

    def test_open_session_does_not_require_a_completed_daily_candle(self):
        with patch.object(service, "_now", return_value=datetime(2026, 10, 22, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))):
            self.client.get_historical_candles_v3.return_value = {"candles": []}
            self.client.get_intraday_candles_v3.return_value = {"candles": [[DAY + "T11:59:00+05:30", 0, 0, 0, 22677]]}
            result = service.intraday(EXPIRY, DAY, KEY)
            self.assertTrue(result["data_available"])

    def test_confirmed_closed_session_skips_candles_chain_and_analytics(self):
        self.client.get_market_timings.return_value = []
        result = service.snapshot(EXPIRY, "2026-10-24", KEY)
        self.assertFalse(result["data_available"])
        self.assertIn("No NSE trading session", result["hint"])
        self.client.get_historical_candles_v3.assert_not_called()
        self.client.get_intraday_candles_v3.assert_not_called()
        self.client.get_option_chain.assert_not_called()
        self.client.get_max_pain.assert_not_called()

    def test_special_weekend_session_is_not_rejected_by_weekday(self):
        self.client.get_market_timings.return_value = [{"exchange": "NSE", "start_time": 1, "end_time": 2}]
        self.client.get_historical_candles_v3.return_value = {"candles": [["2026-10-24T00:00:00+05:30", 0, 0, 0, CLOSE]]}
        self.live_chain()
        self.assertTrue(service.snapshot(EXPIRY, "2026-10-24", KEY)["data_available"])

    def live_chain(self):
        self.client.get_option_chain.return_value = [{
            "strike_price": 22500, "underlying_spot_price": 22650,
            "call_options": {"market_data": {"oi": 650, "ltp": 150}},
            "put_options": {"market_data": {"oi": 1300, "ltp": 20}},
        }]

    def test_missing_live_previous_oi_is_not_a_zero_baseline(self):
        self.live_chain()
        with patch.object(service, "_now", return_value=datetime(2026, 10, 22, 12, tzinfo=service.IST)):
            result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertIsNone(result["strikes"][0]["call_prev_oi"])
        self.assertIsNone(result["strikes"][0]["put_prev_oi"])
        self.assertIn("unavailable", result["availability"]["oi_change"])
        self.assertEqual(result["premium_pnl"]["scenarios"]["snapshot"]["premium_value"], 123500)

    def test_missing_live_premium_blocks_full_pnl_but_keeps_oi_and_priced_leg(self):
        self.live_chain()
        self.client.get_option_chain.return_value[0]["put_options"]["market_data"].pop("ltp")
        with patch.object(service, "_now", return_value=datetime(2026, 10, 22, 12, tzinfo=service.IST)):
            result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertTrue(result["data_available"])
        self.assertIsNone(result["premium_pnl"])
        self.assertIn("1/2", result["availability"]["premiums"])
        self.assertEqual(result["strikes"][0]["call_ltp"], 150)
        self.assertIsNone(result["strikes"][0]["put_ltp"])

    def test_bad_live_oi_is_not_zero_and_verified_dated_oi_remains_usable(self):
        self.live_chain()
        self.client.get_option_chain.return_value[0]["call_options"]["market_data"].pop("oi")
        with patch.object(service, "_now", return_value=datetime(2026, 10, 22, 12, tzinfo=service.IST)):
            result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertEqual(result["source"], "upstox.oi_snapshot")
        self.assertEqual(result["call_oi_total"], 50)
        self.assertIsNone(result["premium_pnl"])

    def test_provider_outage_does_not_hide_independent_chain_data(self):
        self.live_chain()
        self.client.get_max_pain.side_effect = RuntimeError("provider analytics outage")
        with patch.object(service, "_now", return_value=datetime(2026, 10, 22, 12, tzinfo=service.IST)):
            result = service.snapshot(EXPIRY, DAY, KEY)
        self.assertEqual(result["source"], "upstox.option_chain")
        self.assertEqual(result["call_oi_total"], 650)
        self.assertIsNone(result["provider_max_pain"])
        self.assertIsNotNone(result["premium_pnl"])


class ExpiryTests(unittest.TestCase):
    def test_stocks_use_actual_retained_expiries_without_invented_weekly_dates(self):
        client = Mock()
        client.get_known_expiries.return_value = [
            {"expiry": "2026-09-28", "available": True},  # real, holiday-shifted date
            {"expiry": "2026-10-27", "available": False},
        ]
        with patch.object(service, "_now", return_value=datetime(2026, 10, 25, 12, tzinfo=service.IST)), \
             patch.object(service, "get_upstox", return_value=client), patch.object(nmp, "list_expiries", return_value=[
            {"expiry": EXPIRY, "weekly": False, "lot_size": 650, "n_contracts": 48}
        ]):
            rows = service.list_expiries("HDFC")
            current = service.list_expiries("HDFC", include_past=False)
        self.assertEqual([row["expiry"] for row in rows], ["2026-09-28", EXPIRY])
        self.assertEqual(rows[0]["cycle"], "unknown")
        self.assertIsNone(rows[0]["lot_size"])
        self.assertEqual([row["expiry"] for row in current], [EXPIRY])
        self.assertTrue(all("issue_date" not in row for row in rows))
        client.get_oi_data.assert_not_called()
        client.get_expired_expiries.assert_not_called()


class HistoryTests(unittest.TestCase):
    def test_history_uses_selected_underlying_expiry_exact_time_and_date_cutoff(self):
        client = Mock()
        stock = "NSE_EQ|INE040A01034"
        client.get_historical_candles_v3.return_value = {"candles": [
            ["2026-10-22T00:00:00+05:30", 0, 0, 0, 690.25],
            ["2026-10-23T00:00:00+05:30", 0, 0, 0, 691.5],
            ["2026-10-25T00:00:00+05:30", 0, 0, 0, 700],
        ]}

        def provider(key, expiry, date, bucket_interval):
            self.assertEqual(key, stock)
            self.assertEqual(expiry, EXPIRY)
            self.assertEqual(bucket_interval, 1)
            return {"instrument_key": stock, "expiry_date": "27-10-2026",
                    "spot_closing_price": 690.25 if date == DAY else 691.5,
                    "insights": [{"time": "10:15" if date == DAY else "10:14", "max_pain": 720, "spot_price": 690}]}

        client.get_max_pain.side_effect = provider
        points = nmp.build_history(client, [], EXPIRY, "2026-10-23", 7, key=stock, include_other_expiries=False)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].obs_date, DAY)
        self.assertEqual(points[0].obs_time, "10:15")
        self.assertEqual(points[0].expiry_close, 690.25)
        client.get_historical_candles_v3.assert_called_once_with(stock, "days", 1, "2026-10-23", "2026-10-16")

    def test_no_verified_sessions_means_no_history_probes_or_rows(self):
        client = Mock()
        client.get_historical_candles_v3.return_value = {"candles": []}
        self.assertEqual(nmp.build_history(client, [], EXPIRY, DAY, 7, include_other_expiries=False), [])
        client.get_max_pain.assert_not_called()

    def test_missing_exact_time_is_not_replaced_by_nearby_time(self):
        self.assertIsNone(nmp._pick_insight_row([{"time": "10:14"}, {"time": "10:16"}], "10:15"))


if __name__ == "__main__":
    unittest.main()
