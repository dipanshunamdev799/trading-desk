import unittest
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from research.swing.stock_engine import simulate
from research.swing.stocks import corporate_events,sector,prepare_stock

class StockSwingTests(unittest.TestCase):
 def bars(self,rows):
  idx=pd.DatetimeIndex(['2025-01-09 15:25','2025-01-10 09:15'],tz='Asia/Kolkata')
  return pd.DataFrame(rows,index=idx,columns=['open','high','low','close','split_factor','dividend'])
 def run_case(self,b,s):
  return simulate(b,s,{'initial_capital':10000,'risk_fraction':.01,'cost_model':'equity_delivery'},'2025-01-01','2025-02-01',cost_multiplier=0,slippage_bps=0,allow_short=False)
 def test_split_does_not_create_false_stop_loss(self):
  b=self.bars([[100,101,99,100,1,0],[50,56,49,55,2,0]])
  s=pd.DataFrame({'side':[1],'stop':[95],'atr':[2]},index=b.index[:1]);r=self.run_case(b,s);t=r['trades'].iloc[0]
  self.assertAlmostEqual(t.net_r,2);self.assertEqual(t.share_adjustments,1)
  self.assertEqual(t.entry_fill,100);self.assertEqual(t.entry_quantity,20);self.assertEqual(t.quantity,40)
  self.assertAlmostEqual(r['equity'].equity.iloc[-1],10200)
 def test_dividend_entitlement_offsets_ex_date_drop(self):
  b=self.bars([[100,101,99,100,1,0],[95,96,94,95,1,5]])
  s=pd.DataFrame({'side':[1],'stop':[90],'atr':[3]},index=b.index[:1]);r=self.run_case(b,s);t=r['trades'].iloc[0]
  self.assertEqual(t.dividends,50);self.assertAlmostEqual(t.net_pnl,0)
  self.assertAlmostEqual(r['equity'].equity.iloc[-1],10000)
 def test_ex_date_buy_gets_no_prior_entitlement(self):
  b=self.bars([[100,101,99,100,1,0],[95,96,94,95,1,5]])
  s=pd.DataFrame({'side':[1],'stop':[90],'atr':[3]},index=b.index[1:]);t=self.run_case(b,s)['trades'].iloc[0]
  self.assertEqual(t.dividends,0)
 def test_pending_signal_is_converted_after_split(self):
  b=self.bars([[100,101,99,100,1,0],[50,51,49,50,2,0]])
  s=pd.DataFrame({'side':[1],'stop':[95],'atr':[2]},index=b.index[:1]+pd.Timedelta(minutes=5))
  t=self.run_case(b,s)['trades'].iloc[0];self.assertEqual(t.stop,47.5);self.assertEqual(t.entry_fill,50)
 def test_fractional_entitlement_rejected(self):
  b=self.bars([[100,101,99,100,1,0],[66,67,65,66,1.5,0]])
  s=pd.DataFrame({'side':[1],'stop':[97],'atr':[2]},index=b.index[:1])
  # Risk budget yields33shares, requiring an unmodeled fractional entitlement.
  with self.assertRaises(ValueError):self.run_case(b,s)
 def test_nse_split_and_dividend_parsing(self):
  spec={'symbol':'ABC','current_symbol':'ABC'}
  records=[{'symbol':'ABC','series':'EQ','exDate':'10-Jan-2025','subject':'Face Value Split (Sub-Division) - From Rs10/- Per Share To Re 1/- Per Share'},
           {'symbol':'ABC','series':'EQ','exDate':'10-Jan-2025','subject':'Bonus 4:1'},
           {'symbol':'ABC','series':'EQ','exDate':'10-Jan-2025','subject':'Dividend - Rs 5.50 Per Share'}]
  e=corporate_events(spec,records);self.assertEqual(e[0]['factor'],10);self.assertEqual(e[1]['factor'],5);self.assertEqual(e[2]['dividend'],5.5)
 def test_sector_mapping_is_fixed(self):
  self.assertEqual(sector('INFY'),'IT');self.assertEqual(sector('HDFCBANK'),'banks')
 def test_stock_fork_matches_original_without_actions(self):
  from research.swing.engine import simulate as original
  b=self.bars([[100,101,99,100,1,0],[100,112,99,110,1,0]])
  s=pd.DataFrame({'side':[1],'stop':[95],'atr':[2]},index=b.index[:1])
  cfg={'cost_model':'equity_delivery','initial_capital':10000,'risk_fraction':.01}
  a=simulate(b,s,cfg,'2025-01-01','2025-02-01',allow_short=False)
  o=original(b,s,cfg,'2025-01-01','2025-02-01',allow_short=False)
  pd.testing.assert_frame_equal(a['equity'],o['equity'])
  pd.testing.assert_frame_equal(a['trades'][o['trades'].columns],o['trades'])
 def test_adjusted_and_raw_vendor_bases_restore_same_actual_prices(self):
  spec={'symbol':'ABC','current_symbol':'ABC'}
  acts=[{'symbol':'ABC','series':'EQ','exDate':'10-Jan-2025','subject':'Bonus 1:1'}]
  for vendor_adjusted in [True,False]:
   with tempfile.TemporaryDirectory() as folder:
    p=Path(folder);b=self.bars([[50 if vendor_adjusted else 100]*4+[1,0],[50,50,50,50,1,0]])
    b.to_csv(p/'ABC-regular.csv',index_label='ts');b.iloc[:0].to_csv(p/'ABC-special.csv',index_label='ts')
    n,e,audit=prepare_stock(spec,p,acts)
    self.assertEqual(e.open.iloc[0],100);self.assertEqual(e.open.iloc[1],50)
    self.assertEqual(n.open.iloc[0],50);self.assertEqual(n.open.iloc[1],50)
    self.assertFalse(audit['ranking_excluded'])
 def test_unknown_rights_entitlement_quarantines_stock(self):
  spec={'symbol':'ABC','current_symbol':'ABC'}
  acts=[{'symbol':'ABC','series':'EQ','exDate':'10-Jan-2025','subject':'Rights 1:5 @ Premium Rs 99/-'}]
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);b=self.bars([[100,101,99,100,1,0],[100,101,99,100,1,0]])
   b.to_csv(p/'ABC-regular.csv',index_label='ts');b.iloc[:0].to_csv(p/'ABC-special.csv',index_label='ts')
   n,e,audit=prepare_stock(spec,p,acts);self.assertTrue(audit['ranking_excluded'])
 def test_homogeneous_share_scale_does_not_change_signals(self):
  from research.swing.signals import make_signals,clear_cache
  days=pd.bdate_range('2024-01-01',periods=130,tz='Asia/Kolkata')
  idx=pd.DatetimeIndex([d+pd.Timedelta(minutes=555+5*j) for d in days for j in range(75)])
  rng=np.random.default_rng(923);close=200+np.cumsum(rng.normal(.01,.1,len(idx)))
  b=pd.DataFrame({'open':close,'close':close,'high':close+.1,'low':close-.1,'volume':1000.},index=idx)
  c={'family':'A','htf':240,'ltf':120}
  a=make_signals(b,c);scaled=b.copy()
  for col in ['open','high','low','close']:scaled[col]*=5
  s=make_signals(scaled,c)
  np.testing.assert_array_equal(a.side,s.side)
  np.testing.assert_allclose(a.atr*5,s.atr,rtol=1e-10,equal_nan=True)
  np.testing.assert_allclose(a.stop*5,s.stop,rtol=1e-10,equal_nan=True)
  clear_cache()

if __name__=='__main__':unittest.main()
