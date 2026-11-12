"""Freeze research candles without changing the application's database or credentials."""
import calendar
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient


def main():
    out = ROOT / 'artifacts' / 'directional_research'
    cache = out / 'upstox-windows'
    cache.mkdir(parents=True, exist_ok=True)
    client = UpstoxAnalyticsClient(get_settings().upstox_analytics_token, timeout=20, max_retries=1)
    rows, audit = {}, []
    for year in (2025, 2026):
        for month in range(1, 13 if year == 2025 else 12):
            first = f'{year}-{month:02d}-01'
            last = f'{year}-{month:02d}-{8 if (year, month) == (2026, 11) else calendar.monthrange(year, month)[1]:02d}'
            path = cache / f'{first}-5m.json'
            try:
                if path.exists():
                    payload = json.loads(path.read_text())
                else:
                    payload = client.get_historical_candles_v3('NSE_INDEX|Nifty 50', 'minutes', 5, last, first)
                    path.write_text(json.dumps(payload), encoding='utf-8')
                    time.sleep(.25)
                candles = payload.get('candles', [])
                for r in candles:
                    if first <= str(r[0])[:10] <= last:
                        rows[r[0]] = dict(zip(('ts','open','high','low','close','volume','oi'), r))
                audit.append({'from': first, 'to': last, 'bars': len(candles), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
                print(first, len(candles), flush=True)
            except Exception as exc:
                audit.append({'from': first, 'to': last, 'error': type(exc).__name__, 'status': getattr(exc, 'status_code', None)})
                print(first, 'FAILED', type(exc).__name__, flush=True)
                if getattr(exc, 'status_code', None) in (401,403):
                    break
    target = out / 'nifty-upstox-5minute.json'
    target.write_text(json.dumps(sorted(rows.values(), key=lambda r:r['ts'])), encoding='utf-8')
    (out / 'fetch-manifest.json').write_text(json.dumps({'instrument':'NSE_INDEX|Nifty 50','cutoff':'2026-11-08','bars':len(rows),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'windows':audit}, indent=2))
    print('TOTAL',len(rows), flush=True)


if __name__ == '__main__':
    main()
