"""Freeze earlier daily regimes for backward replication, not a new forward holdout."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient


def main():
    out=ROOT/'artifacts'/'directional_research_phase2';(out/'raw').mkdir(parents=True,exist_ok=True)
    client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=30,max_retries=1)
    rows={};windows=[]
    for start,end in [('2000-01-01','2008-12-31'),('2009-01-01','2016-12-31')]:
        path=out/'raw'/f'nifty-daily-{start}.json'
        try:
            if path.exists():payload=json.loads(path.read_text())
            else:
                payload=client.get_historical_candles_v3('NSE_INDEX|Nifty 50','days',1,end,start)
                path.write_text(json.dumps(payload),encoding='utf-8')
            for r in payload.get('candles',[]):
                if start<=r[0][:10]<=end:rows[r[0]]=dict(zip(('ts','open','high','low','close','volume','oi'),r))
            windows.append({'from':start,'to':end,'bars':len(payload.get('candles',[])),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        except Exception as exc:windows.append({'from':start,'to':end,'error':type(exc).__name__,'status':getattr(exc,'status_code',None)})
    target=out/'expanded-nifty-1day.json';target.write_text(json.dumps(sorted(rows.values(),key=lambda r:r['ts'])),encoding='utf-8')
    manifest={'bars':len(rows),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'windows':windows}
    (out/'expanded-daily-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest))


if __name__=='__main__':main()
