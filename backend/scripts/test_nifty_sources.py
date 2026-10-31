"""Provider contracts, units, timestamp provenance and failure isolation."""
import sys
import unittest
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.services import nifty_sources as sources
from app.services.nifty_store import content_key, timestamp

AT = "2026-10-24T18:00:00+00:00"


class SourceTests(unittest.TestCase):
    def test_quotes_use_source_timestamp_and_previous_close_not_cache_time(self):
        quote = {"NSE_INDEX:Nifty 50": {"instrument_token": sources.NIFTY_KEY,
            "last_price": 25000, "prev_close_price": 24500, "timestamp": "2026-10-23T15:30:00+05:30"}}
        row = sources.parse_quotes(quote, {"nifty_spot": sources.NIFTY_KEY}, AT)[0]
        self.assertEqual(row["reported_at"], "2026-10-23T10:00:00+00:00")
        self.assertEqual(row["observed_at"], AT)
        self.assertEqual(row["change"], 500)
        self.assertAlmostEqual(row["change_pct"], 500 / 24500 * 100)
        del quote["NSE_INDEX:Nifty 50"]["timestamp"]
        self.assertEqual(sources.parse_quotes(quote, {"nifty_spot": sources.NIFTY_KEY}, AT), [])

    def test_flow_schema_requires_segment_timestamp_and_preserves_real_zero(self):
        payload = {"NSE_EQ|CASH": [{"time_stamp": 1792713600000,
            "buy_amount": 1_200_000_000, "sell_amount": 1_000_000_000},
            {"time_stamp": 1792800000000, "buy_amount": 500_000_000, "sell_amount": 500_000_000}]}
        rows = sources.parse_flows(payload, "fii_cash", AT)
        self.assertEqual([row["value"] for row in rows], [20, 0])
        self.assertEqual(rows[1]["previous_value"], 20)
        self.assertEqual(rows[0]["context"]["gross_buy_cr"], 120)
        self.assertEqual(rows[0]["unit"], "₹ crore")
        with self.assertRaises(ValueError):
            sources.parse_flows({"data": [{"net": 20}]}, "fii_cash", AT)
        with self.assertRaises(ValueError):
            sources.parse_flows({"NSE_EQ|CASH": [{"buy_amount": 2, "sell_amount": 1}]}, "dii_cash", AT)

    def test_live_cash_scale_anomaly_retains_raw_amounts_without_inventing_crore_units(self):
        rows = sources.parse_flows({"NSE_EQ|CASH": [
            {"time_stamp": 1792713600000, "buy_amount": 14445.54, "sell_amount": 13557.89},
            {"time_stamp": 1792800000000, "buy_amount": 0, "sell_amount": 0}]}, "fii_cash", AT)
        anomaly = rows[0]
        self.assertIsNone(anomaly["value"])
        self.assertEqual(anomaly["quality"], "unverified_units")
        self.assertEqual(anomaly["context"]["raw_buy_amount"], 14445.54)
        self.assertEqual(anomaly["context"]["raw_sell_amount"], 13557.89)
        self.assertIsNone(anomaly["context"]["gross_buy_cr"])
        self.assertEqual(anomaly["context"]["provider_amount_unit"], "INR")
        self.assertEqual(rows[1]["value"], 0)
        self.assertNotIn("quality", rows[1])

    def test_participant_positions_keep_unknown_fields_and_compute_only_known_differences(self):
        payload = {"NSE_FO|INDEX_FUTURES": [
            {"time_stamp": 1792713600000, "total_long_contracts": 100, "total_short_contracts": 40, "buy_amount": 1000},
            {"time_stamp": 1792800000000, "total_long_contracts": 110, "total_short_contracts": 0}],
            "NSE_FO|INDEX_OPTIONS": [{"time_stamp": 1792800000000, "total_call_long_contracts": 0,
                "total_put_long_contracts": 90, "total_call_short_contracts": 100}]}
        futures = sources.parse_positioning(payload, "fii_index_futures", AT)
        self.assertEqual(futures[0]["value"]["net_contracts"], 60)
        self.assertEqual(futures[1]["value"]["net_contracts"], 110)
        self.assertEqual(futures[1]["context"]["changes"]["total_long_contracts"], 10)
        self.assertEqual(futures[1]["context"]["changes"]["total_short_contracts"], -40)
        self.assertIsNone(futures[1]["value"]["buy_amount"])
        options = sources.parse_positioning(payload, "fii_index_options", AT)[0]
        self.assertEqual(options["value"]["total_call_long_contracts"], 0)
        self.assertIsNone(options["value"]["total_put_short_contracts"])
        self.assertNotIn("net_contracts", options["value"])
        with self.assertRaises(ValueError):
            sources.parse_positioning({"NSE_FO|INDEX_FUTURES": [{"time_stamp": 1792800000000}]}, "fii_index_futures", AT)

    def chart(self, symbol="^TNX"):
        day = datetime(2026, 10, 20, 13, 30, tzinfo=timezone.utc)
        stamps = [int((day + timedelta(days=i)).timestamp()) for i in range(4)]
        return {"chart": {"result": [{"meta": {"symbol": symbol, "regularMarketTime": stamps[-1] + 3600,
            "regularMarketPrice": 4.988, "chartPreviousClose": 99.0,
            "exchangeTimezoneName": "America/New_York", "currency": "USD"}, "timestamp": stamps,
            "indicators": {"quote": [{"close": [4.8, 4.9, 4.95, 4.98]}]}}], "error": None}}

    def test_yahoo_yield_is_percent_and_previous_is_not_range_start_close(self):
        rows = sources.parse_yahoo(self.chart(), "us_10y", AT)
        self.assertEqual(len(rows), 4)  # 3 completed bars plus actual delayed quote.
        self.assertEqual(rows[-1]["value"], 4.988)
        self.assertEqual(rows[-1]["unit"], "%")
        self.assertEqual(rows[-1]["previous_value"], 4.95)
        self.assertEqual(rows[-1]["cadence"], "intraday")
        self.assertNotEqual(rows[-1]["reported_at"], AT)
        self.assertTrue(rows[-1]["context"]["unofficial"])
        self.assertIn("session start", rows[0]["basis"])

    def test_yahoo_rejects_wrong_symbol_missing_market_timestamp_and_nonfinite_prices(self):
        with self.assertRaises(ValueError):
            sources.parse_yahoo(self.chart("^GSPC"), "us_10y", AT)
        payload = self.chart()
        del payload["chart"]["result"][0]["meta"]["regularMarketTime"]
        with self.assertRaises(ValueError):
            sources.parse_yahoo(payload, "us_10y", AT)
        self.assertIsNone(sources.number(float("nan")))
        self.assertIsNone(sources.number(True))

    def test_yahoo_bootstrap_is_limited_to_90_completed_sessions_plus_quote(self):
        payload = self.chart()
        result = payload["chart"]["result"][0]
        epoch = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp())
        result["timestamp"] = [epoch + 86400 * i for i in range(200)]
        result["indicators"]["quote"][0]["close"] = [4 + i / 100 for i in range(200)]
        result["meta"]["regularMarketTime"] = epoch + 86400 * 200
        self.assertEqual(len(sources.parse_yahoo(payload, "us_10y", AT)), 91)

    def test_futures_are_explicit_and_fred_keeps_daily_date_basis(self):
        rows = sources.parse_yahoo(self.chart("GC=F"), "gold", AT)
        self.assertIn("futures", rows[-1]["context"]["quoted_instrument"])
        self.assertEqual(rows[-1]["unit"], "USD/troy oz")
        fred = sources.parse_fred("observation_date,DGS2\n2026-10-20,4.70\n2026-10-21,\n2026-10-22,4.65\n", AT)
        self.assertEqual([row["value"] for row in fred], [4.70, 4.65])
        self.assertEqual(fred[-1]["reported_at"], "2026-10-22")
        self.assertFalse(fred[-1]["context"]["release_timestamp_available"])

    def test_membership_requires_all_50_distinct_official_isins(self):
        header = "Company Name,Industry,Symbol,Series,ISIN Code\n"
        rows = [f"Company {i},Sector,SYM{i},EQ,INE{i:09d}\n" for i in range(50)]
        parsed = sources.parse_members(header + "".join(rows))
        self.assertEqual(len(parsed), 50)
        self.assertEqual(parsed[0]["instrument_key"], "NSE_EQ|INE000000000")
        self.assertNotIn("weight", parsed[0])
        for value in (header + "".join(rows[:49]), header + "".join(rows[:49] + [rows[0]])):
            with self.assertRaises(ValueError):
                sources.parse_members(value)

    def test_incomplete_candle_coverage_is_not_used_for_indicators(self):
        with self.assertRaises(ValueError):
            sources.parse_candles({"candles": [["2026-10-23T00:00:00+05:30", 1, 2, 1, 2]], "_partial": True})

    def test_successful_empty_provider_responses_still_report_coverage_errors(self):
        client = SimpleNamespace(get_full_market_quotes_v3=lambda keys: {},
            get_historical_candles_v3=lambda *args: {"candles": []},
            get_option_contracts=lambda key: [{"expiry": "2026-10-27", "lot_size": 65}],
            get_option_chain=lambda *args: [], get_fii_data=lambda **kwargs: {"NSE_EQ|CASH": []},
            get_dii_data=lambda **kwargs: {"NSE_EQ|CASH": []})
        with patch.object(sources, "market_day", return_value=datetime(2026, 10, 24).date()):
            result = sources.collect_market_data(client, include_public=False)
        errors = {row["source"] for row in result["source_errors"]}
        self.assertTrue({"Upstox index quotes", "Upstox daily NIFTY candles", "Upstox NIFTY option chain",
            "Upstox fii_cash", "Upstox fii_index_futures", "Upstox fii_index_options", "Upstox dii_cash"}.issubset(errors))

    def test_collection_uses_actual_contract_expiry_and_isolates_source_errors(self):
        class Client:
            def get_full_market_quotes_v3(self, keys):
                raise RuntimeError("Do not expose this provider body")
            def get_historical_candles_v3(self, key, unit, interval, last, first):
                self.range = (last, first)
                return {"candles": [["2026-10-23T00:00:00+05:30", 100, 110, 90, 105, 0, 0]]}
            def get_option_contracts(self, key):
                return [{"expiry": "2026-10-27", "lot_size": 65, "weekly": True},
                        {"expiry": "2026-11-03", "lot_size": 65, "weekly": True}]
            def get_option_chain(self, key, expiry):
                self.expiry = expiry
                return [{"expiry": expiry, "underlying_key": key, "strike_price": 100,
                         "call_options": {"market_data": {"oi": 0}}, "put_options": {"market_data": {"oi": 0}}}]
            def get_fii_data(self, interval, data_types=None):
                return {"NSE_EQ|CASH": [{"time_stamp": 1792713600000, "buy_amount": 100, "sell_amount": 100}]}
            def get_dii_data(self, interval):
                raise ValueError("No dated flow data")
        client = Client()
        with patch.object(sources, "market_day", return_value=datetime(2026, 10, 24).date()):
            result = sources.collect_market_data(client, include_public=False)
        self.assertEqual(client.expiry, "2026-10-27")  # Tuesday, derived from contracts.
        self.assertGreaterEqual((datetime.fromisoformat(client.range[0]) - datetime.fromisoformat(client.range[1])).days, 450)
        self.assertEqual(len(result["candles"]), 1)
        self.assertEqual(result["observations"][0]["value"], 0)
        self.assertIsNone(result["option_chain_meta"]["reported_at"])
        self.assertIsNone(result["option_chain_meta"]["observed_at"])
        self.assertTrue(any(row["source"] == "Upstox index quotes" for row in result["source_errors"]))
        self.assertNotIn("provider body", str(result["source_errors"]))


class StoreIdentityTests(unittest.TestCase):
    def test_recollecting_same_published_snapshot_is_idempotent_but_corrections_are_retained(self):
        row = {"factor_id": "nifty_spot", "source": "Upstox", "value": 25000,
               "reported_at": "2026-10-23T10:00:00+00:00", "observed_at": AT}
        self.assertEqual(content_key(row), content_key({**row, "observed_at": "2026-10-24T19:00:00+00:00"}))
        self.assertNotEqual(content_key(row), content_key({**row, "value": 25001}))
        self.assertNotEqual(content_key(row), content_key({**row, "reported_at": "2026-10-23T10:01:00+00:00"}))

    def test_naive_clock_timestamps_are_rejected_and_daily_date_is_explicit_anchor(self):
        with self.assertRaises(ValueError):
            timestamp("2026-10-24T10:00:00")
        self.assertEqual(timestamp("2026-10-24").isoformat(), "2026-10-24T00:00:00+00:00")
        self.assertIsNone(timestamp(None))


if __name__ == "__main__":
    unittest.main()
