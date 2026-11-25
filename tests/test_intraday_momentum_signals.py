import unittest

import numpy as np
import pandas as pd

from research.intraday_momentum.signals import make_signals, MECHANISMS


def frame(closes, opens=None, lows=None, highs=None, volumes=None, start='2025-01-06 09:15'):
    c=np.asarray(closes,dtype=float);o=np.asarray(opens,dtype=float) if opens is not None else c-.2
    return pd.DataFrame(dict(open=o,close=c,high=np.maximum(o,c)+.1 if highs is None else highs,
        low=np.minimum(o,c)-.1 if lows is None else lows,volume=np.full(len(c),10000.) if volumes is None else volumes),
        index=pd.date_range(start,periods=len(c),freq='5min',tz='Asia/Kolkata'))


class Signals(unittest.TestCase):
    def rv(self,b,ratio=2.):return pd.Series(ratio,index=b.index)
    def rows(self,b,mechanism,rv=None,**kw):
        return [r for r in make_signals(b,100,self.rv(b) if rv is None else rv,**kw) if r['mechanism']==mechanism]

    def test_first_eligible_morning_qualification_includes_existing_gap(self):
        b=frame([109,109.2,109.4,109.6,109.8])
        rows=self.rows(b,'cross8')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['known_at'],pd.Timestamp('2025-01-06 09:30',tz='Asia/Kolkata'))
        self.assertEqual(rows[0]['raw_price'],109.4)
        self.assertEqual(rows[0]['side'],1)

    def test_volume_gate_off_keeps_finite_rvol_requirement(self):
        b=frame([109,109.2,109.4,109.6])
        self.assertFalse(self.rows(b,'cross8',self.rv(b,1.)))
        row=self.rows(b,'cross8_no_volume',self.rv(b,1.))[0]
        self.assertAlmostEqual(row['score'],abs(row['move']))
        self.assertFalse(self.rows(b,'cross8_no_volume',self.rv(b,np.nan)))

    def test_next_bar_knowledge_and_unfinished_bar_cutoff(self):
        b=frame([100,101,109,111])
        self.assertFalse(make_signals(b,100,self.rv(b),as_of=pd.Timestamp('2025-01-06 09:29:59',tz='Asia/Kolkata')))
        rows=make_signals(b,100,self.rv(b),as_of=pd.Timestamp('2025-01-06 09:30',tz='Asia/Kolkata'))
        self.assertTrue(rows);self.assertTrue(all(r['known_at']<=pd.Timestamp('2025-01-06 09:30',tz='Asia/Kolkata') for r in rows))

    def test_prefix_invariance_and_future_mutation(self):
        b=frame([100,104,109,111,109,112,113,114])
        full=make_signals(b,100,self.rv(b))
        for n in range(1,len(b)+1):
            known=b.index[n-1]+pd.Timedelta(minutes=5)
            expected=[r for r in full if r['known_at']<=known]
            self.assertEqual(make_signals(b.iloc[:n],100,self.rv(b).iloc[:n]),expected)
        changed=b.copy();changed.iloc[5:]=frame([180,70,200],start='2025-01-06 09:40').to_numpy()
        cutoff=b.index[4]+pd.Timedelta(minutes=5)
        self.assertEqual([r for r in full if r['known_at']<=cutoff],
                         [r for r in make_signals(changed,100,self.rv(b)) if r['known_at']<=cutoff])

    def test_breakout_uses_prior_highs_and_negative_direction_is_symmetric(self):
        b=frame([100,104,108,110])
        row=self.rows(b,'breakout8')[0]
        self.assertEqual(row['known_at'],pd.Timestamp('2025-01-06 09:35',tz='Asia/Kolkata'))
        short=frame([99,95,91,89],opens=[99.2,95.2,91.2,89.2])
        self.assertEqual(self.rows(short,'breakout8')[0]['side'],-1)

    def test_vwap_reclaim_uses_previous_bar_vwap(self):
        b=frame([112,108,110.5],opens=[111,110,108],lows=[110.9,107.9,107.8],highs=[112.1,110.1,112])
        rows=self.rows(b,'vwap_reclaim8')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['side'],1)

    def test_exhaustion_is_diagnostic_opposite_direction(self):
        b=frame([109,111,108.5],opens=[108,110,111],lows=[107.9,109.9,108.4],highs=[109.1,111.1,111.1])
        self.assertEqual(self.rows(b,'exhaustion8')[0]['side'],-1)

    def test_zero_volume_flat_bars_and_outside_window_have_no_signal(self):
        b=frame([109,109.2,109.4],volumes=[100,100,0])
        self.assertFalse(make_signals(b,100,self.rv(b)))
        b=frame([109,109.2,109.4],opens=[109,109.2,109.4],lows=[109,109.2,109.4],highs=[109,109.2,109.4])
        self.assertFalse(make_signals(b,100,self.rv(b)))
        b=frame([109,109.2,109.4],start='2025-01-06 11:30')
        self.assertFalse(make_signals(b,100,self.rv(b)))

    def test_validation_and_score_cap(self):
        b=frame([109,109.2,109.4])
        row=self.rows(b,'cross8',self.rv(b,100))[0]
        self.assertAlmostEqual(row['score'],abs(row['move'])*10)
        with self.assertRaises(ValueError):make_signals(b,0,self.rv(b))
        bad=b.copy();bad.index=bad.index.tz_localize(None)
        with self.assertRaises(ValueError):make_signals(bad,100,self.rv(b))
        self.assertEqual(set(MECHANISMS),{'cross8','cross10','breakout8','vwap_reclaim8','exhaustion8','cross8_no_volume'})


if __name__=='__main__':unittest.main()
