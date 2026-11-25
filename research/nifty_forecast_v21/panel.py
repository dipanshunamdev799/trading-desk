"""Create point-in-time stock, sector and market modeling tensors."""
from .common import *
from .universe import SECTOR_NAMES

TECH=('ret1','ret5','ret21','relative5','relative21','vol21','turnover_shock','range_5','beta','sector_beta','sector_lead')
STRUCT=('shared_breadth','shared_finance','shared_iv','shared_risk','cross_dispersion')
COUNTS=('announcement_count','material_count')
CONTENT=('announcement_sign','fundamental_surprise')
REACTION=('event_reaction',)
ACTIVITY=('delivery_rank','deal_intensity')
MARKET=('prior5','prior21','trailvol','advance','dispersion','market_sync','proxy_heavy_gap','cross_downside',
        'shared_breadth','shared_finance','shared_iv','shared_risk','position_level','position_change21','position_concentration')
V20_FIELDS={'shared_breadth':'eq500_spread5','shared_finance':'domestic_rotation_finance','shared_iv':'iv_prev','shared_risk':'vix_move',
            'position_level':'FII_index_futures_level','position_change21':'FII_index_futures_d21','position_concentration':'index_futures_detail_hhi_z'}
GROUPS={'technical':TECH,'market_structure':STRUCT,'corporate_counts':COUNTS,'corporate_content':CONTENT,
        'known_event_reaction':REACTION,'stock_participation':ACTIVITY}


def roll(x,n,min_count=None):
    return pd.DataFrame(x).rolling(n,min_periods=min_count or n).sum().to_numpy(float)


def prev(x):
    return np.concatenate([np.full((1,*x.shape[1:]),np.nan),x[:-1]],axis=0)


def future(x,h):
    out=roll(x,h)
    return np.concatenate([out[h-1:],np.full((h-1,*x.shape[1:]),np.nan)],axis=0)


def used_time(ts):
    v=pd.to_datetime(ts,format='mixed',utc=True,errors='coerce')
    return v.dt.as_unit('ns').astype('int64').to_numpy()


def event_tensor(days,names):
    cols=['symbol','episode_id','eligible','material','text_sign','family']
    e=csv('issuer-events.csv.gz',V18,usecols=cols)
    e=e[e.symbol.isin(names)].drop_duplicates('episode_id',keep='first')
    f=csv('primary-fundamental-events.csv.gz',V18,usecols=['symbol','eligible','statistical_surprise'])
    f=f[f.symbol.isin(names)&f.statistical_surprise.notna()]
    p=csv('stock-event-pairs.csv.gz',V18,usecols=['symbol','episode','horizon','stage','decision','reaction_close','peer_reaction'])
    p=p[p.symbol.isin(names)&p.stage.eq('after_reaction')&p.horizon.eq(1)].drop_duplicates('episode')
    p['reaction']=p.reaction_close-p.peer_reaction.fillna(0.)
    deliv=csv('stock-delivery-features.csv.gz',V19,usecols=['stock','day','eligible_at','pct_z','turnover_inr'])
    deliv=deliv[deliv.stock.isin(names)].rename(columns={'stock':'symbol'}).sort_values('turnover_inr',ascending=False).drop_duplicates(['symbol','day'])
    z=csv('bulk-block-events.csv.gz',V18,usecols=['day','BD_SYMBOL','BD_QTY_TRD','BD_TP_WATP'])
    z=z[z.BD_SYMBOL.isin(names)].rename(columns={'BD_SYMBOL':'symbol'}).copy()
    z['cash_value']=z.BD_QTY_TRD*z.BD_TP_WATP
    z=z.groupby(['day','symbol'],as_index=False).cash_value.max()
    k=days.searchsorted(z.day,side='right')
    ok=k<len(days)
    z=z.loc[ok].copy()
    z['eligible']=days[k[ok]]+'T08:15:00+05:30'
    z['log_deal']=np.log1p(z.cash_value/1.e6)
    guard=pd.to_datetime(days+'T08:55:00+05:30',utc=True).as_unit('ns').astype('int64').to_numpy()
    specs={'announcement_count':(e,'eligible',None,5,False),'material_count':(e,'eligible','material',5,False),
           'announcement_sign':(e,'eligible','text_sign',5,True),'fundamental_surprise':(f,'eligible','statistical_surprise',9,True),
           'event_reaction':(p,'decision','reaction',5,True),'delivery_rank':(deliv,'eligible_at','pct_z',1,True),
           'deal_intensity':(z,'eligible','log_deal',5,False)}
    out={};audit=[]
    start=pd.Timestamp(FIRST,tz=IST).value
    for feature,(a,date,value,win,average) in specs.items():
        t=used_time(a[date]);i=np.searchsorted(guard,t,side='left')
        j=names.get_indexer(a.symbol)
        v=np.ones(len(a)) if value is None else pd.to_numeric(a[value],errors='coerce').to_numpy(float)
        ok=(t>=start)&(i<len(guard))&(j>=0)&np.isfinite(v)
        assert (t[ok]<=guard[i[ok]]).all()
        matrix=np.zeros((len(days),len(names)));counts=np.zeros_like(matrix)
        np.add.at(matrix,(i[ok],j[ok]),v[ok]);np.add.at(counts,(i[ok],j[ok]),1)
        if win>1:
            matrix=roll(matrix,win,1);counts=roll(counts,win,1)
        out[feature]=np.divide(matrix,counts,out=np.full_like(matrix,np.nan),where=counts>0) if average else matrix
        accepted=a.loc[ok,['symbol',date]].copy().rename(columns={date:'first_eligible_timestamp'})
        accepted['decision_day']=days[i[ok]]
        accepted['feature']=feature
        audit.append(accepted)
    write('component-event-clock-audit.csv.gz',pd.concat(audit,ignore_index=True))
    return out


def exposures(r,m,sector_r,groups):
    n,d=r.shape
    beta=np.full((n,d),np.nan);gamma=np.full((n,d),np.nan)
    ver=[]
    for i in range(40,n):
        p=slice(max(0,i-100),i)
        a=r[p];b=m[p,None]
        ok=np.isfinite(a)&np.isfinite(b)
        k=ok.sum(axis=0)
        avg=lambda v:np.sum(np.where(ok,v,0.),axis=0)/np.maximum(k,1)
        v=avg(b*b)-avg(b)**2
        market=np.clip((avg(a*b)-avg(a)*avg(b))/(v+.000014)*.88+.12,.05,2.7)
        market[k<35]=np.nan
        beta[i]=market
        rel=sector_r[p][:,groups[i]]-b
        rr=a-b*market
        active=ok&np.isfinite(rel)&np.isfinite(rr)
        z=active.sum(axis=0)
        avg2=lambda v:np.sum(np.where(active,v,0.),axis=0)/np.maximum(z,1)
        ratio=(avg2(rr*rel)-avg2(rr)*avg2(rel))/(avg2(rel*rel)-avg2(rel)**2+.000024)
        gamma[i]=np.where(z>=35,np.clip(ratio,-.8,1.7),0.)
        if i%10==0:
            fit=rr
            unexplained=rr-rel*gamma[i]
            ver.append(dict(day=i,max_training=i-1,stock_fits=int(np.isfinite(market).sum()),market_beta_median=float(np.nanmedian(market)),
                            sector_beta_median=float(np.median(gamma[i])),raw_variance=float(np.nanmean(a*a)),
                            market_residual_variance=float(np.nanmean(fit*fit)),factor_residual_variance=float(np.nanmean(unexplained*unexplained))))
    return beta,gamma,pd.DataFrame(ver)


def run():
    p=np.load(OUT/'equity-panel.npz',allow_pickle=False)
    ix=pd.Index(p['days']);names=pd.Index(p['symbols']); groups=p['sector']
    ib=cash().pct_change(fill_method=None)
    r=p['return_adjusted']
    raw=np.log1p(r)
    clipped=np.clip(r,-.30,.30)
    m=ib.nifty50.to_numpy(float)
    matrix=np.column_stack([ib.get(SECTORS.get(g,'nifty50')) for g in SECTOR_NAMES])
    bt,gm,receipt=exposures(r,m,matrix,groups)
    receipt.day=ix[receipt.day];receipt.max_training=ix[receipt.max_training]
    write('factor-exposure-receipt.csv',receipt)
    vol=np.sqrt(prev(roll(clipped**2,21,15))/21*252)
    rr1=prev(r);rr5=np.expm1(prev(roll(raw,5,4)));rr21=np.expm1(prev(roll(raw,21,17)))
    mx5=np.expm1(prev(roll(np.log1p(m[:,None]),5))).ravel()
    mx21=np.expm1(prev(roll(np.log1p(m[:,None]),21))).ravel()
    sr=np.expm1(prev(roll(np.log1p(matrix),5)))
    selector=np.arange(len(ix))[:,None]
    prior_t=np.log1p(p['turnover'])
    shock=prev(prior_t)-prev(roll(prior_t,21,15))/21
    rng=np.log(np.maximum(p['high'],.01)/np.maximum(p['low'],.01))
    available=np.isfinite(rr1)&np.concatenate([p['eligible'][:1],p['eligible'][:-1]])
    eq_daily=np.divide(np.sum(np.where(available,rr1,0.),axis=1),available.sum(axis=1).clip(1))
    advance=np.sum(available&(rr1>0),axis=1)/available.sum(axis=1).clip(1)
    dispersion=np.sqrt(np.sum(np.where(available,(rr1-eq_daily[:,None])**2,0.),axis=1)/available.sum(axis=1).clip(1))
    same=np.sum(available&(np.sign(rr1)==np.sign(prev(m)[:,None])),axis=1)/available.sum(axis=1).clip(1)
    down=np.sqrt(np.sum(np.where(available,np.minimum(rr1,0.)**2,0.),axis=1)/available.sum(axis=1).clip(1))
    weight=p['weight_lag5']; w0=np.nan_to_num(weight)
    heavy=np.sum(w0*np.nan_to_num(rr1),axis=1)-eq_daily
    volm=np.sqrt(prev(roll(m[:,None]**2,21,15)).ravel()/21*252)
    f=csv('asof-features.csv.gz',V20)
    f=f[f.cutoff.eq('preauction_0855')].set_index('day').reindex(ix)
    macro={k:f[v].to_numpy(float) for k,v in V20_FIELDS.items()}
    market=dict(prior5=mx5,prior21=mx21,trailvol=volm,advance=advance,dispersion=dispersion,market_sync=same,
                proxy_heavy_gap=heavy,cross_downside=down,**macro)
    stock=dict(ret1=rr1,ret5=rr5,ret21=rr21,relative5=rr5-bt*mx5[:,None],relative21=rr21-bt*mx21[:,None],
               vol21=vol,turnover_shock=shock,range_5=prev(roll(rng,5,4))/5,beta=bt,sector_beta=gm,
               sector_lead=sr[selector,groups]-mx5[:,None],cross_dispersion=np.broadcast_to(dispersion[:,None],r.shape))
    stock.update({k:np.broadcast_to(v[:,None],r.shape) for k,v in macro.items() if k in STRUCT})
    stock.update(event_tensor(ix,names))
    features=(*TECH,*STRUCT,*COUNTS,*CONTENT,*REACTION,*ACTIVITY)
    x=np.stack([stock[item] for item in features],axis=-1).astype(np.float32)
    t=csv('multi-horizon-targets.csv',V20).set_index('day').reindex(ix)
    log_stock=np.log1p(r)
    hold_observed=(prev(p['volume'])>0)&(p['eligible']|((w0>0)&(prev(p['volume'])>0)))
    outputs=dict(days=p['days'],symbols=p['symbols'],fields=np.array(features),market_fields=np.array(MARKET),stock_features=x,
                 market_features=np.column_stack([market[v] for v in MARKET]),weights=weight,sector=groups,eligible=hold_observed,
                 beta=bt,sector_beta=gm,volume=p['volume'],daily_return=r,seed_rank=p['seed_rank'])
    for h in HORIZONS:
        ret=np.expm1(future(log_stock,h));index=np.expm1(future(np.log1p(m[:,None]),h)).ravel()
        sector=np.expm1(future(np.log1p(matrix),h)); vol_h=np.sqrt(future(r**2,h)*252/h)
        rel=ret-index[:,None];sec=sector[selector,groups]
        scale=np.maximum(.005,vol*np.sqrt(h/252))
        target=np.stack((ret,rel,ret-sec,ret/scale,(rel>0).astype(float),np.abs(ret),vol_h,
                         ret-bt*index[:,None]-gm*(sec-index[:,None])),axis=-1)
        target[:,:,4]=np.where(np.isfinite(rel),target[:,:,4],np.nan)
        end=pd.Series(ix,index=ix).shift(1-h).fillna('9999-12-31')
        ref=t[f'cohort_{h}'].notna()
        assert end[ref].eq(t.loc[ref,f'end_0_{h}']).all()
        np.testing.assert_allclose(index[ref],np.expm1(t.loc[ref,f'return_0_{h}']),atol=2.e-10,rtol=0)
        outputs.update({f'target{h}':target.astype(np.float32),f'sector_target{h}':sector, f'index{h}':index,
                        f'end{h}':end.to_numpy(dtype='U10'),f'cohort{h}':t[f'cohort_{h}'].fillna('').to_numpy(dtype='U7'),
                        f'scale{h}':scale})
    write('market-state-features.csv',pd.DataFrame(market,index=ix.rename('day')).reset_index())
    np.savez_compressed(OUT/'component-panel.npz',**outputs)
    save('feature-definitions.json',dict(stock_groups=GROUPS,market_fields=MARKET,market_source=V20_FIELDS,classes=SECTOR_NAMES,
         stock_targets=['absolute','market_relative','sector_relative','vol_normalized','outperform_market','magnitude','realized_volatility','factor_residual'],
         technical='Observed through reference cash close. Relative momentum removes trailing beta against NIFTY. Liquidity shock compares log INR turnover to trailing levels.',
         factor='Cash index beta and sector-relative beta use up to 100 past paired daily observations through the previous cash close. Sector returns later than issue are only training labels.',
         fundamentals='Original V18 eligible timestamp and first statistical result. Previously completed market reaction enters only after recorded eligible reaction.',
         positioning='Market panel only. NSE participant aggregates are never interpreted as positions in individual equities.',
         membership='Monthly official archives under five completed cash-session release allowance plus fixed January liquidity cohort. Training rows must have earlier complete outcomes.'))
    print('Feature tensor:',x.shape, 'point-in-time event joins complete',flush=True)


if __name__=='__main__':
    run()
