# Phase 3: prospective NSE equity microstructure research

Prepared 15 November 2026. This version has three new hypotheses, a bounded read-only observer and quote-based research simulations. It has no demonstrated profitable strategy. Definitions and Python source are hashed together by `readiness freeze` before new observations are used. The machine-readable freeze time, rather than this document's date, is the prospective boundary.

## Constraints inherited from V1 and V2

V2's twelve primary configurations all lost over the complete evaluation window; none qualified through development selection. The least-negative primary expectancy was -18.37 bps per trade. Reduced costs, delayed execution and short-only diagnostics did not establish an executable positive edge. Those reports and their data remain intact. V3 does not rerun their parameter searches, reinterpret a losing configuration as a winner or imply that every possible intraday method must lose.

The retained archive is already exposed to research. Its permitted role here is inventory, timestamp quality and descriptive execution bounds. It is not an independent new alpha evaluation set. All retrospective work stays within 2025-2026. Collection and evaluation stop at 31 December 2026; extending either into 2027 needs explicit user approval and a new scope freeze.

## Exactly three forward hypotheses

| Family | Mechanism under test | Competing baseline | Primary event |
|---|---|---|---|
| H3-A | Directional momentum may persist when displayed depth supports it over several observed seconds | Identical price candidates, price-only and price-plus-volume models | Signed 15-minute price movement and conservative quote markout |
| H3-B | A breakout may be more useful when price remains beyond the old range and spreads/depth support execution | The same breakout timestamps without depth confirmation | Signed 15-minute movement after causal breakout formation |
| H3-C | Reversal in price response, depth and spreads may identify failed continuation | The same exhaustion candidates without depth; continuation is the opposite signed outcome | Avoided continuation loss and opposite-direction 15-minute markout |

Exact thresholds, windows and rejection rules are in `SHADOW_SIGNAL_PROTOCOL.md`. No fourth strategy family, threshold grid, alternative indicator suite or retrospective winner selection is authorized in this version. Horizons 30, 60, 180, 300 and 1,800 seconds are diagnostic; 900 seconds is primary. H3-C avoidance and reversal are two interpretations of the same outcome, not extra independent discoveries.

## Chronological research budget

1. Collect genuine regular-session observations after the protocol freeze. Audit streaming and REST separately. Five quality sessions demonstrate initial quality, not an edge.
2. Use the first 20 passing streaming sessions only for training and quote-cost calibration. Each family needs at least 30 nonoverlapping target episodes spanning ten training days. Fit at most nine ridge models: three families times P, PV and PVD. Ridge alpha is fixed at one; scaling is fitted on training data only. No hyperparameter selection or refitting on evaluation returns.
3. Freeze model hashes and a training-only quote-cost allowance. Predict only on later local session dates. All models use the same complete-case event panel. Predictor signs are aligned with candidate direction; volume/spread magnitudes are unchanged, and bid/ask quantities swap for shorts.
4. Evaluate the next 40 passing streaming sessions, without selecting a favorable ending date. Collect at least 60 passing sessions overall and 1,000 within-stock embargoed target events across at least 50 sessions. Thirty-minute within-stock spacing prevents overlapping primary horizons; correlated stocks remain correlated. Train and evaluation dates are disjoint sessions, so event horizons cannot straddle that boundary.

The source implements collection, training prerequisites, frozen calibration and a future assessment command. No model has been trained on prospective observations yet. Insufficient evidence produces `FORWARD_DATA_REQUIRED`, never a manufactured metric.

## Four primary claims and qualification

The primary family claims compare depth-enhanced versus price-plus-volume decisions on the SAME eligible timestamps, using observed executable-side quote bounds. The fourth claim concerns the shared funded shadow portfolio. Use whole-day bootstrap resampling, 10,000 draws and fixed seed 301. Four one-sided claims use alpha 0.05/4: a 98.75% one-sided lower bound. Diagnostics, alternate horizons, controls and long/short breakdowns are descriptive, without extra significance claims.

Each family needs at least 100 complete evaluation events across 30 evaluation days, a positive adjusted day-cluster lower bound, and mean net economic uplift exceeding max(5 bps, twice the frozen quote-cost uncertainty allowance). The shared portfolio additionally needs at least 75 closed hypothetical trades over 30 active evaluation days, profit factor at least 1.2, positive adjusted day-level funded-return lower bound, maximum EOD and measured intraday drawdown no worse than 15%, worst day no worse than -2%, and the five biggest winners contributing at most 50% of positive P&L. Unresolved or unpriced exposure prevents qualification. These are qualification criteria, not guaranteed loss limits.

The 5 bps per-side impact stress, family/side outcomes, nonfills, missing endpoints, price-only results and market-regime diagnostics must accompany an assessment. Observational depth bounds are never promoted to broker-certified fills. Positive model accuracy alone cannot qualify. Leverage is prohibited. Failed or inconclusive evidence rejects the profitability claim; it does not trigger a new parameter sweep.

## Operational milestones

Milestone A requires actual new regular-session observations with valid clocks. Milestone B requires five fresh sessions with at least 95% fixed-control as-of coverage under the transport-specific rules. Milestone C requires the larger sample and prospective assessment above. None can be inferred from Sunday's closed-market snapshots. No unattended task, service or automatic application startup was installed.
