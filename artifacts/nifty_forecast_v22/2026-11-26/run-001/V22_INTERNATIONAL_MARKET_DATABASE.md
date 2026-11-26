# V22 International market database

The market database covers 2025-01-01 through 2026-11-17. It contains 9,354 primary price-index marks
from 20 market jurisdictions and 25,139 marks across primary and additional series.
Official NSE OHLC was independently reconciled to the V11 close archive on 466 sessions.
The universe admitted a broad local price index with at least 360 closes and at most 13% missing scheduled sessions. The archive
has 1,565 explicitly classified missing or vendor-only session records. Local labels retain exchange holidays, scheduled
half days and time zones from exchange-calendars 4.13.3. A scheduled close plus 60 minutes is the standard
availability guard for primary markets. It is a conservative reconstruction of information flow and depends on a daily vendor snapshot.
[NYSE trading hours](https://www.nyse.com/trade/hours-calendars) · [JPX trading hours](https://www.jpx.co.jp/english/equities/trading/domestic/01.html) · [Exchange calendars](https://github.com/gerrymanoim/exchange_calendars)

## Primary price indices

| market | ticker | currency | exchange | eligible close | valid ohlc | missing close | off calendar rows | utc offsets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| India | NIFTY 50 | INR | NSE | 466 | 466 | 0 | 0 | +0530 |
| United States | ^GSPC | USD | XNYS | 471 | 471 | 0 | 0 | -0400,-0500 |
| Canada | ^GSPTSE | CAD | XTSE | 472 | 472 | 0 | 0 | -0400,-0500 |
| Mexico | ^MXX | MXN | XMEX | 471 | 471 | 0 | 0 | -0600 |
| United Kingdom | ^FTSE | GBP | XLON | 476 | 476 | 0 | 0 | +0000,+0100 |
| France | ^FCHI | EUR | XPAR | 480 | 480 | 0 | 0 | +0100,+0200 |
| Germany | ^GDAXIP | EUR | XETR | 478 | 478 | 0 | 0 | +0100,+0200 |
| Spain | ^IBEX | EUR | XMAD | 480 | 480 | 0 | 0 | +0100,+0200 |
| Italy | FTSEMIB.MI | EUR | XMIL | 477 | 477 | 0 | 0 | +0100,+0200 |
| Switzerland | ^SSMI | CHF | XSWX | 471 | 471 | 0 | 0 | +0100,+0200 |
| Netherlands | ^AEX | EUR | XAMS | 480 | 480 | 0 | 0 | +0100,+0200 |
| Japan | ^N225 | JPY | XTKS | 455 | 455 | 0 | 0 | +0900 |
| Hong Kong | ^HSI | HKD | XHKG | 462 | 462 | 0 | 0 | +0800 |
| Mainland China | 000001.SS | CNY | XSHG | 453 | 453 | 0 | 0 | +0800 |
| South Korea | ^KS11 | KRW | XKRX | 456 | 456 | 1 | 0 | +0900 |
| Taiwan | ^TWII | TWD | XTAI | 453 | 453 | 2 | 0 | +0800 |
| Singapore | ^STI | SGD | XSES | 472 | 472 | 0 | 0 | +0800 |
| Australia | ^AXJO | AUD | XASX | 477 | 477 | 0 | 0 | +1000,+1100 |
| Indonesia | ^JKSE | IDR | XIDX | 446 | 446 | 1 | 0 | +0700 |
| Malaysia | ^KLSE | MYR | XKLS | 458 | 458 | 3 | 0 | +0800 |

## Return conventions and source comparison

Price marks are unadjusted local index levels and subsequent returns exclude dividends. Optional USD returns translate the
local index with matched as-of currency marks. FX, sector and size proxies, VIX, yields, and Brent are context.
Germany uses the DAX price series. The DAX total-return index, the Ibovespa total-return index, the TOPIX ETF, and US duplicate
headline and sector indices remain outside the primary label pool. Thailand does not meet the primary data threshold.
[Official DAX price index](https://stoxx.com/index/daxk/) · [B3 Ibovespa methodology and convention](https://www.b3.com.br/en_us/market-data-and-indices/indices/broad-indices/ibovespa.htm) · [Nasdaq index variants](https://indexes.nasdaq.com/docs/NDX%20Versions.pdf)

Upstox returned a 13-instrument global catalog and six authenticated daily-candle samples from October 1 through November 17,
2026. The table compares their displayed session labels with the primary vendor. Source agreement varies substantially,
particularly for Japan and US levels. The samples retain all discrepancies and were never spliced into the scored primary
series. All 6 attempted independent FRED series timed out. Foreign availability is reconstructed from the venue
clock and historical chart dates. Several venue close series lack an independent point-in-time second feed.
[Upstox global index catalog documentation](https://upstox.com/developer/api-documentation/announcements/global-instruments/) · [Upstox candle timestamp specification](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [Yahoo Finance world indices](https://finance.yahoo.com/markets/world-indices/)

| code | n matched | broker only | provider only | close within 006 | median absolute close diff pct | day return correlation |
| --- | --- | --- | --- | --- | --- | --- |
| us | 34 | 0 | 0 | 0 | 0.282628 | 0.962212 |
| japan | 24 | 7 | 8 | 1 | 0.957437 | 0.069488 |
| hong_kong | 29 | 2 | 3 | 26 | 0.000003 | 0.690233 |
| uk | 34 | 0 | 0 | 1 | 0.067748 | 0.955143 |
| france | 34 | 0 | 0 | 17 | 0.007332 | 0.979024 |
| dax_total | 34 | 0 | 0 | 0 | 0.059384 | 0.984574 |

## Other candidate series and proxies

| code | ticker | role | convention | eligible close | missing close |
| --- | --- | --- | --- | --- | --- |
| thailand | ^SET.BK | primary | local price index | 0 | 455 |
| brazil | ^BVSP | sensitivity | local total-return index | 469 | 0 |
| dax_total | ^GDAXI | context | local gross total-return index | 478 | 0 |
| euro50 | ^STOXX50E | context | local price index | 471 | 7 |
| ndx | ^NDX | context | local price index | 471 | 0 |
| dow | ^DJI | context | local price index | 471 | 0 |
| russell | ^RUT | context | local price index | 471 | 0 |
| us_equal | RSP | context | ETF raw price | 471 | 0 |
| us_finance | XLF | context | ETF raw price | 471 | 0 |
| us_technology | XLK | context | ETF raw price | 471 | 0 |
| uk_mid | ^FTMC | context | local price index | 476 | 0 |
| topix | ^TOPX | context | local price index | 0 | 455 |
| topix_etf | 1306.T | context | ETF raw price | 455 | 0 |
| china300 | 000300.SS | context | local price index | 0 | 453 |
| aus_finance | ^AXFJ | context | local price index | 477 | 0 |
| vix | ^VIX | context | implied risk index | 471 | 0 |
| us10y | ^TNX | context | yield level | 471 | 0 |
| brent | BZ=F | context | vendor continuous commodity front | 473 | 2 |
| dollar | DX-Y.NYB | context | USD basket | 473 | 100 |
| fx_eur | EURUSD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_gbp | GBPUSD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_aud | AUDUSD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_cad | CAD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_jpy | JPY=X | context | USD per local currency after conversion | 485 | 4 |
| fx_hkd | HKD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_cny | CNY=X | context | USD per local currency after conversion | 485 | 4 |
| fx_krw | KRW=X | context | USD per local currency after conversion | 485 | 4 |
| fx_twd | TWD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_sgd | SGD=X | context | USD per local currency after conversion | 485 | 4 |
| fx_inr | INR=X | context | USD per local currency after conversion | 485 | 4 |
| fx_chf | CHF=X | context | USD per local currency after conversion | 485 | 4 |
| fx_mxn | MXN=X | context | USD per local currency after conversion | 485 | 4 |
| fx_idr | IDR=X | context | USD per local currency after conversion | 485 | 4 |
| fx_myr | MYR=X | context | USD per local currency after conversion | 485 | 4 |
| fx_thb | THB=X | context | USD per local currency after conversion | 485 | 4 |
| fx_brl | BRL=X | context | USD per local currency after conversion | 485 | 4 |

[market-universe-audit.csv](market-universe-audit.csv) · [international-source-receipt.json](international-source-receipt.json) · [nse-historical-source-chain.json](nse-historical-source-chain.json) · [international-calendar-gaps.csv](international-calendar-gaps.csv) · [upstox-provider-comparison.csv](upstox-provider-comparison.csv) · [upstox-provider-pair-cases.csv](upstox-provider-pair-cases.csv) · [upstox-provider-date-offset-diagnostic.csv](upstox-provider-date-offset-diagnostic.csv) · [international-daily-book.csv.gz](international-daily-book.csv.gz)

[Back to the V22 report index](NIFTY_V22_RESEARCH.md)
