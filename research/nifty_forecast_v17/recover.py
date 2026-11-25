"""Rate-aware recovery of the predetermined traded history after HTTP 429."""
from concurrent.futures import ThreadPoolExecutor
import time
from urllib.parse import quote
from .common import *
from .acquire import token,API,fetch

FAST={'RELIANCE','ONGC','ITC','HINDUNILVR','MARUTI','M&M','NIFTYBEES','BANKBEES'}


def run():
    stock=pd.read_csv(OUT/'historical-stock-basket.csv')
    p=pd.read_csv(OUT/'stock-identifier-history.csv')
    prior=read('stock-candle-receipt.json')['records']
    counts=pd.DataFrame(prior).groupby('stock').bars.count()
    recovery=[]
    for r in stock.itertuples(index=False):
        valid=int(counts.get(r.stock,0))
        if r.stock not in FAST and valid>=18:
            continue
        minute=5 if r.stock in FAST else 25
        g=p[p.stock.eq(r.stock)]
        variants=[(r.instrument,FIRST,FREEZE)]
        if any(g['isin'].ne(r.isin)):
            variants=[('NSE_EQ|'+q.isin,q.first,q.last) for q in g.itertuples(index=False)
                       if q.rows>=14 and q.isin!=r.isin]
            minute=5
        for key,first,last in variants:
            for start in pd.date_range(pd.Timestamp(first).replace(day=1,month=pd.Timestamp(first).month if minute<=15 else 3*((pd.Timestamp(first).month-1)//3)+1),
                                       last,freq='MS' if minute<=15 else 'QS'):
                a=max(first,start.strftime('%Y-%m-%d'))
                b=min(last,(start+(pd.offsets.MonthEnd() if minute<=15 else pd.offsets.QuarterEnd())).strftime('%Y-%m-%d'))
                recovery.append((0 if minute==5 else 1,r.stock,key,minute,a,b))
    for name,key in [('energy','NSE_INDEX|Nifty Energy'),('broad','NSE_INDEX|Nifty 500')]:
        for d in pd.date_range(FIRST,FREEZE,freq='QS'):
            recovery.append((2,name,key,25,d.strftime('%Y-%m-%d'),min(FREEZE,(d+pd.offsets.QuarterEnd()).strftime('%Y-%m-%d'))))
    recovery=sorted(recovery)
    auth=token()
    def go(x):
        kind,name,key,minute,a,b=x
        if minute==5 and (OUT/'sources/stock-minute'/name/(a+'.json.gz')).exists() and key==stock.set_index('stock').at[name,'instrument']:
            path=OUT/'sources/stock-minute'/name/(a+'.json.gz')
        else:
            path=OUT/'sources'/'retry-minute'/name/f"{key.split('|')[-1]}-{minute}-{a}.json.gz"
        url=API+quote(key,safe='')+f'/minutes/{minute}/{b}/{a}'
        return dict(stock=name,begin=a,end=b,instrument=key,bar_minutes=minute,group='native' if kind==2 else 'recovered',
                    **fetch(url,path,auth,'candles',tries=2))
    out=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,r in enumerate(pool.map(go,recovery),1):
            out.append(r)
            if i%45==0:
                print('Rate-aware recovery',i,'/',len(recovery),flush=True)
    save('stock-recovery-receipt.json',dict(records=out,requested=len(recovery),success=sum(r.get('bars',0)>0 for r in out),
      reason='The original batch hit provider HTTP 429. Selected missing fine feeds were retried after cooldown and additional assets use the documented quarter-length 25-minute endpoint.'))
    print('Recovery returned',sum(r.get('bars',0) for r in out),'bars',flush=True)

if __name__=='__main__':
    run()
