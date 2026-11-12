"""Read-only checks of the running local app, API proxy and browser websocket."""
from __future__ import annotations

import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import json
from pathlib import Path
import time

import requests
from websockets.asyncio.client import connect
from check_web_assets import check_web_assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:3000")
    args = parser.parse_args()
    base = args.url.rstrip("/")
    results = []
    asset_check = check_web_assets(base)
    results.append({"path": "frontend JavaScript/CSS", "ok": asset_check["ok"], "failed_path": asset_check.get("failed_path")})
    print(f"{'PASS' if asset_check['ok'] else 'FAIL'} frontend JavaScript/CSS", flush=True)

    def check(path, validate=None):
        start = time.monotonic()
        result = {"path": path}
        body = None
        try:
            response = requests.get(base + path, timeout=(5, 120))
            response.raise_for_status()
            if path.startswith("/api/"):
                body = response.json()
                if validate:
                    assert validate(body), "Unexpected API response"
            else:
                assert "<title>Trading Desk</title>" in response.text, "Missing app shell"
            result["ok"] = True
        except Exception as exc:
            # Do not echo upstream bodies, which may include sensitive context.
            result.update(ok=False, error=type(exc).__name__)
        result["seconds"] = round(time.monotonic() - start, 2)
        results.append(result)
        print(f"{'PASS' if result['ok'] else 'FAIL'} {path} ({result['seconds']}s)", flush=True)
        return body

    checks = [
        (path, None) for path in ("/", "/nifty", "/maxpain", "/ipos", "/backtests", "/strategies", "/paper", "/credit-spreads", "/data", "/charts")
    ] + [
        ("/api/health", lambda b: b["ok"] and b["database"] == "ok"),
        ("/api/paper/summary", lambda b: "total_pnl" in b),
        ("/api/paper/orders", lambda b: isinstance(b, list)),
        ("/api/paper/positions", lambda b: isinstance(b, list)),
        ("/api/data/coverage", lambda b: isinstance(b, list)),
        ("/api/data/integration", lambda b: "candles" in b["hypertables"]),
        ("/api/nifty/dashboard", lambda b: bool(b["sections"])),
        ("/api/strategies/evaluate", lambda b: len(b["strategies"]) == 11 and all(s["deployment"] == "RESEARCH ONLY" and s["calibrated_probability"] is None for s in b["strategies"])),
        ("/api/credit-spreads/dashboard", lambda b: "summary" in b),
        ("/api/credit-spreads/market", lambda b: "options" in b),
        ("/api/options/expiries", lambda b: isinstance(b, list)),
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda item: check(*item), checks))
    backtests = check("/api/backtests", lambda b: isinstance(b, list))
    if backtests:
        check("/api/backtests/" + requests.utils.quote(backtests[0]["slug"], safe=""), lambda b: "equity" in b)
    ipos = check("/api/ipos", lambda b: "ipos" in b)
    if ipos and ipos["ipos"]:
        check("/api/ipos/" + requests.utils.quote(ipos["ipos"][0]["id"], safe=""), lambda b: len(b["factors"]) == 24)
    snapshot = check("/api/options/max-pain?view=latest", lambda b: "payout_curve" in b)
    if snapshot:
        query = requests.compat.urlencode({key: snapshot[key] for key in ("expiry", "as_of", "instrument_key")})
        for path in ("max-pain/intraday", "pcr/intraday", "iv/history"):
            check("/api/options/" + path + "?" + query, lambda b: "data_available" in b)
        end = date.fromisoformat(snapshot["as_of"])
        query = requests.compat.urlencode({"instrument_key": snapshot["instrument_key"], "interval": "5minute",
                                          "from_date": (end - timedelta(days=7)).isoformat(), "to_date": end.isoformat()})
        check("/api/nifty/price-action?" + query, lambda b: "study" in b and "candles" in b)

    async def websocket():
        start = time.monotonic()
        result = {"path": "/api/market/live"}
        try:
            async with connect(base.replace("http", "ws", 1) + result["path"], origin=base, open_timeout=10) as socket:
                await socket.send(json.dumps({"type": "watch", "instrument_keys": ["NSE_INDEX|Nifty 50"]}))
                event = json.loads(await asyncio.wait_for(socket.recv(), timeout=30))
                assert event["type"] == "market_update" and "status" in event
            result["ok"] = True
        except Exception as exc:
            result.update(ok=False, error=type(exc).__name__)
        result["seconds"] = round(time.monotonic() - start, 2)
        results.append(result)
        print(f"{'PASS' if result['ok'] else 'FAIL'} websocket proxy ({result['seconds']}s)", flush=True)

    asyncio.run(websocket())
    report = Path(__file__).resolve().parents[1] / "data" / "logs" / "smoke.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=2), encoding="utf-8")
    failed = sum(not result["ok"] for result in results)
    print(f"{len(results) - failed}/{len(results)} checks passed; report: {report}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
