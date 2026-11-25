"""Reconcile original prospective forecasts and audit native-clock input readiness."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests

from .common import *
from .acquire import ARCHIVES,AGENT,fetch
from .reference import NATIVE
from research.nifty_forecast_v16 import acquire as source
from research.nifty_forecast_v4.distributions import Distribution


def participant_probe(day):
    date=pd.Timestamp(day).strftime('%d%m%Y')
    by=[]
    for key in ('oi','vol'):
        url=f'https://nsearchives.nseindia.com/content/nsccl/fao_participant_{key}_{date}.csv'
        sent=now()
        rec=dict(family='participant_'+key,day=day,url=url,sent=sent)
        try:
            r=requests.get(url,headers=AGENT,timeout=(7,15))
            rec.update(status=r.status_code,received=now(),server_date=r.headers.get('Date'))
            lines=r.content.decode('utf-8-sig','replace').splitlines()
            title=lines[0][:170] if lines else ''
            dt=pd.Timestamp(day)
            title_date=any(a.casefold() in title.casefold() for a in (dt.strftime('%b %d, %Y'),dt.strftime('%d-%b-%Y'),dt.strftime('%d-%m-%Y')))
            if r.ok and len(lines)>6 and title_date:
                a=pd.read_csv(BytesIO(r.content),skiprows=1,skipinitialspace=True)
                types=set(a.iloc[:,0].astype(str).str.upper().str.strip())
                if {'FII','DII','PRO','CLIENT'}.issubset(types):
                    p=OUT/f'forward/input-staging/{day}-{key}.csv'
                    p.parent.mkdir(parents=True,exist_ok=True)
                    p.write_bytes(r.content)
                    rec.update(file=p.relative_to(OUT).as_posix(),sha256=sha(p),categories=sorted(types),verified=True)
            if 'verified' not in rec:
                rec['verified']=False
        except (requests.RequestException,ValueError,pd.errors.ParserError) as exc:
            rec.update(verified=False,error=type(exc).__name__)
        by.append(rec)
    return by


def same_session_rehearsal():
    z=csv('protected-return-cases.csv.gz')
    rows=[]
    for h in HORIZONS:
        d=z[z.horizon.eq(h)&z.cutoff.eq('native_0910')]
        at=d.day.max()
        assert set(d[d.day.eq(at)].model)==set(NATIVE[h])
        for r in d[d.day.eq(at)].itertuples(index=False):
            rows.append(dict(classification='historical implementation rehearsal',model=r.model,horizon=h,decision_day=at,
                         target_end=r.target_end,probability=r.p,mean=r.mean,median=r.median,law_index=r.law,
                         law_file='protected-return-laws.npz',law_sha256=sha(OUT/'protected-return-laws.npz')))
    write('forward-native-rehearsal.csv',pd.DataFrame(rows))


def settle(known,issue,version,now_):
    root=V19 if version=='V19' else V20
    path=issue['file'] if version=='V19' else issue['law']
    checksum=issue['sha256'] if version=='V19' else issue['law_sha256']
    assert sha(root/path)==checksum
    q=issue.copy()
    targets=q['target_sessions']
    q.update(version=version,status='pending certified target',source_artifact=path,
             confirmed_sessions=[k for k in targets if k in known])
    k=targets[-1]
    if k+'T18:00:00+05:30'<=now_ and q['confirmed_sessions']==targets:
        o=float(issue['reference_close']);cl=np.array([o,*[known[j]['ohlc']['close'] for j in targets]])
        q.update(status='matured on original target',official_close=float(cl[-1]),realized_return=float(cl[-1]/o-1),
                 close_based_rv=float(np.sqrt(np.mean(np.diff(np.log(cl))**2)*252)))
        if 'neutral' in issue.get('name','') or issue.get('model')=='weekly_symmetric':
            with np.load(root/path,allow_pickle=False) as a:
                atoms=a['arithmetic_returns'] if 'arithmetic_returns' in a else a['atoms']
                ww=a['weights']
                res=Distribution(atoms,ww).score(q['realized_return'])
                q['return_scores']={m:float(res[m]) for m in ('p','brier','log_loss','crps')}
    return q


def run():
    old=read('forward-ledger.json',V20)
    now_=now()
    assert FREEZE<now_[:10]<=LAST
    # The inherited cash and Upstox routine writes exclusively to this research version.
    source.OUT=OUT
    source.save=save
    source.forward()
    current=read('forward-ledger.json')
    save('forward-refetch-receipt.json',current)
    archive_roots={'V19':V19,'V20':V20,'V21':OUT}
    known={}
    for r in old['sessions']:
        assert sha(archive_roots[r['archive']]/r['file'])==r['sha256']
        known[r['day']]=r.copy()
    for r in current['sessions']:
        day=r['day']
        if r['status']=='verified':
            if day in known:
                assert known[day]['ohlc']==r['nse_ohlc']
            known[day]=dict(day=day,archive='V21',ohlc=r['nse_ohlc'],file=r['file'],sha256=r['sha256'])
    legacy=[]
    for a,b in zip(old['records'],current['records'],strict=True):
        keys=('issue_hash','issued','target_sessions','reference_close','key','version')
        assert all(a[k]==b[k] for k in keys)
        q=a.copy()
        if a['realized_return'] is None and b['realized_return'] is not None:
            q=b.copy()
        q['completed_target_dates']=[k for k in a['target_sessions'] if k in known]
        if q['realized_return'] is not None:
            assert abs(known[q['target_sessions'][-1]]['ohlc']['close']/q['reference_close']-1-q['realized_return'])<1.e-12
        legacy.append(q)
    dgi=sorted(known)
    ref=dgi[-1]
    staging=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        jobs=[]
        for day in dgi:
            name=f"BhavCopy_NSE_CM_0_0_0_{day.replace('-', '')}_F_0000.csv.zip"
            url=ARCHIVES+name
            jobs.append(('postfreeze_cash',day,[url,url.replace('nsearchives.','archives.')],f'forward/cash/{day}.zip','zip'))
        staging=list(pool.map(fetch,jobs))
    staging+=participant_probe(ref)
    save('forward-input-receipts.json',dict(checked_at=now_,reference_day=ref,captures=staging))
    prior19=[settle(known,r,'V19',now_) for r in read('forward/new-issues.json',V19)['records']]
    prior20=[settle(known,r,'V20',now_) for r in read('forward/new-issues.json',V20)['records']]
    target=prior20[0]['first_target']
    guarded={
       'GIFT opening':['08:55','Same-session eligible timed GIFT contract/continuous quote and cash reference. Rehearse the simple signed-gap coefficient at that cutoff.'],
       'V14 native weekly and monthly':['09:10','Build the original V14 prior cash and eligible option/risk state from newly completed data and run its exact anchored path/distribution generation. The frozen historical archive is a case lookup.'],
       'V18 corporate and V20 weekly omission / price reaction':['09:10','Requires the new V14 parent plus 08:55-eligible issuer filings, matured chronological errors, and verified eligible cash reactions. V20 training-only correction and its fallback must match archived behavior.'],
       'V19 positioning and V20 monthly smooth':['09:10','Requires the new V14 parent, authenticated report availability at the 08:55 snapshot and correct consecutive-session position history. A new isolated report is insufficient for moving-average and positioning features.'],
    }
    ready=[dict(family=k,clock=v[0],reference=ref,earliest_next_opportunity=f'{target}T{v[0]}:00+05:30',status='unissued; gated source snapshot required',requirements=v[1])
           for k,v in guarded.items()]
    write('forward-readiness.csv',pd.DataFrame(ready))
    same_session_rehearsal()
    save('forward-ledger.json',dict(checked_at=now_,sessions=[known[k] for k in dgi],original_issues=legacy,inherited_v19=prior19,
        inherited_v20=prior20,new_issues=[],timed_candidates=ready,predecessor_ledgers={
        'V19':sha(V19/'forward-ledger.json'),'V20':sha(V20/'forward-ledger.json')},
        policy='Completed observations after the November 17 freeze are admitted to this ledger only. Native and opening candidates require actual morning snapshots. V19 and V20 already supply the feasible evening benchmark/risk panel.'))
    print('Forward:',len(known),'certified post-freeze sessions,',len(prior19)+len(prior20),'preserved frozen references',flush=True)


if __name__=='__main__':
    run()
