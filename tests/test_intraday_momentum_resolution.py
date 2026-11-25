import unittest
import pandas as pd
from research.intraday_momentum.resolution import replay


class ResolutionTests(unittest.TestCase):
    def setUp(self):
        ix=pd.date_range('2025-01-02 09:30',periods=61,freq='min',tz='Asia/Kolkata')
        self.bars=pd.DataFrame(dict(open=100.,high=100.1,low=99.9,close=100.,volume=10000),index=ix)
        self.trade=dict(entry_at=ix[0].isoformat(),side='LONG',raw_entry_price=100.,entry_price=100.,quantity=10,
                        stop_price=99.5,target_price=101.,entry_fee_components={'total':0.},net_pnl=-5.)

    def test_earlier_minute_target_resolves_five_minute_ambiguity(self):
        self.bars.iloc[1,self.bars.columns.get_loc('high')]=101.2
        self.bars.iloc[3,self.bars.columns.get_loc('low')]=99.4
        r=replay(self.trade,self.bars,slippage_bps=0)
        self.assertEqual(r['reason_1minute'],'TARGET');self.assertEqual(r['exit_price_1minute'],101.)

    def test_true_one_minute_ambiguity_still_stops_first(self):
        self.bars.iloc[1,self.bars.columns.get_indexer(['high','low'])]=[101.2,99.4]
        r=replay(self.trade,self.bars,slippage_bps=0)
        self.assertEqual(r['reason_1minute'],'STOP_FIRST_AMBIGUOUS')
        self.assertEqual(r['exit_price_1minute'],99.5)

    def test_entry_mismatch_or_missing_path_not_synthetic_fill(self):
        b=self.bars.copy();b.iloc[0,b.columns.get_loc('open')]=102.
        self.assertEqual(replay(self.trade,b)['status'],'entry_open_mismatch')
        self.assertEqual(replay(self.trade,self.bars.drop(self.bars.index[1]))['status'],'missing_path_minute')

    def test_due_bar_future_high_low_cannot_change_time_exit(self):
        before=replay(self.trade,self.bars,slippage_bps=0)
        self.bars.iloc[-1,self.bars.columns.get_indexer(['high','low'])]=[110.,90.]
        after=replay(self.trade,self.bars,slippage_bps=0)
        self.assertEqual(before,after);self.assertEqual(after['reason_1minute'],'TIME_EXIT')


if __name__=='__main__':unittest.main()
