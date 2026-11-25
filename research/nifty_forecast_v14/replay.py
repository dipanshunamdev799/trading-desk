"""Hash immutable predecessors and recompute V13 benchmark forecasts and losses."""
from concurrent.futures import ThreadPoolExecutor
from scipy.special import ndtr

from .common import *
from research.nifty_forecast_v13 import volatility as v13vol
from research.nifty_forecast_v13.paths import score_distribution as v13_score
from research.nifty_forecast_v13.evaluate import disjoint


def protect():
    v12=read('manifest.json',V12)
    v13=read('manifest.json',V13)
    files={ROOT/n:v for n,v in read('protected-inputs.json',V12)['files'].items()}
    files.update({V12/n:v for n,v in v12['files'].items()})
    files.update({ROOT/n:v for n,v in v12['research_code'].items()})
    files.update({V13/n:v for n,v in v13['files'].items()})
    files.update({SRC.parent/'nifty_forecast_v13'/n:v for n,v in v13['source_code'].items()})
    manifests={V12/'manifest.json':sha(V12/'manifest.json'),V13/'manifest.json':sha(V13/'manifest.json')}
    files.update(manifests)
    def compare(pair):
        p,digest=pair
        return None if p.is_file() and sha(p)==digest else str(p)
    with ThreadPoolExecutor(max_workers=7) as pool:
        bad=[a for a in pool.map(compare,files.items()) if a]
    save('prior-protection.json',dict(pass_=not bad,files=len(files),mismatches=bad,manifests={str(k):v for k,v in manifests.items()}))
    if bad:
        raise ValueError(f'{len(bad)} immutable reference files failed their archive hashes. First failures: {bad[:5]}')
    print('Matched prior-file hashes',len(files),flush=True)


def replay():
    original=pd.read_csv(V13/'scored-volatility.csv',low_memory=False)
    labels={h:matrix(f'targets-{h}.csv',V13) for h in HORIZONS}
    inputs={h:matrix(f'features-{h}.csv',V13) for h in HORIZONS}
    v13_risk=read('volatility-fit-ledger.json',V13)
    ledger={(r['horizon'],r['origin'][:7],r['model']):r for r in v13_risk['fits'] if r['model'] in ('egarch','gjr')}
    vol_ids=['prior_trailing','iv_nearest','iv_bracket','iv_calibrated','egarch','gjr','fixed_iv_rv_0.75']
    vrows=[]
    for h in HORIZONS:
        y=labels[h]
        x=inputs[h]
        raw='iv_nearest' if h==5 else 'iv_bracket'
        for day,t in y[y.cohort.notna()].iterrows():
            val=x.loc[day]
            history=y.index[y.endpoint.lt(day)][-180:]
            clean=history[x.loc[history,[raw,'har21']].notna().all(axis=1)]
            adjustment=np.clip(np.exp(np.median(np.log(y.loc[clean,'volatility']/x.loc[clean,raw]))),.72,1.28)
            ret=x.loc[:day,'market_return'].dropna()*100
            for model in vol_ids:
                if model=='prior_trailing':
                    val0=val.rv21
                elif model in ('iv_nearest','iv_bracket'):
                    val0=val[model]
                elif model=='iv_calibrated':
                    val0=val[raw]*adjustment
                elif model=='fixed_iv_rv_0.75':
                    val0=np.sqrt(.75*val[raw]**2+.25*val.har21**2)
                else:
                    fit=ledger[h,day[:7],model]
                    val0=v13vol.volatility_model(ret,h,model,np.asarray(fit['parameters']))
                a=float(t.volatility)
                q=(a/val0)**2
                vrows.append(dict(horizon=h,origin=day,cohort=t.cohort,model=model,prediction=val0,actual=a,
                                  mae=abs(a-val0),qlike=q-np.log(q)-1,ratio=q,variance_error=val0**2-a**2))
    re=pd.DataFrame(vrows).merge(original[['horizon','origin','model','prediction','mae','qlike']],on=['horizon','origin','model'],suffixes=('','_archive'),validate='one_to_one')
    for k in ('prediction','mae','qlike'):
        np.testing.assert_allclose(re[k],re[k+'_archive'],rtol=5e-10,atol=1e-11)
    write('benchmark-volatility-origins.csv',re)
    prior_out=[]
    for (h,n),a in re.groupby(['horizon','model']):
        prior_out.append(dict(horizon=h,model=n,n=len(a),disjoint=disjoint(a.origin,labels[h]),mae=a.mae.mean(),
                              qlike=a.qlike.mean(),bias=(a.prediction-a.actual).mean()))
    write('benchmark-volatility.csv',pd.DataFrame(prior_out))

    rr=re[re.horizon.eq(5)&re.model.isin(['iv_nearest','iv_calibrated','fixed_iv_rv_0.75'])]
    data=rr[rr.model.eq('iv_nearest')][['origin','prediction','actual']]
    band=pd.cut(data.actual/data.prediction,[0,.65,1,1.35,np.inf],
                labels=['actual <= 65% of IV','65-100% of IV','100-135% of IV','actual > 135% of IV'])
    bucket=pd.Series(band.to_numpy(),index=data.origin)
    rr=rr.assign(bucket=rr.origin.map(bucket),error=rr.prediction-rr.actual)
    write('calibration-qlike-anatomy.csv',rr.groupby(['model','bucket']).agg(n=('origin','size'),mean_actual=('actual','mean'),
        mean_forecast=('prediction','mean'),mae=('mae','mean'),qlike=('qlike','mean'),mean_error=('error','mean'),
        total_qlike=('qlike','sum')).reset_index())

    old=pd.read_csv(V13/'distribution-predictions.csv',low_memory=False)
    exact=pd.read_csv(V13/'exact-and-analytic-path-controls.csv',low_memory=False)
    d13=pd.read_csv(V13/'distribution-and-path-leaderboard.csv',low_memory=False)
    bar_ledger=pd.read_csv(V13/'touch-family-loss.csv',low_memory=False)
    bpred=pd.read_csv(V13/'barrier-predictions.csv.gz',low_memory=False)
    drows, bar_rows=[],[]
    path_max=0.
    for h in HORIZONS:
        with np.load(V13/f'joint-path-target-atoms-{h}.npz',allow_pickle=False) as z:
            ids=z['keys']; v=z['values']; names=z['targets'].tolist()
        d13ref=old[old.horizon.eq(h)&old.target.eq('range')].set_index(['origin','model'])
        for j,(day,n) in enumerate(ids):
            if n not in ('diffusion_iv','iv_scaled','rv_scaled'):
                continue
            r=labels[h].loc[day]
            values=v[j,:,names.index('range')]
            k=v13_score(values,r['range'])
            native=d13ref.loc[day,n]
            path_max=max(path_max,abs(native.crps-k['crps']),abs(native.mae-k['mae']))
            np.testing.assert_allclose([k['crps'],k['mae']],[native.crps,native.mae],atol=5e-9)
            drows.append(dict(horizon=h,origin=day,model='V13_'+n,target='range',actual=r['range'],**k))
        with np.load(V13/f'observed-paths-{h}.npz',allow_pickle=False) as z:
            observed=z['paths']
        for day,r in labels[h][labels[h].cohort.notna()].iterrows():
            t=mature(labels[h],day,210)
            hist=observed[t]
            values=hist[:,:,1].max(axis=1)-hist[:,:,2].min(axis=1)
            drows.append(dict(horizon=h,origin=day,model='V13_empirical_exact',target='range',actual=r['range'],**v13_score(values,r['range'])))
            for j,threshold in enumerate(BARRIERS):
                for side in ('upper','lower'):
                    y=bool(r[f'{side}_touch_{j}'])
                    if side=='upper':
                        ph=(hist[:,:,1].max(axis=1)>=1+threshold).mean()
                        z=np.log1p(threshold)
                    else:
                        ph=(hist[:,:,2].min(axis=1)<=1-threshold).mean()
                        z=-np.log1p(-threshold)
                    iv=inputs[h].at[day,'iv_nearest' if h==5 else 'iv_bracket']
                    pa=2*ndtr(-z/(iv*np.sqrt(h/252)))
                    key=dict(horizon=h,origin=day,barrier=str(j),event=side+'_touch',actual=y)
                    bar_rows.extend([{**key,'model':'empirical_exact','p':ph},{**key,'model':'analytic_iv_diffusion','p':pa}])
    bnew=pd.DataFrame(bar_rows).assign(brier=lambda f:(f.p-f.actual)**2)
    bt=bpred[bpred.model.isin(['diffusion_iv','iv_scaled'])&bpred.barrier.isin(list('01234'))&bpred.event.isin(['upper_touch','lower_touch'])].copy()
    bt['brier']=(bt.p-bt.actual)**2
    all_b=pd.concat([bnew,bt[bnew.columns]],ignore_index=True)
    sum_b=all_b.groupby(['horizon','origin','model']).brier.mean().reset_index()
    ctrl=sum_b.merge(bar_ledger,on=['horizon','origin','model'],suffixes=('','_archive'),validate='one_to_one')
    np.testing.assert_allclose(ctrl.brier,ctrl.brier_archive,atol=3e-12)
    write('benchmark-touch-origins.csv',sum_b)
    write('benchmark-touch.csv',sum_b.groupby(['horizon','model']).brier.agg(['size','mean']).reset_index())
    a=pd.DataFrame(drows)
    prior=a[a.model.eq('V13_empirical_exact')].merge(exact[exact.target.eq('range')],on=['horizon','origin','target'],suffixes=('','_archive'))
    np.testing.assert_allclose(prior.crps,prior.crps_archive,atol=1e-11)
    write('benchmark-range-origins.csv',a)
    write('benchmark-range.csv',a.groupby(['horizon','model']).agg(n=('crps','size'),crps=('crps','mean'),mae=('mae','mean'),
         cov80=('coverage80','mean'),width80=('width80','mean')).reset_index())
    end_ids=['PH_NATIVE_PHASE_MIXTURE__scale_only','J12_GROUP_BALANCED__scale_only','B_CHANGE',
             'V8_W_STRUCT_EMBARGO_EQ','NEUTRAL','NEUTRAL__scale_only','V12_NATIVE_RV','J12_Q_GROUP']
    endpoint_parts=[old[old.target.eq('endpoint_return')],pd.read_csv(V13/'protected-rescaled-endpoint.csv',low_memory=False)]
    for n in ['reproduced-endpoint.csv','protected-endpoint.csv']:
        end=pd.read_csv(V13/n,low_memory=False)
        end=end.assign(target='endpoint_return',actual=end.realized_return)
        endpoint_parts.append(end)
    end=pd.concat(endpoint_parts,ignore_index=True)
    end=end[end.model.isin(end_ids)]
    assert not end.duplicated(['horizon','origin','model']).any()
    np.testing.assert_allclose((end.p-end.actual.gt(0))**2,end.brier,atol=3e-12)
    report=d13[d13.target.eq('endpoint_return')&d13.model.isin(end_ids)].copy()
    for row in report.itertuples():
        g=end[end.model.eq(row.model)&end.horizon.eq(row.horizon)]
        if row.cohort!='combined':
            g=g[g.origin.map(labels[row.horizon].cohort).eq(row.cohort)]
        assert len(g)==row.n
        np.testing.assert_allclose([g.brier.mean(),g.crps.mean()],[row.brier,row.crps],atol=3e-12)
    write('benchmark-endpoint-origins.csv',end)
    write('benchmark-endpoint.csv',report)
    save('reproduction.json',dict(status='passed',risk_rows=len(re),risk_max_abs_error=float(abs(re.prediction-re.prediction_archive).max()),
        range_rows=len(a),maximum_range_replay_delta=path_max,barrier_rows=len(all_b),endpoint_rows=len(end),
        method='V13 archived fits and original features for volatility. V13 saved empirical joint atoms or exact mature paths for range. Raw-IV reflection control for analytic touches. Protected per-origin law scores for the exact endpoint baselines.'))
    print('Reproduced V13 risk, range, touch and endpoint benchmark groups',flush=True)


if __name__=='__main__':
    import sys
    {'protect':protect,'replay':replay}[sys.argv[1]]()
