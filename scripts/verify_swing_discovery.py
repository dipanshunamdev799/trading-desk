"""Read-only reconciliation of the frozen broad swing-discovery ledger.

This does not generate signals, select rules, tune models, or rerun executions.
It writes only verification.json, retaining zero-trade journals in the audit.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "swing_discovery"
TZ = "Asia/Kolkata"


class Audit:
    def __init__(self):
        self.failures = []
        self.checks = {}
        self.max_errors = {}

    def check(self, condition, name, detail=None):
        ok = bool(np.asarray(condition).all())
        self.checks[name] = self.checks.get(name, True) and ok
        if not ok and len(self.failures) < 30:
            self.failures.append({"check": name, "detail": str(detail)[:300]})

    def close(self, actual, expected, name, detail=None, atol=1e-6):
        a, b = np.asarray(actual, float), np.asarray(expected, float)
        if a.size:
            error = float(np.max(np.abs(a - b)))
            self.max_errors[name] = max(self.max_errors.get(name, 0.), error)
        self.check(np.isclose(a, b, rtol=1e-10, atol=atol), name, detail)


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def fee(day, buy=True, overnight=True, multiplier=1.):
    """Independent arithmetic of the frozen delivery fee schedule."""
    early = str(day)[:10] < "2026-03-01"
    exchange = .0000297 if early else .0000307
    ipft = .000001 if early else .000000001
    proportional = .001 + (.00015 if buy else 0.) + 1.18 * (exchange + .000001 + ipft)
    fixed = 23.6 + (23.6 if not buy and overnight else 0.)
    return proportional * multiplier, fixed * multiplier


def main():
    audit = Audit()
    protocol, summary, frozen = map(load, ("protocol.json", "run-summary.json", "frozen-finalists.json"))
    index = load("panel-index.json")
    dates = pd.DatetimeIndex(pd.to_datetime(index["dates"], utc=True)).tz_convert(TZ)
    days = dates.strftime("%Y-%m-%d").to_numpy()
    date_index = {str(day): i for i, day in enumerate(days)}
    symbols = index["symbols"]
    symbol_index = {symbol: i for i, symbol in enumerate(symbols)}
    with np.load(OUT / "daily-panel.npz") as panel_file:
        panel = {key: panel_file[key].copy() for key in (
            "actual_open", "actual_high", "actual_low", "actual_close", "eligible",
            "split_factor", "unit_factor", "dividend", "liquidity_volume", "liquidity_turnover")}
    eligible = {s for s, ok in zip(symbols, panel["eligible"]) if ok}
    pools = {"development_stocks": set(protocol["development_stocks"]),
             "reserved_stocks": set(protocol["reserved_stocks"]), "all_eligible_stocks": eligible}
    audit.check(len(symbols) == 500 and len(eligible) == 470, "registered_and_eligible_counts")
    audit.check(len(pools["development_stocks"]) == 375 and len(pools["reserved_stocks"]) == 95,
                "development_and_reserved_counts")
    audit.check(not pools["development_stocks"] & pools["reserved_stocks"] and
                pools["development_stocks"] | pools["reserved_stocks"] == eligible, "disjoint_exhaustive_pools")
    old = {s["isin_at_start"] for s in json.loads((ROOT / "artifacts/stock_swing_research/universe.json").read_text())["stocks"]}
    identities = {s["symbol"]: s["isin_at_start"] for s in load("universe.json")["stocks"]}
    independently_reserved = {s for s in eligible if identities[s] not in old and
                              int(hashlib.sha256(identities[s].encode()).hexdigest()[:8], 16) % 5 == 0}
    audit.check(independently_reserved == pools["reserved_stocks"], "reserved_companies_are_novel_and_hash_selected")

    conn = sqlite3.connect(f"file:{(OUT / 'research.sqlite3').as_posix()}?mode=ro", uri=True)
    audit.check(conn.execute("PRAGMA quick_check").fetchone()[0] == "ok", "sqlite_integrity")
    experiments = pd.read_sql_query("SELECT * FROM experiments", conn)
    configs = {row.id: json.loads(row.configuration) for row in experiments.itertuples()}
    runs = pd.read_sql_query("SELECT * FROM runs", conn)
    run_summaries = {row.key: json.loads(row.summary) for row in runs.itertuples()}
    counts = {name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
              for name in ("experiments", "runs", "portfolio_days", "stock_metrics")}
    audit.check(counts == {"experiments": 1308, "runs": 6429,
                          "portfolio_days": 1190858, "stock_metrics": 1095210}, "actual_ledger_counts", counts)
    phase_counts = experiments.groupby("phase").size().to_dict()
    audit.check(phase_counts == {"coarse": 1174, "development_refinement": 134}, "coarse_and_refinement_counts")
    audit.check(experiments.family.nunique() == 48 and frozen["count"] == 48 and
                len({x["family"] for x in frozen["finalists"]}) == 48, "48_distinct_finalist_families")
    audit.check(all(configs[c["id"]] == c for c in protocol["configurations"]), "protocol_configurations_match_ledger")
    audit.check(all(configs[x["id"]] == x["config"] for x in frozen["finalists"]), "frozen_configurations_match_ledger")
    audit.check(summary["execution_runs"] == counts["runs"] and summary["coarse_configurations"] == 1174 and
                summary["refined_configurations"] == 134 and summary["families"] == 48 and
                summary["registered_stocks"] == 500 and summary["eligible_stocks"] == 470 and
                summary["development_stocks"] == 375 and summary["reserved_new_stocks"] == 95,
                "run_summary_counts_match_ledger")
    expected_stages = {("development", "development_stocks"): 1308,
                       ("validation", "development_stocks"): 1308}
    for pool in pools:
        expected_stages[("final", pool)] = 48
    for stage in ("final_double10", "final_severe20", "two_year"):
        expected_stages[(stage, "all_eligible_stocks")] = 48
    for fold in ("2025-08-10", "2025-11-10", "2026-02-10"):
        expected_stages[("walktrain_" + fold, "development_stocks")] = 1174
        expected_stages[("walktest_" + fold, "all_eligible_stocks")] = 1
    audit.check(runs.groupby(["stage", "pool"]).size().to_dict() == expected_stages, "execution_stage_coverage")
    audit.check(runs.id.isin(configs).all() and not runs.duplicated(["id", "stage", "pool", "start", "end", "cost", "slippage"]).any(),
                "unique_registered_execution_runs")
    audit.check(all(set(group.id) == {x["id"] for x in frozen["finalists"]}
                    for _, group in runs[runs.stage.isin(["final", "final_double10", "final_severe20", "two_year"])].groupby(["stage", "pool"])),
                "frozen_finalists_exclusively_evaluated")
    initial = {row.key: float(configs[row.id].get("initial_capital", 1_000_000)) for row in runs.itertuples()}

    nav = pd.read_sql_query("SELECT * FROM portfolio_days ORDER BY key,day", conn)
    audit.check(nav.key.isin(initial).all() and np.isfinite(nav[["equity", "net_return"]]).all().all() and
                (nav.equity > 0).all(), "finite_registered_nav_rows")
    prior = nav.groupby("key", sort=False).equity.shift().fillna(nav.key.map(initial))
    audit.close(nav.net_return, nav.equity / prior - 1, "all_daily_return_recurrences", atol=1e-12)
    nav_by_key = nav.groupby("key", sort=False)
    ends = nav_by_key.equity.last()
    expected_day_rows = 0
    for row in runs.itertuples():
        expected = days[(days >= row.start) & (days < row.end)]
        actual = nav_by_key.get_group(row.key)
        expected_day_rows += len(expected)
        audit.check(np.array_equal(actual.day.to_numpy(), expected), "complete_exact_session_calendar", row.key)
        metrics = run_summaries[row.key]
        audit.close(metrics["total_return_pct"], (ends[row.key] / initial[row.key] - 1) * 100,
                    "summary_return_matches_nav", row.key)
        audit.check(metrics["stock_count"] == len(pools[row.pool]), "summary_pool_stock_counts", row.key)
    audit.check(expected_day_rows == counts["portfolio_days"], "independently_expected_day_row_count")

    # SQL scans check every stored stock row, including all zero-trade sleeves.
    residuals = conn.execute("""SELECT MAX(ABS(net_profit + fees - gross_profit)),
        MAX(ABS(net_profit - winning_pnl + losing_pnl)),
        MAX(ABS(total_return_pct - net_profit / 10000.)),
        SUM(CASE WHEN fees < 0 OR n_trades < 0 OR winning_trades + losing_trades > n_trades
            OR (n_trades = 0 AND (ABS(net_profit) > .000001 OR ABS(fees) > .000001 OR ABS(gross_profit) > .000001))
            THEN 1 ELSE 0 END) FROM stock_metrics""").fetchone()
    audit.close(residuals[:3], [0, 0, 0], "all_stock_row_pnl_fee_identities")
    audit.check(residuals[3] == 0, "all_stock_row_counts_fees_and_empty_sleeves")
    audit.check(conn.execute("SELECT COUNT(*) FROM (SELECT key,symbol,COUNT(*) n FROM stock_metrics GROUP BY key,symbol HAVING n != 1)").fetchone()[0] == 0,
                "stock_metric_key_symbol_unique")
    aggregate = pd.read_sql_query("""SELECT key,COUNT(*) stock_count,SUM(n_trades) n_trades,
        SUM(net_profit) net_profit,SUM(gross_profit) gross_profit,SUM(fees) fees,
        SUM(sum_r) sum_r FROM stock_metrics GROUP BY key""", conn).set_index("key")
    expected_stock_rows = 0
    for row in runs.itertuples():
        if row.stage.startswith("walktrain_"):
            audit.check(row.key not in aggregate.index, "walktrain_stock_rows_intentionally_absent", row.key)
            continue
        expected_stock_rows += len(pools[row.pool])
        audit.check(row.key in aggregate.index, "all_other_runs_retain_stock_rows", row.key)
        if row.key not in aggregate.index:
            continue
        stock, metrics = aggregate.loc[row.key], run_summaries[row.key]
        audit.check(stock.stock_count == len(pools[row.pool]) and stock.n_trades == metrics["n_trades"],
                    "all_summary_stock_and_trade_counts", row.key)
        audit.close(ends[row.key], initial[row.key] + stock.net_profit / stock.stock_count,
                    "mean_nav_equals_initial_plus_mean_stock_net", row.key)
        audit.close(metrics["fees"], stock.fees, "all_summary_fees_match_stock_metrics", row.key)
        if stock.n_trades:
            audit.close(metrics["expectancy_r"], stock.sum_r / stock.n_trades,
                        "all_summary_r_matches_stock_metrics", row.key)
    audit.check(expected_stock_rows == counts["stock_metrics"], "independently_expected_stock_row_count")

    selected = runs[runs.stage.isin(["final", "two_year"]) | runs.stage.str.startswith("walktest_")]
    stock = pd.read_sql_query("""SELECT m.key,m.symbol,m.n_trades,m.net_profit,m.fees,m.gross_profit,m.sum_r
        FROM stock_metrics m JOIN runs r ON r.key=m.key
        WHERE r.stage IN ('final','two_year') OR r.stage LIKE 'walktest_%'""", conn).set_index(["key", "symbol"])
    total_journal_trades = split_trades = dividend_trades = empty_journals = 0
    max_risk_fraction = max_cash_fraction = 0.
    for row in selected.itertuples():
        label = f"{row.id}-{row.pool}-{row.stage}"
        path = OUT / "finalist_journals" / (label + "-trades.csv")
        eq_path = path.with_name(label + "-equity.csv")
        audit.check(path.exists() and eq_path.exists(), "all_selected_journals_retained", label)
        if not path.exists() or not eq_path.exists():
            continue
        eq = pd.read_csv(eq_path)
        eq_days = pd.to_datetime(eq.iloc[:, 0], utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
        stored_nav = nav_by_key.get_group(row.key)
        audit.check(np.array_equal(eq_days, stored_nav.day), "journal_equity_calendar_matches_ledger", label)
        audit.close(eq.equity, stored_nav.equity, "journal_equity_matches_ledger", label)
        audit.close(eq["return"], stored_nav.net_return, "journal_returns_match_ledger", label, atol=1e-12)
        try:
            journal = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            journal = pd.DataFrame()
        metrics = run_summaries[row.key]
        audit.check(len(journal) == metrics["n_trades"], "journal_trade_count_matches_summary", label)
        if not len(journal):
            empty_journals += 1
            audit.close(stored_nav.equity, initial[row.key], "empty_journal_cash_retained", label)
            continue
        total_journal_trades += len(journal)
        for column in ("signal_day", "entry_day", "exit_day"):
            journal[column] = pd.to_datetime(journal[column], utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
        audit.check(journal.symbol.isin(pools[row.pool]).all(), "journal_symbols_match_stock_pool", label)
        audit.check((journal.entry_day > journal.signal_day).all() and (journal.exit_day >= journal.entry_day).all(),
                    "strict_signal_entry_and_exit_order", label)
        audit.check((journal.signal_day >= row.start).all() and (journal.entry_day >= row.start).all() and
                    (journal.entry_day < row.end).all() and (journal.exit_day < row.end).all(),
                    "no_entries_or_signals_outside_test_period", label)
        audit.check((journal[["entry_quantity", "quantity"]] >= 1).all().all() and
                    (journal[["entry_quantity", "quantity"]] == np.floor(journal[["entry_quantity", "quantity"]])).all().all(),
                    "positive_integer_share_quantities", label)
        audit.close(journal.gross_pnl, (journal["exit"] - journal.entry_adjusted) * journal.quantity + journal.dividends,
                    "journal_gross_pnl_identity", label)
        audit.close(journal.net_pnl, journal.gross_pnl - journal.fees, "journal_net_pnl_identity", label)
        audit.close(journal.net_r, journal.net_pnl / journal.initial_cash_risk, "journal_net_r_identity", label)
        grouped = journal.groupby("symbol").agg(n_trades=("net_pnl", "size"), net_profit=("net_pnl", "sum"),
            fees=("fees", "sum"), gross_profit=("gross_pnl", "sum"), sum_r=("net_r", "sum"))
        stored = stock.loc[row.key].reindex(sorted(pools[row.pool]))
        grouped = grouped.reindex(stored.index, fill_value=0.)
        audit.close(grouped.to_numpy(), stored[grouped.columns].to_numpy(), "all_journal_stock_aggregates_reconcile", label)
        audit.close(journal.net_pnl.sum() / metrics["stock_count"] + initial[row.key], ends[row.key],
                    "all_journal_mean_pnl_reconciles_nav", label)
        cfg = configs[row.id]
        audit.check(cfg.get("exit", "fixed") == "fixed", "fixed_exit_risk_reconstruction_supported", label)
        slip = row.slippage / 10000.
        for symbol, group in journal.groupby("symbol"):
            group = group.sort_values(["entry_day", "exit_day"])
            audit.check((group.entry_day.to_numpy()[1:] > group.exit_day.to_numpy()[:-1]).all(),
                        "no_overlapping_or_same_day_reentries", label + "/" + symbol)
            balance = initial[row.key]
            s = symbol_index[symbol]
            for trade in group.itertuples():
                e, x, sig = (date_index[str(getattr(trade, k))] for k in ("entry_day", "exit_day", "signal_day"))
                detail = f"{label}/{symbol}/{trade.entry_day}"
                valid = np.isfinite(panel["actual_open"][s]) & np.isfinite(panel["actual_high"][s]) & np.isfinite(panel["actual_low"][s]) & np.isfinite(panel["actual_close"][s]) & (panel["actual_low"][s] > 0)
                subsequent = np.flatnonzero(valid & (np.arange(len(dates)) > sig))
                audit.check(len(subsequent) and e == subsequent[0] and e == sig + 1,
                            "entry_is_next_actual_tradable_session", detail)
                audit.close(trade.entry_fill, panel["actual_open"][s, e] * (1 + slip),
                            "entry_fill_uses_actual_price_and_adverse_slippage", detail)
                split_path = panel["split_factor"][s, e + 1:x + 1]
                factor = float(np.prod(split_path))
                split_trades += int(factor != 1.)
                audit.close(trade.quantity, trade.entry_quantity * factor, "held_split_share_entitlement", detail)
                audit.close(trade.entry_adjusted, trade.entry_fill / factor, "held_split_adjusted_entry", detail)
                if len(split_path):
                    entitled = trade.entry_quantity * np.cumprod(split_path)
                    dividend = float(np.sum(entitled * panel["dividend"][s, e + 1:x + 1]))
                else:
                    dividend = 0.
                dividend_trades += int(dividend != 0.)
                audit.close(trade.dividends, dividend, "held_dividend_entitlement", detail)
                audit.close(trade.entry_adjusted * trade.quantity, trade.entry_fill * trade.entry_quantity,
                            "split_does_not_invent_cost_basis_gap", detail)
                br, bf = fee(trade.entry_day, True, False, row.cost)
                sr, sf = fee(trade.entry_day, False, True, row.cost)
                xr, xf = fee(trade.exit_day, False, e != x, row.cost)
                entry_fee = trade.entry_fill * trade.entry_quantity * br + bf
                exit_fee = trade.exit * trade.quantity * xr + xf
                audit.close(trade.fees, entry_fee + exit_fee, "actual_entry_exit_fee_reconstruction", detail)
                original_stop = trade.stop * factor
                stop_fill = original_stop * (1 - slip)
                per_share = trade.entry_fill - stop_fill + trade.entry_fill * br + stop_fill * sr
                risk = per_share * trade.entry_quantity + bf + sf
                audit.close(trade.initial_cash_risk, risk, "initial_cash_risk_reconstruction", detail)
                risk_fraction = trade.initial_cash_risk / balance
                cash_fraction = (trade.entry_fill * trade.entry_quantity + entry_fee) / balance
                max_risk_fraction = max(max_risk_fraction, risk_fraction)
                max_cash_fraction = max(max_cash_fraction, cash_fraction)
                audit.check(0 < risk_fraction <= min(.005, float(cfg.get("risk_fraction", .005))) + 1e-10,
                            "entry_cash_risk_at_most_half_percent_of_prior_flat_equity", detail)
                audit.check(cash_fraction <= 1 + 1e-10, "entry_is_unlevered_including_buy_costs", detail)
                cap = np.floor(panel["liquidity_volume"][s, e] * float(cfg.get("participation", .01)))
                q_risk = np.floor(max(0., balance * cfg.get("risk_fraction", .005) - bf - sf) / per_share)
                q_cash = np.floor(max(0., balance - bf) / (trade.entry_fill * (1 + br)))
                audit.close(trade.entry_quantity, min(q_risk, q_cash, cap), "entry_quantity_matches_risk_cash_liquidity_caps", detail)
                audit.check(panel["liquidity_turnover"][s, e] >= cfg.get("min_turnover", 50_000_000),
                            "entry_lagged_turnover_screen", detail)
                target = (trade.entry_fill * trade.entry_quantity + cfg.get("reward", 2.) * risk + entry_fee + sf) / (trade.entry_quantity * (1 - sr)) / (1 - slip) / factor
                audit.close(trade.target, target, "reward_target_reconstructs_initial_cash_risk", detail)
                if trade.reason == "gap_stop":
                    audit.check(panel["actual_open"][s, x] <= trade.stop, "gap_stop_uses_split_adjusted_stop", detail)
                balance += trade.net_pnl
    conn.close()
    source_paths = [ROOT / "scripts/run_swing_discovery.py", Path(__file__).resolve(), *sorted((ROOT / "research/swing_discovery").glob("*.py"))]
    source_manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
    result = {"passed": not audit.failures, "counts": counts, "phase_counts": phase_counts,
        "families": 48, "stock_pools": {key: len(value) for key, value in pools.items()},
        "checked_journals": len(selected), "checked_journal_trades": total_journal_trades,
        "retained_empty_journals": empty_journals, "held_split_trades": split_trades,
        "held_dividend_trades": dividend_trades, "max_entry_risk_fraction": max_risk_fraction,
        "max_entry_cash_fraction_including_fees": max_cash_fraction,
        "checks": audit.checks, "maximum_absolute_reconciliation_errors": audit.max_errors,
        "failures": audit.failures, "source_manifest_sha256": source_manifest,
        "recorded_execution_source_manifest_sha256": summary["source_sha256"],
        "scope": "All ledger rows and all frozen final/three-pool, two-year and walk-test journals. Walk-training intentionally retains summary/NAV only, so stock-row reconciliation is unavailable for those 3522 runs. No signal generation, strategy selection or executions rerun."}
    (OUT / "verification.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("passed", "counts", "checked_journals", "checked_journal_trades", "held_split_trades", "held_dividend_trades", "failures")}, indent=2))
    if audit.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
