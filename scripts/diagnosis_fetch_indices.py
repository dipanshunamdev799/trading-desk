"""Fetch official TRI via current website endpoint; default retains cached raw data."""
import argparse,json
from pathlib import Path
import requests
OUT=Path(__file__).resolve().parents[1]/'artifacts/swing_diagnosis';RAW=OUT/'benchmark_raw'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args();RAW.mkdir(parents=True,exist_ok=True);rows=[]
 for name in ['NIFTY 50','NIFTY 500','NIFTY BANK','NIFTY IT','NIFTY PHARMA']:
  target=RAW/(name.replace(' ','_')+'-tri.json');url='https://www.niftyindices.com/BackPage/getTotalReturnIndexString';item={'name':name,'url':url,'source_js':'https://liveindexsa.niftyindices.com/assets/js/IISLComponet.js'}
  try:
   if target.exists() and not args.refresh:data=json.loads(target.read_text());item['cached']=True
   else:
    info="{'name':'"+name+"','startDate':'01-Jan-2016','endDate':'09-Nov-2026','indexName':'"+name+"'}"
    r=requests.post(url,json={'cinfo':info},headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.niftyindices.com/reports/historical-data','Content-Type':'application/json; charset=UTF-8'},timeout=25);r.raise_for_status();(RAW/(name.replace(' ','_')+'-new.txt')).write_text(r.text);data=r.json();item.update(status=r.status_code,bytes=len(r.content),content_type=r.headers.get('Content-Type'))
    if isinstance(data,dict):data=json.loads(data.get('d','[]'))
    if isinstance(data,str):data=json.loads(data)
    if not isinstance(data,list) or not data or 'TotalReturnsIndex' not in data[0]:raise ValueError('Response is not a populated official TRI array')
    target.write_text(json.dumps(data))
   item.update(rows=len(data),sample=data[:1])
  except Exception as e:item['error']=str(e)
  rows.append(item);print(item,flush=True)
 # Keep the actual initial network acquisition record as provenance.
 (OUT/'benchmark-fetch-reproduction.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
