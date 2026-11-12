import argparse,json,signal,sys,threading,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for path in [ROOT,ROOT/'backend']:
    if str(path) not in sys.path:sys.path.insert(0,str(path))
from trading_bots.catalog import strategy
from .store import Store
from .engine import Engine,ACTIVE
from .market import MarketData


def run(bot_id):
    store=Store(bot_id);token=uuid.uuid4().hex
    if not store.claim(token):raise SystemExit('A worker already owns this bot')
    stopped=threading.Event()
    def beat():
        while not stopped.is_set():
            try:store.heartbeat(token)
            except Exception:stopped.set();return
            stopped.wait(5)
    heartbeat=threading.Thread(target=beat,daemon=True);heartbeat.start()
    engine=Engine(store,strategy(bot_id),MarketData(),token=token)
    signal.signal(signal.SIGINT,lambda *_:store.control('STOPPED'))
    if hasattr(signal,'SIGTERM'):signal.signal(signal.SIGTERM,lambda *_:store.control('STOPPED'))
    try:
        while not stopped.is_set():
            try:engine.tick()
            except Exception as e:
                try:engine.error(type(e).__name__+': '+str(e)[:300])
                except Exception:break
            state=store.state()
            if state['desired']=='STOPPED' and store.finish_if_stopped(token):break
            stopped.wait(state['config']['poll_seconds'])
    finally:stopped.set();heartbeat.join(timeout=1);store.release(token)


def run_cli(bot_id):
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--command',choices=['start','pause','resume','stop','status']);p.add_argument('--confirm',default='');p.add_argument('--config',type=Path,help='Save a complete bot configuration from JSON, without starting by default');a=p.parse_args()
    if a.config:
        from .manager import Manager
        result=Manager().configure(bot_id,json.loads(a.config.read_text(encoding='utf-8-sig')),a.confirm)
        if not a.command:print(json.dumps(result,default=str));return
    if a.command:
        from .manager import Manager
        m=Manager();result=m.detail(bot_id) if a.command=='status' else m.control(bot_id,a.command,a.confirm)
        print(json.dumps(result,default=str));return
    if not a.worker:
        if Store(bot_id).state()['config']['mode']=='live' and a.confirm!='START LIVE '+bot_id:raise SystemExit('Explicit --confirm "START LIVE '+bot_id+'" required')
        Store(bot_id).control('RUNNING')
    run(bot_id)
