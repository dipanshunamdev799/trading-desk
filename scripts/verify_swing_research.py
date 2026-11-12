"""Independently reconcile frozen swing-research journals and research coverage.

Run after the full study and any report/CI corrections have finished:
    .venv/Scripts/python.exe scripts/verify_swing_research.py
Only journals named by frozen-selection.json are used; old smoke files cannot
silently enter the checks. This script never modifies trading/research inputs.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.swing.signals import catalog, make_signals
from research.swing.validation import trade_uncertainty

TZ = "Asia/Kolkata"
INITIAL = 1_000_000.0
RISK = .005
PARTS = {"development": ("2024-11-10", "2025-11-10"),
         "validation": ("2025-11-10", "2026-05-10"),
         "final": ("2026-05-10", "2026-11-10"),
         "two_year": ("2024-11-10", "2026-11-10")}


def timestamp(value):
    ts = pd.Timestamp(value)
    return ts.tz_localize(TZ) if ts.tzinfo is None else ts.tz_convert(TZ)


def close(actual, expected, label, atol=1e-6):
    if not np.isclose(float(actual), float(expected), rtol=1e-10, atol=atol):
        raise AssertionError(f"{label}: {actual} != {expected}")


def read_bars(path):
    d = pd.read_csv(path)
    d.index = pd.to_datetime(d.pop("ts"), utc=True).dt.tz_convert(TZ)
    assert d.index.is_monotonic_increasing and not d.index.has_duplicates
    return d


def entry_fee(entry, quantity, side, date, instrument):
    """Independent entry-only fee calculation for the declared study models."""
    turnover = entry * quantity
    if instrument == "NIFTY":
        return turnover * .0005
    assert side == 1, "Cash ETFs cannot have overnight short positions"
    early = date < timestamp("2026-03-01")
    exchange = turnover * (.0000297 if early else .0000307)
    sebi = turnover * .000001
    ipft = turnover * (.000001 if early else .000000001)
    brokerage = 20.0
    return brokerage + exchange + sebi + ipft + turnover * .00015 + .18 * (brokerage + exchange + sebi + ipft)


def verify_journal(out, stem, instrument, part, execution, expected_metrics):
    equity_path = out / f"{stem}-equity.csv"
    assert equity_path.exists(), f"Missing frozen equity journal {equity_path}"
    eq = pd.read_csv(equity_path)
    eq.index = pd.to_datetime(eq.iloc[:, 0], utc=True).dt.tz_convert(TZ)
    lo, hi = map(timestamp, PARTS[part])
    assert eq.index.is_monotonic_increasing and not eq.index.has_duplicates
    assert (eq.index > lo).all() and (eq.index <= hi).all()
    assert np.isfinite(eq.equity).all() and (eq.equity > 0).all()
    expected_marks = execution.index[(execution.index >= lo) & (execution.index < hi)] + pd.Timedelta(minutes=5)
    assert eq.index.equals(expected_marks), f"{stem} omits or invents execution-bar equity marks"
    trade_path = out / f"{stem}-trades.csv"
    if int(expected_metrics.n_trades) == 0:
        # An earlier smoke run may have left an unused same-named trade file.
        close(eq.equity.iloc[-1], INITIAL, f"{stem} zero-trade equity")
        return {"stem": stem, "trades": 0, "special_exit_trades": 0,
                "total_net_profit": 0.0, "initial_risk_max_fraction": 0.0}, pd.DataFrame()
    assert trade_path.exists(), f"Missing frozen trade journal {trade_path}"
    trades = pd.read_csv(trade_path)
    for col in ("signal_time", "entry_time", "exit_time"):
        trades[col] = pd.to_datetime(trades[col], utc=True).dt.tz_convert(TZ)
    assert len(trades) == int(expected_metrics.n_trades), f"{stem} trade count mismatch"
    assert (trades.entry_time >= trades.signal_time).all(), f"{stem} entry before signal availability"
    assert (trades.signal_time >= lo).all()
    assert (trades.entry_time >= lo).all() and (trades.entry_time < hi).all()
    assert (trades.exit_time >= trades.entry_time).all() and (trades.exit_time <= hi).all()
    assert trades.entry_time.is_monotonic_increasing
    if len(trades) > 1:
        assert (trades.entry_time.iloc[1:].to_numpy() >= trades.exit_time.iloc[:-1].to_numpy()).all(), f"{stem} overlapping positions"
    close(trades.net_pnl.sum(), float(expected_metrics.net_profit), f"{stem} metrics/trade PnL")
    close(eq.equity.iloc[-1], INITIAL + trades.net_pnl.sum(), f"{stem} final equity/trade PnL")
    close((eq.equity.iloc[-1] / INITIAL - 1) * 100,
          expected_metrics.total_return_pct, f"{stem} return percentage")
    peaks = np.maximum.accumulate(np.r_[INITIAL, eq.equity.to_numpy(float)])[1:]
    close(np.max(1 - eq.equity.to_numpy(float) / peaks) * 100,
          expected_metrics.max_drawdown_pct, f"{stem} marked drawdown")
    cash = INITIAL
    maximum_risk = 0.0
    grid = execution.index
    for trade in trades.itertuples(index=False):
        qty = float(trade.quantity)
        assert qty > 0 and qty == int(qty), f"{stem} noninteger position"
        assert trade.side in (-1, 1)
        risk = float(trade.initial_cash_risk)
        assert 0 < risk <= cash * RISK + 1e-5, f"{stem} planned cash risk exceeds budget"
        maximum_risk = max(maximum_risk, risk / cash)
        fee = entry_fee(trade.entry, int(qty), trade.side, trade.entry_time, instrument)
        assert trade.entry * qty + fee <= cash + 1e-5, f"{stem} unlevered capital constraint"
        where = int(grid.searchsorted(trade.signal_time, side="left"))
        assert where < len(grid) and grid[where] == trade.entry_time, f"{stem} fill is not first tradable open"
        close(trade.side * (trade.exit - trade.entry) * qty,
              trade.gross_pnl, f"{stem} weighted exit gross PnL")
        close(trade.gross_pnl - trade.fees, trade.net_pnl, f"{stem} net PnL after all partial legs")
        close(trade.net_pnl / risk, trade.net_r, f"{stem} net R denominator")
        assert trade.fees >= 0
        cash += trade.net_pnl
    close(cash, eq.equity.iloc[-1], f"{stem} sequential flat equity")
    return {"stem": stem, "trades": len(trades), "total_net_profit": float(trades.net_pnl.sum()),
            "initial_risk_max_fraction": maximum_risk}, trades


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "swing_research")
    args = parser.parse_args()
    out = args.output
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    protocol = json.loads((out / "protocol.json").read_text(encoding="utf-8"))
    frozen = json.loads((out / "frozen-selection.json").read_text(encoding="utf-8"))
    metrics = pd.read_csv(out / "all-period-metrics.csv")
    continuous = pd.read_csv(out / "finalist-two-year-metrics.csv")
    finals = pd.read_csv(out / "final-all-variants-descriptive.csv")
    configs = catalog()
    assert len(configs) == 207 == summary["configurations"] == len(protocol["configs"])
    assert {c["id"] for c in configs} == {c["id"] for c in protocol["configs"]}
    assert protocol["configs"] == configs, "Catalog parameters differ from frozen protocol"
    instruments = summary["instruments"]
    assert set(instruments) == {"NIFTY", "NIFTYBEES", "BANKBEES"}
    expected_keys = {(instrument, c["id"], part)
                     for instrument in instruments for c in configs for part in ("development", "validation", "final")}
    actual_keys = set(map(tuple, metrics[["instrument", "id", "part"]].to_numpy()))
    assert len(metrics) == len(expected_keys) == 207 * 3 * 3
    assert actual_keys == expected_keys and not metrics[["instrument", "id", "part"]].duplicated().any()
    assert frozen["frozen_before_final"] is True
    config_by_id = {c["id"]: c for c in protocol["configs"]}
    selected = [row["id"] for row in frozen["family_finalists"]]
    assert len(selected) == len(set(selected))
    assert len({row["family"] for row in frozen["family_finalists"]}) == len(selected)
    assert frozen["top_three"] == selected[:3] == summary["top_three"]
    for row in frozen["family_finalists"]:
        assert row["config"] == config_by_id[row["id"]]
        assert row["family"] == config_by_id[row["id"]]["family"]
    final_ids = set(selected) | {frozen["fixed_baseline"]}
    journals, bootstrap_checks, causal_checks, ci_mismatches = [], [], [], []
    total_trades = 0
    for instrument in instruments:
        regular = read_bars(out / f"{instrument.lower()}-5minute.csv")
        special = read_bars(out / f"{instrument.lower()}-special-execution.csv")
        execution = pd.concat([regular, special]).sort_index()
        assert not execution.index.has_duplicates
        special_days = set(special.index.normalize())
        for part, ids in (("final", final_ids), ("two_year", set(selected))):
            source = metrics.loc[metrics.part == "final"] if part == "final" else continuous
            for ident in sorted(ids):
                row = source.loc[(source.instrument == instrument) & (source.id == ident)].iloc[0]
                stem = f"finalists/{instrument}-{ident}-{'final' if part == 'final' else 'two-year'}"
                checked, trades = verify_journal(out, stem, instrument, part, execution, row)
                special_count = int(trades.exit_time.dt.normalize().isin(special_days).sum()) if len(trades) else 0
                checked["special_exit_trades"] = special_count
                journals.append(checked)
                total_trades += checked["trades"]
                if part == "final":
                    lo, hi = map(timestamp, PARTS["final"])
                    sessions = execution.index[(execution.index >= lo) & (execution.index < hi)].normalize().unique()
                    if len(trades):
                        assert trades.exit_time.dt.normalize().isin(sessions).all(), "Bootstrap calendar drops executed exits"
                    estimate = trade_uncertainty(trades, sessions)
                    raw_ci = finals.loc[(finals.instrument == instrument) & (finals.id == ident)].iloc[0].r_ci95
                    if isinstance(raw_ci, str):
                        try:
                            stored_ci = json.loads(raw_ci)
                        except json.JSONDecodeError:
                            stored_ci = ast.literal_eval(raw_ci)
                    else:
                        stored_ci = raw_ci
                    for actual, expected in zip(stored_ci, estimate["r_ci95"]):
                        if expected is None:
                            assert actual is None
                        else:
                            if not np.isclose(float(actual), float(expected), rtol=1e-10, atol=1e-10):
                                ci_mismatches.append({"stem": stem, "stored": actual, "expected": expected})
                    bootstrap_checks.append({"instrument": instrument, "id": ident,
                                             "sessions": len(sessions), "special_exit_trades": special_count})
        baseline = make_signals(regular, config_by_id[frozen["fixed_baseline"]])
        known = baseline.htf_available_at.dropna()
        assert (known <= known.index).all(), "Future HTF confirmation used"
        # Recompute a truncated real-data history independently of future rows.
        cutoff = timestamp("2026-02-11 12:40")
        prefix = make_signals(regular.loc[regular.index + pd.Timedelta(minutes=5) <= cutoff].copy(),
                              config_by_id[frozen["fixed_baseline"]])
        pd.testing.assert_frame_equal(baseline.loc[prefix.index], prefix)
        causal_checks.append({"instrument": instrument, "completed_htf_rows": len(known),
                              "prefix_rows_compared": len(prefix)})
    assert not ci_mismatches, f"{len(ci_mismatches)} CI endpoints differ from execution-calendar recomputation; first: {ci_mismatches[:1]}"
    result = {"passed": True, "verified_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
              "configurations": 207, "instruments": instruments, "metric_rows": len(metrics),
              "frozen_family_finalists": len(selected), "journals_checked": len(journals),
              "aggregate_trade_records_checked": total_trades,
              "checks": ["catalog and full metric cube", "frozen candidate identity",
                         "next tradable open and timestamp ordering", "nonoverlapping positions",
                         "integer units and unlevered fee-inclusive capital cap",
                         "planned initial risk <=0.5% previous flat equity",
                         "weighted partial exits and fee/net R reconciliation",
                         "segment boundaries and terminal equity reconciliation",
                         "marked equity drawdown", "special-session-aware final bootstrap",
                         "completed HTF availability and real-data prefix invariance"],
              "causal_samples": causal_checks, "bootstrap_checks": bootstrap_checks,
              "journals": journals,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Checks reconcile frozen selected journals and all metric-row coverage. They cannot certify unobserved intrabar sequencing, historical quote liquidity, corporate-action adjustments, or an untouched historical holdout."}
    (out / "verification.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("passed", "configurations", "metric_rows", "journals_checked", "aggregate_trade_records_checked")}), flush=True)


if __name__ == "__main__":
    main()
