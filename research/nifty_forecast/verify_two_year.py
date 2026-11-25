"""Check strict window isolation and two-year training chronology."""
from __future__ import annotations
import json
import unittest
import numpy as np
import pandas as pd
from .engine import BASE,digest,load_panel
from .two_year import START,TARGET,bounded_features,fit_experts


class TwoYearChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bars,cls.globals_,*_=load_panel(BASE/'inputs-v2',BASE/'supplement-v1',TARGET)
        cls.run_dir=BASE/'two-year-v1'

    def test_older_prices_cannot_affect_any_feature(self):
        x,labels,_,_,_=bounded_features(self.bars,self.globals_)
        modified=[]
        for collection in [self.bars,self.globals_]:
            change={k:v.copy(deep=True) for k,v in collection.items()}
            for frame in change.values():
                frame.loc[frame.index<START,['open','high','low','close']]*=7
            modified.append(change)
        changed,changed_labels,_,_,_=bounded_features(*modified)
        np.testing.assert_equal(x.to_numpy(),changed.to_numpy())
        pd.testing.assert_frame_equal(labels,changed_labels)

    def test_every_used_series_is_inside_two_calendar_years(self):
        _,labels,_,bars,globals_=bounded_features(self.bars,self.globals_)
        for frame in [*bars.values(),*globals_.values()]:
            self.assertTrue((frame.index>=START).all())
            self.assertTrue((frame.index<TARGET).all())
        self.assertEqual(len(bars['nifty_spot']),495)
        self.assertEqual(len(labels),475)
        self.assertTrue((labels.decision_day>=START).all())

    def test_all_fits_and_meta_history_use_prior_bounded_labels(self):
        for target in ['close_return','intraday_return']:
            for fit in json.loads((self.run_dir/f'expert-fits-{target}.json').read_text()):
                self.assertGreaterEqual(fit['first_training_target'],START)
                self.assertLess(fit['last_training_target'],fit['fit_for_target'])
                self.assertLessEqual(fit['training_n'],474)
            replay=pd.read_csv(self.run_dir/f'prequential-{target}.csv')
            for field in ['meta_last_target','calibration_last_target']:
                rows=replay[replay[field].notna()]
                self.assertTrue((rows[field]>=START).all())
                self.assertTrue((rows[field]<=rows.decision_day).all())
            weights=pd.read_csv(self.run_dir/f'daily-weights-{target}.csv').iloc[:,2:]
            np.testing.assert_allclose(weights.sum(axis=1),1.,atol=1e-9)

    def test_future_labels_do_not_change_prior_two_year_experts(self):
        n=475;days=pd.bdate_range('2024-11-18',periods=n+1).strftime('%Y-%m-%d')
        y=np.where(np.sin(np.arange(n))>0,.01,-.01);y[-1]=np.nan
        labels=pd.DataFrame({'decision_day':days[:-1],'target_day':days[1:],'close_return':y})
        x=pd.DataFrame({'rsi14':np.sin(np.arange(n)/11)})
        p,_,_=fit_experts(x,labels,{'short_term_price':['rsi14']},'close_return')
        changed=labels.copy();changed.loc[400:,'close_return']*=-1
        after,_,_=fit_experts(x,changed,{'short_term_price':['rsi14']},'close_return')
        np.testing.assert_equal(p[:401],after[:401])

    def test_saved_call_has_no_imported_longer_history_statistics(self):
        call=json.loads((self.run_dir/'forecast.json').read_text())
        self.assertEqual(call['history_window']['inclusive_start'],START)
        self.assertEqual(digest(BASE/'adaptive-v2/forecast.json'),call['comparison_forecast_sha256'])
        for values in call['forecasts'].values():
            self.assertFalse(any('analog' in k for k in values))
            self.assertLessEqual(values['training_n'],474)
        for name,expected in call['source_code_hashes'].items():
            self.assertEqual(digest(__import__('pathlib').Path(__file__).with_name(name)),expected)


if __name__=='__main__':unittest.main(verbosity=2)
