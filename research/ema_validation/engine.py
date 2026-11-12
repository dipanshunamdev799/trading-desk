"""Cached scalar funded replay of frozen portfolio; validated against original."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from research.swing_diagnosis.common import ROOT,OLD,load_panel,clean
from research.swing_discovery.signals import build_features,generate
from research.swing_discovery.engine import fee_coeff
from research.swing_discovery.diagnostics import portfolio_metrics

OUT=ROOT/'artifacts/ema_validation'
REASONS=['gap_stop','gap_target','time','stop','target','segment_end']
TRADE_COLUMNS=['stock','signal_t','entry_t','exit_t','entry','entry_q','exit','exit_q','net_pnl','fees','initial_risk','net_r','reason','dividends']

def save(name,x):
    OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False),encoding='utf-8')

def prepare():
    p=load_panel()
    with np.load(ROOT/'artifacts/swing_diagnosis/audit-dividend-corrected.npz') as a:p['dividend']=a['dividend'].copy()
    f=build_features(p);cfg=next(x['config'] for x in json.loads((OLD/'frozen-finalists.json').read_text())['finalists'] if x['family']=='ema_cross')
    sig=generate(p,cfg,f);unfiltered=generate(p,{**cfg,'filter':'none','params':{**cfg['params'],'filter':'none'}},f)
    c=p['neutral']['close'];r=c/np.roll(c,1,axis=1)-1;r[:,0]=np.nan
    market=pd.Series(p['niftyclose']);mr=market.pct_change();ratio=(mr.rolling(20).std()/mr.rolling(60).std()).to_numpy()
    rs=f['return60']>f['market_return60'];ema=unfiltered['entry']&p['eligible'][:,None]
    # Exact baseline comes from the previously frozen signal generator.
    assert np.array_equal(sig['entry']&p['eligible'][:,None],ema&rs)
    pool=p['eligible'][:,None]&np.isfinite(c)&(c>0)&np.isfinite(f['atr'])&(f['atr']>0)
    ranks=[]
    for t in range(len(p['dates'])):
        rank=c[:,max(0,t-1)]/c[:,max(0,t-61)]-1
        order=sorted(range(len(c)),key=lambda s:(-rank[s] if np.isfinite(rank[s]) else np.inf,p['symbols'][s]));ranks.append(np.asarray(order))
    return dict(p=p,cfg=cfg,sig=sig,ema=ema,rs=rs,pool=pool,ratio=ratio,gate=ratio>1.2,
      returns=r,ranks=ranks,atr=sig['atr']*p['unit_factor'],fee=[fee_coeff(d,True,False) for d in p['dates']],
      sellfee=[fee_coeff(d,False,True) for d in p['dates']],corr={},cols=np.flatnonzero((p['dates']>=pd.Timestamp('2024-11-10',tz=p['dates'].tz))&(p['dates']<pd.Timestamp('2026-11-10',tz=p['dates'].tz))))

def cache_correlations(q):
    """Complete prior windows use normalized dot-products, missing pairs fallback."""
    for t in q['cols']:
        v=q['returns'][:,max(1,t-60):t];finite=np.isfinite(v).all(axis=1)
        z=np.where(np.isfinite(v),v,0.);z-=z.mean(axis=1)[:,None];norm=np.sqrt((z*z).sum(axis=1))
        z=np.divide(z,norm[:,None],out=np.zeros_like(z),where=norm[:,None]>0)
        q['corr'][t]=(z@z.T>.8,finite)

def correlated(q,t,s,other):
    high,finite=q['corr'][t]
    if finite[s] and finite[other]:return bool(high[s,other])
    a=q['returns'][s,max(1,t-60):t];b=q['returns'][other,max(1,t-60):t];valid=np.isfinite(a)&np.isfinite(b)
    return valid.sum()>=40 and np.std(a[valid])>0 and np.std(b[valid])>0 and np.corrcoef(a[valid],b[valid])[0,1]>.8

def orders(q,mask):
    return [order[mask[order,t-1]] if t>0 else np.array([],int) for t,order in enumerate(q['ranks'])]

def simulate(q,ordered,start='2024-11-10',end='2026-11-10',cost=1.,slip_bps=5,exclude=None,force_end=True):
    p=q['p'];dates=p['dates'];lo=pd.Timestamp(start,tz=dates.tz);hi=pd.Timestamp(end,tz=dates.tz)
    cols=np.flatnonzero((dates>=lo)&(dates<hi));a=p['actual'];o,h,l,c=(a[k] for k in ['open','high','low','close'])
    split=p['split_factor'];div=p['dividend'];volume=p['liquidity_volume'];turn=p['liquidity_turnover'];sectors=p['sector']
    slip=slip_bps/10000;cash=1e6;positions={};trades=[];nav=[];cashpath=[];util=[];count=[];turnover=0.;fees_total=0.;reject={};candidates=0
    def close(s,price,t,why):
        nonlocal cash,turnover,fees_total
        z=positions.pop(s);sr,sf=q['sellfee'][t];sf-=23.6 if z['t']==t else 0
        fee=(price*z['q']*sr+sf)*cost;refund=cost*(z['notional']*.00112+price*z['q']*.00075) if z['t']==t else 0.
        proceeds=price*z['q']-fee+refund;cash+=proceeds;turnover+=price*z['q'];fees_total+=fee-refund
        net=proceeds-z['notional']-z['ef']+z['div'];risk=z['risk']
        trades.append([s,z['t']-1,z['t'],t,z['original'],z['original_q'],price,z['q'],net,z['ef']+fee-refund,risk,net/risk,why,z['div']])
    def rejection(k):reject[k]=reject.get(k,0)+1
    for j,t in enumerate(cols):
        had=set(positions);prev=t-1
        for s in list(positions):
            z=positions[s];factor=split[s,t];qty=z['q']*factor
            if abs(qty-round(qty))>1e-7:raise ValueError('Fractional entitlement')
            z['q']=int(round(qty));z['stop']/=factor;z['target']/=factor
            dividend=z['q']*div[s,t];cash+=dividend;z['div']+=dividend
            if o[s,t]<=z['stop']:close(s,o[s,t]*(1-slip),t,0)
            elif o[s,t]>=z['target']:close(s,z['target']*(1-slip),t,1)
            elif t-z['t']>=10:close(s,o[s,t]*(1-slip),t,2)
        held={s:z['q']*c[s,prev]/split[s,t] for s,z in positions.items()};budget=cash+sum(held.values())
        if prev>=0 and dates[prev]>=lo:
            for s0 in ordered[t]:
                s=int(s0);candidates+=1
                if exclude is not None and s==exclude:rejection('excluded');continue
                if s in had or s in positions:rejection('held');continue
                if len(positions)>=10:rejection('positions');continue
                atr=q['sig']['atr'][s,prev]*p['unit_factor'][s,t];en=o[s,t]*(1+slip);st=en-2*atr
                if not np.isfinite(en+atr+st) or atr<=0 or st<=0:rejection('price');continue
                if turn[s,t]<50e6 or not np.isfinite(volume[s,t]):rejection('liquidity');continue
                if any(correlated(q,t,s,k) for k in positions):rejection('correlation');continue
                br,bf=q['fee'][t];sr,sf=q['sellfee'][t];br*=cost;bf*=cost;sr*=cost;sf*=cost
                stopfill=st*(1-slip);perrisk=en-stopfill+en*br+stopfill*sr
                desired=max(0,.005*budget-bf-sf)/perrisk
                sectorvalue=sum(held.get(k,z['q']*o[k,t]) for k,z in positions.items() if sectors[k]==sectors[s])
                qty=int(np.floor(min(desired,.2*budget/en,max(0,.3*budget-sectorvalue)/en,max(0,cash-bf)/(en*(1+br)),volume[s,t]*.01)))
                if qty<1:rejection('cash_sector_size');continue
                ef=en*qty*br+bf;risk=perrisk*qty+bf+sf;target=(en*qty+2*risk+ef+sf)/(qty*(1-sr))/(1-slip)
                cash-=en*qty+ef;turnover+=en*qty;fees_total+=ef
                positions[s]=dict(q=qty,original_q=qty,original=en,notional=en*qty,ef=ef,t=t,stop=st,target=target,risk=risk,div=0.);held[s]=en*qty
        for s in list(positions):
            z=positions[s]
            if l[s,t]<=z['stop']:close(s,z['stop']*(1-slip),t,3)
            elif h[s,t]>=z['target']:close(s,z['target']*(1-slip),t,4)
        if force_end and j==len(cols)-1:
            for s in list(positions):close(s,c[s,t]*(1-slip),t,5)
        value=sum(z['q']*c[s,t] for s,z in positions.items());equity=cash+value
        if cash< -1e-6 or len(positions)>10:raise AssertionError('Cash/position invariant')
        nav.append(equity);cashpath.append(cash);util.append(value/equity);count.append(len(positions))
    tr=np.asarray(trades,float).reshape(-1,len(TRADE_COLUMNS));nav=np.asarray(nav)
    if force_end and not np.isclose(nav[-1]-1e6,tr[:,8].sum(),atol=1e-6):raise AssertionError('Terminal cash/PnL identity')
    m=portfolio_metrics(pd.Series(nav,index=dates[cols]),len(tr));m.update(exposure_pct=100*np.mean(util),turnover_multiple=turnover/1e6,fees=fees_total,candidates=candidates,min_cash=min(cashpath),max_positions=max(count),rejections=reject)
    return dict(metrics=m,equity=nav,cash=np.asarray(cashpath),utilization=np.asarray(util),positions=np.asarray(count),trades=tr,cols=cols,open_positions=positions)
