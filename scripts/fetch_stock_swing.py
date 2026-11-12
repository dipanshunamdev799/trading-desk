"""Read-only acquisition for the frozen 2024 NIFTY50 stock swing universe."""
from __future__ import annotations
import sys,json,re,time,hashlib,threading
from pathlib import Path
from datetime import date
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research.swing.data import _client,_frame,_windows,validate_sessions,special_execution_bars
OUT=ROOT/'artifacts'/'stock_swing_research'
SYMBOLS='ADANIENT ADANIPORTS APOLLOHOSP ASIANPAINT AXISBANK BAJAJ-AUTO BAJAJFINSV BAJFINANCE BEL BHARTIARTL BPCL BRITANNIA CIPLA COALINDIA DRREDDY EICHERMOT GRASIM HCLTECH HDFCBANK HDFCLIFE HEROMOTOCO HINDALCO HINDUNILVR ICICIBANK INDUSINDBK INFY ITC JSWSTEEL KOTAKBANK LT M&M MARUTI NESTLEIND NTPC ONGC POWERGRID RELIANCE SBILIFE SBIN SHRIRAMFIN SUNPHARMA TATACONSUM TATAMOTORS TATASTEEL TCS TECHM TITAN TRENT ULTRACEMCO WIPRO'.split()
LOCK=threading.Lock(); LAST=0.
def slot():
 global LAST
 with LOCK:
  time.sleep(max(0,.27-(time.monotonic()-LAST)));LAST=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def setup():
 OUT.mkdir(parents=True,exist_ok=True)
 import requests
 if not (OUT/'instrument-master.json').exists():
  (OUT/'instrument-master.json').write_text(json.dumps(_client().download_bod_instruments('NSE')))
 pdf=OUT/'nifty50-2024-11-11.pdf'
 if not pdf.exists():
  response=requests.get('https://taurusmutualfund.com/sites/default/files/2024-11/nifty-index-constituent-as-on-11_11_2024.pdf',timeout=30)
  response.raise_for_status();assert response.content.startswith(b'%PDF');pdf.write_bytes(response.content)
 if not (OUT/'universe-source.txt').exists():
  from pypdf import PdfReader
  (OUT/'universe-source.txt').write_text('\n'.join(p.extract_text() for p in PdfReader(pdf).pages),encoding='utf-8')
 if not (OUT/'nse-actions-all.json').exists():
  response=requests.get('https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date=01-01-2023&to_date=09-11-2026',
    headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.nseindia.com/','Accept':'application/json'},timeout=30)
  response.raise_for_status();assert isinstance(response.json(),list)
  (OUT/'nse-actions-all.json').write_text(response.text)
 master=json.loads((OUT/'instrument-master.json').read_text())
 eq={x['trading_symbol']:x for x in master if x.get('segment')=='NSE_EQ' and x.get('instrument_type')=='EQ'}
 rows=[]
 matches=re.findall(r'(INE[A-Z0-9]{9})\s+(.+?)\s+(\d+\.\d+)\s*$',(OUT/'universe-source.txt').read_text(),re.M)
 assert len(matches)==50
 for symbol,(isin,name,weight) in zip(SYMBOLS,matches):
  current=eq.get(symbol,eq.get('TMPV') if symbol=='TATAMOTORS' else None)
  rows.append({'symbol':symbol,'name_at_start':name.strip(),'isin_at_start':isin,'weight_at_start':float(weight),
               'instrument_key':current['instrument_key'] if current else 'NSE_EQ|'+isin,
               'current_symbol':current['trading_symbol'] if current else None})
 (OUT/'universe.json').write_text(json.dumps({'date':'2024-11-11','source_url':'https://taurusmutualfund.com/sites/default/files/2024-11/nifty-index-constituent-as-on-11_11_2024.pdf','source_sha256':sha(OUT/'nifty50-2024-11-11.pdf'),'policy':'Freeze starting membership; retain later index exits. Current master used only to resolve historical company keys/renames, not choose stocks.','stocks':rows},indent=2))
 return rows
def fetch(spec):
 symbol=spec['symbol'];key=spec['instrument_key'];client=_client();frames=[];windows=[]
 for first,last in _windows(date(2023,1,1),date(2026,11,9)):
  path=OUT/'raw'/symbol/f'{first}-{last}.json';path.parent.mkdir(parents=True,exist_ok=True)
  try:
   if path.exists():wrapped=json.loads(path.read_text())
   else:
    slot();payload=client.get_historical_candles_v3(key,'minutes',5,str(last),str(first))
    wrapped={'instrument_key':key,'from':str(first),'to':str(last),'retrieved_at':pd.Timestamp.now(tz='UTC').isoformat(),'payload':payload}
    path.write_text(json.dumps(wrapped))
   assert wrapped['instrument_key']==key
   f=_frame(wrapped);frames.append(f);windows.append({'from':str(first),'to':str(last),'rows':len(f),'sha256':sha(path)})
  except Exception as e:
   windows.append({'from':str(first),'to':str(last),'error':type(e).__name__,'status':getattr(e,'status_code',None)})
   print(symbol,first,'ERROR',type(e).__name__,getattr(e,'status_code',None),flush=True)
   if getattr(e,'status_code',None) in (400,401,403):break
 raw=pd.concat(frames).sort_index() if frames else _frame([])
 regular,audit=validate_sessions(raw,'2023-01-01','2026-11-10')
 special,sa=special_execution_bars(raw,regular,'2023-01-01','2026-11-10')
 regular.to_csv(OUT/f'{symbol}-regular.csv',index_label='ts');special.to_csv(OUT/f'{symbol}-special.csv',index_label='ts')
 # Daily endpoint independently checks whether whole regular sessions are absent.
 dp=OUT/'raw'/symbol/'daily.json'
 try:
  if dp.exists():daily=json.loads(dp.read_text())
  else:
   slot();daily=client.get_historical_candles_v3(key,'days',1,'2026-11-09','2023-01-01');dp.write_text(json.dumps(daily))
  days=set(_frame(daily).index.strftime('%Y-%m-%d'));missing=sorted(days-set(raw.index.strftime('%Y-%m-%d')))
 except Exception as e:missing=['daily_check_unavailable_'+type(e).__name__]
 audit.update(spec=spec,windows=windows,special=sa,whole_days_missing=missing,regular_sha256=sha(OUT/f'{symbol}-regular.csv'),special_sha256=sha(OUT/f'{symbol}-special.csv'))
 (OUT/f'{symbol}-audit.json').write_text(json.dumps(audit,indent=2,default=str))
 print(symbol,'READY',len(regular),regular.index.normalize().nunique(),'sessions',flush=True)
 return audit
def main():
 rows=setup();t=time.monotonic()
 with ThreadPoolExecutor(max_workers=4) as pool:audits=list(pool.map(fetch,rows))
 (OUT/'acquisition-summary.json').write_text(json.dumps({'stocks':len(rows),'elapsed_seconds':time.monotonic()-t,'audits':{a['spec']['symbol']:a for a in audits}},indent=2))
 print('COMPLETE',len(rows),round(time.monotonic()-t),flush=True)
if __name__=='__main__':main()
