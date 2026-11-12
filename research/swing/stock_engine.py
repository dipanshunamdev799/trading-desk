"""Stock-specific fork of the frozen swing simulator with corporate entitlements.

Original ETF/index engine remains unchanged. Input OHLC and signal levels are in
actual contemporary share units; split_factor is applied before ex-day open to
existing positions, and dividend entitlements are attributed to carried shares.

The input index labels base-candle *starts*. Signal indices label the time at
which a completed observation becomes available. Neither input is shifted by
the engine. Index results are explicitly hypothetical; they are not futures or
option execution results. Equity/ETF models support unlevered integer units.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

TZ = "Asia/Kolkata"


def _timestamp(value):
    result = pd.Timestamp(value)
    return result.tz_localize(TZ) if result.tzinfo is None else result.tz_convert(TZ)


def transaction_cost(price: float, quantity: int, action: str, timestamp,
                     model: str = "index_proxy", overnight: bool = False,
                     multiplier: float = 1.0) -> float:
    """Explicit cash fees, separate from adverse fill-price slippage.

    Rates are fractions of turnover. ETF delivery STT: nil purchases and
    0.001% sales. DP is charged conservatively on every overnight sale order;
    partial exits on the same date can therefore overestimate actual DP fees.
    Income/capital-gains tax and dividends are outside this trading-fee model.
    """
    if quantity <= 0:
        return 0.0
    turnover = abs(float(price) * int(quantity))
    if model == "index_proxy":
        return turnover * .0005 * multiplier
    if model not in ("equity_delivery", "etf_delivery"):
        raise ValueError(f"Unknown cost model: {model}")
    if action not in ("buy", "sell"):
        raise ValueError("action must be buy or sell")
    brokerage = 20.0
    exchange = turnover * (.0000297 if _timestamp(timestamp) < _timestamp("2026-03-01") else .0000307)
    sebi = turnover * .000001
    # Historical IPFT was 0.10/lakh before the combined March 2026 schedule.
    ipft = turnover * (.000001 if _timestamp(timestamp) < _timestamp("2026-03-01") else .000000001)
    stt = turnover * (.001 if model == "equity_delivery" else (.00001 if action == "sell" else 0))
    stamp = turnover * .00015 if action == "buy" else 0.0
    dp = 20.0 if action == "sell" and overnight else 0.0
    gst = .18 * (brokerage + exchange + sebi + ipft + dp)
    return (brokerage + exchange + sebi + ipft + stt + stamp + dp + gst) * multiplier


def summarize(trades: pd.DataFrame, equity: pd.DataFrame, initial_capital=1_000_000.0) -> dict[str, Any]:
    """Session-return ratios and full-resolution, marked-to-market drawdown."""
    if equity.empty:
        return {"trades": 0, "net_profit": 0.0, "net_return_pct": 0.0,
                "win_rate_pct": 0.0, "expectancy_r": None, "profit_factor": None,
                "max_drawdown_pct": 0.0, "sharpe": None, "sortino": None,
                "calmar": None, "exposure_pct": 0.0, "consecutive_losses": 0,
                "average_holding_hours": None, "trades_per_month": 0.0,
                "average_win": None, "average_loss": None, "sessions": 0,
                "n_trades": 0, "total_return_pct": 0.0, "avg_win": None,
                "avg_loss": None, "avg_hold_hours": None, "max_consecutive_losses": 0}
    values = equity.equity.to_numpy(float)
    peaks = np.maximum.accumulate(np.r_[initial_capital, values])[1:]
    max_dd = float(np.max(1 - values / peaks))
    daily = equity.groupby(equity.index.date).equity.last()
    returns = np.diff(np.r_[initial_capital, daily.to_numpy(float)]) / np.r_[initial_capital, daily.to_numpy(float)[:-1]]
    sd = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0.0
    downside = float(np.sqrt(np.mean(np.minimum(returns, 0.0) ** 2)))
    total_return = values[-1] / initial_capital - 1
    annual = (values[-1] / initial_capital) ** (252 / len(daily)) - 1 if values[-1] > 0 else -1.0
    n = len(trades)
    net = trades.net_pnl.to_numpy(float) if n else np.array([])
    wins = net[net > 0]
    losses = net[net < 0]
    streak = worst = 0
    for value in net:
        streak = streak + 1 if value < 0 else 0
        worst = max(worst, streak)
    result = {
        "trades": n, "net_profit": float(values[-1] - initial_capital),
        "net_return_pct": float(total_return * 100), "annualized_return_pct": float(annual * 100),
        "win_rate_pct": float(np.mean(net > 0) * 100) if n else 0.0,
        "expectancy_r": float(trades.net_r.mean()) if n else None,
        "average_win": float(wins.mean()) if len(wins) else None,
        "average_loss": float(losses.mean()) if len(losses) else None,
        "profit_factor": float(wins.sum() / -losses.sum()) if len(losses) else None,
        "max_drawdown_pct": max_dd * 100,
        "sharpe": float(np.mean(returns) / sd * np.sqrt(252)) if sd > 0 else None,
        "sortino": float(np.mean(returns) / downside * np.sqrt(252)) if downside > 0 else None,
        "calmar": float(annual / max_dd) if max_dd > 0 else None,
        "consecutive_losses": worst,
        "average_holding_hours": float(trades.holding_hours.mean()) if n else None,
        "exposure_pct": float(equity.exposed.mean() * 100),
        "trades_per_month": float(n / (len(daily) / 21)), "sessions": len(daily),
        "fees": float(trades.fees.sum()) if n else 0.0,
        "gross_profit": float(trades.gross_pnl.sum()) if n else 0.0,
    }
    result.update(n_trades=n, total_return_pct=result["net_return_pct"],
                  avg_win=result["average_win"], avg_loss=result["average_loss"],
                  avg_hold_hours=result["average_holding_hours"], max_consecutive_losses=worst)
    return result


def simulate(bars: pd.DataFrame, signals: pd.DataFrame, config: dict,
             start: str, end: str, cost_multiplier=1.0, slippage_bps=2.0,
             allow_short=True) -> dict:
    """Simulate one non-overlapping position with next-tradable-open fills.

    Config: reward, exit, max_hold_sessions, risk_fraction, initial_capital,
    cost_model, trail_atr. Optional signal fields: exit_long/exit_short,
    trail_stop, target (for structure exit). ``partial`` takes floor(qty/2) at
    1R and the rest at reward R, retaining the original stop. ``atr_trail``
    tightens from the previous base close and most recently observable ATR.
    ``ema`` uses signal.trail_stop. ``time`` has no fixed target. Other exit
    types retain a fixed target alongside their special exit condition.
    Signals outside [start,end) cannot initiate a position. No future signal
    is used to calculate a trailing stop or an exit at the current open.
    """
    if not isinstance(bars.index, pd.DatetimeIndex) or bars.index.tz is None:
        raise ValueError("bars require a timezone-aware DatetimeIndex")
    if not isinstance(signals.index, pd.DatetimeIndex) or signals.index.tz is None:
        raise ValueError("signals require a timezone-aware DatetimeIndex")
    if not bars.index.is_monotonic_increasing or bars.index.has_duplicates:
        raise ValueError("bars must be ordered with unique timestamps")
    if not signals.index.is_monotonic_increasing or signals.index.has_duplicates:
        raise ValueError("signals must be ordered with unique timestamps")
    mode = config.get("exit", "fixed")
    if mode not in ("fixed", "atr_trail", "macd", "ema", "time", "partial", "structure"):
        raise ValueError(f"Unsupported exit: {mode}")
    initial = float(config.get("initial_capital", 1_000_000))
    risk_fraction = float(config.get("risk_fraction", .005))
    if not 0 < risk_fraction <= 1:
        raise ValueError("risk_fraction must be in (0,1]")
    reward = float(config.get("reward", 2))
    if reward <= 0 or slippage_bps < 0 or cost_multiplier < 0:
        raise ValueError("Invalid reward or friction")
    model = config.get("cost_model", "index_proxy")
    if model in ("equity_delivery", "etf_delivery") and allow_short:
        # Delivery shorting is unsupported: silently manufacturing borrow is unsafe.
        allow_short = False
    lo, hi = _timestamp(start), _timestamp(end)
    d = bars.loc[(bars.index >= lo) & (bars.index < hi)]
    if d.empty:
        empty = pd.DataFrame()
        return {"trades": empty, "equity": empty, "metrics": summarize(empty, empty, initial)}
    idx = d.index
    o, h, l, c = (d[key].to_numpy(float) for key in ("open", "high", "low", "close"))
    if not np.isfinite(np.column_stack((o, h, l, c))).all() or np.any(l <= 0):
        raise ValueError("Non-finite or nonpositive OHLC")
    if np.any(h < np.maximum(o, c)) or np.any(l > np.minimum(o, c)) or np.any(h < l):
        raise ValueError("Inconsistent OHLC")
    ends = pd.DatetimeIndex(d["bar_end"]) if "bar_end" in d else idx + pd.Timedelta(minutes=5)
    if np.any(ends > hi):
        raise ValueError("Base bar crosses segment end")
    day_codes, _ = pd.factorize(idx.date)
    s = signals.loc[(signals.index >= lo) & (signals.index < hi)]
    mappings = idx.searchsorted(s.index, side="left")
    events: dict[int, list[dict]] = {}
    for j, stamp, event in zip(mappings, s.index, s.to_dict("records")):
        if j >= len(d):
            continue
        # Mapping is to the first actually tradable bar, including weekends
        # and exchange holidays. Signals cannot queue past an earlier bar.
        event["timestamp"] = stamp
        events.setdefault(int(j), []).append(event)
    cash = initial
    position = None
    trades: list[dict] = []
    marks = np.empty(len(d))
    exposed = np.zeros(len(d), dtype=bool)
    last_atr = np.nan
    slip = float(slippage_bps) / 10_000
    split_factors=d.get('split_factor',pd.Series(1.,index=idx)).to_numpy(float)
    dividends=d.get('dividend',pd.Series(0.,index=idx)).to_numpy(float)
    if np.any(split_factors<=0) or not np.isfinite(split_factors).all():
        raise ValueError('Invalid share adjustment')

    def fee(price, qty, action, stamp, overnight=False):
        return transaction_cost(price, qty, action, stamp, model, overnight, cost_multiplier)

    def close_leg(price, qty, stamp, reason):
        nonlocal cash, position
        p = position
        action = "sell" if p["side"] == 1 else "buy"
        cost = fee(price, qty, action, stamp, stamp.date() != p["entry_time"].date())
        gross = p["side"] * (price - p["entry"]) * qty
        cash += gross - cost
        p["gross_pnl"] += gross
        p["fees"] += cost
        p["exit_value"] += price * qty
        p["remaining"] -= qty
        p["legs"] += 1
        if p["remaining"] == 0:
            net = p["gross_pnl"] - p["fees"]
            trades.append({
                "signal_time": p["signal_time"], "entry_time": p["entry_time"], "exit_time": stamp,
                "side": p["side"], "entry": p["entry"], "exit": p["exit_value"] / p["quantity"],
                "quantity": p["quantity"], "stop": p["original_stop"], "target": p["target"],
                "entry_fill":p["entry_fill"],"entry_quantity":p["entry_quantity"],
                "dividends":p["dividends"],"share_adjustments":p["share_adjustments"],
                "initial_cash_risk": p["initial_cash_risk"], "gross_pnl": p["gross_pnl"],
                "fees": p["fees"], "net_pnl": net, "net_r": net / p["initial_cash_risk"],
                "reason": reason, "regime": p["regime"], "exit_legs": p["legs"],
                "holding_hours": (stamp - p["entry_time"]).total_seconds() / 3600,
            })
            position = None

    for i in range(len(d)):
        row_events = events.get(i, ())
        if position is not None:
            p=position
            factor=split_factors[i]
            if factor!=1:
                if mode=='partial':
                    raise ValueError('Stock split handling excludes partial-exit configurations')
                if abs(p['remaining']*factor-round(p['remaining']*factor))>1e-8:
                    raise ValueError('Fractional bonus entitlement requires separate cash-in-lieu data')
                for field in ['entry','stop','original_stop','target','partial_target']:
                    p[field]/=factor
                p['quantity']=int(round(p['quantity']*factor));p['remaining']=int(round(p['remaining']*factor))
                p['share_adjustments']+=1
            if dividends[i]>0:
                # Economic ex-date entitlement, credited only to overnight shares.
                entitlement=dividends[i]*p['remaining']
                cash+=entitlement;p['gross_pnl']+=entitlement;p['dividends']+=entitlement
        # Pending prior-session levels must use ex-day share units at execution.
        if split_factors[i]!=1:
            for event in row_events:
                if event['timestamp'].date()<idx[i].date():
                    for field in ['stop','atr','target','target_long','target_short','trail_stop','trail_stop_long','trail_stop_short']:
                        if field in event and pd.notna(event[field]):event[field]/=split_factors[i]
        had_position = position is not None
        for event in row_events:
            atr = event.get("atr", np.nan)
            if pd.notna(atr) and atr > 0:
                last_atr = float(atr)
        # All following values existed at this base bar's start.
        if position is not None:
            p = position
            if mode == "atr_trail" and i > 0 and np.isfinite(last_atr):
                candidate = c[i - 1] - p["side"] * float(config.get("trail_atr", 2.0)) * last_atr
                p["stop"] = max(p["stop"], candidate) if p["side"] > 0 else min(p["stop"], candidate)
            if mode == "ema":
                for event in row_events:
                    candidate = event.get("trail_stop_long" if p["side"] > 0 else "trail_stop_short", event.get("trail_stop", np.nan))
                    if pd.notna(candidate):
                        p["stop"] = max(p["stop"], candidate) if p["side"] > 0 else min(p["stop"], candidate)
            flag = "exit_long" if p["side"] > 0 else "exit_short"
            exit_signal = mode in ("macd", "ema") and any(bool(e.get(flag, False)) for e in row_events)
            timed = day_codes[i] - p["entry_session"] >= int(config.get("max_hold_sessions", 10))
            # Protective gap has priority over optional discretionary/time exit.
            gap_stop = o[i] <= p["stop"] if p["side"] > 0 else o[i] >= p["stop"]
            if gap_stop:
                close_leg(o[i] * (1 - p["side"] * slip), p["remaining"], idx[i], "gap_stop")
            else:
                # Resting protective/limit orders execute before optional
                # time or signal market exits at this open.
                if mode == "partial" and not p["partial_done"]:
                    gap_partial = o[i] >= p["partial_target"] if p["side"] > 0 else o[i] <= p["partial_target"]
                    if gap_partial:
                        p["partial_done"] = True
                        take = p["quantity"] // 2
                        if take:
                            close_leg(p["partial_target"] * (1 - p["side"] * slip), take, idx[i], "partial")
                if position is not None and mode not in ("time", "atr_trail", "ema"):
                    gap_target = o[i] >= p["target"] if p["side"] > 0 else o[i] <= p["target"]
                    if gap_target:
                        close_leg(p["target"] * (1 - p["side"] * slip), p["remaining"], idx[i], "target")
                if position is not None and (exit_signal or timed):
                    close_leg(o[i] * (1 - p["side"] * slip), p["remaining"], idx[i], mode if exit_signal else "time")
        # Consume events once. After an exit, do not reverse on that same bar.
        if position is None and not had_position:
            for event in row_events:
                side = int(event.get("side", 0))
                if side not in (-1, 1) or (side < 0 and not allow_short) or cash <= 0:
                    continue
                entry = o[i] * (1 + side * slip)
                stop = float(event.get("stop", np.nan))
                distance = side * (entry - stop)
                if not np.isfinite(distance) or distance <= 0:
                    continue
                atr = float(event.get("atr", np.nan))
                if config.get("stop_constraints", True) and np.isfinite(atr) and atr > 0:
                    if not .5 * atr <= distance <= 5 * atr:
                        continue
                risk_budget = cash * risk_fraction
                action = "buy" if side > 0 else "sell"
                exit_action = "sell" if side > 0 else "buy"
                stop_fill = stop * (1 - side * slip)
                qty = int(min(risk_budget / distance, cash / entry))
                # Fees are piecewise linear with fixed brokerage; iteration
                # converges quickly and explicitly enforces both constraints.
                for _ in range(10):
                    if qty <= 0:
                        break
                    enter_fee = fee(entry, qty, action, idx[i])
                    risk = side * (entry - stop_fill) * qty + enter_fee + fee(stop_fill, qty, exit_action, idx[i], True)
                    spend = entry * qty + enter_fee
                    if risk <= risk_budget + 1e-8 and spend <= cash + 1e-8:
                        break
                    next_qty = int(qty * min(risk_budget / risk, cash / spend))
                    qty = min(qty - 1, next_qty)
                if qty <= 0:
                    continue
                # Solve the barrier in actual executable prices so a target
                # exit earns reward * the cash-at-risk after both fee legs.
                target_fill = entry + side * reward * risk / qty
                for _ in range(8):
                    target_exit_fee = fee(target_fill, qty, exit_action, idx[i], True)
                    target_fill = entry + side * (reward * risk + enter_fee + target_exit_fee) / qty
                target = target_fill / (1 - side * slip)
                if mode == "structure":
                    structural_target = float(event.get("target_long" if side > 0 else "target_short", event.get("target", np.nan)))
                    if not np.isfinite(structural_target) or side * (structural_target - entry) <= 0:
                        continue
                    target = structural_target
                if target <= 0:
                    continue
                cash -= enter_fee
                position = dict(side=side, entry=entry, stop=stop, original_stop=stop,
                                entry_fill=entry,entry_quantity=qty,dividends=0.,share_adjustments=0,
                                target=target, quantity=qty, remaining=qty,
                                entry_time=idx[i], signal_time=event["timestamp"],
                                entry_session=day_codes[i], initial_cash_risk=risk,
                                fees=enter_fee, gross_pnl=0.0, exit_value=0.0, legs=0,
                                partial_done=False, partial_target=entry + side * distance,
                                regime=str(event.get("regime", "unknown")))
                break
        # Base candle OHLC is examined only after the open action. If both
        # barriers occur, stop-first is deliberately pessimistic.
        if position is not None:
            exposed[i] = True
            p = position
            stop_hit = l[i] <= p["stop"] if p["side"] > 0 else h[i] >= p["stop"]
            if stop_hit:
                stop_price = p["stop"]
                if p["side"] * (o[i] - stop_price) < 0:
                    stop_price = o[i]
                close_leg(stop_price * (1 - p["side"] * slip), p["remaining"], ends[i], "stop")
            else:
                if mode == "partial" and not p["partial_done"]:
                    partial_hit = h[i] >= p["partial_target"] if p["side"] > 0 else l[i] <= p["partial_target"]
                    if partial_hit:
                        take = p["quantity"] // 2
                        p["partial_done"] = True
                        if take > 0:
                            close_leg(p["partial_target"] * (1 - p["side"] * slip), take, ends[i], "partial")
                if position is not None and mode not in ("time", "atr_trail", "ema"):
                    p = position
                    target_hit = h[i] >= p["target"] if p["side"] > 0 else l[i] <= p["target"]
                    if target_hit:
                        close_leg(p["target"] * (1 - p["side"] * slip), p["remaining"], ends[i], "target")
        if i == len(d) - 1 and position is not None:
            close_leg(c[i] * (1 - position["side"] * slip), position["remaining"], ends[i], "segment_end")
        marks[i] = cash + (position["side"] * (c[i] - position["entry"]) * position["remaining"] if position is not None else 0)
    trade_frame = pd.DataFrame(trades)
    mark_frame = pd.DataFrame({"equity": marks, "exposed": exposed}, index=ends)
    mark_frame.index.name = "time"
    return {"trades": trade_frame, "equity": mark_frame,
            "metrics": summarize(trade_frame, mark_frame, initial)}
