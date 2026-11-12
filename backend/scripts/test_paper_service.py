"""Paper valuation should read retained marks without historical backfills."""
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.schemas import PaperOrderIn
from app.services import paper_service


class MarkTests(unittest.IsolatedAsyncioTestCase):
    async def test_cached_daily_close_does_not_request_upstream_history_or_quotes(self):
        db = AsyncMock()
        db.scalar.return_value = 1420.5
        with patch.object(paper_service.upstox_service, "fetch_ltp") as remote:
            self.assertEqual(await paper_service._mark_price(db, "NSE_EQ|TEST"), 1420.5)
        remote.assert_not_called()
        query = str(db.scalar.call_args.args[0])
        self.assertIn("ORDER BY candles.ts DESC", query)
        self.assertIn("LIMIT", query)

    async def test_missing_candles_use_only_the_matching_quote(self):
        db = AsyncMock()
        db.scalar.return_value = None
        with patch.object(paper_service.upstox_service, "fetch_ltp", return_value={
            "unrelated": {"last_price": 999}, "NSE_EQ:TEST": {"last_price": 125},
        }):
            self.assertEqual(await paper_service._mark_price(db, "NSE_EQ|TEST"), 125)
        with patch.object(paper_service.upstox_service, "fetch_ltp", return_value={
            "unrelated": {"last_price": 999},
        }):
            self.assertEqual(await paper_service._mark_price(db, "NSE_EQ|TEST"), 0)

    async def test_unpriced_order_creates_no_order_or_fill(self):
        db = Mock()
        with patch.object(paper_service, "_mark_price", AsyncMock(return_value=0)):
            with self.assertRaisesRegex(ValueError, "not filled"):
                await paper_service.place_order(db, PaperOrderIn(instrument_key="NSE_EQ|TEST", side="BUY", qty=1))
        db.add.assert_not_called()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
