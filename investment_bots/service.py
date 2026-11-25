"""Durable paper portfolios and application-owned daily reconciliation loop."""
from copy import deepcopy
from datetime import datetime, timedelta
import csv
import io
import json
import logging
import threading
import uuid

from .catalog import CATALOG, CAPITAL, DAY0, END, definition
from .data import Inputs, IST, ReadOnlyMarket, CAPTURE_TIMES, canonical, digest
from .engine import DataBlocked, advance, equity, features, fresh_book, target_exposure
from .verification import verify_inputs
from .practice import DEFAULT_POLICY,VERSION as PAPER_VERSION,validate_policy,advance_portfolio

LOG = logging.getLogger(__name__)


class InvestmentBots:
    def __init__(self, db=None, market=None):
        from .db import Postgres
        self.db = db or Postgres()
        self.inputs = Inputs(self.db)
        self.market = market
        self.lock = threading.Lock()
        self.last_attempt = None
        self.busy = False
        with self.connection() as c:
            c.execute('INSERT INTO settings VALUES(1,0) ON CONFLICT DO NOTHING')
            for key in CATALOG:
                c.execute("INSERT INTO controls VALUES(%s,1,'AWAITING_DATA','Frozen research input bundle is required',NULL) ON CONFLICT DO NOTHING", (key,))

    def connection(self):
        return self.db.connection()

    def paper_run(self):
        with self.connection() as c:
            active=c.execute("SELECT payload FROM metadata WHERE key='active_paper_run'").fetchone()
            if not active:return None
            row=c.execute('SELECT * FROM paper_runs WHERE id=%s',(json.loads(active[0]),)).fetchone()
            if row is None:raise DataBlocked('Active paper test is missing; no automatic reset is allowed')
            result=dict(row)
        result['policy']=json.loads(result['policy']);result['seeds']=json.loads(result['seeds']);return result

    def configure_paper(self,policy=None,mode='fresh',at=None):
        policy=validate_policy(policy or DEFAULT_POLICY)
        if mode not in ('fresh','keep'):raise ValueError('Choose fresh or keep existing holdings')
        at=at or datetime.now(IST)
        if not DAY0<=at.date().isoformat()<=END:raise ValueError('New investment tests must start within the2026 paper window')
        identifier=at.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];seeds={}
        with self.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420191)')
            active=c.execute("SELECT payload FROM metadata WHERE key='active_paper_run'").fetchone()
            active=json.loads(active[0]) if active else None
            for bot_id,d in CATALOG.items():
                if mode=='keep':
                    if active:row=c.execute('SELECT payload,sha256 FROM paper_records WHERE run_id=%s AND bot_id=%s ORDER BY session DESC LIMIT 1',(active,bot_id)).fetchone()
                    else:row=c.execute('SELECT payload,sha256 FROM records WHERE bot_id=%s ORDER BY session DESC LIMIT 1',(bot_id,)).fetchone()
                    if row:
                        value=json.loads(row['payload'])
                        if digest(value)!=row['sha256']:raise DataBlocked('Cannot seed from a corrupt saved portfolio')
                        books=value['books']
                        for book in books:book['pending_buys']=[];book['pending_sells']=[];book['pending_resize']={}
                        seeds[bot_id]=books;continue
                seeds[bot_id]=[fresh_book(CAPITAL/d['books']) for _ in range(d['books'])]
            c.execute('INSERT INTO paper_runs VALUES(%s,%s,%s,%s,%s,%s)',(identifier,at.isoformat(),at.date().isoformat(),mode,canonical(policy),canonical(seeds)))
            c.execute("INSERT INTO metadata VALUES('active_paper_run',%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload",(canonical(identifier),))
            self.event(c,None,'PAPER_TEST_STARTED',f'{identifier}: {mode}; {policy["daily_buy_fraction"]:.0%} daily buys, {policy["max_exposure"]:.0%} entry exposure, {policy["max_buy_orders"]} buys/day. Earlier runs retained.')
        self.last_attempt=None
        return self.dashboard()

    def event(self, c, bot_id, kind, message):
        # Repeated polling failures do not create an unbounded identical log.
        prior = c.execute('SELECT kind,message FROM events WHERE bot_id IS NOT DISTINCT FROM %s ORDER BY id DESC LIMIT 1', (bot_id,)).fetchone()
        if not prior or tuple(prior) != (kind, message):
            c.execute('INSERT INTO events(at,bot_id,kind,message) VALUES(%s,%s,%s,%s)',
                      (datetime.now(IST).isoformat(), bot_id, kind, message))

    def control(self, bot_id, action):
        definition(bot_id)
        if action not in ('start', 'resume', 'pause', 'stop'):
            raise ValueError('Use start, resume, pause or stop')
        with self.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420191)')
            if action in ('start', 'resume') and c.execute('SELECT kill_switch FROM settings').fetchone()[0]:
                raise ValueError('Investment kill switch is active; use Start investment bots to release it')
            enabled = action in ('start', 'resume')
            c.execute('UPDATE controls SET enabled=%s,status=%s,error=%s WHERE id=%s',
                      (int(enabled), 'WAITING' if enabled else 'PAUSED', '', bot_id))
            self.event(c, bot_id, 'CONTROL', action)
        self.last_attempt = None
        return self.detail(bot_id)

    def global_control(self, action):
        if action not in ('start', 'pause'):
            raise ValueError('Use start or pause')
        enabled = action == 'start'
        with self.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420191)')
            c.execute('UPDATE settings SET kill_switch=%s', (0 if enabled else 1,))
            c.execute('UPDATE controls SET enabled=%s,status=%s,error=%s', (int(enabled), 'WAITING' if enabled else 'PAUSED', ''))
            self.event(c, None, 'GLOBAL_CONTROL', action)
        self.last_attempt = None
        return self.dashboard()

    def detail(self, bot_id, reference=False):
        d = definition(bot_id)
        run=None if reference else self.paper_run()
        parity = self.inputs.metadata().get('historical_parity',{})
        if parity.get('passed'):
            d['verification'] = f'Historical universe, scores and portfolios verified through {parity["last_session"]}; original day-zero quantities matched'
        with self.connection() as c:
            control = dict(c.execute('SELECT * FROM controls WHERE id=%s', (bot_id,)).fetchone())
            if run:
                row=c.execute('SELECT payload,sha256 FROM paper_records WHERE run_id=%s AND bot_id=%s ORDER BY session DESC LIMIT 1',(run['id'],bot_id)).fetchone()
                history=[dict(r) for r in c.execute('SELECT session,payload FROM paper_records WHERE run_id=%s AND bot_id=%s ORDER BY session',(run['id'],bot_id))]
            else:
                row = c.execute('SELECT payload,sha256 FROM records WHERE bot_id=%s ORDER BY session DESC LIMIT 1', (bot_id,)).fetchone()
                history = [dict(r) for r in c.execute('SELECT session,payload FROM records WHERE bot_id=%s ORDER BY session', (bot_id,))]
            events = [dict(r) for r in c.execute('SELECT * FROM events WHERE bot_id=%s OR bot_id IS NULL ORDER BY id DESC LIMIT 100', (bot_id,))]
        record = json.loads(row['payload']) if row else None
        if row and digest(record) != row['sha256']:
            control.update(status='BLOCKED', error='Stored portfolio checksum mismatch; manual review required')
            record = None
        if run:
            d.update(implementation=PAPER_VERSION,paper_fingerprint=digest(dict(source=d['fingerprint'],policy=run['policy'],version=PAPER_VERSION)),
                     verification='Paced paper sizing and execution limits; original research verification applies to the source strategy only')
            if not row:
                books=run['seeds'][bot_id]
                record=dict(session=None,books=books,decisions=[],metrics=self.metrics(books,CAPITAL))
                if control['enabled'] and not control['error']:control['status']='WAITING_FIRST_SESSION'
        positions = []
        with self.inputs.connection() as c:
            names = {r['key']: json.loads(r['payload']).get('symbol', r['key'])
                     for r in c.execute('SELECT key,payload FROM instruments')}
        if record:
            for j, book in enumerate(record['books']):
                for key, p in book['holdings'].items():
                    positions.append(dict(instrument_key=key, symbol=names.get(key, key), book=j, **p,
                                          reference_quantity=p['value'] / p['mark'],
                                          unrealized_pnl=p['value'] - p['basis']))
        metrics = record['metrics'] if record else dict(equity=CAPITAL, cash=CAPITAL,
                   total_pnl=0, realized_pnl=0, unrealized_pnl=0, fees=0, exposure=0, drawdown=0)
        return dict(definition=d, state={**control, 'enabled': bool(control['enabled']), 'mode': 'paper'},
                    metrics=metrics, positions=positions,
                    orders=[dict(**o, symbol=names.get(o['instrument_key'], o['instrument_key']))
                            for o in record['decisions']] if record else [],
                    last_session=record['session'] if record else None, events=events,
                    history=[dict(session=r['session'], **json.loads(r['payload'])['metrics']) for r in history],
                    accounting='Fractional reference ledger; whole-share intents are a separate report',
                    real_orders_submitted=0,
                    paper_test=dict(id=run['id'],created_at=run['created_at'],starts_on=run['starts_on'],mode=run['mode'],policy=run['policy'],
                        latest_allocation=record.get('allocation') if record else None) if run else None,
                    archived_reference=reference)

    def dashboard(self):
        with self.connection() as c:
            kill = bool(c.execute('SELECT kill_switch FROM settings').fetchone()[0])
        meta = self.inputs.metadata()
        run=self.paper_run()
        return dict(bots=[self.detail(k) for k in CATALOG], global_controls=dict(kill_switch=kill),
                    inputs=dict(ready='bundle' in meta, panel_count=meta.get('bundle', {}).get('panel_count', 0),
                                last_refresh=meta.get('last_refresh'),
                                requirement='Original 2,284-stock panel, static industries, daily bars and corporate actions',
                                parity_verified=bool(meta.get('historical_parity',{}).get('passed')), storage='PostgreSQL',
                                research_archive=meta.get('research_archive'),
                                import_summary=meta.get('duckdb_import'),
                                verification=meta.get('historical_parity'),
                                integrity=meta.get('latest_integrity')),
                    as_of=datetime.now(IST).isoformat(), busy=self.busy, category='investment', mode='paper',
                    paper_testing=dict(id=run['id'],starts_on=run['starts_on'],created_at=run['created_at'],policy=run['policy'],mode=run['mode'],version=PAPER_VERSION) if run else None)

    def reconcile_paper(self,run,bot_id,instruments,sessions,frames,universe,scores,shadow_targets):
        indexes=[i for i,day in enumerate(sessions) if day>=run['starts_on']]
        if not indexes:return
        anchor=indexes[0];books=deepcopy(run['seeds'][bot_id]);peak=max(CAPITAL,sum(equity(b) for b in books))
        for idx in indexes:
            day=sessions[idx];required=set(universe.columns[universe.iloc[max(0,idx-1)]])|{k for b in books for k in b['holdings']}
            missing=sum(not(frames['c'].loc[day,k]>0) for k in required)
            if required and missing/len(required)>.02:raise DataBlocked(f'incomplete_paper_data: {day}, {missing}/{len(required)} missing')
            gate=(lambda key,side,q:self.inputs.evidence(day,key,q)) if bot_id=='C0_R_X' else None
            exposure=shadow_targets.get(day,1.) if bot_id=='C1_R' else 1.
            books,fills,intents,allocation=advance_portfolio(books,day=day,offset=idx-anchor,opens=frames['o'].loc[day].to_dict(),
                closes=frames['c'].loc[day].to_dict(),scores=scores.loc[day].to_dict(),instruments=instruments,policy=run['policy'],
                exposure=exposure,overlay=bot_id=='C1_R',gate=gate)
            if day==END:
                intents=[]
                for b in books:b['pending_buys']=[];b['pending_sells']=[];b['pending_resize']={}
            peak=max(peak,sum(equity(b) for b in books))
            record=dict(session=day,books=deepcopy(books),executions=fills,decisions=intents,metrics=self.metrics(books,peak),
                allocation=allocation,run_id=run['id'],policy=run['policy'],implementation=PAPER_VERSION,source_fingerprint=definition(bot_id)['fingerprint'],
                reconstructed_reference=True,real_orders_submitted=0)
            value,checksum=canonical(record),digest(record)
            with self.connection() as c:
                c.execute('SELECT pg_advisory_xact_lock(73420191)')
                active=c.execute("SELECT payload FROM metadata WHERE key='active_paper_run'").fetchone()
                if not active or json.loads(active[0])!=run['id'] or c.execute('SELECT kill_switch FROM settings').fetchone()[0] or not c.execute('SELECT enabled FROM controls WHERE id=%s',(bot_id,)).fetchone()[0]:return
                old=c.execute('SELECT payload,sha256 FROM paper_records WHERE run_id=%s AND bot_id=%s AND session=%s',(run['id'],bot_id,day)).fetchone()
                if old:
                    if old['payload']!=value or old['sha256']!=checksum:raise DataBlocked(f'paper_record_conflict: {day}; prior results retained')
                else:
                    c.execute('INSERT INTO paper_records VALUES(%s,%s,%s,%s,%s)',(run['id'],bot_id,day,value,checksum))
                    self.event(c,bot_id,'PACED_PAPER_SESSION',f'{day}: {allocation["buy_orders"]} buys, Rs{allocation["buy_amount"]:.2f} deployed, {sum(allocation["deferred"].values())} deferred')

    @staticmethod
    def metrics(books, peak):
        eq = sum(equity(b) for b in books)
        cash = sum(b['cash'] for b in books)
        return dict(equity=eq, cash=cash, total_pnl=eq - CAPITAL,
                    realized_pnl=sum(b['realized_pnl'] for b in books),
                    unrealized_pnl=sum(p['value'] - p['basis'] for b in books for p in b['holdings'].values()),
                    fees=sum(b['fees'] for b in books), exposure=(eq - cash) / eq,
                    drawdown=eq / max(peak, eq) - 1.)

    def reconcile(self, bot_id, instruments, sessions, frames, universe, scores, shadow_targets):
        """Replay from the frozen anchor and compare every previously stored record."""
        if DAY0 not in sessions:
            raise DataBlocked('anchor_session_missing: 2026-11-13')
        anchor = sessions.index(DAY0)
        count = CATALOG[bot_id]['books']
        books = [fresh_book(CAPITAL / count) for _ in range(count)]
        peak = CAPITAL
        for idx in range(anchor, len(sessions)):
            day = sessions[idx]
            required = set(universe.columns[universe.iloc[max(0, idx - 1)]])
            required |= {k for b in books for k in b['holdings']}
            missing = sum(not (frames['c'].loc[day, k] > 0) for k in required)
            if required and missing / len(required) > .02:
                raise DataBlocked(f'incomplete_market_data: {day}, {missing}/{len(required)} missing (>2%)')
            executions, decisions = [], []
            for j in range(count):
                if idx < anchor + j:
                    continue
                gate = ((lambda key, side, q: self.inputs.evidence(day, key, q)) if bot_id == 'C0_R_X' else None)
                books[j], fills, intents = advance(books[j], day=day, offset=idx - anchor - j,
                      opens=frames['o'].loc[day].to_dict(), closes=frames['c'].loc[day].to_dict(),
                      scores=scores.loc[day].to_dict(), instruments=instruments,
                      exposure=shadow_targets.get(day, 1.) if bot_id == 'C1_R' else 1.,
                      overlay=bot_id == 'C1_R', gate=gate)
                # No intention may target an execution session beyond the mandate.
                if day == END:
                    intents = []
                    books[j]['pending_buys'] = []
                    books[j]['pending_sells'] = []
                    books[j]['pending_resize'] = {}
                executions.extend(dict(**r, book=j) for r in fills)
                decisions.extend(dict(**r, book=j) for r in intents)
            eq = sum(equity(b) for b in books)
            peak = max(peak, eq)
            record = dict(session=day, books=deepcopy(books), executions=executions, decisions=decisions,
                          metrics=self.metrics(books, peak), target_exposure=shadow_targets.get(day, 1.) if bot_id == 'C1_R' else 1.,
                          fingerprint=definition(bot_id)['fingerprint'],
                          source_bundle=self.inputs.metadata()['bundle']['sources'],
                          implementation='specification-adapter-v1', real_orders_submitted=0,
                          reconstructed_reference=True)
            value, sha = canonical(record), digest(record)
            with self.connection() as c:
                c.execute('SELECT pg_advisory_xact_lock(73420191)')
                if c.execute("SELECT 1 FROM metadata WHERE key='active_paper_run'").fetchone():return
                enabled = c.execute('SELECT enabled FROM controls WHERE id=%s', (bot_id,)).fetchone()[0]
                if not enabled or c.execute('SELECT kill_switch FROM settings').fetchone()[0]:
                    return  # control changes fence the in-flight reconciler
                previous = c.execute('SELECT payload,sha256 FROM records WHERE bot_id=%s AND session=%s', (bot_id, day)).fetchone()
                if previous:
                    if previous['sha256'] != sha or previous['payload'] != value:
                        raise DataBlocked(f'record_conflict: {day}; retained records were not overwritten')
                else:
                    c.execute('INSERT INTO records VALUES(%s,%s,%s,%s)', (bot_id, day, value, sha))
                    self.event(c, bot_id, 'SESSION', f'{day}: {len(decisions)} whole-share intents; {len(executions)} execution evaluations')

    def shadow(self, instruments, sessions, frames, scores):
        if '2025-04-01' not in sessions:
            raise DataBlocked('C1-R shadow anchor missing: 2025-04-01')
        # sim5 seeds equity=1 on the session before its research anchor. The
        # anchor's zero return counts toward the first 20-return vol estimate.
        book, values, targets = fresh_book(1.), [1.], {}
        anchor = sessions.index('2025-04-01')
        for idx in range(anchor, len(sessions)):
            day = sessions[idx]
            book, _, _ = advance(book, day=day, offset=idx - anchor,
                      opens=frames['o'].loc[day].to_dict(), closes=frames['c'].loc[day].to_dict(),
                      scores=scores.loc[day].to_dict(), instruments=instruments)
            values.append(equity(book))
            targets[day] = target_exposure(values)
        return targets

    def capture(self, at):
        session, clock = at.date().isoformat(), at.strftime('%H:%M:%S')
        if not DAY0 <= session <= END or not '09:00:00' <= clock <= '09:46:30':
            return
        with self.connection() as c:
            if c.execute('SELECT kill_switch FROM settings').fetchone()[0]:
                return
            if not c.execute("SELECT enabled FROM controls WHERE id='C0_R_X'").fetchone()[0]:
                return
        # Never backdate a missed observation. At most 60s after the named slot.
        slots = [label for label in CAPTURE_TIMES if 0 <= (at - datetime.combine(at.date(),
                 datetime.strptime(label, '%H:%M:%S').time(), IST)).total_seconds() < 60]
        if not slots:
            return
        label = slots[-1]
        if label <= '09:05:00' and clock > '09:05:00':
            return
        with self.inputs.connection() as c:
            if c.execute('SELECT 1 FROM snapshots WHERE session=%s AND label=%s', (session, label)).fetchone():
                return
        bot = self.detail('C0_R_X')
        keys = sorted({r['instrument_key'] for r in bot['orders'] if r['quantity'] > 0}
                      | {r['instrument_key'] for r in bot['positions']})
        if not keys:
            return
        try:
            self.market = self.market or ReadOnlyMarket()
            if session not in self.market.expected_sessions(session, session):
                return
            payload = dict(quotes=self.market.quotes(keys), source='upstox_v3', error=None)
        except Exception as exc:
            payload = dict(quotes={}, error=type(exc).__name__ + ': ' + str(exc)[:200])
        self.inputs.snapshot(session, label, datetime.now(IST).isoformat(), payload)

    def tick(self, at=None, force=False):
        at = at or datetime.now(IST)
        if not self.lock.acquire(blocking=False):
            return dict(busy=True)
        self.busy = True
        try:
            self.capture(at)
            if at.strftime('%H:%M') < '07:45' and not force:
                return dict(waiting='Morning reconciliation begins at 07:45 IST')
            if not force and self.last_attempt and (at - self.last_attempt).total_seconds() < 300:
                return dict(waiting='Next daily input check')
            self.last_attempt = at
            with self.connection() as c:
                if c.execute('SELECT kill_switch FROM settings').fetchone()[0]:
                    return dict(paused=True)
                enabled = [r[0] for r in c.execute('SELECT id FROM controls WHERE enabled=1')]
            if not enabled:
                return dict(paused=True)
            until = min((at.date() - timedelta(days=1)).isoformat(), END)
            try:
                if 'bundle' not in self.inputs.metadata():
                    raise DataBlocked('Frozen research inputs missing: import the original 2,284-stock panel bundle')
                self.market = self.market or ReadOnlyMarket()
                self.inputs.refresh(self.market, until)
                instruments, sessions, frames = self.inputs.load(until)
                universe, scores = features(frames['c'], frames['v'], instruments)
                _,_,integrity = verify_inputs(self.inputs,instruments,sessions,frames,universe,scores)
                with self.connection() as c:
                    c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload',
                              ('latest_integrity',canonical(dict(session=sessions[-1],checked_at=at.isoformat(),**integrity))))
                targets = self.shadow(instruments, sessions, frames, scores) if 'C1_R' in enabled else {}
            except Exception as exc:
                for key in enabled:
                    self.block(key, exc, at)
                return dict(blocked=str(exc))
            for key in enabled:
                try:
                    run=self.paper_run()
                    if run:self.reconcile_paper(run,key,instruments,sessions,frames,universe,scores,targets)
                    else:self.reconcile(key, instruments, sessions, frames, universe, scores, targets)
                    with self.connection() as c:
                        status = 'WINDOW_ENDED' if at.date().isoformat() > END else 'RUNNING'
                        c.execute("UPDATE controls SET status=%s,error='',checked_at=%s WHERE id=%s AND enabled=1 AND (SELECT kill_switch FROM settings)=0",
                                  (status, at.isoformat(), key))
                except Exception as exc:
                    self.block(key, exc, at)
            return dict(processed_through=sessions[-1])
        finally:
            self.busy = False
            self.lock.release()

    def block(self, key, exc, at):
        message = ('' if isinstance(exc, DataBlocked) else type(exc).__name__ + ': ') + str(exc)[:400]
        status = 'AWAITING_DATA' if 'Frozen research inputs missing' in message else 'BLOCKED'
        with self.connection() as c:
            c.execute('UPDATE controls SET status=%s,error=%s,checked_at=%s WHERE id=%s AND enabled=1',
                      (status, message, at.isoformat(), key))
            self.event(c, key, status, message)
        if not isinstance(exc, DataBlocked):
            LOG.exception('Investment paper reconciliation blocked for %s', key)

    def export(self, bot_id, kind, reference=False):
        definition(bot_id)
        if kind not in ('orders', 'executions', 'equity'):
            raise ValueError('Export orders, executions or equity')
        rows = []
        run=None if reference else self.paper_run()
        with self.connection() as c:
            query=c.execute('SELECT payload FROM paper_records WHERE run_id=%s AND bot_id=%s ORDER BY session',(run['id'],bot_id)) if run else c.execute('SELECT payload FROM records WHERE bot_id=%s ORDER BY session', (bot_id,))
            for r in query:
                rec = json.loads(r[0])
                if kind == 'equity':
                    rows.append(dict(session=rec['session'], **rec['metrics']))
                else:
                    rows.extend(dict(session=rec['session'], **item) if 'session' not in item else item
                                for item in rec['decisions' if kind == 'orders' else 'executions'])
        stream = io.StringIO()
        fields = sorted({key for r in rows for key in r}) or ['session']
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
        return stream.getvalue()


_manager = None


def manager():
    global _manager
    if _manager is None:
        _manager = InvestmentBots()
    return _manager
