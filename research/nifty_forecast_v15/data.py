"""Build fixed forecast windows, as-of event clocks and remaining-horizon market risk."""
from dataclasses import dataclass

from .common import *
from research.nifty_forecast_v12.alignment import calendar
from research.nifty_forecast_v14.volatility import PROC_SPEC, fit_garch, filter_garch, forecast_variance

PRICE=('cash5','cash21','daily_log_return','sign_streak','har5','har21','ewma_fast','past_largest_gap')
RISK=('atm','vix_level','iv_change','variance_gap','iv_term','overnight_share')
DOMESTIC=('breadth5','breadth21','finance','defensive','concentration','sector_dispersion','intra_sync','breadth_change','f_resid_change')
DERIVATIVES=('iv_skew','iv_curvature','term_curve','oi_hhi','pc_oi','oi_flow','atm_straddle','front_basis','curve_30d',
             'front_oi_change_over_volume','same_contract_cash_gap','front_volume_share')
GLOBAL=('vix_us','vix_move','vxn','nasdaq_shock','asia_shock','hk_shock','usd_inr5','fx_shock','oil_shock',
        'brent5','dgs10_change','gold_etf_risk','intl_dispersion','q_corr_change','us_breadth5')
LIQUIDITY=('e_activity','e_turn','e_activity_participation','e_impact','e_tracked_spread','intra_gap21','downshare_5',
           'closing_share_5','intra_sector_risk','profile_change')
FIELDS=tuple(dict.fromkeys(PRICE+RISK+DOMESTIC+DERIVATIVES+GLOBAL+LIQUIDITY))


@dataclass
class Daily:
    sessions: pd.Index
    prices: pd.DataFrame
    features: pd.DataFrame
    labels: dict
    positions: dict

    @classmethod
    def load(cls):
        p=matrix('price.csv',V6)[['open','high','low','close']]
        x=matrix('features-5.csv',V14).reindex(p.index)
        assert p.index.is_monotonic_increasing and p.index.is_unique and p.index.min()>=FIRST and p.index.max()==FREEZE
        assert (p.high>=p[['open','close']].max(axis=1)).all() and (p.low<=p[['open','close']].min(axis=1)).all()
        assert set(FIELDS).issubset(x.columns)
        y={h:matrix(f'targets-{h}.csv',V14) for h in HORIZONS}
        return cls(p.index,p,x,y,{d:i for i,d in enumerate(p.index)})


def term_position(dte,vol,variance,target):
    nearest=int(np.argmin(abs(dte-target)))
    hi=int(np.searchsorted(dte,target,side='left'))
    if hi<len(dte) and dte[hi]==target:
        return float(vol[hi]),'exact',hi,hi
    if 0<hi<len(dte) and variance[hi]>=variance[hi-1]:
        value=np.interp(target,dte[hi-1:hi+1],variance[hi-1:hi+1])
        return float(np.sqrt(365*value/max(1,target))),'interpolated variance',hi-1,hi
    return float(vol[nearest]),'nearest',nearest,nearest


def make_iv(daily):
    f=pd.read_csv(V12/'surface-quality.csv',low_memory=False)
    f=f[f.iv_status.eq('accepted')&f.method.eq('TRADE')]
    opt={d:g.sort_values('dte') for d,g in f.groupby('day')}
    cash=matrix('official-index-closes.csv',V11).index
    row=[]; forecast_clocks={}
    for day in daily.sessions:
        asof=calendar(day)
        forecast_clocks[day]=asof
        idx=cash.get_loc(day)
        source=cash[idx-1]
        assert source<day
        surface=opt.get(source)
        if surface is not None:
            # The source marks predate the latest cash close. Require expiry after that close.
            eligible=surface[surface.expiry.gt(day)]
        else:
            eligible=pd.DataFrame()
        for left in range(1,22):
            e=asof[left-1]
            dt=(pd.Timestamp(e)-pd.Timestamp(source)).days
            remaining_calendar=(pd.Timestamp(e)-pd.Timestamp(day)).days
            op=dict(asof=day,remaining=left,source_day=source,decision=asof[0]+'T09:10:00+05:30',
                    scheduled_remaining_endpoint=e,calendar_days=remaining_calendar,source_tenor_days=dt)
            if len(eligible):
                ts=eligible.dte.to_numpy()
                level=eligible.atm_iv.to_numpy()
                var=eligible.total_variance.to_numpy()
                iv,rule,i,j=term_position(ts,level,var,dt)
                observed_skew=eligible.skew_down_minus_up.iloc[i] if 'skew_down_minus_up' in eligible else eligible.down_iv.iloc[i]-eligible.up_iv.iloc[i]
                scale=np.sqrt(np.clip((remaining_calendar/365.)/(left/252.),.65,1.45))
                op.update(iv=iv,rule=rule,expiry_low=eligible.expiry.iloc[i],expiry_high=eligible.expiry.iloc[j],
                          iv_calendar_action=iv*scale,skew=observed_skew,curve=eligible.curvature.iloc[i])
            else:
                # An already recorded underlying IV is only admissible with its original earlier source clock.
                x=daily.features.loc[day]
                source=x.option_day if pd.notna(x.option_day) and x.option_day<day else None
                v= float(x.iv_nearest) if source and np.isfinite(x.iv_nearest) else float(x.har21)
                op.update(iv=v,rule='archived ATM fallback' if source else 'past realized fallback',source_day=source,
                          expiry_low=None,expiry_high=None,iv_calendar_action=v,skew=x.iv_skew,curve=x.iv_curvature)
            row.append(op)
    iv=pd.DataFrame(row)
    write('remaining-tenor-availability.csv',iv)
    return iv,forecast_clocks


def future_state(daily):
    raw=matrix('daily-process-features.csv',V14)
    previous=read('process-states.json',V14)
    r=np.log(daily.prices.close).diff()
    returns=raw.daily_log_return.copy()
    returns.loc[r.dropna().index]=r.dropna()
    returns=returns.dropna().mul(100)
    models={}; fitting={}
    for day in daily.sessions:
        if day in previous:
            m=previous[day]['gjr_student']
            models[day]={**m,'state_mode':'original archived V14 GJR filter'}
            continue
        hist=returns.loc[:day].tail(300).to_numpy()
        assert len(hist)>45
        month=day[:7]
        if month not in fitting:
            m=fit_garch(hist,np.zeros(len(hist)),PROC_SPEC['gjr_student'])
            fitting[month]=(day,m)
        date,fit=fitting[month]
        assert date<=day
        s=fit.copy()
        s['next_variance']=float(filter_garch(hist,np.zeros(len(hist)),s,s['initial'])[-1])
        s['variance_curve']=forecast_variance(s,np.zeros(21)).tolist()
        s.update(state_mode='walk-forward V15 continuation',refit_day=date)
        models[day]=s
    save('daily-gjr-states.json',models)


def windows(daily,forecast_clocks):
    windows=[]; realized=[]
    for h in HORIZONS:
        y=daily.labels[h]
        chosen=y[y.cohort.notna()]
        assert len(chosen)==EXPECTED[h]
        for origin,r in chosen.iterrows():
            index=daily.positions[origin]
            terminal=daily.sessions[index+h]
            assert terminal==r.endpoint<=FREEZE
            initial_plan=forecast_clocks[origin][h-1]
            window_data=dict(horizon=h,origin=origin,target=terminal,cohort=r.cohort,
                             initial_planned_endpoint=initial_plan,literal_calendar=int(initial_plan==terminal),
                             origin_reference=float(r.reference),target_close=float(daily.prices.at[terminal,'close']))
            realized.append(window_data)
            for progress,day in enumerate(daily.sessions[index:index+h]):
                cur=float(daily.prices.at[day,'close'])
                left=h-progress
                known=_values(daily.prices.iloc[index+1:index+progress+1])
                if progress==0:
                    fields=dict(known_high=np.nan,known_low=np.nan,range_floor=0.,realized_sum_sq=0.)
                else:
                    c=known[:,3]
                    s=np.diff(np.log(np.r_[r.reference,c]))
                    hi,lo=float(known[:,1].max()/r.reference-1),float(known[:,2].min()/r.reference-1)
                    fields=dict(known_high=hi,known_low=lo,range_floor=hi-lo,realized_sum_sq=float(s@s))
                planned=forecast_clocks[day][left-1]
                windows.append(dict(**window_data,asof=day,checkpoint=progress,remaining=left,
                                    decision=forecast_clocks[day][0]+'T09:10:00+05:30',
                                    asof_calendar_target=planned,plan_differs_from_initial=int(planned!=initial_plan),
                                    checkpoint_is_primary=int(progress in CHECKPOINTS[h]),
                                    current_reference=cur,realized_price_ratio=cur/r.reference,**fields))
    a=pd.DataFrame(windows)
    assert len(a)==sum(EXPECTED[h]*h for h in HORIZONS)
    assert a['asof'].lt(a.target).all() and not a.duplicated(['horizon','origin','checkpoint']).any()
    write('original-windows.csv',pd.DataFrame(realized))
    write('update-calendar.csv',a)
    print('Fixed',len(realized),'windows and',len(a),'update checkpoints',flush=True)


def _values(a):
    return a[['open','high','low','close']].to_numpy(float)


def market_availability(d):
    ext=pd.read_csv(V12/'external-publication-alignment.csv')
    assert ext.source_day.lt(ext.origin).all()
    assert pd.to_datetime(ext.assumed_available,utc=True,format='mixed').le(pd.to_datetime(ext.decision,utc=True,format='mixed')).all()
    global_r=pd.read_csv(V13/'foreign-risk-clock.csv')
    assert global_r.source_day.lt(global_r.origin).all()
    assert pd.to_datetime(global_r.available_assumption,utc=True,format='mixed').le(
      pd.to_datetime(global_r.decision,utc=True,format='mixed')).all()
    et=pd.read_csv(V14/'supplemental-clock.csv')
    assert (et.source<et.origin).all()
    opts=d.features.option_day.dropna()
    assert opts.lt(opts.index.to_series()).all()
    save('data-avail-receipt.json',dict(cash_days=len(d.sessions),first=d.sessions.min(),last=d.sessions.max(),
         domestic='completed cash session features of frozen V14. Official equal-weight breadth is daily.',
         options='EOD derivatives dated strictly before latest observed cash day. Daily quotes have no within-day receipt stamp.',
         futures='Frozen V14 same-contract filtered changes, already lagged and retaining roll flags.',
         international='Frozen earlier-date availability receipts with verified next-session decision timestamps.',
         foreign_receipts=len(ext)+len(global_r)+len(et),v14_data_sha256=sha(V14/'manifest.json')))


def run():
    register()
    daily=Daily.load()
    _,clocks=make_iv(daily)
    windows(daily,clocks)
    market_availability(daily)
    future_state(daily)


if __name__=='__main__':
    run()
