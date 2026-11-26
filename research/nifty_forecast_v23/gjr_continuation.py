"""Reproduce the archived V14 GJR cash state for the genuine forward risk panel."""
from .common import *
from .forward import STUDY_DAY,targets
from .laws import Law
from research.nifty_forecast_v14.volatility import filter_garch,forecast_variance,MINV,MAXV


def path_close_returns(state,h,n,seed):
    rng=np.random.default_rng(seed)
    nu=state['nu']
    innovations=rng.standard_t(nu,size=(n,h))*np.sqrt((nu-2)/nu)
    v=np.full(n,state['next_variance'])
    p=np.empty_like(innovations)
    for k in range(h):
        sample=np.sqrt(np.clip(v,MINV,MAXV))*innovations[:,k]
        p[:,k]=sample/100.
        v=state['omega']+(state['alpha']+state['gamma']*(sample<0))*sample**2+state['beta']*v
    return p


def recover(known):
    root=root_for(14)
    process=csv('daily-process-features.csv',root).rename(columns=lambda x:'day' if x.startswith('Unnamed') else x)
    if 'day' not in process:
        process=process.rename(columns={process.columns[0]:'day'})
    process=process.set_index('day').sort_index()
    fits=read('process-fits.json',root)
    archive=read('process-states.json',root)
    match=[x for x in fits if x['origin'].startswith('2026-11') and x['method']=='gjr_student']
    assert len(match)==1
    fit=match[0]
    state=fit['parameters'].copy()
    r=process.daily_log_return.loc[fit['fit_first']:FREEZE].fillna(0.)*100
    checks=[]
    for day,old in archive.items():
        if not day.startswith('2026-11') or fit['origin']>day:
            continue
        a=r.loc[:day].to_numpy()
        s=state|dict(next_variance=float(np.clip(filter_garch(a,np.zeros(len(a)),state,state['initial'])[-1],MINV,MAXV)))
        q=forecast_variance(s,np.zeros(21))
        checked=float(np.max(abs(q-np.asarray(old['gjr_student']['variance_curve']))))
        assert checked<1.e-11,(day,checked)
        checks.append(dict(day=day,next_variance=s['next_variance'],max_21_session_variance_diff=checked))
    assert checks and process.path_close.loc[FREEZE]>0
    d0=[d for d in sorted(known) if FREEZE<d<STUDY_DAY]
    price=np.array([process.path_close.loc[FREEZE],*[known[d]['ohlc']['close'] for d in d0]])
    actual=100*np.diff(np.log(price))
    v=np.r_[r,actual]
    s=state|dict(next_variance=float(np.clip(filter_garch(v,np.zeros(len(v)),state,state['initial'])[-1],MINV,MAXV)))
    curve=forecast_variance(s,np.zeros(21))
    note=dict(captured_at=now(),fit_start=fit['fit_first'],fit_end=fit['fit_last'],origin=d0[-1],mature_forward_cash_sessions=d0,
              original_process_hash=sha(root/'process-fits.json'),historical_case_reproductions=checks,preserved_parameters=state,
              log_variance_curve_percent_squared=curve.tolist(),updated_next_variance=s['next_variance'],
              ingredient='The V14 monthly cached fit is held fixed. Only published post-freeze cash returns update the exact GJR filtering state.')
    save('forward/v14-gjr-state-receipt.json',note)
    return s,curve,float(np.sqrt(252*np.square(v[-21:]/100).mean())),note


def forward_risk(known,cut):
    s,curve,prior,note=recover(known)
    h=21;n=16384;seed=SEED+661
    raw=path_close_returns(s,h,n,seed)
    rv=np.sqrt(252*np.square(raw).mean(axis=1))
    y=np.expm1(raw.sum(axis=1));w=np.ones(n)/n
    return dict(name='V14_GJR_state_continuation_risk_21',targets=targets(STUDY_DAY)[:h],returns=y,weights=w,
                close_log_returns=raw,realized_volatility=rv,source='forward/v14-gjr-state-receipt.json',
                source_sha256=sha(OUT/'forward/v14-gjr-state-receipt.json'),
                kind='prospective close-risk reference with the verified V14 GJR state and frozen Student-t simulation',
                annualized_rv=float(np.mean(rv)),volatility_analytical_rms=float(np.sqrt(np.mean(curve)*252)/100),
                p_expansion=float(np.mean(rv>1.25*prior)),p_contraction=float(np.mean(rv<.80*prior)),
                config=dict(seed=seed,draws=n,fit_start=note['fit_start'],fit_end=note['fit_end'],exact_cache=note['preserved_parameters'],
                            updated_through=note['origin'],decision_cutoff=cut.isoformat(),expansion_threshold=1.25*prior,
                            contraction_threshold=.80*prior))


def historical():
    root=root_for(14)
    states=read('process-states.json',root)
    rows=[]
    for h in HORIZONS:
        f=csv(f'targets-{h}.csv',root)
        origin='day' if 'day' in f else f.columns[0]
        for a in f[f.cohort.notna()].itertuples(index=False):
            day=getattr(a,origin)
            s=states[day]['gjr_student']
            draws=path_close_returns(s,h,4096,SEED+761*h+pd.Timestamp(day).toordinal())
            vr=np.sqrt(252*(draws**2).mean(axis=1))
            pred=Law.build(vr)
            t=a.trailing_at_origin
            y=a.volatility
            q=1.-pred.cdf(1.25*t)
            volume=pred.moments()[0]
            rat=(y/max(.001,volume))**2
            analyt=float(np.sqrt(np.mean(s['variance_curve'][:h])*252)/100)
            rows.append(dict(horizon=h,origin=day,target=a.endpoint,cohort=a.cohort,p_expand=q,actual_vol=y,actual_expand=bool(y>1.25*t),
                             analytic_rv=analyt,average_rv=volume,mae=abs(y-volume),analytic_mae=abs(y-analyt),
                             brier=(q-(y>1.25*t))**2,qlike=rat-np.log(rat)-1,vol_crps=pred.crps(y)))
    x=pd.DataFrame(rows)
    assert x.target.le(FREEZE).all()
    write('v14-gjr-conditional-volatility-replay.csv.gz',x)
    write('v14-gjr-conditional-volatility-scores.csv',x.groupby('horizon',as_index=False).agg(n=('origin','size'),mae=('mae','mean'),
         analytic_mae=('analytic_mae','mean'),brier=('brier','mean'),qlike=('qlike','mean'),volatility_crps=('vol_crps','mean')))


if __name__=='__main__':
    from .forward import ledger,OPEN
    historical()
    d=forward_risk(ledger(),stamp(STUDY_DAY,OPEN))
    save('forward/v14-gjr-preflight.json',dict(model=d['name'],verified_at=now(),analytic_rv=d['volatility_analytical_rms'],
                                    simulation_rv=d['annualized_rv'],positive_probability=float(np.mean(d['returns']>0)),issued=False))
    print('V14 cached GJR continuation and independent risk replay verified.',flush=True)
