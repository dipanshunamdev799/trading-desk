# Option research data access and execution boundaries

Checked 9 November 2026 with read-only requests. No subscription purchase or order was made.

|Source|Observed result|Research use|
|---|---|---|
|Upstox expired expiry discovery|HTTP401, `UDAPI1149`, Plus required|Broad expired intraday option history remains unavailable through this entitlement. [Official endpoint and error](https://upstox.com/developer/api-documentation/get-expiries/).|
|Upstox active option contracts|2,218 contracts returned|Current instrument-key mapping; historical contract existence is independently checked against dated NSE records.|
|Upstox ordinary active-contract five-minute candles|29 exact contracts fetched successfully for recent diagnostic|17 frozen underlying signals, 68 policy attempts, 62 usable candle proxies; six expired mappings rejected.|
|Official NSE dated derivative archive|255 retained EOD dates; 93 required raw entry files successfully downloaded for daily study|Signal-day dated universe, exact instrument identities, lot sizes and actual daily premiums. Source ZIP SHA256 retained. [NSE reports](https://www.nseindia.com/all-reports-derivatives).|
|Tapetide REST dated derivative option analytics|HTTP200 but `data:null`, notice `api_access_not_in_plan`|Unusable as research data. The provider notice says REST access is not included in the current Free plan and directs users to eligible plans; no upgrade attempted. A successful HTTP status must not be interpreted as usable data.|
|One forward quote snapshot|Eight ATM/ITM CE/PE contracts across nearest/monthly expiries; market `CLOSING_END`; zero eligible quote proxies|Correctly rejects closed-market observations from fresh execution evidence. Raw quotes, Greeks, receipt time, source timestamps and rejection reasons retained.|

The daily study supplies real historical option premiums despite the expired intraday entitlement gap. It uses 106 frozen signal trades and 424 policy rows, with 374 distinct signal/contract outcomes within strategy. These remain daily first-trade/open and official-close proxies; exact first-trade time, contemporaneous bid/ask and immediate execution are unknown. Positive full-day entry/exit volume is an ex-post data-coverage check, not information available at entry. All 424 daily attempts passed this check, so it caused no additional selection.

The intraday diagnostic selects from the prior completed NSE session's contract universe, uses signal-time underlying closes for ATM choice, and requires exact identity when resolving current keys. It compares ATM/one-step ITM and nearest non-expiry-day/month-end expiry policies without substituting another contract when an expired mapping is missing. Volume in the entry and exit candles is an ex-post coverage condition. Actual candle opens can occur after the intended decision instant, so the diagnostic cannot establish executable profitability.

Both premium studies deduct dated option-sale STT: 0.10% through 31 March 2026 and 0.15% from 1 April 2026. Additional round-trip premium-point/cash allowances are explicitly illustrative; a complete dated broker, exchange, SEBI, GST and stamp-duty reconstruction is still absent. [NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).

The capture script checks market status, valid bid/ask, one-lot depth, spread and conservative timestamp/last-trade ages. HTTP quote timestamps may describe response time; last-trade age is a conservative proxy and does not prove the age of the order book. Snapshot receipt and event timestamps remain separate. The script captures once and terminates; it does not place orders or establish a persistent collector.

Code: `scripts/research_option_premiums.py`, `scripts/research_intraday_premiums.py`, `scripts/capture_option_research.py`. Full selection files, accepted/rejected ledgers and manifests accompany their reports. Replays use cached source files. The capture script requires active access and fetches a fresh bounded snapshot.
