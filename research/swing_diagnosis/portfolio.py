"""Funded, integer-share cash portfolio diagnostic; no order submission."""
import numpy as np
import pandas as pd
from research.swing_discovery.engine import fee_coeff
from research.swing_discovery.diagnostics import portfolio_metrics

POLICIES=['equal','volatility','risk','risk_correlation','risk_correlation_dd']

def simulate_portfolio(p,sig,cfg,start,end,policy='risk',slip_bps=5,cost=1.,correct_intraday=False):
    dates=p['dates'];lo=pd.Timestamp(start,tz=dates.tz);hi=pd.Timestamp(end,tz=dates.tz)
    cols=np.flatnonzero((dates>=lo)&(dates<hi));eligible=np.asarray(p['eligible'],bool)
    o,h,l,c=(p['actual'][k] for k in ['open','high','low','close']);neutral=p['neutral']['close']
    returns=neutral/np.roll(neutral,1,axis=1)-1;returns[:,0]=np.nan
    slip=slip_bps/10000;cash=1_000_000.;positions={};trades=[];days=[];reject={};peak=1_000_000.;prior_nav=peak;halt=False
    maxcashrisk=0.;mincash=cash;maxpositions=0;turnover=0.;fees_total=0.;candidate_count=0
    def reject_one(reason):reject[reason]=reject.get(reason,0)+1
    def exit_one(s,price,t,reason):
        nonlocal cash,turnover,fees_total
        z=positions.pop(s);sr,sf=fee_coeff(dates[t],False,z['entry_t']!=t,cost);fee=price*z['q']*sr+sf
        refund=0.
        if correct_intraday and z['entry_t']==t:
            from research.swing_diagnosis.audit_engine import intraday_refund
            refund=intraday_refund(dates[t],z['entry_notional'],price*z['q'],cost)
        proceeds=price*z['q']-fee+refund;cash+=proceeds;turnover+=price*z['q'];fees_total+=fee-refund
        net=proceeds-z['entry_notional']-z['entry_fees']+z['dividends']
        trades.append(dict(symbol=p['symbols'][s],signal_day=str(dates[z['entry_t']-1].date()),entry_day=str(dates[z['entry_t']].date()),exit_day=str(dates[t].date()),
          entry=z['entry_original'],entry_quantity=z['q_original'],exit=price,exit_quantity=z['q'],net_pnl=net,fees=z['entry_fees']+fee-refund,
          initial_risk=z['risk'],net_r=net/z['risk'],reason=reason,dividends=z['dividends']))
    for j,t in enumerate(cols):
        had=set(positions);prev=t-1
        for s in list(positions):
            z=positions[s];factor=p['split_factor'][s,t];q=z['q']*factor
            if abs(q-round(q))>1e-7:raise ValueError('Fractional funded entitlement '+p['symbols'][s])
            z['q']=int(round(q));z['entry']/=factor;z['stop']/=factor;z['target']/=factor
            dividend=z['q']*p['dividend'][s,t];cash+=dividend;z['dividends']+=dividend
            if o[s,t]<=z['stop']:exit_one(s,o[s,t]*(1-slip),t,'gap_stop')
            elif o[s,t]>=z['target']:exit_one(s,z['target']*(1-slip),t,'gap_target')
            elif t-z['entry_t']>=cfg.get('max_hold_sessions',10):exit_one(s,o[s,t]*(1-slip),t,'time')
        # A close-observed drawdown triggers an entry halt beginning next open.
        if policy.endswith('_dd') and 1-prior_nav/peak>=.15:halt=True
        heldvalue={s:z['q']*c[s,prev]/p['split_factor'][s,t] for s,z in positions.items()}
        budget_nav=cash+sum(heldvalue.values())
        if prev>=0 and dates[prev]>=lo:
            candidates=np.flatnonzero(eligible & sig['entry'][:,prev])
            rank=neutral[:,prev]/neutral[:,max(0,prev-60)]-1
            candidates=sorted(candidates,key=lambda s:(-rank[s] if np.isfinite(rank[s]) else np.inf,p['symbols'][s]))
            for s in candidates:
                candidate_count+=1
                if s in had or s in positions:reject_one('already_held_or_same_day_exit');continue
                if halt:reject_one('drawdown_halt');continue
                if len(positions)>=10:reject_one('position_limit');continue
                atr=sig['atr'][s,prev]*p['unit_factor'][s,t];en=o[s,t]*(1+slip);st=en-cfg.get('stop_atr',2)*atr
                if not np.isfinite(en+atr+st) or atr<=0 or st<=0:reject_one('invalid_price_atr');continue
                if p['liquidity_turnover'][s,t]<50_000_000 or not np.isfinite(p['liquidity_volume'][s,t]):reject_one('liquidity');continue
                if 'correlation' in policy and positions:
                    window=returns[:,max(1,prev-59):prev+1];correlated=False
                    for other in positions:
                        valid=np.isfinite(window[s])&np.isfinite(window[other])
                        if valid.sum()>=40 and np.std(window[s,valid])>0 and np.std(window[other,valid])>0:
                            if np.corrcoef(window[s,valid],window[other,valid])[0,1]>.8:correlated=True;break
                    if correlated:reject_one('correlation');continue
                br,bf=fee_coeff(dates[t],True,False,cost);sr,sf=fee_coeff(dates[t],False,True,cost)
                stopfill=st*(1-slip);perrisk=en-stopfill+en*br+stopfill*sr
                if policy=='equal':desired=.10*budget_nav/en
                elif policy=='volatility':
                    v=np.nanstd(returns[s,max(1,prev-59):prev+1],ddof=1)*np.sqrt(252)
                    desired=min(.20,.10*.20/v)*budget_nav/en if v>0 else 0
                else:desired=max(0,.005*budget_nav-bf-sf)/perrisk
                sector=p['sector'][s];sectorvalue=sum(heldvalue.get(k,z['q']*o[k,t]) for k,z in positions.items() if p['sector'][k]==sector)
                q=int(np.floor(min(desired,.2*budget_nav/en,max(0,.3*budget_nav-sectorvalue)/en,
                     max(0,cash-bf)/(en*(1+br)),p['liquidity_volume'][s,t]*.01)))
                if q<1:reject_one('cash_sector_or_size_cap');continue
                ef=en*q*br+bf;risk=perrisk*q+bf+sf;target=(en*q+cfg.get('reward',2)*risk+ef+sf)/(q*(1-sr))/(1-slip)
                cash-=en*q+ef;turnover+=en*q;fees_total+=ef
                positions[s]=dict(q=q,q_original=q,entry=en,entry_original=en,entry_notional=en*q,entry_fees=ef,entry_t=t,stop=st,target=target,risk=risk,dividends=0.)
                heldvalue[s]=en*q;maxcashrisk=max(maxcashrisk,risk/budget_nav)
                mincash=min(mincash,cash);maxpositions=max(maxpositions,len(positions))
        # Daily ambiguity uses stop-first, matching the original control.
        for s in list(positions):
            z=positions[s]
            if l[s,t]<=z['stop']:exit_one(s,z['stop']*(1-slip),t,'stop')
            elif h[s,t]>=z['target']:exit_one(s,z['target']*(1-slip),t,'target')
        if j==len(cols)-1:
            for s in list(positions):exit_one(s,c[s,t]*(1-slip),t,'segment_end')
        invested=sum(z['q']*c[s,t] for s,z in positions.items());nav=cash+invested
        if cash < -1e-6 or len(positions)>10 or not np.isfinite(nav):raise AssertionError('Funded allocation invariant')
        days.append(dict(day=dates[t],equity=nav,cash=cash,invested=invested,positions=len(positions),utilization_pct=100*invested/nav))
        prior_nav=nav;peak=max(peak,nav)
    d=pd.DataFrame(days).set_index('day');tr=pd.DataFrame(trades);m=portfolio_metrics(d.equity,len(tr))
    m.update(policy=policy,exposure_pct=float(d.utilization_pct.mean()),max_positions=maxpositions,min_cash=mincash,
      turnover_multiple=turnover/1_000_000,fees=fees_total,entry_candidates=candidate_count,rejections=reject,
      max_entry_risk_fraction=maxcashrisk,drawdown_halt=halt,
      realized_pnl=float(tr.net_pnl.sum()) if len(tr) else 0.)
    if not np.isclose(d.equity.iloc[-1]-1_000_000,m['realized_pnl'],atol=1e-6):raise AssertionError('Cash/PnL reconciliation')
    return m,d,tr
