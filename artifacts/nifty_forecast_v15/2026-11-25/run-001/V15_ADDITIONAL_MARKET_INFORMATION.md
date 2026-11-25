# V15 additional Upstox, NSE and global inputs

Daily experiments hold the decision clock fixed and test whether the newest eligible block improves a matched forecast. Domestic revisions use NSE official equal-weight breadth, financial-sector and cyclical/defensive rotation, concentration and synchronization. Liquidity uses ETF activity, traded participation, spread and impact proxies and the intraday variance shape. The derivative block uses the new eligible ATM term point, skew and curvature, futures basis, term structure, same-contract futures changes, unsigned OI concentration, volume-normalized OI and straddles. Offshore inputs separate cross-market equity, volatility, currency, oil, gold ETF and rate changes. Attribution is predictive and conditional on the model and the other blocks. Counterfactuals hold one block stale while retaining the same cash anchor.

## New authenticated 25-minute requests

| label | size |
| --- | --- |
| broad | 8 |
| defensive | 8 |
| etf | 8 |

NIFTY 500 and FMCG are cap-weighted market and defensive proxies, and NIFTYBEES is an ETF with volume. The 25-minute index sources use bank, financial services, IT and auto series from the V10 archive. Each group uses the actual instrument identifier and source-file hash. Upstox's cached instrument list did not establish an intraday official NIFTY 500 Equal Weight instrument. That benchmark remains in the daily official NSE cohort. Derivatives use trade-filtered EOD data with an explicit mark date earlier than the latest cash session. The term lookup retains the two source expiries, calendar tenor, quality status and interpolation regime. Nearest, interpolated variance and exact-tenor cases are retained. Same-contract changes preserve the prior roll controls.

[New authenticated calls](intraday-acquisition.json) [Quote tenor and lag audit](remaining-tenor-availability.csv) [Full session source audit](session-source-audit.json) [Daily availability receipt](data-avail-receipt.json) [Freshness and ablation results](V15_INCREMENTAL_INFORMATION_VALUE.md)
