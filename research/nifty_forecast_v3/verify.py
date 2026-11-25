"""V3 source integrity, chronological isolation and hostile leakage tests."""
import json,unittest
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from .audit import ROOT,OUT,OLD,sha,save
from .data import load_series
from .features import build,labels_for
from .models import SPECS,train,predict
from .experiment import available,inner_split,nonoverlap,paired_ci
from .validation import validate_frame

class V3Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=pd.read_csv(OUT/'features.csv',index_col=0)
        cls.labels=pd.read_csv(OUT/'labels-21.csv',index_col=0)
        cls.data,_=load_series()

    def test_dataset_and_source_hashes(self):
        manifest=json.loads((OUT/'dataset-manifest.json').read_text())
        for name,digest in manifest['files'].items():self.assertEqual(sha(OUT/name),digest)
        for m in ['upstox-acquisition.json','fo-acquisition.json']:
            for path,digest in json.loads((OUT/m).read_text())['files'].items():self.assertEqual(sha(ROOT/path),digest)

    def test_old_artifacts_are_unchanged(self):
        records=json.loads((OUT/'audit-start.json').read_text())['prior_forecast_hashes']
        for path,digest in records.items():self.assertEqual(sha(ROOT/path),digest)

    def test_exact_fitted_source_archive_is_preserved(self):
        doc=json.loads((OUT/'fit-source-archive.json').read_text())
        for name,digest in doc['source_hashes'].items():self.assertEqual(sha(Path(doc['path'])/name),digest)

    def test_pre2025_inputs_are_rejected(self):
        x=self.x.head(3).copy();x.index=['2024-12-31','2025-01-02','2025-01-03']
        with self.assertRaisesRegex(ValueError,'PRE_2025'):validate_frame(x)
        data={k:v.copy() for k,v in self.data.items()};data['nifty_spot'].loc['2024-12-31']=data['nifty_spot'].iloc[0]
        with self.assertRaisesRegex(ValueError,'OUT_OF_SCOPE'):build(data)

    def test_registered_future_oracle_is_rejected_by_actual_model_fit(self):
        x=self.x.head(130).copy();y=self.labels.loc[x.index].copy()
        x['price_ret1']=y['return'];x.attrs['available_at']={'price_ret1':pd.Series(pd.to_datetime(x.index)+pd.Timedelta(days=35),index=x.index)}
        with self.assertRaisesRegex(ValueError,'LOOKAHEAD_SENTINEL'):train(SPECS['M00_ridge_price'],x,y)

    def test_unregistered_future_feature_is_rejected(self):
        x=self.x.head(130).copy();x['future_sentinel']=self.labels.loc[x.index,'return']
        with self.assertRaisesRegex(ValueError,'UNREGISTERED'):train(SPECS['M01_ridge_full'],x,self.labels.loc[x.index])

    def test_unfinished_labels_and_inner_overlap_are_purged(self):
        origin='2026-07-01';idx=available(self.labels,origin)
        self.assertTrue((self.labels.loc[idx,'endpoint']<origin).all())
        earlier_unfinished=self.labels.index[(self.labels.index<origin)&(self.labels.endpoint>=origin)]
        self.assertFalse(set(earlier_unfinished)&set(idx))
        fit,val=inner_split(self.labels,idx)
        self.assertTrue((self.labels.loc[fit,'endpoint']<val[0]).all())

    def test_changed_unfinished_targets_do_not_change_a_fitted_prediction(self):
        origin='2026-07-01';idx=available(self.labels,origin);changed=self.labels.copy()
        mask=changed.endpoint>=origin;changed.loc[mask,'return']*=5
        a=train(SPECS['M00_ridge_price'],self.x.loc[idx],self.labels.loc[idx]);b=train(SPECS['M00_ridge_price'],self.x.loc[idx],changed.loc[idx])
        pa=predict(a,self.x.loc[[origin]])[0];pb=predict(b,self.x.loc[[origin]])[0]
        for key in ['p','mean','vol','samples']:np.testing.assert_allclose(pa[key],pb[key])

    def test_feature_reproduction_and_future_source_invariance(self):
        fo=pd.read_csv(OUT/'fo-eod-panel.csv',index_col=0);x,_=build(self.data,fo)
        self.assertEqual(list(x.columns),list(self.x.columns))
        np.testing.assert_allclose(x.to_numpy(),self.x.to_numpy(),rtol=1e-10,atol=1e-12,equal_nan=True)
        modified={k:v.copy() for k,v in self.data.items()}
        for frame in modified.values():frame.loc[frame.index>'2026-07-01',['open','high','low','close']]*=1.2
        later_fo=fo.copy();later_fo.loc[later_fo.index>'2026-07-01','oi_pcr']+=10
        after,_=build(modified,later_fo);mask=x.index<='2026-07-01'
        np.testing.assert_allclose(x.loc[mask].to_numpy(),after.loc[mask].to_numpy(),equal_nan=True)

    def test_guard_amendment_does_not_change_frozen_model_math(self):
        for model_id in ['M00_ridge_price','M01_ridge_full','M05_lgbm']:
            artifact=joblib.load(OUT/'models'/f'h5-2026-07-{model_id}.joblib')
            labels=pd.read_csv(OUT/'labels-5.csv',index_col=0);tr=artifact['train_idx'];origin=artifact['preprocess_available_at']
            regenerated=train(SPECS[model_id],self.x.loc[tr],labels.loc[tr])
            a=predict(artifact['model'],self.x.loc[[origin]],artifact['residuals'])[0]
            b=predict(regenerated,self.x.loc[[origin]],artifact['residuals'])[0]
            for key in ['p','mean','vol','tail02','samples']:np.testing.assert_allclose(a[key],b[key],atol=1e-12)

    def test_independent_targets_are_exact(self):
        price=pd.read_csv(OUT/'price.csv',index_col=0)
        for h in [5,21]:
            labels=labels_for(price,h);i=20
            self.assertAlmostEqual(labels['return'].iloc[i],price.close.iloc[i+h]/price.close.iloc[i]-1)
            self.assertEqual(labels['return'].isna().sum(),h)

    def test_actual_forecast_origins_and_selector_proxy_exclusion(self):
        p=pd.read_csv(OUT/'predictions.csv')
        self.assertTrue((p.origin>='2025-01-01').all())
        selectors=p[p.model.str.startswith('S_')]
        self.assertFalse((selectors.selected_model=='A02_proxy').any())
        for (h,name),g in p.groupby(['horizon','model']):
            selected=nonoverlap(g)
            if len(selected)>1:self.assertTrue((selected.origin.iloc[1:].to_numpy()>=selected.endpoint.iloc[:-1].to_numpy()).all())

    def test_official_underlying_matches_and_oi_identity_is_unique(self):
        check=json.loads((OUT/'official-underlying-crosscheck.json').read_text())
        self.assertEqual(check['matched'],465);self.assertEqual(check['max_abs_points'],0.)
        for path in (OUT/'sources/fo').glob('*.json'):
            doc=json.loads(path.read_text());rows=doc['rows']
            ids=[r['FinInstrmId'] for r in rows];self.assertEqual(len(ids),len(set(ids)))
            self.assertTrue(all(r['TradDt']==doc['day'] for r in rows))
            self.assertTrue(all(float(r['OpnIntrst'])>=0 and float(r['TtlTradgVol'])>=0 for r in rows))

    def test_index_volume_is_not_invented_and_partial_intraday_is_missing(self):
        self.assertTrue(self.data['nifty_spot'].volume.eq(0).all())
        self.assertTrue(self.data['niftybees'].volume.gt(0).all())
        self.assertTrue(self.x.loc['2026-11-16',[c for c in self.x if c.startswith('intraday_')]].isna().all())

    def test_monthly_uncertainty_is_not_manufactured(self):
        self.assertIsNone(paired_ci(np.zeros(76),21))
        self.assertEqual(paired_ci(np.zeros(92),5),[0.,0.])

def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(V3Checks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    save('verification.json',{'tests':result.testsRun,'passed':result.wasSuccessful(),
        'failures':[(str(t),s) for t,s in result.failures],'errors':[(str(t),s) for t,s in result.errors],
        'note':'Validation guards and explicit contract-ID exclusion added after first batch; exact initial fit source archived; representative recomputations verify identical numerical results.'})
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
