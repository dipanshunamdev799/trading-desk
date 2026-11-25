# NIFTY V17 — PRICE DISCOVERY, RESIDUAL RETURN FORECASTING & MARKET MICROSTRUCTURE INTELLIGENCE

## MISSION

You are an autonomous quantitative research scientist with access to our complete trading research infrastructure, Upstox API, NSE archives, Indian equities, global markets, futures, options, ETFs, historical candles, databases and Python execution capabilities.

We have completed V1 through V16 of our NIFTY forecasting research.

V16 produced our strongest historical directional result:

- GIFT NIFTY opening-gap Brier: 0.100841.
- Directional accuracy: 88.71%.
- Opening-gap CRPS: 0.001459.
- Median absolute gap error: 0.1965%.
- Adjusted Brier gain interval: +0.095394 to +0.163392.
- Evaluation: 248 matched historical mornings.

However, the incremental information decayed rapidly beyond the opening gap.

The open-to-close and following-session return experiments demonstrated no meaningful improvement.

This suggests a different research problem:

**Can we identify predictive information about future price movements that is not already reflected in the observable opening price and current market conditions?**

We are deliberately continuing research using 2025–2026 observations.

V17 must investigate price discovery, stock-level information, market microstructure, domestic participation, residual returns and information absorption.

Do not simply repeat V1–V16 with additional hyperparameters.

---

# PRIMARY OBJECTIVES

Retain our original forecasting horizons:

- Next five NIFTY trading sessions.
- Next 21 NIFTY trading sessions.

Additionally investigate:

- Pre-auction opening-gap forecasts.
- Opening-price forecast errors.
- Open-to-close returns.
- Remaining-session returns.
- Future returns after removing the contribution of the initial opening gap.
- Stock-level information transmission.
- Market participation and liquidity.
- Sector-specific price discovery.
- Volatility expansion.
- Future ranges and barrier probabilities.

Determine whether shorter-horizon predictive mechanisms can improve original weekly and monthly forecasts.

## RESTRICTIONS

- Use only 2025–2026 market observations.
- Preserve the original November 17, 2026 historical vintage.
- Acquire additional completed 2026 sessions separately.
- No pre-2025 observations or fitted model states.
- Preserve all V1–V16 artifacts and issued forecasts.
- No live trading, broker orders or capital deployment.
- Previously examined historical results remain research-exposed.

---

# PHASE 1 — REPRODUCE V16 AND ESTABLISH THE REFERENCE SYSTEMS

Read the complete V16 research index, all 18 reports, source code, configurations, availability maps, model artifacts and predictions.

Recover exact implementations from the repository.

## Opening-gap references

| System | Brier |
|---|---:|
| Six-market global factor | 0.233717 |
| V15 offshore model | 0.230235 |
| Simple S&P model | 0.225386 |
| GIFT NIFTY model | 0.100841 |

Reproduce all 248 matched forecasts.

Also reproduce:

- The original 258-morning V15 offshore experiment.
- Pre-auction timing checks.
- Alternative GIFT reference anchors.
- Earlier morning quotes.
- Rollover-screened results.
- Largest-gap exclusion tests.
- Information-decay experiments.
- Regular-session continuation and reversal tests.
- Gap-fill survival forecasts.

## Original weekly and monthly references

- Weekly Brier: 0.228529.
- Weekly CRPS: 0.010457.
- Monthly Brier: 0.245042.
- Monthly CRPS: 0.024694.
- Monthly symmetric Brier: 0.250000.

## Risk and path references

- Weekly volatility MAE: 0.036469 for the V16 offshore/domestic risk model.
- Raw weekly ATM IV MAE: 0.037814.
- Monthly GJR-GARCH volatility MAE: 0.033179.
- Weekly volatility expansion Brier: 0.152707.
- Monthly volatility expansion Brier: 0.172872.
- Weekly GIFT-first barrier Brier: 0.132201.
- Weekly survivor-conditioned barrier Brier: 0.139330.
- Monthly Student-t GJR range CRPS: 0.015422.

Preserve each reference model separately.

Do not combine the best metrics from different systems into one fictional universal forecasting model.

Deliver:

`V17_REPRODUCTION_AND_BASELINES.md`

---

# PHASE 2 — BUILD A ROBUST GIFT NIFTY OPENING-PRICE FORECAST

The opening-gap model is our strongest historical directional candidate.

Investigate its quality deeply without confusing opening-price prediction with post-open return prediction.

## Research A: Strong mechanical baselines

Compare:

1. Raw GIFT overnight return.
2. Basis-adjusted GIFT overnight return.
3. Prior-close anchored GIFT price change.
4. Simple linear mapping from GIFT to the NIFTY opening gap.
5. Historical residual distributions around that mapping.
6. The existing V16 calibrated GIFT forecast.

Determine how much improvement comes from offshore price discovery itself and how much comes from statistical modeling.

## Research B: Forecast timing

Reconstruct forecasts at registered eligible checkpoints, including:

- Previous Indian close.
- After the completed US session.
- 06:00 IST.
- 07:00 IST.
- 08:00 IST.
- 08:30 IST.
- 08:45 IST.
- 08:55 IST.

Use only checkpoints supported by the authentic historical data.

Preserve the distinction between information available at the previous close and information available the following morning.

Audit pre-auction eligibility for each date.

## Research C: Contract and basis quality

Investigate:

- Contract identity.
- Underlying expiry switches.
- Futures basis.
- Roll discontinuities.
- Different reference anchors.
- Trading-hour changes.
- Holiday effects.
- Stale offshore marks.

Prefer dated contracts when available.

Where the vendor alias remains unresolved, maintain explicit uncertainty and conservative rollover sensitivity tests.

## Research D: Gap distribution calibration

Improve forecasts of:

- Direction.
- Expected gap.
- Median gap.
- Gap magnitude.
- Central prediction intervals.
- Large positive and negative gaps.

Use the original 76.61% coverage of the nominal 80% gap interval as a calibration reference.

Test whether better residual estimation improves coverage and proper scores without simply widening the forecast.

Deliver:

`V17_GIFT_OPENING_PRICE_INTELLIGENCE.md`

---

# PHASE 3 — OPENING-PRICE SURPRISE AND RESIDUAL INFORMATION

Introduce a dedicated opening-surprise research framework.

Define:

Opening surprise = Actual opening return − Expected opening return.

The expected opening return must come from a genuinely chronological forecast generated before the relevant opening auction.

Standardize the surprise using uncertainty estimated before the opening outcome.

## Research questions

1. Does opening above the GIFT-implied expectation predict subsequent continuation?

2. Does opening below the expectation predict subsequent reversal?

3. Does the magnitude of the opening surprise affect future volatility?

4. Is the surprise explained by domestic financial-sector leadership?

5. Does an opening surprise accompanied by broad stock participation behave differently from a concentrated opening surprise?

6. Does futures/cash disagreement explain subsequent price behavior?

## Candidate features

- Raw opening surprise.
- Volatility-normalized opening surprise.
- Opening surprise relative to historical residuals.
- Sector-level opening surprises.
- Financial-sector surprise.
- Market-wide opening dispersion.
- Surprise persistence during the first 15–60 minutes.
- Breadth confirmation.

Compare opening surprises against ordinary gap size and direction.

An opening surprise is a statistical residual. It is not automatically proof of mispricing or information that the market has failed to absorb.

Use the actual opening price only for decisions after its availability.

## Required targets

- Subsequent 15-minute return.
- Subsequent 30-minute return.
- Remaining-session return.
- Next-session return.
- Remaining weekly return.
- Remaining monthly return.

Do not score a realized opening surprise as a prediction made before the opening.

Deliver:

`V17_OPENING_SURPRISE_AND_RESIDUAL_RETURNS.md`

---

# PHASE 4 — EXPAND FROM INDEX-LEVEL TO STOCK-LEVEL INTELLIGENCE

We have access to a large Indian-equity universe through Upstox and NSE.

Previous experiments relied heavily on native sector and broad-market indices.

V17 should investigate whether information from individual stocks adds genuinely distinct predictive value.

## Data universe

Investigate authentic historical data covering:

- NIFTY 50 constituents.
- NIFTY 100 constituents.
- NIFTY 200 constituents.
- NIFTY 500 constituents.
- Liquid banking stocks.
- Liquid financial-services stocks.
- IT stocks.
- Energy stocks.
- Auto stocks.
- Consumer stocks.
- Relevant ETFs.

Audit dated historical membership, constituent weights, corporate actions and instrument changes.

Where authentic historical membership is unavailable:

- Use independently defined historically eligible cohorts where possible.
- Keep current-selected stock baskets diagnostic-only.
- Do not claim a current basket represents historical NIFTY membership.

## Candidate market-participation features

Research:

- Advancing versus declining stocks.
- Percentage of stocks outperforming NIFTY.
- Percentage trading above their opening prices.
- Percentage outperforming their sectors.
- Equal-weight stock returns.
- Cross-sectional return dispersion.
- Median stock return.
- Stock-level return asymmetry.
- Breadth acceleration.
- Concentration of positive returns.
- Concentration of negative returns.
- Financial-sector participation.
- Heavyweight versus broader-market participation.

Distinguish actual stock-count breadth from equal-weight index-relative proxies.

## Required comparisons

Compare:

1. Native index features.
2. Official equal-weight breadth.
3. Stock-level breadth.
4. Sector-adjusted stock-level breadth.
5. Financial-sector participation.
6. Combined stock-level and native-index information.

Determine whether individual-equity observations contribute new information or merely reproduce existing indices.

Use date-grouped validation.

Thousands of stocks observed on one date do not constitute thousands of independent future NIFTY outcomes.

Deliver:

`V17_STOCK_LEVEL_MARKET_INTELLIGENCE.md`

---

# PHASE 5 — INTRADAY BREADTH AND PRICE DISCOVERY

Investigate how participation evolves during the Indian trading session.

## Historical checkpoints

Where complete timestamped data supports them, use checkpoints such as:

- 09:25 IST.
- 09:35 IST.
- 09:55 IST.
- 10:20 IST.
- 11:30 IST.
- 12:30 IST.
- 14:00 IST.
- 15:00 IST.

Require completed eligible bars and documented availability allowances.

## Candidate features

- Opening breadth.
- Breadth change since the open.
- Breadth acceleration.
- Percentage of stocks above their intraday VWAP.
- Financial-sector participation.
- Sector leadership transitions.
- Intraday return dispersion.
- Stock-level opening-gap confirmation.
- Participation after large index movements.
- Changes in market-wide synchronization.

VWAP features must use genuine traded-instrument volume. Do not invent spot-index volume.

## Core hypotheses

Investigate whether:

- Broad participation after a positive opening surprise predicts continuation.
- Weak participation during index strength predicts reversal.
- Financial-sector confirmation improves post-open forecasts.
- Rising dispersion indicates weakening market leadership.
- Increasing synchronization predicts volatility expansion.
- Breadth changes provide information beyond the latest NIFTY price movement.

Compare against price-only, volatility-only and native-sector controls.

Do not interpret a statistically attractive subgroup as a reliable forecasting rule without adequate observations and distinct episodes.

Deliver:

`V17_INTRADAY_BREADTH_AND_PARTICIPATION.md`

---

# PHASE 6 — STOCK AND SECTOR LEAD-LAG NETWORKS

Previous global lead-lag experiments primarily examined broad index relationships.

Investigate information transmission within the Indian equity market at higher resolution.

## Candidate relationships

- Large banking stocks to BANK NIFTY.
- Banking stocks to financial services.
- Financial services to NIFTY.
- Large IT stocks to the IT sector.
- Sector leaders to sector followers.
- Heavyweight equities to broader market participation.
- Index futures to cash-market returns.
- ETF prices to underlying index movements.

## Research methods

Investigate:

- Lagged cross-correlations.
- Regularized distributed-lag regression.
- Sparse lead-lag networks.
- Dynamic factor residuals.
- Partial correlations.
- Sector-adjusted return innovations.
- Incremental predictive tests.
- Granger-style predictive tests with appropriate dependence controls.

Use synchronized observations.

Correct for asynchronous trading, stale prices, shared market exposure and overlapping return intervals.

For index constituents, distinguish:

- Mechanical contribution to the index.
- Contemporaneous co-movement.
- Genuine prediction of a later return.

If the same stock movement is already mechanically reflected in the current NIFTY value, do not label that relationship a future predictive signal.

## Evaluation

Test whether network features improve:

- Future NIFTY returns.
- Sector-relative returns.
- Volatility.
- Future ranges.
- Information-decay estimates.
- Five-session and 21-session distributions.

Deliver:

`V17_DOMESTIC_INFORMATION_NETWORKS.md`

---

# PHASE 7 — VOLUME, LIQUIDITY AND ORDER-FLOW INTELLIGENCE

Explore the information available from actual traded instruments.

## Data audit

Investigate authentic historical access to:

- Traded volume.
- Turnover.
- Futures volume.
- Open interest.
- ETF volume.
- Historical bid/ask quotes.
- Trade-level records.
- Market depth.
- Auction data.

Do not assume historical market depth or trade-level order flow is available merely because the live Upstox feed supports it.

## OHLCV-compatible research

Where only historical candles exist, investigate:

- Relative volume.
- Abnormal turnover.
- Volume concentration.
- Return per unit of traded activity.
- Price-volume relationships.
- VWAP deviation.
- Intraday liquidity seasonality.
- Sector-level volume participation.
- Stock-level activity dispersion.
- Amihud-style illiquidity proxies.

Clearly label these as proxies.

## Genuine order-flow research

Only where authenticated historical trade or quote records permit, investigate:

- Signed trade imbalance.
- Bid/ask imbalance.
- Spread.
- Quote changes.
- Depth changes.
- Order-flow persistence.

Do not infer actual buyer/seller initiation, dealer positioning or order-book imbalance from candle volume alone.

## Core question

Does liquidity and trading activity explain future price behavior after controlling for the already-observed price movement?

Test against price-only and volatility-only parents.

Deliver:

`V17_VOLUME_LIQUIDITY_AND_ORDER_FLOW.md`

---

# PHASE 8 — CASH, FUTURES AND ETF PRICE DISAGREEMENT

Investigate whether differences between related instruments contain information about subsequent returns.

## Candidate relationships

- NIFTY futures versus cash index.
- GIFT NIFTY versus domestic NIFTY futures.
- Index ETFs versus their underlying indices.
- Banking ETFs versus banking indices.
- Financial-sector futures versus relevant cash indices.
- Options-implied forward versus actual futures.

## Required adjustments

Account for:

- Contract maturity.
- Futures basis.
- Financing and dividend assumptions.
- Rollover.
- Tracking differences.
- ETF distributions.
- Stale observations.
- Nonsynchronous timestamps.
- Trading spreads where available.

Do not treat every observed price discrepancy as exploitable mispricing.

## Research questions

- Does an unusual cash/futures residual anticipate subsequent cash returns?
- Does a discrepancy resolve through futures movement, cash movement or both?
- Does the relationship depend on liquidity?
- Does cross-instrument disagreement predict volatility?
- Does ETF activity help explain the speed of information absorption?

Compare simple historical basis models against dynamic models.

Evaluate actual incremental predictive information, not merely contemporaneous price correlation.

Deliver:

`V17_CROSS_INSTRUMENT_PRICE_DISCOVERY.md`

---

# PHASE 9 — RESIDUAL RETURN FORECASTING

This is the central V17 modeling task.

Our previous models attempted to predict the entire future NIFTY return.

Investigate whether learning the unexplained component improves estimation.

## Research A: Expected versus residual returns

At each forecast origin, estimate a baseline future return using eligible information.

Then define the historical residual target:

Residual return = Realized future return − Baseline expected return.

The historical baseline prediction must be generated chronologically.

Do not use in-sample fitted residuals as if they were out-of-sample forecast errors.

## Candidate baseline systems

- Neutral expected return.
- Historical expected return.
- GIFT-informed initial-session forecast.
- Domestic rotation forecast.
- Official-breadth forecast.
- Volatility-conditioned forecast.
- V14 structural return model.

## Candidate residual predictors

- Opening surprises.
- Stock-level participation.
- Sector-specific residual returns.
- Relative volume.
- Liquidity changes.
- Cross-instrument disagreement.
- Financial-sector innovations.
- Information-decay measures.

Investigate whether these features explain residual future returns after established baseline information is removed.

## Research B: Orthogonalized feature estimation

Investigate:

- Training-only residualization.
- Partial regression.
- Factor-neutral feature representations.
- Cross-fitted nuisance estimates.
- Regularized residual corrections.

Compare against ordinary direct forecasting.

Any claimed statistical orthogonality must be evaluated on appropriate data and must not be interpreted as evidence of causal identification.

## Research C: Residual distribution forecasting

Produce coherent return distributions using:

- Baseline return location.
- Estimated residual location.
- Conditional volatility.
- Residual asymmetry.
- Historical residual uncertainty.

Evaluate the entire predictive law.

A reduction in point-return error does not automatically imply improved directional probabilities.

Deliver:

`V17_RESIDUAL_RETURN_FORECASTING.md`

---

# PHASE 10 — MULTI-SCALE PREDICTABILITY MAP

Instead of searching indiscriminately across forecasting models, systematically investigate which information sources are useful for which targets.

## Horizons

- Opening gap.
- Next 15 minutes.
- Next 30 minutes.
- Next hour.
- Remaining session.
- Next session.
- Three sessions.
- Five sessions.
- Ten sessions.
- Twenty-one sessions.

## Information families

- Offshore price discovery.
- Global equity direction.
- Official equal-weight breadth.
- Stock-level breadth.
- Financial-sector rotation.
- Sector synchronization.
- Volume and liquidity.
- Futures/cash disagreement.
- Option-implied volatility.
- Option-surface asymmetry.
- Realized volatility.

## Target families

- Direction.
- Expected return.
- Absolute return.
- Volatility.
- Volatility expansion.
- Return distribution.
- Future range.
- Barrier probabilities.

Construct a comprehensive information-source × horizon × target matrix.

Every cell must compare the added information against an appropriate strong parent on identical eligible dates.

Use this matrix to determine where research effort is most productive.

Do not force every information source to predict every target.

Deliver:

`V17_MULTISCALE_PREDICTABILITY_MAP.md`

---

# PHASE 11 — RETURN TO THE ORIGINAL WEEKLY AND MONTHLY OBJECTIVES

Our central long-term objective remains five-session and 21-session NIFTY forecasting.

Do not replace it with opening-gap or intraday forecasting merely because those targets are more predictable.

## Candidate A: Direct forecasting

Preserve the strongest V14–V16 original-horizon systems.

## Candidate B: Predictable component plus residual distribution

Construct a forecast from:

- Estimated initial overnight movement.
- Estimated initial regular-session return.
- Remaining-horizon return distribution.

## Candidate C: Stock-informed structural forecasts

Add validated stock-level participation and liquidity features to strong native and rotation models.

## Candidate D: Residual-corrected historical forecasts

Use the strongest existing distribution as a baseline and estimate whether new information improves its residual errors.

## Candidate E: Multi-task learning

Investigate shared information between:

- Opening gaps.
- Intraday returns.
- Sector returns.
- Weekly returns.
- Monthly returns.
- Volatility transitions.

Use low-dimensional or strongly regularized parameter sharing.

## Critical information restriction

Maintain separate forecast origins for:

1. Previous-session close.
2. Next-morning pre-auction.
3. Post-open.
4. Intraday checkpoints.

A pre-auction forecast has a different information set from a previous-close forecast.

Do not use next-morning GIFT data to improve a forecast purportedly issued at the previous close.

Audit V16's 265-origin GIFT-first path comparison specifically for this distinction.

If the forecast origin differs from the original V14 baseline, reconstruct both systems at the same decision cutoff and report the result separately.

Future intermediate global-market and domestic-market observations must remain unknown when issuing original weekly or monthly forecasts.

Deliver:

`V17_WEEKLY_AND_MONTHLY_FORECASTING.md`

---

# PHASE 12 — VOLATILITY AND PATH INTELLIGENCE

Continue the strongest existing risk-research tracks.

## Preserve benchmarks

- Raw ATM implied volatility.
- V16 offshore/domestic risk model.
- V13 GJR-GARCH.
- V15 fixed IV/RV variance blend.
- V15 Student-t EGARCH.
- V14 Student-t GJR path model.
- V16 GIFT-first path model.

## New hypotheses

Investigate whether:

- Opening surprises predict subsequent volatility.
- Stock-level dispersion improves volatility expansion forecasts.
- Liquidity changes anticipate larger trading ranges.
- Futures/cash disagreement predicts barrier events.
- Domestic participation improves post-opening path forecasts.
- Financial-sector surprises improve asymmetric risk estimates.

## Separate barrier effects

Report:

- Day-one barrier Brier.
- Full-horizon barrier Brier.
- Barrier Brier conditional on surviving day one.
- Subsequent-session first-passage probabilities.

Determine whether improvements extend beyond the already predictable opening movement.

## Simulation quality

Recheck leading V16 256-path systems using larger path counts, such as 2,048 and 8,192, on matched origins.

Use common random numbers where appropriate.

Measure Monte Carlo error separately from forecast uncertainty.

All path-derived quantities must remain coherent.

Deliver:

`V17_VOLATILITY_AND_PATH_INTELLIGENCE.md`

---

# PHASE 13 — DISCOVER ADDITIONAL AUTHENTIC INFORMATION

Continue using the full available Upstox, NSE and global-market universe.

Investigate underused sources where available:

- Dated historical constituent files.
- Exchange corporate-announcement timestamps.
- Scheduled earnings announcements.
- Index rebalancing schedules.
- Historical bulk and block deal information.
- FII/DII activity.
- Cash-market turnover.
- Stock futures.
- Authentic auction records.
- Historical ETF data.
- Historical offshore futures.
- Sector-specific international instruments.

For every source, document:

- Actual availability.
- Historical timestamp quality.
- Coverage.
- Missing observations.
- Revision risk.
- Survivorship exposure.
- Permissible forecast cutoffs.

Distinguish information published before a decision from information only reported afterward.

For corporate announcements, distinguish announcement timing from event timing.

Do not reconstruct unavailable historical expectations using subsequent realized announcements.

Prioritize genuinely new information over repeated transformations of existing indicators.

Deliver:

`V17_NEW_INFORMATION_DISCOVERY.md`

---

# PHASE 14 — AGGRESSIVE FALSIFICATION

V17 must challenge its most promising results.

## Opening-gap controls

- Simple raw-GIFT baseline.
- Basis-adjusted GIFT baseline.
- Previous-session offshore quote.
- Alternative prior anchors.
- Earlier morning observations.
- Strict dated-contract subsets.
- Rollover exclusions.
- Stale-quote exclusions.
- Source-delay sensitivity.
- Largest-gap removal.
- Holiday sensitivity.

## Stock-level controls

- Historical membership audit.
- Corporate-action audit.
- Equal-weight index controls.
- Random eligible stock subsets.
- Sector-neutral controls.
- Feature duplication.
- Block-shifted stock inputs.
- Timestamp perturbations.
- Exclusion of dominant individual stocks.

## Residual forecasting controls

- Direct forecasting.
- Zero residual prediction.
- Historical residual distribution.
- Randomized residual labels.
- Delayed information.
- Block-permuted features.
- Training-period removal.
- Strongest prior reference model.

## Sequential and microstructure controls

- No future bars.
- No current-session official close at earlier cutoffs.
- No end-of-day derivatives records in intraday features.
- No retrospective constituent membership.
- No invented trade initiation.
- No future intermediate returns.

Use future-information sentinel tests.

Any violation must invalidate the affected forecast until corrected and rerun.

Deliver:

`V17_VALIDATION_AND_FALSIFICATION.md`

---

# PHASE 15 — RESEARCH EFFICIENCY AND CUMULATIVE KNOWLEDGE

We have completed sixteen large research versions.

Do not produce another enormous uncontrolled search simply to report larger experiment counts.

## Wave-one registration

Begin with a limited set of materially distinct mechanisms.

For each mechanism, register:

- Hypothesis.
- Target.
- Forecast cutoff.
- Required information.
- Strong parent benchmark.
- Primary metric.
- Eligibility requirements.
- Falsification controls.
- Computational budget.
- Criteria for further exploration.

Expand promising mechanisms only when initial results or diagnostics justify expansion.

When an implementation repeatedly fails against simple strong controls, preserve the failure and redirect resources toward genuinely different hypotheses.

Continue research rather than terminating the overall investigation.

## Cumulative evidence

Update the existing V1–V16 knowledge base.

Distinguish:

- Demonstrated methodological properties.
- Replicated retrospective associations.
- Cohort-dependent improvements.
- Failed implementations.
- Unresolved mechanisms.
- Genuinely new hypotheses.

Do not confuse a large number of reproducible forecasts with a large number of independent outcomes.

Deliver:

`V17_CUMULATIVE_EVIDENCE_AND_RESEARCH_EFFICIENCY.md`

---

# PHASE 16 — MULTI-OBJECTIVE LEADERBOARD

Maintain separate comparisons for:

1. Pre-auction opening-gap forecasting.
2. Opening-gap magnitude.
3. Opening-price surprise.
4. Post-open direction.
5. Remaining-session returns.
6. Gap continuation and reversal.
7. Original five-session direction.
8. Original 21-session direction.
9. Weekly return distributions.
10. Monthly return distributions.
11. Volatility.
12. Volatility expansion.
13. Future ranges.
14. Barrier touches.
15. Survivor-conditioned barrier predictions.
16. Incremental stock-level information.
17. Residual return forecasting.

Use:

- Brier.
- Log loss.
- Accuracy.
- Balanced accuracy.
- CRPS.
- MAE.
- Median absolute error.
- RMSE.
- QLIKE.
- Rank correlation.
- Quantile loss.
- Interval coverage.
- Interval width.
- Calibration.
- Dependence-aware uncertainty.

Preserve the original 265 weekly and 217 monthly comparison cohorts.

For different source eligibility or decision cutoffs, recompute benchmarks on matched observations.

Report disjoint windows and distinct episodes.

Use appropriate date- or episode-grouped dependence controls for intraday observations.

Do not treat multiple bars, stocks or forecast checkpoints as independent NIFTY outcomes.

Deliver:

`V17_COMPLETE_MODEL_COMPARISON.md`

---

# PHASE 17 — PRESERVE AND RESOLVE EXISTING FORWARD FORECASTS

Refresh completed 2026 market observations separately.

The previous V16 refresh occurred at 09:40 IST on November 25, 2026.

Locate:

- V4 late-diagnostic forecasts targeting November 25 and December 17.
- V5 experimental forecasts targeting November 26 and December 18.
- Any subsequently issued genuine research forecasts.

Resolve them only after the actual target sessions have completed and authoritative outcomes are available.

Preserve all original probabilities and distributions.

Do not overwrite an issued forecast using a newly selected model.

If generating new experimental opening-gap forecasts:

- Freeze them before opening-price discovery.
- Preserve exact issue timestamps.
- Archive the eligible GIFT observation.
- Record the applicable vendor instrument and contract information.
- Preserve the complete predictive distribution.
- Resolve using the authoritative opening value.

Maintain separate historical and prospective scoreboards.

Continue retrospective research in parallel.

Do not extend targets beyond the authorized 2026 scope.

Deliver:

`V17_FORWARD_RESEARCH_LEDGER.md`

---

# REQUIRED RESEARCH ARTIFACTS

Produce:

1. `V17_REPRODUCTION_AND_BASELINES.md`
2. `V17_GIFT_OPENING_PRICE_INTELLIGENCE.md`
3. `V17_OPENING_SURPRISE_AND_RESIDUAL_RETURNS.md`
4. `V17_STOCK_LEVEL_MARKET_INTELLIGENCE.md`
5. `V17_INTRADAY_BREADTH_AND_PARTICIPATION.md`
6. `V17_DOMESTIC_INFORMATION_NETWORKS.md`
7. `V17_VOLUME_LIQUIDITY_AND_ORDER_FLOW.md`
8. `V17_CROSS_INSTRUMENT_PRICE_DISCOVERY.md`
9. `V17_RESIDUAL_RETURN_FORECASTING.md`
10. `V17_MULTISCALE_PREDICTABILITY_MAP.md`
11. `V17_WEEKLY_AND_MONTHLY_FORECASTING.md`
12. `V17_VOLATILITY_AND_PATH_INTELLIGENCE.md`
13. `V17_NEW_INFORMATION_DISCOVERY.md`
14. `V17_VALIDATION_AND_FALSIFICATION.md`
15. `V17_CUMULATIVE_EVIDENCE_AND_RESEARCH_EFFICIENCY.md`
16. `V17_COMPLETE_MODEL_COMPARISON.md`
17. `V17_FORWARD_RESEARCH_LEDGER.md`
18. `V17_FINAL_RESEARCH_CONCLUSIONS.md`
19. `V17_NEXT_EXPERIMENTS.md`

Preserve complete reproducible Python code, source hashes, eligibility timestamps, model configurations, predictions, predictive distributions, failed experiments and verification results.

Keep V1–V16 artifacts unchanged.

---

# EXECUTION PRIORITIES

## Wave 1 — Verify and establish the new research problem

Reproduce the GIFT forecast.

Establish mechanical offshore benchmarks.

Audit original forecast cutoffs.

Investigate opening surprises.

## Wave 2 — Discover domestic information

Investigate stock-level participation, intraday breadth, liquidity, volume and cross-instrument relationships.

Prioritize genuinely authentic historical information.

## Wave 3 — Develop residual forecasting

Investigate future return residuals, domestic information networks and unexplained post-opening movements.

Compare against strong simple controls.

## Wave 4 — Integrate with the original objective

Determine whether new stock-level or residual forecasting mechanisms improve five-session and 21-session predictions.

Continue volatility and path research.

## Wave 5 — Challenge and synthesize

Perform rigorous falsification, build the multi-scale predictability map and identify genuinely distinct research candidates.

Preserve all unsuccessful experiments.

---

# FINAL EXECUTION DIRECTIVE

You have permission to inspect the existing repository, retrieve authenticated historical market observations, access available Upstox and NSE data, write Python code, develop statistical and machine-learning models, and execute feasible experiments.

Do not stop at producing a research plan.

Execute the research.

Continue exploiting the complete 2025–2026 market-data universe.

Do not import pre-2025 observations.

Do not silently extend into 2027.

Do not place trades or deploy capital.

## CENTRAL V17 QUESTIONS

We can estimate NIFTY's opening price historically with substantial accuracy using GIFT NIFTY.

But what happens after that information is absorbed?

Can stock-level participation reveal new information?

Can liquidity and volume help forecast genuinely future returns?

Can we identify information transmitted between individual equities and sectors before subsequent index movements?

Can opening-price surprises explain continuation, reversal or volatility?

Can residual forecasting improve our original weekly and monthly predictions?

We have spent sixteen research versions learning how to forecast aggregate market behavior.

V17 must investigate the underlying processes through which market information becomes market prices.

Explore aggressively.

Challenge established assumptions.

Prioritize genuinely distinct mechanisms.

Retain negative findings.

Do not manufacture predictive certainty.

**BEGIN V17 RESEARCH.**