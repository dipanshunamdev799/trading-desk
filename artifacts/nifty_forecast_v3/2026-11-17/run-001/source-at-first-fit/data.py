"""Read-only V3 data acquisition. Persist only observations dated 2025-2026."""
from __future__ import annotations
import csv,io,json,sys,time,zipfile
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import requests
from .audit import ROOT,OUT,OLD,sha,save
sys.path[:0]=[str(ROOT/'backend')]
from app.config import get_settings
from app.services.nifty_sources import INDEX_KEYS
from upstox_analytics import UpstoxAnalyticsClient

START='2025-01-01';END='2026-11-16'
GLOBAL={'global_sp500':'GLOBAL_INDEX|^GSPC','global_dow':'GLOBAL_INDEX|^DJI','global_hang_seng':'GLOBAL_INDEX|^HSI',
    'global_gift':'GLOBAL_INDEX|SGX NIFTY','global_brent':'GLOBAL_INDICATOR|BZUSD','global_usdinr':'GLOBAL_INDICATOR|USDINR'}

def candles(payload):
    records=[]
    for r in payload.get('candles',[]):
        day=pd.Timestamp(r[0]).tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
        if START<=day<=END:records.append({'day':day,'ts':r[0],**dict(zip(['open','high','low','close','volume','oi'],r[1:7]))})
    return records

def collect_upstox():
    dest=OUT/'sources/upstox';dest.mkdir(parents=True,exist_ok=True)
    members=json.loads((OLD/'inputs-v2/dashboard-fresh.json').read_text())['constituents']['members']
    save('current-basket-identities.json',{'classification':'research-only current-membership backcast proxy',
        'source':str(OLD/'inputs-v2/dashboard-fresh.json'),'source_sha256':sha(OLD/'inputs-v2/dashboard-fresh.json'),'members':members})
    keys={**INDEX_KEYS,'nifty_500':'NSE_INDEX|Nifty 500','niftybees':'NSE_EQ|INF204KB14I2',**GLOBAL}
    keys.update({'stock_'+r['symbol']:r['instrument_key'] for r in members})
    token=get_settings().upstox_analytics_token
    def fetch(item):
        name,key=item;path=dest/(name+'.json')
        if path.exists():return name,json.loads(path.read_text())
        c=UpstoxAnalyticsClient(token,timeout=20,max_retries=0)
        try:
            raw=c.get_historical_candles_v3(key,'days',1,END,START)
            obj={'ok':True,'instrument_key':key,'source':'Upstox historical V3','rows':candles(raw)}
        except Exception as e:obj={'ok':False,'instrument_key':key,'error':str(e)[:500]}
        finally:c.session.close()
        obj['acquired_at']=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
        path.write_text(json.dumps(obj),encoding='utf-8');time.sleep(.25)
        return name,obj
    status=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(fetch,j) for j in keys.items()]):
            name,obj=f.result();status.append({'name':name,'ok':obj['ok'],'rows':len(obj.get('rows',[]))})
    save('upstox-acquisition.json',{'start':START,'end':END,'jobs':status,
        'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(dest.glob('*.json'))}})
    print(json.dumps({'upstox_jobs':len(status),'failed':[r for r in status if not r['ok']]}),flush=True)

def read_nifty_fo(path,day):
    with zipfile.ZipFile(path) as z:
        names=[n for n in z.namelist() if n.lower().endswith('.csv')]
        if len(names)!=1 or z.getinfo(names[0]).file_size>150_000_000:raise ValueError('Invalid archive shape')
        with io.TextIOWrapper(z.open(names[0]),encoding='utf-8-sig') as stream:
            rows=[r for r in csv.DictReader(stream) if r['TckrSymb']=='NIFTY']
    if not rows or any(r['TradDt']!=day for r in rows):raise ValueError('Archive source date mismatch')
    return [{k:r[k] for k in ['TradDt','FinInstrmTp','FinInstrmId','XpryDt','FininstrmActlXpryDt','StrkPric','OptnTp',
        'ClsPric','SttlmPric','UndrlygPric','OpnIntrst','ChngInOpnIntrst','TtlTradgVol','NewBrdLotQty']} for r in rows]

def collect_fo():
    dest=OUT/'sources/fo';dest.mkdir(parents=True,exist_ok=True)
    raw=OUT/'sources';old=ROOT/'artifacts/directional_research_phase2/option-nse-raw'
    d=json.loads((OUT/'sources/upstox/nifty_spot.json').read_text())
    days=sorted({r['day'] for r in d['rows']})
    # A delayed broker daily endpoint can omit Monday; the official archive
    # independently verifies its closing underlying and current contract universe.
    if END not in days:days.append(END)
    def fetch(day):
        compact=dest/(day+'.json')
        if compact.exists():return json.loads(compact.read_text())
        sources=[old/(day+'.zip'),raw/('fo-'+day.replace('-','')+'.zip')]
        path=next((p for p in sources if p.exists()),None)
        url='https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'+day.replace('-','')+'_F_0000.csv.zip'
        result={'day':day,'source_url':url}
        try:
            if path is None:
                r=requests.get(url,timeout=20,headers={'User-Agent':'Mozilla/5.0 NiftyResearch/3.0'});r.raise_for_status()
                path=raw/('fo-'+day.replace('-','')+'.zip');path.write_bytes(r.content);time.sleep(.4)
            rows=read_nifty_fo(path,day)
            result.update(ok=True,source_path=str(path),sha256_zip=sha(path),rows=rows)
        except Exception as e:result.update(ok=False,error=str(e)[:250])
        result['acquired_at']=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
        compact.write_text(json.dumps(result),encoding='utf-8');return result
    records=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for i,f in enumerate(as_completed([pool.submit(fetch,day) for day in days]),1):
            records.append(f.result())
            if i%50==0:print('Official FO archives',i,'/',len(days),flush=True)
    save('fo-acquisition.json',{'sessions':len(records),'ok':sum(r['ok'] for r in records),
        'failed':[r for r in records if not r['ok']],
        'files':{str((dest/(r['day']+'.json')).relative_to(ROOT)):sha(dest/(r['day']+'.json')) for r in records}})
    print(json.dumps({'fo_sessions':len(records),'ok':sum(r['ok'] for r in records)}),flush=True)

def load_series():
    data={};quality=[]
    for path in sorted((OUT/'sources/upstox').glob('*.json')):
        doc=json.loads(path.read_text())
        if not doc['ok'] or not doc['rows']:continue
        frame=pd.DataFrame(doc['rows'])
        raw=len(frame);dup=int(frame.duplicated('day').sum())
        valid=np.isfinite(frame[['open','high','low','close']]).all(axis=1)&(frame[['open','high','low','close']]>0).all(axis=1)
        valid &= frame.high.ge(frame[['open','close','low']].max(axis=1))&frame.low.le(frame[['open','close','high']].min(axis=1))
        bad=int((~valid).sum());frame=frame.loc[valid].sort_values('ts').drop_duplicates('day',keep='first').set_index('day').sort_index()
        frame=frame.loc[(frame.index>=START)&(frame.index<=END)]
        data[path.stem]=frame
        quality.append({'name':path.stem,'raw':raw,'duplicates':dup,'invalid':bad,'valid_sessions':len(frame),
            'first':frame.index.min(),'last':frame.index.max(),'volume_positive':int(frame.volume.gt(0).sum()),
            'classification':'research-only current stock basket' if path.stem.startswith('stock_') else 'usable with revised-history/publication limitations'})
    return data,quality

def fo_features(data):
    rows=[];previous={}
    for p in sorted((OUT/'sources/fo').glob('*.json')):
        doc=json.loads(p.read_text())
        if not doc['ok']:continue
        day=doc['day'];source=doc['rows'];futures=[r for r in source if r['FinInstrmTp']=='IDF']
        options=[r for r in source if r['OptnTp'] in ['CE','PE'] and (r['FininstrmActlXpryDt'] or r['XpryDt'])>day]
        expiries=sorted({r['FininstrmActlXpryDt'] or r['XpryDt'] for r in options})
        spot=float(next(r['UndrlygPric'] for r in source if float(r.get('UndrlygPric') or 0)>0))
        row={'day':day,'spot_official':spot}
        if futures:
            f=min((r for r in futures if (r['FininstrmActlXpryDt'] or r['XpryDt'])>day),key=lambda r:r['FininstrmActlXpryDt'] or r['XpryDt'])
            row.update(fut_basis=float(f['ClsPric'])/spot-1,fut_oi=float(f['OpnIntrst']),fut_oi_change=float(f['ChngInOpnIntrst'])/max(1,float(f['OpnIntrst'])),
                fut_dte=(pd.Timestamp(f['FininstrmActlXpryDt'] or f['XpryDt'])-pd.Timestamp(day)).days,
                fut_contract=f['FinInstrmId'],fut_lot=float(f['NewBrdLotQty']))
        if expiries:
            expiry=expiries[0];legs=[r for r in options if (r['FininstrmActlXpryDt'] or r['XpryDt'])==expiry]
            call=[r for r in legs if r['OptnTp']=='CE'];put=[r for r in legs if r['OptnTp']=='PE']
            co=sum(float(r['OpnIntrst']) for r in call);po=sum(float(r['OpnIntrst']) for r in put)
            cv=sum(float(r['TtlTradgVol']) for r in call);pv=sum(float(r['TtlTradgVol']) for r in put)
            if co>0 and po>0:
                row.update(oi_pcr=np.log(po/co),volume_pcr=np.log((pv+1)/(cv+1)),
                    call_concentration=max(float(r['OpnIntrst']) for r in call)/co,
                    put_concentration=max(float(r['OpnIntrst']) for r in put)/po,
                    call_wall=max(call,key=lambda r:float(r['OpnIntrst']))['StrkPric'],
                    put_wall=max(put,key=lambda r:float(r['OpnIntrst']))['StrkPric'],
                    option_dte=(pd.Timestamp(expiry)-pd.Timestamp(day)).days)
                row['call_wall']=float(row['call_wall'])/spot-1;row['put_wall']=float(row['put_wall'])/spot-1
                strikes=np.array(sorted({float(r['StrkPric']) for r in legs}));payout=np.zeros(len(strikes))
                for r in legs:
                    strike=float(r['StrkPric']);oi=float(r['OpnIntrst'])
                    payout+=oi*(np.maximum(strikes-strike,0) if r['OptnTp']=='CE' else np.maximum(strike-strikes,0))
                row['maxpain_distance']=strikes[np.argmin(payout)]/spot-1
                current={r['FinInstrmId']:r for r in legs};prior=previous.get(expiry,{})
                common=[key for key in current.keys()&prior.keys() if current[key]['NewBrdLotQty']==prior[key]['NewBrdLotQty']]
                a=[current[k] for k in common];b=[prior[k] for k in common]
                totals=lambda l,s:sum(float(r['OpnIntrst']) for r in l if r['OptnTp']==s)
                values=[totals(l,s) for l,s in [(a,'PE'),(a,'CE'),(b,'PE'),(b,'CE')]]
                row['matched_pcr_change']=float(np.log(values[0]/values[1])-np.log(values[2]/values[3])) if min(values,default=0)>0 else np.nan
                previous[expiry]=current
        rows.append(row)
    frame=pd.DataFrame(rows).set_index('day').sort_index()
    frame['fut_oi_log_change']=np.log(frame.fut_oi.replace(0,np.nan)).diff()
    same=frame.fut_contract.eq(frame.fut_contract.shift())&frame.fut_lot.eq(frame.fut_lot.shift())
    frame['fut_roll_flag']=(~same).astype(float)
    frame.loc[~same,'fut_oi_log_change']=np.nan
    frame.to_csv(OUT/'fo-eod-panel.csv')
    return frame

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('command',choices=['upstox','fo']);args=p.parse_args()
    collect_upstox() if args.command=='upstox' else collect_fo()
