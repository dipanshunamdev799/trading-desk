"""IPO source identity, missing-data, period and pagination regressions."""
import sys
import json
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.services import ipo_sources as sources
from app.services.ipo_factors import build_detail, calendar_status, growth, matched
from app.services.ipo_service import IpoService
from app.services.ipo_store import IpoStore
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

SUBSCRIPTION_FEED = json.loads((Path(__file__).parent / "fixtures/ipowatch-subscriptions.json").read_text(encoding="utf-8"))


def subscription_feed(records):
    issue = {"ipoId": 1, "ipoName": "Example Polymers", "ipoCloseDate": "2026-11-05", "subscriptionList": records}
    return {"status": 1, "result": [{"ipoSubscriptionJson": [issue]}]}


class SourceTests(unittest.TestCase):
    def test_current_subscription_feed_preserves_all_categories_and_six_published_days(self):
        parsed = sources.parse_subscription_index(json.dumps(SUBSCRIPTION_FEED))
        row = parsed["rows"][0]
        self.assertEqual((row["name"], row["close_date"]), ("Antala Industries", "2026-11-05"))
        self.assertEqual({key: row[key] for key in ("qib", "nii", "snii", "bnii", "retail", "total")},
                         {"qib": 66.72, "nii": 49.94, "snii": 8.30, "bnii": 70.40, "retail": 5.22, "total": 12.79})
        self.assertEqual(len(row["history"]), 6)
        self.assertEqual(row["reported_date"], "2026-11-05")
        self.assertIsNone(row["reported_time"])

    def test_subscription_zero_and_missing_are_distinct_without_carrying_prior_day(self):
        feed = subscription_feed([
            {"categoryName": "QIB (Ex. Anchor)", "subscriptionDate": "2026-11-01", "subscriptionValue": "0"},
            {"categoryName": "Retail", "subscriptionDate": "2026-11-02", "subscriptionValue": "--"}])
        row = sources.parse_subscription_feed(feed)["rows"][0]
        self.assertEqual(row["history"][0]["qib"], 0)
        self.assertIsNone(row["qib"])
        self.assertIsNone(row["retail"])
        self.assertIsNone(row["nii"])

    def test_empty_subscriptions_require_a_valid_success_envelope(self):
        for feed in ({"status": 1, "result": []}, {"status": 1, "result": [{"ipoSubscriptionJson": "[]"}]}):
            self.assertEqual(sources.parse_subscription_feed(feed)["rows"], [])
        for feed in ({"status": 0, "result": []}, {"status": 1}, {"status": True, "result": []}, {"status": 1, "result": [{}]}, {"status": 1, "result": [{"ipoSubscriptionJson": {}}]}):
            with self.subTest(feed=feed), self.assertRaises(ValueError):sources.parse_subscription_feed(feed)
        with self.assertRaises(ValueError):
            sources.parse_subscription_index('<h1>IPO Subscription Status</h1><p>Tracking 0 open IPOs</p><p>Loading open IPO subscription tracker...</p>')

    def test_invalid_subscription_values_and_dates_do_not_become_figures(self):
        for value in (True, -1, float("nan"), float("inf"), "HTTP 500", "1,2", "-5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                sources.parse_subscription_feed(subscription_feed([{"categoryName": "QIB", "subscriptionDate": "2026-11-05", "subscriptionValue": value}]))
        with self.assertRaises(ValueError):
            sources.parse_subscription_feed(subscription_feed([{"categoryName": "QIB", "subscriptionDate": "invalid", "subscriptionValue": 1}]))

    def test_conflicting_publication_day_values_are_rejected(self):
        record = {"categoryName": "NII", "subscriptionDate": "2026-11-05", "subscriptionValue": "1"}
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            sources.parse_subscription_feed(subscription_feed([record, {**record, "subscriptionValue": "2"}]))

    def test_legacy_subscription_tables_still_parse(self):
        html = '<table><tr><th>IPO</th><th>Type</th><th>Close</th><th>QIB</th><th>NII</th><th>Retail</th><th>Total</th><th>Time</th></tr><tr><td>Example Polymers</td><td>SME</td><td>2026-11-05</td><td>0</td><td>0.1</td><td>--</td><td>0.08</td><td>17:00</td></tr></table>'
        row = sources.parse_subscription_index(html)["rows"][0]
        self.assertEqual(row["qib"], 0);self.assertIsNone(row["retail"])
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
        # Keep the upcoming-IPO scenario independent of the wall clock.
        start = (now().astimezone(IST).date() + timedelta(days=3)).isoformat()
        end = (now().astimezone(IST).date() + timedelta(days=5)).isoformat()
        result, factors = self.detail(self.company(bidding_start_date=start, bidding_end_date=end))
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

    def test_newer_published_subscriptions_supply_correct_source_and_history(self):
        row = sources.parse_subscription_feed(SUBSCRIPTION_FEED)["rows"][0]
        research = {"subscriptions": {"data": row, "reported_date": row["reported_date"], "fetched_at": now().isoformat(), "source_url": sources.WATCH_SUBSCRIPTIONS},
                    "subscription_detail": {"data": {"latest": {"qib": 1, "nii": 2}, "history": [{"at": "2026-11-01", "qib": 1}]}, "fetched_at": now().isoformat()}}
        result, factors = self.detail(self.company(status="closed", bidding_end_date="2026-11-05", total_subscription=None), research)
        self.assertEqual(factors["qib"]["value"], 66.72)
        self.assertEqual(factors["nii"]["value"], {"nii": 49.94, "snii": 8.30, "bnii": 70.40})
        self.assertEqual(factors["total"]["value"], 12.79)
        self.assertEqual(factors["qib"]["source"], "IPOWatch (public)")
        self.assertEqual(factors["qib"]["reported_at"], "2026-11-05")
        self.assertEqual(factors["subscription_trend"]["source"], "IPOWatch (public)")
        self.assertEqual(len(result["subscription_history"]), 6)

    def test_detail_total_has_its_actual_source_when_upstox_total_is_missing(self):
        _, factors = self.detail(self.company(total_subscription=None), {"subscription_detail": {"data": {"latest": {"total": 2}}, "fetched_at": now().isoformat()}})
        self.assertEqual(factors["total"]["value"], 2)
        self.assertEqual(factors["total"]["source"], "InvestorGain (public)")

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


class SubscriptionServiceTests(unittest.TestCase):
    def test_subscription_refresh_uses_current_feed_and_new_cache_namespace(self):
        client = Mock();client.store.read.side_effect = lambda method, parameters, load, **kw: load()
        service = IpoService(client);service.repo = Mock()
        with patch.object(sources, "fetch_html", return_value=json.dumps(SUBSCRIPTION_FEED)) as fetch:
            service._public("subscriptions", sources.WATCH_SUBSCRIPTIONS)
        fetch.assert_called_once_with(sources.WATCH_SUBSCRIPTIONS_API)
        params = client.store.read.call_args.args[1]
        self.assertEqual(params["parser_version"], 2)
        self.assertEqual(params["url"], sources.WATCH_SUBSCRIPTIONS_API)
        service.repo.sync.assert_called_once_with("universe:subscriptions")

    def test_failed_feed_remains_an_error_and_does_not_clear_health(self):
        client = Mock();client.store.read.side_effect = lambda method, parameters, load, **kw: load()
        service = IpoService(client);service.repo = Mock()
        with patch.object(sources, "fetch_html", return_value='{"status":0,"result":[]}'):
            service._public("subscriptions", sources.WATCH_SUBSCRIPTIONS)
        self.assertIn("ValueError", service.repo.sync.call_args.args[1])
        self.assertIn("universe:subscriptions", service.failures)

    def test_normalization_matches_issuer_and_retains_date_without_inventing_time(self):
        service = IpoService(Mock());conn = Mock()
        conn.execute.return_value.scalars.return_value = [{"id": "antala", "name": "Antala Industries IPO", "status": "closed", "bidding_end_date": "2026-11-05"}]
        with patch.object(IpoStore, "save_research") as save:
            service._save_subscription_index(conn, sources.parse_subscription_feed(SUBSCRIPTION_FEED), now())
        record = save.call_args.args[1]
        self.assertEqual(record["ipo_id"], "antala")
        self.assertEqual(record["reported_date"], "2026-11-05");self.assertIsNone(record["reported_at"])
        self.assertEqual(record["metrics"]["bnii"], 70.40)
        self.assertEqual(len(record["data"]["history"]), 6)


if __name__ == "__main__":
    unittest.main()
