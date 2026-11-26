"""Validate chronology, stored law weights, source integrity and deliverable links."""
import re

from .common import *
from .laws import loaded,piece


def laws():
    results=[]
    for tab,book,which in [('v23-return-cases.csv.gz','v23-return-laws.npz','model'),
                           ('matched-expert-cases.csv.gz','matched-expert-laws.npz','expert')]:
        z=csv(tab)
        a,w,e=loaded(OUT,book)
        assert len(z)+1==len(e) and e[-1]==len(a)==len(w) and np.array_equal(z.law,np.arange(len(z)))
        assert (np.diff(e)>0).all() and z.day.between(FIRST,FREEZE).all() and z.target.between(FIRST,FREEZE).all()
        assert z.mature_ns.gt(z.issue_ns).all()
        assert not z.duplicated(['day','horizon','clock',which]).any()
        if 'last_mature_ns' in z:
            assert z.last_mature_ns.lt(z.issue_ns).all()
            np.testing.assert_allclose(z.expected_index,z.reference*(1+z['mean']),rtol=0.,atol=1.e-8)
        np.testing.assert_allclose(np.add.reduceat(w,e[:-1]),1.,rtol=0.,atol=1.e-12)
        np.testing.assert_allclose(np.add.reduceat(w*a,e[:-1]),z['mean'],rtol=0.,atol=1.e-11)
        np.testing.assert_allclose(np.add.reduceat(w*(a>0),e[:-1]),z.p,rtol=0.,atol=1.e-11)
        np.testing.assert_allclose((z.p-z.actual.gt(0))**2,z.brier,rtol=0.,atol=1.e-12)
        q=z[['q1','q5','q10','q25','q50','q75','q90','q95','q99']].to_numpy()
        assert (np.diff(q,axis=1)>=-1.e-12).all()
        sample=z.groupby(['horizon','clock',which]).sample(n=3,random_state=SEED)
        for r in sample.itertuples(index=False):
            x=piece((a,w,e),r.law)
            assert abs(x.crps(r.actual)-r.crps)<2.e-10
        for h in HORIZONS:
            for clock in ('native_0910','preauction_0855'):
                x=z[z.horizon.eq(h)&z.clock.eq(clock)]
                assert x.groupby('cohort').day.nunique().reindex(['early','later']).tolist()==list(COHORTS[h][:2])
        results.append(dict(case_file=tab,laws=len(z),atoms=len(a),sampled_crps_replays=len(sample)))
    w=csv('ensemble-date-weights.csv.gz')
    assert w.last_mature_ns.lt(w.issue_ns).all() and w.weight.ge(0).all()
    np.testing.assert_allclose(w.groupby(['horizon','clock','day','method']).weight.sum(),1.,atol=1.e-10,rtol=0.)
    return results


def path_laws():
    m=csv('path-donor-members.csv.gz')
    assert m.source_mature_ns.lt(m.issue_ns).all() and m.target_day.le(FREEZE).all()
    key=['horizon','day','model']
    assert m.groupby(key).size().eq(24).all()
    assert m.groupby(key+['episode']).size().eq(1).all()
    np.testing.assert_allclose(m.groupby(key).weight.sum(),1.,atol=1.e-12,rtol=0.)
    assert m.loc[m.model.str.startswith('mixed_strict')&m.market.ne('india'),'verified_source'].all()
    a=m[m.model.eq('india_state_matched')].sort_values(['horizon','day','slot'])
    c=a.episode.to_numpy()
    for choose in ('mixed_broad','mixed_strict','mixed_vol_only','mixed_random_foreign','mixed_omit_asia','india_vol_same_episodes'):
        b=m[m.model.eq(choose)].sort_values(['horizon','day','slot'])
        assert np.array_equal(c,b.episode)
    scores=csv('v23-path-cases.csv.gz')
    assert scores.last_mature_ns.lt(scores.issue_ns).all()
    same=scores[~scores.model.isin(('india_state_widened',))]
    np.testing.assert_allclose(same.rv_mean,same.anchor,atol=3.e-10,rtol=0.)
    quality=csv('precision-path-index.csv')
    with np.load(OUT/'precision-joint-paths.npz') as p:
        for q in quality.itertuples(index=False):
            z=p[q.key]
            assert z.shape[1:]==(q.horizon,4)
            assert np.isfinite(z).all()
            assert np.all(z[:,:,1]>=np.maximum(z[:,:,0],z[:,:,3])-1.e-7)
            assert np.all(z[:,:,2]<=np.minimum(z[:,:,0],z[:,:,3])+1.e-7)
    large=csv('larger-simulation-path-cases.csv.gz')
    assert large.last_training_maturity.lt(large.issue_ns).all()
    assert set(large.n_draws)=={1024,4096} and set(large.seed)=={1,2}
    return dict(donor_memberships=len(m),scored_paths=len(scores),saved_joint_laws=len(quality),higher_budget_cases=len(large))


def provenance():
    p=read('predecessor-verification.json')
    assert sha(V22/'manifest.json')==p['manifest_sha256']
    v=read('manifest.json',V22)
    for root,part in ((V22,'files'),(ROOT,'code')):
        for r in v[part]:
            assert sha(root/r['path'])==r['sha256'],r['path']
    sources=csv('master-forecast-source-catalog.csv')
    for r in sources.itertuples(index=False):
        assert sha(ROOT/r.file)==r.sha256,r.file
    q=read('foreign-source-receipts.json')
    for r in q['sources']:
        if r.get('file'):
            assert sha(OUT/r['file'])==r['sha256']
    schema=read('master-archive-schema.json')
    count=0
    for f in schema['files']:
        for frame in pd.read_csv(OUT/f,usecols=['origin','target_session'],chunksize=70000):
            assert frame.origin.between(FIRST,FREEZE).all() and frame.target_session.between(FIRST,FREEZE).all()
            count+=len(frame)
    assert count==schema['historical_records']
    return dict(v22_hashed_files=len(v['files']),older_source_catalog_verified=len(sources),archive_date_scoped_rows=count)


def forward():
    a=read('forward-ledger.json')
    old=read('forward-ledger.json',V22)
    preserved=0
    for b in ('original_issues','inherited_v19','inherited_v20'):
        for x,y in zip(a[b],old[b],strict=True):
            for key in ('horizon','target_sessions','reference_close','issue_hash','sha256','law_sha256','issued','issued_at','original_probabilities'):
                assert x.get(key)==y.get(key),(b,key)
            assert x['target_sessions'][-1]<=LAST
            preserved+=1
    assert preserved==13
    fx=csv('forward/completed-foreign-marks.csv.gz')
    rec=read('forward/foreign-receipt.json')
    assert len(fx)==rec['rows']
    assert fx.day.gt(FREEZE).all() and fx.day.le(LAST).all()
    assert pd.to_datetime(fx.available,utc=True).le(pd.Timestamp(rec['captured_at'])).all()
    for r in rec['sources']:
        if r.get('file'):
            assert sha(OUT/r['file'])==r['sha256']
    for v in a['new_issues']:
        cut=pd.Timestamp(v['decision_cutoff'])
        at=pd.Timestamp(v['issued_at'])
        assert 0<=(at-cut).total_seconds()<=75
        assert v['target_sessions'][0]==cut.date().isoformat() and v['target_sessions'][-1]<=LAST
        assert sha(OUT/v['law_file'])==v['law_sha256']
        assert sha(SRC/'forward_issue.py')==v['architecture_sha256']
        expected=hashlib.sha256(json.dumps(v['config'],sort_keys=True,default=str).encode()).hexdigest()
        assert expected==v['configuration_sha256']
        with np.load(OUT/v['law_file']) as z:
            w=z['weights'];r=z['atoms']
            np.testing.assert_allclose(w.sum(),1.,atol=1.e-12,rtol=0.)
            np.testing.assert_allclose(w@(r>0),v['p_up'],atol=1.e-12,rtol=0.)
            if 'ohlc_log_relative' in z.files:
                donor=csv(f"forward/laws/{v['model']}-donors.csv")
                assert donor.mature_ns.lt(cut.value).all()
                np.testing.assert_allclose(np.expm1(z['ohlc_log_relative'][:,-1,3]),r,atol=1.e-12,rtol=0.)
            elif 'close_log_returns' in z.files:
                assert sha(OUT/v['source'])==v['source_sha256']
                state=read(v['source'])
                assert pd.Timestamp(state['captured_at'])<=cut
                assert state['origin']<cut.date().isoformat()
                np.testing.assert_allclose(np.expm1(z['close_log_returns'].sum(axis=1)),r,atol=1.e-12,rtol=0.)
                np.testing.assert_allclose(np.sqrt(252*(z['close_log_returns']**2).mean(axis=1)),z['annualized_volatility'],atol=1.e-12,rtol=0.)
            else:
                source=read(v['source'])
                assert pd.Timestamp(source['receipt']['received'])<=cut
                capture=read('forward/opening-capture.json')
                observed=[r for r in capture['attempts'] if r.get('file')==v['source']]
                assert len(observed)==1
                assert pd.Timestamp(observed[0]['selected_morning_model_availability'])<=cut
    native=read('forward/native-source-readiness.json')
    for r in native['authenticated_options']:
        if 'file' in r:
            assert sha(OUT/r['file'])==r['sha256']
    return dict(preserved_issues=preserved,genuine_new_issues=len(a['new_issues']),completed_foreign_forward_marks=len(fx))


def run():
    stat=dict(law_replays=laws(),**path_laws(),**provenance(),**forward())
    r=read('registration.json')
    assert len(r['hypotheses'])==12
    docs=[OUT/f'V23_{name}.md' for name in REPORTS]+[OUT/'NIFTY_V23_RESEARCH.md',OUT/'README.md']
    for p in docs:
        body=p.read_text(encoding='utf-8')
        assert len(body)>880,p.name
        for key in re.findall(r'\]\(([^)]+)\)',body):
            if not key.startswith(('http','https','#')) and not key=='manifest.json':
                assert (OUT/key).is_file(),(p.name,key)
    for p in SRC.glob('*.py'):
        compile(p.read_text(encoding='utf-8'),str(p),'exec')
    rep=stat|dict(reports=len(REPORTS),figures=3,python_modules=len(list(SRC.glob('*.py'))),registered_hypotheses=12,verified_at=now())
    save('verification-receipt.json',rep)
    files=[dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json']
    code=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(SRC.glob('*.py'))]
    save('manifest.json',dict(stats=rep,files=files,code=code))
    print(json.dumps(rep,indent=2),flush=True)


if __name__=='__main__':
    run()
