"""Documented public downloads; bounded dates and transparent access failures."""
import requests,io,shutil
from .common import *
def run():
    results=[]
    for name in ['DGS10','DGS2','DTWEXBGS','VIXCLS']:
        url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={name}&cosd={START}&coed={END}'
        path=OUT/'extras'/f'{name}.csv';path.parent.mkdir(parents=True,exist_ok=True);sent=now()
        try:
            r=requests.get(url,timeout=20,headers={'User-Agent':'Mozilla/5.0 NiftyResearch/5.0'});r.raise_for_status();f=pd.read_csv(io.StringIO(r.text))
            f.columns=['day','value'];f=f[(f.day>=START)&(f.day<=END)];f['value']=pd.to_numeric(f.value,errors='coerce');f=f.dropna();scope(f.day);f.to_csv(path,index=False)
            results.append({'series':name,'ok':True,'url':url,'sent':sent,'received':now(),'server_date':r.headers.get('Date'),'rows':len(f),'first':f.day.min() if len(f) else None,'last':f.day.max() if len(f) else None,'sha256':sha(path),
                'provenance':'FRED public CSV download; original source Treasury/FRB; VIX original CBOE copyrighted, citation required; research analysis only, no raw republishing',
                'availability':'Conservative2-business-day delay; old actual receipt/revision time unavailable; not an as-delivered vintage'})
        except Exception as e:results.append({'series':name,'ok':False,'url':url,'sent':sent,'received':now(),'error':type(e).__name__})
        print('Public supplement',name,results[-1]['ok'],flush=True)
    save('extra-acquisition.json',results)
    # Do not touch V3/V4 archives; derive only from an isolated copy.
    dest=OUT/'fo';dest.mkdir(exist_ok=True)
    for p in (V3/'sources/fo').glob('*.json'):shutil.copy2(p,dest/p.name)
    from research.nifty_forecast_v3.data import read_nifty_fo
    for day in ['2026-11-17','2026-11-18']:
        url='https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'+day.replace('-','')+'_F_0000.csv.zip';sent=now()
        try:
            response=requests.get(url,timeout=20,headers={'User-Agent':'Mozilla/5.0 NiftyResearch/5.0'});response.raise_for_status();p=dest/(day+'.zip');p.write_bytes(response.content)
            save('fo/'+day+'.json',{'ok':True,'day':day,'rows':read_nifty_fo(p,day),'url':url,'sent':sent,'received':now(),'zip_sha256':sha(p)})
        except Exception as e:save('fo/'+day+'.json',{'ok':False,'day':day,'url':url,'received':now(),'error':type(e).__name__})
    print('Supplement/FO acquisition complete',flush=True)
if __name__=='__main__':run()
