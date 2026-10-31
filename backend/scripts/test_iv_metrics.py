"""Dated IV, expiry horizon, per-field freshness, sample weighting and durable replay."""
import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from sqlalchemy import text
from app.services.iv_metrics import capture_point, minute_points, daily_samples, ranked
from app.services.market_store import MarketStore, IST
from app.services.market_gateway import MarketGateway
from app.services import iv_service

KEY, EXPIRY, DAY = "NSE_INDEX|Nifty 50", "2026-11-03", "2026-10-28"
AT = datetime(2026, 10, 28, 10, tzinfo=IST)


def capture(at=AT, key=KEY, call=20, put=22):
    return {"observed_at": at.isoformat(), "payload": [
        {"expiry": EXPIRY, "underlying_key": key, "strike_price": strike, "underlying_spot_price": 22600,
         "call_options": {"instrument_key": f"C{strike}", "option_greeks": {"iv": call}},
         "put_options": {"instrument_key": f"P{strike}", "option_greeks": {"iv": put}}}
        for strike in (22550, 22600, 22650)]}


class IvMetricTests(unittest.TestCase):
    def point(self, raw):
        return capture_point(raw, KEY, EXPIRY, AT+timedelta(days=7))

    def test_atm_mean_and_calendar_fraction_expected_move(self):
        import math
        p = self.point(capture())
        self.assertEqual((p["iv"], p["call_iv"], p["put_iv"], p["strike"]), (21, 20, 22, 22600))
        days = (datetime(2026, 11, 3, 15, 30, tzinfo=IST)-AT).total_seconds()/86400
        self.assertAlmostEqual(p["expected_move"], 22600*.21*math.sqrt(days/365))
        self.assertAlmostEqual(p["upper"]-p["spot"], p["spot"]-p["lower"])
        self.assertEqual(p["days_to_expiry"], days)

    def test_exact_nearest_missing_does_not_use_next_strike_or_single_leg(self):
        for value in (None, 0, -1, True, float("nan"), float("inf")):
            raw = capture(); raw["payload"][1]["call_options"]["option_greeks"]["iv"] = value
            self.assertIsNone(self.point(raw))
        raw = capture()
        for row in raw["payload"]:
            row["underlying_spot_price"] = 22575
        self.assertEqual(self.point(raw)["strike"], 22550)  # reproducible tie

    def test_identity_duplicates_invalid_spot_and_capture_clock(self):
        for field, value in [("expiry", "2026-11-10"), ("underlying_key", "other"), ("strike_price", 22600), ("underlying_spot_price", None)]:
            raw = capture(); raw["payload"][0][field] = value
            self.assertIsNone(self.point(raw))
        for at in (AT.replace(hour=0), AT.replace(hour=16), AT.replace(tzinfo=None), AT+timedelta(days=8)):
            self.assertIsNone(self.point(capture(at)))
        self.assertIsNone(capture_point(capture(), KEY, EXPIRY, AT-timedelta(seconds=1)))

    def test_stream_iv_freshness_is_independent_of_updated_price_and_oi(self):
        raw = capture()
        raw["provenance"] = {"transport": "websocket", "session_date": DAY, "rest_seed_at": (AT-timedelta(seconds=20)).isoformat()}
        for row in raw["payload"]:
            for side in ("call_options", "put_options"):
                row[side]["_provenance"] = {"iv_source": "websocket", "iv_at": (AT-timedelta(seconds=5)).isoformat()}
        self.assertEqual(self.point(raw)["source"], "WebSocket")
        raw["payload"][1]["call_options"]["_provenance"]["iv_at"] = (AT-timedelta(minutes=2)).isoformat()
        self.assertIsNone(self.point(raw))
        raw["payload"][1]["call_options"]["_provenance"] = {"iv_source": "rest", "iv_at": (AT-timedelta(seconds=20)).isoformat()}
        self.assertEqual(self.point(raw)["source"], "Mixed REST / WebSocket")
        raw["provenance"]["rest_seed_at"] = (AT-timedelta(minutes=2)).isoformat()
        self.assertIsNone(self.point(raw))  # old spot cannot choose ATM despite fresh IV

    def test_expiry_close_gives_true_zero_move_and_no_post_expiry_capture(self):
        at = datetime(2026, 11, 3, 15, 30, tzinfo=IST)
        self.assertEqual(self.point(capture(at))["expected_move"], 0)
        self.assertIsNone(self.point(capture(at+timedelta(days=1))))

    def test_last_capture_per_minute_no_interpolation_and_no_future_day_in_history(self):
        raws = [capture(AT-timedelta(days=2), call=10, put=10), capture(AT-timedelta(days=2)+timedelta(hours=1), call=14, put=14),
                capture(AT-timedelta(days=1)), capture(AT), capture(AT+timedelta(seconds=20), call=24, put=24), capture(AT+timedelta(minutes=3))]
        rows = minute_points(raws, KEY, EXPIRY, AT+timedelta(hours=1))
        self.assertEqual([p["time"] for p in rows if p["date"] == DAY], ["10:00", "10:03"])
        self.assertEqual(next(p["iv"] for p in rows if p["date"] == DAY), 24)
        baseline = daily_samples(rows, DAY)
        self.assertEqual([p["iv"] for p in baseline], [14, 21])
        self.assertEqual(len(daily_samples(rows, "2026-10-27")), 1)

    def test_rank_percentile_daily_weight_ties_constant_range_and_warmup(self):
        p = self.point(capture(call=30, put=30))
        baseline = [{"iv": iv} for iv in (10, 20, 30, 40)]
        result = ranked(p, baseline)
        self.assertAlmostEqual(result["iv_rank"], 100*20/30)
        self.assertEqual(result["iv_percentile"], 50)  # ties strictly excluded
        self.assertIsNone(ranked(p, [{"iv": 10}])["iv_rank"])
        flat = ranked(p, [{"iv": 30}, {"iv": 30}])
        self.assertIsNone(flat["iv_rank"])
        self.assertEqual(flat["iv_percentile"], 0)
        self.assertEqual(ranked(p, [{"iv": 10}, {"iv": 20}])["iv_rank"], 100)

    def test_service_preserves_identity_and_missing_session(self):
        client = Mock()
        with patch.object(iv_service, "get_upstox", return_value=client), patch.object(iv_service, "_now", return_value=AT), patch.object(iv_service, "_session", return_value=(False, None, "No trading session")):
            result = iv_service.history(EXPIRY, DAY, KEY)
        self.assertEqual((result["instrument_key"], result["expiry"], result["as_of"]), (KEY, EXPIRY, DAY))
        self.assertFalse(result["data_available"])
        self.assertIn("No trading session", result["hint"])
        client.get_iv_history.assert_not_called()

    @unittest.skipUnless(os.getenv("RUN_MARKET_DB_TESTS") == "1", "requires local PostgreSQL")
    def test_database_replay_after_gateway_restart_makes_no_provider_calls(self):
        from app.config import get_settings
        key = "TEST_INDEX|iv-"+uuid.uuid4().hex
        store = MarketStore(get_settings().database_url_sync)
        store.initialize()
        remote = Mock()
        try:
            raw = capture(at=AT-timedelta(days=2), key=key)
            # Write the same original response shape the gateway retains.
            with store.engine.begin() as conn:
                from app.services.market_store import request_key
                params = {"instrument_key": key, "expiry_date": EXPIRY, "observed_on": "2026-10-26"}
                store._archive(conn, request_key("get_option_chain", params), "get_option_chain", params, raw["payload"], AT-timedelta(days=2))
            first = MarketGateway(remote, store).get_iv_history(key, EXPIRY, "2026-10-26")
            self.assertEqual(first["points"][0]["iv"], 21)
            store.cache.clear()
            self.assertEqual(MarketGateway(remote, store).get_iv_history(key, EXPIRY, "2026-10-26"), first)
            remote.get_option_chain.assert_not_called()
            self.assertEqual(MarketGateway(remote, store).get_iv_history(key, EXPIRY, "2026-10-23")["points"], [])
        finally:
            with store.engine.begin() as conn:
                conn.execute(text("DELETE FROM market_responses WHERE parameters->>'instrument_key'=:key"), {"key": key})
            store.engine.dispose()


if __name__ == "__main__":
    unittest.main()
