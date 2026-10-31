"""PCR date isolation, real observations, and durable reuse without provider calls."""
import os
import sys
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from fastapi import HTTPException, Response
from sqlalchemy import text
from app.routers.options import pcr_intraday
from app.services import pcr_service
from app.services.market_store import IST, MarketStore
from app.services.market_gateway import MarketGateway

KEY, EXPIRY, DAY = "NSE_INDEX|Nifty 50", "2026-10-27", "2026-10-23"
AT = datetime(2026, 10, 25, 10, tzinfo=IST)

def payload(key=KEY):
    return {"instrument_key": key, "expiry_date": "27-10-2026", "spot_closing_price": 22600,
            "insights": [{"time": "09:15", "pcr": .82, "spot_price": 22719.9},
                         {"time": "09:16", "pcr": 0, "spot_price": 22720}]}

class PcrTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.get_pcr.return_value = payload()

    def result(self):
        with patch.object(pcr_service, "get_upstox", return_value=self.client), \
             patch.object(pcr_service, "_session", return_value=(True, 22600, None)), \
             patch.object(pcr_service, "_now", return_value=AT):
            return pcr_service.intraday(EXPIRY, DAY, KEY)

    def test_real_one_minute_observations_and_zero_pcr_are_preserved(self):
        result = self.result()
        self.client.get_pcr.assert_called_once_with(KEY, expiry=EXPIRY, date=DAY, bucket_interval=1)
        self.client.get_option_chain.assert_not_called()
        self.assertEqual([row["pcr"] for row in result["points"]], [.82, 0])
        self.assertTrue(result["data_available"])

    def test_other_underlying_expiry_date_or_session_close_is_rejected(self):
        for field, value in (("instrument_key", "NSE_EQ|other"), ("expiry_date", "03-11-2026"),
                             ("date", "2026-10-22"), ("spot_closing_price", 23000)):
            with self.subTest(field=field):
                self.client.get_pcr.return_value = {**payload(), field: value}
                self.assertFalse(self.result()["data_available"])
                self.assertEqual(self.result()["points"], [])

    def test_nontrading_or_invalid_session_does_not_fetch_pcr(self):
        with patch.object(pcr_service, "get_upstox", return_value=self.client), \
             patch.object(pcr_service, "_session", return_value=(False, None, "No trading session")):
            result = pcr_service.intraday(EXPIRY, "2026-10-24", KEY)
        self.assertEqual(result["hint"], "No trading session")
        self.client.get_pcr.assert_not_called()

    def test_invalid_missing_and_future_readings_do_not_become_zero_or_filled_minutes(self):
        raw = {"insights": [{"time": "09:17", "pcr": "nan"}, {"time": "09:15", "pcr": .8},
            {"time": "09:19", "pcr": True}, {"time": "09:20", "pcr": -.1}, {"time": "09:99", "pcr": 1},
            {"time": "09:18", "date": "2026-10-22", "pcr": 1}, {"time": "10:01", "pcr": 1}]}
        result = pcr_service.series(raw, DAY, datetime(2026, 10, 23, 10, tzinfo=IST))
        self.assertEqual([row["time"] for row in result], ["09:15", "09:17", "09:19", "09:20"])
        self.assertEqual([row["pcr"] for row in result], [.8, None, None, None])

    def test_route_uses_no_store_and_reports_provider_errors(self):
        response = Response()
        with patch.object(pcr_service, "intraday", return_value={"points": []}):
            pcr_intraday(response, EXPIRY, DAY, KEY)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        with patch.object(pcr_service, "intraday", side_effect=RuntimeError("fixture")):
            with self.assertRaises(HTTPException) as error:
                pcr_intraday(Response(), EXPIRY, DAY, KEY)
        self.assertEqual(error.exception.status_code, 502)

@unittest.skipUnless(os.getenv("RUN_MARKET_DB_TESTS") == "1", "Set RUN_MARKET_DB_TESTS=1")
class PcrDatabaseTests(unittest.TestCase):
    def test_one_minute_history_survives_a_new_gateway_without_refetching(self):
        from app.config import get_settings
        key = "TEST_PCR|"+uuid.uuid4().hex
        store = MarketStore(get_settings().database_url_sync)
        store.initialize()
        gateway = MarketGateway(Mock(), store)
        try:
            with patch.object(gateway, "_validated_analytics", return_value=payload(key)) as upstream:
                first = gateway.get_pcr(key, EXPIRY, DAY)
                second = gateway.get_pcr(key, EXPIRY, DAY)
                self.assertEqual(upstream.call_count, 1)
                self.assertEqual(first, second)
            store.cache.clear()
            other = MarketGateway(Mock(), store)
            with patch.object(other, "_validated_analytics", side_effect=AssertionError("Unexpected refetch")):
                retained = other.get_pcr(key, EXPIRY, DAY)
                self.assertEqual(retained["insights"], payload(key)["insights"])
            with store.engine.connect() as conn:
                self.assertEqual(conn.execute(text("SELECT count(*) FROM market_responses WHERE method='get_pcr' AND parameters->>'instrument_key'=:key"), {"key": key}).scalar(), 1)
        finally:
            with store.engine.begin() as conn:
                conn.execute(text("DELETE FROM market_responses WHERE parameters->>'instrument_key'=:key"), {"key": key})
                conn.execute(text("DELETE FROM market_datasets WHERE parameters->>'instrument_key'=:key"), {"key": key})
            store.engine.dispose()

if __name__ == "__main__":
    unittest.main()
