"""Recover official release vintages and test documented public/archive routes."""
from urllib.parse import urljoin,urlencode
import re
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from .common import *
from research.nifty_forecast_v19 import acquire as public
from research.nifty_forecast_v16.acquire import token

BLS='https://www.bls.gov/bls/news-release/cpi.htm'
FED='https://fraser.stlouisfed.org/files/docs/publications/bls/newsreleases/cpi/'
ROUTES={
 'bls_archive':BLS,
 'bls_calendar_mirror':'https://blsmon1.bls.gov/schedule/news_release/cpi.htm',
 'nse_index_reviews':'https://www.niftyindices.com/press-release',
 'cdsl_modern_daily':'https://www.cdslindia.com/eservices/publications/fiidaily',
 'sebi_equity_sources':'https://www.sebi.gov.in/curation/equity_cash_market.html',
 'nseix_reports':'https://www.nseix.com/markets/reports',
 'sebi_fpi_sources':'https://www.sebi.gov.in/curation/fpi.html',
 'nse_rebalance_rules':'https://www.niftyindices.com/resources/index-rebalancing-schedule',
}
REVIEW={
 '2025-02-21':'https://www.niftyindices.com/Press_Release/ind_prs21022025.pdf',
 '2025-08-22':'https://niftyindices.com/Press_Release/ind_prs22082025.pdf',
 '2026-02-20':'https://www.niftyindices.com/Press_Release/ind_prs23022026.pdf',
 '2026-08-10':'https://www.niftyindices.com/Press_Release/ind_prs10082026.pdf',
}
# The normal calendar does not supply first prints. These observed BLS release days select original PDFs in the FRASER archive.
# Period identity and the actual 08:30 embargo must both match the document header.
DATES=['2025-02-12','2025-03-12','2025-04-10','2025-05-13','2025-06-11','2025-07-15','2025-08-12','2025-09-11',
       '2025-10-24','2025-12-18','2026-01-13','2026-02-13','2026-03-11','2026-04-10','2026-05-12','2026-06-10',
       '2026-07-14','2026-08-12','2026-09-11','2026-10-14','2026-11-10']

def macro_index(doc):
    candidates={}
    if doc.get('file'):
        s=public.raw(OUT/doc['file']).decode('utf8',errors='replace')
        for href in re.findall(r'href=["\x27]([^"\x27]*cpi_\d{8}\.pdf)["\x27]',s,re.I):
            m=re.search(r'cpi_(\d{8})',href).group(1)
            d=pd.to_datetime(m,format='%m%d%Y').date().isoformat()
            if '2025-02-01'<=d<=FREEZE:candidates[d]=urljoin(BLS,href)
    return candidates

def pdf_text(path,n=2):
    if not path.read_bytes().startswith(b'%PDF'):return ''
    r=PdfReader(path)
    return ' '.join(' '.join(p.extract_text().split()) for p in r.pages[:n])

def parse_macro(r):
    if not r.get('file'):return None
    d=r['file'].split('/')[-1][:10]
    x=pdf_text(OUT/r['file'],1)
    y=re.search(r'CONSUMER PRICE INDEX\s*[-–—]\s*([A-Z]+ 20\d{2})',x,re.I)
    if not y or not re.search(r'8:30\s*a\.?m\.?',x,re.I):return None
    date=pd.Timestamp(d)
    # Embedded publication date prevents attributing a nearby scheduled date to a report.
    hdr=x[:y.start()+20]
    textual=rf"{date.strftime('%B')}\s+{date.day:02d}?,?\s+{date.year}" if date.day<10 else rf"{date.strftime('%B')}\s+{date.day},?\s+{date.year}"
    if not (re.search(textual,hdr,re.I) or re.search(rf"{date.strftime('%B')}\s+0?{date.day},?\s+{date.year}",hdr,re.I)):
        return None
    month=pd.to_datetime(y.group(1),format='%B %Y').strftime('%Y-%m')
    if not '2025-01'<=month<=FREEZE[:7]:
        return None
    s=re.search(r'All Urban Consumers\s*\(CPI-U\)\s*(rose|increased|fell|declined|decreased|was unchanged)\s*(\d+(?:\.\d+)?)?',x,re.I)
    if not s:return None
    v=0. if 'unchanged' in s[1].lower() else float(s[2])*(-1 if s[1].lower() in ('fell','declined','decreased') else 1)
    time=pd.Timestamp(d+' 08:30',tz='America/New_York').tz_convert(IST)
    return dict(release=d,eligible=(time+pd.Timedelta(minutes=10)).isoformat(),observed_month=month,mom_first=v,
                file=r['file'],sha256=r['sha256'],source=r['url'])

def scoped_reviews(entries):
    out=[]
    for r in entries:
        if not r.get('file'):continue
        path=OUT/r['file']
        x=pdf_text(path,3)
        if 'Index Maintenance' not in x:continue
        pub=re.search(r'Mumbai,\s*([A-Za-z]+ \d{1,2}, 20\d{2})',x)
        eff=re.search(r'effective from ([A-Za-z]+ \d{1,2}, 20\d{2})',x,re.I)
        if not (pub and eff):continue
        a,b=[pd.Timestamp(z[1]).date().isoformat() for z in (pub,eff)]
        if not FIRST<=a<=b<=FREEZE:continue
        out.append(dict(published_date=a,effective_date=b,index_mention='Nifty 50' in x,
             membership_notice='published additions and deletions, no daily full index weights',file=r['file'],sha256=r['sha256'],source=r['url']))
    return out

def cdsl_monthly():
    """Extract distinct current-month equity reports only through the historical freeze."""
    public.OUT=OUT
    f='cdsl-modern-monthly-probe.json'
    if (OUT/f).exists():
        meta=read(f)
    else:
        old=next(r for r in read('source-discovery-receipt.json')['archive_probes'] if 'cdsl_modern' in str(r.get('file')))
        landing=BeautifulSoup(public.raw(OUT/old['file']),'html.parser')
        link=next(a for a in landing.find_all('a',href=True) if a.get_text(' ',strip=True)=='FII Monthly Data')
        meta=public.grab(urljoin(old['url'],link['href']),'sources/probes/cdsl_modern_monthly.html.gz')
        save(f,meta)
    fields=['day','route','purchase_inr_crore','sale_inr_crore','net_inr_crore','dataset','source']
    rows=[]
    if meta.get('file'):
        doc=BeautifulSoup(public.raw(OUT/meta['file']),'html.parser')
        table=next(t for t in doc.find_all('table') if 'Investment Route' in t.get_text(' ',strip=True)[:260])
        day=''
        equity=False
        for tr in table.find_all('tr'):
            vals=[z.get_text(' ',strip=True) for z in tr.find_all(['td','th'],recursive=False)]
            if len(vals)<4:continue
            if re.fullmatch(r'\d\d-[A-Z]{3}-20\d\d',vals[0]):
                day=pd.to_datetime(vals.pop(0),format='%d-%b-%Y').date().isoformat()
            if not FIRST<=day<=FREEZE:continue
            if vals[0]=='Equity':
                vals.pop(0)
                equity=True
            if not equity or vals[0] not in ('Stock Exchange','Primary market & others','Sub-total'):continue
            buy,sell,net=map(float,vals[1:4])
            assert abs(buy-sell-net)<.021
            rows.append(dict(zip(fields,[day,vals[0],buy,sell,net,'custodian reporting vintage, equity segment',meta['url']])))
            if vals[0]=='Sub-total':equity=False
    d=pd.DataFrame(rows,columns=fields)
    assert not d.duplicated(['day','route']).any()
    old=csv('cdsl-daily-observations.csv.gz',V19)
    known=set(old.day)
    d['new_relative_to_v19']=~d.day.isin(known)
    write('cdsl-extended-daily.csv',d)
    x=d[d.route.eq('Stock Exchange')].merge(csv('multi-horizon-targets.csv'),left_on='day',right_on='origin',how='left')
    audit=[]
    for h in HORIZONS:
        s=x[['net_inr_crore','return_0_'+str(h)]].dropna()
        audit.append(dict(horizon=h,n_completed=len(s),scope='Descriptive on the dated reports; same report date is never used before the next cash session.',
          spearman=s.corr(method='spearman').iloc[0,1] if len(s)>=6 else np.nan))
    write('cdsl-extended-release-associations.csv',pd.DataFrame(audit))
    save('cdsl-extension-receipt.json',dict(rows=len(d),dates=int(d.day.nunique()),new_dates=int(d.loc[d.new_relative_to_v19,'day'].nunique()),
          last=d.day.max() if len(d) else None,source=meta,classification='CDSL daily confirmed custodian equity, not an exchange daily FII/DII cash pair. Original historical first-post timestamp unavailable.'))
    print('CDSL dated addendum',len(d),'equity rows,',d.day.nunique(),'dates',flush=True)

def main():
    public.OUT=OUT
    titles=public.run_jobs([(url,f'sources/probes/{k}.html.gz') for k,url in ROUTES.items()],8)
    ix=next(r for r in titles if r['url']==BLS or 'bls_archive' in str(r.get('file')))
    by=macro_index(ix)
    dates=sorted(set(DATES)|by.keys())
    jobs=[]
    for d in dates:
        url=FED+'cpi_'+d.replace('-','')+'.pdf'
        jobs.append((url,'sources/macro/'+d+'-fraser.pdf'))
    initial=public.run_jobs(jobs,6)
    first=[]
    for r in initial:
        p=parse_macro(r)
        if p:first.append(p)
    remaining=set(dates)-{r['release'] for r in first}
    alternate=[]
    for d in sorted(remaining):
        # A different issuing archive hostname and PDF format from V18's unsuccessful HTML route.
        if d in by:
            alternate.append((by[d],f'sources/macro/{d}-bls.pdf'))
        elif d in DATES:
            alternate.append(('https://blsmon1.bls.gov/news.release/archives/cpi_'+pd.Timestamp(d).strftime('%m%d%Y')+'.pdf',f'sources/macro/{d}-bls.pdf'))
    second=public.run_jobs(alternate,6)
    for r in second:
        p=parse_macro(r)
        if p:first.append(p)
    rev=public.run_jobs([(url,f'sources/membership/{d}.pdf') for d,url in REVIEW.items()],4)
    review=scoped_reviews(rev)
    broker=[]
    edition=read('source-attempts.json',V16)
    g=edition.get('gift_key')
    with requests.Session() as sess:
        sess.headers['Authorization']='Bearer '+token()
        for label,key in [('nifty_cash','NSE_INDEX|Nifty 50'),('gift_offshore',g)]:
            if not key:continue
            url='https://api.upstox.com/v2/expired-instruments/expiries?'+urlencode({'instrument_key':key})
            broker.append(public.grab(url,f'sources/contracts/{label}-expiries.json.gz','json',session=sess))
    write('first-release-cpi.csv',pd.DataFrame(first,columns=['release','eligible','observed_month','mom_first','file','sha256','source']))
    write('nifty-membership-notices.csv',pd.DataFrame(review,columns=['published_date','effective_date','index_mention','membership_notice','file','sha256','source']))
    z=csv('nifty-futures.csv.gz',V19,usecols=['day','id','listed_expiry','actual_expiry','lot'])
    ids=z.groupby(['id','listed_expiry','actual_expiry','lot'],as_index=False).agg(first_seen=('day','min'),last_seen=('day','max'),sessions=('day','nunique'))
    write('futures-contract-identity-inventory.csv',ids)
    save('source-discovery-receipt.json',dict(archive_probes=titles,cpi_attempts=initial+second,official_membership=rev,broker=broker,
      recovered=dict(first_release_cpi=len(first),membership_notices=len(review),verified_domestic_contract_lot_states=len(ids)),
      custody='New CDSL eServices route inspected independently of the V19 form and directory tests. Exact daily exchange FII/DII, daily ETF creations, consensus and historical full constituent weights require dated archive evidence.',
      macro='Dated BLS PDF first release, archived by the Federal Reserve or same official BLS file. Check publication header, month, date and valid window. Ten minutes added to publication, never use months in 2024.',
      sample='Published membership notices identify changes from a specific effective date. They cannot supply a complete daily historical portfolio without auditable initial membership and all intervening revisions.'))
    print('Additional source audit',len(first),'CPI first prints,',len(review),'membership notices,',len(ids),'contract/lot states',flush=True)

if __name__=='__main__':
    import sys
    if '--cdsl' in sys.argv:
        cdsl_monthly()
    else:
        main()

