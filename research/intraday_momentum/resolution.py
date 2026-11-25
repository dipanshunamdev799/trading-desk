"""Fixed-entry one-minute path audit; never a new portfolio or model selection."""
from pathlib import Path
import pandas as pd

from .costs import fees,adverse_price


def replay(trade,bars,slippage_bps=10,hold_minutes=60):
    entry=pd.Timestamp(trade['entry_at']);due=entry+pd.Timedelta(minutes=hold_minutes)
    side=1 if trade['side']=='LONG' else -1
    if entry not in bars.index or due not in bars.index:return dict(status='missing_endpoint')
    observed=float(bars.loc[entry,'open']);expected=float(trade['raw_entry_price'])
    if abs(observed-expected)>max(.02,expected*.0002):return dict(status='entry_open_mismatch',observed=observed,expected=expected)
    stop=trade['stop_price'];target=trade['target_price'];raw=None;reason=None;when=None;both=0
    for at in pd.date_range(entry,due,freq='min'):
        if at not in bars.index:return dict(status='missing_path_minute',at=at.isoformat())
        row=bars.loc[at]
        if at>=due:raw=float(row['open']);reason='TIME_EXIT';when=at;break
        stop_hit=float(row['low'])<=stop if side==1 else float(row['high'])>=stop
        target_hit=float(row['high'])>=target if side==1 else float(row['low'])<=target
        if stop_hit or target_hit:
            both=int(stop_hit and target_hit)
            if stop_hit:
                raw=min(float(row['open']),stop) if side==1 else max(float(row['open']),stop)
                reason='STOP_FIRST_AMBIGUOUS' if both else 'STOP'
            else:raw=target;reason='TARGET'
            when=at;break
    if raw is None or float(bars.loc[when,'volume'])<=0:return dict(status='unobserved_exit')
    exit_side='SELL' if side==1 else 'BUY';exit_fill=adverse_price(raw,exit_side,slippage_bps)
    net=side*(exit_fill-trade['entry_price'])*trade['quantity']-trade['entry_fee_components']['total']-fees(exit_side,exit_fill,trade['quantity'])['total']
    return dict(status='matched',reason_1minute=reason,exit_bar_1minute=when.isoformat(),exit_price_1minute=exit_fill,
                ambiguous_1minute=both,net_pnl_1minute=net,net_pnl_5minute=trade['net_pnl'],net_pnl_difference=net-trade['net_pnl'])


def audit(trades,records,out,count=20):
    from .data import _fetch,insert_raw,connection,dump,sha,TZ
    from .units import restore_bars
    out=Path(out);lookup={(r['day'],r['key']):r for r in records};rows=[]
    chosen=sorted((t for t in trades if t['session']<='2025-08-31'),key=lambda t:(t['entry_at'],t['instrument_key']))[:count]
    for t in chosen:
        key=t['instrument_key'];day=t['session'];path=out/'resolution-raw'/key.replace('|','_')/(day+'.json.gz')
        try:
            doc,cached=_fetch(key,'minutes',1,day,day,path);imported=insert_raw(doc,key,'1minute',day,day)
            with connection() as c:
                c.execute("SELECT ts,open,high,low,close,volume FROM public.candles WHERE instrument_key=%s AND interval='1minute' AND ts>=%s AND ts<%s AND source='upstox' ORDER BY ts",(key,day+' 00:00+05:30',day+' 23:59:59+05:30'))
                records_raw=c.fetchall()
            frame=pd.DataFrame(records_raw,columns=['ts','open','high','low','close','volume'])
            frame['ts']=pd.to_datetime(frame.ts,utc=True).dt.tz_convert(TZ);frame=frame.set_index('ts')
            basis=lookup[(day,key)].get('price_factor',1.)
            frame=restore_bars(frame,basis)
            row=replay(t,frame)
            rows.append(dict(key=key,day=day,entry_at=t['entry_at'],source_file=str(path),source_sha256=sha(path),cached=cached,**imported,**row))
        except Exception as exc:rows.append(dict(key=key,day=day,entry_at=t['entry_at'],status='unavailable',error_type=type(exc).__name__))
    report=dict(selection='First20chronological development trades of the already-frozen selected model; no held-out trade selection',
        chosen=len(chosen),matched=sum(r['status']=='matched' for r in rows),rows=rows,
        limitation='Fixed entries/quantities/thresholds only. Different exits could change later portfolio opportunities; this is not a one-minute portfolio backtest.')
    dump(out/'one-minute-audit.json',report);return report
