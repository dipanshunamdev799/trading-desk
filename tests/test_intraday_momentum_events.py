import copy
import unittest

import numpy as np
import pandas as pd

from research.intraday_momentum.events import make_events,summarize_events


def record(key='ABC',side=1):
    index=pd.date_range('2025-01-06 09:15',periods=75,freq='5min',tz='Asia/Kolkata')
    price=108. if side>0 else 92.
    bars=pd.DataFrame(dict(open=price,high=price+.1,low=price-.1,close=price,volume=10000.),index=index)
    return dict(bars=bars,prev_close=100.,rvol=pd.Series(2.,index=index),key=key,day='2025-01-06',symbol=key)


def event(rows,threshold=.08,horizon='60min',direction='up'):
    return next(r for r in rows if r['threshold']==threshold and r['horizon']==horizon and r['direction']==direction)


def bar(rec,clock,**changes):
    at=pd.Timestamp('2025-01-06 '+clock,tz='Asia/Kolkata')
    for k,v in changes.items():rec['bars'].loc[at,k]=v


class Events(unittest.TestCase):
    def test_gapper_first_eligible_clock_and_two_horizons(self):
        r=record();rows=make_events([r]);e=event(rows)
        self.assertEqual(e['known_at'],'2025-01-06T09:30:00+05:30')
        self.assertEqual(e['entry_at'],e['known_at']);self.assertEqual(e['entry_price'],108)
        self.assertEqual(e['outcome'],'neither');self.assertEqual(len(rows),2)

    def test_overshooting_entry_is_excluded_from_race(self):
        r=record();bar(r,'09:30',open=111,high=111.2,low=110.8,close=111)
        e=event(make_events([r]));self.assertEqual(e['outcome'],'already_at_extension')
        self.assertFalse(e['race_eligible']);self.assertTrue(e['entry_already_at_extension'])

    def test_ambiguous_first_touch_counts_reversal_first(self):
        r=record();bar(r,'09:35',high=111,low=106)
        e=event(make_events([r]));self.assertEqual(e['outcome'],'reversal_first')
        self.assertEqual(e['ambiguous_count'],1)

    def test_opening_gap_resolves_before_later_ambiguous_extremes(self):
        r=record();bar(r,'09:35',open=106,high=111,low=105.8,close=108)
        e=event(make_events([r]));self.assertEqual(e['outcome'],'reversal_first')
        self.assertEqual(e['ambiguous_count'],0);self.assertEqual(e['touch_known_at'],'2025-01-06T09:35:00+05:30')

    def test_two_daily_percentage_points_are_not_one_percent_entry_gain(self):
        r=record();bar(r,'09:30',open=109.5,high=110.1,low=109.4,close=109.6)
        e=event(make_events([r]));self.assertAlmostEqual(e['target_price'],110)
        self.assertLess(e['target_price'],e['entry_price']*1.01)
        self.assertEqual(e['outcome'],'extension_first')

    def test_negative_mover_is_symmetric(self):
        r=record(side=-1);bar(r,'09:35',low=89.9)
        e=event(make_events([r]),direction='down')
        self.assertEqual(e['target_price'],90);self.assertAlmostEqual(e['reversal_price'],92.92)
        self.assertEqual(e['outcome'],'extension_first')

    def test_exact_decimal_threshold_touch_counts_despite_float_rounding(self):
        r=record();bar(r,'09:35',high=110.)
        self.assertEqual(event(make_events([r]))['outcome'],'extension_first')
        r=record(side=-1);bar(r,'09:35',low=90.)
        self.assertEqual(event(make_events([r]),direction='down')['outcome'],'extension_first')

    def test_later_extension_is_not_in_first_sixty_minutes(self):
        r=record();bar(r,'10:40',high=110.1)
        rows=make_events([r]);self.assertEqual(event(rows)['outcome'],'neither')
        self.assertEqual(event(rows,horizon='15:10')['outcome'],'extension_first')

    def test_endpoint_bar_future_extreme_is_not_inside_horizon(self):
        r=record();bar(r,'10:30',high=111)
        rows=make_events([r]);self.assertEqual(event(rows)['outcome'],'neither')
        self.assertEqual(event(rows,horizon='15:10')['outcome'],'extension_first')
        r=record();bar(r,'15:10',high=111)
        self.assertEqual(event(make_events([r]),horizon='15:10')['outcome'],'neither')

    def test_endpoint_future_quality_cannot_censor_an_observed_endpoint_open(self):
        r=record();bar(r,'10:30',high=np.nan,low=np.nan,close=np.nan,volume=np.nan)
        self.assertEqual(event(make_events([r]))['outcome'],'neither')

    def test_qualification_bar_high_does_not_count_as_post_entry_extension(self):
        r=record();bar(r,'09:25',high=112)
        self.assertEqual(event(make_events([r]))['outcome'],'neither')

    def test_future_path_mutation_cannot_move_qualification_or_entry(self):
        a=record();before=event(make_events([a]));b=copy.deepcopy(a);bar(b,'10:00',high=112,low=105)
        after=event(make_events([b]))
        for k in ('known_at','entry_at','entry_price','raw_signal_price','rvol','move'):
            self.assertEqual(before[k],after[k])
        self.assertNotEqual(before['outcome'],after['outcome'])

    def test_rvol_must_be_available_at_qualification(self):
        r=record();r['rvol'][:3]=np.nan
        self.assertEqual(event(make_events([r]))['known_at'],'2025-01-06T09:35:00+05:30')
        r['rvol'][:]=1.4;self.assertFalse(make_events([r]))

    def test_missing_path_is_censored_and_missing_entry_is_separate(self):
        r=record();r['bars']=r['bars'].drop(pd.Timestamp('2025-01-06 10:00',tz='Asia/Kolkata'))
        self.assertEqual(event(make_events([r]))['outcome'],'censored')
        r=record();r['bars']=r['bars'].iloc[:3]
        self.assertEqual(event(make_events([r]))['outcome'],'missing_next_open')

    def test_summary_denominator_discloses_overshoots(self):
        a=record('A');bar(a,'09:35',high=111)
        b=record('B');bar(b,'09:30',open=111,high=111.2,low=110.8,close=111)
        c=record('C')
        summary=summarize_events(make_events([a,b,c]))
        g=next(x for x in summary['groups'] if x['threshold']==.08 and x['horizon']=='60min' and x['direction']=='up')
        self.assertEqual(g['qualifications'],3);self.assertEqual(g['race_count'],2)
        self.assertEqual(g['already_at_extension'],1);self.assertEqual(g['extension_rate'],.5)
        self.assertEqual(g['neither_rate'],.5)


if __name__=='__main__':unittest.main()
