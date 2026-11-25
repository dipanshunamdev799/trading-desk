# Execution costs and uncertainty

The archive can bound some observable trading frictions. It cannot reveal actual broker fills, queue position, hidden liquidity, cancellations, market impact, short-sale availability or a guaranteed execution delay. No order endpoint is called. All numbers below describe retained quotes, not realized trading profits.

## Measured archive evidence

The 16-stock-day replay contains 348,484 updates. Stock-day median spreads range from 0.625 to 3.682 bps. A narrow spread alone does not imply sufficient order capacity or continuous data.

For HDFCBANK on 13 November 2026, at eligible 30-second observation points:

| Approximate notional | Both sides support full modeled size | Median immediate round-trip quote cost, conditional on full depth |
|---|---:|---:|
| Rs100,000 | 96.89% | 10.48 bps |
| Rs500,000 | 22.26% | 8.12 bps |
| Rs1,000,000 | 1.47% | 8.12 bps |

Bounds consume at most 10% of displayed quantity at each observed level and include estimated fees. Larger-size costs appear lower partly because brokerage is capped and because almost all insufficient-depth observations are excluded from that conditional median. This is selection, NOT evidence that Rs1 million trades are easier or cheaper to fill. Insufficient depth remains unfilled/partial; no full-size return is invented.

Latency scenarios use the FIRST available quote at/after 100, 500, 1,000 and 5,000 ms. The first three require an observation within another 200 ms; the last allows another second. In the HDFCBANK example, many subsecond scenarios identify only about 23-38% of observations. Sparse updates cannot establish a precise 100 ms fill price. Five-second scenarios generally have better observation coverage, with different economic meaning. Detailed per-day distributions and missingness are in `detailed-quality.json`.

## Frozen quote-bound model

Long entries walk asks and exits walk bids; shorts reverse those sides. At most 10% of displayed size per level is available to the model. Fill quantity is whole cash-equity shares, at most 1% of the preceding observed 60-second volume, no leverage and within available capital. The initial diagnostic uses at most approximately Rs100,000 notional; funded-shadow sizing uses its own shared capital and risk budgets.

Bid/ask execution already includes spread. Do not add a second half/full-spread charge. Estimated Upstox basic-plan brokerage and NSE intraday charges reuse the frozen V1 fee function: brokerage min(Rs20, 0.1% turnover), combined exchange/IPFT 0.00307%, SEBI 0.0001%, GST 18% on brokerage/exchange/SEBI, sell-side STT 0.025%, buy-side stamp 0.003%. These are estimates before contract-note rounding and not proof of a historical account plan. See the original `SOURCES.md` and current [Upstox charges](https://upstox.com/brokerage-charges/).

The primary hypothetical bound adds one adverse bp per side BEYOND observed quotes, explicitly an assumption. Report three and five bps per-side adverse scenarios; five rather than one reduces a round trip by approximately eight bps. It does not turn assumed impact into measured impact. Limit-order fills are not assumed: without order/queue data, a touched price cannot establish a fill probability. No limit-order strategy return is generated.

Intent time follows the one-second shared selection window. Entry is the first valid fresh quote available at least one second later, with at most one additional second of waiting; otherwise unfilled. A greater-than-0.3% adverse chase is rejected. Actual entry-price changes must still fit cash and stop-risk budgets. Partial next-quote depth is unfilled. Exits use the first qualifying observed stop/target/time/thesis quote, not the stop price if the market gaps through it. Missing or partial exit liquidity reserves capital and halts new entries rather than realizing a convenient price.

## Economic gates and risk accounting

Shared hypothetical capital starts at Rs1 million. At most one position/pending entry, three filled entries daily, no same-symbol reentry, at most 0.5% equity initial risk and a 1% opening-equity daily realized-loss budget. Whole-share sizing includes estimated exit charges and an adverse allowance. Structural stops use observed 60-second extremes plus spread and must be 0.3-1% away. Targets are 1.5R, bounded to 0.75-1.5%; exit also occurs after 30 minutes, at/after 15:10 or following thesis failure. These assumptions are frozen research rules, not guaranteed loss caps during gaps.

Account/market eligibility, daily history, current exact listing identity and short-execution verification are separate gates. Current MIS listing does not satisfy them. REST never inherits the streaming funded gate. Missing models, insufficient sessions or unproven expected net edge reject a candidate.

Using only the first 20 training sessions, calibration requires 200 complete fresh streaming matched-control bounds across ten days. Freeze the median daily cost and the 95th percentile of observed costs; uncertainty allowance = max(1 bp, p95 cost minus median daily cost). Expected net edge must exceed max(5 bps, twice that allowance). The allowance measures observed quote-cost dispersion, not full uncertainty about market impact or broker fills; prospective impact stresses and nonfill disclosure remain necessary. Evaluation data cannot be used to recalibrate it.

Track both EOD drawdown and intraday marked equity using executable-side quote bounds. During missing quotes, drawdown is unknown; a later priced mark cannot certify what happened inside a gap. Unpriced/unresolved exposure prevents qualification. A positive quoted simulation is research evidence requiring further validation, never an authorization to trade.
