"""Freeze completed NIFTY daily candles for directional research (no orders)."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient


def main():
    out = ROOT / 'artifacts' / 'directional_research'
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'nifty-upstox-1day.json'
    if target.exists():
        print('Using frozen daily file:', target.name)
        return
    client = UpstoxAnalyticsClient(get_settings().upstox_analytics_token, timeout=30, max_retries=1)
    payload = client.get_historical_candles_v3('NSE_INDEX|Nifty 50', 'days', 1, '2026-11-08', '2017-01-01')
    rows = sorted((dict(zip(('ts', 'open', 'high', 'low', 'close', 'volume', 'oi'), r))
                   for r in payload['candles'] if '2017-01-01' <= r[0][:10] <= '2026-11-08'),
                  key=lambda r: r['ts'])
    if not rows:
        raise RuntimeError('No daily observations returned')
    target.write_text(json.dumps(rows), encoding='utf-8')
    manifest = {'instrument': 'NSE_INDEX|Nifty 50', 'from': '2017-01-01', 'to': '2026-11-08',
                'bars': len(rows), 'first': rows[0]['ts'], 'last': rows[-1]['ts'],
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    (out / 'daily-fetch-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
