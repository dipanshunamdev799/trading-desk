"""Measure event responses and synchronized diffusion with dated inputs and matched controls."""
from collections import defaultdict
from .common import *

H=(1,3,5,10,21)
NATIVE={'bank':'bank','finance':'financial','it':'it','energy':'energy','auto':'auto','consumer':'defensive'}
FOCUS={'earnings','guidance','order_win','order_cancellation','acquisition','divestment','credit','debt','fundraising',
       'expansion','capex','regulatory','litigation','management','dividend','buyback','action','business_update'}

def load_market():
    seed=csv('issuer-seed.csv').stock.tolist()
    columns=['day','stock','isin','open','close','previous_close','turnover','volume']
    blocks=[csv('official-equity-daily.csv.gz',V17,usecols=columns),csv('supplementary-equity-cash.csv.gz')]
    raw=pd.concat([x[x.stock.isin(seed)].reindex(columns=columns) for x in blocks],ignore_index=True)
    e=raw[raw.day.between(FIRST,FREEZE)&raw.volume.gt(0)&raw.open.gt(0)&raw.close.gt(0)&raw.previous_close.gt(0)].copy()
    e=e.drop_duplicates(['day','stock'],keep=False).sort_values(['day','stock'])
    idx=csv('official-index-closes.csv',V11)
    idx=idx.set_index(idx.columns[0]).sort_index()
    idx=idx.loc[FIRST:FREEZE]
    days=pd.Index(sorted(set(e.day)&set(idx.index)),name='day')
    names=pd.Index(seed,name='stock')
    a={k:e.pivot(index='day',columns='stock',values=k).reindex(index=days,columns=names) for k in columns[2:]}
    full=np.log(a['close']/a['previous_close'])
    full=full.where(full.abs().le(np.log(1.35)))
    regular=np.log(a['close']/a['open']).where(full.notna())
    gap=(full-regular).where(regular.notna())
    m=np.log(idx.nifty50.reindex(days)).diff()
    liquid=a['turnover'].shift().rolling(20,min_periods=10).median()
    vol=full.shift().rolling(25,min_periods=13).std()
    beta=full.rolling(60,min_periods=35).cov(m).div(m.rolling(60,min_periods=35).var(),axis=0).clip(-1,3).shift()
    momentum=full.shift().rolling(5,min_periods=4).sum()
    company_issuance=a['isin'].ffill()
    known_trade=a['close'].notna().cumsum().shift().fillna(0)
    # Retain the actual official daily returns and native continuous open-to-close legs where available.
    tape={}
    for k in ['cash','broad',*NATIVE.values()]:
        d=csv('cash-panel/'+k+'.csv',V16)
        d=d.set_index(d.columns[0]).reindex(days)
        tape[k]=(np.log(d.close).diff().to_numpy(float),np.log(d.close/d.open).to_numpy(float))
    tape['cash']=(m.to_numpy(float),tape['cash'][1])
    return days,names,a,full,regular,gap,liquid,vol,beta,momentum,tape,company_issuance,known_trade

def first_open(eligible,days):
    stamp=pd.Timestamp(eligible)
    d=stamp.strftime('%Y-%m-%d')
    offset=days.searchsorted(d,side='left')
    if offset<len(days) and days[offset]==d and stamp.strftime('%H:%M:%S')>'09:15:00':
        offset+=1
    return offset

def targets(c2c,rth,days,length):
    if c2c.ndim==1:
        c2c=c2c[:,None]
        rth=rth[:,None]
    nxt=np.full_like(c2c,np.nan)
    if length==1:
        return rth.copy()
    for i in range(len(days)-length+1):
        nxt[i]=rth[i]+c2c[i+1:i+length].sum(axis=0)
    return nxt

def group_map(e):
    z=e[e.industry.fillna('').ne('')].sort_values('eligible').drop_duplicates('symbol')
    return z.set_index('symbol')[['sector','eligible']]

def event_bucket(e,days):
    t=pd.Timestamp(e.release); day=t.strftime('%Y-%m-%d')
    return e.publication_bucket if day in days else 'non_trading_day'

def market_releases(e,days,names,ids,known):
    h={}
    seeds=set(names)
    for r in e.itertuples(index=False):
        if r.family not in FOCUS and not r.material:continue
        i=int(first_open(r.eligible,days))
        if i<26 or i+1>=len(days) or r.symbol not in seeds:continue
        j=int(names.get_loc(r.symbol))
        p=i-1
        pre=pd.Timestamp(r.release).strftime('%Y-%m-%d')
        visible=int(days.searchsorted(pre,side='left'))-1
        if visible<0 or known.iat[p,j]<18:continue
        if isinstance(r.isin,str) and r.isin.strip() and ids.iat[visible,j]!=r.isin:
            continue
        h.setdefault((i,j),[]).append(r)
    ranks={'earnings':0,'guidance':1,'credit':2,'order_win':3,'order_cancellation':3,'regulatory':4,'acquisition':4,'management':5}
    schedules=[]
    for (i,j),g in h.items():
        r=min(g,key=lambda v:(ranks.get(v.family,7),v.eligible,v.record_id))
        schedules.append((i,j,r,len(g),event_bucket(r,days)))
    return sorted(schedules,key=lambda row:(row[0],row[1]))

def event_panel():
    e=csv('issuer-events.csv.gz'); f=csv('primary-fundamental-events.csv.gz')
    days,names,prices,close,rth,gap,liquid,vol,beta,momentum,tape,ids,known=load_market()
    dates=days.to_numpy();syms=names.to_numpy()
    by_name=group_map(e)
    sectors=by_name.sector.reindex(names).fillna('other').to_numpy()
    sector_time=by_name.eligible.reindex(names).fillna('9999').to_numpy(str)
    rows=market_releases(e,days,names,ids,known)
    state={}
    for r in f.sort_values('eligible').itertuples(index=False):state.setdefault(r.symbol,[]).append(r)
    occ=np.zeros((len(days),len(names)),dtype=bool)
    for i,j,_,_,_ in rows: occ[i,j]=True
    use=[x.to_numpy(float) for x in (close,rth,gap,vol,beta,momentum,liquid)]
    c,o,g,v,b,m,l=use
    stock_y={h:targets(c,o,days,h) for h in H}
    tape_y={k:{h:targets(*series,days,h)[:,0] for h in H} for k,series in tape.items()}
    out=[]
    for i,j,r,num,bucket in rows:
        for kind in (0,1):
            t=i+kind
            cut=f'{dates[t]} 09:15:00'
            h1_features=(g[i,j],o[i,j],c[i,j]) if kind else (np.nan,np.nan,np.nan)
            prev_allowed=(sector_time<=cut)
            eligible_peers=prev_allowed&(sectors==sectors[j])&(np.arange(len(names))!=j)
            if not prev_allowed[j]:eligible_peers[:]=False
            control=eligible_peers&~occ[max(0,t-4):t+1].any(axis=0)&np.isfinite(v[t])&np.isfinite(m[t])&np.isfinite(l[t])
            # Pair on the same known sector/date and pre-event volatility, momentum and market activity.
            sim_idx=np.flatnonzero(control)
            if len(sim_idx) and np.isfinite([v[t,j],m[t,j],l[t,j]]).all():
                vol0=np.log(np.maximum(v[t,sim_idx],.003)/max(v[t,j],.003))
                mom0=(m[t,sim_idx]-m[t,j])/.04
                liq0=np.log(np.maximum(l[t,sim_idx],1)/max(l[t,j],1))*.33
                dist=np.square(vol0)+np.square(mom0)+np.square(liq0)
                peers=sim_idx[np.argsort(dist)[:4]]
            else:
                peers=np.array([],dtype=int)
            n_known=int(eligible_peers.sum())
            if not np.isfinite(v[t,j]) or not np.isfinite(m[t,j]):continue
            reported=[u for u in state.get(r.symbol,()) if u.eligible<=cut and (pd.Timestamp(cut)-pd.Timestamp(u.eligible)).days<=12]
            latest=reported[-1] if reported and r.family in ('earnings','guidance','presentation') else None
            surprise=latest.statistical_surprise if latest else np.nan
            chem=surprise if pd.notna(surprise) else float(r.text_sign)
            ypeer=o[i,eligible_peers];sr=float(np.mean(ypeer[np.isfinite(ypeer)])) if np.isfinite(ypeer).any() and kind else np.nan
            z=dict(day=dates[t],first_eligible_day=dates[i],decision=cut,stage='after_reaction' if kind else 'first_open',
                   episode=r.episode_id,symbol=r.symbol,family=r.family,n_release_cluster=num,sector=sectors[j] if prev_allowed[j] else 'other',
                   source_eligible=r.eligible,publication=r.release,publication_bucket=bucket,primary_text_sign=r.text_sign,
                   alternative_sign=r.category_direction_proxy,published_fundamental_surprise=surprise,
                   earnings_growth=latest.profit_qoq if latest else np.nan,reported_fundamental_available=latest.eligible if latest else None,
                   reaction_gap=h1_features[0],reaction_regular=h1_features[1],reaction_close=h1_features[2],peer_reaction=sr,
                   prior_vol=v[t,j],prior_momentum=m[t,j],prior_beta=b[t,j],prior_liquidity=np.log(max(1,l[t,j])),
                   matched_count=len(peers),peer_count=n_known,matched_names='|'.join(syms[peers]),
                   disagreement=chem*h1_features[1] if kind else np.nan,explicit_uncertainty=r.explicit_uncertainty)
            if kind:z['age_days']=(pd.Timestamp(cut)-pd.Timestamp(r.eligible)).days
            for h in H:
                if t+h>len(days):continue
                value=stock_y[h][t,j]
                if not np.isfinite(value):continue
                raw_match=stock_y[h][t,peers]
                matched=float(raw_match[np.isfinite(raw_match)].mean()) if np.isfinite(raw_match).any() else np.nan
                avg=stock_y[h][t,eligible_peers]
                peer=float(avg[np.isfinite(avg)].mean()) if np.isfinite(avg).sum()>=3 else np.nan
                nt=NATIVE.get(sectors[j]) if prev_allowed[j] else None
                market=tape_y['cash'][h][t]
                native=tape_y[nt][h][t] if nt else np.nan
                broad=tape_y['broad'][h][t]
                beta0=b[t,j] if np.isfinite(b[t,j]) else 1.
                out.append(z|dict(horizon=h,target_end=dates[t+h-1],stock_return=value,nifty_return=market,related_peer=peer,
                                 sector_return=native,broad_return=broad,relative_market=value-market,
                                 relative_sector=value-native,beta_residual=value-beta0*market,vol_adjusted=(value-beta0*market)/(v[t,j]*np.sqrt(h)),
                                 matched_non_event_return=matched,matched_abnormal=value-matched,peer_excess=peer-market,
                                 sector_excess=native-market,broad_excess=broad-market))
    allrows=pd.DataFrame(out)
    assert allrows.source_eligible.le(allrows.decision).all()
    valid=allrows.reported_fundamental_available.notna()
    assert allrows.loc[valid,'reported_fundamental_available'].le(allrows.loc[valid,'decision']).all()
    write('stock-event-pairs.csv.gz',allrows)
    receipt=dict(issuer_sessions=len(rows),skipped_without_prior_stock_state=len(rows)-allrows.episode.nunique(),
                 score_rows=len(allrows),distinct_issuers=int(allrows.symbol.nunique()),distinct_dates=int(allrows.day.nunique()),
                 priced_cash_days=len(days),first_open='First full cash-market open on or after eligible time. Known same-day releases during trading are studied separately with intraday bars.',
                 reaction_clock='Next full-session open, after the first scored daily reaction is complete and observable. Market and native comparisons have matched potential session opening anchors.',
                 controls='Match to up to four earlier-observable, historically active sector peers on the same date and pre-event volatility, five-session momentum and turnover. Exclude issuers with a known event in the recent past, without screening on future events or future outcomes.')
    save('event-panel-receipt.json',receipt)
    print('Stock event panel',len(rows),'issuer sessions,',len(allrows),'forecast-target rows',flush=True)
    return allrows

def interval_stats(g,key):
    a=g[['symbol','day','episode',key]].dropna()
    n=len(a)
    if n==0:return None
    y=a[key].to_numpy(float)
    y0=y.mean();e=a.assign(_res=y-y0)
    v=0.
    for cols,sgn in [(['day'],1),(['symbol'],1),(['day','symbol'],-1)]:
        groups=e.groupby(cols)._res.sum().to_numpy()
        if len(groups)>1:v+=sgn*(groups@groups)*len(groups)/(len(groups)-1)/n**2
    s=np.sqrt(max(v,0))
    return dict(n=n,different_dates=int(a.day.nunique()),issuers=int(a.symbol.nunique()),episodes=int(a.episode.nunique()),
                mean=y0,median=float(np.median(y)),positive=float(np.mean(y>0)),low=y0-1.96*s,high=y0+1.96*s,
                metric=key,two_way_cluster_sd=s)

def event_statistics(x):
    out=[];network=[];reprice=[]
    metrics=('stock_return','relative_market','relative_sector','beta_residual','vol_adjusted','matched_abnormal')
    for (stage,bucket,fam,h),g in x.groupby(['stage','publication_bucket','family','horizon']):
        if len(g)<12:continue
        for k in metrics:
            s=interval_stats(g,k)
            if s:out.append(dict(stage=stage,timing=bucket,family=fam,horizon=h,**s))
    for (stage,sector0,h),g in x.groupby(['stage','sector','horizon']):
        if len(g)<30:continue
        kinds={'all':g,'earnings':g[g.family.eq('earnings')],'credit':g[g.family.eq('credit')],
               'guidance':g[g.family.eq('guidance')],'orders':g[g.family.isin(['order_win','order_cancellation'])]}
        for track,u in kinds.items():
            if len(u)<10:continue
            for k in ('relative_market','matched_abnormal','peer_excess','sector_excess','broad_excess','nifty_return'):
                s=interval_stats(u,k)
                if s:network.append(dict(stage=stage,sector=sector0,event_family=track,horizon=h,**s))
    priced=x[x.stage.eq('after_reaction')].copy()
    story=priced.published_fundamental_surprise.fillna(priced.primary_text_sign).clip(-2,2)
    priced['signal_source']=np.where(priced.published_fundamental_surprise.notna(),'structured','exchange_text')
    priced['interpretation']=np.where(story.gt(0),'positive business',np.where(story.lt(0),'negative business','unclassified'))
    priced['reaction']=np.where(priced.reaction_regular.gt(.003),'stock rose',np.where(priced.reaction_regular.lt(-.003),'stock fell','muted price'))
    priced['peer_confirmation']=np.where(np.sign(story)==np.sign(priced.peer_reaction),'peer confirms','mixed or unavailable')
    for (s,d,p,h),g in priced.groupby(['signal_source','interpretation','reaction','horizon']):
        if d=='unclassified' or len(g)<12:continue
        for k in ('stock_return','matched_abnormal','peer_excess','nifty_return'):
            a=interval_stats(g,k)
            if a:reprice.append(dict(signal_source=s,business=d,price_reaction=p,horizon=h,**a))
    write('corporate-event-study.csv',pd.DataFrame(out))
    write('domestic-diffusion-study.csv',pd.DataFrame(network))
    write('announcement-repricing-cohorts.csv',pd.DataFrame(reprice))

def intraday():
    from research.nifty_forecast_v17 import stocks
    from research.nifty_forecast_v15.sessions import candles
    ev=csv('issuer-events.csv.gz')
    basket=csv('historical-stock-basket.csv',V17)
    ev=ev[ev.material.eq(1)&ev.symbol.isin(basket.stock)&ev.publication_bucket.eq('during_session')]
    n,_,_=candles((V13/'sources/upstox').glob('nifty-5m-*'),5)
    by={}
    # The inherited loader verifies every hash and prefers the finest complete interval.
    inv=stocks.bar_inventory()
    official=csv('official-equity-daily.csv.gz',V17,usecols=['day','stock','isin'])
    official=official[official.stock.isin(basket.stock)].drop_duplicates(['day','stock'])
    for symbol,t in official.groupby('stock'):
        h=stocks.read_bars(inv[symbol],t.set_index('day')['isin'])
        if h.empty:continue
        h=h[h.resolution.eq(5)].copy()
        h['end']=h.ts+pd.Timedelta(minutes=5)
        by[symbol]={d:q.set_index('ts').sort_index() for d,q in h.groupby('day')}
    sm=basket.set_index('stock').sector
    rows=[]
    for r in ev.itertuples(index=False):
        dt=pd.Timestamp(r.eligible,tz=IST)
        day=dt.strftime('%Y-%m-%d')
        x=by.get(r.symbol,{}).get(day);cash=n.get(day)
        if x is None or cash is None:continue
        t=dt.ceil('5min')
        if t not in x.index or t not in cash.index:continue
        for mins in (5,30,0):
            end=t+pd.Timedelta(minutes=mins) if mins else stamp(day,'15:30')
            if end>stamp(day,'15:30'):continue
            def ret(q):
                g=q[(q.index>=t)&(q.end<=end)]
                return float(np.log(g.close.iloc[-1]/g.open.iloc[0])) if len(g)==round((end-t).total_seconds()/300) and len(g)>0 else np.nan
            actual=ret(x);market=ret(cash)
            if not np.isfinite([actual,market]).all():continue
            peer=[ret(by[s].get(day)) for s in sm.index[sm.eq(sm.at[r.symbol])] if s!=r.symbol and s in by and day in by[s]]
            past=x[x.end.le(dt-pd.Timedelta(minutes=BAR_DELAY))]
            immediate=(np.log(past.close.iloc[-1]/x.open.iloc[0]) if len(past) else np.nan)
            rows.append(dict(day=day,symbol=r.symbol,episode=r.episode_id,family=r.family,available=r.eligible,
                 decision=t.isoformat(),end=end.isoformat(),minutes=mins,stock_return=actual,nifty_return=market,
                 excess=actual-market,peer_return=np.nanmean(peer) if np.isfinite(peer).any() else np.nan,observed_prefix=immediate))
    g=pd.DataFrame(rows)
    write('intraday-event-responses.csv.gz',g)
    out=[]
    if len(g):
        for (m,s),u in g.groupby(['minutes','family']):
            if len(u)<12:continue
            for k in ('excess','stock_return','peer_return','nifty_return'):
                a=interval_stats(u,k)
                if a:out.append(dict(minutes=m,family=s,**a))
    write('intraday-event-summary.csv',pd.DataFrame(out))
    print('Aligned intraday responses',len(g),'rows',flush=True)

if __name__=='__main__':
    import sys
    if 'intraday' in sys.argv:
        intraday()
    else:
        event_statistics(event_panel())
