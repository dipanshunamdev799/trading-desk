"""Extend frozen swing research with continuous two-year evidence for every rule.

This script never selects candidates or edits selected/finalist results. It uses
the exact protocol configurations and reads existing audited local candle files.
Run after the main research protocol and frozen selection have been written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.swing.engine import simulate
from research.swing.signals import clear_cache, make_signals

OUT = ROOT / "artifacts" / "swing_research"
START, END, TZ = "2024-11-10", "2026-11-10", "Asia/Kolkata"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_candles(path):
    frame = pd.read_csv(path)
    frame["ts"] = pd.to_datetime(frame.ts, utc=True).dt.tz_convert(TZ)
    frame = frame.set_index("ts").sort_index()
    if frame.index.has_duplicates:
        raise ValueError(f"Duplicate timestamps in {Path(path).name}")
    return frame


def _trade_signature(frame):
    columns = [col for col in ["signal_time", "entry_time", "exit_time", "side", "entry", "exit", "quantity", "stop", "target", "net_pnl", "net_r", "reason"] if col in frame]
    return hashlib.sha256(frame[columns].to_csv(index=False).encode()).hexdigest()


def _subgroups(trades, instrument, config):
    if trades.empty:
        return []
    t = trades.copy()
    # Calendar year is assigned by realized exit; regime is causal entry regime.
    t["year"] = pd.to_datetime(t.exit_time, utc=True).dt.tz_convert(TZ).dt.year
    t["side_label"] = t.side.map({1: "long", -1: "short"})
    rows = []
    dimensions = [("year", ["year"]), ("regime", ["regime"]),
                  ("side", ["side_label"]), ("reason", ["reason"]),
                  ("year_regime_side", ["year", "regime", "side_label"])]
    for label, keys in dimensions:
        for values, group in t.groupby(keys, dropna=False, sort=True):
            values = values if isinstance(values, tuple) else (values,)
            row = {"instrument": instrument, "id": config["id"], "family": config["family"],
                   "group_type": label, "year": "all", "regime": "all", "side": "all", "reason": "all",
                   "n_trades": len(group), "expectancy_r": float(group.net_r.mean()),
                   "net_profit": float(group.net_pnl.sum()), "win_rate_pct": float(group.net_pnl.gt(0).mean() * 100)}
            row.update({"side" if key == "side_label" else key: value for key, value in zip(keys, values)})
            rows.append(row)
    return rows


def _monthly(equity, trades, instrument, config):
    if equity.empty:
        return []
    month_key = equity.index.strftime("%Y-%m")
    month_ends = equity.groupby(month_key).equity.last()
    exposure = equity.groupby(month_key).exposed.mean() * 100
    previous = float(config.get("initial_capital", 1_000_000))
    rows = []
    exit_month = pd.to_datetime(trades.exit_time, utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m") if len(trades) else pd.Series(dtype=str)
    for month, nav in month_ends.items():
        closed = trades.loc[exit_month == month] if len(trades) else trades
        rows.append({"instrument": instrument, "id": config["id"], "family": config["family"], "month": month,
                     "start_equity": previous, "end_equity": float(nav),
                     "return_pct": float((nav / previous - 1) * 100),
                     "marked_net_profit": float(nav - previous),
                     "realized_trade_net_profit": float(closed.net_pnl.sum()) if len(closed) else 0.0,
                     "n_trades": len(closed), "expectancy_r": float(closed.net_r.mean()) if len(closed) else None,
                     "exposure_pct": float(exposure.loc[month])})
        previous = float(nav)
    return rows


def extend_evidence(output_path=OUT):
    out = Path(output_path)
    protocol_path, frozen_path = out / "protocol.json", out / "frozen-selection.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    frozen_hash = sha(frozen_path)
    protocol_hash = sha(protocol_path)
    configs = protocol["configs"]
    if len({config["id"] for config in configs}) != len(configs):
        raise ValueError("Protocol contains duplicate experiment identifiers")
    source_paths = [Path(__file__), ROOT / "research/swing/engine.py", ROOT / "research/swing/signals.py", ROOT / "research/swing/data.py"]
    source_hashes = {str(path.relative_to(ROOT)): sha(path) for path in source_paths}
    input_hashes = {}
    metrics, all_trades, subgroups, months = [], [], [], []
    t0 = time.monotonic()
    instruments = protocol["instruments"]
    for instrument in instruments:
        regular_path = out / f"{instrument.lower()}-5minute.csv"
        special_path = out / f"{instrument.lower()}-special-execution.csv"
        regular = load_candles(regular_path)
        input_hashes[regular_path.name] = sha(regular_path)
        execution = regular
        if special_path.exists():
            special = load_candles(special_path)
            input_hashes[special_path.name] = sha(special_path)
            execution = pd.concat([regular, special]).sort_index()
            if execution.index.has_duplicates:
                raise ValueError(f"Regular and special execution candles overlap for {instrument}")
        for number, config in enumerate(configs, 1):
            # Indicators intentionally never see special-session execution bars.
            signals = make_signals(regular, config)
            executable = {**config, "initial_capital": 1_000_000, "risk_fraction": .005,
                          "cost_model": "index_proxy" if instrument == "NIFTY" else "etf_delivery"}
            result = simulate(execution, signals, executable, START, END,
                              allow_short=instrument == "NIFTY")
            trades, equity = result["trades"], result["equity"]
            metrics.append({"instrument": instrument, "id": config["id"], "family": config["family"],
                            "part": "two_year_continuous", **result["metrics"],
                            "trade_signature": _trade_signature(trades)})
            if len(trades):
                tagged = trades.copy()
                tagged.insert(0, "family", config["family"])
                tagged.insert(0, "id", config["id"])
                tagged.insert(0, "instrument", instrument)
                all_trades.append(tagged)
            subgroups.extend(_subgroups(trades, instrument, config))
            months.extend(_monthly(equity, trades, instrument, executable))
            if number % 50 == 0 or number == len(configs):
                print(f"Continuous evidence {instrument} {number}/{len(configs)} elapsed={time.monotonic()-t0:.1f}s", flush=True)
        # Bound retained feature objects to one instrument; CSV outputs remain
        # separate from all original selected candidate results.
        clear_cache()
    metric_frame = pd.DataFrame(metrics)
    trades_frame = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame(columns=["instrument", "id", "family"])
    subgroup_frame, monthly_frame = pd.DataFrame(subgroups), pd.DataFrame(months)
    metric_frame.to_csv(out / "continuous-all-variants.csv", index=False)
    trades_frame.to_csv(out / "all-variant-trades.csv", index=False)
    subgroup_frame.to_csv(out / "all-variant-subgroups.csv", index=False)
    monthly_frame.to_csv(out / "monthly-all-variants.csv", index=False)
    unchanged = frozen_hash == sha(frozen_path) and protocol_hash == sha(protocol_path)
    source_hashes_after = {str(path.relative_to(ROOT)): sha(path) for path in source_paths}
    sources_unchanged = source_hashes == source_hashes_after
    summary = {"start": START, "end_exclusive": END, "no_selection": True, "no_tuning": True,
               "configurations": len(configs), "instruments": instruments,
               "continuous_metric_rows": len(metric_frame), "trade_ledger_rows": len(trades_frame),
               "subgroup_rows": len(subgroup_frame), "monthly_rows": len(monthly_frame),
               "protocol_sha256": protocol_hash, "frozen_selection_sha256": frozen_hash,
               "protocol_and_selection_unchanged": unchanged,
               "source_sha256": source_hashes, "source_sha256_after_run": source_hashes_after,
               "source_files_unchanged_during_run": sources_unchanged,
               "input_sha256": input_hashes, "elapsed_seconds": time.monotonic() - t0,
               "outcome_distinct_scenarios_per_instrument": metric_frame.groupby("instrument").trade_signature.nunique().to_dict(),
               "duplicate_signature_caveat": "Identical trade outcomes, including zero-trade rules, do not necessarily imply identical indicator rules or off-market signals.",
               "subgroup_policy": "Trade year uses exit timestamp; regime is the causal entry label. Separate year/regime/side/reason breakdowns and a joint year-regime-side breakdown are descriptive, with no subgroup-driven candidate reselection.",
               "monthly_policy": "Marked-to-market month-end equity changes include open trades. Realized trade P&L is shown separately and need not equal marked month returns.",
               "indicators_and_execution": "Regular-session data only for indicators; valid known special-session raw bars restored for next-tradable-open execution, protection, and marking.",
               "finalist_results_replaced": False}
    (out / "extension-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not unchanged or not sources_unchanged:
        raise RuntimeError("Protocol, selection, or source changed during evidence extension; see extension-summary.json")
    print(json.dumps({key: summary[key] for key in ["configurations", "continuous_metric_rows", "trade_ledger_rows", "subgroup_rows", "monthly_rows", "elapsed_seconds"]}), flush=True)
    return summary


def run(out=OUT):
    """Public entry point for the main research pipeline."""
    return extend_evidence(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(OUT))
    run(parser.parse_args().output)
