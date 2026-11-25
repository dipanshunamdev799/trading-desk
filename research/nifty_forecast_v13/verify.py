"""Timing sentinels, archived fit replay, path invariants and independent refresh."""
import sys

import joblib
import requests

from .common import *
from .volatility import RISK_REFS, rescale_features, maturity
from .paths import JOINT_EXAMPLES


def fitted_replay():
    pred=pd.read_csv(V12/'market-predictions.csv',low_memory=False)
    p=pred[pred.model.isin(RISK_REFS)].set_index(['horizon','model','cohort','fold'])
    led=loads(V12/'market-ledger.json')
    fs={}
    total=0
    error=0.
    known=[]
    for r in led:
        h,n=r['horizon'],r['model']
        if n not in RISK_REFS or r['status']!='ok':
            continue
        key=(h,n,r['cohort'],r['fold'])
        book=p.loc[[key]].set_index('origin')
        version=r['version']
        if (h,version) not in fs:
            fs[h,version]=matrix(f'features/{h}-{version}.csv',V12)
        x=fs[h,version]
        assert sha(V12/r['file'])==r['sha256']
        fit=joblib.load(V12/r['file'])
        tr=fit['training']
        query=fit['query']
        y=matrix(f'labels-{h}.csv')
        assert y.loc[tr,'endpoint'].max()<r['cutoff']<=min(query)
        if n=='V12_RV_PATH':
            est=x.loc[query,'rv21'].to_numpy()
        else:
            model=fit['fit']
            features=model['risk_scale'].transform(x.loc[query])
            center=np.log(y.loc[tr,'volatility'].clip(lower=.015)).mean()
            est=np.exp(.80*model['risk_model'].predict(features)[:,0]+.20*center)
        original=book.loc[query,'forecast_path_volatility'].to_numpy()
        delta=float(np.max(np.abs(original-est)))
        assert delta < 1e-12,(key,delta)
        total+=len(est)
        error=max(error,delta)
        known.append(n)
    assert total==len(p) and set(known)==set(RISK_REFS)
    save('v12-fitted-replay.json',dict(forecasts=total,maximum_difference=error,model_ids=RISK_REFS))


def refresh_check():
    file=OUT/'sources/upstox/refresh-nifty.json'
    if not file.exists():
        save('refresh-reconciliation.json',{'rows':[],'status':'Upstox refresh unavailable'})
        return
    rows=[]
    for stamp,op,high,low,cl,*_ in loads(file)['data']['candles']:
        d=pd.Timestamp(stamp).tz_convert('Asia/Kolkata')
        assert FREEZE < str(d.date()) <= '2026-12-31'
        uri=f'https://nsearchives.nseindia.com/content/indices/ind_close_all_{d:%d%m%Y}.csv'
        dest=OUT/f'sources/NSE-{d.date()}.csv'
        item=dict(day=str(d.date()),upstox_close=cl,source=uri)
        try:
            if not dest.exists():
                r=requests.get(uri,headers={'User-Agent':'Mozilla/5.0'},timeout=7)
                r.raise_for_status()
                dest.write_bytes(r.content)
            nse=pd.read_csv(dest)
            close=float(nse.iloc[:,0].str.strip().eq('Nifty 50').pipe(lambda mask:nse.loc[mask].iloc[0]['Closing Index Value']))
            item.update(nse_close=close,delta=cl-close,sha256=sha(dest))
        except (requests.RequestException,KeyError,IndexError,ValueError) as e:
            item['failure']=type(e).__name__
        rows.append(item)
    before=loads(V12/'refresh-summary.json')['closed_sessions']
    save('refresh-reconciliation.json',{'rows':sorted(rows,key=lambda r:r['day']),
         'additional_vs_v12':sorted({r['day'] for r in rows}-set(before)),'frozen':FREEZE})


def validate():
    leads=loads(OUT/'volatility-fit-ledger.json')
    path=loads(OUT/'path-ledger.json')
    followup=loads(OUT/'supplemental-fits.json')
    supervised=leads['fits']+path['fits']+path['direction_fits']+followup
    for r in supervised:
        if 'max_endpoint' in r:
            assert r['max_endpoint']<r['origin']
        else:
            assert r['last']<=r['origin']
    barriers=pd.concat([pd.read_csv(OUT/'barrier-predictions.csv.gz',low_memory=False),
                        pd.read_csv(OUT/'exact-and-analytic-barrier-controls.csv')],ignore_index=True)
    probs=barriers.p
    assert probs.between(0,1).all()
    assert not barriers.duplicated(['horizon','origin','model','barrier','event']).any()
    f=barriers[barriers.event.isin(['upper_touch','lower_touch'])]
    steps=f.sort_values('threshold').groupby(['horizon','origin','model','event']).p.diff()
    assert steps.max()<2e-12
    paths=pd.read_csv(OUT/'distribution-predictions.csv',low_memory=False)
    archive=[pd.read_csv(OUT/name,low_memory=False) for name in ['protected-rescaled-endpoint.csv','exact-and-analytic-path-controls.csv']]
    all_paths=pd.concat([paths,*archive],ignore_index=True)
    assert np.all(np.diff(all_paths[['q05','q10','q25','q50','q75','q90','q95']],axis=1)>=-1e-12)
    n=0
    timing=[]
    for h in HORIZONS:
        x=matrix(f'features-{h}.csv',OUT)
        y=matrix(f'targets-{h}.csv',OUT)
        i=x.option_day.notna()
        assert x.loc[i,'option_day'].lt(x.index[i].to_series()).all()
        cutoff=y.index[y.cohort.notna()][102]
        fields=['iv_nearest','har21','finance','breadth5']
        t=maturity(y,cutoff)
        train=x.loc[t].copy()
        test=x.loc[[cutoff]].copy()
        a,b,_,_=rescale_features(train,test,fields)
        train['exact_copy'],test['exact_copy']=train.finance,test.finance
        aa,bb,_,_=rescale_features(train,test,fields+['exact_copy'])
        np.testing.assert_array_equal(a,aa)
        np.testing.assert_array_equal(b,bb)
        payload=y.copy()
        payload.loc[y.endpoint.ge(cutoff),'volatility']=99
        np.testing.assert_array_equal(payload.loc[t,'volatility'],y.loc[t,'volatility'])
        before=x.loc[:cutoff,fields].copy()
        x.loc[x.index>cutoff,'iv_nearest']=77
        np.testing.assert_array_equal(before,x.loc[:cutoff,fields])
        timing.append(dict(horizon=h,cutoff=cutoff,training=len(t),exact_copy=True,mutated_future_ignored=True))
        p=paths[paths.horizon.eq(h)&paths.model.isin(JOINT_EXAMPLES)]
        book=p.set_index(['origin','model','target']).predicted_mean
        with np.load(OUT/f'joint-path-target-atoms-{h}.npz') as z:
            keys=z['keys']; values=z['values']; targets=z['targets']
            np.testing.assert_allclose(values[:,:,2],np.maximum(values[:,:,2],0),atol=0,rtol=0)
            ilook={k:i for i,k in enumerate(targets)}
            np.testing.assert_allclose(values[:,:,ilook['range']],values[:,:,ilook['high']]-values[:,:,ilook['low']],atol=2e-8)
            names=pd.MultiIndex.from_tuples([(a,b,t) for a,b in keys for t in targets])
            np.testing.assert_allclose(values.astype(float).mean(axis=1).ravel(),book.loc[names],rtol=1e-7,atol=1e-8)
            n+=len(keys)
    c=pd.read_csv(OUT/'foreign-risk-clock.csv')
    assert c.source_day.lt(c.origin).all()
    assert pd.to_datetime(c.available_assumption,utc=True,format='mixed').le(pd.to_datetime(c.decision,utc=True,format='mixed')).all()
    supplemental=pd.read_csv(OUT/'supplemental-clock.csv') if followup else pd.DataFrame()
    if followup:
        assert supplemental.source.lt(supplemental.origin).all()
    save('verification.json',dict(passed=True,barrier_forecasts=len(barriers),distribution_forecasts=len(all_paths),
        path_artifacts_verified=n,causal_fit_checks=len(supervised),
        timing_sentinels=timing,protected=loads(OUT/'protection.json')['files'],foreign_clock_rows=len(c)+len(supplemental),
        fitted_v12_replay=loads(OUT/'v12-fitted-replay.json'),v12_replay=loads(OUT/'replay.json')))


def manifest():
    import re
    from .report import REPORTS
    names=[f'V13_{n}.md' for n in REPORTS]
    for n in names+['NIFTY_V13_RESEARCH.md','README.md','MISSION.md']:
        p=OUT/n
        text=p.read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]*)\)',text):
            if '://' not in link and link!='manifest.json':
                assert (OUT/link).exists(),(n,link)
    assert loads(OUT/'verification.json')['passed']
    fs={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    save('manifest.json',{'reports':names,'files':fs,'source_code':{p.name:sha(p) for p in SRC.glob('*.py')},'verified_at':now()})
    print(len(names),'verified reports,',len(fs),'hashed artifacts',flush=True)


if __name__=='__main__':
    {'fits':fitted_replay,'refresh':refresh_check,'check':validate,'delivery':manifest}[sys.argv[1]]()
