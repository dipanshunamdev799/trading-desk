"""Versioned ten-year research replay. It never writes paper controls or journals.

The original strategy mandate was 2025–26. This is a separately identified
extension of the same economic rules, with explicit warmup and data limitations.
"""
import argparse
import csv
from datetime import date,datetime,timedelta
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .catalog import CAPITAL,COST
from .data import IST,NIFTY,canonical
from .db import Postgres
from .engine import DataBlocked,features
from .import_duckdb import file_hash
from .reference import sim5,xsim

NIFTY500='NSE_INDEX|Nifty 500'
VERSION='investment-long-history-v2'
TEST_START='2016-11-15'
WARMUP_START='2015-11-15'
TEST_END='2026-11-13'


def native_data(value):
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:native_data(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [native_data(v) for v in value]
    return value


class ResearchStore:
    def __init__(self,db=None):
        self.db=db or Postgres()
        self.schema='investment_research' if self.db.schema=='investment_bots' else self.db.schema
        with self.db.connection() as c:
            c.execute('SELECT pg_advisory_xact_lock(73420201)')
            c.execute(f'CREATE SCHEMA IF NOT EXISTS {self.schema}')
            c.execute(f'''CREATE TABLE IF NOT EXISTS {self.schema}.imports(
                id TEXT PRIMARY KEY,payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS {self.schema}.runs(
                id TEXT PRIMARY KEY,created_at TIMESTAMPTZ DEFAULT now(),manifest TEXT NOT NULL,report TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS {self.schema}.series(
                run_id TEXT,strategy TEXT,session DATE,equity DOUBLE PRECISION,exposure DOUBLE PRECISION,
                PRIMARY KEY(run_id,strategy,session));
                CREATE TABLE IF NOT EXISTS {self.schema}.orders(
                run_id TEXT,strategy TEXT,book INTEGER,sequence INTEGER,payload TEXT NOT NULL,
                PRIMARY KEY(run_id,strategy,book,sequence));
                CREATE TABLE IF NOT EXISTS {self.schema}.rejected_bars(
                import_id TEXT,instrument_key TEXT,session DATE,payload TEXT NOT NULL,
                PRIMARY KEY(import_id,instrument_key,session))''')

    def import_older(self,path,first=WARMUP_START):
        """Read the supplied source once; extend only shared PostgreSQL candles."""
        import duckdb
        source_hash=file_hash(path)
        identity='history-'+hashlib.sha256((source_hash+first+'2025-01-01').encode()).hexdigest()[:20]
        with self.db.connection() as c:
            old=c.execute(f'SELECT payload FROM {self.schema}.imports WHERE id=%s',(identity,)).fetchone()
            if old:return json.loads(old[0])
        source=duckdb.connect(str(path),read_only=True)
        try:
            with self.db.connection() as c:
                c.execute('SELECT pg_advisory_xact_lock(73420201)')
                c.execute('''CREATE TEMP TABLE investment_history_stage(instrument_key TEXT,session DATE,
                    open DOUBLE PRECISION,high DOUBLE PRECISION,low DOUBLE PRECISION,
                    close DOUBLE PRECISION,volume DOUBLE PRECISION,PRIMARY KEY(instrument_key,session)) ON COMMIT DROP''')
                source.execute('''SELECT instrument_key,CAST(ts AS DATE),open,high,low,close,volume
                    FROM candles WHERE interval='1day' AND ts>=? AND ts<'2025-01-01'
                    AND (instrument_key LIKE 'NSE_EQ|%' OR instrument_key IN (?,?))
                    QUALIFY row_number() OVER(PARTITION BY instrument_key,CAST(ts AS DATE) ORDER BY ts DESC)=1
                    ORDER BY instrument_key,ts''',[first,NIFTY,NIFTY500])
                staged=0
                with c.connection.cursor() as writer:
                    while batch:=source.fetchmany(25_000):
                        stream=io.StringIO();csv.writer(stream,lineterminator='\n').writerows(batch);stream.seek(0)
                        writer.copy_expert("COPY investment_history_stage FROM STDIN WITH (FORMAT CSV,NULL '')",stream)
                        staged+=len(batch)
                        if staged%500_000==0:print(f'Staged {staged:,} older daily bars in PostgreSQL.',flush=True)
                valid="least(open,high,low,close)>0 AND high>=low AND greatest(open,high,low,close)<'Infinity'::float8"
                bad=c.execute(f'SELECT * FROM investment_history_stage WHERE NOT({valid})').fetchall()
                for r in bad:
                    c.execute(f'INSERT INTO {self.schema}.rejected_bars VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING',
                              (identity,r[0],r[1],canonical(dict(reason='Original dpanel._read excludes nonpositive/invalid OHLC',
                               open=r[2],high=r[3],low=r[4],close=r[5],volume=r[6]))))
                conflicts=c.execute(f'''SELECT count(*) FROM investment_history_stage a JOIN {self.db.market_table} b
                    ON b.instrument_key=a.instrument_key AND b.interval='1day'
                    AND b.ts=(a.session::timestamp AT TIME ZONE 'Asia/Kolkata') WHERE ({valid.replace('open','a.open').replace('high','a.high').replace('low','a.low').replace('close','a.close')})
                    AND (abs(a.open-b.open)>1e-8 OR abs(a.high-b.high)>1e-8 OR abs(a.low-b.low)>1e-8
                    OR abs(a.close-b.close)>1e-8 OR a.volume IS DISTINCT FROM b.volume)''').fetchone()[0]
                if conflicts:raise DataBlocked(f'{conflicts} older daily bars conflict with PostgreSQL; none overwritten')
                added=c.execute(f'''INSERT INTO {self.db.market_table}
                    (instrument_key,ts,interval,open,high,low,close,volume,oi,source)
                    SELECT instrument_key,(session::timestamp AT TIME ZONE 'Asia/Kolkata'),'1day',
                    open,high,low,close,volume,NULL,'upstox' FROM investment_history_stage
                    WHERE {valid} ON CONFLICT DO NOTHING''').rowcount
                summary=dict(source_sha256=source_hash,first=first,last='2024-12-31',staged=staged,inserted=added,
                             invalid_rows_excluded=len(bad),runtime_storage='PostgreSQL',source_read_only=True)
                c.execute(f'INSERT INTO {self.schema}.imports VALUES(%s,%s)',(identity,canonical(summary)))
            return summary
        finally:source.close()

    def panel(self,first=WARMUP_START,last=TEST_END):
        with self.db.connection() as c:
            all_instruments={r['key']:json.loads(r['payload']) for r in c.execute('SELECT * FROM instruments ORDER BY ordinal')}
            # Written asset class is common equity. The frozen panel also has
            # 279 INF funds and one IN9 partly-paid instrument: neither can enter.
            instruments={k:r for k,r in all_instruments.items() if r['isin'].startswith('INE') and len(r['isin'])==12}
            keys=list(instruments)
            records=c.execute(f'''SELECT DISTINCT ON ((ts AT TIME ZONE 'Asia/Kolkata')::date)
                (ts AT TIME ZONE 'Asia/Kolkata')::date,open,high,low,close FROM {self.db.market_table}
                WHERE interval='1day' AND instrument_key=%s AND ts>=%s AND ts<%s
                ORDER BY (ts AT TIME ZONE 'Asia/Kolkata')::date,ts DESC''',
                (NIFTY,datetime.fromisoformat(first).replace(tzinfo=IST),datetime.fromisoformat(last).replace(tzinfo=IST)+timedelta(days=1))).fetchall()
            calendar=[r[0] for r in records];sessions=[d.isoformat() for d in calendar]
            if not calendar:raise DataBlocked('No PostgreSQL NIFTY daily calendar for this research window')
            day_ix={d:i for i,d in enumerate(calendar)};key_ix={k:i for i,k in enumerate(keys)}
            frames={name:np.full((len(calendar),len(keys)),np.nan) for name in ('o','h','l','c','v')}
            with c.connection.cursor(name='investment_research_panel') as reader:
                reader.itersize=25000
                reader.execute(f'''SELECT DISTINCT ON (instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date)
                    instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date,open,high,low,close,volume
                    FROM {self.db.market_table} WHERE interval='1day' AND ts>=%s AND ts<%s
                    AND instrument_key=ANY(%s) ORDER BY instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date,ts DESC''',
                    (datetime.fromisoformat(first).replace(tzinfo=IST),datetime.fromisoformat(last).replace(tzinfo=IST)+timedelta(days=1),keys))
                while batch:=reader.fetchmany(25000):
                    rows=[r for r in batch if r[1] in day_ix and min(r[2:6])>0 and r[3]>=r[4]]
                    if not rows:continue
                    ii=np.fromiter((day_ix[r[1]] for r in rows),dtype=int)
                    jj=np.fromiter((key_ix[r[0]] for r in rows),dtype=int)
                    vals=np.array([r[2:] for r in rows],dtype=float)
                    for col,name in enumerate(('o','h','l','c','v')):frames[name][ii,jj]=vals[:,col]
            benchmarks={}
            for label,key in [('NIFTY 50 PR',NIFTY),('NIFTY 500 PR',NIFTY500)]:
                rows=c.execute(f'''SELECT (ts AT TIME ZONE 'Asia/Kolkata')::date,close FROM {self.db.market_table}
                    WHERE interval='1day' AND instrument_key=%s AND ts>=%s AND ts<%s ORDER BY ts''',
                    (key,datetime.fromisoformat(first).replace(tzinfo=IST),datetime.fromisoformat(last).replace(tzinfo=IST)+timedelta(days=1))).fetchall()
                benchmarks[label]=np.array([dict(rows).get(d,np.nan) for d in calendar])
        frames={name:pd.DataFrame(v,index=sessions,columns=keys) for name,v in frames.items()}
        return instruments,sessions,frames,benchmarks,dict(original_panel=len(all_instruments),common_equity=len(keys),
                    fund_or_noncommon_removed=len(all_instruments)-len(keys))

    def import_benchmarks(self,path,first=WARMUP_START,last=TEST_END):
        """Include the recent NIFTY 500 rows omitted by the paper-only importer."""
        import duckdb
        from .data import Inputs
        identity='benchmarks-'+hashlib.sha256((file_hash(path)+first+last).encode()).hexdigest()[:20]
        with self.db.connection() as c:
            prior=c.execute(f'SELECT payload FROM {self.schema}.imports WHERE id=%s',(identity,)).fetchone()
            if prior:return json.loads(prior[0])
        source=duckdb.connect(str(path),read_only=True)
        try:
            rows=source.execute('''SELECT instrument_key,CAST(ts AS DATE)::VARCHAR,open,high,low,close,volume
                FROM candles WHERE interval='1day' AND ts>=? AND ts<=? AND instrument_key IN (?,?)
                QUALIFY row_number() OVER(PARTITION BY instrument_key,CAST(ts AS DATE) ORDER BY ts DESC)=1''',
                [first,last,NIFTY,NIFTY500]).fetchall()
        finally:source.close()
        with self.db.connection() as c:
            Inputs(self.db).insert_bars(c,rows)
            report=dict(rows=len(rows),first=first,last=last,indices=[NIFTY,NIFTY500])
            c.execute(f'INSERT INTO {self.schema}.imports VALUES(%s,%s)',(identity,canonical(report)))
        return report


def benchmark_curve(prices,first):
    """One missing reporting mark is disclosed; long gaps invalidate comparison."""
    p=pd.Series(prices,dtype=float)
    marks=p.ffill(limit=1).to_numpy()
    if not np.isfinite(marks[first:]).all():
        raise DataBlocked('Benchmark has missing or stale coverage; a long gap cannot be forward-filled')
    if marks[first]<=0:raise DataBlocked('Invalid benchmark starting price')
    return marks[first:]/marks[first],int(p.iloc[first:].isna().sum())


def metrics(values,days,exposure=None,closed=None):
    values=np.asarray(values,dtype=float)
    if np.isnan(values).any() or not np.isfinite(values).all() or (values<=0).any():
        raise DataBlocked('Invalid equity curve')
    returns=values/np.r_[1.,values[:-1]]-1
    peak=np.maximum.accumulate(np.r_[1.,values])[1:]
    drawdown=values/peak-1
    years=(date.fromisoformat(days[-1])-date.fromisoformat(days[0])).days/365.25
    years=max(years,1/365.25)
    vol=float(np.std(returns,ddof=1)*np.sqrt(252)) if len(returns)>1 else 0.
    sharpe=float(np.mean(returns)/np.std(returns,ddof=1)*np.sqrt(252)) if vol>0 else None
    yearly={};previous=1.
    for year in sorted({d[:4] for d in days}):
        idx=[i for i,d in enumerate(days) if d.startswith(year)]
        last=values[idx[-1]];yearly[year]=float(last/previous-1);previous=last
    trough=int(np.argmin(drawdown));high=int(np.argmax(values[:trough+1]))
    recovered=[i for i in range(trough+1,len(days)) if values[i]>=peak[trough]-1e-12]
    durations=[];count=0
    for d in drawdown:
        count=count+1 if d < -1e-12 else 0;durations.append(count)
    def rolling(n):
        r=values[n:]/values[:-n]-1 if len(values)>n else np.array([])
        return dict(min=float(r.min()),median=float(np.median(r)),max=float(r.max()),positive_fraction=float(np.mean(r>0))) if len(r) else None
    result=dict(total_return=float(values[-1]-1),cagr=float(values[-1]**(1/years)-1),
                final_value_rupees=float(CAPITAL*values[-1]),max_drawdown=float(drawdown.min()),
                annualized_volatility=vol,sharpe_zero_rf=sharpe,worst_day=float(returns.min()),best_day=float(returns.max()),
                annual_returns=yearly,rolling_252_sessions=rolling(252),rolling_756_sessions=rolling(756),
                max_underwater_sessions=int(max(durations,default=0)),
                worst_drawdown=dict(peak=days[high],trough=days[trough],recovery=days[recovered[0]] if recovered else None))
    if exposure is not None:result['average_exposure']=float(np.mean(exposure))
    if closed is not None:
        wins=[t['net_pnl'] for t in closed if t['net_pnl']>0];losses=[-t['net_pnl'] for t in closed if t['net_pnl']<0]
        result.update(closed_positions=len(closed),win_rate=float(len(wins)/len(closed)) if closed else None,
                      profit_factor=float(sum(wins)/sum(losses)) if sum(losses)>0 else None)
    return result


def trade_accounting(results,keys,sessions,integer=False):
    """Track complete position cashflows, including C1 exposure resizes and costs."""
    closed=[];orders=[];open_pnl=0.
    for book,result in enumerate(results):
        active={}
        for sequence,row in enumerate(result['ledger']):
            native={k:int(v) if isinstance(v,np.integer) else float(v) if isinstance(v,np.floating) else v for k,v in row.items()}
            orders.append(dict(book=book,sequence=sequence,**native))
            if row['filled_value']<=0:continue
            stock=row['s'];side=row['side'];amount=row['filled_value'];fee=row['cost']
            if side in ('B','RB'):
                p=active.setdefault(stock,dict(entry=row['t'],cashflow=0.,bought=0.,fees=0.))
                cash=amount+fee if integer else amount
                p['cashflow']-=cash;p['bought']+=cash;p['fees']+=fee
            else:
                if stock not in active:raise DataBlocked('Sell without a recorded research position')
                p=active[stock];p['cashflow']+=amount-fee;p['fees']+=fee
                if side=='S':
                    closed.append(dict(book=book,instrument_key=keys[stock],entry=sessions[p['entry']],exit=sessions[row['t']],
                        net_pnl=float(p['cashflow']),net_return=float(p['cashflow']/p['bought']),fees=float(p['fees']),holding_sessions=row['t']-p['entry']))
                    del active[stock]
        last=len(sessions)-1
        for stock,p in active.items():
            value=result['shares'][stock]*result['_last_marks'][stock]
            open_pnl+=p['cashflow']+value
    return closed,orders,float(open_pnl)


def run_portfolio(a,score,t0,name,*,capital=CAPITAL,cost=COST,phase=0,integer=False,ledger=True):
    tie=np.argsort(np.argsort(np.array(a['keys'])))
    anchor=t0+phase
    kw=dict(cost=cost,tiebreak=tie,integer=integer,ledger=ledger,log=True)
    if name=='C2-S':
        books=[xsim.run(a,score,anchor+j,capital=capital/5,**kw) for j in range(5)]
    elif name=='C1-R':
        shadow=sim5.run(a,score,anchor,cost=cost,tiebreak=tie)
        r=pd.Series(shadow['eq']).pct_change(fill_method=None)
        sigma=r.rolling(20).std()*np.sqrt(252)
        target=(.15/sigma.where(sigma>0)).clip(upper=1).fillna(1).to_numpy()
        books=[xsim.run(a,score,anchor,capital=capital,exposure=target,rebalance_on_exposure=.10,**kw)]
    else:books=[xsim.run(a,score,anchor,capital=capital,**kw)]
    eq=np.mean([np.nan_to_num(b['eq'],nan=1.) for b in books],axis=0)
    exposure=np.sum([np.nan_to_num(b['eq'],nan=1.)*b['expo'] for b in books],axis=0)/np.sum([np.nan_to_num(b['eq'],nan=1.) for b in books],axis=0)
    for b in books:
        b['_last_marks']={s:float(pd.Series(a['c'][:,s]).dropna().iloc[-1]) for s in b['shares']}
    return dict(eq=eq,exposure=exposure,books=books)


def execute(study,start=TEST_START,end=TEST_END,warmup=WARMUP_START):
    instruments,sessions,frames,benchmarks,classification=study.panel(warmup,end)
    first=next(i for i,d in enumerate(sessions) if d>=start)
    if first<84:raise DataBlocked('Not enough pre-test warmup for momentum and volatility')
    keys=list(instruments)
    print(f'PostgreSQL research panel: {len(sessions)} sessions, {len(keys)} common equities; test starts {sessions[first]}.',flush=True)
    universe,scores=features(frames['c'],frames['v'],instruments,start=warmup,end=end)
    a=dict(o=frames['o'].to_numpy(),c=frames['c'].to_numpy(),industry=np.array([r['industry'] for r in instruments.values()]),keys=keys)
    score=scores.to_numpy();days=sessions[first:]
    dataset=hashlib.sha256(canonical(dict(keys=keys,sessions=sessions)).encode())
    for f in ('o','h','l','c','v'):dataset.update(np.ascontiguousarray(frames[f].to_numpy()).view(np.uint8))
    for name,prices in benchmarks.items():
        benchmark_curve(prices,first)  # fail before spending time on simulations
        dataset.update(name.encode());dataset.update(np.ascontiguousarray(prices).view(np.uint8))
    manifest=dict(version=VERSION,start=days[0],end=days[-1],warmup_start=sessions[0],dataset_sha256=dataset.hexdigest(),
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        capital=CAPITAL,cost_per_side=COST,classification=classification,parameters=dict(holdings=20,keep_rank=40,rebalance_sessions=5,industry_cap=6,
        universe_size=300,momentum_sessions=63,volatility_sessions=42,volatility_target=.15,exposure_band=.10),
        universe='Frozen retained 2026 stock snapshot; date-causal price/liquidity eligibility; survivorship biased',
        industry='Frozen static 2026 labels; not point-in-time',accounting='Fractional reference; no cash dividends; no leverage',
        shadow='C0-R shadow starts on the first test decision; E=1 until 20 returns',
        signal_warmup='Price indicators use pre-test observations; no positions/profits from warmup are carried into the test',
        phase_policy='Phase 0 baseline fixed in advance; phases 1–4 are robustness checks, never selected for the headline')
    run_id='tenyear-'+hashlib.sha256(canonical(manifest).encode()).hexdigest()[:20]
    reports={};series={};order_rows=[];trade_rows=[];baselines={};sensitivities={}
    for name in ('C0-R','C1-R','C2-S'):
        print('Running '+name+' baseline and robustness checks.',flush=True)
        result=run_portfolio(a,score,first,name)
        closed,orders,open_pnl=trade_accounting(result['books'],keys,sessions)
        m=metrics(result['eq'][first:],days,result['exposure'][first:],closed)
        reconciliation=sum(t['net_pnl'] for t in closed)+open_pnl-CAPITAL*(result['eq'][-1]-1)
        if abs(reconciliation)>.05:raise DataBlocked(f'{name} cashflow accounting disagrees by ₹{reconciliation}')
        m['cashflow_reconciliation_error_rupees']=float(reconciliation)
        m['orders']=int(sum(r['filled_value']>0 for r in orders))
        reports[name]=m;baselines[name]=result
        series[name]=dict(equity=result['eq'][first:],exposure=result['exposure'][first:])
        trade_rows.extend(dict(strategy=name,**t) for t in closed)
        order_rows.extend(dict(strategy=name,**r) for r in orders)
        phases=[dict(phase=0,**{k:m[k] for k in ('cagr','max_drawdown')})]
        for phase in range(1,5):
            p=run_portfolio(a,score,first,name,phase=phase,ledger=False)
            pm=metrics(p['eq'][first:],days)
            phases.append(dict(phase=phase,cagr=pm['cagr'],max_drawdown=pm['max_drawdown']))
        cost_results=[]
        for rate in (0.,.0045):
            p=run_portfolio(a,score,first,name,cost=rate,ledger=False)
            pm=metrics(p['eq'][first:],days)
            cost_results.append(dict(cost_per_side=rate,cagr=pm['cagr'],max_drawdown=pm['max_drawdown']))
        whole=run_portfolio(a,score,first,name,integer=True,ledger=False)
        wm=metrics(whole['eq'][first:],days,whole['exposure'][first:])
        sensitivities[name]=dict(phases=phases,costs=cost_results,whole_share=dict(cagr=wm['cagr'],max_drawdown=wm['max_drawdown'],final_value_rupees=wm['final_value_rupees']))
        # Independent frozen value engine must agree with the share engine.
        if name=='C0-R':
            ref=sim5.run(a,score,first,tiebreak=np.argsort(np.argsort(np.array(keys))));err=float(np.nanmax(np.abs(ref['eq']-result['eq'])))
            if err>1e-10:raise DataBlocked(f'Long-history sim5/xsim disagreement: {err}')
            m['independent_engine_max_error']=err
    for name,prices in benchmarks.items():
        e,filled=benchmark_curve(prices,first);series[name]=dict(equity=e,exposure=np.ones(len(e)))
        reports[name]=metrics(e,days)
        reports[name]['forward_filled_reporting_marks']=filled
    snapshots=0
    with study.db.connection() as c:snapshots=c.execute('SELECT count(*) FROM snapshots WHERE session>=%s AND session<=%s',(days[0],days[-1])).fetchone()[0]
    reports['C0-R-X']=dict(status='NOT_BACKTESTABLE',reason='Historical pre-open auction evidence absent; no fill-performance estimate can be validated',
                         auction_snapshots=snapshots,assumed_full_fill_reference='C0-R is its assumed-full-fill reference, not an execution-validated C0-R-X result')
    # Inspect held >40% close-to-close moves: do not repair or delete profitable
    # or losing events using hindsight. They are disclosed as source limitations.
    moves=frames['c'].to_numpy()/np.vstack([np.full((1,len(keys)),np.nan),frames['c'].to_numpy()[:-1]])-1
    anomalies=[]
    for t,s in np.argwhere(np.abs(moves)>.40):
        if t<first:continue
        exposures={}
        for name,result in baselines.items():
            held=sum(b['snaps'].get(int(t)-1,{}).get(int(s),0.)/len(result['books']) for b in result['books'])
            if held:exposures[name]=float(held/result['eq'][t-1])
        anomalies.append(dict(session=sessions[t],instrument_key=keys[s],symbol=instruments[keys[s]]['symbol'],
                               close_to_close_return=float(moves[t,s]),previous_close_weights=exposures))
    for name,result in baselines.items():
        reports[name]['holding_marks_without_current_close']=sum(
            int(np.isnan(a['c'][t,s])) for b in result['books'] for t,held in b['snaps'].items()
            if t>=first for s in held)
    missing=(universe.shift(1,fill_value=False)&frames['c'].isna()).sum(axis=1)
    required=universe.shift(1,fill_value=False).sum(axis=1)
    incomplete=[dict(session=sessions[t],missing=int(missing.iloc[t]),required=int(required.iloc[t]))
                for t in range(first,len(sessions)) if required.iloc[t]>0 and missing.iloc[t]/required.iloc[t]>.02]
    test_universe=universe.loc[days]
    # A conservative missing-data scenario masks whole deficient sessions.
    # It changes no prices retrospectively and does not invent unavailable bars.
    masked={name:frame.copy() for name,frame in frames.items()}
    bad_days=[r['session'] for r in incomplete]
    for frame in masked.values():frame.loc[bad_days]=np.nan
    if bad_days:
        _,masked_scores=features(masked['c'],masked['v'],instruments,start=warmup,end=end)
        masked_a=dict(a,o=masked['o'].to_numpy(),c=masked['c'].to_numpy())
        for name in ('C0-R','C1-R','C2-S'):
            p=run_portfolio(masked_a,masked_scores.to_numpy(),first,name,ledger=False)
            qm=metrics(p['eq'][first:],days,p['exposure'][first:])
            sensitivities[name]['whole_day_missing_price_stress']={k:qm[k] for k in ('cagr','max_drawdown','final_value_rupees')}
    report=dict(manifest=manifest,ranking=sorted((k for k in ('C0-R','C1-R','C2-S')),key=lambda k:reports[k]['cagr'],reverse=True),
                strategies=reports,sensitivity=sensitivities,large_move_events=anomalies,
                incomplete_sessions=incomplete,
                quality_policy='Baseline uses the frozen economic engine; a separately reported stress masks all prices on the three >2% incomplete sessions. Paper operational gates would pause on those sessions.',
                universe_counts_by_year={year:dict(min=int(test_universe.loc[test_universe.index.str.startswith(year)].sum(axis=1).min()),
                    median=float(test_universe.loc[test_universe.index.str.startswith(year)].sum(axis=1).median())) for year in sorted({d[:4] for d in days})},
                limitations=['Survivorship bias: frozen retained stock list; delisted securities are not comprehensively represented',
                    'Static industry labels and frozen panel admission use later information',
                    'Price returns only; dividends, spinoff entitlements and cash interest are not credited',
                    '617 corporate-action records cover only a recent feed window; older split/demerger validation is incomplete',
                    'Official-opening-price fills are theoretical, not observed executable fills',
                    'C0-R-X cannot be validated without historical auction evidence',
                    'Reference engine replay: missing-bar sessions retain last valid marks; this is not a claim that all paper operational gates would have permitted uninterrupted processing',
                    'Retrospective versioned research; not an unbiased live-performance estimate'],
                generated_at=datetime.now(IST).isoformat(),real_orders_submitted=0)
    report=native_data(report)
    with study.db.connection() as c:
        c.execute(f'INSERT INTO {study.schema}.runs(id,manifest,report) VALUES(%s,%s,%s) ON CONFLICT(id) DO UPDATE SET report=EXCLUDED.report',
                  (run_id,canonical(manifest),canonical(report)))
        c.execute(f'DELETE FROM {study.schema}.series WHERE run_id=%s',(run_id,))
        c.executemany(f'INSERT INTO {study.schema}.series VALUES(%s,%s,%s,%s,%s)',
            [(run_id,name,day,float(row['equity'][i]),float(row['exposure'][i])) for name,row in series.items() for i,day in enumerate(days)])
        c.execute(f'DELETE FROM {study.schema}.orders WHERE run_id=%s',(run_id,))
        c.executemany(f'INSERT INTO {study.schema}.orders VALUES(%s,%s,%s,%s,%s)',
            [(run_id,r['strategy'],r['book'],r['sequence'],canonical(r)) for r in order_rows])
    return run_id,report,days,series,trade_rows


def export(run_id,report,days,series,trades,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    (folder/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    pd.DataFrame([dict(strategy=n,**{k:v for k,v in m.items() if not isinstance(v,(dict,list))}) for n,m in report['strategies'].items()]).to_csv(folder/'summary.csv',index=False)
    pd.DataFrame({name:{y:r for y,r in m['annual_returns'].items()} for name,m in report['strategies'].items() if 'annual_returns' in m}).to_csv(folder/'annual-returns.csv')
    pd.DataFrame({name:r['equity'] for name,r in series.items()},index=days).to_csv(folder/'equity.csv',index_label='session')
    pd.DataFrame(trades).to_csv(folder/'closed-positions.csv',index=False)
    pd.DataFrame(report['large_move_events']).to_csv(folder/'large-moves.csv',index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,(ax,dd)=plt.subplots(2,1,figsize=(13,9),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    colors=['#007f6d','#2466ad','#d47714','#555c66','#9a6552']
    dates=pd.to_datetime(days)
    for color,(name,r) in zip(colors,series.items()):
        ax.plot(dates,r['equity'],label=name,color=color,linewidth=1.5)
        curve=r['equity']/np.maximum.accumulate(np.r_[1.,r['equity']])[1:]-1
        dd.plot(dates,curve*100,label=name,color=color,linewidth=1)
    ax.set_yscale('log');ax.set_ylabel('Equity / initial capital (log scale)');ax.legend(ncol=3,frameon=False)
    ax.set_title('Investment bots: ten-year retrospective replay\nFrozen survivor universe; static industries; theoretical open fills; 0.225% per side',loc='left')
    dd.set_ylabel('Drawdown (%)');dd.set_xlabel(f'{days[0]} to {days[-1]} | C0-R-X unavailable: historical auction evidence missing')
    for panel in (ax,dd):panel.grid(alpha=.18);panel.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(folder/'equity-and-drawdown.png',dpi=170);plt.close(fig)
    lines=['# Investment bots — ten-year research replay','',f'Run: `{run_id}`. PostgreSQL is the source and primary result store.','',
        f'Test: {days[0]} to {days[-1]}. Indicator warmup starts {report["manifest"]["warmup_start"]}.',
        '', '**These are survivorship-biased, retrospective reference results. They do not establish an executable trading edge.**','',
        '| Strategy | CAGR | Total return | Max drawdown | ₹10 lakh became | Closed positions |',
        '|---|---:|---:|---:|---:|---:|']
    for name in report['ranking']+['NIFTY 50 PR','NIFTY 500 PR']:
        m=report['strategies'][name]
        lines.append(f'| {name} | {m["cagr"]:.2%} | {m["total_return"]:.2%} | {m["max_drawdown"]:.2%} | ₹{m["final_value_rupees"]:,.0f} | {m.get("closed_positions","—")} |')
    lines+=['','C0-R-X: no valid ten-year execution-gated backtest is possible without the historical auction observations.','',
            '## Interpretation limits','']+['- '+s for s in report['limitations']]
    lines+=['','## Source-data audit','',
        f'{len(report["incomplete_sessions"])} sessions exceeded the 2% missing prior-universe data limit. The baseline reference engine carries last marks; the paper application would pause processing. A whole-day missing-price stress is reported separately.',
        '', '| Session | Missing required instruments | Required instruments |','|---|---:|---:|']
    lines += [f'| {r["session"]} | {r["missing"]} | {r["required"]} |' for r in report['incomplete_sessions']]
    lines+=['','The AURUM/formerly-Majesco price gap on 23 Dec 2020 coincides with a large cash distribution. The issuer confirmed a ₹974/share dividend. This price-only engine omits the cash credit; that gap must not be interpreted as the investor\'s total economic loss. [Issuer dividend notice](https://strapi.aurumproptech.in/uploads/Majesco_Communication_on_TDS_on_Dividend_d6479330ee.pdf).',
        '', '## Robustness checks','', '| Strategy | Five-phase CAGR range | Double-cost CAGR | Whole-share CAGR | Missing-day stress CAGR |',
        '|---|---:|---:|---:|---:|']
    for name,s in report['sensitivity'].items():
        phases=[r['cagr'] for r in s['phases']];stress=s.get('whole_day_missing_price_stress',{}).get('cagr',report['strategies'][name]['cagr'])
        doubled=next(r['cagr'] for r in s['costs'] if r['cost_per_side']==.0045)
        lines.append(f'| {name} | {min(phases):.2%}–{max(phases):.2%} | {doubled:.2%} | {s["whole_share"]["cagr"]:.2%} | {stress:.2%} |')
    lines+=['','Price-index benchmarks exclude reinvested cash dividends. [NSE Indices explains price versus total-return indices](https://www.niftyindices.com/resources/index-concepts/total-return-index).',
            '', 'Annual results, cost stress, five rebalance phases, whole-share sensitivity, suspicious large price moves and rolling returns are in the accompanying JSON/CSV exports. Phase 0 is always the headline; no winning phase or parameter was selected.']
    (folder/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,help='Optional one-time source import; otherwise replay PostgreSQL data only')
    parser.add_argument('--output',type=Path,default=Path('artifacts/investment_bots/ten-year'))
    args=parser.parse_args()
    store=ResearchStore()
    if args.source:
        print(json.dumps(store.import_older(args.source),indent=2),flush=True)
        print(json.dumps(store.import_benchmarks(args.source),indent=2),flush=True)
    run_id,report,days,series,trades=execute(store)
    export(run_id,report,days,series,trades,args.output)
    print(canonical(dict(run_id=run_id,ranking=report['ranking'],strategies={n:{k:m.get(k) for k in ('cagr','max_drawdown','final_value_rupees','status')} for n,m in report['strategies'].items()})),flush=True)
