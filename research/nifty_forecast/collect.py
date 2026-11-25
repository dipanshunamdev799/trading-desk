"""Freeze read-only market inputs without altering the dashboard or bot state."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.config import get_settings
from app.services.nifty_catalog import FACTORS, SECTIONS
from app.services.nifty_sources import INDEX_KEYS, collect_market_data
from upstox_analytics import UpstoxAnalyticsClient

IST = ZoneInfo("Asia/Kolkata")


def save(folder, name, value):
    path = folder / name
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    folder = args.out.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / "manifest.json").exists():
        raise FileExistsError("This input freeze already exists; choose another output directory")
    cutoff = datetime.now(IST)
    target = datetime.fromisoformat(args.date).date()
    if target != cutoff.date() or cutoff.hour >= 9:
        raise ValueError("This collector is for today's pre-09:00 IST experiment only")
    settings = get_settings()
    engine = create_engine(settings.database_url_sync, connect_args={"connect_timeout": 8})
    with engine.connect() as conn:
        observations = [dict(row) for row in conn.execute(text("""
            SELECT factor_id,reported_at,observed_at,payload FROM nifty_observations
            WHERE observed_at<=:cutoff AND (reported_at IS NULL OR reported_at<=:cutoff)
            ORDER BY observed_at,reported_at
        """), {"cutoff": cutoff}).mappings()]
        state = conn.execute(text("SELECT payload FROM nifty_research_state WHERE singleton=TRUE")).scalar() or {}
    engine.dispose()
    save(folder, "dashboard-retained.json", {"cutoff": cutoff.isoformat(), "factors": FACTORS,
        "sections": SECTIONS, "observations": observations, "state": state})
    print(f"Frozen {len(observations)} retained observations", flush=True)

    previous = (target - timedelta(days=1)).isoformat()
    keys = {**INDEX_KEYS, "nifty_500": "NSE_INDEX|Nifty 500"}
    jobs = [(f"daily-{factor}.json", "get_historical_candles_v3",
             {"instrument_key": key, "unit": "days", "interval": 1,
              "to_date": previous, "from_date": "2017-01-01"}) for factor, key in keys.items()]
    jobs.extend([
        ("market-status.json", "get_market_status", {"exchange": "NSE"}),
        ("market-holidays.json", "get_market_holidays", {"date": args.date}),
        ("fii-history.json", "get_fii_data", {"data_types": ["NSE_EQ|CASH", "NSE_FO|INDEX_FUTURES", "NSE_FO|INDEX_OPTIONS"], "interval": "1D"}),
        ("dii-history.json", "get_dii_data", {"interval": "1D"}),
        ("nifty-news.json", "get_news", {"category": "instrument_keys", "instrument_keys": [INDEX_KEYS["nifty_spot"]], "page_size": 30}),
    ])

    def fetch(job):
        name, method, parameters = job
        client = UpstoxAnalyticsClient(settings.upstox_analytics_token, timeout=20, max_retries=0)
        start = datetime.now(IST).isoformat()
        try:
            payload = getattr(client, method)(**parameters)
            result = {"ok": True, "payload": payload}
        except Exception as exc:
            # Avoid serializing client state or request headers (credentials).
            result = {"ok": False, "error_type": type(exc).__name__, "error": str(exc)[:600]}
        finally:
            client.session.close()
        return name, {"method": method, "parameters": parameters, "requested_at": start,
                      "acquired_at": datetime.now(IST).isoformat(), **result}

    with ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(fetch, job) for job in jobs]):
            name, result = future.result()
            save(folder, name, result)
            payload = result.get("payload")
            n = len(payload.get("candles", [])) if isinstance(payload, dict) else len(payload) if isinstance(payload, list) else None
            print(f"{name}: ok={result['ok']} rows={n}", flush=True)

    client = UpstoxAnalyticsClient(settings.upstox_analytics_token, timeout=12, max_retries=0)
    current = collect_market_data(client=client, include_public=True)
    client.session.close()
    save(folder, "dashboard-fresh.json", current)
    print(f"Fresh context: {len(current['observations'])} observations; {len(current['source_errors'])} source warnings", flush=True)
    manifest = {"target_date": args.date, "decision_started_at": cutoff.isoformat(),
        "frozen_at": datetime.now(IST).isoformat(), "source": "Upstox read-only REST, retained dashboard, public context adapters",
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                  for p in sorted(folder.glob("*.json"))}}
    save(folder, "manifest.json", manifest)
    print(json.dumps({"folder": str(folder), "frozen_at": manifest["frozen_at"]}), flush=True)


if __name__ == "__main__":
    main()
