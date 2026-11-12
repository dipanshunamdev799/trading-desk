# Implementation audit of the frozen swing study

This audit preserves every original source file and result. The original ledger arithmetic audit passed because its arithmetic matched the inputs and fee assumptions. That did not independently establish the semantic correctness of those inputs. Two defects below illustrate the distinction.

## Verified defect: multi-component dividends were undercounted

`research/swing_discovery/data.py:209` uses `re.search` and keeps the first rupee amount in an NSE dividend subject. A subject can contain interim, ordinary and special distributions on the same ex-date. The parser discards later components.

The frozen NSE records and issuer sources agree on concrete counterexamples:

| Company / ex-date | Frozen credit per share | Sum of stated components | Omitted |
| --- | ---: | ---: | ---: |
| TCS / 2025-01-17 | 10 | 76 | 66 |
| TCS / 2026-01-16 | 11 | 57 | 46 |
| PFIZER / 2025-07-09 | 35 | 165 | 130 |
| 3MINDIA / 2026-07-17 | 160 | 506 | 346 |

There are **106 multi-component subjects** in the retained all-history stock audits; **26 events across 20 eligible companies** fall in the evaluated research period. Every enumerated correction has distinct dividend components in its subject. The patch list is specific to these inspected dividend records, not a general instruction to sum every rupee number in arbitrary corporate announcements (which can include totals or face values).

[TCS issuer payment history](https://www.tcs.com/investor-relations/dividend-payment-details.) confirms the separate ₹10/₹66 and ₹11/₹46 components. [Pfizer issuer dividend history](https://www.pfizerltd.co.in/unclaimed-dividend-shares) confirms the ₹165 distribution. The exact stored NSE subject remains in `audit-dividend-corrections.csv` for every proposed change.

This affects dividend cash entitlements for positions carried into the ex-date and buy-and-hold controls. Prices and entry indicators are unchanged by this dividend-only patch. The correction retains the original model's economic accrual on ex-date; it does not establish that cash was spendable before the issuer's payment date. TCS's issuer page, for example, distinguishes its January record dates from February payment dates.

## Verified defect: delivery taxes applied to same-session exits

`engine.py:15` charges 0.1% STT on each side and 0.015% buy-side stamp duty. `engine.py:58-60` turns off the DP debit for same-session exits but keeps the delivery STT/stamp schedule. The modeled position has not taken delivery when it opens and closes in the same session.

[NSE's levies schedule](https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies) distinguishes delivery from non-delivery, including 0.015% versus 0.003% buy-side stamp duty. [Upstox's primary tariff](https://upstox.com/brokerage-charges/) lists 0.1% STT on delivery buys and sells, versus 0.025% sell-side STT for intraday trades, and no intraday DP charge.

For the existing fixed trade path the statutory excess equals:

`buy turnover * (0.001 + 0.00012) + sell turnover * 0.00075`.

The audit-only engine refunds this at an actual same-session close. Entry sizing, initial planned risk and targets continue to allow for overnight delivery fees, since the exit date is unknown at entry. Flat brokerage remains unchanged, so this isolates the statutory classification issue; broker contract-note rounding, low-notional regulatory caps and intraday brokerage caps are not certified by this exercise.

## Size of the defects on retained fixed trade paths

| Period / 48 all-stock rules | Trades | Same-day trades | Statutory excess | Missing dividends | Positive rules before → after |
| --- | ---: | ---: | ---: | ---: | --- |
| Final six months | 40,557 | 438 | ₹64,374.10 | ₹48,389.50 | 2 → 2 |
| Full two years | 143,272 | 1,254 | ₹192,114.59 | ₹183,090.40 | 0 → 0 |

These cash amounts sum across **48 separate models**, each with 470 independent ₹10 lakh sleeves. They are not cash gains in a single funded portfolio. The final period is included in the two-year period, so their totals must not be added. Fixed-path corrections do not account for later cash-dependent sizing or changed exits.

An exact **96-run corrected replay** (48 frozen rules × final/full-two-year periods) then repeated the original execution with corrected dividend credits and actual same-day statutory taxes. This permits cash-dependent sizing to respond to corrected balances. It did not choose new rules or parameters. Results are in `audit-corrected-replay.csv`, `audit-corrected-replay-summary.json`, and `audit_corrected_journals/`:

| Corrected replay | Positive rules | Median mean-sleeve return | Highest return |
| --- | ---: | ---: | ---: |
| Final six months | 2/48 | −0.048030% | +0.007001% |
| Full two years | 0/48 | −0.191859% | −0.025291% |

KAMA-cross final improved from +0.006677% to +0.007001%; its full-two-year return improved from −0.107582% to −0.106842%. EMA-cross final improved from +0.004651% to +0.005142%; its full-two-year return improved from −0.123547% to −0.122640%. All 96 changes were positive, ranging from 0.000057 to 0.005427 percentage points. This corrects real pessimistic biases without rescuing broad profitability. No revised development/validation selection or complete revised robustness screen was performed in this replay, so it is not a new validation claim.

## Checks that did not reveal an implementation defect

Independent scalar seeded recursions on six actual eligible stocks agree with EMA 9/12/20/26/50/200, ATR14, RSI14, ADX14 and MACD12/26/9. Largest absolute discrepancy is below 2e-10, consistent with floating-point operation order. A separate explicit strict-pivot loop agrees with the engine's delayed confirmation flags. Every one of the 48 family representatives has prefix-invariant entry/exit/ATR/level/regime/trail arrays on the actual-data test cut. Prefix invariance includes the weekly families and KAMA families. This is evidence against future-candle leakage in those tested feature paths, not proof about every possible configuration or data-vintage revision.

Inspection and the retained engine tests show:

- Decisions at completed close execute at the following observed open; a pre-segment signal cannot create an initial position.
- Strict pivots appear after their right-confirmation bars. Prior-week/month levels use completed periods, and weekly oscillator/EMA observations release in the next observed week. This conservatively delays Friday weekly information by one daily decision/entry opportunity; it is documented and is not look-ahead.
- Both-hit daily candles resolve stop first. Gap stops use worse opens plus adverse slippage; favorable gaps through a target fill at the target, not the better open. These are conservative path conventions. Daily OHLC still cannot certify their actual intraday order.
- Fee-aware target algebra produces the intended planned net reward at the modeled overnight exit. Stops, targets and quantity adjust for integer splits, with fractional/unresolved actions quarantined. These are implemented assumptions; the dividend parser bug is an exception to the previously assumed action completeness.
- Sleeve cash includes principal synthetically while a position is held, but one position per sleeve and mark-to-market P&L make its NAV arithmetic self-consistent. This is not a reusable pooled account cash allocator. A funded portfolio must reserve cash and arbitrate simultaneous signals separately.

The new audit-only correction has five controlled regression tests in `research/swing_diagnosis/audit_tests.py`: exact same-day refund, unchanged overnight path, unchanged zero-cost path, reproduction of the multi-component parser defect, and explicit weekly execution timing. All five passed; output is in `audit-tests.log`. Existing research tests remain preserved.

The weekly timing test demonstrates a specific conservative restriction: a week ending Friday 10 January 2025 releases its completed weekly value into Monday 13 January's feature row (`signals.py:142-143`, weekly MACD analog `:156`). The engine reads the previous daily decision at entry (`engine.py:108-109`), so the first corresponding entry is Tuesday 14 January. An otherwise identical explicitly Friday-close decision can enter Monday 13 January. This is a one-session delay versus the earliest feasible weekly-information entry, not a future-candle leak. Its economic effect has not been established by this timing fixture and should be tested in a single controlled alignment comparison with a known exchange calendar.

## Questionable assumptions with measured or bounded implications

**Breadth gate.** Development eligibility requires at least 50% of every stock sleeve to finish positive, including inactive sleeves. This can penalize selective signals. However, only **16/1,308 development rules** traded in fewer than half the 375 development stocks, and only **2 of 166 development-profitable rules** had that mathematical inability to pass. The gate is a research-design choice that deserves active-stock breadth alongside all-stock coverage, but it does not explain most development failures. In validation 168 rules had fewer than half the stocks active, including 46 profitable rules; validation did not itself impose that breadth gate.

**Warmup and provider adjustments.** The dated cohort is selected in October 2024; its 2020–2024 prices support indicator warmup, not a historically selected 2020 investment universe. Actual units are inferred from known action factors and event continuity. Price/volume adjustment and historical quote depth are not independently certified. The inverse-volume assumption may understate capacity if the provider's volume is raw, particularly for stocks with splits. This remains an execution/data question, not a demonstrated indicator failure.

**Future completeness selection.** Thirty starting identities remain excluded for later missing sessions, unresolved actions or discontinuities. The disposition ledger preserves them, but requiring a complete future research path can favor data-complete survivors. Missing counterfactual trades cannot be truthfully filled with zero or synthetic prices. Historically point-in-time membership and delisting/merger consideration remain necessary for a longer study.

**Sample and validation.** Finalists were selected on already examined development/validation dates, and even final dates overlap earlier project research. The 95 held-out companies offer cross-sectional novelty only. Repeated trades across final/development/reserved/all-stock/full-path journals are not independent observations. Frozen-family, block-bootstrap and search corrections help describe uncertainty but cannot restore a genuinely untouched time period.

**Unresolved execution details.** Dividend spendability until pay date, settlement cash reuse, exchange price bands, limit/auction fill availability, order queueing, observed spread and nonlinear market impact are not certified. None is silently corrected by the two demonstrated patches. The broker fee model is configurable research arithmetic, not an exact historical contract-note reproduction.

## Interpretation

The audit establishes real pessimistic biases in dividend credits and same-day taxes, and no tested numerical/causal indicator defect. Fixed-path corrections leave the broad profitability verdict unchanged. Corrected replay and funded-portfolio results should be read before judging whether any particular entry/execution mechanism deserves another controlled test. Neither the old failure nor the two bugs establishes that technical signals can never work, or that correcting implementation automatically produces an edge.
