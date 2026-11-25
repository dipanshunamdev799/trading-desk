import unittest
import pandas as pd
import numpy as np
from research.intraday_momentum.units import (combined_events,factor_from_events,restore_bars,
    current_basis_prev_close,price_factor,UnitBasisError)


class UnitsTests(unittest.TestCase):
    def test_before_on_after_ex_date(self):
        events=[dict(key='K',day='2025-06-16',factor=10,classification='back_adjusted')]
        self.assertEqual(factor_from_events('K','2025-06-13',events),10)
        self.assertEqual(factor_from_events('K','2025-06-16',events),1)
        self.assertEqual(factor_from_events('K','2025-06-17',events),1)
        self.assertEqual(factor_from_events('OTHER','2025-06-13',events),1)

    def test_same_date_split_and_bonus_combine_and_duplicates_do_not(self):
        specs=[dict(symbol='ABC',current_symbol='ABC',instrument_key='K')]
        rows=[dict(symbol='ABC',series='EQ',exDate='16-Jun-2025',subject='Face Value Split - From Rs 2/- To Re 1/-'),
              dict(symbol='ABC',series='EQ',exDate='16-Jun-2025',subject='Bonus 4:1')]
        events,errors=combined_events(rows+[rows[0]],specs)
        self.assertEqual(len(events),1);self.assertEqual(events[0]['factor'],10);self.assertFalse(errors)

    def test_restoration_preserves_raw_and_traded_value(self):
        raw=pd.DataFrame(dict(open=[100.,101.],high=[102.,103.],low=[99.,100.],close=[101.,102.],volume=[10000.,20000.]))
        original=raw.copy(deep=True);restored=restore_bars(raw,10)
        pd.testing.assert_frame_equal(raw,original)
        np.testing.assert_allclose(restored.close*restored.volume,raw.close*raw.volume)
        np.testing.assert_allclose(restored.close,raw.close*10)
        np.testing.assert_allclose(restored.volume,raw.volume/10)

    def test_preference_security_bonus_is_not_equity_share_multiplication(self):
        specs=[dict(symbol='TVSMOTOR',instrument_key='K')]
        rows=[dict(symbol='TVSMOTOR',series='EQ',exDate='25-Aug-2025',subject='Scheme Of Arrangement - Bonus Ncrps 4:1')]
        events,unresolved=combined_events(rows,specs)
        self.assertFalse(events);self.assertEqual(len(unresolved),1)
        self.assertIn('Non-equity',unresolved[0]['reason'])

    def test_prior_close_uses_current_day_basis_at_action(self):
        events=[dict(key='K',day='2025-06-16',factor=10,classification='back_adjusted')]
        # The source previous-close quote is already on the same adjusted basis.
        self.assertEqual(current_basis_prev_close(933,factor_from_events('K','2025-06-16',events)),933)
        self.assertEqual(current_basis_prev_close(933,factor_from_events('K','2025-06-13',events)),9330)

    def test_unverified_basis_cannot_silently_restore(self):
        audit=dict(events=[dict(key='K',day='2025-06-16',factor=10,classification='ambiguous')],reciprocal_volume_confirmed={'K':False})
        with self.assertRaises(UnitBasisError):price_factor('K','2025-06-13',audit)
        audit['events'][0]['classification']='back_adjusted'
        with self.assertRaises(UnitBasisError):price_factor('K','2025-06-13',audit)
        audit['reciprocal_volume_confirmed']['K']=True
        self.assertEqual(price_factor('K','2025-06-13',audit),10)


if __name__=='__main__':unittest.main(verbosity=2)
