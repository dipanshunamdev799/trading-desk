#!/usr/bin/env python3
"""
NIFTY Max Pain research dashboard.

Single script: fetch option-chain / OI / max-pain / spot data from Upstox
(via upstox_analytics.UpstoxAnalyticsClient) and plot research charts with matplotlib.

Charts
------
A. Intraday Max Pain vs NIFTY spot (Upstox interval insights)
B. Theoretical payout curve by candidate settlement price (local calc from OI)
C. Strike-wise Call / Put OI (and OI change)
D. Historical Max Pain at a fixed observation time vs actual expiry close

Validation printed to stdout: chain completeness, edge minima, ties,
local-vs-provider Max Pain agreement, data freshness.

Usage
-----
  python nifty_max_pain.py
  python nifty_max_pain.py --expiry 2026-10-27 --date 2026-10-23
  python nifty_max_pain.py --history-days 45 --save max_pain.png --no-show
  python nifty_max_pain.py --list-expiries

Env
---
  UPSTOX_ANALYTICS_TOKEN   (or pass --token; .env is loaded from script directory)
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Path / imports
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:
    # Token can still come from the environment.
    pass

from upstox_analytics import UpstoxAnalyticsClient, UpstoxAPIError  # noqa: E402

try:
    import matplotlib

    matplotlib.use("Agg")  # headless-safe; --show switches to interactive
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "matplotlib is required. Install it in the interpreter you run this script with:\n"
        "  python -m pip install matplotlib numpy requests python-dotenv\n"
        f"Import error: {exc}"
    )


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NIFTY_KEY = "NSE_INDEX|Nifty 50"
NIFTY_NAME = "NIFTY 50"
DEFAULT_LOT_SIZE = 50  # fallback only; real lot size comes from contracts
SIGNAL_TIME = "10:15"  # fixed observation time for historical research chart
IST_FMT = "%d-%m-%Y"
API_DATE = "%Y-%m-%d"

# Trading-desk palette (matches project DESIGN.md)
C_BG = "#0B0F14"
C_SURFACE = "#121820"
C_BORDER = "#243041"
C_INK = "#E8EDF2"
C_MUTED = "#8B9AAB"
C_ACCENT = "#2DD4A8"
C_DANGER = "#F07178"
C_WARN = "#E5C07B"
C_INFO = "#61AFEF"
C_CALL = "#E06C75"
C_PUT = "#61AFEF"


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class StrikeRow:
    strike: float
    call_oi: float = 0.0
    put_oi: float = 0.0
    call_prev_oi: Optional[float] = None
    put_prev_oi: Optional[float] = None
    call_ltp: float = 0.0
    put_ltp: float = 0.0


@dataclass
class ChainSnapshot:
    expiry: str
    spot: float
    lot_size: int
    rows: List[StrikeRow]
    fetched_at: datetime
    source: str = "upstox.option_chain"

    @property
    def strikes(self) -> np.ndarray:
        return np.array([r.strike for r in self.rows], dtype=float)

    @property
    def call_oi(self) -> np.ndarray:
        return np.array([r.call_oi for r in self.rows], dtype=float)

    @property
    def put_oi(self) -> np.ndarray:
        return np.array([r.put_oi for r in self.rows], dtype=float)


@dataclass
class MaxPainResult:
    strike: float
    min_payout: float
    tied_strikes: List[float]
    candidates: np.ndarray
    call_payout: np.ndarray
    put_payout: np.ndarray
    total_payout: np.ndarray
    warnings: List[str] = field(default_factory=list)

    @property
    def broadness_pts(self) -> float:
        """Half-width of the near-minimum band (payout within 1% of min)."""
        if self.total_payout.size == 0 or self.min_payout <= 0:
            return float("nan")
        thr = self.min_payout * 1.01
        band = self.candidates[self.total_payout <= thr]
        return float((band.max() - band.min()) / 2.0) if band.size else 0.0


# ---------------------------------------------------------------------------
# Max Pain calculation
# ---------------------------------------------------------------------------


def compute_max_pain(
    strikes: Sequence[float],
    call_oi: Sequence[float],
    put_oi: Sequence[float],
    lot_size: int = 1,
    *, oi_in_units: bool = False,
) -> MaxPainResult:
    """
    Max Pain = argmin_S [ sum_K OI_C(K)*max(S-K,0) + OI_P(K)*max(K-S,0) ].

    By default OI counts lots, multiplied by lot_size for rupee terms. Upstox
    supplies underlying quantities: pass oi_in_units=True to avoid multiplying
    those quantities by lot_size a second time. The argmin is unchanged.

    Candidate settlement prices are the observed strikes (standard for index
    options). Warnings cover empty chains, all-zero OI, edge minima, and ties.
    """
    warnings: List[str] = []
    strikes_arr = np.asarray(strikes, dtype=float)
    call_arr = np.asarray(call_oi, dtype=float)
    put_arr = np.asarray(put_oi, dtype=float)

    if strikes_arr.size == 0:
        warnings.append("empty chain: no strikes")
        empty = np.array([])
        return MaxPainResult(
            strike=float("nan"),
            min_payout=float("nan"),
            tied_strikes=[],
            candidates=empty,
            call_payout=empty,
            put_payout=empty,
            total_payout=empty,
            warnings=warnings,
        )

    if np.any(call_arr < 0) or np.any(put_arr < 0):
        warnings.append("negative OI present; clipped to 0")
        call_arr = np.clip(call_arr, 0, None)
        put_arr = np.clip(put_arr, 0, None)

    if float(call_arr.sum() + put_arr.sum()) <= 0:
        warnings.append("all OI is zero: Max Pain undefined")
        empty = np.array([])
        return MaxPainResult(
            strike=float("nan"),
            min_payout=float("nan"),
            tied_strikes=[],
            candidates=empty,
            call_payout=empty,
            put_payout=empty,
            total_payout=empty,
            warnings=warnings,
        )

    order = np.argsort(strikes_arr)
    k = strikes_arr[order]
    c_oi = call_arr[order]
    p_oi = put_arr[order]
    scale = 1.0 if oi_in_units else float(lot_size) if lot_size and lot_size > 0 else 1.0

    # Vectorized payout curve: for each candidate S (strike), sum over all K.
    # payout_total[i] = scale * sum_j [ c_oi[j]*max(S_i-K_j,0) + p_oi[j]*max(K_j-S_i,0) ]
    s = k[:, None]  # (M, 1)
    kk = k[None, :]  # (1, N)
    call_pay = (c_oi[None, :] * np.maximum(s - kk, 0.0)).sum(axis=1) * scale
    put_pay = (p_oi[None, :] * np.maximum(kk - s, 0.0)).sum(axis=1) * scale
    total = call_pay + put_pay

    min_idx = int(np.argmin(total))
    min_val = float(total[min_idx])
    # Ties: exact match within float tolerance relative to curve magnitude.
    tol = max(1.0, abs(min_val) * 1e-9)
    tie_mask = np.abs(total - min_val) <= tol
    tied = [float(x) for x in k[tie_mask]]
    if len(tied) > 1:
        warnings.append(f"tied minima at strikes {tied}")

    if min_idx == 0 or min_idx == len(k) - 1:
        warnings.append(
            f"minimum sits at calculation edge ({k[min_idx]}); expand strike range"
        )

    # Near-minimum band (precision of a single number)
    thr = min_val * 1.01 if min_val > 0 else min_val + 1.0
    band = k[total <= thr]
    if band.size >= 5:
        warnings.append(
            f"broad minimum: {band.size} strikes within 1% of min payout "
            f"({band.min():.0f}–{band.max():.0f})"
        )

    return MaxPainResult(
        strike=float(k[min_idx]),
        min_payout=min_val,
        tied_strikes=tied,
        candidates=k,
        call_payout=call_pay,
        put_payout=put_pay,
        total_payout=total,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Premium-adjusted hypothetical short-option P&L
# ---------------------------------------------------------------------------


@dataclass
class PremiumPnlResult:
    """
    Hypothetical expiry P&L for short AND long option portfolios (NOT actual market P&L).

    Short (seller)  PnL(S) = PremiumValue − P_total(S)
    Long  (buyer)   PnL(S) = −short PnL(S)   [same assumed entry premium]
    """

    candidates: np.ndarray
    # Seller (short) side
    call_pnl: np.ndarray  # short call
    put_pnl: np.ndarray  # short put
    combined_pnl: np.ndarray  # short call + short put
    # Buyer (long) side — explicit series (equals −seller)
    buyer_call_pnl: np.ndarray
    buyer_put_pnl: np.ndarray
    buyer_combined_pnl: np.ndarray
    premium_value: float
    lot_size: float
    call_oi_coverage: float
    put_oi_coverage: float
    min_pnl_price: float  # argmin of seller combined (== argmax payout)
    min_pnl_value: float
    breakeven_prices: List[float]
    pnl_at_spot: Optional[float]
    pnl_at_max_pain: Optional[float]
    scenario: str
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        # Buyer extremes are the mirror of seller
        if self.buyer_combined_pnl.size:
            b_idx = int(np.argmax(self.buyer_combined_pnl))
            max_buy_price = float(self.candidates[b_idx])
            max_buy_val = float(self.buyer_combined_pnl[b_idx])
        else:
            max_buy_price = float("nan")
            max_buy_val = float("nan")
        return {
            "scenario": self.scenario,
            "premium_value": self.premium_value,
            "lot_size": self.lot_size,
            "call_oi_coverage_pct": round(self.call_oi_coverage * 100, 2),
            "put_oi_coverage_pct": round(self.put_oi_coverage * 100, 2),
            "min_pnl_price": self.min_pnl_price,
            "min_pnl_value": self.min_pnl_value,
            "max_buy_pnl_price": max_buy_price,
            "max_buy_pnl_value": max_buy_val,
            "breakeven_prices": self.breakeven_prices,
            "pnl_at_spot": self.pnl_at_spot,
            "pnl_at_max_pain": self.pnl_at_max_pain,
            "warnings": self.warnings,
        }


def validate_chain_for_pnl(
    call_oi: Sequence[float],
    put_oi: Sequence[float],
    call_prem: Sequence[float],
    put_prem: Sequence[float],
    lot_size: float,
) -> List[str]:
    """Data-quality checks; returns warnings (empty = clean)."""
    warnings: List[str] = []
    if lot_size is None or float(lot_size) <= 0:
        warnings.append("invalid lot size")
    c_oi = np.asarray(call_oi, dtype=float)
    p_oi = np.asarray(put_oi, dtype=float)
    c_pr = np.asarray(call_prem, dtype=float)
    p_pr = np.asarray(put_prem, dtype=float)
    if np.any(~np.isfinite(c_oi)) or np.any(~np.isfinite(p_oi)):
        warnings.append("non-finite OI present")
    if np.any(c_oi < 0) or np.any(p_oi < 0):
        warnings.append("negative OI present")
    # zero LTP on non-zero OI is suspicious
    zc = int(np.sum((c_oi > 0) & (c_pr <= 0)))
    zp = int(np.sum((p_oi > 0) & (p_pr <= 0)))
    if zc:
        warnings.append(f"{zc} call strikes with OI but zero/missing premium")
    if zp:
        warnings.append(f"{zp} put strikes with OI but zero/missing premium")
    return warnings


def compute_premium_pnl(
    strikes: Sequence[float],
    call_oi: Sequence[float],
    put_oi: Sequence[float],
    call_prem: Sequence[float],
    put_prem: Sequence[float],
    lot_size: float = 1,
    premium_scale: float = 1.0,
    spot: Optional[float] = None,
    max_pain: Optional[float] = None,
    scenario: str = "snapshot",
    candidates: Optional[Sequence[float]] = None,
    oi_in_units: bool = False,
) -> PremiumPnlResult:
    """
    Hypothetical short-option expiry P&L.

    PnL_C(S) = L * Σ OI_C(K) * (C_K − max(S−K,0))
    PnL_P(S) = L * Σ OI_P(K) * (P_K − max(K−S,0))
    PnL(S)   = PnL_C(S) + PnL_P(S) = PremiumValue − P_total(S)

    L = 1 for OI already in underlying units (oi_in_units=True), otherwise lot_size.
    Premiums are scaled by `premium_scale` (0.9 / 1.0 / 1.1 sensitivity).
    Zero LTP with positive OI is treated as missing (excluded from premium
    contribution and from PnL units that rely on that premium) but still
    contributes intrinsic payout risk via OI in the identity check.
    """
    warnings = validate_chain_for_pnl(call_oi, put_oi, call_prem, put_prem, lot_size)
    k = np.asarray(strikes, dtype=float)
    c_oi = np.clip(np.asarray(call_oi, dtype=float), 0, None)
    p_oi = np.clip(np.asarray(put_oi, dtype=float), 0, None)
    c_pr = np.asarray(call_prem, dtype=float) * float(premium_scale)
    p_pr = np.asarray(put_prem, dtype=float) * float(premium_scale)
    # missing premium => treat as 0 for valuation but track coverage
    c_ok = np.isfinite(c_pr) & (c_pr >= 0) & ((c_pr > 0) | (c_oi == 0))
    p_ok = np.isfinite(p_pr) & (p_pr >= 0) & ((p_pr > 0) | (p_oi == 0))
    c_pr = np.where(c_ok, c_pr, 0.0)
    p_pr = np.where(p_ok, p_pr, 0.0)

    empty = np.array([])
    if k.size == 0:
        return PremiumPnlResult(
            candidates=empty,
            call_pnl=empty,
            put_pnl=empty,
            combined_pnl=empty,
            buyer_call_pnl=empty,
            buyer_put_pnl=empty,
            buyer_combined_pnl=empty,
            premium_value=0.0,
            lot_size=float(lot_size),
            call_oi_coverage=0.0,
            put_oi_coverage=0.0,
            min_pnl_price=float("nan"),
            min_pnl_value=float("nan"),
            breakeven_prices=[],
            pnl_at_spot=None,
            pnl_at_max_pain=None,
            scenario=scenario,
            warnings=warnings + ["empty chain"],
        )

    scale = 1.0 if oi_in_units else float(lot_size) if lot_size and lot_size > 0 else 1.0
    call_oi_cov = float(c_oi[c_ok].sum() / c_oi.sum()) if c_oi.sum() > 0 else 1.0
    put_oi_cov = float(p_oi[p_ok].sum() / p_oi.sum()) if p_oi.sum() > 0 else 1.0

    # Premium collected (constant across S)
    premium_value = float(scale * (np.sum(c_oi * c_pr) + np.sum(p_oi * p_pr)))

    if candidates is not None and len(candidates):
        s_arr = np.asarray(candidates, dtype=float)
    else:
        s_arr = k  # evaluate at strikes like max-pain

    # Vectorized
    s = s_arr[:, None]
    kk = k[None, :]
    call_intrinsic = np.maximum(s - kk, 0.0)
    put_intrinsic = np.maximum(kk - s, 0.0)

    # Seller PnL = scale * Σ OI * (prem - intrinsic)
    call_pnl = (
        scale
        * (
            (c_oi * c_pr)[None, :]
            - c_oi[None, :] * call_intrinsic
        ).sum(axis=1)
    )
    put_pnl = (
        scale
        * (
            (p_oi * p_pr)[None, :]
            - p_oi[None, :] * put_intrinsic
        ).sum(axis=1)
    )
    combined = call_pnl + put_pnl

    # Buyer (long) PnL = scale * Σ OI * (intrinsic - prem)  == -seller
    buyer_call = scale * (
        c_oi[None, :] * call_intrinsic - (c_oi * c_pr)[None, :]
    ).sum(axis=1)
    buyer_put = scale * (
        p_oi[None, :] * put_intrinsic - (p_oi * p_pr)[None, :]
    ).sum(axis=1)
    buyer_combined = buyer_call + buyer_put

    # Identity check: combined should equal premium_value - total_payout
    total_payout = scale * (
        (c_oi[None, :] * call_intrinsic).sum(axis=1)
        + (p_oi[None, :] * put_intrinsic).sum(axis=1)
    )
    ident_err = float(np.max(np.abs(combined - (premium_value - total_payout)))) if s_arr.size else 0.0
    tol = max(1.0, abs(premium_value) * 1e-6)
    if ident_err > tol:
        warnings.append(f"identity check residual {ident_err:.2f} > tol {tol:.2f}")

    min_idx = int(np.argmin(combined))
    min_price = float(s_arr[min_idx])
    min_val = float(combined[min_idx])
    if min_idx == 0 or min_idx == len(s_arr) - 1:
        warnings.append("minimum PnL at candidate-range edge; expand range")

    # Breakevens: sign changes
    bes: List[float] = []
    for i in range(len(s_arr) - 1):
        y0, y1 = combined[i], combined[i + 1]
        if y0 == 0:
            bes.append(float(s_arr[i]))
        elif y0 * y1 < 0:
            # linear interp on piecewise-linear curve
            t = y0 / (y0 - y1)
            bes.append(float(s_arr[i] + t * (s_arr[i + 1] - s_arr[i])))
    if len(s_arr) and combined[-1] == 0:
        bes.append(float(s_arr[-1]))

    def _at(x: Optional[float]) -> Optional[float]:
        if x is None or not np.isfinite(x):
            return None
        # Evaluate the actual settlement, including prices between strikes and
        # outside the plotted range. Nearest-strike lookup changes the payoff.
        return float(premium_value - scale * (
            np.sum(c_oi * np.maximum(float(x) - k, 0.0)) +
            np.sum(p_oi * np.maximum(k - float(x), 0.0))))

    return PremiumPnlResult(
        candidates=s_arr,
        call_pnl=call_pnl,
        put_pnl=put_pnl,
        combined_pnl=combined,
        buyer_call_pnl=buyer_call,
        buyer_put_pnl=buyer_put,
        buyer_combined_pnl=buyer_combined,
        premium_value=premium_value,
        lot_size=float(lot_size),
        call_oi_coverage=call_oi_cov,
        put_oi_coverage=put_oi_cov,
        min_pnl_price=min_price,
        min_pnl_value=min_val,
        breakeven_prices=bes,
        pnl_at_spot=_at(spot),
        pnl_at_max_pain=_at(max_pain),
        scenario=scenario,
        warnings=warnings,
    )


def premium_pnl_scenarios(
    strikes: Sequence[float],
    call_oi: Sequence[float],
    put_oi: Sequence[float],
    call_prem: Sequence[float],
    put_prem: Sequence[float],
    lot_size: float = 1,
    spot: Optional[float] = None,
    max_pain: Optional[float] = None,
    candidates: Optional[Sequence[float]] = None,
    oi_in_units: bool = False,
) -> Dict[str, PremiumPnlResult]:
    """Baseline + ±10% premium sensitivity scenarios."""
    out: Dict[str, PremiumPnlResult] = {}
    for name, scale in (("low_10pct", 0.9), ("snapshot", 1.0), ("high_10pct", 1.1)):
        out[name] = compute_premium_pnl(
            strikes,
            call_oi,
            put_oi,
            call_prem,
            put_prem,
            lot_size=lot_size,
            premium_scale=scale,
            spot=spot,
            max_pain=max_pain,
            scenario=name,
            candidates=candidates,
            oi_in_units=oi_in_units,
        )
    return out


# ---------------------------------------------------------------------------
# Shared helpers (used by CLI and web adapter)
# ---------------------------------------------------------------------------


def oi_payload_to_rows(oi_payload: Dict[str, Any]) -> Tuple[List[StrikeRow], Optional[float]]:
    """
    Convert Upstox get_oi_data payload into StrikeRows + spot.

    Used when the live option chain is gone but an OI snapshot is retained.
    """
    rows: List[StrikeRow] = []
    spot: Optional[float] = None
    try:
        if oi_payload.get("spot_closing_price") is not None:
            spot = float(oi_payload["spot_closing_price"])
    except (TypeError, ValueError):
        spot = None
    for item in oi_payload.get("call_put_oi_data_list") or []:
        if not isinstance(item, dict):
            continue
        strike = float(item.get("strike_price") or 0)
        rows.append(
            StrikeRow(
                strike=strike,
                call_oi=float(item.get("call_oi") or 0),
                put_oi=float(item.get("put_oi") or 0),
            )
        )
    rows.sort(key=lambda r: r.strike)
    return rows, spot


def compute_pcr(call_oi: Sequence[float], put_oi: Sequence[float]) -> Optional[float]:
    """Put OI / Call OI. None when call side is empty."""
    c = float(np.sum(np.clip(np.asarray(call_oi, dtype=float), 0, None)))
    p = float(np.sum(np.clip(np.asarray(put_oi, dtype=float), 0, None)))
    return (p / c) if c else None


def insights_to_series(provider: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize Upstox max-pain insights rows for charts/API."""
    out: List[Dict[str, Any]] = []
    for r in (provider or {}).get("insights") or []:
        if not isinstance(r, dict):
            continue
        out.append(
            {
                "time": r.get("time"),
                "max_pain": r.get("max_pain"),
                "spot_price": r.get("spot_price"),
            }
        )
    return out


def dated_payload_matches(
    payload: Optional[Dict[str, Any]], expiry: str, as_of: str,
    key: str, session_close: Optional[float] = None,
) -> bool:
    """Reject another contract/session, including undated historical carry-forwards.

    Analytics responses often omit their observation date. For completed sessions,
    corroborate their closing spot against the underlying's dated daily candle.
    A requested date alone is insufficient: non-trading dates return stale data.
    """
    if not isinstance(payload, dict) or not payload:
        return False
    if payload.get("instrument_key") not in (None, key):
        return False

    def iso(value: Any) -> Optional[str]:
        for pattern in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(str(value)[:10], pattern).date().isoformat()
            except ValueError:
                pass
        return None

    for field in ("expiry", "expiry_date"):
        if payload.get(field) is not None and iso(payload[field]) != expiry:
            return False
    dated = False
    for field in ("as_of", "date", "trade_date", "session_date"):
        if payload.get(field) is not None:
            if iso(payload[field]) != as_of:
                return False
            dated = True
    if session_close is not None:
        try:
            close = float(payload["spot_closing_price"])
            if not np.isfinite(close) or abs(close - session_close) > 0.02:
                return False
        except (KeyError, TypeError, ValueError):
            return dated
    return True


def apply_provider_override(
    pain: MaxPainResult,
    chain: ChainSnapshot,
    provider: Optional[Dict[str, Any]],
) -> None:
    """
    When local chain is missing or as_of is historical, trust provider max-pain/spot.
    Mutates pain.strike and chain.spot in place.
    """
    if not provider:
        return
    p_mp = provider.get("max_pain")
    p_spot = provider.get("spot_closing_price") or provider.get("spot_price")
    if p_mp is not None:
        try:
            pain.strike = float(p_mp)
        except (TypeError, ValueError):
            pass
    if chain.spot != chain.spot and p_spot is not None:  # NaN
        try:
            chain.spot = float(p_spot)
        except (TypeError, ValueError):
            pass


# ---------------------------------------------------------------------------
# Upstox fetch helpers
# ---------------------------------------------------------------------------


def make_client(token: Optional[str] = None) -> UpstoxAnalyticsClient:
    tok = token or os.getenv("UPSTOX_ANALYTICS_TOKEN")
    if not tok:
        raise SystemExit(
            "UPSTOX_ANALYTICS_TOKEN is not set. Put it in .env next to this script "
            "or pass --token."
        )
    return UpstoxAnalyticsClient(analytics_token=tok)


def list_expiries(client: UpstoxAnalyticsClient, key: str = NIFTY_KEY, expiry: Optional[str] = None) -> List[Dict[str, Any]]:
    contracts = (client.get_option_contracts(key, expiry_date=expiry) if expiry else client.get_option_contracts(key)) or []
    seen: Dict[str, Dict[str, Any]] = {}
    for c in contracts:
        exp = c.get("expiry") or c.get("expiry_date")
        if not exp:
            continue
        rec = seen.setdefault(
            exp,
            {
                "expiry": exp,
                "weekly": bool(c.get("weekly")),
                "lot_size": int(c["lot_size"]) if c.get("lot_size") else None,
                "n_contracts": 0,
            },
        )
        rec["n_contracts"] += 1
        if c.get("lot_size"):
            rec["lot_size"] = int(c["lot_size"])
    return [seen[k] for k in sorted(seen)]


def resolve_expiry(
    client: UpstoxAnalyticsClient,
    expiry: Optional[str],
    key: str = NIFTY_KEY,
) -> Tuple[str, int]:
    """Return (expiry_iso, lot_size). Nearest future expiry when --expiry omitted."""
    exps = list_expiries(client, key)
    if not exps:
        raise SystemExit("No option contracts returned for NIFTY.")

    if expiry:
        for e in exps:
            if e["expiry"] == expiry:
                return e["expiry"], e["lot_size"] or DEFAULT_LOT_SIZE
        # Allow an explicit past/unknown expiry (API may still serve max-pain).
        return expiry, DEFAULT_LOT_SIZE

    today = date.today()
    future = [e for e in exps if date.fromisoformat(e["expiry"]) >= today]
    pick = future[0] if future else exps[0]
    return pick["expiry"], pick["lot_size"] or DEFAULT_LOT_SIZE


def fetch_chain(
    client: UpstoxAnalyticsClient,
    expiry: str,
    lot_size: int,
    key: str = NIFTY_KEY,
) -> ChainSnapshot:
    raw = client.get_option_chain(key, expiry) or []
    rows: List[StrikeRow] = []
    spot = float("nan")
    for item in raw:
        strike = float(item.get("strike_price") or item.get("strike") or 0)
        spot_val = item.get("underlying_spot_price")
        if spot_val is not None and spot_val == spot_val:
            spot = float(spot_val)
        call_md = ((item.get("call_options") or {}).get("market_data")) or {}
        put_md = ((item.get("put_options") or {}).get("market_data")) or {}
        def number(value):
            try:
                result = float(value)
                return result if np.isfinite(result) and result >= 0 else None
            except (TypeError, ValueError):
                return None
        call_oi, put_oi = number(call_md.get("oi")), number(put_md.get("oi"))
        if call_oi is None or put_oi is None or not np.isfinite(strike) or strike <= 0:
            raise ValueError("Incomplete or invalid strike-side OI in option chain")
        rows.append(
            StrikeRow(
                strike=strike,
                call_oi=call_oi,
                put_oi=put_oi,
                call_prev_oi=number(call_md.get("prev_oi")),
                put_prev_oi=number(put_md.get("prev_oi")),
                call_ltp=number(call_md.get("ltp")) or 0.0,
                put_ltp=number(put_md.get("ltp")) or 0.0,
            )
        )
    rows.sort(key=lambda r: r.strike)
    return ChainSnapshot(
        expiry=expiry,
        spot=spot,
        lot_size=lot_size,
        rows=rows,
        fetched_at=datetime.now(),
    )


def fetch_max_pain_insights(
    client: UpstoxAnalyticsClient,
    expiry: str,
    as_of: str,
    bucket_interval: int = 15,
    key: str = NIFTY_KEY,
) -> Optional[Dict[str, Any]]:
    try:
        return client.get_max_pain(
            key,
            expiry=expiry,
            date=as_of,
            bucket_interval=bucket_interval,
        )
    except UpstoxAPIError as exc:
        print(f"  [warn] max-pain API ({as_of}): {exc}", file=sys.stderr)
        return None


def fetch_oi_summary(
    client: UpstoxAnalyticsClient,
    expiry: str,
    as_of: str,
    key: str = NIFTY_KEY,
) -> Optional[Dict[str, Any]]:
    try:
        return client.get_oi_data(key, expiry=expiry, date=as_of)
    except UpstoxAPIError as exc:
        print(f"  [warn] OI API ({as_of}): {exc}", file=sys.stderr)
        return None


def fetch_spot(client: UpstoxAnalyticsClient, key: str = NIFTY_KEY) -> float:
    try:
        q = client.get_ltp_quotes_v3([key]) or {}
        for v in q.values():
            if isinstance(v, dict) and v.get("last_price"):
                return float(v["last_price"])
    except UpstoxAPIError:
        pass
    return float("nan")


def fetch_daily_closes(
    client: UpstoxAnalyticsClient,
    to_date: str,
    from_date: str,
    key: str = NIFTY_KEY,
) -> Dict[str, float]:
    """Map ISO date -> daily close for NIFTY."""
    try:
        raw = client.get_historical_candles_v3(key, "days", 1, to_date, from_date)
    except UpstoxAPIError as exc:
        print(f"  [warn] daily candles: {exc}", file=sys.stderr)
        return {}
    candles = raw.get("candles") if isinstance(raw, dict) else raw
    out: Dict[str, float] = {}
    for c in candles or []:
        # [ts, o, h, l, c, v, oi]
        if not isinstance(c, (list, tuple)) or len(c) < 5:
            continue
        ts = str(c[0])[:10]
        try:
            out[ts] = float(c[4])
        except (TypeError, ValueError):
            continue
    return out


# ---------------------------------------------------------------------------
# Historical research series
# ---------------------------------------------------------------------------


@dataclass
class HistoryPoint:
    expiry: str
    obs_date: str
    obs_time: str
    max_pain: float
    spot: float
    expiry_close: Optional[float]
    kind: str = "session"  # "session" = same-day close; "settlement" = expiry-day close

    @property
    def error_pts(self) -> Optional[float]:
        if self.expiry_close is None or self.max_pain != self.max_pain:
            return None
        return self.expiry_close - self.max_pain

    @property
    def abs_error_pts(self) -> Optional[float]:
        e = self.error_pts
        return abs(e) if e is not None else None


def _candidate_past_expiries(
    as_of_d: date,
    history_days: int,
    listed: Sequence[Dict[str, Any]],
) -> List[str]:
    """
    Historical expiries to try for Chart D.

    Live contract list only holds *current* expiries. Past weeklies/monthlies
    must be synthesized (Upstox still serves max-pain for some of them).
    We try Tuesdays (current NIFTY weekly) plus month-end-ish dates, then any
    listed expiry that has already closed.
    """
    lo = as_of_d - timedelta(days=history_days)
    found: List[str] = []
    for e in listed:
        d = date.fromisoformat(e["expiry"])
        if lo <= d < as_of_d:
            found.append(e["expiry"])

    # Walk back weekly Tuesday expiries (NSE NIFTY weekly day — verify against
    # contract specs; we also try nearby weekdays if Tuesday returns null).
    d = as_of_d
    # Most recent Tuesday on or before as_of
    d = d - timedelta(days=(d.weekday() - 1) % 7)  # Monday=0 … Tuesday=1
    while d >= lo:
        found.append(d.isoformat())
        d -= timedelta(days=7)

    # Monthly: last Tuesday of each month in range
    for m in range(0, history_days // 28 + 2):
        anchor = as_of_d - timedelta(days=28 * m)
        # last day of that month
        if anchor.month == 12:
            nxt = date(anchor.year + 1, 1, 1)
        else:
            nxt = date(anchor.year, anchor.month + 1, 1)
        last = nxt - timedelta(days=1)
        # step back to Tuesday
        tue = last - timedelta(days=(last.weekday() - 1) % 7)
        if lo <= tue < as_of_d:
            found.append(tue.isoformat())

    # Unique, sorted, drop future
    uniq = sorted({x for x in found if date.fromisoformat(x) < as_of_d})
    return uniq


def _pick_insight_row(insights: List[Dict[str, Any]], signal_time: str) -> Optional[Dict[str, Any]]:
    if not insights:
        return None
    want = signal_time[:5]
    for r in insights:
        if str(r.get("time", "")).startswith(want):
            return r

    return None


def build_history(
    client: UpstoxAnalyticsClient,
    expiry_list: Sequence[Dict[str, Any]],
    selected_expiry: str,
    as_of: str,
    history_days: int,
    signal_time: str = SIGNAL_TIME,
    key: str = NIFTY_KEY,
    include_other_expiries: bool = True,
) -> List[HistoryPoint]:
    """
    Research series for Chart D.

    1. Rolling sessions for the *selected* expiry: Max Pain at `signal_time`
       vs that session's NIFTY close (point-in-time, no look-ahead).
    2. Settlement points from completed past expiries when Upstox still
       retains their max-pain history (often only 1–2 recent ones).

    Missing rows are skipped — never backfilled from later data.
    """
    as_of_d = date.fromisoformat(as_of)
    lo_d = as_of_d - timedelta(days=history_days)
    closes = fetch_daily_closes(client, to_date=as_of, from_date=lo_d.isoformat(), key=key)
    points: List[HistoryPoint] = []

    # --- 1. Rolling sessions for selected expiry -------------------------
    # Trading days with a close, from oldest to as_of.
    session_dates = sorted(
        d for d in closes if lo_d <= date.fromisoformat(d) <= as_of_d
    )
    print(f"  rolling sessions to probe: {len(session_dates)}")
    for day in session_dates:
        if date.fromisoformat(day) > as_of_d or day > selected_expiry:
            continue
        mp = fetch_max_pain_insights(
            client, expiry=selected_expiry, as_of=day, bucket_interval=1, key=key
        )
        if not dated_payload_matches(mp, selected_expiry, day, key, closes.get(day)):
            continue
        row = _pick_insight_row(mp.get("insights") or [], signal_time)
        if not row:
            continue
        if row.get("max_pain") is None or row.get("spot_price") is None:
            continue
        max_pain_val = float(row["max_pain"])
        spot_val = float(row["spot_price"])
        if not np.isfinite(max_pain_val) or not np.isfinite(spot_val):
            continue
        close_val = closes.get(day)
        # On the expiry day itself this close is the settlement proxy.
        kind = "settlement" if day == selected_expiry else "session"
        points.append(
            HistoryPoint(
                expiry=selected_expiry,
                obs_date=day,
                obs_time=str(row.get("time") or signal_time),
                max_pain=max_pain_val,
                spot=spot_val,
                expiry_close=float(close_val) if close_val is not None else None,
                kind=kind,
            )
        )

    # --- 2. Settlement points from completed past expiries --------------
    candidates = _candidate_past_expiries(as_of_d, history_days, expiry_list) if include_other_expiries else []
    print(f"  completed-expiry candidates: {len(candidates)}")
    for exp in candidates:
        if exp == selected_expiry:
            continue
        exp_d = date.fromisoformat(exp)
        if exp_d >= as_of_d:
            continue
        if exp not in closes:
            continue
        mp = fetch_max_pain_insights(client, expiry=exp, as_of=exp, bucket_interval=1, key=key)
        if not dated_payload_matches(mp, exp, exp, key, closes.get(exp)):
            continue
        row = _pick_insight_row(mp.get("insights") or [], signal_time)
        if not row:
            continue
        if row.get("max_pain") is None or row.get("spot_price") is None:
            continue
        max_pain_val = float(row["max_pain"])
        spot_val = float(row["spot_price"])
        if not np.isfinite(max_pain_val) or not np.isfinite(spot_val):
            continue
        expiry_close = closes.get(exp)
        if expiry_close is None:
            continue
        points.append(
            HistoryPoint(
                expiry=exp,
                obs_date=exp,
                obs_time=str(row.get("time") or signal_time),
                max_pain=max_pain_val,
                spot=spot_val,
                expiry_close=float(expiry_close),
                kind="settlement",
            )
        )

    points.sort(key=lambda h: h.obs_date)
    return points


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def _style_axes(ax) -> None:
    ax.set_facecolor(C_SURFACE)
    ax.tick_params(colors=C_MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(C_BORDER)
    ax.yaxis.label.set_color(C_MUTED)
    ax.xaxis.label.set_color(C_MUTED)
    ax.title.set_color(C_INK)


def _int_fmt(x, _pos=None) -> str:
    try:
        return f"{int(round(float(x))):,}"
    except Exception:
        return str(x)


def plot_dashboard(
    chain: ChainSnapshot,
    pain: MaxPainResult,
    provider: Optional[Dict[str, Any]],
    insights: Optional[Dict[str, Any]],
    history: List[HistoryPoint],
    as_of: str,
    out_path: Path,
    show: bool = False,
) -> None:
    fig = plt.figure(figsize=(14, 10), facecolor=C_BG)
    gs = fig.add_gridspec(
        2, 2, hspace=0.34, wspace=0.22, left=0.07, right=0.97, top=0.86, bottom=0.08
    )

    # ---- A. Intraday Max Pain vs Spot ---------------------------------
    ax_a = fig.add_subplot(gs[0, 0])
    _style_axes(ax_a)
    ax_a.set_title("A · Intraday Max Pain vs NIFTY spot", loc="left", fontsize=12, fontweight="bold")

    ins = (insights or {}).get("insights") or []
    if ins:
        times = [str(r.get("time", "")) for r in ins]
        mp_line = [float(r.get("max_pain") or np.nan) for r in ins]
        sp_line = [float(r.get("spot_price") or np.nan) for r in ins]
        ax_a.step(range(len(times)), mp_line, where="mid", color=C_ACCENT, lw=2, label="Max Pain")
        ax_a.plot(range(len(times)), sp_line, color=C_INFO, lw=1.8, label="NIFTY spot")
        ax_a.set_xticks(range(len(times)))
        ax_a.set_xticklabels(times, rotation=45, ha="right", fontsize=8)
        ax_a.set_ylabel("Price")
        ax_a.legend(facecolor=C_SURFACE, edgecolor=C_BORDER, labelcolor=C_INK, fontsize=9)
        ax_a.grid(True, color=C_BORDER, alpha=0.5, lw=0.6)
    else:
        ax_a.text(
            0.5, 0.5, "No intraday insights for this date",
            ha="center", va="center", color=C_MUTED, transform=ax_a.transAxes,
        )

    # ---- B. Payout curve ----------------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])
    _style_axes(ax_b)
    ax_b.set_title("B · Theoretical total payout by settlement price", loc="left", fontsize=12, fontweight="bold")

    if pain.candidates.size:
        ax_b.plot(pain.candidates, pain.total_payout / 1e12, color=C_WARN, lw=2, label="Total payout")
        ax_b.plot(pain.candidates, pain.call_payout / 1e12, color=C_CALL, lw=1, alpha=0.7, label="Call payout")
        ax_b.plot(pain.candidates, pain.put_payout / 1e12, color=C_PUT, lw=1, alpha=0.7, label="Put payout")
        ax_b.axvline(pain.strike, color=C_ACCENT, lw=1.5, ls="--", label=f"Max Pain {pain.strike:,.0f}")
        if chain.spot == chain.spot:
            ax_b.axvline(chain.spot, color=C_INFO, lw=1.2, ls=":", label=f"Spot {chain.spot:,.0f}")
        ax_b.scatter([pain.strike], [pain.min_payout / 1e12], color=C_ACCENT, zorder=5, s=40)
        ax_b.set_xlabel("Candidate settlement price")
        ax_b.set_ylabel("Payout (₹ lakh crore)")
        ax_b.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:.1f}"))
        ax_b.legend(facecolor=C_SURFACE, edgecolor=C_BORDER, labelcolor=C_INK, fontsize=8)
        ax_b.grid(True, color=C_BORDER, alpha=0.5, lw=0.6)
    else:
        ax_b.text(0.5, 0.5, "Payout curve unavailable", ha="center", va="center",
                  color=C_MUTED, transform=ax_b.transAxes)

    # ---- C. Strike OI --------------------------------------------------
    ax_c = fig.add_subplot(gs[1, 0])
    _style_axes(ax_c)
    ax_c.set_title("C · Strike-wise open interest", loc="left", fontsize=12, fontweight="bold")

    if chain.rows:
        strikes = chain.strikes
        call_oi = chain.call_oi / 1e6  # millions of contracts
        put_oi = chain.put_oi / 1e6
        w = max(1.0, (strikes[1] - strikes[0]) * 0.4) if len(strikes) > 1 else 1.0
        ax_c.bar(strikes, call_oi, width=w, color=C_CALL, alpha=0.85, label="Call OI")
        ax_c.bar(strikes, -put_oi, width=w, color=C_PUT, alpha=0.85, label="Put OI")
        ax_c.axhline(0, color=C_BORDER, lw=0.8)
        ax_c.axvline(pain.strike if pain.strike == pain.strike else chain.spot,
                     color=C_ACCENT, ls="--", lw=1.2)
        ax_c.set_xlabel("Strike")
        ax_c.set_ylabel("OI (millions of contracts)")
        ax_c.legend(facecolor=C_SURFACE, edgecolor=C_BORDER, labelcolor=C_INK, fontsize=9)
        ax_c.grid(True, color=C_BORDER, alpha=0.5, lw=0.6, axis="y")
    else:
        ax_c.text(0.5, 0.5, "No OI rows", ha="center", va="center",
                  color=C_MUTED, transform=ax_c.transAxes)

    # ---- D. Historical Max Pain vs close -------------------------------
    ax_d = fig.add_subplot(gs[1, 1])
    _style_axes(ax_d)
    ax_d.set_title(
        f"D · Max Pain @ {SIGNAL_TIME} vs close (rolling + settlement)",
        loc="left", fontsize=12, fontweight="bold",
    )

    if history:
        xs = np.arange(len(history))
        mp = [h.max_pain for h in history]
        close = [h.expiry_close if h.expiry_close is not None else np.nan for h in history]
        # Split settlement vs session for clearer legend
        sess = [(i, h) for i, h in enumerate(history) if h.kind != "settlement"]
        sett = [(i, h) for i, h in enumerate(history) if h.kind == "settlement"]
        if sess:
            ax_d.plot(
                [i for i, _ in sess], [h.max_pain for _, h in sess],
                marker="o", ms=4, color=C_ACCENT, lw=1.6, label="Max Pain (signal)",
            )
            ax_d.plot(
                [i for i, _ in sess],
                [h.expiry_close if h.expiry_close is not None else np.nan for _, h in sess],
                marker=".", ms=6, color=C_WARN, lw=1.4, label="Session close",
            )
        if sett:
            ax_d.plot(
                [i for i, _ in sett], [h.max_pain for _, h in sett],
                marker="D", ms=7, color=C_ACCENT, lw=0, label="Max Pain (expiry day)",
            )
            ax_d.plot(
                [i for i, _ in sett],
                [h.expiry_close if h.expiry_close is not None else np.nan for _, h in sett],
                marker="s", ms=7, color=C_WARN, lw=0, label="Expiry close",
            )
        # distance ribbons for settlement
        for i, h in sett:
            if h.expiry_close is not None:
                ax_d.vlines(i, min(h.max_pain, h.expiry_close), max(h.max_pain, h.expiry_close),
                            color=C_DANGER, alpha=0.5, lw=1)

        labels = [f"{h.obs_date[5:]}" + ("*" if h.kind == "settlement" else "") for h in history]
        ax_d.set_xticks(xs)
        ax_d.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax_d.set_ylabel("NIFTY level")
        ax_d.yaxis.set_major_formatter(FuncFormatter(_int_fmt))
        ax_d.legend(facecolor=C_SURFACE, edgecolor=C_BORDER, labelcolor=C_INK, fontsize=8)
        ax_d.grid(True, color=C_BORDER, alpha=0.5, lw=0.6)

        errs = [h.abs_error_pts for h in history if h.abs_error_pts is not None]
        if errs:
            ax_d.text(
                0.02, 0.98,
                f"n={len(errs)}  MAE={np.mean(errs):.0f} pts  "
                f"med={np.median(errs):.0f} pts  (*=expiry day)",
                transform=ax_d.transAxes, va="top", ha="left",
                color=C_MUTED, fontsize=9,
            )
    else:
        ax_d.text(
            0.5, 0.5,
            "No historical points\n(Upstox max-pain history unavailable)",
            ha="center", va="center", color=C_MUTED, transform=ax_d.transAxes,
        )

    # Title / subtitle
    provider_mp = provider.get("max_pain") if provider else None
    provider_txt = f"{provider_mp:,.0f}" if provider_mp is not None else "n/a"
    fig.suptitle(
        f"NIFTY Max Pain · expiry {chain.expiry} · as of {as_of}",
        color=C_INK, fontsize=15, fontweight="bold", x=0.07, ha="left", y=0.98,
    )
    fig.text(
        0.07, 0.935,
        f"Local Max Pain {pain.strike:,.0f} · provider {provider_txt} · "
        f"spot {chain.spot:,.0f} · lot {chain.lot_size} · "
        f"fetched {chain.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}",
        color=C_MUTED, fontsize=10, ha="left",
    )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, facecolor=C_BG)
    print(f"\nSaved chart → {out_path.resolve()}")
    if show:
        try:
            matplotlib.use("TkAgg", force=True)
            plt.show()
        except Exception as exc:
            print(f"(interactive show failed: {exc})")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Metrics / validation
# ---------------------------------------------------------------------------


def print_report(
    chain: ChainSnapshot,
    pain: MaxPainResult,
    provider: Optional[Dict[str, Any]],
    history: List[HistoryPoint],
    lot_size: int,
) -> None:
    line = "=" * 64
    print(line)
    print("NIFTY MAX PAIN — DASHBOARD REPORT")
    print(line)
    print(f"Expiry              : {chain.expiry}")
    print(f"Fetched at          : {chain.fetched_at.isoformat(timespec='seconds')}")
    print(f"NIFTY spot          : {chain.spot:,.2f}")
    print(f"Lot size            : {lot_size}")
    print(f"Strikes in chain    : {len(chain.rows)}")
    if chain.rows:
        print(f"Strike range        : {chain.rows[0].strike:,.0f} – {chain.rows[-1].strike:,.0f}")

    print()
    print("— Max Pain —")
    print(f"Local calc          : {pain.strike:,.0f}")
    if provider:
        p_mp = provider.get("max_pain")
        p_spot = provider.get("spot_closing_price")
        print(f"Upstox provider     : {p_mp}" if p_mp is not None else "Upstox provider     : n/a")
        if p_mp is not None and pain.strike == pain.strike:
            delta = abs(float(p_mp) - pain.strike)
            status = "MATCH" if delta < 1e-6 else f"DIFF {delta:.0f} pts"
            print(f"Agreement           : {status}")
        if p_spot is not None:
            print(f"Provider spot       : {p_spot:,.2f}")
    print(f"Min payout          : ₹{pain.min_payout:,.0f}" if pain.min_payout == pain.min_payout else "Min payout: n/a")
    if pain.tied_strikes:
        print(f"Tied strikes        : {pain.tied_strikes}")
    if pain.candidates.size:
        print(f"Near-min band ±     : {pain.broadness_pts:.0f} pts (within 1% of min)")

    if chain.spot == chain.spot and pain.strike == pain.strike:
        dist = chain.spot - pain.strike
        pct = dist / chain.spot * 100.0 if chain.spot else float("nan")
        side = "above" if dist > 0 else ("below" if dist < 0 else "at")
        print(f"Spot − Max Pain     : {dist:+,.0f} pts ({pct:+.2f}%)  [spot is {side} Max Pain]")

    call_sum = float(chain.call_oi.sum())
    put_sum = float(chain.put_oi.sum())
    print()
    print("— Positioning —")
    print(f"Total Call OI       : {call_sum:,.0f} contracts")
    print(f"Total Put OI        : {put_sum:,.0f} contracts")
    pcr = put_sum / call_sum if call_sum else float("nan")
    print(f"PCR (OI)            : {pcr:.3f}")

    # Nearby payout table
    if pain.candidates.size:
        print()
        print("— Nearby payout curve (₹ crore, contracts × lot × points) —")
        idx = int(np.argmin(np.abs(pain.candidates - pain.strike)))
        lo = max(0, idx - 4)
        hi = min(len(pain.candidates), idx + 5)
        print(f"{'Strike':>10} {'Call pay':>14} {'Put pay':>14} {'Total':>14}")
        for i in range(lo, hi):
            mark = " ←" if i == idx else ""
            print(
                f"{pain.candidates[i]:10,.0f} "
                f"{pain.call_payout[i]/1e7:14,.2f} "
                f"{pain.put_payout[i]/1e7:14,.2f} "
                f"{pain.total_payout[i]/1e7:14,.2f}{mark}"
            )
        print("(units: 1e7 rupees of theoretical intrinsic payout)")

    if history:
        print()
        print("— Historical research (Max Pain @ signal time vs close) —")
        print(f"{'Kind':>10} {'Expiry':>12} {'Obs':>12} {'Time':>6} {'MaxPain':>10} {'Spot':>10} {'Close':>10} {'Err':>8}")
        for h in history:
            err = f"{h.error_pts:+,.0f}" if h.error_pts is not None else "—"
            close_s = f"{h.expiry_close:,.0f}" if h.expiry_close is not None else "—"
            print(
                f"{h.kind:>10} {h.expiry:>12} {h.obs_date:>12} {h.obs_time:>6} "
                f"{h.max_pain:10,.0f} {h.spot:10,.0f} {close_s:>10} {err:>8}"
            )
        errs = [h.abs_error_pts for h in history if h.abs_error_pts is not None]
        if errs:
            hit = sum(1 for e in errs if e <= 50)
            print(
                f"MAE {np.mean(errs):.1f} pts · median {np.median(errs):.1f} · "
                f"within 50 pts: {hit}/{len(errs)} ({100*hit/len(errs):.0f}%)"
            )
            print("Note: 'session' rows compare signal vs same-day close; 'settlement' rows")
            print("      are true expiry-day closes. Descriptive only — not strategy P&L.")

    print()
    print("— Validation —")
    checks = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))

    check("chain_nonempty", len(chain.rows) > 0, f"{len(chain.rows)} strikes")
    check(
        "both_sides_oi",
        call_sum > 0 and put_sum > 0,
        f"C={call_sum:.0f} P={put_sum:.0f}",
    )
    check(
        "min_not_edge",
        pain.candidates.size == 0
        or (
            int(np.argmin(pain.total_payout)) not in (0, len(pain.candidates) - 1)
            if pain.candidates.size
            else True
        ),
    )
    check("max_pain_defined", pain.strike == pain.strike, f"{pain.strike}")
    check(
        "spot_synced",
        chain.spot == chain.spot,
        f"spot={chain.spot}",
    )
    # Edge coverage: spot should not sit in outer 10% of strike range
    if chain.rows and chain.spot == chain.spot:
        kmin, kmax = chain.rows[0].strike, chain.rows[-1].strike
        width = kmax - kmin
        edge_ok = width > 0 and (chain.spot - kmin) > 0.1 * width and (kmax - chain.spot) > 0.1 * width
        check("spot_inside_chain", edge_ok, f"range {kmin:.0f}-{kmax:.0f}")

    for name, ok, detail in checks:
        flag = "PASS" if ok else "WARN"
        print(f"  [{flag}] {name:18} {detail}")

    if pain.warnings:
        for w in pain.warnings:
            print(f"  [warn] {w}")

    print()
    print("Reminder: Max Pain is a theoretical OI payout minimum, not a price forecast.")
    print(line)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="NIFTY Max Pain dashboard (Upstox fetch + matplotlib charts)",
    )
    p.add_argument("--expiry", help="Expiry YYYY-MM-DD (default: nearest listed)")
    p.add_argument("--date", default=date.today().isoformat(), help="As-of date YYYY-MM-DD")
    p.add_argument("--key", default=NIFTY_KEY, help="Underlying instrument key")
    p.add_argument("--token", help="Upstox analytics token (else .env / env)")
    p.add_argument("--bucket", type=int, default=15, help="Intraday bucket minutes (5/15/30/60)")
    p.add_argument("--history-days", type=int, default=40, help="Lookback for research chart")
    p.add_argument("--signal-time", default=SIGNAL_TIME, help="Observation time for history chart")
    p.add_argument("--save", default="max_pain_dashboard.png", help="Output PNG path")
    p.add_argument("--no-show", action="store_true", help="Save only, do not open a window")
    p.add_argument("--list-expiries", action="store_true", help="Print expiries and exit")
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    client = make_client(args.token)

    if args.list_expiries:
        print(f"{'Expiry':>12} {'Weekly':>7} {'Lot':>6} {'Contracts':>10}")
        for e in list_expiries(client, args.key):
            print(
                f"{e['expiry']:>12} {str(e['weekly']):>7} {e['lot_size']:>6} {e['n_contracts']:>10}"
            )
        return 0

    as_of = args.date
    print(f"Fetching NIFTY option data for {as_of} …")
    expiry, lot_size = resolve_expiry(client, args.expiry, args.key)
    print(f"  expiry     : {expiry}")
    print(f"  lot size   : {lot_size}")

    chain = fetch_chain(client, expiry=expiry, lot_size=lot_size, key=args.key)
    if chain.spot != chain.spot:
        chain.spot = fetch_spot(client, args.key)

    print(f"  strikes    : {len(chain.rows)}")
    print(f"  spot       : {chain.spot:,.2f}" if chain.spot == chain.spot else "  spot       : n/a")

    pain = compute_max_pain(chain.strikes, chain.call_oi, chain.put_oi, lot_size, oi_in_units=True)

    print("  fetching provider max-pain …")
    provider = fetch_max_pain_insights(client, expiry, as_of, args.bucket, args.key)

    print("  fetching historical research points …")
    exps = list_expiries(client, args.key)
    history = build_history(
        client,
        exps,
        selected_expiry=expiry,
        as_of=as_of,
        history_days=args.history_days,
        signal_time=args.signal_time,
        key=args.key,
    )
    print(f"  history pts: {len(history)}")

    out = Path(args.save)
    plot_dashboard(
        chain=chain,
        pain=pain,
        provider=provider,
        insights=provider,
        history=history,
        as_of=as_of,
        out_path=out,
        show=not args.no_show,
    )
    print_report(chain, pain, provider, history, lot_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
