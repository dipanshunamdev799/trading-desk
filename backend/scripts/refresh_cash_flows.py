"""Refresh only verified FII/DII cash flows and print their source evidence.

Run from the project root:
  .venv/Scripts/python backend/scripts/refresh_cash_flows.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from app.services.nifty_cash_flows import corroborate_upstox, fetch_nse_cash
from app.services.nifty_sources import parse_flows
from app.services.nifty_store import NiftyStore
from app.services.upstox_service import get_upstox


def main():
    client = get_upstox()
    try:
        official = fetch_nse_cash(client)
        provider = []
        for factor, method in (("fii_cash", "get_fii_data"), ("dii_cash", "get_dii_data")):
            try:
                provider.extend(parse_flows(getattr(client, method)(interval="1D"), factor, datetime.now(timezone.utc).isoformat()))
            except Exception:
                # NSE explicitly identifies its own units; corroboration is optional.
                pass
        official = corroborate_upstox(official, provider)
        saved = NiftyStore(client.store).save_observations(official)
        print(json.dumps({"observations_saved": saved, "observations": official}, indent=2, ensure_ascii=False))
    finally:
        client.store.engine.dispose()


if __name__ == "__main__":
    main()
