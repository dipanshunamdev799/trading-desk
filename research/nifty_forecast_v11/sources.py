"""Read published index vintages, rederive synchronized intraday states and refresh separately."""
from .common import *
from .replay import redirect,dated
from research.nifty_forecast_v10.features import cached

PUBLICATIONS={
    'nifty50equalweight':('2025-01-01','https://www.niftyindices.com/indices/equity/strategy-indices/nifty50-equal-weight'),
    'nifty500equalweight':('2025-01-01','https://www.niftyindices.com/Press_Release/ind_prs31052024.pdf'),
    'nifty100equalweight':('2025-01-01','https://www.niftyindices.com/indices/equity/strategy-indices/nifty100-equal-weight'),
    'niftytop15equalweight':('2025-01-01','https://www.niftyindices.com/Factsheet/Factsheet_NiftyTop15EqualWeight.pdf'),
    'niftytop10equalweight':('2025-07-01','https://www.niftyindices.com/Nifty_Passive_Insights/Nifty%20Passive%20Insights%20Quarterly%20Update%20-%20April%2025%20to%20June%2025.pdf'),
    'nifty500quality50':('2025-07-01','https://www.niftyindices.com/Nifty_Passive_Insights/Nifty%20Passive%20Insights%20Quarterly%20Update%20-%20April%2025%20to%20June%2025.pdf'),
    'nifty500lowvolatility50':('2025-07-01','https://www.niftyindices.com/Nifty_Passive_Insights/Nifty%20Passive%20Insights%20Quarterly%20Update%20-%20April%2025%20to%20June%2025.pdf'),
}
DOMESTIC=['nifty50','niftynext50','nifty100','nifty200','nifty500','niftymidcap150','niftysmallcap250',
          'niftybank','niftyfinancialservices','niftyauto','niftyit','niftyfmcg','niftypharma','niftymetal','niftyenergy']


def official():
    rows=[];hashes={};labels={}
    for p in sorted((V10/'sources/nse-daily').glob('*.csv')):
        hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        f=pd.read_csv(p,skipinitialspace=True)
        n=f['Index Name'].str.strip()
        k=n.str.lower().str.replace(r'[^a-z0-9]','',regex=True)
        labels.update(zip(k,n))
        if k.duplicated().any():raise ValueError(f'Duplicate index identifiers in {p.name}')
        f=f.assign(key=k).set_index('key')
        assert pd.to_datetime(f['Index Date'],dayfirst=True).dt.strftime('%Y-%m-%d').eq(p.stem).all()
        rows.append(pd.to_numeric(f['Closing Index Value'],errors='coerce').rename(p.stem))
    price=pd.DataFrame(rows).sort_index().where(lambda a:a>0)
    allowed=price.reindex(columns=DOMESTIC+list(PUBLICATIONS)).copy()
    for k,(first,_) in PUBLICATIONS.items():
        allowed.loc[allowed.index<first,k]=np.nan
    info=[]
    for k in price:
        q=price[k].dropna()
        if k in PUBLICATIONS:
            floor,link=PUBLICATIONS[k];status='launch or publication corroborated'
        elif k in DOMESTIC:
            floor='2025-01-01';link='https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf';status='long-running domestic reference'
        else:floor=None;link=None;status='inventory only; pre-launch status or distinct mechanism unverified'
        info.append({'key':k,'name':labels[k],'rows':len(q),'first':q.index.min(),'last':q.index.max(),
                     'admit_from':floor,'source':link,'status':status})
    d=pd.read_csv(V10/'native-equal-weight-closes.csv').set_index('day')
    for n,k in [('eq50','nifty50equalweight'),('eq500','nifty500equalweight'),('cap50','nifty50'),('cap500','nifty500')]:
        np.testing.assert_array_equal(d[n],price.loc[d.index,k])
    write('official-index-inventory.csv',pd.DataFrame(info))
    write('official-index-closes.csv',allowed,index=True)
    save('official-source-audit.json',{'archive_hashes':hashes,'archives':len(price),'distinct_indices':len(price.columns),
         'publication_floors':PUBLICATIONS,'clock':'Use previous observed NSE-session archive in the main new breadth tests. Same-close controls have a separate ID.',
         'limitation':'Dated archive retrieved in 2026. Launch corroboration rules out pre-launch use. Exact historic file receipt or later corrections are unavailable.',
         'sector_equal_weight_and_weights':'Authenticated daily historical constituent weights and same-universe sector equal-weight data were not available. Sector aggregates serve as proxies.',
         'global_breadth':'This audit covers the domestic close panel. See global-breadth-audit.json for the separate traded US ETF proxy study.'})
    return allowed


def intraday():
    panel={};hashes={}
    for p in sorted((V10/'sources/intraday').glob('*.json')):
        hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        name=p.name.split('-')[0]
        a=pd.DataFrame(read(p.name,p.parent)['data']['candles'],columns=['ts','open','high','low','close','volume','oi'])
        dt=pd.to_datetime(a.ts,utc=True).dt.tz_convert('Asia/Kolkata')
        a['day']=dt.dt.strftime('%Y-%m-%d');a['minute']=dt.dt.hour*60+dt.dt.minute
        for d,g in a.groupby('day'):
            g=g.sort_values('minute');prices=g[['open','high','low','close']].to_numpy(float)
            if list(g.minute)!=list(range(555,930,25)) or not np.isfinite(prices).all() or (prices<=0).any():continue
            if (prices[:,1]<prices.max(axis=1)).any() or (prices[:,2]>prices.min(axis=1)).any():continue
            panel.setdefault(d,{})[name]=np.diff(np.log(np.r_[prices[0,0],prices[:,3]]))
    trusted=set(pd.read_csv(V10/'sector-intraday.csv').day)
    rows=[]
    for d,g in sorted(panel.items()):
        if set(g)!=set(['bank','financial','it','auto']) or d not in trusted:continue
        z=np.column_stack([g[k] for k in ['bank','financial','it','auto']])
        open_=z[:2].sum(axis=0);middle=z[5:10].sum(axis=0);close=z[-2:].sum(axis=0)
        sign=(open_>0).astype(float)
        rows.append({'day':d,'v11_mid_participation':np.mean(middle>0),'v11_open_follow':np.mean((close>0)==sign),
                     'v11_mid_finance':float(middle[:2].mean()-middle[2:].mean()),
                     'v11_close_concentration':float(np.sum(close**4)/max(1e-15,np.sum(close**2)**2)),
                     'v11_close_pressure':float(close.mean()),'v11_mid_dispersion':float(middle.std())})
    b=pd.DataFrame(rows).set_index('day');assert set(b.index)==trusted
    write('intraday-new-states.csv',b,index=True)
    save('intraday-source-audit.json',{'validated_dates':len(b),'hashes':hashes,'timing':'All four 15-bar sector sessions complete before decision.'})
    return b


def features():
    x,_,s=cached();ix=x['ten'].index
    cash=official();intra=intraday()
    lp=np.log(cash);r=lp.diff();old=matrix('rotation.csv',V8)
    labels=['50','100','500'];sp=pd.DataFrame({k:lp[f'nifty{k}equalweight']-lp[f'nifty{k}'] for k in labels})
    delta=sp.diff(5);long=sp.diff(21)
    gain=pd.concat([delta.add_prefix('b5_'),long.add_prefix('b21_')],axis=1)
    control=pd.DataFrame({'size':lp.niftymidcap150.diff(21)-lp.nifty50.diff(21),
                          'small':lp.niftysmallcap250.diff(21)-lp.nifty500.diff(21),
                          'rel_risk':r.nifty500equalweight.rolling(21).std()-r.nifty500.rolling(21).std(),
                          'rel_level_risk':r.nifty50.rolling(21).std()})
    pieces={
      'BREADTH':gain[['b5_50','b5_500','b21_50','b21_500']],
      'EQUAL':lp[['nifty50equalweight','nifty500equalweight']].diff(5),
      'CAP':lp[['nifty50','nifty500']].diff(5).add_prefix('cap_'),
      'PAIR100':gain[['b5_100','b21_100']],
      'CONTROL':control,
      'CHANGE':pd.DataFrame({'b_accel':delta['500'].diff(5),'b_weak_market_up':delta['50'].clip(upper=0)*lp.nifty50.diff(5).clip(lower=0),
                             'b_divergence':delta['500']-delta['50'],'b_risk':r.nifty500equalweight.rolling(21).std()-r.nifty500.rolling(21).std()}),
      'PERSIST':pd.DataFrame({'b_persist50':long['50'].rolling(21).mean(),'b_persist500':long['500'].rolling(21).mean(),
                              'b_participation_persist':delta['500'].gt(0).astype(float).rolling(21).mean()}),
      'FACTOR':pd.DataFrame({'q_quality':lp.nifty500quality50.diff(21)-lp.nifty500.diff(21),
                             'q_lowvol':lp.nifty500lowvolatility50.diff(21)-lp.nifty500.diff(21)}),
    }
    sectors=DOMESTIC[-8:]
    sector_mom=lp[sectors].diff(5)
    power=sector_mom.abs();shares=power.div(power.sum(axis=1).replace(0,np.nan),axis=0)
    idx_rank=sector_mom.rank(axis=1,pct=True)
    conc=pd.DataFrame({'lead_narrow':lp.niftytop15equalweight.diff(5)-lp.nifty50equalweight.diff(5),
         'lead_large':lp.nifty50.diff(5)-lp.nifty500.diff(5),'lead_sector_concentration':(shares**2).sum(axis=1,min_count=1),
         'lead_rank_change':idx_rank.diff().abs().mean(axis=1),'lead_sector_dispersion':sector_mom.std(axis=1),
         'lead_finance_spread':lp.niftybank.diff(21)-lp.nifty50.diff(21)})
    pieces['CONC']=conc
    pieces['INTERACT']=pd.DataFrame({'b_fin_interact':delta['500']*(lp.niftybank.diff(5)-lp.nifty50.diff(5)),
        'b_risk_interact':delta['50']*r.nifty50.rolling(21).std(),'b_rebalance_month':pd.Series(cash.index.str[5:7].isin(['03','06','09','12']),index=cash.index).astype(float)})
    result={k:a.shift().reindex(ix) for k,a in pieces.items()}
    result['SAME_CLOSE']=pieces['BREADTH'].reindex(ix)
    result['LAG5']=pieces['BREADTH'].shift(6).reindex(ix)
    result['RESID']=result['BREADTH'].join(result['CONTROL'])
    result['INTRADAY']=intra.reindex(ix)
    result['GLOBAL']=matrix('global-context.csv',V9)[['q_india_diverge','q_global_shock','q_global_vix','q_corr_change']].reindex(ix)
    result['DERIV'],fields=dated();result['DERIV']=result['DERIV'][fields['DATED_FUTURES']+fields['DATED_STRADDLE']].reindex(ix)
    result['ETF']=matrix('etf.csv',V8).reindex(ix)
    states=s[['s_vol','s_liquidity','s_defensive','s_bank']].join(result['BREADTH'][['b5_500']]).join(result['CONC'][['lead_sector_concentration']]).join(result['GLOBAL'][['q_india_diverge']])
    result['STATE']=states
    result['STATE_CHANGE']=states.diff(5)
    result['STATE_PERSIST']=states.rolling(21,min_periods=15).mean()
    definitions={}
    for name,a in result.items():
        assert a.index.equals(ix)
        write(f'matrices/{name}.csv',a,index=True)
        definitions[name]={'columns':list(a),'hash':sha(OUT/f'matrices/{name}.csv'),'complete_rows':int(a.notna().all(axis=1).sum())}
    save('feature-definitions.json',definitions)
    print('Official archives',len(cash),'series admitted',len(cash.columns),'complete intraday',len(intra),flush=True)


def refresh():
    import requests
    from research.nifty_forecast_v9 import acquire
    redirect(acquire,'refresh')
    acquire.run()
    a=read('acquisition.json',OUT/'refresh')
    raw=pd.read_csv(OUT/'refresh/acquired-candles.csv')
    days=sorted(raw.loc[raw.instrument.eq('nifty_spot')&raw.day.gt('2026-11-17'),'day'].unique())
    prev=read('refresh/refresh-audit.json',V10)['post_frozen_dates']
    holiday='https://betanseapi.nseindia.com/resources/exchange-communication-holidays'
    save('refresh-summary.json',{'dates':days,'last_completed':days[-1],'additional_vs_V10':sorted(set(days)-set(prev)),
          'validated_rows':len(raw),'official':a['official_crosscheck'],'calendar':holiday})


if __name__=='__main__':
    import sys
    {'features':features,'refresh':refresh}[sys.argv[1]]()
