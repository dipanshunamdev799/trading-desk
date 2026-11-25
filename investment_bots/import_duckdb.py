"""One-time, read-only import from the supplied research DB to application PostgreSQL.

DuckDB is an optional import dependency. Portfolio processing never opens it.
The original loader is retained as evidence, never executed to discover paths.
"""
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import numpy as np
import pandas as pd

from .catalog import START, END
from .data import Inputs, IST, NIFTY, canonical, digest
from .engine import DataBlocked


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def frozen_metadata(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        raw = list(csv.DictReader(handle))
    if len(raw) != 2284 or len({r['instrument_key'] for r in raw}) != 2284:
        raise DataBlocked('Expected 2,284 unique frozen dpanel_meta.csv rows')
    rows = []
    for r in raw:
        key = r['instrument_key']
        isin = r.get('isin') or key.split('|')[-1]
        symbol = r.get('trading_symbol') or r.get('symbol')
        if not key.startswith('NSE_EQ|') or key != 'NSE_EQ|' + isin or not symbol:
            raise DataBlocked('Invalid frozen instrument identity: ' + key)
        rows.append(dict(instrument_key=key, isin=isin, symbol=symbol, name=r.get('name') or '',
                         segment=r.get('segment') or 'NSE_EQ', instrument_type=r.get('instrument_type') or 'EQ',
                         industry=r.get('industry') or 'Other'))
    return rows


def _pin_metadata(c, rows, sources, actions):
    old = c.execute("SELECT payload FROM metadata WHERE key='bundle'").fetchone()
    if old:
        if json.loads(old[0])['sources'] == sources:
            return
        raise DataBlocked('Frozen input bundle already pinned; the importer will not replace it')
    for i, row in enumerate(rows):
        c.execute('INSERT INTO instruments VALUES(%s,%s,%s)', (row['instrument_key'], i, canonical(row)))
    bundle = dict(sources=sources, imported_at=datetime.now(IST).isoformat(), panel_count=2284,
                  instruments_digest=digest(rows), actions_digest=digest(actions))
    c.execute('INSERT INTO metadata VALUES(%s,%s)', ('bundle', canonical(bundle)))


def validate_panel(source, path, rows):
    """Compare source prices against the supplied frozen cache before any write."""
    if rows is None:
        raise DataBlocked('The frozen panel requires dpanel_meta.csv alongside its cache')
    with np.load(path, allow_pickle=False) as z:
        keys = z['keys'].astype(str).tolist()
        if keys != [r['instrument_key'] for r in rows]:
            raise DataBlocked('Frozen cache keys/order differ from dpanel_meta.csv')
        dates = pd.to_datetime(z['dates']).strftime('%Y-%m-%d')
        mask = (dates >= START) & (dates <= END)
        days = dates[mask].tolist()
        frame = source.execute("""SELECT instrument_key AS key,CAST(ts AS DATE)::VARCHAR AS session,
            open AS o,high AS h,low AS l,close AS c,volume AS v FROM candles
            WHERE interval='1day' AND ts>=? AND ts<=?
            QUALIFY row_number() OVER(PARTITION BY instrument_key,CAST(ts AS DATE) ORDER BY ts DESC)=1""",
            [START, END]).fetchdf()
        report = {}
        for field in ('o','h','l','c','v'):
            actual = frame.pivot(index='session',columns='key',values=field).reindex(index=days,columns=keys).to_numpy()
            expected = z[field][mask]
            missing = int((np.isnan(actual) != np.isnan(expected)).sum())
            both = np.isfinite(actual) & np.isfinite(expected)
            max_error = float(np.max(np.abs(actual[both]-expected[both]) / np.maximum(np.abs(expected[both]),1.))) if both.any() else 0.
            report[field] = dict(missing_cells=missing,max_relative_error=max_error)
        index = frame[frame.key == NIFTY].set_index('session').reindex(days)
        expected_index = z['ix_Nifty_50'][mask]
        actual_index = index[['o','h','l','c']].to_numpy()
        report['nifty'] = dict(missing_cells=int((np.isnan(actual_index)!=np.isnan(expected_index)).sum()),
                              max_relative_error=float(np.nanmax(np.abs(actual_index-expected_index)/np.maximum(np.abs(expected_index),1.))))
        if any(r['missing_cells'] or r['max_relative_error']>1e-9 for r in report.values()):
            raise DataBlocked('Frozen panel / source DB mismatch: '+canonical(report))
    return dict(passed=True, sessions=len(days), instruments=len(keys),
                first_session=days[0],last_session=days[-1],fields=report)


def ingest(database, *, loader=None, metadata=None, panel=None, inputs=None, progress=print):
    import duckdb  # one-time source reader, not a runtime dependency
    inputs = inputs or Inputs()
    path = Path(database).resolve()
    sources = {path.name: file_hash(path)}
    if loader:
        sources[Path(loader).name] = file_hash(loader)
    rows = frozen_metadata(metadata) if metadata else None
    if metadata:
        sources[Path(metadata).name] = file_hash(metadata)
    if panel:
        sources[Path(panel).name] = file_hash(panel)
    progress('Reading research source in read-only mode; writing only to PostgreSQL.')
    source = duckdb.connect(str(path), read_only=True)
    try:
        tables = {r[0] for r in source.execute('SHOW TABLES').fetchall()}
        if not {'candles', 'corporate_actions'} <= tables:
            raise DataBlocked('Research source requires candles and corporate_actions tables')
        comparison = validate_panel(source,panel,rows) if panel else None
        if comparison:
            progress(f'Frozen cache matches the source DB: {comparison["sessions"]} sessions × {comparison["instruments"]} stocks.')
        action_cursor = source.execute('SELECT * FROM corporate_actions ORDER BY isin,ex_date,name')
        columns = [d[0] for d in action_cursor.description]
        actions = [dict(zip(columns, [v.isoformat() if hasattr(v, 'isoformat') else v for v in row]))
                   for row in action_cursor.fetchall()]
        with inputs.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420191)')
            prior = c.execute("SELECT payload FROM metadata WHERE key='duckdb_import'").fetchone()
            already = bool(prior and json.loads(prior[0])['sources'].get(path.name) == sources[path.name])
            if already:
                summary = json.loads(prior[0])
                progress('Identical research price source already imported; checking frozen metadata.')
            else:
                c.execute('''CREATE TEMP TABLE investment_daily_stage(
                    instrument_key TEXT, session DATE, open DOUBLE PRECISION, high DOUBLE PRECISION,
                    low DOUBLE PRECISION, close DOUBLE PRECISION, volume DOUBLE PRECISION,
                    PRIMARY KEY(instrument_key,session)) ON COMMIT DROP''')
                query = """SELECT instrument_key,CAST(ts AS DATE) AS session,open,high,low,close,volume
                    FROM candles WHERE interval='1day' AND ts>=? AND ts<=?
                    AND (instrument_key LIKE 'NSE_EQ|%' OR instrument_key=?)
                    QUALIFY row_number() OVER(PARTITION BY instrument_key,CAST(ts AS DATE) ORDER BY ts DESC)=1
                    ORDER BY instrument_key,session"""
                reader = source.execute(query, [START, END, NIFTY])
                count = 0
                with c.connection.cursor() as writer:
                    while batch := reader.fetchmany(20_000):
                        stream = io.StringIO()
                        csv.writer(stream, lineterminator='\n').writerows(batch)
                        stream.seek(0)
                        writer.copy_expert('COPY investment_daily_stage FROM STDIN WITH (FORMAT CSV, NULL \'\')', stream)
                        count += len(batch)
                        if count % 200_000 == 0:
                            progress(f'Staged {count:,} completed daily bars in PostgreSQL.')
                invalid = c.execute('''SELECT count(*) FROM investment_daily_stage WHERE
                    least(open,high,low,close)<=0 OR high<greatest(open,close) OR low>least(open,close)
                    OR high<low OR volume<0 OR NOT isfinite(session)
                    OR NOT(open<'Infinity'::float8 AND high<'Infinity'::float8 AND low<'Infinity'::float8
                           AND close<'Infinity'::float8 AND volume<'Infinity'::float8)''').fetchone()[0]
                if invalid:
                    raise DataBlocked(f'{invalid} invalid daily bars; import rolled back')
                conflicts = c.execute(f"""SELECT count(*) FROM investment_daily_stage a JOIN {inputs.market_table} b
                    ON b.instrument_key=a.instrument_key AND b.interval='1day'
                    AND b.ts=(a.session::timestamp AT TIME ZONE 'Asia/Kolkata')
                    WHERE abs(a.open-b.open)>1e-8 OR abs(a.high-b.high)>1e-8
                    OR abs(a.low-b.low)>1e-8 OR abs(a.close-b.close)>1e-8
                    OR a.volume IS DISTINCT FROM b.volume""").fetchone()[0]
                if conflicts:
                    raise DataBlocked(f'panel_check: {conflicts} existing PostgreSQL bars disagree with the supplied source; none overwritten')
                inserted = c.execute(f"""INSERT INTO {inputs.market_table}
                    (instrument_key,ts,interval,open,high,low,close,volume,oi,source)
                    SELECT instrument_key,(session::timestamp AT TIME ZONE 'Asia/Kolkata'),'1day',
                           open,high,low,close,volume,NULL,'upstox'
                    FROM investment_daily_stage ON CONFLICT DO NOTHING""").rowcount
                bounds = c.execute('SELECT min(session),max(session) FROM investment_daily_stage WHERE instrument_key=%s', (NIFTY,)).fetchone()
                summary = dict(sources=sources, daily_rows=count, inserted_rows=inserted,
                               first_session=bounds[0].isoformat(), last_session=bounds[1].isoformat(),
                               corporate_actions=len(actions), imported_at=datetime.now(IST).isoformat(),
                               source_read_only=True, runtime_storage='PostgreSQL')
            if comparison:
                summary['panel_comparison'] = comparison
            old_actions = c.execute("SELECT payload FROM metadata WHERE key='corporate_actions'").fetchone()
            if old_actions and digest(json.loads(old_actions[0])) != digest(actions):
                raise DataBlocked('Corporate-action source differs from the pinned PostgreSQL snapshot')
            c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO NOTHING', ('corporate_actions', canonical(actions)))
            for file in [loader, metadata]:
                if file:
                    content = Path(file).read_bytes()
                    name = 'daily_inputs/' + Path(file).name
                    c.execute('INSERT INTO source_files(name,sha256,content) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING',
                              (name, hashlib.sha256(content).hexdigest(), content))
            if rows:
                _pin_metadata(c, rows, sources, actions)
            summary = {**summary, 'metadata_ready': rows is not None or 'bundle' in inputs.metadata()}
            c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload',
                      ('duckdb_import', canonical(summary)))
        progress(f'Imported {summary["daily_rows"]:,} daily bars and {len(actions)} corporate actions into PostgreSQL.')
        return summary
    finally:
        source.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Read a research DuckDB source once and import into application PostgreSQL')
    parser.add_argument('database', type=Path)
    parser.add_argument('--loader', type=Path)
    parser.add_argument('--metadata', type=Path)
    parser.add_argument('--panel', type=Path)
    args = parser.parse_args()
    print(json.dumps(ingest(args.database, loader=args.loader, metadata=args.metadata,panel=args.panel), indent=2))
