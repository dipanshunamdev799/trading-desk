"""Verify complete V16 deliverables and freeze the artifact checksums."""
import re
from urllib.parse import unquote

from .common import *
from .model import quantify


def verification():
    historical=read('v15-opening-reproduction.json')
    clock=read('point-in-time-verification.json')
    leak=read('no-future-and-copy-verification.json')
    old=read('predecessor-protection.json')
    assert historical['passed'] and clock['passed'] and leak['passed'] and old['valid']
    report_technical={}
    protected_files=set()
    objects=read('path-archive.json')
    table=pd.read_csv(V15/'original-windows.csv').set_index(['horizon','origin'])
    h,n=0,0
    for v in objects['files']:
        h+=1
        k=(v['horizon'],v['origin'])
        row=table.loc[k]
        assert v['target']==row.target and v['origin']<v['day']<=v['target']<=FREEZE
        assert v['reference_close']==row.origin_reference
        assert sha(OUT/v['file'])==v['sha256']
        key=(v['original_v14'],v['v14_sha256'])
        if key not in protected_files:
            assert sha(V14/key[0])==key[1]
            protected_files.add(key)
        with np.load(OUT/v['file'],allow_pickle=False) as z:
            for name in objects['joint_models']:
                a=z[name]
                assert a.shape==(PATH_N,v['horizon'],4) and np.isfinite(a).all()
                assert (a[:,:,1]>=np.maximum(a[:,:,0],a[:,:,3])).all()
                assert (a[:,:,2]<=np.minimum(a[:,:,0],a[:,:,3])).all()
                n+=1
            assert z['simulated_analogue_states'].shape==(PATH_N,v['horizon'],4)
    assert h==len(table)==sum(EXPECTED.values())
    report_technical.update(original_windows=h,verified_joint_laws=n,scenario_count_per_law=PATH_N,
                              unique_protected_path_files=len(protected_files))
    s=pd.read_csv(OUT/'path-scores.csv.gz',usecols=['horizon','origin','model','target','actual_endpoint','p_up'])
    assert len(s)==h*(len(objects['joint_models'])+len(objects['protected_joint_models']))
    assert s.p_up.between(0,1).all()
    p=pd.read_csv(OUT/'path-passage-scores.csv.gz')
    assert len(p)==len(s)*10
    assert p.p.between(0,1).all() and p.p_first_session.le(p.p).all()
    assert p.loc[p.actual_first.eq(1),'conditional_brier'].isna().all()
    assert p.actual_first.le(p.horizon+1).all()
    report_technical.update(protected_and_new_path_scores=len(s),barrier_rows=len(p))
    archive={}
    for key in ('opening','decay','network'):
        for q in sorted(OUT.glob(key+'-*-scores.csv.gz')):
            tag=q.name.removesuffix('-scores.csv.gz')
            forecast=pd.read_csv(q)
            assert len(forecast)>0 and forecast.last_training_end.lt(forecast.day).all()
            assert forecast.day.le(forecast.target_date).all() and forecast.target_date.le(FREEZE).all()
            assert forecast.day.ge(FIRST).all() and forecast.p_up.between(0,1).all()
            with np.load(OUT/(tag+'-laws.npz'),allow_pickle=False) as fitted:
                atoms=fitted['atoms']
                assert atoms.shape==(len(forecast),160) and np.isfinite(atoms).all()
                for j in np.linspace(0,len(forecast)-1,9,dtype=int):
                    r=forecast.iloc[j]
                    assert r.law==j
                    y=r.actual if r.target=='session_risk' else np.log1p(r.actual)
                    res=quantify(atoms[j].astype(float),y,r.target!='session_risk')
                    np.testing.assert_allclose(res['crps'],r.crps,atol=2.e-8,rtol=0)
            archive[tag]=len(forecast)
    assert len(archive)==10
    report_technical.update(session_forecast_files=archive,session_distribution_rows=sum(archive.values()))
    ledger=read('forward-ledger.json')
    assert ledger['v4_sha256']==sha(V4/'prospective-ledger.jsonl')
    assert ledger['v5_sha256']==sha(V5/'experimental-forecasts.json')
    assert all(z['maturity'].startswith('resolved') or z['realized_return'] is None and not z['scores'] for z in ledger['records'])
    save('validation-receipt.json',dict(passed=True,checked_at=now(),historical_end=FREEZE,**report_technical,
        point_in_time_checks=clock['eligible_clock_checks'],prior_artifacts=old['v15_artifacts'],
        protected_prior_code=old['v15_code'],v15_reproduced=historical['archived_rows'],future_checks=leak['law_checks'],
        genuine_forward_records=len(ledger['records']),new_forward_issues=ledger['new_v16_issues']))


def delivery():
    verification()
    mission=(OUT/'MISSION.md').read_text(encoding='utf-8-sig')
    expected=set(re.findall(r'`(V16_[A-Z_]+\.md)`',mission))
    reports={f.name for f in OUT.glob('V16_*.md')}
    assert len(expected)==18 and expected==reports
    linked=0
    for f in [*sorted(OUT.glob('V16_*.md')),OUT/'NIFTY_V16_RESEARCH.md',OUT/'README.md']:
        data=f.read_text(encoding='utf-8')
        assert data.startswith('# ') and '�' not in data
        for m in re.findall(r'\[[^\[\]\n]+\]\(([^\s)]+)\)',data):
            if '://' in m or m=='manifest.json':continue
            assert (f.parent/unquote(m)).exists(),(f.name,m)
            linked+=1
    protect={p.relative_to(ROOT).as_posix():sha(p) for p in [V15/'manifest.json',V14/'manifest.json',
                        V4/'prospective-ledger.jsonl',V5/'experimental-forecasts.json']}
    assets={}
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name!='manifest.json':
            assert p.stat().st_size>0,p
            assets[p.relative_to(OUT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    code={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(SRC.glob('*.py'))}
    save('manifest.json',dict(built_at=now(),validated=True,reports=len(reports),artifact_count=len(assets),validated_links=linked,
                              artifacts=assets,source_code=code,predecessors=protect))
    print('Verified',len(reports),'reports,',linked,'links and',len(assets),'archived artifacts',flush=True)

if __name__=='__main__':
    delivery()
