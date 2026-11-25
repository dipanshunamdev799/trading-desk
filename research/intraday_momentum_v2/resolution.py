"""Fixed-entry 1m replay with original completed5m failure/trailing decisions."""
from pathlib import Path
import pandas as pd
from research.intraday_momentum import data as base
from research.intraday_momentum.units import restore_bars
from research.intraday_momentum.costs import adverse_price,fees


def replay(t,record,bars,cfg):
    entry=pd.Timestamp(t['entry_at']);side=1 if t['side']=='LONG' else -1
    hold=60 if cfg.exit in ('F','B') else 90 if cfg.exit=='S' else 120
    due=min(entry+pd.Timedelta(minutes=hold),entry.normalize()+pd.Timedelta(hours=15,minutes=10))
    if entry not in bars.index or due not in bars.index:return {'status':'missing_endpoint'}
    if abs(float(bars.loc[entry,'open'])-t['raw_entry_price'])>max(.02,t['raw_entry_price']*.0002):return {'status':'entry_open_mismatch'}
    stop=t['initial_stop'];target=t['target_price'];initialR=abs(t['entry_price']-stop);reason=None
    b5=record['bars'];f=record['_features']
    for at in pd.date_range(entry,due,freq='min'):
        if at not in bars.index:return {'status':'missing_path_minute','at':at.isoformat()}
        row=bars.loc[at];o=float(row['open']);pending=False
        completed=at-pd.Timedelta(minutes=5)
        if at>entry and completed in b5.index and at.minute%5==0:
            j=b5.index.get_loc(completed);close=float(b5.iloc[j]['close'])
            if cfg.exit in ('S','A') and cfg.variant!='no_failure' and j>=2:
                pending=side*(close-f['vwap'][j])<0 and side*(b5.iloc[j-1]['close']-f['vwap'][j-1])<0 and f['change3'][j]*side<0
            if cfg.exit=='A' and side*(close-t['entry_price'])>=initialR:
                proposed=close-side*1.5*f['atr'][j];stop=max(stop,proposed) if side==1 else min(stop,proposed)
        if pending or at>=due:raw=o;reason='MOMENTUM_FAILURE' if pending else 'TIME_EXIT';break
        sh=float(row['low'])<=stop if side==1 else float(row['high'])>=stop
        th=float(row['high'])>=target if side==1 else float(row['low'])<=target
        if sh or th:
            raw=(min(o,stop) if side==1 else max(o,stop)) if sh else target
            reason='STOP_FIRST_AMBIGUOUS' if sh and th else 'STOP' if sh else 'TARGET';break
    if reason is None or float(row['volume'])<=0:return {'status':'unobserved_exit'}
    leave='SELL' if side==1 else 'BUY';price=adverse_price(raw,leave,cfg.slippage_bps)
    net=side*(price-t['entry_price'])*t['quantity']-t['entry_fee_components']['total']-fees(leave,price,t['quantity'])['total']
    return dict(status='matched',reason_1minute=reason,net_pnl_1minute=net,net_pnl_5minute=t['net_pnl'],net_pnl_difference=net-t['net_pnl'],exit_bar_1minute=at.isoformat())


def audit(trades,records,out,cfg,count=20):
    out=Path(out);lookup={(r['day'],r['key']):r for r in records};rows=[]
    chosen=sorted([t for t in trades if '2025-01-01'<=t['session']<='2025-09-30'],key=lambda t:(t['entry_at'],t['instrument_key']))[:count]
    for t in chosen:
        key=t['instrument_key'];day=t['session'];path=out/'raw'/key.replace('|','_')/(day+'.json.gz')
        try:
            payload,cached=base._fetch(key,'minutes',1,day,day,path);imported=base.insert_raw(payload,key,'1minute',day,day)
            with base.connection() as c:
                c.execute("SELECT ts,open,high,low,close,volume FROM public.candles WHERE instrument_key=%s AND interval='1minute' AND source='upstox' AND ts>=%s AND ts<%s ORDER BY ts",(key,day+' 00:00+05:30',day+' 23:59:59+05:30'))
                frame=pd.DataFrame(c.fetchall(),columns=['ts','open','high','low','close','volume'])
            frame['ts']=pd.to_datetime(frame.ts,utc=True).dt.tz_convert(base.TZ);frame=frame.set_index('ts')
            rec=lookup[(day,key)];frame=restore_bars(frame,rec['price_factor']);result=replay(t,rec,frame,cfg)
            rows.append(dict(key=key,day=day,source_file=str(path),source_sha256=base.sha(path),**imported,**result))
        except Exception as exc:rows.append(dict(key=key,day=day,status='unavailable',error_type=type(exc).__name__))
    report=dict(chosen=len(chosen),matched=sum(x['status']=='matched' for x in rows),rows=rows,
        selection='First20 chronological development trades, fixed before evaluation; no outcome-based sample selection',
        limitation='Fixed entries/quantities; original completed5m trailing/failure decisions,1m price paths. Not an alternate portfolio or certified fills.')
    base.dump(out/'audit.json',report);return report
