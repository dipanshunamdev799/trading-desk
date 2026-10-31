"""IPO universe, sourced research and durable background collection."""
from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text

from . import ipo_sources as sources
from .ipo_factors import build_detail, calendar_status, matched
from .ipo_store import IpoStore
from .market_store import now
from .upstox_service import get_upstox


class IpoService:
    def __init__(self, client):
        self.client = client
        self.repo = IpoStore(client.store)
        self.catalog_lock = threading.Lock()
        self.failures: dict[str, float] = {}

    def _public(self, kind, url, company=None):
        key = f"{company['id'] if company else 'universe'}:{kind}"
        if self.failures.get(key, 0) > time.monotonic():
            return
        def load():
            self.client.store.count("ipo_public_source_fetches")
            html = sources.fetch_html(url)
            if kind == "index":
                return sources.parse_index(html)
            if kind == "subscriptions":
                return sources.parse_subscription_index(html)
            parser = {"gmp": sources.parse_gmp, "fundamentals": sources.parse_fundamentals,
                      "subscription_detail": sources.parse_subscription_detail, "recommendations": sources.parse_recommendations}[kind]
            data = parser(html, company["name"])
            metrics = {"gmp": data["gmp"]} if kind == "gmp" else {}
            return {"ipo_id": company["id"], "kind": kind, "source_url": url, "data": data,
                    "reported_at": data.get("reported_at"), "metrics": metrics}
        normalize = self._save_index if kind == "index" else self._save_subscription_index if kind == "subscriptions" else IpoStore.save_research
        try:
            self.client.store.read("ipo_public_" + kind,
                {"url": url, "ipo_id": company["id"] if company else None, "parser_version": 1}, load, normalize=normalize)
            self.repo.sync(key)
        except Exception as exc:
            self.failures[key] = time.monotonic() + 300
            self.repo.sync(key, f"{type(exc).__name__}: {str(exc)[:220]}")

    def _save_index(self, conn, payload, at):
        companies = list(conn.execute(text("SELECT payload FROM ipo_companies ORDER BY (source='Upstox') DESC")).scalars())
        public_ids = []
        for row in payload["rows"]:
            company = next((company for company in companies if matched(company, row)), None)
            if not company and row["status"] in {"upcoming", "open"} and row.get("bidding_start_date"):
                company = {"id": "investorgain-" + row["source_id"], "name": row["name"], "status": row["status"],
                           "issue_type": row["issue_type"], "maximum_price": row["price"], "issue_size": row["issue_size"],
                           "lot_size": row["lot_size"], "bidding_start_date": row["bidding_start_date"], "bidding_end_date": row["bidding_end_date"]}
                IpoStore.save_company(conn, company, at, "InvestorGain (public)")
                companies.append(company)
            if not company:
                continue
            if company["id"].startswith("investorgain-"):
                company = {**company, "name": row["name"], "status": row["status"], "issue_type": row["issue_type"],
                    "maximum_price": row["price"], "issue_size": row["issue_size"], "lot_size": row["lot_size"],
                    "bidding_start_date": row["bidding_start_date"], "bidding_end_date": row["bidding_end_date"]}
                IpoStore.save_company(conn, company, at, "InvestorGain (public)")
                public_ids.append(company["id"])
            IpoStore.save_research(conn, {"ipo_id": company["id"], "kind": "index", "source_url": row["url"],
                "data": row, "metrics": {"gmp": row["gmp"]}, "reported_at": row.get("reported_at")}, at)
        IpoStore.save_feed(conn, "public", public_ids, at)

    def _save_subscription_index(self, conn, payload, at):
        companies = list(conn.execute(text("SELECT payload FROM ipo_companies ORDER BY (source='Upstox') DESC")).scalars())
        for row in payload["rows"]:
            company = next((company for company in companies if matched(company, row)), None)
            if not company or calendar_status(company) in {"upcoming", "announced"}:
                continue
            IpoStore.save_research(conn, {"ipo_id": company["id"], "kind": "subscriptions", "source_url": sources.WATCH_SUBSCRIPTIONS,
                "data": row, "metrics": {key: row.get(key) for key in ("qib", "nii", "retail", "total")}, "reported_at": None}, at)

    def refresh_catalog(self):
        with self.catalog_lock:
            for status in ("upcoming", "open", "closed", "listed"):
                ids, complete = [], False
                try:
                    for page in range(1, 101):
                        raw = self.client.get_ipos(status=status, page_number=page, records=30)
                        rows = raw.get("data", []) if isinstance(raw, dict) else raw
                        if not isinstance(rows, list):
                            raise ValueError("Unrecognized Upstox IPO page")
                        ids.extend(row["id"] for row in rows if isinstance(row, dict) and row.get("id"))
                        if len(rows) < 30 or status in ("closed", "listed"):
                            complete = True
                            break
                    if not complete:
                        raise ValueError("IPO pagination limit reached; retained universe has not been replaced")
                    self.repo.set_feed("upstox:" + status, ids)
                    self.repo.sync("upstox:" + status)
                except Exception as exc:
                    self.repo.sync("upstox:" + status, f"{type(exc).__name__}: {str(exc)[:220]}")
            self._public("index", sources.GAIN_INDEX)
            self._public("subscriptions", sources.WATCH_SUBSCRIPTIONS)

    def enrich(self, company: dict):
        key = company["id"]
        if not key.startswith("investorgain-"):
            try:
                self.client.get_ipo_details(key)
                self.repo.sync("upstox-detail:" + key)
            except Exception as exc:
                self.repo.sync("upstox-detail:" + key, f"{type(exc).__name__}: {str(exc)[:220]}")
        index = self.repo.research(key).get("index")
        if not index:
            return
        url = index["data"]["url"]
        for kind, path in (("gmp", "/gmp/"), ("fundamentals", "/ipo/"),
                           ("subscription_detail", "/subscription/"), ("recommendations", "/recommendations/")):
            self._public(kind, url.replace("/gmp/", path, 1), company)

    def refresh_all(self):
        self.refresh_catalog()
        ids = self.repo.active_ids()
        companies = [company for company in self.repo.companies() if company["id"] in ids]
        companies.sort(key=lambda company: (not bool(company.get("bidding_start_date")), company.get("bidding_start_date") or "9999"))
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="ipo-collector") as pool:
            list(pool.map(self.enrich, companies))

    def catalogue(self):
        self.refresh_catalog()
        ids, companies, research = self.repo.active_ids(), self.repo.companies(), self.repo.all_research()
        rows = []
        for company in companies:
            if company["id"] not in ids:
                continue
            if company["id"].startswith("investorgain-") and any(
                peer["id"] in ids and not peer["id"].startswith("investorgain-") and matched(peer, {
                    "name": company["name"], "price": company.get("maximum_price"), "bidding_end_date": company.get("bidding_end_date")
                }) for peer in companies):
                continue
            detail = build_detail(company, research.get(company["id"], {}), companies, research)
            factors = {factor["id"]: factor for factor in detail["factors"]}
            rows.append({**detail["company"], "coverage": detail["coverage"], "conflicts": detail["conflicts"],
                "has_public_research": bool(research.get(company["id"])),
                "signals": {key: factors[key] for key in ("qib", "nii", "retail", "total", "gmp", "gmp_trend")}})
        rows.sort(key=lambda row: (row.get("bidding_start_date") or "9999", row["name"]))
        return {"ipos": rows, "count": len(rows), "checked_at": now().isoformat(),
                "sources": [row for row in self.repo.health() if row["source"].startswith(("upstox:", "universe:"))],
                "refresh_seconds": 60, "recent_listing_limit": 30}

    def detail(self, ipo_id: str):
        companies = self.repo.companies()
        company = next((row for row in companies if row["id"] == ipo_id), None)
        if company is None:
            raise KeyError(ipo_id)
        self.enrich(company)
        companies, research = self.repo.companies(), self.repo.all_research()
        company = next(row for row in companies if row["id"] == ipo_id)
        result = build_detail(company, research.get(ipo_id, {}), companies, research, self.repo.observations(ipo_id))
        result["source_errors"] = [row for row in self.repo.health() if row.get("error") and (row["source"].startswith(ipo_id + ":") or row["source"] == "upstox-detail:" + ipo_id)]
        return result


_service = None
_service_lock = threading.Lock()


def get_ipo_service() -> IpoService:
    global _service
    with _service_lock:
        if _service is None:
            _service = IpoService(get_upstox())
        return _service
