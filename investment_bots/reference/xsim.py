"""Phase 8 execution-aware portfolio engine.

Semantics are those of the frozen reference engine phase5/sim5.py (C0-R spec), re-expressed in shares and rupees so that
execution can be modelled order by order. With the default arguments (fills at the official open, fractional shares,
fill fraction 1) it reproduces sim5 to floating-point precision (tests/test_phase8.py). sim5.py itself is untouched.

Additions (all off by default):
  fill(t, s, side, rupees, qty) -> (price | None, fraction, tag)
        per-order executable price and filled fraction. price None or fraction 0 = not filled.
        Sells not (fully) filled stay pending (retried next session, as in sim5); buys not filled are dropped (sim5).
  integer=True
        whole-share quantities. Buy quantity is fixed BEFORE the open from information at the decision close:
        qty = floor(weight * equity_at_decision_close / decision_close_price); costs are paid from cash.
        Orders that round to zero shares are logged as 'zero_qty' (invalid quantity) and not sent.
  ledger=True
        returns every order: intended quantity/value, fill price, fraction, filled value, cost, tag.
Units: capital in rupees; returned eq is normalised to 1.0 at the start (comparable with sim5).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd


def run(A, score, t0, N=20, keep=40, R=5, sector_max=6, cost=0.00225, min_buy_frac=0.2, first_decision=True,
        exposure=None, rebalance_on_exposure=0.0, tiebreak=None, cost_fn=None, capital=1e6, t1=None,
        fill=None, integer=False, ledger=False, log=False):
    o, c, ind = A["o"], A["c"], A["industry"]
    T = c.shape[0]
    t1 = T if t1 is None else t1
    K = float(capital)
    cash, hold = K, {}            # hold[s] = {"q": shares, "px": last mark, "t": entry index, "e": entry price}
    pend_sell, pend_buy, pend_resize = [], [], {}
    eq = np.full(T, np.nan)
    expo = np.zeros(T)
    trades, turn, costs_paid, nn = [], 0.0, 0.0, np.zeros(T)
    led, snaps = [], {}
    start = t0 if first_decision else t0 + 1
    eq[t0 - 1 if t0 > 0 else 0] = 1.0
    eq_dec = K                    # equity (rupees) at the most recent close = decision-time equity

    def tc(s, rupees, t, side):
        if cost_fn is not None:
            return cost_fn(s, rupees / K, t, side)   # cost_fn works in fractions of the book's capital
        return cost

    def px_fill(t, s, side, rupees, qty):
        if fill is None:
            p = o[t, s]
            return (None if np.isnan(p) else p), 1.0, "open"
        return fill(t, s, side, rupees, qty)

    for t in range(t0, t1):
        # ---------------- open: sells (full exits; partial fills stay pending)
        for s in pend_sell:
            if s not in hold:
                continue
            h = hold[s]
            if np.isnan(o[t, s]):
                if ledger:
                    led.append({"t": t, "s": s, "side": "S", "intended_qty": h["q"], "fill_px": None, "frac": 0.0,
                                "filled_value": 0.0, "cost": 0.0, "tag": "no_open"})
                continue
            fp, f, tag = px_fill(t, s, "S", h["q"] * o[t, s], h["q"])
            if fp is None or f <= 0:
                if ledger:
                    led.append({"t": t, "s": s, "side": "S", "intended_qty": h["q"], "fill_px": None, "frac": 0.0,
                                "filled_value": 0.0, "cost": 0.0, "tag": tag})
                h["q"], h["px"] = h["q"], h["px"]
                continue
            # a partial sell never leaves a dust remainder (fixed fees on dust would be charged on every retry)
            if f < 1.0 and (f >= 0.995 or (1 - f) * h["q"] * fp < max(500.0, 0.0005 * K)):
                f = 1.0
            q_sell = h["q"] * min(f, 1.0)
            if integer:
                q_sell = h["q"] if f >= 1 else math.floor(q_sell)
            v = q_sell * fp
            k = tc(s, v, t, "s")
            cash += v * (1 - k)
            costs_paid += v * k
            turn += v
            if ledger:
                led.append({"t": t, "s": s, "side": "S", "intended_qty": h["q"], "fill_px": fp, "frac": q_sell / h["q"],
                            "filled_value": v, "cost": v * k, "tag": tag})
            if q_sell >= h["q"] - 1e-12:
                hold.pop(s)
                trades.append((s, h["t"], t, fp / h["e"] - 1))
            else:
                h["q"] -= q_sell
        pend_sell = [s for s in pend_sell if s in hold]
        for s, h in hold.items():
            if not np.isnan(o[t, s]):
                h["px"] = o[t, s]
        eq_open = cash + sum(h["q"] * h["px"] for h in hold.values())
        # ---------------- resizes (vol-target rescale): sells first, then buys
        for s, tgt in sorted(pend_resize.items(), key=lambda x: (x[1] - (hold[x[0]]["q"] * hold[x[0]]["px"] if x[0] in hold else 0.0) / max(eq_open, 1e-12))):
            if s not in hold or np.isnan(o[t, s]):
                continue
            h = hold[s]
            d_val = tgt * eq_open - h["q"] * h["px"]
            if d_val == 0:
                continue
            side = "S" if d_val < 0 else "B"
            fp, f, tag = px_fill(t, s, side, abs(d_val), abs(d_val) / h["px"])
            if fp is None or f <= 0:
                continue
            v = abs(d_val) * min(f, 1.0) * (fp / h["px"])
            if side == "B":
                v = min(v, cash)
                if v <= 0:
                    continue
            dq = v / fp
            if integer:
                dq = math.floor(dq)
                v = dq * fp
                if dq <= 0:
                    continue
            k = tc(s, v, t, side.lower())
            if side == "S":
                h["q"] -= dq
                cash += v * (1 - k)
            else:
                if integer:
                    cash -= v * (1 + k)
                    h["q"] += dq
                else:
                    cash -= v
                    h["q"] += dq * (1 - k)
            costs_paid += v * k
            turn += v
            if ledger:
                led.append({"t": t, "s": s, "side": "R" + side, "intended_qty": abs(d_val) / h["px"], "fill_px": fp,
                            "frac": min(f, 1.0), "filled_value": v, "cost": v * k, "tag": tag})
        pend_resize = {}
        # ---------------- buys
        for s, w in pend_buy:
            if len(hold) >= N or s in hold:
                continue
            if np.isnan(o[t, s]):
                if ledger:
                    led.append({"t": t, "s": s, "side": "B", "intended_qty": None, "fill_px": None, "frac": 0.0,
                                "filled_value": 0.0, "cost": 0.0, "tag": "no_open"})
                continue
            if integer:
                ref = c[t - 1, s]
                q_int = math.floor(w * eq_dec / ref) if ref == ref and ref > 0 else 0
                if q_int <= 0:
                    if ledger:
                        led.append({"t": t, "s": s, "side": "B", "intended_qty": 0, "fill_px": None, "frac": 0.0,
                                    "filled_value": 0.0, "cost": 0.0, "tag": "zero_qty"})
                    continue
                fp, f, tag = px_fill(t, s, "B", q_int * ref, q_int)
                if fp is None or f <= 0:
                    if ledger:
                        led.append({"t": t, "s": s, "side": "B", "intended_qty": q_int, "fill_px": None, "frac": 0.0,
                                    "filled_value": 0.0, "cost": 0.0, "tag": tag})
                    continue
                q = math.floor(q_int * min(f, 1.0))
                k = tc(s, q * fp, t, "b")
                q = min(q, math.floor(cash / (fp * (1 + k)))) if fp > 0 else 0
                if q <= 0 or q * fp < min_buy_frac * eq_open / N:
                    if ledger:
                        led.append({"t": t, "s": s, "side": "B", "intended_qty": q_int, "fill_px": fp, "frac": 0.0,
                                    "filled_value": 0.0, "cost": 0.0, "tag": "skipped_cash_or_min"})
                    continue
                v = q * fp
                cash -= v * (1 + k)
                costs_paid += v * k
                turn += v
                hold[s] = {"q": q, "px": fp, "t": t, "e": fp}
                if ledger:
                    led.append({"t": t, "s": s, "side": "B", "intended_qty": q_int, "fill_px": fp, "frac": q / q_int,
                                "filled_value": v, "cost": v * k, "tag": tag})
                continue
            amt = min(w * eq_open, cash)
            if amt < min_buy_frac * eq_open / N:
                continue
            fp, f, tag = px_fill(t, s, "B", amt, amt / o[t, s])
            if fp is None or f <= 0:
                if ledger:
                    led.append({"t": t, "s": s, "side": "B", "intended_qty": amt / o[t, s], "fill_px": None, "frac": 0.0,
                                "filled_value": 0.0, "cost": 0.0, "tag": tag})
                continue
            amt_f = amt * min(f, 1.0)
            if f < 1.0 and amt_f < min_buy_frac * eq_open / N:
                if ledger:
                    led.append({"t": t, "s": s, "side": "B", "intended_qty": amt / o[t, s], "fill_px": fp, "frac": 0.0,
                                "filled_value": 0.0, "cost": 0.0, "tag": "partial_below_min"})
                continue
            k = tc(s, amt_f, t, "b")
            cash -= amt_f
            costs_paid += amt_f * k
            turn += amt_f
            hold[s] = {"q": amt_f * (1 - k) / fp, "px": fp, "t": t, "e": fp}
            if ledger:
                led.append({"t": t, "s": s, "side": "B", "intended_qty": amt / o[t, s], "fill_px": fp, "frac": min(f, 1.0),
                            "filled_value": amt_f, "cost": amt_f * k, "tag": tag})
        pend_buy = []
        # ---------------- close: mark
        for s, h in hold.items():
            if not np.isnan(c[t, s]):
                h["px"] = c[t, s]
        inv = sum(h["q"] * h["px"] for h in hold.values())
        eq_r = cash + inv
        eq[t] = eq_r / K
        eq_dec = eq_r
        expo[t] = inv / eq_r
        nn[t] = len(hold)
        if log:
            snaps[t] = {s: h["q"] * h["px"] / K for s, h in hold.items()}
        # ---------------- close: decisions (identical to sim5)
        e_t = 1.0 if exposure is None else float(exposure[t])
        is_reb = t >= start and (t - t0) % R == 0
        if not is_reb:
            if exposure is not None and rebalance_on_exposure > 0 and abs(expo[t] - e_t) > max(rebalance_on_exposure, 1e-9):
                scale = e_t / max(expo[t], 1e-12)
                pend_resize = {s: h["q"] * h["px"] / eq_r * scale for s, h in hold.items()}
            continue
        sc = score[t]
        ok = np.flatnonzero(~np.isnan(sc))
        if len(ok) < N:
            continue
        order = ok[np.argsort(-sc[ok], kind="stable")] if tiebreak is None else ok[np.lexsort((tiebreak[ok], -sc[ok]))]
        rank = {s: i for i, s in enumerate(order)}
        pend_sell = [s for s in hold if rank.get(s, 10 ** 9) >= keep]
        kept = [s for s in hold if s not in pend_sell]
        cnt = pd.Series(ind[kept]).value_counts().to_dict() if kept else {}
        slots = N - len(kept)
        new = []
        for s in order:
            if slots <= 0:
                break
            if s in hold or cnt.get(ind[s], 0) >= sector_max:
                continue
            new.append(s)
            cnt[ind[s]] = cnt.get(ind[s], 0) + 1
            slots -= 1
        pend_buy = [(s, e_t / N) for s in new]
        if exposure is not None and rebalance_on_exposure > 0 and abs(expo[t] - e_t) > rebalance_on_exposure:
            scale = e_t / max(expo[t], 1e-12)
            pend_resize = {s: hold[s]["q"] * hold[s]["px"] / eq_r * scale for s in kept}
    last = t1 - 1
    return {"eq": eq, "expo": expo, "trades": trades, "turnover": turn / K, "costs": costs_paid / K, "n_names": nn,
            "holdings": {s: h["q"] * h["px"] / (eq[last] * K) for s, h in hold.items()},
            "shares": {s: h["q"] for s, h in hold.items()}, "cash": cash, "snaps": snaps, "ledger": led,
            "pending": {"sell": list(pend_sell), "buy": [(s, w) for s, w in pend_buy], "resize": dict(pend_resize)}}
