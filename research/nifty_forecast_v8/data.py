"""Causal market-state inputs and historical source reconciliation."""
import io
from concurrent.futures import ThreadPoolExecutor
import requests
from .common import *
from research.nifty_forecast_v5.data import load
from research.nifty_forecast_v7.features import structure, SECTORS
from research.nifty_forecast_v7.reproduce import references

END='2026-11-17'


def global_sources(index, raw_index):
    codes=['NASDAQCOM','DGS10','VIXCLS']
    def get(code):
        url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}&cosd=2025-01-01&coed={END}'
        log={'series':code,'url':url,'requested_at':now()}
        path=OUT/f'sources/{code}.csv'
        try:
            if path.exists():payload=path.read_bytes()
            else:
                r=requests.get(url,timeout=10);log['http']=r.status_code;r.raise_for_status();payload=r.content
                log['response_date']=r.headers.get('Date')
            frame=pd.read_csv(io.BytesIO(payload))
            y=pd.to_numeric(frame.set_index(frame.columns[0])[code],errors='coerce').dropna().sort_index().loc['2025-01-01':END]
            if len(y)<200:raise ValueError('Incomplete historical series')
            path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(payload)
            log.update(rows=len(y),sha256=sha(path),status='available',first=y.index[0],last=y.index[-1])
            return code,y,log
        except (requests.RequestException,ValueError,KeyError) as exc:
            log.update(status='failed',error=type(exc).__name__);return code,None,log
    with ThreadPoolExecutor(max_workers=3) as pool:received=list(pool.map(get,codes))
    dates=list(raw_index);next_session=dict(zip(dates,dates[1:]+['2026-11-18']))
    out=matrix('global-reference.csv').reindex(index)
    evidence=[]
    for code,y,log in received:
        if y is None:continue
        # Two full US business days plus a 23:00 New York cutoff protects the FRED receipt assumption.
        available=(pd.DatetimeIndex(y.index)+2*pd.offsets.BDay()+pd.Timedelta(hours=23)).tz_localize('America/New_York').tz_convert('UTC')
        values=(y.diff(5) if code!='NASDAQCOM' else y.pct_change(5,fill_method=None)).to_numpy()
        vals=[]
        for d in index:
            decision=pd.Timestamp(next_session[d]+' 09:10',tz='Asia/Kolkata').tz_convert('UTC')
            loc=available.searchsorted(decision,side='right')-1
            usable=loc>=0 and (decision-available[loc]).days<=7
            vals.append(values[loc] if usable else np.nan)
            if usable:evidence.append({'origin':d,'series':code,'source_day':y.index[loc],
                                       'assumed_available':available[loc].isoformat(),'decision':decision.isoformat()})
        out[code]=vals
    save('global-source-probes.json',[log for _,_,log in received]);write('new-global-availability.csv',pd.DataFrame(evidence))
    return out


def intraday(price):
    records=[];audit=[]
    for path in sorted((V7/'intraday-sources').glob('*.json')):
        records.extend(read(path.name,path.parent)['data']['candles'])
        audit.append({'archive':path.name,'sha256':sha(path)})
    f=pd.DataFrame(records,columns=['timestamp','open','high','low','close','volume','oi'])
    stamp=pd.to_datetime(f.timestamp,utc=True).dt.tz_convert('Asia/Kolkata')
    f['day']=stamp.dt.strftime('%Y-%m-%d');f['minute']=stamp.dt.hour*60+stamp.dt.minute
    expected=list(range(9*60+15,15*60+30,25));rows=[];rejected=[]
    for day,g in f.groupby('day'):
        if day not in price.index:continue
        g=g.sort_values('minute');a=g[['open','high','low','close']].to_numpy(float)
        if list(g.minute)!=expected or not np.isfinite(a).all() or (a<=0).any() or (a[:,1]<a.max(axis=1)).any() or (a[:,2]>a.min(axis=1)).any():
            rejected.append(day);continue
        path=np.log(np.r_[a[0,0],a[:,3]]);inc=np.diff(path)
        ref=price.loc[day,'close'];official_error=abs(a[-1,3]-ref)
        rows.append({'day':day,'opening50':path[2]-path[0],'closing50':path[-1]-path[-3],
                     'intraday_reversal':(path[-1]-path[2])*np.sign(path[2]-path[0]),'intraday_rv':np.linalg.norm(inc),
                     'downside_share':sum(inc[inc<0]**2)/max(sum(inc**2),1e-12),
                     'late_range_share':np.log(a[-3:,1]/a[-3:,2]).sum()/max(np.log(a[:,1]/a[:,2]).sum(),1e-12),
                     'close_diff_points':a[-1,3]-ref,'close_diff_bps':10000*official_error/ref})
    data=pd.DataFrame(rows).set_index('day').sort_index()
    save('intraday-reconciliation.json',{'received_bars':len(f),'source':'Upstox historical NSE_INDEX|Nifty 50, 25-minute bar start times',
         'full_regular_sessions':len(data),'excluded_sessions':rejected,'grid_ist':'09:15 to 15:30 (15 bars)',
         'daily_reference':'Frozen native daily NIFTY close from V6, not overwritten',
         'median_abs_close_difference':float(data.close_diff_points.abs().median()),'max_abs_close_difference':float(data.close_diff_points.abs().max()),
         'over_10bp':int((data.close_diff_bps>10).sum()),'archive_hashes':audit})
    return data


def etfs(raw,index):
    series={'niftybees':raw['niftybees']}
    for p in (V5/'liquidity').glob('*.csv'):series[p.stem]=pd.read_csv(p,index_col=0)
    rows=[]
    for name,f in series.items():
        vol=pd.to_numeric(f.volume).where(lambda a:a>0);close=pd.to_numeric(f.close);turn=close*vol
        ret=close.pct_change(fill_method=None)
        own=raw['nifty_spot'].close.pct_change(5) if name.lower()=='niftybees' else None
        f=pd.DataFrame({'turn':np.log(turn/turn.shift().rolling(21,min_periods=15).median()),
                        'activity':np.log(vol/vol.shift().rolling(21,min_periods=15).median()),
                        'impact':abs(ret)/(turn/1e8),'rv':ret.rolling(5).std()}).reindex(index)
        if own is not None:f['tracked_spread']=close.pct_change(5).reindex(index)-own.reindex(index)
        rows.append(f)
    out=pd.concat(rows,keys=series,axis=1).T.groupby(level=1).mean().T.add_prefix('e_')
    out['e_shock']=out.e_activity.diff(5);out['e_activity_participation']=pd.concat([r.activity for r in rows],axis=1).gt(0).mean(axis=1)
    return out


def build(skip_fetch=False):
    if not read('reproduction.json')['passed']:raise RuntimeError('Reproduce V7 first')
    raw,inventory=load();native,volume,defense=references();idx=native.index;price=matrix('price.csv');allidx=raw['nifty_spot'].index
    base=native.drop(columns=defense)
    st,daily,momentum,rv=structure(raw,allidx)
    c=raw['nifty_spot'].close;market=c.pct_change(5);mkt_daily=c.pct_change(fill_method=None)
    groups={
        'bank':['bank_nifty','nifty_financial'],
        'defense':['nifty_fmcg','nifty_pharma','nifty_auto','nifty_metal','nifty_energy']}
    s=pd.DataFrame({'r_bank':st.financial_spread,'r_def':st.defensive_dispersion},index=allidx)
    x=pd.DataFrame(index=allidx)
    for k,series in s.items():
        x[k]=series;x[k+'_change']=series.diff(5);x[k+'_lag1']=series.diff(5).shift();x[k+'_lag5']=series.diff(5).shift(5)
        x[k+'_lag10']=series.diff(5).shift(10);x[k+'_average']=series.rolling(10).mean()
        x[k+'_norm']=series.diff(5)/series.shift().rolling(63,min_periods=30).std().clip(lower=.001)
        x[k+'_slope']=series.rolling(10).apply(lambda a:np.dot(a,np.arange(10)-4.5)/82.5,raw=True)
        x[k+'_accel']=series.diff(5).diff(5);x[k+'_switch']=np.sign(series)-np.sign(series.shift(5))
        x[k+'_extreme']=x[k+'_norm'].where(x[k+'_norm'].abs()>1.5,0).where(x[k+'_norm'].notna())
        beta=series.rolling(63,min_periods=35).cov(market)/market.rolling(63,min_periods=35).var().clip(lower=1e-8)
        x[k+'_residual']=(series-beta.shift()*market).diff(5)
    x['r_breadth_interaction']=x.r_def_change*(st.participation-.5)
    x['r_risk_interaction']=x.r_bank_change*mkt_daily.rolling(21).std()
    x['m_financial']=momentum[groups['bank']].mean(axis=1)-market
    x['m_cyclical']=momentum[groups['defense']].std(axis=1)
    x['m_participation']=st.participation-st.participation.rolling(21).mean()
    x['m_broad']=raw['idx_Nifty_500'].close.reindex(allidx).pct_change(5)-market
    x['m_vol_divergence']=rv.std(axis=1)/mkt_daily.rolling(5).std().clip(lower=.001)
    x['m_asymmetry']=daily.clip(upper=0).pow(2).rolling(21).mean().mean(axis=1)/daily.pow(2).rolling(21).mean().mean(axis=1)
    x['m_sync']=st.mean_corr;x['m_transition']=st.p_high_corr_next;x['m_concentration']=st.concentration
    x['m_rotation_speed']=momentum.rank(axis=1).diff(5).abs().mean(axis=1)
    x['m_leader_persistence']=st.leader_persistence
    x['m_implied_transition']=raw['india_vix'].close.reindex(allidx).pct_change(5)-mkt_daily.rolling(21).std().pct_change(5)
    panel=pd.DataFrame(index=allidx)
    beta=daily.rolling(63,min_periods=40).cov(mkt_daily).div(mkt_daily.rolling(63,min_periods=40).var().clip(lower=1e-8),axis=0)
    residual=daily-beta.shift().mul(mkt_daily,axis=0)
    panel['panel_common']=daily.mean(axis=1).rolling(5).sum();panel['panel_resid']=residual.mean(axis=1).rolling(5).sum()
    panel['panel_dispersion']=residual.rolling(5).sum().std(axis=1);panel['panel_volatility']=rv.mean(axis=1)
    market_panel=matrix('liquidity.csv',V7).filter(regex='^proxy_').reindex(idx)
    frames={'native':native,'base':base,'state':matrix('state-features.csv'),'volume':volume,'rotation':x.reindex(idx),
            'etf':etfs(raw,idx),'intraday':intraday(price),'panel':panel.reindex(idx),'stock_proxy':market_panel,
            'global':global_sources(idx,allidx) if not skip_fetch else matrix('global.csv',OUT),
            'positions':matrix('liquidity.csv',V7).filter(regex='^d_').reindex(idx)}
    for name,f in frames.items():f.replace([np.inf,-np.inf],np.nan).to_csv(OUT/f'{name}.csv')
    reference=matrix('market-structure.csv',V7)
    # Verify same rotation columns on all origins where the frozen V7 matrix has warmup.
    earlier=reference[['financial_spread','defensive_dispersion']].diff(5).dropna()
    np.testing.assert_allclose(x.loc[earlier.index,['r_bank_change','r_def_change']],earlier,atol=1e-12)
    save('data-manifest.json',{'input_boundary':['2025-01-01',END],'rows':len(idx),'columns':{n:list(f.columns) for n,f in frames.items()},
          'file_hashes':{n:sha(OUT/f'{n}.csv') for n in frames},'inventory':inventory,
          'native_source_revisions':read('actual-source-revision-audit.json',V6)})
    print('Frozen V8 inputs',len(idx),'daily rows,',len(frames['intraday']),'complete intraday dates',flush=True)


if __name__=='__main__':build()
