"""Freeze overlapping read-only institutional history for weight research."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
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
    p=argparse.ArgumentParser()
    p.add_argument('--date',default='2026-11-17')
    p.add_argument('--out',type=Path,default=BASE/'institutional-v1')
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    target=date.fromisoformat(args.date)
    cutoff=datetime.now(ZoneInfo('Asia/Kolkata'))
    if target!=cutoff.date() or cutoff.hour>=9:
        raise ValueError('This freeze is for the current pre-market experiment')
    token=get_settings().upstox_analytics_token
    dates=[];day=date(2026,4,1)
    while day<target:
        dates.append(day.isoformat());day+=timedelta(days=35)
    jobs=[(provider,start) for provider in ['fii','dii'] for start in dates]
    def fetch(job):
        provider,start=job
        client=UpstoxAnalyticsClient(token,timeout=15,max_retries=0)
        try:
            kwargs={'interval':'1D','from_date':start}
            if provider=='fii':kwargs['data_types']=['NSE_EQ|CASH','NSE_FO|INDEX_FUTURES','NSE_FO|INDEX_OPTIONS']
            payload=getattr(client,f'get_{provider}_data')(**kwargs)
            result={'ok':True,'payload':payload}
        except Exception as exc:
            result={'ok':False,'error_type':type(exc).__name__,'error':str(exc)[:600]}
        finally:client.session.close()
        return f'{provider}-{start}.json',{'provider':provider,'from_date':start,
            'acquired_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),**result}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(fetch,j) for j in jobs]):
            name,value=future.result();write_json(args.out/name,value)
            sizes={k:len(v) for k,v in value.get('payload',{}).items()}
            print(name,value['ok'],sizes,flush=True)
    write_json(args.out/'manifest.json',{'target_date':args.date,'frozen_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),
        'files':{p.name:digest(p) for p in sorted(args.out.glob('*.json'))}})


if __name__=='__main__':main()
