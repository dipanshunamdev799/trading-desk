# NIFTY V19 — MARKET POSITIONING, CAPITAL FLOW PROXIES, CROWDING & SUPPLY–DEMAND INTELLIGENCE

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, derivatives, ETFs, corporate disclosures, global markets, historical candles, databases and Python execution capabilities.

We have completed V1 through V18 of our NIFTY forecasting research.

We have extensively investigated:

- Technical indicators and price action.
- Domestic market internals.
- Financial-sector rotation.
- Official equal-weight breadth.
- Global-market relationships.
- Statistical and machine-learning models.
- Training-data composition.
- Options-implied expectations.
- Volatility and market paths.
- Offshore price discovery.
- Stock-level participation.
- Corporate announcements and fundamentals.

Our strongest historical forecasting results concern opening gaps, volatility, trading ranges and selected weekly return distributions.

V18 produced a new weekly Brier point leader of 0.223481 through a corporate residual overlay.

However, a much less explored source of information also produced promising results: delivery participation, derivatives participant positioning and bulk/block transactions.

**V19 must investigate how market positioning, trading participation and changes in exposure relate to future market movements.**

Continue actively experimenting using 2025–2026 observations.

Do not simply repeat previous research with additional hyperparameters.

---

# PRIMARY OBJECTIVES

Retain our original forecasting objectives:

- NIFTY return over the next five trading sessions.
- NIFTY return over the next 21 trading sessions.
- Directional probabilities.
- Expected and median returns.
- Coherent conditional return distributions.

Additionally investigate:

- Positioning changes.
- Position crowding.
- Delivery participation.
- Capital flow proxies.
- Sector-level trading activity.
- Position-price disagreement.
- Volatility expansion.
- Future ranges.
- Tail risk.
- Potential position-unwinding events.

Determine whether these information sources provide incremental value over our strongest existing forecasting systems.

## RESTRICTIONS

- Use only 2025–2026 observations.
- Preserve the November 17, 2026 frozen historical vintage.
- Acquire additional completed 2026 observations separately.
- No pre-2025 observations or fitted model states.
- Preserve all V1–V18 artifacts.
- No broker orders, live trading or capital deployment.
- Previously examined historical observations remain research-exposed.
- Do not manufacture causal explanations or independently validated forecasting claims.

---

# PHASE 1 — REPRODUCE V18 AND ESTABLISH STRONG REFERENCES

Read the complete V18 research index, all 19 reports, source scripts, model configurations, data inventories, forecast laws and verification artifacts.

Recover exact implementations from the repository.

## Original-horizon references

| Forecasting system | Brier | CRPS |
|---|---:|---:|
| V14 weekly parent | 0.228529 | 0.010457 |
| V18 weekly corporate residual overlay | 0.223481 | 0.010318 |
| V14 monthly direction reference | 0.245042 | Recover exact matching law |
| V18 monthly corporate overlay | 0.259808 | Recover from artifacts |
| Monthly symmetric probability | 0.250000 | Recover from artifacts |
| V15 monthly distribution leader | Recover from artifacts | 0.024694 |

## Rebuilt 08:55 weekly references

| Forecasting system | Brier | CRPS |
|---|---:|---:|
| Structural parent | 0.238274 | 0.010658 |
| Delivery, positioning and transaction activity | 0.232338 | 0.010352 |
| Fundamental augmentation | 0.248263 | 0.011103 |
| V17 session decomposition | 0.238003 | 0.010309 |

Reproduce the complete V18 corporate residual-overlay experiment, including its 223 actively fitted origins and inactive fallback cases.

Reproduce the new delivery, positioning and bulk/block results individually and jointly.

Determine whether the combined improvement came predominantly from one information block or an interaction among several blocks.

Preserve all existing opening-gap, volatility, volatility-expansion and joint-path references.

Do not combine separate metric leaders into one fictitious forecasting system.

Deliver `V19_REPRODUCTION_AND_BASELINES.md`.

---

# PHASE 2 — BUILD THE HISTORICAL MARKET POSITIONING DATABASE

Audit the complete V18 non-price information archive.

Existing observations include:

- 109,980 delivery rows across 466 dates.
- 1,532 derivatives participant OI rows across 383 dates.
- 2,970 bulk/block transaction records across 151 dates.
- 117,517 supplementary cash-market records across 58 sessions.

Investigate whether additional authenticated 2025–2026 observations can be obtained.

## Candidate information sources

- NSE participant-wise open interest reports.
- Participant-wise trading-volume reports.
- Index futures positioning.
- Stock futures positioning.
- Index options positioning.
- Stock options positioning.
- Stock delivery quantities.
- Delivery percentages.
- Cash-market turnover.
- Historical bulk deals.
- Historical block deals.
- Institutional cash activity.
- Exchange margin and market-wide position-limit information, where available.
- Historical securities lending information, where available.

These are candidate sources, not assumptions about availability.

## Required source audit

For every dataset, record:

- Source and file identifier.
- Observation date.
- Publication timestamp or conservative availability allowance.
- Participant classification.
- Instrument classification.
- Contract units.
- Historical lot size.
- Coverage.
- Missing observations.
- Revision risk.
- Applicable forecast cutoffs.

Distinguish a missing report from a genuine zero observation.

Do not treat an end-of-day report as available before that session's close.

Where exact historical publication times cannot be established, apply conservative delays and test their sensitivity.

Do not repeatedly execute previously failed retrieval requests without a materially different authorized retrieval method.

Deliver `V19_MARKET_POSITIONING_DATABASE.md`.

---

# PHASE 3 — PARTICIPANT POSITIONING INTELLIGENCE

Investigate the historical derivatives positioning of each participant category actually present in the authenticated reports.

Potential categories include:

- Foreign institutional participants.
- Domestic institutional participants.
- Proprietary participants.
- Clients.

Use the exact definitions supplied by the source.

## Candidate measurements

For each eligible participant and instrument family, investigate:

- Long contracts.
- Short contracts.
- Net contracts.
- Gross contracts.
- Long-to-short ratios.
- Net exposure relative to gross exposure.
- Daily changes in positioning.
- Five-session positioning changes.
- Twenty-one-session positioning changes.
- Positioning persistence.
- Positioning acceleration.
- Participant exposure disagreement.
- Position concentration.

Keep index futures, stock futures and options categories separate.

Account for changes in lot size and contract composition where supported.

## Critical interpretation restrictions

Every derivatives contract has both a long and a short side.

Aggregate participant net positions are mechanically related across participant groups.

Do not count mechanically redundant position columns as independent information sources.

Do not infer:

- Institutional conviction.
- Dealer hedging direction.
- Actual cash inflows.
- Portfolio-level economic exposure.
- Position liquidation.

Unless the underlying data genuinely supports the inference.

Long calls, short calls, long puts and short puts cannot be converted into reliable delta exposure using aggregate contract counts alone.

Strike, maturity and Greek information are required for defensible exposure estimation.

Label unsupported approximations as proxies.

## Research hypotheses

Investigate whether:

1. Persistent changes in index futures positioning precede future NIFTY returns.

2. Participant disagreement predicts volatility expansion.

3. Changes in positioning contain more information than absolute position levels.

4. Positioning information is more useful at weekly than monthly horizons.

5. Position changes predict subsequent sector rotation.

6. Participant information adds value beyond ordinary futures OI, prices and implied volatility.

Compare every mechanism against strong matched price-based controls.

Deliver `V19_PARTICIPANT_POSITIONING_INTELLIGENCE.md`.

---

# PHASE 4 — DELIVERY PARTICIPATION AND STOCK-LEVEL ACTIVITY

Research the complete historical stock-delivery universe.

Delivery statistics may describe a different form of trading participation than ordinary turnover, but they do not identify the direction or ownership of the delivered shares.

## Candidate measurements

Investigate:

- Delivery quantity.
- Delivery percentage.
- Delivery value.
- Relative delivery quantity.
- Delivery activity relative to historical turnover.
- Abnormal delivery participation.
- Delivery acceleration.
- Persistence of high delivery activity.
- Cross-sectional delivery dispersion.
- Sector-level delivery participation.

Use historically valid traded quantities, prices and corporate-action adjustments.

Do not compare raw share quantities across different companies without appropriate normalization.

## Research A: Price and delivery interaction

Investigate joint states such as:

- Rising price with unusually high delivery.
- Rising price with low delivery.
- Falling price with unusually high delivery.
- Falling price with low delivery.
- Increasing delivery during consolidation.
- Delivery concentration during volatility expansion.

These are research categories, not accumulation or distribution labels.

## Research B: Delivery breadth

Construct measures such as:

- Percentage of eligible stocks with unusually high delivery.
- Percentage experiencing increasing delivery participation.
- Sector-balanced delivery breadth.
- Financial-sector delivery concentration.
- Delivery activity among outperforming stocks.
- Delivery activity among underperforming stocks.

Compare against ordinary stock breadth, official equal-weight breadth and turnover-based controls.

## Research C: Future market behavior

Investigate whether delivery measurements improve predictions of:

- Stock-relative returns.
- Sector-relative returns.
- NIFTY direction.
- Volatility expansion.
- Future ranges.
- Return persistence.
- Reversals.

Require evidence that delivery contributes information beyond price, volume and market conditions.

Deliver `V19_DELIVERY_PARTICIPATION_RESEARCH.md`.

---

# PHASE 5 — POSITION CROWDING AND POTENTIAL UNWINDING

Investigate whether unusual positioning concentrations are associated with future market changes.

## Candidate crowding proxies

- Participant net exposure relative to historical exposure.
- Participant gross exposure relative to historical exposure.
- Concentrated derivatives positioning.
- Simultaneous exposure changes across related instruments.
- Positioning divergence from price momentum.
- Positioning divergence from market breadth.
- Unusually persistent positioning.
- Concentrated delivery activity across stocks.

Use training-defined normalization.

Do not use full-sample percentiles to identify historical extremes.

## Research questions

1. Does unusually high positioning concentration predict subsequent volatility?

2. Does price momentum become less persistent when positioning is unusually concentrated?

3. Does positioning concentration interact with deteriorating breadth?

4. Do changes in positioning accompany subsequent trend reversals?

5. Can historical positioning identify elevated risk of rapid exposure reduction?

## Important distinction

A reduction in aggregate open interest does not establish forced liquidation.

It may arise from expiration, rollover, ordinary position closing or other mechanisms.

Use the term "position-unwinding proxy" unless actual liquidation information exists.

Separate observed exposure reduction from hypothesized future unwinding.

## Evaluation

Research:

- Future position changes.
- Future absolute returns.
- Volatility expansion.
- Directional continuation.
- Directional reversal.
- Extreme price movements.
- Conditional return distributions.

Compare with simple volatility, momentum and OI baselines.

Deliver `V19_CROWDING_AND_UNWINDING_RESEARCH.md`.

---

# PHASE 6 — POSITION-PRICE DIVERGENCE

Develop a dedicated research framework for disagreement between positioning and market behavior.

## Candidate relationships

- Futures positioning versus NIFTY returns.
- Positioning versus financial-sector rotation.
- Positioning versus official equal-weight breadth.
- Delivery participation versus stock-relative performance.
- Participant exposure versus ATM implied volatility.
- Positioning changes versus futures basis.
- Participant disagreement versus market concentration.

Investigate levels, changes, persistence and statistically estimated innovations.

## Residual positioning

Estimate expected positioning changes using causally available:

- Price returns.
- Volatility.
- Futures basis.
- Time to expiration.
- Historical positioning.
- Market breadth.

Then calculate the difference between observed positioning and the estimated expectation.

Investigate whether this residual contributes information beyond ordinary positioning levels.

Use historical out-of-sample or appropriately chronological residual construction.

Do not call a statistical residual proof of hidden institutional information.

## Required comparison

Compare:

1. Price-only forecasts.
2. Positioning-only forecasts.
3. Price plus ordinary positioning.
4. Price plus residual positioning.
5. Price plus positioning disagreement.
6. Strong existing structural models plus positioning information.

Determine whether the effect is primarily related to direction, return magnitude, dispersion or tail behavior.

Deliver `V19_POSITION_PRICE_DIVERGENCE.md`.

---

# PHASE 7 — BULK AND BLOCK TRANSACTION INTELLIGENCE

Investigate authenticated historical large-transaction records.

## Candidate measurements

- Transaction quantity.
- Transaction value.
- Transaction size relative to ordinary turnover.
- Disclosed purchase or sale designation.
- Number of distinct transactions.
- Repeated disclosed participants.
- Sector concentration.
- Transaction price relative to an eligible reference price.
- Persistence of transaction activity.
- Subsequent stock and sector behavior.

Separate bulk deals from block deals.

Preserve the source's transaction classification.

Deduplicate related records where supported, without incorrectly removing economically distinct transaction legs.

Where both buyer and seller records describe the same transaction, avoid double-counting total transferred value.

## Research questions

- Does unusual large-transaction activity precede future volatility?
- Do transaction prices relative to market prices contain useful information?
- Are repeated disclosures associated with persistent stock-relative returns?
- Does sector-level transaction concentration predict rotation?
- Does transaction activity contribute anything beyond ordinary turnover and observed price reactions?

## Restrictions

A disclosed large purchase is not necessarily evidence of future buying.

A transaction may involve ownership transfer, portfolio restructuring or other motives.

Do not infer undisclosed intentions.

Use actual publication times and conservative availability allowances.

Deliver `V19_LARGE_TRANSACTION_RESEARCH.md`.

---

# PHASE 8 — EXPLORE AUTHENTIC CAPITAL FLOW INFORMATION

V18 could verify derivatives participant positioning but could not obtain a usable dated cash-market FII/DII flow series.

Continue investigating this limitation through alternative authorized sources.

Potential sources include:

- Official exchange institutional activity publications.
- Depository disclosures.
- Dated fund-flow reports.
- Historical ETF creation/redemption information.
- Mutual-fund industry publications.
- Authenticated foreign portfolio investment statistics.

For every source, distinguish:

- Actual cash flows.
- Gross purchases and sales.
- Net cash transactions.
- Changes in assets under management.
- Changes in derivatives exposure.
- Changes in prices.
- Delivery participation.

These are not interchangeable.

Changes in fund AUM may result from market appreciation rather than new investment.

ETF trading volume does not directly measure fund subscriptions or redemptions.

## Research questions

Where authentic historical flow information exists, investigate:

- Flow persistence.
- Flow reversals.
- Foreign versus domestic flow disagreement.
- Flow-price disagreement.
- Sector-level capital allocation.
- Subsequent weekly and monthly returns.
- Conditional volatility.

If authentic dated data remains unavailable, explicitly record the blocker and continue with verified positioning and delivery sources.

Do not construct fictional historical institutional flows.

Deliver `V19_AUTHENTIC_CAPITAL_FLOW_RESEARCH.md`.

---

# PHASE 9 — MARKET-WIDE POSITIONING AND PARTICIPATION FACTORS

Aggregate stock-level and participant-level measurements into compact market-state representations.

## Proposed factors

1. Participant positioning.
2. Positioning change.
3. Participant disagreement.
4. Delivery participation.
5. Delivery breadth.
6. Large-transaction activity.
7. Exposure concentration.
8. Position-price divergence.

These are candidate factors, not predetermined useful signals.

## Aggregation methods

Compare:

- Equal-company weighting.
- Sector-balanced weighting.
- Historical liquidity weighting.
- Historically valid market-cap weighting.
- Authentic index weighting where available.

Where dated constituent weights are unavailable, label the resulting measurements as proxies.

Preserve exact-copy invariance and avoid mechanically redundant features.

## Cross-sectional learning

Investigate whether positioning and delivery help estimate future sector leadership.

Compare stock-level features with:

- Official sector indices.
- Official equal-weight breadth.
- Native financial rotation.
- Existing stock-participation controls.
- Price and turnover factors.

Do not inflate NIFTY sample size by counting every stock-date observation as an independent future index outcome.

Deliver `V19_AGGREGATE_POSITIONING_FACTORS.md`.

---

# PHASE 10 — COMBINE FUNDAMENTAL INFORMATION WITH POSITIONING

V18 found a promising weekly corporate residual overlay, but ordinary fundamental augmentation and stock-event transfer performed poorly.

Investigate whether positioning helps explain when corporate information matters.

## Candidate interactions

- Positive corporate developments with increasing delivery participation.
- Earnings surprises with participant exposure changes.
- Fundamental deterioration with weak breadth.
- Corporate information accompanied by unusually concentrated trading activity.
- Financial-sector earnings developments with changing derivatives positions.
- Scheduled corporate events with elevated market-priced risk.

Do not infer that positioning changes were caused by a particular corporate announcement without adequate evidence.

## Required attribution experiment

Using identical origins and decision cutoffs, compare:

A. Strong structural parent.

B. Parent plus corporate information.

C. Parent plus delivery information.

D. Parent plus participant positioning.

E. Parent plus large-transaction information.

F. Parent plus a combined non-price information block.

G. Parent plus corporate-positioning interactions.

H. Matched shuffled and delayed controls.

Identify the marginal contribution of each information block.

Investigate alternative addition orders because correlated inputs may produce order-dependent attribution.

Deliver `V19_FUNDAMENTAL_POSITIONING_INTERACTIONS.md`.

---

# PHASE 11 — DEVELOP BETTER WEEKLY AND MONTHLY FORECASTS

The original NIFTY forecasting objectives remain the main priority.

## Candidate A: Direct positioning model

Estimate future NIFTY returns from a compact representation of positioning and delivery.

## Candidate B: Structural augmentation

Add verified positioning information to the strongest existing domestic breadth and rotation models.

## Candidate C: Residual correction

Use new information to predict chronological errors from:

- V14 weekly probability-shrinkage forecasts.
- V18 corporate residual forecasts.
- V17 same-clock session-decomposition forecasts.

## Candidate D: Regularized location-scale forecasting

Investigate whether positioning contributes more effectively to:

- Expected return.
- Conditional volatility.
- Return asymmetry.
- Tail probabilities.

## Candidate E: Structural distribution mixture

Combine complete predictive laws representing different information sources.

Potential experts:

- Domestic market structure.
- Corporate developments.
- Participant positioning.
- Delivery participation.
- Historical returns.
- Market-priced risk.

Compare fixed mixtures before attempting learned weights.

## Mandatory controls

Preserve the exact original forecast clock.

Evaluate previous-close, pre-auction and post-open systems separately.

Require fully matured historical targets and causal preprocessing.

Preserve the original five-session and 21-session endpoints.

Do not use actual future positioning observations when constructing multi-session forecasts.

## Primary targets for comparison

Weekly Brier:

- V14: 0.228529.
- V18 corporate overlay: 0.223481.

Weekly CRPS:

- V14: 0.010457.
- V18 corporate overlay: 0.010318.
- V17 same-clock decomposition: 0.010309 at its distinct forecast cutoff.

Monthly:

- Directional Brier: 0.245042.
- Neutral Brier: 0.250000.
- Distribution CRPS: 0.024694.

These are historical references, not guaranteed achievable future results.

Deliver `V19_ORIGINAL_HORIZON_FORECASTING.md`.

---

# PHASE 12 — POSITIONING-INFORMED VOLATILITY AND PATH FORECASTS

Investigate whether positioning information is more useful for risk than direction.

## Research targets

- Future realized volatility.
- Volatility expansion.
- Volatility contraction.
- Entry into high-volatility conditions.
- Future high-low range.
- Downside excursions.
- Upside excursions.
- Barrier touches.
- Extreme price movements.

## Strong historical benchmarks

- Raw weekly ATM IV MAE: 0.037814.
- V16 weekly offshore/domestic risk MAE: 0.036469.
- Monthly GJR-GARCH MAE: 0.033179.
- Weekly volatility expansion Brier: 0.152707.
- Monthly volatility expansion Brier: 0.172872.
- Monthly Student-t GJR range CRPS: 0.015422.

Compare every positioning-enhanced candidate against strong existing volatility and path systems.

Investigate whether exposure concentration improves the prediction of volatility transitions beyond raw IV.

If constructing joint market paths, derive all claimed joint outcomes from the same path law.

Maintain separate standalone forecasts where joint coherence has not been established.

Deliver `V19_POSITIONING_AND_RISK_INTELLIGENCE.md`.

---

# PHASE 13 — FALSIFICATION AND ROBUSTNESS

All promising discoveries must survive appropriate challenges.

## Positioning controls

- One-session-delayed positioning.
- Five-session-delayed positioning.
- Block-shifted positioning.
- Block-permuted positioning.
- Removal of mechanically redundant participant categories.
- Alternative normalization methods.
- Rollover exclusions.
- Expiry-period exclusions.
- Missing-report sensitivity.
- Lot-size and unit-conversion checks.

## Delivery controls

- Ordinary traded volume.
- Ordinary turnover.
- Random eligible stock subsets.
- Exclusion of dominant stocks.
- Sector-neutral aggregation.
- Corporate-action exclusions.
- Alternative historical normalization windows.

## Transaction controls

- Matched high-turnover days without disclosed large transactions.
- Shifted transaction dates.
- Removal of unusually large deals.
- Alternative transaction aggregation.
- Duplicate-transaction sensitivity.

## Forecasting controls

- Strongest applicable archived parent.
- Chronological fitting.
- Fully matured labels.
- Training-only preprocessing.
- Exact forecast-cutoff matching.
- Purging and embargoes.
- Future-information sentinel tests.
- Exact-copy invariance.
- Date- and episode-aware uncertainty.
- Representative refit-and-reselection null experiments.

Preserve separate earlier and later historical results.

Investigate whether improvements disappear after removing individual favorable market episodes.

Do not claim that V19-only search adjustments eliminate cumulative V1–V19 selection bias.

Deliver `V19_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 14 — RESEARCH EFFICIENCY AND EXPERIMENT DISCIPLINE

We have completed eighteen extensive research versions.

V19 should prioritize meaningful discovery over experiment volume.

Begin with no more than 24 materially distinct primary hypotheses.

For each hypothesis, register:

- Economic rationale.
- Information source.
- Forecast target.
- Decision cutoff.
- Strong parent.
- Primary metric.
- Matched eligibility.
- Negative control.
- Initial computational budget.
- Criteria for follow-up experimentation.

## Experiment expansion rules

Expand a research track when:

- Its underlying data is sufficiently reliable.
- It represents a genuinely different information mechanism.
- Matched historical comparisons show potentially useful improvements.
- Its behavior can be investigated across different periods.
- Additional experiments could distinguish competing explanations.

Redirect research effort when:

- The new information consistently fails against strong controls.
- The apparent result depends on invalid timing.
- Improvements are explained by duplicated features.
- Performance depends excessively on one market episode.
- Shifted or randomized information performs equally well.

Failure of a particular hypothesis is not a reason to terminate the overall research project.

Do not generate thousands of nearly identical configurations merely to increase experiment counts.

Deliver `V19_HYPOTHESIS_REGISTRY_AND_RESEARCH_EFFICIENCY.md`.

---

# PHASE 15 — COMPLETE MODEL COMPARISON

Preserve the established historical cohorts:

- Earlier weekly: 173 origins.
- Later weekly: 92 origins.
- Combined weekly: 265 origins.
- Earlier monthly: 141 origins.
- Later monthly: 76 origins.
- Combined monthly: 217 origins.

These represent only 53 and 11 disjoint weekly and monthly outcome windows.

Where positioning coverage changes eligibility, compare all systems on identical eligible dates.

Also report coverage across the full intended forecast population.

Do not hide missing coverage behind favorable matched-subset results.

## Separate leaderboards

1. Original weekly direction.
2. Original monthly direction.
3. Weekly endpoint distributions.
4. Monthly endpoint distributions.
5. Participant positioning information.
6. Delivery participation information.
7. Bulk/block transaction information.
8. Positioning-fundamental interactions.
9. Volatility forecasting.
10. Volatility expansion.
11. Future ranges.
12. Tail risk.

## Required metrics

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- MAE.
- RMSE.
- Variance QLIKE.
- Rank correlation.
- Calibration.
- Interval coverage.
- Interval width.
- Origin count.
- Disjoint outcome count.
- Search-adjusted uncertainty.

Maintain a clear distinction between:

- Improvement over a weak parent.
- Improvement over a strong parent.
- New retrospective point leader.
- Replicated historical relationship.
- Independently validated performance.

Deliver `V19_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 16 — FORWARD RESEARCH LEDGER

Refresh completed 2026 market observations separately from the frozen historical vintage.

The last V18 refresh occurred at 15:08 IST on November 25, 2026.

Locate all six existing V4 and V5 forecasts targeting:

- November 25.
- November 26.
- December 17.
- December 18.

Resolve forecasts only when the relevant sessions have completed and authoritative outcomes are available.

Preserve their original issue classifications, including any late-diagnostic status.

Do not overwrite an existing forecast with a newly fitted model.

## New research-only forecasts

Where operationally feasible, freeze a small predefined panel including:

- GIFT opening-gap reference.
- V14 weekly reference.
- V18 corporate-overlay weekly reference.
- Monthly neutral reference.
- Monthly directional research candidate.
- Weekly and monthly volatility references.
- A justified V19 positioning candidate.

Record complete distributions, model configurations, source cutoffs and genuine issue timestamps.

Keep prospective results separate from retrospective research.

If forecast targets would extend into 2027, do not issue them without authorization.

Continue historical research in parallel.

Deliver `V19_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V19_REPRODUCTION_AND_BASELINES.md`
2. `V19_MARKET_POSITIONING_DATABASE.md`
3. `V19_PARTICIPANT_POSITIONING_INTELLIGENCE.md`
4. `V19_DELIVERY_PARTICIPATION_RESEARCH.md`
5. `V19_CROWDING_AND_UNWINDING_RESEARCH.md`
6. `V19_POSITION_PRICE_DIVERGENCE.md`
7. `V19_LARGE_TRANSACTION_RESEARCH.md`
8. `V19_AUTHENTIC_CAPITAL_FLOW_RESEARCH.md`
9. `V19_AGGREGATE_POSITIONING_FACTORS.md`
10. `V19_FUNDAMENTAL_POSITIONING_INTERACTIONS.md`
11. `V19_ORIGINAL_HORIZON_FORECASTING.md`
12. `V19_POSITIONING_AND_RISK_INTELLIGENCE.md`
13. `V19_VALIDATION_AND_FALSIFICATION.md`
14. `V19_HYPOTHESIS_REGISTRY_AND_RESEARCH_EFFICIENCY.md`
15. `V19_COMPLETE_MODEL_COMPARISON.md`
16. `V19_FORWARD_RESEARCH_LEDGER.md`
17. `V19_FINAL_RESEARCH_CONCLUSIONS.md`
18. `V19_NEXT_EXPERIMENTS.md`

Preserve complete reproducible Python code, source files, feature definitions, eligibility timestamps, model configurations, forecasts, predictive distributions, failed experiments and verification results.

Keep all V1–V18 artifacts unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Establish the new information universe

Reproduce V18.

Audit participant positioning, delivery, bulk/block transactions and supplementary cash-market data.

Identify the separate contribution of each information family.

## Wave 2 — Discover positioning relationships

Research participant exposure, delivery participation, crowding, exposure changes and position-price disagreement.

Start with simple statistical models and strong controls.

## Wave 3 — Develop combined market intelligence

Investigate fundamental-positioning interactions, cross-sectional activity and aggregate positioning factors.

Explore authentic capital-flow information where available.

## Wave 4 — Improve original forecasts

Integrate promising mechanisms into strong weekly and monthly forecasting systems.

Investigate residual correction, coherent distributions and risk forecasting.

## Wave 5 — Challenge and synthesize

Perform falsification, timing sensitivity, matched comparisons, episode-level evaluation and forward-ledger reconciliation.

Update the cumulative research knowledge base.

Preserve unsuccessful hypotheses.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing research repository, access authenticated historical market sources, retrieve permitted datasets, write Python code, develop quantitative models and execute feasible experiments.

Do not stop after producing a research plan.

Execute the research.

Continue actively exploring the complete 2025–2026 market-data universe.

Do not silently import earlier observations or extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V19 QUESTIONS

Can participant positioning reveal useful information that conventional price indicators do not?

Does delivery participation improve forecasts of future sector leadership or NIFTY returns?

Does unusual exposure concentration predict volatility or future reversals?

Can disagreement between positioning, corporate developments and observed market behavior improve predictive distributions?

Can these mechanisms improve our original weekly and monthly NIFTY forecasts?

We have researched price behavior, global information, volatility, market expectations and corporate fundamentals.

V19 must investigate market participation and positioning as a distinct source of predictive intelligence.

Explore creatively.

Prioritize information quality.

Challenge every apparent discovery.

Preserve negative findings.

Do not manufacture certainty.

**BEGIN V19 RESEARCH.**