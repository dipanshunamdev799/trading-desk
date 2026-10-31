"""Regression checks for research math, alignment and honest missingness."""
import math
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.nifty_analytics import correlate_series, option_snapshot, technical_snapshot
from app.services.nifty_catalog import FACTORS, FACTOR_MAP, SECTIONS


def bars(count, flat=False):
    start = datetime(2025, 1, 1)
    return [{"ts": (start + timedelta(days=i)).isoformat(), "open": 100 if flat else 100 + i,
             "high": 102 if flat else 102 + i, "low": 99 if flat else 99 + i,
             "close": 100 if flat else 100 + i, "volume": 0, "interval": "1day"}
            for i in range(count)]


def chain():
    result = []
    for strike, call, put in ((90, 10, 30), (100, 20, 20), (110, 30, 10)):
        row = {"strike_price": strike, "underlying_spot_price": 101, "expiry": "2026-10-27"}
        for side, oi, iv, delta in (("call", call, 20, .5), ("put", put, 22, -.5)):
            row[side + "_options"] = {"market_data": {"oi": oi, "prev_oi": oi - 5, "volume": 2 if side == "call" else 3},
                                     "option_greeks": {"iv": iv, "delta": delta, "gamma": 0, "theta": -1, "vega": 2}}
        result.append(row)
    return result


class CatalogTests(unittest.TestCase):
    def test_complete_sections_and_unique_valid_metadata(self):
        self.assertEqual(len(SECTIONS), 10)
        self.assertEqual(len(FACTORS), len(FACTOR_MAP))
        self.assertEqual({section["id"] for section in SECTIONS}, {factor["section_id"] for factor in FACTORS})
        # Every item in the supplied checklist has a home, with the timeframe
        # trend item split into daily/hourly/intraday rows.
        self.assertEqual(len(FACTORS), 127)
        self.assertEqual([sum(factor["section_id"] == section["id"] for factor in FACTORS) for section in SECTIONS], [10, 9, 8, 8, 15, 20, 11, 15, 18, 13])
        for factor in FACTORS:
            with self.subTest(factor=factor["id"]):
                self.assertIn(factor["priority"], {"P1", "P2", "P3", "P4"})
                self.assertIn(factor["kind"], {"driver", "indicator", "context"})
                self.assertGreater(factor["stale_after_seconds"], 0)
                self.assertTrue(factor["description"])
                self.assertTrue(factor["source_url"].startswith("https://"))


class TechnicalTests(unittest.TestCase):
    def test_sort_dedupe_previous_session_and_no_index_volume(self):
        source = bars(55)
        expected = technical_snapshot(source)
        actual = technical_snapshot(list(reversed(source)) + [source[-1], {"ts": "bad", "close": 999}])
        self.assertEqual(actual, expected)
        self.assertEqual(actual["nifty_spot"]["value"], 154)
        self.assertEqual(actual["nifty_spot"]["previous_value"], 153)
        self.assertAlmostEqual(actual["nifty_spot"]["change_pct"], 100 / 153)
        self.assertIsNone(actual["volume"]["value"])
        self.assertIsNone(actual["vwap"]["value"])
        # Positive index aggregate fields do not suddenly establish a traded
        # volume or index VWAP either.
        for row in source:
            row["volume"] = 1000
        self.assertIsNone(technical_snapshot(source)["volume"]["value"])

    def test_warmups_ema_rsi_macd_and_atr(self):
        short = technical_snapshot(bars(14))
        self.assertIsNone(short["rsi"]["value"])
        self.assertIsNone(short["ema"]["value"]["21"])
        self.assertIsNone(short["macd"]["value"])
        self.assertIsNone(short["atr_volatility"]["value"]["atr_14"])
        actual = technical_snapshot(bars(60))
        self.assertEqual(actual["rsi"]["value"], 100)
        self.assertAlmostEqual(actual["ema"]["value"]["21"], 149)
        self.assertIsNone(actual["ema"]["value"]["100"])
        self.assertAlmostEqual(actual["macd"]["value"]["macd"], 7)
        self.assertAlmostEqual(actual["macd"]["value"]["histogram"], 0)
        self.assertAlmostEqual(actual["atr_volatility"]["value"]["atr_14"], 3)
        self.assertEqual(actual["daily_trend"]["value"], "uptrend")
        self.assertIsNone(actual["hourly_trend"]["value"])
        self.assertEqual(technical_snapshot(bars(20, flat=True))["rsi"]["value"], 50)

    def test_breakout_uses_only_previous_completed_bars(self):
        source = bars(21)
        source[-1].update(open=200, high=202, low=199, close=201)
        actual = technical_snapshot(source)
        self.assertEqual(actual["support_resistance"]["value"], {"support": 99, "resistance": 121})
        self.assertEqual(actual["breakouts"]["value"], "breakout")
        self.assertIsNone(actual["market_structure"]["value"])

    def test_intraday_previous_close_and_explicit_proxy_vwap(self):
        source = [{"ts": "2026-10-22T15:29:00+05:30", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 2},
                  {"ts": "2026-10-23T09:15:00+05:30", "open": 103, "high": 106, "low": 102, "close": 104, "volume": 1},
                  {"ts": "2026-10-23T09:16:00+05:30", "open": 104, "high": 109, "low": 103, "close": 106, "volume": 3}]
        for row in source:
            row.update(interval="1minute", instrument_type="FUTIDX")
        actual = technical_snapshot(source)
        self.assertEqual(actual["previous_close"]["value"], 101)
        self.assertEqual(actual["nifty_spot"]["previous_value"], 101)
        expected_vwap = ((106 + 102 + 104) / 3 + (109 + 103 + 106)) / 4
        self.assertAlmostEqual(actual["vwap"]["value"], expected_vwap)
        self.assertIsNone(actual["opening_range"]["value"]["opening_30min"])
        self.assertIsNone(actual["atr_volatility"]["value"]["realised_volatility_20d_pct"])

    def test_invalid_ohlc_and_nonfinite_are_not_indicators(self):
        invalid = bars(1)
        invalid[0]["high"] = 1
        invalid += [{"ts": "2026-01-01", "open": 100, "high": 101, "low": 99, "close": float("nan")}]
        self.assertTrue(all(metric["value"] is None for metric in technical_snapshot(invalid).values()))


class OptionTests(unittest.TestCase):
    def test_complete_chain_math_and_same_strike_skew(self):
        actual = option_snapshot(chain())
        self.assertEqual(actual["pcr"]["value"], 1)
        self.assertEqual(actual["call_oi"]["value"], 60)
        self.assertEqual(actual["put_oi"]["value"], 60)
        self.assertEqual(actual["call_oi_change"]["value"], 15)
        self.assertEqual(actual["put_oi_change"]["value"], 15)
        self.assertEqual(actual["max_pain"]["value"], 100)
        self.assertEqual(actual["max_pain"]["payout_curve"], [{"strike": 90, "payout": 400}, {"strike": 100, "payout": 200}, {"strike": 110, "payout": 400}])
        self.assertEqual(actual["iv"]["value"], 21)
        self.assertEqual(actual["iv_skew"]["value"], 2)
        self.assertEqual(actual["option_volume"]["value"], 15)

    def test_absent_fields_do_not_invent_zero_or_complete_totals(self):
        source = chain()
        del source[0]["call_options"]["market_data"]["oi"]
        del source[1]["put_options"]["market_data"]["prev_oi"]
        del source[2]["put_options"]["option_greeks"]["gamma"]
        actual = option_snapshot(source)
        for key in ("pcr", "call_oi", "call_oi_change", "put_oi_change", "max_pain"):
            self.assertIsNone(actual[key]["value"])
        self.assertIsNone(actual["call_oi"]["strikes"][0]["open_interest"])
        self.assertEqual(actual["option_greeks"]["value"]["strikes"][0]["call"]["gamma"], 0)
        self.assertIsNone(actual["option_greeks"]["value"]["strikes"][2]["put"]["gamma"])

    def test_missing_atm_iv_does_not_substitute_another_strike(self):
        source = chain()
        del source[1]["put_options"]["option_greeks"]["iv"]
        actual = option_snapshot(source)
        self.assertIsNone(actual["iv"]["value"])
        self.assertIsNone(actual["iv_skew"]["value"])

    def test_zero_oi_and_mixed_expiries_are_explicitly_unavailable(self):
        source = chain()
        for row in source:
            row["call_options"]["market_data"]["oi"] = 0
        self.assertIsNone(option_snapshot(source)["pcr"]["value"])
        source[-1]["expiry"] = "2026-11-03"
        self.assertTrue(all(row["value"] is None for row in option_snapshot(source).values()))


class CorrelationTests(unittest.TestCase):
    def series(self, count=30):
        value, start, rows = 100, datetime(2026, 1, 1), []
        for index in range(count):
            value *= 1 + [0.01, -0.02, 0.03, -0.005, 0.015][index % 5]
            rows.append({"ts": (start + timedelta(days=index)).date().isoformat(), "value": value})
        return rows

    def test_returns_correlate_and_duplicate_dates_are_deduped(self):
        left = self.series()
        right = [{**row, "value": row["value"] * 7} for row in left]
        actual = correlate_series(list(reversed(left)) + [left[-1]], right)
        self.assertEqual(actual["sample_count"], 29)
        self.assertAlmostEqual(actual["coefficient"], 1)

    def test_missing_date_does_not_match_multi_day_return_to_daily_return(self):
        left = self.series()
        right = [row for i, row in enumerate(left) if i != 10]
        actual = correlate_series(left, right)
        self.assertEqual(actual["sample_count"], 27)
        self.assertAlmostEqual(actual["coefficient"], 1)

    def test_minimum_sample_and_constant_return_guards(self):
        left = self.series(10)
        self.assertIsNone(correlate_series(left, left)["coefficient"])
        flat = [{**row, "value": 100} for row in self.series()]
        actual = correlate_series(flat, flat)
        self.assertIsNone(actual["coefficient"])
        self.assertIn("constant", actual["note"])


if __name__ == "__main__":
    unittest.main()
