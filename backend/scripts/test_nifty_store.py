"""NIFTY PostgreSQL retention tests; opt in with RUN_MARKET_DB_TESTS=1.

Only unique test factor/event records are created and removed. The application
research state is never replaced by these tests and no provider is called.
"""
import os
import sys
import unittest
import uuid
import json
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.config import get_settings
from app.services.market_store import MarketStore
from app.services.nifty_store import NiftyStore


@unittest.skipUnless(os.getenv("RUN_MARKET_DB_TESTS") == "1", "Set RUN_MARKET_DB_TESTS=1 for local TimescaleDB tests")
class NiftyDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.fixture = "TEST_NIFTY_" + uuid.uuid4().hex
        self.market = MarketStore(get_settings().database_url_sync)
        self.repo = NiftyStore(self.market)
        self.market.initialize()

    def tearDown(self):
        with self.market.engine.begin() as conn:
            conn.execute(text("DELETE FROM nifty_observations WHERE factor_id=:id"), {"id": self.fixture})
            conn.execute(text("DELETE FROM nifty_research_events WHERE payload->>'test_fixture'=:id"), {"id": self.fixture})
        self.market.engine.dispose()

    def observation(self, **values):
        return {"factor_id": self.fixture, "source": "Test fixture", "source_url": "https://example.org/test",
            "value": 100, "reported_at": "2026-10-23T10:00:00+00:00", "observed_at": "2026-10-23T11:00:00+00:00", **values}

    def test_batch_is_idempotent_revisions_survive_and_late_old_data_does_not_replace_latest(self):
        row = self.observation()
        self.assertEqual(self.repo.save_observations([row]), 1)
        self.assertEqual(self.repo.save_observations([{**row, "observed_at": "2026-10-23T12:00:00+00:00"}]), 0)
        late_old = self.observation(value=90, reported_at="2026-10-23T09:00:00+00:00", observed_at="2026-10-23T14:00:00+00:00")
        correction = self.observation(value=101, observed_at="2026-10-23T13:00:00+00:00")
        self.assertEqual(self.repo.save_observations([late_old, correction]), 2)
        self.assertEqual(self.repo.latest()[self.fixture]["value"], 101)
        history = self.repo.history(self.fixture)
        self.assertEqual([row["value"] for row in history], [90, 100, 101])
        self.assertEqual([row["value"] for row in self.repo.history(self.fixture, limit=2)], [100, 101])

    def test_calendar_shows_latest_revision_and_accepts_future_event_dates(self):
        row = {"id": self.fixture + "_event", "test_fixture": self.fixture, "title": "Policy release",
               "event_at": "2027-01-05T10:00:00+00:00", "observed_at": "2026-10-23T11:00:00+00:00",
               "source": "Test fixture", "source_url": "https://example.org/test"}
        revised = {**row, "event_at": "2027-01-06T10:00:00+00:00", "observed_at": "2026-10-23T12:00:00+00:00"}
        self.assertEqual(self.repo.save_events([row, revised]), 2)
        self.assertEqual(self.repo.save_events([{**revised, "observed_at": "2026-10-24T12:00:00+00:00"}]), 0)
        events = [event for event in self.repo.events(1000) if event.get("test_fixture") == self.fixture]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_at"], revised["event_at"])

    def test_verified_cash_report_survives_later_ambiguous_provider_refresh(self):
        # Session-local temporary table shadows the real table only on this
        # connection. No fixture cash figures are visible to application readers.
        with self.market.engine.connect() as conn:
            transaction = conn.begin()
            try:
                conn.exec_driver_sql("CREATE TEMPORARY TABLE nifty_observations (LIKE public.nifty_observations INCLUDING ALL) ON COMMIT DROP")
                test_store = NiftyStore(SimpleNamespace(initialize=lambda: None,
                    engine=SimpleNamespace(connect=lambda: nullcontext(conn))))
                def insert(key, source, value, reported, observed, quality):
                    payload = {"factor_id": "fii_cash", "source": source, "value": value, "quality": quality}
                    conn.execute(text("""INSERT INTO nifty_observations
                        (observation_key,factor_id,source,reported_at,observed_at,payload)
                        VALUES(:key,'fii_cash',:source,:reported,:observed,CAST(:data AS jsonb))"""),
                        {"key": key, "source": source, "reported": reported, "observed": observed, "data": json.dumps(payload)})
                insert("official", "NSE", 887.65, "2026-10-23T00:00:00+05:30", "2026-10-24T10:00:00Z", "exchange_report")
                insert("ambiguous", "Upstox", None, "2026-10-23T00:00:00+05:30", "2026-10-24T11:00:00Z", "unverified_units")
                self.assertEqual(test_store.latest()["fii_cash"]["value"], 887.65)
                insert("next-session", "Upstox", None, "2026-10-26T00:00:00+05:30", "2026-10-26T13:00:00Z", "unverified_units")
                self.assertIsNone(test_store.latest()["fii_cash"]["value"])
            finally:
                transaction.rollback()


if __name__ == "__main__":
    unittest.main()
