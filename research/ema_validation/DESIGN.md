# EMA conditional validation protocol

Frozen 12 November 2026 before new randomization outcomes. Previous discovery and
diagnosis sources/artifacts remain read-only. All 2024–2026 dates are contaminated.
No optimization or candidate selection on this history is claimed.

Primary A/B/C/D hold relative-strength eligibility on: EMA vs randomized entries,
with vs without volatility expansion. A=EMA+RS+gate; B=random+RS+gate;
C=EMA+RS; D=random+RS. Supplementary four cells remove ONLY the RS eligibility
filter, preserving RS-based candidate ranking, to isolate that filter's effect.
They do not remove every use of momentum information from the frozen strategy.

Daily neutral split-unit closes c(s,t). SMA-seeded EMA20/50 use alpha=2/(n+1).
Bull cross: EMA20[t]>EMA50[t] AND EMA20[t-1]<=EMA50[t-1]. Stock close[t]/close[t-60]-1
must exceed NIFTY price-index close[t]/close[t-60]-1 for RS eligibility. Gate:
sample std(ddof1) of20 completed NIFTY daily simple returns divided by corresponding
60-return std >1.2. Incomplete/warmup observations cannot signal. All decisions
at completed close t; earliest execution next observed open t+1.

Actual account starts Rs1m, long cash, risk0.5% of pre-entry equity including planned
overnight fees/adverse stop fill, integer shares, initial stop=entry fill-2ATR14.
ATR14 uses SMA-seeded Wilder smoothing(alpha1/14) of true range. Fee-aware net2R
target, next-open exit after10 observed sessions. No trailing stop. Next-open fills
5bps adverse; adverse gaps stop at worse open, target no favorable gap; daily
both-hit stop-first. Ex-date economic dividend credit (not certified pay-date
buying power); corrected multi-component dividends and actual same-day taxes.
Original date-specific delivery schedule/flat brokerage retained; stress doubles
fees and uses10bps. No leverage/cash interest/capital-gains tax. Ten open positions,
20% per-name notional cap,30% per-sector cap on admission,1% lag20 median volume
participation, Rs5crore lag20 median turnover, correlation>0.8 versus any held name
rejects (previous60 returns, minimum40 finite pair observations). Prior60 stock
return descending, symbol alphabetical tie, determines candidate priority. No15%
drawdown halt in the frozen risk+correlation policy. Keep original cash and
corporate-action timing. Daily last research close liquidates for retrospective
comparisons; prospective engine must not force-liquidate merely because data ends.

Random controls:1000 fixed seeds 120260001..120261000. Per completed date choose
exactly K stock opportunities without replacement from eligible RS-on/off names,
where K is that day's EMA-cross count in the same eligible pool. This count is
known at decision close, not an eventual realized trade/return count. Random
uniform priorities are shared across gate/no-gate and RS-on/off cells for each
seed/date/stock. Gate is applied AFTER selection, so B/D have identical randomized
opportunities on expansion dates. EMA rank/cash rules remain unchanged. No seed is
selected. Preserve summaries/daily equity/cash/exposure/trades for all runs.
Exact executed trade/holding/exposure matching is impossible with independent
causal position paths; quantify mismatches, never force fills based on original
future exits. A conditional-date opportunity null, not an unconditional p-value
correcting earlier strategy discovery. Current frozen eligibility retains prior
future-completeness/survival bias; acknowledge rather than silently fix universe.

Primary horizon continuous11Nov2024–9Nov2026, plus final-six-month reset A/B/C/D
to reproduce prior account conventions. Secondary development/validation/final
attributions on continuous paths are not independent replications. Supplementary
RS factorial uses full horizon. Common-date circular10-session block bootstrap
3000 draws for fixed-portfolio and paired contribution contrasts; market-event
cluster summaries/leave-one-event-out replay, stock contributions and exclude
highest-PNL name replay. Conditional Monte Carlo p=(1+#null>=observed)/(1001).
Family-wise Holm adjustment on EMA gated, EMA ungated and gate interaction tests;
separate simultaneous bootstrap contrasts for EMA/gate/interaction/RS filter.
Seeds are not independent market histories; randomization ranks do not remove
post-selection bias or provide a tradable forecast.

Threshold robustness is diagnostic, not selection:1.1/1.2/1.3 and EWMA20/60
(alpha2/(n+1), bias-corrected variance) compare on development dates only. Freeze
1.2 unchanged for all final evaluation and prospective recording. Episodes are
maximal contiguous expansion sessions, additionally pooled into events separated
by fewer than10 non-expansion sessions; no future episode endpoint informs entry.
Retrospective episode attribution may use future endpoints solely for reporting.
Test fixed-rule exclusion of largest contributor and largest event; label these
post-outcome sensitivity tests, never revised candidates.

Benchmarks: official NIFTY50/500 TRI with previous-close-known strategy utilization
and conservative round-trip costs on allocation changes. Zero cash return. This
is an idealized exposure-timing control, not certified ETF execution. Sector TRI
control restricted to verified Bank/IT/Pharma mappings; leave unmatched sectors
unavailable. Add same-lag utilized frozen cohort equal-weight total-return proxy,
not a reconstructed rebalancing index. All limitations remain explicit.

Earlier historical universe feasibility: attempt dated official snapshots and
membership archives; do not backdate2024survivors. Prospective recorder starts
flat from12Nov2026 with configuration/source/input hashes, append-only completed
daily observations and deterministic state/journal output. No broker credentials,
live order routing, or invented future trades; no parameter changes.
