import unittest
import numpy as np
import pandas as pd
from research.swing_discovery.engine import simulate,fee_coeff

def panel(rows,split=None,div=None):
    a=np.asarray(rows,float);dates=pd.date_range('2025-01-01',periods=len(a),tz='Asia/Kolkata')
    actual={k:a[:,i][None,:] for i,k in enumerate(['open','high','low','close'])}
    actual['volume']=np.full((1,len(a)),1e6)
    return {'symbols':['ABC'],'dates':dates,'actual':actual,'neutral':actual,'unit_factor':np.ones((1,len(a))),
      'split_factor':np.asarray([split or [1]*len(a)]),'dividend':np.asarray([div or [0]*len(a)])}
def signal(p,entry=None,level=95):
    n=len(p['dates']);return {'entry':np.asarray([entry or [True]+[False]*(n-1)]),'atr':np.full((1,n),2.),'level':np.full((1,n),float(level))}
def run(p,s,**cfg):
    return simulate(p,s,{'initial_capital':10000,'risk_fraction':.01,'stop_mode':'level','buffer':0,**cfg},
      '2025-01-01','2025-02-01',cost_multiplier=0,slippage_bps=0,keep_trades=True)

class DiscoveryEngineTests(unittest.TestCase):
 def test_completed_day_executes_next_day_only(self):
    p=panel([[100,150,50,100],[100,101,99,100]])
    r=run(p,signal(p));self.assertEqual(len(r['trades']),1);self.assertEqual(r['trades'].iloc[0].entry_day,str(p['dates'][1]))
    self.assertEqual(r['trades'].iloc[0].net_pnl,0)
 def test_daily_ambiguity_stop_first(self):
    p=panel([[100,101,99,100],[100,115,94,110]])
    t=run(p,signal(p))['trades'].iloc[0];self.assertEqual(t.reason,'stop');self.assertAlmostEqual(t.net_r,-1)
 def test_gap_stop_worse_than_stop(self):
    p=panel([[100,101,99,100],[100,101,99,100],[90,91,89,90]])
    t=run(p,signal(p))['trades'].iloc[0];self.assertEqual(t.reason,'gap_stop');self.assertAlmostEqual(t.net_r,-2)
 def test_target_gets_no_favorable_gap_improvement(self):
    p=panel([[100,101,99,100],[100,101,99,100],[120,121,119,120]])
    t=run(p,signal(p))['trades'].iloc[0];self.assertEqual(t.exit,110);self.assertAlmostEqual(t.net_r,2)
 def test_cash_and_fee_inclusive_risk(self):
    p=panel([[100,101,99,100],[100,101,99,100],[100,200,99,190]])
    r=simulate(p,signal(p),{'initial_capital':10000,'risk_fraction':.01,'stop_mode':'level','buffer':0},
      '2025-01-01','2025-02-01',keep_trades=True)
    t=r['trades'].iloc[0];self.assertLessEqual(t.initial_cash_risk,100+1e-8)
    self.assertAlmostEqual(r['equity'].iloc[-1],10000+t.net_pnl)
    self.assertGreater(t.fees,0);self.assertAlmostEqual(t.net_r,2,places=5)
 def test_split_not_false_price_loss(self):
    p=panel([[100,101,99,100],[100,101,99,100],[50,56,49,55]],split=[1,1,2]);p['unit_factor']=np.asarray([[2.,2.,1.]])
    # Neutral historical share units: signal support47.5, ATR1.
    s=signal(p,level=47.5);s['atr'][:]=1
    t=run(p,s)['trades'].iloc[0];self.assertEqual(t.quantity,40);self.assertAlmostEqual(t.net_r,2)
 def test_dividend_entitlement_in_economic_return(self):
    p=panel([[100,101,99,100],[100,101,99,100],[95,96,94,95]],div=[0,0,5])
    t=run(p,signal(p,level=90))['trades'].iloc[0];self.assertEqual(t.dividends,50);self.assertAlmostEqual(t.net_pnl,0)
 def test_lagged_participation_cap(self):
    p=panel([[100,101,99,100],[100,101,99,100]]);p['median_volume20']=np.full((1,2),100.)
    t=run(p,signal(p))['trades'].iloc[0];self.assertEqual(t.quantity,1)
 def test_no_prior_split_signal_leak(self):
    p=panel([[100,101,99,100],[100,101,99,100]])
    r=simulate(p,signal(p),{},'2025-01-02','2025-02-01',keep_trades=True)
    self.assertTrue(r['trades'].empty)
 def test_fee_schedule_matches_frozen_stock_engine(self):
    from research.swing.stock_engine import transaction_cost
    for day in ['2025-01-01','2026-03-02']:
      for buy in [True,False]:
       rate,fixed=fee_coeff(day,buy,True)
       self.assertAlmostEqual(rate*100000+fixed,transaction_cost(100,1000,'buy' if buy else 'sell',day,'equity_delivery',True))

if __name__=='__main__':unittest.main()
