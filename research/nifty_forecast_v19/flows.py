"""Alternative official depository and AMFI source acquisition and flow audit."""
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re
from scipy.stats import spearmanr

from .common import *
from .acquire import run_jobs,raw,sessions

CDSL='https://www.cdslindia.com/Publications/ForeignPortInvestor.html'
AMFI='https://www.amfiindia.com/research-information/amfi-monthly'
MONTHS={m.strftime('%b').lower():m.month for m in pd.date_range('2025-01-01','2025-12-01',freq='MS')}

def html(ref):
    return BeautifulSoup(raw(OUT/ref),'html.parser')

def get():
    b=html('sources/probes/cdsl_fortnight_directory.gz')
    a=html('sources/probes/amfi_monthly.gz')
    found={}
    for l in b.find_all('a',href=True):
        link=l['href']; t=' '.join(l.get_text(' ',strip=True).split())
        if 'FORTNIGHTLYSECWISEPAGES' in link.upper():
            tag='cdsl-sector'
        elif re.search(r'/latest_\d{8}\.xls',link,re.I):
            tag='cdsl-daily'
        else:
            continue
        d=pd.to_datetime(t,format='mixed',dayfirst=t[:1].isdigit(),errors='coerce')
        if pd.isna(d):continue
        day=d.date().isoformat()
        if FIRST<=day<=FREEZE:
            found[tag,day]=urljoin(CDSL,link)
    for l in a.find_all('a',href=True):
        link=l['href']
        m=re.search(r'/am([a-z]{3})(20\d{2})repo\.xls$',link,re.I)
        if m and m[1].lower() in MONTHS:
            day=(pd.Timestamp(int(m[2]),MONTHS[m[1].lower()],1)+pd.offsets.MonthEnd()).date().isoformat()
            if FIRST<=day<=FREEZE:
                found['amfi-monthly',day]=urljoin(AMFI,link)
    tasks=[]
    for (s,d),url in sorted(found.items()):
        ext='.html.gz' if s=='cdsl-sector' else '.xls'
        tasks.append((url,f'sources/{s}/{d}{ext}'))
    receipts=run_jobs(tasks,workers=8)
    save('flow-source-receipts.json',receipts)
    print('Retained alternative official flow reports',sum(r.get('file') is not None for r in receipts),'of',len(receipts),flush=True)

def money(x):
    try:return float(str(x).strip().replace(',','').replace('(','-').replace(')',''))
    except ValueError:return np.nan

def sheets(path):
    payload=raw(path)
    if payload.startswith((b'\xd0\xcf\x11\xe0',b'\x09\x08',b'\x09\x04')):
        import xlrd
        book=xlrd.open_workbook(file_contents=payload)
        return [[[xlrd.xldate_as_datetime(v.value,book.datemode).strftime('%d-%b-%Y') if v.ctype==xlrd.XL_CELL_DATE else v.value
                  for v in sheet.row(i)] for i in range(sheet.nrows)] for sheet in book.sheets()]
    if payload.startswith(b'PK'):
        ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        with ZipFile(BytesIO(payload)) as wb:
            common=[]
            if 'xl/sharedStrings.xml' in wb.namelist():
                shared=ET.fromstring(wb.read('xl/sharedStrings.xml'))
                common=[''.join(t.text or '' for t in z.findall('.//x:t',ns)) for z in shared]
            out=[]
            for s in sorted(k for k in wb.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',k)):
                table=[]
                doc=ET.fromstring(wb.read(s))
                for row in doc.findall('.//x:sheetData/x:row',ns):
                    parsed=[]
                    for c in row.findall('x:c',ns):
                        pos=0
                        for q in re.match('[A-Z]+',c.attrib['r'])[0]:pos=pos*26+ord(q)-64
                        val=c.findtext('x:v','',ns)
                        typ=c.get('t')
                        if typ=='s':val=common[int(val)]
                        if typ=='inlineStr':val=''.join(q.text or '' for q in c.findall('.//x:t',ns))
                        parsed.extend(['']*max(0,pos-1-len(parsed)))
                        parsed.append(val)
                    table.append(parsed)
                out.append(table)
            return out
    b=BeautifulSoup(payload,'html.parser')
    return [[[c.get_text(' ',strip=True) for c in r.find_all(['td','th'],recursive=False)] for r in t.find_all('tr')] for t in b.find_all('table')]

def parse_daily(path,day):
    for tbl in sheets(path):
        start=next((i for i,r in enumerate(tbl) if 'gross purchases' in ' '.join(map(str,r)).lower() and
                    'net investment' in ' '.join(map(str,r)).lower()),None)
        if start is None:continue
        last_asset=''
        hits=[]
        title=' '.join(' '.join(map(str,r)) for r in tbl[:start])
        daytag=re.search(r'\d{1,2}[- /](?:[A-Za-z]{3}|\d{1,2})[- /]20\d{2}',title)
        identified=daytag is not None and pd.to_datetime(daytag[0],dayfirst=True).date().isoformat()==day
        for r0 in tbl[start+1:]:
            r=[*r0,'','','','','','','']
            tx=' '.join(map(str,r[:3])).strip()
            if tx.lower().startswith('reporting date'):break
            d=re.search(r'\d{1,2}[- /][A-Za-z]{3}[- /]20\d{2}',tx,re.I)
            if d:
                dt=pd.to_datetime(d[0],dayfirst=True).date().isoformat()
                if dt!=day:break
                identified=True
            asset=next((name for name in ('Equity','Debt','Hybrid') if re.search(r'\b'+name.lower()+r'\b',tx,re.I)),None)
            if asset in ('Debt','Hybrid') and hits:
                break
            if asset:last_asset=asset
            numbers=[money(k) for k in r[3:6]]
            if last_asset=='Equity' and min(r[3:6],key=lambda x:len(str(x)))!='' and np.isfinite(numbers).all():
                route=str(r[2]).strip()
                if route:
                    hits.append(dict(day=day,route=route,gross_purchase_inr_crore=numbers[0],gross_sale_inr_crore=numbers[1],
                                    net_inr_crore=numbers[2],purchase_sell_net_gap=numbers[0]-numbers[1]-numbers[2]))
        if hits and identified:
            routes={t['route'].casefold():t for t in hits}
            if len(hits)!=3 or not {'stock exchange','primary market & others','sub-total'}.issubset(routes):continue
            if any(abs(x['purchase_sell_net_gap'])>.025 for x in hits):continue
            k=('gross_purchase_inr_crore','gross_sale_inr_crore','net_inr_crore')
            if any(abs(routes['stock exchange'][p]+routes['primary market & others'][p]-routes['sub-total'][p])>.025 for p in k):continue
            return hits
    return []

def sector_data(path,day):
    b=BeautifulSoup(raw(path),'html.parser')
    tables=b.find_all('table')
    year=day[:4]
    guard=r'(?:'+pd.Timestamp(day).strftime('%b').lower()+'|'+pd.Timestamp(day).strftime('%B').lower()+r')'
    title=b.get_text(' ',strip=True)[:1500].lower()
    if year not in title or not re.search(r'\b'+guard,title):
        return []
    ans=[]
    for tbl in tables:
        allrows=tbl.find_all('tr')
        arr=[[' '.join(c.get_text(' ',strip=True).split()) for c in item.find_all(['td','th'],recursive=False)] for item in allrows]
        labels=' '.join(' '.join(r) for r in arr[:4]).lower()
        if 'sector' not in labels or not any(x in labels for x in ('crore','cr.','inr','investments','rupees')):
            continue
        span=[]
        for tr in allrows[:3]:
            columns=[]
            for c in tr.find_all(['td','th'],recursive=False):
                columns.extend([c.get_text(' ',strip=True)]*int(c.get('colspan',1)))
            span.append(columns)
        net=[i for i,(p,q,r) in enumerate(zip(*span)) if p.lower().startswith('net investment') and
             'inr' in q.lower() and r.lower()=='equity']
        if len(net)!=2:
            continue
        first,last=net
        if not re.search(r'\b'+guard+r'\b',span[0][last].lower()) or year not in span[0][last]:continue
        for row in arr:
            if len(row)<5:continue
            is_sector=re.fullmatch(r'\d{1,2}\.?',row[0]) is not None
            is_total=any(x.lower() in ('total','grand total') for x in row[:2])
            if not (is_sector or is_total):
                continue
            k=1 if is_sector or not row[0] else 0
            s=row[k] if is_sector else 'Total'
            if len(s)<3 or s.replace('.','').isdigit():continue
            base=k+1
            nums=[money(x) for x in row[base:]]
            if np.isfinite(nums).sum()<3:continue
            if last-2>=len(nums):continue
            prior_years=re.findall(r'20\d{2}',span[0][first])
            prior=nums[first-2] if prior_years and min(prior_years)>='2025' else np.nan
            ans.append(dict(day=day,sector=s,prior_net_equity_inr_crore=prior,net_equity_inr_crore=nums[last-2],
                            reporting_span=span[0][last],headers=' || '.join(' / '.join(r) for r in arr[:4] if r)))
        if ans:return ans
    return []

def amfi_data(path,day):
    out=[]
    per=pd.Timestamp(day)
    for table in sheets(path):
        header=' '.join(' '.join(map(str,r)) for r in table[:4]).casefold()
        if not all(t in header for t in [per.strftime('%B %Y').casefold(),'net inflow','funds mobilized','redemption']):
            continue
        section=''
        for row in table:
            if len(row)<2:continue
            name=' '.join(str(row[1]).casefold().split())
            text0=name
            if not text0:continue
            if str(row[0]).strip()=='II' and re.search(r'equity.*schemes',name):
                section='equity'
            if str(row[0]).strip()=='VI' and 'index funds' in name:
                section='index_funds'
            if str(row[0]).strip()=='VII' and 'exchange traded' in name:
                section='etf'
            if 'close ended schemes' in name or 'close-ended schemes' in name:
                break
            if re.fullmatch(r'sub\s*total\s*[-–]?\s*ii',name) and section=='equity':
                group='open_end_equity'
            elif name in ('equity etf','other etfs','other etf','gold etf','index funds'):
                group={'equity etf':'equity_etf','other etfs':'other_etf','other etf':'other_etf','gold etf':'gold_etf','index funds':'index_funds'}[name]
            elif re.fullmatch(r'sub\s*total\s*[-–]?\s*vi',name) and section=='index_funds':
                group='index_funds'
            else:
                continue
            if group is None:continue
            cells=[money(x) for x in row]
            k=4
            if len(cells)<8 or not np.isfinite(cells[k:k+3]).all() or abs(cells[k]-cells[k+1]-cells[k+2])>.06:
                continue
            out.append(dict(period_end=day,category=group,gross_sales_inr_crore=cells[k],redemptions_inr_crore=cells[k+1],
                           net_inr_crore=cells[k+2],aum_inr_crore=cells[k+3] if len(cells)>k+3 else np.nan,
                           source_row=text0[:120],checks='gross sales less redemptions matches net within 0.06'))
    return pd.DataFrame(out).drop_duplicates(['period_end','category']).to_dict('records') if out else []

def eligible_day(d,kind,days):
    obs=pd.Timestamp(d)
    # A further publication buffer is conservative and a sensitivity. Retrieved archives carry no verified historical first-print timestamp.
    after=obs+pd.Timedelta(days=1 if kind=='daily' else 10 if kind=='fortnight' else 20)
    i=days.searchsorted(after.date().isoformat(),side='left')
    return days[i] if i<len(days) else None

def relation(a,daycol,value,k,days,closes):
    a=a.dropna(subset=[value]).sort_values(daycol).copy()
    a['observed_flow']=a[value].astype(float)
    a['eligible_day']=a[daycol].map(lambda d:eligible_day(d,k,days))
    results=[]
    for h in HORIZONS:
        pos=days.get_indexer(a.eligible_day)
        live=(pos>5)&(pos+h-1<len(days))
        b=a.loc[live,['eligible_day','observed_flow']].copy()
        i=pos[live]
        ar=np.log(closes.to_numpy())
        future=ar[i+h-1]-ar[i-1]
        past=ar[i-1]-ar[i-6]
        vol=np.array([np.sqrt(252*np.mean(np.diff(ar[j-1:j+h])**2)) for j in i])
        for endpoint,values in [('future_return',future),('future_realized_vol',vol),('trailing_return',past),('lag_net',b.observed_flow.shift().to_numpy())]:
            joint=np.isfinite(values)
            z=b.observed_flow.to_numpy()[joint]
            w=values[joint]
            r=spearmanr(z,w).statistic if len(w)>5 and np.std(z)>0 and np.std(w)>0 else np.nan
            results.append(dict(series=k,horizon=h,test=endpoint,n=len(w),spearman=r,status='descriptive paired release-vintage association'))
    return results

def main():
    if not (OUT/'flow-source-receipts.json').exists():
        get()
    kinds={'cdsl-sector':sector_data,'cdsl-daily':parse_daily,'amfi-monthly':amfi_data}
    out={k:[] for k in kinds}
    audit=[]
    for r in read('flow-source-receipts.json'):
        p=OUT/r['file'] if r.get('file') else None
        k=next((k for k in kinds if '/'+k+'/' in r.get('file','')),None) if p else None
        if k is None:continue
        d=p.name[:10]
        try:
            ans=kinds[k](p,d)
            for row in ans:row.update(file=r['file'])
            out[k].extend(ans)
            audit.append(dict(type=k,day=d,file=r['file'],rows=len(ans),error=None))
        except (ValueError,IndexError,TypeError,KeyError,ImportError,OSError) as e:
            audit.append(dict(type=k,day=d,file=r['file'],rows=0,error=str(e)))
    a={k:pd.DataFrame(v) for k,v in out.items()}
    days=sessions()
    closes=csv('official-index-closes.csv',V11).set_index('Unnamed: 0').nifty50.reindex(days)
    cases=[]
    daily=a['cdsl-daily']
    if len(daily):
        for category,q in daily.groupby('route'):
            res=relation(q.drop_duplicates('day'),'day','net_inr_crore','daily',days,closes)
            cases+=[x|{'category':category} for x in res]
    am=a['amfi-monthly']
    if len(am):
        for tag,x in am.groupby('category'):
            result=relation(x,'period_end','net_inr_crore','monthly',days,closes)
            for item in result:item['category']=tag
            cases+=result
    fpi=a['cdsl-sector']
    if len(fpi):
        sectors=fpi[fpi.sector.ne('Total')]
        national=sectors.groupby('day',as_index=False).agg(net_equity_inr_crore=('net_equity_inr_crore','sum'))
        fpi_total=fpi[fpi.sector.eq('Total')][['day','net_equity_inr_crore']].rename(columns={'net_equity_inr_crore':'published_total'})
        check=national.merge(fpi_total,on='day',how='left')
        check['published_total_diff']=check.net_equity_inr_crore-check.published_total
        write('cdsl-sector-reconciliation.csv',check)
        for tag,x in [('sector_sum',national),*list(sectors.groupby('sector'))]:
            cases += [z|{'category':tag} for z in relation(x,'day','net_equity_inr_crore','fortnight',days,closes)]
    for k,v in a.items():
        if v.empty:v=pd.DataFrame(columns=['day','file'])
        write(k+'-observations.csv.gz',v)
    write('flow-parsing-audit.csv',pd.DataFrame(audit))
    write('capital-flow-associations.csv',pd.DataFrame(cases,columns=['series','category','horizon','test','n','spearman','status']))
    save('capital-flow-receipt.json',dict(audited_at=now(),archive_history={k:{'rows':len(d),
        'dates':int(d['day' if 'day' in d else 'period_end'].nunique()) if len(d) else 0} for k,d in a.items()},
        daily='Custodian-reported CDSL equity series, separate from NSE/BSE/MSEI daily cash market provisional FII/DII. Trading date and reporting date may differ.',
        amfi='Actual fund unit gross sales less redemptions, in INR crore. Includes AMFI-defined schemes. AUM is a separate numerator and equity trading is not directly measured.',
        sector='Dated custody sector equity, INR crore. Uses the second net investment group, INR column, listed equity, with dates checked in official header. AUC and prior net are distinct.',
        flows_blocker='No complete dated daily NSE exchange provisional FII/DII cash pair or matched daily ETF creation-redemption series on audited official routes.',
        timing='No historical first-publication receipt. Standalone descriptive screens use first cash session after 1 day for daily custody, 10 for fortnightly equity and 20 days after end of AMFI period. Excluded from the primary forecasting panel.'))
    print('Alternative source audited',[(k,len(v)) for k,v in a.items()],flush=True)

if __name__=='__main__':
    main()

