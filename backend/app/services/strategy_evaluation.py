"""One market picture shared by all strategy assessments; no order side effects."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .strategy_context import candle_factors, dashboard_factors, timestamp, IST
from .strategy_scoring import score_all

ROOT = Path(__file__).resolve().parents[3]
VERSION = "multifactor-v1"


def load_weight_evidence():
    """Optional local, versioned validation artifact; absence never invents edge."""
    from ..config import get_settings
    path = get_settings().data_dir / "strategy-factor-evidence.json"
    if not path.exists():
        return None, None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            raise ValueError("evidence root must be an object")
        return result, None
    except (OSError, ValueError) as exc:
        return None, "Strategy weight evidence was ignored: " + str(exc)


def descriptive_evidence():
    """Historical selection results are disclosures, never probability training."""
    path = ROOT / "artifacts" / "last_year_ranking" / "family-leaders.csv"
    rows = []
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                rows.append({"family": row["family"], "configuration": row["strategy"],
                    "trades": int(row["trades"]), "net_points_per_trade": float(row["net5_mean"]),
                    "profit_factor": float(row["net5_profit_factor"]),
                    "net_points_ci95": json.loads(row["net5_conditional_ci95"])})
    except (OSError, KeyError, ValueError, TypeError):
        pass
    return {"validated": False, "method": "retrospective_selected_family_leaders",
            "source": "artifacts/last_year_ranking/family-leaders.csv", "family_leaders": rows,
            "positioning_source": "artifacts/project_alpha/positioning-report.md",
            "note": "Retrospective winners of 3,600 configurations; all listed net-point intervals include zero. "
                    "Prior positioning tests passed zero of 72 joint corrected-return/incremental gates. "
                    "Neither result supplies a calibrated win probability or learned positive factor weight."}


def evaluate_market(candles, dashboard, at, *, session_phase="unknown", candle_source="Retained NIFTY five-minute candles", evidence=None):
    """Pure assessment entry point, also usable by offline diagnostics.

    Offline callers must pass historically available dashboard snapshots. A
    current-state dashboard is never substituted for a historical missing one.
    """
    at = timestamp(at)
    if at is None:
        raise ValueError("Timezone-aware as-of time required")
    prices, context = candle_factors(candles, at, candle_source)
    other, audit = dashboard_factors(dashboard, at, context["spot"], context["atr"])
    factors = {**prices, **other}
    context["session_phase"] = session_phase
    history = descriptive_evidence()
    scores = score_all(factors, at, evidence=evidence)
    aliases = {"compression": "compression_breakout", "gap_continuation": "gap_follow"}
    for score in scores:
        family = aliases.get(score["id"], score["id"])
        score["historical_evidence"] = {"prior_history_note": history["note"],
            "source": history["source"], "descriptive_result": next((r for r in history["family_leaders"] if r["family"] == family), None)}
        # Session verification is a hard gate and cannot be overcome by score.
        if session_phase != "open":
            score["status"] = "watch" if score.get("coverage", 0) else "insufficient_data"
            score["reasons"].append("Exchange session is closed or unverified; assessment is not an actionable entry")
        score["action"] = "NO TRADE"
        score["deployment"] = "RESEARCH ONLY"
    weighted_ids = {row["id"] for score in scores for row in score["factors"] if row["weight"] > 0}
    for row in factors.values():
        effective = [f["reliability"] for score in scores for f in score["factors"] if f["id"] == row["id"] and f["weight"] > 0]
        row["default_predictive_reliability"] = row["reliability"]
        row["reliability"] = max(effective, default=row["reliability"])
        row["scoring_status"] = "weighted" if row["id"] in weighted_ids else "descriptor" if row["available"] else "unavailable"
    for row in audit:
        row["scoring_status"] = "context" if row["available"] else "unavailable"
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "as_of": at.isoformat(),
        "version": VERSION, "market_context": context,
        "input_audit": [*factors.values(), *audit], "strategies": scores,
        "errors": context.pop("errors", []) + [f"{r.get('source', 'Source')}: {r.get('error', 'unavailable')}" for r in dashboard.get("source_errors", [])],
        "notes": [
            "Confidence is a bounded research assessment score, not a probability of profit. No strategy is validated for deployment.",
            "All strategies share one source snapshot. Only completed five-minute bars establish entry setups; daily technicals are context.",
            "Positioning descriptors have zero default predictive reliability: 0/72 prior tests passed. A dated, corrected incremental-validation artifact can activate a strategy-specific mapping.",
            "Absent or stale observations reduce coverage. No source timestamp is inferred from fetch time; opposing signals retain their negative contributions.",
            "Historical candles lack first-receipt/revision vintages. Offline replay needs point-in-time inputs; this endpoint evaluates current context only.",
        ],
        "methodology": {"version": VERSION,
            "weight_basis": "Declared strategy prerequisites and corroboration relevance; equal dependence-domain priors with effective budgets reduced by domain reliability/completeness; not fitted optimal coefficients",
            "correlation_policy": "Price/setup/EMA/momentum share one price budget; OI/PCR/Max Pain share positioning; equity breadth/global share context",
            "confidence_kind": "uncalibrated_research_assessment", "calibrated_probability": None,
            "historical_evidence": history, "documentation": "STRATEGY_EVALUATION.md"}}


def evaluate_live():
    """Read the shared gateway once, not once per strategy; keep failures visible."""
    from .nifty_service import get_nifty_service
    from .upstox_service import get_upstox
    errors, candles, phase = [], [], "unknown"
    try:
        dashboard = get_nifty_service().dashboard(auto_refresh=False)
    except Exception as exc:
        dashboard = {"sections": [], "events": []}
        errors.append("NIFTY market context unavailable: " + type(exc).__name__)
    at = datetime.now(timezone.utc)
    day = at.astimezone(IST).date()
    source = "Shared NIFTY candle gateway"
    try:
        client = get_upstox()
        response = client.get_historical_candles_v3("NSE_INDEX|Nifty 50", "minutes", 5,
            day.isoformat(), (day-timedelta(days=21)).isoformat())
        candles = [dict(zip(("ts", "open", "high", "low", "close", "volume", "oi"), row))
                   for row in response.get("candles", [])]
        source += " · " + str(response.get("_source", "retained/provider"))
    except Exception as exc:
        errors.append("Five-minute candle history unavailable: " + type(exc).__name__)
    try:
        phase = get_upstox().get_market_session("NSE_INDEX|Nifty 50").get("phase", "unknown")
    except Exception as exc:
        errors.append("Exchange session unverified: " + type(exc).__name__)
    # Source snapshots can be received during collection; decide after reads so
    # legitimate receipt times cannot accidentally appear to be in the future.
    evidence, evidence_error = load_weight_evidence()
    result = evaluate_market(candles, dashboard, datetime.now(timezone.utc), session_phase=phase, candle_source=source, evidence=evidence)
    if evidence_error:
        errors.append(evidence_error)
    result["errors"].extend(errors)
    return result
