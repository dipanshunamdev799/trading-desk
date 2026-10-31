"""Deterministic fixtures: timing, coverage, thresholds and independent data failures."""
import asyncio
import os
import sys
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.services.price_action import analyze, CATALOG, IST

START = datetime(2026, 10, 23, 9, 15, tzinfo=IST)
END = START.replace(hour=16)


def bar(index, o, h, l, c):
    return {"ts": (START+timedelta(minutes=index*5)).isoformat(), "open": o, "high": h, "low": l, "close": c}


def wave(count=75):
    import math
    rows = []
    for i in range(count):
        o = 22500 + math.sin(i*.7)*30 + i*.5
        c = 22500 + math.sin((i+1)*.7)*30 + (i+1)*.5
        rows.append(bar(i, o, max(o, c)+3+(i%3)*.75, min(o, c)-3-(i%3)*.75, c))
    return rows


def study(rows, **kwargs):
    return analyze(rows, "5minute", now=END, **kwargs)


class PriceActionTests(unittest.TestCase):
    def test_all_requested_concepts_have_explicit_rules(self):
        self.assertEqual([r["id"] for r in CATALOG], list(range(1, 48)))
        self.assertTrue(all(r["rule"] and r["group"] for r in CATALOG))

    def test_forming_bar_cannot_confirm_orb_or_pattern(self):
        rows = [bar(0, 100, 102, 99, 101), bar(1, 101, 102, 100, 101), bar(2, 101, 103, 100, 102), bar(3, 102, 110, 101, 109)]
        out = analyze(rows, "5minute", now=START+timedelta(minutes=18))
        self.assertEqual(out["completed_bars"], 3)
        self.assertEqual(out["forming_bars"], 1)
        self.assertFalse(any(e["concept"] == 39 for e in out["events"]))
        closed = analyze(rows, "5minute", now=START+timedelta(minutes=20))
        self.assertTrue(any(e["concept"] == 39 and e["known_at"].endswith("09:35:00+05:30") for e in closed["events"]))

    def test_missing_opening_bar_and_incompatible_grain_disable_orb(self):
        rows = wave()
        for result in (study(rows[1:]), analyze(rows, "15minute", now=END, orb_minutes=5)):
            self.assertFalse(any(l["concept"] == 39 for l in result["lines"]))
            self.assertTrue(any("Opening range unavailable" in n for n in result["notes"]))

    def test_future_or_other_session_candles_do_not_supply_patterns(self):
        self.assertEqual(study(wave(), session="2026-10-22")["events"], [])
        self.assertEqual(analyze(wave(), "5minute", now=START-timedelta(minutes=1))["completed_bars"], 0)

    def test_bad_ohlc_duplicate_and_naive_time(self):
        original = bar(0, 100, 102, 99, 101)
        rows = [original, original, {**original, "ts": "2026-10-23T09:20:00"}, bar(2, 100, 99, 98, 100), bar(3, 100, float("inf"), 99, 100), bar(4, True, 102, 99, 100)]
        out = study(rows)
        self.assertEqual(out["completed_bars"], 1)

    def test_daily_levels_never_use_same_or_future_day(self):
        daily = [{**bar(0, 100, 120, 80, 110), "ts": (START-timedelta(days=1)).isoformat()}, bar(0, 100, 999, 1, 110)]
        result = study(wave(), daily=daily)
        self.assertEqual(result["previous_session"], "2026-10-22")
        self.assertEqual([x["points"][0]["value"] for x in result["lines"] if x["concept"] in (7, 8)], [120, 80])
        result = study(wave(), daily=[])
        self.assertIsNone(result["previous_session"])
        self.assertFalse(any(l["concept"] in (7, 8) for l in result["lines"]))

    def test_no_lookahead_for_every_prefix_or_pivot_timestamp(self):
        rows = wave()
        full = study(rows)
        for n in range(5, len(rows)):
            prefix = study(rows[:n])
            expected = [e for e in full["events"] if e["ts"] <= rows[n-1]["ts"]]
            self.assertEqual(prefix["events"], expected, f"future bars revised events for prefix {n}")
        swings = [e for e in full["events"] if e["label"] in ("HH", "HL", "LH", "LL")]
        self.assertTrue(swings)
        self.assertTrue(all(datetime.fromisoformat(e["known_at"])-datetime.fromisoformat(e["ts"]) == timedelta(minutes=5) for e in swings))

    def test_gap_does_not_create_fvg_or_three_candle_star(self):
        out = study([bar(0, 100, 102, 99, 101), bar(1, 101, 103, 100, 102), bar(3, 108, 110, 107, 109)])
        self.assertEqual(out["missing_bars"], 1)
        self.assertFalse(any(e["concept"] in (29, 30, 44) for e in out["events"]))

    def test_fvg_waits_for_third_close_and_mitigation_for_later_bar(self):
        rows = [bar(0, 100, 102, 99, 101), bar(1, 101, 108, 100, 107), bar(2, 107, 110, 106, 109), bar(3, 109, 110, 104, 105), bar(4, 105, 106, 101, 103)]
        out = study(rows)
        gap = next(z for z in out["zones"] if z["concept"] == 44)
        self.assertEqual((gap["low"], gap["high"]), (102, 106))
        self.assertEqual(gap["start"], rows[2]["ts"])
        self.assertEqual(gap["end"], rows[4]["ts"])
        self.assertFalse(gap["active"])
        retests = [e for e in out["events"] if e["concept"] == 47]
        self.assertEqual(len(retests), 1)
        self.assertEqual(retests[0]["ts"], rows[3]["ts"])

    def test_engulfing_requires_preceding_trend(self):
        rows = [bar(0, 108, 110, 106, 107), bar(1, 107, 108, 103, 104), bar(2, 104, 105, 101, 102), bar(3, 101, 108, 100, 107)]
        matches = [e for e in study(rows)["events"] if e["concept"] == 21]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["ts"], rows[-1]["ts"])
        self.assertFalse(any(e["concept"] == 21 for e in study(rows[2:])["events"]))

    def test_break_retest_and_false_break_use_later_closed_candle(self):
        daily = [{**bar(0, 90, 100, 80, 95), "ts": (START-timedelta(days=1)).isoformat()}]
        rows = [bar(0, 98, 100, 97, 99), bar(1, 99, 105, 99, 104), bar(2, 104, 105, 100, 103), bar(3, 103, 104, 98, 99)]
        out = study(rows, daily=daily)
        retests = [e for e in out["events"] if e["concept"] == 13]
        self.assertEqual([e["ts"] for e in retests], [rows[2]["ts"]])
        failed = study(rows[:2]+[bar(2, 104, 105, 97, 98)], daily=daily)
        self.assertTrue(any(e["concept"] == 15 and e["ts"] == rows[2]["ts"] for e in failed["events"]))

    def test_running_day_high_does_not_draw_final_high_into_past(self):
        rows = [bar(0, 100, 102, 99, 101), bar(1, 101, 110, 100, 109)]
        out = study(rows)
        highs = next(l["points"] for l in out["lines"] if l["label"] == "Day high")
        self.assertEqual([p["value"] for p in highs], [102, 110])

    def test_daily_and_weekly_are_explicitly_not_intraday_studies(self):
        out = analyze(wave(), "1day", now=END)
        self.assertEqual(out["events"], [])
        self.assertIn("intraday", out["notes"][0])

    def test_daily_reference_failure_does_not_erase_intraday_chart(self):
        from app.routers.nifty import price_action_chart
        rows = [SimpleNamespace(**{**b, "ts": datetime.fromisoformat(b["ts"]), "volume": None, "oi": None}) for b in wave()]
        with patch("app.routers.nifty.market_data.get_candles", new=AsyncMock(side_effect=[(rows, "db"), RuntimeError("daily offline")])):
            result = asyncio.run(price_action_chart(interval="5minute", from_date="2026-10-23", to_date="2026-10-23", session="2026-10-23", orb_minutes=15, round_step=100, db=None))
        self.assertEqual(result["count"], 75)
        self.assertTrue(result["study"]["events"])
        self.assertIsNone(result["study"]["previous_session"])

    def test_head_shoulders_and_inverse_need_later_neckline_break(self):
        prices = [100, 102, 105, 102, 98, 95, 98, 104, 110, 104, 98, 95, 98, 103, 105, 102, 99, 96, 90]
        for n, values in [(17, prices), (18, [210-p for p in prices])]:
            rows = [bar(i, v, v+.5, v-.5, v) for i, v in enumerate(values)]
            self.assertFalse(any(e["concept"] == n for e in study(rows[:-1])["events"]))
            self.assertTrue(any(e["concept"] == n and e["ts"] == rows[-1]["ts"] for e in study(rows)["events"]))

    def test_triangle_requires_three_confirmed_pairs_and_closed_boundary_break(self):
        prices = [100, 105, 110, 104, 98, 95, 98, 105, 110, 107, 103, 100, 104, 108, 110, 108, 106, 105, 106, 108, 112]
        for n, values in [(36, prices), (37, [210-p for p in prices])]:
            rows = [bar(i, v, v+.5, v-.5, v) for i, v in enumerate(values)]
            self.assertFalse(any(e["concept"] == n for e in study(rows[:-1])["events"]))
            self.assertTrue(any(e["concept"] == n for e in study(rows)["events"]))


if __name__ == "__main__":
    unittest.main()
