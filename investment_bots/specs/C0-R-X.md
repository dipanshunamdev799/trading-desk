# C0-R-X — C0-R with execution-evidence-gated simulated fills

Version: frozen fingerprint `3d1228a7750225ed` · document date 2026-11-14 · data window 2025-01-01 → 2026-12-31

> **RESEARCH / PAPER-TRADING SPECIFICATION — NOT A LIVE-TRADING AUTHORIZATION.**
> - This document describes frozen research rules and the paper-trading convention.
> - It does not authorize placing orders with real capital.
> - No component referenced here can place broker orders. The paper pipeline asserts that no order methods exist and records `real_orders_submitted: 0`.
> - Research data are restricted to **2025-01-01 → 2026-12-31**.
> - Any rule change creates a new version with a new fingerprint; it never edits this strategy.

## A. Strategy overview

| Item | Value |
|---|---|
| Strategy name | C0-R-X — C0-R with execution-evidence-gated simulated fills |
| Identifier (pipeline key) | `C0_R_X` |
| Frozen configuration fingerprint | `3d1228a7750225ed` (sha256 of the canonical config JSON, first 16 hex; computed by `research/swing_2025_2026/phase8/paper8.py::fingerprints()`) |
| Frozen code version | Config version `124623e3a4b1db81` (hash of the frozen sources: `phase5/sim5.py` ea13b4b83932de7c, `phase6/p6common.py` de078880d7513c11, `phase6/paper6.py` fe388b065c52952f, `phase7/p7common.py` 02cc5c95261e8fbd, `phase7/integrity.py` 0641588d14be8224, `phase7/paper7.py` 2881b43b130dace5) |
| Type | Cross-sectional stock-ranking and periodic-rebalancing strategy (relative momentum) with an execution-evidence gate on simulated fills (execution-validation research variant) |
| Asset class / market | Indian listed common equity, NSE cash market (segment `NSE_EQ`) |
| Direction | **Long-only.** No short positions, no derivatives, no leverage |
| Holdings | 20 equal-weight target positions |
| Rebalancing frequency | Every 5 trading sessions |
| Expected holding period | Variable, set by the retention rule (rank < 40). Historically (C0-R, 247 closed positions, 2025-04 → 2026-11): mean **28.4 sessions**, median 20 sessions, 10th–90th percentile 10–60 sessions. Positions are always reviewed at 5-session multiples |
| Decision data | Completed daily bars only (information cutoff = close of the decision session) |
| Execution convention | Next session's official open (NSE pre-open call-auction price) — **but a fill is simulated only when prospective auction evidence classifies the order 'likely'** |
| Status | Forward paper-trading ready as an EXPLORATORY execution-validation shadow. 0 forward sessions processed as of 2026-11-14. Requires the pre-open capture task to run. **Not approved for live capital.** |

### How it attempts to generate returns
- It ranks the ~300 most liquid eligible NSE stocks by **3-month price return divided by recent daily volatility** (a volatility-adjusted momentum score). It holds the 20 best-ranked names subject to an industry cap, and keeps a holding while it stays inside the top 40.
- It harvests the **cross-sectional momentum** effect: recent relative winners tend to keep outperforming over the following weeks. The retention band (enter in the top 20, exit only below rank 40) limits turnover.
- Phase 7 attribution showed most return variance is explained by market, breadth and momentum-factor exposure (R² 0.81). The residual alpha (+12.8 %/yr) is **not statistically significant** (t = 1.81).

### What this strategy is NOT
**NOT USED** — none of these are part of selection, entry or exit:
- MACD, EMA or SMA crossovers;
- RSI or other oscillators;
- support/resistance;
- candlestick or chart patterns;
- breakouts;
- stop-losses or trailing stops;
- profit targets;
- market-regime filters, NIFTY trend, India VIX or breadth.

These were researched in earlier phases (4H/2H MACD/EMA/S-R systems, breakout and dip-entry timing) and rejected. A position is opened or closed **only** by the ranking and rebalancing rules below.

C0-R-X uses exactly the C0-R stock-selection, sizing and scheduling rules. It changes only **which simulated orders are allowed to fill**: an order fills (at the official open) only if live pre-open auction data captured that morning classify it as `likely`. Otherwise it is not filled: buys are dropped, sells stay pending. Its purpose is to measure how much of C0-R survives when only defensibly observable fills are counted. **Satisfying the evidence gate does not prove that a real order would have filled.**

### Key source code (authoritative, frozen unless stated)
| Path (under `research/swing_2025_2026/` unless noted) | Role |
|---|---|
| `phase5/sim5.py` | Reference portfolio engine (frozen). Selection, retention, sector cap, sizing, schedule, next-open fills, costs |
| `phase6/p6common.py::inputs_fixed()` | Corrected (R) universe: fund/ETF ISIN exclusion, causal corporate-action mask, score |
| `daily.py` (class `D25`) | 2025-01-01 data slice, fund name filter, big-move detection, history count, top-300 universe |
| `selection.py::build()` | `volnorm_3m` score (3-month return ÷ (42-session log-return stdev × √63)) |
| `../swing_mtf/phase2/features.py` | `ret`, `shift` helpers |
| `../swing_mtf/phase2/dpanel.py`, `../swing_mtf/phase2/daily_data.py` | Daily panel, instrument master snapshot, NIFTY-500 industry mapping |
| `dmodels.py::arrays()` | Benchmark series (EW universe, momentum factor, NIFTY 50) — reporting only |
| `phase6/p6common.py::vt_exposure()` | Volatility-target exposure (not used by this strategy) |
| `phase8/xsim.py` | Execution-aware re-expression of sim5 (equal to ≤ 1.6e-15); whole shares, ledger, fill callbacks |
| `phase8/c2s.py` | C2-S five-book wrapper (not used by this strategy) |
| `phase8/paper8.py` | Forward paper pipeline: records, orders file, state, fingerprints |
| `phase8/auction_capture.py` | Pre-open snapshot capture and the auction evidence classifier (**the fill gate**) |
| `phase7/integrity.py` | Nine data-integrity checks that gate every paper decision |
| `phase6/costs6.py` | Account-size cost model (research only) |
| `trading-desk/trading_strategies/verification/spec_impl.py` | Independent implementation written from this document (verification) |

### Frozen parameters
| Parameter | Value | Unit | Source |
|---|---|---|---|
| Research data start | 2025-01-01 | date | `cfg.CUTOFF` |
| Research window end (hard stop) | 2026-12-31 | date | `p8common.WINDOW_END` |
| Universe size | 300 | instruments | `D25.universe(top=300)` |
| ADV window | 63 | sessions | `D25.universe(window=63)` |
| ADV minimum valid values | 50 | sessions (`int(63 × 0.8)`) | `D25.universe` |
| Minimum history for eligibility | 63 | valid closes since 2025-01-01 | `D25.universe(min_hist=63)` |
| Minimum history for a score | 64 | valid closes since 2025-01-01 | `selection.build need['volnorm_3m']` |
| Momentum lookback | 63 | sessions | `selection.build` |
| Volatility window | 42 | daily log returns | `selection.build` |
| Volatility minimum valid | 36 | daily log returns | `selection.build` |
| Score horizon scaling | √63 | — | `selection.build` |
| Target holdings N | 20 | positions | `C0["N"]` |
| Retention threshold | sell if 0-based rank ≥ 40 | rank | `C0["keep"]` |
| Industry cap at selection | 6 | positions per industry | `C0["sector_max"]` |
| Rebalance interval R | 5 | trading sessions | `C0["R"]` |
| Slot size | 1/20 of equity at the fill-session open | fraction | sim5 |
| Minimum buy | 20 % of an **unscaled** 1/20 slot (= 1 % of equity at the open) | fraction | `C0["min_buy_frac"]` |
| Reference transaction cost | 0.225 % of traded value per side | fraction | `C0["cost"]` |
| Large-move threshold (corporate-action mask) | 40 % | close-to-close move | `daily.D25._quality` |
| Mask length after a large move | event session + 5 | sessions | `p6common.inputs_fixed` |
| Leverage | none (cash ≥ 0, gross exposure ≤ 100 %) | — | sim5 |
| Gate: decision snapshot | last snapshot label ≤ 09:05:00 IST | time | `auction_capture.DECISION_MARKET` |
| Gate: post-match snapshot | first label in [09:12:00, 09:15:00) | time | `auction_capture.POST_MATCH` |
| Gate: staleness | 120 | seconds | `auction_capture.STALE_SECONDS` |
| Gate: maximum participation | 0.10 | fraction of indicative and of final matched quantity | `classify_auction(part_likely=0.10)` |
| Snapshot schedule | 09:00:30, 09:02:00, 09:03:30, 09:04:30, 09:06:00, 09:07:30, 09:09:00, 09:11:00, 09:12:30, 09:14:00, 09:15:30, 09:20:00, 09:30:00, 09:45:30 | IST | `auction_capture.SCHEDULE` |

## B. Tradable instrument universe

**Single source of truth:** the eligible universe U_t for session *t* is computed only from data through the close of *t*. The algorithm below reproduces the frozen implementation exactly. That was verified in every session of 2025-01-01 → 2026-11-13: 0 mismatching cells (`verification/verify_specs.py`, check 1).

| # | Rule | Exact definition |
|---|---|---|
| 1 | Exchange | NSE |
| 2 | Segment | `NSE_EQ` (Upstox instrument master, BOD snapshot `NSE.json.gz`) |
| 3 | Instrument type | `EQ` |
| 4 | Panel membership | The instrument is one of the **2,284 keys** of the frozen daily panel. The panel admitted `NSE_EQ`/`EQ` instruments of the master snapshot that had **≥ 260 daily bars** in the vendor cache when the panel was built (`dpanel.build`). The key set is fixed: instruments listed later are never added (see 16) |
| 5 | Fund/ETF name filter | Excluded if the trading symbol contains any of `ETF`, `BEES`, `IETF`, `GOLD`, `LIQUID`, `NIFTY`, `SENSEX`, or the upper-cased name contains any of ` ETF` (leading space), `FUND`, `EXCHANGE TRADED` |
| 6 | ISIN filter (corrected) | **Excluded if the ISIN starts with `INF`** (mutual-fund/ETF units). This is the correction that removed silver ETFs from the frozen Phase-5 books. Admissible company equity has ISIN prefix `INE`. The integrity gate `classification` additionally requires every universe member to have a **12-character ISIN starting `INE`** and no fund naming, and **blocks the decision** if any member fails. The panel contains INE 2,004 / INF 279 / IN9 1 instruments; the single IN9 (partly-paid) instrument never entered U_t |
| 7 | History | `H_t,i` = number of sessions s ≤ t, s ≥ 2025-01-01, with a valid (non-missing) close. Eligible only if **H_t,i ≥ 63** |
| 8 | Valid bar on t | close_t,i present **and** volume_t,i **> 0** |
| 9 | Liquidity | `ADV_t,i` defined (below) |
| 10 | Corporate-action mask | Not masked on *t* (rule 14) |
| 11 | Top-N | Among instruments passing 4–10, rank by ADV_t,i **descending**; the first **300** form U_t |

**Average traded value (ADV):**

```
TV_s,i  = close_s,i × volume_s,i                      (rupees; vendor split/bonus-adjusted close × adjusted volume)
W_t     = the 63 consecutive panel sessions ending at t (t-62 … t)
ADV_t,i = median{ TV_s,i : s ∈ W_t, TV_s,i not missing }   if count(non-missing) ≥ 50
        = undefined                                        otherwise
```

Missing values inside the window are ignored, not filled. The latest completed session *t* **is included**.

| # | Topic | Rule |
|---|---|---|
| 12 | Trading suspension | No dedicated suspension flag is used. A suspended stock has no bar (missing close) or zero volume on *t*, so it fails rule 8 that day. A missing close does not reset H. A holding that leaves U_t is sold at the next rebalance (§G) |
| 13 | Missing data | Missing cells are never forward-filled for eligibility, ADV, momentum or volatility. Portfolio marking uses the last valid price (§N) |
| 14 | Corporate-action exclusions | Rule below |
| 15 | Ranking ties (universe) | Instruments with exactly equal ADV at the 300 boundary are ordered by **panel column order** in the frozen code. The written intent is instrument_key ascending. **No boundary tie occurred in 2025–26.** The integrity check `universe_ties` blocks the paper decision if one ever occurs (unresolved design point, fail-closed) |
| 16 | Newly listed securities | Not admitted: the panel key set is fixed (rule 4). A stock listed after the panel build can never enter, even after 63 sessions of history. **Known limitation**; adding instruments requires a new version |
| 17 | Delisted / unavailable | The vendor master lists only currently listed instruments, so stocks delisted before the snapshot are absent (**survivorship limitation**, effect unknown). An instrument whose data stop simply stops being eligible (fails rule 8). A held instrument without data stays marked at its last price, and its sell stays pending until an opening price exists |

**Rule 14 — corporate-action / bad-print mask:**

```
move_t,i      = close_t,i / close_{t-1,i} - 1   (t-1 = previous panel session; undefined if either close missing)
large move    : |move_t,i| > 0.40, checked only for instruments not excluded by the NAME filter (rule 5)
classification (frozen code):
   reverted   if any k in 1..5 has |close_{t+k,i} / close_{t-1,i} - 1| < 0.15
   persistent otherwise
masked sessions:
   persistent : t … t+5                         (causal: starts at the session where the move is observable)
   reverted   : t-5 … t+5  (frozen code)        <- uses knowledge of a future print (look-ahead)
```

- **The reverted branch never occurred in 2025–26**: all 20 large moves were persistent, mostly suspected unadjusted demergers. The look-ahead therefore had no historical effect.
- The Phase-7 written rule, and the rule for any live implementation, is **mask t … t+5 for every large move**. It is applied at the close of *t*, when the move is observable.
- Splits and bonuses are vendor back-adjusted; all 19 feed events in 2025-11 … 2026-11 were verified.
- A position held into a large move takes the price move: the mask only blocks eligibility.

**Algorithm (each decision session t):**

```python
def eligible_universe(t):
    cand = [i for i in PANEL_KEYS
            if not name_is_fund(symbol[i], name[i]) and not isin[i].startswith("INF")
            and H[t][i] >= 63 and close[t][i] is not None and volume[t][i] > 0
            and ADV[t][i] is not None and not masked[t][i]]
    cand.sort(key=lambda i: (-ADV[t][i], panel_column_index[i]))   # frozen tie order
    U = cand[:300]
    assert all(isin[i].startswith("INE") and len(isin[i]) == 12 for i in U)   # integrity gate; else BLOCK decision
    return U
```

Industry label (used by the industry cap): the NIFTY-500 list's `Industry` matched by ISIN (static snapshot taken when the panel was built, **not point-in-time**). Every instrument not on that list has industry **`"Other"`**, which is treated as **one industry** for the cap. 21 labels exist. 85 of the 468 instruments that were ever eligible are `"Other"`, and the 6-name cap on `"Other"` was binding in 41 of 396 historical sessions.

## C. Market data requirements

| Input | Source | Timeframe / history | Update | Timestamp convention | Adjustment | Missing-data rule | Validation | Used for |
|---|---|---|---|---|---|---|---|---|
| Daily OHLCV | Upstox v3 historical candles → DuckDB `research/market_data.duckdb` table `candles` (`interval='1day'`) | 2025-01-01 → last completed session (≤ 2026-12-31) | Once per trading day, next morning (completed sessions only) | Bar = session date (normalized, IST); usable only after that session's close | Split/bonus back-adjusted by vendor; **dividends not adjusted** | Never filled for signals; last price used only for marking | One row per (instrument, date) (store holds 75,105 duplicates, de-duplicated keeping the latest load); OHLC consistency; volume > 0; completeness gate before deciding | **Signal**, universe, marking, fill price (open) |
| Session calendar | Dates on which the NIFTY 50 index has a stored daily bar | same | same | session date | — | A calendar day without a NIFTY 50 bar is **not a session** | — | Schedule counting |
| Instrument master | Upstox BOD NSE master (`NSE.json.gz`) snapshot → `broad_universe.csv` | static snapshot | not updated (fixed key set) | — | — | — | integrity `classification` | Universe |
| ISIN | instrument master | static | — | — | — | — | 12 chars, prefix `INE` for members | Universe |
| Industry | NIFTY-500 list (`ind_nifty500list.csv`) by ISIN; else `"Other"` | static snapshot | not updated | — | — | missing → `"Other"` | — | Industry cap |
| Corporate actions | Upstox `/v2/fundamentals/{isin}/corporate-actions` cached in `corporate_actions` (2025-11-14 … 2026-11-13 only; no demergers) | as available | as cached | ex-date | — | absent table → integrity check fails → **decision blocked** | `split_bonus` check | Validation only (the mask in §B is price-based) |
| Benchmarks | NIFTY 50 index; EW of U_{t-1}; costless top-quintile 3-month momentum | daily | daily | close | — | — | — | **Reporting only** |
| Portfolio state | Paper pipeline state files (`results/phase8/paper/state/`) | since day 0 | each run | session close | — | corrupt/inconsistent → **block** | hash + deterministic replay | Accounting / audit |
| 1-minute bars | Upstox v3 historical minutes → DuckDB `interval='1minute'` | fill days | next morning | bar start, IST | same as daily | missing → scenario marked uncertain | — | **Execution research only** |
| Pre-open quote snapshots (v3 full quotes) | Upstox `/v3/market-quote/quotes` | 14 per session 09:00:30–09:45:30 IST | live | server `timestamp` + receive time | — | failed snapshot stored as failure, never filled | sha256 manifest | **Fill gate (§K)** |

**Signal data vs execution data vs reporting:**
- **Signals** use only daily close, volume and the static master/industry data.
- **Execution simulation (reference convention)** uses the official daily **open** of the fill session.
- **The fill gate** additionally uses the pre-open snapshots (§K).
- **Benchmarks, 1-minute bars and quotes** are reporting/research inputs, except the quotes used by the gate.

**No pre-2025 observations:**
- Every array is sliced to dates ≥ 2025-01-01 **before** any computation, so no indicator is warmed up with older prices.
- Consequence: the first valid score appears once an instrument has 64 valid 2025 closes (2025-04-02 for the first instruments).
- The panel-membership rule (≥ 260 vendor bars when the panel was built) is the one place where the existence of pre-2025 history influenced which instruments are in the panel. No pre-2025 **price** enters any calculation (documented limitation).

## D. Indicators and input signals

All indicators use completed daily bars. The latest completed session *t* **is included**. Row arithmetic is over panel sessions; `t-k` means k sessions earlier, and a missing cell stays missing.

| # | Name | Purpose | Inputs | Formula | Lookback | Min. observations | Update | Edge cases |
|---|---|---|---|---|---|---|---|---|
| D1 | History H_t,i | eligibility / score validity | close | count of sessions s ∈ [2025-01-01, t] with close present | all of 2025+ | — | daily | missing closes do not count |
| D2 | Traded value TV_t,i | liquidity | close, volume | close × volume | 1 session | — | daily | missing if either missing |
| D3 | ADV_t,i | universe ranking | TV | median of non-missing TV over sessions t-62…t | 63 sessions | 50 | daily | undefined if < 50 |
| D4 | Log return r_t,i | volatility | close | ln(close_t / close_{t-1}) | 1 session | — | daily | missing if either close missing (no gap bridging) |
| D5 | σ42_t,i | normalize momentum | r | sample stdev, **ddof = 1**, of non-missing r over sessions t-41…t (**not annualized**) | 42 returns | 36 | daily | σ = 0 → see D7 |
| D6 | mom3_t,i | momentum | close | close_t / close_{t-63} − 1 | 63 sessions | close_{t-63} present | daily | missing if close_{t-63} missing |
| D7 | Score S_t,i | ranking | D1, D5, D6, U | **S = mom3 / (σ42 × √63)** if i ∈ U_t and H ≥ 64 and σ42 defined, else undefined | — | see column | daily | σ42 = 0 gives ±∞ (or undefined if mom3 = 0); **no ±∞ score occurred inside U_t in 2025–26**; the frozen code would rank +∞ first; no explicit rule (unresolved design point; a live implementation should fail closed on a non-finite score) |

**Pseudocode (exact):**

```python
H[t][i]      = count(close[s][i] is not None for s in sessions if s <= t)          # since 2025-01-01 only
ADV[t][i]    = median(nonmissing(close[s][i]*vol[s][i] for s in t-62..t)) if count >= 50 else None
r[t][i]      = log(close[t][i] / close[t-1][i])  if both present else None
sigma42[t][i]= stdev(nonmissing(r[s][i] for s in t-41..t), ddof=1) if count >= 36 else None
mom3[t][i]   = close[t][i] / close[t-63][i] - 1  if both present else None
S[t][i]      = mom3 / (sigma42 * sqrt(63))       if i in U[t] and H[t][i] >= 64 and all defined else None
```

**Numerical example (illustrative):**
- close_t = 520.00, close_{t-63} = 400.00, so mom3 = 0.300000;
- σ42 = 0.021000 (2.1 % daily), so σ42 × √63 = 0.021 × 7.937254 = 0.166682;
- **S = 0.300000 / 0.166682 = 1.79983.**

A stock with the same 30 % return but σ42 = 0.035 scores 1.07990, so lower-volatility trends rank higher.

**Ranking:** see §E. No other indicator exists in this strategy.

## E. Stock ranking and selection

| Item | Rule |
|---|---|
| Candidate pool | All i ∈ U_t with a defined score S_t,i (normally all 300) |
| Sort | S_t,i **descending** |
| Ties | instrument_key **ascending** (string order). No tie inside the top 45 ever occurred in 2025–26 (one tie in total, at a low rank); verified to have no historical effect |
| Rank | 0-based position in the sorted list (rank 0 = best) |
| Missing score | Not ranked. A holding without a score (left U_t, or undefined S) is treated as rank = ∞, i.e. sold |
| Minimum candidates | If fewer than **20** instruments have a defined score on a decision session, **the entire decision is skipped**: no sells, no buys. Existing holdings and any pending sells carry on. Happened only on 2025-04-01 (0 valid scores) |
| Retention | A holding is **kept** iff its rank **< 40** (ranks 0–39). Rank ≥ 40 or unranked ⇒ sell |
| Maximum holdings | 20 (kept + new) |
| Entry priority | Existing holdings are evaluated first (kept or sold). New entries fill the remaining 20 − kept slots |
| Industry cap | While walking the ranking, a candidate is skipped if (kept + already-selected new) names of its industry ≥ 6. `"Other"` is one industry |
| Skipped top names | Skipped candidates (held, or industry full) are passed over and the walk **continues to lower ranks** (beyond rank 19 if needed) until 20 names or the list ends |
| Fewer qualifiers | If the walk ends with fewer than 20 names, the unused slots stay in cash |
| Drift | No resizing of kept positions |

```python
def select(t, holdings):                      # holdings: dict instrument -> value
    order = sorted([i for i in U[t] if S[t][i] is not None],
                   key=lambda i: (-S[t][i], instrument_key[i]))
    if len(order) < 20:
        return None                           # decision skipped: no sells, no buys
    rank = {i: k for k, i in enumerate(order)}
    sells = [i for i in holdings if rank.get(i, INF) >= 40]
    kept  = [i for i in holdings if i not in sells]
    count = Counter(industry[i] for i in kept)
    new, slots = [], 20 - len(kept)
    for i in order:
        if slots <= 0: break
        if i in holdings or count[industry[i]] >= 6: continue
        new.append(i); count[industry[i]] += 1; slots -= 1
    return sells, kept, new                   # buy orders are issued in this rank order
```

Note: `sells` are computed from the holdings that exist at the decision close. A pending, still-unfilled sell from an earlier decision is **replaced** by this list. If that name now ranks < 40 it is kept, and its old sell is cancelled.

## F. Entry rules

**Selection signal ≠ execution.** The selection signal is created at the close of decision session *t* from completed data. Execution is a separate step at the next session's open, governed by §K.

**A new position in instrument i is opened at the open of session t+1 if and only if ALL of the following hold:**
1. *t* is a scheduled rebalance session of the book (§J) and the decision was not skipped (≥ 20 defined scores).
2. i ∈ U_t, S_t,i is defined, and i appears in `new` from §E (i.e. not held, industry count < 6, and within the first 20 − kept successful picks of the ranking walk).
3. At the open of t+1: an official open price for i exists (missing open ⇒ the buy is **dropped**, not deferred).
4. At execution time the book holds fewer than 20 positions. If an earlier sell could not execute (no open), the book may still hold 20 names, and the later buys in rank order are skipped.
5. Capital: amount = min(slot_target, cash), and amount ≥ 0.2 × (equity_open / 20). Otherwise the buy is skipped (§I).
6. **Evidence gate (C0-R-X only):** the prospective auction evidence for (session t+1, instrument i, side BUY, strategy C0_R_X) has status **`likely`** (§K decision table). Any other status, or no evidence, means the buy is **not filled**. It is dropped exactly like a buy without an opening price, the slot stays in cash until the next rebalance, and an alert `fill_not_assumed` is logged.

| Timestamp | Event |
|---|---|
| Close of t (15:30 IST + closing-price publication) | Information cutoff for the decision |
| Next morning, 07:45 IST (paper pipeline) | Data refreshed, gates passed, decision computed, target weights and **intended orders** written (`orders/<t+1>.json`) |
| 09:00–09:05 IST on t+1 | Window in which an equivalent real pre-open MARKET order would have to be entered (secondary-source rule; not exercised — no real orders) |
| 09:15 IST on t+1 (official open, set by the call auction) | **Reference simulated fill price — applied only if the evidence gate passes** |

**Order type / fill policy:**
- Reference convention: fill at the official open, full quantity, cost 0.225 % of value.
- Paper order quantity: whole shares, `floor(weight × book equity at the decision close ÷ decision close price)`. Orders with quantity 0 are rejected and logged.
- **Uncertain execution:** in the reference convention no execution uncertainty is modelled, because the official open is an observed price. In C0-R-X, uncertainty (no evidence, stale data, thin or imbalanced auction) means **no fill**.

```python
def entries_at_open(t1, new_list, book):
    for i, w in new_list:                       # rank order; w = 1/20
        if len(book.holdings) >= 20 or i in book.holdings or open[t1][i] is None:
            continue                            # dropped (not carried to a later session)
        amount = min(w * book.equity_open, book.cash)
        if amount < 0.2 * book.equity_open / 20:
            continue                            # below minimum buy
        if evidence_status(date[t1], i, "BUY", "C0_R_X") != "likely":
            alert("fill_not_assumed", ...); continue   # simulated non-fill
        book.cash -= amount
        book.holdings[i] = Position(value=amount * (1 - 0.00225), mark=open[t1][i])
```

## G. Exit rules

**A holding i is sold at the open of session t+1 if, at the close of a scheduled rebalance session t (decision not skipped):**
- **rank_t(i) ≥ 40**, or
- i is **unranked**: not in U_t (fails liquidity, history, valid-bar, fund or corporate-action rules) or S_t,i undefined.

| Mechanism | Status |
|---|---|
| Rank deterioration / retention threshold | **USED**: sell iff rank ≥ 40 at a rebalance decision |
| Ineligibility (left U_t) | **USED**, evaluated only at rebalance decisions |
| Industry constraint | **NOT USED for exits.** The cap applies only when choosing new names; drift above 6 names or a high weight is never forced out (historical maximum single-industry weight 37.9 %) |
| Fixed stop-loss | **NOT USED** |
| Trailing stop | **NOT USED** |
| Profit target | **NOT USED** |
| Time-based exit | **NOT USED** |
| Momentum-reversal exit between rebalances | **NOT USED** |
| Regime-based exit | **NOT USED** |
| Portfolio-level liquidation rule | **NOT USED** |
| Allocation reduction | **NOT USED** (no partial reductions) |

**Execution of exits:**
- Sells execute first at the open, before buys, for the full position.
- **No opening price** for i on t+1: the sell stays **pending** and is retried at each following session's open until it executes. A newer decision replaces the pending list (§E note).
- Proceeds net of 0.225 % are available to buys in the same session.
- **C0-R-X:** a sell fills only if the evidence for (session, i, SELL, C0_R_X) is `likely`. Otherwise it stays pending and needs fresh evidence in the next session.

**Corporate actions:** a holding hit by a > 40 % move is **not** sold by that event. It becomes ineligible for t … t+5, so if a rebalance falls in that window it is unranked and sold at the next open.

**Missing data / suspended holding:** the holding is marked at its last valid price. It is sold at the first rebalance at which it is unranked, but only executes when an opening price exists (pending until then).

**Partial fills:**
- Reference convention: none.
- Research engines (`xsim`): a partial sell leaves the remainder pending, and a remainder below ₹500 or 0.05 % of book capital is completed.

**Operational vs strategy exits:**
- The strategy has no discretionary or emergency exit.
- Operational controls (blocked decisions, alerts, manual review) **never sell**. They preserve the previous state and defer the decision.
- Any manual liquidation would be outside this specification and must be recorded as a manual intervention.

## H. Entry and exit timing (IST)

**Sessions** are the dates with a stored NIFTY 50 daily bar.
- Weekends and exchange holidays are not sessions.
- **Special sessions that have a daily bar count as sessions.** The 2025-26 data contain 2025-02-01 (Saturday budget session), 2025-10-21 (Muhurat), 2026-02-01 (Sunday) and 2026-11-08 (Sunday). They advance the 5-session schedule, and a fill can occur at their open. A Muhurat session's open is an evening, roughly one-hour session: **realism of fills there is unresolved**.

| Time (IST) | Step | Information available |
|---|---|---|
| Session t, 15:30 | Market close; official close published | — |
| t+1, 07:45 (paper pipeline `run_morning.cmd`) | Evaluate execution evidence of session t; refresh completed daily bars through t; completeness gate (≤ 2 % of universe ∪ holdings missing); rebuild panel from DuckDB (must match cache); 9 integrity checks; compute U_t, S_t, ranking; replay books from day 0; write records for session t and the orders file for t+1 | **Completed bars through close of t only** |
| t+1, 08:57–09:47 (`run_capture.cmd`) | Pre-open/opening quote snapshots for order instruments, holdings and universe (raw, checksummed) | live quotes |
| 09:00–09:05 | Pre-open: market and limit orders accepted (**since 2026-09-07; secondary sources: Rupeezy, Tradejini, Zerodha TradingQnA, Upstox docs — NSE primary page not retrieved**) | — |
| 09:05 → random close 09:08–09:10 | Limit orders only | — |
| 09:10–09:12 | Order matching at the single equilibrium price (max matched qty → min imbalance → closest to previous close); market orders matched first | — |
| 09:12–09:15 | Transition | — |
| 09:15 | Normal market opens; official open = auction price (or first trade if no price was discovered) | — |
| 09:15 (t+1) | **Reference simulated fills** at the official open: sells, then buys (C0-R-X: only gate-approved orders, determined the following morning when evidence is evaluated) | — |
| t+2, 07:45 | Records for session t+1 written (end-of-day reconciliation happens here; positions marked at the t+1 close) | — |

**Distinctions:**
- **Verified:** the official open equals the first traded 1-minute price in 99.6 % of 512 historical fills. The 09:15 one-minute bar contains the auction volume.
- **Unverified exchange rules:** the 2026-09-07 pre-open timings above.
- **Broker-specific:** some brokers convert market orders to protected limit orders and reject after their own cut-off. Not applicable to the paper system.

**Planned execution session does not occur** (unexpected holiday, no data):
- Nothing is decided or executed. Orders apply to the **next session that has data**.
- An `expected_session_missing` alert is raised when the calendar expected a session but data are absent.

**Incomplete trading day:** a session counts if the daily bar exists. Opening prices are used as provided.

**Window:** no order is generated for an execution session after 2026-12-31.

## I. Position sizing and portfolio allocation

| Item | Rule |
|---|---|
| Portfolio equity (close) | cash + Σ_i value_i, each holding marked at its latest valid close |
| Equity at the open | equity_open = cash + Σ holdings marked at the fill-session open (after the session's sells). |
| Target stock count | 20 |
| Weight per new buy | 1/20 = 5 % of equity_open |
| Buy amount | `amount = min(weight × equity_open, cash)` |
| Minimum buy | skip if `amount < 0.2 × equity_open / 20` (1 % of equity_open) |
| Costs (reference) | `cash -= amount`; position value = `amount × (1 − 0.00225)`. Sell proceeds = `value × (1 − 0.00225)` |
| Kept positions | not resized (drift) |
| Industry | ≤ 6 names per industry at selection; weights are not capped |
| Exposure | ≤ 100 % (cash ≥ 0) |
| Leverage | none |
| Fractional shares | **Reference accounting uses fractional shares (values).** Paper orders use whole shares |
| Whole-share order quantity | BUY: `qty = floor(weight × equity_at_decision_close_₹ ÷ close_t)`. SELL: all shares held (`floor` when ≥ 1 share; a sub-1-share holding cannot form a valid order and is flagged) |
| Minimum order quantity | 1 share; `qty = 0` ⇒ order **rejected** (`zero_or_negative_qty`), logged, not sent to capture |
| Rebalance threshold | none for weights |
| Leftover cash | stays in cash (0 % return in reference results) until a later buy uses it |
| Paper capital | ₹10,00,000 (notional, for quantities and cost estimates) |

**Worked example (illustrative, fresh book):**
- Equity ₹10,00,000, all cash. Slot = ₹50,000.
- The candidate's decision-day close is ₹520.00; whole-share qty = floor(50,000 / 520) = **96**.
- Reference accounting at a ₹525.00 open: amount = ₹50,000, cost ₹112.50, position value ₹49,887.50 (fractional 95.0238 shares).
- The whole-share paper order is 96 shares = ₹50,400.00 + fees. **The reference ledger and the order list therefore differ by rounding. This is a known, documented limitation.**

## J. Rebalancing logic

| Item | Rule |
|---|---|
| Frequency | every 5 trading sessions |
| Schedule anchor | t_start = the book's day 0 (paper: **2026-11-13**; historical research: 2025-04-01, session index 62) |
| Decision sessions | every session t ≥ t_start with (t − t_start) mod 5 = 0, counted in panel sessions |
| Phase | fixed by the anchor; there is no choice of phase. The phase matters: historically the five possible phases of C0-R gave 43.5–54.0 % total return |
| Evaluated positions | all holdings at every decision |
| Existing holdings | kept iff rank < 40 |
| Replacements | §E walk |
| Order sequence at next open | sells → buys (rank order) |
| Sell proceeds | available to the same session's buys |
| Drift | not corrected |
| Non-rebalance sessions | no selection activity; only pending sells are retried |
| Missed rebalance | A decision cannot be "made up". If the paper run is blocked or late, the book is replayed deterministically from day 0 once data and gates are valid, so the decision is computed from the data that were available for that session. Real orders could not have been placed in the meantime |
| Idempotency | Rerunning a session reproduces identical records (immutable files; a differing recomputation is a `record_conflict` incident, never an overwrite). The orders file is written once per decision session. A run lock refuses concurrent duplicates |

```python
def rebalance_cycle(book, t):            # at the close of session t
    if (t - book.t_start) % 5 != 0:
        return
    res = select(t, book.holdings)       # §E
    if res is None:
        return                           # <20 scores: skip everything
    sells, kept, new = res
    book.pending_sells = sells           # replaces older pending sells
    book.pending_buys = [(i, 1/20) for i in new]

def next_open(book, t1):
    execute_sells(book, t1)              # full exits; no open -> stay pending ; C0-R-X: only 'likely'
    mark_to_open(book, t1)
    execute_buys(book, t1)               # §F ; C0-R-X: only 'likely'
```

## K. Execution rules

| Layer | What it is | Status |
|---|---|---|
| 1. Frozen backtest / paper accounting convention | Fill at the **official open** of the next session, full quantity, 0.225 % cost per side; sells before buys; missing open ⇒ sell pending, buy dropped; **plus the evidence gate** | Frozen; theoretical (an observed price, not an observed fill) |
| 2. Research execution simulation (Phase 8) | Auction-size bounds from the 09:15 one-minute bar; post-open participation-limited fills (5–20 % of minute volume, typical price ± estimated half-spread, buys cancelled after 30 min, sells carried); delays; random non-fills | Research estimates; spreads are statistical estimators, **not quotes** |
| 3. Actual broker/exchange execution | Whether a pre-open market order would fill, at what price, with what queue priority | **Not verified. No order has ever been placed** |

| Topic | Rule / evidence |
|---|---|
| Intended order type (real-world equivalent, not authorized) | Pre-open MARKET order entered 09:00–09:05 IST (market orders not accepted after 09:05 per the 2026-09-07 rules) |
| Post-open fallback (research guidance) | If the auction fill is missed, use a post-open market order: about +16.6 bp vs the open at ₹10 L. **Do not cancel:** cancelled buys historically missed about +77 bp over 5 sessions |
| Partial fills | Reference: none. Research engine: remainder pending (sells) or dropped (buys) |
| Pending orders | Sells: retried every session until filled or replaced by the next decision. Buys: valid for one session only |
| Liquidity | Up to ₹1 Cr, 95th-percentile order ≈ 1 % of first-30-minute traded value; at ₹10 Cr ≈ 10 % |
| Spreads | Charged tiered half-spread in the account-size model 0.025 / 0.05 / 0.125 % (ADV ≥ ₹100 Cr / ≥ ₹20 Cr / below); measured opening estimates median 2.5 bp (Abdi–Ranaldo on 1-minute bars). No historical quotes exist |
| Market impact (research model) | 1.0 × σ_daily × √(order value ÷ ADV); uncalibrated |
| Brokerage / statutory (research model) | brokerage ₹0 or ₹20 per order; STT 0.1 % both sides; NSE 0.00297 %; SEBI 0.0001 %; GST 18 % on (brokerage + exchange + SEBI); stamp 0.015 % on buys; DP ₹18 per scrip per sell day. Rates as understood for 2025-26, **not verified against a broker contract** |
| Reference cost used in all frozen results | 0.225 % of traded value per side (includes an allowance for spread/slippage) |
| Order states (paper) | `intended` (orders file) → `rejected` (validation: zero/fractional/NaN qty, invalid price, non-INE key) or `captured` → `evaluated` (evidence) → `filled` (gate `likely`) / `not_filled` (any other status) |

### Evidence gate (C0-R-X) — exact rule
**Inputs** (from `results/phase8/capture/<date>/` snapshots, evaluated next morning by `auction_capture.evaluate`):
- `dec` = quote fields of instrument i in the **last snapshot whose label ≤ 09:05:00**. With the frozen schedule that is the 09:04:30 snapshot.
- `final` = fields in the **first snapshot with label in [09:12:00, 09:15:00)**, i.e. 09:12:30.
- `q` = the intended whole-share quantity of the C0_R_X order in `orders/<date>.json`, sized at ₹10 L paper capital.
- `stale` = |server `timestamp` of the quote − snapshot receive time| > **120 s**, or the timestamp is missing/unparseable.

**Decision table** (evaluated top to bottom; first match wins):

| # | Condition | Status | Simulated fill? | Buy | Sell |
|---|---|---|---|---|---|
| 1 | no `dec` (no snapshot before the cutoff, capture not run, API failed, instrument absent) | `unobserved` | NO | dropped | pending, retried next session |
| 2 | `dec` stale | `stale_quote` | NO | dropped | pending |
| 3 | `indicative_equilibrium_price` ≤ 0 or missing, or `indicative_equilibrium_quantity` ≤ 0 or missing | `no_auction_indicated` | NO | dropped | pending |
| 4 | `indicative_imbalance_quantity_market` missing or ≠ 0 (sign convention undocumented) | `uncertain_market_imbalance` | NO | dropped | pending |
| 5 | q > 0.10 × `indicative_equilibrium_quantity` | `uncertain_size` | NO | dropped | pending |
| 6 | `final` present and `final.volume` ≤ 0 | `no_auction_final` | NO | dropped | pending |
| 7 | `final` present and q > 0.10 × `final.volume` | `uncertain_size` | NO | dropped | pending |
| 8 | otherwise | **`likely`** | **YES, at the official daily open** | opened | closed |

```python
def gate(q, dec, final, stale):
    if dec is None: return "unobserved"
    if stale: return "stale_quote"
    if (dec.iep or 0) <= 0 or (dec.ieq or 0) <= 0: return "no_auction_indicated"
    if dec.imbalance_market is None or dec.imbalance_market != 0: return "uncertain_market_imbalance"
    if q > 0.10 * dec.ieq: return "uncertain_size"
    if final is not None:
        if (final.volume or 0) <= 0: return "no_auction_final"
        if q > 0.10 * final.volume: return "uncertain_size"
    return "likely"
fill = (gate(...) == "likely")              # fill price = official open of that session
```

**Assumptions and limits:**
- `final.volume` at 09:12:30 is assumed to equal the auction's matched quantity.
- The `timestamp` field is the server response time, so it detects delayed responses, not unchanged auction values.
- A `likely` status means only that the order was small relative to observed auction interest. **It is not evidence of an actual fill.**
- Every non-fill raises one `fill_not_assumed` alert per (date, instrument), and every evidence record is appended to `results/phase8/execution_evidence.jsonl` with observed fields, estimates and the classification kept separate.

## L. Risk management

| Control | Present? | Detail |
|---|---|---|
| Max positions | YES | 20 |
| Industry concentration | PARTIAL | ≤ 6 names per industry at selection only; no weight cap; drift allowed (max observed 37.9 %); `"Other"` is one bucket |
| Exposure | NO active control | fully invested whenever ≥ 20 names qualify; cash only from unfilled slots/rounding |
| Cash allocation | none beyond the above | — |
| Leverage | NONE | cash ≥ 0 |
| Volatility targeting | **NOT USED** | — |
| Drawdown monitoring | REPORTING ONLY | drawdown since day 0 is recorded daily; **no drawdown-triggered action** |
| Stop-loss / liquidation | **NOT USED** | — |
| Market gap exposure | UNMITIGATED | Up to 6 sessions from a shock to the first possible trade, and a uniform market fall does not change ranks. Hypothetical −10 % gap with 1–2 %/session continuation: about −15 % to −20 % for C0-R before any reaction |
| Momentum-factor risk | UNMITIGATED | momentum beta ≈ 0.8–1.05; hypothetical −20 % momentum shock ≈ −16 % (C0-R) |
| Correlation risk | UNMITIGATED | worst historical day −4.3 % (C0-R); ×2 stress −8.5 % |
| Illiquidity / suspension | PARTIAL | top-300 ADV filter; a suspended holding cannot be sold until it has an open (hypothetical 20-session suspension + −30 % reopen: −1.8 to −8.5 points) |
| Operational failure | YES (fail-closed) | integrity, completeness, state, engine-reconciliation gates; any failure ⇒ no new decision, previous state preserved, incident logged |

**Strategy exit vs monitoring alert:** alerts never trade. Only §G rules trade.

**Historical observations (retrospective, research-exposed, 2025-04-01 → 2026-11-13, reference costs):** No history: the gate needs prospective auction snapshots, which do not exist before 2026-11-16. Historical analogue (bar-volume bounds, not observations): 46–100 % of C0-R orders at ₹10 L would be 'likely' (central 86.6 %).

**Hypothetical stresses (not forecasts):** see the table above.

**C0-R-X-specific risk (simulation):** non-filled buys leave cash, so the book may be under-invested relative to C0-R. Non-filled sells keep risk on until evidence permits the exit. The simulated book is not a risk control: it measures execution realism.

## M. Market-regime behaviour

| Question | Answer |
|---|---|
| Detects market regimes? | **NOT USED** |
| Uses NIFTY trend? | **NOT USED** (NIFTY 50 only defines the session calendar and is a reporting benchmark) |
| Uses India VIX? | **NOT USED** |
| Uses breadth? | **NOT USED** |
| Changes parameters across regimes? | **NOT USED**: all parameters are constant |
| Reduces exposure in unfavourable markets? | **NOT USED** |
| Automatic regime switching / self-modification | **NOT USED.** Rules never change themselves; any change is a new version |

## N. Failure and edge-case handling

| Case | Behaviour | Class |
|---|---|---|
| Missing candle for an instrument on t | Not eligible on t; holding marked at last price; sell (if any) waits for an open | deterministic rule |
| > 2 % of (universe ∪ holdings) missing the new session | **No decision**; previous state preserved; `incomplete_market_data` incident | fail-closed |
| Stale daily data (session expected by calendar but absent) | No decision; `expected_session_missing` alert | deferred |
| Invalid instrument in universe (non-INE, fund) | integrity `classification` fails → decision blocked | fail-closed |
| Incomplete liquidity window (< 50 values) | ADV undefined → not eligible | deterministic |
| Zero volatility (σ42 = 0) | score ±∞/undefined; undefined ⇒ unranked; **±∞ has no explicit rule** (never occurred) | **unresolved design requirement** (recommend fail-closed) |
| Undefined momentum score | unranked (sold if held, at a rebalance) | deterministic |
| Corporate-action ambiguity (> 40 % move) | ineligible t … t+5; held position takes the move | deterministic |
| Corporate-action table missing | integrity fails → blocked | fail-closed |
| API failure (calendar) | cached holiday list, else weekday calendar; alert | degraded |
| API failure (quotes) | snapshot stored as failed; nothing fabricated; gate → `unobserved` → no fill | simulated non-fill |
| No opening auction / no price discovered | official open = first normal-market trade (exchange rule); reference fill uses the official open as published; gate → `no_auction_indicated` → no fill | simulated non-fill |
| Missing opening price | sell pending (retried), buy dropped | deterministic |
| Thin order book / thin auction | reference: no effect; gate: `uncertain_size` → no fill | — |
| Partial fills | reference: none; research engine: sell remainder pending, buy reduced | — |
| Duplicate execution attempts / duplicate runs | run lock refuses; registry + immutable records make reruns no-ops; at most one execution per instrument per session | idempotent |
| Insufficient cash | buy amount capped at cash; skipped if < 1 % of equity_open | deterministic |
| Sector-cap conflict | candidate skipped; walk continues | deterministic |
| Portfolio-state corruption / replay mismatch | `inconsistent_state` → blocked; state files untouched | fail-closed, manual review |
| Engine disagreement (sim5 vs xsim > 1e-9) | blocked | fail-closed |
| Suspended holding | marked at last price; unranked at the next rebalance → sell pending until an open exists | deterministic |
| Pending sells at a new decision | replaced by the new sell list | deterministic |
| Scheduled rebalance interrupted (crash) | rerun; state verified; capture resumes without duplicating snapshots | idempotent |
| Fewer than 20 valid scores | whole decision skipped | deterministic |
| Holding count still 20 at buy time (unfilled sell) | remaining buys skipped | deterministic |
| Zero-share whole-share order | rejected, logged; reference ledger unaffected (documented discrepancy) | logged |
| Special session (Muhurat, weekend budget day) | counted as a session if a daily bar exists | **realism unresolved** |
| Evidence missing because the capture task did not run | `unobserved` → no fill; alert once per (date, instrument) | simulated non-fill |
| Sub-1-share holding | cannot form a valid sell order → no evidence → stays pending (only possible at very small capital; at ₹10 L buys with qty 0 never get evidence, so such holdings do not arise) | unresolved edge, documented |

## O. Complete trading algorithm

```python
# Runs each trading morning (07:45 IST) for the last completed session T. Decisions use data <= close of T only.
def daily_run(today):
    lock("decide")                                         # refuse duplicates
    T_expected = last_calendar_session_before(today)
    evaluate_execution_evidence(T_expected)                # gate inputs for fills at T_expected's open
    refresh_daily_bars(until=T_expected, cap="2026-12-31")
    if missing_fraction(T_expected, universe_prev | holdings) > 0.02:
        return block("incomplete_market_data")             # previous state preserved
    if not rebuild_panel_from_db_matches_cache(): return block("panel_check")
    data = load_validated_panel(since="2025-01-01")        # 1. validated data
    if not all(integrity_checks(data)): return block("validation")
    U = {t: eligible_universe(t) for t in sessions}        # 2. universe (§B)
    S = {t: scores(t, U[t]) for t in sessions}             # 3. signals (§D)
    book = replay_book(start=DAY0, capital=CAPITAL, fill_gate=evidence_status)   # 4-15
    verify_state(book)                                     # stored state == replay, else block
    write_immutable_records(T)                             # 16. audit + monitoring
    write_orders_file(next_session(T), validated_orders()) # intended whole-share orders
    save_state(); append_hash_chained_log(); mark_done("decide", T)

def replay_book(start, capital, fill_gate):
    book = Book(cash=capital)
    for t in sessions_from(start):
        # 12-14 execution at the open of t (orders decided at the close of t-1)
        for i in list(book.pending_sells):
            if open[t][i] is None or fill_gate(date[t], i, 'SELL') != 'likely': continue   # stays pending
            book.cash += book.value_at_open(i, t) * (1 - 0.00225); book.remove(i)
        book.mark(open, t)
        eq_open = book.equity()
        for i, w in book.pending_buys:                     # rank order
            if len(book.holdings) >= 20 or i in book.holdings or open[t][i] is None: continue
            amount = min(w * eq_open, book.cash)
            if amount < 0.2 * eq_open / 20: continue
            if fill_gate(date[t], i, 'BUY') != 'likely': alert('fill_not_assumed'); continue
            book.cash -= amount; book.add(i, amount * (1 - 0.00225), mark=open[t][i])
        book.pending_buys = []
        book.mark(close, t)                                # 15. equity at close (last valid price if missing)
        # 6-11 decisions at the close of t
        if (t - start) % 5 != 0: continue
        res = select(t, book.holdings)                     # §E (None if < 20 scores)
        if res is None: continue
        sells, kept, new = res
        book.pending_sells = sells
        book.pending_buys = [(i, 1 / 20) for i in new]
    return book
```

Rounding rules:
- Reference accounting has no rounding (floating point).
- Order quantities are `floor()` to whole shares at the decision close.
- Ranks are exact float comparisons with instrument_key tie-break.

## P. Worked trading examples (all prices and quantities ILLUSTRATIVE, not historical trades)

**Example 1 — new entry.**
- **Decision session:** 2026-11-20 (a scheduled rebalance).
- **Stock X:** in U_t (ADV ₹180 Cr, H = 230, valid bar, not masked, ISIN INE…). close_t = ₹520.00, close_{t-63} = ₹400.00, σ42 = 0.021, so **S = 1.79983**, rank 7. Not held; its industry has 2 kept names (< 6). The book keeps 15 names, so 5 slots are open, and X is the 3rd successful pick of the walk.
- **Orders file (07:45 on 2026-11-23):** BUY X, weight 0.05, qty = floor(0.05 × 10,00,000 / 520) = 96.
- **09:04:30 snapshot:** IEP ₹524.50, IEQ 41,200, market imbalance 0, server timestamp fresh. 96 ≤ 0.10 × 41,200 = 4,120. At 09:12:30 the volume is 39,880, and 96 ≤ 3,988.
- **Status `likely`** → simulated fill at the official open ₹525.00: amount = ₹50,000, cost ₹112.50, value ₹49,887.50.

**Example 2 — exit and replacement.**
- **Holding Y:** at the next rebalance (2026-11-27) Y's score falls to 0.41, rank 52 (≥ 40), so **SELL Y**.
- **Holding Z** sits at rank 38 (< 40), so it is kept, even though new top-20 names exist.
- **Replacement walk:** the ranks 0–21 names are either held or in an industry that already has 6 names, so they are skipped. The first free candidate is W at rank 22, so **BUY W**.
- **At the 2026-11-30 open:** sell Y for the full position at the official open, net of 0.225 %. The proceeds join cash, then W is bought with min(1/20 × equity_open, cash).
- **C0-R-X:** the sell executes only if Y's SELL evidence is `likely`; otherwise Y stays held and pending, with the same check the next session. W's buy needs its own `likely` status.

**Example 3 — thin auction, uncertain fill.**
- **BUY T:** qty 96. At 09:04:30, IEP ₹310.20, IEQ 700, market imbalance 0. 96 > 0.10 × 700 = 70, so **`uncertain_size`** → **not filled**.
- **Consequences:** the buy is dropped, an alert is logged, and the slot stays in cash until the next rebalance (5 sessions later). C0-R, by contrast, records the fill at the official open.
- **Variant — sell with market imbalance:** SELL U, IEQ 25,000, `indicative_imbalance_quantity_market` = −1,800 → **`uncertain_market_imbalance`** → U stays held and pending; the next session needs new evidence.
- **Variant — capture task not run:** every order → `unobserved` → nothing fills that session.

## Q. Strategy verification

| Item | Value |
|---|---|
| Authoritative code | §A table |
| Fingerprint | `3d1228a7750225ed` |
| Config version | `124623e3a4b1db81` (frozen sources unchanged as of 2026-11-14) |
| Independent implementation | `trading-desk/trading_strategies/verification/spec_impl.py` (written from this document; no research-engine imports) |
| Comparison script | `trading-desk/trading_strategies/verification/verify_specs.py` → `verification_report.json` |

**Verification results (run 2026-11-14, data 2025-01-01 → 2026-11-13) — ALL PASS:**
1. Eligible universe identical in every session (0 mismatching cells).
2. Score identical in 100 % of cells; no ±∞ score inside the universe.
3. C0-R orders identical: 512 / 512 (session, instrument, side).
4. C0-R equity difference 0.0; final holdings and pending orders identical.
5. C1-R exposure difference ≤ 1.5e-15; equity difference ≤ 8.9e-16.
6. C2-S aggregate equity difference ≤ 8.9e-16.
7. C0-R-X gate: 1,152 / 1,152 fixture cases agree with `auction_capture.classify_auction`.
8. Parameters and gate constants match the code; the four fingerprints match `paper8.fingerprints()`.
9. C0-R-X portfolio mechanics under a deterministic synthetic gate: equity difference ≤ 1.6e-15.
10. Whole-share quantities of the 80 issued day-0 orders follow the §I formula exactly.

**Expected outputs:**
| Case | Expected | Test |
|---|---|---|
| C0-R-X | no historical evidence exists; verification is the gate decision table (1,152 fixture cases) and the portfolio mechanics under a synthetic gate | `verification/verify_specs.py` checks 7 and 9 |
| sim5 ≡ xsim | max equity difference ≤ 1e-12 | `tests/test_phase8.py::test_xsim_reproduces_sim5` |
| research ≡ paper engine | identical orders, cash, holdings, equity | `phase7/reconcile.py` |

**How to confirm an independent implementation:**
1. Load the panel (2025-01-01+).
2. Reproduce U_t and S_t for every session.
3. Run the book from the anchor.
4. Compare session-by-session orders, holdings (names and values to 1e-12), cash and equity with `verify_specs.py`.
5. Compare the whole-share order list of the latest orders file.

**Required implementation tests:**
- universe tie handling;
- σ = 0;
- < 20 scores;
- pending sell replacement;
- unfilled sell blocking buys;
- minimum buy;
- whole-share zero quantity;
- special sessions;
- the 2 % completeness gate.

**Known discrepancies** (none changed any historical result):
- ADV ties: column order in code vs key order in the written intent.
- Bad-print mask: t−5 in code (look-ahead, never fired) vs t … t+5 in the written rule.
- ISIN rule: the code excludes `INF`; the gate requires `INE`.
- Fractional reference ledger vs whole-share orders.
- Phase-6 text overstated the tiered half-spread by 2× (results used the charged values).

## R. Research status and limitations

| Item | Status |
|---|---|
| Historical window | 2025-01-01 → 2026-11-13 (research start 2025-04-01; first effective decision 2025-04-08) |
| Evaluation status | **Research-exposed.** The whole period was inspected across phases; no independent out-of-sample data exist |
| Paper-trading readiness | Forward paper-trading ready as an EXPLORATORY execution-validation shadow. 0 forward sessions processed as of 2026-11-14. Requires the pre-open capture task to run. |
| Prospective sessions observed | **0.** Day 0 = 2026-11-13; at most 32 forward sessions fit before 2026-12-31. The pre-registered 250-session validation **cannot** be completed inside the mandate and is not weakened |
| Execution uncertainty | Opening-auction fills are inferred from bar-volume bounds (central: 87 % of C0-R orders at ₹10 L, 70 % at ₹1 Cr would be small vs the auction), **not observed** |
| Path sensitivity | Trivial execution differences move single-path results by about ±4 points; the rebalance phase by up to 11 points (C0-R) |
| Survivorship | Delisted stocks absent from the vendor master: effect unknown |
| Corporate actions | No demerger feed; price-based mask; dividends not credited (≈ 0.6 %/yr understatement of EW-relative excess) |
| Industry data | Static NIFTY-500 snapshot; `"Other"` bucket |
| Attribution | About 81 % of variance explained by market, breadth and momentum; alpha t = 1.81 (not significant) |
| Live-capital approval | **NOT APPROVED.** Retrospective profitability does not imply future performance. Live use would require explicit authorization, an extended data window, ≥ 250 prospective sessions with an unchanged config version, a significantly positive factor-adjusted return net of measured costs, and verified real execution |
