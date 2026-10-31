"""Session switching, V3 wire format, durability, stale fields and date isolation."""
import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from sqlalchemy import text
from app.services.market_session import session_context
from app.services.market_stream import MarketStream
from app.services.market_stream_store import MarketStreamStore
from app.services.market_store import IST, MarketStore
from app.services import maxpain_greeks
from upstox_ws_v3 import FeedResponseProto, UpstoxMarketDataWSV3

KEY, LEG, EXPIRY = "NSE_INDEX|Nifty 50", "NSE_FO|fixture", "2026-10-27"
AT = datetime(2026, 10, 26, 10, 0, tzinfo=IST)

def chain(key=KEY):
    return [{"underlying_key": key, "expiry": EXPIRY, "strike_price": 22600,
        "call_options": {"instrument_key": LEG, "market_data": {"oi": 100, "ltp": 20},
                         "option_greeks": {"delta": .5, "gamma": .01, "theta": -2, "vega": 3, "iv": 15}},
        "put_options": {"instrument_key": "NSE_FO|put", "market_data": {"oi": 50, "ltp": 25},
                        "option_greeks": {"delta": -.5, "gamma": .01, "theta": -2, "vega": 3, "iv": 16}}}]

def frame(at=AT, values=None):
    return {"type": "live_feed", "currentTs": str(int(at.timestamp() * 1000)), "feeds": {
        LEG: {"fullFeed": {"marketFF": values or {"ltpc": {"ltp": 21, "cp": 20, "ltt": int(at.timestamp()*1000)},
             "optionGreeks": {"delta": .6, "gamma": 0, "theta": -2.2, "vega": 4}, "oi": 0, "iv": .1334}}}}}

class SessionTests(unittest.TestCase):
    def context(self, at=AT, status="NORMAL_OPEN", timings=True, updated=AT):
        rows = [{"exchange": "NSE", "start_time": int(at.replace(hour=9, minute=15).timestamp()*1000),
                 "end_time": int(at.replace(hour=15, minute=30).timestamp()*1000)}] if timings else []
        return session_context(KEY, {"status": status, "last_updated": int(updated.timestamp()*1000)}, rows,
            {KEY: {"timestamp": at.isoformat(), "last_trade_time": "2026-10-23T15:30:00+05:30"}}, at)

    def test_active_requires_current_exchange_status_and_calendar(self):
        self.assertTrue(self.context()["active"])
        self.assertFalse(self.context(timings=False)["active"])
        self.assertFalse(self.context(status="NORMAL_CLOSE")["active"])
        self.assertFalse(self.context(updated=AT-timedelta(days=3))["active"])

    def test_closed_weekend_keeps_last_trade_date_not_receipt_date(self):
        result = self.context(at=AT-timedelta(days=1), status="CLOSING_END", timings=False)
        self.assertEqual(result["session_date"], "2026-10-23")
        self.assertEqual(result["phase"], "closed")

    def test_special_weekend_session_can_stream(self):
        sunday = AT-timedelta(days=1)
        self.assertTrue(self.context(at=sunday, updated=sunday)["active"])

    def test_unknown_status_does_not_claim_live(self):
        result = session_context(KEY, None, None, {}, AT)
        self.assertFalse(result["active"])
        self.assertEqual(result["phase"], "unknown")

class StreamTests(unittest.TestCase):
    def setUp(self):
        self.clock = patch("app.services.market_stream.now", return_value=AT)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        self.gateway = SimpleNamespace(store=Mock())
        self.stream = MarketStream(self.gateway, SimpleNamespace(market_stream_enabled=True,
            market_stream_max_instruments=1500, market_stream_stale_seconds=30))
        self.stream.repo = Mock()
        self.stream._on_connect(None)
        self.stream.active_keys = {KEY, LEG}
        self.stream.seed_chain(KEY, EXPIRY, chain(), {"transport": "rest", "observed_at": AT.isoformat()})

    def test_official_protobuf_full_feed_and_real_zeros(self):
        p = FeedResponseProto()
        p.currentTs = int(AT.timestamp()*1000)
        m = p.feeds[LEG].fullFeed.marketFF
        m.ltpc.ltp = 21
        m.optionGreeks.delta = .6
        m.iv = .1334
        result = UpstoxMarketDataWSV3.decode_protobuf(p.SerializeToString())
        self.assertEqual(result["type"], "initial_feed")
        values = result["feeds"][LEG]["fullFeed"]["marketFF"]
        self.assertEqual(values["optionGreeks"]["gamma"], 0)
        self.assertEqual(values["oi"], 0)
        self.assertNotIn("marketOHLC", values)

    def test_iv_units_zero_oi_signed_theta_and_baseline_are_preserved(self):
        self.stream._apply(frame(), AT)
        rows, meta = self.stream.chain(KEY, EXPIRY)
        call = rows[0]["call_options"]
        self.assertAlmostEqual(call["option_greeks"]["iv"], 13.34)
        self.assertEqual(call["option_greeks"]["theta"], -2.2)
        self.assertEqual(call["market_data"]["oi"], 0)
        self.assertEqual(meta["live_legs"], 1)
        self.assertEqual(rows[0]["put_options"]["_provenance"]["greeks_source"], "rest")
        self.assertEqual(self.stream.chains[(KEY, EXPIRY)][0][0]["call_options"]["market_data"]["oi"], 100)

    def test_stale_greeks_cannot_be_refreshed_by_a_new_price(self):
        self.stream._apply(frame(AT-timedelta(seconds=40)), AT)
        self.stream._apply(frame(values={"ltpc": {"ltp": 22, "cp": 20}}), AT)
        rows, meta = self.stream.chain(KEY, EXPIRY)
        self.assertEqual(rows[0]["call_options"]["market_data"]["ltp"], 22)
        self.assertEqual(rows[0]["call_options"]["option_greeks"]["delta"], .5)
        self.assertEqual(meta["live_legs"], 0)

    def test_volume_provenance_tracks_vtt_independently_and_new_prices_do_not_refresh_it(self):
        self.stream._apply(frame(values={"vtt": "42"}), AT)
        rows, meta = self.stream.chain(KEY, EXPIRY)
        self.assertEqual(rows[0]["call_options"]["market_data"]["volume"], "42")
        self.assertEqual(meta["live_volume_legs"], 1)
        self.assertEqual(meta["live_oi_legs"], 0)
        self.assertEqual(datetime.fromisoformat(meta["volume_reported_at"]), AT)
        later = AT + timedelta(seconds=40)
        with patch("app.services.market_stream.now", return_value=later):
            self.stream._apply(frame(at=later, values={"ltpc": {"ltp": 22, "cp": 20}}), later)
            _, meta = self.stream.chain(KEY, EXPIRY)
        self.assertEqual(meta["live_volume_legs"], 0)
        self.assertIsNone(meta["volume_reported_at"])

    def test_disconnect_closed_exchange_and_reconnect_never_serve_old_live_values(self):
        self.stream._apply(frame(), AT)
        self.assertTrue(self.stream.quotes([LEG]))
        self.stream.active_keys.clear()
        self.assertFalse(self.stream.quotes([LEG]))
        self.stream.active_keys.add(LEG)
        self.stream._on_close()
        self.assertFalse(self.stream.quotes([LEG]))
        self.stream._on_connect(None)
        self.assertFalse(self.stream.quotes([LEG]))

    def test_invalid_future_out_of_order_and_previous_connection_frames_are_not_published(self):
        self.stream._apply(frame(), AT)
        for f in [frame(AT-timedelta(seconds=1)), frame(AT+timedelta(minutes=1)), {**frame(), "currentTs": None},
                  {**frame(), "_connection_generation": "old"}]:
            f["feeds"][LEG]["fullFeed"]["marketFF"]["ltpc"]["ltp"] = 999
            self.stream._apply(f, AT)
        self.assertEqual(self.stream.quotes([LEG])[LEG]["last_price"], 21)

    def test_commit_happens_before_cache_publication(self):
        def commit(batch):
            self.assertFalse(self.stream.ticks)
            self.stream.stop_event.set()
        self.stream.repo.ticks.side_effect = commit
        self.stream.queue.put((frame(), AT))
        self.stream._write_loop()
        self.assertTrue(self.stream.ticks)

    def test_storage_failure_does_not_publish_uncommitted_values(self):
        def fail(batch):
            self.stream.stop_event.set()
            raise ConnectionError("fixture")
        self.stream.repo.ticks.side_effect = fail
        self.stream.queue.put((frame(), AT))
        self.stream._write_loop()
        self.assertFalse(self.stream.ticks)

    def test_latest_closed_greeks_are_distinct_from_historical_capture(self):
        client = Mock()
        client.get_current_option_chain_snapshot.return_value = {"payload": chain(), "observed_at": AT.isoformat(), "transport": "rest"}
        result = maxpain_greeks.snapshot(client, KEY, EXPIRY, "2026-10-23", valid_session=True,
            checked_at=AT, latest=True, market_context={"phase": "closed", "active": False, "session_date": "2026-10-23"})
        self.assertTrue(result["data_available"])
        self.assertEqual(result["status"], "latest_rest")
        self.assertIn("not a certified historical", result["hint"])
        client.get_retained_option_chain.return_value = None
        result = maxpain_greeks.snapshot(client, KEY, EXPIRY, "2026-10-23", valid_session=True, checked_at=AT)
        self.assertFalse(result["data_available"])

    def test_subscription_alias_uses_supported_greeks_mode(self):
        ws = UpstoxMarketDataWSV3(Mock())
        ws.subscribe([LEG], "option_chain")
        self.assertIn(LEG, ws._subscriptions["option_greeks"])

    def test_manager_uses_one_connection_only_during_an_active_session(self):
        instances = []
        class Socket:
            is_running = False
            def __init__(self, *args, **kwargs):
                self.subscribe, self.unsubscribe = Mock(), Mock()
                instances.append(self)
            def start_background(self): self.is_running = True
            def stop(self): self.is_running = False
        self.stream.ws_factory = Socket
        self.stream.sessions = Mock()
        self.stream.sessions.context.return_value = {"active": False}
        self.stream.maintain()
        self.assertEqual(instances, [])
        self.stream.sessions.context.return_value = {"active": True}
        self.stream.maintain(); self.stream.maintain()
        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0].subscribe.call_args.kwargs["mode"], "full")
        self.stream.sessions.context.return_value = {"active": False}
        self.stream.maintain()
        self.assertFalse(instances[0].is_running)
        self.assertFalse(self.stream.status()["connected"])

@unittest.skipUnless(os.getenv("RUN_MARKET_DB_TESTS") == "1", "Set RUN_MARKET_DB_TESTS=1")
class StreamDatabaseTests(unittest.TestCase):
    def test_stream_tables_retain_ticks_and_exact_dated_chains(self):
        from app.config import get_settings
        store = MarketStore(get_settings().database_url_sync)
        repo = MarketStreamStore(store)
        key = "TEST_STREAM|"+uuid.uuid4().hex
        f = frame()
        f["feeds"] = {key: f["feeds"][LEG]}
        try:
            repo.ticks([(f, AT)])
            repo.chain(key, EXPIRY, chain(key), {"observed_at": "2026-10-23T15:30:00+05:30", "session_date": "2026-10-23", "transport": "websocket"})
            saved = repo.retained_chain(key, EXPIRY, "2026-10-23")
            self.assertEqual(saved["payload"][0]["underlying_key"], key)
            self.assertIsNone(repo.retained_chain(key, EXPIRY, "2026-10-22"))
            with store.engine.connect() as conn:
                self.assertEqual(conn.execute(text("SELECT count(*) FROM market_stream_ticks WHERE instrument_key=:key"), {"key": key}).scalar(), 1)
        finally:
            with store.engine.begin() as conn:
                conn.execute(text("DELETE FROM market_stream_ticks WHERE instrument_key=:key"), {"key": key})
                conn.execute(text("DELETE FROM market_stream_chains WHERE underlying_key=:key"), {"key": key})
            store.engine.dispose()

if __name__ == "__main__":
    unittest.main()
