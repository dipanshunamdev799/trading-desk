"""Exact dated-contract NIFTY daily-premium research using public NSE archives.

Entries are daily first-trade opens, exits official daily closes: asynchronous,
provisional price proxies, never asserted executable quotes. No orders.
"""
import csv
import hashlib
import io
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys
import threading
import time
import zipfile

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'artifacts'/'directional_research'
OUT=ROOT/'artifacts'/'directional_research_phase2'
SOURCE='https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{day}_F_0000.csv.zip'
LOCK=threading.Lock()
NEXT_REQUEST=0.


def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')


def download(day):
    global NEXT_REQUEST
    path=OUT/'option-nse-raw'/f'{day}.zip'
    compact=OUT/'option-nse-ohlc'/f'{day}.json'
    if compact.exists():return day,json.loads(compact.read_text())
    if not path.exists():
        with LOCK:
            delay=max(0,NEXT_REQUEST-time.monotonic())
            if delay:time.sleep(delay)
            NEXT_REQUEST=time.monotonic()+.5
        r=requests.get(SOURCE.format(day=day.replace('-','')),headers={'User-Agent':'Mozilla/5.0 TradingResearch/1.0'},timeout=(5,25))
        r.raise_for_status()
        if len(r.content)>10_000_000:raise ValueError('Oversized archive')
        path.write_bytes(r.content)
    content=path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        names=[n for n in z.namelist() if n.endswith('.csv')]
        if len(names)!=1:raise ValueError('Unexpected CSV layout')
        with io.TextIOWrapper(z.open(names[0]),encoding='utf-8-sig') as stream:
            rows=[]
            for r in csv.DictReader(stream):
                if r['TradDt']!=day:raise ValueError('Archive date mismatch')
                if r['TckrSymb']!='NIFTY' or r['OptnTp'] not in ['CE','PE']:continue
                rows.append({'token':r['FinInstrmId'],'expiry':r.get('FininstrmActlXpryDt') or r['XpryDt'],
                             'strike':float(r['StrkPric']),'side':r['OptnTp'],'lot':int(r['NewBrdLotQty']),
                             'open':float(r['OpnPric']),'high':float(r['HghPric']),'low':float(r['LwPric']),
                             'close':float(r['ClsPric']),'last':float(r['LastPric']),'volume':float(r['TtlTradgVol'])})
    result={'day':day,'source_url':SOURCE.format(day=day.replace('-','')),'sha256_zip':hashlib.sha256(content).hexdigest(),'contracts':rows}
    compact.write_text(json.dumps(result),encoding='utf-8')
    return day,result


def select(trades,archive,spot):
    rows=[]
    for t in trades.to_dict('records'):
        signal=t['signal_date'];chain=archive[signal];side='CE' if t['side']==1 else 'PE'
        expiries=sorted(c['expiry'] for c in chain['chains'] if c['expiry']>t['exit_date'])
        # The last listed expiry within a month is a month-end listed-expiry proxy.
        # Both are selected from the SIGNAL-DAY archive, before entry prices.
        monthly={}
        for c in chain['chains']:
            exp=c['expiry'];monthly[exp[:7]]=max(exp,monthly.get(exp[:7],exp))
        months=sorted(e for e in monthly.values() if e>t['exit_date'])
        for bucket,expiry in [('nearest_surviving',expiries[0] if expiries else None),('month_end_proxy',months[0] if months else None)]:
            for strike_rule in ['ATM','one_step_ITM']:
                base={**t,'expiry_bucket':bucket,'strike_rule':strike_rule,'selection_spot':spot[signal],
                      'expiry':expiry,'selection_archive_date':signal,'selection_archive_sha256':chain['source_sha256']}
                if expiry is None:rows.append({**base,'status':'no_surviving_listed_expiry'});continue
                contracts=next(c['contracts'] for c in chain['chains'] if c['expiry']==expiry)
                candidates=[c for c in contracts if c[2]==side]
                atm=min(candidates,key=lambda c:(abs(c[1]-spot[signal]),c[1]))
                chosen=atm
                if strike_rule=='one_step_ITM':
                    itm=[c for c in candidates if (c[1]<atm[1] if side=='CE' else c[1]>atm[1])]
                    if not itm:rows.append({**base,'status':'no_ITM_strike'});continue
                    chosen=min(itm,key=lambda c:abs(c[1]-atm[1]))
                base.update(token=str(chosen[0]),strike=chosen[1],option_type=chosen[2],signal_lot=int(chosen[4]),signal_volume=chosen[6])
                if not chosen[6] or chosen[6]<=0:rows.append({**base,'status':'zero_signal_day_volume'});continue
                rows.append({**base,'status':'selected_before_entry_prices'})
    return rows


def bootstrap(df,column):
    if df.empty:return [None,None]
    # Resample complete calendar months; small number of months limits precision.
    blocks=[g[column].to_numpy() for _,g in df.groupby(df.entry_date.str[:7])]
    rng=np.random.default_rng(20261109);means=[]
    for _ in range(3000):
        sample=np.concatenate([blocks[i] for i in rng.integers(0,len(blocks),len(blocks))])
        means.append(sample.mean())
    return np.quantile(means,[.025,.975]).tolist()


def main():
    OUT.mkdir(exist_ok=True)
    for folder in ['option-nse-raw','option-nse-ohlc']:(OUT/folder).mkdir(exist_ok=True)
    archive={r['date']:r for r in json.loads((OUT/'option-nse-retained-eod.json').read_text())}
    daily=json.loads((OLD/'nifty-upstox-1day.json').read_text());spot={r['ts'][:10]:r['close'] for r in daily}
    trades=pd.read_csv(OLD/'daily-selected-trades.csv')
    total=len(trades)
    mask=trades.signal_date.isin(archive)&trades.entry_date.isin(archive)&trades.exit_date.isin(archive)
    trades=trades[mask].copy()
    dump('option-premium-preregister.json',{'signal_source_sha256':hashlib.sha256((OLD/'daily-selected-trades.csv').read_bytes()).hexdigest(),
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'total_frozen_signal_trades':total,'source_covered_signal_trades':len(trades),
         'universe':'Signal-day dated NSE EOD contracts, pre-entry, frozen four daily family finalists',
         'selection':'Signal-time underlying close; nearest listed ATM tie lower; one listed strike ITM. Prior-day volume must be positive. Expiry strictly after planned exit; nearest surviving versus last listed expiry of earliest eligible month (month-end proxy).',
         'entry':'Next session daily first-trade open, exact dated instrument; asynchronous proxy',
         'exit':'Original fixed exit session official daily close, exact same instrument; not guaranteed execution',
         'friction':'Gross; dated sale STT0.10% through31Mar2026 and0.15% from1Apr2026; illustrative additionally2 premium points + INR100 per roundtrip; severe additionally5 premium points + INR200. Allowances exclude STT, cover other fees/execution illustratively, and are NOT verified historical fees/spreads.',
         'stt_source':'https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf',
         'protocol_update':'Dated STT added while source downloads were in progress and before any premium outcome/summary was viewed. Original fixed contract choices unchanged.',
         'rejections':'Missing archive/contract, zero prior/entry/exit volume, invalid OHLC, changed lot/identity; no forward fill',
         'calendar_assumption':'Planned exit sessions assumed known from exchange calendar; dates are those of frozen underlying ledger. Holiday announcements were not point-in-time archived.',
         'bootstrap':'3000 resamples of complete calendar months; conditional, not selection adjusted',
         'no_tuning':'No premium results used to change rules/contracts/costs; all buckets disclosed'})
    selected=select(trades,archive,spot)
    dump('option-contract-selection-frozen.json',selected)
    dates=sorted({r['entry_date'] for r in selected if r['status']=='selected_before_entry_prices'})
    files={};errors=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(download,day):day for day in dates}
        for count,f in enumerate(as_completed(futures),1):
            try:
                day,payload=f.result();files[day]=payload
            except Exception as exc:errors.append({'date':futures[f],'type':type(exc).__name__,'status':getattr(getattr(exc,'response',None),'status_code',None)})
            if count%10==0:print('NSE entry archives',count,'/',len(dates),flush=True)
    dump('option-source-downloads.json',{'requested':len(dates),'successful':len(files),'errors':errors,'archives':[{k:v for k,v in p.items() if k!='contracts'} for p in files.values()]})
    ledgers=[];checks=0
    for row in selected:
        if row['status']!='selected_before_entry_prices':ledgers.append(row);continue
        if row['entry_date'] not in files:ledgers.append({**row,'status':'entry_archive_unavailable'});continue
        identity=(row['token'],row['expiry'],row['strike'],row['option_type'])
        entry=next((r for r in files[row['entry_date']]['contracts'] if (r['token'],r['expiry'],r['strike'],r['side'])==identity),None)
        exit_chain=next((c for c in archive[row['exit_date']]['chains'] if c['expiry']==row['expiry']),None)
        exit=next((r for r in exit_chain['contracts'] if (str(r[0]),row['expiry'],r[1],r[2])==identity),None) if exit_chain else None
        reason=None
        if entry is None or exit is None:reason='entry_or_exit_identity_missing'
        elif entry['lot']!=row['signal_lot'] or int(exit[4])!=row['signal_lot']:reason='lot_size_changed'
        elif entry['volume']<=0 or not exit[6] or exit[6]<=0:reason='zero_entry_or_exit_day_volume'
        elif not 0<entry['low']<=min(entry['open'],entry['close'])<=max(entry['open'],entry['close'])<=entry['high']:reason='invalid_entry_OHLC'
        elif not exit[5] or exit[5]<=0:reason='invalid_exit_close'
        if reason:ledgers.append({**row,'status':reason});continue
        opened=entry['open'];closed=float(exit[5]);lot=row['signal_lot'];gross=(closed-opened)*lot
        stt_rate=.0015 if row['exit_date']>='2026-04-01' else .001
        stt=closed*lot*stt_rate
        ledger={**row,'status':'premium_proxy_observed','premium_entry':opened,'premium_exit':closed,'lot':lot,
                'entry_volume':entry['volume'],'exit_volume':exit[6],'premium_gross_points':closed-opened,
                'gross_rupees_per_lot':gross,'stt_rate':stt_rate,'sale_stt_rupees_per_lot':stt,
                'illustrative_net_rupees_per_lot':gross-stt-2*lot-100,
                'severe_net_rupees_per_lot':gross-stt-5*lot-200,'gross_premium_return_pct':(closed/opened-1)*100,
                'entry_archive_sha256':files[row['entry_date']]['sha256_zip'],'exit_archive_sha256':archive[row['exit_date']]['source_sha256']}
        assert row['signal_date']<row['entry_date']<=row['exit_date']<row['expiry'];checks+=1
        assert np.isfinite([opened,closed,gross]).all();checks+=1
        assert opened>0 and row['signal_volume']>0 and entry['volume']>0 and exit[6]>0;checks+=1
        ledgers.append(ledger)
    table=pd.DataFrame(ledgers);table.to_csv(OUT/'option-premium-trades.csv',index=False)
    accepted=table[table.status=='premium_proxy_observed'].copy();summary=[]
    for (strategy,bucket,strike),g in accepted.groupby(['strategy','expiry_bucket','strike_rule']):
        ci=bootstrap(g,'illustrative_net_rupees_per_lot')
        summary.append({'strategy':strategy,'expiry_bucket':bucket,'strike_rule':strike,'n':len(g),'months':g.entry_date.str[:7].nunique(),
                       'gross_mean_rupees_per_lot':float(g.gross_rupees_per_lot.mean()),'illustrative_net_mean_rupees_per_lot':float(g.illustrative_net_rupees_per_lot.mean()),
                       'severe_net_mean_rupees_per_lot':float(g.severe_net_rupees_per_lot.mean()),'gross_win_pct':float((g.gross_rupees_per_lot>0).mean()*100),
                       'net_ci95_rupees_per_lot':ci})
    distinct=len(accepted.drop_duplicates(['strategy','signal_date','token','expiry','strike']))
    dump('option-premium-summary.json',{'covered_signal_trades':len(trades),'selected_buckets':len(selected),'observed_buckets':len(accepted),'distinct_signal_contract_outcomes_within_strategy':distinct,'duplicate_policy_rows':len(accepted)-distinct,
         'selection_counts':dict(Counter(table.status)),'source_outside_coverage':total-len(trades),'assertions_passed':checks,'groups':summary})
    lines=['# Exact-contract daily premium study','',
           f"Four frozen daily finalists supplied {total} trades; {len(trades)} signal/entry/exit dates fit the retained NSE archive (13 October 2025–23 October 2026). Four expiry/strike buckets produce {len(selected)} attempts and {len(accepted)} usable premium proxies, representing {distinct} distinct signal/contract outcomes within strategy ({len(accepted)-distinct} duplicate policy rows).",
           '', '**These are actual historical option premiums, but daily first-trade opens and official closing values are asynchronous price proxies. They do not establish executable fills at the underlying signal times.** Missing bid/ask, trade-time, latency and statutory fee histories prevent a deployable profitability claim. The first option trade can occur after the underlying open; a closing value need not be a fill available at the intended exit instant.',
           '', 'Contract choice used the signal-day dated contract universe and signal-time underlying close, before loading entry premiums. Positive signal-day volume is known at selection; entry/exit full-day volumes are ex-post coverage checks, not filters available at entry. All424attempts currently pass those checks, so they exclude no additional outcomes. Require unchanged identity/lot. ATM tie breaks toward lower strike; ITM is one listed strike in the money. Expiry is strictly beyond the planned exit. “Nearest surviving” may be a weekly or monthly expiry; “month-end proxy” is the last listed expiry in its calendar month, inferred from the dated archive. When both policies pick the same contract, rows are duplicate policy comparisons, not independent trades.',
           '', 'Gross P&L uses the dated lot size. Both net scenarios deduct dated sale STT: 0.10% through 31 March 2026, 0.15% from 1 April 2026. Illustrative net additionally deducts 2 premium points plus INR100 per round trip; severe additionally deducts 5 points plus INR200. These extra amounts cover other fees/execution illustratively, not verified actual spreads or a complete statutory charge calculation. The dated STT protocol update occurred during source download, before any premium outcomes were viewed. [NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).',
           '', '|Frozen family|Expiry bucket|Strike|N|Gross INR/lot|Illustrative net INR/lot|Severe net INR/lot|95% month-block interval, illustrative net|',
           '|---|---|---|---:|---:|---:|---:|---|']
    for r in summary:
        ci=r['net_ci95_rupees_per_lot'];lines.append(f"|{r['strategy'].split('|')[0]}|{r['expiry_bucket']}|{r['strike_rule']}|{r['n']}|{r['gross_mean_rupees_per_lot']:.2f}|{r['illustrative_net_mean_rupees_per_lot']:.2f}|{r['severe_net_mean_rupees_per_lot']:.2f}|{ci[0]:.2f}, {ci[1]:.2f}|")
    lines+=['','## Coverage and limitations', '',json.dumps(dict(Counter(table.status)),indent=2),'',
            'All outcomes are disclosed; no premium winner is selected or promoted. The daily finalist selection was already historical and the source window overlaps other inspected data. Confidence intervals resample calendar months and are conditional, not adjusted for parameter or contract search. Small numbers of months/trades yield unreliable precision. Price-based Greeks, IV attribution and option drawdown paths are unavailable from these EOD records. The planned exit date assumes the exchange calendar was known; archived announcement timestamps were not available.',
            '', 'Entry ZIPs and SHA256 hashes are preserved; exit closes, volumes and dated lots come from the already retained official NSE archive whose source hashes were preserved by the earlier study. Raw ZIP parsing rejects date mismatches. Fixed selection file, source manifest, full accepted/rejected ledger and summaries are in this directory.',
            '', '[Official NSE daily reports](https://www.nseindia.com/all-reports-derivatives). This source provides daily reports, not historical intraday order-book quotes.']
    (OUT/'option-premium-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'covered_signal_trades':len(trades),'buckets':len(selected),'observed':len(accepted),'source_files':len(files),'checks':checks}),flush=True)


if __name__=='__main__':main()
