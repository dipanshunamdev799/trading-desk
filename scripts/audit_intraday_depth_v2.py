"""Predeclared one-stock/day paired depth feasibility; never a trading bot."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import hashlib,json
import numpy as np
import pandas as pd
from research.intraday_momentum import data as base
from research.intraday_momentum_v2.data import OUT
from research.intraday_momentum_v2.capture import book_features
from research.intraday_momentum.costs import fees


def main():
    frozen={'script':base.sha(Path(__file__)),'definition':base.sha(ROOT/'research/intraday_momentum_v2/H3_DIAGNOSTIC.md')}
    rows=[];h=hashlib.sha256()
    with base.connection() as c:
        c.execute("SET LOCAL statement_timeout='60s'")
        c.execute("SELECT source_at,received_at,payload FROM market_stream_ticks WHERE instrument_key=%s AND source_at>=%s AND source_at<%s ORDER BY source_at,received_at",('NSE_EQ|INE002A01018','2026-11-13 09:15+05:30','2026-11-13 15:10+05:30'))
        source=c.fetchall()
    for r in source:
        raw=r['payload'];h.update(json.dumps(raw,sort_keys=True).encode());h.update((str(r['source_at'])+str(r['received_at'])).encode())
        full=(raw.get('fullFeed') or {}).get('marketFF') or {};levels=(full.get('marketLevel') or {}).get('bidAskQuote') or []
        f=book_features(raw,r['received_at'],int(r['source_at'].timestamp()*1000))
        if not levels or not f['best_bid'] or not f['best_ask'] or f['spread_bps'] is None:continue
        rows.append(dict(at=max(r['source_at'],r['received_at']),source_at=r['source_at'],mid=(f['best_bid']+f['best_ask'])/2,bid=f['best_bid'],ask=f['best_ask'],
            aq=float(levels[0].get('askQ',0)),imb=f['depth_imbalance'],spread=f['spread_bps'],volume=float(f['traded_volume'] or 0)))
    if not rows:
        base.dump(OUT/'depth-diagnostic.json',dict(status='NO_USABLE_BOOK',raw_rows=len(source),code=frozen));return
    frame=pd.DataFrame(rows).drop_duplicates('at',keep='last').set_index('at').sort_index();frame.index=frame.index.tz_convert('Asia/Kolkata')
    grid=pd.date_range('2026-11-13 09:15','2026-11-13 15:10',freq='s',tz='Asia/Kolkata')
    aligned=frame.reindex(grid,method='ffill');age=(aligned.index-aligned['source_at']).dt.total_seconds()
    fresh=(age<=2)&(age>=0)&(aligned.ask>=aligned.bid)&(aligned.bid>0)
    aligned.loc[~fresh,['mid','bid','ask','volume','imb','spread','aq']]=np.nan
    x=pd.DataFrame(index=grid);x['r60']=aligned.mid.pct_change(60,fill_method=None)*1e4;x['r5']=aligned.mid.pct_change(5,fill_method=None)*1e4
    delta=aligned.volume-aligned.volume.shift(60);x['v60']=np.log1p(delta.where(delta>=0));x['imb']=aligned.imb;x['spread']=aligned.spread
    x['imb_mean5']=aligned.imb.rolling(5,min_periods=5).mean();x['imb_std5']=aligned.imb.rolling(5,min_periods=5).std()
    y=(aligned.mid.shift(-30)/aligned.mid-1)*1e4
    episodes=(np.arange(len(grid))%30==0);valid=np.isfinite(x).all(axis=1)&np.isfinite(y)
    train=valid&episodes&(grid.strftime('%H:%M')>='09:16')&(grid.strftime('%H:%M')<='11:59')
    test=valid&episodes&(grid.strftime('%H:%M')>='13:00')&(grid.strftime('%H:%M')<='15:00')
    predictions=[];metrics=[];ys=y.loc[test].to_numpy()
    for label,cols in [('price',['r60','r5']),('price_volume',['r60','r5','v60']),('price_volume_depth',list(x.columns))]:
        a=x.loc[train,cols].to_numpy();b=x.loc[test,cols].to_numpy();mu=a.mean(axis=0);sd=a.std(axis=0);sd=np.where(sd>1e-12,sd,1.)
        a=np.c_[np.ones(len(a)),(a-mu)/sd];b=np.c_[np.ones(len(b)),(b-mu)/sd];penalty=np.eye(a.shape[1]);penalty[0,0]=0
        coeff=np.linalg.solve(a.T@a+penalty,a.T@y.loc[train].to_numpy());pred=b@coeff
        markouts=[]
        for at,p in zip(x.index[test],pred):
            z=aligned.loc[at];q=max(0,min(int(100000/z.ask),int(delta.loc[at]*.01),int(z.aq*.1)))
            expectedfees=(fees('BUY',float(z.ask),q)['total']+fees('SELL',float(z.bid),q)['total'])/(z.ask*q)*1e4 if q else np.inf
            take=q>0 and p>float(z.spread)+expectedfees+2+10
            net=None
            if take:
                entry=float(z.ask)*1.0001;exit=float(aligned.loc[at+pd.Timedelta(seconds=30),'bid'])*.9999
                net=((exit-entry)*q-fees('BUY',entry,q)['total']-fees('SELL',exit,q)['total'])/(entry*q)*1e4;markouts.append(net)
            predictions.append(dict(model=label,at=at.isoformat(),prediction_bps=float(p),actual_mid_return_bps=float(y.loc[at]),eligible_quote_markout=bool(take),quantity=q,net_markout_bps=net))
        metrics.append(dict(model=label,train_episodes=int(train.sum()),test_episodes=int(test.sum()),mae_bps=float(np.mean(abs(pred-ys))),
            correlation=float(np.corrcoef(pred,ys)[0,1]) if np.std(pred)>0 and np.std(ys)>0 else None,directional_accuracy=float(np.mean((pred>0)==(ys>0))),
            eligible_long_quote_markouts=len(markouts),mean_net_markout_bps=float(np.mean(markouts)) if markouts else None))
    result=dict(status='ONE_STOCK_DAY_FEASIBILITY_ONLY',classification='FORWARD_DATA_REQUIRED',source_rows=len(source),usable_book_updates=len(rows),fresh_grid_fraction=float(fresh.mean()),
        source_sha256=h.hexdigest(),code=frozen,metrics=metrics,stock='RELIANCE',day='2026-11-13',independent_days=1,
        limitation='Exposed retrospective single stock/day, conditional complete episodes, not portfolio returns, no fill guarantee or day-level inference')
    result['availability_policy']='As of max(source_at,received_at), never source clock alone'
    base.dump(OUT/'depth-diagnostic-asof.json',result);pd.DataFrame(predictions).to_csv(OUT/'depth-predictions-asof.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
