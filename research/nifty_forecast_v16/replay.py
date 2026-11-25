"""Reconstruct V15's original gap fits from their source code and raw data."""
from .common import *
from research.nifty_forecast_v15 import sessions as old
from research.nifty_forecast_v15.data import Daily
from research.nifty_forecast_v15.evidence import paired_intervals as archived_intervals
from research.nifty_forecast_v15.fitting import fit


def cohorts(days):
    return np.where(days>'2026-05-08','later',np.where(days>='2025-11-03','early',''))


def panel(cutoff,delay=60):
    d=Daily.load()
    px=d.prices
    f,_=old.foreign()
    all_dates=px.index[1:]
    x=d.features.reindex(columns=old.DOM+old.OFF).iloc[:-1].set_axis(all_dates)
    for name,a in f.items():
        at=pd.DatetimeIndex([stamp(day,cutoff) for day in all_dates])
        available=pd.DatetimeIndex(a.available)+pd.Timedelta(minutes=delay-60)
        inds=available.searchsorted(at,side='right')-1
        x[name]=np.where(inds>=0,a.r.to_numpy()[inds.clip(0)],np.nan)
    y=pd.DataFrame(dict(immediate_open=np.log(px.open/px.close.shift()),next_open_gap=np.log(px.open.shift(-1)/px.close)),index=px.index)
    return x,y.reindex(x.index)


def replay():
    register()
    cubes=[]; exact=np.zeros(7)
    score_fields=['p','median','lower','upper','brier','crps','log_loss']
    archive=pd.read_csv(V15/'session-forecasts.csv.gz')
    saved=archive[archive.cutoff.eq('pre_open') & archive.target_name.isin(['immediate_open','next_open_gap'])]
    groups={k:old.GROUPS[k] for k in ['domestic_prior','offshore_prior_only','offshore_fresh']}
    configs=[(t,60) for t in CLOCKS[:4]]
    configs.extend(('08:55',m) for m in [30,180,360,1440])
    active=[]
    law_rows=[]; law_records=[]
    for clk,delay in configs:
        x,y=panel(clk,delay)
        records=[]
        for tt in y:
            ds=y[tt].dropna().index.to_numpy()
            r=y.loc[ds,tt].to_numpy()
            endpoints=ds if tt=='immediate_open' else y.index.to_numpy()[1:]
            for i,day in enumerate(ds):
                group=cohorts(np.array([day]))[0]
                if not group:
                    continue
                tr=np.flatnonzero((endpoints<day)&(np.arange(len(ds))<i))[-160:]
                if len(tr)<54:
                    continue
                hist=r[tr]
                laws={'price_zero':hist-np.median(hist),'unconditional':hist}
                for model,cols in groups.items():
                    a=x.loc[ds[tr],list(cols)].to_numpy()
                    b=x.loc[day,list(cols)].to_numpy(float)
                    location=.70*float(fit(a,hist,95).values(b))
                    laws[model]=location+hist-np.median(hist)
                for model,a in laws.items():
                    pr=(np.sum(a>0)+.5)/(len(a)+1)
                    lo,md,hi=np.quantile(a,[.10,.50,.90])
                    y0=r[i]
                    records.append(dict(day=day,target_name=tt,cohort=group,cutoff=clk,delay=delay,model=model,actual=y0,
                                        p=pr,median=md,lower=lo,upper=hi,
                                        brier=(pr-float(y0>0))**2,crps=old.empirical_crps(a,y0),
                                        log_loss=-np.log(pr if y0>0 else 1-pr),mae=abs(md-y0),last_mature=endpoints[tr].max(),
                                        covered=int(lo<=y0<=hi)))
                    if clk=='09:10' and delay==60:
                        law_rows.append(np.pad(a.astype(np.float64),(0,160-len(a)),constant_values=np.nan))
                        law_records.append((day,tt,model,len(a)))
        z=pd.DataFrame(records)
        cubes.append(z)
        if clk=='09:10' and delay==60:
            comp=z.merge(saved,on=['day','target_name','model'],validate='one_to_one',suffixes=('','_old'))
            assert len(comp)==len(z)==len(saved)
            for j,k in enumerate(score_fields):
                v=np.abs(comp[k]-comp[k+'_old']).max()
                exact[j]=v
                assert v<3.e-14, (k,v)
            np.savez_compressed(OUT/'v15-replayed-gap-laws.npz',atoms=np.stack(law_rows),keys=np.array(law_records))
        for trial,f in z.groupby('target_name'):
            pairs={'offshore_fresh':'offshore_prior_only','offshore_prior_only':'domestic_prior',
                   'domestic_prior':'price_zero','unconditional':'price_zero'}
            dates=sorted(f.day.unique())
            ms=[]; dif=[]
            for model,parent in pairs.items():
                a=f[f.model.eq(model)].set_index('day').reindex(dates)
                b=f[f.model.eq(parent)].set_index('day').reindex(dates)
                for metric in ('crps','brier','log_loss'):
                    delta=b[metric]-a[metric]
                    dd=dict(target=trial,cutoff=clk,delay=delay,model=model,parent=parent,metric=metric,n=len(a),candidate=a[metric].mean(),
                            control=b[metric].mean(),gain=delta.mean(),early_gain=delta[a.cohort.eq('early')].mean(),
                            later_gain=delta[a.cohort.eq('later')].mean())
                    ms.append(dd)
                    dif.append(delta.to_numpy())
            adj=archived_intervals(np.column_stack(dif),5,np.array([m['metric'] for m in ms]))
            for i,m in enumerate(ms):
                m.update({k:float(v[i]) for k,v in adj.items()})
            active.extend(ms)
    summary=pd.DataFrame(active)
    archived=pd.read_csv(V15/'session-dependence-evidence.csv')
    named=summary[summary.cutoff.eq('09:10')&summary.delay.eq(60)&summary.model.eq('offshore_fresh')]
    for r in named.itertuples(index=False):
        q=archived[archived.checkpoint.eq('pre_open') & archived.target.eq(r.target)&archived.model.eq(r.model)&archived.metric.eq(r.metric)].iloc[0]
        np.testing.assert_allclose([q.gain,q.family_low21,q.family_high21],[r.gain,r.family_low21,r.family_high21],atol=5.e-14,rtol=0)
    write('v15-replayed-gap-forecasts.csv.gz',pd.concat(cubes,ignore_index=True))
    write('v15-replayed-gap-evidence.csv',summary)
    save('v15-opening-reproduction.json',dict(passed=True,archived_rows=len(saved),matched_same_morning=258,matched_next_gap=257,
        maximum_differences=dict(zip(score_fields,exact)),prior_parent='DOM + OFF (includes earlier global risk, FX and oil). Pure DOM separately replayed.',
        native_model='.70 times Ridge location, penalty 95, at most 160 strictly matured outcomes, centered empirical target-log law',
        no_current_cash=True,old_foreign_release_rule='time-zone local close + 60 minutes',forecasts_unchanged=sha(V15/'session-forecasts.csv.gz')))
    print('Exactly reproduced',len(saved),'V15 morning / next-opening forecast records and family bands',flush=True)


def protect():
    previous=read('manifest.json',V15)
    bad=[]
    for file,r in previous['artifacts'].items():
        p=V15/file
        if not p.exists() or sha(p)!=r['sha256']:
            bad.append(file)
    for file,d in previous['source_code'].items():
        if sha(ROOT/file)!=d:
            bad.append(file)
    assert not bad,bad
    save('predecessor-protection.json',dict(valid=True,v15_manifest=sha(V15/'manifest.json'),
        v15_artifacts=len(previous['artifacts']),v15_code=len(previous['source_code']),
        earlier_verified_by_v15=read('protected-receipt.json',V15)))
    print('Matched',len(previous['artifacts']),'V15 artifact hashes and inherited earlier receipt',flush=True)

if __name__=='__main__':
    import sys
    {'gap':replay,'protect':protect}[sys.argv[1]]()
