"""Deterministic investment portfolio tests; no live data or broker access."""
from copy import deepcopy
from datetime import datetime
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from contextlib import contextmanager
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from investment_bots.catalog import CATALOG, definition
from investment_bots.data import Inputs, IST, NIFTY, canonical
from investment_bots.engine import (DataBlocked, advance, auction_gate, equity, features,
                                    fresh_book, select, target_exposure, whole_quantity)
from investment_bots.service import InvestmentBots
from investment_bots.db import Postgres


@contextmanager
def test_database():
    db=Postgres("investment_test_"+uuid.uuid4().hex[:12])
    try:yield db
    finally:db.drop_test_schema()


def instruments(n=70):
    return {f'NSE_EQ|INE{i:09d}': dict(isin=f'INE{i:09d}', symbol=f'STOCK{i}', name=f'Company {i}',
            industry=f'Industry {i % 12}', segment='NSE_EQ', instrument_type='EQ',
            instrument_key=f'NSE_EQ|INE{i:09d}') for i in range(n)}


META = instruments()
KEYS = list(META)
SCORES = {k: 100 - i for i, k in enumerate(KEYS)}
PRICES = {k: 100. for k in KEYS}


def step(book, offset=0, **kwargs):
    args = dict(day='2026-11-13', offset=offset, opens=PRICES, closes=PRICES,
                scores=SCORES, instruments=META)
    return advance(book, **(args | kwargs))


class SelectionTests(unittest.TestCase):
    def test_top20_and_industry_cap_continue_beyond_top20(self):
        meta = deepcopy(META)
        for k in KEYS[:30]: meta[k]['industry'] = 'Other'
        _, kept, new = select(SCORES, {}, meta)
        self.assertEqual(len(new), 20)
        self.assertEqual(new[:6], KEYS[:6])
        self.assertEqual(new[6], KEYS[30])
        self.assertEqual(kept, [])

    def test_rank39_kept_rank40_and_unranked_sold(self):
        held = {KEYS[39]: {}, KEYS[40]: {}, 'missing': {}}
        sells, kept, _ = select(SCORES, held, META)
        self.assertEqual(kept, [KEYS[39]])
        self.assertEqual(sells, [KEYS[40], 'missing'])

    def test_ties_by_key_and_fewer20_skip(self):
        tied = {k: 1 for k in reversed(KEYS)}
        self.assertEqual(select(tied, {}, META)[2], sorted(KEYS)[:20])
        self.assertIsNone(select(dict(list(SCORES.items())[:19]), {}, META))
        with self.assertRaises(DataBlocked):select({**SCORES, KEYS[0]: float('inf')}, {}, META)


class FeatureTests(unittest.TestCase):
    def panel(self, n=25, days=90):
        meta = instruments(n)
        ix = pd.bdate_range('2025-01-01', periods=days).strftime('%Y-%m-%d')
        t = np.arange(days)
        close = pd.DataFrame({k: 100 * np.exp(.003*t + .01*np.sin(t+i)) for i,k in enumerate(meta)}, index=ix)
        volume = pd.DataFrame({k: 100000+i*999 for i,k in enumerate(meta)}, index=ix)
        return meta, close, volume

    def test_exact_score_sample_vol_and_no_pre2025_warmup(self):
        meta, c, v = self.panel()
        u, s = features(c, v, meta)
        k = next(iter(meta))
        returns = np.log(c[k].to_numpy()[1:] / c[k].to_numpy()[:-1])[-42:]
        expected = (c[k].iloc[-1] / c[k].iloc[-64] - 1) / (np.std(returns,ddof=1)*np.sqrt(63))
        self.assertAlmostEqual(s[k].iloc[-1], expected, places=11)
        self.assertTrue(s.iloc[:63].isna().all().all())
        self.assertTrue(u.iloc[-1].all())
        oldc, oldv = c.copy(), v.copy()
        oldc.loc['2024-12-31'] = 1; oldv.loc['2024-12-31'] = 1
        pd.testing.assert_frame_equal(features(oldc.sort_index(),oldv.sort_index(),meta)[1],s)

    def test_causal_six_session_mask_never_changes_previous_scores(self):
        meta,c,v = self.panel(days=100)
        k = next(iter(meta)); c.loc[c.index[80]:,k] *= 1.6
        u,s = features(c,v,meta)
        self.assertTrue(u[k].iloc[79])
        self.assertFalse(u[k].iloc[80:86].any())
        self.assertTrue(u[k].iloc[86])
        pd.testing.assert_frame_equal(features(c.iloc[:80],v.iloc[:80],meta)[1],s.iloc[:80])

    def test_zero_vol_and_adv_boundary_tie_fail_closed(self):
        meta,c,v = self.panel(n=301)
        c[:] = 100.; v[:] = 100.
        with self.assertRaisesRegex(DataBlocked,'universe_ties'): features(c,v,meta)
        with self.assertRaisesRegex(DataBlocked,'non_finite_score'):features(c.iloc[:,:25],v.iloc[:,:25],instruments(25))

    def test_fund_and_inf_excluded(self):
        meta,c,v = self.panel()
        keys = list(meta)
        meta[keys[0]]['symbol']='SILVERETF';meta[keys[1]]['isin']='INF000000001'
        u,_=features(c,v,meta)
        self.assertFalse(u[keys[:2]].any().any())


class EngineTests(unittest.TestCase):
    def test_decision_has_no_same_session_fill_and_cost_accounting(self):
        book, fills, intents = step(fresh_book())
        self.assertFalse(fills);self.assertEqual(equity(book),1_000_000)
        self.assertEqual(len(intents),20);self.assertEqual(intents[0]['quantity'],500)
        book,fills,_=step(book,offset=1,day='2026-11-16')
        self.assertEqual(len(book['holdings']),20)
        self.assertAlmostEqual(equity(book),997750.)
        self.assertAlmostEqual(book['fees'],2250.)
        self.assertEqual(book['cash'],0.)
        self.assertTrue(all(f['real_orders_submitted']==0 for f in fills))

    def test_sell_before_buy_and_missing_sell_waits_missing_buy_dropped(self):
        book,_,_=step(fresh_book());book,_,_=step(book,1)
        scores={k:100-i for i,k in enumerate(KEYS[20:]+KEYS[:20])}
        book,_,_=step(book,5,scores=scores)
        first_sell=book['pending_sells'][0]['instrument_key']
        first_buy=book['pending_buys'][0]['instrument_key']
        opens={**PRICES,first_sell:None,first_buy:None}
        book,fills,_=step(book,6,opens=opens,scores=scores)
        self.assertEqual(book['pending_sells'][0]['instrument_key'],first_sell)
        self.assertEqual(book['pending_buys'],[])
        sides=[f['side'] for f in fills if f.get('reference_quantity')]
        self.assertEqual(sides,sorted(sides,key=lambda s:s!='SELL'))
        self.assertLessEqual(len(book['holdings']),20)

    def test_new_decision_replaces_pending_sell_when_rank_recovers(self):
        book,_,_=step(fresh_book());book,_,_=step(book,1)
        key=KEYS[0];book['pending_sells']=[dict(instrument_key=key,quantity=500)]
        book,_,_=step(book,5,opens={**PRICES,key:None})
        self.assertEqual(book['pending_sells'],[])
        self.assertIn(key,book['holdings'])

    def test_fewer20_skips_entire_overlay_decision(self):
        book,_,_=step(fresh_book());book,_,_=step(book,1)
        original=deepcopy(book);original['pending_sells']=[dict(instrument_key=KEYS[0],quantity=500)]
        book,_,intents=step(original,5,opens={**PRICES,KEYS[0]:None},scores={},overlay=True,exposure=.5)
        self.assertFalse(intents);self.assertFalse(book['pending_resize'])
        self.assertEqual(book['pending_sells'],original['pending_sells'])

    def test_minimum_buy_uses_unscaled_slot_and_cash_never_negative(self):
        book,_,_=step(fresh_book(),exposure=.1)
        book,fills,_=step(book,1)
        self.assertFalse(book['holdings'])
        self.assertTrue(all(f['reason']=='minimum_buy' for f in fills))
        self.assertEqual(book['cash'],1_000_000)

    def test_retained_unfilled_sells_prevent_over20(self):
        book,_,_=step(fresh_book());book,_,_=step(book,1)
        book['pending_buys']=[dict(instrument_key=KEYS[21],quantity=500,weight=.05)]
        book,fills,_=step(book,2)
        self.assertEqual(len(book['holdings']),20)
        self.assertEqual(fills[0]['reason'],'position_limit')

    def test_daily_c1_rescale_even_without_rank_rebalance(self):
        book,_,_=step(fresh_book());book,_,_=step(book,1)
        book,_,intents=step(book,2,overlay=True,exposure=.5)
        self.assertEqual(len(book['pending_resize']),20)
        self.assertTrue(all(i['reason']=='exposure_resize' for i in intents))
        book,fills,_=step(book,3,overlay=True,exposure=.5)
        exposed=sum(p['value'] for p in book['holdings'].values())/equity(book)
        self.assertAlmostEqual(exposed,.5,delta=.002)
        self.assertGreater(book['cash'],0)
        self.assertTrue(all(f['side']=='SELL' for f in fills))
        pnl=book['realized_pnl']+sum(p['value']-p['basis'] for p in book['holdings'].values())
        self.assertAlmostEqual(pnl,equity(book)-1_000_000)

    def test_vol_target_exact_and_undefined(self):
        returns=np.linspace(-.02,.02,20);values=np.r_[1.,np.cumprod(1+returns)]
        self.assertAlmostEqual(target_exposure(values),.15/(np.std(returns,ddof=1)*np.sqrt(252)))
        self.assertEqual(target_exposure([1]*21),1.)
        self.assertEqual(target_exposure([1]*10),1.)

    def test_reference_fractional_versus_zero_whole_intent_explicit(self):
        self.assertEqual(whole_quantity(10000,14000),0)
        prices={k:14000 for k in KEYS}
        b,_,intents=step(fresh_book(200_000),closes=prices,opens=prices)
        self.assertTrue(all(i['status']=='REJECTED' for i in intents))
        b,_,_=step(b,1,closes=prices,opens=prices)
        self.assertEqual(len(b['holdings']),20)  # documented fractional reference convention


class AuctionTests(unittest.TestCase):
    def test_response_received_after_cutoff_cannot_justify_earlier_entry(self):
        with test_database() as db:
            source=Inputs(db);key=KEYS[0]
            q=dict(indicative_equilibrium_price=100,indicative_equilibrium_quantity=10000,
                   indicative_imbalance_quantity_market=0,timestamp='2026-11-16T09:04:59+05:30')
            source.snapshot('2026-11-16','09:04:30','2026-11-16T09:05:01+05:30',dict(quotes={key:q}))
            self.assertEqual(source.evidence('2026-11-16',key,500),'unobserved')
            q['timestamp']='2026-11-16T09:03:30+05:30'
            source.snapshot('2026-11-16','09:03:30','2026-11-16T09:03:31+05:30',dict(quotes={key:q}))
            self.assertEqual(source.evidence('2026-11-16',key,500),'likely')

    def test_wrong_date_or_undated_receipt_is_not_decision_evidence(self):
        for received in ('2026-11-15T09:04:31+05:30','2026-11-16T09:04:31'):
            with test_database() as db:
                source=Inputs(db);key=KEYS[0]
                q=dict(indicative_equilibrium_price=100,indicative_equilibrium_quantity=10000,
                       indicative_imbalance_quantity_market=0,timestamp='2026-11-16T09:04:30+05:30')
                source.snapshot('2026-11-16','09:04:30',received,dict(quotes={key:q}))
                self.assertEqual(source.evidence('2026-11-16',key,500),'unobserved')

    def test_classifier_rule_precedence_and_boundaries(self):
        dec=dict(iep=100,ieq=1000,imbalance_market=0)
        self.assertEqual(auction_gate(100,None),'unobserved')
        self.assertEqual(auction_gate(100,dec,stale=True),'stale_quote')
        self.assertEqual(auction_gate(100,{**dec,'iep':0}),'no_auction_indicated')
        self.assertEqual(auction_gate(100,{**dec,'imbalance_market':None}),'uncertain_market_imbalance')
        self.assertEqual(auction_gate(101,dec),'uncertain_size')
        self.assertEqual(auction_gate(100,dec,dict(volume=0)),'no_auction_final')
        self.assertEqual(auction_gate(100,dec,dict(volume=999)),'uncertain_size')
        self.assertEqual(auction_gate(100,dec,dict(volume=1000)),'likely')
        self.assertEqual(auction_gate(100,dec),'likely')
        self.assertEqual(auction_gate(100,{**dec,'ieq':float('nan')}),'no_auction_indicated')
        self.assertEqual(auction_gate(float('nan'),dec),'rejected_order')
        self.assertEqual(auction_gate(0,dec),'rejected_order')

    def test_unobserved_buys_dropped_sells_carried_no_fabricated_fill(self):
        b,_,_=step(fresh_book());b,fills,_=step(b,1,gate=lambda *a:'unobserved')
        self.assertFalse(b['holdings']);self.assertEqual(b['cash'],1_000_000)
        b,_,_=step(fresh_book());b,_,_=step(b,1)
        b['pending_sells']=[dict(instrument_key=KEYS[0],quantity=500)]
        b,fills,_=step(b,2,gate=lambda *a:'stale_quote')
        self.assertIn(KEYS[0],b['holdings']);self.assertEqual(len(b['pending_sells']),1)

    def test_snapshot_choice_timestamp_and_checksum(self):
        with test_database() as db:
            source=Inputs(db);key=KEYS[0]
            q=dict(indicative_equilibrium_price=100,indicative_equilibrium_quantity=10000,
                   indicative_imbalance_quantity_market=0,timestamp='2026-11-16T09:04:30+05:30')
            source.snapshot('2026-11-16','09:04:30','2026-11-16T09:04:31+05:30',dict(quotes={key:q}))
            self.assertEqual(source.evidence('2026-11-16',key,500),'likely')
            self.assertEqual(source.evidence('2026-11-16',key,0),'rejected_order')
            source.snapshot('2026-11-16','09:12:30','2026-11-16T09:12:31+05:30',dict(quotes={key:{**q,'volume':1}}))
            self.assertEqual(source.evidence('2026-11-16',key,500),'uncertain_size')
            with source.connection() as c:c.execute("UPDATE snapshots SET payload='{}'")
            with self.assertRaisesRegex(DataBlocked,'checksum'):source.evidence('2026-11-16',key,500)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.db=Postgres('investment_test_'+uuid.uuid4().hex[:12]);self.service=InvestmentBots(self.db)
    def tearDown(self):self.db.drop_test_schema()

    def test_four_registered_paper_enabled_with_independent_storage(self):
        from trading_bots.catalog import IDS
        dash=self.service.dashboard()
        self.assertEqual(len(dash['bots']),4);self.assertEqual(len(IDS),11)
        self.assertTrue(all(b['state']['enabled'] and b['state']['mode']=='paper' for b in dash['bots']))
        self.assertEqual(sum(b['metrics']['cash'] for b in dash['bots']),4_000_000)
        self.assertTrue(all(b['real_orders_submitted']==0 for b in dash['bots']))

    def test_missing_inputs_stay_waiting_without_accessing_provider(self):
        with patch('investment_bots.service.ReadOnlyMarket',side_effect=AssertionError('unexpected provider')):
            self.service.tick(datetime(2026,11,14,8,tzinfo=IST),force=True)
        self.assertTrue(all(b['state']['status']=='AWAITING_DATA' for b in self.service.dashboard()['bots']))

    def test_latched_pause_persists_restart_and_no_implicit_liquidation(self):
        self.service.global_control('pause')
        restarted=InvestmentBots(self.db)
        self.assertTrue(restarted.dashboard()['global_controls']['kill_switch'])
        with self.assertRaises(ValueError):restarted.control('C0_R','start')
        restarted.global_control('start');restarted.control('C2_S','pause')
        self.assertFalse(restarted.detail('C2_S')['state']['enabled'])
        self.assertTrue(restarted.detail('C0_R')['state']['enabled'])

    def replay_fixture(self, bot_id='C0_R', missing=False):
        sessions=['2026-11-12','2026-11-13','2026-11-15','2026-11-16','2026-11-17','2026-11-18','2026-11-19']
        frames={f:pd.DataFrame(PRICES,index=sessions) for f in ['o','h','l','c','v']}
        if missing:frames['c'].loc[sessions[2],KEYS[:2]]=np.nan
        u=pd.DataFrame(True,index=sessions,columns=KEYS)
        scores=pd.DataFrame(SCORES,index=sessions)
        with self.service.inputs.connection() as c:
            c.execute('INSERT INTO metadata VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET payload=EXCLUDED.payload',('bundle',canonical(dict(sources={'fixture':'immutable'}))))
        self.service.reconcile(bot_id,META,sessions,frames,u,scores,{})
        return sessions,frames,u,scores

    def test_replay_idempotency_and_conflict_keeps_original_record(self):
        sessions,frames,u,scores=self.replay_fixture()
        before=self.service.detail('C0_R')
        self.replay_fixture();self.assertEqual(before,self.service.detail('C0_R'))
        frames['o'].loc[sessions[2],KEYS[0]]=120
        with self.assertRaisesRegex(DataBlocked,'record_conflict'):
            self.service.reconcile('C0_R',META,sessions,frames,u,scores,{})
        self.assertEqual(before,self.service.detail('C0_R'))

    def test_staggered_books_and_special_session_count(self):
        sessions,_,_,_=self.replay_fixture('C2_S')
        b=self.service.detail('C2_S')
        self.assertEqual(b['history'][0]['cash'],1_000_000)
        self.assertEqual(len(b['positions']),100)
        self.assertEqual(len(b['history']),6)  # Sunday fixture advances phase, not a weekday counter
        with self.service.connection() as c:
            r=json.loads(c.execute("SELECT payload FROM records WHERE bot_id='C2_S' AND session=%s",(sessions[2],)).fetchone()[0])
        self.assertEqual(len(r['books'][0]['holdings']),20)
        self.assertEqual(r['books'][1]['cash'],200_000)

    def test_completeness_gate_blocks_without_overwriting_previous_state(self):
        with self.assertRaisesRegex(DataBlocked,'incomplete_market_data'):self.replay_fixture(missing=True)
        self.assertEqual(self.service.detail('C0_R')['last_session'],'2026-11-13')

    def test_pause_fences_inflight_reconciler(self):
        self.service.control('C0_R','pause')
        self.replay_fixture()
        self.assertIsNone(self.service.detail('C0_R')['last_session'])

    def test_final_window_session_has_no_next_year_intents(self):
        sessions=['2026-11-13','2026-12-31']
        frames={f:pd.DataFrame(PRICES,index=sessions) for f in ['o','h','l','c','v']}
        u=pd.DataFrame(True,index=sessions,columns=KEYS)
        scores=pd.DataFrame(SCORES,index=sessions)
        with self.service.inputs.connection() as c:
            c.execute('INSERT INTO metadata VALUES(%s,%s)',('bundle',canonical(dict(sources={'fixture':'immutable'}))))
        self.service.reconcile('C0_R',META,sessions,frames,u,scores,{})
        self.assertFalse(self.service.detail('C0_R')['orders'])
        with self.service.connection() as c:
            r=json.loads(c.execute("SELECT payload FROM records WHERE bot_id='C0_R' ORDER BY session DESC LIMIT 1").fetchone()[0])
        self.assertFalse(r['books'][0]['pending_sells'])
        self.assertFalse(r['books'][0]['pending_buys'])

    def test_scheduled_tick_processes_all_four_after_valid_inputs(self):
        sessions=['2025-04-01','2026-11-13','2026-11-16']
        frames={f:pd.DataFrame(PRICES,index=sessions) for f in ['o','h','l','c','v']}
        with self.service.inputs.connection() as c:
            c.execute('INSERT INTO metadata VALUES(%s,%s)',('bundle',canonical(dict(sources={'fixture':'immutable'}))))
        self.service.market=object()
        u=pd.DataFrame(True,index=sessions,columns=KEYS)
        scores=pd.DataFrame(SCORES,index=sessions)
        with patch.object(self.service.inputs,'refresh'),patch.object(self.service.inputs,'load',return_value=(META,sessions,frames)),patch('investment_bots.service.features',return_value=(u,scores)),patch('investment_bots.service.verify_inputs',return_value=(None,None,{'integrity':{}})):
            self.service.tick(datetime(2026,11,17,8,tzinfo=IST),force=True)
        bots={b['definition']['id']:b for b in self.service.dashboard()['bots']}
        self.assertTrue(all(b['state']['status']=='RUNNING' for b in bots.values()))
        self.assertEqual(len(bots['C0_R']['positions']),20)
        self.assertFalse(bots['C0_R_X']['positions'])
        self.assertEqual(len(bots['C2_S']['positions']),20)

    def test_shadow_vol_target_includes_seeded_anchor_return(self):
        from investment_bots.reference import sim5
        rng=np.random.default_rng(2026);n=70;t=50
        c=100*np.exp(np.cumsum(rng.normal(0,.04,(t,n)),axis=0))
        score=rng.normal(size=(t,n));sessions=pd.bdate_range('2025-03-31',periods=t).strftime('%Y-%m-%d').tolist()
        a=dict(o=c,c=c,industry=np.array([META[k]['industry'] for k in KEYS]))
        ref=sim5.run(a,score,1)['eq']
        sigma=pd.Series(ref).pct_change(fill_method=None).rolling(20).std()*np.sqrt(252)
        expected=(.15/sigma.where(sigma>0)).clip(upper=1).fillna(1)
        frames={'o':pd.DataFrame(c,index=sessions,columns=KEYS),'c':pd.DataFrame(c,index=sessions,columns=KEYS)}
        actual=self.service.shadow(META,sessions,frames,pd.DataFrame(score,index=sessions,columns=KEYS))
        np.testing.assert_allclose([actual[d] for d in sessions[1:]],expected.iloc[1:],atol=1e-12,rtol=0)

    def test_export_reports_reference_and_whole_share_columns(self):
        self.replay_fixture()
        orders=self.service.export('C0_R','orders');fills=self.service.export('C0_R','executions')
        self.assertIn('quantity',orders);self.assertIn('reference_quantity',fills)
        self.assertIn('real_orders_submitted',fills)
        with self.assertRaises(ValueError):self.service.control('unknown','start')

    def test_api_scope_exports_origin_and_live_rejection(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routers.investment_bots import router
        app=FastAPI();app.include_router(router)
        with patch('app.routers.investment_bots.manager',return_value=self.service):
            with TestClient(app) as client:
                self.assertEqual(client.get('/investment-bots/dashboard').status_code,200)
                self.assertEqual(client.post('/investment-bots/C0_R/control',json={'action':'start','mode':'live'}).status_code,422)
                self.assertEqual(client.post('/investment-bots/C0_R/control',json={'action':'pause'},headers={'Origin':'https://evil.example'}).status_code,403)
                self.assertEqual(client.post('/investment-bots/C0_R/control',json={'action':'pause'}).status_code,200)
                self.assertEqual(client.get('/investment-bots/C2_S/specification').status_code,200)
                self.assertEqual(client.get('/investment-bots/C0_R/export?kind=equity').status_code,200)


class BundleTests(unittest.TestCase):
    def test_postgres_import_conflict_preserves_existing_market_data(self):
        with test_database() as db:
            source=Inputs(db);key=KEYS[0]
            source.save_bars(key,[['2026-11-13',100,101,99,100,1000]],'2026-11-13')
            with self.assertRaisesRegex(DataBlocked,'panel_check'):
                with source.connection() as c:
                    source.insert_bars(c,[(key,'2026-11-13',100,102,99,101,1000)])
            with source.connection() as c:
                close=c.execute(f'SELECT close FROM {db.market_table} WHERE instrument_key=%s',(key,)).fetchone()[0]
            self.assertEqual(close,100)

    def test_split_bonus_safeguard_rejects_unadjusted_ex_date(self):
        sessions=['2026-11-12','2026-11-13'];key=KEYS[0]
        actions=[dict(isin=META[key]['isin'],name='Stock split',ex_date='2026-11-13')]
        c=pd.DataFrame({key:[100,50]},index=sessions)
        with self.assertRaisesRegex(DataBlocked,'split_bonus'):
            Inputs.validate_actions(actions,META,sessions,c)
        c[key]=[100,99]
        Inputs.validate_actions(actions,META,sessions,c)

    def test_bundle_identity_pin_daily_validation_and_no_substitute_universe(self):
        with tempfile.TemporaryDirectory() as d,test_database() as db:
            folder=Path(d)/'bundle';folder.mkdir();source=Inputs(db)
            meta=instruments(2284)
            with (folder/'instruments.csv').open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,list(next(iter(meta.values()))));w.writeheader();w.writerows(meta.values())
            with (folder/'daily.csv').open('w',newline='',encoding='utf-8') as f:
                w=csv.writer(f);w.writerow(['instrument_key','session','open','high','low','close','volume'])
                w.writerow([NIFTY,'2026-11-13',100,101,99,100,0])
                w.writerow([next(iter(meta)),'2026-11-13',100,101,99,100,1000])
            (folder/'corporate_actions.json').write_text('[]')
            source.import_bundle(folder);source.import_bundle(folder)
            loaded,sessions,_=source.load('2026-11-13')
            self.assertEqual(len(loaded),2284);self.assertEqual(sessions,['2026-11-13'])
            (folder/'corporate_actions.json').write_text('[{"changed":true}]')
            with self.assertRaisesRegex(ValueError,'already pinned'):source.import_bundle(folder)
            with source.connection() as c:c.execute("UPDATE instruments SET payload='{}' WHERE ordinal=0")
            with self.assertRaisesRegex(DataBlocked,'snapshot_changed'):source.load('2026-11-13')


class FrozenReferenceTests(unittest.TestCase):
    """Cross-check the adapter against unmodified supplied engines, not a test reimplementation."""
    def fixture(self):
        rng=np.random.default_rng(20261114)
        n,t=70,110
        c=100*np.exp(np.cumsum(rng.normal(.001,.015,(t,n)),axis=0))
        o=c*np.exp(rng.normal(0,.004,(t,n)))
        score=rng.normal(size=(t,n))
        a=dict(o=o,c=c,industry=np.array([META[k]['industry'] for k in KEYS]))
        return a,score

    def ours(self,a,scores,phase=0,capital=1e6,targets=None,gate=False):
        b=fresh_book(capital);values=np.ones(len(scores))
        for t in range(phase,len(scores)):
            callback=(lambda key,side,q: 'likely' if (t+KEYS.index(key))%4 else 'unobserved') if gate else None
            b,_,_=advance(b,day=f'session-{t}',offset=t-phase,
                opens=dict(zip(KEYS,a['o'][t])),closes=dict(zip(KEYS,a['c'][t])),
                scores=dict(zip(KEYS,scores[t])),instruments=META,
                exposure=targets[t] if targets is not None else 1.,overlay=targets is not None,gate=callback)
            values[t]=equity(b)/capital
        return values,b

    def test_c0_against_frozen_sim5(self):
        from investment_bots.reference import sim5
        a,score=self.fixture()
        reference=sim5.run(a,score,0,log=True)
        values,b=self.ours(a,score)
        np.testing.assert_allclose(values,reference['eq'],atol=1e-12,rtol=0)
        self.assertEqual(set(b['holdings']),{KEYS[k] for k in reference['holdings']})

    def test_c1_fixed_open_equity_against_frozen_sim5(self):
        from investment_bots.reference import sim5
        a,score=self.fixture();targets=.65+.3*np.sin(np.arange(len(score))*.2)
        reference=sim5.run(a,score,0,exposure=targets,rebalance_on_exposure=.10)
        values,_=self.ours(a,score,targets=targets)
        np.testing.assert_allclose(values,reference['eq'],atol=1e-12,rtol=0)

    def test_c2_five_phase_aggregate_against_frozen_sim5(self):
        from investment_bots.reference import sim5
        a,score=self.fixture();expected=[];actual=[]
        for j in range(5):
            expected.append(np.nan_to_num(sim5.run(a,score,j)['eq'],nan=1.))
            actual.append(self.ours(a,score,phase=j,capital=200000)[0])
        np.testing.assert_allclose(np.mean(actual,axis=0),np.mean(expected,axis=0),atol=1e-12,rtol=0)

    def test_c0x_gate_path_against_frozen_xsim(self):
        from investment_bots.reference import xsim
        a,score=self.fixture()
        def fill(t,s,side,rupees,qty):return (a['o'][t,s],1.,'likely') if (t+s)%4 else (None,0.,'unobserved')
        reference=xsim.run(a,score,0,fill=fill)
        values,_=self.ours(a,score,gate=True)
        np.testing.assert_allclose(values,reference['eq'],atol=1e-12,rtol=0)


if __name__ == '__main__':unittest.main(verbosity=2)
