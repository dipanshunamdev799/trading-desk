"""Verify V21 integrity, same-date scoring, rebuilt joint laws and source custody."""
import re

from .common import *
from .reconstruction import MAIN
from research.nifty_forecast_v20.modeling import disjoint


def documents():
    wanted={f'V21_{s}.md' for s in REPORTS}
    assert {p.name for p in OUT.glob('V21_*.md')}==wanted and len(wanted)==19
    links=0
    for name in sorted(wanted|{'NIFTY_V21_RESEARCH.md','README.md'}):
        p=OUT/name
        content=p.read_text(encoding='utf-8')
        assert content.startswith('#') and len(content)>250,name
        for ref in re.findall(r'\]\(([^)]+)\)',content):
            if ref.startswith(('https://','http://')) or ref in ('verification.json','manifest.json'):
                continue
            assert (p.parent/ref).is_file(),(name,ref)
            links+=1
    return links


def archives():
    m=read('manifest.json',V20)
    for root,rows in [(V20,m['files']),(ROOT,m['source_files'])]:
        for d in rows:
            assert sha(root/d['file'])==d['sha256'],d['file']
    assert sha(V20/'manifest.json')==read('predecessor-receipt.json')['manifest_sha256']
    source=read('source-receipt.json')['records']
    accepted=[r for r in source if 'file' in r]
    assert all(FIRST<=d['day']<=FREEZE for d in accepted)
    for d in accepted:
        root=ROOT if d.get('base')=='repository' else OUT
        assert sha(root/d['file'])==d['sha256'],d['file']
    assert len([x for x in accepted if x['family']=='cash'])==466
    assert len([x for x in accepted if x['family']=='nifty50_weights'])==22
    u=csv('official-weight-cash-reconciliation.csv.gz')
    assert u.loc[u.close.notna(),'exact_tick'].all()
    v=csv('cash-identity-and-actions.csv.gz')
    z=v[v.symbol.eq('BAJFINANCE')&v.day.eq('2025-06-16')]
    assert len(z)==1 and abs(z.ratio.iloc[0]-.1)<1.e-12
    w=csv('weight-snapshot-audit.csv')
    for name in ('NIFTY 50','NIFTY Next 50'):
        n=w[w.index_name.eq(name)&w.flavor.eq('official_monthly_csv')]
        assert len(n)==22 and n.count().measured==22
        assert n.eligible_lag5.gt(n.measured).all()
    return dict(v20_artifacts=len(m['files']),v20_code=len(m['source_files']),source_files_verified=len(accepted),
                exact_weight_prices=int(u.exact_tick.sum()),verified_bajaj_split_bonus=True)


def model_laws():
    z=csv('index-forecast-cases.csv.gz')
    assert z.target_end.le(FREEZE).all() and z['day'].ge(FIRST).all()
    with np.load(OUT/'index-forecast-laws.npz',allow_pickle=False) as book:
        a,w,o=book['atoms'],book['weights'],book['offsets']
        k=len(z)
        assert len(o)==k+1 and o[-1]==len(a)==len(w) and np.all(np.diff(o)>0)
        assert np.isfinite(a).all() and (w>=0).all() and (a>-1).all()
        base=o[:-1]
        np.testing.assert_allclose(np.add.reduceat(w,base),1,rtol=0,atol=3.e-10)
        np.testing.assert_allclose(np.add.reduceat(w*(a>0),base),z.p,rtol=0,atol=3.e-10)
        np.testing.assert_allclose(np.add.reduceat(w*a,base),z['mean'],rtol=0,atol=3.e-10)
        law=z[(z.cutoff=='preauction_0855')&(z.model=='stock_pooled_joint')].sort_values(['horizon','day'])
        for h in HORIZONS:
            f=law[law.horizon.eq(h)]
            ix={key:int(v) for key,v in f.groupby('cohort').size().items()}
            assert (ix['early'],ix['later'],disjoint(f))==EXPECTED[h]
        predicted=np.stack([a[o[i]:o[i+1]] for i in law.law])
        with np.load(OUT/'joint-simultaneous-laws.npz',allow_pickle=False) as p:
            w=p['asset_weights'];r=p['stock_returns'];b=p['basis'];member=p['asset_indices']
            assert r.shape[0]==482 and r.shape[1]==256
            np.testing.assert_allclose(w.sum(axis=1),1,atol=1.e-10)
            assert ((member==-1)==(w==0)).all()
            np.testing.assert_allclose(np.einsum('ijk,ik->ij',r,w)+b,predicted,rtol=0,atol=3.e-8)
    p=csv('protected-return-cases.csv.gz')
    m=p.merge(z,on=['horizon','cutoff','model','day'],validate='1:1',suffixes=('_old','_v21'))
    assert len(m)==len(p)==2892
    for name in ('actual','p','brier','crps','log_loss'):
        np.testing.assert_allclose(m[f'{name}_old'],m[f'{name}_v21'],rtol=0,atol=2.e-12)
    with np.load(OUT/'bottom-up-volatility-laws.npz',allow_pickle=False) as rv:
        risk=csv('risk-comparison-cases.csv.gz')
        x=risk[risk.law.ge(0)]
        assert len(rv['offsets'])==len(x)+1 and rv['atoms'].min()>0
        np.testing.assert_allclose(np.add.reduceat(rv['weights'],rv['offsets'][:-1]),1,atol=2.e-12)
    return dict(index_predictions=len(z),independent_horizon_counts=EXPECTED,accounted_simultaneous_laws=len(law),
                protected_replays=len(m),volatility_laws=len(x))


def forward():
    q=read('forward-ledger.json')
    prior=read('forward-ledger.json',V20)
    for a,b in zip(q['original_issues'],prior['records'],strict=True):
        assert a['issue_hash']==b['issue_hash'] and a['target_sessions']==b['target_sessions'] and a['issued']==b['issued']
    for members,root in [(q['inherited_v19'],V19),(q['inherited_v20'],V20)]:
        for i,old in zip(members,read('forward/new-issues.json',root)['records'],strict=True):
            assert i['issued_at']==old['issued_at'] and i['target_sessions']==old['target_sessions']
            assert i['target_sessions'][-1]<=LAST and i['target_sessions'][0]>i['issued_at'][:10]
            assert sha(root/i['source_artifact'])==old.get('sha256',old.get('law_sha256'))
    root={'V19':V19,'V20':V20,'V21':OUT}
    for r in q['sessions']:
        assert FREEZE<r['day']<=LAST and sha(root[r['archive']]/r['file'])==r['sha256']
    d=[x for x in read('forward-input-receipts.json')['captures'] if 'file' in x]
    for r in d:
        assert FREEZE<r['day']<=LAST and sha(OUT/r['file'])==r['sha256']
    return dict(legacy=len(q['original_issues']),legacy_resolved=sum(x['realized_return'] is not None for x in q['original_issues']),
        dated_references=len(q['inherited_v19'])+len(q['inherited_v20']),new_issues=len(q['new_issues']),
        certified_sessions=len(q['sessions']),staged_capture_files=len(d))


def run():
    a=documents();b=archives();c=model_laws();d=forward()
    registration=read('registration.json')
    assert len(registration['hypotheses'])<=16
    before=min([r['attempts'][0]['sent'] for r in read('source-receipt.json')['records'] if r.get('attempts')])
    assert registration['registered_at']<=before
    for p in SRC.glob('*.py'):
        compile(p.read_text(encoding='utf-8'),str(p),'exec')
    save('verification.json',dict(verified_at=now(),reports=len(REPORTS),local_links=a,archive_checks=b,law_checks=c,forward_checks=d,
                                  clock_controls=read('validation-receipt.json'),tracking_model=MAIN))
    entries=[dict(path=p.relative_to(OUT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*'))
             if p.is_file() and p.name!='manifest.json']
    code=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(SRC.glob('*.py'))]
    save('manifest.json',dict(study='NIFTY V21',scope=[FIRST,FREEZE],reports=len(REPORTS),files=entries,code=code,
                             protected_v20_manifest=sha(V20/'manifest.json'),count=len(entries),bytes=sum(x['bytes'] for x in entries)))
    print('Verified',len(REPORTS),'reports,',a,'local links,',c['index_predictions'],'return laws and',len(entries),'artifact hashes',flush=True)


if __name__=='__main__':
    run()
