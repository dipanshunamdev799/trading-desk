"""Explainable, research-only suitability scoring across independent domains.

Weights express declared strategy requirements and observed data quality. They
are not fitted probabilities of profit. In particular the retrospective family
leaderboard cannot supply predictive weights. All candle-derived indicators
share one budget; all same-chain positioning indicators share another.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30))
VERSION = "multi-factor-v1"


def _profile(id, name, configuration, window, filter_name, requirements, corroboration):
    return {"id": id, "name": name, "configuration": configuration, "window": window,
            "filter": filter_name, "hold_minutes": 60, "requirements": requirements,
            "corroboration": corroboration}


PROFILES = [
    _profile("ema_trend", "EMA12/26 trend", "12/26 gap > 0.5 ATR · afternoon · trend filter",
             "afternoon", "trend", ["ema_trend", "regime_trend"], ["momentum", "structure"]),
    _profile("failed_breakout", "Failed breakout", "20-bar lookback · range filter",
             "all", "range", ["structure", "regime_trend"], ["rsi", "extension"]),
    _profile("pullback", "EMA9/21 pullback", "EMA21 · 0.75 ATR tolerance · afternoon · EMA alignment",
             "afternoon", "ema_aligned", ["ema_alignment"], ["structure", "momentum"]),
    _profile("donchian", "Donchian breakout", "6-bar lookback · afternoon · trend filter",
             "afternoon", "trend", ["structure", "regime_trend"], ["ema_trend", "momentum"]),
    _profile("momentum", "Momentum", "3-bar move > 0.5 ATR · morning · normal volatility",
             "morning", "normal_vol", ["momentum", "volatility"], ["ema_trend", "structure"]),
    _profile("compression", "Compression breakout", "3 ATR prior range · 1 ATR body · afternoon · trend filter",
             "afternoon", "trend", ["structure", "regime_trend"], ["ema_trend", "momentum"]),
    _profile("orb", "Opening-range breakout", "15-minute range · 0.25 ATR buffer · afternoon · EMA alignment",
             "afternoon", "ema_aligned", ["structure", "ema_alignment"], ["momentum"]),
    _profile("ema_reversion", "EMA mean reversion", "2 ATR distance · morning · range filter",
             "morning", "range", ["extension", "regime_trend"], ["rsi"]),
    _profile("gap_continuation", "Gap continuation", "3 ATR gap · before 11:00 · high-volatility filter",
             "morning", "high_vol", ["volatility"], ["ema_trend", "momentum", "structure"]),
    _profile("gap_fade", "Gap fade", "3 ATR gap · before 11:00 · range filter",
             "morning", "range", ["regime_trend"], ["extension", "rsi"]),
    _profile("rsi_reversion", "RSI mean reversion", "RSI40 · morning · range filter",
             "morning", "range", ["rsi", "regime_trend"], ["extension"]),
]
PROFILE_MAP = {profile["id"]: profile for profile in PROFILES}
POSITIONING = ("max_pain", "pcr", "oi_balance", "oi_walls")
CONTEXT = ("breadth", "global_markets", "flows")
PRICE = ("ema_trend", "ema_alignment", "momentum", "structure", "rsi", "extension", "regime_trend", "volatility")
DOMAIN_REASONS = {
    "price": "All setup, trend, momentum, oscillator and regime readings derive from price and share one domain budget.",
    "positioning": "Max Pain, PCR and OI metrics share one options-positioning budget; they are not independent votes.",
    "context": "Breadth, overseas markets and flows share a conservative context budget because equity risk can overlap.",
    "risk": "Event clearance measures setup suitability; it is not a directional forecast.",
}


def _number(value, default=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    try:
        parsed = float(value)
    except (OverflowError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def _clip(value, low=0., high=1.):
    return min(high, max(low, value))


def _time(value):
    if isinstance(value, datetime):
        result = value
    else:
        try:
            result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    return result.astimezone(timezone.utc) if result.tzinfo is not None and result.utcoffset() is not None else None


def _rows(factors):
    if isinstance(factors, dict):
        return {str(key): {**row, "id": str(key)} for key, row in factors.items() if isinstance(row, dict)}
    return {str(row["id"]): dict(row) for row in factors or [] if isinstance(row, dict) and row.get("id")}


def _relevance(profile, key):
    if key == f"setup_{profile['id']}":
        return 1., "The exact strategy setup is a required condition, not an additional independent confirmation."
    if key in profile["requirements"]:
        return 1., "Direct requirement of this strategy's frozen configuration."
    if key in profile["corroboration"]:
        return .5, "Related price corroboration shares the price budget; half-relevance is a declared structural prior, not a fitted edge."
    if key in POSITIONING:
        return .5, "Expiry-specific positioning is contextual evidence, with no validated incremental predictive edge in existing research."
    if key in CONTEXT:
        return .5, "Broad market context can confirm or contradict this candidate's direction; it shares one context budget."
    if key == "event_risk":
        return 1., "Dated event exposure affects whether this intraday setup can be assessed reliably."
    return 0., "No direct requirement or established incremental role for this strategy; excluded from its score."


def _group(key):
    if key in PRICE or key.startswith("setup_"):
        return "price"
    if key in POSITIONING:
        return "positioning"
    if key in CONTEXT:
        return "context"
    if key == "event_risk":
        return "risk"
    return "unmapped"


def _history(evidence, profile_id):
    if not isinstance(evidence, dict):
        return None
    history = evidence.get("strategy_history", {})
    return history.get(profile_id) if isinstance(history, dict) else None


def _evidence_multiplier(evidence, strategy_id, factor_id, at):
    """Only causal, explicitly validated incremental evidence can change a weight.

    This deliberately accepts discounts only. A historical claim needs source,
    training-end and available-at timestamps and a positive post-selection
    validation assertion. Retrospective P&L is disclosed separately.
    """
    if not isinstance(evidence, dict) or evidence.get("method") != "chronological_incremental" or evidence.get("validated") is not True:
        return 1., None
    known = _time(evidence.get("known_at"))
    training_end = _time(evidence.get("training_end"))
    if known is None or training_end is None or training_end > known or known > at or not evidence.get("source"):
        return 1., "Historical weighting evidence rejected: publication/training cutoff or source was not valid at this decision."
    strategy_factors = evidence.get("strategy_factors", {})
    strategy_rows = strategy_factors.get(strategy_id, {}) if isinstance(strategy_factors, dict) else {}
    item = strategy_rows.get(factor_id, {}) if isinstance(strategy_rows, dict) else {}
    multiplier = _number(item.get("reliability_multiplier")) if isinstance(item, dict) else None
    if multiplier is None or not 0 <= multiplier <= 1:
        return 1., None
    return multiplier, f"Validated chronological incremental evidence applies a {multiplier:.3f} reliability multiplier ({evidence['source']})."


def _predictive_mapping(evidence, strategy_id, factor_id, at):
    """Activate a directional hypothesis only after incremental validation.

    This route separates a well-observed measurement from an unvalidated
    directional interpretation. It cannot rewrite the mechanical entry setup,
    the required regime, or an event's known direction-independent risk.
    """
    if factor_id.startswith("setup_") or factor_id in {"regime_trend", "volatility", "event_risk"}:
        return None, None
    if not isinstance(evidence, dict) or evidence.get("method") != "chronological_incremental" or evidence.get("validated") is not True:
        return None, None
    known, training_end = _time(evidence.get("known_at")), _time(evidence.get("training_end"))
    if known is None or training_end is None or training_end > known or known > at or not evidence.get("source"):
        return None, None
    strategy_factors = evidence.get("strategy_factors", {})
    strategy_rows = strategy_factors.get(strategy_id, {}) if isinstance(strategy_factors, dict) else {}
    item = strategy_rows.get(factor_id, {}) if isinstance(strategy_rows, dict) else {}
    if not isinstance(item, dict) or "predictive_reliability" not in item:
        return None, None
    validation_end = _time(item.get("validation_end"))
    predictive_quality = _number(item.get("predictive_reliability"))
    signal_multiplier = _number(item.get("signal_multiplier"))
    lower = _number(item.get("incremental_ci_low"))
    adjusted_p = _number(item.get("corrected_p_value"))
    samples = _number(item.get("validation_samples"))
    valid = (validation_end is not None and training_end < validation_end <= known and
             predictive_quality is not None and 0 <= predictive_quality <= 1 and
             signal_multiplier is not None and -1 <= signal_multiplier <= 1 and
             lower is not None and lower > 0 and adjusted_p is not None and 0 <= adjusted_p <= .05 and
             samples is not None and samples >= 30 and samples.is_integer())
    if not valid:
        return None, "Directional historical mapping rejected: chronological incremental validation, corrected significance or minimum sample gates were not met."
    return {"reliability": predictive_quality, "signal_multiplier": signal_multiplier}, (
        f"Validated earlier-sample incremental mapping: signal × {signal_multiplier:.3f}, predictive reliability {predictive_quality:.3f}; "
        f"{int(samples)} validation samples, corrected p={adjusted_p:.4f}, incremental lower bound {lower:.4f} ({evidence['source']}).")


def _window(profile, at):
    # Original research tests the *signal candle start*, then observes its
    # completed five-minute close. A 13:00 candle is actionable at 13:05.
    signal_at = at.astimezone(IST) - timedelta(minutes=5)
    minute = signal_at.hour * 60 + signal_at.minute
    if profile["window"] == "afternoon":
        return minute >= 780
    if profile["window"] == "morning":
        return 570 <= minute < 660
    return minute >= 570


def _alignment(profile, key, signal, direction):
    if key == f"setup_{profile['id']}":
        return abs(signal) if direction else 0.
    if key == "regime_trend":
        return -signal if profile["filter"] == "range" else signal
    if key == "volatility":
        return -signal if profile["filter"] == "normal_vol" else signal
    if key == "event_risk":
        return signal
    return signal * direction


def score_strategy(profile, factors, at, evidence=None):
    """Return signed suitability and deliberately separate heuristic confidence.

    Each relevant independent domain has equal prior capacity. Its effective
    capacity is reduced by quality and completeness before normalization.
    Within a domain, relevance times quality determines weights. Supporting and
    opposing readings receive the same weighting rule. Missing domains retain
    their place in the coverage denominator, even though usable weights sum to one.
    """
    profile = PROFILE_MAP[profile] if isinstance(profile, str) else profile
    decision = _time(at)
    if decision is None:
        raise ValueError("A timezone-aware decision timestamp is required")
    inputs = _rows(factors)
    setup_key = f"setup_{profile['id']}"
    setup = inputs.get(setup_key, {})
    setup_value = setup.get("value") if isinstance(setup.get("value"), dict) else {}
    setup_signal = _number(setup.get("signal"), 0.)
    direction = 1 if setup_signal > 0 else -1 if setup_signal < 0 else 0
    triggered = setup_value.get("triggered") is True and direction != 0
    considered_keys = [setup_key, *profile["requirements"], *profile["corroboration"], *POSITIONING, *CONTEXT, "event_risk"]
    all_keys = list(dict.fromkeys([*considered_keys, *inputs]))
    rows = []
    evidence_notes = []
    for key in all_keys:
        original = inputs.get(key, {})
        structural_relevance, explanation = _relevance(profile, key)
        applicability = _clip(_number(original.get("relevance_multiplier"), 1.))
        relevance = structural_relevance * applicability
        quality = _clip(_number(original.get("reliability"), 0.))
        signal = _number(original.get("signal"))
        stamp = _time(original.get("reported_at"))
        observed = _time(original.get("observed_at"))
        valid_observed = "observed_at" not in original or original["observed_at"] is None or (observed is not None and observed <= decision)
        ttl = _number(original.get("ttl_seconds"))
        within_ttl = ttl is None or (ttl >= 0 and stamp is not None and (decision-stamp).total_seconds() <= ttl)
        valid_time = stamp is not None and stamp <= decision and valid_observed and within_ttl
        available = (original.get("available") is True and signal is not None and valid_time and
                     bool(original.get("source")) and original.get("status") not in ("stale", "missing", "invalid"))
        reason = str(original.get("reason") or "Observation not supplied.")
        if relevance and original and not valid_time:
            reason += " Missing, naive, future or expired source timestamp; excluded at this decision."
        if relevance and original and not original.get("source"):
            reason += " Measurement provenance is absent; excluded at this decision."
        mapping, mapping_note = _predictive_mapping(evidence, profile["id"], key, decision)
        if mapping is not None:
            measurement_quality = _clip(_number(original.get("measurement_reliability"), 1.))
            quality = measurement_quality * mapping["reliability"]
            if signal is not None:
                signal *= mapping["signal_multiplier"]
        if mapping_note:
            evidence_notes.append(mapping_note)
            reason += " " + mapping_note
        multiplier, note = _evidence_multiplier(evidence, profile["id"], key, decision)
        if note:
            evidence_notes.append(note)
            reason += " " + note
        quality *= multiplier
        available = available and quality > 0
        alignment = _clip(_alignment(profile, key, _clip(signal or 0., -1., 1.), direction), -1., 1.) if available else 0.
        stance = ("irrelevant" if not relevance else "unavailable" if not available else
                  "supports" if alignment > 0 else "opposes" if alignment < 0 else "neutral")
        rows.append({"id": key, "label": original.get("label", key.replace("_", " ").title()),
                     "group": _group(key), "structural_relevance": structural_relevance,
                     "applicability_multiplier": applicability, "raw_relevance": relevance, "reliability": quality if available else 0.,
                     "available": bool(available), "signal": signal, "alignment": alignment, "stance": stance,
                     "normalized_weight": 0., "weight": 0., "contribution_points": 0.,
                     "reason": reason + " " + explanation, "source": original.get("source"),
                     "reported_at": original.get("reported_at"), "value": original.get("value")})
    expected_groups = list(dict.fromkeys(row["group"] for row in rows if row["raw_relevance"] > 0))
    domain_data = {}
    for group in expected_groups:
        members = [row for row in rows if row["group"] == group and row["raw_relevance"] > 0]
        usable = [row for row in members if row["available"]]
        raw_sum = math.fsum(row["raw_relevance"] * row["reliability"] for row in usable)
        relevance_sum = math.fsum(row["raw_relevance"] for row in members)
        reliability = raw_sum / relevance_sum if relevance_sum else 0.
        domain_data[group] = (members, usable, raw_sum, reliability)
    active_groups = [group for group in expected_groups if domain_data[group][3] > 0]
    domain_quality_sum = math.fsum(domain_data[group][3] for group in active_groups)
    groups = []
    for group in expected_groups:
        members, usable, raw_sum, reliability = domain_data[group]
        weight = reliability / domain_quality_sum if domain_quality_sum else 0.
        if weight and raw_sum:
            for row in usable:
                # Divide before multiplying the domain weight so very small
                # but finite raw weights cannot underflow their denominator.
                share = (row["raw_relevance"] * row["reliability"]) / raw_sum
                row["normalized_weight"] = row["weight"] = weight * share
                row["contribution_points"] = 100 * row["weight"] * row["alignment"]
        # Quality and completeness are measured against all expected members;
        # missing readings must not improve the quality of the remaining ones.
        contribution = sum(row["contribution_points"] for row in members)
        alignment = contribution / (100 * weight) if weight else 0.
        support = sum(row["weight"] * max(row["alignment"], 0.) for row in usable)
        opposition = sum(row["weight"] * max(-row["alignment"], 0.) for row in usable)
        internal_conflict = 2 * min(support, opposition) / (support + opposition) if support + opposition else 0.
        groups.append({"id": group, "weight": weight, "prior_capacity": 1 / len(expected_groups),
                       "alignment": alignment, "reliability": reliability, "available": group in active_groups,
                       "contribution_points": contribution, "internal_conflict": internal_conflict,
                       "reason": DOMAIN_REASONS.get(group, "No independent evidence role established.")})
    score = sum(row["contribution_points"] for row in rows)
    coverage = len(active_groups) / len(expected_groups) if expected_groups else 0.
    quality = sum(group["reliability"] for group in groups if group["available"]) / len(active_groups) if active_groups else 0.
    support = sum(group["weight"] * max(group["alignment"], 0.) for group in groups)
    opposition = sum(group["weight"] * max(-group["alignment"], 0.) for group in groups)
    conflict = 2 * min(support, opposition) / (support + opposition) if support + opposition else 0.
    confidence = _clip(max(score, 0.) * coverage * quality * (1 - conflict), 0., 100.)
    setup_row = next(row for row in rows if row["id"] == setup_key)
    reasons = []
    blocked = []
    if not setup_row["available"]:
        reasons.append("Exact setup cannot be evaluated from reliable completed price data.")
    if not triggered:
        blocked.append("The exact strategy setup has not triggered.")
    if setup_value.get("hard_filter_passed") is False:
        blocked.append("The strategy's required regime/alignment/volatility filter did not pass.")
    failed = setup_value.get("failed_requirements")
    if isinstance(failed, list):
        blocked.extend(str(value) for value in failed)
    if not _window(profile, decision):
        blocked.append("Outside this configuration's signal-candle entry window.")
    cutoff = decision.astimezone(IST).replace(hour=15, minute=10, second=0, microsecond=0)
    if decision + timedelta(minutes=profile["hold_minutes"]) > cutoff:
        blocked.append("The 60-minute research holding period would pass the 15:10 IST exit cutoff.")
    if decision.astimezone(IST).weekday() >= 5:
        blocked.append("Weekend decision timestamp; a normal exchange session is required.")
    if score <= 0:
        blocked.append("Weighted opposition equals or exceeds weighted support.")
    missing_groups = [group["id"] for group in groups if not group["available"]]
    if missing_groups:
        reasons.append("Missing independent domains reduce confidence: " + ", ".join(missing_groups) + ".")
    if conflict > 0:
        reasons.append(f"Independent domains disagree; the {conflict:.1%} conflict adjustment reduces confidence.")
    if any(group["internal_conflict"] > 0 for group in groups):
        reasons.append("Opposing readings within a shared domain cancel before cross-domain confidence is assessed.")
    reasons.extend(dict.fromkeys(blocked))
    reasons.extend(dict.fromkeys(evidence_notes))
    if not triggered or not setup_row["available"]:
        confidence = 0.
    if not setup_row["available"] or not active_groups:
        status = "insufficient_data"
    elif blocked:
        status = "watch"
    elif len(active_groups) < 2:
        status = "insufficient_data"
        reasons.append("A single evidence domain cannot establish a multi-factor candidate.")
    else:
        status = "candidate"
    label = "high" if confidence >= 70 else "moderate" if confidence >= 40 else "low" if confidence > 0 else "unavailable"
    reasons.append(f"Suitability {score:.2f}/100 × domain coverage {coverage:.1%} × observed quality/completeness {quality:.1%} × agreement {1-conflict:.1%} = heuristic confidence {confidence:.2f}/100" + ("; no triggered, reliable setup means confidence is unavailable." if not triggered or not setup_row["available"] else "."))
    reasons.append("Confidence describes present evidence and setup suitability, not the probability of a profitable trade; historical and forward acceptance remain unpassed.")
    return {"id": profile["id"], "name": profile["name"], "configuration": profile["configuration"],
            "configuration_version": VERSION, "direction": "bullish" if direction > 0 else "bearish" if direction < 0 else "neutral",
            "setup_triggered": triggered, "status": status, "score": score,
            "confidence_score": confidence, "confidence_label": label, "coverage": coverage,
            "quality": quality, "conflict": conflict, "calibrated_probability": None,
            "factors": rows, "groups": groups, "reasons": reasons,
            "historical_evidence": _history(evidence, profile["id"]), "deployment": "RESEARCH ONLY",
            "weight_basis": "Equal independent-domain prior capacity, reduced by domain quality/completeness before normalization; requirement relevance 1, corroboration 0.5; normalized by observed reliability within each domain. These are declared structural priors, not statistically fitted predictive weights."}


def score_all(factors, at, evidence=None):
    return [score_strategy(profile, factors, at, evidence) for profile in PROFILES]
