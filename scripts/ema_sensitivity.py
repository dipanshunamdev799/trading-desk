from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.ema_validation.engine import *

def main():
    q=prepare();cache_correlations(q);p=q['p'];dates=p['dates'];entry=q['ema']&q['rs'];base=entry&q['gate'][None,:];order=orders(q,base)
    a=simulate(q,order);tr=a['trades'];names=p['symbols'];out=[]
    frame=pd.DataFrame(tr,columns=TRADE_COLUMNS)
    frame['symbol']=[names[int(s)] for s in frame.stock];frame['entry_date']=[str(dates[int(t)].date()) for t in frame.entry_t];frame['signal_date']=[str(dates[int(t)].date()) for t in frame.signal_t]
    stock=frame.groupby('symbol').agg(trades=('net_pnl','size'),net_pnl=('net_pnl','sum'),fees=('fees','sum'),mean_net_r=('net_r','mean')).sort_values('net_pnl',ascending=False).reset_index()
    stock['contribution_pct_initial']=stock.net_pnl/1e4;stock.to_csv(OUT/'stock-contributions.csv',index=False)
    best=names.index(stock.iloc[0].symbol);r=simulate(q,order,exclude=best);out.append(dict(test='exclude_highest_pnl_stock',excluded=names[best],**r['metrics']))
    gate=q['gate'].copy();gate[:q['cols'][0]-1]=False;gate[q['cols'][-1]:]=False
    on=np.flatnonzero(gate);ids=np.full(len(gate),-1,int);episode=[]
    if len(on):
        groups=np.split(on,np.flatnonzero(np.diff(on)>10)+1)
        for i,g in enumerate(groups):
            ids[g]=i;episode.append(dict(event=i,start=str(dates[g[0]].date()),end=str(dates[g[-1]].date()),expansion_sessions=len(g),calendar_sessions=int(g[-1]-g[0]+1)))
    frame['event']=[ids[int(t)] for t in frame.signal_t];assert frame.event.ge(0).all()
    for e in episode:
        g=frame[frame.event==e['event']];e.update(trades=len(g),stocks=g.symbol.nunique(),net_pnl=g.net_pnl.sum(),mean_net_r=g.net_r.mean(),signal_days=g.signal_t.nunique())
        blocked=base.copy();blocked[:,ids==e['event']]=False;r=simulate(q,orders(q,blocked));out.append(dict(test='leave_one_event_out',excluded=str(e['event']),**r['metrics']))
    pd.DataFrame(episode).to_csv(OUT/'market-episodes.csv',index=False);frame.to_csv(OUT/'A-trades.csv',index=False)
    pd.DataFrame(out).to_csv(OUT/'exclusion-replays.csv',index=False)
    rows=[]
    for stage,(start,end) in json.loads((OUT/'freeze.json').read_text())['stages'].items():
        for cost,slip,label in [(1,5,'baseline'),(2,10,'double_fees10bps'),(3,20,'triple_fees20bps')]:
            r=simulate(q,order,start,end,cost,slip);rows.append(dict(stage=stage,scenario=label,**r['metrics']))
    pd.DataFrame(rows).to_csv(OUT/'cost-sensitivity.csv',index=False)
    # Diagnostic robustness on development only; final gate stays strictly1.2.
    r=pd.Series(p['niftyclose']).pct_change();ew=(r.ewm(span=20,min_periods=20,adjust=True).std()/r.ewm(span=60,min_periods=60,adjust=True).std()).to_numpy()
    rows=[]
    for method,ratio in [('sample_std20_60',q['ratio']),('ewma_span20_60',ew)]:
        for threshold in [1.1,1.2,1.3]:
            mask=entry&(ratio[None,:]>threshold);run=simulate(q,orders(q,mask),'2024-11-10','2025-11-10')
            rows.append(dict(method=method,threshold=threshold,stage='development_only',**run['metrics']))
    pd.DataFrame(rows).to_csv(OUT/'development-threshold-sensitivity.csv',index=False)
    # Actual known completed-date context, not retrospective optimized entry lag.
    observed=frame.copy();market=p['niftyclose'];onstart=np.zeros(len(gate),int);start=0
    for t in range(len(gate)):
        if gate[t] and (t==0 or not gate[t-1]):start=t
        onstart[t]=start
    observed['expansion_age_sessions']=[int(t)-onstart[int(t)] for t in observed.signal_t]
    for n in [5,20]:observed[f'prior_market_return{n}_pct']=[100*(market[int(t)]/market[int(t)-n]-1) for t in observed.signal_t]
    observed.to_csv(OUT/'entry-event-context.csv',index=False)
    save('sensitivity-summary.json',dict(best_stock=names[best],best_stock_pnl=float(stock.iloc[0].net_pnl),top5_pnl=float(stock.head(5).net_pnl.sum()),total_pnl=float(frame.net_pnl.sum()),
      event_count=len(episode),contiguous_expansion_episodes=int(np.sum(gate&~np.r_[False,gate[:-1]])),expansion_sessions=int(gate.sum()),
      final_expansion_sessions=int(gate[(dates>=pd.Timestamp('2026-05-10',tz=dates.tz))].sum()),
      caveat='Highest stock/event exclusions are post-outcome sensitivity replays; they do not define revised strategies. Development thresholds are diagnostics only; frozen final/prospective threshold remains1.2.'))
    print('SENSITIVITY_COMPLETE',flush=True)

if __name__=='__main__':main()
