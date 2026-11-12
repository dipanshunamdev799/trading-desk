"""Lifecycle tests use isolated SQLite journals and deterministic market/broker fixtures."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from datetime import datetime,timedelta
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'backend'),str(ROOT/'scripts')]
from trading_bots.catalog import IDS,strategy
from trading_bots.common.store import Store,encoded,defaults
from trading_bots.common.engine import Engine
from trading_bots.common.manager import Manager
from trading_bots.common.broker import PaperBroker,UnknownSubmission,UpstoxBroker

AT=datetime.fromisoformat('2026-11-06T13:05:00+05:30')
BARS=json.loads((ROOT/'artifacts'/'directional_research'/'nifty-upstox-5minute.json').read_text())


class Market:
    bid=99.9;ask=100.;bid_qty=650;ask_qty=650;connected=True;fresh=True
    def candles(self,at):return BARS
    def select(self,side,spot,at):return {'key':'NSE_FO|TEST','symbol':'NIFTY TEST CE' if side==1 else 'NIFTY TEST PE','exchange':'NSE_FO','expiry':'2026-11-17','strike':25000,'lot':65,'option_type':'CE' if side==1 else 'PE'}
    def quote(self,key,at):
        if not self.connected:raise ConnectionError('fixture disconnected')
        ts=(at if self.fresh else at-timedelta(hours=1)).isoformat()
        return {'bid':self.bid,'ask':self.ask,'bid_qty':self.bid_qty,'ask_qty':self.ask_qty,'source_at':ts,'last_trade_at':ts,'captured_at':ts,'market_open':True}


class Bots(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store('ema_trend',self.temp.name);self.market=Market()
        self.cfg={**defaults(),'capital':1000000,'max_loss_per_trade':100000,'max_daily_loss':100000,'max_quantity':65}
        with self.store.tx() as c:c.execute('UPDATE state SET config=?',(encoded(self.cfg),))
        self.store.control('RUNNING');self.engine=Engine(self.store,strategy('ema_trend'),self.market,PaperBroker())
    def tearDown(self):self.temp.cleanup()
    def trades(self):return [r['payload'] for r in self.store.rows('trades')]
    def enter(self):self.engine.tick(AT);self.assertEqual(self.trades()[0]['status'],'OPEN')
    def test_complete_entry_pause_exit_and_persistent_log(self):
        self.enter();self.store.control('PAUSED');self.market.bid=110;self.market.ask=110.1
        self.engine.tick(AT+timedelta(minutes=60))
        t=self.trades()[0];self.assertEqual(t['status'],'CLOSED');self.assertGreater(t['gross_pnl'],0);self.assertLess(t['net_pnl'],t['gross_pnl'])
        self.assertEqual(Store('ema_trend',self.temp.name).rows('trades')[0]['payload']['id'],t['id']);self.assertGreater(len(self.store.rows('events')),3)
        self.assertIn(t['id'],self.store.export())
    def test_no_duplicate_signal_or_order_after_restart(self):
        self.enter();Engine(Store('ema_trend',self.temp.name),strategy('ema_trend'),self.market,PaperBroker()).tick(AT+timedelta(seconds=1))
        self.assertEqual(len(self.trades()),1);self.assertEqual(len(self.store.rows('orders')),1)
    def test_unacknowledged_paper_intent_never_replays_old_quote(self):
        from unittest.mock import patch
        with patch.object(self.engine,'_submit',return_value=None):self.engine.tick(AT)
        self.assertEqual(self.trades()[0]['status'],'ENTRY_PENDING');self.store.control('PAUSED');self.market.connected=False
        Engine(self.store,strategy('ema_trend'),self.market,PaperBroker()).tick(AT+timedelta(days=1))
        self.assertEqual(self.trades()[0]['status'],'REJECTED');self.assertEqual(self.trades()[0]['quantity'],0)
        self.assertEqual(self.store.rows('orders')[0]['payload']['status'],'CANCELLED')
        with self.store.connection() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM control.exposure').fetchone()[0],0)
    def test_partial_entry_cancels_unfilled_and_retains_actual_quantity(self):
        cfg={**self.cfg,'max_quantity':130}
        with self.store.tx() as c:c.execute('UPDATE state SET config=?',(encoded(cfg),))
        self.market.ask_qty=65;self.enter();self.assertEqual(self.trades()[0]['quantity'],65)
        self.assertEqual(self.store.rows('orders')[0]['payload']['status'],'CANCELLED')
        with self.store.connection() as c:self.assertEqual(c.execute('SELECT qty FROM control.exposure').fetchone()[0],65)
    def test_partial_exit_retries_remaining_only(self):
        cfg={**self.cfg,'max_quantity':130}
        with self.store.tx() as c:c.execute('UPDATE state SET config=?',(encoded(cfg),))
        self.enter();self.assertEqual(self.trades()[0]['quantity'],130);self.market.bid_qty=65;self.store.control('STOPPED')
        self.engine.tick(AT+timedelta(seconds=5));self.assertEqual(self.trades()[0]['sold_quantity'],65)
        self.engine.tick(AT+timedelta(seconds=10));self.assertEqual(self.trades()[0]['status'],'CLOSED');self.assertEqual(self.trades()[0]['sold_quantity'],130)
    def test_risk_rejection_is_logged(self):
        with self.store.tx() as c:c.execute('UPDATE state SET config=?',(encoded({**self.cfg,'max_loss_per_trade':100}),))
        self.engine.tick(AT);self.assertFalse(self.trades());self.assertEqual(self.store.rows('signals')[0]['status'],'SKIPPED')
    def test_stale_book_never_fills(self):
        self.market.fresh=False;self.engine.tick(AT);self.assertFalse(self.trades());self.assertEqual(self.store.rows('signals')[0]['status'],'SKIPPED')
    def test_disconnected_entry_is_logged_as_skipped(self):
        self.market.connected=False
        with self.assertRaises(ConnectionError):self.engine.tick(AT)
        self.assertFalse(self.trades());signal=self.store.rows('signals')[0]
        self.assertEqual(signal['status'],'SKIPPED');self.assertIn('ConnectionError',signal['payload']['rejection_reason'])
    def test_invalid_candles_cannot_generate_an_order(self):
        from unittest.mock import patch
        invalid=[dict(BARS[-1],ts=(AT-timedelta(minutes=5)).isoformat(),high=-1)]
        with patch.object(self.market,'candles',return_value=invalid):
            with self.assertRaisesRegex(ValueError,'Invalid OHLC'):self.engine.tick(AT)
        self.assertFalse(self.trades());self.assertFalse(self.store.rows('orders'))
    def test_expired_signal_is_skipped(self):
        self.engine.tick(AT+timedelta(seconds=11))
        self.assertFalse(self.trades());self.assertIn('Stale',self.store.rows('signals')[0]['payload']['rejection_reason'])
    def test_configured_premium_stop_and_target(self):
        for field,bid,reason in [('stop_percent',80,'STOP_LOSS'),('target_percent',130,'TARGET')]:
            with self.subTest(field=field),tempfile.TemporaryDirectory() as root:
                s=Store('ema_trend',root);s.control('RUNNING');cfg={**self.cfg,field:20}
                with s.tx() as c:c.execute('UPDATE state SET config=?',(encoded(cfg),))
                m=Market();e=Engine(s,strategy('ema_trend'),m,PaperBroker());e.tick(AT)
                m.bid=bid;m.ask=bid+.1;e.tick(AT+timedelta(seconds=5))
                t=s.rows('trades')[0]['payload'];self.assertEqual(t['status'],'CLOSED');self.assertEqual(t['exit_reason'],reason)
    def test_trailing_stop_preserves_high_water_after_restart(self):
        with self.store.tx() as c:c.execute('UPDATE state SET config=?',(encoded({**self.cfg,'trailing_percent':10}),))
        self.enter();self.market.bid=120;self.market.ask=120.1;self.store.control('PAUSED');self.engine.tick(AT+timedelta(seconds=5))
        self.market.bid=107;self.market.ask=107.1
        Engine(self.store,strategy('ema_trend'),self.market,PaperBroker()).tick(AT+timedelta(seconds=10))
        self.assertEqual(self.trades()[0]['exit_reason'],'TRAILING_STOP');self.assertEqual(self.trades()[0]['high_water_bid'],120)
    def test_global_kill_closes_and_blocks(self):
        self.enter()
        with self.store.tx() as c:c.execute('UPDATE control.settings SET payload=?',(encoded({**self.store.global_settings(c),'kill_switch':True}),))
        self.engine.tick(AT+timedelta(seconds=5));self.assertEqual(self.trades()[0]['exit_reason'],'GLOBAL_KILL');self.assertEqual(len(self.trades()),1)
    def test_missing_price_retains_exposure_on_stop(self):
        self.enter();self.store.control('STOPPED');self.market.connected=False
        with self.assertRaises(ConnectionError):self.engine.tick(AT+timedelta(seconds=5))
        self.assertEqual(self.trades()[0]['status'],'OPEN')
        with self.store.connection() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM control.exposure').fetchone()[0],1)
    def test_unknown_submission_never_retried(self):
        class Broker(PaperBroker):
            calls=0
            def submit(self,o):self.calls+=1;raise UnknownSubmission('fixture network timeout')
            def lookup(self,o):return None
        b=Broker();e=Engine(self.store,strategy('ema_trend'),self.market,b);e.tick(AT);e.tick(AT+timedelta(seconds=5))
        self.assertEqual(b.calls,1);self.assertEqual(self.store.state()['status'],'ERROR');self.assertEqual(self.trades()[0]['status'],'UNKNOWN')
    def test_recover_accepted_order_by_tag_without_resubmit(self):
        class Broker(PaperBroker):
            calls=0
            def submit(self,o):self.calls+=1;raise UnknownSubmission('fixture crashed before ACK')
            def lookup(self,o):return {'order_id':'recovered-tag','status':'COMPLETE','filled_qty':65,'average_price':100}
        b=Broker();e=Engine(self.store,strategy('ema_trend'),self.market,b);e.tick(AT)
        Engine(self.store,strategy('ema_trend'),self.market,b).tick(AT+timedelta(seconds=5));self.assertEqual(b.calls,1);self.assertEqual(self.trades()[0]['quantity'],65)
    def test_broker_rejection_releases_reservation(self):
        class Broker(PaperBroker):
            def submit(self,o):return {'order_id':'rejected','status':'REJECTED','filled_qty':0,'average_price':0}
        Engine(self.store,strategy('ema_trend'),self.market,Broker()).tick(AT);self.assertEqual(self.trades()[0]['status'],'REJECTED')
        with self.store.connection() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM control.exposure').fetchone()[0],0)
    def test_worker_fencing_and_independent_logs(self):
        self.assertTrue(self.store.claim('first'));self.assertFalse(self.store.claim('second'))
        other=Store('donchian',self.temp.name);self.assertTrue(other.claim('second'));self.assertFalse(other.rows('events'));self.assertNotEqual(self.store.path,other.path)
    def test_global_reservation_blocks_other_bot(self):
        self.enter();other=Store('pullback',self.temp.name);other.control('RUNNING')
        with other.tx() as c:c.execute('UPDATE state SET config=?',(encoded(self.cfg),))
        with self.store.tx() as c:c.execute('UPDATE control.settings SET payload=?',(encoded({**self.store.global_settings(c),'max_positions':1}),))
        s={'id':'other','at':AT.isoformat(),'side':1,'spot':25000,'reason':'fixture','indicators':{}}
        with self.assertRaisesRegex(ValueError,'Global position'):
            Engine(other,strategy('pullback'),self.market,PaperBroker())._enter(s,self.market.select(1,25000,AT),self.market.quote('',AT),AT,PaperBroker())
    def test_live_requires_separate_configuration(self):
        from unittest.mock import patch
        import app.config
        with patch.object(app.config,'get_settings') as getter:
            getter.return_value.trading_bots_live_enabled=False
            with self.assertRaises(ValueError):UpstoxBroker()
    def test_config_is_locked_while_position_exists(self):
        self.enter()
        with self.assertRaisesRegex(ValueError,'Stop and flatten'):Manager(self.temp.name).configure('ema_trend',self.cfg)
    def test_api_restart_pauses_and_reconciles_retained_position(self):
        self.enter()
        from unittest.mock import patch
        m=Manager(self.temp.name)
        with patch.object(m,'spawn') as spawn:
            m.recover();spawn.assert_called_once_with('ema_trend')
        self.assertEqual(self.store.state()['desired'],'PAUSED')
        Engine(Store('ema_trend',self.temp.name),strategy('ema_trend'),self.market,PaperBroker()).tick(AT+timedelta(seconds=5))
        self.assertEqual(len(self.store.rows('orders')),1);self.assertEqual(self.trades()[0]['quantity'],65)
    def test_global_attempt_throttle_preserves_exit_capacity(self):
        with self.store.tx() as c:
            settings=self.store.global_settings(c);settings.update(max_orders_per_minute=2,max_positions=1);c.execute('UPDATE control.settings SET payload=?',(encoded(settings),))
            self.engine._attempt(c,{'id':'first'},'ENTRY')
            with self.assertRaises(ValueError):self.engine._attempt(c,{'id':'next'},'ENTRY')
            self.engine._attempt(c,{'id':'exit'},'EXIT')
    def test_live_partial_cumulative_fills_are_applied_once(self):
        class Broker(PaperBroker):
            polls=0;cancel_calls=0
            def submit(self,o):return {'order_id':'fixture','status':'PENDING','filled_qty':0,'average_price':0}
            def poll(self,o):
                self.polls+=1;return {'order_id':'fixture','status':'PENDING' if self.polls==1 else 'CANCELLED','filled_qty':65,'average_price':100}
            def cancel(self,o):self.cancel_calls+=1
        b=Broker();e=Engine(self.store,strategy('ema_trend'),self.market,b);e.tick(AT);e.tick(AT+timedelta(seconds=1));e.tick(AT+timedelta(seconds=2))
        self.assertEqual(self.trades()[0]['quantity'],65);self.assertEqual(b.cancel_calls,1);self.assertEqual(len(self.store.rows('orders')),1)
    def test_mode_change_cannot_use_wrong_broker(self):
        with self.store.tx() as c:c.execute('UPDATE state SET config=?',(encoded({**self.cfg,'mode':'live','live_activated':True}),))
        s={'id':'mode','at':AT.isoformat(),'side':1,'spot':25000,'reason':'fixture','indicators':{}}
        with self.assertRaisesRegex(ValueError,'mode changed'):self.engine._enter(s,self.market.select(1,25000,AT),self.market.quote('',AT),AT,PaperBroker())
        self.assertFalse(self.trades())
    def test_concurrent_bots_reserve_atomically(self):
        from concurrent.futures import ThreadPoolExecutor
        other=Store('pullback',self.temp.name);other.control('RUNNING')
        with other.tx() as c:
            c.execute('UPDATE state SET config=?',(encoded(self.cfg),));c.execute('UPDATE control.settings SET payload=?',(encoded({**other.global_settings(c),'max_positions':1}),))
        def enter(store):
            e=Engine(store,strategy(store.bot_id),self.market,PaperBroker());s={'id':store.bot_id,'at':AT.isoformat(),'side':1,'spot':25000,'reason':'fixture','indicators':{}}
            try:e._enter(s,self.market.select(1,25000,AT),self.market.quote('',AT),AT,PaperBroker());return True
            except ValueError:return False
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(enter,[self.store,other]))
        self.assertEqual(sum(results),1)
    def test_daily_loss_room_and_count(self):
        with self.store.tx() as c:
            self.store.save(c,'trades',{'id':'prior','signal_id':'old','status':'CLOSED','mode':'paper','created_at':AT.isoformat(),'exit_at':AT.isoformat(),'net_pnl':-99500})
        self.engine.tick(AT);self.assertEqual(len(self.trades()),1);self.assertEqual(self.store.rows('signals')[0]['status'],'SKIPPED')


class WorkerProcesses(unittest.TestCase):
    def test_cli_configuration_saves_without_starting(self):
        import subprocess
        with tempfile.TemporaryDirectory() as root:
            result=subprocess.run([sys.executable,'-m','trading_bots.ema_trend_bot','--config',str(ROOT/'trading_bots/config/paper.example.json')],cwd=ROOT,env={**os.environ,'TRADING_BOTS_DATA_DIR':root},capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,msg=result.stderr)
            state=json.loads(result.stdout)['state'];self.assertEqual(state['desired'],'STOPPED');self.assertEqual(state['config']['mode'],'paper');self.assertFalse(state['worker_alive'])
    def test_workers_run_independently_and_stop_cleanly(self):
        import time
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as root:
            m=Manager(root);healthy=m.store('ema_trend');faulty=m.store('donchian')
            healthy.control('PAUSED');faulty.control('PAUSED')
            # An unactivated live configuration fails before constructing any live adapter.
            # It exercises worker isolation without invoking a remote broker.
            with faulty.tx() as c:c.execute('UPDATE state SET config=?',(encoded({**defaults(),'mode':'live','live_activated':False}),))
            with patch.dict(os.environ,{'UPSTOX_TRADING_TOKEN':'','TRADING_BOTS_LIVE_ENABLED':'false'}):
                try:
                    m.spawn('ema_trend');m.spawn('donchian')
                    deadline=time.monotonic()+20
                    while time.monotonic()<deadline:
                        if m.alive(healthy) and m.alive(faulty) and faulty.state()['status']=='ERROR':break
                        time.sleep(.2)
                    self.assertTrue(m.alive(healthy));self.assertTrue(m.alive(faulty))
                    self.assertEqual(healthy.state()['status'],'PAUSED');self.assertEqual(faulty.state()['status'],'ERROR')
                    self.assertIn('not been explicitly activated',faulty.state()['error'])
                    self.assertTrue(faulty.rows('events'));self.assertFalse(healthy.rows('orders'));self.assertFalse(faulty.rows('orders'))
                finally:
                    healthy.control('STOPPED');faulty.control('STOPPED')
                    for child in m.children.values():
                        try:child.wait(timeout=15)
                        except Exception:child.kill();child.wait(timeout=5)
                self.assertFalse(m.alive(healthy));self.assertFalse(m.alive(faulty))


class GlobalControls(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch
        self.temp=tempfile.TemporaryDirectory();self.manager=Manager(self.temp.name)
        self.spawn=patch.object(self.manager,'spawn',side_effect=lambda key:self.manager.store(key).claim('test-'+key))
        self.mock_spawn=self.spawn.start()
    def tearDown(self):self.spawn.stop();self.temp.cleanup()
    def test_startup_activates_all_paper_bots(self):
        result=self.manager.startup()
        self.assertEqual(set(result['started']),set(IDS));self.assertFalse(result['failed'])
        self.assertTrue(all(self.manager.detail(key)['state']['status']=='RUNNING' for key in IDS))
    def test_global_start_is_idempotent_for_healthy_workers(self):
        self.manager.start_all();result=self.manager.start_all()
        self.assertEqual(self.mock_spawn.call_count,11);self.assertEqual(set(result['already_running']),set(IDS));self.assertFalse(result['started'])
        result=self.manager.startup();self.assertEqual(self.mock_spawn.call_count,11);self.assertEqual(len(result['already_running']),11)
    def test_startup_preserves_kill_and_global_start_releases_it(self):
        self.manager.global_config({**self.manager.global_config(),'kill_switch':True})
        result=self.manager.startup()
        self.assertFalse(result['started']);self.mock_spawn.assert_not_called();self.assertTrue(self.manager.global_config()['kill_switch'])
        result=self.manager.start_all()
        self.assertEqual(len(result['started']),11);self.assertFalse(self.manager.global_config()['kill_switch'])
    def test_live_bots_require_individual_activation(self):
        from unittest.mock import patch
        s=self.manager.store('ema_trend')
        with s.tx() as c:c.execute('UPDATE state SET config=?',(encoded({**defaults(),'mode':'live','live_activated':True}),))
        with patch('trading_bots.common.manager.UpstoxBroker',side_effect=AssertionError('No live adapter should be constructed')):
            result=self.manager.startup()
        self.assertEqual(len(result['started']),10);self.assertEqual(result['skipped'][0]['bot_id'],'ema_trend');self.assertEqual(s.state()['desired'],'STOPPED')
    def test_retained_exposure_keeps_protective_worker_paused(self):
        s=self.manager.store('ema_trend')
        with s.tx() as c:c.execute('UPDATE state SET config=?',(encoded({**defaults(),'capital':1000000,'max_loss_per_trade':100000,'max_daily_loss':100000,'max_quantity':65}),))
        s.control('RUNNING');Engine(s,strategy('ema_trend'),Market(),PaperBroker()).tick(AT)
        result=self.manager.startup()
        self.assertEqual(s.state()['desired'],'PAUSED');self.assertTrue(self.manager.alive(s))
        self.assertEqual(len(s.rows('orders')),1);self.assertIn('ema_trend',[r['bot_id'] for r in result['skipped']]);self.assertEqual(len(result['started']),10)
    def test_one_worker_start_failure_does_not_block_other_bots(self):
        def spawn(key):
            if key=='ema_trend':raise OSError('fixture worker launch failed')
            self.manager.store(key).claim('test-'+key)
        self.mock_spawn.side_effect=spawn
        result=self.manager.start_all()
        self.assertEqual(len(result['started']),10);self.assertEqual(result['failed'][0]['bot_id'],'ema_trend')
        self.assertEqual(self.manager.store('ema_trend').state()['status'],'ERROR')
    def test_individual_start_cannot_override_a_global_kill(self):
        self.manager.global_config({**self.manager.global_config(),'kill_switch':True})
        with self.assertRaisesRegex(ValueError,'kill switch'):self.manager.control('ema_trend','start')
        self.mock_spawn.assert_not_called()
    def test_start_winning_the_stop_race_keeps_worker_alive(self):
        s=self.manager.store('ema_trend');s.claim('old');s.control('STOPPED');s.control('RUNNING')
        self.assertFalse(s.finish_if_stopped('old'));self.assertTrue(self.manager.alive(s))
    def test_exiting_worker_can_be_replaced_before_its_process_finishes(self):
        from unittest.mock import Mock,patch
        s=self.manager.store('ema_trend');s.claim('old');s.control('STOPPED')
        self.assertTrue(s.finish_if_stopped('old'));s.control('RUNNING')
        with self.assertRaisesRegex(RuntimeError,'lease lost'):s.heartbeat('old')
        self.manager.children['ema_trend']=Mock(poll=Mock(return_value=None))
        self.spawn.stop()
        try:
            with patch('trading_bots.common.manager.subprocess.Popen') as launch:
                self.manager.spawn('ema_trend');launch.assert_called_once()
            self.assertTrue(s.claim('replacement'));s.release('old')
            self.assertTrue(self.manager.alive(s))
        finally:self.spawn.start()


class Api(unittest.TestCase):
    def test_routes_configs_exports_and_origin(self):
        from unittest.mock import patch
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routers.trading_bots import router
        import trading_bots.common.manager as mod
        with tempfile.TemporaryDirectory() as p:
            m=Manager(p);app=FastAPI();app.include_router(router)
            with patch.object(mod,'_manager',m):
                client=TestClient(app);r=client.get('/trading-bots/dashboard');self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['bots']),11)
                r=client.post('/trading-bots/ema_trend/control',json={'action':'pause'});self.assertEqual(r.status_code,200)
                r=client.get('/trading-bots/ema_trend/export?kind=signals');self.assertEqual(r.status_code,200);self.assertIn('data_json',r.text)
                r=client.post('/trading-bots/ema_trend/control',headers={'Origin':'https://untrusted.example'},json={'action':'start'});self.assertEqual(r.status_code,403)
                r=client.put('/trading-bots/ema_trend/config',json={'config':{**defaults(),'max_quantity':-1}});self.assertEqual(r.status_code,422)
                r=client.get('/trading-bots/not-a-bot');self.assertEqual(r.status_code,400)
                r=client.put('/trading-bots/global',json={'kill_switch':True});self.assertEqual(r.status_code,200);self.assertTrue(r.json()['kill_switch'])
    def test_global_start_and_startup_endpoints(self):
        from unittest.mock import patch
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routers.trading_bots import router
        import trading_bots.common.manager as mod
        with tempfile.TemporaryDirectory() as root:
            m=Manager(root);app=FastAPI();app.include_router(router)
            with patch.object(mod,'_manager',m),patch.object(m,'spawn',side_effect=lambda key:m.store(key).claim('test-'+key)):
                client=TestClient(app)
                r=client.post('/trading-bots/startup');self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['started']),11)
                r=client.put('/trading-bots/global',json={'kill_switch':True});self.assertEqual(r.status_code,200)
                r=client.post('/trading-bots/startup');self.assertFalse(r.json()['started']);self.assertTrue(m.global_config()['kill_switch'])
                r=client.post('/trading-bots/global/start',headers={'Origin':'https://untrusted.example'});self.assertEqual(r.status_code,403);self.assertTrue(m.global_config()['kill_switch'])
                r=client.post('/trading-bots/global/start');self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['started']),11);self.assertFalse(m.global_config()['kill_switch'])


class StrategyParity(unittest.TestCase):
    def test_all_eleven_rules_match_research(self):
        import research_directional_lab as lab
        from trading_bots.common.strategy import features
        d,_=lab.load_data();gold=lab.features(d);actual=features(d.to_dict('records'),datetime.fromisoformat('2026-11-09T00:00:00+05:30'))
        source={(family,params):side for family,params,side in lab.rules(gold)}
        params={'ema_trend':'12_26_gap0.5','failed_breakout':'lookback20','pullback':'ema21_tolerance0.75','donchian':'lookback6_buffer0','momentum':'lookback3_atr0.5','compression_breakout':'range3_body1','orb':'minutes15_buffer0.25','ema_reversion':'distance2','gap_follow':'gap_atr3','gap_fade':'gap_atr3','rsi_reversion':'rsi40_distance0'}
        from trading_bots.common.strategy import eligible
        for key in IDS:
            module=strategy(key);expected=eligible(gold,source[(key,params[key])],module.DEFINITION)
            np.testing.assert_array_equal(module.signals(actual),expected,err_msg=key)


if __name__=='__main__':unittest.main()
