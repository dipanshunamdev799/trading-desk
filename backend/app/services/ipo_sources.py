"""Public IPO tables with strict identity matching, explicit gaps and provenance.

Public providers are supplementary, not exchange data. Never pass the Upstox
authenticated session to these sites. No ratings or qualitative judgements are
invented from subscription counts or GMP.
"""
from __future__ import annotations

import math
import re
import threading
import time
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from .market_store import IST, now

GAIN_INDEX = "https://www.investorgain.com/report/ipo-gmp-live/331/"
WATCH_SUBSCRIPTIONS = "https://ipowatch.in/ipo-subscription-status-today/"
ALLOWED_HOSTS = {"www.investorgain.com", "investorgain.com", "ipowatch.in"}
_rate_lock = threading.Lock()
_next_request = 0.0


def number(value) -> float | None:
    if value is None:
        return None
    text = str(value).replace("−", "-").strip()
    if not text or "[.]" in text or text.lower() in {"na", "n/a", "none", "null"}:
        return None
    match = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", text)
    if not match:
        return None
    result = float(match.group().replace(",", ""))
    return result if math.isfinite(result) else None


def identity(name: str) -> str:
    words = re.sub(r"\b(ipo|limited|ltd|private|pvt)\b", "", name.lower())
    return re.sub(r"[^a-z0-9]", "", words)


def same_company(left: str, right: str) -> bool:
    a, b = identity(left), identity(right)
    # Verified alternative naming in Upstox's JPL catalogue and issuer filing.
    aliases = {"reliancejio": "jioplatforms"}
    a, b = aliases.get(a, a), aliases.get(b, b)
    return bool(a and b) and (a == b or SequenceMatcher(None, a, b).ratio() >= 0.86)


def source_date(value: str, *, history=False, reference: date | None = None) -> str | None:
    reference = reference or now().astimezone(IST).date()
    value = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", value.strip(), flags=re.I).replace(",", "")
    for fmt in ("%Y-%m-%d", "%d-%b %H:%M", "%d %b %I:%M %p", "%d %b %Y", "%b %d %Y", "%B %d %Y", "%d %B %Y", "%d-%b", "%d %b"):
        try:
            parsed = datetime.strptime(value if "%Y" in fmt else f"{value} {reference.year}", fmt if "%Y" in fmt else fmt + " %Y")
            if "%Y" not in fmt:
                parsed = parsed.replace(year=reference.year)
                if history and parsed.date() > reference + timedelta(days=1):
                    parsed = parsed.replace(year=reference.year - 1)
                elif not history and (reference - parsed.date()).days > 180:
                    parsed = parsed.replace(year=reference.year + 1)
            return parsed.replace(tzinfo=IST).isoformat() if "%H" in fmt or "%I" in fmt else parsed.date().isoformat()
        except ValueError:
            continue
    return None


def money_cr(value) -> float | None:
    if value is None:
        return None
    match = re.search(r"(?:₹|Rs\.?|INR)\s*([-+]?\d[\d,]*(?:\.\d+)?)\s*(?:Cr\b|Crore)", str(value), re.I)
    return number(match.group(1)) if match else None


def rows(table) -> list[list[str]]:
    return [[cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"], recursive=False)]
            for row in table.find_all("tr") if row.find_all(["td", "th"], recursive=False)]


def fetch_html(url: str) -> str:
    global _next_request
    for _ in range(4):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.port:
            raise ValueError("Public IPO URL is not on the allowed source hosts")
        with _rate_lock:
            delay = _next_request - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            _next_request = time.monotonic() + 0.35
        # Intentionally separate from the authenticated Upstox client.
        with requests.get(url, timeout=(5, 20), allow_redirects=False, stream=True,
                          headers={"User-Agent": "TradingDesk/0.1 (public IPO research; cached requests)"}) as response:
            if response.is_redirect:
                url = urljoin(url, response.headers["Location"])
                continue
            response.raise_for_status()
            body = bytearray()
            for part in response.iter_content(65536):
                body.extend(part)
                if len(body) > 5_000_000:
                    raise ValueError("IPO source response exceeded the size limit")
            return bytes(body).decode(response.encoding or "utf-8", errors="replace")
    raise ValueError("Too many IPO source redirects")


def parse_index(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for row in soup.select("tr"):
        cells = {cell.get("data-label"): cell for cell in row.find_all("td", recursive=False)}
        name_cell = cells.get("Name")
        anchor = name_cell.find("a") if name_cell else None
        if not anchor or "/gmp/" not in anchor.get("href", ""):
            continue
        def text(label):
            return cells[label].get_text(" ", strip=True) if label in cells else ""
        gmp_cell = cells.get("GMP")
        first = gmp_cell.find("b") if gmp_cell else None
        badges = [e.get_text(strip=True) for e in name_cell.select(".badge")]
        status = next(({"U": "upcoming", "O": "open", "C": "closed"}[b] for b in badges if b in {"U", "O", "C"}), "listed")
        url = urljoin(GAIN_INDEX, anchor["href"])
        result.append({"name": anchor.get_text(" ", strip=True), "url": url,
            "source_id": url.rstrip("/").split("/")[-1], "status": status,
            "issue_type": "sme" if "sme" in name_cell.get_text().lower() else "regular",
            "gmp": number(first.get_text()) if first else None,
            "price": number(text("Price (₹)")), "issue_size": number(text("IPO Size")),
            "lot_size": number(text("Lot")), "bidding_start_date": source_date(text("Open").split("GMP:")[0].strip()),
            "bidding_end_date": source_date(text("Close").split("GMP:")[0].strip()),
            "reported_at": source_date(text("Updated-On"), history=True)})
    if not result:
        raise ValueError("IPO GMP index table was not found; source layout may have changed")
    return {"rows": result}


def parse_subscription_index(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for table in soup.find_all("table"):
        data = rows(table)
        if not data or not all(word in " ".join(data[0]).lower() for word in ("qib", "retail", "total")):
            continue
        for row, node in zip(data[1:], table.find_all("tr")[1:]):
            if len(row) < 8:
                continue
            link = node.find("a")
            result.append({"name": row[0], "close_date": source_date(row[2]),
                "qib": number(row[3]), "nii": number(row[4]), "retail": number(row[5]), "total": number(row[6]),
                "reported_time": row[7], "source_url": urljoin(WATCH_SUBSCRIPTIONS, link["href"]) if link else WATCH_SUBSCRIPTIONS})
    if not result:
        raise ValueError("IPO category subscription table was not found")
    return {"rows": result}


def section(soup, title: str) -> dict:
    heading = soup.find(["h2", "h3"], string=lambda value: value and title.lower() in value.lower())
    if heading is None:
        heading = next((node for node in soup.find_all(["h2", "h3"]) if title.lower() in node.get_text(" ", strip=True).lower()), None)
    tables, paragraphs = [], []
    if heading:
        for node in heading.next_elements:
            if not isinstance(node, Tag):
                continue
            if node.name in ("h1", "h2"):
                break
            if node.name == "table":
                tables.append(rows(node))
            if node.name in ("p", "li") and not node.find_parent("table"):
                paragraphs.append(node.get_text(" ", strip=True))
    return {"tables": tables, "text": " ".join(paragraphs)}


def validate_identity(soup, expected_name):
    heading = soup.find("h1")
    actual = heading.get_text(" ", strip=True) if heading else ""
    actual = re.split(r"\b(GMP|Details|Live Subscription|Recommendations|Date, Review)\b", actual)[0]
    if not same_company(expected_name, actual):
        raise ValueError("Public source IPO identity does not match the selected company")


def parse_gmp(html: str, name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    validate_identity(soup, name)
    history = []
    for table in soup.find_all("table"):
        data = rows(table)
        if not data or not data[0][0].startswith("GMP Date"):
            continue
        for row in data[1:]:
            if len(row) < 2:
                continue
            stamp, premium = source_date(row[0], history=True), number(row[1].split("(")[0])
            if stamp:
                history.append({"at": stamp, "value": premium})
    history.sort(key=lambda point: point["at"])
    return {"history": history, "gmp": history[-1]["value"] if history else None,
            "reported_at": history[-1]["at"] if history else None}


def parse_fundamentals(html: str, name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    validate_identity(soup, name)
    tables = [rows(table) for table in soup.find_all("table")]
    facts, financials, kpis, valuation = {}, {}, {}, {}
    for table in tables:
        if not table:
            continue
        for row in table:
            if len(row) == 2:
                facts[row[0].strip().lower().rstrip(":")] = row[1]
        if table[0][0].lower().startswith("period ended"):
            financials = {"periods": table[0][1:], "rows": {row[0]: [number(value) for value in row[1:]] for row in table[1:]}}
        if table[0][0] == "KPI":
            kpis = {"periods": table[0][1:], "rows": {row[0].rstrip(":"): [number(value) for value in row[1:]] for row in table[1:]}}
        if "Pre IPO" in table[0] and "Post IPO" in table[0]:
            valuation = {row[0]: {"pre": number(row[1]), "post": number(row[2])} for row in table[1:] if len(row) >= 3}
    objects = []
    for table in section(soup, "Objectives")["tables"]:
        for row in table[1:]:
            if len(row) < 3 or row[1].strip().lower() == "total":
                continue
            purpose = row[1].lower()
            label = ("Debt repayment" if any(word in purpose for word in ("repay", "borrow", "debt")) else
                     "Capital expenditure" if any(word in purpose for word in ("capital expenditure", "manufactur", "equipment", "plant")) else
                     "Working capital" if "working capital" in purpose else "General corporate purposes" if "general corporate" in purpose else "Other disclosed use")
            objects.append({"purpose": label, "amount_cr": number(row[2])})
    about = section(soup, "About Company")["text"]
    certifications = sorted(set(re.findall(r"\b(?:RDSO|ISO(?:\s*\d{4,5})?|IATF(?:\s*\d{4,5})?|NABL|BIS)\b", about, re.I)))
    return {"facts": facts, "financials": financials, "kpis": kpis, "valuation": valuation,
            "objects": objects, "business_excerpt": " ".join(about.split()[:24]), "certifications": certifications,
            "tables": tables}


def category(header: str) -> str | None:
    header = header.lower().replace(" ", "")
    for words, key in ((["snii", "shni", "smallnii"], "snii"), (["bnii", "bhni", "bignii"], "bnii"),
                       (["qib"], "qib"), (["nii", "hni"], "nii"), (["retail", "rii"], "retail"), (["total", "overall"], "total")):
        if any(word in header for word in words):
            return key
    return None


def parse_subscription_detail(html: str, name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    validate_identity(soup, name)
    history, latest, anchors = [], {}, []
    for table in soup.find_all("table"):
        data = rows(table)
        if not data:
            continue
        header = " ".join(data[0]).lower()
        if "anchor investor" in header and "allotted" in header:
            for row in data[1:]:
                if len(row) >= 4 and row[0].isdigit():
                    anchors.append({"name": row[1], "shares": number(row[2]), "amount_cr": number(row[3])})
        if "qib" in header and "retail" in header:
            columns = {index: category(label) for index, label in enumerate(data[0]) if category(label)}
            for row in data[1:]:
                if not row:
                    continue
                values = {key: number(row[index]) for index, key in columns.items() if index < len(row)}
                stamp = source_date(row[0], history=True)
                if stamp:
                    history.append({"at": stamp, **values})
                elif values:
                    latest = values
    if history:
        history.sort(key=lambda point: point["at"])
        latest = history[-1]
    return {"history": history, "latest": latest, "anchors": anchors,
            "anchor_amount_cr": round(sum(row["amount_cr"] or 0 for row in anchors), 4) if anchors else None,
            "anchor_count": len(anchors) if anchors else None}


def parse_recommendations(html: str, name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    validate_identity(soup, name)
    recommendations = []
    for table in soup.find_all("table"):
        data = rows(table)
        if not data or not any("recommendation" in label.lower() or "broker" in label.lower() for label in data[0]):
            continue
        for row in data[1:]:
            if len(row) >= 2 and any(word in " ".join(row).lower() for word in ("subscribe", "avoid", "neutral", "apply")):
                recommendations.append({"reviewer": row[0], "opinion": " · ".join(row[1:])[:180]})
    return {"recommendations": recommendations}
