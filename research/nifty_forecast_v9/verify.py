"""Verify maturity, target alignment, synthetic invariance and archive integrity."""
import argparse
import joblib
from .common import *
from .run_models import inputs, fit_variant, indices
from .models import Distribution


def prior():
    manifest=read('preservation.json');bad=[]
    for p,d in manifest['files'].items():
        file=ROOT/p
        if not file.is_file() or sha(file)!=d:bad.append(p)
    save('prior-integrity.json',{'at':now(),'checked':len(manifest['files']),'changed':bad,'passed':not bad})
    if bad:raise AssertionError(bad)
    print('Rehashed',len(manifest['files']),'protected V1–V8 files',flush=True)


def run(require_reports=False):
    checks=[]
    def check(ok,name):
        if not ok:raise AssertionError(name)
        checks.append(name)
    protected=read('prior-integrity.json');check(protected['passed'],'Protected earlier files and frozen ledgers match')
    repro=read('reproduction.json');check(repro['passed'] and repro['v8_rows']==2949 and repro['older_weekly_rows']==644 and repro['max_abs_error']<1e-12,'V8 winners and controlled experiments, plus prior reference laws reproduced')
    manifest=read('feature-manifest.json');check(manifest['past_feature_truncation_verified'] and all(sha(OUT/(n+'.csv'))==v for n,v in manifest['hashes'].items()),'Causal financial/panel features and matrix hashes verified')
    check(all(r['day']>='2025-01-01' and r['day']<='2026-12-31' for r in pd.read_csv(OUT/'acquired-candles.csv')[['day']].to_dict('records')),'Acquired inputs confined to 2025–2026')
    p=pd.read_csv(OUT/'all-predictions.csv');reg=read('experiment-registry.json');ok=[r for r in reg['attempts'] if r['status']=='ok']
    check(not p.duplicated(['cohort','horizon','model','origin']).any(),'Unique model and outcome keys')
    for (c,h),g in p.groupby(['cohort','horizon']):
        y=matrix(f'extended-labels-{h}.csv',OUT) if c=='refresh' else matrix(f'labels-{h}.csv')
        expected=y.loc[g.origin];np.testing.assert_array_equal(g.endpoint,expected.endpoint);np.testing.assert_allclose(g.realized_return,expected['return'],atol=1e-12)
    check(True,'Each forecast joined to its exact matured endpoint and vintage')
    np.testing.assert_allclose(p.brier,(p.p-p.outcome)**2,atol=1e-12)
    np.testing.assert_allclose(p.expected_price,p.reference_close*(1+p.predicted_mean),atol=1e-8)
    np.testing.assert_allclose(p.filter(regex='^bucket[0-6]_p$').sum(axis=1),1.,atol=1e-12)
    check((np.diff(p[['q05','q10','q25','q50','q75','q90','q95']],axis=1)>=0).all() and p.p.between(0,1).all(),'Coherent law outcomes, ordered quantiles, bucket mass and endpoint price')
    check(all(r['last_endpoint']<r['cutoff'] and r['inner_last_endpoint']<r['inner_cutoff'] for r in ok if 'model_file' in r),'Mature outer labels and purged residual-fitting partition')
    check(all(sha(OUT/r['model_file'])==r['sha256'] for r in ok if 'model_file' in r),'Saved model hashes match registrations')
    check(all(r['last_gate_endpoint'] is None or r['last_gate_endpoint']<r['cutoff'] for r in read('reliability-ledger.json')),'Reliability labels mature before gate fitting')
    diag=pd.read_csv(OUT/'reliability-diagnostics.csv').dropna(subset=['last_recent_mature_endpoint']);check((diag.last_recent_mature_endpoint<diag.origin).all(),'Online error features reject all unresolved outcomes')
    weights=pd.read_csv(OUT/'expert-weights.csv').filter(regex='^P_');np.testing.assert_allclose(weights.sum(axis=1),1,atol=1e-12)
    check((weights>=0).all().all(),'Adaptive mixtures are convex combinations of complete laws')
    paths=read('path-reconstruction-samples.json');check(all(max(r['source_endpoints'])<r['origin'] for r in paths),'Every saved path block matured before its origin')
    for r in paths[:10]:
        d=Distribution(np.expm1(np.asarray(r['log_return_paths']).sum(axis=1)),r['weights'])
        score=p[(p.horizon==r['horizon'])&(p.origin==r['origin'])&(p.model==r['model'])].iloc[0]
        np.testing.assert_allclose([d.stats()['p_up'],d.stats()['mean_return']],[score.p,score.predicted_mean],atol=1e-12)
    check(True,'Saved simulated blocks compound to the scored endpoint law')
    for suite in ['invariance','sector-alias']:
        rep=pd.read_csv(OUT/'duplicate-replay'/f'{suite}-effects.csv');old=pd.read_csv(V8/f'{suite}-effects.csv')
        rows=rep[rep.required_invariance];check(len(rows)==(110 if suite=='invariance' else 15) and rows.passes_tolerance.all(),suite+' exact duplicate tolerance')
        np.testing.assert_allclose(rep.max_law_error,old.max_law_error,atol=1e-10)
    contrasts=read('benchmark-comparisons.json');check(all('adjusted95_block10' not in r for r in contrasts if r['horizon']==21),'Monthly intervals withheld')
    null=pd.read_csv(OUT/'null-search-maxima.csv');check(set(null.draw)==set(range(-1,24)),'24 refitted search nulls plus genuine search')
    x,_=inputs();replays=[]
    for f in ok:
        if f.get('model') not in ['P_ROT','P_STRUCTURE','T_KALMAN'] or f['horizon']!=5 or f['cohort']!='later':continue
        y=matrix('labels-5.csv');obj=joblib.load(OUT/f['model_file']);s=reg['specifications'][f['model']]
        tr,ii,vv,q=(obj[k] for k in ['tr','ii','vv','q']);m0,res0=None,None
        # A synthetic future-labelled value must never change fitting partitions or scored laws.
        changed=y.copy();changed.loc[changed.endpoint>=f['cutoff'],'return']=9.999
        tt,jj,ww,_=indices(changed,f['cutoff'],s)
        assert list(tt)==tr and list(jj)==ii and list(ww)==vv
        _,_,_,ds=fit_variant(s,x[s['frame']],changed,tr,ii,vv,q)
        expected=p[(p.horizon==5)&(p.cohort=='later')&(p.model==f['model'])].set_index('origin').loc[q]
        vals=['p','predicted_mean','predicted_median','crps','brier']
        got=pd.DataFrame(d.score(y.loc[t,'return']) for d,t in zip(ds,q))[vals].to_numpy()
        np.testing.assert_allclose(got,expected[vals],atol=1e-12,rtol=1e-12)
        replays.append({'model':f['model'],'fold':f['fold'],'n':len(q),'max_error':float(abs(got-expected[vals].to_numpy()).max())})
    check(sum(r['n'] for r in replays)==276,'Replayed 276 V9 forecasts and rejected future-label sentinel')
    official=read('acquisition.json')['official_crosscheck'];check(all(r['status']!='verified' or np.isfinite(r['official_close']) for r in official),'Independent source reconciliation retained, with unavailable sources explicit')
    if require_reports:
        m=read('report-manifest.json');check(len(m)==16 and all(sha(OUT/n)==v for n,v in m.items()),'All sixteen requested reports and manifest verified')
    save('verification.json',{'passed':True,'completed_at':now(),'protected_files':protected['checked'],'checks':checks,'refitted':replays})
    print('Verify passed:',len(checks),'checks and',sum(r['n'] for r in replays),'forecast refits',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prior',action='store_true');parser.add_argument('--reports',action='store_true');args=parser.parse_args()
    if args.prior:prior()
    else:run(args.reports)
