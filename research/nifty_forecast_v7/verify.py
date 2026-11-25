"""Check the fitted research outputs, exact interventions and prior preservation."""
import argparse
import joblib
from .common import *
from .experiments import all_frames
from .models import fit, laws, location


def preserved():
    files=read('preservation.json')['files']
    failures=[p for p,digest in files.items() if not (ROOT/p).exists() or sha(ROOT/p)!=digest]
    save('prior-integrity-verification.json',{'checked_at':now(),'checked':len(files),'changed':failures,'passed':not failures})
    if failures:raise AssertionError(failures)
    print('Preserved',len(files),'prior files',flush=True)


def run(reports=False):
    checks=[]
    def check(condition,name):
        if not condition:raise AssertionError(name)
        checks.append(name)
    integrity=read('prior-integrity-verification.json')
    check(integrity['passed'] and integrity['checked']==len(read('preservation.json')['files']),'Earlier versions rehashed without changes')
    check(read('v6-reproduction.json')['passed'] and read('legacy-reproduction.json')['passed'],'V4–V6 reconstruction passed')
    x=pd.read_csv(OUT/'all-predictions.csv');registry=read('experiment-registry.json')
    check(not x.duplicated(['horizon','model','origin']).any(),'Unique model/horizon/origin keys')
    for h,z in x.groupby('horizon'):
        labels=matrix(f'labels-{h}.csv').loc[z.origin]
        np.testing.assert_allclose(z.realized_return,labels['return'],atol=1e-12)
        np.testing.assert_array_equal(z.endpoint,labels.endpoint)
    check(x.origin.min()>='2025-01-01' and x.endpoint.max()<='2026-12-31','Every label matched to its session horizon and scope')
    check((np.diff(x[['q05','q10','q25','q50','q75','q90','q95']],axis=1)>=0).all(),'Endpoint quantiles ordered')
    np.testing.assert_allclose(x.filter(regex='^bucket[0-6]_p$').sum(axis=1),1,atol=1e-12)
    np.testing.assert_allclose(x.brier,(x.p-x.outcome)**2,atol=1e-12)
    np.testing.assert_allclose(x.expected_endpoint,x.reference_close*(1+x.predicted_mean),atol=1e-9)
    check(x.p.between(0,1).all(),'Coherent sign scores, return buckets and endpoint means')
    fit_records=[r for r in registry['fit_attempts'] if r['status']=='ok']
    check(all(r['last_endpoint']<r['train_cutoff'] and r['inner_last_endpoint']<r['inner_cutoff']<r['cutoff'] for r in fit_records),'Outer/inner fit endpoints matured, purged and embargoed')
    check(all(sha(OUT/r['artifact'])==r['sha256'] for r in fit_records),'Fitted model hashes match')
    check(all(r['last_endpoint']<r['cutoff'] for r in registry['auxiliary_fits']),'Intermediate global/risk models use matured labels')
    check(all(all(a['endpoint']<r['cutoff'] for a in r['history']) and r['inner_last_endpoint']<r['inner_first'] for r in registry['integration_fits']),'Mixture weights and sign calibration exclude unresolved forecasts')
    pred=x.set_index(['model','horizon','origin'])
    cols=['p','predicted_mean','crps','brier']
    np.testing.assert_allclose(pred.loc['C_RAW',cols].sort_index(),pred.loc['C_DUP_BALANCED',cols].sort_index(),atol=1e-12)
    check(True,'Duplicate plus compensating penalty reproduces raw forecasts')
    comparison=read('benchmark-contrasts.json')
    check(all('adjusted95_block10' not in r for r in comparison if r['horizon']==21),'Monthly precision withheld')
    aud=read('intraday-audit.json');intraday=matrix('intraday-features.csv',OUT)
    check(len(intraday)==aud['complete_sessions'] and set(x[x.model=='L_INTRADAY'].origin)<=set(intraday.index),'Intraday models use complete sessions only')
    check(read('feature-checks.json')['market_structure_truncation_invariant'],'Truncating future input bars preserves past structure features')
    # Refit three leaders for every weekly fold against the persisted outputs.
    frames,_=all_frames();low=frames['nodef'];rot=frames['rotation'];frames['rotation_domestic']=pd.concat([low,rot[['financial_spread','defensive_dispersion']]],axis=1)
    label=matrix('labels-5.csv');replayed=0;max_error=0.;coefficients=[];replay_laws=[]
    for r in fit_records:
        if r['horizon']!=5 or r['model'] not in ['T_ROT_DOMESTIC','L_DAILY','T_ELASTIC_EMBARGO']:continue
        saved=joblib.load(OUT/r['artifact']);cfg=registry['configurations'][r['model']];f=frames[cfg['frame']]
        ii=saved['inner'];vv=saved['validation'];tr=saved['training'];q=saved['query']
        inner=fit(cfg,f.loc[ii],label.loc[ii,'return'].to_numpy());model=fit(cfg,f.loc[tr],label.loc[tr,'return'].to_numpy())
        res=label.loc[vv,'return'].to_numpy()-location(inner,f.loc[vv]);d=laws(model,f.loc[q],res,f.loc[vv,'p_rv21'].to_numpy())
        actual=pd.DataFrame(law.score(y) for law,y in zip(d,label.loc[q,'return']))[cols].to_numpy()
        reference=pred.loc[(r['model'],5,q),cols].to_numpy()
        np.testing.assert_allclose(actual,reference,atol=1e-12)
        replayed+=len(q);max_error=max(max_error,float(abs(actual-reference).max()))
        scale=model['scale'];weights=model['transform']@model['estimator'].coef_
        for j,feature in enumerate(scale.cols):
            coefficients.append({'model':r['model'],'fold':r['fold'],'cutoff':r['cutoff'],'feature':feature,
                'training_median':scale.med[j],'training_mean':scale.mu[j],'training_std':scale.sd[j],
                'coefficient_per_standardized_input':weights[j],'intercept':model['estimator'].intercept_})
        for origin,law in zip(q,d):
            replay_laws.append({'model':r['model'],'fold':r['fold'],'origin':origin,'endpoint':label.loc[origin,'endpoint'],
                                'return_atoms':law.a.tolist(),'weights':law.w.tolist(),'status':'reconstructed exposed-history forecast'})
    check(replayed==276,'Fresh replay of three leading weekly configurations')
    pd.DataFrame(coefficients).to_csv(OUT/'retained-feature-weights.csv',index=False)
    (OUT/'retained-endpoint-laws.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in replay_laws),encoding='utf-8')
    if reports:
        manifest=read('report-manifest.json')
        check(len(manifest)==15 and all(sha(OUT/p)==digest for p,digest in manifest.items()),'All fifteen required reports and fixed hashes')
    save('verification.json',{'passed':True,'checked_at':now(),'checks':checks,'replayed_rows':replayed,'replay_max_error':max_error,
                               'protected_files':integrity['checked']})
    print('Verified',len(checks),'checks, replayed',replayed,'weekly forecasts',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preserve-only',action='store_true');parser.add_argument('--reports',action='store_true');args=parser.parse_args()
    if args.preserve_only:preserved()
    else:run(args.reports)
