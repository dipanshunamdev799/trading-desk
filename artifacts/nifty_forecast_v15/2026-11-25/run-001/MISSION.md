# NIFTY V15 — SEQUENTIAL MARKET INTELLIGENCE, INFORMATION ARRIVAL & DYNAMIC FORECAST UPDATING

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global markets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V14 of our NIFTY forecasting research.

We have extensively investigated statistical models, machine learning, Indian market internals, sector rotation, official equal-weight breadth, global-market relationships, training-data composition, options-implied expectations, volatility models, extreme movements and coherent market-path simulations.

Our historical results have improved, but independent forecasting superiority remains unestablished.

**We are deliberately continuing active research using 2025–2026 observations.**

V15 must investigate a substantially different forecasting framework.

Instead of treating each forecast as an isolated prediction, investigate how forecasts should evolve as new information arrives.

### Central objective

Develop a research framework capable of learning:

- What the market currently implies about its future.
- How those expectations change.
- Which new information contributes to forecast revisions.
- Whether forecast revisions improve predictive quality.
- Whether observed price movements invalidate earlier market assumptions.
- How uncertainty evolves as a forecast approaches its endpoint.

Continue exploring new approaches.

Do not simply repeat V1–V14 with additional hyperparameters.

## PRIMARY FORECASTING TARGETS

Retain:

- Next five NIFTY trading sessions.
- Next 21 NIFTY trading sessions.

Continue researching:

- Directional probability.
- Expected and median returns.
- Endpoint distributions.
- Realized volatility.
- Volatility transitions.
- Trading ranges.
- Extreme movements.
- Barrier-touch probabilities.
- Coherent market paths.

Introduce fixed-endpoint and sequential forecast updating as additional research frameworks.

### Research restrictions

- Use only 2025–2026 observations.
- Preserve the frozen November 17, 2026 vintage.
- Additional completed 2026 sessions may be acquired separately.
- No pre-2025 market observations or fitted states.
- No live trading.
- No broker orders.
- No capital deployment.
- Preserve all V1–V14 artifacts.
- All previously examined historical observations remain research-exposed.

---

# PHASE 1 — REPRODUCE AND UNDERSTAND V14

Read the complete V14 research index, all 19 reports, model configurations, historical predictions, full path laws, source files, experiment registries and verification artifacts.

Recover exact model implementations from the repository.

## Weekly volatility references

| Model | MAE |
|---|---:|
| Trailing realized volatility | 0.046394 |
| Raw ATM implied volatility | 0.037814 |
| V13 calibrated IV | 0.037517 |
| V14 IV-fed GJR | 0.037402 |
| Fixed 75% IV / 25% RV variance blend | 0.038196 |

Preserve variance QLIKE comparisons, especially the strong raw-IV and fixed-mixture benchmarks.

## Monthly volatility references

| Model | MAE |
|---|---:|
| Trailing realized volatility | 0.048044 |
| Bracketed IV | 0.039406 |
| V13 GJR-GARCH | 0.033179 |
| V14 IV/GJR blend | 0.033780 |

## Volatility expansion references

| Horizon | Historical Brier | Raw-IV Brier |
|---|---:|---:|
| Weekly | 0.222296 | 0.155657 |
| Monthly | 0.299434 | 0.186036 |

Reproduce the exact probability-construction procedure.

Do not assume a point estimate of implied volatility is itself a probability forecast of expansion.

## Path and endpoint references

- Weekly endpoint Brier: 0.228529.
- Weekly endpoint CRPS: 0.010457.
- Monthly endpoint Brier: 0.245042.
- Monthly endpoint CRPS: 0.024750.
- Weekly diffusion range CRPS: 0.005793.
- Monthly Student-t GJR range CRPS: 0.015422.
- Monthly Student-t GJR nominal-80% range coverage: 76.5%.
- Weekly touch Brier: 0.143371.
- Monthly touch Brier: 0.181085.

These point leaders come from different systems.

Do not combine them into one fictitious winning model.

Deliver `V15_REPRODUCTION_AND_BASELINES.md`.

---

# PHASE 2 — INTRODUCE FIXED-ENDPOINT FORECASTING

Previous research predominantly predicted returns over rolling five-session and 21-session horizons.

V15 must additionally investigate forecasts that retain the same target date while receiving new information.

## Weekly example

At session T0, issue a forecast for the close at T+5.

Then reconstruct forecast updates after:

- T+1.
- T+2.
- T+3.
- T+4.

Every update must predict the same original T+5 endpoint.

Do not silently move the target forward another five sessions.

## Monthly example

At T0, issue a forecast for T+21.

Update the forecast as subsequent sessions complete.

Evaluate daily updates and registered checkpoints such as:

- T+1.
- T+5.
- T+10.
- T+15.
- T+20.

## Mathematical consistency

If the original reference price is S0, the current observed price is St, and the target endpoint is SH:

Original-horizon return = (St / S0) × (SH / St) − 1.

The already-realized portion is known.

The remaining return distribution must be forecast.

Do not mistake the realized portion of the original return for predictive skill.

## Required comparison

At every update checkpoint, compare against:

1. Original frozen forecast.
2. Current price with zero expected remaining return.
3. Current price plus historical remaining-horizon distribution.
4. Current price plus raw-IV remaining-horizon distribution.
5. Current price plus GJR remaining-horizon distribution.
6. A fully refitted statistical forecast.
7. An incrementally updated forecast.

Use identical target dates and information cutoffs.

Prediction becoming easier as the endpoint approaches does not establish that an update algorithm adds information.

The update must outperform appropriate same-time, same-remaining-horizon controls.

Deliver `V15_FIXED_ENDPOINT_FORECASTING.md`.

---

# PHASE 3 — MEASURE THE VALUE OF NEW INFORMATION

Develop a systematic method for determining which new market observations improve forecasts.

## Information blocks

Research:

- NIFTY price movements.
- Official equal-weight breadth.
- Financial-sector rotation.
- Defensive/cyclical rotation.
- Market concentration.
- Sector synchronization.
- Implied volatility.
- Option-surface changes.
- Futures basis.
- ETF activity.
- Historical realized volatility.
- Intraday market structure.
- Global-market movements.
- Currency and commodity changes.

## Experimental design

For every historical update origin, generate:

### Model A: No new information

Retain the earlier predictive distribution.

### Model B: Price update only

Account for the newly realized market return and reduced remaining horizon.

### Model C: Price plus updated risk

Include new implied or realized volatility information.

### Model D: Price, risk and domestic market internals

Include updated breadth, rotation and structural information.

### Model E: Complete eligible information

Include all justified newly available inputs.

Compare incremental changes between adjacent models.

Where information blocks are correlated, investigate alternative addition orders and matched ablations.

Do not interpret predictive attribution as causal economic attribution.

## Research questions

- Does fresh breadth improve a forecast after the latest NIFTY return is already known?
- Does the new option surface improve risk estimates beyond the older surface?
- Do global-market observations contribute information before domestic prices absorb them?
- Does financial-sector rotation explain useful forecast revisions?
- Are some feature updates merely noise?

Measure incremental Brier, CRPS, volatility loss, range loss and barrier calibration.

Deliver `V15_INCREMENTAL_INFORMATION_VALUE.md`.

---

# PHASE 4 — FORECAST REVISION INTELLIGENCE

Study how forecast changes relate to new information.

## Revision targets

Measure changes in:

- Probability of an up finish.
- Expected endpoint.
- Median endpoint.
- Predictive volatility.
- Distribution width.
- Upper-tail risk.
- Lower-tail risk.
- Expected remaining range.
- Barrier-touch probabilities.

Investigate both the magnitude and direction of forecast revisions.

## Candidate approaches

Compare:

- Complete model refitting.
- Incremental Bayesian updating.
- State-space filtering.
- Kalman-style parameter updating.
- Regularized residual corrections.
- Fixed-weight forecast revisions.
- Uncertainty-dependent shrinkage.
- Historical innovation-based updating.

Test whether revisions are excessive, insufficient or appropriately calibrated.

## Forecast coherence through time

For a fixed future target variable, correctly specified conditional expectations should have no systematically predictable revision given earlier information.

Investigate whether forecast revisions are associated with previously available variables.

Treat these as diagnostic tests, not proof of a correctly specified model.

Do not impose a zero-drift price martingale merely because conditional forecasts of a fixed target should satisfy consistency properties.

Deliver `V15_FORECAST_REVISION_MODELS.md`.

---

# PHASE 5 — INFORMATION TIMING AND MARKET SESSION STRUCTURE

Our historical market universe contains information generated at different times.

Investigate whether precisely controlling information arrival reveals relationships that daily-close feature matrices conceal.

## Historical decision checkpoints

Where authentic data permits, reconstruct forecasts at:

- Before the Indian market opens.
- After the opening period.
- Mid-session.
- Near the Indian close.
- After the completed Indian session.

Predefine exact IST cutoff times.

Account for:

- US trading sessions.
- Asian-market sessions.
- European-market sessions.
- Currency and commodity trading.
- Indian market holidays.
- Foreign holidays.
- Daylight-saving changes.
- Source publication delays.

## Candidate research questions

1. Does the offshore market explain the next Indian opening gap?
2. Does opening breadth improve the forecast after the gap is observed?
3. Does early financial-sector leadership predict subsequent Indian market behavior?
4. Does late-session participation improve the next-day or weekly forecast?
5. Does a new option snapshot improve the forecast beyond previously available option prices?

Only use data authentically available at the specified cutoff.

End-of-day option archives must not enter intraday forecasts.

If historical receipt times or synchronized snapshots are unavailable, use conservative delays or classify the experiment as diagnostic-only.

## Target separation

For intraday research, distinguish:

- Remaining same-session return.
- Next-session opening gap.
- Next-session close.
- Remaining five-session endpoint.
- Remaining 21-session endpoint.

Do not replace the primary weekly and monthly objectives with whichever intraday target performs best retrospectively.

Deliver `V15_INFORMATION_TIMING_AND_SESSIONS.md`.

---

# PHASE 6 — DISTINGUISH SHOCKS FROM PERSISTENT MARKET CHANGES

A large market movement may represent:

- A temporary price shock.
- A persistent change in expected returns.
- A volatility transition.
- A structural change in sector leadership.
- A repricing of uncertainty.
- Ordinary movement within the previous forecast distribution.

Investigate whether these cases can be differentiated using available information.

## Candidate inputs

- Return surprise relative to the previous predictive law.
- Implied-volatility surprise.
- Sector-rotation surprise.
- Breadth surprise.
- Unexpected global-relative performance.
- Opening-gap magnitude.
- Intraday reversal.
- Changes in market concentration.
- Volatility term-structure changes.
- Persistence of consecutive directional movements.

## Candidate methods

- Standardized predictive residuals.
- Causal change-point detection.
- Regularized state-space models.
- Sequential volatility estimation.
- Strongly regularized shock/persistence mixtures.
- Historical conditional response analysis.

Do not assume a large standardized residual represents a permanent market change.

## Required evaluation

Determine whether the detected shock improves forecasts of:

- Remaining endpoint return.
- Future volatility.
- Future range.
- Directional continuation.
- Reversal.
- Barrier touches.

Compare against simple rules that ignore the shock or update only volatility.

Deliver `V15_SHOCK_VERSUS_PERSISTENCE.md`.

---

# PHASE 7 — CONDITIONAL MARKET-PATH UPDATING

Extend V14's coherent OHLC path framework.

A market path already issued at T0 contains assumptions about possible future prices.

As new observations arrive, investigate whether that distribution can be updated.

## Candidate A: Restart the forecast

Generate a new distribution from the current observed price and market state.

## Candidate B: Condition the original paths

Condition or reweight the previously generated paths based on observed developments.

Investigate whether particle depletion or a lack of suitable paths makes this unreliable.

## Candidate C: Hybrid path updating

Combine information from the original predictive law with newly generated conditional paths.

## Candidate D: Volatility-state updating

Update the implied-volatility and GARCH states while preserving an appropriate conditional path model.

## Candidate E: Historical analogue updating

Identify historical paths that resemble the observed initial portion of the forecast horizon.

Require adequate analogue diversity.

## Mathematical requirements

For the original forecast window:

- Completed highs and lows are known.
- The realized range cannot shrink.
- A barrier that has already been touched remains touched.
- First-passage events already resolved cannot become unresolved.
- Future path uncertainty applies only to the remaining sessions.

The updated law must incorporate both observed and simulated path segments consistently.

Generate endpoint, volatility, range, excursions, drawdown and touch probabilities from the same joint path ensemble.

Evaluate conditional path forecasts against simple restarted diffusion and IV-scaled historical paths.

Deliver `V15_CONDITIONAL_PATH_UPDATING.md`.

---

# PHASE 8 — DEEP VOLATILITY EXPANSION RESEARCH

Raw implied volatility produced substantial point improvements for forecasting volatility expansion in V14.

Investigate this discovery independently from the more difficult direction problem.

## Research objectives

Forecast:

- Probability of volatility expanding by 25%.
- Probability of volatility expanding by 50%.
- Probability of volatility contracting by 20%.
- Entry into a high-volatility state.
- Persistence of high volatility.
- Magnitude of future volatility change.

Retain the exact V14 definitions for reproducibility.

Additional thresholds must be registered before evaluation.

## Strong benchmarks

Include:

- Historical transition frequencies.
- Trailing volatility.
- Volatility persistence.
- Raw implied volatility.
- India VIX.
- GJR-GARCH.
- EGARCH.
- Fixed IV/RV variance mixtures.

## New hypotheses

Investigate whether expansion forecasts improve through:

- Changes in implied volatility.
- Implied versus expected realized variance.
- Recent volatility surprises.
- Breadth deterioration.
- Sector synchronization.
- Intraday semivariance.
- Volatility term structure.
- Global volatility shocks.

Use matched comparisons against raw IV.

Investigate the relative value of the IV level and its change.

Avoid introducing complexity unless it adds measurable information.

Evaluate Brier, log loss, calibration, volatility MAE and variance QLIKE separately.

Deliver `V15_VOLATILITY_EXPANSION_INTELLIGENCE.md`.

---

# PHASE 9 — LEARN FROM FORECAST ERRORS WITHOUT LEAKAGE

V14 archived 712 severe-error case records.

Use those records to investigate recurring weaknesses.

## Error families

Study:

- Underestimated volatility.
- Overestimated volatility.
- Unexpected upside movements.
- Unexpected downside movements.
- Underestimated ranges.
- Overestimated ranges.
- Directional overconfidence.
- Upper-tail misses.
- Lower-tail misses.
- Failed barrier predictions.

## Research approach

Develop causal diagnostics based on:

- Recently resolved forecast errors.
- Distribution of standardized residuals.
- Model disagreement.
- Historical analogue availability.
- Feature-distribution shifts.
- Parameter instability.
- Volatility-model disagreement.
- Implied versus realized risk divergence.

A five-session forecast error becomes available only after its five-session endpoint resolves.

A 21-session error becomes available only after its 21-session endpoint resolves.

Intermediate price observations may be used to update a forecast, but the unresolved final loss must remain unavailable.

## Important qualification

V14's range-miss warning models failed against historical frequency controls.

Do not assume error-prediction models will succeed.

Test whether simpler uncertainty shrinkage or scenario reporting is more defensible.

Deliver `V15_CAUSAL_FORECAST_ERROR_LEARNING.md`.

---

# PHASE 10 — EXTREME MOVEMENT AND SCENARIO INTELLIGENCE

Our historical data contains too few independent extreme monthly episodes to support reliable estimation of detailed rare-event probabilities.

Do not abandon extreme-risk research.

Instead, distinguish probabilistic forecasting from scenario analysis.

## Probabilistic research

Investigate:

- Empirical tail frequencies.
- Student-t innovations.
- Asymmetric historical innovations.
- Conservative tail mixtures.
- Training-only distribution recalibration.
- Episode-weighted tail estimation.

Evaluate proper scores and calibration.

## Scenario research

Construct transparent market scenarios representing:

- Sustained upside momentum.
- Sustained downside momentum.
- Sudden volatility expansion.
- Large opening gaps.
- Broad-market reversals.
- Sector concentration breakdowns.
- Persistent high volatility.
- Unexpected global shocks.

Scenarios may be constructed from authentic historical episodes or explicitly stated hypothetical assumptions.

Do not assign precise occurrence probabilities unless the available evidence supports them.

## Scenario validation

Investigate whether the scenario set captures the characteristics of historical severe-error cases.

Keep scenarios separate from the calibrated central predictive distribution.

A stress scenario is not a 95th or 99th percentile forecast unless that probability has been justified.

Deliver `V15_EXTREME_RISK_AND_SCENARIO_INTELLIGENCE.md`.

---

# PHASE 11 — FIRST-PASSAGE AND TIME-TO-EVENT FORECASTING

Expand the previous barrier research into sequential event forecasting.

Investigate:

- Probability of touching a level during the remaining horizon.
- Time until the first touch.
- Probability of touching the opposite barrier after an initial hit.
- Probability of reaching progressively more distant levels.
- Probability of no additional barrier events.
- Conditional continuation after a large movement.

## Required controls

Compare:

- Unconditional historical event frequencies.
- Historical conditional event frequencies.
- Constant-IV diffusion.
- GJR path simulations.
- Trend-conditioned paths.
- Sequentially updated path distributions.

## Evaluation

Research appropriate survival and time-to-event methods.

Distinguish:

- Unconditional event probability.
- Probability conditional on survival without a previous hit.
- Time to touch conditional on a hit.
- Censoring at the forecast endpoint.
- Ambiguous first-hit ordering.

When daily OHLC does not reveal ordering, preserve the ambiguity.

Evaluate remaining-horizon predictions only on appropriate eligible risk sets.

Do not manufacture skill by scoring already-resolved barrier events as uncertain future predictions.

Deliver `V15_SEQUENTIAL_FIRST_PASSAGE.md`.

---

# PHASE 12 — RETURN TO THE ORIGINAL DIRECTIONAL FORECASTING OBJECTIVE

Do not allow the risk-forecasting work to replace our original goal of predicting weekly and monthly NIFTY returns.

Investigate whether sequential information improves directional forecasts.

## Mandatory reference systems

- V8 residualized rotation.
- V11 official-breadth models.
- V12 risk-rescaled phase-zero model.
- V13 IV-scaled all-phase mixture.
- V14 weekly probability-shrinkage model.
- V14 domestic location plus GJR dispersion.
- Neutral and historical distribution controls.

## Candidate research systems

- Updated sector-rotation models.
- Updated official-breadth models.
- Volatility-normalized return models.
- Fixed-endpoint probability models.
- Sequentially updated structural mixtures.
- Conditional sign-and-magnitude laws.
- Strongly regularized drift estimates.
- Updated path-derived endpoint distributions.

## Attribution requirements

Determine whether any directional improvement arises from:

1. The already-realized price movement.
2. A shorter remaining horizon.
3. Better estimated return location.
4. Better estimated return dispersion.
5. Better asymmetry estimation.
6. Probability shrinkage.
7. Genuinely incremental market information.

Only the last four mechanisms involving new estimation or information should be investigated as potential modeling improvements; elapsed time and realized price movement require matched controls.

Report original five-session and 21-session performance separately from sequential-update performance.

Deliver `V15_DIRECTIONAL_FORECAST_DISCOVERY.md`.

---

# PHASE 13 — EXPLORE ADDITIONAL MARKET INFORMATION

Continue using our full Upstox, NSE and global-market data universe.

Do not assume previously unsuccessful sources are fundamentally useless.

Investigate substantially different information roles.

## Domestic information

- Authentic equal-weight breadth.
- Financial-sector leadership.
- Cross-sector intraday synchronization.
- Index and ETF divergence.
- Changes in liquidity.
- Cash versus futures disagreement.

## Derivatives information

- Newly available implied volatility.
- Changes in skew and curvature.
- Option-surface revisions.
- Same-contract futures changes.
- Unsigned positioning concentration.
- Straddle and term-structure movements.

## Global information

- Offshore market shocks.
- Global volatility changes.
- Foreign sector leadership.
- Currency and commodity movements.
- Global versus domestic breadth.
- Changes in cross-market synchronization.

Investigate whether these sources help estimate forecast revisions, future risk or conditional scenarios rather than forcing every source into a directional model.

Every new source requires a documented availability audit and matched parent comparison.

Deliver `V15_ADDITIONAL_MARKET_INFORMATION.md`.

---

# PHASE 14 — IMPROVE EVIDENCE QUALITY THROUGH EPISODE-LEVEL EVALUATION

Our historical rolling forecasts are strongly dependent.

The combined chronology contains:

- 265 weekly origins and 53 non-overlapping windows.
- 217 monthly origins and 11 non-overlapping windows.

Sequential forecasting will create even more predictions per original target window.

These additional updates must not be counted as independent market outcomes.

## Required evaluation units

Report results at:

- Individual forecast origin.
- Forecast-update checkpoint.
- Original forecast window.
- Fixed endpoint.
- Disjoint outcome window.
- Distinct market episode.

## Dependence controls

Investigate:

- Target-date-grouped comparisons.
- Episode-weighted scores.
- Dependence-aware block resampling.
- Disjoint-window phases.
- Clustered loss comparisons.
- Leave-event-out diagnostics.
- Leave-month-out diagnostics.

Use common support when comparing different update methods.

Do not treat multiple forecasts for the same endpoint as independent observations.

## Extreme-event research

Report the actual number of distinct extreme episodes.

Where episode counts are insufficient for reliable inference, withhold precise confidence claims.

Deliver `V15_EPISODE_LEVEL_EVALUATION.md`.

---

# PHASE 15 — EXPERIMENTAL FORECASTING ARCHITECTURE

Build a research-only architecture that integrates successful mechanisms without requiring every mechanism to reside in one model.

Investigate the following layers.

## Layer 1: Market-state estimation

Construct causal representations of:

- Market direction.
- Breadth.
- Sector rotation.
- Financial leadership.
- Volatility.
- Liquidity.
- Global risk.

## Layer 2: Endpoint forecasting

Produce complete weekly and monthly return distributions using the strongest justified models.

## Layer 3: Volatility forecasting

Evaluate separate short- and long-horizon volatility mechanisms.

Preserve raw IV and GJR-GARCH as strong references.

## Layer 4: Conditional path forecasting

Generate coherent distributions for highs, lows, ranges, drawdowns and barriers.

## Layer 5: Information updating

Revise forecasts as eligible new observations arrive.

## Layer 6: Scenario analysis

Describe important plausible outcomes that may not be adequately represented by the central predictive law.

## Layer 7: Evidence and uncertainty

Report:

- Historical performance.
- Forecast calibration.
- Data quality.
- Model limitations.
- Current information cutoff.
- Uncertainty about model applicability.

The architecture is a research hypothesis.

Every component must earn its inclusion through appropriate comparisons.

Standalone models must remain separately labeled when they do not form a coherent joint law.

Deliver `V15_EXPERIMENTAL_FORECAST_ARCHITECTURE.md`.

---

# PHASE 16 — VALIDATION AND FALSIFICATION

Preserve all established safeguards:

- Chronological walk-forward estimation.
- Matured-label enforcement.
- Point-in-time source alignment.
- Training-only transformations.
- Purging and embargoes.
- Exact-copy invariance.
- Matched-origin comparisons.
- Dependence-aware uncertainty.
- Complete experiment accounting.
- Future-information sentinel tests.

## New sequential controls

Investigate:

- Frozen forecasts.
- Price-only updates.
- Volatility-only updates.
- Delayed information.
- Randomized information revisions.
- Shifted market-state inputs.
- Simulated noise updates.
- Restarted forecasts.
- Historical analogue controls.

Verify that artificial future observations cannot change an earlier archived forecast.

Test whether forecast revisions improve proper scores beyond their same-time controls.

Register initial experiments, parameter ranges, follow-up criteria and computational budgets.

Preserve adaptive follow-ups as explicitly research-exposed discoveries.

Do not claim V15-only multiple-comparison adjustments eliminate the cumulative selection effects from V1–V15.

Deliver `V15_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 17 — COMPLETE RESEARCH COMPARISON

Maintain separate leaderboards for:

1. Original weekly direction.
2. Original monthly direction.
3. Original weekly return distributions.
4. Original monthly return distributions.
5. Weekly volatility.
6. Monthly volatility.
7. Volatility expansion.
8. Trading-range distributions.
9. Barrier-touch forecasting.
10. First-passage forecasting.
11. Fixed-endpoint forecasts.
12. Sequential forecast updating.
13. Incremental information value.
14. Forecast calibration.

Use matched comparisons with the strongest applicable V1–V14 references.

Report:

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- Volatility MAE.
- Variance QLIKE.
- Quantile loss.
- Interval scores.
- Interval coverage.
- Interval width.
- Appropriate joint-distribution scores.
- Origin counts.
- Distinct endpoint counts.
- Disjoint outcome counts.
- Episode counts.
- Search-adjusted uncertainty.

Do not collapse all research objectives into one arbitrary ranking score.

Deliver `V15_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 18 — PRESERVE AND EVALUATE FORWARD RESEARCH FORECASTS

Separately refresh completed 2026 market observations available at execution time.

Do not modify the original November 17 data vintage.

Locate previously issued V4 and V5 experimental forecasts and their immutable issue records.

Resolve forecasts only when their actual target sessions have completed and authoritative outcomes are available.

Do not substitute new predictions for previously issued predictions.

Report genuine forward observations separately from reconstructed historical forecasts.

If producing new V15 experimental forecasts:

- Freeze the model specifications.
- Record exact issue timestamps.
- Archive source observations.
- Preserve original predictive distributions.
- Record subsequent updates separately.
- Maintain the same fixed target date.
- Record revisions and their causes.
- Score all issued forecasts, including unsuccessful ones.

Continue retrospective experimentation in parallel.

Forward tracking is an additional research activity, not a requirement to stop historical discovery.

Do not extend targets beyond the agreed 2025–2026 scope without authorization.

Deliver `V15_FORWARD_RESEARCH_LEDGER.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V15_REPRODUCTION_AND_BASELINES.md`
2. `V15_FIXED_ENDPOINT_FORECASTING.md`
3. `V15_INCREMENTAL_INFORMATION_VALUE.md`
4. `V15_FORECAST_REVISION_MODELS.md`
5. `V15_INFORMATION_TIMING_AND_SESSIONS.md`
6. `V15_SHOCK_VERSUS_PERSISTENCE.md`
7. `V15_CONDITIONAL_PATH_UPDATING.md`
8. `V15_VOLATILITY_EXPANSION_INTELLIGENCE.md`
9. `V15_CAUSAL_FORECAST_ERROR_LEARNING.md`
10. `V15_EXTREME_RISK_AND_SCENARIO_INTELLIGENCE.md`
11. `V15_SEQUENTIAL_FIRST_PASSAGE.md`
12. `V15_DIRECTIONAL_FORECAST_DISCOVERY.md`
13. `V15_ADDITIONAL_MARKET_INFORMATION.md`
14. `V15_EPISODE_LEVEL_EVALUATION.md`
15. `V15_EXPERIMENTAL_FORECAST_ARCHITECTURE.md`
16. `V15_VALIDATION_AND_FALSIFICATION.md`
17. `V15_COMPLETE_MODEL_COMPARISON.md`
18. `V15_FORWARD_RESEARCH_LEDGER.md`
19. `V15_FINAL_RESEARCH_CONCLUSIONS.md`
20. `V15_NEXT_EXPERIMENTS.md`

Preserve reproducible Python code, source hashes, configurations, model parameters, forecast timestamps, original predictive laws, updated laws, information revisions, per-origin scores, failed experiments and verification results.

Keep V1–V14 artifacts unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Establish the new research framework

Reproduce V14.

Implement fixed-endpoint forecasting, same-time controls and episode-level evaluation.

## Wave 2 — Investigate information arrival

Test the incremental value of new price, breadth, rotation, volatility, derivatives and global observations.

## Wave 3 — Develop sequential forecasts

Investigate forecast revisions, conditional path updating, shock persistence and volatility expansion.

## Wave 4 — Improve direction and risk

Test whether sequential market information improves original weekly and monthly forecasting mechanisms.

## Wave 5 — Extreme outcomes

Investigate remaining tail weaknesses, conditional first passage and transparent scenario intelligence.

## Wave 6 — Synthesis

Compare all meaningful results against the strongest existing systems.

Preserve genuine forward observations separately.

Document discoveries, failures and unresolved mechanisms.

Allocate research effort according to productive findings rather than indiscriminately expanding configuration counts.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing research repository, access authenticated historical market data, write Python code, fit statistical and machine-learning models, reconstruct market information, simulate conditional paths and execute feasible experiments.

Do not stop after producing a plan.

Execute the research.

Continue using the complete available 2025–2026 market-data universe.

Explore substantially different methods.

Do not silently import pre-2025 observations or extend beyond 2026.

Do not place trades or deploy capital.

## CENTRAL V15 QUESTIONS

Can we forecast NIFTY more effectively by studying how market expectations evolve?

Which new observations provide genuinely incremental predictive information?

Can a forecast improve intelligently as new sessions complete, beyond the mechanical benefit of observing more of the realized outcome?

Can volatility expansion be predicted more reliably than direction?

Can we distinguish temporary shocks from persistent changes in market behavior?

Can we improve the original five-session and 21-session directional forecasts using these discoveries?

We have completed fourteen substantial research versions.

V15 must investigate the evolving information process behind market forecasting, not merely create another static feature matrix.

Continue researching aggressively.

Challenge existing assumptions.

Preserve negative findings.

Do not manufacture certainty.

**BEGIN V15 RESEARCH.**