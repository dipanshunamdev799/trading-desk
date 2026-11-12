"""Bounded recent exact-contract candle diagnostic for frozen intraday finalists."""
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'backend'),str(ROOT/'scripts')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient
from research_option_premiums import download

OLD=ROOT/'artifacts'/'directional_research'
OUT=ROOT/'artifacts'/'directional_research_phase2'


def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')


def main():
    trades=pd.read_csv(OLD/'lab-selected-trades.csv')
    trades=trades[(trades.session>='2026-11-02')&(trades.session<='2026-11-06')&trades.strategy.str.startswith(('ema_trend|','donchian|','pullback|'))].copy()
    daily=json.loads((OLD/'nifty-upstox-1day.json').read_text())
    dates=sorted(r['ts'][:10] for r in daily)
    prior={day:max(d for d in dates if d<day) for day in trades.session.unique()}
    dump('option-intraday-preregister.json',{'families':['ema_trend','donchian','pullback'],'frozen_signal_trades':len(trades),
         'window':['2026-11-02','2026-11-06'],'old_signal_ledger_sha256':hashlib.sha256((OLD/'lab-selected-trades.csv').read_bytes()).hexdigest(),
         'contract_universe':'Prior-session official NSE archive; current instrument_key only accepted if exacttoken/expiry/strike/type matches; expired mapping unavailable is rejected',
         'expiry':'Nearest non-expiry-day (strictly after session date) vs month-end listed-expiry proxy; ATM and one listed strike ITM using signal-time spot close',
         'entry_exit':'Original frozen next-open entry and fixed exit; exact five-minute option open / final candleclose. Require all bars present, positive entry/exit volume, unchanged lot and positive previous-session volume.',
         'costs':'DatedsaleSTT0.15%; additionally2premiumpts+INR100 or5pts+INR200friction allowances; not full statutoryfee reconstruction',
         'limitations':'Onlyfive recent sessions; no bid/ask or first-trade timestamp. No executablefillclaim; historical selection exposure and repeatedcontractpolicies acknowledged.'})
    raw={}
    for day in sorted(set(prior.values())):
        _,raw[day]=download(day)
    current=json.loads((OUT/'option-current-contracts.json').read_text())
    keys={(str(r['exchange_token']),r['expiry'],float(r['strike_price']),r['instrument_type']):r['instrument_key'] for r in current}
    index=pd.DataFrame(json.loads((OLD/'nifty-upstox-5minute.json').read_text()))
    index['stamp']=pd.to_datetime(index.ts,utc=True)
    spot=dict(zip(index.stamp,index.close))
    selection=[]
    for t in trades.to_dict('records'):
        signal=pd.Timestamp(t['entry_at']).tz_convert('UTC')
        mark=float(spot[signal-pd.Timedelta(minutes=5)])
        side='CE' if t['direction']==1 else 'PE';universe=raw[prior[t['session']]]['contracts']
        expiries=sorted({r['expiry'] for r in universe if r['expiry']>t['session']})
        monthly={}
        for r in universe:
            exp=r['expiry'];monthly[exp[:7]]=max(exp,monthly.get(exp[:7],exp))
        months=sorted(e for e in monthly.values() if e>t['session'])
        for bucket,exp in [('nearest_nonexpiry_day',expiries[0]),('month_end_proxy',months[0])]:
            subset=[r for r in universe if r['expiry']==exp and r['side']==side]
            atm=min(subset,key=lambda r:(abs(r['strike']-mark),r['strike']))
            itm=min((r for r in subset if (r['strike']<atm['strike'] if side=='CE' else r['strike']>atm['strike'])),key=lambda r:abs(r['strike']-atm['strike']))
            for strike_rule,contract in [('ATM',atm),('one_step_ITM',itm)]:
                identity=(contract['token'],exp,contract['strike'],side);key=keys.get(identity)
                row={**t,'expiry_bucket':bucket,'strike_rule':strike_rule,'selection_spot':mark,
                     'universe_date':prior[t['session']],'expiry':exp,'strike':contract['strike'],'option_type':side,
                     'token':contract['token'],'lot':contract['lot'],'prior_volume':contract['volume'],'instrument_key':key}
                row['status']='selected' if key and contract['volume']>0 else 'expired_or_missing_exact_current_mapping' if not key else 'zero_prior_volume'
                selection.append(row)
    dump('option-intraday-selection-frozen.json',selection)
    client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=15,max_retries=0)
    cache=OUT/'option-intraday-candles';cache.mkdir(exist_ok=True)
    fetched={};errors=[]
    for key in sorted({r['instrument_key'] for r in selection if r['status']=='selected'}):
        path=cache/(key.split('|')[1]+'.json')
        try:
            if path.exists():p=json.loads(path.read_text())
            else:
                p=client.get_historical_candles_v3(key,'minutes',5,'2026-11-06','2026-11-02');path.write_text(json.dumps(p));time.sleep(.25)
            frame=pd.DataFrame(p['candles'],columns=['ts','open','high','low','close','volume','oi'])
            frame['stamp']=pd.to_datetime(frame.ts,utc=True)
            if frame.stamp.duplicated().any():raise ValueError('Duplicatecandles')
            fetched[key]=frame.set_index('stamp')
        except Exception as e:errors.append({'instrument_key':key,'type':type(e).__name__,'status':getattr(e,'status_code',None)})
    ledger=[]
    for row in selection:
        if row['status']!='selected':ledger.append(row);continue
        frame=fetched.get(row['instrument_key'])
        entry=pd.Timestamp(row['entry_at']).tz_convert('UTC');exit=pd.Timestamp(row['exit_at']).tz_convert('UTC')
        expected=pd.date_range(entry,exit-pd.Timedelta(minutes=5),freq='5min')
        if frame is None:ledger.append({**row,'status':'candle_fetch_failed'});continue
        if not expected.isin(frame.index).all():ledger.append({**row,'status':'missing_holding_candles'});continue
        e=frame.loc[entry];x=frame.loc[exit-pd.Timedelta(minutes=5)]
        if e.volume<=0 or x.volume<=0:ledger.append({**row,'status':'zero_entry_or_exit_volume'});continue
        if not (0<e.open and 0<x.close):ledger.append({**row,'status':'invalid_premium'});continue
        if not 0<e.low<=min(e.open,e.close)<=max(e.open,e.close)<=e.high or not 0<x.low<=min(x.open,x.close)<=max(x.open,x.close)<=x.high:
            ledger.append({**row,'status':'invalid_OHLC'});continue
        gross=(float(x.close)-float(e.open))*row['lot'];stt=float(x.close)*row['lot']*.0015
        ledger.append({**row,'status':'observed_candle_proxy','premium_entry':float(e.open),'premium_exit':float(x.close),'entry_volume':float(e.volume),'exit_volume':float(x.volume),
                       'gross_rupees_per_lot':gross,'sale_stt_rupees_per_lot':stt,'illustrative_net_rupees_per_lot':gross-stt-2*row['lot']-100,
                       'severe_net_rupees_per_lot':gross-stt-5*row['lot']-200})
    table=pd.DataFrame(ledger);table.to_csv(OUT/'option-intraday-trades.csv',index=False)
    accepted=table[table.status=='observed_candle_proxy'];groups=[]
    for (strategy,bucket,strike),g in accepted.groupby(['strategy','expiry_bucket','strike_rule']):
        groups.append({'family':strategy.split('|')[0],'expiry_bucket':bucket,'strike_rule':strike,'n':len(g),'sessions':g.session.nunique(),
                       'gross_mean_rupees_per_lot':float(g.gross_rupees_per_lot.mean()),'illustrative_net_mean_rupees_per_lot':float(g.illustrative_net_rupees_per_lot.mean()),
                       'severe_net_mean_rupees_per_lot':float(g.severe_net_rupees_per_lot.mean())})
    summary={'underlying_trades':len(trades),'policy_attempts':len(table),'observed_policy_rows':len(accepted),'rejections':table.status.value_counts().to_dict(),'groups':groups,'fetch_errors':errors}
    dump('option-intraday-summary.json',summary)
    lines=['# Recent intraday premium diagnostic','',f"{len(trades)} fixed EMA/Donchian/pullback signals from 2–6 November 2026 generated {len(table)} predeclared contract-policy attempts; {len(accepted)} had complete positive-volume entry/exit candle evidence.",
           '', 'The prior completed session\'s official NSE contract universe was used before the decision. Strike choice used the underlying candle close at the frozen signal, with next-five-minute option open entry and original fixed-time candle close exit. Current Upstox instrument keys were accepted only for exact dated token/expiry/strike/type matches. Missing expired mappings were rejected. Nearest expiry excludes same-day expiry; month-end expiry is a listed-calendar inference. ATM versus one listed strike ITM are disclosed in full, including duplicate contracts across policies.',
           '', '**This is a tiny, historically inspected candle-price diagnostic, not executable option-profit validation.** Option opens can occur after the candle boundary, and no bid/ask or exact trade timestamps establish latency/fills. Future entry/exit volume is a retrospective coverage requirement, not a claim that those fills could be anticipated. Do not combine correlated policy rows as independent trades.',
           '', 'Both net scenarios deduct dated 0.15% sale STT. Additional allowances are 2 premium points + INR100 or 5 points + INR200 per round trip, covering other fees/execution illustratively; no fully reconstructed statutory cost claim.',
           '', '|Family|Expiry|Strike|N|Sessions|Gross INR/lot|Illustrative net INR/lot|Severe net INR/lot|','|---|---|---|---:|---:|---:|---:|---:|']
    for r in groups:lines.append(f"|{r['family']}|{r['expiry_bucket']}|{r['strike_rule']}|{r['n']}|{r['sessions']}|{r['gross_mean_rupees_per_lot']:.2f}|{r['illustrative_net_mean_rupees_per_lot']:.2f}|{r['severe_net_mean_rupees_per_lot']:.2f}|")
    lines+=['','Coverage: '+json.dumps(summary['rejections']), '', 'No confidence or profitability claim is made from this five-session window. Full selections, rejected rows, raw option candles and prior-day official source ZIPs are retained. [Upstox historical candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/). [NSE dated STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).']
    (OUT/'option-intraday-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'underlying_trades':len(trades),'policies':len(table),'observed':len(accepted),'requests':len(fetched),'errors':len(errors)}))


if __name__=='__main__':main()
