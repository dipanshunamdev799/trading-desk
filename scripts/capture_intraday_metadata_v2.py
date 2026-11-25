"""Current-session eligibility evidence; never backdate into historical tests.

Separate from frozen strategy source. Public Upstox MIS/suspensions plus raw
market status/timings into existing market_responses; derived coverage local.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from datetime import datetime
import gzip,hashlib,json
import requests
from research.intraday_momentum import data as base
from research.intraday_momentum_v2.data import OUT


def main():
    at=datetime.now().astimezone();plan=json.loads((OUT/'jobs-plan.json').read_text());keys={s['instrument_key'] for s in plan['cohort']['stocks']}
    items={};audit=[]
    for kind,name in [('mis','NSE_MIS'),('suspended','suspended-instrument')]:
        url='https://assets.upstox.com/market-quote/instruments/exchange/'+name+'.json.gz'
        try:
            response=requests.get(url,timeout=25);response.raise_for_status();raw=response.content;payload=json.loads(gzip.decompress(raw))
            path=OUT/'raw/metadata'/at.strftime('%Y%m%d-%H%M%S')/(name+'.json.gz');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
            items[kind]=(payload,{'source_url':url});entries=payload if isinstance(payload,list) else payload.get('data',[])
            present={r.get('instrument_key') for r in entries if isinstance(r,dict)}
            audit.append(dict(kind=kind,source_url=url,raw_sha256=base.sha(path),rows=len(entries),cohort_matches=sorted(keys&present),fields=sorted({k for row in entries if isinstance(row,dict) for k in row})))
        except Exception as exc:audit.append(dict(kind=kind,error_type=type(exc).__name__))
    for kind,method,args in [('status','get_market_status',('NSE',)),('timings','get_market_timings',(at.date().isoformat(),))]:
        try:items[kind]=(getattr(base._client(),method)(*args),{'exchange':'NSE','date':at.date().isoformat()})
        except Exception as exc:audit.append(dict(kind=kind,error_type=type(exc).__name__))
    for kind,(payload,params) in items.items():
        encoded=json.dumps(params,sort_keys=True);ident=hashlib.sha256(('intraday_v2.metadata.'+kind+encoded).encode()).hexdigest()
        with base.connection(write=True) as c:
            c.execute('INSERT INTO market_responses(recorded_at,request_key,method,parameters,payload) VALUES(%s,%s,%s,%s::jsonb,%s::jsonb) ON CONFLICT DO NOTHING',
                (at,ident,'intraday_v2.metadata.'+kind,encoded,json.dumps(payload,allow_nan=False)))
    result=dict(observed_at=at.isoformat(),results=audit,archived_primary_kinds=sorted(items),
        limitation='Current BOD/public broker lists, not backdated MIS/margin/short eligibility or execution guarantees',real_orders_submitted=0)
    base.dump(OUT/'current-metadata-audit.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
