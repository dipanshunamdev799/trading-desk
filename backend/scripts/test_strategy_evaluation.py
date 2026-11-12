"""Read-only live orchestration and evidence-loading boundaries."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services import strategy_evaluation as service


class SharedGateway:
    """Deliberately exposes only real gateway method names, no mock fallback."""
    def __init__(self):
        self.candle_reads = 0
        self.session_reads = 0

    def get_historical_candles_v3(self, instrument, unit, interval, end, start):
        self.candle_reads += 1
        return {"candles": []}

    def get_market_session(self, instrument):
        self.session_reads += 1
        return {"phase": "open"}


class StrategyEvaluationTests(unittest.TestCase):
    def test_live_evaluation_reads_shared_sources_once_and_never_enables_execution(self):
        gateway = SharedGateway()
        research = ROOT / "artifacts" / "project_alpha" / "alpha-config.json"
        before = research.read_bytes() if research.exists() else None
        with patch("app.services.nifty_service.get_nifty_service") as nifty, \
             patch("app.services.upstox_service.get_upstox", return_value=gateway), \
             patch.object(service, "load_weight_evidence", return_value=(None, None)):
            nifty.return_value.dashboard.return_value = {"sections": [], "events": []}
            result = service.evaluate_live()
            nifty.return_value.dashboard.assert_called_once_with(auto_refresh=False)
        self.assertEqual(gateway.candle_reads, 1)
        self.assertEqual(gateway.session_reads, 1)
        self.assertEqual(result["market_context"]["session_phase"], "open")
        self.assertEqual(len(result["strategies"]), 11)
        self.assertEqual(result["errors"], [])
        for score in result["strategies"]:
            self.assertEqual(score["action"], "NO TRADE")
            self.assertEqual(score["deployment"], "RESEARCH ONLY")
            self.assertIsNone(score["calibrated_probability"])
            self.assertEqual(score["confidence_score"], 0.)
        if before is not None:
            self.assertEqual(research.read_bytes(), before)

    def test_source_failures_remain_visible_and_do_not_remove_profiles(self):
        with patch("app.services.nifty_service.get_nifty_service", side_effect=RuntimeError("fixture")), \
             patch("app.services.upstox_service.get_upstox", side_effect=RuntimeError("fixture")), \
             patch.object(service, "load_weight_evidence", return_value=(None, None)):
            result = service.evaluate_live()
        self.assertEqual(len(result["strategies"]), 11)
        self.assertEqual(len(result["errors"]), 3)
        self.assertTrue(all(score["status"] != "candidate" for score in result["strategies"]))

    def test_optional_evidence_absence_malformed_and_valid_object(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch("app.config.get_settings", return_value=SimpleNamespace(data_dir=Path(directory))):
            self.assertEqual(service.load_weight_evidence(), (None, None))
            path = Path(directory) / "strategy-factor-evidence.json"
            for invalid in ("invalid json", "[]"):
                path.write_text(invalid, encoding="utf-8")
                evidence, error = service.load_weight_evidence()
                self.assertIsNone(evidence)
                self.assertIn("ignored", error)
            payload = {"method": "retrospective_winner", "validated": False}
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(service.load_weight_evidence(), (payload, None))

    def test_route_is_read_only_and_disables_caching(self):
        from fastapi import Response
        from app.routers import strategies
        response = Response()
        with patch.object(strategies, "evaluate_live", return_value={"strategies": []}) as evaluate:
            self.assertEqual(strategies.evaluate(response), {"strategies": []})
            evaluate.assert_called_once_with()
        self.assertEqual(response.headers["cache-control"], "no-store")


if __name__ == "__main__":
    unittest.main()
