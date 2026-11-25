"""Use the publication clock, reporting contexts and original facts in NSE integrated results."""
from itertools import chain
import math
import re
import sqlite3
from urllib.parse import urlencode,urlsplit,urlunsplit
import xml.etree.ElementTree as ET
from .common import *
from .inventory import one_day,time_value,sector
from .sources import NSE,grab,jobs,unpack

FIN=NSE+'/api/integrated-filing-results'
BOARD=NSE+'/api/corporate-board-meetings'
FACTS={
 'revenue':('RevenueFromOperations','RevenueFromOperationsGross','RevenueFromOperationsNet','NetSalesIncomeFromOperations','TotalRevenueFromOperations','IncomeFromOperations'),
 'total_income':('TotalIncome','TotalIncomeFromOperations','TotalIncomeNetOfExciseDuty','Income'),
 'interest_income':('InterestEarned','TotalInterestEarned','InterestIncome'),
 'profit_owners':('ProfitLossAttributableToOwnersOfParent','ProfitLossForPeriodAttributableToOwnersOfParent','ProfitLossAttributableToEquityHoldersOfParent'),
 'profit':('ProfitLossForPeriod','ProfitLossForThePeriod','ProfitLoss','NetProfitLossForPeriod','NetProfitLossForThePeriod','ProfitLossFromContinuingOperations','NetProfitLossForThePeriodFromContinuingOperations'),
 'pre_tax':('ProfitLossBeforeTax','TotalProfitBeforeTax','ProfitBeforeTax'),
 'operating_profit':('OperatingProfit','OperatingProfitLoss','ProfitLossFromOperations','OperatingProfitBeforeProvisionsAndContingencies'),
 'eps':('BasicEarningsLossPerShareFromContinuingOperations','BasicEarningsLossPerShare','BasicEarningsPerShare','BasicEPS'),
 'debt':('Borrowings','TotalBorrowings','BorrowingsDebt'),
 'debt_current':('CurrentBorrowings','BorrowingsCurrent'),
 'debt_noncurrent':('NoncurrentBorrowings','BorrowingsNoncurrent'),
 'cash':('CashAndCashEquivalents','CashAndCashEquivalentsAtEndOfPeriod'),
 'assets':('Assets','TotalAssets'),
 'op_cash':('NetCashFlowsFromUsedInOperatingActivities','CashFlowsFromUsedInOperatingActivities','NetCashGeneratedFromOperatingActivities'),
 'capex':('PurchaseOfPropertyPlantAndEquipment','PaymentsToAcquirePropertyPlantAndEquipment','PaymentsForPurchaseOfPropertyPlantAndEquipment'),
 'finance_cost':('FinanceCosts','InterestExpended','FinanceCost'),
}
INSTANT={'debt','debt_current','debt_noncurrent','cash','assets'}
FLOW={'op_cash','capex'}

def canonical(s):
    p=urlsplit(str(s))
    if p.scheme=='https' and p.netloc in ('nsearchives.nseindia.in','nsearchives.nseindia.com','archives.nseindia.com') and p.path.startswith('/corporate/'):
        return urlunsplit((p.scheme,'nsearchives.nseindia.com',p.path,p.query,''))
    return None

def naive(ts):
    return pd.Timestamp(ts).isoformat(sep=' ')

def midnight_options(v):
    x=time_value(v)
    if x is not None:return pd.Timestamp(x)
    d=one_day(str(v or ''))
    return pd.Timestamp(d)+pd.Timedelta(days=1) if d else pd.NaT

def listings():
    all_symbols=csv('issuer-seed.csv').stock.tolist()
    seed=set(all_symbols)
    symbols=all_symbols[:160]
    req=[]
    for s in symbols:
        u=FIN+'?'+urlencode(dict(index='equities',symbol=s,from_date='01-01-2025',to_date='17-11-2026'))
        req.append((u,f'sources/financial-index/{s}.json.gz','json'))
    for m in pd.date_range(FIRST,FREEZE,freq='QS'):
        end=min(m+pd.offsets.QuarterEnd(),pd.Timestamp(FREEZE))
        u=BOARD+'?'+urlencode(dict(index='equities',from_date=m.strftime('%d-%m-%Y'),to_date=end.strftime('%d-%m-%Y')))
        req.append((u,f'sources/board-notices/{m:%Y-%m}.json.gz','json'))
    fetched=list(jobs(req,8))
    # The listing defaults to twenty rows. Recover calendar-year windows for
    # truncated issuers and verify coverage again before selecting documents.
    gaps=[]
    for rec in fetched:
        if not rec.get('file'):continue
        p=OUT/rec['file']
        if p.parent.name!='financial-index':continue
        j=json.loads(unpack(p))
        if isinstance(j,dict) and j.get('totalCount',0)>len(j.get('data',[])):
            gaps.append(p.name.split('.json')[0])
    additional=[]
    for symbol in gaps:
        for a,b,tag in [('01-01-2025','31-12-2025','2025'),('01-01-2026','17-11-2026','2026')]:
            u=FIN+'?'+urlencode(dict(index='equities',symbol=symbol,from_date=a,to_date=b))
            additional.append((u,f'sources/financial-recovery/{symbol}/{tag}.json.gz','json'))
    recovery=list(jobs(additional,10))
    extra=[]
    for rec in recovery:
        if not rec.get('file'):continue
        p=OUT/rec['file']
        j=json.loads(unpack(p))
        if not isinstance(j,dict) or j.get('totalCount',0)<=len(j.get('data',[])):
            continue
        symbol=p.parent.name
        yr=int(p.name[:4])
        for m in pd.date_range(f'{yr}-01-01',min(f'{yr}-12-31',FREEZE),freq='QS'):
            a=m.strftime('%d-%m-%Y')
            b=min(m+pd.offsets.QuarterEnd(),pd.Timestamp(FREEZE)).strftime('%d-%m-%Y')
            u=FIN+'?'+urlencode(dict(index='equities',symbol=symbol,from_date=a,to_date=b))
            extra.append((u,f'sources/financial-recovery/{symbol}/{m:%Y-%m}.json.gz','json'))
    fetched+=recovery+list(jobs(extra,10))
    files=[];calendar=[];quality=[]
    for x in fetched:
        if not x.get('file'):continue
        p=OUT/x['file']; ix=json.loads(unpack(p))
        if p.parent.name=='financial-index' or p.parent.parent.name=='financial-recovery':
            data=ix.get('data',[]) if isinstance(ix,dict) else ix
            total=ix.get('totalCount',len(data)) if isinstance(ix,dict) else len(data)
            symbol=p.name.split('.json')[0] if p.parent.name=='financial-index' else p.parent.name
            quality.append(dict(stock=symbol,source=x['file'],returned=len(data),claimed_total=total,exact_symbol=sum(r.get('symbol')==symbol for r in data)))
            for r in data:
                if r.get('symbol')!=symbol:continue
                q=one_day(r.get('qe_Date'))
                broadcast=time_value(r.get('broadcast_Date')); release=time_value(r.get('creation_Date'))
                original=str(r.get('type_Sub') or '').strip().lower()=='original'
                rev=midnight_options(r.get('revised_Date')) if r.get('revised_Date') else pd.NaT
                xml=canonical(r.get('xbrl')); html=canonical(r.get('ixbrl'))
                if not q or not (FIRST<=q<=FREEZE) or release is None or (broadcast and release<broadcast):continue
                # Where the exchange replaced the listed document, it may only be seen at the later update.
                available=max(pd.Timestamp(release),rev) if pd.notna(rev) else pd.Timestamp(release)
                if available.strftime('%Y-%m-%d')>FREEZE or (not original and pd.isna(rev) and not r.get('type_Sub')):continue
                if not any((xml,html)):continue
                files.append(dict(symbol=symbol,quarter_end=q,company=r.get('cmName'),basis=r.get('consolidated'),
                     release=naive(available),eligible=naive(available+pd.Timedelta(minutes=RELEASE_DELAY)),listed_release=naive(release),
                     broadcast=naive(broadcast) if broadcast else None,sequence=r.get('seq_Id'),revised=int(not original or pd.notna(rev)),
                     revision_note=r.get('revision_Remark'),revision_time=naive(rev) if pd.notna(rev) else None,
                     source_index=x['file'],xbrl=xml,ixbrl=html,public_pdf=r.get('pdf_attach')))
        else:
            for r in ix if isinstance(ix,list) else ix.get('data',[]):
                symbol=r.get('bm_symbol'); release=time_value(r.get('sysTime')); filed=time_value(r.get('bm_timestamp'))
                scheduled=one_day(r.get('proposedMeetingDate') or r.get('bm_date'))
                if symbol not in seed or release is None or (filed and release<filed) or not scheduled:continue
                if not FIRST<=release.date().isoformat()<=FREEZE or not FIRST<=scheduled<=LAST:continue
                detail=' '.join(str(r.get(k) or '') for k in ('bm_desc','bm_purpose'))
                if not re.search(r'earnings|financial results|quarterly results',detail,re.I):continue
                if release.date().isoformat()>scheduled:continue
                prior=one_day(r.get('oriiginalMeetingDate'))
                calendar.append(dict(symbol=symbol,isin=r.get('sm_isin'),public_by=naive(pd.Timestamp(release)+pd.Timedelta(minutes=RELEASE_DELAY)),
                     scheduled=scheduled,prior_scheduled=prior,revision=int(bool(prior and prior!=scheduled)),
                     cancelled=int(bool(re.search(r'cancell?ed',detail,re.I))),source=x['file'],company=r.get('sm_name')))
    u=pd.DataFrame(files).sort_values(['symbol','quarter_end','eligible','sequence']).drop_duplicates(['symbol','quarter_end','xbrl','ixbrl'],keep='first')
    write('structured-results-listing.csv.gz',u)
    write('structured-listing-coverage.csv',pd.DataFrame(quality))
    if calendar:
        k=pd.DataFrame(calendar).sort_values('public_by').drop_duplicates(['symbol','scheduled','revision','cancelled','prior_scheduled'])
    else:
        k=pd.DataFrame(columns=['symbol','scheduled','prior_scheduled','revision','cancelled','public_by','source'])
    write('scheduled-board-results.csv.gz',k)
    save('financial-listing-receipt.json',fetched)
    # First report per issuer, period and legal basis plus the first identified amendment.
    z=u.assign(is_consolidated=u.basis.fillna('').eq('Consolidated').astype(int))
    z=z.sort_values(['revised','quarter_end','is_consolidated','symbol','eligible'],ascending=[True,True,False,True,True])
    z=z.drop_duplicates(['symbol','quarter_end','basis','revised'],keep='first')
    # Keep every issuer-period first, while giving the planned consolidated basis priority within a period.
    z['preference']=z.groupby(['symbol','quarter_end','revised']).cumcount()
    z=z.sort_values(['revised','preference','quarter_end','symbol']).head(1280)
    write('structured-documents-planned.csv.gz',z.drop(columns=['is_consolidated','preference']))
    print('Structured filing inventory',len(u),'rows,',len(z),'documents and',len(k),'published earnings notices',flush=True)
    return z

def local(t):
    return t.rsplit('}',1)[-1].rsplit(':',1)[-1]

def facts(payload,r):
    root=ET.fromstring(payload)
    contexts={};units={}
    for e in root.iter():
        k=local(e.tag)
        if k=='context':
            v={local(a.tag):a.text.strip() for a in e.iter() if local(a.tag) in ('startDate','endDate','instant') and a.text}
            dim=[(str(a.attrib.get('dimension','')),str(a.text or '')) for a in e.iter() if local(a.tag) in ('explicitMember','typedMember')]
            if any(not re.search(r'consolidat|standalone',x+' '+y,re.I) for x,y in dim):continue
            if 'Consolidated'==r.basis and any('standalone' in y.lower() for _,y in dim):continue
            if 'Non-Consolidated'==r.basis and any('consolidated' in y.lower() and 'non' not in y.lower() for _,y in dim):continue
            start=v.get('startDate');end=v.get('endDate') or v.get('instant')
            # Parse the exact dated financial observation supplied by the issuer, excluding all pre-2025 contexts.
            if end!=r.quarter_end or not FIRST<=end<=FREEZE or (start and start<FIRST):continue
            length=(pd.Timestamp(end)-pd.Timestamp(start)).days+1 if start else 0
            if 0<=length<=366:
                contexts[e.get('id')]=(start,end,length,len(dim))
        elif k=='unit':
            units[e.get('id')]=' '.join(str(a.text or '').strip() for a in e.iter() if local(a.tag)=='measure')
    rev={key.lower():(name,j) for name,keys in FACTS.items() for j,key in enumerate(keys)}
    accepted={}
    for e in root.iter():
        tag=e.get('name',local(e.tag)); tag=local(tag)
        q=rev.get(tag.lower()); c=contexts.get(e.get('contextRef'))
        if not q or not c:continue
        metric,priority=q
        duration=c[2]
        if (metric in INSTANT and duration!=0) or (metric in FLOW and duration<65) or (metric not in INSTANT|FLOW and not 65<=duration<=105):continue
        unit=units.get(e.get('unitRef'),'')
        if metric!='eps' and 'INR' not in unit.upper():continue
        if metric=='eps' and unit and 'INR' not in unit.upper() and 'PURE' not in unit.upper():continue
        try:
            v=float(''.join(e.itertext()).strip().replace(',',''))
            if e.get('sign')=='-':v=-abs(v)
            if e.get('scale'):v*=10.**int(e.get('scale'))
        except (ValueError,OverflowError):continue
        if not math.isfinite(v):continue
        accepted.setdefault(metric,[]).append((priority,c[3],duration,dict(metric=metric,value=v,unit=unit,tag=tag,
                       context=e.get('contextRef'),period_start=c[0],period_end=c[1],duration=duration)))
    out=[]
    for group in accepted.values():
        a=sorted(group,key=lambda x:x[:3]); x=a[0]
        if len([j for j in a if j[:3]==x[:3] and abs(j[3]['value']-x[3]['value'])>max(1.e-8,1.e-8*abs(x[3]['value']))]):
            continue
        out.append(x[3])
    return out

def comparable(d):
    rows=[]
    for (symbol,basis),f in d.groupby(['symbol','basis'],dropna=False):
        state={}
        for r in f.sort_values(['eligible','quarter_end','sequence']).itertuples(index=False):
            current=pd.Timestamp(r.quarter_end)
            last_key=(current-pd.offsets.QuarterEnd()).strftime('%Y-%m-%d')
            year_key=(current-pd.DateOffset(years=1)+pd.offsets.QuarterEnd(0)).strftime('%Y-%m-%d')
            p=state.get(last_key); yr=state.get(year_key)
            if p is not None and p['eligible']>=r.eligible:p=None
            if yr is not None and yr['eligible']>=r.eligible:yr=None
            profit=r.profit_owners if pd.notna(r.profit_owners) else r.profit
            profit_tag='owner' if pd.notna(r.profit_owners) else 'total'
            sales=r.revenue if pd.notna(r.revenue) else r.total_income if pd.notna(r.total_income) else r.interest_income
            kind='revenue' if pd.notna(r.revenue) else 'total_income' if pd.notna(r.total_income) else 'interest_income'
            margin=profit/sales if pd.notna(sales) and sales>0 and pd.notna(profit) else np.nan
            op_margin=r.operating_profit/sales if pd.notna(sales) and sales>0 and pd.notna(r.operating_profit) else np.nan
            def change(x,y):
                if pd.isna(x) or pd.isna(y) or y==0:return np.nan
                return float(np.clip((x-y)/max(abs(y),.12*abs(x)), -2.,2.))
            qoq=change(sales,p['sales']) if p and p['kind']==kind else np.nan
            yoy=change(sales,yr['sales']) if yr and yr['kind']==kind else np.nan
            earnings=change(profit,p['profit']) if p and p['profit_tag']==profit_tag else np.nan
            earnings_yoy=change(profit,yr['profit']) if yr and yr['profit_tag']==profit_tag else np.nan
            old_profits=[a['profit'] for k,a in sorted(state.items()) if k<r.quarter_end and a['eligible']<r.eligible and a['profit_tag']==profit_tag and pd.notna(a['profit'])][-3:]
            expect=np.nan
            if p and pd.notna(p['profit']) and len(old_profits)>=2 and p['profit_tag']==profit_tag:
                expect=p['profit']+.35*float(np.median(np.diff(old_profits)))
            m=margin-p['margin'] if p and pd.notna(p['margin']) and pd.notna(margin) else np.nan
            o=op_margin-p['op_margin'] if p and pd.notna(p['op_margin']) and pd.notna(op_margin) else np.nan
            out=dict(symbol=symbol,basis=basis,quarter_end=r.quarter_end,eligible=r.eligible,release=r.release,sequence=r.sequence,
                     revised=r.revised,source_file=r.source_file,sales=sales,sales_definition=kind,profit_measure=profit,profit_definition=profit_tag,
                     profit_margin=margin,operating_margin=op_margin,revenue_qoq=qoq,revenue_yoy=yoy,profit_qoq=earnings,profit_yoy=earnings_yoy,
                     profit_expectation=expect,statistical_surprise=change(profit,expect),margin_delta=m,operating_margin_delta=o,
                     reported_debt=r.debt if pd.notna(r.debt) else r.debt_current+r.debt_noncurrent,reported_cash=r.cash,
                     reported_op_cash=r.op_cash,reported_capex=r.capex,prior_quarter=p['end'] if p else None,
                     prior_quarter_public=p['eligible'] if p else None,prior_year_public=yr['eligible'] if yr else None,
                     known_previous_profit_count=len(old_profits))
            if p:assert p['eligible']<r.eligible
            state[r.quarter_end]=dict(kind=kind,sales=sales,profit_tag=profit_tag,profit=profit,margin=margin,
                 op_margin=op_margin,end=r.quarter_end,eligible=r.eligible)
            rows.append(out)
    return pd.DataFrame(rows)

def run():
    register()
    z=listings()
    rows=list(z.itertuples(index=False))
    tasks=[]
    for r in rows:
        suffix='xml' if r.xbrl else 'html'
        tasks.append((r.xbrl or r.ixbrl,f'sources/facts/{r.symbol}-{r.quarter_end}-{r.sequence}.{suffix}.gz','document'))
    receipts=list(jobs(tasks,10))
    allfact=[]; reports=[]
    for r,q in zip(rows,receipts):
        ff=OUT/q['file'] if q.get('file') else None
        b=[]
        if ff:
            try:b=facts(unpack(ff),r)
            except ET.ParseError:b=[]
        if not b and r.ixbrl:
            rc=grab(r.ixbrl,f'sources/inline/{r.symbol}-{r.quarter_end}-{r.sequence}.html.gz','document')
            q['inline_attempt']=rc
            if rc.get('file'):
                try:b=facts(unpack(OUT/rc['file']),r)
                except ET.ParseError:b=[]
                if b:ff=OUT/rc['file']
        q['parsed_facts']=len(b)
        if not b:continue
        shared=dict(symbol=r.symbol,quarter_end=r.quarter_end,release=r.release,eligible=r.eligible,basis=r.basis,
                    sequence=r.sequence,revised=r.revised,source_file=ff.relative_to(OUT).as_posix())
        reports.append(shared|{k:next((x['value'] for x in b if x['metric']==k),np.nan) for k in FACTS})
        allfact.extend(shared|v for v in b)
    save('structured-document-receipt.json',receipts)
    if not reports:
        raise RuntimeError('No authentic machine-readable quarterly facts parsed')
    raw=pd.DataFrame(allfact)
    assert raw.period_end.between(FIRST,FREEZE).all() and raw.period_start.dropna().ge(FIRST).all()
    write('structured-financial-facts.csv.gz',raw)
    z=pd.DataFrame(reports)
    write('structured-quarterly-reports.csv.gz',z)
    c=comparable(z)
    # One arrival per issuer and reporting period by lead availability. Versioned facts are retained separately.
    best=c.sort_values(['eligible','revised','basis']).drop_duplicates(['symbol','quarter_end'])
    write('fundamental-comparisons.csv.gz',c)
    write('primary-fundamental-events.csv.gz',best)
    save('fundamental-receipt.json',dict(registered_documents=len(receipts),parsed_reports=len(reports),fact_rows=len(raw),
         reporting_periods=int(best.quarter_end.nunique()),issuers=int(best.symbol.nunique()),primary_reporting_events=len(best),
         metrics=raw.metric.value_counts().to_dict(),revenue_qoq=int(best.revenue_qoq.notna().sum()),profit_yoy=int(best.profit_yoy.notna().sum()),
         statistical_surprises=int(best.statistical_surprise.notna().sum()),period_rule='Exact quarter-end contexts, current-quarter duration 65–105 days, no pre-2025 context start, explicit INR units, duplicate or conflicting context guard. Cash flow and capex can use a longer current-year reporting period and are preserved with context.',
         expectation='Most recent comparable reported profit plus 0.35 times median change in up to three prior releases. No historical analyst consensus or authenticated prior guidance panel.'))
    print('Structured data parsed',len(reports),'reports and',len(raw),'facts',flush=True)

if __name__=='__main__':
    run()
