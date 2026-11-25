"""Historical data assembly, conditional targets, and intraday jump-sensitive measurements."""
from .common import *
from research.nifty_forecast_v13.data import OHLC, valid_ohlc, daily as frozen_daily
from research.nifty_forecast_v12.common import bundle_entries

# These families are shared by the supervised models and their independent nulls.
BASE = ('atm','trailing','vix_level','term_slope','cash5','cash21')
DOM = ('finance','breadth5','breadth21','sector_dispersion','concentration','defensive',
       'f_resid_change','breadth_change','sign_streak','trend5','trend_acceleration','sector_sync')
SURFACE = ('sskew_down30','sskew_up30','scurvature30','term_curve','term_slope','sstrip_var30',
           'sdensity_q1030','sdensity_q9030','simplied_skew_moment30','sdensity_five_pct_down30','sup5_proxy30',
           'sskew_down30_chg1','sskew_up30_chg5','satm_iv30_chg1','satm_iv30_chg5','term_slope_chg5',
           'oi_hhi','oi_near','pc_oi','oi_flow','vol_oi','atm_term_inv','atm1','vrp')
INTRA = ('session_vol_5','firsthour_share_5','midday_share_5','closing_share_5','downshare_5',
         'sign_consistency_5','intraday_reversal_5','signed_excursion_5','jump_share_5','jump_share_1',
         'overnight_share','intra_sector_risk','intra_sync','profile_change','rth_gap_ratio')
GLOBAL = ('vix_us','vix_move','vxn','vxn_move','us_shock','asia_shock','hk_shock','nasdaq_shock',
          'fx_shock','oil_shock','gold_etf_risk','dgs10_change','intl_dispersion','q_corr_change','weak_global')
MECHANICS = ('front_basis','curve_30d','front_oi_change_over_volume','roll_event','e_activity','e_turn',
             'etf_turnover_change','vix_change','iv_skew','iv_over_rv')


def market_history():
    p, official = frozen_daily()
    older = pd.DataFrame(read('nifty_spot.json',V5/'sources')['rows']).set_index('day')[OHLC].sort_index()
    older = older.loc[FIRST:p.index.min()].iloc[:-1]
    merged = pd.concat([older,p]).loc[FIRST:FREEZE].sort_index()
    assert merged.index.is_unique and merged.index.is_monotonic_increasing and valid_ohlc(merged).all()
    np.testing.assert_allclose(p.close,official.reindex(p.index),atol=.05,rtol=0)
    audit = (merged.close-official.reindex(merged.index)).rename('provider_minus_official').to_frame()
    audit['primary_path'] = audit.index.isin(p.index)
    write('official-close-reconciliation.csv',audit,index=True)
    return merged,p


def intraday_profiles(daily):
    rows, rejected = [],[]
    for interval in (1,5):
        for file in sorted((V13/'sources/upstox').glob(f'nifty-{interval}m-*.json')):
            candles = read(file.name,file.parent)['data']['candles']
            a=pd.DataFrame(candles,columns=['stamp',*OHLC,'volume','oi'])
            if a.empty:
                continue
            time=pd.to_datetime(a.stamp,utc=True).dt.tz_convert('Asia/Kolkata')
            a['day']=time.dt.strftime('%Y-%m-%d')
            a['minute']=time.dt.hour*60+time.dt.minute
            for day,frame in a.groupby('day'):
                if day not in daily.index:
                    continue
                g=frame.sort_values('minute')
                expected=np.arange(555,930,interval)
                if not np.array_equal(g.minute.to_numpy(),expected) or not valid_ohlc(g).all():
                    rejected.append(dict(day=day,interval=interval,bars=len(g),source=file.name,reason='incomplete regular grid or invalid OHLC'))
                    continue
                ar=g[OHLC].to_numpy()
                prev=np.log(daily.close.shift().at[day])
                r=np.diff(np.log(np.r_[ar[0,0],ar[:,3]]))
                gap=np.log(ar[0,0])-prev
                variance=float(r@r)
                bpv=float(np.pi/2 * len(r)/(len(r)-1) * np.sum(np.abs(r[1:])*np.abs(r[:-1])))
                power=float(np.sum(r**4))
                early=g.minute.to_numpy()<615
                late=g.minute.to_numpy()>=870
                mid=~(early|late)
                first=float(r[early].sum())
                final=float(r[late].sum())
                total=float(r.sum())
                out=dict(day=day,interval=interval,bars=len(r),raw_variance=variance,bipower=bpv,
                         positive_excess=max(variance-bpv,0.),jump_share=max(variance-bpv,0.)/max(variance,1e-10),
                         max_abs_intraday=float(np.max(abs(r))),var_concentration=float(power/max(variance**2,1e-15)),
                         firsthour_share=float(np.sum(r[early]**2)/max(variance,1e-10)),
                         midday_share=float(np.sum(r[mid]**2)/max(variance,1e-10)),
                         closing_share=float(np.sum(r[late]**2)/max(variance,1e-10)),
                         upshare=float(np.sum(r[r>0]**2)/max(variance,1e-10)),
                         downshare=float(np.sum(r[r<0]**2)/max(variance,1e-10)),
                         sign_consistency=float(np.mean(r[1:]*r[:-1]>0)),
                         intraday_reversal=-first*final,session_return=total,overnight_log=gap,
                         signed_excursion=float((ar[:,1].max()+ar[:,2].min())/ar[0,0]-2),
                         closing_difference=float(ar[-1,3]-daily.close.at[day]),
                         high_difference=float(ar[:,1].max()-daily.high.at[day]),
                         low_difference=float(ar[:,2].min()-daily.low.at[day]),source=file.name)
                rows.append(out)
    tab=pd.DataFrame(rows).sort_values(['day','interval'])
    assert not tab.duplicated(['day','interval']).any()
    assert tab.day.ge(FIRST).all() and tab.day.le(FREEZE).all()
    write('intraday-profile.csv',tab)
    write('intraday-rejections.csv',pd.DataFrame(rejected))
    join=pd.DataFrame(index=daily.index)
    for interval in (1,5):
        f=tab[tab.interval.eq(interval)].set_index('day')
        # Features use only complete grids. Estimate the positive excess within each full session.
        f['session_vol']=np.sqrt(252*f.raw_variance)
        fields=['session_vol','raw_variance','bipower','positive_excess','jump_share','max_abs_intraday',
                'firsthour_share','midday_share','closing_share','upshare','downshare','sign_consistency',
                'intraday_reversal','signed_excursion','var_concentration','overnight_log']
        join=join.join(f[fields].add_suffix(f'_{interval}'))
    gap=np.log(daily.open/daily.close.shift())
    rth=np.log(daily.close/daily.open)
    join['gap']=gap
    join['rth']=rth
    join['overnight_share']=gap.pow(2).rolling(10,min_periods=7).sum()/(gap.pow(2)+rth.pow(2)).rolling(10,min_periods=7).sum()
    join['profile_change']=join.closing_share_5-join.closing_share_5.rolling(21,min_periods=9).median()
    join['rth_gap_ratio']=np.log((1.e-8+rth.pow(2).rolling(10,min_periods=7).mean())/(1.e-8+gap.pow(2).rolling(10,min_periods=7).mean()))
    for k in (1,5):
        vals=join[f'jump_share_{k}']
        cutoff=vals.shift().rolling(126,min_periods=35).quantile(.9)
        join[f'jump_flag_{k}']=vals.gt(cutoff).where(vals.notna()&cutoff.notna())
        join[f'jump_share_{k}_shift21']=vals.shift(21)
    return tab,join


def supplemental(index):
    sources=read('supplemental-sources.json',V13)
    f=pd.DataFrame(index=index)
    clock=[]
    for item in sources:
        if item['name']=='gold_proxy':
            a=pd.DataFrame(read('gold_proxy.json',V13/'sources/upstox')['data']['candles'])
            stamp=pd.to_datetime(a[0],utc=True).dt.tz_convert('Asia/Kolkata').dt.strftime('%Y-%m-%d')
            g=pd.Series(a[4].astype(float).to_numpy(),index=stamp).sort_index()
            series=np.sqrt(252*np.log(g).diff().pow(2).rolling(15,min_periods=10).mean()).dropna()
            name='gold_etf_risk'
        elif item['name']=='nasdaq_implied' and 'path' in item:
            series=pd.to_numeric(matrix(Path(item['path']).name,V13/'sources').VXNCLS,errors='coerce').dropna()/100
            name='vxn'
        else:
            continue
        series=series.loc[FIRST:FREEZE]
        dates=series.index.to_numpy(str)
        inds=np.searchsorted(dates,index,side='left')-1
        src=pd.Series(np.where(inds>=0,dates[np.maximum(inds,0)],None),index=index)
        f[name]=src.map(series)
        valid=src.dropna()
        assert valid.lt(valid.index.to_series()).all()
        clock.extend(dict(origin=d,field=name,source=s,assumed_available=s+' 23:00 UTC') for d,s in valid.items())
    write('supplemental-clock.csv',pd.DataFrame(clock))
    return f


def streaks(close):
    signs=np.sign(np.diff(np.log(close),prepend=np.log(close[0])))
    s=np.zeros(len(signs))
    for i,z in enumerate(signs[1:],1):
        s[i]=s[i-1]+z if s[i-1]*z>0 else z
    return s


def daily_features(all_prices, intraday):
    p=all_prices
    close=np.log(p.close)
    d=pd.DataFrame(index=p.index)
    d['daily_log_return']=close.diff()
    for k in (3,5,10,21,42,63):
        d[f'rv{k}']=np.sqrt(252*d.daily_log_return.pow(2).rolling(k,min_periods=min(k,16)).mean())
    d['overnight_rv21']=np.sqrt(252*intraday.gap.pow(2).rolling(21,min_periods=15).mean())
    d['rth_rv21']=np.sqrt(252*intraday.rth.pow(2).rolling(21,min_periods=15).mean())
    d['rv_decomposition']=np.sqrt(d.overnight_rv21**2+d.rth_rv21**2)
    d['ewma_fast']=np.sqrt(252*d.daily_log_return.pow(2).ewm(alpha=.18,adjust=False,min_periods=16).mean())
    d['ewma_slow']=np.sqrt(252*d.daily_log_return.pow(2).ewm(alpha=.035,adjust=False,min_periods=25).mean())
    d['intra_gap21']=np.sqrt(252*(intraday.raw_variance_5+intraday.gap.pow(2)).rolling(21,min_periods=14).mean())
    d['trend5']=close.diff(5)
    d['trend_acceleration']=close.diff(5)-close.diff(5).shift(5)
    d['sign_streak']=streaks(p.close.to_numpy())
    d['past_largest_gap']=intraday.gap.abs().rolling(5,min_periods=4).max()
    return d.join(intraday)


def observed_targets(p,h):
    old=matrix(f'targets-{h}.csv',V13)
    with np.load(V13/f'observed-paths-{h}.npz',allow_pickle=False) as ar:
        paths=ar['paths']
        origins=ar['origins']
    assert np.array_equal(old.index,origins)
    metric=observed_metrics(paths)
    y=old.copy()
    for k,v in metric.items():
        if k in old:
            np.testing.assert_allclose(v,old[k],rtol=1e-11,atol=3e-13)
        else:
            y[k]=v
    np.testing.assert_array_equal(y.endpoint,p.index[h:])
    assert y.index.min()>=FIRST and y.endpoint.max()<=FREEZE
    return paths,y


def observed_metrics(paths):
    c=paths[:,:,3]
    pre=np.column_stack([np.ones(len(c)),c[:,:-1]])
    r=np.log(c/pre)
    h=r.shape[1]
    k=h//2
    g=np.log(paths[:,:,0]/pre)
    rth=np.log(c/paths[:,:,0])
    var=(r*r).mean(axis=1)
    end=c[:,-1]-1.
    agg=np.sum(r,axis=1)
    direction=np.sign(agg)
    share=np.max(abs(r),axis=1)/np.maximum(np.sum(abs(r),axis=1),1e-10)
    return dict(endpoint_return=end,abs_return=abs(end),volatility=np.sqrt(252*var),variance=252*var,
        high=paths[:,:,1].max(axis=1)-1.,low=paths[:,:,2].min(axis=1)-1.,
        range=paths[:,:,1].max(axis=1)-paths[:,:,2].min(axis=1),
        peak_shock_share=share,aligned_fraction=(r*direction[:,None]>0).mean(axis=1),
        biggest_signed_log=np.take_along_axis(r,np.argmax(abs(r),axis=1)[:,None],axis=1)[:,0],
        max_daily=np.max(abs(r),axis=1),max_gap=np.max(abs(g),axis=1),
        first_gap=g[:,0],net_overnight=g.sum(axis=1),net_intraday=rth.sum(axis=1),
        vol_first=np.sqrt(252*np.mean(r[:,:k]**2,axis=1)),vol_last=np.sqrt(252*np.mean(r[:,k:]**2,axis=1)),
        speed=np.sqrt(252*np.mean(r[:,k:]**2,axis=1))-np.sqrt(252*np.mean(r[:,:k]**2,axis=1)),
        acceleration=direction*(np.mean(r[:,k:],axis=1)-np.mean(r[:,:k],axis=1)))


def add_thresholds(h,y,x):
    train_only=[]
    for day, row in y.iterrows():
        sample=mature(y,day,210)
        if len(sample)<34:
            train_only.append(dict(origin=day,cutoff=day,train_n=len(sample)))
            continue
        m=y.iloc[sample]
        assert m.endpoint.max()<day
        train_only.append(dict(origin=day,cutoff=day,train_n=len(sample),last_mature=m.endpoint.max(),
            high_risk=m.volatility.quantile(.75),var90=m.variance.quantile(.90),up90=m.endpoint_return.quantile(.90),
            down10=m.endpoint_return.quantile(.10),range90=m.range.quantile(.90),high90=m.high.quantile(.90),
            low10=m.low.quantile(.10),gap90=m.max_gap.quantile(.90),accel90=m.acceleration.quantile(.90),
            speed90=m.speed.quantile(.90)))
    t=pd.DataFrame(train_only).set_index('origin').reindex(y.index)
    s=x.loc[y.index,'trailing']
    iv=x.loc[y.index,'atm']
    y['horizon_sd_at_origin']=iv*np.sqrt(h/252.)
    y['trailing_at_origin']=s
    y['vol_change']=y.volatility-s
    y['vol_acceleration']=y.speed-(s-s.shift(max(1,h//2)))
    valid=t.train_n.ge(34)&s.notna()&iv.notna()

    events={
      'upper_fixed': y.endpoint_return.ge(.03 if h==5 else .05),
      'lower_fixed': y.endpoint_return.le(-(.03 if h==5 else .05)),
      'range_fixed': y.range.ge(.055 if h==5 else .10),
      'upper_excursion_fixed':y.high.ge(.05),
      'lower_excursion_fixed':y.low.le(-.05),
      'upper_relative':y.endpoint_return.ge(t.up90),
      'lower_relative':y.endpoint_return.le(t.down10),
      'range_relative':y.range.ge(t.range90),
      'high_relative':y.high.ge(t.high90),
      'low_relative':y.low.le(t.low10),
      'upper_iv_scaled': y.endpoint_return.ge(1.5*y.horizon_sd_at_origin),
      'lower_iv_scaled': y.endpoint_return.le(-1.5*y.horizon_sd_at_origin),
      'range_iv_scaled': y.range.ge(2*y.horizon_sd_at_origin),
      'expand': y.volatility.ge(1.25*s),
      'contract': y.volatility.le(.8*s),
      'high_state':y.volatility.ge(t.high_risk),
      'enter_high':s.lt(t.high_risk)&y.volatility.ge(t.high_risk),
      'exit_high':s.ge(t.high_risk)&y.volatility.lt(t.high_risk),
      'persist_high': y.vol_first.ge(t.high_risk)&y.vol_last.ge(t.high_risk),
      'rapid_risk':y.speed.gt(t.speed90),
      'variance_extreme':y.variance.ge(t.var90),
      'persist_up': y.endpoint_return.ge(t.up90)&y.aligned_fraction.ge(.65)&y.peak_shock_share.le(.5),
      'persist_down':y.endpoint_return.le(t.down10)&y.aligned_fraction.ge(.65)&y.peak_shock_share.le(.5),
      'gap_fixed':y.max_gap.ge(.012),
      'gap_relative':y.max_gap.ge(t.gap90),
      'acceleration':y.acceleration.ge(t.accel90)}
    for k,a in events.items():
        y['event_'+k]=a.astype(float).where(valid)
    for k in ['enter_high','exit_high']:
        condition=s.lt(t.high_risk) if k=='enter_high' else s.ge(t.high_risk)
        y[f'event_{k}']=y[f'event_{k}'].where(condition)
    return t,y


def option_checks():
    m=pd.read_csv(V12/'horizon-alignment.csv',low_memory=False)
    native=m[m.version.eq('TRADE')]
    assert native.option_source_day.lt(native.origin).all() and native.source_lag_sessions.eq(1).all()
    tails={}
    for (h,variant,d,_),law in bundle_entries(V12/'laws/aligned-Q.npz'):
        if variant in {'TRADE','LAG5','LIQUID','TRUNCATED','SETTLEMENT'}:
            tails[int(h),variant,d]=(law.w[law.a>=.03].sum(),law.w[law.a<=-.03].sum(),law.w@law.a)
    return m,tails


def prepare():
    register()
    px,p=market_history()
    intraday,i=intraday_profiles(px)
    d=daily_features(px,i)
    extra=supplemental(p.index)
    # Process fitting can use early 2025 sessions, with a shorter market-priced eligibility history.
    write('daily-process-features.csv',d.join(p.close.rename('path_close')),index=True)
    align,q=option_checks()

    for h in HORIZONS:
        paths,y=observed_targets(p,h)
        x=matrix(f'features-{h}.csv',V13).reindex(p.index)
        x=x.join(d.drop(columns=d.columns.intersection(x.columns))).join(extra).copy()
        raw='iv_nearest' if h==5 else 'iv_bracket'
        x['atm']=x[raw]
        x['trailing']=d[f'rv{h}']
        x['vix_change']=x.vix_level.diff(5)/100
        x['atm1']=x.atm.diff()
        x['vrp']=x.atm.pow(2)-x.rv21.pow(2)
        x['atm_term_inv']=-x.term_slope
        x['f_resid_change']=x.finance.diff(5)
        x['breadth_change']=x.breadth5.diff(5)
        x['sector_sync']=x.intra_sync
        x['vix_move']=x.vix_us.diff(3)/100
        x['vxn_move']=x.vxn.diff(3)
        x['weak_global']=x.vix_move*(-x.breadth5).clip(lower=0)
        x['etf_turnover_change']=x.e_turn.diff(5)
        mx=align[align.horizon.eq(h)]
        variants=[]
        for variant in ['TRADE','LAG5','LIQUID','TRUNCATED','SETTLEMENT']:
            a=mx[mx.version.eq(variant)].set_index('origin').reindex(x.index)
            available=a.option_source_day.notna()
            assert a.loc[available,'option_source_day'].lt(a.index[available].to_series()).all()
            new=a[['iv_nearest','iv_term','iv_skew','iv_curvature','density_forward_skew','density_priced_down5']].add_prefix(variant.lower()+'_')
            v=np.asarray([q.get((h,variant,k),(np.nan,np.nan,np.nan)) for k in x.index])
            new[[variant.lower()+'_q_up3',variant.lower()+'_q_down3',variant.lower()+'_q_mean']]=v
            variants.append(new)
        x=pd.concat([x,*variants],axis=1)
        assert x.columns.is_unique
        t,y=add_thresholds(h,y,x)
        labels=y[y.cohort.notna()]
        assert len(labels)==(265 if h==5 else 217) and labels.filter(like='event_').notna().any(axis=1).all()
        write(f'features-{h}.csv',x.replace([np.inf,-np.inf],np.nan),index=True)
        write(f'targets-{h}.csv',y,index=True)
        write(f'thresholds-{h}.csv',t,index=True)
        np.savez_compressed(OUT/f'observed-{h}.npz',paths=paths,origins=y.index.to_numpy(str))
        print(f'{h} sessions: {len(labels)} inherited origins and {len(y)} matured-capable OHLC windows',flush=True)
    counts=intraday.groupby('interval').agg(sessions=('day','size'),median_excess_share=('jump_share','median'),
                 mean_overnight_log=('overnight_log','mean'),median_intraday_variance=('raw_variance','median')).reset_index()
    counts.to_csv(OUT/'intraday-summary.csv',index=False)
    save('data-receipt.json',dict(frozen=FREEZE,full_daily=len(px),frozen_paths_daily=len(p),intraday=len(intraday),
          earlier_global_rows=len(pd.read_csv(V13/'foreign-risk-clock.csv')),source_first=px.index.min(),
          sources={'v13_manifest':sha(V13/'manifest.json'),'v12_option_laws':sha(V12/'laws/aligned-Q.npz')},
          scope='Reused frozen V13 market data and complete authenticated intraday grids. Additional market periods are outside evaluation.'))


if __name__=='__main__':
    prepare()
