# NIFTY V16 — CROSS-MARKET INFORMATION TRANSMISSION, SESSION DECOMPOSITION & DIRECTIONAL INTELLIGENCE

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global markets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V15 of our NIFTY forecasting research.

We have investigated hundreds of models, thousands of market relationships, alternative statistical methods, options-implied distributions, volatility dynamics, market-path simulations and sequential forecasting.

V15 produced a particularly interesting directional discovery:

Fresh offshore market information improved same-morning NIFTY opening-gap forecasting on 258 matched historical mornings.

- Domestic baseline Brier: 0.265168.
- Offshore-enhanced Brier: 0.227947.
- Domestic baseline CRPS: 0.003241.
- Offshore-enhanced CRPS: 0.002920.
- Earlier-cohort Brier gain: 0.050636.
- Later-cohort Brier gain: 0.024415.
- Family-adjusted gain interval: +0.003563 to +0.070877.

This result is promising but remains research-exposed and subject to historical availability assumptions and cumulative model-selection risk.

Our original weekly and monthly directional forecasting problems remain unresolved.

**We are deliberately continuing active research using 2025–2026 observations.**

V16 must investigate whether decomposing market behavior according to information arrival and trading sessions allows us to extract more predictive intelligence from our extensive market-data universe.

Do not simply repeat the previous fifteen versions with additional hyperparameters.

---

# PRIMARY OBJECTIVES

Retain our original primary forecasting horizons:

- Next five NIFTY trading sessions.
- Next 21 NIFTY trading sessions.

Introduce dedicated auxiliary research objectives:

- Same-morning opening gap.
- Next-session opening gap.
- Overnight return.
- Regular-session return.
- Opening momentum.
- Intraday continuation and reversal.
- Cross-market information transmission.
- Volatility expansion.
- Information absorption.
- Conditional return magnitude.
- Session-aware market paths.

Determine whether these auxiliary forecasting mechanisms can improve the original weekly and monthly forecasts.

## RESTRICTIONS

- Use only 2025–2026 market observations.
- Preserve the original November 17, 2026 historical vintage.
- Acquire additional completed 2026 sessions separately.
- Do not import pre-2025 market data or fitted model states.
- Preserve all V1–V15 research artifacts and issued forecasts.
- No broker orders, live trading or capital deployment.
- All previously examined historical results remain research-exposed.

---

# PHASE 1 — REPRODUCE V15 AND AUDIT THE OPENING-GAP DISCOVERY

This is the highest-priority V16 task.

Read all relevant V15 reports, source scripts, configurations, forecast archives and verification results.

Recover and reproduce the exact offshore opening-gap system.

Do not infer implementation details from the summary.

Reproduce:

- All 258 matched morning forecasts.
- Earlier and later cohort performance.
- The domestic-only parent.
- Offshore-enhanced forecasts.
- The adjusted gain interval.
- The unsuccessful next-session gap experiment.
- Delayed and shifted information controls.
- Exact historical feature-availability rules.

## Critical timing audit

Investigate whether the 09:10 IST forecast cutoff occurs before or during the relevant historical opening-price discovery process.

Verify the historical NSE pre-open schedule and the methodology used to calculate the official NIFTY opening value.

Investigate whether any input directly or indirectly contains:

- Opening auction prices.
- Indicative equilibrium prices.
- Current-session NIFTY prices.
- Current-session constituent opening prices.
- Auction-derived market breadth.
- Other information generated during opening-price discovery.

Reconstruct additional strictly pre-auction forecast cutoffs, such as:

- 08:30 IST.
- 08:45 IST.
- 08:55 IST.

Use only information genuinely available at those times.

Compare these forecasts against the original 09:10 system on identical dates.

For any source without authentic receipt timestamps, apply conservative historical availability assumptions and disclose the resulting limitations.

If the opening-gap advantage disappears before opening-price discovery, report that clearly.

Do not treat an opening price that has already been substantially determined as an unknown future outcome.

Deliver:

`V16_OPENING_GAP_REPRODUCTION_AND_TIMING_AUDIT.md`

---

# PHASE 2 — BUILD A GLOBAL INFORMATION-ARRIVAL MAP

Our market-data universe contains instruments operating across different timezones and trading sessions.

Build a historically valid representation of information availability.

## Candidate information sources

### United States

- S&P 500.
- Nasdaq Composite.
- Nasdaq 100.
- Dow Jones.
- Russell indices.
- VIX.
- Sector indices and ETFs.
- Equal-weight versus cap-weight indices.
- US Treasury yields.

### Europe

- DAX.
- FTSE.
- CAC.
- Euro Stoxx indices.
- Available European sector and volatility measures.

### Asia

- Nikkei.
- TOPIX.
- Hang Seng.
- Shanghai and Shenzhen indices.
- Other available Asian indices.
- Asian market breadth and dispersion.

### India-linked offshore markets

- GIFT NIFTY.
- Authentic historical offshore NIFTY futures, where available.
- Indian equity ADRs.
- International India-focused ETFs.
- USD/INR and other relevant currency measures.

### Commodities

- Brent crude.
- WTI crude.
- Gold.
- Relevant industrial commodities.

These are candidate sources. Do not assume they are all available historically.

## Information-timing requirements

For every source, record:

- Exchange timezone.
- Trading-session schedule.
- Historical observation timestamp.
- Historical publication or receipt timestamp, where available.
- Conservative availability buffer.
- Holiday schedule.
- Daylight-saving transitions.
- Last eligible observation for each Indian forecast cutoff.

Do not align foreign market data using calendar dates alone.

The US session, European session and Asian session may contain different information sets at the same Indian decision time.

Distinguish:

- Previous completed foreign sessions.
- Current partial foreign sessions.
- Overnight futures observations.
- Stale observations.
- Asynchronous market closes.

Do not fabricate historical intraday or offshore observations.

Deliver:

`V16_GLOBAL_INFORMATION_ARRIVAL_MAP.md`

---

# PHASE 3 — DEEP OPENING-GAP FORECASTING RESEARCH

Define the opening-gap target as:

Gap(t) = OfficialOpen(t) / OfficialClose(t−1) − 1

Verify that the official opening value and prior close refer to the correct consecutive NSE trading sessions.

## Forecast objectives

Research:

- Probability of a positive opening gap.
- Expected opening gap.
- Median opening gap.
- Opening-gap magnitude.
- Opening-gap return distribution.
- Probability of large positive or negative gaps.

## Strong baseline models

Include:

1. Neutral probability.
2. Historical gap frequency.
3. Empirical historical gap distribution.
4. Previous domestic return and volatility.
5. Previous US-market return.
6. Simple equal-weight offshore return factor.
7. GIFT NIFTY-implied gap, where authenticated historical quotes exist.
8. V15 offshore-enhanced system.

A complex global model must demonstrate incremental value beyond simple foreign-market returns and GIFT NIFTY where available.

## Candidate global representations

Investigate:

- Foreign equity-market direction.
- Foreign market synchronization.
- Foreign market dispersion.
- Global technology leadership.
- Global financial-sector leadership.
- Currency-adjusted returns.
- Global risk-on/risk-off factors.
- US-to-Asia market continuation.
- US-to-Asia market reversal.
- Global versus Indian relative strength.

## Candidate models

- Regularized linear regression.
- Regularized logistic regression.
- Ridge.
- Cluster-balanced regression.
- Student-t conditional distributions.
- Sign-and-magnitude distributions.
- Shallow nonlinear models.
- Compact cross-market factor models.

Investigate models that estimate direction and magnitude jointly.

Do not optimize solely for classification accuracy.

## Evaluation

Report:

- Brier.
- Log loss.
- Balanced accuracy.
- Directional accuracy.
- CRPS.
- MAE.
- RMSE.
- Calibration.
- Large-gap probability calibration.
- Earlier/later cohort performance.
- Matched benchmark gains.

Daily gaps provide more distinct target observations than overlapping monthly returns, but may still exhibit serial dependence and common event exposure.

Deliver:

`V16_ADVANCED_OPENING_GAP_FORECASTING.md`

---

# PHASE 4 — INVESTIGATE GIFT NIFTY AND OFFSHORE PRICE DISCOVERY

Where authentic historical observations are available, investigate the relationship between offshore India-linked instruments and the next official NIFTY open.

## Candidate questions

- How accurately does offshore NIFTY pricing anticipate the official Indian opening gap?
- Does the broader global market add information beyond offshore NIFTY itself?
- Does offshore NIFTY react differently to US and Asian market developments?
- Does disagreement between offshore pricing and global equities contain incremental information?
- Does unusual offshore movement predict subsequent Indian intraday continuation or reversal?

## Data requirements

Audit:

- Contract identity.
- Contract rollover.
- Trading hours.
- Currency denomination.
- Basis and carry.
- Historical quote timestamps.
- Actual quote availability before each forecast cutoff.

Distinguish offshore futures prices from predicted cash-index levels.

Account for contract basis rather than treating the futures price as the exact expected opening index.

If authentic historical offshore quotes cannot be obtained, document the blocker.

Do not reconstruct historical GIFT NIFTY prices from actual subsequent NIFTY opening values.

Deliver:

`V16_OFFSHORE_PRICE_DISCOVERY.md`

---

# PHASE 5 — SEPARATE OVERNIGHT AND REGULAR-SESSION RETURNS

The daily NIFTY close-to-close return consists of two distinct components.

Using log returns:

Daily return = Overnight return + Regular-session return

Where:

- Overnight return = log(CurrentOpen / PreviousClose).
- Regular-session return = log(CurrentClose / CurrentOpen).

Investigate whether these components respond to different information.

## Research A: Overnight returns

Investigate:

- US market behavior.
- European market behavior.
- Asian market behavior.
- Offshore NIFTY.
- Currency movements.
- Commodity movements.
- Global volatility.
- Previous domestic risk conditions.

## Research B: Regular-session returns

Investigate:

- Domestic opening gap.
- Early-session breadth.
- Financial-sector rotation.
- Opening sector participation.
- Intraday volatility.
- Futures/cash relationships.
- ETF activity.
- Option-surface changes where historically available.

## Research C: Relationship between components

Investigate whether:

1. Large positive opening gaps tend to continue during the regular session.
2. Large negative gaps tend to reverse.
3. Gap continuation depends on financial-sector leadership.
4. Broad domestic participation reinforces offshore information.
5. Narrow participation produces greater reversal risk.
6. Gap magnitude relative to implied volatility modifies subsequent behavior.

These are hypotheses, not established market rules.

Compare against simple continuation and reversal controls.

Deliver:

`V16_OVERNIGHT_AND_INTRADAY_RETURN_DECOMPOSITION.md`

---

# PHASE 6 — GAP ABSORPTION, CONTINUATION AND REVERSAL

Understanding the opening gap is not sufficient.

Research what happens after the market absorbs offshore information.

## Define targets

- Open-to-close return.
- First-hour return.
- Remaining-session return after the first hour.
- Probability of closing in the gap direction.
- Probability of partially retracing the gap.
- Probability of fully retracing the gap.
- Time to gap fill, conditional on a fill.
- Subsequent one-, three- and five-session returns.

Distinguish gap filling from intraday reversal and endpoint direction.

## Candidate features

- Gap size.
- Gap direction.
- Gap relative to expected volatility.
- Offshore market synchronization.
- Opening breadth.
- Banking-sector confirmation.
- Defensive/cyclical participation.
- Intraday volatility concentration.
- Futures confirmation.
- Market-wide dispersion.

## Research methods

- Conditional historical frequencies.
- Regularized probability models.
- Survival and first-passage models.
- Gap-conditioned return distributions.
- Simple state-transition models.
- Matched historical path resampling.

Only use opening and intraday observations after they have become available.

Do not use the opening gap to predict an earlier opening gap.

Do not infer executable profitability from the ability to forecast a gap that occurs before regular cash-market trading.

Deliver:

`V16_GAP_ABSORPTION_AND_REVERSAL.md`

---

# PHASE 7 — CROSS-MARKET INFORMATION NETWORKS

Previous global-feature experiments mostly failed when foreign inputs were appended to weekly directional models.

Investigate a more structured hypothesis:

Different global markets may transmit different information to different parts of the Indian market at different times.

## Candidate relationships

- Nasdaq → Indian IT.
- Global financial-sector performance → Indian financial leadership.
- Crude oil → Indian energy and oil-sensitive sectors.
- USD/INR → IT and export-oriented sectors.
- Global volatility → Indian volatility.
- Asian market synchronization → Indian opening participation.
- US rates → Indian financial-sector and risk conditions.

## Research design

For each relationship:

1. Verify historical timing.
2. Define the intermediate Indian target.
3. Test direct predictive value.
4. Test delayed and shifted controls.
5. Determine whether the intermediate forecast improves NIFTY predictions.
6. Compare against domestic-only and global-only controls.

Investigate whether global information is strongest before the Indian market opens and becomes less useful after domestic prices incorporate it.

Measure predictive associations rather than claiming causal economic transmission.

Deliver:

`V16_CROSS_MARKET_INFORMATION_NETWORKS.md`

---

# PHASE 8 — INVESTIGATE INFORMATION DECAY

Market information may be useful only for a limited amount of time.

Develop a dedicated research framework to estimate this decay.

## Research objectives

Measure the predictive value of fresh offshore information for:

- Same-morning opening gap.
- First-hour return.
- Remaining intraday return.
- Next-session return.
- Three-session return.
- Five-session return.
- Ten-session return.
- Twenty-one-session return.

Use identical information cutoffs within each comparison.

## Experiment

Compare:

- Fresh information.
- One-session-delayed information.
- Two-session-delayed information.
- Five-session-delayed information.
- Smoothed information.
- Block-shifted controls.
- Domestic-only information.

Investigate whether different foreign markets have different predictive lifetimes.

Determine whether the information adds value beyond an already-observed opening gap.

Do not infer that the informational advantage persists for a week simply because it predicts the opening price.

Deliver:

`V16_INFORMATION_DECAY_RESEARCH.md`

---

# PHASE 9 — RESEARCH CROSS-MARKET DISAGREEMENT

Global markets do not always move together.

Investigate whether disagreement among markets provides useful information about the next Indian session.

## Candidate signals

- US strength with Asian weakness.
- Asian strength after US weakness.
- Global equities rising while global volatility rises.
- US technology leadership without financial-sector participation.
- Offshore NIFTY strength relative to global equities.
- Currency weakness despite equity strength.
- Commodity shocks diverging from broad-market direction.

Use training-defined normalized measures rather than arbitrary thresholds selected from evaluation results.

## Forecast targets

- Opening-gap direction.
- Opening-gap magnitude.
- Domestic sector rotation.
- Gap continuation.
- Intraday volatility.
- Future downside risk.
- Five-session return distribution.

Compare simple global averages against disagreement-based representations.

Investigate whether disagreement provides genuinely distinct information or merely increases model complexity.

Deliver:

`V16_CROSS_MARKET_DISAGREEMENT.md`

---

# PHASE 10 — DEVELOP MULTI-SCALE DIRECTIONAL FORECASTING

Our original goal remains forecasting NIFTY over the next week and month.

Investigate whether learning shorter, more interpretable forecasting mechanisms can improve these longer-horizon predictions.

## Candidate A: Direct forecasting

Use existing V14 and other strongest weekly/monthly reference systems.

## Candidate B: First-session decomposition

Forecast:

- Next opening gap.
- Next regular-session return.
- Remaining four-session or 20-session return.

## Candidate C: Session-component simulation

Build a conditional model generating future overnight and intraday return components.

Allow future risk and market states to evolve probabilistically.

## Candidate D: Multi-task learning

Investigate shared representations across:

- Same-morning opening gap.
- Next-session close.
- Three-session return.
- Five-session return.
- Twenty-one-session return.
- Volatility expansion.

## Candidate E: Structural mixtures

Combine complete predictive distributions from:

- Domestic rotation.
- Official breadth.
- Offshore opening-gap intelligence.
- Historical distributions.
- Risk-informed return models.

## Critical restriction

For an original weekly forecast, future offshore observations are unknown.

For an original monthly forecast, future opening gaps are unknown.

Never insert actual future global-market returns, future domestic opens or other realized intermediate observations into an original forecast.

Where necessary, simulate future external information jointly or integrate it out using defensible assumptions.

Evaluate forecasts issued before the original horizon begins.

Keep sequentially updated forecasts separate.

Deliver:

`V16_MULTISCALE_DIRECTIONAL_FORECASTING.md`

---

# PHASE 11 — CONTINUE VOLATILITY INTELLIGENCE

Volatility expansion remains among our strongest research discoveries.

Preserve the V15 point leaders:

## Weekly 25% volatility expansion

- Historical frequency Brier: 0.222296.
- Raw IV: 0.155657.
- Fixed IV/RV blend: 0.152707.

## Monthly 25% volatility expansion

- Historical frequency Brier: 0.299434.
- Raw IV: 0.186036.
- Student-t EGARCH: 0.172872.

## Research questions

- Does offshore volatility improve domestic volatility-expansion forecasts?
- Does a large opening gap alter expected future volatility?
- Are overnight and regular-session volatility driven by different mechanisms?
- Does disagreement among global markets predict volatility expansion?
- Does domestic implied volatility already capture the relevant offshore risk information?

Compare against raw IV, the fixed IV/RV blend, GARCH and EGARCH.

Require incremental value over these strong benchmarks.

Preserve separate MAE, QLIKE, transition-probability and calibration rankings.

Deliver:

`V16_SESSION_AWARE_VOLATILITY_INTELLIGENCE.md`

---

# PHASE 12 — SESSION-AWARE JOINT MARKET PATHS

Extend V14 and V15 path-generation research.

Generate future paths using distinct conditional processes for:

- Overnight gaps.
- Regular-session returns.
- Intraday volatility.
- Financial-sector leadership.
- Global risk.
- Volatility-state evolution.

Compare against:

- Constant-IV diffusion.
- IV-scaled historical paths.
- Student-t GJR paths.
- IV-GJR paths.
- Previous V15 restarted paths.

Derive all joint forecast quantities from the same generated path ensemble:

- Endpoint returns.
- Directional probabilities.
- High and low distributions.
- Future range.
- Realized volatility.
- Barrier-touch probabilities.
- Drawdown.
- First-passage events.

Investigate whether explicitly modeling overnight and regular-session components improves range and tail calibration.

Do not assume a predicted overnight gap automatically produces better multi-session paths.

Deliver:

`V16_SESSION_AWARE_PATH_FORECASTING.md`

---

# PHASE 13 — TEST STRONGER DIRECTIONAL BASELINES

Some previous models may have been compared against insufficiently competitive baselines.

Investigate simple directional systems designed to reveal how much complexity actually contributes.

Include:

- Neutral probability.
- Historical frequency.
- Previous-return momentum.
- Mean reversion.
- Global return factor.
- GIFT NIFTY, if available.
- Domestic financial rotation.
- Official breadth.
- Simple additive global/domestic models.
- Fixed distribution mixtures.

Preserve the original V14 combined weekly benchmarks:

- Brier: 0.228529.
- CRPS: 0.010457.

Preserve monthly benchmarks:

- V14 domestic location/GJR Brier: 0.245042.
- V15 restarted GJR CRPS: 0.024694.
- Symmetric directional probability benchmark: 0.250000 Brier.

Do not select weaker V15 directional references when stronger V14 systems are eligible.

Deliver:

`V16_STRONG_BASELINE_COMPARISON.md`

---

# PHASE 14 — FALSIFICATION AND SEARCH-RISK CONTROL

The cumulative research search across V1–V15 is substantial.

V16 must test whether its new findings survive meaningful challenges.

## Opening-gap falsification

Required tests:

- Earlier pre-auction decision cutoffs.
- Alternative source-availability assumptions.
- Foreign-session timestamp perturbations.
- One-session and multiple-session delays.
- Block-permuted offshore inputs.
- Synthetic noise controls.
- Removal of individual foreign markets.
- GIFT NIFTY-only comparisons.
- Strong simple offshore-factor comparisons.
- Leave-month-out sensitivity.
- Removal of unusually large gap episodes.
- Holidays and nonstandard session checks.

## Weekly and monthly falsification

Required tests:

- No future intermediate observations.
- Matched original forecast horizons.
- Earlier and later cohort comparisons.
- Fully matured labels.
- Training-only transformations.
- Purging and embargoes.
- Exact-copy invariance where applicable.
- Dependence-aware uncertainty.
- Representative refit-and-reselection null experiments.

Do not describe the V15 adjusted interval as independent confirmation.

Do not imply that V16-only statistical adjustment accounts for the entire adaptive V1–V16 research process.

## Experiment discipline

Begin with a limited, registered batch of genuinely distinct mechanisms.

Expand promising tracks only when matched comparisons or diagnostics justify the additional research.

Retain negative and inconclusive results.

Do not manufacture thousands of nearly identical configurations merely to increase the reported experiment count.

Deliver:

`V16_VALIDATION_AND_FALSIFICATION.md`

---

# PHASE 15 — REFRESH AND RESOLVE EXISTING FORECASTS

Separately refresh completed 2026 market sessions.

V15's recorded refresh was at 08:51 IST on November 25, 2026, and reported completed closes through November 23.

Audit the November 24 session status against the authoritative exchange calendar.

Do not infer whether a missing date is a holiday, an unavailable observation or a failed refresh.

Locate previously issued:

- V4 late-diagnostic forecasts targeting November 25 and December 17.
- V5 experimental forecasts targeting November 26 and December 18.
- Any subsequent genuinely issued research forecasts.

Resolve only targets whose sessions have completed and whose authoritative outcomes are available.

Preserve the original issue records and complete predictive distributions.

Do not overwrite predictions with newly fitted models.

If issuing a new V16 opening-gap research forecast, freeze it before the relevant opening-price discovery process, with its exact source availability and configuration recorded.

Keep genuinely prospective observations separate from historical reconstructions.

Continue retrospective research in parallel.

Deliver:

`V16_FORWARD_RESEARCH_LEDGER.md`

---

# PHASE 16 — COMPLETE RESEARCH LEADERBOARD

Maintain separate comparisons for:

1. Same-morning opening-gap direction.
2. Opening-gap magnitude and distribution.
3. Next-session opening gap.
4. Regular-session return.
5. Gap continuation and reversal.
6. One-session direction.
7. Original five-session direction.
8. Original 21-session direction.
9. Weekly return distributions.
10. Monthly return distributions.
11. Volatility expansion.
12. Future range.
13. Barrier-touch probabilities.
14. Session-aware joint paths.

Report actual origin counts, matched eligibility, distinct outcome windows, episode counts, calibration, proper scores, benchmark gains and search-adjusted uncertainty.

Use the strongest relevant V1–V15 controls.

Keep the standard earlier, later and combined weekly/monthly cohorts available for comparison.

Do not force one universal winning model.

Deliver:

`V16_COMPLETE_MODEL_COMPARISON.md`

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V16_OPENING_GAP_REPRODUCTION_AND_TIMING_AUDIT.md`
2. `V16_GLOBAL_INFORMATION_ARRIVAL_MAP.md`
3. `V16_ADVANCED_OPENING_GAP_FORECASTING.md`
4. `V16_OFFSHORE_PRICE_DISCOVERY.md`
5. `V16_OVERNIGHT_AND_INTRADAY_RETURN_DECOMPOSITION.md`
6. `V16_GAP_ABSORPTION_AND_REVERSAL.md`
7. `V16_CROSS_MARKET_INFORMATION_NETWORKS.md`
8. `V16_INFORMATION_DECAY_RESEARCH.md`
9. `V16_CROSS_MARKET_DISAGREEMENT.md`
10. `V16_MULTISCALE_DIRECTIONAL_FORECASTING.md`
11. `V16_SESSION_AWARE_VOLATILITY_INTELLIGENCE.md`
12. `V16_SESSION_AWARE_PATH_FORECASTING.md`
13. `V16_STRONG_BASELINE_COMPARISON.md`
14. `V16_VALIDATION_AND_FALSIFICATION.md`
15. `V16_FORWARD_RESEARCH_LEDGER.md`
16. `V16_COMPLETE_MODEL_COMPARISON.md`
17. `V16_FINAL_RESEARCH_CONCLUSIONS.md`
18. `V16_NEXT_EXPERIMENTS.md`

Preserve reproducible Python code, source hashes, model configurations, information timestamps, experiment registries, per-origin forecasts, complete predictive laws, failed experiments and verification artifacts.

Keep V1–V15 artifacts unchanged.

---

# EXECUTION PRIORITIES

## Wave 1 — Verify the promising discovery

Reproduce the V15 opening-gap result.

Audit pre-open information timing.

Establish strong offshore and domestic baselines.

## Wave 2 — Discover cross-market mechanisms

Investigate GIFT NIFTY where available, global-market information arrival, cross-market relationships and information decay.

## Wave 3 — Understand Indian session behavior

Research overnight returns, opening gaps, domestic absorption, intraday continuation and reversal.

## Wave 4 — Integrate with the original objective

Investigate multi-scale learning and session decomposition for weekly and monthly forecasting.

Continue volatility and market-path research.

## Wave 5 — Challenge the findings

Conduct matched falsification tests, temporal sensitivity analysis, prospective forecast reconciliation and cumulative search-risk assessment.

Allocate additional computation to genuinely productive discoveries.

Avoid repeating unsuccessful previous experiments without a materially different hypothesis.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing repository, retrieve authenticated historical market observations, access available Upstox and global-market sources, write Python code, develop models and execute feasible experiments.

Do not stop at producing a research plan.

Continue actively investigating 2025–2026 market observations.

Do not silently extend the historical scope.

Do not place trades or deploy capital.

## CENTRAL V16 QUESTIONS

Can we predict NIFTY's opening gap before opening-price discovery?

Which foreign markets provide genuinely incremental information?

How quickly does the Indian market absorb offshore information?

Can we predict whether an opening gap will continue or reverse?

Are overnight and regular-session returns generated by different predictive mechanisms?

Can learning these individual mechanisms improve our original weekly and monthly NIFTY forecasts?

We have spent fifteen research versions primarily learning from aggregated market behavior.

V16 must investigate the sequence through which global information reaches the Indian market, influences price discovery and potentially affects subsequent returns.

Be creative.

Challenge previous assumptions.

Execute meaningful experiments.

Preserve scientific integrity.

**BEGIN V16 RESEARCH.**