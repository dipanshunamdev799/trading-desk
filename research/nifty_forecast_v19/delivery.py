"""Verify the requested report set, source hashes, chronology and complete law archives."""
import re
import sqlite3
from contextlib import closing

from .common import *
from research.nifty_forecast_v18.delivery import references

SOURCE_BOOKS=('source-receipts.json','alternate-source-preflight.json','flow-source-receipts.json','cash-form-probes.json',
              'joint-law-receipts.json','forward-ledger.json','forward/new-issues.json','forward/alternate-market-receipts.json',
              'forward/certification-probes.json')

def links(reports):
    count=0
    for path in reports:
        body=path.read_text(encoding='utf-8')
        assert body.strip().startswith('#') and len(body)>450
        for target in re.findall(r'\]\(([^)]+)\)',body):
            if target.startswith(('https://','http://')) or target=='manifest.json':
                continue
            assert (path.parent/target).is_file(),(path.name,target)
            count+=1
    return count

def verify_receipts():
    n={}
    for name in SOURCE_BOOKS:
        checks=0
        for file,fingerprint in sorted(set(references(read(name)))):
            p=OUT/file
            assert p.is_file() and sha(p)==fingerprint,(name,file)
            checks+=1
        n[name]=checks
    for r in read('joint-law-receipts.json')['files']:
        assert sha(V17/r['parent_file'])==r['parent_sha256']
    for x in (OUT/'forward').glob('*/receipt.json'):
        for file,fingerprint in set(references(json.loads(x.read_text(encoding='utf-8')))):
            assert (OUT/file).is_file() and sha(OUT/file)==fingerprint
    return n

def weighted_laws(name,case):
    d=csv(case)
    with np.load(OUT/name,allow_pickle=False) as z:
        atom=z['atoms']; weights=z['weights']; off=z['offsets']
        assert len(off)==len(d)+1 and off[-1]==len(atom)==len(weights)
        assert np.isfinite(atom).all() and np.isfinite(weights).all() and np.all(weights>=0)
        np.testing.assert_allclose(np.add.reduceat(weights,off[:-1]),1,atol=1.e-9,rtol=0)
        assert np.all(np.diff(off)>0)
    return len(d)

def plain_laws(name,case,atom='log_return_atoms'):
    d=csv(case)
    d=d[d.law.ge(0)]
    with np.load(OUT/name,allow_pickle=False) as z:
        assert len(z[atom])==len(d) and np.isfinite(z[atom]).all()
        assert sorted(d.law.astype(int))==list(range(len(d)))
    return len(d)

def main():
    reports=[OUT/f'V19_{key}.md' for key in REPORTS]
    assert len(reports)==18 and all(x.is_file() for x in reports)
    assert set(reports)==set(OUT.glob('V19_*.md'))
    link_count=links([*reports,OUT/'README.md',OUT/'NIFTY_V19_RESEARCH.md'])
    audited=verify_receipts()
    s=read('predecessor-protection.json')
    assert sha(V18/'manifest.json')==s['v18_manifest']
    with closing(sqlite3.connect(OUT/'market-positioning.sqlite')) as db:
        assert db.execute('pragma quick_check').fetchone()[0]=='ok'
        v=db.execute('select count(*) from delivery_reports').fetchone()[0]
        assert v==read('database-receipt.json')['delivery']['full_rows']
        assert db.execute('select count(*) from participants where day>=substr(eligible_at,1,10)').fetchone()[0]==0
        assert db.execute("select count(*) from delivery_reports where day<'2025-01-01' or day>'2026-11-17'").fetchone()[0]==0
    f=read('forward-ledger.json')
    original=read('forward-ledger.json',V18)
    keys=['issue_class','issue_hash','issued','target_sessions','reference_close','original_probabilities','law_p_up','p_up','mean_return']
    assert len(f['records'])==len(original['records'])==6
    old={ (r['key'],r['horizon']):r for r in original['records'] }
    for r in f['records']:
        q=old[(r['key'],r['horizon'])]
        assert all(q.get(k)==r.get(k) for k in keys)
        if r['realized_return'] is not None:
            assert r['completed_target_dates']==r['target_sessions']
            assert abs(r['official_close']/r['reference_close']-1-r['realized_return'])<1.e-12
            if r.get('resolution_at'):
                assert pd.Timestamp(r['resolution_at'])>=stamp(r['target_sessions'][-1],'18:00')
                assert r['binary_scores'] and r['scores']
    assert len(f['new_references'])==f['new_v19_issues']==3
    for r in f['new_references']:
        assert r['issued_at'][:10]<r['target_sessions'][0] and r['target_sessions'][-1]<=LAST
        assert len(r['target_sessions'])==r['horizon']
    n0=weighted_laws('v18-native-replayed-laws.npz','v18-native-exact-replay.csv')
    n1=weighted_laws('native-residual-laws.npz','native-residual-cases.csv.gz')
    n2=weighted_laws('native-mechanism-laws.npz','native-mechanism-cases.csv.gz')
    e=plain_laws('endpoint-laws.npz','endpoint-cases.csv.gz')
    v=plain_laws('volatility-laws.npz','risk-cases.csv.gz','annualized_volatility_atoms')
    dated=csv('deal-audited.csv.gz').groupby('day').premium_to_previous_close.count()
    unpriced=dated[dated.eq(0)].index
    daily=csv('positioning-daily-features.csv.gz').set_index('day')
    assert daily.loc[unpriced,'deal_n'].gt(0).all()
    assert daily.loc[unpriced,['deal_premium','deal_cash_turnover_share']].isna().all().all()
    for p in SRC.glob('*.py'):
        compile(p.read_text(encoding='utf-8'),str(p),'exec')
    receipt=dict(verified_at=now(),reports=len(reports),local_links=link_count,source_receipts=audited,native_original=n0,
                 native_v19=n1,native_sensitivity=n2,original_endpoint_atoms=e,volatility_laws=v,prior_v18_hashes=s['artifacts'],
                 legacy_original_issues=len(f['records']),new_reference_laws=f['new_v19_issues'],
                 legacy_resolutions=sum(r['realized_return'] is not None for r in f['records']),
                 dated_deal_sessions_without_cash_references=len(unpriced),
                 chronological_sentinels=read('validation-receipt.json')['future_information_sentinels'])
    save('delivery-receipt.json',receipt)
    files=[]
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name!='manifest.json' and p.suffix not in ('.partial','.part'):
            files.append(dict(file=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    code=[dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(SRC.glob('*.py'))]
    save('manifest.json',dict(study='NIFTY V19',frozen_scope=[FIRST,FREEZE],reports=len(reports),file_count=len(files),
                            bytes=sum(r['bytes'] for r in files),files=files,source_files=code,
                            immutable_V18_manifest=s['v18_manifest'],verification=receipt))
    print('Verified',len(reports),'reports,',link_count,'local references,',len(files),'artifact hashes and all original issue classifications',flush=True)

if __name__=='__main__':
    main()

