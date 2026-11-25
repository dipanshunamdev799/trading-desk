# NIFTY V5 — LARGE-SCALE PREDICTIVE SIGNAL DISCOVERY
## Global Markets × Indian Equities × Derivatives × Machine Learning

### MISSION

You are an autonomous quantitative research scientist with access to our trading research environment, Upstox integrations, NSE market data, global-market datasets, historical archives, databases, and Python execution capabilities.

We have completed V1 through V4 of our NIFTY forecasting research.

Our previous experiments did not establish an independently validated predictive edge.

**That does not mean we should stop researching.**

V5 is an ambitious exploratory research program designed to discover predictive information that our previous models may have missed.

We have a large universe of market information. Our previous research concentrated heavily on engineered indicators, basic feature-group weighting, regression, and a limited set of nonlinear models.

I want you to investigate substantially different approaches.

### PRIMARY OBJECTIVE

Discover relationships in the available 2025–2026 market data that improve forecasts of:

1. NIFTY returns over the next **5 trading sessions**.
2. NIFTY returns over the next **21 trading sessions**.

Secondary targets may include volatility, return magnitude, large directional movements, and conditional market behavior.

You may research alternative targets or shorter intermediate horizons when they improve our understanding of the primary problems.

Do not assume the same modeling approach will work for both primary horizons.

### IMPORTANT PHILOSOPHY

- Explore aggressively.
- Test competing hypotheses.
- Use the available data intelligently.
- Write new experimental code.
- Investigate unconventional signal combinations.
- Preserve failed experiments.
- Allow promising exploratory findings to motivate further investigation.
- Never confuse retrospective improvement with independently proven forecasting skill.

We are doing research, not deploying capital.

**Continue experimenting even if no model reaches statistical qualification. Do not manufacture significance or promote an unvalidated model simply to produce a winner.**

---

# PHASE 1 — UNDERSTAND OUR EXISTING SYSTEM

Read the full V1–V4 research history.

Inspect:

- Research reports.
- Feature-engineering pipelines.
- Upstox integrations.
- NSE derivatives archives.
- Market-data ingestion systems.
- Global-market sources.
- Existing database schemas.
- Training and evaluation code.
- Experiment registries.
- Historical prediction records.

Pay particular attention to the V4 findings:

- Weekly LightGBM: 66.30% directional accuracy, Brier 0.226049.
- Weekly residual-shrunk distribution: Brier 0.206257, but inadequate interval coverage.
- Weekly student-shrunk distribution: CRPS 0.010896.
- Weekly LightGBM's advantage disappeared when September was excluded.
- Monthly forecasting remained unstable.
- No adjusted weekly improvement was established.
- No independently validated model exists.

Do not simply repeat these configurations.

Diagnose which information and model families remain underexplored.

Preserve the complete V1–V4 research environment and frozen artifacts.

Create an isolated V5 workspace.

---

# PHASE 2 — DISCOVER THE FULL AVAILABLE DATA UNIVERSE

Do not assume our current 129 features represent everything we can learn.

Audit the actual available historical data.

Explore internal datasets, archived responses, API capabilities, individual securities, indices, historical candles, derivatives, and any connected global-market sources.

## A. Indian market universe

Investigate:

- NIFTY 50 and other broad indices.
- NIFTY 100, 200, 500, and other available indices.
- BANK NIFTY.
- NIFTY FINANCIAL SERVICES.
- Sector indices.
- Midcap and smallcap indices.
- Liquid NSE individual equities.
- Index constituents.
- Equity and index futures.
- Available options archives.
- Market breadth.
- Liquidity and volume information.
- ETFs and related traded instruments.

Do not limit the study to the current 50 NIFTY constituents.

Investigate whether broader participation and sector changes contain information about subsequent index returns.

Use historically valid constituent membership and weights where available. Mark current-membership approximations as survivorship-exposed research features.

## B. Global markets

Audit all accessible global price, derivatives, currency, commodity, bond, and risk datasets.

Potential categories:

**United States**
- S&P 500.
- Nasdaq.
- Dow Jones.
- Russell indices.
- US equity futures.
- VIX.
- Treasury yields.
- US dollar index.
- Sector and technology leadership.

**Europe**
- STOXX indices.
- DAX.
- FTSE.
- CAC.
- Available European futures and risk indicators.

**Asia**
- Nikkei.
- Hang Seng.
- Shanghai Composite.
- CSI indices.
- KOSPI.
- Taiwan indices.
- GIFT NIFTY.

**Cross-asset**
- USD/INR.
- DXY.
- Brent and WTI crude.
- Gold and silver.
- Industrial metals.
- Interest-rate indicators.
- Yield spreads.
- Available credit/risk proxies.

These are candidate data categories, not assertions that every series exists in Upstox.

Use an additional source only when access, provenance, historical timestamps, and collection permissions are verified.

Do not claim unavailable observations exist.

## C. Derivatives intelligence

Investigate historically available:

- NIFTY futures basis.
- Futures OI changes.
- Futures rollover.
- Price/OI relationships.
- Options call/put OI.
- Changes in OI.
- OI concentration.
- Put/call volume ratios.
- Strike positioning.
- Expiry characteristics.
- Available implied-volatility measures.
- Institutional positioning.

Treat contract changes, expiries, lot-size changes, and rollovers correctly.

Do not fabricate historical Greeks or IV surfaces.

## D. Data availability and time alignment

For every data series, record:

- Instrument and source.
- Historical coverage.
- Frequency.
- Number of valid observations.
- Missingness.
- Historical source availability.
- Publication or receipt timing.
- Timestamp timezone.
- Data revisions.
- Whether the series can be used in a historical premarket forecast.

Apply timezone-aware market-session alignment, including daylight-saving changes and different exchange holidays.

A US closing price that had not yet occurred by an Indian forecast cutoff must never enter that forecast.

Differentiate a historical bar timestamp from the actual time its contents became available.

### Deliverable

`V5_DATA_UNIVERSE.md`

Provide a detailed inventory and rank underused data families by availability, distinct information content, and research potential.

---

# PHASE 3 — GLOBAL-TO-NIFTY LEAD/LAG RESEARCH

This is a major new research direction.

Instead of simply adding global-market returns to a machine-learning model, investigate how global-market information relates to future NIFTY returns.

## Research hypotheses

1. Does US technology-sector leadership predict future Indian IT-sector performance?

2. Do changes in US bond yields anticipate shifts in Indian equity-market risk appetite?

3. Does the combination of oil and USD/INR movements contain more information than either variable individually?

4. Does global equity weakness matter differently when Indian market breadth is strong?

5. Do changes in Asian markets anticipate Indian sector rotation?

6. Does Indian market relative strength versus global indices predict continuation or reversal?

7. Do global risk-off shocks produce delayed rather than immediate effects in Indian equities?

8. Do correlations across global markets contain information about future NIFTY volatility or returns?

9. Does the dispersion between US, European, and Asian equity performance signal changing global regimes?

10. Do global-market relationships become stronger or weaker during specific Indian volatility regimes?

These are hypotheses to test, not assumptions.

## Required experiments

Research:

- Cross-market lead/lag relationships.
- Lagged cross-correlations.
- Rolling correlations.
- Relative returns.
- Global risk-factor construction.
- Global market dispersion.
- Global equity/bond/commodity divergence.
- Principal-component and dynamic-factor approaches.
- Changes in cross-asset correlations.
- Regime-dependent relationships.
- Predictive information incremental to Indian market features.

Use methods appropriate for dependent time-series data.

If conducting Granger-style predictive tests, distinguish predictive precedence from actual causation.

Compare global-only, Indian-only, and combined models on matched forecast origins.

**Find out whether global information genuinely improves NIFTY forecasts, rather than simply increasing model dimensionality.**

---

# PHASE 4 — MARKET INTERNALS AND CROSS-SECTIONAL INTELLIGENCE

Research whether information hidden inside individual stocks can forecast broader index behavior.

## Candidate features

- Percentage of stocks in positive trends.
- Distribution of short-term and medium-term momentum.
- Market-wide return dispersion.
- Sector-wise return dispersion.
- New highs versus new lows.
- Breadth acceleration/deceleration.
- Volatility across individual stocks.
- Correlation among major stocks.
- Changes in market concentration.
- Rotation between defensive and cyclical sectors.
- Large-cap versus midcap versus smallcap relative strength.
- Broad-index versus NIFTY divergence.
- Bank and financial-sector participation.
- Sector leadership persistence.
- Sector leadership reversal.

Explore whether these signals predict:

- NIFTY directional returns.
- Market corrections.
- Trend continuation.
- Volatility expansion.
- Large future movements.

## Cross-sectional learning

Investigate an alternative to training only on NIFTY observations.

We have many instruments and potentially many aligned observations.

Research whether models trained across multiple Indian equities or sector indices can learn transferable relationships.

Potential approaches:

- Cross-sectional return prediction.
- Factor models.
- Shared models across securities.
- Hierarchical models.
- Multi-task learning.
- Sector-conditioned forecasting.
- Aggregation of instrument-level forecasts into index-level forecasts.

Important:

Multiple securities observed on the same date are not independent NIFTY outcomes.

Use date-grouped validation, appropriate dependence adjustments, and causal features.

A large stock-date training panel may help estimate shared relationships, but it does not magically create more independent monthly NIFTY observations.

Any index-level aggregation must use historically defensible membership and weights.

---

# PHASE 5 — DERIVATIVES × PRICE × VOLATILITY RESEARCH

Previous V3/V4 experiments used derivative features, but the information may depend on interactions and specific market conditions.

Research structured relationships rather than isolated OI variables.

Candidate questions:

- Does rising OI alongside rising prices mean something different from rising OI alongside falling prices?
- Does unusually concentrated call or put OI have predictive value after conditioning on trend?
- Does futures basis predict future returns or merely reflect carry?
- Do changes in positioning matter more near expiry?
- Is unusual OI movement informative only during high volatility?
- Does derivatives positioning help predict large moves more effectively than simple direction?
- Does volatility compression combined with positioning concentration precede volatility expansion?

Research differences between:

- Absolute positioning.
- Changes in positioning.
- Positioning relative to historical norms.
- Positioning adjusted for market activity.
- Positioning conditional on price/volatility regimes.

Normalize contracts and expiry effects correctly.

Use controlled ablations to determine whether derivatives add predictive value beyond price, sector, and global inputs.

---

# PHASE 6 — TEST NEW MODELING APPROACHES

We should not lock ourselves into the previous modeling families.

However, new models must be justified by available samples and research hypotheses.

## Track A: Dynamic factor models

Investigate whether global and Indian asset returns can be summarized into a small set of changing factors.

Compare:

- Static PCA.
- Rolling PCA fitted causally.
- Regularized factor regression.
- Dynamic-factor approaches when identifiable.
- Global and domestic factor interactions.

## Track B: Nonlinear interaction models

Evaluate:

- LightGBM.
- XGBoost.
- CatBoost.
- Generalized additive models.
- Shallow interaction models.
- Small, heavily regularized nonlinear models.

Research whether interactions between global, sector, derivatives, and volatility variables explain previously unstable results.

## Track C: Regime-specific models

Investigate:

- Causal volatility regimes.
- Trend and sideways regimes.
- Global risk-on/risk-off regimes.
- Sector participation regimes.
- Markov-switching or hidden-state approaches with appropriate safeguards.

Evaluate whether models work only within certain pre-identifiable conditions.

Do not infer a historical regime using future outcomes.

## Track D: Sequence learning

Explore whether recent sequences contain more information than static indicators.

Candidate approaches:

- Structured-lag regression.
- Temporal convolution.
- Small recurrent architectures.
- Lightweight attention mechanisms, only if justified.

Compare them against simple lagged-feature baselines.

Do not assume deep learning is appropriate merely because there are millions of intraday records.

## Track E: Conditional distribution models

Research coherent forecasts for:

- Direction.
- Return magnitude.
- Expected return.
- Median return.
- Quantiles.
- Large-move probabilities.

Explore flexible but regularized distributions and conditional return models.

Evaluate calibration, CRPS, Brier score, return error, and interval coverage.

All quantities derived from a single endpoint distribution must be internally coherent.

## Track F: Historical analogue and similarity models

Research nearest historical market states defined by:

- Indian trend.
- Global risk.
- Sector rotation.
- Volatility.
- Derivatives.
- Market breadth.

Compare similarity metrics, feature-group selections, and conditional distributions.

Investigate whether analogue methods perform better for unusual market conditions than generic supervised models.

## Track G: Multi-horizon and auxiliary-target learning

Investigate whether learning related tasks helps:

- One-session returns.
- Three-session returns.
- Five-session returns.
- Twenty-one-session returns.
- Volatility.
- Market breadth changes.
- Sector-relative performance.

Shorter horizons may offer more frequent learning signals.

But do not assume success on an auxiliary target implies success for weekly or monthly NIFTY forecasting.

Evaluate primary horizons independently.

---

# PHASE 7 — DISCOVER CONDITIONAL SIGNALS

A signal may appear useless on average but informative in a particular market environment.

Investigate hypotheses such as:

- Momentum works under low volatility but reverses under high volatility.
- Negative global-market signals matter more when Indian breadth is deteriorating.
- Derivatives positioning matters mainly near expiry.
- Sector dispersion is useful after unusually concentrated rallies.
- Oil and currency effects change across inflation or global risk regimes.

For every conditional relationship:

1. Define the regime using information available at the forecast origin.
2. Measure the training sample size.
3. Measure the number of independent evaluation windows.
4. Estimate the conditional effect.
5. Compare against a regime-aware baseline.
6. Test stability across time.
7. Adjust interpretation for the number of explored interactions.

Do not create increasingly narrow conditions merely to find a high-accuracy subgroup.

Track selective-forecast coverage as well as accuracy.

---

# PHASE 8 — EXPERIMENTAL DESIGN AND VALIDATION

Continue researching extensively, but keep the search auditable.

## Historical scope

Use only 2025–2026 observations.

No pre-2025 fitted state, indicators, training labels, or historical observations.

Every target must mature fully before use.

Use the same market calendar rules as V4.

## Controlled research structure

Organize experiments by hypothesis and research track.

For each track:

1. Establish a simple baseline.
2. Develop initial features.
3. Test a small set of models.
4. Evaluate incremental improvements.
5. Conduct feature-group ablations.
6. Stress-test apparent winners.
7. Record failures.
8. Decide whether to expand that track.

You may expand promising directions, but register each new hypothesis before testing it.

Avoid unconstrained automated hyperparameter searches across hundreds of thousands of combinations.

## Chronological evaluation

Use purged, embargo-aware rolling or expanding training where appropriate.

Fit preprocessing and feature selection inside historical training folds.

Compare candidates on identical forecast dates.

Report:

- Brier score.
- Log loss.
- Accuracy.
- Balanced accuracy.
- Return MAE/RMSE.
- CRPS.
- Quantile losses.
- Distribution coverage.
- Dependence-aware uncertainty.
- Effective independent sample size.
- Performance by time period and regime.

Use multiple-testing adjustments and stability checks when interpreting the strongest results across large experimental families.

Explicitly test whether promising effects disappear after excluding individual months, including September 2026.

## Critical research-integrity requirement

All previously explored 2025–2026 periods are research-exposed.

New results from those periods are exploratory, even when obtained through chronological cross-validation.

Do not pretend a new random seed, alternate split, or modified feature matrix produces independent confirmation.

However, do not terminate discovery just because independent confirmation is unavailable.

Use retrospective data to identify and refine hypotheses, label their evidence correctly, and preserve their configurations for future testing.

---

# PHASE 9 — BUILD A SIGNAL DISCOVERY RANKING

I want an explicit ranking of promising feature families and hypotheses.

Do not rank solely by one model's accuracy.

For each hypothesis, report:

- Signal description.
- Data sources.
- Timeframe.
- Target horizon.
- Economic or behavioral rationale.
- Historical coverage.
- Incremental forecasting improvement.
- Stability across folds.
- Dependence on particular months.
- Missingness and leakage risk.
- Complexity.
- Statistical uncertainty.
- Current evidence status.
- Recommended next experiment.

Use these evidence classifications:

**REJECTED:** A failed or invalid hypothesis with a documented reason.

**INCONCLUSIVE:** No useful signal demonstrated, but evidence insufficient to rule it out.

**EXPLORATORY LEAD:** An interesting retrospective effect requiring additional testing.

**ROBUST RETROSPECTIVE CANDIDATE:** A comparatively stable effect surviving the registered retrospective stress tests, but still research-exposed.

**INDEPENDENTLY VALIDATED:** Reserved only for genuinely independent evidence satisfying the predetermined validation requirements.

Do not force every feature into a positive or negative category.

---

# PHASE 10 — BUILD THE BEST EXPLORATORY WEEKLY AND MONTHLY SYSTEMS

After completing the research tracks, identify the strongest exploratory approaches for each horizon.

We want:

### Weekly model
- Five-session directional probability.
- Expected return.
- Median return.
- Conditional return distribution.
- Confidence and uncertainty estimates.
- Evidence of incremental value from global, sector, or derivatives signals.

### Monthly model
- Twenty-one-session directional probability.
- Expected return.
- Median return.
- Return distribution.
- Explicitly reported uncertainty and effective sample size.

Monthly model complexity must reflect the very limited number of independent outcomes.

If different models produce incompatible statistics, present them as distinct model outputs rather than combining them into one incoherent forecast.

A mathematically coherent endpoint distribution is preferred when forecasting the full return distribution.

### Model comparison

Compare at least:

- Existing V4 frozen controls.
- Price-only baselines.
- Global-only models.
- Indian sector/breadth models.
- Derivatives models.
- Cross-market combined models.
- Best regularized nonlinear models.
- Best coherent distribution models.

Use identical historical origins whenever possible.

Do not allow V5 research to modify frozen V4 candidates or their existing prospective ledger.

---

# PHASE 11 — DELIVERABLES

Create:

1. `V5_DATA_UNIVERSE.md`
2. `V5_GLOBAL_MARKET_RESEARCH.md`
3. `V5_INDIAN_MARKET_INTERNALS.md`
4. `V5_DERIVATIVES_INTELLIGENCE.md`
5. `V5_CROSS_MARKET_FEATURES.md`
6. `V5_ADVANCED_MODEL_EXPERIMENTS.md`
7. `V5_CONDITIONAL_SIGNALS.md`
8. `V5_VALIDATION_AND_STRESS_TESTS.md`
9. `V5_SIGNAL_RANKING.md`
10. `V5_WEEKLY_MODEL_RESEARCH.md`
11. `V5_MONTHLY_MODEL_RESEARCH.md`
12. `V5_FINAL_COMPARISON.md`
13. `V5_RESEARCH_CONCLUSIONS.md`
14. `V5_NEXT_HYPOTHESES.md`

Save complete reproducible code, features, configurations, metrics, per-origin predictions, rejected hypotheses, and model artifacts.

Produce a searchable experiment registry.

The final report must clearly distinguish what V5 newly discovered from what V1–V4 had already tested.

---

# FINAL EXECUTION INSTRUCTIONS

You have permission to use the available local research environment, inspect data, write Python code, execute experiments, build features, train models, and evaluate results.

Do not stop at a proposal.

Perform the research that the available systems and computing resources support.

Work in stages so that early experiments inform where to spend further research effort.

Be computationally efficient, but do not prematurely abandon promising avenues just because the first experiment is inconclusive.

Be especially creative about relationships involving:

- Global-market behavior.
- Indian sector rotation.
- Broad market participation.
- Derivatives positioning.
- Cross-asset volatility.
- Cross-sectional learning.
- Regime-dependent interactions.
- Transferable market factors.

Avoid merely recreating indicators already tested in V1–V4.

If there are thousands of usable historical inputs, investigate how to extract nonredundant, economically meaningful signals from them.

Do not treat repeated snapshots or correlated instruments as independent forecast outcomes.

Do not place trades or deploy models with live capital.

Do not silently expand beyond the 2025–2026 historical scope.

### THE KEY OBJECTIVE

I want us to investigate the possibility that NIFTY movements are better explained by the **joint state and evolution of Indian equities, global markets, derivatives, liquidity, and volatility** than by traditional NIFTY-only indicators.

Discover the most informative relationships.

Challenge previous results.

Explore new model families.

Find conditional opportunities.

Identify weaknesses and failure modes.

Do not stop simply because the previous four research versions failed to establish an independent edge.

**Success in V5 means discovering and rigorously characterizing new predictive hypotheses, improving our historical research results where possible, and identifying the strongest candidates for eventual independent validation.**

Even if every new hypothesis fails, the research should produce a clearly documented understanding of what was tested and why.

Begin by auditing the available market-data universe, then execute the global-to-NIFTY and cross-sectional research tracks first.