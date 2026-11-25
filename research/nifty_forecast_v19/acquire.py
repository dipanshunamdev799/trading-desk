"""Public exchange archive retrieval with immutable source receipts."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import re
import requests
from .common import *

NSE='https://www.nseindia.in'
ARCH='https://nsearchives.nseindia.com'
SEBI='https://www.sebi.gov.in/curation/fpi.html'
CDSL='https://www.cdslindia.com/Publications/FIITrends.aspx'
NSDL='https://pilot.fpi.nsdl.co.in/Reports/ReportsListing.aspx'
DOCS={
    'delivery_index':NSE+'/all-reports',
    'derivatives_index':NSE+'/all-reports-derivatives',
    'lending_index':NSE+'/all-reports-slb',
    'cash_activity':NSE+'/reports/fii-dii',
    'cash_latest':NSE+'/api/fiidiiTradeReact',
    'official_depository_directory':SEBI,
    'cdsl_archive':CDSL,
    'cdsl_reporting_scope':'https://www.cdslindia.com/publications/fiinote.html',
    'nsdl_directory':NSDL,
    'nsdl_archive':'https://pilot.fpi.nsdl.co.in/Reports/Archive.aspx',
    'nsdl_original_archive':'https://www.fpi.nsdl.co.in/web/Reports/Archive.aspx',
    'nsdl_dii_archive':'https://pilot.fpi.nsdl.co.in/Users/DIIGenerateReport.aspx?Rep=A',
}
ALTERNATIVE={
    'cdsl_fortnight_directory':'https://www.cdslindia.com/Publications/ForeignPortInvestor.html',
    'cdsl_tradewise_directory':'https://www.cdslindia.com/Publications/EquityDataFII.html',
    'amfi_monthly':'https://www.amfiindia.com/research-information/amfi-monthly',
    'cdsl_daily_current':'https://www.cdslindia.com/Publications/FIIDailyData.aspx',
    'cdsl_monthly_current':'https://www.cdslindia.com/Publications/FIIMonthlyData.aspx',
    'nsdl_fortnight_directory':'https://pilot.fpi.nsdl.co.in/Reports/ArchiveSector.aspx',
    'mwpl_filed_example':'https://nsearchives.nseindia.com/content/fo/mpl_nov2026.csv',
    'combined_oi_filed_example':'https://nsearchives.nseindia.com/content/fo/nseoi_17112026.zip',
}

def raw(p):
    return gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()

def grab(url,relative,kind='any',params=None,session=None):
    loc=OUT/relative
    a=dict(url=url,params=params,request_time=now(),file=relative)
    if loc.is_file():
        return a|dict(status=200,sha256=sha(loc),bytes=loc.stat().st_size,cached=True)
    http=requests if session is None else session
    try:
        r=http.get(url,params=params,timeout=(5,11),headers={'User-Agent':'Mozilla/5.0','Accept':'text/csv,text/html,application/json,*/*','Referer':url.rsplit('/',1)[0]+'/'})
        a.update(status=r.status_code,url=r.url,received=now(),server_date=r.headers.get('Date'),content_type=r.headers.get('Content-Type'))
        body=r.content
        if not r.ok or not body:
            return a|dict(file=None)
        if kind=='csv' and body.lstrip().startswith((b'<',b'{"')):
            return a|dict(file=None,reason='response was not an exchange CSV')
        if kind=='json':
            r.json()
        loc.parent.mkdir(parents=True,exist_ok=True)
        tmp=loc.with_suffix(loc.suffix+'.partial')
        tmp.write_bytes(gzip.compress(body,mtime=0,compresslevel=3) if loc.suffix=='.gz' else body)
        tmp.replace(loc)
        return a|dict(sha256=sha(loc),bytes=loc.stat().st_size)
    except (ValueError,requests.RequestException) as ex:
        return a|dict(file=None,error=type(ex).__name__)

def run_jobs(tasks,workers=9):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        result=[]
        for i,a in enumerate(pool.map(lambda r:grab(*r),tasks),1):
            if i%100==0:print('Archived source requests',i,'of',len(tasks),flush=True)
            result.append(a)
    return result

def sessions():
    n=csv('official-index-closes.csv',V11).iloc[:,0].astype(str)
    return pd.Index(n[n.between(FIRST,FREEZE)].drop_duplicates().sort_values(),name='day')

def archive():
    register()
    if (OUT/'source-receipts.json').is_file():
        return
    days=sessions()
    tasks=[]
    for date in days:
        d=pd.Timestamp(date).strftime('%d%m%Y')
        tasks.append((f'{ARCH}/content/nsccl/fao_participant_vol_{d}.csv',f'sources/participant-volume/{date}.csv.gz','csv'))
        if not (V18/'sources/participants'/f'{date}.csv.gz').is_file():
            tasks.append((f'{ARCH}/archives/nsccl/fao_participant_oi_{d}.csv',f'sources/participant-oi-recovery/{date}.csv.gz','csv'))
    # Probe dated individual-security position-limit and borrowing reports through the official routes.
    # Acquire the discovered daily families only when the representative responses are structured data.
    probes=[]
    for d in ('2025-04-15','2025-10-20','2026-06-15','2026-11-17'):
        a=pd.Timestamp(d).strftime('%d%m%Y')
        probes.extend([
            (f'{ARCH}/content/fo/fo_mwpl_{a}.csv',f'sources/probes/mwpl-{d}.csv.gz','csv'),
            (f'{ARCH}/content/fo/fo_secban_{a}.csv',f'sources/probes/ban-{d}.csv.gz','csv'),
            (f'{ARCH}/archives/slbs/bhav/SLB_Bhavcopy_{a}.csv',f'sources/probes/slb-{d}.csv.gz','csv'),
            (f'{ARCH}/content/slbs/SLB_{a}.csv',f'sources/probes/slb-alternative-{d}.csv.gz','csv'),
            (f'{ARCH}/archives/equities/mkt/MA{a[:4]+a[-2:]}.csv',f'sources/probes/cash-market-report-{d}.csv.gz','csv'),
        ])
    docs=[(v,f'sources/probes/{k}.html.gz','any') for k,v in DOCS.items()]
    result=run_jobs(tasks+probes+docs)
    save('source-receipts.json',result)
    print('Retained',sum(r.get('sha256') is not None for r in result),'new public responses',flush=True)

if __name__=='__main__':
    import sys
    if 'alternatives' in sys.argv:
        if not (OUT/'alternate-source-preflight.json').is_file():
            save('alternate-source-preflight.json',run_jobs([(v,f'sources/probes/{k}.gz') for k,v in ALTERNATIVE.items()]))
    else:
        archive()
