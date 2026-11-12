"""Input causality and parity with the frozen directional research rules."""
from __future__ import annotations

import copy
import json
import math
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "scripts")]

from app.services.strategy_context import candle_factors, dashboard_factors, timestamp

IST = timezone(timedelta(hours=5, minutes=30))
AT = datetime(2026, 11, 10, 13, 5, tzinfo=IST)
STAMP = "2026-11-10T13:00:00+05:30"


def generated_candles():
    """Synthetic OHLC used for invariants, never counted as trading evidence."""
    rows = []
    for day_index, day in enumerate(("2026-11-05", "2026-11-06", "2026-11-09", "2026-11-10")):
        start = datetime.fromisoformat(day + "T09:15:00+05:30")
        for i in range(71):
            opened = 25000 + day_index * 40 + i * 1.7 + math.sin(i / 3) * 8
            closed = opened + math.cos(i / 4) * 2
            rows.append({"ts": (start + timedelta(minutes=5*i)).isoformat(), "open": opened,
                         "high": max(opened, closed) + 4, "low": min(opened, closed) - 4,
                         "close": closed, "volume": 0})
    return rows


def reading(key, value, **extra):
    return {"id": key, "label": key, "section_id": "test", "value": value,
            "status": "available", "source": "Synthetic invariant fixture",
            "source_url": "https://example.invalid/test", "reported_at": STAMP,
            "observed_at": STAMP, **extra}


def dashboard(*rows, events=None):
    return {"sections": [{"id": "test", "factors": list(rows)}], "events": events or []}


class CandleContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = generated_candles()

    def test_completed_prefix_is_unchanged_by_later_candles(self):
        prefix = [r for r in self.rows if timestamp(r["ts"]) + timedelta(minutes=5) <= AT]
        before = copy.deepcopy(self.rows)
        complete, context = candle_factors(self.rows, AT)
        truncated, truncated_context = candle_factors(prefix, AT)
        self.assertEqual(complete, truncated)
        self.assertEqual(context, truncated_context)
        self.assertEqual(self.rows, before)
        self.assertTrue(context["current_session_complete_so_far"])
        self.assertTrue(complete["ema_trend"]["available"])

    def test_missing_open_or_internal_bar_invalidates_current_setups(self):
        for missing_clock in ("09:15", "12:00"):
            with self.subTest(missing_clock=missing_clock):
                rows = [r for r in self.rows if r["ts"][:16] != "2026-11-10T" + missing_clock]
                factors, context = candle_factors(rows, AT)
                self.assertFalse(context["current_session_complete_so_far"])
                self.assertFalse(any(f["available"] for f in factors.values()))

    def test_undated_clock_conflicting_revision_and_invalid_ohlc_fail_closed(self):
        for mutation in ("naive", "revision", "ohlc"):
            with self.subTest(mutation=mutation):
                rows = copy.deepcopy(self.rows)
                target = next(r for r in rows if r["ts"][:16] == "2026-11-10T13:00")
                if mutation == "naive":
                    target["ts"] = target["ts"][:19]
                elif mutation == "revision":
                    rows.append({**target, "close": target["close"] + .1})
                else:
                    target["low"] = target["high"] + 1
                factors, context = candle_factors(rows, AT)
                self.assertTrue(context["errors"])
                self.assertFalse(any(f["available"] for f in factors.values()))

    def test_previous_session_cannot_be_current_confirmation(self):
        factors, _ = candle_factors(self.rows, AT + timedelta(days=1))
        self.assertFalse(any(f["available"] for f in factors.values()))

    def test_nan_source_values_never_produce_usable_factors(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["ts"][:16] == "2026-11-10T13:00")["close"] = float("nan")
        factors, context = candle_factors(rows, AT)
        self.assertTrue(context["errors"])
        self.assertFalse(any(f["available"] for f in factors.values()))


class DashboardContextTests(unittest.TestCase):
    def test_stale_future_received_undated_and_quality_rejected_inputs_are_excluded(self):
        value = {"advances": 30, "declines": 20, "universe_size": 50, "available_constituents": 50}
        changes = ({"reported_at": "2026-11-10T12:00:00+05:30"},
                   {"observed_at": "2026-11-10T14:00:00+05:30"},
                   {"reported_at": None}, {"reported_at": "2026-11-10T13:00:00"},
                   {"quality_note": "Source rejected"}, {"source": None})
        fresh, _ = dashboard_factors(dashboard(reading("advance_decline", value)), AT)
        self.assertTrue(fresh["breadth"]["available"])
        self.assertAlmostEqual(fresh["breadth"]["signal"], .2)
        for change in changes:
            with self.subTest(change=change):
                signals, _ = dashboard_factors(dashboard(reading("advance_decline", value, **change)), AT)
                self.assertFalse(signals["breadth"]["available"])

    def test_partial_breadth_is_not_full_universe_confirmation(self):
        row = reading("advance_decline", {"advances": 30, "declines": 19,
                      "universe_size": 50, "available_constituents": 49})
        signals, _ = dashboard_factors(dashboard(row), AT)
        self.assertFalse(signals["breadth"]["available"])

    def test_oi_changes_require_identical_expiry_and_both_timestamps(self):
        call = reading("call_oi_change", 100, expiry="2026-11-17")
        put = reading("put_oi_change", 200, expiry="2026-11-24")
        signals, _ = dashboard_factors(dashboard(call, put), AT)
        self.assertFalse(signals["oi_balance"]["available"])
        put["expiry"] = call["expiry"]
        signals, _ = dashboard_factors(dashboard(call, put), AT)
        self.assertTrue(signals["oi_balance"]["available"])
        self.assertEqual(signals["oi_balance"]["reliability"], 0.)
        put["observed_at"] = "2026-11-10T14:00:00+05:30"
        signals, _ = dashboard_factors(dashboard(call, put), AT)
        self.assertFalse(signals["oi_balance"]["available"])

    def test_max_pain_requires_unexpired_valid_source_expiry(self):
        for expiry in (None, "not-a-date", "2026-11-09"):
            with self.subTest(expiry=expiry):
                signals, _ = dashboard_factors(dashboard(reading("max_pain", 25100, expiry=expiry)), AT, 25000, 20)
                self.assertFalse(signals["max_pain"]["available"])
        signals, _ = dashboard_factors(dashboard(reading("max_pain", 25100, expiry="2026-11-17")), AT, 25000, 20)
        self.assertTrue(signals["max_pain"]["available"])
        self.assertEqual(signals["max_pain"]["reliability"], 0.)

    def test_event_future_receipt_or_missing_provenance_is_not_known_risk(self):
        event = {"id": "fixture", "title": "Synthetic release", "event_at": "2026-11-10T13:30:00+05:30",
                 "impact": "high", "source": "Synthetic calendar", "source_url": "https://example.invalid/calendar",
                 "observed_at": STAMP}
        signals, _ = dashboard_factors(dashboard(events=[event]), AT)
        self.assertTrue(signals["event_risk"]["available"])
        self.assertEqual(signals["event_risk"]["signal"], -1.)
        for change in ({"observed_at": "2026-11-10T14:00:00+05:30"},
                       {"observed_at": None}, {"source": None}, {"source_url": None}):
            with self.subTest(change=change):
                signals, _ = dashboard_factors(dashboard(events=[{**event, **change}]), AT)
                self.assertFalse(signals["event_risk"]["available"])

    def test_empty_calendar_and_daily_technicals_cannot_add_confirmation(self):
        row = reading("ema", {"9": 25000, "21": 24900}, section_id="technicals")
        signals, audit = dashboard_factors(dashboard(row), AT)
        self.assertFalse(signals["event_risk"]["available"])
        self.assertNotIn("ema", signals)
        self.assertIn("Daily technical", next(r["reason"] for r in audit if r["id"] == "input_ema"))
        self.assertFalse(any(r.get("scored") for r in audit))

    def test_overseas_context_uses_prior_return_scale_and_ignores_future_points(self):
        history, value = [], 4000.
        for i in range(22):
            value *= 1.01 if i % 2 else .995
            history.append({"ts": (AT - timedelta(days=22-i)).isoformat(), "value": value})
        row = reading("sp500", value, change_pct=1., history=history)
        signals, _ = dashboard_factors(dashboard(row), AT)
        self.assertTrue(signals["global_markets"]["available"])
        self.assertGreater(signals["global_markets"]["signal"], .5)
        row["history"] = history + [{"ts": (AT + timedelta(days=1)).isoformat(), "value": 1.}]
        after, _ = dashboard_factors(dashboard(row), AT)
        self.assertEqual(signals["global_markets"], after["global_markets"])


class FrozenResearchParityTests(unittest.TestCase):
    def test_all_eleven_setups_match_existing_lab_on_three_observed_prefixes(self):
        source = ROOT / "artifacts" / "directional_research" / "nifty-upstox-5minute.json"
        if not source.exists():
            self.skipTest("Observed research candle artifact not present")
        import pandas as pd
        import research_directional_lab as lab

        # Read the artifact once, then calculate only five complete sessions.
        # Expected signals come from the pre-existing lab, not this adapter.
        raw = json.loads(source.read_text(encoding="utf-8"))
        sessions = {}
        for row in raw:
            if "09:15" <= row["ts"][11:16] < "15:10":
                sessions.setdefault(row["ts"][:10], []).append(row)
        expected_clocks = [(datetime(2000, 1, 1, 9, 15) + timedelta(minutes=5*i)).strftime("%H:%M") for i in range(71)]
        complete = [day for day, rows in sorted(sessions.items())
                    if sorted(r["ts"][11:16] for r in rows) == expected_clocks]
        if len(complete) < 5:
            self.skipTest("Need five complete observed sessions for frozen-rule parity")
        observed = [row for day in complete[-5:] for row in sorted(sessions[day], key=lambda r: r["ts"])]
        frame = pd.DataFrame(observed)
        frame["ts"] = pd.to_datetime(frame.ts, utc=True).dt.tz_convert("Asia/Kolkata")
        frame["day"] = frame.ts.dt.strftime("%Y-%m-%d")
        features = lab.features(frame)
        configurations = {config[1:5]: config[-1] for config in lab.configurations(features) if config[5] == 60}
        profiles = (
            ("ema_trend", "ema_trend", "12_26_gap0.5", "trend", "afternoon"),
            ("failed_breakout", "failed_breakout", "lookback20", "range", "all"),
            ("pullback", "pullback", "ema21_tolerance0.75", "ema_aligned", "afternoon"),
            ("donchian", "donchian", "lookback6_buffer0", "trend", "afternoon"),
            ("momentum", "momentum", "lookback3_atr0.5", "normal_vol", "morning"),
            ("compression", "compression_breakout", "range3_body1", "trend", "afternoon"),
            ("orb", "orb", "minutes15_buffer0.25", "ema_aligned", "afternoon"),
            ("ema_reversion", "ema_reversion", "distance2", "range", "morning"),
            ("gap_continuation", "gap_follow", "gap_atr3", "high_vol", "all"),
            ("gap_fade", "gap_fade", "gap_atr3", "range", "all"),
            ("rsi_reversion", "rsi_reversion", "rsi40_distance0", "range", "morning"),
        )
        rules = {(family, parameter): side for family, parameter, side in lab.rules(features)}
        for clock in ("10:00", "13:00", "14:05"):
            index = features.index[(features.day == complete[-1]) & (features.ts.dt.strftime("%H:%M") == clock)][0]
            decision = features.loc[index, "known_at"]
            actual, context = candle_factors(observed, decision)
            self.assertTrue(context["current_session_complete_so_far"])
            for pid, family, parameter, filter_name, window in profiles:
                with self.subTest(clock=clock, strategy=pid):
                    value = actual["setup_" + pid]["value"]
                    self.assertEqual(value["direction"], int(rules[(family, parameter)][index]))
                    expected = int(configurations[(family, parameter, filter_name, window)][index])
                    self.assertEqual(value["triggered"], expected != 0)


if __name__ == "__main__":
    unittest.main()
