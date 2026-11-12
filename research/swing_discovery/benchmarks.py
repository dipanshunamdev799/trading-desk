"""Buy-and-hold sleeves with the same cash, fee and entry-liquidity assumptions."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .engine import fee_coeff
from .diagnostics import portfolio_metrics

def buy_hold(panel,stocks,start,end,slip_bps=5.):
    dates=pd.DatetimeIndex(panel['dates']);lo=pd.Timestamp(start,tz=dates.tz);hi=pd.Timestamp(end,tz=dates.tz)
    cols=np.flatnonzero((dates>=lo)&(dates<hi));select=np.asarray(stocks,int);n=len(select)
    a=panel['actual'];cash=np.full(n,1_000_000.);q=np.zeros(n,int);ever=np.zeros(n,bool);entry_t=np.zeros(n,int)
    nav=[];slip=slip_bps/10000
    volume=panel.get('median_volume20',panel['liquidity_volume']);turn=panel.get('liquidity_value',panel['liquidity_turnover'])
    for t in cols:
        sf=panel['split_factor'][select,t]
        fractional=np.abs(q*sf-np.round(q*sf))>1e-7
        if fractional.any():raise ValueError('Unmodeled fractional benchmark entitlement')
        q=np.round(q*sf).astype(int);cash+=q*panel['dividend'][select,t]
        o=a['open'][select,t];c=a['close'][select,t]
        ready=~ever&np.isfinite(o)&(turn[select,t]>=50_000_000)&np.isfinite(volume[select,t])
        rate,fixed=fee_coeff(dates[t],True,False);fill=o*(1+slip)
        quantity=np.minimum(np.floor((cash-fixed)/(fill*(1+rate))),np.floor(volume[select,t]*.01))
        ready&=np.isfinite(quantity)&(quantity>=1)
        ids=np.flatnonzero(ready)
        q[ids]=quantity[ids].astype(int);cash[ids]-=q[ids]*fill[ids]*(1+rate)+fixed;ever[ids]=True;entry_t[ids]=t
        if t==cols[-1]:
            sr,sf=fee_coeff(dates[t],False,False);exitfill=c*(1-slip);cost=exitfill*q*sr+sf+(entry_t!=t)*23.6
            cash+=np.where(q>0,exitfill*q-cost,0);q[:]=0
        value=cash+np.where(q>0,q*c,0)
        if not np.isfinite(value).all():raise ValueError('Missing held benchmark quote')
        nav.append(value)
    values=np.asarray(nav).T;equity=pd.Series(values.mean(axis=0),index=dates[cols])
    return {'equity':equity,'stock_metrics':pd.DataFrame({'symbol':[panel['symbols'][i] for i in select],
       'total_return_pct':(values[:,-1]/1_000_000-1)*100,'bought':ever}),
       'summary':portfolio_metrics(equity,int(ever.sum()))}

def write_benchmarks(panel,out,development,reserved,allstocks):
    rows=[];stock=[]
    parts={'development':('2024-11-10','2025-11-10'),'validation':('2025-11-10','2026-05-10'),
      'final':('2026-05-10','2026-11-10'),'two_year':('2024-11-10','2026-11-10')}
    for pool,indices in [('development_stocks',development),('reserved_stocks',reserved),('all_eligible_stocks',allstocks)]:
        for part,(start,end) in parts.items():
            r=buy_hold(panel,indices,start,end);rows.append({'pool':pool,'stage':part,**r['summary']})
            frame=r['stock_metrics'].copy();frame.insert(0,'stage',part);frame.insert(0,'pool',pool);stock.append(frame)
            if pool=='all_eligible_stocks':r['equity'].to_csv(out/f'buy-hold-{part}-equity.csv',header=['equity'])
    pd.DataFrame(rows).to_csv(out/'buy-hold-benchmarks.csv',index=False)
    pd.concat(stock,ignore_index=True).to_csv(out/'buy-hold-stock-results.csv',index=False)
