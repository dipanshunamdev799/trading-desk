"""Compact market representations, authoritative breadth and matched source additions."""
from .common import *
from research.nifty_forecast_v9.run_models import inputs as v9_inputs
from research.nifty_forecast_v7.features import SECTORS
from research.nifty_forecast_v5.data import load


def make():
    p,_=v9_inputs()
    base=p['base'];state=matrix('state-context.csv',V9);idx=base.index;rot=matrix('rotation.csv',V8);fp=matrix('financial.csv',V9)
    v=matrix('etf.csv',V8);glob=matrix('global-context.csv',V9);position=matrix('positions.csv',V8)
    all5=base[['p_ret5','p_ret21','p_rv21','i_participation']].join(fp[['f_resid63']])
    all10=all5.join(rot[['r_def_residual','m_broad','m_sync','m_vol_divergence']]).join(v[['e_turn']])
    all20=all10.join(base[['p_vix','p_trend','i_dispersion','i_nifty_it_rel21','i_nifty_energy_rel5']]).join(rot[['m_financial','m_cyclical','m_asymmetry','m_rotation_speed','m_leader_persistence']])
    assert [f.shape[1] for f in [all5,all10,all20]]==[5,10,20]
    daily=matrix('sector-returns.csv',V7);spot=matrix('price.csv').close.pct_change(fill_method=None).reindex(daily.index)
    beta=daily.rolling(63,min_periods=35).cov(spot).div(spot.rolling(63,min_periods=35).var().clip(lower=1e-8),axis=0).shift()
    component=beta.mul(spot,axis=0);residual=daily-component
    label='bank_nifty'
    comp=pd.DataFrame({'common_momentum':component.mean(axis=1).rolling(5).sum(),'common_dispersion':component.std(axis=1).rolling(5).mean(),
                       'common_finance':component[label].rolling(5).sum(),'residual_momentum':residual.mean(axis=1).rolling(5).sum(),
                       'residual_dispersion':residual.rolling(5).sum().std(axis=1),'residual_finance':residual[label].rolling(5).sum()}).reindex(idx)
    state_cols=['s_trend','s_vol','s_breadth','s_liquidity','s_bank','s_defensive']
    dynamics=state[state_cols]
    prior=dynamics.shift()
    means=dynamics.shift().rolling(42,min_periods=25).mean();lagmeans=prior.shift().rolling(42,min_periods=25).mean()
    arp=(dynamics.rolling(42,min_periods=25).cov(prior)/prior.rolling(42,min_periods=25).var().clip(lower=1e-8)).shift().clip(-.9,.9)
    transition=means+arp*(prior-lagmeans)
    d=pd.read_csv(OUT/'native-equal-weight-closes.csv').set_index('day').sort_index()
    ew=pd.DataFrame({'eq50_relative5':d.eq50.pct_change(5)-d.cap50.pct_change(5),
                     'eq500_relative5':d.eq500.pct_change(5)-d.cap500.pct_change(5),
                     'eq50_relative21':d.eq50.pct_change(21)-d.cap50.pct_change(21),
                     'eq500_relative21':d.eq500.pct_change(21)-d.cap500.pct_change(21)}).reindex(idx)
    intr=pd.read_csv(OUT/'sector-intraday.csv').set_index('day').reindex(idx)
    vo=pd.read_csv(V9/'acquired-candles.csv');etf=vo[vo.instrument=='bankbees'].set_index('day')
    turnover=etf.close*etf.volume;activity=(turnover/turnover.shift().rolling(21,min_periods=15).median()).clip(.1,10).reindex(idx)
    # Rolling basis residual is a carry/roll proxy, with no inferred financing yield.
    mark=position.d_fut_basis;median=mark.shift().rolling(63,min_periods=30).median()
    deriv=position.assign(d_basis_residual=mark-median,d_basis_reset=mark.diff().abs(),d_open_interest_per_activity=position.d_fut_oi_log_change/activity)
    lag=rot[['r_bank_residual','r_def_residual']]
    q=lambda a,b:pd.concat([a,b.reindex(a.index)],axis=1)
    result={'five':all5,'ten':all10,'twenty':all20,'native':p['native'],'native_rot':p['cluster_rot'],'rotation':p['residual'],
            'breadth':q(all10,ew),'intraday':q(all10,intr),'derivatives':q(all10,deriv),
            'derivatives_raw':q(all10,position),'global':q(all10,glob[['q_india_diverge','q_global_shock','q_global_vix','q_corr_change']]),
            'common_factor':q(all10,comp.filter(regex='^common_')),'residual_factor':q(all10,comp.filter(regex='^residual_')),
            'state_level':q(all10,dynamics),'state_lag':q(all10,dynamics.shift(1).add_suffix('_lag')),
            'state_transition':q(all10,transition.add_suffix('_expected')),
            'persistent':q(all10,dynamics.rolling(21,min_periods=15).mean().add_suffix('_persistent')),
            'distributed':q(all10,pd.concat([lag.shift(k).add_suffix(f'_lag{k}') for k in [0,5,10,21]],axis=1)),
            'no_banks':all10.drop(columns=['f_resid63']),'source_lag':q(all10.drop(columns=['f_resid63','r_def_residual']),all10[['f_resid63','r_def_residual']].shift()),
            'shifted_state':all10.copy()}
    mask={'intraday_complete':intr.notna().all(axis=1),'breadth_complete':ew.notna().all(axis=1)}
    # Drop repeated exact feature names (the structured representations preserve distinct transformations).
    for n,a in result.items():result[n]=a.loc[:,~a.columns.duplicated()].replace([np.inf,-np.inf],np.nan)
    cap=matrix('price.csv').close.reindex(d.index);delta=(cap-d.cap50).abs().dropna()
    return result,mask,state,{'official_cap_overlap':len(delta),'official_cap_max_delta':float(delta.max()),
           'official_cap_abs_difference_gt_1':int((delta>1).sum()),'official_equal_weight_count':d.eq50.notna().sum()}


def run():
    frames,masks,state,audit=make()
    for name,x in frames.items():write(f'matrices/{name}.csv',x,index=True)
    write('matrix-eligibility.csv',pd.DataFrame(masks),index=True);write('selection-states.csv',state,index=True)
    save('feature-audit.json',{'checks':audit,'matrices':{k:{'cols':list(x),'rows':len(x),'sha256':sha(OUT/f'matrices/{k}.csv')} for k,x in frames.items()},
         'timing':'Domestic daily state from completed close. Intraday complete regular session only. Frozen foreign publication buffers. Inherited one-session derivative lag.'})
    print('Defined',len(frames),'dated matrices and matched parent controls',flush=True)


def cached():
    audit=read('feature-audit.json')
    return {k:matrix(f'matrices/{k}.csv',OUT) for k in audit['matrices']},matrix('matrix-eligibility.csv',OUT),matrix('selection-states.csv',OUT)


if __name__=='__main__':run()
