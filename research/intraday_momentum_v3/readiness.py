"""Freeze definitions and count only genuine post-freeze open-market coverage."""
from datetime import datetime,timedelta
from collections import defaultdict
from pathlib import Path
import gzip,json,math
from zoneinfo import ZoneInfo
from .common import OUT,SOURCE,dump,now,sha
from .features import timestamp


def freeze():
    path=OUT/'protocol-frozen.json';docs={f.name:sha(f) for f in SOURCE.glob('*.md')};code={f.name:sha(f) for f in SOURCE.glob('*.py')}
    if path.exists():
        old=json.loads(path.read_text());assert old['documents']==docs and old['code']==code,'Use a new version after changing a frozen forward protocol';return old
    result=dict(version='V3.1-pre-forward-resume-guard',frozen_at=now().isoformat(),documents=docs,code=code,primary_hypotheses=['H3-A','H3-B','H3-C'],primary_horizon_seconds=900,
        diagnostic_horizons_seconds=[30,60,180,300,1800],scope_end='2026-12-31',scheduling_enabled=False,real_orders_allowed=False)
    dump(path,result);return result


def covered_grid(records,day,transport):
    zone=ZoneInfo('Asia/Kolkata');start=datetime.fromisoformat(day+'T09:15:00').replace(tzinfo=zone).timestamp();end=start+355*60
    step=1 if transport=='ws' else 5;limit=2 if transport=='ws' else 10;good=set()
    records=sorted(records,key=lambda r:r['available'])
    for i,r in enumerate(records):
        if not r['valid']:continue
        until=min(end,r['source']+limit,r['received']+limit,records[i+1]['available'] if i+1<len(records) else end)
        # Source/receipt are original; these are derived as-of intervals only.
        lo=max(start,r['available']);last=math.floor(until/step);first=math.ceil(lo/step)
        for t in range(first,last+1):
            if start<=t*step<end:good.add(t)
    return len(good)/int((end-start)/step)


def audit():
    protocol=json.loads((OUT/'protocol-frozen.json').read_text());frozen=timestamp(protocol['frozen_at']);groups=defaultdict(list);controls={};excluded=0;open_rows=0;fresh_by_transport=defaultdict(int)
    for directory in sorted((OUT/'runs').glob('*')) if (OUT/'runs').exists() else []:
        manifest=json.loads((directory/'manifest.json').read_text())
        if manifest.get('protocol_sha256')!=sha(OUT/'protocol-frozen.json'):continue
        path=directory/'quote-quality.jsonl.gz'
        if not path.exists():continue
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            for line in stream:
                r=json.loads(line);s=timestamp(r['source_at']);recv=timestamp(r['received_at']);avail=timestamp(r['available_at']);day=s.astimezone(ZoneInfo('Asia/Kolkata')).date().isoformat()
                if not r['market_active'] or s<frozen or recv<frozen or not '2026-01-01'<=day<='2026-12-31':excluded+=1;continue
                processed=timestamp(r.get('processed_at')) or avail;effective=max(avail,processed);limit=2 if r['transport']=='ws' else 10
                if r['valid_book'] and -1<=(effective-s).total_seconds()<=limit and 0<=(effective-recv).total_seconds()<=limit:
                    open_rows+=1;fresh_by_transport[r['transport']]+=1
                ident=(day,r['transport']);controls.setdefault(ident,set()).update(manifest.get('controls',[]))
                groups[(day,r['transport'],r['key'])].append(dict(source=s.timestamp(),received=recv.timestamp(),available=effective.timestamp(),valid=r['valid_book']))
    sessions=[]
    for (day,transport),ks in controls.items():
        coverage={key:covered_grid(groups.get((day,transport,key),[]),day,transport) for key in ks}
        passed=bool(coverage) and min(coverage.values())>=.95
        sessions.append(dict(session=day,transport=transport,fixed_control_count=len(ks),control_coverage=coverage,quality_pass=passed,
            minimum_control_coverage=min(coverage.values(),default=0)))
    ws=sum(x['quality_pass'] and x['transport']=='ws' for x in sessions);rest=sum(x['quality_pass'] and x['transport']=='rest' for x in sessions)
    result=dict(checked_at=now().isoformat(),fresh_open_observations=open_rows,excluded_closed_or_prefreeze_rows=excluded,sessions=sessions,
        milestone_A_streaming_open_received=fresh_by_transport['ws']>0,milestone_A_rest_open_received=fresh_by_transport['rest']>0,
        milestone_B_streaming_quality=ws>=5,milestone_B_rest_quality=rest>=5,quality_pass_sessions_ws=ws,quality_pass_sessions_rest=rest,
        milestone_C_sufficient_evidence=False,shadow_funded_ready=False,predictor_frozen=False,
        status='FORWARD_DATA_REQUIRED',explanation='C additionally needs60freshregularsessions and1000embargoedstockepisodes across>=50days with matched controls. No claim of statistical independence across stocks.')
    dump(OUT/'forward-readiness.json',result);print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','audit']);a=p.parse_args()
    if a.action=='freeze':print(json.dumps(freeze(),indent=2))
    else:audit()
