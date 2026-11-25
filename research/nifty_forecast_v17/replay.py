"""Regenerate the published V16/V15 baselines and authenticate their protected inputs."""
from .common import *
from research.nifty_forecast_v16 import replay as old15, model as old_law, session_models as old
from research.nifty_forecast_v16.evidence import bands, pairs


def gap_replay():
    frame,y=old.load()
    wanted=['gift_raw','gift_calibrated','gift_roll_screened','gift_delay10','gift_delay25','equal_six','single_US']
    all_sc=[]; differences={}
    for cut in ('08:30','08:45','08:55','09:10'):
        selected=old.prepare(y,frame[frame.cutoff.eq(cut)].set_index('day').reindex(y.index))
        engine=old.Engine(selected,y)
        engine.run('opening_gap','gap',[m for m in old.opening_specs(cut in ('08:55','09:10')) if m.name in wanted])
        replayed=pd.DataFrame(engine.rows).drop(columns='law')
        label=cut.replace(':','')
        stored=pd.read_csv(V16/f'opening-{label}-scores.csv.gz')
        dup=stored[stored.model.isin(wanted)].merge(replayed,on=['day','cutoff','model'],validate='one_to_one',suffixes=('_old',''))
        assert len(dup)==len(replayed)==len(stored[stored.model.isin(wanted)])
        errors={k:float((dup[k]-dup[k+'_old']).abs().max()) for k in ['p_up','crps','brier','mae','median','lo','hi','covered']}
        assert max(errors.values())<5.e-14,errors
        differences[cut]=dict(n=len(dup),max_error=errors)
        all_sc.append(replayed)
    h=pd.concat(all_sc,ignore_index=True)
    write('baseline-v16-gap-replayed.csv.gz',h)

    rows=[]
    for cutoff in ('08:30','08:45','08:55','09:10'):
        X,Y=old15.panel(cutoff)
        L=pd.read_csv(V16/'v15-replayed-gap-forecasts.csv.gz')
        bench=L[L.cutoff.eq(cutoff)&L.delay.eq(60)&L.model.isin(['offshore_fresh','offshore_prior_only','domestic_prior'])]
        for target in ('immediate_open','next_open_gap'):
            outcome=Y[target].dropna()
            ds=outcome.index.to_numpy()
            deadlines=ds if target=='immediate_open' else Y.index.to_numpy()[1:]
            r=outcome.to_numpy()
            for j,d in enumerate(ds):
                cohort=old15.cohorts(np.array([d]))[0]
                if not cohort:continue
                tr=np.flatnonzero((deadlines<d)&(np.arange(len(ds))<j))[-160:]
                if len(tr)<54:continue
                past=r[tr]
                for name in ('offshore_fresh','offshore_prior_only','domestic_prior'):
                    g=list(old15.old.GROUPS[name])
                    fitted=old15.fit(X.loc[ds[tr],g].to_numpy(),past,95)
                    a=.70*float(fitted.values(X.loc[d,g].to_numpy()))+past-np.median(past)
                    p=(np.count_nonzero(a>0)+.5)/(len(a)+1)
                    b=(p-(r[j]>0))**2
                    q=old15.old.empirical_crps(a,r[j])
                    rows.append(dict(cutoff=cutoff,day=d,target_name=target,cohort=cohort,model=name,p=p,brier=b,crps=q))
    a=pd.DataFrame(rows)
    b=pd.read_csv(V16/'v15-replayed-gap-forecasts.csv.gz')
    b=b[b.delay.eq(60)&b.model.isin(a.model.unique())]
    m=a.merge(b,on=['day','cutoff','target_name','model'],validate='one_to_one',suffixes=('','_v16'))
    assert len(m)==len(a)==len(b)
    errors={k:float((m[k]-m[k+'_v16']).abs().max()) for k in ['p','brier','crps']}
    assert max(errors.values())<3.e-14
    write('baseline-v15-gap-replayed.csv.gz',a)
    e=a[a.cutoff.eq('08:55')].rename(columns={'target_name':'target'})
    e['baseline']='offshore_prior_only'
    old_p=pairs(e,['target'],['brier','crps'])
    save('opening-reproduction.json',dict(v16=differences,v15_rows=len(m),v15_max_errors=errors,baseline_bands=old_p.to_dict('records')))
    print('Re-fit',len(h),'V16 and',len(a),'V15 forecasts across four clocks',flush=True)

def exact_replay():
    keys=pd.read_csv(V16/'v15-v16-gap-common-units.csv.gz')
    q=keys[keys.cutoff.eq('08:55')]
    main=q[q.model.eq('gift_raw')].set_index('day')
    support=main.index
    extra=pd.read_csv(V16/'opening-0855-scores.csv.gz')
    out=[]
    for tag in ('gift_raw','equal_six','single_US','V15_offshore_fresh'):
        g=q[q.model.eq(tag)].set_index('day').reindex(support)
        out.append(dict(experiment='248 matched opening',model=tag,n=len(g),brier=g.brier.mean(),crps=g.crps.mean()))
    # The source archive stores the full variable-width basis-policy inputs and generated scores.
    shift=matrix('offshore-anchor-identity.csv',V16)
    y=matrix('session-targets.csv',V16)
    a=pd.read_csv(V16/'offshore-anchor-sensitivity.csv')
    base=a[a.model.isin(['prior_1515','prior_1530','prior_1540','earlier_quote_buffer','prior_basis_median5'])]
    checked=[]
    for r in base.itertuples(index=False):
        ys=y.gap.to_numpy(float); xx=shift[r.model].reindex(y.index).to_numpy(float)
        i=y.index.get_loc(r.day)
        train=np.flatnonzero(np.isfinite(xx)&(np.arange(len(xx))<i))[-160:]
        residual=ys[train]-xx[train]
        v=old_law.quantify(xx[i]+np.quantile(residual-np.median(residual),old_law.Q),ys[i])
        checked.append(abs(v['brier']-r.brier)+abs(v['crps']-r.crps))
    assert max(checked)<5.e-14
    for zz in ('all','no_large_gaps','non_roll','strict_ordinary_non_roll'):
        g=extra[extra.model.eq('gift_raw')].copy()
        if zz=='no_large_gaps':g=g[g.actual.abs().lt(.01)]
        if 'non_roll' in zz:g=g[g.roll_guard.eq(0)]
        if zz=='strict_ordinary_non_roll':
            dates=pd.to_datetime(y.index)
            prev=pd.to_datetime(y.origin)
            ok=(np.busday_count(prev.to_numpy(dtype='datetime64[D]'),dates.to_numpy(dtype='datetime64[D]'))<=1)&(dates.dayofweek<5)&y.regular_weekday.eq(1)
            g=g[g.day.isin(y.index[ok])]
        out.append(dict(experiment='08:55 '+zz,model='gift_raw',n=len(g),brier=g.brier.mean(),crps=g.crps.mean()))

    c=pd.read_csv(V16/'session-continuation-scores.csv.gz')
    np.testing.assert_allclose((c.p-c.actual)**2,c.brier,atol=2.e-15)
    s=pd.read_csv(V16/'first-touch-fill-scores.csv.gz')
    with np.load(V16/'gap-fill-time-laws.npz',allow_pickle=False) as z:
        laws=z['prob']
    assert len(s)==len(laws)
    vals=[]
    for i,r in enumerate(s.itertuples(index=False)):
        opened=1 if r.cutoff=='09:25' else 12
        a=laws[i].astype(float)
        curve=np.cumsum(a)[opened+1:76]
        actual=np.arange(opened+1,76)>=r.actual_bar
        vals.append(np.mean((curve-actual)**2))
    np.testing.assert_allclose(vals,s.integrated_brier,atol=2.e-6,rtol=0)
    # Check V16 information decay by recompiling the registered two nested estimators.
    z,y=old.load()
    f=old.prepare(y,z[z.cutoff.eq('08:55')].set_index('day').reindex(y.index))
    e=old.Engine(f,y)
    for target in old.DTARGETS:
        cohort=y['cohort_'+target].to_numpy() if target in ('five','twentyone') else None
        e.run('pre_session_decay',target,[m for m in old.decay_specs(False) if m.name in
              ('domestic','eq_fresh','eq_lag1','eq_lag2','eq_lag5','eq_lag17','gift_conditional','eq_smooth')],cohort)
    sc=pd.DataFrame(e.rows)
    src=pd.read_csv(V16/'decay-0855-scores.csv.gz')
    q0=sc.merge(src[src.exercise.eq('pre_session_decay')&src.model.isin(sc.model.unique())],
                on=['day','target','model','cutoff'],validate='one_to_one',suffixes=('','_prior'))
    assert len(q0)==len(sc)
    np.testing.assert_allclose(q0.crps,q0.crps_prior,atol=3.e-14,rtol=0)
    np.testing.assert_allclose(q0.brier,q0.brier_prior,atol=3.e-14,rtol=0)
    write('baseline-v16-decay-scores.csv.gz',sc)
    write('reproduced-opening-sensitivity.csv',pd.DataFrame(out))
    write('reproduced-continuation.csv',c.groupby(['cutoff','target','model'],as_index=False).agg(n=('day','size'),brier=('brier','mean')))
    write('reproduced-survival.csv',s.assign(computed_integrated=vals).groupby(['cutoff','threshold','model'],as_index=False).agg(
          n=('day','size'),brier=('brier','mean'),integrated_brier=('computed_integrated','mean')))
    save('session-baseline-reproduction.json',dict(anchor_values=len(checked),anchor_max_diff=max(checked),decay_rows=len(sc),
          continuation_rows=len(c),time_laws=len(laws),maximum_timing_error=float(np.max(abs(np.array(vals)-s.integrated_brier)))))
    print('Replayed rollover, anchor and decay; verified',len(s),'survival forecasts',flush=True)

def earlier():
    from research.nifty_forecast_v16.common import OUT as prior
    manifest=read('manifest.json',prior)
    checked=[]
    for f,r in manifest['artifacts'].items():
        assert sha(prior/f)==r['sha256'],f
        checked.append(f)
    for f,h in manifest['source_code'].items():
        assert sha(ROOT/f)==h,f
    save('predecessor-protection.json',dict(passed=True,checked=len(checked),source_files=len(manifest['source_code']),
        earlier=read('predecessor-protection.json',prior),v16_manifest=sha(prior/'manifest.json')))
    print('Verified all',len(checked),'V16 files and the inherited protection chain',flush=True)

if __name__=='__main__':
    import sys
    {'opening':gap_replay,'sessions':exact_replay,'protect':earlier}[sys.argv[1]]()
