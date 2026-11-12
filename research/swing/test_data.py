"""Data chronology and special-session preservation checks; no network or skips.

Run ``.venv/Scripts/python.exe -m unittest research.swing.test_data -v``.
"""
from pathlib import Path
import unittest

import pandas as pd

from research.swing.data import SPECIAL_SESSION_DATES, _frame, special_execution_bars, validate_sessions


class DataValidationTests(unittest.TestCase):
    def frame(self, index):
        return pd.DataFrame({"open": 100., "high": 101., "low": 99.,
                             "close": 100., "volume": 10., "oi": 0.}, index=index)

    def test_missing_offline_instrument_returns_empty_audited_frames(self):
        frame = _frame([])
        clean, audit = validate_sessions(frame, "2023-01-01", "2026-11-10")
        special, special_audit = special_execution_bars(frame, clean, "2023-01-01", "2026-11-10")
        self.assertTrue(clean.empty and special.empty)
        self.assertEqual(audit["rows"], 0)
        self.assertEqual(special_audit["rows"], 0)

    def test_regular_requires_all_75_bars(self):
        idx = pd.date_range("2026-11-09 09:15", periods=75, freq="5min", tz="Asia/Kolkata", name="ts")
        frame = self.frame(idx)
        self.assertEqual(len(validate_sessions(frame, "2026-11-01", "2026-11-10")[0]), 75)
        self.assertTrue(validate_sessions(frame.iloc[:-1], "2026-11-01", "2026-11-10")[0].empty)

    def test_regular_rejects_invalid_ohlc_and_asof_day(self):
        idx = pd.date_range("2026-11-09 09:15", periods=75, freq="5min", tz="Asia/Kolkata", name="ts")
        frame = self.frame(idx)
        self.assertTrue(validate_sessions(frame, "2026-11-01", "2026-11-09")[0].empty)
        frame.iloc[2, frame.columns.get_loc("high")] = 98
        self.assertTrue(validate_sessions(frame, "2026-11-01", "2026-11-10")[0].empty)

    def test_special_keeps_evening_and_post1530_but_not_ordinary_strays(self):
        idx = pd.DatetimeIndex(["2024-11-01 18:00", "2024-11-01 18:00", "2024-11-01 18:05",
                                "2026-11-09 16:00", "2026-11-08 15:30"], tz="Asia/Kolkata", name="ts")
        frame = self.frame(idx)
        frame.iloc[2, frame.columns.get_loc("high")] = 98
        regular = frame.iloc[[3]].copy()
        special, audit = special_execution_bars(frame, regular, "2023-01-01", "2026-11-10")
        self.assertEqual(len(special), 2)
        self.assertTrue(special.index.is_unique)
        self.assertEqual(set(special.index.strftime("%Y-%m-%d")), {"2024-11-01", "2026-11-08"})
        self.assertEqual((special.index[-1].hour, special.index[-1].minute), (15, 30))
        self.assertEqual(audit["invalid_ohlc_excluded"], 1)
        self.assertEqual(len(special_execution_bars(frame, regular, "2023-01-01", "2026-11-08")[0]), 1)

    def test_saved_special_sessions_preserve_all_observed_rows(self):
        out = Path(__file__).resolve().parents[2] / "artifacts" / "swing_research"
        expected = {"2023-11-12": 12, "2024-03-02": 21, "2024-05-18": 21,
                    "2024-11-01": 12, "2025-10-21": 12, "2026-11-08": 14}
        for symbol in ("nifty", "niftybees", "bankbees"):
            with self.subTest(symbol=symbol):
                frame = pd.read_csv(out / f"{symbol}-special-execution.csv")
                stamp = pd.to_datetime(frame.ts, utc=True).dt.tz_convert("Asia/Kolkata")
                self.assertEqual(len(frame), 92)
                self.assertTrue(stamp.is_unique and stamp.is_monotonic_increasing)
                self.assertEqual(frame.groupby(stamp.dt.strftime("%Y-%m-%d")).size().to_dict(), expected)
                self.assertTrue((stamp.dt.hour >= 18).any())
                self.assertTrue(set(stamp.dt.strftime("%Y-%m-%d")).issubset(SPECIAL_SESSION_DATES))


if __name__ == "__main__":
    unittest.main()
