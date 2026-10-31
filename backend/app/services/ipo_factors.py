"""Pure IPO factor mapping. Missing facts and subjective assessments stay explicit."""
from __future__ import annotations

from datetime import date, datetime

from . import ipo_sources as sources
from .market_store import IST, expiry_time, now

FACTOR_DEFINITIONS = [
    ("qib", "QIB subscription", "Demand", "x"),
    ("nii", "NII / HNI subscription", "Demand", "x"),
    ("retail", "Retail subscription", "Demand", "x"),
    ("total", "Overall subscription", "Demand", "x"),
    ("subscription_trend", "Day-wise demand trend", "Demand", "history"),
    ("gmp", "Grey market premium", "Demand", "gmp"),
    ("gmp_trend", "GMP trend", "Demand", "trend"),
    ("issue_size", "Issue size", "Structure", "cr"),
    ("fresh_ofs", "Fresh issue vs OFS", "Structure", "structure"),
    ("ofs_sellers", "OFS selling shareholders", "Structure", "text"),
    ("proceeds", "Use of proceeds", "Structure", "objects"),
    ("promoter_holding", "Promoter holding post-IPO", "Structure", "%"),
    ("anchors", "Anchor investors", "Structure", "anchors"),
    ("lead_manager", "Lead managers & track record", "Structure", "manager"),
    ("pe", "P/E at issue price", "Valuation", "pe"),
    ("returns", "RoNW / ROE / ROCE", "Valuation", "returns"),
    ("ebitda_margin", "EBITDA margin", "Valuation", "%"),
    ("revenue_growth", "Revenue / income growth", "Fundamentals", "%"),
    ("pat_growth", "PAT growth", "Fundamentals", "%"),
    ("borrowings", "Debt / borrowings", "Fundamentals", "cr"),
    ("business", "Business moat & customer diversification", "Fundamentals", "business"),
    ("sector", "Sector tailwinds", "Sentiment", "sector"),
    ("peer_listings", "Peer IPO listing track record", "Sentiment", "listings"),
    ("recommendations", "Broker / analyst recommendations", "Sentiment", "recommendations"),
]


def calendar_status(company: dict, today: str | None = None) -> str:
    today = today or now().astimezone(IST).date().isoformat()
    start, end = company.get("bidding_start_date"), company.get("bidding_end_date")
    if start and start > today:
        return "upcoming"
    if company.get("status") == "listed":
        return "listed"
    if end and end < today:
        return "closed"
    if start and end and start <= today <= end:
        return "open"
    return "announced" if not start else company.get("status", "upcoming")


def matched(company: dict, row: dict) -> bool:
    if not sources.same_company(company.get("name", ""), row.get("name", "")):
        return False
    old, new = sources.number(company.get("maximum_price")), sources.number(row.get("price"))
    if old and new and abs(old - new) / old > 0.02:
        return False
    left, right = company.get("bidding_end_date"), row.get("bidding_end_date") or row.get("close_date")
    return not (left and right and left != right)


def periods(data: dict, annual=False):
    result = []
    for index, value in enumerate(data.get("periods", [])):
        parsed = sources.source_date(value, history=True)
        if not parsed:
            continue
        day = date.fromisoformat(parsed[:10])
        if not annual or (day.month, day.day) == (3, 31):
            result.append((day, index))
    return sorted(result, reverse=True)


def financial_row(data: dict, *names: str):
    wanted = {name.lower() for name in names}
    return next((values for key, values in data.get("rows", {}).items() if key.lower() in wanted), [])


def growth(data: dict, *names: str):
    annual, values = periods(data, annual=True), financial_row(data, *names)
    if len(annual) < 2:
        return None, None
    (end, i), (previous, j) = annual[:2]
    if end.year - previous.year != 1 or max(i, j) >= len(values) or values[i] is None or values[j] is None or values[j] <= 0:
        return None, None
    return (values[i] / values[j] - 1) * 100, f"FY{previous.year} → FY{end.year}"


def build_detail(company: dict, research: dict, companies=None, all_research=None, observations=None) -> dict:
    status = calendar_status(company)
    pending = status in ("upcoming", "announced")
    fundamentals = research.get("fundamentals", {}).get("data", {})
    facts, valuation = fundamentals.get("facts", {}), fundamentals.get("valuation", {})
    finances, kpis = fundamentals.get("financials", {}), fundamentals.get("kpis", {})
    public = research.get("subscriptions", {}).get("data", {}) if not pending else {}
    sub_detail = research.get("subscription_detail", {}).get("data", {})
    categories = {**public, **sub_detail.get("latest", {})} if not pending else {}
    index = research.get("index", {}).get("data", {})
    gmp_data = research.get("gmp", {}).get("data", {})
    quote = gmp_data.get("gmp") if gmp_data.get("history") else index.get("gmp")
    upper = sources.number(company.get("maximum_price"))
    gmp_history = gmp_data.get("history", [])
    known_gmp = [point for point in gmp_history if point.get("value") is not None]
    trend = None
    if quote is not None and len(known_gmp) >= 2:
        previous, peak = known_gmp[-2]["value"], max(point["value"] for point in known_gmp)
        trend = {"direction": "Rising" if quote > previous else "Falling" if quote < previous else "Flat",
                 "change_rs": quote - previous, "from_peak_pct": (quote / peak - 1) * 100 if peak > 0 else None}
    current_overall = sources.number(company.get("total_subscription")) if not pending else None
    values = {}
    def put(key, value, kind=None, note=None, period=None, review=False):
        source = research.get(kind, {}) if kind else {}
        until = expiry_time("ipo_public_" + kind, {}, {}, datetime.fromisoformat(source["fetched_at"])) if source.get("fetched_at") else None
        if kind is None and company.get("fetched_at"):
            until = expiry_time("get_ipo_details", {}, company, datetime.fromisoformat(company["fetched_at"]))
        values[key] = {"value": value,
            "status": "pending" if pending and key in {"qib", "nii", "retail", "total", "subscription_trend"} else
                      "unavailable" if value is None or value == [] else "stale" if until and until < now() else "review" if review else "available",
            "source": "InvestorGain (public)" if kind and kind != "subscriptions" else "IPOWatch (public)" if kind else company.get("catalog_source", "Upstox"),
            "source_url": source.get("source_url") if kind else "https://upstox.com/developer/api-documentation/get-ipo-details/" if company.get("catalog_source") == "Upstox" else research.get("index", {}).get("source_url"),
            "fetched_at": source.get("fetched_at", company.get("fetched_at")), "reported_at": source.get("reported_at"),
            "period": period, "note": note}
    for key in ("qib", "retail"):
        put(key, categories.get(key), "subscription_detail" if key in sub_detail.get("latest", {}) else "subscriptions",
            "QIB bids can build late in the bidding window; compare at the same bidding day and time." if key == "qib" else None)
    nii = {key: categories.get(key) for key in ("nii", "snii", "bnii")}
    put("nii", nii if any(value is not None for value in nii.values()) else None,
        "subscription_detail" if "nii" in sub_detail.get("latest", {}) else "subscriptions")
    put("total", current_overall if current_overall is not None else categories.get("total"), None if current_overall is not None else "subscriptions")
    if current_overall is not None and categories.get("total") is not None and abs(current_overall - categories["total"]) > 0.02:
        values["total"]["note"] = f"Public source reports {categories['total']}x; Upstox reports {current_overall}x. Sources may use different update times."
    history = sub_detail.get("history", []) if not pending else []
    put("subscription_trend", history or None, "subscription_detail", "Only publisher-dated history is shown as day-wise demand. Collected snapshots are not backfilled bidding-day data.")
    put("gmp", {"rupees": quote, "percent": quote / upper * 100 if upper and quote is not None else None} if quote is not None else None,
        "gmp" if gmp_data.get("history") else "index", "Unofficial grey-market indication; not an executable quote or a listing-price forecast.")
    put("gmp_trend", trend, "gmp", "Change versus the previous published daily observation; drawdown uses this source's observed history.")
    put("issue_size", sources.number(company.get("issue_size")))
    fresh = sources.money_cr(facts.get("fresh issue"))
    ofs = sources.money_cr(facts.get("offer for sale") or facts.get("offer for sale (ofs)"))
    total = sources.money_cr(facts.get("issue size") or facts.get("total issue size"))
    if ofs is None and fresh is not None and total and abs(fresh - total) <= 0.01:
        ofs = 0.0
    if fresh is None and ofs is not None and total and abs(ofs - total) <= 0.01:
        fresh = 0.0
    structure = {"fresh_cr": fresh, "ofs_cr": ofs, "fresh_pct": fresh / total * 100 if fresh is not None and total else None,
                 "ofs_pct": ofs / total * 100 if ofs is not None and total else None}
    structure_note = "Percentages use the same source's total; unknown amounts remain blank. An undisclosed remainder is not assumed to be OFS."
    maker = sources.money_cr(facts.get("reserved for market maker"))
    if maker is not None:
        structure_note += f" This source separately reports ₹{maker:g} Cr reserved for the market maker; verify gross/net fresh-issue definitions in the RHP."
    put("fresh_ofs", structure if fresh is not None or ofs is not None else None, "fundamentals", structure_note)
    if total is not None and sources.number(company.get("issue_size")) is not None and abs(total - sources.number(company["issue_size"])) > 0.01:
        values["issue_size"]["note"] = f"Provider issue size shown; the public filing summary reports ₹{total:g} Cr. Check rounding and issue scope in the RHP."
    put("ofs_sellers", "Not applicable · all-fresh issue" if ofs == 0 else facts.get("selling shareholders") or facts.get("ofs selling shareholders"), "fundamentals",
        "Verify seller identities and promoter / financial-investor classification in the RHP." if ofs != 0 else "No OFS in the disclosed all-fresh issue.")
    put("proceeds", fundamentals.get("objects") or None, "fundamentals")
    put("promoter_holding", valuation.get("Promoter Holding", {}).get("post"), "fundamentals")
    anchors = sub_detail.get("anchors", [])
    put("anchors", {"amount_cr": sub_detail.get("anchor_amount_cr"), "count": sub_detail.get("anchor_count"), "investors": anchors} if anchors else None,
        "subscription_detail", "Disclosed allocations; investor quality is not inferred from names.")
    manager = facts.get("lead managers") or facts.get("lead manager")
    peer_listings, manager_listings = [], []
    for peer in companies or []:
        if peer["id"] == company["id"] or calendar_status(peer) != "listed":
            continue
        listing, price = sources.number(peer.get("listing_price")), sources.number(peer.get("cut_off_price"))
        if not listing or not price:
            continue
        point = {"name": peer["name"], "listing_return_pct": (listing / price - 1) * 100, "listing_date": (peer.get("timeline") or {}).get("listing_date")}
        if company.get("industry") and peer.get("industry") == company["industry"]:
            peer_listings.append(point)
        peer_facts = (all_research or {}).get(peer["id"], {}).get("fundamentals", {}).get("data", {}).get("facts", {})
        if manager and (peer_facts.get("lead managers") or peer_facts.get("lead manager")) == manager:
            manager_listings.append(point)
    put("lead_manager", {"names": manager, "tracked_listings": manager_listings} if manager else None, "fundamentals",
        "Reputation is not inferred from a name; track record covers only retained, matched lead managers.", review=bool(manager and not manager_listings))
    put("pe", valuation.get("P/E (x)") or valuation.get("P/E"), "fundamentals", "Published pre/post-IPO EPS bases may differ; verify the earnings denominator.")
    annual_kpi = periods(kpis, annual=True)
    kpi_index = annual_kpi[0][1] if annual_kpi else 0
    kpi_period = f"FY{annual_kpi[0][0].year}" if annual_kpi else "Period not specified"
    def kpi(*names):
        row = financial_row(kpis, *names)
        return row[kpi_index] if len(row) > kpi_index else None
    returns = {"ronw": kpi("RoNW", "Return on Net Worth"), "roe": kpi("ROE"), "roce": kpi("ROCE")}
    put("returns", returns if any(value is not None for value in returns.values()) else None, "fundamentals", period=kpi_period)
    put("ebitda_margin", kpi("EBITDA Margin"), "fundamentals", period=kpi_period)
    revenue_growth, revenue_period = growth(finances, "Revenue", "Revenue from Operations", "Total Income")
    basis = next((key for key in finances.get("rows", {}) if key.lower() in {"revenue", "revenue from operations", "total income"}), None)
    put("revenue_growth", revenue_growth, "fundamentals", f"Source measure: {basis}. Full fiscal years only.", revenue_period)
    pat_growth, pat_period = growth(finances, "Profit After Tax", "PAT")
    put("pat_growth", pat_growth, "fundamentals", "Not calculated when the prior period is zero or a loss.", pat_period)
    financial_periods = periods(finances)
    i = financial_periods[0][1] if financial_periods else 0
    borrowing = financial_row(finances, "Total Borrowing", "Total Borrowings", "Borrowings")
    put("borrowings", borrowing[i] if len(borrowing) > i else None, "fundamentals", period=financial_periods[0][0].isoformat() if financial_periods else None)
    about = fundamentals.get("business_excerpt")
    put("business", {"excerpt": about, "certifications": fundamentals.get("certifications", [])} if about else None, "fundamentals",
        "Business context is disclosed; competitive durability and customer concentration require a filing review.", review=True)
    put("sector", {"industry": company["industry"]} if company.get("industry") else None, None,
        "Sector classification is available; a sourced tailwind thesis still needs review.", review=True)
    put("peer_listings", peer_listings or None, None, "Same reported industry, retained recent listings only, using actual listing and cut-off prices.")
    put("recommendations", research.get("recommendations", {}).get("data", {}).get("recommendations") or None, "recommendations",
        "Attributed third-party opinions; verify publication dates and reasoning at the source.")
    for n, (key, label, group, unit) in enumerate(FACTOR_DEFINITIONS, 1):
        values[key].update({"id": key, "number": n, "label": label, "group": group, "unit": unit})
    conflicts = []
    if index.get("issue_type") and company.get("issue_type") and index["issue_type"] != company["issue_type"]:
        conflicts.append("Mainboard/SME classification differs between sources; verify the exchange filing.")
    if company.get("status") != status and status != "announced":
        conflicts.append(f"Provider status is {company.get('status')}; displayed {status} stage follows announced bidding dates.")
    return {"company": {**company, "stage": status}, "factors": [values[key] for key, *_ in FACTOR_DEFINITIONS],
            "coverage": sum(value["value"] is not None for value in values.values()), "conflicts": conflicts,
            "gmp_history": gmp_history, "subscription_history": history, "observations": observations or [], "financials": finances,
            "sources": [{"kind": key, "source_url": row.get("source_url"), "fetched_at": row.get("fetched_at"), "reported_at": row.get("reported_at")} for key, row in research.items()],
            "checked_at": now().isoformat(), "raw_upstox": {key: value for key, value in company.items() if key not in {"fetched_at", "catalog_source"}} if company.get("catalog_source") == "Upstox" else None}
