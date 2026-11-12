import unittest,json
import numpy as np
import pandas as pd
from research.regime_opportunities.framework import OUT,ROOT,classify
from research.regime_opportunities.forward import events,bh
from research.regime_opportunities.engine import simulate
from research.ema_validation.engine import prepare,cache_correlations,orders,simulate as reference
from scripts import research_regimes as runner

class RegimeOpportunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner.worker_init();cls.q=runner.Q;cls.inputs=runner.INPUT
        cls.market=pd.read_csv(OUT/'market-OHLC.csv',index_col=0);cls.market.index=pd.DatetimeIndex(pd.to_datetime(cls.market.index,utc=True)).tz_convert('Asia/Kolkata')
        cls.tri=pd.read_csv(OUT/'official-TRI.csv',index_col=0);cls.tri.index=cls.market.index

    def test_protective_engine_exact_reference_parity(self):
        q=self.q;entry=self.inputs['entry_EMA']&self.inputs['mask_vol_expansion'][None,:];order=orders(q,entry)
        for cost,slip in [(1,5),(2,10)]:
            a=simulate(q,order,cost=cost,slip_bps=slip);b=reference(q,order,cost=cost,slip_bps=slip)
            np.testing.assert_allclose(a['equity'],b['equity'],rtol=0,atol=1e-8);np.testing.assert_allclose(a['trades'],b['trades'],rtol=0,atol=1e-8)

    def test_holding_benchmark_has_no_protective_exit(self):
        a=simulate(self.q,orders(self.q,self.inputs['entry_buyhold10']),'2026-05-10','2026-11-10',hold_only=True)
        self.assertTrue(np.isin(a['trades'][:,12],[2,5]).all());self.assertGreaterEqual(a['cash'].min(),0);self.assertLessEqual(a['positions'].max(),10)

    def test_framework_future_truncation_invariance_and_unavailability(self):
        p=self.q['p'];sector=self.tri[['Nifty Bank','Nifty IT','Nifty Pharma']];full,feat,defs=classify(self.market,sector,(p,None));cut=len(self.market)-65
        prefix,pfeat,_=classify(self.market.iloc[:cut],sector.iloc[:cut],(p,None))
        for name in full:
            np.testing.assert_array_equal(full[name][:cut],prefix[name]);np.testing.assert_allclose(feat[name][:cut],pfeat[name],equal_nan=True)
        before=self.market.index<pd.Timestamp('2024-11-10',tz=self.market.index.tz)
        for d in defs:
            if d['scope']=='stock_recent':self.assertFalse(full[d['regime']][before].any());self.assertFalse(np.isfinite(feat[d['regime']][before]).any())

    def test_sample_volatility_ratio_and_transition(self):
        a,feat,_=classify(self.market,self.tri[['Nifty Bank','Nifty IT','Nifty Pharma']]);r=self.market.close.pct_change().to_numpy();t=800
        expected=np.std(r[t-19:t+1],ddof=1)/np.std(r[t-59:t+1],ddof=1)
        self.assertAlmostEqual(feat['vol_expansion'][t],expected,places=12)
        np.testing.assert_array_equal(a['new_expansion'],a['vol_expansion']&~np.r_[False,a['vol_expansion'][:-1]])

    def test_random_opportunity_counts_and_pool(self):
        for style in ['momentum','meanreversion','EMA','MACD','support']:
            mask=runner.random_mask(style,261112001);source=self.inputs['entry_'+style];d=self.q['cols']-1
            np.testing.assert_array_equal(mask[:,d].sum(axis=0),source[:,d].sum(axis=0));self.assertFalse((mask&~self.q['pool']).any())

    def test_hash_priority_is_fixed_and_not_momentum_ranking(self):
        import hashlib
        universe=json.loads((ROOT/'artifacts/swing_discovery/universe.json').read_text())['stocks'];isin={x['symbol']:x['isin_at_start'] for x in universe};q=self.q
        for t in [q['cols'][0],q['cols'][-1]]:
            day=str(q['p']['dates'][t-1].date());expected=sorted(range(len(q['p']['symbols'])),key=lambda s:hashlib.sha256((day+'|'+isin[q['p']['symbols'][s]]+'|regime_reference20261112').encode()).digest())
            np.testing.assert_array_equal(q['ranks'][t],expected)

    def test_episode_separation_and_multiple_testing(self):
        a=np.zeros(50,bool);a[[1,21]]=True;self.assertEqual(len(events(a)),1)
        a[:]=False;a[[1,22]]=True;self.assertEqual(len(events(a)),2)
        np.testing.assert_allclose(bh([.01,.04,.2]),[.03,.06,.2])

if __name__=='__main__':unittest.main()
