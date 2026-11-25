# NIFTY V18 — EVENT-DRIVEN INTELLIGENCE, FUNDAMENTAL INFORMATION DIFFUSION & MARKET EXPECTATION REPRICING

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, corporate announcements, derivatives, ETFs, global markets, historical candles, databases and Python execution capabilities.

We have completed V1 through V17 of our NIFTY forecasting research.

We have extensively investigated price-based information, technical indicators, market internals, sector rotation, global relationships, options-implied expectations, volatility dynamics, market microstructure and residual return forecasting.

Our strongest historical results concern opening-price prediction and volatility forecasting.

Our original five-session and 21-session directional forecasting objectives remain unresolved.

V17 acquired:

- 176,022 corporate announcement records from 2025.
- 169,204 corporate announcement records from 2026.
- 956,709 official equity cash-market records.
- 748 eligible tagged announcements for the selected stock basket.

We have not yet deeply exploited this corporate information universe.

V18 must investigate whether information originating outside conventional price and volume indicators can improve our forecasts.

**Continue actively experimenting using 2025–2026 observations. Do not simply repeat previous research with additional hyperparameters.**

## PRIMARY OBJECTIVES

Forecast NIFTY over:

- Five trading sessions.
- Twenty-one trading sessions.

Investigate directional probabilities, expected returns, coherent return distributions, volatility, trading ranges and tail risk.

Secondary stock, sector, event and shorter-horizon forecasts are permitted when they help explain or improve the primary objectives.

## RESTRICTIONS

- Use only 2025–2026 observations.
- Preserve the November 17, 2026 frozen historical vintage.
- Acquire additional completed 2026 observations separately.
- No pre-2025 market data or fitted model states.
- Preserve all V1–V17 artifacts.
- No live trading, broker orders or capital deployment.
- All previously examined historical outcomes remain research-exposed.

---

# PHASE 1 — REPRODUCTION AND RESEARCH BASELINES

Read all relevant V17 reports, source code, announcement archives, model configurations, forecast laws and experiment registries.

Reproduce the strongest applicable reference systems.

| Forecasting target | Reference score |
|---|---:|
| Opening-gap Brier | 0.100841 |
| Opening-gap accuracy | 88.71% |
| Original weekly Brier | 0.228529 |
| Original weekly CRPS | 0.010457 |
| Original monthly Brier | 0.245042 |
| Original monthly CRPS | 0.024694 |
| Monthly symmetric Brier | 0.250000 |
| Weekly volatility MAE, V16 | 0.036469 |
| Monthly volatility MAE | 0.033179 |
| Weekly volatility expansion Brier | 0.152707 |
| Monthly volatility expansion Brier | 0.172872 |

Also reproduce V17's same-clock weekly distribution comparison:

- Parent CRPS: 0.010658.
- Session-decomposition CRPS: 0.010309.

Recover exact implementations rather than inferring model specifications from summary descriptions.

Preserve separate decision cutoffs for previous-close, pre-auction and post-open forecasts.

Do not combine separate metric leaders into one fictitious model.

Deliver `V18_REPRODUCTION_AND_BASELINES.md`.

---

# PHASE 2 — BUILD A HISTORICAL CORPORATE INFORMATION DATABASE

This is the highest-priority V18 data task.

Investigate the complete corporate announcement universe acquired in V17.

Expand beyond the previous 30-stock research basket wherever historically valid data permits.

## Announcement inventory

Extract and classify available:

- Financial results.
- Quarterly earnings.
- Revenue and profitability changes.
- Management guidance.
- Investor presentations.
- Order wins.
- Contract cancellations.
- Business expansion.
- Acquisitions.
- Divestments.
- Capital expenditure.
- Fundraising.
- Debt developments.
- Credit-rating changes.
- Regulatory developments.
- Litigation.
- Management changes.
- Dividends.
- Buybacks.
- Corporate actions.
- Material business updates.

These are candidate information categories, not assumptions about archive completeness.

## Historical availability

For every record, preserve:

- Company identifier.
- ISIN where available.
- Announcement category.
- Exchange dissemination timestamp.
- Reporting period.
- Relevant event date.
- Source file.
- Attachment availability.
- Revision status.
- Earliest permissible forecast cutoff.

Distinguish when an event occurred from when the information became public.

Use exchange dissemination time plus a conservative availability allowance.

Do not backdate information to the reporting period.

## Deduplication

Identify repeated announcements, amended disclosures, attachments, duplicate exchange publications and multiple filings concerning the same underlying event.

Do not count duplicated announcements as independent information arrivals.

Investigate whether announcement counts are distorted by changes in reporting practices or archive coverage.

Deliver `V18_CORPORATE_INFORMATION_DATABASE.md`.

---

# PHASE 3 — SEMANTIC MARKET INFORMATION EXTRACTION

Investigate whether announcement content can be transformed into reproducible quantitative features.

## Extract structured information

Where supported by the actual document, extract:

- Announcement category.
- Positive or negative business development.
- Reported financial quantities.
- Management guidance changes.
- Materiality indicators.
- Expected implementation horizon.
- Revenue implications.
- Profitability implications.
- Financing implications.
- Regulatory implications.
- Explicitly stated uncertainty.

Use deterministic extraction, document parsing, statistical NLP or locally available language models where appropriate.

## Important restrictions

If using a language model:

- Supply only information available at the historical cutoff.
- Do not allow external knowledge of subsequent company performance.
- Preserve the model version, prompt and extracted outputs.
- Require source excerpts supporting material classifications.
- Test whether simpler rule-based extraction performs equally well.

Do not allow a language model to infer sentiment from knowledge of what subsequently happened to the stock.

Do not fabricate financial quantities when an announcement is ambiguous.

Keep classification uncertainty and missing values explicit.

## Research question

Does semantic information add value beyond announcement category, frequency, company identity and subsequent observable price behavior?

Compare text-derived features with simple non-text controls.

Deliver `V18_SEMANTIC_INFORMATION_EXTRACTION.md`.

---

# PHASE 4 — FUNDAMENTAL CHANGE AND EARNINGS INTELLIGENCE

Research whether changes in underlying business performance provide information about subsequent market returns.

## Candidate fundamental inputs

Where authentically available, investigate:

- Revenue growth.
- Earnings growth.
- Operating margins.
- Profitability changes.
- Debt levels.
- Cash flow.
- Capital expenditure.
- Management guidance.
- Credit conditions.

Normalize quantities appropriately across companies and sectors.

Use only financial observations permitted under the 2025–2026 restriction.

A report published during 2025 may contain earlier-year financial quantities. Do not silently incorporate those pre-2025 observations.

## Earnings surprises

Distinguish:

1. Actual results versus authentic pre-announcement consensus.
2. Actual results versus earlier disclosed guidance.
3. Actual results versus a causally estimated statistical expectation.
4. Changes from previously reported financial quantities.

These are different measurements.

If authentic historical analyst consensus is unavailable, use clearly labeled statistical expectation proxies.

Do not call ordinary earnings growth an analyst-consensus surprise.

## Core hypotheses

Investigate whether:

- Improving aggregate financial results predict sustained market strength.
- Weakening profitability predicts future downside risk.
- Financial-sector earnings developments affect broader market direction.
- Earnings dispersion predicts subsequent sector rotation.
- Fundamental changes improve medium-horizon forecasting more than intraday forecasting.

Treat these as untested hypotheses.

Deliver `V18_FUNDAMENTAL_CHANGE_AND_EARNINGS.md`.

---

# PHASE 5 — CORPORATE EVENT STUDIES

Conduct systematic event studies to determine how markets respond to new company information.

## Candidate event families

- Earnings announcements.
- Guidance changes.
- Material order announcements.
- Acquisitions.
- Regulatory developments.
- Credit-rating changes.
- Fundraising.
- Management changes.
- Other material corporate events.

## Research horizons

Measure subsequent behavior over:

- First eligible trading interval.
- One session.
- Three sessions.
- Five sessions.
- Ten sessions.
- Twenty-one sessions.

Separate announcements issued before the open, during the session and after the close.

## Return measurements

Compare:

- Raw stock returns.
- Market-adjusted returns.
- Sector-adjusted returns.
- Volatility-adjusted returns.
- Abnormal return relative to a causal baseline.

Estimate benchmark exposures using only eligible historical data.

Investigate whether the response is immediate, delayed, persistent or reversing.

## Critical question

Does the event contain predictive information beyond the market reaction already observed at the decision cutoff?

A large realized announcement-day return is not itself evidence of an exploitable delayed response.

Use matched non-event controls and appropriate date, company and event clustering.

Deliver `V18_CORPORATE_EVENT_STUDIES.md`.

---

# PHASE 6 — POST-ANNOUNCEMENT INFORMATION DIFFUSION

Investigate whether corporate information propagates gradually across related stocks, sectors and the broader index.

## Candidate mechanisms

- Large-bank earnings affecting other banks.
- Major IT-company guidance affecting sector peers.
- Energy-company developments affecting related industries.
- Financial-sector credit developments affecting broader market risk.
- Major heavyweight announcements affecting market concentration.
- Industry-wide corporate developments producing persistent sector rotation.

These are predictive research hypotheses, not assumed causal relationships.

## Required experiment

Compare:

1. The announcing stock's subsequent return.
2. Related stocks' subsequent returns.
3. Sector-index returns.
4. Broader market returns.
5. NIFTY returns.

Control for common market movement and contemporaneous index contribution.

Do not mistake the mechanical contribution of a large constituent to NIFTY for prediction of subsequent index movement.

## Event propagation

Investigate whether information spreads:

- Immediately.
- Over the remaining trading session.
- Over subsequent sessions.
- Across a sector.
- Across economically related sectors.

Test whether any measurable delayed relationship survives price-based controls and source-timing perturbations.

Deliver `V18_INFORMATION_DIFFUSION_NETWORKS.md`.

---

# PHASE 7 — AGGREGATE COMPANY INFORMATION INTO NIFTY INTELLIGENCE

Stock-level event predictability does not automatically imply index-level predictability.

Develop market-wide information representations.

## Candidate aggregate features

- Number of positive corporate developments.
- Number of negative corporate developments.
- Earnings improvement breadth.
- Earnings deterioration breadth.
- Sector-level guidance changes.
- Fundamental growth dispersion.
- Financial-sector announcement intensity.
- Material-event concentration.
- Aggregate corporate optimism or deterioration.
- Changes in information-arrival intensity.
- Positive-versus-negative event asymmetry.

## Aggregation methods

Compare:

- Equal-company weighting.
- Sector-balanced weighting.
- Liquidity-based weighting.
- Historical market-cap weighting.
- Authentic point-in-time index weighting.

Use actual historical weights only where available.

Otherwise, label the aggregation as a proxy rather than true NIFTY constituent contribution.

Distinguish the absence of announcements from missing archive coverage.

Normalize announcement frequencies using historically available reporting patterns.

## Key research question

Can aggregated company-level developments provide additional weekly or monthly information beyond:

- Official equal-weight breadth.
- Financial-sector rotation.
- Price momentum.
- Historical volatility.
- Market concentration.
- Existing structural forecasts?

Deliver `V18_AGGREGATE_FUNDAMENTAL_INTELLIGENCE.md`.

---

# PHASE 8 — EXPECTATION VERSUS REALITY

Investigate how corporate information interacts with observable market expectations.

## Candidate situations

- Positive earnings with a negative stock reaction.
- Negative earnings with a positive stock reaction.
- Strong company announcements with weak sector participation.
- Weak corporate developments during a strong market trend.
- Fundamental improvement accompanied by elevated implied volatility.
- Positive corporate information concentrated in a small number of companies.

## Research questions

1. Does disagreement between business information and price reaction predict subsequent continuation or reversal?

2. Does the market react differently to similar events under different volatility conditions?

3. Are fundamental changes more predictive when sector breadth confirms them?

4. Does the absence of an immediate price response suggest delayed information diffusion?

5. Does event information improve downside or upside asymmetry?

Compare event information against price-reaction-only models.

Use only reaction information already observed at the decision cutoff.

Do not assume disagreement represents mispricing.

Deliver `V18_EXPECTATIONS_AND_MARKET_REPRICING.md`.

---

# PHASE 9 — SCHEDULED EVENTS AND FORWARD UNCERTAINTY

Investigate information about events known to be scheduled before the forecast horizon begins.

## Candidate events

- Scheduled earnings releases.
- RBI decisions.
- Federal Reserve decisions.
- Verified economic announcements.
- Index rebalancing.
- Derivative expirations.
- Other historically documented scheduled events.

## Research objectives

Estimate whether scheduled event exposure improves forecasts of:

- Future realized volatility.
- Volatility expansion.
- Trading range.
- Barrier-touch probability.
- Conditional return magnitude.
- Distribution asymmetry.

Investigate whether ATM implied volatility already incorporates the relevant scheduled-event risk.

Do not use an event's eventual outcome before its actual release.

Do not fabricate a historical event calendar using dates that became known only afterward.

Deliver `V18_EVENT_CALENDAR_AND_FORWARD_RISK.md`.

---

# PHASE 10 — ADDITIONAL NON-PRICE INFORMATION DISCOVERY

Continue exploring authentic market-information sources.

Investigate available:

- Historical FII/DII activity.
- Exchange institutional participant reports.
- Bulk and block deals.
- Stock delivery statistics.
- Promoter transactions.
- Shareholding disclosures.
- Credit-rating publications.
- Macroeconomic release vintages.
- Industry-level activity measures.
- Corporate financing developments.

V17 encountered unavailable or unusable responses for some of these sources.

Do not repeatedly execute identical failed retrieval requests without a justified alternative.

Use alternative authorized public sources where feasible.

Preserve source provenance, availability timing and revision history.

Do not interpret institutional activity as a directional signal without empirical testing.

For macroeconomic data, use the value actually available at the decision date rather than a later revised value.

Deliver `V18_NON_PRICE_INFORMATION_DISCOVERY.md`.

---

# PHASE 11 — BUILD EVENT-INFORMED WEEKLY AND MONTHLY FORECASTS

Our original forecasting objective remains central.

## Candidate A: Fundamental information alone

Estimate returns from compact corporate and fundamental information representations.

## Candidate B: Event-augmented structural model

Add event features to the strongest domestic breadth and rotation models.

## Candidate C: Fundamental residual correction

Estimate whether corporate information explains chronological forecast errors from the strongest existing return-distribution models.

## Candidate D: Multi-timescale information model

Distinguish:

- Immediate announcement effects.
- Short-term market reaction.
- Weekly information diffusion.
- Monthly fundamental changes.

## Candidate E: Event-conditioned distributions

Use corporate information to estimate changes in:

- Return location.
- Conditional volatility.
- Distribution asymmetry.
- Tail probabilities.

## Candidate F: Complementary forecasting ensemble

Investigate mixtures combining:

- Domestic structural forecasts.
- Fundamental information forecasts.
- Event-driven forecasts.
- Historical distributions.
- Risk-informed distributions.

Compare simple fixed mixtures before introducing learned weights.

## Mandatory evaluation

Compare every candidate against strong same-clock V14–V17 controls.

Preserve the original 265 weekly and 217 monthly evaluation origins wherever eligibility permits.

Use identical forecast cutoffs and target definitions.

Do not compare an event-enhanced model with additional morning information against a previous-close model and attribute the difference entirely to the event features.

Deliver `V18_EVENT_INFORMED_NIFTY_FORECASTING.md`.

---

# PHASE 12 — FUNDAMENTAL INFORMATION AND VOLATILITY

Our most consistent historical forecasting opportunities have concerned risk.

Investigate whether corporate information improves these capabilities.

## Research hypotheses

- Concentrated earnings announcements increase subsequent volatility.
- Conflicting corporate developments increase market dispersion.
- Negative financial-sector information increases downside uncertainty.
- Earnings uncertainty contributes to volatility expansion.
- Unexpected corporate developments increase future trading ranges.

Compare against:

- Raw ATM IV.
- India VIX.
- IV/RV variance mixtures.
- GJR-GARCH.
- EGARCH.
- V14 joint path models.
- V16 offshore/domestic risk models.
- V17 stock-participation risk models.

Investigate whether corporate information improves forecasts beyond risk already embedded in options prices.

Keep point-volatility, volatility-transition and full-distribution forecasts separate.

Deliver `V18_FUNDAMENTAL_RISK_INTELLIGENCE.md`.

---

# PHASE 13 — EVENT-DRIVEN TRANSFER LEARNING

Previous broad panel-transfer experiments failed to establish reliable improvement.

Investigate a different mechanism: learning common responses to specific corporate events across related companies.

## Candidate approaches

- Pooled earnings-response models.
- Sector-specific event-response models.
- Hierarchical event effects.
- Company-specific adjustments.
- Shared fundamental representations.
- Event-conditioned sector factors.
- Strongly regularized NIFTY-specific adaptation.

Compare against:

- No-transfer models.
- Ordinary pooled models.
- Randomized event categories.
- Shifted announcement dates.
- Matched non-event stock observations.
- Equivalent-complexity price-only models.

Group training and validation by date and event episode.

Do not count thousands of company announcements as thousands of independent NIFTY outcomes.

Transfer learning may help estimate common responses without increasing the number of independent index outcomes.

Deliver `V18_EVENT_DRIVEN_TRANSFER_LEARNING.md`.

---

# PHASE 14 — FALSIFICATION AND INFORMATION-QUALITY CONTROLS

Every apparent discovery must survive serious challenges.

## Announcement controls

- Shift dissemination timestamps.
- Delay announcement availability.
- Shuffle event categories within appropriate blocks.
- Remove duplicate announcements.
- Remove low-materiality announcements.
- Exclude dominant companies.
- Exclude individual event families.
- Remove unusually large event episodes.
- Test alternative text-classification procedures.
- Compare with announcement counts alone.
- Compare with observed price reactions alone.

## Fundamental controls

- Audit reporting-period boundaries.
- Audit restatements.
- Audit prior-period values.
- Reject pre-2025 observations.
- Verify historical consensus availability.
- Test sector-neutral aggregation.
- Test alternative aggregation weights.

## Forecasting controls

- Fully matured labels.
- Chronological fitting.
- Training-only transformations.
- Appropriate purging and embargoes.
- Exact-copy invariance.
- Future-information sentinel tests.
- Matched-origin comparisons.
- Date- and episode-aware uncertainty.
- Representative refit-and-reselection null experiments.

Do not interpret statistical predictive relationships as proven causal economic mechanisms.

Do not claim V18-only adjustments remove cumulative V1–V18 search bias.

Deliver `V18_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 15 — RESEARCH EFFICIENCY

Do not create another enormous uncontrolled model search.

Begin with a registered batch of materially distinct hypotheses.

For each hypothesis define:

- Information source.
- Economic rationale.
- Forecast target.
- Forecast cutoff.
- Strong parent model.
- Primary metric.
- Eligibility requirements.
- Negative controls.
- Experiment budget.
- Criteria for additional investigation.

First establish data coverage and materiality.

Then perform simple event studies and aggregate-feature experiments.

Introduce more complex models only where the underlying information demonstrates promising historical value.

Continue the broader research even when individual mechanisms fail.

Preserve every important negative finding.

Deliver `V18_RESEARCH_EFFICIENCY_AND_KNOWLEDGE_BASE.md`.

---

# PHASE 16 — COMPLETE RESEARCH COMPARISON

Maintain separate leaderboards for:

- Original weekly directional forecasting.
- Original monthly directional forecasting.
- Weekly return distributions.
- Monthly return distributions.
- Stock-level event predictability.
- Sector-level information diffusion.
- Fundamental information value.
- Volatility forecasting.
- Volatility expansion.
- Future ranges.
- Tail risk.

Report:

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- MAE and RMSE.
- Variance QLIKE.
- Rank correlation.
- Calibration.
- Interval coverage and width.
- Origin counts.
- Distinct event counts.
- Disjoint target windows.
- Search-adjusted uncertainty.

Separate improvements over simple parents from improvements over the strongest archived models.

Preserve the established reference cohorts.

Do not force one universal winner.

Deliver `V18_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 17 — FORWARD RESEARCH AND EVIDENCE PRESERVATION

Refresh completed 2026 observations separately from the frozen historical vintage.

Locate all six existing V4 and V5 forecast records.

The previous V17 refresh occurred at 13:44 IST on November 25, 2026, when all six records remained pending.

Resolve forecasts only after their actual target sessions have completed and authoritative outcomes are available.

Do not modify original forecasts.

Where feasible, issue frozen research-only forecasts from a small, predefined panel of distinct candidates:

- GIFT opening-gap model.
- V14 weekly endpoint model.
- Symmetric monthly model.
- Weekly IV/RV risk model.
- Monthly GJR or EGARCH risk model.
- A justified V18 event-informed candidate.

Keep prospective results separate from retrospective experimentation.

Do not extend forecast targets beyond December 2026 without authorization.

Continue historical research in parallel.

Deliver `V18_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V18_REPRODUCTION_AND_BASELINES.md`
2. `V18_CORPORATE_INFORMATION_DATABASE.md`
3. `V18_SEMANTIC_INFORMATION_EXTRACTION.md`
4. `V18_FUNDAMENTAL_CHANGE_AND_EARNINGS.md`
5. `V18_CORPORATE_EVENT_STUDIES.md`
6. `V18_INFORMATION_DIFFUSION_NETWORKS.md`
7. `V18_AGGREGATE_FUNDAMENTAL_INTELLIGENCE.md`
8. `V18_EXPECTATIONS_AND_MARKET_REPRICING.md`
9. `V18_EVENT_CALENDAR_AND_FORWARD_RISK.md`
10. `V18_NON_PRICE_INFORMATION_DISCOVERY.md`
11. `V18_EVENT_INFORMED_NIFTY_FORECASTING.md`
12. `V18_FUNDAMENTAL_RISK_INTELLIGENCE.md`
13. `V18_EVENT_DRIVEN_TRANSFER_LEARNING.md`
14. `V18_VALIDATION_AND_FALSIFICATION.md`
15. `V18_RESEARCH_EFFICIENCY_AND_KNOWLEDGE_BASE.md`
16. `V18_COMPLETE_MODEL_COMPARISON.md`
17. `V18_FORWARD_RESEARCH_LEDGER.md`
18. `V18_FINAL_RESEARCH_CONCLUSIONS.md`
19. `V18_NEXT_EXPERIMENTS.md`

Preserve all source data, announcement timestamps, extracted information, classification rules, Python code, configurations, forecasts, failed experiments, source hashes and verification results.

Keep all V1–V17 artifacts unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Unlock corporate information

Audit the announcement archives.

Build an authenticated, timestamped corporate information database.

Extract structured information.

## Wave 2 — Discover event responses

Conduct stock and sector event studies.

Investigate information diffusion, persistence and price reactions.

## Wave 3 — Build market-wide intelligence

Aggregate company information into sector and index-level representations.

Investigate fundamental breadth and expectation changes.

## Wave 4 — Improve original forecasts

Test incremental event and fundamental information against strong weekly and monthly forecasting models.

Continue volatility and market-path research.

## Wave 5 — Challenge and synthesize

Perform falsification, temporal sensitivity analysis, source-quality checks and complete matched comparisons.

Preserve successful and unsuccessful discoveries.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect our existing research repository, access authenticated historical market sources, retrieve permitted corporate disclosures, parse documents, write Python code, develop statistical and machine-learning models and execute feasible research.

Do not stop at producing a plan.

Execute the research.

Continue actively exploiting the complete 2025–2026 market-data universe.

Do not silently import earlier observations.

Do not extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V18 QUESTIONS

Can corporate information provide genuinely incremental predictive value beyond price-based indicators?

Can earnings and management guidance improve weekly or monthly NIFTY forecasting?

Does information propagate gradually between companies, sectors and the broader market?

Can fundamental breadth reveal information that technical breadth does not?

Can disagreement between corporate developments and observed price reactions predict subsequent movement?

Can corporate events improve forecasts of volatility, future ranges and tail risk?

We have spent seventeen research versions investigating how market prices behave.

V18 must investigate whether the underlying information that influences those prices can improve our understanding of future market behavior.

Be creative.

Prioritize new information over repeated parameter optimization.

Challenge every apparent discovery.

Preserve scientific integrity.

**BEGIN V18 RESEARCH.**