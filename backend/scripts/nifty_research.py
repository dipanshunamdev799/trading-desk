"""Collect, inspect and import NIFTY research without running the web app.

Examples (from the project root):
  .venv/Scripts/python backend/scripts/nifty_research.py refresh
  .venv/Scripts/python backend/scripts/nifty_research.py watch --seconds 300
  .venv/Scripts/python backend/scripts/nifty_research.py dashboard --output data/nifty-dashboard.json
  .venv/Scripts/python backend/scripts/nifty_research.py import research.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from app.routers.nifty import EventBatch, ObservationBatch
from app.services.nifty_catalog import FACTORS, FACTOR_MAP, SECTIONS
from app.services.nifty_service import get_nifty_service, utc_now


def emit(value, output=None):
    payload = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str)
    if output:
        destination = Path(output).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
        print(f"Written {destination}")
    else:
        print(payload)


def main():
    parser = argparse.ArgumentParser(description="NIFTY factor research collector and source import")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("refresh", help="Collect available configured/public sources once")
    watch = sub.add_parser("watch", help="Collect repeatedly; Ctrl+C stops")
    watch.add_argument("--seconds", type=int, default=300)
    for command in ("catalog", "dashboard"):
        sub.add_parser(command).add_argument("--output")
    imp = sub.add_parser("import", help="Import sourced factor observations and/or calendar events from JSON")
    imp.add_argument("file", type=Path)
    history = sub.add_parser("history")
    history.add_argument("factor_id", choices=sorted(FACTOR_MAP))
    history.add_argument("--limit", type=int, default=365)
    history.add_argument("--output")
    args = parser.parse_args()
    if args.command == "catalog":
        emit({"sections": SECTIONS, "factors": FACTORS, "total": len(FACTORS)}, args.output)
        return 0
    service = get_nifty_service()
    try:
        if args.command == "refresh":
            result = service.refresh()
            emit(result)
            return 1 if result["status"] == "failed" else 0
        if args.command == "watch":
            if args.seconds < 60:
                parser.error("--seconds must be at least 60")
            while True:
                emit(service.refresh())
                time.sleep(args.seconds)
        if args.command == "dashboard":
            emit(service.dashboard(auto_refresh=False), args.output)
        elif args.command == "history":
            if not 1 <= args.limit <= 2000:
                parser.error("--limit must be between 1 and 2000")
            emit(service.history(args.factor_id, args.limit), args.output)
        elif args.command == "import":
            payload = json.loads(args.file.read_text(encoding="utf-8-sig"))
            if not isinstance(payload, dict) or not (payload.get("observations") or payload.get("events")):
                parser.error("JSON requires observations and/or events arrays")
            # Validate the entire file before committing either batch.
            observations = ObservationBatch.model_validate({"observations": payload["observations"]}) if payload.get("observations") else None
            events = EventBatch.model_validate({"events": payload["events"]}) if payload.get("events") else None
            result = {}
            if observations:
                rows = [{**row.model_dump(mode="json", exclude_none=True), "observed_at": utc_now(),
                         "unit": row.unit or FACTOR_MAP[row.factor_id]["unit"], "basis": "Sourced research import"} for row in observations.observations]
                result["observations_saved"] = service.repo.save_observations(rows)
            if events:
                result["events_saved"] = service.repo.save_events([row.model_dump(mode="json", exclude_none=True) for row in events.events])
            emit(result)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        from app.services.upstox_service import get_market_store
        get_market_store().engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
