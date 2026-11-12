"""Verify that a running frontend can serve the JavaScript and CSS its pages reference."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from urllib.parse import urlsplit

import requests


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        path = attrs.get("src") if tag == "script" else attrs.get("href") if tag == "link" and "stylesheet" in attrs.get("rel", "").split() else None
        if path and path.startswith("/_next/static/") and urlsplit(path).path.endswith((".js", ".css")) and path not in self.paths:
            self.paths.append(path)


def check_web_assets(base, pages=("/", "/ipos"), get=requests.get):
    base = base.rstrip("/")
    result = {"ok": False, "pages": [], "assets": []}
    checked = set()
    for page in pages:
        try:
            response = get(base + page, timeout=(3, 5))
            response.raise_for_status()
            parser = Assets()
            parser.feed(response.text)
            if not parser.paths:
                raise ValueError("No application assets referenced")
            result["pages"].append(page)
        except Exception as exc:
            result.update(failed_path=page, error=type(exc).__name__)
            return result
        for asset in parser.paths:
            if asset in checked:
                continue
            checked.add(asset)
            try:
                response = get(base + asset, timeout=(3, 5))
                expected = "text/css" if urlsplit(asset).path.endswith(".css") else "javascript"
                if response.status_code != 200 or expected not in response.headers.get("Content-Type", "").lower() or not response.content:
                    raise ValueError("Application asset is missing or has the wrong content type")
                result["assets"].append(asset)
            except Exception as exc:
                result.update(failed_path=asset, error=type(exc).__name__)
                return result
    result["ok"] = True
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:3000")
    args = parser.parse_args()
    result = check_web_assets(args.url)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)
