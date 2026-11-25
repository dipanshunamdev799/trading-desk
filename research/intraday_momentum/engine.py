"""Cash-equity intraday portfolio experiment, without any broker capability.

All strategies share one cash account, a chronological three-entry daily cap,
integer shares, and causal decision-time size/volume limits. The caller passes
audited historical sessions; this module never reads or writes a database.
"""
from collections import Counter
from dataclasses import dataclass,asdict
import math

import numpy as np
import pandas as pd

from .costs import fees,adverse_price

MECHANISMS=('cross8','cross10','breakout8','vwap_reclaim8','exhaustion8','cross8_no_volume')


@dataclass(frozen=True)
class Config:
    mechanism:str
    stop:float=.005
    target:float=.01
    hold_minutes:int=60
    capital:float=1_000_000.
    risk_fraction:float=.005
    daily_loss_fraction:float=.01
    max_trades_per_day:int=3
    participation:float=.01
    slippage_bps:float=10.
    chase_limit:float=.005
    entry_delay_bars:int=0
    allow_short:bool=False

    @property
    def name(self):
        return self.mechanism+'-sl'+str(int(self.stop*10000))+'-'+('long_short_diagnostic' if self.allow_short else 'long_only')


def catalog():return [Config(m,stop=s) for m in MECHANISMS for s in (.005,.01)]


def planned_size(signal,decision_bar,equity,day_pnl,day_start,config):
    """Quantity fixed from information available at the decision close."""
    side=int(signal['side']);close=float(signal['raw_price'])
    if close<=0 or not math.isfinite(close):return 0
    entry_side='BUY' if side==1 else 'SELL';exit_side='SELL' if side==1 else 'BUY'
    # Cash and risk are reserved at the maximum permitted entry price.
    worst=close*(1+config.chase_limit)
    risk_room=min(equity*config.risk_fraction,day_start*config.daily_loss_fraction+day_pnl)
    if risk_room<=0:return 0
    vol=float(decision_bar['volume'])
    if not math.isfinite(vol) or vol<=0:return 0
    high=min(math.floor(equity/worst),math.floor(vol*config.participation));low=0
    expected_stop=adverse_price(worst*(1-side*config.stop),exit_side,config.slippage_bps)
    loss_per_share=max(0,side*(worst-expected_stop))
    while low<high:
        q=(low+high+1)//2
        entry_fee=fees(entry_side,worst,q)['total'];exit_fee=fees(exit_side,expected_stop,q)['total']
        if worst*q+entry_fee<=equity and q*loss_per_share+entry_fee+exit_fee<=risk_room:low=q
        else:high=q-1
    return low


def fill_trade(record,signal,quantity,config,*,equity=None,risk_room=None):
    """Next-open fill and stop-first five-minute execution model."""
    bars=record['bars'];known=pd.Timestamp(signal['known_at']);side=int(signal['side'])
    wanted=known+pd.Timedelta(minutes=5*config.entry_delay_bars)
    if not '09:30'<=wanted.strftime('%H:%M')<='11:30':return None,'entry_outside_window'
    if wanted not in bars.index:return None,'missing_entry_bar'
    i=int(bars.index.get_loc(wanted))
    entry_side='BUY' if side==1 else 'SELL';exit_side='SELL' if side==1 else 'BUY'
    row=bars.iloc[i]
    # A flat entry candle is future information, not an admission filter. Only
    # an absent trade observation prevents modeling a fill; size was fixed
    # from the already-completed decision candle.
    if float(row['volume'])<=0:return None,'no_entry_liquidity'
    entry=adverse_price(float(row['open']),entry_side,config.slippage_bps)
    raw=float(signal['raw_price'])
    if side*(entry/raw-1)>config.chase_limit+1e-12:return None,'beyond_chase_limit'
    entry_fee=fees(entry_side,entry,quantity)
    if equity is not None and entry*quantity+entry_fee['total']>equity:
        return None,'gap_exceeds_cash'
    estimated_stop=adverse_price(entry*(1-side*config.stop),exit_side,config.slippage_bps)
    risk_at_entry=max(0,side*(entry-estimated_stop))*quantity+entry_fee['total']+fees(exit_side,estimated_stop,quantity)['total']
    if risk_room is not None and risk_at_entry>risk_room+1e-8:
        return None,'gap_exceeds_planned_risk'
    stop=entry*(1-side*config.stop);target=entry*(1+side*config.target)
    due=min(wanted+pd.Timedelta(minutes=config.hold_minutes),wanted.normalize()+pd.Timedelta(hours=15,minutes=10))
    if due not in bars.index:
        raise ValueError('Missing scheduled exit price: '+record['key']+' '+str(due))
    exit_raw=None;reason=None;ambiguous=False;exit_time=None;busy_until=None;exit_volume=None
    for j in range(i,len(bars)):
        at=bars.index[j];b=bars.iloc[j];o,h,l,c,v=(float(b[x]) for x in ('open','high','low','close','volume'))
        if at>=due:
            exit_raw=o;reason='TIME_EXIT';exit_time=at;busy_until=at;exit_volume=v;break
        stop_hit=l<=stop if side==1 else h>=stop
        target_hit=h>=target if side==1 else l<=target
        if stop_hit or target_hit:
            ambiguous=stop_hit and target_hit
            if stop_hit:
                exit_raw=min(o,stop) if side==1 else max(o,stop)
                reason='STOP_FIRST_AMBIGUOUS' if ambiguous else 'STOP'
            else:exit_raw=target;reason='TARGET'
            exit_time=at;busy_until=at+pd.Timedelta(minutes=5);exit_volume=v;break
    if exit_raw is None:raise ValueError('No exit observation')
    if exit_volume<=0:
        raise ValueError('Exit observation has zero traded volume')
    exit_price=adverse_price(exit_raw,exit_side,config.slippage_bps)
    ef=entry_fee;xf=fees(exit_side,exit_price,quantity)
    gross=side*(exit_price-entry)*quantity;net=gross-ef['total']-xf['total']
    result=dict(instrument_key=record['key'],symbol=record['symbol'],session=record['day'],
        decision_at=known.isoformat(),entry_at=wanted.isoformat(),exit_bar_at=exit_time.isoformat(),
        capital_released_at=busy_until.isoformat(),side='LONG' if side==1 else 'SHORT',quantity=quantity,
        decision_price=raw,entry_price=entry,exit_price=exit_price,stop_price=stop,target_price=target,
        raw_entry_price=float(row['open']),raw_exit_price=exit_raw,
        planned_loss_at_entry=risk_at_entry,
        slippage_rupees=(abs(entry-float(row['open']))+abs(exit_price-exit_raw))*quantity,
        gross_before_slippage=side*(exit_raw-float(row['open']))*quantity,
        reason=reason,ambiguous=ambiguous,gross_pnl=gross,fees=ef['total']+xf['total'],net_pnl=net,
        observed_move=float(signal['move']),rvol=float(signal['rvol']),score=float(signal['score']),
        decision_bar_participation=quantity/float(bars.loc[known-pd.Timedelta(minutes=5),'volume']),
        entry_bar_participation=quantity/float(row['volume']),exit_bar_participation=quantity/exit_volume,
        entry_fee_components=ef,exit_fee_components=xf,mode='research_model',real_orders_submitted=0)
    return result,'filled'


def run(records,signals,calendar,config):
    """Signals are precomputed without inspecting any future bar."""
    lookup={(r['day'],r['key']):r for r in records}
    by_day={}
    for s in signals:
        if s['mechanism']!=config.mechanism:continue
        if not config.allow_short and s['side']!=1:continue
        day=pd.Timestamp(s['known_at']).date().isoformat()
        if day in calendar:by_day.setdefault(day,[]).append(s)
    equity=config.capital;peak=equity;trades=[];daily=[];rejections=Counter()
    for day in calendar:
        opening=equity;used=set();count=0;busy=None;day_pnl=0.;halted=False
        for signal in sorted(by_day.get(day,[]),key=lambda s:(pd.Timestamp(s['known_at']),-s['score'],s['key'])):
            known=pd.Timestamp(signal['known_at'])
            if busy is not None and known<busy:rejections['position_already_open']+=1;continue
            if halted:rejections['daily_loss_budget']+=1;continue
            if count>=config.max_trades_per_day:rejections['daily_trade_cap']+=1;continue
            if signal['key'] in used:rejections['same_symbol_reentry']+=1;continue
            record=lookup[(day,signal['key'])];bar_time=known-pd.Timedelta(minutes=5)
            if bar_time not in record['bars'].index:raise ValueError('Decision bar absent')
            q=planned_size(signal,record['bars'].loc[bar_time],equity,day_pnl,opening,config)
            if q<=0:rejections['cash_risk_or_volume_size']+=1;continue
            trade,tag=fill_trade(record,signal,q,config,equity=equity,
                risk_room=min(equity*config.risk_fraction,opening*config.daily_loss_fraction+day_pnl))
            if trade is None:rejections[tag]+=1;continue
            trade.update(strategy=config.name,equity_before=equity)
            equity+=trade['net_pnl'];day_pnl+=trade['net_pnl'];trade['equity_after']=equity
            trades.append(trade);used.add(signal['key']);count+=1;busy=pd.Timestamp(trade['capital_released_at'])
            halted=day_pnl<=-opening*config.daily_loss_fraction
        peak=max(peak,equity)
        daily.append(dict(session=day,equity=equity,return_fraction=equity/opening-1,
                          pnl=equity-opening,trades=count,drawdown=equity/peak-1))
    return dict(config=asdict(config),name=config.name,trades=trades,daily=daily,rejections=dict(rejections))


def summarize(result,first=None,last=None):
    rows=[r for r in result['daily'] if (first is None or r['session']>=first) and (last is None or r['session']<=last)]
    trades=[t for t in result['trades'] if (first is None or t['session']>=first) and (last is None or t['session']<=last)]
    if not rows:return dict(trades=0,calendar_days=0)
    returns=np.array([r['return_fraction'] for r in rows]);curve=np.cumprod(1+returns)
    dd=curve/np.maximum.accumulate(np.r_[1.,curve])[1:]-1
    pos=sum(t['net_pnl'] for t in trades if t['net_pnl']>0);neg=-sum(t['net_pnl'] for t in trades if t['net_pnl']<0)
    elapsed=max((pd.Timestamp(rows[-1]['session'])-pd.Timestamp(rows[0]['session'])).days/365.25,1/365.25)
    return dict(trades=len(trades),calendar_days=len(rows),active_days=sum(r['trades']>0 for r in rows),
        total_return=float(curve[-1]-1),cagr=float(curve[-1]**(1/elapsed)-1),
        net_pnl=float(sum(t['net_pnl'] for t in trades)),gross_pnl=float(sum(t['gross_pnl'] for t in trades)),
        fees=float(sum(t['fees'] for t in trades)),profit_factor=float(pos/neg) if neg else None,
        win_rate=float(sum(t['net_pnl']>0 for t in trades)/len(trades)) if trades else None,
        net_per_trade=float(np.mean([t['net_pnl'] for t in trades])) if trades else None,
        mean_net_bps_per_trade=float(np.mean([t['net_pnl']/(t['entry_price']*t['quantity'])*10000 for t in trades])) if trades else None,
        slippage_rupees=float(sum(t['slippage_rupees'] for t in trades)),
        entry_turnover=float(sum(t['entry_price']*t['quantity'] for t in trades)),
        max_drawdown=float(dd.min()),drawdown_basis='End-of-day marked cash equity; not intraday path drawdown',
        sharpe_zero_rf=float(returns.mean()/returns.std(ddof=1)*np.sqrt(252)) if returns.std(ddof=1)>0 else None,
        stop_first_ambiguous_trades=sum(t['ambiguous'] for t in trades),
        entry_participation_over_1pct=sum(t['entry_bar_participation']>.01 for t in trades),
        exit_participation_over_1pct=sum(t['exit_bar_participation']>.01 for t in trades))


def block_bootstrap(result,first=None,last=None,iterations=2000,seed=731):
    rows=[r for r in result['daily'] if (first is None or r['session']>=first) and (last is None or r['session']<=last)]
    x=np.array([r['return_fraction'] for r in rows]);n=len(x)
    if n<10:return dict(status='insufficient_days')
    rng=np.random.default_rng(seed);width=20
    starts=rng.integers(0,n,size=(iterations,math.ceil(n/width)))
    indexes=(starts[:,:,None]+np.arange(width))%n
    samples=x[indexes.reshape(iterations,-1)[:,:n]]
    totals=np.prod(1+samples,axis=1)-1
    lo,hi=np.quantile(totals,[.025,.975])
    return dict(block_sessions=width,iterations=iterations,seed=seed,total_return_ci95=[float(lo),float(hi)],
                resampled_fraction_positive=float(np.mean(totals>0)),
                limitation='Conditional on this observed sample and selected model; not a multiple-testing-adjusted probability of a profitable strategy')
