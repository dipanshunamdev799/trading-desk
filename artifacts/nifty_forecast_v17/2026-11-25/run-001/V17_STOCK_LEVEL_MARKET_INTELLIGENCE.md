# NIFTY V17 — Stock-level market intelligence

The historical research basket contains **30 common stocks and two ETFs**. Five dated January 2025 cash files rank traded rupee turnover within six defined sleeves. The seed dates precede the frozen evaluation period. This is a historically eligible, turnover-ranked sample with a discretionary sector shortlist. Complete dated NIFTY 50/100/200/500 constituent membership and free-float weights were unavailable. Therefore, archive-native sector/index series and official equal-weight index relative returns remain separate from actual stock-count breadth. NIFTYBEES and BANKBEES are traded instruments. The share baseline discards incoherent bars, overlap duplicates and mismatched ISINs. 12,588 stock/date pairs were compared with the official daily file. The matched panel identified 2 observed transitions and 98 marked ex-action stock days. The official archive recorded 117 basket-related corporate actions, including events without matching five-minute observations.

| stock | sector | rank | isin |
| --- | --- | --- | --- |
| HDFCBANK | bank | 1 | INE040A01034 |
| AXISBANK | bank | 2 | INE238A01034 |
| ICICIBANK | bank | 3 | INE090A01021 |
| SBIN | bank | 4 | INE062A01020 |
| KOTAKBANK | bank | 5 | INE237A01028 |
| INDUSINDBK | bank | 6 | INE095A01012 |
| BAJFINANCE | finance | 1 | INE296A01024 |
| BAJAJFINSV | finance | 2 | INE918I01026 |
| JIOFIN | finance | 3 | INE758E01017 |
| SHRIRAMFIN | finance | 4 | INE721A01047 |
| INFY | it | 1 | INE009A01021 |
| TCS | it | 2 | INE467B01029 |
| HCLTECH | it | 3 | INE860A01027 |
| PERSISTENT | it | 4 | INE262H01021 |
| WIPRO | it | 5 | INE075A01022 |
| RELIANCE | energy | 1 | INE002A01018 |
| NTPC | energy | 2 | INE733E01010 |
| ONGC | energy | 3 | INE213A01029 |
| POWERGRID | energy | 4 | INE752E01010 |
| BPCL | energy | 5 | INE029A01011 |
| M&M | auto | 1 | INE101A01026 |
| MARUTI | auto | 2 | INE585B01010 |
| EICHERMOT | auto | 3 | INE066A01021 |
| BAJAJ-AUTO | auto | 4 | INE917I01010 |
| TVSMOTOR | auto | 5 | INE494B01023 |
| ITC | defensive | 1 | INE154A01025 |
| HINDUNILVR | defensive | 2 | INE030A01027 |
| TATACONSUM | defensive | 3 | INE192A01025 |
| BRITANNIA | defensive | 4 | INE216A01030 |
| GODREJCP | defensive | 5 | INE102D01028 |
| NIFTYBEES | ETF | 1 | INF204KB14I2 |
| BANKBEES | ETF | 1 | INF204KB15I9 |

## Historical support and identity checks

KOTAKBANK, BAJFINANCE and SHRIRAMFIN have dated instrument-history entries. Some past keys failed and coverage differs by period. The same-day OHLCV panel uses the exact valid identifier where the source supplied it. A transition or implausibly large observed close-to-open discontinuity invalidates the overnight stock comparison. The action date is a separate sensitivity screen. The 25-minute fills preserve wider data for the audit and network where synchronized. Actual intraday stock-count features use only five-minute completed bars. The fixed top-300 January cohort and all-EQ official market file provide separate close-only tests before original-horizon issues.

| cutoff | dates | minimum | median | maximum | financial | stock count breadth | synchronized native |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 0.000000 |
| 09:35 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 0.000000 |
| 09:55 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 7.000000 |
| 10:20 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 7.000000 |
| 11:30 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 7.000000 |
| 12:30 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 7.000000 |
| 14:00 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 7.000000 |
| 15:00 | 400 | 18 | 20.000000 | 20 | 400 | 398 | 7.000000 |

Historical equity intake covered 408 archive sessions and 956,709 official EQ records. The receipt records aggregation results and raw source hashes.

[Symbol and resolution coverage](stock-bar-coverage.csv) · [Stock eligibility receipts](stock-eligibility-receipt.json) · [Date-indexed instrument history](stock-identifier-history.csv) · [Stock and exchange price audit](stock-identity-and-price-audit.csv.gz) · [Cash equity archive receipt](official-equity-receipt.json) · [Official cash breadth](official-stock-breadth.csv) · [NSE index methodology](https://nsearchives.nseindia.com/content/indices/Nifty_Broad_Market_Indices_Methodology.pdf)
