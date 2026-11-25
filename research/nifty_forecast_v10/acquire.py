"""Historical sector intraday synchronization and public equal-weight archives."""
import io
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
import requests
from .common import *
from research.nifty_forecast_v5.data import load

INDEX={'bank':'Nifty Bank','financial':'Nifty Fin Service','it':'Nifty IT','auto':'Nifty Auto'}
END='2026-11-17'


def download(name,url,headers,folder):
    p=OUT/folder/name;p.parent.mkdir(parents=True,exist_ok=True)
    log={'url':url,'path':str(p.relative_to(OUT)),'requested':now()}
    try:
        if not p.exists():
            response=requests.get(url,headers=headers,timeout=8);log.update(http=response.status_code,response_date=response.headers.get('Date'));response.raise_for_status();p.write_bytes(response.content)
        log.update(status='ok',bytes=p.stat().st_size,sha256=sha(p));return p,log
    except requests.RequestException as exc:log.update(status='unavailable',error=type(exc).__name__);return None,log


def intraday(index):
    sys.path.insert(0,str(ROOT/'backend'))
    from app.config import get_settings
    auth={'Authorization':'Bearer '+get_settings().upstox_analytics_token,'Accept':'application/json'}
    tasks=[]
    for n,label in INDEX.items():
        key=quote('NSE_INDEX|'+label,safe='')
        for start in pd.date_range('2025-01-01','2026-10-01',freq='QS'):
            end=min(start+pd.offsets.QuarterEnd(startingMonth=3),pd.Timestamp(END))
            tasks.append((n,str(start.date()),f'https://api.upstox.com/v3/historical-candle/{key}/minutes/25/{end.date()}/{start.date()}'))
    def get(args):
        n,s,url=args;p,log=download(f'{n}-{s}.json',url,auth,'sources/intraday');log['instrument']=n
        try:return n,read(p.name,p.parent)['data']['candles'] if p else [],log
        except (KeyError,ValueError):log['status']='invalid payload';return n,[],log
    with ThreadPoolExecutor(max_workers=4) as p:got=list(p.map(get,tasks))
    expected=list(range(555,930,25));ret={};invalid=[];all_n={}
    for n in INDEX:
        bars=[b for name,rows,_ in got if name==n for b in rows];all_n[n]=len(bars)
        a=pd.DataFrame(bars,columns=['ts','open','high','low','close','volume','oi']);date=pd.to_datetime(a.ts,utc=True).dt.tz_convert('Asia/Kolkata')
        a['day']=date.dt.strftime('%Y-%m-%d');a['minute']=date.dt.hour*60+date.dt.minute
        for d,g in a.groupby('day'):
            if d not in index:continue
            g=g.sort_values('minute');m=g[['open','high','low','close']].to_numpy(float)
            if list(g.minute)!=expected or not np.isfinite(m).all() or (m<=0).any() or (m[:,1]<m.max(axis=1)).any() or (m[:,2]>m.min(axis=1)).any():
                invalid.append({'day':d,'instrument':n,'n':len(g)});continue
            r=np.diff(np.log(np.r_[m[0,0],m[:,3]]));ret.setdefault(d,{})[n]=r
    rows=[]
    for d,names in sorted(ret.items()):
        if set(names)!=set(INDEX):continue
        z=np.column_stack([names[n] for n in INDEX]);corr=np.corrcoef(z.T)[np.triu_indices(len(INDEX),1)];morning=z[:2].sum(axis=0);late=z[-2:].sum(axis=0)
        if not np.isfinite(corr).all():continue
        rows.append({'day':d,'intra_open_breadth':np.mean(morning>0),'intra_late_breadth':np.mean(late>0),
                     'intra_sync':corr.mean(),'intra_close_open_rotation':late[1]-late[2]-(morning[1]-morning[2]),
                     'intra_late_risk_share':np.sum(z[-3:]**2)/np.sum(z**2),'intra_sector_risk':np.sqrt(np.sum(z**2,axis=0)).mean()})
    result=pd.DataFrame(rows);write('sector-intraday.csv',result)
    save('intraday-source-audit.json',{'requests':[r for _,_,r in got],'bars':all_n,'matched_complete':len(result),'excluded':invalid,
         'session_rule':'Four authentic sector indices, exact 15 x 25-minute regular IST closes. First/last two bars represent 50 minutes. Daily NIFTY labels retain authoritative archived closing values.'})
    print('Acquired',sum(all_n.values()),'sector candles with',len(result),'complete matched dates',flush=True)


def weighted_archives(index):
    browser={'User-Agent':'Mozilla/5.0 V10-Research'}
    # Query the published daily index archive. Only the historical native index closes are used.
    def get(d):
        day=pd.Timestamp(d);url=f'https://nsearchives.nseindia.com/content/indices/ind_close_all_{day:%d%m%Y}.csv'
        p,log=download(f'{d}.csv',url,browser,'sources/nse-daily');log['day']=d
        if not p:return {},log
        try:
            x=pd.read_csv(io.BytesIO(p.read_bytes()),skipinitialspace=True);x.columns=x.columns.str.strip()
            key=x.iloc[:,0].astype(str).str.lower().str.replace(r'[^a-z0-9]','',regex=True)
            output={'day':d}
            for n,k in [('eq50','nifty50equalweight'),('eq500','nifty500equalweight'),('cap50','nifty50'),('cap500','nifty500')]:
                s=x.loc[key==k,'Closing Index Value'];output[n]=float(s.iloc[0]) if len(s) else np.nan
            return output,log
        except (ValueError,KeyError,IndexError):log['status']='invalid payload';return {},log
    with ThreadPoolExecutor(max_workers=8) as p:res=list(p.map(get,index))
    df=pd.DataFrame([d for d,_ in res if d]);write('native-equal-weight-closes.csv',df)
    # A factsheet is only a dated snapshot. Do not turn it into a daily historical weights panel.
    facts,log=download('ind_nifty50.pdf','https://www.niftyindices.com/Factsheet/ind_nifty50.pdf',browser,'sources/constituents')
    save('breadth-source-audit.json',{'daily_archives':[l for _,l in res],'factsheet':log,'observed_counts':df.notna().sum().to_dict() if len(df) else {},
        'membership_status':'Historical daily constituent weights not established. Use official historical cap/equal-weight index contrasts only. No current member basket undergoes historical weighting.'})
    print('NSE official daily index rows:',len(df),'equal-weight observations:',df.notna().sum().to_dict(),flush=True)


def run():
    raw,_=load();idx=raw['nifty_spot'].index
    if not (OUT/'intraday-source-audit.json').exists():intraday(idx)
    if not (OUT/'breadth-source-audit.json').exists():weighted_archives(idx)
    # Isolated refresh uses the same evidenced API and archive reconciliation as V9.
    from research.nifty_forecast_v9 import acquire as v9
    nested=OUT/'refresh';nested.mkdir(exist_ok=True)
    v9.OUT=nested;v9.save=lambda n,d:save('refresh/'+n,d);v9.write=lambda n,d:write('refresh/'+n,d)
    if not (nested/'acquisition.json').exists():v9.run()


if __name__=='__main__':run()
