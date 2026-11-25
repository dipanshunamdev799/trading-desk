"""Independent verification of V14 causality, saved laws, passage probabilities and delivery."""
from concurrent.futures import ThreadPoolExecutor

from .common import *
from .generation import TICK
from .path_score import summaries
from .signals import fit_logistic
from .volatility import robust_design,design_apply


def temporal():
    ys={h:matrix(f'targets-{h}.csv') for h in HORIZONS}
    audit=[]
    models=read('signal-fit-ledger.json')
    for input_,key in [(models['fits'],'training_dates'),(read('endpoint-fits.json'),'train_origins')]:
        for k in input_:
            h=k['horizon']; cutoff=k.get('cutoff',k.get('origin'))
            assert k['last_mature']<cutoff
            assert ys[h].loc[k[key],'endpoint'].max()==k['last_mature']
    calibration=pd.read_csv(OUT/'standalone-calibrated-intervals.csv.gz')
    known=calibration.max_calibration_endpoint.notna()
    assert calibration.loc[known,'max_calibration_endpoint'].lt(calibration.loc[known,'origin']).all()
    if known.any():
        assert (calibration.loc[known,'upper']>=calibration.loc[known,'lower']).all()
    for r in read('joint-path-ledger.json')['rows']:
        cutoff=r['origin']
        assert r['causal_surface_day']<cutoff
        assert ys[5].loc[r['prior_fit_origins'],'endpoint'].max()==r['last_mature']<cutoff
        assert ys[21].loc[r['block_training'],'endpoint'].max()==r['block_last_mature']<cutoff
        assert all(a['last'] is None or a['last']<cutoff for a in r['calibration_history'])
    for k in read('process-fits.json'):
        assert FIRST<=k['fit_first']<=k['fit_last']<=k['origin']<=FREEZE
    offshore=pd.read_csv(V13/'foreign-risk-clock.csv')
    assert offshore.source_day.lt(offshore.origin).all()
    assert pd.to_datetime(offshore.available_assumption,utc=True,format='mixed').le(
           pd.to_datetime(offshore.decision,utc=True,format='mixed')).all()
    local=pd.read_csv(OUT/'supplemental-clock.csv')
    assert local.source.lt(local.origin).all()
    for h in HORIZONS:
        x=matrix(f'features-{h}.csv')
        domain=ys[h]
        for origin in domain.index[domain.cohort.notna()][[0,43,106]]:
            sr=domain.iloc[mature(domain,origin,180)]
            train=x.loc[sr.index].copy()
            test=x.loc[[origin]].copy()
            fields=['atm','trailing','iv_skew','finance','breadth5']
            a,b,z=robust_design(train,test,fields)
            train['duplicated_iv']=train.atm
            test['duplicated_iv']=test.atm
            a2,b2,z2=robust_design(train,test,fields+['duplicated_iv'])
            np.testing.assert_array_equal(a,a2)
            np.testing.assert_array_equal(b,b2)
            actual=sr.event_expand.to_numpy()
            beta,_=fit_logistic(a,actual)
            modified=domain.copy()
            modified.loc[modified.endpoint.ge(origin),'event_expand']=1-modified.loc[modified.endpoint.ge(origin),'event_expand']
            equivalent=modified.iloc[mature(modified,origin,180)]
            az=robust_design(x.loc[equivalent.index],x.loc[[origin]],fields)
            coef,_=fit_logistic(az[0],equivalent.event_expand.to_numpy())
            np.testing.assert_array_equal(design_apply(b,beta),design_apply(az[1],coef))
            audit.append(dict(horizon=h,origin=origin,mature=len(sr),exact_feature_copy=True,
                              changed_unmatured_labels_no_effect=True))
    save('timing-verification.json',dict(sentinels=audit,signal_fits=len(models['fits']),calibration_rows=len(calibration),
         earlier_foreign_clocks=len(offshore),extra_market_clocks=len(local)))
    return len(audit)


def laws():
    package=read('joint-path-ledger.json')
    order=pd.read_csv(OUT/'path-ordering.csv.gz',low_memory=False,dtype={'barrier':str})
    bars=pd.read_csv(OUT/'path-passage.csv.gz',low_memory=False,dtype={'barrier':str})
    key=['horizon','origin','model','barrier']
    order=order.set_index(key)
    a=bars[bars.side.eq('upper')].set_index(key)
    b=bars[bars.side.eq('lower')].set_index(key).reindex(a.index)
    order=order.reindex(a.index)
    np.testing.assert_allclose(order.p_both+order.p_neither,1-a.p_touch-b.p_touch+2*order.p_both,atol=3.e-12)
    np.testing.assert_allclose(order.p_upper_first+order.p_lower_first+order.p_same_candle+order.p_neither,1.,atol=3.e-12)
    assert np.all(order.p_both<=np.minimum(a.p_touch,b.p_touch)+1.e-12)
    assert not bars.duplicated(key+['side']).any()
    assert bars.p_touch.ge(bars.p_close-1.e-12).all() and bars.p_close.ge(bars.p_endpoint-1.e-12).all()
    assert bars.p_touch.between(0,1).all()
    f=bars[bars.barrier.isin(list('01234'))].copy()
    ordered=f.sort_values('threshold').groupby(['horizon','origin','model','side']).p_touch.diff()
    assert ordered.dropna().le(1.e-12).all()
    p=f.pivot(index=['origin','model','side','barrier'],columns='horizon',values='p_touch').dropna()
    assert p[5].le(p[21]+1.e-12).all()
    roundoff=0.
    for r in bars[['horizon','p_by_session','p_touch']].itertuples(index=False):
        vals=np.asarray(json.loads(r.p_by_session))
        assert len(vals)==r.horizon and np.diff(vals).min()>=-1.e-12
        roundoff=max(roundoff,abs(vals[-1]-r.p_touch))
    assert roundoff<6.e-11
    assert len(package['rows'])==265
    def verify_record(r):
        file=OUT/r['file']
        assert sha(file)==r['sha256']
        with np.load(file,allow_pickle=False) as z:
            w=z['joint_pit_weights']
            assert np.isclose(w.sum(),1.) and np.all(w>0)
            for m in z.files:
                if m=='joint_pit_weights':
                    continue
                a=z[m]
                assert a.shape==(N,21,4) and a.dtype.kind=='i'
                assert np.all(a[:,:,1]>=np.maximum(a[:,:,0],a[:,:,3]))
                assert np.all(a[:,:,2]<=np.minimum(a[:,:,0],a[:,:,3]))
        return len(package['models'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        count=sum(pool.map(verify_record,package['rows']))
    selected=[r for i,r in enumerate(package['rows']) if i in (0,36,111,198,230,264) or r['origin']==DEMO]
    points=pd.read_csv(OUT/'path-marginals.csv.gz',low_memory=False)
    sub=points.set_index(['horizon','origin','model','target'])
    s=0
    for r in selected:
        d=r['origin']
        with np.load(OUT/r['file'],allow_pickle=False) as z:
            for n in ('constant_iv','gjr_iv','joint_pit','joint_tail_width'):
                filename='path_mixture' if n=='joint_pit' else n
                w=z['joint_pit_weights'] if n=='joint_pit' else np.full(N,1/N)
                for h in HORIZONS:
                    key=(h,d,n,'range')
                    if key not in sub.index:
                        continue
                    ar=np.exp(z[filename][:,:h].astype(float)*TICK)
                    range_=ar[:,:,1].max(axis=1)-ar[:,:,2].min(axis=1)
                    value=sub.loc[key]
                    score=summaries(range_,np.array([value.actual]),w)[0]
                    for k in ['crps','predicted_mean','q025','q975','coverage95']:
                        np.testing.assert_allclose(score[k],value[k],atol=3.e-12)
                    s+=1
    return dict(verified_joint_models=count,joint_common_origin_probability_rows=len(p),passage_rows=len(bars),
                ordering_rows=len(order),max_cdf_roundtrip_error=roundoff,independent_marginal_scores=s)


def check():
    assert read('prior-protection.json')['pass_']
    assert read('reproduction.json')['status']=='passed'
    sentinels=temporal()
    result=laws()
    forecast=pd.read_csv(OUT/'endpoint-attribution.csv').set_index(['horizon','origin','model'])
    with np.load(OUT/'standalone-endpoint-laws.npz',allow_pickle=False) as z:
        keys=z['keys']
        offsets=z['offsets']
        atoms=z['atoms']
        weights=z['weights']
    assert len(keys)==len(forecast) and offsets[-1]==len(weights)==len(atoms)
    np.testing.assert_allclose(np.add.reduceat(weights,offsets[:-1]),1.,atol=1.e-12,rtol=0)
    assert np.isfinite(atoms).all() and (atoms>-1.).all() and (weights>=0.).all()
    for i in range(0,len(keys),97):
        horizon,day,name,finish=keys[i]
        assert FIRST<=day<finish<=FREEZE
        a,b=offsets[i:i+2]
        r=forecast.loc[int(horizon),day,name]
        scored=summaries(atoms[a:b],np.array([r.actual]),weights[a:b])[0]
        np.testing.assert_allclose(scored['crps'],r.crps,atol=3.e-12,rtol=0)
    save('verification.json',dict(passed=True,
           previous_hashes=read('prior-protection.json')['files'],v13_reference_replay=read('reproduction.json'),
           sentinels=sentinels,standalone_endpoint_laws=len(keys),**result))
    print('Verified',result['verified_joint_models'],'whole laws and',result['passage_rows'],'barrier forecasts',flush=True)


def deliver():
    import re
    from .report import TITLES
    names=[f'V14_{n}.md' for n in TITLES]
    for name in names+['NIFTY_V14_RESEARCH.md','README.md','MISSION.md']:
        p=OUT/name
        assert p.is_file(),name
        for link in re.findall(r'\]\(([^)]*)\)',p.read_text(encoding='utf-8')):
            if '://' not in link and link!='manifest.json':
                assert (OUT/link).exists(),(name,link)
    assert read('verification.json')['passed']
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json']
    with ThreadPoolExecutor(max_workers=5) as pool:
        digests=list(pool.map(sha,files))
    save('manifest.json',dict(reports=names,verified_at=now(),files={p.relative_to(OUT).as_posix():v for p,v in zip(files,digests)},
         bytes=sum(p.stat().st_size for p in files),source={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(SRC.glob('*.py'))}))
    print('Verified links for',len(names),'reports and hashed',len(files),'V14 artifacts',flush=True)


if __name__=='__main__':
    import sys
    {'check':check,'deliver':deliver}[sys.argv[1]]()
