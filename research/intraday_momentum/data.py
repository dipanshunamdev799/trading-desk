"""Primary Upstox acquisition and PostgreSQL-only intraday study inputs.

Community text, cohort metadata, plans, audits and results stay in local files.
Only authentic, unmodified Upstox OHLCV observations are inserted in the existing
public.candles table. No table creation or application/bot controls are used.
"""
from __future__ import annotations

import argparse
from collections import Counter,deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import date, datetime, timedelta
import gzip
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/intraday_momentum'
UNIVERSE=ROOT/'artifacts/swing_discovery/universe.json'
LEGACY=ROOT/'artifacts/stock_swing_research'
START='2024-11-14';END='2026-11-13';WARMUP='2024-07-01'
TZ='Asia/Kolkata';NIFTY='NSE_INDEX|Nifty 50'
FIELDS=('open','high','low','close','volume')
REQUIRED_BARS=72  # 09:15..15:10, including the hard-exit opening observation.
_lock=threading.Lock();_last_request=0.;_local=threading.local()
_request_times=deque()


def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str),encoding='utf-8');tmp.replace(path)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _settings():
    sys.path.insert(0,str(ROOT/'backend'))
    from app.config import get_settings
    return get_settings()


@contextmanager
def connection(write=False):
    import psycopg2
    from psycopg2.extras import DictCursor
    dsn=_settings().database_url_sync.replace('postgresql+psycopg2://','postgresql://')
    raw=psycopg2.connect(dsn,application_name='intraday-momentum-upstox-data',
        options='-c search_path=public -c default_transaction_read_only='+('off' if write else 'on'))
    raw.set_session(readonly=not write)
    try:
        with raw.cursor(cursor_factory=DictCursor) as c:
            yield c
        if write:raw.commit()
        else:raw.rollback()
    except BaseException:raw.rollback();raise
    finally:raw.close()


def _client():
    if not hasattr(_local,'client'):
        from upstox_analytics import UpstoxAnalyticsClient
        _local.client=UpstoxAnalyticsClient(analytics_token=_settings().upstox_analytics_token,
                                           timeout=25,max_retries=1)
    return _local.client


def _slot():
    global _last_request
    while True:
        with _lock:
            now=time.monotonic()
            while _request_times and now-_request_times[0]>=1801:_request_times.popleft()
            delay=max(0.,.26-(now-_last_request))
            # Published standard API budget: 2,000 / 30min. Reserve headroom
            # for retries and the user's already-running application readers.
            if len(_request_times)>=1750:delay=max(delay,_request_times[0]+1801-now)
            if delay<=0:
                _request_times.append(now);_last_request=now;return
        time.sleep(min(delay,20.))


def _month_end(month):
    d=date.fromisoformat(month+'-01')
    return ((d.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)).isoformat()


def _previous_month(month):return (date.fromisoformat(month+'-01')-timedelta(days=1)).strftime('%Y-%m')


def _rows(payload):
    if isinstance(payload,dict):payload=payload.get('payload',payload)
    if isinstance(payload,dict):payload=payload.get('data',payload)
    if not isinstance(payload,dict) or not isinstance(payload.get('candles'),list):
        raise ValueError('Upstox response has no candle array')
    return payload['candles']


def _validated_rows(payload,key,interval,first,last):
    """Validate/deduplicate authentic rows; do not adjust any source number."""
    found={};duplicates=0
    for row in _rows(payload):
        if not isinstance(row,(list,tuple)) or len(row)<6:raise ValueError('Malformed candle row')
        ts=pd.Timestamp(row[0])
        if ts.tzinfo is None:raise ValueError('Source timestamp lacks timezone')
        ts=ts.tz_convert(TZ)
        if not first<=ts.date().isoformat()<=last:continue
        if interval=='5minute' and (ts.minute%5 or ts.second or ts.microsecond):
            raise ValueError('Source timestamp is not a five-minute grid start')
        vals=[float(x) for x in row[1:6]]
        if not np.isfinite(vals).all() or min(vals[:4])<=0 or vals[4]<0:
            raise ValueError('Invalid source price/volume')
        o,h,l,c,v=vals
        if h<max(o,c,l)-1e-8 or l>min(o,c,h)+1e-8:raise ValueError('Inconsistent source OHLC')
        oi=None if len(row)<7 or row[6] is None else float(row[6])
        if oi is not None and not np.isfinite(oi):raise ValueError('Invalid source OI')
        value=(key,ts.to_pydatetime(),interval,o,h,l,c,v,oi,'upstox')
        if ts in found:
            duplicates+=1
            if found[ts]!=value:raise ValueError('Conflicting source duplicate timestamp')
        found[ts]=value
    return list(found.values()),duplicates


def _same(a,b):
    return all((x is None and y is None) or (x is not None and y is not None and abs(float(x)-float(y))<=1e-8)
               for x,y in zip(a,b))


def insert_raw(payload,key,interval,first,last):
    """Atomic raw-source import. Existing conflicting candles are never replaced."""
    from psycopg2.extras import execute_values
    rows,duplicates=_validated_rows(payload,key,interval,first,last)
    if not rows:return dict(source_rows=0,inserted=0,duplicates=duplicates)
    times=[r[1] for r in rows]
    with connection(write=True) as c:
        c.execute('SELECT pg_advisory_xact_lock(hashtext(%s))',(key+'|'+interval,))
        c.execute('SELECT ts,open,high,low,close,volume,oi,source FROM public.candles '
                  'WHERE instrument_key=%s AND interval=%s AND ts=ANY(%s)',(key,interval,times))
        existing={r[0]:r for r in c.fetchall()}
        for r in rows:
            old=existing.get(r[1])
            if old is not None and (old[-1]!='upstox' or not _same(old[1:7],r[3:9])):
                raise ValueError('PostgreSQL candle conflict; entire source job refused: '+key+' '+str(r[1]))
        execute_values(c,'INSERT INTO public.candles(instrument_key,ts,interval,open,high,low,close,volume,oi,source) VALUES %s '
                       'ON CONFLICT(instrument_key,interval,ts) DO NOTHING',rows,page_size=2000)
        # Detect any concurrent conflicting writer rather than silently accepting
        # its values after ON CONFLICT. A mismatch rolls back this entire job.
        c.execute('SELECT ts,open,high,low,close,volume,oi,source FROM public.candles '
                  'WHERE instrument_key=%s AND interval=%s AND ts=ANY(%s)',(key,interval,times))
        after={r[0]:r for r in c.fetchall()}
        for r in rows:
            old=after.get(r[1])
            if old is None or old[-1]!='upstox' or not _same(old[1:7],r[3:9]):
                raise ValueError('Concurrent PostgreSQL candle conflict; source job rolled back')
    return dict(source_rows=len(rows),inserted=len(rows)-len(existing),duplicates=duplicates)


def _fetch(key,unit,interval,first,last,path):
    if path.exists():
        doc=json.loads(gzip.decompress(path.read_bytes()))
        if (doc['instrument_key'],doc['unit'],doc['interval'],doc['from_date'],doc['to_date'])!=(key,unit,interval,first,last):
            raise ValueError('Cached request identity mismatch')
        return doc,True
    _slot();payload=_client().get_historical_candles_v3(key,unit,interval,last,first)
    doc=dict(provider='upstox',instrument_key=key,unit=unit,interval=interval,from_date=first,to_date=last,
             fetched_at=datetime.now().astimezone().isoformat(),payload=payload)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(doc,allow_nan=False).encode(),mtime=0))
    return doc,False


def _daily(specs):
    keys=[s['instrument_key'] for s in specs]
    with connection() as c:
        c.execute('SELECT DISTINCT ON(instrument_key,(ts AT TIME ZONE %s)::date) '
                  'instrument_key,(ts AT TIME ZONE %s)::date,open,high,low,close,volume FROM public.candles '
                  "WHERE interval=%s AND instrument_key=ANY(%s) AND ts>=%s AND ts<%s AND source='upstox' "
                  'ORDER BY instrument_key,(ts AT TIME ZONE %s)::date,ts DESC',
                  (TZ,TZ,'1day',keys+[NIFTY],WARMUP+' 00:00:00+05:30',END+' 23:59:59+05:30',TZ))
        records=c.fetchall()
    frame=pd.DataFrame(records,columns=['key','day',*FIELDS]);frame['day']=frame['day'].astype(str)
    calendar=sorted(frame.loc[frame.key==NIFTY,'day'].unique().tolist())
    if not calendar:raise ValueError('PostgreSQL NIFTY daily calendar unavailable')
    eq=frame[frame.key!=NIFTY]
    panels={f:eq.pivot(index='day',columns='key',values=f).reindex(index=calendar,columns=keys) for f in FIELDS}
    return calendar,panels


def prepare(out=OUT):
    from .units import load_audit,price_factor,UnitBasisError
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cohort=json.loads(UNIVERSE.read_text(encoding='utf-8'));specs=cohort['stocks']
    assert len(specs)==500 and len({s['instrument_key'] for s in specs})==500
    daily_dispositions=[]
    with connection() as c:
        c.execute("SELECT instrument_key,count(*) FROM public.candles WHERE interval='1day' AND instrument_key=ANY(%s) AND source='upstox' GROUP BY 1",
                  ([s['instrument_key'] for s in specs],))
        have=dict(c.fetchall())
    for spec in specs:
        key=spec['instrument_key']
        if key in have:continue
        path=out/'raw'/key.replace('|','_')/'daily.json.gz'
        try:
            doc,cached=_fetch(key,'days',1,WARMUP,END,path)
            result=insert_raw(doc,key,'1day',WARMUP,END)
            daily_dispositions.append(dict(key=key,symbol=spec['symbol'],status='imported' if result['source_rows'] else 'unavailable',
                                           path=str(path),sha256=sha(path),cached=cached,**result))
        except Exception as exc:
            daily_dispositions.append(dict(key=key,symbol=spec['symbol'],status='unavailable',
                                           error_type=type(exc).__name__,status_code=getattr(exc,'status_code',None)))
    calendar,p=_daily(specs);previous=p['close'].shift(1)
    adv=(p['close']*p['volume']).rolling(63,min_periods=50).median().shift(1)
    unit_audit=load_audit(out);factors=pd.DataFrame(1.,index=calendar,columns=previous.columns)
    unit_blocked=[]
    for key in factors.columns:
        for day in calendar:
            if not START<=day<=END:continue  # warmup admission is never traded
            try:factors.loc[day,key]=price_factor(key,day,unit_audit)
            except UnitBasisError as exc:
                factors.loc[day,key]=np.nan;unit_blocked.append(dict(key=key,day=day,reason=str(exc)))
    # Raw price*volume already preserves traded value under the verified
    # reciprocal provider adjustment. The absolute ₹50 floor needs actual units.
    eligible=(previous*factors>=50)&(adv>=5e7)&factors.notna()
    # Dated primary-source action metadata is local research evidence only.
    # Ex-date distributions/unit changes must not masquerade as momentum.
    action_path=LEGACY/'nse-actions-all.json';excluded_actions=[]
    actions=json.loads(action_path.read_text(encoding='utf-8'))
    extension_path=out/'unit-audit/nse-actions-2026-11-10-13.json'
    extension=json.loads(extension_path.read_text()) if extension_path.exists() else {}
    actions+=extension.get('data',[])
    for spec in specs:
        symbols={spec['symbol'],spec.get('current_symbol')}
        isins={spec['isin_at_start'],spec['instrument_key'].split('|')[-1]}
        for action in actions:
            if action.get('symbol') not in symbols and action.get('isin') not in isins:continue
            subject=str(action.get('subject','')).lower()
            if not any(word in subject for word in ('dividend','bonus','split','rights','demerg','scheme','amalgam','merger','consolidation')):continue
            try:day=pd.Timestamp(datetime.strptime(action['exDate'],'%d-%b-%Y')).date().isoformat()
            except (ValueError,KeyError):continue
            if day in eligible.index:
                eligible.loc[day,spec['instrument_key']]=False
                excluded_actions.append(dict(key=spec['instrument_key'],day=day,subject=action.get('subject')))
    hit=eligible&((p['high']>=previous*1.08)|(p['low']<=previous*.92))
    hit.loc[[d for d in calendar if not START<=d<=END]]=False
    candidates=[];context=[];jobs={};by_key={s['instrument_key']:s for s in specs}
    for key in hit.columns:
        for day in calendar:
            if not START<=day<=END or not eligible.loc[day,key]:continue
            rec=dict(key=key,symbol=by_key[key]['symbol'],day=day,
                raw_prev_close=float(previous.loc[day,key]),price_factor=float(factors.loc[day,key]),
                prev_close=float(previous.loc[day,key]*factors.loc[day,key]),adv=float(adv.loc[day,key]))
            context.append(rec)
            if hit.loc[day,key]:
                candidates.append(rec)
                for month in (day[:7],_previous_month(day[:7])):
                    ident=key+'|'+month
                    jobs[ident]=dict(id=ident,key=key,symbol=by_key[key]['symbol'],month=month,first=month+'-01',last=min(_month_end(month),END))
    plan=dict(version='intraday-stock-data-v2-contemporaneous-units',start=START,end=END,warmup=WARMUP,calendar=calendar,
        universe_sha256=sha(UNIVERSE),source_universe=str(UNIVERSE),cohort=cohort,
        daily_dispositions=daily_dispositions,candidates=sorted(candidates,key=lambda r:(r['day'],r['key'])),
        unit_adjustment_sha256=sha(out/'unit-audit/unit-adjustment-audit.json'),unit_basis_blocked=unit_blocked,
        unit_policy='Restore actual share units locally. Admission prior close uses current-day factor. Raw adjusted price*volume preserves ADV; same-clock RVOL computed before restoring day bars.',
        action_metadata=dict(path=str(action_path),sha256=sha(action_path),coverage_end='2026-11-13' if extension.get('data') is not None else '2026-11-09',excluded_exdates=excluded_actions,
                             extension_path=str(extension_path),extension_sha256=sha(extension_path) if extension_path.exists() else None,
                             policy='Exclude known capital-action and dividend exdates; no NSE prices or metadata written to PostgreSQL'),
        jobs=sorted(jobs.values(),key=lambda r:(r['key'],r['month'])),
        universe_dispositions=[dict(key=s['instrument_key'],symbol=s['symbol'],daily_rows=int(p['close'][s['instrument_key']].notna().sum()),
            eligible_days=int(eligible.loc[[d for d in calendar if START<=d<=END],s['instrument_key']].sum()),
            potential_event_days=int(hit[s['instrument_key']].sum())) for s in specs],
        selection='Daily extreme screen is acquisition-only; strategy must cross threshold causally on completed five-minute bars',
        frozen_at=datetime.now().astimezone().isoformat())
    dump(out/'daily-context.json',context);dump(out/'jobs-plan.json',plan)
    print(f"Plan: {len(specs)} cohort names, {len(candidates)} potential event stock-days, {len(jobs)} current/prior-month jobs.",flush=True)
    return plan


def _legacy_file(job):
    # Exact date-bound raw responses from the earlier primary Upstox acquisition.
    for f in sorted((LEGACY/'raw'/job['symbol']).glob(job['first']+'-*.json')):
        doc=json.loads(f.read_text(encoding='utf-8'))
        if doc.get('instrument_key')!=job['key']:continue
        if (doc.get('from'),doc.get('to'))!=(job['first'],job['last']):continue
        # November 2026's earlier response ends Nov 9: do not pretend it covers
        # the extended Nov 13 endpoint. Fetch the complete requested month.
        if f.stem.split('-')[-3:]!=job['last'].split('-'):continue
        return f,doc
    return None,None


def _one(job,out):
    path=out/'raw'/job['key'].replace('|','_')/(job['month']+'-5minute.json.gz')
    try:
        old,doc=_legacy_file(job)
        if old is not None:
            payload=doc;source_path=old;cached=True;source_kind='existing_primary_upstox_response'
        else:
            payload,cached=_fetch(job['key'],'minutes',5,job['first'],job['last'],path)
            source_path=path;source_kind='primary_upstox_http'
        imported=insert_raw(payload,job['key'],'5minute',job['first'],job['last'])
        return dict(**job,status='ok' if imported['source_rows'] else 'empty',path=str(source_path),sha256=sha(source_path),
                    cached=cached,source_kind=source_kind,**imported)
    except Exception as exc:
        # Do not print response URLs/headers/tokens in acquisition logs.
        return dict(**job,status='failed',error_type=type(exc).__name__,reason=str(exc)[:220] if isinstance(exc,ValueError) else None,
                    status_code=getattr(exc,'status_code',None))


def acquire(plan,out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);started=time.monotonic();results=[]
    old_path=out/'acquisition-manifest.json';prior={}
    if old_path.exists():
        old=json.loads(old_path.read_text())
        if old.get('plan_sha256')!=sha(out/'jobs-plan.json'):raise ValueError('Cannot resume a changed acquisition plan')
        prior={r['id']:r for r in old['jobs']}
    todo=[]
    for job in plan['jobs']:
        old=prior.get(job['id'])
        if old and old.get('status')=='ok' and Path(old['path']).exists() and sha(old['path'])==old['sha256']:
            results.append(old)
        else:todo.append(job)
    print(f"Acquisition resume: {len(results)} completed source jobs retained, {len(todo)} to fetch/import.",flush=True)
    with (out/'acquisition-jobs.jsonl').open('a',encoding='utf-8') as log,ThreadPoolExecutor(max_workers=4) as pool:
        pending={pool.submit(_one,job,out):job for job in todo}
        for future in as_completed(pending):
            result=future.result();results.append(result);log.write(json.dumps(result,allow_nan=False,default=str)+'\n');log.flush()
            if len(results)%50==0 or len(results)==len(plan['jobs']):
                progress=dict(jobs_done=len(results),jobs_total=len(plan['jobs']),statuses=dict(Counter(r['status'] for r in results)),
                              rows=sum(r.get('source_rows',0) for r in results),inserted=sum(r.get('inserted',0) for r in results),
                              elapsed_seconds=round(time.monotonic()-started,1))
                dump(out/'acquisition-progress.json',progress);print(progress,flush=True)
    manifest=dict(version=plan['version'],plan_sha256=sha(out/'jobs-plan.json'),jobs=sorted(results,key=lambda r:r['id']),
        lineage=old.get('lineage',[]) if old_path.exists() else [],
        elapsed_seconds=time.monotonic()-started,storage='Authentic primary Upstox candles in public.candles; local provenance/results')
    dump(out/'acquisition-manifest.json',manifest);return manifest


def _regular_frames(rows):
    """Return complete, valid regular sessions and quarantine reasons."""
    if not rows:return {},Counter()
    frame=pd.DataFrame(rows,columns=['ts',*FIELDS]);frame['ts']=pd.to_datetime(frame.ts,utc=True).dt.tz_convert(TZ)
    frame=frame.set_index('ts').sort_index();valid={};reasons=Counter()
    for day,group in frame.groupby(frame.index.date):
        # Data after the hard15:10 exit is not needed. In particular a later
        # closing-auction schedule must not censor otherwise usable mornings.
        regular=group.between_time('09:15','15:10')
        expected=pd.date_range(str(day)+' 09:15',periods=REQUIRED_BARS,freq='5min',tz=TZ)
        if len(regular)!=REQUIRED_BARS or not regular.index.equals(expected):reasons['missing_or_duplicate_required_bars']+=1;continue
        vals=regular[list(FIELDS)].to_numpy(float)
        invalid=(not np.isfinite(vals).all() or (vals[:,:4]<=0).any() or (vals[:,4]<0).any() or
            (regular.high<regular[['open','close','low']].max(axis=1)-1e-8).any() or
            (regular.low>regular[['open','close','high']].min(axis=1)+1e-8).any())
        if invalid:reasons['invalid_ohlcv_session']+=1;continue
        valid[str(day)]=regular[list(FIELDS)].astype(float)
    return valid,reasons


def load_sessions(plan,out=OUT):
    from .units import load_audit,price_factor,restore_bars,current_basis_prev_close
    out=Path(out);grouped={};records=[];dispositions=[]
    unit_audit=load_audit(out)
    if plan.get('unit_adjustment_sha256')!=sha(out/'unit-audit/unit-adjustment-audit.json'):
        raise ValueError('Regenerate/rebase the acquisition plan after the verified share-unit audit before loading results')
    for r in plan['candidates']:grouped.setdefault(r['key'],[]).append(r)
    manifest=json.loads((out/'acquisition-manifest.json').read_text())
    jobs={r['id']:r for r in manifest['jobs']};calendar=plan['calendar'];counts=Counter()
    for key,events in grouped.items():
        first=min(_previous_month(r['day'][:7])+'-01' for r in events)
        last=max(r['day'] for r in events)
        with connection() as c:
            c.execute('SELECT ts,open,high,low,close,volume FROM public.candles WHERE instrument_key=%s AND interval=%s '
                      'AND ts>=%s AND ts<%s AND source=%s ORDER BY ts',
                      (key,'5minute',first,last+' 23:59:59+05:30','upstox'))
            valid,reasons=_regular_frames(c.fetchall())
        counts.update(reasons)
        # A refused/conflicting source month must not sneak back into the RVOL
        # denominator through candles retained by an earlier application fetch.
        valid={day:bars for day,bars in valid.items()
               if jobs.get(key+'|'+day[:7],{}).get('status')=='ok'}
        cumulative={day:f.volume.cumsum().to_numpy() for day,f in valid.items()}
        for event in events:
            day=event['day'];status=jobs.get(key+'|'+day[:7],{}).get('status')
            if status!='ok':reason='current_month_source_job_'+str(status)
            elif day not in valid:reason='candidate_session_missing_or_quarantined'
            else:reason=None
            if reason:
                counts[reason]+=1;dispositions.append(dict(**event,status=reason));continue
            earlier=[d for d in calendar if d<day][-20:]
            history=[cumulative[d] for d in earlier if d in cumulative]
            raw_bars=valid[day]
            baseline=np.median(np.vstack(history),axis=0) if len(history)>=10 else np.full(REQUIRED_BARS,np.nan)
            rvol=pd.Series(np.divide(cumulative[day],baseline,out=np.full(REQUIRED_BARS,np.nan),where=baseline>0),index=raw_bars.index,name='rvol')
            if len(history)<10:counts['candidate_insufficient_rvol_history']+=1
            factor=price_factor(key,day,unit_audit)
            raw_previous=event.get('raw_prev_close',event['prev_close'])
            if not np.isclose(event.get('price_factor',factor),factor):raise ValueError('Plan/source share-unit factors differ')
            # RVOL is already computed on the common adjusted share basis.
            # Restore only the execution-day bars and corresponding prior close.
            restored={**event,'prev_close':current_basis_prev_close(raw_previous,factor),'price_factor':factor}
            records.append(dict(**restored,bars=restore_bars(raw_bars,factor),rvol=rvol,rvol_prior_sessions=len(history)))
            dispositions.append(dict(**event,status='loaded',rvol_prior_sessions=len(history)))
    dump(out/'load-audit.json',dict(candidate_count=len(plan['candidates']),loaded=len(records),counts=dict(counts),dispositions=dispositions))
    print(f'Loaded {len(records)} candidate sessions from PostgreSQL; audit {dict(counts)}',flush=True)
    return records


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['plan','acquire','load'])
    parser.add_argument('--output',type=Path,default=OUT);args=parser.parse_args()
    if args.mode=='plan':prepare(args.output)
    else:
        plan=json.loads((args.output/'jobs-plan.json').read_text())
        if args.mode=='acquire':acquire(plan,args.output)
        else:load_sessions(plan,args.output)
