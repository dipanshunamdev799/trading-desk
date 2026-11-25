"""Meaningful numerical, chronological and immutable-ledger tests."""
import json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
import pandas as pd
from .common import *
from .distributions import Distribution,BUCKETS
from .ledger import append,events,verify_files,resolution_eligible
from .prospective import timing
from research.nifty_forecast_v3.experiment import available,inner_split

class V4Checks(unittest.TestCase):
    def test_all_v3_inputs_preserved(self):
        for r in read('v3-audit-inventory.json'):self.assertEqual(sha(ROOT/r['path']),r['sha256'])
        for r in read('v3-source-review.json'):self.assertEqual(sha(r['path']),r['sha256'])
    def test_original_probabilities_reproduced(self):
        r=read('v3-reproduction-checks.json');self.assertTrue(r['passed']);self.assertEqual(len(r['independent_refits']),2)
        self.assertLess(max(d['max_probability_difference'] for d in r['folds']),1e-12)
    def test_distribution_identity(self):
        d=Distribution([-.1,0,.02,.05],[1,2,3,4]);s=d.stats(25000)
        self.assertAlmostEqual(s['p_up'],.7);self.assertAlmostEqual(s['p_nonpositive'],.3);self.assertAlmostEqual(sum(s['buckets']),1)
        self.assertAlmostEqual(s['expected_endpoint'],25000*(1+sum(d.w*d.a)))
        self.assertAlmostEqual(s['expected_absolute_return'],float(d.w@abs(d.a)))
        self.assertIsNone(s['path_breach_probability']);self.assertIsNone(s['future_realized_volatility'])
    def test_weighted_crps_against_definition(self):
        d=Distribution([-.1,0,.02,.05],[1,2,3,4]);y=.01
        brute=float(d.w@abs(d.a-y)-.5*np.sum(d.w[:,None]*d.w[None,:]*abs(d.a[:,None]-d.a[None,:])))
        self.assertAlmostEqual(d.score(y)['crps'],brute)
    def test_quantiles_noncrossing(self):
        q=Distribution([.02,-.03,0,.04],[.1,.6,.2,.1]).quantile(np.linspace(0,1,101));self.assertTrue((np.diff(q)>=0).all())
    def test_invalid_support_rejected(self):
        for a,w in [([-1,0],None),([np.nan,0],None),([0,.1],[-1,1]),([0],[0])]:
            with self.assertRaises(ValueError):Distribution(a,w)
    def test_scope_including_2027(self):
        for day in ['2024-12-31','2027-01-01']:
            with self.assertRaises(ValueError):check_scope([day])
    def test_timing_late_rejected(self):
        with self.assertRaises(ValueError):timing('2026-11-18T09:11:00+05:30','2026-11-18T09:11:30+05:30')
        self.assertFalse(timing('2026-11-18T09:11:00+05:30','2026-11-18T09:11:30+05:30',True))
    def test_timing_early_started_valid(self):self.assertTrue(timing('2026-11-18T09:02:00+05:30','2026-11-18T09:10:30+05:30'))
    def test_incomplete_resolution_rejected(self):
        f={'expected_endpoint':'2026-11-23'};self.assertFalse(resolution_eligible(f,'2026-11-23T15:00:00+05:30'));self.assertTrue(resolution_eligible(f,'2026-11-23T18:00:00+05:30'))
    def test_append_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ledger.jsonl';a=append(p,'FORECAST','key',{'value':1});before=p.read_bytes()
            with self.assertRaises(ValueError):append(p,'FORECAST','key',{'value':2})
            self.assertEqual(p.read_bytes(),before);b=append(p,'RESOLUTION','key',{'value':2});self.assertEqual(b['previous_hash'],a['hash']);self.assertEqual(len(events(p)),2)
    def test_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ledger.jsonl';append(p,'FORECAST','key',{'value':1});p.write_text(p.read_text().replace('"value":1','"value":2'))
            with self.assertRaises(ValueError):events(p)
    def test_partial_write_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ledger.jsonl';p.write_text('{')
            with self.assertRaises(ValueError):events(p)
    def test_changed_frozen_file_rejected(self):
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            p=Path(tmp)/'frozen.json';p.write_text('{}');event={'payload':{'files':{str(p.relative_to(ROOT)):sha(p)}}};verify_files(event)
            p.write_text('{"changed":true}')
            with self.assertRaises(ValueError):verify_files(event)
    def test_writer_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ledger.jsonl';p.with_suffix('.lock').write_text('held')
            with self.assertRaises(FileExistsError):append(p,'FORECAST','key',{})
    def test_mixed_timestamp_regression(self):
        stamps=pd.to_datetime(['2026-11-16 03:45:00+00:00','2026-11-17T09:55:00+00:00'],utc=True,format='mixed');self.assertEqual(len(stamps),2)
    def test_all_distribution_training_mature_and_purged(self):
        for r in read('distribution-fit-ledger.json'):
            self.assertLess(r['last_training_endpoint'],r['query_first']);self.assertLess(r['inner_fit_last_endpoint'],r['inner_first'])
    def test_monthly_uncertainty_not_invented(self):
        for r in read('v4-uncertainty.json'):
            if r['horizon']==21:self.assertIsNone(r['paired95']);self.assertIsNone(r['familywise95'])
    def test_cohort_separation(self):
        for e in events(OUT/'prospective-ledger.jsonl'):
            verify_files(e)
            if e['kind']=='FORECAST' and e['payload']['cohort']=='LATE_DIAGNOSTIC':self.assertFalse(e['payload']['primary_eligible'])
    def test_calibration_disabled_and_frozen(self):
        self.assertEqual(read('registry.json')['calibration_diagnostics']['activation'],'NONE; raw frozen policies remain raw')
    def test_stop_rules_respect_boundary(self):
        self.assertIn('2027',read('prospective-stop-rules.json')['scope_stop']);self.assertGreater(read('prospective-stop-rules.json')['fixed_final_disjoint_n']['21'],4)
    def test_resolution_roundtrip_and_idempotence(self):
        from . import prospective as ps
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            folder=Path(tmp);ledger=folder/'events.jsonl';days=['2026-11-18','2026-11-19','2026-11-20','2026-11-23','2026-11-24']
            f={'reference':'2026-11-17','reference_close':100.,'expected_endpoint':days[-1],'target_sessions':days,
                'binary_probabilities':{'Z_neutral':.5,'Z_reversion':.45},
                'distributions':{'D00_empirical':{'atoms':[-.01,.03],'weights':[.5,.5]},'D03_residual_shrunk':{'atoms':[-.02,.04],'weights':[.5,.5]}}}
            append(ledger,'FORECAST','test',{'primary_eligible':True,'forecasts':{'5':f},'files':{}})
            candles=[[d+'T00:00:00+05:30',100,104,99,102 if d==days[-1] else 100,0,0] for d in ['2026-11-17']+days]
            class FakeResponse:
                def json(self):return {'data':{'candles':candles}}
            class FakeCapture:
                def __init__(self,folder):self.requests=[]
                def get(self,*args):return FakeResponse()
            with patch.object(ps,'OUT',folder),patch.object(ps,'LEDGER',ledger),patch.object(ps,'now',lambda:'2026-11-25T19:00:00+05:30'),patch.object(ps,'Capture',FakeCapture):
                ps.resolve();after=ledger.read_bytes();ps.resolve();self.assertEqual(ledger.read_bytes(),after)
            records=events(ledger);self.assertEqual(len(records),2);r=records[-1]['payload'];self.assertAlmostEqual(r['realized_return'],.02)
            self.assertAlmostEqual(r['binary_scores']['Z_neutral']['brier'],.25);self.assertAlmostEqual(r['matched_binary_improvements']['Z_reversion']['brier_vs_Z_neutral'],.25-.55**2)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(V4Checks);result=unittest.TextTestRunner(verbosity=2).run(suite)
    save('verification.json',{'tests':result.testsRun,'passed':result.wasSuccessful(),'failures':[(str(a),b) for a,b in result.failures],'errors':[(str(a),b) for a,b in result.errors],'verified_at':now()})
    raise SystemExit(0 if result.wasSuccessful() else 1)
