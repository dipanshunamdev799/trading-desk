"""Controlled regressions for the new audit-only correction, not trading advice."""
import unittest
import numpy as np
import pandas as pd
from research.swing_discovery.engine import simulate as original
from research.swing_diagnosis.audit_engine import simulate,intraday_refund
from research.swing_discovery.data import events_for

def fixture(stop=True):
    rows=[[100,101,99,100],[100,101,90 if stop else 99,100],[100,101,99,100]]
    a=np.asarray(rows,float);bars={k:a[:,i][None,:] for i,k in enumerate(['open','high','low','close'])}
    p=dict(symbols=['ABC'],dates=pd.date_range('2025-01-01',periods=3,tz='Asia/Kolkata'),actual=bars,neutral=bars)
    s=dict(entry=np.array([[True,False,False]]),atr=np.full((1,3),2.))
    cfg=dict(initial_capital=1e6,risk_fraction=.005,stop_atr=2,max_hold_sessions=10,exit='fixed')
    return p,s,cfg

class AuditCorrections(unittest.TestCase):
    def test_same_day_refunds_only_actual_taxes(self):
        p,s,c=fixture();kw=dict(start='2025-01-01',end='2025-02-01',slippage_bps=5,keep_trades=True)
        a=original(p,s,c,**kw);b=simulate(p,s,c,**kw);x=a['trades'].iloc[0];y=b['trades'].iloc[0]
        saving=float(intraday_refund(x.entry_day,x.entry_fill*x.entry_quantity,x.exit*x.quantity))
        self.assertAlmostEqual(y.net_pnl-x.net_pnl,saving)
        self.assertAlmostEqual(x.fees-y.fees,saving)
        self.assertEqual(x.initial_cash_risk,y.initial_cash_risk)
        self.assertEqual(x.target,y.target);self.assertEqual(x.entry_quantity,y.entry_quantity)
        self.assertAlmostEqual(b['equity'].iloc[-1],1e6+y.net_pnl)

    def test_overnight_path_has_identical_fees(self):
        p,s,c=fixture(False);kw=dict(start='2025-01-01',end='2025-02-01',slippage_bps=5,keep_trades=True)
        a=original(p,s,c,**kw);b=simulate(p,s,c,**kw)
        np.testing.assert_allclose(a['equity'],b['equity'])
        self.assertEqual(a['trades'].iloc[0].fees,b['trades'].iloc[0].fees)

    def test_zero_cost_has_no_refund(self):
        p,s,c=fixture();kw=dict(start='2025-01-01',end='2025-02-01',cost_multiplier=0,slippage_bps=5,keep_trades=True)
        a=original(p,s,c,**kw);b=simulate(p,s,c,**kw)
        np.testing.assert_allclose(a['equity'],b['equity'])

    def test_source_parser_reproduces_multicomponent_defect(self):
        spec=dict(symbol='ABC',current_symbol='ABC',isin_at_start='INEABC',instrument_key='NSE_EQ|INEABC')
        records=[dict(symbol='ABC',isin='INEABC',series='EQ',exDate='17-Jan-2025',subject='Interim Dividend - Rs 10 Per Share Special Dividend - Rs 66 Per Share')]
        event=events_for(spec,records)[0]
        self.assertEqual(event['dividend'],10.)
        correction=pd.read_csv('artifacts/swing_diagnosis/audit-dividend-corrections.csv')
        actual=correction[(correction.symbol=='TCS')&(correction.date=='2025-01-17')].iloc[0]
        self.assertEqual(actual.corrected,76.);self.assertEqual(actual.delta,66.)

    def test_weekly_release_delays_earliest_weekly_execution_one_session(self):
        from research.swing_discovery.signals import _weekly_averages
        dates=pd.bdate_range('2025-01-06',periods=9,tz='Asia/Kolkata')
        close=np.arange(1.,10.)[None,:]
        weekly,_=_weekly_averages(close,dates,1,1)
        self.assertTrue(np.isnan(weekly[0,4]))  # Friday completed close withheld.
        self.assertEqual(weekly[0,5],5.)  # Monday daily decision sees Friday.
        bars={k:np.full((1,9),100.) for k in ['open','high','low','close']}
        p=dict(symbols=['ABC'],dates=dates,actual=bars)
        original_timing=dict(entry=np.isfinite(weekly),atr=np.full((1,9),2.))
        earliest=dict(entry=np.array([[False]*4+[True]+[False]*4]),atr=np.full((1,9),2.))
        kw=dict(start='2025-01-06',end='2025-02-01',slippage_bps=0,cost_multiplier=0,keep_trades=True)
        actual=simulate(p,original_timing,{},**kw)['trades'].iloc[0]
        possible=simulate(p,earliest,{},**kw)['trades'].iloc[0]
        self.assertEqual(str(actual.entry_day)[:10],'2025-01-14')
        self.assertEqual(str(possible.entry_day)[:10],'2025-01-13')

if __name__=='__main__':unittest.main()
