"""Independent failure-case regression checks; fixtures do not count as market evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import alpha_signal_engine as signal
import research_alpha_metrics as account


class SignalFailureCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candles=[r for r in json.loads((ROOT/'artifacts'/'directional_research'/'nifty-upstox-5minute.json').read_text()) if r['ts'][:10]>='2026-11-01']

    def assert_abstention(self,result):
        self.assertEqual(result['action'],'NO TRADE')
        self.assertIsNone(result['candidate_action'])
        self.assertFalse(result['broker_order_sent'])

    def test_empty_feed(self):
        self.assert_abstention(signal.evaluate([],'2026-11-06T13:05:00+05:30','NORMAL_OPEN'))

    def test_missing_timestamp(self):
        self.assert_abstention(signal.evaluate([{'open':100,'high':101,'low':99,'close':100}],'2026-11-06T13:05:00+05:30','NORMAL_OPEN'))

    def test_last_valid_research_candidate_never_places_order(self):
        result=signal.evaluate(self.candles,'2026-11-06T14:10:00+05:30','NORMAL_OPEN')
        self.assertEqual(result['action'],'NO TRADE')
        self.assertEqual(result['candidate_action'],'BUY CE')
        self.assertFalse(result['broker_order_sent'])

    def test_delayed_entry_cannot_exit_after_cutoff(self):
        self.assert_abstention(signal.evaluate(self.candles,'2026-11-06T14:10:30+05:30','NORMAL_OPEN'))

    def test_closed_market(self):
        self.assert_abstention(signal.evaluate(self.candles,'2026-11-06T14:10:00+05:30','CLOSING_END'))

    def test_stale_signal_bar(self):
        self.assert_abstention(signal.evaluate(self.candles,'2026-11-06T14:12:00+05:30','NORMAL_OPEN'))

    def test_timestamp_alignment(self):
        shifted=copy.deepcopy(self.candles)
        for row in shifted:row['ts']=(pd.Timestamp(row['ts'])+pd.Timedelta(seconds=30)).isoformat()
        self.assert_abstention(signal.evaluate(shifted,'2026-11-06T13:05:30+05:30','NORMAL_OPEN'))

    def test_conflicting_duplicate(self):
        data=copy.deepcopy(self.candles)
        row=copy.deepcopy(next(r for r in data if r['ts'].startswith('2026-11-06T14:05:00')))
        row['close']+=.1;row['high']=max(row['high'],row['close'])
        data.append(row)
        self.assert_abstention(signal.evaluate(data,'2026-11-06T14:10:00+05:30','NORMAL_OPEN'))

    def test_future_prices_never_enter_features(self):
        before=signal.evaluate(self.candles,'2026-11-06T14:10:00+05:30','NORMAL_OPEN')
        data=copy.deepcopy(self.candles)
        for r in data:
            if pd.Timestamp(r['ts'])>=pd.Timestamp('2026-11-06T14:10:00+05:30'):
                r.update(open=1e8,high=1e8,low=1e8,close=1e8)
        after=signal.evaluate(data,'2026-11-06T14:10:00+05:30','NORMAL_OPEN')
        self.assertEqual(before,after)


class AccountFailureCases(unittest.TestCase):
    def test_remaining_daily_planned_risk(self):
        rows=[]
        for entry,exit in [('13:05','13:20'),('13:30','13:45'),('14:00','14:15')]:
            rows.append({'entry_at':f'2026-11-02T{entry}:00+05:30','exit_at':f'2026-11-02T{exit}:00+05:30',
                'premium_entry':100,'lot':65,'planned_stop_loss_rupees':500,'severe_net_rupees_per_lot':-900})
        outcomes,skips=account.simulate(pd.DataFrame(rows),250000,.005)
        self.assertEqual(len(outcomes),2)
        self.assertEqual(sum(r['net'] for r in outcomes),-1800)
        self.assertTrue(skips)

    def test_cash_funds_full_execution_reserve(self):
        # One adverse but within-full-premium loss each week. The last candidate has
        # INR6750cash: enough for premium+200 but not premium+525severe reserve.
        rows=[]
        for i in range(36):
            entry=pd.Timestamp('2025-01-06T13:05:00+05:30')+pd.Timedelta(days=7*i)
            rows.append({'entry_at':entry.isoformat(),'exit_at':(entry+pd.Timedelta(minutes=30)).isoformat(),
                'premium_entry':100,'lot':65,'planned_stop_loss_rupees':500,'severe_net_rupees_per_lot':-6950})
        outcomes,_=account.simulate(pd.DataFrame(rows),250000,.005)
        self.assertEqual(len(outcomes),35)
        self.assertEqual(outcomes[-1]['equity'],6750)


if __name__=='__main__':unittest.main()
