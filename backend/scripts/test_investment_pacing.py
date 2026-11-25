"""Capital deployment invariants and isolated PostgreSQL paper-run integration."""
from copy import deepcopy
from datetime import datetime
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd

ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from investment_bots.practice import DEFAULT_POLICY,advance_portfolio,validate_policy
from investment_bots.engine import fresh_book,equity
from investment_bots.service import InvestmentBots
from investment_bots.data import IST,canonical
from test_investment_bots import test_database,META,KEYS,SCORES,PRICES


def step(books,offset,**kwargs):
    args=dict(day=f'2026-11-{19+offset:02d}',offset=offset,opens=PRICES,closes=PRICES,scores=SCORES,instruments=META,policy=DEFAULT_POLICY)
    return advance_portfolio(books,**(args|kwargs))


class DeploymentTests(unittest.TestCase):
    def test_initial_allocation_is_queued_and_only_two_names_fill(self):
        books,orders,intents,allocation=step([fresh_book()],0)
        self.assertEqual(orders,[]);self.assertEqual(len(intents),20);self.assertEqual(books[0]['cash'],1e6)
        books,orders,intents,allocation=step(books,1)
        self.assertEqual(allocation['buy_orders'],2);self.assertEqual(len(books[0]['holdings']),2)
        self.assertEqual(len(books[0]['pending_buys']),18);self.assertGreater(books[0]['cash'],900000)
        self.assertLessEqual(allocation['buy_amount'],100000)
    def test_many_days_cannot_deploy_full_capital(self):
        books=[fresh_book()]
        for offset in range(25):
            books,orders,_,allocation=step(books,offset,day='2026-12-01')
            eq=sum(equity(b) for b in books);held=sum(p['value'] for b in books for p in b['holdings'].values())
            self.assertLessEqual(allocation['buy_orders'],2);self.assertLessEqual(allocation['buy_amount'],allocation['daily_buy_limit']+1e-7)
            self.assertLessEqual(held/eq,.5+1e-9);self.assertGreaterEqual(books[0]['cash'],.5*eq-1e-7)
        self.assertEqual(len(books[0]['holdings']),20)
    def test_staggered_books_share_one_daily_allowance(self):
        books=[fresh_book(200000) for _ in range(5)]
        for offset in range(20):
            books,orders,_,allocation=step(books,offset,day='2026-12-01')
            buys=[x for x in orders if x.get('side')=='BUY' and 'reference_amount' in x]
            self.assertLessEqual(len(buys),2);self.assertLessEqual(allocation['buy_amount'],100000)
            self.assertTrue(all(b['cash']>=0 for b in books))
        self.assertTrue(all(b['holdings'] for b in books))
    def test_overlay_topups_obey_order_and_position_caps(self):
        b=fresh_book();b['cash']=970000
        for key in KEYS[:3]:b['holdings'][key]=dict(value=10000,mark=100,basis=10000,entry_session='2026-11-19')
        b['pending_resize']={key:.1 for key in KEYS[:3]}
        books,orders,_,allocation=step([b],1,overlay=True)
        self.assertEqual(allocation['buy_orders'],2)
        self.assertLessEqual(allocation['buy_amount'],100000)
        self.assertTrue(all(p['value']<=50000+1e-7 for p in books[0]['holdings'].values()))
    def test_volatility_overlay_does_not_concentrate_the_staged_ramp(self):
        books=[fresh_book()]
        for offset in range(5):
            books,orders,_,allocation=step(books,offset,overlay=True)
            self.assertFalse(any(x.get('reason')=='exposure_resize' for x in orders))
        self.assertEqual(len(books[0]['holdings']),8)
    def test_rank_sells_are_not_stopped_by_buy_limit(self):
        b=fresh_book();b['cash']=0
        for key in KEYS[:20]:b['holdings'][key]=dict(value=50000,mark=100,basis=50000,entry_session='2026-11-19')
        b['pending_sells']=[dict(instrument_key=k,quantity=500) for k in KEYS[:20]]
        books,orders,_,_=step([b],1)
        self.assertEqual(len([x for x in orders if x['side']=='SELL']),20);self.assertFalse(books[0]['holdings'])
        self.assertAlmostEqual(books[0]['cash'],997750)
    def test_auction_rejection_never_consumes_or_fabricates_funds(self):
        books,_,_,_=step([fresh_book()],0)
        books,orders,_,allocation=step(books,1,gate=lambda *args:'uncertain_market_imbalance')
        self.assertEqual(books[0]['cash'],1e6);self.assertEqual(allocation['buy_orders'],0);self.assertFalse(books[0]['pending_buys'])
        self.assertEqual(len([x for x in orders if x.get('status')=='DROPPED']),20)
    def test_missing_open_and_invalid_policy_fail_safely(self):
        books,_,_,_=step([fresh_book()],0);prices={k:None for k in PRICES}
        books,orders,_,allocation=step(books,1,opens=prices)
        self.assertEqual(allocation['buy_orders'],0);self.assertEqual(books[0]['cash'],1e6)
        for value in (dict(max_buy_orders=True),dict(max_exposure=float('nan')),dict(daily_buy_fraction=0),dict(unknown=1)):
            with self.assertRaises(ValueError):validate_policy(value)
    def test_capital_conservation_includes_entry_fees(self):
        books,_,_,_=step([fresh_book()],0);books,orders,_,allocation=step(books,1)
        self.assertAlmostEqual(equity(books[0])+books[0]['fees'],1e6)
        self.assertAlmostEqual(sum(x['reference_amount'] for x in orders if 'reference_amount' in x),allocation['buy_amount'])
    def test_cash_budget_still_binds_if_order_count_is_relaxed(self):
        policy={**DEFAULT_POLICY,'max_buy_orders':20}
        books,_,_,_=step([fresh_book()],0,policy=policy)
        books,_,_,allocation=step(books,1,policy=policy)
        self.assertLessEqual(allocation['buy_amount'],100000+1e-7)
        self.assertGreaterEqual(books[0]['cash'],900000-1e-7)


class PaperRunTests(unittest.TestCase):
    def fixture(self,service):
        sessions=['2026-11-19','2026-11-20','2026-11-23'];frames={k:pd.DataFrame(PRICES,index=sessions) for k in ('o','h','l','c','v')}
        universe=pd.DataFrame(True,index=sessions,columns=KEYS);scores=pd.DataFrame(SCORES,index=sessions)
        return sessions,frames,universe,scores
    def test_fresh_run_preserves_old_ledger_and_restart_budgets(self):
        with test_database() as db:
            service=InvestmentBots(db)
            with service.connection() as c:
                c.execute('INSERT INTO metadata VALUES(%s,%s)',('bundle',canonical(dict(sources={'fixture':'original'}))))
                # A prior fully invested reference account is preserved byte-for-byte.
                old=dict(session='2026-11-18',books=[fresh_book()],executions=[],decisions=[],metrics=service.metrics([fresh_book()],1e6))
                from investment_bots.data import digest
                c.execute('INSERT INTO records VALUES(%s,%s,%s,%s)',('C0_R','2026-11-18',canonical(old),digest(old)))
            result=service.configure_paper(at=datetime(2026,11,19,16,tzinfo=IST))
            self.assertEqual(result['bots'][0]['metrics']['cash'],1e6);self.assertIsNone(result['bots'][0]['last_session'])
            run=service.paper_run();sessions,frames,u,scores=self.fixture(service)
            service.reconcile_paper(run,'C0_R',META,sessions,frames,u,scores,{})
            before=service.detail('C0_R');restarted=InvestmentBots(db)
            restarted.reconcile_paper(restarted.paper_run(),'C0_R',META,sessions,frames,u,scores,{})
            self.assertEqual(before,restarted.detail('C0_R'));self.assertEqual(len(before['positions']),4)
            self.assertEqual(len(restarted.detail('C0_R',True)['history']),1)
            with service.connection() as c:
                saved=c.execute("SELECT payload FROM records WHERE bot_id='C0_R'").fetchone()[0]
            self.assertEqual(saved,canonical(old))
    def test_c2_daily_limit_is_global_and_pauses_remain_latched(self):
        with test_database() as db:
            service=InvestmentBots(db);service.configure_paper(at=datetime(2026,11,19,16,tzinfo=IST))
            sessions,frames,u,scores=self.fixture(service);run=service.paper_run()
            service.reconcile_paper(run,'C2_S',META,sessions,frames,u,scores,{})
            with service.connection() as c:
                records=[json.loads(r[0]) for r in c.execute("SELECT payload FROM paper_records WHERE bot_id='C2_S'")]
            self.assertTrue(all(r['allocation']['buy_orders']<=2 for r in records))
            service.global_control('pause');service.configure_paper(at=datetime(2026,11,19,17,tzinfo=IST))
            self.assertTrue(InvestmentBots(db).dashboard()['global_controls']['kill_switch'])
            self.assertTrue(all(not b['state']['enabled'] for b in service.dashboard()['bots']))
    def test_first_session_does_not_backdate_entries_and_old_run_is_fenced(self):
        with test_database() as db:
            service=InvestmentBots(db);service.configure_paper(at=datetime(2026,11,19,16,tzinfo=IST));old=service.paper_run()
            service.configure_paper(at=datetime(2026,11,19,17,tzinfo=IST))
            sessions,frames,u,scores=self.fixture(service);service.reconcile_paper(old,'C0_R',META,sessions,frames,u,scores,{})
            with service.connection() as c:self.assertEqual(c.execute('SELECT count(*) FROM paper_records').fetchone()[0],0)
            self.assertTrue(all(b['metrics']['fees']==0 for b in service.dashboard()['bots']))
    def test_keep_mode_does_not_liquidate_existing_holdings(self):
        with test_database() as db:
            service=InvestmentBots(db);b=fresh_book();b['cash']=0
            for key in KEYS[:20]:b['holdings'][key]=dict(value=50000,mark=100,basis=50000,entry_session='2026-11-16')
            old=dict(session='2026-11-18',books=[b],executions=[],decisions=[],metrics=service.metrics([b],1e6))
            from investment_bots.data import digest
            with service.connection() as c:c.execute('INSERT INTO records VALUES(%s,%s,%s,%s)',('C0_R','2026-11-18',canonical(old),digest(old)))
            result=service.configure_paper(mode='keep',at=datetime(2026,11,19,16,tzinfo=IST))
            bot=next(x for x in result['bots'] if x['definition']['id']=='C0_R')
            self.assertEqual(len(bot['positions']),20);self.assertEqual(bot['metrics']['cash'],0)
    def test_configuration_route_rejects_foreign_origin_and_live_mode(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routers import investment_bots as routes
        app=FastAPI();app.include_router(routes.router)
        with test_database() as db,patch.object(routes,'manager',return_value=InvestmentBots(db)):
            client=TestClient(app);body={'mode':'fresh','policy':DEFAULT_POLICY}
            self.assertEqual(client.post('/investment-bots/paper-testing',json=body,headers={'Origin':'https://untrusted.example'}).status_code,403)
            headers={'Origin':'http://127.0.0.1:3000'}
            self.assertEqual(client.post('/investment-bots/paper-testing',json={'mode':'live'},headers=headers).status_code,422)
            good=client.post('/investment-bots/paper-testing',json=body,headers=headers)
            self.assertEqual(good.status_code,200);self.assertEqual(good.json()['paper_testing']['policy']['max_buy_orders'],2)
            archive=client.get('/investment-bots/C0_R/archive',headers=headers)
            self.assertEqual(archive.status_code,200);self.assertTrue(archive.json()['archived_reference'])


if __name__=='__main__':unittest.main(verbosity=2)
