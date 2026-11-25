# V5 data universe

V5 independently acquired189 Upstox identities:25 domestic index/VIX series,
13 actual listed global instruments,150 stocks and NIFTYBEES; all 189 requests
succeeded. A registered liquidity extension acquired four additional ETFs,
bringing the successful daily-price universe to 193 instruments. The stocks are
the old50 current names plus the alphabetically first 100 eligible current
Nifty500 names outside that basket. This is an explicitly survivorship-exposed
research sample, not historically authenticated index membership or a claim that
these are the 150 most liquid stocks. No current index weights are invented.

Official FO coverage is 467 compact sessions (V3's465 plus17/18 November). Official
18 November index OHLC and cash-market bhavcopy resolve the broker's delayed
daily publication. NIFTY reference25,227.95 matches the FO underlying exactly.
All 25 domestic identities are explicitly mapped to the official index names;
index/cash source dates and OHLC identities are checked. Published index Volume
is constituent-aggregate activity, not traded NIFTY spot volume, and was not
mixed with genuine ETF traded volume.

The main frozen historical matrix has 403 origins,176 features,2Apr2025–17Nov2026;
the separate authenticated latest-input snapshot extends through18Nov. Main
historical feature/price prefixes remain numerically unchanged. Additional ETF
and research-only stock-volume features live in separate files, not a silently
changed initial dataset. Median missingness of primary families is measured below;
missing values use train-only medians, not future/backward fills.

|family|features|median_missing|
|---|---|---|
|d|19|0.0|
|g|52|0.0|
|i|52|0.0|
|l|18|0.0|
|p|13|0.0|
|s|10|0.0|
|x|12|0.0|

The available global catalogue contains S&P500, Dow Jones, FTSE100,DAX,CAC40,
Hang Seng,Nikkei225,US Tech100,GIFT NIFTY,US30,Brent,WTI and USD/INR. US Tech100 is
the provider's instrument, not relabeled Nasdaq Composite or a pure technology
sector index; US30/GIFT/commodity instruments retain futures/CFD ambiguity and
roll risks. There is no authenticated Russell,Shanghai,CSI,KOSPI,Taiwan,US sector,
credit-spread,DXY,USVIX or yield panel in the successful Upstox downloads.

Four bounded public FRED downloads (DGS10,DGS2,DTWEXBGS,VIXCLS) failed; correct
official Treasury2025/2026 feed probes timed out. They are documented as unavailable,
not zero-valued features or failed economic theories. No key/access restriction
was bypassed. Gold/silver and US/HongKong exposures were obtained as actual
INR-traded ETFs; their returns contain currency/tracking/premium effects and are
not commodity spot or foreign exchange closing-index observations. Historical
IV surfaces/Greeks/news sentiment were not manufactured.

Read-only database schema/method/identity coverage is in database-audit.json;
the current instrument masters and official current membership list are retained
with URLs/acquisition clocks/hashes. These catalogues are metadata, not historical
membership proof. Complete V1–V4 reports/source were read and 2727 existing artifacts
hashed for preservation; V4's ledger/protocol remain unchanged.

Ranked information priorities: (1) native sector/broad index leadership, strongest
usable lead; (2) genuine ETF activity/cross-asset proxies, mixed incremental evidence;
(3) global regional/relative-state structure, available but no incremental gain;
(4) authentic FO interactions, available but no increment; (5) wider stock panels,
rich but survivorship-exposed and poor transfer; (6) bond/USD-risk/IV/news information,
not currently authenticated/accessed as historical panels.

Instrument documentation: [Upstox instruments](https://upstox.com/developer/api-documentation/instruments/),
[Historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/).
Official latest input URLs are in latest-sources/acquisition.json; FRED/Treasury
failures and attempted bounded URLs are retained separately. No pre2025 market
observations or warmup state enter the study.

|identity|family|valid|first|last|invalid|duplicate|
|---|---|---|---|---|---|---|
|bank_nifty|domestic|466|2025-01-01|2026-11-17|0|0|
|g_^DJI|global|464|2025-01-01|2026-11-17|10|0|
|g_^FCHI|global|474|2025-01-02|2026-11-17|8|0|
|g_^FTSE|global|475|2025-01-03|2026-11-17|10|0|
|g_^GDAXI|global|481|2025-01-02|2026-11-17|5|0|
|g_^GSPC|global|489|2025-01-01|2026-11-17|0|0|
|g_^HSI|global|455|2025-01-02|2026-11-17|5|0|
|g_^N225|global|453|2025-01-06|2026-11-17|3|0|
|g_BZUSD|global|545|2025-01-01|2026-11-17|0|0|
|g_CLUSD|global|543|2025-01-02|2026-11-17|2|0|
|g_DOW_FUTURES|global|499|2025-01-02|2026-11-17|8|0|
|g_IXIX|global|481|2025-01-01|2026-11-17|9|0|
|g_SGX_NIFTY|global|492|2025-01-01|2026-11-17|3|0|
|g_USDINR|global|558|2025-01-01|2026-11-17|0|0|
|idx_Nifty_100|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_200|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_500|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_Commodities|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_Consumption|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_NIFTY_HEALTHCARE|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_Infra|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_InfraLog|domestic|254|2025-11-10|2026-11-17|0|0|
|idx_NIFTY_MIDCAP_100|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_NIFTY_MIDCAP_150|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_Midcap_50|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_Next_50|domestic|466|2025-01-01|2026-11-17|0|0|
|idx_Nifty_Smallcap_500|domestic|132|2026-05-11|2026-11-17|0|0|
|india_vix|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_auto|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_energy|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_financial|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_fmcg|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_it|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_metal|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_pharma|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_psu_bank|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_realty|domestic|466|2025-01-01|2026-11-17|0|0|
|nifty_spot|domestic|466|2025-01-01|2026-11-17|0|0|
|niftybees|etf|466|2025-01-01|2026-11-17|0|0|
|s_360ONE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AADHARHFC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AARTIIND|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AAVAS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ABB|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ABBOTINDIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ABCAPITAL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ABDL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ABREL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ABSLAMC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ACC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ACE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ACMESOLAR|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ACUTAAS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ADANIENSOL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ADANIENT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ADANIGREEN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ADANIPORTS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ADANIPOWER|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AEGISLOG|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AEGISVOPAK|stock_proxy|364|2025-06-02|2026-11-17|0|0|
|s_AETHER|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AFCONS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AFFLE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AIAENG|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AIIL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AJANTPHARM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ALKEM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AMBER|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AMBUJACEM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ANANDRATHI|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ANANTRAJ|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ANGELONE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ANTHEM|stock_proxy|329|2025-07-21|2026-11-17|0|0|
|s_ANURAS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_APARINDS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_APLAPOLLO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_APOLLOHOSP|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_APOLLOTYRE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_APTUS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ARE&M|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ASAHIINDIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ASHOKLEY|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ASIANPAINT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ASTERDM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ASTRAL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ATGL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ATHERENERG|stock_proxy|383|2025-05-06|2026-11-17|0|0|
|s_ATUL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AUBANK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AUROPHARMA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AVANTIFEED|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AWL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AXISBANK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_AZAD|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BAJAJ-AUTO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BAJAJFINSV|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BAJAJHFL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BAJAJHLDNG|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BAJFINANCE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BALKRISIND|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BALRAMCHIN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BANDHANBNK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BANKBARODA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BANKINDIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BATAINDIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BBOX|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BDL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BEL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BELRISE|stock_proxy|367|2025-05-28|2026-11-17|0|0|
|s_BEML|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BERGEPAINT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BHARATCOAL|stock_proxy|206|2026-01-19|2026-11-17|0|0|
|s_BHARATFORG|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BHARTIARTL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BHARTIHEXA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BHEL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BIOCON|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BLS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BLUESTARCO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BOSCHLTD|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BPCL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BRIGADE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BRITANNIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BSE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_BSOFT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CAMS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CANBK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CANFINHOME|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CANHLIFE|stock_proxy|268|2025-10-17|2026-11-17|0|0|
|s_CAPLIPOINT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CARBORUNIV|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CARTRADE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CASTROLIND|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CCL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CDSL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CEATLTD|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CEMPRO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CENTRALBK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CESC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CGCL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CGPOWER|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CHAMBLFERT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CHENNPETRO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CHOICEIN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CHOLAFIN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CHOLAHLDNG|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CIEINDIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CIPLA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CLEAN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_CLEANMAX|stock_proxy|176|2026-03-02|2026-11-17|0|0|
|s_CMPDI|stock_proxy|158|2026-03-30|2026-11-17|0|0|
|s_COALINDIA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_DRREDDY|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_EICHERMOT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ETERNAL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_GRASIM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_HCLTECH|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_HDFCBANK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_HDFCLIFE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_HINDALCO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_HINDUNILVR|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ICICIBANK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_INDIGO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_INFY|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ITC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_JIOFIN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_JSWSTEEL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_KOTAKBANK|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_LT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_M&M|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_MARUTI|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_MAXHEALTH|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_NESTLEIND|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_NTPC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ONGC|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_POWERGRID|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_RELIANCE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_SBILIFE|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_SBIN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_SHRIRAMFIN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_SUNPHARMA|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TATACONSUM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TATASTEEL|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TCS|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TECHM|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TITAN|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TMPV|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_TRENT|stock_proxy|466|2025-01-01|2026-11-17|0|0|
|s_ULTRACEMCO|stock_proxy|466|2025-01-01|2026-11-17|0|0|
