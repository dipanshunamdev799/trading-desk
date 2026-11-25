"""Verify the V20 report set, law reconstruction, scope and predecessor preservation."""
import hashlib
import re
from .common import *
from research.nifty_forecast_v18.delivery import references

BOOKS=('source-discovery-receipt.json','cdsl-extension-receipt.json','forward-refresh-receipt.json','forward/options-probes.json')

def checksum(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def docs():
    reports=[OUT/f'V20_{x}.md' for x in REPORTS]
    assert len(reports)==20 and set(reports)==set(OUT.glob('V20_*.md'))
    total=0
    for p in [*reports,OUT/'README.md',OUT/'NIFTY_V20_RESEARCH.md']:
        b=p.read_text(encoding='utf-8')
        assert b.lstrip().startswith('#') and len(b)>400,p.name
        for target in re.findall(r'\]\(([^)]+)\)',b):
            if target.startswith(('https://','http://')) or target=='manifest.json':
                continue
            assert (p.parent/target).is_file(),(p.name,target)
            total+=1
    return total

def sources():
    out={}
    for key in BOOKS:
        pairs=sorted(set(references(read(key))))
        for file,h in pairs:
            assert checksum(OUT/file)==h,(key,file)
        out[key]=len(pairs)
    past=read('predecessor-inventory.json')
    assert checksum(V19/'manifest.json')==past['v19_manifest']
    p=read('forward-ledger.json')
    q=read('forward-ledger.json',V19)
    keys=('issue_hash','issue_class','issued','original_probabilities','p_up','law_p_up','target_sessions','reference_close')
    assert len(p['records'])==len(q['records'])==6
    originals={(r['key'],r['horizon']):r for r in q['records']}
    for r in p['records']:
        o=originals[r['key'],r['horizon']]
        assert all(r.get(k)==o.get(k) for k in keys)
        if r['realized_return'] is not None:
            assert r['completed_target_dates']==r['target_sessions']
            assert abs(r['official_close']/r['reference_close']-1-r['realized_return'])<1.e-12
            if o['realized_return'] is not None:assert r['realized_return']==o['realized_return']
    issue=read('forward/new-issues.json',V19)
    assert p['v19_issue_file_sha256']==checksum(V19/'forward/new-issues.json')
    for a,b in zip(issue['records'],p['inherited_v19_research'],strict=True):
        assert all(b[k]==v for k,v in a.items())
        assert checksum(V19/a['file'])==a['sha256']
    for r in p['sessions']:
        fp={'V19':V19,'V20':OUT}[r['archive']]/r['file']
        assert checksum(fp)==r['sha256']
        assert FREEZE<r['day']<=LAST
    for r in p['new_issues']:
        assert r['first_target']>r['issued_at'][:10] and r['target']<=LAST
        assert len(r['target_sessions'])==r['horizon']
        assert checksum(OUT/r['law'])==r['law_sha256']
    return out|dict(new_issues=len(p['new_issues']),prior_issues=len(p['inherited_v19_research']),
                    legacy_resolved=sum(x['realized_return'] is not None for x in p['records']))

def forecast_laws():
    n={}
    for name,root in [('native-mechanism-laws.npz','native-mechanism-cases.csv.gz'),('architecture-laws.npz','architecture-cases.csv.gz')]:
        cases=csv(root,usecols=['law','day','target_end','last_mature','horizon','model','p','mean','cohort'])
        assert cases.target_end.le(FREEZE).all()
        seen=cases.last_mature.notna()
        assert cases.loc[seen,'last_mature'].lt(cases.loc[seen,'day']).all()
        with np.load(OUT/name,allow_pickle=False) as a:
            atom,w,o=a['atoms'],a['weights'],a['offsets']
            assert len(o)==len(cases)+1 and o[-1]==len(atom)==len(w)
            assert len(atom)>0 and (np.diff(o)>0).all() and np.isfinite(atom).all() and (w>=0).all()
            np.testing.assert_allclose(np.add.reduceat(w,o[:-1]),1,rtol=0,atol=1.e-8)
            mass=np.add.reduceat(w*(atom>0),o[:-1])
            np.testing.assert_allclose(mass,cases.p,rtol=0,atol=2.e-8)
            np.testing.assert_allclose(np.add.reduceat(w*atom,o[:-1]),cases['mean'],rtol=0,atol=2.e-8)
        n[name]=len(cases)
    q=csv('native-source-clock-audit.csv')
    assert q.participant_guard.le(q.input_snapshot).all() and q.input_snapshot.le(q.parent_decision).all()
    z=csv('multi-horizon-targets.csv')
    early=z.cohort_5.eq('early').sum()
    late=z.cohort_5.eq('later').sum()
    assert (early,late,z.cohort_21.eq('early').sum(),z.cohort_21.eq('later').sum())==(173,92,141,76)
    live=z['return_0_21'].notna()
    for features in [('return_0_5','return_5_21'),('return_0_5','return_5_10','return_10_15','return_15_21')]:
        np.testing.assert_allclose(z.loc[live,list(features)].sum(axis=1),z.loc[live,'return_0_21'],rtol=0,atol=1.e-12)
    parts=np.load(OUT/'component-law-archive.npz',allow_pickle=False)['log_return_components']
    assert parts.ndim==3 and parts.shape[-1]==4 and len(parts)==217*6
    late=csv('strong-parent-component-cases.csv.gz')
    with np.load(OUT/'strong-parent-component-laws.npz',allow_pickle=False) as a:
        atoms=a['log_parent_atoms']
        assert atoms.shape==(217*4,256) and len(late)==217*4*7
        assert late.loc[~late.active,'correction'].eq(0).all()
        terminal=np.expm1(atoms[late.law.to_numpy()]+late.correction.to_numpy()[:,None])
        np.testing.assert_allclose((terminal>0).mean(axis=1),late.p,rtol=0,atol=1.e-12)
        np.testing.assert_allclose(terminal.mean(axis=1),late['mean'],rtol=0,atol=1.e-12)
    asof=csv('asof-features.csv.gz',usecols=['day','cutoff','decision'])
    used=late[late.last_mature.notna()].merge(asof,on=['day','cutoff'],validate='m:1')
    assert used.last_mature.lt(used.decision.str[:10]).all() and late.target_end.le(FREEZE).all()
    r=csv('coherent-path-law-recipes.csv.gz',usecols=['parent_file','parent_sha256','simulations']).drop_duplicates()
    assert r.simulations.eq(256).all() and len(r)==482
    for e in r.itertuples(index=False):
        assert checksum(V17/e.parent_file)==e.parent_sha256
    risk=read('risk-receipt.json')
    assert risk['exact_path_parent_cases']==1928 and risk['maximum_path_score_difference']<1.e-9
    return n|dict(component_laws=len(parts),strong_component_cases=len(late),protected_OHLC_sources=len(r),native_clock_cases=len(q),
                  exact_path_parent_cases=risk['exact_path_parent_cases'])

def validate_lifetimes():
    p=csv('asof-features.csv.gz',usecols=['day','source_release','decision','cutoff'])
    assert p.source_release.le(p.decision).all()
    key=p.set_index(['cutoff','day']).decision.str[:10]
    assert key.index.is_unique
    q=read('lifetime-receipt.json')
    z=csv('information-lifetime-matrix.csv')
    assert z.family.nunique()==18 and z.age.nunique()==7 and z.cutoff.nunique()==2
    assert z[['family','mode','age','cutoff','start_offset','end_offset','metric']].drop_duplicates().shape[0]==len(z)
    assert z.loc[z['mode'].eq('cumulative'),'end_offset'].nunique()==8
    assert z.loc[z['mode'].eq('risk'),'end_offset'].nunique()==8
    assert z[z.end_offset.eq(21)].n_total.eq(217).all()
    n=0
    with pd.read_csv(OUT/'lifetime-cases.csv.gz',chunksize=100000,
                     usecols=['law','shift','active','day','last_mature','target_end','cutoff']) as fd:
        for d in fd:
            assert d.target_end.le(FREEZE).all() and d.day.ge(FIRST).all()
            assert d.loc[~d.active,'shift'].eq(0).all()
            a=d[d.active]
            issued=key.reindex(pd.MultiIndex.from_frame(a[['cutoff','day']])).to_numpy()
            assert (a.last_mature.to_numpy()<issued).all()
            n+=len(d)
    assert n==q['case_rows'] and np.load(OUT/'lifetime-parent-laws.npz',allow_pickle=False)['atoms'].shape[0]==q['target_clock_cells']
    return dict(case_rows=n,matrix_rows=len(z),family_count=18,ages=7)

def main():
    count=docs()
    receipts=sources()
    law=forecast_laws()
    life=validate_lifetimes()
    for p in SRC.glob('*.py'):
        compile(p.read_text(encoding='utf-8'),str(p),'exec')
    save('delivery-receipt.json',dict(at=now(),reports=20,verifiable_local_links=count,sources=receipts,laws=law,
        lifetime=life,protected_v19_file_count=read('predecessor-inventory.json')['artifacts']))
    source=[]
    for p in sorted(SRC.glob('*.py')):
        source.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=checksum(p),bytes=p.stat().st_size))
    files=[]
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name!='manifest.json' and p.suffix not in ('.partial','.part'):
            files.append(dict(file=p.relative_to(OUT).as_posix(),sha256=checksum(p),bytes=p.stat().st_size))
    save('manifest.json',dict(study='NIFTY V20',historical_scope=[FIRST,FREEZE],reports=20,
                v19_manifest=checksum(V19/'manifest.json'),source_files=source,files=files,
                verification=read('delivery-receipt.json'),file_count=len(files),bytes=sum(x['bytes'] for x in files)))
    print('Verified 20 reports,',count,'local links,',n_safe(life['case_rows']),'lifetime predictions and',len(files),'artifact hashes',flush=True)

def n_safe(n):
    return f'{n:,}'

if __name__=='__main__':
    main()

