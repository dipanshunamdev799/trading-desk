import unittest
import pandas as pd
from research.intraday_momentum.data import _regular_frames,_validated_rows


def rows(count=75):
    ix=pd.date_range('2025-01-02 09:15',periods=count,freq='5min',tz='Asia/Kolkata')
    return [(t.to_pydatetime(),100,101,99,100,10000) for t in ix]


class DataTests(unittest.TestCase):
    def test_closing_auction_tail_not_required_for_morning_study(self):
        full,_=_regular_frames(rows());prefix,_=_regular_frames(rows(72))
        pd.testing.assert_frame_equal(full['2025-01-02'],prefix['2025-01-02'])
        self.assertEqual(len(prefix['2025-01-02']),72)

    def test_missing_or_duplicate_morning_bar_is_not_filled(self):
        for bad in (rows()[:2]+rows()[3:],rows()+[rows()[3]]):
            frames,reasons=_regular_frames(bad)
            self.assertFalse(frames);self.assertEqual(sum(reasons.values()),1)

    def test_raw_payload_validation_never_adjusts_source_units(self):
        payload={'candles':[['2025-01-02T09:15:00+05:30',100,101,99,100,2000,0]]}
        data,dupes=_validated_rows(payload,'KEY','5minute','2025-01-02','2025-01-02')
        self.assertEqual(data[0][3:9],(100.,101.,99.,100.,2000.,0.))
        self.assertEqual(data[0][-1],'upstox');self.assertEqual(dupes,0)

    def test_conflicting_source_duplicate_cannot_be_imported(self):
        a=['2025-01-02T09:15:00+05:30',100,101,99,100,2000,0]
        b=[*a];b[4]=100.5
        with self.assertRaisesRegex(ValueError,'Conflicting source duplicate'):
            _validated_rows({'candles':[a,b]},'KEY','5minute','2025-01-02','2025-01-02')


if __name__=='__main__':unittest.main()
