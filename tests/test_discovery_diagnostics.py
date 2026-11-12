import unittest
import numpy as np
import pandas as pd
from research.swing_discovery.diagnostics import deflated_sharpe,pbo_cscv,portfolio_metrics,development_score

class DiagnosticsTests(unittest.TestCase):
 def test_single_trial_zero_mean_dsr_half(self):
  r=np.tile([-1.,1.],100)
  self.assertAlmostEqual(deflated_sharpe(r,[0],1)['dsr'],.5)
 def test_trial_search_penalizes_identical_observed_sharpe(self):
  rng=np.random.default_rng(12);r=rng.normal(.002,.01,250)
  one=deflated_sharpe(r,[-.1,.1],1);many=deflated_sharpe(r,[-.1,.1],1000)
  self.assertGreater(one['dsr'],many['dsr'])
 def test_dsr_scale_invariance(self):
  rng=np.random.default_rng(22);r=rng.normal(.001,.01,150)
  self.assertAlmostEqual(deflated_sharpe(r,[0,.1],20)['dsr'],deflated_sharpe(r*100,[0,.1],20)['dsr'])
 def test_cash_dsr_not_claimed(self):
  self.assertIsNone(deflated_sharpe(np.zeros(200),[0],5)['dsr'])
 def test_pbo_identical_outcomes_not_identifiable(self):
  self.assertIsNone(pbo_cscv(pd.DataFrame({'a':np.arange(120),'b':np.arange(120)}))['pbo'])
 def test_pbo_symmetric_folds_and_duplicate_control(self):
  rng=np.random.default_rng(14);x=pd.DataFrame(rng.normal(0,.01,(120,4)),columns=list('abcd'));x['copy']=x.a
  d=pbo_cscv(x);self.assertEqual(d['symmetric_splits'],20);self.assertEqual(d['original_rules'],5);self.assertEqual(d['distinct_rules'],4)
  self.assertTrue(0<=d['pbo']<=1)
 def test_catastrophic_drawdown_cannot_be_offset_by_profit(self):
  self.assertEqual(development_score({'n_trades':10000,'worst_stock_drawdown_pct':26,'sharpe':100,'expectancy_r':100}),-1e9)
 def test_sample_veto_is_explicit(self):
  summary={'n_trades':75,'worst_stock_drawdown_pct':1,'sharpe':1,'expectancy_r':.1}
  self.assertEqual(development_score(summary),-1e9);self.assertGreater(development_score(summary,min_trades=50),-1e9)
 def test_marked_drawdown_includes_initial_capital(self):
  nav=pd.Series([900000.,950000.],index=pd.date_range('2025-01-01',periods=2));m=portfolio_metrics(nav)
  self.assertAlmostEqual(m['max_drawdown_pct'],10)

if __name__=='__main__':unittest.main()
