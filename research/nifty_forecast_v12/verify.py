"""Independently verify dates, finite probability laws, priced densities and delivery."""
from concurrent.futures import ThreadPoolExecutor
import joblib
from .common import *
from research.nifty_forecast_v9.run_models import cohort_queries

SCORES=['p','predicted_mean','predicted_median','brier','crps','log_loss','coverage50','coverage80','width80']


def run():
    p=pd.read_csv(OUT/'all-predictions.csv',float_precision='round_trip')
    q={h:cohort_queries(h).set_index('origin') for h in [5,21]}
    y={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    assert not p.duplicated(['horizon','model','origin']).any()
    assert p.origin.str[:4].isin(['2025','2026']).all() and p.endpoint.le(FREEZE).all()
    for h,a in p.groupby('horizon'):
        first=q[h].loc[a.origin]
        np.testing.assert_array_equal(first.endpoint,a.endpoint)
        np.testing.assert_array_equal(first.split,a.cohort)
        np.testing.assert_allclose(first.realized_return,a.realized_return,atol=1e-12,rtol=0)
    np.testing.assert_allclose((p.p-p.outcome)**2,p.brier,atol=1e-12)
    np.testing.assert_allclose(p.reference_close*(1+p.predicted_mean),p.expected_price,atol=1e-8)
    np.testing.assert_allclose(p.q90-p.q10,p.width80,atol=1e-12)
    np.testing.assert_allclose(p.q75-p.q25,p.width50,atol=1e-12)
    np.testing.assert_allclose(p[[f'train_bucket{i}_p' for i in range(6)]].sum(axis=1),1.,atol=1e-12)
    assert (np.diff(p[['q05','q10','q25','q50','q75','q90','q95']].to_numpy(),axis=1)>=0).all()
    original=read('registry.json')
    rows=[r for r in original['attempts'] if r['status']=='ok' and 'file' in r]
    objects={r['file']:r for r in rows}
    forecast_slots={k:g.origin.tolist() for k,g in p.groupby(['horizon','cohort','fold','model'])}
    def check_fit(row):
        path=OUT/row['file'];assert sha(path)==row['sha256']
        g=joblib.load(path);label=y[row['horizon']]
        tr=g['training'];assert len(tr)==len(set(tr))==row['training']
        if len(tr):assert label.loc[tr,'endpoint'].max()<row['cutoff']
        assert row['cutoff']<=min(g['query'])
        if 'inner_dates' in g:
            assert label.loc[g['inner_dates'],'endpoint'].max()<row['inner_cutoff']==g['validation'][0]
            assert label.loc[g['validation'],'endpoint'].max()<row['cutoff']
        else:assert forecast_slots[row['horizon'],row['cohort'],row['fold'],row['model']]==g['query']
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(check_fit,objects.values()))
    for r in rows:
        if 'last_endpoint' in r:assert r['last_endpoint']<r['cutoff'] and r['inner_last_endpoint']<r['inner_cutoff']
        elif r['training']:assert r['training_last_endpoint']<r['cutoff']
    combos=read('ensemble-ledger.json')
    for r in combos:
        w=np.asarray(r['weights']);assert np.isfinite(w).all() and (w>=0).all() and abs(w.sum()-1)<1e-11
        tr=r['fit_origins']
        if tr:assert y[r['horizon']].loc[tr,'endpoint'].max()<r['cutoff']
    ix=p.set_index(['horizon','model','origin'])
    covered=set();parts=[]
    all_keys=set(ix.index.tolist())
    for batch in ['phase','market','priced','ensemble']:
        rec=read(f'{batch}-laws.json')
        file=OUT/rec['path']
        assert sha(file)==rec['sha256']
        part=0
        for (h,n,day,end),d in bundle_entries(file):
            key=(int(h),n,day)
            assert key not in covered and key in all_keys
            assert (np.diff(d.a)>=0).all() and np.isfinite(d.a).all() and np.isfinite(d.w).all()
            assert min(d.a)>-1 and min(d.w)>=0 and abs(d.w.sum()-1)<1e-12
            got=ix.loc[key]
            assert got.endpoint==end
            s=d.score(got.realized_return)
            np.testing.assert_allclose([s[c] for c in SCORES],got[SCORES].to_numpy(float),rtol=1e-11,atol=2e-11,
                                       err_msg=f'{n} {day} {h}')
            covered.add(key);part+=1
        assert part==rec['forecasts']
        parts.append(rec)
    assert covered==all_keys
    save('full-law-archive.json',{'forecasts':len(covered),'parts':parts,'key_order':['horizon','model','origin','endpoint'],
          'storage':'For row i use atoms and weights from offsets[i] through offsets[i+1] (exclusive). Risk-neutral priced diagnostic is identified separately in registry.'})

    options=read('options-source-audit.json')
    a=pd.read_csv(OUT/'surface-quality.csv',low_memory=False)
    accepted=a[a.density_status.eq('accepted')].set_index(['day','expiry','method'])
    # Statistical laws and priced-law QC use separate artifacts and verification.
    count=0;max_moment=0.
    for k,d in bundle_entries(OUT/'option-density-atoms.npz'):
        row=accepted.loc[k]
        assert k[0]<k[1]<= '2026-12-31'
        assert min(d.w)>=0 and abs(d.w.sum()-1.)<1e-12 and min(d.a)>-1
        max_moment=max(max_moment,abs(d.w@d.a))
        assert abs(d.w@d.a)<1e-7 and row.external_mass<=.38+1e-12 and row.mass_shift<=.14+1e-12
        count+=1
    assert count==len(accepted)
    clock=pd.read_csv(OUT/'horizon-alignment.csv')
    series=matrix('official-index-closes.csv',V11).index
    positions={d:i for i,d in enumerate(series)}
    assert (clock.origin.map(positions)-clock.option_source_day.map(positions)==clock.source_lag_sessions).all()
    assert clock.loc[~clock.version.eq('SAME_CLOSE'),'option_source_day'].lt(clock.loc[~clock.version.eq('SAME_CLOSE'),'origin']).all()
    n=p[p.model.eq('Q12_NATURALLY_ALIGNED')]
    if len(n):
        check=clock.loc[clock.version.eq('NATURAL'),['horizon','origin','expiry']].merge(n,on=['horizon','origin'])
        assert check.expiry.eq(check.endpoint).all()
    ext=pd.read_csv(OUT/'external-publication-alignment.csv')
    assert ext.source_day.lt(ext.origin).all()
    assert pd.to_datetime(ext.assumed_available,utc=True,format='mixed').le(pd.to_datetime(ext.decision,utc=True,format='mixed')).all()
    for rec in read('feature-receipts.json')['files']:assert sha(OUT/rec['path'])==rec['hash']
    for doc in read('publication-source-receipts.json'):
        if 'sha256' in doc:assert sha(OUT/doc['path'])==doc['sha256']
    copy=pd.read_csv(OUT/'ensemble-exact-invariance.csv')
    new=pd.read_csv(OUT/'market-timing-and-copy-sentinels.csv')
    assert copy.exact.all() and new.maximum_atom_delta.max()<1.e-10
    old=read('protected-verification.json')
    assert old['passed'] and read('exact-replay.json')['passed'] and read('legacy-breadth-replay.json')['passed']
    save('verification.json',{'passed':True,'predictions':len(p),'complete_forecasts_recomputed':len(covered),
          'priced_expiry_distributions_checked':count,'max_priced_forward_moment_error':max_moment,'distinct_fit_artifacts':len(objects),
          'attempts_with_coefficients':len(rows),'simplex_fit_records':len(combos),'ensemble_exact_copy_checks':len(copy),
          'casewise_timing_and_copy_checks':len(new),'protected_files':old['checked'],
          'daily_options_archives':options['sessions'],'external_timestamp_rows':len(ext),'source_alignment_rows':len(clock),
          'unestimated_folds':sum(r['status']!='ok' for r in original['attempts']),
          'checks':['Complete endpoint outcomes on frozen origins','Forecast points, masses, quantiles and interval scores recomputed',
                    'Option density normalization and martingale/price-fit constraints checked',
                    'Historical source lag and earlier realized maturity independently checked','V1–V11 manifest files matched']})
    print('Verified',len(covered),'complete forecasting laws and',count,'priced expiry laws',flush=True)


def delivery():
    import re
    from .reports import TITLES
    reports=[f'V12_{i}.md' for i in TITLES]
    for name in reports+['NIFTY_V12_RESEARCH.md','README.md','MISSION.md','verification.json']:
        assert (OUT/name).is_file(),name
    for name in reports+['NIFTY_V12_RESEARCH.md','README.md']:
        for link in re.findall(r'\]\(([^)]+)\)',(OUT/name).read_text(encoding='utf-8')):
            if '://' not in link and link!='manifest.json':assert (OUT/link).exists(),(name,link)
    fs={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    save('manifest.json',{'verified_at':now(),'reports':reports,'files':fs,
          'research_code':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(SRC.glob('*.py'))}})
    print(len(reports),'verified reports and',len(fs),'hashed artifacts',flush=True)


if __name__=='__main__':
    import sys
    {'verify':run,'delivery':delivery}[sys.argv[1]]()
