# NIFTY V21 — BOTTOM-UP MARKET INTELLIGENCE, CROSS-SECTIONAL LEARNING & PROBABILISTIC INDEX RECONSTRUCTION

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, sector indices, global markets, derivatives, corporate disclosures, participant positioning, historical candles, databases and Python execution capabilities.

We have completed V1 through V20 of our NIFTY forecasting research.

Our research has covered an extensive universe of technical, statistical, fundamental, structural, positioning and market-implied information.

Most previous forecasting systems attempted to predict NIFTY directly.

V21 must investigate a different mechanism:

**Can we forecast the underlying components of the Indian equity market and reconstruct a coherent predictive distribution of NIFTY from those components?**

We have access to substantially more individual-equity and sector observations than independent NIFTY outcomes.

Investigate whether those observations can improve parameter estimation, identify common predictive mechanisms and reduce forecasting uncertainty.

Do not incorrectly treat correlated equity observations as independent index outcomes.

Do not merely repeat previous unsuccessful sector-transfer experiments.

Continue actively experimenting using 2025–2026 observations.

---

# PRIMARY OBJECTIVES

Retain our original forecasting targets:

- NIFTY return over the next five trading sessions.
- NIFTY return over the next 21 trading sessions.
- Probability of a positive return.
- Expected return.
- Median return.
- Complete predictive return distribution.

Additionally investigate:

- Individual-stock return distributions.
- Sector return distributions.
- Common market-factor predictability.
- Sector-relative return predictability.
- Index contribution forecasting.
- Cross-sectional return dispersion.
- Market concentration.
- Joint equity-market risk.
- Bottom-up index reconstruction.

The individual-stock and sector research must ultimately address whether it can improve the original NIFTY forecasting objectives.

## RESTRICTIONS

- Use only 2025–2026 observations.
- Preserve the November 17, 2026 frozen historical vintage.
- Acquire additional completed 2026 observations separately.
- No pre-2025 market observations or fitted states.
- Preserve all V1–V20 artifacts and issued forecasts.
- No live trading, broker orders or capital deployment.
- All previously examined historical observations remain research-exposed.

---

# PHASE 1 — REPRODUCE V20 AND ESTABLISH STRONG REFERENCES

Read the complete V20 research index, all 20 reports, source code, model configurations, feature definitions, experiment registry and predictive laws.

Recover exact implementations.

## Original weekly references

| Model | Brier | CRPS |
|---|---:|---:|
| V14 weekly parent | 0.228529 | 0.010457 |
| V18 corporate residual correction | 0.223481 | 0.010318 |
| V20 training-omission candidate | 0.221693 | 0.010274 |
| V20 corporate price-reaction candidate | 0.223384 | 0.010258 |

## Original monthly references

| Model | Brier | CRPS |
|---|---:|---:|
| Neutral probability | 0.250000 | Recover corresponding law |
| V14 monthly parent | 0.245042 | 0.024989 |
| V19 positioning correction | 0.228199 | 0.024010 |
| V20 embargo candidate | 0.228088 | 0.024003 |
| V20 smoothed positioning | 0.228602 | 0.023786 |

Preserve the separately evaluated 08:55 references, particularly V17 session decomposition and the archived GJR return distribution.

## Important negative findings

Reproduce:

- Unsuccessful previous sector-transfer experiments.
- Unsuccessful general cross-sectional transfer experiments.
- V20's unsuccessful temporal return decomposition.
- V19 delivery-based stock ranking.
- V18 corporate event-response pooling.
- V20's weak post-first-week positioning results.

Determine exactly why the previous cross-sectional implementations failed.

Distinguish failures of:

- Stock-relative return prediction.
- Absolute stock return prediction.
- Sector prediction.
- Market-factor prediction.
- Transfer learning.
- Aggregation.
- Distribution construction.

Preserve every original forecast.

Deliver `V21_REPRODUCTION_AND_PRIOR_TRANSFER_FORENSICS.md`.

---

# PHASE 2 — BUILD AN AUTHENTIC HISTORICAL EQUITY UNIVERSE

Investigate the complete Indian-equity universe available through Upstox and NSE.

## Candidate universe

- NIFTY 50 constituents.
- NIFTY 100 constituents.
- NIFTY 200 constituents.
- NIFTY 500 constituents.
- Liquid banking and financial-services stocks.
- IT stocks.
- Energy stocks.
- Automobile stocks.
- Consumer stocks.
- Healthcare stocks.
- Industrial stocks.
- Relevant ETFs.

Use existing authenticated equity archives before acquiring redundant data.

## Required historical data

For each security, investigate:

- Daily OHLC.
- Traded volume.
- Turnover.
- Delivery participation.
- Corporate announcements.
- Financial results.
- Sector classification.
- Instrument identifiers.
- Corporate actions.
- Historically available shares outstanding.
- Historical index membership.
- Historical free-float market capitalization.
- Historical index weights.

Do not assume all fields are available.

## Historical universe construction

Prioritize authentic dated constituent membership and weights.

Where unavailable, establish fixed eligible research cohorts using information observed during 2025.

For example, use a predefined January 2025 liquidity selection rule, applied only after its selection observations are available.

Do not use today's constituent list as historical membership.

Do not silently exclude delisted, suspended or subsequently unsuccessful securities.

Distinguish price-index returns from total shareholder returns.

Corporate-action adjustments must be causally valid and consistent with the target price index.

Deliver `V21_HISTORICAL_EQUITY_UNIVERSE.md`.

---

# PHASE 3 — RECONSTRUCT INDEX RETURN CONTRIBUTIONS

This is the highest-priority feasibility investigation.

Before attempting to forecast NIFTY from individual stocks, determine whether we can accurately reconstruct its realized returns using historically valid inputs.

## Track A: Authentic index reconstruction

Where dated constituent membership and weights exist, investigate the actual index calculation methodology.

Account for:

- Free-float weighting.
- Weight drift.
- Constituent changes.
- Corporate actions.
- Index divisor changes.
- Rebalancing.
- Price-index conventions.

Verify reconstructed historical index returns against official NIFTY returns.

## Track B: Fixed-weight research portfolios

Where authentic historical weights are unavailable, construct clearly labeled proxy portfolios.

Compare:

- Equal-weight portfolios.
- Historical liquidity-weighted portfolios.
- Sector-balanced portfolios.
- Historically valid capitalization-weighted portfolios.
- Fixed proxy baskets.

These are not necessarily NIFTY replicas.

## Track C: Statistical index reconstruction

Investigate whether a small number of official sector indices can reconstruct NIFTY returns using constrained coefficients estimated from earlier observations.

Potential methods:

- Nonnegative regression.
- Simplex-constrained regression.
- Strongly regularized sector mixtures.
- Training-only factor reconstruction.

Statistically estimated coefficients must not be presented as official constituent weights.

## Evaluation

Measure:

- Reconstruction bias.
- Tracking-error volatility.
- MAE.
- RMSE.
- Correlation.
- Weekly and monthly tracking errors.
- Sensitivity to major market movements.
- Stability across historical periods.

Do not introduce future realized weights into an original forecast.

If reliable index reconstruction is impossible, continue with explicit proxy-portfolio and residual-index forecasting.

Deliver `V21_INDEX_RETURN_RECONSTRUCTION.md`.

---

# PHASE 4 — SEPARATE COMMON MARKET RETURNS FROM RELATIVE RETURNS

A stock return contains several possible components.

Investigate a parsimonious factor decomposition:

Stock return = Market component + Sector component + Stock-specific component.

For example:

r(i,t) = beta(i) × M(t) + gamma(i) × F(sector,t) + epsilon(i,t)

Estimate exposures using earlier eligible observations only.

## Research questions

1. Can common market returns be forecast more effectively using pooled stock information?

2. Can future sector-relative returns be estimated more reliably than absolute returns?

3. Does stock-specific predictability contribute materially to the weighted index?

4. Does apparently successful stock ranking disappear when translated into an aggregate market forecast?

5. Are the strongest sector forecasts primarily reproducing their exposure to NIFTY itself?

## Candidate factors

Investigate:

- Broad market.
- Financial leadership.
- Defensive/cyclical rotation.
- Size.
- Momentum.
- Relative volatility.
- Quality, where historically valid.
- Liquidity.
- Market concentration.

Compare economically defined factors with training-only statistical factors.

Do not use actual future market-factor returns when producing original forecasts.

All future factors must themselves be forecast, simulated or integrated out.

Deliver `V21_MARKET_SECTOR_AND_STOCK_FACTOR_DECOMPOSITION.md`.

---

# PHASE 5 — CROSS-SECTIONAL RETURN FORECASTING

Develop individual-stock and sector-level research forecasts.

## Candidate targets

- Absolute future return.
- Market-relative return.
- Sector-relative return.
- Volatility-normalized return.
- Probability of outperforming the market.
- Future return magnitude.
- Future realized volatility.

## Candidate inputs

Use the strongest authenticated historical information:

### Technical information

- Momentum.
- Trend.
- Relative strength.
- Volatility.
- Volume and turnover.
- Market-relative movement.

### Structural information

- Sector leadership.
- Official breadth.
- Stock-level participation.
- Financial rotation.
- Return dispersion.

### Fundamental information

- Corporate disclosures.
- Financial results.
- Statistical earnings surprises.
- Observed announcement reactions.

### Positioning information

- Delivery participation.
- Large disclosed transactions.
- Authenticated stock-derivatives information where available.

### Market-risk information

- Index implied volatility.
- Sector volatility.
- Global risk.
- Broad-market conditions.

## Candidate methods

Begin with simple, sample-efficient approaches:

- Pooled Ridge.
- Elastic Net.
- Hierarchical regression.
- Cross-sectional rank models.
- Regularized factor regression.
- Sector-specific partial pooling.
- Low-rank multi-output regression.

Investigate shallow nonlinear models only when simpler models establish a promising mechanism.

## Evaluation

Report:

- Date-level rank correlation.
- MAE.
- RMSE.
- Brier.
- CRPS.
- Calibration.
- Sector-level forecast quality.
- Stability across dates and sectors.

Weight evaluation dates appropriately so that dates containing more available equities do not automatically dominate the results.

Deliver `V21_CROSS_SECTIONAL_RETURN_FORECASTING.md`.

---

# PHASE 6 — LEARN SHARED PREDICTIVE RELATIONSHIPS ACROSS EQUITIES

Previous broad transfer-learning approaches failed to establish reliable NIFTY improvements.

V21 must investigate more specifically what information can be shared.

## Candidate relationships

- Momentum persistence across related equities.
- Sector-relative reversal.
- Earnings response across comparable companies.
- Delivery-conditioned return behavior.
- Volatility-normalized price response.
- Liquidity-dependent price movement.
- Exposure to common market shocks.

## Candidate architectures

A. Independent stock models.

B. Fully pooled equity model.

C. Sector-specific pooled models.

D. Shared coefficients with strongly regularized sector deviations.

E. Shared coefficients with strongly regularized company deviations.

F. Separate common-market and relative-return forecasting heads.

G. Historical-factor model with pooled residual estimation.

## Critical validation requirements

Group training and evaluation by market date.

For every prediction, require fully matured historical outcomes.

Do not train on future returns from other stocks observed during the same unresolved market period.

Use appropriate temporal purging across all securities.

Evaluate transfer learning against:

- NIFTY-only training.
- No-transfer models.
- Randomized auxiliary targets.
- Shifted auxiliary observations.
- Equal-complexity controls.
- Sector-neutral controls.

Additional stock-level observations may improve estimation of shared parameters, but cannot be counted as independent NIFTY outcomes.

Deliver `V21_SAMPLE_EFFICIENT_CROSS_SECTIONAL_LEARNING.md`.

---

# PHASE 7 — FORECAST FUTURE SECTOR CONTRIBUTIONS

Investigate whether future NIFTY returns can be understood through the expected contributions of major market segments.

## Research targets

For each sector, estimate:

- Expected absolute return.
- Expected market-relative return.
- Conditional volatility.
- Probability of outperformance.
- Contribution to aggregate market return.
- Contribution to aggregate market risk.

Use authentic dated weights where available.

Otherwise, describe contributions to the defined proxy portfolio rather than NIFTY itself.

## Core experiments

Compare:

1. Direct NIFTY forecasting.
2. Direct sector forecasting.
3. Bottom-up stock-to-sector forecasting.
4. Sector-to-index reconstruction.
5. Stock-to-index reconstruction.
6. Direct NIFTY forecasting with sector-derived residual corrections.

Determine whether sector forecasting improves the aggregate forecast or merely redistributes an already-known market expectation.

## Mechanism decomposition

Investigate whether improvements arise from:

- Better estimation of common market direction.
- Better relative-sector predictions.
- More accurate exposure estimates.
- Better conditional volatility.
- Better estimation of cross-sector dependence.

Deliver `V21_SECTOR_CONTRIBUTION_FORECASTING.md`.

---

# PHASE 8 — JOINT RETURN DISTRIBUTIONS AND CROSS-STOCK DEPENDENCE

This is essential.

Forecasting every stock independently and averaging the predictions does not produce a reliable index distribution.

Stocks share substantial common risk.

## Investigate dependence structures

Compare:

- Historical covariance.
- Shrunk covariance.
- Market-factor covariance.
- Sector-factor covariance.
- Dynamic factor covariance.
- Conditional historical residual blocks.
- Heavy-tailed factor innovations.

Use simple low-dimensional dependence structures before attempting complex high-dimensional models.

## Joint scenario generation

Generate simultaneous stock or sector return scenarios using:

- Forecast common market factors.
- Forecast sector factors.
- Conditional stock-specific returns.
- Shared volatility states.
- Historically estimated residual dependence.

For each simulated scenario, reconstruct the corresponding index or proxy-portfolio return.

Account for future weight drift where relevant.

## Coherence

Derive from the same complete joint law:

- Probability of positive index return.
- Expected return.
- Median return.
- Return quantiles.
- Expected endpoint.
- Central prediction intervals.
- Tail probabilities.

Do not average individual-stock probabilities to calculate the probability of an index up move.

Do not assume cross-stock independence unless explicitly testing it as a diagnostic control.

Simulation draws do not create additional historical evidence.

Test Monte Carlo convergence using increasing scenario counts.

Deliver `V21_JOINT_EQUITY_RETURN_DISTRIBUTIONS.md`.

---

# PHASE 9 — TEST TOP-DOWN VERSUS BOTTOM-UP FORECASTING

Construct a controlled competition between fundamentally different forecasting architectures.

## Candidate A: Strong direct forecast

The strongest justified V20 weekly or monthly predictive law.

## Candidate B: Sector-based bottom-up forecast

Aggregate coherent sector forecasts.

## Candidate C: Stock-based bottom-up forecast

Aggregate coherent individual-stock forecasts.

## Candidate D: Common-factor forecast

Forecast the common market factor and reconstruct aggregate returns.

## Candidate E: Hybrid forecast

Use the strong direct NIFTY distribution as the common market anchor while allowing cross-sectional information to adjust its location, scale or asymmetry.

## Candidate F: Residual correction

Estimate whether bottom-up information predicts chronological errors of the strongest direct NIFTY system.

## Candidate G: Complete-law mixture

Combine direct and bottom-up distributions using fixed or strongly regularized training-only weights.

## Mandatory evaluation

Compare:

- Direct versus bottom-up.
- Bottom-up versus simple historical aggregation.
- Shared versus independent stock models.
- Joint versus independent scenario construction.
- Corrected versus uncorrected NIFTY laws.
- Weekly versus monthly performance.

Test whether apparent improvements come from return location, volatility, asymmetry or simple probability shrinkage.

Do not choose a weak direct parent merely to make bottom-up forecasting appear successful.

Deliver `V21_TOP_DOWN_VERSUS_BOTTOM_UP.md`.

---

# PHASE 10 — MARKET CONCENTRATION AND EFFECTIVE DIVERSIFICATION

Investigate whether the index is more predictable when its performance is dominated by particular stocks or sectors.

## Candidate measurements

- Concentration of market weights.
- Concentration of expected return contributions.
- Concentration of realized return contributions.
- Effective number of contributing securities.
- Sector return dispersion.
- Cross-stock synchronization.
- Common-factor variance share.
- Financial-sector leadership.
- Heavyweight versus broader-market divergence.

Distinguish observable index weights from statistical exposure proxies.

## Research questions

- Does broad participation improve directional persistence?
- Does concentrated leadership increase forecast uncertainty?
- Does common-factor dominance reduce the benefit of stock-specific forecasts?
- Do stock-specific signals cancel when aggregated?
- Can cross-sectional dispersion predict subsequent index volatility?

Compare against established official breadth, rotation and raw-IV controls.

Deliver `V21_CONCENTRATION_AND_DIVERSIFICATION.md`.

---

# PHASE 11 — BOTTOM-UP RISK FORECASTING

Investigate whether cross-stock and cross-sector risk information improves NIFTY volatility forecasting.

## Candidate mechanisms

- Predicted individual-stock volatility.
- Predicted sector volatility.
- Conditional correlations.
- Sector volatility divergence.
- Common market-risk factors.
- Changes in cross-sectional synchronization.
- Downside semivariance.
- Concentration of risk contributions.

Where the required weights and covariance forecasts are available, investigate portfolio variance:

Variance = w-transpose × Covariance × w.

Account for the distinction between conditional return variance and the future realized-volatility target.

## Strong references

- Raw weekly ATM IV MAE: 0.037814.
- V16 weekly offshore/domestic risk MAE: 0.036469.
- Monthly GJR volatility MAE: 0.033179.
- Monthly GJR variance QLIKE: 0.199677.
- Weekly volatility expansion Brier: 0.152707.
- Monthly volatility expansion Brier: 0.172872.

Investigate whether stock-level information improves risk forecasts beyond the implied and historical volatility information already available.

Do not force direction and risk forecasting to use the same architecture.

Deliver `V21_BOTTOM_UP_RISK_FORECASTING.md`.

---

# PHASE 12 — INTEGRATE PREVIOUS CORPORATE AND POSITIONING DISCOVERIES

Preserve the strongest V18–V20 information sources.

Investigate whether their usefulness becomes clearer through bottom-up modeling.

## Corporate information

Test whether corporate disclosures improve:

- Individual-stock forecasts.
- Sector forecasts.
- Weighted return contributions.
- Weekly NIFTY residual forecasts.

Compare event content with simple announcement counts and previously observed price reactions.

## Positioning information

Test whether aggregate participant positioning improves:

- Common market-factor forecasts.
- Sector-factor forecasts.
- Monthly index residual forecasts.
- Cross-sectional risk forecasts.

Do not fabricate stock-specific participant positioning from exchange-wide aggregate reports.

## Required comparison

Investigate whether:

- Corporate information works better at the company level.
- Positioning works better at the common-factor level.
- Implied volatility works better as a risk anchor.
- Official breadth works better as a market-participation factor.

These are hypotheses, not established model assignments.

Deliver `V21_INFORMATION_SOURCE_SPECIALIZATION.md`.

---

# PHASE 13 — RESEARCH STATISTICAL POWER AND SAMPLE EFFICIENCY

V20 estimated that the current historical sample has limited power to distinguish modest forecasting gains from noise.

Investigate whether cross-sectional parameter sharing can genuinely improve estimation.

## Required analysis

- Number of stock observations.
- Number of distinct market dates.
- Number of distinct sectors.
- Number of disjoint outcome windows.
- Cross-sectional dependence.
- Common-factor dominance.
- Effective sample diagnostics.
- Parameter uncertainty.
- Training-sample sensitivity.

## Simulation research

Construct controlled synthetic experiments under explicitly stated assumptions.

Investigate cases containing:

- A genuinely shared predictive relationship.
- Sector-specific predictive relationships.
- Pure common-market noise.
- Correlated stock-specific noise.
- Spurious cross-sectional relationships.
- No genuine index predictability.

Determine whether the proposed architecture can distinguish these cases.

Compare pooled estimation against direct NIFTY estimation.

Do not treat simulated results as actual market validation.

The purpose is to understand when bottom-up learning could help and when it cannot.

Deliver `V21_SAMPLE_EFFICIENCY_AND_POWER.md`.

---

# PHASE 14 — AGGRESSIVE FALSIFICATION

## Universe controls

- Historical membership verification.
- Corporate-action sensitivity.
- Random historically eligible stock subsets.
- Removal of dominant securities.
- Alternative sector groupings.
- Proxy-weight sensitivity.
- Missing-security sensitivity.

## Cross-sectional controls

- Date-grouped validation.
- Shuffled stock-specific labels.
- Shifted company features.
- Randomized sector assignments.
- Common-factor-only controls.
- Equal-complexity direct models.
- Training-only factor estimation.

## Joint-distribution controls

- Independent stock scenarios as a diagnostic.
- Alternative covariance estimators.
- Historical joint residual blocks.
- Alternative factor structures.
- Scenario convergence.
- Tail calibration.
- Tracking-error sensitivity.

## Forecasting safeguards

- Chronological estimation.
- Fully matured labels.
- Training-only preprocessing.
- Appropriate purging and embargoes.
- Exact forecast-clock matching.
- Future-information sentinel tests.
- Exact-copy invariance.
- Matched-origin comparisons.
- Dependence-aware uncertainty.
- Representative refit-and-reselection null experiments.

Preserve earlier and later cohort results separately.

Investigate the effect of removing individual favorable market episodes.

Do not claim V21-only statistical adjustments remove cumulative V1–V21 selection bias.

Deliver `V21_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 15 — EXPERIMENT DISCIPLINE

Begin with no more than 16 materially distinct primary hypotheses.

For each hypothesis register:

- Proposed mechanism.
- Required information.
- Forecast target.
- Decision cutoff.
- Primary metric.
- Strong reference model.
- Negative control.
- Minimum data-quality requirements.
- Computational budget.
- Criteria for follow-up.

## Stage-one feasibility gates

First determine:

1. Can we reconstruct a sufficiently accurate historical index or explicitly defined proxy?
2. Can we forecast stock or sector returns better than simple controls?
3. Does the predictive information survive aggregation?
4. Does it contribute anything beyond the common market factor?

Do not spend most of the research budget constructing sophisticated joint models if the underlying forecasts contain no incremental information.

If bottom-up directional forecasting fails, investigate whether the same architecture improves volatility, covariance estimation or model uncertainty.

Continue the broader research rather than terminating the project.

Deliver `V21_HYPOTHESIS_REGISTRY.md`.

---

# PHASE 16 — COMPLETE RESEARCH COMPARISON

Preserve the established cohorts:

- Weekly: 173 earlier, 92 later, 265 combined.
- Monthly: 141 earlier, 76 later, 217 combined.

These contain only 53 and 11 disjoint outcome windows.

Maintain separate leaderboards for:

1. Individual-stock absolute return prediction.
2. Individual-stock relative return prediction.
3. Sector forecasting.
4. Common-market-factor forecasting.
5. Index reconstruction accuracy.
6. Bottom-up weekly probability forecasting.
7. Bottom-up monthly probability forecasting.
8. Weekly and monthly return distributions.
9. Hybrid direct and bottom-up forecasts.
10. Cross-sectional risk forecasting.
11. Sample-efficient learning.

Report:

- Brier.
- Log loss.
- CRPS.
- Accuracy.
- Balanced accuracy.
- MAE.
- RMSE.
- Rank correlation.
- Variance QLIKE.
- Calibration.
- Tracking error.
- Prediction interval coverage and width.
- Matched origin count.
- Distinct market dates.
- Disjoint outcome windows.
- Search-adjusted uncertainty.

Do not report stock-level predictive improvements as index-level improvements unless the index comparison demonstrates them.

Deliver `V21_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 17 — FORWARD RESEARCH AND OPERATIONAL READINESS

Preserve all V4–V20 issued forecasts.

Resolve matured forecasts using authoritative outcomes without modifying the original predictions.

V19 and V20 have already frozen neutral-return and volatility references.

However, the strongest weekly corporate and monthly positioning directional candidates were not reported as newly frozen forward forecasts.

Investigate and document the exact operational blockers preventing their prospective issuance.

Where feasible, prepare a small frozen research panel containing:

## Weekly

- Symmetric or historical benchmark.
- V14 weekly parent.
- V18 corporate residual correction.
- V20 weekly Brier candidate.
- V20 weekly distribution candidate.

## Monthly

- Symmetric benchmark.
- V14 monthly parent.
- V19 positioning correction.
- V20 smoothed-positioning candidate.

## Risk

- Raw ATM IV.
- IV/RV blend.
- GJR-GARCH.
- Student-t EGARCH.

## Opening

- Simple GIFT NIFTY opening-gap forecast.

Any new V21 candidate should be added only after its exact implementation and historical comparison are documented.

Record genuine issue timestamps, information cutoffs, full predictive laws, source hashes and configuration hashes.

Do not retrospectively issue missing forecasts.

If the valid issue time has passed, preserve the missed issue as such and use the next valid research opportunity.

Do not issue targets extending beyond December 2026 without authorization.

Continue retrospective experimentation in parallel.

Deliver `V21_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V21_REPRODUCTION_AND_PRIOR_TRANSFER_FORENSICS.md`
2. `V21_HISTORICAL_EQUITY_UNIVERSE.md`
3. `V21_INDEX_RETURN_RECONSTRUCTION.md`
4. `V21_MARKET_SECTOR_AND_STOCK_FACTOR_DECOMPOSITION.md`
5. `V21_CROSS_SECTIONAL_RETURN_FORECASTING.md`
6. `V21_SAMPLE_EFFICIENT_CROSS_SECTIONAL_LEARNING.md`
7. `V21_SECTOR_CONTRIBUTION_FORECASTING.md`
8. `V21_JOINT_EQUITY_RETURN_DISTRIBUTIONS.md`
9. `V21_TOP_DOWN_VERSUS_BOTTOM_UP.md`
10. `V21_CONCENTRATION_AND_DIVERSIFICATION.md`
11. `V21_BOTTOM_UP_RISK_FORECASTING.md`
12. `V21_INFORMATION_SOURCE_SPECIALIZATION.md`
13. `V21_SAMPLE_EFFICIENCY_AND_POWER.md`
14. `V21_VALIDATION_AND_FALSIFICATION.md`
15. `V21_HYPOTHESIS_REGISTRY.md`
16. `V21_COMPLETE_MODEL_COMPARISON.md`
17. `V21_FORWARD_RESEARCH_LEDGER.md`
18. `V21_FINAL_RESEARCH_CONCLUSIONS.md`
19. `V21_NEXT_EXPERIMENTS.md`

Preserve all reproducible source code, data receipts, feature definitions, eligibility rules, fit configurations, scenario distributions, failed experiments and verification artifacts.

Keep V1–V20 unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Establish feasibility

Reproduce prior references.

Audit historical equity membership and weighting information.

Determine whether authentic index reconstruction is possible.

## Wave 2 — Discover component predictability

Research stock, sector and common-market factors.

Investigate whether pooled estimation improves predictive relationships.

## Wave 3 — Investigate aggregation

Determine whether useful component forecasts survive aggregation.

Develop coherent joint return distributions only where justified.

## Wave 4 — Integrate

Compare direct, bottom-up and hybrid forecasting systems.

Investigate residual correction and bottom-up risk estimation.

## Wave 5 — Falsification and scientific synthesis

Challenge all apparent improvements.

Quantify estimation uncertainty.

Preserve prospective references.

Document whether bottom-up forecasting provides genuinely distinct information.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect our existing repository, access authenticated historical market data, retrieve permitted datasets, write Python code, fit statistical and machine-learning models, simulate joint equity-market distributions and execute feasible experiments.

Do not stop at producing a research plan.

Execute the research.

Continue actively exploiting the complete 2025–2026 market-data universe.

Do not import pre-2025 observations.

Do not extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V21 QUESTIONS

Can individual-equity observations improve the estimation of common market-return relationships?

Can sector forecasting improve NIFTY direction forecasting?

Does stock-specific predictability survive aggregation into an index?

Can bottom-up return distributions outperform direct NIFTY return distributions?

Can corporate information improve company-level forecasts while participant positioning improves common-market forecasts?

Can cross-sectional learning help overcome some of our parameter-estimation limitations without artificially inflating the number of independent market outcomes?

We have spent twenty research versions attempting to understand and forecast NIFTY.

V21 must investigate whether forecasting its underlying components provides a genuinely different and more effective approach.

Explore creatively.

Prioritize scientific discoveries over experiment counts.

Preserve negative findings.

Do not manufacture predictive certainty.

**BEGIN V21 RESEARCH.**