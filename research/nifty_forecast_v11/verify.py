"""Verify immutable parent vintages, chronological fits, complete laws and report links."""
from concurrent.futures import ThreadPoolExecutor
import joblib
from .common import *
from .engine import Distribution,cohort_queries


def protected():
    files=read('protected-inputs.json')['files']
    def check(f):
        path=ROOT/f
        return path.is_file() and sha(path)==files[f]
    with ThreadPoolExecutor(max_workers=6) as p:
        status=list(p.map(check,files))
    changed=[k for k,ok in zip(files,status) if not ok]
    save('protected-hash-verification.json',{'checked':len(files),'changed_or_missing':changed,'passed':not changed})
    assert not changed,changed[:10]
    print(len(files),'protected files verified',flush=True)


def verify():
    q={h:cohort_queries(h).set_index('origin') for h in [5,21]}
    lab={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    p=pd.read_csv(OUT/'all-predictions.csv',float_precision='round_trip')
    assert not p.duplicated(['model','horizon','origin']).any()
    for h,a in p.groupby('horizon'):
        ref=q[h].loc[a.origin]
        np.testing.assert_array_equal(ref.endpoint,a.endpoint)
        np.testing.assert_array_equal(ref.split,a.cohort)
        np.testing.assert_allclose(ref.realized_return,a.realized_return,atol=1e-12,rtol=0)
    np.testing.assert_allclose((p.p-p.outcome)**2,p.brier,atol=1e-12)
    np.testing.assert_allclose(p.reference_close*(1+p.predicted_mean),p.expected_price,atol=1e-8)
    np.testing.assert_allclose(p[[f'train_bucket{i}_p' for i in range(6)]].sum(axis=1),1.,atol=1e-12)
    np.testing.assert_allclose(p.predicted_median,p.q50,atol=1e-12)
    np.testing.assert_allclose(p.q90-p.q10,p.width80,atol=1e-12)
    np.testing.assert_allclose(p.q75-p.q25,p.width50,atol=1e-12)
    assert (np.diff(p[['q05','q10','q25','q50','q75','q90','q95']].to_numpy(),axis=1)>=0).all()
    spec=read('registry.json')
    fitted=[r for r in spec['attempts'] if r['status']=='ok' and 'file' in r]
    def one(r):
        path=OUT/r['file'];assert sha(path)==r['sha256']
        obj=joblib.load(path);y=lab[r['horizon']]
        assert len(set(obj['train']))==len(obj['train'])==r['training']
        assert len(set(obj['inner_dates']))==len(obj['inner_dates'])
        assert y.loc[obj['train'],'endpoint'].max()==r['training_endpoint']<r['cutoff']<=min(obj['query'])
        assert y.loc[obj['inner_dates'],'endpoint'].max()==r['inner_endpoint']<r['inner_cutoff']==obj['validation'][0]
        assert y.loc[obj['validation'],'endpoint'].max()<r['cutoff']
        if spec['configurations'][r['model']].get('small_disjoint'):
            pos={d:i for i,d in enumerate(y.index)}
            assert min(np.diff([pos[d] for d in obj['train']]))>=r['horizon']
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(one,fitted))
    weights=0
    for r in spec['attempts']:
        if not r['batch'].startswith('ensemble'):continue
        y=lab[r['horizon']]
        for v in r['conditional_weights'].values():
            assert all(a>=0 for a in v['weights']) and abs(sum(v['weights'])-1)<1e-11
            if v['dates']:assert y.loc[v['dates'],'endpoint'].max()<r['cutoff']
            weights+=1
    keys=['horizon','model','origin']
    index=p.set_index(keys)
    replayed=0
    for path in sorted(OUT.glob('*-laws.jsonl')):
        with path.open(encoding='utf-8') as f:
            for line in f:
                a=json.loads(line)
                law=Distribution.__new__(Distribution)
                law.a=np.asarray(a['atoms']);law.w=np.asarray(a['weights'])
                assert np.isfinite(law.a).all() and np.isfinite(law.w).all() and abs(law.w.sum()-1)<1e-12
                assert min(law.a)>-1 and min(law.w)>=0 and (np.diff(law.a)>=0).all()
                row=index.loc[a['horizon'],a['model'],a['origin']]
                score=law.score(row.realized_return)
                metrics=['brier','crps','p','predicted_mean','predicted_median','coverage50','coverage80','log_loss']
                np.testing.assert_allclose([score[m] for m in metrics],row[metrics].to_numpy(float),atol=1e-11,rtol=1e-11,
                                           err_msg=f"{a['model']} {a['origin']}")
                assert a['endpoint']==row.endpoint
                replayed+=1
    old=read('v10-replay.json');assert old['passed']
    assert read('reproduction.json',OUT/'replay/older')['passed']
    assert read('protected-hash-verification.json')['passed']
    f=pd.read_csv(OUT/'invariance-and-sentinel.csv');assert len(f)==24 and f.max_atom_delta.max()<1e-10
    for n,d in read('feature-definitions.json').items():assert sha(OUT/f'matrices/{n}.csv')==d['hash']
    save('verification.json',{'passed':True,'predictions':len(p),'model_configurations':len(spec['configurations']),'artifact_fits':len(fitted),
         'weight_vectors':weights,'complete_laws':replayed,'legacy_v10_refits':sum(g['rows'] for g in old['checks']),
         'legacy_v10_mixtures':old['mixtures'],'invariance_future_sentinel':len(f),'max_sentinel_error':f.max_atom_delta.max(),
         'unestimated':sum(r['status']!='ok' for r in spec['attempts']),
         'checks':['Matched all scored endpoints and returns','Recomputed stored atoms and weights','Verified fit hashes and date purges',
                   'Verified past-only mixture fitting','Verified V1–V10 protected hashes','Kept November 17 frozen vintage separate']})
    print('V11 verified',len(p),'forecast rows,',replayed,'complete laws and',len(fitted),'chronological fit artifacts',flush=True)


def delivery():
    from .reports import TITLES
    files=[f'V11_{k}.md' for k in TITLES]
    for f in files+['README.md','MISSION.md','NIFTY_V11_RESEARCH.md','verification.json']:
        assert (OUT/f).is_file(),f
    import re
    for f in files+['NIFTY_V11_RESEARCH.md','README.md']:
        for link in re.findall(r'\]\(([^)]+)\)',(OUT/f).read_text(encoding='utf-8')):
            if '://' not in link and link!='manifest.json':assert (OUT/link).exists(),(f,link)
    directory={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    save('manifest.json',{'checked':now(),'reports':files,'files':directory,'research_code':{p.relative_to(ROOT).as_posix():sha(p) for p in SRC.glob('*.py')}})
    print(len(files),'verified reports;',len(directory),'hashed delivery files',flush=True)


if __name__=='__main__':
    import sys
    {'protected':protected,'verify':verify,'delivery':delivery}[sys.argv[1]]()
