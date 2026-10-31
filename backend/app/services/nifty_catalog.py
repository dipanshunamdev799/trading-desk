"""The complete NIFTY research checklist, independent of data availability.

``source_url`` identifies a recommended primary source. It is not provenance for
an observation: adapters must attach the actual fetched source and timestamp.
Priorities follow the supplied research checklist, not predictive importance.
"""
from __future__ import annotations

SECTIONS = [
    {"id": "global_markets", "title": "Global Markets", "description": "Overseas equities, futures and market sentiment."},
    {"id": "commodities_currencies", "title": "Commodities & Currencies", "description": "Volatility, energy, metals and exchange rates."},
    {"id": "rates_bonds", "title": "Interest Rates & Bonds", "description": "Sovereign yields, monetary policy and liquidity."},
    {"id": "institutional_flows", "title": "Institutional Money Flows", "description": "Foreign and domestic positioning and investment flows."},
    {"id": "derivatives_options", "title": "NIFTY Derivatives & Options", "description": "Expiry-specific positioning, option risk and contract terms."},
    {"id": "economy_government", "title": "Indian Economy & Government", "description": "Economic releases, public spending, policy and regulation."},
    {"id": "earnings_constituents", "title": "Corporate Earnings & Index Constituents", "description": "Earnings, guidance, index weights and constituent contributions."},
    {"id": "sectors_breadth", "title": "Sector Performance & Market Breadth", "description": "Sector leadership and participation beneath the index."},
    {"id": "technicals", "title": "Technical Analysis & Price Action", "description": "Observed price behaviour with explicit calculation windows."},
    {"id": "news_events", "title": "News, Geopolitics & Events", "description": "Dated releases and developments requiring source verification."},
]

NSE = "https://www.nseindia.com/"
NSE_REPORTS = "https://www.nseindia.com/all-reports-derivatives"
NSE_CHAIN = "https://www.nseindia.com/option-chain"
RBI = "https://www.rbi.org.in/"
FED = "https://www.federalreserve.gov/monetarypolicy.htm"
MOSPI = "https://www.mospi.gov.in/"
INDICES = "https://www.niftyindices.com/"

# id, label, priority, kind, unit, description, suggested source
_GROUPS = {
    "global_markets": [
        ("sp500", "S&P 500", "P1", "driver", "points", "US large-cap index level and change; match the actual US trading session.", "https://www.spglobal.com/spdji/en/indices/equity/sp-500/"),
        ("nasdaq", "Nasdaq Composite / Nasdaq 100", "P1", "driver", "points", "Technology-sensitive US equity benchmarks; retain the exact benchmark identity.", "https://indexes.nasdaq.com/"),
        ("dow", "Dow Jones", "P1", "driver", "points", "Dow Jones Industrial Average level and change.", "https://www.spglobal.com/spdji/en/indices/equity/dow-jones-industrial-average/"),
        ("us_futures", "US market futures", "P1", "driver", "points", "Contract-specific US index futures with expiry and quote time.", "https://www.cmegroup.com/markets/equities.html"),
        ("nikkei", "Nikkei 225", "P1", "driver", "points", "Japanese equity benchmark level and session change.", "https://indexes.nikkei.co.jp/en/nkave"),
        ("hang_seng", "Hang Seng", "P1", "driver", "points", "Hong Kong equity benchmark level and session change.", "https://www.hsi.com.hk/eng"),
        ("shanghai", "Shanghai Composite", "P1", "driver", "points", "Mainland China equity benchmark level and session change.", "https://english.sse.com.cn/"),
        ("europe", "European markets", "P1", "driver", "points", "Named European equity benchmarks; keep each index and currency separate.", "https://www.stoxx.com/"),
        ("gift_nifty", "GIFT NIFTY", "P1", "driver", "points", "GIFT NIFTY futures level, expiry and basis versus dated NIFTY spot.", "https://www.nseix.com/"),
        ("global_sentiment", "Global market sentiment", "P1", "context", "assessment", "Source-dated global risk appetite assessment with supporting observations.", "https://www.cboe.com/tradable_products/vix/"),
    ],
    "commodities_currencies": [
        ("india_vix", "India VIX", "P1", "indicator", "volatility points", "NSE implied volatility index level and change, not a directional forecast.", "https://www.nseindia.com/market-data/india-vix"),
        ("brent", "Brent crude oil", "P1", "driver", "USD/barrel", "Named Brent crude contract or spot assessment with timestamp and expiry.", "https://www.ice.com/products/219/Brent-Crude-Futures"),
        ("wti", "WTI crude oil", "P1", "driver", "USD/barrel", "Named WTI crude contract or spot assessment with timestamp and expiry.", "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.html"),
        ("gold", "Gold", "P3", "driver", "USD/troy oz", "Gold benchmark with currency, unit and contract identity preserved.", "https://www.lbma.org.uk/prices-and-data/precious-metal-prices"),
        ("silver", "Silver", "P3", "driver", "USD/troy oz", "Silver benchmark with currency, unit and contract identity preserved.", "https://www.lbma.org.uk/prices-and-data/precious-metal-prices"),
        ("usdinr", "USD/INR", "P1", "driver", "INR/USD", "Rupees per US dollar; distinguish reference fixing from live FX quotes.", RBI),
        ("dxy", "US Dollar Index (DXY)", "P1", "driver", "points", "US dollar basket index with quote timestamp.", "https://www.ice.com/products/194/US-Dollar-Index-Futures"),
        ("natural_gas", "Natural gas", "P3", "driver", "USD/MMBtu", "Named natural gas benchmark; geography and contract matter.", "https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.html"),
        ("copper", "Industrial metals / copper", "P3", "driver", "USD/lb", "Copper contract price with exchange, contract and unit; other metals may be attached separately.", "https://www.cmegroup.com/markets/metals/base/copper.html"),
    ],
    "rates_bonds": [
        ("us_10y", "US 10-year Treasury yield", "P2", "driver", "%", "Ten-year US Treasury yield; changes expressed in basis points.", "https://home.treasury.gov/resource-center-data-chart-center/interest-rates"),
        ("us_2y", "US 2-year Treasury yield", "P2", "driver", "%", "Two-year US Treasury yield and dated change.", "https://home.treasury.gov/resource-center-data-chart-center/interest-rates"),
        ("fed_policy", "Federal Reserve policy", "P3", "driver", "% / stance", "Federal funds target range, decision date and official policy statement.", FED),
        ("india_10y", "Indian 10-year government yield", "P2", "driver", "%", "Named Indian government benchmark yield and settlement date.", RBI),
        ("rbi_repo", "RBI repo rate & policy stance", "P3", "driver", "% / stance", "Policy repo rate and current dated MPC stance.", RBI),
        ("rbi_liquidity", "RBI liquidity operations", "P3", "driver", "INR crore", "Dated injection or absorption operations, tenor and net liquidity.", RBI),
        ("rate_differential", "US–India interest-rate differential", "P2", "driver", "percentage points", "Indian minus US yield using matched maturities and observation dates.", RBI),
        ("government_borrowing", "Government borrowing & bond supply", "P3", "driver", "INR crore", "Dated central-government borrowing plans, auctions and issuance.", RBI),
    ],
    "institutional_flows": [
        ("fii_cash", "FII/FPI cash-market net flow", "P1", "driver", "INR crore", "Exchange-reported net foreign cash buying/selling; provisional status retained.", "https://www.nseindia.com/reports/fii-dii"),
        ("dii_cash", "DII cash-market net flow", "P1", "driver", "INR crore", "Exchange-reported net domestic institutional cash buying/selling.", "https://www.nseindia.com/reports/fii-dii"),
        ("fii_index_futures", "FII index futures positioning", "P2", "indicator", "contracts", "Participant-specific long and short index futures positions by session.", NSE_REPORTS),
        ("fii_index_options", "FII index options positioning", "P2", "indicator", "contracts", "Participant-specific option long/short calls and puts; no direction inferred from totals alone.", NSE_REPORTS),
        ("mutual_fund_flows", "Mutual fund inflows & outflows", "P4", "driver", "INR crore", "Category-wise gross and net fund flows for the published reporting period.", "https://www.amfiindia.com/"),
        ("etf_flows", "ETF flows", "P4", "driver", "INR crore", "Creation/redemption or net flow data with named funds and reporting periods.", "https://www.amfiindia.com/"),
        ("fpi_trends", "Foreign portfolio investment trends", "P4", "driver", "INR crore", "Foreign portfolio flows by asset class and reporting period.", "https://www.fpi.nsdl.co.in/"),
        ("bulk_block_deals", "Bulk & block deals", "P3", "context", "deals", "Named buyers/sellers, shares, prices and exchange publication date.", "https://www.nseindia.com/report-detail/display-bulk-and-block-deals"),
    ],
    "derivatives_options": [
        ("pcr", "Put/Call Ratio (OI)", "P1", "indicator", "ratio", "Sum put OI divided by sum call OI for one complete expiry snapshot.", NSE_CHAIN),
        ("call_oi", "Strike-wise Call Open Interest", "P1", "indicator", "provider OI units", "Call OI by strike and expiry; preserve provider units and missing strikes.", NSE_CHAIN),
        ("put_oi", "Strike-wise Put Open Interest", "P1", "indicator", "provider OI units", "Put OI by strike and expiry; preserve provider units and missing strikes.", NSE_CHAIN),
        ("call_oi_change", "Change in Call OI", "P1", "indicator", "provider OI units", "Current minus previous call OI on matched strikes for one expiry.", NSE_CHAIN),
        ("put_oi_change", "Change in Put OI", "P1", "indicator", "provider OI units", "Current minus previous put OI on matched strikes for one expiry.", NSE_CHAIN),
        ("max_pain", "Max Pain", "P1", "indicator", "points", "Listed strike minimizing total intrinsic option payout; positioning descriptor only.", NSE_CHAIN),
        ("futures_basis", "NIFTY futures premium/discount", "P2", "indicator", "points", "Futures minus contemporaneous underlying spot, with expiry and time to expiry.", NSE_REPORTS),
        ("futures_buildup", "Futures long/short buildup", "P2", "indicator", "assessment", "Price and OI changes jointly classify observed buildup; no causal claim.", NSE_REPORTS),
        ("covering_unwinding", "Short covering & long unwinding", "P2", "indicator", "assessment", "Matched futures price/OI changes distinguish covering from unwinding.", NSE_REPORTS),
        ("iv", "Implied volatility (IV)", "P3", "indicator", "%", "Mean of call and put IV at the same nearest-to-spot strike and expiry.", NSE_CHAIN),
        ("iv_skew", "IV skew: puts versus calls", "P4", "indicator", "percentage points", "Put IV minus call IV at the same nearest-to-spot strike and expiry; no mixed moneyness.", NSE_CHAIN),
        ("option_greeks", "Option Greeks", "P4", "indicator", "per option", "Strike-wise Delta, Gamma, Theta and Vega with missing fields retained.", "https://upstox.com/developer/api-documentation/option-greek/"),
        ("option_volume", "Option volume", "P1", "indicator", "provider volume units", "Call and put traded volume by strike, expiry and timestamp.", NSE_CHAIN),
        ("expiry_calendar", "NIFTY expiry calendar", "P1", "context", "date", "Actual listed expiry dates; holidays and exchange rule changes apply.", NSE_REPORTS),
        ("contract_specs", "Lot sizes & contract specifications", "P1", "context", "contract terms", "Current listed lot sizes and dated exchange contract specification changes.", NSE_REPORTS),
    ],
    "economy_government": [
        ("union_budget", "Union Budget announcements", "P3", "driver", "event", "Dated official budget measures and affected sectors.", "https://www.indiabudget.gov.in/"),
        ("government_policy", "Government policies & regulations", "P3", "driver", "event", "Official policy releases, effective dates and scope.", "https://pib.gov.in/"),
        ("rbi_monetary_policy", "RBI monetary policy", "P3", "driver", "event", "MPC decision, projections, minutes and implementation dates.", RBI),
        ("cpi", "CPI inflation", "P3", "driver", "% YoY", "Consumer inflation with reference month, release date and revisions.", MOSPI),
        ("wpi", "WPI inflation", "P3", "driver", "% YoY", "Wholesale inflation with reference month and release vintage.", "https://eaindustry.nic.in/"),
        ("gdp", "GDP growth", "P3", "driver", "% YoY", "Real and nominal GDP identified separately with period and estimate vintage.", MOSPI),
        ("iip", "Industrial production (IIP)", "P3", "driver", "% YoY", "Industrial production growth by reference month and revision vintage.", MOSPI),
        ("pmi", "Manufacturing & services PMI", "P3", "driver", "index", "Manufacturing and services purchasing manager indices, separately labelled.", "https://www.pmi.spglobal.com/"),
        ("gst", "GST collections", "P3", "driver", "INR crore", "Monthly gross and net GST receipts with reporting period.", "https://www.gst.gov.in/"),
        ("fiscal_deficit", "Fiscal deficit", "P3", "driver", "INR crore / % GDP", "Fiscal deficit, year-to-date period and budget comparison.", "https://cga.nic.in/"),
        ("current_account", "Current account deficit", "P3", "driver", "% GDP", "Quarterly current account balance with currency and GDP share.", RBI),
        ("trade_deficit", "Trade deficit", "P3", "driver", "USD billion", "Merchandise/services trade balance with published reference month.", "https://commerce.gov.in/"),
        ("exports_imports", "Exports & imports", "P3", "driver", "USD billion", "Separate export and import values and growth; merchandise/services identified.", "https://commerce.gov.in/"),
        ("bank_credit", "Bank credit growth", "P3", "driver", "% YoY", "Bank credit growth with reporting fortnight or month.", RBI),
        ("deposit_growth", "Deposit growth", "P3", "driver", "% YoY", "Bank deposit growth with matched reporting period.", RBI),
        ("employment", "Employment & unemployment", "P3", "driver", "% / persons", "Official employment measures with survey population and period.", MOSPI),
        ("monsoon", "Monsoon & rainfall", "P3", "driver", "% departure", "Observed and forecast rainfall, geography, season and normal baseline.", "https://mausam.imd.gov.in/"),
        ("government_capex", "Government capital expenditure", "P3", "driver", "INR crore", "Actual expenditure versus budget with fiscal reference period.", "https://cga.nic.in/"),
        ("disinvestment", "Disinvestment & privatisation", "P3", "driver", "event / INR crore", "Official stake-sale plans, execution dates and proceeds.", "https://dipam.gov.in/"),
        ("sebi_regulation", "SEBI & other regulatory changes", "P3", "driver", "event", "Published circulars, effective dates and affected market segments.", "https://www.sebi.gov.in/"),
    ],
    "earnings_constituents": [
        ("quarterly_earnings", "Quarterly earnings results", "P3", "driver", "INR crore", "Issuer-filed quarterly results with standalone/consolidated basis.", NSE),
        ("earnings_revisions", "Earnings upgrades & downgrades", "P3", "driver", "% / revision", "Attributable estimate revisions with analyst source and comparison vintage.", NSE),
        ("revenue_profit_growth", "Revenue & profit growth", "P3", "driver", "% YoY", "Comparable period revenue and profit changes from filings.", NSE),
        ("profit_margins", "Corporate profit margins", "P3", "driver", "%", "Named margin measure and comparable accounting periods.", NSE),
        ("management_guidance", "Management guidance", "P3", "driver", "assessment", "Dated attributable guidance, forecast period and conditions.", NSE),
        ("heavyweight_moves", "NIFTY heavyweight stock movements", "P2", "driver", "%", "Constituent price changes and contemporaneous index weights.", INDICES),
        ("stock_contribution", "Stock contribution to NIFTY points", "P2", "indicator", "index points", "Contribution computed from valid constituent weights and matched price returns.", INDICES),
        ("corporate_announcements", "Corporate announcements", "P3", "driver", "event", "Exchange-filed announcements with issuer and publication time.", NSE),
        ("corporate_actions", "Dividends, buybacks & fundraising", "P3", "driver", "event / INR crore", "Declared corporate actions, ex-dates and funding terms.", NSE),
        ("nifty_rebalancing", "NIFTY index rebalancing", "P4", "context", "event", "Official index membership/weight changes and effective dates.", INDICES),
        ("sector_earnings", "Sector-wise earnings trends", "P3", "driver", "%", "Comparable sector aggregate earnings with coverage and weighting disclosed.", NSE),
    ],
    "sectors_breadth": [
        *[(key, label, "P2", "indicator", "points", f"{label} level, return and relative performance versus matched NIFTY sessions.", INDICES) for key, label in [
            ("bank_nifty", "Bank NIFTY"), ("nifty_financial", "NIFTY Financial Services"),
            ("nifty_it", "NIFTY IT"), ("nifty_auto", "NIFTY Auto"), ("nifty_fmcg", "NIFTY FMCG"),
            ("nifty_pharma", "NIFTY Pharma"), ("nifty_metal", "NIFTY Metal"), ("nifty_energy", "NIFTY Energy"),
            ("nifty_realty", "NIFTY Realty"), ("nifty_psu_bank", "NIFTY PSU Bank"),
        ]],
        ("advance_decline", "Advance/decline ratio", "P2", "indicator", "ratio", "Advancing divided by declining stocks in a specified universe and session.", NSE),
        ("stocks_above_ema", "NIFTY stocks above 20/50/200 EMA", "P2", "indicator", "stocks", "Counts and available constituent denominator for each EMA lookback.", NSE),
        ("highs_lows_52w", "New 52-week highs & lows", "P2", "indicator", "stocks", "New annual extremes in a stated constituent universe with adjusted prices.", NSE),
        ("nifty_equal_weight", "Equal-weighted NIFTY performance", "P2", "indicator", "points / %", "Official equal-weight index compared over the same sessions.", INDICES),
        ("relative_strength", "Sector & stock relative strength", "P2", "indicator", "ratio / %", "Named benchmark-relative returns using matched observation windows.", INDICES),
    ],
    "technicals": [
        ("nifty_spot", "NIFTY spot price & change", "P1", "indicator", "points", "Observed NIFTY index close/quote and change versus the previous session.", NSE),
        ("daily_trend", "Daily trend", "P3", "indicator", "trend", "Daily close relative to EMA21 and EMA50; requires 50 valid daily bars.", NSE),
        ("hourly_trend", "Hourly trend", "P3", "indicator", "trend", "Hourly close relative to EMA21 and EMA50; requires genuine hourly bars.", NSE),
        ("intraday_trend", "Intraday trend", "P3", "indicator", "trend", "Intraday close relative to EMA21 and EMA50 with interval disclosed.", NSE),
        ("support_resistance", "Support & resistance", "P3", "indicator", "points", "Lowest low and highest high of the previous 20 completed bars.", NSE),
        ("previous_high_low", "Previous day high & low", "P3", "indicator", "points", "Observed high and low from the previous available Indian trading session.", NSE),
        ("previous_close", "Previous close", "P3", "indicator", "points", "Previous available Indian session close, not the prior intraday bar.", NSE),
        ("opening_gap", "Opening gap", "P3", "indicator", "points / %", "First observed current-session open minus previous-session close.", NSE),
        ("volume", "Volume & volume spikes", "P3", "indicator", "traded units", "Only actual traded-instrument volume; NIFTY spot has no directly traded volume.", NSE),
        ("vwap", "VWAP", "P3", "indicator", "points", "Session typical-price VWAP only for an explicitly identified traded instrument.", NSE),
        ("ema", "EMA 9 / 21 / 50 / 100 / 200", "P3", "indicator", "points", "SMA-seeded exponential moving averages; insufficient periods remain missing.", NSE),
        ("rsi", "RSI", "P3", "indicator", "0–100", "14-period Wilder RSI, requiring at least 15 closes.", NSE),
        ("macd", "MACD", "P3", "indicator", "points", "SMA-seeded EMA12 minus EMA26, with EMA9 signal and histogram after 34 closes.", NSE),
        ("atr_volatility", "ATR & realised volatility", "P3", "indicator", "points / % annualised", "Wilder ATR14 and 20-return sample volatility of log returns, annualised only for daily bars.", NSE),
        ("breakouts", "Breakouts & breakdowns", "P3", "indicator", "state", "Latest close compared with the preceding 20-bar high and low.", NSE),
        ("market_structure", "Higher/lower highs & lows", "P3", "indicator", "state", "Two confirmed swing highs and lows using two neighbouring bars on either side.", NSE),
        ("opening_range", "Opening & previous-session range", "P3", "indicator", "points", "Observed 09:15–09:45 IST intraday range and previous available session range.", NSE),
        ("momentum", "Trend strength & momentum", "P3", "indicator", "% / EMA spread", "14-bar rate of change and EMA21/50 percentage spread; no direction prediction.", NSE),
    ],
    "news_events": [
        ("us_india_trade", "US–India tariffs & trade agreements", "P3", "driver", "event", "Official bilateral trade announcements, terms and effective dates.", "https://commerce.gov.in/"),
        ("us_china_trade", "US–China trade tensions", "P3", "driver", "event", "Official tariff/trade developments and implementation dates.", "https://ustr.gov/"),
        ("geopolitics", "Wars & geopolitical conflicts", "P3", "driver", "event", "Source-attributed conflict developments and identifiable market channels.", "https://news.un.org/"),
        ("sanctions_supply_chain", "Sanctions & supply-chain disruptions", "P3", "driver", "event", "Dated sanctions and verified trade/logistics disruptions.", "https://ofac.treasury.gov/"),
        ("elections", "Elections & political developments", "P3", "driver", "event", "Election dates, official results and dated policy developments.", "https://www.eci.gov.in/"),
        ("major_announcements", "Major government announcements", "P3", "driver", "event", "Official releases with publication time and scope.", "https://pib.gov.in/"),
        ("central_bank_calendar", "RBI & Federal Reserve meetings", "P3", "context", "calendar", "Official scheduled decision dates; unscheduled decisions retained separately.", FED),
        ("macro_release_calendar", "Inflation & employment releases", "P3", "context", "calendar", "Official release calendars including release timezone and reference period.", MOSPI),
        ("earnings_calendar", "Corporate earnings calendar", "P3", "context", "calendar", "Issuer-announced earnings/board meeting dates with verification status.", NSE),
        ("ipo_share_sales", "IPOs & major share sales", "P3", "context", "event", "Offer calendar, terms, selling shareholders and announcement dates.", NSE),
        ("global_index_rebalancing", "MSCI & other index rebalancing", "P4", "context", "event", "Index-provider announced changes with announcement and effective dates.", "https://www.msci.com/index-review"),
        ("index_expiries", "NIFTY & Bank NIFTY expiry dates", "P1", "context", "calendar", "Actual listed expiry dates for both underlyings; no assumed weekday rules.", NSE_REPORTS),
        ("unexpected_news", "Unexpected economic/political news", "P3", "driver", "event", "Verified source-dated unscheduled developments; uncertainty remains explicit.", "https://pib.gov.in/"),
    ],
}

_FAST = {"global_markets", "commodities_currencies", "derivatives_options", "sectors_breadth", "technicals"}
_MONTHLY = {"cpi", "wpi", "iip", "pmi", "gst", "fiscal_deficit", "trade_deficit", "exports_imports", "employment", "government_capex", "mutual_fund_flows", "etf_flows"}
_QUARTERLY = {"gdp", "current_account", "quarterly_earnings", "revenue_profit_growth", "profit_margins", "sector_earnings"}
_DAILY = {"fii_cash", "dii_cash", "fii_index_futures", "fii_index_options", "bulk_block_deals", "us_10y", "us_2y", "india_10y", "rate_differential"}
_EVENTS = {"fed_policy", "rbi_repo", "rbi_liquidity", "government_borrowing", "expiry_calendar", "contract_specs", "rbi_monetary_policy"}


def _cadence(factor_id: str, section_id: str) -> tuple[str, int]:
    if factor_id in _MONTHLY:
        return "monthly release", 45 * 86400
    if factor_id in _QUARTERLY:
        return "quarterly release", 130 * 86400
    if factor_id in _DAILY or section_id == "institutional_flows":
        return "trading-session release", 4 * 86400
    if factor_id in _EVENTS or section_id in {"news_events", "economy_government", "earnings_constituents"}:
        return "event driven; verify latest publication", 7 * 86400
    if section_id in _FAST:
        return "market session; provider dependent", 4 * 86400
    return "publication dependent", 7 * 86400


FACTORS = []
for _section_id, _rows in _GROUPS.items():
    for _id, _label, _priority, _kind, _unit, _description, _source in _rows:
        _cad, _stale = _cadence(_id, _section_id)
        FACTORS.append({"id": _id, "section_id": _section_id, "label": _label,
                       "priority": _priority, "kind": _kind, "unit": _unit,
                       "description": _description, "source_url": _source,
                       "cadence": _cad, "stale_after_seconds": _stale})
FACTOR_MAP = {factor["id"]: factor for factor in FACTORS}
