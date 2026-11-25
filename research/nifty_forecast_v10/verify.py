"""Independently check chronology, archived weights, links and output integrity."""
from concurrent.futures import ThreadPoolExecutor
import joblib
from .common import *
from .analyze import BATCHES,cohort_queries,nonoverlap
from .estimators import Distribution


def mapping():
    y={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    allowed={(h,c,d):(e,r) for h in y for d,e,r,c in
             cohort_queries(h)[['origin','endpoint','realized_return','split']].itertuples(index=False,name=None)}
    return y,allowed


def verify_source(receipt,root):
    if 'path' not in receipt or 'sha256' not in receipt:return None
    path=Path(receipt['path'])
    if not path.is_absolute():path=root/path
    assert path.is_file() and sha(path)==receipt['sha256'],str(path)
    return str(path)


def datachecks():
    y,allowed=mapping();reg=read('experiment-registry.json');p=pd.read_csv(OUT/'all-predictions.csv',float_precision='round_trip')
    assert len(p)==sum(r.get('query_count',0) for r in reg['attempts']),len(p)
    assert not p.duplicated(['horizon','cohort','model','origin']).any()
    actual=[allowed[key] for key in p[['horizon','cohort','origin']].itertuples(index=False,name=None)]
    np.testing.assert_array_equal(p.endpoint,[x[0] for x in actual])
    np.testing.assert_allclose(p.realized_return,[x[1] for x in actual],rtol=0,atol=1e-12)
    np.testing.assert_allclose(p.brier,(p.p-p.outcome)**2,atol=1e-12)
    np.testing.assert_allclose(p.expected_price,p.reference_close*(1+p.predicted_mean),atol=1e-9)
    np.testing.assert_allclose(p.predicted_median,p.q50,atol=1e-12)
    np.testing.assert_allclose(p.width50,p.q75-p.q25,atol=1e-12)
    np.testing.assert_allclose(p.width80,p.q90-p.q10,atol=1e-12)
    assert (p.p.between(0,1, inclusive='both')&p.origin.gt('2024-12-31')&p.endpoint.lt('2027')).all()
    assert (np.diff(p[['q05','q10','q25','q50','q75','q90','q95']].to_numpy(),axis=1)>=-1e-12).all()
    np.testing.assert_allclose(p[[f'bucket{i}_p' for i in range(7)]].sum(axis=1),1,atol=1e-12)
    b=p[[f'train_bucket{i}_p' for i in range(6)]].to_numpy()
    np.testing.assert_allclose(b.sum(axis=1),1,atol=1e-12)
    np.testing.assert_allclose(np.square(b-np.eye(6)[p.train_bucket_actual]).sum(axis=1),p.train_bucket_brier,atol=1e-12)
    by=(p.groupby(['horizon','cohort','fold','model']).origin.apply(list)).to_dict()
    estimated=[a for a in reg['attempts'] if a['status']=='ok'];fit_files=[a for a in estimated if a.get('artifact')]
    frames={h:cohort_queries(h) for h in y}
    all_dates=pd.read_csv(OUT/'matrix-eligibility.csv',index_col=0)
    extra=pd.read_csv(OUT/'dated-derivatives-inputs.csv',index_col=0)
    cash=pd.read_csv(OUT/'native-equal-weight-closes.csv').set_index('day').sort_index()
    d=extra.reindex(cash.index).shift()
    all_dates['DATED_FUTURES']=d.curve_30d.notna().reindex(all_dates.index).fillna(False)
    all_dates['DATED_STRADDLE']=d.straddle_21day_scale.notna().reindex(all_dates.index).fillna(False)
    receipt_checks=[]
    for item in read('breadth-source-audit.json')['daily_archives']:
        got=verify_source(item,OUT)
        if got:receipt_checks.append(got)
    intra=read('intraday-source-audit.json')
    for key in ['requests','receipts','quarters']:
        if key in intra and isinstance(intra[key],list):
            for item in intra[key]:
                got=verify_source(item,OUT)
                if got:receipt_checks.append(got)
    for path,h in read('dated-derivatives-audit.json')['sources'].items():
        got=verify_source({'path':path,'sha256':h},ROOT)
        if got:receipt_checks.append(got)
    for name,record in read('feature-audit.json')['matrices'].items():
        assert sha(OUT/f'matrices/{name}.csv')==record['sha256']
    for n in ['N_EQ_OFFICIAL','N_EQ_CONTROL','N_INTRA_PANEL','N_INTRA_CONTROL']:
        k='breadth_complete' if n.startswith('N_EQ') else 'intraday_complete'
        dates=p.loc[p.model.eq(n),'origin']
        assert all_dates.loc[dates,k].all()

    def artifact(a):
        h=a['horizon'];s=reg['configurations'][a['model']]
        path=OUT/a['artifact'];assert sha(path)==a['sha256']
        obj=joblib.load(path);training=obj['training'];inner=obj['inner'];validation=obj['validation'];query=obj['query']
        label=y[21 if a['batch']=='transfer' else h]
        assert sorted(query)==sorted(by[h,a['cohort'],a['fold'],a['model']])
        assert label.loc[training,'endpoint'].max()==a['latest_endpoint']<a['cutoff']
        assert label.loc[inner,'endpoint'].max()==a['inner_latest_endpoint']<a['inner_cutoff']==validation[0]
        assert label.loc[validation,'endpoint'].max()<a['cutoff']<=min(query)
        assert len(training)==a['training'] and len(set(training))==len(training)
        assert len(inner)==a['inner_fit'] and len(set(inner))==len(inner)
        if s.get('budget'):assert len(training)==s['budget']
        if a['batch']=='transfer':
            for kind,key in [('model','training'),('inner_model','inner')]:
                for n,dates in obj[kind]['fit_dates'].items():assert set(dates).issubset(obj[key]),n
        else:
            if a['training_metrics'].get('phase_sample_sizes') and s.get('overlap') in ['phase0','phase1']:
                t=a['training_metrics'];assert t['nominal_rows']==t['disjoint_training_windows'] and abs(t['overlap_effective_count']-t['nominal_rows'])<1e-10
            if 'eligible' in s:assert all_dates.loc[training,s['eligible']].all()

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(artifact,fit_files))
    for a in estimated:
        assert len(by[a['horizon'],a['cohort'],a['fold'],a['model']])==a['query_count']
    prediction=p.set_index(['horizon','cohort','model','origin'])
    replay=0
    for path in sorted(OUT.glob('*-laws.jsonl')):
        with path.open(encoding='utf-8') as f:
            for line in f:
                a=json.loads(line);assert a['horizon'] in [5,21]
                row=prediction.loc[a['horizon'],a['cohort'],a['model'],a['origin']]
                law=Distribution.__new__(Distribution)
                law.a=np.asarray(a['atoms'],float);law.w=np.asarray(a['weights'],float)
                # The stored vector is already normalized. Renormalizing across a 50% atom tie can change a quantile.
                assert np.isfinite(law.a).all() and np.isfinite(law.w).all() and np.all(np.diff(law.a)>=0)
                assert np.min(law.a)>-1 and np.min(law.w)>=0 and abs(law.w.sum()-1)<1e-12
                ref=law.score(row.realized_return)
                values=['p','predicted_mean','predicted_median','brier','crps','log_loss','coverage50','coverage80']
                np.testing.assert_allclose([ref[k] for k in values],row[values].to_numpy(float),atol=2e-11,rtol=1e-11,
                                           err_msg=f"{path.name} {a['model']} {a['origin']}")
                if a['model'].startswith('J10_'):
                    assert abs(sum(a['weights'])-1)<1e-12
                replay+=1
    counts={}
    for h in y:
        z=p[(p.horizon==h)&p.model.eq('NEUTRAL')].copy()
        counts[h]={c:{'n':len(g),'disjoint':len(nonoverlap(g))} for c,g in z.groupby('cohort')}
        counts[h]['combined']={'n':len(z),'disjoint':len(nonoverlap(z))}
    assert [counts[h]['combined']['disjoint'] for h in [5,21]]==[53,11]
    old=read('reproduction.json')
    assert old['passed'] and old['V9_forecasts']==1612 and old['V8_leading_forecasts']==184 and old['maximum_discrepancy']<1e-12
    assert read('protected-hash-check.json')['pass']
    diagnostics=pd.read_csv(OUT/'invariance-sentinel.csv')
    assert len(diagnostics)==54 and diagnostics.max_atom_error.max()<2e-10
    copies=[]
    for file in ['invariance','sector-alias']:
        d=pd.read_csv(OUT/f'duplicate-replay/{file}-effects.csv').query('required_invariance')
        assert d.passes_tolerance.all();copies.append(len(d))
    assert sum(copies)==125
    frequency=pd.read_csv(OUT/'bounded-null-selection.csv')
    assert set(frequency.draw)==set(range(-1,16))
    assert read('refresh/refresh-audit.json')['additional_since_v9']==[]
    result={'passed':True,'checked_at':now(),'scored_predictions':len(p),'registered_configurations':len(reg['configurations']),
        'chronological_fit_artifacts_verified':len(fit_files),'failed_or_ineligible_folds_retained':len(reg['attempts'])-len(estimated),
        'complete_atom_laws_recomputed':replay,'source_receipt_hashes_checked':len(set(receipt_checks)),'cohorts':counts,
        'protected_replays':old['V9_forecasts']+old['V8_leading_forecasts'],'legacy_required_copy_checks':sum(copies),
        'V10_copy_and_future_sentinel_checks':len(diagnostics),'checks':[
          'All immutable forecast origin/endpoints and observed returns matched frozen registry',
          'Every documented selection hash, label maturity, inner purge and row cap checked',
          'NSE raw archive checksums, coverage masks and model feature matrices audited',
          'Weighted law probability, point, CRPS, log score and central interval coverage recomputed',
          'No V1–V9 protected artifacts changed',
          'Four post-freeze completed sessions separated from training data']}
    save('verification.json',result)
    print(result,flush=True)


def fixed_curve():
    data=pd.read_csv(OUT/'all-predictions.csv')
    models=data[data.model.str.startswith('LC_')]
    results=[]
    for h,g in models.groupby('horizon'):
        ids=[set(a.origin) for _,a in g.groupby('model')]
        common=set.intersection(*ids)
        for name,q in g[g.origin.isin(common)].groupby('model'):
            results.append({'horizon':h,'model':name,'origins':len(q),'first':q.origin.min(),'last':q.origin.max(),
                            'disjoint':len(nonoverlap(q)),'brier':q.brier.mean(),'crps':q.crps.mean(),
                            'accuracy':((q.p>=.5)==q.outcome).mean()})
    write('learning-curves-fixed-origins.csv',pd.DataFrame(results))


def manifest():
    from .report import NAMES
    names=['NIFTY_V10_RESEARCH.md','README.md','MISSION.md']+[f'V10_{s}.md' for s in NAMES]
    for name in names:
        assert (OUT/name).is_file(),name
    for name in ['NIFTY_V10_RESEARCH.md']+[f'V10_{s}.md' for s in NAMES]:
        import re
        content=(OUT/name).read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)',content):
            if '://' not in link and link!='manifest.json':assert (OUT/link).exists(),(name,link)
    assets={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    code={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(SRC.glob('*.py'))}
    save('manifest.json',{'verified_at':now(),'output_file_count':len(assets),'reports':names,
         'verification_sha256':assets['verification.json'],'files':assets,'research_code':code})
    print('Delivery linked and hashed',len(assets),'files;',len(NAMES),'reports',flush=True)


if __name__=='__main__':
    import sys
    {'data':datachecks,'curve':fixed_curve,'manifest':manifest}[sys.argv[1]]()
