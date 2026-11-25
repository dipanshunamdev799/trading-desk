"""Investment state and market inputs live exclusively in the configured PostgreSQL."""
from contextlib import contextmanager
from pathlib import Path
import re
import sys

from psycopg2.extras import DictCursor, execute_batch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))


class Session:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, statement, params=None):
        cursor = self.connection.cursor(cursor_factory=DictCursor)
        cursor.execute(statement, params)
        return cursor

    def executemany(self, statement, rows):
        cursor = self.connection.cursor()
        execute_batch(cursor, statement, rows, page_size=500)
        return cursor


class Postgres:
    def __init__(self, schema='investment_bots'):
        if schema != 'investment_bots' and not re.fullmatch(r'investment_test_[0-9a-f]{12}', schema):
            raise ValueError('Unsupported investment schema')
        from app.services.upstox_service import get_market_store
        self.engine = get_market_store().engine
        self.schema = schema
        self.market_table = 'public.candles' if schema == 'investment_bots' else schema + '.candles'
        with self.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420190)')
            c.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
            c.execute('''
                CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS instruments(key TEXT PRIMARY KEY, ordinal INTEGER UNIQUE, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS snapshots(session TEXT, label TEXT, received_at TEXT, payload TEXT,
                    sha256 TEXT, PRIMARY KEY(session,label));
                CREATE TABLE IF NOT EXISTS controls(id TEXT PRIMARY KEY, enabled INTEGER, status TEXT, error TEXT, checked_at TEXT);
                CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), kill_switch INTEGER);
                CREATE TABLE IF NOT EXISTS records(bot_id TEXT, session TEXT, payload TEXT, sha256 TEXT,
                    PRIMARY KEY(bot_id,session));
                CREATE TABLE IF NOT EXISTS events(id BIGSERIAL PRIMARY KEY, at TEXT, bot_id TEXT, kind TEXT, message TEXT);
                CREATE TABLE IF NOT EXISTS source_files(name TEXT PRIMARY KEY, sha256 TEXT NOT NULL, content BYTEA NOT NULL,
                    imported_at TIMESTAMPTZ NOT NULL DEFAULT now());
                CREATE TABLE IF NOT EXISTS paper_runs(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,starts_on TEXT NOT NULL,
                    mode TEXT NOT NULL,policy TEXT NOT NULL,seeds TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS paper_records(run_id TEXT REFERENCES paper_runs(id),bot_id TEXT,session TEXT,
                    payload TEXT NOT NULL,sha256 TEXT NOT NULL,PRIMARY KEY(run_id,bot_id,session));
            ''')
            if schema != 'investment_bots':
                c.execute('''CREATE TABLE IF NOT EXISTS candles(instrument_key TEXT,ts TIMESTAMPTZ,interval TEXT,
                    open DOUBLE PRECISION,high DOUBLE PRECISION,low DOUBLE PRECISION,close DOUBLE PRECISION,
                    volume DOUBLE PRECISION,oi DOUBLE PRECISION,source TEXT,
                    PRIMARY KEY(instrument_key,ts,interval))''')

    @contextmanager
    def connection(self):
        raw = self.engine.raw_connection()
        try:
            # schema is validated above, never supplied by a route/request.
            with raw.cursor() as cursor:
                cursor.execute(f'SET LOCAL search_path TO {self.schema},public')
            yield Session(raw)
            raw.commit()
        except BaseException:
            raw.rollback()
            raise
        finally:
            raw.close()

    def drop_test_schema(self):
        if not re.fullmatch(r'investment_test_[0-9a-f]{12}', self.schema):
            raise ValueError('Only an isolated test schema may be dropped')
        with self.connection() as c:
            c.execute(f'DROP SCHEMA {self.schema} CASCADE')
