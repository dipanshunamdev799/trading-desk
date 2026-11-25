"""Test horizon maturity, overlap handling, distributions and frozen artifacts."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from .engine import BASE,digest,load_panel
from .two_year import bounded_features,START,TARGET
from .horizons import (future_sessions,horizon_labels,matured_indices,fit_experts,
    replay_predictions,magnitude_distribution,block_interval,nonoverlapping)
from .score_horizons import resolve


class HorizonChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bars,globals_,*_=load_panel(BASE/'inputs-v2',BASE/'supplement-v1',TARGET)
        cls.x,cls.days,_,cls.bars,_=bounded_features(bars,globals_)
        cls.calendar=json.loads((BASE/'horizon-calendar-v1.json').read_text())
        cls.future=future_sessions(cls.bars['nifty_spot'].index[-1],cls.calendar,21)
        cls.run_dir=BASE/'horizons-v2'

    def test_calendar_includes_special_sessions_and_excludes_holidays(self):
        self.assertEqual(self.future[4],'2026-11-23')
        self.assertEqual(self.future[20],'2026-12-16')
        self.assertNotIn('2026-11-24',self.future)
        self.assertEqual(future_sessions('2026-01-30',self.calendar,3),['2026-02-01','2026-02-02','2026-02-03'])

    def test_five_and_twenty_one_session_returns_use_correct_endpoints(self):
        price=self.bars['nifty_spot']
        for h in [5,21]:
            labels=horizon_labels(self.days,self.bars,self.future,h)
            row=labels.iloc[100];pos=price.index.get_loc(row.decision_day)
            self.assertAlmostEqual(row.horizon_return,price.close.iloc[pos+h]/price.close.iloc[pos]-1)
            self.assertEqual(row.label_end_day,price.index[pos+h])
            self.assertEqual(int(labels.horizon_return.isna().sum()),h)

    def test_earlier_but_unfinished_month_labels_are_unavailable(self):
        labels=horizon_labels(self.days,self.bars,self.future,21)
        i=400;available=matured_indices(labels,i)
        self.assertIn(i-21,available);self.assertNotIn(i-20,available);self.assertNotIn(i-1,available)
        self.assertTrue((labels.label_end_day.iloc[available]<=labels.decision_day.iloc[i]).all())

    def test_unfinished_outcome_changes_cannot_change_past_predictions_or_ranges(self):
        labels=horizon_labels(self.days,self.bars,self.future,21)
        x=self.x[['rsi14']].copy();groups={'short_term_price':['rsi14']}
        p,n,_=fit_experts(x,labels,groups,21)
        a,wa=replay_predictions(p,n,labels,21)
        cutoff=400;changed=labels.copy()
        future=(changed.label_end_day>labels.decision_day.iloc[cutoff])&changed.horizon_return.notna()
        changed.loc[future,'horizon_return']*=-3
        later,nn,_=fit_experts(x,changed,groups,21)
        b,wb=replay_predictions(later,nn,changed,21)
        np.testing.assert_equal(p[:cutoff+1],later[:cutoff+1])
        np.testing.assert_allclose(wa[:cutoff+1],wb[:cutoff+1])
        cols=['calibrated_adaptive','calibration_intercept','median_return','q10','q90']
        np.testing.assert_allclose(a.loc[a.i<=cutoff,cols],b.loc[b.i<=cutoff,cols])

    def test_empirical_median_respects_probability_mass_on_each_side_of_zero(self):
        values=np.array([-.03,-.01,.01,.03])
        up=magnitude_distribution(values,.6);down=magnitude_distribution(values,.4)
        self.assertGreater(up['quantiles']['0.5'],0)
        self.assertLess(down['quantiles']['0.5'],0)
        self.assertAlmostEqual(up['mean'],.004)

    def test_overlap_subset_has_disjoint_return_windows(self):
        frame=pd.read_csv(self.run_dir/'evaluation-month.csv')
        selected=nonoverlapping(frame)
        for i in range(1,len(selected)):
            self.assertGreaterEqual(selected.decision_day.iloc[i],selected.label_end_day.iloc[i-1])
        self.assertEqual(len(selected),2)

    def test_monthly_confidence_interval_is_withheld_when_history_is_too_short(self):
        self.assertIsNone(block_interval(np.zeros(36),21))
        self.assertEqual(block_interval(np.zeros(84),5),[0.,0.])

    def test_every_saved_training_and_update_endpoint_is_mature(self):
        for name in ['week','month']:
            for fit in json.loads((self.run_dir/f'expert-fits-{name}.json').read_text()):
                self.assertGreaterEqual(fit['first_training_origin'],START)
                self.assertLessEqual(fit['last_training_endpoint'],fit['fit_after_close'])
            replay=pd.read_csv(self.run_dir/f'prequential-{name}.csv')
            for field in ['meta_last_endpoint','calibration_last_endpoint','magnitude_last_endpoint']:
                rows=replay[replay[field].notna()]
                self.assertTrue((rows[field]<=rows.decision_day).all())
            weights=pd.read_csv(self.run_dir/f'daily-weights-{name}.csv').iloc[:,3:]
            np.testing.assert_allclose(weights.sum(axis=1),1.,atol=1e-9)

    def test_outcome_scoring_waits_for_the_full_horizon(self):
        call=json.loads((self.run_dir/'forecast.json').read_text())
        future=self.future
        candles=[[call['reference_date']+'T00:00:00+05:30',100,100,100,100,0,0]]
        candles += [[day+'T00:00:00+05:30',101,101,101,101,0,0] for day in future[:5]]
        scores=resolve(call,candles)
        self.assertEqual(scores['week']['status'],'resolved')
        self.assertEqual(scores['month']['status'],'pending')

    def test_frozen_sources_and_previous_daily_call_are_unchanged(self):
        call=json.loads((self.run_dir/'forecast.json').read_text())
        self.assertEqual(call['history_window']['inclusive_start'],START)
        self.assertEqual(digest(Path(call['comparison_daily_forecast_path'])),call['comparison_daily_forecast_sha256'])
        for name,expected in call['source_code_hashes'].items():
            self.assertEqual(digest(Path(__file__).with_name(name)),expected)


if __name__=='__main__':unittest.main(verbosity=2)
