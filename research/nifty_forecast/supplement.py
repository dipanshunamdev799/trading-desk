"""Append a separately hashed source batch; never rewrite an input freeze."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient

GLOBALS = {'sp500': 'GLOBAL_INDEX|^GSPC', 'dow': 'GLOBAL_INDEX|^DJI',
    'hang_seng': 'GLOBAL_INDEX|^HSI', 'gift_nifty': 'GLOBAL_INDEX|SGX NIFTY',
    'brent': 'GLOBAL_INDICATOR|BZUSD', 'usdinr': 'GLOBAL_INDICATOR|USDINR'}


def main():
    folder = ROOT / 'artifacts/nifty_forecast/2026-11-17/supplement-v1'
    folder.mkdir(parents=True, exist_ok=False)
    token = get_settings().upstox_analytics_token
    def fetch(pair):
        name, key = pair
        client = UpstoxAnalyticsClient(token, timeout=15, max_retries=0)
        at = datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
        try:
            payload = client.get_historical_candles_v3(key, 'days', 1, '2026-11-16', '2017-01-01')
            result = {'ok': True, 'payload': payload}
        except Exception as exc:
            result = {'ok': False, 'error_type': type(exc).__name__, 'error': str(exc)[:600]}
        finally:
            client.session.close()
        return name, {'instrument_key': key, 'requested_at': at,
                      'acquired_at': datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(), **result}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(fetch, pair) for pair in GLOBALS.items()]):
            name, result = f.result()
            (folder/f'daily-{name}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(name, result['ok'], len(result.get('payload', {}).get('candles', [])), flush=True)
    manifest = {'frozen_at': datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
        'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.json')}}
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
