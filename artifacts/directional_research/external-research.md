# External evidence and research implications

Checked 9 November 2026. Broker documentation, academic findings and trader anecdotes have different evidential roles. None establishes a profitable NIFTY options strategy for this account.

## Upstox history is not limited to seven trading days

Upstox V3 documents minute/hour history from January 2022. A request for 1–15 minute candles is limited to one month; larger minute intervals and hourly bars allow a quarter. Daily history is documented from January 2000, with a decade per request. These are endpoint capabilities, not a guarantee of complete coverage for every instrument. [Upstox Historical Candle Data V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).

The account was actually tested: January 2025 five-minute NIFTY candles returned successfully. Twenty-three monthly requests from January 2025 through 8 November 2026 returned 34,386 raw bars. A separate request returned 2,442 daily observations from January 2017 through 8 November 2026. The frozen local files and manifests establish what was received, independently of the general documentation.

Expired derivatives use separate discovery and candle endpoints. The expiry-discovery documentation describes up to six months of expired dates and error `UDAPI1149` for missing Upstox Plus access. The account returned that exact error with HTTP 401. The expired candle endpoint describes OHLC, volume and OI; this is not a historical bid/ask feed. [Get Expiries](https://upstox.com/developer/api-documentation/get-expiries/), [Expired Historical Candle Data](https://upstox.com/developer/api-documentation/get-expired-historical-candle-data/).

Ordinary historical candles for currently listed options did work. A deliberately limited availability probe retrieved November 17, 2026 25,000 CE and PE history. Many bars were absent or had zero volume. The strike was selected using the latest observed spot level, so this is a data-access diagnostic with hindsight selection, not a historical ATM strategy test. Paying for an entitlement would not by itself supply years of intraday quotes; verify depth and retention before choosing a data source.

## Indian contract details must come from dated records

NSE currently specifies Tuesday weekly expiries and the last Tuesday for monthly NIFTY options, adjusted to the previous trading day when Tuesday is a holiday. It directs users to the dated contract file for applicable lot sizes. A historical backtest must load each actual expiry, instrument identity and lot size rather than apply today's calendar or lot size to every year. [NSE NIFTY 50 contract specifications](https://www.nseindia.com/static/products-services/equity-derivatives-nifty50).

The intraday lab's 15:10 exit is a conservative research boundary. It is not a claim about the current exchange closing auction, derivatives close, or an optimal liquidation time. Short/special sessions are explicitly excluded from that lab; the daily study includes published special-session observations.

## Why price direction is only the first layer

Time decay reduces an option's theoretical time value when other pricing inputs are unchanged. Its rate varies with moneyness and time to expiration; it should not be modeled as a constant penalty across all weekly contracts. [Options Industry Council: Theta](https://www.optionseducation.org/advancedconcepts/theta).

Implied-volatility changes also affect option prices. A correct directional forecast can lose money if the underlying move is too small, too slow, or accompanied by falling implied volatility. [Options Industry Council: Vega](https://www.optionseducation.org/advancedconcepts/vega).

Research inference: compare exact premium outcomes for the same underlying signal, timestamp and fixed holding rule across expiry/moneyness buckets. First compare near-ATM contracts, modestly ITM contracts, nearest eligible weekly expiry and the monthly expiry. Greek-based approximations can explain a result; they cannot substitute for actual tradable prices. Nearest weekly and monthly can be the same instrument in monthly-expiry week, so deduplicate them.

## Academic evidence: useful hypotheses, not a transferred edge

Gao, Han, Li and Zhou's 2018 study finds that the first half-hour return predicts the last half-hour return in historical S&P 500 ETF data, with stronger patterns under certain volatility, volume and news conditions. This motivates testing intraday continuation and its conditional behavior. It does not demonstrate that a different rule, different Indian trading window, or weekly option purchase will work. Our afternoon trend test is a related hypothesis, not a replication of that paper's specification. [Market intraday momentum, Journal of Financial Economics](https://www.sciencedirect.com/science/article/pii/S0304405X18301351), [author university publication record](https://profiles.wustl.edu/en/publications/market-intraday-momentum/).

Bailey and coauthors explain how searching many strategies can create impressive false discoveries, and why ordinary holdout methods can be unreliable when research repeatedly revisits data. This informs the full experiment ledger, chronological selection, disclosure of earlier October exposure, and refusal to pick a new winner from the final-period grid. We have not computed that paper's PBO statistic; block-bootstrap intervals here are conditional and are not a multiple-testing correction. [The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).

## What trader discussions contribute

One self-described experienced trader discusses higher-timeframe direction, option-chain context and strikes around 0.4–0.6 delta. A reply emphasizes actual spreads and liquidity. These are sensible hypotheses for contract selection and execution tests; neither identity nor profitability was verified. The present research does not assume that the suggested delta band is optimal. [IndianStreetBets discussion: simple rules to trade options](https://www.reddit.com/r/IndianStreetBets/comments/12t4jwb/simple_rules_to_trade_options_based_on_my_5year/).

Another trader describes ATM/ITM buying with EMA9/21, price action and RSI, while explicitly reporting difficulty achieving consistent profits. This is a useful counterexample to treating several confirming indicators as sufficient evidence. The EMA-filtered project signals were therefore replayed rather than accepted on anecdote. [IndianStreetBets: option-buying practices and experiences](https://www.reddit.com/r/IndianStreetBets/comments/18ueg4w/option_buying_best_practices_and_experiences/).

No Reddit user was contacted. No claims about win rates or profits from these discussions were incorporated as measured evidence.

## Implications for the next experiment

Use a small frozen rule set, real information timestamps, exact contracts and conservative fills. Treat OI/PCR, IV, sectors and macro data as additions whose incremental contribution must be tested. A market-state classifier may return “insufficient evidence” and no trade. More indicator agreement, a popular story about institutional order flow, or a larger parameter search does not eliminate that state.
