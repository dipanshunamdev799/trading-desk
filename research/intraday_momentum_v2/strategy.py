"""Causal families and funded chronological execution; no broker imports."""
from dataclasses import dataclass,replace,asdict
import math
import numpy as np
import pandas as pd

from research.intraday_momentum.costs import fees,adverse_price
from research.intraday_momentum.engine import Config as SizeConfig,planned_size,summarize,block_bootstrap


@dataclass(frozen=True)
class Config:
    family:str
    exit:str='F'
    variant:str='main'
    direction:int=1
    slippage_bps:float=10.
    participation:float=.01
    capital:float=1_000_000.
    delay:int=0
    @property
    def name(self):return f'{self.family}-{self.exit}-{self.variant}-'+('long' if self.direction==1 else 'short_diagnostic')


def catalog():
    primary=[Config(f,e) for f in ('H1','H2','H4','H5') for e in ('F','S','A')]
    controls=[Config('H1','F',v) for v in ('price_only','no_market','peers')]+[Config('H2','S','no_failure')]
    controls += [Config(f,'B','baseline') for f in ('B8','B10')]
    return primary+controls+[replace(c,direction=-1) for c in primary]


def features(record):
    b=record['bars'];a=b.to_numpy(float);o,h,l,c,v=a.T
    pv=np.r_[o[0],c[:-1]];tr=np.maximum(h-l,np.maximum(abs(h-pv),abs(l-pv)))
    atr=pd.Series(tr).rolling(14,min_periods=3).mean().to_numpy()
    vw=np.divide(np.cumsum((h+l+c)/3*v),np.cumsum(v),out=np.full(len(c),np.nan),where=np.cumsum(v)>0)
    return dict(o=o,h=h,l=l,c=c,v=v,vwap=vw,atr=atr,
        move=c/record['prev_close']-1,rvol=record['rvol'].to_numpy(float),
        change3=np.r_[np.full(3,np.nan),c[3:]/c[:-3]-1],
        ph=pd.Series(h).shift().rolling(3).max().to_numpy(),
        pl=pd.Series(l).shift().rolling(3).min().to_numpy(),
        vm=pd.Series(v).shift().rolling(3).median().to_numpy(),
        efficiency=np.divide(abs(c-o[0]),np.cumsum(abs(c-pv)),out=np.zeros(len(c)),where=np.cumsum(abs(c-pv))>0))


def signals(record,market,peer=None):
    """Only prefixes determine feature values and qualifying observations."""
    f=features(record);n=len(f['c']);times=record['bars'].index
    if n<4:return []
    result=[]
    for side in (1,-1):
        # Directional coordinates permit exact symmetric signal definitions.
        c=f['c']*side;o=f['o']*side;h=f['h'] if side==1 else -f['l'];l=f['l'] if side==1 else -f['h']
        peak=np.maximum.accumulate(h);priorpeak=np.r_[np.nan,peak[:-1]]
        move=f['move']*side;vw=f['vwap']*side;mr=np.asarray(market['return'])*side
        ph=f['ph'] if side==1 else -f['pl']
        orig_range=f['h']-f['l'];loc=np.divide(c-l,orig_range,out=np.zeros(n),where=orig_range>0)
        pull=(priorpeak-c)/f['c']
        dist=(c-vw)/f['c'];rvol=f['rvol'];mkt=(mr>=-.0025)
        common=(f['v']>0)&(orig_range>0)&np.isfinite(rvol)&(rvol>0)
        ignition=(move>=.02)&(move<=.05)&(c>max(h[:3])*1.+abs(max(h[:3]))*.0005)&(c>ph)&(f['change3']*side>=.003)&(c>vw)&(dist<=.015)&(loc>=.7)
        priornegative=np.array([any(c[j]<o[j] for j in range(max(0,i-3),i)) for i in range(n)])
        prevhigh=np.r_[np.nan,h[:-1]]
        pullback=(priorpeak*side/record['prev_close']-1)*side
        h2=(pullback>=.02)&(pullback<=.06)&(move>=.01)&(pull>=.003)&(pull<=.012)&priornegative&(c>prevhigh)&(c>vw)&(f['v']>=1.2*f['vm'])&(rvol>=1.5)&mkt
        h4=(move>=.06)&(move<=.12)&((f['c']/f['o'][0]-1)*side>=.03)&(f['change3']*side>=.003)&(c>ph)&(c>vw)&(dist<=.02)&((peak-c)/f['c']<=.008)&(rvol>=2)&mkt
        prevlow=np.r_[np.nan,l[:-1]];prevclose=np.r_[np.nan,c[:-1]];orlow=min(l[:3])
        # H5 follows a failed opposite-side breakout (long buys failed downside).
        h5=(prevlow<orlow)&(prevclose>=orlow)&(c>prevhigh)&(move>=-.05)&(move<=-.005)&(rvol>=1.5)&(f['change3']*side>0)&(move-mr>=0)
        masks={('H1','main'):ignition&(rvol>=2)&mkt&(move-mr>=.015),
               ('H1','price_only'):ignition&mkt&(move-mr>=.015),
               ('H1','no_market'):ignition&(rvol>=2),
               ('H1','peers'):ignition&(rvol>=2)&mkt&(move-mr>=.015)&(np.asarray(peer)*side>=.002) if peer is not None else np.zeros(n,dtype=bool),
               ('H2','main'):h2,('H2','no_failure'):h2,('H4','main'):h4,('H5','main'):h5,
               ('B8','baseline'):(move>=.08)&(rvol>=1.5)&(c>vw),
               ('B10','baseline'):(move>=.10)&(rvol>=1.5)&(c>vw)}
        for (family,variant),mask in masks.items():
            if side==-1 and variant!='main':continue
            first=family in ('H1','H5','B8','B10')
            for i in np.flatnonzero(common&mask):
                known=times[i]+pd.Timedelta(minutes=5);clock=known.strftime('%H:%M')
                low='09:35' if family=='H1' else '10:00' if family=='H4' else '09:30' if family.startswith('B') else '09:45'
                high='11:30' if family in ('H1','B8','B10') else '13:30'
                if not low<=clock<=high:continue
                result.append(dict(key=record['key'],symbol=record['symbol'],day=record['day'],family=family,variant=variant,side=side,
                    known_at=known.isoformat(),index=int(i),raw_price=float(f['c'][i]),score=float(abs(move[i])*min(rvol[i],10)),
                    move=float(f['move'][i]),rvol=float(rvol[i]),atr=float(f['atr'][i]),
                    swing_stop=float(f['pl'][i] if side==1 else f['ph'][i]) if np.isfinite(f['pl'][i] if side==1 else f['ph'][i]) else None,
                    vwap_distance=float(dist[i]),market_return=float(market['return'][i]),market_vol=float(market['lag_vol']),
                    peer_return=float(peer[i]) if peer is not None and np.isfinite(peer[i]) else None,
                    gap=float(f['o'][0]/record['prev_close']-1),intraday_move=float(f['c'][i]/f['o'][0]-1),
                    efficiency=float(f['efficiency'][i]),adv=record['adv'],sector=record['sector']))
                if first:break
    return result


def distances(s,cfg):
    if cfg.exit=='F':return .005,.01,60
    if cfg.exit=='B':return .01,.01,60
    stop=(s['raw_price']-s['swing_stop'])*s['side']/s['raw_price']+.001 if cfg.exit=='S' else 1.5*s['atr']/s['raw_price']
    if not np.isfinite(stop) or not .003<=stop<=.012:return None
    return stop,min(.02,max(.0075,2*stop)) if cfg.exit=='S' else .02,90 if cfg.exit=='S' else 120


def fill(record,s,q,cfg,dist,equity,risk_room):
    bars=record['bars'];wanted=pd.Timestamp(s['known_at'])+pd.Timedelta(minutes=cfg.delay*5)
    if wanted not in bars.index or wanted.strftime('%H:%M')>'13:30':return None,'entry_unavailable'
    i=bars.index.get_loc(wanted);a=bars.to_numpy(float);side=s['side'];enter='BUY' if side==1 else 'SELL';leave='SELL' if side==1 else 'BUY'
    if a[i,4]<=0:return None,'unobserved_entry'
    entry=adverse_price(float(a[i,0]),enter,cfg.slippage_bps)
    if side*(entry/s['raw_price']-1)>.003+1e-12:return None,'chase_limit'
    stopfrac,targetfrac,hold=dist;stop=entry*(1-side*stopfrac);initialstop=stop;target=entry*(1+side*targetfrac)
    ef=fees(enter,entry,q);stopfill=adverse_price(stop,leave,cfg.slippage_bps)
    risk=max(0,side*(entry-stopfill))*q+ef['total']+fees(leave,stopfill,q)['total']
    if entry*q+ef['total']>equity or risk>risk_room+1e-8:return None,'entry_cash_or_risk'
    due=min(wanted+pd.Timedelta(minutes=hold),wanted.normalize()+pd.Timedelta(hours=15,minutes=10))
    if due not in bars.index:raise ValueError('Missing scheduled exit '+record['key']+' '+str(due))
    feat=record['_features'];pending=False;reason=None;amb=False
    for j in range(i,len(a)):
        at=bars.index[j];o,h,l,c,v=a[j]
        if at>=due or pending:raw=float(o);reason='MOMENTUM_FAILURE' if pending else 'TIME_EXIT';release=at;break
        sh=l<=stop if side==1 else h>=stop;th=h>=target if side==1 else l<=target
        if sh or th:
            amb=bool(sh and th)
            raw=float(min(o,stop) if side==1 else max(o,stop)) if sh else target
            reason='STOP_FIRST_AMBIGUOUS' if amb else 'STOP' if sh else 'TARGET';release=at+pd.Timedelta(minutes=5);break
        if cfg.exit in ('S','A') and cfg.variant!='no_failure' and j>=2:
            pending=(side*(c-feat['vwap'][j])<0 and side*(a[j-1,3]-feat['vwap'][j-1])<0 and feat['change3'][j]*side<0)
        if cfg.exit=='A' and side*(c-entry)>=entry*stopfrac:
            proposed=c-side*1.5*feat['atr'][j]
            stop=max(stop,proposed) if side==1 else min(stop,proposed)
    if reason is None or v<=0:raise ValueError('Unobserved exit '+record['key']+' '+record['day'])
    xfprice=adverse_price(raw,leave,cfg.slippage_bps);xf=fees(leave,xfprice,q);gross=side*(xfprice-entry)*q
    return dict(strategy=cfg.name,instrument_key=record['key'],symbol=record['symbol'],session=record['day'],
        decision_at=s['known_at'],entry_at=wanted.isoformat(),exit_bar_at=at.isoformat(),capital_released_at=release.isoformat(),
        side='LONG' if side==1 else 'SHORT',quantity=q,entry_price=entry,exit_price=xfprice,raw_entry_price=float(a[i,0]),raw_exit_price=raw,
        initial_stop=initialstop,final_stop=stop,target_price=target,planned_loss_at_entry=risk,
        entry_fee_components=ef,exit_fee_components=xf,fees=ef['total']+xf['total'],gross_pnl=gross,net_pnl=gross-ef['total']-xf['total'],
        gross_before_slippage=side*(raw-a[i,0])*q,slippage_rupees=(abs(entry-a[i,0])+abs(xfprice-raw))*q,
        reason=reason,ambiguous=amb,decision_bar_participation=q/a[s['index'],4],entry_bar_participation=q/a[i,4],exit_bar_participation=q/v,
        holding_minutes=(release-wanted).total_seconds()/60,signal_features=s), 'filled'


def run(records,all_signals,calendar,cfg):
    lookup={(r['day'],r['key']):r for r in records};events={}
    for s in all_signals:
        if s['family']==cfg.family and s['variant']==cfg.variant and s['side']==cfg.direction and s['day'] in calendar:
            events.setdefault(s['day'],[]).append(s)
    equity=cfg.capital;peak=equity;trades=[];days=[];reject=[]
    for day in calendar:
        opening=equity;used=set();busy=None;count=0;daypnl=0
        for s in sorted(events.get(day,[]),key=lambda x:(x['known_at'],-x['score'],x['key'])):
            tag=None;known=pd.Timestamp(s['known_at']);dist=None
            if busy is not None and known<busy:tag='position_open'
            elif daypnl<=-opening*.01:tag='daily_loss_budget'
            elif count>=3:tag='daily_trade_cap'
            elif s['key'] in used:tag='symbol_reentry'
            else:
                dist=distances(s,cfg)
                if dist is None:tag='stop_distance_outside_bounds'
            if tag is None:
                rec=lookup[(day,s['key'])];sizecfg=SizeConfig('v2',stop=dist[0],target=dist[1],chase_limit=.003,slippage_bps=cfg.slippage_bps,participation=cfg.participation)
                q=planned_size(s,rec['bars'].iloc[s['index']],equity,daypnl,opening,sizecfg)
                if q<=0:tag='size_zero'
                else:
                    trade,tag=fill(rec,s,q,cfg,dist,equity,min(equity*.005,opening*.01+daypnl))
                    if trade:
                        trade['equity_before']=equity;equity+=trade['net_pnl'];daypnl+=trade['net_pnl'];trade['equity_after']=equity
                        trades.append(trade);busy=pd.Timestamp(trade['capital_released_at']);used.add(s['key']);count+=1
            reject.append(dict(strategy=cfg.name,day=day,key=s['key'],known_at=s['known_at'],status=tag))
        peak=max(peak,equity);days.append(dict(session=day,equity=equity,pnl=equity-opening,return_fraction=equity/opening-1,trades=count,drawdown=equity/peak-1))
    return dict(name=cfg.name,config=asdict(cfg),trades=trades,daily=days,rejections=reject)
