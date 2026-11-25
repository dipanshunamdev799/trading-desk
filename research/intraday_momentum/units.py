"""Restore contemporaneous share units locally; never alter stored source bars.

Upstox back-adjusts historical prices down and volumes up after share-count
actions. NSE bhavcopies independently verify that reciprocal convention. Later
action metadata here decodes the vendor's historical encoding; it is not a
future-dependent trading signal. Percentage returns and price*volume are invariant.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
import zipfile

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/intraday_momentum'
ACTIONS=ROOT/'artifacts/stock_swing_research/nse-actions-all.json'
UNIVERSE=ROOT/'artifacts/swing_discovery/universe.json'
START='2024-07-01';END='2026-11-13'


class UnitBasisError(ValueError):pass


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def combined_events(records,specs,start=START,end=END):
    by_symbol={s['symbol']:s for s in specs}
    for s in specs:
        if s.get('current_symbol'):by_symbol.setdefault(s['current_symbol'],s)
    grouped=defaultdict(lambda:dict(factor=1.,subjects=[]));seen=set();unresolved=[]
    for row in records:
        spec=by_symbol.get(row.get('symbol'));subject=row.get('subject','')
        if spec is None or row.get('series')!='EQ':continue
        if not any(x in subject.lower() for x in ('bonus','split')):continue
        try:day=datetime.strptime(row['exDate'],'%d-%b-%Y').date().isoformat()
        except (ValueError,KeyError):continue
        if not start<=day<=end:continue
        identity=(spec['instrument_key'],day,subject)
        if identity in seen:continue
        seen.add(identity);factor=None
        if any(term in subject.lower() for term in ('ncrps','preference','debenture','warrant')):
            unresolved.append(dict(key=spec['instrument_key'],symbol=spec['symbol'],day=day,subject=subject,
                                   reason='Non-equity security distribution; not an equity-share multiplication'))
            continue
        if 'bonus' in subject.lower():
            match=re.search(r'(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)',subject)
            if match and float(match[2])>0:factor=1+float(match[1])/float(match[2])
        else:
            numbers=re.findall(r'(?:Rs\.?|Re\.?)\s*(\d+(?:\.\d+)?)',subject,re.I)
            if len(numbers)>=2 and float(numbers[1])>0:factor=float(numbers[0])/float(numbers[1])
        if factor is None or factor<=0:
            unresolved.append(dict(key=spec['instrument_key'],symbol=spec['symbol'],day=day,subject=subject));continue
        value=grouped[(spec['instrument_key'],spec['symbol'],day)];value['factor']*=factor;value['subjects'].append(subject)
    result=[dict(key=k,symbol=s,day=d,**r) for (k,s,d),r in grouped.items()]
    return sorted(result,key=lambda x:(x['key'],x['day'])),unresolved


def factor_from_events(key,day,events,strict=True):
    """An ex-date already uses its new units; only strictly later actions apply."""
    factor=1.
    for event in events:
        if event['key']!=key or event['day']<=day:continue
        if strict and event.get('classification')!='back_adjusted':
            raise UnitBasisError('Unresolved future source unit basis: '+key+' '+event['day'])
        factor*=float(event['factor'])
    return factor


def price_factor(key,day,audit=None,out=OUT):
    audit=audit or load_audit(out)
    factor=factor_from_events(key,day,audit['events'])
    if factor!=1. and not audit['reciprocal_volume_confirmed'].get(key,False):
        raise UnitBasisError('Reciprocal volume convention not independently verified: '+key)
    return factor


def restore_bars(bars,factor):
    """Return a copy; raw PostgreSQL observations and RVOL inputs stay unchanged."""
    if not math.isfinite(factor) or factor<=0:raise ValueError('Invalid share-unit factor')
    restored=bars.copy()
    restored[['open','high','low','close']]*=factor
    restored['volume']/=factor
    return restored


def current_basis_prev_close(raw_previous_close,factor):
    return float(raw_previous_close)*float(factor)


def _nse_rows(path):
    with zipfile.ZipFile(path) as z:
        name=next(n for n in z.namelist() if n.lower().endswith('.csv'))
        return [r for r in csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig'))) if r.get('SctySrs')=='EQ']


def build_audit(out=OUT):
    from .data import connection,dump
    out=Path(out);folder=out/'unit-audit';folder.mkdir(parents=True,exist_ok=True)
    specs=json.loads(UNIVERSE.read_text())['stocks'];records=json.loads(ACTIONS.read_text())
    extension=folder/'nse-actions-2026-11-10-13.json'
    extra=json.loads(extension.read_text()) if extension.exists() else {}
    records+=extra.get('data',[])
    events,unresolved=combined_events(records,specs)
    eventkeys=sorted({e['key'] for e in events})
    with connection() as c:
        c.execute("SELECT instrument_key,(ts AT TIME ZONE 'Asia/Kolkata')::date,open,high,low,close,volume "
                  "FROM public.candles WHERE interval='1day' AND instrument_key=ANY(%s) AND ts>=%s AND ts<%s ORDER BY instrument_key,ts",
                  (eventkeys,START+' 00:00+05:30',END+' 23:59:59+05:30'))
        daily=pd.DataFrame(c.fetchall(),columns=['key','day','open','high','low','close','volume'])
    daily['day']=daily.day.astype(str)
    for e in events:
        data=daily[daily.key==e['key']];before=data[data.day<e['day']].tail(1);after=data[data.day>=e['day']].head(1)
        e['classification']='ambiguous'
        if before.empty or after.empty or after.day.iloc[0]!=e['day']:continue
        ratio=float(after.open.iloc[0]/before.close.iloc[0]);e['ex_open_previous_close_ratio']=ratio
        adjusted=abs(math.log(ratio));unadjusted=abs(math.log(ratio*e['factor']))
        if adjusted<unadjusted and adjusted<=.20:e['classification']='back_adjusted'
        elif unadjusted<adjusted and unadjusted<=.20:e['classification']='unadjusted'
    checks=[];missing_samples=[]
    by_key={s['instrument_key']:s for s in specs}
    for day in ('2024-11-14','2024-12-02','2025-06-13'):
        file=folder/(day.replace('-','')+'-nse-bhavcopy.zip')
        if not file.exists():missing_samples.append(day);continue
        nse=_nse_rows(file)
        by_symbol={r['TckrSymb']:r for r in nse};by_isin={r['ISIN']:r for r in nse}
        for key in eventkeys:
            spec=by_key[key];row=by_symbol.get(spec['symbol']) or by_symbol.get(spec.get('current_symbol')) or by_isin.get(spec['isin_at_start'])
            pg=daily[(daily.key==key)&(daily.day==day)]
            if row is None or pg.empty:continue
            factor=factor_from_events(key,day,events,strict=False)
            if factor<=1.:continue
            pg=pg.iloc[0];nse_volume=float(row['TtlTradgVol']);nse_close=float(row['ClsPric'])
            restored_close=float(pg.close)*factor
            volume_error=float(pg.volume)-nse_volume*factor
            close_error_bps=(restored_close/nse_close-1)*10000
            checks.append(dict(key=key,symbol=spec['symbol'],day=day,factor=factor,
                nse_raw_close=nse_close,nse_raw_volume=nse_volume,upstox_adjusted_close=float(pg.close),
                upstox_adjusted_volume=float(pg.volume),restored_close=restored_close,
                close_error_bps=close_error_bps,adjusted_volume_error_shares=volume_error,
                reciprocal_volume_matches=abs(volume_error)<=max(2.,nse_volume*factor*.0005),
                restored_price_matches=abs(close_error_bps)<=20.,source=str(file),source_sha256=sha(file)))
    confirmed={key:False for key in eventkeys}
    for key in eventkeys:
        evidence=[c for c in checks if c['key']==key]
        confirmed[key]=bool(evidence) and all(c['reciprocal_volume_matches'] and c['restored_price_matches'] for c in evidence)
    report=dict(version='intraday-contemporaneous-units-v1',events=events,unresolved_events=unresolved,
        reciprocal_volume_confirmed=confirmed,nse_bhavcopy_checks=checks,missing_nse_samples=missing_samples,
        sources=dict(actions=str(ACTIONS),actions_sha256=sha(ACTIONS),universe_sha256=sha(UNIVERSE),
            extension=str(extension),extension_sha256=sha(extension) if extension.exists() else None,
            extension_available=bool(extra.get('data') is not None)),
        policy='Restore prices × strictly-future share factor and volume ÷ factor locally only, after computing raw-basis RVOL; prior close uses current-session factor.',
        tolerance='NSE sample reciprocal-volume residual <=max(2adjusted shares,5bp); restored close within20bp. Vendor share-factor rounding causes observed volume residuals up to2bp; this is approximate reciprocal adjustment, not exact reconstruction of each original share.',
        limitation='Three official dated samples verify the per-company convention where available, not every historical quote. Known corporate-action coverage only; unknown restructurings remain separate exclusions.')
    dump(folder/'unit-adjustment-audit.json',report)
    return report


def load_audit(out=OUT):
    path=Path(out)/'unit-audit/unit-adjustment-audit.json'
    return json.loads(path.read_text()) if path.exists() else build_audit(out)


if __name__=='__main__':
    result=build_audit()
    print(json.dumps(dict(events=len(result['events']),stocks=len(result['reciprocal_volume_confirmed']),
        classified=dict(pd.Series([x['classification'] for x in result['events']]).value_counts()),
        confirmed=sum(result['reciprocal_volume_confirmed'].values()),nse_checks=len(result['nse_bhavcopy_checks'])),default=int))
