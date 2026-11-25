"""Build strictly timed cash, breadth, liquidity, surprise and relation panels."""
from .common import *
from research.nifty_forecast_v15.sessions import candles
from research.nifty_forecast_v16.replay import cohorts

PX=('known_move','known_rth','cash_last5','cash_last15','gap_seen')
RV=('prefix_rv','iv_prev','trailing_vol','prefix_range')
EW=('eq50_spread1','eq500_spread1','eq500_spread5','eq500_spread21','official_finance1')
NATIVE=('native_bank_rel','native_finance_rel','native_it_rel','native_energy_rel','native_auto_rel','native_defensive_rel',
        'native_sync','native_dispersion','native_bank_accel')
STOCK=('stock_above_open','stock_advance','stock_outperform','stock_median','stock_equal','stock_dispersion','stock_asymmetry',
       'stock_up_concentration','stock_down_concentration','stock_breadth_change','stock_acceleration','stock_sync')
STANDARD=('own_sector_above','own_sector_mean','own_sector_dispersion','own_sector_open','own_sector_last5','own_sector_sync')
FIN=('bank_above','finance_above','bank_rel','financial_lead','bank_sector_surprise','it_sector_surprise','heavy_vs_broad')
LIQ=('above_proxy_vwap','vwap_deviation','relative_volume','activity_dispersion','volume_concentration','relative_turnover',
     'negative_activity','return_per_volume','financial_volume','signed_activity_proxy','liquidity_acceleration')
SURPRISE=('open_surprise','open_surprise_z','abs_surprise_z','surprise_gift_remaining','surprise_x_breadth','surprise_x_finance')
CROSS=('nifty_etf_tracking','bank_etf_tracking','etf_tracking_vs_past','bank_tracking_vs_past','etf_volume','bank_etf_volume',
       'basis_previous','basis_previous_z','previous_same_contract','prior_future_curve','previous_parity_gap','cash_vs_gift_repricing')
OPTIONS=('iv_prev','iv_skew','iv_term','iv_curvature','vix_level','OI_pc_prior')
NEWS=('news_results','news_schedule','news_action','news_finance','news_broad')
GLOBAL=('forex_yesterday','us_yesterday','global_vix','us_breadth','fx_risk')
PRE_STOCK=('stock_above_open','stock_advance','stock_dispersion','stock_equal','relative_volume','above_proxy_vwap','bank_above','heavy_vs_broad')
ALTS=('subset1_above','subset1_dispersion','subset2_above','subset2_dispersion','without_heavy_above','without_heavy_dispersion',
      'action_clean_above','action_clean_dispersion')
SIZE=('expected_gap','pred_gap_std')

FAMILIES={
 'opening_surprise':SURPRISE,'official_equal_weight':EW,'native_sector':NATIVE,'stock_breadth':STOCK,
 'sector_adjusted_stock':STANDARD,'financial_participation':FIN,'volume_liquidity':LIQ,'cross_instrument':CROSS,
 'option_surface':OPTIONS[1:],'realized_volatility':RV,'international':GLOBAL,
 'announcements':NEWS,
}


def corr_score(a):
    a=np.asarray(a,dtype=float)
    good=a[np.isfinite(a)]
    return float(abs(np.mean(np.sign(good)))) if len(good) else np.nan

def value(a,stat='mean'):
    v=np.asarray(a,dtype=float)
    x=v[np.isfinite(v)]
    if not len(x):return np.nan
    if stat=='positive':return float((x>0).mean())
    if stat=='negative':return float((x<0).mean())
    return float(getattr(np,stat)(x))

def concentration(a,kind):
    a=np.asarray(a,dtype=float)
    a=a[np.isfinite(a)]
    x=np.maximum(a*kind,0)
    return float(x@x/(x.sum()**2)) if np.sum(x)>0 else np.nan


def cross_section(z,sets):
    nat=z[z.sector.eq('native')].set_index('stock')
    raw=z[~z.sector.isin(['native','ETF']) & z.interval_minutes.eq(5)]
    r=raw[raw.ret_open.notna()]
    et=z[z.sector.eq('ETF')].set_index('stock')
    d=dict(stock_n=len(r),stock_group_n=r.sector.nunique(),stock_valid_gaps=int(r.known_gap.notna().sum()),source_native_n=len(nat))
    for name in ('bank','finance','it','energy','auto','defensive','broad'):
        if name in nat.index:
            for key in ('ret_open','ret_day','known_gap','last5','last15','rv','range'):
                d[f'{name}_index_{key}']=float(nat.at[name,key])
            d[name+'_index_time']=nat.at[name,'cutoff_bar_end']
    for nm in ('bank','finance','it','auto','energy','defensive'):
        sub=r[r.sector.eq(nm)]
        d[nm+'_above']=value(sub.ret_open,'positive')
        d[nm+'_own_return']=value(sub.ret_open)
        d[nm+'_own_gap']=value(sub.known_gap)
        d[nm+'_own_range']=value(sub.range)
        d[nm+'_own_rv']=value(sub.rv)
        d[nm+'_own_last5']=value(sub.last5)
        d[nm+'_own_last15']=value(sub.last15)
        d[nm+'_own_relvol']=value(sub.relative_volume)
        d[nm+'_cross_dispersion']=value(sub.ret_open,'std')
    if len(r)<14:
        return d
    a=r.ret_day; b=r.ret_open
    # Five-minute shares are neutralized against synchronized sibling medians.
    # Separate native-sector controls use their own authenticated bar time.
    native_open=r.groupby('sector').ret_open.transform('median')
    native_gap=r.groupby('sector').known_gap.transform('median')
    native_fast=r.groupby('sector').last5.transform('median')
    n=b-native_open
    s=r.known_gap-native_gap
    t=r.last5-native_fast
    if r.ret_open.std()>0:
        skew=(r.ret_open-r.ret_open.mean()).pow(3).mean()/r.ret_open.std()**3
    else:skew=0.
    d.update(stock_above_open=value(b,'positive'),stock_advance=value(a,'positive'),stock_median=value(b,'median'),
      stock_equal=value(b),stock_dispersion=value(b,'std'),stock_asymmetry=skew,
      stock_up_concentration=concentration(b,1),stock_down_concentration=concentration(b,-1),stock_sync=corr_score(r.last5),
      own_sector_above=value(n,'positive'),own_sector_mean=value(n),own_sector_dispersion=value(n,'std'),
      own_sector_open=value(s),own_sector_last5=value(t),own_sector_sync=corr_score(t),
      stock_breadth_last5=value(r.last5,'positive'),stock_breadth_last15=value(r.last15,'positive'),
      bank_rel=value((b-native_open)[r.sector.eq('bank')]),financial_lead=value(b[r.sector.isin(['bank','finance'])])-value(b[~r.sector.isin(['bank','finance'])]),
      bank_sector_surprise=value(s[r.sector.eq('bank')]),it_sector_surprise=value(s[r.sector.eq('it')]),
      heavy_vs_broad=value(b[r['rank'].eq(1)])-value(b[r['rank'].gt(1)]),broad_gap=value(r.known_gap),
      above_proxy_vwap=value(r.vwap_deviation,'positive'),vwap_deviation=value(r.vwap_deviation),
      relative_volume=value(r.relative_volume),activity_dispersion=value(r.relative_volume,'std'),
      volume_concentration=concentration(np.exp(r.relative_volume.clip(-1,1)),1),relative_turnover=value(r.relative_turnover),
      negative_activity=value(r.relative_volume[b.lt(0)])-value(r.relative_volume[b.gt(0)]),
      return_per_volume=value(r.return_per_volume),financial_volume=value(r.relative_volume[r.sector.isin(['bank','finance'])]),
      signed_activity_proxy=value(r.activity_sign_proxy))
    for name,ss in [('subset1',r[r.stock.isin(sets[0])]),('subset2',r[r.stock.isin(sets[1])]),('without_heavy',r[r['rank'].gt(1)]),
                    ('action_clean',r[r.date_ex_action.eq(0)])]:
        d[name+'_above']=value(ss.ret_open,'positive')
        d[name+'_dispersion']=value(ss.ret_open,'std')
    for sym,key,ref in [('NIFTYBEES','etf','cash'),('BANKBEES','bank_etf','bank')]:
        if sym in et.index:
            d[key+'_recent_open']=float(et.at[sym,'ret_open'])
            d[key+'_recent_last5']=float(et.at[sym,'last5'])
            d[key+'_volume']=float(et.at[sym,'relative_volume'])
            d[key+'_vwap']=float(et.at[sym,'vwap_deviation'])
            d[key+'_last_time']=et.at[sym,'cutoff_bar_end']
    return d


def history_state():
    x=matrix('features-5.csv',V14)
    ew=matrix('official-index-closes.csv',V11)
    y=pd.DataFrame(index=ew.index)
    lp=np.log(ew)
    eq500=lp.nifty500equalweight-lp.nifty500
    eq50=lp.nifty50equalweight-lp.nifty50
    y['eq50_spread1']=eq50.diff()
    for h in (1,5,21):
        y[f'eq500_spread{h}']=eq500.diff(h)
    y['official_finance1']=(lp.niftyfinancialservices-lp.nifty50).diff()
    fields={'basis_previous':'front_basis','previous_same_contract':'same_contract_cash_gap','prior_future_curve':'curve_30d',
       'previous_parity_gap':'future_parity_gap','iv_prev':'atm','iv_skew':'iv_skew','iv_term':'iv_term','iv_curvature':'iv_curvature',
       'vix_level':'vix_level','OI_pc_prior':'pc_oi','forex_yesterday':'usd_inr5',
       'us_yesterday':'us_shock','global_vix':'vix_us','us_breadth':'us_breadth5','fx_risk':'fx_shock',
       'domestic_rotation_finance':'finance','domestic_rotation_defensive':'defensive','rolling_rv5':'har5',
       'trailing_vol':'rv21','prior_ret5':'cash5','prior_ret21':'cash21','surface_available':'surface_available'}
    y=y.join(x.reindex(columns=list(fields.values())).rename(columns={v:k for k,v in fields.items()}),how='outer')
    y['basis_previous_z']=(y.basis_previous-y.basis_previous.shift(1).rolling(35,min_periods=15).median())/y.basis_previous.shift(1).rolling(35,min_periods=15).std().clip(.00003)
    y['option_source_day']=x.option_day
    return y


def target_window(bars,apply_at,p,idx,cohort):
    dt=bars.index
    start=dt.searchsorted(apply_at,side='left')
    if start>=len(bars) or dt[start]!=apply_at:
        return None
    close=p.close.iloc[idx]
    spot=bars.open.iloc[start]
    if not np.isfinite(spot) or spot<=0:return None
    o=dict(day=p.index[idx],cutoff=apply_at.strftime('%H:%M'),cohort=cohort,origin=p.index[idx-1],label_anchor=float(spot),
       target_first_bar=dt[start].isoformat(),official_open=float(p.open.iloc[idx]),official_close=float(close))
    for n,label in [(3,'r15'),(6,'r30'),(12,'r60')]:
        if start+n<=len(bars) and dt[start+n-1]==apply_at+pd.Timedelta(minutes=5*(n-1)):
            o[label]=np.log(bars.close.iloc[start+n-1]/spot)
            o['end_'+label]=p.index[idx]
    o.update(regular_residual=np.log(close/spot),end_regular_residual=p.index[idx])
    tail=bars.iloc[start:]
    if len(tail):
        raw=np.diff(np.log(np.r_[spot,tail.close]))
        o.update(remaining_vol=np.sqrt(raw@raw),remaining_range=np.log(tail.high.max()/tail.low.min()),
             touch_up=float(tail.high.max()/spot>=1.005),touch_down=float(tail.low.min()/spot<=.995),
             end_remaining_vol=p.index[idx],end_remaining_range=p.index[idx],end_touch_up=p.index[idx],end_touch_down=p.index[idx])
    if idx+1<len(p):
        o['next_session']=np.log(p.close.iloc[idx+1]/close)
        o['end_next_session']=p.index[idx+1]
    for h in (3,5,10,21):
        j=idx+h-1
        if j<len(p):
            o[f'remaining_{h}']=np.log(p.close.iloc[j]/spot)
            o[f'end_remaining_{h}']=p.index[j]
    o['abs_regular']=abs(o['regular_residual']);o['end_abs_regular']=p.index[idx]
    return o


def build():
    f=pd.read_csv(OUT/'stock-snapshots.csv.gz',low_memory=False)
    roster=pd.read_csv(OUT/'historical-stock-basket.csv')
    r=roster[roster.sector.ne('ETF')]
    rng=np.random.default_rng(SEED)
    subsets=[]
    for _ in range(2):
        subsets.append({k for _,z in r.groupby('sector') for k in rng.choice(z.stock,size=max(2,len(z)//2),replace=False)})
    save('stock-random-subsets.json',dict(seed=SEED,subsets=[sorted(z) for z in subsets],largest_exclusions=r[r['rank'].eq(1)].stock.tolist()))
    cross=[]
    stock_returns={}
    for key,g in f.groupby(['day','cutoff'],sort=True):
        cross.append(dict(day=key[0],cutoff=key[1],**cross_section(g,subsets)))
        stock_returns[key]=g.loc[g.interval_minutes.eq(5)&~g.sector.isin(['native','ETF']),'ret_open'].to_numpy(float)
    cross=pd.DataFrame(cross).sort_values(['day','cutoff'])
    close_x=cross[cross.cutoff.eq('17:00')].set_index('day')
    history=history_state()
    o=matrix('opening-baseline-expectation.csv')
    n,_files,_miss=candles((V13/'sources/upstox').glob('nifty-5m-*'),5)
    p=matrix('cash-panel/cash.csv',V16)
    anns=pd.read_csv(OUT/'announcement-availability.csv.gz',low_memory=False)
    anns['ts']=pd.to_datetime(anns.eligible,utc=True,format='mixed').dt.tz_convert(IST)
    attrs=roster.set_index('stock').sector
    anns['sector']=anns.stock.map(attrs)
    feat=[]; targets=[]; n0=[]
    look={(d,t):g for (d,t),g in cross.set_index(['day','cutoff']).iterrows()}
    for i,day in enumerate(p.index):
        if i==0:continue
        prev=p.index[i-1]
        cash=n.get(day)
        if cash is None or len(cash)<24 or cash.index[0]!=stamp(day,'09:15') or day in {'2025-10-21','2026-11-08'}:
            continue
        prev_close=p.close.iloc[i-1]
        official_open=p.open.iloc[i]
        truegap=np.log(official_open/prev_close)
        snap_gap=np.log(cash.open.iloc[0]/prev_close)
        risk=history.loc[prev]
        old_surface=risk.option_source_day if 'option_source_day' in risk else None
        if pd.notna(old_surface):
            assert old_surface<day
        earlier=o.loc[day] if day in o.index else None
        if earlier is not None:
            assert earlier.last_matured<day and pd.Timestamp(earlier.decision)<stamp(day,'09:00')
        for clock in SESSION_CLOCKS:
            dt=stamp(day,clock)
            y=target_window(cash,dt,p,i,cohorts(np.array([day]))[0])
            if y is None:continue
            eligible=cash[cash.end.le(dt-pd.Timedelta(minutes=5))]
            if not len(eligible):continue
            cur=float(eligible.close.iloc[-1])
            step=np.diff(np.log(np.r_[cash.open.iloc[0],eligible.close]))
            gap_hist=dict(risk.drop(labels=['option_source_day']).to_dict())
            x0=look.get((day,clock),pd.Series(dtype=float))
            q={**gap_hist,**x0.to_dict()}
            if 'stock_n' not in q:q['stock_n']=0
            xopen=np.log(cur/cash.open.iloc[0])
            q['stock_outperform']=value(stock_returns[(day,clock)]-xopen,'positive') if q['stock_n']>=14 else np.nan
            for k in ['bank','finance','it','auto','energy','defensive']:
                market_end=q.get(k+'_index_time')
                if isinstance(market_end,str):
                    same=eligible[eligible.end.le(pd.Timestamp(market_end))]
                    known_return=np.log(same.close.iloc[-1]/cash.open.iloc[0]) if len(same) else np.nan
                    q[f'native_{k}_rel']=q.get(k+'_index_ret_open',np.nan)-known_return
                else:
                    q[f'native_{k}_rel']=np.nan
            u=[q.get(f'native_{k}_rel',np.nan) for k in ['bank','finance','it','energy','auto','defensive']]
            q['native_sync']=corr_score(u);q['native_dispersion']=value(u,'std')
            q['native_bank_accel']=q.get('bank_index_last5',np.nan)-step[-1]
            # Issuer and traded ETF returns use the same completed-session endpoints as the cash controls.
            etime=q.get('etf_last_time')
            maybe=eligible[eligible.end.le(pd.Timestamp(etime))] if isinstance(etime,str) else []
            q['nifty_etf_tracking']=q.get('etf_recent_open',np.nan)-np.log(maybe.close.iloc[-1]/cash.open.iloc[0]) if len(maybe) else np.nan
            q['bank_etf_tracking']=q.get('bank_etf_recent_open',np.nan)-q.get('bank_index_ret_open',np.nan) if q.get('bank_etf_last_time')==q.get('bank_index_time') else np.nan
            available_anns=anns[anns.ts.le(dt)&anns.ts.gt(stamp(prev,'17:00'))]
            q['news_results']=int(available_anns.results.sum())
            q['news_schedule']=int(available_anns.board_schedule.sum())
            q['news_action']=int(available_anns.corp_action.sum())
            q['news_finance']=int(available_anns.sector.isin(['bank','finance']).sum())
            q['news_broad']=available_anns.stock.nunique()
            exp=earlier.expected_log_gap if earlier is not None else np.nan
            sig=earlier.forecast_log_std if earlier is not None else np.nan
            mean_gap=earlier.expected_gap if earlier is not None else np.nan
            sigma_gap=earlier.pred_gap_std if earlier is not None else np.nan
            surprise=np.expm1(truegap)-mean_gap
            z=surprise/max(sigma_gap,.001) if np.isfinite(sigma_gap) else np.nan
            qs=(np.expm1(snap_gap)-mean_gap)/max(sigma_gap,.001) if np.isfinite(sigma_gap) else np.nan
            observed_move=np.log(cur/prev_close)
            q.update(day=day,cutoff=clock,decision=dt.isoformat(),feature_last_bar=eligible.end.iloc[-1].isoformat(),
                     old_cash=prev,official_open_receipt='exchange open label post-auction, tested against first recorded bar open',
                     option_source=old_surface,known_move=observed_move,known_rth=xopen,
                     cash_last5=step[-1],cash_last15=float(step[-3:].sum()) if len(step)>=3 else np.nan,
                     gap_seen=truegap,prefix_rv=np.sqrt(step@step),prefix_range=np.log(eligible.high.max()/eligible.low.min()),
                     expected_gap=exp,pred_gap_std=sig,open_surprise=surprise,expected_open_arithmetic=mean_gap,open_surprise_z=z,proxy_surprise_z=qs,
                     abs_surprise_z=abs(z),surprise_gift_remaining=(observed_move-exp),cash_vs_gift_repricing=observed_move-exp,
                     surprise_x_breadth=z*q.get('stock_above_open',np.nan),surprise_x_finance=z*q.get('financial_lead',np.nan))
            y['eligible_stocks']=q['stock_n']
            y['predicted_open_available']=int(np.isfinite(exp))
            y['open_proxy_disagreement']=abs(snap_gap-truegap)
            assert pd.Timestamp(q['feature_last_bar'])+pd.Timedelta(minutes=5)<=dt
            assert pd.Timestamp(y['target_first_bar'])>=dt
            feat.append(q);targets.append(y)
        n0.append(dict(day=day,official_open=official_open,observed_first_bar_open=cash.open.iloc[0],
                  open_gap=truegap,observed_open_gap=snap_gap,expected_gap=earlier.expected_log_gap if earlier is not None else np.nan,
                  prediction_stamp=earlier.decision if earlier is not None else None))
    f=pd.DataFrame(feat).sort_values(['day','cutoff'])
    f['stock_breadth_change']=f.stock_above_open-f.groupby('day').stock_above_open.transform('first')
    f['stock_acceleration']=f.groupby('day').stock_above_open.diff().groupby(f.day).diff()
    f['liquidity_acceleration']=f.groupby('day').relative_volume.diff()
    for k,d in [('nifty_etf_tracking','etf_tracking_vs_past'),('bank_etf_tracking','bank_tracking_vs_past')]:
        f[d]=f[k]-f.groupby('cutoff')[k].transform(lambda x:x.shift(1).rolling(25,min_periods=10).median())
    y=pd.DataFrame(targets).sort_values(['day','cutoff'])
    assert not f.duplicated(['day','cutoff']).any()
    write('intraday-feature-panel.csv.gz',f)
    write('intraday-target-panel.csv.gz',y)
    write('observed-open_and_surprise.csv',pd.DataFrame(n0))
    sc=pd.DataFrame(n0)
    save('intraday-timing-receipt.json',dict(clocks=SESSION_CLOCKS,rows=len(f),dates=f.day.nunique(),paired_preauction_expectation=int(sc.expected_gap.notna().sum()),
       cash_open_first_bar_exact=int(sc.official_open.eq(sc.observed_first_bar_open).sum()),
       primary='Only preceding live-equivalent bars with five minute publication margin. Outcome starts at the first independent cash-bar open at the decision. Official auction open usable after the open.',
       fallback='First recorded cash-bar open is a separate surprise sensitivity; original V16 cash target anchored to the official opening value.'))
    print('Built',len(f),'post-open snapshots across',f.day.nunique(),'unique market days',flush=True)
    # Original horizons are drawn before the first opening, with distinct actual information sets.
    base=matrix('session-targets.csv',V16)
    gm=pd.read_csv(OUT/'gift-decision-clock.csv')
    gift_close=gm[gm.clock.eq('prior_close')].set_index('day').return_1530
    lookup_v16=pd.read_csv(V16/'decision-features.csv.gz',low_memory=False)
    pre=lookup_v16[lookup_v16.cutoff.eq('08:55')].set_index('day')
    rows=[];labels=[]
    cols=['prior_ret5','prior_ret21','rolling_rv5','trailing_vol','domestic_rotation_finance','domestic_rotation_defensive','iv_prev','iv_skew','iv_term',
          'vix_level','basis_previous','prior_future_curve']
    no_lead=set(PRE_STOCK)|{'stock_n','nifty_etf_tracking','etf_volume'}
    for i in range(1,len(p)):
        dd,pp=p.index[i],p.index[i-1]
        prev_close=p.close.iloc[i-1]
        q0=history.reindex([pp]).iloc[0]
        stock=close_x.loc[pp] if pp in close_x.index else pd.Series(dtype=float)
        core={k:stock.get(k,np.nan) for k in no_lead}
        core.update({k:q0.get(k,np.nan) for k in cols+list(EW)})
        for tm in ('previous_1700','preauction_0855'):
            dec=stamp(pp,'17:00') if tm=='previous_1700' else stamp(dd,'08:55')
            earlier=o.loc[dd] if dd in o.index and tm=='preauction_0855' else None
            yy={**core,'expected_gap':earlier.expected_log_gap if earlier is not None else gift_close.get(dd,np.nan),
                 'pred_gap_std':earlier.forecast_log_std if earlier is not None else np.nan}
            if tm=='preauction_0855':
                for k in ('eq6','us_mean','asia_mean','gift_proxy','vix_move','foreign_sd','us_asia'):
                    yy[k]=pre.at[dd,k] if dd in pre.index else np.nan
            rows.append(dict(day=dd,origin=pp,cutoff=tm,decision=dec.isoformat(),**yy))
        zz=dict(day=dd,origin=pp,cohort=cohorts(np.array([dd]))[0])
        for h,k in [('gap',1),('original1',1),('original3',3),('original5',5),('original10',10),('original21',21)]:
            if i+k-1>=len(p):continue
            date=p.index[i+k-1]
            zz[h]=np.log((p.open.iloc[i] if h=='gap' else p.close.iloc[i+k-1])/prev_close)
            zz['end_'+h]=date
        for h in HORIZONS:
            tag='five' if h==5 else 'twentyone'
            zz[f'cohort_{h}']=base.at[dd,'cohort_'+tag] if dd in base.index else ''
        zz['initial_rth']=np.log(p.close.iloc[i]/p.open.iloc[i]);zz.update(end_initial_rth=dd)
        labels.append(zz)
    write('original-feature-panel.csv.gz',pd.DataFrame(rows))
    write('original-target-panel.csv',pd.DataFrame(labels))


if __name__=='__main__':
    build()
