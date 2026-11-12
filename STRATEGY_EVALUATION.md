# Multi-factor strategy evaluation

The evaluator compares the eleven directional research configurations below against one market snapshot. Its score describes the strength and quality of the available evidence for a setup. It is **not a calibrated probability of a profitable trade**, an option-premium return forecast, or an authorization to place an order. The existing Project Alpha validation and execution gates remain separate.

## Weighting and explanation

The initial weighting policy distinguishes structural relevance from measured predictive performance. A prerequisite of the strategy receives structural relevance `1`; a corroborating factor receives `0.5`. Contextual applicability can then discount relevance. Irrelevant inputs are excluded. These values are declared policy, not estimated forecasting coefficients. A factor does not lose relevance just because it contradicts the candidate direction: reliable opposing evidence keeps its negative contribution.

Factors share one of four dependence domains:

| Domain | Factors and purpose |
|---|---|
| Price | Setup geometry, EMA/trend/momentum/RSI, extension, price regime, volatility, and other candle-derived confirmations |
| Positioning | Expiry-specific PCR, OI structure/changes, and Max Pain |
| Context | Broad participation, external markets, and institutional context, subject to valid transformations |
| Risk | Dated event context and suitability, without treating event presence as a price prediction |

Each relevant domain begins with equal **prior capacity**. Its usable budget is then reduced by the domain's observed reliability and completeness, before the effective budgets normalize across available domains. A nearly unreliable context reading therefore cannot claim half the score merely because price and context are the only domains present. All candle-derived factors stay in the price budget. Adding several EMA or momentum confirmations therefore cannot create several independent domain votes. This is a conservative dependence policy rather than a claim that historical correlations have been estimated. OI-PCR and Max Pain likewise share their positioning budget.

Within each domain, raw factor weight is relevance multiplied by effective reliability. Effective reliability already includes any accepted historical-evidence multiplier; it is not multiplied twice. Raw weights normalize to the domain budget. The factor's signed alignment captures supporting versus opposing evidence, while magnitude captures signal strength. A weak but fresh reading differs from a strong stale reading: the former has small signed magnitude; the latter has reduced or zero usable reliability.

The equations in [the scoring core](backend/app/services/strategy_scoring.py) are:

```text
relevance_i = structural_relevance_i × applicability_multiplier_i
u_i = relevance_i × effective_reliability_i

Q_g = sum(u_i for usable members of domain g)
      / sum(relevance_i for every expected member of domain g)
W_g = Q_g / sum(Q_h for available domains h)
w_i = W_g × u_i / sum(u_j for usable members of domain g)
contribution_i = 100 × w_i × alignment_i
score = sum(contribution_i)

coverage = number_of_available_domains / 4
quality = mean(Q_g for available domains)

P = sum(domain_weight × max(domain_alignment, 0))
N = sum(domain_weight × max(-domain_alignment, 0))
conflict = 2 × min(P, N) / (P + N), or 0 when P + N = 0

confidence = max(score, 0) × coverage × quality × (1 - conflict)
```

Here `Q_g` is domain quality and `W_g` is its effective weight; a domain is available when `Q_g > 0`. Equal prior capacities cancel in the normalization, leaving effective weights proportional to quality. When all domain qualities are zero, all weights, score, coverage, and confidence are zero. Alignment is bounded to `[-1, 1]`, total usable factor weights sum to one when any domain is available, score lies between `-100` and `100`, and confidence is bounded to `[0, 100]`. Missing expected members contribute zero quality while remaining in the relevance denominator, so removing a missing observation cannot improve completeness. Supporting and opposing factors within a domain cancel before cross-domain conflict is calculated; each domain also exposes its own `internal_conflict`.

Confidence is forced to zero when the exact setup is unavailable or has not triggered. A single available domain cannot establish a multi-factor candidate. With only complete price evidence, for example, even perfect positive alignment has only one-quarter domain coverage. Time, regime, and holding-horizon failures produce explicit watch reasons. The live wrapper also checks the exchange session and always returns `action: "NO TRADE"` and `deployment: "RESEARCH ONLY"`.

The result exposes considered and excluded factors, domains, normalized weights, signed alignment, contribution, reliability, provenance, and the reason each factor was used or rejected. Domain-level scores, missing-domain coverage, and conflict explain the aggregate. A strong-looking score with narrow coverage is therefore distinguishable from broad independent agreement.

Validated historical evidence can activate a strategy-specific directional mapping, including its sign and predictive reliability, or discount an existing factor's reliability. A retrospective winner table does not qualify. The initial fallback deliberately makes no claim of learned optimal weights. Applicability is separate: Max Pain's relevance is discounted by `min(1, 60 / minutes_to_expiry)` for the sixty-minute research horizon; an absent or expired contract has no applicability. This is a time-horizon policy, not an estimated pinning probability.

The current live [market adapter](backend/app/services/strategy_context.py) gives Max Pain, PCR, OI balance/walls, and untransformed daily institutional flows **zero default predictive reliability**. It still exposes their values and exclusion reasons. Fresh positioning descriptors can receive a strategy-specific mapping through the validated artifact described below. Without that evidence, they do not change the live directional score. Historical discount metadata alone cannot activate a zero-reliability mapping, and no artifact can resurrect an unavailable or stale measurement. A factor with no defined usable signal, such as untransformed daily flow, also remains unavailable. The same caution applies to unsupported macro/news transformations.

The live event calendar can contribute adverse event risk when a sourced high-impact release, already received by the decision, falls inside the holding horizon. If publication time is absent, the timestamp explicitly records calendar receipt, not event publication. An empty or incomplete calendar does not count as affirmative clearance. Historical event receipt/revision reconstruction remains an offline-data requirement.

## Optional historical-evidence artifact

The live service optionally reads `data/strategy-factor-evidence.json` under the configured data directory. A missing file keeps the conservative defaults. Malformed JSON is ignored with a visible error. The loader does not train a model, certify a study, or manufacture an artifact from the retrospective leaderboard; the declared results must come from the chronological validation workflow below.

The scorer accepts the following top-level metadata for a directional activation:

| Field | Required value or constraint |
|---|---|
| `method` | `"chronological_incremental"` |
| `validated` | `true` |
| `source` | Nonempty study/source identifier |
| `training_end` | Timezone-aware timestamp |
| `known_at` | Timezone-aware timestamp, with `training_end <= known_at <= decision` |
| `strategy_factors` | Object keyed by engine strategy ID, then factor ID |

Each activated factor entry under `strategy_factors[strategy_id][factor_id]` needs:

| Field | Required value or constraint |
|---|---|
| `validation_end` | Timezone-aware timestamp, with `training_end < validation_end <= known_at` |
| `signal_multiplier` | Number in `[-1, 1]`; negative reverses the descriptor's directional mapping |
| `predictive_reliability` | Number in `[0, 1]` |
| `incremental_ci_low` | Strictly positive lower bound for the tested incremental outcome |
| `corrected_p_value` | Number in `[0, 0.05]`, adjusted for the disclosed search |
| `validation_samples` | Integer of at least thirty; this minimum alone is not evidence of adequate power |

An accepted mapping sets effective reliability to measurement reliability multiplied by predictive reliability, then applies an optional `reliability_multiplier` in `[0, 1]`. It multiplies the descriptor signal by `signal_multiplier` before strategy alignment. A supplied factor's `relevance_multiplier` can only discount its structural relevance within `[0, 1]`. The mechanical `setup_*`, `regime_trend`, `volatility`, and `event_risk` definitions cannot be rewritten by historical directional mappings.

The artifact is strategy-specific; for example, acceptance for `pullback` does not enable the same factor for `ema_trend`. Profile IDs include `compression` and `gap_continuation`, while the older research CSV names those families `compression_breakout` and `gap_follow`. See [the profile registry](backend/app/services/strategy_scoring.py) for the complete identifiers. The scorer validates metadata and decision-time eligibility; independent reproduction of the underlying statistical study remains necessary. No qualifying artifact is supplied with this implementation.

## API and offline entry points

`GET /strategies/evaluate` reads one shared current market picture and evaluates every profile. Its [route](backend/app/routers/strategies.py) disables response caching. [The orchestration service](backend/app/services/strategy_evaluation.py) exposes `evaluate_live()` for current data and `evaluate_market(candles, dashboard, at, ...)` for controlled offline inputs. It does not add an order route or change the existing Alpha execution configuration.

The response contains `as_of`, `market_context`, `input_audit`, `strategies`, `errors`, `notes`, and `methodology`. Each strategy includes `score`, `confidence_score`, `coverage`, `quality`, `conflict`, `factors`, `groups`, `reasons`, and historical disclosures. Each factor shows `structural_relevance`, `applicability_multiplier`, `raw_relevance`, `reliability`, `weight`, `alignment`, `stance`, `contribution_points`, and source metadata. Audit status distinguishes a weighted input from a visible descriptor or unavailable measurement; having a visible value does not imply nonzero predictive weight. The API leaves `calibrated_probability` null. Arithmetic values are returned without display rounding so contributions can be reconciled to the total.

The offline function requires a historically valid dashboard snapshot. Current stored candles lack full first-receipt and revision vintages, so merely passing an earlier `at` does not turn them into an execution-faithful historical replay.

The existing [Alpha diagnostic CLI](scripts/alpha_signal_engine.py) attaches the same assessment while preserving its frozen execution gates. For a current read-only capture:

```powershell
.\.venv\Scripts\python.exe scripts\alpha_signal_engine.py --live --output data\strategy-assessment.json
```

The live command collects the current dashboard context and optional local weight evidence. Alongside the result, it saves `data/strategy-assessment.inputs.json` containing the decision time, exchange status, candles, market snapshot, and scoring evidence. Result hashes identify the candle inputs and market snapshot. This capture improves reproducibility; it does not reconstruct missing historical receipt/revision vintages.

For offline diagnostics, `--market-snapshot <path>` accepts a raw dashboard JSON captured as of the requested `--at`; `--weight-evidence <path>` accepts the chronological-validation artifact. Omit missing context rather than substitute today's dashboard into an old decision. The saved input bundle can also be passed directly to `alpha_signal_engine.evaluate(**bundle)` after loading its JSON.

## Sources and timing

The market picture combines completed five-minute NIFTY candles with the sourced factors across the [NIFTY catalog](backend/app/services/nifty_catalog.py), including price context, volatility, participation, institutional flows, external markets, and expiry-specific options positioning. Every factor must retain its underlying meaning, timeframe, source, publication time, receipt time, and expiry where applicable. A field can be useful context without being a directional vote.

- The [NIFTY service](backend/app/services/nifty_service.py) supplies structured factors with `value`, `status`, `reported_at`, `observed_at`, `source`, `expiry`, `basis`, and quality information. Its default technical indicators use **completed daily candles**, as established in [the collector](backend/app/services/nifty_sources.py). Those values provide daily context; the five-minute setup must be established from five-minute candles.
- The catalog's broad freshness windows describe retained research availability. An intraday assessment needs tighter decision-time checks. A retained factor marked `available` must not automatically be treated as a live signal.
- Publication and collection time are different. A newly fetched chain with no source market timestamp does not become fresh exchange data. A historical assessment must exclude observations published or received after its decision time; today's `latest()` observation cannot reconstruct what was known then.
- [Option analytics](backend/app/services/nifty_analytics.py) retain missing strike fields and reject mixed-expiry aggregates. PCR, OI totals, OI changes, OI walls, and Max Pain share underlying chain information. OI does not identify whether a position was bought or written, and Max Pain is an intrinsic-payout minimum rather than a guaranteed price target.
- [Volume PCR](backend/app/services/pcr_service.py) is distinct from OI PCR. Cumulative traded volume does not identify buying versus writing. [ATM IV](backend/app/services/iv_metrics.py) requires matched strike, expiry, spot, units, and observation provenance. Greeks describe option sensitivity, not independent directional conviction.
- NIFTY spot has no directly traded volume. A volume or VWAP factor requires an identified traded instrument and actual volume; index placeholders must remain unavailable.
- Economic levels and qualitative headlines are not mechanically converted into bullish or bearish scores. Events without a verified surprise or direction remain risk context. Unavailable or irrelevant factors are reported explicitly rather than invented.

## Strategy definitions

These definitions match the family leaders in [the last-year ranking](artifacts/last_year_ranking/family-leaders.csv) and the rules in [the directional laboratory](scripts/research_directional_lab.py). They are research rules, not a fitted multi-factor model.

For the table, `C`, `O`, `H`, and `L` denote the completed signal candle. `A` is the mean of the preceding fourteen true ranges; the signal candle is excluded from its ATR baseline. `E9`, `E12`, `E21`, and `E26` are the laboratory's exponential moving averages. `Hn` and `Ln` are the preceding `n` bars' highest high and lowest low within the session, excluding the signal candle. Direction `s` is `+1` for long and `-1` for short. All comparisons are strict unless shown otherwise.

The common trend measure is `T = (E9 - E21) / A`. Twelve-bar path efficiency is the absolute twelve-bar close change divided by the sum of absolute intervening close changes. The trend filter requires efficiency `>= 0.35` and `abs(T) >= 0.5`; the range filter requires efficiency `< 0.25`. EMA alignment means `s × T > 0`. Relative volatility is `A` divided by the prior rolling 200-observation median of ATR, with at least 100 baseline observations. High volatility means relative volatility `>= 1.2`; normal volatility means `< 1.2`.

| Configuration | Long setup | Short setup | Required filter and signal-bar window |
|---|---|---|---|
| EMA12/26 trend | `(E12 - E26) / A > 0.5` | `(E12 - E26) / A < -0.5` | Trend; afternoon |
| Failed breakout, 20 bars | `L < L20`, `C > L20`, and `C > O` | `H > H20`, `C < H20`, and `C < O` | Range; all |
| EMA9/21 pullback | `E9 > E21`, `L <= E9 + 0.75A`, `C > E9`, and `C > O` | `E9 < E21`, `H >= E9 - 0.75A`, `C < E9`, and `C < O` | EMA aligned; afternoon |
| Donchian breakout, 6 bars | `C > H6` | `C < L6` | Trend; afternoon |
| Momentum, 3 bars | Current close minus close three bars earlier `> 0.5A` | Same change `< -0.5A` | Normal volatility; morning |
| Compression breakout | Prior six-bar span `< 3A`, `C > H6`, and `(C - O) / A > 1` | Prior six-bar span `< 3A`, `C < L6`, and `(C - O) / A < -1` | Trend; afternoon |
| Opening-range breakout | `C > opening_high_15m + 0.25A` | `C < opening_low_15m - 0.25A` | EMA aligned; afternoon; complete opening range required |
| EMA mean reversion | `(C - E21) / A < -2` | `(C - E21) / A > 2` | Range; morning |
| Gap continuation | Opening gap `/ A > 3` | Opening gap `/ A < -3` | High volatility; before 11:00 |
| Gap fade | Opening gap `/ A < -3` | Opening gap `/ A > 3` | Range; before 11:00 |
| RSI40 mean reversion | RSI `< 40` and `C < E21` | RSI `> 60` and `C > E21` | Range; morning |

The lab computes EMA with `ewm(span=period, adjust=False)` and RSI from exponentially smoothed gains/losses with `alpha=1/14`; these should not silently be interchanged with the daily dashboard's SMA-seeded EMA and Wilder-seeded RSI implementations. Price-derived indicators retain earlier-session context; intraday extrema, returns, and efficiency use the laboratory's session boundaries.

Windows refer to **signal-bar start times in IST**: all begins at 09:30, morning is 09:30 to before 11:00, and afternoon begins at 13:00. A five-minute signal is known at its close, so a 13:00 signal becomes known at 13:05. The ranked configurations use the following bar's open and a sixty-minute hold, with exit by 15:10 and one position at a time per configuration. Missing bars or a partially observed opening range must not count as complete confirmation.

The original gap reference is the previous complete research session's **15:10 close**, not the official daily close. If a session was excluded, the reference can span more than one exchange session. Changing that reference, indicator initialization, entry timing, or filter changes the strategy and requires a separately versioned study.

## What the historical ranking establishes

The supplied table is the best cumulative index-points configuration from each family over a retrospectively inspected year, after five illustrative index points per trade and a minimum of fifty trades. The source [ranking summary](artifacts/last_year_ranking/summary.json) records 3,600 tested configurations, 2,947 eligible configurations, and 247 complete sessions from 10 November 2025 through 6 November 2026. Choosing the strongest family member on that same period introduces selection bias. Its profit factor and trade count cannot be used as fitted predictive reliability or a probability of success.

Every reported conditional 95% interval for average net points per trade spans zero:

| Family | Net points per trade | Conditional 95% interval |
|---|---:|---:|
| EMA12/26 trend | 7.25 | -0.76 to 15.55 |
| Failed breakout | 6.13 | -2.03 to 13.75 |
| EMA9/21 pullback | 2.46 | -4.02 to 9.01 |
| Donchian | 5.22 | -6.30 to 16.61 |
| Momentum | 3.20 | -1.67 to 8.27 |
| Compression | 8.78 | -8.74 to 27.85 |
| Opening range | 1.14 | -5.66 to 8.42 |
| EMA reversion | 3.80 | -7.81 to 15.48 |
| Gap continuation | 1.13 | -7.85 to 9.53 |
| Gap fade | 0.79 | -7.10 to 9.58 |
| RSI reversion | 0.74 | -9.85 to 11.92 |

These intervals, generated by [the ranking script](scripts/rank_last_year.py) using five-session moving blocks, remain conditional on already selected configurations; they do not correct the full strategy search. The reported index-point profits also do not establish option-buying profitability after spreads, IV changes, theta, slippage, taxes, fees, and capital constraints.

The existing [positioning study](artifacts/project_alpha/positioning-report.md) found zero of seventy-two fixed contrasts passing both corrected return and incremental-improvement criteria. Max Pain direction generally worsened tested outcomes. The [Project Alpha report](PROJECT_ALPHA_RESULTS.md) also shows that fifteen-minute EMA confirmation largely repeated the five-minute signals. These findings justify conservative treatment of positioning and shared-price confirmations; they do not establish a reliable inverse Max Pain strategy.

## Requirements before learned calibration

1. Freeze the strategy, feature transformations, source eligibility, holding horizon, costs, dependence groups, and intended outcome before fitting. Record source and code hashes. Keep underlying direction and option-premium outcomes distinct.
2. Reconstruct snapshots using only information actually available at each decision. Preserve release vintages, original receipt times, dated contracts, expiry, lot size, and missing opportunities. Never join a decision to that session's final OI or a later revision.
3. Fit relevance, reliability, correlation, and weight parameters on earlier training sessions only. Use rolling or expanding chronological folds; purge overlapping holding horizons at fold boundaries. Reserve a later calibration interval and a separate final evaluation interval.
4. Compare the complete model with the same covered price-only baseline and simple momentum controls. Test factor and group ablations, regime stability, source-age sensitivity, and realistic cost/execution stress. Account for the number of strategies and variants searched.
5. If a profitable-trade probability is required, calibrate it on held-out predictions, with a defined executable outcome and sufficient independent sessions. Report Brier score or log loss, reliability bins, confidence intervals, discrimination, and sample coverage. A weighted alignment score must not be renamed a probability.
6. Accept historical evidence for a factor only when it identifies the exact strategy, factor, outcome, costs, observation scope, chronological split, effective sample size, and selection adjustment. Negative, unstable, or uncertain incremental performance should reduce its predictive influence; a strong current reading cannot compensate for invalid provenance.
7. Freeze the resulting version before prospective observation. Follow the existing [forward protocol](artifacts/project_alpha/alpha-config.json): at least sixty distinct sessions and two hundred opportunities, or the larger predeclared cluster-adjusted power target, without optional stopping on profit. Changes start a new experiment. Preserve the current `RESEARCH ONLY` gate until acceptance requirements are met.

The implementation's assessment score can improve consistency and visibility immediately. Whether the multi-factor model improves recommendations is a separate empirical question to answer with these chronological comparisons.
