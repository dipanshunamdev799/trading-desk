# NSE cash-equity intraday momentum: primary-source research

Retrieved **15 November 2026 (Asia/Kolkata)**. This note documents data and execution constraints for research, not a claim that the supplied discretionary framework is profitable. No broker orders or database changes were made while preparing it.

## Historical data versus live observations

[Upstox Historical Candle Data V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) documents minute/hour history from January 2022. Minute intervals 1–15 require requests covering no more than one month; larger minute intervals allow one quarter. The returned candle fields are timestamp, open, high, low, close, volume and open interest. Daily history is documented from January 2000. These are availability bounds, not a guarantee that every stock/session is complete.

[Upstox Market Data Feed V3](https://upstox.com/developer/api-documentation/v3/get-market-data-feed/) documents live bid/ask prices and quantities at multiple depth levels, total buy/sell quantities, traded volume and timestamps. The normal Full subscription has documented instrument/connection limits; Full D30 is a separate subscription tier. Depth is a live observation, not a field in the historical-candle response.

**Research inference:** candles can support completed-bar momentum, cumulative traded-volume comparisons, an OHLCV-derived VWAP proxy and price-action tests. They cannot recreate historical active orders, queue position, cancellations, aggressor-side flow or contemporaneous spreads. A volume or candle-direction proxy must not be labelled observed order flow. A five-minute bar that crosses a trigger does not establish the order in which its high and low occurred.

## Cash-equity transaction-cost model

The [Upstox price schedule](https://upstox.com/brokerage-charges/) lists these ordinary equity-intraday charges:

| Component | Research rate |
|---|---:|
| Basic-plan brokerage | Lower of ₹20 and 0.1% of each executed order value |
| STT | 0.025% of sell turnover |
| Stamp duty | 0.003% of buy turnover |
| SEBI turnover fee | ₹10/crore of turnover |
| DP charge | None for ordinary same-day equity intraday |

The [Upstox brokerage calculator](https://upstox.com/calculator/brokerage-calculator/) explicitly describes GST as 18% of brokerage, exchange and SEBI charges. The schedule is current, not independent verification of every historical account's brokerage plan. Use it as a disclosed modeling convention; actual plan, order splitting, rounding and contract notes may differ. Investor income tax is not a transaction fee in this simulation.

The [NSE circular FA73061, dated 27 February 2026](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf) confirms combined cash-market transaction charges plus IPFT of **₹307/crore each side**, both before and after 1 March 2026. Before that date the split is ₹297 plus ₹10; afterwards it is ₹306.99 plus ₹0.01. The reallocation does not change the combined outflow. For a study beginning after 1 October 2024, use combined **0.00307% per side**, not that rate plus the former IPFT charge.

The [Upstox October 2024 revision notice](https://upstox.com/announcements/updates/revision-in-transaction-charges-from-1-october-2024/) provides the earlier dated fee-change context. A study extending before that effective date needs its prior schedule rather than silently using this combined rate for all history.

An implementable current-plan per-order estimate, with `v` denoting executed turnover in rupees, is:

```python
brokerage = min(20.0, 0.001 * v)
exchange_including_ipft = 0.0000307 * v
sebi = 0.000001 * v
gst = 0.18 * (brokerage + exchange_including_ipft + sebi)
stt = 0.00025 * v if side == 'SELL' else 0.0
stamp = 0.00003 * v if side == 'BUY' else 0.0
fee = brokerage + exchange_including_ipft + sebi + gst + stt + stamp
```

For illustration, buying ₹100,000 and selling ₹101,000 produces approximately **₹82.97** of these fees before slippage, using unrounded intermediate amounts. This is a calculation under the above assumptions, not a certified contract note. Short entries incur sell-side STT at entry and buy-side stamp duty at cover. A 1% gross target is not a 1% net account return. A useful stress is adverse slippage of 5, 10 and 20 basis points **per side**, rather than assuming the official bar open is executable without friction.

## Leverage and short-sale eligibility

[Upstox's NSE 500 leverage announcement](https://upstox.com/announcements/margins/enjoy-up-to-5x-leverage-on-intraday-trading-for-all-nse-500-stocks/) describes **up to** five-times intraday leverage and explicitly allows broker changes. Its page has inconsistent publication/body dates, so it is evidence of the conditional product offering, not a reliable historical daily margin archive.

[Upstox instruments documentation](https://upstox.com/developer/api-documentation/instruments/) describes `intraday_margin` and `intraday_leverage` in instrument data. Instrument files refresh daily; next-day files omit delisted instruments and expired contracts. A current instrument file cannot establish past listing, margin or tradability status.

[SEBI's 5 January 2024 short-selling framework](https://www.sebi.gov.in/legal/circulars/jan-2024/framework-for-short-selling_80448.html), reproduced in the [NSE Clearing circular CMPL60221](https://nsearchives.nseindia.com/content/circulars/CMPL60221.pdf), permits retail and institutional short selling, prohibits naked short selling and specifies delivery obligations at settlement. Its annexure identifies F&O-segment securities as eligible, and distinguishes institutional intraday restrictions and retail disclosure timing. These provisions do not certify that an arbitrary stock-day in our panel was available through Upstox's intraday product.

**Modeling consequence:** report long-only primary results separately from analytical long/short results unless dated short eligibility can be demonstrated. Treat constant 5x leverage as a sensitivity/scenario, not an observed historical entitlement. A failed short cover at a price limit must not become a fabricated end-of-day fill or an ordinary overnight position.

## Price bands, surveillance and intraday availability

[NSE price-band guidance](https://www.nseindia.com/static/products-services/equity-market-price-bands) lists daily bands of 2%, 5%, 10% and 20%. Securities with derivative products do not have those static daily bands, but operating ranges apply. Today's bands must not be backdated to every session.

[NSE Additional Surveillance Measures](https://www.nseindia.in/static/regulations/additional-surveillance-measure) uses measures related to price/volume variation and volatility. Surveillance can include narrower bands, periodic auctions and movement to trade-for-trade. ASM status alone is not a complete universal intraday-eligibility rule; stage and dated circular matter.

[NSE clearing and settlement guidance](https://www.nseindia.com/static/products-services/equity-market-clearing-settlement) says surveillance trade-for-trade obligations are gross: every deal produces settlement obligations. [Upstox's T2T explanation](https://upstox.com/learning-center/share-market/what-is-trade-to-trade-t2t-stocks/article-1885/) states that compulsory-delivery T2T securities are not ordinary intraday candidates.

**Research inference:** the eight-percent screen can disproportionately select stocks close to a ten-percent circuit and does not establish liquidity. Historical daily EQ/BE status, price-band files, surveillance changes, suspensions and broker MIS availability should be retained where obtainable. Without them, report eligibility as unverified and avoid calling paper fills executable. Flag persistent one-price/zero-range bars and missing exit bars; OHLCV alone cannot distinguish a locked order queue from a fillable market.

## Implications for the supplied framework

The user's description is a set of hypotheses, not a frozen algorithm or an audited tradebook. The screenshot does not supply complete entry/exit timestamps, position sizes, charges, losing sessions or a capital-denominator history.

For a causal test, an eight-percent mover must mean price change **already observed by the decision time** from the prior eligible close, not a stock selected because its eventual daily high/close moved eight percent. Today's eventual total volume must not be used to pass an earlier relative-volume screen. Rank simultaneous signals using information available then; enforce the two/three-trade daily cap in one shared chronological portfolio. Model next-bar entries, adverse opening gaps, stop-first ambiguous bars, integer shares, costs and portfolio cash limits. Separate threshold-continuation, pullback and exhaustion/fade variants before inspecting results; the trader's intuition and reading of active orders cannot be reproduced by candle data alone.
