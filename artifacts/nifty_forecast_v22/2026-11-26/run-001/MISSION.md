# NIFTY V22 — INTERNATIONAL MARKET LEARNING, TRANSFERABLE PREDICTIVE RELATIONSHIPS & HISTORICAL MARKET ANALOGUES

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, international equity markets, derivatives, ETFs, corporate disclosures, participant positioning, historical candles, databases and Python execution capabilities.

We have completed V1 through V21 of our NIFTY forecasting research.

We have extensively investigated technical indicators, market internals, global relationships, corporate information, participant positioning, options-implied expectations, volatility, market paths and bottom-up equity forecasting.

V21 successfully reconstructed realized NIFTY returns from dated constituent holdings.

However, bottom-up forecasting generally failed to outperform our strongest direct NIFTY systems.

The common market-return component remains difficult to predict.

V22 must investigate a fundamentally different research question:

**Can we learn predictive relationships from multiple international equity markets and transfer those relationships to NIFTY?**

Previously, we primarily used international market observations as explanatory features.

Now investigate international markets as separate forecasting tasks, historical research environments and sources of transferable market-behavior relationships.

Continue actively experimenting using 2025–2026 observations.

Do not simply repeat the previous broad auxiliary-market pooling experiments.

---

## PRIMARY OBJECTIVES

Retain the original forecasting objectives:

- NIFTY return over the next five trading sessions.
- NIFTY return over the next 21 trading sessions.
- Directional probability.
- Expected and median return.
- Complete coherent predictive return distributions.

Additionally investigate:

- Internationally transferable predictive relationships.
- Historical market analogues.
- Market-specific versus universal return behavior.
- Global common-factor forecasting.
- Country-specific return innovations.
- Volatility transitions.
- Cross-market distribution calibration.
- Sample-efficient transfer learning.

## RESTRICTIONS

- Use only 2025–2026 observations.
- Preserve the original November 17, 2026 historical vintage.
- Acquire additional completed 2026 observations separately.
- No pre-2025 observations, warm-up histories or fitted model states.
- Preserve all V1–V21 artifacts and issued forecasts.
- No live trading, broker orders or capital deployment.
- Previously examined historical outcomes remain research-exposed.
- Additional international observations must not be counted as independent NIFTY outcomes.

---

# PHASE 1 — REPRODUCE V21 AND AUDIT PRIOR TRANSFER LEARNING

Read the complete V21 research index, all 19 reports, source scripts, model configurations, forecast distributions and verification artifacts.

## Original weekly references

| Model | Brier | CRPS |
|---|---:|---:|
| V14 weekly parent | 0.228529 | 0.010457 |
| V18 corporate residual | 0.223481 | 0.010318 |
| V20 weekly Brier leader | 0.221693 | 0.010274 |
| V20 corporate price-reaction model | 0.223384 | 0.010258 |
| V21 asymmetry correction | 0.222129 | 0.010167 |

## Original monthly references

| Model | Brier | CRPS |
|---|---:|---:|
| Neutral probability | 0.250000 | Recover matching law |
| V14 monthly parent | 0.245042 | 0.024989 |
| V19 positioning correction | 0.228199 | 0.024010 |
| V20 embargo candidate | 0.228088 | 0.024003 |
| V20 smoothed positioning | 0.228602 | 0.023786 |
| V21 aggregate positioning correction | 0.223819 | 0.023184 |

Reproduce the earlier/later deterioration of the V21 monthly candidate.

## Preserve V21 reconstruction references

- Daily reconstruction MAE: 0.424 basis points.
- Weekly reconstruction MAE: 1.383 basis points.
- Monthly reconstruction MAE: 4.323 basis points.

Preserve the dated holdings database and corrected corporate-action handling.

## Prior transfer-learning forensics

Investigate the exact implementations and failures of:

- V5 cross-market forecasting.
- V9 cross-sectional market learning.
- V10 auxiliary-instrument transfer.
- V18 event-response pooling.
- V21 equity and sector pooling.

Determine whether previous failures arose from:

- Inappropriate target alignment.
- Common-factor duplication.
- Excessive model complexity.
- Negative transfer.
- Differences in market structure.
- Insufficient domain adaptation.
- Weak underlying predictive relationships.

Do not repeat failed implementations without a materially different research hypothesis.

Deliver `V22_REPRODUCTION_AND_TRANSFER_FORENSICS.md`.

---

# PHASE 2 — BUILD THE INTERNATIONAL MARKET RESEARCH UNIVERSE

Investigate the complete authenticated international equity-market universe accessible through our existing infrastructure.

## Candidate markets

### United States

- S&P 500.
- Nasdaq 100.
- Dow Jones.
- Russell 2000.
- S&P equal-weight indices.
- Major sector indices and ETFs.

### Europe

- DAX.
- FTSE 100.
- CAC 40.
- Euro Stoxx 50.
- Other eligible broad-market and sector indices.

### Asia

- Nikkei 225.
- TOPIX.
- Hang Seng.
- Shanghai Composite.
- CSI 300.
- KOSPI.
- Taiwan market indices.
- Singapore market indices.

### Other markets

Investigate available Australian, Canadian, Brazilian, Indonesian and other emerging-market indices.

These are candidates, not assumptions about historical availability.

## Additional market context

Where authentically available, acquire:

- Country-specific volatility indices.
- Local interest rates.
- Exchange rates.
- Market breadth.
- Sector-relative returns.
- Equity futures.
- Equal-weight indices.
- ETF activity.

Avoid treating multiple ETFs tracking the same index as independent markets.

## Required data audit

For every market, preserve:

- Exchange timezone.
- Local session schedule.
- Historical holidays.
- Daylight-saving transitions.
- Source timestamps.
- Publication and availability assumptions.
- Price-index versus total-return convention.
- Local-currency versus converted-currency return convention.
- Missing observations.
- Corporate-action adjustment methodology.

Use local-currency price-index returns as a primary comparable target where feasible.

Study currency-converted returns separately.

Do not silently combine incompatible return definitions.

Deliver `V22_INTERNATIONAL_MARKET_DATABASE.md`.

---

# PHASE 3 — STANDARDIZE FORECASTING TASKS ACROSS COUNTRIES

Create comparable forecasting problems for every eligible international market.

## Targets

Forecast:

- One local trading session.
- Three local trading sessions.
- Five local trading sessions.
- Ten local trading sessions.
- Twenty-one local trading sessions.

For each horizon, investigate:

- Absolute return.
- Volatility-normalized return.
- Directional probability.
- Absolute return magnitude.
- Realized volatility.
- Volatility expansion.
- Future range, where reliable OHLC exists.

## Comparable feature families

Construct consistently defined features describing:

- Momentum.
- Trend.
- Mean reversion.
- Realized volatility.
- Drawdown.
- Sector rotation.
- Market concentration.
- Breadth.
- Global-relative strength.
- Currency movements.
- Market-implied risk where available.

Keep missing feature families explicit.

Do not fabricate international equivalents of Indian participant positioning or stock-delivery statistics.

## Timing requirements

Each market forecast must use only observations available at its own decision cutoff.

When fitting an India forecast, international training labels must have fully matured before the Indian decision timestamp.

Do not use foreign returns that overlap unresolved future Indian targets.

Maintain both local trading-session and common timestamp representations.

Deliver `V22_INTERNATIONAL_FORECAST_TASKS.md`.

---

# PHASE 4 — SEPARATE GLOBAL COMMON RISK FROM COUNTRY-SPECIFIC INFORMATION

International markets share substantial global risk.

Pooling many countries may simply duplicate the same global-market movement.

Investigate a parsimonious representation:

Country return = Global factor component + Regional factor component + Country-specific component.

Estimate factor exposures using earlier eligible observations.

## Candidate factors

- Global equity-market direction.
- Global volatility.
- US technology leadership.
- Global financial leadership.
- Regional equity-market movements.
- Currency risk.
- Commodity risk.
- Global market synchronization.

Compare economically defined factors with training-only statistical factors.

## Core questions

1. Which relationships are common across countries?

2. Which relationships are specific to individual markets?

3. Can country-specific return innovations be forecast after global-market exposure is removed?

4. Does pooled learning improve prediction of the global component itself?

5. Does international transfer help estimate India's residual return rather than its already-observed offshore movement?

## Critical controls

For India-specific predictions, exclude contemporaneous or future Indian returns from any constructed input that would not have been available.

Where a global factor includes India mechanically, investigate leave-India-out alternatives.

Do not treat an accurately reconstructed global return as a successful forecast of that return.

Deliver `V22_GLOBAL_AND_COUNTRY_FACTOR_DECOMPOSITION.md`.

---

# PHASE 5 — DISCOVER TRANSFERABLE PREDICTIVE RELATIONSHIPS

Investigate whether particular market-behavior relationships recur across countries.

## Candidate mechanisms

- Momentum persistence.
- Short-term reversal.
- Volatility clustering.
- Volatility expansion.
- Drawdown recovery.
- Return asymmetry.
- Breadth deterioration.
- Sector leadership transitions.
- Market synchronization.
- Risk-premium variation.
- Relative strength.
- Conditional return magnitude.

## Research design

For each mechanism:

1. Estimate it independently within each eligible market.
2. Estimate a shared international relationship.
3. Allow strongly regularized country-specific deviations.
4. Test the relationship in countries excluded from model fitting.
5. Test its incremental contribution to NIFTY.
6. Compare against NIFTY-only estimation.

## Candidate methods

- Pooled Ridge.
- Hierarchical regression.
- Partial pooling.
- Random-coefficient models.
- Low-rank multi-task learning.
- Bayesian shrinkage.
- Shared representations with country-specific output heads.

Begin with low-complexity models.

Do not assume that a large international panel justifies deep neural networks.

## Transferability diagnostics

Measure:

- Coefficient sign agreement.
- Coefficient dispersion.
- Cross-country prediction quality.
- Cross-region prediction quality.
- Earlier/later stability.
- Negative-transfer frequency.
- Sensitivity to excluding dominant markets.

A predictive relationship is not transferable simply because pooled historical performance is better.

It must demonstrate appropriate performance outside the markets or environments used to estimate it.

Deliver `V22_TRANSFERABLE_MARKET_RELATIONSHIPS.md`.

---

# PHASE 6 — HISTORICAL MARKET ANALOGUES ACROSS COUNTRIES

This is a major new research direction.

Instead of searching only Indian market history for comparable conditions, investigate whether other markets experienced similar observable market states during 2025–2026.

## Market-state representation

Construct normalized features describing:

- Recent trend.
- Drawdown.
- Volatility.
- Volatility change.
- Breadth.
- Sector rotation.
- Global-relative strength.
- Return dispersion.
- Market synchronization.
- Risk conditions.

Standardize features using eligible historical observations.

Do not use subsequent market behavior to identify a supposedly similar state.

## Candidate analogue methods

- Nearest-neighbor historical states.
- Mahalanobis-distance matching.
- Regularized metric learning.
- Factor-space similarity.
- Volatility-normalized path matching.
- Sector-balanced market-state matching.

## Required comparison

Compare:

A. Indian historical analogues only.

B. International historical analogues only.

C. Combined Indian and international analogues.

D. Random eligible historical windows.

E. Simple volatility-conditioned historical distributions.

F. The strongest direct NIFTY forecast.

## Analogue outcome construction

For each matched historical state, inspect its subsequent fully matured return path.

Normalize and map historical paths into the current Indian market context using causally estimated volatility and other justified transformations.

Do not assume foreign historical returns can be directly applied to NIFTY.

## Diversity requirements

Prevent a collection of highly correlated countries experiencing the same global episode from dominating the analogue set.

Investigate:

- Date diversification.
- Regional diversification.
- Episode-level weighting.
- Maximum weight per global episode.
- Effective analogue sample size.

Deliver `V22_INTERNATIONAL_MARKET_ANALOGUES.md`.

---

# PHASE 7 — RESEARCH MARKET TRANSITIONS ACROSS ENVIRONMENTS

Investigate whether international observations improve our understanding of how market states evolve.

## Candidate transitions

- Low volatility to high volatility.
- High volatility to low volatility.
- Broad participation to concentrated leadership.
- Persistent momentum to reversal.
- Drawdown to recovery.
- Stable risk to sudden expansion.
- Global synchronization to regional divergence.

## Research questions

- Are volatility transitions more transferable than directional relationships?
- Do similar market states produce similar future ranges across countries?
- Does country-specific structure materially change transition probabilities?
- Can international learning improve the estimation of exceptional market movements?
- Can foreign historical episodes provide useful stress scenarios for NIFTY?

## Candidate models

- Conditional transition frequencies.
- Regularized state-transition models.
- Hierarchical transition estimation.
- Low-dimensional state-space models.
- Conditional empirical path mixtures.

Use filtered or otherwise causally available market states.

Do not use retrospectively smoothed regime classifications as historical forecast inputs.

Compare every transition model against appropriate local-market persistence controls.

Deliver `V22_CROSS_MARKET_STATE_TRANSITIONS.md`.

---

# PHASE 8 — INDIA-SPECIFIC ADAPTATION

Internationally estimated relationships may not transfer directly to India.

Investigate how much adaptation is required.

## Candidate architectures

### A. India-only reference

Use our strongest existing NIFTY models.

### B. International-only transfer

Estimate the predictive relationship outside India and apply it to NIFTY.

### C. International initialization

Estimate shared relationships internationally, then adapt using matured Indian observations.

### D. Hierarchical adaptation

Use shared international coefficients with India-specific deviations.

### E. Residual adaptation

Use international information to estimate chronological errors of existing strong NIFTY models.

### F. Complete-law mixture

Combine India-specific and internationally informed predictive distributions.

## Indian information blocks

Preserve:

- Corporate price reactions.
- Financial-sector rotation.
- Official equal-weight breadth.
- Participant positioning.
- Authentic constituent contributions.
- ATM implied volatility.
- Domestic realized volatility.

Investigate whether these Indian-specific sources complement transferable international relationships.

Do not force foreign markets to have matching Indian information fields.

## Adaptation sensitivity

Evaluate fixed training budgets using the same available Indian dates.

Compare internationally informed initialization against ordinary regularization, historical parameter priors and zero-centered shrinkage.

Determine whether improvements genuinely arise from international information rather than simply stronger parameter shrinkage.

Deliver `V22_INDIA_SPECIFIC_DOMAIN_ADAPTATION.md`.

---

# PHASE 9 — IMPROVE WEEKLY AND MONTHLY RETURN DISTRIBUTIONS

The original NIFTY forecasting objectives remain central.

## Weekly candidates

Investigate international information as:

- A direct return predictor.
- A common-factor predictor.
- A residual correction to V20.
- An asymmetry correction to V21.
- A volatility-normalized historical analogue distribution.

## Monthly candidates

Investigate international information as:

- A common-market-state predictor.
- A residual correction to V19–V21 positioning models.
- A conditional distribution calibration mechanism.
- A historical analogue law.
- A strongly regularized transferable return model.

## Coherent distribution requirements

Every candidate predictive law must generate consistent:

- Probability of a positive return.
- Expected return.
- Median return.
- Return quantiles.
- Prediction intervals.
- Tail probabilities.

Where combining predictive laws, use valid distribution mixtures.

Do not average incompatible statistics and describe them as one coherent forecast.

## Required attribution

Separate improvements caused by:

1. Better expected return.
2. Better probability calibration.
3. Better dispersion estimation.
4. Better asymmetry.
5. Better tail representation.
6. Shrinkage toward historical distributions.

Compare every candidate against the strongest applicable same-clock V20 and V21 references.

Deliver `V22_INTERNATIONALLY_INFORMED_NIFTY_FORECASTS.md`.

---

# PHASE 10 — CROSS-MARKET RISK AND TAIL INTELLIGENCE

Our strongest historical capabilities remain related to risk forecasting.

Investigate whether risk relationships transfer internationally more effectively than directional relationships.

## Research targets

- Weekly and monthly realized volatility.
- Volatility expansion.
- Volatility contraction.
- Future high-low ranges.
- Extreme upside and downside returns.
- Drawdowns.
- Conditional tail distributions.

## Mandatory protected references

- Weekly ATM IV MAE: 0.037814.
- Weekly offshore/domestic MAE: 0.036469.
- Monthly GJR volatility MAE: 0.033179.
- Monthly GJR variance QLIKE: 0.199677.
- Weekly volatility expansion Brier: 0.152707.
- Monthly volatility expansion Brier: 0.172872.
- Monthly Student-t GJR range CRPS: 0.015422.

## Candidate mechanisms

- International volatility-transition learning.
- Country-adapted GARCH parameter shrinkage.
- Volatility-normalized international innovations.
- Cross-market heavy-tail estimation.
- International historical path analogues.
- Global-shock-conditioned risk distributions.

Where estimating tails, account for common global episodes.

Do not treat five markets experiencing the same crisis as five independent crises.

Keep stress scenarios separate from probabilistically calibrated forecasts.

Deliver `V22_INTERNATIONAL_RISK_AND_TAIL_INTELLIGENCE.md`.

---

# PHASE 11 — RIGOROUS OUT-OF-MARKET AND OUT-OF-TIME VALIDATION

This is essential to V22.

## Validation designs

### A. Chronological international validation

Train on earlier matured observations and evaluate subsequent observations.

### B. Leave-one-country-out validation

Exclude an entire country from estimation.

### C. Leave-one-region-out validation

Exclude a complete regional market group.

### D. Leave-global-episode-out diagnostics

Investigate sensitivity to individual global market episodes without introducing future information into historical fits.

### E. India-only evaluation

Evaluate the original NIFTY target populations using fully causal historical transfer.

## Negative controls

Include:

- Randomized country assignments.
- Shifted international inputs.
- Randomized auxiliary targets.
- Date-preserving label permutations.
- Common-global-factor-only controls.
- Equal-complexity India-only models.
- Duplicated-market controls.
- Removal of highly correlated index trackers.
- Delayed international information.
- Random historical analogues.

Preserve exact-copy invariance where applicable.

A transfer architecture must not improve simply because an economically identical index was included several times.

## Critical requirement

Every historical training fold must end before its applicable forecast cutoff, with all training outcomes fully matured.

Holding out a country does not permit training on future global observations.

Deliver `V22_TRANSFER_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 12 — QUANTIFY WHAT INTERNATIONAL LEARNING CAN AND CANNOT SOLVE

V20 established that our available NIFTY outcome sample has limited statistical power.

V21 demonstrated that adding stocks does not remove common market uncertainty.

Investigate whether international learning can improve estimation without making unjustified independence assumptions.

## Required diagnostics

Report:

- Number of international markets.
- Number of distinct trading dates.
- Number of global market episodes.
- Country-level dependence.
- Cross-market return correlations.
- Global common-factor variance share.
- Effective training information.
- Parameter uncertainty.
- Negative-transfer frequency.
- Indian forecast uncertainty.

## Synthetic experiments

Construct controlled simulations representing:

1. Stable predictive relationships across countries.
2. Country-specific relationships.
3. Shared global shocks with no predictable returns.
4. Temporary international relationships.
5. Structural changes between training and evaluation.
6. International relationships that do not apply to India.

Determine when pooled estimation, partial pooling or India-only estimation is preferable.

Clearly label synthetic results.

Do not present simulated improvements as evidence of actual market predictability.

Deliver `V22_SAMPLE_EFFICIENCY_AND_TRANSFER_LIMITS.md`.

---

# PHASE 13 — EXPERIMENT DISCIPLINE

Begin with no more than 16 materially distinct primary hypotheses.

Register each hypothesis before executing its initial experiment.

Include:

- Proposed mechanism.
- Required markets.
- Information cutoff.
- Forecast horizon.
- Strong parent model.
- Primary metric.
- Negative controls.
- Eligibility requirements.
- Computational budget.
- Criteria for expansion.

## Stage-one feasibility questions

1. Are international forecasting tasks sufficiently comparable?
2. Are any predictive relationships stable across markets?
3. Does transfer outperform ordinary regularization?
4. Does the result survive common-factor-preserving controls?
5. Does the transferred relationship improve NIFTY specifically?

Do not allocate most of the research budget to increasingly complex transfer architectures if simple models reveal no transferable information.

If directional transfer fails, redirect resources toward volatility, distribution calibration, tail modeling and historical analogue research.

Continue exploring genuinely distinct mechanisms.

Deliver `V22_HYPOTHESIS_REGISTRY.md`.

---

# PHASE 14 — COMPLETE MULTI-MARKET RESEARCH COMPARISON

Maintain separate leaderboards for:

- International directional prediction.
- International return distributions.
- Cross-country generalization.
- Historical market analogues.
- Transferable predictive relationships.
- India-specific adaptation.
- Original weekly NIFTY direction.
- Original monthly NIFTY direction.
- Weekly and monthly NIFTY distributions.
- Volatility and market risk.
- Tail and path forecasting.

Preserve the original Indian comparison populations:

- Weekly: 173 earlier, 92 later, 265 combined.
- Monthly: 141 earlier, 76 later, 217 combined.

These contain only 53 and 11 disjoint outcome windows.

Recompute strong references on matched origins when eligibility changes.

Report:

- Brier.
- Log loss.
- CRPS.
- Accuracy.
- Balanced accuracy.
- MAE and RMSE.
- Rank correlation.
- Variance QLIKE.
- Calibration.
- Interval coverage and width.
- Forecast coverage.
- Dependence-aware uncertainty.

Use representative refit-and-reselection null experiments.

Do not claim V22-only statistical adjustment eliminates cumulative V1–V22 selection bias.

Deliver `V22_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 15 — FORWARD RESEARCH LEDGER

Preserve all V4–V21 issued forecasts.

Resolve only genuinely matured forecasts using authoritative outcomes.

Do not modify previously issued probabilities or distributions.

V21 reported that opening-gap and native directional candidates had been staged for valid morning cutoffs, but no new forecasts had been issued.

## Operational research requirement

Document the exact reasons why the strongest directional candidates have not yet accumulated prospective observations.

Prepare a small frozen research panel containing:

### Weekly

- Neutral or historical control.
- V14 parent.
- V18 corporate correction.
- V20 Brier leader.
- V21 distribution leader.

### Monthly

- Symmetric control.
- V14 parent.
- V19 positioning correction.
- V20 smoothed positioning.
- V21 aggregate positioning correction.

### Additional references

- GIFT opening-gap model.
- Weekly implied-volatility reference.
- Monthly GJR reference.
- Volatility expansion references.

Add a V22 candidate only if its implementation, information cutoff and matched historical comparisons are fully documented.

If a valid issue cutoff has already passed, preserve the missed issue and use the next eligible opportunity.

Archive genuine issue timestamps, complete predictive laws, configuration hashes, source receipts and target sessions.

Do not retrospectively fabricate forecasts.

Do not issue targets extending beyond December 2026 without authorization.

Continue retrospective experimentation independently of the forward ledger.

Deliver `V22_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V22_REPRODUCTION_AND_TRANSFER_FORENSICS.md`
2. `V22_INTERNATIONAL_MARKET_DATABASE.md`
3. `V22_INTERNATIONAL_FORECAST_TASKS.md`
4. `V22_GLOBAL_AND_COUNTRY_FACTOR_DECOMPOSITION.md`
5. `V22_TRANSFERABLE_MARKET_RELATIONSHIPS.md`
6. `V22_INTERNATIONAL_MARKET_ANALOGUES.md`
7. `V22_CROSS_MARKET_STATE_TRANSITIONS.md`
8. `V22_INDIA_SPECIFIC_DOMAIN_ADAPTATION.md`
9. `V22_INTERNATIONALLY_INFORMED_NIFTY_FORECASTS.md`
10. `V22_INTERNATIONAL_RISK_AND_TAIL_INTELLIGENCE.md`
11. `V22_TRANSFER_VALIDATION_AND_FALSIFICATION.md`
12. `V22_SAMPLE_EFFICIENCY_AND_TRANSFER_LIMITS.md`
13. `V22_HYPOTHESIS_REGISTRY.md`
14. `V22_COMPLETE_MODEL_COMPARISON.md`
15. `V22_FORWARD_RESEARCH_LEDGER.md`
16. `V22_FINAL_RESEARCH_CONCLUSIONS.md`
17. `V22_NEXT_EXPERIMENTS.md`

Preserve all reproducible Python code, source observations, availability timestamps, feature definitions, experiment configurations, predictive laws, negative results and verification artifacts.

Keep all V1–V21 artifacts unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — International data and prior research forensics

Audit previous transfer-learning failures.

Establish comparable international forecasting tasks.

Separate shared global information from country-specific information.

## Wave 2 — Discover transferable relationships

Investigate which relationships survive out-of-market and chronological validation.

Prioritize simple mechanisms.

## Wave 3 — International historical analogues

Investigate comparable market states and subsequent return paths from multiple countries.

Control global-episode redundancy.

## Wave 4 — India-specific adaptation

Integrate promising international relationships with domestic corporate, positioning, breadth and risk information.

Evaluate against strong original weekly and monthly benchmarks.

## Wave 5 — Risk, validation and synthesis

Investigate transferable volatility and tail mechanisms.

Challenge apparent winners.

Quantify estimation uncertainty.

Preserve forward forecasts separately.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect our existing research repository, retrieve authenticated historical international market observations, access available Upstox and NSE data, write Python code, develop quantitative models, construct historical market analogues and execute feasible experiments.

Do not stop after producing a research plan.

Execute the research.

Continue actively exploring the complete 2025–2026 market-data universe.

Do not import pre-2025 observations.

Do not extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V22 QUESTIONS

Can international equity markets teach us predictive relationships that are difficult to estimate from Indian history alone?

Which market relationships are universal, and which are country-specific?

Can international historical analogues improve NIFTY return distributions?

Can transferable market-state relationships improve weekly or monthly directional forecasts?

Can international risk learning improve volatility and tail forecasts?

Can we make better use of two years of global data without creating an illusion of independent Indian market outcomes?

We have spent twenty-one research versions investigating NIFTY from numerous perspectives.

V22 must investigate whether learning from multiple international market environments provides a genuinely different source of forecasting intelligence.

Be creative.

Execute meaningful experiments.

Challenge previous assumptions.

Preserve negative findings.

Do not manufacture certainty.

**BEGIN V22 RESEARCH.**