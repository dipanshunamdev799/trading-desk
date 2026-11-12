import unittest
import numpy as np
import pandas as pd
from research.swing_diagnosis.portfolio import simulate_portfolio

def fixture(n=20):
    days=pd.date_range('2025-01-01',periods=4,tz='Asia/Kolkata');a=np.full((n,4),100.)
    actual={'open':a.copy(),'high':a+1,'low':a-1,'close':a.copy(),'volume':a*1e6}
    p=dict(dates=days,symbols=[f'S{i:02}' for i in range(n)],sector=[f'sector{i%5}' for i in range(n)],eligible=np.ones(n,bool),
      actual=actual,neutral=actual,unit_factor=np.ones_like(a),split_factor=np.ones_like(a),dividend=np.zeros_like(a),
      liquidity_turnover=np.full_like(a,1e9),liquidity_volume=np.full_like(a,1e6))
    sig=dict(entry=np.zeros_like(a,dtype=bool),atr=np.full_like(a,2.));sig['entry'][:,0]=True
    return p,sig

class FundedPortfolioTests(unittest.TestCase):
    def test_shared_cash_position_cap_and_terminal_reconciliation(self):
        p,s=fixture();m,d,t=simulate_portfolio(p,s,{},'2025-01-01','2025-01-05','equal',0,0)
        self.assertEqual(m['max_positions'],10);self.assertGreaterEqual(d.cash.min(),0)
        self.assertAlmostEqual(d.equity.iloc[-1],1e6+t.net_pnl.sum())
        self.assertEqual(t.entry_quantity.sum(),10000)
        self.assertTrue((pd.to_datetime(t.entry_day)>pd.to_datetime(t.signal_day)).all())
    def test_sector_limit_restricts_shared_account(self):
        p,s=fixture();p['sector']=['one']*20
        m,d,t=simulate_portfolio(p,s,{},'2025-01-01','2025-01-05','equal',0,0)
        self.assertEqual(m['max_positions'],3);self.assertEqual(t.entry_quantity.sum(),3000)
    def test_gap_stops_and_fees_reconcile_real_cash(self):
        p,s=fixture(1);p['actual']['open'][0,2]=90;p['actual']['high'][0,2]=91;p['actual']['low'][0,2]=89;p['actual']['close'][0,2]=90
        m,d,t=simulate_portfolio(p,s,{},'2025-01-01','2025-01-05','risk',5,1)
        self.assertEqual(t.iloc[0].reason,'gap_stop');self.assertLess(t.iloc[0].net_r,-1)
        self.assertLessEqual(m['max_entry_risk_fraction'],.005)
        self.assertAlmostEqual(d.equity.iloc[-1],1e6+t.net_pnl.sum())
    def test_split_and_dividend_preserve_economic_cash(self):
        p,s=fixture(1)
        for k in ['open','high','low','close']:p['actual'][k][0,2:]/=2
        p['split_factor'][0,2]=2;p['unit_factor'][0,:2]=2;p['dividend'][0,2]=1
        m,d,t=simulate_portfolio(p,s,{},'2025-01-01','2025-01-05','equal',0,0)
        self.assertEqual(t.iloc[0].exit_quantity,2*t.iloc[0].entry_quantity)
        self.assertAlmostEqual(t.iloc[0].net_pnl,t.iloc[0].dividends)
        self.assertAlmostEqual(d.equity.iloc[-1],1e6+t.net_pnl.sum())

if __name__=='__main__':unittest.main()
