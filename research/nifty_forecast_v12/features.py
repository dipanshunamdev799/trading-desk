"""Causal cross-instrument measures with explicit roles and event provenance."""
from .alignment import FOMC,RBI,calendar
from .common import *
from research.nifty_forecast_v5.data import load

REBALANCE={
 '2025-03-28':('2025-02-21','https://www.niftyindices.com/Press_Release/ind_prs21022025.pdf','NIFTY50 and NIFTY50 Equal Weight'),
 '2025-09-30':('2025-08-22','https://niftyindices.com/Press_Release/ind_prs22082025.pdf','NIFTY50 and broad indices'),
 '2026-03-30':('2026-02-23','https://www.niftyindices.com/Press_Release/ind_prs23022026.pdf','broad-market review; no NIFTY50 replacements'),
}

OPTIONS=['iv_nearest','iv_bracket','iv7','iv30','iv_term','iv_target_total_sd','atm_straddle','straddle_horizon_scaled',
         'iv_skew','iv_curvature','parity_mad_fraction','option_forward_basis','future_parity_gap',
         'density_external_mass','density_forward_skew','density_priced_down5']
REAL=['lag_rv5','rv21','rv63','vix_level']
OPT_CORE=['iv_nearest','iv_over_rv','iv_term','iv_change','iv_skew']
FUT=['front_basis','curve_30d','same_contract_cash_gap','front_oi_change_over_volume','front_volume_share']
DOM=['breadth5','breadth21','finance','defensive','cash5','cash21','concentration','sector_dispersion']
XJOINT=['cash_vs_basis','fin_vs_skew','breadth_vs_iv','position_vs_breadth','mom_vs_ivchange','conc_vs_skew','etf_vs_iv','parity_disagreement']
INTRA=['intra_sector_risk','intra_late_risk_share','intra_sync','v11_mid_dispersion','v11_close_concentration']
ETF=['e_turn','e_activity','e_rv','e_shock']
GLOB=['nasdaq5','vix_us','dgs10_change','usd_inr5','brent5','us_breadth5','q_global_shock','q_corr_change']
SCHEDULE=['near_weekly_expiry','near_monthly_expiry','roll_observed','fomc_during_window','rbi_during_window',
          'index_review_during_window','fomc_recent','rbi_recent']
SHOCK=['prior_move','sector_shock','breadth_decay','iv_jump','global_jump']


def zscore(x):
    prior=x.shift()
    m=prior.rolling(63,min_periods=28).median()
    dev=prior.rolling(63,min_periods=28).std().clip(lower=1e-8)
    return ((x-m)/dev).clip(-4,4)


def allowed_series(series,available,base,n,kind):
    p=series.sort_index().dropna()
    delta=p.diff(5) if kind=='difference' else p if kind=='level' else np.log(p.where(p>0)).diff(5)
    table=available[available.series.eq(n)].set_index('origin')
    dates=table.source_day.reindex(base)
    field='assumed_available' if 'assumed_available' in table else 'available_assumption'
    available_at=table[field].reindex(base)
    decision=table.decision.reindex(base)
    av=pd.to_datetime(available_at,utc=True,errors='coerce',format='mixed')
    close=pd.to_datetime(decision,utc=True,errors='coerce',format='mixed')
    ok=dates.notna()&(dates<dates.index.to_series())&av.le(close)
    out=dates.where(ok).map(delta)
    return out,pd.DataFrame({'source_day':dates,'assumed_available':available_at,'decision':decision},index=base).loc[ok]


def international(idx):
    available=pd.read_csv(V8/'new-global-availability.csv')
    g=pd.DataFrame(index=idx);timing=[]
    for name,c,kind in [('NASDAQCOM','nasdaq5','log'),('VIXCLS','vix_us','level'),('DGS10','dgs10_change','difference')]:
        f=pd.read_csv(V8/f'sources/{name}.csv',index_col=0)
        g[c],d=allowed_series(pd.to_numeric(f[name],errors='coerce'),available,idx,name,kind)
        timing.extend(d.rename_axis('origin').reset_index().assign(input=c).to_dict('records'))
    universe,_=load()
    a=pd.read_csv(V5/'global-availability.csv')
    for n,c in [('g_USDINR','usd_inr5'),('g_BZUSD','brent5')]:
        g[c],d=allowed_series(universe[n].close,a,idx,n,'log')
        timing.extend(d.rename_axis('origin').reset_index().assign(input=c).to_dict('records'))
    # V11 Nasdaq and V9 regime measurements retain their recorded conservative clock.
    g=g.join(matrix('matrices/US_EQ.csv',V11)[['us_breadth5']]).join(matrix('matrices/GLOBAL.csv',V11)[['q_global_shock','q_corr_change']])
    write('external-publication-alignment.csv',pd.DataFrame(timing))
    return g


def daily():
    price=matrix('price.csv')
    official=matrix('official-index-closes.csv',V11)
    idx=price.index
    spot=official.nifty50
    log=np.log(spot)
    ret=log.diff()
    breadth=matrix('matrices/BREADTH.csv',V11)
    conc=matrix('matrices/CONC.csv',V11)
    state=matrix('selection-states.csv',V10)
    v10=matrix('matrices/ten.csv',V10)
    vix=matrix('matrices/native.csv',V10).p_vix
    rv=pd.DataFrame({
       'lag_rv5':ret.rolling(5,min_periods=4).std()*np.sqrt(252),
       'rv21':ret.rolling(21,min_periods=15).std()*np.sqrt(252),
       'rv63':ret.rolling(63,min_periods=40).std()*np.sqrt(252),
       'cash5':log.diff(5),'cash21':log.diff(21),'prior_move':ret.abs(),
    }).reindex(idx)
    rv['vix_level']=vix.reindex(idx)
    rv['breadth5']=breadth.b5_500
    rv['breadth21']=breadth.b21_500
    rv['finance']=v10.f_resid63
    rv['defensive']=v10.r_def_residual
    rv['concentration']=conc.lead_sector_concentration
    rv['sector_dispersion']=state.s_sector_dispersion
    intra=matrix('sector-intraday.csv',V10).join(matrix('matrices/INTRADAY.csv',V11)).reindex(idx)
    etf=matrix('matrices/ETF.csv',V11).reindex(idx)
    f=matrix('futures-observed.csv',OUT).reindex(official.index).shift().reindex(idx)
    return (price,rv.join(intra).join(etf).join(international(idx)).join(f),official.index)


def scheduled(origin,planned,listed):
    fed=[f'{y}-{d}' for y,days in FOMC.items() for d in days.split()]
    # FOMC release on the US session is assumed too late for that Indian origin.
    rbi=[d for issued,(days,_) in RBI.items() if issued<=origin for d in days.split()]
    rev=[d for d,(issued,_,_) in REBALANCE.items() if issued<=origin]
    week,mth=listed
    distance=lambda d:(pd.Timestamp(d)-pd.Timestamp(origin)).days
    return {
      'near_weekly_expiry':int(isinstance(week,str) and 0<=distance(week)<=2),
      'near_monthly_expiry':int(isinstance(mth,str) and 0<=distance(mth)<=3),
      'fomc_during_window':int(any(origin<=d<planned for d in fed)),
      'rbi_during_window':int(any(origin<d<=planned for d in rbi)),
      'index_review_during_window':int(any(origin<d<=planned for d in rev)),
      'fomc_recent':int(any(-3<=distance(d)<0 for d in fed)),
      'rbi_recent':int(any(-2<=distance(d)<=0 for d in rbi)),
    }


def make():
    price,base,official=daily();table=pd.read_csv(OUT/'horizon-alignment.csv')
    daily_expiries=pd.read_csv(OUT/'surface-quality.csv',usecols=['day','expiry','method'])
    chain=daily_expiries[daily_expiries.method.eq('TRADE')].groupby('day').expiry.apply(sorted).to_dict()
    created=[]
    for h in [5,21]:
        for version,rows in table[table.horizon.eq(h)].groupby('version'):
            r=rows.set_index('origin').reindex(base.index)
            x=base.join(r[OPTIONS])
            x['iv_over_rv']=np.log(r.iv_nearest/x.rv21.clip(lower=.02))
            # Differences can reflect an expiry change. Use roll metadata and explicit long-tenor controls.
            x['iv_change']=r.iv_nearest.diff(5)
            x['roll_observed']=x.roll_event
            x['sector_shock']=x.finance.abs()
            x['breadth_decay']=-x.breadth5
            x['iv_jump']=r.iv_nearest.diff().abs()
            x['global_jump']=x.q_global_shock.abs()
            z={c:zscore(x[c]) for c in ['cash5','front_basis','finance','iv_skew','breadth5','iv_over_rv',
                           'front_oi_change_over_volume','iv_change','concentration','e_turn']}
            x['cash_vs_basis']=z['cash5']-z['front_basis']
            x['fin_vs_skew']=z['finance']*z['iv_skew']
            x['breadth_vs_iv']=z['breadth5']*z['iv_over_rv']
            x['position_vs_breadth']=z['front_oi_change_over_volume']*z['breadth5']
            x['mom_vs_ivchange']=z['cash5']*z['iv_change']
            x['conc_vs_skew']=z['concentration']*z['iv_skew']
            x['etf_vs_iv']=z['e_turn']*z['iv_change']
            x['parity_disagreement']=x.future_parity_gap.abs()
            event=[]
            for day,s in r.iterrows():
                eligible=[e for e in chain.get(s.option_source_day,[]) if e>=day]
                week=eligible[0] if eligible else None
                event.append(scheduled(day,s.planned_endpoint,(week,x.front_expiry.at[day])))
            x=x.join(pd.DataFrame(event,index=r.index)).replace([np.inf,-np.inf],np.nan)
            x['surface_available']=r.status.eq('ok')
            x['density_available']=r.density_available.eq(True)
            for i in range(5):
                x[f'noise_{i}']=np.random.default_rng(SEED+210+i+h).normal(size=len(x))
            y=x.select_dtypes(include=[np.number,'bool'])
            path=f'features/{h}-{version}.csv'
            write(path,y,index=True)
            created.append({'horizon':h,'version':version,'path':path,'rows_available':int(x.surface_available.sum()),'hash':sha(OUT/path)})
    save('feature-receipts.json',{'files':created,'fomc_statement_dates':FOMC,'rbi_releases':RBI,'index_review_notices':REBALANCE,
           'event_semantics':'Listed expiry and announced policy/review dates are planned information; rolls and prior moves are already observed. Retrospective surprises and realized outcome tails are excluded as features.',
           'feature_families':{'option_core':OPT_CORE,'trailing_realized':REAL,'futures':FUT,'domestic':DOM,'cross_instrument':XJOINT,
                               'intraday':INTRA,'ETF':ETF,'global':GLOB,'schedule':SCHEDULE,'training_threshold_shocks':SHOCK}})
    print('Generated',len(created),'dated, horizon-specific matrices',flush=True)


if __name__=='__main__':make()
