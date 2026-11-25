"""Causal positioning features with observation dates, source guards and sector proxies."""
from .common import *
from .acquire import sessions
from .database import release,next_dates
from research.nifty_forecast_v16.model import fit

FUTURES=('ordinary_oi_change','ordinary_oi_5','ordinary_oi_concentration','front_basis','curve_30d','days_to_expiry','roll_event')
LEVEL=('FII_index_futures_level','DII_index_futures_level','Pro_index_futures_level',
       'FII_stock_futures_level','DII_stock_futures_level','FII_index_calls_level','FII_index_puts_level',
       'FII_stock_calls_level','FII_stock_puts_level')
CHANGES=('FII_index_futures_d1','FII_index_futures_d5','FII_index_futures_d21','DII_index_futures_d5',
         'Pro_index_futures_d5','FII_stock_futures_d5','FII_index_calls_d5','FII_index_puts_d5',
         'FII_stock_calls_d5','FII_stock_puts_d5','FII_index_futures_accel','FII_index_futures_persist')
CROWD=('index_futures_detail_hhi_z','stock_futures_detail_hhi_z','index_futures_disagree',
       'index_calls_disagree','fii_gross_volume_share','failed_breadth_crowding','derivative_reduction_proxy')
INNOV=('innovation_1','innovation_5','innovation_dii','innovation_option_call','innovation_option_put')
POSITION=LEVEL[:3]+CHANGES[:7]+CROWD
DELIVERY=tuple('del_'+k for k in ('intensity','high_frac','rising_frac','dispersion','sector_equal','financial_concentration',
                         'flow_concentration','adv_high','dec_high','consolidation','up_low','down_low','volatility_concentration'))
DEALS=tuple('deal_'+k for k in ('n','size','premium','rolling_balance','recurrence','cash_turnover_share','block_share','elevated'))
CORE=POSITION+DELIVERY+DEALS
SECTORS={'bank':'niftybank','finance':'niftyfinancialservices','it':'niftyit','energy':'niftyenergy',
         'auto':'niftyauto','consumer':'niftyfmcg','materials':'niftymetal','health':'niftypharma'}
VINTAGES=('open_interest','traded_volume','delivery','deals','futures')

def ratio(a,b):
    return a/b.where(b.gt(0))

def prior_z(s,win=60,n=25):
    lag=s.shift().rolling(win,min_periods=n)
    return ((s-lag.mean())/lag.std().where(lag.std().gt(1.e-10))).clip(-8,8)

def part_features(days):
    d=csv('participants.csv.gz')
    d['is_count']=1
    checks=csv('participant-audit.csv.gz')
    eligible=checks[checks.status.eq('accepted')].pivot(index='day',columns='kind',values='present').reindex(days)
    totals={}
    for k in ('open_interest','traded_volume'):
        totals[k]=d[d.kind.eq(k)].set_index(['day','instrument','participant']).sort_index()
    z={}
    for instr in d.instrument.unique():
        a=totals['open_interest'].xs(instr,level='instrument')
        g=a.gross_share.unstack('participant').reindex(days)
        net=a.net_market_share.unstack('participant').reindex(days)
        z[instr+'_detail_hhi']=g.pow(2).sum(axis=1,min_count=4)
        z[instr+'_detail_hhi_z']=prior_z(z[instr+'_detail_hhi'])
        z[instr+'_disagree']=net.std(axis=1,ddof=0,skipna=False)
        for group in ['FII','DII','Pro','Client']:
            p=group+'_'+instr
            n=net[group]
            gross=g[group]
            z[p+'_level']=n
            z[p+'_own_ratio']=a.xs(group,level='participant').net_over_gross.reindex(days)
            z[p+'_gross_share']=gross
            for l in (1,5,21):
                z[p+'_d'+str(l)]=n.diff(l)
            z[p+'_accel']=n.diff().diff()
            z[p+'_persist']=np.sign(n.diff()).rolling(5,min_periods=4).mean()
    w=totals['traded_volume'].xs('index_futures',level='instrument')
    z['fii_gross_volume_share']=w.xs('FII',level='participant').gross_share.reindex(days)
    z['participant_volume_z']=prior_z(w.gross_contracts.groupby(level='day').sum().reindex(days).pipe(np.log1p))
    return pd.DataFrame(z,index=days),eligible

def cash_state(days):
    i=csv('official-index-closes.csv',V11).rename(columns={'Unnamed: 0':'day'}).set_index('day').reindex(days)
    f=csv('futures-observed.csv',V12).rename(columns={'Unnamed: 0':'day'}).set_index('day').reindex(days)
    z=csv('nifty-futures.csv.gz')
    z['oi_clean']=z.oi_contracts.where(z.oi_unit_reconciles)
    g=z.groupby('day')
    total=g.oi_clean.sum(min_count=1).reindex(days)
    invalid=g.oi_unit_reconciles.min().reindex(days).eq(False)
    total=total.mask(invalid)
    f['ordinary_oi']=total
    f['ordinary_oi_change']=np.log(total.where(total.gt(0))).diff()
    f['ordinary_oi_5']=np.log(total.where(total.gt(0))).diff(5)
    f['ordinary_oi_concentration']=ratio(g.oi_clean.max().reindex(days),total)
    f['days_to_expiry']=(pd.to_datetime(f.front_expiry)-pd.Series(pd.to_datetime(days),index=days)).dt.days
    f['cash_ret']=np.log(i.nifty50).diff()
    f['cash_momentum']=np.log(i.nifty50).diff(5)
    f['cash_breadth_change']=np.log(i.nifty500equalweight/i.nifty50).diff(5)
    f['normalized_cash_vol']=f.cash_ret.rolling(10,min_periods=8).std()
    v=csv('original-feature-panel.csv.gz',V17)
    v=v[v.cutoff.eq('previous_1700')].set_index('origin').reindex(days)
    f['state_iv']=v.iv_prev
    f['state_skew']=v.iv_skew
    return f,i

def get_stock(days):
    d=csv('delivery-fixed-issuers.csv.gz').sort_values(['day','stock'])
    d=d[d['isin'].notna()].rename(columns={'isin':'issuer_id'}).drop_duplicates(['day','issuer_id']).copy()
    # Trust the dated reference close when the whole-share file and cash bhavcopy agree.
    d=d[d.price_crosscheck.eq(True)].copy()
    d['log_return']=np.log(d.close/d.previous_close)
    d['pct']=d.delivery_pct_recomputed.where(d.delivery_percent_match.eq(True)&d.delivery_pct_recomputed.between(0,100))
    d['lqty']=np.log1p(d.delivered_qty.where(d.delivered_qty.ge(0)))
    d['lvol']=np.log1p(d.traded_qty.where(d.traded_qty.gt(0)))
    d['lturn']=np.log1p(d.turnover.where(d.turnover.gt(0)))
    for k in ('pct','lqty','lvol','lturn'):
        d[k+'_z']=d.groupby('issuer_id')[k].transform(prior_z)
    d['pct_z25']=d.groupby('issuer_id').pct.transform(lambda s:prior_z(s,25,17))
    d['pct_rising']=d.groupby('issuer_id').pct.diff().gt(0).where(d.groupby('issuer_id').pct.diff().notna())
    d['persistence']=d.groupby('issuer_id').pct_z.transform(lambda x:x.gt(1).where(x.notna()).rolling(5,min_periods=4).mean())
    d['trailing_abs']=d.groupby('issuer_id').log_return.transform(lambda s:s.abs().shift().rolling(25,min_periods=15).median())
    d['liquidity_weight']=d.groupby('issuer_id').turnover.transform(lambda s:s.shift().rolling(25,min_periods=15).median())
    d['return5']=d.groupby('issuer_id').log_return.transform(lambda s:s.rolling(5,min_periods=5).sum())
    d['volatility25']=d.groupby('issuer_id').log_return.transform(lambda s:s.rolling(25,min_periods=15).std())
    pre=pd.read_csv(V17/'historical-stock-basket.csv').drop_duplicates('isin').set_index('isin').sector
    e=csv('issuer-events.csv.gz',V18,usecols=['isin','sector','eligible']).rename(columns={'isin':'issuer_id','sector':'from_filing'})
    e=e[e.issuer_id.notna()&e.from_filing.ne('other')].copy()
    e['filetime']=pd.to_datetime(e.eligible)
    d['cash_time']=pd.to_datetime(d.day+' 15:30:00')
    d=pd.merge_asof(d.sort_values('cash_time'),e[['issuer_id','filetime','from_filing']].sort_values('filetime'),
                     left_on='cash_time',right_on='filetime',by='issuer_id',direction='backward')
    d['sector']=d.issuer_id.map(pre).where(d.day.gt('2025-01-29')).fillna(d.from_filing).fillna('other')
    d['known_group']=d.sector.ne('other')
    right=csv('corporate-actions-audit.csv',V17,usecols=['isin','ex_date']).rename(columns={'isin':'issuer_id','ex_date':'day'}).drop_duplicates()
    right['archived_corporate_action']=True
    d=d.merge(right,on=['issuer_id','day'],how='left',validate='m:1')
    d['archived_corporate_action']=d.archived_corporate_action.eq(True)
    stock_group=csv('issuer-seed.csv').sort_values('stock').stock.to_numpy()
    shuffled=np.random.default_rng(SEED).permutation(stock_group)
    d['half0']=d.stock.isin(shuffled[:len(shuffled)//2])
    d['top_seed']=d.stock.isin(csv('issuer-seed.csv').head(15).stock)
    d['source_seq']=pd.Series(np.arange(len(days)),index=days).reindex(d.day).to_numpy()
    return d.sort_values(['day','stock']).reset_index(drop=True)

def weights(a,w):
    live=a.notna()&w.notna()&w.gt(0)
    return float(np.average(a[live],weights=w[live])) if live.any() else np.nan

def del_views(stock,days):
    rows=[];sector=[]
    for day,g in stock.groupby('day'):
        a=g[g.pct_z.notna()&g.log_return.notna()].copy()
        if len(a)<40 or day<='2025-01-29':
            continue
        high=a.pct_z.ge(1)
        low=a.pct_z.le(-1)
        retail=a.delivery_value_inr_close_proxy
        market=retail.sum(min_count=1)
        hhi=float((retail/market).pow(2).sum()) if market>0 else np.nan
        fin=a.sector.isin(['bank','finance'])
        sect=a[a.known_group].groupby('sector').pct_z.mean()
        r=dict(day=day,del_n=len(a),del_intensity=a.pct_z.mean(),del_high_frac=high.mean(),del_rising_frac=a.pct_rising.mean(),
              del_dispersion=a.pct_z.std(ddof=0),del_sector_equal=sect.mean(),del_financial_concentration=retail[fin].sum()/market,
              del_flow_concentration=hhi,del_adv_high=(high&a.log_return.gt(0)).mean(),del_dec_high=(high&a.log_return.lt(0)).mean(),
              del_consolidation=(high&a.log_return.abs().le(.5*a.trailing_abs)).mean(),
              del_up_low=(low&a.log_return.gt(0)).mean(),del_down_low=(low&a.log_return.lt(0)).mean(),
              del_volatility_concentration=weights(a.volatility25,retail)*hhi,del_relative_qty=a.lqty_z.mean(),
              del_persist=a.persistence.mean(),del_weight_liquid=weights(a.pct_z,a.liquidity_weight),
              del_z25=a.pct_z25.mean(),del_ex_heavy=a.loc[~a.top_seed,'pct_z'].mean(),
              del_no_actions=a.loc[~a.archived_corporate_action&~a.log_return.abs().gt(.18),'pct_z'].mean(),
              del_half0=a.loc[a.half0,'pct_z'].mean(),del_half1=a.loc[~a.half0,'pct_z'].mean(),
              del_volume_control=a.lvol_z.mean(),del_turnover_control=a.lturn_z.mean(),
              del_pricectl_advance=a.log_return.gt(0).mean(),del_pricectl_dispersion=a.log_return.std(ddof=0))
        rows.append(r)
        for group,q in a[a.sector.isin(SECTORS)].groupby('sector'):
            if len(q)<3:
                continue
            sector.append(dict(day=day,sector=group,sector_index=SECTORS[group],n=len(q),delivery=q.pct_z.mean(),
                               delivery_high=q.pct_z.ge(1).mean(),delivery_signed=(np.sign(q.log_return)*q.pct_z).mean(),
                               liquid_delivery=weights(q.pct_z,q.liquidity_weight),price=q.log_return.mean(),
                               turnover=q.lturn_z.mean(),volume=q.lvol_z.mean()))
    return pd.DataFrame(rows).set_index('day').reindex(days),pd.DataFrame(sector)

def deals(days):
    z=csv('deal-audited.csv.gz')
    a=csv('deal-archives.csv.gz')
    ok=a.groupby('month').category.nunique()
    g=z.groupby('day')
    n=g.size().reindex(days)
    v=g.matched_block_once_proxy.sum().reindex(days)
    support=pd.Series(days.str[:7].map(ok)==2,index=days)
    def complete(x):
        return x.fillna(0).where(support)
    def with_cash_reference(x):
        # A day with reported legs and missing eligible cash data remains missing.
        return x.mask(n.isna(),0.).where(support)
    out=pd.DataFrame(index=days)
    out['deal_n']=np.log1p(complete(n))
    out['deal_size']=np.log1p(complete(v))
    out['deal_premium']=with_cash_reference(g.premium_to_previous_close.median().reindex(days))
    out['deal_rolling_balance']=complete(g.signed_reported_leg.sum().reindex(days)).rolling(5,min_periods=4).sum().pipe(lambda s:np.arcsinh(s/1.e9))
    duplicates=z.duplicated(['stock','category'],keep='first').astype(float)
    out['deal_recurrence']=complete(duplicates.groupby(z.day).mean().reindex(days))
    out['deal_cash_turnover_share']=with_cash_reference(g.share_of_day_turnover.median().reindex(days)).clip(0,4)
    out['deal_block_share']=complete(z.category.eq('block').groupby(z.day).mean().reindex(days))
    out['deal_elevated']=prior_z(out.deal_size)
    alt=z.loc[z.matched_block_once_proxy.le(z.groupby('day').matched_block_once_proxy.transform('max'))].copy()
    alt.loc[alt.groupby('day').matched_block_once_proxy.idxmax(),'matched_block_once_proxy']=0.
    out['deal_without_largest']=np.log1p(complete(alt.groupby('day').matched_block_once_proxy.sum().reindex(days)))
    out['deal_naive_amount']=np.log1p(complete(g.reported_consideration.sum().reindex(days)))
    return out,support

def innovations(d):
    state=('cash_ret','cash_momentum','cash_breadth_change','normalized_cash_vol','ordinary_oi_change','front_basis',
           'curve_30d','days_to_expiry','state_iv','state_skew')
    yp=('FII_index_futures_d1','FII_index_futures_d5','DII_index_futures_d5','FII_index_calls_d5','FII_index_puts_d5')
    rows=[];fits=[]
    for name,target in zip(INNOV,yp):
        yes=d[target].to_numpy(float)
        x=d[list(state)].assign(prior_position=d[target].shift(),prior_change5=d[target].shift(5))
        a=x.to_numpy(float)
        ans=np.full(len(d),np.nan)
        for i in range(len(d)):
            t=np.flatnonzero(np.isfinite(yes[:i]))[-120:]
            if len(t)<40 or not np.isfinite(yes[i]):
                continue
            m=fit(a[t],yes[t],75.)
            ans[i]=yes[i]-m.values(a[i])
            fits.append(dict(observation=d.index[i],training_last=d.index[t[-1]],n=len(t),model=name,predicted=m.values(a[i]),
                             residual=ans[i],**m.receipt(list(x))))
        rows.append(pd.Series(ans,index=d.index,name=name))
    return pd.concat(rows,axis=1),fits

def make_panel(d,support,days):
    old=csv('original-feature-panel.csv.gz',V17,usecols=['day','cutoff','decision','origin'])
    event=csv('event-aggregate-features.csv.gz',V18,usecols=['day','cutoff','origin','decision_local'])
    post=event[event.cutoff.isin(POST)].drop(columns='decision_local').assign(decision=lambda a:a.day+'T'+a.cutoff+':00+05:30')
    a=pd.concat([old,post],ignore_index=True).sort_values(['day','cutoff'])
    cal=pd.Series(np.arange(len(days)),index=days)
    support=support.reindex(days)
    for dt in (0,1,5):
        # Positioning observation may only enter at 08:15 on the NEXT exchange session.
        r=a.decision.str[:10].map(cal)-1-dt
        ix=np.where(r.notna()&r.ge(0),r,-1).astype(int)
        date=np.where(ix>=0,days.to_numpy()[ix],None)
        values=d.reindex(date).reset_index(drop=True)
        following=next_dates(days)
        t=pd.DataFrame({'source_day':date,'source_release':[release(k,following) if k else None for k in date]})
        for k in VINTAGES:
            t[k+'_observed']=support[k].reindex(date).fillna(False).astype(int).to_numpy()
        if dt==0:
            out=pd.concat([a.reset_index(drop=True),t,values],axis=1)
        else:
            selected=[*CORE,*INNOV,'deal_without_largest']
            out=pd.concat([out,t[['source_day','source_release']].add_suffix(f'_delay{dt}'),
                           values[selected].add_suffix(f'_delay{dt}')],axis=1)
    available=out.source_release.notna()
    assert out.loc[available,'source_release'].le(out.loc[available,'decision']).all()
    assert out.loc[available,'source_day'].lt(out.loc[available,'decision'].str[:10]).all()
    return out

def main():
    days=sessions()
    z,support=part_features(days)
    f,index=cash_state(days)
    d=get_stock(days)
    own,sectors=del_views(d,days)
    bulk,valid=deals(days)
    all_=pd.concat([z,f,own,bulk],axis=1)
    all_['failed_breadth_crowding']=all_.index_futures_detail_hhi_z*all_.cash_breadth_change
    all_['derivative_reduction_proxy']=all_.ordinary_oi_change.clip(upper=0)*all_.index_futures_detail_hhi_z
    pred,fits=innovations(all_)
    all_=all_.join(pred)
    support=support.assign(delivery=own.del_n.notna(),deals=valid,futures=f.ordinary_oi.notna())
    panel=make_panel(all_,support,days)
    write('positioning-daily-features.csv.gz',all_.reset_index())
    write('stock-delivery-features.csv.gz',d)
    write('sector-delivery-features.csv.gz',sectors)
    write('asof-positioning-features.csv.gz',panel)
    write('asof-positioning-coverage.csv',panel.groupby('cutoff',as_index=False)[[k+'_observed' for k in VINTAGES]].sum())
    with gzip.open(OUT/'position-innovation-fits.ndjson.gz','wt',encoding='utf8') as g:
        for receipt in fits:
            g.write(json.dumps(receipt,default=str,allow_nan=False)+'\n')
    save('feature-receipt.json',dict(days=len(days),stock_rows=len(d),sector_rows=len(sectors),decision_rows=len(panel),
          innovations=len(fits),documented_groups=sorted(set(d.sector)),source_fields={
           'participant_levels':LEVEL,'position_changes':CHANGES,'crowding':CROWD,'innovation':INNOV,
           'delivery':DELIVERY,'two_sided_deals':DEALS,'ordinary_nifty_futures':FUTURES},
          cap_weighting='Authentic historical issuer free-float weights unavailable for this universe. Equal-company, known-sector equal and lagged traded-liquidity weights are preserved. Official equal-weight index returns provide a separate measured comparator.',
          name_inner='Issuer identity uses dated NSE cash ISIN. Fixed January names and dates with authenticated mappings. No new names selected from later performance.',
          timing='STOCK and FO archive reports enter by the next NSE cash session 08:15 IST. Innovation fit uses only earlier raw observation days. Dated industry known by cash close or from frozen January roster.'))
    print('As-of panel ready',len(panel),len(fits),flush=True)

if __name__=='__main__':
    main()

