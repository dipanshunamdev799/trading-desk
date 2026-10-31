"""Persistence tests against the configured local TimescaleDB (opt-in).

RUN_MARKET_DB_TESTS=1 enables tests. All fixtures use a unique TEST_CACHE key;
cleanup only removes that test's rows. No Upstox requests are made.
"""
from __future__ import annotations

import os
import sys
import threading
import time
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from sqlalchemy import event, text

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from app.config import get_settings
from app.services.market_gateway import MarketGateway
from app.services.market_store import IST, MarketStore, MemoryCache, canonical_interval, expiry_time, request_key


class CachePolicyTests(unittest.TestCase):
    def test_confirmed_empty_session_calendar_is_not_a_one_minute_price_miss(self):
        at = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)
        self.assertEqual(expiry_time("get_market_timings", {"date": "2026-10-24"}, [], at), at + timedelta(days=1))
        self.assertIsNone(expiry_time("get_market_timings", {"date": "2026-10-23"}, [], at))

    def test_historical_success_is_durable_but_missing_history_is_retried(self):
        at = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)
        self.assertIsNone(expiry_time("get_max_pain", {"date": "2026-10-23"}, {"max_pain": 22700}, at))
        self.assertGreater(expiry_time("get_max_pain", {"date": "2026-10-23"}, {}, at), at)

    def test_live_analytics_expire_at_next_minute_not_sixty_seconds_later(self):
        at = datetime(2026, 10, 26, 4, 0, 48, tzinfo=timezone.utc)
        self.assertEqual(expiry_time("get_max_pain", {"date": "2026-10-26"}, {"max_pain": 22700}, at),
                         datetime(2026, 10, 26, 4, 1, tzinfo=timezone.utc))

    def test_cache_is_bounded_and_does_not_share_mutable_objects(self):
        cache = MemoryCache(max_entries=2)
        cache.put("a", {"rows": [1]}, 60)
        hit, value = cache.get("a")
        self.assertTrue(hit)
        value["rows"].append(2)
        self.assertEqual(cache.get("a")[1], {"rows": [1]})
        cache.put("b", 2, 60)
        cache.put("c", 3, 60)
        self.assertFalse(cache.get("a")[0])


@unittest.skipUnless(os.getenv("RUN_MARKET_DB_TESTS") == "1", "Set RUN_MARKET_DB_TESTS=1 for local TimescaleDB tests")
class MarketDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.key = "TEST_CACHE|" + uuid.uuid4().hex
        self.store = MarketStore(get_settings().database_url_sync)
        self.store.initialize()

    def tearDown(self):
        # Never touch real instrument rows or unrelated request histories.
        with self.store.engine.begin() as conn:
            for table, column in [("candles", "instrument_key"), ("candle_coverage", "instrument_key"),
                                  ("max_pain_points", "instrument_key"), ("option_contracts", "underlying_key")]:
                conn.execute(text(f"DELETE FROM {table} WHERE {column} LIKE :key"), {"key": self.key + "%"})
            for table in ("market_datasets", "market_responses"):
                conn.execute(text(f"DELETE FROM {table} WHERE parameters::text LIKE :key"), {"key": "%" + self.key + "%"})
            for table, column in [("ipo_companies", "id"), ("ipo_research", "ipo_id"), ("ipo_observations", "ipo_id"),
                                  ("ipo_feeds", "name"), ("ipo_sync_state", "source")]:
                conn.execute(text(f"DELETE FROM {table} WHERE {column} LIKE :key"), {"key": self.key + "%"})
        self.store.engine.dispose()

    def params(self):
        return {"instrument_key": self.key, "date": "2026-10-19"}

    @staticmethod
    def bars(day, close=100):
        return {"candles": [[day + "T09:15:00+05:30", close, close + 1, close - 1, close, 10, 20]]}

    def test_memory_then_database_survive_a_new_process_without_api(self):
        calls = []
        def load():
            calls.append(1)
            return {"max_pain": 100}
        self.assertEqual(self.store.read("test_history", self.params(), load), {"max_pain": 100})
        self.store.read("test_history", self.params(), load)
        self.assertEqual(len(calls), 1)
        restarted = MarketStore(get_settings().database_url_sync)
        try:
            result = restarted.read("test_history", self.params(), lambda: self.fail("Retained history must not call upstream"))
            self.assertEqual(result, {"max_pain": 100})
            self.assertEqual(restarted.metrics["db_hits"], 1)
        finally:
            restarted.engine.dispose()

    def test_greeks_archive_uses_exact_ist_day_expiry_and_original_time_after_restart(self):
        expiry = "2026-10-27"
        params = {"instrument_key": self.key, "expiry_date": expiry, "observed_on": "2026-10-23"}
        for stamp, label in [(datetime(2026, 10, 23, 10, tzinfo=IST), "morning"),
                             (datetime(2026, 10, 23, 15, 29, tzinfo=IST), "last session snapshot"),
                             (datetime(2026, 10, 24, 0, 1, tzinfo=IST), "next IST day")]:
            day_params = {**params, "observed_on": stamp.date().isoformat()}
            with patch("app.services.market_store.now", return_value=stamp):
                self.store.read("get_option_chain", day_params, lambda label=label: [{"label": label}], force=True)
        restarted = MarketStore(get_settings().database_url_sync)
        remote = Mock()
        gateway = MarketGateway(remote, restarted)
        try:
            saved = gateway.get_retained_option_chain(self.key, expiry, "2026-10-23")
            self.assertEqual(saved["payload"], [{"label": "last session snapshot"}])
            self.assertEqual(datetime.fromisoformat(saved["observed_at"]).astimezone(IST), datetime(2026, 10, 23, 15, 29, tzinfo=IST))
            self.assertIsNone(gateway.get_retained_option_chain(self.key, expiry, "2026-10-22"))
            self.assertIsNone(gateway.get_retained_option_chain(self.key, "2026-10-28", "2026-10-23"))
            remote.get_option_chain.assert_not_called()
            remote.get_option_greeks_v3.assert_not_called()
        finally:
            restarted.engine.dispose()

    def test_new_store_does_not_repeat_hypertable_ddl_during_active_reads(self):
        restarted = MarketStore(get_settings().database_url_sync)
        statements = []
        def capture(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)
        event.listen(restarted.engine, "before_cursor_execute", capture)
        try:
            restarted.initialize()
            self.assertFalse(any("create_hypertable" in statement for statement in statements))
            self.assertTrue(restarted.initialized)
        finally:
            restarted.engine.dispose()

    def test_ipo_details_and_unknown_provider_fields_survive_cache_and_restart(self):
        from unittest.mock import Mock
        from app.services.ipo_store import IpoStore
        remote = Mock()
        remote.get_ipo_details.return_value = {"id": self.key, "name": "TEST IPO " + self.key,
            "status": "open", "bidding_start_date": "2026-10-23", "total_subscription": "0.08",
            "provider_future_field": {"raw": [1, 2, 3]}}
        client = MarketGateway(remote, self.store, 100000)
        expected = client.get_ipo_details(self.key)
        self.assertEqual(client.get_ipo_details(self.key), expected)
        remote.get_ipo_details.assert_called_once()
        restarted = MarketStore(get_settings().database_url_sync)
        try:
            self.assertEqual(MarketGateway(object(), restarted).get_ipo_details(self.key), expected)
            company = next(row for row in IpoStore(restarted).companies() if row["id"] == self.key)
            self.assertEqual(company["provider_future_field"], {"raw": [1, 2, 3]})
            points = IpoStore(restarted).observations(self.key)
            self.assertEqual(len(points), 1)
            self.assertEqual(points[0]["value"], 0.08)
        finally:
            restarted.engine.dispose()

    def test_public_ipo_research_is_committed_before_return_and_reused_without_http(self):
        from unittest.mock import Mock
        from app.services.ipo_service import IpoService
        from app.services.ipo_store import IpoStore
        company = {"id": self.key, "name": "Example Polymers IPO"}
        html = '<h1>Example Polymers IPO GMP Today</h1><table><tr><th>GMP Date</th><th>GMP</th></tr><tr><td>24-Oct 17:00</td><td>₹10</td></tr></table>'
        service = IpoService(MarketGateway(object(), self.store))
        with patch("app.services.ipo_sources.fetch_html", return_value=html) as fetch:
            service._public("gmp", "https://www.investorgain.com/gmp/example/1/", company)
        fetch.assert_called_once()
        self.assertEqual(IpoStore(self.store).research(self.key)["gmp"]["data"]["gmp"], 10)
        self.assertEqual(len(IpoStore(self.store).observations(self.key)), 1)
        restarted = MarketStore(get_settings().database_url_sync)
        try:
            with patch("app.services.ipo_sources.fetch_html", side_effect=AssertionError("Must use retained source")) as fetch:
                IpoService(MarketGateway(object(), restarted))._public("gmp", "https://www.investorgain.com/gmp/example/1/", company)
                fetch.assert_not_called()
        finally:
            restarted.engine.dispose()

    def test_concurrent_workers_share_one_upstream_fill(self):
        other = MarketStore(get_settings().database_url_sync)
        calls = []
        guard = threading.Lock()
        def load():
            with guard:
                calls.append(1)
            time.sleep(0.05)
            return {"max_pain": 100}
        try:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda i: (self.store if i % 2 else other).read("test_history", self.params(), load), range(8)))
            self.assertEqual(len(calls), 1)
            self.assertTrue(all(result["max_pain"] == 100 for result in results))
        finally:
            other.engine.dispose()

    def test_database_failure_does_not_populate_memory_or_return_unpersisted_data(self):
        with patch.object(self.store, "_archive", side_effect=RuntimeError("simulated DB failure")):
            with self.assertRaises(RuntimeError):
                self.store.read("test_history", self.params(), lambda: {"max_pain": 100})
        key = request_key("test_history", self.params())
        self.assertFalse(self.store.cache.get(key)[0])
        with self.store.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT count(*) FROM market_datasets WHERE request_key=:key"), {"key": key}).scalar(), 0)

    def test_failed_fetch_is_not_recorded_as_successful_empty_coverage(self):
        with self.assertRaises(RuntimeError):
            self.store.read("test_history", self.params(), lambda: (_ for _ in ()).throw(RuntimeError("upstream failure")))
        self.assertEqual(self.store.read("test_history", self.params(), lambda: {"max_pain": 101}), {"max_pain": 101})

    def test_internal_candle_gap_fetches_only_missing_day(self):
        calls = []
        def load(lo, hi):
            calls.append((lo, hi))
            return self.bars(lo)
        for day in ("2026-10-19", "2026-10-21"):
            self.store.candles(self.key, "minutes", 1, day, day, load)
        result = self.store.candles(self.key, "minutes", 1, "2026-10-19", "2026-10-21", load)
        self.assertEqual(calls[-1], ("2026-10-20", "2026-10-20"))
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(result["candles"]), 3)
        restarted = MarketStore(get_settings().database_url_sync)
        try:
            result = restarted.candles(self.key, "minutes", 1, "2026-10-19", "2026-10-21", lambda *args: self.fail("Unexpected API call"))
            self.assertEqual(len(result["candles"]), 3)
            self.assertEqual(result["_source"], "db")
        finally:
            restarted.engine.dispose()

    def test_overlapping_ranges_reuse_covered_days_and_keep_ist_midnight(self):
        calls = []
        def load(lo, hi):
            calls.append((lo, hi))
            return {"candles": [[lo + "T00:00:00+05:30", 100, 101, 99, 100, 10, 20]]}
        self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", load)
        result = self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-20", load)
        self.assertEqual(calls, [("2026-10-19", "2026-10-19"), ("2026-10-20", "2026-10-20")])
        self.assertEqual(len(result["candles"]), 2)
        self.assertEqual(result["candles"][0][0], "2026-10-19T00:00:00+05:30")
        self.assertEqual(canonical_interval("days", 1), "1day")

    def test_existing_daily_data_does_not_depend_on_new_coverage_or_upstream(self):
        with self.store.engine.begin() as conn:
            self.store._upsert_bars(conn, self.key, "1day", self.bars("2026-10-19")["candles"])
        result = self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda *args: self.fail("Existing daily bars must not be refetched"))
        self.assertEqual(len(result["candles"]), 1)
        self.assertEqual(result["_source"], "db")

    def test_legacy_intraday_history_survives_upstream_outage_with_partial_label(self):
        with self.store.engine.begin() as conn:
            self.store._upsert_bars(conn, self.key, "1minute", self.bars("2026-10-19")["candles"])
        result = self.store.candles(self.key, "minutes", 1, "2026-10-19", "2026-10-19",
            lambda *args: (_ for _ in ()).throw(RuntimeError("upstream no longer serves this period")))
        self.assertEqual(len(result["candles"]), 1)
        self.assertTrue(result["_partial"])
        self.assertEqual(result["_source"], "db_partial")
        cached = self.store.candles(self.key, "minutes", 1, "2026-10-19", "2026-10-19", lambda *args: self.fail("Should use cache"))
        self.assertTrue(cached["_partial"])
        self.assertEqual(cached["_source"], "db_partial")

    def test_successful_window_is_committed_even_when_later_window_fails(self):
        calls = []
        def load(lo, hi):
            calls.append((lo, hi))
            if len(calls) == 2:
                raise RuntimeError("later chunk failed")
            return self.bars(lo)
        with self.assertRaises(RuntimeError):
            self.store.candles(self.key, "minutes", 1, "2026-08-01", "2026-09-10", load)
        with self.store.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT count(*) FROM candles WHERE instrument_key=:key"), {"key": self.key}).scalar(), 1)
            self.assertEqual(conn.execute(text("SELECT count(*) FROM candle_coverage WHERE instrument_key=:key"), {"key": self.key}).scalar(), 28)

    def test_wrong_date_response_is_not_stored_as_selected_day(self):
        result = self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda *args: self.bars("2026-10-16"))
        self.assertEqual(result["candles"], [])
        with self.store.engine.connect() as conn:
            coverage = conn.execute(text("SELECT row_count,valid_until FROM candle_coverage WHERE instrument_key=:key"), {"key": self.key}).one()
            self.assertEqual(coverage[0], 0)
            self.assertIsNotNone(coverage[1])

    def test_missing_history_is_negative_cached_then_retried(self):
        calls = []
        def missing(*args):
            calls.append(1)
            return {"candles": []}
        self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", missing)
        self.store.cache.clear()
        self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", missing)
        self.assertEqual(len(calls), 1)
        with self.store.engine.begin() as conn:
            conn.execute(text("UPDATE candle_coverage SET valid_until=now()-interval '1 second' WHERE instrument_key=:key"), {"key": self.key})
        self.store.cache.clear()
        result = self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda lo, hi: self.bars(lo))
        self.assertEqual(len(result["candles"]), 1)

    def test_force_refresh_updates_stored_price_and_invalidates_memory(self):
        self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda lo, hi: self.bars(lo, 100))
        self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda lo, hi: self.bars(lo, 110), force=True)
        result = self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda *args: self.fail("Unexpected API call"))
        self.assertEqual(result["candles"][0][4], 110)

    def test_live_candle_coverage_expires_at_next_minute(self):
        at = datetime(2026, 10, 26, 9, 15, 48, tzinfo=IST)
        with patch("app.services.market_store.now", return_value=at):
            self.store.candles(self.key, "minutes", 1, "2026-10-26", "2026-10-26", lambda lo, hi: self.bars(lo))
        with self.store.engine.connect() as conn:
            until = conn.execute(text("SELECT valid_until FROM candle_coverage WHERE instrument_key=:key"), {"key": self.key}).scalar()
        self.assertEqual(until, datetime(2026, 10, 26, 9, 16, tzinfo=IST))

    def test_current_day_minute_request_uses_intraday_not_empty_history(self):
        class Remote:
            def get_historical_candles_v3(remote, *args):
                self.fail("Current-day minute bars must use intraday")
            def get_intraday_candles_v3(remote, *args):
                return self.bars("2026-10-26")
        at = datetime(2026, 10, 26, 10, 0, tzinfo=IST)
        with patch("app.services.market_store.now", return_value=at):
            result = MarketGateway(Remote(), self.store, 100000).get_historical_candles_v3(
                self.key, "minutes", 1, "2026-10-26", "2026-10-26")
        self.assertEqual(len(result["candles"]), 1)

    def test_current_week_is_not_frozen_as_completed_historical_data(self):
        at = datetime(2026, 10, 29, 10, 0, tzinfo=IST)
        with patch("app.services.market_store.now", return_value=at):
            self.store.candles(self.key, "weeks", 1, "2026-10-26", "2026-10-29", lambda *args: self.bars("2026-10-26"))
        with self.store.engine.connect() as conn:
            until = conn.execute(text("SELECT valid_until FROM candle_coverage WHERE instrument_key=:key AND day='2026-10-26'"), {"key": self.key}).scalar()
        self.assertIsNotNone(until)
        self.assertEqual(until, at.replace(minute=1))

    def test_retained_expired_contracts_are_available_without_upstream(self):
        underlying = self.key
        class Remote:
            def get_expired_option_contracts(remote, key, expiry):
                return [{"underlying_key": key, "expiry": expiry, "strike_price": 100, "instrument_type": "CE",
                         "instrument_key": underlying + "|100CE", "lot_size": 65}]
        gateway = MarketGateway(Remote(), self.store, 100000)
        first = gateway.get_option_contracts(self.key, "2026-10-20")
        self.store.cache.clear()
        self.assertEqual(MarketGateway(object(), self.store).get_option_contracts(self.key, "2026-10-20"), first)

    def test_expired_contract_reuses_candles_saved_while_it_was_active(self):
        self.store.candles(self.key, "days", 1, "2026-10-19", "2026-10-19", lambda lo, hi: self.bars(lo))
        gateway = MarketGateway(object(), self.store)
        result = gateway.get_expired_historical_candles(self.key + "|20-10-2026", "day", "2026-10-19", "2026-10-19")
        self.assertEqual(len(result["candles"]), 1)
        self.assertEqual(gateway.store.metrics.get("upstream_calls", 0), 0)

    def test_quote_snapshots_use_cache_and_are_archived_in_timescale(self):
        class Remote:
            calls = 0
            def get_ltp_quotes_v3(remote, instrument_keys):
                remote.calls += 1
                return {instrument_keys[0]: {"last_price": 100}}
        remote = Remote()
        gateway = MarketGateway(remote, self.store, 100000)
        gateway.get_ltp_quotes_v3([self.key])
        gateway.get_ltp_quotes_v3([self.key])
        self.assertEqual(remote.calls, 1)
        with self.store.engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT count(*) FROM market_responses WHERE parameters::text LIKE :key"), {"key": "%" + self.key + "%"}).scalar(), 1)
            tables = list(conn.execute(text("SELECT hypertable_name FROM timescaledb_information.hypertables WHERE hypertable_schema='public'")).scalars())
        self.assertTrue({"candles", "market_responses", "max_pain_points"}.issubset(tables))

    def test_carry_forward_checks_newer_gaps_and_replays_from_db_without_synthetic_bars(self):
        self.store.candles(self.key, "days", 1, "2026-10-14", "2026-10-14", lambda *args: self.bars("2026-10-14", 99.05))
        calls = []
        class Remote:
            def get_historical_candles_v3(remote, key, unit, interval, hi, lo):
                calls.append((lo, hi))
                return self.bars("2026-10-22", 67.05)
        gateway = MarketGateway(Remote(), self.store, 100000)
        price = gateway.get_previous_option_close(self.key, "2026-10-23")
        self.assertEqual(price, {"close": 67.05, "price_date": "2026-10-22"})
        self.assertEqual(calls, [("2026-10-15", "2026-10-22")])
        restarted = MarketStore(get_settings().database_url_sync)
        try:
            self.assertEqual(MarketGateway(object(), restarted).get_previous_option_close(self.key, "2026-10-23"), price)
            self.assertEqual(restarted.metrics.get("upstream_calls", 0), 0)
            with restarted.engine.connect() as conn:
                days = list(conn.execute(text("SELECT (ts AT TIME ZONE 'Asia/Kolkata')::date FROM candles WHERE instrument_key=:key ORDER BY ts"), {"key": self.key}).scalars())
            self.assertEqual([day.isoformat() for day in days], ["2026-10-14", "2026-10-22"])
        finally:
            restarted.engine.dispose()

    def test_carry_forward_backfills_older_trade_with_expired_contract_identity(self):
        calls = []
        class Remote:
            def get_expired_historical_candles(remote, key, interval, hi, lo):
                calls.append((key, lo, hi))
                return {"candles": []} if lo > "2026-10-09" else self.bars("2026-10-09", 99.05)
        expired = self.key + "|20-10-2026"
        price = MarketGateway(Remote(), self.store, 100000).get_previous_option_close(expired, "2026-10-19")
        self.assertEqual(price, {"close": 99.05, "price_date": "2026-10-09"})
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(key == expired for key, lo, hi in calls))
        self.assertTrue(all(hi < "2026-10-19" for key, lo, hi in calls))

    def test_no_prior_trade_remains_missing_and_empty_backfill_is_reused(self):
        calls = []
        class Remote:
            def get_historical_candles_v3(remote, key, unit, interval, hi, lo):
                calls.append((lo, hi))
                return {"candles": []}
        gateway = MarketGateway(Remote(), self.store, 100000)
        self.assertIsNone(gateway.get_previous_option_close(self.key, "2026-10-23"))
        self.assertEqual(len(calls), 4)
        self.assertEqual(min(lo for lo, hi in calls), "2025-10-23")
        self.assertTrue(all(hi < "2026-10-23" for lo, hi in calls))
        self.store.cache.clear()
        self.assertIsNone(MarketGateway(object(), self.store).get_previous_option_close(self.key, "2026-10-23"))

    def test_known_expiries_include_retained_evidence_and_exclude_empty_probes(self):
        self.store.read("get_max_pain", {"instrument_key": self.key, "expiry": "2026-10-20", "date": "2026-10-19"},
                        lambda: {"max_pain": 700})
        self.store.read("get_oi_data", {"instrument_key": self.key, "expiry": "2026-10-13", "date": "2026-10-12"}, lambda: {})
        with self.store.engine.begin() as conn:
            self.store.save_contracts(conn, self.key, [{"expiry": "2026-10-27", "strike_price": 700,
                "instrument_type": "CE", "instrument_key": self.key + "FO", "lot_size": 650}], datetime.now(timezone.utc))
        self.assertEqual(MarketGateway(object(), self.store).get_known_expiries(self.key), [
            {"expiry": "2026-10-20", "available": True}, {"expiry": "2026-10-27", "available": False}])

    def test_old_retained_price_is_not_used_when_newer_coverage_fetch_fails(self):
        self.store.candles(self.key, "days", 1, "2026-10-14", "2026-10-14", lambda *args: self.bars("2026-10-14"))
        class Remote:
            def get_historical_candles_v3(remote, *args):
                raise RuntimeError("Cannot verify newer trades")
        with self.assertRaises(RuntimeError):
            MarketGateway(Remote(), self.store, 100000).get_previous_option_close(self.key, "2026-10-23")


if __name__ == "__main__":
    unittest.main()
