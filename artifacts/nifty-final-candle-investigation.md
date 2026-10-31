# NIFTY 50 final one-minute candle investigation

Investigated on 24 October 2026. The supplied chart matches the latest session, 23 October 2026. Times below are IST.

## Finding

The evidence strongly supports a closing-auction price update. The chart displays the transition from the last continuous-session index value to the auction-derived closing value as an ordinary one-minute candle. Calling this a bad upstream candle is not supported by the checks performed.

## Observed data

The direct Upstox V3 historical API, bypassing the application's cache, returned:

| Time on 23 October | Open | High | Low | Close |
| --- | ---: | ---: | ---: | ---: |
| 15:14 | 22,511.10 | 22,524.15 | 22,507.95 | 22,517.00 |
| Each minute, 15:15–15:27 | 22,516.40 | 22,516.40 | 22,516.40 | 22,516.40 |
| 15:28 | 22,516.40 | 22,600.00 | 22,516.40 | 22,600.00 |
| 15:29 | 22,600.00 | 22,600.00 | 22,600.00 | 22,600.00 |

The large body represents an 83.60-point change, approximately 0.3713%.

NSE's official index daily report independently records Nifty 50's closing value on 23 October as **22,600.00**. The downloaded report is `nifty-nse-official-index-close-2026-10-23.csv` in this directory.

The same structure occurs in all four sessions returned for 19–23 October:

| Session | Value held from 15:15 through 15:27 | Minute containing closing update | Final value |
| --- | ---: | --- | ---: |
| 19 October | 22,873.55 | 15:29 | 22,888.95 |
| 21 October | 22,738.45 | 15:29 | 22,811.35 |
| 22 October | 22,666.55 | 15:28 | 22,687.65 |
| 23 October | 22,516.40 | 15:28 | 22,600.00 |

The raw final minutes for these sessions are retained in `nifty-closing-auction-session-check.json`. No session was returned for 20 October; it is not counted as a checked session.

## Exchange rules explaining the structure

NSE circular CMTR75479 confirms that the Closing Auction Session (CAS) went live on 3 August 2026. Under the schedule applicable to the session investigated, eligible cash stocks leave continuous trading at 15:15. The auction order-entry period closes randomly during 15:28–15:30, and matching starts after order entry ends. This timing accounts for the pause followed by a discrete closing-price update. An index reflects its constituent share prices; it is not directly traded as a cash security.

Sources:

- [NSE CAS implementation circular, 30 July 2026](https://nsearchives.nseindia.com/content/circulars/CMTR75479.pdf)
- [NSE closing-auction operating schedule](https://www.nseindia.com/static/products-services/closing-auction-session)
- [NSE official daily index report, 23 October 2026](https://nsearchives.nseindia.com/content/indices/ind_close_all_23102026.csv)

## Application checks and limits

The direct upstream candle agrees with the application's stored/API candle. Inspection of the gateway, store, market-data service, and chart transformation found no application interpolation that creates the flat interval or the 83.60-point candle. The chart renders the supplied OHLC data.

The attribution to CAS is a strongly supported inference from the official session rules, the independently confirmed closing value, and repeated upstream timing. An exchange tick-by-tick audit was not obtained. NSE's public intraday chart endpoint returned an empty series during this investigation, so it did not provide an independent intraday comparison.

## Recommended presentation correction

Preserve the raw observations. Distinguish the auction phase visually and identify the closing-price update separately from continuous-session price action. Research calculations should explicitly choose whether to include auction updates. Any session classification should use effective dates and instrument applicability, rather than applying a permanent 15:15 cutoff to every ticker or historical date.

No application code or stored market data was changed during this investigation.
