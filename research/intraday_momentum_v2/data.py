"""Independent all-session cohort acquisition; only raw Upstox candles enter PG."""
from datetime import datetime
import json
from pathlib import Path
import shutil
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
import time

import numpy as np
import pandas as pd

from research.intraday_momentum import data as base
from research.intraday_momentum.units import load_audit,price_factor

OUT=base.ROOT/'artifacts/intraday_momentum_v2'
START='2025-01-01';END='2026-11-13';N=100


def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'jobs-plan.json').exists():raise RuntimeError('Plan already frozen; resume acquisition instead')
    cohort=json.loads(base.UNIVERSE.read_text());specs=cohort['stocks']
    calendar,p=base._daily(specs)
    prior=(p['close']*p['volume']).rolling(63,min_periods=50).median().shift(1)
    previous=p['close'].shift(1)
    freeze_day=max(d for d in calendar if d<START)
    units=load_audit(base.OUT)
    # Rank pre-2025 liquidity only, not any 2025/26 returns, outcomes or coverage.
    ranking=[]
    for s in specs:
        key=s['instrument_key'];adv=float(prior.loc[freeze_day,key])
        close=float(p['close'].loc[freeze_day,key])*price_factor(key,freeze_day,units)
        if np.isfinite(adv) and adv>=5e7 and close>=50:
            ranking.append({**s,'freeze_adv':adv,'freeze_price':close})
    ranking.sort(key=lambda s:(-s['freeze_adv'],s['instrument_key']));selected=ranking[:N]
    assert len(selected)==N
    old_plan=json.loads((base.OUT/'jobs-plan.json').read_text())
    excluded={(r['key'],r['day']) for r in old_plan['action_metadata']['excluded_exdates']}
    candidates=[]
    for s in selected:
        key=s['instrument_key']
        for day in calendar:
            if not START<=day<=END:continue
            factor=price_factor(key,day,units);prev=float(previous.loc[day,key]);adv=float(prior.loc[day,key])
            if not np.isfinite(prev+adv) or prev*factor<50 or adv<5e7 or (key,day) in excluded:continue
            candidates.append(dict(key=key,symbol=s['symbol'],sector=s['sector'],day=day,
                raw_prev_close=prev,prev_close=prev*factor,price_factor=factor,adv=adv))
    months=pd.period_range('2024-12','2026-11',freq='M').astype(str)
    jobs=[]
    for s in selected+[{'instrument_key':base.NIFTY,'symbol':'NIFTY50'}]:
        for month in months:
            key=s['instrument_key']
            jobs.append(dict(id=key+'|'+month,key=key,symbol=s['symbol'],month=month,
                first=month+'-01',last=min(base._month_end(month),END)))
    audit_dir=OUT/'unit-audit';audit_dir.mkdir(exist_ok=True)
    for name in ('unit-adjustment-audit.json','nse-actions-2026-11-10-13.json'):
        shutil.copy2(base.OUT/'unit-audit'/name,audit_dir/name)
    plan=dict(version='intraday-momentum-v2-independent-cohort-v1',start=START,end=END,
        warmup='2024-07-01',calendar=calendar,cohort={**cohort,'stocks':selected},
        universe_sha256=base.sha(base.UNIVERSE),unit_adjustment_sha256=base.sha(audit_dir/'unit-adjustment-audit.json'),
        selection=dict(frozen_on=freeze_day,method='Top100 lagged63-session median traded value, >=50 observations, price>=50, ADV>=5crore; only pre2025 information',
            evaluated_dates='2025-01-01..2026-11-13',all_months_independent_of_future_extremes=True),
        candidates=sorted(candidates,key=lambda r:(r['day'],r['key'])),jobs=sorted(jobs,key=lambda j:j['id']),
        action_metadata=old_plan['action_metadata'],frozen_at=datetime.now().astimezone().isoformat(),
        original_study_sha256=base.sha(base.OUT/'research-manifest.json'),ranking=ranking)
    base.dump(OUT/'jobs-plan.json',plan)
    old=json.loads((base.OUT/'acquisition-manifest.json').read_text());known={j['id']:j for j in old['jobs']}
    retained=[]
    for j in jobs:
        prev=known.get(j['id'])
        if prev and prev['status']=='ok' and all(prev[k]==j[k] for k in ('key','first','last')):
            if base.sha(prev['path'])!=prev['sha256']:raise RuntimeError('Reused source hash mismatch')
            retained.append(prev)
    base.dump(OUT/'acquisition-manifest.json',dict(version=plan['version'],plan_sha256=base.sha(OUT/'jobs-plan.json'),
        jobs=retained,lineage=[dict(reused_from=str(base.OUT/'acquisition-manifest.json'),
            source_sha256=base.sha(base.OUT/'acquisition-manifest.json'),identical_source_jobs=len(retained))]))
    print(f'Independent plan: {N} stocks + NIFTY, {len(candidates)} eligible stock-days, {len(jobs)} full-month jobs; {len(retained)} exact existing sources retained; {len(jobs)-len(retained)} missing.',flush=True)
    return plan


def acquire(plan):
    """Durable incremental manifests; recover completed jobs after interruption.

    V1's frozen acquire helper shadows its manifest variable with a loop job;
    leave that historical source unchanged and fix the integration here.
    """
    manifest_path=OUT/'acquisition-manifest.json'
    saved=json.loads(manifest_path.read_text())
    if saved['plan_sha256']!=base.sha(OUT/'jobs-plan.json'):raise RuntimeError('Plan changed')
    prior={j['id']:j for j in saved['jobs']}
    logpath=OUT/'acquisition-jobs.jsonl'
    if logpath.exists():
        for line in logpath.read_text().splitlines():
            if line.strip():
                j=json.loads(line);prior[j['id']]=j
    results={};todo=[]
    for j in plan['jobs']:
        old=prior.get(j['id'])
        if old and old.get('status')=='ok' and Path(old['path']).exists() and base.sha(old['path'])==old['sha256']:
            results[j['id']]=old
        else:todo.append(j)
    started=time.monotonic()
    def persist():
        manifest={**saved,'jobs':sorted(results.values(),key=lambda j:j['id']),
            'manifest_status':'complete' if len(results)==len(plan['jobs']) and all(j['status']=='ok' for j in results.values()) else 'incomplete'}
        base.dump(manifest_path,manifest)
        progress=dict(jobs_done=len(results),jobs_total=len(plan['jobs']),statuses=dict(Counter(j['status'] for j in results.values())),
                      source_rows=sum(j.get('source_rows',0) for j in results.values()),elapsed_seconds=round(time.monotonic()-started,1))
        base.dump(OUT/'acquisition-progress.json',progress);print(progress,flush=True)
    print(f'Recovered {len(results)} verified source jobs; retry/fetch {len(todo)}.',flush=True)
    persist()
    with logpath.open('a',encoding='utf-8') as log,ThreadPoolExecutor(max_workers=4) as pool:
        for fut in as_completed([pool.submit(base._one,j,OUT) for j in todo]):
            j=fut.result();results[j['id']]=j;log.write(json.dumps(j,allow_nan=False)+'\n');log.flush()
            if len(results)%25==0 or len(results)==len(plan['jobs']):persist()
    persist()
    return results


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['plan','acquire','load']);args=p.parse_args()
    if args.mode=='plan':prepare()
    else:
        plan=json.loads((OUT/'jobs-plan.json').read_text())
        if args.mode=='acquire':acquire(plan)
        else:base.load_sessions(plan,OUT)
