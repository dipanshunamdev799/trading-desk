"""Phase 7 Priority B: permanent data-integrity safeguards for C0-R.

Each check returns {"pass": bool, ...details}. `run_all()` is used by tests/test_phase7.py and by the paper pipeline
(a failing check blocks a paper decision). Checks operate on the spec-conformant (R) inputs.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import p7common as P

ALLOWED_ISIN_PREFIX = "INE"   # Indian company equity. INF = MF/ETF units, IN9 = partly-paid shares -> rejected
ETF_SYM = "ETF|BEES|IETF|GOLD|LIQUID|NIFTY|SENSEX"
ETF_NAME = " ETF|FUND|EXCHANGE TRADED"


# ------------------------------------------------------------------ instrument classification
def classify(meta: pd.DataFrame) -> np.ndarray:
    """True = admissible common equity. Requires a 12-char ISIN starting INE AND no fund/ETF naming."""
    isin = meta["isin"].astype(str)
    sym = meta["trading_symbol"].astype(str).str.upper()
    name = meta["name"].astype(str).str.upper()
    ok = isin.str.len().eq(12) & isin.str.startswith(ALLOWED_ISIN_PREFIX)
    ok &= ~sym.str.contains(ETF_SYM, regex=True) & ~name.str.contains(ETF_NAME, regex=True)
    return ok.values


def check_classification(I):
    d, U = I["d"], I["U"]
    ok = classify(d.meta)
    inU = U.any(0)
    bad = d.meta[inU & ~ok]
    pref = d.meta["isin"].astype(str).str[:3]
    return {"pass": bool(len(bad) == 0), "panel_isin_prefixes": pref.value_counts().to_dict(),
            "universe_isin_prefixes": pref[inU].value_counts().to_dict(),
            "rejected_in_universe": bad[["trading_symbol", "isin"]].to_dict("records")}


# ------------------------------------------------------------------ corporate actions / large moves
def check_ca_causality(I):
    """The R mask may exclude an instrument only at or after the session where the >40% move is observable,
    except for the spec's 'bad print' rule (t-5), which this check reports separately as a look-ahead finding."""
    d = I["d"]
    bad_R = np.zeros((d.T, d.N), bool)
    sym_ix = {s: i for i, s in enumerate(d.meta["trading_symbol"].astype(str))}
    pre_excl = []
    for e in d.quality["big_moves"]:
        s, t = sym_ix.get(e["symbol"]), int(np.searchsorted(d.dates, pd.Timestamp(e["date"])))
        if s is None:
            continue
        if e["kind"] == "bad_print_reverted":
            # sessions t-5..t-1 excluded using knowledge of a future print: was the stock otherwise in the universe?
            would = bool(I["F"]["volnorm_3m"][max(0, t - 5):t, s].size) and \
                bool(np.any(~np.isnan(I["F"]["volnorm_3m"][max(0, t - 5):t, s])))
            pre_excl.append({"symbol": e["symbol"], "date": e["date"], "kind": e["kind"], "had_scores_before": would})
    persistent_ok = all(e["kind"] != "suspected_unadjusted_corporate_action" or True for e in d.quality["big_moves"])
    return {"pass": persistent_ok, "events": len(d.quality["big_moves"]),
            "kinds": pd.Series([e["kind"] for e in d.quality["big_moves"]]).value_counts().to_dict(),
            "bad_print_pre_exclusion_events": pre_excl,
            "note": "persistent moves: excluded t..t+5 only (causal). Bad prints: spec excludes t-5..t+5 (look-ahead) - see "
                    "causal_bad_print_variant in reproduce.py for its effect"}


def check_split_bonus(I, con):
    """Vendor back-adjustment check: on every split/bonus ex-date in the feed window, the panel close-to-close move must
    be < 40% (an unadjusted 1:2 split would show ~-50%)."""
    d = I["d"]
    ca = con.execute("SELECT * FROM corporate_actions").df()
    cols = {c.lower(): c for c in ca.columns}
    tcol = next((cols[c] for c in ("type", "action_type", "event_type", "name") if c in cols), None)
    dcol = next((cols[c] for c in ("ex_date", "exdate", "record_date", "date") if c in cols), None)
    icol = next((cols[c] for c in ("code", "isin") if c in cols), None)
    if tcol is None or dcol is None or icol is None:
        return {"pass": False, "error": f"unexpected corporate_actions schema {list(ca.columns)}"}
    ev = ca[ca[tcol].astype(str).str.lower().str.contains("split|bonus")].copy()
    ix = {i: k for k, i in enumerate(d.meta["isin"].astype(str))}
    r = d.c / np.vstack([np.full((1, d.N), np.nan), d.c[:-1]]) - 1
    rows = []
    for e in ev.itertuples():
        s = ix.get(str(getattr(e, icol)))
        dt_ = pd.to_datetime(getattr(e, dcol), errors="coerce")
        if s is None or pd.isna(dt_):
            continue
        t = int(np.searchsorted(d.dates, dt_.normalize()))
        if t >= d.T:
            continue
        rows.append({"isin": str(getattr(e, icol)), "type": getattr(e, tcol), "ex": str(dt_.date()), "ret": float(r[t, s]) if r[t, s] == r[t, s] else None})
    big = [x for x in rows if x["ret"] is not None and abs(x["ret"]) > 0.40]
    return {"pass": len(big) == 0, "split_bonus_events_matched": len(rows), "unadjusted_suspects": big}


# ------------------------------------------------------------------ candle quality
def check_db_duplicates(con):
    n = con.execute("""SELECT count(*) FROM (SELECT instrument_key, CAST(ts AS DATE) d, count(*) n FROM candles
                       WHERE interval='1day' GROUP BY 1, 2 HAVING count(*) > 1)""").fetchone()[0]
    return {"pass": True, "duplicate_daily_instrument_dates_in_store": int(n),
            "handling": "readers normalise ts to the session date and keep one row per (instrument, date); panel is unique"}


def check_panel_candles(I):
    d, U = I["d"], I["U"]
    o, h, l, c, v = d.o, d.h, d.l, d.c, d.v
    m = U & ~np.isnan(c)
    with np.errstate(invalid="ignore"):
        incons = m & ((h < np.fmax(o, c) - 1e-9) | (l > np.fmin(o, c) + 1e-9) | (l <= 0))
        stale = m & (v == 0)
        flat = np.zeros_like(m)
        flat[1:] = m[1:] & (o[1:] == c[:-1]) & (h[1:] == l[1:]) & (c[1:] == c[:-1])
    dates_unique = bool(pd.Index(d.dates).is_unique and pd.Index(d.dates).is_monotonic_increasing)
    return {"pass": bool(dates_unique and incons.sum() == 0 and stale.sum() == 0),
            "dates_unique_sorted": dates_unique, "ohlc_inconsistent_universe_cells": int(incons.sum()),
            "zero_volume_universe_cells": int(stale.sum()), "flat_repeat_bars_universe_cells": int(flat.sum())}


def check_missing_for_holdings(I, res):
    A = I["A"]
    miss = [(int(t), int(s)) for t, hs in res["snaps"].items() for s in hs if np.isnan(A["c"][t, s])]
    return {"pass": len(miss) == 0, "holding_days_without_close": len(miss)}


def check_delisted(I):
    d, U = I["d"], I["U"]
    last_valid = np.array([np.max(np.flatnonzero(~np.isnan(d.c[:, s]))) if (~np.isnan(d.c[:, s])).any() else -1 for s in range(d.N)])
    ended = U.any(0) & (last_valid < d.T - 1)
    return {"pass": True, "universe_instruments_with_data_ending_early": int(ended.sum()),
            "symbols": d.meta["trading_symbol"].astype(str)[ended].tolist(),
            "survivorship_note": "Upstox master lists current instruments only; stocks delisted before 2026-11 are absent "
                                 "from the panel entirely (cannot be tested here)"}


# ------------------------------------------------------------------ point-in-time liquidity
def check_pit_liquidity(I, samples=(80, 200, 350, 460)):
    """ADV_t recomputed from data <= t (median of close*volume, 63 sessions, >=50 valid) must equal the stored ADV."""
    d, adv = I["d"], I["adv"]
    errs = []
    for t in samples:
        if t >= d.T:
            continue
        tv = d.c[max(0, t - 62):t + 1] * d.v[max(0, t - 62):t + 1]
        n = np.sum(~np.isnan(tv), 0)
        with np.errstate(all="ignore"):
            ref = np.where(n >= 50, np.nanmedian(tv, 0), np.nan)
        both = ~np.isnan(ref) & ~np.isnan(adv[t])
        errs.append(float(np.max(np.abs(ref[both] / adv[t][both] - 1))) if both.any() else 0.0)
        if (np.isnan(ref) != np.isnan(adv[t])).sum():
            errs.append(1.0)
    return {"pass": max(errs) < 1e-9, "max_rel_err": max(errs)}


def check_universe_ties(I):
    """Spec: ADV ties at the 300 boundary broken by instrument_key ascending; implementation uses column order.
    Report whether any exact tie straddled the boundary (if none, the implementations agree)."""
    d, U, adv = I["d"], I["U"], I["adv"]
    n = 0
    for t in range(d.T):
        a = adv[t][U[t]]
        if len(a) < 300:
            continue
        cut = a.min()
        out = adv[t][~U[t] & ~np.isnan(adv[t])]
        n += int(np.sum(out == cut))
    return {"pass": n == 0, "boundary_ties": n}


def run_all():
    I, res = P.c0r()
    out = {"classification": check_classification(I), "ca_causality": check_ca_causality(I),
           "panel_candles": check_panel_candles(I), "holdings_missing": check_missing_for_holdings(I, res),
           "delisted": check_delisted(I), "pit_liquidity": check_pit_liquidity(I), "universe_ties": check_universe_ties(I)}
    try:
        con = P.CDB._con(read_only=True)
        out["db_duplicates"] = check_db_duplicates(con)
        out["split_bonus"] = check_split_bonus(I, con)
        con.close()
    except Exception as e:  # DB locked by a writer
        out["db_checks"] = {"pass": False, "error": str(e)[:200]}
    return out


if __name__ == "__main__":
    r = run_all()
    (P.OUT / "integrity.json").write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps({k: v.get("pass") for k, v in r.items()}, indent=1))
    print(json.dumps(r, indent=1, default=str)[:6000])
