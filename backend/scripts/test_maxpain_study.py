"""Forward-only targets, observed expiries, coverage and statistical safeguards."""
import csv
import io
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.services import maxpain_study as study
from app.services.backtest_service import normalize_backtest

def chain(later=False):
    return {"symbol": "NIFTY", "expiry": "2026-10-22", "contracts": [
        ["C100", 100, "CE", 1 if later else 1000, 1, 1, 1], ["P100", 100, "PE", 1, 1, 1, 1],
        ["C120", 120, "CE", 1, 1, 1, 1], ["P120", 120, "PE", 1000 if later else 1, 1, 1, 1]]}

def data():
    daily = {"2026-10-21": {"chains": [chain()], "spots": {"NIFTY": [110]}},
             "2026-10-22": {"chains": [chain(True)], "spots": {"NIFTY": [105]}}}
    prices = {"NIFTY": {"2026-10-21": {"open": 109, "high": 113, "low": 90, "close": 110},
                        "2026-10-22": {"open": 112, "high": 116, "low": 104, "close": 105}}}
    return daily, prices

class StudyTests(unittest.TestCase):
    def analyze(self, daily, prices):
        with patch.object(study, "UNIVERSE", [("NIFTY", "Nifty", "NSE_INDEX|Nifty 50")]), \
             patch.object(study, "HORIZONS", (1,)):
            return study.analyze(daily, prices, "2026-10-20", "2026-10-23")

    def test_target_uses_prior_oi_and_next_open_never_future_max_pain(self):
        daily, prices = data()
        result = self.analyze(daily, prices)
        row = result["observations"][0]
        self.assertEqual(study.chain_target(chain(True))["target"], 120)
        self.assertEqual(row["target"], 100)
        self.assertEqual(row["entry_open"], 112)
        self.assertEqual(row["entry_date"], "2026-10-22")
        self.assertEqual(row["snapshot_date"], "2026-10-21")
        self.assertTrue(row["closer"])
        self.assertFalse(row["mirror_closer"])
        self.assertFalse(row["range_reached_target"], "Pre-entry day's low must not count as a future touch")

    def test_moving_toward_then_overshooting_does_not_count_as_finishing_closer(self):
        prices = {"2026-10-22": {"open": 90, "high": 116, "low": 89, "close": 115}}
        row = study.observation("NIFTY", "Nifty", "key", "2026-10-22", "2026-10-21", "2026-10-22", 1, {"target": 100}, prices)
        self.assertTrue(row["moved_toward"])
        self.assertFalse(row["closer"])
        self.assertTrue(row["range_reached_target"])

    def test_already_at_target_is_not_an_automatic_win(self):
        prices = {"2026-10-22": {"open": 100, "high": 102, "low": 99, "close": 100}}
        row = study.observation("NIFTY", "Nifty", "key", "2026-10-22", "2026-10-21", "2026-10-22", 1, {"target": 100}, prices)
        self.assertIsNone(row["closer"])
        summary = study.summarize([row])
        self.assertEqual(summary["n"], 0)
        self.assertEqual(summary["already_at_target"], 1)
        self.assertIsNone(summary["closer_rate"])

    def test_missing_files_wrong_prices_and_contract_adjustments_are_counted(self):
        for reason in ("missing_nse_file", "underlying_close_not_corroborated", "contract_strike_or_lot_adjustment"):
            with self.subTest(reason=reason):
                daily, prices = data()
                if reason == "missing_nse_file": del daily["2026-10-21"]
                elif reason == "underlying_close_not_corroborated": daily["2026-10-22"]["spots"]["NIFTY"] = [106]
                else: daily["2026-10-22"]["chains"][0]["contracts"][0][4] = 2
                result = self.analyze(daily, prices)
                self.assertEqual(result["observations"], [])
                self.assertEqual(result["exclusion_reasons"][reason], 1)

    def test_missing_and_duplicate_option_sides_never_become_zero_oi(self):
        incomplete = chain(); incomplete["contracts"].pop()
        with self.assertRaisesRegex(ValueError, "missing_strike_side"): study.chain_target(incomplete)
        duplicate = chain(); duplicate["contracts"].append(duplicate["contracts"][0])
        with self.assertRaisesRegex(ValueError, "duplicate_strike_side"): study.chain_target(duplicate)

    def test_cluster_bootstrap_is_reproducible_and_requires_distinct_expiries(self):
        rows = [{"expiry": f"2026-10-{index+1:02}", "closer": index % 2 == 0, "mirror_closer": index % 3 == 0} for index in range(12)]
        self.assertEqual(study.bootstrap(rows), study.bootstrap(rows))
        self.assertIsNone(study.bootstrap([{**row, "expiry": "2026-10-01"} for row in rows]))

    def test_unpaired_contracts_are_separate_sensitivity_not_strict_evidence(self):
        daily, prices = data()
        daily["2026-10-21"]["chains"][0]["contracts"].pop()
        result = self.analyze(daily, prices)
        strict = next(row for row in result["groups"] if row["coverage_mode"] == "strict" and row["proximity"] == "all")
        sensitivity = next(row for row in result["groups"] if row["coverage_mode"] == "published" and row["proximity"] == "all")
        self.assertEqual(strict["summary"]["n"], 0)
        self.assertEqual(sensitivity["summary"]["n"], 1)
        self.assertEqual(result["observations"][0]["unpaired_strikes"], 1)
        self.assertFalse(result["observations"][0]["strict_eligible"])

    def test_daily_parser_requires_exact_date_and_preserves_real_zero_oi(self):
        headers = ["TradDt", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "OpnIntrst", "FinInstrmId", "UndrlygPric", "NewBrdLotQty"]
        def archive(day):
            stream = io.StringIO(); writer = csv.writer(stream)
            writer.writerow(headers); writer.writerow([day,"NIFTY","2026-10-22",100,"CE",0,"C100",110,65])
            output = io.BytesIO()
            with zipfile.ZipFile(output, "w") as zipped: zipped.writestr("data.csv", stream.getvalue())
            return output.getvalue()
        result = study.parse_bhavcopy(archive("2026-10-21"), "2026-10-21")
        self.assertEqual(result["chains"][0]["contracts"][0][3], 0)
        self.assertEqual(len(result["sha256"]), 64)
        with self.assertRaisesRegex(ValueError, "different trading date"):
            study.parse_bhavcopy(archive("2026-10-20"), "2026-10-21")

    def test_research_report_is_not_normalized_into_fake_trades_or_returns(self):
        raw = {"name": "Research", "metrics": {"kind": "max_pain_convergence"}, "research": {"groups": []}}
        result = normalize_backtest(Path("study.json"), raw)
        self.assertEqual(result["research"], {"groups": []})
        self.assertEqual(result["trades"], [])
        self.assertNotIn("total_return", result["metrics"])

if __name__ == "__main__": unittest.main()
