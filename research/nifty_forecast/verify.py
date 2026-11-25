"""Research checks aimed at information leakage and reproducibility."""
from __future__ import annotations
import unittest
import numpy as np
import pandas as pd
from .engine import (BASE, ROOT, Scale, check_manifest, global_features, load_panel,
                     make_features, fit_logistic, predict_logistic, digest)


class ForecastChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=load_panel(BASE/'inputs-v2',BASE/'supplement-v1','2026-11-17')

    def test_raw_input_hashes(self):
        check_manifest(BASE/'inputs-v2')
        check_manifest(BASE/'supplement-v1')

    def test_unfinished_us_session_excluded(self):
        f=pd.DataFrame({'close':np.arange(100,124,dtype=float)},
            index=pd.date_range('2026-10-24',periods=24).strftime('%Y-%m-%d'))
        before=global_features(f,['2026-11-17'])
        f.loc['2026-11-16','close']=9999
        np.testing.assert_equal(before,global_features(f,['2026-11-17']))
        self.assertFalse(np.array_equal(before,global_features(f,['2026-11-18'])))

    def test_future_indian_prices_cannot_change_earlier_features(self):
        bars,global_data,*_=self.loaded
        x,labels,core=make_features(bars,global_data,'2026-11-17')
        changed={k:v.copy(deep=True) for k,v in bars.items()}
        for frame in changed.values():
            frame.loc[frame.index>'2026-09-01',['open','high','low','close']] *= 1.1
        after,_,_=make_features(changed,global_data,'2026-11-17')
        mask=labels.decision_day<'2026-09-01'
        np.testing.assert_equal(x.loc[mask].to_numpy(),after.loc[mask].to_numpy())

    def test_train_only_scaling(self):
        a=np.array([[1.,np.nan],[3.,4.],[5.,8.]])
        scaler=Scale().fit(a)
        mean=scaler.mean.copy(); median=scaler.median.copy()
        scaler.transform(np.array([[1e9,-1e9]]))
        np.testing.assert_equal(scaler.mean,mean)
        np.testing.assert_equal(scaler.median,median)
        self.assertEqual(float(median[1]),6.)

    def test_labels_have_one_session_lead(self):
        bars,globals_,*_=self.loaded
        _,labels,_=make_features(bars,globals_,'2026-11-17')
        self.assertTrue((labels.target_day>labels.decision_day).all())
        i=len(labels)-2
        expected=bars['nifty_spot'].close.iloc[-1]/bars['nifty_spot'].close.iloc[-2]-1
        self.assertAlmostEqual(float(labels.close_return.iloc[i]),float(expected))
        self.assertTrue(pd.isna(labels.close_return.iloc[-1]))

    def test_walkforward_training_and_current_label(self):
        for name in ['close_return','intraday_return']:
            r=pd.read_csv(BASE/f'run-v3/walk-forward-{name}.csv')
            self.assertEqual(len(r),504)
            self.assertTrue((r.training_last_target<=r.decision_day).all())
            self.assertTrue((r.decision_day<r.target_day).all())
            self.assertLess(r.target_day.max(),'2026-11-17')
            self.assertTrue(r.ensemble.between(.05,.95).all())

    def test_logistic_probability_matches_balanced_intercept(self):
        a=np.zeros((200,2));y=np.tile([0.,1.],100)
        b=fit_logistic(a,y,10)
        np.testing.assert_allclose(predict_logistic(a,b),.5,atol=1e-7)


if __name__=='__main__':
    unittest.main(verbosity=2)
