"""Score matured weekly/monthly calls separately from immutable forecasts."""
from __future__ import annotations
import argparse
from datetime import datetime,timedelta
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from app.config import get_settings
from upstox_analytics import UpstoxAnalyticsClient
from .engine import BASE,digest,write_json


def resolve(call,candles):
    by_day={r[0][:10]:r for r in candles}
    days=sorted(by_day)
    if call['reference_date'] not in by_day:
        return {name:{'status':'pending_reference_publication'} for name in call['forecasts']}
    base=days.index(call['reference_date']);reference=float(by_day[days[base]][4]);result={}
    for name,f in call['forecasts'].items():
        index=base+f['horizon_sessions']
        if index>=len(days):
            result[name]={'status':'pending','available_sessions':len(days)-base-1};continue
        endpoint=days[index]
        if endpoint!=f['expected_endpoint_date']:
            result[name]={'status':'calendar_or_missing_data_review_required',
                'candidate_endpoint':endpoint,'frozen_expected_endpoint':f['expected_endpoint_date']};continue
        close=float(by_day[endpoint][4]);ret=close/reference-1;p=f['up_probability']['calibrated_adaptive']
        quantiles=f['closing_level_quantiles']
        result[name]={'status':'resolved','horizon_sessions':f['horizon_sessions'],
            'official_reference_close':reference,'reference_revision_points':reference-call['reference_close'],
            'official_endpoint_date':endpoint,'official_endpoint_close':close,'return':ret,
            'up':ret>0,'up_probability':p,'direction_correct':bool((p>=.5)==(ret>0)),
            'brier':float((p-int(ret>0))**2),
            'central50_contains_endpoint':quantiles['0.25']<=close<=quantiles['0.75'],
            'central80_contains_endpoint':quantiles['0.1']<=close<=quantiles['0.9']}
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,default=BASE/'horizons-v2')
    args=parser.parse_args();path=args.run/'forecast.json';frozen=digest(path)
    call=json.loads(path.read_text());now=datetime.now(ZoneInfo('Asia/Kolkata'))
    eligible=[name for name,f in call['forecasts'].items() if now.date().isoformat()>f['expected_endpoint_date']
        or (now.date().isoformat()==f['expected_endpoint_date'] and (now.hour,now.minute)>=(16,10))]
    if not eligible:
        print(json.dumps({'status':'pending','endpoints':{k:v['expected_endpoint_date'] for k,v in call['forecasts'].items()}}));return
    end=now.date() if (now.hour,now.minute)>=(16,10) else now.date()-timedelta(days=1)
    client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=15,max_retries=0)
    try:payload=client.get_historical_candles_v3('NSE_INDEX|Nifty 50','days',1,end.isoformat(),call['reference_date'])
    finally:client.session.close()
    result=resolve(call,payload.get('candles',[]))
    if digest(path)!=frozen:raise AssertionError('Original forecast changed')
    output=args.run/f"outcome-{now.strftime('%Y%m%dT%H%M%S%f')}.json"
    write_json(output,{'scored_at':now.isoformat(),'forecast_sha256':frozen,'results':result,
        'source':'Upstox published daily candles','raw_response':payload})
    print(json.dumps({'saved':str(output),'results':result},indent=2))


if __name__=='__main__':main()
