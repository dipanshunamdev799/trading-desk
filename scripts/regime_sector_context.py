from pathlib import Path
import sys,json,hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
import requests
from research.regime_opportunities.framework import OUT,save
from research.regime_opportunities.forward import INDEX_PERIODS,analyze,bh

def main():
    raw=OUT/'sector_raw';raw.mkdir(exist_ok=True)
    names=['NIFTY AUTO','NIFTY FMCG','NIFTY METAL','NIFTY REALTY','NIFTY ENERGY','NIFTY FINANCIAL SERVICES','NIFTY PSU BANK','NIFTY MEDIA','NIFTY CONSUMER DURABLES','NIFTY OIL & GAS','NIFTY HEALTHCARE INDEX']
    def fetch(name):
        target=raw/(name.replace(' ','_').replace('&','and')+'.json');meta={'index':name,'endpoint':'https://www.niftyindices.com/BackPage/getTotalReturnIndexString'}
        try:
            if target.exists():data=json.loads(target.read_text())
            else:
                info="{'name':'"+name+"','startDate':'01-Jan-2016','endDate':'09-Nov-2026','indexName':'"+name+"'}"
                r=requests.post(meta['endpoint'],json={'cinfo':info},headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.niftyindices.com/reports/historical-data','Content-Type':'application/json; charset=UTF-8'},timeout=25);r.raise_for_status();obj=r.json();data=json.loads(obj['d']) if isinstance(obj,dict) else json.loads(obj) if isinstance(obj,str) else obj
                assert isinstance(data,list) and data and 'TotalReturnsIndex' in data[0];target.write_text(json.dumps(data))
            a=pd.DataFrame(data);a['day']=pd.to_datetime(a.Date,format='%d %b %Y').dt.tz_localize('Asia/Kolkata');a['value']=pd.to_numeric(a.TotalReturnsIndex.astype(str).str.replace(',',''));a=a.sort_values('day')
            assert not a.day.duplicated().any();meta.update(rows=len(a),first=str(a.day.iloc[0].date()),last=str(a.day.iloc[-1].date()),sha256=hashlib.sha256(target.read_bytes()).hexdigest());return meta,a.set_index('day').value
        except Exception as e:meta['error']=type(e).__name__;return meta,None
    with ThreadPoolExecutor(max_workers=4) as pool:fetched=list(pool.map(fetch,names))
    save('expanded-sector-acquisition.json',[x[0] for x in fetched]);labels=pd.read_csv(OUT/'regime-labels.csv',index_col=0);features=pd.read_csv(OUT/'regime-features.csv',index_col=0);dates=pd.DatetimeIndex(pd.to_datetime(labels.index,utc=True)).tz_convert('Asia/Kolkata');columns=list(labels);mask=labels.to_numpy(bool);available=np.isfinite(features[columns].to_numpy())
    anchor=np.flatnonzero(dates>=pd.Timestamp('2017-01-01',tz=dates.tz))[0];grid=(np.arange(len(dates))-anchor)%20==0;rows=[];paths=[]
    for meta,series in fetched:
        if series is None:continue
        x=series.reindex(dates).to_numpy();paths.append(pd.DataFrame({'day':dates,'index':meta['index'],'TRI':x}));y=np.full(len(x),np.nan);y[:-10]=100*(x[10:]/x[:-10]-1)
        if meta['index'] in ['NIFTY CONSUMER DURABLES','NIFTY OIL & GAS']:y[dates<pd.Timestamp('2020-01-15',tz=dates.tz)]=np.nan
        for stage,(start,end) in INDEX_PERIODS.items():
            use=(dates>=pd.Timestamp(start,tz=dates.tz))&(dates<pd.Timestamp(end,tz=dates.tz));future=np.r_[dates[10:].asi8,np.full(10,np.iinfo(np.int64).max)];use&=future<pd.Timestamp(end,tz=dates.tz).value
            for method,choose in [('all_dates_block20',use),('nonoverlap20grid',use&grid)]:
                ix=np.flatnonzero(choose);rows+=analyze(y[ix],mask[ix],available[ix],columns,stage,meta['index']+'_TRI',10,method,ix)
        print('SECTOR_CONTEXT',meta['index'],meta['rows'],flush=True)
    extra=pd.DataFrame(rows);extra.to_csv(OUT/'expanded-sector-forward.csv',index=False)
    if paths:pd.concat(paths).to_csv(OUT/'expanded-sector-TRI.csv',index=False)
    core=pd.read_csv(OUT/'forward-regime-contrasts.csv');combined=pd.concat([core,extra],ignore_index=True);combined['bh_q']=np.nan;combined['BY_q']=np.nan
    for _,g in combined.groupby(['stage','horizon','method']):
        q=bh(g.p);combined.loc[g.index,'bh_q']=q;combined.loc[g.index,'BY_q']=np.minimum(1,q*np.sum(1/np.arange(1,len(g)+1)))
    combined.to_csv(OUT/'forward-contrasts-combined.csv',index=False)
    save('sector-context-scope.json',dict(regime_classifier='FrozenBank/IT/Pharma3sectorproxyunchanged. AdditionalofficialsectorTRIonlysecondaryoutcomesbyalreadyfrozenregimes; noentryselectionornewregime thresholds.',horizon=10,
      missing='Failed/shortindexhistoriesexplicitinacquisitionmanifest, no syntheticbackfill. ConfirmedConsumerDurables/OilGas prelaunchobservationsbefore15Jan2020excluded frominferentialoutcomes. Otheraddedindiceslaunchhistorynotindividuallycertified; secondarycontextonly. Currentcohortsectorlabelsnotusedforlongindexhistory.',launch_source='https://www.niftyindices.com/Press_Release/ind_prs15012020.pdf',multiple_testing='RecomputeBH/BYovercombinedcore+expandedoutcomes perstage/horizon/method. Originalfrozenchoicesremainbaseddevelopmentstockcontrasts, unchanged.'))
    print('EXPANDED_SECTOR_COMPLETE',len(extra),flush=True)

if __name__=='__main__':main()
