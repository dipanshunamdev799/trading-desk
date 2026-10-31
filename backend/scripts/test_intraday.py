"""One-minute intraday adapter tests; no market-data requests."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from fastapi import HTTPException, Response
from app.routers.options import max_pain_intraday
from app.services import max_pain_service


class IntradayTests(unittest.TestCase):
    def test_requests_real_one_minute_buckets_without_building_chain(self):
        client = Mock()
        client.get_historical_candles_v3.return_value = {"candles": [["2026-10-23T00:00:00+05:30", 0, 0, 0, 22600]]}
        client.get_max_pain.return_value = {"expiry_date": "27-10-2026", "spot_closing_price": 22600, "insights": [
            {"time": "09:15", "max_pain": 22700, "spot_price": 22600},
            {"time": "09:16", "max_pain": 22750, "spot_price": 22625},
        ]}
        with patch.object(max_pain_service, "get_upstox", return_value=client), \
             patch.object(max_pain_service.nmp, "fetch_chain") as chain:
            result = max_pain_service.intraday("2026-10-27", "2026-10-23", "NSE_INDEX|Nifty 50")
        client.get_max_pain.assert_called_once_with(
            "NSE_INDEX|Nifty 50", expiry="2026-10-27", date="2026-10-23", bucket_interval=1
        )
        chain.assert_not_called()
        self.assertEqual(result["bucket_minutes"], 1)
        self.assertEqual([row["time"] for row in result["insights"]], ["09:15", "09:16"])
        self.assertTrue(result["fetched_at"].endswith("+05:30"))

    def test_route_disables_caching_and_keeps_provider_failures_visible(self):
        response = Response()
        with patch.object(max_pain_service, "intraday", return_value={"insights": []}):
            result = max_pain_intraday(response, "2026-10-27", "2026-10-23", "NSE_INDEX|Nifty 50")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(result["insights"], [])
        with patch.object(max_pain_service, "intraday", side_effect=RuntimeError("upstream unavailable")):
            with self.assertRaises(HTTPException) as error:
                max_pain_intraday(Response(), "2026-10-27", "2026-10-23", "NSE_INDEX|Nifty 50")
        self.assertEqual(error.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
