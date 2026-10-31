"""IPO source identity, missing-data, period and pagination regressions."""
import sys
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.services import ipo_sources as sources
from app.services.ipo_factors import build_detail, calendar_status, growth, matched
from app.services.ipo_service import IpoService
from app.services.market_store import IST, expiry_time, now

FUNDAMENTALS = '''<h1>Example Polymers IPO Details 2026</h1>
<table><tr><td>Issue Size</td><td>₹100 Cr</td></tr><tr><td>Fresh Issue</td><td>₹100 Cr</td></tr><tr><td>Lead Managers</td><td>Example Capital</td></tr></table>
<h2>About Company</h2><p>Example manufactures specialised materials. Its facility has ISO 9001 certification.</p>
<h2>IPO Objectives</h2><table><tr><th>#</th><th>Issue Objects</th><th>Amt (₹ Cr.)</th></tr><tr><td>1</td><td>Repayment of borrowings</td><td>20</td></tr></table>
<h2>Company Financials</h2><table><tr><th>Period Ended</th><th>30 Jun 2026</th><th>31 Mar 2026</th><th>31 Mar 2025</th></tr>
<tr><td>Total Income</td><td>30</td><td>120</td><td>100</td></tr><tr><td>Profit After Tax</td><td>2</td><td>15</td><td>10</td></tr><tr><td>Total Borrowing</td><td>35</td><td>40</td><td>50</td></tr></table>
<h2>Key Performance Indicators</h2><table><tr><th>KPI</th><th>Jun 30, 2026</th><th>Mar 31, 2026</th></tr>
<tr><td>ROE</td><td>5%</td><td>20%</td></tr><tr><td>RoNW</td><td>4%</td><td>18%</td></tr><tr><td>EBITDA Margin</td><td>8%</td><td>16%</td></tr></table>
<table><tr><th>Metric</th><th>Pre IPO</th><th>Post IPO</th></tr><tr><td>P/E (x)</td><td>20</td><td>25</td></tr><tr><td>Promoter Holding</td><td>90%</td><td>65%</td></tr></table>'''


class SourceTests(unittest.TestCase):
    def test_yearless_dates_work_on_python_315_and_rollover_is_explicit(self):
        self.assertEqual(sources.source_date("29-Oct", reference=date(2026, 10, 24)), "2026-10-29")
        self.assertEqual(sources.source_date("2-Jan", reference=date(2026, 12, 20)), "2027-01-02")
        self.assertTrue(sources.source_date("24-Oct 20:02", reference=date(2026, 10, 24)).startswith("2026-10-24T20:02"))

    def test_missing_gmp_is_not_the_zero_percentage_beside_it(self):
        self.assertIsNone(sources.number("₹--"))
        self.assertIsNone(sources.money_cr("Approx [.] Equity Shares"))
        self.assertIsNone(sources.money_cr("1,000,000 shares"))
        self.assertEqual(sources.money_cr("1,000,000 shares (₹45.00 Cr)"), 45)
        self.assertEqual(sources.number("₹-5"), -5)

    def test_wrong_company_on_a_200_response_is_rejected(self):
        with self.assertRaises(ValueError):
            sources.parse_fundamentals("<h1>Beauty Garage IPO Details</h1>", "Core4 Engineers")
        self.assertFalse(matched({"name": "Example Polymers IPO", "maximum_price": 100}, {"name": "Example Polymers", "price": 200}))
        self.assertFalse(matched({"name": "Example Polymers IPO", "bidding_end_date": "2026-10-27"}, {"name": "Example Polymers", "close_date": "2026-11-27"}))

    def test_gmp_history_keeps_an_explicit_latest_quote_gap(self):
        html = '<h1>Example Polymers IPO GMP Today</h1><table><tr><th>GMP Date</th><th>GMP</th></tr><tr><td>24-Oct 17:00</td><td>₹-- (0.00%)</td></tr><tr><td>23-Oct 17:00</td><td>₹10 (10%)</td></tr></table>'
        result = sources.parse_gmp(html, "Example Polymers IPO")
        self.assertIsNone(result["gmp"])
        self.assertEqual(len(result["history"]), 2)
        self.assertEqual(result["history"][0]["value"], 10)

    def test_financial_tables_keep_periods_and_sources_separate(self):
        data = sources.parse_fundamentals(FUNDAMENTALS, "Example Polymers")
        self.assertEqual(data["objects"], [{"purpose": "Debt repayment", "amount_cr": 20}])
        self.assertEqual(data["valuation"]["Promoter Holding"]["post"], 65)
        self.assertIn("ISO 9001", data["certifications"])
        self.assertLessEqual(len(data["business_excerpt"].split()), 24)
        rate, period = growth(data["financials"], "Total Income")
        self.assertAlmostEqual(rate, 20)
        self.assertEqual(period, "FY2025 → FY2026")

    def test_public_http_fetch_rejects_private_or_insecure_destinations(self):
        for url in ("http://ipowatch.in/", "https://127.0.0.1/", "https://www.investorgain.com:8443/", "https://user@ipowatch.in/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                sources.fetch_html(url)


class FactorTests(unittest.TestCase):
    def company(self, **changes):
        return {"id": "example", "name": "Example Polymers IPO", "status": "open", "catalog_source": "Upstox",
                "bidding_start_date": "2026-10-27", "bidding_end_date": "2026-10-29", "maximum_price": 100,
                "issue_size": 100, "total_subscription": "0", "fetched_at": now().isoformat(), **changes}

    def detail(self, company=None, research=None):
        result = build_detail(company or self.company(), research or {})
        return result, {row["id"]: row for row in result["factors"]}

    def test_all_24_factors_are_ordered_and_early_totals_are_pending_not_zero(self):
        result, factors = self.detail()
        self.assertEqual([factor["number"] for factor in result["factors"]], list(range(1,25)))
        for key in ("qib", "nii", "retail", "total", "subscription_trend"):
            self.assertIsNone(factors[key]["value"])
            self.assertEqual(factors[key]["status"], "pending")
        self.assertEqual(result["company"]["stage"], "upcoming")

    def test_real_zero_qib_after_bidding_starts_is_preserved(self):
        _, factors = self.detail(self.company(bidding_start_date="2026-10-23"), {
            "subscriptions": {"data": {"qib": 0, "nii": 0.05, "retail": 0.14, "total": 0.08}, "fetched_at": now().isoformat()}})
        self.assertEqual(factors["qib"]["value"], 0)
        self.assertEqual(factors["qib"]["status"], "available")
        self.assertIsNone(factors["nii"]["value"]["snii"])

    def test_ratios_use_full_fiscal_year_but_borrowings_use_latest_period(self):
        data = sources.parse_fundamentals(FUNDAMENTALS, "Example Polymers")
        _, factors = self.detail(research={"fundamentals": {"data": data, "fetched_at": now().isoformat()}})
        self.assertEqual(factors["returns"]["value"]["roe"], 20)
        self.assertEqual(factors["returns"]["period"], "FY2026")
        self.assertEqual(factors["borrowings"]["value"], 35)
        self.assertEqual(factors["borrowings"]["period"], "2026-06-30")
        self.assertEqual(factors["fresh_ofs"]["value"]["ofs_pct"], 0)
        self.assertEqual(factors["sector"]["status"], "unavailable")

    def test_stale_research_is_not_marked_as_refreshed_by_page_check(self):
        _, factors = self.detail(research={"index": {"data": {"gmp": 10}, "fetched_at": (now()-timedelta(days=1)).isoformat()}})
        self.assertEqual(factors["gmp"]["status"], "stale")
        self.assertIsNone(factors["gmp"]["reported_at"])

    def test_sme_market_maker_remainder_is_not_invented_as_ofs(self):
        _, factors = self.detail(research={"fundamentals": {"data": {"facts": {
            "total issue size": "₹54.82 Cr", "fresh issue": "₹48.12 Cr",
            "reserved for market maker": "₹6.70 Cr"}}, "fetched_at": now().isoformat()}})
        self.assertAlmostEqual(factors["fresh_ofs"]["value"]["fresh_pct"], 48.12 / 54.82 * 100)
        self.assertIsNone(factors["fresh_ofs"]["value"]["ofs_cr"])
        self.assertIn("market maker", factors["fresh_ofs"]["note"])
        _, factors = self.detail(research={"fundamentals": {"data": {"facts": {
            "issue size": "₹100 Cr", "offer for sale": "₹100 Cr"}}, "fetched_at": now().isoformat()}})
        self.assertEqual(factors["fresh_ofs"]["value"]["fresh_cr"], 0)
        self.assertEqual(factors["fresh_ofs"]["value"]["ofs_pct"], 100)

    def test_loss_or_zero_prior_profit_is_not_a_misleading_growth_percentage(self):
        value, _ = growth({"periods": ["31 Mar 2026", "31 Mar 2025"], "rows": {"PAT": [10, -5]}}, "PAT")
        self.assertIsNone(value)

    def test_undated_announcements_are_not_scheduled_or_subscribed(self):
        result, factors = self.detail(self.company(bidding_start_date=None, bidding_end_date=None, total_subscription="0.42"))
        self.assertEqual(result["company"]["stage"], "announced")
        self.assertIsNone(factors["total"]["value"])

    def test_pagination_collects_every_upcoming_page(self):
        client = Mock()
        client.get_ipos.side_effect = lambda **kwargs: ([{"id": f"ipo-{i}"} for i in range(30)] if kwargs["status"] == "upcoming" and kwargs["page_number"] == 1 else [{"id":"last-ipo"}] if kwargs["status"] == "upcoming" else [])
        service = IpoService(client)
        service.repo = Mock()
        service._public = Mock()
        service.refresh_catalog()
        self.assertEqual(len(service.repo.set_feed.call_args_list[0].args[1]), 31)
        self.assertEqual(client.get_ipos.call_count, 5)


if __name__ == "__main__":
    unittest.main()
