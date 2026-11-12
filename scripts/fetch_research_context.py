"""Bounded, read-only Phase 2 data acquisition; never overwrites Phase 1."""
import calendar
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient

OUT=ROOT/'artifacts'/'directional_research_phase2'


def fetch(label,key,years):
    cache=OUT/'raw'/label;cache.mkdir(parents=True,exist_ok=True)
    client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=25,max_retries=1)
    rows={};audit=[]
    for year in years:
        for month in range(1,13 if year<2026 else 12):
            start=f'{year}-{month:02d}-01';end=f'{year}-{month:02d}-{8 if (year,month)==(2026,11) else calendar.monthrange(year,month)[1]:02d}'
            path=cache/f'{start}.json'
            try:
                if path.exists():payload=json.loads(path.read_text())
                else:
                    payload=client.get_historical_candles_v3(key,'minutes',5,end,start)
                    path.write_text(json.dumps(payload),encoding='utf-8');time.sleep(.4)
                for row in payload.get('candles',[]):
                    if start<=row[0][:10]<=end:rows[row[0]]=dict(zip(('ts','open','high','low','close','volume','oi'),row))
                audit.append({'from':start,'to':end,'bars':len(payload.get('candles',[])),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
                print(label,start,len(payload.get('candles',[])),flush=True)
            except Exception as exc:
                audit.append({'from':start,'to':end,'error':type(exc).__name__,'status':getattr(exc,'status_code',None)})
                print(label,start,'ERROR',type(exc).__name__,getattr(exc,'status_code',None),flush=True)
                if getattr(exc,'status_code',None) in (401,403):break
    target=OUT/f'{label}-5minute.json'
    target.write_text(json.dumps(sorted(rows.values(),key=lambda r:r['ts'])),encoding='utf-8')
    manifest={'instrument':key,'cutoff':'2026-11-08','bars':len(rows),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'windows':audit}
    (OUT/f'{label}-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(label,'TOTAL',len(rows),flush=True)
    return manifest


def main():
    jobs=[('expanded-nifty','NSE_INDEX|Nifty 50',[2022,2023,2024]),
          ('context-vix','NSE_INDEX|India VIX',[2025,2026]),
          ('context-niftybees','NSE_EQ|INF204KB14I2',[2025,2026])]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda args:fetch(*args),jobs))
    print('Completed',[(r['instrument'],r['bars']) for r in results])


if __name__=='__main__':main()
