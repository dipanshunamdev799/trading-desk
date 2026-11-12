"""Matched-entry five-minute path check of five previously frozen finalists.

This is an execution-resolution diagnostic, not a new strategy or portfolio
backtest. It never changes entries, sizes, parameters or finalist selection.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.swing_discovery.data import DEFAULT_OUT, LEGACY, TZ, dump, prepare_data, sha
from research.swing_discovery.engine import fee_coeff
from research.swing.stocks import prepare_stock

SLIPPAGE_BPS = 5.
SLIP = SLIPPAGE_BPS / 10000
SUPPORTED = {"fixed", "time"}


def day(value):
    x = pd.Timestamp(value)
    return x.tz_localize(TZ).normalize() if x.tzinfo is None else x.tz_convert(TZ).normalize()


def replay_trade(row, config, sessions, daily, split_factor, cash_dividend):
    """Replay one unchanged daily entry; reject unsupported or missing paths.

    All thresholds stay in original entry units. Carried split positions are
    rejected explicitly instead of guessing whether the journal's final stop is
    in its original share basis. Both-hit five-minute bars remain stop-first.
    """
    entry_day, exit_day = day(row["entry_day"]), day(row["exit_day"])
    mode = config.get("exit", "fixed")
    base = {"symbol": row["symbol"], "signal_day": str(row["signal_day"]),
            "entry_day": str(entry_day), "daily_exit_day": str(exit_day),
            "daily_reason": row["reason"], "daily_net_pnl": float(row["net_pnl"]),
            "daily_net_r": float(row["net_r"]), "mode": mode}

    def reject(reason, **detail):
        return base | {"status": "rejected", "rejection": reason, **detail}

    if mode not in SUPPORTED:
        return reject("unsupported_trailing_or_signal_exit_requires_daily_stop_reconstruction")
    days = daily.index[(daily.index >= entry_day) & (daily.index <= exit_day)]
    if not len(days) or days[0] != entry_day or days[-1] != exit_day:
        return reject("daily_journal_dates_absent_from_panel")
    quantity = int(row["entry_quantity"])
    entry_fill = float(row["entry_fill"])
    risk = float(row["initial_cash_risk"])
    if quantity <= 0 or risk <= 0:
        return reject("invalid_quantity_or_initial_cash_risk")
    if (int(row["quantity"]) != quantity or not np.isclose(float(row["entry_adjusted"]), entry_fill)
            or not np.allclose(split_factor.reindex(days[1:]).to_numpy(), 1)):
        return reject("carried_split_or_share_basis_change")
    missing = [str(d.date()) for d in days if d not in sessions or not len(sessions[d])]
    if missing:
        return reject("missing_complete_five_minute_session", missing_dates=json.dumps(missing))
    stop, target = float(row["stop"]), float(row["target"])
    if not np.isfinite(stop) or (mode == "fixed" and not np.isfinite(target)):
        return reject("invalid_stop_or_target")
    # Preserve the exact daily entry and size; require an observed matching open.
    expected_open = entry_fill / (1 + SLIP)
    observed_open = float(sessions[entry_day].open.iloc[0])
    open_difference_bps = (observed_open / expected_open - 1) * 10000
    if abs(observed_open - expected_open) > max(.02, expected_open * .0001):
        return reject("entry_open_mismatch_above_one_bp_or_two_paise", entry_open_difference_bps=open_difference_bps)
    high_difference = max(abs(float(sessions[d].high.max()) / float(daily.loc[d, "high"]) - 1) * 10000 for d in days)
    low_difference = max(abs(float(sessions[d].low.min()) / float(daily.loc[d, "low"]) - 1) * 10000 for d in days)
    daily_both = bool(mode == "fixed" and ((daily.loc[days, "low"] <= stop) & (daily.loc[days, "high"] >= target)).any())
    earned_dividends, ambiguity, result = 0., 0, None
    for d in days:
        bars = sessions[d]
        if d != entry_day:
            earned_dividends += quantity * float(cash_dividend.get(d, 0.))
        for j, (timestamp, bar) in enumerate(bars.iterrows()):
            opening = float(bar.open)
            # The matched daily entry occurs at this first open, so it has no
            # pre-entry stop/target or dividend entitlement at that same open.
            if d != entry_day or j > 0:
                if opening <= stop:
                    result = (timestamp, opening * (1 - SLIP), "five_minute_gap_stop")
                elif mode == "fixed" and opening >= target:
                    result = (timestamp, target * (1 - SLIP), "five_minute_gap_target")
                elif d == exit_day and j == 0 and row["reason"] == "signal_or_time":
                    result = (timestamp, opening * (1 - SLIP), "scheduled_daily_time_exit")
            if result is not None: break
            hit_stop = float(bar.low) <= stop
            hit_target = mode == "fixed" and float(bar.high) >= target
            if hit_stop and hit_target: ambiguity += 1
            if hit_stop:
                result = (timestamp, stop * (1 - SLIP), "five_minute_stop")
            elif hit_target:
                result = (timestamp, target * (1 - SLIP), "five_minute_target")
            if result is not None: break
        if result is not None: break
    if result is None:
        if row["reason"] == "segment_end":
            bars = sessions[exit_day]
            result = (bars.index[-1], float(bars.close.iloc[-1]) * (1 - SLIP), "five_minute_segment_end")
        else:
            return reject("daily_level_hit_absent_in_complete_five_minute_path", daily_both_hit=daily_both,
                          entry_open_difference_bps=open_difference_bps,
                          maximum_high_difference_bps=high_difference, maximum_low_difference_bps=low_difference)
    timestamp, price, reason = result
    buy_rate, buy_fixed = fee_coeff(entry_day, True, False)
    sell_rate, sell_fixed = fee_coeff(timestamp, False, day(timestamp) != entry_day)
    buy_fees = entry_fill * quantity * buy_rate + buy_fixed
    sell_fees = price * quantity * sell_rate + sell_fixed
    gross = (price - entry_fill) * quantity + earned_dividends
    net = gross - buy_fees - sell_fees
    return base | {"status": "matched", "rejection": "", "entry_fill": entry_fill, "quantity": quantity,
                   "stop": stop, "target": target, "initial_cash_risk": risk, "five_minute_exit": str(timestamp),
                   "five_minute_exit_fill": price, "five_minute_reason": reason,
                   "five_minute_dividends": earned_dividends, "five_minute_fees": buy_fees + sell_fees,
                   "five_minute_gross_pnl": gross, "five_minute_net_pnl": net, "five_minute_net_r": net / risk,
                   "net_pnl_difference": net - float(row["net_pnl"]), "net_r_difference": net / risk - float(row["net_r"]),
                   "daily_both_hit": daily_both, "five_minute_both_hit_bars": ambiguity,
                   "entry_open_difference_bps": open_difference_bps,
                   "maximum_high_difference_bps": high_difference, "maximum_low_difference_bps": low_difference}


def verify(out=DEFAULT_OUT, stages=("final", "two_year")):
    out = Path(out)
    frozen_path = out / "frozen-finalists.json"
    if not frozen_path.exists(): raise RuntimeError("Finalists are not frozen yet; no check was run")
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    assert frozen["frozen_before_reserved_evaluation"] is True
    ids = frozen["preselected_finer_resolution_ids"]
    assert len(ids) == 5 and len(set(ids)) == 5
    configs = {x["id"]: {**x["config"], **x["config"].get("params", {})} for x in frozen["finalists"]}
    journals = {(i, stage): out / "finalist_journals" / f"{i}-all_eligible_stocks-{stage}-trades.csv" for i in ids for stage in stages}
    missing = [str(p) for p in journals.values() if not p.exists()]
    if missing: raise RuntimeError("Required frozen journals are not complete: " + ", ".join(missing))
    panel = prepare_data(out)
    eligible = {s for s, e in zip(panel["symbols"], panel["eligible"]) if e}
    original = json.loads((LEGACY / "universe.json").read_text(encoding="utf-8"))["stocks"]
    specs = {x["symbol"]: x for x in original}
    cached_symbols = set(specs) & eligible
    records = json.loads((LEGACY / "nse-actions-all.json").read_text(encoding="utf-8"))
    sessions, stock_failures, fingerprints = {}, {}, {}
    for symbol in sorted(cached_symbols):
        paths = [LEGACY / f"{symbol}-regular.csv", LEGACY / f"{symbol}-special.csv"]
        try:
            _, execution, audit = prepare_stock(specs[symbol], LEGACY, records)
            if audit["ranking_excluded"]:
                stock_failures[symbol] = "five_minute_corporate_or_price_audit_quarantine"
                continue
            sessions[symbol] = {d: g for d, g in execution.groupby(execution.index.normalize())}
            fingerprints[symbol] = {str(p): sha(p) for p in paths}
        except Exception as exc:
            stock_failures[symbol] = "five_minute_load_failed_" + type(exc).__name__
    rows, counts = [], Counter()
    for (ident, stage), journal in journals.items():
        try: trades = pd.read_csv(journal)
        except pd.errors.EmptyDataError: trades = pd.DataFrame()
        counts[f"{ident}|{stage}|all_journal_trades"] = len(trades)
        for index, row in trades.iterrows():
            symbol = row["symbol"]
            base = {"id": ident, "stage": stage, "journal_row": int(index), "symbol": symbol}
            if symbol not in cached_symbols:
                counts[f"{ident}|{stage}|outside_original_cached_eligible_cohort"] += 1
                continue
            if symbol in stock_failures:
                rows.append(base | {"status": "rejected", "rejection": stock_failures[symbol]})
                continue
            k = panel["symbols"].index(symbol)
            daily = pd.DataFrame({c: panel["actual"][c][k] for c in ("open", "high", "low", "close")}, index=panel["dates"])
            split = pd.Series(panel["split_factor"][k], index=panel["dates"])
            div = pd.Series(panel["dividend"][k], index=panel["dates"])
            rows.append(base | replay_trade(row, configs[ident], sessions[symbol], daily, split, div))
    frame = pd.DataFrame(rows)
    if not len(frame): frame = pd.DataFrame(columns=["id", "stage", "status", "rejection"])
    frame.to_csv(out / "intraday-resolution-check.csv", index=False)
    summaries = []
    for (ident, stage), group in frame.groupby(["id", "stage"]):
        matched = group[group.status == "matched"]
        summary = {"id": ident, "stage": stage, "cached_cohort_trade_rows": len(group), "matched": len(matched),
                   "rejected": len(group) - len(matched), "rejection_counts": group.loc[group.status != "matched", "rejection"].value_counts().to_dict()}
        if len(matched):
            summary.update(daily_both_hit_trades=int(matched.daily_both_hit.sum()),
                           five_minute_both_hit_bars=int(matched.five_minute_both_hit_bars.sum()),
                           daily_net_pnl=float(matched.daily_net_pnl.sum()), five_minute_net_pnl=float(matched.five_minute_net_pnl.sum()),
                           sum_net_pnl_difference=float(matched.net_pnl_difference.sum()),
                           mean_net_r_difference=float(matched.net_r_difference.mean()),
                           maximum_absolute_net_r_difference=float(matched.net_r_difference.abs().max()),
                           changed_matched_net_r_trades=int((matched.net_r_difference.abs() > 1e-8).sum()))
        summaries.append(summary)
    stage_summary = {}
    for stage, group in frame.groupby("stage"):
        matched = group[group.status == "matched"]
        stage_summary[stage] = {"matched": len(matched), "rejected": len(group) - len(matched),
                                "daily_both_hit_trades": int(matched.daily_both_hit.sum()) if len(matched) else 0,
                                "five_minute_both_hit_bars": int(matched.five_minute_both_hit_bars.sum()) if len(matched) else 0,
                                "maximum_absolute_net_r_difference": float(matched.net_r_difference.abs().max()) if len(matched) else None}
    result = {"status": "complete", "frozen_finalists_sha256": sha(frozen_path), "preselected_ids": ids,
              "selection_rationale": {"rule": "First five preselected_finer_resolution_ids from the frozen development/validation ranking, before reserved evaluation; no replacements based on intraday or final outcomes.",
                                      "records": [{k: x[k] for k in ("id", "family", "development_validation_eligible", "selection_score")} for x in frozen["finalists"] if x["id"] in ids]},
              "aggregate_by_stage": stage_summary,
              "stages": list(stages), "slippage_bps": SLIPPAGE_BPS, "cost_multiplier": 1.,
              "timestamp_semantics": "Provider five-minute candle START in Asia/Kolkata. An intrabar hit is localized to this bar, not claimed to occur at its start.",
              "original_cached_starting_stocks": len(specs), "eligible_cached_stock_count": len(cached_symbols),
              "eligible_cached_symbols": sorted(cached_symbols), "stock_load_rejections": stock_failures,
              "journal_scope_counts": dict(counts), "summaries": summaries,
              "journal_sha256": {str(p): sha(p) for p in journals.values()}, "five_minute_source_sha256": fingerprints,
              "limitations": ["Matched daily entries, original entry quantities and original cash risk are held fixed. This is not a five-minute strategy/portfolio replay: different exits could change subsequent entries, capital and quantities.",
                              "Only the five IDs preselected before reserved evaluation are checked. No parameters or finalists are selected from these outcomes.",
                              "Coverage is the original dated Nifty 50 cache intersected with the eligible broad cohort, not all 470 eligible stocks.",
                              "Fixed-target and time-only modes are supported. Trailing/signal exit modes and trades carrying splits or changed share units are explicitly rejected.",
                              "Five-minute OHLC cannot resolve a bar containing both stop and target; stop-first remains conservative. Intrabar stop gaps between observations also remain unknown.",
                              "A one-bp/two-paise entry-open tolerance is required; missing complete sessions and daily hits not observed in the complete five-minute path are rejected, never filled synthetically.",
                              "Observed five-minute opens/highs/lows/closes can differ from daily candles, particularly official daily close versus last intraday print; range discrepancies are reported per trade.",
                              "Dividends use ex-date economic entitlement; broker fees and taxes match the daily engine with adverse 5bp fills. No spreads, order-book impact or payment-date funding are reconstructed."]}
    dump(out / "intraday-resolution-check.json", result)
    print(json.dumps({"rows": len(frame), "matched": int((frame.status == "matched").sum()), "summaries": summaries}, indent=2))
    return frame, result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--stages", nargs="+", choices=["final", "two_year"], default=["final", "two_year"])
    args = parser.parse_args()
    verify(args.out, args.stages)
