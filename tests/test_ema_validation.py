import unittest,tempfile,json
from pathlib import Path
import numpy as np
import pandas as pd
from research.ema_validation.engine import *
from research.ema_validation.paper import validate_payload,init,record
from scripts.validate_ema import random_masks
from scripts.ema_analyze import holm
from research.swing_diagnosis.portfolio import simulate_portfolio

class FrozenEMAValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.q=prepare();cache_correlations(cls.q)

    def test_exact_funded_parity_for_universal_and_gated_cost_stress(self):
        q=self.q
        for gate,cost,slip in [(False,1,5),(True,1,5),(True,2,10)]:
            entry=q['sig']['entry']&q['p']['eligible'][:,None]&(q['gate'][None,:] if gate else True)
            fast=simulate(q,orders(q,entry),cost=cost,slip_bps=slip)
            m,d,t=simulate_portfolio(q['p'],{**q['sig'],'entry':entry},q['cfg'],'2024-11-10','2026-11-10','risk_correlation',slip,cost,True)
            np.testing.assert_allclose(fast['equity'],d.equity,rtol=0,atol=1e-8)
            np.testing.assert_allclose(fast['trades'][:,8],t.net_pnl,rtol=0,atol=1e-8)
            self.assertGreaterEqual(fast['cash'].min(),0);self.assertLessEqual(fast['positions'].max(),10)

    def test_exact_opportunity_counts_rs_eligibility_and_common_gate(self):
        q=self.q;m=random_masks(q,120260001)
        for rs in [0,1]:
            source=q['ema']&q['pool']&(q['rs'] if rs else True);d=q['cols']-1
            np.testing.assert_array_equal(m[rs][:,d].sum(axis=0),source[:,d].sum(axis=0))
            self.assertFalse((m[rs]&~q['pool']).any())
            if rs:self.assertFalse((m[rs]&~q['rs']).any())
            # The gate suppresses whole completed dates, never redraws on remainingdays.
            np.testing.assert_array_equal((m[rs]&q['gate'][None,:])[:,q['gate']],m[rs][:,q['gate']])
        again=random_masks(q,120260001);np.testing.assert_array_equal(m[1],again[1])

    def test_randomized_prefix_does_not_depend_on_future_dataset_length(self):
        q=self.q;cut=q['cols'][-100];short={**q,'p':{**q['p'],'dates':q['p']['dates'][:cut]},'cols':q['cols'][q['cols']<cut]}
        for k in ['ema','rs','pool']:short[k]=q[k][:,:cut]
        full=random_masks(q,120260007);prefix=random_masks(short,120260007)
        for rs in [0,1]:np.testing.assert_array_equal(full[rs][:,:cut-1],prefix[rs][:,:cut-1])

    def test_paper_rejects_unfinished_incomplete_and_unverified_bars(self):
        row=dict(open=100,high=101,low=99,close=100,volume=10000,split_factor=1,dividend=0)
        good=dict(date='2026-11-12',previous_session_date='2026-11-11',calendar_source='verified NSE session',price_basis='actual_unadjusted',corporate_actions_verified=True,source='fixture',bars={'ABC':row},nifty_close=25000)
        validate_payload(good,['ABC'],now='2026-11-12 11:00:00+00:00')
        with self.assertRaises(ValueError):validate_payload(good,['ABC'],now='2026-11-12 01:00:00+00:00')
        with self.assertRaises(ValueError):validate_payload(good,['ABC','DEF'],now='2026-11-12 11:00:00+00:00')
        with self.assertRaises(ValueError):validate_payload({**good,'corporate_actions_verified':False},['ABC'],now='2026-11-12 11:00:00+00:00')

    def test_paper_initialization_is_idempotent_and_starts_without_invented_trades(self):
        with tempfile.TemporaryDirectory() as d:
            a=init(d);b=init(d);self.assertEqual(a,b)
            state=json.loads((Path(d)/'state.json').read_text());self.assertEqual(state['trades'],0);self.assertEqual(state['equity'],1e6)
            self.assertEqual(len((Path(d)/'events.jsonl').read_text().splitlines()),1)

    def test_holm_arithmetic(self):np.testing.assert_allclose(holm([.01,.04,.2]),[.03,.08,.2])

    def test_paper_bridge_append_only_and_duplicate_idempotency(self):
        p=self.q['p'];bars={}
        for s,ok in enumerate(p['eligible']):
            if ok:
                c=float(p['actual']['close'][s,-1]);bars[p['symbols'][s]]=dict(open=c,high=c*1.01,low=c*.99,close=c,volume=1000000,split_factor=1,dividend=0)
        payload=dict(date='2026-11-10',previous_session_date='2026-11-09',calendar_source='test fixture only',price_basis='actual_unadjusted',corporate_actions_verified=True,source='synthetic unit test',nifty_close=float(p['niftyclose'][-1]),bars=bars)
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'feed.json';source.write_text(json.dumps(payload));base=Path(d)/'ledger'
            a=record(source,base);b=record(source,base);self.assertEqual(a,b);self.assertEqual(a['trades'],0)
            self.assertEqual(len((base/'events.jsonl').read_text().splitlines()),2)
            payload['source']='revised fixture';source.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):record(source,base)

    def test_paper_refuses_missing_observed_session_bridge(self):
        p=self.q['p'];bars={}
        for s,ok in enumerate(p['eligible']):
            if ok:
                c=float(p['actual']['close'][s,-1]);bars[p['symbols'][s]]=dict(open=c,high=c*1.01,low=c*.99,close=c,volume=1000000,split_factor=1,dividend=0)
        payload=dict(date='2026-11-11',previous_session_date='2026-11-10',calendar_source='test fixture only',price_basis='actual_unadjusted',corporate_actions_verified=True,source='synthetic unit test',nifty_close=float(p['niftyclose'][-1]),bars=bars)
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'feed.json';source.write_text(json.dumps(payload));base=Path(d)/'ledger'
            with self.assertRaises(ValueError):record(source,base)
            self.assertEqual(len((base/'events.jsonl').read_text().splitlines()),1)

if __name__=='__main__':unittest.main()
