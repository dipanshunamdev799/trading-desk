from dataclasses import replace
import unittest
import numpy as np
import pandas as pd
from research.intraday_momentum_v2.strategy import Config,features,signals,distances,fill,run
from research.intraday_momentum_v2.capture import book_features,epoch,stale_instruments
from research.intraday_momentum_v2.resolution import replay

DAY='2025-01-02'
def at(t):return pd.Timestamp(DAY+' '+t,tz='Asia/Kolkata')
def record(key='A'):
    idx=pd.date_range(at('09:15'),at('15:10'),freq='5min')
    b=pd.DataFrame(dict(open=100.,high=100.2,low=99.8,close=100.,volume=100000.),index=idx)
    r=dict(key=key,symbol=key,day=DAY,bars=b,prev_close=98.,rvol=pd.Series(3.,index=idx),adv=1e9,sector='Test')
    r['_features']=features(r);return r
def sig(key='A',clock='09:35'):
    return dict(key=key,symbol=key,day=DAY,family='H1',variant='main',side=1,known_at=at(clock).isoformat(),
        index=int((at(clock)-pd.Timedelta(minutes=5)-at('09:15')).total_seconds()/300),raw_price=100.,score=1.,atr=.4,swing_stop=99.5)

class V2Tests(unittest.TestCase):
    def test_signal_prefix_invariance(self):
        r=record();b=r['bars'];b.loc[at('09:30'),['open','high','low','close']]=[100,101.1,99.9,101]
        market=dict(return_=np.zeros(len(b)))
        market={'return':np.zeros(len(b)),'lag_vol':.01}
        full=signals(r,market)
        k=8;short={**r,'bars':b.iloc[:k],'rvol':r['rvol'].iloc[:k]}
        prefix=signals(short,{'return':market['return'][:k],'lag_vol':.01})
        before=[s for s in full if pd.Timestamp(s['known_at'])<=b.index[k-1]+pd.Timedelta(minutes=5)]
        self.assertEqual(prefix,before)
        self.assertTrue(any(s['family']=='H1' for s in before))

    def test_efficiency_bounded_and_no_future_bar_changes_past_features(self):
        r=record();b=r['bars'];b.loc[at('09:15'),['open','high','low','close']]=[99,100.2,98.8,100]
        before=features(r);b.loc[at('13:00'): ,['open','high','low','close']]*=2
        after=features(r)
        self.assertTrue((before['efficiency']<=1+1e-12).all())
        for key in ('vwap','atr','ph','pl','vm','efficiency'):
            np.testing.assert_allclose(before[key][:20],after[key][:20],equal_nan=True)

    def test_structure_stop_bounds_and_atr_are_not_optimized_clamps(self):
        s=sig();self.assertIsNotNone(distances(s,Config('H1','S')))
        self.assertIsNone(distances({**s,'swing_stop':90.},Config('H1','S')))
        self.assertIsNone(distances({**s,'atr':.01},Config('H1','A')))

    def test_next_open_and_stop_first(self):
        r=record();r['bars'].loc[at('09:35'),['high','low']]=[102.,98.]
        r['_features']=features(r)
        t,tag=fill(r,sig(),10,Config('H1',slippage_bps=0),(.005,.01,60),1e6,5000)
        self.assertEqual(tag,'filled');self.assertEqual(t['entry_at'],at('09:35').isoformat())
        self.assertEqual(t['exit_price'],99.5);self.assertTrue(t['ambiguous'])

    def test_trailing_update_does_not_apply_to_earlier_low_in_same_bar(self):
        r=record();b=r['bars'];b.loc[at('09:35'),['open','high','low','close']]=[100.,101.5,99.7,101.]
        b.loc[at('09:40'),['open','high','low','close']]=[100.4,100.5,100.3,100.4]
        r['_features']=features(r);r['_features']['atr']=np.full(len(b),.2)
        t,_=fill(r,sig(),10,Config('H1','A',slippage_bps=0),(.006,.02,120),1e6,5000)
        self.assertEqual(t['exit_bar_at'],at('09:40').isoformat())
        self.assertEqual(t['exit_price'],100.4)

    def test_missing_exit_fails_entire_configuration(self):
        r=record();r['bars']=r['bars'].drop(at('10:35'));r['_features']=features(r)
        with self.assertRaisesRegex(ValueError,'Missing scheduled'):
            fill(r,sig(),10,Config('H1'),(.005,.01,60),1e6,5000)

    def test_cash_guard_precedes_missing_future_exit(self):
        r=record();r['bars']=r['bars'].drop(at('10:35'));r['_features']=features(r)
        t,tag=fill(r,sig(),10000,Config('H1',slippage_bps=0),(.005,.01,60),100.,5000)
        self.assertIsNone(t);self.assertEqual(tag,'entry_cash_or_risk')

    def test_flat_future_entry_does_not_cancel_eligible_order(self):
        r=record();r['bars'].loc[at('09:35'),['open','high','low','close']]=100.;r['_features']=features(r)
        self.assertEqual(fill(r,sig(),10,Config('H1'),(.005,.01,60),1e6,5000)[1],'filled')

    def test_portfolio_shared_cap_nonoverlap_and_cash_reconcile(self):
        records=[record(k) for k in 'ABCDE'];ss=[sig('A'),sig('B'),sig('C','10:35'),sig('D','11:35'),sig('E','12:35')]
        result=run(records,ss,[DAY],Config('H1',slippage_bps=0))
        self.assertEqual(len(result['trades']),3)
        self.assertEqual([t['symbol'] for t in result['trades']],['A','C','D'])
        self.assertAlmostEqual(result['daily'][-1]['equity'],1e6+sum(t['net_pnl'] for t in result['trades']))
        self.assertEqual([x['status'] for x in result['rejections']].count('position_open'),1)

    def test_short_tax_sides_and_reserved_collateral(self):
        r=record();s={**sig(),'side':-1};cfg=Config('H1',direction=-1)
        t,_=fill(r,s,10,cfg,(.005,.01,60),1e6,5000)
        self.assertGreater(t['entry_fee_components']['stt'],0)
        self.assertEqual(t['exit_fee_components']['stt'],0)
        self.assertGreater(t['exit_fee_components']['stamp'],0)
        self.assertAlmostEqual(t['net_pnl'],t['gross_pnl']-t['fees'])

    def test_future_entry_volume_does_not_resize(self):
        a=record();b=record();b['bars'].loc[at('09:35'),'volume']=100
        left=run([a],[sig()],[DAY],Config('H1'))['trades'][0]
        right=run([b],[sig()],[DAY],Config('H1'))['trades'][0]
        self.assertEqual(left['quantity'],right['quantity'])
        self.assertGreater(right['entry_bar_participation'],.01)

    def test_momentum_failure_uses_next_open(self):
        r=record();r['_features']['vwap']=np.full(len(r['bars']),101.)
        r['_features']['change3']=np.full(len(r['bars']),-.001)
        r['bars'].loc[at('09:40'),'open']=99.9
        t,_=fill(r,sig(),10,Config('H1','S',slippage_bps=0),(.01,.02,90),1e6,5000)
        self.assertEqual(t['reason'],'MOMENTUM_FAILURE')
        self.assertEqual(t['exit_bar_at'],at('09:40').isoformat())
        self.assertEqual(t['exit_price'],99.9)

    def test_later_candidates_do_not_change_earlier_cashflow(self):
        records=[record(k) for k in 'ABC'];ss=[sig('A'),sig('B','10:35')]
        before=run(records,ss,[DAY],Config('H1'))
        after=run(records,ss+[sig('C','12:35')],[DAY],Config('H1'))
        self.assertEqual(before['trades'],after['trades'][:2])

    def test_quote_metrics_are_displayed_depth_not_executed_flow(self):
        received=at('10:00').to_pydatetime();ms=int(received.timestamp()*1000)
        f=book_features({'fullFeed':{'marketFF':{'ltpc':{'ltp':100,'ltt':ms-60000,'ltq':10},
            'marketLevel':{'bidAskQuote':[{'bidP':99.9,'bidQ':300,'askP':100.1,'askQ':100}]},'vtt':1000}}},received,ms)
        self.assertAlmostEqual(f['spread_bps'],20.)
        self.assertAlmostEqual(f['depth_imbalance'],.5)
        self.assertFalse(f['feed_stale']);self.assertTrue(f['trade_stale'])
        self.assertNotIn('aggressive_buy_volume',f)

    def test_unknown_or_future_quote_time_not_fresh(self):
        received=at('10:00').to_pydatetime();f=book_features({},received,None)
        self.assertTrue(f['feed_stale']);self.assertIsNone(f['spread_bps'])
        self.assertIsNone(epoch('bad'))

    def test_per_instrument_gaps_visible_when_other_keys_are_active(self):
        missing=stale_instruments({'A','B','C'},{'A':99,'B':70},100)
        self.assertEqual([x['key'] for x in missing],['B','C'])
        self.assertEqual(missing[0]['seconds_since_received'],30)
        self.assertIsNone(missing[1]['seconds_since_received'])

    def test_one_minute_replay_resolves_five_minute_dual_touch(self):
        r=record();r['bars'].loc[at('09:35'),['high','low']]=[102,98];r['_features']=features(r)
        cfg=Config('H1',slippage_bps=0);t,_=fill(r,sig(),10,cfg,(.005,.01,60),1e6,5000)
        ix=pd.date_range(at('09:35'),at('10:35'),freq='min')
        b=pd.DataFrame(dict(open=100.,high=100.1,low=99.9,close=100.,volume=10000.),index=ix)
        b.loc[at('09:35'),'high']=101.1
        audit=replay(t,r,b,cfg)
        self.assertEqual(audit['status'],'matched');self.assertEqual(audit['reason_1minute'],'TARGET')
        self.assertGreater(audit['net_pnl_difference'],0)

if __name__=='__main__':unittest.main()
