"""Point-in-time observation cohort, fixed controls and causal watchlist changes."""
from collections import defaultdict
from collections import deque
from datetime import timedelta
import hashlib,json
import numpy as np
import pandas as pd
from .common import OUT,base,dump,now,sha


def stable(key,day):return hashlib.sha256((day+'|'+key).encode()).hexdigest()


def build():
    at=now();today=at.astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date();day=today.isoformat()
    path=OUT/'universes'/(day+'.json')
    if path.exists():
        result=json.loads(path.read_text());dump(OUT/'universe-current.json',result);return result
    meta=json.loads((OUT/'metadata-reconciliation.json').read_text());bykey={r['key']:r for r in meta}
    old=json.loads((base.ROOT/'artifacts/intraday_momentum_v2/jobs-plan.json').read_text());corekeys={s['instrument_key'] for s in old['cohort']['stocks']}
    original=json.loads(base.UNIVERSE.read_text());known=[s['instrument_key'] for s in original['stocks'] if s['instrument_key'] in bykey]
    with base.connection() as c:
        c.execute("SET LOCAL statement_timeout='45s'")
        c.execute("SELECT instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date,high,low,close,volume FROM public.candles WHERE instrument_key=ANY(%s) AND interval='1day' AND source='upstox' AND ts>=%s AND ts<%s ORDER BY instrument_key,ts",
            (known,str(today-timedelta(days=180))+' 00:00+05:30',day+' 00:00+05:30'))
        frame=pd.DataFrame(c.fetchall(),columns=['key','day','high','low','close','volume']).drop_duplicates(['key','day'],keep='last')
    history={}
    for key,g in frame.groupby('key'):
        g=g.sort_values('day').tail(63);adv=float((g.close*g.volume).median());vol=float((g.high-g.low).div(g.close).median())
        history[key]=dict(adv=adv,lag_range_fraction=vol,last_close=float(g.iloc[-1].close),history_sessions=len(g),history_last_day=str(g.iloc[-1].day),
                          stale_history=(today-g.iloc[-1].day).days>7)
    core=sorted(corekeys&set(bykey),key=lambda k:stable(k,day))
    broader=sorted([k for k,h in history.items() if k not in corekeys and h['history_sessions']>=20 and h['adv']>=5e7 and h['last_close']>=50],key=lambda k:(-history[k]['lag_range_fraction'],stable(k,day)))[:300]
    extras=sorted([k for k,r in bykey.items() if k not in corekeys and k not in broader and r['in_mis'] and k not in history],key=lambda k:stable(k,day))[:80]
    selected=list(dict.fromkeys(core+broader+extras))[:480]
    # Matched controls: deterministic within price/ADV bins, not future winners.
    bins=defaultdict(list)
    for key in selected:
        h=history.get(key)
        if h and not h['stale_history']:
            bins[(h['adv']>=1e9,h['last_close']>=500)].append(key)
    controls=[]
    for bucket,ks in sorted(bins.items()):controls.extend(sorted(ks,key=lambda k:stable(k,day))[:5])
    controls=controls[:20]
    rows=[]
    for key in selected:
        tags=['existing_liquid' if key in corekeys else 'broader_known_liquid' if key in broader else 'new_listing_observation_only']
        if key in controls:tags.append('matched_control')
        rows.append({**bykey[key],**history.get(key,{'adv':None,'history_sessions':0,'stale_history':True}),
                     'groups':tags,'continuous_full':key in controls or key in core[:10]})
    result=dict(prepared_at=at.isoformat(),session=day,metadata_sha256=sha(OUT/'metadata-reconciliation.json'),stocks=rows,
        scanner_max=480,full_max=40,controls=controls,regular_source='Upstox market status/timings',
        policy='Frozen current BOD identities; pre-session daily PG history only. Unknown/stale history permits observation, not economic eligibility. Reuse same-day plan on restart.',
        account_active_verified=False,short_execution_verified=False,real_orders_submitted=0)
    dump(path,result);dump(OUT/'universe-current.json',result)
    print(json.dumps({'stocks':len(rows),'core':len(core),'broader':len(broader),'extras':len(extras),'controls':len(controls)},indent=2));return result


class Scanner:
    def __init__(self,plan):
        self.plan=plan;self.metadata={r['key']:r for r in plan['stocks']};self.latest={};self.previous={};self.watch=set();self.rotation=0;self.history={}
        self.fixed={r['key'] for r in plan['stocks'] if r['continuous_full']}
        self.fixed=set(sorted(self.fixed)[:30])
    def update(self,q):
        if q.key not in self.metadata:return
        old=self.latest.get(q.key)
        if old and (q.available_at<old.available_at or q.source_at<old.source_at):return
        self.previous[q.key]=old;self.latest[q.key]=q
        self.history.setdefault(q.key,deque(maxlen=100)).append(q)
    def select(self,at):
        scored=[]
        for key,history in self.history.items():
            available=[q for q in history if q.available_at<=at]
            if not available:continue
            q=available[-1]
            if q.available_at>at or not q.cp or not q.last or not q.fresh(at):continue
            move=abs(q.last/q.cp-1);old=available[-2] if len(available)>1 else None;acc=abs(q.last/old.last-1) if old and old.last else 0
            turnover=q.last*q.volume if q.volume is not None else 0
            score=move+2*acc+min(turnover/1e10,.02)
            scored.append((score,key,dict(move=move,latest_update_return=acc,observed_turnover=turnover)))
        slots=max(0,self.plan['full_max']-len(self.fixed));ranked=sorted(scored,key=lambda x:(-x[0],x[1]))
        dynamic=[(k,s,f) for s,k,f in ranked if k not in self.fixed][:slots]
        chosen=self.fixed|{x[0] for x in dynamic};before=self.watch;self.watch=chosen;self.rotation+=1
        return dict(at=at.isoformat(),rotation=self.rotation,added=sorted(chosen-before),removed=sorted(before-chosen),
            full_keys=sorted(chosen),fixed_controls=sorted(self.fixed),dynamic=[dict(key=k,score=s,**f) for k,s,f in dynamic],
            reason='Fixed matched controls/core retained; top causal observed move/turnover/last-update acceleration within full subscription budget')

if __name__=='__main__':build()
