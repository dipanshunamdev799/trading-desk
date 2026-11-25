"""Verify source availability, exact endpoints, stored laws and future-information isolation."""
from .common import *
from .residual import Engine,STOCK,BIN_TARGETS


def times(x):
    return pd.to_datetime(x,utc=True,format='mixed')


def sentinels(f,y):
    f=f.join(f.groupby('day')[list(STOCK)].shift(1).add_prefix('earlier_'))
    rows=[]
    for clock,key in [('09:25','r30'),('10:20','regular_residual'),('10:20','remaining_21'),('09:25','remaining_vol'),('10:20','touch_down')]:
        x=f[f.cutoff.eq(clock)].set_index('day').copy()
        truth=y[y.cutoff.eq(clock)].set_index('day')
        forecasts=pd.read_csv(OUT/f'residual-{clock.replace(":","")}-scores.csv.gz',usecols=['day','cohort','target','model'])
        supported=forecasts[forecasts.target.eq(key)].groupby(['cohort','day']).size()
        dates=[]
        for cohort in ('early','later'):
            pool=supported.loc[cohort]
            common=pool[pool.eq(pool.max())].index
            dates.append(common[len(common)//2])
        for day in dates:
            t=truth.copy()
            assert day in x.index and np.isfinite(t.at[day,key])
            known_end=t['end_'+key].astype('string')
            t.loc[t.index!=day,'cohort']=''
            main=Engine(x,t,clock)
            main.run(key)
            future=x.columns[x.dtypes.map(pd.api.types.is_numeric_dtype)]
            x1=x.copy()
            for c in future:
                x1[c]=x1[c].astype(float)
            x1.loc[x1.index>day,future]=77.0
            t1=t.copy()
            alter=(known_end>=day)&t1[key].notna()
            if key in BIN_TARGETS:
                t1.loc[alter,key]=1.-t1.loc[alter,key]
            else:
                t1[key]=t1[key].astype(float)
                t1.loc[alter,key]=.43-t1.loc[alter,key]
            changed=Engine(x1,t1,clock)
            changed.run(key)
            assert [k['model'] for k in main.rows]==[k['model'] for k in changed.rows]
            assert len(main.rows)>0
            np.testing.assert_array_equal(np.stack(main.atoms),np.stack(changed.atoms))
            np.testing.assert_array_equal([r['p'] for r in main.rows],[r['p'] for r in changed.rows])
            rows.append(dict(day=day,cutoff=clock,target=key,laws=len(main.rows),changed_future_feature_rows=int((x.index>day).sum()),
                        changed_unmatured_labels=int(alter.sum()),max_difference=0))
    return rows


def run():
    f=pd.read_csv(OUT/'intraday-feature-panel.csv.gz',low_memory=False)
    t=pd.read_csv(OUT/'intraday-target-panel.csv.gz',low_memory=False)
    s=pd.read_csv(OUT/'stock-snapshots.csv.gz',low_memory=False)
    g=pd.read_csv(OUT/'gift-decision-clock.csv')
    a=pd.read_csv(OUT/'announcement-availability.csv.gz')
    assert list(f[['day','cutoff']].itertuples(index=False,name=None))==list(t[['day','cutoff']].itertuples(index=False,name=None))
    assert times(f.feature_last_bar).add(pd.Timedelta(minutes=5)).le(times(f.decision)).all()
    assert times(t.target_first_bar).ge(times(f.decision)).all()
    assert s.cutoff.notna().all()
    assert times(s.cutoff_bar_end).add(pd.Timedelta(minutes=5)).le(times(s.day+'T'+s.cutoff+':00+05:30')).all()
    assert times(g.latest_available).le(times(g.decision)).all()
    assert times(a.disseminated).add(pd.Timedelta(minutes=5)).eq(times(a.eligible)).all()
    assert (s.day.between(FIRST,FREEZE)).all() and (f.day.between(FIRST,FREEZE)).all()
    assert f.old_cash.lt(f.day).all()
    assert f.loc[f.option_source.notna(),'option_source'].lt(f.loc[f.option_source.notna(),'day']).all()
    o=pd.read_csv(OUT/'original-cutoff-audit.csv')
    assert o.max_label_end.lt(o.maturity_guard_day).all()
    assert o.target.ge(o.day).all()
    targets=matrix('original-target-panel.csv')
    for h in HORIZONS:
        target='original'+str(h)
        official=matrix(f'targets-{h}.csv',V14).endpoint_return
        k=targets[f'cohort_{h}'].notna()
        np.testing.assert_allclose(np.expm1(targets.loc[k,target]),official.loc[targets.loc[k,'origin']],atol=3e-14,rtol=0.)
        assert int(k.sum())==EXPECTED[h]
    same_vol=pd.read_csv(OUT/'postopen-volatility-scores.csv.gz')
    prior_vol=pd.read_csv(V16/'volatility-scores.csv.gz')
    vol=same_vol[same_vol.model.eq('cash_risk')].merge(prior_vol[prior_vol.model.eq('raw_iv')],
          on=['horizon','cutoff','day'],validate='1:1')
    np.testing.assert_array_equal(vol.actual,vol.actual_vol)
    np.testing.assert_array_equal(vol.expansion,vol.actual_expand)
    laws=[]
    for clock in SESSION_CLOCKS:
        tag='residual-'+clock.replace(':','')
        d=pd.read_csv(OUT/(tag+'-scores.csv.gz'),low_memory=False)
        with np.load(OUT/(tag+'-laws.npz'),allow_pickle=False) as stored:
            ar=stored['atoms']
        assert len(d)==len(ar) and np.all(d.law.to_numpy()==np.arange(len(d))) and np.isfinite(ar).all()
        assert d.last_mature.lt(d.day).all()
        assert d.day.between(FIRST,FREEZE).all()
        isbin=d.target.isin(BIN_TARGETS)
        valid=d.brier.notna()&~isbin&~d.model.eq('neutral')
        np.testing.assert_allclose((ar[valid]>0).mean(axis=1),d.loc[valid,'p'],rtol=0,atol=1/128)
        if isbin.any():
            np.testing.assert_allclose(ar[isbin].mean(axis=1),d.loc[isbin,'p'],rtol=0,atol=1/128)
        laws.append(dict(cutoff=clock,n=len(d),dates=d.day.nunique(),targets=d.target.nunique()))
    validations=sentinels(f,t)
    write('future-sentinels.csv',pd.DataFrame(validations))
    receipts=dict(frozen_scope=[FIRST,FREEZE],cash_feature_rows=len(f),stock_feature_rows=len(s),gap_mark_rows=len(g),announcement_rows=len(a),
                 original_cohorts=EXPECTED,matched_volatility_target_rows=len(vol),residual_forecasts=laws,
                 sentinel_cases=len(validations),sentinel_laws=sum(k['laws'] for k in validations),
                 clock_checks=['5-minute publication guard for cash and traded proxies','Target source opens at or after each intraday decision',
                       'Earlier cash and option-surface sessions only','Maturity strictly before original issue day at both original clocks',
                       'Exact endpoint agreement with V14 on both original evaluation cohorts'],
                 caveats=['Cash OHLC and publication delays are official and conservative proxies. Historical per-feed delivery latency is unavailable.',
                          'Bernoulli law locations are exact in per-case forecast p. The 128 equal-mass atom representation approximates that p.',
                          'Archived V16 path systems retain their original cutoff and modeling assumptions.'])
    save('validation-receipt.json',receipts)
    print('Validated chronological feature and target clocks,',receipts['sentinel_laws'],'unchanged laws, and protected endpoint targets',flush=True)


if __name__=='__main__':
    run()
