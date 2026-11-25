"""Company, sector and market aggregates at distinct historical decision clocks."""
from collections import deque
from .common import *

COUNT=('count2','count9','count31','issuer_count9','earnings9','financial9','count_shift','attached_rate')
TEXT=('lexical_direction','positive_rate','negative_rate','text_dispersion','uncertainty','material_concentration','financial_sign')
FUND=('fund_coverage','fund_growth_breadth','fund_profit_breadth','fund_surprise','fund_margins','fund_dispersion','fund_financial','fund_recent',
      'fund_debt_to_quarterly_sales','fund_operating_cash_to_sales')
WEIGHT=('weighted_sign','sector_balanced_sign','weighted_fund','sector_balanced_fund')
REACT=('reaction_mean','reaction_dispersion','reaction_size','reaction_fraction','reaction_peer')
DISAG=('fund_price_disagreement','text_price_disagreement','positive_muted','negative_high_vol','agreement_fraction')
ALTS=('alternative_sign','without_dominant','without_earnings','after_24h','after_72h','material_only','without_large_episodes')
SCHEDULE=('fed_count','rbi_count','earnings_notice_count','earnings_issuer_count','financial_notice_count','board_revision_count','known_front_expiry_in_window')
EXTRA=('delivery_median','delivery_dispersion','delivery_higher','fii_pos','dii_pos','bulk_balance','bulk_number','block_number',
       'us_first_print_cpi','us_first_print_cpi_change')
STATE=('prior_ret5','prior_ret21','rolling_rv5','trailing_vol','domestic_rotation_finance','domestic_rotation_defensive',
       'iv_prev','iv_skew','iv_term','vix_level','basis_previous','prior_future_curve','eq50_spread1','eq500_spread1','eq500_spread5','eq500_spread21','official_finance1')

def val(x):
    a=pd.to_numeric(x,errors='coerce').dropna()
    return float(a.mean()) if len(a) else np.nan

def spread(x):
    a=pd.to_numeric(x,errors='coerce').dropna()
    return float(a.std(ddof=0)) if len(a) else np.nan

def weight(x,w):
    mask=x.notna()&w.notna()&w.gt(0)
    return float(np.average(x[mask],weights=w[mask])) if mask.any() else np.nan

def dynamic_dates(q,timestamp,now,days):
    times=q[timestamp]
    lower=(pd.Timestamp(now)-pd.Timedelta(days=days)).isoformat(sep=' ')
    start=times.searchsorted(lower,side='right')
    stop=times.searchsorted(now,side='right')
    return q.iloc[start:stop]

def contacts(b,v,cut,start,h,expiry):
    # The cash horizon is approximated from weekdays and announcements known at issue.
    end=(pd.Timestamp(start)+pd.offsets.BDay(h-1)).strftime('%Y-%m-%d')
    policy=v[v.public_by.le(cut)&v.date.between(start,end)]
    notices=b.iloc[:b.public_by.searchsorted(cut,side='right')]
    changes=notices[notices.revision.eq(1)&notices.prior_scheduled.notna()]
    latest=notices.drop_duplicates(['symbol','scheduled'],keep='last')
    if len(changes):
        ix=pd.MultiIndex.from_arrays([latest.symbol,latest.scheduled])
        invalid=pd.MultiIndex.from_arrays([changes.symbol,changes.prior_scheduled])
        latest=latest.loc[~ix.isin(invalid)]
    placed=latest[latest.cancelled.eq(0)&latest.scheduled.between(start,end)]
    known=expiry[expiry.day.lt(cut[:10])]
    front=known.front_expiry.iloc[-1] if len(known) else None
    front_exposure=float(start<=front<=end) if isinstance(front,str) and front>=start else np.nan
    return dict(fed_count=int(policy.family.eq('FED').sum()),rbi_count=int(policy.family.eq('RBI').sum()),
                earnings_notice_count=len(placed),earnings_issuer_count=int(placed.symbol.nunique()),
                financial_notice_count=int(placed.sector.isin(['bank','finance']).sum()),board_revision_count=int(placed.revision.sum()),
                schedule_end=end,last_notice=placed.public_by.max() if len(placed) else None,
                known_front_expiry_in_window=front_exposure,known_front_expiry=front,
                known_front_expiry_source_day=known.day.iloc[-1] if len(known) else None)

def market_nonprice(x,y,z,dates,cpi,cut):
    d=cut[:10]
    i=int(dates.searchsorted(d,side='left'))-1
    if i<0:return dict.fromkeys(EXTRA,np.nan)
    eligible=dates[i]
    deliver=x.get(eligible)
    part=y.get(eligible)
    deals=z[(z.day<=eligible)&(z.day>=(pd.Timestamp(eligible)-pd.Timedelta(days=9)).strftime('%Y-%m-%d'))]
    v=deliver.delivery_pct.dropna() if deliver is not None else pd.Series(dtype=float)
    def pos(t):
        if part is None:return np.nan
        u=part[part.participant.eq(t)]
        if u.empty:return np.nan
        lo=u.future_index_long.iloc[0]
        sh=u.future_index_short.iloc[0]
        return (lo-sh)/max(lo+sh,1.)
    side=next((k for k in deals if k.lower() in ('bd_buy_sell','buy_sell','bssl','bd_buy_sell_flag') or 'buy_sell' in k.lower()),None)
    sign=(deals[side].astype(str).str.upper().map({'BUY':1,'SELL':-1,'B':1,'S':-1}).mean() if side else np.nan)
    reports=cpi[cpi.eligible.le(cut)].sort_values('eligible')
    pr=reports.first_release_mom_pct.to_numpy(float)
    return dict(delivery_median=v.median(),delivery_dispersion=spread(v),delivery_higher=val(v.ge(50)),fii_pos=pos('FII'),dii_pos=pos('DII'),
                bulk_number=int(deals.file.astype(str).str.startswith('bulk').sum()),block_number=int(deals.file.astype(str).str.startswith('block').sum()),
                bulk_balance=sign,non_price_max_day=eligible,us_first_print_cpi=pr[-1] if len(pr) else np.nan,
                us_first_print_cpi_change=pr[-1]-pr[-2] if len(pr)>1 else np.nan,
                us_first_print_available=reports.eligible.iloc[-1] if len(pr) else None)

def build(events,financial,stock,calendar,policy,timing,market):
    """Common historical and future-sentinel feature builder."""
    e=events.sort_values('eligible').reset_index(drop=True).copy()
    f=financial.sort_values('eligible').reset_index(drop=True).copy()
    s=stock.sort_values('decision').reset_index(drop=True)
    b=calendar.sort_values('public_by')
    expiry=csv('futures-observed.csv',V12).rename(columns={'Unnamed: 0':'day'}).sort_values('day')
    docket=csv('issuer-seed.csv').set_index('stock')
    liquidity=np.sqrt(docket.mean_turnover.clip(lower=1)/docket.mean_turnover.median()).clip(.25,4.)
    leader=set(docket.head(10).index)
    sectors=e[e.industry.fillna('').ne('')].drop_duplicates('symbol').set_index('symbol')[['sector','eligible']]
    for z in (e,f):z['liquidity_weight']=z.symbol.map(liquidity)
    aux=[]
    horizon=[]
    for clock,g in timing.sort_values('decision').groupby('cutoff',sort=False):
        past=deque(maxlen=35)
        for r in g.itertuples(index=False):
            cut=str(r.decision).replace('T',' ')[:19]
            date=pd.Timestamp(cut)
            if not FIRST<=cut[:10]<=FREEZE:continue
            days2=dynamic_dates(e,'eligible',cut,2)
            recent=dynamic_dates(e,'eligible',cut,9)
            older=dynamic_dates(e,'eligible',cut,31)
            material=recent[recent.material.eq(1)]
            q=recent.drop_duplicates('symbol',keep='last')
            fnow=dynamic_dates(f,'eligible',cut,130).drop_duplicates('symbol',keep='last').copy()
            fnow['sector0']=fnow.symbol.map(sectors.sector).where(fnow.symbol.map(sectors.eligible).fillna('9999').le(cut),'other')
            hist_expect=float(np.mean(past)) if len(past)>=12 else np.nan
            cycle=len(recent)
            past.append(cycle)
            lags=[dynamic_dates(e,'eligible',(date-pd.Timedelta(hours=h)).isoformat(sep=' '),9).drop_duplicates('symbol',keep='last') for h in (24,72)]
            daily=material.eligible.str[:10].value_counts() if len(material) else pd.Series(dtype=float)
            bunch=daily.index[daily>max(6,(hist_expect/6 if np.isfinite(hist_expect) else 6))]
            info=fnow.statistical_surprise.fillna(fnow.profit_qoq)
            fundsector=fnow.assign(tmp=info).groupby('sector0').tmp.mean()
            y=dynamic_dates(s,'decision',cut,9).drop_duplicates('symbol',keep='last')
            signs=y.published_fundamental_surprise.fillna(y.primary_text_sign)
            fn=y.published_fundamental_surprise
            ar=y.reaction_regular
            out=dict(day=r.day,origin=r.origin,cutoff=clock,decision_local=cut,
             count2=np.log1p(len(days2)),count9=np.log1p(len(recent)),count31=np.log1p(len(older)),issuer_count9=q.symbol.nunique(),
             earnings9=int(recent.family.eq('earnings').sum()),financial9=int(recent.sector.isin(['bank','finance']).sum()),
             count_shift=(cycle-hist_expect)/max(5,hist_expect) if np.isfinite(hist_expect) else np.nan,
             attached_rate=val(recent.attachment.fillna('').ne('')),archive_support=1,
             lexical_direction=val(q.text_sign),positive_rate=val(q.text_sign.gt(0)),negative_rate=val(q.text_sign.lt(0)),
             text_dispersion=spread(q.text_sign),uncertainty=val(q.explicit_uncertainty),
             material_concentration=float((material.symbol.value_counts(normalize=True)**2).sum()),
             financial_sign=val(q.loc[q.sector.isin(['bank','finance']),'text_sign']),fund_coverage=len(fnow),
             fund_growth_breadth=val(fnow.revenue_qoq.dropna().gt(0)),fund_profit_breadth=val(fnow.profit_qoq.dropna().gt(0)),
             fund_surprise=val(fnow.statistical_surprise),fund_margins=val(fnow.margin_delta),fund_dispersion=spread(info),
             fund_financial=val(info[fnow.sector0.isin(['bank','finance'])]),fund_recent=int(dynamic_dates(f,'eligible',cut,14).symbol.nunique()),
             fund_debt_to_quarterly_sales=val((fnow.reported_debt/fnow.sales.where(fnow.sales.gt(0))).clip(0,15)),
             fund_operating_cash_to_sales=val((91*fnow.reported_op_cash/fnow.cash_context_days/fnow.sales.where(fnow.sales.gt(0))).clip(-5,5)),
             weighted_sign=weight(q.text_sign,q.liquidity_weight),sector_balanced_sign=val(q.groupby('sector').text_sign.mean()),
             weighted_fund=weight(info,fnow.liquidity_weight),sector_balanced_fund=val(fundsector),
             reaction_mean=val(ar),reaction_dispersion=spread(ar),reaction_size=val(ar.abs()),reaction_fraction=val(ar.dropna().gt(0)),reaction_peer=val(y.peer_reaction),
             fund_price_disagreement=val(fn*ar),text_price_disagreement=val(y.primary_text_sign*ar),
             positive_muted=val(ar.abs().lt(.003)&signs.gt(0)),negative_high_vol=val(signs.lt(0)&y.prior_vol.gt(.022)),
             agreement_fraction=val((np.sign(signs)==np.sign(ar)).loc[ar.notna()&signs.ne(0)]),
             alternative_sign=val(q.category_direction_proxy),without_dominant=val(q.loc[~q.symbol.isin(leader),'text_sign']),
             without_earnings=val(q.loc[~q.family.eq('earnings'),'text_sign']),after_24h=val(lags[0].text_sign),after_72h=val(lags[1].text_sign),
             material_only=val(material.text_sign),without_large_episodes=val(q.loc[~q.eligible.str[:10].isin(bunch),'text_sign']),
             last_announcement=recent.eligible.max() if len(recent) else None,last_known_report=fnow.eligible.max() if len(fnow) else None,
             last_known_reaction=y.decision.max() if len(y) else None)
            out.update(market_nonprice(*market,cut))
            aux.append(out)
            for h in HORIZONS:
                horizon.append(dict(day=r.day,cutoff=clock,horizon=h,**contacts(b,policy,cut,r.day,h,expiry)))
    q=pd.DataFrame(aux)
    for k in ('last_announcement','last_known_report','last_known_reaction'):
        ok=q[k].notna()
        assert q.loc[ok,k].le(q.loc[ok,'decision_local']).all()
    return q,pd.DataFrame(horizon)

def load_inputs():
    e=csv('issuer-events.csv.gz')
    f=csv('primary-fundamental-events.csv.gz')
    c=csv('structured-financial-facts.csv.gz',usecols=['source_file','metric','duration'])
    c=c[c.metric.eq('op_cash')].drop_duplicates('source_file').set_index('source_file').duration
    f['cash_context_days']=f.source_file.map(c)
    px=csv('stock-event-pairs.csv.gz',usecols=['stage','horizon','day','decision','symbol','published_fundamental_surprise','primary_text_sign','reaction_regular','peer_reaction','prior_vol'])
    px=px[px.stage.eq('after_reaction')&px.horizon.eq(1)]
    cal=csv('scheduled-board-results.csv.gz')
    sect=e.sort_values('eligible').drop_duplicates('symbol').set_index('symbol').sector
    cal['sector']=cal.symbol.map(sect)
    pp=csv('policy-schedule.csv')
    timing=csv('original-feature-panel.csv.gz',V17)
    z=csv('intraday-feature-panel.csv.gz',V17,usecols=['day','cutoff','decision','old_cash'])
    z=z[z.cutoff.isin(['09:25','10:20'])].rename(columns={'old_cash':'origin'})
    timing=pd.concat([timing[['day','origin','cutoff','decision']],z[['day','origin','cutoff','decision']]],ignore_index=True)
    x=csv('delivery-statistics.csv.gz')
    y=csv('participant-open-interest.csv.gz')
    z=csv('bulk-block-events.csv.gz')
    dates=pd.Index(sorted(x.day.unique()))
    macro=(csv('macro-release-vintages.csv') if (OUT/'macro-release-vintages.csv').exists() else pd.DataFrame(columns=['eligible','first_release_mom_pct']))
    return e,f,px,cal,pp,timing,(dict(tuple(x.groupby('day'))),dict(tuple(y.groupby('day'))),z,dates,macro)

def run():
    f,s=build(*load_inputs())
    write('event-aggregate-features.csv.gz',f)
    write('event-schedule-exposures.csv.gz',s)
    cols=[*COUNT,*TEXT,*FUND,*WEIGHT,*REACT,*DISAG,*EXTRA]
    coverage=[]
    for c,g in f.groupby('cutoff'):
        coverage.extend(dict(cutoff=c,field=k,n=int(g[k].notna().sum()),sample_mean=val(g[k])) for k in cols)
    write('aggregate-feature-coverage.csv',pd.DataFrame(coverage))
    print('Built aggregate clocks',len(f),'and schedule exposures',len(s),flush=True)

if __name__=='__main__':
    run()
