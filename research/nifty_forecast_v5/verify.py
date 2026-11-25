"""Numerical reproduction, causal construction, frozen versions and forecast identities."""
import json,unittest,warnings,joblib
from unittest.mock import patch
import numpy as np
import pandas as pd
from .common import *
from .data import load
from .features import build,completion,align_global
from .models import fit,laws,mean_prediction
from .validation import validate_training
from research.nifty_forecast_v4.distributions import Distribution
from research.nifty_forecast_v3.experiment import available,inner_split

class V5Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=pd.read_csv(OUT/'features.csv',index_col=0);cls.labels={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [1,3,5,21]};cls.data,_=load()
        cls.pred=pd.read_csv(OUT/'all-predictions.csv');cls.call=read('experimental-forecasts.json')
    def test_preserve_every_prior_artifact_and_v4_ledger(self):
        for name,digest in read('history-audit.json')['preservation_hashes'].items():self.assertEqual(sha(ROOT/name),digest)
    def test_source_dataset_hashes(self):
        for name,digest in read('acquisition.json')['files'].items():self.assertEqual(sha(ROOT/name),digest)
        for name,digest in read('dataset-manifest.json')['files'].items():self.assertEqual(sha(OUT/name),digest)
    def test_bounded_raw_source_dates(self):
        for frame in self.data.values():scope(frame.index)
        for stamp in ['2024-12-31','2027-01-01']:
            with self.assertRaises(ValueError):scope([stamp])
    def test_mature_embargo_for_every_success(self):
        for r in read('experiment-registry.json'):
            if r['status']=='ok':self.assertLess(r['last_training_endpoint'],r['first_query'])
            if 'last_inner_endpoint' in r:self.assertLess(r['last_inner_endpoint'],r['inner_first'])
    def test_model_artifact_hashes(self):
        for r in read('experiment-registry.json'):
            if r['status']=='ok':self.assertEqual(sha(ROOT/r['artifact']),r['sha256'])
    def test_identical_dates_and_outcomes(self):
        f=self.pred[self.pred.split=='outer_exposed']
        for h in [5,21]:
            g=f[f.horizon==h];self.assertEqual(g.model.nunique(),34);self.assertEqual(set(g.groupby('model').size()),{92 if h==5 else 76})
            self.assertFalse(g.duplicated(['model','origin']).any());self.assertTrue((g.groupby('origin').realized_return.max()-g.groupby('origin').realized_return.min()).abs().max()<1e-12)
    def test_dst_completion(self):
        self.assertEqual(completion('2025-03-07','GLOBAL|^GSPC').tz_convert('UTC').hour,23)
        self.assertEqual(completion('2025-03-10','GLOBAL|^GSPC').tz_convert('UTC').hour,22)
    def test_future_global_close_excluded(self):
        s=pd.Series([1.,999.],index=['2026-11-16','2026-11-17']);origin=['2026-11-16'];decision=[pd.Timestamp('2026-11-17 09:10',tz='Asia/Kolkata')]
        aligned,_=align_global(s,'GLOBAL|^GSPC',origin,decision);self.assertEqual(aligned.iloc[0],1.)
    def test_all_recorded_global_availability(self):
        f=pd.read_csv(OUT/'global-availability.csv')
        for r in f.itertuples():self.assertLessEqual(pd.Timestamp(r.available_assumption),pd.Timestamp(r.decision))
    def test_future_source_perturbation_invariance(self):
        data={k:v.copy() for k,v in self.data.items()};day=self.x.index[-30]
        data['nifty_spot'].loc[data['nifty_spot'].index>day,'close']*=1.1
        for name,f in data.items():
            if name.startswith('g_'):f.loc[f.index>day,'close']*=1.2
        with warnings.catch_warnings():warnings.simplefilter('ignore',pd.errors.PerformanceWarning);rebuilt,_,_=build(data,extra=False)
        common=[c for c in rebuilt if c in self.x];np.testing.assert_allclose(rebuilt.loc[:day,common],self.x.loc[:day,common],equal_nan=True,atol=1e-10,rtol=1e-10)
    def test_independent_refit_native_model(self):
        day='2026-06-30';h=5;idx=available(self.labels[h],day);ii,vv=inner_split(self.labels[h],idx);ctx={'labels':self.labels,'cutoff':day}
        inner=fit('I00',self.x.loc[ii],self.labels[h].loc[ii,'return'].to_numpy(),h,ctx);res=self.labels[h].loc[vv,'return'].to_numpy()-mean_prediction(inner,self.x.loc[vv],ctx)
        model=fit('I00',self.x.loc[idx],self.labels[h].loc[idx,'return'].to_numpy(),h,ctx)
        g=self.pred[(self.pred.horizon==h)&(self.pred.model=='I00')&(self.pred.fold=='2026-07')]
        pred=laws(model,self.x.loc[g.origin],ctx,res);np.testing.assert_allclose([d.stats()['p_up'] for d in pred],g.p,atol=1e-10,rtol=1e-10)
    def test_training_endpoint_guard(self):
        day=self.x.index[120];ctx={'labels':self.labels,'cutoff':day};idx=self.x.index[:120]
        with self.assertRaisesRegex(ValueError,'UNMATURED'):validate_training(self.x.loc[idx],21,ctx)
    def test_future_oracle_rejected(self):
        x=self.x.head(5).copy();x['p_future_oracle']=1
        with self.assertRaisesRegex(ValueError,'UNREGISTERED'):validate_training(x,5,{})
        x=self.x.head(5).copy();x.attrs['available_at']={'p_ret1':[pd.Timestamp('2026-12-31',tz='Asia/Kolkata')]*5}
        with self.assertRaisesRegex(ValueError,'FUTURE_AVAILABILITY'):validate_training(x,5,{})
    def test_issued_distribution_identities(self):
        for f in self.call['forecasts'].values():
            law=Distribution(f['atoms'],f['weights']);s=law.stats(self.call['reference_close']);saved=f['statistics']
            for name in ['p_up','mean_return','median_return','expected_endpoint','expected_absolute_return']:self.assertAlmostEqual(s[name],saved[name])
            self.assertAlmostEqual(s['p_up']+s['p_nonpositive'],1);self.assertAlmostEqual(sum(s['buckets']),1);self.assertIsNone(saved['path_breach_probability']);self.assertIsNone(saved['future_realized_volatility'])
    def test_crps_bruteforce(self):
        d=Distribution([-.03,0,.05],[.2,.3,.5]);y=.01;v=d.w@abs(d.a-y)-.5*np.sum(d.w[:,None]*d.w[None,:]*abs(d.a[:,None]-d.a[None,:]));self.assertAlmostEqual(d.score(y)['crps'],v)
    def test_source_prefix_and_close18(self):
        fresh=pd.read_csv(OUT/'latest-inputs/features.csv',index_col=0);np.testing.assert_allclose(fresh.loc[self.x.index],self.x,equal_nan=True,atol=1e-10,rtol=1e-10)
        self.assertEqual(self.call['reference_session'],'2026-11-18');self.assertAlmostEqual(self.call['reference_close'],25227.95)
        doc=read('fo/2026-11-18.json');official=float(next(r['UndrlygPric'] for r in doc['rows'] if float(r.get('UndrlygPric') or 0)>0));self.assertAlmostEqual(official,self.call['reference_close'])
    def test_fresh_issue_before_horizons(self):
        self.assertTrue(self.call['before_first_target_session']);self.assertLess(self.call['issued_at'][:10],self.call['first_target_session'])
        for f in self.call['forecasts'].values():scope(f['target_sessions']);self.assertEqual(len(f['target_sessions']),f['horizon']);self.assertLess(f['last_training_endpoint'],self.call['reference_session'])
    def test_no_unfinished_us_close_in_live_features(self):
        f=pd.read_csv(OUT/'latest-inputs/global-availability.csv');f=f[f.origin=='2026-11-18']
        for r in f.itertuples():self.assertLessEqual(pd.Timestamp(r.available_assumption),pd.Timestamp(self.call['issued_at']))
    def test_issued_inputs_and_exact_source(self):
        for name,digest in self.call['input_hashes'].items():self.assertEqual(sha(ROOT/name),digest)
        for name,digest in self.call['source_code_hashes'].items():self.assertEqual(sha(OUT/'source-at-issue'/name),digest)
        self.assertEqual(sha(OUT/'source-at-first-fit/models.py'),read('registry.json')['source_hashes']['models.py'])
    def test_proxy_excluded_from_selected_systems(self):self.assertTrue(all(f['model'] not in ['T01','BR00','L03'] for f in self.call['forecasts'].values()))
    def test_date_grouping_not_random_stock_rows(self):
        for name in ['stock-panel.csv','sector-panel.csv']:
            frame=pd.read_csv(OUT/name);self.assertGreater(len(frame),frame.date.nunique());self.assertFalse(frame.duplicated(['date','asset']).any())
    def test_monthly_intervals_withheld(self):
        for r in read('uncertainty.json'):
            if r['horizon']==21:self.assertIsNone(r['paired95']);self.assertIsNone(r['simultaneous95'])
    def test_failed_attempts_preserved_and_repaired(self):
        failed=[r for r in read('fits-stage3.json') if r['status']=='failed'];fixed=read('fits-stage3-repair.json');self.assertEqual(len(failed),11);self.assertEqual(len(fixed),11);self.assertTrue(all(r['model']=='I06_forest' for r in failed))
    def test_randomized_training_controls_not_skill(self):self.assertTrue(all(r['brier']>.25 for r in read('negative-controls.json')))
    def test_resolution_requires_completed_close(self):
        from .score import mature
        self.assertFalse(mature('2026-11-26','2026-11-26T15:00:00+05:30'));self.assertTrue(mature('2026-11-26','2026-11-26T18:00:00+05:30'))
    def test_pending_scorer_has_no_network_or_mutation(self):
        from . import score
        p=OUT/'evaluation-ledger.jsonl';before=p.read_bytes() if p.exists() else None
        with patch.object(score,'now',lambda:'2026-11-18T23:00:00+05:30'),patch.object(score.requests,'get',side_effect=AssertionError('Unexpected network')):score.run()
        self.assertEqual(before,p.read_bytes() if p.exists() else None)
    def test_benchmarks_frozen_before_target(self):
        b=read('frozen-benchmark-supplement.json');self.assertEqual(b['forecast_sha256'],sha(OUT/'experimental-forecasts.json'));self.assertLess(b['issued_at'][:10],self.call['first_target_session'])
        law=Distribution(b['weekly_empirical']['atoms'],b['weekly_empirical']['weights']);self.assertAlmostEqual(law.stats(self.call['reference_close'])['p_up'],b['weekly_empirical']['statistics']['p_up'])

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(V5Checks))
    save('verification.json',{'tested_at':now(),'tests':result.testsRun,'passed':result.wasSuccessful(),'failures':[(str(a),b) for a,b in result.failures],'errors':[(str(a),b) for a,b in result.errors],
        'amendment':'Schema/availability/maturity contracts added after discovery fits; exact original fit and issue source archived; independent native-model refit verifies unchanged numeric result.'})
    raise SystemExit(0 if result.wasSuccessful() else 1)
