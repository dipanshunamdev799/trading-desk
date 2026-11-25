"""Phase 6 shared code: frozen configs, immutable experiment registry, extended risk metrics. 2025-26 data only."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "phase5"))
sys.path.insert(0, str(HERE.parent))
import p5common as P5  # noqa: E402
import sim5  # noqa: E402
import cfg  # noqa: E402

OUT = cfg.RES / "phase6"
EXP = OUT / "experiments"
for p in (OUT, EXP):
    p.mkdir(parents=True, exist_ok=True)

# ---------------- frozen strategies (DO NOT MODIFY): SPEC_PHASE5.md
C0 = dict(P5.C0)  # N20, keep40, R5, sector_max6, cost .225%/side, min_buy_frac .2
C1_OVERLAY = {"target": 0.15, "window": 20, "rebalance_on_exposure": 0.10, "cap": 1.0, "source": "C0 shadow returns"}


def fingerprint(cfg_: dict) -> str:
    return hashlib.sha256(json.dumps(cfg_, sort_keys=True, default=str).encode()).hexdigest()[:16]


def record(name: str, config: dict, results: dict) -> str:
    """Write-once experiment record keyed by config fingerprint. Refuses to overwrite a different result."""
    fp = fingerprint({"name": name, **config})
    path = EXP / f"{name}__{fp}.json"
    payload = {"name": name, "fingerprint": fp, "config": config, "results": results, "data_window": "2025-01-01..2026-11-13"}
    if path.exists():
        old = json.loads(path.read_text())
        if json.dumps(old["results"], sort_keys=True, default=str) != json.dumps(payload["results"], sort_keys=True, default=str):
            raise RuntimeError(f"immutable record {path.name} exists with different results - investigate, do not overwrite")
        return fp
    path.write_text(json.dumps(payload, indent=1, default=str))
    return fp


import os  # noqa: E402
FIXED = os.environ.get("P6_UNIVERSE") == "fixed"
SUF = "_R" if FIXED else ""  # _R = research-spec universe (INF funds excluded, causal corporate-action mask)


def inputs():
    """Frozen-universe inputs by default; spec-conformant (INF-ISIN funds excluded) when P6_UNIVERSE=fixed."""
    return inputs_fixed() if FIXED else P5.inputs()


def c0_shadow():
    I = inputs()
    return sim5.run(I["A"], I["score"], I["t0"], **C0)


def vt_exposure(c0_eq, target=0.15, window=20, cap=1.0, estimator="std"):
    """Frozen C1 estimator: rolling sample stdev (ddof=1) of C0 shadow close-to-close daily returns x sqrt(252);
    exposure_t = min(cap, target / sigma_t); 1.0 until `window` returns exist. Value at t uses returns up to close t."""
    r = pd.Series(c0_eq).pct_change()
    if estimator == "std":
        v = r.rolling(window).std().values * math.sqrt(252)
    elif estimator == "ewma":
        v = np.sqrt((r ** 2).ewm(alpha=1 - 0.94, adjust=False).mean().values * 252)
    else:
        raise KeyError(estimator)
    return np.nan_to_num(np.clip(target / np.where(v > 0, v, np.nan), 0, cap), nan=1.0)


def run_c1(target=0.15, window=20, reb=0.10, cap=1.0, **extra):
    I = inputs()
    sh = c0_shadow()
    e = vt_exposure(sh["eq"], target, window, cap)
    return sim5.run(I["A"], I["score"], I["t0"], exposure=e, rebalance_on_exposure=reb, **{**C0, **extra}), e


def risk_metrics(res, A, seg=None):
    """Extended risk set on daily returns (whole study period unless seg given)."""
    d = A["dates"]
    eq = pd.Series(res["eq"], index=d).ffill()
    m = cfg.seg_mask(d, seg) if seg else (d >= pd.Timestamp(cfg.SEG["DEV"][0]))
    e = eq[m].dropna()
    r = e.pct_change().dropna()
    dd = e / e.cummax() - 1
    under = (dd < 0).astype(int)
    runs = under.groupby((under != under.shift()).cumsum()).sum()
    wk = (1 + r).resample("W").prod() - 1
    q = np.percentile(r, 5)
    yrs = len(r) / 252
    ex = pd.Series(res["expo"], index=d)[m]
    return {"total": float(e.iloc[-1] / e.iloc[0] - 1), "cagr": float((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1),
            "vol": float(r.std() * math.sqrt(252)), "sharpe": cfg.sharpe(r.values),
            "sortino": float(r.mean() / r[r < 0].std() * math.sqrt(252)), "mdd": float(dd.min()),
            "calmar": float(((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1) / abs(dd.min())),
            "worst_day": float(r.min()), "worst_week": float(wk.min()), "cvar95_day": float(r[r <= q].mean()),
            "max_dd_duration_sessions": int(runs.max()), "avg_exposure": float(ex.mean()),
            "turnover_py": res["turnover"] / yrs, "costs_py": res["costs"] / yrs, "trades": len(res["trades"])}


# ---------------- spec-conformant universe (Phase-6 audit finding: ETF filter missed INF-ISIN funds, e.g. silver ETFs)
_IF = None


def inputs_fixed():
    """Same as inputs(), but funds/ETFs are excluded by ISIN prefix 'INF' (Indian MF/ETF units) in addition to the old
    name filter. This is the behaviour the written spec already required ('ETFs and funds removed')."""
    global _IF
    if _IF is not None:
        return _IF
    I = dict(P5.inputs())
    d = I["d"]
    inf = d.meta["isin"].astype(str).str.startswith("INF").values
    old_etf, old_u, old_bad = d.etf.copy(), dict(d._u), d.bad.copy()
    # causal corporate-action mask (research spec section 14): persistent >40% moves exclude only event day .. +5 sessions
    bad = np.zeros_like(d.bad)
    sym_ix = {s: i for i, s in enumerate(d.meta["trading_symbol"].astype(str))}
    for e in d.quality["big_moves"]:
        s, t = sym_ix.get(e["symbol"]), int(np.searchsorted(d.dates, pd.Timestamp(e["date"])))
        if s is None:
            continue
        lo = t - 5 if e["kind"] == "bad_print_reverted" else t
        bad[max(0, lo):t + 6, s] = True
    d.etf, d.bad, d._u = old_etf | inf, bad, {}
    U = d.universe(300)
    d.etf, d._u, d.bad = old_etf, old_u, old_bad
    I["U"] = U
    I["score"] = np.where(U, I["F"]["volnorm_3m"], np.nan)
    I["inf_mask"] = inf
    _IF = I
    return I


def run_fixed(variant="C0", **extra):
    I = inputs_fixed()
    base = sim5.run(I["A"], I["score"], I["t0"], **{**C0, **({} if variant == "C1" else extra)})
    if variant == "C0":
        return base, None
    e = vt_exposure(base["eq"], C1_OVERLAY["target"], C1_OVERLAY["window"])
    return sim5.run(I["A"], I["score"], I["t0"], exposure=e, rebalance_on_exposure=0.10, **{**C0, **extra}), e
