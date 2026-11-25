# Frozen shadow-signal protocol

This is a read-only research evaluator. It cannot submit an order and is independent of application bot workers. Until prospective quality, frozen models, cost calibration and account eligibility pass, candidates are logged as rejected; no funded shadow entries occur. No daily trade quota is filled by force.

## Common candidate clock

Process genuinely available rich quotes at most once per stock/transport/second between 09:30 and 14:30 IST. Price conditions create the common event universe; volume/depth confirmations are separate booleans. Log all candidates, including rejects and unfilled intents. Rate-limit candidates to one per family/stock/transport/30 seconds. For primary analysis, mark at most one eligible event per stock/30 minutes across families and transports. This avoids within-stock overlapping horizons; it does not establish independence across stocks.

All rules require current valid fresh books and observed one- and five-minute return anchors. Conditions below use mid-prices and bps; daily returns use the observed previous close. Missing conditions fail rather than being imputed.

## H3-A: persistent support during momentum

Price candidate: absolute 60-second return at least 20 bps, absolute 300-second return at least 50 bps, both signs agree, and absolute daily move at least 1%. Candidate direction is the sign of the one-minute return.

Volume confirmation: latest 60-second cumulative-volume increment at least twice the median of the five previous nonoverlapping observed minute increments.

Depth confirmation: at least eight observed seconds in the last ten seconds, at least 80% supporting the direction with five-level imbalance above +0.2 for longs or below -0.2 for shorts, current spread no more than 10 bps. Equal weight per observed second prevents a message burst from masquerading as persistence.

Mechanism: consistent price response plus persistent displayed support might distinguish useful continuation from an isolated price jump. Reject the claim if the depth-enhanced model lacks prespecified prospective net improvement over price plus volume, after quote costs and missingness.

## H3-B: liquidity-confirmed breakout

Price candidate: the last three observed seconds of mid-price are all above the prior high plus 5 bps, or below the prior low minus 5 bps. The old range uses observed mids from 5-300 seconds before decision, excluding the latest five seconds. Require at least three distinct observed seconds in that holding window and absolute one-minute return at least 10 bps. Direction is the breakout side.

Volume confirmation: minute volume acceleration at least 1.5. Depth confirmation: direction times mean ten-second imbalance at least +0.1, current spread at most 10 bps and at most twice its observed 60-second median (median floored at 0.1 bp for the ratio).

Mechanism: a held breakout with supportive quotes may have more executable follow-through than an initial crossing. The competing baselines receive identical breakout timestamps, not separately optimized candle events. Failed holding, missing anchors or economically inadequate future movement reject it.

## H3-C: exhaustion and failed continuation

Price candidate: absolute five-minute return at least 100 bps, absolute daily move at least 2%, and an opposite-signed one-minute return of at least 10 bps. Candidate direction is opposite the original five-minute impulse.

Volume confirmation: minute volume acceleration at least one. Depth confirmation: mean ten-second imbalance opposes the original impulse, and current spread is at least twice its observed minute median, floored at 0.1 bp. Spread widening here warns about execution; it is not assumed beneficial.

Evaluate continuation avoidance and opposite-direction reversal on the same event. Their signed primary returns are opposites. Short reversals cannot enter the shared funded simulation without separate contemporaneous short-execution verification. Quote-bound results alone cannot verify borrow or broker permission. Reject reversal profitability if apparent predictive value disappears after widening spread, depth and delayed-entry costs.

## Baselines, controls and targets

Fit P (returns at 5/60/300 seconds and daily return), PV (P plus volume60 and volume acceleration), and PVD (PV plus one-/five-level imbalance, ten-second mean/std imbalance, spread and bid/ask depth5). Exactly nine fixed ridge fits, training-only normalization and no hyperparameter grid. Use the same complete-case timestamps and 900-second labels. Other predefined horizons are diagnostics. Preserve source/receipt/commit times, exact pre-entry books and fresh NIFTY/VIX context; context is descriptive in this fixed model budget.

Attach up to two fresh matched controls from frozen price/turnover bins at every candidate. Controls share side, timestamp, horizon and transport but are not trades. Store missing match counts. Controls have training weight 0.5 each; targets weight one. Whole-day inference accounts for dependence, including reused controls. Controls do not count toward the 1,000 embargoed target requirement.

Endpoint = first valid fresh quote at/after the fixed horizon, no more than two seconds late for WS or ten seconds for REST. Do not seek a better future quote. Record invalid, late, missing and uncollected endpoints separately. Diagnostic quote markouts use whole shares up to about Rs100,000 notional and 1% of past minute volume, with partial depth unresolved. These event markouts differ from funded selected-trade returns.

## Shared selection and hypothetical ledger

Keep candidate records separate from selections. After at least the next integer-second boundary, process the completed selection batch at the actual observed time. Recheck the price setup and current quote/feature freshness. Rank by frozen PVD expected signed gross movement minus current executable-side round-trip quote costs; ties break by instrument key then family. Candidates must additionally satisfy both volume and depth confirmation. A stale/expired setup is rejected.

Hypothetical equity, daily entry count, used symbols, pending intent and open-position quotes persist atomically across manual recorder restarts. Restarting does not create new capital, reset the three-entry cap or release an unresolved position. A mismatched protocol or corrupt saved state prevents silent reuse. Feature warmup restarts from genuinely new quotes; an expired pending intent remains unfilled. Acquisition downtime is missing, and a later quote cannot certify an unobserved intraday drawdown.

The top feasible candidate can reserve shared capital. Entry is not backdated to the signal: wait at least another second for the first fresh quote, with no more than one extra second of observation delay. Apply the frozen cash, risk, quote-depth, chase and eligibility rules in `EXECUTION_COST_MODEL.md`. Later entries are rejected while capital is pending or open. At most three FILLED hypothetical entries per local session, no same-symbol reentry, no leverage. Proposed stops, targets and fees are illustrative until every gate passes; unavailable proposals stay explicitly null with a reason.

Thesis failure means directionally nonpositive ten-second mean imbalance while price is adverse to entry, observed for at least three elapsed seconds. Request exit at the subsequent quote; gaps are not filled with synthetic seconds. Stop, target, 30-minute holding cutoff and 15:10 cutoff are evaluated against actual available-side quotes. Unknown exit prices reserve capital, stop further entries and block qualification. Per-quote priced marked equity and closed-trade equity are separate.

Every candidate stores instrument/time/family/side, the full pre-entry book and feature vector, transport clocks, account and metadata state, shared capital/risk, illustrative size/entry/stop/target, quote costs, P/PV/PVD predictions when frozen, confirmation flags and acceptance/rejection reason. Selection and ledger events preserve rejected, unfilled, pending and unresolved states. No model means no expected-return number is invented from target distance.

## Prospective decision rule

Use the first 20 passing streaming sessions for training and quote-cost allowance, then the next 40 for evaluation. No evaluation-based refit or threshold revision. `evaluate.py` implements the minimum evidence and four-claim day-cluster checks in `V3_RESEARCH_PLAN.md`. Family increment compares net observed 15-minute quote returns selected by PV versus PVD at common events, with the frozen economic hurdle. Missing or partial quote bounds are reported. Report H3-C avoidance as the negative of original continuation exposure, not an additional discovery.

Reject the profitability claim if the sample, economic increment, confidence bounds, funded performance or execution sensitivity is inadequate. Any revised family/threshold after outcome inspection needs a new protocol and new future evaluation sample. Existing application trading bots remain outside this experiment.
