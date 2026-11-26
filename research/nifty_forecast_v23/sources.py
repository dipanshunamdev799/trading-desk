"""Read-only foreign provenance and independent daily path verification."""
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from io import BytesIO

import requests

from .common import *
from research.nifty_forecast_v22.sources import UA

SERIES = {'us': '^GSPC', 'japan': '^N225', 'hong_kong': '^HSI', 'uk': '^FTSE', 'france': '^FCHI', 'dax_total': '^GDAXI'}
FRED = {'us': 'SP500', 'japan': 'NIKKEI225'}


def broker(job):
    from research.nifty_forecast_v15.sources import token, API
    code, symbol = job
    name = f'sources/foreign-broker/{code}.json'
    url = API + quote('GLOBAL_INDEX|' + symbol, safe='') + f'/days/1/{FREEZE}/{FIRST}'
    receipt = dict(code=code, vendor='Upstox', symbol=symbol, sent_at=now(), requested=[FIRST, FREEZE], url=url)
    try:
        key = token()
        if not key:
            return None, receipt | {'status': 'credential unavailable'}
        res = requests.get(url, headers=UA | {'Authorization': 'Bearer ' + key}, timeout=(8, 20))
        receipt.update(status=res.status_code, received_at=now(), server_date=res.headers.get('Date'))
        if not res.ok:
            return None, receipt
        raw = res.json()['data']['candles']
        clipped = [x for x in raw if FIRST <= x[0][:10] <= FREEZE]
        assert len(clipped) == len(raw), 'unrequested date returned'
        save(name, dict(code=code, symbol=symbol, rows=clipped, receipt=receipt))
        a = pd.DataFrame([(r[0][:10], r[0], *r[1:5]) for r in clipped],
                         columns=['day', 'broker_time', 'open2', 'high2', 'low2', 'close2'])
        a = a.sort_values('broker_time').drop_duplicates('day', keep='last')
        return a, receipt | dict(rows=len(a), duplicate_labels=len(clipped)-len(a), file=name, sha256=sha(OUT / name))
    except (requests.RequestException, KeyError, TypeError, ValueError, AssertionError) as err:
        return None, receipt | dict(error=type(err).__name__)


def fred(job):
    code, symbol = job
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv'
    receipt = dict(code=code, vendor='Federal Reserve Bank of St. Louis', symbol=symbol, sent_at=now(), requested=[FIRST, FREEZE])
    try:
        res = requests.get(url, headers=UA, params={'id': symbol, 'cosd': FIRST, 'coed': FREEZE}, timeout=(7, 18))
        receipt.update(status=res.status_code, received_at=now(), url=res.url)
        if not res.ok:
            return None, receipt
        data = pd.read_csv(BytesIO(res.content))
        assert data.iloc[:, 0].between(FIRST, FREEZE).all()
        rows = pd.DataFrame({'day': data.iloc[:, 0], 'fred_close': pd.to_numeric(data[symbol], errors='coerce')}).dropna()
        name = f'sources/fred/{code}.csv'
        write(name, rows)
        return rows, receipt | dict(rows=len(rows), file=name, sha256=sha(OUT / name))
    except (requests.RequestException, KeyError, TypeError, ValueError, AssertionError) as err:
        return None, receipt | dict(error=type(err).__name__)


def run():
    tape = csv('international-daily-book.csv.gz', V22, usecols=['code','day','role','open','high','low','close','source_timestamp','ohlc_valid'])
    with ThreadPoolExecutor(max_workers=8) as pool:
        f = list(pool.map(broker, SERIES.items()))
        independent = list(pool.map(fred, FRED.items()))
    all_pairs = []
    aggregate = []
    offsets = []
    for (key, symbol), (up, receipt) in zip(SERIES.items(), f, strict=True):
        p = tape[tape.code.eq(key) & tape.close.notna()].drop(columns='code')
        if up is None or up.empty:
            legacy = V22 / f'sources/upstox/{symbol[1:]}.json'
            if not legacy.is_file():
                aggregate.append(dict(code=key, comparison='unavailable', strict_dates=0))
                continue
            rows = read(legacy.relative_to(V22), V22)['candles']
            up = pd.DataFrame([(x[0][:10], x[0], *x[1:5]) for x in rows],
                              columns=['day', 'broker_time', 'open2', 'high2', 'low2', 'close2']).drop_duplicates('day')
            type_ = 'V22 bounded sample fallback'
        else:
            type_ = 'full requested interval'
        q = p.merge(up, on='day', how='outer', indicator=True, validate='1:1').sort_values('day')
        absolute = abs(q[['open', 'high', 'low', 'close']].to_numpy() - q[['open2', 'high2', 'low2', 'close2']].to_numpy())
        stress = absolute / q[['open', 'high', 'low', 'close']].to_numpy()
        q['max_ohlc_relative_disagreement'] = np.max(stress, axis=1)
        q['strict_bar'] = q.ohlc_valid.eq(True) & (q.max_ohlc_relative_disagreement <= .001) & q.role.eq('primary')
        q['code'] = key
        both = q[q._merge.eq('both')].copy()
        b1, b2 = both.close.pct_change(), both.close2.pct_change()
        aggregate.append(dict(code=key, symbol=symbol, comparison=type_, calendar_marks=len(p), broker_marks=len(up),
                              paired=len(both), strict_dates=int(q.strict_bar.sum()), first_paired=both.day.min(), last_paired=both.day.max(),
                              only_broker=int(q._merge.eq('right_only').sum()), only_primary=int(q._merge.eq('left_only').sum()),
                              within_006=int(abs(both.close-both.close2).le(.06).sum()), within_10bp_all_ohlc=int(both.max_ohlc_relative_disagreement.le(.001).sum()),
                              median_close_bps=float(1.e4*(abs(both.close-both.close2)/both.close).median()), return_corr=b1.corr(b2),
                              scope='same local label; close-only FRED cannot independently validate excursions'))
        for k in range(-2, 3):
            offsets.append(dict(code=key, session_shift=k, corr=b1.corr(b2.shift(k))))
        all_pairs.append(q)
    with_fred = []
    for (code, _), (df, receipt) in zip(FRED.items(), independent, strict=True):
        if df is not None and not df.empty:
            q = tape[tape.code.eq(code)].merge(df, on='day', validate='1:1')
            q['difference'] = q.close - q.fred_close
            with_fred.append(q)
    write('foreign-full-ohlc-pairs.csv.gz', pd.concat(all_pairs, ignore_index=True))
    write('foreign-source-agreement.csv', pd.DataFrame(aggregate))
    write('foreign-session-offsets.csv', pd.DataFrame(offsets))
    write('foreign-independent-close-pairs.csv', pd.concat(with_fred, ignore_index=True) if with_fred else pd.DataFrame(columns=['day','code','close','fred_close']))
    save('foreign-source-receipts.json', dict(captured_at=now(), sources=[r for _, r in f + independent],
          strict='Same bounded local price-index session. All four marks within 10 basis points. Every mark in a donor window must qualify, including its cash reference. A close-only check never verifies a high or low.',
          engineering='Unresolved currency, price versus total return, and clock differences remain exclusions. Published date labels are joined without fitting an apparent lag.',
          docs=['https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/',
                'https://fred.stlouisfed.org/series/SP500','https://fred.stlouisfed.org/series/NIKKEI225']))
    print(pd.DataFrame(aggregate)[['code','paired','strict_dates']].to_string(index=False), flush=True)


if __name__ == '__main__':
    run()
