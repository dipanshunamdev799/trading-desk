"""Verify output scope, current forecast clocks, law consistency and artifact integrity."""
import re

from .common import *
from .india import load_laws,from_book
from .reference import NATIVE
from research.nifty_forecast_v17.weekly import evaluate


def verify_india():
    z=csv('india-forecast-cases.csv.gz')
    arrays=load_laws(OUT,'india-forecast-laws.npz')
    a,w,e=arrays
    assert len(z)+1==len(e) and np.array_equal(z.law,np.arange(len(z))) and e[-1]==len(a)==len(w)
    assert (np.diff(e)>0).all() and z.last_mature_ns.lt(z.issue_ns).all()
    assert z.day.ge(FIRST).all() and z.target_end.le(FREEZE).all()
    np.testing.assert_allclose(np.add.reduceat(w,e[:-1]),1.,atol=1.e-12,rtol=0.)
    np.testing.assert_allclose(np.add.reduceat(w*a,e[:-1]),z['mean'],atol=1.e-11,rtol=0.)
    np.testing.assert_allclose(np.add.reduceat(w*(a>0),e[:-1]),z.p,atol=1.e-12,rtol=0.)
    np.testing.assert_allclose(z.reference_close*(1.+z['mean']),z.expected_index,atol=2.e-8,rtol=0.)
    assert z.filter(regex=r'^q[0-9]+$').diff(axis=1).iloc[:,1:].ge(-1.e-12).all(axis=None)
    checks=0
    for h in ORIGINAL:
        for clock in ('preauction_0855','native_0910'):
            q=z[z.horizon.eq(h)&z.cutoff.eq(clock)]
            expected=EXPECTED[h]
            ref=q[q.model.eq('archived_same_clock' if clock=='preauction_0855' else 'exact_v14')]
            assert ref.groupby('cohort').day.nunique().reindex(['early','later']).tolist()==list(expected[:2])
            for r in q.groupby('model').sample(n=4,random_state=SEED).itertuples(index=False):
                law=from_book(arrays,r.law)
                res=evaluate(*law,r.actual)
                for k in ('p','crps','brier','mean','log_loss','median'):
                    assert abs(res[k]-getattr(r,k))<2.e-9,(k,r.day,r.model)
                checks+=1
            if clock=='native_0910':
                for key,(b,c) in NATIVE[h].items():
                    p=q[q.model.eq(key)]
                    assert (abs(p.brier.mean()-b)<6.e-7 and abs(p.crps.mean()-c)<6.e-7)
    return dict(india_weighted_laws=len(z),india_sampled_complete_proper_score_replays=checks,india_atom_weights=len(a))


def verify_international():
    f=csv('international-feature-panel.csv.gz')
    t=csv('international-target-panel.csv.gz')
    assert f.day.between(FIRST,FREEZE).all() and t.day.between(FIRST,FREEZE).all()
    assert t.target_day.dropna().between(FIRST,FREEZE).all()
    assert f.last_local_available_ns.lt(f.issue_ns).all()
    assert not f.duplicated(['code','day']).any() and not t.duplicated(['row','horizon']).any()
    cover=csv('market-universe-audit.csv')
    assert int(cover.primary_eligible.sum())==f.code.nunique()
    assert cover.loc[cover.primary_eligible,'convention'].eq('local price index').all()
    timing={};total=0;replays=0
    for h in HORIZONS:
        cols=['model','code','clock_ns','last_train_ns','mature_ns','issue_ns','day','target_day',
              'law','center_normalized','horizon_scale','p','mean','brier','ret']
        g=csv(f'market-forecast-cases-{h}.csv.gz',usecols=cols)
        assert g.target_day.between(FIRST,FREEZE).all() and g.mature_ns.gt(g.issue_ns).all()
        assert g.last_train_ns.lt(g.clock_ns).all() and g.clock_ns.le(g.issue_ns).all()
        q=csv(f'international-fit-receipts-{h}.csv')
        assert q.n_later_than_cut.eq(0).all() and q.last_mature.lt(q.fit_cut_ns).all()
        strict=q[q.model.eq('loco_transfer')&q.holdout.ne('india')]
        assert strict.n_markets.max()<=f.code.nunique()-2
        assert q[q.model.eq('loco_transfer')&q.holdout.eq('india')].n_markets.max()==f.code.nunique()-1
        lo=q[q.model.eq('loro_transfer')]
        assert lo.n_markets.max()<f.code.nunique()-1
        shape=np.load(OUT/f'market-forecast-atoms-{h}.npz')['s']
        s=g.sample(min(1500,len(g)),random_state=SEED)
        atoms=np.expm1(np.clip(s.horizon_scale.to_numpy()[:,None]*(shape[s.law]+s.center_normalized.to_numpy()[:,None]),-1.9,1.5))
        np.testing.assert_allclose((atoms>0).mean(axis=1),s.p,atol=.000001,rtol=0)
        np.testing.assert_allclose(atoms.mean(axis=1),s['mean'],atol=2.e-9,rtol=0)
        np.testing.assert_allclose((s.p-s.ret.gt(0))**2,s.brier,atol=3.e-10,rtol=0)
        timing[h]=dict(case_count=len(g),fit_certificates=len(q),strict_reserved_cutoff=True)
        total+=len(g);replays+=len(s)
    return dict(primary_markets=f.code.nunique(),market_origins=len(f),target_tasks=len(t),international_forecast_cases=total,
                international_laws_sample_replays=replays,by_horizon=timing)


def verify_paths():
    catalogue=csv('analogue-law-atlas.csv')
    member=csv('analogue-law-members.csv.gz')
    prior=csv('india-calibrated-risk-path-recipes.csv.gz')
    sample=member.merge(catalogue[['law','horizon','issue_ns','model','path_from','path_to','max_week_weight']],on='law',validate='m:1')
    assert sample.mature_ns.lt(sample.issue_ns).all() and not sample.duplicated(['law','row']).any()
    assert (sample.origin<sample.endpoint).all()
    weights=member.groupby('law').weight.sum()
    np.testing.assert_allclose(weights,1.,atol=1.e-12,rtol=0.)
    limited=sample[sample.model.ne('foreign_uncapped')]
    assert limited.groupby(['law','episode']).size().le(2).all()
    assert limited.groupby(['law','episode','market']).size().le(1).all()
    assert np.allclose(limited.groupby('law').episode.nunique().rdiv(1.),limited.groupby('law').max_week_weight.first(),atol=1.e-11)
    for h in ORIGINAL:
        target=catalogue[catalogue.horizon.eq(h)]
        p=np.load(OUT/'analogue-observed-path-laws.npz')[f'p{h}']
        assert p.shape==(int(target.members.sum()),h,4)
        assert np.min(p[:,:,1]-np.maximum(p[:,:,0],p[:,:,3]))>=-2.e-7 and np.min(np.minimum(p[:,:,0],p[:,:,3])-p[:,:,2])>=-2.e-7
        v=sample[sample.horizon.eq(h)].sort_values(['law','order'])
        assert np.array_equal(v.path_from.to_numpy()+v.order.to_numpy(),np.arange(len(p)))
        np.testing.assert_allclose(np.expm1(p[:,-1,3].astype(float)),v.mapped_terminal,atol=4.e-8,rtol=1.e-6)
        rr=prior[prior.horizon.eq(h)]
        scaled=np.load(OUT/'india-calibrated-risk-ohlc-laws.npz')[f'p{h}']
        assert scaled.shape==(int((rr.path_to-rr.path_from).sum()),h,4)
        assert np.min(scaled[:,:,1]-np.maximum(scaled[:,:,0],scaled[:,:,3]))>=-2.e-7
        assert np.min(np.minimum(scaled[:,:,0],scaled[:,:,3])-scaled[:,:,2])>=-2.e-7
    return dict(analogue_laws=len(catalogue),analogue_paths=len(member),risk_path_laws=len(prior))


def verify_sources_and_forward():
    m=read('manifest.json',V21)
    for root,recs in ((V21,m['files']),(ROOT,m['code'])):
        for r in recs:
            assert sha(root/r['path'])==r['sha256'],r['path']
    hist=read('international-source-receipt.json')
    for r in hist['sources']:
        if r.get('file'):
            assert sha(OUT/r['file'])==r['sha256']
    for r in read('nse-historical-source-chain.json')['files']:
        assert sha(ROOT/r['file'])==r['sha256']
    f=read('forward-ledger.json')
    old=read('forward-ledger.json',V21)
    for key in ('original_issues','inherited_v19','inherited_v20'):
        for a,b in zip(f[key],old[key],strict=True):
            for tag in ('target_sessions','reference_close','key','issue_hash','law_sha256','sha256'):
                assert a.get(tag)==b.get(tag)
            assert a['target_sessions'][-1]<=LAST
    for r in f['archive_receipts']:
        assert sha(ROOT/r['path'])==r['sha256']
    source_files=read('forward-input-receipts.json')
    live=csv('forward/eligible-foreign-completed-sessions.csv.gz')
    assert len(live)==source_files['n_eligible_international']
    assert live.day.gt(FREEZE).all() and live.day.le(LAST).all()
    assert (pd.to_datetime(live.available,utc=True)<=pd.to_datetime(live.captured_at,utc=True)).all()
    staged=read('forward/staged-model-configurations.json')
    assert len(staged['rows'])==f['staged_model_count']
    for row in staged['rows']:
        assert sha(ROOT/row['implementation'])==row['implementation_sha256']
        assert sha(ROOT/row['historical_source'])==row['historical_source_sha256']
        exact={k:row[k] for k in ('short','horizon','clock','implementation','implementation_sha256','input_requirements',
                        'historical_source','historical_source_sha256','classification','law_integrity')}
        assert hashlib.sha256(json.dumps(exact,sort_keys=True).encode()).hexdigest()==row['configuration_sha256']
    return dict(v21_artifacts_verified=len(m['files']),v21_code_files_verified=len(m['code']),
                source_receipts=len(hist['sources']),forward_issue_count=sum(len(f[k]) for k in ('original_issues','inherited_v19','inherited_v20')),
                v22_new_forward_issues=len(f['new_issues']),forward_foreign_marks=len(live))


def run():
    stats=verify_india()|verify_international()|verify_paths()|verify_sources_and_forward()
    documents=[OUT/f'V22_{name}.md' for name in REPORTS]+[OUT/'NIFTY_V22_RESEARCH.md',OUT/'README.md']
    for p in documents:
        body=p.read_text(encoding='utf-8')
        assert len(body)>=800,p.name
        for ref in re.findall(r'\]\(([^)]+)\)',body):
            if not ref.startswith(('http://','https://','#')) and ref!='manifest.json':
                assert (OUT/ref).is_file(),(p.name,ref)
    for p in SRC.glob('*.py'):
        compile(p.read_text(encoding='utf-8'),str(p),'exec')
    out=stats|dict(verified_at=now(),reports=len(REPORTS),figures=2,local_links_verified=True)
    save('verification-receipt.json',out)
    work=[dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
          for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json']
    code=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(SRC.glob('*.py'))]
    save('manifest.json',dict(stats=out,files=work,code=code))
    print(json.dumps(out,indent=2),flush=True)


if __name__=='__main__':
    run()
