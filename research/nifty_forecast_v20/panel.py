"""Build chronological information families and close-to-close targets."""
from .common import *

PRICE=('prior_ret5','prior_ret21','rolling_rv5','trailing_vol')
GROUPS={
 'offshore_gift':('gift_proxy','gift_cash_mark','gift_night'),
 'global_equities':('eq6','foreign_sd','us_asia','vix_move'),
 'domestic_internals':('domestic_rotation_defensive','basis_previous','prior_future_curve','same_day_sector_dispersion'),
 'financial_rotation':('domestic_rotation_finance','official_finance1','financial21','financial_lead_change'),
 'equal_weight_breadth':('eq50_spread1','eq500_spread1','eq500_spread5','eq500_spread21'),
 'stock_participation':('allEQ_advance','allEQ_dispersion','allEQ_activity_relative','seed300_advance','seed300_concentration'),
 'corporate_announcements':('count2','count9','count31','earnings9','lexical_direction','uncertainty','material_only'),
 'structured_financials':('fund_growth_breadth','fund_profit_breadth','fund_surprise','fund_dispersion','fund_financial','fund_price_disagreement'),
 'participant_futures':('FII_index_futures_level','FII_index_futures_d5','FII_index_futures_d21','DII_index_futures_level',
     'Pro_index_futures_level','index_futures_detail_hhi_z','FII_stock_futures_d5'),
 'participant_options':('FII_index_calls_level','FII_index_puts_level','FII_index_calls_d5','FII_index_puts_d5','index_calls_disagree','index_puts_disagree'),
 'participant_volume':('fii_gross_volume_share','participant_volume_z','fii_stock_vol_share','pro_option_vol_share'),
 'delivery':('del_intensity','del_high_frac','del_rising_frac','del_dispersion','del_flow_concentration'),
 'large_transactions':('deal_n','deal_size','deal_premium','deal_rolling_balance','deal_cash_turnover_share'),
 'atm_iv':('iv_prev','vix_level','iv_gap'),
 'option_surface':('iv_skew','iv_term','surface_curve','surface_tail'),
 'realized_volatility':('normalized_cash_vol','rv_shock','overnight_rv21','rth_rv21','vol_ratio5_21'),
 'intraday_structure':('intraday_rv','jump_share_5','closing_share_5','firsthour_share_5','intraday_reversal_5'),
 'institutional_flows':('custody_equity','fortnightly_equity','mutual_equity','direct_cash_fii','direct_cash_dii'),
}

POSITION={
 'fii_level':('FII_index_futures_level',),
 'fii_changes':tuple('FII_index_futures_d'+str(i) for i in (1,3,5,10,21)),
 'dii_level':('DII_index_futures_level',),
 'pro_level':('Pro_index_futures_level',),
 'gross_exposure':('FII_index_futures_gross_share','DII_index_futures_gross_share','Pro_index_futures_gross_share'),
 'concentration':('index_futures_detail_hhi_z','index_futures_disagree','stock_futures_detail_hhi_z'),
 'trading_volume':GROUPS['participant_volume'],
 'stock_futures':('FII_stock_futures_level','FII_stock_futures_d5','DII_stock_futures_level','Pro_stock_futures_level'),
 'options':GROUPS['participant_options'],
 'persistence':('FII_index_futures_slow','FII_index_futures_accel','FII_index_futures_z','DII_index_futures_slow'),
 'new_innovations':('analogue_fii_shock','analogue_dii_shock','analogue_fii_rank'),
}
CORPORATE={
 'counts':('count2','count9','count31','earnings9','financial9','issuer_count9'),
 'semantics':('lexical_direction','positive_rate','negative_rate','uncertainty','text_dispersion','material_only'),
 'structured':GROUPS['structured_financials'],
 'calendar':('earnings_notice_count','financial_notice_count','earnings_issuer_count'),
 'price_reaction':('reaction_mean','reaction_peer','reaction_dispersion','fund_price_disagreement'),
 'weighting':('sector_balanced_fund','weighted_fund','financial_sign','sector_balanced_sign'),
}
CORE=PRICE+('domestic_rotation_finance','eq500_spread5','eq50_spread1','iv_prev','iv_term','stock_equal')
WEEKLY=CORE+('count2','count9','lexical_direction','fund_surprise','fund_financial','reaction_mean','earnings_notice_count')
MONTHLY=CORE+('FII_index_futures_d21','FII_index_futures_level','DII_index_futures_level','Pro_index_futures_level',
              'index_futures_detail_hhi_z','financial21','FII_index_futures_slow')
COMPLEMENT={
 'native_market':('domestic_rotation_finance','eq500_spread5','eq50_spread1','allEQ_advance'),
 'corporate':('count2','count9','lexical_direction','fund_surprise','fund_financial','reaction_mean'),
 'positioning':('FII_index_futures_d21','FII_index_futures_level','Pro_index_futures_level','index_futures_detail_hhi_z'),
 'delivery':('del_intensity','del_high_frac','del_rising_frac'),
 'volatility':('iv_prev','iv_term','normalized_cash_vol'),
}

def dedup(items):
    return tuple(dict.fromkeys(items))

def cash():
    z=csv('official-index-closes.csv',V11).rename(columns={'Unnamed: 0':'day'}).set_index('day').loc[FIRST:FREEZE]
    assert z.index.is_monotonic_increasing and len(z)==466 and z.nifty50.notna().all()
    return z

def observed():
    z=cash()
    c=np.log(z.nifty50.to_numpy())
    r=np.r_[np.nan,np.diff(c)]
    f=csv('original-target-panel.csv',V17).set_index('day')
    pos=z.index.get_indexer(f.index)
    assert (pos>0).all() and list(z.index[pos-1])==f.origin.tolist()
    d=f[['origin','cohort_5','cohort_21']].copy()
    d['reference_close']=z.nifty50.to_numpy()[pos-1]
    d['first_session']=list(z.index[pos])
    target=list(dict.fromkeys([(0,h) for h in LIFETIMES]+list(INCREMENTS)+list(COMPONENTS)+[(5,21)]))
    for a,b in target:
        good=pos+b-1<len(z)
        ids=pos[good]
        label=f'{a}_{b}'
        d.loc[good,'return_'+label]=c[ids+b-1]-c[ids+a-1]
        d.loc[good,'end_'+label]=z.index[ids+b-1]
        d.loc[good,'start_'+label]=z.index[ids+a]
        realized=np.sqrt(np.square(r[ids[:,None]+np.arange(a,b)]).mean(axis=1)*252)
        d.loc[good,'risk_'+label]=realized
    for h in (1,3,5,10,21):
        p=f[f'original{h}'].notna()
        np.testing.assert_allclose(d.loc[p,f'return_0_{h}'],f.loc[p,f'original{h}'],rtol=0,atol=2.e-10)
        assert (d.loc[p,f'end_0_{h}']==f.loc[p,f'end_original{h}']).all()
    for h in HORIZONS:
        g=d[d[f'cohort_{h}'].notna()]
        assert len(g)==EXPECTED[h]
    return d

def analogues(g):
    cols=('cash_ret','cash_momentum','normalized_cash_vol','front_basis','days_to_expiry','cash_breadth_change','roll_event')
    models={}
    for name,variable in [('fii','FII_index_futures_d1'),('dii','DII_index_futures_d1')]:
        a=g.reindex(columns=cols).assign(known_position=g[variable].shift()).to_numpy(float)
        y=g[variable].to_numpy(float)
        val=np.full(len(a),np.nan)
        rank=np.full(len(a),np.nan)
        for i in range(60,len(a)):
            before=np.flatnonzero(np.isfinite(y[:i]))[-150:]
            if len(before)<50 or not np.isfinite(y[i]):continue
            hist=a[before]
            m=np.nanmedian(hist,axis=0)
            m=np.nan_to_num(m)
            hist=np.where(np.isfinite(hist),hist,m)
            now_=np.where(np.isfinite(a[i]),a[i],m)
            s=np.maximum(hist.std(axis=0),1.e-6)
            dist=(np.clip((hist-now_)/s,-7,7)**2).mean(axis=1)
            nearest=before[np.argsort(dist,kind='stable')[:15]]
            anchor=np.median(y[nearest])
            val[i]=y[i]-anchor
            past_noise=val[max(0,i-100):i]
            if np.isfinite(past_noise).sum()>=30:
                valid=past_noise[np.isfinite(past_noise)]
                rank[i]=((valid<val[i]).sum()+.5)/(len(valid)+1)
        models[f'analogue_{name}_shock']=val
        models[f'analogue_{name}_rank']=rank
    return pd.DataFrame(models,index=g.index)

def activity(c):
    g=csv('positioning-daily-features.csv.gz',V19).set_index('day').reindex(c.index)
    extra={}
    for p in ('FII_index_futures','DII_index_futures'):
        v=g[p+'_level']
        for n in (3,10):extra[p+f'_d{n}']=v.diff(n)
        extra[p+'_slow']=v.rolling(21,min_periods=16).mean()
        hist=v.shift().rolling(63,min_periods=30)
        extra[p+'_z']=(v-hist.mean())/hist.std().replace(0,np.nan)
    d=csv('participants.csv.gz',V19,usecols=['day','kind','participant','instrument','gross_share'])
    for key,exposure,contract in [('fii_stock_vol_share','FII','stock_futures'),('pro_option_vol_share','Pro','index_calls')]:
        extra[key]=d[d.kind.eq('traded_volume')&d.participant.eq(exposure)&d.instrument.eq(contract)].set_index('day').gross_share
    rel=np.log(c.niftyfinancialservices/c.nifty50)
    extra['financial21']=rel.diff(21)
    extra['financial_lead_change']=rel.diff(5)-rel.diff(21)*5/21
    cols=[k for k in ('niftybank','niftyit','niftypharma','niftyauto','niftyfmcg','niftymetal','niftyenergy') if k in c]
    extra['same_day_sector_dispersion']=np.log(c[cols]).diff().std(axis=1)
    c21=g.cash_ret.rolling(21,min_periods=15).std()
    extra['vol_ratio5_21']=g.cash_ret.rolling(5,min_periods=4).std()/c21
    extra['rv_shock']=g.cash_ret.abs()/c21.shift()
    stock=csv('official-stock-breadth.csv',V17).set_index('day').reindex(c.index)
    intra=csv('daily-process-features.csv',V14).set_index('day').reindex(c.index)
    fields=('overnight_rv21','rth_rv21',*GROUPS['intraday_structure'])
    return pd.concat([g,pd.DataFrame(extra,index=g.index),analogues(g),stock,intra.reindex(columns=fields)],axis=1)

def release_series(p,series,window,days):
    if p.empty:return pd.Series(dtype=float)
    q=p.dropna(subset=[series]).sort_values('day').drop_duplicates('day',keep='last')
    due=(pd.to_datetime(q.day)+pd.to_timedelta(window,unit='D')).dt.strftime('%Y-%m-%d')
    row=days.searchsorted(due,side='left')
    inside=row<len(days)
    return pd.Series(q.loc[inside,series].to_numpy(float),index=days[row[inside]]).groupby(level=0).last()

def flows(d,days):
    fs=csv('cdsl-daily-observations.csv.gz',V19)
    fs=fs[fs.route.eq('Stock Exchange')]
    v=csv('cdsl-sector-observations.csv.gz',V19)
    v=v[v.sector.ne('Total')].groupby('day',as_index=False).net_equity_inr_crore.sum(min_count=1)
    m=csv('amfi-monthly-observations.csv.gz',V19).rename(columns={'period_end':'day'})
    m=m[m.category.eq('open_end_equity')]
    for name,q,k,lag,cap in [('custody_equity',fs,'net_inr_crore',1,3),('fortnightly_equity',v,'net_equity_inr_crore',10,12),
       ('mutual_equity',m,'net_inr_crore',20,20)]:
        v=release_series(q,k,lag,days).reindex(days)
        pos=pd.Series(np.arange(len(days)),index=days).where(v.notna()).ffill()
        age=pd.Series(np.arange(len(days)),index=days)-pos
        vals=v.ffill().where(age.le(cap))
        previous=d.decision.str[11:16].lt('08:15')
        assert not previous.any()
        d[name]=vals.reindex(d.decision.str[:10]).to_numpy()
        d[name+'_new_release']=v.reindex(d.decision.str[:10]).notna().to_numpy()
    return d

def make():
    c=cash()
    y=observed()
    before=csv('original-feature-panel.csv.gz',V17)
    before=before[before.cutoff.isin(CLOCKS)]
    corp=csv('event-aggregate-features.csv.gz',V18)
    sched=csv('event-schedule-exposures.csv.gz',V18)
    sched=sched[sched.horizon.eq(5)].drop(columns='horizon')
    p=csv('asof-positioning-features.csv.gz',V19,usecols=['day','cutoff','source_day','source_release'])
    d=before.merge(p,on=['day','cutoff'],validate='1:1')
    d=d.merge(corp.drop(columns=['origin']),on=['day','cutoff'],validate='1:1').merge(sched,on=['day','cutoff'],validate='1:1')
    assert d.source_release.le(d.decision).all()
    for k in ('last_announcement','last_known_report','last_known_reaction','last_notice'):
        v=d[k].notna()
        assert d.loc[v,k].le(d.loc[v,'decision_local']).all(),k
    z=activity(c)
    z=z.reindex(d.source_day)
    z.index=d.index
    d=d.join(z.drop(columns=z.columns.intersection(d.columns)))
    gift=csv('gift-decision-clock.csv',V17)
    gift=gift[gift.decision.str[11:16].isin(['17:00','08:55'])].copy()
    gift['cutoff']=gift.decision.str[11:16].map({'17:00':'previous_1700','08:55':'preauction_0855'})
    d=d.merge(gift[['day','cutoff','return_1530','last_night_relative_cash','latest_available']],on=['day','cutoff'],how='left',validate='1:1').copy()
    assert d.loc[d.latest_available.notna(),'latest_available'].le(d.loc[d.latest_available.notna(),'decision']).all()
    d['gift_cash_mark']=d.return_1530
    d['gift_night']=d.last_night_relative_cash
    d['iv_gap']=d.iv_prev-d.trailing_vol
    opt=csv('features-21.csv',V14,usecols=['day','option_day','iv_curvature','density_priced_down5']).set_index('day').reindex(d.origin)
    valid=opt.option_day.notna()
    assert (opt.index[valid]>opt.loc[valid,'option_day']).all()
    d['surface_curve']=opt.iv_curvature.to_numpy()
    d['surface_tail']=opt.density_priced_down5.to_numpy()
    d['surface_source_day']=opt.option_day.to_numpy()
    d=flows(d,c.index)
    d=d.sort_values(['cutoff','day']).reset_index(drop=True)
    write('asof-features.csv.gz',d)
    write('multi-horizon-targets.csv',y.reset_index())
    cov=[]
    for clock,g in d.groupby('cutoff'):
        for name,fields in GROUPS.items():
            for k in fields:cov.append(dict(cutoff=clock,family=name,feature=k,finite=int(g.reindex(columns=[k]).iloc[:,0].notna().sum()),
                                             snapshot_n=len(g)))
    write('feature-coverage.csv',pd.DataFrame(cov))
    save('feature-definitions.json',dict(groups=GROUPS,positioning=POSITION,corporate=CORPORATE,core=CORE,weekly=WEEKLY,monthly=MONTHLY,
         complementarity=COMPLEMENT,price_controls=PRICE,causal_analogue='15 nearest earlier standardized historical states drawn from up to 150 rows, minimum 50. Compare actual minus median of neighbors. Rank against earlier innovations.',
         publication='V19 modeled 08:15 next NSE session for EOD bodies. V18 filing clocks, V17 GIFT availability and V14 surface option days verified separately. CDSL/AMFI releases carry explicit conservative lags and remain sparse.',
         windows='Exact NSE cash close intervals with fully observed endpoint. Cumulative and component labels share a cash calendar.',
         flow_policy='Limited carry-forward from an assumed vintage. Confirmed custodian data and monthly subscriptions are separate from provisional exchange net cash. Sparse or unavailable features remain missing.'))
    print('V20 feature panel',len(d),'rows across',len(GROUPS),'source families',flush=True)

if __name__=='__main__':
    make()

