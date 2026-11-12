"""Chronological daily long-cash research engine, vectorized across stock sleeves.

Every stock owns separate capital; averaging its NAV does not create a pooled
single-account portfolio. Daily stop/target ambiguity is resolved stop first.
Decision arrays are known after session close and execute at the next open.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

def fee_coeff(day,buy=True,overnight=True,multiplier=1.):
    """Return proportional turnover fee and fixed order fee (equity delivery)."""
    exchange=.0000297 if str(day)[:10]<'2026-03-01' else .0000307
    ipft=.000001 if str(day)[:10]<'2026-03-01' else .000000001
    rate=.001+(.00015 if buy else 0)+1.18*(exchange+.000001+ipft)
    fixed=20*1.18+(20*1.18 if not buy and overnight else 0)
    return rate*multiplier,fixed*multiplier

def simulate(panel,signals,config,start,end,stocks=None,slippage_bps=2.,cost_multiplier=1.,keep_trades=False):
    dates=pd.DatetimeIndex(panel['dates'])
    lo=pd.Timestamp(start);hi=pd.Timestamp(end)
    if dates.tz is not None:
        lo=lo.tz_localize(dates.tz) if lo.tzinfo is None else lo.tz_convert(dates.tz)
        hi=hi.tz_localize(dates.tz) if hi.tzinfo is None else hi.tz_convert(dates.tz)
    columns=np.flatnonzero((dates>=lo)&(dates<hi))
    sel=np.arange(len(panel['symbols'])) if stocks is None else np.asarray(stocks,int)
    n=len(sel);length=len(columns)
    if not length or not n:raise ValueError('Empty stock/date research segment')
    actual=panel['actual'];o,h,l,c=(np.asarray(actual[k],float)[sel] for k in ['open','high','low','close'])
    unit=np.asarray(panel.get('unit_factor',np.ones_like(actual['close'])),float)[sel]
    split=np.asarray(panel.get('split_factor',np.ones_like(actual['close'])),float)[sel]
    div=np.asarray(panel.get('dividend',np.zeros_like(actual['close'])),float)[sel]
    entry_mask=np.asarray(signals['entry'],bool)[sel]
    exit_mask=np.asarray(signals.get('exit',np.zeros_like(signals['entry'])),bool)[sel]
    atr=np.asarray(signals['atr'],float)[sel]
    level=np.asarray(signals.get('level',np.full_like(signals['atr'],np.nan)),float)[sel]
    trail=np.asarray(signals.get('trail',np.full_like(signals['atr'],np.nan)),float)[sel]
    liquidity=np.asarray(panel.get('liquidity_value',np.full_like(actual['close'],np.inf)),float)[sel]
    volume=np.asarray(panel.get('median_volume20',np.full_like(actual['close'],np.inf)),float)[sel]
    initial=float(config.get('initial_capital',1_000_000));fraction=float(config.get('risk_fraction',.005))
    reward=float(config.get('reward',2));stop_atr=float(config.get('stop_atr',2))
    hold=int(config.get('max_hold_sessions',10));mode=config.get('exit','fixed')
    if mode not in ['fixed','time','atr_trail','ema','macd','trend']:raise ValueError('Unsupported daily exit '+mode)
    cash=np.full(n,initial);qty=np.zeros(n,int);entry=np.zeros(n);stop=np.zeros(n);target=np.zeros(n)
    initial_risk=np.zeros(n);enter_fees=np.zeros(n);entry_at=np.zeros(n,int);dividends=np.zeros(n)
    entry_fill=np.zeros(n);entry_qty=np.zeros(n,int);entry_signal=np.zeros(n,int)
    ntr=np.zeros(n,int);sum_r=np.zeros(n);win_count=np.zeros(n,int);win_sum=np.zeros(n);loss_sum=np.zeros(n)
    lose_count=np.zeros(n,int);fee_sum=np.zeros(n);gross_sum=np.zeros(n);hold_hours=np.zeros(n)
    streak=np.zeros(n,int);worst=np.zeros(n,int);peak=np.full(n,initial);maxdd=np.zeros(n)
    nav=np.zeros((n,length));exposed=np.zeros((n,length),bool);trades=[]
    slip=slippage_bps/10000;min_turnover=float(config.get('min_turnover',50_000_000));participation=float(config.get('participation',.01))

    def close(mask,price,t,reason):
        nonlocal qty,cash,streak,worst
        ids=np.flatnonzero(mask)
        if not len(ids):return
        price=np.broadcast_to(price,(n,))[ids]
        rate,fixed=fee_coeff(dates[t],False,False,cost_multiplier)
        overnight=entry_at[ids]!=t
        fees=price*qty[ids]*rate+fixed+overnight*(20*1.18*cost_multiplier)
        gross=(price-entry[ids])*qty[ids]+dividends[ids]
        net=gross-enter_fees[ids]-fees
        cash[ids]+=(price-entry[ids])*qty[ids]-fees
        ntr[ids]+=1;sum_r[ids]+=net/initial_risk[ids]
        wins=net>0;losses=net<0
        win_count[ids]+=wins;lose_count[ids]+=losses
        win_sum[ids]+=np.where(wins,net,0);loss_sum[ids]+=np.where(losses,-net,0)
        fee_sum[ids]+=enter_fees[ids]+fees;gross_sum[ids]+=gross
        elapsed=0 if reason in ['gap_stop','gap_target','signal_or_time'] else 6.25
        hours=(dates[t]-dates[entry_at[ids]]).total_seconds()/3600+elapsed
        hold_hours[ids]+=hours
        streak[ids]=np.where(losses,streak[ids]+1,0);worst[ids]=np.maximum(worst[ids],streak[ids])
        if keep_trades:
            for k,j in enumerate(ids):
                trades.append({'symbol':panel['symbols'][sel[j]],'signal_day':str(dates[entry_signal[j]]),'entry_day':str(dates[entry_at[j]]),
                  'exit_day':str(dates[t]),'entry_fill':entry_fill[j],'entry_quantity':int(entry_qty[j]),'entry_adjusted':entry[j],
                  'quantity':int(qty[j]),'exit':price[k],'stop':stop[j],'target':target[j],'initial_cash_risk':initial_risk[j],
                  'dividends':dividends[j],'gross_pnl':gross[k],'fees':enter_fees[j]+fees[k],'net_pnl':net[k],
                  'net_r':net[k]/initial_risk[j],'reason':reason,'holding_hours':hours[k]})
        qty[ids]=0

    for j,t in enumerate(columns):
        valid=np.isfinite(o[:,t])&np.isfinite(h[:,t])&np.isfinite(l[:,t])&np.isfinite(c[:,t])&(l[:,t]>0)
        had=qty>0
        if np.any(had&~valid):raise ValueError('Missing daily bar while a stock position is held')
        changed=had&(split[:,t]!=1)
        if changed.any():
            q=qty[changed]*split[changed,t]
            if np.any(np.abs(q-np.round(q))>1e-7):raise ValueError('Fractional entitlement is not modeled')
            qty[changed]=np.round(q).astype(int)
            entry[changed]/=split[changed,t];stop[changed]/=split[changed,t];target[changed]/=split[changed,t]
        cash[had]+=qty[had]*div[had,t];dividends[had]+=qty[had]*div[had,t]
        prev=t-1
        if prev>=0:
            # Known previous closes are converted into today's share units.
            if mode=='atr_trail':
                candidate=c[:,prev]/split[:,t]-float(config.get('trail_atr',2))*atr[:,prev]*unit[:,t]
                update=had&np.isfinite(candidate);stop[update]=np.maximum(stop[update],candidate[update])
            elif mode=='ema':
                candidate=trail[:,prev]*unit[:,t];update=had&np.isfinite(candidate);stop[update]=np.maximum(stop[update],candidate[update])
        close(had&(o[:,t]<=stop),o[:,t]*(1-slip),t,'gap_stop')
        if mode not in ['time','atr_trail','ema']:
            close((qty>0)&(o[:,t]>=target),target*(1-slip),t,'gap_target')
        if prev>=0:
            optional=exit_mask[:,prev] if mode in ['macd','ema','trend'] else np.zeros(n,bool)
            close((qty>0)&(optional|((t-entry_at)>=hold)),o[:,t]*(1-slip),t,'signal_or_time')
        # A signal before the segment start cannot initiate a new test position.
        if prev>=0 and dates[prev]>=lo:
            ready=(qty==0)&~had&valid&entry_mask[:,prev]&(cash>0)&np.isfinite(atr[:,prev])&(atr[:,prev]>0)
            # Panel liquidity arrays are lagged rolling medians known at this
            # open, through the preceding completed session (not t-2).
            ready&=~np.isnan(liquidity[:,t])&(liquidity[:,t]>=min_turnover)
            en=o[:,t]*(1+slip);a=atr[:,prev]*unit[:,t]
            st=en-stop_atr*a
            if config.get('stop_mode','atr') in ['swing','level']:
                st=level[:,prev]*unit[:,t]-float(config.get('buffer',.2))*a
            distance=en-st
            ready&=np.isfinite(st)&(st>0)&(distance>=.5*a)&(distance<=8*a)
            br,bf=fee_coeff(dates[t],True,False,cost_multiplier);sr,sf=fee_coeff(dates[t],False,True,cost_multiplier)
            stop_fill=st*(1-slip);per_share=en-stop_fill+en*br+stop_fill*sr
            budget=cash*fraction
            q_risk=np.floor(np.maximum(0,budget-bf-sf)/np.maximum(per_share,1e-20))
            q_cash=np.floor(np.maximum(0,cash-bf)/(en*(1+br)))
            # Data panel already expresses lagged median volume in today's share
            # units; multiplying again on an ex-date would double-count a split.
            cap=np.floor(volume[:,t]*participation)
            quantity=np.minimum(np.minimum(q_risk,q_cash),cap)
            ready&=np.isfinite(quantity)&(quantity>=1)
            ids=np.flatnonzero(ready)
            if len(ids):
                q=quantity[ids].astype(int);ef=en[ids]*q*br+bf
                risk=(en[ids]-stop_fill[ids])*q+ef+stop_fill[ids]*q*sr+sf
                # Algebraic fixed target yields reward*initial cash risk net of
                # the modeled overnight sell fees and adverse target slippage.
                tf=(en[ids]*q+reward*risk+ef+sf)/(q*(1-sr))
                cash[ids]-=ef;qty[ids]=q;entry[ids]=en[ids];stop[ids]=st[ids];target[ids]=tf/(1-slip)
                initial_risk[ids]=risk;enter_fees[ids]=ef;entry_at[ids]=t;entry_signal[ids]=prev
                dividends[ids]=0;entry_fill[ids]=en[ids];entry_qty[ids]=q
        exposed[:,j]=qty>0
        # Conservative daily ordering, including entries made at this open.
        close((qty>0)&(l[:,t]<=stop),stop*(1-slip),t,'stop')
        if mode not in ['time','atr_trail','ema']:
            close((qty>0)&(h[:,t]>=target),target*(1-slip),t,'target')
        if j==length-1:close(qty>0,c[:,t]*(1-slip),t,'segment_end')
        marked=cash+np.where(qty>0,(c[:,t]-entry)*qty,0)
        if not np.isfinite(marked).all():raise ValueError('Nonfinite sleeve NAV')
        nav[:,j]=marked;peak=np.maximum(peak,marked);maxdd=np.maximum(maxdd,1-marked/peak)
    returns=nav/np.concatenate([np.full((n,1),initial),nav[:,:-1]],axis=1)-1
    mean=returns.mean(axis=1);sd=returns.std(axis=1,ddof=1) if length>1 else np.zeros(n);down=np.sqrt(np.minimum(returns,0).__pow__(2).mean(axis=1))
    total=nav[:,-1]/initial-1;annual=np.maximum(nav[:,-1]/initial,1e-20)**(252/length)-1
    calendar_days=(dates[columns[-1]]-dates[columns[0]]).days+1
    cagr=np.maximum(nav[:,-1]/initial,1e-20)**(365.25/max(calendar_days,1))-1
    def divide(a,b):return np.divide(a,b,out=np.full(n,np.nan),where=b>0)
    metrics=pd.DataFrame({'symbol':[panel['symbols'][k] for k in sel],'n_trades':ntr,'net_profit':nav[:,-1]-initial,
      'total_return_pct':total*100,'annualized_return_pct':annual*100,'cagr_pct':cagr*100,
      'win_rate_pct':divide(win_count,ntr)*100,'profit_factor':divide(win_sum,loss_sum),'expectancy_r':divide(sum_r,ntr),
      'avg_win':divide(win_sum,win_count),'avg_loss':-divide(loss_sum,lose_count),'max_drawdown_pct':maxdd*100,
      'sharpe':divide(mean,sd)*np.sqrt(252),'sortino':divide(mean,down)*np.sqrt(252),'calmar':divide(cagr,maxdd),
      'avg_hold_hours':divide(hold_hours,ntr),'exposure_pct':exposed.mean(axis=1)*100,'fees':fee_sum,'gross_profit':gross_sum,
      'max_consecutive_losses':worst,'trades_per_month':ntr/(length/21),'sessions':length,
      'winning_trades':win_count,'losing_trades':lose_count,'winning_pnl':win_sum,'losing_pnl':loss_sum,'sum_r':sum_r})
    # Equal initial capital, no inter-sleeve reallocation. Mean NAV is a summary,
    # not the mean of daily returns (which would imply daily rebalancing).
    portfolio=nav.mean(axis=0);pr=portfolio/np.r_[initial,portfolio[:-1]]-1
    return {'stock_metrics':metrics,'equity':pd.Series(portfolio,index=dates[columns]),
            'returns':pd.Series(pr,index=dates[columns]),'stock_equity':nav,
            'trades':pd.DataFrame(trades),'dates':dates[columns]}

EXECUTION_KEYS=['initial_capital','risk_fraction','reward','stop_atr','max_hold_sessions','exit','stop_mode','buffer','trail_atr','min_turnover','participation']
def execution_signature(config):
    import json
    return json.dumps({k:config.get(k) for k in EXECUTION_KEYS},sort_keys=True)

def simulate_many(panel,signal_list,configs,start,end,stocks=None,slippage_bps=5.,cost_multiplier=1.,keep_trades=False):
    """Identical-execution rules run together; independent sleeve state per rule.

    Precomputed completed-candle indicators are sliced, never recomputed on this
    short execution window. This is an execution optimization, not vectorized
    future-return screening. Results are split back into their own NAV paths.
    """
    if not configs or len(configs)!=len(signal_list):raise ValueError('Batch configurations/signals must have equal positive length')
    if len({execution_signature(c) for c in configs})!=1:raise ValueError('Batch execution rules differ')
    dates=pd.DatetimeIndex(panel['dates']);lo=pd.Timestamp(start);hi=pd.Timestamp(end)
    if dates.tz is not None:
        lo=lo.tz_localize(dates.tz) if lo.tzinfo is None else lo.tz_convert(dates.tz)
        hi=hi.tz_localize(dates.tz) if hi.tzinfo is None else hi.tz_convert(dates.tz)
    col=np.flatnonzero((dates>=lo)&(dates<hi))
    if not len(col):raise ValueError('Empty date research segment')
    col=np.r_[max(0,col[0]-1),col] if col[0]>0 else col
    select=np.arange(len(panel['symbols'])) if stocks is None else np.asarray(stocks,int)
    count=len(configs);n=len(select)
    p={'dates':dates[col],'symbols':[str(c['id'])+'|'+panel['symbols'][s] for c in configs for s in select],
       'actual':{k:np.tile(np.asarray(v)[np.ix_(select,col)],(count,1)) for k,v in panel['actual'].items()}}
    for key in ['unit_factor','split_factor','dividend','liquidity_value','median_volume20']:
        if key in panel:p[key]=np.tile(np.asarray(panel[key])[np.ix_(select,col)],(count,1))
    sig={}
    for key in ['entry','exit','atr','level','trail']:
        if not any(key in s for s in signal_list):continue
        fill=False if key in ['entry','exit'] else np.nan
        sig[key]=np.concatenate([np.asarray(s.get(key,np.full_like(s['atr'],fill,dtype=bool if key in ['entry','exit'] else float)))[np.ix_(select,col)] for s in signal_list],axis=0)
    combined=simulate(p,sig,configs[0],start,end,slippage_bps=slippage_bps,cost_multiplier=cost_multiplier,keep_trades=keep_trades)
    outputs={}
    for j,cfg in enumerate(configs):
        frame=combined['stock_metrics'].iloc[j*n:(j+1)*n].copy();frame['symbol']=[panel['symbols'][s] for s in select]
        nav=combined['stock_equity'][j*n:(j+1)*n];value=nav.mean(axis=0);r=value/np.r_[cfg.get('initial_capital',1_000_000),value[:-1]]-1
        tr=combined['trades']
        if keep_trades and len(tr):
            tr=tr[tr.symbol.str.startswith(str(cfg['id'])+'|')].copy();tr['symbol']=tr.symbol.str.split('|',n=1).str[1]
        outputs[cfg['id']]={'stock_metrics':frame,'equity':pd.Series(value,index=combined['dates']),
          'returns':pd.Series(r,index=combined['dates']),'stock_equity':nav,'trades':tr,'dates':combined['dates']}
    return outputs
