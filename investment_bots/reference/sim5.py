"""Phase 5 ranking-portfolio simulator: implements the Candidate C spec exactly (STRATEGY_SPEC.md) plus versioned
variant switches. Independent of psim/Book (written from the spec), used as the third implementation.

Daily cycle for day t (decisions use data up to the close of t; orders fill at the open of t+1):
  open  : execute pending sells (full exits) at the open; mark holdings to the open; execute pending buys/resizes
  close : mark to close; record equity
  close : on a decision day, rank eligible stocks and create orders for the next open
C0 semantics ('drift' mode): sell holdings ranked >= keep (0-based rank >= keep-1 means rank number >= keep+... see note),
buy highest-ranked non-held names until N holdings, at most sector_max per industry; new buy = equity_open/N limited by
cash, skipped if < min_buy_frac of a slot; positions drift between rebalances.
Rank convention: 0-based position in the descending score order (rank 0 = best). "Sell if rank >= keep" with keep=40
means the 41st name and below are sold, exactly as Book (paper engine) and the spec ("ranked 41st or worse").
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd


def run(A, score, t0, N=20, keep=40, R=5, sector_max=6, cost=0.00225, min_buy_frac=0.2, first_decision=True,
        cand_pool=None, mode="drift", weights=None, pos_cap=None, band=0.0, exposure=None, rebalance_on_exposure=0.0,
        entry_rank=None, impact_k=0.0, capital=1e6, adv=None, sig=None, sector_cap_frac=None, t1=None, stop_pct=0.0, cost_fn=None, part_cap=None, log=False, tiebreak=None):
    """Returns dict(eq, expo, trades, turnover, costs, gross_buys, n_names).
    mode 'drift'   : C0 behaviour (full exits/entries only).
    mode 'reweight': on decision days every holding is reset to its target weight (equal or `weights`), subject to
                     a no-trade band `band` (fraction of equity) and `pos_cap`; `exposure[t]` scales targets.
    exposure       : optional array of target gross exposure (0..1). In drift mode it scales the size of new buys and,
                     if |current-target| > rebalance_on_exposure, all positions are scaled proportionally next open.
    cand_pool      : if 'topN', candidates are restricted to the top-N ranks (reproduces psim); default = full ranking.
    impact_k       : square-root impact, extra cost per side = impact_k * daily_vol * sqrt(trade_value / ADV_value).
    """
    o, c, ind = A["o"], A["c"], A["industry"]
    T = c.shape[0]
    t1 = T if t1 is None else t1
    cash, hold = 1.0, {}  # hold[s] = {"v": value, "px": last mark price, "t": entry index, "e": entry price}
    pend_sell, pend_buy, pend_resize = [], [], {}
    eq = np.full(T, np.nan)
    expo = np.zeros(T)
    trades, turn, costs_paid, nn = [], 0.0, 0.0, np.zeros(T)
    start = t0 if first_decision else t0 + 1
    snaps = {}  # optional daily close snapshots {t: {stock: value}} (log=True)
    eq[t0 - 1 if t0 > 0 else 0] = 1.0

    def tc(s, value, t, side="b"):
        if cost_fn is not None:  # account-size-aware cost model (Phase 6); value is a fraction of equity
            return cost_fn(s, value, t, side)
        k = cost
        if impact_k and adv is not None and value > 0:
            a = adv[t - 1, s] if t > 0 else np.nan
            sg = sig[t - 1, s] if t > 0 else np.nan
            if a == a and a > 0 and sg == sg:
                k += impact_k * sg * math.sqrt(value * capital / a)
        return k

    for t in range(t0, t1):
        # ---------------- open: sells
        for s in pend_sell:
            if s in hold and not np.isnan(o[t, s]):
                h = hold[s]
                v_full = h["v"] * o[t, s] / h["px"]
                lim = (part_cap * adv[t - 1, s] / capital) if (part_cap and adv is not None and adv[t - 1, s] == adv[t - 1, s]) else np.inf
                if v_full > lim:  # partial fill: sell what the participation cap allows, rest stays pending
                    v = lim
                    h["v"] = v_full - v
                    h["px"] = o[t, s]
                    k = tc(s, v, t, "s")
                    cash += v * (1 - k)
                    costs_paid += v * k
                    turn += v
                    continue
                hold.pop(s)
                v = v_full
                k = tc(s, v, t, "s")
                cash += v * (1 - k)
                costs_paid += v * k
                turn += v
                trades.append((s, h["t"], t, o[t, s] / h["e"] - 1))
        pend_sell = [s for s in pend_sell if s in hold]  # unfilled (no open price) stay pending
        for s, h in hold.items():
            if not np.isnan(o[t, s]):
                h["v"] *= o[t, s] / h["px"]
                h["px"] = o[t, s]
        eq_open = cash + sum(h["v"] for h in hold.values())
        # resizes (reweight / exposure scaling): sells first, then buys
        for s, tgt in sorted(pend_resize.items(), key=lambda x: (x[1] - hold.get(x[0], {"v": 0})["v"] / max(eq_open, 1e-12))):
            if s not in hold or np.isnan(o[t, s]):
                continue
            d = tgt * eq_open - hold[s]["v"]
            if d < 0:
                v = -d
                k = tc(s, v, t)
                hold[s]["v"] -= v
                cash += v * (1 - k)
                costs_paid += v * k
                turn += v
            elif d > 0:
                v = min(d, cash)
                if v <= 0:
                    continue
                k = tc(s, v, t)
                cash -= v
                hold[s]["v"] += v * (1 - k)
                costs_paid += v * k
                turn += v
        pend_resize = {}
        # buys
        for s, w in pend_buy:
            if len(hold) >= N or s in hold or np.isnan(o[t, s]):
                continue
            amt = min(w * eq_open, cash)
            if part_cap and adv is not None and adv[t - 1, s] == adv[t - 1, s]:
                amt = min(amt, part_cap * adv[t - 1, s] / capital)  # partial fill (no carry-over)
            if amt < min_buy_frac * eq_open / N:
                continue
            k = tc(s, amt, t)
            cash -= amt
            costs_paid += amt * k
            turn += amt
            hold[s] = {"v": amt * (1 - k), "px": o[t, s], "t": t, "e": o[t, s]}
        pend_buy = []
        # ---------------- close: mark
        for s, h in hold.items():
            if not np.isnan(c[t, s]):
                h["v"] *= c[t, s] / h["px"]
                h["px"] = c[t, s]
        inv = sum(h["v"] for h in hold.values())
        eq[t] = cash + inv
        expo[t] = inv / eq[t]
        nn[t] = len(hold)
        if log:
            snaps[t] = {s: h["v"] for s, h in hold.items()}
        # ---------------- close: decisions
        if stop_pct:  # optional per-position stop on close (variant only; not part of C0)
            for s, h in hold.items():
                if s not in pend_sell and not np.isnan(c[t, s]) and c[t, s] / h["e"] - 1 < -stop_pct:
                    pend_sell.append(s)
        e_t = 1.0 if exposure is None else float(exposure[t])
        is_reb = t >= start and (t - t0) % R == 0
        if not is_reb:
            if exposure is not None and abs(expo[t] - e_t) > max(rebalance_on_exposure, 1e-9) and rebalance_on_exposure > 0:
                scale = e_t / max(expo[t], 1e-12)
                pend_resize = {s: h["v"] / eq[t] * scale for s, h in hold.items()}
            continue
        sc = score[t]
        ok = np.flatnonzero(~np.isnan(sc))
        if len(ok) < N:
            continue
        if tiebreak is None:  # frozen behaviour: ties keep panel column order (stable sort)
            order = ok[np.argsort(-sc[ok], kind="stable")]
        else:  # research spec: ties broken by instrument_key ascending (tiebreak = rank of key)
            order = ok[np.lexsort((tiebreak[ok], -sc[ok]))]
        rank = {s: i for i, s in enumerate(order)}
        pend_sell = [s for s in hold if rank.get(s, 10 ** 9) >= keep]
        kept = [s for s in hold if s not in pend_sell]
        cap = sector_max if sector_cap_frac is None else max(1, math.ceil(sector_cap_frac * N))
        cnt = pd.Series(ind[kept]).value_counts().to_dict() if kept else {}
        slots = N - len(kept)
        pool = order[:N] if cand_pool == "topN" else (order[:entry_rank] if entry_rank else order)
        new = []
        for s in pool:
            if slots <= 0:
                break
            if s in hold or cnt.get(ind[s], 0) >= cap:
                continue
            new.append(s)
            cnt[ind[s]] = cnt.get(ind[s], 0) + 1
            slots -= 1
        names = kept + new
        if mode == "drift":
            base = 1.0 / N
            pend_buy = [(s, base * e_t) for s in new]
            if exposure is not None and rebalance_on_exposure > 0 and abs(expo[t] - e_t) > rebalance_on_exposure:
                scale = e_t / max(expo[t], 1e-12)
                pend_resize = {s: hold[s]["v"] / eq[t] * scale for s in kept}
        else:  # reweight
            if weights is not None:
                w = np.array([weights[t, s] if weights[t, s] == weights[t, s] else 0.0 for s in names])
                w = w / w.sum() * (len(names) / N) if w.sum() > 0 else np.full(len(names), 1.0 / N)
            else:
                w = np.full(len(names), 1.0 / N)
            if pos_cap is not None:
                w = np.minimum(w, pos_cap)
            w = w * e_t
            tw = dict(zip(names, w))
            for s in kept:
                cur = hold[s]["v"] / eq[t]
                if abs(tw[s] - cur) > band:
                    pend_resize[s] = tw[s]
            pend_buy = [(s, tw[s]) for s in new]
    return {"eq": eq, "expo": expo, "trades": trades, "turnover": turn, "costs": costs_paid, "n_names": nn,
            "holdings": {s: h["v"] / eq[t] for s, h in hold.items()}, "snaps": snaps,
            "pending": {"sell": list(pend_sell), "buy": [(s, w) for s, w in pend_buy], "resize": dict(pend_resize)}}
