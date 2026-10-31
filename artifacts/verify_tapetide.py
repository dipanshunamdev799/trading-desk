"""Read-only provider comparison. Supply Tapetide refresh token on stdin."""
import sys, json, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from app.services.upstox_service import get_upstox

token = sys.stdin.readline().strip()
r = requests.post('https://mcp.tapetide.com/token', data={'grant_type':'refresh_token','refresh_token':token}, timeout=30)
r.raise_for_status()
headers = {'Authorization':'Bearer '+r.json()['access_token'], 'Accept':'application/json, text/event-stream'}
def tap(name, args):
    r=requests.post('https://mcp.tapetide.com/mcp', headers=headers, json={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':name,'arguments':args}}, timeout=45)
    r.raise_for_status()
    raw=r.json()
    text=raw['result']['content'][0]['text']
    try: return json.loads(text)
    except ValueError: return {'unparsed_text':text,'isError':raw['result'].get('isError')}
jobs=[('RELIANCE','get_price_history',{'symbol':'RELIANCE','days':20}),('TCS','get_price_history',{'symbol':'TCS','days':20}),('HDFCBANK','get_price_history',{'symbol':'HDFCBANK','days':20}),('quotes','get_batch_quotes',{'symbols':['RELIANCE','TCS','HDFCBANK']}),('flows','get_fii_dii_detail',{})]
out={'tapetide':{},'upstox':{},'comparison':{}}
with ThreadPoolExecutor(max_workers=3) as pool:
    futures=[(label,pool.submit(tap,name,args)) for label,name,args in jobs]
    for label,f in futures:
        try:out['tapetide'][label]=f.result()
        except Exception as e:out['tapetide'][label]={'error':str(e)}
initial=json.loads((ROOT/'artifacts/tapetide-initial-data.json').read_text())
for label,name in [('NIFTY','get_index_history'),('options','get_option_chain')]:
    out['tapetide'][label]=json.loads(initial[name]['result']['content'][0]['text'])
c=get_upstox()
keys={'RELIANCE':'NSE_EQ|INE002A01018','TCS':'NSE_EQ|INE467B01029','HDFCBANK':'NSE_EQ|INE040A01034','NIFTY':'NSE_INDEX|Nifty 50'}
for label,key in keys.items():
    d=out['tapetide'][label].get('data',[])
    rows=d['bars'] if isinstance(d,dict) else d
    if not rows:continue
    lo=min(x['date'] for x in rows);hi=max(x['date'] for x in rows)
    try:
        raw=c.get_historical_candles_v3(key,'days',1,hi,lo)
        out['upstox'][label]=raw
        candles=raw.get('candles',[]) if isinstance(raw,dict) else raw
        byday={x[0][:10]:x for x in candles}
        mismatches=[];matched=0;missing=[]
        fields=['open','high','low','close']+([] if label=='NIFTY' else ['volume'])
        for row in rows:
            bar=byday.get(row['date'])
            if bar is None:missing.append(row['date']);continue
            matched+=1
            for i,field in enumerate(fields,1):
                a=row[field];b=bar[i]
                if abs(float(a)-float(b))> (0.011 if field!='volume' else 0):
                    mismatches.append({'date':row['date'],'field':field,'tapetide':a,'upstox':b,'difference':round(a-b,6)})
        out['comparison'][label]={'tapetide_rows':len(rows),'matched_dates':matched,'fields':fields,'missing_in_upstox':missing,'missing_in_tapetide':sorted(set(byday)-{x['date'] for x in rows}),'mismatches':mismatches}
    except Exception as e:out['comparison'][label]={'error':str(e)}
opt=out['tapetide']['options']['data'];day=opt['snapshot_ts'][:10];expiry=opt['expiry_date']
for name,fn in [('oi',lambda:c.get_oi_data(keys['NIFTY'],expiry,day)),('pcr',lambda:c.get_pcr(keys['NIFTY'],expiry,day,1)),('max_pain',lambda:c.get_max_pain(keys['NIFTY'],expiry,day,1)),('quotes',lambda:c.get_full_market_quotes_v3(list(keys.values())[:3])),('fii',lambda:c.get_fii_data(from_date='2026-10-01')),('dii',lambda:c.get_dii_data(from_date='2026-10-01'))]:
    try:out['upstox'][name]=fn()
    except Exception as e:out['upstox'][name]={'error':str(e)}
(ROOT/'artifacts/tapetide-upstox-comparison.json').write_text(json.dumps(out,indent=2,default=str))
print(json.dumps(out['comparison'],indent=2))
for k in ['oi','pcr','max_pain','quotes','fii','dii']:print(k,str(out['upstox'].get(k))[:1400])
print('TAP QUOTES',str(out['tapetide']['quotes'])[:2000]);print('TAP FLOWS',str(out['tapetide']['flows'])[:2000])
