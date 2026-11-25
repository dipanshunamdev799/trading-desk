"""Focused checks for learned weights, sequence boundaries and evidence gates."""
from __future__ import annotations
import json
import unittest
import numpy as np
import pandas as pd
from .engine import BASE,digest
from .adaptive import (imbalance,feature_groups,project_simplex,learn_blend,
                       sequential_blend,expert_predictions,fit_calibrator)


def synthetic(n=600):
    rng=np.random.default_rng(737)
    dates=pd.bdate_range('2020-01-01',periods=n+1).strftime('%Y-%m-%d')
    returns=rng.choice([-.01,.01],n).astype(float);returns[-1]=np.nan
    labels=pd.DataFrame({'decision_day':dates[:-1],'target_day':dates[1:],
                         'close_return':returns,'intraday_return':returns})
    t=np.arange(n)
    pred=np.column_stack([.5+.05*np.sin(t/17),.5+.06*np.cos(t/23),.5+.02*np.sin(t/9)])
    counts=np.full_like(pred,600,dtype=int)
    return labels,pred,counts


class AdaptiveChecks(unittest.TestCase):
    def test_cash_ratio_invariant_to_common_unit_scale(self):
        expected=imbalance(15000.,11000.)
        for scale in [.0001,10.,1e7]:
            self.assertAlmostEqual(expected,imbalance(15000.*scale,11000.*scale))
        self.assertTrue(np.isnan(imbalance(0.,0.)))
        self.assertTrue(np.isnan(imbalance(-1.,2.)))

    def test_simplex_constraints(self):
        for v in [np.array([.2,.3,.5]),np.array([-10.,3.,6.])]:
            w=project_simplex(v)
            self.assertTrue((w>=0).all());self.assertAlmostEqual(w.sum(),1.)

    def test_prediction_errors_reward_the_better_expert(self):
        y=np.tile([0.,1.],200)
        p=np.column_stack([np.full(len(y),.5),.1+.8*y,.9-.8*y])
        w=learn_blend(p,y)
        self.assertGreater(w[1],.8);self.assertLess(w[2],.001)
        self.assertLess(np.mean((p@w-y)**2),.25)

    def test_future_labels_cannot_change_past_weights_or_calibration(self):
        labels,pred,counts=synthetic()
        a,wa=sequential_blend(pred,counts,labels,'close_return',start=0)
        changed=labels.copy();changed.loc[450:,'close_return']*=-1
        b,wb=sequential_blend(pred,counts,changed,'close_return',start=0)
        np.testing.assert_allclose(wa[:451],wb[:451],atol=1e-12)
        np.testing.assert_allclose(a.calibrated_adaptive.iloc[:451],b.calibrated_adaptive.iloc[:451],atol=1e-12)

    def test_missing_and_short_history_experts_receive_zero_primary_weight(self):
        labels,pred,counts=synthetic(400)
        counts[:,1]=100;pred[-1,2]=np.nan
        replay,w=sequential_blend(pred,counts,labels,'close_return',start=0)
        self.assertEqual(w[-1,2],0.);self.assertEqual(w[-1,3],0.)
        self.assertAlmostEqual(w[-1].sum(),1.)
        self.assertTrue(replay.calibrated_adaptive.between(.05,.95).all())

    def test_future_training_labels_do_not_change_earlier_expert_fits(self):
        labels,_,_=synthetic(800)
        x=pd.DataFrame({'return1_risk_scaled':np.sin(np.arange(800)/11),
                        'rsi14':np.cos(np.arange(800)/23)})
        groups={k:v for k,v in feature_groups(x.columns).items() if v}
        p,_,_=expert_predictions(x,labels,groups,'close_return')
        changed=labels.copy();changed.loc[690:,'close_return']*=-1
        after,_,_=expert_predictions(x,changed,groups,'close_return')
        np.testing.assert_equal(p[:691],after[:691])

    def test_calibration_is_monotone(self):
        p=np.linspace(.3,.7,200);y=np.tile([1.,0.],100)
        beta=fit_calibrator(p,y)
        self.assertGreaterEqual(beta[1],0.);self.assertLessEqual(beta[1],3.)

    def test_saved_allocations_and_training_boundaries(self):
        run=BASE/'adaptive-v2'
        forecast=json.loads((run/'forecast.json').read_text())
        self.assertEqual(digest(BASE/'run-v3/forecast.json'),forecast['original_forecast_sha256'])
        for name in ['close_return','intraday_return']:
            r=pd.read_csv(run/f'prequential-{name}.csv')
            for clock in ['meta_last_target','calibration_last_target']:
                available=r[clock].notna()
                self.assertTrue((r.loc[available,clock]<=r.loc[available,'decision_day']).all())
            w=pd.read_csv(run/f'daily-weights-{name}.csv').iloc[:,2:]
            np.testing.assert_allclose(w.sum(axis=1),1.,atol=1e-9)
            self.assertTrue((w.to_numpy()>=-1e-12).all())
            for fit in json.loads((run/f'expert-fits-{name}.json').read_text()):
                self.assertLess(fit['last_training_target'],fit['fit_for_target'])


if __name__=='__main__':unittest.main(verbosity=2)
