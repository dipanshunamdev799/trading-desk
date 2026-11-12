# Rate-based charge sensitivities

1854 trade/scenario rows cover actualdaily premiums,recentoptioncandles andhistoricallyreceivedsnapshots. Three brokerage assumptions(10/20/30INR perexecutedorder) are all disclosed. None is claimed as the recovered client tariff.

The model separates exchange,IPFT,SEBI,saleSTT,buystamp,GSTandbrokerage. It preserves theMarch2026 exchange/IPFT reallocation without doublecounting the oldIPFT. STTchanges on1April2026. GSTuses brokerage+exchange+IPFT perpublishedbroker table. Calculations are unrounded estimates; contract-note rounding,taxaggregation,rebates,partial-ordercharges and actualhistoricaltariff remain unverified.

Ask/bid snapshot returns already include spread. Candle returns still need unknownspread/latency sensitivities. Additional2/5premium-point scenarios do not replace observed spread. None of these fee assumptions creates more independent market observations.

Four numeric rate-transition/count checks passed. Fullpertradecostbreakdown and allconfigurationmeans are retained. [NSE fee circular](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf), [NSE STT](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf), [Upstox charges](https://upstox.com/brokerage-charges/).