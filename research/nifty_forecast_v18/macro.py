"""Harvest first-release CPI observations from the issuing agency's dated archive."""
import html
import re
from urllib.parse import urljoin
from .common import *
from .sources import grab,jobs,unpack

LANDING='https://www.bls.gov/bls/news-release/cpi.htm'

def run():
    index=grab(LANDING,'sources/macro/bls-archive.html.gz')
    tasks=[]
    if index.get('file'):
        page=unpack(OUT/index['file']).decode('utf8',errors='replace')
        items=set(re.findall(r'href=["\x27]([^"\x27]+/cpi_\d{8}\.htm)["\x27]',page,re.I))
        for item in sorted(items):
            date=pd.to_datetime(re.search(r'cpi_(\d{8})',item).group(1),format='%m%d%Y',errors='coerce')
            if pd.isna(date) or not '2025-03-01'<=date.strftime('%Y-%m-%d')<=FREEZE:continue
            tasks.append((urljoin(LANDING,item),f'sources/macro/cpi-{date:%Y-%m-%d}.html.gz',None))
    if not tasks:
        tasks=[('https://www.bls.gov/news.release/archives/cpi_02132026.htm','sources/macro/cpi-2026-02-13.html.gz',None)]
    receipts=list(jobs(tasks,5))
    rows=[]
    for r in receipts:
        if not r.get('file'):continue
        p=OUT/r['file'];date=p.name[4:14]
        raw=unpack(p).decode('utf-8',errors='replace')
        t=' '.join(html.unescape(re.sub('<[^>]+>',' ',raw)).split())
        ref=re.search(r'CONSUMER PRICE INDEX\s*[-–]\s*([A-Z]+ 20\d{2})',t,re.I)
        header=re.search(r'embargoed until.{0,120}?(?:8:30 a\.m|08:30)',t,re.I)
        if not ref or not header:continue
        month=pd.to_datetime(ref.group(1),format='%B %Y').strftime('%Y-%m')
        if month<'2025-02':continue
        a=re.search(r'All Urban Consumers\s*\(CPI-U\)\s*(rose|increased|fell|declined|decreased)\s*(\d+(?:\.\d+)?)\s+percent',t,re.I)
        if a:
            v=float(a.group(2))*(-1 if a.group(1).lower() in ('fell','declined','decreased') else 1)
        elif re.search(r'All Urban Consumers\s*\(CPI-U\)\s*was unchanged',t,re.I):
            v=0.
        else:continue
        publication=pd.Timestamp(date+' 08:30:00',tz='America/New_York').tz_convert(IST)
        rows.append(dict(released=date,eligible=(publication+pd.Timedelta(minutes=RELEASE_DELAY)).tz_localize(None).isoformat(sep=' '),
                         observation_month=month,first_release_mom_pct=v,file=r['file'],url=r['url']))
    z=pd.DataFrame(rows,columns=['released','eligible','observation_month','first_release_mom_pct','file','url'])
    write('macro-release-vintages.csv',z)
    save('macro-release-receipt.json',dict(index=index,attempts=receipts,usable=len(z),
         rule='Actual dated archive release and official 08:30 ET publication header. Current-month first reported percent, no 2024 observations and no revised monthly history.'))
    print('BLS first-release CPI observations',len(z),flush=True)

if __name__=='__main__':
    run()
