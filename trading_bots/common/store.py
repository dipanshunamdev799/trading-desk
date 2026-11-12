"""Separate bot journals with atomic shared risk reservations (SQLite rollback journals)."""
import csv,io,json,os,sqlite3,time,uuid
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]


def now():return datetime.now(timezone.utc).isoformat()
def encoded(value):return json.dumps(value,allow_nan=False,default=str)
def defaults():return {'mode':'paper','capital':250000,'max_quantity':650,'max_loss_per_trade':1250,'max_daily_loss':2500,
    'max_trades_per_day':5,'max_positions':1,'stop_percent':None,'target_percent':None,'trailing_percent':None,
    'max_spread_percent':2,'quote_max_age_seconds':5,'signal_max_age_seconds':10,'poll_seconds':5,
    'slippage_points':.05,'brokerage_per_order':20,'order_timeout_seconds':15,'live_activated':False}


class Store:
    def __init__(self,bot_id,root=None):
        self.bot_id=bot_id;self.root=Path(root or os.environ.get('TRADING_BOTS_DATA_DIR',ROOT/'logs')).resolve();self.root.mkdir(parents=True,exist_ok=True)
        self.path=self.root/(bot_id+'.sqlite3');self.shared=self.root/'control.sqlite3'
        with self.connection() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1),desired TEXT,status TEXT,config TEXT,heartbeat TEXT,error TEXT,last_signal TEXT);
              CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,at TEXT,kind TEXT,payload TEXT);
              CREATE TABLE IF NOT EXISTS signals(id TEXT PRIMARY KEY,at TEXT,status TEXT,payload TEXT);
              CREATE TABLE IF NOT EXISTS trades(id TEXT PRIMARY KEY,signal_id TEXT UNIQUE,status TEXT,payload TEXT);
              CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,trade_id TEXT,kind TEXT,status TEXT,payload TEXT);
              CREATE TABLE IF NOT EXISTS control.settings(id INTEGER PRIMARY KEY CHECK(id=1),payload TEXT);
              CREATE TABLE IF NOT EXISTS control.exposure(bot_id TEXT,trade_id TEXT PRIMARY KEY,mode TEXT,capital REAL,risk REAL,qty INTEGER);
              CREATE TABLE IF NOT EXISTS control.workers(bot_id TEXT PRIMARY KEY,token TEXT,pid INTEGER,heartbeat REAL);
              CREATE TABLE IF NOT EXISTS control.attempts(id TEXT PRIMARY KEY,at REAL);
            ''')
            c.execute("INSERT OR IGNORE INTO state VALUES(1,'STOPPED','STOPPED',?,NULL,NULL,NULL)",(encoded(defaults()),))
            c.execute('INSERT OR IGNORE INTO control.settings VALUES(1,?)',(encoded({'kill_switch':False,'max_positions':3,'max_capital':750000,'max_orders_per_minute':20}),))
    @contextmanager
    def connection(self):
        c=sqlite3.connect(self.path,timeout=30,isolation_level=None);c.row_factory=sqlite3.Row
        c.execute('PRAGMA synchronous=FULL');c.execute('PRAGMA journal_mode=DELETE');c.execute('ATTACH DATABASE ? AS control',(str(self.shared),))
        try:yield c
        finally:c.close()
    @contextmanager
    def tx(self):
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE')
            try:yield c;c.commit()
            except BaseException:c.rollback();raise
    def state(self,c=None):
        if c is None:
            with self.connection() as c:return self.state(c)
        s=dict(c.execute('SELECT * FROM state').fetchone());s['config']=json.loads(s['config']);return s
    def global_settings(self,c=None):
        if c is None:
            with self.connection() as c:return self.global_settings(c)
        return json.loads(c.execute('SELECT payload FROM control.settings').fetchone()[0])
    def event(self,c,kind,**payload):c.execute('INSERT INTO events(at,kind,payload) VALUES(?,?,?)',(now(),kind,encoded(payload)))
    def rows(self,table,c=None):
        if table not in ('trades','orders','signals','events'):raise ValueError('Invalid journal table')
        if c is None:
            with self.connection() as c:return self.rows(table,c)
        return [{**dict(r),'payload':json.loads(r['payload'])} for r in c.execute('SELECT * FROM '+table+' ORDER BY rowid DESC')]
    def save(self,c,table,record):
        if table=='trades':c.execute('INSERT INTO trades VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,payload=excluded.payload',(record['id'],record['signal_id'],record['status'],encoded(record)))
        elif table=='orders':c.execute('INSERT INTO orders VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,payload=excluded.payload',(record['id'],record['trade_id'],record['kind'],record['status'],encoded(record)))
        else:raise ValueError('Unsupported journal')
    def claim(self,token):
        with self.tx() as c:
            old=c.execute('SELECT * FROM control.workers WHERE bot_id=?',(self.bot_id,)).fetchone()
            if old and old['pid']>0 and old['heartbeat']>time.time()-30 and old['token']!=token:return False
            c.execute('INSERT OR REPLACE INTO control.workers VALUES(?,?,?,?)',(self.bot_id,token,os.getpid(),time.time()));return True
    def fenced(self,c,token):
        row=c.execute('SELECT token,pid FROM control.workers WHERE bot_id=?',(self.bot_id,)).fetchone()
        if token and (not row or row['token']!=token or row['pid']<0):raise RuntimeError('Worker lease lost')
    def heartbeat(self,token):
        with self.tx() as c:
            self.fenced(c,token);c.execute('UPDATE control.workers SET heartbeat=? WHERE bot_id=?',(time.time(),self.bot_id));c.execute('UPDATE state SET heartbeat=?',(now(),))
    def release(self,token):
        with self.tx() as c:c.execute('DELETE FROM control.workers WHERE bot_id=? AND token=?',(self.bot_id,token))
    def finish_if_stopped(self,token):
        with self.tx() as c:
            self.fenced(c,token)
            active=c.execute("SELECT 1 FROM trades WHERE status IN ('OPEN','ENTRY_PENDING','EXIT_PENDING','UNKNOWN') LIMIT 1").fetchone()
            if self.state(c)['desired']!='STOPPED' or active:return False
            # Mark the exiting owner before releasing the transaction, so a new
            # Start can replace it even before its OS process has fully exited.
            c.execute('UPDATE control.workers SET pid=-1,heartbeat=0 WHERE bot_id=? AND token=?',(self.bot_id,token))
            return True
    def control(self,desired):
        if desired not in ('RUNNING','PAUSED','STOPPED'):raise ValueError('Invalid control')
        with self.tx() as c:
            if desired=='RUNNING' and self.global_settings(c)['kill_switch']:raise ValueError('Global kill switch is active; use Global Start to restart paper bots')
            active=c.execute("SELECT 1 FROM trades WHERE status IN ('OPEN','ENTRY_PENDING','EXIT_PENDING','UNKNOWN') LIMIT 1").fetchone()
            c.execute('UPDATE state SET desired=?,status=?,error=NULL',(desired,'STOPPING' if desired=='STOPPED' and active else desired));self.event(c,'CONTROL',desired=desired)
    def export(self,table='trades'):
        rows=self.rows(table);buf=io.StringIO()
        columns={'trades':['mode','instrument_key','symbol','exchange','direction','entry_at','exit_at','quantity','entry_price','exit_price','entry_reason','exit_reason','stop_price','target_price','gross_pnl','entry_fees','exit_fees','net_pnl','holding_seconds'],
            'orders':['trade_id','kind','side','instrument_key','created_at','updated_at','quantity','limit_price','broker_order_id','applied_qty','applied_value','applied_fees','execution_error'],
            'signals':['at','side','underlying','spot','reason','rejection_reason'], 'events':['at','kind']}
        w=csv.DictWriter(buf,fieldnames=['bot_id','id','status',*columns[table],'data_json']);w.writeheader()
        for row in reversed(rows):
            record={k:row['payload'].get(k,row.get(k,'')) for k in columns[table]}
            record.update(bot_id=self.bot_id,id=row.get('id'),status=row.get('status',row.get('kind')),data_json=encoded(row['payload']))
            # Keep provider text from becoming a spreadsheet formula when the CSV is opened.
            w.writerow({k:"'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v for k,v in record.items()})
        return buf.getvalue()
