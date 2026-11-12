"""Synthetic regression fixtures only; none is counted as a market outcome."""
from datetime import datetime,timedelta,timezone
import unittest
from alpha_event_engine import ExitPolicy,candle_replay,quote_fill,quote_exit
from research_alpha_streams import parse_quotes,replay

IST=timezone(timedelta(hours=5,minutes=30))


class EngineChecks(unittest.TestCase):
    def setUp(self):
        self.at=datetime(2026,11,2,13,0,tzinfo=IST)
        self.trade={'entry_at':self.at.isoformat(),'direction':1,'lot':65,'signal_atr':10,'signal_spot':1000,'signal_structure_stop':985}
    def bars(self,rows):
        return {self.at+timedelta(minutes=5*i):dict(zip(['open','high','low','close','volume'],row)) for i,row in enumerate(rows)}
    def test_same_bar_path_bounds(self):
        bars=self.bars([[100,125,75,110,100]])
        p=ExitPolicy('bound',5,premium_stop=.2,target_r=1)
        a=candle_replay(self.trade,bars,{},p);b=candle_replay(self.trade,bars,{},p,'favorable_first')
        self.assertEqual(a['premium_exit'],80);self.assertEqual(b['premium_exit'],120)
        self.assertEqual(a['ambiguity_count'],1)
    def test_gap_stop_is_not_guaranteed_price(self):
        bars=self.bars([[100,110,95,105,100],[60,70,55,65,100]])
        result=candle_replay(self.trade,bars,{},ExitPolicy('gap',10,premium_stop=.2))
        self.assertEqual(result['premium_exit'],60);self.assertEqual(result['exit_at'],(self.at+timedelta(minutes=5)).isoformat())
    def test_underlying_trigger_waits_for_confirmation(self):
        bars=self.bars([[100,105,95,101,100],[90,95,85,92,100]])
        u=self.bars([[1000,1005,985,998,0],[998,1000,990,995,0]])
        result=candle_replay(self.trade,bars,u,ExitPolicy('underlying',10,underlying_atr=1))
        self.assertEqual(result['premium_exit'],90);self.assertEqual(result['exit_reason'],'underlying_stop_next_open')
    def test_trailing_uses_prior_close_not_current_high(self):
        bars=self.bars([[100,150,90,110,100],[110,115,100,105,100]])
        result=candle_replay(self.trade,bars,{},ExitPolicy('trail',10,premium_stop=.2,trailing_fraction=.2))
        self.assertEqual(result['exit_reason'],'time_exit');self.assertEqual(result['premium_exit'],105)
    def test_missing_and_zero_volume_remain_unresolved(self):
        bars=self.bars([[100,110,95,105,100]])
        result=candle_replay(self.trade,bars,{},ExitPolicy('missing',10))
        self.assertEqual(result['status'],'unsupported_missing_bar');self.assertTrue(result['unresolved_position'])
        bars=self.bars([[100,110,95,105,100],[105,110,100,107,0]])
        self.assertEqual(candle_replay(self.trade,bars,{},ExitPolicy('zero',10))['status'],'unsupported_zero_volume_bar')
    def test_session_cutoff_caps_long_hold(self):
        self.at=self.at.replace(hour=15);self.trade['entry_at']=self.at.isoformat()
        result=candle_replay(self.trade,self.bars([[100,110,95,105,100],[105,110,100,107,100]]),{},ExitPolicy('long',120))
        self.assertEqual(result['holding_minutes'],10);self.assertEqual(result['exit_reason'],'session_cutoff')
    def order(self):
        return {'known_at':self.at.isoformat(),'instrument_key':'SYNTHETIC|1','side':'BUY','quantity':130,'lot':65,'limit_price':102}
    def quote(self,offset=500,**changes):
        at=self.at+timedelta(milliseconds=offset)
        return {'instrument_key':'SYNTHETIC|1','received_at':at.isoformat(),'source_at':at.isoformat(),'book_timestamp_verified':True,'market_status':'NORMAL_OPEN','bid':100,'ask':101,'bid_qty':130,'ask_qty':130,**changes}
    def test_latency_limit_and_depth(self):
        quotes=[self.quote(100,ask=100),self.quote(500,ask=103)]
        self.assertEqual(quote_fill(self.order(),quotes)['status'],'MISSED')
        self.assertEqual(quote_fill(self.order(),[self.quote(500)])['price'],101)
    def test_partial_requires_explicit_accounting(self):
        q=self.quote(500,ask_qty=65)
        self.assertEqual(quote_fill(self.order(),[q])['status'],'MISSED')
        r=quote_fill(self.order(),[q],allow_partial=True)
        self.assertEqual(r['filled_quantity'],65);self.assertEqual(r['cancelled_quantity'],65);self.assertEqual(r['status'],'PARTIAL_CANCELLED_PROXY')
    def test_unverified_stale_future_and_wrong_market_rejected(self):
        for changes in [{'book_timestamp_verified':False},{'source_at':(self.at-timedelta(seconds=3)).isoformat()},
                        {'source_at':(self.at+timedelta(seconds=3)).isoformat()},{'market_status':'CLOSED'}]:
            self.assertEqual(quote_fill(self.order(),[self.quote(500,**changes)])['status'],'MISSED')
    def test_stop_bid_exit_respects_latency_and_gap(self):
        intent={**self.order(),'entry_at':self.at.isoformat(),'due_at':(self.at+timedelta(minutes=60)).isoformat()}
        r=quote_exit(intent,[self.quote(500,bid=79,ask=80),self.quote(1000,bid=60,ask=61)],stop_price=80)
        self.assertEqual(r['price'],60);self.assertEqual(r['stop_gap_per_unit'],20)
    def test_no_exit_quote_is_unresolved(self):
        intent={**self.order(),'entry_at':self.at.isoformat(),'due_at':(self.at+timedelta(minutes=60)).isoformat()}
        self.assertEqual(quote_exit(intent,[])['status'],'UNRESOLVED_NO_VALID_EXIT_QUOTE')
    def snapshot(self,seconds,bid=99.8,ask=100):
        received=self.at+timedelta(seconds=seconds);source=received+timedelta(milliseconds=100)
        return {'source_at':source.isoformat(),'received_at':received.isoformat(),'ltt':str(int((source-timedelta(milliseconds=100)).timestamp()*1000)),
                'bid':bid,'ask':ask,'bid_qty':65,'ask_qty':65,'book_timestamp_verified':False}
    def snapshot_row(self):
        return {'entry_at':self.at.isoformat(),'exit_at':(self.at+timedelta(minutes=60)).isoformat(),'lot':65}
    def test_snapshot_strict_mode_does_not_promote_frame_timestamp(self):
        q=parse_quotes([self.snapshot(-.5),self.snapshot(.5),self.snapshot(3599.5,bid=105,ask=105.5)])
        a=replay(self.snapshot_row(),q,'verified_exchange_book','time60',250,2000)
        b=replay(self.snapshot_row(),q,'frame_snapshot','time60',250,2000)
        self.assertEqual(a['status'],'rejected_no_valid_decision_quote')
        self.assertEqual(b['status'],'observed_bid_ask_snapshot_proxy');self.assertEqual(b['premium_exit'],105)
        self.assertLessEqual(datetime.fromisoformat(b['exit_at']),self.at+timedelta(minutes=60))
    def test_snapshot_limit_is_anchored_before_decision(self):
        q=parse_quotes([self.snapshot(-.5),self.snapshot(.5,bid=110,ask=110.5)])
        r=replay(self.snapshot_row(),q,'frame_snapshot','time60',250,2000)
        self.assertEqual(r['status'],'missed_entry')
    def test_snapshot_exit_gap_and_unresolved_are_explicit(self):
        q=parse_quotes([self.snapshot(-.5),self.snapshot(.5),self.snapshot(5,bid=79,ask=79.5),self.snapshot(5.5,bid=60,ask=60.5)])
        r=replay(self.snapshot_row(),q,'frame_snapshot','premium20',250,2000)
        self.assertEqual(r['premium_exit'],60);self.assertEqual(r['stop_gap_per_unit'],20)
        r=replay(self.snapshot_row(),q[:2],'frame_snapshot','time60',250,2000)
        self.assertEqual(r['status'],'unresolved_no_valid_exit_quote');self.assertNotIn('gross_rupees_per_lot',r)


if __name__=='__main__':unittest.main(verbosity=2)
