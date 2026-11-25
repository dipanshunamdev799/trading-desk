# V16 Global information arrival map

A forecast snapshot stores the exchange-local date of each completed foreign observation, its assumed publication time in IST, the price-bar timestamp where relevant, the earliest assumed eligibility and the age of the eligible mark. The foreign cash inputs are US, European and Asian observations with distinct clocks. Local time-zone conversion accounts for US and European daylight-saving changes. We distinguish the preceding completed cash session from a valid Asian partial session and from a contemporaneous vendor futures or indicator mark. The snapshot keeps earlier known marks through weekends and missing or confirmed holiday observations. Calendar labels printed at midnight are treated as date labels, with exchange close or vendor roll conventions plus explicit buffers. Historic receipt stamps, where unavailable, remain empty.

## Completed daily source timing

| source | timezone | assumed local close | buffer minutes | reconstructable end of day marks |
| --- | --- | --- | --- | --- |
| spx | America/New_York | 16:00 | 60 | 489 |
| dow | America/New_York | 16:00 | 60 | 474 |
| ftse | Europe/London | 16:35 | 60 | 485 |
| dax | Europe/Berlin | 17:40 | 60 | 486 |
| nikkei | Asia/Tokyo | 15:35 | 60 | 378 |
| hsi | Asia/Hong_Kong | 16:15 | 60 | 455 |
| tech | America/New_York | 16:05 | 60 | 490 |
| cac | Europe/Paris | 17:40 | 60 | 482 |
| fx | Asia/Kolkata | 23:59 | 1,440 | 558 |
| brent | America/New_York | 23:59 | 1,440 | 545 |
| wti | America/New_York | 23:59 | 1,440 | 545 |
| gift_day | Asia/Kolkata | 23:59 | 1,440 | 495 |

## Authenticated intraday history added

| series | instrument | bar minutes | requests | successful | bars |
| --- | --- | --- | --- | --- | --- |
| brent | GLOBAL_INDICATOR/BZUSD | 25 | 8 | 8 | 23,815 |
| fx | GLOBAL_INDICATOR/USDINR | 25 | 8 | 8 | 15,559 |
| gift | GLOBAL_INDEX/SGX NIFTY | 5 | 23 | 21 | 93,175 |
| hsi | GLOBAL_INDEX/^HSI | 25 | 8 | 8 | 6,750 |
| nikkei | GLOBAL_INDEX/^N225 | 25 | 8 | 8 | 6,025 |
| spx | GLOBAL_INDEX/^GSPC | 25 | 8 | 8 | 6,982 |
| us_tech | GLOBAL_INDEX/IXIX | 25 | 8 | 8 | 6,968 |

The US block uses S&P 500, Dow and a vendor US Tech 100 reference, alongside the preserved dated Nasdaq/FRED volatility and Treasury features and a new alignment of archived SPY, RSP, XLF and XLK closes. The ETFs proxy cap weight, equal weight, finance and technology. European rows cover FTSE, DAX and CAC. Asia uses Nikkei and Hang Seng completed closes plus current dated partial marks. GIFT uses its named vendor global series, and FX, Brent and WTI have separate close and timestamp rules. Upstox did not establish a comparable historic intraday Russell, TOPIX, mainland Chinese index or India ADR series in these tested records. The FX and oil daily date labels receive an extra day beyond nominal local midnight. Their eligible intra-market bars have separate clocks and age guards. Missing intervals remain missing. [Global instrument metadata](https://upstox.com/developer/api-documentation/announcements/global-instruments/) · [Historical candle intervals](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)

The screening sensitivity flagged **336** decision/source rows where selected 2026 vendor date marks fell on published cash-venue closure dates, then reran the factor after dropping those printed dates and carrying the latest verified preceding session. This comparison treats a venue holiday print as a vendor-clock sensitivity. It uses observed earlier vendor dates for 2025 and the published normal-session rules. Nasdaq price changes come from historical ETF closes and can include tracking, distribution and corporate-action effects. Briefed futures contracts, forecasts and authenticated capture timestamps are stored separately from corrected clock assumptions. [NYSE calendar](https://www.nyse.com/trade/hours-calendars) · [JPX calendar](https://www.jpx.co.jp/english/corporate/about-jpx/calendar/) · [HKEX 2026 calendar](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/SEHK/2025/ce_SEHK_CT_075_2025.pdf) · [Euronext calendar](https://www.euronext.com/en/trading/trading-hours-holidays)

## Holiday handling sensitivity

| model | n | brier | crps |
| --- | --- | --- | --- |
| official_holiday_carry_forward | 258 | 0.238625 | 0.003046 |
| raw_date_labels | 258 | 0.237415 | 0.003037 |

[Complete per-source clock map](information-clock.csv.gz) · [Normalized bar hashes](normalized-market-data.json) · [RSP, SPY, XLF and XLK clock](us-etf-information-clock.csv) · [ETF provenance](us-etf-source-receipt.json) · [Calendar receipts](exchange-calendar-receipts.json) · [Checked holiday rows](verified-holiday-flag-sensitivity.csv) · [Provider request receipts](foreign-intraday-acquisition.json)
