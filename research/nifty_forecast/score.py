"""Resolve the frozen call from published daily candles, in a separate file."""
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


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',type=Path,default=BASE/'run-v3')
    args=parser.parse_args()
    path=args.run/'forecast.json'
    original=digest(path)
    call=json.loads(path.read_text(encoding='utf-8'))
    target=call['target_date'];now=datetime.now(ZoneInfo('Asia/Kolkata'))
    if now.date().isoformat()<target or (now.date().isoformat()==target and (now.hour,now.minute)<(16,10)):
        raise SystemExit('Outcome pending: wait for the target session to close and its daily candle to be published.')
    start=(datetime.fromisoformat(target)-timedelta(days=14)).date().isoformat()
    client=UpstoxAnalyticsClient(get_settings().upstox_analytics_token,timeout=15,max_retries=0)
    try:
        payload=client.get_historical_candles_v3('NSE_INDEX|Nifty 50','days',1,target,start)
    finally:
        client.session.close()
    candles=sorted(payload.get('candles',[]),key=lambda r:r[0])
    matches=[(i,r) for i,r in enumerate(candles) if r[0][:10]==target]
    if not matches:
        raise SystemExit('Outcome pending: Upstox has not published the target daily candle; the call is unchanged.')
    i,bar=matches[-1]
    if i==0:
        raise ValueError('Previous official daily close unavailable')
    previous=float(candles[i-1][4]);opening=float(bar[1]);closing=float(bar[4])
    result={'forecast_sha256':original,'scored_at':now.isoformat(),'target_date':target,
        'source':'Upstox published daily candles','raw_daily_response':payload,
        'official_previous_close':previous,'official_open':opening,'official_close':closing,
        'frozen_reference_close':call['levels']['reference_close'],
        'reference_revision_points':previous-call['levels']['reference_close'],
        'scores':{}}
    for name,up in [('close_return',closing>previous),('intraday_return',closing>opening)]:
        p=call['forecasts'][name]['up_probability']['ensemble']
        result['scores'][name]={'up':bool(up),'raw_up_probability':p,
            'direction_correct':bool((p>=.5)==up),'brier':float((p-int(up))**2)}
    intervals=call['forecasts']['close_return']['closing_level_quantiles']
    result['central50_contains_close']=intervals['0.25']<=closing<=intervals['0.75']
    result['central80_contains_close']=intervals['0.1']<=closing<=intervals['0.9']
    if digest(path)!=original:
        raise AssertionError('The frozen forecast changed')
    output=args.run/f"outcome-{now.strftime('%Y%m%dT%H%M%S%f')}.json"
    write_json(output,result)
    print(json.dumps({'saved':str(output),'scores':result['scores']},indent=2))


if __name__=='__main__':
    main()
