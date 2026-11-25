"""Read-only historical Upstox acquisition and complete session checks."""
from urllib.parse import quote
import sys
import requests
from .common import *


def run():
    sys.path.insert(0, str(ROOT/'backend'))
    from app.config import get_settings
    token = get_settings().upstox_analytics_token
    requests_log, bars = [], []
    data = OUT/'intraday-sources'
    data.mkdir(parents=True, exist_ok=True)
    for start in pd.date_range('2025-01-01', '2026-10-01', freq='QS'):
        end = min(start + pd.offsets.QuarterEnd(startingMonth=3), pd.Timestamp('2026-11-17'))
        key = quote('NSE_INDEX|Nifty 50', safe='')
        url = f'https://api.upstox.com/v3/historical-candle/{key}/minutes/25/{end.date()}/{start.date()}'
        path = data/f'{start.date()}.json'
        record = {'url': url, 'sent': now(), 'rows': 0}
        try:
            if not path.exists():
                response = requests.get(url, headers={'Authorization': 'Bearer '+token}, timeout=14)
                record.update(status=response.status_code, server_date=response.headers.get('Date'), received=now())
                response.raise_for_status()
                path.write_bytes(response.content)
            candles = json.loads(path.read_bytes())['data']['candles']
            bars.extend(candles)
            record.update(rows=len(candles), sha256=sha(path))
        except (requests.RequestException, KeyError, ValueError) as exc:
            record['failure'] = type(exc).__name__
        requests_log.append(record)
    price = matrix('price.csv')
    good, rejects = [], []
    expected = list(range(9*60+15, 15*60+30, 25))
    if bars:
        raw = pd.DataFrame(bars, columns=['timestamp','open','high','low','close','provider_volume','oi'])
        timestamp = pd.to_datetime(raw.timestamp, utc=True).dt.tz_convert('Asia/Kolkata')
        raw['day'] = timestamp.dt.strftime('%Y-%m-%d')
        raw['minute'] = timestamp.dt.hour*60+timestamp.dt.minute
        for day, group in raw.sort_values('minute').groupby('day'):
            if day not in price.index:
                continue
            oc = group[['open','high','low','close']].to_numpy(float)
            if list(group.minute) != expected or not np.isfinite(oc).all() or (oc<=0).any() or np.any(oc[:,1]<oc.max(axis=1)) or np.any(oc[:,2]>oc.min(axis=1)):
                rejects.append({'day': day, 'rows': len(group), 'reason': 'incomplete/nonregular grid or invalid OHLC'})
                continue
            first = oc[0,0]
            path = np.log(np.r_[first, oc[:,3]])
            good.append({'origin': day, 'intraday_rms': np.linalg.norm(np.diff(path)),
                         'first_hour_proxy': path[2]-path[0], 'last_hour_proxy': path[-1]-path[-3],
                         'close_difference_points': oc[-1,3]-price.loc[day,'close']})
    result = pd.DataFrame(good, columns=['origin','intraday_rms','first_hour_proxy','last_hour_proxy','close_difference_points']).set_index('origin')
    result.to_csv(OUT/'intraday-features.csv')
    save('intraday-audit.json', {'requests': requests_log, 'complete_sessions': len(good), 'rejected': rejects,
         'features': '25-minute close increments over exact 15-bar 09:15 to 15:30 IST grid. Opening/closing proxies each span 50 minutes. Provider index volume excluded.'})
    print('Intraday full sessions', len(good), 'received candles', len(bars), flush=True)


if __name__=='__main__':
    run()
