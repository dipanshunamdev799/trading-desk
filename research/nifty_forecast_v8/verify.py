"""Rehash protected research and independently refit representative V8 forecasts."""
import argparse
import joblib
from .common import *
from .experiments import frames
from .models import fit, location, predict


def prior():
    files=read('preservation.json')['files']
    bad=[p for p,d in files.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=d]
    save('prior-verification.json',{'at':now(),'files':len(files),'changed':bad,'passed':not bad})
    if bad:raise AssertionError(bad)
    print('Verified',len(files),'protected V1–V7 files',flush=True)


def run(reports=False):
    checks=[]
    def check(condition,name):
        if not condition:raise AssertionError(name)
        checks.append(name)
    old=read('prior-verification.json');check(old['passed'],'V1–V7 artifacts and frozen forecast ledgers unchanged')
    repro=read('reproduction.json');check(repro['passed'] and repro['forecasts']==644 and repro['max_error']<1e-12,'644 weekly prior forecasts reproduced')
    legacy=read('legacy-reproduction.json');check(legacy['passed'] and len(legacy['fold_vectors'])==81,'81 V4/V5 saved model vectors reproduced')
    manifest=read('data-manifest.json');check(all(sha(OUT/f'{n}.csv')==d for n,d in manifest['file_hashes'].items()),'Feature matrices match their manifest')
    p=pd.read_csv(OUT/'all-predictions.csv');r=read('search-ledger.json')
    check(not p.duplicated(['cohort','horizon','model','origin']).any(),'Unique origin/model/horizon/cohort forecasts')
    for h,g in p.groupby('horizon'):
        y=matrix(f'labels-{h}.csv').loc[g.origin]
        np.testing.assert_allclose(y['return'],g.realized_return,atol=1e-12)
        np.testing.assert_array_equal(y.endpoint,g.endpoint)
    check(p.origin.min()>='2025-01-01' and p.endpoint.max()<='2026-12-31','Correct frozen 5/10/15/21-session endpoints and 2025–2026 scope')
    check((np.diff(p[['q05','q10','q25','q50','q75','q90','q95']],axis=1)>=0).all(),'Coherent ordered quantiles')
    np.testing.assert_allclose(p.filter(regex='^bucket[0-6]_p$').sum(axis=1),1.,atol=1e-12)
    np.testing.assert_allclose(p.brier,(p.p-p.outcome)**2,atol=1e-12)
    np.testing.assert_allclose(p.expected_price,p.reference_close*(1+p.predicted_mean),atol=1e-9)
    check(p.p.between(0,1).all(),'Same-law probability score, bucket sums and price means')
    folds=[f for f in r['fold_attempts'] if f['status']=='ok']
    check(all(f['last_endpoint']<f['train_cutoff'] and f['inner_last_endpoint']<f['inner_cutoff'] for f in folds if 'train_cutoff' in f),'Purged inner and mature outer fits, including embargo and earlier cohorts')
    check(all(sha(OUT/f['artifact'])==f['sha256'] for f in folds if 'artifact' in f),'Saved model hashes recorded in batch ledgers')
    global_availability=pd.read_csv(OUT/'new-global-availability.csv')
    check((pd.to_datetime(global_availability.assumed_available,utc=True)<=pd.to_datetime(global_availability.decision,utc=True)).all(),'Foreign cutoff alignment for new FRED series')
    check(all(f['last_endpoint']<f['cutoff'] for f in r['global_intermediate_fits'] if f['status']=='ok'),'Global intermediates matured before their own cutoff')
    integration=read('integration-ledger.json')
    check(all(all(q['endpoint']<f['cutoff'] for q in f['historical_origins']) for f in integration if f['status']=='ok'),'Training-only joint-law learning')
    check(all(f['calibration_fit_last_endpoint']<f['gate_first_origin'] for f in integration if 'gate_first_origin' in f),'Calibrator fitting labels purged from later gate')
    for name in ['invariance','sector-alias']:
        effect=pd.read_csv(OUT/f'{name}-effects.csv');required=effect[effect.required_invariance]
        check(len(required)==(110 if name=='invariance' else 15) and required.passes_tolerance.all(),f'{name} complete laws meet exact-copy tolerance')
    idx=p.set_index(['model','horizon','origin']).sort_index();cols=['p','predicted_mean','predicted_median','crps','brier']
    for key in ['W_RES','W_STRUCT','W_LEVEL']:
        np.testing.assert_allclose(idx.loc[key+'_DEDUP',cols],idx.loc[key+'_CLONE',cols],atol=1e-12)
    check(True,'Copies of leading data configurations leave canonical output unchanged')
    comparison=read('comparisons.json');check(all('simultaneous95_block10' not in c for c in comparison if c['horizon']==21),'Monthly confidence intervals withheld')
    intr=matrix('intraday.csv',OUT)
    check(set(p[p.model=='A_INTRADAY'].origin)<=set(intr.index) and set(p[p.model=='A_INTRADAY_STRICT'].origin)<=set(intr[intr.close_diff_bps<=10].index),
          'Intraday regular session and price discrepancy controls enforced')
    x,_=frames();replay=[];weights=[];atoms=[]
    for f in folds:
        if f.get('model') not in ['R_RESIDUAL','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','M_STATE_SMOOTH']:continue
        if f['model']!='M_STATE_SMOOTH' and f['horizon']!=5:continue
        cfg=r['configurations'][f['model']];q=joblib.load(OUT/f['artifact']);h=f['horizon'];y=matrix(f'labels-{h}.csv');a=x[cfg['frame']]
        tr,ii,vv,test=(q[z] for z in ['training','inner_dates','validation','queries'])
        m=fit(cfg,a.loc[tr],y.loc[tr,'return'].to_numpy());m0=fit(cfg,a.loc[ii],y.loc[ii,'return'].to_numpy())
        residual=y.loc[vv,'return'].to_numpy()-location(m0,a.loc[vv]);risk=a.loc[vv,'p_rv21'].to_numpy()
        laws=predict(m,a.loc[test],residual,risk,np.zeros(len(vv)))
        pred=pd.DataFrame(d.score(y.loc[origin,'return']) for d,origin in zip(laws,test))[cols].to_numpy()
        expected=idx.xs((f['model'],h),level=['model','horizon']).loc[test,cols].to_numpy()
        np.testing.assert_allclose(pred,expected,atol=1e-12)
        replay.append({'model':f['model'],'horizon':h,'fold':f['fold'],'origins':len(test),'max_abs_error':float(abs(pred-expected).max())})
        s=m['scale'];b=m['transform']@m['estimator'].coef_
        for j,c in enumerate(s.cols):weights.append({'model':f['model'],'horizon':h,'fold':f['fold'],'feature':c,'coefficient':b[j],'center':s.mu[j],'scale':s.sd[j],'median':s.med[j],'intercept':m['estimator'].intercept_})
        for origin,d in zip(test,laws):atoms.append({'model':f['model'],'horizon':h,'origin':origin,'endpoint':y.loc[origin,'endpoint'],'atoms':d.a.tolist(),'weights':d.w.tolist()})
    check(sum(f['origins'] for f in replay)==352,'Independent fitted replay of three weekly leads and monthly smoothed state')
    write('retained-feature-weights.csv',pd.DataFrame(weights));(OUT/'retained-endpoint-laws.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in atoms),encoding='utf-8')
    if reports:
        reports=read('report-manifest.json')
        check(len(reports)==17 and all(sha(OUT/name)==d for name,d in reports.items()),'All seventeen requested reports verified')
    save('verification.json',{'passed':True,'completed_at':now(),'checks':checks,'protected_files':old['files'],'replay':replay})
    print('Verified',len(checks),'checks and',sum(f['origins'] for f in replay),'refitted predictions',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prior',action='store_true');parser.add_argument('--reports',action='store_true');args=parser.parse_args()
    if args.prior:prior()
    else:run(args.reports)
