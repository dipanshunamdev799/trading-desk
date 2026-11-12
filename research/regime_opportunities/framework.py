from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from research.ema_validation.engine import prepare,ROOT,OLD
from research.swing.data import _frame
from research.swing_discovery.signals import build_features,generate,smooth,lag
from research.swing_diagnosis.common import clean

OUT=ROOT/'artifacts/regime_opportunities'
PERIODS={'development':('2024-11-10','2025-11-10'),'validation':('2025-11-10','2026-05-10'),'final':('2026-05-10','2026-11-10'),'two_year':('2024-11-10','2026-11-10')}
def save(name,x):
    OUT.mkdir(exist_ok=True,parents=True);(OUT/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False),encoding='utf-8')

def rolling(x,n,method='mean'):return getattr(pd.Series(x).rolling(n,min_periods=n),method)().to_numpy()
def prior_median(x):return pd.Series(x).rolling(252,min_periods=126).median().shift().to_numpy()

def classify(market,sector,stock=None):
    dates=market.index;c=market.close.to_numpy();o=market.open.to_numpy();r=pd.Series(c,index=dates).pct_change().to_numpy()
    p={'dates':dates,'symbols':['NIFTY'],'neutral':{k:market[k].to_numpy()[None,:] for k in ['open','high','low','close','volume']},'nifty':c,'sector':['index']}
    f=build_features(p);vol20=rolling(r,20,'std');vol60=rolling(r,60,'std');ratio=vol20/vol60;ema20=smooth(c[None,:],20)[0];ema50=smooth(c[None,:],50)[0];ema200=smooth(c[None,:],200)[0]
    efficiency=abs(c-np.r_[np.full(60,np.nan),c[:-60]])/rolling(abs(np.r_[np.nan,np.diff(c)]),60,'sum')
    states={};definitions=[];features={}
    def add(name,dimension,v,condition,rule,scope='index_long'):
        v=np.asarray(v,float);states[name]=np.isfinite(v)&condition;features[name]=v
        definitions.append(dict(regime=name,dimension=dimension,rule=rule,scope=scope))
    add('vol_expansion','volatility_ratio',ratio,ratio>1.2,'std20/std60>1.2')
    add('vol_contraction','volatility_ratio',ratio,ratio<.8,'std20/std60<.8')
    med=prior_median(vol20);v=vol20-med
    add('high_volatility','volatility_level',v,v>0,'vol20>prior252median(min126)')
    add('low_volatility','volatility_level',v,v<=0,'vol20<=prior252median(min126)')
    adx=f['adx'][0];add('strong_adx','ADX',adx,adx>=25,'WilderADX14>=25');add('weak_adx','ADX',adx,adx<20,'WilderADX14<20')
    valid=np.where(np.isfinite(ema200),c,np.nan);bull=(c>ema200)&(ema50>ema200);bear=(c<ema200)&(ema50<ema200)
    for name,condition in [('bull_trend',bull),('bear_trend',bear),('mixed_trend',~bull&~bear)]:add(name,'trend',valid,condition,name+' close/EMA50/EMA200 alignment')
    add('efficient_trend','efficiency',efficiency,efficiency>=.3,'ER60>=.3');add('inefficient_range','efficiency',efficiency,efficiency<=.15,'ER60<=.15')
    positive=rolling((r>0).astype(float),20)
    add('persistent_up','persistence',positive,positive>=.65,'positive20dayfraction>=.65');add('persistent_down','persistence',positive,positive<=.35,'positive20dayfraction<=.35')
    z=(c-ema20)/f['atr'][0];add('market_oversold','reversion',z,z<=-2,'(close-EMA20)/ATR14<=-2');add('market_overbought','reversion',z,z>=2,'(close-EMA20)/ATR14>=2')
    age=np.zeros(len(c),int)
    for t in range(len(c)):age[t]=(age[t-1]+1 if t else 1) if ratio[t]>1.2 else 0
    add('new_expansion','transition',ratio,(age==1),'first expansion session');add('persistent_expansion','transition',ratio,age>=5,'expansion age>=5sessions')
    cluster=pd.Series(r*r).rolling(60,min_periods=60).corr(pd.Series(r*r).shift()).to_numpy()
    add('vol_clustered','vol_clustering',cluster,cluster>0,'lag1squaredreturncorr60>0');add('vol_unclustered','vol_clustering',cluster,cluster<=0,'lag1squaredreturncorr60<=0')
    gap=abs(o/np.r_[np.nan,c[:-1]]-1);gf=rolling((gap>.01).astype(float),20)
    add('frequent_market_gaps','overnight',gf,gf>=.2,'fraction20absmarketgap>1%>=.2');add('infrequent_market_gaps','overnight',gf,gf<.2,'fraction20absmarketgap>1%<.2')
    sec=sector.reindex(dates).to_numpy();ret=sec/np.vstack([np.full((60,sec.shape[1]),np.nan),sec[:-60]])-1;spread=np.nanmax(ret,axis=1)-np.nanmin(ret,axis=1);delta=spread-prior_median(spread)
    add('sector_rotation_wide','sector_rotation',delta,delta>0,'Bank/IT/Pharma60returnspread>prior252median(min126)')
    lead=np.argmax(np.where(np.isfinite(ret),ret,-np.inf),axis=1);shiftlead=np.r_[np.full(20,-1),lead[:-20]];validsec=np.where(np.isfinite(ret).all(axis=1),spread,np.nan)
    add('sector_leader_changed','sector_rotation',validsec,lead!=shiftlead,'leading3sector60returnindex differs20sessionsago')
    if stock is not None:
        panel,sf=stock;cstock=panel['neutral']['close'][panel['eligible']];vstock=panel['neutral']['volume'][panel['eligible']];rstock=cstock/np.roll(cstock,1,axis=1)-1;rstock[:,0]=np.nan
        def align(x):
            a=pd.Series(x,index=panel['dates']).reindex(dates).to_numpy(copy=True);a[dates<pd.Timestamp('2024-11-10',tz=dates.tz)]=np.nan;return a
        for n in [20,50,200]:
            e=smooth(cstock,n);finite=np.isfinite(e)&np.isfinite(cstock);breadth=np.divide(((cstock>e)&finite).sum(axis=0),finite.sum(axis=0),out=np.full(cstock.shape[1],np.nan),where=finite.sum(axis=0)>=.8*len(cstock))
            b=align(breadth);add(f'breadth{n}_broad','breadth',b,b>=.7,f'fractionaboveEMA{n}>=.7','stock_recent');add(f'breadth{n}_narrow','breadth',b,b<=.3,f'fractionaboveEMA{n}<=.3','stock_recent')
            if n==50:
                change=breadth-np.r_[np.full(20,np.nan),breadth[:-20]];bc=align(change)
                add('breadth_improving','breadth_transition',bc,bc>=.1,'breadth50change20>=.10','stock_recent');add('breadth_deteriorating','breadth_transition',bc,bc<=-.1,'breadth50change20<=-.10','stock_recent')
        dispersion=rolling(np.nanstd(rstock,axis=0,ddof=1),20);d=align(dispersion-prior_median(dispersion))
        add('high_dispersion','dispersion',d,d>0,'mean20crosssectionretstd>prior252median(min126)','stock_recent');add('low_dispersion','dispersion',d,d<=0,'mean20crosssectionretstd<=prior252median(min126)','stock_recent')
        mr=pd.Series(panel['niftyclose']).pct_change();corr=[]
        for row in rstock:corr.append(pd.Series(row).rolling(60,min_periods=60).corr(mr).to_numpy())
        cm=np.nanmedian(corr,axis=0);delta=align(cm-prior_median(cm))
        add('high_market_correlation','correlation',delta,delta>0,'medianstockNIFTYcorr60>prior252median(min126)','stock_recent');add('low_market_correlation','correlation',delta,delta<=0,'medianstockNIFTYcorr60<=prior252median(min126)','stock_recent')
        volmean=pd.DataFrame(vstock.T).rolling(20,min_periods=20).mean().shift().to_numpy().T;participation=align(np.nanmedian(vstock/volmean,axis=0))
        add('high_volume_participation','activity',participation,participation>=1.25,'medianstockvolume/meanprior20>=1.25','stock_recent');add('low_volume_participation','activity',participation,participation<=.75,'medianstockvolume/meanprior20<=.75','stock_recent')
    return states,features,definitions

def build():
    q=prepare();p=q['p'];old=ROOT/'artifacts/swing_diagnosis/benchmark_raw/history-probe-NIFTY.json'
    parts=[_frame(json.loads(old.read_text())),_frame(json.loads((OLD/'raw/NIFTY/daily.json').read_text()))]
    market=pd.concat(parts).sort_index();market.index=market.index.normalize();market=market[~market.index.duplicated(keep='last')]
    hist=pd.read_csv(ROOT/'artifacts/swing_diagnosis/benchmark-tri-history.csv');hist['day']=pd.to_datetime(hist.day).dt.tz_localize('Asia/Kolkata');tri=hist.pivot(index='day',columns='index',values='value').reindex(market.index)
    sf=build_features(p);states,features,definitions=classify(market,tri[['Nifty Bank','Nifty IT','Nifty Pharma']],(p,sf))
    entries={}
    for name,cfg in [('momentum',dict(family='donchian_breakout',lookback=20,break_buffer=0)),('EMA',dict(family='ema_cross',fast=20,slow=50)),('MACD',dict(family='macd_cross',fast=12,slow=26,signal=9)),('support',dict(family='pivot_bounce',pivot=2,zone=.5))]:
        entries[name]=generate(p,{**cfg,'filter':'none'},sf)['entry']&q['pool']
    rsi=sf['rsi'];entries['meanreversion']=(rsi<30)&(lag(rsi)>=30)&q['pool'];entries['buyhold10']=q['pool'].copy()
    universe=json.loads((OLD/'universe.json').read_text())['stocks'];isin={x['symbol']:x['isin_at_start'] for x in universe};rank=np.stack(q['ranks'])
    for t in q['cols']:
        day=str(p['dates'][t-1].date());rank[t]=sorted(range(len(p['symbols'])),key=lambda s:hashlib.sha256((day+'|'+isin[p['symbols'][s]]+'|regime_reference20261112').encode()).digest())
    masks={'universal':np.ones(len(p['dates']),bool)}
    for name in states:masks[name]=pd.Series(states[name],index=market.index).reindex(p['dates']).fillna(False).to_numpy(bool)
    arrays={f'entry_{k}':v for k,v in entries.items()}|{f'mask_{k}':v for k,v in masks.items()};arrays['ranks']=rank
    np.savez_compressed(OUT/'portfolio-inputs.npz',**arrays);market.to_csv(OUT/'market-OHLC.csv');tri.to_csv(OUT/'official-TRI.csv')
    values=pd.DataFrame(features,index=market.index);labels=pd.DataFrame(states,index=market.index);values.to_csv(OUT/'regime-features.csv');labels.to_csv(OUT/'regime-labels.csv')
    save('definitions.json',definitions);save('data-scope.json',dict(index_sessions=len(market),index_first=str(market.index[0]),index_last=str(market.index[-1]),stock_count=int(p['eligible'].sum()),stock_start='2024-11-11',stock_end='2026-11-09',regimes=len(definitions),
      stock_history_limit='No stockportfolio orcrosssection inferential performance beforedated2024cohort; priorpriceswarmup only. Futurecompletenessselectioninherited.',sector_limit='Official3sectorTRIproxy; allothersectorresultscohortproxies, nothistoricalsectorindices.'))
    return q,market,tri,states,definitions
