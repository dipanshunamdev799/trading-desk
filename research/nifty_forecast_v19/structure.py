"""Separate stock, sector, transaction and crowding tests with dated controls."""
from scipy.stats import spearmanr
from .common import *
from .acquire import sessions
from .features import FUTURES,LEVEL,CROWD,CHANGES,INNOV
from .forecast import matrix,matured
from research.nifty_forecast_v16.model import fit

STOCK_PRICE=('log_return','return5','volatility25','lvol_z','lturn_z','lturn','trailing_abs')
STOCK_DELIVERY=('pct_z','lqty_z','persistence','pct_rising','signed_delivery','liquid_interaction')

def rank_corr(x,y):
    a=np.asarray(x,float);b=np.asarray(y,float)
    valid=np.isfinite(a)&np.isfinite(b)
    return float(spearmanr(a[valid],b[valid]).statistic) if valid.sum()>=6 and np.std(a[valid])>1.e-12 and np.std(b[valid])>1.e-12 else np.nan

def get_close(days):
    return csv('official-index-closes.csv',V11).set_index('Unnamed: 0').reindex(days)

def add_targets(s,days,close):
    # A complete date-by-issuer matrix prevents a missing cash session from shortening a horizon.
    panel=s.pivot(index='day',columns='issuer_id',values='log_return').reindex(days)
    n=np.log(close.nifty50)
    i=days.get_indexer(s.day)
    j=panel.columns.get_indexer(s.issuer_id)
    for h in HORIZONS:
        out=panel.rolling(h,min_periods=h).sum().shift(-h).to_numpy()
        m=(n.shift(-h)-n).to_numpy()
        s[f'target{h}']=out[i,j]-m[i]
        s[f'raw{h}']=out[i,j]
        s[f'end{h}']=pd.Series(days,index=days).shift(-h).reindex(s.day).to_numpy()
        s[f'market{h}']=m[i]
        s[f'abs{h}']=abs(s[f'target{h}'])
    return s

def fit_on_days(a,days,settings,targets,endcols,penalty):
    output=[]
    fs=[]
    ds=a.day.to_numpy()
    dates=np.unique(ds)
    rec=a.reset_index(drop=True)
    xs={name:matrix(rec,fields) for name,fields in settings.items()}
    for tar,endcol in zip(targets,endcols):
        y=rec[tar].to_numpy(float)
        ends=rec[endcol].fillna('9999-12-31').to_numpy()
        for i,d in enumerate(dates):
            if i<70:continue
            pos=np.flatnonzero((ds==d)&np.isfinite(y))
            if len(pos)<6:continue
            start=dates[max(0,i-85)]
            train=np.flatnonzero((ds>=start)&(ends<d)&(ds<d)&np.isfinite(y))
            if len(np.unique(ds[train]))<30:continue
            for arm,x in xs.items():
                live=np.isfinite(x[pos]).sum(axis=1)>=3
                if arm in ('price_volume_delivery','sector_plus_delivery'):
                    live&=np.isfinite(x[pos,-1])
                eligible=pos[live]
                if not len(eligible):
                    continue
                m=fit(x[train],y[train],penalty)
                pred=.70*m.values(x[eligible])+.30*np.median(y[train])
                z=rec.iloc[eligible][['day','unit',endcol]].rename(columns={endcol:'target_end'}).copy()
                z=z.assign(model=arm,target=tar,prediction=pred,actual=y[eligible],abs_error=abs(pred-y[eligible]),
                           sq_error=(pred-y[eligible])**2,latested=max(ends[train]),train_dates=len(np.unique(ds[train])))
                output.append(z)
                fs.append(dict(observation=d,target=tar,model=arm,last_mature=max(ends[train]),training_rows=len(train),
                               training_days=len(np.unique(ds[train])),**m.receipt(list(settings[arm]))))
    return pd.concat(output,ignore_index=True),fs

def daily_metrics(book):
    values=[]
    for (day,target,model),g in book.groupby(['day','target','model']):
        values.append(dict(day=day,target=target,model=model,n=len(g),rank_correlation=rank_corr(g.prediction,g.actual),
                              mae=g.abs_error.mean(),rmse=np.sqrt(g.sq_error.mean())))
    return pd.DataFrame(values)

def delivery_background(x):
    r=x.log_return
    p=x.pct_z
    vol=x.volatility25
    state=np.select([r.gt(0)&p.ge(1),r.gt(0)&p.le(-1),r.lt(0)&p.ge(1),r.lt(0)&p.le(-1),
                     p.ge(1)&r.abs().le(.5*x.trailing_abs),p.ge(1)&vol.gt(vol.groupby(x.day).transform('median'))],
                    ['up_high','up_low','down_high','down_low','consolidation_high','volatile_high'],default='middle')
    # Consolidation and volatile-day buckets can overlap directional buckets and are therefore tested independently.
    x=x.assign(state=state)
    a=[]
    for tag,m in [('up_high',state=='up_high'),('up_low',state=='up_low'),('down_high',state=='down_high'),('down_low',state=='down_low'),
       ('consolidation_high',p.ge(1)&r.abs().le(.5*x.trailing_abs)),('volatile_high',p.ge(1)&vol.gt(vol.groupby(x.day).transform('median'))),
       ('ordinary_participation',p.between(-1,1))]:
        for h in HORIZONS:
            c=x.loc[m,['day',f'target{h}',f'abs{h}']].dropna()
            g=c.groupby('day').mean()
            a.append(dict(horizon=h,state=tag,stock_dates=len(c),dates=len(g),mean_market_relative=g[f'target{h}'].mean(),
                          mean_absolute_relative=g[f'abs{h}'].mean()))
    return pd.DataFrame(a)

def stock_and_sector(days,close):
    s=csv('stock-delivery-features.csv.gz')
    x=add_targets(s,days,close)
    x=x[x.day.gt('2025-01-29')&x.pct_z.notna()].copy()
    x['unit']=x.issuer_id
    x['signed_delivery']=np.sign(x.log_return)*x.pct_z
    x['liquid_interaction']=x.pct_z*np.clip(x.lturn_z,-4,4)
    r={'price_volume':STOCK_PRICE,'delivery_only':STOCK_DELIVERY,'price_volume_delivery':STOCK_PRICE+STOCK_DELIVERY}
    p,receipts=fit_on_days(x,days,r,[f'target{h}' for h in HORIZONS],[f'end{h}' for h in HORIZONS],240)
    write('stock-transfer-cases.csv.gz',p)
    keys=['day','unit','target']
    paired=p.groupby(keys).model.transform('nunique').eq(len(r))
    write('stock-transfer-daily.csv',daily_metrics(p[paired]))
    write('stock-delivery-states.csv',delivery_background(x))
    sec=csv('sector-delivery-features.csv.gz').rename(columns={'sector':'unit'})
    pr=csv('positioning-daily-features.csv.gz').set_index('day')
    sec=sec.join(pr[["FII_index_futures_d5","FII_stock_futures_d5","innovation_5","cash_breadth_change"]],on='day')
    i=days.get_indexer(sec.day); j=close.columns.get_indexer(sec.sector_index)
    index=np.log(close)
    rel=index.subtract(index.nifty50,axis='index')
    for h in HORIZONS:
        a=(rel.shift(-h)-rel).to_numpy()
        sec[f'target{h}']=a[i,j]
        sec[f'end{h}']=pd.Series(days,index=days).shift(-h).to_numpy()[i]
    sec['official_sector_momentum']=rel.diff(5).to_numpy()[i,j]
    sec['official_sector_day']=rel.diff().to_numpy()[i,j]
    ctrl=('price','turnover','volume','cash_breadth_change','official_sector_momentum','official_sector_day')
    sd=('delivery','delivery_high','delivery_signed','liquid_delivery')
    extra=('FII_index_futures_d5','FII_stock_futures_d5','innovation_5')
    blocks={'sector_price_turnover':ctrl,'sector_plus_delivery':ctrl+sd,'sector_plus_positions':ctrl+extra,'sector_all':ctrl+sd+extra}
    f,fitrows=fit_on_days(sec,days,blocks,[f'target{h}' for h in HORIZONS],[f'end{h}' for h in HORIZONS],160)
    write('sector-transfer-cases.csv.gz',f)
    live=f.groupby(keys).model.transform('nunique').eq(len(blocks))
    write('sector-transfer-daily.csv',daily_metrics(f[live]))
    with gzip.open(OUT/'transfer-fit-receipts.ndjson.gz','wt',encoding='utf8') as b:
        for z in receipts+fitrows:b.write(json.dumps(z,allow_nan=False,default=str)+'\n')
    return x

def transactions(x):
    d=csv('deal-audited.csv.gz')
    d['amount_before']=d.groupby('day').matched_block_once_proxy.transform('sum').groupby(d.day).transform('first')
    d['already_seen']=d.groupby(['stock','category']).cumcount().gt(0)
    ds=x.set_index(['day','stock'])
    events=set(zip(d.day,d.stock))
    business=x.groupby('day')
    output=[]
    for q in d.groupby(['day','stock','category'],as_index=False).agg(amount=('matched_block_once_proxy','sum'),
        naive=('reported_consideration','sum'),legs=('legs','sum'),pairs=('same_size_price_pairs','sum'),
        signed=('signed_reported_leg','sum'),premium=('premium_to_previous_close','median'),recurrence=('already_seen','max')).itertuples(index=False):
        if (q.day,q.stock) not in ds.index:
            continue
        origin=ds.loc[q.day,q.stock]
        pool=business.get_group(q.day)
        pool=pool[~pool.stock.map(lambda t:(q.day,t) in events)]
        same=pool[pool.sector.eq(origin.sector)&pool.sector.ne('other')]
        if len(same)<6:continue
        eligible=same[same.lturn.ge(same.lturn.quantile(.60))].copy()
        if len(eligible)<3:continue
        eligible['distance']=abs(eligible.lturn-origin.lturn)+1.3*abs(eligible.lturn_z-origin.lturn_z)+40*abs(eligible.log_return-origin.log_return)
        peer=eligible.dropna(subset=['distance']).sort_values(['distance','stock']).head(3)
        if len(peer)!=3:continue
        for h in HORIZONS:
            label=origin[f'target{h}']
            prices=peer[f'target{h}']
            if pd.isna(label) or prices.isna().any():continue
            ret=label-prices.mean()
            risk=abs(label)-prices.abs().mean()
            output.append(dict(day=q.day,eligible_at=origin.eligible_at,stock=q.stock,sector=origin.sector,
                target_end=origin[f'end{h}'],horizon=h,category=q.category,match_stocks=','.join(peer.stock),amount=q.amount,
                all_legs_amount=q.naive,both_sides=q.pairs,reported_net_legs=q.signed,legs=q.legs,premium=q.premium,recurrence=q.recurrence,
                amount_over_turnover=q.amount/origin.turnover,return_relative_to_controls=ret,absolute_relative_to_controls=risk))
    z=pd.DataFrame(output)
    results=[]
    for (h,k),g in z.groupby(['horizon','category']):
        benchmark=g.groupby('day').amount.max().shift().expanding(min_periods=12).quantile(.90)
        g=g.join(benchmark.rename('lag_large_threshold'),on='day')
        for label,sub in [('all',g),('no_large',g[g.amount.le(g.lag_large_threshold)]),('recurrent',g[g.recurrence]),
                          ('premium',g[g.premium.gt(0)]),('discount',g[g.premium.lt(0)])]:
            v=sub.groupby('day')[['return_relative_to_controls','absolute_relative_to_controls']].mean()
            results.append(dict(horizon=h,category=k,subset=label,events=len(sub),dates=len(v),
                excess_return=v.return_relative_to_controls.mean(),absolute_excess=v.absolute_relative_to_controls.mean(),
                signed_premium_rank=rank_corr(sub.premium,sub.return_relative_to_controls)))
    write('transaction-matched-cases.csv.gz',z)
    write('transaction-event-summary.csv',pd.DataFrame(results))

def crowding(days,index):
    x=csv('positioning-daily-features.csv.gz').set_index('day').reindex(days)
    x['prior_vol']=x.cash_ret.rolling(21,min_periods=15).apply(lambda s:np.sqrt(np.square(s).mean()*252),raw=True)
    x['crowd_flag']=x.index_futures_detail_hhi_z.ge(1.).where(x.index_futures_detail_hhi_z.notna())
    x['leader_flag']=x.cash_breadth_change.lt(0).where(x.cash_breadth_change.notna())
    groups={'all':np.ones(len(x),bool),'crowded':x.crowd_flag.eq(True),'ordinary':x.crowd_flag.eq(False),
            'crowded_weak_breadth':x.crowd_flag.eq(True)&x.leader_flag.eq(True),'cohort_2025':days.str.startswith('2025'),
            'cohort_2026':days.str.startswith('2026')}
    baseline=('cash_ret','cash_momentum','prior_vol','cash_breadth_change','state_iv',*FUTURES)
    feats={'price_iv_oi':baseline,'position_levels':baseline+LEVEL,'position_changes':baseline+CHANGES,
       'position_innovations':baseline+INNOV,'position_crowding':baseline+CROWD,'position_crowding_delay5':baseline+tuple()}
    x0={k:matrix(x,fields) for k,fields in feats.items()}
    x0['position_crowding_delay5']=matrix(x.join(x[list(CROWD)].shift(5).add_suffix('_lag5')),baseline+tuple(k+'_lag5' for k in CROWD))
    cases=[];stat=[]
    for h in HORIZONS:
        r=np.log(index.nifty50).shift(-h)-np.log(index.nifty50)
        rv=pd.Series(np.sqrt(x.cash_ret.pow(2).rolling(h,min_periods=h).mean().shift(-h)*252),index=days)
        future=np.log(x.ordinary_oi.shift(-h)/x.ordinary_oi)
        expiry=x.days_to_expiry.gt(3)&x.roll_event.eq(0)
        outcome={'reversal':(np.sign(x.cash_momentum)*r<0).astype(float).where(r.notna()&x.cash_momentum.notna()),
                 'expansion':rv.ge(1.25*x.prior_vol).astype(float).where(rv.notna()&x.prior_vol.notna()),
                 'oi_reduction':future.le(np.log(.92)).astype(float).where(future.notna()),
                 'realized_vol':rv}
        en=pd.Series(days,index=days).shift(-h).fillna('9999-12-31').to_numpy()
        observed=days.to_numpy()
        for name,t in outcome.items():
            y=t.to_numpy(float)
            for i in np.flatnonzero(np.isfinite(y)):
                tr=matured(observed,en,y,i,n=120)
                if len(tr)<60:continue
                for model,a in x0.items():
                    mdl=fit(a[tr],y[tr],180)
                    p=.68*mdl.values(a[i])+.32*np.mean(y[tr])
                    if name!='realized_vol':p=np.clip(p,.02,.98)
                    cases.append(dict(horizon=h,day=observed[i],target_end=en[i],outcome=name,model=model,actual=y[i],pred=p,
                                      score=(p-y[i])**2,expire_filter=int(expiry.iloc[i]),training_end=max(en[tr])))
            for group,v in groups.items():
                for q in (False,True):
                    keep=v&expiry if q else v
                    value=t[keep].dropna()
                    stat.append(dict(horizon=h,group=group,outcome=name,ex_expiry=q,count=len(value),rate_or_mean=value.mean(),
                          concentration_rank=rank_corr(x.loc[value.index,'index_futures_detail_hhi_z'],value)))
    write('crowding-conditional-states.csv',pd.DataFrame(stat))
    write('crowding-case-tests.csv.gz',pd.DataFrame(cases))

if __name__=='__main__':
    days=sessions()
    close=get_close(days)
    x=stock_and_sector(days,close)
    transactions(x)
    crowding(days,close)

