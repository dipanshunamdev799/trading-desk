"""Bounded read-only market archive acquisition, separate from frozen vintages."""
import gzip
import io
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import requests
from .common import *

FROZEN='2026-11-17'
ADDITIONAL={'private_bank':'NIFTY PVT BANK','bankbees':'BANKBEES','psu_etf':'PSUBNKBEES',
            'financial_etf':'FINIETF','insurance_sbi':'SBILIFE','insurance_hdfc':'HDFCLIFE','insurance_icici':'ICICIPRULI'}
REFRESH=['nifty_spot','india_vix','bank_nifty','nifty_financial','nifty_psu_bank','idx_Nifty_500','nifty_fmcg','nifty_pharma','nifty_auto','nifty_metal','nifty_energy','nifty_it','nifty_realty','niftybees']


def run():
    today=pd.Timestamp(now())
    safe_day=today.normalize()-pd.Timedelta(days=int(today.hour<16))
    end=min(safe_day.date().isoformat(),'2026-12-31')
    if end<=FROZEN:raise RuntimeError('No post-vintage completed dates')
    sys.path.insert(0,str(ROOT/'backend'))
    from app.config import get_settings
    token=get_settings().upstox_analytics_token
    old={r['name']:r for r in read('data-manifest.json',V8)['inventory']}
    path=V5/'metadata/NSE.json.gz';keys=json.loads(gzip.decompress(path.read_bytes()))
    selected={s:next((r for r in keys if r.get('trading_symbol')==ticker and r.get('segment') in ['NSE_INDEX','NSE_EQ']),None) for s,ticker in ADDITIONAL.items()}
    plan=[(n,old[n]['key'],'2026-11-10') for n in REFRESH]+[(n,r['instrument_key'],'2025-01-01') for n,r in selected.items() if r]
    archive=OUT/'market-sources';archive.mkdir(parents=True,exist_ok=True)
    def grab(job):
        name,key,start=job;url=f'https://api.upstox.com/v3/historical-candle/{quote(key,safe="")}/days/1/{end}/{start}'
        log={'name':name,'key':key,'start':start,'end':end,'url':url,'sent':now()}
        destination=archive/(name+'.json')
        try:
            if destination.exists():data=json.loads(destination.read_bytes())
            else:
                r=requests.get(url,headers={'Authorization':'Bearer '+token,'Accept':'application/json'},timeout=12)
                log.update(http=r.status_code,received=now(),server_date=r.headers.get('Date'));r.raise_for_status()
                data=r.json();destination.write_bytes(r.content)
            table=pd.DataFrame(data['data']['candles'],columns=['stamp','open','high','low','close','volume','oi'])
            stamps=pd.to_datetime(table.stamp,utc=True).dt.tz_convert('Asia/Kolkata');table['day']=stamps.dt.strftime('%Y-%m-%d')
            values=table[['open','high','low','close']].to_numpy(float)
            valid=np.isfinite(values).all(axis=1)&(values>0).all(axis=1)&(values[:,1]>=values.max(axis=1))&(values[:,2]<=values.min(axis=1))
            table=table[valid & table.day.between(start,end)].sort_values('day').drop_duplicates('day')
            table['instrument']=name;log.update(status='ok',rows=len(table),sha256=sha(destination),first=table.day.min(),last=table.day.max())
            return log,table
        except (requests.RequestException,KeyError,ValueError) as exc:
            log.update(status='unavailable',failure=type(exc).__name__);return log,pd.DataFrame()
    with ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(grab,plan))
    candles=pd.concat([f for _,f in result],ignore_index=True);write('acquired-candles.csv',candles)
    nse=[]
    fresh=candles[(candles.instrument=='nifty_spot')&(candles.day>FROZEN)]
    for r in fresh.itertuples():
        date=pd.Timestamp(r.day);url=f'https://nsearchives.nseindia.com/content/indices/ind_close_all_{date:%d%m%Y}.csv'
        log={'origin':r.day,'url':url,'upstox_close':r.close,'sent':now()};path=archive/f'NSE-indices-{r.day}.csv'
        try:
            if not path.exists():
                response=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=10);log['http']=response.status_code;response.raise_for_status();path.write_bytes(response.content)
            f=pd.read_csv(io.BytesIO(path.read_bytes()));f.columns=f.columns.str.strip();row=f[f.iloc[:,0].astype(str).str.strip()=='Nifty 50'].iloc[0]
            close=float(row['Closing Index Value']);log.update(official_close=close,delta=close-r.close,sha256=sha(path),status='verified')
        except (requests.RequestException,KeyError,ValueError,IndexError) as exc:log.update(status='unavailable',failure=type(exc).__name__)
        nse.append(log)
    overlap=[]
    for name in REFRESH:
        earlier=V5/'sources'/f'{name}.json'
        if not earlier.exists():continue
        lookup={r['day']:r['close'] for r in json.loads(earlier.read_bytes())['rows']}
        for r in candles[(candles.instrument==name)&(candles.day<=FROZEN)].itertuples():
            if r.day in lookup:overlap.append({'asset':name,'date':r.day,'old_close':lookup[r.day],'new_close':r.close,'delta':r.close-lookup[r.day]})
    write('source-overlap.csv',pd.DataFrame(overlap))
    save('acquisition.json',{'frozen_through':FROZEN,'chosen_completed_boundary':end,'requests':[l for l,_ in result],
          'unmatched_metadata':[n for n,r in selected.items() if r is None],'official_crosscheck':nse,
          'new_NIFTY_sessions':list(fresh.day),'membership':'Selected insurance equities and financial ETFs are explicit instruments, not historical index constituents.'})
    print('Acquired',len(candles),'validated bars. New completed NIFTY dates',list(fresh.day),flush=True)


if __name__=='__main__':run()
