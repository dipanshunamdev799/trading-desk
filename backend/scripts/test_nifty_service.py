"""Research freshness, data retention and API import validation regressions."""
from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from pydantic import ValidationError
from app.routers.nifty import EventInput, ObservationInput
from app.services.nifty_catalog import FACTOR_MAP
from app.services.nifty_service import NiftyService, latest_revisions


class MemoryRepo:
    def __init__(self):
        self.rows, self.payload, self.calendar = [], {}, []
    def save_observations(self, rows):
        self.rows.extend(deepcopy(rows))
        return len(rows)
    def latest(self):
        return {row["factor_id"]: row for row in self.rows}
    def history(self, factor_id, limit=365):
        return [row for row in self.rows if row["factor_id"] == factor_id][-limit:]
    def save_state(self, payload):
        self.payload = deepcopy(payload)
    def state(self):
        return deepcopy(self.payload)
    def save_events(self, rows):
        self.calendar.extend(rows)
        return len(rows)
    def events(self, limit=100):
        return self.calendar[:limit]


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.repo = MemoryRepo()
        self.service = NiftyService(self.repo, lambda: {"source_errors": []})
        self.at = datetime.now(timezone.utc)
    def factor(self, observation, history=None):
        return self.service._factor(FACTOR_MAP["sp500"], observation, history or [], self.at)
    def test_zero_is_present_and_missing_is_not_zero(self):
        self.assertEqual(self.factor({"value": 0, "reported_at": self.at.isoformat()})["status"], "available")
        missing = self.factor(None)
        self.assertIsNone(missing["value"])
        self.assertEqual(missing["status"], "missing")
    def test_collection_time_cannot_make_undated_or_old_source_fresh(self):
        self.assertEqual(self.factor({"value": 100, "reported_at": None, "observed_at": self.at.isoformat()})["status"], "stale")
        old = (self.at - timedelta(days=20)).isoformat()
        self.assertEqual(self.factor({"value": 100, "reported_at": old, "observed_at": self.at.isoformat()})["status"], "stale")
    def test_change_does_not_compare_different_sources_or_same_timestamp_revision(self):
        stamp = self.at.isoformat()
        row = {"value": 110, "source": "A", "reported_at": stamp}
        self.assertIsNone(self.factor(row, [{"value": 90, "source": "B", "reported_at": (self.at-timedelta(days=1)).isoformat()}])["change"])
        self.assertIsNone(self.factor(row, [{"value": 90, "source": "A", "reported_at": stamp}])["change"])
        point = {"value": 100, "source": "A", "reported_at": (self.at-timedelta(days=1)).isoformat()}
        result = self.factor(row, [point])
        self.assertEqual(result["change"], 10)
        self.assertEqual(result["change_pct"], 10)
    def test_empty_source_refresh_retains_successful_series_and_replaces_errors(self):
        self.repo.payload = {"candles": [{"ts": "2026-01-01", "close": 100}], "expiries": [{"expiry": "2026-01-15"}], "source_errors": [{"source": "old", "error": "old"}]}
        result = self.service.refresh()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(self.repo.payload["candles"][0]["close"], 100)
        self.assertEqual(self.repo.payload["source_errors"], [])
    def test_no_composite_direction_and_every_catalog_factor_visible(self):
        result = self.service.dashboard(auto_refresh=False)
        self.assertEqual(len(result["sections"]), 10)
        self.assertEqual(result["summary"]["missing"], len(FACTOR_MAP))
        self.assertNotIn("prediction", result)
        self.assertNotIn("signal", result)
    def test_refresh_lock_prevents_duplicate_collection(self):
        self.service.refresh_lock.acquire()
        try:
            self.assertEqual(self.service.request_refresh(), "running")
            self.assertEqual(self.service.refresh()["status"], "running")
        finally:
            self.service.refresh_lock.release()
    def test_disabled_automatic_collector_does_not_run_on_dashboard_read(self):
        settings = SimpleNamespace(nifty_collector_enabled=False, nifty_refresh_seconds=60)
        with patch("app.services.nifty_service.get_settings", return_value=settings), patch.object(self.service, "request_refresh") as request:
            self.service.dashboard(auto_refresh=True)
            request.assert_not_called()
        # Explicit collection still works when automatic collection is off.
        self.assertEqual(self.service.refresh()["status"], "completed")
    def test_signed_flows_do_not_get_price_return_correlation(self):
        result = self.service.correlations("fii_cash")
        self.assertIsNone(result["coefficient"])
        self.assertEqual(result["sample_count"], 0)
    def test_nested_null_warmup_retains_missing_reason(self):
        row = {"value": {"atr_14": None, "nested": {"volatility": None}},
               "context": "Requires 15 valid bars; received 3.", "reported_at": self.at.isoformat()}
        result = self.service._factor(FACTOR_MAP["atr_volatility"], row, [], self.at)
        self.assertEqual(result["status"], "missing")
        self.assertEqual(result["availability_note"], row["context"])
        row["value"]["atr_14"] = 0
        self.assertEqual(self.service._factor(FACTOR_MAP["atr_volatility"], row, [], self.at)["status"], "available")
    def test_unverified_cash_units_keep_zero_but_never_claim_freshness(self):
        row = {"value": 0, "reported_at": self.at.isoformat(), "quality": "unverified_units",
               "quality_note": "Publisher units conflict; verify original cash release."}
        result = self.service._factor(FACTOR_MAP["fii_cash"], row, [], self.at)
        self.assertEqual(result["value"], 0)
        self.assertEqual(result["status"], "stale")
        self.assertEqual(result["quality_note"], row["quality_note"])
        self.assertEqual(result["availability_note"], row["quality_note"])
        row["value"] = None
        result = self.service._factor(FACTOR_MAP["fii_cash"], row, [], self.at)
        self.assertEqual(result["status"], "missing")
        self.assertEqual(result["availability_note"], row["quality_note"])
    def test_contract_terms_and_original_chain_metadata_survive_collection(self):
        metadata = {"reported_at": None, "observed_at": "2026-10-22T10:00:00+00:00", "expiry": "2026-10-27"}
        self.service.collector = lambda: {"option_chain": [{"strike_price": 100, "expiry": "2026-10-27"}],
            "option_chain_meta": metadata,
            "expiries": [{"expiry": "2026-10-27", "weekly": True, "lot_sizes": [65]}]}
        result = self.service.refresh()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(self.repo.payload["option_chain_meta"], metadata)
        self.assertEqual(self.repo.latest()["call_oi"]["expiry"], "2026-10-27")
        self.assertEqual(self.service._factor(FACTOR_MAP["call_oi"], self.repo.latest()["call_oi"], [], self.at)["expiry"], "2026-10-27")
        specs = self.repo.latest()["contract_specs"]
        self.assertEqual(specs["value"][0]["lot_sizes"], [65])
        self.assertIsNone(specs["reported_at"])
        self.assertIn("no historical change", specs["context"])
    def test_correlation_keeps_current_source_and_unit(self):
        start = self.at - timedelta(days=30)
        self.repo.payload["candles"] = []
        for index in range(30):
            stamp = (start + timedelta(days=index)).isoformat()
            price = 100 + index + index % 3
            self.repo.payload["candles"].append({"ts": stamp, "close": price})
            self.repo.rows.append({"factor_id": "sp500", "value": price, "reported_at": stamp, "source": "A", "unit": "points"})
            self.repo.rows.append({"factor_id": "sp500", "value": 10_000 - price, "reported_at": stamp, "source": "B", "unit": "different units"})
        # The selected latest observation decides which consistent series is
        # used, even when another source has conflicting values on every date.
        self.repo.rows.append({**self.repo.rows[-2]})
        result = self.service.correlations("sp500")
        self.assertEqual(result["source"], "A")
        self.assertEqual(result["unit"], "points")
        self.assertEqual(result["sample_count"], 29)
        self.assertAlmostEqual(result["coefficient"], 1)
    def test_correlation_uses_exchange_date_and_latest_actual_timestamp(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.repo.payload["candles"] = []
        for index in range(30):
            day = start + timedelta(days=index)
            value = 100 + index + index % 3
            self.repo.payload["candles"].append({"ts": day.date().isoformat(), "close": value})
            # 01:00 UTC is the preceding US calendar date. An earlier 22:00
            # UTC quote from that same market date must not outrank it.
            for timestamp, quote in ((day + timedelta(hours=22), 999), (day + timedelta(days=1, hours=1), value)):
                self.repo.rows.append({"factor_id": "sp500", "value": quote, "reported_at": timestamp.isoformat(),
                    "source": "A", "unit": "points", "context": {"exchange_timezone": "America/New_York"}})
        result = self.service.correlations("sp500")
        self.assertEqual(result["sample_count"], 29)
        self.assertAlmostEqual(result["coefficient"], 1)
        # An explicit publisher session date takes precedence over UTC dates,
        # including when a completed bar was timestamped at local midnight.
        for row in self.repo.rows:
            row["context"]["session_date"] = (datetime.fromisoformat(row["reported_at"]) - timedelta(hours=5)).date().isoformat()
            row["context"]["exchange_timezone"] = "UTC"
        self.assertAlmostEqual(self.service.correlations("sp500")["coefficient"], 1)
    def test_null_and_unverified_revisions_supersede_old_numeric_evidence(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        old_rows = []
        for index in range(30):
            stamp = (start + timedelta(days=index)).isoformat()
            old_rows.append({"factor_id": "sp500", "value": 100 + index + index % 3,
                "source": "A", "unit": "points", "reported_at": stamp, "observed_at": stamp})
        invalidated = {**old_rows[-2], "value": None, "observed_at": "2026-03-01T00:00:00Z"}
        bad_units = {**old_rows[-3], "value": 0, "observed_at": "2026-03-01T00:00:00Z", "quality_note": "Units unverified"}
        # Deliberately place newer revisions before old numeric rows to prove
        # acquired time, rather than input position or numeric presence, wins.
        evidence = [invalidated, bad_units, *old_rows]
        resolved = latest_revisions(evidence)
        self.assertEqual(len(resolved), 30)
        self.assertIsNone(resolved[-2]["value"])
        current = old_rows[-1]
        factor = self.service._factor(FACTOR_MAP["sp500"], current, evidence, self.at)
        self.assertEqual(factor["previous_value"], old_rows[-4]["value"])
        self.assertEqual(len(factor["history"]), 28)
        self.assertNotIn(0, [point["value"] for point in factor["history"]])
        self.repo.rows = [*evidence, current]
        self.repo.payload["candles"] = [{"ts": row["reported_at"], "close": row["value"]} for row in old_rows]
        correlation = self.service.correlations("sp500")
        # Two missing adjacent sessions remove three matched return intervals.
        self.assertEqual(correlation["sample_count"], 26)
        self.assertAlmostEqual(correlation["coefficient"], 1)
        self.assertEqual(len(self.service.history("sp500")["observations"]), 33)


class ImportTests(unittest.TestCase):
    def observation(self, **changes):
        row = {"factor_id": "sp500", "value": 100, "reported_at": "2026-01-01T12:00:00Z", "source": "Published feed", "source_url": "https://example.com/release"}
        return ObservationInput.model_validate({**row, **changes})
    def test_requires_known_factor_aware_time_and_finite_value(self):
        for changes in ({"factor_id": "fake"}, {"reported_at": "2026-01-01"}, {"value": float("nan")}, {"value": None}, {"value": {"x": float("inf")}}, {"source_url": "javascript:alert(1)"}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.observation(**changes)
    def test_published_observations_cannot_be_future_events(self):
        future = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        with self.assertRaises(ValidationError):
            self.observation(reported_at=future)
        event = EventInput(id="fed-1", title="Meeting", event_at=future, source="Federal Reserve", source_url="https://www.federalreserve.gov/")
        self.assertEqual(event.id, "fed-1")


if __name__ == "__main__":
    unittest.main()
