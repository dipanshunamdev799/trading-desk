"""Safety and arithmetic invariants for multi-factor strategy suitability."""
import copy
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.strategy_scoring import PROFILES, score_all, score_strategy

AT = "2026-11-10T13:05:00+05:30"
STAMP = "2026-11-10T13:00:00+05:30"


def factor(key, signal=1., reliability=1.):
    return {"id": key, "label": key, "available": True, "signal": signal,
            "reliability": reliability, "reported_at": STAMP, "source": "test fixture",
            "reason": "Synthetic invariant test; not historical market evidence."}


def complete():
    keys = ["ema_trend", "momentum", "structure", "regime_trend", "max_pain", "pcr",
            "oi_balance", "oi_walls", "breadth", "global_markets", "flows", "event_risk"]
    rows = {key: factor(key) for key in keys}
    rows["setup_ema_trend"] = {**factor("setup_ema_trend"), "value": {"triggered": True, "hard_filter_passed": True}}
    return rows


def directional_evidence(**changes):
    item = {"signal_multiplier": -1., "predictive_reliability": .6,
            "validation_end": "2026-11-09T15:30:00+05:30", "incremental_ci_low": .1,
            "corrected_p_value": .04, "validation_samples": 40}
    item.update(changes)
    return {"method": "chronological_incremental", "validated": True, "source": "synthetic test evidence",
            "known_at": STAMP, "training_end": "2026-10-01T15:30:00+05:30",
            "strategy_factors": {"ema_trend": {"pcr": item}}}


class StrategyScoringTests(unittest.TestCase):
    def test_normalized_weights_and_exact_signed_contributions(self):
        result = score_strategy("ema_trend", complete(), AT)
        self.assertEqual(result["status"], "candidate")
        self.assertAlmostEqual(sum(row["weight"] for row in result["factors"]), 1.)
        self.assertAlmostEqual(sum(row["contribution_points"] for row in result["factors"]), result["score"])
        self.assertAlmostEqual(sum(group["weight"] for group in result["groups"]), 1.)
        self.assertAlmostEqual(result["score"], 100.)
        self.assertAlmostEqual(result["confidence_score"], 100.)
        self.assertIsNone(result["calibrated_probability"])

    def test_opposition_keeps_the_same_weight(self):
        inputs = complete()
        original = score_strategy("ema_trend", inputs, AT)
        inputs["pcr"]["signal"] = -1.
        opposed = score_strategy("ema_trend", inputs, AT)
        before = next(row for row in original["factors"] if row["id"] == "pcr")
        after = next(row for row in opposed["factors"] if row["id"] == "pcr")
        self.assertEqual(before["weight"], after["weight"])
        self.assertAlmostEqual(before["contribution_points"], -after["contribution_points"])
        self.assertEqual(after["stance"], "opposes")
        self.assertLess(opposed["confidence_score"], original["confidence_score"])

    def test_correlated_signals_cannot_expand_domain_budget(self):
        inputs = complete()
        original = score_strategy("ema_trend", inputs, AT)
        inputs["new_ema_alias"] = factor("new_ema_alias")
        more = score_strategy("ema_trend", inputs, AT)
        self.assertEqual(original["confidence_score"], more["confidence_score"])
        self.assertEqual(original["score"], more["score"])
        for group in more["groups"]:
            self.assertAlmostEqual(group["weight"], .25)
        alias = next(row for row in more["factors"] if row["id"] == "new_ema_alias")
        self.assertEqual(alias["stance"], "irrelevant")
        self.assertEqual(alias["weight"], 0.)

    def test_a_single_domain_cannot_create_high_confidence(self):
        inputs = {key: row for key, row in complete().items() if key in {"setup_ema_trend", "ema_trend", "momentum", "structure", "regime_trend"}}
        result = score_strategy("ema_trend", inputs, AT)
        self.assertEqual(result["coverage"], .25)
        self.assertLessEqual(result["confidence_score"], 25.)
        self.assertEqual(result["status"], "insufficient_data")

    def test_missing_and_stale_readings_do_not_disappear_from_quality(self):
        rows = complete()
        before = score_strategy("ema_trend", rows, AT)
        rows["pcr"]["status"] = "stale"
        rows["max_pain"]["available"] = False
        result = score_strategy("ema_trend", rows, AT)
        self.assertLess(result["quality"], before["quality"])
        self.assertLess(result["confidence_score"], before["confidence_score"])
        self.assertEqual(next(row for row in result["factors"] if row["id"] == "pcr")["weight"], 0.)

    def test_future_or_naive_source_timestamp_is_excluded(self):
        rows = complete()
        rows["pcr"]["reported_at"] = "2026-11-10T14:00:00+05:30"
        rows["max_pain"]["reported_at"] = "2026-11-10T13:00:00"
        rows["oi_balance"]["observed_at"] = "2026-11-10T14:00:00+05:30"
        result = score_strategy("ema_trend", rows, AT)
        for row in result["factors"]:
            if row["id"] in {"pcr", "max_pain", "oi_balance"}:
                self.assertEqual(row["weight"], 0.)
                self.assertIn("timestamp", row["reason"])

    def test_future_and_retrospective_evidence_cannot_tune_weights(self):
        rows = complete()
        before = score_strategy("ema_trend", rows, AT)
        evidence = {"method": "chronological_incremental", "validated": True, "source": "synthetic",
                    "known_at": "2026-11-11T13:00:00+05:30", "training_end": STAMP,
                    "strategy_factors": {"ema_trend": {"pcr": {"reliability_multiplier": 0.}}}}
        after = score_strategy("ema_trend", rows, AT, evidence)
        self.assertEqual(before["score"], after["score"])
        self.assertEqual(before["confidence_score"], after["confidence_score"])
        evidence["known_at"] = STAMP
        evidence["method"] = "retrospective_winner"
        after = score_strategy("ema_trend", rows, AT, evidence)
        self.assertEqual(before["confidence_score"], after["confidence_score"])

    def test_valid_causal_incremental_evidence_can_discount_reliability(self):
        rows = complete()
        evidence = {"method": "chronological_incremental", "validated": True, "source": "synthetic",
                    "known_at": STAMP, "training_end": "2026-11-09T15:30:00+05:30",
                    "strategy_factors": {"ema_trend": {"pcr": {"reliability_multiplier": .2}}}}
        result = score_strategy("ema_trend", rows, AT, evidence)
        pcr = next(row for row in result["factors"] if row["id"] == "pcr")
        self.assertAlmostEqual(pcr["reliability"], .2)
        self.assertLess(pcr["weight"], .0625)
        self.assertLess(result["confidence_score"], 100.)

    def test_cross_domain_conflict_penalizes_confidence(self):
        rows = complete()
        for key in ["max_pain", "pcr", "oi_balance", "oi_walls"]:
            rows[key]["signal"] = -1.
        result = score_strategy("ema_trend", rows, AT)
        self.assertAlmostEqual(result["score"], 50.)
        self.assertAlmostEqual(result["conflict"], .5)
        self.assertAlmostEqual(result["confidence_score"], 25.)

    def test_setup_and_frozen_time_filter_cannot_be_overridden_by_score(self):
        rows = complete()
        rows["setup_ema_trend"]["value"]["hard_filter_passed"] = False
        result = score_strategy("ema_trend", rows, AT)
        self.assertEqual(result["status"], "watch")
        rows["setup_ema_trend"]["value"]["triggered"] = False
        result = score_strategy("ema_trend", rows, AT)
        self.assertEqual(result["confidence_score"], 0.)
        result = score_strategy("ema_trend", complete(), "2026-11-10T14:15:00+05:30")
        self.assertEqual(result["status"], "watch")
        self.assertTrue(any("cutoff" in reason for reason in result["reasons"]))

    def test_unavailable_setup_cannot_borrow_options_confidence(self):
        rows = complete()
        rows["setup_ema_trend"]["available"] = False
        result = score_strategy("ema_trend", rows, AT)
        self.assertEqual(result["status"], "insufficient_data")
        self.assertEqual(result["confidence_score"], 0.)

    def test_both_directions_and_all_profiles_are_supported_without_mutation(self):
        rows = complete()
        saved = copy.deepcopy(rows)
        results = score_all(rows, AT)
        self.assertEqual(len(results), 11)
        self.assertEqual(len({p["id"] for p in PROFILES}), 11)
        self.assertEqual(rows, saved)
        for key, value in rows.items():
            if key not in {"regime_trend", "event_risk"}:
                value["signal"] = -value["signal"]
        result = score_strategy("ema_trend", rows, AT)
        self.assertEqual(result["direction"], "bearish")
        self.assertAlmostEqual(result["score"], 100.)

    def test_naive_decision_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            score_all({}, "2026-11-10T13:00:00")

    def test_validated_mapping_can_activate_a_measured_unvalidated_factor(self):
        rows = complete()
        rows["pcr"]["reliability"] = 0.
        rows["pcr"]["measurement_reliability"] = .5
        result = score_strategy("ema_trend", rows, AT, directional_evidence())
        pcr = next(row for row in result["factors"] if row["id"] == "pcr")
        self.assertAlmostEqual(pcr["reliability"], .3)
        self.assertEqual(pcr["signal"], -1.)
        self.assertEqual(pcr["stance"], "opposes")
        self.assertGreater(pcr["weight"], 0.)
        self.assertIsNone(result["calibrated_probability"])

    def test_invalid_predictive_gates_cannot_activate_a_factor(self):
        rows = complete()
        rows["pcr"]["reliability"] = 0.
        invalid_items = [
            {"validation_samples": 29}, {"validation_samples": 30.5}, {"corrected_p_value": .051},
            {"corrected_p_value": -.1}, {"incremental_ci_low": 0.}, {"signal_multiplier": 2.},
            {"predictive_reliability": 1.1}, {"validation_end": "2026-12-01T15:30:00+05:30"},
            {"validation_end": "2026-09-01T15:30:00+05:30"},
        ]
        for changes in invalid_items:
            with self.subTest(changes=changes):
                result = score_strategy("ema_trend", rows, AT, directional_evidence(**changes))
                pcr = next(row for row in result["factors"] if row["id"] == "pcr")
                self.assertEqual(pcr["weight"], 0.)
                self.assertEqual(pcr["stance"], "unavailable")

    def test_validated_mapping_cannot_resurrect_stale_or_missing_measurements(self):
        for change in ({"available": False}, {"ttl_seconds": 1}, {"status": "stale"}, {"source": None}):
            with self.subTest(change=change):
                rows = complete()
                rows["pcr"].update(reliability=0., **change)
                result = score_strategy("ema_trend", rows, AT, directional_evidence())
                pcr = next(row for row in result["factors"] if row["id"] == "pcr")
                self.assertEqual(pcr["weight"], 0.)

    def test_factor_applicability_adjusts_relevance_without_changing_sign(self):
        rows = complete()
        rows["pcr"]["relevance_multiplier"] = .2
        result = score_strategy("ema_trend", rows, AT)
        pcr = next(row for row in result["factors"] if row["id"] == "pcr")
        self.assertAlmostEqual(pcr["raw_relevance"], .1)
        self.assertLess(pcr["weight"], .0625)
        self.assertEqual(pcr["stance"], "supports")

    def test_ema_alignment_is_a_distinct_shared_price_factor(self):
        rows = complete()
        rows["ema_alignment"] = factor("ema_alignment", -1.)
        rows["setup_pullback"] = {**factor("setup_pullback"), "value": {"triggered": True}}
        result = score_strategy("pullback", rows, AT)
        alignment = next(row for row in result["factors"] if row["id"] == "ema_alignment")
        trend = next(row for row in result["factors"] if row["id"] == "ema_trend")
        self.assertEqual(alignment["group"], "price")
        self.assertEqual(alignment["raw_relevance"], 1.)
        self.assertEqual(alignment["stance"], "opposes")
        self.assertEqual(trend["stance"], "irrelevant")

    def test_negligible_quality_domain_has_negligible_influence_in_both_directions(self):
        rows = {key: row for key, row in complete().items() if key in {
            "setup_ema_trend", "ema_trend", "momentum", "structure", "regime_trend"}}
        rows["momentum"]["signal"] = -1.
        before = score_strategy("ema_trend", rows, AT)
        for direction in (1., -1.):
            with self.subTest(direction=direction):
                rows["breadth"] = factor("breadth", direction, .000001)
                result = score_strategy("ema_trend", rows, AT)
                context = next(group for group in result["groups"] if group["id"] == "context")
                self.assertLess(context["weight"], .000001)
                self.assertLess(abs(result["score"] - before["score"]), .001)
                self.assertLess(abs(result["confidence_score"] - before["confidence_score"]), .001)
                self.assertGreater(result["confidence_score"], 0.)

    def test_subnormal_raw_weights_do_not_divide_by_zero(self):
        rows = {key: row for key, row in complete().items() if key in {
            "setup_ema_trend", "ema_trend", "momentum", "structure", "regime_trend"}}
        rows["pcr"] = factor("pcr", 1., 5e-324)
        result = score_strategy("ema_trend", rows, AT)
        self.assertTrue(math.isfinite(result["score"]))
        self.assertTrue(math.isfinite(result["confidence_score"]))
        self.assertAlmostEqual(sum(row["weight"] for row in result["factors"]), 1.)
        rows["setup_ema_trend"]["reliability"] = 5e-324
        for key in ("ema_trend", "momentum", "structure", "regime_trend"):
            rows[key]["available"] = False
        result = score_strategy("ema_trend", rows, AT)
        self.assertEqual(result["status"], "insufficient_data")
        self.assertTrue(math.isfinite(result["confidence_score"]))

    def test_huge_numeric_inputs_are_rejected_without_float_overflow(self):
        rows = complete()
        rows["pcr"]["signal"] = 10**1000
        rows["max_pain"]["reliability"] = 10**1000
        evidence = directional_evidence(validation_samples=10**1000)
        result = score_strategy("ema_trend", rows, AT, evidence)
        self.assertTrue(math.isfinite(result["score"]))
        self.assertTrue(math.isfinite(result["confidence_score"]))
        for row in result["factors"]:
            if row["id"] in {"pcr", "max_pain"}:
                self.assertEqual(row["weight"], 0.)


if __name__ == "__main__":
    unittest.main()
