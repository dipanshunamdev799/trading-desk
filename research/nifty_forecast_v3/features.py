from __future__ import annotations
import json
import numpy as np
import pandas as pd
from .audit import OUT,OLD,save,sha
from .data import load_series,fo_features,START,END

def build(data,fo=None):
    for frame in data.values():
        if any(day<START or day>END for day in frame.index):raise ValueError('OUT_OF_SCOPE_MARKET_OBSERVATION')
    d=data['nifty_spot'];c=d.close.astype(float);r=c.pct_change();x=pd.DataFrame(index=d.index)
    rv=r.rolling(21).std().clip(lower=.001)
    for n in [1,5,10,21,63]:x[f'price_ret{n}']=c.pct_change(n)
    for n in [5,21,63]:x[f'price_rv{n}']=r.rolling(n).std()
    x['price_downvol21']=r.clip(upper=0).pow(2).rolling(21).mean().pow(.5)
    for n in [10,21,63]:x[f'price_ema{n}']=(c/c.ewm(span=n,adjust=False).mean()-1)/rv
    delta=c.diff();u=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean();v=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    x['price_rsi']=u/(u+v);x['price_acceleration']=c.pct_change(5)-c.pct_change(21)/4
    x['price_persistence']=r.gt(0).rolling(21).mean();x['price_rv_ratio']=x.price_rv5/rv
    tr=pd.concat([d.high-d.low,(d.high-c.shift()).abs(),(d.low-c.shift()).abs()],axis=1).max(axis=1)
    x['price_atr']=tr.rolling(14).mean()/c;x['price_body']=(d.close-d.open)/c
    x['price_range']=(d.high-d.low)/c;x['price_close_location']=(c-d.low)/(d.high-d.low).replace(0,np.nan)
    x['price_gap']=d.open/c.shift()-1
    vi=data['india_vix'].close.reindex(d.index).astype(float)
    x['risk_vix']=vi;x['risk_vix_change5']=vi.pct_change(5,fill_method=None)
    x['risk_vix_acceleration']=vi.pct_change(fill_method=None)-vi.pct_change(5,fill_method=None)/5
    x['risk_implied_realized_spread']=vi/100-rv*np.sqrt(252)
    sectors=[k for k in data if k.startswith('nifty_') and k not in ['nifty_spot','nifty_500']]+['bank_nifty']
    sector_returns=[]
    for key in sectors:
        sc=data[key].close.reindex(d.index).astype(float);rr=sc.pct_change(5,fill_method=None);sector_returns.append(rr)
        for n in [5,21]:x['sector_'+key+f'_rel{n}']=sc.pct_change(n,fill_method=None)-c.pct_change(n)
    sr=pd.concat(sector_returns,axis=1)
    x['sector_participation']=sr.gt(0).sum(axis=1)/sr.notna().sum(axis=1).replace(0,np.nan)
    x['sector_dispersion']=sr.std(axis=1);x['sector_breadth_change5']=x.sector_participation.diff(5)
    x['sector_divergence']=sr.mean(axis=1)-c.pct_change(5)
    x['sector_concentration']=sr.abs().max(axis=1)/sr.abs().sum(axis=1).replace(0,np.nan)
    x['sector_nifty500_relative']=data['nifty_500'].close.reindex(d.index).pct_change(21,fill_method=None)-c.pct_change(21)
    # Conservative 00:30 clock: latest source date strictly before origin day.
    for name,g in data.items():
        if not name.startswith('global_'):continue
        vals=pd.DataFrame({'ret1':g.close.pct_change(),'ret5':g.close.pct_change(5),'rv21':g.close.pct_change().rolling(21).std()},index=g.index)
        source_days=np.array(vals.index)
        for i,day in enumerate(d.index):
            j=np.searchsorted(source_days,day,side='left')-1
            if j>=0 and (pd.Timestamp(day)-pd.Timestamp(source_days[j])).days<=7:
                for col in vals:x.loc[day,name+'_'+col]=vals.iloc[j][col]
    etf=data['niftybees'].reindex(d.index)
    x['etf_relative_volume']=etf.volume/etf.volume.shift().rolling(21).median()
    x['etf_relative_turnover']=(etf.close*etf.volume)/(etf.close*etf.volume).shift().rolling(21).median()
    x['etf_tracking5']=etf.close.pct_change(5,fill_method=None)-c.pct_change(5)
    if fo is not None:
        numeric=fo.select_dtypes('number').drop(columns=['spot_official','fut_oi','fut_lot','fut_contract'],errors='ignore')
        lag=numeric.reindex(d.index).shift(1) # explicit additional publication lag
        x=pd.concat([x,lag.add_prefix('fo_')],axis=1)
    # Genuine institutional history; all dates are 2026, no earlier warmup.
    from research.nifty_forecast.adaptive import institutional_features
    inst,_=institutional_features(OLD/'institutional-v1',OLD/'inputs-v2',list(d.index))
    inst.index=d.index;x=pd.concat([x,inst.shift(1).add_prefix('institution_')],axis=1)
    p=OUT/'sources/nifty-intraday.csv'
    if p.exists():
        bars=pd.read_csv(p);bars['clock']=pd.to_datetime(bars.ts,utc=True).dt.tz_convert('Asia/Kolkata')
        bars['day']=bars.clock.dt.strftime('%Y-%m-%d');bars['minute']=bars.clock.dt.hour*60+bars.clock.dt.minute
        values=bars[['open','high','low','close']]
        valid=np.isfinite(values).all(axis=1)&(values>0).all(axis=1)
        valid &= bars.high.ge(values.max(axis=1))&bars.low.le(values.min(axis=1))
        invalid_days=set(bars.loc[~valid,'day']);bars=bars[~bars.day.isin(invalid_days)]
        bars=bars[(bars.minute>=555)&(bars.minute<=925)].drop_duplicates('ts').sort_values('ts')
        summaries=[]
        for day,b in bars.groupby('day'):
            if len(b)<70 or b.minute.min()!=555 or b.minute.max()<920:continue
            cr=b.close.pct_change().dropna();first=float(b.open.iloc[0]);last=float(b.close.iloc[-1])
            summaries.append({'day':day,'intraday_first_hour':float(b.close.iloc[min(11,len(b)-1)])/first-1,
                'intraday_last_hour':last/float(b.open.iloc[-12])-1,'intraday_rv':float(np.sqrt(np.sum(cr**2))),
                'intraday_efficiency':abs(last-first)/max(1e-9,float(b.close.diff().abs().sum())),
                'intraday_range':float(b.high.max()/b.low.min()-1)})
        intraday=pd.DataFrame(summaries).set_index('day').reindex(d.index)
        x=pd.concat([x,intraday],axis=1)
    # Current-membership proxy is separately tagged and ineligible for selectors.
    stocks=pd.concat({k:data[k].close for k in data if k.startswith('stock_')},axis=1).reindex(d.index)
    stock_ret=stocks.pct_change(fill_method=None);stock_ret=stock_ret.where(stock_ret.abs()<=.35)
    for n in [5,21,63]:
        momentum=stocks.pct_change(n,fill_method=None)
        x[f'proxy_above_ema{n}']=stocks.gt(stocks.ewm(span=n,adjust=False).mean()).mean(axis=1)
        x[f'proxy_momentum_dispersion{n}']=momentum.std(axis=1)
    x['proxy_advance_fraction']=stock_ret.gt(0).sum(axis=1)/stock_ret.notna().sum(axis=1).replace(0,np.nan)
    x['proxy_dispersion']=stock_ret.std(axis=1)
    x['proxy_equalweight_relative']=stock_ret.mean(axis=1).rolling(21).sum()-c.pct_change(21)
    x['proxy_new_high_fraction']=stocks.ge(stocks.shift().rolling(63).max()).mean(axis=1)
    x['proxy_new_low_fraction']=stocks.le(stocks.shift().rolling(63).min()).mean(axis=1)
    x['proxy_correlation']=stock_ret.rolling(21).corr(stock_ret.mean(axis=1)).mean(axis=1)
    x=x.copy()
    x['interaction_mom_risk']=x.price_ret21*x.price_rv21
    x['interaction_breadth_return']=x.sector_participation*x.price_ret5
    x['interaction_dispersion_risk']=x.sector_dispersion*x.price_rv21
    x['interaction_fii_trend']=x.institution_fii_futures_position_imbalance*x.price_ret21
    for col in ['price_ret1','price_ret5','price_rv21','sector_participation']:
        for lag in [1,3,5]:x[f'sequence_{col}_lag{lag}']=x[col].shift(lag)
    x['calendar_weekday']=pd.to_datetime(x.index).day_of_week.astype(float)
    valid=x.price_ret63.notna()&x.price_rv63.notna()
    return x.loc[valid].replace([np.inf,-np.inf],np.nan),d.loc[valid]

def labels_for(price,h):
    c=price.close.to_numpy(float);n=len(c);rows=[]
    for i,day in enumerate(price.index):
        if i+h<n:
            path=c[i:i+h+1];lr=np.diff(np.log(path));ret=path[-1]/path[0]-1
            rows.append({'origin':day,'endpoint':price.index[i+h],'return':ret,'direction':float(ret>0),
                'volatility':float(np.sqrt(np.mean(lr**2)*252)),
                'path_loss':float(path[1:].min()/path[0]-1),'absolute_return':abs(ret)})
        else:rows.append({'origin':day,'endpoint':None,'return':np.nan,'direction':np.nan,'volatility':np.nan,'path_loss':np.nan,'absolute_return':np.nan})
    return pd.DataFrame(rows,index=price.index)

def prepare():
    data,quality=load_series();fo=fo_features(data)
    # Official archive underlying should corroborate current close, not rewrite it.
    aligned=data['nifty_spot'].close.reindex(fo.index);diff=(aligned-fo.spot_official).abs()
    save('official-underlying-crosscheck.json',{'matched':int(diff.notna().sum()),'max_abs_points':float(diff.max()),'over_one_point':int(diff.gt(1).sum())})
    x,price=build(data,fo);x.to_csv(OUT/'features.csv');price.to_csv(OUT/'price.csv')
    definitions=[{'feature':col,'family':col.split('_')[0],
        'classification':'research-only current-basket proxy' if col.startswith('proxy_') else 'usable with explicit limitations',
        'availability':'extra one domestic session lag' if col.startswith(('fo_','institution_')) else 'strict preceding source calendar date' if col.startswith('global_') else 'previous completed Indian session',
        'finite':int(x[col].notna().sum()),'missing_fraction':float(x[col].isna().mean())} for col in x]
    save('feature-definitions.json',definitions)
    for h in [5,21]:labels_for(price,h).to_csv(OUT/f'labels-{h}.csv')
    save('dataset-manifest.json',{'start':START,'last_completed_session':END,'raw_sessions':len(data['nifty_spot']),
        'eligible_feature_rows':len(x),'feature_count':len(x.columns),'first_origin':x.index[0],'last_origin':x.index[-1],
        'files':{p.name:sha(p) for p in [OUT/'features.csv',OUT/'price.csv',OUT/'labels-5.csv',OUT/'labels-21.csv']},
        'source_manifests':{p.name:sha(p) for p in [OUT/'upstox-acquisition.json',OUT/'fo-acquisition.json']},
        'exposure':'All historical origins are research-exposed; no independent confirmation set'})
    print(json.dumps({'rows':len(x),'features':len(x.columns),'first':x.index[0],'last':x.index[-1]}),flush=True)
if __name__=='__main__':prepare()
