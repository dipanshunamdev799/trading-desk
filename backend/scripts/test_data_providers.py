"""Provider ordering, schema and provenance tests; no network or database calls."""
from __future__ import annotations

import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from tapetide_data import TapetideAPIError, TapetideClient
from upstox_analytics import UpstoxAPIError
from app.services.data_providers import TapetideFallback, upstream_unavailable
from app.services.market_gateway import MarketGateway
from app.services.market_store import expiry_time

KEY = "NSE_EQ|INE002A01018"
OTHER = "NSE_EQ|INE467B01029"
DAY = "2026-10-23"
AT = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)


class Store:
    def __init__(self):
        self.reads = []
        self.secondary = {}

    def count(self, name):
        pass

    def read(self, method, params, load, **kwargs):
        self.reads.append((method, params))
        key = repr((method, params))
        if method.startswith("tapetide.") and key in self.secondary:
            return copy.deepcopy(self.secondary[key])
        result = load()
        if method.startswith("tapetide."):
            self.secondary[key] = copy.deepcopy(result)
        return result

    def candles(self, key, unit, interval, first, last, load, **kwargs):
        return load(first, last)


class Remote:
    def __init__(self, payload=None, error=None):
        self.payload, self.error, self.calls = payload, error, 0

    def result(self):
        self.calls += 1
        if self.error:
            raise self.error
        return copy.deepcopy(self.payload)

    def get_ltp_quotes_v3(self, instrument_keys):
        return self.result()

    def get_historical_candles_v3(self, instrument_key, unit, interval, to_date, from_date=None):
        return self.result()

    def get_balance_sheet(self, isin, statement_type="consolidated", full_statement=True):
        return self.result()


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.client = Mock(spec=TapetideClient)
        self.client.BASE_URL = TapetideClient.BASE_URL
        self.fallback = TapetideFallback(self.client, self.store)
        self.clock = patch("app.services.data_providers.now", return_value=AT)
        self.day = patch("app.services.data_providers.market_day", return_value=AT.date())
        self.clock.start()
        self.day.start()
        self.addCleanup(self.clock.stop)
        self.addCleanup(self.day.stop)

    def gateway(self, remote, fallback=True):
        return MarketGateway(remote, self.store, 100000, fallback=self.fallback if fallback else None)

    def fake_native(self, endpoint, **params):
        if endpoint == "search_stocks":
            data = [{"nse_symbol": "RELIANCE"}]
        elif endpoint == "get_stock_profile":
            data = {"company": {"isin": "INE002A01018"}}
        elif endpoint == "get_stock_quote":
            data = {"symbol": "RELIANCE", "price": 100, "updated_at": DAY + "T10:00:00+00:00"}
        else:
            data = []
        return {"data": data, "_provider": "tapetide", "_provenance": {"endpoint": endpoint}}

    def test_primary_quote_does_not_contact_secondary(self):
        primary = {KEY: {"last_price": 0, "instrument_token": KEY}}
        self.assertEqual(self.gateway(Remote(primary)).get_ltp_quotes_v3([KEY]), primary)
        self.client.call.assert_not_called()

    def test_only_missing_quotes_are_filled_and_invalid_alias_is_replaced(self):
        primary = {OTHER: {"last_price": 99}, KEY: {"last_price": None}}
        with patch.object(self.fallback, "native", side_effect=self.fake_native):
            result = self.gateway(Remote(primary)).get_ltp_quotes_v3([OTHER, KEY])
        self.assertEqual(result[OTHER], primary[OTHER])
        self.assertNotIn(KEY, result)
        self.assertEqual(result[KEY.replace("|", ":")]["_provider"], "tapetide")
        self.assertEqual(result[KEY.replace("|", ":")]["timestamp"], DAY + "T10:00:00+00:00")

    def test_upstream_outage_uses_fallback_but_recovery_always_checks_primary(self):
        remote = Remote(error=UpstoxAPIError(503, "unavailable"))
        gateway = self.gateway(remote)
        with patch.object(self.fallback, "native", side_effect=self.fake_native):
            first = gateway.get_ltp_quotes_v3([KEY])
        self.assertEqual(first[KEY.replace("|", ":")]["_provider"], "tapetide")
        remote.error, remote.payload = None, {KEY: {"last_price": 101}}
        self.assertEqual(gateway.get_ltp_quotes_v3([KEY]), remote.payload)
        self.assertEqual(remote.calls, 2)

    def test_missing_upstox_token_can_use_fallback(self):
        error = RuntimeError("UPSTOX_ANALYTICS_TOKEN is required for an API cache miss; retained database data remains readable.")
        with patch.object(self.fallback, "native", side_effect=self.fake_native):
            self.assertTrue(self.gateway(Remote(error=error)).get_ltp_quotes_v3([KEY]))

    def test_database_failure_is_not_hidden_by_failover(self):
        with patch.object(self.store, "read", side_effect=RuntimeError("database write failed")):
            with self.assertRaisesRegex(RuntimeError, "database write failed"):
                self.gateway(Remote()).get_ltp_quotes_v3([KEY])
        self.client.call.assert_not_called()

    def test_bad_input_and_disabled_fallback_preserve_original_error(self):
        for error, enabled in [(UpstoxAPIError(400, "bad instrument"), True), (UpstoxAPIError(503, "unavailable"), False)]:
            with self.assertRaises(UpstoxAPIError) as caught:
                self.gateway(Remote(error=error), enabled).get_ltp_quotes_v3([KEY])
            self.assertIs(caught.exception, error)
        self.client.call.assert_not_called()

    def test_secondary_quota_error_preserves_upstox_error(self):
        error = UpstoxAPIError(503, "unavailable")
        self.client.call.side_effect = TapetideAPIError(429)
        with self.assertRaises(UpstoxAPIError) as caught:
            self.gateway(Remote(error=error)).get_ltp_quotes_v3([KEY])
        self.assertIs(caught.exception, error)

    def test_secondary_namespace_is_separate_and_reused(self):
        self.client.call.return_value = {"data": {"value": 3}, "meta": {"as_of": "original"}}
        a = self.fallback.native("get_forecasts", symbol="RELIANCE")
        b = self.fallback.native("get_forecasts", symbol="RELIANCE")
        self.client.call.assert_called_once()
        self.assertEqual(a, b)
        self.assertTrue(all(method.startswith("tapetide.") for method, _ in self.store.reads))
        self.assertEqual(a["meta"]["as_of"], "original")

    def test_secondary_history_never_gets_immutable_upstox_expiry_policy(self):
        deadline = expiry_time("tapetide.get_option_chain", {"date": DAY}, {"data": [1]}, AT)
        self.assertEqual(deadline, AT + timedelta(seconds=300))

    def test_ambiguous_or_mismatched_equity_identity_is_rejected(self):
        with patch.object(self.fallback, "native", return_value={"data": [{"nse_symbol": "WRONG"}, {"nse_symbol": "OTHER"}]}):
            with self.assertRaises(ValueError):
                self.fallback.symbol(KEY)
        with patch.object(self.fallback, "native", side_effect=[{"data": [{"nse_symbol": "WRONG"}]}, {"data": {"company": {"isin": "DIFFERENT"}}}]):
            with self.assertRaises(ValueError):
                self.fallback.symbol(KEY)

    def test_daily_fallback_converts_adjusted_prices_to_raw_and_keeps_primary(self):
        raw = {"data": [{"date": DAY, "open": 49, "high": 51, "low": 48, "close": 50, "raw_close": 100, "volume": 8}], "_provenance": {}}
        with patch.object(self.fallback, "symbol", return_value="RELIANCE"), patch.object(self.fallback, "native", return_value=raw):
            result = self.fallback.candles(KEY, "days", 1, DAY, DAY)
            self.assertEqual(result["candles"][0][1:], [98, 102, 96, 100, 8, None])
            primary = {"candles": [[DAY + "T00:00:00+05:30", 1, 2, 0, 1, 3, None]], "_partial": True}
            merged = self.fallback.candles(KEY, "days", 1, DAY, DAY, primary)
        self.assertEqual(merged["candles"], primary["candles"])
        self.assertTrue(merged["_partial"])

    def test_missing_raw_close_does_not_splice_adjusted_candle_into_raw_history(self):
        raw = {"data": [{"date": DAY, "open": 49, "high": 51, "low": 48, "close": 50, "raw_close": None}], "_provenance": {}}
        with patch.object(self.fallback, "symbol", return_value="RELIANCE"), patch.object(self.fallback, "native", return_value=raw):
            self.assertIsNone(self.fallback.candles(KEY, "days", 1, DAY, DAY))

    def test_index_fallback_uses_daily_paged_endpoint_for_long_windows(self):
        def native(endpoint, **params):
            if endpoint == "list_indices":
                return {"data": [{"name": "Nifty 50", "exchange": "NSE", "slug": "nifty-50"}]}
            return {"data": [{"date": DAY, "open": 1, "high": 2, "low": 0, "close": 1}],
                    "meta": {"has_more": False}, "_provenance": {"endpoint": endpoint}}
        with patch.object(self.fallback, "native", side_effect=native) as read:
            result = self.fallback.candles("NSE_INDEX|Nifty 50", "days", 1, "2025-01-01", DAY)
        self.assertEqual(result["candles"][0][4], 1)
        self.assertEqual(read.call_args.args[0], "list_index_levels")
        self.assertEqual(read.call_args.kwargs["order"], "asc")

    def test_quote_dataset_reports_actual_mixed_provider(self):
        remote = Remote({OTHER: {"last_price": 99}})
        with patch.object(self.fallback, "native", side_effect=self.fake_native):
            result = self.gateway(remote).get_dataset("get_ltp_quotes_v3", instrument_keys=[OTHER, KEY])
        self.assertEqual(result["provider"], "mixed")

    def test_normalizers_keep_secondary_provenance_and_verified_cash_units(self):
        from app.services.nifty_sources import parse_flows, parse_quotes
        quote = {KEY: {"last_price": 100, "timestamp": DAY + "T10:00:00+00:00", "_provider": "tapetide", "_provenance": {"source_url": "https://api.tapetide.com/v1/stocks/RELIANCE/quote"}}}
        self.assertEqual(parse_quotes(quote, {"example": KEY}, AT.isoformat())[0]["source"], "Tapetide")
        flows = {"NSE_EQ|CASH": [{"time_stamp": 1792693800000, "buy_amount": 10_000,
                  "sell_amount": 9_000, "_provider": "tapetide", "_provenance": {}}]}
        observation = parse_flows(flows, "fii_cash", AT.isoformat())[0]
        self.assertEqual(observation["source"], "Tapetide")
        self.assertEqual(observation["context"]["unit_status"], "documented")

    def test_intraday_and_current_day_are_not_filled_with_eod_data(self):
        self.assertIsNone(self.fallback.candles(KEY, "minutes", 1, DAY, DAY))
        self.assertIsNone(self.fallback.candles(KEY, "days", 1, AT.date().isoformat(), AT.date().isoformat()))
        self.client.call.assert_not_called()

    def test_daily_gateway_outage_returns_fallback_without_primary_candle_writes(self):
        remote = Remote(error=UpstoxAPIError(503, "unavailable"))
        secondary = {"candles": [[DAY + "T00:00:00+05:30", 1, 2, 0, 1, 3, None]], "_provider": "tapetide"}
        with patch.object(self.fallback, "candles", return_value=secondary):
            result = self.gateway(remote).get_historical_candles_v3(KEY, "days", 1, DAY, DAY)
        self.assertEqual(result, secondary)
        self.assertFalse(self.store.reads)

    def test_cash_flows_convert_explicit_crore_to_documented_rupees(self):
        raw = {"data": [{"date": DAY, "fii_buy_cr": 10, "fii_sell_cr": 9}], "_provenance": {}}
        with patch.object(self.fallback, "native", return_value=raw):
            result = self.fallback.flows("get_fii_data", {"from_date": DAY})
        self.assertEqual(result["NSE_EQ|CASH"][0]["buy_amount"], 100_000_000)
        self.assertEqual(result["NSE_EQ|CASH"][0]["_provider"], "tapetide")

    def test_option_fallback_requires_exact_session_and_expiry_and_never_fakes_intraday(self):
        raw = {"data": {"snapshot_ts": DAY + " 10:00:00+00", "expiry_date": "2026-10-27", "pcr": .7, "spot": 22600}, "_provenance": {}}
        params = {"instrument_key": "NSE_INDEX|Nifty 50", "expiry": "2026-10-27", "date": DAY}
        with patch.object(self.fallback, "native", return_value=raw):
            result = self.fallback.options("get_pcr", params)
            self.assertEqual(result["pcr"], .7)
            self.assertEqual(result["insights"], [])
            self.assertIsNone(self.fallback.options("get_pcr", {**params, "date": "2026-10-22"}))
            self.assertIsNone(self.fallback.options("get_pcr", {**params, "expiry": "current_week"}))
            self.assertIsNone(self.fallback.options("get_oi_data", params))

    def test_native_fundamental_schema_uses_envelope_only_after_primary_miss(self):
        remote = Remote({"value": 1})
        gateway = self.gateway(remote)
        self.assertEqual(gateway.get_dataset("get_balance_sheet", isin="INE002A01018")["provider"], "upstox")
        self.client.call.assert_not_called()
        remote.payload = {}
        with patch.object(self.fallback, "dataset", return_value={"data": {"balance_sheet": [1]}, "_provider": "tapetide"}):
            result = gateway.get_dataset("get_balance_sheet", isin="INE002A01018")
        self.assertEqual(result["provider"], "tapetide")
        self.assertEqual(result["schema"], "tapetide")

    def test_new_datasets_are_accessible_and_overlapping_aliases_cannot_bypass_primary(self):
        gateway = self.gateway(Remote())
        self.client.call.return_value = {"data": [1]}
        self.assertEqual(gateway.get_dataset("get_forecasts", symbol="RELIANCE")["provider"], "tapetide")
        with self.assertRaisesRegex(ValueError, "primary source"):
            gateway.get_dataset("get_stock_profile", symbol="RELIANCE")


class TransportTests(unittest.TestCase):
    def test_unknown_or_write_endpoint_is_rejected_before_http(self):
        client = TapetideClient("test")
        for endpoint in ("add_portfolio_stocks", "https://example.com/", "remove_from_watchlist"):
            with self.assertRaises(ValueError):
                client.call(endpoint)

    def test_transport_error_does_not_expose_response_body_or_token(self):
        client = TapetideClient("private-token")
        session = Mock()
        session.get.return_value.status_code = 401
        session.get.return_value.text = "private-token"
        client._local.session = session
        with self.assertRaises(TapetideAPIError) as caught:
            client.call("get_stock_quote", symbol="RELIANCE")
        self.assertNotIn("private-token", str(caught.exception))
        self.assertFalse(session.get.call_args.kwargs["allow_redirects"])

    def test_invalid_body_and_missing_required_parameters_fail_cleanly(self):
        client = TapetideClient("private-token", requests_per_second=100000)
        with self.assertRaises(ValueError):
            client.call("get_stock_quote")
        with self.assertRaisesRegex(ValueError, "documented range"):
            client.call("list_indices", limit=500)
        session = Mock()
        session.get.return_value.status_code = 200
        session.get.return_value.json.return_value = {"error": "missing"}
        client._local.session = session
        with self.assertRaises(TapetideAPIError):
            client.call("get_stock_quote", symbol="RELIANCE")


if __name__ == "__main__":
    unittest.main()
