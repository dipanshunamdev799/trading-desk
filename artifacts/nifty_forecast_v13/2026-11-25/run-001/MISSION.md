# NIFTY V13 — VOLATILITY INTELLIGENCE, OPTIONS SURFACE DYNAMICS & MARKET PATH FORECASTING

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global markets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V12 of our NIFTY forecasting research.

V12 unlocked an extensive historical derivatives dataset and produced our strongest new finding concerning future realized volatility.

However, directional forecasting and complete return-distribution improvements remain inconclusive.

**We are deliberately continuing active research using 2025–2026 observations.**

Do not stop experimentation because independent validation is unavailable.

V13 must investigate substantially richer forecasting objectives using our entire available market-data universe.

## PRIMARY OBJECTIVES

For both five-session and 21-session horizons, investigate:

- Directional probability.
- Expected return.
- Median return.
- Realized volatility.
- Absolute return magnitude.
- Probable future trading range.
- Maximum favorable and adverse movements relative to the reference price.
- Probability of touching specified price levels.
- Distribution of future highs and lows.
- Conditional return paths.
- Downside and upside risk.
- Coherent endpoint return distributions.

Keep the original five-session and 21-session endpoint targets intact.

New path and risk targets must be evaluated separately.

Do not confuse endpoint probability with the probability of touching a level before the endpoint.

### Research restrictions

- Use only 2025–2026 observations.
- Preserve the original November 17, 2026 historical vintage.
- Additional completed 2026 sessions may be acquired separately.
- No pre-2025 market observations or fitted states.
- No live trades.
- No broker orders.
- No capital deployment.
- All previously examined history remains research-exposed.

---

# PHASE 1 — REPRODUCE V12 AND ESTABLISH STRONG BENCHMARKS

Read all V12 reports, source code, historical option reconstructions, configurations, forecasts, quality diagnostics and verification artifacts.

Reproduce the exact reference systems.

## Weekly realized-volatility benchmarks

| System | Annualized volatility MAE |
|---|---:|
| Trailing realized volatility | 0.046394 |
| Raw near-expiry ATM implied volatility | 0.037814 |
| Fitted realized-risk model | 0.043246 |
| Fitted IV model | 0.040918 |
| Five-session-delayed IV model | 0.041674 |
| IV plus ETF activity | 0.040642 |
| IV plus synchronized intraday risk | 0.040569 on 263 origins |

## Monthly realized-volatility benchmarks

| System | Annualized volatility MAE |
|---|---:|
| Trailing realized volatility | 0.048044 |
| Bracketed implied volatility | 0.039406 |
| Fitted realized-risk model | 0.040910 |
| Fitted IV model | 0.040178 |
| IV plus synchronized intraday risk | 0.039122 |

Reproduce the strongest probability and distribution references:

- V11 combined weekly Brier: 0.231728.
- V11 combined weekly CRPS: 0.010777.
- V12 combined weekly Brier: 0.229715.
- V12 combined weekly CRPS: 0.010677.
- V11 later-weekly Brier: 0.156795.
- V11 later-weekly CRPS: 0.009262.
- Monthly symmetric Brier: 0.250000.
- Monthly symmetric CRPS: 0.025420.

Recover exact model IDs and configurations from the repository.

Do not infer implementations from descriptive names.

Verify target definitions, trading-session conventions, annualization factors, source delays and matched-origin eligibility.

In particular, investigate whether differences between calendar-time option maturities and trading-session realized volatility affect the comparison.

Preserve all V1–V12 artifacts.

Deliver `V13_REPRODUCTION_AND_BENCHMARKS.md`.

---

# PHASE 2 — MAKE VOLATILITY FORECASTING A MAJOR RESEARCH TRACK

V12's raw ATM implied-volatility measure substantially outperformed trailing realized volatility.

It also outperformed several more complex fitted models.

Our first objective is to understand why.

## 2.1 Benchmark traditional volatility models

Research:

- Historical rolling volatility.
- Exponentially weighted volatility.
- Parkinson volatility.
- Garman–Klass volatility.
- Rogers–Satchell volatility.
- Yang–Zhang volatility.
- ARCH and GARCH.
- EGARCH.
- GJR-GARCH.
- HAR volatility models.
- Regularized volatility regression.
- Realized-volatility models using valid intraday data.

Compare estimators using consistent future volatility targets.

Where estimators measure different quantities, document the distinction.

Daily close-to-close volatility, intraday realized volatility and overnight risk are not interchangeable.

## 2.2 Market-implied volatility models

Research:

- Raw ATM implied volatility.
- Expiry-aligned implied volatility.
- Bracketed total implied variance.
- Term-structure-adjusted IV.
- Call-side and put-side IV.
- Volatility skew.
- Volatility curvature.
- Implied volatility changes.
- Model-free implied variance where strike coverage permits.
- India VIX and authenticated volatility-index histories.

Use both raw implied measures and simple training-only calibration.

Treat raw IV as a mandatory strong benchmark.

A fitted model that beats trailing realized volatility but fails to beat raw IV has not established incremental forecasting value.

## 2.3 Hybrid volatility forecasts

Compare:

- Implied volatility alone.
- Realized volatility alone.
- Fixed IV/RV mixtures.
- HAR models with implied volatility.
- Conditional location-scale models.
- Volatility-conditioned empirical distributions.
- Regime-conditioned IV adjustments.
- Strongly regularized dynamic mixtures.

Investigate whether model complexity adds value beyond simple fixed combinations.

## 2.4 Evaluation

Measure:

- Volatility MAE.
- RMSE.
- QLIKE on consistently defined variance forecasts.
- Forecast bias.
- Rank correlation.
- Calibration by volatility bucket.
- Performance during volatility expansions.
- Performance during volatility contractions.
- Earlier-versus-later cohort stability.
- Matched improvement over raw IV.

Do not compare QLIKE calculated on variance with QLIKE calculated on standard deviation as though they were equivalent.

Deliver `V13_ADVANCED_VOLATILITY_RESEARCH.md`.

---

# PHASE 3 — LEARN FROM THE ENTIRE HISTORICAL OPTIONS SURFACE

V12 reconstructed a substantial number of historical option-implied distributions.

V13 should investigate how these surfaces evolve through time.

## 3.1 Surface representation

Construct compact, interpretable features describing:

- ATM volatility.
- Downside skew.
- Upside skew.
- Smile curvature.
- Term-structure slope.
- Term-structure curvature.
- Near-expiry versus longer-expiry volatility.
- Implied downside-tail mass.
- Implied upside-tail mass.
- Risk-neutral distribution asymmetry.
- Risk-neutral quantiles.

Use forward-relative moneyness and consistent maturity conventions.

Do not compare changing strike positions as if they represented identical economic exposures.

## 3.2 Surface dynamics

Research:

- One-session surface changes.
- Five-session surface changes.
- Skew acceleration.
- Volatility term-structure transitions.
- Sudden downside repricing.
- Volatility compression and expansion.
- Changes in implied asymmetry.
- Changes in implied tail probabilities.
- Persistence of surface shapes.

Investigate whether surface changes contain more useful information than absolute surface levels.

## 3.3 Low-dimensional options factors

Research whether multiple surface characteristics can be represented by a small number of factors.

Potential approaches:

- Economically defined level, slope and curvature factors.
- Training-only PCA.
- Functional principal components.
- Regularized surface-factor regression.
- Dynamic factor models.
- Compact parametric surface representations.

Compare sophisticated approaches against simple ATM IV, skew and term-structure summaries.

Preserve exact-copy invariance where applicable.

## 3.4 Expiry and contract controls

Account for:

- Changing time to expiration.
- Contract rolls.
- Weekly and monthly expiration differences.
- Exchange holidays.
- Strike availability.
- Zero-volume contracts.
- Stale marks.
- Settlement-price differences.
- Nonsynchronous observations.

Do not assume changes around an expiry represent changes in market expectations without controlling for mechanical maturity effects.

Deliver `V13_OPTIONS_SURFACE_DYNAMICS.md`.

---

# PHASE 4 — VOLATILITY RISK PREMIUM AND EXPECTATION ERRORS

Research whether differences between market-priced risk and statistically expected risk contain predictive information.

## Candidate measurements

- Implied variance minus causally forecast realized variance.
- Ratio of implied to statistically expected volatility.
- Downside versus upside volatility pricing.
- Term-structure disagreement.
- Implied versus historical return asymmetry.
- Market-implied versus statistical tail risk.
- Changes in these differences.

Distinguish an ex-ante estimated variance risk premium from the ex-post difference between implied variance and subsequently realized variance.

Future realized variance must never enter an input available at the forecast origin.

## Research questions

1. Does unusually expensive implied risk predict future volatility contraction?

2. Does relatively inexpensive implied risk precede volatility expansion?

3. Does downside-risk pricing add information beyond ATM IV?

4. Does the relationship depend on financial-sector rotation or broad-market breadth?

5. Are risk-pricing differences more useful for magnitude than direction?

6. Does a combination of realized-risk forecasts and market-priced risk outperform either source alone?

## Physical distribution estimation

Investigate strongly regularized methods for mapping risk-neutral distributions into candidate physical return distributions.

Potential methods:

- Location adjustments.
- Scale adjustments.
- Exponential tilting.
- Asymmetric probability adjustments.
- Empirical risk-premium corrections.
- Fixed mixtures of market-implied and statistical distributions.

Use only previously matured outcomes for calibration.

Do not interpret an option-implied risk-neutral distribution as the actual conditional probability law of future returns.

Deliver `V13_RISK_PREMIUM_AND_EXPECTATIONS.md`.

---

# PHASE 5 — FORECAST THE FUTURE MARKET RANGE

This is a major new research objective.

Previous research concentrated on where NIFTY would finish after five or 21 sessions.

Investigate how far NIFTY may travel during those sessions.

## Define new targets

Using reference close S0 and the subsequent H complete sessions, define:

### Maximum upward movement

U(H) = maximum future high / S0 − 1

### Maximum downward movement

D(H) = minimum future low / S0 − 1

### Future trading range

Range(H) = (maximum future high − minimum future low) / S0

### Close-based excursion

Construct separate maximum and minimum future close-relative returns.

Do not conflate daily high/low excursions with close-based excursions.

### Additional targets

- Maximum peak-to-trough drawdown.
- Maximum rebound.
- Future absolute endpoint return.
- Realized variance.
- Number of positive sessions.
- Largest individual daily movement.
- Overnight versus regular-session movement.

Keep reference-relative adverse movement distinct from peak-to-trough drawdown.

## Candidate inputs

Research:

- ATM implied volatility.
- Historical range estimators.
- Option-implied quantiles.
- Volatility skew.
- Term structure.
- Intraday volatility.
- Sector dispersion.
- Financial rotation.
- Equal-weight breadth.
- Futures positioning.
- ETF activity.
- Global risk conditions.

## Candidate methods

- Quantile regression.
- Regularized range regression.
- Conditional empirical range distributions.
- Volatility-scaled historical ranges.
- Distributional regression.
- Historical path analogues.
- Simple diffusion-based benchmarks.

Compare predicted range distributions against unconditional historical distributions and volatility-scaled historical controls.

Evaluate quantile loss, interval calibration, MAE and tail behavior.

A predicted endpoint quantile must not be relabeled as a likely maximum or minimum during the forecast horizon.

Deliver `V13_FUTURE_RANGE_FORECASTING.md`.

---

# PHASE 6 — FIRST-PASSAGE AND PRICE-LEVEL PROBABILITY FORECASTING

Investigate the probability of NIFTY touching specified price levels before the forecast horizon expires.

## Research targets

For both weekly and monthly horizons, evaluate probabilities of reaching:

- +0.5%.
- +1%.
- +2%.
- +3%.
- +5%.
- −0.5%.
- −1%.
- −2%.
- −3%.
- −5%.

Also investigate volatility-scaled barriers established at the forecast origin.

These thresholds are research targets, not trading recommendations or stop-loss rules.

## Distinguish these events

- Finishing above a specified price.
- Touching a price at any point.
- Closing above a price during any target session.
- Touching an upper barrier before a lower barrier.
- Touching both barriers.
- Touching neither barrier.

These are mathematically different events.

Where both barriers are reached during the same daily candle and the ordering cannot be established, mark the order as ambiguous.

Use genuine intraday data to resolve ordering only when complete and sufficiently granular observations support it.

Never invent an intrabar sequence.

## Research methods

Compare:

- Historical event frequencies.
- Volatility-conditioned historical frequencies.
- Regularized binary probability models.
- Conditional historical path simulation.
- Diffusion-based first-passage benchmarks.
- State-dependent path models.
- Option-informed volatility-path models.

Evaluate Brier, log loss, calibration and coverage across the entire registered barrier family.

Barrier probabilities should satisfy appropriate monotonicity conditions.

For example, the probability of reaching +5% must not exceed the probability of reaching +2% over the same horizon.

Deliver `V13_FIRST_PASSAGE_AND_BARRIER_PROBABILITIES.md`.

---

# PHASE 7 — BUILD COHERENT MARKET PATH MODELS

Previous research tested basic daily AR models and historical block simulation.

V13 should investigate improved path models informed by actual option prices and domestic market structure.

## Candidate A: Historical path resampling

Sample historical contiguous paths using only matured training observations.

Preserve dependence between daily returns, volatility and excursions.

Research conditional scaling using current implied volatility.

## Candidate B: Implied-volatility-scaled paths

Use an estimated physical volatility forecast derived from market-implied information.

Combine it with standardized historical return innovations.

Investigate whether this improves endpoint, range and barrier calibration.

## Candidate C: State-dependent volatility dynamics

Research simple models with:

- Conditional drift.
- Time-varying volatility.
- Asymmetric return shocks.
- Volatility clustering.
- Regime transitions.

Keep model complexity consistent with available observations.

## Candidate D: Domestic structure and market-priced risk

Investigate whether:

- Financial rotation informs return location.
- Equal-weight breadth informs directional asymmetry.
- Options prices inform conditional scale.
- Intraday volatility informs path dynamics.
- Global risk informs volatility transitions.

Treat these as competing hypotheses, not fixed architecture assumptions.

## Candidate E: Joint OHLC path models

Where reliable data supports it, investigate historical block representations containing:

- Overnight gaps.
- Open-to-close returns.
- Intraday high-relative excursions.
- Intraday low-relative excursions.

Preserve valid OHLC relationships.

A daily close-only simulation cannot directly establish intraday barrier probabilities without additional assumptions.

## Coherence requirements

For any system presented as one joint path forecast, derive the following from the same simulated path ensemble:

- Endpoint distribution.
- Expected endpoint return.
- Endpoint up probability.
- Future high and low distributions.
- Realized volatility.
- Price-level touch probabilities.
- Drawdown distribution.

Keep standalone forecasts separately labeled when they do not arise from a joint law.

Simulated paths are not additional observed market outcomes.

Quantify simulation error separately from statistical estimation uncertainty.

Deliver `V13_COHERENT_MARKET_PATH_MODELS.md`.

---

# PHASE 8 — CROSS-MARKET VOLATILITY TRANSMISSION

Previous global-market inputs frequently failed to improve NIFTY direction forecasts.

Investigate whether they are more useful for forecasting risk.

## Research universe

Use authenticated available data covering:

- US VIX.
- India VIX.
- Nasdaq volatility.
- US equity-market volatility.
- Asian-market volatility.
- USD/INR volatility.
- Crude-oil volatility.
- Gold volatility.
- Interest-rate changes.
- Global equity dispersion.
- Global market synchronization.

Do not assume all requested volatility series exist.

Where direct volatility measures are unavailable, use clearly labeled realized-volatility proxies.

## Research questions

- Do global volatility shocks precede Indian volatility expansion?
- Does foreign volatility improve Indian risk forecasts beyond domestic IV?
- Do currency and commodity shocks modify NIFTY downside risk?
- Does global risk become more informative when domestic breadth deteriorates?
- Are volatility spillovers stronger at weekly or monthly horizons?

## Required comparisons

- Domestic realized risk.
- Domestic implied risk.
- Global risk alone.
- Domestic plus global risk.
- Global/domestic volatility divergence.
- Global-risk-conditioned path distributions.

Use exact cross-market session alignment and conservative publication delays.

Compare every global addition against raw domestic IV as well as its immediate parent.

Deliver `V13_GLOBAL_VOLATILITY_TRANSMISSION.md`.

---

# PHASE 9 — OPTIONS POSITIONING AND STRIKE-LEVEL STRUCTURE

Continue extracting information from the historical derivatives universe.

Research:

- Strike-wise OI concentration.
- OI changes.
- Call/put positioning asymmetry.
- Concentration near the forward price.
- Volume relative to OI.
- Changes in positioning across expiries.
- Distance between major OI concentrations and the current forward.
- Changes in concentration during volatility expansion.
- Relationships between option prices, OI and traded volume.

## Important restrictions

Open interest alone does not reveal whether dealers are net long or short.

Do not infer dealer gamma exposure, market-maker inventories or directional positioning without authenticated supporting information.

If estimating gamma-weighted OI or similar quantities, label them as unsigned exposure proxies and state all assumptions.

Do not treat high-OI strikes as guaranteed support, resistance or price magnets.

## Research hypotheses

Investigate whether positioning concentrations improve:

- Future range forecasts.
- Barrier-touch probabilities.
- Volatility forecasts.
- Expiry-conditioned behavior.
- Conditional distribution asymmetry.

Compare against price-surface-only models.

Determine whether OI and volume add information beyond the prices themselves.

Deliver `V13_STRIKE_POSITIONING_RESEARCH.md`.

---

# PHASE 10 — EVENT-CONDITIONED RISK FORECASTING

Expand V12's event research, focusing on volatility and path behavior.

Investigate verified events such as:

- Weekly expiration.
- Monthly expiration.
- Futures rollover.
- RBI policy decisions.
- Federal Reserve decisions.
- Scheduled macroeconomic announcements.
- Index rebalancing.
- Major previous-session price shocks.
- Sudden IV changes.
- Extreme sector rotation.

Distinguish events known before the forecast origin from events observed afterward.

For each event family, investigate:

- Future realized volatility.
- Expected absolute movement.
- Future trading range.
- Downside and upside excursions.
- Option-implied risk calibration.
- Barrier-touch probabilities.

Determine whether implied volatility systematically overestimates or underestimates realized risk around particular event types.

Report event counts and disjoint outcomes.

Do not construct narrow subgroups merely to obtain attractive historical results.

Deliver `V13_EVENT_CONDITIONED_RISK.md`.

---

# PHASE 11 — IMPROVE EXISTING DIRECTIONAL FORECASTS THROUGH RISK INFORMATION

Do not abandon the directional research accumulated through V1–V12.

Investigate whether more accurate conditional volatility estimates improve probability forecasts.

## Candidate hypotheses

1. Volatility-normalized return targets improve estimation of directional relationships.

2. Market-implied scale helps calibrate the confidence of existing domestic-rotation forecasts.

3. Financial-sector rotation is more informative under particular implied-volatility conditions.

4. Equal-weight breadth predicts direction differently during volatility expansion and contraction.

5. Option-surface asymmetry contributes incremental information beyond domestic market structure.

## Required systems

Compare:

- V12 phase-zero probability leader.
- All-phase mixtures.
- V11 official-breadth models.
- V8 residualized rotation.
- V10 structural blend.
- V11 and V12 group-balanced ensembles.
- Risk-scaled versions of these systems.
- Volatility-normalized target variants.
- Raw-IV-conditioned variants.
- Options-skew-conditioned variants.

Keep the location and scale effects separate in the experimental attribution.

A scale adjustment may improve Brier without discovering new directional information.

Explain whether improvements arise from better return location, better dispersion, probability shrinkage or some combination.

Deliver `V13_RISK_INFORMED_DIRECTIONAL_MODELS.md`.

---

# PHASE 12 — MONTHLY FORECASTING RESEARCH

Monthly directional forecasting remains unresolved.

Our combined monthly sample contains 217 rolling origins but only 11 disjoint return windows.

V12 nevertheless found encouraging historical results for implied-volatility-based monthly risk forecasting.

Investigate monthly forecasting through separate objectives.

## Track A: Monthly direction

Continue researching:

- Persistent official breadth.
- Financial-sector leadership.
- Risk-premium-conditioned directional models.
- Slowly changing market factors.
- Phase-balanced statistical forecasts.

Retain the monthly symmetric probability of 0.5 as a strong benchmark.

## Track B: Monthly volatility

Investigate:

- Bracketed implied variance.
- Monthly IV term structure.
- HAR-IV models.
- Implied and realized variance mixtures.
- Global volatility transmission.
- Intraday risk aggregation.

## Track C: Monthly path and range

Investigate:

- Expected monthly high-low range.
- Maximum adverse excursion.
- Probability of large movements.
- Conditional path simulation.
- Downside tail estimates.

## Track D: Monthly distribution forecasting

Compare:

- Symmetric historical laws.
- Market-priced scale adjustments.
- Volatility-conditioned empirical laws.
- Risk-neutral-to-physical mappings.
- Coherent market-path distributions.

Keep monthly evidence limitations explicit.

Do not treat improved monthly volatility forecasts as proof of directional predictability.

Deliver `V13_MONTHLY_RISK_AND_RETURN_RESEARCH.md`.

---

# PHASE 13 — HISTORICAL DATA QUALITY AND NEW INFORMATION DISCOVERY

Continue auditing the complete available Upstox and NSE universe.

Prioritize additional data that genuinely supports the new forecasting targets.

Investigate:

- Historical one-minute and five-minute index candles.
- Complete daily OHLC histories.
- Synchronized sector-index candles.
- Intraday ETF data.
- Historical index futures.
- Dated option contracts.
- Historical India VIX.
- Global volatility measures.
- Authentic policy-event calendars.

Verify:

- Exchange sessions.
- Timezones.
- Daylight-saving changes.
- Holidays.
- Missing bars.
- Source revisions.
- OHLC consistency.
- Intraday-versus-daily reference discrepancies.
- Historical availability.

Maintain separate data-quality classifications for primary research and diagnostic-only sources.

Where original publication timestamps are unavailable, use conservative delays and disclose the limitation.

Do not fabricate missing historical observations.

Deliver `V13_DATA_QUALITY_AND_NEW_SOURCES.md`.

---

# PHASE 14 — VALIDATION, FALSIFICATION AND SEARCH RISK

Maintain the established research safeguards:

- Chronological walk-forward fitting.
- Matured-label enforcement.
- Purging and embargoes.
- Training-only preprocessing.
- Historical source availability.
- Exact-copy invariance.
- Matched-origin comparisons.
- Block-bootstrap uncertainty.
- Disjoint-window diagnostics.
- Complete experiment accounting.
- Future-information sentinel tests.

## New volatility controls

Compare:

- Raw implied volatility.
- Delayed implied volatility.
- Trailing realized volatility.
- Standard volatility-persistence models.
- Simple fixed IV/RV blends.
- Shifted option-surface features.
- Block-permuted market-priced risk features.

Determine whether improved risk forecasts depend on current option information or merely persistent volatility conditions.

## New path controls

Compare:

- Unconditional historical paths.
- Volatility-scaled historical paths.
- Simple diffusion models.
- Randomized state-conditioned paths.
- Shuffled or shifted conditioning variables.

Investigate whether complex path models genuinely improve on simple volatility scaling.

## Reconstruction sensitivity

Repeat leading results under reasonable alternatives for:

- Discount-rate assumptions.
- Forward-price estimates.
- Liquidity screens.
- Closing versus settlement marks.
- Strike truncation.
- Smoothing.
- Expiry alignment.
- Historical source delays.

## Search-risk assessment

V1–V12 have already examined a very large number of hypotheses.

Pre-register initial V13 research families, metrics and model-expansion criteria.

Retain adaptive follow-up experimentation but label it appropriately.

Use representative refit-and-reselection null studies where feasible.

Do not claim that V13-only adjustment removes cumulative V1–V13 selection bias.

Deliver `V13_VALIDATION_AND_FALSIFICATION.md`.

---

# PHASE 15 — CREATE A MULTI-OBJECTIVE RESEARCH LEADERBOARD

Use the established weekly and monthly cohorts:

- Earlier weekly: 173 origins.
- Later weekly: 92 origins.
- Combined weekly: 265 origins.
- Earlier monthly: 141 origins.
- Later monthly: 76 origins.
- Combined monthly: 217 origins.

If new target definitions or source requirements change eligibility, report the actual origin count and recompute all relevant benchmarks on identical dates.

Create separate leaderboards for:

1. Weekly directional probability.
2. Weekly endpoint distribution.
3. Weekly realized volatility.
4. Weekly return magnitude.
5. Weekly future range.
6. Weekly barrier probabilities.
7. Monthly directional probability.
8. Monthly endpoint distribution.
9. Monthly realized volatility.
10. Monthly future range and path risk.
11. Cross-cohort stability.
12. Incremental information value.

## Required metrics

For probability forecasts:

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- Calibration.

For return distributions:

- CRPS.
- Quantile loss.
- MAE and RMSE.
- Interval coverage.
- Interval width.
- Tail calibration.

For risk forecasts:

- Volatility MAE.
- Variance QLIKE.
- RMSE.
- Rank correlation.
- Range forecast error.
- Excursion quantile loss.
- Barrier probability calibration.

For all research families:

- Origin count.
- Disjoint-window count.
- Appropriate dependence diagnostics.
- Earlier/later results.
- Matched benchmark improvement.
- Search-adjusted uncertainty.
- Evidence classification.

Do not collapse every forecasting objective into an arbitrary universal ranking score.

Maintain separate research candidates for separate objectives.

Deliver `V13_COMPLETE_MODEL_COMPARISON.md`.

---

# PHASE 16 — BUILD AN EXPERIMENTAL NIFTY FORECAST REPORT

Create a research-only reporting interface demonstrating how the strongest candidate systems could describe future NIFTY behavior.

For each horizon, report:

## Direction

- Probability of an up move.
- Expected return.
- Median return.

## Endpoint distribution

- Central 50% interval.
- Central 80% interval.
- Relevant tail probabilities.

## Volatility

- Market-implied volatility.
- Statistical realized-volatility estimate.
- Hybrid volatility estimate.

## Market path

- Distribution of future highs.
- Distribution of future lows.
- Expected trading range.
- Maximum adverse and favorable movement distributions.
- Price-level touch probabilities.

## Evidence

- Exact model versions.
- Data cutoff.
- Forecast timestamp.
- Historical calibration.
- Known limitations.
- Whether forecasts come from one coherent law or separate models.
- Explicit research-only status.

Do not fabricate current predictions.

If producing a new forward research forecast, freeze it before its target outcomes occur, preserve the complete inputs and configuration, and record it separately from the historical leaderboard.

Do not modify earlier forecast ledgers.

Deliver `V13_EXPERIMENTAL_FORECAST_REPORT.md`.

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V13_REPRODUCTION_AND_BENCHMARKS.md`
2. `V13_ADVANCED_VOLATILITY_RESEARCH.md`
3. `V13_OPTIONS_SURFACE_DYNAMICS.md`
4. `V13_RISK_PREMIUM_AND_EXPECTATIONS.md`
5. `V13_FUTURE_RANGE_FORECASTING.md`
6. `V13_FIRST_PASSAGE_AND_BARRIER_PROBABILITIES.md`
7. `V13_COHERENT_MARKET_PATH_MODELS.md`
8. `V13_GLOBAL_VOLATILITY_TRANSMISSION.md`
9. `V13_STRIKE_POSITIONING_RESEARCH.md`
10. `V13_EVENT_CONDITIONED_RISK.md`
11. `V13_RISK_INFORMED_DIRECTIONAL_MODELS.md`
12. `V13_MONTHLY_RISK_AND_RETURN_RESEARCH.md`
13. `V13_DATA_QUALITY_AND_NEW_SOURCES.md`
14. `V13_VALIDATION_AND_FALSIFICATION.md`
15. `V13_COMPLETE_MODEL_COMPARISON.md`
16. `V13_EXPERIMENTAL_FORECAST_REPORT.md`
17. `V13_FINAL_RESEARCH_CONCLUSIONS.md`
18. `V13_NEXT_EXPERIMENTS.md`

Preserve complete reproducible Python code, model configurations, historical option surfaces, target definitions, simulation parameters, per-origin forecasts, negative controls, failed experiments and verification results.

Keep all V1–V12 files unchanged.

---

# EXECUTION STRATEGY

## Wave 1 — Volatility intelligence

Reproduce V12.

Establish raw implied volatility as a strong benchmark.

Investigate traditional, market-implied and hybrid volatility models.

## Wave 2 — Options surface dynamics

Research skew, curvature, term structure, risk premiums and strike-level positioning.

Determine which information contributes genuinely distinct forecasting value.

## Wave 3 — Market path intelligence

Develop future-range, excursion and barrier probability forecasts.

Compare simple historical path methods against market-informed alternatives.

## Wave 4 — Integration

Investigate whether improved risk estimates enhance directional probabilities, return distributions and joint market-path forecasts.

## Wave 5 — Global and monthly research

Research cross-market volatility transmission, longer-horizon risk and monthly forecasting.

## Wave 6 — Falsification and synthesis

Challenge apparent winners using strong benchmarks, alternative reconstructions, temporal sensitivity and negative controls.

Produce a complete scientific account of what was discovered.

Allocate additional computation to promising new hypotheses rather than repeatedly tuning existing winners.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing research environment, access authenticated historical market data, write Python code, reconstruct option surfaces, fit statistical and machine-learning models, simulate conditional return paths and execute experiments.

Do not stop at creating a research plan.

Execute feasible research using our available infrastructure.

Continue actively exploring 2025–2026 observations.

Do not import pre-2025 observations.

Do not silently extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V13 RESEARCH QUESTIONS

Can we predict how much NIFTY will move more reliably than we can predict its direction?

Can we use the historical options surface to forecast volatility, asymmetry and tail risk?

Can we estimate the probability of NIFTY reaching particular levels during the next week or month?

Can we combine domestic market structure, options pricing, realized risk and global-market behavior into coherent predictive return paths?

Can better risk estimation improve our existing directional forecasting systems?

We have accumulated twelve versions of directional and distributional research.

V13 must expand our understanding of the full future market behavior, rather than merely attempting to reduce historical Brier by another small amount.

Explore aggressively.

Challenge every assumption.

Preserve every important result.

Do not manufacture certainty.

**BEGIN V13 RESEARCH.**