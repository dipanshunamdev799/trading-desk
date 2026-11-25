# NIFTY V14 — EXTREME MOVEMENT INTELLIGENCE, STOCHASTIC VOLATILITY & CALIBRATED MARKET PATHS

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global markets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V13 of our NIFTY forecasting research.

We have investigated hundreds of forecasting configurations, hundreds of thousands of predictions, extensive market relationships, statistical estimation, options-implied distributions, volatility forecasting and conditional market paths.

V13 demonstrated promising historical results for volatility, future trading ranges and price-level touch probabilities.

However, our models continue to underestimate some exceptional market movements, and independent forecasting superiority remains unestablished.

**We are deliberately continuing active research using 2025–2026 observations.**

V14 must investigate a deeper problem:

Can we understand and forecast the dynamics that generate future market movements, including ordinary fluctuations, volatility transitions, persistent trends, sudden shocks and extreme price excursions?

Do not simply repeat previous feature-engineering and model-selection experiments.

## PRIMARY OBJECTIVES

For both five-session and 21-session horizons, investigate:

- Directional probability.
- Expected and median returns.
- Future realized volatility.
- Volatility expansion and contraction.
- Full endpoint return distributions.
- Future trading ranges.
- Maximum upward and downward excursions.
- First-passage probabilities.
- Extreme market movements.
- Conditional tail risk.
- Coherent joint market paths.

Retain the original endpoint forecasting objectives.

Use only 2025–2026 observations.

No live trading, broker orders or capital deployment.

All previously examined historical periods remain research-exposed.

---

# PHASE 1 — REPRODUCE V13 AND ESTABLISH STRONG BENCHMARKS

Read all V13 reports, model configurations, saved paths, historical option surfaces, predictions, experiment registries and verification artifacts.

Recover exact implementations from the repository.

## Weekly volatility benchmarks

| System | Annualized volatility MAE |
|---|---:|
| Trailing realized volatility | 0.046394 |
| Raw ATM implied volatility | 0.037814 |
| Calibrated implied volatility | 0.037517 |
| EGARCH | 0.039975 |
| GJR-GARCH | 0.040318 |
| 75% IV / 25% RV variance mixture | 0.038196 |

Also reproduce raw IV variance QLIKE of 0.276187, calibrated IV QLIKE of 0.338910 and the fixed mixture's QLIKE of 0.273634.

Investigate why calibration improved MAE while worsening QLIKE.

## Monthly volatility benchmarks

| System | Annualized volatility MAE |
|---|---:|
| Trailing realized volatility | 0.048044 |
| Bracketed implied volatility | 0.039406 |
| EGARCH | 0.034943 |
| GJR-GARCH | 0.033179 |

## Market-path benchmarks

| Target | Historical baseline | Diffusion benchmark |
|---|---:|---:|
| Weekly range CRPS | 0.007918 | 0.005793 |
| Weekly range MAE | 0.010385 | 0.008182 |
| Monthly range CRPS | 0.019522 | 0.016275 |
| Weekly barrier Brier | 0.156019 | 0.144154 |
| Monthly barrier Brier | 0.206812 | 0.184067 |

Preserve the IV-scaled historical-path alternatives as additional strong references.

## Endpoint forecasting benchmarks

- V13 combined weekly Brier: 0.229587.
- V13 combined weekly CRPS: 0.010472.
- V11 later-weekly Brier: 0.156795.
- V11 later-weekly CRPS: 0.009262.
- Monthly symmetric Brier: 0.250000.
- V13 dispersion-adjusted monthly CRPS: 0.025220.

Verify identical target definitions, units, annualization, maturity alignment, historical availability and matched-origin eligibility.

Preserve all V1–V13 artifacts.

Deliver `V14_REPRODUCTION_AND_BENCHMARKS.md`.

---

# PHASE 2 — UNDERSTAND THE DIFFERENCE BETWEEN ORDINARY AND EXTREME MARKET MOVEMENTS

Our models may estimate ordinary market behavior reasonably well while underestimating exceptional movements.

Investigate that possibility systematically.

## Define extreme-movement targets

Research:

- Large positive endpoint returns.
- Large negative endpoint returns.
- Unusually large high-low ranges.
- Large upward excursions.
- Large downward excursions.
- Sudden volatility expansion.
- Persistent directional movements.
- Unusually large overnight gaps.
- Multi-session trend acceleration.
- Extreme realized variance.

Evaluate both fixed percentage thresholds and thresholds normalized using information available at the forecast origin.

Use training-defined quantiles for relative-extreme classifications.

Never calculate thresholds from the evaluation outcomes.

## Research questions

1. Are extreme returns primarily associated with unusually large daily shocks or persistent multi-session directional movements?

2. Does volatility increase before large market movements?

3. Do large movements begin with sector synchronization or financial-sector rotation?

4. Does weakening breadth precede extreme downside behavior?

5. Does strong broad-market participation precede persistent upside behavior?

6. Do option prices recognize future exceptional movements?

7. Do volatility models systematically underestimate transitions from calm to turbulent markets?

8. Does the relationship differ between positive and negative extreme movements?

For every target, report event frequency, number of distinct episodes and disjoint outcome counts.

Do not treat a sequence of overlapping extreme-return labels as multiple independent crises.

Deliver `V14_EXTREME_MOVEMENT_ANATOMY.md`.

---

# PHASE 3 — RESEARCH VOLATILITY TRANSITIONS

Previous research primarily forecast the level of future realized volatility.

V14 should investigate whether changes in volatility are separately predictable.

## Targets

- Future volatility expansion.
- Future volatility contraction.
- Transition into a high-volatility state.
- Transition out of a high-volatility state.
- Speed of volatility changes.
- Persistence of elevated volatility.
- Volatility acceleration.

Define causal regime thresholds using training observations.

## Candidate signals

Research:

- ATM implied volatility changes.
- Implied versus realized variance.
- India VIX changes.
- Volatility term-structure inversion.
- Changes in downside skew.
- Sector volatility dispersion.
- Market-wide return synchronization.
- Financial-sector stress proxies.
- ETF turnover changes.
- Futures positioning.
- Global volatility shocks.
- Currency and commodity volatility.

## Candidate models

- Simple persistence controls.
- Logistic transition models.
- Regularized state-space models.
- Causal regime-transition models.
- Filtered hidden-state models.
- Volatility-conditioned transition matrices.
- Asymmetric GARCH forecasts.
- HAR-IV models.

Do not use retrospectively smoothed volatility states for forecasts issued at historical origins.

Compare every model with simple volatility-persistence and raw-IV controls.

Deliver `V14_VOLATILITY_TRANSITION_MODELS.md`.

---

# PHASE 4 — STOCHASTIC VOLATILITY AND ASYMMETRIC MARKET DYNAMICS

V13 found that weekly raw IV remained a strong benchmark while monthly GJR-GARCH produced better point estimates than bracketed IV.

Investigate whether combining those mechanisms produces useful volatility dynamics.

## Research tracks

### A. Asymmetric GARCH

Investigate:

- GARCH.
- EGARCH.
- GJR-GARCH.
- Gaussian innovations.
- Student-t innovations.
- Skewed innovations where identifiable.

Study asymmetric volatility responses to positive and negative return shocks.

Compare estimated parameter stability across historical periods.

### B. GARCH with market-implied information

Research models incorporating:

- ATM implied variance.
- India VIX.
- Implied volatility term structure.
- Implied versus forecast realized variance.
- Market-implied risk changes.

Test whether implied information improves forecasts of future volatility paths rather than just average horizon volatility.

### C. Multi-scale volatility

Separate:

- Short-term volatility.
- Weekly volatility.
- Monthly volatility.
- Persistent background volatility.
- Temporary volatility shocks.

Investigate HAR-type representations, component volatility models and regularized multi-timescale models.

### D. Stochastic volatility

Where available observations support estimation, investigate:

- Simple latent-volatility state-space models.
- Mean-reverting stochastic volatility.
- Asymmetric return-volatility dependence.
- Low-dimensional regime-switching volatility.

Use strongly constrained parameterizations.

Do not fit complex stochastic volatility models merely because the options archive contains many strikes.

Multiple strikes observed on the same date do not create independent realized-volatility outcomes.

### E. Horizon-dependent risk estimation

Investigate whether one coherent volatility process can reproduce the strong short-horizon IV results and longer-horizon GJR-GARCH results.

Compare against separately estimated weekly and monthly volatility systems.

Account for calendar time, trading sessions, overnight gaps and holidays.

Deliver `V14_STOCHASTIC_AND_ASYMMETRIC_VOLATILITY.md`.

---

# PHASE 5 — SEPARATE CONTINUOUS MOVEMENTS FROM PRICE JUMPS

A standard diffusion model may underestimate extreme paths because market prices do not always evolve through small, continuous changes.

Investigate whether incorporating discrete shocks improves forecasts.

## Historical jump analysis

Use the validated one-minute and five-minute NIFTY data where available.

Research:

- Overnight gaps.
- Large intraday returns.
- Sudden price discontinuities.
- Volatility clustering.
- Concentrated intraday movements.
- Changes in intraday volatility structure.

Investigate realized variance, bipower variation and other defensible jump-sensitive measures.

Account for market microstructure noise, irregular observations and session boundaries.

Compare jump diagnostics across one-minute and five-minute sampling frequencies.

Do not assume every large sampled return is a statistically identifiable jump.

## Candidate path models

Compare:

1. Standard diffusion.
2. Heavy-tailed diffusion innovations or discrete heavy-tailed return models.
3. Historical innovation resampling.
4. Jump-diffusion.
5. Separate overnight-gap models.
6. Asymmetric volatility paths.
7. Regime-dependent shock mixtures.

Start with simple empirical estimates and strongly regularized parameters.

Estimate jump frequency and magnitude using matured training observations only.

Do not overfit rare historical shocks.

Use extreme-value models only when the available tail sample supports credible estimation; otherwise report the limitation and use simpler empirical or shrinkage methods.

Deliver `V14_JUMPS_AND_DISCONTINUOUS_MOVEMENTS.md`.

---

# PHASE 6 — RESEARCH PERSISTENT DIRECTIONAL MOVEMENTS

V13's October 15 monthly reconstruction substantially underestimated the realized upside movement.

Investigate whether exceptional returns arise from repeated directional continuation rather than a single large jump.

## Research topics

- Multi-session momentum persistence.
- Return-sign persistence.
- Consecutive positive or negative sessions.
- Trend acceleration.
- Market breadth persistence.
- Financial-sector leadership persistence.
- Sector synchronization.
- Trend reversals.
- Asymmetry between rising and falling markets.

## Candidate approaches

- Regularized autoregressive models.
- Trend-conditioned empirical paths.
- Causal directional-state transition models.
- Historical block resampling.
- Persistent drift models with strong shrinkage.
- Regime-conditioned return innovations.

Compare against zero-drift and simple historical-drift benchmarks.

Do not fit a persistent bullish regime merely because it explains the October 15 example.

Treat that example as one diagnostic case within the complete evaluation chronology.

Test whether the proposed mechanism improves forecasts across earlier and later periods.

Deliver `V14_TREND_PERSISTENCE_AND_PATH_DIRECTION.md`.

---

# PHASE 7 — OPTIONS-IMPLIED TAIL INTELLIGENCE

Use the historical options surface reconstructed in V12 and V13.

Investigate whether options prices contain information about future extreme movements beyond ATM volatility.

## Research inputs

- Downside implied volatility.
- Upside implied volatility.
- Skew slope.
- Smile curvature.
- Risk-neutral tail probabilities.
- Risk-neutral quantile spreads.
- Constant-maturity surface changes.
- Short-term versus longer-term skew.
- Extreme strike repricing.
- Traded option volume.
- Unsigned OI concentration.

## Research questions

1. Does downside skew improve prediction of large negative excursions?

2. Does upside option repricing contain information about persistent rallies?

3. Does surface curvature improve future range forecasts?

4. Does implied tail pricing predict the frequency of extreme realized returns?

5. Does short-term skew contain information about near-term volatility transitions?

6. Are extreme option prices primarily responding to existing volatility rather than anticipating future movements?

## Required controls

Compare with:

- ATM implied volatility alone.
- Historical volatility.
- GJR-GARCH.
- Historical tail frequencies.
- IV-scaled historical distributions.
- Delayed options surfaces.
- Shifted or block-permuted surface inputs.

Use alternative strike truncation and liquidity filters.

Do not infer unsupported tail probabilities from illiquid or unobserved strikes.

Risk-neutral distributions are not physical return distributions.

Deliver `V14_OPTIONS_TAIL_INTELLIGENCE.md`.

---

# PHASE 8 — INTRADAY MARKET STRUCTURE AND VOLATILITY INFORMATION

V13 obtained hundreds of validated complete intraday sessions.

Investigate whether those observations can improve estimates of future daily and multi-session risk.

## Candidate information

- Opening gaps.
- First-hour realized volatility.
- Midday volatility.
- Closing-hour realized volatility.
- Intraday directional persistence.
- Intraday reversals.
- Relative upper and lower excursions.
- Intraday variance concentration.
- Positive and negative realized semivariance.
- Overnight versus regular-session volatility.
- Cross-sector intraday synchronization.
- Sector leadership changes.

Investigate whether the composition of daily volatility matters for future risk.

For example, two days may have similar close-to-close volatility but very different overnight and intraday behavior.

## Research methods

- HAR models using validated realized-volatility inputs.
- Realized-GARCH approaches where feasible.
- Intraday volatility-profile estimation.
- Separate overnight and regular-session models.
- Regularized cross-sector volatility factors.
- Intraday-conditioned historical path resampling.

Use only complete historical sessions and observations available at each forecast cutoff.

The official daily close remains the endpoint reference.

Do not manufacture missing bars.

Deliver `V14_INTRADAY_VOLATILITY_STRUCTURE.md`.

---

# PHASE 9 — BUILD BETTER JOINT MARKET PATHS

V13 generated 512 OHLC paths per forecast using historical resampling and diffusion methods.

V14 should investigate improved generative representations of market behavior.

## Candidate A: Strong simple benchmark

Constant-volatility diffusion using raw or causally calibrated implied volatility.

## Candidate B: Asymmetric GARCH paths

Simulate return paths with causally initialized, evolving conditional volatility.

## Candidate C: Hybrid IV-GARCH paths

Use market-implied information to estimate near-term risk while permitting statistical volatility dynamics to evolve throughout the horizon.

## Candidate D: Heavy-tailed paths

Replace Gaussian return innovations with regularized Student-t or historical standardized innovations.

## Candidate E: Gap and jump paths

Model overnight gaps and intraday shocks separately.

## Candidate F: Regime-transition paths

Permit future volatility and directional states to evolve probabilistically.

Never provide actual future market states to the simulation.

## Candidate G: Empirical OHLC block paths

Resample historical blocks preserving relationships among:

- Opening gaps.
- Intraday returns.
- Daily high and low excursions.
- Volatility.
- Return asymmetry.
- Consecutive directional movements.

## Candidate H: Coherent path mixtures

Combine complete path-generating mechanisms using fixed or strongly regularized training-only weights.

## Simulation requirements

Investigate Monte Carlo convergence at increasing path counts, such as:

- 512.
- 2,048.
- 8,192.

Use common random numbers where appropriate for stable matched comparisons.

Evaluate simulation error separately from model uncertainty.

Test discretization sensitivity rather than assuming 24 simulated steps per session are sufficient for barrier estimation.

Where mathematically appropriate, investigate Brownian-bridge corrections for within-step barrier crossings.

Bridge corrections for continuous paths must not be applied blindly across overnight jumps.

## Joint coherence

Every path model must derive the following from the same generated paths:

- Endpoint return distribution.
- Expected and median endpoint returns.
- Directional probability.
- Future maximum high.
- Future minimum low.
- Trading range.
- Realized volatility.
- Drawdown.
- Rebound.
- Upper and lower barrier probabilities.
- First-passage ordering where identifiable.

Enforce all mathematical and OHLC consistency constraints.

Deliver `V14_ADVANCED_JOINT_PATH_MODELS.md`.

---

# PHASE 10 — FIX PREDICTION INTERVAL UNDERCOVERAGE

This is one of the highest-priority V14 objectives.

V13 produced the following nominal-80% range interval coverage:

- Weekly diffusion: 71.7%.
- Weekly IV-scaled historical paths: 76.6%.
- Monthly diffusion: 59.9%.
- Monthly IV-scaled historical paths: 69.6%.

The narrow intervals produced by some models miss too many realized outcomes.

Investigate whether calibration can improve coverage without making forecasts excessively wide.

## Candidate methods

- Training-only volatility-scale calibration.
- Empirical residual-quantile adjustments.
- Volatility-conditioned interval calibration.
- Asymmetric upper and lower quantile adjustments.
- Regularized distribution recalibration.
- Rolling calibration using matured outcomes.
- Time-series conformal-style calibration with dependence-aware safeguards.
- Mixtures with historical tail distributions.

Do not claim standard distribution-free conformal coverage guarantees when exchangeability or other required assumptions are violated.

For standalone interval adjustments, explicitly state if the intervals no longer arise from the original predictive law.

For coherent path models, investigate recalibrating or reweighting complete paths rather than independently changing incompatible output quantities.

## Evaluation

Measure:

- 50%, 80%, 90% and 95% interval coverage.
- Interval width.
- Proper interval scores.
- CRPS.
- Quantile loss.
- Upper-tail misses.
- Lower-tail misses.
- Conditional coverage by predicted volatility.
- Coverage during volatility transitions.
- Earlier/later cohort stability.

Do not optimize coverage alone.

An extremely wide interval that always contains the outcome is not necessarily informative.

Deliver `V14_PREDICTIVE_CALIBRATION_AND_INTERVALS.md`.

---

# PHASE 11 — FIRST-PASSAGE AND BARRIER DYNAMICS

Continue the V13 barrier research.

Evaluate:

- ±0.5%.
- ±1%.
- ±2%.
- ±3%.
- ±5%.
- Volatility-scaled barriers.

Investigate whether stochastic volatility, asymmetric innovations, jumps and overnight gaps improve barrier probabilities beyond simple diffusion.

## Additional research targets

- Probability of hitting an upper barrier.
- Probability of hitting a lower barrier.
- Probability of hitting both.
- Probability of hitting neither.
- Upper-first probability.
- Lower-first probability.
- Time until the first touch.
- Probability of a touch within each successive target session.

Distinguish survival beyond a barrier-hitting time from the probability of hitting a barrier before the horizon ends.

Use interval-censored or ambiguous ordering labels where appropriate.

Do not invent event ordering from daily OHLC candles.

## Coherence requirements

- More distant barriers cannot have greater touch probability than nearer barriers on the same side.
- Cumulative touch probabilities cannot decrease as the horizon expands.
- Touch probabilities must be at least as large as corresponding endpoint exceedance probabilities.
- The joint probabilities for both-sided hits, one-sided hits and neither-sided hits must be internally consistent.

Compare directly estimated barrier models with probabilities extracted from complete simulated paths.

Deliver `V14_BARRIER_AND_FIRST_PASSAGE_DYNAMICS.md`.

---

# PHASE 12 — GLOBAL SHOCKS AND CROSS-MARKET RISK TRANSMISSION

Use the broader global-market universe to investigate whether external shocks help predict domestic volatility transitions or extreme movements.

Research available:

- US equity volatility.
- Nasdaq volatility.
- Asian-market volatility.
- Global equity synchronization.
- USD/INR.
- Crude oil.
- Gold.
- US interest rates.
- Global risk dispersion.
- Foreign market overnight movements.

Investigate:

- Global shocks preceding Indian opening gaps.
- Currency shocks preceding domestic volatility expansion.
- Global risk changes interacting with weak Indian breadth.
- Cross-market shocks influencing conditional downside risk.
- Foreign volatility changes beyond information already reflected in India VIX and domestic IV.

Compare against strong domestic-risk parents.

Use exact historical time alignment and conservative publication delays.

Previous global additions frequently failed. A new global model must investigate a distinct mechanism rather than simply append additional features.

Deliver `V14_GLOBAL_SHOCK_TRANSMISSION.md`.

---

# PHASE 13 — RISK-INFORMED DIRECTIONAL FORECASTING

Continue developing the original five-session and 21-session directional forecasts.

Investigate whether improved volatility dynamics and path representations help estimate directional probabilities more accurately.

Research:

- Volatility-normalized targets.
- Asymmetric return distributions.
- Conditional location-scale models.
- Breadth and rotation interactions with risk transitions.
- Sign-and-magnitude laws.
- Drift estimates strongly shrunk toward zero.
- IV-scaled structural return laws.
- GARCH-scaled structural return laws.
- Complete path-derived endpoint distributions.

Preserve the strongest V13 endpoint models.

Separately quantify:

1. Improvements in estimated return location.
2. Improvements in estimated dispersion.
3. Improvements in asymmetry.
4. Improvements caused by probability shrinkage.
5. Improvements caused by tail representation.

A scale adjustment that improves Brier does not necessarily identify additional directional information.

Retain the monthly symmetric forecast as a mandatory benchmark.

Deliver `V14_RISK_INFORMED_ENDPOINT_FORECASTING.md`.

---

# PHASE 14 — DEEP FORENSICS OF FORECAST FAILURES

Instead of studying only the strongest average scores, investigate the most important forecast failures.

## Required analysis

For each leading model, identify:

- Largest Brier losses.
- Largest CRPS losses.
- Largest range underestimates.
- Largest volatility underestimates.
- Unexpected upside moves.
- Unexpected downside moves.
- Failed barrier forecasts.
- Simultaneous failures across multiple systems.

Investigate whether failures are associated with:

- Volatility transitions.
- Price jumps.
- Unexpected trend persistence.
- Global shocks.
- Financial-sector rotation.
- Breadth changes.
- Option-surface repricing.
- Insufficient historical analogues.
- Model estimation uncertainty.

Compare the October 15, 2026 reconstruction with other major historical forecast failures.

Do not tune models exclusively to one unusual episode.

Determine whether potential warning indicators can be computed before the target outcome occurs.

If a failure cannot be anticipated with the available information, report that explicitly.

Deliver `V14_FORECAST_FAILURE_FORENSICS.md`.

---

# PHASE 15 — VALIDATION AND FALSIFICATION

Maintain all existing research safeguards:

- Only 2025–2026 observations.
- Matured labels.
- Chronological fitting.
- Training-only transformations.
- Appropriate purge and embargo.
- Point-in-time source alignment.
- Exact-copy invariance.
- Matched-origin comparisons.
- Dependence-aware uncertainty.
- Complete search accounting.
- Future-information sentinel tests.

## New falsification requirements

For stochastic volatility models:

- Compare against constant-volatility diffusion.
- Test alternative innovation distributions.
- Perturb parameters.
- Test training-window sensitivity.
- Compare against raw IV and GJR-GARCH.

For jump models:

- Compare genuine historical jump features with shifted controls.
- Investigate sampling-frequency sensitivity.
- Remove individual extreme episodes.
- Test whether improved tails merely result from wider distributions.

For calibration:

- Compare with unadjusted laws.
- Test earlier/later stability.
- Report coverage and sharpness jointly.
- Prevent unresolved outcomes from entering calibration.

For path models:

- Check simulation convergence.
- Check barrier monotonicity.
- Check OHLC consistency.
- Check joint probability coherence.
- Compare with IV-scaled historical paths.

Run representative refit-and-reselection null experiments.

Do not claim V14-only search adjustments remove the cumulative selection effects from V1–V14.

Deliver `V14_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 16 — MULTI-OBJECTIVE RESEARCH LEADERBOARD

Use the established historical cohorts:

- Earlier weekly: 173 origins.
- Later weekly: 92 origins.
- Combined weekly: 265 origins.
- Earlier monthly: 141 origins.
- Later monthly: 76 origins.
- Combined monthly: 217 origins.

Where additional target or source requirements change eligibility, recompute every reference on identical origins.

Maintain separate leaderboards for:

1. Weekly directional forecasting.
2. Monthly directional forecasting.
3. Weekly endpoint distributions.
4. Monthly endpoint distributions.
5. Weekly volatility forecasting.
6. Monthly volatility forecasting.
7. Future range forecasting.
8. Extreme-movement probabilities.
9. Barrier-touch forecasting.
10. First-passage forecasting.
11. Prediction interval calibration.
12. Joint market-path quality.
13. Cross-cohort stability.

Use Brier, log loss, CRPS, QLIKE, quantile losses, interval scores, MAE, RMSE, rank correlation, appropriate multivariate scores and calibration measures.

Report disjoint outcome counts and dependence diagnostics.

Maintain a Pareto frontier of forecasting quality, calibration, complexity and stability.

Do not force a universal winner.

Deliver `V14_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 17 — RESEARCH FORECASTING REPORT

Create an experimental NIFTY market-intelligence report containing:

- Directional probabilities.
- Expected and median endpoint returns.
- Endpoint prediction intervals.
- Weekly and monthly volatility forecasts.
- Probability of volatility expansion.
- Expected future range.
- Upper and lower excursion distributions.
- Barrier-touch probabilities.
- Expected time to barrier touch, conditional on a touch when appropriate.
- Extreme-movement probabilities.
- Joint market-path visualizations.
- Model uncertainty.
- Known historical weaknesses.

Clearly identify which outputs arise from one coherent path distribution and which are standalone estimates.

Include historical calibration and benchmark comparisons.

If issuing a new forward experimental forecast, freeze it before any target outcome occurs and archive it separately.

Do not fabricate a current forecast or modify earlier forecast ledgers.

Deliver `V14_EXPERIMENTAL_MARKET_INTELLIGENCE.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V14_REPRODUCTION_AND_BENCHMARKS.md`
2. `V14_EXTREME_MOVEMENT_ANATOMY.md`
3. `V14_VOLATILITY_TRANSITION_MODELS.md`
4. `V14_STOCHASTIC_AND_ASYMMETRIC_VOLATILITY.md`
5. `V14_JUMPS_AND_DISCONTINUOUS_MOVEMENTS.md`
6. `V14_TREND_PERSISTENCE_AND_PATH_DIRECTION.md`
7. `V14_OPTIONS_TAIL_INTELLIGENCE.md`
8. `V14_INTRADAY_VOLATILITY_STRUCTURE.md`
9. `V14_ADVANCED_JOINT_PATH_MODELS.md`
10. `V14_PREDICTIVE_CALIBRATION_AND_INTERVALS.md`
11. `V14_BARRIER_AND_FIRST_PASSAGE_DYNAMICS.md`
12. `V14_GLOBAL_SHOCK_TRANSMISSION.md`
13. `V14_RISK_INFORMED_ENDPOINT_FORECASTING.md`
14. `V14_FORECAST_FAILURE_FORENSICS.md`
15. `V14_VALIDATION_AND_FALSIFICATION.md`
16. `V14_COMPLETE_MODEL_COMPARISON.md`
17. `V14_EXPERIMENTAL_MARKET_INTELLIGENCE.md`
18. `V14_FINAL_RESEARCH_CONCLUSIONS.md`
19. `V14_NEXT_EXPERIMENTS.md`

Preserve all Python code, model parameters, configurations, simulation seeds, per-origin predictive laws, target definitions, source hashes, failed experiments and verification artifacts.

Keep all V1–V13 files unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Understand forecasting failures

Reproduce V13.

Investigate extreme movements, volatility transitions and the limitations of existing diffusion models.

## Wave 2 — Improve market dynamics

Research asymmetric volatility, jumps, overnight gaps, heavy-tailed innovations and persistent directional movements.

## Wave 3 — Exploit additional market intelligence

Investigate options-implied tails, intraday volatility structure and global shock transmission.

## Wave 4 — Build better joint paths

Combine the most promising mechanisms into coherent OHLC path distributions.

## Wave 5 — Improve calibration

Investigate prediction interval undercoverage, tail calibration and barrier probability consistency.

## Wave 6 — Integrate and falsify

Evaluate endpoint, volatility, range, extreme-movement and first-passage forecasting against the strongest historical references.

Allocate additional computation to productive research mechanisms.

Do not exhaust the experiment budget on indiscriminate architecture searches.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing repository, access authenticated historical market sources, write Python code, reconstruct historical option surfaces, fit statistical models, simulate market paths and execute feasible experiments.

Do not stop at producing a research plan.

Continue active research on 2025–2026 observations.

Do not silently extend the data scope.

Do not deploy models or place trades.

## CENTRAL V14 QUESTIONS

Can we predict transitions from ordinary market conditions into unusually volatile conditions?

Can we explain why existing path models underestimate exceptional market movements?

Can market-implied expectations and asymmetric volatility dynamics produce better future return paths?

Can we forecast future ranges and price-level touch probabilities while maintaining reliable calibration?

Can better market-path models improve our original weekly and monthly endpoint forecasts?

We have accumulated thirteen versions of quantitative research.

V14 must investigate the mechanisms that generate market movements, rather than only estimating where the market might finish.

Explore aggressively.

Challenge previous assumptions.

Preserve negative findings.

Never manufacture statistical certainty.

**BEGIN V14 RESEARCH.**