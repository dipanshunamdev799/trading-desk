# Expanded strategy discovery: research design before simulation

The earlier broad index study tested 207 configurations; the later stock transfer
study tested 13 distinct selected variants, not the full stock strategy space.
This new experiment addresses that limitation rather than counting minor changes
as independent discoveries. It preserves the earlier studies and their failures.

## Discovery and hypotheses

MACD/PPO, EMA/adaptive averages, structural support/resistance, and hybrids are
separate hypothesis families. Indicator roles include entry, trend/regime filter,
exit, and stop placement. The companion discovery notes cite original research
and primary indicator documentation and define causal rules before simulation.

The motivating multiple-testing evidence is Sullivan, Timmermann and White's
technical-rule study and Bailey and Lopez de Prado's Deflated Sharpe Ratio:

- https://ideas.repec.org/p/fmg/fmgdps/dp303.html
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

These sources motivate controls, not an assertion that any indicator is profitable
in Indian equities. Large grids create opportunities to find lucky winners. A
larger experiment alone is not stronger evidence.

## Universe, resolution and scope

Seek a dated, point-in-time NIFTY500 universe at the beginning of the existing
November2024-November2026 test interval, deduplicating overlapping index groups.
Current instrument metadata may resolve historical identity but cannot choose
stocks by their subsequent survival or returns. Every unresolved/removed name
stays in the disposition ledger. If a dated universe cannot be obtained, disclose
the alternative and its bias rather than call it point-in-time.

The broad panel uses daily execution and daily/weekly indicators. The small
existing five-minute stock panel is available for a distinct resolution check.
Daily bars can conservatively resolve simultaneous stop/target touches only by
stop-first convention; they cannot establish the actual intraday sequence.
Unavailable volume-at-price and historical delivery-volume data must not be
invented. A recent price-volume histogram is not true volume profile.

Prices before November2024 provide warmup only for the starting2024 universe;
using those same selected names for a2020 investment universe would introduce
lookahead/survivorship selection. Longer-cycle claims require earlier dated
membership records. The evaluated interval and its cycle limitations remain
explicit even when the price cache extends further back.

## Sequential experiment stages

1. Freeze discovery families, parameter bounds, costs, universe rules and selectors.
2. Run a systematic coarse screen on development dates and development stocks.
3. Select useful parameter neighborhoods using development results only; refine
   neighboring values and predefined component interactions, retaining every loss.
4. Validate configurations without changing their rules; choose/freeze finalists.
5. Evaluate frozen finalists once on reserved dates and held-out stock groups.
6. Run predeclared cost, stop, boundary, regime and parameter-stability falsification
   checks; report evidence against a candidate as clearly as evidence for it.

Stock groups are deterministic by historical identity hash. A reserved cross-
section provides new companies, not a wholly independent market history. The
calendar's final dates overlap earlier project research, so a genuinely untouched
temporal holdout cannot be manufactured. New forward observations remain required.

## Chronology and execution contract

No unconfirmed pivot, unfinished week, or current day's eventual extrema can be
used before availability. Decisions use completed candles; entries fill next
tradable open. Stops use known price/ATR/structure at decision time and executable
entry risk. Gaps can exceed the intended risk budget. If stop and target both
touch in one daily candle, assume stop first. Limit targets receive no beneficial
gap improvement. Fees, taxes, adverse slippage and dividend/split entitlements
are explicit model inputs, not adjustments chosen after seeing winners.

Individual rule/stock research sleeves have integer shares, one position, cash
notional limits and configurable0.5%risk. A mean across independent sleeves is
not a pooled single-account portfolio. Any implemented pooled portfolio needs
explicit concurrent-position, sector and cash constraints and next-open ranking.
Liquidity filters must use lagged observations; quote depth, actual spreads,
historical volume adjustment and market impact cannot be certified from OHLCV.

## Statistical inference and ranking

Use chronological development/validation/final splits, rolling train/test folds,
cross-stock breadth, regime breakdowns and neighborhood stability. Keep zero-
trade configurations and all excluded stock identities visible. Measure daily
marked equity, netR, exposure, trade counts and cost stress; reject catastrophic
drawdown or inadequate samples before applying a balanced descriptive score.

Use a common-calendar block bootstrap across rule portfolios to preserve broad
market and cross-rule dependence. Approximate search-wide max-t/Reality-Check-
style controls are conditional diagnostics, not automatic evidence of an edge.
Where feasible add development-only CSCV/PBO and a correctly labeled DSR
diagnostic, disclosing IID and trial-count assumptions rather than presenting a
conditional probability as the probability that a strategy is truly profitable.

Top20 means a complete ranked candidate table with pass/fail status. If fewer
than20strategies demonstrate robust evidence, do not label the remainder robust.
No historical ranking authorizes paper workers, broker orders or live deployment.
