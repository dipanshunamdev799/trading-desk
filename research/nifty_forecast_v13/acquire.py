"""Only historical candle reads. Raw replies and availability receipts remain in V13."""
import sys
import time
from urllib.parse import quote

import requests
from .common import ROOT, OUT, FREEZE, pd, sha, now, save, register


def acquire():
    register()
    sys.path.insert(0, str(ROOT / 'backend'))
    from app.config import get_settings

    token = get_settings().upstox_analytics_token
    folder = OUT / 'sources/upstox'
    folder.mkdir(parents=True, exist_ok=True)
    requests_log = []
    key = quote('NSE_INDEX|Nifty 50', safe='')
    jobs = []
    for size in (5, 1):
        for start in pd.date_range('2025-01-01', FREEZE, freq='MS'):
            end = min(start + pd.offsets.MonthEnd(), pd.Timestamp(FREEZE))
            jobs.append((f'nifty-{size}m-{start.date()}', key, 'minutes', size, str(start.date()), str(end.date())))
    local = pd.Timestamp(now())
    bound = min('2026-12-31', str((local - pd.Timedelta(days=int(local.hour < 16))).date()))
    if bound > FREEZE:
        jobs.append(('refresh-nifty', key, 'days', 1, '2026-11-18', bound))
    jobs += [(name, quote(symbol, safe=''), 'days', 1, '2025-01-01', FREEZE)
             for name, symbol in [('india-vix', 'NSE_INDEX|India VIX'), ('etf-nifty', 'NSE_EQ|INF204KB14I2')]]
    with requests.Session() as session:
        for name, symbol, unit, size, start, end in jobs:
            url = f'https://api.upstox.com/v3/historical-candle/{symbol}/{unit}/{size}/{end}/{start}'
            file = folder / (name + '.json')
            receipt = dict(source=url, name=name, start=start, end=end, sent=now())
            if not file.exists():
                for attempt in range(2):
                    time.sleep(.37)
                    try:
                        response = session.get(url, headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}, timeout=13)
                        receipt.update(http=response.status_code, received=now(), server_date=response.headers.get('Date'))
                        if response.ok and 'candles' in response.json().get('data', {}):
                            file.write_bytes(response.content)
                            break
                        if response.status_code not in (429, 500, 502, 503, 504):
                            break
                        time.sleep(1.1)
                    except (requests.RequestException, ValueError) as exc:
                        receipt.update(error=type(exc).__name__)
            if file.exists():
                receipt.update(path=str(file.relative_to(OUT)), sha256=sha(file))
            requests_log.append(receipt)
            save('acquisition.json', requests_log)
    print('Upstox historical sources available', sum('path' in r for r in requests_log), '/', len(jobs), flush=True)


if __name__ == '__main__':
    acquire()
