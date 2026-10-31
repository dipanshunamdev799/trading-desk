"""Volume aggregation, exact capture dates, mixed-source freshness and DB-only replay."""
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
from app.services.volume_pcr import chain_point, chain_series
from app.services.market_store import IST, MarketStore
from app.services.market_gateway import MarketGateway
from app.services import max_pain_service, pcr_service

DAY, EXPIRY, KEY = "2026-10-26", "2026-10-27", "NSE_INDEX|Nifty 50"
AT = datetime(2026, 10, 26, 10, tzinfo=IST)


def capture(key=KEY, at=AT):
    return {"observed_at": at.isoformat(), "payload": [
        {"expiry": EXPIRY, "underlying_key": key, "strike_price": strike, "underlying_spot_price": 22600,
         "call_options": {"instrument_key": f"CALL{strike}", "market_data": {"volume": call}},
         "put_options": {"instrument_key": f"PUT{strike}", "market_data": {"volume": put}}}
        for strike, call, put in [(22500, 10, 20), (23000, 90, 30)]]}


class VolumePcrTests(unittest.TestCase):
    def point(self, value):
        return chain_point(value, KEY, EXPIRY, DAY, AT + timedelta(hours=8))

    def test_ratio_of_totals_not_average_of_strike_ratios(self):
        point = self.point(capture())
        self.assertEqual(point["volume_pcr"], .5)
        self.assertEqual((point["call_volume"], point["put_volume"]), (100, 50))

    def test_missing_negative_nonfinite_bool_and_zero_denominator_are_not_fabricated_ratios(self):
        for value in [None, -1, float("nan"), True]:
            raw = capture(); raw["payload"][0]["call_options"]["market_data"]["volume"] = value
            self.assertIsNone(self.point(raw))
        raw = capture()
        for row in raw["payload"]:
            row["call_options"]["market_data"]["volume"] = 0
        self.assertIsNone(self.point(raw))
        raw = capture()
        for row in raw["payload"]:
            row["put_options"]["market_data"]["volume"] = 0
        self.assertEqual(self.point(raw)["volume_pcr"], 0)

    def test_other_day_expiry_underlying_duplicates_and_overnight_receipt_are_rejected(self):
        cases = [capture(at=AT-timedelta(days=1)), capture(at=AT.replace(hour=0)), capture(at=AT.replace(hour=18))]
        for field, value in [("expiry", "2026-11-03"), ("underlying_key", "other"), ("strike_price", 23000)]:
            raw = capture(); raw["payload"][0][field] = value; cases.append(raw)
        raw = capture(); raw["payload"][0]["put_options"]["instrument_key"] = "CALL22500"; cases.append(raw)
        for raw in cases:
            self.assertIsNone(self.point(raw))
        self.assertIsNone(chain_point(capture(), KEY, EXPIRY, DAY, AT-timedelta(seconds=1)))

    def test_stream_volume_freshness_is_separate_from_oi_or_price(self):
        raw = capture()
        raw["provenance"] = {"transport": "websocket", "session_date": DAY,
            "live_volume_legs": 4, "volume_reported_at": AT.isoformat()}
        self.assertEqual(self.point(raw)["volume_source"], "websocket_capture")
        raw["provenance"]["live_volume_legs"] = 3
        self.assertIsNone(self.point(raw))
        raw["provenance"]["rest_seed_at"] = (AT-timedelta(seconds=45)).isoformat()
        self.assertEqual(self.point(raw)["volume_source"], "mixed_capture")
        raw["provenance"]["rest_seed_at"] = (AT-timedelta(minutes=4)).isoformat()
        self.assertIsNone(self.point(raw))

    def test_latest_capture_per_minute_wins_without_interpolating_missing_minutes(self):
        first = capture(at=AT); second = capture(at=AT+timedelta(seconds=15))
        second["payload"][0]["put_options"]["market_data"]["volume"] = 40
        points = chain_series([second, first, capture(at=AT+timedelta(minutes=3))], KEY, EXPIRY, DAY, AT+timedelta(hours=1))
        self.assertEqual([point["time"] for point in points], ["10:00", "10:03"])
        self.assertEqual(points[0]["volume_pcr"], .7)

    def test_volume_can_be_available_without_oi_history(self):
        client = Mock(); client.get_pcr.side_effect = RuntimeError("OI provider down")
        client.get_volume_pcr_history.return_value = [self.point(capture())]
        with patch.object(pcr_service, "get_upstox", return_value=client), \
             patch.object(pcr_service, "_session", return_value=(True, None, None)), \
             patch.object(pcr_service, "_now", return_value=AT):
            result = pcr_service.intraday(EXPIRY, DAY, KEY)
        self.assertTrue(result["data_available"])
        self.assertTrue(result["volume_pcr_available"])
        self.assertFalse(result["oi_pcr_available"])
        self.assertIsNone(result["points"][0]["pcr"])
        self.assertEqual(result["points"][0]["volume_pcr"], .5)

    def test_only_committed_active_feed_captures_can_prove_a_session_when_daily_candle_is_missing(self):
        client = Mock(); client.has_retained_market_session.return_value = True
        with patch.object(max_pain_service, "_now", return_value=AT+timedelta(days=2)), \
             patch.object(max_pain_service.nmp, "fetch_daily_closes", return_value={}):
            self.assertTrue(max_pain_service._session(client, DAY, EXPIRY, KEY)[0])
            client.has_retained_market_session.return_value = False
            self.assertFalse(max_pain_service._session(client, DAY, EXPIRY, KEY)[0])


@unittest.skipUnless(os.getenv("RUN_MARKET_DB_TESTS") == "1", "Set RUN_MARKET_DB_TESTS=1")
class VolumeDatabaseTests(unittest.TestCase):
    def test_archived_volume_survives_gateway_restart_without_upstream_and_uses_exact_day(self):
        from app.config import get_settings
        store = MarketStore(get_settings().database_url_sync)
        store.initialize()
        key = "TEST_VOLUME|" + uuid.uuid4().hex
        params = {"instrument_key": key, "expiry_date": EXPIRY, "observed_on": DAY}
        try:
            with patch("app.services.market_store.now", return_value=AT):
                store.read("get_option_chain", params, lambda: capture(key)["payload"])
            remote = Mock()
            first = MarketGateway(remote, store).get_volume_pcr_history(key, EXPIRY, DAY)
            store.cache.clear()
            replay = MarketGateway(remote, store).get_volume_pcr_history(key, EXPIRY, DAY)
            self.assertEqual(first, replay)
            self.assertEqual(replay[0]["volume_pcr"], .5)
            self.assertEqual(MarketGateway(remote, store).get_volume_pcr_history(key, EXPIRY, "2026-10-23"), [])
            remote.get_option_chain.assert_not_called()
            self.assertEqual(store.recorded_session_dates(key, DAY, DAY), [])  # REST receipt alone proves no session.
        finally:
            with store.engine.begin() as conn:
                conn.execute(text("DELETE FROM market_responses WHERE parameters->>'instrument_key'=:key"), {"key": key})
                conn.execute(text("DELETE FROM market_datasets WHERE parameters->>'instrument_key'=:key"), {"key": key})
            store.engine.dispose()


if __name__ == "__main__":
    unittest.main()
