import json,logging,os,subprocess,sys,time
from pathlib import Path
from .store import Store,encoded,now
from .config import BotConfig,GlobalConfig
from .engine import ACTIVE
from .broker import UpstoxBroker
from ..catalog import IDS,strategy
ROOT=Path(__file__).resolve().parents[2]


class Manager:
    def __init__(self,root=None):self.root=root;self.children={}
    def store(self,key):strategy(key);return Store(key,self.root)
    def alive(self,s):
        with s.connection() as c:r=c.execute('SELECT * FROM control.workers WHERE bot_id=?',(s.bot_id,)).fetchone()
        return bool(r and r['pid']>0 and r['heartbeat']>time.time()-30)
    def spawn(self,key):
        s=self.store(key)
        if self.alive(s):return
        child=self.children.get(key)
        if child and child.poll() is None:
            with s.connection() as c:lease=c.execute('SELECT pid FROM control.workers WHERE bot_id=?',(key,)).fetchone()
            if not lease or lease['pid']!=-1:return
        env=os.environ.copy()
        if self.root:env['TRADING_BOTS_DATA_DIR']=str(self.root)
        with (s.root/(key+'.worker.log')).open('a',encoding='utf-8') as log:
            self.children[key]=subprocess.Popen([sys.executable,'-m','trading_bots.'+key+'_bot','--worker'],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    def recover(self):
        for key in IDS:
            s=self.store(key)
            if self.alive(s):continue
            if any(r['status'] in ACTIVE for r in s.rows('trades')):
                s.control('PAUSED');self.spawn(key)
                with s.tx() as c:s.event(c,'RECOVERY',reason='Entries paused; reconcile retained orders/positions')
            elif s.state()['desired']=='RUNNING':
                s.control('PAUSED')
                with s.tx() as c:c.execute("UPDATE state SET status='ERROR',error='Worker interrupted; resume explicitly after review'")
    def startup(self):
        self.recover()
        return self.start_all(automatic=True)
    def start_all(self,automatic=False):
        result={'started':[],'already_running':[],'skipped':[],'failed':[]}
        s=self.store(IDS[0])
        with s.tx() as c:
            cfg=s.global_settings(c)
            if cfg['kill_switch'] and automatic:
                result['skipped']=[{'bot_id':key,'reason':'Global kill switch is active'} for key in IDS]
                return result
            if not automatic:
                cfg['kill_switch']=False
                c.execute('UPDATE control.settings SET payload=?',(encoded(cfg),))
            s.event(c,'GLOBAL_START',automatic=automatic,mode='paper')
        for key in IDS:
            journal=None
            try:
                journal=self.store(key);state=journal.state()
                if state['config']['mode']!='paper':
                    result['skipped'].append({'bot_id':key,'reason':'Live bots require individual confirmation'})
                    continue
                healthy=self.alive(journal)
                if healthy and state['desired']=='RUNNING' and state['status']!='ERROR':
                    result['already_running'].append(key)
                    continue
                if any(row['status'] in ACTIVE for row in journal.rows('trades')):
                    if not healthy:self.control(key,'pause')
                    result['skipped'].append({'bot_id':key,'reason':'Retained position/order requires individual review; protection continues'})
                    continue
                self.control(key,'start')
                result['started'].append(key)
            except Exception as exc:
                message=type(exc).__name__+': '+str(exc)[:200]
                result['failed'].append({'bot_id':key,'reason':message})
                try:
                    if journal is None:raise RuntimeError('Bot journal unavailable')
                    with journal.tx() as c:
                        c.execute("UPDATE state SET status='ERROR',error=?",(message,))
                        journal.event(c,'GLOBAL_START_FAILED',reason=message)
                except Exception:logging.getLogger(__name__).exception('Could not persist global start failure for %s',key)
        return result
    def control(self,key,action,confirmation=''):
        s=self.store(key);cfg=s.state()['config']
        if action not in ('start','pause','resume','stop'):raise ValueError('Unknown bot action')
        if action in ('start','resume') and cfg['mode']=='live':
            if confirmation!='START LIVE '+key:raise ValueError('Type START LIVE '+key+' to start real execution')
            UpstoxBroker()
        s.control({'start':'RUNNING','resume':'RUNNING','pause':'PAUSED','stop':'STOPPED'}[action])
        if action in ('start','resume') or any(r['status'] in ACTIVE for r in s.rows('trades')):self.spawn(key)
        return self.detail(key)
    def configure(self,key,value,confirmation=''):
        cfg=BotConfig(**value).model_dump();s=self.store(key)
        if cfg['max_loss_per_trade']>cfg['capital'] or cfg['max_daily_loss']>cfg['capital']:raise ValueError('Risk cannot exceed allocated capital')
        if cfg['mode']=='live':
            if confirmation!='ENABLE LIVE '+key:raise ValueError('Type ENABLE LIVE '+key+' to activate live configuration')
            UpstoxBroker();cfg['live_activated']=True
        else:cfg['live_activated']=False
        with s.tx() as c:
            if s.state(c)['desired']!='STOPPED' or any(r['status'] in ACTIVE for r in s.rows('trades',c)):raise ValueError('Stop and flatten before changing configuration')
            c.execute('UPDATE state SET config=?',(encoded(cfg),));s.event(c,'CONFIGURATION',config=cfg)
        return self.detail(key)
    def global_config(self,value=None):
        s=self.store(IDS[0])
        if value is not None:
            cfg=GlobalConfig(**value).model_dump()
            if cfg['max_orders_per_minute']<=cfg['max_positions']:raise ValueError('Order budget must reserve capacity for exits')
            with s.tx() as c:c.execute('UPDATE control.settings SET payload=?',(encoded(cfg),));s.event(c,'GLOBAL_CONFIGURATION',config=cfg)
            if cfg['kill_switch']:
                for key in IDS:self.control(key,'stop')
        return s.global_settings()
    def detail(self,key):
        s=self.store(key);state=s.state();alive=self.alive(s)
        trades=[r['payload'] for r in s.rows('trades')];orders=[r['payload'] for r in s.rows('orders')]
        active=[t for t in trades if t['status'] in ACTIVE];closed=[t for t in trades if t['status']=='CLOSED' and t['mode']==state['config']['mode']]
        if state['desired']=='STOPPED' and active:state['status']='STOPPING'
        elif state['desired'] in ('RUNNING','PAUSED') and not alive:
            child=self.children.get(key);state['status']='STARTING' if child and child.poll() is None else 'ERROR' if state['desired']=='RUNNING' or active else 'PAUSED'
            if state['status']=='ERROR':state['error']=state['error'] or 'Worker unhealthy; retained positions/orders require review'
        state['worker_alive']=alive
        return {'definition':strategy(key).DEFINITION.json(),'state':state,'positions':active,'trades':trades,'orders':orders,'signals':s.rows('signals')[:200],'events':s.rows('events')[:300],
            'metrics':{'realized_pnl':sum(t.get('net_pnl',0) for t in closed)+sum(t.get('realized_pnl_so_far',0) for t in active),'unrealized_pnl':sum(t.get('unrealized_pnl',0) for t in active),'closed_trades':len(closed),'win_rate':100*sum(t['net_pnl']>0 for t in closed)/len(closed) if closed else None},'storage':str(s.path)}
    def dashboard(self):return {'bots':[self.detail(key) for key in IDS],'global':self.global_config(),'as_of':now()}


_manager=None
def manager():
    global _manager
    if _manager is None:_manager=Manager()
    return _manager
