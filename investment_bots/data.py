"""Frozen input bundle and a read-only Upstox market-data adapter.

The universe is imported, never inferred from a different research project. Source
hashes pin the instrument/industry snapshot for the life of these four versions.
"""
from datetime import date, datetime, time, timedelta
import csv
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from .catalog import START, END
from .engine import DataBlocked

IST = ZoneInfo('Asia/Kolkata')
NIFTY = 'NSE_INDEX|Nifty 50'
ROOT = Path(__file__).resolve().parents[1]
CAPTURE_TIMES = ('09:00:30', '09:02:00', '09:03:30', '09:04:30', '09:06:00', '09:07:30',
                 '09:09:00', '09:11:00', '09:12:30', '09:14:00', '09:15:30', '09:20:00',
                 '09:30:00', '09:45:30')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Inputs:
    def __init__(self, db=None):
        from .db import Postgres
        self.db = db or Postgres()
        self.market_table = self.db.market_table

    def connection(self):
        return self.db.connection()

    def metadata(self):
        with self.connection() as c:
            return {r['key']: json.loads(r['payload']) for r in c.execute('SELECT * FROM metadata')}

    def import_bundle(self, folder):
        """Import the documented interchange format; refuse replacements after pinning."""
        folder = Path(folder).resolve()
        required = ['instruments.csv', 'daily.csv', 'corporate_actions.json']
        if not all((folder / name).is_file() for name in required):
            raise ValueError('Bundle requires instruments.csv, daily.csv and corporate_actions.json; see investment_bots/README.md')
        sources = {n: hashlib.sha256((folder / n).read_bytes()).hexdigest() for n in required}
        with (folder / 'instruments.csv').open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.DictReader(handle))
        rows = [dict(r, name=r.get('name', '')) for r in rows]
        if len(rows) != 2284 or len({r['instrument_key'] for r in rows}) != 2284:
            raise ValueError('Expected the original 2,284 unique frozen panel keys; no substitute universe is accepted')
        for r in rows:
            if (r.get('segment') != 'NSE_EQ' or r.get('instrument_type') != 'EQ'
                    or not r['instrument_key'].startswith('NSE_EQ|')
                    or r.get('isin') != r['instrument_key'].split('|', 1)[1]
                    or not r.get('symbol') or not r.get('industry')):
                raise ValueError('Instrument identity, symbol, segment, type and static industry are required')
        actions = json.loads((folder / 'corporate_actions.json').read_text(encoding='utf-8-sig'))
        if not isinstance(actions, list):
            raise ValueError('corporate_actions.json must be a list of source action records')
        candles = pd.read_csv(folder / 'daily.csv', dtype={'instrument_key': str, 'session': str})
        cols = ['instrument_key', 'session', 'open', 'high', 'low', 'close', 'volume']
        if not all(n in candles for n in cols):
            raise ValueError('daily.csv requires: ' + ', '.join(cols))
        candles = candles.loc[candles.session.between(START, END), cols]
        if candles.duplicated(['instrument_key', 'session']).any():
            raise ValueError('De-duplicate the source daily panel keeping the latest load before importing')
        if not set(candles.instrument_key).issubset({r['instrument_key'] for r in rows} | {NIFTY}):
            raise ValueError('Daily data contain keys outside the frozen panel')
        if NIFTY not in set(candles.instrument_key):
            raise ValueError('NIFTY 50 daily bars are required for the session calendar')
        for r in candles.itertuples(index=False, name=None):
            self.validate_bar(r)
        with self.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420191)')
            old = c.execute("SELECT payload FROM metadata WHERE key='bundle'").fetchone()
            if old:
                if json.loads(old[0])['sources'] == sources:
                    return self.metadata()
                raise ValueError('Frozen inputs already pinned. Replacement requires a new strategy version and a separate data directory')
            for i, r in enumerate(rows):
                c.execute('INSERT INTO instruments VALUES(%s,%s,%s)',
                          (r['instrument_key'], i, canonical(dict(r, name=r.get('name', '')))))
            self.insert_bars(c, candles.itertuples(index=False, name=None))
            c.execute('INSERT INTO metadata VALUES(%s,%s)', ('bundle', canonical(dict(sources=sources,
                       imported_at=datetime.now(IST).isoformat(), panel_count=2284,
                       instruments_digest=digest(rows), actions_digest=digest(actions)))))
            c.execute('INSERT INTO metadata VALUES(%s,%s)', ('corporate_actions', canonical(actions)))
        return self.metadata()

    @staticmethod
    def validate_bar(row):
        import math
        key, session, o, h, l, close, v = row
        date.fromisoformat(session)
        if not all(math.isfinite(float(x)) and x > 0 for x in (o, h, l, close)):
            raise DataBlocked(f'invalid_ohlc: {key} {session}')
        if l > min(o, close) or h < max(o, close) or h < l or not math.isfinite(float(v)) or v < 0:
            raise DataBlocked(f'invalid_ohlcv: {key} {session}')

    def load(self, until):
        meta = self.metadata()
        if 'bundle' not in meta:
            raise DataBlocked('Frozen research inputs missing: import the original 2,284-stock panel bundle')
        if 'corporate_actions' not in meta:
            raise DataBlocked('corporate_actions_missing')
        with self.connection() as c:
            instruments = {r['key']: json.loads(r['payload']) for r in c.execute('SELECT * FROM instruments ORDER BY ordinal')}
            if len(instruments) != 2284:
                raise DataBlocked('frozen_panel_membership_changed')
            if digest(list(instruments.values())) != meta['bundle']['instruments_digest']:
                raise DataBlocked('frozen_instrument_snapshot_changed')
            if digest(meta['corporate_actions']) != meta['bundle']['actions_digest']:
                raise DataBlocked('corporate_action_snapshot_changed')
            cursor = c.execute(f"""SELECT DISTINCT ON (instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date)
                instrument_key AS key, to_char(ts AT TIME ZONE 'Asia/Kolkata','YYYY-MM-DD') AS session,
                open AS o,high AS h,low AS l,close AS c,volume AS v
                FROM {self.market_table} WHERE interval='1day' AND ts>=%s AND ts<%s
                ORDER BY instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date,ts DESC""",
                (datetime.fromisoformat(START).replace(tzinfo=IST),
                 datetime.fromisoformat(min(until, END)).replace(tzinfo=IST)+timedelta(days=1)))
            frame = pd.DataFrame.from_records(cursor.fetchall(),columns=['key','session','o','h','l','c','v'])
            frame = frame[frame.key.isin(set(instruments) | {NIFTY})]
        if frame.empty:
            raise DataBlocked('daily_panel_missing')
        sessions = sorted(frame.loc[frame.key == NIFTY, 'session'])
        if not sessions:
            raise DataBlocked('nifty_session_calendar_missing')
        frames = {field: frame.pivot(index='session', columns='key', values=field).reindex(
                  index=sessions, columns=list(instruments)) for field in ('o', 'h', 'l', 'c', 'v')}
        self.validate_actions(meta['corporate_actions'], instruments, sessions, frames['c'])
        return instruments, sessions, frames

    @staticmethod
    def validate_actions(actions, instruments, sessions, closes):
        """Frozen split/bonus safeguard: vendor-adjusted ex-date move must be <=40%."""
        if not actions:
            return
        lower = {k.lower(): k for row in actions for k in row}
        kind = next((lower[k] for k in ('type', 'action_type', 'event_type', 'name') if k in lower), None)
        when = next((lower[k] for k in ('ex_date', 'exdate', 'record_date', 'date') if k in lower), None)
        identity = next((lower[k] for k in ('code', 'isin') if k in lower), None)
        if not all((kind, when, identity)):
            raise DataBlocked('split_bonus: unexpected corporate-action schema')
        keys = {r['isin']: k for k, r in instruments.items()}
        dates = pd.Index(sessions)
        for row in actions:
            if not any(s in str(row.get(kind, '')).lower() for s in ('split', 'bonus')):
                continue
            key = keys.get(str(row.get(identity)))
            day = pd.to_datetime(row.get(when), errors='coerce')
            if key is None or pd.isna(day):
                continue
            idx = dates.searchsorted(day.date().isoformat())
            if not 0 < idx < len(dates):
                continue
            before, after = closes[key].iloc[idx-1:idx+1]
            if pd.notna(before) and pd.notna(after) and abs(after / before - 1) > .40:
                raise DataBlocked(f'split_bonus: unadjusted price suspect {key} {day.date()}')

    def refresh(self, gateway, until):
        """Fetch only completed daily bars; never broaden the frozen universe."""
        meta = self.metadata()
        if 'bundle' not in meta:
            raise DataBlocked('Frozen research inputs missing: import the original 2,284-stock panel bundle')
        until = min(until, END)
        if meta.get('last_refresh') == until and not meta.get('refresh_failures'):
            return
        with self.connection() as c:
            keys = [r[0] for r in c.execute('SELECT key FROM instruments ORDER BY ordinal')]
            previous = self.latest(c, NIFTY, until)
        # Overlap one session so partial previous downloads can be repaired.
        first = previous or START
        index_rows = gateway.daily(NIFTY, first, until)
        self.save_bars(NIFTY, index_rows, until)
        with self.connection() as c:
            new_sessions = [d for d in self.sessions(c, NIFTY, until) if d > (previous or '')]
        expected = gateway.expected_sessions(first, until)
        with self.connection() as c:
            stored = set(self.sessions(c, NIFTY, until))
        if set(expected) - stored:
            raise DataBlocked('expected_session_missing: NIFTY daily bar absent')
        if not new_sessions and not meta.get('refresh_failures'):
            with self.connection() as c:
                c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload',
                          ('last_refresh',canonical(until)))
            return
        if new_sessions or meta.get('last_refresh') != until:
            failures = []
            for key in keys:
                try:
                    with self.connection() as c:
                        latest = self.latest(c, key, until)
                    self.save_bars(key, gateway.daily(key, min(latest or START, first), until), until)
                except Exception:
                    failures.append(key)
            with self.connection() as c:
                c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload', ('refresh_failures', canonical(failures)))
                c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload', ('last_refresh', canonical(until)))

    def save_bars(self, key, rows, until):
        normalized = []
        for row in rows:
            session = str(row[0])[:10]
            if not START <= session <= min(until, END):
                continue
            r = (key, session, *[float(x) for x in row[1:6]])
            self.validate_bar(r)
            normalized.append(r)
        with self.connection() as c:
            self.insert_bars(c, normalized, update=True)

    def latest(self, c, key, until):
        rows = self.sessions(c, key, until)
        return max(rows) if rows else None

    def index_prices(self, sessions):
        with self.connection() as c:
            cursor = c.execute(f"""SELECT DISTINCT ON ((ts AT TIME ZONE 'Asia/Kolkata')::date)
                to_char(ts AT TIME ZONE 'Asia/Kolkata','YYYY-MM-DD') AS session,open,high,low,close
                FROM {self.market_table} WHERE instrument_key=%s AND interval='1day' AND ts>=%s AND ts<%s
                ORDER BY (ts AT TIME ZONE 'Asia/Kolkata')::date,ts DESC""",
                (NIFTY,datetime.fromisoformat(sessions[0]).replace(tzinfo=IST),
                 datetime.fromisoformat(sessions[-1]).replace(tzinfo=IST)+timedelta(days=1)))
            data = pd.DataFrame.from_records(cursor.fetchall(),columns=['session','open','high','low','close'])
        return data.set_index('session').reindex(sessions).to_numpy()

    def sessions(self, c, key, until):
        rows = c.execute(f"""SELECT DISTINCT to_char(ts AT TIME ZONE 'Asia/Kolkata','YYYY-MM-DD')
                            FROM {self.market_table} WHERE instrument_key=%s AND interval='1day'
                            AND ts>=%s AND ts<%s ORDER BY 1""",
                         (key, datetime.fromisoformat(START).replace(tzinfo=IST),
                          datetime.fromisoformat(until).replace(tzinfo=IST)+timedelta(days=1)))
        return [r[0] for r in rows]

    def insert_bars(self, c, rows, update=False):
        rows = [(key,datetime.fromisoformat(day).replace(tzinfo=IST),'1day',o,h,l,close,v,None,'upstox')
                for key,day,o,h,l,close,v in rows]
        conflict = ("DO UPDATE SET open=EXCLUDED.open,high=EXCLUDED.high,low=EXCLUDED.low,"
                    "close=EXCLUDED.close,volume=EXCLUDED.volume,source=EXCLUDED.source") if update else 'DO NOTHING'
        c.executemany(f"""INSERT INTO {self.market_table}
            (instrument_key,ts,interval,open,high,low,close,volume,oi,source)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT(instrument_key,ts,interval) {conflict}""", rows)
        if not update and rows:
            # Importing a frozen source must not silently accept different bars
            # already stored by the application, or overwrite other research.
            c.execute('CREATE TEMP TABLE investment_import_check(instrument_key TEXT,ts TIMESTAMPTZ,interval TEXT,open DOUBLE PRECISION,high DOUBLE PRECISION,low DOUBLE PRECISION,close DOUBLE PRECISION,volume DOUBLE PRECISION) ON COMMIT DROP')
            c.executemany('INSERT INTO investment_import_check VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
                          [r[:8] for r in rows])
            conflicts = c.execute(f"""SELECT count(*) FROM investment_import_check a JOIN {self.market_table} b
                USING(instrument_key,ts,interval)
                WHERE abs(a.open-b.open)>1e-8 OR abs(a.high-b.high)>1e-8 OR abs(a.low-b.low)>1e-8
                OR abs(a.close-b.close)>1e-8 OR a.volume IS DISTINCT FROM b.volume""").fetchone()[0]
            if conflicts:
                raise DataBlocked(f'panel_check: {conflicts} stored daily bars disagree with the frozen import; nothing overwritten')

    def snapshot(self, session, label, received_at, payload):
        with self.connection() as c:
            c.execute('INSERT INTO snapshots VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
                      (session, label, received_at, canonical(payload), digest(payload)))

    def evidence(self, session, key, quantity):
        from .engine import auction_gate
        if quantity <= 0:
            return 'rejected_order'
        with self.connection() as c:
            rows = [dict(r) for r in c.execute('SELECT * FROM snapshots WHERE session=%s ORDER BY label', (session,))]
        def received_in_window(record, first, last, inclusive_end=False):
            # A slot label is not the time a network response became available.
            # Late replies must not justify an earlier auction decision.
            try:
                received = datetime.fromisoformat(record['received_at'].replace('Z', '+00:00'))
                if received.tzinfo is None:
                    return False
                local = received.astimezone(IST)
                clock = local.strftime('%H:%M:%S.%f')
                return (local.date().isoformat() == session and first <= clock and
                        (clock <= last + '.000000' if inclusive_end else clock < last))
            except (ValueError, TypeError, AttributeError):
                return False

        decs = [r for r in rows if r['label'] <= '09:05:00'
                and received_in_window(r, '09:00:00', '09:05:00', inclusive_end=True)]
        finals = [r for r in rows if '09:12:00' <= r['label'] < '09:15:00'
                  and received_in_window(r, '09:12:00', '09:15:00')]

        def fields(record):
            if record is None:
                return None, True
            payload = json.loads(record['payload'])
            if digest(payload) != record['sha256']:
                raise DataBlocked('auction_snapshot_checksum_mismatch')
            quote = payload.get('quotes', {}).get(key)
            if quote is None:
                return None, True
            try:
                source = quote.get('timestamp')
                if isinstance(source, (float, int)) or str(source).isdigit():
                    source = datetime.fromtimestamp(float(source) / (1000 if float(source) > 1e11 else 1), IST)
                else:
                    source = datetime.fromisoformat(str(source).replace('Z', '+00:00'))
                if source.tzinfo is None:
                    raise ValueError('undated quote')
                stale = abs((source - datetime.fromisoformat(record['received_at'])).total_seconds()) > 120
            except (ValueError, TypeError, OverflowError):
                stale = True
            return dict(iep=quote.get('indicative_equilibrium_price'),
                        ieq=quote.get('indicative_equilibrium_quantity'),
                        imbalance_market=quote.get('indicative_imbalance_quantity_market'),
                        volume=quote.get('volume')), stale
        dec, stale = fields(decs[-1] if decs else None)
        final, _ = fields(finals[0] if finals else None)
        return auction_gate(quantity, dec, final, stale)


class ReadOnlyMarket:
    """Exposes market data only. No broker submission interface is provided."""
    def __init__(self):
        from app.services.upstox_service import get_upstox
        self._gateway = get_upstox()

    def daily(self, key, first, last):
        # Use the primary source directly; adjusted daily data must not silently
        # change vendor through the app's unrelated fallback policy.
        return self._gateway._remote_call('get_historical_candles_v3', key, 'days', 1, last, first)['candles']

    def expected_sessions(self, first, last):
        days = pd.date_range(first, last)
        expected = []
        for day in days:
            timings = self._gateway.get_market_timings(day.date().isoformat())
            if not isinstance(timings, list):
                raise DataBlocked('calendar_unavailable')
            if any(r.get('exchange') in ('NSE', 'NSE_EQ') for r in timings):
                expected.append(day.date().isoformat())
        return expected

    def quotes(self, keys):
        result = {}
        for start in range(0, len(keys), 100):
            payload = self._gateway._remote_call('get_full_market_quotes_v3', keys[start:start + 100])
            for q in payload.values():
                key = q.get('instrument_token') or q.get('instrument_key')
                if key:
                    result[key] = q
        return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import frozen investment research inputs into the application PostgreSQL')
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    inputs = Inputs()
    if args.bundle.is_file() and args.bundle.suffix.lower() == '.zip':
        from .archive import import_archive
        result = import_archive(args.bundle, inputs)
    else:
        result = inputs.import_bundle(args.bundle)
    print(json.dumps(result, indent=2))
