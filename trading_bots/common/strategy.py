from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Definition:
    id: str
    name: str
    description: str
    rank: int
    filter: str
    window: str
    parameters: dict
    hold_minutes: int = 60

    def json(self): return asdict(self)


def features(candles, at):
    """Same causal feature definitions as the frozen research, with input checks."""
    d=pd.DataFrame(candles)
    if d.empty: raise ValueError('No candles available')
    d['ts']=pd.to_datetime(d.ts,utc=True).dt.tz_convert('Asia/Kolkata')
    d=d[d.ts+pd.Timedelta(minutes=5)<=pd.Timestamp(at)].sort_values('ts',kind='stable')
    if (d.groupby('ts')[['open','high','low','close']].nunique()>1).any().any():raise ValueError('Conflicting candle revisions')
    d=d.drop_duplicates('ts');d['day']=d.ts.dt.strftime('%Y-%m-%d')
    minute=d.ts.dt.hour*60+d.ts.dt.minute;d=d[(minute>=555)&(minute<910)].copy()
    if d.empty:raise ValueError('No completed research-session candles')
    if not np.isfinite(d[['open','high','low','close']]).all().all() or not (d.low>0).all() or not (d.high>=d[['open','low','close']].max(axis=1)).all() or not (d.low<=d[['open','high','close']].min(axis=1)).all():raise ValueError('Invalid OHLC')
    today=pd.Timestamp(at).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
    accepted=[]
    for day,g in d.groupby('day'):
        clock=list(g.ts.dt.hour*60+g.ts.dt.minute)
        expected=list(range(555,clock[-1]+5,5))
        if clock!=expected or (g.ts.dt.second!=0).any():
            if day==today:raise ValueError('Missing or misaligned current-session candles')
            continue
        if day==today or len(clock)==71:accepted.append(day)
    d=d[d.day.isin(accepted)].reset_index(drop=True)
    if d.empty:raise ValueError('No complete context sessions')
    g=d.groupby('day');d['minute']=d.ts.dt.hour*60+d.ts.dt.minute;d['known_at']=d.ts+pd.Timedelta(minutes=5)
    prior=g.close.shift();tr=pd.concat([d.high-d.low,(d.high-prior).abs(),(d.low-prior).abs()],axis=1).max(axis=1)
    d['atr']=tr.shift().rolling(14,min_periods=14).mean();d['vol_ratio']=d.atr/d.atr.shift().rolling(200,min_periods=100).median()
    delta=g.close.diff();gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean();loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean();d['rsi']=100*gain/(gain+loss)
    for n in [5,9,12,21,26,50]:d[f'ema{n}']=d.close.ewm(span=n,adjust=False).mean()
    for n in [3,6,12,20]:
        d[f'ret{n}']=g.close.diff(n)/d.atr
        d[f'high{n}']=g.high.transform(lambda s:s.shift().rolling(n,min_periods=n).max())
        d[f'low{n}']=g.low.transform(lambda s:s.shift().rolling(n,min_periods=n).min())
    d['efficiency']=g.close.diff(12).abs()/delta.abs().groupby(d.day).transform(lambda s:s.rolling(12,min_periods=12).sum())
    d['trend']=(d.ema9-d.ema21)/d.atr;d['distance']=(d.close-d.ema21)/d.atr;d['body']=(d.close-d.open)/d.atr
    for n in [15,30,60]:
        h=d.high.where(d.minute<555+n).groupby(d.day).cummax().groupby(d.day).ffill()
        l=d.low.where(d.minute<555+n).groupby(d.day).cummin().groupby(d.day).ffill()
        d[f'orb_high{n}']=h.where(d.minute+5>=555+n);d[f'orb_low{n}']=l.where(d.minute+5>=555+n)
    d['session_open']=g.open.transform('first');d['prev_research_close']=d.day.map(g.close.last().shift());d['gap']=(d.session_open-d.prev_research_close)/d.atr
    return d


def direction(long,short):return np.where(long & ~short,1,np.where(short & ~long,-1,0)).astype(np.int8)


def eligible(f,side,definition):
    filters={'trend':(f.efficiency>=.35)&(f.trend.abs()>=.5),'range':f.efficiency<.25,
        'ema_aligned':side*f.trend>0,'normal_vol':f.vol_ratio<1.2,'high_vol':f.vol_ratio>=1.2,'none':np.ones(len(f),bool)}
    windows={'all':f.minute>=570,'morning':(f.minute>=570)&(f.minute<660),'afternoon':f.minute>=780}
    return np.where(filters[definition.filter]&windows[definition.window]&f.atr.gt(0),side,0).astype(np.int8)
