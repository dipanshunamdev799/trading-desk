"""Daily data restricted to 2025-01-01+, point-in-time universe, data-quality report.

All arrays are sliced to dates >= CUTOFF BEFORE any computation, so no pre-2025 price can warm up an indicator.
Universe (each day t): NSE EQ stocks (ETFs/funds removed) with >= 63 sessions of 2025+ history, ranked by 63-day median
traded value (close x volume); top N. Bad prints (a >40% move that reverses within 5 sessions) are excluded for the
affected days +-5 sessions; persistent >40% one-day moves (20 in 2025-26, mostly suspected unadjusted demergers,
e.g. SIEMENS, RAYMOND, ABFRL, TMPV, SKFINDIA - unverified) exclude the stock from 30 sessions before to 5 after.
NOTE: using the next 5 sessions to classify a move is look-ahead for the exclusion mask only; live, a large move would
be checked against exchange corporate-action announcements instead.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import cfg

import dpanel  # noqa: E402  (phase2 module, reused for loading the cached daily matrices)


class D25:
    def __init__(self):
        P = dpanel.load()
        m = P.dates >= cfg.CUTOFF
        self.dates = P.dates[m]
        self.o, self.h, self.l, self.c, self.v = (x[m] for x in (P.o, P.h, P.l, P.c, P.v))
        self.ix = {k: v[m] for k, v in P.ix.items()}
        self.meta = P.meta
        self.keys = P.keys
        self.industry = P.industry
        self.T, self.N = self.c.shape
        self.dint = self.dates.values.astype("datetime64[D]").astype(np.int64)
        self._u = {}
        self.quality = self._quality()

    def _quality(self):
        sym = self.meta["trading_symbol"].astype(str)
        etf = (sym.str.contains("ETF|BEES|IETF|GOLD|LIQUID|NIFTY|SENSEX", regex=True) |
               self.meta["name"].astype(str).str.upper().str.contains(" ETF|FUND|EXCHANGE TRADED", regex=True)).values
        r = self.c / np.vstack([np.full((1, self.N), np.nan), self.c[:-1]]) - 1
        big = np.abs(np.nan_to_num(r)) > 0.40
        bad = np.zeros_like(big)
        events = []
        for t, s in np.argwhere(big):
            if etf[s]:
                continue
            fut = self.c[t + 1:t + 6, s]
            pre = self.c[t - 1, s]
            reverted = np.any(np.abs(fut / pre - 1) < 0.15) if len(fut) and pre == pre else False
            kind = "bad_print_reverted" if reverted else "suspected_unadjusted_corporate_action"
            if reverted:
                bad[max(0, t - 5):t + 6, s] = True
            else:
                # Mostly demergers that Upstox did not adjust (unverified). Exclude the stock 30 sessions before to
                # 5 after, so no strategy holds a position through the artificial drop. Other days are kept.
                bad[max(0, t - 30):t + 6, s] = True
            events.append({"date": str(self.dates[t].date()), "symbol": sym.iloc[s], "ret": float(r[t, s]), "kind": kind})
        dup = 0  # dates are unique by construction of the cache (drop_duplicates on ts)
        nifty_days = int(np.sum(~np.isnan(self.ix["Nifty_50"][:, 3])))
        self.etf, self.bad = etf, bad
        return {"sessions": int(self.T), "first": str(self.dates[0].date()), "last": str(self.dates[-1].date()),
                "nifty_sessions": nifty_days, "etf_or_fund_excluded": int(etf.sum()), "big_moves": events,
                "duplicate_dates": dup}

    def history(self):
        return np.cumsum(~np.isnan(self.c), axis=0)

    def universe(self, top=300, window=63, min_hist=63):
        k = (top, window, min_hist)
        if k in self._u:
            return self._u[k]
        tv = pd.DataFrame(self.c * self.v).rolling(window, min_periods=int(window * .8)).median().values
        ok = (self.history() >= min_hist) & ~np.isnan(self.c) & ~np.isnan(tv) & (self.v > 0) & ~self.etf[None, :] & ~self.bad
        rk = pd.DataFrame(np.where(ok, tv, np.nan)).rank(axis=1, ascending=False, method="first").values
        U = ok & (rk <= top)
        self._u[k] = U
        return U

    def fwd(self, h):
        o1 = np.vstack([self.o[1:], np.full((1, self.N), np.nan)])
        ch = np.vstack([self.c[h:], np.full((h, self.N), np.nan)])
        return ch / o1 - 1

    def excess(self, h, U, mode="ew"):
        r = self.fwd(h)
        ru = np.where(U, r, np.nan)
        ew = np.nanmean(ru, 1)[:, None]
        if mode == "ew":
            return r - ew
        out = r - ew
        for g in np.unique(self.industry):
            if g == "Other":
                continue
            mm = self.industry == g
            sub = ru[:, mm]
            s = np.nansum(sub, 1)[:, None]
            n = np.sum(~np.isnan(sub), 1)[:, None]
            loo_n = n - ~np.isnan(sub)
            out[:, mm] = np.where(loo_n >= 2, r[:, mm] - (s - np.nan_to_num(sub)) / np.maximum(loo_n, 1), out[:, mm])
        return out


if __name__ == "__main__":
    d = D25()
    U = d.universe(300)
    q = d.quality
    print(json.dumps({k: v for k, v in q.items() if k != "big_moves"}, indent=1))
    ev = pd.DataFrame(q["big_moves"])
    print(ev.kind.value_counts().to_dict() if len(ev) else "no big moves")
    print(ev.head(30).to_string(index=False) if len(ev) else "")
    first_full = d.dates[np.argmax(U.sum(1) >= 290)]
    print("universe reaches 290 names on", first_full.date(), "| median names", int(np.median(U.sum(1)[70:])))
    ev.to_csv(cfg.RES / "dq_big_moves.csv", index=False)
    json.dump({k: v for k, v in q.items() if k != "big_moves"}, open(cfg.RES / "dq_summary.json", "w"), indent=1)
