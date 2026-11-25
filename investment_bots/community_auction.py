"""Local-only exploratory auction replay. PostgreSQL is opened READ ONLY.

No app worker, broker, Postgres constructor, ResearchStore constructor or result
writer is called. Community observations and all derived outputs stay on disk.
Final-auction approximations are deliberately never labelled validated C0-R-X.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import csv
from datetime import datetime
from functools import lru_cache
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import zipfile

import numpy as np
import pandas as pd

from .engine import features
from .long_history import ResearchStore, metrics, native_data, trade_accounting
from .reference import xsim

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/investment_bots/community-auction'
VERSION = 'community-auction-exploratory-v1'


def download_sources(raw):
    """Pinned public data downloads only; no source code is executed."""
    import requests
    raw.mkdir(parents=True,exist_ok=True)
    commits=[('tkanhe/NSE-India-PreOpen-Market-Data','653479863adbc4e7ed87fbf67e62f01f04a59f04'),
             ('howutrade/nse-preopen-data','4d493e274a9000a16fe69c29610ff78376312333'),
             ('ferozmd53/nse-preopen-data','98f7a54c8b9f9b8d924481792d5e5b76d059662d')]
    manifest=[]
    for repo,commit in commits:
        path=raw/(repo.split('/')[0]+'.zip')
        if not path.exists():
            response=requests.get(f'https://codeload.github.com/{repo}/zip/{commit}',timeout=180)
            response.raise_for_status();path.write_bytes(response.content)
        manifest.append(dict(repository=repo,commit=commit,file=path.name,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
    existing=raw/'sources.json'
    if existing.exists():
        prior=json.loads(existing.read_text())
        if {(x['file'],x['sha256']) for x in prior}!={(x['file'],x['sha256']) for x in manifest}:
            raise ValueError('Downloaded archives differ from the pinned local manifest')
    else:existing.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    with zipfile.ZipFile(raw/'tkanhe.zip') as z:
        name=next(n for n in z.namelist() if n.endswith('.7z'))
        (raw/'tkanhe.7z').write_bytes(z.read(name))


def number(value):
    try:
        x = float(str(value).replace(',', '').strip())
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def observation(symbol, price, volume, timestamp=None, buy=None, sell=None):
    b, s = number(buy), number(sell)
    return dict(symbol=str(symbol).strip().upper(), price=number(price), volume=number(volume),
                timestamp=timestamp, imbalance=None if b is None or s is None else b-s)


@lru_cache(maxsize=20000)
def quote_day(timestamp):
    try:return datetime.strptime(timestamp,'%d-%b-%Y %H:%M:%S').date().isoformat()
    except (ValueError,TypeError):return None


def load_archive(source, raw):
    """Read data formats, never execute downloaded Python or spreadsheet macros."""
    records = {}; duplicates = 0; conflicts = 0; files = 0; rejected = 0; timestamp_rejected=0
    def add(day, row):
        nonlocal duplicates, conflicts, rejected, timestamp_rejected
        if not row['symbol'] or row['symbol']=='NONE':rejected += 1;return
        if row['timestamp'] and quote_day(row['timestamp'])!=day:
            timestamp_rejected+=1;return
        key = (day, row['symbol'])
        if key in records:
            duplicates += 1
            if records[key] != row:
                conflicts += 1
                # Different snapshots without trustworthy capture times cannot
                # be ordered causally. Exclude instead of choosing a winner.
                records[key]['conflicted'] = True
            return
        records[key] = row
    if source == 'tkanhe':
        import py7zr
        from py7zr.io import BytesIOFactory
        archive = raw/'tkanhe.7z'
        with py7zr.SevenZipFile(archive) as z:
            factory = BytesIOFactory(limit=250_000_000)
            z.extractall(factory=factory)
            for name in z.getnames():
                if not name.endswith('.csv'):continue
                m=re.search(r'_(\d{2}\.\d{2}\.\d{2})\.csv$',name)
                if not m:continue
                day=datetime.strptime(m[1],'%y.%m.%d').date().isoformat();files+=1
                text=factory.get(name).read().decode('utf-8-sig',errors='replace')
                for row in csv.DictReader(io.StringIO(text)):
                    if row.get('Series','EQ').strip() != 'EQ':continue
                    add(day,observation(row.get('Symbol'),row.get('PreOpenPrice'),row.get('FinalQty',row.get('TradedQty'))))
    elif source == 'howutrade':
        with zipfile.ZipFile(raw/'howutrade.zip') as z:
            # ALL avoids counting the same stock four times; dates with only
            # a category file are explicitly absent, not inferred.
            for name in sorted(z.namelist()):
                m=re.search(r'preOpenALL(\d{8})\.json$',name)
                if not m:continue
                day=datetime.strptime(m[1],'%d%m%Y').date().isoformat();files+=1
                doc=json.loads(z.read(name))
                for row in doc.get('data',[]):
                    meta=row.get('metadata',{});q=row.get('detail',{}).get('preOpenMarket',{})
                    add(day,observation(meta.get('symbol'),q.get('finalPrice',meta.get('iep')),
                        q.get('finalQuantity',meta.get('finalQuantity')),q.get('lastUpdateTime'),
                        q.get('atoBuyQty'),q.get('atoSellQty')))
    elif source == 'ferozmd53':
        with zipfile.ZipFile(raw/'ferozmd53.zip') as z:
            for name in sorted(z.namelist()):
                m=re.search(r'pre-open-FO-(\d{2}-[A-Z]{3}-\d{4})(?: \(\d+\))?\.csv$',name)
                if not m:continue
                day=datetime.strptime(m[1],'%d-%b-%Y').date().isoformat();files+=1
                for row in csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig',errors='replace'))):
                    add(day,observation(row.get('SYMBOL'),row.get('FINAL_PRICE'),row.get('FINAL_QUANTITY'),row.get('LAST_UPDATE')))
    else:raise ValueError(source)
    dates=sorted({d for d,s in records})
    usable={k:v for k,v in records.items() if not v.get('conflicted')}
    audit=dict(source=source,files=files,records=len(records),distinct_dates=len(dates),
               first=dates[0],last=dates[-1],duplicate_rows=duplicates,conflicting_duplicate_rows=conflicts,
               excluded_conflicting_keys=len(records)-len(usable),rejected_rows=rejected,
               wrong_or_unparseable_quote_date_rows_excluded=timestamp_rejected,
               positive_volume_rows=sum((r['volume'] or 0)>0 for r in usable.values()),
               market_imbalance_rows=sum(r['imbalance'] is not None for r in usable.values()),
               zero_market_imbalance_rows=sum(r['imbalance']==0 for r in usable.values()),
               verified_decision_capture_rows=0,
               strict_status='NOT_IDENTIFIABLE: no verified <=09:05 capture with freshness evidence')
    return usable,audit


class ReadOnlyDB:
    """Enforce server-side read-only transactions, including named cursors."""
    market_table='public.candles'
    @contextmanager
    def connection(self):
        import psycopg2
        from psycopg2.extras import DictCursor
        sys.path.insert(0,str(ROOT/'backend'))
        from app.config import get_settings
        dsn=get_settings().database_url_sync.replace('postgresql+psycopg2://','postgresql://')
        raw=psycopg2.connect(dsn,options='-c default_transaction_read_only=on -c search_path=investment_bots,public',
                             application_name='community-auction-READ-ONLY')
        raw.set_session(readonly=True,isolation_level='REPEATABLE READ')
        class Reader:
            connection=raw
            def execute(self,sql,params=None):
                if not sql.lstrip().upper().startswith(('SELECT','SHOW')):raise ValueError('Read-only SQL required')
                c=raw.cursor(cursor_factory=DictCursor);c.execute(sql,params);return c
        try:
            reader=Reader()
            assert reader.execute('SHOW transaction_read_only').fetchone()[0]=='on'
            yield reader
        finally:raw.rollback();raw.close()


def panel(cache):
    cache.mkdir(parents=True,exist_ok=True)
    npz=cache/'panel.npz';meta=cache/'panel.json'
    if npz.exists() and meta.exists():
        m=json.loads(meta.read_text());data=np.load(npz,allow_pickle=False)
        f={n:pd.DataFrame(data[n],index=m['sessions'],columns=list(m['instruments'])) for n in ('o','h','l','c','v')}
        return m['instruments'],m['sessions'],f
    # Reuse ONLY the SELECT-based panel loader, not its DDL/result writers.
    study=ResearchStore.__new__(ResearchStore);study.db=ReadOnlyDB()
    instruments,sessions,frames,_,_=study.panel('2017-05-01','2026-11-13')
    np.savez_compressed(npz,**{n:f.to_numpy() for n,f in frames.items()})
    meta.write_text(json.dumps(dict(instruments=instruments,sessions=sessions)),encoding='utf-8')
    return instruments,sessions,frames


def gate_status(obs,qty,official_open,mode,participation=.10):
    if obs is None:return 'missing_observation'
    if mode=='strict':return 'unverified_decision_capture'
    if mode=='coverage_only':return 'coverage_only'
    price,volume=obs['price'],obs['volume']
    if price is None or price<=0 or volume is None or volume<=0:return 'no_final_auction'
    # Reject mismatched units, corporate-action discrepancies and first-trade
    # opens rather than treating them as confirmed auction executions.
    if abs(price/official_open-1)>.01:return 'price_mismatch'
    if mode=='zero_imbalance_proxy':
        if obs['imbalance'] is None:return 'missing_market_imbalance'
        if obs['imbalance']!=0:return 'nonzero_market_imbalance'
    if qty>participation*volume:return 'participation_limit'
    return 'proxy_pass'


def execute(out=OUT):
    raw=out/'raw';out.mkdir(parents=True,exist_ok=True)
    for entry in json.loads((raw/'sources.json').read_text()):
        if hashlib.sha256((raw/entry['file']).read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('Raw source checksum mismatch: '+entry['file'])
    with zipfile.ZipFile(raw/'tkanhe.zip') as z:
        name=next(n for n in z.namelist() if n.endswith('.7z'))
        if z.read(name)!=(raw/'tkanhe.7z').read_bytes():raise ValueError('Derived 7z differs from pinned ZIP')
    sources={};audits={}
    for source in ('tkanhe','howutrade','ferozmd53'):
        sources[source],audits[source]=load_archive(source,raw)
        print('Archive audit',audits[source],flush=True)
    (out/'archive-audit.json').write_text(json.dumps(audits,indent=2),encoding='utf-8')
    instruments,sessions,frames=panel(out/'cache');keys=list(instruments)
    print(f'Read-only panel: {len(sessions)} sessions, {len(keys)} equities.',flush=True)
    universe,scores=features(frames['c'],frames['v'],instruments,start=sessions[0],end=sessions[-1])
    prior=universe.shift(1,fill_value=False)
    missing=(prior&frames['c'].isna()).sum(axis=1);required=prior.sum(axis=1)
    incomplete=[dict(session=day,missing=int(missing.loc[day]),required=int(required.loc[day]))
                for day in sessions if required.loc[day]>0 and missing.loc[day]/required.loc[day]>.02]
    a=dict(o=frames['o'].to_numpy(),c=frames['c'].to_numpy(),industry=np.array([r['industry'] for r in instruments.values()]))
    score=scores.to_numpy();ties=np.argsort(np.argsort(np.array(keys)))
    symbols=[instruments[k]['symbol'].upper() for k in keys]
    duplicate_symbols=[s for s,n in Counter(symbols).items() if n>1]
    results=[];curves=[];orders=[];closed_all=[];coverage=[];sensitivity=[]
    for source,observations in sources.items():
        audit=audits[source];first=next(i for i,d in enumerate(sessions) if d>=audit['first'])
        last=max(i for i,d in enumerate(sessions) if d<=audit['last']);t0=first-1
        if t0<84:raise ValueError('Insufficient warmup')
        days=sessions[first:last+1]
        matched=sum((day,sym) in observations for day in days for sym in set(symbols))
        observed_days={d for d,s in observations}
        coverage.append(dict(source=source,start=days[0],end=days[-1],trading_sessions=len(days),
            observed_sessions=sum(day in observed_days for day in days),matched_stock_days=matched,
            mapping='Exact frozen symbol only; no inferred historical renames',excluded_ambiguous_symbols=duplicate_symbols))
        coverage[-1]['incomplete_price_sessions']=[x for x in incomplete if days[0]<=x['session']<=days[-1]]
        modes=['reference','coverage_only','volume_proxy']
        if audit['market_imbalance_rows']:modes.append('zero_imbalance_proxy')
        for mode in modes:
            counter=Counter()
            def fill(t,s,side,rupees,qty):
                ob=observations.get((sessions[t],symbols[s])) if symbols[s] not in duplicate_symbols else None
                tag=gate_status(ob,qty,a['o'][t,s],mode)
                counter[tag]+=1
                return (a['o'][t,s],1.,tag) if tag in ('coverage_only','proxy_pass') else (None,0.,tag)
            r=xsim.run(a,score,t0,t1=last+1,tiebreak=ties,integer=True,ledger=True,log=True,
                       fill=None if mode=='reference' else fill)
            r['_last_marks']={s:r['holdings'][s]*r['eq'][last]*1e6/q for s,q in r['shares'].items()}
            trades,ledger,open_pnl=trade_accounting([r],keys,sessions,integer=True)
            m=metrics(r['eq'][first:last+1],days,r['expo'][first:last+1],trades)
            err=sum(t['net_pnl'] for t in trades)+open_pnl-1e6*(r['eq'][last]-1)
            if abs(err)>.05:raise ValueError(f'Cashflow mismatch {source}/{mode}: {err}')
            for order in ledger:
                order.update(session=sessions[order['t']],instrument_key=keys[order['s']],symbol=symbols[order['s']])
            intended=[o for o in ledger if o['intended_qty'] and o['intended_qty']>0]
            m.update(source=source,mode=mode,start=days[0],end=days[-1],
                filled_orders=sum(o['filled_value']>0 for o in ledger),attempts=len(ledger),
                gate_counts=dict(counter),cashflow_error_rupees=err,
                ending_holdings=len(r['holdings']),pending_sells=len(r['pending']['sell']),
                average_holdings=float(np.mean(r['n_names'][first:last+1])),
                archive_observed_intents=sum((o['session'],o['symbol']) in observations for o in intended),
                positive_quantity_intents=len(intended),
                total_fees_rupees=float(r['costs']))
            results.append(m)
            for i,day in enumerate(days):curves.append(dict(source=source,mode=mode,session=day,equity=r['eq'][first+i],exposure=r['expo'][first+i]))
            orders.extend(dict(source=source,mode=mode,**o) for o in ledger)
            closed_all.extend(dict(source=source,mode=mode,**t) for t in trades)
            print(source,mode,'return',round(m['total_return']*100,2),'DD',round(m['max_drawdown']*100,2),'fills',m['filled_orders'],flush=True)
            if mode in ('volume_proxy','zero_imbalance_proxy'):
                for part,cost in ((.01,.00225),(.05,.00225),(.10,.0045)):
                    def stress_fill(t,s,side,rupees,qty):
                        ob=observations.get((sessions[t],symbols[s])) if symbols[s] not in duplicate_symbols else None
                        tag=gate_status(ob,qty,a['o'][t,s],mode,part)
                        return (a['o'][t,s],1.,tag) if tag=='proxy_pass' else (None,0.,tag)
                    stress=xsim.run(a,score,t0,t1=last+1,tiebreak=ties,integer=True,fill=stress_fill,cost=cost)
                    sm=metrics(stress['eq'][first:last+1],days,stress['expo'][first:last+1])
                    sensitivity.append(dict(source=source,mode=mode,participation=part,cost_per_side=cost,**sm))
    report=dict(version=VERSION,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_manifest=json.loads((raw/'sources.json').read_text()),archive_audit=audits,coverage=coverage,
        strict_C0_R_X=dict(status='NOT_IDENTIFIABLE',reason='No verified capture-time/freshness evidence at the decision cutoff; no strict performance claimed'),
        accounting=dict(capital_rupees=1000000,cost_per_side=.00225,whole_shares=True,profits_reinvested=True,
            initial_positions='Cash; first decision on prior trading close',end_positions='Marked to market, no forced liquidation',
            final_volume_participation=.10,final_price_tolerance=.01,market_data='Existing Upstox PostgreSQL candles; SELECT only',
            community_data_and_results='Local files only; never sent to PostgreSQL'),results=results,sensitivity=sensitivity,
        market_panel_sha256=hashlib.sha256((out/'cache/panel.npz').read_bytes()).hexdigest(),
        market_metadata_sha256=hashlib.sha256((out/'cache/panel.json').read_bytes()).hexdigest(),
        limitations=['All proxy variants use final-auction information unavailable at the 09:05 decision; not an executable historical C0-R-X result',
            'Final volume substitutes for indicative quantity; ATO buy-minus-sell is only an assumed proxy for market imbalance',
            'Missing/conflicting observations block buys and delay sells; no synthetic fallback fills',
            'FO category archives cover cash equities eligible for derivatives, not the full momentum universe',
            'Frozen retained universe/industry labels introduce survivorship and later-information bias',
            'No dividends, spinoff credits or interest; older corporate actions incompletely audited',
            'Missing daily prices retain last marks; this reference replay does not enforce the paper worker operational data-pause gate',
            'No actual fills observed; no forced liquidation of outstanding holdings; windows overlap and are not independent',
            'Research-only source terms; archives are not guaranteed accurate or complete'],real_orders_submitted=0)
    (out/'report.json').write_text(json.dumps(native_data(report),indent=2,allow_nan=False),encoding='utf-8')
    def write_csv(name,rows):
        rows=native_data(rows)
        fields=list(dict.fromkeys(k for r in rows for k in r))
        with (out/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    write_csv('summary.csv',results);write_csv('equity.csv',curves);write_csv('orders.csv',orders);write_csv('closed-positions.csv',closed_all)
    write_csv('sensitivity.csv',sensitivity)
    lines=['# Community auction experiment','', '**Exploratory final-auction proxies, not a validated C0-R-X backtest.**',
           '', 'All community data/results are local. PostgreSQL was accessed through server-enforced read-only transactions.',
           '', '| Archive | Window | Model | Total return | CAGR | Max drawdown | Avg exposure | Ending value (₹) | Filled orders |',
           '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for m in results:
        lines.append(f"| {m['source']} | {m['start']} – {m['end']} | {m['mode']} | {m['total_return']:.2%} | {m['cagr']:.2%} | {m['max_drawdown']:.2%} | {m['average_exposure']:.1%} | {m['final_value_rupees']:,.0f} | {m['filled_orders']} |")
    lines+=['','reference = C0-R official-open reference on the same dates; coverage_only = fills only where an archive row exists; volume_proxy = final-volume participation limit; zero_imbalance_proxy = additionally require zero ATO buy-minus-sell.','',
            '## Limits','']+['- '+s for s in report['limitations']]
    lines+=['','## Source coverage','', '| Archive | Trading sessions | Observed sessions | Reference order intents with archive rows |', '|---|---:|---:|---:|']
    for c in coverage:
        m=next(m for m in results if m['source']==c['source'] and m['mode']=='reference')
        lines.append(f"| {c['source']} | {c['trading_sessions']} | {c['observed_sessions']} | {m['archive_observed_intents']} / {m['positive_quantity_intents']} |")
    lines+=['','Incomplete price sessions in each test (last marks retained; paper processing would pause):',
            '', '```json',json.dumps({c['source']:c['incomplete_price_sessions'] for c in coverage},indent=2),'```']
    lines+=['','## Fixed sensitivity checks','','| Archive | Proxy | Participation | Cost/side | Total return | Max drawdown |','|---|---|---:|---:|---:|---:|']
    for m in sensitivity:lines.append(f"| {m['source']} | {m['mode']} | {m['participation']:.0%} | {m['cost_per_side']:.3%} | {m['total_return']:.2%} | {m['max_drawdown']:.2%} |")
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(12,11),layout='constrained')
    labels=dict(reference='C0-R reference',coverage_only='Archive coverage only',volume_proxy='Final-volume proxy',zero_imbalance_proxy='Final-volume + zero-imbalance proxy')
    colors=dict(reference='#555555',coverage_only='#9b79bb',volume_proxy='#008a80',zero_imbalance_proxy='#cc7c14')
    for ax,source in zip(axes,sources):
        rows=[r for r in results if r['source']==source]
        for row in rows:
            points=[p for p in curves if p['source']==source and p['mode']==row['mode']]
            ax.plot(pd.to_datetime([p['session'] for p in points]),[p['equity']*10 for p in points],label=labels[row['mode']],color=colors[row['mode']])
        ax.set(title=f"{source}: {rows[0]['start']} to {rows[0]['end']}",ylabel='Equity (₹ lakh)')
        ax.grid(alpha=.2);ax.legend(loc='upper left',fontsize=8)
    fig.suptitle('Community auction experiment — final-auction proxies, not validated C0-R-X\n₹10 lakh per run; 0.225% cost per side; whole shares',fontsize=13)
    fig.savefig(out/'equity-comparison.png',dpi=150);plt.close(fig)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--download',action='store_true',help='Download the pinned community archives locally')
    args=parser.parse_args()
    if args.download:download_sources(args.output/'raw')
    execute(args.output)
