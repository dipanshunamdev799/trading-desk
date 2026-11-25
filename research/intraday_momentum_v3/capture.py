"""Manually started, bounded market-hours observer. No scheduler or orders."""
import asyncio,base64,gzip,hashlib,json,os,shutil,time,uuid
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from psycopg2.extras import execute_values
from .common import OUT,SOURCE,now,client,base,dump,sha,archive_response
from .auth import authorize
from .universe import build,Scanner
from .features import normalize,timestamp
from .shadow import Evaluator

IST=ZoneInfo('Asia/Kolkata')


class RunLock:
    def __enter__(self):
        OUT.mkdir(parents=True,exist_ok=True);self.file=(OUT/'observer.lock').open('a+b');self.file.seek(0);self.file.write(b'0');self.file.flush();self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt;msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl;fcntl.flock(self.file,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:self.file.close();raise RuntimeError('Another V3 observer holds the lock')
        return self
    def __exit__(self,*args):self.file.close()


def market_window(status,timings,at):
    if at.astimezone(IST).year>2026:return False,'2027_REQUIRES_EXPLICIT_APPROVAL'
    updated=timestamp(status.get('last_updated')) if isinstance(status,dict) else None
    if not updated or updated.astimezone(IST).date()!=at.astimezone(IST).date() or updated>at+timedelta(seconds=1):return False,'MARKET_STATUS_STALE_OR_UNDATED'
    windows=[r for r in timings if r.get('exchange')=='NSE'] if isinstance(timings,list) else []
    normal=any(timestamp(r.get('start_time')) and timestamp(r.get('end_time')) and timestamp(r['start_time'])<=at<timestamp(r['end_time']) for r in windows)
    return bool(normal and status.get('status')=='NORMAL_OPEN'),'NORMAL_OPEN' if normal and status.get('status')=='NORMAL_OPEN' else 'CLOSED_OR_NONREGULAR_PHASE'


def archive_batch(batch):
    rows=[]
    for frame,received in batch:
        source=timestamp(frame.get('currentTs'))
        if source is None:continue
        for key,feed in frame.get('feeds',{}).items():rows.append((source,key,received,frame.get('type','unknown'),json.dumps(feed,allow_nan=False)))
    if rows:
        with base.connection(write=True) as c:
            execute_values(c,'INSERT INTO market_stream_ticks(source_at,instrument_key,received_at,feed_type,payload) VALUES %s ON CONFLICT DO NOTHING',rows,page_size=1000)
    return len(rows)


class Observer:
    def __init__(self,plan,directory,seconds,transport='auto',smoke=False):
        self.plan=plan;self.directory=directory;self.seconds=seconds;self.transport=transport;self.smoke=smoke;self.c=client();self.scanner=Scanner(plan)
        self.started=now();self.deadline=time.monotonic()+seconds;self.rows=0;self.rawbytes=0;self.frames=0;self.candidates=0;self.open_rows=0;self.last_seen={};self.mode=None;self.active=False
        self.market={};self.last_market=0;self.connection_generation=0;self.stop=False;self.queue=asyncio.Queue(maxsize=2000)
        self.context_keys=['NSE_INDEX|Nifty 50','NSE_INDEX|India VIX'];self.context={}
        self.last_resource_check=0;self.disk_ok=True
        self.health_path=OUT/'observer-health.json';self.stop_path=OUT/'stop.request'
        self.events=gzip.open(directory/'derived-events.jsonl.gz','at',encoding='utf-8');self.raw=gzip.open(directory/'raw-packets.jsonl.gz','at',encoding='utf-8')
        self.refs=gzip.open(directory/'packet-refs.jsonl.gz','at',encoding='utf-8')
        self.quality=gzip.open(directory/'quote-quality.jsonl.gz','at',encoding='utf-8');self.fresh_valid=0
        self.evaluator=Evaluator(plan,self.emit,gate={'quality_pass':False,'predictor_frozen':False})
        self.ledger_state=OUT/'shadow-ledger-state.json'
        if self.ledger_state.exists():
            saved=json.loads(self.ledger_state.read_text())
            if saved.get('protocol_sha256')!=sha(OUT/'protocol-frozen.json'):raise RuntimeError('Prior hypothetical capital state belongs to another protocol; reconcile before observation')
            self.evaluator.ledger.restore(saved['ledger'])
        self.evaluator.context=self.context_at
        from .model import load
        self.evaluator.model=load()
        if self.evaluator.model:
            ready=json.loads((OUT/'forward-readiness.json').read_text()) if (OUT/'forward-readiness.json').exists() else {}
            auth=json.loads((OUT/'auth-audit.json').read_text()) if (OUT/'auth-audit.json').exists() else {}
            entitlement=auth.get('account_entitlement',{});checked=timestamp(auth.get('checked_at'))
            account=bool(checked and checked.astimezone(IST).date()==now().astimezone(IST).date() and entitlement.get('is_active') and 'NSE' in (entitlement.get('exchanges') or []) and 'I' in (entitlement.get('products') or []))
            calibration=json.loads((OUT/'execution-calibration.json').read_text()) if (OUT/'execution-calibration.json').exists() else {}
            lock=json.loads((OUT/'execution-calibration-freeze.json').read_text()) if (OUT/'execution-calibration-freeze.json').exists() else {}
            calibrated=calibration.get('fresh_forward_controls') and lock.get('sha256')==sha(OUT/'execution-calibration.json') and calibration.get('model_sha256')==sha(OUT/'frozen-forward-model.json') and calibration.get('training_end')==self.evaluator.model['training_end']
            uncertainty=calibration.get('uncertainty_bps',float('inf')) if calibrated else float('inf')
            self.evaluator.ledger.gate.update(quality_pass=ready.get('milestone_B_streaming_quality',False),predictor_frozen=True,
                account_segments_verified=account,short_execution_verified=False,execution_uncertainty_bps=uncertainty)
    def context_at(self,at):
        return {key:dict(last=q.last,previous_close=q.cp,return_fraction=q.last/q.cp-1 if q.last and q.cp else None,
            source_at=q.source_at.isoformat(),received_at=q.received_at.isoformat())
            for key,q in self.context.items() if q.available_at<=at and q.fresh(at)}
    def emit(self,row):
        if row.get('kind')=='candidate':self.candidates+=1
        self.events.write(json.dumps({'recorded_at':now().isoformat(),**row},default=str,allow_nan=False)+'\n');self.events.flush()
        if row.get('kind') in ('candidate','selection','shadow_ledger') and hasattr(self,'ledger_state'):
            dump(self.ledger_state,dict(protocol_sha256=sha(OUT/'protocol-frozen.json'),updated_at=now().isoformat(),ledger=self.evaluator.ledger.state()))
    def health(self,state,reason=None):
        health=dict(state=state,reason=reason,checked_at=now().isoformat(),pid=os.getpid(),run=str(self.directory),transport=self.mode,
            rows_committed=self.rows,open_market_rows_committed=self.open_rows,frames=self.frames,raw_bytes=self.rawbytes,
            candidates=self.candidates,queue_size=self.queue.qsize(),elapsed_seconds=(now()-self.started).total_seconds(),
            bytes_per_second=self.rawbytes/max(1,(now()-self.started).total_seconds()),
            silent_watch_keys=[k for k in sorted(self.scanner.watch) if k not in self.last_seen or (now()-self.last_seen[k]).total_seconds()>15],
            market=self.market,real_orders_submitted=0,unattended_scheduling=False,shadow_funded_gate=False)
        health['fresh_valid_book_rows']=self.fresh_valid
        dump(self.health_path,health);dump(self.directory/'health.json',health)
        if reason:self.emit(dict(kind='health_alert',state=state,reason=reason))
    def continuing(self):
        if self.stop or self.stop_path.exists() or time.monotonic()>=self.deadline:return False
        if now().astimezone(IST).year>2026:
            self.health('STOPPING','2027_REQUIRES_EXPLICIT_APPROVAL');return False
        if self.rawbytes>=8*1024**3 or self.rows>=5_000_000:
            self.health('STOPPING','RESOURCE_LIMIT');return False
        if time.monotonic()-self.last_resource_check>=5:
            self.disk_ok=shutil.disk_usage(OUT).free>=20*1024**3;self.last_resource_check=time.monotonic()
        if not self.disk_ok:
            self.health('STOPPING','FREE_DISK_BELOW_20GIB');return False
        return True
    async def session(self,force=False):
        if force or time.monotonic()-self.last_market>=60:
            try:
                status=await asyncio.to_thread(self.c.get_market_status,'NSE');day=now().astimezone(IST).date().isoformat()
                timings=await asyncio.to_thread(self.c.get_market_timings,day)
                await asyncio.to_thread(archive_response,'intraday_v3.market_status',{'exchange':'NSE'},status)
                await asyncio.to_thread(archive_response,'intraday_v3.market_timings',{'date':day},timings)
                checked=now();self.active,reason=market_window(status,timings,checked)
                future=[timestamp(r.get('start_time')) for r in timings if r.get('exchange')=='NSE' and timestamp(r.get('start_time')) and timestamp(r['start_time'])>checked] if isinstance(timings,list) else []
                self.market={'active':self.active,'phase':reason,'checked_at':checked.isoformat(),'next_open_today':min(future).isoformat() if future else None}
            except Exception as exc:self.active=False;self.market={'active':False,'error_type':type(exc).__name__}
            self.last_market=time.monotonic()
        return self.active
    def process(self,key,payload,source,received,mode,committed):
        q=normalize(key,payload,source,received,mode,committed)
        if q is None:
            self.emit(dict(kind='quote_quality',key=key,transport=mode,status='MISSING_OR_INVALID_TIMESTAMP'))
            return
        if q:
            if key in self.context_keys:self.context[key]=q;return
            self.last_seen[key]=received;self.scanner.update(q)
            processed=now()
            self.quality.write(json.dumps(dict(key=key,transport=mode,source_at=q.source_at.isoformat(),received_at=received.isoformat(),
                available_at=q.available_at.isoformat(),processed_at=processed.isoformat(),valid_book=q.valid_book,market_active=self.active))+'\n');self.quality.flush()
            if self.active and q.valid_book and q.fresh(processed):self.fresh_valid+=1
            if self.active and q.valid_book:self.evaluator.observe(q,processed)
    async def writer(self):
        while not self.stop or not self.queue.empty():
            batch=[]
            try:item=await asyncio.wait_for(self.queue.get(),.5);batch.append(item)
            except asyncio.TimeoutError:continue
            while len(batch)<50 and not self.queue.empty():batch.append(self.queue.get_nowait())
            try:
                count=await asyncio.to_thread(archive_batch,[(f,r) for f,r in batch]);committed=now();self.rows+=count
                if self.active:self.open_rows+=count
                for frame,received in batch:
                    self.refs.write(json.dumps({'received_at':received.isoformat(),'source_at':frame.get('currentTs'),'committed_at':committed.isoformat(),'keys':list(frame.get('feeds',{}))})+'\n')
                    for key,payload in sorted(frame.get('feeds',{}).items(),key=lambda x:not x[0].startswith('NSE_INDEX')):self.process(key,payload,frame.get('currentTs'),received,'ws',committed)
                self.refs.flush()
            except Exception as exc:self.health('FAILED','PG_COMMIT_OR_PROCESS_'+type(exc).__name__);self.stop=True
            finally:
                for _ in batch:self.queue.task_done()
    async def rest(self):
        self.mode='rest_5s';last_broad=0
        while self.continuing():
            active=await self.session()
            if not active and not self.smoke:
                self.health('CLOSED',self.market.get('phase','MARKET_UNVERIFIED'));return
            broad=time.monotonic()-last_broad>=30
            keys=[s['key'] for s in self.plan['stocks']]+self.context_keys if broad else sorted(self.scanner.watch)
            if not keys:keys=[s['key'] for s in self.plan['stocks'][:40]]
            try:
                for start in range(0,len(keys),500):
                    selected=keys[start:start+500];payload=await asyncio.to_thread(self.c.get_full_market_quotes_v3,selected);received=now()
                    encoded=json.dumps(payload,allow_nan=False);self.rawbytes+=len(encoded.encode());self.frames+=1
                    self.raw.write(json.dumps({'transport':'rest','received_at':received.isoformat(),'payload':payload},allow_nan=False)+'\n');self.raw.flush()
                    await asyncio.to_thread(archive_response,'intraday_v3.quotes',{'keys':selected},payload,received);committed=now();self.rows+=len(payload)
                    if active:self.open_rows+=len(payload)
                    for value in sorted(payload.values(),key=lambda v:not v.get('instrument_token','').startswith('NSE_INDEX')):
                        key=value.get('instrument_token');self.process(key,value,value.get('timestamp'),received,'rest',committed)
                if broad:
                    self.emit({'kind':'watchlist',**self.scanner.select(now())});last_broad=time.monotonic()
                self.health('CAPTURING_OPEN' if active else 'CLOSED_SMOKE_ONLY')
            except Exception as exc:
                self.emit(dict(kind='rest_failure',error_type=type(exc).__name__));self.health('DEGRADED','REST_REQUEST_OR_COMMIT_FAILED')
            await asyncio.sleep(min(5,max(0,self.deadline-time.monotonic())))
    async def ws(self):
        import websockets
        from upstox_ws_v3 import UpstoxMarketDataWSV3
        self.mode='ws';writer=asyncio.create_task(self.writer());delay=1
        try:
            while self.continuing() and await self.session():
                uri,attempts=await asyncio.to_thread(authorize,self.c)
                if not uri:
                    self.emit(dict(kind='authorization_unavailable',attempts=attempts));self.health('AUTH_BLOCKED','BROKER_FEED_AUTHORIZATION_REJECTED');return False
                try:
                    async with websockets.connect(uri,open_timeout=15,ping_interval=20,ping_timeout=10,max_size=4*1024**2,max_queue=128) as ws:
                        self.connection_generation+=1;self.emit(dict(kind='connected',generation=self.connection_generation));last_rotation=0;last_health=0
                        async def control(method,mode,keys):
                            if keys:await ws.send(json.dumps({'guid':uuid.uuid4().hex,'method':method,'data':{'mode':mode,'instrumentKeys':list(keys)}}).encode())
                        await control('sub','ltpc',[s['key'] for s in self.plan['stocks']]+self.context_keys)
                        event=self.scanner.select(now());self.emit({'kind':'watchlist',**event});await control('change_mode','full',event['full_keys'])
                        while self.continuing() and await self.session():
                            try:raw=await asyncio.wait_for(ws.recv(),min(5,max(.01,self.deadline-time.monotonic())))
                            except asyncio.TimeoutError:
                                self.emit(dict(kind='no_frame_5s',generation=self.connection_generation));self.health('DEGRADED','NO_FRAME_5S');continue
                            received=now();self.frames+=1;self.rawbytes+=len(raw)
                            self.raw.write(json.dumps({'transport':'ws','received_at':received.isoformat(),'bytes_b64':base64.b64encode(raw if isinstance(raw,bytes) else raw.encode()).decode()})+'\n');self.raw.flush()
                            frame=UpstoxMarketDataWSV3.decode_protobuf(raw) if isinstance(raw,bytes) else json.loads(raw)
                            if frame.get('feeds'):await self.queue.put((frame,received))
                            else:self.emit(dict(kind='feed_status',frame=frame))
                            if time.monotonic()-last_rotation>=30:
                                event=self.scanner.select(now());self.emit({'kind':'watchlist',**event});await control('change_mode','ltpc',event['removed']);await control('change_mode','full',event['added']);last_rotation=time.monotonic()
                            if time.monotonic()-last_health>=5:self.health('CAPTURING_OPEN');last_health=time.monotonic()
                    if not self.continuing() or not self.active:break
                except Exception as exc:
                    self.emit(dict(kind='disconnected',error_type=type(exc).__name__,generation=self.connection_generation));self.health('RECONNECTING','SOCKET_INTERRUPTION')
                    await asyncio.sleep(min(delay,max(0,self.deadline-time.monotonic())));delay=min(delay*2,30)
            return True
        finally:self.stop=True;await writer
    async def run(self):
        try:
            active=await self.session(force=True)
            while not active and not self.smoke and self.continuing() and self.market.get('next_open_today'):
                self.health('WAITING_OPEN','TODAY_SCHEDULED_SESSION_NOT_YET_OPEN');await asyncio.sleep(min(30,max(0,self.deadline-time.monotonic())));active=await self.session()
            if not active and not self.smoke:self.health('CLOSED','NO_CURRENT_REGULAR_SESSION');return
            if self.transport=='rest' or (self.smoke and not self.active):await self.rest()
            else:
                success=await self.ws()
                if not success and self.transport=='auto' and time.monotonic()<self.deadline:
                    self.stop=False;self.health('REST_FALLBACK','STREAM_UNAVAILABLE_REST_IS_SEPARATE_PRODUCT');await self.rest()
        finally:
            self.evaluator.close();self.health('STOPPED','MANUAL_OR_BOUNDED_SHUTDOWN');self.events.close();self.raw.close();self.refs.close();self.quality.close()


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['run','stop','status']);p.add_argument('--seconds',type=int,default=28800);p.add_argument('--transport',choices=['auto','ws','rest'],default='auto');p.add_argument('--smoke-closed',action='store_true');args=p.parse_args()
    if args.action=='stop':dump(OUT/'stop.request',{'requested_at':now().isoformat()});print('Stop requested');return
    if args.action=='status':print((OUT/'observer-health.json').read_text() if (OUT/'observer-health.json').exists() else 'NOT_STARTED');return
    if not 1<=args.seconds<=28800:raise ValueError('Duration must be1..28800seconds')
    if now().astimezone(IST).year>2026:raise RuntimeError('2027 collection/evaluation requires explicit user approval and a new scope freeze')
    with RunLock():
        stop=OUT/'stop.request'
        if stop.exists():stop.unlink()
        metadata=json.loads((OUT/'metadata-audit.json').read_text()) if (OUT/'metadata-audit.json').exists() else {}
        checked=timestamp(metadata.get('checked_at'))
        if checked is None or checked.astimezone(IST).date()!=now().astimezone(IST).date():
            from .metadata import main as refresh
            refresh()
            metadata=json.loads((OUT/'metadata-audit.json').read_text());checked=timestamp(metadata.get('checked_at'))
            if checked is None or metadata.get('status')=='INCOMPLETE' or checked.astimezone(IST).date()!=now().astimezone(IST).date():
                raise RuntimeError('Current-day metadata could not be verified; observer not started')
        plan=build();directory=OUT/'runs'/now().strftime('%Y%m%d-%H%M%S');directory.mkdir(parents=True)
        if not (OUT/'protocol-frozen.json').exists():raise RuntimeError('Freeze the V3 protocol before capture')
        from .readiness import freeze
        freeze()  # Verify source/document hashes before every run.
        previous=json.loads((OUT/'observer-health.json').read_text()) if (OUT/'observer-health.json').exists() else None
        dump(directory/'manifest.json',dict(started_at=now().isoformat(),seconds=args.seconds,transport=args.transport,smoke_closed=args.smoke_closed,
            previous_run=previous,universe_sha256=sha(OUT/'universe-current.json'),code={f.name:sha(f) for f in SOURCE.glob('*.py')},
            controls=plan['controls'],universe_session=plan['session'],protocol_sha256=sha(OUT/'protocol-frozen.json'),
            no_orders=True,scheduling_enabled=False,scope_end='2026-12-31',shadow_enabled=False))
        asyncio.run(Observer(plan,directory,args.seconds,args.transport,args.smoke_closed).run())
        print('Bounded observer finished:',directory)

if __name__=='__main__':main()
