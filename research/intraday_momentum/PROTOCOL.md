# Intraday stock momentum — preregistered exploratory protocol

Version: `intraday-stock-momentum-v1`. Prepared 15 November 2026, before this
study's strategy results. This is a research experiment, not an instruction to
start a worker or place orders. Existing F&O and investment bots are untouched.

## Question and evidence

Does a mechanically defined, morning, high-volume NSE cash-equity mover setup
retain positive expectancy after plausible execution costs? The supplied post is
a hypothesis-generating discretionary framework. Its screenshot is an anecdote;
it does not reveal invested capital, complete fills, losses, fees or an audited
track record. We cannot claim to reproduce the author's intuition or live order
book interpretation from candles.

Primary question: an as-of-time mover filter combined with volume/VWAP and a
fixed 1% price target. A separate descriptive event study measures the proposed
8%→10% and 10%→12% extensions. These are percentage points of the day's return,
not the same as earning 1% from a later trade entry.

## Data and universe freeze

- Prices are existing or newly acquired **Upstox** observations, accessed through
  PostgreSQL. Preserve acquisition provenance; do not overwrite conflicting bars.
  Community prose, screenshots, results and any community data stay outside PG.
- The evaluation window is **14 November 2024–13 November 2026**, using the dated
  500-company fund-membership cohort supplied by the existing research pipeline,
  rather than today's winners. Freeze eligible identity/action exclusions and
  the dated membership source in the data manifest. Prefer five-minute equity
  bars, with one-minute bars only for a fixed ambiguity audit if available. Freeze instrument
  cohort, exclusions, source hashes and available coverage in a separate manifest
  before computing strategy returns. A shorter available window is explicitly
  a feasibility result, not silently represented as two years.
- Use the broadest feasible cohort independent of subsequent performance. Never
  construct the universe from historical end-of-day gainers, today's successful
  stocks or the four screenshot names. A current retained instrument master is
  acceptable only as an explicitly survivorship-biased exploratory cohort.
- Each session's liquidity eligibility uses only earlier sessions: previous
  close at least ₹50 and prior 63-session median daily traded value at least
  ₹5 crore, with at least 50 valid earlier sessions. Daily OHLCV alone may screen
  prospective stock-days; it may not identify the final intraday winners.
- A daily `high / previous_close - 1 ≥8%` screen may reduce downloads for the
  positive-mover strategies: every completed close reaching 8% must lie inside
  such a day's high. It is an **acquisition optimization only**; trade eligibility
  still waits for an actual completed-bar morning qualification. Fetching only those days
  cannot support the 4% control, negative movers or a full daily RVOL baseline.
  Acquire the appropriate independent set for those comparisons or report them
  `NOT_TESTED_DATA_COVERAGE`, rather than conditioning their results on 8% winners.
  The 4% comparison remains registered but **NOT_TESTED_DATA_COVERAGE** in this
  study; acquiring its independent candidate set would require about 9,700
  requests. It is replaced in the executable catalog by a volume-gate ablation.
- Check units, duplicates, timestamps, chronological order and missing bars.
  Opening gaps caused by splits/bonus/demerger must not become momentum signals.
  Use historical adjusted previous close where certified; otherwise exclude
  known affected ex-dates and disclose incomplete corporate-action coverage.
- Historical MIS availability, price bands, trade-to-trade restrictions, depth
  and queue position are not inferred from today's flags. If these histories are
  unavailable, mark executable long/short returns as provisional.

## Common definitions

Use only completed regular-session bars, timestamped in Asia/Kolkata. At a bar's
completion, the decision price is its close. Daily change is close divided by
the previous completed session's official close minus one. Let `d` be its sign.

- As-of VWAP proxy: cumulative `(high+low+close)/3 × volume` divided by cumulative
  volume from 09:15 through the decision bar. It is a candle proxy, not observed
  tick VWAP.
- Cumulative RVOL: today's cumulative volume through this clock bucket divided
  by the median cumulative volume through the same bucket in the previous 20
  exchange trading sessions, using valid observations from that window; require
  at least 10 valid prior sessions and RVOL ≥1.5. Never divide
  by the eventual full-day volume. Correct comparable units around known splits.
  This requires previous-session intraday data, not merely event-day files. If
  acquisition cost prevents that history, a clearly separate exploratory model
  may use current cumulative volume as a fraction of prior daily volume with a
  fixed elapsed-session adjustment. It must not be called same-time RVOL or
  silently substituted into this catalog; freeze its formula before its P&L.
- Require positive latest-bar volume and a nonflat current candle (high>low).
  For direction-following entries, require the decision close
  on the corresponding side of VWAP.
- Every catalog row, including the volume-gate ablation, requires a finite,
  positive same-clock RVOL observation. The ablation removes only the ≥1.5
  threshold and retains the same RVOL-based candidate priority; it is **volume
  gate off**, not a claim that all volume information was removed.
- Decision times may produce entries from 09:30 through 11:30 inclusive. A signal
  at a completed bar enters at the *next* bar's open, including adverse slippage;
  the signal bar's closing price is not an assumed executable fill.

## Frozen catalog: six mechanisms × two stops = 12 configurations

All variants have a **1.0% price target from entry**, with stop distance either
**0.5% or 1.0%**, maximum hold **60 minutes**, and forced cash-session exit by
15:10. No stop is widened. Long/short variants are symmetric in their rules;
results are also broken down by direction. Let a directional prior-bar extreme
mean the high for an upward mover and the low for a downward mover.

| ID | Mechanical entry hypothesis |
|---|---|
| `cross8` | First eligible completed morning bar with absolute daily change ≥8%, RVOL qualified, enter in `d` with VWAP alignment. Gappers already above 8% at the first eligible clock qualify. Fire once per direction per stock-day. |
| `cross10` | Same as `cross8`, but threshold 10%. |
| `breakout8` | Absolute daily change ≥8%; close breaks the prior three completed bars' directional extreme; RVOL and VWAP aligned; enter in `d`. Four consecutive five-minute observations are required for that comparison. |
| `vwap_reclaim8` | Absolute daily change ≥8%; prior close is on the wrong side of the prior bar's VWAP, and current close reclaims the correct side of current VWAP; RVOL qualified; enter in `d`. A gap reclaim is allowed; no extra intrabar touch is required. |
| `exhaustion8` | Absolute daily change ≥8%; two prior completed bars have directional bodies in `d`; current close crosses the immediately prior bar's opposite extreme, indicating rejection; RVOL qualified; enter against `d`. |
| `cross8_no_volume` | Same first-qualified-bar rule as `cross8`, without the RVOL≥1.5 gate. Finite positive RVOL remains required and still contributes to candidate priority. Report as "volume gate off". |

The catalog is the entire initial search. A descriptive baseline of qualified
first-8% events may be reported without converting it into another optimized
strategy. Never select a different stop, threshold, window, direction or parameter
after viewing held-out results and call the changed rule the original winner.

**Primary portfolio is long-only.** Use positive daily-change signals for the
continuation/breakout/pullback/ablation rules. The `exhaustion8` family and any symmetric
short component are diagnostic and cannot become the selected primary bot from
this study: dated broker intraday-short eligibility is absent. Their accounting
must not be mixed into the primary cash-only NAV or capital totals.

## Funded portfolio and chronological execution

- ₹10 lakh starting cash; no leverage in the primary long-only portfolio. Target
  planned stop risk per new position is 0.5% of current marked equity, subject to
  cash and modeled costs: a 0.5% stop can use at most approximately 100% notional,
  a 1% stop approximately 50%, before liquidity/cost caps. Report net basis points per
  trade alongside rupee and NAV results so the edge is not confused with capital.
- Whole shares; size at the decision close, including the fee estimate, and cap
  quantity to 1% of the **completed decision bar's** volume. Fix that quantity
  before observing the next open. Known cash/estimated costs must allow the order; never use future volume to
  decide entry size. Volume participation is a model, not evidence of opening
  fill liquidity.
- Skip an entry if its modeled next-open fill exceeds a 0.5% adverse-price limit
  relative to the decision close. Do not invent an intrabar resting-limit fill.
  Anchor stop/target to the actual modeled entry fill, not the earlier close.
- At most **three entries per day across the whole portfolio**, at most **one
  simultaneous position**, and no same-symbol re-entry that day. These limits
  are not applied independently to every stock and then summed as if capital
  were unlimited. A session may have zero trades.
- If simultaneous candidates exist, prioritize `abs(daily_change) × min(RVOL,10)`,
  then stable instrument key. No ranking
  by subsequent P&L, maximum excursion or end-of-day move.
- Stop entering once net realized daily loss reaches 1% of opening equity. This
  gate prevents subsequent entries; it is not a guarantee that the final daily
  loss stays below 1%. Stops, fees, gaps and failed exits can cross that level.
  Before an entry, also cap its estimated stop loss including fees/slippage to
  the smaller of 0.5% current equity and the remaining daily loss room
  (`1% opening equity + realized daily P&L`). This admission guard can reduce
  the next position before the realized-loss halt is reached. Keep the
  decision-time quantity fixed; reject an actual opening fill that exceeds
  available cash or this reserved risk instead of resizing with future data.
- Handle exits before new entries. For an opening gap through a stop, use the
  adverse available open, not the stop level. If stop and target are both touched
  within an unresolved candle, charge the stop first. Do not give favorable target
  gap improvement in the conservative base case.
- A 60-minute time exit uses the open of the due bar, not that bar's later close.
- Missing/zero-volume bars cannot create fills. A failed exit remains pending;
  do not free its capital for another position. Identify unresolved end-of-session
  exposure separately; an overnight mark is not an observed intraday liquidation.
  This research implementation fails the entire affected configuration on an
  unavailable scheduled or triggered exit and reports an unresolved execution
  case. It does not continue that portfolio, drop the trade, synthesize a
  liquidation, or claim to simulate the pending position's later disposition.
- A historical short is a hypothetical MIS-capable execution unless dated broker
  eligibility is available. Report long-only and short components separately.

## Costs and fixed stress cases

Use a separately recorded dated Indian cash-intraday fee schedule from primary
sources, including brokerage, sell-side STT, exchange charges, SEBI fees, stamp
duty and GST on its applicable base. Report costs explicitly. Apply **10 basis
points adverse slippage on each side** in the base case; this is an assumption.

The mandatory fixed stress is **25 bps adverse slippage per side**. Optional
one-extra-bar latency, lower participation and a fixed one-minute resolution
audit may be reported as additional stress diagnostics if their data exist;
they are not extra selectable models. Wide spreads, circuits and queue position
can be worse than these assumptions.

## Selection, uncertainty and reporting

The chronological periods are fixed as follows:

- Development: **2024-11-14–2025-08-31**.
- Validation: **2025-09-01–2026-02-28**.
- Final: **2026-03-01–2026-11-13**.

Keep validation and the final period
untouched until implementation and the selection rule are frozen. This calendar
has appeared in earlier project research, so it is pseudo-out-of-sample evidence,
not a claim of a wholly unseen market history.

1. Implement synthetic regression tests before full strategy returns: future-bar
   mutation cannot change past signals; next-bar fills; correct daily RVOL;
   global three-trade and one-position limits; gap/ambiguous-bar exits; integer
   cashflow and fee reconciliation; deterministic candidate ordering.
2. Report all 12 configurations across all three periods, including failures
   and data-unavailable controls; distinguish primary from diagnostic rows.
   Choose at most one eligible long-only continuation/breakout/pullback/ablation
   candidate by **development-only** net expectancy per unit notional,
   subject to positive development expectancy and ≥50 development closed trades.
   Break ties by lower development drawdown, then frozen ID. Freeze that selection
   before opening validation/final results. Neither held-out period can choose a
   replacement or tune the original rule. No qualifying candidate is a valid outcome.
3. For the selected rule report final net return, CAGR only for sufficient length,
   drawdown, profit factor, win rate, payoff ratio, net basis points/trade, fills,
   trading days, exposure, turnover, fee/slippage drag and unresolved exits.
   Include zero-trade sessions in portfolio statistics and confidence intervals.
4. Use common-session block resampling (20-session blocks, at least 1,000 draws)
   for net daily expectancy/return uncertainty. Stock trades from one market day
   are not independent observations. Disclose the 12-model search; a best-of-12
   positive backtest is not itself evidence against chance.
5. A paper-candidate label requires ≥50 final closed trades across ≥30 traded
   sessions, positive final funded return and expectancy, no unclosed execution/accounting issues,
   and positive funded return as well as positive mean net basis points per trade
   under the 25 bps/side stress. A 95% interval crossing zero is explicitly
   inconclusive. No candidate is automatically installed as a bot.

The 8→10 event study uses only the **first as-of crossing** per stock-day, and
reports extension before reversal, time to extension, and censoring at the common
session endpoint. An event's eventual outcome cannot retrospectively decide
whether it would have entered the portfolio.

Implementation clarification before any strategy P&L: the event study uses the
first RVOL-qualified completed morning observation per threshold/direction,
including existing gappers. The extension is two percentage points of daily
return from the previous close; the competing reversal is 1% of raw next-open
entry. Evaluate next 60 minutes and through 15:10 separately, using adverse-first
classification for unresolved dual-hit bars. Count and disclose overshoots,
missing entries and censored paths rather than folding them into hit rates.

Data-engineering clarification before strategy P&L: provider-back-adjusted
split/bonus OHLCV must be reconstructed to contemporaneous share units for the
rupee price floor, whole-share sizing and volume participation. Keep original
Upstox candles unchanged in PostgreSQL. Same-clock RVOL can use the provider's
common adjusted-volume basis: its common scale cancels. A corrected acquisition
plan may add missed eligible stock-days before any P&L is viewed; record its
version and retain the previous plan, source jobs and reason for the correction.

The required execution grid is 09:15 through the 15:10 hard-exit opening
observation (72 five-minute bars). Later closing-auction observations are not
required and may not censor an otherwise usable morning. This grid decision is
fixed before strategy returns. Missing required observations remain quarantined
and counted; no later-session bars are fabricated or forward-filled.
