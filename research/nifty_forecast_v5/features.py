"""Causal cross-market/participation features, with explicit availability tables."""
from datetime import datetime,time,timedelta
from zoneinfo import ZoneInfo
import shutil
from .common import *
from .data import load

MARKETS={'^DJI':('America/New_York',16,0),'^GSPC':('America/New_York',16,0),
 '^FTSE':('Europe/London',16,30),'^GDAXI':('Europe/Berlin',17,30),'^FCHI':('Europe/Paris',17,30),
 '^HSI':('Asia/Hong_Kong',16,10),'^N225':('Asia/Tokyo',15,30)}
def completion(day,key):
    symbol=key.split('|')[-1]
    if symbol in MARKETS:
        zone,h,m=MARKETS[symbol]
        return pd.Timestamp(datetime.combine(pd.Timestamp(day).date(),time(h,m),ZoneInfo(zone)))+pd.Timedelta(hours=2)
    # Unknown futures/CFD/FX daily conventions: conservative full extra UTC day.
    return pd.Timestamp(day,tz='UTC')+pd.Timedelta(days=2)

def align_global(series,key,origins,decisions):
    available=pd.DatetimeIndex([completion(day,key) for day in series.index]).tz_convert('UTC')
    result=[];chosen=[]
    for origin,decision in zip(origins,decisions):
        i=available.searchsorted(pd.Timestamp(decision).tz_convert('UTC'),side='right')-1
        if i<0 or (pd.Timestamp(decision).tz_convert('UTC')-available[i]).days>7:result.append(np.nan);chosen.append(None)
        else:result.append(series.iloc[i]);chosen.append({'source_day':series.index[i],'available_assumption':available[i].isoformat()})
    return pd.Series(result,index=origins),chosen

def build(data,extra=True):
    for f in data.values():scope(f.index)
    price=data['nifty_spot'];c=price.close.astype(float);days=list(c.index)
    from research.nifty_forecast.horizons import future_sessions
    calendar=read('horizon-calendar-v1.json',ROOT/'artifacts/nifty_forecast/2026-11-17')
    nextday=days[1:]+future_sessions(days[-1],calendar,1);decision=[pd.Timestamp(d+' 09:10',tz='Asia/Kolkata') for d in nextday]
    # Latest experimental issue cannot consume a foreign close that is still future now.
    decision[-1]=min(decision[-1],pd.Timestamp(now()))
    x=pd.DataFrame(index=c.index);ret=c.pct_change(fill_method=None);alignments=[]
    for h in [1,3,5,10,21,63]:x[f'p_ret{h}']=c.pct_change(h,fill_method=None)
    for h in [5,21,63]:x[f'p_rv{h}']=ret.rolling(h).std()
    x['p_trend']=c/c.ewm(span=21,adjust=False).mean()-1;x['p_range']=price.high/price.low-1
    x['p_acceleration']=x.p_ret5-x.p_ret21/4;x['p_vix']=data['india_vix'].close.reindex(c.index)
    domestic={k:f for k,f in data.items() if k not in ['nifty_spot','india_vix','niftybees'] and not k.startswith(('g_','s_'))}
    sector=[]
    for k,f in domestic.items():
        cc=f.close.reindex(c.index).astype(float)
        for h in [5,21]:x[f'i_{k}_rel{h}']=cc.pct_change(h,fill_method=None)-c.pct_change(h)
        sector.append(cc.pct_change(5,fill_method=None))
    sr=pd.concat(sector,axis=1);x['i_participation']=sr.gt(0).sum(axis=1)/sr.notna().sum(axis=1).replace(0,np.nan)
    x['i_dispersion']=sr.std(axis=1);x['i_acceleration']=x.i_participation.diff(5)
    x['i_concentration']=sr.abs().max(axis=1)/sr.abs().sum(axis=1).replace(0,np.nan)
    x['i_leadership_persistence']=sr.rank(axis=1).corrwith(sr.shift(5).rank(axis=1),axis=1)
    x['i_defensive_cyclical']=(x.i_nifty_fmcg_rel5+x.i_nifty_pharma_rel5-x.i_nifty_auto_rel5-x.i_nifty_metal_rel5)/2
    for k,f in data.items():
        if not k.startswith('g_'):continue
        for h in [1,3,5,21]:
            vals,chosen=align_global(f.close.pct_change(h,fill_method=None),f'GLOBAL|{k[2:]}'.replace('DOW_FUTURES','DOW FUTURES').replace('SGX_NIFTY','SGX NIFTY'),days,decision)
            x[f'g_{k[2:]}_ret{h}']=vals
            if h==1:
                for origin,dec,ch in zip(days,decision,chosen):
                    if ch:alignments.append({'origin':origin,'decision':dec.isoformat(),'series':k,**ch})
    # Fixed relationships, not combinatorial interaction mining.
    def col(name):return x[name] if name in x else pd.Series(np.nan,index=x.index)
    eq=[n for n in x if n.startswith('g_') and n.endswith('_ret5') and any(s in n for s in ['GSPC','DJI','FTSE','GDAXI','FCHI','HSI','N225','IXIX'])]
    x['x_global_mean']=x[eq].mean(axis=1);x['x_global_dispersion']=x[eq].std(axis=1)
    x['x_india_relative']=x.p_ret5-x.x_global_mean
    x['x_oil_fx']=col('g_BZUSD_ret5')*col('g_USDINR_ret5')
    x['x_global_breadth']=x.x_global_mean*(x.i_participation-.5)
    x['x_tech_it']=col('g_IXIX_ret5')-col('i_nifty_it_rel5')-x.p_ret5
    x['x_asia_europe']=x[[n for n in eq if 'HSI' in n or 'N225' in n]].mean(axis=1)-x[[n for n in eq if any(s in n for s in ['FTSE','GDAXI','FCHI'])]].mean(axis=1)
    x['x_equity_oil']=x.x_global_mean-col('g_BZUSD_ret5')
    x['x_india_global_corr21']=x.p_ret1.rolling(21).corr(col('g_GSPC_ret1'))
    x['x_corr_change']=x.x_india_global_corr21-x.x_india_global_corr21.shift(21)
    x['x_global_corr21']=col('g_GSPC_ret1').rolling(21).corr(col('g_FTSE_ret1'))
    x['x_global_vol']=x.x_global_mean.rolling(21).std()
    if extra:
        for name in ['DGS10','DGS2','DTWEXBGS','VIXCLS']:
            p=OUT/'extras'/f'{name}.csv'
            if not p.exists():continue
            f=pd.read_csv(p,index_col=0);s=f.value
            for transform,values in [('level',s),('change5',s.diff(5))]:
                a=[];available=pd.DatetimeIndex([pd.Timestamp(day,tz='America/New_York')+pd.offsets.BDay(2)+pd.Timedelta(hours=18) for day in s.index]).tz_convert('UTC')
                for dec in decision:
                    j=available.searchsorted(dec.tz_convert('UTC'),side='right')-1
                    a.append(values.iloc[j] if j>=0 and (dec.tz_convert('UTC')-available[j]).days<8 else np.nan)
                x[f'b_{name}_{transform}']=a
        if 'b_DGS10_level' in x and 'b_DGS2_level' in x:x['b_yield_spread']=x.b_DGS10_level-x.b_DGS2_level
        # Read isolated official archives; runtime output redirect only.
        import research.nifty_forecast_v3.data as d3
        prev=d3.OUT
        try:
            d3.OUT=OUT;staging=OUT/'sources/fo';staging.parent.mkdir(exist_ok=True)
            if not staging.exists():shutil.copytree(OUT/'fo',staging)
            fo=d3.fo_features(data)
        finally:d3.OUT=prev
        for name in fo.select_dtypes('number').columns:
            if name not in ['spot_official','fut_oi','fut_lot','fut_contract']:x['d_'+name]=fo[name].reindex(c.index).shift(1)
        if 'd_fut_oi_log_change' in x:
            x['d_price_oi']=x.p_ret5*x.d_fut_oi_log_change;x['d_concentration_risk']=(x.d_call_concentration+x.d_put_concentration)*x.p_rv21
            x['d_position_expiry']=x.d_oi_pcr/(1+x.d_option_dte);x['d_basis_z']=(x.d_fut_basis-x.d_fut_basis.rolling(63).mean())/x.d_fut_basis.rolling(63).std()
            x['d_oi_z']=(x.d_fut_oi_log_change-x.d_fut_oi_log_change.rolling(63).mean())/x.d_fut_oi_log_change.rolling(63).std()
    # Survivorship-exposed wider stock basket, explicitly isolated.
    stocks=pd.concat({k:f.close for k,f in data.items() if k.startswith('s_')},axis=1).reindex(c.index)
    rr=stocks.pct_change(fill_method=None);rr=rr.where(abs(rr)<=.35)
    for h in [5,21]:
        mom=stocks.pct_change(h,fill_method=None)
        x[f's_dispersion{h}']=mom.std(axis=1);x[f's_positive{h}']=mom.gt(0).sum(axis=1)/mom.notna().sum(axis=1).replace(0,np.nan)
    x['s_advance']=rr.gt(0).sum(axis=1)/rr.notna().sum(axis=1).replace(0,np.nan)
    x['s_newhigh']=stocks.gt(stocks.shift().rolling(63).max()).mean(axis=1);x['s_newlow']=stocks.lt(stocks.shift().rolling(63).min()).mean(axis=1)
    x['s_breadth_acceleration']=x.s_positive5.diff(5);x['s_equalweight_relative']=rr.mean(axis=1).rolling(21).sum()-x.p_ret21
    x['s_common_correlation']=rr.rolling(21).corr(rr.mean(axis=1)).mean(axis=1)
    for name in ['p_ret1','p_ret5','p_rv21','i_participation','x_global_mean','d_oi_pcr']:
        if name in x:
            for lag in [1,3,5]:x[f'l_{name}_{lag}']=x[name].shift(lag)
    x=x.replace([np.inf,-np.inf],np.nan);x=x[x.p_ret63.notna()&x.p_rv63.notna()]
    return x,price.loc[x.index],pd.DataFrame(alignments)

def run():
    data,inv=load();x,price,align=build(data);x.to_csv(OUT/'features.csv');price.to_csv(OUT/'price.csv');align.to_csv(OUT/'global-availability.csv',index=False)
    save('data-inventory.json',inv)
    from research.nifty_forecast_v3.features import labels_for
    for h in [1,3,5,21]:labels_for(price,h).to_csv(OUT/f'labels-{h}.csv')
    save('feature-definitions.json',[{'name':c,'family':c.split('_')[0],'missing_fraction':float(x[c].isna().mean()),'classification':'SURVIVORSHIP_RESEARCH_ONLY' if c.startswith('s_') else 'CAUSAL_WITH_PUBLICATION_VINTAGE_LIMITATIONS'} for c in x])
    save('dataset-manifest.json',{'created':now(),'rows':len(x),'features':len(x.columns),'first':x.index[0],'last':x.index[-1],'start':START,'end':END,'files':{p.name:sha(p) for p in [OUT/'features.csv',OUT/'price.csv',OUT/'labels-1.csv',OUT/'labels-3.csv',OUT/'labels-5.csv',OUT/'labels-21.csv']}})
    print('V5 features',x.shape,'price',price.index[-1],flush=True)
if __name__=='__main__':run()
