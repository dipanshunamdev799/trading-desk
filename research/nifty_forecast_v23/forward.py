"""Stage immutable legacy issues and acquire the minimal genuine morning research inputs."""
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import sys
import time

import requests

from .common import *
from .laws import Law
from research.nifty_forecast_v16 import acquire as live
from research.nifty_forecast_v21 import forward as settlement
from research.nifty_forecast_v22 import sources as previous_sources
from research.nifty_forecast_v15.sources import token, API

CALENDAR='https://archives.nseindia.com/content/circulars/CMTR71775.pdf'
HOLS={'2026-11-24','2026-12-25'}
OPEN='08:55'
NATIVE='09:10'
STUDY_DAY='2026-11-26'
END='16:30'


def targets(day):
    return [d.date().isoformat() for d in pd.bdate_range(day,LAST) if d.date().isoformat() not in HOLS]


def guard_day():
    cur=pd.Timestamp(now()).tz_convert(IST)
    assert FREEZE<cur.date().isoformat()<=LAST
    return cur


def ledger(refresh=False):
    old=read('forward-ledger.json',V22)
    original=[r.copy() for r in old['original_issues']]
    at=guard_day()
    known={r['day']:r.copy() for r in old['sessions']}
    receipts=[]
    if refresh:
        live.OUT=OUT
        live.save=lambda name,obj:save('forward/authoritative-reconciliation.json' if name=='forward-ledger.json' else name,obj)
        live.forward()
        current=read('forward/authoritative-reconciliation.json')
        receipts=current['sessions']
        for a,b in zip(original,current['records'],strict=True):
            assert all(a[k]==b[k] for k in ('version','horizon','key','issue_hash','issued','target_sessions','reference_close'))
            if a.get('realized_return') is None and b.get('realized_return') is not None:
                a.update({k:b[k] for k in ('realized_return','official_close','scores','maturity')})
        for r in receipts:
            d=r['day']
            if r['status']=='verified':
                if d in known:
                    assert known[d]['ohlc']==r['nse_ohlc']
                known[d]=dict(day=d,ohlc=r['nse_ohlc'],archive='V23',file=r['file'],sha256=r['sha256'])
    for r in original:
        r['completed_target_dates']=[d for d in r['target_sessions'] if d in known]
    for date,r in known.items():
        base=OUT if r['archive']=='V23' else root_for(int(r['archive'][1:]))
        assert sha(base/r['file'])==r['sha256'],date
    inherited={}
    for ver in (19,20):
        vals=read('forward/new-issues.json',root_for(ver))['records']
        rex=[settlement.settle(known,x,f'V{ver}',at.isoformat()) for x in vals]
        for a,b in zip(rex,old[f'inherited_v{ver}'],strict=True):
            for key in ('source_artifact','reference_close','target_sessions','sha256','law_sha256'):
                assert a.get(key)==b.get(key)
        inherited[f'inherited_v{ver}']=rex
    issued=[]
    if (OUT/'forward/issued.json').is_file():
        issued=read('forward/issued.json')['issues']
    save('forward-ledger.json',dict(checked_at=now(),study_day=STUDY_DAY,frozen_research_end=FREEZE,calendar=CALENDAR,
         sessions=[known[k] for k in sorted(known)],original_issues=original,new_issues=issued,**inherited,
         predecessor_ledger_sha256=sha(V22/'forward-ledger.json'),original_cash_reconciliation=receipts))
    return known


def broker(name,url,received_deadline=None):
    receipt=dict(name=name,url=url,sent=now())
    try:
        credential=token()
        if not credential:
            return [],receipt|dict(status='credential unavailable')
        r=requests.get(url,headers=previous_sources.UA|{'Authorization':'Bearer '+credential},timeout=(5,9))
        ended=pd.Timestamp(now())
        receipt.update(received=ended.isoformat(),status=r.status_code,server_date=r.headers.get('Date'))
        if not r.ok:
            return [],receipt
        bars=r.json()['data']['candles']
        clip=[x for x in bars if FREEZE<x[0][:10]<=STUDY_DAY]
        name=f'forward/raw/{name}-{ended.strftime("%H%M%S-%f")}.json'
        save(name,dict(receipt=receipt,candles=clip))
        receipt.update(file=name,sha256=sha(OUT/name),n=len(clip))
        if received_deadline is not None and ended>received_deadline:
            return [],receipt|dict(rejected='response arrived after the information cutoff')
        return clip,receipt
    except (requests.RequestException,KeyError,ValueError,TypeError) as e:
        return [],receipt|dict(error=type(e).__name__)


def completed_foreign(at):
    previous_sources.OUT=OUT
    catalog=csv('market-universe-audit.csv',V22)
    codes=set(catalog.loc[catalog.primary_eligible,'code'])|{'vix','ndx','us_finance'}
    items=[s for s in previous_sources.SERIES if s.code in codes and s.code!='india' and s.exchange is not None]
    def collect(s):
        sched=previous_sources.schedule(s,'2026-11-18',at.date().isoformat())
        sched=sched[sched.available.le(at)]
        if sched.empty:
            return None,dict(code=s.code,status='no published session in period')
        last=sched.day.max()
        a,rec=previous_sources.yahoo(s,'2026-11-18',last,'forward/vendor')
        if a.empty:
            return None,rec
        a['stamp']=pd.to_datetime(a.source_timestamp,utc=True,format='mixed')
        a=a[a.stamp.le(at)].sort_values('stamp').drop_duplicates('day',keep='last')
        ok=sched.merge(a,on='day',validate='1:1').dropna(subset=['close'])
        return ok.assign(code=s.code,role=s.role),rec|dict(eligible=len(ok),last_eligible=last)
    with ThreadPoolExecutor(max_workers=8) as pool:
        z=list(pool.map(collect,items))
    f=pd.concat([a for a,_ in z if a is not None],ignore_index=True)
    assert len(f) and f.day.gt(FREEZE).all() and f.available.le(at).all()
    write('forward/completed-foreign-marks.csv.gz',f)
    save('forward/foreign-receipt.json',dict(captured_at=at.isoformat(),rows=len(f),markets=f.code.nunique(),sources=[r for _,r in z]))
    return f


def configure():
    at=guard_day()
    r=read('forward/staged-model-configurations.json',V22)['rows']
    config=[]
    for s in r:
        cand=s['short']
        cfg=dict(name=cand,horizon=s['horizon'],clock=s['clock'],inherited_sha256=s['configuration_sha256'],
                 conditions=s['input_requirements'])
        if cand in ('weekly_symmetric','monthly_neutral_reference'):
            cfg.update(status='existing genuine immutable issue guards the same target')
        elif s['clock']=='09:10':
            cfg.update(status='requires native V14 reconstruction and exact morning feature state; evaluate at cutoff')
        else:
            cfg.update(status='observe eligibility, prefer genuine prior frozen risk references')
        config.append(cfg)
    config.extend([
        dict(name='V22 domestic correction',horizon=5,clock=NATIVE,conditions=['New exact V14 and V21 laws','eligible corporate and market breadth inputs','frozen older errors'],status='requires native parent'),
        dict(name='V22 foreign-tail mixture',horizon=21,clock=NATIVE,conditions=['New exact V21 positioning parent','fully matured analogue donors'],status='requires native parent'),
        dict(name='V22_architecture_india_monthly_path',horizon=21,clock=OPEN,conditions=['guarded domestic cash','frozen V19 GJR risk anchor','earlier observed donor paths'],status='capture scheduled'),
        dict(name='V22_architecture_mixed_monthly_path',horizon=21,clock=OPEN,conditions=['guarded cash, foreign state, frozen GJR','earlier observed donor paths'],status='capture scheduled'),
    ])
    payload=dict(frozen_at=at.isoformat(),study_day=STUDY_DAY,calendar=CALENDAR,origin_target_sessions=targets(STUDY_DAY)[:21],
                 preauction_processing_seconds=75,native_processing_seconds=75,configurations=config,
                 implementation=Path(__file__).relative_to(ROOT).as_posix(),implementation_sha256=sha(Path(__file__)))
    path=OUT/'forward/staged-configurations.json'
    if not path.exists():
        save('forward/staged-configurations.json',payload)
    return read('forward/staged-configurations.json')


def stage():
    at=guard_day()
    configure()
    known=ledger(refresh=True)
    latest=max(q for q in known if q<STUDY_DAY)
    gift_key=read('source-attempts.json',root_for(16))['gift_key']
    url=API+quote(gift_key,safe='')+f'/minutes/5/{latest}/{latest}'
    bars,receipt=broker('gift-previous-cash',url)
    fx=completed_foreign(at)
    save('forward/pre-cutoff-staging.json',dict(staged_at=now(),latest_cash=latest,gift_key=gift_key,previous_gift_receipt=receipt,
         prior_gift_rows=len(bars),available_foreign_rows=len(fx),has_authentication=bool(token()),authenticated_order_endpoints_used=0,
         next_checkpoints=[stamp(STUDY_DAY,OPEN).isoformat(),stamp(STUDY_DAY,NATIVE).isoformat()]))
    print('Staged',len(fx),'guarded foreign marks and',len(bars),'prior GIFT bars. Reference cash',latest,flush=True)


if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else 'stage'
    if cmd=='stage':
        stage()
    elif cmd=='settle':
        ledger(refresh=True)
    elif cmd in ('watch','dry-run','native-check'):
        from .forward_issue import run
        run(cmd)
    else:
        raise SystemExit('Expected stage, settle, watch, dry-run or native-check')
