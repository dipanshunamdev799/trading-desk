"""Independent predecessor hash audit and exact benchmark re-scoring."""
from concurrent.futures import ThreadPoolExecutor
from scipy.stats import chi2

from .common import *
from research.nifty_forecast_v14.path_score import summaries, log_brier, indices
from research.nifty_forecast_v14.generation import TICK
from research.nifty_forecast_v13.volatility import volatility_model


def protect():
    files={ROOT/n:v for n,v in read('protected-inputs.json',V12)['files'].items()}
    for release in (V12,V13,V14):
        m=read('manifest.json',release)
        files.update({release/n:v for n,v in m['files'].items()})
        if 'source' in m:
            files.update({ROOT/n:v for n,v in m['source'].items()})
        if 'research_code' in m:
            files.update({ROOT/n:v for n,v in m['research_code'].items()})
        if 'source_code' in m:
            files.update({SRC.parent/release.parent.parent.name/n:v for n,v in m['source_code'].items()})
        files[release/'manifest.json']=sha(release/'manifest.json')
    def bad(item):
        f,d=item
        return str(f) if not f.is_file() or sha(f)!=d else None
    with ThreadPoolExecutor(max_workers=7) as p:
        failures=[r for r in p.map(bad,files.items()) if r]
    save('protected-receipt.json',dict(files=len(files),valid=not failures,mismatches=failures,
         manifests={f.name+'/'+f.parent.parent.name:v for f,v in files.items() if f.name=='manifest.json' and f.parent in (V12,V13,V14)}))
    if failures:
        raise ValueError(f'{len(failures)} predecessors failed existing hashes, first {failures[:3]}')
    print('Matched',len(files),'predecessor hashes',flush=True)


def predictions():
    registry=read('volatility-fit-ledger.json',V13)
    coeff={(r['horizon'],r['origin'][:7]):r['parameters'] for r in registry['fits'] if r['model']=='gjr'}
    state=read('process-states.json',V14)
    v14=pd.read_csv(V14/'risk-scores-per-origin.csv',low_memory=False)
    v13=pd.read_csv(V13/'scored-volatility.csv',low_memory=False)
    expansions=pd.read_csv(V14/'transition-and-tail-probabilities.csv.gz',low_memory=False)
    risk,volprob,end,path,barriers=[],[],[],[],[]
    B_names={5:'trend_shrink',21:'trend_persistent'}
    fixed_rows=pd.read_csv(V14/'path-passage.csv.gz',usecols=['horizon','origin','model','barrier','side','p_touch','actual'],
                           dtype={'barrier':str})
    fixed_rows=fixed_rows[fixed_rows.barrier.isin(list('01234'))&fixed_rows.model.isin(B_names.values())]
    touch_by=fixed_rows.set_index(['horizon','origin','model','barrier','side'])
    margins=pd.read_csv(V14/'path-marginals.csv.gz',low_memory=False)
    marg=margins[margins.model.isin(['regime_state','gjr_student'])&margins.target.isin(['range','endpoint_return'])].set_index(
        ['horizon','origin','model','target'])
    archive=pd.read_csv(V14/'endpoint-attribution.csv').set_index(['horizon','origin','model'])
    with np.load(V14/'standalone-endpoint-laws.npz',allow_pickle=False) as z:
        lawkeys=z['keys'];offs=z['offsets']
        atoms=z['atoms'];weights=z['weights']
    for h in HORIZONS:
        y=matrix(f'targets-{h}.csv',V14);x=matrix(f'features-{h}.csv',V14)
        v13_x=matrix(f'features-{h}.csv',V13)
        ix=y[y.cohort.notna()]
        assert len(ix)==EXPECTED[h]
        with np.load(V14/f'observed-{h}.npz',allow_pickle=False) as z:
            observed=z['paths']
        for day,row in ix.iterrows():
            rr=v13_x.loc[day]
            risk0=rr.iv_nearest if h==5 else rr.iv_bracket
            old=y[y.endpoint.lt(day)].index[-180:]
            used=old[v13_x.loc[old,['har21','iv_nearest' if h==5 else 'iv_bracket']].notna().all(axis=1)]
            calib=np.clip(np.exp(np.median(np.log(y.loc[used,'volatility']/v13_x.loc[used,'iv_nearest' if h==5 else 'iv_bracket']))),.72,1.28)
            preds={
                'V13_trailing':rr.rv21,
                'V13_raw_ATM' if h==5 else 'V13_bracketed_IV':risk0,
                'V13_calibrated_IV':risk0*calib,
                'V13_75IV25RV':np.sqrt(.75*risk0**2+.25*rr.har21**2),
                'V13_GJR':volatility_model(v13_x.loc[:day,'market_return'].dropna()*100,h,'gjr',np.array(coeff[h,day[:7]])),
                'gjr_ivx':np.sqrt(np.mean(state[day]['gjr_ivx']['variance_curve'][:h])*252)/100,
                'blend_gjr_iv':np.sqrt(np.mean(state[day]['blend_gjr_iv']['variance_curve'][:h])*252)/100,
            }
            for m,p in preds.items():
                ratio=(row.volatility/p)**2
                risk.append(dict(horizon=h,origin=day,cohort=row.cohort,model=m,prediction=p,actual=row.volatility,
                            mae=abs(p-row.volatility),qlike=ratio-np.log(ratio)-1))
            iv=x.at[day,'atm']
            raw=float(chi2.sf(h*(1.25*row.trailing_at_origin/iv)**2,h))
            month=ix.index[ix.index.str[:7]==day[:7]][0]
            hist=y[y.endpoint.lt(month)].tail(185).event_expand.dropna()
            bas=(hist.sum()+.75)/(len(hist)+1.50)
            for name,p in [('iv_raw',raw),('historical',bas)]:
                volprob.append(dict(horizon=h,origin=day,cohort=row.cohort,model=name,p=p,actual=int(row.event_expand),
                                    brier=(p-row.event_expand)**2))
            with np.load(V14/f'joint-paths/{day}.npz',allow_pickle=False) as z:
                allowed=[B_names[h]]+(['gjr_student','regime_state'] if h==21 else [])
                for name in allowed:
                    a=np.exp(TICK*z[name][:,:h])
                    w=np.full(len(a),1/len(a))
                    r=a[:,:,1].max(axis=1)-a[:,:,2].min(axis=1)
                    if h==21 and name in ('gjr_student','regime_state'):
                        values=r if name=='gjr_student' else a[:,-1,3]-1
                        target='range' if name=='gjr_student' else 'endpoint_return'
                        old_m=marg.loc[h,day,name,target]
                        s=summaries(values,np.array([row[target]]),w)[0]
                        np.testing.assert_allclose(s['crps'],old_m.crps,atol=3.e-12)
                        path.append(dict(horizon=h,origin=day,cohort=row.cohort,model=name,target=target,
                                         crps=s['crps'],coverage80=s['coverage80']))
                    if name==B_names[h]:
                        raw=observed[y.index.get_loc(day):y.index.get_loc(day)+1]
                        for j,k in enumerate(BARRIERS):
                            for side in ('upper','lower'):
                                p=float((indices(a,k,side)<=h).mean())
                                actual=int(indices(raw,k,side)[0]<=h)
                                old_b=touch_by.loc[h,day,name,str(j),side]
                                assert old_b.actual==actual and abs(old_b.p_touch-p)<1.e-12
                                barriers.append(dict(horizon=h,origin=day,cohort=row.cohort,model=name,
                                    barrier=k,side=side,brier=(p-actual)**2))
    for i,(h,day,name,finish) in enumerate(lawkeys):
        if (h,name) not in [('5','sign_shrinkage'),('21','domestic_location_gjr_scale')]:
            continue
        p,q=offs[i:i+2]; r=archive.loc[int(h),day,name]
        a=atoms[p:q];w=weights[p:q]
        p_up=float(w@(a>0))
        replay=summaries(a,np.array([r.actual]),w)[0]
        b,l=log_brier(p_up,int(r.actual>0))
        np.testing.assert_allclose([b,replay['crps']],[r.brier,r.crps],atol=2.e-12)
        end.append(dict(horizon=int(h),origin=day,cohort=r.cohort,model=name,brier=b,crps=replay['crps']))
    p=pd.DataFrame(risk)
    compare=p.merge(v14[['horizon','origin','model','prediction']],on=['horizon','origin','model'],
                     validate='one_to_one',suffixes=('','_archived'))
    assert len(compare)==len(p)
    np.testing.assert_allclose(compare.prediction,compare.prediction_archived,atol=3.e-12,rtol=0)
    a=pd.DataFrame(volprob)
    t=a.merge(expansions[expansions.event.eq('expand')][['horizon','origin','model','p']],
              on=['horizon','origin','model'],suffixes=('','_archive'),validate='one_to_one')
    assert len(t)==len(a)
    np.testing.assert_allclose(t.p,t.p_archive,atol=3.e-13,rtol=0)
    output={'volatility':p,'expansion':a,'path':pd.DataFrame(path),'endpoint':pd.DataFrame(end),'touch':pd.DataFrame(barriers)}
    for n,data in output.items():
        write('replay-'+n+'.csv',data)
    save('benchmark-replay.json',dict(passed=True,rows={k:len(v) for k,v in output.items()},
         maximum_risk_delta=float(abs(compare.prediction-compare.prediction_archived).max()),
         maximum_expansion_delta=float(abs(t.p-t.p_archive).max()),
         fixed_touch='V14 OHLC path and original root-relative thresholds independently re-scored',
         weekly_range='V13 diffusion path atoms independently preserved in V14 benchmark-range-origins.csv; match V14 V13_diffusion_iv',
         probability_method='Raw IV standard deviation sets the chi-square variance-tail reference. V14 historical is beta-smoothed frequency by matured monthly fit.'))
    # Retain all requested endpoint benchmarks including separately eligible early and later studies.
    names={'V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO_EQ','J11_BREADTH_ALL','B_CHANGE','V12_NATIVE_RV','NEUTRAL','J11_EXCLUDE_B_ROT'}
    part=pd.read_csv(V13/'protected-endpoint.csv',low_memory=False)
    new=pd.read_csv(V13/'reproduced-endpoint.csv',low_memory=False)
    old=pd.concat([part,new],ignore_index=True)
    allow=old[old.model.isin(names)].copy()
    allow['target']='endpoint_return'
    allow['actual']=allow.realized_return
    v13f=pd.concat([pd.read_csv(V13/'distribution-predictions.csv',low_memory=False),
                    pd.read_csv(V13/'protected-rescaled-endpoint.csv',low_memory=False)],ignore_index=True)
    v13f=v13f[v13f.target.eq('endpoint_return')&v13f.model.isin(
        ['PH_NATIVE_PHASE_MIXTURE__scale_only','J12_GROUP_BALANCED__scale_only','NEUTRAL__scale_only'])]
    v14f=pd.read_csv(V14/'endpoint-attribution.csv',low_memory=False)
    v14f=v14f[((v14f.horizon.eq(5)&v14f.model.eq('sign_shrinkage'))|
                  (v14f.horizon.eq(21)&v14f.model.eq('domestic_location_gjr_scale')))].rename(columns={'p_up':'p','se':'squared_error'})
    keep=['horizon','origin','model','p','brier','crps','log_loss','pinball','mae','squared_error','coverage50',
          'coverage80','width50','width80','q10','q90','predicted_mean','predicted_median','actual']
    merged=pd.concat([g.reindex(columns=keep) for g in (allow,v13f,v14f)],ignore_index=True).drop_duplicates(['horizon','origin','model'])
    names={'PH_NATIVE_PHASE_MIXTURE__scale_only':'V13_IV_all_phase','J12_GROUP_BALANCED__scale_only':'V13_weekly_CRPS',
           'NEUTRAL__scale_only':'V13_IV_symmetric','sign_shrinkage':'V14_sign_shrinkage',
           'domestic_location_gjr_scale':'V14_domestic_GJR'}
    merged['model']=merged.model.replace(names)
    write('earlier-endpoint-references.csv.gz',merged)
    print('Re-scored V14 fixed laws, variance and expansion benchmarks',flush=True)


if __name__=='__main__':
    import sys
    {'protect':protect,'scores':predictions}[sys.argv[1]]()
