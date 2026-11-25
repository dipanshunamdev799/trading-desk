"""Financial dynamics, lagged innovations and date-level market representations."""
from .common import *
from research.nifty_forecast_v5.data import load
from research.nifty_forecast_v8.experiments import frames as parent_frames
from research.nifty_forecast_v7.features import SECTORS


def residual(series,market,window):
    beta=series.rolling(window,min_periods=max(20,window//2)).cov(market)/market.rolling(window,min_periods=max(20,window//2)).var().clip(lower=1e-8)
    return series-beta.shift()*market


def expected_ar(value):
    lag=value.shift();model_mean=value.shift().rolling(42,min_periods=25).mean()
    lag_mean=lag.shift().rolling(42,min_periods=25).mean()
    beta=(value.rolling(42,min_periods=25).cov(lag)/lag.rolling(42,min_periods=25).var().clip(lower=1e-10)).shift().clip(-.9,.9)
    return model_mean+beta*(lag-lag_mean)


def robust_surprise(value):
    hist=value.shift().rolling(42,min_periods=25)
    return ((value-hist.median())/((hist.quantile(.75)-hist.quantile(.25))/1.35).clip(lower=1e-5)).clip(-8,8)


def quantities(raw,acquired):
    spot=raw['nifty_spot'].copy();index=spot.index
    close=spot.close;md=close.pct_change(fill_method=None);market=close.pct_change(5)
    names=['bank_nifty','nifty_financial','nifty_psu_bank','idx_Nifty_500',*SECTORS]
    closes=pd.DataFrame({n:raw[n].close.reindex(index) for n in dict.fromkeys(names)})
    a=acquired[acquired.instrument.isin(['private_bank','bankbees','financial_etf','psu_etf','insurance_sbi','insurance_hdfc','insurance_icici'])]
    for n,g in a.groupby('instrument'):closes[n]=g.set_index('day').close.reindex(index)
    r=closes.pct_change(5,fill_method=None);daily=closes.pct_change(fill_method=None)
    bank=r.bank_nifty-r.nifty_financial
    private=r.get('private_bank',pd.Series(np.nan,index=index));insurance=r.filter(regex='^insurance_').mean(axis=1)
    f=pd.DataFrame({'f_spread':bank,'f_change':bank.diff(5),'f_accel':bank.diff(5).diff(5),
         'f_persist':bank.rolling(21).mean(),'f_psu_private':r.nifty_psu_bank-private,
         'f_bank_broad':r.bank_nifty-r.idx_Nifty_500,'f_insurance_bank':insurance-r.bank_nifty,
         'f_vol_adjusted':(bank.diff(5)/bank.shift().rolling(42,min_periods=25).std().clip(lower=.001)),
         'f_corr_change':daily.bank_nifty.rolling(21).corr(daily.nifty_financial).diff(5),
         'f_rank_shift':r[['bank_nifty','nifty_financial','nifty_psu_bank','private_bank']].rank(axis=1).bank_nifty.diff(5),
         'f_dispersion':r[['bank_nifty','nifty_financial','nifty_psu_bank','private_bank']].std(axis=1),
         'f_etf_tracking':r.get('bankbees',pd.Series(np.nan,index=index))-r.bank_nifty,
         'f_fin_etf_tracking':r.get('financial_etf',pd.Series(np.nan,index=index))-r.nifty_financial},index=index)
    for h in [42,63,84]:f[f'f_resid{h}']=residual(bank,market,h).diff(5)
    f['f_bank_innovation']=residual(daily.bank_nifty,md,63)
    f['f_bank_surprise']=f.f_bank_innovation-expected_ar(f.f_bank_innovation)
    sectors=daily[SECTORS]
    betas=sectors.rolling(63,min_periods=40).cov(md).div(md.rolling(63,min_periods=40).var().clip(lower=1e-8),axis=0).shift()
    orth=sectors-betas.mul(md,axis=0);mom=orth.rolling(5).sum()
    panel=pd.DataFrame({'c_residual_mean':mom.mean(axis=1),'c_residual_dispersion':mom.std(axis=1),
                       'c_residual_breadth':mom.gt(0).sum(axis=1)/mom.notna().sum(axis=1).replace(0,np.nan),
                       'c_residual_rotation':mom.rank(axis=1).diff(5).abs().mean(axis=1),
                       'c_common_risk':sectors.mean(axis=1).rolling(21).std(),
                       'c_panel_delta':mom.mean(axis=1).diff(5)})
    stock=pd.DataFrame({n:v.close.reindex(index) for n,v in raw.items() if n.startswith('s_')})
    daily_stock=stock.pct_change(fill_method=None);rs=daily_stock.where(daily_stock.abs()<.35)
    var=md.rolling(63,min_periods=40).var().clip(lower=1e-8)
    stock_res=rs-rs.rolling(63,min_periods=40).cov(md).div(var,axis=0).shift().mul(md,axis=0)
    proxy=pd.DataFrame({'stock_resid_dispersion':stock_res.std(axis=1),'stock_resid_breadth':stock_res.gt(0).sum(axis=1)/stock_res.notna().sum(axis=1).replace(0,np.nan),
                        'stock_common':rs.mean(axis=1).rolling(5).sum(),'stock_count':rs.notna().sum(axis=1)})
    return f,panel,proxy


def build():
    raw,_=load();new=pd.read_csv(OUT/'acquired-candles.csv');old_frames,_=parent_frames();idx=old_frames['base'].index
    f,sector,proxy=quantities(raw,new);r=matrix('rotation.csv',V8);etf=matrix('etf.csv',V8);position=matrix('positions.csv',V8)
    global_=matrix('global.csv',V8);st=matrix('market-structure.csv',V7);native=old_frames['base'];price=matrix('price.csv')
    glob=pd.DataFrame({'q_global_equity':global_.x_global_mean,'q_global_rates':global_['DGS10'],
                       'q_global_fx':global_.g_USDINR_ret5,'q_global_oil':global_.g_BZUSD_ret5,
                       'q_global_vix':global_.VIXCLS,'q_global_tech':global_.NASDAQCOM},index=idx)
    glob['q_india_diverge']=residual(native.p_ret5,glob.q_global_equity,63)
    glob['q_corr_change']=native.p_ret5.rolling(42,min_periods=30).corr(glob.q_global_equity).diff(5)
    glob['q_global_shock']=robust_surprise(glob.q_global_equity)
    levels=pd.DataFrame({'z_bank':f.f_change.reindex(idx),'z_defense':r.r_def_change,'z_etf':etf.e_turn,
                          'z_vol':native.p_rv21,'z_basis':position.d_fut_basis,'z_breadth':st.participation,'z_global':glob.q_india_diverge})
    innovation=pd.DataFrame(index=idx)
    for c in levels:
        v=levels[c];innovation[c+'_level']=v;innovation[c+'_delta']=v.diff(5)
        innovation[c+'_ar']=v-expected_ar(v);innovation[c+'_robust']=robust_surprise(v)
    state=pd.DataFrame({'s_trend':native.p_ret21/(native.p_rv21.clip(lower=.001)*np.sqrt(21)),
                        's_vol':native.p_rv21,'s_vol_change':native.p_rv21.diff(5),'s_breadth':st.participation,
                        's_concentration':st.concentration,'s_sync':st.mean_corr,'s_sector_dispersion':native.i_dispersion,
                        's_rotation_persistence':f.f_persist.reindex(idx),'s_bank':f.f_spread.reindex(idx),
                        's_defensive':r.r_def,'s_liquidity':etf.e_turn,'s_global_vol':glob.q_global_vix,
                        's_cross_corr':glob.q_corr_change,'s_acf':price.close.pct_change().rolling(42).corr(price.close.pct_change().shift()),
                        's_trend_consistency':price.close.pct_change().gt(0).rolling(21).mean()})
    datasets={'financial':f.reindex(idx),'panel':sector.reindex(idx),'proxy':proxy.reindex(idx),
              'state-context':state,'innovation':innovation,'global-context':glob}
    for key,data in datasets.items():write(key+'.csv',data.replace([np.inf,-np.inf],np.nan),index=True)
    # Truncating future bars leaves past financial and cross-sectional transformations unchanged.
    cutoff='2026-03-31';truncated={n:x.loc[:cutoff] for n,x in raw.items()}
    before=quantities(truncated,new[new.day<=cutoff]);full=(f,sector,proxy)
    for a,b in zip(before,full):np.testing.assert_allclose(a,b.loc[a.index,a.columns],atol=1e-11,equal_nan=True)
    save('feature-manifest.json',{'hashes':{name:sha(OUT/f'{name}.csv') for name in datasets},
          'definitions':{k:list(v.columns) for k,v in datasets.items()},'past_feature_truncation_verified':True,
          'financial_observed':{k:int(v.notna().sum()) for k,v in f.reindex(idx).items()},'stock_proxy_count':int(proxy.stock_count.max())})
    print('Built financial, innovation, global and date-grouped panel representations',flush=True)


if __name__=='__main__':build()
