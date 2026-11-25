# NIFTY V20 — HORIZON-SPECIFIC PREDICTIVE INTELLIGENCE, INFORMATION LIFETIMES & STRUCTURAL FORECAST INTEGRATION

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, derivatives, ETFs, corporate disclosures, participant positioning, global markets, historical candles, databases and Python execution capabilities.

We have completed V1 through V19 of our NIFTY forecasting research.

We have accumulated substantial knowledge across:

- Technical indicators.
- Domestic market internals.
- Financial-sector rotation.
- Official equal-weight breadth.
- Global-market relationships.
- Statistical and machine-learning models.
- Training-data composition.
- Options-implied expectations.
- Volatility dynamics.
- Market-path forecasting.
- Offshore price discovery.
- Stock-level participation.
- Corporate announcements and fundamentals.
- Derivatives participant positioning.
- Delivery participation and large transactions.

V18 produced our strongest combined weekly directional point result.

V19 produced our strongest combined monthly directional and distribution point results.

However, combining the strongest weekly and monthly information sources did not automatically improve both horizons.

This motivates a new central research hypothesis:

**Different market information sources may operate over different predictive timescales.**

V20 must investigate this hypothesis systematically.

We are deliberately continuing active research using 2025–2026 observations.

Do not stop retrospective experimentation simply because independent validation remains unavailable.

Do not simply repeat V1–V19 with additional hyperparameters.

---

# PRIMARY OBJECTIVES

Retain the original forecasting objectives:

- NIFTY return over the next five trading sessions.
- NIFTY return over the next 21 trading sessions.
- Directional probability.
- Expected and median return.
- Complete coherent predictive return distributions.

Additionally investigate:

- Information lifetimes.
- Predictive response across horizons.
- Signal persistence.
- Delayed market responses.
- Temporary versus persistent predictive relationships.
- Horizon-specific model architectures.
- Complementarity between information sources.
- Volatility and market-path forecasting.

## RESTRICTIONS

- Use only 2025–2026 market observations.
- Preserve the November 17, 2026 frozen historical vintage.
- Acquire additional completed 2026 observations separately.
- No pre-2025 observations or fitted model states.
- Preserve all V1–V19 research artifacts and issued forecasts.
- No live trading, broker orders or capital deployment.
- All previously examined historical outcomes remain research-exposed.
- Do not manufacture causal interpretations or independently validated performance claims.

---

# PHASE 1 — REPRODUCE AND AUDIT THE STRONGEST V19 DISCOVERIES

Read the complete V19 research index, all 18 reports, source code, configurations, experiment registry, fit receipts, participant archives and forecast distributions.

Recover exact implementations rather than inferring them from summary descriptions.

## Original weekly references

| System | Brier | CRPS |
|---|---:|---:|
| V14 weekly parent | 0.228529 | 0.010457 |
| V18 corporate residual overlay | 0.223481 | 0.010318 |
| V18 plus V19 positioning | 0.232431 | 0.010467 |

## Original monthly references

| System | Brier | CRPS |
|---|---:|---:|
| V14 monthly parent | 0.245042 | 0.024989 |
| Neutral monthly probability | 0.250000 | Recover matching law |
| V15 monthly distribution leader | Recover matching law | 0.024694 |
| V19 positioning residual overlay | 0.228199 | 0.024010 |

## V19 active monthly comparison

| System | Brier | CRPS |
|---|---:|---:|
| Exact V14 parent | 0.241294 | 0.025046 |
| Bias-only correction | 0.279342 | 0.026404 |
| Positioning correction | 0.218307 | 0.023710 |
| Correction without fitted bias | 0.227153 | 0.024182 |
| Additional one-session delay | 0.225051 | 0.023806 |
| Additional five-session delay | 0.258460 | 0.025077 |

Reproduce the earlier/later monthly gain decomposition, inactive fallback cases, block-removal sensitivity and placebo results.

The 159 active monthly origins represent only eight non-overlapping windows.

Do not present them as 159 independent observations.

## Critical timing audit

V19 admits historical end-of-day reports at 08:15 IST on the following NSE session.

Verify exactly how these observations enter the archived native V14 and V18 forecast clocks.

Confirm that the residual correction does not use participant reports that were unavailable when the original parent forecast was issued.

If the corrected system uses a later information cutoff than its parent:

- Reconstruct an appropriate same-clock parent.
- Report the effect of the changed information set separately.
- Preserve the original archived forecasts.
- Correct any invalid leaderboard comparisons.

This audit must be completed before declaring V19's positioning overlay an improvement over the original native forecast.

Deliver `V20_REPRODUCTION_AND_TIMING_AUDIT.md`.

---

# PHASE 2 — BUILD A CUMULATIVE PREDICTIVE INFORMATION REGISTRY

Create a consolidated inventory of the strongest discoveries across V1–V19.

For every major information family, document:

- Exact feature definitions.
- Source provenance.
- Availability rules.
- Historical coverage.
- Forecast cutoffs.
- Primary forecast targets.
- Strongest matched comparisons.
- Earlier/later performance.
- Falsification results.
- Known failure mechanisms.
- Redundant information.
- Unresolved research questions.

## Mandatory information families

1. Offshore GIFT NIFTY pricing.
2. Global equity-market behavior.
3. Native Indian market internals.
4. Financial-sector rotation.
5. Official equal-weight breadth.
6. Stock-level participation.
7. Corporate announcements.
8. Structured financial results.
9. Participant futures positioning.
10. Participant options positioning.
11. Participant trading volume.
12. Delivery participation.
13. Bulk and block transactions.
14. ATM implied volatility.
15. Options surface characteristics.
16. Realized-volatility dynamics.
17. Intraday market structure.
18. Authentic institutional flow information where available.

Distinguish raw observations, constructed proxies and fitted latent factors.

Classify each discovery as:

- Methodologically established.
- Replicated retrospective association.
- Promising but inconclusive.
- Cohort-dependent.
- Failed against strong controls.
- Unresolved because of insufficient data.
- Independently validated, only where genuinely supported.

Deliver `V20_CUMULATIVE_INFORMATION_REGISTRY.md`.

---

# PHASE 3 — DISCOVER THE PREDICTIVE LIFETIME OF EVERY INFORMATION SOURCE

This is the highest-priority new scientific investigation.

Previous research usually compared information sources at isolated horizons.

V20 must study how predictive information changes across time.

## Research horizons

Investigate:

- One session.
- Two sessions.
- Three sessions.
- Five sessions.
- Seven sessions.
- Ten sessions.
- Fifteen sessions.
- Twenty-one sessions.

The primary objectives remain five and 21 sessions.

Intermediate horizons are mechanism-discovery tools.

Do not redefine the primary forecasting objective around whichever intermediate horizon performs best retrospectively.

## Research A: Cumulative response

Measure whether an information source predicts the cumulative return from the original forecast origin to each horizon.

## Research B: Incremental response

Separately investigate non-overlapping future return components:

- Session one.
- Sessions two through three.
- Sessions four through five.
- Sessions six through ten.
- Sessions eleven through fifteen.
- Sessions sixteen through twenty-one.

This distinction is essential.

An information source may predict the first session strongly and appear to predict the entire monthly return simply because that initial movement remains embedded in the cumulative outcome.

That does not establish predictive information about later sessions.

## Research C: Predictive decay

For every information source, measure performance when using:

- Fresh information.
- One-session-delayed information.
- Three-session-delayed information.
- Five-session-delayed information.
- Ten-session-delayed information.
- Twenty-one-session-delayed information.

Investigate whether smoothed or persistent representations outperform fresh observations.

## Research D: Response shape

Determine whether each information family exhibits a historical relationship consistent with:

- Immediate information absorption.
- Gradual information absorption.
- Delayed predictive response.
- Persistent directional association.
- Temporary directional association.
- Reversal after an initial response.
- Risk prediction without directional prediction.

Do not interpret these statistical response shapes as proven economic transmission mechanisms.

## Required output

Construct a comprehensive information-source × horizon × target matrix.

For each eligible cell report:

- Parent performance.
- Enhanced performance.
- Absolute gain.
- Relative gain.
- Matched origin count.
- Disjoint outcome count.
- Earlier/later performance.
- Dependence-aware uncertainty.
- Shifted-information control.

Deliver `V20_PREDICTIVE_INFORMATION_LIFETIMES.md`.

---

# PHASE 4 — DEEP MONTHLY POSITIONING RESEARCH

V19's monthly residual correction is the highest-priority individual directional candidate.

Investigate its mechanism without merely tuning the existing winner.

## 4.1 Separate information blocks

Evaluate:

- FII index-futures position level.
- FII index-futures changes.
- DII index-futures position level.
- Proprietary participant position level.
- Participant gross exposure.
- Participant concentration.
- Participant trading-volume information.
- Stock-futures positioning.
- Aggregate options positioning.

Remove mechanically redundant features.

Do not infer portfolio delta exposure from aggregate option contract counts.

## 4.2 Investigate participant information across timescales

Compare:

- Daily position changes.
- Three-session changes.
- Five-session changes.
- Ten-session changes.
- Twenty-one-session changes.
- Persistent exposure levels.
- Positioning acceleration.
- Training-only standardized deviations.

Determine whether V19's larger 21-session positioning coefficients reflect a persistent market state or genuinely incremental information about future returns.

## 4.3 Investigate position innovations

Estimate expected positioning changes using prior available:

- NIFTY returns.
- Volatility.
- Historical positioning.
- Futures basis.
- Expiry information.
- Market breadth.

Compare ordinary position changes with unexpected position changes.

V19's unexpected-change implementation underperformed simple controls.

Any renewed experiment must introduce a genuinely different mechanism.

## 4.4 Coefficient stability

Investigate:

- Sign stability.
- Magnitude stability.
- Sensitivity to individual training episodes.
- Sensitivity to training-window size.
- Earlier-versus-later relationships.
- Expiry and rollover sensitivity.
- Parameter uncertainty.

Do not convert median historical coefficients into fixed trading rules.

## 4.5 Explain earlier/later divergence

The monthly positioning gain was:

- Earlier: +0.026437 Brier.
- Later: −0.000954 Brier.

Investigate whether this discrepancy is associated with:

- Changing participant exposure.
- Changing market volatility.
- Different market trends.
- Training composition.
- Different derivatives contract structures.
- Position concentration.
- Market regime.
- Estimation instability.
- Historical selection.

Do not assume the available observations can establish which explanation is causal.

Deliver `V20_MONTHLY_POSITIONING_MECHANISMS.md`.

---

# PHASE 5 — DEEP WEEKLY CORPORATE INFORMATION RESEARCH

V18's corporate residual correction remains the strongest original weekly probability reference.

Investigate why it performed better than ordinary fundamental augmentation.

## Candidate information blocks

- Announcement intensity.
- Material announcements.
- Financial results.
- Statistical earnings surprises.
- Sector-level fundamental developments.
- Corporate information dispersion.
- Scheduled earnings exposure.
- Corporate price-reaction disagreement.

Use the authenticated V18 corporate database.

## Required comparisons

- V14 parent.
- Bias-only correction.
- Count-only correction.
- Semantic correction.
- Structured fundamental correction.
- Complete V18 corporate residual correction.
- Positioning-only correction.
- Corporate plus positioning correction.
- Delayed and shifted corporate information.

Investigate whether improvement originates from:

1. Better conditional return location.
2. Probability shrinkage.
3. Correction of historical forecast bias.
4. Improved distribution asymmetry.
5. Better volatility estimation.
6. Genuine incremental corporate information.

## Special research question

Does corporate information add value primarily during periods with unusually high announcement activity?

Use causal thresholds and matched event-conditioned baselines.

Do not select favorable earnings periods retrospectively and present them as an operational regime-selection rule.

Deliver `V20_WEEKLY_CORPORATE_INFORMATION_MECHANISMS.md`.

---

# PHASE 6 — DEVELOP HORIZON-SPECIALIZED FORECASTING SYSTEMS

Do not assume the same feature matrix should forecast every horizon.

## Candidate weekly architecture

Investigate combinations of:

- Domestic market structure.
- Financial-sector rotation.
- Official equal-weight breadth.
- Corporate residual correction.
- Short-horizon implied volatility.
- Historical distribution shrinkage.

## Candidate monthly architecture

Investigate combinations of:

- Persistent financial-sector leadership.
- Derivatives participant positioning.
- Position concentration.
- Slow market-state variables.
- GJR-GARCH dispersion.
- Historical and symmetric distribution controls.

These are candidate architectures, not predetermined winning systems.

## Required experiments

Compare:

A. One shared information representation for every horizon.

B. Completely separate weekly and monthly models.

C. Shared market-state representation with horizon-specific output heads.

D. Shared core model with horizon-specific residual corrections.

E. Sparse horizon-specific feature groups.

F. Strongly regularized multi-horizon learning.

G. Fixed horizon-specialized distribution mixtures.

Assess whether separate architectures outperform shared architectures on matched historical samples.

Account for the additional selection risk created by choosing features separately for each horizon.

Deliver `V20_HORIZON_SPECIALIZED_MODELS.md`.

---

# PHASE 7 — PREDICT RETURN COMPONENTS THROUGH TIME

Develop a structured decomposition of the 21-session forecasting problem.

Instead of directly forecasting the entire monthly return, investigate whether different mechanisms predict different future segments.

## Example decomposition

- Sessions one through five.
- Sessions six through ten.
- Sessions eleven through fifteen.
- Sessions sixteen through twenty-one.

Construct the final return by consistently compounding or summing log-return components.

## Candidate hypotheses

- Corporate information may help forecast the first weekly component.
- Persistent positioning may contain information about later components.
- Short-term IV may inform initial risk.
- GJR-GARCH may inform longer-horizon volatility.

These hypotheses must be tested rather than assumed.

## Critical requirements

At the original forecast origin, all future components remain unknown.

Do not insert realized first-week returns into the original monthly prediction.

Preserve dependence between future return components.

Do not assume component forecasts are independent merely because their outcome windows do not overlap.

Investigate:

- Joint multi-output regression.
- Conditional historical component distributions.
- Low-rank coefficient sharing.
- Regularized distributed-horizon models.
- Joint residual resampling.
- Coherent path simulation.

Compare against direct five-session and 21-session forecasts.

Deliver `V20_TEMPORAL_RETURN_DECOMPOSITION.md`.

---

# PHASE 8 — INFORMATION COMPLEMENTARITY AND REDUNDANCY

V19 found that adding positioning to the strongest weekly corporate model worsened its forecasts.

Investigate why.

## Research questions

- Do corporate and positioning features provide overlapping information?
- Do their useful lifetimes differ?
- Do the estimated effects interfere because of model regularization?
- Does the additional feature block increase estimation variance?
- Do the information sources have conflicting historical relationships?
- Is one information source helpful only after controlling for another?

## Required experiments

Use matched, registered combinations of:

- Native market structure.
- Corporate information.
- Participant positioning.
- Delivery participation.
- Volatility information.

Measure:

- Standalone predictive performance.
- Marginal feature contribution.
- Leave-one-block-out performance.
- Alternative addition orders.
- Prediction correlation.
- Forecast-error correlation.
- Feature-space redundancy.
- Training-period sensitivity.

Investigate whether improvements arise from genuinely distinct information or merely additional shrinkage.

Preserve feature and expert duplication invariance.

Do not interpret order-dependent attribution as a causal economic decomposition.

Deliver `V20_INFORMATION_COMPLEMENTARITY.md`.

---

# PHASE 9 — DEVELOP STRONGER RESIDUAL CORRECTION FRAMEWORKS

V18 and V19 both found promising historical improvements by correcting existing forecast distributions.

Investigate residual correction as a dedicated architecture.

## Base framework

Forecast = Strong existing baseline + Estimated correction.

The correction must be learned from chronological historical forecast errors.

Do not fit corrections to in-sample residuals and describe them as out-of-sample forecast errors.

## Candidate correction mechanisms

- Bias-only correction.
- Return-location correction.
- Scale correction.
- Probability correction.
- Conditional asymmetry correction.
- Corporate-information correction.
- Positioning-information correction.
- Horizon-specific corrections.
- Regularized combinations.

## Preserve distribution coherence

A correction to direction probability, expected return or scale must produce a mathematically coherent complete predictive law.

Do not independently change several incompatible statistics and present them as one distribution.

## Conservative correction mechanisms

Investigate:

- Shrinkage toward zero correction.
- Fixed correction weights.
- Training-only learned correction weights.
- Correction magnitude limits.
- Parameter uncertainty.
- Mixtures of corrected and uncorrected laws.

Compare against the unchanged parent and a simple bias-only parent.

Report both active-model performance and complete-population performance including fallback cases.

Deliver `V20_STRUCTURAL_RESIDUAL_CORRECTIONS.md`.

---

# PHASE 10 — RESEARCH WHEN A FORECAST CORRECTION SHOULD BE ACTIVE

Previous adaptive gating and reliability models often failed.

V20 should investigate narrower, more interpretable activation mechanisms.

## Candidate activation variables

- Adequate matured training observations.
- Historical source completeness.
- Participant-position concentration.
- Corporate announcement intensity.
- Volatility state.
- Model disagreement.
- Feature-distribution distance.
- Correction parameter uncertainty.

## Required comparisons

- Always use the parent.
- Always apply the correction.
- Apply a fixed fractional correction.
- Use a predetermined conservative activation rule.
- Use a strongly regularized causal activation model.

Report:

- Forecast coverage.
- Active forecast count.
- Inactive forecast count.
- Active-sample performance.
- Complete-population performance.
- Performance of the parent on the same active dates.
- Earlier/later stability.

An activation rule is not useful merely because its selected forecasts perform well.

It must outperform the appropriate parent and justify what happens on excluded dates.

Use only matured historical losses when learning activation rules.

Deliver `V20_CORRECTION_ACTIVATION_RESEARCH.md`.

---

# PHASE 11 — PRESERVE AND IMPROVE RISK FORECASTING

The strongest historical risk findings must remain separate from directional research.

## Mandatory references

| Objective | Protected reference |
|---|---:|
| Raw weekly ATM IV MAE | 0.037814 |
| V16 offshore/domestic weekly MAE | 0.036469 |
| Monthly GJR volatility MAE | 0.033179 |
| Monthly GJR variance QLIKE | 0.199677 |
| Weekly volatility expansion Brier | 0.152707 |
| Monthly volatility expansion Brier | 0.172872 |
| Monthly Student-t GJR range CRPS | 0.015422 |
| Pre-auction weekly GIFT-first barrier Brier | 0.132201 |

Recover exact cutoffs and matched populations for every reference.

## Research hypotheses

Investigate whether:

- Positioning improves longer-horizon return location while GJR supplies scale.
- Corporate information improves weekly location while ATM IV supplies scale.
- Participant concentration improves volatility-transition estimates.
- Corporate and positioning information contribute more to asymmetry than volatility level.

Use matched comparisons against raw IV, GJR and the strongest existing risk systems.

Do not equate improved direction with improved volatility forecasting.

Do not force independently fitted components into a supposedly coherent joint law unless the mathematical construction supports it.

Deliver `V20_HORIZON_SPECIALIZED_RISK_MODELS.md`.

---

# PHASE 12 — INVESTIGATE THE LIMITS OF AVAILABLE PREDICTABILITY

After nineteen extensive research versions, we should understand not only what works, but also what the available data may be capable of supporting.

## Research A: Historical signal strength

Estimate the magnitude of the relationship between each major information family and its corresponding future return target.

Report:

- Rank correlation.
- Linear predictive association.
- Cross-validated incremental explanatory power.
- Forecast improvement over strong baselines.
- Stability across historical blocks.

## Research B: Estimation uncertainty

Investigate how much forecast variation arises from:

- Different training periods.
- Feature measurement uncertainty.
- Parameter instability.
- Outcome overlap.
- Alternative model specifications.
- Different historical market episodes.

## Research C: Power and detectable effects

Estimate the approximate historical effect sizes required to distinguish useful forecasts from noise under the available dependence structure.

Use simulation-based power analysis under explicitly documented assumptions.

Do not claim that a failed significance test establishes the absence of predictability.

## Research D: Historical learning efficiency

Investigate whether auxiliary stock, sector, event and participant observations can improve parameter estimation without incorrectly inflating the number of independent NIFTY outcomes.

Preserve the distinction between additional explanatory information and additional independent target observations.

## Research E: Remaining opportunities

Identify genuinely underexplored information families that could plausibly improve forecasts.

Prioritize authenticated new information over increasingly elaborate transformations of previously unsuccessful features.

Deliver `V20_PREDICTABILITY_AND_INFORMATION_LIMITS.md`.

---

# PHASE 13 — ADDITIONAL AUTHENTIC DATA DISCOVERY

Continue exploring the complete available market-data universe.

Prioritize unresolved sources from earlier versions:

- Authentic daily institutional cash flows.
- Longer daily CDSL coverage within 2025–2026.
- Dated sector-level foreign investment reports.
- Fund subscription and redemption information.
- Historical ETF creation/redemption records.
- Participant trading-volume records.
- Dated GIFT NIFTY contracts.
- Historical futures contract identities.
- Historical constituent membership and weights.
- Authentic analyst expectations.
- First-release macroeconomic observations.

For every source:

- Establish historical coverage.
- Verify information availability.
- Preserve revision history where available.
- Distinguish observation date from publication date.
- Document missing or inaccessible records.
- Identify a distinct predictive mechanism.

Do not manufacture observations to complete a dataset.

Do not repeatedly pursue unavailable endpoints without a materially different retrieval approach.

Use only 2025–2026 observations.

Deliver `V20_ADDITIONAL_INFORMATION_DISCOVERY.md`.

---

# PHASE 14 — DESIGN A UNIFIED RESEARCH FORECASTING FRAMEWORK

Develop a research-only system capable of producing separate horizon-specific forecasts.

## Layer 1: Causal data availability

Determine which information is available at:

- Previous-session close.
- Previous-session evening.
- Pre-auction.
- Post-open.
- Intraday checkpoints.

## Layer 2: Information representation

Construct distinct information families:

- Domestic structural information.
- Corporate information.
- Positioning information.
- Offshore information.
- Market-implied risk.
- Realized market risk.

## Layer 3: Horizon-specific estimation

Investigate separate weekly and monthly location, scale and asymmetry estimation.

## Layer 4: Residual correction

Apply only justified horizon-specific corrections.

## Layer 5: Predictive distribution

Generate coherent distributions producing:

- Directional probability.
- Expected return.
- Median return.
- Endpoint quantiles.
- Expected NIFTY endpoint.
- Prediction intervals.
- Tail probabilities.

## Layer 6: Risk and path forecasting

Provide separately validated volatility and path distributions where appropriate.

## Layer 7: Evidence reporting

For every forecast, disclose:

- Forecast origin.
- Information cutoff.
- Target session.
- Exact model version.
- Active correction.
- Parent forecast.
- Corrected forecast.
- Historical calibration.
- Missing information.
- Known limitations.

This architecture remains research-only.

Every layer must earn inclusion through appropriate historical comparisons.

Deliver `V20_EXPERIMENTAL_FORECASTING_FRAMEWORK.md`.

---

# PHASE 15 — FALSIFICATION AND CUMULATIVE SEARCH CONTROL

V20 must preserve all established validation safeguards.

## Core controls

- Chronological fitting.
- Matured-label enforcement.
- Training-only preprocessing.
- Point-in-time source availability.
- Purging and embargoes.
- Matched forecast clocks.
- Exact-copy invariance.
- Future-information sentinel tests.
- Dependence-aware uncertainty.

## Horizon-specific controls

- Delayed information.
- Shifted information.
- Block-permuted inputs.
- Randomized residual targets.
- Intermediate-return decomposition controls.
- Strong same-horizon baselines.
- Equal-complexity shared models.

## Residual correction controls

- Unchanged parent.
- Bias-only correction.
- Zero correction.
- Fixed shrinkage.
- Removing fitted bias.
- Delayed information.
- Removing favorable training episodes.

## Historical robustness

Report:

- Earlier cohort.
- Later cohort.
- Combined cohort.
- All disjoint-window phases.
- Leave-month-out results.
- Leave-extreme-episode-out results.
- Active-model coverage.
- Complete-population performance.

Run representative refit-and-reselection null experiments.

Preserve all negative results.

Do not claim V20-only statistical adjustment accounts for the entire adaptive V1–V20 research process.

Deliver `V20_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 16 — CONTROL RESEARCH COMPLEXITY

V20 must be a focused research phase.

Begin with no more than 20 primary hypotheses.

Register:

- Hypothesis.
- Economic or statistical rationale.
- Information family.
- Forecast target.
- Forecast cutoff.
- Strong parent.
- Primary metric.
- Negative control.
- Computational budget.
- Criteria for adaptive follow-up.

Prioritize:

1. Information lifetimes.
2. Monthly positioning mechanisms.
3. Weekly corporate correction mechanisms.
4. Horizon-specialized architectures.
5. Temporal return decomposition.

Use archived forecasts rather than refitting every historical system unnecessarily.

Perform computationally expensive follow-ups only where the initial experiments justify them.

Do not create hundreds of nearly identical models merely to report a larger search.

Continue exploring genuinely different mechanisms when particular hypotheses fail.

Deliver `V20_HYPOTHESIS_REGISTRY_AND_SEARCH_EFFICIENCY.md`.

---

# PHASE 17 — COMPLETE MULTI-HORIZON LEADERBOARD

Preserve the established historical cohorts:

- Earlier weekly: 173 origins.
- Later weekly: 92 origins.
- Combined weekly: 265 origins.
- Earlier monthly: 141 origins.
- Later monthly: 76 origins.
- Combined monthly: 217 origins.

These contain only 53 and 11 disjoint weekly and monthly outcome windows.

Maintain separate leaderboards for:

- Weekly direction.
- Monthly direction.
- Weekly return distributions.
- Monthly return distributions.
- Information lifetimes.
- Incremental return components.
- Corporate residual corrections.
- Positioning residual corrections.
- Volatility forecasts.
- Volatility transitions.
- Range and barrier forecasts.
- Cross-cohort stability.

For every comparison, report actual origin count, disjoint-window count, coverage, matched parent, Brier, log loss, CRPS, calibration and appropriate uncertainty.

Do not combine separate metric winners into a fictional universal model.

Keep forecasts issued at different decision cutoffs in separate comparisons.

Deliver `V20_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 18 — EXPAND AND PRESERVE THE FORWARD RESEARCH PANEL

Continue retrospective research while separately accumulating genuine forward observations.

## Existing records

Preserve the original V4 and V5 records.

V19 resolved the V4 five-session late-diagnostic forecast targeting November 25:

- Reference: 25,387.40.
- Realized endpoint: 25,819.25.
- Realized return: +1.7010%.
- LightGBM probability: 70.84%.
- Sector-model probability: 68.05%.

Preserve its late-diagnostic classification.

Do not describe it as independent confirmation.

The remaining five legacy records must be resolved when their targets mature.

## V19 frozen references

Preserve the three research references issued at 16:56 IST on November 25, 2026:

- Monthly neutral distribution targeting December 24.
- Five-session GJR volatility forecast targeting December 2.
- Twenty-one-session GJR volatility forecast targeting December 24.

Do not modify those forecasts.

## New research panel

Where operationally feasible, freeze exact implementations of:

### Weekly candidates

- Neutral or historical reference.
- V14 weekly parent.
- V18 corporate residual overlay.
- A justified V20 horizon-specialized candidate.

### Monthly candidates

- Symmetric monthly reference.
- Original V14 domestic/GJR parent.
- Bias-only correction.
- V19 positioning residual overlay.
- A justified V20 horizon-specialized candidate.

### Risk references

- Raw weekly ATM IV.
- Weekly IV/RV blend.
- Monthly GJR-GARCH.
- Monthly Student-t EGARCH volatility-expansion model.

### Opening reference

- Simple raw or calibrated GIFT NIFTY opening-gap model.

Issue each forecast only at its valid decision cutoff.

Archive:

- Exact issue timestamp.
- Source availability.
- Configuration hash.
- Model version.
- Complete predictive distribution.
- Target session.
- Matched benchmark.
- Actual outcome after maturity.

Do not issue retrospective predictions and label them prospective.

Do not extend forecast targets beyond the authorized 2026 scope.

Continue historical experimentation in parallel.

Deliver `V20_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V20_REPRODUCTION_AND_TIMING_AUDIT.md`
2. `V20_CUMULATIVE_INFORMATION_REGISTRY.md`
3. `V20_PREDICTIVE_INFORMATION_LIFETIMES.md`
4. `V20_MONTHLY_POSITIONING_MECHANISMS.md`
5. `V20_WEEKLY_CORPORATE_INFORMATION_MECHANISMS.md`
6. `V20_HORIZON_SPECIALIZED_MODELS.md`
7. `V20_TEMPORAL_RETURN_DECOMPOSITION.md`
8. `V20_INFORMATION_COMPLEMENTARITY.md`
9. `V20_STRUCTURAL_RESIDUAL_CORRECTIONS.md`
10. `V20_CORRECTION_ACTIVATION_RESEARCH.md`
11. `V20_HORIZON_SPECIALIZED_RISK_MODELS.md`
12. `V20_PREDICTABILITY_AND_INFORMATION_LIMITS.md`
13. `V20_ADDITIONAL_INFORMATION_DISCOVERY.md`
14. `V20_EXPERIMENTAL_FORECASTING_FRAMEWORK.md`
15. `V20_VALIDATION_AND_FALSIFICATION.md`
16. `V20_HYPOTHESIS_REGISTRY_AND_SEARCH_EFFICIENCY.md`
17. `V20_COMPLETE_MODEL_COMPARISON.md`
18. `V20_FORWARD_RESEARCH_LEDGER.md`
19. `V20_FINAL_RESEARCH_CONCLUSIONS.md`
20. `V20_NEXT_EXPERIMENTS.md`

Preserve complete reproducible Python code, feature definitions, source hashes, model configurations, per-origin predictions, predictive distributions, failed experiments and verification artifacts.

Keep all V1–V19 files unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Reproduction and synthesis

Reproduce V19.

Audit forecast timing.

Build the cumulative predictive information registry.

## Wave 2 — Information lifetime discovery

Investigate cumulative and incremental responses across horizons.

Determine whether corporate, positioning, breadth, rotation and risk information have different useful timescales.

## Wave 3 — Horizon specialization

Develop separate weekly and monthly architectures.

Investigate residual corrections and temporal return decomposition.

## Wave 4 — Integration

Combine only information sources that demonstrate complementary value.

Investigate coherent return distributions and horizon-specific risk models.

## Wave 5 — Falsification and forward evidence

Challenge apparent winners.

Quantify estimation uncertainty.

Preserve the prospective research panel.

Document the remaining unexplored mechanisms.

Do not stop retrospective research simply because forward observations require time to mature.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect our existing research repository, retrieve authenticated historical market observations, access available Upstox and NSE data, write Python code, develop quantitative models and execute feasible experiments.

Do not stop after producing a research plan.

Execute the research.

Continue actively exploiting the complete 2025–2026 market-data universe.

Do not import pre-2025 market observations.

Do not extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V20 QUESTIONS

Does every market information source have a distinct predictive lifetime?

Does corporate information primarily help forecast near-term returns?

Does participant positioning provide useful information about longer-horizon returns?

Does the apparent monthly positioning signal persist after removing the first week's movement?

Can horizon specialization outperform universal forecasting architectures?

Can we improve our original weekly and monthly forecasts by integrating the strongest discoveries from all nineteen research versions?

We have spent nineteen research versions discovering individual sources of predictive intelligence.

V20 must investigate how those sources operate through time, how they interact, and how they can be combined without destroying useful information.

Explore creatively.

Execute meaningful experiments.

Prioritize genuinely new knowledge.

Preserve negative findings.

Do not manufacture certainty.

**BEGIN V20 RESEARCH.**