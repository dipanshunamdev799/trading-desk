"""Backfill historical candles from Upstox into TimescaleDB.

Usage (from trading_v2 root, with venv active):
  .venv\\Scripts\\python.exe backend\\scripts\\backfill_candles.py ^
      --instrument "NSE_INDEX|Nifty 50" --interval 1minute --from 2026-01-01
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.db import SessionLocal  # noqa: E402
from app.services import market_data  # noqa: E402


async def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill Upstox candles into Postgres")
    parser.add_argument("--instrument", required=True, help='e.g. "NSE_INDEX|Nifty 50"')
    parser.add_argument("--interval", default="1minute")
    parser.add_argument("--from", dest="from_date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", default=None, help="YYYY-MM-DD (default today)")
    args = parser.parse_args()
    to_date = args.to_date or datetime.now().strftime("%Y-%m-%d")

    async with SessionLocal() as db:
        written = await market_data.backfill_candles(
            db,
            instrument_key=args.instrument,
            interval=args.interval,
            from_date=args.from_date,
            to_date=to_date,
        )
        rows, source = await market_data.get_candles(
            db,
            args.instrument,
            args.interval,
            from_date=args.from_date,
            to_date=to_date,
        )
    print(f"written={written} stored={len(rows)} source={source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
