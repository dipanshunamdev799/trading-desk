"""Regression for HTML-only readiness after replacing a running Next.js build."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from check_web_assets import check_web_assets


class WebAssetsTests(unittest.TestCase):
    def page(self):
        return Mock(text='<link rel="stylesheet" href="/_next/static/style.css"><script src="/_next/static/webpack-old.js"></script>')

    def asset(self, content_type, status=200):
        return Mock(status_code=status, headers={"Content-Type": content_type}, content=b"asset")

    def test_healthy_html_and_api_do_not_mask_a_missing_runtime(self):
        get = Mock(side_effect=[self.page(), self.asset("text/css"), self.asset("text/html", 400)])
        result = check_web_assets("http://127.0.0.1:3000", get=get)
        self.assertFalse(result["ok"])
        self.assertEqual(result["failed_path"], "/_next/static/webpack-old.js")

    def test_html_fallback_is_not_accepted_as_javascript(self):
        get = Mock(side_effect=[self.page(), self.asset("text/css"), self.asset("text/html")])
        self.assertFalse(check_web_assets("http://127.0.0.1:3000", get=get)["ok"])

    def test_shared_assets_are_checked_once_and_both_pages_are_checked(self):
        get = Mock(side_effect=[self.page(), self.asset("text/css"), self.asset("application/javascript"), self.page()])
        result = check_web_assets("http://127.0.0.1:3000", get=get)
        self.assertTrue(result["ok"])
        self.assertEqual(result["pages"], ["/", "/ipos"])
        self.assertEqual(get.call_count, 4)


if __name__ == "__main__":
    unittest.main()
