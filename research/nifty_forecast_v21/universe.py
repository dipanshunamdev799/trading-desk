"""Build the dated equity universe, action-aware cash tape and guarded weights."""
import gzip
from io import BytesIO, StringIO
import re
from zipfile import ZipFile

from pypdf import PdfReader

from .common import *

PRICE_FIELDS = {'TradDt':'day','ISIN':'isin','FinInstrmId':'instrument','TckrSymb':'symbol','SctySrs':'series',
                'FinInstrmNm':'name','OpnPric':'open','HghPric':'high','LwPric':'low','ClsPric':'close',
                'PrvsClsgPric':'exchange_previous','TtlTradgVol':'volume','TtlTrfVal':'turnover'}
SECTOR_NAMES = ('bank','finance','it','auto','energy','consumer','health','materials','industrial','telecom','other')
NUMBER = r'-?[\d,]+(?:\.\d+)?'
PDF_ROW = re.compile(rf'^\s*([A-Z0-9&_.-]+)\s{{2,}}(.+?)\s{{2,}}(.+?)\s{{2,}}({NUMBER})\s{{2,}}({NUMBER})\s{{2,}}({NUMBER})\s*$')


def sector(industry):
    s = str(industry).lower()
    rules = (
        ('bank',r'(?:sector |commercial )bank\b'),('finance',r'financ|\bnbfc\b|insurance|holding comp|investment company|capital market'),
        ('it',r'information technology|computer|software|it enabled'),('auto',r'automob|automotiv|\bauto\b|cars|vehicle|wheeler|scooter'),
        ('energy',r'oil|gas|power|refiner|petrol|coal|fuel'),('health',r'health|hospital|pharm|medical'),
        ('materials',r'metal|steel|minerals|cement|aluminium|zinc|chemical|iron'),
        ('consumer',r'consum|fmcg|food|retail|beverage|coffee|personal care|paint|gems|cigarette|hotels|brew'),
        ('industrial',r'capital goods|industr|engineer|construction|defen[cs]e|electrical|ship|aerospace|port|logistic|rail'),
        ('telecom',r'telecom|cellular'),
    )
    return next((key for key,p in rules if re.search(p,s)), 'other')


def official_weights():
    catalog = read('source-receipt.json')['records']
    days = pd.Index(cash().index)
    rows, states = [], []
    for record in catalog:
        if record['family'] not in ('nifty50_weights','index_families') or 'file' not in record:
            continue
        month = record['day']
        i = days.searchsorted(month, side='right')-1
        measure = days[i]
        guard = {f'eligible_lag{k}': days[i+k+1] if i+k+1<len(days) else None for k in (0,1,5,10)}
        with ZipFile(OUT / record['file']) as z:
            for key in z.namelist():
                raw = z.read(key)
                if key.lower().endswith('.csv'):
                    frame = parse_weight_csv(raw)
                    family = 'NIFTY Next 50' if 'next' in key.lower() else 'NIFTY 50'
                    flavor = 'official_monthly_csv'
                elif key.lower().endswith('.pdf'):
                    flavor = 'official_monthly_pdf'
                    family, stamp, frame = parse_weight_pdf(raw)
                    if stamp!=measure:
                        states.append(dict(month=month,measured=measure,index_name=family,flavor=flavor,status='printed date differs',member=key))
                        continue
                else:
                    continue
                total = frame.mcap_crore.sum()
                pct = frame.weight_pct.sum()
                valid = len(frame)>=8 and total>0 and 97<=pct<=103 and frame.symbol.is_unique
                if not valid:
                    states.append(dict(month=month,measured=measure,index_name=family,flavor=flavor,count=len(frame),
                                       rounded_sum=pct,status='insufficient parsed coverage',member=key))
                    continue
                frame['mcap_weight'] = frame.mcap_crore/total
                frame['published_weight'] = frame.weight_pct/pct
                # Positive-weight special situation components are retained in both membership and coverage audits.
                frame['sector'] = frame.industry.map(sector)
                if family=='NIFTY Bank':
                    frame['sector']='bank'
                frame = frame.assign(month=month,measured=measure,index_name=family,flavor=flavor,file=record['file'],
                                     member=key,sha256=record['sha256'],**guard)
                rows.append(frame)
                states.append(dict(month=month,measured=measure,index_name=family,flavor=flavor,count=len(frame),
                                   positive_weights=int(frame.weight_pct.gt(0).sum()),rounded_sum=pct,
                                   max_weight_delta=float(frame.mcap_weight.sub(frame.published_weight).abs().max()),
                                   status='verified weight total' if 99.75<=pct<=100.25 else 'mcap normalized; weight total discrepancy',member=key,
                                   candidates_with_close=int(frame.close_reported.notna().sum()),**guard))
    data=pd.concat(rows,ignore_index=True)
    write('dated-weights.csv.gz',data)
    write('weight-snapshot-audit.csv',pd.DataFrame(states))
    return data


def parse_weight_csv(raw):
    text=raw.decode('cp1252')
    ln=next(i for i,s in enumerate(text.splitlines()) if 'security symbol' in s.lower() and 'weight' in s.lower())
    d=pd.read_csv(StringIO(text),skiprows=ln,dtype=str).iloc[:,:7]
    d.columns=['order','symbol','company','industry','equity_capital_rupees','mcap_crore','weight_pct']
    d=d[pd.to_numeric(d.order,errors='coerce').notna()&d.symbol.notna()].drop(columns='order').copy()
    for k in ('equity_capital_rupees','mcap_crore','weight_pct'):
        d[k]=pd.to_numeric(d[k].str.replace(',','',regex=False),errors='coerce')
    d=d[d.weight_pct.notna()&d.mcap_crore.notna()].copy()
    d['symbol']=d.symbol.str.strip().str.upper()
    d['close_reported']=np.nan
    return d


def parse_weight_pdf(raw):
    reader=PdfReader(BytesIO(raw))
    text='\n'.join(p.extract_text(extraction_mode='layout') for p in reader.pages)
    label=re.search(r'Constituents of ([^\n]+)',text)
    day=re.search(r'[A-Z][a-z]+ \d{1,2}, 20(?:25|26)',text)
    assert label and day, text[:270]
    label=label.group(1).strip()
    if label.casefold().startswith('nifty'):
        label='NIFTY'+label[5:]
    rows=[]
    for line in text.splitlines():
        m=PDF_ROW.match(line)
        if m:
            a,b,c,d,e,f=m.groups()
            rows.append((a,b,c,*[float(n.replace(',','')) for n in (d,e,f)]))
    d=pd.DataFrame(rows,columns=['symbol','company','industry','close_reported','mcap_crore','weight_pct'])
    d['equity_capital_rupees']=np.nan
    return label,pd.Timestamp(day.group()).strftime('%Y-%m-%d'),d


def all_cash():
    out=[]
    for rec in read('source-receipt.json')['records']:
        if rec['family']!='cash' or 'file' not in rec:
            continue
        p=(ROOT if rec.get('base')=='repository' else OUT)/rec['file']
        with ZipFile(p) as z:
            with z.open(next(k for k in z.namelist() if k.lower().endswith('.csv'))) as f:
                d=pd.read_csv(f,usecols=list(PRICE_FIELDS),low_memory=False).rename(columns=PRICE_FIELDS)
        day=rec['day']
        assert d.day.astype(str).eq(day).all(), (p,day,d.day.unique())
        out.append(d[d.close.gt(0)&d.symbol.notna()&d.series.isin(['EQ','BE','BZ','SM','ST'])].copy())
    d=pd.concat(out,ignore_index=True)
    assert set(d.day)==set(cash().index)
    d=d.sort_values(['day','symbol','volume','series'],ascending=[True,True,False,False]).drop_duplicates(['day','symbol'])
    return d


def num(value):
    return float(value.replace(',',''))


def multiplier(subject):
    s=str(subject).lower()
    factors=[]
    if 'split' in s or 'consolidat' in s or 'sub-division' in s:
        m=re.search(r'from\s+(?:r[se]\.?\s*)?([\d,.]+).*?\bto\s+(?:r[se]\.?\s*)?([\d,.]+)',s)
        if m:
            a,b=[num(x.rstrip('.')) for x in m.groups()]
            if a>0 and b>0:
                factors.append(b/a)
    if 'bonus' in s:
        m=re.search(r'([0-9]+)\s*:\s*([0-9]+)',s)
        if m:
            a,b=map(int,m.groups())
            if b>0:
                factors.append(b/(b+a))
    return float(np.prod(factors)) if factors else np.nan


def action_source():
    rows=[];receipts=[]
    for year in (2025,2026):
        p=V17/f'sources/source-probes/corporate-action-{year}.json.gz'
        with gzip.open(p,'rt',encoding='utf-8') as f:
            body=json.load(f)
        if isinstance(body,dict):
            body=body.get('data',body.get('corporateActions',[]))
        for r in body:
            key=r.get('exDate') or r.get('ex_date')
            iso=isinstance(key,str) and bool(re.match(r'^20\d\d-\d\d-\d\d',key))
            day=pd.to_datetime(key,errors='coerce',dayfirst=not iso)
            if pd.isna(day) or not (FIRST<=day.date().isoformat()<=FREEZE):
                continue
            rows.append(dict(day=day.date().isoformat(),symbol=r.get('symbol') or r.get('stock'),action_isin=r.get('isin'),
                             subject=r.get('subject') or r.get('purpose') or '',broadcast=r.get('broadcastDate')))
        receipts.append(dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),raw=len(body)))
    d=pd.DataFrame(rows).dropna(subset='symbol').drop_duplicates()
    d=d.groupby(['day','symbol'],as_index=False).agg(subject=('subject',lambda x:' / '.join(sorted(set(x)))),
                                                   action_isin=('action_isin','first'),broadcast=('broadcast','first'))
    d['ratio']=d.subject.map(multiplier)
    return d,receipts


def price_returns(raw,actions,days):
    fields=['day','symbol','isin','instrument','series','open','high','low','close','exchange_previous','volume','turnover']
    d=raw[fields].sort_values(['symbol','day']).merge(actions,on=['day','symbol'],how='left',validate='m:1')
    d['seq']=days.get_indexer(d.day)
    g=d.groupby('symbol',sort=False)
    d['previous']=g.close.shift()
    d['previous_isin']=g.isin.shift()
    d['adjacent']=d.seq.sub(g.seq.shift()).eq(1)
    changed=d['isin'].ne(d.previous_isin)&d.previous_isin.notna()
    d['isin_changed']=changed
    c=d.subject.fillna('').str.lower()
    special=c.str.contains('demerger|de-merger|merger|rights|special dividend|split|sub-division|bonus|consolidat|scheme of arrangement')
    raw_return=d.close.div(d.previous).sub(1).where(d.adjacent)
    exchange_return=d.close.div(d.exchange_previous.replace(0,np.nan)).sub(1).where(d.adjacent)
    ref_ratio=d.exchange_previous.div(d.previous)
    ref_ok=ref_ratio.between(.035,25)&ref_ratio.sub(1).abs().gt(.001)&(special|changed)
    declared_denom=d.previous*d.ratio
    ratio_ok=d.ratio.between(.035,25)&d.adjacent
    exchange_matches=ref_ratio.div(d.ratio).sub(1).abs().lt(.015)
    exchange_recovers=(exchange_return.abs()<raw_return.abs())&(ref_ok)&(~ratio_ok|exchange_matches)
    chosen=np.select([ratio_ok,exchange_recovers],[declared_denom,d.exchange_previous],default=d.previous)
    d['return_raw']=raw_return
    d['return_exchange']=exchange_return
    d['return_adjusted']=(d.close/chosen-1).where(d.adjacent)
    unresolved=(changed&~(ratio_ok|exchange_recovers))|(special&raw_return.abs().gt(.33)&~(ratio_ok|exchange_recovers))
    d.loc[unresolved,'return_adjusted']=np.nan
    d['action_treatment']=np.select([unresolved,ratio_ok,exchange_recovers],['unresolved identity/action','ratio from dated action','verified exchange reset'],default='previous traded close')
    if (OUT/'sources/actions/2025-10-07.pdf').is_file():
        e=d.day.eq('2025-10-14')&d.symbol.eq('TATAMOTORS')&d.open.gt(0)&d.adjacent
        assert e.sum()==1
        d.loc[e,'return_adjusted']=d.loc[e,'close']/d.loc[e,'open']-1
        d.loc[e,'subject']='NSE Indices October 7 demerger notice. Surviving quote rebased to official session open.'
        d.loc[e,'action_treatment']='confirmed demerger opening basis'
    audit=d[d.subject.notna()|changed].copy()
    write('cash-identity-and-actions.csv.gz',audit.drop(columns=['open','high','low']))
    return d


def align_weights(d,days,names,adjusted):
    p=d[d.flavor.eq('official_monthly_csv')]
    base=p[p.index_name.eq('NIFTY 50')]
    adj=np.nan_to_num(adjusted,nan=0.)
    wealth=np.cumprod(1+adj,axis=0)
    assert np.isfinite(wealth).all() and (wealth>0).all()
    official={}
    for lag in (0,1,5,10):
        w=np.full(adjusted.shape,np.nan)
        month=np.full(len(days),'',dtype='U10')
        for start,b in base.groupby(f'eligible_lag{lag}'):
            i=days.get_loc(start)
            later=days.searchsorted(b.month.iloc[0])
            j=days.get_loc(b.measured.iloc[0])
            q=b.set_index('symbol').mcap_weight.reindex(names).fillna(0).to_numpy(float)
            assert abs(q.sum()-1)<1.e-8 and i>j and later>=j
            growth=wealth[i-1:-1]/wealth[j]
            z=growth*q
            w[i:]=z/z.sum(axis=1,keepdims=True)
            month[i:]=b.month.iloc[0]
        official[f'weight_lag{lag}']=w
        official[f'vintage_lag{lag}']=month
    return official


def run():
    catalog=official_weights()
    raw=all_cash()
    d0=raw[(raw.day<=SEED_END)&raw.series.eq('EQ')&raw.volume.gt(0)]
    seed=d0.groupby('symbol',as_index=False).agg(seed_sessions=('day','nunique'),median_turnover=('turnover','median'),name=('name','last'))
    seed=seed[seed.seed_sessions>=12].sort_values(['median_turnover','symbol'],ascending=[False,True]).reset_index(drop=True)
    seed['liquidity_rank']=np.arange(1,len(seed)+1)
    seed=seed.head(240).assign(observed_through=SEED_END)
    write('january-liquidity-universe.csv',seed)
    names=pd.Index(sorted(set(seed.symbol)|set(catalog.symbol)))
    cash_table=cash()
    days=cash_table.index
    actions,receipts=action_source()
    d=price_returns(raw[raw.symbol.isin(names)].copy(),actions[actions.symbol.isin(names)],days)
    panels={k:d.pivot(index='day',columns='symbol',values=k).reindex(index=days,columns=names).to_numpy(float)
            for k in ('open','high','low','close','exchange_previous','volume','turnover','return_raw','return_adjusted','return_exchange')}
    w=align_weights(catalog,days,names,panels['return_adjusted'])
    map_=np.full((len(days),len(names)),SECTOR_NAMES.index('other'),dtype=np.int8)
    new=np.zeros(map_.shape,bool)
    pdf=catalog[catalog.flavor.eq('official_monthly_pdf')].copy()
    for first,part in catalog.dropna(subset='eligible_lag5').groupby('eligible_lag5'):
        i=days.get_loc(first)
        spec=part[part.flavor.eq('official_monthly_csv')].drop_duplicates('symbol').copy()
        groups=spec.set_index('symbol').sector
        pos=names.get_indexer(spec.symbol)
        map_[i:,pos]=[SECTOR_NAMES.index(x) for x in groups]
        actual=part[part.index_name.eq('NIFTY Bank')].symbol.unique()
        map_[i:,names.get_indexer(actual)]=SECTOR_NAMES.index('bank')
        new[i:,pos]=True
    core=np.isin(names,seed.symbol)
    present=panels['volume']>0
    original=(days.to_numpy()>SEED_END)[:,None]&core[None,:]
    eligible=original|new
    records=pdf.merge(d[['day','symbol','isin','close']],left_on=['measured','symbol'],right_on=['day','symbol'],how='left',validate='m:1')
    records['price_difference']=records.close_reported-records.close
    records['exact_tick']=records.price_difference.abs().lt(.011)
    write('official-weight-cash-reconciliation.csv.gz',records[['index_name','flavor','measured','month','symbol','isin','close_reported','close','price_difference','exact_tick','published_weight']])
    d.drop(columns=['seq']).to_csv(OUT/'cash-equity-research-panel.csv.gz',index=False)
    np.savez_compressed(OUT/'equity-panel.npz',days=days.to_numpy(dtype='U10'),symbols=names.to_numpy(dtype='U30'),
                        eligible=eligible,sector=map_,seed_rank=seed.set_index('symbol').liquidity_rank.reindex(names).fillna(9999).to_numpy(int),
                        **panels,**w)
    write('historical-equity-inventory.csv',raw.groupby(['symbol','series'],as_index=False).agg(first=('day','min'),last=('day','max'),
        rows=('day','nunique'),distinct_isins=('isin','nunique'),sample_name=('name','first')))
    save('universe-receipt.json',dict(cash_sessions=len(days),new_cash_files=sum(r['family']=='cash' and r.get('base')!='repository' and 'file' in r for r in read('source-receipt.json')['records']),
         all_cash_security_days=len(raw),all_symbols=int(raw.symbol.nunique()),seed_names=len(seed),modeled_symbols=len(names),
         eligible_equity_dates=int((eligible&present).sum()),sector_names=SECTOR_NAMES,weight_csv_vintages=int(catalog[catalog.flavor.eq('official_monthly_csv')].month.nunique()),
         dated_rows=len(catalog),pdf_price_compares=int(records.close.notna().sum()),pdf_exact_prices=int(records.exact_tick.sum()),
         action_treatments=d.action_treatment.value_counts().to_dict(),corporate_sources=receipts,
         eligibility='Membership and classification enter prospectively after five completed cash sessions. Fixed January liquidity cohort can enter from February.',
         missing='Halted or missing securities remain in the identity archive. Zero contribution on missing price is a marked no-price carry convention only for reconstruction.',
         coverage_limit='Official NIFTY 50, NIFTY Next 50 and selected sector monthly membership. NIFTY 200/500 positions and daily free-float factor/divisor history unavailable.',
         publication_limit='Archive filenames and table dates identify measurement, not first publication. Release lag sensitivity and month-end ex-post comparison remain distinct.'))
    print('Built',len(names),'equity series;',int(eligible.sum()),'eligible equity dates;',len(catalog),'official dated rows.',flush=True)


if __name__=='__main__':
    run()
