"""Authenticated universe discovery and bounded2025–2026 acquisition."""
import csv,gzip,io,json,time,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import quote
import requests
from .common import *

def public(url,name):
    p=OUT/'metadata'/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():return p.read_bytes()
    sent=now();r=requests.get(url,timeout=35,headers={'User-Agent':'Mozilla/5.0 NiftyResearch/5.0'});r.raise_for_status();p.write_bytes(r.content)
    save('metadata/'+name+'.provenance.json',{'source_url':url,'sent':sent,'received':now(),'server_date':r.headers.get('Date'),'sha256':sha(p),'classification':'Current metadata, not historical membership'})
    return r.content

def acquire():
    sys.path[:0]=[str(ROOT/'backend')]
    from app.config import get_settings
    from app.services.nifty_sources import INDEX_KEYS
    token=get_settings().upstox_analytics_token
    globals_=json.loads(gzip.decompress(public('https://assets.upstox.com/market-quote/instruments/exchange/global.json.gz','global.json.gz')))
    master=json.loads(gzip.decompress(public('https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz','NSE.json.gz')))
    save('global-instrument-inventory.json',globals_)
    indices=[r for r in master if r.get('segment')=='NSE_INDEX'];save('domestic-index-inventory.json',indices)
    keys={k:{'key':v,'family':'domestic','label':k} for k,v in INDEX_KEYS.items()}
    # Native broad/size/style/sector index series; fixed metadata-based inclusion, no return selection.
    terms=['Nifty 100','Nifty 200','Nifty 500','Nifty Midcap','Nifty Smallcap','Nifty Next 50','Nifty 50 Equal','Nifty Consumption','Nifty Commodities','Nifty Infra','Nifty India Defence','Nifty Healthcare','Nifty Private Bank']
    for r in sorted(indices,key=lambda r:r['instrument_key']):
        label=r.get('name',r.get('trading_symbol',''))
        if any(t.lower() in label.lower() for t in terms):keys['idx_'+r['instrument_key'].split('|')[-1].replace(' ','_')]={'key':r['instrument_key'],'family':'domestic','label':label}
    keys['niftybees']={'key':'NSE_EQ|INF204KB14I2','family':'etf','label':'NIFTYBEES'}
    # Every actually listed global instrument is probed; no invented category coverage.
    for r in globals_:
        key=r.get('instrument_key');label=r.get('name',r.get('trading_symbol',key))
        if key:keys['g_'+key.split('|')[-1].replace('/','_').replace(' ','_')]={'key':key,'family':'global','label':label}
    # Current broad-index universe is research-only. Fixed first100 symbols outside old50.
    members=list(csv.DictReader(io.StringIO(public('https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv','nifty500-current.csv').decode('utf-8-sig'))))
    old=read('current-basket-identities.json',V3)['members'];oldsymbols={r['symbol'] for r in old}
    lookup={r.get('trading_symbol'):r for r in master if r.get('segment')=='NSE_EQ' and r.get('instrument_type')=='EQ'}
    extra=[r for r in sorted(members,key=lambda r:r['Symbol']) if r['Symbol'] not in oldsymbols and r['Symbol'] in lookup][:100]
    for r in old:keys['s_'+r['symbol']]={'key':r['instrument_key'],'family':'stock_proxy','label':r['symbol'],'industry':'CURRENT_MEMBERSHIP_UNAUTHENTICATED'}
    for r in extra:keys['s_'+r['Symbol']]={'key':lookup[r['Symbol']]['instrument_key'],'family':'stock_proxy','label':r['Symbol'],'industry':r.get('Industry','unknown')}
    save('requested-universe.json',{'registered_before_returns':now(),'identities':keys,'stock_selection':'old50 plus alphabetical first100 currently listed Nifty500 members outside old50; research-only, no historical index weights'})
    dest=OUT/'sources';dest.mkdir(exist_ok=True)
    def fetch(item):
        name,meta=item;p=dest/(name+'.json')
        if p.exists():return json.loads(p.read_text())
        sent=now();url='https://api.upstox.com/v3/historical-candle/'+quote(meta['key'],safe='')+'/days/1/'+END+'/'+START
        try:
            response=requests.get(url,headers={'Authorization':'Bearer '+token,'Accept':'application/json'},timeout=25)
            if response.status_code!=200:raise ValueError('HTTP_'+str(response.status_code))
            raw=response.json().get('data',{}).get('candles',[]);rows=[]
            for r in raw:
                stamp=pd.Timestamp(r[0]);day=stamp.tz_convert('Asia/Kolkata').strftime('%Y-%m-%d')
                if START<=day<=END:rows.append({'day':day,'ts':r[0],**dict(zip(['open','high','low','close','volume','oi'],r[1:7]))})
            doc={'name':name,**meta,'ok':True,'rows':rows,'source_url':url,'sent_at':sent,'received_at':now(),'server_date':response.headers.get('Date')}
        except Exception as e:doc={'name':name,**meta,'ok':False,'rows':[],'error':str(e)[:180],'sent_at':sent,'received_at':now()}
        p.write_text(json.dumps(doc),encoding='utf-8');time.sleep(.2);return doc
    results=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for i,f in enumerate(as_completed([pool.submit(fetch,j) for j in keys.items()]),1):
            d=f.result();results.append({'name':d['name'],'family':d['family'],'ok':d['ok'],'rows':len(d['rows']),'error':d.get('error')})
            if i%25==0:print('Acquired',i,'/',len(keys),flush=True)
    save('acquisition.json',{'requested':len(keys),'results':results,'files':{str(p.relative_to(ROOT)):sha(p) for p in dest.glob('*.json')}})
    print('Acquisition complete',len(results),'HTTP failures',sum(not r['ok'] for r in results),flush=True)

def load():
    data={};inventory=[]
    for p in sorted((OUT/'sources').glob('*.json')):
        doc=json.loads(p.read_text());row={k:doc.get(k) for k in ['name','key','family','label','received_at','source_url']};row.update(valid=0,first=None,last=None,invalid=0,duplicates=0)
        if doc['ok'] and doc['rows']:
            f=pd.DataFrame(doc['rows']);row['duplicates']=int(f.day.duplicated().sum())
            valid=np.isfinite(f[['open','high','low','close']]).all(axis=1)&(f[['open','high','low','close']]>0).all(axis=1)
            valid &= f.high.ge(f[['open','low','close']].max(axis=1))&f.low.le(f[['open','high','close']].min(axis=1))
            row['invalid']=int((~valid).sum());f=f[valid].sort_values('ts').drop_duplicates('day').set_index('day').sort_index();scope(f.index)
            if len(f):data[doc['name']]=f;row.update(valid=len(f),first=f.index.min(),last=f.index.max())
        row['availability']='Current basket survivorship research-only' if doc['family']=='stock_proxy' else 'Revised historical vendor vintage; actual old receipt time unavailable'
        inventory.append(row)
    return data,inventory
if __name__=='__main__':acquire()
